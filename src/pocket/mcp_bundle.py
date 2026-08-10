"""POCKET embedded MCP catalog — 3 internal + 7 best external.

Agents call tools through this registry (CLI / HTTP / local bridges).
Users do **not** open browser tabs for these — agents invoke them headlessly.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 10 MCPs: 3 internal (host stack) + 7 external (best-in-class)
# ---------------------------------------------------------------------------

INTERNAL_MCPS: List[Dict[str, Any]] = [
    {
        "id": "pocket",
        "name": "POCKET Core",
        "kind": "internal",
        "transport": "python",
        "module": "pocket.mcp_server",
        "blurb": "Coherent host: habitat · screen · work · fusion voice · phone pair · drafts · CLI",
        "tools": [
            "platform_map", "platform_health", "find_feature",
            "sovereign_stack", "computing_clouds",
            "remote_browser_status", "remote_browser_open", "remote_browser_sense", "remote_browser_benchmark",
            "iot_status", "iot_list", "iot_register", "iot_phone", "iot_hz_status",
            "habitat_status", "habitat_pulse", "habitat_assign",
            "screen_status", "screen_set", "screen_sense", "screen_act",
            "vcomp_open", "vcomp_sense", "vcomp_act", "vcomp_shell",
            "work_start", "work_tick", "work_package", "work_handoff", "work_status",
            "fusion_voice", "fusion_schema", "aria_turn",
            "phone_surface", "pair_mint", "pair_status",
            "draft_create", "draft_promote", "cli_run", "cli_list",
            # Everyday life — all agents (never auto-pay)
            "life_catalog", "life_status", "life_classify",
            "food_order", "flight_search", "shop_search", "web_browse", "reservation",
            "web_search", "web_fetch", "integrations_list", "integrations_execute",
            "integrations_readiness", "loomgraph_run", "loomgraph_catalog",
            "loomgraph_status", "assist_route",
            "list_skills", "wsl_status", "auro_status", "muse_status", "tools_for_prompt",
            # PROTO-CAPSULE-WASM-009 multi-sandbox + WebGPU
            "capsule_status", "capsule_list", "capsule_allocate", "capsule_execute",
            "capsule_commit", "capsule_terminate", "webgpu_probe",
            # Product Studio first-class
            "studio_map", "studio_status", "studio_open", "studio_playbooks",
            "studio_storyboard", "studio_caption", "studio_list_recordings",
            "studio_list_exports", "studio_presets", "studio_record_start",
            "studio_record_stop", "studio_render", "studio_viral", "studio_batch",
            "studio_ship", "imagine_compose",
            # Agent mail (our own accounts + inboxes)
            "mail_status", "mail_accounts", "mail_account_create",
            "mail_inbox", "mail_send", "mail_read", "mail_draft",
            # Website interfaces via Python engines
            "web_ui_open", "web_ui_sense", "web_ui_act", "web_ui_fetch",
            "web_ui_search", "web_ui_browse", "web_ui_status",
            # Models → Python agents / engines
            "python_engine", "python_engines_list",
        ],
    },
    {
        "id": "nexus",
        "name": "NEXUS MERIDIAN",
        "kind": "internal",
        "transport": "stdio",
        "command": "python",
        "args_hint": r"-c import nexus.server",
        "path_hint": r"C:\Users\Medin\OneDrive\nexus",
        "blurb": "Nine workers · MCP federation · intelligence tools",
        "tools": ["list_repos", "status", "security_audit", "list_mcp_servers"],
    },
    {
        "id": "loom",
        "name": "LOOM",
        "kind": "internal",
        "transport": "catalog",
        "catalog_dir": r"C:\Users\Medin\OneDrive\mcps\loom",
        "blurb": "Agents dispatch · vault · runspace · knowledge · plans",
        "tools": ["agents_dispatch", "vault_search", "plan_create", "skills_run", "workspace_view"],
    },
]

EXTERNAL_MCPS: List[Dict[str, Any]] = [
    {
        "id": "github",
        "name": "GitHub",
        "kind": "external",
        "transport": "cli",  # agent uses `gh` CLI — no user tab
        "bin": "gh",
        "blurb": "Repos · PRs · issues · via gh CLI (signed-in host)",
        "tools": ["repo_list", "pr_list", "issue_list", "pr_create", "clone", "api"],
    },
    {
        "id": "cloudflare-docs",
        "name": "Cloudflare Docs",
        "kind": "external",
        "transport": "http",
        "url": "https://docs.mcp.cloudflare.com/mcp",
        "blurb": "Workers · Pages · platform docs for agents",
        "tools": ["search", "read"],
    },
    {
        "id": "cloudflare",
        "name": "Cloudflare",
        "kind": "external",
        "transport": "http",
        "url": "https://mcp.cloudflare.com/mcp",
        "blurb": "Account / product MCP surface",
        "tools": ["*"],
    },
    {
        "id": "cloudflare-bindings",
        "name": "Cloudflare Bindings",
        "kind": "external",
        "transport": "http",
        "url": "https://bindings.mcp.cloudflare.com/mcp",
        "blurb": "KV · D1 · R2 · bindings for Workers",
        "tools": ["*"],
    },
    {
        "id": "cloudflare-builds",
        "name": "Cloudflare Builds",
        "kind": "external",
        "transport": "http",
        "url": "https://builds.mcp.cloudflare.com/mcp",
        "blurb": "CI / Pages builds",
        "tools": ["*"],
    },
    {
        "id": "cloudflare-observability",
        "name": "Cloudflare Observability",
        "kind": "external",
        "transport": "http",
        "url": "https://observability.mcp.cloudflare.com/mcp",
        "blurb": "Logs · metrics for agents",
        "tools": ["*"],
    },
    {
        "id": "filesystem",
        "name": "Filesystem (agent workspace)",
        "kind": "external",
        "transport": "python",
        "module": "pocket.mcp_bundle",
        "blurb": "Read/write under allowed workspaces only — agent CLI style",
        "tools": ["fs_read", "fs_write", "fs_list", "fs_stat"],
    },
]


def catalog() -> Dict[str, Any]:
    all_m = INTERNAL_MCPS + EXTERNAL_MCPS
    return {
        "ok": True,
        "schema": "pocket.mcp_bundle.v1",
        "doctrine": (
            "10 MCPs embedded: 3 internal (pocket · nexus · loom) + 7 external. "
            "Agents invoke tools headlessly — never open user browser tabs for MCP."
        ),
        "internal": 3,
        "external": 7,
        "total": len(all_m),
        "servers": all_m,
        "agent_access": True,
        "user_tabs": False,
    }


def list_tools() -> Dict[str, Any]:
    tools = []
    for s in INTERNAL_MCPS + EXTERNAL_MCPS:
        for t in s.get("tools") or []:
            tools.append({
                "server": s["id"],
                "kind": s["kind"],
                "tool": t,
                "blurb": s.get("blurb"),
            })
    return {"ok": True, "count": len(tools), "tools": tools}


def _safe_workspace(path: str = "") -> Path:
    home = Path.home().resolve()
    allowed = [
        home / ".pocket",
        home / "OneDrive" / "pocket-os",
        home / "Documents",
        Path(os.environ.get("POCKET_WORKSPACE") or home / ".pocket" / "workspace"),
    ]
    p = Path(path or (home / ".pocket" / "workspace")).expanduser()
    try:
        rp = p.resolve()
    except Exception:
        rp = p
    for a in allowed:
        try:
            rp.relative_to(a.resolve())
            return rp
        except Exception:
            continue
    # default workspace only
    d = home / ".pocket" / "workspace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fs_list(path: str = "", limit: int = 40) -> Dict[str, Any]:
    root = _safe_workspace(path) if path else _safe_workspace("")
    if not root.exists():
        return {"ok": False, "error": f"missing {root}"}
    items = []
    try:
        for c in sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:limit]:
            items.append({"name": c.name, "dir": c.is_dir(), "bytes": c.stat().st_size if c.is_file() else 0})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "path": str(root), "items": items}


def fs_read(path: str, max_chars: int = 12000) -> Dict[str, Any]:
    p = _safe_workspace(path) if not Path(path).is_absolute() else Path(path)
    # re-check under home
    try:
        p.resolve().relative_to(Path.home().resolve())
    except Exception:
        return {"ok": False, "error": "path must be under home"}
    if not p.is_file():
        return {"ok": False, "error": "not a file"}
    try:
        text = p.read_text(encoding="utf-8", errors="replace")[:max_chars]
        return {"ok": True, "path": str(p), "text": text, "bytes": p.stat().st_size}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def fs_write(path: str, content: str) -> Dict[str, Any]:
    p = Path(path).expanduser()
    try:
        p.resolve().relative_to(Path.home().resolve())
    except Exception:
        return {"ok": False, "error": "path must be under home"}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content or "", encoding="utf-8")
    return {"ok": True, "path": str(p), "bytes": p.stat().st_size}


def invoke(server: str, tool: str, **params) -> Dict[str, Any]:
    """Agent-facing MCP invoke — routes internal/external without user UI."""
    sid = (server or "").lower().strip()
    tool = (tool or "").lower().strip()

    # --- pocket internal ---
    if sid in ("pocket", "pocket-core"):
        return _invoke_pocket(tool, params)

    # --- github via gh CLI (no browser tab) ---
    if sid == "github":
        return _invoke_github(tool, params)

    # --- filesystem ---
    if sid == "filesystem":
        if tool in ("fs_list", "list"):
            return fs_list(params.get("path") or "", int(params.get("limit") or 40))
        if tool in ("fs_read", "read"):
            return fs_read(params.get("path") or "", int(params.get("max_chars") or 12000))
        if tool in ("fs_write", "write"):
            return fs_write(params.get("path") or "", params.get("content") or "")
        if tool == "fs_stat":
            p = Path(params.get("path") or "").expanduser()
            if not p.exists():
                return {"ok": False, "error": "missing"}
            st = p.stat()
            return {"ok": True, "path": str(p), "bytes": st.st_size, "dir": p.is_dir()}

    # --- nexus bridge if present ---
    if sid == "nexus":
        try:
            from pocket import nexus_bridge as nb

            if hasattr(nb, "run_nexus"):
                return nb.run_nexus(params.get("prompt") or tool, job={})
            if hasattr(nb, "status"):
                return {"ok": True, "status": nb.status(), "tool": tool, "params": params}
            return {"ok": True, "module": "nexus_bridge", "tool": tool, "note": "use NEXUS desk agent for full runs"}
        except Exception as e:
            return {"ok": False, "error": f"nexus: {e}", "hint": "ensure NEXUS on host"}

    # --- loom catalog hint ---
    if sid == "loom":
        cat = Path(r"C:\Users\Medin\OneDrive\mcps\loom\tools")
        tools = [p.stem for p in cat.glob("*.json")][:40] if cat.is_dir() else []
        return {
            "ok": True,
            "server": "loom",
            "tool": tool,
            "note": "LOOM tools catalog on disk — wire live stdio when loom server is running",
            "available_tools": tools,
            "params": params,
        }

    # --- remote HTTP MCP (document only — live session uses grok config) ---
    for s in EXTERNAL_MCPS:
        if s["id"] == sid and s.get("transport") == "http":
            return {
                "ok": True,
                "server": sid,
                "tool": tool,
                "transport": "http",
                "url": s.get("url"),
                "note": (
                    "Remote MCP is configured in ~/.grok/config.toml for Grok. "
                    "POCKET agents use CLI/local bridges for host work; "
                    "Grok/Claude sessions inherit the remote MCP tools."
                ),
                "params": params,
            }

    return {"ok": False, "error": f"unknown server/tool {sid}.{tool}", "catalog": catalog()["servers"]}


def _invoke_mail_web(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent mail + website UI + Python engines (shared MCP / skill path)."""
    t = (tool or "").lower().strip()
    p = params or {}

    # --- Agent mail (our own accounts) ---
    if t in ("mail_status", "agent_mail_status"):
        from pocket.agent_mail import status as am_status

        return am_status()
    if t in ("mail_accounts", "agent_mail_accounts"):
        from pocket.agent_mail import list_accounts

        return list_accounts(limit=int(p.get("limit") or 100))
    if t in ("mail_account_create", "agent_mail_create", "create_mail_account"):
        from pocket.agent_mail import create_account

        return create_account(
            p.get("agent") or p.get("agent_id") or p.get("id") or p.get("name") or "",
            name=p.get("name") or "",
            blurb=p.get("blurb") or p.get("desc") or "",
            kind=p.get("kind") or "agent",
            owner=p.get("owner") or "",
        )
    if t in ("mail_inbox", "agent_inbox", "inbox"):
        from pocket.agent_mail import inbox

        return inbox(
            p.get("agent") or p.get("agent_id") or p.get("from_agent") or "assist",
            limit=int(p.get("limit") or 30),
            unread_only=bool(p.get("unread_only") or p.get("unread")),
        )
    if t in ("mail_send", "agent_mail_send"):
        from pocket.agent_mail import send as am_send

        return am_send(
            from_agent=p.get("from") or p.get("from_agent") or p.get("agent") or "scribe",
            to=p.get("to") or "",
            subject=p.get("subject") or "POCKET agent mail",
            body=p.get("body") or p.get("text") or p.get("prompt") or "",
            cc=p.get("cc") or "",
            external=bool(p.get("external")),
            dry_run=bool(p.get("dry_run")),
        )
    if t in ("mail_read", "agent_mail_read"):
        from pocket.agent_mail import read_message

        return read_message(
            p.get("agent") or p.get("agent_id") or "assist",
            p.get("id") or p.get("mail_id") or p.get("message_id") or "",
            mark_read=p.get("mark_read", True) is not False,
        )
    if t in ("mail_draft",):
        from pocket.pocket_mail import draft as mail_draft

        return mail_draft(
            to=p.get("to") or "",
            subject=p.get("subject") or "",
            body=p.get("body") or p.get("text") or "",
            template=p.get("template") or "custom",
            owner=p.get("owner") or p.get("agent") or "",
        )

    # --- Website interfaces (Python engines) ---
    if t in ("web_ui_status", "webui_status"):
        from pocket.web_ui_engine import status as wu_status

        return wu_status()
    if t in ("web_ui_open", "webui_open", "site_open"):
        from pocket.web_ui_engine import open_url

        return open_url(p.get("url") or p.get("text") or p.get("prompt") or "", profile=p.get("profile") or "Default")
    if t in ("web_ui_sense", "webui_sense", "site_sense"):
        from pocket.web_ui_engine import sense

        return sense(agent=p.get("agent") or "mcp")
    if t in ("web_ui_act", "webui_act", "site_act"):
        from pocket.web_ui_engine import act

        return act(
            p.get("action") or p.get("text") or "sense",
            agent=p.get("agent") or "mcp",
            **{k: v for k, v in p.items() if k not in ("action", "text", "agent", "prompt")},
        )
    if t in ("web_ui_fetch", "webui_fetch"):
        from pocket.web_ui_engine import fetch

        return fetch(p.get("url") or p.get("text") or p.get("prompt") or "", max_chars=int(p.get("max_chars") or 14000))
    if t in ("web_ui_search", "webui_search"):
        from pocket.web_ui_engine import search

        return search(p.get("query") or p.get("q") or p.get("text") or p.get("prompt") or "", max_results=int(p.get("max_results") or 6))
    if t in ("web_ui_browse", "webui_browse", "site_browse"):
        from pocket.web_ui_engine import browse

        return browse(p.get("url") or p.get("text") or p.get("prompt") or "", profile=p.get("profile") or "Default")

    # --- Models use Python agents / engines ---
    if t in ("python_engines_list", "list_python_engines", "engines_list"):
        from pocket.web_ui_engine import list_engines

        return list_engines()
    if t in ("python_engine", "run_engine", "engine_run"):
        from pocket.web_ui_engine import run_python_engine

        return run_python_engine(
            p.get("engine") or p.get("name") or p.get("id") or "web_research",
            p.get("prompt") or p.get("text") or p.get("goal") or "",
            params=p,
        )
    return {"ok": False, "error": f"unknown mail/web tool {tool}"}


