# Acquisition Helper — Agent Registry

M&A SME acquisition research — dual registry for **Cursor dev agents** and **CrewAI runtime agents**.

## Skill resolution order

1. **Cursor built-ins** — `C:\Users\remyg\.cursor\skills-cursor\<name>\SKILL.md`
2. **User skills** — `C:\Users\remyg\.agents\skills\<name>\SKILL.md`
3. **Project overlays** — `.cursor/skills/<name>/SKILL.md`

**Rule:** One agent = one skill. Supervisor routes; build agents edit code.

---

## Cursor dev agents

| Agent | Skill | Primary files |
|-------|-------|---------------|
| **SupervisorAgent** | `crew-orchestration` | Routes only |
| **FlowAuthorAgent** | `acquisition-flow` | `src/acquisition_helper/flow/`, `main.py` |
| **CrewAuthorAgent** | `m-and-a-research` | `crews/research_crew/`, `config/` |
| **ControlLayerAgent** | `control-layer` | `control/` |
| **ToolsAuthorAgent** | `crew-tools` | `tools/` |
| **GuardianAgent** | `proactive-guardian` | Pre-change scan |
| **VerificationAgent** | `verification-before-completion` | `~/.agents/skills/` |
| **DebugAgent** | `systematic-debugging` | `~/.agents/skills/` |
| **PatternLearningAgent** | `pattern-error-learning` | `docs/learnings.md` |

---

## Runtime production agents (CrewAI)

### Flow steps

| Step | Module |
|------|--------|
| Intake | `flow/acquisition_flow.py` + `crews/intake_crew/` |
| Plan | `control/flow_planner.py` |
| Research | `crews/research_crew/` (tiered) |
| Admin QA | `crews/admin_crew/` |
| Report | `reporting/markdown_report.py` |

### Research crew (Expert tier — 11 agents)

| ID | Role |
|----|------|
| `explorer` | Data Infrastructure & Source Explorer |
| `director` | M&A Scoping Director |
| `profiler` | SME Operations Profiler |
| `financier` | LBO Financial Modeler |
| `sourcer` | Deal Flow Origination Specialist |
| `tech_architect` | Tech-Debt & Integration Architect |
| `workforce_analyst` | Workforce Dynamics Analyst |
| `risk_assessor` | Structural Risk & Deal-Killer Assessor |
| `validator` | Output Validation Supervisor |
| `red_teamer` | Strategic Red Teamer |
| `reporter` | Executive M&A Briefing Architect |

### Admin agents (control + admin_crew)

WorkflowOrchestrator, IntakeAnalyst, FlowPlanner, BudgetMonitor, ComplianceValidator, RedTeamTester, CriticSupervisor, PromptRefiner, SchemaEnforcer, GuardrailsEngine, TraceLogger.

---

## Supervisor routing examples

| User intent | Agent chain |
|-------------|-------------|
| Change tier matrix | ControlLayer → Guardian → Verification |
| Add Serper to sourcer | ToolsAuthor → m-and-a-research → Verification |
| HITL / Flow change | FlowAuthor → ControlLayer → Verification |
| Fix budget threshold | ControlLayer → Verification |

---

## Known failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `GEMINI_API_KEY is not set` | Missing env | Copy `.env.example` → `.env` |
| Partial report on interrupt | Ctrl+C mid-run | See `output/` partial markdown |
| Token HITL loop | Exceeded profile ceiling | Approve or use `essential` tier |

See also `docs/learnings.md`.

---

## Rules index

| Rule | Path |
|------|------|
| Project rules | `.cursor/rules/project-rules.mdc` |
| Agent safety | `.cursor/rules/agent-safety.mdc` |
| Layer routing | `.cursor/rules/layer-routing.mdc` |
| HITL checkpoints | `.cursor/rules/hitl-checkpoints.mdc` |
| Verification gate | `.cursor/rules/verification-gate.mdc` |
