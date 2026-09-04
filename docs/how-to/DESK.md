# How-to: Desk

## Start

```powershell
$env:PYTHONPATH = "…\pocket-os\src"
python -m pocket serve --host 0.0.0.0 --port 8787
```

Open http://127.0.0.1:8787/desk  
Login: user `pocket` + password in `%USERPROFILE%\.pocket\ACCESS.txt`

## Agents (pick on home)

Codex · Grok · Claude · Assistant · Muse Spark · Auro · Aria · Plan · Build · Genetic · Coding Swarm · Browser · GitHub · NEXUS · MESIE · …

## Multi-work (Desktop + Edge)

Stay on `/desk` — do not open Spark or Crew as standalone pages.

1. Click **Spark** (or Codex / Grok) to seat one agent.
2. Click a **second** agent — the desk splits. Two panes, two composers, one window.
3. Or click **Side by side**, then pick two agents / Shift-click sessions.
4. **Spark + Grok** on the empty desk seats both at once.
5. **Crew** (More menu) is an in-window repo lane (1–2 seats). Still this Desktop/Edge app.

Deep links (same window): `/desk?split=1` · `/desk?agent=spark` · `/desk?tab=crew`

## Common modes

| Mode | Use |
|------|-----|
| codex / grok / claude | Coding |
| assist | Digital life |
| genetic | Internal model evolution |
| **multi_plan** | **Reason → tasks + sub-agents → live sovereign terminal box in chat** |
| voice | Aria talk-back |
| browser | Real Edge + tags |
| work | Working board / life ops |
| coding_swarm | Multi-agent + pixel artifacts |

## Tips

- Session tabs are clickable; bottom picker searches + resumes  
- Work Studio **Open on desk** sets handoff prompt  
- Pixel memory rail: Store / Look / Artifacts  
- Platform map: skill `platform_map` or `GET /v1/platform/coherent`  

## API

```http
POST /v1/sessions  {"mode":"genetic","title":"Gene run"}
POST /v1/sessions/{id}/messages  {"text":"hash and plan"}
```
