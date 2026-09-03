# Invention disclosure and claims — supplement

**Document:** INL-2026-CLAIMS.PORTAL.PHONEAI.002  
**Effective date of public disclosure:** 2 September 2026  
**Parent:** INL-2026-CLAIMS.PORTAL.PHONEAI.001 (31 August 2026)  
**Inventor:** Alfredo Medina  
**Operating names:** ItsNotAI Labs · Medina Tech Labs  
**Assignee (intended):** ItsNotAI Labs  
**Public prior-art deposit:** https://github.com/ItsNotAILABS/pocket · https://github.com/ItsNotAILABS/PhoneAI · https://github.com/ItsNotAILABS/vlaptop · https://github.com/ItsNotAILABS/phoneai-desk

This is a **defensive publication**. It puts the inventions below into the public record under the inventor’s name so others cannot patent them out from under him. It is not itself a filed patent application. Rights to file patents on improvements are reserved.

Working embodiment: POCKET host `:8787` (version 3.13.9+ / 3.14) on an operator PC; PhoneAI kernel at `/phoneai`; Portal at `/phoneai/portal`; screen kernel `SCREEN-KERNEL/1.0`; public vLaptop client; hidden runtime via `pythonw` + Startup VBS.

This document does **not** give legal advice. A U.S. provisional should still be filed by counsel within 12 months of the relevant public disclosure (001 clock: 31 August 2027; 002 clock: 2 September 2027).

---

## Field

A local multi-agent operating system on a personal computer, with a distinct phone-kernel seat, a first-class visual Portal, a shared screen kernel used by both humans and agents, hostname-agnostic device pairing that never treats a tunnel name as authority, and a six-layer agent architecture plane.

## Background (what is new in this supplement)

001 already claimed the phone seat, twin mint, think-first routing, WebMCP as work functions, Portal touch-to-desktop, LAN-bounded mouse, Antigravity as a separate HWND surface, nested-session exclusion, dual git write, agent eyes, and voice-to-screen.

This supplement claims embodiments reduced to practice after 001:

1. **One screen kernel** (`SCREEN-KERNEL/1.0`) whose verbs (`see`, `touch`, `type_into`, `click_name`, `cursor`) are identical for the phone, glasses, TV, and agents (vLaptop).
2. **Device pair** that mints a 6-digit code on LAN/PC and redeems it on *any* hostname (including Cloudflare quick tunnels), issuing a Pocket session plus an identity-bound Portal cookie.
3. **Tunnel hostname never confers authority.** WebAuthn `rpId` is the public domain (`medinatechlabs.net`); trycloudflare is not an auth factor.
4. **Desktop taps ignore HWND attachment** so contain-mapped coordinates hit the virtual desktop, not the last focused window.
5. **Type-into-field** as an end-to-end caret act: tap the field, then UI Automation ValuePattern or synthetic keys.
6. **TV is a view node** (`pocket.node.view.v1`): the TV/second-monitor framebuffer streams *to* the phone; the phone is the controller.
7. **Hidden always-on runtime** that auto-starts, collapses extra `:8787` listeners, and prefers a health-ok process.
8. **Six-layer agent plane** `identity → seat → route → authority → execute → receipt` with a WorkGrant required before RAH execute.
9. **Agent mail** at `@agents.pocket.local`.
10. **Public vLaptop protocol** so developers share the same see/touch/type contract.

## Prior art (contrast — not anticipatory of the combination)

