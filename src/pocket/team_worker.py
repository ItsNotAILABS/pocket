"""Team worker — ticks tenant-jailed workspaces and binds seats/jobs.

Founder-host only. Does not invent teams for market seats.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from pocket.live_events import emit

STATE = Path.home() / ".pocket" / "team_worker.json"
INTERVAL = 90.0

_lock = threading.Lock()
_stop = threading.Event()
_thread: Optional[threading.Thread] = None
_started = False
_state: Dict[str, Any] = {"ok": True, "ticks": 0, "last": None}


def _save_state() -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(_state, indent=2, default=str)[:40_000], encoding="utf-8")


def status() -> Dict[str, Any]:
    alive = bool(_thread and _thread.is_alive())
    return {
        "ok": True,
        "worker": "team",
        "alive": alive,
        "interval_sec": INTERVAL,
        "founder_only": True,
        **_state,
    }


def bind_seat(tid: str, agent: str, *, principal: str = "pocket") -> Dict[str, Any]:
    from pocket.team_workspace import invite

    return invite(tid, agent, principal=principal)


def bind_job(job: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.tenant_jail import attach_team_to_job

    return attach_team_to_job(job)


def tick(*, principal: str = "pocket") -> Dict[str, Any]:
    from pocket.team_workspace import list_teams, note, receipt

    listed = list_teams(principal=principal)
    n = 0
    for row in listed.get("teams") or []:
        tid = str(row.get("id") or "")
        if not tid:
            continue
        note(tid, "team-worker pulse", agent="team-worker", principal=principal)
        receipt(tid, {"worker": "team", "at": time.time(), "id": tid}, principal=principal)
        n += 1
    with _lock:
        _state["ticks"] = int(_state.get("ticks") or 0) + 1
        _state["last"] = {"at": time.time(), "principal": principal, "teams": n}
        _state["error"] = ""
        _save_state()
    emit("team", f"tick principal={principal} teams={n}", agent="TEAM-WORKER", role="worker")
    return {"ok": True, "principal": principal, "teams": n, **status()}


def ensure_running(*, principal: str = "pocket") -> Dict[str, Any]:
    global _started, _thread
    with _lock:
        if _started and _thread and _thread.is_alive():
            return status()
        _stop.clear()

        def loop() -> None:
            while not _stop.is_set():
                try:
                    tick(principal=principal)
                except Exception as e:
                    with _lock:
                        _state["error"] = str(e)[:200]
                        _save_state()
                _stop.wait(INTERVAL)

        _thread = threading.Thread(target=loop, name="pocket-team-worker", daemon=True)
        _thread.start()
        _started = True
        _state["started_at"] = time.time()
        _state["principal"] = principal
        _save_state()
    emit("team", "team worker armed", agent="TEAM-WORKER", role="worker")
    return status()


def stop() -> Dict[str, Any]:
    global _started
    _stop.set()
    _started = False
    return {"ok": True, "stopped": "team"}
