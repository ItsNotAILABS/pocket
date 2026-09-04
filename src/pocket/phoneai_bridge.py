"""PhoneAI substrate on the POCKET host — no Mongo required.

Implements the PhoneAI Expo client's /api/* contract so the native app
points at :8787 (same Wi-Fi) instead of a separate FastAPI+Mongo stack.
Workspace is ~/.pocket/phoneai_ws (not founder OneDrive).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import platform
import re
import secrets
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / ".pocket" / "phoneai"
WS = Path.home() / ".pocket" / "phoneai_ws"
STATE = ROOT / "state.json"
_lock = Lock()
BOOTED = time.time()
PAIR_TTL = 300
MAX_READ = 512 * 1024
MAX_WRITE = 256 * 1024

TOOLS: List[Dict[str, Any]] = [
    {"id": "substrate_info", "name": "Substrate Info", "category": "System", "icon": "hardware-chip", "description": "Inspect the POCKET host.", "risk": "read", "params": []},
    {"id": "list_directory", "name": "List Directory", "category": "Filesystem", "icon": "folder", "description": "List files in the PhoneAI workspace.", "risk": "read", "params": [{"key": "path", "label": "Path", "type": "text", "placeholder": "."}]},
    {"id": "read_file", "name": "Read File", "category": "Filesystem", "icon": "document", "description": "Read a bounded UTF-8 file.", "risk": "read", "params": [{"key": "path", "label": "Path", "type": "text", "placeholder": "README.md"}]},
    {"id": "write_file", "name": "Write File", "category": "Filesystem", "icon": "create", "description": "Write a bounded UTF-8 file (CONFIRM).", "risk": "write", "danger": True, "confirmation_required": True, "params": [{"key": "path", "label": "Path", "type": "text", "placeholder": "notes/todo.md"}, {"key": "content", "label": "Content", "type": "textarea"}]},
    {"id": "git_status", "name": "Git Status", "category": "VCS", "icon": "git-branch", "description": "git status in workspace.", "risk": "read", "params": [{"key": "path", "label": "Repository", "type": "text", "placeholder": "."}]},
    {"id": "git_log", "name": "Git Log", "category": "VCS", "icon": "list", "description": "git log in workspace.", "risk": "read", "params": [{"key": "path", "label": "Repository", "type": "text", "placeholder": "."}]},
    {"id": "process_list", "name": "Process List", "category": "System", "icon": "pulse", "description": "Inspect processes.", "risk": "read", "params": []},
    {"id": "system_metrics", "name": "System Metrics", "category": "System", "icon": "speedometer", "description": "CPU/disk.", "risk": "read", "params": []},
    {"id": "pocket_status", "name": "POCKET Status", "category": "POCKET", "icon": "planet", "description": "Host heart, CLIs, companion.", "risk": "read", "params": []},
    {"id": "grok_ask", "name": "Grok CLI", "category": "Agents", "icon": "flash", "description": "Run Grok CLI on the host.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "codex_ask", "name": "Codex CLI", "category": "Agents", "icon": "code-slash", "description": "Run Codex CLI on the host.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "spark_ask", "name": "Muse Spark", "category": "Agents", "icon": "flash", "description": "Meta Muse Spark 1.2 via Muse Code CLI (not Ollama).", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "claude_ask", "name": "Claude Code", "category": "Agents", "icon": "code-slash", "description": "Claude Code CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "gemini_ask", "name": "Gemini CLI", "category": "Agents", "icon": "flash", "description": "Gemini CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "opencode_ask", "name": "OpenCode", "category": "Agents", "icon": "code-slash", "description": "OpenCode CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "cursor_ask", "name": "Cursor Agent", "category": "Agents", "icon": "code-slash", "description": "Cursor Agent CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "aider_ask", "name": "Aider", "category": "Agents", "icon": "git-branch", "description": "Aider CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "copilot_ask", "name": "Copilot CLI", "category": "Agents", "icon": "code-slash", "description": "GitHub Copilot CLI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "antigravity", "name": "Antigravity", "category": "Agents", "icon": "planet", "description": "Paste into Antigravity chat and press send.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "spectral_ask", "name": "Spectral", "category": "Agents", "icon": "pulse", "description": "MESIE spectral agent.", "risk": "read", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "physics_ask", "name": "Physics", "category": "Agents", "icon": "speedometer", "description": "Working physics agent.", "risk": "read", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "agi_ask", "name": "AGI", "category": "Agents", "icon": "flash", "description": "Short dense working AGI.", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "imagine", "name": "Imagine", "category": "Create", "icon": "image", "description": "Generate a still (no cap).", "risk": "write", "params": [{"key": "prompt", "label": "Prompt", "type": "textarea"}]},
    {"id": "webmcp_scan", "name": "WebMCP scan", "category": "WebMCP", "icon": "grid", "description": "Diffuse page/app/host into every action PhoneAI can read.", "risk": "read", "params": [{"key": "url", "label": "URL (optional)", "type": "text"}]},
    {"id": "webmcp_list", "name": "WebMCP list", "category": "WebMCP", "icon": "list", "description": "Read the action catalog.", "risk": "read", "params": [{"key": "q", "label": "Filter", "type": "text"}]},
    {"id": "github_sync", "name": "GitHub sync", "category": "VCS", "icon": "cloud-upload", "description": "Commit PhoneAI vault and push to GitHub like Pocket.", "risk": "write", "params": [{"key": "message", "label": "Message", "type": "text", "placeholder": "phoneai"}]},
    {"id": "github_status", "name": "GitHub status", "category": "VCS", "icon": "logo-github", "description": "Where PhoneAI writes on GitHub.", "risk": "read", "params": []},
    {"id": "shell_exec", "name": "Shell", "category": "System", "icon": "terminal", "description": "Bounded PowerShell in Pocket/PhoneAI/sovereign workspaces.", "risk": "write", "danger": True, "confirmation_required": True, "params": [{"key": "command", "label": "Command", "type": "text", "placeholder": "python -m pytest -q"}, {"key": "cwd", "label": "Cwd", "type": "text", "placeholder": ""}]},
    {"id": "harness_run", "name": "Work harness", "category": "Agents", "icon": "git-network", "description": "Think → shell → one engine → receipt.", "risk": "write", "params": [{"key": "goal", "label": "Goal", "type": "textarea"}, {"key": "shell", "label": "Shell (optional)", "type": "text"}]},
    {"id": "eyes_see", "name": "Eyes", "category": "Vision", "icon": "eye", "description": "See Portal or Antigravity frame.", "risk": "read", "params": [{"key": "which", "label": "portal or anti", "type": "text"}]},
    {"id": "runtime_status", "name": "Runtime status", "category": "System", "icon": "pulse", "description": "Are POCKET host and watchdog up?", "risk": "read", "params": []},
    {"id": "runtime_ensure", "name": "Bring host up", "category": "System", "icon": "play", "description": "Start POCKET + watchdog so PhoneAI stays up.", "risk": "write", "params": [{"key": "which", "label": "all / pocket / watchdog", "type": "text"}]},
    {"id": "runtime_install", "name": "Install always-on", "category": "System", "icon": "download", "description": "Logon task + Startup so the host comes back after login.", "risk": "write", "params": []},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    WS.mkdir(parents=True, exist_ok=True)
    readme = WS / "README.md"
    if not readme.exists():
        readme.write_text(
            "# PhoneAI workspace on POCKET\n\nTyped tools from the phone write here, not the founder OneDrive.\n",
            encoding="utf-8",
        )
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"pairings": [], "sessions": {}, "executions": []}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def substrate() -> Dict[str, Any]:
    WS.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(str(WS))
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "workspace_root": str(WS),
        "uptime_seconds": int(time.time() - BOOTED),
        "disk": {"total": disk.total, "used": disk.used, "free": disk.free},
        "capabilities": [t["id"] for t in TOOLS],
        "protocol": "nexus.device-substrate.v1",
        "pocket": True,
        "host": "http://127.0.0.1:8787",
    }


def health() -> Dict[str, Any]:
    return {"status": "ready", "mongo": False, "pocket": True, "substrate": substrate()}


def _resolve(raw: str, *, must_exist: bool = True) -> Path:
    candidate = (WS / (raw or ".")).resolve()
    try:
        candidate.relative_to(WS.resolve())
    except ValueError as exc:
        raise ValueError("path_outside_workspace") from exc
    if must_exist and not candidate.exists():
        raise FileNotFoundError("path_not_found")
    return candidate


def pair_init() -> Dict[str, Any]:
    code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))
    pair_id = str(uuid.uuid4())
    rec = {
        "pair_id": pair_id,
        "code": code,
        "code_hash": hashlib.sha256(code.encode()).hexdigest(),
        "created_at": time.time(),
        "expires_at": time.time() + PAIR_TTL,
        "confirmed": False,
    }
    with _lock:
        data = _load()
        data["pairings"] = [p for p in data.get("pairings") or [] if float(p.get("expires_at") or 0) > time.time()]
        data["pairings"].append(rec)
        _save(data)
    return {
        "pair_id": pair_id,
        "session_id": pair_id,
        "pairing_code": code,
        "expires_at": datetime.fromtimestamp(rec["expires_at"], tz=timezone.utc).isoformat(),
        "substrate": substrate(),
    }


def _mint(device_label: str) -> Dict[str, Any]:
    token = "phoneai_" + secrets.token_urlsafe(32)
    session_id = str(uuid.uuid4())
    with _lock:
        data = _load()
        data.setdefault("sessions", {})[hashlib.sha256(token.encode()).hexdigest()] = {
            "session_id": session_id,
            "device_label": device_label[:80],
            "paired_at": _now(),
            "revoked": False,
        }
        _save(data)
    return {"token": token, "session_id": session_id, "substrate": substrate()}


def pair_confirm(code: str, device_label: str = "phone") -> Dict[str, Any]:
    raw = (code or "").strip().upper()
    h = hashlib.sha256(raw.encode()).hexdigest()
    now = time.time()
    with _lock:
        data = _load()
        hit = None
        for p in data.get("pairings") or []:
            if p.get("code_hash") == h and not p.get("confirmed") and float(p.get("expires_at") or 0) > now:
                hit = p
                break
        if not hit:
            return {"ok": False, "error": "invalid_or_expired_pairing_code", "http": 401}
        hit["confirmed"] = True
        _save(data)
    sess = _mint(device_label or "phone")
    sess["ok"] = True
    return sess


def pair_auto(*, allow: bool = True) -> Dict[str, Any]:
    if not allow:
        return {"ok": False, "error": "auto_pair_disabled", "http": 403}
    sess = _mint("demo-phone")
    sess["ok"] = True
    return sess


def session_from_bearer(authorization: str) -> Optional[Dict[str, Any]]:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    h = hashlib.sha256(token.encode()).hexdigest()
    with _lock:
        data = _load()
        rec = (data.get("sessions") or {}).get(h)
        if rec and not rec.get("revoked"):
            return rec
    return None


def pair_revoke(session: Dict[str, Any]) -> Dict[str, Any]:
    sid = session.get("session_id")
    with _lock:
        data = _load()
        for rec in (data.get("sessions") or {}).values():
            if rec.get("session_id") == sid:
                rec["revoked"] = True
                rec["revoked_at"] = _now()
        _save(data)
    return {"ok": True}


def _run(args: List[str], cwd: Path) -> Tuple[int, str]:
    try:
        r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=8, check=False)
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()[:120000]


def execute_local(tool_id: str, params: Dict[str, Any]) -> Tuple[str, List[str], Dict[str, Any]]:
    if tool_id == "substrate_info":
        data = substrate()
        return "succeeded", [json.dumps(data, sort_keys=True)], data
    if tool_id == "pocket_status":
        from pocket.live_companion import status as live
        from pocket.model_clis import inventory

        data = {"companion": live(), "clis": inventory(), "host": "http://127.0.0.1:8787/phoneai"}
        return "succeeded", ["pocket live"], data
    if tool_id == "list_directory":
        path = _resolve(str(params.get("path") or "."))
        if not path.is_dir():
            raise ValueError("not_a_directory")
        items = []
        for item in sorted(path.iterdir(), key=lambda p: p.name.lower())[:400]:
            st = item.stat()
            items.append({"name": item.name, "kind": "dir" if item.is_dir() else "file", "size": st.st_size})
        return "succeeded", [f"listed {len(items)}"], {"path": str(path), "items": items}
    if tool_id == "read_file":
        path = _resolve(str(params.get("path") or ""))
        if not path.is_file():
            raise ValueError("not_a_file")
        if path.stat().st_size > MAX_READ:
            raise ValueError("file_too_large")
        text = path.read_text(encoding="utf-8", errors="replace")
        return "succeeded", [f"read {len(text)}"], {"path": str(path), "content": text}
    if tool_id == "write_file":
        path = _resolve(str(params.get("path") or ""), must_exist=False)
        content = str(params.get("content") or "")
        encoded = content.encode()
        if len(encoded) > MAX_WRITE:
            raise ValueError("write_too_large")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return "succeeded", [f"wrote {len(encoded)}"], {"path": str(path), "bytes": len(encoded)}
    if tool_id in ("git_status", "git_log"):
        path = _resolve(str(params.get("path") or "."))
        if not (path / ".git").exists():
            raise ValueError("not_a_git_repository")
        args = ["git", "status", "--short", "--branch"] if tool_id == "git_status" else ["git", "log", "--oneline", "-n", "10"]
        rc, output = _run(args, path)
        return ("succeeded" if rc == 0 else "failed"), output.splitlines()[:80], {"exit_code": rc, "output": output}
    if tool_id == "process_list":
        args = ["tasklist"] if os.name == "nt" else ["ps", "-eo", "pid,comm"]
        rc, output = _run(args, WS)
        return ("succeeded" if rc == 0 else "failed"), output.splitlines()[:80], {"exit_code": rc, "output": output[:4000]}
    if tool_id == "system_metrics":
        disk = shutil.disk_usage(str(WS))
        data = {"cpu_count": os.cpu_count(), "disk_free": disk.free, "disk_total": disk.total}
        return "succeeded", [json.dumps(data)], data
    if tool_id == "webmcp_scan":
        from pocket.webmcp import scan

        data = scan(url=str(params.get("url") or ""), fusion=bool(params.get("fusion")))
        return "succeeded", [f"{data.get('count')} actions"], {"count": data.get("count"), "sources": data.get("sources"), "sample": (data.get("actions") or [])[:40]}
    if tool_id == "webmcp_list":
        from pocket.webmcp import find_actions

        hits = find_actions(str(params.get("q") or params.get("prompt") or ""))
        return "succeeded", [f"{len(hits)} hits"], {"actions": hits[:80]}
    if tool_id == "github_status":
        from pocket.phoneai_github import snapshot as gh_snap

        data = gh_snap()
        return "succeeded", [data.get("url") or ""], data
    if tool_id == "eyes_see":
        from pocket.agent_eyes import see as eyes_see

        data = eyes_see(which=str(params.get("which") or "portal"))
        data.pop("base64", None)
        return "succeeded", [data.get("url") or ""], data
    if tool_id == "shell_exec":
        from pocket.shell_exec import run as sh_run

        data = sh_run(str(params.get("command") or params.get("prompt") or ""), cwd=str(params.get("cwd") or ""))
        return ("succeeded" if data.get("ok") else "failed"), [(data.get("stdout") or data.get("error") or "")[:200]], data
    if tool_id == "harness_run":
        from pocket.work_harness import run as harness_run

        data = harness_run(
            str(params.get("goal") or params.get("prompt") or ""),
            shell=str(params.get("shell") or ""),
            cwd=str(params.get("cwd") or ""),
            engine=str(params.get("engine") or "auto"),
        )
        return ("succeeded" if data.get("ok") else "failed"), [data.get("reply") or ""], data
    if tool_id == "runtime_status":
        from pocket.host_runtime import status as runtime_status

        data = runtime_status()
        return "succeeded", ["up" if data.get("up") else "down"], data
    if tool_id == "runtime_ensure":
        from pocket.host_runtime import ensure as runtime_ensure

        data = runtime_ensure(str(params.get("which") or params.get("prompt") or "all"))
        return ("succeeded" if data.get("ok") else "failed"), ["host " + ("up" if data.get("up") else "starting")], data
    if tool_id == "runtime_install":
        from pocket.host_runtime import install as runtime_install

        data = runtime_install()
        return ("succeeded" if data.get("ok") else "failed"), [data.get("launcher") or ""], data
    if tool_id == "github_sync":
        from pocket.phoneai_github import push as gh_push

        data = gh_push(message=str(params.get("message") or params.get("prompt") or "phoneai"))
        return ("succeeded" if data.get("ok") else "failed"), [data.get("url") or data.get("out") or ""], data
    if tool_id in (
        "grok_ask",
        "codex_ask",
        "spark_ask",
        "claude_ask",
        "gemini_ask",
        "opencode_ask",
        "cursor_ask",
        "aider_ask",
        "copilot_ask",
        "antigravity",
        "spectral_ask",
        "physics_ask",
        "agi_ask",
        "imagine",
        "work",
    ):
        engine = {
            "grok_ask": "grok",
            "codex_ask": "codex",
            "spark_ask": "spark",
            "claude_ask": "claude",
            "gemini_ask": "gemini",
            "opencode_ask": "opencode",
            "cursor_ask": "cursor",
            "aider_ask": "aider",
            "copilot_ask": "copilot",
            "antigravity": "antigravity",
            "spectral_ask": "spectral",
            "physics_ask": "physics",
            "agi_ask": "agi",
            "imagine": "imagine",
        }.get(tool_id, "auto")
        prompt = str(params.get("prompt") or params.get("text") or "")
        r = ask_engine(prompt, engine=engine)
        st = "succeeded" if r.get("ok") else "failed"
        return st, [r.get("reply") or r.get("error") or ""], r
    raise ValueError("unknown_tool")


def execute(session: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    tool_id = str(body.get("tool_id") or "")
    tool = next((t for t in TOOLS if t["id"] == tool_id), None)
    if not tool:
        return {"ok": False, "error": "unknown_tool", "http": 404}
    if tool.get("confirmation_required") and str(body.get("confirmation") or "") != "CONFIRM":
        return {"ok": False, "error": "confirmation_required", "http": 409}
    started = time.monotonic()
    started_at = _now()
    try:
        status_value, logs, result = execute_local(tool_id, body.get("params") or {})
        error = None
    except Exception as e:
        status_value, logs, result, error = "failed", [str(e)], {}, str(e)[:200]
    execution_id = str(uuid.uuid4())
    receipt = {
        "schema": "nexus.execution-receipt.v1",
        "request_id": execution_id,
        "component": "phoneai",
        "action": tool_id,
        "status": status_value,
        "session_id": session.get("session_id"),
        "started_at": started_at,
        "finished_at": _now(),
        "duration_ms": int((time.monotonic() - started) * 1000),
        "result": result,
        "error": error,
    }
    payload = json.dumps({k: v for k, v in receipt.items() if k != "digest"}, sort_keys=True, default=str).encode()
    receipt["digest"] = hashlib.sha256(payload).hexdigest()
    doc = {
        "ok": True,
        "execution_id": execution_id,
        "tool_id": tool_id,
        "tool_name": tool["name"],
        "params": body.get("params") or {},
        "session_id": session.get("session_id"),
        "started_at": started_at,
        "created_at": started_at,
        "completed_at": receipt["finished_at"],
        "status": status_value,
        "logs": [{"ts": receipt["finished_at"], "level": "info", "message": line} for line in logs[:80]],
        "report": "",
        "receipt": receipt,
        "stream_path": f"/api/stream/{execution_id}",
    }
    with _lock:
        data = _load()
        data.setdefault("executions", []).insert(0, doc)
        data["executions"] = data["executions"][:80]
        _save(data)
    return doc


def history(session: Dict[str, Any]) -> Dict[str, Any]:
    sid = session.get("session_id")
    with _lock:
        data = _load()
        rows = [e for e in data.get("executions") or [] if e.get("session_id") == sid]
    return {"executions": rows[:50]}


def execution_detail(session: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
    sid = session.get("session_id")
    with _lock:
        data = _load()
        for e in data.get("executions") or []:
            if e.get("execution_id") == execution_id and e.get("session_id") == sid:
                return e
    return {"ok": False, "error": "execution_not_found", "http": 404}


_ENGINE_ALIASES = {
    "anti": "antigravity",
    "agy": "antigravity",
    "muse": "spark",
    "muse-spark": "spark",
    "muse_spark": "spark",
    "glimmer": "spark",
    "life": "life",
    "spectral-agi": "spectral-agi",
    "sagi": "spectral-agi",
    "spectral_agi": "spectral-agi",
    "image": "imagine",
    "img": "imagine",
}

_KNOWN_ENGINES = (
    "grok",
    "codex",
    "antigravity",
    "spark",
    "claude",
    "gemini",
    "qwen",
    "opencode",
    "cursor",
    "aider",
    "copilot",
    "auro-endure",
    "endure",
    "spectral",
    "physics",
    "agi",
    "spectral-agi",
    "sagi",
    "imagine",
    "life",
    "auro",
    "ghost",
    "logic",
    "pattern",
    "heuristic",
    "portal",
    "pocket-agent",
)


def _pick_engine(text: str, engine: str) -> str:
    e = (engine or "auto").strip().lower()
    e = _ENGINE_ALIASES.get(e, e)
    if e in _KNOWN_ENGINES:
        return e
    low = (text or "").lower()
    if "ollama" in low:
        return "spark"
    if any(w in low for w in ("antigravity", "anti gravity", "agy")):
        return "antigravity"
    if any(w in low for w in ("muse spark", "muse code", "spark", "glimmer")):
        return "spark"
    from pocket.phone_life import classify as life_classify

    lk = life_classify(text)
    if lk and lk != "chat":
        return "life"
    if "claude" in low:
        return "claude"
    if "gemini" in low:
        return "gemini"
    if "opencode" in low:
        return "opencode"
    if "cursor" in low:
        return "cursor"
    if "aider" in low:
        return "aider"
    if "copilot" in low:
        return "copilot"
    if any(w in low for w in ("spectral", "mesie", "spectrum", "physics", "free fall", "wavelength", "kinetic")) or re.search(r"\bagi\b", low):
        return "spectral-agi"
    if any(w in low for w in ("generate image", "draw ", "imagine ", "make an image")):
        return "imagine"
    if any(w in low for w in ("codex", "implement", "fix this", "write code", "patch", "test file")):
        return "codex"
    return "grok"


def _cli_env(*, extra_path: str = "") -> Dict[str, str]:
    """Child CLIs must not inherit this Grok session or they deadlock the desk."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GROK_")}
    env["CI"] = "1"
    env.pop("GROK_SESSION_ID", None)
    env.pop("GROK_AGENT", None)
    if extra_path:
        env["PATH"] = extra_path + os.pathsep + env.get("PATH", "")
    return env


