"""POCKET Power — one command plane no vendor chat app has.

Sense the lab → pick a multi-workflow → run it on this host → receipt.
Custody stays here. Never auto-pay.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.power.v1"
ROOT = Path.home() / ".pocket" / "power"
RUNS = ROOT / "runs.jsonl"
ROOT.mkdir(parents=True, exist_ok=True)

THEIRS = {
    "name": "Vendor chat + rented browser + their cloud",
    "custody": "their_cloud",
    "signed_in_browser": "vendor_session",
    "phone_iot": "app_talks_to_their_cloud",
    "local_models": "optional_adapter",
    "billing_source": "their_store",
    "auto_pay": "sometimes_hidden",
    "host_tools": "none_or_rented",
    "workflows_on_host": 0,
}


def pulse() -> Dict[str, Any]:
    from pocket.mcp_fifty import catalog as tool_cat
    from pocket.multi_workflows import catalog as wf_cat
    from pocket.sovereign_stack import computing_clouds, stack_status

    clouds = computing_clouds()
    tools = tool_cat()
    wfs = wf_cat()
    stack = stack_status()
    last = recall(limit=1).get("runs") or []
    go_sum = None
    try:
        from pocket.go_plane import snapshot as go_snap

        g = go_snap()
        go_sum = {
            "active_count": g.get("active_count"),
            "workflow_count": g.get("workflow_count"),
            "working": g.get("working"),
            "armed": g.get("armed"),
            "workflow_status": g.get("workflow_status"),
            "go_count": g.get("go_count"),
        }
    except Exception:
        pass
    return {
        "ok": True,
        "schema": SCHEMA,
        "product": "POCKET Power",
        "tagline": "Host command plane — sense, route, run, receipt.",
        "clouds": clouds.get("count"),
        "cloud_ids": [c.get("id") for c in (clouds.get("clouds") or [])],
        "listening": [c.get("id") for c in (clouds.get("clouds") or []) if c.get("status") in ("listening", "primary", "ready")],
        "tools": tools.get("count"),
        "universal_tools": tools.get("universal"),
        "workflows": wfs.get("total"),
        "families": wfs.get("families"),
        "remote": (stack.get("remote") or {}).get("public_url"),
        "last_run": last[0] if last else None,
        "go": go_sum,
        "http": {
            "pulse": "GET /v1/power",
            "do": "POST /v1/power/do {goal}",
            "vs": "GET /v1/power/vs",
            "ui": "GET /power",
        },
    }


def vs_theirs() -> Dict[str, Any]:
    p = pulse()
    ours = {
        "name": "POCKET host + Forge + Engine + MESIE",
        "custody": "lab_host_sovereign",
        "signed_in_browser": "your_edge_profile",
        "phone_iot": "pair_plus_hz_mesh",
        "local_models": "auro_plus_mesie",
        "billing_source": "revenuecat_on_host",
        "auto_pay": "never",
        "host_tools": p.get("tools"),
        "workflows_on_host": p.get("workflows"),
        "clouds": p.get("clouds"),
    }
    axes = [
        {
            "axis": "Custody of logins and prompts",
            "ours": ours["custody"],
            "theirs": THEIRS["custody"],
            "we_win": True,
        },
        {
            "axis": "Signed-in browser",
            "ours": ours["signed_in_browser"],
            "theirs": THEIRS["signed_in_browser"],
            "we_win": True,
        },
        {
            "axis": "Phone + home IoT on the same desk",
            "ours": ours["phone_iot"],
            "theirs": THEIRS["phone_iot"],
            "we_win": True,
        },
        {
            "axis": "On-host tools (not a rented farm)",
            "ours": ours["host_tools"],
            "theirs": THEIRS["host_tools"],
            "we_win": True,
        },
        {
            "axis": "Named multi-agent workflows on the machine",
            "ours": ours["workflows_on_host"],
            "theirs": THEIRS["workflows_on_host"],
            "we_win": True,
        },
        {
            "axis": "Never auto-pay",
            "ours": ours["auto_pay"],
            "theirs": THEIRS["auto_pay"],
            "we_win": True,
        },
        {
            "axis": "Billing catalog you own",
            "ours": ours["billing_source"],
            "theirs": THEIRS["billing_source"],
            "we_win": True,
        },
    ]
    return {
        "ok": True,
        "schema": "pocket.power.vs.v1",
        "ours": ours,
        "theirs": THEIRS,
        "axes": axes,
        "score": f"{sum(1 for a in axes if a['we_win'])}/{len(axes)} axes on-host",
        "note": "Vendor apps rent a browser and a model. This plane runs the lab.",
    }


def _score(goal: str, wf: Dict[str, Any]) -> int:
    g = (goal or "").lower()
    blob = " ".join(
        [
            wf.get("id") or "",
            wf.get("title") or "",
            wf.get("family") or "",
            wf.get("desc") or "",
            " ".join(wf.get("agents") or []),
        ]
    ).lower()
    score = 0
    for tok in g.replace("/", " ").replace("-", " ").split():
        if len(tok) < 3:
            continue
        if tok in blob:
            score += 3
    hints = {
        "trade": "forge",
        "binance": "forge",
        "parallax": "forge",
        "paywall": "engine",
        "revenue": "billing",
        "shipaton": "engine",
        "spectrum": "mesie",
        "embed": "mesie",
        "phone": "phone_iot",
        "iot": "phone_iot",
        "voice": "voice_studio",
        "studio": "voice_studio",
        "nexus": "nexus",
        "morning": "daily",
        "evening": "daily",
        "ship": "ship",
        "paper": "research",
        "health": "triple",
        "cloud": "triple",
    }
    for k, fam in hints.items():
        if k in g and wf.get("family") == fam:
            score += 8
    return score


def pick(goal: str) -> Dict[str, Any]:
    from pocket.multi_workflows import WORKFLOWS

    ranked = sorted(WORKFLOWS, key=lambda w: _score(goal, w), reverse=True)
    top = ranked[0] if ranked else None
    return {
        "ok": bool(top),
        "goal": goal,
        "workflow_id": (top or {}).get("id"),
        "title": (top or {}).get("title"),
        "family": (top or {}).get("family"),
        "score": _score(goal, top) if top else 0,
        "alts": [{"id": w["id"], "title": w["title"], "score": _score(goal, w)} for w in ranked[1:4]],
    }


def do(goal: str, *, dry: bool = False, workflow_id: str = "") -> Dict[str, Any]:
    from pocket.multi_workflows import run as run_wf

    goal = (goal or "").strip()
    if not goal and not workflow_id:
        return {"ok": False, "error": "say a goal or pass workflow_id"}
    choice = {"workflow_id": workflow_id, "title": workflow_id, "goal": goal, "score": 99}
    if not workflow_id:
        choice = pick(goal)
        workflow_id = choice.get("workflow_id") or ""
    t0 = time.time()
    pulse_before = pulse()
    run = run_wf(workflow_id, dry=dry, params={"goal": goal, "text": goal})
    rec = {
        "schema": SCHEMA,
        "ts": time.time(),
        "goal": goal,
        "pick": choice,
        "run": {
            "ok": run.get("ok"),
            "workflow_id": run.get("workflow_id"),
            "passed": run.get("passed"),
            "total": run.get("total"),
            "ms": run.get("ms"),
            "log_path": run.get("log_path"),
        },
        "pulse_clouds": pulse_before.get("clouds"),
        "ms": int((time.time() - t0) * 1000),
        "ok": bool(run.get("ok")),
    }
    _append(rec)
    try:
        from pocket.go_plane import set_surface

        set_surface("power", status="ready" if rec.get("ok") else "fail", detail=goal or workflow_id)
    except Exception:
        pass
    try:
        from pocket.pixel_vmem import store_agent_run

        store_agent_run(
            agent="power",
            mode="power",
            prompt=goal or workflow_id,
            result=json.dumps(rec["run"], default=str)[:4000],
        )
    except Exception:
        pass
    return rec


def recall(limit: int = 8) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    if RUNS.is_file():
        for line in RUNS.read_text(encoding="utf-8", errors="replace").splitlines()[- max(1, limit) :]:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    rows.reverse()
    return {"ok": True, "count": len(rows), "runs": rows}


def morning() -> Dict[str, Any]:
    return do("morning seatbelt health clouds", workflow_id="mw097_morning_seatbelt")


def summarize_do(rec: Dict[str, Any]) -> str:
    pick = rec.get("pick") or {}
    run = rec.get("run") or {}
    title = pick.get("title") or run.get("workflow_id") or "workflow"
    ok = "ok" if rec.get("ok") else "partial"
    return (
        f"**Power** {ok}: {title} · "
        f"{run.get('passed') or 0}/{run.get('total') or 0} steps · "
        f"{run.get('ms') or rec.get('ms') or 0} ms.\n"
        f"Goal: {rec.get('goal') or '—'}\n"
        "Open `/power` to recall. Never auto-pay."
    )


def _append(rec: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    with RUNS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, default=str) + "\n")
