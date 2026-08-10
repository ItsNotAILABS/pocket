"""POCKET internal API surface — single map for desk, agents, MCP, Grok/HTTP clients.

Organized by domain so the platform reads as one product, not scattered routes.
Server keeps handlers; this module is the catalog + health of the surface.
"""

from __future__ import annotations

from typing import Any, Dict, List

from pocket import __version__, PRODUCT, TAGLINE

# Domain → routes (method implied by path group; POST noted)
SURFACE: Dict[str, List[Dict[str, str]]] = {
    "core": [
        {"path": "/health", "method": "GET", "summary": "Liveness"},
        {"path": "/v1/status", "method": "GET", "summary": "Host status + engines"},
        {"path": "/v1/ready", "method": "GET", "summary": "Production checklist"},
        {"path": "/v1/api", "method": "GET", "summary": "This catalog"},
        {"path": "/v1/platform", "method": "GET", "summary": "Platform manifest"},
        {"path": "/desk", "method": "GET", "summary": "Agent desk UI"},
        {"path": "/os", "method": "GET", "summary": "Agent OS hub"},
    ],
    "habitat_hybrid": [
        {"path": "/v1/habitat", "method": "GET", "summary": "Residents + rooms + activity"},
        {"path": "/v1/habitat", "method": "POST", "summary": "open true|false"},
        {"path": "/v1/habitat/pulse", "method": "POST", "summary": "Pulse resident status"},
        {"path": "/v1/habitat/assign", "method": "POST", "summary": "Assign task to resident"},
    ],
    "screen_vcomp": [
        {"path": "/v1/screen", "method": "GET", "summary": "Share mode status"},
        {"path": "/v1/screen", "method": "POST", "summary": "mode off|view|control"},
        {"path": "/v1/screen/frame", "method": "GET", "summary": "Live JPEG frame"},
        {"path": "/v1/screen/context", "method": "GET", "summary": "Fusion context for agents"},
        {"path": "/v1/screen/act", "method": "POST", "summary": "Mouse/type when control"},
        {"path": "/v1/vcomp", "method": "GET", "summary": "Virtual computer status"},
        {"path": "/v1/vcomp/open", "method": "POST", "summary": "Boot VComp"},
        {"path": "/v1/vcomp/sense", "method": "POST", "summary": "Fusion sense"},
        {"path": "/v1/vcomp/act", "method": "POST", "summary": "Act on host"},
        {"path": "/v1/vcomp/shell", "method": "POST", "summary": "Shell in vcomp workspace"},
    ],
    "work_mode": [
        {"path": "/v1/work", "method": "GET", "summary": "Live working sessions"},
        {"path": "/v1/work/start", "method": "POST", "summary": "Start persistent work"},
        {"path": "/v1/work/turn", "method": "POST", "summary": "Turn inside work mode"},
        {"path": "/v1/work/package", "method": "POST", "summary": "Bag conversation"},
        {"path": "/v1/work/handoff", "method": "POST", "summary": "Make artifacts from package"},
    ],
    "mcp_cli": [
        {"path": "/v1/mcp", "method": "GET", "summary": "10 MCPs (3 internal + 7 external)"},
        {"path": "/v1/mcp/tools", "method": "GET", "summary": "Flattened tool list"},
        {"path": "/v1/mcp/invoke", "method": "POST", "summary": "Agent invoke server.tool"},
        {"path": "/v1/cli", "method": "GET", "summary": "CLI inventory"},
        {"path": "/v1/cli/run", "method": "POST", "summary": "Run CLI for agents (no user tabs)"},
    ],
    "drafts_preview": [
        {"path": "/v1/work-surface", "method": "GET", "summary": "Hierarchy + drafts"},
        {"path": "/v1/drafts", "method": "GET", "summary": "List drafts"},
        {"path": "/v1/drafts", "method": "POST", "summary": "Create draft"},
        {"path": "/v1/drafts/promote", "method": "POST", "summary": "Promote → folder|github|pixel"},
        {"path": "/v1/preview", "method": "GET", "summary": "Preview store status"},
        {"path": "/v1/preview/{id}", "method": "GET", "summary": "HTML iframe document"},
        {"path": "/v1/preview", "method": "POST", "summary": "Put HTML preview"},
    ],
    "github": [
        {"path": "/v1/github", "method": "GET", "summary": "gh auth status"},
        {"path": "/v1/github/repos", "method": "GET", "summary": "List repos"},
        {"path": "/v1/github/issues", "method": "GET", "summary": "List issues"},
        {"path": "/v1/github/prs", "method": "GET", "summary": "List PRs"},
        {"path": "/v1/github/clone", "method": "POST", "summary": "Clone (agent CLI)"},
        {"path": "/v1/github/create", "method": "POST", "summary": "Create repo"},
        {"path": "/v1/github/pr", "method": "POST", "summary": "Open PR"},
    ],
    "agents_jobs": [
        {"path": "/v1/sessions", "method": "GET", "summary": "List sessions"},
        {"path": "/v1/sessions", "method": "POST", "summary": "Create session"},
        {"path": "/v1/jobs", "method": "POST", "summary": "Enqueue agent job"},
        {"path": "/v1/agents/catalog", "method": "GET", "summary": "Desk catalog"},
        {"path": "/v1/agents/first-class", "method": "GET", "summary": "Full registry"},
        {"path": "/v1/harness", "method": "GET", "summary": "Harness status"},
        {"path": "/v1/harness/live", "method": "GET", "summary": "Live subagents"},
        {"path": "/v1/subagents", "method": "GET", "summary": "Helpers roster"},
        {"path": "/v1/swarm", "method": "GET", "summary": "Coding swarm roster"},
    ],
    "vision_fusion": [
        {"path": "/v1/vision/observe", "method": "GET", "summary": "OCULUS observe"},
        {"path": "/v1/vision/ui_map", "method": "GET", "summary": "UI map"},
        {"path": "/v1/vision/understand", "method": "GET", "summary": "Pixel understand"},
        {"path": "/v1/live/vision", "method": "GET", "summary": "Live frame"},
        {"path": "/v1/fusion/remake", "method": "POST", "summary": "Fusion remake"},
        {"path": "/v1/rfe/synthesize", "method": "POST", "summary": "RFE materialize"},
    ],
    "conversational_fusion": [
        {"path": "/v1/fusion/voice", "method": "GET", "summary": "Conversational Fusion schema + DFW experts"},
        {"path": "/v1/fusion/voice", "method": "POST", "summary": "Fuse voice metadata → expert/patience/preload"},
        {"path": "/v1/fusion/voice/schema", "method": "GET", "summary": "Metadata + fusion schemas"},
        {"path": "/v1/fusion/voice/last", "method": "GET", "summary": "Last fusion for session_id"},
    ],
    "phone_pair": [
        {"path": "/phone", "method": "GET", "summary": "POCKET Phone (Aria/Working first-class)"},
        {"path": "/v1/node/pair", "method": "POST", "summary": "Mint pair code (desk)"},
        {"path": "/v1/node/redeem", "method": "POST", "summary": "Phone redeems pair code"},
        {"path": "/v1/node/hello", "method": "GET", "summary": "Node presence"},
        {"path": "/v1/node/status", "method": "GET", "summary": "Peers + tray"},
    ],
    "skills_platform": [
        {"path": "/v1/platform/coherent", "method": "GET", "summary": "One map: surfaces + skills + flow"},
        {"path": "/v1/skills", "method": "GET", "summary": "Full skill suite (platform + Latin)"},
        {"path": "/v1/skills/run", "method": "POST", "summary": "Run skill for agents"},
        {"path": "/v1/skills/platform", "method": "GET", "summary": "Platform skills only"},
    ],
    "sovereign_remote_iot": [
        {"path": "/v1/sovereign", "method": "GET", "summary": "Doctrine + our clouds + remote browser + IoT"},
        {"path": "/v1/computing-clouds", "method": "GET", "summary": "OUR computing clouds inventory"},
        {"path": "/v1/remote-browser", "method": "GET", "summary": "Our remote browser status (must beat theirs)"},
        {"path": "/v1/remote-browser/benchmark", "method": "GET", "summary": "Remote browser hard suite"},
        {"path": "/v1/remote-browser/open", "method": "POST", "summary": "Open signed-in Edge URL"},
        {"path": "/v1/remote-browser/sense", "method": "POST", "summary": "Fusion sense pack"},
        {"path": "/v1/remote-browser/act", "method": "POST", "summary": "Host control act"},
        {"path": "/v1/iot", "method": "GET", "summary": "Home IoT + phone bridge"},
        {"path": "/v1/iot/devices", "method": "GET", "summary": "List home devices"},
        {"path": "/v1/iot/devices", "method": "POST", "summary": "Register / seed devices"},
        {"path": "/v1/iot/phone", "method": "GET", "summary": "Phone LAN/remote/pair URLs"},
    ],
    "memory_pixel": [
        {"path": "/v1/vmem", "method": "GET", "summary": "Pixel memory status"},
        {"path": "/v1/vmem/artifacts", "method": "GET", "summary": "List artifacts"},
        {"path": "/v1/vmem/put", "method": "POST", "summary": "Store text"},
        {"path": "/v1/vmem/look", "method": "GET", "summary": "Look symbol"},
        {"path": "/v1/vmem/recreate", "method": "POST", "summary": "Recreate export"},
    ],
    "os_projects": [
        {"path": "/v1/os", "method": "GET", "summary": "Agent OS dashboard"},
        {"path": "/v1/os/systems", "method": "GET", "summary": "Systems live"},
        {"path": "/v1/os/projects", "method": "GET", "summary": "Native projects"},
        {"path": "/v1/os/run", "method": "POST", "summary": "Run project"},
    ],
}