def _run_timeout(args: List[str], *, cwd: str, timeout: float, stdin: str = "") -> Tuple[int, str, str]:
    try:
        r = subprocess.run(
            args,
            cwd=cwd,
            input=stdin or None,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            env=_cli_env(),
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)[:200]


def _attach_thread(engine: str, thread_id: str) -> Optional[Dict[str, Any]]:
    """Only resume a thread the user picked. Never auto-attach the live Grok session."""
    tid = (thread_id or "").strip()
    if not tid or tid.startswith(("s-", "pa-")):
        return None
    live = (os.environ.get("GROK_SESSION_ID") or "").strip()
    if live and tid == live:
        return None
    from pocket.live_desk import pick_thread

    th = pick_thread(engine, tid)
    hid = str((th or {}).get("id") or "")
    if live and hid == live:
        return None
    return th


def _local_chat(text: str, thought: Dict[str, Any], where: Dict[str, Any]) -> Dict[str, Any]:
    """Real internal model (Auro/Ghost/Heuristic) — never nested Grok CLI."""
    prefer = str(thought.get("engine") or "")
    try:
        from pocket.engines import internal_reply

        r = internal_reply(text, prefer=prefer if prefer not in ("grok", "auto", "session", "talk") else "")
        r.update(where)
        r.setdefault("why", thought.get("why"))
        return r
    except Exception as e:
        return {
            "ok": True,
            "engine": "phoneai",
            "reply": f"PhoneAI is up ({thought.get('why') or 'ok'}).\n\n{text[:800]}",
            "error": str(e)[:120],
            **where,
        }


