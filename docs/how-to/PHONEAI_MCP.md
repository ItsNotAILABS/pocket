# How-to: MCP apps inside PhoneAI

Surface: **`/phoneai/mcp`** (also the **MCP** tile on `/phoneai/app`)

Each embedded MCP server is a **phone app**. You do not open a Cloudflare / GitHub MCP tab. The PhoneAI seat lists servers, then runs **phone-safe** tools on the host.

## Open

1. Sign up + Face ID (or home LAN).  
2. Kernel → **MCP** / **MCP apps**.  
3. Tap a server (Pocket, Nexus, Loom, GitHub, Cloudflare, Files).  
4. Tap **Open** on a safe tool (status, catalog, list, health, map).

## APIs

```http
GET  /v1/phoneai/mcp
POST /v1/phoneai/mcp/invoke
{"server":"pocket","tool":"platform_health"}
```

Unsafe tools (`shell`, `touch`, `webmcp_use`, `fs_write`, `runtime_install`, …) return:

```json
{"ok": false, "error": "this tool is not a PhoneAI MCP app action — owner desk only"}
```

Owner desk / stdio MCP still has the full catalog: `python -m pocket.mcp_server`.

## Doctrine

- Agents invoke MCP **headlessly**.  
- Humans on PhoneAI get **apps**, not raw JSON-RPC.  
- Public tunnel visitors without a seat never load `/phoneai/mcp`.

## Related

[MCP.md](MCP.md) · [AGENTS_MCP_TOOLS.md](../AGENTS_MCP_TOOLS.md) · [PHONEAI.md](PHONEAI.md) · paper [PHONEAI_MCP_APPS_PAPER.md](../research/PHONEAI_MCP_APPS_PAPER.md)
