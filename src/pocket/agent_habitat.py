"""Hybrid Agent Habitat — GUI floor where agents live and work.

Some agents are permanent residents of the habitat (always visible on the desk).
They show live status (idle / thinking / working / speaking / sensing) and can
be focused into chat or assigned a task without living only in a message list.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "habitat"
ROOT.mkdir(parents=True, exist_ok=True)
STATE_PATH = ROOT / "state.json"

# Permanent residents of the hybrid floor (live & work here)
RESIDENTS: List[Dict[str, Any]] = [
    {
        "id": "codex",
        "name": "Codex",
        "role": "Host coding",
        "room": "forge",
        "color": "#22c55e",
        "desk_mode": "codex",
        "home": "local",
    },
    {
        "id": "grok",
        "name": "Grok",
        "role": "Code + research",
        "room": "lab",
        "color": "#06b6d4",
        "desk_mode": "grok",
        "home": "local",
    },
    {
        "id": "claude",
        "name": "Claude",
        "role": "Agent SDK tools",
        "room": "studio",
        "color": "#f59e0b",
        "desk_mode": "claude",
        "home": "local",
    },
    {
        "id": "loomgraph",
        "name": "LOOMGRAPH",
        "role": "Graph+loop harness",
        "room": "ops",
        "color": "#34d399",
        "desk_mode": "harness",
        "home": "local",
        "note": "Default forever orchestration — see the graph, run the loop",
    },
    {
        "id": "aria",
        "name": "Aria",
        "role": "Voice persona",
        "room": "lounge",
        "color": "#0b84fe",
        "desk_mode": "voice",
        "home": "voice",
    },
    {
        "id": "work",
        "name": "Working",
        "role": "Live voice + hardware",
        "room": "ops",
        "color": "#f472b6",
        "desk_mode": "work",
        "home": "hardware",
    },
    {
        "id": "sophia",
        "name": "Sophia",
        "role": "Coding swarm lead",
        "room": "swarm",
        "color": "#c084fc",
        "desk_mode": "coding_swarm",
        "home": "swarm",
    },
    {
        "id": "solver",
        "name": "Solver",
        "role": "Coding swarm builder",
        "room": "swarm",
        "color": "#a78bfa",
        "desk_mode": "coding_swarm",
        "home": "swarm",
    },
    {
        "id": "oculus",
        "name": "OCULUS",
        "role": "Vision · fusion eyes",
        "room": "watch",
        "color": "#22d3ee",
        "desk_mode": "vision",
        "home": "hardware",
    },
    {
        "id": "archon",
        "name": "ARCHON",
        "role": "Orchestrator",
        "room": "bridge",
        "color": "#f43f5e",
        "desk_mode": "archon",
        "home": "mesh",
    },
    {
        "id": "github",
        "name": "GitHub",
        "role": "Cloud · gh CLI",
        "room": "cloud",
        "color": "#e6edf3",
        "desk_mode": "github",
        "home": "cloud",
    },
]

_state: Dict[str, Any] = {
    "residents": {},
    "activity": [],
    "open": True,
    "updated_at": 0.0,
}


def _boot_residents() -> None:
    for r in RESIDENTS:
        rid = r["id"]
        if rid not in _state["residents"]:
            _state["residents"][rid] = {
                **r,
                "status": "idle",
                "task": "",
                "last_line": "At home in the habitat",
                "updated_at": time.time(),
                "pulses": 0,
            }


def _load() -> None:
    global _state
    if STATE_PATH.exists():
        try:
            d = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                _state.update(d)
        except Exception:
            pass
    _boot_residents()


def _save() -> None:
    _state["updated_at"] = time.time()
    try:
        STATE_PATH.write_text(json.dumps(_state, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass


_load()


def set_open(open_: bool = True) -> Dict[str, Any]:
    _state["open"] = bool(open_)
    _save()
    return status()


def pulse(
    agent_id: str,
    *,
    status: str = "working",
    task: str = "",
    line: str = "",
) -> Dict[str, Any]:
    """Update a resident's live state (called from jobs/harness/work mode)."""
    _boot_residents()
    aid = (agent_id or "").lower().strip()
    # aliases
    aliases = {
        "voice": "aria",
        "v2v": "aria",
        "coding_swarm": "sophia",
        "swarm": "sophia",
        "vision": "oculus",
        "screen": "oculus",
        "working": "work",
        "live_work": "work",
    }
    aid = aliases.get(aid, aid)
    rec = _state["residents"].get(aid)
    if not rec:
        # guest card
        rec = {
            "id": aid,
            "name": aid.title(),
            "role": "guest",
            "room": "guest",
            "color": "#a1a1aa",
            "desk_mode": aid,
            "home": "guest",
            "status": "idle",
            "task": "",
            "last_line": "",
            "pulses": 0,
        }
        _state["residents"][aid] = rec
    rec["status"] = (status or "working")[:32]
    if task:
        rec["task"] = task[:200]
    if line:
        rec["last_line"] = line[:240]
    rec["updated_at"] = time.time()
    rec["pulses"] = int(rec.get("pulses") or 0) + 1
    _state["activity"].append(
        {
            "at": time.time(),
            "agent": aid,
            "status": rec["status"],
            "task": rec.get("task"),
            "line": rec.get("last_line"),
        }
    )
    _state["activity"] = _state["activity"][-80:]
    _save()
    return {"ok": True, "resident": rec}


