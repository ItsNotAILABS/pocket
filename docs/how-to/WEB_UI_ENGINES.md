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

## 20 named uses

```http
GET  /v1/engine-uses
POST /v1/engine-uses  {"goal":"research multi-agent hosts"}   # auto-pick
POST /v1/engine-uses  {"use":"browse_sense","prompt":"https://example.com"}
POST /v1/engine-uses  {"use":"build_model","prompt":"ROI formula helper"}
```

| id | Tool / engine |
|----|----------------|
| research_topic | web_ui_search |
| read_page | web_ui_fetch |
| open_site | web_ui_open |
| browse_sense | web_ui_browse |
| sense_ui / act_ui | sense / act |
| life_ops · assist_route | life / assist engines |
| agent_mail | scribe |
| genetic_evolve · math_local · memory_world · local_llm | genetic / ghost / world / auro |
| mcp_tool · integration · loom_loop · coding_swarm | host engines |
| **build_model** | **model_forge** — create platform model |
| **use_built_model** | express_model by id |
| vcomp_shell | virtual computer |

Skill: `engine_uses` · `engine_use`

## Build models when needed

Agents create specialists and register them for genetic / express:

```http
POST /v1/models/suggest  {"goal":"calculate ROI with phi scaling"}
POST /v1/models/build
{
  "model_id": "user-roi",
  "name": "ROI helper",
  "kind": "formula",
  "formula": "x * phi",
  "fit_keywords": ["roi", "phi", "return"],
  "register_now": true
}
POST /v1/internal-models/express  {"model":"user-roi","goal":"100"}
POST /v1/genetic/run  {"goal":"compute ROI with phi", "generations":2}
```

Kinds: `template` · `heuristic` · `formula` · `wrap` · `code` · `auro`

```json
{"skill":"model_build","params":{"kind":"wrap","name":"web-spec","wrap_engine":"web_research"}}
{"skill":"python_engine","params":{"engine":"model_forge"},"prompt":"build a math formula model for ROI"}
```

Storage: `~/.pocket/user_models/` · auto-loaded on host boot into internal model registry.

## Safety

- Never auto-pay · never silent publish  
- Prefer fetch/search for read-only research  
- Act requires Control arming on desk  
- Code models block import/open/exec  

## Code

`pocket.web_ui_engine` · `pocket.model_forge` · wired in MCP / skills / server
