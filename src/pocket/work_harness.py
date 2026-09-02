"""Work harness for Pocket + PhoneAI: think → optional shell → one engine → receipt."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from pocket.agent_runtime import route_think
from pocket.shell_exec import pick_cwd_for_goal, run as shell_run


def run(
    goal: str,
    *,
    engine: str = "auto",
    shell: str = "",
    cwd: str = "",
    timeout: float = 25,
) -> Dict[str, Any]:
    text = (goal or "").strip()
    if not text and not shell:
        return {"ok": False, "error": "goal or shell required"}
    thought = route_think(text or shell, engine)
    work = cwd or str(pick_cwd_for_goal(text or shell))
    steps: List[Dict[str, Any]] = [{"kind": "think", **thought}]
    sh: Dict[str, Any] = {}
    cmd = (shell or "").strip()
    if not cmd and thought.get("engine") == "codex" and any(
        w in (text or "").lower() for w in ("pytest", "run tests", "test this")
    ):
        cmd = "python -m pytest -q --tb=line"
    if cmd:
        sh = shell_run(cmd, cwd=work, timeout=timeout)
        steps.append({"kind": "shell", **sh})
    engine_out: Dict[str, Any] = {}
    if text:
        from pocket.phoneai_bridge import ask_engine

        engine_out = ask_engine(text, engine=engine if engine != "auto" else str(thought.get("engine") or "auto"))
        steps.append({"kind": "engine", "engine": engine_out.get("engine"), "ok": engine_out.get("ok")})
    helpers: Dict[str, Any] = {}
    try:
        from pocket.agentic_harness import plan_subagents

        helpers = {"names": plan_subagents(text, mode=str(thought.get("engine") or ""))}
    except Exception as e:
        helpers = {"error": str(e)[:120]}
    ok = bool((not cmd or sh.get("ok")) and (not text or engine_out.get("ok") or engine_out.get("reply")))
    return {
        "ok": ok,
        "product": "POCKET work harness",
        "arch": "pocket.agent.arch.v1",
        "execute": "harness",
        "goal": text[:400],
        "cwd": work,
        "thought": thought,
        "shell": sh,
        "engine": engine_out,
        "helpers": helpers,
        "steps": steps,
        "reply": engine_out.get("reply") or sh.get("stdout") or sh.get("error") or "",
        "ms": int(engine_out.get("latency_ms") or sh.get("ms") or 0),
        "at": time.time(),
    }
