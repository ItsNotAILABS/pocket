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
| Portal | `/phoneai/portal` | Spatial Fit/Fill of the PC. Live WebSocket JPEG + instant touch. 5G uses smaller faster frames. Session cookie required off-LAN. |
| Agents | `/agents` | Names, faces, DMs, group chats, Agent Mail |
| TV | `/phoneai/tv` | Same-Wi-Fi 16:9 stream + touch |
| Doorbell | `/phoneai/doorbell` | Home camera MJPEG/HTTP |
| PC cam | `/phoneai/cam` | Laptop webcam only after PC Allow |
| Antigravity | `/phoneai/anti` | HWND stream of the real Antigravity app + window-local touch |
| Code desk | `/phoneai/work` | Coder persona (Grok, KEEP, whole family repos) + harness + shell |
| Coder | `GET /v1/phoneai/coder` | Long-term Grok coding agent seated on PhoneAI |
| Agent eyes | `GET /v1/eyes?which=portal\|anti` | Agents see the same frames |
| Engines | `GET /v1/engines` | Live CLIs + internals |
| Shell | `POST /v1/phoneai/shell` | Bounded PowerShell |
| Harness | `POST /v1/phoneai/harness` | Think → shell → engine |
| Claims | `GET /v1/claims` · `GET /claims` | Defensive publication 001+002 |
| Marks | `GET /v1/marks` · `GET /marks` | Trademark clearance registry |
| Screen kernel | `GET /v1/screen/kernel` | SCREEN-KERNEL/1.1 |
| Screen body | `POST /v1/screen/embody` · `GET /v1/screen/body` | Agents inhabit the live pointer |
| Stream | `WS /v1/phoneai/portal/ws` | `pocket.stream.v1` JSON envelope + JPEG |
| Screen family protocols | `GET /v1/protocols/screen-family` | Kernel, stream, body, pair, origin, runtime, arch |
| Glasses HUD | `/phoneai/glasses` | Glance cards (no JPEG until Stream). Wake word PhoneAI. Camera → Coder. |
| AirPods | `/phoneai/airpods` | Always listen waits for PhoneAI …. Dictation until send. |
| Wear | `POST /v1/phoneai/wear` | Wake, glance, spatial left/right window, dictation, HUD heartbeat, camera |
| Live web | `/phoneai/web` | Agent previews and project pages |
| Voice → screen | `POST /v1/phoneai/voice-screen` | Click named UI, scroll, right-click, open URL |

## Agent eyes

MCP tools: `eyes_see`, `eyes_touch`, `eyes_catalog`, `screen_embody`, `screen_see`, `screen_touch`, `screen_type`, `screen_click`  
WebMCP invoke: `eyes_see_portal`, `eyes_see_anti`, `eyes_touch`  
HTTP: `GET /v1/eyes?which=portal` · `POST /v1/eyes/touch`

Touch is LAN, signed-in, or the named tunnel. Portal blacks out its own window. Anti stream is the Antigravity HWND only.

## Agent social + cron + steer + browser

| Action | Path |
|--------|------|
| People + faces | `GET /v1/agents/people` · `GET /v1/agents/face/{id}.svg` |
| DM | `POST /v1/agents/dm` |
| Email | `POST /v1/agents/email` (`@agents.pocket.local`) |
| Groups | `POST /v1/agents/groups` · `POST /v1/agents/groups/post` |
| Cron memory | `GET /v1/cron/memory?days=1\|7` |
| Steer sub-agent | `POST /v1/subagents/steer` |
| Drive desktop browser | `POST /v1/browser/drive` |

MCP: `agent_people`, `agent_dm`, `agent_email`, `agent_group_post`, `subagent_steer`, `cron_memory`, `browser_drive`, `web_ui_drive`.

## Always-on

Register servers in runtime (`pocket.host_runtime`). PhoneAI and Pocket agents call `runtime_ensure`.

```text
python -m pocket ensure
python -m pocket install
```

`install` writes `~/.pocket/run-pocket-runtime.cmd`, a logon scheduled task, and a Startup shortcut. Keep the PC awake.

## Workspaces the shell may use

`~/.pocket`, `OneDrive/pocket-os`, `OneDrive/PhoneAI`, `OneDrive/sovereign_forge_os`, `OneDrive/sovereign_libraries`
