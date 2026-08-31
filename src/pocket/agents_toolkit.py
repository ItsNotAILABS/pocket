"""Comprehensive agent toolkit manifest — every tool & use for the POCKET app via internal MCP.

Agents should load this first:
  GET /v1/agents/tools
  skill agents_toolkit
  MCP: agents_toolkit | mcp_catalog | tools_for_prompt

Doctrine:
  · Internal MCP (pocket) is the primary tool surface
  · Skills / HTTP / python_engine share the same modules
  · Prefer engine_use (20 uses) for common work; model_build when a specialist is missing
"""

from __future__ import annotations

from typing import Any, Dict, List


def manifest() -> Dict[str, Any]:
    """Full live toolkit for agents."""
    from pocket import PRODUCT, __version__, LAB
    from pocket.mcp_bundle import catalog as mcp_catalog
    from pocket.platform_coherence import PLATFORM_SKILLS
    from pocket.web_ui_engine import ENGINE_USES, list_engines
    from pocket.model_forge import KINDS, list_built, status as forge_status

    mcp = mcp_catalog()
    pocket_tools: List[str] = []
    servers = []
    for s in mcp.get("servers") or []:
        servers.append(
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "kind": s.get("kind"),
                "blurb": s.get("blurb"),
                "tools": list(s.get("tools") or []),
            }
        )
        if s.get("id") == "pocket":
            pocket_tools = list(s.get("tools") or [])

    skills = [
        {
            "id": sid,
            "worker": meta.get("worker"),
            "desc": meta.get("desc"),
            "tags": meta.get("tags") or [],
            "kind": meta.get("kind"),
        }
        for sid, meta in sorted(PLATFORM_SKILLS.items())
    ]

    uses = [
        {
            "id": u["id"],
            "title": u["title"],
            "tool": u["tool"],
            "engine": u["engine"],
            "improves": u.get("improves"),
            "example": u.get("example"),
            "how": _use_how(u),
        }
        for u in ENGINE_USES
    ]

    engines = list_engines().get("engines") or []
    built = list_built()

    return {
        "ok": True,
        "schema": "pocket.agents_toolkit.v1",
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "doctrine": [
            "You are a POCKET host agent — not a generic chatbot.",
            "Call tools via internal MCP (server=pocket) or POST /v1/skills/run.",
            "Never open user browser tabs for MCP — invoke headlessly.",
            "Never auto-pay; never silent publish; draft mail by default.",
            "Prefer engine_use for the 20 named uses; model_build when you need a new specialist.",
            "Genetic flow evolves which internal models run for hard multi-model goals.",
        ],
        "how_to_call": {
            "stdio_mcp": "PYTHONPATH=src python -m pocket.mcp_server",
            "mcp_tools_list": "JSON-RPC tools/list → pocket_* + mcp_catalog + mcp_invoke + mcp_stream",
            "mcp_invoke": {
                "server": "pocket",
                "tool": "<tool_id>",
                "params": {"prompt": "…", "text": "…", "url": "…"},
            },
            "mcp_stream": {
                "poll": "GET /v1/mcp/stream?after=<seq>",
                "page": "GET /v1/mcp/stream/page",
                "clear": "POST /v1/mcp/stream/clear",
                "skill": "mcp_stream",
                "tool": "mcp_stream | pocket_mcp_stream",
            },
            "invoke_any_being": 'POST /v1/agents/invoke {"name":"<id from GET /v1/agents/roster>","prompt":"…"}  · skill agent_invoke · MCP pocket_agent_invoke',
            "roster": "GET /v1/agents/roster — every first-class agent (127+) plus Damian keepers",
            "autonomous": "GET /v1/agents/autonomous · skill autonomous_ensure",
            "http_skill": 'POST /v1/skills/run {"skill":"<id>","prompt":"…","params":{}}',
            "http_engine": 'POST /v1/python-engine {"engine":"<id>","prompt":"…"}',
            "http_use": 'POST /v1/engine-uses {"use":"<id>","prompt":"…"}',
            "http_use_auto": 'POST /v1/engine-uses {"goal":"free text"}',
            "http_model_build": "POST /v1/models/build",
            "catalog": "GET /v1/agents/tools  (this document, live JSON)",
            "docs": "/docs/view/AGENTS_MCP_TOOLS",
        },
        "mcp": {
            "total_servers": mcp.get("total"),
            "internal": mcp.get("internal"),
            "external": mcp.get("external"),
            "servers": servers,
            "pocket_tools": pocket_tools,
            "pocket_tool_count": len(pocket_tools),
        },
        "platform_skills": skills,
        "platform_skill_count": len(skills),
        "engine_uses": uses,
        "engine_use_count": len(uses),
        "python_engines": engines,
        "python_engine_count": len(engines),
        "model_forge": {
            "kinds": list(KINDS),
            "built_count": built.get("count"),
            "status": forge_status(),
        },
        "surfaces": {
            "desk": "/desk",
            "phone": "/phone",
            "mail": "/mail",
            "docs": "/docs",
            "install": "/install",
            "work": "/work",
            "loomgraph": "/loomgraph",
            "catalog": "/v1/catalog",
            "agents_tools": "/v1/agents/tools",
        },
        "quick_start_for_agents": _quick_start(),
        "tool_groups": _tool_groups(pocket_tools),
        "safety": [
            "Never auto-pay (food, shop, flights, reservations — user confirms)",
            "Never silent SMTP send without explicit intent",
            "Act on UI only when Control/VComp armed",
            "Code models forbid import/open/exec",
            "Capsules for untrusted eval (20 capsule reasons)",
            "Market seats never see founder disk",
        ],
    }


