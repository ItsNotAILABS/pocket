# POCKET — Major Charter

**Binding law:** [DOCTRINE.md](DOCTRINE.md) · machine: `GET /v1/doctrine`

**Product:** AI workspace that runs on *your* machine.  
**Company face:** public GitHub + marketing when you ship.  
**Founder face:** this tree, local desk, internal git only.

---

## Mission

Give people a **daily desk** where coding agents (Codex, Grok, Claude), planning, and host tools feel like one product — private by default, team-ready by invite, sellable without looking like a lab notebook.

---

## Non‑negotiables

1. **Founder ≠ public** — WIP never auto-publishes to customer GitHub.  
2. **Desk is home** — chat + agents + sessions; other surfaces feed the desk.  
3. **Codex and Grok stay separate** — clear names, separate sessions.  
4. **Strangers don’t get the desk** — public URL locked without login.  
5. **Voice is optional tech** — lives in open-source [pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text); POCKET consumes when needed.  
6. **Summaries must summarize** — humans read them; not log dumps.  
7. **Work Studio designs labor; desk runs it** — loops/types → handoff to sessions.

---

## What users buy

| Surface | Job to be done |
|---------|----------------|
| **Desk** | Talk to Codex/Grok, run work, see sessions |
| **Platform / Power** | GO (what is live) + do a goal on this host |
| **Work Studio** | Design multi-step work once |
| **Devices / pixel memory** | Private pass & recall on your infrastructure |
| **API** | Automate the same host |
| **Voice stack (OSS)** | Speak / listen / agent personas when product needs it |

---

## Architecture (one sentence)

Local host (`:8787`) + auth seats + agent modes + optional tunnel + optional voice modules + deliberate public release.

---

## Next polishes (priority order)

See [POLISH.md](POLISH.md).

---

## Release rule

Ship to `ItsNotAILABS/pocket` only when the story is:

> Open app → Codex or Grok → work → summary makes sense → team invite works.

Not when an internal experiment is half-done.
