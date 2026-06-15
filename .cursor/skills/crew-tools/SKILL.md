---
name: crew-tools
description: Serper and custom CrewAI tools for Explorer and Deal Sourcer agents
---

# Crew Tools

Paths:
- `src/acquisition_helper/tools/serper_tool.py`
- `src/acquisition_helper/tools/registry.py`

Requires `SERPER_API_KEY` in `.env`. Assign tools only to agents that need web search (explorer, sourcer).

Use `crewai_tools.SerperDevTool` when available; fall back gracefully if key missing.
