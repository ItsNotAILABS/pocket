"""Long-lived integrated consoles for agents — PowerShell, WSL, Python CLI.

These are not one-shot shell jobs and not a separate black window the user
has to babysit. Agents own them via session bind + /v1/terminals; the desk
shows the live log tail inside the chat/agent UI.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.tokenomics import burn


def _resolve_cwd(workspace: str = "workspace", cwd: str = "") -> str:
    try:
        from pocket.executor import resolve_cwd

        return resolve_cwd({"workspace": workspace, "cwd": cwd or ""})
    except Exception:
        return cwd or str(Path.home())

ROOT = Path.home() / ".pocket" / "terminals"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_TERMS: Dict[str, "LiveTerminal"] = {}

# All supported console kinds agents can use
KINDS = frozenset(
    {
        "powershell",
        "cmd",
        "wsl",
        "python",
        "python_wsl",
        "py",
        "ipython",
    }
)


def default_wsl_distro() -> str:
    """Prefer Debian, then Ubuntu, then first listed distro."""
    wsl = shutil.which("wsl") or shutil.which("wsl.exe") or ""
    if not wsl:
        return ""
    try:
        p = subprocess.run(
            [wsl, "-l", "-q"],
            capture_output=True,
            timeout=8,
            text=True,
            encoding="utf-16-le",
            errors="replace",
        )
        names = [n.strip().replace("\x00", "") for n in (p.stdout or "").splitlines() if n.strip()]
        # clean weird nulls
        names = [n for n in names if n and n.lower() not in ("windows subsystem for linux",)]
        for prefer in ("Debian", "Ubuntu", "Ubuntu-22.04", "Ubuntu-24.04"):
            for n in names:
                if n.lower() == prefer.lower() or n.lower().startswith(prefer.lower()):
                    return n
        return names[0] if names else ""
    except Exception:
        return "Debian"


def host_python() -> str:
    """Prefer founder arm64 Python, then current interpreter."""
    candidates = [
        Path(r"C:\Users\Medin\AppData\Local\Programs\Python\Python311-arm64\python.exe"),
        Path(sys.executable) if sys.executable else None,
        Path(shutil.which("python") or ""),
        Path(shutil.which("python3") or ""),
    ]
    for c in candidates:
        if c and str(c) and c.is_file():
            return str(c)
    return sys.executable or "python"


class LiveTerminal:
    def __init__(
        self,
        tid: str,
        *,
        kind: str = "powershell",
        cwd: str = "",
        session_id: str = "",
        label: str = "",
        distro: str = "",
    ):
        self.id = tid
        self.kind = _normalize_kind(kind)
        self.cwd = cwd
        self.session_id = session_id
        self.label = label or self.kind
        self.distro = distro or ""
        self.created_at = time.time()
        self.log_path = ROOT / f"{tid}.log"
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._buffer = ""
        self.alive = False
        self.last_cmd = ""
        self.cmd_count = 0

    def start(self) -> None:
        kind = self.kind
        env = {**os.environ}
        # Prevent Python from buffering so agents see output
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        if kind in ("wsl", "python_wsl"):
            distro = self.distro or default_wsl_distro() or "Debian"
            self.distro = distro
            wsl = shutil.which("wsl") or shutil.which("wsl.exe") or "wsl"
            if kind == "python_wsl":
                # Interactive python3 inside WSL (agent-integrated)
                cmd = [
                    wsl,
                    "-d",
                    distro,
                    "--",
                    "bash",
                    "-lc",
                    "cd ~/pocket-wsl 2>/dev/null || mkdir -p ~/pocket-wsl && cd ~/pocket-wsl; "
                    "export PYTHONUNBUFFERED=1; "
                    "exec python3 -u -i -c \"import sys; print('POCKET WSL Python', sys.version.split()[0]); print('cwd ready');\"",
                ]
                # -i alone is cleaner for REPL
                cmd = [wsl, "-d", distro, "--", "bash", "-lc", "cd ~/pocket-wsl 2>/dev/null || (mkdir -p ~/pocket-wsl && cd ~/pocket-wsl); export PYTHONUNBUFFERED=1; exec python3 -u -i"]
            else:
                # Login bash in workspace
                cmd = [
                    wsl,
                    "-d",
                    distro,
                    "--",
                    "bash",
                    "-lc",
                    "mkdir -p ~/pocket-wsl; cd ~/pocket-wsl; "
                    "echo \"[POCKET WSL] distro=$WSL_DISTRO_NAME host=$(hostname) python3=$(python3 --version 2>/dev/null || echo missing)\"; "
                    "exec bash -i",
                ]
        elif kind in ("python", "py", "ipython"):
            py = host_python()
            cmd = [py, "-u", "-i"]
        elif kind == "cmd":
            cmd = ["cmd.exe", "/Q", "/K"]
        else:
            cmd = [
                "powershell.exe",
                "-NoLogo",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
            ]

        banner = (
            f"[POCKET console {self.id} kind={self.kind} "
            f"distro={self.distro or '-'} cwd={self.cwd or '.'}]\n"
            f"[agents use this console — not a separate black window]\n"
        )
        self.log_path.write_text(banner, encoding="utf-8")
        with self._lock:
            self._buffer = banner

        creation = 0
        if sys.platform == "win32":
            # Hide console window — integrated only
            creation = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        self._proc = subprocess.Popen(
            cmd,
            cwd=self.cwd if self.cwd and Path(self.cwd).is_dir() else None,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            env=env,
            creationflags=creation,
        )
        self.alive = True
        t = threading.Thread(target=self._reader, name=f"term-{self.id}", daemon=True)
        t.start()
        time.sleep(0.35)
        # Warm hello so log is never empty
        try:
            if kind in ("python", "py", "ipython"):
                self.write("import sys; print('POCKET host Python', sys.version.split()[0])")
            elif kind == "python_wsl":
                self.write("import sys; print('POCKET WSL Python', sys.version.split()[0])")
            elif kind == "wsl":
                self.write("pwd; which python3; python3 --version 2>/dev/null || true")
            elif kind == "powershell":
                self.write("Write-Host \"POCKET PowerShell ready · $PSVersionTable.PSVersion\"")
        except Exception:
            pass

    def _reader(self) -> None:
        assert self._proc and self._proc.stdout
        while self._proc.poll() is None:
            try:
                data = self._proc.stdout.read(256)
            except Exception:
                break
            if not data:
                break
            text = data.decode("utf-8", errors="replace")
            with self._lock:
                self._buffer = (self._buffer + text)[-120000:]
            try:
                with open(self.log_path, "a", encoding="utf-8", errors="replace") as f:
                    f.write(text)
            except Exception:
                pass
        self.alive = False
        with self._lock:
            self._buffer += "\n[console exited]\n"

    def write(self, text: str) -> None:
        if not self._proc or not self._proc.stdin or self._proc.poll() is not None:
            raise RuntimeError("console not running")
        payload = text if text.endswith("\n") else text + "\n"
        self._proc.stdin.write(payload.encode("utf-8", errors="replace"))
        self._proc.stdin.flush()
        self.last_cmd = text.rstrip()
        self.cmd_count += 1
        with self._lock:
            self._buffer = (self._buffer + f"\n» {text.rstrip()}\n")[-120000:]
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"\n» {text.rstrip()}\n")
        except Exception:
            pass

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            buf = self._buffer
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "distro": self.distro or None,
            "cwd": self.cwd,
            "session_id": self.session_id,
            "alive": self.alive and self._proc is not None and self._proc.poll() is None,
            "pid": self._proc.pid if self._proc else None,
            "log_tail": buf[-40000:],
            "log_path": str(self.log_path),
            "created_at": self.created_at,
            "last_cmd": self.last_cmd,
            "cmd_count": self.cmd_count,
            "agent_integrated": True,
        }

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self.alive = False


def _normalize_kind(kind: str) -> str:
    k = (kind or "powershell").lower().strip().replace("-", "_")
    aliases = {
        "ps": "powershell",
        "pwsh": "powershell",
        "bash": "wsl",
        "linux": "wsl",
        "py": "python",
        "python3": "python",
        "repl": "python",
        "wsl_python": "python_wsl",
        "python-wsl": "python_wsl",
        "ipython": "python",
    }
    k = aliases.get(k, k)
    if k not in KINDS and k not in ("powershell", "cmd", "wsl", "python", "python_wsl"):
        return "powershell"
    return k


def create_terminal(
    *,
    kind: str = "powershell",
    workspace: str = "workspace",
    cwd: str = "",
    session_id: str = "",
    label: str = "",
    distro: str = "",
) -> Dict[str, Any]:
    kind = _normalize_kind(kind)
    path = cwd or _resolve_cwd(workspace, "")
    tid = f"t-{uuid.uuid4().hex[:10]}"
    term = LiveTerminal(
        tid,
        kind=kind,
        cwd=path,
        session_id=session_id,
        label=label or kind,
        distro=distro,
    )
    term.start()
    with _lock:
        _TERMS[tid] = term
    burn("session_open", meta={"terminal": tid, "kind": kind})
    return term.snapshot()


def get_terminal(tid: str) -> Optional[Dict[str, Any]]:
    with _lock:
        t = _TERMS.get(tid)
    return t.snapshot() if t else None


def list_terminals() -> List[Dict[str, Any]]:
    with _lock:
        items = list(_TERMS.values())
    return [t.snapshot() for t in items]


def send_terminal(tid: str, command: str) -> Dict[str, Any]:
    with _lock:
        t = _TERMS.get(tid)
    if not t:
        return {"ok": False, "error": "terminal not found"}
    try:
        t.write(command)
        # Wait a bit longer for WSL/Python REPL output
        time.sleep(0.45 if t.kind in ("wsl", "python", "python_wsl") else 0.25)
        burn("job_shell", meta={"terminal": tid, "interactive": True, "kind": t.kind})
        return {"ok": True, **t.snapshot()}
    except Exception as e:
        return {"ok": False, "error": str(e), **t.snapshot()}


def stop_terminal(tid: str) -> Dict[str, Any]:
    with _lock:
        t = _TERMS.pop(tid, None)
    if not t:
        return {"ok": False, "error": "not found"}
    t.stop()
    return {"ok": True, "id": tid, "status": "stopped"}


def bind_session_terminal(session_id: str) -> Optional[str]:
    """Find terminal linked to a session."""
    with _lock:
        for t in _TERMS.values():
            if t.session_id == session_id and t.alive:
                return t.id
    return None


def ensure_agent_console(
    session_id: str = "",
    *,
    kind: str = "powershell",
    workspace: str = "workspace",
    prefer_existing: bool = True,
) -> Dict[str, Any]:
    """Get or create an integrated console for an agent session."""
    kind = _normalize_kind(kind)
    if prefer_existing and session_id:
        tid = bind_session_terminal(session_id)
        if tid:
            snap = get_terminal(tid)
            if snap and snap.get("alive"):
                # If kind differs and user wants specific kind, create new
                if not kind or snap.get("kind") == kind or kind == "powershell":
                    return {"ok": True, "created": False, **snap}
    return {
        "ok": True,
        "created": True,
        **create_terminal(kind=kind, workspace=workspace, session_id=session_id, label=f"agent-{kind}"),
    }


def agent_run(
    command: str,
    *,
    session_id: str = "",
    kind: str = "powershell",
    wait_ms: int = 600,
) -> Dict[str, Any]:
    """Agent-facing: ensure console of kind, run command, return log tail."""
    cmd = (command or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command"}
    ens = ensure_agent_console(session_id, kind=kind)
    tid = ens.get("id")
    if not tid:
        return {"ok": False, "error": "could not create console", **ens}
    out = send_terminal(tid, cmd)
    if wait_ms > 0:
        time.sleep(min(wait_ms, 5000) / 1000.0)
        fresh = get_terminal(tid) or out
        return {"ok": bool(out.get("ok")), "command": cmd, **fresh}
    return {"ok": bool(out.get("ok")), "command": cmd, **out}


def catalog() -> Dict[str, Any]:
    """What consoles agents can open."""
    distro = default_wsl_distro()
    wsl_ok = bool(shutil.which("wsl") or shutil.which("wsl.exe"))
    return {
        "ok": True,
        "schema": "pocket.agent_console.v1",
        "kinds": [
            {"id": "powershell", "label": "PowerShell", "os": "windows", "available": True},
            {"id": "cmd", "label": "cmd.exe", "os": "windows", "available": True},
            {"id": "python", "label": "Python CLI (host)", "os": "windows", "available": True, "bin": host_python()},
            {
                "id": "wsl",
                "label": f"WSL bash ({distro or 'n/a'})",
                "os": "linux",
                "available": wsl_ok and bool(distro),
                "distro": distro or None,
            },
            {
                "id": "python_wsl",
                "label": f"Python CLI in WSL ({distro or 'n/a'})",
                "os": "linux",
                "available": wsl_ok and bool(distro),
                "distro": distro or None,
            },
        ],
        "live": list_terminals(),
        "doctrine": (
            "Consoles are integrated for agents (hidden process, visible log in desk). "
            "Not a separate black Python window. Prefer python_wsl for Linux packages; "
            "python for host-side arm64 interpreter."
        ),
    }
