"""Damian fleet — internal autonomous keepers for the platform.

Up to 100 Damians. Most are headless background. Some are live. Some are
brains (planning / world / cortex). Some are hearts (care / heartbeat / health).

Users do not need to see them. Operators do — via /v1/damians.

They keep the platform "always working" without stacking user-facing agents.
"""

from __future__ import annotations

import json
import random
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "damians"
STATE = ROOT / "fleet.json"
LOG = ROOT / "pulses.jsonl"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_thread: Optional[threading.Thread] = None
_stop = threading.Event()
_started = False

# Role archetypes — pool we stamp onto individual Damians
ARCHETYPES: List[Dict[str, Any]] = [
    {
        "role": "heart",
        "organ": "heart",
        "headless": True,
        "live": False,
        "duty": "care",
        "blurb": "Host health · voice ensure · runtime heartbeat care",
        "interval_bias": 0.7,
    },
    {
        "role": "brain",
        "organ": "brain",
        "headless": True,
        "live": False,
        "duty": "think",
        "blurb": "World model · dual-loop warm · light planning ticks",
        "interval_bias": 1.2,
    },
    {
        "role": "sentinel",
        "organ": "nerve",
        "headless": True,
        "live": False,
        "duty": "guard",
        "blurb": "Safety policy · port posture · soft threat watch",
        "interval_bias": 1.0,
    },
    {
        "role": "gardener",
        "organ": "hand",
        "headless": True,
        "live": False,
        "duty": "prune",
        "blurb": "Prune snaps · log hygiene · disk keep-alive",
        "interval_bias": 2.0,
    },
    {
        "role": "echo",
        "organ": "voice",
        "headless": True,
        "live": True,
        "duty": "signal",
        "blurb": "Live events · operator signal without user noise",
        "interval_bias": 0.9,
    },
    {
        "role": "oculus",
        "organ": "eye",
        "headless": True,
        "live": False,
        "duty": "see",
        "blurb": "Ensure vision feed · screen share pulse",
        "interval_bias": 1.4,
    },
    {
        "role": "swarm_link",
        "organ": "mesh",
        "headless": True,
        "live": False,
        "duty": "swarm",
        "blurb": "Always-on swarm linkage · pulse when due",
        "interval_bias": 1.5,
    },
    {
        "role": "forge",
        "organ": "hand",
        "headless": True,
        "live": False,
        "duty": "build",
        "blurb": "Engine inventory · CLI presence · tool readiness",
        "interval_bias": 1.8,
    },
    {
        "role": "console_ward",
        "organ": "hand",
        "headless": True,
        "live": False,
        "duty": "console",
        "blurb": "WSL/Python console catalog · agent tool path warm",
        "interval_bias": 2.2,
    },
    {
        "role": "board_clerk",
        "organ": "heart",
        "headless": True,
        "live": False,
        "duty": "board",
        "blurb": "Working board hygiene · needs_you reminders (internal)",
        "interval_bias": 1.6,
    },
    {
        "role": "live_pulse",
        "organ": "heart",
        "headless": False,
        "live": True,
        "duty": "live",
        "blurb": "Visible-to-ops live tick · habitat soft pulse",
        "interval_bias": 0.8,
    },
    {
        "role": "dreamer",
        "organ": "brain",
        "headless": True,
        "live": False,
        "duty": "dream",
        "blurb": "Dream mode / serendipity soft arm",
        "interval_bias": 3.0,
    },
    {
        "role": "capsule",
        "organ": "memory",
        "headless": True,
        "live": False,
        "duty": "memory",
        "blurb": "Time capsules · memory continuity",
        "interval_bias": 2.5,
    },
    {
        "role": "wiki_moth",
        "organ": "brain",
        "headless": True,
        "live": False,
        "duty": "wiki",
        "blurb": "Infinite wiki watcher soft tick",
        "interval_bias": 2.0,
    },
    {
        "role": "mesh_heart",
        "organ": "heart",
        "headless": True,
        "live": True,
        "duty": "mesh",
        "blurb": "HZ / mesh hook soft status",
        "interval_bias": 1.3,
    },
    {
        "role": "sovereign",
        "organ": "nerve",
        "headless": True,
        "live": False,
        "duty": "sovereign",
        "blurb": "Sovereign stack readiness pulse",
        "interval_bias": 2.4,
    },
]