# How the whole product flows together (one shell — not separate apps)
FLOW = [
    "1. Habitat — agents live/work (GUI floor; open by default)",
    "2. Chat — conversation with one seated agent (desk center)",
    "3. Screen — optional share View/Control + VComp (all agents)",
    "4. Workspace — summary, files, helpers, Get pair code",
    "5. Phone — /phone · Aria/Working first-class · redeem pair",
    "6. Working mode — voice + screen + package → handoff artifacts",
    "7. Conversational Fusion — voice metadata → DFW expert/patience (POCKET)",
    "8. MCP/CLI + skills — agents call headlessly (no user tabs)",
    "9. Discover — GET /v1/platform/coherent · skill platform_map",
]

# Source modules by domain (folder sense without mass renames)
MODULES = {
    "habitat_hybrid": ["agent_habitat.py", "app_ui.py"],
    "screen_vcomp": ["screen_share.py", "virtual_computer.py", "perception.py", "vision_core.py"],
    "work_mode": ["work_mode.py", "voice_skills.py"],
    "conversational_fusion": ["conversational_fusion.py", "voice_skills.py", "executor.py"],
    "phone_pair": ["phone_ui.py", "node_transfer.py"],
    "mcp_cli": ["mcp_bundle.py", "mcp_server.py", "cli_tools.py"],
    "skills_platform": ["platform_coherence.py", "skill_suite.py", "skill_runner.py"],
    "drafts_preview": ["work_surface.py", "app_preview.py"],
    "github": ["github_hub.py", "repos.py"],
    "agents_jobs": ["executor.py", "worker.py", "agentic_harness.py", "first_class_agents.py", "sessions.py", "jobs.py"],
    "vision_fusion": ["fusion_remake.py", "rfe_kernel.py", "live_vision.py", "page_renderer.py"],
    "memory_pixel": ["pixel_vmem.py"],
    "os_projects": ["agent_os.py"],
}


