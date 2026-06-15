"""Acquisition Flow — intake, HITL, plan, research, QA, report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from acquisition_helper.config.loader import load_defaults
from acquisition_helper.control.budget_monitor import BudgetMonitor
from acquisition_helper.control.flow_planner import (
    build_workflow_plan,
    format_plan_summary,
    write_workflow_plan,
)
from acquisition_helper.control.guardrails import is_safe
from acquisition_helper.control.hitl import (
    approve_budget_extension,
    approve_workflow,
    confirm_requirements,
    run_intake_wizard,
)
from acquisition_helper.control.profiles import get_profile
from acquisition_helper.crews.admin_crew import run_admin_qa, run_prompt_refiner
from acquisition_helper.crews.intake_crew import normalize_requirements
from acquisition_helper.crews.research_crew import kickoff_research
from acquisition_helper.env import OUTPUT_DIR, REPORT_FILENAME, ensure_output_dir
from acquisition_helper.models.intake import (
    ApprovalStatus,
    HitlDecision,
    TierName,
    UserRequirements,
)
from acquisition_helper.models.workflow_plan import WorkflowPlan
from acquisition_helper.reporting.markdown_report import get_final_report_text


class FlowState(BaseModel):
    requirements: UserRequirements | None = None
    approval: ApprovalStatus = Field(default_factory=ApprovalStatus)
    workflow_plan: WorkflowPlan | None = None
    crew_output: Any | None = None
    qa_passed: bool = False
    rework_count: int = 0
    cancelled: bool = False
    error_message: str | None = None


class AcquisitionPipeline:
    """Orchestrates the full acquisition research pipeline with HITL gates."""

    def __init__(
        self,
        *,
        requirements: UserRequirements | None = None,
        skip_wizard: bool = False,
        non_interactive: bool = False,
    ) -> None:
        self._state = FlowState()
        self._provided_requirements = requirements
        self._skip_wizard = skip_wizard
        self._non_interactive = non_interactive
        self._defaults = load_defaults()
        self._qa_threshold = float(
            (self._defaults.get("qa") or {}).get("pass_score_threshold", 0.7)
        )
        self._max_rework = int((self._defaults.get("qa") or {}).get("max_rework_loops", 2))

    @property
    def state(self) -> FlowState:
        return self._state

    def run_intake(self) -> UserRequirements | None:
        if self._provided_requirements is not None:
            self._state.requirements = self._provided_requirements
            return self._state.requirements

        if self._skip_wizard:
            defaults_block = self._defaults.get("defaults") or {}
            self._state.requirements = UserRequirements(
                strategic_intent=str(self._defaults.get("strategic_intent", "")).strip(),
                sector=str(defaults_block.get("sector", "")),
                geography=str(defaults_block.get("geography", "")),
                financial_constraints=str(defaults_block.get("financial_constraints", "")),
                candidate_count=int(defaults_block.get("candidate_count", 12)),
                tier=TierName(str(defaults_block.get("tier", "standard"))),
            )
            return self._state.requirements

        self._state.requirements = run_intake_wizard(self._defaults)
        return self._state.requirements

    def run_requirements_hitl(self) -> bool:
        requirements = self._state.requirements
        if requirements is None:
            return False

        profile = get_profile(requirements.control_profile)
        if self._non_interactive or not profile.hitl_on_requirements:
            self._state.approval.requirements_approved = True
            return True

        while True:
            decision = confirm_requirements(requirements)
            if decision == HitlDecision.APPROVE:
                self._state.approval.requirements_approved = True
                self._state.requirements = normalize_requirements(requirements)
                return True
            if decision == HitlDecision.CANCEL:
                self._state.cancelled = True
                return False
            requirements = run_intake_wizard(self._defaults)
            self._state.requirements = requirements

    def run_planning(self) -> WorkflowPlan | None:
        requirements = self._state.requirements
        if requirements is None:
            return None

        plan = build_workflow_plan(requirements)
        self._state.workflow_plan = plan
        ensure_output_dir()
        write_workflow_plan(plan, OUTPUT_DIR)
        return plan

    def run_workflow_hitl(self) -> bool:
        plan = self._state.workflow_plan
        requirements = self._state.requirements
        if plan is None or requirements is None:
            return False

        profile = get_profile(requirements.control_profile)
        summary = format_plan_summary(plan)
        print(f"\n{summary}\n")

        if self._non_interactive or not profile.hitl_on_workflow:
            self._state.approval.workflow_approved = True
            return True

        decision = approve_workflow(summary)
        if decision == HitlDecision.APPROVE:
            self._state.approval.workflow_approved = True
            return True
        if decision == HitlDecision.CANCEL:
            self._state.cancelled = True
            return False

        requirements = run_intake_wizard(self._defaults)
        self._state.requirements = requirements
        self.run_planning()
        return self.run_workflow_hitl()

    def run_budget_preflight(self, budget: BudgetMonitor) -> bool:
        plan = self._state.workflow_plan
        if plan is None:
            return False
        if not budget.preflight_ok(plan.estimated_tokens_max):
            print(
                f"Warning: tier estimate ({plan.estimated_tokens_max:,}) exceeds "
                f"budget ceiling ({budget.ceiling:,})."
            )
        return True

    def run_research(self) -> object | None:
        requirements = self._state.requirements
        if requirements is None:
            return None
        if not is_safe(requirements.strategic_intent):
            self._state.error_message = "Guardrails blocked strategic intent (possible PII/secret)."
            return None

        output = kickoff_research(requirements)
        self._state.crew_output = output
        return output

    def run_qa_loop(self, budget: BudgetMonitor) -> bool:
        requirements = self._state.requirements
        output = self._state.crew_output
        if requirements is None or output is None:
            return False

        research_text = get_final_report_text(output)
        profile = get_profile(requirements.control_profile)
        max_loops = min(self._max_rework, profile.qa_max_rework)

        while self._state.rework_count <= max_loops:
            qa = run_admin_qa(requirements, research_text, pass_threshold=self._qa_threshold)
            budget.record(total=5000)

            if qa.passed:
                self._state.qa_passed = True
                return True

            if self._state.rework_count >= max_loops:
                print(f"QA did not pass after {max_loops} rework loops. Proceeding with best effort.")
                return True

            if budget.requires_hitl():
                profile_obj = get_profile(requirements.control_profile)
                if not approve_budget_extension(
                    budget.usage.total_tokens,
                    budget.ceiling,
                    plan.estimated_tokens_max if (plan := self._state.workflow_plan) else 0,
                ):
                    return True

            feedback = run_prompt_refiner(requirements, qa.feedback)
            print(f"\nPrompt refinement for rework:\n{feedback[:500]}...\n")
            self._state.rework_count += 1
            output = kickoff_research(requirements)
            self._state.crew_output = output
            research_text = get_final_report_text(output)
            budget.record_from_crew_output(output)

        return True

    def execute(self) -> FlowState:
        if not self.run_intake():
            return self._state

        requirements = self._state.requirements
        if requirements is None:
            return self._state

        budget = BudgetMonitor(profile=get_profile(requirements.control_profile))

        if not self.run_requirements_hitl():
            return self._state

        self.run_planning()
        if not self.run_workflow_hitl():
            return self._state

        self.run_budget_preflight(budget)

        output = self.run_research()
        if output is not None:
            budget.record_from_crew_output(output)

        self.run_qa_loop(budget)
        return self._state


def run_flow(
    *,
    requirements: UserRequirements | None = None,
    skip_wizard: bool = False,
    non_interactive: bool = False,
) -> FlowState:
    pipeline = AcquisitionPipeline(
        requirements=requirements,
        skip_wizard=skip_wizard,
        non_interactive=non_interactive,
    )
    return pipeline.execute()
