"""Research crew factory — builds tiered Crew from YAML + registry."""

from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task

from acquisition_helper.config.loader import format_template, load_agents_config, load_tasks_config
from acquisition_helper.control.agent_registry import TierSpec, get_tier_spec
from acquisition_helper.env import get_llm_model_lite, get_llm_model_pro
from acquisition_helper.models.intake import TierName, UserRequirements
from acquisition_helper.tools.serper_tool import get_tools_for_agent


def _make_llm(*, model: str) -> LLM:
    return LLM(model=model, api_key=os.environ.get("GEMINI_API_KEY"))


def _build_agent(
    agent_id: str,
    agent_cfg: dict[str, Any],
    *,
    variables: dict[str, Any],
    use_pro: bool,
    tools: list[Any],
) -> Agent:
    model = get_llm_model_pro() if use_pro else get_llm_model_lite()
    return Agent(
        role=format_template(str(agent_cfg.get("role", agent_id)), variables),
        goal=format_template(str(agent_cfg.get("goal", "")), variables),
        backstory=format_template(str(agent_cfg.get("backstory", "")), variables),
        verbose=True,
        llm=_make_llm(model=model),
        tools=tools,
    )


def build_research_crew(requirements: UserRequirements) -> Crew:
    spec = get_tier_spec(requirements.tier)
    agents_yaml = load_agents_config()
    tasks_yaml = load_tasks_config()

    variables: dict[str, Any] = {
        "strategic_intent": requirements.strategic_intent,
        "sector": requirements.sector,
        "geography": requirements.geography,
        "financial_constraints": requirements.financial_constraints,
        "candidate_count": requirements.candidate_count,
    }

    agents: dict[str, Agent] = {}
    for agent_id in spec.agent_ids:
        cfg = agents_yaml.get(agent_id)
        if not cfg:
            raise ValueError(f"Missing agent config for '{agent_id}'")
        tools = get_tools_for_agent(agent_id, spec.agents_with_tools)
        agents[agent_id] = _build_agent(
            agent_id,
            cfg,
            variables=variables,
            use_pro=agent_id in spec.pro_model_agents,
            tools=tools,
        )

    task_objects: dict[str, Task] = {}
    ordered_tasks: list[Task] = []

    for task_id in spec.task_ids:
        task_cfg = tasks_yaml.get(task_id)
        if not task_cfg:
            raise ValueError(f"Missing task config for '{task_id}'")
        agent_key = str(task_cfg.get("agent", ""))
        agent = agents.get(agent_key)
        if agent is None:
            raise ValueError(f"Task '{task_id}' references unknown agent '{agent_key}'")

        context_ids = spec.task_context.get(task_id, ())
        context_tasks = [task_objects[cid] for cid in context_ids if cid in task_objects]

        task = Task(
            description=format_template(str(task_cfg.get("description", "")), variables),
            expected_output=str(task_cfg.get("expected_output", "")),
            agent=agent,
            context=context_tasks or None,
            async_execution=bool(task_cfg.get("async_execution", task_id in spec.parallel_tasks)),
        )
        task_objects[task_id] = task
        ordered_tasks.append(task)

    return Crew(
        agents=list(agents.values()),
        tasks=ordered_tasks,
        process=Process.sequential,
        verbose=True,
    )


def kickoff_research(requirements: UserRequirements) -> object:
    crew = build_research_crew(requirements)
    return crew.kickoff()
