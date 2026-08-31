# POCKET × PhoneAI infrastructure

Operator host `:8787`. Inventor: Alfredo Medina / ItsNotAI Labs.

## Surfaces (nothing is a leftover tab)

| Surface | Path | For |
|---------|------|-----|
| Desk | `/desk` | Owner |
| PhoneAI website | `/phoneai` | Professional intro before the app (tunnel this) |
| PhoneAI kernel | `/phoneai/app` | Phone seat |
| Setup | `/setup` | Account · host · always-on · open |
| Runtime | `GET /v1/runtime` · `POST /v1/runtime/ensure` | Servers inside the product; agents bring them up |
| Portal | `/phoneai/portal` | Live PC on the phone. Per-window focus makes that app the main window. Phone-only zoom, L/R, drag, joystick, live type |
| Antigravity | `/phoneai/anti` | HWND stream of the real Antigravity app + window-local touch |
| Code desk | `/phoneai/work` | Engines + harness + shell |
| Agent eyes | `GET /v1/eyes?which=portal\|anti` | Agents see the same frames |
| Engines | `GET /v1/engines` | Live CLIs + internals |
| Shell | `POST /v1/phoneai/shell` | Bounded PowerShell |
| Harness | `POST /v1/phoneai/harness` | Think → shell → engine |
| Claims | `GET /v1/claims` | Defensive publication |
| Glasses HUD | `/phoneai/glasses` | Meta glasses / any HUD browser — stream + voice-to-screen |
| Live web | `/phoneai/web` | Agent previews and project pages |
| Voice → screen | `POST /v1/phoneai/voice-screen` | Click named UI, scroll, right-click, open URL |

## Agent eyes

MCP tools: `eyes_see`, `eyes_touch`, `eyes_catalog`  
WebMCP invoke: `eyes_see_portal`, `eyes_see_anti`, `eyes_touch`  
HTTP: `GET /v1/eyes?which=portal` · `POST /v1/eyes/touch`

Touch is LAN-only. Portal blacks out its own window. Anti stream is the Antigravity HWND only.

## Always-on

Register servers in runtime (`pocket.host_runtime`). PhoneAI and Pocket agents call `runtime_ensure`.

```text
python -m pocket ensure
python -m pocket install
```

`install` writes `~/.pocket/run-pocket-runtime.cmd`, a logon scheduled task, and a Startup shortcut. Keep the PC awake.

## Workspaces the shell may use

`~/.pocket`, `OneDrive/pocket-os`, `OneDrive/PhoneAI`, `OneDrive/sovereign_forge_os`, `OneDrive/sovereign_libraries`