def _use_how(u: Dict[str, Any]) -> str:
    return (
        f'MCP invoke pocket/{u["tool"]} or skill {u["tool"]} '
        f'or POST /v1/engine-uses {{"use":"{u["id"]}","prompt":"…"}} '
        f'or python_engine engine={u["engine"]}'
    )


def _quick_start() -> List[Dict[str, str]]:
    return [
        {"step": "1", "do": "mcp_catalog or GET /v1/agents/tools", "why": "See all tools"},
        {"step": "2", "do": "engine_uses", "why": "20 primary product uses"},
        {"step": "3", "do": "engine_use with goal text", "why": "Auto-route research/mail/browse/…"},
        {"step": "4", "do": "model_build if specialist missing", "why": "Register new internal model"},
        {"step": "5", "do": "genetic_flow for multi-model goals", "why": "Evolve which modules run"},
        {"step": "6", "do": "mail_* for agent inboxes", "why": "Our agents.pocket.local mail"},
        {"step": "7", "do": "web_ui_* for websites", "why": "Headless or signed-in Edge"},
        {"step": "8", "do": "capsule_* for untrusted work", "why": "Isolation + WebGPU"},
    ]


def _tool_groups(pocket_tools: List[str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {
        "platform": [],
        "screen_habitat": [],
        "work_voice_phone": [],
        "life_web": [],
        "integrations_loom": [],
        "capsules_studio": [],
        "mail": [],
        "web_ui_engines": [],
        "models_genetic": [],
        "other": [],
    }
    for t in pocket_tools:
        if t.startswith(("platform", "find_", "sovereign", "computing", "list_skills", "tools_for")):
            groups["platform"].append(t)
        elif t.startswith(("screen", "habitat", "vcomp", "remote_browser", "iot")):
            groups["screen_habitat"].append(t)
        elif t.startswith(("work_", "fusion", "aria", "phone", "pair", "voice")):
            groups["work_voice_phone"].append(t)
        elif t.startswith(("life_", "food", "flight", "shop", "web_", "reservation", "assist")):
            groups["life_web"].append(t)
        elif t.startswith(("integrations", "loomgraph")):
            groups["integrations_loom"].append(t)
        elif t.startswith(("capsule", "webgpu", "studio", "imagine", "viral")):
            groups["capsules_studio"].append(t)
        elif t.startswith("mail_"):
            groups["mail"].append(t)
        elif t.startswith(("web_ui", "python_engine", "engine_", "model_")):
            groups["web_ui_engines"].append(t)
        elif t.startswith(("genetic", "internal", "express", "rah")):
            groups["models_genetic"].append(t)
        else:
            groups["other"].append(t)
    return groups


def markdown() -> str:
    """Render comprehensive agent-facing markdown."""
    m = manifest()
    lines: List[str] = [
        f"# {m['product']} — Agents · Internal MCP · Tools & Uses",
        "",
        f"**Version:** {m['version']} · **Lab:** {m['lab']}  ",
        f"**Schema:** `{m['schema']}`  ",
        f"**Live JSON:** `GET /v1/agents/tools`  ",
        f"**HTML docs:** `/docs/view/AGENTS_MCP_TOOLS`",
        "",
        "This is the **one file agents need** for the POCKET app through our **internal MCP**.",
        "",
        "---",
        "",
        "## Doctrine",
        "",
    ]
    for d in m["doctrine"]:
        lines.append(f"- {d}")
    lines += [
        "",
        "## How to call tools",
        "",
        "### 1. Stdio MCP (Grok / Claude / Cursor)",
        "",
        "```bash",
        "PYTHONPATH=src python -m pocket.mcp_server",
        "```",
        "",
        "JSON-RPC: `initialize` · `tools/list` · `tools/call`",
        "",
        "| Tool name pattern | Meaning |",
        "|-------------------|---------|",
        "| `pocket_<tool>` | Core host tool (e.g. `pocket_mail_inbox`) |",
        "| `mcp_catalog` | List 10 MCP servers |",
        "| `mcp_invoke` | `{server, tool, params}` for any server |",
        "| `mcp_stream` | Live MCP JSON-RPC protocol stream (poll frames) |",
        "",
        "### Live MCP JSON-RPC Protocol Stream",
        "",
        "```http",
        "GET  /v1/mcp/stream?after=<seq>",
        "GET  /v1/mcp/stream/page",
        "POST /v1/mcp/stream/clear",
        "```",
        "",
        "Skill: `mcp_stream` · every invoke + stdio frame is mirrored mid-wire.",
        "",
        "### 2. HTTP skills (desk / any client)",
        "",
        "```http",
        "POST /v1/skills/run",
        'Content-Type: application/json',
        "",
        '{"skill":"engine_use","prompt":"research multi-agent hosts"}',
        "```",
        "",
        "### 3. Named uses (recommended entry point)",
        "",
        "```http",
        "GET  /v1/engine-uses",
        'POST /v1/engine-uses  {"goal":"check agent inbox"}',
        'POST /v1/engine-uses  {"use":"browse_sense","prompt":"https://example.com"}',
        "```",
        "",
        "### 4. Python engines",
        "",
        "```http",
        'POST /v1/python-engine  {"engine":"web_research","prompt":"POCKET agents"}',
        'POST /v1/python-engine  {"engine":"model_forge","prompt":"build math ROI model"}',
        "```",
        "",
        "---",
        "",
        "## Quick start for agents",
        "",
    ]
    for q in m["quick_start_for_agents"]:
        lines.append(f"{q['step']}. **{q['do']}** — {q['why']}")
    lines += [
        "",
        "---",
        "",
        "## 20 engine uses (primary product surface)",
        "",
        "| id | Title | Tool | Engine | Improves |",
        "|----|-------|------|--------|----------|",
    ]
    for u in m["engine_uses"]:
        lines.append(
            f"| `{u['id']}` | {u['title']} | `{u['tool']}` | `{u['engine']}` | {u.get('improves','')} |"
        )
    lines += [
        "",
        "### Examples",
        "",
        "```json",
        '{"skill":"engine_use","prompt":"research multi-agent edge hosts"}',
        '{"skill":"engine_use","params":{"use":"agent_mail"},"prompt":"inbox"}',
        '{"skill":"engine_use","params":{"use":"build_model"},"prompt":"ROI formula helper"}',
        '{"skill":"engine_use","params":{"use":"genetic_evolve"},"prompt":"hash plan and next steps"}',
        "```",
        "",
        "---",
        "",
        "## Internal MCP servers (3) + external (7)",
        "",
        "| Server | Kind | Blurb |",
        "|--------|------|-------|",
    ]
    for s in m["mcp"]["servers"]:
        lines.append(
            f"| `{s['id']}` | {s.get('kind')} | {s.get('blurb') or ''} |"
        )
    lines += [
        "",
        f"**POCKET core tools:** {m['mcp']['pocket_tool_count']}",
        "",
        "### Pocket tools by group",
        "",
    ]
    for gname, tools in (m.get("tool_groups") or {}).items():
        if not tools:
            continue
        lines.append(f"#### {gname}")
        lines.append("")
        lines.append(", ".join(f"`{t}`" for t in tools))
        lines.append("")
    lines += [
        "### Full pocket tool list",
        "",
        "```",
        "\n".join(m["mcp"]["pocket_tools"]),
        "```",
        "",
        "---",
        "",
        f"## Platform skills ({m['platform_skill_count']})",
        "",
        "Same modules as MCP — call via `POST /v1/skills/run`.",
        "",
        "| Skill | Worker | Description |",
        "|-------|--------|-------------|",
    ]
    for s in m["platform_skills"]:
        desc = (s.get("desc") or "").replace("|", "/")
        lines.append(f"| `{s['id']}` | {s.get('worker') or ''} | {desc} |")
    lines += [
        "",
        "---",
        "",
        f"## Python engines ({m['python_engine_count']})",
        "",
        "| Engine | For |",
        "|--------|-----|",
    ]
    for e in m["python_engines"]:
        lines.append(f"| `{e.get('id')}` | {e.get('for') or ''} |")
    lines += [
        "",
        "---",
        "",
        "## Model Forge — build models when needed",
        "",
        f"**Kinds:** {', '.join(f'`{k}`' for k in m['model_forge']['kinds'])}  ",
        f"**Built on host:** {m['model_forge']['built_count']}",
        "",
        "```http",
        "POST /v1/models/suggest  {\"goal\":\"calculate ROI with phi\"}",
        "POST /v1/models/build",
        "{",
        '  \"model_id\": \"user-roi\",',
        '  \"kind\": \"formula\",',
        '  \"formula\": \"x * phi\",',
        '  \"fit_keywords\": [\"roi\", \"phi\"],',
        '  \"register_now\": true',
        "}",
        "POST /v1/internal-models/express  {\"model\":\"user-roi\",\"goal\":\"100\"}",
        "POST /v1/genetic/run  {\"goal\":\"compute ROI with phi\",\"generations\":2}",
        "```",
        "",
        "Skills: `model_suggest` · `model_build` · `model_list_built` · `model_register` · `express_model` · `genetic_flow`",
        "",
        "---",
        "",
        "## Agent Mail",
        "",
        "| Action | Call |",
        "|--------|------|",
        "| Status | `mail_status` / GET `/v1/agent-mail` |",
        "| Accounts | `mail_accounts` |",
        "| Create | `mail_account_create` |",
        "| Inbox | `mail_inbox` params.agent |",
        "| Send | `mail_send` from/to/subject/body |",
        "| Read | `mail_read` |",
        "| UI | `/mail` |",
        "",
        "Domain: **agents.pocket.local**",
        "",
        "---",
        "",
        "## Genetic flow · internal models",
        "",
        "| Action | Call |",
        "|--------|------|",
        "| List modules | `internal_models` / GET `/v1/internal-models` |",
        "| Express one | `express_model` params.model |",
        "| Genetic run | `genetic_flow` / POST `/v1/genetic/run` |",
        "| Desk mode | `mode=genetic` |",
        "",
        "Built-in modules: ghost · world · auro · guppy · heuristic · identity (+ forged user-*)",
        "",
        "---",
        "",
        "## Capsules (untrusted work)",
        "",
        "`capsule_status` · `capsule_allocate` · `capsule_execute` · `capsule_commit` · `capsule_terminate` · `webgpu_probe`",
        "",
        "20 reasons: skill `capsule_reasons` (untrusted_eval, sandbox_tests, …).",
        "",
        "---",
        "",
        "## Surfaces",
        "",
        "| Surface | Path |",
        "|---------|------|",
    ]
    for k, v in (m.get("surfaces") or {}).items():
        lines.append(f"| {k} | `{v}` |")
    lines += [
        "",
        "---",
        "",
        "## Safety",
        "",
    ]
    for s in m["safety"]:
        lines.append(f"- {s}")
    lines += [
        "",
        "---",
        "",
        "## Recipe cheat sheet",
        "",
        "```text",
        "Orient          → platform_map | pocket_identity | protocols_map",
        "Research        → engine_use research_topic | web_ui_search | web_search",
        "Read URL        → engine_use read_page | web_ui_fetch",
        "Open site       → engine_use open_site | web_ui_browse",
        "Sense screen    → screen_sense | web_ui_sense",
        "Life ops        → life_catalog | food_order | flight_search | shop_search",
        "Mail            → mail_inbox | mail_send",
        "Need specialist → model_suggest → model_build → express_model",
        "Hard multi-model→ genetic_flow",
        "Untrusted code  → capsule_allocate → capsule_execute",
        "Ship demo       → studio_ship | studio_viral",
        "Graph loop      → loomgraph_run",
        "Parallel big    → rah_run (expensive)",
        "```",
        "",
        "---",
        "",
        f"_Generated live by `pocket.agents_toolkit` · {m['version']}_",
        "",
    ]
    return "\n".join(lines)


def write_docs_file() -> Dict[str, Any]:
    """Write docs/AGENTS_MCP_TOOLS.md under the repo."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    path = root / "docs" / "AGENTS_MCP_TOOLS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = markdown()
    path.write_text(text, encoding="utf-8")
    # also root AGENTS.md for coding agents
    agents = root / "AGENTS.md"
    agents.write_text(
        "# POCKET — for coding agents\n\n"
        "Load the full toolkit:\n\n"
        "- **Live:** `GET http://127.0.0.1:8787/v1/agents/tools`\n"
        "- **Doc:** [docs/AGENTS_MCP_TOOLS.md](docs/AGENTS_MCP_TOOLS.md)\n"
        "- **HTML:** `/docs/view/AGENTS_MCP_TOOLS`\n"
        "- **Skill:** `agents_toolkit`\n"
        "- **MCP:** `python -m pocket.mcp_server` then `mcp_catalog` / `pocket_*` tools\n\n"
        + text[:12000]
        + "\n\n_(truncated in AGENTS.md — full file at docs/AGENTS_MCP_TOOLS.md)_\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "path": str(path),
        "agents_md": str(agents),
        "bytes": path.stat().st_size,
        "skills": m_count_skills(),
        "tools": m_count_tools(),
    }


def m_count_skills() -> int:
    try:
        from pocket.platform_coherence import PLATFORM_SKILLS

        return len(PLATFORM_SKILLS)
    except Exception:
        return 0


def m_count_tools() -> int:
    try:
        from pocket.mcp_bundle import catalog

        for s in catalog().get("servers") or []:
            if s.get("id") == "pocket":
                return len(s.get("tools") or [])
    except Exception:
        pass
    return 0