def _default_state() -> Dict[str, Any]:
    return {
        "enabled": True,
        "target_count": 64,  # default fleet size; max 100
        "max_count": 100,
        "interval_sec": 22,
        "max_active_per_pulse": 10,
        "pulses": 0,
        "last_pulse_at": 0.0,
        "last_summary": {},
        "damians": [],
        "internal": True,
        "user_visible": False,
        "created_at": time.time(),
    }


def _load() -> Dict[str, Any]:
    if STATE.exists():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            base = _default_state()
            base.update({k: v for k, v in data.items() if k != "damians" or v})
            if data.get("damians"):
                base["damians"] = data["damians"]
            return base
        except Exception:
            pass
    return _default_state()


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    # Don't dump huge history into main state
    slim = dict(data)
    STATE.write_text(json.dumps(slim, indent=2, default=str)[:2_000_000], encoding="utf-8")


def _log_pulse(rec: Dict[str, Any]) -> None:
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str)[:4000] + "\n")
    except Exception:
        pass


def _mint_damian(index: int, arch: Dict[str, Any]) -> Dict[str, Any]:
    n = index + 1
    return {
        "id": f"damian-{n:03d}",
        "name": f"Damian-{n:03d}",
        "index": n,
        "role": arch["role"],
        "organ": arch.get("organ") or "hand",
        "headless": bool(arch.get("headless", True)),
        "live": bool(arch.get("live", False)),
        "duty": arch.get("duty") or "care",
        "blurb": arch.get("blurb") or "",
        "interval_bias": float(arch.get("interval_bias") or 1.0),
        "status": "idle",
        "pulses": 0,
        "last_pulse_at": 0.0,
        "last_ok": None,
        "last_note": "",
        "created_at": time.time(),
        "internal": True,
    }


def build_fleet(count: int = 48) -> List[Dict[str, Any]]:
    """Create up to 100 Damians with mixed roles (mostly headless)."""
    count = max(1, min(100, int(count)))
    damians: List[Dict[str, Any]] = []
    # Weight: more hearts/brains/sentinels early, gardeners later
    pool = list(ARCHETYPES)
    # Ensure first dozen cover core organs
    core_roles = ["heart", "brain", "sentinel", "echo", "live_pulse", "oculus", "swarm_link", "mesh_heart"]
    core_arch = {a["role"]: a for a in pool}
    for i in range(count):
        if i < len(core_roles) and core_roles[i] in core_arch:
            arch = core_arch[core_roles[i]]
        else:
            # ~85% headless archetypes
            if random.random() < 0.85:
                candidates = [a for a in pool if a.get("headless")]
            else:
                candidates = pool
            arch = candidates[i % len(candidates)]
        damians.append(_mint_damian(i, arch))
    return damians


def arm(*, count: Optional[int] = None, force_rebuild: bool = False) -> Dict[str, Any]:
    """Ensure fleet exists and background loop is running."""
    global _started, _thread
    with _lock:
        data = _load()
        target = count if count is not None else int(data.get("target_count") or 48)
        target = max(1, min(100, int(target)))
        data["target_count"] = target
        data["enabled"] = True
        existing = data.get("damians") or []
        if force_rebuild or len(existing) < target:
            # Grow or rebuild
            if force_rebuild or not existing:
                data["damians"] = build_fleet(target)
            else:
                # append until target
                start = len(existing)
                extra = build_fleet(target)[start:target]
                # re-index extras
                for j, d in enumerate(extra):
                    idx = start + j
                    d["id"] = f"damian-{idx + 1:03d}"
                    d["name"] = f"Damian-{idx + 1:03d}"
                    d["index"] = idx + 1
                data["damians"] = existing + extra
                data["damians"] = data["damians"][:target]
        elif len(existing) > target:
            data["damians"] = existing[:target]
        _save(data)
        _stop.clear()
        if not (_thread and _thread.is_alive()):
            _thread = threading.Thread(target=_loop, name="pocket-damian-fleet", daemon=True)
            _thread.start()
            _started = True
    emit(
        "damians",
        f"fleet armed n={target} (internal keepers)",
        agent="DAMIAN",
        role="daemon",
    )
    return status()


def ensure_running() -> Dict[str, Any]:
    data = _load()
    if not data.get("damians") or not data.get("enabled", True):
        return arm()
    if not (_started and _thread and _thread.is_alive()):
        return arm(count=int(data.get("target_count") or 48))
    return status()


def stop() -> Dict[str, Any]:
    global _started
    with _lock:
        data = _load()
        data["enabled"] = False
        _save(data)
        _stop.set()
        _started = False
    return status()