def ask_engine(text: str, *, engine: str = "auto", thread_id: str = "", wrap_coder: bool = False) -> Dict[str, Any]:
    """Think, then one engine. Do not resume the live Grok session (that freezes PhoneAI + desk)."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "say something"}
    from pocket.agent_runtime import route_think

    thought = route_think(text, engine)
    if thought.get("tool") == "session_new":
        from pocket.agent_runtime import create_phoneai_session

        r = create_phoneai_session(persona_id="researcher", kind="both", title=text[:80])
        r["route"] = thought
        return r
    if thought.get("tool") == "agent_talk":
        from pocket.agent_runtime import talk

        bits = text.split()
        r = talk(bits[2] if len(bits) > 2 else "phoneai", bits[-1] if bits else "grok", text)
        r["route"] = thought
        return r
    if thought.get("tool") == "twin_mint":
        from pocket.twin_mint import mint

        r = mint("phoneai")
        r["route"] = thought
        r["reply"] = "Twin minted on this PC."
        return r
    if thought.get("tool") == "studio_ship":
        from pocket.agent_network import ship

        r = ship((text.split()[-1] if text.split() else "agent"), "git")
        r["route"] = thought
        return r
    if (engine or "auto") in ("auto", ""):
        chosen = thought.get("engine") if thought.get("engine") in _KNOWN_ENGINES else "grok"
    else:
        chosen = _pick_engine(text, engine)
    if chosen == "grok" and (
        wrap_coder
        or engine in ("coder", "grok_coder")
        or "coder" in str(thought.get("why") or "")
    ):
        try:
            from pocket.coder_persona import wrap_task

            text = wrap_task(text)
        except Exception:
            pass
    th = _attach_thread(chosen if chosen in ("grok", "codex") else engine, thread_id)
    cwd = str((th or {}).get("cwd") or "") or str(WS)
    Path(cwd).mkdir(parents=True, exist_ok=True)
    resume_id = str((th or {}).get("id") or "") if th else ""
    where = {
        "you_are_working_on": (th or {}).get("title") or "new",
        "cwd": cwd,
        "thread_id": resume_id,
        "route": thought,
    }
    if chosen == "antigravity":
        try:
            from pocket.antigravity_chat import handle as anti_handle

            low = text.lower()
            action = "send"
            if any(w in low for w in ("new chat", "new thread", "start over", "new conversation")):
                action = "new"
            elif any(w in low for w in ("continue", "keep going", "click", "notification")):
                action = "continue"
            sent = anti_handle(action, text, cwd=cwd)
            return {
                "ok": bool(sent.get("ok")),
                "engine": "antigravity",
                "reply": sent.get("reply") or sent.get("thread") or "Antigravity updated.",
                "webmcp": sent.get("webmcp"),
                "thread": sent.get("thread") or sent.get("text"),
                "opened": sent.get("opened"),
                **where,
            }
        except Exception as e:
            return {"ok": False, "engine": "antigravity", "error": str(e)[:200], **where}
    if chosen == "life":
        from pocket.phone_life import act as life_act

        r = life_act("auto", text)
        r.setdefault("engine", "life")
        r.update(where)
        return r
    if chosen == "portal":
        r = {
            "ok": True,
            "engine": "portal",
            "reply": "Open Portal on the phone: /phoneai/portal — Watch the real PC or Touch it.",
            "open": "/phoneai/portal",
        }
        r.update(where)
        return r
    if chosen in ("auro-endure", "endure"):
        from pocket.auro_endure import run as endure_run

        r = endure_run(text)
        r.setdefault("engine", "auro-endure")
        r.setdefault("reply", r.get("summary") or r.get("error") or "endure ran")
        r.update(where)
        return r
    if chosen in ("auro", "ghost", "logic", "pattern", "heuristic", "world", "guppy"):
        from pocket.engines import internal_reply

        r = internal_reply(text, prefer=chosen)
        r.update(where)
        return r
    if chosen in (
        "spark",
        "claude",
        "gemini",
        "qwen",
        "opencode",
        "cursor",
        "aider",
        "copilot",
        "spectral",
        "physics",
        "agi",
        "spectral-agi",
        "sagi",
        "imagine",
        "pocket-agent",
    ):
        from pocket.phone_agents import run_agent

        r = run_agent(chosen, text, cwd=cwd)
        r.setdefault("engine", chosen)
        r.update(where)
        if not r.get("ok") or not (r.get("reply") or r.get("image_url")):
            fb = _local_chat(text, thought, where)
            fb["cli"] = {k: r.get(k) for k in ("engine", "error", "ok")}
            return fb
        return r
    if chosen == "codex":
        from pocket.executor import which_codex, _codex_argv

        codex = which_codex()
        if not codex:
            return {"ok": False, "engine": "codex", "error": "Codex CLI is not installed on the host"}
        cmd = _codex_argv(codex) + ["exec", "--skip-git-repo-check", "-C", cwd, "-s", "workspace-write"]
        # Never resume a live Grok/Pocket session id into Codex.
        if resume_id and not resume_id.startswith(("s-", "pa-")) and len(resume_id) > 8:
            cmd += ["resume", resume_id, "-"]
        else:
            cmd += ["-"]
        rc, out, err = _run_timeout(cmd, cwd=cwd, timeout=float(os.environ.get("POCKET_CODEX_TIMEOUT") or "180"), stdin=text[:8000])
        reply = (out or err or "").strip() or f"codex exit {rc}"
        if rc == 124:
            return {"ok": False, "engine": "codex", "error": "Codex timed out — try a shorter ask", "reply": reply[-4000:], **where}
        return {"ok": rc == 0, "engine": "codex", "reply": reply[-8000:], "returncode": rc, **where}
    if chosen == "grok":
        try:
            from pocket.grok_bridge import run_grok_phone, which_grok

            if not which_grok():
                fb = _local_chat(text, thought, where)
                fb["error"] = "Grok CLI is not on PATH"
                fb["engine"] = "grok"
                return fb
            md, err, _eng = run_grok_phone(text, cwd)
            ok = bool((md or "").strip()) and "CLI not found" not in (md or "")
            return {
                "ok": ok,
                "engine": "grok",
                "reply": (md or err or "")[-8000:],
                "error": "" if ok else (err or "grok empty"),
                **where,
            }
        except Exception as e:
            fb = _local_chat(text, thought, where)
            fb["cli"] = str(e)[:200]
            fb["engine"] = "grok"
            return fb
    return _local_chat(text, thought, where)


def work(
    text: str,
    *,
    engine: str = "grok",
    thread_id: str = "",
    cwd: str = "",
    repo: str = "",
    session_id: str = "",
    new: bool = False,
) -> Dict[str, Any]:
    """Code desk only: wired CLI + GitHub/local repo. No personas / RAH / agent attach."""
    from pocket.phoneai_code_desk import run as desk_run

    return desk_run(
        text,
        cli=engine or "grok",
        session_id=session_id or thread_id,
        repo=repo,
        cwd=cwd,
        new=bool(new),
    )


def work_stream_chunks(
    text: str,
    *,
    engine: str = "grok",
    thread_id: str = "",
    cwd: str = "",
    repo: str = "",
    session_id: str = "",
    new: bool = False,
):
    """Yield (event, payload) then a final done dict. Used by SSE."""
    from pocket.phoneai_code_desk import run_stream

    yield from run_stream(
        text,
        cli=engine or "grok",
        session_id=session_id or thread_id,
        repo=repo,
        cwd=cwd,
        new=bool(new),
    )


def how_html() -> str:
    return """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>How to use PhoneAI × POCKET</title>