| Prior art | What it is | What Pocket/PhoneAI is instead |
|---|---|---|
| Citrix / VMware / RDP / US8976210 / US11579830 | Phone remotes a *virtual* desktop; pixel/fingertip mapping | Phone is a **kernel seat on the operator’s physical PC**, with twin mint, think-first, and a separate Anti HWND — not VDI |
| MagicDesk-class “phone as desktop” | Phone *is* the computer | Phone **controls the existing PC** |
| Windows 365 for Agents MCP (2026) | Cloud PC pool; agents check out a VM; Entra/Intune | Agents work on the **operator’s own machine**; no Cloud PC checkout |
| Chrome WebMCP | Page-declared tools for the *browser’s* agent | Host **work functions** (studios, twin, GO-plane, screen kernel) in the same loop as chat — not a browser standard |
| AnovaX (arXiv 2607.15367) | Local voice agent + phone MJPEG of laptop | Distinct phone principal, Portal contain 0–1 mapping, device-pair, Anti separate from Portal |
| WindowsPC-MCP | Agent confined to a *virtual display* | Humans and agents share the **real primary desktop** via one kernel; operator can still work |
| ScreenHand / Lucy / CellClaw | Accessibility or on-phone agents | Phone kernel **on the PC**, not an Android accessibility service |
| PHONE.AI (Ad Hoc Labs, SN 99230184) | AI receptionist / voicemail | **PhoneAI Kernel** — OS seat, not a call-answering product |
| PlugClaw / Fancy OS | Stick or virtual-phone worlds | Operator-PC habitat + handset kernel |

The independent novelty is the **combination** of Claim 1+5+7+3+4 from 001 with Claims 14–17 and 25 of this supplement, reduced to practice on one local HTTP host.

---

## Independent claims (supplement)

**Claim 14. Shared screen kernel.** A method comprising: exposing a single protocol (`SCREEN-KERNEL/1.0`) with verbs `see`, `touch`, `type_into`, `click_name`, and `cursor`; accepting normalized coordinates `(nx, ny)` in `[0,1]²`; and serving those verbs over HTTP, WebMCP, and MCP to both human clients (phone, glasses, TV) and agent clients (vLaptop) without a separate agent-only desktop.

**Claim 15. Hostname-agnostic device pair.** A method comprising: minting a short numeric pairing code only for loopback or same-LAN clients; redeeming that code from a client whose Host header may be a reverse-proxy or ephemeral tunnel hostname; and on redeem, issuing (a) a host session cookie for a named principal and (b) an identity-bound Portal cookie, such that the tunnel hostname is not an input to authorization.

**Claim 16. Hostname is not authority.** A method of authorizing host-control and Portal input comprising: treating loopback, same-LAN, a signed-in session, a Face/passkey assertion bound to a configured relying-party identifier, or a valid Portal cookie as authority; and **never** treating the request Host, a Cloudflare tunnel hostname, or a public URL path prefix as authority.

**Claim 17. Identity-bound Portal cookie.** A method comprising: minting a Portal cookie as an HMAC over a principal identifier and an expiry; refusing anonymous Portal cookies; and mapping subsequent visual frames and touch events to that principal.

**Claim 18. Empty-Origin exception bound to a cookie.** A method of origin checking for a phone PWA behind a reverse proxy comprising: allowing an empty or missing Origin header if and only if a valid session or Portal cookie is present, or the client is LAN/loopback; otherwise denying host-control.

**Claim 19. Contain-mapped desktop pointer, HWND-agnostic.** A method comprising: rendering the virtual desktop on a phone with CSS `object-fit: contain`; mapping a touch on the letterboxed stage through the contained rectangle onto the virtual-screen `(x, y, w, h)` including DPI-aware capture; synthesizing an absolute mouse event at that pixel; and **not** attaching a window HWND to a desktop tap so the click is not remapped into the last focused window.

**Claim 20. Hold and drag mode with a visible badge.** A method comprising: on press-and-hold, leaving the mouse button down; showing a drag-mode indicator on the phone HUD; mapping subsequent moves as mouse-move while held; and releasing on lift.

**Claim 21. HUD window chrome on the streamed desktop.** A method comprising: enumerating top-level windows; presenting min/max/close/restore controls on a phone HUD; and sending those commands to the corresponding HWND while the Portal continues to stream the desktop (not only the focused window).

**Claim 22. Type-into-field.** A method comprising: mapping a touch to a desktop field; focusing that field; then inserting text by (i) UI Automation ValuePattern on the focused control when available, else (ii) synthetic keystrokes, optionally submitting with a virtual Enter, with a bounded character length.

