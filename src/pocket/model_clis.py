"""Model CLIs that come with every POCKET seat.

Host detects/installs the strong coding agents once.
Spark is Meta Muse Code (`muse`) — never Ollama / Muse Glimmer.
On signup we drop wrappers into the tenant so the user does not install anything.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
HOST_BIN = ROOT / "bin"
SKIP_INSTALL_ENV = "POCKET_SKIP_CLI_INSTALL"

MODEL_CLIS: List[Dict[str, Any]] = [
    {
        "id": "grok",
        "bin": "grok",
        "label": "Grok CLI",
        "group": "model",
        "extra_paths": [Path.home() / ".grok" / "bin" / "grok.exe", Path.home() / ".grok" / "bin" / "grok"],
    },
    {
        "id": "codex",
        "bin": "codex",
        "label": "OpenAI Codex CLI",
        "group": "model",
        "npm": "@openai/codex",
    },
    {
        "id": "claude",
        "bin": "claude",
        "label": "Claude Code CLI",
        "group": "model",
        "npm": "@anthropic-ai/claude-code",
    },
    {
        "id": "gemini",
        "bin": "gemini",
        "label": "Gemini CLI",
        "group": "model",
        "npm": "@google/gemini-cli",
    },
    {
        "id": "qwen",
        "bin": "qwen",
        "label": "Qwen Code CLI",
        "group": "model",
        "npm": "@qwen-code/qwen-code",
    },
    {
        "id": "spark",
        "bin": "ollama",
        "label": "Muse Glimmer (open weights)",
        "group": "model",
        "extra_paths": [Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"],
        "install_hint": "ollama pull muse-glimmer",
        "note": "Meta Muse Glimmer 30B Apache-2.0 open weights via local Ollama",
    },
    {
        "id": "opencode",
        "bin": "opencode",
        "label": "OpenCode CLI",
        "group": "model",
        "npm": "opencode-ai",
    },
    {
        "id": "cursor",
        "bin": "cursor-agent",
        "label": "Cursor Agent CLI",
        "group": "model",
        "extra_paths": [
            Path.home() / ".local" / "bin" / "cursor-agent",
            Path.home() / "AppData" / "Local" / "cursor-agent" / "cursor-agent.exe",
        ],
    },
    {
        "id": "aider",
        "bin": "aider",
        "label": "Aider CLI",
        "group": "model",
        "pip": "aider-chat",
    },
    {
        "id": "copilot",
        "bin": "copilot",
        "label": "GitHub Copilot CLI",
        "group": "model",
        "npm": "@github/copilot",
    },
    {
        "id": "pocket-agent",
        "bin": "pocket-agent",
        "label": "POCKET Agent CLI",
        "group": "model",
        "pip_editable": Path.home() / "OneDrive" / "pocket-agent",
    },
]


def _which(bin_name: str, extra: Optional[List[Path]] = None) -> str:
    w = shutil.which(bin_name) or ""
    if w and not w.lower().endswith(".ps1"):
        return w
    if w.lower().endswith(".ps1"):
        cmd = w[:-4] + ".cmd"
        if os.path.isfile(cmd):
            return cmd
    for p in extra or []:
        if p and Path(p).is_file():
            return str(Path(p))
    if bin_name == "grok":
        cand = Path.home() / ".grok" / "bin" / "grok.exe"
        if cand.is_file():
            return str(cand)
    if bin_name in ("muse", "muse-code"):
        try:
            from pocket.phone_agents import which_muse

            m = which_muse()
            if m:
                return m
        except Exception:
            pass
    host = HOST_BIN / (bin_name + (".cmd" if os.name == "nt" else ""))
    if host.is_file():
        return str(host)
    return w


def detect(spec: Dict[str, Any]) -> Dict[str, Any]:
    path = _which(spec["bin"], spec.get("extra_paths"))
    return {
        "id": spec["id"],
        "bin": spec["bin"],
        "label": spec["label"],
        "group": spec.get("group") or "model",
        "available": bool(path),
        "path": path or None,
        "npm": spec.get("npm") or "",
        "note": spec.get("note") or "",
        "install_hint": spec.get("install_hint") or "",
    }


def inventory() -> Dict[str, Any]:
    tools = [detect(s) for s in MODEL_CLIS]
    return {
        "ok": True,
        "ready": all(t["available"] for t in tools),
        "available": sum(1 for t in tools if t["available"]),
        "count": len(tools),
        "tools": tools,
        "note": "These CLIs are installed on the host. New seats get wrappers in their workspace — no extra install.",
    }


def _write_shim(dest: Path, target: str, bin_name: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        dest.write_text(
            f"@echo off\r\n"
            f"REM POCKET seat shim — {bin_name} on the host\r\n"
            f"\"{target}\" %*\r\n",
            encoding="utf-8",
        )
    else:
        dest.write_text(
            "#!/usr/bin/env bash\n"
            f'exec "{target}" "$@"\n',
            encoding="utf-8",
        )
        try:
            dest.chmod(0o755)
        except Exception:
            pass


def _npm() -> str:
    return shutil.which("npm.cmd") or shutil.which("npm") or ""


def _install_npm(pkg: str) -> Dict[str, Any]:
    npm = _npm()
    if not npm:
        return {"ok": False, "error": "npm not on PATH"}
    try:
        r = subprocess.run(
            [npm, "install", "-g", pkg],
            capture_output=True,
            text=True,
            timeout=240,
        )
        return {
            "ok": r.returncode == 0,
            "error": "" if r.returncode == 0 else ((r.stderr or r.stdout or "")[:300]),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _install_pip(pkg: str) -> Dict[str, Any]:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            capture_output=True,
            text=True,
            timeout=240,
        )
        return {
            "ok": r.returncode == 0,
            "error": "" if r.returncode == 0 else ((r.stderr or r.stdout or "")[:300]),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _install_pocket_agent(src: Path) -> Dict[str, Any]:
    py = sys.executable
    if not src.is_dir():
        return {"ok": False, "error": "pocket-agent checkout missing"}
    try:
        r = subprocess.run(
            [py, "-m", "pip", "install", "-e", str(src), "-q"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {
            "ok": r.returncode == 0,
            "error": "" if r.returncode == 0 else ((r.stderr or r.stdout or "")[:300]),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def ensure_host_clis(*, install: Optional[bool] = None) -> Dict[str, Any]:
    """Make sure model CLIs exist on this machine (used by every seat)."""
    if install is None:
        install = (os.environ.get(SKIP_INSTALL_ENV) or "").strip() not in ("1", "true", "yes")
    HOST_BIN.mkdir(parents=True, exist_ok=True)
    actions = []
    for spec in MODEL_CLIS:
        before = detect(spec)
        if before["available"]:
            actions.append({**before, "action": "present"})
            continue
        if not install:
            actions.append({**before, "action": "skipped"})
            continue
        if spec.get("npm"):
            res = _install_npm(spec["npm"])
            after = detect(spec)
            actions.append({**after, "action": "npm", "install_ok": res.get("ok"), "error": res.get("error")})
        elif spec.get("pip"):
            res = _install_pip(spec["pip"])
            after = detect(spec)
            actions.append({**after, "action": "pip", "install_ok": res.get("ok"), "error": res.get("error")})
        elif spec.get("wsl"):
            actions.append({**before, "action": "wsl-manual", "error": spec.get("install_hint") or "install in WSL"})
        elif spec.get("pip_editable"):
            res = _install_pocket_agent(Path(spec["pip_editable"]))
            after = detect(spec)
            if not after["available"]:
                # wrapper to python -m pocket_agent even if console_script missed PATH
                py = sys.executable
                shim = HOST_BIN / ("pocket-agent.cmd" if os.name == "nt" else "pocket-agent")
                if os.name == "nt":
                    shim.write_text(
                        f"@echo off\r\n\"{py}\" -m pocket_agent %*\r\n",
                        encoding="utf-8",
                    )
                else:
                    shim.write_text(f"#!/usr/bin/env bash\nexec \"{py}\" -m pocket_agent \"$@\"\n", encoding="utf-8")
                after = detect(spec)
            actions.append({**after, "action": "pip", "install_ok": res.get("ok"), "error": res.get("error")})
        else:
            actions.append({**before, "action": "missing"})
    inv = inventory()
    inv["actions"] = actions
    (ROOT / "model_clis.json").write_text(json.dumps(inv, indent=2, default=str), encoding="utf-8")
    return inv


def provision_seat_clis(user: str) -> Dict[str, Any]:
    """Write per-seat wrappers so signup users already have every model CLI."""
    user = (user or "").strip().lower()
    if not user:
        return {"ok": False, "error": "user required"}
    try:
        from pocket.platform_space import tenant_root

        root = tenant_root(user)
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
    bindir = root / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    tools = []
    for spec in MODEL_CLIS:
        det = detect(spec)
        target = det.get("path") or ""
        if not target and spec["id"] == "pocket-agent":
            target = str(HOST_BIN / ("pocket-agent.cmd" if os.name == "nt" else "pocket-agent"))
            if not Path(target).is_file():
                py = sys.executable
                target = ""
                shim_host = HOST_BIN / ("pocket-agent.cmd" if os.name == "nt" else "pocket-agent")
                HOST_BIN.mkdir(parents=True, exist_ok=True)
                shim_host.write_text(
                    f"@echo off\r\n\"{py}\" -m pocket_agent %*\r\n"
                    if os.name == "nt"
                    else f"#!/usr/bin/env bash\nexec \"{py}\" -m pocket_agent \"$@\"\n",
                    encoding="utf-8",
                )
                target = str(shim_host)
                det = detect(spec)
        name = spec["bin"] + (".cmd" if os.name == "nt" else "")
        if det.get("path") or target:
            _write_shim(bindir / name, det.get("path") or target, spec["bin"])
        tools.append({**det, "shim": str(bindir / name)})
    readme = root / "files" / "CLI.md"
    lines = [
        f"# {user} — model CLIs",
        "",
        "These are already installed on this POCKET host. You do not install them yourself.",
        f"Shims live in `{bindir}`.",
        "",
    ]
    for t in tools:
        mark = "ready" if t.get("available") or t.get("shim") else "pending"
        lines.append(f"- **{t['label']}** (`{t['bin']}`) — {mark}")
    lines += [
        "",
        "Internal (no extra CLI): Auro, Guppy, genetic flow — run from the desk.",
        "Spark is Muse Glimmer open weights (`ollama pull muse-glimmer`).",
        "",
    ]
    readme.parent.mkdir(parents=True, exist_ok=True)
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "ok": True,
        "user": user,
        "bin": str(bindir),
        "ready": sum(1 for t in tools if t.get("available") or Path(t.get("shim") or "").is_file()),
        "count": len(tools),
        "tools": tools,
        "at": time.time(),
    }
    (root / "cli.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return payload


def ensure_seat(user: str, *, install_host: bool = False) -> Dict[str, Any]:
    host = inventory()
    if install_host and not host.get("ready"):
        host = ensure_host_clis(install=True)
    seat = provision_seat_clis(user)
    return {"ok": bool(seat.get("ok")), "host": host, "seat": seat}


_bg_started = False
_bg_lock = threading.Lock()


def start_host_cli_install_bg() -> None:
    global _bg_started
    with _bg_lock:
        if _bg_started:
            return
        _bg_started = True

    def _run():
        try:
            ensure_host_clis(install=True)
        except Exception as e:
            print(f"[POCKET] model cli install warn: {e}", flush=True)

    threading.Thread(target=_run, name="pocket-model-clis", daemon=True).start()
