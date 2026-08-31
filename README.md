<p align="center">
  <img src="docs/brand/pocket-mark.svg" width="120" alt="POCKET"/>
</p>

<h1 align="center">POCKET</h1>

<p align="center">
  <strong>Multi-agent workstation and enterprise control plane.</strong><br/>
  Desktop · Edge · Cloud account · teams · policy · devices · agents · voice · APIs
</p>

## Use on this PC

Sign in without the Edge password box:

- [http://127.0.0.1:8787/v1/auth/desktop/enter](http://127.0.0.1:8787/v1/auth/desktop/enter)
- Desk: [http://127.0.0.1:8787/desk](http://127.0.0.1:8787/desk)
- PhoneAI: [http://127.0.0.1:8787/phoneai](http://127.0.0.1:8787/phoneai)

`GET /v1/phoneai/sessions` mints a Pocket or PhoneAI session. Agents think first (`route_think`) and use at most one tool.

**Invention claims (Alfredo Medina, ItsNotAI Labs, 31 Aug 2026):** [docs/research/INVENTION_CLAIMS_2026.md](docs/research/INVENTION_CLAIMS_2026.md) — Portal stream, Antigravity desktop-app view, twin mint, WebMCP work functions. Defensive publication.

**Portal** (first-class PC stream): [http://127.0.0.1:8787/phoneai/portal](http://127.0.0.1:8787/phoneai/portal)  
**Antigravity** (HWND stream + touch): [http://127.0.0.1:8787/phoneai/anti](http://127.0.0.1:8787/phoneai/anti)  
**Agent eyes:** `GET /v1/eyes?which=portal` · `GET /v1/eyes?which=anti` · MCP `eyes_see` / `eyes_touch`  
Infra map: [docs/INFRA.md](docs/INFRA.md)

## What POCKET is

POCKET is the user/team/policy envelope for the wider ItsNotAI Labs runtime. It gives people one place to use local agents, voice, models, tools and devices while keeping identity, tenancy, policy, approvals, audit and product routing in one control plane.

```text
Users / Teams / Devices
          │
          ▼
        POCKET
          │
          ├── identity + organizations
          ├── RBAC / policy / approvals
          ├── device pairing
          ├── routing + capability discovery
          ├── quotas + idempotency
          ├── audit + incidents
          ├── health / readiness
          ├── Desk / Phone / Mail / Work UI
          └── Cloud account + install channels
          │
          ▼
NEXUS federation
  ├── Pocket Voice
  ├── POCKET Agent
  ├── MatDaemon
  ├── CAPSULA
  ├── Medina Memory
  └── model / connector / research runtimes
```

## Product channels

| Channel | Purpose |
|---|---|
| **POCKET Desktop** | Installable Electron application with bundled local host and tray/startup integration |
| **POCKET Edge App** | Existing local engine in a dedicated Microsoft Edge app window |
| **POCKET Cloud Account** | Cloudflare Worker + D1 + R2 account, organizations, invites, devices, task relay and entitlement plane |
| **POCKET API** | Versioned local/cloud APIs for agents, voice, teams, work, mail, models and tools |

Read [`docs/POCKET_PRODUCT_CHANNELS_V3.md`](docs/POCKET_PRODUCT_CHANNELS_V3.md).

## Core product surfaces

| Surface | Path |
|---|---|
| Desk | `/desk` |
| PhoneAI website | `/phoneai` |
| PhoneAI kernel | `/phoneai/app` |
| Setup / always-on | `/setup` · `python -m pocket install` |
| Phone | `/phone` |
| Voice Studio | `/studio/voice` |
| Docs | `/docs` |
| Agent Mail | `/mail` |
| Install hub | `/install` |
| Work Studio | `/work` |
| LOOMGRAPH | `/loomgraph` |
| Tour | `/tour` |
| Get/install | `/get` |
| Developer API | `/developers` |
| Health | `/health` |
| Catalog | `/v1/catalog` |
| Ready/class | `/v1/ready` · `/v1/class` |

## Control-plane intelligence

POCKET now includes deterministic control-plane helpers for decisions that should not live inside prompts:

- capability routing with confidence and review fallback;
- policy decisions: `allow`, `deny`, `confirm`;
- tenant/principal/action-scoped idempotency;
- quota evaluation;
- approval records for privileged operations;
- audit events;
- incident objects;
- secret references that point to operator-managed credentials rather than copying secret values;
- dependency health aggregation;
- release-state classification from machine-readable evidence.

The ecosystem declaration is [`ecosystem.surface.json`](ecosystem.surface.json).

## POCKET family protocols

Canonical family objects include:

```text
pocket.family.v1
pocket.context-snap.v1
pocket.execution-receipt.v1
```

NEXUS extends the family with shared objects for tasks, plans, policy, budgets, jobs, leases, retries, health, telemetry, memory, artifacts, approvals and handoffs.

Machine-readable schemas live under the repository protocol/schema documentation added to the Alpha control plane.

## Build POCKET Desktop

Windows:

```powershell
.\scripts\Build-POCKET-Desktop-Exe.ps1 -Arch auto
```

Build x64 and Windows ARM64:

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

The desktop host reuses a healthy local engine instead of repeatedly restarting it.

## Run the local host

Use the repository's documented host launcher for your platform, then open:

```text
http://127.0.0.1:8787/desk
```

Useful checks:

```text
GET /health
GET /v1/ready
GET /v1/catalog
```

## Deploy POCKET Cloud

Provision the Cloudflare resources described in [`docs/POCKET_CLOUD_ACCOUNT.md`](docs/POCKET_CLOUD_ACCOUNT.md), configure protected environment values, then run:

```powershell
$env:POCKET_D1_DATABASE_ID = "your-d1-id"
.\scripts\Deploy-POCKET-Cloud.ps1
```

The Cloud account provides the always-online identity/organization/device plane while local workstations remain execution substrates.

## Enterprise tenancy

POCKET separates:

- user identity;
- organization membership;
- owner/admin/member/viewer roles;
- paired device identity;
- local market/seat identity;
- agent/session identity;
- project/workspace scope.

Cloud organizations use D1-backed membership and invitation records. A paired device receives a restricted device key rather than inheriting the founder/operator session.

See [`docs/MULTI_USER.md`](docs/MULTI_USER.md).

## Device and execution model

```text
User intent
   │
   ▼
POCKET identity + tenant scope
   │
   ▼
Policy decision
   │
   ├── deny ──► denial receipt
   ├── confirm ──► approval surface
   └── allow
          │
          ▼
Capability route
          │
          ▼
Agent / Voice / PhoneAI / CAPSULA / MatDaemon
          │
          ▼
Artifact + execution receipt + audit event
```

This gives browser, desktop, mobile and API clients the same operating model instead of separate ad-hoc permissions.

## POCKET Agent

[POCKET Agent](https://github.com/ItsNotAILABS/pocket-agent) handles long-running execution, durable goals, recursive agent harnesses, schedules, capsules, budgets, retries, leases and receipts.

Typical family flow:

```text
POCKET request
  -> agent.run
  -> bounded long-running work
  -> artifacts
  -> pocket.execution-receipt.v1
  -> POCKET activity / audit / memory
```

## Pocket Voice

[Pocket Voice](https://github.com/ItsNotAILABS/pocket-voice-to-text) handles patient turn-taking, STT control, personas, agentic voice flows, Voice Studio context and provider resilience.

POCKET hosts same-origin product surfaces and can hand long-running voice work to POCKET Agent.

## PhoneAI

[PhoneAI](https://github.com/ItsNotAILABS/PhoneAI) is the mobile workstation-control surface. Its production MVP supports paired sessions, real bounded local filesystem/Git/system operations, execution receipts and revocation.

## Agent Mail

POCKET includes its own agent mail namespace:

```text
*@agents.pocket.local
```

UI:

```text
/mail
```

API:

```text
/v1/agent-mail/*
```

Install slice:

```bash
curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/master/install/mail.sh | sh
```

## Install slices

The POCKET family can be installed by capability rather than as one monolith:

```text
agent
sdk
skills
knowledge
capsules
mail
plug
```

Catalog: [`pocket-agent/install/slices.json`](https://github.com/ItsNotAILABS/pocket-agent/blob/master/install/slices.json)

## Enterprise operating model

A strong deployment separates four planes:

```text
Cloud account plane
  identity / org / entitlement / device relay

Local host plane
  private workstation data / local tools / local models

Execution plane
  POCKET Agent / CAPSULA / MatDaemon / connectors

Evidence plane
  receipts / audit / artifacts / health / release evidence
```

Recommended controls:

```text
[ ] tenant scope on every externally reachable mutation
[ ] role/capability checks before privileged actions
[ ] idempotency on retried mutations
[ ] per-key / per-tenant quotas
[ ] request IDs across cross-repo hops
[ ] approval object for irreversible actions
[ ] health + readiness endpoints
[ ] artifact hashes and execution receipts
[ ] revocable device sessions
[ ] separate rollback and data-recovery procedures
```

## Release and packaging

Canonical release documentation:

- [`docs/POCKET_RELEASE_RUNBOOK.md`](docs/POCKET_RELEASE_RUNBOOK.md)
- [`docs/POCKET_PRODUCT_CHANNELS_V3.md`](docs/POCKET_PRODUCT_CHANNELS_V3.md)
- [`docs/POCKET_CLOUD_ACCOUNT.md`](docs/POCKET_CLOUD_ACCOUNT.md)
- [`ENTERPRISE.md`](ENTERPRISE.md)
- [`SECURITY.md`](SECURITY.md)
- [`ALPHA.md`](ALPHA.md)

Desktop packaging includes checksum-oriented artifact workflows and separate local/cloud/Edge launch modes.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/INDEX.md`](docs/INDEX.md) | master platform map |
| [`docs/HOW_TO.md`](docs/HOW_TO.md) | operator recipes |
| [`docs/how-to/AGENT_MAIL.md`](docs/how-to/AGENT_MAIL.md) | agent mail |
| [`docs/how-to/GENETIC_FLOW.md`](docs/how-to/GENETIC_FLOW.md) | internal model composition |
| [`docs/how-to/WEB_UI_ENGINES.md`](docs/how-to/WEB_UI_ENGINES.md) | model-driven UI engines |
| [`docs/how-to/MCP.md`](docs/how-to/MCP.md) | MCP integration |
| [`docs/how-to/INSTALL.md`](docs/how-to/INSTALL.md) | install channels |
| [`docs/how-to/API_RECIPES.md`](docs/how-to/API_RECIPES.md) | API recipes |

## Ecosystem

| Component | Role |
|---|---|
| [NEXUS](https://github.com/ItsNotAILABS/nexus) | federation and protocol authority |
| [POCKET Agent](https://github.com/ItsNotAILABS/pocket-agent) | long-running execution |
| [Pocket Voice](https://github.com/ItsNotAILABS/pocket-voice-to-text) | conversation control |
| [PhoneAI](https://github.com/ItsNotAILABS/PhoneAI) | mobile device/workstation control |
| [CAPSULA](https://github.com/ItsNotAILABS/CAPSULA) | isolated runtime/build capsules |
| [MatDaemon](https://github.com/ItsNotAILABS/MatDaemon) | bounded compute |
| [Medina Memory](https://github.com/ItsNotAILABS/MedinaMemorySystems) | durable continuity |

Repository: https://github.com/ItsNotAILABS/pocket
