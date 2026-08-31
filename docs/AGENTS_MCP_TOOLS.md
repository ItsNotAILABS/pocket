# POCKET — Agents · Internal MCP · Tools & Uses

**Version:** 3.6.0 · **Lab:** ItsNotAI Labs  
**Schema:** `pocket.agents_toolkit.v1`  
**Live JSON:** `GET /v1/agents/tools`  
**HTML docs:** `/docs/view/AGENTS_MCP_TOOLS`

This is the **one file agents need** for the POCKET app through our **internal MCP**.

---

## Doctrine

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
| `mcp_stream` | Live MCP JSON-RPC protocol stream (poll frames) |
| `universal_*` | **60 universal tools** — any agent, no `pocket_` prefix |
| pack tools | Full **200-tool** pack (60 universal + 140 ecosystem) |

**200-tool pack:** `GET /v1/mcp/fifty` · `mcp_invoke {server:"universal", tool:"universal_ping"}`

**100 multi workflows:** `GET /v1/workflows/multi` · `POST /v1/workflows/multi/run {"id":"mw001_stack_health"}` · skill `multi_workflows`

**Power (the missing command plane):** `GET /power` · `POST /v1/power/do {"goal":"morning seatbelt"}` · `GET /v1/power/vs` · skills `power_do` `power_pulse` `power_vs`

**GO (live active states + working workflows):** `POST /v1/go` arms daily+triple · `GET /v1/go` is the board of every surface + all 100 workflow slots · Power runs write into GO · skills `go` `go_state` `go_tick`

### Live MCP JSON-RPC Protocol Stream

Every `invoke` and stdio JSON-RPC frame is mirrored mid-wire:

```http
GET  /v1/mcp/stream?after=<seq>
GET  /v1/mcp/stream/page
POST /v1/mcp/stream/clear
```

