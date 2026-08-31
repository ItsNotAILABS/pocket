# POCKET — for coding agents

Load the full toolkit:

- **Live:** `GET http://127.0.0.1:8787/v1/agents/tools`
- **Doc:** [docs/AGENTS_MCP_TOOLS.md](docs/AGENTS_MCP_TOOLS.md)
- **HTML:** `/docs/view/AGENTS_MCP_TOOLS`
- **Skill:** `agents_toolkit`
- **MCP:** `python -m pocket.mcp_server` then `mcp_catalog` / `pocket_*` tools

# POCKET — Agents · Internal MCP · Tools & Uses

**Version:** 3.6.0 · **Lab:** ItsNotAI Labs  
**Schema:** `pocket.agents_toolkit.v1`  
**Live JSON:** `GET /v1/agents/tools`  
**HTML docs:** `/docs/view/AGENTS_MCP_TOOLS`

This is the **one file agents need** for the POCKET app through our **internal MCP**.

---

## Doctrine

**Canon:** [DOCTRINE.md](DOCTRINE.md) · `GET /v1/doctrine` (30 host laws).  
**Your being:** [docs/doctrine/BEINGS.md](docs/doctrine/BEINGS.md) · `GET /v1/doctrine/beings` · `GET /v1/doctrine/{id}`.

- You are a POCKET host agent — not a generic chatbot.
- Call tools via internal MCP (server=pocket) or POST /v1/skills/run.
- Never open user browser tabs for MCP — invoke headlessly.
- Never auto-pay; never silent publish; draft mail by default.
- Prefer engine_use for the 20 named uses; model_build when you need a new specialist.
- Genetic flow evolves which internal models run for hard multi-model goals.

## How to call tools

### 1. Stdio MCP (Grok / Claude / Cursor)

```bash
PYTHONPATH=src python -m pocket.mcp_server
```

JSON-RPC: `initialize` · `tools/list` · `tools/call`

| Tool name pattern | Meaning |
|-------------------|---------|
| `pocket_<tool>` | Core host tool (e.g. `pocket_mail_inbox`) |
| `mcp_catalog` | List 10 MCP servers |
| `mcp_invoke` | `{server, tool, params}` for any server |

### 2. HTTP skills (desk / any client)

```http
POST /v1/skills/run
Content-Type: application/json

{"skill":"engine_use","prompt":"research multi-agent hosts"}
```

### 3. Named uses (recommended entry point)

```http
GET  /v1/engine-uses
POST /v1/engine-uses  {"goal":"check agent inbox"}
POST /v1/engine-uses  {"use":"browse_sense","prompt":"https://example.com"}
```

### 4. Python engines

```http
POST /v1/python-engine  {"engine":"web_research","prompt":"POCKET agents"}
POST /v1/python-engine  {"engine":"model_forge","prompt":"build math ROI model"}
```

---

## Quick start for agents

1. **mcp_catalog or GET /v1/agents/tools** — See all tools
2. **engine_uses** — 20 primary product uses
3. **engine_use with goal text** — Auto-route research/mail/browse/…
4. **model_build if specialist missing** — Register new internal model
5. **genetic_flow for multi-model goals** — Evolve which modules run
6. **mail_* for agent inboxes** — Our agents.pocket.local mail
7. **web_ui_* for websites** — Headless or signed-in Edge
8. **capsule_* for untrusted work** — Isolation + WebGPU

---

## 20 engine uses (primary product surface)

| id | Title | Tool | Engine | Improves |
|----|-------|------|--------|----------|
| `research_topic` | Research a topic | `web_ui_search` | `web_research` | Fast host search without opening a browser tab |
| `read_page` | Read a page (headless) | `web_ui_fetch` | `web_research` | Pull page text for summarization / evidence |
| `open_site` | Open a website (signed-in Edge) | `web_ui_open` | `remote_browser` | Use real cookies/profile for authenticated sites |
| `browse_sense` | Open + sense website UI | `web_ui_browse` | `web_ui` | Start a website session and see what's on screen |
| `sense_ui` | Sense open UI | `web_ui_sense` | `screen` | Fusion/OCR brief of current page or desk |
| `act_ui` | Act on website UI | `web_ui_act` | `remote_browser` | Click/type when Control or VComp is armed (never auto-pay) |
| `life_ops` | Life ops (food/flight/shop/reserve) | `python_engine` | `life_ops` | Route real-life requests; user always confirms payment |
| `assist_route` | Digital assistant route | `python_engine` | `assist` | Pick the right life/coding engine for free text |
| `agent_mail` | Agent Mail inbox/send | `python_engine` | `scribe` | Our own agents.pocket.local accounts + inboxes |
| `genetic_evolve` | Genetic flow over models | `python_engine` | `genetic` | Evolve which internal models run for a goal |
| `math_local` | Local math / ghost | `python_engine` | `ghost` | Zero-token deterministic math / hash / phi |
| `memory_world` | World-model memory | `python_engine` | `world` | Facts and memory brief from host world model |
| `local_llm` | Local LMR (Auro) | `python_engine` | `auro` | On-host meaning model without cloud round-trip |
| `mcp_tool` | Invoke MCP tool | `python_engine` | `mcp` | Any pocket MCP tool headlessly |
| `integration` | Run integration | `python_engine` | `integrations` | Open/execute catalog integrations (Discord, etc.) |
| `loom_loop` | LOOMGRAPH loop | `python_engine` | `loomgraph` | See the graph · run the multi-step loop |
| `coding_swarm` | Coding swarm | `python_engine` | `coding_swarm` | Multi-agent code + pixel artifacts |
| `build_model` | Build a platform model | `python_engine` | `model_forge` | Create a new internal model and register it when missing |
| `use_built_model` | Express a built model | `python_engine` | `express_model` | Run a forged/registered model by id |
| `vcomp_shell` | Virtual computer shell | `python_engine` | `vcomp` | Isolated shell on host virtual computer |