def _invoke_pocket(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    t = tool
    # Agent mail + website UI + python engines first
    if t in (
        "mail_status", "mail_accounts", "mail_account_create",
        "mail_inbox", "mail_send", "mail_read", "mail_draft",
        "agent_mail_status", "agent_inbox", "agent_mail_send",
        "web_ui_open", "web_ui_sense", "web_ui_act", "web_ui_fetch",
        "web_ui_search", "web_ui_browse", "web_ui_status",
        "python_engine", "python_engines_list",
        "webui_open", "webui_sense", "webui_act", "site_open", "site_browse",
        "run_engine", "engines_list",
    ):
        return _invoke_mail_web(t, params)
    # Coherent platform tools (same as skills)
    if t in (
        "platform_map", "platform_health", "find_feature", "list_agents",
        "habitat_status", "habitat_open", "habitat_pulse", "habitat_assign",
        "screen_view", "screen_control", "screen_off",
        "fusion_voice", "fusion_schema", "fusion_last", "aria_turn", "voice_skills_list",
        "phone_surface", "pair_mint", "pair_status",
        "work_status",
        "sovereign_stack", "computing_clouds",
        "remote_browser_status", "remote_browser_open", "remote_browser_sense", "remote_browser_benchmark",
        "iot_status", "iot_list", "iot_register", "iot_phone", "iot_hz_status",
        "voice_studio_open",
        # Everyday life + host tools (all agents)
        "life_catalog", "life_status", "life_classify",
        "food_order", "flight_search", "shop_search", "web_browse", "reservation",
        "web_search", "web_fetch", "integrations_list", "integrations_execute",
        "integrations_readiness", "loomgraph_run", "loomgraph_catalog", "loomgraph_status",
        "loomgraph_mermaid", "assist_route",
        "list_skills", "wsl_status", "auro_status", "muse_status", "tools_for_prompt",
        "discord", "open_discord", "integration_run", "run_integration",
        "loomgraph", "graph_loop", "orchestrate_graph",
        "food", "flight", "flights", "shop", "buy", "browse", "reserve", "dining",
        "capsule_status", "capsule_list", "capsule_allocate", "capsule_execute",
        "capsule_commit", "capsule_terminate", "webgpu_probe",
        "capsule", "capsules", "webgpu",
        "studio_map", "studio_status", "studio_open", "studio_playbooks",
        "studio_storyboard", "studio_caption", "studio_list_recordings",
        "studio_list_exports", "studio_presets", "studio_record_start",
        "studio_record_stop", "studio_render", "studio_viral", "studio_batch",
        "studio_ship", "studio_auto", "viral_pack", "imagine_compose",
    ):
        from pocket.platform_coherence import run_platform_skill

        return run_platform_skill(t, prompt=params.get("text") or params.get("prompt") or params.get("url") or "", params=params)
    if t in ("screen_status", "screen"):
        from pocket.screen_share import status

        return status()
    if t in ("screen_set", "share"):
        from pocket.screen_share import set_share

        return set_share(
            mode=params.get("mode") or "",
            monitor=params.get("monitor"),
            vcomp=params.get("vcomp"),
        )
    if t in ("screen_sense", "sense"):
        from pocket.screen_share import fusion_context

        return fusion_context(agent=params.get("agent") or "mcp")
    if t in ("screen_act", "act"):
        from pocket.screen_share import act_for_agent

        return act_for_agent(
            params.get("action") or "sense",
            agent=params.get("agent") or "mcp",
            **{k: v for k, v in params.items() if k not in ("action", "agent")},
        )
    if t.startswith("vcomp") or t in ("open", "shell"):
        from pocket import virtual_computer as vc

        if t in ("vcomp_open", "open"):
            return vc.open_computer(label=params.get("label") or "mcp")
        if t in ("vcomp_sense",):
            return vc.sense_computer()
        if t in ("vcomp_act",):
            return vc.act(params.get("action") or "sense", **params)
        if t in ("vcomp_shell", "shell"):
            return vc.shell(params.get("command") or params.get("cmd") or "echo ok")
    if t.startswith("work_") or t in ("start", "tick", "package", "handoff"):
        from pocket.work_mode import (
            start_work,
            status as work_status,
            append_turn,
            package_session,
            handoff_artifacts,
            tick,
        )

        if t in ("work_start", "start"):
            return start_work(
                session_id=params.get("session_id") or "",
                voice=params.get("voice", True) is not False,
                screen=params.get("screen") or "control",
                chrome=params.get("chrome", True) is not False,
            )
        if t in ("work_tick", "tick"):
            return tick(params.get("session_id") or "")
        if t in ("work_package", "package"):
            return package_session(params.get("session_id") or "")
        if t in ("work_handoff", "handoff"):
            return handoff_artifacts(
                params.get("session_id") or "",
                kinds=params.get("kinds") or ["html", "md", "pixel"],
            )
        if t == "work_status":
            return work_status(params.get("session_id") or "")
        if t == "work_turn":
            return append_turn(
                params.get("session_id") or "",
                role=params.get("role") or "user",
                text=params.get("text") or "",
            )
    if t in ("draft_create",):
        from pocket.work_surface import create_draft

        return create_draft(
            title=params.get("title") or "MCP draft",
            kind=params.get("kind") or "html",
            content=params.get("content") or "",
            layer=params.get("layer") or "preview",
            source="mcp",
        )
    if t in ("draft_promote",):
        from pocket.work_surface import promote_draft

        return promote_draft(
            params.get("id") or "",
            target=params.get("target") or "folder",
            name=params.get("name") or "",
        )
    if t in ("cli_list",):
        from pocket.cli_tools import inventory

        return inventory()
    if t in ("cli_run", "run_cli"):
        from pocket.cli_tools import run_cli

        return run_cli(
            params.get("bin") or params.get("tool") or "",
            params.get("args") or [],
            cwd=params.get("cwd") or "",
            timeout=float(params.get("timeout") or 60),
        )
    return {"ok": False, "error": f"unknown pocket tool {tool}"}


def _invoke_github(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """GitHub for agents via `gh` CLI only — never opens a browser tab."""
    if not shutil.which("gh"):
        return {"ok": False, "error": "gh CLI not on PATH"}
    from pocket.github_hub import status, list_repos, list_issues, list_prs, create_pr
    from pocket.repos import clone_repo, create_github_repo

    if tool in ("status", "auth"):
        return status()
    if tool in ("repo_list", "repos", "list"):
        return list_repos(int(params.get("limit") or 15))
    if tool in ("issue_list", "issues"):
        return list_issues(int(params.get("limit") or 15), repo=params.get("repo") or "")
    if tool in ("pr_list", "prs"):
        return list_prs(int(params.get("limit") or 15), repo=params.get("repo") or "")
    if tool in ("pr_create", "create_pr"):
        return create_pr(
            params.get("title") or "POCKET update",
            body=params.get("body") or "",
            cwd=params.get("cwd") or "",
            repo=params.get("repo") or "",
        )
    if tool in ("clone",):
        return clone_repo(params.get("repo") or params.get("url") or "")
    if tool in ("create_repo",):
        return create_github_repo(params.get("name") or "pocket-app")
    if tool in ("api",):
        args = ["gh", "api", params.get("path") or "user"]
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=40)
            return {"ok": r.returncode == 0, "stdout": (r.stdout or "")[:4000], "stderr": (r.stderr or "")[:800]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    return {"ok": False, "error": f"unknown github tool {tool}"}


def grok_config_snippet() -> str:
    """TOML fragment to embed POCKET MCP into ~/.grok/config.toml."""
    pocket = Path(__file__).resolve().parents[2]  # pocket-os root-ish
    src = Path(__file__).resolve().parents[1]
    return f'''
# --- POCKET MCP (agent tools, no user tabs) ---
[mcp_servers.pocket]
command = "python"
args = ["-m", "pocket.mcp_server"]
enabled = true
startup_timeout_sec = 45

[mcp_servers.pocket.env]
PYTHONPATH = "{src}"
POCKET_MCP = "1"
'''
