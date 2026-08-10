# How-to: MCP for models (Grok / Claude / Cursor)

POCKET exposes a **stdio MCP server** so external AIs call host tools headlessly.

## Start

```powershell
$env:PYTHONPATH = "C:\Users\Medin\OneDrive\pocket-os\src"
python -m pocket.mcp_server
```

JSON-RPC on stdin/stdout: `initialize` · `tools/list` · `tools/call`.

## Config sketch (Grok / similar)

```toml
[mcp_servers.pocket]
command = "python"
args = ["-m", "pocket.mcp_server"]
# ensure PYTHONPATH includes pocket-os/src
```

## Important tools

| Tool | Use |
|------|-----|
| `mcp_catalog` | All 10 MCP servers |
| `mcp_invoke` | Any server.tool |
| `pocket_mail_inbox` | Agent inbox |
| `pocket_mail_send` | Agent mail |
| `pocket_web_ui_browse` | Website UI |
| `pocket_python_engine` | Named Python engine |
| `pocket_platform_map` | Full platform map |
| `pocket_genetic_flow` | Genetic run (via skills path) |

Many tools are listed as `pocket_<name>` from the pocket server catalog.

## HTTP alternative (no stdio)

```http
POST /v1/skills/run
{"skill":"mail_inbox","params":{"agent":"assist"}}
```

```python
from pocket.mcp_bundle import invoke, catalog
catalog()
invoke("pocket", "python_engines_list")
invoke("pocket", "mail_accounts")
```

## Doctrine

Agents invoke tools **headlessly**. Users do **not** open browser tabs for MCP. Website work uses `web_ui_*` on the host Edge/Fusion path.