<style>
body{margin:0;font-family:ui-sans-serif,system-ui;background:#05060a;color:#e4e4e7}
.wrap{max-width:720px;margin:0 auto;padding:28px 18px 80px;line-height:1.55}
h1{color:#fafafa;letter-spacing:-.04em}
h2{color:#34d399;font-size:15px;letter-spacing:.06em;text-transform:uppercase}
a{color:#10a37f} code{background:#121218;padding:2px 6px;border-radius:6px}
.card{border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:14px 16px;margin:12px 0;background:#121218}
</style></head>
<body><div class="wrap">
<p><a href="/phoneai">Kernel home</a> · <a href="/phone">POCKET Phone</a> · <a href="/desk">Desk</a></p>
<h1>How to use PhoneAI with POCKET</h1>
<p>PhoneAI is the <b>phone-native kernel</b>. POCKET on this PC is the <b>host</b> (:8787). They are one product now — the phone talks to Pocket, not a separate Mongo server.</p>

<div class="card">
<h2>1. Fastest — phone browser (same Wi-Fi)</h2>
<p>On the phone open:</p>
<p><code>http://192.168.12.127:8787/phoneai</code></p>
<p>That is the kernel OS (apps grid + floating <b>P</b> Live agent). Sign in at <code>/login</code> if asked. Add to Home Screen for a PWA.</p>
</div>

<div class="card">
<h2>2. POCKET Phone seat</h2>
<p><code>http://192.168.12.127:8787/phone</code> — chat, Aria, work. Same account as desk.</p>
</div>

<div class="card">
<h2>3. Native PhoneAI app (Expo)</h2>
<p>On this PC, in <code>OneDrive/PhoneAI/frontend</code>:</p>
<pre>set EXPO_PUBLIC_BACKEND_URL=http://192.168.12.127:8787
set EXPO_PUBLIC_POCKET_URL=http://192.168.12.127:8787
yarn start</pre>
<p>Scan the QR with Expo Go. Tap <b>AUTO-INITIALIZE</b> (or enter the pair code from <code>POST /api/pair/init</code>). You land on <b>KERNEL</b>. Tools talk to Pocket. The <b>P</b> button is POCKET Live.</p>
</div>

<div class="card">
<h2>What the phone is allowed to do</h2>
<p><b>On the phone:</b> Home is chat, camera, maps, notes, reminders, lists — add to Home Screen. Spark uses <b>Muse Glimmer open weights</b> on this PC (<code>ollama pull muse-glimmer</code>). Desk work is still at <code>/phoneai/work</code> for Grok/Codex/Antigravity.</p>
</div>
</div></body></html>
"""
