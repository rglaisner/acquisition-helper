"""Token budget monitoring and HITL threshold triggers."""

from __future__ import annotations

import os

from acquisition_helper.control.profiles import ControlProfile, get_profile
from acquisition_helper.models.intake import ControlProfileName
from acquisition_helper.models.report import TokenUsageSnapshot


def _parse_token_ceiling(raw: str | None, profile_ceiling: int | None) -> int | None:
    if raw is None:
        return profile_ceiling
    stripped = raw.strip().lower()
    if not stripped or stripped in {"unlimited", "none", "inf", "infinity"}:
        return None
    value = int(stripped)
    return None if value <= 0 else value


class BudgetMonitor:
    def __init__(self, profile: ControlProfile | None = None) -> None:
        self._profile = profile or get_profile(ControlProfileName.STANDARD)
        self._ceiling = _parse_token_ceiling(
            os.environ.get("TOKEN_BUDGET"),
            self._profile.token_ceiling,
        )
        self._usage = TokenUsageSnapshot()

    @property
    def ceiling(self) -> int | None:
        return self._ceiling

    @property
    def is_unlimited(self) -> bool:
        return self._ceiling is None

    @property
    def usage(self) -> TokenUsageSnapshot:
        return self._usage

    def record(self, *, total: int, prompt: int = 0, completion: int = 0, requests: int = 0) -> None:
        self._usage.total_tokens += total
        self._usage.prompt_tokens += prompt
        self._usage.completion_tokens += completion
        self._usage.successful_requests += requests

    def record_from_crew_output(self, crew_output: object) -> None:
        usage = getattr(crew_output, "token_usage", None)
        if usage is None:
            return
        self.record(
            total=getattr(usage, "total_tokens", 0) or 0,
            prompt=getattr(usage, "prompt_tokens", 0) or 0,
            completion=getattr(usage, "completion_tokens", 0) or 0,
            requests=getattr(usage, "successful_requests", 0) or 0,
        )

    def exceeds_ceiling(self) -> bool:
        if self._ceiling is None:
            return False
        return self._usage.total_tokens >= self._ceiling

    def estimate_next_phase_cost(self, tier_tokens_max: int) -> int:
        remaining = max(0, tier_tokens_max - self._usage.total_tokens)
        return remaining

    def requires_hitl(self) -> bool:
        return self._profile.hitl_on_budget and self.exceeds_ceiling()

    def preflight_ok(self, estimated_max: int) -> bool:
        if self._ceiling is None:
            return True
        return estimated_max <= self._ceiling
