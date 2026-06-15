---
name: acquisition-flow
description: CrewAI Flow orchestration — intake, HITL, plan approval, kickoff in src/acquisition_helper/flow/
---

# Acquisition Flow

Primary files:
- `src/acquisition_helper/flow/acquisition_flow.py`
- `src/acquisition_helper/main.py`

Patterns:
- `@Flow` + Pydantic state (`FlowState`)
- HITL via `control/hitl.py` CLI prompts
- Persist outputs to `output/`

Do not define research agents here — delegate to crews.
