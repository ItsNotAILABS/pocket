# Pickup — POCKET parked 2026-09-04 (PhoneAI screen + code desk)

**Stop here.** Switch to KILN (`E:\KILN` grok/work). Resume Pocket from this file later.

## How to pick Pocket back up

1. Read this file + `~/.pocket/PICKUP.md` + `~/.pocket/work_ledger.json`
2. Host: `python -m pocket serve --host 0.0.0.0 --port 8787` in `OneDrive/pocket-os`
3. Public: https://pocket.medinatechlabs.net/ (PhoneAI landing; kernel needs Face ID)
4. Tests: `python -m pytest tests/test_phoneai_portal.py tests/test_phoneai_code_desk.py tests/test_host_control_policy.py -q`

## PhoneAI now

- Portal `/phoneai/portal`: 1:1 laptop pane, controls under the screen, WS-only live stream
- **Keyboard does not open on screen tap.** Tap **Type** (pill) when you need it; Done hides it
- Code desk `/phoneai/work`: Grok / Codex / Meta / Gemini CLIs + GitHubs, New session is `cd-…` not an agent
- **Crew** `/crew`: one lane per repo, 1–2 agent seats side by side on different parts. You steer. No extra OS windows.

## Done (do not redo)

- Public tunnel = PhoneAI site; live shells gated (LAN or signup + Face ID)
- MCP apps inside kernel; phone-safe invoke
- Full registry `/v1/registry`
- Kernel grouped + search + pulse; OS live control plane
- Vision stills `/brand/vision/`
- Screen park off capture; Copilot not auto-open
- Mailbox **split to own repo** `ItsNotAILABS/pocket-mailbox` (:8792)
- Code desk unmixed from personas/agents
- Portal 1:1 + no auto-keyboard

## Next on Pocket (when you return)

- SMTP optional send in mailbox repo
- PhoneAI Mail tile → mailbox API
- Meta Muse Code CLI on PATH if you want that desk lane live
- Push remaining `GROK_INBOX.md` only if you want it public (leave local)

## Other works (switch to these now)

| Work | Path / URL | Pickup |
|------|------------|--------|
| **KILN workspace** | `E:\KILN` (`grok/work`) + Codex `E:\workspaces\kiln-codex` (`codex/work`) → [ItsNotAILABS/kiln-workspace](https://github.com/ItsNotAILABS/kiln-workspace) `cb6b184` | Live site https://kiln-git.grok.me/. Domain later: `kiln.medinatechlabs.net` (`docs/DOMAIN.md`). Read `E:\KILN\WORKSPACE.md`. |
| **KILN Foundry L1** | `E:\repos\KILN` → [ItsNotAILABS/KILN](https://github.com/ItsNotAILABS/KILN) | Registry includes kiln-workspace, pocket, mailbox, sovereign-engine. |
| **Sovereign Engine** | `E:\repos\sovereign-engine` → [FreddyCreates/sovereign-engine](https://github.com/FreddyCreates/sovereign-engine) `b35efa9` | Frontend `/api/v1/infra` + `/api/v1/finance`. AGENTS.md: no fake MRR. |
| **PhoneAI** | Pocket `/phoneai/app` + [ItsNotAILABS/PhoneAI](https://github.com/ItsNotAILABS/PhoneAI) | Kernel/OS live on host; Expo twin is separate repo. |
| **Mailbox** | `OneDrive/pocket-mailbox` | `python -m pocket_mailbox` |
| **Voice** | `OneDrive/pocket-voice-to-text` `89abf43` | :8790 |
| **Agent** | `OneDrive/pocket-agent` `4ea88f3` | clean |

## Law

Agents propose. Policy evaluates. Owners approve. Wallets sign. Receipts remember.
