"""Tests for tier registry."""

from acquisition_helper.control.agent_registry import TIER_REGISTRY, get_tier_spec
from acquisition_helper.models.intake import TierName


def test_tier_agent_counts():
    assert len(get_tier_spec(TierName.ESSENTIAL).agent_ids) == 3
    assert len(get_tier_spec(TierName.STANDARD).agent_ids) == 7
    assert len(get_tier_spec(TierName.ADVANCED).agent_ids) == 10
    assert len(get_tier_spec(TierName.EXPERT).agent_ids) == 11


def test_expert_has_red_teamer():
    spec = get_tier_spec(TierName.EXPERT)
    assert "red_teamer" in spec.agent_ids
    assert "redteam" in spec.task_ids


def test_all_tiers_registered():
    assert set(TIER_REGISTRY.keys()) == set(TierName)
