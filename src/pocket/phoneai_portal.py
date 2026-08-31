"""PhoneAI portal — stream the real PC and optionally touch it from the phone."""

from __future__ import annotations

import io
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from typing import Any, Dict, Optional, Tuple

_grab_lock = threading.Lock()
_last_jpeg: Dict[str, Any] = {"t": 0.0, "key": "", "data": b"", "meta": {}}
_ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="portal-grab")

# SM_XVIRTUALSCREEN … SM_CYVIRTUALSCREEN
_SM_X = 76
_SM_Y = 77
_SM_W = 78
_SM_H = 79


def _user32():
    import ctypes

    return ctypes.windll.user32


def virtual_screen() -> Dict[str, int]:
    u = _user32()
    return {
        "x": int(u.GetSystemMetrics(_SM_X)),
        "y": int(u.GetSystemMetrics(_SM_Y)),
        "w": int(u.GetSystemMetrics(_SM_W) or 1920),
        "h": int(u.GetSystemMetrics(_SM_H) or 1080),
    }


def window_rect(title_substr: str = "Antigravity") -> Optional[Dict[str, int]]:
    from pocket.screen_share import list_windows

    needle = (title_substr or "").lower()
    for w in list_windows(limit=60):
        title = (w.get("title") or "").lower()
        if needle and needle not in title:
            continue
        hwnd = int(w.get("hwnd") or 0)
        if hwnd <= 0:
            continue
        import ctypes
        from ctypes import wintypes

        rect = wintypes.RECT()
        if not _user32().GetWindowRect(hwnd, ctypes.byref(rect)):
            continue
        return {
            "hwnd": hwnd,
            "x": int(rect.left),
            "y": int(rect.top),
            "w": int(rect.right - rect.left),
            "h": int(rect.bottom - rect.top),
            "title": w.get("title") or "",
        }
    return None


def geom(target: str = "desktop") -> Dict[str, Any]:
    t = (target or "desktop").lower()
    if t in ("window", "anti", "antigravity", "app"):
        wr = window_rect("Antigravity") or window_rect("anti")
        if wr:
            return {"ok": True, "target": "window", **wr}
    vs = virtual_screen()
    return {"ok": True, "target": "desktop", "hwnd": 0, "title": "desktop", **vs}


def _placeholder(msg: str = "Portal") -> bytes:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (960, 540), (8, 10, 18))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, 920, 500], outline=(0, 255, 134), width=2)
    d.text((60, 240), msg[:80], fill=(244, 244, 245))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


def _capture_primary():
    from PIL import ImageGrab

    return ImageGrab.grab()


def grab_jpeg(*, target: str = "desktop", max_w: int = 960) -> Tuple[bytes, Dict[str, Any]]:
    """Primary-monitor JPEG. Never block the host on all-screens grab."""
    key = f"{target}:{max_w}"
    now = time.time()
    with _grab_lock:
        if _last_jpeg.get("key") == key and now - float(_last_jpeg.get("t") or 0) < 0.35 and _last_jpeg.get("data"):
            return _last_jpeg["data"], _last_jpeg["meta"]
    g = {"ok": True, "target": "desktop"}
    try:
        vs = virtual_screen()
        g.update(vs)
    except Exception:
        g.update({"x": 0, "y": 0, "w": 1920, "h": 1080})
    img = None
    try:
        from pocket.live_vision import FRAME_PATH, ensure_vision

        ensure_vision(interval=0.9)
        if FRAME_PATH.is_file() and time.time() - FRAME_PATH.stat().st_mtime < 3:
            data = FRAME_PATH.read_bytes()
            if len(data) > 800:
                meta = {**g, "via": "live_vision", "bytes": len(data)}
                with _grab_lock:
                    _last_jpeg.update({"t": now, "key": key, "data": data, "meta": meta})
                return data, meta
    except Exception:
        pass
    try:
        img = _ex.submit(_capture_primary).result(timeout=1.6)
    except (FutTimeout, Exception):
        img = None
    if img is None:
        data = _last_jpeg.get("data") or _placeholder("Waiting for desktop frame…")
        meta = {**g, "via": "placeholder", "bytes": len(data)}
        return data, meta
    img = img.convert("RGB")
    if img.width > max_w:
        ratio = max_w / float(img.width)
        img = img.resize((max_w, max(1, int(img.height * ratio))))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=55)
    data = buf.getvalue()
    g["frame_w"] = img.width
    g["frame_h"] = img.height
    g["bytes"] = len(data)
    g["via"] = "primary"
    with _grab_lock:
        _last_jpeg.update({"t": now, "key": key, "data": data, "meta": g})
    return data, g


