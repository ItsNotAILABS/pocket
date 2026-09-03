"""Screen body — agents inhabit the same SCREEN-KERNEL as the phone.

Not a screenshot tool. The agent *is* the pointer, caret, and named buttons
on the live desktop (or TV / Antigravity HWND).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA = "pocket.screen.body.v1"
ROOT = Path.home() / ".pocket" / "screen_body.json"
VERBS = ("see", "touch", "type_into", "click_name", "cursor", "inhabit", "leave")


def _load() -> Dict[str, Any]:
    if ROOT.is_file():
        try:
            data = json.loads(ROOT.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def _save(data: Dict[str, Any]) -> None:
    ROOT.parent.mkdir(parents=True, exist_ok=True)
    ROOT.write_text(json.dumps(data, indent=2), encoding="utf-8")


def inhabit(agent: str = "coder", *, which: str = "desktop") -> Dict[str, Any]:
    """Claim the live screen as this agent's body."""
    who = (agent or "coder").strip()[:80] or "coder"
    w = (which or "desktop").lower()
    if w in ("portal", "pc", "laptop", "primary", ""):
        w = "desktop"
    rec = {
        "schema": SCHEMA,
        "agent": who,
        "which": w,
        "at": time.time(),
        "verbs": list(VERBS),
        "stream": "pocket.stream.v1",
    }
    blob = _load()
    blob["occupant"] = rec
    history = blob.get("history") or []
    history.append({"agent": who, "which": w, "at": rec["at"]})
    blob["history"] = history[-40:]
    _save(blob)
    from pocket.screen_kernel import see, snapshot

    eyes = see(which=w)
    return {
        "ok": True,
        "schema": SCHEMA,
        "inhabited": True,
        "agent": who,
        "which": w,
        "kernel": snapshot(),
        "see": {k: eyes.get(k) for k in ("ok", "which", "bytes", "via", "geom") if k in eyes},
        "how": "This agent now owns see/touch/type_into/click_name/cursor on that screen.",
    }


def leave(agent: str = "") -> Dict[str, Any]:
    blob = _load()
    occ = blob.get("occupant") or {}
    if agent and occ.get("agent") and occ.get("agent") != agent:
        return {"ok": False, "error": "another agent inhabits the screen", "occupant": occ}
    blob["occupant"] = None
    _save(blob)
    return {"ok": True, "left": True, "was": occ}


def occupant() -> Dict[str, Any]:
    blob = _load()
    occ = blob.get("occupant") or {}
    return {"ok": True, "schema": SCHEMA, "occupant": occ or None, "inhabited": bool(occ)}


def act(
    verb: str = "see",
    *,
    agent: str = "",
    which: str = "",
    nx: float = 0.5,
    ny: float = 0.5,
    text: str = "",
    name: str = "",
    kind: str = "tap",
    submit: bool = False,
) -> Dict[str, Any]:
    """Run a body verb. Inhabit first if this agent is not the occupant."""
    from pocket.screen_kernel import click_name, cursor, see, touch, type_into

    v = (verb or "see").strip().lower()
    occ = (_load().get("occupant") or {})
    who = (agent or occ.get("agent") or "coder")[:80]
    w = (which or occ.get("which") or "desktop").lower()
    if v in ("inhabit", "embody", "enter", "wear"):
        return inhabit(who, which=w)
    if v in ("leave", "exit", "release"):
        return leave(who)
    if not occ or occ.get("agent") != who:
        inhabit(who, which=w)
    t0 = time.time()
    if v in ("see", "look", "eyes"):
        out = see(which=w)
    elif v in ("cursor", "where"):
        out = cursor()
    elif v in ("click_name", "click", "button"):
        out = click_name(name or text)
    elif v in ("type_into", "type", "keys"):
        out = type_into(text, nx=nx, ny=ny, target=w if w in ("desktop", "tv", "anti") else "desktop", submit=submit)
    elif v in ("touch", "tap", "hold", "drag", "hover"):
        out = touch(kind if v == "touch" else v, nx=nx, ny=ny, text=text, target=w if w in ("desktop", "tv", "anti") else "desktop")
    else:
        return {"ok": False, "error": f"unknown body verb {v}", "verbs": list(VERBS)}
    out = dict(out or {})
    out["body"] = SCHEMA
    out["agent"] = who
    out["verb"] = v
    out["ms"] = int((time.time() - t0) * 1000)
    return out


def snapshot() -> Dict[str, Any]:
    from pocket.screen_kernel import snapshot as ksnap

    return {
        "ok": True,
        "schema": SCHEMA,
        "occupant": (_load().get("occupant") or None),
        "kernel": ksnap(),
        "http": [
            "POST /v1/screen/embody",
            "GET /v1/screen/body",
            "POST /v1/screen/body",
        ],
        "mcp": ["screen_embody", "screen_see", "screen_touch", "screen_type", "screen_click"],
        "note": "Agents wear the live PC the same way PhoneAI Portal does.",
    }
