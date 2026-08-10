"""Proxy + ensure Pocket Voice API (:8790) so the Edge desk never sees "unreachable".

Desk calls same-origin:
  GET  /v1/pocket-voice/health
  POST /v1/pocket-voice/v1/turn/decide
  POST /v1/pocket-voice/ensure
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

VOICE_PORT = int(os.environ.get("POCKET_VOICE_PORT") or "8790")
VOICE_BASE = (os.environ.get("POCKET_VOICE_URL") or f"http://127.0.0.1:{VOICE_PORT}").rstrip("/")


def _port_open(port: int = VOICE_PORT) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


def health() -> Dict[str, Any]:
    try:
        req = urllib.request.Request(f"{VOICE_BASE}/health", method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"raw": raw[:200]}
            data["ok"] = True
            data["proxy"] = True
            data["upstream"] = VOICE_BASE
            return data
    except Exception as e:
        return {
            "ok": False,
            "proxy": True,
            "upstream": VOICE_BASE,
            "error": str(e)[:200],
            "port_open": _port_open(),
        }


def proxy_request(
    method: str,
    subpath: str,
    *,
    body: Optional[Dict[str, Any]] = None,
    timeout: float = 8.0,
) -> Tuple[int, Dict[str, Any]]:
    """Forward to voice API. subpath like /health or /v1/turn/decide."""
    sp = subpath if str(subpath).startswith("/") else f"/{subpath}"
    url = f"{VOICE_BASE}{sp}"
    data = None
    headers = {"Accept": "application/json", "User-Agent": "POCKET-voice-proxy"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=(method or "GET").upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                obj = json.loads(raw) if raw else {}
            except Exception:
                obj = {"raw": raw[:500]}
            if isinstance(obj, dict):
                obj.setdefault("proxy", True)
            return int(r.status), obj if isinstance(obj, dict) else {"ok": True, "data": obj}
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8", errors="replace")
            obj = json.loads(raw) if raw else {"error": str(e)}
        except Exception:
            obj = {"error": str(e)[:200]}
        if isinstance(obj, dict):
            obj["proxy"] = True
        return int(e.code), obj if isinstance(obj, dict) else {"ok": False, "error": str(e)}
    except Exception as e:
        return 502, {"ok": False, "proxy": True, "error": str(e)[:200], "upstream": VOICE_BASE}


def _voice_root() -> Optional[Path]:
    candidates = [
        Path(os.environ.get("POCKET_VOICE_ROOT") or ""),
        Path.home() / "OneDrive" / "pocket-voice-to-text",
        Path(__file__).resolve().parents[3] / "pocket-voice-to-text",
        Path.home() / "OneDrive" / "pocket-os" / ".." / "pocket-voice-to-text",
    ]
    for c in candidates:
        if not c:
            continue
        try:
            p = c.resolve()
        except Exception:
            p = c
        if (p / "server" / "api.js").is_file():
            return p
    return None


def _node_bin() -> Optional[str]:
    import shutil

    n = shutil.which("node")
    if n:
        return n
    for c in (
        Path(os.environ.get("ProgramFiles") or r"C:\Program Files") / "nodejs" / "node.exe",
        Path(os.environ.get("ProgramFiles(x86)") or r"C:\Program Files (x86)") / "nodejs" / "node.exe",
        Path(os.environ.get("LOCALAPPDATA") or "") / "Programs" / "nodejs" / "node.exe",
    ):
        if c and c.is_file():
            return str(c)
    return None


def ensure_voice(*, wait_sec: float = 4.0) -> Dict[str, Any]:
    """Start Pocket Voice if down; return health."""
    h = health()
    if h.get("ok"):
        return {"ok": True, "already": True, "health": h}

    root = _voice_root()
    node = _node_bin()
    if not root or not node:
        return {
            "ok": False,
            "error": "voice root or node not found",
            "root": str(root) if root else None,
            "node": node,
        }

    log_dir = Path.home() / ".pocket"
    log_dir.mkdir(parents=True, exist_ok=True)
    out = open(log_dir / "pocket-voice.log", "a", encoding="utf-8", errors="replace")
    err = open(log_dir / "pocket-voice-err.log", "a", encoding="utf-8", errors="replace")
    env = os.environ.copy()
    env["PORT"] = str(VOICE_PORT)
    env["HOST"] = "0.0.0.0"
    creation = 0
    if sys.platform == "win32":
        creation = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | 0x00000200
    try:
        subprocess.Popen(
            [node, "server/api.js"],
            cwd=str(root),
            env=env,
            stdout=out,
            stderr=err,
            creationflags=creation,
        )
    except Exception as e:
        return {"ok": False, "error": f"start failed: {e}"}

    deadline = time.time() + max(1.0, wait_sec)
    while time.time() < deadline:
        h = health()
        if h.get("ok"):
            return {"ok": True, "started": True, "health": h}
        time.sleep(0.35)
    return {"ok": False, "started": True, "health": health(), "error": "voice started but health timeout"}
