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
            "eyes_see", "eyes_touch", "eyes_catalog",
            "screen_embody", "screen_see", "screen_touch", "screen_type", "screen_click", "screen_cursor",
            "team_open", "team_list", "team_note", "team_invite", "team_tick", "team_bind", "team_status",
            "endure_run", "endure_status", "endure_enqueue",
            "runtime_status", "runtime_ensure", "runtime_install",
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
            "agent_people", "agent_dm", "agent_group_post", "agent_email",
            "subagent_steer", "cron_memory", "browser_drive",
            # Website interfaces via Python engines
            "web_ui_open", "web_ui_sense", "web_ui_act", "web_ui_fetch",
            "web_ui_search", "web_ui_browse", "web_ui_drive", "web_ui_status",
            "webmcp_scan", "webmcp_list", "webmcp_use", "webmcp_find",
            # Models → Python agents / engines
            "python_engine", "python_engines_list",
            "engine_uses", "engine_use",
            "model_build", "model_list_built", "model_register", "model_suggest",
            # Comprehensive agent toolkit
            "agents_toolkit", "agents_tools", "tools_manifest",
            "agent_arch", "agent_turn", "agent_invoke", "agent_roster", "autonomous_status", "autonomous_ensure",
            "keep_start", "keep_status", "keep_stop",
            "kernel_status", "kernel_calibrate", "kernel_slab", "cognitive_loop",
            "workflow_start", "workflow_tick", "workflow_status", "workflow_stop",
            "multi_plan",
            # Live MCP JSON-RPC protocol stream
            "mcp_stream",
            # Agent virtual numbers + softphone
            "call_status", "call_numbers", "call_assign",
            "call_dial", "call_answer", "call_hangup", "call_speak", "call_list",
            "multi_workflows", "multi_workflow_run", "multi_workflow_get", "multi_workflow_families",
            "power_do", "power_pulse", "power_vs", "power_recall",
            "go", "go_state", "go_tick",
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

_PACK_ATTACHED = False


def _attach_pack_tools() -> None:
    global _PACK_ATTACHED
    if _PACK_ATTACHED:
        return
    try:
        from pocket.mcp_fifty import ids

        pocket = next(s for s in INTERNAL_MCPS if s["id"] == "pocket")
        have = set(pocket["tools"])
        for i in ids():
            if i not in have:
                pocket["tools"].append(i)
        _PACK_ATTACHED = True
    except Exception:
        pass


