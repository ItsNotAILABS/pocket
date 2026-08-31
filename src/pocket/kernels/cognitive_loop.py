"""Five cognitive stages → real Pocket invoke, not a slide mapping.

Stages run on software lanes (min(32, CPUs)). Each stage names a being
the AI roster already knows. gemini-coder / sprint-orchestrator are
first-class aliases that route to real engines (Grok/Codex + HYDRA/RAH).
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

STAGES: List[Dict[str, str]] = [
    {"id": "sense", "agent": "scrutator", "job": "lookup", "why": "ingest + fetch"},
    {"id": "embed", "agent": "ghost", "job": "identity", "why": "local represent"},
    {"id": "plan", "agent": "plan", "job": "", "why": "outline only"},
    {"id": "act", "agent": "sprint-orchestrator", "job": "fanout", "why": "dispatch work"},
    {"id": "verify", "agent": "sentinel", "job": "", "why": "receipt / sanity"},
]

# Aliases the calibration report named — must resolve on the roster.
STAGE_ALIASES = {
    "gemini-coder": ["grok", "codex", "claude"],
    "sprint-orchestrator": ["hydra", "rah", "archon"],
    "sentinel": ["SENTINEL_HEADLESS", "scrutator"],
}


def _invoke(name: str, prompt: str, job: str = "") -> Dict[str, Any]:
    from pocket.agent_invoke import invoke

    # Try preferred name then aliases
    names = [name] + list(STAGE_ALIASES.get(name, []))
    last: Dict[str, Any] = {}
    for n in names:
        last = invoke(n, prompt=prompt, job=job, sync=False)
        if last.get("ok"):
            last["routed_as"] = n
            last["requested"] = name
            return last
    last.setdefault("ok", False)
    last["requested"] = name
    return last


def run_loop(
    goal: str,
    *,
    lanes: int = 0,
    parallel: bool = True,
    stages: Optional[List[str]] = None,
) -> Dict[str, Any]:
    from pocket.kernels.probe import probe_host
    from pocket.kernels.slab import get_cache

    host = probe_host()
    nlanes = lanes or int(host.get("logical_lanes") or 1)
    want = set(stages or [s["id"] for s in STAGES])
    plan = [s for s in STAGES if s["id"] in want]
    cache = get_cache("cognitive", size=256)
    buf = cache.alloc()
    t0 = time.perf_counter()
    results: List[Dict[str, Any]] = []

    def one(s: Dict[str, str]) -> Dict[str, Any]:
        st = time.perf_counter()
        r = _invoke(s["agent"], goal, job=s.get("job") or "")
        r["stage"] = s["id"]
        r["stage_ms"] = round((time.perf_counter() - st) * 1000, 3)
        r["why"] = s["why"]
        return r

    if parallel and len(plan) > 1:
        with ThreadPoolExecutor(max_workers=max(1, min(nlanes, len(plan)))) as ex:
            futs = {ex.submit(one, s): s["id"] for s in plan}
            for f in as_completed(futs):
                try:
                    results.append(f.result())
                except Exception as e:
                    results.append({"ok": False, "stage": futs[f], "error": str(e)})
        results.sort(key=lambda x: [s["id"] for s in plan].index(x.get("stage") or "") if x.get("stage") in [s["id"] for s in plan] else 99)
    else:
        results = [one(s) for s in plan]

    cache.free(buf)
    dt = time.perf_counter() - t0
    ok = all(r.get("ok") for r in results) if results else False
    return {
        "ok": ok,
        "schema": "pocket.kernel.cognitive_loop.v1",
        "goal": (goal or "")[:400],
        "stages": [s["id"] for s in plan],
        "lanes_used": min(nlanes, len(plan)),
        "logical_lanes": nlanes,
        "silicon_tensor_units": host.get("silicon_tensor_units"),
        "loop_ms": round(dt * 1000, 3),
        "results": results,
        "slab": cache.stats(),
        "note": "Stages invoke real roster agents. Loop ms is dispatch+queue, not LLM token time.",
    }
