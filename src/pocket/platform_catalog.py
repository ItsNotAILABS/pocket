"""Live catalog of everything POCKET has built — one place for docs, agents, APIs.

Used by:
  GET /v1/catalog
  GET /v1/platform/catalog
  docs hub HTML
  identity inject (short form)
"""

from __future__ import annotations

from typing import Any, Dict, List

from pocket import PRODUCT, TAGLINE, LAB, __version__, COMPANY, ORG


def systems() -> List[Dict[str, Any]]:
    """Ordered product systems (built + wired)."""
    return [
        {
            "id": "desk",
            "name": "Desk",
            "where": "/desk",
            "api": ["/v1/sessions", "/v1/jobs"],
            "how_to": "docs/how-to/DESK.md",
            "for": "Coding agents · sessions · live rail",
        },
        {
            "id": "phone",
            "name": "Phone",
            "where": "/phone",
            "api": ["/v1/phone", "/v1/pair"],
            "how_to": "docs/how-to/PHONE.md",
            "for": "Remote seat · Aria · assist",
        },
        {
            "id": "agent_mail",
            "name": "Agent Mail",
            "where": "/mail",
            "api": [
                "/v1/agent-mail",
                "/v1/agent-mail/accounts",
                "/v1/agent-mail/inbox",
                "/v1/agent-mail/send",
            ],
            "skills": [
                "mail_status",
                "mail_accounts",
                "mail_account_create",
                "mail_inbox",
                "mail_send",
                "mail_read",
            ],
            "mcp": ["mail_status", "mail_inbox", "mail_send", "mail_accounts"],
            "how_to": "docs/how-to/AGENT_MAIL.md",
            "domain": "agents.pocket.local",
            "for": "Our own agent email accounts + inboxes",
        },
        {
            "id": "pocket_mail",
            "name": "POCKET MAIL",
            "where": "/mail",
            "api": ["/v1/mail", "/v1/mail/draft", "/v1/mail/send"],
            "skills": ["mail_draft", "mail_status"],
            "how_to": "docs/how-to/AGENT_MAIL.md",
            "for": "Official SMTP + templates (external send)",
        },
        {
            "id": "genetic_flow",
            "name": "Internal models · Genetic flow",
            "where": "mode=genetic",
            "api": [
                "/v1/internal-models",
                "/v1/genetic/run",
                "/v1/genetic/status",
                "/v1/internal-models/express",
            ],
            "skills": ["internal_models", "genetic_flow", "genetic_status", "express_model"],
            "modes": ["genetic", "genetic_flow", "internal", "internal_models"],
            "how_to": "docs/how-to/GENETIC_FLOW.md",
            "for": "Modules (ghost·world·auro·guppy·heuristic·identity) evolve which run",
        },
        {
            "id": "web_ui",
            "name": "Website UI Engine",
            "where": "MCP web_ui_* · Python engines",
            "api": [
                "/v1/web-ui",
                "/v1/web-ui/open",
                "/v1/web-ui/sense",
                "/v1/web-ui/browse",
                "/v1/python-engine",
                "/v1/python-engines",
            ],
            "skills": [
                "web_ui_open",
                "web_ui_sense",
                "web_ui_act",
                "web_ui_browse",
                "web_ui_fetch",
                "python_engine",
                "python_engines_list",
            ],
            "mcp": ["web_ui_open", "web_ui_browse", "python_engine", "python_engines_list"],
            "how_to": "docs/how-to/WEB_UI_ENGINES.md",
            "for": "Models drive websites via Python — no user MCP tabs",
        },
        {
            "id": "mcp",
            "name": "MCP Colony",
            "where": "python -m pocket.mcp_server",
            "api": ["/v1/mcp", "/v1/skills/run"],
            "how_to": "docs/how-to/MCP.md",
            "for": "10 MCPs · pocket core + github + nexus + loom + CF + fs",
        },
        {
            "id": "install",
            "name": "Install slices",
            "where": "/install",
            "api": ["/v1/install/slices"],
            "how_to": "docs/how-to/INSTALL.md",
            "for": "One-line SDK · skills · knowledge · plug-n-play agent",
        },
        {
            "id": "keep",
            "name": "KEEP · ISOLATE · RECALL",
            "where": "API + docs",
            "api": ["/v1/keep", "/v1/isolate", "/v1/recall"],
            "how_to": "docs/KEEP_ISOLATE_RECALL_MAIL.md",
            "for": "Agents until chat ends · isolated browsers · recall codes",
        },
        {
            "id": "rah",
            "name": "RAH",
            "where": "mode=rah · skill rah_run",
            "api": ["/v1/rah/run", "/v1/rah/plan", "/v1/rah/status"],
            "skills": ["rah_run", "rah_plan", "rah_status"],
            "how_to": "docs/how-to/RAH.md",
            "for": "Recursive Agent Harnesses — full sub-harness fan-out",
        },
        {
            "id": "loomgraph",
            "name": "LOOMGRAPH",
            "where": "/loomgraph",
            "api": ["/v1/loomgraph/run", "/v1/loomgraph"],
            "how_to": "docs/LOOMGRAPH.md",
            "for": "See the graph · run the loop",
        },
        {
            "id": "work_studio",
            "name": "Work Studio",
            "where": "/work",
            "api": ["/v1/work-studio", "/v1/work-studio/assist"],
            "how_to": "docs/how-to/WORK_STUDIO.md",
            "for": "Digital life assistant · loops → desk handoff",
        },
        {
            "id": "habitat",
            "name": "Habitat",
            "where": "desk rail",
            "api": ["/v1/habitat"],
            "skills": ["habitat_status", "habitat_pulse"],
            "for": "Agents live on hybrid GUI floor",
        },
        {
            "id": "screen",
            "name": "Screen · OCULUS · VComp",
            "where": "desk columns",
            "api": ["/v1/screen", "/v1/vision"],
            "skills": ["screen_sense", "remote_browser_open"],
            "for": "View/Control + fusion sense + remote browser",
        },
        {
            "id": "voice",
            "name": "Aria · Voice",
            "where": "/studio/voice · mode=voice",
            "api": ["/v1/voice"],
            "how_to": "docs/VOICE_STUDIO.md",
            "for": "Talk · act · speak back",
        },
        {
            "id": "economy",
            "name": "Economy",
            "where": "API · skills",
            "api": ["/v1/economy"],
            "skills": ["economy_map", "economy_twins"],
            "for": "Wallets · twin wallets · Parallax bridge",
        },
        {
            "id": "capsule",
            "name": "WASM Capsules",
            "where": "skills capsule_*",
            "api": ["/v1/capsules"],
            "skills": ["capsule_allocate", "capsule_execute", "capsule_reasons"],
            "for": "Isolated untrusted work · WebGPU",
        },
        {
            "id": "pixel",
            "name": "Pixel memory",
            "where": "desk Workspace rail",
            "api": ["/v1/vmem", "/v1/vmem/put"],
            "how_to": "docs/CODING_SWARM_PIXEL.md",
            "for": "Store · look · recreate · pass artifacts",
        },
    ]


