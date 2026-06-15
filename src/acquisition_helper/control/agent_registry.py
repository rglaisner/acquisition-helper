"""Agent registry — tier → agents and task DAG."""

from __future__ import annotations

from dataclasses import dataclass, field

from acquisition_helper.models.intake import TierName


@dataclass(frozen=True)
class TierSpec:
    tier: TierName
    agent_ids: tuple[str, ...]
    task_ids: tuple[str, ...]
    task_context: dict[str, tuple[str, ...]] = field(default_factory=dict)
    parallel_tasks: tuple[str, ...] = ()
    agents_with_tools: tuple[str, ...] = ()
    pro_model_agents: tuple[str, ...] = ()


TIER_REGISTRY: dict[TierName, TierSpec] = {
    TierName.ESSENTIAL: TierSpec(
        tier=TierName.ESSENTIAL,
        agent_ids=("director", "integrated_analyst", "reporter"),
        task_ids=("scope", "integrated_research", "report"),
        task_context={"report": ("integrated_research",)},
        agents_with_tools=(),
        pro_model_agents=("reporter",),
    ),
    TierName.STANDARD: TierSpec(
        tier=TierName.STANDARD,
        agent_ids=(
            "explorer", "director", "profiler", "sourcer", "financier", "validator", "reporter",
        ),
        task_ids=("explore", "scope", "profile", "source", "finance", "validate", "report"),
        task_context={
            "profile": ("scope", "explore"),
            "source": ("scope", "explore"),
            "finance": ("scope",),
            "validate": ("source", "finance", "profile"),
            "report": ("validate",),
        },
        parallel_tasks=("source", "finance"),
        agents_with_tools=("explorer", "sourcer"),
        pro_model_agents=("validator", "reporter"),
    ),
    TierName.ADVANCED: TierSpec(
        tier=TierName.ADVANCED,
        agent_ids=(
            "explorer", "director", "profiler", "financier", "sourcer",
            "tech_architect", "workforce_analyst", "risk_assessor", "validator", "reporter",
        ),
        task_ids=(
            "explore", "scope", "profile", "finance", "source",
            "tech", "workforce", "risk", "validate", "report",
        ),
        task_context={
            "profile": ("scope",),
            "finance": ("scope",),
            "source": ("scope", "explore"),
            "tech": ("profile", "source"),
            "workforce": ("profile", "source"),
            "risk": ("finance", "source"),
            "validate": ("tech", "workforce", "risk"),
            "report": ("validate",),
        },
        parallel_tasks=("profile", "finance", "source"),
        agents_with_tools=("explorer", "sourcer"),
        pro_model_agents=("validator", "reporter"),
    ),
    TierName.EXPERT: TierSpec(
        tier=TierName.EXPERT,
        agent_ids=(
            "explorer", "director", "profiler", "financier", "sourcer",
            "tech_architect", "workforce_analyst", "risk_assessor",
            "validator", "red_teamer", "reporter",
        ),
        task_ids=(
            "explore", "scope", "profile", "finance", "source",
            "tech", "workforce", "risk", "validate", "redteam", "report",
        ),
        task_context={
            "profile": ("scope",),
            "finance": ("scope",),
            "source": ("scope", "explore"),
            "tech": ("profile", "source"),
            "workforce": ("profile", "source"),
            "risk": ("finance", "source"),
            "validate": ("tech", "workforce", "risk"),
            "redteam": ("tech", "workforce", "risk", "validate"),
            "report": ("tech", "workforce", "risk", "redteam"),
        },
        parallel_tasks=("profile", "finance", "source"),
        agents_with_tools=("explorer", "sourcer"),
        pro_model_agents=("validator", "red_teamer", "reporter"),
    ),
}


AGENT_PHASES: dict[str, str] = {
    "explorer": "Phase1_Scope",
    "director": "Phase1_Scope",
    "profiler": "Phase2_Parallel",
    "financier": "Phase2_Parallel",
    "sourcer": "Phase2_Parallel",
    "integrated_analyst": "Phase2_Research",
    "tech_architect": "Phase3_DeepDive",
    "workforce_analyst": "Phase3_DeepDive",
    "risk_assessor": "Phase3_DeepDive",
    "validator": "Phase4_QA",
    "red_teamer": "Phase4_QA",
    "reporter": "Phase5_Output",
}


def get_tier_spec(tier: TierName) -> TierSpec:
    return TIER_REGISTRY[tier]


def list_tiers() -> list[TierName]:
    return list(TIER_REGISTRY.keys())
