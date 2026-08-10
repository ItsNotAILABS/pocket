"""Claude Agent SDK bridge for POCKET desk.

Embeds Claude Code's autonomous agent loop (same harness as Claude Code)
into POCKET jobs: stream tool/text progress into the desk transcript and
emit capability-sandbox receipts for audit.

Fallback: if `claude-agent-sdk` is not installed or the run fails at import/
CLI discovery, callers should fall back to the classic `claude` CLI path.
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def sdk_installed() -> bool:
    try:
        import importlib.util

        return bool(importlib.util.find_spec("claude_agent_sdk"))
    except Exception:
        return False


def status() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": True,
        "sdk_installed": sdk_installed(),
        "package": "claude-agent-sdk",
        "engine": "claude-agent-sdk",
        "auth": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")),
    }
    try:
        from pocket.executor import which_claude

        out["cli"] = bool(which_claude())
        out["cli_path"] = which_claude() or None
    except Exception:
        out["cli"] = False
        out["cli_path"] = None
    out["ready"] = out["sdk_installed"] and (out["auth"] or out["cli"])
    return out


def _message_text(msg: Any) -> str:
    """Best-effort extract human text from an SDK message object."""
    parts: List[str] = []
    # ResultMessage
    if hasattr(msg, "result") and isinstance(getattr(msg, "result"), str):
        if msg.result.strip():
            return msg.result.strip()
    content = getattr(msg, "content", None)
    if content is None:
        # some messages expose .text
        t = getattr(msg, "text", None)
        if isinstance(t, str) and t.strip():
            return t.strip()
        return ""
    if isinstance(content, str):
        return content.strip()
    for block in content or []:
        btype = getattr(block, "type", None) or type(block).__name__
        if hasattr(block, "text") and getattr(block, "text"):
            parts.append(str(block.text))
        elif btype in ("tool_use", "ToolUseBlock") or type(block).__name__ == "ToolUseBlock":
            name = getattr(block, "name", None) or getattr(block, "tool_name", "tool")
            inp = getattr(block, "input", None) or getattr(block, "tool_input", {}) or {}
            summary = ""
            if isinstance(inp, dict):
                for k in ("command", "file_path", "path", "pattern", "query"):
                    if inp.get(k):
                        summary = f" {k}={str(inp[k])[:120]}"
                        break
            parts.append(f"· tool `{name}`{summary}")
        elif btype in ("tool_result", "ToolResultBlock") or type(block).__name__ == "ToolResultBlock":
            # keep short
            raw = getattr(block, "content", None)
            if isinstance(raw, str) and raw.strip():
                parts.append(f"  ↳ {raw.strip()[:240]}")
    return "\n".join(p for p in parts if p).strip()


def _subtype(msg: Any) -> str:
    return str(getattr(msg, "subtype", "") or "")


def _record_tool_receipt(
    *,
    grant: Any,
    tool_name: str,
    detail: str,
    ok: bool = True,
    trap: str = "",
) -> None:
    try:
        from pocket.agent_sandbox import Receipt, _write_receipt
        import uuid

        action = "shell" if tool_name.lower() in ("bash", "shell") else "fs_write"
        if tool_name.lower() in ("read", "glob", "grep", "search"):
            action = "fs_read"
        elif tool_name.lower() in ("webfetch", "webfetch", "web_search"):
            action = "net_http"
        rec = Receipt(
            id=str(uuid.uuid4())[:12],
            ok=ok,
            profile=getattr(grant, "profile", "claude_agent"),
            action=f"claude_tool:{tool_name}",
            agent_id=getattr(grant, "agent_id", "claude") or "claude",
            caps_used=sorted(getattr(grant, "caps", set()) or []),
            detail=(detail or "")[:800],
            started_at=time.time(),
            ended_at=time.time(),
            fuel_spent=1,
            trap=trap or "",
        )
        _write_receipt(rec)
    except Exception:
        pass


def run_claude_agent(
    prompt: str,
    cwd: str,
    *,
    job_id: str = "",
    session_id: str = "",
    max_turns: int = 24,
    allow_bash: Optional[bool] = None,
    system_prompt: str = "",
) -> Tuple[str, str, str]:
    """
    Run Claude Agent SDK loop (sync wrapper for POCKET executor).

    Returns (result_text, error_or_empty, engine_id).
    engine_id is "claude-agent-sdk" on success path.
    """
    if not sdk_installed():
        return "", "claude-agent-sdk not installed (pip install claude-agent-sdk)", "claude-agent-sdk"

    prompt = (prompt or "").strip()
    if not prompt:
        return "", "empty prompt", "claude-agent-sdk"

    work = str(Path(cwd or os.getcwd()).resolve())
    if allow_bash is None:
        allow_bash = (
            os.environ.get("POCKET_CLAUDE_BASH", "1").strip() not in ("0", "false", "no")
            or (os.environ.get("POCKET_EDITION") or "").lower() == "founder"
        )

    # Capability grant for receipts / policy context
    try:
        from pocket.agent_sandbox import PROFILES, mint_grant

        profile = "claude_agent" if "claude_agent" in PROFILES else "workspace_write"
        grant = mint_grant(
            profile,
            workspace_path=work,
            agent_id="claude",
            session_id=session_id or "",
            net_hosts=["*"],
        )
    except Exception:
        grant = None  # type: ignore

    allowed: List[str] = ["Read", "Write", "Edit", "Glob", "Grep"]
    if allow_bash:
        allowed.append("Bash")

    sys_bits = [
        "You are Claude running inside POCKET desk (ItsNotAI Labs).",
        "Be concise. Prefer small patches. Use markdown with fenced code when showing code.",
        f"Workspace: {work}",
    ]
    if system_prompt:
        sys_bits.append(system_prompt.strip())

    try:
        return asyncio.run(
            _run_async(
                prompt=prompt,
                work=work,
                job_id=job_id,
                max_turns=max_turns,
                allowed_tools=allowed,
                system_prompt="\n".join(sys_bits),
                grant=grant,
            )
        )
    except RuntimeError as e:
        # Nested event loop (rare) — try anyio if available
        if "asyncio.run()" in str(e) or "running event loop" in str(e).lower():
            try:
                import anyio

                return anyio.run(
                    _run_async,
                    prompt=prompt,
                    work=work,
                    job_id=job_id,
                    max_turns=max_turns,
                    allowed_tools=allowed,
                    system_prompt="\n".join(sys_bits),
                    grant=grant,
                )
            except Exception as e2:
                return "", f"claude-agent-sdk loop error: {e2}", "claude-agent-sdk"
        return "", f"claude-agent-sdk loop error: {e}", "claude-agent-sdk"
    except Exception as e:
        return "", f"claude-agent-sdk failed: {e}", "claude-agent-sdk"


async def _run_async(
    *,
    prompt: str,
    work: str,
    job_id: str,
    max_turns: int,
    allowed_tools: List[str],
    system_prompt: str,
    grant: Any,
) -> Tuple[str, str, str]:
    from claude_agent_sdk import ClaudeAgentOptions, query

    try:
        from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, ToolUseBlock
    except Exception:
        AssistantMessage = object  # type: ignore
        ResultMessage = object  # type: ignore
        TextBlock = object  # type: ignore
        ToolUseBlock = object  # type: ignore

    from pocket.stream_util import update_progress

    # PreToolUse hook → sandbox receipts
    async def pre_tool_hook(input_data, tool_use_id, context):  # noqa: ANN001
        try:
            tool_name = str((input_data or {}).get("tool_name") or "tool")
            tool_input = (input_data or {}).get("tool_input") or {}
            detail = f"{tool_name} {tool_input}"[:500]
            if grant is not None:
                _record_tool_receipt(grant=grant, tool_name=tool_name, detail=detail, ok=True)
            # Stream a line into the desk
            if job_id:
                update_progress(
                    job_id,
                    (getattr(update_progress, "_buf", "") or "") + f"\n· tool `{tool_name}`",
                    engine="claude-agent-sdk",
                )
        except Exception:
            pass
        return {}

    hooks = None
    try:
        from claude_agent_sdk import HookMatcher

        hooks = {"PreToolUse": [HookMatcher(hooks=[pre_tool_hook])]}
    except Exception:
        hooks = None

    opts_kwargs: Dict[str, Any] = {
        "cwd": work,
        "allowed_tools": allowed_tools,
        "permission_mode": "acceptEdits",
        "max_turns": max_turns,
        "system_prompt": system_prompt,
    }
    if hooks:
        opts_kwargs["hooks"] = hooks
    # Prefer system claude if present
    try:
        from pocket.executor import which_claude

        cli = which_claude()
        if cli:
            opts_kwargs["cli_path"] = cli
    except Exception:
        pass

    options = ClaudeAgentOptions(**opts_kwargs)

    transcript: List[str] = []
    final_result = ""
    last_stream = ""
    tool_count = 0

    def push(line: str) -> None:
        nonlocal last_stream
        if not line:
            return
        transcript.append(line)
        # keep stream buffer readable
        last_stream = "\n".join(transcript)[-45000:]
        if job_id:
            update_progress(job_id, last_stream, engine="claude-agent-sdk")

    push(f"[engine=claude-agent-sdk cwd={work} tools={','.join(allowed_tools)}]\n")
    push("Claude Agent SDK loop starting…")

    try:
        async for message in query(prompt=prompt, options=options):
            # Result
            if type(message).__name__ == "ResultMessage" or isinstance(message, ResultMessage):
                res = getattr(message, "result", None)
                if isinstance(res, str) and res.strip():
                    final_result = res.strip()
                    push(res.strip())
                continue

            # Assistant / tool
            text = _message_text(message)
            if not text:
                # subtype init/etc.
                st = _subtype(message)
                if st and st not in ("", "init"):
                    push(f"· {st}")
                continue

            # Count tool lines
            if "tool `" in text or text.startswith("· tool"):
                tool_count += 1
            push(text)
    except Exception as e:
        err = str(e)
        # Auth / CLI missing — bubble up for CLI fallback
        low = err.lower()
        if "cli" in low or "not found" in low or "auth" in low or "api" in low:
            return "", f"claude-agent-sdk: {err}", "claude-agent-sdk"
        return (
            last_stream or "",
            f"claude-agent-sdk run error: {err}",
            "claude-agent-sdk",
        )

    body = (final_result or last_stream or "").strip()
    if not body:
        return "", "claude-agent-sdk returned empty output", "claude-agent-sdk"

    # Polish for desk bubbles
    try:
        from pocket.reply_format import polish_agent_output

        polished = polish_agent_output(body[-60000:], engine="claude")
    except Exception:
        polished = body[-60000:]

    footer = ""
    if tool_count:
        footer = f"\n\n_[claude-agent-sdk · {tool_count} tool event(s) · receipts under ~/.pocket/sandbox/receipts]_"
    header = f"[engine=claude-agent-sdk · cwd={work}]\n\n"
    out = header + (polished or body) + footer
    if job_id:
        update_progress(job_id, out, engine="claude-agent-sdk")
    return out, "", "claude-agent-sdk"
