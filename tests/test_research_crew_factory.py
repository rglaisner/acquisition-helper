"""Tests for research crew factory (structure only, no LLM)."""

from unittest.mock import patch

from acquisition_helper.crews.research_crew.factory import build_research_crew
from acquisition_helper.models.intake import TierName, UserRequirements


def _requirements(tier: TierName) -> UserRequirements:
    return UserRequirements(
        strategic_intent="Test intent",
        sector="Tech",
        geography="EU",
        financial_constraints="EBITDA $5M",
        candidate_count=5,
        tier=tier,
    )


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
def test_build_essential_crew_task_count():
    crew = build_research_crew(_requirements(TierName.ESSENTIAL))
    assert len(crew.tasks) == 3
    assert len(crew.agents) == 3


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
def test_build_expert_crew_task_count():
    crew = build_research_crew(_requirements(TierName.EXPERT))
    assert len(crew.tasks) == 11
    assert len(crew.agents) == 11
