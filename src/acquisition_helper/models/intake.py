"""Pydantic models for user intake and strategic intent."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class TierName(str, Enum):
    ESSENTIAL = "essential"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ControlProfileName(str, Enum):
    CONSERVATIVE = "conservative"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


class UserRequirements(BaseModel):
    strategic_intent: str = Field(
        description="M&A thesis and transformation goals for the target platform"
    )
    sector: str = Field(default="SME services / light industrial")
    geography: str = Field(default="North America, Western Europe")
    financial_constraints: str = Field(
        default="EBITDA $2M–$15M; DSCR > 1.25x post-LBO"
    )
    candidate_count: int = Field(default=12, ge=1, le=50)
    tier: TierName = TierName.STANDARD
    control_profile: ControlProfileName = ControlProfileName.STANDARD


class ApprovalStatus(BaseModel):
    requirements_approved: bool = False
    workflow_approved: bool = False
    budget_approved: bool = False


class HitlDecision(str, Enum):
    APPROVE = "approve"
    EDIT = "edit"
    CANCEL = "cancel"


ApprovalLiteral = Literal["approve", "edit", "cancel"]
