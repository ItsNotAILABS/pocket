# POCKET screen family protocols

**Family:** `pocket.screen.family.v1`  
**Date:** 2 September 2026  
**Inventor:** Alfredo Medina / ItsNotAI Labs  

These are the wire contracts for PhoneAI Portal, vLaptop, pocket-agent embodiment, pairing, origin trust, and the always-on host. Implementations live in POCKET `:8787`. Clients: PhoneAI Kernel, vLaptop, pocket-sdk.

Live: `GET /v1/protocols` · `GET /v1/protocols/{slug}` · `GET /v1/contracts`

---

## Family map

| Protocol | Slug | Speaks |
|---|---|---|
| **SCREEN-KERNEL/1.1** | `screen-kernel` | see · touch · type · click · cursor |
| **pocket.stream.v1** | `stream` | JSON envelope then JPEG on Portal WS |
| **pocket.screen.body.v1** | `screen-body` | Agent inhabits the kernel |
| **pocket.device.pair.v1** | `device-pair` | Code + WebAuthn → revocable `portal_device` |
| **pocket.origin.v1** | `origin` | Exact hosts only |
| **pocket.runtime.singleton.v1** | `runtime` | One attested watchdog |
| **pocket.agent.arch.v1** | `agent-arch` | identity → seat → route → authority → execute → receipt |
| **pocket.screen.matrix.v1** | `screen-matrix` | 3×3 affine `nx,ny` → desktop pixel |

Hostname is never authority. Tunnel names do not mint seats.

---

## 1. SCREEN-KERNEL/1.1

**Schema:** `pocket.screen.kernel.v1`

Coordinates are always **unit square of the visible frame** (`nx, ny ∈ [0,1]`), not of the last HWND.

### Verbs

| Verb | HTTP | Body |
|---|---|---|
| see | `POST /v1/screen/see` | `{ which: desktop\|tv\|anti }` |
| touch | `POST /v1/screen/touch` | `{ kind, nx, ny, target?, hwnd? }` |
| type | `POST /v1/screen/type` | `{ text, nx, ny, click_first?, submit? }` |
| click | `POST /v1/screen/click` | `{ name }` |
| cursor | (via kernel snapshot / body) | — |
| embody | `POST /v1/screen/embody` | `{ agent, which }` |

`kind`: `hover` | `tap` | `hold` | `down` | `up` | `drag` | `scroll` | `right` | `key`.

**Rules**

1. Green cursor is the real mouse. Hover moves it; tap clicks there.
2. Type targets the field at `nx,ny` (UIA ValuePattern, else keys).
3. Named click is accessibility Name, not OCR-only.
4. Desktop taps are HWND-agnostic.
5. Humans (phone, glasses, TV) and agents share these verbs.

---

## 2. pocket.stream.v1

**Transport:** `WS /v1/phoneai/portal/ws`  
**Hello (text opcode 1):**

```json
{
  "ok": true,
  "kind": "hello",
  "schema": "pocket.stream.v1",
  "protocol": "SCREEN-KERNEL/1.1",
  "embody": true,
  "ws": true,
  "spatial": true
}
```

**Each frame:** text opcode 1 (envelope) then binary opcode 2 (JPEG):

```json
{
  "kind": "frame",
  "schema": "pocket.stream.v1",
  "seq": 1842,
  "geom": { "x": 0, "y": 0, "w": 1920, "h": 1080, "hwnd": 0 },
  "matrix": [[1920, 0, 0], [0, 1080, 0], [0, 0, 1]],
  "via": "primary",
  "bytes": 48120
}
```

Client `cfg` JSON: `{ "kind": "cfg", "max_w", "q", "fps", "target", "hwnd" }`.  
Client touch JSON uses SCREEN-KERNEL verbs on the same socket.

**Matrix:** column `[nx, ny, 1]` × `M` → desktop pixel. Same as `pocket.screen.matrix.v1`.

---

## 3. pocket.screen.body.v1

