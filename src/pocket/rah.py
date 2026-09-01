"""Recursive Agent Harnesses (RAH) — POCKET native.

The recursive unit is a **full agent harness** (not a bare model call):

  · Own context window (fresh job + workspace slice)
  · Full tool access via POCKET executor / skills / mesh
  · Planning loop (mode plan → implement engines)
  · Ability to spawn further sub-harnesses (depth-capped)

Parent agents write an **orchestration plan** (JSON or a small Python fan-out
script). Intermediate results live on the filesystem under
``~/.pocket/rah/<run_id>/`` so the parent context never holds every leaf.

Doctrine (POCKET way):
  Identity-stamped · mesh-aware · job-session backed · protocol-cataloged.
  Cap parallel + depth so a laptop host stays usable (~15× cost warning).

Refs: RAH pattern (harness recursion), RLM contrast, Claude Code dynamic
workflows — implemented with POCKET jobs, not a foreign runtime.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROTOCOL_ID = "MEDINA-RAH/1.0"
PROTOCOL_NAME = "Recursive Agent Harnesses"
SCHEMA = "pocket.rah.v1"

# Safety defaults for host (override via env)
DEFAULT_MAX_DEPTH = int(os.environ.get("POCKET_RAH_MAX_DEPTH") or "3")
HARD_MAX_DEPTH = 5
DEFAULT_MAX_PARALLEL = int(os.environ.get("POCKET_RAH_MAX_PARALLEL") or "12")
HARD_MAX_PARALLEL = int(os.environ.get("POCKET_RAH_HARD_PARALLEL") or "48")
DEFAULT_LEAF_MODE = (os.environ.get("POCKET_RAH_LEAF_MODE") or "plan").lower()
VERIFY_MODE = (os.environ.get("POCKET_RAH_VERIFY_MODE") or "plan").lower()

ROOT = Path.home() / ".pocket" / "rah"
_lock = threading.Lock()
_RUNS: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Catalog / doctrine
# ---------------------------------------------------------------------------

DOCTRINE = {
    "name": PROTOCOL_NAME,
    "id": PROTOCOL_ID,
    "schema": SCHEMA,
    "recursive_unit": "full agent harness (context + tools + plan + spawn)",
    "not": "bare model call (that is RLM territory)",
    "parent_action": "writes orchestration plan/script; runtime fans out harnesses",
    "state": "filesystem under ~/.pocket/rah/<run_id>/ + job store",
    "when_to_use": [
        "Independent subtasks (no heavy shared mutable state)",
        "Cheap verification signal (tests, lint, schema, adversarial reviewer)",
        "High-value work worth ~15× tokens of a single agent",
    ],
    "when_not": [
        "Tight sequential dependency chains",
        "Naming conflicts across parallel writers without isolation",
        "Low-value chores — use linear agent or light mesh",
    ],
    "vs_rlm": {
        "RLM": "recursive unit = bare model on text segments",
        "RAH": "recursive unit = full harness with tools + filesystem",
    },
    "pocket_hooks": [
        "mode=rah | recursive_harness | rah_fanout",
        "POST /v1/rah/run",
        "GET /v1/rah/status",
        "skill rah_run · rah_plan · rah_status",
        "GET /v1/protocols/rah",
    ],
}


def _limits(depth_cap: Optional[int] = None, parallel: Optional[int] = None) -> Tuple[int, int]:
    d = depth_cap if depth_cap is not None else DEFAULT_MAX_DEPTH
    p = parallel if parallel is not None else DEFAULT_MAX_PARALLEL
    d = max(1, min(HARD_MAX_DEPTH, int(d)))
    p = max(1, min(HARD_MAX_PARALLEL, int(p)))
    return d, p


# ---------------------------------------------------------------------------
# Auto-detect: agents choose RAH without the user naming it
# ---------------------------------------------------------------------------

# Strong signals → auto-run RAH (score +2 each, need threshold)
_RAH_STRONG: List[re.Pattern] = [
    re.compile(
        r"\b(audit|scan|review|check|cover)\b.{0,40}\b(every|all|each|entire|whole)\b",
        re.I,
    ),
    re.compile(
        r"\b(every|all|each)\b.{0,30}\b(endpoint|route|api|module|package|file|service|handler|agent|protocol)\b",
        re.I,
    ),
    re.compile(
        r"\b(port|migrate|rewrite|convert)\b.{0,60}\b(codebase|entire|all|every|whole|monorepo)\b",
        re.I,
    ),
    re.compile(
        r"\b(port|migrate|rewrite)\b.{0,80}\b(zig|rust|typescript|python|java|go)\b.{0,40}\b(to|into|from)\b",
        re.I,
    ),
    re.compile(
        r"\b(parallel|fan-?out|in parallel|many agents|hundreds of|dozens of)\b.{0,40}"
        r"\b(agent|harness|worker|sub-?agent|task|slice)\b",
        re.I,
    ),
    re.compile(r"\b(recursive agent harness|\brah\b|harness recursion)\b", re.I),
    re.compile(
        r"\b(large-?scale|massive|fleet|bulk)\b.{0,30}\b(refactor|audit|migration|rewrite|scan)\b",
        re.I,
    ),
]

# Medium signals → +1 each
_RAH_MEDIUM: List[re.Pattern] = [
    re.compile(r"\b(independent|embarrassingly parallel|no shared state)\b", re.I),
    re.compile(r"\b(across (the )?(codebase|repo|monorepo|packages|services))\b", re.I),
    re.compile(r"\b(multi-?module|multi-?package|multi-?service|multi-?endpoint)\b", re.I),
    re.compile(r"\b(split (into|the) work|break (this|it) (up|into)|divide and conquer)\b", re.I),
    re.compile(r"\b(all ten|all 10|all eleven|all 11)\b.{0,20}\bprotocol", re.I),
    re.compile(r"(?m)^\s*(?:\d+[\.\)]|[-*])\s+.+\n(?:\s*(?:\d+[\.\)]|[-*])\s+.+\n){3,}", re.I),
]

# Anti-signals → do NOT auto RAH (cheap / sequential / chatty)
_RAH_ANTI: List[re.Pattern] = [
    re.compile(
        r"\b(what is|who are you|hello|hi\b|thanks|explain briefly|one file|single function|"
        r"quick fix|typo|rename this|where is|how do i open|status only|just list)\b",
        re.I,
    ),
    re.compile(r"\b(step by step in order|must be sequential|after that then|depends on previous)\b", re.I),
]

# Modes that may auto-escalate into RAH (not shell/term)
_RAH_ESCALATE_MODES = frozenset(
    {
        "codex",
        "claude",
        "grok",
        "plan",
        "build",
        "ship",
        "agent",
        "doer",
        "coding_swarm",
        "pixel_swarm",
        "harness",
        "swarm",
        "assist",
        "assistant",
        "archon",
        "wiki",
        "codebase",
        "custom_agent",
        "ask",
        "work",
        "working",
        "auro",
        "auro14b",
        "meaning",
    }
)


def score_rah_fit(prompt: str, *, mode: str = "") -> Dict[str, Any]:
    """Score whether this task should use RAH. Agents call this; users need not mention RAH."""
    text = (prompt or "").strip()
    # Drop identity injection noise for scoring
    for marker in ("[POCKET IDENTITY]", "# You are in POCKET", "[POCKET PLATFORM]", "[POCKET PROTOCOLS]"):
        if marker in text:
            text = text.split(marker)[0].strip() or text
    low = text.lower()
    mode = (mode or "").lower()
    score = 0
    reasons: List[str] = []
    anti: List[str] = []

    if mode in ("rah", "recursive_harness", "rah_fanout", "rah_audit"):
        return {
            "ok": True,
            "use_rah": True,
            "auto": True,
            "score": 100,
            "threshold": 3,
            "reasons": ["mode already rah"],
            "anti": [],
            "suggested_leaves": 8,
            "suggested_depth": 2,
        }

    for rx in _RAH_ANTI:
        if rx.search(text):
            anti.append(rx.pattern[:60])
            score -= 2

    for rx in _RAH_STRONG:
        if rx.search(text):
            score += 2
            reasons.append(f"strong:{rx.pattern[:50]}")

    for rx in _RAH_MEDIUM:
        if rx.search(text):
            score += 1
            reasons.append(f"medium:{rx.pattern[:50]}")

    # Length / complexity proxies
    if len(text) > 900:
        score += 1
        reasons.append("long_brief")
    if len(re.findall(r"(?m)^\s*(?:\d+[\.\)]|[-*])\s+", text)) >= 4:
        score += 2
        reasons.append("bullet_list_4+")

    # Security fleet / full surface audits
    if any(k in low for k in ("missing auth", "authn", "rbac", "owasp", "threat model")) and any(
        k in low for k in ("all", "every", "entire", "across", "fleet")
    ):
        score += 2
        reasons.append("security_fleet")

    threshold = int(os.environ.get("POCKET_RAH_AUTO_THRESHOLD") or "2")
    use = score >= threshold and mode not in ("shell", "term", "voice", "v2v")
    # Explicit disable
    if str(os.environ.get("POCKET_RAH_AUTO") or "1").strip().lower() in ("0", "false", "no", "off"):
        use = False
        anti.append("POCKET_RAH_AUTO=0")

    # Leaf count from score
    leaves = 4
    if score >= 5:
        leaves = 8
    if score >= 7:
        leaves = 12
    if score >= 9:
        leaves = min(16, DEFAULT_MAX_PARALLEL)
    depth = 1 if score < 5 else 2

    return {
        "ok": True,
        "use_rah": use,
        "auto": use,
        "score": score,
        "threshold": threshold,
        "reasons": reasons[:12],
        "anti": anti[:8],
        "suggested_leaves": leaves,
        "suggested_depth": depth,
        "mode": mode,
        "doctrine": "Agents must auto-use RAH when score>=threshold; user need not say RAH",
    }


def should_auto_rah(prompt: str, *, mode: str = "") -> bool:
    return bool(score_rah_fit(prompt, mode=mode).get("use_rah"))


def maybe_auto_rah(
    prompt: str,
    *,
    mode: str = "",
    job: Optional[Dict[str, Any]] = None,
    cwd: str = "",
    execute: bool = False,
    grant_id: str = "",
) -> Optional[Dict[str, Any]]:
    """Plan by default. Leaves run only with a valid WorkGrant."""
    job = job or {}
    if job.get("_rah_done") or job.get("rah_skip") or job.get("_harness_inner"):
        return None
    if mode in ("rah", "recursive_harness", "rah_fanout", "rah_audit"):
        # Already on RAH path
        return None
    if mode and mode not in _RAH_ESCALATE_MODES and mode not in ("", "auto"):
        # Unknown modes still score; only block pure shell-like later
        pass

    fit = score_rah_fit(prompt, mode=mode)
    if not fit.get("use_rah"):
        return {"ok": True, "skipped": True, "fit": fit}

    if not execute:
        plan = plan_fanout(
            prompt,
            max_leaves=int(fit.get("suggested_leaves") or 8),
            hint="auto-selected by POCKET RAH detector",
        )
        return {"ok": True, "auto": True, "execute": False, "fit": fit, "plan": plan}

    from pocket.work_grant import valid as grant_valid

    g = grant_valid(grant_id or str((job or {}).get("grant_id") or ""), capability="rah")
    if not g.get("ok"):
        plan = plan_fanout(
            prompt,
            max_leaves=int(fit.get("suggested_leaves") or 8),
            hint="RAH plan only — WorkGrant required to execute",
        )
        return {"ok": True, "auto": True, "execute": False, "fit": fit, "plan": plan, "grant": g}

    # Cap auto runs for host safety
    max_leaves = min(int(fit.get("suggested_leaves") or 8), int(os.environ.get("POCKET_RAH_AUTO_MAX_LEAVES") or "10"))
    max_depth = min(int(fit.get("suggested_depth") or 2), 2)
    max_parallel = min(max_leaves, int(os.environ.get("POCKET_RAH_AUTO_PARALLEL") or "6"))

    run = run_rah(
        (prompt or "")[:8000],
        max_leaves=max_leaves,
        max_parallel=max_parallel,
        max_depth=max_depth,
        parent_job_id=str(job.get("id") or ""),
        session_id=str(job.get("session_id") or ""),
        cwd=cwd or job.get("cwd") or "",
        verify=True,
        synthesize=True,
        hint="AUTO: agent selected RAH (user did not need to ask)",
    )
    return {
        "ok": bool(run.get("ok")),
        "auto": True,
        "execute": True,
        "fit": fit,
        "run": run,
        "markdown": format_result_markdown(run),
        "engine": "rah",
    }


def run_dir(run_id: str) -> Path:
    p = ROOT / run_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "leaves").mkdir(exist_ok=True)
    (p / "scripts").mkdir(exist_ok=True)
    (p / "verify").mkdir(exist_ok=True)
    return p


def manifest() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "protocol": PROTOCOL_ID,
        "name": PROTOCOL_NAME,
        "doctrine": DOCTRINE,
        "defaults": {
            "max_depth": DEFAULT_MAX_DEPTH,
            "hard_max_depth": HARD_MAX_DEPTH,
            "max_parallel": DEFAULT_MAX_PARALLEL,
            "hard_max_parallel": HARD_MAX_PARALLEL,
            "leaf_mode": DEFAULT_LEAF_MODE,
            "verify_mode": VERIFY_MODE,
            "root": str(ROOT),
        },
        "apis": [
            "POST /v1/rah/run",
            "POST /v1/rah/plan",
            "GET /v1/rah",
            "GET /v1/rah/status",
            "GET /v1/rah/runs/{id}",
            "GET /v1/protocols/rah",
        ],
        "skills": ["rah_run", "rah_plan", "rah_status", "rah_verify"],
        "modes": ["rah", "recursive_harness", "rah_fanout", "rah_audit"],
    }


# ---------------------------------------------------------------------------
# Planning — parent decomposes task into independent leaf harnesses
# ---------------------------------------------------------------------------

def plan_fanout(
    task: str,
    *,
    max_leaves: int = 16,
    hint: str = "",
) -> Dict[str, Any]:
    """Decompose a large task into independent leaf goals (no LLM required).

    Uses structural heuristics + optional explicit script. Parent can also pass
    a full JSON plan via run_rah(plan=...).
    """
    task = (task or "").strip()
    max_leaves = max(1, min(HARD_MAX_PARALLEL, int(max_leaves or 16)))
    leaves: List[Dict[str, Any]] = []

    # Explicit numbered list in the prompt
    numbered = re.findall(
        r"(?m)^\s*(?:\d+[\.\)]\s*|[-*]\s+)(.+)$",
        task,
    )
    if len(numbered) >= 2:
        for i, line in enumerate(numbered[:max_leaves]):
            leaves.append(
                {
                    "id": f"L{i+1:02d}",
                    "goal": line.strip()[:2000],
                    "mode": DEFAULT_LEAF_MODE,
                    "independent": True,
                }
            )
    else:
        # Domain fan-out templates for common RAH jobs
        low = task.lower()
        if any(k in low for k in ("audit", "auth", "endpoint", "api", "security")):
            templates = [
                "Inventory public/private routes and mark auth requirements",
                "Check session/token validation on write endpoints",
                "Check RBAC / role gates on admin and owner routes",
                "Scan for missing CSRF / CORS / rate-limit on mutating APIs",
                "List secret-handling and logging risks near auth paths",
                "Propose minimal fixes with file paths and test ideas",
            ]
            for i, t in enumerate(templates[:max_leaves]):
                leaves.append(
                    {
                        "id": f"L{i+1:02d}",
                        "goal": f"{t}\n\nParent task: {task[:800]}",
                        "mode": "plan" if i < 4 else DEFAULT_LEAF_MODE,
                        "independent": True,
                        "lane": "security",
                    }
                )
        elif any(k in low for k in ("migrate", "port", "refactor", "every file", "codebase")):
            templates = [
                "Map modules and dependency boundaries",
                "Identify pure/leaf packages safe for parallel rewrite",
                "Draft interface contracts and shared types",
                "Propose parallel worker slices (by package)",
                "Define verification: tests, typecheck, smoke",
                "Risk list: shared state, naming conflicts, sequential gates",
            ]
            for i, t in enumerate(templates[:max_leaves]):
                leaves.append(
                    {
                        "id": f"L{i+1:02d}",
                        "goal": f"{t}\n\nParent task: {task[:800]}",
                        "mode": DEFAULT_LEAF_MODE,
                        "independent": True,
                        "lane": "migration",
                    }
                )
        elif any(k in low for k in ("protocol", "mesh", "pocket", "platform")):
            try:
                from pocket.protocols.platform_protocols import list_protocols

                for i, p in enumerate(list_protocols()[:max_leaves]):
                    leaves.append(
                        {
                            "id": f"L{i+1:02d}",
                            "goal": (
                                f"Assess and improve POCKET protocol `{p['slug']}` "
                                f"({p['name']}): health, APIs, agent awareness.\n"
                                f"Parent: {task[:600]}"
                            ),
                            "mode": "plan",
                            "independent": True,
                            "lane": "protocol",
                            "protocol_slug": p["slug"],
                        }
                    )
            except Exception:
                pass
        if not leaves:
            # Generic parallel slices
            slices = [
                "Clarify goals, constraints, success metrics",
                "Enumerate independent work units for parallel harnesses",
                "Deep-dive unit A (first major slice)",
                "Deep-dive unit B (second major slice)",
                "Deep-dive unit C (third major slice)",
                "Define verification / adversarial checks",
                "Synthesize findings into an ordered ship plan",
            ]
            for i, t in enumerate(slices[:max_leaves]):
                leaves.append(
                    {
                        "id": f"L{i+1:02d}",
                        "goal": f"{t}\n\nParent task: {task[:900]}",
                        "mode": DEFAULT_LEAF_MODE,
                        "independent": True,
                    }
                )

    if hint:
        leaves.insert(
            0,
            {
                "id": "L00",
                "goal": f"Honor parent hint: {hint[:500]}\n\nTask: {task[:600]}",
                "mode": "plan",
                "independent": True,
            },
        )
        leaves = leaves[:max_leaves]

    return {
        "ok": True,
        "schema": "pocket.rah.plan.v1",
        "task": task[:4000],
        "leaves": leaves,
        "count": len(leaves),
        "max_depth": DEFAULT_MAX_DEPTH,
        "verify": True,
        "synthesize": True,
        "note": "Independent leaves only — parent synthesizes; state on filesystem",
    }


def write_orchestration_script(run_id: str, plan: Dict[str, Any]) -> Path:
    """Materialize a Python orchestration script the parent 'wrote' (auditable)."""
    rd = run_dir(run_id)
    path = rd / "scripts" / "orchestrate.py"
    leaves = plan.get("leaves") or []
    body = f'''# RAH orchestration — auto-generated by POCKET
# Protocol: {PROTOCOL_ID}
# Run: {run_id}
# This script is the parent harness's fan-out artifact (code-first recursion).

LEAVES = {json.dumps(leaves, indent=2)}
TASK = {json.dumps((plan.get("task") or "")[:4000])}
MAX_PARALLEL = {int(plan.get("max_parallel") or DEFAULT_MAX_PARALLEL)}
MAX_DEPTH = {int(plan.get("max_depth") or DEFAULT_MAX_DEPTH)}

def main():
    print(f"RAH orchestrate run={run_id!r} leaves={{len(LEAVES)}} parallel={{MAX_PARALLEL}}")
    # Runtime executes leaves via pocket.rah.run_rah — this file is the audit trail.
    return {{"leaves": len(LEAVES), "task": TASK[:200]}}

if __name__ == "__main__":
    main()
'''
    path.write_text(body, encoding="utf-8")
    # Also dump plan.json
    (rd / "plan.json").write_text(json.dumps(plan, indent=2, default=str), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Leaf harness — full independent agent (job + tools + optional recurse)
# ---------------------------------------------------------------------------

def _run_leaf_harness(
    leaf: Dict[str, Any],
    *,
    run_id: str,
    depth: int,
    max_depth: int,
    parent_job_id: str = "",
    session_id: str = "",
    cwd: str = "",
    allow_recurse: bool = True,
) -> Dict[str, Any]:
    """One complete harness: identity, job, tools, optional sub-RAH."""
    from pocket.jobs import create_job, get as get_job, save as save_job
    from pocket.worker import process_one

    lid = leaf.get("id") or f"L{uuid.uuid4().hex[:6]}"
    goal = (leaf.get("goal") or leaf.get("prompt") or leaf.get("task") or "").strip()
    mode = (leaf.get("mode") or DEFAULT_LEAF_MODE).lower()
    # Never nest rah mode infinitely via mode alone without depth check
    if mode in ("rah", "recursive_harness", "rah_fanout", "rah_audit") and depth >= max_depth:
        mode = DEFAULT_LEAF_MODE

    started = time.time()
    rec: Dict[str, Any] = {
        "id": lid,
        "goal": goal[:500],
        "mode": mode,
        "depth": depth,
        "status": "running",
        "started_at": started,
        "run_id": run_id,
    }
    try:
        from pocket.agentic_harness import _set_live

        _set_live(
            {
                "id": f"rah-{run_id}-{lid}",
                "name": f"RAH:{lid}",
                "agent": f"RAH/{lid}",
                "goal": goal[:300],
                "status": "running",
                "job_id": parent_job_id,
                "session_id": session_id,
                "parent_mode": "rah",
                "source": "rah",
                "depth": depth,
                "started_at": started,
            }
        )
    except Exception:
        pass

    # Stamp identity + RAH doctrine into leaf context
    try:
        from pocket.pocket_identity import wrap_user_prompt

        goal_full = wrap_user_prompt(
            f"[RAH leaf {lid} depth={depth}/{max_depth}]\n{goal}",
            mode=mode,
            max_identity=900,
        )
        goal_full += (
            "\n\n[RAH] You are a **full agent harness** leaf. "
            "Own context + tools. Write results clearly. "
            "If you need more parallelism and depth allows, say FANOUT: with a bullet list.\n"
        )
    except Exception:
        goal_full = goal

    # Optional explicit recurse from leaf
    sub_rah = None
    if (
        allow_recurse
        and depth < max_depth
        and leaf.get("recurse")
        and isinstance(leaf.get("sub_plan") or leaf.get("leaves"), (dict, list))
    ):
        sub_plan = leaf.get("sub_plan")
        if isinstance(leaf.get("leaves"), list):
            sub_plan = {"task": goal, "leaves": leaf["leaves"], "verify": False, "synthesize": True}
        if isinstance(sub_plan, dict):
            sub_rah = run_rah(
                sub_plan.get("task") or goal,
                plan=sub_plan,
                depth=depth + 1,
                max_depth=max_depth,
                max_parallel=int(leaf.get("max_parallel") or 4),
                parent_job_id=parent_job_id,
                session_id=session_id,
                cwd=cwd,
                verify=bool(sub_plan.get("verify", False)),
            )

    if mode in ("auro", "auro14b", "meaning"):
        rec["engine"] = "auro"
        try:
            from pocket.auro14b_bridge import auro_root

            root = auro_root()
            if root:
                import sys

                pth = str(root)
                if pth not in sys.path:
                    sys.path.insert(0, pth)
                from pocket.auro_rah_adapter import run_auro_rah

                ar = run_auro_rah(
                    goal,
                    max_parallel=int(leaf.get("max_parallel") or 4),
                    depth=1,
                    grant_id=str(parent_job_id or ""),
                    tenant=str(session_id or ""),
                )
                rec["status"] = "done" if ar.get("ok") else "fail"
                rec["ok"] = bool(ar.get("ok"))
                rec["result"] = (ar.get("synthesis") or json.dumps(ar, default=str))[:12000]
                rec["auro_run_id"] = ar.get("auro_run_id")
                rec["adapter"] = ar.get("adapter")
                rec["finished_at"] = time.time()
                rec["duration_sec"] = round(rec["finished_at"] - started, 2)
                return rec
        except Exception as e:
            rec["error"] = str(e)[:400]
        try:
            from pocket.internal_models.modules.auro import AuroModel

            class _Deep:
                def strategy(self) -> str:
                    return "deep"

            res = AuroModel().express(goal, genome=_Deep())
            rec["status"] = "done" if getattr(res, "ok", True) else "fail"
            rec["ok"] = bool(getattr(res, "ok", True))
            rec["result"] = str(getattr(res, "text", res) or "")[:12000]
            rec["finished_at"] = time.time()
            rec["duration_sec"] = round(rec["finished_at"] - started, 2)
            return rec
        except Exception as e:
            rec["error"] = ((rec.get("error") or "") + " | " + str(e))[:400]
            # fall through to host job
    job = create_job(
        goal_full[:20000],
        name=f"rah:{run_id}:{lid}",
        mode=mode if mode not in ("rah", "recursive_harness", "rah_fanout") else DEFAULT_LEAF_MODE,
        workspace="workspace",
        cwd=cwd or "",
        session_id=session_id or "",
        message_id="",
    )
    job["rah_run_id"] = run_id
    job["rah_leaf_id"] = lid
    job["rah_depth"] = depth
    job["_harness_inner"] = True  # avoid double outer harness spam
    job["harness"] = True
    save_job(job)
    rec["job_id"] = job["id"]

    # Drain this leaf (bounded)
    deadline = time.time() + float(leaf.get("timeout_sec") or 180)
    process_one()
    while time.time() < deadline:
        j = get_job(job["id"])
        if not j:
            break
        st = j.get("status")
        if st in ("done", "failed", "cancelled", "error"):
            rec["status"] = "done" if st == "done" else "fail"
            rec["ok"] = st == "done"
            rec["result"] = (j.get("result") or "")[:12000]
            rec["error"] = (j.get("error") or "")[:800]
            rec["engine"] = j.get("engine") or mode
            break
        process_one()
        time.sleep(0.25)
    else:
        rec["status"] = "timeout"
        rec["ok"] = False
        rec["error"] = "leaf harness timeout"
        try:
            from pocket.jobs import cancel_job

            cancel_job(job["id"], reason="rah leaf timeout")
        except Exception:
            pass

    if sub_rah:
        rec["sub_rah"] = {
            "run_id": sub_rah.get("run_id"),
            "ok": sub_rah.get("ok"),
            "leaves": sub_rah.get("completed"),
            "synthesis_head": (sub_rah.get("synthesis") or "")[:1500],
        }

    rec["finished_at"] = time.time()
    rec["duration_sec"] = round(rec["finished_at"] - started, 2)

    # Persist leaf artifact on filesystem (parent context stays light)
    try:
        leaf_path = run_dir(run_id) / "leaves" / f"{lid}.json"
        leaf_path.write_text(json.dumps(rec, indent=2, default=str)[:200_000], encoding="utf-8")
        md_path = run_dir(run_id) / "leaves" / f"{lid}.md"
        md_path.write_text(
            f"# RAH leaf {lid}\n\n**mode:** {mode} · **depth:** {depth}\n\n"
            f"## Goal\n{goal[:2000]}\n\n## Result\n\n{rec.get('result') or rec.get('error') or ''}\n",
            encoding="utf-8",
        )
    except Exception:
        pass

    try:
        from pocket.agentic_harness import _finish_live

        _finish_live(
            f"rah-{run_id}-{lid}",
            ok=bool(rec.get("ok")),
            summary=str(rec.get("result") or rec.get("error") or "")[:200],
        )
    except Exception:
        pass

    try:
        from pocket.pixel_vmem import put_artifact

        put_artifact(
            f"# RAH {lid}\n\n{rec.get('result') or ''}\n",
            title=f"rah-{run_id}-{lid}",
            language="md",
            agent="rah",
            agent_role="harness-leaf",
            ai_version=mode,
            run_id=run_id,
            tags=["rah", "harness", lid.lower()],
            note=f"depth={depth}",
        )
    except Exception:
        pass

    return rec


# ---------------------------------------------------------------------------
# Verify + synthesize
# ---------------------------------------------------------------------------

def _verify_results(run_id: str, task: str, leaves: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Adversarial / consistency check over leaf outputs (cheap plan pass)."""
    ok_n = sum(1 for L in leaves if L.get("ok"))
    fail_n = len(leaves) - ok_n
    conflicts: List[str] = []
    # Simple conflict: same file path claimed with opposite conclusions
    paths = {}
    for L in leaves:
        text = (L.get("result") or "") + " " + (L.get("goal") or "")
        for m in re.findall(r"[\w./\\-]+\.(?:py|ts|js|tsx|go|rs)\b", text):
            paths.setdefault(m, []).append(L.get("id"))
    for p, owners in paths.items():
        if len(set(owners)) > 3:
            conflicts.append(f"hotspot path {p} touched by {owners}")

    summary = {
        "ok": fail_n == 0 or ok_n >= max(1, len(leaves) // 2),
        "leaves_ok": ok_n,
        "leaves_fail": fail_n,
        "conflicts": conflicts[:12],
        "signal": "filesystem leaf md + job status",
        "advice": (
            "Independent slices preferred. For code migrations, pin ownership per package "
            "to avoid naming conflicts (classic RAH failure mode)."
        ),
    }
    try:
        (run_dir(run_id) / "verify" / "report.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
    except Exception:
        pass

    # Optional deeper verify job
    if str(os.environ.get("POCKET_RAH_DEEP_VERIFY") or "").strip() in ("1", "true", "yes"):
        try:
            from pocket.jobs import create_job, get as get_job, save as save_job
            from pocket.worker import process_one

            blob = "\n\n".join(
                f"### {L.get('id')}\nok={L.get('ok')}\n{(L.get('result') or '')[:1500]}"
                for L in leaves[:20]
            )
            vprompt = (
                "You are the RAH verification harness inside POCKET. "
                "Review leaf outputs for contradictions, missing coverage, and ship risk.\n\n"
                f"Parent task: {task[:1500]}\n\n{blob}"
            )
            vj = create_job(vprompt, name=f"rah-verify:{run_id}", mode=VERIFY_MODE)
            vj["_harness_inner"] = True
            save_job(vj)
            deadline = time.time() + 120
            process_one()
            while time.time() < deadline:
                j = get_job(vj["id"])
                if j and j.get("status") in ("done", "failed"):
                    summary["deep_verify"] = (j.get("result") or j.get("error") or "")[:4000]
                    break
                process_one()
                time.sleep(0.3)
        except Exception as e:
            summary["deep_verify_error"] = str(e)[:200]
    return summary


def _synthesize(run_id: str, task: str, leaves: List[Dict[str, Any]], verify: Dict[str, Any]) -> str:
    lines = [
        f"# RAH synthesis · `{run_id}`",
        "",
        f"**Protocol:** {PROTOCOL_ID} · **schema:** {SCHEMA}",
        f"**Parent task:** {task[:1500]}",
        "",
        f"**Leaves:** {len(leaves)} · ok={verify.get('leaves_ok')} fail={verify.get('leaves_fail')}",
        "",
        "## Leaf results",
    ]
    for L in leaves:
        status = "OK" if L.get("ok") else "FAIL"
        head = (L.get("result") or L.get("error") or "")[:900]
        lines.append(f"### {L.get('id')} · {status} · mode={L.get('mode')} · {L.get('duration_sec')}s")
        lines.append(head or "_(empty)_")
        lines.append("")
    if verify.get("conflicts"):
        lines.append("## Conflict signals")
        for c in verify["conflicts"]:
            lines.append(f"- {c}")
        lines.append("")
    lines.append("## Next steps (POCKET)")
    lines.append("1. Promote verified slices into Codex/Claude implementation sessions")
    lines.append("2. Use mesh/loomgraph for dependent follow-ups (not more blind parallel)")
    lines.append("3. Re-run RAH only when subtasks stay independent + cheap to verify")
    lines.append("")
    lines.append(f"_Artifacts: `~/.pocket/rah/{run_id}/`_")
    text = "\n".join(lines)
    try:
        (run_dir(run_id) / "synthesis.md").write_text(text, encoding="utf-8")
    except Exception:
        pass
    return text


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run_rah(
    task: str,
    *,
    plan: Optional[Dict[str, Any]] = None,
    depth: int = 0,
    max_depth: Optional[int] = None,
    max_parallel: Optional[int] = None,
    max_leaves: int = 16,
    parent_job_id: str = "",
    session_id: str = "",
    cwd: str = "",
    verify: bool = True,
    synthesize: bool = True,
    hint: str = "",
) -> Dict[str, Any]:
    """Execute a Recursive Agent Harness run (POCKET-native)."""
    max_depth, max_parallel = _limits(max_depth, max_parallel)
    if depth > max_depth:
        return {
            "ok": False,
            "error": f"max depth {max_depth} exceeded",
            "depth": depth,
            "protocol": PROTOCOL_ID,
        }

    run_id = f"rah-{uuid.uuid4().hex[:12]}"
    if depth > 0:
        run_id = f"rah-d{depth}-{uuid.uuid4().hex[:10]}"

    task = (task or "").strip()
    if not task and not plan:
        return {"ok": False, "error": "task or plan required", "protocol": PROTOCOL_ID}

    if not plan:
        plan = plan_fanout(task, max_leaves=max_leaves, hint=hint)
    else:
        plan = dict(plan)
        plan.setdefault("task", task)
        if not plan.get("leaves"):
            plan = plan_fanout(plan.get("task") or task, max_leaves=max_leaves, hint=hint)

    plan["max_depth"] = max_depth
    plan["max_parallel"] = max_parallel
    plan["depth"] = depth
    plan["run_id"] = run_id

    script_path = write_orchestration_script(run_id, plan)
    leaves_spec: List[Dict[str, Any]] = list(plan.get("leaves") or [])
    if not leaves_spec:
        return {"ok": False, "error": "empty plan", "run_id": run_id}

    started = time.time()
    run_rec: Dict[str, Any] = {
        "ok": True,
        "schema": SCHEMA,
        "protocol": PROTOCOL_ID,
        "run_id": run_id,
        "depth": depth,
        "max_depth": max_depth,
        "max_parallel": max_parallel,
        "task": task[:4000],
        "script": str(script_path),
        "status": "running",
        "started_at": started,
        "leaves_planned": len(leaves_spec),
        "session_id": session_id,
        "parent_job_id": parent_job_id,
    }
    with _lock:
        _RUNS[run_id] = run_rec
    try:
        (run_dir(run_id) / "run.json").write_text(
            json.dumps(run_rec, indent=2, default=str), encoding="utf-8"
        )
    except Exception:
        pass

    results: List[Dict[str, Any]] = []
    workers = min(max_parallel, len(leaves_spec))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rah-leaf") as pool:
        futs = {
            pool.submit(
                _run_leaf_harness,
                leaf,
                run_id=run_id,
                depth=depth,
                max_depth=max_depth,
                parent_job_id=parent_job_id,
                session_id=session_id,
                cwd=cwd,
                allow_recurse=depth + 1 < max_depth,
            ): leaf
            for leaf in leaves_spec
        }
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:
                leaf = futs[fut]
                results.append(
                    {
                        "id": leaf.get("id"),
                        "ok": False,
                        "status": "fail",
                        "error": str(e)[:400],
                        "goal": (leaf.get("goal") or "")[:300],
                    }
                )

    # Stable order by leaf id
    results.sort(key=lambda x: str(x.get("id") or ""))

    v_out: Dict[str, Any] = {"ok": True, "skipped": True}
    if verify and plan.get("verify", True):
        v_out = _verify_results(run_id, task, results)

    synthesis = ""
    if synthesize and plan.get("synthesize", True):
        synthesis = _synthesize(run_id, task, results, v_out)

    finished = time.time()
    ok_n = sum(1 for r in results if r.get("ok"))
    run_rec.update(
        {
            "status": "done",
            "ok": ok_n > 0 and (v_out.get("ok", True) or ok_n >= len(results) // 2),
            "finished_at": finished,
            "duration_sec": round(finished - started, 2),
            "completed": ok_n,
            "failed": len(results) - ok_n,
            "leaves": results,
            "verify": v_out,
            "synthesis": synthesis,
            "cost_note": (
                "RAH is ~15× a single-agent run — use only for independent, "
                "high-value work with a verification signal."
            ),
            "artifact_root": str(run_dir(run_id)),
        }
    )
    with _lock:
        _RUNS[run_id] = run_rec
    try:
        (run_dir(run_id) / "run.json").write_text(
            json.dumps(
                {k: v for k, v in run_rec.items() if k != "synthesis"}
                | {"synthesis_path": str(run_dir(run_id) / "synthesis.md")},
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass

    return run_rec


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        if run_id in _RUNS:
            return dict(_RUNS[run_id])
    p = ROOT / run_id / "run.json"
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def list_runs(*, limit: int = 30) -> Dict[str, Any]:
    items = []
    if ROOT.is_dir():
        for d in sorted(ROOT.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            if not d.is_dir():
                continue
            meta = get_run(d.name) or {"run_id": d.name}
            items.append(
                {
                    "run_id": d.name,
                    "ok": meta.get("ok"),
                    "status": meta.get("status"),
                    "task": (meta.get("task") or "")[:120],
                    "completed": meta.get("completed"),
                    "duration_sec": meta.get("duration_sec"),
                }
            )
    return {"ok": True, "schema": "pocket.rah.runs.v1", "runs": items, "root": str(ROOT)}


def status() -> Dict[str, Any]:
    with _lock:
        live = [r for r in _RUNS.values() if r.get("status") == "running"]
    return {
        "ok": True,
        "protocol": PROTOCOL_ID,
        "name": PROTOCOL_NAME,
        "live_runs": len(live),
        "defaults": manifest()["defaults"],
        "recent": list_runs(limit=8).get("runs") or [],
    }


def format_result_markdown(run: Dict[str, Any]) -> str:
    if not run:
        return "# RAH\n\n_(empty run)_"
    if run.get("synthesis"):
        return str(run["synthesis"])
    return (
        f"# RAH `{run.get('run_id')}`\n\n"
        f"ok={run.get('ok')} completed={run.get('completed')}/{run.get('leaves_planned')}\n\n"
        f"{(run.get('task') or '')[:500]}\n"
    )


# Executor entry
def run_rah_job(prompt: str, *, cwd: str = "", job: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
    job = job or {}
    # Allow JSON plan in prompt
    plan = None
    text = (prompt or "").strip()
    if text.startswith("{") and '"leaves"' in text:
        try:
            plan = json.loads(text)
            text = plan.get("task") or plan.get("prompt") or "RAH plan"
        except Exception:
            plan = None
    # Strip identity noise for planning seed
    seed = text
    for marker in ("[POCKET IDENTITY]", "# You are in POCKET", "[POCKET PLATFORM]"):
        if marker in seed:
            seed = seed.split(marker)[0].strip() or text[:2000]

    max_leaves = int(job.get("rah_max_leaves") or job.get("max_leaves") or 12)
    max_parallel = job.get("rah_max_parallel") or job.get("max_parallel")
    max_depth = job.get("rah_max_depth") or job.get("max_depth")

    run = run_rah(
        seed[:8000],
        plan=plan,
        depth=int(job.get("rah_depth") or 0),
        max_depth=max_depth,
        max_parallel=max_parallel,
        max_leaves=max_leaves,
        parent_job_id=str(job.get("id") or ""),
        session_id=str(job.get("session_id") or ""),
        cwd=cwd or job.get("cwd") or "",
        verify=job.get("rah_verify", True) is not False,
        synthesize=True,
    )
    md = format_result_markdown(run)
    err = "" if run.get("ok") else (run.get("error") or "rah completed with failures")
    return md, err, "rah"
