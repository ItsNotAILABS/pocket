"""CLI inventory — tools Python agents and LLMs can invoke on the host.

Production apps + CLIs people actually have when they build with AI.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

CLI_CATALOG: List[Dict[str, str]] = [
    {"id": "git", "bin": "git", "label": "Git", "group": "scm"},
    {"id": "gh", "bin": "gh", "label": "GitHub CLI", "group": "scm"},
    {"id": "codex", "bin": "codex", "label": "OpenAI Codex CLI", "group": "ai"},
    {"id": "claude", "bin": "claude", "label": "Claude Code CLI", "group": "ai"},
    {"id": "gemini", "bin": "gemini", "label": "Gemini CLI", "group": "ai-free-usage"},
    {"id": "qwen", "bin": "qwen", "label": "Qwen Code", "group": "ai-open"},
    {"id": "opencode", "bin": "opencode", "label": "OpenCode", "group": "ai-open"},
    {"id": "aider", "bin": "aider", "label": "Aider", "group": "ai-open"},
    {"id": "ollama", "bin": "ollama", "label": "Ollama", "group": "ai-local"},
    {"id": "llama", "bin": "llama-cli", "label": "llama.cpp CLI", "group": "ai-local"},
    {"id": "lms", "bin": "lms", "label": "LM Studio CLI", "group": "ai-local"},
    {"id": "goose", "bin": "goose", "label": "Goose", "group": "ai-open"},
    {"id": "openhands", "bin": "openhands", "label": "OpenHands", "group": "ai-open"},
    {"id": "continue", "bin": "cn", "label": "Continue CLI", "group": "ai-open"},
    {"id": "grok", "bin": "grok", "label": "Grok CLI", "group": "ai"},
    {"id": "antigravity", "bin": "antigravity", "label": "Antigravity", "group": "ai"},
    {"id": "cursor", "bin": "cursor", "label": "Cursor CLI", "group": "ai"},
    {"id": "code", "bin": "code", "label": "VS Code CLI", "group": "editor"},
    {"id": "node", "bin": "node", "label": "Node.js", "group": "runtime"},
    {"id": "npm", "bin": "npm", "label": "npm", "group": "runtime"},
    {"id": "python", "bin": "python", "label": "Python", "group": "runtime"},
    {"id": "pip", "bin": "pip", "label": "pip", "group": "runtime"},
    {"id": "docker", "bin": "docker", "label": "Docker CLI", "group": "ops"},
    {"id": "kubectl", "bin": "kubectl", "label": "kubectl", "group": "ops"},
    {"id": "wrangler", "bin": "wrangler", "label": "Cloudflare Wrangler", "group": "ops"},
    {"id": "cloudflared", "bin": "cloudflared", "label": "cloudflared", "group": "ops"},
    {"id": "terraform", "bin": "terraform", "label": "Terraform", "group": "ops"},
    {"id": "cargo", "bin": "cargo", "label": "Rust cargo", "group": "runtime"},
    {"id": "go", "bin": "go", "label": "Go", "group": "runtime"},
    {"id": "powershell", "bin": "powershell", "label": "PowerShell", "group": "shell"},
    {"id": "wsl", "bin": "wsl", "label": "WSL", "group": "shell"},
    {"id": "winget", "bin": "winget", "label": "winget", "group": "shell"},
]


def which_tool(bin_name: str) -> str:
    p = shutil.which(bin_name) or ""
    if p:
        return p
    if bin_name == "grok":
        cand = Path.home() / ".grok" / "bin" / "grok.exe"
        if cand.exists():
            return str(cand)
    if bin_name == "antigravity":
        for c in (
            Path.home() / "AppData" / "Local" / "Programs" / "Antigravity" / "Antigravity.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "antigravity" / "antigravity.exe",
            Path.home() / "AppData" / "Local" / "antigravity" / "antigravity.exe",
        ):
            if c.exists():
                return str(c)
        w = shutil.which("antigravity.cmd") or shutil.which("agy")
        if w:
            return w
    return ""


def inventory() -> Dict[str, Any]:
    tools = []
    for t in CLI_CATALOG:
        path = which_tool(t["bin"])
        tools.append({**t, "available": bool(path), "path": path or None})
    sample_ids = {"git", "gh", "node", "python", "codex", "docker", "gemini", "qwen", "opencode", "ollama", "go"}
    for t in tools:
        if t["available"] and t["id"] in sample_ids:
            try:
                r = subprocess.run(
                    [t["path"] or t["bin"], "--version"],
                    capture_output=True,
                    text=True,
                    timeout=8,
                )
                t["version"] = ((r.stdout or r.stderr or "")[:160]).strip()
            except Exception:
                t["version"] = ""
    return {
        "ok": True,
        "count": len(tools),
        "available": sum(1 for x in tools if x["available"]),
        "ai_available": sum(1 for x in tools if x["available"] and x["group"].startswith("ai")),
        "tools": tools,
        "note": "CLIs on PATH. Authentication and provider credentials remain owned by each host CLI.",
    }


CLI_CATALOG.extend(
    [
        {"id": "rg", "bin": "rg", "label": "ripgrep", "group": "dev"},
        {"id": "curl", "bin": "curl", "label": "curl", "group": "net"},
        {"id": "jq", "bin": "jq", "label": "jq", "group": "dev"},
        {"id": "pnpm", "bin": "pnpm", "label": "pnpm", "group": "runtime"},
        {"id": "yarn", "bin": "yarn", "label": "yarn", "group": "runtime"},
        {"id": "uv", "bin": "uv", "label": "uv", "group": "runtime"},
        {"id": "npx", "bin": "npx", "label": "npx", "group": "runtime"},
        {"id": "pytest", "bin": "pytest", "label": "pytest", "group": "dev"},
        {"id": "ssh", "bin": "ssh", "label": "ssh", "group": "ops"},
        {"id": "scp", "bin": "scp", "label": "scp", "group": "ops"},
    ]
)

_DENY_RE = (
    r"rm\s+-rf\s+[\\/]",
    r"format\s+",
    r"mkfs",
    r"shutdown",
    r"reboot",
    r":\s*\(\)\s*\{",
)


def run_cli(
    bin_name: str,
    args: Optional[List[str]] = None,
    *,
    cwd: str = "",
    timeout: float = 60,
    allow_open_app: bool = False,
) -> Dict[str, Any]:
    """Run a host CLI for agents — stdout capture, no user browser tabs."""
    from pocket.live_events import emit

    bin_name = (bin_name or "").strip()
    args = list(args or [])
    if not bin_name:
        return {"ok": False, "error": "bin required"}

    path = which_tool(bin_name) or shutil.which(bin_name) or ""
    if not path:
        for t in CLI_CATALOG:
            if t["id"] == bin_name.lower():
                path = which_tool(t["bin"])
                bin_name = t["bin"]
                break
    if not path:
        return {"ok": False, "error": f"CLI not found: {bin_name}", "hint": "install or add to PATH"}

    argv = [path] + [str(a) for a in args]
    joined = " ".join(argv)
    import re as _re

    for pat in _DENY_RE:
        if _re.search(pat, joined, _re.I):
            return {"ok": False, "error": "command denied by agent CLI policy", "command": joined[:200]}

    work = cwd or str(Path.home() / ".pocket" / "workspace")
    Path(work).mkdir(parents=True, exist_ok=True)
    emit("cli", f"agent run {bin_name}", agent="CLI", role="python", meta={"args": args[:8]})
    try:
        r = subprocess.run(
            argv,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=max(5.0, min(float(timeout or 60), 300.0)),
            encoding="utf-8",
            errors="replace",
        )
        return {
            "ok": r.returncode == 0,
            "returncode": r.returncode,
            "bin": bin_name,
            "path": path,
            "argv": argv[:20],
            "stdout": (r.stdout or "")[-12000:],
            "stderr": (r.stderr or "")[-4000:],
            "cwd": work,
            "agent_access": True,
            "user_tab": False,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "bin": bin_name}
    except Exception as e:
        return {"ok": False, "error": str(e), "bin": bin_name}


def open_cli_app(tool_id: str) -> Dict[str, Any]:
    """Open associated desktop app — user-facing; prefer run_cli for agents."""
    from pocket.desktop import open_app
    from pocket.live_events import emit

    tid = (tool_id or "").lower().strip()
    emit("cli", f"Open tool/app {tid} (user surface)", agent="cli", role="python")
    mapping = {
        "antigravity": "antigravity",
        "cursor": "cursor",
        "code": "code",
        "vscode": "code",
        "github": "github",
        "gh": "github",
        "docker": "docker",
        "wt": "wt",
        "terminal": "wt",
    }
    app = mapping.get(tid, tid)
    return open_app(app)
