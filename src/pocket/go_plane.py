"""GO — live operating plane.

Holds the active states and working workflows you keep asking for.
Power, multi-workflows, KEEP, Working mode, long workflows, and clouds
all write here. `go()` is the one start that syncs the whole lab.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.go.v1"
ROOT = Path.home() / ".pocket" / "go"
STATE = ROOT / "state.json"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = threading.RLock()

# Surfaces that must always have an active state
SURFACES = (
    "pocket",
    "forge",
    "engine",
    "mesie",
    "nexus",
    "voice",
    "phone",
    "hz",
    "auro",
    "keep",
    "work_mode",
    "long_workflow",
    "power",
    "habitat",
    "screen",
    "billing",
    "phoneai",
    "twin",
    "webmcp",
    "network",
    "antigravity",
    "portal",
    "engines",
    "runtime",
    "agents",
    "agent_arch",
)

LIVE = {"live", "running", "listening", "primary", "ready", "online", "ok"}


def _empty() -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "updated_at": 0.0,
        "go_count": 0,
        "surfaces": {},
        "workflows": {},
        "working": [],
        "armed": [],
        "last_go": None,
        "log": [],
    }


def _load() -> Dict[str, Any]:
    if STATE.is_file():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                base = _empty()
                base.update(data)
                return base
        except Exception:
            pass
    return _empty()


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = time.time()
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, default=str)[:800000], encoding="utf-8")


def _log(data: Dict[str, Any], line: str) -> None:
    data.setdefault("log", []).append({"t": time.time(), "line": line[:240]})
    data["log"] = data["log"][-80:]


def _ensure_workflow_slots(data: Dict[str, Any]) -> None:
    try:
        from pocket.multi_workflows import WORKFLOWS
    except Exception:
        return
    slots = data.setdefault("workflows", {})
    for w in WORKFLOWS:
        wid = w["id"]
        if wid not in slots:
            slots[wid] = {
                "id": wid,
                "title": w["title"],
                "family": w["family"],
                "status": "idle",
                "ok": None,
                "runs": 0,
                "last_ms": None,
                "last_at": None,
                "last_error": "",
            }


def set_surface(name: str, *, status: str, detail: Any = None, url: str = "") -> None:
    with _lock:
        data = _load()
        data.setdefault("surfaces", {})[name] = {
            "id": name,
            "status": status,
            "detail": detail,
            "url": url,
            "updated_at": time.time(),
            "active": status in LIVE,
        }
        _save(data)


def record_workflow(
    wid: str,
    *,
    status: str,
    ok: Optional[bool] = None,
    ms: Optional[int] = None,
    error: str = "",
    title: str = "",
    family: str = "",
) -> None:
    with _lock:
        data = _load()
        _ensure_workflow_slots(data)
        slot = data["workflows"].setdefault(
            wid,
            {
                "id": wid,
                "title": title or wid,
                "family": family,
                "status": "idle",
                "ok": None,
                "runs": 0,
                "last_ms": None,
                "last_at": None,
                "last_error": "",
            },
        )
        if title:
            slot["title"] = title
        if family:
            slot["family"] = family
        slot["status"] = status
        if ok is not None:
            slot["ok"] = ok
        if ms is not None:
            slot["last_ms"] = ms
        if status in ("running", "ok", "fail"):
            slot["last_at"] = time.time()
        if status in ("ok", "fail"):
            slot["runs"] = int(slot.get("runs") or 0) + 1
        if error:
            slot["last_error"] = error[:240]
        working = [k for k, v in data["workflows"].items() if v.get("status") in ("running", "armed")]
        data["working"] = working
        data["armed"] = [k for k, v in data["workflows"].items() if v.get("status") == "armed"]
        _log(data, f"wf {wid} → {status}")
        _save(data)


def arm(wid: str) -> Dict[str, Any]:
    record_workflow(wid, status="armed")
    return {"ok": True, "armed": wid}


def sync() -> Dict[str, Any]:
    """Refresh every active state from the live lab."""
    from pocket.sovereign_stack import computing_clouds

    clouds = computing_clouds()
    for c in clouds.get("clouds") or []:
        set_surface(
            str(c.get("id") or "cloud"),
            status=str(c.get("status") or "unknown"),
            detail=c.get("role") or c.get("name"),
            url=str(c.get("url") or ""),
        )

    try:
        from pocket.keep_agents import status as keep_status

        k = keep_status()
        running = k.get("running") if isinstance(k.get("running"), list) else []
        set_surface("keep", status="running" if running else "idle", detail={"count": len(running)})
    except Exception as e:
        set_surface("keep", status="error", detail=str(e)[:120])

    try:
        from pocket.work_mode import status as work_status

        w = work_status()
        live = int(w.get("live") or 0)
        set_surface("work_mode", status="live" if live else "idle", detail={"live": live, "sessions": w.get("sessions")})
    except Exception as e:
        set_surface("work_mode", status="error", detail=str(e)[:120])

    try:
        from pocket.kernels.long_workflow import list_runs

        lw = list_runs(limit=20)
        runs = lw.get("runs") or lw.get("workflows") or []
        running = [r for r in runs if (r.get("status") or "") == "running"]
        set_surface("long_workflow", status="running" if running else "idle", detail={"running": len(running), "listed": len(runs)})
    except Exception as e:
        set_surface("long_workflow", status="error", detail=str(e)[:120])

    try:
        from pocket.live_desk import desk as live_desk

        d = live_desk(limit=4)
        n = len(d.get("antigravity_threads") or [])
        set_surface("antigravity", status="ready" if n else "idle", detail={"threads": n, "url": "/phoneai/anti"})
        set_surface("phoneai", status="ready", url="/phoneai")
        set_surface("portal", status="ready", url="/phoneai/portal", detail={"modes": ["watch", "touch"], "hd": True})
        try:
            from pocket.agent_social import status as social_status

            ss = social_status()
            set_surface("agents", status="ready", url="/agents", detail={"agents": ss.get("agents"), "groups": ss.get("groups")})
        except Exception as e:
            set_surface("agents", status="error", detail=str(e)[:120])
        try:
            from pocket.engines import catalog as eng_cat

            ec = eng_cat()
            set_surface("engines", status="ready", url="/v1/engines", detail={"ready": (ec.get("ready") or [])[:16]})
        except Exception as e:
            set_surface("engines", status="error", detail=str(e)[:120])
    except Exception as e:
        set_surface("antigravity", status="error", detail=str(e)[:120])

    try:
        from pocket.twin_mint import snapshot as twin_snap

        tw = twin_snap("phoneai")
        set_surface("twin", status="ready" if tw.get("ok") else "idle", detail=tw.get("twin", {}).get("root"))
    except Exception as e:
        set_surface("twin", status="error", detail=str(e)[:120])

    try:
        from pocket.webmcp import catalog as webmcp_cat

        wc = webmcp_cat()
        set_surface("webmcp", status="ready", detail={"actions": wc.get("count")})
        set_surface("network", status="ready", url="/network")
    except Exception as e:
        set_surface("webmcp", status="error", detail=str(e)[:120])

    try:
        from pocket.power import recall

        last = (recall(limit=1).get("runs") or [None])[0]
        set_surface("power", status="ready" if last else "idle", detail=last.get("goal") if last else None)
    except Exception as e:
        set_surface("power", status="error", detail=str(e)[:120])

    try:
        from pocket.agent_habitat import status as hstat

        h = hstat()
        n = h.get("count") or len(h.get("residents") or h.get("agents") or [])
        set_surface("habitat", status="ready" if n else "idle", detail={"residents": n})
    except Exception as e:
        set_surface("habitat", status="error", detail=str(e)[:120])

    try:
        from pocket.screen_share import status as sc

        s = sc()
        set_surface("screen", status=s.get("mode") or "off", detail=s.get("label"))
    except Exception as e:
        set_surface("screen", status="error", detail=str(e)[:120])

    try:
        from itsnotai_internal.billing_sdk import CANONICAL_PLANS

        set_surface("billing", status="ready", detail={"plans": list(CANONICAL_PLANS)})
    except Exception as e:
        set_surface("billing", status="error", detail=str(e)[:120])

    with _lock:
        data = _load()
        _ensure_workflow_slots(data)
        data["working"] = [k for k, v in data["workflows"].items() if v.get("status") in ("running", "armed")]
        data["armed"] = [k for k, v in data["workflows"].items() if v.get("status") == "armed"]
        active = [s for s in (data.get("surfaces") or {}).values() if s.get("active")]
        data["active_count"] = len(active)
        data["workflow_count"] = len(data.get("workflows") or {})
        _save(data)
    return snapshot()


def snapshot() -> Dict[str, Any]:
    with _lock:
        data = _load()
        _ensure_workflow_slots(data)
        surfaces = data.get("surfaces") or {}
        wfs = data.get("workflows") or {}
        by_status: Dict[str, int] = {}
        for v in wfs.values():
            st = v.get("status") or "idle"
            by_status[st] = by_status.get(st, 0) + 1
        return {
            "ok": True,
            "schema": SCHEMA,
            "product": "GO",
            "updated_at": data.get("updated_at"),
            "go_count": data.get("go_count") or 0,
            "active_count": sum(1 for s in surfaces.values() if s.get("active")),
            "surface_count": len(surfaces),
            "workflow_count": len(wfs),
            "working": list(data.get("working") or []),
            "armed": list(data.get("armed") or []),
            "workflow_status": by_status,
            "surfaces": surfaces,
            "workflows": wfs,
            "last_go": data.get("last_go"),
            "log": (data.get("log") or [])[-20:],
            "http": {
                "state": "GET /v1/go",
                "go": "POST /v1/go",
                "tick": "POST /v1/go/tick",
                "ui": "GET /power",
            },
        }


def go(*, arm_daily: bool = True, run_morning: bool = False) -> Dict[str, Any]:
    """One start: sync every active state, arm daily/triple workflows, optional morning run."""
    snap = sync()
    armed: List[str] = []
    if arm_daily:
        try:
            from pocket.multi_workflows import WORKFLOWS

            for w in WORKFLOWS:
                if w["family"] in ("daily", "triple"):
                    arm(w["id"])
                    armed.append(w["id"])
        except Exception:
            pass
    morning = None
    if run_morning:
        try:
            from pocket.power import morning as power_morning

            morning = power_morning()
        except Exception as e:
            morning = {"ok": False, "error": str(e)}
    with _lock:
        data = _load()
        data["go_count"] = int(data.get("go_count") or 0) + 1
        data["last_go"] = {
            "at": time.time(),
            "armed": armed,
            "morning": bool(run_morning),
        }
        _log(data, f"GO #{data['go_count']} armed={len(armed)}")
        _save(data)
    out = snapshot()
    out["just_armed"] = armed
    out["morning"] = morning
    out["ok"] = True
    return out


def tick() -> Dict[str, Any]:
    return sync()


def summarize(g: Optional[Dict[str, Any]] = None) -> str:
    """Human lines for desk agents — not a JSON dump."""
    snap = g if isinstance(g, dict) and g.get("schema") else snapshot()
    lines = [
        f"**GO** — {snap.get('active_count') or 0} surfaces live · "
        f"{snap.get('workflow_count') or 0} workflow slots · "
        f"GO runs: {snap.get('go_count') or 0}.",
    ]
    working = snap.get("working") or []
    armed = snap.get("armed") or []
    if working:
        lines.append("**Working:** " + ", ".join(working[:10]))
    if armed:
        lines.append("**Armed:** " + ", ".join(armed[:12]))
    st = snap.get("workflow_status") or {}
    if st:
        bits = [f"{k}={v}" for k, v in sorted(st.items())]
        lines.append("**Slots:** " + " · ".join(bits))
    live = [s.get("id") for s in (snap.get("surfaces") or {}).values() if s.get("active")]
    if live:
        lines.append("**Live surfaces:** " + ", ".join(live[:16]))
    lines.append("Open `/os` or `/power`. Skills: `go` · `power_do` · `go_state`.")
    return "\n".join(lines)
