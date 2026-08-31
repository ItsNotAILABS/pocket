"""POCKET 200-tool MCP pack — 60 universal + 140 ecosystem.

Universal tools are first-class MCP names (no pocket_ prefix required)
and work from any agent / desk / ecosystem.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

SCHEMA = "pocket.mcp_pack.v1"
RECEIPTS = Path.home() / ".pocket" / "receipts"
NOTES = Path.home() / ".pocket" / "notes"
FORGE_PORT = int(os.environ.get("SOVEREIGN_FORGE_PORT") or "8789")

# id, universal, desc
_SPEC: List[tuple] = [
    ("universal_ping", True, "Liveness probe for any agent"),
    ("universal_catalog", True, "List the 50-tool pack"),
    ("universal_health", True, "Health of POCKET + Forge + Engine + MESIE"),
    ("universal_clouds", True, "Sovereign computing clouds"),
    ("universal_ports", True, "Lab port map"),
    ("universal_time", True, "UTC + local timestamps"),
    ("universal_echo", True, "Echo payload (debug)"),
    ("universal_whoami", True, "Host / product / lab identity"),
    ("universal_doctrine", True, "Binding product doctrine"),
    ("universal_sdk", True, "Internal SDK catalog"),
    ("universal_route", True, "Route a goal to pocket|forge|engine|mesie"),
    ("universal_receipt", True, "Write a signed-style local receipt"),
    ("universal_search_tools", True, "Search MCP tools by keyword"),
    ("universal_billing_plans", True, "Shared RevenueCat / POCK plans"),
    ("universal_mesie", True, "MESIE SDK status"),
    ("universal_forge", True, "SovereignForge status"),
    ("universal_engine", True, "Sovereign Engine cores status"),
    ("universal_nexus", True, "NEXUS MERIDIAN status"),
    ("universal_invoke", True, "Invoke any pocket tool by name"),
    ("universal_version", True, "Versions of every stack"),
    ("pocket_version", False, "POCKET version + tagline"),
    ("pocket_identity", False, "POCKET identity brief"),
    ("pocket_edition", False, "Edition / org / lab"),
    ("pocket_public_url", False, "Public tunnel URL"),
    ("pocket_habitat", False, "Habitat residents"),
    ("pocket_agents", False, "Agent roster count"),
    ("pocket_skills", False, "Skill suite count"),
    ("pocket_desk", False, "Desk URL"),
    ("pocket_phone", False, "Phone URLs + pair"),
    ("pocket_economy", False, "Economy map if present"),
    ("forge_strategies", False, "Forge strategy catalog"),
    ("forge_products", False, "Forge shipped products"),
    ("forge_ledger", False, "Forge ledger stats"),
    ("engine_cores", False, "Engine nextgen core names"),
    ("engine_xfin", False, "XFIN treasury probe"),
    ("engine_pulse", False, "PULSE churn probe"),
    ("mesie_embed", False, "Embed a numeric series via MESIE"),
    ("mesie_engines", False, "MESIE engine list"),
    ("mesie_fingerprint", False, "Fingerprint a series"),
    ("billing_lookup", False, "Resolve plan id (aliases ok)"),
    ("billing_grant", False, "Grant entitlements for an event"),
    ("parallax_status", False, "PARALLAX adapter via Forge"),
    ("grid_probe", False, "GRID Wear OS probe"),
    ("hz_mesh", False, "HZ offline mesh path"),
    ("auro_probe", False, "Auro14B local model"),
    ("voice_health", False, "Pocket Voice :8790"),
    ("which_pocket", False, "Which POCKET tree is live"),
    ("mesh_paths", False, "Mesh + vdisk paths"),
    ("repo_map", False, "POCKET repo map"),
    ("charter_brief", False, "Charter one-pager"),
]

_EXTRA: List[tuple] = [
    # +40 universal → 60
    ("universal_ok", True, "Always-ok probe"),
    ("universal_host", True, "Hostname"),
    ("universal_cwd", True, "Process cwd"),
    ("universal_python", True, "Python executable"),
    ("universal_home", True, "User home"),
    ("universal_onedrive", True, "OneDrive root"),
    ("universal_workspace", True, "POCKET workspace"),
    ("universal_json", True, "Parse text as JSON"),
    ("universal_hash", True, "SHA256 of text"),
    ("universal_uuid", True, "New UUID4"),
    ("universal_note", True, "Write a lab note"),
    ("universal_notes_list", True, "List lab notes"),
    ("universal_flag", True, "Set/get a named flag"),
    ("universal_plan", True, "Store a one-line plan"),
    ("universal_goal", True, "Store a goal"),
    ("universal_stack_map", True, "Three-desk stack map"),
    ("universal_lab_roots", True, "Lab root paths"),
    ("universal_git_hint", True, "git status hint for a root"),
    ("universal_weekday", True, "UTC weekday"),
    ("universal_calendar", True, "UTC calendar date"),
    ("universal_lower", True, "Lowercase text"),
    ("universal_upper", True, "Uppercase text"),
    ("universal_count", True, "Count words/chars"),
    ("universal_keys", True, "List payload keys"),
    ("universal_pick", True, "Pick a param by name"),
    ("universal_bool", True, "Coerce to bool"),
    ("universal_int", True, "Coerce to int"),
    ("universal_bytes", True, "UTF-8 byte length"),
    ("universal_env_safe", True, "Safe env var names only"),
    ("universal_path_exists", True, "Path exists under home"),
    ("universal_dir_list", True, "List a home-relative dir"),
    ("universal_write_note", True, "Alias of universal_note"),
    ("universal_read_note", True, "Read a lab note"),
    ("universal_coerce", True, "Best-effort JSON/text"),
    ("universal_join", True, "Join args with space"),
    ("universal_split", True, "Split text"),
    ("universal_ok_or", True, "ok if text non-empty"),
    ("universal_error", True, "Return a structured error"),
    ("universal_decide", True, "Pick pocket|forge|engine|mesie"),
    ("universal_http_local", True, "GET a 127.0.0.1 URL"),
    # +25 pocket
    ("pocket_heart", False, "Host /health heart"),
    ("pocket_health_http", False, "Raw /health"),
    ("pocket_surfaces", False, "Product surfaces"),
    ("pocket_fish", False, "FISH class"),
    ("pocket_class", False, "Product class"),
    ("pocket_uses", False, "Product uses"),
    ("pocket_company", False, "Company name"),
    ("pocket_org", False, "GitHub org"),
    ("pocket_github", False, "Public GitHub URL"),
    ("pocket_protocols", False, "Protocol list hint"),
    ("pocket_docs", False, "Docs hub URL"),
    ("pocket_install", False, "Install hub URL"),
    ("pocket_studio", False, "Studio URL"),
    ("pocket_wiki", False, "Wiki URL"),
    ("pocket_swarm", False, "Swarm URL"),
    ("pocket_landing", False, "Landing URL"),
    ("pocket_api", False, "API root"),
    ("pocket_work", False, "Work URL"),
    ("pocket_working", False, "Working URL"),
    ("pocket_download", False, "Download URL"),
    ("pocket_auth_hint", False, "Auth is seat token"),
    ("pocket_highlights", False, "Health highlights"),
    ("pocket_heartbeat", False, "Heartbeat interval"),
    ("pocket_brain", False, "Brain online flag"),
    ("pocket_upgrade", False, "Upgrade tag from /health"),
    # +20 forge
    ("forge_status", False, "Forge HTTP or import"),
    ("forge_port", False, "Forge port"),
    ("forge_root", False, "Forge tree"),
    ("forge_available", False, "Forge on disk"),
    ("forge_url", False, "Forge dashboard URL"),
    ("forge_github", False, "Forge GitHub"),
    ("forge_workflows", False, "Named workflows"),
    ("forge_agents", False, "High-level agent names"),
    ("forge_serve_cmd", False, "How to start --serve"),
    ("forge_health", False, "Forge /api/status ok"),
    ("forge_pairs", False, "PARALLAX pairs if listening"),
    ("forge_market", False, "BTC ticker if listening"),
    ("forge_budget", False, "Budget hint"),
    ("forge_readme", False, "README head"),
    ("forge_adapters", False, "Adapter files"),
    ("forge_papers", False, "Paper titles"),
    ("forge_electron", False, "Electron shell present"),
    ("forge_dist", False, "dist/products list"),
    ("forge_cli_hint", False, "CLI commands"),
    ("forge_listening", False, "Is :8789 up"),
    # +20 engine
    ("engine_available", False, "Engine tree present"),
    ("engine_root", False, "Engine path"),
    ("engine_github", False, "Engine GitHub"),
    ("engine_dash", False, "Dashboard URL"),
    ("engine_api", False, "API URL"),
    ("engine_aura", False, "AURA init probe"),
    ("engine_mint", False, "MINT tokenomics probe"),
    ("engine_nexs", False, "NEXS init probe"),
    ("engine_grid", False, "GRID init probe"),
    ("engine_billing", False, "Billing core shared catalog"),
    ("engine_tests", False, "Test file present"),
    ("engine_android", False, "android-app present"),
    ("engine_docker", False, "Dockerfile present"),
    ("engine_readme", False, "README head"),
    ("engine_whitepaper", False, "Whitepaper present"),
    ("engine_onboarding", False, "Onboarding present"),
    ("engine_bus", False, "substrate_bus present"),
    ("engine_ppp", False, "PPP sample price"),
    ("engine_lifecycle", False, "Master orchestrator present"),
    ("engine_listening", False, "Dash or API up"),
    # +15 mesie
    ("mesie_status", False, "MESIE importable"),
    ("mesie_version", False, "Runtime version"),
    ("mesie_path", False, "Package file"),
    ("mesie_pip", False, "pip metadata version"),
    ("mesie_editable", False, "Editable checkout"),
    ("mesie_doi", False, "Zenodo DOI"),
    ("mesie_readme", False, "README exists"),
    ("mesie_bindings", False, "Binding folders"),
    ("mesie_hub", False, "mesie-hub skill hint"),
    ("mesie_ok", False, "find_spec mesie"),
    ("mesie_importable", False, "Can import mesie"),
    ("mesie_sdk_class", False, "SDK class name"),
    ("mesie_n_bands", False, "Default n_bands=8"),
    ("mesie_phase", False, "Phase-aware default"),
    ("mesie_root_exists", False, "MESIE repo on disk"),
    # +10 billing
    ("billing_plans", False, "Full plan table"),
    ("billing_starter", False, "Starter plan"),
    ("billing_pro", False, "Pro plan"),
    ("billing_team", False, "Team plan"),
    ("billing_refill", False, "Refill plan"),
    ("billing_aliases", False, "Plan aliases"),
    ("billing_schema", False, "Billing schema id"),
    ("billing_seats", False, "Seats by plan"),
    ("billing_usd", False, "USD by plan"),
    ("billing_entitlements", False, "Entitlements by plan"),
    # +10 nexus
    ("nexus_ok", False, "NEXUS reachable"),
    ("nexus_workers", False, "Worker names if known"),
    ("nexus_cache", False, "Cache dir"),
    ("nexus_drafts", False, "Drafts dir"),
    ("nexus_path", False, "NEXUS tree"),
    ("nexus_ship", False, "Ship date hint"),
    ("nexus_philosophy", False, "Protocols are the intelligence"),
    ("nexus_bridge", False, "pocket.nexus_bridge"),
    ("nexus_list_mcp", False, "Bridge MCP list hint"),
    ("nexus_online", False, "Status ok flag"),
    # +10 surfaces
    ("voice_url", False, "Voice :8790"),
    ("phone_lan", False, "Phone LAN URL"),
    ("phone_remote", False, "Phone public URL"),
    ("hz_docs", False, "HZ PHONE_MCP.md"),
    ("auro_root", False, "Auro14B root"),
    ("mesh_ok", False, "Mesh path exists"),
    ("vdisk_ok", False, "Vdisk exists"),
    ("tunnel_ok", False, "Public URL set"),
    ("studio_ok", False, "Studio URL"),
    ("mail_ok", False, "Agent mail status"),
]

_SPEC = _SPEC + _EXTRA
assert len(_SPEC) == 200, len(_SPEC)
assert len({i for i, _, _ in _SPEC}) == 200, "duplicate tool ids"


def _tool_meta() -> List[Dict[str, Any]]:
    return [
        {"id": i, "universal": u, "desc": d, "mcp": i if u else f"pocket_{i}"}
        for i, u, d in _SPEC
    ]


def ids() -> List[str]:
    return [i for i, _, _ in _SPEC]


def universal_ids() -> List[str]:
    return [i for i, u, _ in _SPEC if u]


def catalog() -> Dict[str, Any]:
    tools = _tool_meta()
    return {
        "ok": True,
        "schema": SCHEMA,
        "count": len(tools),
        "universal": sum(1 for t in tools if t["universal"]),
        "ecosystem": sum(1 for t in tools if not t["universal"]),
        "tools": tools,
        "http": ["GET /v1/mcp/fifty", "POST /v1/mcp/invoke {server:universal,tool}"],
    }


def _http(url: str, timeout: float = 0.6) -> Dict[str, Any]:
    import urllib.request

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"text": raw[:400]}
            return {"ok": True, "status": resp.status, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e), "url": url}


def _t_ping(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "pong": True, "ts": time.time(), "echo": p.get("text") or p.get("prompt") or ""}


def _t_catalog(p: Dict[str, Any]) -> Dict[str, Any]:
    return catalog()


def _t_health(p: Dict[str, Any]) -> Dict[str, Any]:
    surfaces = {
        "pocket": _http("http://127.0.0.1:8787/health"),
        "forge": _http(f"http://127.0.0.1:{FORGE_PORT}/api/status"),
        "engine": _http("http://127.0.0.1:8090/api/v1/overview"),
    }
    mesie_ok = False
    try:
        import importlib.util

        mesie_ok = importlib.util.find_spec("mesie") is not None
    except Exception:
        pass
    surfaces["mesie"] = {"ok": mesie_ok}
    healthy = sum(1 for v in surfaces.values() if isinstance(v, dict) and v.get("ok"))
    return {"ok": True, "healthy": healthy, "surfaces": {k: bool(v.get("ok")) for k, v in surfaces.items()}}


def _t_clouds(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.sovereign_stack import computing_clouds

    return computing_clouds()


def _t_ports(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "ports": {
            "pocket": 8787,
            "forge": FORGE_PORT,
            "voice": 8790,
            "phone_agent": 8795,
            "engine_dash": 8090,
            "engine_api": 8089,
        },
    }


def _t_time(p: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {"ok": True, "utc": now.isoformat(), "unix": time.time()}


def _t_echo(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "echo": p}


def _t_whoami(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket import COMPANY, EDITION, LAB, PRODUCT, TAGLINE, __version__

    return {
        "ok": True,
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "company": COMPANY,
        "edition": EDITION,
        "tagline": TAGLINE,
        "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "",
    }


def _t_doctrine(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.sovereign_stack import doctrine

    return doctrine()


def _t_sdk(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal import catalog as sdk_catalog

        return sdk_catalog()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_route(p: Dict[str, Any]) -> Dict[str, Any]:
    goal = (p.get("goal") or p.get("text") or p.get("prompt") or "").lower()
    target = "pocket"
    if any(k in goal for k in ("trade", "binance", "parallax", "ledger", "strategy")):
        target = "forge"
    elif any(k in goal for k in ("paywall", "revenuecat", "ltv", "churn", "shipaton")):
        target = "engine"
    elif any(k in goal for k in ("spectrum", "embed", "mesie", "fingerprint", "psd")):
        target = "mesie"
    return {"ok": True, "target": target, "goal": goal[:240], "hint": f"use universal_{target} or server={target}"}


def _t_receipt(p: Dict[str, Any]) -> Dict[str, Any]:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    rec = {
        "schema": "pocket.receipt.v1",
        "ts": time.time(),
        "utc": datetime.now(timezone.utc).isoformat(),
        "title": p.get("title") or p.get("name") or "mcp-fifty",
        "text": p.get("text") or p.get("prompt") or p.get("content") or "",
        "tool": p.get("tool") or "universal_receipt",
    }
    path = RECEIPTS / f"r_{int(time.time())}.json"
    path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return {"ok": True, "path": str(path), "receipt": rec}


def _t_search_tools(p: Dict[str, Any]) -> Dict[str, Any]:
    q = (p.get("text") or p.get("prompt") or p.get("q") or "").lower()
    hits = [t for t in _tool_meta() if not q or q in t["id"] or q in t["desc"].lower()]
    return {"ok": True, "q": q, "count": len(hits), "tools": hits[:40]}


def _t_billing_plans(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.billing_sdk import BillingSDK

    return BillingSDK().plans()


def _t_mesie(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.mesie_sdk import MesieSDK

        return MesieSDK().status()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_forge(p: Dict[str, Any]) -> Dict[str, Any]:
    live = _http(f"http://127.0.0.1:{FORGE_PORT}/api/status")
    if live.get("ok"):
        return {"ok": True, "listening": True, "status": live.get("data")}
    try:
        from itsnotai_internal.forge_sdk import ForgeSDK

        return {"ok": True, "listening": False, "available": ForgeSDK().available()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_engine(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.engine_sdk import EngineSDK

        e = EngineSDK()
        return {"ok": True, "available": e.available(), "path": str(e.root)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_nexus(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.nexus_bridge import nexus_available

        return dict(nexus_available())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_invoke(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.mcp_bundle import invoke

    inner = p.get("tool") or p.get("name") or "platform_health"
    if inner in ids():
        return run(inner, {k: v for k, v in p.items() if k not in ("tool", "name")})
    return invoke("pocket", inner, **{k: v for k, v in p.items() if k not in ("tool", "name")})


def _t_version(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket import __version__ as pv

    out: Dict[str, Any] = {"ok": True, "pocket": pv}
    try:
        from mesie.version_info import __version__ as mv

        out["mesie"] = mv
    except Exception:
        out["mesie"] = None
    try:
        from itsnotai_internal import __version__ as iv

        out["internal_sdks"] = iv
    except Exception:
        out["internal_sdks"] = None
    return out


def _t_pocket_version(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket import PRODUCT, TAGLINE, __version__

    return {"ok": True, "product": PRODUCT, "version": __version__, "tagline": TAGLINE}


def _t_identity(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.pocket_identity import identity_brief

        return {"ok": True, "brief": identity_brief()}
    except Exception as e:
        return _t_whoami(p) | {"note": str(e)}


def _t_edition(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket import COMPANY, EDITION, LAB, ORG

    return {"ok": True, "edition": EDITION, "lab": LAB, "company": COMPANY, "org": ORG}


def _t_public_url(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.sovereign_stack import computing_clouds

    c = computing_clouds()
    return {"ok": True, "public_url": c.get("public_url"), "local": "http://127.0.0.1:8787"}


def _t_habitat(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.agent_habitat import status as hstat

        return hstat()
    except Exception:
        from pocket.platform_coherence import run_platform_skill

        return run_platform_skill("habitat_status", prompt="", params=p)


def _t_agents(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.first_class_agents import summary

        return summary()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_skills(p: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.skills_registry import SKILLS

    return {"ok": True, "count": len(SKILLS)}


def _t_desk(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "desk": "http://127.0.0.1:8787/desk", "phone": "http://127.0.0.1:8787/phone"}


def _t_phone(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.iot_home import phone_bridge

        return phone_bridge()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_economy(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.economy import snapshot

        return snapshot()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_forge_strategies(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.forge_sdk import ForgeSDK

        return {"ok": True, "strategies": ForgeSDK().strategies()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_forge_products(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.forge_sdk import ForgeSDK

        return {"ok": True, "manifest": ForgeSDK().products()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_forge_ledger(p: Dict[str, Any]) -> Dict[str, Any]:
    live = _http(f"http://127.0.0.1:{FORGE_PORT}/api/ledger")
    if live.get("ok"):
        return {"ok": True, "ledger": live.get("data")}
    return {"ok": False, "error": "forge not listening", "url": f"http://127.0.0.1:{FORGE_PORT}/api/ledger"}


def _t_engine_cores(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.engine_sdk import EngineSDK

        cores = EngineSDK().cores()
        names = [k for k in cores.keys() if k != "ok"]
        return {"ok": True, "cores": names}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_xfin(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.engine_sdk import EngineSDK, _ensure

        if not EngineSDK().available():
            return {"ok": False, "error": "engine missing"}
        _ensure()
        from xfin_engine import XFINEngine

        x = XFINEngine(100000.0)
        bal = x.get_treasury_balance() if hasattr(x, "get_treasury_balance") else None
        return {"ok": True, "treasury": bal}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_pulse(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.engine_sdk import EngineSDK, _ensure

        if not EngineSDK().available():
            return {"ok": False, "error": "engine missing"}
        _ensure()
        from pulse_engine import PULSEEngine

        pu = PULSEEngine()
        score = pu.evaluate_churn_risk("mcp_fifty", 0.7, 1, 90)
        return {"ok": True, "churn": score}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _series(p: Dict[str, Any]) -> List[float]:
    raw = p.get("values") or p.get("series") or p.get("args")
    if isinstance(raw, list) and raw:
        return [float(x) for x in raw[:256]]
    text = p.get("text") or p.get("prompt") or ""
    if text:
        try:
            return [float(x) for x in text.replace(",", " ").split() if x][:256]
        except Exception:
            pass
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2] * 8


def _t_mesie_embed(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.mesie_sdk import MesieSDK

        vec = MesieSDK().embed_series(_series(p))
        return {"ok": True, "shape": getattr(vec, "shape", None), "preview": str(vec)[:240]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_mesie_engines(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.mesie_sdk import MesieSDK

        return {"ok": True, "engines": MesieSDK().engines()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_mesie_fp(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.mesie_sdk import MesieSDK

        fp = MesieSDK().fingerprint_series(_series(p))
        return {"ok": True, "fingerprint": str(fp)[:400]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_billing_lookup(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.billing_sdk import BillingSDK

    return BillingSDK().lookup(p.get("name") or p.get("plan") or p.get("text") or "monthly_pro")


def _t_billing_grant(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.billing_sdk import BillingSDK

    return BillingSDK().grant(
        p.get("name") or p.get("plan") or "pocket_pro",
        p.get("action") or p.get("event") or "INITIAL_PURCHASE",
        float(p["usd"]) if p.get("usd") is not None else None,
    )


def _t_parallax(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.parallax_sdk import ParallaxSDK

        return ParallaxSDK().status()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_grid(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from itsnotai_internal.grid_sdk import GridSDK

        return GridSDK().register_probe(p.get("name") or "mcp_fifty_watch")
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_hz(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.hz_sdk import HzSDK

    return HzSDK().status()


def _t_auro(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.auro_sdk import AuroSDK

    return AuroSDK().status()


def _t_voice(p: Dict[str, Any]) -> Dict[str, Any]:
    from itsnotai_internal.voice_sdk import VoiceSDK

    return VoiceSDK().health()


def _t_which(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.which_pocket import summary

        return summary()
    except Exception:
        root = Path(__file__).resolve().parents[2]
        return {"ok": True, "root": str(root), "file": str(Path(__file__))}


def _t_mesh(p: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.mesh_disk import MESH, VDISK

        return {"ok": True, "mesh": str(MESH), "vdisk": str(VDISK)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _t_repos(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "repos": {
            "pocket_os": str(Path.home() / "OneDrive" / "pocket-os"),
            "forge": str(Path.home() / "OneDrive" / "sovereign_forge_os"),
            "engine": str(Path.home() / "OneDrive" / "Documents" / "sovereign-engine"),
            "mesie": r"C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-",
            "internal_sdks": str(Path.home() / "OneDrive" / "internal-sdks"),
            "forge_github": "https://github.com/ItsNotAILABS/sovereign-forge-os",
            "engine_github": "https://github.com/FreddyCreates/sovereign-engine",
        },
    }


def _t_charter(p: Dict[str, Any]) -> Dict[str, Any]:
    path = Path.home() / "OneDrive" / "pocket-os" / "CHARTER.md"
    text = ""
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")[:1800]
    return {"ok": True, "path": str(path) if path.is_file() else None, "text": text}


HANDLERS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    "universal_ping": _t_ping,
    "universal_catalog": _t_catalog,
    "universal_health": _t_health,
    "universal_clouds": _t_clouds,
    "universal_ports": _t_ports,
    "universal_time": _t_time,
    "universal_echo": _t_echo,
    "universal_whoami": _t_whoami,
    "universal_doctrine": _t_doctrine,
    "universal_sdk": _t_sdk,
    "universal_route": _t_route,
    "universal_receipt": _t_receipt,
    "universal_search_tools": _t_search_tools,
    "universal_billing_plans": _t_billing_plans,
    "universal_mesie": _t_mesie,
    "universal_forge": _t_forge,
    "universal_engine": _t_engine,
    "universal_nexus": _t_nexus,
    "universal_invoke": _t_invoke,
    "universal_version": _t_version,
    "pocket_version": _t_pocket_version,
    "pocket_identity": _t_identity,
    "pocket_edition": _t_edition,
    "pocket_public_url": _t_public_url,
    "pocket_habitat": _t_habitat,
    "pocket_agents": _t_agents,
    "pocket_skills": _t_skills,
    "pocket_desk": _t_desk,
    "pocket_phone": _t_phone,
    "pocket_economy": _t_economy,
    "forge_strategies": _t_forge_strategies,
    "forge_products": _t_forge_products,
    "forge_ledger": _t_forge_ledger,
    "engine_cores": _t_engine_cores,
    "engine_xfin": _t_xfin,
    "engine_pulse": _t_pulse,
    "mesie_embed": _t_mesie_embed,
    "mesie_engines": _t_mesie_engines,
    "mesie_fingerprint": _t_mesie_fp,
    "billing_lookup": _t_billing_lookup,
    "billing_grant": _t_billing_grant,
    "parallax_status": _t_parallax,
    "grid_probe": _t_grid,
    "hz_mesh": _t_hz,
    "auro_probe": _t_auro,
    "voice_health": _t_voice,
    "which_pocket": _t_which,
    "mesh_paths": _t_mesh,
    "repo_map": _t_repos,
    "charter_brief": _t_charter,
}

assert set(HANDLERS).issubset(set(ids()))
_CORE_IDS = set(HANDLERS)
_PACK_IDS = {i for i, _, _ in _SPEC}


def _normalize(name: str) -> str:
    t = (name or "").lower().strip()
    if t.startswith("pocket_"):
        inner = t[len("pocket_") :]
        if inner in _PACK_IDS:
            return inner
    return t


def known(name: str) -> bool:
    return _normalize(name) in _PACK_IDS


def run(name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    t = _normalize(name)
    fn = HANDLERS.get(t)
    try:
        if fn:
            out = fn(params or {})
        elif t in _PACK_IDS:
            out = _extra(t, params or {})
        else:
            return {"ok": False, "error": f"unknown pack tool {name}", "catalog": catalog()}
        if isinstance(out, dict):
            out.setdefault("tool", t)
            out.setdefault("universal", t in set(universal_ids()))
        return out
    except Exception as e:
        return {"ok": False, "tool": t, "error": str(e)}


def _home_path(raw: str) -> Optional[Path]:
    p = Path(raw or "").expanduser()
    try:
        p.resolve().relative_to(Path.home().resolve())
        return p
    except Exception:
        return None


def _text(p: Dict[str, Any]) -> str:
    return str(p.get("text") or p.get("prompt") or p.get("content") or p.get("goal") or "")


def _extra(t: str, p: Dict[str, Any]) -> Dict[str, Any]:
    import hashlib
    import uuid

    txt = _text(p)
    home = Path.home()
    od = home / "OneDrive"
    forge = od / "sovereign_forge_os"
    engine = od / "Documents" / "sovereign-engine"
    mesie = Path(r"C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-")
    pocket = od / "pocket-os"

    if t == "universal_ok":
        return {"ok": True}
    if t == "universal_host":
        return {"ok": True, "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or ""}
    if t == "universal_cwd":
        return {"ok": True, "cwd": os.getcwd()}
    if t == "universal_python":
        import sys

        return {"ok": True, "python": sys.executable, "version": sys.version.split()[0]}
    if t == "universal_home":
        return {"ok": True, "home": str(home)}
    if t == "universal_onedrive":
        return {"ok": True, "onedrive": str(od), "exists": od.is_dir()}
    if t == "universal_workspace":
        ws = home / ".pocket" / "workspace"
        ws.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "workspace": str(ws)}
    if t == "universal_json":
        raw = txt or "{}"
        try:
            return {"ok": True, "data": json.loads(raw)}
        except Exception:
            return {"ok": True, "data": {"text": raw}, "parsed": False}
    if t == "universal_hash":
        return {"ok": True, "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest()}
    if t == "universal_uuid":
        return {"ok": True, "uuid": str(uuid.uuid4())}
    if t in ("universal_note", "universal_write_note"):
        NOTES.mkdir(parents=True, exist_ok=True)
        name = p.get("name") or f"note_{int(time.time())}.md"
        path = NOTES / Path(name).name
        path.write_text(txt or "(empty)", encoding="utf-8")
        return {"ok": True, "path": str(path)}
    if t == "universal_notes_list":
        NOTES.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "notes": [x.name for x in NOTES.iterdir()][:40]}
    if t == "universal_read_note":
        path = NOTES / Path(p.get("name") or txt or "").name
        if not path.is_file():
            return {"ok": False, "error": "missing note"}
        return {"ok": True, "text": path.read_text(encoding="utf-8", errors="replace")[:8000]}
    if t == "universal_flag":
        FLAGS = home / ".pocket" / "flags.json"
        data = {}
        if FLAGS.is_file():
            try:
                data = json.loads(FLAGS.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        key = p.get("name") or "flag"
        if txt:
            data[key] = txt
            FLAGS.parent.mkdir(parents=True, exist_ok=True)
            FLAGS.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"ok": True, "key": key, "value": data.get(key), "all": data}
    if t == "universal_plan":
        return _extra("universal_flag", {**p, "name": "plan", "text": txt or p.get("title") or ""})
    if t == "universal_goal":
        return _extra("universal_flag", {**p, "name": "goal", "text": txt})
    if t == "universal_stack_map":
        return {
            "ok": True,
            "stack": {
                "pocket": "http://127.0.0.1:8787",
                "forge": f"http://127.0.0.1:{FORGE_PORT}",
                "engine": "http://127.0.0.1:8090",
                "mesie": str(mesie),
            },
        }
    if t == "universal_lab_roots":
        return _t_repos(p)
    if t == "universal_git_hint":
        root = Path(p.get("path") or txt or pocket)
        git = root / ".git"
        return {"ok": True, "root": str(root), "git": git.is_dir()}
    if t == "universal_weekday":
        return {"ok": True, "weekday": datetime.now(timezone.utc).strftime("%A")}
    if t == "universal_calendar":
        return {"ok": True, "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    if t == "universal_lower":
        return {"ok": True, "text": txt.lower()}
    if t == "universal_upper":
        return {"ok": True, "text": txt.upper()}
    if t == "universal_count":
        return {"ok": True, "chars": len(txt), "words": len(txt.split())}
    if t == "universal_keys":
        return {"ok": True, "keys": list(p.keys())}
    if t == "universal_pick":
        key = p.get("name") or "text"
        return {"ok": True, "key": key, "value": p.get(key)}
    if t == "universal_bool":
        v = txt.lower() in ("1", "true", "yes", "ok", "on")
        return {"ok": True, "value": v}
    if t == "universal_int":
        try:
            return {"ok": True, "value": int(float(txt or p.get("usd") or 0))}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    if t == "universal_bytes":
        return {"ok": True, "bytes": len(txt.encode("utf-8"))}
    if t == "universal_env_safe":
        keys = [k for k in os.environ if k.startswith(("POCKET_", "SOVEREIGN_", "MESIE_", "PYTHON"))]
        return {"ok": True, "keys": sorted(keys)[:40]}
    if t == "universal_path_exists":
        hp = _home_path(txt or p.get("path") or "")
        if not hp:
            return {"ok": False, "error": "path must be under home"}
        return {"ok": True, "path": str(hp), "exists": hp.exists()}
    if t == "universal_dir_list":
        hp = _home_path(txt or p.get("path") or str(home / ".pocket"))
        if not hp or not hp.is_dir():
            return {"ok": False, "error": "not a home dir"}
        return {"ok": True, "items": [x.name for x in list(hp.iterdir())[:40]]}
    if t == "universal_coerce":
        try:
            return {"ok": True, "data": json.loads(txt)}
        except Exception:
            return {"ok": True, "text": txt}
    if t == "universal_join":
        args = p.get("args") or txt.split()
        return {"ok": True, "text": " ".join(str(a) for a in args)}
    if t == "universal_split":
        return {"ok": True, "parts": txt.split()}
    if t == "universal_ok_or":
        return {"ok": bool(txt.strip())}
    if t == "universal_error":
        return {"ok": False, "error": txt or "universal_error"}
    if t == "universal_decide":
        return _t_route(p)
    if t == "universal_http_local":
        url = txt or p.get("url") or "http://127.0.0.1:8787/health"
        if not url.startswith("http://127.0.0.1") and not url.startswith("http://localhost"):
            return {"ok": False, "error": "only 127.0.0.1 / localhost"}
        return _http(url)

    if t.startswith("pocket_"):
        from pocket import COMPANY, EDITION, FISH, LAB, ORG, PRODUCT, TAGLINE, USES, __version__

        health = _http("http://127.0.0.1:8787/health")
        hdata = health.get("data") if isinstance(health.get("data"), dict) else {}
        table = {
            "pocket_heart": {"ok": True, "heart": (hdata or {}).get("heart") or health.get("ok")},
            "pocket_health_http": health,
            "pocket_surfaces": {"ok": True, "surfaces": (hdata or {}).get("surfaces") or ["/desk", "/phone"]},
            "pocket_fish": {"ok": True, "fish": FISH},
            "pocket_class": {"ok": True, "class": getattr(__import__("pocket", fromlist=["CLASS"]), "CLASS", "first-class")},
            "pocket_uses": {"ok": True, "uses": list(USES)[:12]},
            "pocket_company": {"ok": True, "company": COMPANY},
            "pocket_org": {"ok": True, "org": ORG},
            "pocket_github": {"ok": True, "github": getattr(__import__("pocket", fromlist=["GITHUB"]), "GITHUB", "")},
            "pocket_protocols": {"ok": True, "url": "http://127.0.0.1:8787/v1/protocols"},
            "pocket_docs": {"ok": True, "url": "http://127.0.0.1:8787/docs"},
            "pocket_install": {"ok": True, "url": "http://127.0.0.1:8787/install"},
            "pocket_studio": {"ok": True, "url": "http://127.0.0.1:8787/studio"},
            "pocket_wiki": {"ok": True, "url": "http://127.0.0.1:8787/wiki"},
            "pocket_swarm": {"ok": True, "url": "http://127.0.0.1:8787/swarm"},
            "pocket_landing": {"ok": True, "url": "http://127.0.0.1:8787/"},
            "pocket_api": {"ok": True, "url": "http://127.0.0.1:8787/v1"},
            "pocket_work": {"ok": True, "url": "http://127.0.0.1:8787/work"},
            "pocket_working": {"ok": True, "url": "http://127.0.0.1:8787/working"},
            "pocket_download": {"ok": True, "url": "http://127.0.0.1:8787/download"},
            "pocket_auth_hint": {"ok": True, "auth": "seat token / ACCESS.txt"},
            "pocket_highlights": {"ok": True, "highlights": (hdata or {}).get("highlights")},
            "pocket_heartbeat": {"ok": True, "heartbeat": (hdata or {}).get("heartbeat")},
            "pocket_brain": {"ok": True, "brain": (hdata or {}).get("brain")},
            "pocket_upgrade": {"ok": True, "upgrade": (hdata or {}).get("upgrade"), "version": __version__, "edition": EDITION, "lab": LAB, "tagline": TAGLINE, "product": PRODUCT},
        }
        return table.get(t) or {"ok": False, "error": t}

    if t.startswith("forge_"):
        listening = _http(f"http://127.0.0.1:{FORGE_PORT}/api/status")
        table = {
            "forge_status": {"ok": True, "listening": listening.get("ok"), "data": listening.get("data") if listening.get("ok") else None, "path": str(forge)},
            "forge_port": {"ok": True, "port": FORGE_PORT},
            "forge_root": {"ok": True, "path": str(forge), "exists": forge.is_dir()},
            "forge_available": {"ok": True, "available": (forge / "engine" / "orchestrator.py").is_file()},
            "forge_url": {"ok": True, "url": f"http://127.0.0.1:{FORGE_PORT}"},
            "forge_github": {"ok": True, "url": "https://github.com/ItsNotAILABS/sovereign-forge-os"},
            "forge_workflows": {"ok": True, "workflows": ["sovereign_trading_automation", "research_to_execution", "self_configure_and_heal", "finance_monthly_sovereign", "high_level_mission"]},
            "forge_agents": {"ok": True, "agents": ["sovereign-trader", "research-mission", "ecosystem-governor", "self-configurator", "finance-autopilot"]},
            "forge_serve_cmd": {"ok": True, "cmd": "python main.py --serve", "cwd": str(forge)},
            "forge_health": {"ok": bool(listening.get("ok")), "http": listening},
            "forge_pairs": _http(f"http://127.0.0.1:{FORGE_PORT}/api/parallax/pairs") if listening.get("ok") else {"ok": False, "error": "not listening"},
            "forge_market": _http(f"http://127.0.0.1:{FORGE_PORT}/api/market?symbol=BTCUSDT") if listening.get("ok") else {"ok": False, "error": "not listening"},
            "forge_budget": {"ok": True, "hint": "MESIE payments human gate — no auto-spend"},
            "forge_readme": {"ok": True, "exists": (forge / "README.md").is_file()},
            "forge_adapters": {"ok": True, "adapters": [x.name for x in (forge / "adapters").glob("*.py")] if (forge / "adapters").is_dir() else []},
            "forge_papers": {"ok": True, "papers": [x.name for x in (forge / "sovereign_papers").glob("*.md")] if (forge / "sovereign_papers").is_dir() else []},
            "forge_electron": {"ok": True, "exists": (forge / "electron" / "main.js").is_file()},
            "forge_dist": {"ok": True, "products": [x.name for x in (forge / "dist" / "products").iterdir()] if (forge / "dist" / "products").is_dir() else []},
            "forge_cli_hint": {"ok": True, "commands": ["status", "strategies", "market", "route", "budget", "ledger", "workflow"]},
            "forge_listening": {"ok": True, "listening": bool(listening.get("ok"))},
        }
        return table.get(t) or {"ok": False, "error": t}

    if t.startswith("engine_"):
        listening = _http("http://127.0.0.1:8090/api/v1/overview")
        if not listening.get("ok"):
            listening = _http("http://127.0.0.1:8089/health")
        table = {
            "engine_available": {"ok": True, "available": (engine / "sovereign_infrastructure").is_dir()},
            "engine_root": {"ok": True, "path": str(engine)},
            "engine_github": {"ok": True, "url": "https://github.com/FreddyCreates/sovereign-engine"},
            "engine_dash": {"ok": True, "url": "http://127.0.0.1:8090"},
            "engine_api": {"ok": True, "url": "http://127.0.0.1:8089"},
            "engine_tests": {"ok": True, "exists": (engine / "tests" / "test_nextgen_systems.py").is_file()},
            "engine_android": {"ok": True, "exists": (engine / "android-app").is_dir()},
            "engine_docker": {"ok": True, "exists": (engine / "Dockerfile").is_file()},
            "engine_readme": {"ok": True, "exists": (engine / "README.md").is_file()},
            "engine_whitepaper": {"ok": True, "exists": (engine / "TECHNICAL_WHITEPAPER.md").is_file()},
            "engine_onboarding": {"ok": True, "exists": (engine / "TEAM_ONBOARDING.md").is_file()},
            "engine_bus": {"ok": True, "exists": (engine / "sovereign_infrastructure" / "substrate_bus.py").is_file()},
            "engine_lifecycle": {"ok": True, "exists": (engine / "sovereign_infrastructure" / "nextgen_systems" / "nextgen_master_orchestrator.py").is_file()},
            "engine_listening": {"ok": True, "listening": bool(listening.get("ok"))},
            "engine_billing": _t_billing_lookup({"name": "pocket_pro"}),
        }
        if t == "engine_aura":
            try:
                from itsnotai_internal.engine_sdk import EngineSDK, _ensure

                if EngineSDK().available():
                    _ensure()
                    from aura_engine import AURAEngine

                    AURAEngine()
                    return {"ok": True, "core": "AURA"}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        if t == "engine_mint":
            try:
                from itsnotai_internal.engine_sdk import EngineSDK, _ensure

                if EngineSDK().available():
                    _ensure()
                    from mint_engine import MINTEngine

                    m = MINTEngine(100000.0)
                    st = m.get_tokenomics_state() if hasattr(m, "get_tokenomics_state") else True
                    return {"ok": True, "core": "MINT", "state": st}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        if t == "engine_nexs":
            try:
                from itsnotai_internal.engine_sdk import EngineSDK, _ensure

                if EngineSDK().available():
                    _ensure()
                    from nexs_engine import NEXSEngine

                    NEXSEngine()
                    return {"ok": True, "core": "NEXS"}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        if t == "engine_grid":
            return _t_grid(p)
        if t == "engine_ppp":
            try:
                import sys

                cores = str(engine / "sovereign_infrastructure" / "cores")
                if cores not in sys.path:
                    sys.path.insert(0, cores)
                from ppp_localization_core import PPPLocalizationCore

                return {"ok": True, "price": PPPLocalizationCore().compute_local_price(99.0, "BR")}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return table.get(t) or {"ok": False, "error": t}

    if t.startswith("mesie_"):
        import importlib.util

        spec = importlib.util.find_spec("mesie")
        table = {
            "mesie_status": {"ok": spec is not None, "importable": spec is not None},
            "mesie_ok": {"ok": spec is not None},
            "mesie_importable": {"ok": True, "importable": spec is not None},
            "mesie_path": {"ok": True, "path": getattr(spec, "origin", None) if spec else None},
            "mesie_root_exists": {"ok": True, "exists": mesie.is_dir(), "path": str(mesie)},
            "mesie_readme": {"ok": True, "exists": (mesie / "README.md").is_file()},
            "mesie_doi": {"ok": True, "doi": "10.5281/zenodo.20598320"},
            "mesie_hub": {"ok": True, "skill": "mesie-hub"},
            "mesie_n_bands": {"ok": True, "n_bands": 8},
            "mesie_phase": {"ok": True, "phase_aware": True},
            "mesie_sdk_class": {"ok": True, "class": "SpectralIntelligenceSDK"},
            "mesie_editable": {"ok": True, "editable": mesie.is_dir()},
            "mesie_pip": {"ok": True, "pip_show": "0.2.0", "runtime": "1.2.0"},
            "mesie_bindings": {"ok": True, "bindings": [x.name for x in (mesie / "bindings").iterdir()] if (mesie / "bindings").is_dir() else []},
        }
        if t == "mesie_version":
            try:
                import mesie

                return {"ok": True, "version": getattr(mesie, "__version__", None)}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return table.get(t) or {"ok": False, "error": t}

    if t.startswith("billing_"):
        from itsnotai_internal.billing_sdk import ALIASES, CANONICAL_PLANS, SCHEMA as BS

        if t == "billing_plans":
            return {"ok": True, "plans": CANONICAL_PLANS}
        if t == "billing_aliases":
            return {"ok": True, "aliases": ALIASES}
        if t == "billing_schema":
            return {"ok": True, "schema": BS}
        if t == "billing_seats":
            return {"ok": True, "seats": {k: v.get("seats") for k, v in CANONICAL_PLANS.items()}}
        if t == "billing_usd":
            return {"ok": True, "usd": {k: v.get("usd") for k, v in CANONICAL_PLANS.items()}}
        if t == "billing_entitlements":
            return {"ok": True, "entitlements": {k: v.get("entitlements") for k, v in CANONICAL_PLANS.items()}}
        key = {"billing_starter": "pocket_starter", "billing_pro": "pocket_pro", "billing_team": "pocket_team", "billing_refill": "pock_refill"}.get(t)
        if key:
            return {"ok": True, "plan": CANONICAL_PLANS[key], "id": key}
        return {"ok": False, "error": t}

    if t.startswith("nexus_"):
        nx = home / "OneDrive" / "nexus"
        cache = home / ".nexus" / "cache"
        drafts = home / ".nexus" / "drafts"
        st = _t_nexus(p)
        table = {
            "nexus_ok": {"ok": bool(st.get("ok"))},
            "nexus_online": {"ok": True, "online": bool(st.get("ok"))},
            "nexus_cache": {"ok": True, "path": str(cache), "exists": cache.is_dir()},
            "nexus_drafts": {"ok": True, "path": str(drafts), "exists": drafts.is_dir()},
            "nexus_path": {"ok": True, "path": str(nx), "exists": nx.is_dir()},
            "nexus_ship": {"ok": True, "ship_date": "2026-07-28"},
            "nexus_philosophy": {"ok": True, "text": "Protocols are the intelligence. Not a feature. The substrate."},
            "nexus_bridge": st,
            "nexus_list_mcp": {"ok": True, "hint": "nexus__nexus_list_mcp_servers"},
            "nexus_workers": {"ok": True, "workers": ["archon", "scribe", "cipher", "forge", "herald", "lumen", "bridge", "weaver", "hermes"]},
        }
        return table.get(t) or {"ok": False, "error": t}

    if t == "voice_url":
        return {"ok": True, "url": os.environ.get("POCKET_VOICE_URL") or "http://127.0.0.1:8790"}
    if t == "phone_lan":
        return {"ok": True, "url": "http://192.168.12.127:8787/phone"}
    if t == "phone_remote":
        return {"ok": True, "url": "https://pocket.medinatechlabs.net/phone"}
    if t == "hz_docs":
        doc = od / "hz-offline" / "docs" / "PHONE_MCP.md"
        return {"ok": True, "path": str(doc), "exists": doc.is_file()}
    if t == "auro_root":
        root = home / "Documents" / "GitHub" / "Auro14B"
        return {"ok": True, "path": str(root), "exists": root.is_dir()}
    if t == "mesh_ok":
        try:
            from pocket.mesh_disk import MESH

            return {"ok": Path(MESH).exists(), "path": str(MESH)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    if t == "vdisk_ok":
        try:
            from pocket.mesh_disk import VDISK

            return {"ok": Path(VDISK).exists(), "path": str(VDISK)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    if t == "tunnel_ok":
        c = _t_public_url(p)
        return {"ok": bool(c.get("public_url")), "public_url": c.get("public_url")}
    if t == "studio_ok":
        return {"ok": True, "url": "http://127.0.0.1:8787/studio"}
    if t == "mail_ok":
        try:
            from pocket.agent_mail import status as am

            return am()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    return {"ok": False, "error": f"unhandled extra {t}"}
