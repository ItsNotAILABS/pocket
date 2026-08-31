# How-to: Multi-plan · live sovereign terminal

When you pick **Multi-plan** on the desk (or use mode `multi_plan`), the agent:

1. **Reasons** about your goal  
2. Builds a **task list** with **sub-agents** (ARCHON, SCRUTATOR, FORGE, …)  
3. **Executes** tasks in order (can expand more if something fails)  
4. Streams everything into a **sovereign WSL-style terminal box** in the chat  

## Desk

1. Open `/desk` (hard-refresh once after update)  
2. Pick **Multi-plan**  
3. Send a multi-part goal, e.g.  
   `Research agent mail then check inbox and summarize`

A green **wsl · multi-plan** terminal pops in the agent bubble:

- traffic-light title bar  
- `$ goal` line  
- **reason** paragraph  
- task rows (○ pending · ● running · ✓ done · ✗ failed) with agents  
- scrolling live log  
- footer: done N/M · expanded · run_id  

While running, the box updates live (session poll + `update_progress`).

## API / skill

```http
POST /v1/multi-plan/run
{"goal":"Research X then mail assist a summary"}
```

```json
{"skill":"multi_plan","prompt":"…"}
```

```python
from pocket.multi_plan import run_multi_plan
run_multi_plan("Research pocket then list mail accounts")
```

Modes: `multi_plan` · `multiplan` · `plan_exec` · `agentic_plan`

## Sub-agents used

ARCHON · SCRUTATOR · FORGE · SENTINEL · OCULUS · PORTARIUS · SCRIBE · NAVIGATOR · GHOST · GENETIC · SHIP · VCOMP · AURO

## Adaptive expansion

If a task fails, multi-plan can append a recovery task (up to 3 expansions) and keep going until the budget is hit.