An agent **is** the pointer. Not a screenshot tool.

```
POST /v1/screen/embody   { "agent": "coder", "which": "desktop" }
GET  /v1/screen/body
POST /v1/screen/body     { "verb": "see|touch|type_into|click_name|cursor|leave", ... }
```

MCP: `screen_embody` `screen_see` `screen_touch` `screen_type` `screen_click` `screen_cursor`

Occupant is stored under `~/.pocket/screen_body.json`. One occupant at a time. Leave releases it.

pocket-agent / vLaptop:

```python
from pocket_sdk import Pocket
Pocket().embody("pocket-agent")
```

---

## 4. pocket.device.pair.v1

Away-from-home pairing. A 6-digit code is **not** a founder credential.

1. LAN/PC: `POST /v1/auth/device/mint` → 6-digit code, 10 minutes.
2. Phone on **exact origin**: `GET /v1/auth/device/begin` → WebAuthn **create**.
3. `POST /v1/auth/device/redeem` `{ code, credential }`.
4. Host issues principal `device:<id>`, role `portal_device`, identity-bound Portal cookie, WorkGrant capability `portal`.

**Cannot** shell, RAH, vault, install. Visual Portal only.

Revoke: `POST /v1/auth/device/revoke` `{ id }` (LAN or owner).  
List: `GET /v1/auth/device/list`.

---

## 5. pocket.origin.v1

Allowed origin host is **exact**:

- request `Host`
- loopback / RFC1918 LAN
- hostname of `POCKET_PUBLIC_URL` (default `pocket.medinatechlabs.net`)
- each host in `POCKET_ALLOWED_ORIGINS`

**Not allowed:** `*.medinatechlabs.net`, `*.trycloudflare.com`, parent-domain WebAuthn `rpId`.

`rpId` = exact request host.

---

## 6. pocket.runtime.singleton.v1

One watchdog.

- Lock: `~/.pocket/runtime.lock` (process-attested, msvcrt/fcntl).
- Second `python -m pocket runtime` exits.
- Install: Startup VBS only (no extra ONLOGON task unless `POCKET_RUNTIME_TASK=1`).
- Hung-port kill: only `python`/`pythonw` on the Pocket port.
- Ports: `GET /v1/runtime/ports` lists all; `POST /v1/runtime/ports/maintain` only heals owned listeners.

---

## 7. pocket.agent.arch.v1

Layers: `identity → seat → route → authority → execute → receipt`.

Seats: `pocket` | `phoneai` | `node` | `screen`.  
Execute lanes: harness, rah, invoke, talk, session, plan, **screen**.

Screen lane: wording such as “embody the screen” → `screen_embody` → inhabit + see/touch/type.

WorkGrant required before RAH execute. Device pair never grants RAH.

---

## Objects

| Schema | Meaning |
|---|---|
| `pocket.screen.kernel.v1` | Shared verbs |
| `pocket.stream.v1` | WS envelope + JPEG |
| `pocket.screen.body.v1` | Occupant record |
| `pocket.screen.matrix.v1` | 3×3 affine |
| `pocket.device.pair.v1` | Mint / begin / redeem |
| `pocket.origin.v1` | Exact origin set |
| `pocket.runtime.singleton.v1` | Watchdog lock |
| `pocket.agent.arch.v1` | Turn plane |
| `pocket.portal.session.v1` | Identity-bound Portal cookie |
| `pocket.node.view.v1` | TV as view node |

---

## Clients

| Client | Speaks |
|---|---|
| PhoneAI Kernel | stream + kernel + device-pair |
| vLaptop 1.1 | kernel + embody + body |
| pocket-sdk 0.3 | kernel + embody |
| MCP pocket | screen_* tools |

## Authority

| Caller | see | touch | shell |
|---|---|---|---|
| LAN | yes | yes | founder |
| Owner seat | yes | yes | yes |
| `portal_device` | yes | yes | **no** |
| Public hostname alone | no | no | no |
