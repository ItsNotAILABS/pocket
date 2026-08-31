"""Universal agentic coding harness — subagents for every main agent.

Codex, Grok, Claude, plan, build, coding_swarm, and custom modes all route
through this harness so:
  - Subagents can be @mentioned or auto-planned
  - Live running state is visible/animated on the desk
  - Results land as pixel artifacts
  - Official benchmarks can score integration depth
"""

from __future__ import annotations

import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Tuple

from pocket.live_events import emit

_lock = threading.Lock()
# job_id -> list of subagent run records
_RUNS: Dict[str, List[Dict[str, Any]]] = {}
# global roster for GET /v1/subagents/running
_LIVE: Dict[str, Dict[str, Any]] = {}

_pool = ThreadPoolExecutor(max_workers=6, thread_name_prefix="pocket-sub")

# Auto-attach helpers by task signature — layered by work surface hierarchy
# hardware → local → browser → cloud → preview (see work_surface.hierarchy)
AUTO_RULES: List[Tuple[re.Pattern, List[str]]] = [
    # Local code
    (re.compile(r"\b(test|pytest|unit test|coverage|shell|powershell)\b", re.I), ["FORGE_HEADLESS"]),
    (re.compile(r"\b(sovereign|forge os|sovereign_forge)\b", re.I), ["FORGE_HEADLESS", "SHIP_HEADLESS"]),
    (re.compile(r"\b(security|auth|owasp|xss|csrf|threat)\b", re.I), ["SENTINEL_HEADLESS"]),
    (re.compile(r"\b(research|benchmark|compare|paper)\b", re.I), ["RESEARCH_HEADLESS"]),
    (re.compile(r"\b(ship|release|demo|launch|beta)\b", re.I), ["SHIP_HEADLESS"]),
    (re.compile(r"\b(ui|ux|design|layout|css|animation|preview|html|mockup)\b", re.I), ["DESIGN"]),
    (re.compile(r"\b(code|implement|refactor|fix|bug|typescript|python)\b", re.I), ["FORGE_HEADLESS"]),
    # Browser / web surface
    (re.compile(r"\b(browser|website|open edge|navigate|scrape|web page)\b", re.I), ["RESEARCH_HEADLESS"]),
    # Cloud / GitHub
    (re.compile(r"\b(github|pull request|\bpr\b|push|clone|repo)\b", re.I), ["SHIP_HEADLESS"]),
    # Hardware / embodiment
    (re.compile(r"\b(screenshot|click|desktop app|open notepad|vision|ui map)\b", re.I), ["ARCHON"]),
    # Draft / simulation before commit
    (re.compile(r"\b(draft|simulate|simulation|sandbox preview|before commit)\b", re.I), ["DESIGN"]),
    # Platform coherence surfaces
    (re.compile(r"\b(habitat|resident|agent floor)\b", re.I), ["ARCHON"]),
    (re.compile(r"\b(screen share|vcomp|virtual computer|control mode)\b", re.I), ["ARCHON"]),
    (re.compile(r"\b(working mode|package handoff|handoff artifacts)\b", re.I), ["ARCHON"]),
    (re.compile(r"\b(aria|voice agent|fusion voice|dfw|hotel hold|flight delay)\b", re.I), ["ARCHON"]),
    (re.compile(r"\b(phone pair|pair code|pocket phone)\b", re.I), ["ARCHON"]),
    (re.compile(r"\b(platform map|list skills|where is|find feature)\b", re.I), ["ARCHON"]),
]

CODING_MODES = frozenset(
    {
        "codex",
        "grok",
        "claude",
        "plan",
        "build",
        "ship",
        "coding_swarm",
        "pixel_swarm",
        "harness",
        "swarm_code",
        "code_swarm",
        "swarm",
        "rah",
        "recursive_harness",
        "rah_fanout",
        "rah_audit",
        "custom_agent",
        "wiki",
        "agent",
        "doer",
        "github",
        "gh",
        "browser",
        "web",
        "desktop",
        "vision",
        "voice",
        "work",
        "working",
    }
)


