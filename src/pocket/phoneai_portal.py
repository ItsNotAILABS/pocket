"""PhoneAI portal — stream the real PC and optionally touch it from the phone."""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import secrets
import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

_grab_lock = threading.Lock()
_last_jpeg: Dict[str, Any] = {"t": 0.0, "key": "", "data": b"", "meta": {}}
_ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="portal-grab")
_grabbing = threading.Event()

# SM_XVIRTUALSCREEN … SM_CYVIRTUALSCREEN
_SM_X = 76
_SM_Y = 77
_SM_W = 78
_SM_H = 79


_DPI = False


def _dpi_aware() -> None:
    """Python defaults to DPI-unaware; SM_CXSCREEN then crops the right and bottom."""
    global _DPI
    if _DPI:
        return
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    _DPI = True


def _user32():
    import ctypes

    _dpi_aware()
    return ctypes.windll.user32


def virtual_screen() -> Dict[str, int]:
    u = _user32()
    return {
        "x": int(u.GetSystemMetrics(_SM_X)),
        "y": int(u.GetSystemMetrics(_SM_Y)),
        "w": int(u.GetSystemMetrics(_SM_W) or 1920),
        "h": int(u.GetSystemMetrics(_SM_H) or 1080),
    }


def primary_screen() -> Dict[str, int]:
    """Full primary display including the Windows taskbar (rcMonitor, not rcWork)."""
    u = _user32()
    try:
        import ctypes
        from ctypes import wintypes

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", ctypes.c_ulong),
            ]

        pt = wintypes.POINT(0, 0)
        hmon = u.MonitorFromPoint(pt, 1)  # MONITOR_DEFAULTTOPRIMARY
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        if hmon and u.GetMonitorInfoW(hmon, ctypes.byref(mi)):
            r = mi.rcMonitor
            return {
                "x": int(r.left),
                "y": int(r.top),
                "w": int(r.right - r.left),
                "h": int(r.bottom - r.top),
            }
    except Exception:
        pass
    return {
        "x": 0,
        "y": 0,
        "w": int(u.GetSystemMetrics(0) or 1920),
        "h": int(u.GetSystemMetrics(1) or 1080),
    }


def list_monitors() -> Dict[str, Any]:
    """Every attached display — HDMI/DisplayPort TVs show up as extra monitors."""
    rows: list = []
    try:
        import ctypes
        from ctypes import wintypes

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long),
            ]

        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_longlong
        )

        def _cb(hmon, hdc, lprect, lparam):
            r = lprect.contents
            i = len(rows)
            w = int(r.right - r.left)
            h = int(r.bottom - r.top)
            primary = int(r.left) == 0 and int(r.top) == 0
            rows.append(
                {
                    "id": i,
                    "x": int(r.left),
                    "y": int(r.top),
                    "w": w,
                    "h": h,
                    "primary": primary,
                    "label": "PC" if primary else f"Display {i + 1}",
                    "hint": "This PC" if primary else "Often the HDMI / smart TV",
                }
            )
            return 1

        _user32().EnumDisplayMonitors(0, 0, MonitorEnumProc(_cb), 0)
    except Exception:
        ps = primary_screen()
        rows = [{"id": 0, "primary": True, "label": "PC", "hint": "This PC", **ps}]
    if not rows:
        ps = primary_screen()
        rows = [{"id": 0, "primary": True, "label": "PC", "hint": "This PC", **ps}]
    return {"ok": True, "monitors": rows, "count": len(rows)}


def find_app_window(*needles: str) -> Optional[Dict[str, Any]]:
    from pocket.screen_share import list_windows

    wants = [n.lower() for n in (needles or ("antigravity",)) if n]
    for w in list_windows(limit=60):
        title = (w.get("title") or "").lower()
        if "portal" in title:
            continue
        if not any(n in title for n in wants):
            continue
        hwnd = int(w.get("hwnd") or 0)
        if hwnd <= 0:
            continue
        import ctypes
        from ctypes import wintypes

        rect = wintypes.RECT()
        if not _user32().GetWindowRect(hwnd, ctypes.byref(rect)):
            continue
        ww = int(rect.right - rect.left)
        hh = int(rect.bottom - rect.top)
        if ww < 80 or hh < 80:
            continue
        return {
            "hwnd": hwnd,
            "x": int(rect.left),
            "y": int(rect.top),
            "w": ww,
            "h": hh,
            "title": w.get("title") or "",
        }
    return None


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


GA_ROOT = 2
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E
WM_CLOSE = 0x0010
HWND_TOP = 0
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
_SKIP_FOCUS = ("portal · phoneai", "phoneai portal", "/phoneai/portal")


def _bind_user32():
    import ctypes
    from ctypes import wintypes

    u = _user32()
    if getattr(u, "_pocket_bound", False):
        return u
    u.WindowFromPoint.argtypes = [wintypes.POINT]
    u.WindowFromPoint.restype = wintypes.HWND
    u.GetAncestor.argtypes = [wintypes.HWND, ctypes.c_uint]
    u.GetAncestor.restype = wintypes.HWND
    u.GetForegroundWindow.restype = wintypes.HWND
    u.IsWindow.argtypes = [wintypes.HWND]
    u.IsWindow.restype = ctypes.c_bool
    u.IsIconic.argtypes = [wintypes.HWND]
    u.IsIconic.restype = ctypes.c_bool
    u.IsZoomed.argtypes = [wintypes.HWND]
    u.IsZoomed.restype = ctypes.c_bool
    u.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    u.SetForegroundWindow.argtypes = [wintypes.HWND]
    u.BringWindowToTop.argtypes = [wintypes.HWND]
    u.SetActiveWindow.argtypes = [wintypes.HWND]
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.GetWindowThreadProcessId.restype = wintypes.DWORD
    u.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, ctypes.c_bool]
    u.IsWindowVisible.argtypes = [wintypes.HWND]
    u.IsWindowVisible.restype = ctypes.c_bool
    u.PostMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, ctypes.c_size_t, ctypes.c_size_t]
    u._pocket_bound = True  # type: ignore[attr-defined]
    return u


