"""Sovereign stack doctrine — own remote browser, own cloud, phone + home IoT.

This is the product truth (not "avoid all cloud"):

1. **Remote browser** — *ours* must beat theirs on every test/benchmark
   (signed-in Edge host, Fusion eyes, Control, VComp, evidence pack).
2. **Phone** — first-class remote desk + **home IoT** (pair, mesh, BLE/HZ, devices).
3. **Remote** — always required (named tunnel, LAN, seats). Already: pocket.medinatechlabs.net.
4. **Cloud models / compute** — *our* version of cloud: work runs on *our* host +
   *our* computing clouds (deploys, Workers-class edge, Auro, NEXUS, mesh vdisk).
   Prompts do not "leave to a third-party Connected Apps product" when inference
   and tools execute inside the sovereign perimeter (host + lab clouds we operate).
   External vendor APIs are optional adapters — not the product identity.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket import PRODUCT, TAGLINE, __version__

ROOT = Path.home() / ".pocket"
_CLOUDS_CACHE: Dict[str, Any] = {}
_CLOUDS_CACHE_AT = 0.0
_CLOUDS_TTL = 8.0
PUBLIC_URL_FILE = ROOT / "PUBLIC_URL.txt"
CF_ENV = ROOT / "cloudflare-named.env"


def _read_public_url() -> str:
    for p in (PUBLIC_URL_FILE, Path(__file__).resolve().parents[2] / "PUBLIC_URL.txt"):
        try:
            if p.is_file():
                for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = line.strip()
                    if line.startswith("http"):
                        return line.rstrip("/")
                    if "https://" in line:
                        # "PHONE / remote users: https://..."
                        i = line.find("https://")
                        return line[i:].split()[0].rstrip("/")
        except Exception:
            pass
    try:
        if CF_ENV.is_file():
            for line in CF_ENV.read_text(encoding="utf-8", errors="replace").splitlines():
                if "POCKET_PUBLIC_URL=" in line or "POCKET_CF_HOSTNAME=" in line:
                    v = line.split("=", 1)[-1].strip().strip('"')
                    if v and not v.startswith("http"):
                        v = "https://" + v
                    if v.startswith("http"):
                        return v.rstrip("/")
    except Exception:
        pass
    return (os.environ.get("POCKET_PUBLIC_URL") or "").rstrip("/")


def _http_ok(url: str, timeout: float = 0.35) -> bool:
    try:
        import urllib.request

        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", 200) or 200) < 500
    except Exception:
        return False


def _forge_root() -> Path:
    env = os.environ.get("SOVEREIGN_FORGE_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for p in (
        Path.home() / "OneDrive" / "sovereign_forge_os",
        Path(r"C:\Users\Medin\OneDrive\sovereign_forge_os"),
    ):
        if p.is_dir():
            return p
    return Path.home() / "OneDrive" / "sovereign_forge_os"


def _engine_root() -> Path:
    env = os.environ.get("SOVEREIGN_ENGINE_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    for p in (
        Path.home() / "OneDrive" / "Documents" / "sovereign-engine",
        Path(r"C:\Users\Medin\OneDrive\Documents\sovereign-engine"),
    ):
        if p.is_dir():
            return p
    return Path.home() / "OneDrive" / "Documents" / "sovereign-engine"


def _forge_cloud() -> Dict[str, Any]:
    root = _forge_root()
    port = int(os.environ.get("SOVEREIGN_FORGE_PORT") or "8789")
    url = f"http://127.0.0.1:{port}"
    present = (root / "engine" / "orchestrator.py").is_file()
    listening = _http_ok(url + "/api/status") if present else False
    if listening:
        status = "listening"
    elif present:
        status = "ready"
    else:
        status = "missing"
    return {
        "id": "sovereign_forge",
        "kind": "trading_envelope",
        "name": "SovereignForge OS",
        "status": status,
        "url": url,
        "path": str(root) if present else None,
        "role": "MESIE-routed strategies · PARALLAX · payments ledger · high-level agents",
        "sovereign": True,
        "port": port,
        "note": "Does not bind POCKET Owner :8787 or Users :8788. Start: SOVEREIGN_FORGE_PORT=8789 python main.py",
        "sdk": "itsnotai_internal.forge_sdk",
    }


def _mesie_cloud() -> Dict[str, Any]:
    root = Path(r"C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-")
    if not root.is_dir():
        root = Path.home() / "Multi-Element-Spectral-Intelligence-Engine-MESIE-"
    spec_ok = False
    version = None
    try:
        import importlib.util

        spec_ok = importlib.util.find_spec("mesie") is not None
        if spec_ok:
            from mesie.version_info import __version__ as mv  # type: ignore

            version = mv
    except Exception:
        spec_ok = (root / "mesie" / "sdk.py").is_file() or (root / "mesie" / "sdk").is_dir()
    return {
        "id": "mesie_sdk",
        "kind": "science_engine",
        "name": "MESIE Spectral Intelligence SDK",
        "status": "ready" if spec_ok else "missing",
        "path": str(root) if root.is_dir() else None,
        "version": version,
        "role": "Embed / match / fingerprint / generate — science substrate for Forge + Engine",
        "sovereign": True,
        "sdk": "itsnotai_internal.mesie_sdk",
        "note": "pip show mesie reports 0.2.0 wheel; runtime package is 1.2.0 editable",
    }


def _engine_cloud() -> Dict[str, Any]:
    root = _engine_root()
    present = (root / "sovereign_infrastructure" / "nextgen_systems").is_dir()
    dash = int(os.environ.get("SOVEREIGN_ENGINE_DASH_PORT") or "8090")
    api = int(os.environ.get("SOVEREIGN_ENGINE_API_PORT") or "8089")
    listening = _http_ok(f"http://127.0.0.1:{dash}/api/v1/overview") or _http_ok(
        f"http://127.0.0.1:{api}/health"
    )
    if listening:
        status = "listening"
    elif present:
        status = "ready"
    else:
        status = "missing"
    return {
        "id": "sovereign_engine",
        "kind": "monetization",
        "name": "Sovereign Engine",
        "status": status,
        "url": f"http://127.0.0.1:{dash}",
        "api": f"http://127.0.0.1:{api}",
        "path": str(root) if present else None,
        "role": "XFIN AURA PULSE MINT GRID NEXS · RevenueCat Shipaton",
        "sovereign": True,
        "sdk": "itsnotai_internal.engine_sdk",
    }


def doctrine() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.sovereign_stack.v1",
        "product": PRODUCT,
        "version": __version__,
        "tagline": TAGLINE,
        "pillars": [
            {
                "id": "remote_browser",
                "name": "Our remote browser",
                "must": "Beat theirs on every test and benchmark",
                "means": (
                    "Host-signed Edge + Fusion sense + optional Control + VComp + "
                    "evidence pack — not a rented third-party browser session that owns your logins."
                ),
                "win_condition": "Higher grounded actions, lower thrash, signed-in fidelity, measurable RTT",
            },
            {
                "id": "phone_iot",
                "name": "Phone + home IoT",
                "must": "Phone works and connects IoT around the home",
                "means": "Pair desk↔phone, LAN remote, HZ/BLE mesh, device registry, agent skills",
            },
            {
                "id": "remote",
                "name": "Remote access",
                "must": "Always on the roadmap — not optional",
                "means": "Named Cloudflare tunnel, LAN, seats, node pair, phone desk",
            },
            {
                "id": "our_cloud",
                "name": "Our computing cloud + models",
                "must": "Work stays in the sovereign perimeter",
                "means": (
                    "Host POCKET + our deploys/edge/Auro/NEXUS/mesh/Forge/MESIE/Engine are *our* cloud. "
                    "When jobs run here, prompts are not handed to a Connected-Apps vendor "
                    "as the product — they execute under our control. Vendor model APIs "
                    "are adapters we choose, not the identity of the stack."
                ),
            },
        ],
        "vs_theirs": {
            "their_remote_browser": "Vendor-hosted browser; they store login/session data",
            "our_remote_browser": "Your Edge profile + host eyes/control; custody on lab host",
            "their_cloud_models": "Their multi-tenant training/ops perimeter",
            "our_cloud_models": "Our host + our computing clouds (deploys, edge, Auro, NEXUS, Forge, MESIE, Engine)",
            "their_phone": "App talking to their cloud",
            "our_phone": "Remote desk + home IoT mesh into the lab host",
        },
    }


def computing_clouds(*, refresh: bool = False) -> Dict[str, Any]:
    """Inventory of *our* compute surfaces (what the lab already operates)."""
    global _CLOUDS_CACHE_AT, _CLOUDS_CACHE
    now = time.time()
    if not refresh and _CLOUDS_CACHE and (now - _CLOUDS_CACHE_AT) < _CLOUDS_TTL:
        return _CLOUDS_CACHE
    clouds: List[Dict[str, Any]] = []

    # 1. Host co-pilot (always)
    clouds.append(
        {
            "id": "host_pocket",
            "kind": "host",
            "name": "POCKET host",
            "status": "primary",
            "url": "http://127.0.0.1:8787",
            "role": "Agents, Fusion, remote browser, desk, phone API",
            "sovereign": True,
        }
    )

    # 2. Public remote (named tunnel)
    pub = _read_public_url()
    clouds.append(
        {
            "id": "edge_tunnel",
            "kind": "edge",
            "name": "Named Cloudflare tunnel",
            "status": "ready" if pub else "configure",
            "url": pub or None,
            "role": "Remote seats, phone away from LAN, public product URL",
            "sovereign": True,
            "ops": "cloudflared + ~/.pocket/cloudflare-named.env",
        }
    )

    # 3. Local deploys (platform deploys)
    try:
        from pocket.platform import list_deploys

        deps = list_deploys()
        running = [d for d in deps if d.get("status") == "running"]
        clouds.append(
            {
                "id": "local_deploys",
                "kind": "compute",
                "name": "Host deploys (static/npm/python)",
                "status": "ready",
                "running": len(running),
                "total": len(deps),
                "role": "Ship services on lab compute without leaving the desk",
                "sovereign": True,
            }
        )
    except Exception as e:
        clouds.append({"id": "local_deploys", "status": "error", "error": str(e)[:80]})

    # 4. Mesh vdisk / high-capacity
    try:
        from pocket.mesh_disk import MESH, VDISK

        clouds.append(
            {
                "id": "mesh_vdisk",
                "kind": "storage",
                "name": "Mesh vdisk",
                "status": "ready",
                "path": str(MESH),
                "vdisk": str(VDISK),
                "role": "Agent artifacts, transfers, large work off C:",
                "sovereign": True,
            }
        )
    except Exception as e:
        clouds.append({"id": "mesh_vdisk", "status": "error", "error": str(e)[:80]})

    # 5. Auro local model
    try:
        from pocket.auro14b_bridge import status as auro_status

        a = auro_status()
        clouds.append(
            {
                "id": "auro",
                "kind": "model",
                "name": "Auro14B (local)",
                "status": "ready" if a.get("ok") or a.get("available") else "optional",
                "detail": a,
                "role": "On-host model — prompts never leave for this path",
                "sovereign": True,
            }
        )
    except Exception:
        clouds.append(
            {
                "id": "auro",
                "kind": "model",
                "name": "Auro14B (local)",
                "status": "optional",
                "role": "Local model adapter when installed",
                "sovereign": True,
            }
        )

    # 6. NEXUS intelligence
    try:
        from pocket.nexus_bridge import nexus_available

        n = nexus_available()
        clouds.append(
            {
                "id": "nexus",
                "kind": "intelligence",
                "name": "NEXUS MERIDIAN",
                "status": "ready" if n.get("ok") else "offline",
                "role": "Lab intelligence MCP federation",
                "sovereign": True,
            }
        )
    except Exception:
        clouds.append({"id": "nexus", "kind": "intelligence", "status": "optional", "sovereign": True})

    # 7. Voice OSS + Fusion
    clouds.append(
        {
            "id": "voice_stack",
            "kind": "voice",
            "name": "Pocket Voice + Conversational Fusion",
            "status": "ready",
            "url": os.environ.get("POCKET_VOICE_URL") or "http://127.0.0.1:8790",
            "role": "Patient VAD · Fusion routing on host",
            "sovereign": True,
        }
    )

    # 8. HZ offline mesh (home/IoT adjacency)
    hz_root = Path.home() / "OneDrive" / "hz-offline"
    if not hz_root.is_dir():
        hz_root = Path(r"C:\Users\Medin\OneDrive\hz-offline")
    clouds.append(
        {
            "id": "hz_mesh",
            "kind": "iot_mesh",
            "name": "HZ offline mesh",
            "status": "ready" if hz_root.is_dir() else "missing",
            "path": str(hz_root) if hz_root.is_dir() else None,
            "role": "Phone BLE / offline mesh / home adjacency",
            "sovereign": True,
        }
    )

    # 9. SovereignForge OS — trading / MESIE / PARALLAX envelope
    # Never bind :8787 (Owner) or :8788 (Users). Forge default :8789.
    clouds.append(_forge_cloud())

    # 10. MESIE SDK (editable science engine)
    clouds.append(_mesie_cloud())

    # 11. Sovereign Engine (RevenueCat / Shipaton cores)
    clouds.append(_engine_cloud())

    payload = {
        "ok": True,
        "schema": "pocket.computing_clouds.v1",
        "doctrine": "These are OUR computing clouds — work here stays in the sovereign perimeter.",
        "count": len(clouds),
        "clouds": clouds,
        "public_url": pub or None,
    }
    _CLOUDS_CACHE = payload
    _CLOUDS_CACHE_AT = time.time()
    return payload


def stack_status() -> Dict[str, Any]:
    """One payload for desk/phone/agents."""
    clouds = computing_clouds()
    try:
        from pocket.remote_browser import status as rb_status

        rb = rb_status()
    except Exception as e:
        rb = {"ok": False, "error": str(e)[:120]}
    try:
        from pocket.iot_home import status as iot_status

        iot = iot_status()
    except Exception as e:
        iot = {"ok": False, "error": str(e)[:120]}

    return {
        "ok": True,
        "schema": "pocket.sovereign_stack.status.v1",
        "doctrine": doctrine(),
        "computing_clouds": clouds,
        "remote_browser": rb,
        "iot_home": iot,
        "remote": {
            "public_url": clouds.get("public_url"),
            "local": "http://127.0.0.1:8787",
            "phone": "/phone",
            "required": True,
        },
        "ts": time.time(),
    }
