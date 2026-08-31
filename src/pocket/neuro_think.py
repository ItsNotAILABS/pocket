"""Spherical neuro thinking — embed POCKET neuro tech into primary engines.

Not a prompt slogan. Regions actually compute in parallel around the task
(connectome-style), then a compact packet is injected into Grok / Claude /
Codex / Spark / Auro so they work more rounded: perceive, remember, plan,
compute, act, verify — together, not as a linear chat.

Regions (internal, no third-party brain API):
  sensory      — classify the work
  hippocampus  — World Model recall + fact-check
  prefrontal   — Heuristic local plan
  cerebellum   — Ghost / Logic / Pattern when the task is computational
  motor        — which host skills fit
  dmn          — self / POCKET identity stance
  critic       — missing info + how to know it's done
  silicon      — measured host lanes (cached)

Codex gets a 2-line critic (token-lean). The others get the sphere packet.
"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from pocket.live_events import emit

NEURO_ENGINES = frozenset(
    {
        "grok",
        "novae_grok",
        "claude",
        "codex",
        "novae_codex",
        "muse_spark",
        "muse",
        "spark",
        "auro",
        "auro14b",
        "ro14b",
        "him",
    }
)

_silicon_cache: Dict[str, Any] = {"ts": 0.0, "host": {}}


def _silicon() -> Dict[str, Any]:
    now = time.time()
    if now - float(_silicon_cache.get("ts") or 0) < 90 and _silicon_cache.get("host"):
        return _silicon_cache["host"]
    try:
        from pocket.kernels.probe import probe_host

        h = probe_host()
        slim = {
            "lanes": h.get("logical_lanes"),
            "cpus": h.get("cpus"),
            "tensor_units": h.get("silicon_tensor_units"),
            "backends": h.get("backends") or [],
        }
    except Exception:
        slim = {"lanes": 1, "cpus": 1, "tensor_units": 0, "backends": []}
    _silicon_cache["ts"] = now
    _silicon_cache["host"] = slim
    return slim


def _classify(prompt: str) -> str:
    low = (prompt or "").lower()
    if any(k in low for k in ("prove", "gcd", "prime", "hash", "phi", "theorem", "math")):
        return "math"
    if any(k in low for k in ("edit", "fix", "patch", "code", "file", "repo", "test", "bug")):
        return "code"
    if any(k in low for k in ("research", "why", "explain", "brief", "lookup", "what is")):
        return "research"
    if any(k in low for k in ("image", "visual", "imagine", "design", "ui", "screen")):
        return "create"
    if any(k in low for k in ("buy", "book", "schedule", "email", "ops", "follow")):
        return "ops"
    return "general"


def _region_sensory(prompt: str, mode: str) -> Dict[str, Any]:
    words = re.findall(r"[A-Za-z0-9_./-]{3,}", prompt or "")
    uniq = []
    for w in words:
        lw = w.lower()
        if lw not in uniq:
            uniq.append(w)
    return {
        "region": "sensory",
        "class": _classify(prompt),
        "entities": uniq[:8],
        "mode": mode,
    }


def _region_hippocampus(prompt: str) -> Dict[str, Any]:
    try:
        from pocket import world_model as wm

        wm.ensure_db()
        hits = wm.search(prompt or "", kind="all", limit=4)
        fc = wm.fact_check(prompt or "")
        facts = []
        for h in (hits.get("results") or [])[:4]:
            if isinstance(h, dict):
                facts.append(
                    str(h.get("text") or h.get("name") or h.get("subject") or h)[:80]
                )
            else:
                facts.append(str(h)[:80])
        return {
            "region": "hippocampus",
            "facts": facts,
            "supported": fc.get("supported"),
            "n": len(hits.get("results") or []),
        }
    except Exception as e:
        return {"region": "hippocampus", "error": str(e)[:80], "facts": []}


def _region_prefrontal(prompt: str) -> Dict[str, Any]:
    p = (prompt or "").strip()
    kind = _classify(p)
    steps = {
        "code": ["Find the exact file", "Make the smallest real edit", "Run a verify command"],
        "math": ["Compute locally (Ghost/Logic)", "Show the receipt", "Do not guess the number"],
        "research": ["Recall world facts", "Fetch only if needed", "Cite + one next action"],
        "create": ["Compose or preview on host", "Show the file", "Don't invent a generator"],
        "ops": ["List the steps", "Never auto-pay", "Ask the user to confirm"],
        "general": [f"Clarify: {p[:72]}", "One concrete host step", "Leave a receipt"],
    }
    return {"region": "prefrontal", "plan": steps.get(kind, steps["general"]), "ok": True}


def _region_cerebellum(prompt: str) -> Dict[str, Any]:
    low = (prompt or "").lower()
    want_math = any(
        k in low for k in ("math", "prove", "gcd", "prime", "hash", "phi", "number", "count", "stats")
    )
    if not want_math:
        return {"region": "cerebellum", "engaged": False}
    try:
        from pocket.ghost_math import run_ghost

        text, err, eng = run_ghost(prompt)
        return {
            "region": "cerebellum",
            "engaged": True,
            "engine": eng,
            "digest": (text or err or "")[:280],
        }
    except Exception as e:
        return {"region": "cerebellum", "engaged": True, "error": str(e)[:80]}


def _region_motor(prompt: str, mode: str) -> Dict[str, Any]:
    skills: List[str] = []
    low = (prompt or "").lower()
    table = [
        ("code", "platform_map"),
        ("file", "platform_map"),
        ("screen", "screen_sense"),
        ("imagine", "imagine_compose"),
        ("bot", "bots_list"),
        ("proof", "foundations_map"),
        ("math", "foundations_map"),
        ("search", "web_search"),
        ("phone", "phone_surface"),
    ]
    for key, skill in table:
        if key in low and skill not in skills:
            skills.append(skill)
    if mode in ("codex", "novae_codex") and "platform_map" not in skills:
        skills.append("platform_map")
    return {"region": "motor", "skills": skills[:4] or ["platform_map"]}


def _region_dmn(mode: str) -> Dict[str, Any]:
    stance = {
        "codex": "Write real files. Verify. Short human summary.",
        "novae_codex": "Nova coding hands in tenant workspace.",
        "grok": "Research+code here. Cite fetches. Don't auto-publish.",
        "novae_grok": "Nova research hands. Plan then act.",
        "claude": "Tool loop with receipts. Stay POCKET's agent.",
        "muse_spark": "Parallel lanes then one synthesis.",
        "muse": "Parallel lanes then one synthesis.",
        "spark": "Parallel lanes then one synthesis.",
        "auro": "Local meaning. No third-party LLM required.",
        "auro14b": "Local Auro LMR. Physics/meaning first.",
    }
    return {
        "region": "dmn",
        "self": "POCKET host agent",
        "stance": stance.get(mode, "Help the user operate POCKET on this host."),
    }


def _region_critic(prompt: str, kind: str) -> Dict[str, Any]:
    missing = []
    low = (prompt or "").lower()
    if kind == "code" and not any(k in low for k in ("file", "path", "test", "repo", ".py", ".ts")):
        missing.append("concrete path or test")
    if kind == "ops" and "confirm" not in low:
        missing.append("user confirmation before pay/send")
    if len((prompt or "").strip()) < 8:
        missing.append("a real task")
    verify = {
        "code": "diff + test or command that proves it",
        "math": "internal Ghost/Logic receipt, not a guessed number",
        "research": "named sources + one next action",
        "create": "preview/file the user can open",
        "ops": "checklist + who must confirm",
        "general": "one artifact on the host",
    }.get(kind, "one host artifact")
    return {"region": "critic", "missing": missing[:3], "done_when": verify}


def think(prompt: str, *, mode: str = "", timeout_s: float = 0.85) -> Dict[str, Any]:
    """Run the sphere in parallel. Fast. Internal only."""
    t0 = time.perf_counter()
    mode = (mode or "").strip().lower()
    kind = _classify(prompt)
    silicon = _silicon()
    regions: Dict[str, Any] = {}

    jobs = {
        "sensory": lambda: _region_sensory(prompt, mode),
        "hippocampus": lambda: _region_hippocampus(prompt),
        "prefrontal": lambda: _region_prefrontal(prompt),
        "cerebellum": lambda: _region_cerebellum(prompt),
        "motor": lambda: _region_motor(prompt, mode),
        "dmn": lambda: _region_dmn(mode),
        "critic": lambda: _region_critic(prompt, kind),
    }
    with ThreadPoolExecutor(max_workers=7) as ex:
        futs = {ex.submit(fn): name for name, fn in jobs.items()}
        try:
            for f in as_completed(futs, timeout=timeout_s):
                name = futs[f]
                try:
                    regions[name] = f.result()
                except Exception as e:
                    regions[name] = {"region": name, "error": str(e)[:80]}
        except TimeoutError:
            for f, name in futs.items():
                if name not in regions:
                    regions[name] = {"region": name, "error": "timeout"}

    packet = format_packet(kind, mode, silicon, regions)
    compact = format_compact(kind, regions)
    out = {
        "ok": True,
        "schema": "pocket.neuro_think.v1",
        "spherical": True,
        "internal": True,
        "third_party": False,
        "kind": kind,
        "mode": mode,
        "silicon": silicon,
        "regions": regions,
        "packet": packet,
        "compact": compact,
        "ms": round((time.perf_counter() - t0) * 1000, 2),
    }
    try:
        emit("neuro", f"{mode or 'agent'} {kind} {out['ms']}ms", agent="NEURO", role="python")
    except Exception:
        pass
    # Silent subcortex writeback — never block the engine turn
    try:
        import threading
        from pocket.cortex_subcortex import start_dual

        threading.Thread(
            target=start_dual,
            kwargs={"goal": prompt or "", "session_id": "", "mode": mode or "neuro", "wait_subcortex_ms": 0},
            daemon=True,
            name="neuro-subcortex",
        ).start()
    except Exception:
        pass
    return out


def format_packet(kind: str, mode: str, silicon: Dict[str, Any], regions: Dict[str, Any]) -> str:
    hip = regions.get("hippocampus") or {}
    pre = regions.get("prefrontal") or {}
    cer = regions.get("cerebellum") or {}
    mot = regions.get("motor") or {}
    dmn = regions.get("dmn") or {}
    cri = regions.get("critic") or {}
    facts = "; ".join(hip.get("facts") or [])[:220] or "none yet"
    plan = " | ".join((pre.get("plan") or [])[:3])[:220]
    skills = ",".join(mot.get("skills") or [])
    missing = ",".join(cri.get("missing") or []) or "—"
    math = ""
    if cer.get("engaged"):
        math = f"\nmath: {(cer.get('digest') or '')[:180]}"
    return (
        "[NEURO SPHERE] Think with all regions at once — perception, memory, plan, compute, act, verify.\n"
        f"class={kind} engine={mode or 'host'} lanes={silicon.get('lanes')} "
        f"backends={','.join(silicon.get('backends') or []) or 'cpu'}\n"
        f"self: {dmn.get('stance') or 'POCKET host agent'}\n"
        f"memory: {facts}\n"
        f"plan: {plan}\n"
        f"skills: {skills}\n"
        f"missing: {missing}\n"
        f"done_when: {cri.get('done_when')}"
        f"{math}\n"
        "Do not skip critic. Prefer one verified host artifact over a long essay."
    )


def format_compact(kind: str, regions: Dict[str, Any]) -> str:
    cri = regions.get("critic") or {}
    mot = regions.get("motor") or {}
    return (
        f"NEURO: class={kind} verify={cri.get('done_when')} "
        f"skills={','.join((mot.get('skills') or [])[:3])}"
    )


def inject(prompt: str, *, mode: str = "") -> Tuple[str, Dict[str, Any]]:
    """Attach a neuro packet (or compact line for Codex) unless already present."""
    base = prompt or ""
    m = (mode or "").strip().lower()
    if m not in NEURO_ENGINES:
        return base, {"ok": False, "skipped": True}
    if "[NEURO SPHERE]" in base[:2500] or "NEURO: class=" in base[:800]:
        return base, {"ok": True, "already": True}
    packet = think(base, mode=m)
    if m in ("codex", "novae_codex"):
        extra = packet.get("compact") or ""
    else:
        extra = packet.get("packet") or ""
    if not extra:
        return base, packet
    return base.rstrip() + "\n\n" + extra + "\n", packet