def _title_of(hwnd: int) -> str:
    import ctypes

    u = _user32()
    n = int(u.GetWindowTextLengthW(hwnd) or 0)
    if n < 1:
        return ""
    buf = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(hwnd, buf, n + 1)
    return (buf.value or "").strip()


def _rect_of(hwnd: int) -> Dict[str, int]:
    import ctypes
    from ctypes import wintypes

    rect = wintypes.RECT()
    if not _user32().GetWindowRect(int(hwnd), ctypes.byref(rect)):
        return {"x": 0, "y": 0, "w": 0, "h": 0}
    return {
        "x": int(rect.left),
        "y": int(rect.top),
        "w": int(rect.right - rect.left),
        "h": int(rect.bottom - rect.top),
    }


def window_at(x: int, y: int) -> Optional[Dict[str, Any]]:
    """Top-level window under a desktop pixel (z-order, not just bounding boxes)."""
    import ctypes
    from ctypes import wintypes

    u = _bind_user32()
    pt = wintypes.POINT(int(x), int(y))
    hwnd = u.WindowFromPoint(pt)
    if not hwnd:
        return None
    root = int(u.GetAncestor(hwnd, GA_ROOT) or hwnd)
    if root <= 0 or not u.IsWindow(root):
        return None
    title = _title_of(root)
    if any(s in title.lower() for s in _SKIP_FOCUS):
        return None
    rec = {"hwnd": root, "title": title[:120], **_rect_of(root)}
    rec["child"] = int(hwnd)
    return rec


_WIN_CACHE: Dict[str, Any] = {"t": 0.0, "data": None}


def windows(*, limit: int = 40) -> Dict[str, Any]:
    """Open windows as phone tabs. Cached so the live JPEG is never starved."""
    now = time.time()
    hit = _WIN_CACHE.get("data")
    if isinstance(hit, dict) and now - float(_WIN_CACHE.get("t") or 0) < 1.8:
        return hit
    try:
        from pocket.screen_share import list_windows

        u = _bind_user32()
        fg = int(u.GetForegroundWindow() or 0)
        rows: list = []
        for w in list_windows(limit=max(int(limit), 8) * 2):
            hwnd = int(w.get("hwnd") or 0)
            title = (w.get("title") or "").strip()
            if hwnd <= 0 or len(title) < 2:
                continue
            if any(s in title.lower() for s in _SKIP_FOCUS):
                continue
            iconic = False
            zoomed = False
            try:
                iconic = bool(u.IsIconic(hwnd))
            except Exception:
                pass
            try:
                zoomed = bool(u.IsZoomed(hwnd))
            except Exception:
                pass
            r = _rect_of(hwnd)
            rows.append(
                {
                    "hwnd": hwnd,
                    "title": title[:80],
                    "focused": hwnd == fg,
                    "main": hwnd == fg,
                    "minimized": iconic,
                    "maximized": zoomed,
                    **r,
                }
            )
            if len(rows) >= limit:
                break
        rows.sort(key=lambda x: (0 if x.get("focused") else 1, 1 if x.get("minimized") else 0))
        data = {
            "ok": True,
            "focused": fg,
            "title": _title_of(fg)[:80] if fg else "",
            "windows": rows,
            "count": len(rows),
        }
    except Exception as e:
        data = {"ok": False, "windows": [], "count": 0, "error": str(e)[:200]}
    _WIN_CACHE["t"] = now
    _WIN_CACHE["data"] = data
    return data


def focus_hwnd(hwnd: int, *, make_main: bool = True) -> Dict[str, Any]:
    """Literally make this HWND the foreground / main window on the PC."""
    import ctypes
    from ctypes import wintypes

    u = _bind_user32()
    k32 = ctypes.windll.kernel32
    hwnd = int(hwnd or 0)
    if hwnd <= 0 or not u.IsWindow(hwnd):
        return {"ok": False, "error": "no window"}
    title = _title_of(hwnd)
    if any(s in title.lower() for s in _SKIP_FOCUS):
        return {"ok": False, "error": "skip portal viewer", "title": title}
    try:
        u.AllowSetForegroundWindow(-1)
    except Exception:
        pass
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, SW_RESTORE)
    fg = u.GetForegroundWindow()
    cur = int(k32.GetCurrentThreadId())
    pid = wintypes.DWORD(0)
    fg_tid = int(u.GetWindowThreadProcessId(fg, ctypes.byref(pid)) or 0)
    tgt_tid = int(u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid)) or 0)
    attached = []
    for tid in (fg_tid, tgt_tid):
        if tid and tid != cur:
            if u.AttachThreadInput(cur, tid, True):
                attached.append(tid)
    u.BringWindowToTop(hwnd)
    u.SetForegroundWindow(hwnd)
    try:
        u.SetActiveWindow(hwnd)
    except Exception:
        pass
    if make_main:
        u.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
    for tid in attached:
        u.AttachThreadInput(cur, tid, False)
    now = int(u.GetForegroundWindow() or 0)
    _WIN_CACHE["t"] = 0.0
    return {
        "ok": now == hwnd or now != 0,
        "hwnd": hwnd,
        "focused": now,
        "title": title[:80],
        "main": now == hwnd,
    }


