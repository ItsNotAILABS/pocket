# How-to: One-line install slices

Hub UI: **http://127.0.0.1:8787/install**  
Catalog: `GET /v1/install/slices` (or slices embedded in hub HTML)

## Slices

| Slice | What you get |
|-------|----------------|
| agent | Full POCKET Agent install |
| sdk | Python SDK |
| skills | Skills pack |
| knowledge | App knowledge for agents |
| capsules | WASM capsule bits |
| plug | Plug-n-play agent profile |
| host | Point at this host |
| **mail** | **Agent Mail** knowledge + skill (`agents.pocket.local`) |

## One-liners (GitHub raw — when published)

```bash
# Unix
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install.sh | sh
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/sdk.sh | sh
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/skills.sh | sh
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/knowledge.sh | sh
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/plug.sh | sh
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/mail.sh | sh
```

```powershell
# Windows
irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install.ps1 | iex
irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/sdk.ps1 | iex
irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/mail.ps1 | iex
```

## From this host (mirror)

When the host is up, the hub also shows host-mirrored one-liners:

```text
curl -fsSL http://127.0.0.1:8787/install/sdk.sh | sh
irm http://127.0.0.1:8787/install/sdk.ps1 | iex
```

## Repo layout

`pocket-agent/install/slices.json` + scripts.  
Runtime: `pocket.install_hub`.