Skill: `mcp_stream` · Tool: `pocket_mcp_stream` / `mcp_stream`

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
| `habitat_open` | ARCHON | Mark habitat open for desk session |
| `habitat_pulse` | ARCHON | Pulse a resident status/line |
| `habitat_status` | ARCHON | Habitat residents, rooms, activity |
| `imagine_compose` | STUDIO | Compose device still (rotato phone / macbook web) |
| `integrations_execute` | ARCHON | Execute any integration for real (Discord desktop, Edge SaaS, board) |
| `integrations_list` | ARCHON | 54 life integrations catalog (Discord, OpenTable, DoorDash…) |
| `integrations_readiness` | ARCHON | Per-integration executable readiness (desktop installed? url? board?) |
| `internal_models` | ARCHON | List internal models as modules (ghost, world, auro, guppy, heuristic, identity) |
| `iot_hz_status` | ARCHON | HZ offline mesh status for phone BLE / home adjacency |
| `iot_list` | ARCHON | List home IoT devices |
| `iot_phone` | ARCHON | Phone LAN/remote/pair bridge for home |
| `iot_register` | ARCHON | Register a home IoT device (name, kind, room, address) |
| `iot_status` | ARCHON | Home IoT + phone bridge status |
| `lab_status` | ARCHON | Lab readiness: host · studio · capsules · life · phone |
| `life_catalog` | ARCHON | Catalog of everyday life skills (food, flights, shop, web, reserve) |
| `life_classify` | ARCHON | Classify text into food/flight/shop/browse/reservation |
| `life_status` | ARCHON | Working board + life ops status |
| `list_agents` | ARCHON | First-class desk + phone agents |
| `list_skills` | ARCHON | Full skill suite for agents (platform + life + host) |
| `loomgraph_catalog` | ARCHON | LOOMGRAPH playbook graphs catalog + mermaid |
| `loomgraph_mermaid` | ARCHON | LOOMGRAPH mermaid diagram for a playbook graph |
| `loomgraph_run` | ARCHON | LOOMGRAPH — run loop-orchestrated multi-agent graph (default harness) |
| `loomgraph_status` | ARCHON | LOOMGRAPH live runs + recent receipts |
| `mail_account_create` | SCRIBE | Create our own email account for an agent |
| `mail_accounts` | SCRIBE | List our agent email accounts (@agents.pocket.local) |
| `mail_draft` | SCRIBE | Official POCKET MAIL draft (SMTP path) |
| `mail_inbox` | SCRIBE | Read an agent inbox |
| `mail_read` | SCRIBE | Open one agent mail message |
| `mail_send` | SCRIBE | Send agent↔agent or external mail |
| `mail_status` | SCRIBE | Agent mail + POCKET MAIL status (accounts, inboxes, SMTP) |
| `mcp_catalog` | ARCHON | 10 embedded MCPs catalog |
| `mcp_invoke` | ARCHON | Invoke MCP server.tool (params.server + params.tool) |
| `model_build` | ARCHON | Build a new internal model and register it on the platform |
| `model_list_built` | ARCHON | List agent-built models on this host |
| `model_register` | ARCHON | Register built models into genetic/express registry |
| `model_suggest` | ARCHON | Suggest a model blueprint from a free-text goal |
| `muse_status` | ARCHON | Muse Spark multimodal assist surface |
| `pair_mint` | ARCHON | Mint desk pair code for phone |
| `pair_status` | ARCHON | Node identity + peers + open codes |
| `phone_surface` | ARCHON | Phone surface URLs + pair instructions |
| `platform_health` | ARCHON | Domain health for habitat/screen/work/fusion/mcp/agents |
| `platform_map` | ARCHON | Full coherent platform map (surfaces, flow, findability) |
| `pocket_identity` | ARCHON | Who we are: POCKET host agents — help users with POCKET |
| `protocols_map` | ARCHON | Ten major POCKET protocols catalog (mesh, MCP, auth, jobs, phone, voice…) |
| `protocols_status` | ARCHON | Health of all 10 major protocols |
| `python_engine` | ARCHON | Run a named Python agent/engine (browser, mail, genetic, auro…) |
| `python_engines_list` | ARCHON | List Python agents/engines models can invoke |
| `rah_plan` | ARCHON | Plan RAH leaf fan-out without executing (preview independence) |
| `rah_run` | ARCHON | Recursive Agent Harnesses — fan out full sub-harnesses in parallel (expensive) |
| `rah_status` | ARCHON | RAH live/recent runs and defaults |
| `remote_browser_benchmark` | ARCHON | Run suite: our remote browser must pass every axis |
| `remote_browser_open` | NAVIGATOR | Open URL in signed-in Edge (our remote browser) |
| `remote_browser_sense` | OCULUS | Fusion sense pack for remote browser |
| `remote_browser_status` | NAVIGATOR | Our remote browser status vs theirs |
| `reservation` | NAVIGATOR | Restaurant reservation drive (OpenTable) — you confirm |
| `screen_control` | OCULUS | Enable Control mode (agents may drive mouse/keyboard) |
| `screen_off` | OCULUS | Turn screen share off |
| `screen_sense` | OCULUS | Fusion context brief from shared screen |
| `screen_status` | OCULUS | Screen share mode status |
| `screen_view` | OCULUS | Enable View mode (agents see fusion screen) |
| `shop_search` | NAVIGATOR | Shopping search (Amazon etc.) — you checkout |
| `sovereign_stack` | ARCHON | Doctrine: our remote browser, remote, phone IoT, our clouds |
| `studio_auto` | STUDIO | Alias studio_viral — polish latest recording |
| `studio_batch` | STUDIO | Multi-preset batch render |
| `studio_caption` | STUDIO | Launch blurb + social posts for demo exports |
| `studio_full_loop` | STUDIO | One intent: record and ship / stop and ship full demo loop |
| `studio_list_exports` | STUDIO | List polished studio exports |
| `studio_list_recordings` | STUDIO | List host recordings in ~/.pocket/recordings |
| `studio_map` | STUDIO | First-class Product Studio map for agents (features + playbooks) |
| `studio_open` | STUDIO | Studio URLs for desk / phone / LAN |
| `studio_playbooks` | STUDIO | Agent playbooks: viral ship, record+polish, storyboard, caption |
| `studio_presets` | STUDIO | Viral presets (rotato_phone, x_screencast, macbook_web…) |
| `studio_record_start` | SPECULUM | Start full-desktop record for studio polish |
| `studio_record_stop` | SPECULUM | Stop record and save mp4 |
| `studio_render` | STUDIO | Render one preset from recording |
| `studio_ship` | STUDIO | End-to-end ship: viral pack + caption + next steps |
| `studio_status` | STUDIO | Studio health: ffmpeg, recordings, exports, surfaces |
| `studio_storyboard` | STUDIO | Plan hook→proof→CTA demo beats agents can execute |
| `studio_viral` | STUDIO | Viral pack: phone remake + web + screencast |
| `tools_for_prompt` | ARCHON | Plan which host tools match a natural-language prompt |
| `vcomp_open` | ARCHON | Open virtual computer workspace |
| `viral_pack` | STUDIO | Alias studio_viral |
| `voice_skills_list` | ARCHON | Aria everyday skills (time, lists, travel…) |
| `voice_status` | ARCHON | Aria voice product status · skills · API |
| `voice_studio_open` | ARCHON | Voice Studio URL + map paper → product (canvas, snap, fusion) |
| `voice_turn` | ARCHON | Run one Aria product turn (skills + host actions + speak) |
| `web_browse` | NAVIGATOR | Open/search web in Edge + light page sense |
| `web_fetch` | SCRUTATOR | Fetch a URL and return cleaned text |
| `web_search` | SCRUTATOR | Host web search (DDG/Brave multi-backend) without leaving POCKET |
| `web_ui_act` | NAVIGATOR | Act on website interface (click/type when armed) |
| `web_ui_browse` | NAVIGATOR | Open website + sense (MCP website interface session) |
| `web_ui_fetch` | SCRUTATOR | Fetch URL text headlessly |
| `web_ui_open` | NAVIGATOR | Open website in host browser (Python engine) |
| `web_ui_search` | SCRUTATOR | Host web search for models |
| `web_ui_sense` | NAVIGATOR | Sense open website UI for agents |
| `web_ui_status` | NAVIGATOR | Website UI engine + Python engines catalog |
| `webgpu_probe` | ARCHON | Host WebGPU/GPU adapter probe + acceleration doctrine |
| `work_handoff` | ARCHON | Handoff package → artifacts |
| `work_package` | ARCHON | Package working conversation |
| `work_start` | ARCHON | Start Working mode session |
| `work_status` | ARCHON | Live Working sessions |
| `wsl_status` | ARCHON | WSL / Linux distro status for integrated console |

