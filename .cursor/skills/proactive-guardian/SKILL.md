---
name: proactive-guardian
description: Pre-change risk scan — token blow-up, YAML/agent ID mismatch, missing tools
---

# Proactive Guardian

Before merging crew or tier changes:

1. Every task `agent:` key exists in agents YAML for that tier
2. `agent_registry.py` tier lists match YAML filenames
3. Expert tier task `context` references valid task IDs
4. Adding agents increases estimated token range — flag if > `TOKEN_BUDGET`
5. No secrets in YAML or Python literals
