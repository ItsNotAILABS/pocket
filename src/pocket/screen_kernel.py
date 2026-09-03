"""Screen kernel — see, touch, type, click named buttons.

One contract for people (phone/glasses/TV) and agents (vLaptop).
Host implementation of the public vlaptop / screen-kernel protocol.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

SCHEMA = "pocket.screen.kernel.v1"
PROTOCOL = "SCREEN-KERNEL/1.0"


def see(*, which: str = "desktop", max_w: int = 960) -> Dict[str, Any]:
    from pocket.agent_eyes import see as eyes_see

    w = (which or "desktop").lower()
    if w in ("anti", "antigravity", "agy"):
        return eyes_see(which="anti")
    if w in ("tv", "hdmi", "monitor"):
        from pocket.home_mesh import grab_tv_to_phone
        import base64

        data, meta = grab_tv_to_phone()
        return {
            "ok": True,
            "eyes": True,
            "which": "tv",
            "bytes": len(data or b""),
            "via": meta.get("via"),
            "mime": "image/jpeg",
            "base64": base64.b64encode(data).decode("ascii")[:80_000] if data else "",
            "how": "TV framebuffer or second monitor → phone.",
        }
    return eyes_see(which="portal")


def cursor() -> Dict[str, Any]:
    from pocket.phoneai_portal import _cursor, primary_screen

    x, y = _cursor()
    ps = primary_screen()
    w = max(1, int(ps.get("w") or 1))
    h = max(1, int(ps.get("h") or 1))
    return {
        "ok": True,
        "x": x,
        "y": y,
        "nx": (x - int(ps.get("x") or 0)) / w,
        "ny": (y - int(ps.get("y") or 0)) / h,
        "screen": ps,
    }


def touch(
    kind: str = "tap",
    *,
    nx: float = 0.5,
    ny: float = 0.5,
    text: str = "",
    dx: float = 0.0,
    dy: float = 0.0,
    target: str = "desktop",
    hwnd: int = 0,
    button: str = "left",
) -> Dict[str, Any]:
    from pocket.phoneai_portal import touch as portal_touch

    return portal_touch(
        kind,
        nx=nx,
        ny=ny,
        text=text,
        dx=dx,
        dy=dy,
        target=target,
        hwnd=int(hwnd or 0),
        button=button,
    )


def type_into(
    text: str,
    *,
    nx: float = 0.5,
    ny: float = 0.5,
    target: str = "desktop",
    click_first: bool = True,
    submit: bool = False,
) -> Dict[str, Any]:
    """Click the selected field, then type. End-to-end caret → keys."""
    t0 = time.time()
    raw = text or ""
    typed = touch("type_field" if click_first else "key", nx=nx, ny=ny, text=raw, target=target)
    if submit:
        from pocket.phoneai_portal import touch as portal_touch

        portal_touch("key", nx=nx, ny=ny, vk=13, target=target)
    return {
        "ok": bool(typed.get("ok")),
        "schema": SCHEMA,
        "kind": "type_into",
        "chars": len(raw),
        "nx": nx,
        "ny": ny,
        "typed": typed,
        "ms": int((time.time() - t0) * 1000),
    }


def click_name(name: str) -> Dict[str, Any]:
    from pocket.ui_click import click_named_element

    return click_named_element(name)


def snapshot() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "product": "Screen kernel",
        "public": "https://github.com/ItsNotAILABS/vlaptop",
        "verbs": ["see", "touch", "type_into", "click_name", "cursor"],
        "http": [
            "GET /v1/screen/kernel",
            "POST /v1/screen/see",
            "POST /v1/screen/touch",
            "POST /v1/screen/type",
            "POST /v1/screen/click",
        ],
        "note": "People and agents share this. vLaptop is an agent's personal seat on the same kernel.",
    }
