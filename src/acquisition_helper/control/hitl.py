"""CLI human-in-the-loop prompts."""

from __future__ import annotations

from acquisition_helper.models.intake import ApprovalLiteral, HitlDecision, UserRequirements


def prompt_hitl(message: str, *, allow_edit: bool = True) -> HitlDecision:
    options = "[A]pprove"
    if allow_edit:
        options += " / [E]dit / [C]ancel"
    else:
        options += " / [C]ancel"

    print(f"\n--- HITL ---\n{message}\n{options}: ", end="", flush=True)
    while True:
        raw = input().strip().lower()
        if raw in ("a", "approve", ""):
            return HitlDecision.APPROVE
        if allow_edit and raw in ("e", "edit"):
            return HitlDecision.EDIT
        if raw in ("c", "cancel"):
            return HitlDecision.CANCEL
        print(f"Invalid choice. {options}: ", end="", flush=True)


def prompt_yes_no(message: str, *, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    print(f"{message}{suffix}", end="", flush=True)
    raw = input().strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def prompt_text(message: str, default: str = "") -> str:
    if default:
        print(f"{message} [{default}]: ", end="", flush=True)
    else:
        print(f"{message}: ", end="", flush=True)
    raw = input().strip()
    return raw if raw else default


def prompt_int(message: str, default: int) -> int:
    while True:
        raw = prompt_text(message, str(default))
        try:
            return int(raw)
        except ValueError:
            print("Enter a valid integer.")


def run_intake_wizard(defaults: dict[str, object]) -> UserRequirements:
    print("\n=== Acquisition Helper — Intake Wizard ===\n")

    strategic_intent = prompt_text(
        "Strategic intent (M&A thesis)",
        str(defaults.get("strategic_intent", "")).strip(),
    )
    sector = prompt_text("Target sector", str(defaults.get("sector", "")))
    geography = prompt_text("Geography", str(defaults.get("geography", "")))
    financial_constraints = prompt_text(
        "Financial constraints",
        str(defaults.get("financial_constraints", "")),
    )
    candidate_count = prompt_int(
        "Target candidate count",
        int(defaults.get("candidate_count", 12)),
    )

    print("\nTiers: essential (3) | standard (7) | advanced (10) | expert (11)")
    tier_raw = prompt_text("Select tier", str(defaults.get("tier", "standard"))).lower()

    print("\nProfiles: conservative | standard | aggressive")
    profile_raw = prompt_text(
        "Control profile",
        str(defaults.get("control_profile", "standard")),
    ).lower()

    from acquisition_helper.models.intake import ControlProfileName, TierName

    tier_map = {t.value: t for t in TierName}
    profile_map = {p.value: p for p in ControlProfileName}

    return UserRequirements(
        strategic_intent=strategic_intent,
        sector=sector,
        geography=geography,
        financial_constraints=financial_constraints,
        candidate_count=candidate_count,
        tier=tier_map.get(tier_raw, TierName.STANDARD),
        control_profile=profile_map.get(profile_raw, ControlProfileName.STANDARD),
    )


def confirm_requirements(requirements: UserRequirements) -> HitlDecision:
    summary = (
        f"Strategic intent:\n{requirements.strategic_intent}\n\n"
        f"Sector: {requirements.sector}\n"
        f"Geography: {requirements.geography}\n"
        f"Financial: {requirements.financial_constraints}\n"
        f"Candidates: {requirements.candidate_count}\n"
        f"Tier: {requirements.tier.value}\n"
        f"Profile: {requirements.control_profile.value}"
    )
    return prompt_hitl(f"Review requirements:\n\n{summary}")


def approve_workflow(plan_summary: str) -> HitlDecision:
    return prompt_hitl(f"Review proposed workflow:\n\n{plan_summary}")


def approve_budget_extension(current: int, ceiling: int, estimate: int) -> bool:
    return prompt_yes_no(
        f"Token usage {current:,} exceeds ceiling {ceiling:,}. "
        f"Estimated additional cost: {estimate:,}. Continue?",
        default=False,
    )


def decision_to_literal(decision: HitlDecision) -> ApprovalLiteral:
    return decision.value  # type: ignore[return-value]
