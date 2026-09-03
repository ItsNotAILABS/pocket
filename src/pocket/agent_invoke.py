"""Invoke EVERY first-class POCKET agent (the 127+ roster), plus Damian keepers.

Source of truth for who exists: pocket.first_class_agents.build_registry()
plus damian_fleet members. AIs never invent a name — they GET the roster.

  GET  /v1/agents/roster
  POST /v1/agents/invoke  {name, prompt, job?, sync?}
  GET  /v1/agents/autonomous
  skill agent_invoke · MCP pocket_agent_invoke
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from pocket.live_events import emit

SCHEMA = "pocket.agent_invoke.v1"


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "-").replace("_", "-")


def _entries() -> List[Dict[str, Any]]:
    """Flatten first-class registry + Damian keepers into invoke records."""
    items: List[Dict[str, Any]] = []
    seen: set = set()

    def add(rec: Dict[str, Any]) -> None:
        i = rec["id"]
        if i in seen:
            return
        seen.add(i)
        rec.setdefault("http", "POST /v1/agents/invoke")
        rec.setdefault("skill", "agent_invoke")
        rec.setdefault("mcp", "pocket_agent_invoke")
        items.append(rec)

    try:
        from pocket.first_class_agents import build_registry

        reg = build_registry(live=False)
        for a in reg.get("agents") or []:
            kind = str(a.get("kind") or "desk")
            invoke = {
                "desk": "job",
                "catalog": "headless",
                "swarm": "swarm",
                "latin": "latin",
                "design": "design",
                "headless": "headless_pack",
                "ship": "ship",
                "custom": "custom",
            }.get(kind, "dispatch")
            aliases = [str(x) for x in (a.get("aliases") or [])]
            if a.get("desk_mode"):
                aliases.append(str(a["desk_mode"]))
            if a.get("mention"):
                aliases.append(str(a["mention"]))
            if a.get("name"):
                aliases.append(str(a["name"]))
            add(
                {
                    "id": a["id"],
                    "name": a.get("name") or a["id"],
                    "kind": kind,
                    "group": a.get("group") or "",
                    "desk_mode": a.get("desk_mode") or "",
                    "engine": a.get("engine") or "",
                    "mention": a.get("mention") or "",
                    "invoke": invoke,
                    "autonomous": kind in ("headless",) or bool(a.get("harness") is False and kind == "headless"),
                    "blurb": (a.get("blurb") or a.get("role") or "")[:160],
                    "aliases": aliases,
                    "first_class": True,
                    "color": a.get("color") or "",
                }
            )
    except Exception:
        pass

    try:
        from pocket.damian_fleet import status as dst

        st = dst(include_all=True)
        for d in st.get("damians") or []:
            did = str(d.get("id") or "")
            if not did:
                continue
            add(
                {
                    "id": did,
                    "name": d.get("name") or did,
                    "kind": "damian",
                    "group": "Damian fleet",
                    "desk_mode": "",
                    "engine": "damian",
                    "mention": did,
                    "invoke": "damian",
                    "autonomous": True,
                    "blurb": f"{d.get('role') or 'keeper'} · organ={d.get('organ')}",
                    "aliases": [d.get("name") or "", d.get("role") or ""],
                    "first_class": False,
                    "internal": True,
                }
            )
        add(
            {
                "id": "damian-fleet",
                "name": "Damian fleet",
                "kind": "damian",
                "group": "Damian fleet",
                "invoke": "damian",
                "autonomous": True,
                "blurb": f"{st.get('count') or 0} internal keepers (max {st.get('max_count') or 100})",
                "aliases": ["damian", "damians", "keepers"],
                "first_class": False,
                "internal": True,
            }
        )
    except Exception:
        pass

    for extra_id, blurb, invoke, auto in (
        ("keep", "KEEP until chat ends", "keep", True),
        ("long-workflow", "Days-long cognitive workflow + context compact", "workflow", True),
        ("neuro-silicon", "Measured host lanes + slab + cognitive loop", "kernel", True),
        ("kernel-slab", "SLUB-shaped userspace slab", "kernel", True),
        ("gemini-coder", "Alias → grok/codex lane", "job", False),
        ("sprint-orchestrator", "Alias → RAH/HYDRA", "rah", True),
        ("rah", "Recursive harness fan-out", "rah", True),
        ("always-on-swarm", "Host pulse loop", "swarm", True),
        ("pocket-organism", "Mini heart + mini brain", "organism", True),
        ("mini-heart", "Host pulse", "organism", True),
        ("mini-brain", "Host thoughts", "organism", True),
        ("auro-endure", "Auro experiment-and-endure", "endure", True),
        ("codex", "First-class Codex CLI", "job", False),
        ("team-workspace", "Persistent long-work team folder", "team", True),
    ):
        add(
            {
                "id": extra_id,
                "name": extra_id,
                "kind": "runtime",
                "group": "Runtime",
                "invoke": invoke,
                "autonomous": auto,
                "blurb": blurb,
                "aliases": [],
                "first_class": False,
            }
        )
    return items


def roster() -> Dict[str, Any]:
    items = _entries()
    first = sum(1 for a in items if a.get("first_class"))
    auto = sum(1 for a in items if a.get("autonomous"))
    by_kind: Dict[str, int] = {}
    for a in items:
        by_kind[str(a.get("kind") or "?")] = by_kind.get(str(a.get("kind") or "?"), 0) + 1
    return {
        "ok": True,
        "schema": SCHEMA,
        "count": len(items),
        "first_class": first,
        "autonomous": auto,
        "by_kind": by_kind,
        "how": {
            "invoke": 'POST /v1/agents/invoke {"name":"<id from this list>","prompt":"…"}',
            "skill": 'POST /v1/skills/run {"skill":"agent_invoke","params":{"name":"researcher","prompt":"…"}}',
            "mcp": "pocket_agent_invoke · pocket_agent_roster",
            "mention": "@ARCHON / @sophia / @DESIGN — POST /v1/subagents/dispatch",
            "rule": "Name MUST be an id (or alias) from this roster. Do not invent agents.",
        },
        "agents": items,
    }


def _resolve(name: str) -> Optional[Dict[str, Any]]:
    raw = (name or "").strip()
    if not raw:
        return None
    n = _norm(raw)
    items = _entries()
    # ALL-CAPS mention (ARCHON, OCULUS, DESIGN) prefers the mesh/latin worker
    if raw.isupper() and raw.replace("_", "").isalnum() and len(raw) >= 3:
        for a in items:
            if str(a.get("mention") or "") == raw:
                return a
    # 1 exact id
    for a in items:
        if _norm(a["id"]) == n:
            return a
    # 2 mention / desk_mode
    for a in items:
        if _norm(str(a.get("mention") or "")) == n or _norm(str(a.get("desk_mode") or "")) == n:
            return a
    # 3 aliases / name
    for a in items:
        if _norm(str(a.get("name") or "")) == n:
            return a
        for al in a.get("aliases") or []:
            if _norm(str(al)) == n:
                return a
    # 4 suffix after catalog: latin: swarm:
    if ":" in n:
        tail = n.split(":", 1)[-1]
        return _resolve(tail)
    # 5 being doctrine alias
    try:
        from pocket.being_doctrine import get_being

        b = get_being(raw)
        if b:
            return _resolve(b["id"]) or _resolve(b["name"])
    except Exception:
        pass
    return None


def _queue_job(
    mode: str,
    prompt: str,
    *,
    session_id: str = "",
    name: str = "",
    team_id: str = "",
    cwd: str = "",
    owner: str = "",
) -> Dict[str, Any]:
    from pocket.jobs import create_job
    from pocket.worker import process_one

    job = create_job(
        prompt or f"invoked {mode}",
        name=(name or f"invoke:{mode}")[:40],
        mode=mode if mode else "plan",
        session_id=session_id or "",
        cwd=cwd or "",
        owner=owner or "",
        team_id=team_id or "",
    )
    try:
        process_one()
    except Exception:
        pass
    return {
        "ok": True,
        "queued": True,
        "job_id": job.get("id"),
        "mode": job.get("mode"),
        "status": job.get("status"),
        "poll": f"/v1/jobs/{job.get('id')}",
        "agent": name or mode,
    }


def invoke(
    name: str,
    *,
    prompt: str = "",
    job: str = "",
    session_id: str = "",
    params: Optional[Dict[str, Any]] = None,
    sync: bool = False,
) -> Dict[str, Any]:
    raw = (name or "").strip()
    params = params or {}
    prompt = (prompt or params.get("text") or params.get("message") or "").strip()
    job = (job or params.get("action") or params.get("job") or "").strip()
    session_id = session_id or str(params.get("session_id") or "")
    if params.get("sync") in (True, "1", "true", "yes"):
        sync = True
    emit("invoke", f"{raw}: {(prompt or job)[:80]}", agent=(raw or "INVOKE")[:24].upper(), role="invoke")

    if not raw:
        return {"ok": False, "error": "name required", "hint": "GET /v1/agents/roster", "count": roster()["count"]}

    rec = _resolve(raw)
    if not rec:
        # last chance: mesh dispatch so a typo still leaves an artifact
        try:
            from pocket.subagent_dispatch import dispatch

            d = dispatch(prompt or job or raw, agents=[raw.upper()], from_agent="AI")
            d["warning"] = f"{raw} is not on the first-class roster — dispatched as mesh mention"
            d["hint"] = "GET /v1/agents/roster"
            return d
        except Exception as e:
            return {"ok": False, "error": f"unknown agent {raw}: {e}", "hint": "GET /v1/agents/roster"}

    kind = rec.get("invoke") or rec.get("kind")
    aid = rec["id"]
    out: Dict[str, Any] = {"agent": aid, "name": rec.get("name"), "kind": rec.get("kind"), "resolved": rec["id"]}

    # --- runtime specials ---
    if kind == "team" or aid in ("team-workspace", "team", "long-work"):
        from pocket.team_workspace import get as team_get, list_teams, open_team

        try:
            from pocket.team_workspace import owner_from_user

            owner = owner_from_user({"user": str((params or {}).get("owner") or (params or {}).get("principal") or "pocket")})
        except ValueError as e:
            return {"ok": False, "error": str(e), **out}
        if (job or prompt or "").lower() in ("list", "status"):
            r = list_teams(principal=owner)
            r.update(out)
            return r
        if (params or {}).get("id") and not prompt:
            r = team_get(str(params.get("id")), principal=owner)
            r.update(out)
            return r
        r = open_team(
            prompt or job or "long work",
            agents=list((params or {}).get("agents") or []) or None,
            principal=owner,
        )
        r.update(out)
        return r
    if kind == "endure" or aid in ("auro-endure", "endure", "auro_endure"):
        from pocket.auro_endure import run as endure_run

        r = endure_run(prompt or job)
        r.update(out)
        return r
    if kind == "keep" or aid == "keep":
        from pocket.keep_agents import start as keep_start

        r = keep_start(
            session_id=session_id,
            goal=prompt or "Keep working until this chat ends",
            with_browser=bool(params.get("with_browser", False)),
        )
        r.update(out)
        return r
    if kind == "workflow" or aid in ("long-workflow", "workflow"):
        from pocket.kernels.long_workflow import get as wf_get, list_runs, start as wf_start, tick as wf_tick

        j = (job or prompt or "").lower()
        if "list" in j or "status" in j and not (params or {}).get("id"):
            r = list_runs()
            r.update(out)
            return r
        if (params or {}).get("id") and ("tick" in j or not prompt):
            r = wf_tick(str(params.get("id")))
            r.update(out)
            return r
        r = wf_start(prompt or job or "long workflow", session_id=session_id, max_hours=float((params or {}).get("max_hours") or 168))
        r.update(out)
        return r
    if kind == "kernel" or aid in ("neuro-silicon", "kernel-slab"):
        if aid == "kernel-slab" or "slab" in (job or prompt).lower():
            from pocket.kernels.slab import bench_slab, slab_status

            r = bench_slab() if "bench" in (job or prompt).lower() else slab_status()
            r.update(out)
            return r
        from pocket.kernels.neuro_silicon import calibrate, driver_status

        r = calibrate(run_loop="noloop" not in (job or prompt).lower(), goal=prompt) if (
            "calibrat" in (job or prompt).lower() or not job
        ) else driver_status()
        r.update(out)
        return r
    if kind == "rah" or aid == "rah" or aid == "sprint-orchestrator":
        from pocket.rah import run_rah

        r = run_rah(prompt or job or "fan out independent slices", session_id=session_id)
        if isinstance(r, dict):
            r.update(out)
        return r
    if kind == "organism" or aid in ("pocket-organism", "mini-heart", "mini-brain"):
        from pocket.organism import snapshot

        snap = snapshot()
        snap.update(out)
        snap["ok"] = True
        return snap
    if kind == "swarm" and aid in ("always-on-swarm",):
        from pocket.always_on_swarm import start, status

        r = status() if (job or prompt).lower() in ("status", "health", "") else start()
        r.update(out)
        return r
    if kind == "damian" or rec.get("kind") == "damian":
        from pocket.damian_fleet import pulse_now, ensure_running

        ensure_running()
        r = pulse_now(n=1 if aid != "damian-fleet" else None)
        r.update(out)
        r["ok"] = True
        return r

    # --- latin ---
    if kind == "latin" or rec.get("kind") == "latin":
        from pocket.alpha_workers import get_worker, run_worker

        latin = (rec.get("mention") or rec.get("name") or aid.split(":")[-1]).upper()
        w = get_worker(latin)
        if w:
            jobs = [str(x).lower() for x in (w.get("jobs") or [])]
            j = job.lower()
            if not j or j not in jobs + ["help", "identity", "who"]:
                token = (prompt.split() or ["help"])[0].lower().strip(",.:")
                j = token if token in jobs else "help"
            md, err, eng = run_worker(w["id"], j, prompt=prompt, params=params)
            out.update({"ok": not err, "job": j, "engine": eng, "markdown": md, "error": err or ""})
            return out

    # --- design / ship / headless pack ---
    mention = (rec.get("mention") or rec.get("name") or aid.split(":")[-1]).upper()
    if kind == "design" or rec.get("kind") == "design":
        from pocket.design_agents import run_design_agent

        r = run_design_agent(mention, prompt or job or "critique")
        if isinstance(r, dict):
            r.update(out)
        return r
    if kind == "ship" or rec.get("kind") == "ship":
        from pocket.ship_agents import run_ship_agent

        r = run_ship_agent(mention, prompt or job or "status")
        if isinstance(r, dict):
            r.update(out)
        return r
    if kind == "headless_pack" or rec.get("kind") == "headless":
        from pocket.subagent_dispatch import _run_headless

        r = _run_headless(mention, prompt or job)
        if isinstance(r, dict):
            r.update(out)
        return r

    # --- catalog SKU (researcher, coder, …) ---
    if kind == "headless" or rec.get("kind") == "catalog":
        from pocket.agents import run_headless

        sku = aid.split(":", 1)[-1] if aid.startswith("catalog:") else aid
        r = run_headless(sku, prompt or job or f"run {sku}", sync=bool(sync))
        if isinstance(r, dict):
            r.update(out)
        return r

    # --- coding swarm personas ---
    if rec.get("kind") == "swarm" or kind == "swarm":
        from pocket.coding_swarm import run_coding_swarm

        tagged = prompt or job
        handle = rec.get("mention") or aid.split(":")[-1]
        if handle and f"@{handle}" not in tagged.lower():
            tagged = f"@{handle} {tagged}".strip()
        md, err, eng = run_coding_swarm(tagged, session_id=session_id)
        out.update({"ok": not err, "markdown": md, "error": err or "", "engine": eng})
        return out

    # --- custom ---
    if rec.get("kind") == "custom" or kind == "custom":
        from pocket.custom_agents import run_custom_agent

        cid = aid.split(":", 1)[-1] if ":" in aid else aid
        r = run_custom_agent(cid, prompt or job)
        if isinstance(r, dict):
            r.update(out)
        return r

    # --- desk / engine: real job on this host ---
    mode = rec.get("desk_mode") or rec.get("engine") or aid
    if rec.get("kind") == "desk" or kind == "job":
        try:
            from pocket.agent_habitat import pulse

            pulse(str(mode), status="working", task=(prompt or job)[:80], line=f"invoked {aid}")
        except Exception:
            pass
        q = _queue_job(
            str(mode),
            prompt or job,
            session_id=session_id,
            name=str(rec.get("name") or aid),
            team_id=str((params or {}).get("team_id") or ""),
            cwd=str((params or {}).get("cwd") or ""),
            owner=str((params or {}).get("owner") or ""),
        )
        q.update(out)
        return q

    # --- NEXUS / MESIE companions still in first-class as desk ---
    if aid in ("nexus",) or str(rec.get("engine")) == "nexus":
        try:
            from pocket.nexus_bridge import run_worker as nx

            r = nx(job or "status", prompt or "status", params)
            if isinstance(r, dict):
                r.update(out)
                return r
        except Exception as e:
            out.update({"ok": False, "error": str(e)})
            return out

    # fallback mesh
    from pocket.subagent_dispatch import dispatch

    d = dispatch(prompt or job or aid, agents=[mention or aid.upper()], from_agent="AI")
    d.update(out)
    return d


def autonomous_status() -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": True, "schema": "pocket.autonomous.v1", "ts": time.time(), "systems": {}}

    def _put(key: str, fn) -> None:
        try:
            out["systems"][key] = fn()
        except Exception as e:
            out["systems"][key] = {"ok": False, "error": str(e)}

    _put("keep", lambda: __import__("pocket.keep_agents", fromlist=["status"]).status())
    _put("swarm", lambda: __import__("pocket.always_on_swarm", fromlist=["status"]).status())
    _put("dream", lambda: __import__("pocket.dream_mode", fromlist=["status"]).status())
    _put("organism", lambda: __import__("pocket.organism", fromlist=["snapshot"]).snapshot())
    try:
        from pocket.time_capsules import status as cap_st

        out["systems"]["capsules"] = cap_st()
    except Exception as e:
        out["systems"]["capsules"] = {"ok": False, "error": str(e)}
    try:
        from pocket.agent_hook import hook_status

        out["systems"]["mesh_hook"] = hook_status()
    except Exception as e:
        out["systems"]["mesh_hook"] = {"ok": False, "error": str(e)}
    try:
        from pocket.damian_fleet import status as dst

        out["systems"]["damian"] = dst()
    except Exception as e:
        out["systems"]["damian"] = {"ok": False, "error": str(e)}
    try:
        from pocket.rah import status as rst

        out["systems"]["rah"] = rst()
    except Exception as e:
        out["systems"]["rah"] = {"ok": False, "error": str(e)}
    running = [
        k
        for k, v in out["systems"].items()
        if isinstance(v, dict)
        and (v.get("running") or (v.get("ok") and (v.get("alive") or (v.get("heart") or {}).get("alive"))))
    ]
    out["running"] = running
    out["roster_count"] = len(_entries())
    return out


def ensure_autonomous() -> Dict[str, Any]:
    notes: List[str] = []
    try:
        from pocket.agent_hook import ensure_mesh_hook

        ensure_mesh_hook()
        notes.append("mesh_hook")
    except Exception as e:
        notes.append(f"mesh_hook skipped: {e}")
    try:
        from pocket.always_on_swarm import ensure_running

        ensure_running()
        notes.append("swarm")
    except Exception as e:
        notes.append(f"swarm skipped: {e}")
    try:
        from pocket.dream_mode import ensure_running as er

        er()
        notes.append("dream")
    except Exception as e:
        notes.append(f"dream skipped: {e}")
    try:
        from pocket.damian_fleet import ensure_running as ed

        ed()
        notes.append("damian")
    except Exception as e:
        notes.append(f"damian skipped: {e}")
    st = autonomous_status()
    st["armed"] = notes
    return st
