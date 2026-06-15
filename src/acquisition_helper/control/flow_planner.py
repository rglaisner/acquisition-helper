"""Workflow planner — Mermaid diagrams and ASCII summaries."""

from __future__ import annotations

from pathlib import Path

import yaml

from acquisition_helper.control.agent_registry import AGENT_PHASES, get_tier_spec
from acquisition_helper.env import CONFIG_DIR, OUTPUT_DIR
from acquisition_helper.models.intake import TierName, UserRequirements
from acquisition_helper.models.workflow_plan import AgentNode, TaskEdge, WorkflowPlan


def _load_defaults() -> dict[str, object]:
    path = CONFIG_DIR / "defaults.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_agent_roles() -> dict[str, str]:
    path = CONFIG_DIR / "agents" / "agents_all.yaml"
    with path.open(encoding="utf-8") as handle:
        agents = yaml.safe_load(handle) or {}
    return {aid: str(cfg.get("role", aid)) for aid, cfg in agents.items()}


def build_workflow_plan(requirements: UserRequirements) -> WorkflowPlan:
    spec = get_tier_spec(requirements.tier)
    roles = _load_agent_roles()
    defaults = _load_defaults()
    estimates = (defaults.get("token_estimates") or {}).get(requirements.tier.value, {})

    agents = [
        AgentNode(
            id=aid,
            role=roles.get(aid, aid),
            phase=AGENT_PHASES.get(aid, "Unknown"),
        )
        for aid in spec.agent_ids
    ]

    edges: list[TaskEdge] = []
    for task_id, ctx_tasks in spec.task_context.items():
        for ctx in ctx_tasks:
            edges.append(TaskEdge(source=ctx, target=task_id))

    mermaid = _build_mermaid(requirements.tier, spec.agent_ids, spec.task_context, spec.parallel_tasks)
    ascii_summary = _build_ascii(spec.agent_ids, roles)

    return WorkflowPlan(
        tier=requirements.tier,
        agents=agents,
        edges=edges,
        mermaid=mermaid,
        estimated_tokens_min=int(estimates.get("min", 0)),
        estimated_tokens_max=int(estimates.get("max", 0)),
        ascii_summary=ascii_summary,
    )


def _build_mermaid(
    tier: TierName,
    agent_ids: tuple[str, ...],
    task_context: dict[str, tuple[str, ...]],
    parallel_tasks: tuple[str, ...],
) -> str:
    phases: dict[str, list[str]] = {}
    for aid in agent_ids:
        phase = AGENT_PHASES.get(aid, "Other")
        phases.setdefault(phase, []).append(aid)

    lines = ["flowchart LR"]
    for phase, ids in phases.items():
        safe_phase = phase.replace(" ", "_")
        lines.append(f"    subgraph {safe_phase} [{phase}]")
        for aid in ids:
            node_id = aid.replace("_", "")
            label = aid.replace("_", " ").title().replace(" ", "")
            lines.append(f"        {node_id}[{label}]")
        lines.append("    end")

    task_to_agent = {
        "explore": "explorer", "scope": "director", "profile": "profiler",
        "finance": "financier", "source": "sourcer",
        "integrated_research": "integrated_analyst",
        "tech": "tech_architect", "workforce": "workforce_analyst",
        "risk": "risk_assessor", "validate": "validator",
        "redteam": "red_teamer", "report": "reporter",
    }

    for task_id, ctx_tasks in task_context.items():
        target = task_to_agent.get(task_id, task_id).replace("_", "")
        for ctx in ctx_tasks:
            source = task_to_agent.get(ctx, ctx).replace("_", "")
            lines.append(f"    {source} --> {target}")

    header = f"%% Tier: {tier.value}"
    return header + "\n" + "\n".join(lines)


def _build_ascii(agent_ids: tuple[str, ...], roles: dict[str, str]) -> str:
    lines = ["Agent pipeline:"]
    for index, aid in enumerate(agent_ids, start=1):
        lines.append(f"  {index}. [{aid}] {roles.get(aid, aid)}")
    return "\n".join(lines)


def format_plan_summary(plan: WorkflowPlan) -> str:
    agent_table = "\n".join(
        f"  - {node.id}: {node.role} ({node.phase})" for node in plan.agents
    )
    return (
        f"Tier: {plan.tier.value}\n"
        f"Estimated tokens: {plan.estimated_tokens_min:,} – {plan.estimated_tokens_max:,}\n\n"
        f"{plan.ascii_summary}\n\n"
        f"Agents:\n{agent_table}\n\n"
        f"Mermaid (also saved to output/workflow_plan.md):\n"
        f"```mermaid\n{plan.mermaid}\n```"
    )


def write_workflow_plan(plan: WorkflowPlan, output_dir: Path | None = None) -> tuple[Path, Path]:
    out = output_dir or OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    mmd_path = out / "workflow_plan.mmd"
    md_path = out / "workflow_plan.md"

    mmd_path.write_text(plan.mermaid, encoding="utf-8")

    md_content = "\n".join([
        "# Workflow Plan",
        "",
        f"**Tier:** {plan.tier.value}",
        f"**Estimated tokens:** {plan.estimated_tokens_min:,} – {plan.estimated_tokens_max:,}",
        "",
        "## Agent Summary",
        "",
        plan.ascii_summary,
        "",
        "## Agents",
        "",
        "| ID | Role | Phase |",
        "|----|------|-------|",
        *[f"| {n.id} | {n.role} | {n.phase} |" for n in plan.agents],
        "",
        "## Flow Diagram",
        "",
        "```mermaid",
        plan.mermaid,
        "```",
        "",
    ])
    md_path.write_text(md_content, encoding="utf-8")
    return mmd_path, md_path
