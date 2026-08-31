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