def catalog() -> Dict[str, Any]:
    routes = []
    for domain, items in SURFACE.items():
        for it in items:
            routes.append({**it, "domain": domain})
    coherent = {}
    try:
        from pocket.platform_coherence import coherent as _coherent

        c = _coherent()
        coherent = {
            "schema": c.get("schema"),
            "skill_count": c.get("skill_count"),
            "find": c.get("find"),
            "user_tabs_in_app": c.get("user_tabs_in_app"),
            "agent_entry": c.get("agent_entry"),
        }
    except Exception:
        coherent = {"hint": "GET /v1/platform/coherent"}
    return {
        "ok": True,
        "schema": "pocket.platform_api.v1",
        "product": PRODUCT,
        "version": __version__,
        "tagline": TAGLINE,
        "flow": FLOW,
        "domains": list(SURFACE.keys()),
        "modules": MODULES,
        "route_count": len(routes),
        "routes": routes,
        "groups": {k: v for k, v in SURFACE.items()},
        "coherent": coherent,
        "auth": "Basic OR X-Pocket-Access OR Bearer sk_pocket_… OR loopback desk",
        "mcp_stdio": "python -m pocket.mcp_server  (PYTHONPATH=src)",
        "desk": "http://127.0.0.1:8787/desk",
        "phone": "http://127.0.0.1:8787/phone",
        "discover": "GET /v1/platform/coherent · skill platform_map",
    }


