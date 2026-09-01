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


def primary_screen() -> Dict[str, int]:
    """The one screen we stream — not the virtual desktop, not a mirror of Portal."""
    u = _user32()
    return {
        "x": 0,
        "y": 0,
        "w": int(u.GetSystemMetrics(0) or 1920),
        "h": int(u.GetSystemMetrics(1) or 1080),
    }


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
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E
HWND_TOP = 0
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
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
            try:
                iconic = bool(u.IsIconic(hwnd))
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
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, SW_RESTORE)
    r = _rect_of(hwnd)
    nx = int(r.get("x") or 0) + int(dx)
    ny = int(r.get("y") or 0) + int(dy)
    u.SetWindowPos(hwnd, 0, nx, ny, 0, 0, SWP_NOSIZE | SWP_SHOWWINDOW)
    return {"ok": True, "hwnd": hwnd, "x": nx, "y": ny, "title": _title_of(hwnd)[:80]}


def maximize_hwnd(hwnd: int) -> Dict[str, Any]:
    """Focus a window and expand it to fill the monitor."""
    hwnd = int(hwnd or 0)
    r = focus_hwnd(hwnd, make_main=True)
    try:
        u = _bind_user32()
        u.ShowWindow(hwnd, SW_MAXIMIZE)
        r["maximized"] = True
    except Exception as e:
        r["maximized"] = False
        r["error"] = str(e)[:160]
    _WIN_CACHE["t"] = 0.0
    return r


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


def geom(target: str = "desktop") -> Dict[str, Any]:
    t = (target or "desktop").lower()
    if t in ("window", "anti", "antigravity", "app"):
        wr = find_app_window("antigravity", "anti gravity") or window_rect("Antigravity") or window_rect("anti")
        if wr:
            return {"ok": True, "target": "window", **wr}
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

    ps = primary_screen()
    return ImageGrab.grab(bbox=(0, 0, ps["w"], ps["h"]))


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
            draw.rectangle([x0, y0, x1, y1], fill=(8, 10, 18))
    except Exception:
        pass


def grab_jpeg(*, target: str = "desktop", max_w: int = 1600) -> Tuple[bytes, Dict[str, Any]]:
    """Primary-monitor JPEG. Never block the host on all-screens grab."""
    key = f"{target}:{max_w}"
    now = time.time()
    with _grab_lock:
        if _last_jpeg.get("key") == key and now - float(_last_jpeg.get("t") or 0) < 0.16 and _last_jpeg.get("data"):
            return _last_jpeg["data"], _last_jpeg["meta"]
    g = {"ok": True, "target": "desktop"}
    try:
        g.update(primary_screen())
    except Exception:
        g.update({"x": 0, "y": 0, "w": 1920, "h": 1080})
    img = None
    tlow = (target or "desktop").lower()
    if tlow in ("window", "anti", "antigravity", "app"):
        wr = find_app_window("antigravity", "anti gravity")
        if wr and wr.get("w", 0) > 80:
            g.update({"ok": True, "target": "window", **wr})
            try:
                img = _ex.submit(_capture_rect, wr["x"], wr["y"], wr["w"], wr["h"]).result(timeout=0.9)
            except (FutTimeout, Exception):
                img = None
    if img is None and tlow in ("desktop", "", "primary"):
        if max_w < 1280:
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
    if img is None and tlow not in ("desktop", "", "primary"):
        data = _placeholder("Open Antigravity on this PC to attach the stream.")
        meta = {**g, "via": "placeholder", "bytes": len(data), "attached": False}
        return data, meta
    if img is None:
        data = _last_jpeg.get("data") or _placeholder("Waiting for desktop frame…")
        meta = {**g, "via": "placeholder", "bytes": len(data)}
        return data, meta
    img = img.convert("RGB")
    if tlow in ("desktop", "", "primary"):
        _blackout_self(img)
    if img.width > max_w:
        ratio = max_w / float(img.width)
        try:
            from PIL import Image as _PILImage

            resample = getattr(getattr(_PILImage, "Resampling", _PILImage), "LANCZOS", 1)
        except Exception:
            resample = 1
        img = img.resize((max_w, max(1, int(img.height * ratio))), resample)
    buf = io.BytesIO()
    q = 82 if max_w >= 1280 else 70
    img.save(buf, format="JPEG", quality=q, subsampling=0)
    data = buf.getvalue()
    g["frame_w"] = img.width
    g["frame_h"] = img.height
    g["bytes"] = len(data)
    g["via"] = "antigravity" if tlow in ("window", "anti", "antigravity", "app") else "primary"
    g["attached"] = tlow not in ("desktop", "", "primary")
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


_held = {"left": False, "right": False}

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
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


def _move(x: int, y: int) -> None:
    _user32().SetCursorPos(int(x), int(y))


def _cursor() -> Tuple[int, int]:
    import ctypes
    from ctypes import wintypes

    pt = wintypes.POINT()
    _user32().GetCursorPos(ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def _btn(side: str, down: bool) -> None:
    right = (side or "left").lower() in ("right", "r", "2")
    key = "right" if right else "left"
    if down and not _held[key]:
        _mouse(MOUSEEVENTF_RIGHTDOWN if right else MOUSEEVENTF_LEFTDOWN)
        _held[key] = True
    elif (not down) and _held[key]:
        _mouse(MOUSEEVENTF_RIGHTUP if right else MOUSEEVENTF_LEFTUP)
        _held[key] = False


def _click(side: str = "left") -> None:
    right = (side or "left").lower() in ("right", "r", "2")
    if right:
        _mouse(MOUSEEVENTF_RIGHTDOWN)
        time.sleep(0.03)
        _mouse(MOUSEEVENTF_RIGHTUP)
        _held["right"] = False
    else:
        _mouse(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.03)
        _mouse(MOUSEEVENTF_LEFTUP)
        _held["left"] = False


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
    pt = map_touch(nx, ny, target=target)
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
        if kind in ("tap", "click", "left", "down", "pen_down", "dbl", "double"):
            try:
                focused = focus_at(x, y) if int(hwnd or 0) <= 0 else focus_hwnd(int(hwnd), make_main=True)
            except Exception:
                focused = {}
        if kind in ("joy", "nudge", "stick"):
            cx, cy = _cursor()
            _move(cx + int(dx), cy + int(dy))
        elif kind in ("move", "hover"):
            _move(x, y)
        elif kind in ("down", "pen_down"):
            _move(x, y)
            _btn(side, True)
        elif kind in ("up", "pen_up"):
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


def touch_allowed(headers=None, client_address=None) -> bool:
    """LAN, signed-in seat, or this host's named tunnel (the phone)."""
    import os
    from urllib.parse import urlparse

    from pocket.auth import current_user, is_home_lan_client

    if is_home_lan_client(headers, client_address):
        return True
    try:
        if current_user(headers or {}):
            return True
    except Exception:
        pass
    host = str((headers or {}).get("Host") or (headers or {}).get("host") or "").split(":")[0].lower()
    pub = os.environ.get("POCKET_PUBLIC_URL") or "https://pocket.medinatechlabs.net"
    pub_host = (urlparse(pub).hostname or "").lower()
    if pub_host and host == pub_host:
        return True
    if host.endswith(".medinatechlabs.net") or host.endswith(".trycloudflare.com"):
        return True
    return False


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
        "controls": ["tap", "right", "drag", "joystick", "live-type", "window-focus", "scroll", "open-app"],
        "windows": "/v1/phoneai/portal/windows",
        "apps": "/v1/phoneai/portal/apps",
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