---

## Python engines (25)

| Engine | For |
|--------|-----|
| `browser` | Edge · X · Copilot · lookups |
| `remote_browser` | Open · sense · act · benchmark |
| `web_research` | search_web · fetch_url |
| `life_ops` | food · flights · shop · reserve |
| `navigator` | alias of life web actions |
| `assist` | route digital life intents |
| `scribe` | agent email · inbox · send |
| `mail` | official SMTP mail |
| `genetic` | internal models genetic flow |
| `ghost` | pure math / hash |
| `guppy` | desk actuator fish |
| `world` | memory / facts |
| `auro` | local LMR |
| `mcp` | invoke any MCP tool |
| `integrations` | execute integrations |
| `loomgraph` | graph loop harness |
| `keep` | KEEP background agents |
| `coding_swarm` | multi-agent code |
| `screen` | Fusion sense · control |
| `vcomp` | virtual computer shell |
| `model_forge` | build + register platform models |
| `express_model` | express any registered model id |
| `engine_uses` | list/run the 20 named uses |
| `user-math-helper` | built formula: Auto-suggested for: math formula helper for percentages |
| `user-roi` | built formula: ROI |

---

## Model Forge — build models when needed

**Kinds:** `template`, `heuristic`, `formula`, `wrap`, `code`, `auro`  
**Built on host:** 2

```http
POST /v1/models/suggest  {"goal":"calculate ROI with phi"}
POST /v1/models/build
{
  "model_id": "user-roi",
  "kind": "formula",
  "formula": "x * phi",
  "fit_keywords": ["roi", "phi"],
  "register_now": true
}
POST /v1/internal-models/express  {"model":"user-roi","goal":"100"}
POST /v1/genetic/run  {"goal":"compute ROI with phi","generations":2}
```

Skills: `model_suggest` · `model_build` · `model_list_built` · `model_register` · `express_model` · `genetic_flow`

---

## Agent Mail

| Action | Call |
|--------|------|
| Status | `mail_status` / GET `/v1/agent-mail` |
| Accounts | `mail_accounts` |
| Create | `mail_account_create` |
| Inbox | `mail_inbox` params.agent |
| Send | `mail_send` from/to/subject/body |
| Read | `mail_read` |
| UI | `/mail` |

Domain: **agents.pocket.local**

---

## Genetic flow · internal models

| Action | Call |
|--------|------|
| List modules | `internal_models` / GET `/v1/internal-models` |
| Express one | `express_model` params.model |
| Genetic run | `genetic_flow` / POST `/v1/genetic/run` |
| Desk mode | `mode=genetic` |

Built-in modules: ghost · world · auro · guppy · heuristic · identity (+ forged user-*)

---

## Capsules (untrusted work)

`capsule_status` · `capsule_allocate` · `capsule_execute` · `capsule_commit` · `capsule_terminate` · `webgpu_probe`

20 reasons: skill `capsule_reasons` (untrusted_eval, sandbox_tests, …).

---

## Surfaces

| Surface | Path |
|---------|------|
| desk | `/desk` |
| phone | `/phone` |
| mail | `/mail` |
| docs | `/docs` |
| install | `/install` |
| work | `/work` |
| loomgraph | `/loomgraph` |
| catalog | `/v1/catalog` |
| agents_tools | `/v1/agents/tools` |

---

## Safety

- Never auto-pay (food, shop, flights, reservations — user confirms)
- Never silent SMTP send without explicit intent
- Act on UI only when Control/VComp armed
- Code models forbid import/open/exec
- Capsules for untrusted eval (20 capsule reasons)
- Market seats never see founder disk

---

## Recipe cheat sheet

```text
Orient          → platform_map | pocket_identity | protocols_map
Research        → engine_use research_topic | web_ui_search | web_search
Read URL        → engine_use read_page | web_ui_fetch
Open site       → engine_use open_site | web_ui_browse
Sense screen    → screen_sense | web_ui_sense
Life ops        → life_catalog | food_order | flight_search | shop_search
Mail            → mail_inbox | mail_send
Need specialist → model_suggest → model_build → express_model
Hard multi-model→ genetic_flow
Untrusted code  → capsule_allocate → capsule_execute
Ship demo       → studio_ship | studio_viral
Graph loop      → loomgraph_run
Parallel big    → rah_run (expensive)
```

---

_Generated live by `pocket.agents_toolkit` · 3.6.0_
