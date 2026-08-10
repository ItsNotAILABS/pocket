# POCKET Desktop (Electron) — sovereign shell

Electron shell for the local POCKET host UI. Dark window, single-instance, secure defaults.

**Version:** 2.2.0 · **App ID:** `com.medinatech.pocket`  
**Lab:** ItsNotAI Labs · Medina Tech Labs

## Sovereignty doctrine

| Rule | Implementation |
|------|----------------|
| Host-first | Operator role always loads **local** `127.0.0.1:8787` |
| No password storage | Config stores desk URL only — never seat keys / passwords |
| Sandboxed renderer | `contextIsolation` · `nodeIntegration: false` · `sandbox` · `webSecurity` |
| Navigation lock | Only the chosen desk origin navigates in-window; other https → system browser |
| Never kill healthy host | Quit closes Electron only |
| Separate profiles | Owner vs User `userData` so both can run |

## Requirements

- Node.js 18+ and npm
- Python with POCKET installable as `python -m pocket` (for local host)
- Host URL default: **http://127.0.0.1:8787/**

## Production run

### Option A — launcher (host + Electron)

From **pocket-os** repo root:

```powershell
.\scripts\Start-POCKET-Electron.ps1
```

### Option B — Electron only (auto-starts host)

```powershell
cd desktop-electron
npm.cmd install
npm.cmd start
```

If port 8787 is down, **main.js** spawns `python -m pocket serve` (local, detached).

### Operator vs User

```powershell
# Sovereign owner (local host only, no onboarding)
$env:POCKET_CLIENT_ROLE = "operator"
npm start

# User seat (source picker: team cloud / this PC / custom URL)
$env:POCKET_CLIENT_ROLE = "user"
npm start
```

## Menu (2.2)

| Menu | Action |
|------|--------|
| Open desk | `/desk` |
| Docs hub | `/docs` |
| Agent Mail | `/mail` |
| Install slices | `/install` |
| Work Studio | `/work` |
| Phone | `/phone` |
| Help → ecosystem | ItsNotAILABS/pocket · pocket-agent · pocket-voice |

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `POCKET_URL` | — | Override desk base (legacy) |
| `POCKET_ROOT` | parent of `desktop-electron` | Repo root for `python -m pocket serve` |
| `POCKET_PYTHON` | auto / `python` | Python executable |
| `POCKET_CLIENT_ROLE` | `user` (packaged) | `operator` / `owner` / `user` |
| `POCKET_PUBLIC_URL` | pocket.medinatechlabs.net | Default cloud desk for onboarding |
| `POCKET_DEV` | unset | Set `1` for DevTools |

## Security (production defaults)

| Setting | Value |
|---------|-------|
| `contextIsolation` | `true` |
| `nodeIntegration` | `false` |
| `sandbox` | `true` |
| `webSecurity` | `true` |

External **http(s)** links open in the system browser only.  
**Never** opens `file://` scripts as documents via shell.

## Package scripts

```bash
npm start          # node run-electron.js
npm run pack       # electron-builder --dir
npm run dist       # Windows NSIS + portable
npm run dist:arm64
npm run dist:x64
```

## Ecosystem

| Product | Repo |
|---------|------|
| Host runtime | [ItsNotAILABS/pocket](https://github.com/ItsNotAILABS/pocket) |
| Agent + slices | [ItsNotAILABS/pocket-agent](https://github.com/ItsNotAILABS/pocket-agent) |
| Voice | [ItsNotAILABS/pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text) |
| Edge app window | `scripts/Open-POCKET-Edge.cmd` / `.ps1` |
