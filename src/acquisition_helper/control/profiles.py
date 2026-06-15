"""Control profiles — token ceilings and HITL frequency."""

from __future__ import annotations

from dataclasses import dataclass

from acquisition_helper.models.intake import ControlProfileName


@dataclass(frozen=True)
class ControlProfile:
    name: ControlProfileName
    token_ceiling: int
    hitl_on_requirements: bool
    hitl_on_workflow: bool
    hitl_on_budget: bool
    qa_max_rework: int


PROFILES: dict[ControlProfileName, ControlProfile] = {
    ControlProfileName.CONSERVATIVE: ControlProfile(
        name=ControlProfileName.CONSERVATIVE,
        token_ceiling=200_000,
        hitl_on_requirements=True,
        hitl_on_workflow=True,
        hitl_on_budget=True,
        qa_max_rework=3,
    ),
    ControlProfileName.STANDARD: ControlProfile(
        name=ControlProfileName.STANDARD,
        token_ceiling=500_000,
        hitl_on_requirements=True,
        hitl_on_workflow=True,
        hitl_on_budget=True,
        qa_max_rework=2,
    ),
    ControlProfileName.AGGRESSIVE: ControlProfile(
        name=ControlProfileName.AGGRESSIVE,
        token_ceiling=1_000_000,
        hitl_on_requirements=True,
        hitl_on_workflow=False,
        hitl_on_budget=True,
        qa_max_rework=1,
    ),
}


def get_profile(name: ControlProfileName) -> ControlProfile:
    return PROFILES[name]
