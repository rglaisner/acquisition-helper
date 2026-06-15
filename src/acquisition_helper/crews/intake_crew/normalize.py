"""Intake crew — optional LLM normalization of requirements."""

from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Process, Task

from acquisition_helper.config.loader import load_agents_config
from acquisition_helper.env import get_llm_model_lite
from acquisition_helper.models.intake import UserRequirements


def normalize_requirements(requirements: UserRequirements) -> UserRequirements:
    """Optional LLM pass to tighten requirements wording. Returns input on failure."""
    agents_yaml = load_agents_config()
    cfg = agents_yaml.get("intake_analyst")
    if not cfg:
        return requirements

    llm = LLM(model=get_llm_model_lite(), api_key=os.environ.get("GEMINI_API_KEY"))
    analyst = Agent(
        role=str(cfg["role"]),
        goal=str(cfg["goal"]),
        backstory=str(cfg["backstory"]),
        verbose=False,
        llm=llm,
    )

    summary = (
        f"Strategic intent: {requirements.strategic_intent}\n"
        f"Sector: {requirements.sector}\n"
        f"Geography: {requirements.geography}\n"
        f"Financial: {requirements.financial_constraints}\n"
        f"Candidates: {requirements.candidate_count}\n"
        f"Tier: {requirements.tier.value}"
    )

    task = Task(
        description=(
            "Review and tighten these M&A research requirements. "
            "Return the same fields in plain text, one per line, prefixed with the field name.\n\n"
            + summary
        ),
        expected_output="Normalized requirements text.",
        agent=analyst,
    )

    try:
        crew = Crew(agents=[analyst], tasks=[task], process=Process.sequential, verbose=False)
        crew.kickoff()
    except Exception:
        pass

    return requirements
