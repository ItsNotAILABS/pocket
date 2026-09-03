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
    if any(w in low for w in ("long work", "team workspace", "agent team")):
        try:
            from pocket.team_workspace import cwd_for

            p = Path(cwd_for())
            if p.is_dir():
                return p
        except Exception:
            pass
    return WS


_DENY = (
    "invoke-expression", "iex ", "downloadstring", "start-process",
    " -enc", "frombase64", "bypass", "remove-item", "rm -", "format ",
    "shutdown", "restart-computer", "stop-computer", "new-service",
    "schtasks", "set-executionpolicy",
)


def _scrub_env() -> Dict[str, str]:
    keep_prefix = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "USERNAME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "OS", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "PROGRAMFILES", "LOCALAPPDATA", "APPDATA")
    out: Dict[str, str] = {}
    for k, v in os.environ.items():
        ku = k.upper()
        if ku.startswith(("GROK_", "OPENAI", "ANTHROPIC", "AWS_", "AZURE_", "GITHUB_", "GH_TOKEN", "POCKET_BASIC", "POCKET_TWIN", "NPM_", "HUGGING", "XAI_")):
            continue
        if any(ku == p or ku.startswith(p) for p in keep_prefix):
            out[k] = v
    out["CI"] = "1"
    out["POCKET_BOUNDED_SHELL"] = "1"
    return out


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
    low = cmd.lower()
    if any(tok in low for tok in _DENY):
        return {"ok": False, "blocked": True, "error": "command not allowed in bounded shell"}
    # HTTP and agents cannot opt out of the destructive blacklist.
    g = guard_shell(cmd, allow_destructive=False)
    if not g.get("ok"):
        return g
    work = resolve_cwd(cwd)
    env = _scrub_env()
    t0 = time.time()
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
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