def status(*, include_all: bool = False) -> Dict[str, Any]:
    data = _load()
    damians = data.get("damians") or []
    by_role: Dict[str, int] = {}
    by_organ: Dict[str, int] = {}
    headless = live = brains = hearts = 0
    for d in damians:
        by_role[d.get("role") or "?"] = by_role.get(d.get("role") or "?", 0) + 1
        by_organ[d.get("organ") or "?"] = by_organ.get(d.get("organ") or "?", 0) + 1
        if d.get("headless"):
            headless += 1
        if d.get("live"):
            live += 1
        if d.get("organ") == "brain":
            brains += 1
        if d.get("organ") == "heart":
            hearts += 1
    sample = damians if include_all else damians[:24]
    alive = _started and _thread is not None and _thread.is_alive()
    return {
        "ok": True,
        "schema": "pocket.damian_fleet.v1",
        "internal": True,
        "user_visible": False,
        "enabled": bool(data.get("enabled")),
        "running": alive and bool(data.get("enabled")),
        "thread_alive": alive,
        "count": len(damians),
        "target_count": data.get("target_count"),
        "max_count": 100,
        "headless": headless,
        "live": live,
        "brains": brains,
        "hearts": hearts,
        "by_role": by_role,
        "by_organ": by_organ,
        "interval_sec": data.get("interval_sec"),
        "max_active_per_pulse": data.get("max_active_per_pulse"),
        "pulses": data.get("pulses"),
        "last_pulse_at": data.get("last_pulse_at"),
        "last_summary": data.get("last_summary"),
        "damians": sample,
        "doctrine": (
            "Damians are internal autonomous keepers. Most headless. "
            "Hearts care for health/voice. Brains warm cognition. "
            "Users need not know; operators use GET /v1/damians."
        ),
    }


