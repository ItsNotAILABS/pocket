# Pickup — POCKET parked 2026-09-04

**Stop here.** Resume from this file. Do not rediscover the day.

## How to pick Pocket back up

1. Read this file + `~/.pocket/PICKUP.md` + `~/.pocket/work_ledger.json`
2. Host: `python -m pocket serve --host 0.0.0.0 --port 8787` in `OneDrive/pocket-os`
3. Public: https://pocket.medinatechlabs.net/ (PhoneAI landing; kernel needs Face ID)
4. Tests: `python -m pytest tests/test_registry.py tests/test_phoneai_mcp_apps.py tests/test_host_control_policy.py tests/test_phoneai_os_and_endure.py -q`

## Last Pocket commits (pushed)

| SHA | What |
|-----|------|
| `fddff28` | 3.16.7 PhoneAI public seat, MCP apps, registry, kernel/OS, vision stills |
| `0a9a697` | `.kiln/project.json` — ships in KILN |

## Done (do not redo)

- Public tunnel = PhoneAI site; live shells gated (LAN or signup + Face ID)
- MCP apps inside kernel; phone-safe invoke
- Full registry `/v1/registry`
- Kernel grouped + search + pulse; OS live control plane
- Vision stills `/brand/vision/`
- Screen park off capture; Copilot not auto-open
- Mailbox **split to own repo** `ItsNotAILABS/pocket-mailbox` (:8792)

## Next on Pocket (when you return)

- SMTP optional send in mailbox repo
- PhoneAI Mail tile → mailbox API
- Push remaining `GROK_INBOX.md` only if you want it public (leave local)

## Other works (switch to these now)

| Work | Path / URL | Pickup |
|------|------------|--------|
| **KILN** | `E:\KILN` app (no git) + `E:\repos\KILN` → [ItsNotAILABS/KILN](https://github.com/ItsNotAILABS/KILN) `7bc4d8c` | Pocket is in `projects/registry.json`. Seed `itsnotailabs/pocket` in `E:\KILN/src/lib/kiln/seed.ts`. |
| **Sovereign Engine** | `E:\repos\sovereign-engine` → [FreddyCreates/sovereign-engine](https://github.com/FreddyCreates/sovereign-engine) `b35efa9` | Frontend `/api/v1/infra` + `/api/v1/finance`. AGENTS.md: no fake MRR. |
| **PhoneAI** | Pocket `/phoneai/app` + [ItsNotAILABS/PhoneAI](https://github.com/ItsNotAILABS/PhoneAI) | Kernel/OS live on host; Expo twin is separate repo. |
| **Mailbox** | `OneDrive/pocket-mailbox` | `python -m pocket_mailbox` |
| **Voice** | `OneDrive/pocket-voice-to-text` `89abf43` | :8790 |
| **Agent** | `OneDrive/pocket-agent` `4ea88f3` | clean |

## Law

Agents propose. Policy evaluates. Owners approve. Wallets sign. Receipts remember.
