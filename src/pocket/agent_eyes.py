"""Eyes for agents — live Portal and Antigravity frames as tools, not extra screens."""

from __future__ import annotations

import base64
from typing import Any, Dict


def see(*, which: str = "portal") -> Dict[str, Any]:
    """Give an agent a still of the primary screen or the Antigravity window."""
    from pocket.phoneai_portal import grab_jpeg, geom

    w = (which or "portal").lower()
    target = "antigravity" if w in ("anti", "antigravity", "agy") else "desktop"
    data, meta = grab_jpeg(target=target, max_w=720)
    g = geom(target)
    b64 = base64.b64encode(data).decode("ascii") if data else ""
    return {
        "ok": True,
        "eyes": True,
        "which": "antigravity" if target == "antigravity" else "portal",
        "attached": bool(g.get("hwnd")) if target == "antigravity" else True,
        "title": g.get("title") or target,
        "geom": {k: g.get(k) for k in ("x", "y", "w", "h", "hwnd")},
        "bytes": len(data or b""),
        "via": meta.get("via"),
        "url": "/v1/phoneai/anti/frame" if target == "antigravity" else "/v1/phoneai/portal/frame",
        "mime": "image/jpeg",
        "base64": b64[:80_000] if b64 else "",
        "how_agents": "Call eyes_see then eyes_touch with nx,ny in 0..1 on that frame.",
    }


def act(kind: str = "tap", *, which: str = "portal", nx: float = 0.5, ny: float = 0.5, text: str = "") -> Dict[str, Any]:
    w = (which or "portal").lower()
    if w in ("anti", "antigravity", "agy"):
        from pocket.antigravity_chat import anti_touch

        return anti_touch(kind, nx=nx, ny=ny, text=text)
    from pocket.phoneai_portal import touch as portal_touch

    return portal_touch(kind, nx=nx, ny=ny, text=text, target="desktop")


def catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "product": "agent eyes",
        "uses": [
            {"id": "eyes_see_portal", "which": "portal", "do": "Primary-screen JPEG for agents"},
            {"id": "eyes_see_anti", "which": "antigravity", "do": "Antigravity HWND JPEG"},
            {"id": "eyes_touch", "do": "nx,ny tap/drag/type on portal or anti window"},
        ],
        "see": "GET /v1/eyes?which=portal|anti",
        "touch": "POST /v1/eyes/touch",
    }