def quick_start() -> List[Dict[str, str]]:
    return [
        {"step": "1", "title": "Start host", "cmd": "python -m pocket serve --host 0.0.0.0 --port 8787"},
        {"step": "2", "title": "Open desk", "url": "http://127.0.0.1:8787/desk"},
        {"step": "3", "title": "Sign in", "note": "ACCESS.txt password · user pocket"},
        {"step": "4", "title": "Docs hub", "url": "http://127.0.0.1:8787/docs"},
        {"step": "5", "title": "Agent mail", "url": "http://127.0.0.1:8787/mail"},
        {"step": "6", "title": "Install slices", "url": "http://127.0.0.1:8787/install"},
        {"step": "7", "title": "MCP for agents", "cmd": "PYTHONPATH=src python -m pocket.mcp_server"},
    ]


def how_tos() -> List[Dict[str, str]]:
    return [
        {"id": "desk", "title": "Desk & agents", "path": "docs/how-to/DESK.md"},
        {"id": "agent_mail", "title": "Agent Mail", "path": "docs/how-to/AGENT_MAIL.md"},
        {"id": "genetic", "title": "Genetic flow", "path": "docs/how-to/GENETIC_FLOW.md"},
        {"id": "web_ui", "title": "Website UI & Python engines", "path": "docs/how-to/WEB_UI_ENGINES.md"},
        {"id": "mcp", "title": "MCP for models", "path": "docs/how-to/MCP.md"},
        {"id": "install", "title": "One-line install slices", "path": "docs/how-to/INSTALL.md"},
        {"id": "rah", "title": "RAH harnesses", "path": "docs/how-to/RAH.md"},
        {"id": "work", "title": "Work Studio", "path": "docs/how-to/WORK_STUDIO.md"},
        {"id": "phone", "title": "Phone pair", "path": "docs/how-to/PHONE.md"},
        {"id": "api", "title": "API recipes", "path": "docs/how-to/API_RECIPES.md"},
    ]


