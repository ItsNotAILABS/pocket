"""Endure worker — queued cycles. Never claims learning without native stateful eval."""

from __future__ import annotations

import json
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "endure_worker"
STATE = ROOT / "STATE.json"
INTERVAL = 20.0

_lock = threading.Lock()
_queue: Deque[Dict[str, Any]] = deque()
_stop = threading.Event()
_thread: Optional[threading.Thread] = None
_started = False
_state: Dict[str, Any] = {
    "ok": True,
    "learning": False,
    "stateful_eval": False,
    "native": False,
    "runs": 0,
    "last": None,
}


def _honest(r: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(r or {})
    r["learning"] = bool(r.get("learning") and r.get("stateful_eval") and r.get("native"))
    r.setdefault("stateful_eval", False)
    r.setdefault("native", False)
    if not r["learning"] and "learn" in str(r.get("summary") or "").lower() and "not learning" not in str(r.get("summary") or "").lower():
        r["summary"] = "Auro Endure adapter. Not learning until native stateful evaluation exists."
    return r


def _save() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(_state, indent=2, default=str)[:80_000], encoding="utf-8")


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "worker": "endure",
        "alive": bool(_thread and _thread.is_alive()),
        "queued": len(_queue),
        "learning": False if not (_state.get("learning") and _state.get("stateful_eval") and _state.get("native")) else True,
        **{k: _state.get(k) for k in ("runs", "last", "native", "stateful_eval", "error")},
    }


def run(goal: str, *, experiments: int = 2, cycles: int = 1) -> Dict[str, Any]:
    from pocket.auro_endure import run as endure_run

    r = _honest(endure_run(goal, experiments=experiments, cycles=cycles))
    with _lock:
        _state["runs"] = int(_state.get("runs") or 0) + 1
        _state["last"] = {
            "at": time.time(),
            "goal": (goal or "")[:120],
            "learning": r.get("learning"),
            "native": r.get("native"),
            "stateful_eval": r.get("stateful_eval"),
        }
        _state["learning"] = bool(r.get("learning"))
        _state["native"] = bool(r.get("native"))
        _state["stateful_eval"] = bool(r.get("stateful_eval"))
        _state["error"] = ""
        _save()
    emit("endure", f"run learning={r.get('learning')} native={r.get('native')}", agent="ENDURE-WORKER", role="worker")
    return r


def enqueue(goal: str, *, experiments: int = 2, cycles: int = 1) -> Dict[str, Any]:
    ensure_running()
    rec = {
        "id": "en-" + uuid.uuid4().hex[:10],
        "goal": (goal or "").strip()[:4000] or "Keep a useful experiment alive.",
        "experiments": int(experiments),
        "cycles": int(cycles),
        "queued_at": time.time(),
    }
    with _lock:
        _queue.append(rec)
    return {"ok": True, "queued": rec, **status()}


def process_one() -> bool:
    with _lock:
        if not _queue:
            return False
        rec = _queue.popleft()
    try:
        run(rec.get("goal") or "", experiments=int(rec.get("experiments") or 2), cycles=int(rec.get("cycles") or 1))
    except Exception as e:
        with _lock:
            _state["error"] = str(e)[:200]
            _save()
    return True


def ensure_running() -> Dict[str, Any]:
    global _started, _thread
    with _lock:
        if _started and _thread and _thread.is_alive():
            return status()
        _stop.clear()

        def loop() -> None:
            while not _stop.is_set():
                try:
                    if not process_one():
                        _stop.wait(INTERVAL)
                except Exception as e:
                    with _lock:
                        _state["error"] = str(e)[:200]
                        _save()
                    _stop.wait(INTERVAL)

        _thread = threading.Thread(target=loop, name="pocket-endure-worker", daemon=True)
        _thread.start()
        _started = True
        _state["started_at"] = time.time()
        _save()
    emit("endure", "endure worker armed (not learning)", agent="ENDURE-WORKER", role="worker")
    return status()


def stop() -> Dict[str, Any]:
    global _started
    _stop.set()
    _started = False
    return {"ok": True, "stopped": "endure", "learning": False}