def platform_brief(*, max_chars: int = 1800) -> str:
    """Inject into agent system context so the platform is one product."""
    try:
        from pocket.pocket_identity import identity_brief

        ident = identity_brief(max_chars=min(700, max_chars // 2))
    except Exception:
        ident = "You are a POCKET host agent. Help users with POCKET."
    try:
        from pocket.platform_coherence import platform_brief as _pb

        base = _pb(max_chars=max(400, max_chars - len(ident) - 100))
    except Exception:
        base = (
            "POCKET: Habitat+Chat+Screen+Workspace+Working+Phone+Fusion+MCP. "
            "Discover: skill platform_map or GET /v1/platform/coherent. "
            "Run: POST /v1/skills/run. Protocols: GET /v1/protocols."
        )
    try:
        from pocket.loomgraph import brief as loomgraph_brief

        lg = loomgraph_brief(max_chars=400)
        if lg:
            base = (base.rstrip() + "\n" + lg).strip()
    except Exception:
        pass
    return (ident + "\n\n" + base).strip()[:max_chars]


def list_live(*, session_id: str = "", job_id: str = "") -> Dict[str, Any]:
    with _lock:
        items = list(_LIVE.values())
    if session_id:
        items = [i for i in items if i.get("session_id") == session_id or not i.get("session_id")]
    if job_id:
        items = [i for i in items if i.get("job_id") == job_id]
    # newest first
    items.sort(key=lambda x: -(x.get("updated_at") or 0))
    running = sum(1 for i in items if i.get("status") == "running")
    return {
        "ok": True,
        "schema": "pocket.agentic_harness.live.v1",
        "running": running,
        "total": len(items),
        "subagents": items[:40],
        "animated": True,
    }


def runs_for_job(job_id: str) -> List[Dict[str, Any]]:
    with _lock:
        return list(_RUNS.get(job_id or "", []) or [])


def _set_live(rec: Dict[str, Any]) -> None:
    rid = rec.get("id") or uuid.uuid4().hex[:10]
    rec["id"] = rid
    rec["updated_at"] = time.time()
    with _lock:
        _LIVE[rid] = rec


def _finish_live(rid: str, *, ok: bool, summary: str = "") -> None:
    with _lock:
        rec = _LIVE.get(rid)
        if not rec:
            return
        rec["status"] = "done" if ok else "fail"
        rec["ok"] = ok
        rec["summary"] = (summary or "")[:240]
        rec["updated_at"] = time.time()
        rec["finished_at"] = time.time()
        # keep done chips briefly; prune old
        cutoff = time.time() - 120
        dead = [k for k, v in _LIVE.items() if (v.get("finished_at") or 0) and v["finished_at"] < cutoff]
        for k in dead:
            _LIVE.pop(k, None)


def plan_subagents(prompt: str, *, mode: str = "", explicit: Optional[List[str]] = None) -> List[str]:
    """Who should run alongside the main agent."""
    names: List[str] = []
    if explicit:
        for n in explicit:
            u = str(n or "").upper().strip()
            if u and u not in names:
                names.append(u)
    try:
        from pocket.subagent_dispatch import parse_mentions

        for n in parse_mentions(prompt or ""):
            if n not in names:
                names.append(n)
    except Exception:
        pass
    # Auto helpers for coding-class modes (Codex included — full harness, no caps)
    if (mode or "").lower() in CODING_MODES or not mode:
        for rx, agents in AUTO_RULES:
            if rx.search(prompt or ""):
                for a in agents:
                    if a not in names:
                        names.append(a)
    # Cap concurrent helpers so desk stays snappy
    return names[:4]


def _execute_one(
    name: str,
    goal: str,
    *,
    job_id: str,
    session_id: str,
    parent_mode: str,
) -> Dict[str, Any]:
    rid = f"sa-{uuid.uuid4().hex[:10]}"
    rec = {
        "id": rid,
        "name": name,
        "agent": name,
        "goal": (goal or "")[:300],
        "status": "running",
        "job_id": job_id,
        "session_id": session_id,
        "parent_mode": parent_mode,
        "source": "harness",
        "started_at": time.time(),
        "updated_at": time.time(),
    }
    _set_live(rec)
    emit(
        "subagents",
        f"subagent @{name} started",
        agent=name,
        role="subagent",
        job_id=job_id,
        session_id=session_id,
        meta={"harness": True, "id": rid},
    )
    try:
        from pocket.subagent_dispatch import dispatch

        # Use dispatch engine for real mesh/latin/headless work
        out = dispatch(goal, from_agent=(parent_mode or "USER").upper()[:20], agents=[name])
        ok = bool(out.get("ok"))
        results = out.get("results") or []
        run = (results[0].get("run") if results else {}) or {}
        summary = str(run.get("message") or run.get("brief") or run.get("ok") or out)[:240]
        # Pixel artifact
        try:
            from pocket.pixel_vmem import put_artifact

            put_artifact(
                f"# Subagent @{name}\n\nGoal: {goal}\n\n```json\n{str(out)[:8000]}\n```\n",
                title=f"subagent-{name}-{rid}",
                language="md",
                agent=name.lower(),
                agent_role="subagent",
                ai_version=parent_mode,
                run_id=job_id or rid,
                tags=["subagent", "harness", name.lower()],
                note=f"subagent of {parent_mode}",
            )
        except Exception:
            pass
        _finish_live(rid, ok=ok, summary=summary)
        emit(
            "subagents",
            f"subagent @{name} {'done' if ok else 'fail'}",
            agent=name,
            role="subagent",
            job_id=job_id,
            session_id=session_id,
            level="info" if ok else "warn",
            meta={"harness": True, "id": rid, "ok": ok},
        )
        final = {
            **rec,
            "status": "done" if ok else "fail",
            "ok": ok,
            "summary": summary,
            "dispatch": {"dispatched": out.get("dispatched"), "mentions": out.get("mentions")},
            "finished_at": time.time(),
        }
    except Exception as e:
        _finish_live(rid, ok=False, summary=str(e)[:200])
        final = {**rec, "status": "fail", "ok": False, "summary": str(e)[:200], "finished_at": time.time()}
        emit("subagents", f"subagent @{name} error", agent=name, role="subagent", level="error", job_id=job_id)

    with _lock:
        _RUNS.setdefault(job_id or "_", []).append(final)
    return final


def spawn_parallel(
    names: List[str],
    goal: str,
    *,
    job_id: str = "",
    session_id: str = "",
    parent_mode: str = "",
    wait: bool = True,
    timeout: float = 90.0,
) -> List[Dict[str, Any]]:
    if not names:
        return []
    futs = {
        _pool.submit(
            _execute_one,
            n,
            goal,
            job_id=job_id,
            session_id=session_id,
            parent_mode=parent_mode,
        ): n
        for n in names
    }
    if not wait:
        return [{"name": n, "status": "running", "async": True} for n in names]
    done: List[Dict[str, Any]] = []
    try:
        for fut in as_completed(futs, timeout=timeout):
            try:
                done.append(fut.result())
            except Exception as e:
                done.append({"name": futs[fut], "ok": False, "summary": str(e), "status": "fail"})
    except Exception:
        # timeout — return what we have + still-running markers
        for fut, n in futs.items():
            if fut.done():
                try:
                    done.append(fut.result())
                except Exception as e:
                    done.append({"name": n, "ok": False, "status": "fail", "summary": str(e)})
            else:
                done.append({"name": n, "status": "running", "ok": None, "summary": "still running"})
    return done


def format_subagent_footer(runs: List[Dict[str, Any]]) -> str:
    if not runs:
        return ""
    lines = ["", "---", "## Subagents (harness)", ""]
    for r in runs:
        st = r.get("status") or ("done" if r.get("ok") else "fail")
        mark = "✓" if r.get("ok") else ("…" if st == "running" else "✗")
        lines.append(
            f"- {mark} **@{r.get('name') or r.get('agent')}** · {st} — {(r.get('summary') or '')[:160]}"
        )
    lines.append("")
    lines.append("_Subagents animated live on the Workspace → Helpers rail._")
    return "\n".join(lines)


def run_with_harness(
    mode: str,
    prompt: str,
    *,
    job_id: str = "",
    session_id: str = "",
    cwd: str = "",
    main: Optional[Callable[[], Tuple[str, str, str]]] = None,
    sub_agents: Optional[List[str]] = None,
    parallel_subs: bool = True,
) -> Tuple[str, str, str]:
    """
    Run main agent callable with planned subagents.

    Subagents start in parallel with the main agent (when parallel_subs=True)
    so the desk can animate them during the primary run.
    """
    mode = (mode or "agent").lower()
    goal = (prompt or "").strip()
    planned = plan_subagents(goal, mode=mode, explicit=sub_agents)

    # Fire subagents early for animation + overlap
    sub_future = None
    if planned and parallel_subs:
        sub_future = _pool.submit(
            spawn_parallel,
            planned,
            goal,
            job_id=job_id,
            session_id=session_id,
            parent_mode=mode,
            wait=True,
            timeout=120.0,
        )
        emit(
            "subagents",
            f"harness planned {len(planned)} subagent(s): {', '.join(planned)}",
            agent="HARNESS",
            role="harness",
            job_id=job_id,
            session_id=session_id,
            meta={"agents": planned, "parent_mode": mode},
        )
        if job_id:
            try:
                from pocket.stream_util import update_progress

                update_progress(
                    job_id,
                    f"[harness] spawning subagents: {', '.join('@'+a for a in planned)}\n",
                    engine=mode,
                )
            except Exception:
                pass

    out, err, eng = "", "", mode
    if main is not None:
        out, err, eng = main()
    else:
        out, err, eng = f"(no main runner for {mode})", "no main", mode

    runs: List[Dict[str, Any]] = []
    if sub_future is not None:
        try:
            runs = sub_future.result(timeout=125)
        except Exception as e:
            runs = [{"name": "HARNESS", "ok": False, "status": "fail", "summary": str(e)}]
    elif planned and not parallel_subs:
        runs = spawn_parallel(
            planned,
            goal,
            job_id=job_id,
            session_id=session_id,
            parent_mode=mode,
            wait=True,
        )

    footer = format_subagent_footer(runs)
    if footer and out:
        out = out.rstrip() + "\n" + footer
    elif footer and not out:
        out = footer

    # Index harness run in pixel
    try:
        from pocket.pixel_vmem import put_artifact

        put_artifact(
            out or "",
            title=f"harness-{mode}-{job_id or 'run'}",
            language="md",
            agent="harness",
            agent_role="Universal Agentic Harness",
            ai_version=mode,
            run_id=job_id or uuid.uuid4().hex[:10],
            tags=["harness", mode, "subagents"],
            note=f"parent={mode} subs={len(runs)}",
        )
    except Exception:
        pass

    return out, err, eng or mode


def harness_status() -> Dict[str, Any]:
    live = list_live()
    layers = {}
    try:
        from pocket.work_surface import harness_layers, hierarchy

        layers = harness_layers()
        hier = hierarchy()
    except Exception:
        hier = {}
    return {
        "ok": True,
        "schema": "pocket.agentic_harness.v1",
        "coding_modes": sorted(CODING_MODES),
        "auto_rules": len(AUTO_RULES),
        "live": live,
        "hierarchy": hier.get("layers") if isinstance(hier, dict) else [],
        "layer_map": layers.get("map") if isinstance(layers, dict) else {},
        "doctrine": (
            "Preview/draft → local or browser work → promote to folder or GitHub. "
            "Hardware for embodiment. Full harness on coding modes — @mentions always win."
        ),
        "features": [
            "subagents for codex/grok/claude/plan/swarm/build/github/browser/desktop",
            "parallel spawn + live animation bus",
            "pixel artifacts per subagent",
            "mention parse + auto plan by task signature",
            "work-surface hierarchy: hardware · local · browser · cloud · preview",
            "draft promote before cloud commit",
        ],
    }
