"""Custom agent builder — Emergent-style specialized agents with tools + sub-agents.

Agents persist under ~/.pocket/custom_agents/ and register on the mesh.
They can be invoked from desk @mentions, build loops, and the phone app.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "custom_agents"
ROOT.mkdir(parents=True, exist_ok=True)
_lock = Lock()

TOOL_CATALOG = {
    "files": "Read/write workspace files (sandbox-gated)",
    "web": "Search and fetch URLs",
    "git": "Sovereign git / repo notes",
    "test": "Run pytest / npm test heuristics",
    "shell": "Host shell (founder only)",
    "wsl": "Native WSL Linux (founder only)",
    "desktop": "Open apps / capture (founder only)",
    "mesh": "Send mesh messages / leave artifacts",
    "deploy": "Static deploy helper",
    "plan": "Structured planning only",
    "voice": "Pocket Voice API (localhost, no host FS)",
}

# Tools that force a tighter sandbox profile
FOUNDER_ONLY_TOOLS = frozenset({"shell", "wsl", "desktop", "deploy"})


def _slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]+", "_", (name or "agent").strip()).strip("_").upper()
    return (s or "AGENT")[:32]


def _path(aid: str) -> Path:
    return ROOT / f"{aid.lower()}.json"


def list_agents() -> List[Dict[str, Any]]:
    out = []
    with _lock:
        for fp in sorted(ROOT.glob("*.json")):
            try:
                out.append(json.loads(fp.read_text(encoding="utf-8")))
            except Exception:
                continue
    return out


def get_agent(aid: str) -> Optional[Dict[str, Any]]:
    aid = _slug(aid)
    fp = _path(aid)
    if not fp.exists():
        return None
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return None


def create_agent(
    *,
    name: str,
    role: str = "",
    personality: str = "",
    tools: Optional[List[str]] = None,
    sub_agents: Optional[List[str]] = None,
    system: str = "",
    owner: str = "pocket",
) -> Dict[str, Any]:
    aid = _slug(name)
    tools = [t for t in (tools or ["files", "plan", "mesh"]) if t in TOOL_CATALOG]
    if not tools:
        tools = ["files", "plan"]
    sub_agents = [ _slug(s) for s in (sub_agents or []) ][:8]
    rec = {
        "id": aid,
        "name": name or aid,
        "role": (role or "specialist")[:200],
        "personality": (personality or "precise, helpful, ships real artifacts")[:500],
        "system": (system or "")[:4000],
        "tools": tools,
        "sub_agents": sub_agents,
        "owner": owner,
        "created_at": time.time(),
        "runs": 0,
        "last_at": 0,
        "status": "ready",
    }
    with _lock:
        _path(aid).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    try:
        from pocket.mesh_disk import ensure_agent

        ensure_agent(aid, role="custom")
    except Exception:
        pass
    return {"ok": True, **rec}


def delete_agent(aid: str) -> Dict[str, Any]:
    aid = _slug(aid)
    fp = _path(aid)
    if fp.exists():
        fp.unlink()
        return {"ok": True, "deleted": aid}
    return {"ok": False, "error": "not found"}


def _profile_for_tools(tools: set, *, is_founder: bool = True) -> str:
    """Map tool set → sandbox profile (least privilege)."""
    if tools & FOUNDER_ONLY_TOOLS:
        return "founder_tool" if is_founder else "market_seat"
    if "voice" in tools and not (tools & {"files", "web", "git", "mesh"}):
        return "voice_plugin"
    if "files" in tools or "plan" in tools or "git" in tools or "test" in tools:
        return "workspace_write"
    if "web" in tools:
        return "workspace_read"
    return "compute"


def run_custom_agent(
    aid: str,
    prompt: str,
    *,
    cwd: str = "",
    job: Optional[Dict] = None,
    is_founder: bool = True,
) -> Dict[str, Any]:
    """Execute one turn under capability sandbox (files/plan/web/voice gated)."""
    from pocket.agent_sandbox import mint_grant, safe_write_text, voice_turn

    agent = get_agent(aid)
    if not agent:
        return {"ok": False, "error": f"custom agent {aid} not found"}
    job = job or {}
    text = (prompt or "").strip()
    work = Path(cwd or job.get("cwd") or (Path.home() / ".pocket" / "workspaces" / "custom" / aid.lower()))
    work.mkdir(parents=True, exist_ok=True)
    steps: List[Dict[str, Any]] = []
    tools = set(agent.get("tools") or [])
    # Strip founder-only tools for market seats
    if not is_founder:
        tools = tools - FOUNDER_ONLY_TOOLS

    profile = _profile_for_tools(tools, is_founder=is_founder)
    grant = mint_grant(
        profile,
        workspace_path=str(work.resolve()),
        agent_id=agent.get("id") or aid,
        session_id=str(job.get("session_id") or job.get("id") or ""),
        net_hosts=["127.0.0.1", "localhost"] if "voice" in tools or "web" in tools else [],
    )
    # web needs net:http — expand grant caps for workspace_read when web present
    if "web" in tools:
        grant.caps.add("net:http")
        if "*" not in grant.net_hosts and not grant.net_hosts:
            grant.net_hosts = ["*"]  # web search; still audited via steps

    # 1) write brief (sandbox write)
    if "files" in tools or "plan" in tools:
        brief = work / f"brief_{int(time.time())}.md"
        body = (
            f"# {agent.get('name')} run\n\n"
            f"**Role:** {agent.get('role')}\n"
            f"**Personality:** {agent.get('personality')}\n"
            f"**Sandbox profile:** {profile}\n\n"
            f"## Task\n{text}\n\n"
            f"## System\n{agent.get('system') or '(default)'}\n"
        )
        wr = safe_write_text(grant, str(brief), body)
        steps.append(
            {
                "tool": "files",
                "ok": bool(wr.get("ok")),
                "path": str(brief),
                "trap": wr.get("trap"),
                "receipt": (wr.get("receipt") or {}).get("id"),
            }
        )

    # 2) plan skeleton
    plan_path = work / "PLAN.md"
    plan_body = (
        f"# Plan — {agent.get('id')}\n\n"
        f"1. Understand: {text[:400]}\n"
        f"2. Tools: {', '.join(sorted(tools))}\n"
        f"3. Sandbox: `{profile}` · caps `{', '.join(sorted(grant.caps))}`\n"
        f"4. Sub-agents: {', '.join(agent.get('sub_agents') or []) or 'none'}\n"
        f"5. Deliver artifact under `{work}`\n"
        f"6. Report status\n"
    )
    wrp = safe_write_text(grant, str(plan_path), plan_body)
    steps.append(
        {
            "tool": "plan",
            "ok": bool(wrp.get("ok")),
            "path": str(plan_path),
            "trap": wrp.get("trap"),
            "receipt": (wrp.get("receipt") or {}).get("id"),
        }
    )

    # 3) optional web research note
    if "web" in tools and any(k in text.lower() for k in ("research", "lookup", "search", "find")):
        try:
            from pocket.web_research import search_web

            sr = search_web(text[:200])
            wr = safe_write_text(grant, str(work / "research.json"), json.dumps(sr, indent=2)[:12000])
            steps.append({"tool": "web", "ok": bool(wr.get("ok")), "trap": wr.get("trap")})
        except Exception as e:
            steps.append({"tool": "web", "ok": False, "error": str(e)[:200]})

    # 3b) voice (Pocket Voice API) when tool present and prompt looks spoken/support
    if "voice" in tools and any(
        k in text.lower() for k in ("say ", "speak", "voice", "call", "support", "customer", "refund", "hello")
    ):
        vg = mint_grant(
            "voice_plugin",
            agent_id=agent.get("id") or aid,
            session_id=str(job.get("session_id") or ""),
            net_hosts=["127.0.0.1", "localhost"],
        )
        vr = voice_turn(
            vg,
            text[:500],
            business_mode="customer_service",
            session_id=str(job.get("session_id") or agent.get("id") or "custom"),
        )
        steps.append(
            {
                "tool": "voice",
                "ok": bool(vr.get("ok")),
                "trap": vr.get("trap"),
                "reply": ((vr.get("result") or {}).get("reply") if isinstance(vr.get("result"), dict) else None),
            }
        )

    # 4) mesh artifact
    if "mesh" in tools:
        try:
            from pocket.mesh_disk import leave_artifact

            leave_artifact(
                agent["id"],
                f"custom_{int(time.time())}.md",
                f"# {agent['id']}\n\nprofile={profile}\n\n{text[:2000]}\n",
                notify=["ARCHON"],
            )
            steps.append({"tool": "mesh", "ok": True})
        except Exception as e:
            steps.append({"tool": "mesh", "ok": False, "error": str(e)[:120]})

    # 5) fan-out sub-agents
    sub_results = []
    for sub in (agent.get("sub_agents") or [])[:4]:
        try:
            from pocket.subagent_dispatch import dispatch

            r = dispatch(f"@{sub} assist for: {text[:300]}", from_agent=agent["id"], agents=[sub])
            sub_results.append({"agent": sub, "ok": r.get("ok")})
        except Exception as e:
            sub_results.append({"agent": sub, "ok": False, "error": str(e)[:120]})

    # 6) deliverable stub code if backend-ish role
    role = (agent.get("role") or "").lower()
    if any(x in role for x in ("code", "backend", "frontend", "build", "engineer")):
        src = work / "main.py"
        if not src.exists():
            code = (
                f'"""Generated by custom agent {agent["id"]} (sandbox={profile})"""\n'
                f"def main():\n"
                f"    print({text[:80]!r})\n"
                f"\n"
                f"if __name__ == '__main__':\n"
                f"    main()\n"
            )
            wr = safe_write_text(grant, str(src), code)
            steps.append({"tool": "files", "ok": bool(wr.get("ok")), "path": str(src), "trap": wr.get("trap")})

    agent["runs"] = int(agent.get("runs") or 0) + 1
    agent["last_at"] = time.time()
    agent["last_profile"] = profile
    with _lock:
        _path(agent["id"]).write_text(json.dumps(agent, indent=2), encoding="utf-8")

    denied = [s for s in steps if s.get("trap")]
    summary = (
        f"## {agent.get('name')} complete\n\n"
        f"- Sandbox profile: `{profile}`\n"
        f"- Caps: {', '.join(sorted(grant.caps))}\n"
        f"- Steps: {len(steps)}"
        + (f" · denied: {len(denied)}" if denied else "")
        + f"\n- Workspace: `{work}`\n"
        f"- Sub-agents: {sub_results}\n"
        f"- Tools used: {[s.get('tool') for s in steps]}\n"
    )
    return {
        "ok": True,
        "agent": agent["id"],
        "workspace": str(work),
        "sandbox_profile": profile,
        "caps": sorted(grant.caps),
        "steps": steps,
        "sub_agents": sub_results,
        "summary": summary,
        "engine": f"custom:{agent['id']}",
    }


def tools_catalog() -> Dict[str, Any]:
    return {"ok": True, "tools": TOOL_CATALOG}
