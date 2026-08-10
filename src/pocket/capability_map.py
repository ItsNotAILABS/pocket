"""Live host capability map — what AIs can actually do *right now*.

Injected into AI workspace so agents stop guessing and re-probing.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List


def build_capability_map() -> Dict[str, Any]:
    caps: Dict[str, Any] = {
        "schema": "pocket.capability-map.v1",
        "at": time.time(),
        "at_h": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engines": {},
        "embodiment": {},
        "infra": {},
        "safety": {},
        "ai_workspace": {},
        "infinite_wiki": {
            "get_file_profile": "POST /v1/wiki/profile {path}",
            "read_file_lines": "POST /v1/wiki/lines {path,start,end}",
            "find_symbol": "POST /v1/wiki/symbol {name}",
            "search": "POST /v1/wiki/search {q}",
            "index_tree": "POST /v1/wiki/index {root}",
            "rule": "Never load whole multi-kLOC files — profile then slice",
        },
        "agent_os": {
            "dashboard": "GET /v1/os",
            "systems": "GET /v1/os/systems",
            "parity": "GET /v1/os/parity",
            "projects": "GET|POST /v1/os/projects",
            "run": "POST /v1/os/run {project_id}",
            "run_artifact": "POST /v1/os/run-artifact {symbol}",
            "screen": "/os",
            "rule": "Every agent system is first-class — prefer /os then desk modes",
        },
        "tips": [],
    }
    try:
        from pocket.executor import available_engines

        eng = available_engines()
        caps["engines"] = {
            "codex": bool(eng.get("codex")),
            "grok": bool(eng.get("grok")),
            "claude": bool(eng.get("claude")),
            "claude_agent_sdk": bool(eng.get("claude_agent_sdk")),
            "coding_swarm": True,
            "pixel_memory": True,
            "agent_os": True,
            "shell": True,
            "wsl": bool(eng.get("wsl")),
            "desktop": True,
            "browser": True,
            "woa": True,
            "paths": {
                "codex": eng.get("codex_path"),
                "grok": eng.get("grok_path"),
                "claude": eng.get("claude_path"),
            },
        }
    except Exception as e:
        caps["engines"] = {"error": str(e)}

    try:
        from pocket.desktop import list_apps

        apps = list_apps() if callable(list_apps) else []
        if isinstance(apps, dict):
            apps = apps.get("apps") or apps.get("items") or []
        caps["embodiment"]["apps"] = [
            (a.get("id") if isinstance(a, dict) else str(a)) for a in (apps or [])[:40]
        ]
        caps["embodiment"]["app_count"] = len(apps or [])
    except Exception:
        try:
            from pocket.safety import ALLOWED_APPS

            caps["embodiment"]["apps"] = sorted(list(ALLOWED_APPS))[:40]
            caps["embodiment"]["app_count"] = len(ALLOWED_APPS)
        except Exception as e:
            caps["embodiment"]["error"] = str(e)

    caps["embodiment"].update(
        {
            "screenshot": True,
            "vision": True,
            "vision_first_class": True,
            "oculus": True,
            "browser_agent": True,
            "offload_queue": True,
            "proof_packs": True,
            "ui_click": True,
            "clipboard": True,
        }
    )

    try:
        from pocket.mesh_disk import mesh_root

        caps["infra"]["mesh_root"] = str(mesh_root())
        caps["infra"]["agent_bus"] = True
        caps["infra"]["channels"] = ["freq-0", "freq-coding", "freq-4"]
    except Exception as e:
        caps["infra"]["mesh"] = str(e)

    try:
        from pocket.ai_workspace import ROOT as AW

        caps["ai_workspace"]["root"] = str(AW)
        caps["ai_workspace"]["auto_inject"] = True
    except Exception:
        pass

    try:
        from pocket.learn import list_learned

        skills = list_learned()
        caps["infra"]["learned_skills"] = len(skills)
    except Exception:
        caps["infra"]["learned_skills"] = 0

    try:
        from pocket.offload_queue import list_tasks

        caps["infra"]["offload_queued"] = len(list_tasks(status="queued", limit=50))
        caps["infra"]["offload_done"] = len(list_tasks(status="done", limit=50))
    except Exception:
        pass

    caps["safety"] = {
        "shell_allowlist": True,
        "app_allowlist": True,
        "url_policy": True,
        "audit_log": str((__import__("pathlib").Path.home() / ".pocket" / "safety.log")),
        "paper_money_only_for_parallax": True,
    }

    # Capability sandbox (Wasm-shaped) + voice + studios
    try:
        from pocket.agent_sandbox import status as sb_status, list_profiles, wasmtime_available

        sb = sb_status()
        prof = list_profiles().get("profiles") or {}
        caps["sandbox"] = {
            "profiles": list(prof.keys()),
            "wasmtime": wasmtime_available(),
            "receipts_dir": sb.get("receipts_dir"),
            "grant": "POST /v1/sandbox/grant",
            "check": "POST /v1/sandbox/check",
            "read": "POST /v1/sandbox/read",
            "write": "POST /v1/sandbox/write",
            "voice": "POST /v1/sandbox/voice  (needs pocket-voice :8790)",
            "wasm": "POST /v1/sandbox/wasm",
            "doc": "docs/research/POCKET_AGENT_WASM_SANDBOX.md",
        }
    except Exception as e:
        caps["sandbox"] = {"error": str(e)[:120]}

    caps["voice"] = {
        "oss_repo": "https://github.com/ItsNotAILABS/pocket-voice-to-text",
        "api_default": "http://127.0.0.1:8790",
        "catalog": "GET http://127.0.0.1:8790/v1",
        "desk_mic": "browser STT on /desk 🎙",
        "agent_bridge": "POST /v1/sandbox/voice",
        "doc": "docs/AGENT_VOICE.md",
    }

    caps["studios"] = {
        "desk": {"url": "/desk", "job": "Chat with Codex/Grok — daily home"},
        "work_studio": {
            "url": "/work",
            "job": "Design work types & loops → hand off to desk",
            "api": ["GET /v1/work-studio", "POST /v1/work-loops/generate", "POST /v1/dual"],
            "handoff": "localStorage pocket_work_handoff → /desk?agent=",
        },
        "product_studio": {
            "url": "/studio",
            "job": "Product demos / viral exports from recordings",
            "api": ["POST /v1/studio/product_phone", "POST /v1/studio/product_web", "GET /v1/record/*"],
        },
        "rule": "Work Studio designs labor; Product Studio packages demos; Desk runs agents",
    }

    caps["pixel_memory"] = {
        "status": "GET /v1/vmem",
        "put": "POST /v1/vmem/put",
        "look": "GET /v1/vmem/look?symbol=",
        "pass": "POST /v1/vmem/pass",
    }

    caps["tips"] = [
        "Desk is home — Codex and Grok are separate agents",
        "Custom agents run under sandbox profiles (receipts in ~/.pocket/sandbox)",
        "Work Studio designs loops; Send to desk to run them",
        "Product Studio (/studio) is demos/exports — not agent chat",
        "Voice for agents: start pocket-voice on :8790 then POST /v1/sandbox/voice",
        "Prefer /v1/offload for multi-step real-world work",
        "Read AI_WORKSPACE CONTEXT before listing the repo",
    ]
    return caps


def capability_markdown(cmap: Dict[str, Any] | None = None) -> str:
    c = cmap or build_capability_map()
    eng = c.get("engines") or {}
    emb = c.get("embodiment") or {}
    inf = c.get("infra") or {}
    lines = [
        "# Host capability map (live)",
        "",
        f"Updated: {c.get('at_h')}",
        "",
        "## Engines",
        f"- Codex: {eng.get('codex')} · Grok: {eng.get('grok')} · Claude: {eng.get('claude')}",
        f"- Desktop/Browser/WOA: on",
        "",
        "## Embodiment",
        f"- Apps allowlisted: {emb.get('app_count', 0)}",
        f"- Screenshot/vision/offload/proof: yes",
        f"- Sample apps: {', '.join((emb.get('apps') or [])[:12])}",
        "",
        "## Infra",
        f"- Mesh: {inf.get('mesh_root', '—')}",
        f"- Learned skills: {inf.get('learned_skills', 0)}",
        f"- Offload queued/done: {inf.get('offload_queued', 0)}/{inf.get('offload_done', 0)}",
        "",
        "## Tips",
    ]
    for t in c.get("tips") or []:
        lines.append(f"- {t}")
    return "\n".join(lines)
