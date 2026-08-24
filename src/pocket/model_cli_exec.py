"""Bounded adapters for stable headless AI CLI contracts.

Adapters intentionally use POCKET's existing run_cli policy rather than raw
shell. Auth remains owned by each CLI on the host.
"""
from __future__ import annotations

from typing import Any, Dict

from pocket.cli_tools import run_cli


def invoke(lane: str, prompt: str, *, cwd: str = "", model: str = "", timeout: float = 180) -> Dict[str, Any]:
    lane = (lane or "").strip().lower()
    prompt = (prompt or "").strip()
    if not prompt:
        return {"ok": False, "error": "prompt required"}

    # Stable non-interactive contracts from upstream CLIs.
    if lane in {"gemini", "gemini-cli"}:
        args = ["-p", prompt, "--output-format", "json"]
        if model:
            args += ["--model", model]
        return run_cli("gemini", args, cwd=cwd, timeout=timeout)

    if lane in {"qwen", "qwen-code"}:
        args = ["-p", prompt, "--output-format", "json", "--max-wall-time", f"{int(max(30, min(timeout, 600)))}s"]
        if model:
            args += ["--model", model]
        return run_cli("qwen", args, cwd=cwd, timeout=timeout)

    if lane == "opencode":
        return run_cli("opencode", ["run", prompt], cwd=cwd, timeout=timeout)

    if lane == "ollama":
        selected = model or "qwen3-coder"
        return run_cli("ollama", ["run", selected, prompt], cwd=cwd, timeout=timeout)

    return {"ok": False, "error": f"lane has no stable headless adapter: {lane}"}


def supported() -> Dict[str, Any]:
    return {
        "ok": True,
        "lanes": {
            "gemini-cli": {"headless": True, "structured": True, "auth": "existing CLI session"},
            "qwen-code": {"headless": True, "structured": True, "budgets": True, "auth": "existing CLI session/provider"},
            "opencode": {"headless": True, "structured": False, "auth": "existing provider/local configuration"},
            "ollama": {"headless": True, "structured": False, "auth": "none for local runtime"},
        },
    }
