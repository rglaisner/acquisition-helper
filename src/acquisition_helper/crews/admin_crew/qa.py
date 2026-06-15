"""Admin crew — QA, prompt refinement, schema enforcement."""

from __future__ import annotations

import json
import os
import re

from crewai import Agent, Crew, LLM, Process, Task

from acquisition_helper.config.loader import format_template, load_agents_config, load_tasks_config
from acquisition_helper.env import get_llm_model_pro
from acquisition_helper.models.intake import UserRequirements
from acquisition_helper.models.report import QAResult


def _make_llm() -> LLM:
    return LLM(model=get_llm_model_pro(), api_key=os.environ.get("GEMINI_API_KEY"))


def _parse_qa_result(raw: str) -> QAResult:
    try:
        data = json.loads(raw)
        return QAResult(
            passed=bool(data.get("passed", False)),
            score=float(data.get("score", 0.0)),
            feedback=str(data.get("feedback", "")),
            requires_rework=bool(data.get("requires_rework", False)),
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        passed = "pass" in raw.lower() and "fail" not in raw.lower()
        score_match = re.search(r"score[:\s]+([0-9.]+)", raw, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else (0.8 if passed else 0.4)
        return QAResult(
            passed=passed and score >= 0.7,
            score=score,
            feedback=raw[:2000],
            requires_rework=not passed,
        )


def run_admin_qa(
    requirements: UserRequirements,
    research_output: str,
    *,
    pass_threshold: float = 0.7,
) -> QAResult:
    agents_yaml = load_agents_config()
    tasks_yaml = load_tasks_config()

    variables = {
        "strategic_intent": requirements.strategic_intent,
        "sector": requirements.sector,
        "geography": requirements.geography,
        "financial_constraints": requirements.financial_constraints,
        "candidate_count": requirements.candidate_count,
    }

    critic_cfg = agents_yaml["critic_supervisor"]
    critic = Agent(
        role=str(critic_cfg["role"]),
        goal=str(critic_cfg["goal"]),
        backstory=str(critic_cfg["backstory"]),
        verbose=True,
        llm=_make_llm(),
    )

    qa_task_cfg = tasks_yaml["qa_critic"]
    qa_task = Task(
        description=(
            format_template(str(qa_task_cfg["description"]), variables)
            + f"\n\nResearch output to score:\n{research_output[:12000]}"
        ),
        expected_output=str(qa_task_cfg["expected_output"]),
        agent=critic,
    )

    crew = Crew(agents=[critic], tasks=[qa_task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    raw = result.raw if hasattr(result, "raw") else str(result)
    qa = _parse_qa_result(raw)
    if qa.score >= pass_threshold and not qa.requires_rework:
        return QAResult(passed=True, score=qa.score, feedback=qa.feedback, requires_rework=False)
    return QAResult(
        passed=False,
        score=qa.score,
        feedback=qa.feedback,
        requires_rework=True,
    )


def run_prompt_refiner(requirements: UserRequirements, qa_feedback: str) -> str:
    agents_yaml = load_agents_config()
    tasks_yaml = load_tasks_config()

    refiner_cfg = agents_yaml["prompt_refiner"]
    refiner = Agent(
        role=str(refiner_cfg["role"]),
        goal=str(refiner_cfg["goal"]),
        backstory=str(refiner_cfg["backstory"]),
        verbose=True,
        llm=_make_llm(),
    )

    refine_cfg = tasks_yaml["prompt_refine"]
    task = Task(
        description=(
            str(refine_cfg["description"])
            + f"\n\nQA feedback:\n{qa_feedback}\n\nStrategic intent:\n{requirements.strategic_intent}"
        ),
        expected_output=str(refine_cfg["expected_output"]),
        agent=refiner,
    )

    crew = Crew(agents=[refiner], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)
