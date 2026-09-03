"""POCKET runtime worker — keep host alive with a ~873ms heartbeat.

This is the process Electron (and Launch-POCKET) should run, not a bare
`serve` that can hang on mesh bootstrap. Heartbeat is written every 873ms
to ~/.pocket/runtime_heartbeat.json so the UI/Electron can show "alive".
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

HEART_MS = int(os.environ.get("POCKET_HEART_MS") or "873")
HOST = os.environ.get("POCKET_HOST") or "127.0.0.1"
PORT = int(os.environ.get("POCKET_PORT") or "8787")
ROOT = Path(os.environ.get("POCKET_ROOT") or Path(__file__).resolve().parents[2])
STATE_DIR = Path.home() / ".pocket"
HEART_FILE = STATE_DIR / "runtime_heartbeat.json"
PID_FILE = STATE_DIR / "runtime_worker.pid"

_stop = threading.Event()
_serve_proc: Optional[subprocess.Popen] = None
_beats = 0
_started_at = time.time()


def _write_heart(extra: Optional[Dict[str, Any]] = None) -> None:
    global _beats
    _beats += 1
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": True,
        "ts": time.time(),
        "beat": _beats,
        "interval_ms": HEART_MS,
        "uptime_sec": round(time.time() - _started_at, 2),
        "host": HOST,
        "port": PORT,
        "serve_pid": _serve_proc.pid if _serve_proc and _serve_proc.poll() is None else None,
        "worker_pid": os.getpid(),
        "desk": f"http://{HOST}:{PORT}/desk",
        "landing": f"http://{HOST}:{PORT}/",
    }
    if extra:
        payload.update(extra)
    HEART_FILE.write_text(json.dumps(payload), encoding="utf-8")


def port_open(host: str = HOST, port: int = PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.35):
            return True
    except Exception:
        return False


def http_ok(host: str = HOST, port: int = PORT) -> bool:
    """True only if /health answers (not a hung LISTEN socket)."""
    import urllib.request

    try:
        req = urllib.request.Request(
            f"http://{host}:{port}/health",
            headers={"User-Agent": "pocket-runtime-worker"},
        )
        with urllib.request.urlopen(req, timeout=0.8) as r:
            return int(getattr(r, "status", 200) or 200) == 200
    except Exception:
        return False


def _kill_port_holders() -> None:
    """Drop hung listeners on PORT (Windows)."""
    if sys.platform != "win32":
        return
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        pids = set()
        needle = f":{PORT}"
        for line in out.splitlines():
            if "LISTENING" not in line.upper() and "LISTEN" not in line.upper():
                continue
            if needle not in line:
                continue
            parts = line.split()
            if parts:
                try:
                    pids.add(int(parts[-1]))
                except ValueError:
                    pass
        for pid in pids:
            if pid <= 0 or pid == os.getpid():
                continue
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except Exception:
                pass
    except Exception:
        pass


def _python() -> str:
    return sys.executable


def _listen_pids() -> list:
    pids = []
    if sys.platform != "win32":
        return pids
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        needle = f":{PORT}"
        seen = set()
        for line in out.splitlines():
            if "LISTENING" not in line.upper():
                continue
            if needle not in line:
                continue
            parts = line.split()
            try:
                pid = int(parts[-1])
            except (ValueError, IndexError):
                continue
            if pid > 0 and pid not in seen:
                seen.add(pid)
                pids.append(pid)
    except Exception:
        pass
    return pids


def collapse_extras() -> None:
    """One healthy listener. Drop newer duplicate serves (they cause Portal lag)."""
    pids = _listen_pids()
    if len(pids) <= 1:
        return
    keep = None
    if _serve_proc and _serve_proc.poll() is None and _serve_proc.pid in pids:
        keep = _serve_proc.pid
    else:
        keep = min(pids)
    me = os.getpid()
    for pid in pids:
        if pid in (keep, me):
            continue
        try:
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            pass


def start_serve() -> None:
    global _serve_proc
    if _serve_proc and _serve_proc.poll() is None:
        if http_ok():
            collapse_extras()
        return
    if port_open() and http_ok():
        collapse_extras()
        return
    if port_open() and not http_ok():
        print("[POCKET runtime] hung listener — killing before start", flush=True)
        _kill_port_holders()
        time.sleep(1.0)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["POCKET_AURO_TRAIN"] = env.get("POCKET_AURO_TRAIN") or "0"
    # Mesh hook async — never block first HTTP
    env["POCKET_MESH_HOOK_ASYNC"] = "1"
    # Break away from any parent Job Object (Grok/agent shells kill children
    # when the shell command ends — that looked like a "crashing" Edge app).
    creation = 0
    if sys.platform == "win32":
        creation = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            | 0x01000000  # CREATE_BREAKAWAY_FROM_JOB
            | 0x00000200  # CREATE_NEW_PROCESS_GROUP
            | 0x00000008  # DETACHED_PROCESS
        )
    err_log = STATE_DIR / "serve-child-err.log"
    out_log = STATE_DIR / "serve-child-out.log"
    try:
        out_f = open(out_log, "a", encoding="utf-8", errors="replace")
        err_f = open(err_log, "a", encoding="utf-8", errors="replace")
    except Exception:
        out_f = subprocess.DEVNULL
        err_f = subprocess.DEVNULL
    _serve_proc = subprocess.Popen(
        [_python(), "-u", "-m", "pocket", "serve", "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=str(ROOT),
        env=env,
        stdout=out_f,
        stderr=err_f,
        creationflags=creation,
        close_fds=True,
    )


def heartbeat_loop() -> None:
    fail = 0
    while not _stop.is_set():
        try:
            listening = port_open()
            ok = http_ok() if listening else False
            if not listening or not ok:
                fail += 1
            else:
                fail = 0
            # Require 2 failed checks (~1.7s) before restart to avoid thrash
            if fail >= 2:
                if listening and not ok:
                    print("[POCKET runtime] desk not answering — restart hung host", flush=True)
                    if _serve_proc and _serve_proc.poll() is None:
                        try:
                            _serve_proc.kill()
                        except Exception:
                            pass
                    _kill_port_holders()
                    time.sleep(0.8)
                start_serve()
                fail = 0
            elif ok:
                collapse_extras()
            _write_heart({"port_open": listening, "http_ok": ok, "listeners": len(_listen_pids())})
        except Exception as e:
            try:
                _write_heart({"ok": False, "error": str(e)[:200]})
            except Exception:
                pass
        _stop.wait(HEART_MS / 1000.0)


def run() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    print(f"[POCKET runtime] worker pid={os.getpid()} heart={HEART_MS}ms port={PORT}", flush=True)
    start_serve()
    t = threading.Thread(target=heartbeat_loop, name="pocket-heart-873", daemon=True)
    t.start()
    try:
        while not _stop.is_set():
            # Reap + restart serve if it died
            if _serve_proc is not None and _serve_proc.poll() is not None:
                print(f"[POCKET runtime] serve exited code={_serve_proc.returncode} — restart", flush=True)
                start_serve()
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        _stop.set()
        if _serve_proc and _serve_proc.poll() is None:
            try:
                _serve_proc.terminate()
            except Exception:
                pass
        print("[POCKET runtime] stopped", flush=True)


if __name__ == "__main__":
    run()
