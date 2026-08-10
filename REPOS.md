# POCKET repository map (ItsNotAI Labs)

Organize public surface around **product**, **agent**, **voice**, and **hub** — not personal clutter.

## Public product surface

| Repo | Role | License |
|------|------|---------|
| **[pocket](https://github.com/ItsNotAILABS/pocket)** | Core host runtime, desk, phone, Electron, genetic, Agent Mail, MCP, docs | Researcher / company |
| **[pocket-agent](https://github.com/ItsNotAILABS/pocket-agent)** | Public RLM + harness + RAH + WASM + **install slices** (agent, SDK, skills, knowledge, capsules, **mail**, plug) | MIT / research |
| **[pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text)** | Sovereign voice STT/TTS · patient VAD · multi-personality · POCKET fusion | MIT |
| **pocket-app** | User hub docs + doors (Edge/Electron/Phone) — may mirror under org | Researcher |

## Install slices (pocket-agent)

```text
install.sh / install.ps1     → full agent CLI
install/sdk.*                → Python SDK
install/skills.*             → skills pack
install/knowledge.*          → AGENTS.md + protocols
install/capsules.*           → WASM reasons + helpers
install/mail.*               → Agent Mail knowledge + skill (agents.pocket.local)
install/plug.*               → bundle
install/host.*               → host path notes
```

Live hub: `http://127.0.0.1:8787/install` when host is up.

## Desktop shells (this repo)

| Shell | Path | Notes |
|-------|------|-------|
| **Electron** | `desktop-electron/` v2.2 | Sovereign: Owner=local only; User=source picker; nav lock |
| **Edge app** | `scripts/Open-POCKET-Edge.cmd` · `.ps1` | Ensure host up → `msedge --app=/desk` |

## Local layout (this machine)

```text
OneDrive/pocket-os/          ← operator source of truth (host)
  src/pocket/                runtime (mail, genetic, web_ui, MCP, …)
  docs/ + docs/how-to/       product + how-tos
  desktop-electron/          sovereign shell
  scripts/Open-POCKET-Edge*  Edge app launchers
  REPOS.md                   ← this file

OneDrive/pocket-agent/       ← public CLI + slices → github ItsNotAILABS/pocket-agent
OneDrive/pocket-voice-to-text/ → github ItsNotAILABS/pocket-voice-to-text
OneDrive/pocket-app/         ← user hub docs

~/.pocket/                   runtime state (never commit)
  agent_mail/                agent inboxes
  genetic_flow/              genetic receipts
  mail/                      POCKET MAIL SMTP outbox
```

## What stays off public product repos

- Operator `ACCESS.txt` / secrets / `.env`  
- Founder personal OneDrive trees  
- Tenant data under `~/.pocket/tenants/`  
- Mesh keys, API key material, session tokens  

## Related lab systems (separate products)

| Repo / org | Role |
|------------|------|
| `ItsNotAILABS/*` | Company org — primary home for public lab work |
| MESIE, Auro14B, NEXUS / MERIDIAN | Spectral / LMR / intelligence — link, keep separate |
| AIFX, Parallax, etc. | Domain products — do **not** dump into pocket |

## Naming

- Product: `pocket`, `pocket-agent`, `pocket-voice-to-text`, `pocket-app`  
- Public downloads: only via `/download` after Researcher License when gated  
- Org: **ItsNotAILABS**
