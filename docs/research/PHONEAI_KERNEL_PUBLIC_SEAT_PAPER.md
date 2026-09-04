# PhoneAI as a Public Seat: Named Tunnel, Signup, Face ID, and a Locked Live Kernel

**Paper ID:** INL-2026-PHONEAI.SEAT.001  
**Date:** 4 September 2026  
**Lab:** ItsNotAI Labs (Dallas)  
**Thesis:** The public URL is PhoneAI. The live kernel is a device seat. Hitting the link is not access.

## Abstract

POCKET’s named Cloudflare tunnel (`pocket.medinatechlabs.net`) previously served live PhoneAI HTML shells to anyone who knew the URL. Stream APIs were already cookie- or LAN-gated; the kernel, Portal, and computer pages were not. This paper records the product rule that is now implemented: the public website is PhoneAI marketing + signup + Face ID pairing. Kernel, Portal, Antigravity, glasses, MCP apps, and computer stream HTML require home LAN, a signed-in seat cookie, a portal device token, or a WebAuthn session. Random visitors receive a lock page. After signup and Face ID, the same URL is the user’s phone app.

## 1. Problem

A named tunnel is a stable public hostname. If `/phoneai/app` and `/phoneai/portal` are `ALWAYS_PUBLIC`, a crawler or a forwarded link loads the full kernel UI. Even when JPEG/WebSocket frames 401, the shell leaks layout, engine names, and attack surface. The opposite mistake — locking `/` — hides the product.

Users also needed a real on-ramp: create a seat, Face ID *this* phone, then use PhoneAI as an app, not as a password prompt on every navigation.

## 2. Policy

| Class | Paths | Public internet |
|-------|--------|-----------------|
| Always public | `/`, `/phoneai`, `/signup`, `/login`, `/phoneai/pair`, health, claims, docs, auth begin/redeem | Yes |
| Live shells | `/phoneai/app`, `/os`, `/portal`, `/computer`, `/anti`, `/mcp`, glasses, TV, doorbell | LAN **or** seat / Face ID / portal cookie |
| Visual + life APIs | `/v1/phoneai/portal/*`, talk, life, MCP catalog | Same as live shells |
| Host control | shell, harness, eyes touch, WebMCP use, runtime install | Home LAN / founder only |

`path_is_public` consults `_portal_device_ok`: home LAN (no `CF-Connecting-IP`), `current_user` (Bearer / `pocket_session`), portal cookie, or passkey session.

Unauthenticated navigations to live shells return `public_gate_html` (Sign in · PhoneAI + Face ID), not JSON 401.

On the named host, `GET /` serves PhoneAI landing, not the owner map.

## 3. Pairing

LAN mint (`POST /v1/auth/device/mint`) issues a 6-digit code. Tunnel redeem requires WebAuthn. Principal is `device:<id>` with role `portal_device`. That role may view Portal; it may not shell the host (`host_control.allow` consequence `shell` fails).

## 4. After Face ID

Cookies travel on ordinary navigations, so the kernel HTML can load. MCP apps, Portal, and life APIs use the same cookie. The user bookmarks `/phoneai/app`. Sharing the public link does not share the cookie.

## 5. Evidence

Unit tests in `tests/test_host_control_policy.py` assert remote CF clients cannot `path_is_public` the live shells, LAN can, and a Bearer seat can. Live checks against the named tunnel return landing on `/` and “Sign in · PhoneAI” on `/phoneai/app`.

## 6. Related work

[PHONEAI_MCP_APPS_PAPER.md](PHONEAI_MCP_APPS_PAPER.md) · [POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md](POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md) · [whitepapers/PHONEAI_PUBLIC_TUNNEL.md](../whitepapers/PHONEAI_PUBLIC_TUNNEL.md) · [how-to/PHONEAI.md](../how-to/PHONEAI.md)
