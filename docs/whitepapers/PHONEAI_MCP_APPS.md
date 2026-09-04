# White paper — MCP apps inside PhoneAI

**Status:** Implemented  
**Surfaces:** `/phoneai/mcp` · kernel tile **MCP**  
**Code:** `pocket.phoneai_mcp`

## Claim

Embedded MCP servers are PhoneAI apps. The phone runs a safe subset. Agents keep the full colony.

## Folder

Pocket Core · NEXUS · LOOM · GitHub · Cloudflare Docs / Bindings / Builds / Observability · Filesystem.

## Invoke rule

Phone `POST /v1/phoneai/mcp/invoke` → `safe_invoke`. Status/list/catalog/map/health only. No shell, no screen act, no WebMCP use.

## References

[research/PHONEAI_MCP_APPS_PAPER.md](../research/PHONEAI_MCP_APPS_PAPER.md) · [how-to/PHONEAI_MCP.md](../how-to/PHONEAI_MCP.md) · [how-to/MCP.md](../how-to/MCP.md)