### Examples

```json
{"skill":"engine_use","prompt":"research multi-agent edge hosts"}
{"skill":"engine_use","params":{"use":"agent_mail"},"prompt":"inbox"}
{"skill":"engine_use","params":{"use":"build_model"},"prompt":"ROI formula helper"}
{"skill":"engine_use","params":{"use":"genetic_evolve"},"prompt":"hash plan and next steps"}
```

---

## Internal MCP servers (3) + external (7)

| Server | Kind | Blurb |
|--------|------|-------|
| `pocket` | internal | Coherent host: habitat · screen · work · fusion voice · phone pair · drafts · CLI |
| `nexus` | internal | Nine workers · MCP federation · intelligence tools |
| `loom` | internal | Agents dispatch · vault · runspace · knowledge · plans |
| `github` | external | Repos · PRs · issues · via gh CLI (signed-in host) |
| `cloudflare-docs` | external | Workers · Pages · platform docs for agents |
| `cloudflare` | external | Account / product MCP surface |
| `cloudflare-bindings` | external | KV · D1 · R2 · bindings for Workers |
| `cloudflare-builds` | external | CI / Pages builds |
| `cloudflare-observability` | external | Logs · metrics for agents |
| `filesystem` | external | Read/write under allowed workspaces only — agent CLI style |

**POCKET core tools:** 110

### Pocket tools by group

#### platform

`platform_map`, `platform_health`, `find_feature`, `sovereign_stack`, `computing_clouds`, `list_skills`, `tools_for_prompt`

#### screen_habitat

`remote_browser_status`, `remote_browser_open`, `remote_browser_sense`, `remote_browser_benchmark`, `iot_status`, `iot_list`, `iot_register`, `iot_phone`, `iot_hz_status`, `habitat_status`, `habitat_pulse`, `habitat_assign`, `screen_status`, `screen_set`, `screen_sense`, `screen_act`, `vcomp_open`, `vcomp_sense`, `vcomp_act`, `vcomp_shell`

#### work_voice_phone

`work_start`, `work_tick`, `work_package`, `work_handoff`, `work_status`, `fusion_voice`, `fusion_schema`, `aria_turn`, `phone_surface`, `pair_mint`, `pair_status`

#### life_web

`life_catalog`, `life_status`, `life_classify`, `food_order`, `flight_search`, `shop_search`, `web_browse`, `reservation`, `web_search`, `web_fetch`, `assist_route`, `web_ui_open`, `web_ui_sense`, `web_ui_act`, `web_ui_fetch`, `web_ui_search`, `web_ui_browse`, `web_ui_status`

#### integrations_loom

`integrations_list`, `integrations_execute`, `integrations_readiness`, `loomgraph_run`, `loomgraph_catalog`, `loomgraph_status`

#### capsules_studio

`capsule_status`, `capsule_list`, `capsule_allocate`, `capsule_execute`, `capsule_commit`, `capsule_terminate`, `webgpu_probe`, `studio_map`, `studio_status`, `studio_open`, `studio_playbooks`, `studio_storyboard`, `studio_caption`, `studio_list_recordings`, `studio_list_exports`, `studio_presets`, `studio_record_start`, `studio_record_stop`, `studio_render`, `studio_viral`, `studio_batch`, `studio_ship`, `imagine_compose`

#### mail

`mail_status`, `mail_accounts`, `mail_account_create`, `mail_inbox`, `mail_send`, `mail_read`, `mail_draft`

#### web_ui_engines

`python_engine`, `python_engines_list`, `engine_uses`, `engine_use`, `model_build`, `model_list_built`, `model_register`, `model_suggest`

