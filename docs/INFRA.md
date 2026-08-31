# POCKET × PhoneAI infrastructure

Operator host `:8787`. Inventor: Alfredo Medina / ItsNotAI Labs.

## Surfaces (nothing is a leftover tab)

| Surface | Path | For |
|---------|------|-----|
| Desk | `/desk` | Owner |
| PhoneAI kernel | `/phoneai` | Phone seat |
| Portal | `/phoneai/portal` | One-screen Watch + Touch (primary monitor, not recursive) |
| Antigravity | `/phoneai/anti` | HWND stream of the real Antigravity app + window-local touch |
| Code desk | `/phoneai/work` | Engines + harness + shell |
| Agent eyes | `GET /v1/eyes?which=portal\|anti` | Agents see the same frames |
| Engines | `GET /v1/engines` | Live CLIs + internals |
| Shell | `POST /v1/phoneai/shell` | Bounded PowerShell |
| Harness | `POST /v1/phoneai/harness` | Think → shell → engine |
| Claims | `GET /v1/claims` | Defensive publication |

## Agent eyes

MCP tools: `eyes_see`, `eyes_touch`, `eyes_catalog`  
WebMCP invoke: `eyes_see_portal`, `eyes_see_anti`, `eyes_touch`  
HTTP: `GET /v1/eyes?which=portal` · `POST /v1/eyes/touch`

Touch is LAN-only. Portal blacks out its own window. Anti stream is the Antigravity HWND only.

## Workspaces the shell may use

`~/.pocket`, `OneDrive/pocket-os`, `OneDrive/PhoneAI`, `OneDrive/sovereign_forge_os`, `OneDrive/sovereign_libraries`
