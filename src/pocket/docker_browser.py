"""POCKET ISOLATE — isolated browsers for self-hosted agents.

Primary: Docker Chromium/Chrome with CDP (when Docker is installed).
Fallback: dedicated Edge user-data-dir per session under ~/.pocket/browser_profiles/

Doctrine:
  · One agent session → one isolated browser profile/container
  · Containers die when the KEEP agent / chat session ends
  · Host Edge profile is NEVER shared with isolated agents unless opted in
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "isolate"
PROFILES = ROOT / "browser_profiles"
STATE = ROOT / "browsers.json"
for _d in (ROOT, PROFILES):
    _d.mkdir(parents=True, exist_ok=True)

_lock = Lock()
SCHEMA = "pocket.isolate.v1"
PRODUCT = "POCKET ISOLATE"

# Default image — browserless chromium with CDP
DEFAULT_IMAGE = os.environ.get("POCKET_DOCKER_BROWSER_IMAGE") or "browserless/chrome:latest"
DEFAULT_CDP_BASE = int(os.environ.get("POCKET_DOCKER_BROWSER_PORT_BASE") or "9222")


def _load() -> Dict[str, Any]:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "browsers": {}}


def _save(data: Dict[str, Any]) -> None:
    STATE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def docker_available() -> Dict[str, Any]:
    exe = shutil.which("docker")
    if not exe:
        return {"ok": False, "available": False, "error": "docker not on PATH", "exe": None}
    try:
        p = subprocess.run(
            [exe, "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        ver = (p.stdout or "").strip() or (p.stderr or "")[:80]
        return {
            "ok": p.returncode == 0,
            "available": p.returncode == 0,
            "exe": exe,
            "version": ver,
            "error": None if p.returncode == 0 else (p.stderr or "docker version failed")[:160],
        }
    except Exception as e:
        return {"ok": False, "available": False, "exe": exe, "error": str(e)[:160]}


def _free_port(start: int = DEFAULT_CDP_BASE) -> int:
    for port in range(start, start + 80):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start + int(time.time()) % 1000


def _edge_exe() -> Optional[str]:
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return None


def status() -> Dict[str, Any]:
    d = docker_available()
    with _lock:
        data = _load()
        browsers = list((data.get("browsers") or {}).values())
    live = [b for b in browsers if b.get("status") == "running"]
    return {
        "ok": True,
        "product": PRODUCT,
        "schema": SCHEMA,
        "docker": d,
        "mode": "docker" if d.get("available") else "profile_fallback",
        "browsers": len(browsers),
        "running": len(live),
        "live": live[:20],
        "profiles_dir": str(PROFILES),
        "api": {
            "status": "GET /v1/isolate",
            "start": "POST /v1/isolate/start",
            "stop": "POST /v1/isolate/stop",
            "list": "GET /v1/isolate/list",
        },
        "doctrine": "Isolated browser per agent session; torn down when chat ends.",
    }


def list_browsers() -> Dict[str, Any]:
    with _lock:
        data = _load()
        items = list((data.get("browsers") or {}).values())
    return {"ok": True, "browsers": items, "count": len(items)}


def start(
    *,
    session_id: str = "",
    keep_id: str = "",
    url: str = "about:blank",
    label: str = "",
    prefer: str = "auto",  # auto | docker | profile
) -> Dict[str, Any]:
    """Start an isolated browser bound to a session/KEEP agent."""
    sid = (session_id or keep_id or ("iso-" + uuid.uuid4().hex[:8])).strip()
    bid = "br-" + uuid.uuid4().hex[:10]
    prefer_n = (prefer or "auto").lower()
    dock = docker_available()
    use_docker = prefer_n == "docker" or (prefer_n == "auto" and dock.get("available"))

    if use_docker and dock.get("available"):
        port = _free_port()
        name = f"pocket-iso-{bid[-8:]}"
        exe = dock["exe"]
        try:
            cmd = [
                exe,
                "run",
                "-d",
                "--rm",
                "--name",
                name,
                "-p",
                f"127.0.0.1:{port}:3000",
                "-e",
                "CONNECTION_TIMEOUT=600000",
                DEFAULT_IMAGE,
            ]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if p.returncode != 0:
                # fall through to profile
                use_docker = False
                docker_err = (p.stderr or p.stdout or "docker run failed")[:200]
            else:
                cid = (p.stdout or "").strip()
                rec = {
                    "id": bid,
                    "kind": "docker",
                    "status": "running",
                    "session_id": sid,
                    "keep_id": keep_id or "",
                    "container_id": cid,
                    "container_name": name,
                    "cdp_port": port,
                    "url": url,
                    "label": label or name,
                    "endpoint": f"http://127.0.0.1:{port}",
                    "image": DEFAULT_IMAGE,
                    "started_at": time.time(),
                }
                with _lock:
                    data = _load()
                    data.setdefault("browsers", {})[bid] = rec
                    _save(data)
                # open URL via host edge pointing? browserless uses /?url=
                return {"ok": True, "browser": rec, "product": PRODUCT, "message": f"Docker browser on :{port}"}
        except Exception as e:
            use_docker = False
            docker_err = str(e)[:200]
    else:
        docker_err = dock.get("error") or "docker unavailable"

    # Profile fallback — isolated Edge user-data-dir
    edge = _edge_exe()
    if not edge:
        return {
            "ok": False,
            "error": "no docker and no Edge for profile isolation",
            "docker_error": docker_err,
        }
    profile = PROFILES / sid
    profile.mkdir(parents=True, exist_ok=True)
    port = _free_port(9300)
    try:
        argv = [
            edge,
            f"--user-data-dir={profile}",
            f"--remote-debugging-port={port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--new-window",
            url or "about:blank",
        ]
        proc = subprocess.Popen(
            argv,
            cwd=str(profile),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        rec = {
            "id": bid,
            "kind": "profile",
            "status": "running",
            "session_id": sid,
            "keep_id": keep_id or "",
            "pid": proc.pid,
            "profile": str(profile),
            "cdp_port": port,
            "url": url,
            "label": label or f"edge-{sid[:12]}",
            "endpoint": f"http://127.0.0.1:{port}",
            "started_at": time.time(),
            "docker_fallback_reason": docker_err,
        }
        with _lock:
            data = _load()
            data.setdefault("browsers", {})[bid] = rec
            _save(data)
        return {
            "ok": True,
            "browser": rec,
            "product": PRODUCT,
            "message": f"Isolated Edge profile for {sid} (Docker unavailable)",
            "mode": "profile_fallback",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "docker_error": docker_err}


def stop(browser_id: str = "", *, session_id: str = "", keep_id: str = "") -> Dict[str, Any]:
    """Stop one browser or all for a session/keep agent."""
    stopped = []
    with _lock:
        data = _load()
        browsers = data.get("browsers") or {}
        targets = []
        if browser_id and browser_id in browsers:
            targets = [browser_id]
        else:
            for bid, b in browsers.items():
                if session_id and b.get("session_id") == session_id:
                    targets.append(bid)
                elif keep_id and b.get("keep_id") == keep_id:
                    targets.append(bid)
        for bid in targets:
            b = browsers.get(bid) or {}
            if b.get("kind") == "docker":
                name = b.get("container_name") or ""
                if name and shutil.which("docker"):
                    try:
                        subprocess.run(
                            ["docker", "rm", "-f", name],
                            capture_output=True,
                            timeout=30,
                        )
                    except Exception:
                        pass
            elif b.get("kind") == "profile" and b.get("pid"):
                try:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/PID", str(b["pid"]), "/T", "/F"],
                            capture_output=True,
                            timeout=15,
                        )
                    else:
                        os.kill(int(b["pid"]), 15)
                except Exception:
                    pass
            b["status"] = "stopped"
            b["stopped_at"] = time.time()
            stopped.append(bid)
            # keep record briefly then drop
            browsers.pop(bid, None)
        data["browsers"] = browsers
        _save(data)
    return {"ok": True, "stopped": stopped, "count": len(stopped), "product": PRODUCT}


def stop_for_session(session_id: str) -> Dict[str, Any]:
    return stop(session_id=session_id)