def catalog() -> Dict[str, Any]:
    _attach_pack_tools()
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
    _attach_pack_tools()
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

    # Live JSON-RPC protocol stream (internal invoke channel)
    try:
        from pocket.mcp_stream import emit_frame

        emit_frame(
            direction="in",
            method=f"tools/call:{sid}.{tool}",
            payload={"server": sid, "tool": tool, "params": params},
            channel="invoke",
        )
    except Exception:
        pass

    result: Dict[str, Any]

    # --- pocket internal ---
    if sid in ("pocket", "pocket-core"):
        result = _invoke_pocket(tool, params)

    # --- universal 50-tool pack (any agent, any desk) ---
    elif sid in ("universal", "pocket-universal", "u", "fifty"):
        from pocket.mcp_fifty import run as run_fifty

        result = run_fifty(tool, params)

    # --- github via gh CLI (no browser tab) ---
    elif sid == "github":
        result = _invoke_github(tool, params)

    # --- filesystem ---
    elif sid == "filesystem":
        if tool in ("fs_list", "list"):
            result = fs_list(params.get("path") or "", int(params.get("limit") or 40))
        elif tool in ("fs_read", "read"):
            result = fs_read(params.get("path") or "", int(params.get("max_chars") or 12000))
        elif tool in ("fs_write", "write"):
            result = fs_write(params.get("path") or "", params.get("content") or "")
        elif tool == "fs_stat":
            p = Path(params.get("path") or "").expanduser()
            if not p.exists():
                result = {"ok": False, "error": "missing"}
            else:
                st = p.stat()
                result = {"ok": True, "path": str(p), "bytes": st.st_size, "dir": p.is_dir()}
        else:
            result = {"ok": False, "error": f"unknown filesystem tool {tool}"}

    # --- nexus bridge if present ---
    elif sid == "nexus":
        try:
            from pocket import nexus_bridge as nb

            if hasattr(nb, "run_nexus"):
                result = nb.run_nexus(params.get("prompt") or tool, job={})
            elif hasattr(nb, "status"):
                result = {"ok": True, "status": nb.status(), "tool": tool, "params": params}
            else:
                result = {"ok": True, "module": "nexus_bridge", "tool": tool, "note": "use NEXUS desk agent for full runs"}
        except Exception as e:
            result = {"ok": False, "error": f"nexus: {e}", "hint": "ensure NEXUS on host"}

    # --- loom catalog hint ---
    elif sid == "loom":
        cat = Path(r"C:\Users\Medin\OneDrive\mcps\loom\tools")
        tools = [p.stem for p in cat.glob("*.json")][:40] if cat.is_dir() else []
        result = {
            "ok": True,
            "server": "loom",
            "tool": tool,
            "note": "LOOM tools catalog on disk — wire live stdio when loom server is running",
            "available_tools": tools,
            "params": params,
        }

    else:
        # --- remote HTTP MCP (document only — live session uses grok config) ---
        result = {"ok": False, "error": f"unknown server/tool {sid}.{tool}", "catalog": catalog()["servers"]}
        for s in EXTERNAL_MCPS:
            if s["id"] == sid and s.get("transport") == "http":
                result = {
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
                break

    if not isinstance(result, dict):
        result = {"ok": True, "result": result}

    try:
        from pocket.mcp_stream import emit_frame

        emit_frame(
            direction="out",
            method=f"tools/call:{sid}.{tool}",
            payload=result,
            error=None if result.get("ok", True) else result.get("error"),
            channel="invoke",
        )
    except Exception:
        pass

    return result


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
    if t in ("web_ui_drive", "browser_drive", "drive_browser"):
        from pocket.web_ui_engine import drive as browser_drive

        return browser_drive(
            p.get("url") or "",
            goal=p.get("goal") or p.get("prompt") or p.get("text") or "",
            steps=p.get("steps") if isinstance(p.get("steps"), list) else None,
            profile=p.get("profile") or "Default",
        )
    if t in ("agent_people", "agent_faces", "agent_social"):
        from pocket.agent_social import list_people, status as social_status

        if t == "agent_social":
            return social_status()
        return list_people()
    if t in ("agent_dm",):
        from pocket.agent_social import dm

        return dm(
            p.get("from") or p.get("from_agent") or "system",
            p.get("to") or p.get("agent") or "",
            p.get("text") or p.get("body") or p.get("prompt") or "",
            also_email=bool(p.get("email")),
        )
    if t in ("agent_email",):
        from pocket.agent_social import email_agents

        return email_agents(
            p.get("from") or p.get("from_agent") or "scribe",
            p.get("to") or "",
            subject=p.get("subject") or "",
            body=p.get("body") or p.get("text") or p.get("prompt") or "",
        )
    if t in ("agent_group_post",):
        from pocket.agent_social import group_post

        return group_post(
            p.get("group") or p.get("id") or "",
            p.get("from") or p.get("from_agent") or "system",
            p.get("text") or p.get("body") or p.get("prompt") or "",
        )
    if t in ("subagent_steer", "steer_subagent"):
        from pocket.subagent_dispatch import steer

        return steer(
            p.get("instruction") or p.get("text") or p.get("prompt") or "",
            run_id=p.get("run_id") or p.get("id") or "",
            agent=p.get("agent") or p.get("name") or "",
        )
    if t in ("cron_memory", "autonomy_memory"):
        from pocket.autonomy import last_week, yesterday

        days = str(p.get("days") or "1")
        sid = p.get("id") or p.get("schedule") or ""
        return last_week(sid) if days in ("7", "week") else yesterday(sid)

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
    if t in ("engine_uses", "list_engine_uses", "web_ui_uses"):
        from pocket.web_ui_engine import list_uses

        return list_uses()
    if t in ("webmcp_scan", "webmcp_diffuse"):
        from pocket.webmcp import scan

        return scan(url=p.get("url") or "", fusion=bool(p.get("fusion") or p.get("screen")))
    if t in ("webmcp_list", "webmcp_catalog"):
        from pocket.webmcp import catalog

        return catalog(refresh=bool(p.get("refresh")))
    if t in ("webmcp_find",):
        from pocket.webmcp import find_actions

        return {"ok": True, "hits": find_actions(p.get("q") or p.get("query") or p.get("name") or "")}
    if t in ("webmcp_use", "webmcp_act"):
        from pocket.webmcp import use_action

        return use_action(p.get("name") or p.get("id") or p.get("action") or "", prompt=p.get("prompt") or p.get("text") or "")
    if t in ("engine_use", "run_engine_use"):
        from pocket.web_ui_engine import run_use, pick_use

        uid = p.get("use") or p.get("use_id") or p.get("id") or ""
        prompt = p.get("prompt") or p.get("text") or p.get("goal") or ""
        if not uid and prompt:
            return pick_use(prompt)
        return run_use(uid, prompt, params=p)
    if t in ("model_build", "build_model", "forge_model"):
        from pocket.model_forge import build_model

        return build_model(
            model_id=str(p.get("model_id") or p.get("id") or ""),
            name=str(p.get("name") or ""),
            kind=str(p.get("kind") or "template"),
            description=str(p.get("description") or p.get("text") or p.get("prompt") or ""),
            tags=p.get("tags") if isinstance(p.get("tags"), list) else None,
            template=str(p.get("template") or ""),
            rules=p.get("rules") if isinstance(p.get("rules"), list) else None,
            default=str(p.get("default") or ""),
            formula=str(p.get("formula") or ""),
            wrap_engine=str(p.get("wrap_engine") or ""),
            wrap_params=p.get("wrap_params") if isinstance(p.get("wrap_params"), dict) else None,
            code=str(p.get("code") or ""),
            system=str(p.get("system") or ""),
            fit_keywords=p.get("fit_keywords") if isinstance(p.get("fit_keywords"), list) else None,
            register_now=p.get("register_now", True) is not False,
            author=str(p.get("author") or "agent"),
        )
    if t in ("model_list_built", "list_built_models", "models_built"):
        from pocket.model_forge import list_built

        return list_built(limit=int(p.get("limit") or 50))
    if t in ("model_register", "register_models"):
        from pocket.model_forge import register_built

        return register_built(str(p.get("model") or p.get("model_id") or p.get("id") or ""))
    if t in ("model_suggest", "suggest_model"):
        from pocket.model_forge import suggest_from_goal

        return suggest_from_goal(p.get("goal") or p.get("prompt") or p.get("text") or "")
    if t in ("agents_toolkit", "agents_tools", "tools_manifest", "agent_tools"):
        from pocket.agents_toolkit import manifest, markdown, write_docs_file

        fmt = (p.get("format") or p.get("fmt") or "json").lower()
        if fmt in ("md", "markdown"):
            return {"ok": True, "format": "markdown", "markdown": markdown()}
        if fmt in ("write", "file", "docs"):
            return write_docs_file()
        return manifest()
    if t in ("multi_plan", "multiplan", "plan_exec", "agentic_plan"):
        from pocket.multi_plan import run_multi_plan

        return run_multi_plan(
            p.get("prompt") or p.get("goal") or p.get("text") or "",
            job_id=str(p.get("job_id") or ""),
            session_id=str(p.get("session_id") or ""),
            max_tasks=int(p.get("max_tasks") or 24),
        )
    if t in ("mcp_stream", "mcp_rpc_stream", "protocol_stream", "jsonrpc_stream"):
        from pocket.mcp_stream import list_frames, snapshot, format_term_view, clear as mcp_clear

        action = str(p.get("action") or p.get("mode") or "").lower()
        if action in ("clear", "reset"):
            return mcp_clear()
        after = int(p.get("after") or p.get("seq") or 0)
        limit = int(p.get("limit") or 50)
        fmt = str(p.get("format") or p.get("fmt") or "json").lower()
        if fmt in ("term", "markdown", "md"):
            return {"ok": True, "format": "term", "markdown": format_term_view(after_seq=after, limit=limit)}
        return {"ok": True, **snapshot(), "frames": list_frames(after_seq=after, limit=limit)}
    if t in ("call_status", "calls_status"):
        from pocket.agent_calls import status as calls_status

        return calls_status()
    if t in ("call_numbers", "list_call_numbers"):
        from pocket.agent_calls import list_numbers

        return list_numbers()
    if t in ("call_assign", "assign_number"):
        from pocket.agent_calls import assign_number

        return assign_number(
            str(p.get("agent") or p.get("agent_id") or p.get("id") or ""),
            name=str(p.get("name") or ""),
            area=str(p.get("area") or "201"),
            line=str(p.get("line") or ""),
        )
    if t in ("call_dial", "dial", "phone_call"):
        from pocket.agent_calls import dial

        return dial(
            from_agent=str(p.get("from") or p.get("from_agent") or p.get("agent") or "phone_agent"),
            to=str(p.get("to") or p.get("number") or ""),
            purpose=str(p.get("purpose") or p.get("reason") or p.get("prompt") or p.get("text") or ""),
            text=str(p.get("text") or ""),
            mode=str(p.get("mode") or "soft"),
            session_id=str(p.get("session_id") or ""),
        )
    if t in ("call_answer",):
        from pocket.agent_calls import answer

        return answer(str(p.get("id") or p.get("call_id") or ""), by=str(p.get("by") or "agent"))
    if t in ("call_hangup",):
        from pocket.agent_calls import hangup

        return hangup(str(p.get("id") or p.get("call_id") or ""), reason=str(p.get("reason") or "hangup"))
    if t in ("call_speak",):
        from pocket.agent_calls import speak

        return speak(
            str(p.get("id") or p.get("call_id") or ""),
            str(p.get("text") or p.get("message") or ""),
            role=str(p.get("role") or "agent"),
        )
    if t in ("call_list", "list_calls"):
        from pocket.agent_calls import list_calls

        return list_calls(status=str(p.get("status") or ""), limit=int(p.get("limit") or 30))
    if t in ("agent_arch", "agent_architecture"):
        from pocket.agent_arch import snapshot as arch_snap

        return arch_snap()
    if t in ("agent_turn", "arch_turn"):
        from pocket.agent_arch import turn as arch_turn

        return arch_turn(
            str(p.get("prompt") or p.get("text") or p.get("goal") or ""),
            agent=str(p.get("agent") or p.get("name") or p.get("persona") or ""),
            seat=str(p.get("seat") or "pocket"),
            engine=str(p.get("engine") or "auto"),
            grant_id=str(p.get("grant_id") or p.get("grant") or ""),
            shell=str(p.get("shell") or p.get("command") or ""),
            cwd=str(p.get("cwd") or ""),
            use=str(p.get("use") or "auto"),
        )
    if t in ("agent_roster",):
        from pocket.agent_invoke import roster

        return roster()
    if t in ("agent_invoke",):
        from pocket.agent_invoke import invoke

        return invoke(
            str(p.get("name") or p.get("agent") or p.get("id") or ""),
            prompt=str(p.get("prompt") or p.get("text") or p.get("message") or ""),
            job=str(p.get("job") or p.get("action") or ""),
            session_id=str(p.get("session_id") or ""),
            params=p,
        )
    return {"ok": False, "error": f"unknown mail/web tool {tool}"}


def _invoke_pocket(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    t = tool
    if t in ("multi_workflows", "multi_workflow_run", "multi_workflow_get", "multi_workflow_families"):
        from pocket.multi_workflows import catalog as mw_cat, families as mw_fam, get as mw_get, run as mw_run

        if t in ("multi_workflows",):
            return mw_cat(family=params.get("family") or params.get("name") or "")
        if t == "multi_workflow_families":
            return mw_fam()
        if t == "multi_workflow_get":
            return mw_get(params.get("name") or params.get("id") or params.get("text") or "")
        return mw_run(
            params.get("name") or params.get("id") or params.get("text") or "mw001_stack_health",
            dry=bool(params.get("dry")),
            params=params,
        )
    if t in ("power_do", "power_pulse", "power_vs", "power_recall"):
        from pocket.power import do as power_do, pulse as power_pulse, recall as power_recall, vs_theirs

        if t == "power_pulse":
            return power_pulse()
        if t == "power_vs":
            return vs_theirs()
        if t == "power_recall":
            return power_recall(int(params.get("limit") or 8))
        return power_do(
            params.get("goal") or params.get("text") or params.get("prompt") or "",
            dry=bool(params.get("dry")),
            workflow_id=str(params.get("name") or params.get("id") or params.get("workflow_id") or ""),
        )
    if t in ("go", "go_state", "go_tick"):
        from pocket.go_plane import go as go_start, snapshot as go_snap, tick as go_tick

        if t == "go_state":
            return go_snap()
        if t == "go_tick":
            return go_tick()
        return go_start(
            arm_daily=params.get("arm_daily", True) is not False,
            run_morning=bool(params.get("morning") or params.get("text") == "morning"),
        )
    try:
        from pocket.mcp_fifty import known, run as run_fifty

        if known(t):
            return run_fifty(t, params)
    except Exception:
        pass
    # Agent mail + website UI + python engines first
    if t in (
        "mail_status", "mail_accounts", "mail_account_create",
        "mail_inbox", "mail_send", "mail_read", "mail_draft",
        "agent_mail_status", "agent_inbox", "agent_mail_send",
        "web_ui_open", "web_ui_sense", "web_ui_act", "web_ui_fetch",
        "web_ui_search", "web_ui_browse", "web_ui_drive", "web_ui_status",
        "agent_people", "agent_dm", "agent_group_post", "agent_email", "agent_social",
        "subagent_steer", "cron_memory", "browser_drive",
        "python_engine", "python_engines_list",
        "engine_uses", "engine_use", "list_engine_uses",
        "model_build", "model_list_built", "model_register", "model_suggest",
        "build_model", "forge_model",
        "agents_toolkit", "agents_tools", "tools_manifest",
        "agent_arch", "agent_turn",
        "agent_invoke", "agent_roster", "autonomous_status", "autonomous_ensure",
        "keep_start", "keep_status", "keep_stop",
        "kernel_status", "kernel_calibrate", "kernel_slab", "cognitive_loop",
        "workflow_start", "workflow_tick", "workflow_status", "workflow_stop",
        "multi_plan", "multiplan", "plan_exec", "agentic_plan",
        "mcp_stream", "mcp_rpc_stream", "protocol_stream", "jsonrpc_stream",
        "call_status", "call_numbers", "call_assign",
        "call_dial", "call_answer", "call_hangup", "call_speak", "call_list",
        "webui_open", "webui_sense", "webui_act", "site_open", "site_browse",
        "run_engine", "engines_list",
    ):
        return _invoke_mail_web(t, params)
    # Coherent platform tools (same as skills)
    if t in (
        "platform_map", "platform_health", "find_feature", "list_agents",
        "agent_arch", "agent_turn",
        "agent_invoke", "agent_roster", "autonomous_status", "autonomous_ensure",
        "keep_start", "keep_status", "keep_stop",
        "kernel_status", "kernel_calibrate", "kernel_slab", "cognitive_loop",
        "workflow_start", "workflow_tick", "workflow_status", "workflow_stop",
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
            target=params.get("target") or "",
            window_title=params.get("window_title") or params.get("title") or "",
            window_hwnd=params.get("window_hwnd") or params.get("hwnd"),
            label=params.get("label") or params.get("name") or "",
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
    if t in ("runtime_status", "runtime_ensure", "runtime_install"):
        from pocket import host_runtime as hr

        if t == "runtime_status":
            return hr.status()
        if t == "runtime_install":
            return hr.install()
        return hr.ensure(str(params.get("which") or params.get("id") or "all"))
    if t in ("eyes_see", "eyes_touch", "eyes_catalog"):
        from pocket.agent_eyes import act as eyes_act, catalog as eyes_cat, see as eyes_see

        if t == "eyes_catalog":
            return eyes_cat()
        if t == "eyes_see":
            return eyes_see(which=str(params.get("which") or "portal"))
        return eyes_act(
            str(params.get("kind") or "tap"),
            which=str(params.get("which") or "portal"),
            nx=float(params.get("nx") or 0.5),
            ny=float(params.get("ny") or 0.5),
            text=str(params.get("text") or ""),
        )
    from pocket.mcp_dispatch import dispatch as gate_dispatch, handles as gate_handles

    if gate_handles(t):
        return gate_dispatch(t, params)
    if t in ("screen_embody", "screen_see", "screen_touch", "screen_type", "screen_click", "screen_cursor", "screen_body"):
        from pocket.screen_body import act as body_act, inhabit

        if t == "screen_embody":
            return inhabit(str(params.get("agent") or params.get("name") or "coder"), which=str(params.get("which") or "desktop"))
        if t == "screen_cursor":
            return body_act("cursor", agent=str(params.get("agent") or ""))
        verb = {
            "screen_see": "see",
            "screen_touch": "touch",
            "screen_type": "type_into",
            "screen_click": "click_name",
            "screen_body": str(params.get("verb") or "see"),
        }.get(t, "see")
        return body_act(
            verb,
            agent=str(params.get("agent") or ""),
            which=str(params.get("which") or ""),
            nx=float(params.get("nx") or 0.5),
            ny=float(params.get("ny") or 0.5),
            text=str(params.get("text") or ""),
            name=str(params.get("name") or ""),
            kind=str(params.get("kind") or "tap"),
            submit=bool(params.get("submit")),
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
