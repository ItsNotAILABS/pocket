# POCKET agents + WebAssembly sandbox + voice

**Status:** design + host capability layer (Python). Wasmtime optional later.  
**Audience:** founder / integrators building agent tools inside POCKET.

---

## 1. The problem

POCKET agents (Codex, Grok, custom tools, mesh workers, market seats) need to:

1. **Act** on the host (files, shell, desktop, network)  
2. **Stay useful** without becoming a full compromise of the machine  
3. **Speak and listen** when that helps the human (pair coding, support, status)

Today: safety is allowlists + RBAC + founder/market disk split. That is good host policy, but **untrusted or AI-generated tool code** still wants a tighter box than “run as the operator user.”

Wasm’s model matches how we already think about seats and tools: **zero ambient authority**, grant only what the host imports.

---

## 2. What Wasm gives us (and what it does not)

### Strengths we want

| Wasm property | POCKET use |
|---------------|------------|
| No ambient authority | Tool modules cannot touch FS/net unless granted |
| Linear memory + bounds | Guest state cannot walk host process memory |
| CFI / validated modules | Reject malformed agent plugins |
| Fast instances | Spin tool per job, discard after |
| WASI / Component Model | Typed caps: `fs:read`, `net:fetch`, `clock`, … |

### Risks we must not ignore

- Runtime bugs (compiler backends, escapes) → keep runtime patched; prefer process isolation for high risk  
- Guest can still corrupt *its own* memory (C/C++ tools)  
- Side channels on shared hardware  
- DoS without fuel/memory/timeouts  
- Over-granting caps destroys the model  

**Bottom line for POCKET:** treat Wasm (or a Wasm-*shaped* capability host) as the **default box for untrusted tools**, not as the only layer for secrets or multi-tenant crypto isolation.

---

## 3. Architecture inside POCKET

```
Human (desk / phone / voice)
        │
        ▼
   Session + agent mode (Codex / Grok / custom)
        │
        ├── trusted host path ──► executor (CLI agents, allowlisted apps)
        │
        └── tool call ──► Capability Gate ──► Sandbox instance
                                │                    │
                                │                    ├── pure compute (always)
                                │                    ├── fs:read  (paths)
                                │                    ├── fs:write (paths)
                                │                    ├── net:http (hosts)
                                │                    └── none by default
                                │
                         audit log (safety.log + sandbox receipts)
```

### Profiles (least privilege)

| Profile | Who | Caps (default) |
|---------|-----|----------------|
| `compute` | generated snippets, pure transforms | CPU + memory only, short fuel |
| `workspace_read` | research / wiki helpers | read under active workspace |
| `workspace_write` | coding agents (founder) | read/write active workspace |
| `market_seat` | invited users | tenant tree only |
| `voice_plugin` | STT/TTS side tools | no FS; may call voice API localhost |
| `untrusted` | third-party .wasm / guest code | compute only + explicit grant |

Founder desktop apps / shell stay on the **trusted path** with existing `safety.py` allowlists — not every action goes through Wasm.

---

## 4. Where Pocket Voice fits agents

Voice is not “another agent brain.” It is an **I/O modality** with the same capability discipline.

| Voice path | Agent value inside POCKET |
|------------|---------------------------|
| STT continuous | Hands-free prompts while Codex/Grok run |
| TTS / status | Speak “tests passed” / “blocked on auth” |
| Voice agent personality | Support seat, sales demo, founder brief |
| Business modes | CS routing without host shell |
| Coding+voice | Dictate into composer; commands map to desk actions |
| HTTP API (`:8790`) | Subagents / phone / friends call turns without mic on server |

### Capability rules for voice tools

- Browser STT stays in the **browser** (user gesture, HTTPS/localhost)  
- Server voice engine (`pocket-voice` API) gets **no FS/net** except what you wire  
- A mesh/subagent may call `/v1/turn` with a session id — that is a **granted HTTP capability**, not ambient host power  
- Never grant voice tools `shell` or desktop open by default  

### Practical wiring (phases)

1. **Now:** capability gate + docs; voice OSS for clients  
2. **Next:** desk 🎙 → optional `PocketVoice` stack; agent status → TTS  
3. **Later:** run guest tool modules under Wasmtime with WASI caps mapped from profiles  

---

## 5. Host capability gate (implemented)

Python module: `pocket.agent_sandbox`

- Defines profiles and grants  
- Checks path containment, host allowlists, fuel/timeouts  
- Emits **receipts** (JSON) for audit — like Wasm trap/result records  
- Optional: if `wasmtime` CLI is installed, run `.wasm` with **no preopens** unless grant says otherwise  

This is the WASI idea without waiting for full Component Model wiring: **imports are explicit**.

---

## 6. Best practices for POCKET (2026)

1. **Least privilege** — default profile `compute` or `workspace_read`  
2. **Resource limits** — every sandbox job: max_ms, max_memory_mb, fuel  
3. **Market seats** — never founder OneDrive/mesh roots  
4. **Defense in depth** — high-risk tools: OS process/container + sandbox  
5. **Validate boundaries** — all JSON/tool args checked before grant  
6. **Patch runtimes** — Wasmtime/browser engines on a cadence  
7. **Voice** — treat mic/TTS as UX caps, not privilege escalators  

---

## 7. Success criteria

Agents feel powerful **and** bounded:

- Custom tools and AI-generated helpers run in a box with receipts  
- Voice makes coding and support seats usable without new ambient power  
- Founder desk still has full power on the trusted path when *you* choose it  

---

## References (conceptual)

- Wasm sandbox / WASI capability model  
- Wasmtime fuel, memory limits, multi-tenant guidance  
- POCKET `safety.py`, `rbac.py`, `platform_space.py` (existing host policy)  
- [pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text) (voice OSS + API)