def move_hwnd(hwnd: int, dx: int, dy: int) -> Dict[str, Any]:
    """Drag a desktop app window by pixel delta — double-tap then swipe."""
    u = _bind_user32()
    hwnd = int(hwnd or 0)
    if hwnd <= 0 or not u.IsWindow(hwnd):
        return {"ok": False, "error": "no window"}
    title = _title_of(hwnd)
    if any(s in title.lower() for s in _SKIP_FOCUS):
        return {"ok": False, "error": "skip portal viewer", "title": title}
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, SW_RESTORE)
    try:
        if u.IsZoomed(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
    except Exception:
        pass
    r = _rect_of(hwnd)
    nx = int(r.get("x") or 0) + int(dx)
    ny = int(r.get("y") or 0) + int(dy)
    u.SetWindowPos(hwnd, 0, nx, ny, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_SHOWWINDOW)
    now = _rect_of(hwnd)
    return {"ok": True, "hwnd": hwnd, "x": now.get("x", nx), "y": now.get("y", ny), "title": title[:80]}


def maximize_hwnd(hwnd: int) -> Dict[str, Any]:
    """Focus a window and expand it to fill the monitor (toggle if already max)."""
    hwnd = int(hwnd or 0)
    r = focus_hwnd(hwnd, make_main=True)
    try:
        u = _bind_user32()
        if u.IsZoomed(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
            r["maximized"] = False
            r["restored"] = True
        else:
            u.ShowWindow(hwnd, SW_MAXIMIZE)
            r["maximized"] = True
    except Exception as e:
        r["maximized"] = False
        r["error"] = str(e)[:160]
    _WIN_CACHE["t"] = 0.0
    return r


def minimize_hwnd(hwnd: int) -> Dict[str, Any]:
    u = _bind_user32()
    hwnd = int(hwnd or 0)
    if hwnd <= 0 or not u.IsWindow(hwnd):
        return {"ok": False, "error": "no window"}
    title = _title_of(hwnd)
    if any(s in title.lower() for s in _SKIP_FOCUS):
        return {"ok": False, "error": "skip portal viewer", "title": title}
    u.ShowWindow(hwnd, SW_MINIMIZE)
    _WIN_CACHE["t"] = 0.0
    return {"ok": True, "hwnd": hwnd, "minimized": True, "title": title[:80]}


def restore_hwnd(hwnd: int) -> Dict[str, Any]:
    hwnd = int(hwnd or 0)
    r = focus_hwnd(hwnd, make_main=True)
    try:
        u = _bind_user32()
        u.ShowWindow(hwnd, SW_RESTORE)
        r["restored"] = True
        r["maximized"] = False
        r["minimized"] = False
    except Exception as e:
        r["error"] = str(e)[:160]
    _WIN_CACHE["t"] = 0.0
    return r


def close_hwnd(hwnd: int) -> Dict[str, Any]:
    u = _bind_user32()
    hwnd = int(hwnd or 0)
    if hwnd <= 0 or not u.IsWindow(hwnd):
        return {"ok": False, "error": "no window"}
    title = _title_of(hwnd)
    if any(s in title.lower() for s in _SKIP_FOCUS):
        return {"ok": False, "error": "skip portal viewer", "title": title}
    try:
        u.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    except Exception as e:
        return {"ok": False, "error": str(e)[:160], "hwnd": hwnd, "title": title[:80]}
    _WIN_CACHE["t"] = 0.0
    return {"ok": True, "hwnd": hwnd, "closed": True, "title": title[:80]}


def _wheel_hwnd(hwnd: int, x: int, y: int, dy: float, dx: float = 0.0) -> None:
    """Scroll the given window: activate it, then wheel at that point."""
    import ctypes

    u = _bind_user32()
    hwnd = int(hwnd or 0)
    if hwnd > 0 and u.IsWindow(hwnd):
        try:
            if u.IsIconic(hwnd):
                u.ShowWindow(hwnd, SW_RESTORE)
            u.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def _pack_delta(amount: float) -> int:
        ticks = int(round(float(amount) * 8))
        if ticks == 0:
            ticks = 1 if float(amount) >= 0 else -1
        ticks = max(-8, min(8, ticks))
        delta = int(-120 * ticks)
        return ctypes.c_uint32((delta << 16) & 0xFFFFFFFF).value

    lparam = ctypes.c_uint32(((int(y) & 0xFFFF) << 16) | (int(x) & 0xFFFF)).value
    if hwnd > 0:
        try:
            if abs(float(dy) or 0) >= abs(float(dx) or 0):
                u.PostMessageW(hwnd, WM_MOUSEWHEEL, _pack_delta(dy), lparam)
            if abs(float(dx) or 0) > 0.02:
                u.PostMessageW(hwnd, WM_MOUSEHWHEEL, _pack_delta(dx), lparam)
        except Exception:
            pass
    _move(x, y)
    times = 1
    for _ in range(times):
        if abs(float(dx) or 0) > 0.02:
            hticks = int(round(float(dx) * 8)) or (1 if float(dx) > 0 else -1)
            _mouse(MOUSEEVENTF_HWHEEL, 0, 0, int(-120 * max(-8, min(8, hticks))))
        ticks = int(round(float(dy) * 8))
        if ticks == 0:
            ticks = 1 if float(dy) >= 0 else -1
        _mouse(MOUSEEVENTF_WHEEL, 0, 0, int(-120 * max(-8, min(8, ticks))))


def focus_at(x: int, y: int) -> Dict[str, Any]:
    hit = window_at(x, y)
    if not hit:
        return {"ok": False, "error": "no window at point"}
    return {**focus_hwnd(int(hit["hwnd"])), "hit": hit}


def geom(target: str = "desktop", hwnd: int = 0) -> Dict[str, Any]:
    t = (target or "desktop").lower()
    hid = int(hwnd or 0)
    if hid > 0 or t in ("focus", "window", "app", "mobile"):
        if hid <= 0:
            wr = find_app_window("antigravity", "anti gravity") or window_rect("Antigravity")
        else:
            r = _rect_of(hid)
            wr = {"hwnd": hid, "title": _title_of(hid), **r} if r.get("w", 0) > 40 else None
        if wr and int(wr.get("w") or 0) > 40:
            return {"ok": True, "target": "focus", **wr}
    if t in ("window", "anti", "antigravity", "app"):
        wr = find_app_window("antigravity", "anti gravity") or window_rect("Antigravity") or window_rect("anti")
        if wr:
            return {"ok": True, "target": "window", **wr}
    if t.startswith("monitor") or t in ("tv", "display", "hdmi", "screen"):
        mons = (list_monitors().get("monitors") or [])
        idx = 0
        try:
            idx = int(hwnd or 0)
        except Exception:
            idx = 0
        if t in ("tv", "hdmi") and len(mons) > 1:
            idx = next((m["id"] for m in mons if not m.get("primary")), mons[-1]["id"])
        if 0 <= idx < len(mons):
            m = mons[idx]
            return {"ok": True, "target": "monitor", "hwnd": 0, "title": m.get("label") or "display", **m}
    ps = primary_screen()
    return {"ok": True, "target": "desktop", "hwnd": 0, "title": "primary", **ps}


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

    _dpi_aware()
    ps = primary_screen()
    # Grab the full primary framebuffer (physical pixels after DPI awareness).
    return ImageGrab.grab(bbox=(int(ps["x"]), int(ps["y"]), int(ps["x"] + ps["w"]), int(ps["y"] + ps["h"])))


def _capture_rect(x: int, y: int, w: int, h: int):
    from PIL import ImageGrab

    return ImageGrab.grab(bbox=(int(x), int(y), int(x + w), int(y + h)))


_SKIP_TITLES = ("portal · phoneai", "phoneai portal", "/phoneai/portal")


def _blackout_self(img) -> None:
    """Paint over the Portal viewer so the stream cannot contain itself."""
    try:
        from PIL import ImageDraw
        from pocket.screen_share import list_windows

        draw = ImageDraw.Draw(img)
        pw, ph = img.size
        ps = primary_screen()
        sx = pw / float(ps["w"] or pw)
        sy = ph / float(ps["h"] or ph)
        for w in list_windows(limit=40):
            title = (w.get("title") or "").lower()
            if not any(s in title for s in _SKIP_TITLES):
                continue
            hwnd = int(w.get("hwnd") or 0)
            if hwnd <= 0:
                continue
            import ctypes
            from ctypes import wintypes

            rect = wintypes.RECT()
            if not _user32().GetWindowRect(hwnd, ctypes.byref(rect)):
                continue
            x0 = int((rect.left - ps["x"]) * sx)
            y0 = int((rect.top - ps["y"]) * sy)
            x1 = int((rect.right - ps["x"]) * sx)
            y1 = int((rect.bottom - ps["y"]) * sy)
            area = max(0, x1 - x0) * max(0, y1 - y0)
            # A maximized Portal tab would grey the whole laptop. Skip huge rects.
            if area > 0.18 * pw * ph:
                continue
            draw.rectangle([x0, y0, x1, y1], fill=(8, 10, 18))
    except Exception:
        pass


def grab_jpeg(*, target: str = "desktop", max_w: int = 1600, quality: int = 0, hwnd: int = 0) -> Tuple[bytes, Dict[str, Any]]:
    """Primary-monitor JPEG, or the focused window when hwnd/target=focus."""
    q = int(quality) if quality else (62 if max_w >= 1280 else 52)
    q = max(40, min(q, 80))
    key = f"{target}:{int(hwnd or 0)}:{max_w}:{q}"
    now = time.time()
    coalesce = 0.04 if max_w <= 1280 else 0.08
    with _grab_lock:
        if _last_jpeg.get("key") == key and now - float(_last_jpeg.get("t") or 0) < coalesce and _last_jpeg.get("data"):
            return _last_jpeg["data"], _last_jpeg["meta"]
    g = {"ok": True, "target": "desktop"}
    try:
        g.update(primary_screen())
    except Exception:
        g.update({"x": 0, "y": 0, "w": 1920, "h": 1080})
    img = None
    tlow = (target or "desktop").lower()
    hid = int(hwnd or 0)
    if hid > 0 or tlow in ("focus", "mobile"):
        g0 = geom("focus", hid)
        if int(g0.get("w") or 0) > 40:
            g.update({"ok": True, "target": "focus", **g0})
            try:
                img = _ex.submit(_capture_rect, g0["x"], g0["y"], g0["w"], g0["h"]).result(timeout=0.9)
            except (FutTimeout, Exception):
                img = None
    if img is None and tlow in ("window", "anti", "antigravity", "app"):
        wr = find_app_window("antigravity", "anti gravity")
        if wr and wr.get("w", 0) > 80:
            g.update({"ok": True, "target": "window", **wr})
            try:
                img = _ex.submit(_capture_rect, wr["x"], wr["y"], wr["w"], wr["h"]).result(timeout=0.9)
            except (FutTimeout, Exception):
                img = None
    if img is None and (tlow.startswith("monitor") or tlow in ("tv", "display", "hdmi", "screen")):
        g0 = geom(tlow, hid)
        if int(g0.get("w") or 0) > 40:
            g.update({"ok": True, "target": "monitor", **g0})
            try:
                img = _ex.submit(_capture_rect, g0["x"], g0["y"], g0["w"], g0["h"]).result(timeout=0.9)
            except (FutTimeout, Exception):
                img = None
    if img is None and tlow in ("desktop", "", "primary"):
        try:
            img = _ex.submit(_capture_primary).result(timeout=0.8)
        except (FutTimeout, Exception):
            img = None
    if img is None and tlow not in ("desktop", "", "primary"):
        data = _placeholder("Open Antigravity on this PC to attach the stream.")
        meta = {**g, "via": "placeholder", "bytes": len(data), "attached": False}
        return data, meta
    if img is None:
        prev = _last_jpeg.get("data") or b""
        if prev:
            meta = {**(_last_jpeg.get("meta") or {}), **g, "via": "hold", "bytes": len(prev)}
            return prev, meta
        data = _placeholder("Waiting for desktop frame…")
        meta = {**g, "via": "placeholder", "bytes": len(data)}
        return data, meta
    img = img.convert("RGB")
    if tlow in ("desktop", "", "primary") and (now - float(_last_jpeg.get("blackout_t") or 0) > 2.5):
        _blackout_self(img)
        _last_jpeg["blackout_t"] = now
    if img.width > max_w:
        ratio = max_w / float(img.width)
        try:
            from PIL import Image as _PILImage

            resample = getattr(getattr(_PILImage, "Resampling", _PILImage), "BILINEAR", 2)
        except Exception:
            resample = 2
        img = img.resize((max_w, max(1, int(img.height * ratio))), resample)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=q, subsampling=2, optimize=False)
    data = buf.getvalue()
    g["frame_w"] = img.width
    g["frame_h"] = img.height
    g["bytes"] = len(data)
    g["via"] = "antigravity" if tlow in ("window", "anti", "antigravity", "app") else "primary"
    g["attached"] = tlow not in ("desktop", "", "primary")
    with _grab_lock:
        _last_jpeg.update({"t": now, "key": key, "data": data, "meta": g})
    return data, g


def map_touch(nx: float, ny: float, *, target: str = "desktop", hwnd: int = 0) -> Dict[str, int]:
    """nx,ny are 0..1 of the pixels on the phone. Desktop stream = full laptop, not the last tab."""
    nx = max(0.0, min(1.0, float(nx)))
    ny = max(0.0, min(1.0, float(ny)))
    t = (target or "desktop").lower()
    hid = int(hwnd or 0)
    if t in ("desktop", "", "primary"):
        g = geom("desktop", hwnd=0)
        x = int(g["x"] + nx * g["w"])
        y = int(g["y"] + ny * g["h"])
        return {"x": x, "y": y, "target": "desktop", "hwnd": hid}
    g = geom(t, hwnd=hid)
    x = int(g["x"] + nx * g["w"])
    y = int(g["y"] + ny * g["h"])
    return {"x": x, "y": y, "target": g.get("target") or t, "hwnd": int(g.get("hwnd") or hid)}


_held = {"left": False, "right": False}

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_ESCAPE = 0x1B
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E


def _mouse(flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> None:
    _user32().mouse_event(int(flags), int(dx), int(dy), int(data), 0)


def _abs_xy(x: int, y: int) -> Tuple[int, int]:
    vs = virtual_screen()
    w = max(1, int(vs["w"]) - 1)
    h = max(1, int(vs["h"]) - 1)
    ax = int(round((int(x) - int(vs["x"])) * 65535 / w))
    ay = int(round((int(y) - int(vs["y"])) * 65535 / h))
    return max(0, min(65535, ax)), max(0, min(65535, ay))


def _send_mouse(flags: int, x: Optional[int] = None, y: Optional[int] = None, data: int = 0) -> bool:
    """Absolute SendInput so the hovered window sees the same pixel the phone shows."""
    try:
        import ctypes
        from ctypes import wintypes

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = (
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p),
            )

        class INPUT(ctypes.Structure):
            _fields_ = (("type", wintypes.DWORD), ("mi", MOUSEINPUT))

        fl = int(flags)
        dx = dy = 0
        if x is not None and y is not None:
            dx, dy = _abs_xy(int(x), int(y))
            fl |= MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK
        inp = INPUT(0, MOUSEINPUT(dx, dy, int(data), fl, 0, None))
        n = int(ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)) or 0)
        return n >= 1
    except Exception:
        return False


