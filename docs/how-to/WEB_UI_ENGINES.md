# How-to: Website UI + Python engines

Models and agents drive **real website interfaces** through **Python** — not by opening MCP browser tabs for the user.

## Tools

| Tool / API | What it does |
|------------|----------------|
| `web_ui_open` | Open URL in signed-in Edge |
| `web_ui_sense` | Fusion sense of current UI |
| `web_ui_act` | Click/type when Control/VComp armed |
| `web_ui_browse` | Open + sense session |
| `web_ui_fetch` | Headless page text |
| `web_ui_search` | Host web search |
| `python_engine` | Run any named engine |
| `python_engines_list` | Catalog (~20 engines) |

## Engines models can call

browser · remote_browser · web_research · life_ops · assist · scribe · mail · genetic · ghost · guppy · world · auro · mcp · integrations · loomgraph · keep · coding_swarm · screen · vcomp

## Recipes

### Open and sense a site

```http
POST /v1/web-ui/browse
{"url":"https://example.com"}
```

### Search without a browser tab

```http
POST /v1/web-ui/search
{"query":"POCKET agent OS"}
```

### Run a named engine

```http
POST /v1/python-engine
{"engine":"browser","prompt":"lookup multi-agent platforms"}
```

```http
POST /v1/python-engine
{"engine":"scribe","prompt":"inbox","params":{"agent":"assist"}}
```

### Skill / MCP

```json
{"skill":"web_ui_browse","prompt":"https://news.ycombinator.com"}
{"skill":"python_engine","params":{"engine":"web_research","prompt":"edge AI hosts"}}
```

```python
from pocket.mcp_bundle import invoke
invoke("pocket", "web_ui_open", url="https://example.com")
invoke("pocket", "python_engine", engine="ghost", prompt="phi 3")
```

## Safety

- Never auto-pay · never silent publish  
- Prefer fetch/search for read-only research  
- Act requires Control arming on desk  

## Code

`pocket.web_ui_engine` · wired in `mcp_bundle`, `platform_coherence`, `server`
