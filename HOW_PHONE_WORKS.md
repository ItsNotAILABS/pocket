# How the phone actually works

## Product

**POCKET Phone** is a remote control for agents on your PC — with **Aria** and **Working** as first-class voice agents, plus plan/code/research.

1. Phone opens the LAN URL (same Wi‑Fi as the lab PC).
2. **Pair** away from home with a 6-digit PC code **plus Face ID on this phone**. The code alone is not an owner login.
3. Sign in with your seat (same as desk).
4. Pick **Aria** / **Working** / Plan / Code / …
5. Talk (🎙) or type. PC worker runs the agent.
6. Phone polls until done; Aria replies can speak via TTS.
7. Conversational Fusion on the host routes multi-domain travel help.

## First-class voice

| Mode | What it is |
|------|------------|
| **Aria** | Voice ↔ Voice agent · patient listening · Fusion metadata |
| **Working** | Live voice + host screen/hardware + package → handoff |
| Plan / Code / Grok / Novae | Same remote desk modes as before |

## Pair with desk (seamless)

1. **On PC desk:** Workspace panel → **Get pair code** (or Nodes).
2. **On phone:** open `/phone` → enter code on unlock screen or **More → Pair with desk**.
3. Chip shows **Linked · &lt;host&gt;**; transfers + presence use `X-Pocket-Node-Token`.
4. Sign in for agent sessions (pair alone is not a full seat).

| API | Role |
|-----|------|
| `POST /v1/node/pair` | Desk mints code |
| `POST /v1/node/redeem` | Phone redeems → `pair_token` |
| `POST /v1/fusion/voice` | Host Deep Fusion for Aria turns |
| `POST /v1/sessions` | Phone creates Aria/Working sessions |

## URLs

| Who | URL |
|-----|-----|
| Phone (same Wi‑Fi) | `http://<your-pc-lan-ip>:8787/phone` |
| PC browser / Edge | `http://127.0.0.1:8787/desk` |
| Phone manifest | `/phone/manifest.webmanifest` (Add to Home Screen) |

## Not this

- Fake instant “AI reply” with no PC work  
- Dead mailbox / queue you never see again  
- Broken public tunnel as the only path  

## Windows + OneDrive note

Codex sandbox can fail on raw `...\OneDrive\...` paths. POCKET may map folders with `subst` so agents can write for real.

## Claude

If Claude Code CLI is on PATH, use Claude mode from the full desk (phone focuses Aria/Working + primary engines).
