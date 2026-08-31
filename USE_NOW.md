# POCKET 3.7 — ship on this host

**Desk is home.** Agents are POCKET agents: they get identity + GO live board + can run `power_do` / `go` without you naming skills.

| Open | What |
|------|------|
| http://127.0.0.1:8787/desk | Codex / Grok / Power — work happens here |
| http://127.0.0.1:8787/os | Platform board (GO + 100 workflows) |
| http://127.0.0.1:8787/power | Command plane (Do it · GO) |

Ports: **Owner :8787** · **Users :8788** · **Forge :8789** (never put Forge on Users).

Say on desk: **“hit GO”**, **“what’s working”**, **“morning seatbelt”**, **“do it on the host”**. Host tools run first; the model must use those results.

---

# POCKET v0.6 — orchestration on top of your CLIs

You already have **Codex** and **Grok**. POCKET does not replace them — it **orchestrates** them.

## Open

**POCKET Owner:** http://127.0.0.1:8787/desk (shortcut **POCKET Owner**)  
**POCKET for Users:** http://127.0.0.1:8788/desk (shortcut **POCKET for Users**)

## Why POCKET is valuable

| You already have | POCKET adds |
|------------------|-------------|
| Codex CLI | Parallel multi-session desk + history |
| Grok CLI | Same + plan handoffs + research pulls |
| Local shell | **Live interactive terminals** (long-lived) |
| Manual deploys | **Static / npm / python** with **logs** |
| Guessing cost | Stream tokens + POCK meter + usage API |
| Desk-only | Phone/LAN remote of the same desk |

## Features (v0.6)

1. **Stream tokens while jobs run** — log + ~tok update every ~0.8s  
2. **+ Live term** — interactive PowerShell (not one-shot)  
3. **Deploy** — Static · **npm** · **python** (+ log button)  
4. **+ Grok agent** / **+ Codex** — your CLIs, multi-tab  
5. **+ Plan handoff** — deferred plans, not coding  

## API highlights

- `GET /v1/platform` — why POCKET + inventory  
- `POST /v1/deploy` `{kind:static|npm|python, workspace, command?}`  
- `GET /v1/deploys/{id}/log`  
- `POST /v1/terminals` · `POST /v1/terminals/{id}/send`  
- Running jobs: `log_tail`, `stream_tokens` on session messages  

## Phone

Same Wi‑Fi: `http://192.168.12.127:8787/`  
Keep PC awake. Startup: `scripts\Start-POCKET-NoAdmin.ps1`
