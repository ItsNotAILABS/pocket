# Universal Agentic Harness (POCKET 3.1)

## What it does

Every primary coding agent (**Codex, Grok, Claude, plan, build, wiki, custom…**) runs inside the **agentic harness**:

1. Plans helper subagents (`@mentions` + task auto-rules)
2. Spawns them **in parallel** while the main agent works
3. Streams live status to **Workspace → Helpers** (animated)
4. Appends a **Subagents** footer to the transcript
5. Saves artifacts into **pixel memory**

## Auto rules (examples)

| Task signal | Subagent |
|-------------|----------|
| test / pytest | FORGE_HEADLESS |
| security / auth | SENTINEL_HEADLESS |
| research / benchmark | RESEARCH_HEADLESS |
| ship / release | SHIP_HEADLESS |
| ui / design / css | DESIGN |
| code / implement / fix | FORGE_HEADLESS |

Plus any explicit `@ARCHON`, `@DESIGN`, etc.

## Disable

```text
POCKET_HARNESS=0
```

Or per job: `"harness": false`.

## APIs

- `GET /v1/harness` — harness status  
- `GET /v1/harness/live` — animated running subagents  
- `GET /v1/subagents` — full roster (includes harness source)  
- `GET /v1/benchmarks/official` — integration suite  

## Benchmarks

```bash
PYTHONPATH=src python -m pocket.official_benchmarks
```

Target: **≥99%**. Official suite scores imports, Agent OS, pixel multi-way, coding swarm, harness plan/spawn, UI markers, modes, sandbox, voice path, etc.