def idle(agent_id: str, line: str = "") -> Dict[str, Any]:
    return pulse(agent_id, status="idle", line=line or "Back in the habitat")


def status() -> Dict[str, Any]:
    _boot_residents()
    # Live overlays from sessions / harness / work
    live_map: Dict[str, str] = {}
    try:
        from pocket.sessions import list_sessions

        for s in list_sessions(30) or []:
            mode = str(s.get("mode") or "").lower()
            st = str(s.get("status") or "").lower()
            if st in ("running", "busy", "streaming"):
                live_map[mode] = "working"
    except Exception:
        pass
    try:
        from pocket.agentic_harness import list_live

        lv = list_live()
        for sa in lv.get("subagents") or []:
            if sa.get("status") == "running":
                name = str(sa.get("name") or sa.get("agent") or "").lower()
                live_map[name] = "working"
    except Exception:
        pass
    try:
        from pocket.work_mode import status as ws

        w = ws()
        if w.get("live"):
            live_map["work"] = "working"
    except Exception:
        pass
    try:
        from pocket.screen_share import status as sc

        s = sc()
        if s.get("can_view"):
            live_map["oculus"] = live_map.get("oculus") or "sensing"
        if s.get("can_control"):
            live_map["work"] = live_map.get("work") or "working"
    except Exception:
        pass

    residents = []
    for r in RESIDENTS:
        rid = r["id"]
        rec = dict(_state["residents"].get(rid) or r)
        # overlay live
        if rid in live_map:
            rec["status"] = live_map[rid]
        elif rid == "aria" and live_map.get("voice"):
            rec["status"] = live_map["voice"]
        elif rid == "sophia" and (live_map.get("coding_swarm") or live_map.get("forge_headless")):
            rec["status"] = "working"
        # stale working → idle after 3 min without pulse
        if rec.get("status") in ("working", "thinking", "speaking", "sensing"):
            age = time.time() - float(rec.get("updated_at") or 0)
            if age > 180 and rid not in live_map:
                rec["status"] = "idle"
        residents.append(rec)

    rooms: Dict[str, List[str]] = {}
    for rec in residents:
        rooms.setdefault(rec.get("room") or "floor", []).append(rec["id"])

    return {
        "ok": True,
        "schema": "pocket.agent_habitat.v1",
        "open": bool(_state.get("open", True)),
        "residents": residents,
        "rooms": rooms,
        "activity": list(reversed(_state.get("activity") or []))[:24],
        "updated_at": _state.get("updated_at"),
        "doctrine": (
            "Hybrid floor: these agents live here and work in the open. "
            "Chat is still the conversation; the habitat is where you see them."
        ),
    }


def assign(agent_id: str, task: str) -> Dict[str, Any]:
    """Seat an agent with a task string (desk will open their mode)."""
    return pulse(agent_id, status="working", task=task, line=f"Assigned: {task[:120]}")
