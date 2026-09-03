"""Always-on host runtime — servers that stay inside Pocket and PhoneAI.

The HTTP app is `pocket` on :8787. PhoneAI is a surface on that same host,
not a second listener. A watchdog process (`python -m pocket runtime`)
restarts serve when it dies. Agents on this PC can bring both up.

  GET  /v1/runtime            status of every registered server
  POST /v1/runtime/ensure     start pocket + watchdog if down
  POST /v1/runtime/install    logon scheduled task + Startup shortcut
  python -m pocket ensure
  python -m pocket install
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
HOME = Path.home() / ".pocket"
HEART = HOME / "runtime_heartbeat.json"
WATCH_PID = HOME / "runtime.pid"
LOG = HOME / "host-runtime.log"
PORT = int(os.environ.get("POCKET_PORT") or "8787")
PUBLIC = os.environ.get("POCKET_PUBLIC_URL") or "https://pocket.medinatechlabs.net"
PY = sys.executable

# Surfaces that live on the pocket host (not extra processes)
POCKET_SURFACES = (
    {"id": "desk", "path": "/desk", "name": "POCKET desk"},
    {"id": "phoneai", "path": "/phoneai", "name": "PhoneAI landing"},
    {"id": "phoneai_app", "path": "/phoneai/app", "name": "PhoneAI kernel"},
    {"id": "portal", "path": "/phoneai/portal", "name": "Portal"},
    {"id": "agents", "path": "/agents", "name": "Agents"},
    {"id": "anti", "path": "/phoneai/anti", "name": "Antigravity"},
    {"id": "setup", "path": "/setup", "name": "Setup"},
    {"id": "signup", "path": "/signup", "name": "Sign up"},
    {"id": "install", "path": "/install", "name": "Install hub"},
)


def _log(msg: str) -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _http_ok(path: str = "/health", timeout: float = 1.4) -> bool:
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{PORT}{path}",
            headers={"User-Agent": "pocket-host-runtime"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return int(getattr(r, "status", 200) or 200) == 200
    except Exception:
        return False


def _port_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.35):
            return True
    except Exception:
        return False


def _heart() -> Dict[str, Any]:
    if not HEART.is_file():
        return {}
    try:
        data = json.loads(HEART.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _watchdog_alive() -> bool:
    h = _heart()
    ts = float(h.get("ts") or 0)
    if ts and (time.time() - ts) < 45:
        return True
    if WATCH_PID.is_file():
        try:
            pid = int(WATCH_PID.read_text(encoding="utf-8").strip() or "0")
        except Exception:
            pid = 0
        if pid > 0:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False
            except Exception:
                return False
    return False


def _tunnel_listening() -> bool:
    try:
        out = subprocess.check_output(
            ["tasklist"],
            text=True,
            errors="replace",
            timeout=4,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
        return "cloudflared" in (out or "").lower()
    except Exception:
        return False


def urls() -> Dict[str, str]:
    local = f"http://127.0.0.1:{PORT}"
    pub = PUBLIC.rstrip("/")
    return {
        "local": local,
        "public": pub,
        "desk": f"{local}/desk",
        "phoneai": f"{local}/phoneai",
        "phoneai_app": f"{local}/phoneai/app",
        "setup": f"{local}/setup",
        "signup": f"{local}/signup",
        "install": f"{local}/install",
        "tunnel_phoneai": f"{pub}/phoneai",
        "tunnel_setup": f"{pub}/setup",
        "tunnel_signup": f"{pub}/signup",
        "tunnel_desk": f"{pub}/desk",
    }


def catalog() -> List[Dict[str, Any]]:
    """Servers that belong in the product runtime (not leftover scripts)."""
    pocket_up = _http_ok("/health")
    watch_up = _watchdog_alive()
    tunnel_up = _tunnel_listening()
    u = urls()
    return [
        {
            "id": "pocket",
            "name": "POCKET host",
            "kind": "http",
            "port": PORT,
            "up": pocket_up,
            "port_open": _port_open(),
            "health": "/health",
            "how": "python -m pocket serve --host 0.0.0.0 --port 8787",
            "ensure": "python -m pocket ensure",
            "surfaces": list(POCKET_SURFACES),
            "urls": {"local": u["local"], "public": u["public"]},
            "inside": ["pocket", "phoneai"],
        },
        {
            "id": "watchdog",
            "name": "Runtime watchdog",
            "kind": "supervisor",
            "up": watch_up,
            "heart": str(HEART),
            "how": "python -m pocket runtime",
            "note": "Restarts serve when :8787 stops answering. Required for always-up.",
            "inside": ["pocket", "phoneai"],
        },
        {
            "id": "tunnel",
            "name": "Cloudflare named tunnel",
            "kind": "edge",
            "up": tunnel_up,
            "optional": True,
            "url": u["public"],
            "how": "cloudflared tunnel run (named tunnel on this PC)",
            "note": "Phone / glasses reach PhoneAI through this hostname.",
            "inside": ["pocket", "phoneai"],
        },
    ]


def status() -> Dict[str, Any]:
    servers = catalog()
    pocket = next((s for s in servers if s["id"] == "pocket"), {})
    return {
        "ok": True,
        "schema": "pocket.host_runtime.v1",
        "up": bool(pocket.get("up")),
        "always_on": bool(next((s for s in servers if s["id"] == "watchdog"), {}).get("up")),
        "servers": servers,
        "urls": urls(),
        "install": {
            "cli": "python -m pocket install",
            "page": "/setup",
            "hub": "/install",
            "agent": "POST /v1/runtime/ensure  ·  tool runtime_ensure",
        },
        "agents": {
            "bring_up": "runtime_ensure",
            "status": "runtime_status",
            "install": "runtime_install",
            "cli": "python -m pocket ensure",
        },
    }


def _spawn(argv: List[str], *, pid_file: Optional[Path] = None) -> Dict[str, Any]:
    HOME.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(SRC), env.get("PYTHONPATH", "")])
    env.setdefault("POCKET_PUBLIC_URL", PUBLIC)
    flags = 0
    if os.name == "nt":
        flags = (
            int(getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200))
            | int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))
            | int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
        )
    log_f = open(HOME / "runtime-spawn.log", "a", encoding="utf-8", errors="replace")
    log_f.write(f"\n--- spawn {time.strftime('%Y-%m-%d %H:%M:%S')} {' '.join(argv)}\n")
    log_f.flush()
    p = subprocess.Popen(
        argv,
        cwd=str(ROOT),
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        close_fds=os.name != "nt",
        creationflags=flags,
        start_new_session=(os.name != "nt"),
    )
    if pid_file is not None:
        pid_file.write_text(str(p.pid), encoding="utf-8")
    _log(f"spawned pid={p.pid} {' '.join(argv)}")
    return {"ok": True, "pid": p.pid, "cmd": argv}


def ensure(which: str = "all") -> Dict[str, Any]:
    """Bring named servers up. Safe to call from a live host (no second serve)."""
    want = (which or "all").strip().lower()
    if want in ("", "all", "*"):
        want_ids = ["watchdog", "pocket"]
    else:
        want_ids = [w.strip() for w in want.replace(",", " ").split() if w.strip()]
    actions: List[Dict[str, Any]] = []
    pocket_up = _http_ok("/health")
    watch_up = _watchdog_alive()

    if "watchdog" in want_ids or "runtime" in want_ids:
        if watch_up:
            actions.append({"id": "watchdog", "ok": True, "already": True})
        else:
            r = _spawn([PY, "-u", "-m", "pocket", "runtime"], pid_file=WATCH_PID)
            r["id"] = "watchdog"
            actions.append(r)
            time.sleep(1.2)
            watch_up = _watchdog_alive() or True

    if "pocket" in want_ids or "host" in want_ids or "serve" in want_ids:
        if pocket_up:
            actions.append({"id": "pocket", "ok": True, "already": True, "url": urls()["local"]})
        else:
            if watch_up or _watchdog_alive():
                for _ in range(8):
                    time.sleep(0.6)
                    if _http_ok("/health"):
                        break
            if not _http_ok("/health"):
                r = _spawn([PY, "-u", "-m", "pocket", "runtime"], pid_file=WATCH_PID)
                r["id"] = "pocket"
                r["via"] = "watchdog"
                actions.append(r)
                for _ in range(12):
                    time.sleep(0.5)
                    if _http_ok("/health"):
                        break
            pocket_up = _http_ok("/health")
            if pocket_up and not any(a.get("id") == "pocket" for a in actions):
                actions.append(
                    {
                        "id": "pocket",
                        "ok": True,
                        "via": "watchdog",
                        "url": urls()["local"],
                    }
                )
            elif not pocket_up:
                actions.append(
                    {
                        "id": "pocket",
                        "ok": False,
                        "error": "host did not answer /health",
                        "url": urls()["local"],
                    }
                )

    if "tunnel" in want_ids:
        actions.append(
            {
                "id": "tunnel",
                "ok": _tunnel_listening(),
                "note": "Named tunnel is operator-installed (cloudflared). Status only — agents do not spawn credentials.",
            }
        )

    snap = status()
    snap["ensured"] = actions
    snap["ok"] = bool(snap.get("up")) or any(a.get("ok") for a in actions)
    return snap


def _pythonw() -> str:
    p = Path(PY)
    if p.name.lower() == "python.exe":
        w = p.with_name("pythonw.exe")
        if w.is_file():
            return str(w)
    return PY


def install() -> Dict[str, Any]:
    """Hidden always-on: pythonw watchdog, logon task, Startup. No console window."""
    HOME.mkdir(parents=True, exist_ok=True)
    pyw = _pythonw()
    cmd_path = HOME / "run-pocket-runtime.cmd"
    body = (
        "@echo off\r\n"
        f'cd /d "{ROOT}"\r\n'
        f'set PYTHONPATH={SRC}\r\n'
        f'set POCKET_PUBLIC_URL={PUBLIC}\r\n'
        f'set POCKET_EDITION=founder\r\n'
        f'start "" "{pyw}" -m pocket runtime\r\n'
    )
    cmd_path.write_text(body, encoding="ascii")
    notes: List[str] = [f"wrote {cmd_path}", f"hidden interpreter {pyw}"]

    vbs_path = HOME / "run-pocket-runtime.vbs"
    esc = lambda p: str(p).replace("\\", "\\\\")
    vbs_path.write_text(
        "Set sh = CreateObject(\"Wscript.Shell\")\r\n"
        f'sh.CurrentDirectory = "{esc(ROOT)}"\r\n'
        f'sh.Environment("Process")("PYTHONPATH") = "{esc(SRC)}"\r\n'
        'sh.Environment("Process")("POCKET_EDITION") = "founder"\r\n'
        f'sh.Run """{esc(pyw)}"" -m pocket runtime", 0, False\r\n',
        encoding="ascii",
    )
    notes.append(f"wrote {vbs_path}")

    startup = Path(os.environ.get("APPDATA") or "") / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_cmd = None
    if startup.is_dir():
        startup_cmd = startup / "POCKET-Runtime.vbs"
        startup_cmd.write_text(vbs_path.read_text(encoding="ascii"), encoding="ascii")
        notes.append(f"startup {startup_cmd}")

    task = {"ok": False, "name": "POCKET Runtime"}
    if os.name == "nt":
        try:
            r = subprocess.run(
                [
                    "schtasks",
                    "/Create",
                    "/TN",
                    "POCKET Runtime",
                    "/SC",
                    "ONLOGON",
                    "/RL",
                    "LIMITED",
                    "/F",
                    "/TR",
                    f'wscript.exe //B "{vbs_path}"',
                ],
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            task = {
                "ok": r.returncode == 0,
                "name": "POCKET Runtime",
                "out": ((r.stdout or "") + (r.stderr or ""))[:400],
            }
            notes.append("schtasks " + ("ok" if task["ok"] else "skipped"))
        except Exception as e:
            task = {"ok": False, "name": "POCKET Runtime", "error": str(e)[:200]}

    brought = ensure("all")
    return {
        "ok": True,
        "schema": "pocket.install.always_on.v1",
        "launcher": str(cmd_path),
        "startup": str(startup_cmd) if startup_cmd else None,
        "task": task,
        "notes": notes,
        "runtime": brought,
        "urls": urls(),
        "next": [
            "Keep this PC awake (sleep kills :8787).",
            "Tunnel PhoneAI at " + urls()["tunnel_phoneai"],
            "Create a seat at " + urls()["signup"],
            "Agents call runtime_ensure or `python -m pocket ensure`.",
        ],
    }


def setup_snapshot() -> Dict[str, Any]:
    st = status()
    return {
        "ok": True,
        "steps": [
            {"id": "account", "title": "Create your seat", "href": "/signup", "done": False},
            {
                "id": "host",
                "title": "Bring the host up",
                "href": "/v1/runtime/ensure",
                "done": bool(st.get("up")),
            },
            {
                "id": "always_on",
                "title": "Install always-on",
                "href": "/v1/runtime/install",
                "done": bool(st.get("always_on")),
            },
            {"id": "desk", "title": "Open POCKET", "href": "/desk", "done": False},
            {"id": "phoneai", "title": "Open PhoneAI", "href": "/phoneai/app", "done": False},
        ],
        "runtime": st,
        "urls": urls(),
    }
