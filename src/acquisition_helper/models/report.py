"""Report-related models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class QAResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    feedback: str = ""
    requires_rework: bool = False


class TokenUsageSnapshot(BaseModel):
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