def map_touch(nx: float, ny: float, *, target: str = "desktop") -> Dict[str, int]:
    nx = max(0.0, min(1.0, float(nx)))
    ny = max(0.0, min(1.0, float(ny)))
    g = geom(target)
    x = int(g["x"] + nx * g["w"])
    y = int(g["y"] + ny * g["h"])
    return {"x": x, "y": y, "target": g.get("target") or target, "hwnd": int(g.get("hwnd") or 0)}


def _mouse(flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> None:
    _user32().mouse_event(int(flags), int(dx), int(dy), int(data), 0)


def _move(x: int, y: int) -> None:
    _user32().SetCursorPos(int(x), int(y))


def touch(
    kind: str = "tap",
    *,
    nx: float = 0.5,
    ny: float = 0.5,
    dy: float = 0.0,
    text: str = "",
    target: str = "desktop",
) -> Dict[str, Any]:
    """Phone touch → real mouse/keyboard on this PC."""
    kind = (kind or "tap").lower().strip()
    pt = map_touch(nx, ny, target=target)
    x, y = pt["x"], pt["y"]
    t0 = time.time()
    try:
        if kind in ("move", "hover"):
            _move(x, y)
        elif kind in ("down", "pen_down"):
            _move(x, y)
            _mouse(0x0002)
        elif kind in ("up", "pen_up"):
            _move(x, y)
            _mouse(0x0004)
        elif kind in ("drag",):
            _move(x, y)
        elif kind in ("tap", "click"):
            _move(x, y)
            _mouse(0x0002)
            time.sleep(0.03)
            _mouse(0x0004)
        elif kind in ("dbl", "double"):
            _move(x, y)
            for _ in range(2):
                _mouse(0x0002)
                time.sleep(0.03)
                _mouse(0x0004)
                time.sleep(0.05)
        elif kind in ("right", "rclick"):
            _move(x, y)
            _mouse(0x0008)
            time.sleep(0.03)
            _mouse(0x0010)
        elif kind in ("scroll", "wheel"):
            _move(x, y)
            delta = int(-120 if dy >= 0 else 120)
            if abs(dy) > 0.08:
                delta = int(-120 * max(-4, min(4, round(dy * 6))))
            _mouse(0x0800, 0, 0, delta)
        elif kind in ("type", "text") and text:
            from pocket.ui_maneuver import type_text

            _move(x, y)
            type_text(text[:400])
        else:
            _move(x, y)
            _mouse(0x0002)
            time.sleep(0.03)
            _mouse(0x0004)
        return {"ok": True, "kind": kind, **pt, "ms": int((time.time() - t0) * 1000)}
    except Exception as e:
        return {"ok": False, "kind": kind, "error": str(e)[:200], **pt}


def snapshot() -> Dict[str, Any]:
    vs = virtual_screen()
    return {
        "ok": True,
        "portal": True,
        "product": "PhoneAI Portal",
        "grade": "production",
        "first_class": True,
        "separate_from": "antigravity",
        "modes": ["watch", "touch"],
        "targets": ["desktop"],
        "geom": {"ok": True, "target": "desktop", **vs},
        "watch": "/phoneai/portal",
        "frame": "/v1/phoneai/portal/frame",
        "touch": "POST /v1/phoneai/portal/touch",
        "policy": {
            "touch": "home LAN / loopback only",
            "frame_coalesce_ms": 300,
            "one_grab_at_a_time": True,
        },
        "note": "First-class PC stream. Antigravity remains its own desktop-app view at /phoneai/anti.",
    }