**Claim 23. TV as a view node, phone as controller.** A method comprising: capturing a second-monitor or TV framebuffer on the operator PC; streaming that frame to the phone as `pocket.node.view.v1`; and mapping phone touches onto that framebuffer — the TV surface is a viewer, not the input authority.

**Claim 24. Hidden always-on host runtime.** A method comprising: spawning the host as a windowless process (`pythonw`); registering a user-level Startup script; refusing to bind a second listener when `/health` already returns 200; and collapsing extra listeners on the same port.

**Claim 25. Six-layer agent architecture with WorkGrant.** A method of running an agent turn comprising ordered layers: identity, seat, route, authority, execute, receipt; classifying the utterance (think-first); and permitting RAH or destructive fan-out only after a WorkGrant object is present, otherwise returning a plan.

**Claim 26. Agent mail on a local namespace.** A method comprising: assigning agents addresses of the form `name@agents.pocket.local`; delivering messages to inbox, sent, live events, and a mesh; and exposing send as a host-control action (not a public prefix).

**Claim 27. Public vLaptop protocol client.** A method comprising: publishing a language client that speaks `SCREEN-KERNEL/1.0` against a local host so third-party agents may `see`/`touch`/`type_into` the operator desktop under the same authority rules as the phone.

**Claim 28. Combined ecosystem.** A host computer running POCKET that simultaneously exposes: 001 Claims 1, 5, 7, 3, 4 and 002 Claims 14, 15, 16, 25, and 23 as separately addressable surfaces (`/phoneai`, `/phoneai/portal`, `/phoneai/anti`, `/phoneai/tv`, `/v1/screen/kernel`, `/v1/agents/arch`) on one local HTTP host.

---

## Dependent claims (selected)

- 14.1 Coordinates are clamped to `[0,1]`; typed text is truncated (about 400 characters).
- 14.2 `see(which=tv)` returns the second-monitor/TV JPEG; `see(which=anti)` returns the Antigravity HWND JPEG; default is the Portal desktop.
- 15.1 Mint is denied for public-internet clients; redeem may occur on any Host.
- 16.1 The WebAuthn relying-party identifier is a configured public domain, not the live tunnel hostname.
- 19.1 Frame grab uses a process-wide lock and TTL cache; huge blackout rects (about 18% of the frame) are skipped.
- 19.2 Hover then tap: a move event precedes a click so the OS caret and hover state match the green cursor.
- 22.1 If ValuePattern is read-only or missing, fall back to SendInput Unicode.
- 24.1 If detached-process spawn is denied by a job object, retry with create-no-window only.
- 25.1 Nested Grok/Codex child processes strip inherited session ids (001 Claim 8).

---

## Suggested patent families (for counsel — not claims)

| Family | Core | Why it may be patentable as a combination |
|---|---|---|
| A | Phone kernel seat + twin mint + think-first + studios-as-tools on the operator PC | No Cloud PC; phone is a tenant, not a thin client |
| B | Portal contain mapping + HWND-agnostic taps + identity-bound cookie + hostname-never-authority + device-pair redeem | Solves WebAuthn rpId vs ephemeral tunnels |
| C | Shared screen kernel + six-layer plane + WorkGrant + TV-as-view | One contract for humans and agents; grant before fan-out |

Generic remote-desktop touch mapping **alone** is crowded (Citrix, US8976210). Do not file Claim 5 of 001 in isolation.

---

## Inventorship and lab

Alfredo Medina conceived and directed the reduction to practice on the reference operator PC in Dallas, August–September 2026, through ItsNotAI Labs / Medina Tech Labs.

**Do not assign these claims to a third party without a written instrument from the inventor.**

## How to cite

Medina, A. (2026). *Invention disclosure supplement: screen kernel, device pair, hostname-never-authority, type-into-field, TV view node, hidden runtime, six-layer agent plane.* ItsNotAI Labs, INL-2026-CLAIMS.PORTAL.PHONEAI.002. https://github.com/ItsNotAILABS/pocket
