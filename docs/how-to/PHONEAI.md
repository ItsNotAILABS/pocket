# How-to: PhoneAI (public site + kernel)

**Public site:** https://pocket.medinatechlabs.net/  
**Kernel (after seat):** `/phoneai/app`  
**Pair:** `/phoneai/pair`  
**MCP apps:** `/phoneai/mcp`

PhoneAI is the live website on the named tunnel. Hitting the link does **not** open the kernel. Sign up, then Face ID this phone. After that the app, Portal, and MCP folder work on that device.

## What is public vs locked

| URL | Anonymous internet | After signup + Face ID / LAN |
|-----|--------------------|------------------------------|
| `/` `/phoneai` | PhoneAI landing | same |
| `/signup` `/login` `/phoneai/pair` | Open | same |
| `/phoneai/app` `/phoneai/portal` `/phoneai/computer` `/phoneai/mcp` | Sign-in + Face ID gate | Kernel / Portal / MCP apps |
| Frames, talk, life, MCP invoke | 401 | Paired seat |

LAN (this PC / home Wi-Fi, no Cloudflare) can open the kernel without a tunnel cookie.

## First use on a phone

1. Open https://pocket.medinatechlabs.net/ — this is PhoneAI, not the owner desk.  
2. **Sign up** (`/signup`) — username + password or GitHub.  
3. **Face ID** (`/login` or pair flow) — WebAuthn on *this* phone.  
4. Optional: mint a 6-digit code on the PC (`POST /v1/auth/device/mint`, LAN only) and redeem on the tunnel (`/phoneai/pair`).  
5. **Enter PhoneAI** → `/phoneai/app`. Bookmark it.

## Apps on the kernel

Chat, camera, photos, maps, notes, Portal (live PC), Anti, glasses, TV/doorbell nodes, **MCP apps**, docs.

MCP servers are apps: Pocket Core, NEXUS, LOOM, GitHub, Cloudflare, filesystem. See [PHONEAI_MCP.md](PHONEAI_MCP.md).

## APIs

```http
GET  /v1/phoneai/kernel
GET  /v1/phoneai/mcp
POST /v1/phoneai/mcp/invoke   {"server":"pocket","tool":"platform_health"}
GET  /v1/auth/me
```

Host-control (shell, eyes, WebMCP *use*, install) stays founder / home LAN. A portal_device seat cannot shell the PC.

## Docs

- Product: this page · [PHONE.md](PHONE.md) (older `/phone` surface)  
- MCP: [MCP.md](MCP.md) · [PHONEAI_MCP.md](PHONEAI_MCP.md)  
- Papers: [research/PHONEAI_KERNEL_PUBLIC_SEAT_PAPER.md](../research/PHONEAI_KERNEL_PUBLIC_SEAT_PAPER.md) · [research/PHONEAI_MCP_APPS_PAPER.md](../research/PHONEAI_MCP_APPS_PAPER.md)  
- Tunnel lock: [whitepapers/PHONEAI_PUBLIC_TUNNEL.md](../whitepapers/PHONEAI_PUBLIC_TUNNEL.md)
