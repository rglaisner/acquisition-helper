# Acquisition Helper

AI-driven M&A research pipeline for SME platform acquisition targets. Built with [CrewAI](https://docs.crewai.com/en/introduction) **Flows** (orchestration) and **Crews** (tiered research agents).

## Features

- **CLI intake wizard** with human-in-the-loop approval gates
- **Tiered agent complexity**: Essential (3) → Expert (11) production agents
- **Admin control layer**: budget monitoring, QA loops, flow planning, Mermaid diagrams
- **Markdown reports** with execution logs and token usage

## Quick start

```bash
# 1. Create virtual environment and install
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
# or with uv:
uv sync

# Gemini models require the google-genai SDK (included via crewai[google-genai] in pyproject.toml).

# 2. Configure environment
copy .env.example .env
# Edit .env — set GEMINI_API_KEY (required), SERPER_API_KEY (optional)

# 3. Run interactive flow
crewai run
# or
python -m acquisition_helper.main

# Legacy shim (deprecated)
python Baseline.py
```

## Tiers

| Tier | Agents | Use case |
|------|--------|----------|
| `essential` | 3 | Fast executive brief |
| `standard` | 7 | Sourcing + finance + validation |
| `advanced` | 10 | + tech, workforce, risk deep-dive |
| `expert` | 11 | Full Baseline parity + red team |

## Control profiles

| Profile | Token ceiling | HITL frequency |
|---------|---------------|----------------|
| `conservative` | Lower | More gates |
| `standard` | Default | Balanced |
| `aggressive` | Higher | Fewer interrupts |

Set via `CONTROL_PROFILE` in `.env` or during CLI intake.

## Output

- `output/SME_Platform_Acquisition_Report.md` — final report
- `output/workflow_plan.md` — Mermaid workflow diagram + agent table

## Project layout

```
src/acquisition_helper/
├── main.py           # CLI entry
├── flow/             # AcquisitionFlow
├── crews/            # intake, research, admin crews
├── control/          # registry, budget, planner, HITL
├── models/           # Pydantic schemas
├── tools/            # Serper search
├── config/           # YAML agents/tasks/defaults
└── reporting/        # Markdown assembly
```

## Development

See `AGENTS.md` for Cursor dev agent registry and `.cursor/rules/` for coding standards.

```bash
pytest tests/
python -m py_compile src/acquisition_helper/main.py
```

## License

Private / internal use.
