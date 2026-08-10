"""Lab hub — first-class readiness for Studio · Capsules · Life · IoT · Host.

Does not merge product tabs. Lab is a map + actions that open real surfaces.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List


def _ok_card(
    id: str,
    name: str,
    *,
    ok: bool,
    blurb: str,
    open_tab: str = "",
    href: str = "",
    skill: str = "",
    detail: Any = None,
    actions: List[Dict[str, str]] | None = None,
) -> Dict[str, Any]:
    return {
        "id": id,
        "name": name,
        "ok": ok,
        "status": "ready" if ok else "attention",
        "blurb": blurb,
        "open_tab": open_tab,
        "href": href,
        "skill": skill,
        "detail": detail,
        "actions": actions or [],
    }


def lab_status() -> Dict[str, Any]:
    """Single readiness payload for Lab UI + agents."""
    cards: List[Dict[str, Any]] = []
    t0 = time.time()

    # 1) Host / serve
    host_ok = True
    host_detail: Dict[str, Any] = {"service": "pocket"}
    try:
        from pocket import __version__, TAGLINE

        host_detail["version"] = __version__
        host_detail["tagline"] = TAGLINE
    except Exception as e:
        host_ok = False
        host_detail["error"] = str(e)[:120]
    cards.append(
        _ok_card(
            "host",
            "Host · always on",
            ok=host_ok,
            blurb="Desk + tunnel need python -m pocket serve running on this PC.",
            open_tab="platform",
            href="/desk",
            detail=host_detail,
            actions=[
                {"label": "Desk", "tab": "desk"},
                {"label": "Platform", "tab": "platform"},
            ],
        )
    )

    # 2) Product Studio
    studio_ok = False
    studio_detail: Dict[str, Any] = {}
    try:
        from pocket.studio_core import first_class_status

        studio_detail = first_class_status()
        studio_ok = bool(studio_detail.get("ready") or (studio_detail.get("video") or {}).get("ffmpeg"))
    except Exception as e:
        studio_detail = {"error": str(e)[:160]}
    cards.append(
        _ok_card(
            "studio",
            "Product Studio",
            ok=studio_ok,
            blurb="Record → storyboard → viral → ship. First-class agent skills.",
            open_tab="studio",
            href="/studio",
            skill="studio_map",
            detail={
                "ffmpeg": (studio_detail.get("video") or {}).get("ffmpeg"),
                "recordings": (studio_detail.get("video") or {}).get("recordings"),
                "exports": (studio_detail.get("video") or {}).get("exports"),
                "message": studio_detail.get("message"),
            },
            actions=[
                {"label": "Open Studio", "tab": "studio"},
                {"label": "Seat Studio agent", "agent": "studio"},
                {"label": "Ship pack", "api": "POST /v1/studio/ship"},
            ],
        )
    )

    # 3) Capsules
    cap_ok = True
    cap_detail: Dict[str, Any] = {}
    try:
        from pocket.protocols.multi_sandbox_capsule import status as capsule_status, probe_webgpu

        cap_detail = capsule_status()
        wg = probe_webgpu()
        cap_detail["webgpu"] = {
            "adapters": wg.get("adapters"),
            "enable_recommendation": wg.get("enable_recommendation"),
        }
        cap_ok = bool(cap_detail.get("ok", True))
    except Exception as e:
        cap_ok = False
        cap_detail = {"error": str(e)[:160]}
    cards.append(
        _ok_card(
            "capsules",
            "Multi-Sandbox Capsules",
            ok=cap_ok,
            blurb="Isolated HostWorker / WASI · WebGPU probe · OverlayFS commit.",
            open_tab="lab",
            href="/lab",
            skill="capsule_status",
            detail={
                "protocol": cap_detail.get("protocol"),
                "capsules": cap_detail.get("capsules"),
                "memory": cap_detail.get("memory"),
                "webgpu": cap_detail.get("webgpu"),
            },
            actions=[
                {"label": "Allocate 512MB", "api": "POST /v1/capsule/allocate"},
                {"label": "WebGPU probe", "skill": "webgpu_probe"},
            ],
        )
    )

    # 4) Life ops
    life_ok = True
    life_detail: Dict[str, Any] = {}
    try:
        from pocket.life_ops import life_skill_catalog

        cat = life_skill_catalog()
        life_detail = {"skills": len(cat), "ids": [c["id"] for c in cat[:8]]}
    except Exception as e:
        life_ok = False
        life_detail = {"error": str(e)[:120]}
    cards.append(
        _ok_card(
            "life",
            "Everyday life skills",
            ok=life_ok,
            blurb="Food · flights · shop · web · reserve — never auto-pay.",
            open_tab="working",
            href="/work",
            skill="life_catalog",
            detail=life_detail,
            actions=[
                {"label": "Working board", "tab": "working"},
                {"label": "Work Studio", "tab": "work"},
                {"label": "Seat Assist", "agent": "assist"},
            ],
        )
    )

    # 5) Phone + IoT
    phone_ok = True
    phone_detail: Dict[str, Any] = {}
    try:
        from pocket.phone_ui import phone_ready
        from pocket.iot_home import status as iot_status

        phone_detail["phone"] = phone_ready()
        phone_detail["iot"] = iot_status()
        phone_ok = bool(phone_detail["phone"].get("ok", True))
    except Exception as e:
        phone_ok = False
        phone_detail = {"error": str(e)[:160]}
    cards.append(
        _ok_card(
            "phone_iot",
            "Phone · pair · IoT",
            ok=phone_ok,
            blurb="PWA on tunnel · pair code · same-WiFi devices.",
            open_tab="phone",
            href="/phone",
            skill="phone_surface",
            detail={
                "remote": ((phone_detail.get("phone") or {}).get("urls") or {}).get("remote"),
                "lan": ((phone_detail.get("phone") or {}).get("urls") or {}).get("lan"),
                "iot_devices": len(((phone_detail.get("iot") or {}).get("devices") or [])),
            },
            actions=[
                {"label": "Phone", "tab": "phone"},
                {"label": "Pair + IoT", "workflow": "phone_iot"},
            ],
        )
    )

    ready_n = sum(1 for c in cards if c.get("ok"))
    return {
        "ok": True,
        "first_class": True,
        "schema": "pocket.lab.v1",
        "product": "POCKET Lab",
        "title": "Lab · build better tech",
        "doctrine": [
            "Lab maps readiness — it does not merge Desk / Studio / Phone into one UI",
            "Each card opens its own first-class tab or agent",
            "Host must stay running for tunnel + phone",
        ],
        "cards": cards,
        "ready": ready_n,
        "total": len(cards),
        "all_first_class": ready_n == len(cards),
        "flow": [
            "1. Keep host serve up (this machine)",
            "2. Studio agent: record → stop → ship in one intent",
            "3. Phone: pair then one-tap seat unlock",
            "4. Capsules: allocate / exec from Lab",
            "5. Life: Working board + Assist",
        ],
        "ms": int((time.time() - t0) * 1000),
        "ts": time.time(),
    }


def lab_brief(*, max_chars: int = 900) -> str:
    st = lab_status()
    lines = [
        "POCKET Lab (first-class map):",
        f"· Ready {st.get('ready')}/{st.get('total')} surfaces",
    ]
    for c in st.get("cards") or []:
        mark = "OK" if c.get("ok") else "!"
        lines.append(f"· [{mark}] {c.get('name')}: {c.get('blurb')}")
    lines.append("Open /lab or desk tab Lab — never merges product tabs.")
    return "\n".join(lines)[:max_chars]
