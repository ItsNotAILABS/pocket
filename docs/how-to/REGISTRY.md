# How-to: Full registry

**Live JSON:** `GET /v1/registry`  
**Phone app:** `/phoneai/registry`  
**Public list:** `/registry`  
**File:** [../whitepapers/POCKET_FULL_REGISTRY.json](../whitepapers/POCKET_FULL_REGISTRY.json)

One registry for **all** of:

| Lane | What |
|------|------|
| PhoneAI apps | Kernel tiles (chat, Portal, MCP, glasses, …) |
| MCP apps | Pocket, Nexus, Loom, GitHub, Cloudflare, files |
| Systems | Platform catalog (`/v1/catalog`) |
| How-tos | `docs/how-to/*` |
| Papers | `docs/research/*` |
| White papers | `docs/whitepapers/*` |
| Technologies | `TECHNOLOGY_REGISTRY.json` |

## Use

```http
GET /v1/registry
```

`counts` is the inventory. `entries[]` is the flat list (`kind`: `phoneai-app` · `mcp-app` · `system` · `how-to` · `paper` · `whitepaper` · `doc` · `technology`).

On the phone: Kernel → **Registry**. Tabs filter by kind.

## Related

[PHONEAI.md](PHONEAI.md) · [PHONEAI_MCP.md](PHONEAI_MCP.md) · [INDEX.md](../INDEX.md)
