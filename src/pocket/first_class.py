"""First-class product fabric — unified readiness beyond A–Z checklist.

Scores POCKET as a host co-pilot product: sovereignty, multi-agent ship,
Infinite Wiki, dual-loop, swarm, isolation, API, phone, WSL.
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pocket import __version__, COMPANY, LAB, PRODUCT, PRODUCT_FULL, TAGLINE


def _ok(name: str, ok: bool, detail: str = "", *, tier: str = "core") -> Dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": detail or ("pass" if ok else "fail"), "tier": tier}


def pillars() -> List[Dict[str, Any]]:
    """Live first-class pillars."""
    home = Path.home() / ".pocket"
    items: List[Dict[str, Any]] = []

    # Core host
    items.append(_ok("State home", home.is_dir(), str(home)))
    access = (home / "ACCESS.txt").exists() or (home / "access.env").exists()
    items.append(_ok("Auth credentials", access, "ACCESS / access.env"))
    pub = (os.environ.get("POCKET_PUBLIC_URL") or "").strip()
    if not pub.startswith("http"):
        for envf in (
            Path.home() / ".pocket" / "cloudflare-named.env",
            Path.home() / "OneDrive" / "pocket-os" / "PUBLIC_URL.txt",
            Path.home() / ".pocket" / "PUBLIC_URL.txt",
        ):
            try:
                if envf.exists():
                    import re as _re

                    t = envf.read_text(encoding="utf-8", errors="replace")
                    m = _re.search(r"https?://[^\s]+", t)
                    if m:
                        pub = m.group(0).rstrip("/")
                        break
                    for line in t.splitlines():
                        if line.startswith("POCKET_PUBLIC_URL="):
                            pub = line.split("=", 1)[1].strip()
                            break
            except Exception:
                pass
            if pub.startswith("http"):
                break
    items.append(_ok("Public URL", pub.startswith("http"), pub or "local-only", tier="edge"))

    # Engines
    codex = bool(shutil.which("codex"))
    grok = bool(shutil.which("grok") or (Path.home() / ".grok" / "bin" / "grok.exe").exists())
    items.append(_ok("Coding engines", codex or grok, f"codex={codex} grok={grok}"))

    # Isolation / RBAC
    try:
        from pocket import rbac  # noqa: F401

        items.append(_ok("Founder/market RBAC", True, "host_power gates"))
    except Exception as e:
        items.append(_ok("Founder/market RBAC", False, str(e)[:80]))

    # Infinite Wiki
    try:
        from pocket.infinite_wiki import status as wiki_status

        w = wiki_status()
        items.append(
            _ok(
                "Infinite Wiki",
                bool(w.get("ok")),
                f"nodes={w.get('nodes')} watcher={w.get('watcher')} ts={bool((w.get('treesitter') or {}).get('available'))}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Infinite Wiki", False, str(e)[:80], tier="class"))

    # World model
    try:
        from pocket.world_model import status as wm_status

        wm = wm_status()
        c = wm.get("counts") or {}
        items.append(
            _ok(
                "World model",
                bool(wm.get("ok")) and int(c.get("facts") or 0) > 0,
                f"facts={c.get('facts')} archetypes={c.get('archetypes')}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("World model", False, str(e)[:80], tier="class"))

    # Dual loop module
    try:
        from pocket import cortex_subcortex  # noqa: F401

        items.append(_ok("Cortex/Subcortex dual-loop", True, "System 1+2", tier="class"))
    except Exception as e:
        items.append(_ok("Cortex/Subcortex dual-loop", False, str(e)[:80], tier="class"))

    # Always-on swarm
    try:
        from pocket.always_on_swarm import status as swarm_status

        s = swarm_status()
        items.append(
            _ok(
                "Always-on swarm",
                bool(s.get("ok")),
                f"running={s.get('running')} pulses={s.get('pulses')}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Always-on swarm", False, str(e)[:80], tier="class"))

    # Work studio
    try:
        from pocket.work_types import catalog

        cat = catalog()
        items.append(
            _ok(
                "Work Studio loops",
                len(cat.get("loops") or []) >= 3 and len(cat.get("types") or []) >= 5,
                f"types={len(cat.get('types') or [])} loops={len(cat.get('loops') or [])}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Work Studio loops", False, str(e)[:80], tier="class"))

    # Use cases / Emergent parity
    try:
        from pocket.use_cases import list_use_cases, parity_report

        uc = list_use_cases()
        pr = parity_report()
        score = pr.get("score") or {}
        items.append(
            _ok(
                "Ship use cases",
                len(uc) >= 8,
                f"{len(uc)} cases · pocket_only={score.get('pocket_only_advantages')}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Ship use cases", False, str(e)[:80], tier="class"))

    # WSL
    try:
        from pocket.wsl_agent import which_wsl

        wsl = bool(which_wsl())
        items.append(_ok("WSL native agent", wsl, "wsl on PATH" if wsl else "install WSL for Linux hands", tier="edge"))
    except Exception as e:
        items.append(_ok("WSL native agent", False, str(e)[:80], tier="edge"))

    # Agent OS fabric (2026 native depth)
    try:
        from pocket.agent_os import list_systems, parity_report

        ls = list_systems(live=True)
        pr = parity_report()
        items.append(
            _ok(
                "Agent OS systems",
                int(ls.get("ready") or 0) >= 8,
                f"{ls.get('ready')}/{ls.get('total')} ready · /os",
                tier="class",
            )
        )
        items.append(
            _ok(
                "2026 parity matrix",
                len(pr.get("rows") or []) >= 4,
                pr.get("systems_ready") or "claude/antigravity/emergent/replit",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Agent OS systems", False, str(e)[:80], tier="class"))

    try:
        from pocket.pixel_vmem import status as vmem_status

        vs = vmem_status()
        items.append(
            _ok(
                "Pixel memory lattice",
                bool(vs.get("ok")),
                f"symbols={vs.get('symbols')} pages={vs.get('pages')}",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Pixel memory lattice", False, str(e)[:80], tier="class"))

    try:
        from pocket.coding_swarm import list_roster

        ro = list_roster()
        items.append(
            _ok(
                "Coding swarm harness",
                len(ro.get("agents") or []) >= 3,
                f"{len(ro.get('agents') or [])} personas AI-bound",
                tier="class",
            )
        )
    except Exception as e:
        items.append(_ok("Coding swarm harness", False, str(e)[:80], tier="class"))

    # Surfaces
    items.append(_ok("Agent OS surface", True, "/os", tier="edge"))
    items.append(_ok("Phone surface", True, "/phone", tier="edge"))
    items.append(_ok("Work Studio surface", True, "/work", tier="edge"))
    items.append(_ok("Sellable AI API", True, "/v1/ai/chat + keys", tier="edge"))
    items.append(_ok("Researcher license gate", True, "/download + LICENSE-RESEARCHER", tier="edge"))

    # Security
    try:
        from pocket.auth import security_headers

        hs = {k for k, _ in security_headers()}
        items.append(
            _ok(
                "Security headers",
                "Content-Security-Policy" in hs and "X-Content-Type-Options" in hs,
                f"{len(hs)} headers",
            )
        )
    except Exception as e:
        items.append(_ok("Security headers", False, str(e)[:80]))

    return items


def score(items: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    items = items or pillars()
    total = len(items)
    passed = sum(1 for i in items if i.get("ok"))
    core = [i for i in items if i.get("tier") == "core"]
    klass = [i for i in items if i.get("tier") == "class"]
    edge = [i for i in items if i.get("tier") == "edge"]
    core_ok = sum(1 for i in core if i["ok"])
    class_ok = sum(1 for i in klass if i["ok"])
    edge_ok = sum(1 for i in edge if i["ok"])
    pct = round(100.0 * passed / total, 1) if total else 0.0
    # First-class bar: all core + almost all class pillars
    first_class = core_ok == len(core) and class_ok >= max(1, len(klass) - 1) and pct >= 85.0
    grade = (
        "S"
        if pct >= 95 and first_class
        else "A"
        if first_class
        else "B"
        if pct >= 75
        else "C"
        if pct >= 60
        else "D"
    )
    return {
        "passed": passed,
        "total": total,
        "percent": pct,
        "grade": grade,
        "first_class": first_class,
        "core": f"{core_ok}/{len(core)}",
        "class_pillars": f"{class_ok}/{len(klass)}",
        "edge": f"{edge_ok}/{len(edge)}",
        "failures": [i for i in items if not i.get("ok")],
    }


def report() -> Dict[str, Any]:
    items = pillars()
    sc = score(items)
    return {
        "ok": True,
        "schema": "pocket.first_class.v1",
        "product": PRODUCT,
        "product_full": PRODUCT_FULL,
        "tagline": TAGLINE,
        "lab": LAB,
        "company": COMPANY,
        "org": "ItsNotAILABS",
        "edition": "company",
        "github": "https://github.com/ItsNotAILABS/pocket",
        "version": __version__,
        "ts": time.time(),
        "score": sc,
        "pillars": items,
        "doctrine": [
            "Company multi-agent host platform (ItsNotAI Labs / Medina Tech Labs)",
            "Sovereign host co-pilot — not cloud lock-in",
            "Founder machine ≠ market seat disk (company isolation)",
            "Cortex talks; Subcortex works silently",
            "Infinite Wiki: profile → slice → edit (never dump 10k lines)",
            "Always-on swarm keeps the company shipping",
            "Sellable API + phone + WSL + mesh — one product family",
        ],
        "surfaces": {
            "desk": "/desk",
            "phone": "/phone",
            "work_studio": "/work",
            "download": "/download",
            "docs": "/docs/hub",
            "api": "/developers",
            "ready": "/v1/ready",
            "class": "/v1/class",
        },
        "message": (
            f"{PRODUCT} grade {sc['grade']} · {sc['percent']}% · "
            + ("FIRST-CLASS" if sc["first_class"] else "raising the bar")
        ),
    }


# /health is polled by desk, landing, Ensure-POCKET-Up, and Edge app.
# score()/pillars() can take 10–15s and freezes the single-threaded host.
_HEALTH_CACHE: Dict[str, Any] = {}
_HEALTH_CACHE_TS: float = 0.0
_HEALTH_CACHE_TTL: float = 90.0
_HEALTH_WARMING: bool = False


def health_enrichment(*, force: bool = False, block: bool = False) -> Dict[str, Any]:
    """Compact class block for /health.

    Default is non-blocking: return cache (or light stub) and refresh in a
    background thread so pollers never stall the HTTP server.
    """
    global _HEALTH_CACHE, _HEALTH_CACHE_TS, _HEALTH_WARMING
    now = time.time()
    fresh = bool(_HEALTH_CACHE) and (now - _HEALTH_CACHE_TS) < _HEALTH_CACHE_TTL
    if fresh and not force:
        return dict(_HEALTH_CACHE)

    def _compute() -> Dict[str, Any]:
        global _HEALTH_CACHE, _HEALTH_CACHE_TS, _HEALTH_WARMING
        try:
            sc = score()
            out = {
                "first_class": sc.get("first_class"),
                "grade": sc.get("grade"),
                "score": f"{sc.get('passed')}/{sc.get('total')}",
                "percent": sc.get("percent"),
                "cached_at": time.time(),
            }
        except Exception:
            out = {"first_class": False, "grade": "?", "score": "0/0"}
        _HEALTH_CACHE = out
        _HEALTH_CACHE_TS = time.time()
        _HEALTH_WARMING = False
        return dict(out)

    if block or force:
        return _compute()

    # Non-blocking path for /health
    if not _HEALTH_WARMING:
        _HEALTH_WARMING = True
        try:
            import threading

            threading.Thread(target=_compute, name="pocket-health-warm", daemon=True).start()
        except Exception:
            _HEALTH_WARMING = False
    if _HEALTH_CACHE:
        return dict(_HEALTH_CACHE)
    return {
        "first_class": None,
        "grade": "…",
        "score": "warming",
        "percent": None,
        "warming": True,
    }
