# POCKET platform surface (coherent)

One host co-pilot — **not** separate pieces. Everything from desk, phone, voice Fusion, Habitat, Screen, Working, MCP/CLI, and skills shares the same map.

## Product flow

1. **Habitat** — agents live/work (GUI floor; open by default)  
2. **Chat** — one seated agent  
3. **Screen** — View / Control + VComputer (all agents)  
4. **Workspace** — files, helpers, **Get pair code**  
5. **Phone** — `/phone` · Aria/Working first-class · redeem pair  
6. **Working** — voice + screen + package → handoff  
7. **Conversational Fusion** — voice metadata → DFW expert/patience (POCKET host)  
8. **MCP / CLI / skills** — agents only (no user tabs for tools)  

## Discover (agents + humans)

| Entry | Purpose |
|-------|---------|
| `GET /v1/platform/coherent` | **One map**: surfaces, skills, flow, find, health |
| `GET /v1/api` | Full route catalog (`platform_api`) |
| `GET /v1/skills` | Full suite + `platform_skills` |
| `GET /v1/skills/platform` | Platform skills only |
| `POST /v1/skills/run` | `{ "skill": "platform_map" }` etc. |
| `POST /v1/mcp/invoke` | `{ "server": "pocket", "tool": "platform_map" }` |
| Desk tabs | Desk · Habitat · Screen · OS · Work · Studio · API · Phone · Browser (in-app) |
| Phone | Aria · Working · pair · mic |
| Voice Studio | `/studio/voice` · canvas · persona · code snap |

## Platform skills (agents)

| Skill | Does |
|-------|------|
| `platform_map` | Full coherent map |
| `platform_health` | Domain health |
| `find_feature` | Locate tab/API/skill by query |
| `habitat_*` | status / open / pulse / assign |
| `screen_*` | status / view / control / off / sense |
| `vcomp_open` | Virtual computer |
| `work_*` | start / status / package / handoff |
| `fusion_voice` | Conversational Fusion route |
| `fusion_schema` / `fusion_last` | Schema / last result |
| `aria_turn` / `voice_skills_list` | Aria everyday + fusion hint |
| `phone_surface` / `pair_mint` / `pair_status` | Phone + desk pair |
| `mcp_catalog` / `mcp_invoke` / `cli_list` / `cli_run` | Agent tools |

Example:

```http
POST /v1/skills/run
{ "skill": "fusion_voice", "prompt": "flight delayed need hotel hold" }
```

```http
POST /v1/mcp/invoke
{ "server": "pocket", "tool": "platform_map" }
```

## Module map

| Domain | Modules |
|--------|---------|
| Coherence | `platform_coherence.py`, `platform_api.py` |
| Habitat | `agent_habitat.py`, `app_ui.py` |
| Screen / VComp | `screen_share.py`, `virtual_computer.py` |
| Work | `work_mode.py`, `voice_skills.py` |
| Voice Fusion | `conversational_fusion.py`, `executor.py` |
| Phone / pair | `phone_ui.py`, `node_transfer.py` |
| Skills | `skill_suite.py`, `skill_runner.py`, `orchestrator_exec.py` |
| MCP / CLI | `mcp_bundle.py`, `mcp_server.py`, `cli_tools.py` |
| Agents | `first_class_agents.py`, `agentic_harness.py`, `executor.py` |

Source of truth: `pocket.platform_api.SURFACE` + `pocket.platform_coherence.SURFACES`.

## MCP stdio

```bash
set PYTHONPATH=src
python -m pocket.mcp_server
```

`~/.grok/config.toml` → `[mcp_servers.pocket]`.

## Desk UI findability

- Top tabs stay **inside** the POCKET shell (`showAppTab`)  
- Habitat open by default  
- Phone tab embeds `/phone`  
- Agents: “list skills”, “platform map”, “find feature habitat”  

## Phone findability

- Aria + Working first-class modes  
- Pair with desk code from Workspace  
- Fusion chip on voice turns  