def _pulse_one(d: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one Damian duty — soft, never blocks host long."""
    duty = d.get("duty") or "care"
    note = ""
    ok = True
    t0 = time.time()
    try:
        if duty == "care":
            # Heart: health + voice
            try:
                from pocket.voice_proxy import health as vh, ensure_voice

                h = vh()
                if not h.get("ok"):
                    ensure_voice(wait_sec=1.2)
                    h = vh()
                note = f"voice ok={h.get('ok')}"
                ok = bool(h.get("ok"))
            except Exception as e:
                note = f"voice {e}"[:80]
                ok = False
            # heartbeat file touch awareness
            try:
                hf = Path.home() / ".pocket" / "runtime_heartbeat.json"
                note += f" · heart_file={hf.exists()}"
            except Exception:
                pass

        elif duty == "think":
            try:
                from pocket.world_model import status as wm, ensure_db

                ensure_db()
                w = wm()
                note = f"world ok={w.get('ok')} facts={(w.get('counts') or {}).get('facts')}"
            except Exception as e:
                note = f"world {e}"[:80]
            try:
                from pocket.world_model import log_subcortex

                log_subcortex("damian_brain", f"{d.get('id')} think tick")
                note += " · subcortex log"
            except Exception:
                pass

        elif duty == "guard":
            try:
                from pocket.safety import policy_summary

                p = policy_summary()
                note = f"safety keys={len(p) if isinstance(p, dict) else '?'}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "prune":
            # Light prune of old damian pulse log if huge
            try:
                if LOG.exists() and LOG.stat().st_size > 2_000_000:
                    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-500:]
                    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    note = "pruned pulse log"
                else:
                    note = "garden ok"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "signal":
            emit(
                "damians",
                f"{d.get('name')} live signal",
                agent=str(d.get("name") or "DAMIAN"),
                role="damian",
            )
            note = "echoed"

        elif duty == "see":
            try:
                from pocket.live_vision import ensure_vision

                ensure_vision()
                note = "vision armed"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "swarm":
            try:
                from pocket.always_on_swarm import status as ss, ensure_running

                st = ss()
                if not st.get("running"):
                    ensure_running()
                    st = ss()
                note = f"swarm running={st.get('running')} pulses={st.get('pulses')}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "build":
            try:
                from pocket.executor import available_engines

                e = available_engines()
                note = f"codex={e.get('codex')} grok={e.get('grok')} wsl={e.get('wsl')}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "console":
            try:
                from pocket.terminals import catalog

                c = catalog()
                avail = sum(1 for k in (c.get("kinds") or []) if k.get("available"))
                note = f"consoles available={avail}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "board":
            try:
                from pocket.working_board import status as bs

                b = bs()
                c = b.get("counts") or {}
                note = f"board needs_you={c.get('needs_you')} done={c.get('done')}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "live":
            try:
                from pocket.agent_habitat import status as hs

                h = hs()
                note = f"habitat residents={len(h.get('residents') or [])}"
            except Exception as e:
                note = str(e)[:80]
            emit("damians", f"{d.get('name')} live pulse", agent=str(d.get("name")), role="damian")

        elif duty == "dream":
            try:
                from pocket.dream_mode import ensure_running as er

                er()
                note = "dream armed"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "memory":
            try:
                from pocket.time_capsules import ensure_running as er

                er()
                note = "capsules armed"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "wiki":
            try:
                from pocket.infinite_wiki import status as ws

                w = ws()
                note = f"wiki nodes={w.get('nodes')} watcher={w.get('watcher')}"
            except Exception as e:
                note = str(e)[:80]

        elif duty == "mesh":
            try:
                from pocket.hz_mesh import list_lanes

                m = list_lanes()
                note = f"mesh lanes={len(m.get('lanes') or m.get('channels') or []) if isinstance(m, dict) else '?'}"
            except Exception:
                note = "mesh soft"

        elif duty == "sovereign":
            try:
                from pocket.sovereign_stack import stack_status

                s = stack_status()
                note = f"sovereign ok={s.get('ok')}"
            except Exception as e:
                note = str(e)[:80]

        else:
            note = "idle keeper"
    except Exception as e:
        ok = False
        note = f"fault {e}"[:120]

    ms = int((time.time() - t0) * 1000)
    return {
        "id": d.get("id"),
        "role": d.get("role"),
        "duty": duty,
        "ok": ok,
        "note": note,
        "ms": ms,
    }


def pulse_now(*, n: Optional[int] = None) -> Dict[str, Any]:
    """Run one fleet pulse: activate up to N Damians by duty bias."""
    with _lock:
        data = _load()
        damians = data.get("damians") or []
        if not damians:
            return {"ok": False, "error": "fleet empty — call arm"}
        max_n = int(n or data.get("max_active_per_pulse") or 10)
        max_n = max(1, min(20, max_n))
        # Prefer hearts/brains and stale damian
        now = time.time()
        scored = []
        for d in damians:
            age = now - float(d.get("last_pulse_at") or 0)
            bias = float(d.get("interval_bias") or 1.0)
            organ_boost = 1.5 if d.get("organ") in ("heart", "brain") else 1.0
            score = age * organ_boost / max(0.3, bias)
            scored.append((score, d))
        scored.sort(key=lambda x: -x[0])
        chosen = [d for _, d in scored[:max_n]]

    results = []
    for d in chosen:
        r = _pulse_one(d)
        results.append(r)
        d["status"] = "ok" if r.get("ok") else "warn"
        d["pulses"] = int(d.get("pulses") or 0) + 1
        d["last_pulse_at"] = time.time()
        d["last_ok"] = r.get("ok")
        d["last_note"] = r.get("note") or ""

    with _lock:
        data = _load()
        # merge pulse stats back by id
        by_id = {d["id"]: d for d in (data.get("damians") or [])}
        for d in chosen:
            if d["id"] in by_id:
                by_id[d["id"]].update(
                    {
                        "status": d.get("status"),
                        "pulses": d.get("pulses"),
                        "last_pulse_at": d.get("last_pulse_at"),
                        "last_ok": d.get("last_ok"),
                        "last_note": d.get("last_note"),
                    }
                )
        data["damians"] = list(by_id.values()) if by_id else data.get("damians")
        data["pulses"] = int(data.get("pulses") or 0) + 1
        data["last_pulse_at"] = time.time()
        data["last_summary"] = {
            "active": len(results),
            "ok": sum(1 for r in results if r.get("ok")),
            "roles": sorted({r.get("role") for r in results}),
        }
        _save(data)

    _log_pulse({"at": time.time(), "results": results})
    return {
        "ok": True,
        "active": len(results),
        "results": results,
        "summary": data.get("last_summary"),
    }


def _loop() -> None:
    while not _stop.is_set():
        try:
            data = _load()
            if not data.get("enabled"):
                _stop.wait(5)
                continue
            pulse_now()
            interval = max(12, int(data.get("interval_sec") or 22))
        except Exception as e:
            emit("damians", f"fleet loop error {e}", agent="DAMIAN", role="daemon", level="warn")
            interval = 30
        _stop.wait(interval)


def scale(count: int) -> Dict[str, Any]:
    """Resize fleet 1..100 and re-arm."""
    return arm(count=count, force_rebuild=False)
