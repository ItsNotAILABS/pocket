"""Bounded shell for Pocket and PhoneAI — never a free host."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.sanity import guard_shell

WS = Path.home() / ".pocket" / "phoneai_ws"

ROOTS: List[Path] = [
    Path.home() / ".pocket",
    Path.home() / "OneDrive" / "pocket-os",
    Path.home() / "OneDrive" / "PhoneAI",
    Path.home() / "OneDrive" / "sovereign_forge_os",
    Path.home() / "OneDrive" / "sovereign_libraries",
]


def allowed_roots() -> List[str]:
    return [str(p) for p in ROOTS if p.exists()]


def resolve_cwd(cwd: str = "") -> Path:
    raw = (cwd or "").strip() or str(WS)
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = WS / p
    p = p.resolve()
    for root in ROOTS:
        try:
            r = root.resolve()
        except Exception:
            continue
        if str(p).lower().startswith(str(r).lower()):
            p.mkdir(parents=True, exist_ok=True)
            return p
    WS.mkdir(parents=True, exist_ok=True)
    return WS.resolve()


def pick_cwd_for_goal(goal: str) -> Path:
    low = (goal or "").lower()
    if "sovereign" in low or "forge" in low:
        cand = Path.home() / "OneDrive" / "sovereign_forge_os"
        if cand.is_dir():
            return cand
    if "phoneai" in low:
        cand = Path.home() / "OneDrive" / "PhoneAI"
        if cand.is_dir():
            return cand
    if "pocket" in low:
        cand = Path.home() / "OneDrive" / "pocket-os"
        if cand.is_dir():
            return cand
    return WS


def run(
    command: str,
    *,
    cwd: str = "",
    timeout: float = 25,
    allow_destructive: bool = False,
) -> Dict[str, Any]:
    cmd = (command or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command"}
    g = guard_shell(cmd, allow_destructive=allow_destructive)
    if not g.get("ok"):
        return g
    work = resolve_cwd(cwd)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GROK_")}
    env["CI"] = "1"
    t0 = time.time()
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            cwd=str(work),
            capture_output=True,
            timeout=max(3, min(float(timeout), 60)),
            env=env,
        )
        out = (r.stdout or b"").decode("utf-8", errors="replace")
        err = (r.stderr or b"").decode("utf-8", errors="replace")
        return {
            "ok": r.returncode == 0,
            "returncode": r.returncode,
            "stdout": out[-12000:],
            "stderr": err[-4000:],
            "ms": int((time.time() - t0) * 1000),
            "cwd": str(work),
            "command": cmd[:500],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "cwd": str(work), "command": cmd[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "cwd": str(work), "command": cmd[:200]}