def health_domains() -> Dict[str, Any]:
    """Lightweight domain health for /v1/ready-style checks."""
    out: Dict[str, Any] = {}
    try:
        from pocket.agent_habitat import status as h

        s = h()
        out["habitat"] = {"ok": True, "residents": len(s.get("residents") or [])}
    except Exception as e:
        out["habitat"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.screen_share import status as sc

        s = sc()
        out["screen"] = {"ok": True, "mode": s.get("mode")}
    except Exception as e:
        out["screen"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.mcp_bundle import catalog as mc

        c = mc()
        out["mcp"] = {"ok": True, "total": c.get("total"), "internal": c.get("internal"), "external": c.get("external")}
    except Exception as e:
        out["mcp"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.cli_tools import inventory

        inv = inventory()
        out["cli"] = {"ok": True, "available": inv.get("available"), "count": inv.get("count")}
    except Exception as e:
        out["cli"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.first_class_agents import summary

        sm = summary()
        out["agents"] = {"ok": True, "total": sm.get("total_agents")}
    except Exception as e:
        out["agents"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.work_mode import status as ws

        w = ws()
        out["work_mode"] = {"ok": True, "live": w.get("live")}
    except Exception as e:
        out["work_mode"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.conversational_fusion import schema as cfs

        s = cfs()
        out["conversational_fusion"] = {"ok": True, "industry": s.get("industry"), "version": s.get("version")}
    except Exception as e:
        out["conversational_fusion"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.platform_coherence import platform_skills

        out["skills_platform"] = {"ok": True, "count": len(platform_skills())}
    except Exception as e:
        out["skills_platform"] = {"ok": False, "error": str(e)[:80]}
    try:
        from pocket.node_transfer import hello

        h = hello()
        out["phone_pair"] = {"ok": True, "node_id": h.get("node_id"), "label": h.get("label")}
    except Exception as e:
        out["phone_pair"] = {"ok": False, "error": str(e)[:80]}
    return {"ok": True, "domains": out}


def bootstrap_platform() -> Dict[str, Any]:
    """Warm modes, habitat, MCP alignment, protocols, identity — call on serve start."""
    notes = []
    try:
        from pocket.first_class_agents import ensure_modes_aligned, summary

        al = ensure_modes_aligned()
        sm = summary()
        notes.append(f"agents={sm.get('total_agents')} modes_aligned={al.get('ok')}")
    except Exception as e:
        notes.append(f"agents:{e}")
    try:
        from pocket.agent_habitat import status as h

        notes.append(f"habitat_residents={len(h().get('residents') or [])}")
    except Exception as e:
        notes.append(f"habitat:{e}")
    try:
        from pocket.mcp_bundle import catalog as mc

        notes.append(f"mcp={mc().get('total')}")
    except Exception as e:
        notes.append(f"mcp:{e}")
    # Wire major protocols + warm imports so agents can use them immediately
    try:
        from pocket.pocket_identity import ensure_protocols_wired

        wire = ensure_protocols_wired()
        notes.extend(wire.get("notes") or [])
        notes.append("identity=POCKET")
    except Exception as e:
        notes.append(f"protocols:{e}")
    try:
        from pocket.economy import domain_status, ensure_twin

        for aid in ("aria", "codex", "claude", "grok", "rah", "plan"):
            ensure_twin(aid)
        ds = domain_status()
        notes.append(f"economy_twins={ds.get('twins')} rail={ds.get('settlement_rail')}")
    except Exception as e:
        notes.append(f"economy:{e}")
    return {"ok": True, "notes": notes, "version": __version__}
