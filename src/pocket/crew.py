"""Crew board — one lane per repo, 1–2 agent seats side by side.

You steer. Each seat is a wired CLI (Grok / Codex / Meta / Gemini) on a
named *part* of the same repo. They share NOTES so they can hand off.
We do **not** spawn extra OS windows: those steal focus and lag Portal.
The board *is* the side-by-side spawn.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
STATE = ROOT / "crew.json"
SCHEMA = "pocket.crew.v1"
MAX_SEATS = 2
CLIS = ("grok", "codex", "meta", "gemini", "spark")

_lock = threading.Lock()
_runs: Dict[str, threading.Thread] = {}


def _load() -> Dict[str, Any]:
    if STATE.is_file():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("lanes"), list):
                return data
        except Exception:
            pass
    return {"schema": SCHEMA, "lanes": []}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    data["schema"] = SCHEMA
    data["updated"] = time.time()
    STATE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _lane(data: Dict[str, Any], lid: str) -> Optional[Dict[str, Any]]:
    for ln in data.get("lanes") or []:
        if ln.get("id") == lid:
            return ln
    return None


def _seat(data: Dict[str, Any], sid: str) -> Optional[tuple]:
    for ln in data.get("lanes") or []:
        for st in ln.get("seats") or []:
            if st.get("id") == sid:
                return ln, st
    return None


def board() -> Dict[str, Any]:
    with _lock:
        data = _load()
    clis = []
    try:
        from pocket.phoneai_code_desk import detect_clis, list_repos

        clis = detect_clis()
        repos = list_repos(80)
    except Exception:
        repos = {"ok": False, "repos": []}
    return {
        "ok": True,
        "schema": SCHEMA,
        "layout": "side-by-side",
        "max_seats": MAX_SEATS,
        "note": "One lane per repo. 1–2 CLIs, different parts. You steer. No extra OS windows.",
        "lanes": data.get("lanes") or [],
        "clis": clis,
        "repos": repos.get("repos") or [],
        "wired": [c["id"] for c in clis if c.get("available")],
    }


def spawn(
    *,
    repo: str,
    clis: Optional[List[str]] = None,
    parts: Optional[List[str]] = None,
    goal: str = "",
) -> Dict[str, Any]:
    repo = (repo or "").strip()
    if not repo:
        return {"ok": False, "error": "pick a repo"}
    names = [str(c).strip().lower() for c in (clis or ["grok"]) if str(c).strip()]
    names = [c if c in CLIS else "grok" for c in names][:MAX_SEATS]
    if not names:
        names = ["grok"]
    parts = [str(p).strip()[:80] for p in (parts or [])]
    while len(parts) < len(names):
        parts.append(f"part {len(parts) + 1}")
    loc = {"ok": True, "cwd": "", "repo": repo}
    try:
        from pocket.phoneai_code_desk import ensure_repo_cwd

        loc = ensure_repo_cwd(repo)
    except Exception as e:
        loc = {"ok": False, "error": str(e)[:200], "cwd": "", "repo": repo}
    cwd = str(loc.get("cwd") or "")
    full = str(loc.get("repo") or repo)
    with _lock:
        data = _load()
        lane = next((ln for ln in data["lanes"] if (ln.get("repo") or "").lower() == full.lower()), None)
        if lane is None:
            lane = {
                "id": "ln-" + uuid.uuid4().hex[:8],
                "repo": full,
                "cwd": cwd,
                "goal": (goal or "")[:400],
                "seats": [],
                "notes": [],
                "created": time.time(),
                "updated": time.time(),
            }
            data["lanes"].insert(0, lane)
        elif cwd:
            lane["cwd"] = cwd
        if goal:
            lane["goal"] = goal[:400]
        room = MAX_SEATS - len(lane.get("seats") or [])
        if room <= 0:
            return {
                "ok": False,
                "error": f"{full} already has {MAX_SEATS} seats — steer them or close one",
                "lane": lane,
            }
        added = []
        for cli, part in list(zip(names, parts))[:room]:
            seat = {
                "id": "st-" + uuid.uuid4().hex[:8],
                "cli": cli,
                "part": part or cli,
                "status": "idle",
                "log": [],
                "created": time.time(),
                "updated": time.time(),
            }
            lane["seats"].append(seat)
            added.append(seat)
        lane["updated"] = time.time()
        _save(data)
    _handoff(lane["id"], f"spawned {', '.join(s['cli']+' on '+s['part'] for s in added)}")
    return {"ok": True, "lane": lane, "added": added, "cwd": cwd, "repo_ok": bool(loc.get("ok")), "repo_error": loc.get("error") or ""}


def _handoff(lane_id: str, text: str, *, agent: str = "you") -> None:
    line = {"t": time.time(), "agent": agent, "text": (text or "")[:400]}
    with _lock:
        data = _load()
        ln = _lane(data, lane_id)
        if not ln:
            return
        notes = ln.setdefault("notes", [])
        notes.append(line)
        ln["notes"] = notes[-40:]
        ln["updated"] = time.time()
        _save(data)
    try:
        from pocket.team_workspace import note as team_note

        team_note(lane_id.replace("ln-", "crew-")[:32], text, agent=agent, principal="pocket")
    except Exception:
        pass


def steer(seat_id: str, text: str, *, wait: bool = False) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "say what this seat should do"}
    with _lock:
        data = _load()
        hit = _seat(data, seat_id)
        if not hit:
            return {"ok": False, "error": "unknown seat"}
        lane, seat = hit
        if seat.get("status") == "running":
            return {"ok": False, "error": "that seat is already running — wait or steer the other"}
        seat["status"] = "running"
        seat["updated"] = time.time()
        seat.setdefault("log", []).append({"role": "you", "text": text, "t": time.time()})
        _save(data)
        lid, sid, cli, part, cwd, repo = (
            lane["id"],
            seat["id"],
            seat["cli"],
            seat.get("part") or "",
            lane.get("cwd") or "",
            lane.get("repo") or "",
        )
        notes = list(lane.get("notes") or [])[-6:]
    prompt = (
        f"You are the {cli} seat on {repo}.\n"
        f"Your part only: {part}\n"
        f"Do not take the other seat's part. Hand off via short notes.\n"
        f"Recent crew notes: {json.dumps(notes, default=str)[:800]}\n\n"
        f"Steer: {text}"
    )
    if wait:
        return _run_seat(lid, sid, cli, cwd, repo, prompt)
    t = threading.Thread(
        target=_run_seat,
        args=(lid, sid, cli, cwd, repo, prompt),
        name=f"crew-{sid}",
        daemon=True,
    )
    _runs[sid] = t
    t.start()
    return {"ok": True, "seat_id": sid, "status": "running", "cli": cli, "part": part, "repo": repo}


def _run_seat(lid: str, sid: str, cli: str, cwd: str, repo: str, prompt: str) -> Dict[str, Any]:
    try:
        from pocket.phoneai_code_desk import run as desk_run

        r = desk_run(prompt, cli=cli, repo=repo, cwd=cwd, new=True)
    except Exception as e:
        r = {"ok": False, "error": str(e)[:200], "engine": cli}
    reply = str(r.get("reply") or r.get("error") or "")[:4000]
    with _lock:
        data = _load()
        hit = _seat(data, sid)
        if hit:
            _ln, seat = hit
            seat["status"] = "idle" if r.get("ok") else "error"
            seat["updated"] = time.time()
            seat.setdefault("log", []).append(
                {"role": cli, "text": reply or "(empty)", "t": time.time(), "ok": bool(r.get("ok"))}
            )
            seat["log"] = seat["log"][-30:]
            _save(data)
    _handoff(lid, f"{cli}@{sid[:8]} done: {reply[:180]}", agent=cli)
    return {"ok": bool(r.get("ok")), "seat_id": sid, "reply": reply, "engine": r.get("engine") or cli}


def close_seat(seat_id: str) -> Dict[str, Any]:
    with _lock:
        data = _load()
        hit = _seat(data, seat_id)
        if not hit:
            return {"ok": False, "error": "unknown seat"}
        lane, seat = hit
        lane["seats"] = [s for s in lane.get("seats") or [] if s.get("id") != seat_id]
        if not lane["seats"]:
            data["lanes"] = [ln for ln in data["lanes"] if ln.get("id") != lane["id"]]
        else:
            lane["updated"] = time.time()
        _save(data)
    return {"ok": True, "closed": seat_id}


def html() -> str:
    from pocket.crew_ui import crew_html

    return crew_html()
