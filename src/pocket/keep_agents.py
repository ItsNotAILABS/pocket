"""POCKET KEEP — self-hosted agents that keep working until the chat ends.

A KEEP agent is bound to a desk/session (chat). It:
  · runs as a background service loop (LOOMGRAPH pulses + optional skills)
  · owns an isolated Docker/profile browser (POCKET ISOLATE)
  · stops automatically when the session ends, is closed, or max_hours elapses
  · can be reattached via RECALL codes

Doctrine:
  · Work continues while the conversation is alive — not one-shot jobs only
  · Isolation: browser not shared with host profile
  · Honest stop: chat end / close / recall revoke / budget
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "keep"
STATE = ROOT / "agents.json"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_threads: Dict[str, threading.Thread] = {}
_stops: Dict[str, threading.Event] = {}

PRODUCT = "POCKET KEEP"
SCHEMA = "pocket.keep.v1"
PROTOCOL = "POCKET-KEEP/1.0"


def _load() -> Dict[str, Any]:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "agents": {}}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _session_alive(session_id: str) -> bool:
    if not session_id:
        return True  # unbound keep (manual stop only)
    p = Path.home() / ".pocket" / "sessions" / f"{session_id}.json"
    if not p.is_file():
        return False
    try:
        s = json.loads(p.read_text(encoding="utf-8"))
        st = (s.get("status") or "").lower()
        if st in ("closed", "ended", "deleted", "archived"):
            return False
        if s.get("chat_ended") or s.get("ended_at"):
            return False
        return True
    except Exception:
        return p.is_file()


def status() -> Dict[str, Any]:
    with _lock:
        data = _load()
        agents = list((data.get("agents") or {}).values())
        alive_threads = {k: t.is_alive() for k, t in _threads.items()}
    running = [a for a in agents if a.get("status") == "running"]
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "agents": len(agents),
        "running": len(running),
        "threads": alive_threads,
        "live": running[:30],
        "api": {
            "status": "GET /v1/keep",
            "start": "POST /v1/keep/start",
            "stop": "POST /v1/keep/stop",
            "list": "GET /v1/keep/list",
            "tick": "POST /v1/keep/tick",
        },
        "doctrine": "Self-hosted agents keep working until the chat ends; isolated browsers via ISOLATE.",
    }


def list_agents() -> Dict[str, Any]:
    with _lock:
        data = _load()
        items = list((data.get("agents") or {}).values())
    items.sort(key=lambda a: float(a.get("updated_at") or 0), reverse=True)
    return {"ok": True, "agents": items, "count": len(items)}


def get_agent(keep_id: str) -> Dict[str, Any]:
    with _lock:
        data = _load()
        a = (data.get("agents") or {}).get(keep_id)
    if not a:
        return {"ok": False, "error": "unknown keep agent", "id": keep_id}
    return {"ok": True, "agent": a}


def start(
    *,
    session_id: str = "",
    goal: str = "",
    graph_id: str = "default",
    interval_sec: float = 45.0,
    max_hours: float = 4.0,
    with_browser: bool = True,
    browser_url: str = "about:blank",
    label: str = "",
    owner: str = "",
) -> Dict[str, Any]:
    """Start a KEEP agent bound to a chat session (optional but recommended)."""
    kid = "keep-" + uuid.uuid4().hex[:10]
    goal_n = (goal or "Stay productive on this chat until it ends").strip()
    stop = threading.Event()
    now = time.time()
    agent = {
        "id": kid,
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "status": "running",
        "session_id": (session_id or "").strip(),
        "goal": goal_n[:500],
        "graph_id": graph_id or "default",
        "interval_sec": max(15.0, float(interval_sec or 45)),
        "max_until": now + max(0.25, float(max_hours or 4)) * 3600,
        "label": (label or goal_n[:40])[:80],
        "owner": (owner or "pocket").strip().lower(),
        "with_browser": bool(with_browser),
        "browser_id": "",
        "pulses": 0,
        "last_pulse_at": 0,
        "last_result": {},
        "history": [],
        "created_at": now,
        "updated_at": now,
        "stop_reason": "",
    }

    browser_rec = None
    if with_browser:
        try:
            from pocket.docker_browser import start as iso_start

            br = iso_start(
                session_id=session_id or kid,
                keep_id=kid,
                url=browser_url or "about:blank",
                label=f"keep-{kid[-6:]}",
            )
            if br.get("ok"):
                browser_rec = br.get("browser")
                agent["browser_id"] = (browser_rec or {}).get("id") or ""
                agent["browser"] = {
                    "id": agent["browser_id"],
                    "kind": (browser_rec or {}).get("kind"),
                    "endpoint": (browser_rec or {}).get("endpoint"),
                }
        except Exception as e:
            agent["browser_error"] = str(e)[:160]

    with _lock:
        data = _load()
        data.setdefault("agents", {})[kid] = agent
        _save(data)
        _stops[kid] = stop

    def loop():
        emit("keep", f"KEEP {kid} start · session={session_id or 'none'}", agent="KEEP", role="service")
        while not stop.is_set():
            # end conditions
            if time.time() > float(agent.get("max_until") or 0):
                _finish(kid, "max_hours")
                break
            if session_id and not _session_alive(session_id):
                _finish(kid, "chat_ended")
                break

            # pulse: LOOMGRAPH run (bounded)
            pulse_res: Dict[str, Any] = {}
            try:
                from pocket.loomgraph import run as lg_run

                pulse_res = lg_run(
                    goal_n,
                    graph_id=agent.get("graph_id") or "default",
                    max_loops=1,
                    max_nodes=12,
                    author=agent.get("owner") or "keep",
                )
            except Exception as e:
                pulse_res = {"ok": False, "error": str(e)[:160]}

            with _lock:
                data = _load()
                a = (data.get("agents") or {}).get(kid)
                if not a or a.get("status") != "running":
                    break
                a["pulses"] = int(a.get("pulses") or 0) + 1
                a["last_pulse_at"] = time.time()
                a["updated_at"] = time.time()
                a["last_result"] = {
                    "ok": pulse_res.get("ok"),
                    "path": pulse_res.get("path"),
                    "id": pulse_res.get("id"),
                    "ms": pulse_res.get("ms"),
                    "message": (pulse_res.get("message") or "")[:200],
                }
                hist = a.setdefault("history", [])
                hist.append(a["last_result"])
                a["history"] = hist[-40:]
                data["agents"][kid] = a
                _save(data)
                # refresh local agent max_until etc
                agent.update(a)

            # wait interval or stop
            if stop.wait(timeout=float(agent.get("interval_sec") or 45)):
                break

        # cleanup browser
        try:
            from pocket.docker_browser import stop as iso_stop

            iso_stop(keep_id=kid, session_id=session_id or "")
        except Exception:
            pass
        emit("keep", f"KEEP {kid} stopped", agent="KEEP", role="service")

    t = threading.Thread(target=loop, name=f"pocket-keep-{kid[-8:]}", daemon=True)
    with _lock:
        _threads[kid] = t
    t.start()

    return {
        "ok": True,
        "agent": agent,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "message": "KEEP agent running until chat ends (or max hours / stop)",
        "recall_hint": "Mint a RECALL code with POST /v1/recall/mint to reattach later",
    }


def _finish(keep_id: str, reason: str) -> None:
    with _lock:
        data = _load()
        a = (data.get("agents") or {}).get(keep_id)
        if a:
            a["status"] = "stopped"
            a["stop_reason"] = reason
            a["updated_at"] = time.time()
            a["ended_at"] = time.time()
            data["agents"][keep_id] = a
            _save(data)
        ev = _stops.get(keep_id)
        if ev:
            ev.set()


def stop(keep_id: str = "", *, session_id: str = "") -> Dict[str, Any]:
    stopped = []
    with _lock:
        data = _load()
        agents = data.get("agents") or {}
        targets = []
        if keep_id and keep_id in agents:
            targets = [keep_id]
        elif session_id:
            targets = [k for k, a in agents.items() if a.get("session_id") == session_id]
        for kid in targets:
            ev = _stops.get(kid)
            if ev:
                ev.set()
            a = agents.get(kid) or {}
            a["status"] = "stopped"
            a["stop_reason"] = a.get("stop_reason") or "manual_stop"
            a["ended_at"] = time.time()
            a["updated_at"] = time.time()
            agents[kid] = a
            stopped.append(kid)
        data["agents"] = agents
        _save(data)
    for kid in stopped:
        try:
            from pocket.docker_browser import stop as iso_stop

            iso_stop(keep_id=kid)
        except Exception:
            pass
    return {"ok": True, "stopped": stopped, "count": len(stopped)}


def end_chat(session_id: str) -> Dict[str, Any]:
    """Call when a desk chat/session ends — stops all KEEP agents + browsers for it."""
    if not session_id:
        return {"ok": False, "error": "session_id required"}
    # mark session ended on disk
    try:
        p = Path.home() / ".pocket" / "sessions" / f"{session_id}.json"
        if p.is_file():
            s = json.loads(p.read_text(encoding="utf-8"))
            s["chat_ended"] = True
            s["ended_at"] = time.time()
            s["status"] = "closed"
            p.write_text(json.dumps(s, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass
    r = stop(session_id=session_id)
    try:
        from pocket.docker_browser import stop_for_session

        br = stop_for_session(session_id)
    except Exception:
        br = {"ok": False}
    return {
        "ok": True,
        "session_id": session_id,
        "keep": r,
        "browsers": br,
        "message": "Chat ended — KEEP agents and isolated browsers stopped",
    }


def tick(keep_id: str) -> Dict[str, Any]:
    """Force one LOOMGRAPH pulse now (debug / UI)."""
    g = get_agent(keep_id)
    if not g.get("ok"):
        return g
    a = g["agent"]
    if a.get("status") != "running":
        return {"ok": False, "error": "agent not running"}
    try:
        from pocket.loomgraph import run as lg_run

        r = lg_run(a.get("goal") or "", graph_id=a.get("graph_id") or "default", max_loops=1)
        return {"ok": True, "pulse": r, "keep_id": keep_id}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
