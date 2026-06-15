"""Tests for flow planner."""

from acquisition_helper.control.flow_planner import build_workflow_plan, write_workflow_plan
from acquisition_helper.models.intake import TierName, UserRequirements


def _sample_requirements(tier: TierName = TierName.STANDARD) -> UserRequirements:
    return UserRequirements(
        strategic_intent="Acquire SME platform for AgentOS integration.",
        sector="Industrial services",
        geography="US Midwest",
        financial_constraints="EBITDA $3M–$10M",
        candidate_count=10,
        tier=tier,
    )


def test_build_workflow_plan_standard_has_agents():
    plan = build_workflow_plan(_sample_requirements(TierName.STANDARD))
    assert plan.tier == TierName.STANDARD
    assert len(plan.agents) == 7
    assert plan.mermaid.startswith("%% Tier: standard")
    assert "flowchart LR" in plan.mermaid


def test_build_workflow_plan_expert_has_eleven_agents():
    plan = build_workflow_plan(_sample_requirements(TierName.EXPERT))
    assert len(plan.agents) == 11
    assert any(node.id == "red_teamer" for node in plan.agents)


def test_write_workflow_plan_creates_files(tmp_path):
    plan = build_workflow_plan(_sample_requirements())
    mmd, md = write_workflow_plan(plan, tmp_path)
    assert mmd.exists()
    assert md.exists()
    assert "flowchart LR" in mmd.read_text(encoding="utf-8")
    assert "Workflow Plan" in md.read_text(encoding="utf-8")