#### other

`draft_create`, `draft_promote`, `cli_run`, `cli_list`, `wsl_status`, `auro_status`, `muse_status`, `agents_toolkit`, `agents_tools`, `tools_manifest`

### Full pocket tool list

```
platform_map
platform_health
find_feature
sovereign_stack
computing_clouds
remote_browser_status
remote_browser_open
remote_browser_sense
remote_browser_benchmark
iot_status
iot_list
iot_register
iot_phone
iot_hz_status
habitat_status
habitat_pulse
habitat_assign
screen_status
screen_set
screen_sense
screen_act
vcomp_open
vcomp_sense
vcomp_act
vcomp_shell
work_start
work_tick
work_package
work_handoff
work_status
fusion_voice
fusion_schema
aria_turn
phone_surface
pair_mint
pair_status
draft_create
draft_promote
cli_run
cli_list
life_catalog
life_status
life_classify
food_order
flight_search
shop_search
web_browse
reservation
web_search
web_fetch
integrations_list
integrations_execute
integrations_readiness
loomgraph_run
loomgraph_catalog
loomgraph_status
assist_route
list_skills
wsl_status
auro_status
muse_status
tools_for_prompt
capsule_status
capsule_list
capsule_allocate
capsule_execute
capsule_commit
capsule_terminate
webgpu_probe
studio_map
studio_status
studio_open
studio_playbooks
studio_storyboard
studio_caption
studio_list_recordings
studio_list_exports
studio_presets
studio_record_start
studio_record_stop
studio_render
studio_viral
studio_batch
studio_ship
imagine_compose
mail_status
mail_accounts
mail_account_create
mail_inbox
mail_send
mail_read
mail_draft
web_ui_open
web_ui_sense
web_ui_act
web_ui_fetch
web_ui_search
web_ui_browse
web_ui_status
python_engine
python_engines_list
engine_uses
engine_use
model_build
model_list_built
model_register
model_suggest
agents_toolkit
agents_tools
tools_manifest
```

---

## Platform skills (129)

Same modules as MCP — call via `POST /v1/skills/run`.

| Skill | Worker | Description |
|-------|--------|-------------|
| `agents_toolkit` | ARCHON | Full agent toolkit: internal MCP tools, 20 uses, skills, engines, model forge |
| `aria_turn` | ARCHON | Local Aria skill try + fusion hint (no mic) |
| `assist_route` | ARCHON | Route a request to the right digital-assistant engine |
| `auro_status` | ARCHON | Local Auro meaning model status |
| `capsule_allocate` | ARCHON | Allocate isolated capsule (tier 256/512/1024MB, optional WebGPU) |
| `capsule_commit` | ARCHON | Commit capsule OverlayFS → ChangeSet merge |
| `capsule_execute` | ARCHON | Execute command inside a capsule (HostWorker / WASI) |
| `capsule_list` | ARCHON | List live multi-sandbox capsules |
| `capsule_status` | ARCHON | Multi-sandbox capsule protocol status (PROTO-CAPSULE-WASM-009) |
| `capsule_terminate` | ARCHON | Terminate capsule and release memory reservation |
| `cli_list` | ARCHON | CLI inventory for agents |
| `cli_run` | ARCHON | Run allowlisted CLI (params.bin + args) |
| `computing_clouds` | ARCHON | Inventory OUR computing clouds (host, tunnel, deploys, Auro, NEXUS, HZ) |
| `economy_map` | ARCHON | Economic domain: wallets, twin wallets, escrow, clearing, Parallax bridge |
| `economy_twins` | ARCHON | List digital twin wallets for agents |
| `engine_use` | ARCHON | Run one named use id (or auto-pick from prompt) |
| `engine_uses` | ARCHON | 20 named uses for web_ui + python_engine (research, browse, mail, forge…) |
| `express_model` | ARCHON | Express one internal model module on a goal (no full genetic loop) |
| `find_feature` | ARCHON | Find where a feature lives (desk tab, phone, API, skill) |
| `flight_search` | NAVIGATOR | Flight search (Google Flights) — you book & pay |
| `food_order` | NAVIGATOR | Food delivery options in Edge — you pay (never auto-checkout) |
| `fusion_last` | ARCHON | Last fusion result for session_id |
| `fusion_schema` | ARCHON | Conversational Fusion schema + experts |
| `fusion_voice` | ARCHON | Conversational Fusion: route expert/patience/preload (DFW) |
| `genetic_flow` | ARCHON | Run genetic flow — evolve which internal model modules execute for a goal |
| `genetic_status` | ARCHON | Recent genetic flow runs + module readiness |
| `habitat_assign` | ARCHON | Assign task to habitat resident |
| `habit

_(truncated in AGENTS.md — full file at docs/AGENTS_MCP_TOOLS.md)_
