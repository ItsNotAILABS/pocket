"""Multi-plan orchestrator — reason → task list + sub-agents → execute → live chat term.

Visible in chat as a **sovereign terminal box** (WSL-wrapped look) that streams
plan / tasks / sub-agent progress while the job runs.

Flow:
  1. REASON  — understand goal, constraints, success criteria
  2. PLAN    — list of tasks + which sub-agent each needs
  3. EXECUTE — work through tasks (can expand more mid-run)
  4. STREAM  — update_progress + live_events so the desk term box redraws

Modes: multi_plan · multiplan · plan_exec · agentic_plan
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "multi_plan"
ROOT.mkdir(parents=True, exist_ok=True)

PRODUCT = "POCKET Multi-Plan"
SCHEMA = "pocket.multi_plan.v1"
ENGINE = "multi-plan"

# Sub-agent roster (who can be assigned)
SUBAGENTS = {
    "ARCHON": "Orchestrator — routes and synthesizes",
    "SCRUTATOR": "Research · web · evidence",
    "FORGE": "Code · build · test",
    "SENTINEL": "Security · audit · sanity",
    "OCULUS": "Screen · vision · UI map",
    "PORTARIUS": "Open apps · Edge · desktop",
    "SCRIBE": "Mail · drafts · compose",
    "NAVIGATOR": "Life ops · web UI · browse",
    "GHOST": "Math · hash · deterministic",
    "AURO": "Local meaning / LMR",
    "SHIP": "Ship · release · demo",
    "GENETIC": "Internal model evolution",
    "VCOMP": "Virtual computer shell",
}

TERM_OPEN = "[[POCKET_TERM:multi_plan]]"
TERM_CLOSE = "[[/POCKET_TERM]]"


def _jid() -> str:
    return uuid.uuid4().hex[:12]


def _stream(
    job_id: str,
    state: Dict[str, Any],
    *,
    log_line: str = "",
    session_id: str = "",
) -> None:
    """Push sovereign-term payload into the running chat message."""
    if log_line:
        state.setdefault("log", []).append(
            {"t": time.strftime("%H:%M:%S"), "line": log_line[:400]}
        )
        # keep last 80 lines
        state["log"] = state["log"][-80:]
    state["updated_at"] = time.time()
    body = format_term_payload(state)
    if job_id:
        try:
            from pocket.stream_util import update_progress

            update_progress(job_id, body, engine=ENGINE)
        except Exception:
            pass
    emit(
        "multi_plan",
        log_line or state.get("phase") or "tick",
        agent="MULTI_PLAN",
        role="host",
        session_id=session_id or state.get("session_id") or "",
        job_id=job_id,
        meta={"phase": state.get("phase"), "done": state.get("tasks_done"), "total": state.get("tasks_total")},
    )


def format_term_payload(state: Dict[str, Any]) -> str:
    """Markdown + machine JSON for the chat sovereign terminal box."""
    # Human-readable prefix so non-UI clients still see progress
    lines = [
        f"# Multi-plan · {state.get('phase', '…')}",
        f"**Goal:** {state.get('goal', '')[:200]}",
        "",
        "## Reasoning",
        state.get("reasoning") or "…",
        "",
        "## Tasks",
    ]
    for t in state.get("tasks") or []:
        st = t.get("status") or "pending"
        icon = {"pending": "○", "running": "●", "done": "✓", "failed": "✗", "skipped": "–"}.get(st, "·")
        agents = ", ".join(t.get("agents") or []) or "—"
        lines.append(f"- {icon} **T{t.get('id')}** [{st}] {t.get('title')} · agents: `{agents}`")
        if t.get("result_preview"):
            lines.append(f"  _{str(t['result_preview'])[:160]}_")
    lines += ["", "## Live log"]
    for row in (state.get("log") or [])[-12:]:
        lines.append(f"`{row.get('t')}` {row.get('line')}")
    human = "\n".join(lines)
    # Compact JSON for UI term box (no huge result bodies)
    compact = {
        "schema": SCHEMA,
        "run_id": state.get("run_id"),
        "phase": state.get("phase"),
        "goal": state.get("goal"),
        "reasoning": state.get("reasoning"),
        "tasks": [
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "agents": t.get("agents") or [],
                "kind": t.get("kind"),
                "result_preview": (t.get("result_preview") or "")[:200],
            }
            for t in (state.get("tasks") or [])
        ],
        "log": (state.get("log") or [])[-40:],
        "tasks_done": state.get("tasks_done"),
        "tasks_total": state.get("tasks_total"),
        "expanded": state.get("expanded") or 0,
        "ok": state.get("ok"),
    }
    return f"{human}\n\n{TERM_OPEN}\n{json.dumps(compact, ensure_ascii=False)}\n{TERM_CLOSE}\n"


def reason_and_plan(goal: str) -> Dict[str, Any]:
    """Decompose goal into tasks + sub-agents (deterministic + optional engines)."""
    g = (goal or "").strip()
    low = g.lower()
    tasks: List[Dict[str, Any]] = []
    reasoning_bits = [
        f"Goal received ({len(g)} chars).",
        "Decomposing into independent tasks with named sub-agents.",
    ]

    def add(title: str, agents: List[str], kind: str, detail: str = "") -> None:
        tasks.append(
            {
                "id": len(tasks) + 1,
                "title": title,
                "detail": detail or title,
                "agents": agents,
                "kind": kind,
                "status": "pending",
                "result_preview": "",
            }
        )

    # Always start with orientation
    add("Orient · platform map & identity", ["ARCHON"], "orient", "Confirm we are on POCKET host")

    # Keyword-driven expansion (agent can add more mid-run)
    if any(w in low for w in ("research", "look up", "search", "what is", "find out")):
        add("Research evidence pack", ["SCRUTATOR", "NAVIGATOR"], "research", g)
        reasoning_bits.append("Detected research intent → SCRUTATOR + NAVIGATOR.")
    if any(w in low for w in ("code", "implement", "fix", "bug", "api", "build", "refactor")):
        add("Code / build plan", ["FORGE"], "code", g)
        add("Sanity check", ["SENTINEL"], "audit", "Quick security/sanity pass")
        reasoning_bits.append("Detected coding intent → FORGE + SENTINEL.")
    if any(w in low for w in ("mail", "email", "inbox", "notify", "message agent")):
        add("Agent mail / comms", ["SCRIBE"], "mail", g)
        reasoning_bits.append("Detected mail intent → SCRIBE.")
    if any(w in low for w in ("screen", "see", "ui", "click", "vision")):
        add("Screen sense / vision", ["OCULUS"], "screen", g)
        reasoning_bits.append("Detected screen intent → OCULUS.")
    if any(w in low for w in ("open", "browser", "edge", "website", "browse")):
        add("Open / browse website", ["PORTARIUS", "NAVIGATOR"], "web", g)
        reasoning_bits.append("Detected browser intent → PORTARIUS + NAVIGATOR.")
    if any(w in low for w in ("math", "hash", "phi", "calculate", "compute")):
        add("Local math / ghost", ["GHOST"], "math", g)
        reasoning_bits.append("Detected math intent → GHOST.")
    if any(w in low for w in ("genetic", "evolve", "internal model")):
        add("Genetic flow over models", ["GENETIC"], "genetic", g)
        reasoning_bits.append("Detected genetic intent → GENETIC.")
    if any(w in low for w in ("ship", "release", "demo", "viral")):
        add("Ship / demo pack", ["SHIP"], "ship", g)
        reasoning_bits.append("Detected ship intent → SHIP.")
    if any(w in low for w in ("life", "food", "flight", "shop", "reserve", "dinner")):
        add("Life ops route", ["NAVIGATOR"], "life", g)
        reasoning_bits.append("Detected life-ops intent → NAVIGATOR.")

    # Multi-part: split on "then" / numbered bullets / newlines
    parts = re.split(r"\bthen\b|\band then\b|\n\s*[-*]\s+|\n\s*\d+[.)]\s+", low)
    if len(parts) > 2:
        reasoning_bits.append(f"Detected {len(parts)} sequential slices → one task each.")
        for i, part in enumerate(parts[1:6], start=1):
            part = part.strip()[:120]
            if part and len(part) > 8:
                add(f"Slice {i}: {part[:80]}", ["ARCHON", "FORGE"], "slice", part)

    # Default if still thin
    if len(tasks) <= 1:
        add("Primary work package", ["ARCHON", "SCRUTATOR"], "general", g)
        add("Synthesize answer", ["ARCHON"], "synth", "Combine evidence into a clear reply")
        reasoning_bits.append("General multi-step package (no strong keyword match).")
    else:
        add("Synthesize final answer", ["ARCHON"], "synth", "Combine all task outputs")

    reasoning_bits.append(f"Plan has {len(tasks)} tasks; sub-agents may expand if blocked.")
    return {
        "reasoning": " ".join(reasoning_bits),
        "tasks": tasks,
        "success": "All tasks done or explicitly skipped; final synthesis produced.",
    }


def _run_task(task: Dict[str, Any], goal: str) -> Tuple[bool, str]:
    """Execute one task via host engines/skills. Returns (ok, preview)."""
    kind = (task.get("kind") or "general").lower()
    detail = task.get("detail") or task.get("title") or goal
    try:
        if kind == "orient":
            from pocket.platform_coherence import run_platform_skill

            r = run_platform_skill("platform_map", prompt="")
            return True, f"platform_map ok={r.get('ok')} domains={len(r.get('domains') or r.get('map') or [])}"

        if kind == "research":
            from pocket.web_ui_engine import run_use

            r = run_use("research_topic", detail)
            n = len(r.get("results") or [])
            return bool(r.get("ok", True)), f"search hits={n} · {(r.get('query') or detail)[:80]}"

        if kind == "web":
            from pocket.web_ui_engine import run_use

            # open or search
            if detail.strip().startswith("http"):
                r = run_use("browse_sense", detail.strip().split()[0])
            else:
                r = run_use("research_topic", detail)
            return bool(r.get("ok", True)), str(r.get("message") or r.get("use") or "web")[:120]

        if kind == "mail":
            from pocket.agent_mail import inbox, status

            st = status()
            ib = inbox("assist")
            return True, f"mail accounts={st.get('accounts')} unread={ib.get('unread')}"

        if kind == "math":
            from pocket.internal_models import express_one

            er = express_one("ghost", detail)
            text = getattr(er, "text", None) or str(er)
            return bool(getattr(er, "ok", True)), text[:160]

        if kind == "genetic":
            from pocket.internal_models import run_genetic_flow

            r = run_genetic_flow(detail, generations=2, population=4)
            return bool(r.get("ok")), f"fitness={r.get('fitness')} gens={r.get('generations')}"

        if kind == "screen":
            from pocket.platform_coherence import run_platform_skill

            r = run_platform_skill("screen_sense", prompt=detail)
            return bool(r.get("ok", True)), str(r.get("brief") or r.get("error") or "screen")[:160]

        if kind == "code":
            from pocket.web_ui_engine import run_python_engine

            r = run_python_engine("coding_swarm", detail[:500])
            return bool(r.get("ok", True)), str(r.get("text") or r.get("message") or "code")[:160]

        if kind == "life":
            from pocket.web_ui_engine import run_use

            r = run_use("life_ops", detail)
            return bool(r.get("ok", True)), str(r.get("message") or r.get("use") or "life")[:160]

        if kind == "ship":
            from pocket.platform_coherence import run_platform_skill

            r = run_platform_skill("studio_status", prompt="")
            return bool(r.get("ok", True)), f"studio ok={r.get('ok')}"

        if kind == "audit":
            from pocket.platform_coherence import run_platform_skill

            r = run_platform_skill("platform_health", prompt="")
            return bool(r.get("ok", True)), f"health ok={r.get('ok')}"

        if kind == "synth":
            return True, "Synthesis ready from completed task previews."

        if kind == "slice":
            from pocket.web_ui_engine import run_use

            r = run_use("assist_route", detail)
            return bool(r.get("ok", True)), str(r.get("engine") or r.get("message") or "slice")[:160]

        # general
        from pocket.web_ui_engine import run_use

        r = run_use("assist_route", detail)
        return bool(r.get("ok", True)), str(r.get("engine") or "general")[:160]
    except Exception as e:
        return False, f"error: {e}"[:160]


def run_multi_plan(
    goal: str,
    *,
    job_id: str = "",
    session_id: str = "",
    max_tasks: int = 24,
    max_expand: int = 3,
) -> Dict[str, Any]:
    """Full multi-plan run with live sovereign-term streaming into chat."""
    run_id = _jid()
    plan = reason_and_plan(goal)
    state: Dict[str, Any] = {
        "schema": SCHEMA,
        "product": PRODUCT,
        "run_id": run_id,
        "goal": goal,
        "phase": "reason",
        "reasoning": plan["reasoning"],
        "tasks": plan["tasks"],
        "tasks_total": len(plan["tasks"]),
        "tasks_done": 0,
        "expanded": 0,
        "log": [],
        "session_id": session_id,
        "ok": False,
        "success_criteria": plan.get("success"),
    }
    # persist
    (ROOT / f"{run_id}.json").write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")

    _stream(job_id, state, log_line="▸ reason: decomposing goal…", session_id=session_id)
    time.sleep(0.05)
    state["phase"] = "plan"
    _stream(
        job_id,
        state,
        log_line=f"▸ plan: {len(state['tasks'])} tasks · sub-agents assigned",
        session_id=session_id,
    )

    # Notify mesh of planned agents
    agents_used = set()
    for t in state["tasks"]:
        for a in t.get("agents") or []:
            agents_used.add(a)
    _stream(
        job_id,
        state,
        log_line=f"▸ agents: {', '.join(sorted(agents_used)) or 'ARCHON'}",
        session_id=session_id,
    )

    state["phase"] = "execute"
    i = 0
    while i < len(state["tasks"]) and i < max_tasks:
        task = state["tasks"][i]
        task["status"] = "running"
        _stream(
            job_id,
            state,
            log_line=f"▸ T{task['id']} running · {','.join(task.get('agents') or [])} · {task['title'][:60]}",
            session_id=session_id,
        )
        # optional mesh ping
        try:
            from pocket.subagent_dispatch import dispatch

            for a in (task.get("agents") or [])[:2]:
                dispatch(
                    f"[multi-plan T{task['id']}] {task.get('detail') or task['title']}",
                    from_agent="MULTI_PLAN",
                    agents=[a],
                )
        except Exception:
            pass

        ok, preview = _run_task(task, goal)
        task["status"] = "done" if ok else "failed"
        task["result_preview"] = preview
        state["tasks_done"] = sum(1 for t in state["tasks"] if t.get("status") == "done")
        _stream(
            job_id,
            state,
            log_line=f"{'✓' if ok else '✗'} T{task['id']} {task['status']} · {preview[:100]}",
            session_id=session_id,
        )

        # Adaptive expansion: if failed research/code, add recovery task
        if not ok and state["expanded"] < max_expand:
            state["expanded"] += 1
            nid = len(state["tasks"]) + 1
            state["tasks"].append(
                {
                    "id": nid,
                    "title": f"Recover after T{task['id']} failure",
                    "detail": f"Retry differently: {task.get('detail') or task['title']}",
                    "agents": ["ARCHON", "SCRUTATOR"],
                    "kind": "slice",
                    "status": "pending",
                    "result_preview": "",
                }
            )
            state["tasks_total"] = len(state["tasks"])
            _stream(
                job_id,
                state,
                log_line=f"▸ expand: added T{nid} recovery task (#{state['expanded']})",
                session_id=session_id,
            )

        i += 1

    state["phase"] = "done"
    state["ok"] = state["tasks_done"] > 0
    # Final synthesis
    synth_lines = [
        f"# Multi-plan complete · `{run_id}`",
        f"**Goal:** {goal}",
        f"**Tasks:** {state['tasks_done']}/{state['tasks_total']} done · expanded={state['expanded']}",
        "",
        "## Reasoning",
        state.get("reasoning") or "",
        "",
        "## Results",
    ]
    for t in state["tasks"]:
        icon = "✓" if t.get("status") == "done" else "✗"
        synth_lines.append(
            f"{icon} **T{t['id']} {t['title']}** ({', '.join(t.get('agents') or [])})  \n  {t.get('result_preview') or '—'}"
        )
    synth_lines += [
        "",
        "_Visible in chat as the sovereign multi-plan terminal while it ran._",
    ]
    state["synthesis"] = "\n".join(synth_lines)
    _stream(job_id, state, log_line="▸ done · synthesis ready", session_id=session_id)

    (ROOT / f"{run_id}.json").write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    # Return full body for final message
    final = format_term_payload(state) + "\n\n" + state["synthesis"]
    return {
        "ok": state["ok"],
        "run_id": run_id,
        "state": state,
        "markdown": final,
        "engine": ENGINE,
    }


def run_job(prompt: str, *, cwd: str = "", job: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
    """Executor entry for mode=multi_plan."""
    j = job or {}
    job_id = str(j.get("id") or "")
    session_id = str(j.get("session_id") or "")
    r = run_multi_plan(prompt or "", job_id=job_id, session_id=session_id)
    md = r.get("markdown") or ""
    err = "" if r.get("ok") else "multi-plan incomplete"
    return md, err, ENGINE


def list_runs(limit: int = 15) -> List[Dict[str, Any]]:
    rows = []
    for p in sorted(ROOT.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            rows.append(
                {
                    "run_id": d.get("run_id"),
                    "goal": (d.get("goal") or "")[:120],
                    "phase": d.get("phase"),
                    "tasks_done": d.get("tasks_done"),
                    "tasks_total": d.get("tasks_total"),
                    "ok": d.get("ok"),
                }
            )
        except Exception:
            continue
    return rows
