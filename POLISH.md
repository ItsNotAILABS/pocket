# POCKET — Next polishes

Priority stack after charter. Check off as done.

## P0 — Daily desk feels solid

- [x] Codex / Grok separation restored  
- [x] Session tabs clickable; login gate not blocking  
- [x] More agents scrollable  
- [x] Bottom agent picker (search + resume session)  
- [x] Live session summary (readable)  
- [x] Agent picker: keyboard ↑↓ Enter  
- [x] Empty state always wired to `pickAgent`  
- [x] Host auto-restart never leaves hung :8787  
- [x] Voice ↔ Voice = specialized agent only (not all chats)  
- [x] Live stream banner + caret + compact code snippets  
- [x] Mic chrome: dictation vs Voice agent labels  

## P1 — Connected product

- [x] Work Studio → desk handoff  
- [x] Work Studio “Run on desk” for each loop card  
- [x] Agent Mail UI + accounts @agents.pocket.local  
- [x] Genetic desk mode + docs/how-tos + `/v1/catalog`  
- [x] Website UI engines + python_engine MCP  
- [x] Phone UI same agent labels as desk  
- [x] Pixel memory: store last chat turn one-click  

## P2 — Voice + agent sandbox

Repo: https://github.com/ItsNotAILABS/pocket-voice-to-text  
Design: `docs/research/POCKET_AGENT_WASM_SANDBOX.md`

- [x] STT continuous  
- [x] TTS + agent + personalities + business + coding demos  
- [x] HTTP API + tests on voice repo  
- [x] Capability sandbox module (`agent_sandbox.py`) + `/v1/sandbox/*`  
- [x] Voice plugin profile → localhost voice API only  
- [x] Desk Voice ↔ Voice specialized agent (patient VAD + speak back)  
- [x] Claude Agent SDK bridge for Claude desk mode  
- [ ] Optional vendor under `vendor/pocket-voice`  
- [ ] Optional voice agent personality for phone support mode  
- [ ] Wasmtime guest runner hardened (preopens only on grant)  
- [ ] Custom agent tools default to `untrusted` / `compute` profile

## P3 — Sell / market

- [ ] One-page pricing story (plain language)  
- [ ] Public README = customer face only  
- [ ] Demo video script: desk 60s  
- [ ] Promote path documented (internal → public)  

## P4 — Reliability

- [x] Health endpoint returns edition + app_url (via `/health`)  
- [ ] Vision never freezes host accept loop  
- [ ] Ensure-POCKET-Up on login failure toast  

---

**Charter:** [CHARTER.md](CHARTER.md)  
**Founder split:** [FOUNDER.md](FOUNDER.md)  
**Version:** 2.2.0  