def _move(x: int, y: int) -> None:
    xi, yi = int(x), int(y)
    _user32().SetCursorPos(xi, yi)
    if not _send_mouse(MOUSEEVENTF_MOVE, xi, yi):
        _mouse(MOUSEEVENTF_MOVE)


def _cursor() -> Tuple[int, int]:
    import ctypes
    from ctypes import wintypes

    pt = wintypes.POINT()
    _user32().GetCursorPos(ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def _btn(side: str, down: bool) -> None:
    right = (side or "left").lower() in ("right", "r", "2")
    key = "right" if right else "left"
    flag_down = MOUSEEVENTF_RIGHTDOWN if right else MOUSEEVENTF_LEFTDOWN
    flag_up = MOUSEEVENTF_RIGHTUP if right else MOUSEEVENTF_LEFTUP
    if down and not _held[key]:
        if not _send_mouse(flag_down):
            _mouse(flag_down)
        _held[key] = True
    elif (not down) and _held[key]:
        if not _send_mouse(flag_up):
            _mouse(flag_up)
        _held[key] = False


def _click(side: str = "left") -> None:
    right = (side or "left").lower() in ("right", "r", "2")
    key = "right" if right else "left"
    down = MOUSEEVENTF_RIGHTDOWN if right else MOUSEEVENTF_LEFTDOWN
    up = MOUSEEVENTF_RIGHTUP if right else MOUSEEVENTF_LEFTUP
    if not _send_mouse(down):
        _mouse(down)
    if not _send_mouse(up):
        _mouse(up)
    _held[key] = False


def _vk(code: int, *, times: int = 1) -> None:
    u = _user32()
    n = max(1, min(int(times or 1), 40))
    for _ in range(n):
        u.keybd_event(int(code) & 0xFF, 0, 0, 0)
        u.keybd_event(int(code) & 0xFF, 0, 2, 0)


def _type_live(text: str) -> None:
    """Type onto the focused PC window."""
    raw = text or ""
    if not raw:
        return
    try:
        import ctypes
        from ctypes import wintypes

        u = _user32()

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = (
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p),
            )

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = (
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p),
            )

        class _INPUTunion(ctypes.Union):
            _fields_ = (("mi", MOUSEINPUT), ("ki", KEYBDINPUT))

        class INPUT(ctypes.Structure):
            _fields_ = (("type", wintypes.DWORD), ("union", _INPUTunion))

        KEYEVENTF_UNICODE = 0x0004
        KEYEVENTF_KEYUP = 0x0002
        for ch in raw[:80]:
            if ch in ("\n", "\r"):
                _vk(VK_RETURN)
                continue
            if ch == "\b":
                _vk(VK_BACK)
                continue
            if ch == "\t":
                _vk(VK_TAB)
                continue
            code = ord(ch)
            down = INPUT()
            down.type = 1
            down.union.ki = KEYBDINPUT(0, code, KEYEVENTF_UNICODE, 0, None)
            up = INPUT()
            up.type = 1
            up.union.ki = KEYBDINPUT(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)
            arr = (INPUT * 2)(down, up)
            nsent = int(u.SendInput(2, ctypes.byref(arr), ctypes.sizeof(INPUT)) or 0)
            if nsent < 1:
                scan = int(u.VkKeyScanW(code) & 0xFF)
                if scan and scan != 0xFF:
                    _vk(scan)
    except Exception:
        from pocket.ui_maneuver import type_text

        type_text(raw, use_clipboard=len(raw) > 2)


