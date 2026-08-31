"""100 multi-agent workflows — each is a DAG of MCP pack tools.

Catalog: GET /v1/workflows/multi
Run:     POST /v1/workflows/multi/run  {"id":"mw001_stack_health"}
MCP:     multi_workflows · multi_workflow_run · multi_workflow_get
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.multi_workflows.v1"
OUT = Path.home() / ".pocket" / "multi_workflows"
OUT.mkdir(parents=True, exist_ok=True)


def _w(
    wid: str,
    title: str,
    family: str,
    agents: List[str],
    steps: List[str],
    desc: str = "",
) -> Dict[str, Any]:
    return {
        "id": wid,
        "title": title,
        "family": family,
        "agents": agents,
        "steps": [{"id": i + 1, "tool": s} for i, s in enumerate(steps)],
        "step_count": len(steps),
        "desc": desc or title,
        "multi": True,
    }


WORKFLOWS: List[Dict[str, Any]] = [
    # --- triple stack (10) ---
    _w("mw001_stack_health", "Triple-stack health sweep", "triple", ["ARCHON"],
       ["universal_health", "universal_ports", "universal_clouds", "universal_version"]),
    _w("mw002_stack_map", "Map all desks and roots", "triple", ["ARCHON", "SCRUTATOR"],
       ["universal_stack_map", "universal_lab_roots", "repo_map", "which_pocket"]),
    _w("mw003_who_runs_what", "Identity + doctrine + route", "triple", ["ARCHON"],
       ["universal_whoami", "universal_doctrine", "charter_brief", "universal_route"]),
    _w("mw004_billing_across", "Shared billing on every desk", "triple", ["ARCHON", "SHIP"],
       ["universal_billing_plans", "billing_aliases", "engine_billing", "pocket_economy"]),
    _w("mw005_listen_sweep", "Who is listening", "triple", ["SENTINEL"],
       ["pocket_health_http", "forge_listening", "engine_listening", "voice_health"]),
    _w("mw006_sdk_tour", "Internal SDK + MESIE + Forge", "triple", ["FORGE", "ARCHON"],
       ["universal_sdk", "universal_mesie", "universal_forge", "universal_engine"]),
    _w("mw007_git_three", "Git present on three trees", "triple", ["FORGE"],
       ["universal_git_hint", "forge_github", "engine_github", "pocket_github"]),
    _w("mw008_receipt_day", "Write a daily receipt", "triple", ["SCRIBE", "GHOST"],
       ["universal_time", "universal_calendar", "universal_receipt", "universal_notes_list"]),
    _w("mw009_decide_goal", "Route a goal then ping target", "triple", ["ARCHON"],
       ["universal_goal", "universal_decide", "universal_ping", "universal_ok"]),
    _w("mw010_ports_and_urls", "Ports, tunnel, desk, phone", "triple", ["NAVIGATOR"],
       ["universal_ports", "pocket_public_url", "pocket_desk", "pocket_phone"]),
    # --- pocket (15) ---
    _w("mw011_pocket_boot", "POCKET boot card", "pocket", ["ARCHON"],
       ["pocket_version", "pocket_edition", "pocket_heart", "pocket_brain"]),
    _w("mw012_pocket_face", "Company / org / fish", "pocket", ["SCRIBE"],
       ["pocket_company", "pocket_org", "pocket_fish", "pocket_class"]),
    _w("mw013_pocket_surfaces", "Every product surface", "pocket", ["NAVIGATOR"],
       ["pocket_surfaces", "pocket_landing", "pocket_studio", "pocket_wiki", "pocket_swarm"]),
    _w("mw014_pocket_work_urls", "Work + working + download", "pocket", ["ARCHON"],
       ["pocket_work", "pocket_working", "pocket_download", "pocket_install"]),
    _w("mw015_pocket_habitat", "Habitat + agents + skills", "pocket", ["ARCHON"],
       ["pocket_habitat", "pocket_agents", "pocket_skills", "list_skills"]),
    _w("mw016_pocket_docs", "Docs + protocols + auth", "pocket", ["SCRIBE"],
       ["pocket_docs", "pocket_protocols", "pocket_auth_hint", "pocket_api"]),
    _w("mw017_pocket_identity", "Identity brief + charter", "pocket", ["SCRIBE"],
       ["pocket_identity", "charter_brief", "universal_whoami"]),
    _w("mw018_pocket_economy", "Economy snapshot + billing", "pocket", ["SHIP"],
       ["pocket_economy", "billing_plans", "billing_seats"]),
    _w("mw019_pocket_highlights", "Health highlights + upgrade", "pocket", ["ARCHON"],
       ["pocket_highlights", "pocket_upgrade", "pocket_heartbeat"]),
    _w("mw020_pocket_uses", "Product uses list", "pocket", ["ARCHON"],
       ["pocket_uses", "universal_catalog", "universal_search_tools"]),
    _w("mw021_pocket_mail", "Mail ready check", "pocket", ["SCRIBE"],
       ["mail_ok", "mail_status"]),
    _w("mw022_pocket_studio_ok", "Studio surface check", "pocket", ["SHIP"],
       ["studio_ok", "pocket_studio"]),
    _w("mw023_pocket_mesh", "Mesh + vdisk", "pocket", ["VCOMP"],
       ["mesh_paths", "mesh_ok", "vdisk_ok"]),
    _w("mw024_pocket_tunnel", "Public tunnel check", "pocket", ["NAVIGATOR"],
       ["tunnel_ok", "pocket_public_url", "phone_remote"]),
    _w("mw025_pocket_which", "Which tree is live", "pocket", ["ARCHON"],
       ["which_pocket", "pocket_version", "universal_cwd"]),
    # --- forge (12) ---
    _w("mw026_forge_boot", "Forge boot card", "forge", ["FORGE"],
       ["forge_root", "forge_available", "forge_port", "forge_url"]),
    _w("mw027_forge_live", "Forge live status", "forge", ["FORGE"],
       ["forge_listening", "forge_health", "forge_status"]),
    _w("mw028_forge_book", "Strategies + products + ledger", "forge", ["FORGE", "GHOST"],
       ["forge_strategies", "forge_products", "forge_ledger"]),
    _w("mw029_forge_trade_prep", "Trade prep (no auto-spend)", "forge", ["FORGE", "SENTINEL"],
       ["forge_market", "forge_budget", "forge_cli_hint"]),
    _w("mw030_forge_parallax", "PARALLAX pairs + adapter", "forge", ["FORGE"],
       ["forge_pairs", "parallax_status"]),
    _w("mw031_forge_papers", "Papers + adapters + dist", "forge", ["SCRIBE"],
       ["forge_papers", "forge_adapters", "forge_dist"]),
    _w("mw032_forge_ship", "Serve command + GitHub", "forge", ["SHIP"],
       ["forge_serve_cmd", "forge_github", "forge_readme"]),
    _w("mw033_forge_agents", "High-level agents + workflows", "forge", ["ARCHON"],
       ["forge_agents", "forge_workflows"]),
    _w("mw034_forge_electron", "Desktop shell present", "forge", ["FORGE"],
       ["forge_electron", "forge_available"]),
    _w("mw035_forge_route", "Route a trade goal", "forge", ["ARCHON"],
       ["universal_route", "forge_status", "universal_receipt"]),
    _w("mw036_forge_mesie_bridge", "Forge + MESIE together", "forge", ["GHOST"],
       ["universal_forge", "universal_mesie", "mesie_ok"]),
    _w("mw037_forge_health_only", "Listening or not", "forge", ["SENTINEL"],
       ["forge_listening", "universal_ports"]),
    # --- engine (12) ---
    _w("mw038_engine_boot", "Engine boot card", "engine", ["SHIP"],
       ["engine_root", "engine_available", "engine_github"]),
    _w("mw039_engine_listen", "Dash + API up", "engine", ["SENTINEL"],
       ["engine_dash", "engine_api", "engine_listening"]),
    _w("mw040_engine_cores", "Six nextgen cores", "engine", ["FORGE"],
       ["engine_cores", "engine_xfin", "engine_pulse", "engine_aura"]),
    _w("mw041_engine_token", "MINT + NEXS + GRID", "engine", ["FORGE"],
       ["engine_mint", "engine_nexs", "engine_grid"]),
    _w("mw042_engine_ppp", "PPP localization", "engine", ["SHIP"],
       ["engine_ppp", "billing_usd"]),
    _w("mw043_engine_docs", "Whitepaper + onboarding", "engine", ["SCRIBE"],
       ["engine_readme", "engine_whitepaper", "engine_onboarding"]),
    _w("mw044_engine_shipaton", "Shipaton artifacts", "engine", ["SHIP"],
       ["engine_android", "engine_docker", "engine_tests"]),
    _w("mw045_engine_bus", "Substrate bus + lifecycle", "engine", ["ARCHON"],
       ["engine_bus", "engine_lifecycle"]),
    _w("mw046_engine_billing", "Engine uses shared catalog", "engine", ["SHIP"],
       ["engine_billing", "billing_pro", "billing_aliases"]),
    _w("mw047_engine_grid_iot", "GRID + HZ + phone", "engine", ["NAVIGATOR"],
       ["grid_probe", "hz_mesh", "pocket_phone"]),
    _w("mw048_engine_route", "Route a paywall goal", "engine", ["ARCHON"],
       ["universal_goal", "universal_decide", "engine_available"]),
    _w("mw049_engine_health", "Engine + billing health", "engine", ["SENTINEL"],
       ["universal_engine", "universal_billing_plans"]),
    # --- mesie (10) ---
    _w("mw050_mesie_boot", "MESIE import card", "mesie", ["GHOST"],
       ["mesie_ok", "mesie_importable", "mesie_path"]),
    _w("mw051_mesie_version", "Runtime vs pip version", "mesie", ["GHOST"],
       ["mesie_version", "mesie_pip", "mesie_editable"]),
    _w("mw052_mesie_science", "Embed + engines list", "mesie", ["GHOST"],
       ["mesie_engines", "mesie_n_bands", "mesie_phase"]),
    _w("mw053_mesie_repo", "DOI + readme + bindings", "mesie", ["SCRIBE"],
       ["mesie_doi", "mesie_readme", "mesie_bindings"]),
    _w("mw054_mesie_root", "Repo on disk", "mesie", ["FORGE"],
       ["mesie_root_exists", "mesie_hub"]),
    _w("mw055_mesie_sdk", "SDK class probe", "mesie", ["GHOST"],
       ["mesie_sdk_class", "universal_mesie"]),
    _w("mw056_mesie_status", "Status only (no embed)", "mesie", ["GHOST"],
       ["mesie_status", "mesie_ok"]),
    _w("mw057_mesie_route", "Route a spectrum goal", "mesie", ["ARCHON"],
       ["universal_route", "mesie_ok", "universal_receipt"]),
    _w("mw058_mesie_with_forge", "Science under Forge", "mesie", ["FORGE", "GHOST"],
       ["mesie_ok", "forge_available", "universal_sdk"]),
    _w("mw059_mesie_with_pocket", "Science under POCKET", "mesie", ["ARCHON", "GHOST"],
       ["pocket_version", "mesie_ok", "universal_clouds"]),
    # --- billing (8) ---
    _w("mw060_billing_table", "Full plan table", "billing", ["SHIP"],
       ["billing_plans", "billing_schema", "billing_aliases"]),
    _w("mw061_billing_starter", "Starter path", "billing", ["SHIP"],
       ["billing_starter", "billing_lookup"]),
    _w("mw062_billing_pro", "Pro path (monthly_pro alias)", "billing", ["SHIP"],
       ["billing_pro", "billing_lookup"]),
    _w("mw063_billing_team", "Team path", "billing", ["SHIP"],
       ["billing_team", "billing_seats"]),
    _w("mw064_billing_refill", "POCK refill", "billing", ["SHIP"],
       ["billing_refill", "billing_usd"]),
    _w("mw065_billing_ents", "Entitlements matrix", "billing", ["SENTINEL"],
       ["billing_entitlements", "billing_grant"]),
    _w("mw066_billing_pocket", "POCKET economy + plans", "billing", ["SHIP"],
       ["pocket_economy", "universal_billing_plans"]),
    _w("mw067_billing_engine", "Engine grant path", "billing", ["SHIP"],
       ["engine_billing", "billing_grant"]),
    # --- nexus (6) ---
    _w("mw068_nexus_boot", "NEXUS online", "nexus", ["ARCHON"],
       ["nexus_ok", "nexus_online", "universal_nexus"]),
    _w("mw069_nexus_workers", "Nine workers", "nexus", ["ARCHON"],
       ["nexus_workers", "nexus_philosophy"]),
    _w("mw070_nexus_disk", "Cache + drafts", "nexus", ["FORGE"],
       ["nexus_cache", "nexus_drafts", "nexus_path"]),
    _w("mw071_nexus_ship", "Ship date + bridge", "nexus", ["SHIP"],
       ["nexus_ship", "nexus_bridge"]),
    _w("mw072_nexus_mcp", "MCP list hint", "nexus", ["ARCHON"],
       ["nexus_list_mcp", "universal_sdk"]),
    _w("mw073_nexus_with_pocket", "NEXUS as a cloud", "nexus", ["ARCHON"],
       ["universal_clouds", "nexus_ok"]),
    # --- phone / iot (6) ---
    _w("mw074_phone_urls", "Phone LAN + remote", "phone_iot", ["NAVIGATOR"],
       ["phone_lan", "phone_remote", "pocket_phone"]),
    _w("mw075_hz_home", "HZ mesh + docs", "phone_iot", ["NAVIGATOR"],
       ["hz_mesh", "hz_docs"]),
    _w("mw076_iot_grid", "GRID + HZ", "phone_iot", ["NAVIGATOR"],
       ["grid_probe", "hz_mesh", "mesh_ok"]),
    _w("mw077_pair_surface", "Phone pair surface", "phone_iot", ["NAVIGATOR"],
       ["pocket_phone", "pocket_desk", "tunnel_ok"]),
    _w("mw078_home_ok", "Home adjacency", "phone_iot", ["NAVIGATOR"],
       ["hz_mesh", "mesh_ok", "vdisk_ok"]),
    _w("mw079_phone_health", "Phone + host heart", "phone_iot", ["SENTINEL"],
       ["pocket_heart", "phone_lan", "universal_ports"]),
    # --- voice / studio (6) ---
    _w("mw080_voice_boot", "Voice URL + health", "voice_studio", ["AURO"],
       ["voice_url", "voice_health"]),
    _w("mw081_studio_boot", "Studio + pocket studio", "voice_studio", ["SHIP"],
       ["studio_ok", "pocket_studio"]),
    _w("mw082_auro_local", "Auro local model", "voice_studio", ["AURO"],
       ["auro_probe", "auro_root"]),
    _w("mw083_voice_fusion", "Voice + whoami", "voice_studio", ["AURO", "ARCHON"],
       ["voice_health", "universal_whoami"]),
    _w("mw084_studio_ship", "Studio surface for ship", "voice_studio", ["SHIP"],
       ["studio_ok", "pocket_download", "universal_receipt"]),
    _w("mw085_voice_ports", "Voice port in map", "voice_studio", ["SENTINEL"],
       ["universal_ports", "voice_url"]),
    # --- ship (6) ---
    _w("mw086_ship_card", "What we can ship today", "ship", ["SHIP"],
       ["pocket_version", "forge_github", "engine_github", "universal_version"]),
    _w("mw087_ship_tests", "Test artifacts present", "ship", ["SENTINEL"],
       ["engine_tests", "forge_available", "mesie_ok"]),
    _w("mw088_ship_android", "Android + docker", "ship", ["SHIP"],
       ["engine_android", "engine_docker"]),
    _w("mw089_ship_notes", "Write a ship note", "ship", ["SCRIBE"],
       ["universal_note", "universal_notes_list", "universal_receipt"]),
    _w("mw090_ship_flags", "Plan + goal flags", "ship", ["ARCHON"],
       ["universal_plan", "universal_goal", "universal_flag"]),
    _w("mw091_ship_readme", "Readmes exist", "ship", ["SCRIBE"],
       ["forge_readme", "engine_readme", "mesie_readme"]),
    # --- research (5) ---
    _w("mw092_research_map", "Lab map for a paper", "research", ["SCRUTATOR"],
       ["universal_stack_map", "repo_map", "universal_lab_roots"]),
    _w("mw093_research_mesie", "MESIE citations", "research", ["SCRUTATOR", "GHOST"],
       ["mesie_doi", "mesie_version", "mesie_bindings"]),
    _w("mw094_research_forge", "Forge papers list", "research", ["SCRUTATOR"],
       ["forge_papers", "charter_brief"]),
    _w("mw095_research_engine", "Engine whitepaper", "research", ["SCRUTATOR"],
       ["engine_whitepaper", "engine_onboarding"]),
    _w("mw096_research_hash", "Hash a claim", "research", ["GHOST"],
       ["universal_hash", "universal_uuid", "universal_receipt"]),
    # --- daily (4) ---
    _w("mw097_morning_seatbelt", "Morning seatbelt", "daily", ["ARCHON"],
       ["universal_time", "universal_health", "pocket_heart", "universal_calendar"]),
    _w("mw098_midday_route", "Midday goal route", "daily", ["ARCHON"],
       ["universal_goal", "universal_decide", "universal_clouds"]),
    _w("mw099_evening_receipt", "Evening receipt", "daily", ["SCRIBE"],
       ["universal_weekday", "universal_receipt", "universal_notes_list"]),
    _w("mw100_night_listen", "Night listen sweep", "daily", ["SENTINEL"],
       ["forge_listening", "engine_listening", "pocket_heart", "nexus_ok"]),
]

assert len(WORKFLOWS) == 100, len(WORKFLOWS)
assert len({w["id"] for w in WORKFLOWS}) == 100
assert all(w["step_count"] >= 2 for w in WORKFLOWS)


def catalog(*, family: str = "") -> Dict[str, Any]:
    fam = (family or "").strip().lower()
    items = [w for w in WORKFLOWS if not fam or w["family"] == fam]
    families: Dict[str, int] = {}
    for w in WORKFLOWS:
        families[w["family"]] = families.get(w["family"], 0) + 1
    return {
        "ok": True,
        "schema": SCHEMA,
        "count": len(items),
        "total": 100,
        "families": families,
        "workflows": [
            {
                "id": w["id"],
                "title": w["title"],
                "family": w["family"],
                "agents": w["agents"],
                "steps": w["step_count"],
                "desc": w["desc"],
            }
            for w in items
        ],
        "http": ["GET /v1/workflows/multi", "POST /v1/workflows/multi/run"],
    }


def families() -> Dict[str, Any]:
    c = catalog()
    return {"ok": True, "families": c["families"], "total": 100}


def get(wid: str) -> Dict[str, Any]:
    key = (wid or "").strip().lower()
    for w in WORKFLOWS:
        if w["id"] == key or w["id"].endswith("_" + key) or w["id"].split("_", 1)[0] == key:
            return {"ok": True, "workflow": w}
    return {"ok": False, "error": f"unknown workflow {wid}", "hint": "GET /v1/workflows/multi"}


def run(wid: str, *, dry: bool = False, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    found = get(wid)
    if not found.get("ok"):
        return found
    wf = found["workflow"]
    t0 = time.time()
    results: List[Dict[str, Any]] = []
    try:
        from pocket.go_plane import record_workflow

        record_workflow(wf["id"], status="running", title=wf["title"], family=wf["family"])
    except Exception:
        pass
    if not dry:
        from pocket.mcp_fifty import known, run as run_tool
        from pocket.mcp_bundle import invoke

        for step in wf["steps"]:
            tool = step["tool"]
            try:
                if known(tool):
                    out = run_tool(tool, params or {})
                else:
                    out = invoke("pocket", tool, **(params or {}))
            except Exception as e:
                out = {"ok": False, "error": str(e), "tool": tool}
            results.append(
                {
                    "id": step["id"],
                    "tool": tool,
                    "ok": bool(out.get("ok")) if isinstance(out, dict) else True,
                    "preview": str({k: out[k] for k in list(out)[:6]})[:240] if isinstance(out, dict) else str(out)[:240],
                }
            )
    else:
        results = [{"id": s["id"], "tool": s["tool"], "ok": True, "dry": True} for s in wf["steps"]]
    ok = all(s.get("ok") for s in results) if results else False
    payload = {
        "ok": ok,
        "schema": SCHEMA,
        "workflow_id": wf["id"],
        "title": wf["title"],
        "family": wf["family"],
        "agents": wf["agents"],
        "dry": dry,
        "passed": sum(1 for s in results if s.get("ok")),
        "total": len(results),
        "ms": int((time.time() - t0) * 1000),
        "steps": results,
    }
    path = OUT / f"{wf['id']}_{int(time.time())}.json"
    path.write_text(json.dumps(payload, indent=2, default=str)[:200000], encoding="utf-8")
    payload["log_path"] = str(path)
    try:
        from pocket.go_plane import record_workflow

        record_workflow(
            wf["id"],
            status="ok" if ok else "fail",
            ok=ok,
            ms=payload["ms"],
            error="" if ok else "step failed",
            title=wf["title"],
            family=wf["family"],
        )
    except Exception:
        pass
    return payload


def run_family(family: str, *, dry: bool = True) -> Dict[str, Any]:
    items = [w for w in WORKFLOWS if w["family"] == family]
    runs = [run(w["id"], dry=dry) for w in items]
    return {
        "ok": all(r.get("ok") for r in runs),
        "family": family,
        "count": len(runs),
        "passed": sum(1 for r in runs if r.get("ok")),
        "runs": runs,
    }
