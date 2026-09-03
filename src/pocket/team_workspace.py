"""Persistent team workspace for long work — founder, tenant-jailed.

Root: ~/.pocket/tenants/<principal>/teams/<safe-id>/
IDs are [a-z0-9][a-z0-9_-]{0,31}. Canonicalized paths must stay under that root.
Market seats cannot open these routes (RBAC /v1/team).
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.team.workspace.v1"
PROTOCOL = "POCKET-TEAM-WORKSPACE/1.0"
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
SAFE_PRINCIPAL = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
DEFAULT_AGENTS = ("codex", "grok", "coder")


def _principal(raw: str) -> str:
    p = (raw or "").strip().lower()
    if not p or not SAFE_PRINCIPAL.match(p) or ".." in p or "/" in p or "\\" in p:
        raise ValueError("invalid principal")
    return p


def owner_from_user(user: Optional[Dict[str, Any]] = None) -> str:
    """Filesystem-safe tenant id bound to an authenticated principal."""
    raw = ""
    if user:
        raw = str(user.get("user") or "")
    s = re.sub(r"[^a-z0-9._-]+", "-", (raw or "").strip().lower()).strip("-.")[:64]
    if s in ("", "anonymous", "none", "market"):
        raise ValueError("unauthenticated principal")
    if not SAFE_PRINCIPAL.match(s) or ".." in s:
        raise ValueError("invalid principal")
    return s


def tenant_root(principal: str) -> Path:
    who = _principal(principal)
    return (Path.home() / ".pocket" / "tenants" / who / "teams").resolve()


def _safe_id(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not SAFE_ID.match(s) or ".." in s or "/" in s or "\\" in s:
        raise ValueError("invalid team id")
    return s


def _jail(root: Path, child: Path) -> Path:
    r = root.resolve()
    c = child.resolve()
    c.relative_to(r)
    return c


def _dir(tid: str, principal: str) -> Path:
    root = tenant_root(principal)
    return _jail(root, root / _safe_id(tid))


def _meta(tid: str, principal: str) -> Path:
    return _dir(tid, principal) / "TEAM.json"


def _load(tid: str, principal: str) -> Optional[Dict[str, Any]]:
    try:
        p = _meta(tid, principal)
    except ValueError:
        return None
    if not p.is_file():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if str(rec.get("owner") or "") != _principal(principal):
        return None
    return rec


def _save(rec: Dict[str, Any]) -> None:
    owner = _principal(str(rec.get("owner") or ""))
    tid = _safe_id(str(rec.get("id") or ""))
    rec["updated_at"] = time.time()
    rec["owner"] = owner
    d = _dir(tid, owner)
    (d / "workspace").mkdir(parents=True, exist_ok=True)
    (d / "receipts").mkdir(parents=True, exist_ok=True)
    (d / "seats").mkdir(parents=True, exist_ok=True)
    rec["cwd"] = str(_jail(d, d / "workspace"))
    _meta(tid, owner).write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")


def _seed(cwd: Path, goal: str, engines: List[str]) -> None:
    cwd.mkdir(parents=True, exist_ok=True)
    readme = cwd / "README.md"
    if not readme.is_file():
        readme.write_text(
            f"# Team workspace\n\nGoal: {goal}\n\nEngines: {', '.join(engines)}\n"
            "Founder-owned. Survives chat. KEEP does not.\n",
            encoding="utf-8",
        )
    notes = cwd / "NOTES.md"
    if not notes.is_file():
        notes.write_text(f"# Notes\n\n- opened {time.strftime('%Y-%m-%d %H:%M')}\n", encoding="utf-8")
    inbox = cwd / "INBOX.md"
    if not inbox.is_file():
        inbox.write_text("# Team inbox\n\nAgents leave handoffs here.\n", encoding="utf-8")


def _engines() -> List[str]:
    out: List[str] = []
    try:
        from pocket.executor import which_codex, which_grok_cli

        if which_codex():
            out.append("codex")
        if which_grok_cli():
            out.append("grok")
    except Exception:
        pass
    return out or ["grok"]


def open_team(
    goal: str = "",
    *,
    team_id: str = "",
    agents: Optional[List[str]] = None,
    engines: Optional[List[str]] = None,
    label: str = "",
    principal: str = "",
) -> Dict[str, Any]:
    try:
        owner = _principal(principal)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    tenant_root(owner).mkdir(parents=True, exist_ok=True)
    tid = (team_id or "").strip().lower()
    if tid:
        try:
            _safe_id(tid)
        except ValueError:
            return {"ok": False, "error": "invalid team id"}
        rec = _load(tid, owner)
        if rec:
            rec["goal"] = (goal or rec.get("goal") or "")[:4000]
            if agents:
                rec["agents"] = list(dict.fromkeys(list(rec.get("agents") or []) + list(agents)))
            rec["status"] = "open"
            _save(rec)
            return get(tid, principal=owner)
    else:
        tid = "team-" + uuid.uuid4().hex[:10]
    eng = list(engines or _engines())
    ag = list(dict.fromkeys(list(agents or DEFAULT_AGENTS) + eng))
    rec = {
        "id": tid,
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "owner": owner,
        "status": "open",
        "label": (label or (goal or "long work")[:48])[:80],
        "goal": (goal or "long-running team work").strip()[:4000],
        "agents": ag,
        "engines": eng,
        "workflows": [],
        "created_at": time.time(),
        "updated_at": time.time(),
    }
    _save(rec)
    _seed(Path(rec["cwd"]), rec["goal"], eng)
    return get(tid, principal=owner)


def get(tid: str, *, principal: str = "") -> Dict[str, Any]:
    try:
        owner = _principal(principal)
        rec = _load(tid, owner)
    except ValueError as e:
        return {"ok": False, "error": str(e), "id": tid}
    if not rec:
        return {"ok": False, "error": "unknown team", "id": tid}
    cwd = Path(rec.get("cwd") or "")
    try:
        cwd = _jail(_dir(tid, owner), cwd if cwd.parts else (_dir(tid, owner) / "workspace"))
    except ValueError:
        return {"ok": False, "error": "escaped cwd", "id": tid}
    rec["ok"] = True
    rec["cwd"] = str(cwd)
    rec["exists"] = cwd.is_dir()
    rec["files"] = sorted(p.name for p in cwd.iterdir())[:40] if cwd.is_dir() else []
    return rec


def list_teams(*, principal: str = "") -> Dict[str, Any]:
    try:
        root = tenant_root(principal)
    except ValueError as e:
        return {"ok": False, "error": str(e), "teams": [], "count": 0}
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    owner = _principal(principal)
    for p in root.glob("*/TEAM.json"):
        try:
            _jail(root, p.parent)
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if str(rec.get("owner") or "") != owner:
            continue
        rows.append(
            {
                "id": rec.get("id"),
                "label": rec.get("label"),
                "goal": (rec.get("goal") or "")[:120],
                "status": rec.get("status"),
                "owner": rec.get("owner"),
                "agents": rec.get("agents") or [],
                "cwd": rec.get("cwd"),
                "updated_at": rec.get("updated_at"),
            }
        )
    rows.sort(key=lambda r: float(r.get("updated_at") or 0), reverse=True)
    return {"ok": True, "schema": SCHEMA, "count": len(rows), "owner": owner, "teams": rows}


def invite(tid: str, agent: str, *, principal: str = "") -> Dict[str, Any]:
    rec = _load(tid, principal)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    a = (agent or "").strip()[:40]
    if not a or "/" in a or "\\" in a or ".." in a:
        return {"ok": False, "error": "invalid agent"}
    rec.setdefault("agents", [])
    if a not in rec["agents"]:
        rec["agents"].append(a)
    seat = _dir(tid, principal) / "seats" / (re.sub(r"[^a-zA-Z0-9._-]+", "-", a)[:40] + ".md")
    try:
        seat = _jail(_dir(tid, principal) / "seats", seat)
    except ValueError:
        return {"ok": False, "error": "escaped seat"}
    seat.parent.mkdir(parents=True, exist_ok=True)
    if not seat.is_file():
        seat.write_text(f"# Seat {a}\n\nowner={principal}\nJoined {time.strftime('%Y-%m-%d %H:%M')}\n", encoding="utf-8")
    _save(rec)
    return get(tid, principal=principal)


def note(tid: str, text: str, *, agent: str = "team", principal: str = "") -> Dict[str, Any]:
    rec = _load(tid, principal)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    line = f"- {time.strftime('%H:%M')} @{agent}: {(text or '').strip()[:400]}\n"
    p = Path(rec["cwd"]) / "NOTES.md"
    try:
        p = _jail(Path(rec["cwd"]), p)
    except ValueError:
        return {"ok": False, "error": "escaped notes"}
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    rec["last_note"] = line.strip()
    _save(rec)
    return {"ok": True, "id": tid, "note": line.strip(), "cwd": rec["cwd"]}


def receipt(tid: str, body: Dict[str, Any], *, principal: str = "") -> Path:
    d = _dir(tid, principal) / "receipts"
    d = _jail(_dir(tid, principal), d)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{int(time.time())}-{uuid.uuid4().hex[:6]}.json"
    p.write_text(json.dumps(body, indent=2, default=str)[:80_000], encoding="utf-8")
    return p


def bind_workflow(tid: str, workflow_id: str, *, principal: str = "") -> Dict[str, Any]:
    rec = _load(tid, principal)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    wfs = rec.setdefault("workflows", [])
    if workflow_id and workflow_id not in wfs:
        wfs.append(workflow_id)
    rec["status"] = "working"
    _save(rec)
    return get(tid, principal=principal)


def cwd_for(tid: str = "", *, principal: str = "") -> str:
    if tid:
        rec = _load(tid, principal)
        if rec:
            return str(rec.get("cwd") or "")
    listed = list_teams(principal=principal).get("teams") or []
    if listed:
        return str(listed[0].get("cwd") or "")
    t = open_team("long work", principal=principal)
    return str(t.get("cwd") or "")


def snapshot(*, principal: str = "") -> Dict[str, Any]:
    listed = list_teams(principal=principal)
    return {
        "ok": bool(listed.get("ok")),
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "owner": listed.get("owner") or principal,
        "root": str(tenant_root(principal)) if principal else "",
        "count": listed.get("count") or 0,
        "teams": listed.get("teams") or [],
        "founder_only": True,
        "http": [
            "GET /v1/team/workspace",
            "POST /v1/team/workspace",
            "POST /v1/team/invite",
            "POST /v1/team/note",
        ],
        "note": "Founder-only. Tenant-jailed. Long workflows pass cwd+team_id into jobs.",
    }
