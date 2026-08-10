<p align="center">
  <img src="docs/brand/pocket-mark.svg" width="120" alt="POCKET"/>
</p>

<h1 align="center">POCKET</h1>

<p align="center">
  <b>Company multi-agent workstation</b><br/>
  ItsNotAI Labs · Medina Tech Labs<br/>
  Desktop app · Edge app · Cloudflare account · team seats · sellable API
</p>

---

## Product channels

POCKET is no longer one development server exposed through a tunnel.

| Channel | Purpose |
|---|---|
| **POCKET Desktop** | Installable Electron app with a bundled local `pocket-host.exe`, Desktop/Start-menu shortcuts, tray mode, and optional start-at-login. |
| **POCKET Edge App** | The same local engine in a Microsoft Edge app window for users who prefer the existing Edge surface. |
| **POCKET Cloud Account** | Independent Cloudflare Worker + D1 + R2 account, organization, invitation, paired-device, task relay, and entitlement-gated download plane. |

Read [POCKET Product Channels v3](docs/POCKET_PRODUCT_CHANNELS_V3.md).

### Availability rule

- Opening Electron or the Edge launcher starts or reuses the packaged local engine.
- A healthy engine is never restarted.
- An unknown listener is never killed automatically.
- The Cloudflare account stays online without depending on the operator's local port or Cloudflare Tunnel.
- A paired desktop only needs to be online when a cloud task requires local execution.

## Isolation

- **Owner/operator** — full local founder host.
- **Cloud organization members** — their own account and organization role.
- **Local market members** — their own credentials and tenant sandbox.
- A paired cloud device receives a restricted `sk_pocket_*` key, not the founder owner session.

## Build POCKET Desktop

```powershell
.\scripts\Build-POCKET-Desktop-Exe.ps1 -Arch auto
```

Build both Windows architectures:

```powershell
.\scripts\Build-POCKET-Desktop-Exe.ps1 -Arch both
```

Developer modes:

```powershell
cd desktop-electron
npm install
npm run start:local
npm run start:cloud
npm run start:edge
```

## Deploy POCKET Cloud

Provision D1 and R2 once, configure `BOOTSTRAP_TOKEN` and `RELEASE_ADMIN_TOKEN`, then:

```powershell
$env:POCKET_D1_DATABASE_ID = "your-d1-id"
.\scripts\Deploy-POCKET-Cloud.ps1
```

Validate the generated Worker URL before changing any existing tunnel or production DNS. See [POCKET Cloud Account](docs/POCKET_CLOUD_ACCOUNT.md).

## Existing local surfaces

| Surface | URL |
|---|---|
| Desk | `/desk` |
| Phone | `/phone` |
| **Docs hub** | `/docs` |
| **Agent Mail** | `/mail` |
| Install slices | `/install` |
| Work Studio | `/work` |
| LOOMGRAPH | `/loomgraph` |
| Overview | `/tour` |
| Get/install | `/get` |
| API | `/developers` |
| Health | `/health` |
| Live catalog | `/v1/catalog` |
| Class / ready | `/v1/class` · `/v1/ready` |

## Documentation

| Doc | What |
|-----|------|
| [docs/INDEX.md](docs/INDEX.md) | Master platform map |
| [docs/HOW_TO.md](docs/HOW_TO.md) | How-to recipe index |
| [docs/how-to/AGENT_MAIL.md](docs/how-to/AGENT_MAIL.md) | Our agent email + inboxes |
| [docs/how-to/GENETIC_FLOW.md](docs/how-to/GENETIC_FLOW.md) | Internal models · genetic |
| [docs/how-to/WEB_UI_ENGINES.md](docs/how-to/WEB_UI_ENGINES.md) | Models drive websites via Python |
| [docs/how-to/MCP.md](docs/how-to/MCP.md) | MCP for Grok/Claude/Cursor |
| [docs/how-to/INSTALL.md](docs/how-to/INSTALL.md) | One-line install slices |
| [docs/how-to/API_RECIPES.md](docs/how-to/API_RECIPES.md) | Copy-paste APIs |

HTML hub on a running host: **http://127.0.0.1:8787/docs**

---

## Ecosystem (ItsNotAI Labs)

| Product | Repo | What it is |
|---------|------|------------|
| **POCKET host** | [ItsNotAILABS/pocket](https://github.com/ItsNotAILABS/pocket) | This repo — desk, phone, MCP, genetic, mail, install hub |
| **POCKET Agent** | [ItsNotAILABS/pocket-agent](https://github.com/ItsNotAILABS/pocket-agent) | Long-running CLI + **one-line slices** (agent, SDK, skills, knowledge, capsules, **mail**, plug) |
| **Pocket Voice** | [ItsNotAILABS/pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text) | Sovereign STT/TTS · patient VAD · multi-personality agents |
| **Desktop (Electron)** | `desktop-electron/` in this repo | **Sovereign shell** v2.2 — local host or team desk; never stores passwords |
| **Edge app** | `scripts/Open-POCKET-Edge.cmd` | Edge `--app=` window for desk (host auto-up) |

### New product uses (v3.6+)

| Use | How |
|-----|-----|
| **Agent Mail** | Our own `*@agents.pocket.local` accounts + inboxes · UI `/mail` · API `/v1/agent-mail/*` · slice `install/mail.sh` |
| **Genetic flow** | Internal models as modules · desk **Genetic** · `POST /v1/genetic/run` |
| **Website UI engines** | Models drive sites via Python MCP (`web_ui_*`, `python_engine`) — not user MCP tabs |
| **Install slices** | One-liners for agent, SDK, skills, knowledge, capsules, **mail**, plug · `/install` |
| **Docs hub** | `/docs` + how-tos under `docs/how-to/` · live `GET /v1/catalog` |
| **RAH** | Recursive full harness fan-out · `POST /v1/rah/run` |
| **KEEP / ISOLATE / RECALL** | Agents until chat ends · isolated browsers · recall codes |
| **Sovereign Electron** | Operator = local only · User = source picker · navigation locked to desk origin |
| **Edge desk** | `scripts/Open-POCKET-Edge.cmd` · production host ensure + app window |

```bash
# Agent Mail slice (any machine)
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/mail.sh | sh
# Windows: irm …/install/mail.ps1 | iex
```

---

## Multi-user

Cloud organizations use D1-backed owner/admin/member/viewer memberships and expiring invite codes. The existing local host retains its separate seat system and founder/market isolation.

See [docs/MULTI_USER.md](docs/MULTI_USER.md) and [docs/POCKET_PRODUCT_CHANNELS_V3.md](docs/POCKET_PRODUCT_CHANNELS_V3.md).

## Evidence boundary

A merged source branch is not proof of a live Cloudflare deployment or a downloadable Windows binary. Those claims require the protected deployment workflow, Windows release artifacts, checksums, and clean-install evidence in [docs/POCKET_RELEASE_RUNBOOK.md](docs/POCKET_RELEASE_RUNBOOK.md).

## Repository

https://github.com/ItsNotAILABS/pocket
