"""Serper web search tool wiring."""

from __future__ import annotations

import os
from typing import Any


def get_serper_tool() -> Any | None:
    if not os.environ.get("SERPER_API_KEY"):
        return None
    try:
        from crewai_tools import SerperDevTool

        return SerperDevTool()
    except ImportError:
        return None


def get_tools_for_agent(agent_id: str, agents_with_tools: tuple[str, ...]) -> list[Any]:
    if agent_id not in agents_with_tools:
        return []
    tool = get_serper_tool()
    return [tool] if tool is not None else []
