"""Persistent team workspace for long work.

A real on-disk room a *team* of Pocket agents share:

  ~/.pocket/teams/<id>/
    TEAM.json       roster, goal, engines (Codex first-class when CLI is here)
    workspace/      cwd for Codex / Grok / shell
    receipts/       JSON receipts
    seats/          per-agent notes

Survives chat end, host restart, and PhoneAI. KEEP dies with the chat;
this does not. Long workflows attach here so ticks write into the same tree.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "teams"
SCHEMA = "pocket.team.workspace.v1"
PROTOCOL = "POCKET-TEAM-WORKSPACE/1.0"
DEFAULT_ENGINES = ("codex", "grok")
DEFAULT_AGENTS = ("codex", "grok", "coder")


def _tid() -> str:
    return "team-" + uuid.uuid4().hex[:10]


def _dir(tid: str) -> Path:
    return ROOT / tid


def _meta(tid: str) -> Path:
    return _dir(tid) / "TEAM.json"


def _load(tid: str) -> Optional[Dict[str, Any]]:
    p = _meta(tid)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save(rec: Dict[str, Any]) -> None:
    rec["updated_at"] = time.time()
    d = _dir(rec["id"])
    (d / "workspace").mkdir(parents=True, exist_ok=True)
    (d / "receipts").mkdir(parents=True, exist_ok=True)
    (d / "seats").mkdir(parents=True, exist_ok=True)
    _meta(rec["id"]).write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")


def _seed(cwd: Path, goal: str, engines: List[str]) -> None:
    cwd.mkdir(parents=True, exist_ok=True)
    readme = cwd / "README.md"
    if not readme.is_file():
        readme.write_text(
            f"# Team workspace\n\nGoal: {goal}\n\n"
            f"Engines: {', '.join(engines)}\n"
            "This folder is the persistent cwd for the agent team. "
            "Codex and Grok run *here*. Notes and receipts stay on this PC.\n",
            encoding="utf-8",
        )
    notes = cwd / "NOTES.md"
    if not notes.is_file():
        notes.write_text(f"# Notes\n\n- opened {time.strftime('%Y-%m-%d %H:%M')}\n", encoding="utf-8")
    inbox = cwd / "INBOX.md"
    if not inbox.is_file():
        inbox.write_text("# Team inbox\n\nAgents leave handoffs here.\n", encoding="utf-8")


def _engines() -> List[str]:
    out = list(DEFAULT_ENGINES)
    try:
        from pocket.executor import which_codex

        if which_codex() and "codex" not in out:
            out.insert(0, "codex")
    except Exception:
        pass
    return out


def open_team(
    goal: str = "",
    *,
    team_id: str = "",
    agents: Optional[List[str]] = None,
    engines: Optional[List[str]] = None,
    label: str = "",
) -> Dict[str, Any]:
    """Create or reopen a persistent team workspace."""
    ROOT.mkdir(parents=True, exist_ok=True)
    tid = (team_id or "").strip()
    if tid:
        rec = _load(tid)
        if rec:
            rec["goal"] = (goal or rec.get("goal") or "")[:4000]
            if agents:
                rec["agents"] = list(dict.fromkeys(list(rec.get("agents") or []) + list(agents)))
            rec["status"] = "open"
            _save(rec)
            return get(tid)
    tid = tid or _tid()
    eng = list(engines or _engines())
    ag = list(dict.fromkeys(list(agents or DEFAULT_AGENTS) + eng))
    rec = {
        "id": tid,
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "status": "open",
        "label": (label or (goal or "long work")[:48])[:80],
        "goal": (goal or "long-running team work").strip()[:4000],
        "agents": ag,
        "engines": eng,
        "workflows": [],
        "created_at": time.time(),
        "updated_at": time.time(),
        "cwd": str(_dir(tid) / "workspace"),
    }
    _seed(Path(rec["cwd"]), rec["goal"], eng)
    _save(rec)
    return get(tid)


def get(tid: str) -> Dict[str, Any]:
    rec = _load(tid)
    if not rec:
        return {"ok": False, "error": "unknown team", "id": tid}
    cwd = Path(rec.get("cwd") or (_dir(tid) / "workspace"))
    rec["ok"] = True
    rec["cwd"] = str(cwd)
    rec["exists"] = cwd.is_dir()
    rec["files"] = sorted(p.name for p in cwd.iterdir())[:40] if cwd.is_dir() else []
    return rec


def list_teams() -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in ROOT.glob("team-*/TEAM.json"):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": rec.get("id"),
                    "label": rec.get("label"),
                    "goal": (rec.get("goal") or "")[:120],
                    "status": rec.get("status"),
                    "agents": rec.get("agents") or [],
                    "cwd": rec.get("cwd"),
                    "updated_at": rec.get("updated_at"),
                }
            )
        except Exception:
            continue
    rows.sort(key=lambda r: float(r.get("updated_at") or 0), reverse=True)
    return {"ok": True, "schema": SCHEMA, "count": len(rows), "teams": rows}


def invite(tid: str, agent: str) -> Dict[str, Any]:
    rec = _load(tid)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    a = (agent or "").strip()
    if not a:
        return {"ok": False, "error": "agent required"}
    rec.setdefault("agents", [])
    if a not in rec["agents"]:
        rec["agents"].append(a)
    seat = _dir(tid) / "seats" / f"{a.replace('/', '-')[:40]}.md"
    seat.parent.mkdir(parents=True, exist_ok=True)
    if not seat.is_file():
        seat.write_text(f"# Seat {a}\n\nJoined {time.strftime('%Y-%m-%d %H:%M')}\n", encoding="utf-8")
    _save(rec)
    return get(tid)


def note(tid: str, text: str, *, agent: str = "team") -> Dict[str, Any]:
    rec = _load(tid)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    line = f"- {time.strftime('%H:%M')} @{agent}: {(text or '').strip()[:400]}\n"
    p = Path(rec["cwd"]) / "NOTES.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(line)
    rec["last_note"] = line.strip()
    _save(rec)
    return {"ok": True, "id": tid, "note": line.strip(), "cwd": rec["cwd"]}


def receipt(tid: str, body: Dict[str, Any]) -> Path:
    d = _dir(tid) / "receipts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{int(time.time())}-{uuid.uuid4().hex[:6]}.json"
    p.write_text(json.dumps(body, indent=2, default=str)[:80_000], encoding="utf-8")
    return p


def bind_workflow(tid: str, workflow_id: str) -> Dict[str, Any]:
    rec = _load(tid)
    if not rec:
        return {"ok": False, "error": "unknown team"}
    wfs = rec.setdefault("workflows", [])
    if workflow_id and workflow_id not in wfs:
        wfs.append(workflow_id)
    rec["status"] = "working"
    _save(rec)
    return get(tid)


def cwd_for(tid: str = "") -> str:
    if tid:
        rec = _load(tid)
        if rec:
            return str(rec.get("cwd") or (_dir(tid) / "workspace"))
    # latest open team
    listed = list_teams().get("teams") or []
    if listed:
        return str(listed[0].get("cwd") or "")
    t = open_team("long work")
    return str(t.get("cwd") or "")


def snapshot() -> Dict[str, Any]:
    listed = list_teams()
    return {
        "ok": True,
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "root": str(ROOT),
        "count": listed.get("count") or 0,
        "teams": listed.get("teams") or [],
        "http": [
            "GET /v1/team/workspace",
            "POST /v1/team/workspace",
            "POST /v1/team/invite",
            "POST /v1/team/note",
        ],
        "note": "Long work lives here. Codex CLI on this host uses this cwd. KEEP dies with chat; the team folder does not.",
    }
