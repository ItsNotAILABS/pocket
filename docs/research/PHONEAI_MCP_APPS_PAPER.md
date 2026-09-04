# MCP Apps Inside PhoneAI: Embedded Servers as a Phone Folder

**Paper ID:** INL-2026-PHONEAI.MCP.001  
**Date:** 4 September 2026  
**Lab:** ItsNotAI Labs (Dallas)  
**Thesis:** MCP is not a tab the user opens. On PhoneAI, each MCP server is an app. Invoke on the phone is a safe subset; the owner desk keeps full tools.

## Abstract

POCKET embeds ten MCP servers (three internal: Pocket Core, NEXUS, LOOM; seven external including GitHub, Cloudflare family, and a workspace filesystem). Agents already call them headlessly via stdio and `mcp_invoke`. This paper describes the **human** surface: those servers appear as apps inside the PhoneAI kernel (`/phoneai/app` MCP tile and `/phoneai/mcp`). Catalog is available to a paired seat. Phone invoke is restricted to read/status/list/map/health tools. Shell, click, WebMCP *use*, writes, and install stay off the phone.

## 1. Why apps, not a protocol screen

MCP JSON-RPC is for models. A phone kernel that dumps `tools/list` is a developer console, not a product. Users understand folders of apps. Mapping `server.id → app icon` makes Pocket, Nexus, GitHub, and Cloudflare first-class PhoneAI software without teaching JSON-RPC.

The same catalog powers agents (`GET /v1/mcp`, `mcp_catalog`). PhoneAI is a view, not a second registry.

## 2. Surfaces

| Surface | Role |
|---------|------|
| `/phoneai/app#mcp` | In-kernel folder |
| `/phoneai/mcp` | Full-screen MCP home |
| `GET /v1/phoneai/mcp` | App list + safe tool names |
| `POST /v1/phoneai/mcp/invoke` | Allow-listed tools only |
| `python -m pocket.mcp_server` | Full stdio for Grok / Claude / Cursor |

## 3. Safety

`phoneai_mcp.tool_is_safe` allows exact names (`platform_health`, `fs_list`, `mail_inbox`, …) and suffixes (`_status`, `_list`, `_catalog`, `_map`, `_health`). Tokens such as `shell`, `touch`, `act`, `write`, `use`, `install`, `send` are denied. Denied invokes return a structured error; they do not fall through to `mcp_bundle.invoke`.

Portal-device seats therefore cannot drive the desktop from an MCP app icon. Founder LAN / owner password still uses `/v1/mcp/invoke`.

## 4. Relation to WebMCP

WebMCP diffuses *page* actions. MCP apps are *servers*. PhoneAI keeps both: Web live (`/phoneai/web`) vs MCP folder (`/phoneai/mcp`). `webmcp_list` / `webmcp_find` are phone-safe; `webmcp_use` is not.

## 5. Related

[how-to/PHONEAI_MCP.md](../how-to/PHONEAI_MCP.md) · [AGENTS_MCP_TOOLS.md](../AGENTS_MCP_TOOLS.md) · [whitepapers/PHONEAI_MCP_APPS.md](../whitepapers/PHONEAI_MCP_APPS.md) · [POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md](POCKET_PHONEAI_NETWORK_WEBMCP_PAPER.md)
