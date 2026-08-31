# POCKET — Platform index

**Version:** live via `GET /v1/catalog` · **Product:** Native Agent OS on your computer  
**Lab:** ItsNotAI Labs · **Company:** Medina Tech Labs

This is the **master map** of everything built and wired. How-to recipes: [HOW_TO.md](HOW_TO.md) · Live hub: `/docs`

**Binding doctrine (read first):** [../DOCTRINE.md](../DOCTRINE.md) · [DOCTRINE.md](DOCTRINE.md) · live `GET /v1/doctrine`

---

## Which POCKET?

| Face | Open |
|------|------|
| **YOUR POCKET** | http://127.0.0.1:8787/which · shortcut **POCKET Owner** |
| **USER FACING** | https://pocket.medinatechlabs.net · shortcut **POCKET Seat (test)** |

[WHICH_POCKET.md](WHICH_POCKET.md) — gold OWNER vs green SEAT.

## Start here

| Step | Action |
|------|--------|
| 1 | `PYTHONPATH=src python -m pocket serve --host 0.0.0.0 --port 8787` |
| 2 | Open http://127.0.0.1:8787/which then `/desk` — Owner login from `~/.pocket/ACCESS.txt` |
| 3 | **Agents toolkit (all MCP tools + uses):** [AGENTS_MCP_TOOLS.md](AGENTS_MCP_TOOLS.md) · live `GET /v1/agents/tools` |
| 4 | Browse http://127.0.0.1:8787/docs |
| 5 | Agent mail http://127.0.0.1:8787/mail |
| 6 | Install slices http://127.0.0.1:8787/install |
| 7 | MCP: `PYTHONPATH=src python -m pocket.mcp_server` |

---

## Product systems (built)

| ID | Name | Surface / API | How-to |
|----|------|---------------|--------|
| desk | Desk | `/desk` · sessions/jobs | [how-to/DESK.md](how-to/DESK.md) |
| phone | Phone | `/phone` · pair | [how-to/PHONE.md](how-to/PHONE.md) |
| agent_mail | **Agent Mail** | `/mail` · `/v1/agent-mail/*` | [how-to/AGENT_MAIL.md](how-to/AGENT_MAIL.md) |
| pocket_mail | POCKET MAIL (SMTP) | `/v1/mail/*` | same |
| genetic_flow | **Internal models · genetic** | mode=`genetic` · `/v1/genetic/*` | [how-to/GENETIC_FLOW.md](how-to/GENETIC_FLOW.md) |
| web_ui | **Website UI + engines** | `/v1/web-ui/*` · MCP | [how-to/WEB_UI_ENGINES.md](how-to/WEB_UI_ENGINES.md) |
| mcp | MCP Colony | stdio MCP server | [how-to/MCP.md](how-to/MCP.md) |
| install | Install slices | `/install` | [how-to/INSTALL.md](how-to/INSTALL.md) |
| keep | KEEP · ISOLATE · RECALL | `/v1/keep` · isolate · recall | [KEEP_ISOLATE_RECALL_MAIL.md](KEEP_ISOLATE_RECALL_MAIL.md) |
| rah | RAH harnesses | `/v1/rah/run` | [how-to/RAH.md](how-to/RAH.md) |
| loomgraph | LOOMGRAPH | `/loomgraph` | [LOOMGRAPH.md](LOOMGRAPH.md) |
| work_studio | Work Studio | `/work` | [how-to/WORK_STUDIO.md](how-to/WORK_STUDIO.md) |
| habitat | Habitat | desk rail | skill `habitat_status` |
| screen | Screen · OCULUS · VComp | desk columns | skill `screen_sense` |
| voice | Aria · Voice Studio | `/studio/voice` | [VOICE_STUDIO.md](VOICE_STUDIO.md) |
| economy | Economy · twins | `/v1/economy` | skills `economy_*` |
| capsule | WASM capsules | skills `capsule_*` | protocol docs |
| pixel | Pixel memory | `/v1/vmem` | [CODING_SWARM_PIXEL.md](CODING_SWARM_PIXEL.md) |

---

## Doctrine (short)

1. **Host-first** — work runs on this PC, not a vendor chat tab.  
2. **Skills = MCP = API = same Python modules.**  
3. **Models use engines** — website UIs via `web_ui_*` / `python_engine`, not user clicking MCP UIs.  
4. **Internal models are modules** — genetic flow picks which run.  
5. **Agents have their own mail** — `*@agents.pocket.local` inboxes.  
6. **Explicit send / never auto-pay.**  

---

## Key code modules

| Module | Role |
|--------|------|
| `pocket.server` | HTTP host :8787 |
| `pocket.agent_mail` | Agent accounts + inboxes |
| `pocket.pocket_mail` | Official SMTP mail |
| `pocket.web_ui_engine` | Website UI + 20 Python engines |
| `pocket.internal_models` | Genetic flow modules |
| `pocket.mcp_bundle` / `mcp_server` | MCP tools |
| `pocket.platform_coherence` | Platform skills map |
| `pocket.platform_catalog` | Live catalog |
| `pocket.install_hub` | One-line slices |
| `pocket.rah` | Recursive harnesses |
| `pocket.keep_agents` | KEEP until chat ends |

---

## Related docs

- [../DOCTRINE.md](../DOCTRINE.md) — binding laws, oath, faces, forbidden, amendment  
- [doctrine/BEINGS.md](doctrine/BEINGS.md) — every AI + organism: oaths, vows, laws · `GET /v1/doctrine/beings`  
- [HOW_TO.md](HOW_TO.md) — recipe index  
- [PLATFORM_SURFACE.md](PLATFORM_SURFACE.md) — surfaces  
- [API_QUICKSTART.md](API_QUICKSTART.md) — API  
- [SECURITY.md](SECURITY.md) — isolation  
- [SHIP_FOR_USERS.md](SHIP_FOR_USERS.md) — ship  
- [GENETIC_FLOW.md](GENETIC_FLOW.md) — genetic doctrine  
- [KEEP_ISOLATE_RECALL_MAIL.md](KEEP_ISOLATE_RECALL_MAIL.md) — keep/mail  
