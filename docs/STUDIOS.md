# How Studios integrate with the Desk

POCKET has **one home** (the Desk) and two studios that feed it.

```
┌─────────────────────────────────────────────────────────────┐
│  DESK  /desk                                                │
│  Codex · Grok · sessions · voice mic · pixel memory         │
│  ← daily product surface                                    │
└──────────────▲──────────────────────────▲───────────────────┘
               │ handoff                  │ handoff
               │ (prompt + agent)         │ (demo copy → Grok)
    ┌──────────┴──────────┐    ┌──────────┴──────────┐
    │  WORK STUDIO /work  │    │ PRODUCT STUDIO      │
    │  Design types/loops │    │ /studio             │
    │  dual · swarm       │    │ Recordings → demos  │
    └─────────────────────┘    └─────────────────────┘
```

## Work Studio (`/work`)

| | |
|--|--|
| **Job** | Design *how* agents should work (types, loops, dual-loop, swarm) |
| **Not** | Day-to-day chat with Codex/Grok |
| **To Desk** | “Send Build to desk”, loop generate confirm, `sendToDesk(mode, prompt)` |
| **Mechanism** | `localStorage.pocket_work_handoff` + `/desk?agent=…` |
| **APIs** | `/v1/work-studio`, `/v1/work-loops/*`, `/v1/dual`, `/v1/swarm/*` |

## Product Studio (`/studio`)

| | |
|--|--|
| **Job** | Turn host recordings into marketing demos (phone/web frames, exports) |
| **Not** | Agent labor design or multi-session chat |
| **To Desk** | “Send caption to Desk (Grok)” for copy polish |
| **APIs** | `/v1/studio/product_phone`, `/v1/studio/product_web`, record/* |

## Desk (`/desk`)

| | |
|--|--|
| **Job** | Chat with agents, run work, sessions, summary, devices, pixel memory |
| **Consumes** | Handoffs from both studios; sandbox for custom tools; optional voice API |

## Auth

Studios share the same cookies/tokens as Desk (`pocket_token` / desktop auto-login on localhost).

## Sandbox

Custom agents and tool-like actions use `agent_sandbox` profiles so studio-generated work still cannot ambient-access the founder disk when running as market tools.
