---
name: control-layer
description: Budget monitor, flow planner, HITL, agent registry, control profiles
---

# Control Layer

Paths: `src/acquisition_helper/control/`

| Module | Role |
|--------|------|
| `agent_registry.py` | Tier → agent IDs + task DAG |
| `flow_planner.py` | Mermaid + workflow plan |
| `budget_monitor.py` | Token tracking + HITL threshold |
| `hitl.py` | CLI approve/edit/cancel |
| `profiles.py` | conservative / standard / aggressive |
| `guardrails.py` | PII/secret scan |

Ported from Scraper_Intel `js/control/` patterns — Python, no LLM required for core logic.
