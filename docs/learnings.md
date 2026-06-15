# Acquisition Helper — Collaborative Learnings

Append recurring patterns and fixes here (see `.cursor/rules/learnings.mdc`).

## Known failures

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `GEMINI_API_KEY is not set` | Missing `.env` | Copy `.env.example` → `.env` and set key |
| `Google Gen AI SDK is not installed` | `crewai` installed without `[google-genai]` extra | Run `uv sync` or reinstall with `pip install -e .` |
| Partial report on Ctrl+C | Interrupt mid-crew | Check `output/` for partial markdown; resume via checkpoint if enabled |
| Token threshold HITL | Budget exceeded | Approve continuation or lower tier / `CONTROL_PROFILE=conservative` |
| Serper tool errors | Missing `SERPER_API_KEY` | Set key or run without web search (Essential tier) |