def touch(
    kind: str = "tap",
    *,
    nx: float = 0.5,
    ny: float = 0.5,
    dy: float = 0.0,
    dx: float = 0.0,
    text: str = "",
    target: str = "desktop",
    button: str = "left",
    vk: int = 0,
    n: int = 1,
    hwnd: int = 0,
) -> Dict[str, Any]:
    """Phone touch → real mouse/keyboard on this PC.

    Phone zoom is view-only (CSS on the handset). These events always hit
    the unzoomed desktop at nx,ny in 0..1 of the primary screen / window.
    Tap/focus makes that window the literal foreground (main) window.
    """
    kind = (kind or "tap").lower().strip()
    side = (button or "left").lower()
    pt = map_touch(nx, ny, target=target, hwnd=int(hwnd or 0))
    x, y = pt["x"], pt["y"]
    t0 = time.time()
    focused: Dict[str, Any] = {}
    try:
        if kind in ("focus", "main", "foreground", "activate"):
            if int(hwnd or 0) > 0:
                focused = focus_hwnd(int(hwnd), make_main=True)
            else:
                focused = focus_at(x, y)
            return {"ok": bool(focused.get("ok")), "kind": kind, **pt, "focus": focused, "hwnd": focused.get("hwnd") or hwnd, "ms": int((time.time() - t0) * 1000)}
        if kind in ("move_window", "drag_window"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            g = primary_screen()
            px = int(float(dx) * float(g.get("w") or 1920))
            py = int(float(dy) * float(g.get("h") or 1080))
            moved = move_hwnd(hid, px, py) if hid else {"ok": False, "error": "no window"}
            return {"ok": bool(moved.get("ok")), "kind": kind, **pt, "hwnd": hid, "moved": moved, "ms": int((time.time() - t0) * 1000)}
        if kind in ("maximize", "full", "expand", "fullscreen"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            focused = maximize_hwnd(hid) if hid else {"ok": False, "error": "no window"}
            return {
                "ok": bool(focused.get("ok")),
                "kind": kind,
                **pt,
                "focus": focused,
                "hwnd": hid,
                "maximized": bool(focused.get("maximized")),
                "ms": int((time.time() - t0) * 1000),
            }
        if kind in ("minimize", "min", "iconify"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            focused = minimize_hwnd(hid) if hid else {"ok": False, "error": "no window"}
            return {"ok": bool(focused.get("ok")), "kind": kind, **pt, "focus": focused, "hwnd": hid, "ms": int((time.time() - t0) * 1000)}
        if kind in ("restore", "unmax"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            focused = restore_hwnd(hid) if hid else {"ok": False, "error": "no window"}
            return {"ok": bool(focused.get("ok")), "kind": kind, **pt, "focus": focused, "hwnd": hid, "ms": int((time.time() - t0) * 1000)}
        if kind in ("close", "quit_window"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            focused = close_hwnd(hid) if hid else {"ok": False, "error": "no window"}
            return {"ok": bool(focused.get("ok")), "kind": kind, **pt, "focus": focused, "hwnd": hid, "ms": int((time.time() - t0) * 1000)}
        if kind in ("joy", "nudge", "stick"):
            cx, cy = _cursor()
            _move(cx + int(dx), cy + int(dy))
        elif kind in ("move", "hover"):
            _move(x, y)
        elif kind in ("down", "pen_down", "hold", "press"):
            _move(x, y)
            _btn(side, True)
        elif kind in ("up", "pen_up", "release"):
            _move(x, y)
            _btn(side, False)
        elif kind in ("drag",):
            _move(x, y)
            if not _held["left"] and not _held["right"]:
                _btn(side, True)
        elif kind in ("tap", "click", "left"):
            _move(x, y)
            _click("left")
        elif kind in ("dbl", "double"):
            _move(x, y)
            _click("left")
            time.sleep(0.05)
            _click("left")
        elif kind in ("right", "rclick"):
            _move(x, y)
            _click("right")
        elif kind in ("scroll", "wheel"):
            hid = int(hwnd or 0)
            if hid <= 0:
                hit = window_at(x, y) or {}
                hid = int(hit.get("hwnd") or 0)
            _wheel_hwnd(hid, x, y, float(dy or 0), float(dx or 0))
            pt["hwnd"] = hid
        elif kind in ("open", "launch", "app"):
            from pocket.desktop import open_app

            aid = (text or "").strip() or (button if button not in ("left", "right") else "")
            launched = open_app(aid)
            time.sleep(0.35)
            focused = {}
            try:
                from pocket.ui_maneuver import focus_window_title

                focused = focus_window_title(str(launched.get("label") or aid)[:40])
            except Exception:
                pass
            return {
                "ok": bool(launched.get("ok")),
                "kind": kind,
                "app": aid,
                "launched": launched,
                "focus": focused,
                **pt,
                "ms": int((time.time() - t0) * 1000),
            }
        elif kind in ("key", "keys"):
            code = int(vk or 0)
            if code:
                _vk(code, times=n)
            elif text:
                _type_live(text)
        elif kind in ("type", "text") and text:
            _type_live(text[:400])
        else:
            _move(x, y)
            _click("left")
        out = {"ok": True, "kind": kind, "held": dict(_held), **pt, "ms": int((time.time() - t0) * 1000)}
        if focused:
            out["focus"] = focused
        return out
    except Exception as e:
        return {"ok": False, "kind": kind, "error": str(e)[:200], **pt}


_TOKEN_TTL = 60 * 60 * 2
_TOKEN_REG = Path.home() / ".pocket" / "portal_tokens.json"
_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _portal_secret() -> bytes:
    p = Path.home() / ".pocket" / "portal.key"
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.is_file():
        return p.read_bytes()[:64] or b"pocket-portal"
    raw = os.urandom(32)
    p.write_bytes(raw)
    try:
        os.chmod(p, 0o600)
    except Exception:
        pass
    return raw


def mint_portal_token(principal: str = "") -> str:
    """Bind a short-lived Portal capability to a principal. Never mint for anonymous."""
    who = (principal or "").strip()[:80]
    if not who:
        raise ValueError("portal token requires a principal")
    ts = str(int(time.time()))
    nonce = secrets.token_hex(8)
    msg = f"{ts}.{who}.{nonce}".encode("utf-8")
    sig = hmac.new(_portal_secret(), msg, hashlib.sha256).hexdigest()[:32]
    tok = f"{ts}.{who}.{nonce}.{sig}"
    try:
        reg = {}
        if _TOKEN_REG.is_file():
            reg = json.loads(_TOKEN_REG.read_text(encoding="utf-8"))
        live = reg.get("live") or {}
        live[tok[-40:]] = {"principal": who, "at": time.time(), "revoked": False}
        cut = time.time() - _TOKEN_TTL
        live = {k: v for k, v in live.items() if float(v.get("at") or 0) > cut and not v.get("revoked")}
        _TOKEN_REG.parent.mkdir(parents=True, exist_ok=True)
        _TOKEN_REG.write_text(json.dumps({"live": live}, indent=2), encoding="utf-8")
    except Exception:
        pass
    return tok


def check_portal_token(token: str) -> bool:
    raw = (token or "").strip()
    parts = raw.split(".")
    # Legacy timestamp-only tokens (ts.sig) never confer authority.
    if len(parts) != 4:
        return False
    ts, who, nonce, sig = parts
    try:
        age = time.time() - int(ts)
    except Exception:
        return False
    if age < 0 or age > _TOKEN_TTL or not who:
        return False
    expect = hmac.new(_portal_secret(), f"{ts}.{who}.{nonce}".encode("utf-8"), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(expect, sig[:32]):
        return False
    try:
        if _TOKEN_REG.is_file():
            live = (json.loads(_TOKEN_REG.read_text(encoding="utf-8")).get("live") or {})
            rec = live.get(raw[-40:])
            if rec and rec.get("revoked"):
                return False
    except Exception:
        pass
    return True


def portal_cookie(token: str, *, secure: bool = False) -> str:
    parts = [
        f"pocket_portal={token}",
        "Path=/",
        f"Max-Age={_TOKEN_TTL}",
        "HttpOnly",
        "SameSite=Lax",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def token_from_headers(headers=None, query: Optional[Dict[str, Any]] = None) -> str:
    headers = headers or {}
    h = headers.get("X-Pocket-Portal") or headers.get("x-pocket-portal") or ""
    if h:
        return str(h).strip()
    cookie = headers.get("Cookie") or headers.get("cookie") or ""
    for part in cookie.split(";"):
        k, _, v = part.strip().partition("=")
        if k == "pocket_portal":
            return v.strip()
    if query:
        return str((query.get("pt") or query.get("token") or [""])[0] if isinstance(query.get("pt"), list) else (query.get("pt") or query.get("token") or ""))
    return ""


def origin_ok(headers=None, client_address=None) -> bool:
    """Same-origin or LAN. Hostname suffix is not authority."""
    headers = headers or {}
    origin = (headers.get("Origin") or headers.get("origin") or "").strip()
    if not origin:
        from pocket.auth import is_home_lan_client

        return is_home_lan_client(headers, client_address)
    host = str(headers.get("Host") or headers.get("host") or "").split(":")[0].lower()
    oh = (urlparse(origin).hostname or "").lower()
    if not oh:
        return False
    if host and oh == host:
        return True
    if oh in ("127.0.0.1", "localhost") or oh.startswith("192.168.") or oh.startswith("10."):
        return True
    return False


def touch_allowed(headers=None, client_address=None, query: Optional[Dict[str, Any]] = None) -> bool:
    """LAN, signed-in seat, or a minted portal session — not the open internet."""
    from pocket.auth import current_user, is_home_lan_client

    if is_home_lan_client(headers, client_address):
        return True
    try:
        if current_user(headers or {}):
            return True
    except Exception:
        pass
    tok = token_from_headers(headers, query)
    if tok and check_portal_token(tok):
        return True
    return False


def ws_accept_key(key: str) -> str:
    digest = hashlib.sha1((key.strip() + _WS_GUID).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def _ws_send(sock, payload: bytes, opcode: int = 1) -> None:
    n = len(payload)
    hdr = bytes([0x80 | (opcode & 0x0F)])
    if n < 126:
        hdr += bytes([n])
    elif n < 65536:
        hdr += bytes([126]) + struct.pack("!H", n)
    else:
        hdr += bytes([127]) + struct.pack("!Q", n)
    sock.sendall(hdr + payload)


def _ws_recv_frame(sock, stash: Optional[list] = None) -> Optional[Tuple[int, bytes]]:
    """Read one frame. Timeout mid-header leaves bytes in stash instead of desyncing."""
    if stash is None:
        stash = [b""]

    def need(n: int) -> bytes:
        while len(stash[0]) < n:
            chunk = sock.recv(n - len(stash[0]))
            if not chunk:
                raise ConnectionError("closed")
            stash[0] += chunk
        out = stash[0][:n]
        stash[0] = stash[0][n:]
        return out

    try:
        hdr = need(2)
        opcode = hdr[0] & 0x0F
        masked = bool(hdr[1] & 0x80)
        n = hdr[1] & 0x7F
        if n == 126:
            ext = need(2)
            n = struct.unpack("!H", ext)[0]
        elif n == 127:
            ext = need(8)
            n = struct.unpack("!Q", ext)[0]
        if n > 2_000_000:
            return None
        mask = need(4) if masked else b""
        data = need(n) if n else b""
        if masked and mask:
            data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        return opcode, data
    except TimeoutError:
        return (0xFE, b"")  # pending — try again, stash keeps partial bytes
    except (ConnectionError, OSError):
        return None


def _kick_grab(target: str, max_w: int, quality: int, hwnd: int = 0) -> None:
    if _grabbing.is_set():
        return
    _grabbing.set()

    def _run() -> None:
        try:
            grab_jpeg(target=target, max_w=max_w, quality=quality, hwnd=hwnd)
        except Exception:
            pass
        finally:
            _grabbing.clear()

    threading.Thread(target=_run, name="portal-ws-grab", daemon=True).start()


def peek_jpeg(*, target: str = "desktop", max_w: int = 1280, quality: int = 72, hwnd: int = 0) -> Optional[Tuple[bytes, Dict[str, Any]]]:
    key = f"{target}:{int(hwnd or 0)}:{int(max_w)}:{int(quality)}"
    with _grab_lock:
        data = _last_jpeg.get("data") or b""
        meta = dict(_last_jpeg.get("meta") or {})
        age = time.time() - float(_last_jpeg.get("t") or 0)
        have = bool(data) and _last_jpeg.get("key") == key
    if age > 0.06 or not have:
        _kick_grab(target, max_w, quality, hwnd)
    if have:
        return data, meta
    if data and age < 0.45:
        return data, meta
    return None


def run_portal_ws(sock, headers=None, client_address=None) -> None:
    """One connection: binary JPEGs out, JSON touch in. No HTTP round-trip per move."""
    sock.settimeout(0.02)
    cfg = {"max_w": 1600, "q": 74, "target": "desktop", "fps": 16.0, "hwnd": 0}
    last = 0.0
    stash: list = [b""]
    hello = json.dumps({"ok": True, "kind": "hello", "ws": True, "spatial": True}).encode("utf-8")
    try:
        _ws_send(sock, hello, 1)
    except Exception:
        return
    _kick_grab("desktop", 1280, 72)
    while True:
        now = time.time()
        interval = 1.0 / max(4.0, min(float(cfg["fps"]), 20.0))
        if now - last >= interval:
            peeked = peek_jpeg(
                target=str(cfg.get("target") or "desktop"),
                max_w=int(cfg.get("max_w") or 1280),
                quality=int(cfg.get("q") or 72),
                hwnd=int(cfg.get("hwnd") or 0),
            )
            if peeked:
                try:
                    _ws_send(sock, peeked[0], 2)
                    last = now
                except Exception:
                    break
        try:
            frame = _ws_recv_frame(sock, stash)
        except TimeoutError:
            continue
        except OSError:
            break
        if frame is None:
            break
        opcode, payload = frame
        if opcode == 0xFE:
            continue
        if opcode == 8:
            break
        if opcode == 9:
            try:
                _ws_send(sock, payload, 10)
            except Exception:
                break
            continue
        if opcode != 1:
            continue
        try:
            msg = json.loads(payload.decode("utf-8"))
        except Exception:
            continue
        if not isinstance(msg, dict):
            continue
        if not touch_allowed(headers, client_address):
            try:
                _ws_send(sock, json.dumps({"ok": False, "error": "reauth"}).encode("utf-8"), 1)
            except Exception:
                break
            continue
        from pocket.ratelimit import hit as rl_hit

        ok_rl, _reason = rl_hit("portal_ws_msg", str((client_address or ("?", 0))[0]), kind="portal_touch")
        if not ok_rl:
            continue
        kind = str(msg.get("kind") or "")
        if kind in ("cfg", "config", "net"):
            if msg.get("max_w"):
                cfg["max_w"] = max(640, min(int(msg["max_w"]), 1920))
            if msg.get("target"):
                cfg["target"] = str(msg.get("target") or "desktop")
            if msg.get("hwnd") is not None:
                cfg["hwnd"] = int(msg.get("hwnd") or 0)
            if msg.get("q") or msg.get("quality"):
                cfg["q"] = max(40, min(int(msg.get("q") or msg.get("quality")), 90))
            if msg.get("fps"):
                cfg["fps"] = float(msg["fps"])
            continue
        if kind in ("ping", "hello"):
            continue
        try:
            touch(
                kind,
                nx=float(msg.get("nx") if msg.get("nx") is not None else 0.5),
                ny=float(msg.get("ny") if msg.get("ny") is not None else 0.5),
                dy=float(msg.get("dy") or 0),
                dx=float(msg.get("dx") or 0),
                text=str(msg.get("text") or msg.get("app") or ""),
                target=str(msg.get("target") or cfg.get("target") or "desktop"),
                button=str(msg.get("button") or "left"),
                vk=int(msg.get("vk") or 0),
                n=int(msg.get("n") or 1),
                hwnd=int(msg.get("hwnd") or 0),
            )
        except Exception:
            continue


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
        "phone_zoom": "view-only — PC zoom never changes",
        "controls": ["tap", "hold", "right", "drag", "joystick", "live-type", "window-focus", "scroll", "open-app", "minimize", "maximize", "close"],
        "windows": "/v1/phoneai/portal/windows",
        "apps": "/v1/phoneai/portal/apps",
        "targets": ["desktop"],
        "geom": {"ok": True, "target": "desktop", **vs},
        "watch": "/phoneai/portal",
        "frame": "/v1/phoneai/portal/frame",
        "touch": "POST /v1/phoneai/portal/touch",
        "policy": {
            "touch": "LAN, signed-in, or portal session cookie",
            "frame": "same gate as touch — no anonymous JPEG",
            "frame_coalesce_ms": 80,
            "one_grab_at_a_time": True,
            "live": "WebSocket /v1/phoneai/portal/ws",
        },
        "note": "First-class PC stream. Antigravity remains its own desktop-app view at /phoneai/anti.",
    }
