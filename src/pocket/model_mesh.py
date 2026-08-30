"""POCKET model/CLI mesh.

Discovers local/open/free-usage model runtimes, coding-agent CLIs, and the
AURO/MESIE native intelligence family. No provider-specific auth is stored
here; POCKET uses the user's existing local CLI/session credentials.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import importlib.util
import shutil
from typing import Any, Dict, List


@dataclass(frozen=True)
class Lane:
    id: str
    bin: str
    kind: str
    cost: str
    privacy: str
    capabilities: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    env_hint: str = ""
    python_module: str = ""


LANES: tuple[Lane, ...] = (
    Lane("auro", "auro", "native-intelligence-runtime", "local-free", "local", ("spectral", "embed", "foundation", "benchmark", "reason", "research"), ("mesie",), python_module="mesie"),
    Lane("mesie", "mesie", "native-intelligence-runtime", "local-free", "local", ("spectral", "embed", "foundation", "benchmark", "validation", "research"), python_module="mesie"),
    Lane("ollama", "ollama", "local-model-runtime", "local-free", "local", ("chat", "code", "reason", "embed")),
    Lane("llama.cpp", "llama-cli", "local-model-runtime", "local-free", "local", ("chat", "code", "reason"), ("llama",)),
    Lane("lmstudio", "lms", "local-model-runtime", "local-free", "local", ("chat", "code", "reason", "server")),
    Lane("opencode", "opencode", "coding-agent", "free-models-or-byo", "mixed", ("code", "edit", "agent", "mcp", "multi-session")),
    Lane("aider", "aider", "coding-agent", "open-source-byo-or-local", "mixed", ("code", "edit", "git", "test", "voice")),
    Lane("gemini-cli", "gemini", "coding-agent", "account-or-api-quota", "cloud", ("code", "agent", "search", "mcp", "large-context")),
    Lane("qwen-code", "qwen", "coding-agent", "open-source-byo-or-local", "mixed", ("code", "agent", "mcp", "subagents", "teams")),
    Lane("codex", "codex", "coding-agent", "account-or-api", "cloud", ("code", "edit", "agent", "test")),
    Lane("claude", "claude", "coding-agent", "account-or-api", "cloud", ("code", "edit", "agent", "mcp")),
    Lane("grok", "grok", "coding-agent", "account-or-api", "cloud", ("chat", "code", "agent")),
    Lane("continue", "cn", "coding-agent", "open-source-byo-or-local", "mixed", ("code", "agent", "local")),
    Lane("goose", "goose", "coding-agent", "open-source-byo-or-local", "mixed", ("code", "agent", "mcp")),
    Lane("openhands", "openhands", "coding-agent", "open-source-byo-or-local", "mixed", ("code", "agent", "sandbox")),
)


def _resolve(lane: Lane) -> str:
    candidates = (lane.bin,) + lane.aliases
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    if lane.python_module and importlib.util.find_spec(lane.python_module):
        return f"python:{lane.python_module}"
    return ""


def inventory() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lane in LANES:
        path = _resolve(lane)
        row = asdict(lane)
        row["available"] = bool(path)
        row["path"] = path or None
        row["capabilities"] = list(lane.capabilities)
        row["aliases"] = list(lane.aliases)
        out.append(row)
    return out


def route(task: str, *, require_local: bool = False, prefer_free: bool = True) -> Dict[str, Any]:
    low = (task or "").lower()
    wanted = {"chat"}
    if any(x in low for x in ("code", "repo", "bug", "test", "refactor", "build", "deploy")):
        wanted |= {"code", "agent"}
    if any(x in low for x in ("search", "research", "web")):
        wanted.add("research")
    if any(x in low for x in ("mcp", "tool", "connector")):
        wanted.add("mcp")
    if any(x in low for x in ("spectral", "frequency", "signal", "embed", "benchmark", "mesie", "auro")):
        wanted |= {"spectral", "embed", "benchmark"}

    scored = []
    for lane in inventory():
        if not lane["available"]:
            continue
        if require_local and lane["privacy"] != "local":
            continue
        caps = set(lane["capabilities"])
        score = 4 * len(caps & wanted)
        if prefer_free and ("free" in lane["cost"] or "open-source" in lane["cost"]):
            score += 3
        if lane["privacy"] == "local":
            score += 2
        if lane["kind"] == "native-intelligence-runtime" and caps & wanted:
            score += 2
        if "agent" in wanted and lane["kind"] == "coding-agent":
            score += 2
        scored.append((score, lane))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return {
        "ok": bool(scored),
        "task": task,
        "wanted": sorted(wanted),
        "selected": scored[0][1] if scored else None,
        "alternates": [row for _, row in scored[1:6]],
    }


def summary() -> Dict[str, Any]:
    rows = inventory()
    return {
        "ok": True,
        "registered": len(rows),
        "available": sum(1 for r in rows if r["available"]),
        "local_available": sum(1 for r in rows if r["available"] and r["privacy"] == "local"),
        "native_intelligence": [r for r in rows if r["kind"] == "native-intelligence-runtime"],
        "lanes": rows,
    }
