# White paper — PhoneAI on the public tunnel

**Status:** Implemented on the founder host  
**Host:** https://pocket.medinatechlabs.net/  
**Code:** `pocket.auth.PHONEAI_LIVE_SHELLS`, `_portal_device_ok`, `public_gate_html`

## Claim

The live website is PhoneAI. Signup + Face ID unlocks the app on that phone. The raw link is not the kernel.

## Mechanics

1. Named tunnel terminates TLS at Cloudflare and forwards to `:8787`.  
2. `CF-Connecting-IP` marks the client as internet, not home LAN.  
3. Landing (`/` on that Host) is PhoneAI marketing.  
4. Live shells require LAN **or** seat cookie **or** passkey **or** portal device.  
5. Gate HTML brands PhoneAI and, after success, opens `/phoneai/app`.

## What a stranger sees

- `/` — PhoneAI site  
- `/phoneai/app` — Sign in · PhoneAI (Face ID button)  
- Frames / talk — 401 JSON  

## What a paired user sees

Kernel, Portal, computer, MCP apps, life APIs — same origin, cookie sent.

## References

[research/PHONEAI_KERNEL_PUBLIC_SEAT_PAPER.md](../research/PHONEAI_KERNEL_PUBLIC_SEAT_PAPER.md) · [how-to/PHONEAI.md](../how-to/PHONEAI.md) · [SECURITY.md](../SECURITY.md)
