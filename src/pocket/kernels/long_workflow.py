"""Long-running cognitive workflows — days, not one-shot loops.

State lives on disk (`~/.pocket/kernels/workflows/`). A tick:
  1. Appends to a growing context log
  2. Runs the 5-stage cognitive loop against that context
  3. Checkpoints
  4. Compacts old ticks so the file stays usable for *longgg* runs

Host-bound by default (survives chat). Optional session_id binds like KEEP.
On boot, `ensure_running()` restarts threads for status=running runs.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "kernels" / "workflows"
ROOT.mkdir(parents=True, exist_ok=True)

SCHEMA = "pocket.long_workflow.v1"
DEFAULT_INTERVAL = 90.0
DEFAULT_HOURS = 168.0  # 7 days
KEEP_TICKS_FULL = 24
COMPACT_AFTER = 80
MAX_NOTE = 480

_lock = threading.Lock()
_stops: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}


def _path(wid: str) -> Path:
    return ROOT / f"{wid}.json"


def _load(wid: str) -> Optional[Dict[str, Any]]:
    p = _path(wid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save(wf: Dict[str, Any]) -> None:
    wf["updated_at"] = time.time()
    p = _path(wf["id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(wf, indent=2, default=str), encoding="utf-8")


def _list_ids() -> List[str]:
    return [p.stem for p in ROOT.glob("wf-*.json")]


def _compact(wf: Dict[str, Any]) -> None:
    ticks = list(wf.get("ticks") or [])
    if len(ticks) <= COMPACT_AFTER:
        return
    old, keep = ticks[:-KEEP_TICKS_FULL], ticks[-KEEP_TICKS_FULL:]
    bits = []
    ok_n = sum(1 for t in old if t.get("ok"))
    bits.append(f"{len(old)} older ticks compacted ({ok_n} ok).")
    for t in old[:3] + old[-2:]:
        bits.append(f"t{t.get('n')}: {(t.get('note') or '')[:80]}")
    archive = wf.setdefault("compacted", [])
    archive.append({"until_tick": old[-1].get("n"), "at": time.time(), "summary": " | ".join(bits)[:1200]})
    wf["ticks"] = keep
    ctx = wf.setdefault("context", {})
    ctx["rolled_summary"] = (ctx.get("rolled_summary") or "")
    add = "\n".join(bits)
    ctx["rolled_summary"] = (ctx["rolled_summary"] + "\n" + add)[-8000:]


def _ctx_blob(wf: Dict[str, Any], limit: int = 3500) -> str:
    ctx = wf.get("context") or {}
    parts = [
        f"GOAL: {wf.get('goal')}",
        f"CYCLE: {wf.get('cycles')}  ticks={wf.get('tick_count')}  hours_cap={wf.get('max_hours')}",
    ]
    if ctx.get("rolled_summary"):
        parts.append("HISTORY:\n" + str(ctx["rolled_summary"])[-1500:])
    if ctx.get("last_plan"):
        parts.append("LAST_PLAN:\n" + str(ctx["last_plan"])[:800])
    if ctx.get("last_sense"):
        parts.append("LAST_SENSE:\n" + str(ctx["last_sense"])[:800])
    arts = ctx.get("artifacts") or []
    if arts:
        parts.append("ARTIFACTS:\n" + "\n".join(str(a)[:120] for a in arts[-12:]))
    text = "\n\n".join(parts)
    return text[:limit]


def start(
    goal: str,
    *,
    session_id: str = "",
    interval_sec: float = DEFAULT_INTERVAL,
    max_hours: float = DEFAULT_HOURS,
    keep: bool = False,
    agents: Optional[List[str]] = None,
    label: str = "",
    host_bound: bool = True,
    auto_arm: bool = True,
) -> Dict[str, Any]:
    """Begin a long workflow. host_bound=True survives chat (default)."""
    wid = "wf-" + uuid.uuid4().hex[:12]
    now = time.time()
    hours = max(0.25, float(max_hours or DEFAULT_HOURS))
    wf = {
        "id": wid,
        "schema": SCHEMA,
        "status": "running",
        "goal": (goal or "long cognitive workflow").strip()[:4000],
        "label": (label or (goal or "workflow")[:48])[:80],
        "session_id": "" if host_bound else (session_id or "").strip(),
        "host_bound": bool(host_bound),
        "interval_sec": max(20.0, float(interval_sec or DEFAULT_INTERVAL)),
        "max_hours": hours,
        "max_until": now + hours * 3600,
        "keep_id": "",
        "extra_agents": list(agents or ["gemini-coder", "sprint-orchestrator"]),
        "cycles": 0,
        "tick_count": 0,
        "ticks": [],
        "compacted": [],
        "context": {
            "rolled_summary": "",
            "last_plan": "",
            "last_sense": "",
            "artifacts": [],
            "open_questions": [],
        },
        "last_error": "",
        "stop_reason": "",
        "created_at": now,
        "updated_at": now,
    }
    if keep:
        try:
            from pocket.keep_agents import start as keep_start

            kr = keep_start(
                session_id=wf["session_id"],
                goal=wf["goal"],
                interval_sec=max(45.0, wf["interval_sec"]),
                max_hours=hours,
                with_browser=False,
                label=f"wf:{wid[-6:]}",
            )
            ag = (kr.get("agent") or {}) if isinstance(kr, dict) else {}
            wf["keep_id"] = str(ag.get("id") or kr.get("id") or "")
        except Exception as e:
            wf["keep_error"] = str(e)[:160]
    _save(wf)
    if auto_arm:
        _arm(wid)
    emit("workflow", f"start {wid} hours={hours} host_bound={host_bound}", agent="WORKFLOW", role="kernel")
    return get(wid)


def _arm(wid: str) -> None:
    ev = threading.Event()
    with _lock:
        old = _stops.get(wid)
        if old:
            old.set()
        _stops[wid] = ev

    def loop() -> None:
        while not ev.is_set():
            wf = _load(wid)
            if not wf or wf.get("status") != "running":
                break
            if time.time() > float(wf.get("max_until") or 0):
                stop(wid, reason="max_hours")
                break
            sid = wf.get("session_id") or ""
            if sid:
                try:
                    from pocket.keep_agents import _session_alive

                    if not _session_alive(sid):
                        stop(wid, reason="chat_ended")
                        break
                except Exception:
                    pass
            try:
                tick(wid)
            except Exception as e:
                wf = _load(wid) or {}
                wf["last_error"] = str(e)[:300]
                _save(wf)
            iv = max(20.0, float((wf or {}).get("interval_sec") or DEFAULT_INTERVAL))
            ev.wait(iv)

    t = threading.Thread(target=loop, name=f"pocket-wf-{wid[-6:]}", daemon=True)
    t.start()
    with _lock:
        _threads[wid] = t


def tick(wid: str) -> Dict[str, Any]:
    """One long-cycle: cognitive loop + extra agents, then checkpoint."""
    from pocket.kernels.cognitive_loop import run_loop
    from pocket.kernels.slab import get_cache

    wf = _load(wid)
    if not wf:
        return {"ok": False, "error": "unknown workflow", "id": wid}
    if wf.get("status") not in ("running", "paused"):
        return {"ok": False, "error": f"status={wf.get('status')}", "id": wid}

    scratch = get_cache("long-wf", size=512)
    buf = scratch.alloc()
    blob = _ctx_blob(wf)
    prompt = f"{wf.get('goal')}\n\n--- long context ---\n{blob}"
    t0 = time.perf_counter()
    loop = run_loop(prompt, parallel=True)
    extras: List[Dict[str, Any]] = []
    try:
        from pocket.agent_invoke import invoke

        for name in wf.get("extra_agents") or []:
            extras.append(invoke(name, prompt=prompt[:1500], sync=False))
    except Exception as e:
        extras.append({"ok": False, "error": str(e)})

    ms = round((time.perf_counter() - t0) * 1000, 3)
    n = int(wf.get("tick_count") or 0) + 1
    note_parts = []
    for r in loop.get("results") or []:
        st = r.get("stage")
        if st == "plan":
            wf["context"]["last_plan"] = str(r.get("markdown") or r.get("message") or "")[:1200]
        if st == "sense":
            wf["context"]["last_sense"] = str(r.get("markdown") or r.get("brief") or r.get("message") or "")[:1200]
        if r.get("job_id"):
            wf["context"].setdefault("artifacts", []).append(f"job:{r['job_id']}")
        note_parts.append(f"{st}={'ok' if r.get('ok') else 'fail'}")
    note = f"cycle {n} {ms}ms " + " ".join(note_parts)

    rec = {
        "n": n,
        "at": time.time(),
        "ok": bool(loop.get("ok")),
        "loop_ms": loop.get("loop_ms"),
        "tick_ms": ms,
        "note": note[:MAX_NOTE],
        "stages_ok": [r.get("stage") for r in (loop.get("results") or []) if r.get("ok")],
        "extra_ok": sum(1 for e in extras if e.get("ok")),
    }
    wf["tick_count"] = n
    wf["cycles"] = n
    wf["ticks"] = list(wf.get("ticks") or []) + [rec]
    wf["last_error"] = "" if rec["ok"] else (loop.get("error") or note)[:300]
    arts = wf["context"].setdefault("artifacts", [])
    wf["context"]["artifacts"] = arts[-80:]
    _compact(wf)
    _save(wf)
    scratch.free(buf)
    emit("workflow", f"tick {wid} n={n} {ms}ms", agent="WORKFLOW", role="kernel")
    return {"ok": True, "id": wid, "tick": rec, "context_chars": len(_ctx_blob(wf)), "status": get(wid)}


def pause(wid: str) -> Dict[str, Any]:
    wf = _load(wid)
    if not wf:
        return {"ok": False, "error": "unknown workflow"}
    wf["status"] = "paused"
    _save(wf)
    ev = _stops.get(wid)
    if ev:
        ev.set()
    return get(wid)


def resume(wid: str) -> Dict[str, Any]:
    wf = _load(wid)
    if not wf:
        return {"ok": False, "error": "unknown workflow"}
    if time.time() > float(wf.get("max_until") or 0):
        wf["status"] = "done"
        wf["stop_reason"] = "max_hours"
        _save(wf)
        return get(wid)
    wf["status"] = "running"
    wf["stop_reason"] = ""
    _save(wf)
    _arm(wid)
    return get(wid)


def stop(wid: str, *, reason: str = "stop") -> Dict[str, Any]:
    wf = _load(wid)
    if not wf:
        return {"ok": False, "error": "unknown workflow"}
    wf["status"] = "done"
    wf["stop_reason"] = reason
    _save(wf)
    ev = _stops.get(wid)
    if ev:
        ev.set()
    kid = wf.get("keep_id")
    if kid:
        try:
            from pocket.keep_agents import stop as kstop

            kstop(kid)
        except Exception:
            pass
    return get(wid)


def get(wid: str) -> Dict[str, Any]:
    wf = _load(wid)
    if not wf:
        return {"ok": False, "error": "unknown workflow", "id": wid}
    alive = bool(_threads.get(wid) and _threads[wid].is_alive() and wf.get("status") == "running")
    return {
        "ok": True,
        "schema": SCHEMA,
        "id": wf["id"],
        "status": wf.get("status"),
        "thread_alive": alive,
        "goal": wf.get("goal"),
        "label": wf.get("label"),
        "host_bound": wf.get("host_bound"),
        "session_id": wf.get("session_id"),
        "keep_id": wf.get("keep_id"),
        "interval_sec": wf.get("interval_sec"),
        "max_hours": wf.get("max_hours"),
        "hours_left": max(0.0, (float(wf.get("max_until") or 0) - time.time()) / 3600.0),
        "tick_count": wf.get("tick_count"),
        "compacted": len(wf.get("compacted") or []),
        "context_chars": len(_ctx_blob(wf)),
        "last_tick": (wf.get("ticks") or [None])[-1],
        "last_error": wf.get("last_error"),
        "stop_reason": wf.get("stop_reason"),
        "created_at": wf.get("created_at"),
        "updated_at": wf.get("updated_at"),
        "poll": f"/v1/workflows/{wf['id']}",
    }


def list_runs(*, limit: int = 40) -> Dict[str, Any]:
    rows = []
    for wid in _list_ids():
        g = get(wid)
        if g.get("ok"):
            rows.append(g)
    rows.sort(key=lambda x: float(x.get("updated_at") or 0), reverse=True)
    return {
        "ok": True,
        "schema": SCHEMA,
        "count": len(rows),
        "running": sum(1 for r in rows if r.get("status") == "running"),
        "workflows": rows[: max(1, int(limit))],
    }


def ensure_running() -> Dict[str, Any]:
    """Boot: re-arm every disk run still marked running."""
    armed = []
    for wid in _list_ids():
        wf = _load(wid)
        if not wf or wf.get("status") != "running":
            continue
        if time.time() > float(wf.get("max_until") or 0):
            stop(wid, reason="max_hours")
            continue
        if not (_threads.get(wid) and _threads[wid].is_alive()):
            _arm(wid)
            armed.append(wid)
    return {"ok": True, "armed": armed, **list_runs(limit=20)}