def catalog() -> Dict[str, Any]:
    """Full live catalog for API + docs hub."""
    systems_list = systems()
    skills_n = 0
    mcp_n = 0
    try:
        from pocket.platform_coherence import PLATFORM_SKILLS

        skills_n = len(PLATFORM_SKILLS)
    except Exception:
        pass
    try:
        from pocket.mcp_bundle import catalog as mcp_cat

        mcp_n = mcp_cat().get("total") or 0
    except Exception:
        pass
    try:
        from pocket.agent_mail import status as am

        mail = am()
    except Exception:
        mail = {"ok": False}
    try:
        from pocket.internal_models import list_models

        models = list_models()
    except Exception:
        models = []
    try:
        from pocket.web_ui_engine import list_engines

        engines = list_engines().get("engines") or []
    except Exception:
        engines = []

    return {
        "ok": True,
        "schema": "pocket.platform_catalog.v1",
        "product": PRODUCT,
        "version": __version__,
        "tagline": TAGLINE,
        "lab": LAB,
        "company": COMPANY,
        "org": ORG,
        "systems": systems_list,
        "system_count": len(systems_list),
        "platform_skills": skills_n,
        "mcp_servers": mcp_n,
        "agent_mail": {
            "ok": mail.get("ok"),
            "domain": mail.get("domain"),
            "accounts": mail.get("accounts"),
            "unread": mail.get("total_unread"),
        },
        "internal_models": models,
        "python_engines": [{"id": e.get("id"), "for": e.get("for")} for e in engines],
        "quick_start": quick_start(),
        "how_tos": how_tos(),
        "docs": {
            "hub": "/docs",
            "index": "docs/INDEX.md",
            "how_to": "docs/HOW_TO.md",
            "genetic": "docs/GENETIC_FLOW.md",
            "keep_mail": "docs/KEEP_ISOLATE_RECALL_MAIL.md",
            "platform": "docs/PLATFORM_SURFACE.md",
        },
        "surfaces": {
            "desk": "/desk",
            "phone": "/phone",
            "mail": "/mail",
            "work": "/work",
            "install": "/install",
            "loomgraph": "/loomgraph",
            "developers": "/developers",
            "docs": "/docs",
            "health": "/health",
        },
        "doctrine": (
            "Organize once: systems are first-class, skills/MCP/API share the same Python modules, "
            "models use engines — not user browser tabs."
        ),
    }


def markdown_index() -> str:
    c = catalog()
    lines = [
        f"# {PRODUCT} platform catalog",
        f"**{c['version']}** · {c['tagline']}",
        "",
        "## Systems",
        "",
        "| System | Where | How-to |",
        "|--------|-------|--------|",
    ]
    for s in c["systems"]:
        lines.append(
            f"| **{s['name']}** | `{s.get('where','')}` | {s.get('how_to') or '—'} |"
        )
    lines += [
        "",
        "## Quick start",
        "",
    ]
    for q in c["quick_start"]:
        if q.get("cmd"):
            lines.append(f"{q['step']}. **{q['title']}** — `{q['cmd']}`")
        elif q.get("url"):
            lines.append(f"{q['step']}. **{q['title']}** — {q['url']}")
        else:
            lines.append(f"{q['step']}. **{q['title']}** — {q.get('note','')}")
    lines += [
        "",
        f"Live JSON: `GET /v1/catalog` · HTML hub: `/docs`",
        "",
    ]
    return "\n".join(lines)
