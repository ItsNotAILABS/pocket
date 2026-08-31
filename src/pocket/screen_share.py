"""Screen share + VComputer surface for all agents.

Modes:
  off     — agents do not receive host screen (default)
  view    — agents get live fusion frames + symbols (read-only eyes)
  control — view + mouse/keyboard through VComputer act (user-granted)

Users pick which screen (monitor index) and whether agents may control.
This is the policy layer behind the desk Screen column.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "screen_share"
ROOT.mkdir(parents=True, exist_ok=True)
STATE_PATH = ROOT / "state.json"

_state: Dict[str, Any] = {
    "mode": "off",  # off | view | control
    "monitor": 0,
    # target: "desktop" (all monitors) | "primary" | "monitor:N" | "window" + window_title/hwnd
    "target": "desktop",
    "window_title": "",
    "window_hwnd": 0,
    "label": "desktop",
    "agents_allowed": ["*"],  # * = all desk agents
    "vcomp": False,
    "updated_at": 0.0,
    "last_brief": "",
    "last_seq": 0,
}


def _load() -> None:
    global _state
    if STATE_PATH.exists():
        try:
            d = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                _state.update(d)
        except Exception:
            pass


def _save() -> None:
    _state["updated_at"] = time.time()
    try:
        STATE_PATH.write_text(json.dumps(_state, indent=2), encoding="utf-8")
    except Exception:
        pass


_load()


def _hwnd_alive(hwnd: int) -> bool:
    """True if top-level window handle is still a real usable window."""
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        h = int(hwnd or 0)
        if h <= 0:
            return False
        if not user32.IsWindow(h):
            return False
        # Cloaked / invisible UWP shells still IsWindow — require non-tiny rect
        rect = wintypes.RECT()
        if not user32.GetWindowRect(h, ctypes.byref(rect)):
            return False
        w = int(rect.right - rect.left)
        hh = int(rect.bottom - rect.top)
        if w < 80 or hh < 60:
            return False
        # Not visible and not minimized → treat as dead for sharing
        try:
            if not user32.IsWindowVisible(h) and not user32.IsIconic(h):
                return False
        except Exception:
            pass
        return True
    except Exception:
        return False


def heal_share_target(*, force_desktop: bool = False) -> Dict[str, Any]:
    """Reset stale window targets (e.g. closed reservation/OpenTable hwnd).

    Without this, Screen column stays on a dead window and frames look broken.
    """
    healed = False
    reason = ""
    target = str(_state.get("target") or "desktop").lower()
    hwnd = int(_state.get("window_hwnd") or 0)
    if force_desktop or target in ("window", "hwnd") or hwnd > 0:
        if force_desktop or (hwnd > 0 and not _hwnd_alive(hwnd)):
            _state["target"] = "desktop"
            _state["window_hwnd"] = 0
            _state["window_title"] = ""
            if not force_desktop and (_state.get("label") or "").lower() not in ("desktop", "primary", ""):
                # Keep human-readable note of recovery
                _state["label"] = "desktop"
            else:
                _state["label"] = "desktop"
            healed = True
            reason = "stale_window_hwnd" if not force_desktop else "force_desktop"
            _save()
            emit("screen", f"healed share target → desktop ({reason})", agent="OCULUS", role="host")
    return {"healed": healed, "reason": reason, "target": _state.get("target"), "mode": _state.get("mode")}


def status() -> Dict[str, Any]:
    # Auto-heal dead window targets so desk Screen column recovers without restart
    heal = heal_share_target()
    return {
        "ok": True,
        "schema": "pocket.screen_share.v1",
        "first_class": True,
        **{k: _state.get(k) for k in (
            "mode", "monitor", "target", "window_title", "window_hwnd",
            "label", "agents_allowed", "vcomp",
            "updated_at", "last_brief", "last_seq",
        )},
        "can_view": _state.get("mode") in ("view", "control"),
        "can_control": _state.get("mode") == "control",
        "healed": heal,
        "targets": list_targets(),
        "api": {
            "status": "GET /v1/screen",
            "set": "POST /v1/screen  {mode,monitor,target,window_title,vcomp}",
            "frame": "GET /v1/screen/frame",
            "context": "GET /v1/screen/context",
            "sense": "POST /v1/screen/sense",
            "act": "POST /v1/screen/act  (control mode only)",
        },
        "note": (
            "Pick target=desktop (all monitors) or a specific window so POCKET can stay "
            "open while agents watch another app. User must grant view/control. "
            "Stale window handles auto-heal to desktop."
        ),
    }


def list_targets() -> Dict[str, Any]:
    """Monitors + top-level windows the user can share (excluding tiny/tool windows)."""
    monitors: List[Dict[str, Any]] = [
        {"id": "desktop", "label": "All monitors (full desktop)", "kind": "desktop"},
        {"id": "primary", "label": "Primary monitor", "kind": "monitor", "index": 0},
    ]
    try:
        import ctypes

        user32 = ctypes.windll.user32
        vs_w = int(user32.GetSystemMetrics(78) or 0)
        vs_h = int(user32.GetSystemMetrics(79) or 0)
        if vs_w > 0:
            monitors.append(
                {
                    "id": "monitor:1",
                    "label": f"Secondary / virtual ({vs_w}×{vs_h})",
                    "kind": "monitor",
                    "index": 1,
                }
            )
    except Exception:
        pass
    windows: List[Dict[str, Any]] = []
    try:
        windows = list_windows(limit=40)
    except Exception:
        windows = []
    return {"monitors": monitors, "windows": windows}


def list_windows(*, limit: int = 40) -> List[Dict[str, Any]]:
    """Visible top-level windows (for sharing a non-POCKET app)."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    EnumWindows = user32.EnumWindows
    IsWindowVisible = user32.IsWindowVisible
    GetWindowTextW = user32.GetWindowTextW
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    GetWindowRect = user32.GetWindowRect
    GetClassNameW = user32.GetClassNameW

    results: List[Dict[str, Any]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def _cb(hwnd, _lp):
        if not IsWindowVisible(hwnd):
            return True
        n = GetWindowTextLengthW(hwnd)
        if n < 1:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        GetWindowTextW(hwnd, buf, n + 1)
        title = (buf.value or "").strip()
        if not title or len(title) < 2:
            return True
        # Skip our own overlays when possible
        low = title.lower()
        if low in ("program manager",):
            return True
        rect = wintypes.RECT()
        if not GetWindowRect(hwnd, ctypes.byref(rect)):
            return True
        w = int(rect.right - rect.left)
        h = int(rect.bottom - rect.top)
        if w < 120 or h < 80:
            return True
        cls = ctypes.create_unicode_buffer(128)
        GetClassNameW(hwnd, cls, 128)
        results.append(
            {
                "id": f"hwnd:{int(hwnd)}",
                "hwnd": int(hwnd),
                "title": title[:120],
                "class": (cls.value or "")[:60],
                "w": w,
                "h": h,
                "kind": "window",
                # Hint: POCKET Edge app titles often contain pocket/desk
                "is_pocket": ("pocket" in low and ("desk" in low or "edge" in low or "localhost" in low or "127.0.0.1" in low)),
            }
        )
        return len(results) < limit * 2

    EnumWindows(_cb, 0)
    # Prefer non-POCKET windows first so the picker is useful while desk is open
    results.sort(key=lambda x: (1 if x.get("is_pocket") else 0, -(x.get("w") or 0) * (x.get("h") or 0)))
    return results[:limit]


def set_share(
    *,
    mode: str = "",
    monitor: Optional[int] = None,
    label: str = "",
    vcomp: Optional[bool] = None,
    agents: Optional[List[str]] = None,
    target: str = "",
    window_title: str = "",
    window_hwnd: Optional[int] = None,
    reset_target: bool = False,
) -> Dict[str, Any]:
    m = (mode or _state.get("mode") or "off").lower().strip()
    if m not in ("off", "view", "control"):
        return {"ok": False, "error": f"mode must be off|view|control, got {mode}"}
    _state["mode"] = m
    # Turning share on without an explicit window → prefer healthy desktop
    if m in ("view", "control") and (reset_target or not target):
        hwnd = int(_state.get("window_hwnd") or 0)
        if reset_target or (hwnd > 0 and not _hwnd_alive(hwnd)) or str(_state.get("target") or "") == "window":
            if reset_target or (hwnd > 0 and not _hwnd_alive(hwnd)):
                heal_share_target(force_desktop=reset_target or True)
    if monitor is not None:
        _state["monitor"] = max(0, int(monitor))
    if target:
        t = str(target).strip().lower()
        _state["target"] = t
        if t.startswith("monitor:"):
            try:
                _state["monitor"] = int(t.split(":", 1)[1])
            except Exception:
                pass
        if t.startswith("hwnd:"):
            try:
                _state["window_hwnd"] = int(t.split(":", 1)[1])
                _state["target"] = "window"
            except Exception:
                pass
        if t in ("desktop", "all", "full"):
            _state["target"] = "desktop"
            _state["label"] = "desktop"
        if t in ("primary", "monitor:0"):
            _state["target"] = "primary"
            _state["monitor"] = 0
    if window_title:
        _state["window_title"] = str(window_title)[:120]
        _state["target"] = "window"
    if window_hwnd is not None:
        _state["window_hwnd"] = int(window_hwnd)
        if int(window_hwnd) > 0:
            _state["target"] = "window"
    if label:
        _state["label"] = str(label)[:80]
    elif _state.get("target") == "window" and _state.get("window_title"):
        _state["label"] = str(_state.get("window_title"))[:80]
    if vcomp is not None:
        _state["vcomp"] = bool(vcomp)
        if vcomp and m != "off":
            try:
                from pocket.virtual_computer import open_computer

                open_computer(label="screen-share")
            except Exception:
                pass
        if not vcomp and m == "off":
            try:
                from pocket.virtual_computer import close_computer

                close_computer()
            except Exception:
                pass
    if agents is not None:
        _state["agents_allowed"] = [str(a) for a in agents][:40] or ["*"]
    _save()
    emit(
        "screen",
        f"share mode={m} target={_state.get('target')} mon={_state['monitor']} vcomp={_state.get('vcomp')}",
        agent="OCULUS",
        role="host",
    )
    return status()

def agent_may_view(agent: str = "") -> bool:
    if _state.get("mode") not in ("view", "control"):
        return False
    allow = _state.get("agents_allowed") or ["*"]
    if "*" in allow:
        return True
    a = (agent or "").lower()
    return any(a == x.lower() or a.startswith(x.lower()) for x in allow)


def agent_may_control(agent: str = "") -> bool:
    return _state.get("mode") == "control" and agent_may_view(agent)


def _grab_window_image(hwnd: int = 0, title_substr: str = ""):
    """Capture a specific top-level window so POCKET can stay open on top."""
    import ctypes
    from ctypes import wintypes
    from PIL import ImageGrab

    user32 = ctypes.windll.user32
    hwnd = int(hwnd or 0)
    if hwnd <= 0 and title_substr:
        needle = title_substr.lower()
        for w in list_windows(limit=60):
            if needle in (w.get("title") or "").lower() and not w.get("is_pocket"):
                hwnd = int(w.get("hwnd") or 0)
                break
    if hwnd <= 0:
        return None, 0
    # Restore if minimized
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    except Exception:
        pass
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None, hwnd
    # Slight inset to avoid shadow borders
    x0, y0 = int(rect.left), int(rect.top)
    x1, y1 = int(rect.right), int(rect.bottom)
    if x1 - x0 < 40 or y1 - y0 < 40:
        return None, hwnd
    try:
        # all_screens=True required for multi-monitor window coords
        img = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        return img, hwnd
    except Exception:
        try:
            img = ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True)
            return img, hwnd
        except Exception:
            return None, hwnd


def grab_frame(*, include_image: bool = True) -> Dict[str, Any]:
    """Live frame for desktop / monitor / specific window (not only POCKET)."""
    mon = int(_state.get("monitor") or 0)
    target = str(_state.get("target") or "desktop").lower()
    try:
        from PIL import ImageGrab
        import base64
        import io

        img = None
        used = target

        # 1) Explicit window target — work in POCKET while watching another app
        if target in ("window", "hwnd") or int(_state.get("window_hwnd") or 0) > 0 or _state.get("window_title"):
            hwnd_try = int(_state.get("window_hwnd") or 0)
            if hwnd_try > 0 and not _hwnd_alive(hwnd_try):
                heal_share_target()
                target = "desktop"
                img = None
            else:
                img, hwnd_used = _grab_window_image(
                    hwnd_try,
                    str(_state.get("window_title") or ""),
                )
                if img is not None:
                    used = f"window:{hwnd_used}"
                    _state["window_hwnd"] = hwnd_used
                else:
                    # Dead/invisible window → fall back to full desktop so share never sticks broken
                    heal_share_target(force_desktop=True)
                    target = "desktop"
                    img = None

        # 2) Full virtual desktop (all monitors) — best default so POCKET isn't the only thing
        if img is None and target in ("desktop", "all", "full", "", "window"):
            try:
                import ctypes

                user32 = ctypes.windll.user32
                vs_x = user32.GetSystemMetrics(76)
                vs_y = user32.GetSystemMetrics(77)
                vs_w = user32.GetSystemMetrics(78)
                vs_h = user32.GetSystemMetrics(79)
                if vs_w > 0 and vs_h > 0:
                    img = ImageGrab.grab(
                        bbox=(vs_x, vs_y, vs_x + vs_w, vs_y + vs_h),
                        all_screens=True,
                    )
                    used = "desktop"
            except Exception:
                img = None

        # 3) Secondary / monitor index
        if img is None and (target.startswith("monitor") or mon > 0):
            try:
                import ctypes

                user32 = ctypes.windll.user32
                vs_x = user32.GetSystemMetrics(76)
                vs_y = user32.GetSystemMetrics(77)
                vs_w = user32.GetSystemMetrics(78)
                vs_h = user32.GetSystemMetrics(79)
                img = ImageGrab.grab(bbox=(vs_x, vs_y, vs_x + vs_w, vs_y + vs_h), all_screens=True)
                if img.width > 1600 and mon >= 1:
                    x0 = min(mon, 2) * (img.width // 2)
                    x1 = min(img.width, x0 + img.width // 2)
                    img = img.crop((x0, 0, x1, img.height))
                    used = f"monitor:{mon}"
            except Exception:
                img = None

        # 4) Primary only
        if img is None:
            try:
                img = ImageGrab.grab(all_screens=True)
                used = "all_screens"
            except Exception:
                img = ImageGrab.grab(all_screens=False)
                used = "primary"

        max_w = 1280
        if img.width > max_w:
            ratio = max_w / float(img.width)
            img = img.resize((max_w, int(img.height * ratio)))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=58)
        raw = buf.getvalue()
        b64 = base64.b64encode(raw).decode("ascii")
        # also refresh live_vision path for desk stream
        try:
            from pocket.live_vision import FRAME_PATH, META_PATH
            import time as _t

            FRAME_PATH.write_bytes(raw)
            META_PATH.write_text(
                f'{{"seq":{_state.get("last_seq",0)+1},"at":{_t.time()},'
                f'"bytes":{len(raw)},"w":{img.width},"h":{img.height},'
                f'"monitor":{mon},"target":"{used}"}}',
                encoding="utf-8",
            )
        except Exception:
            pass
        _state["last_seq"] = int(_state.get("last_seq") or 0) + 1
        out = {
            "ok": True,
            "mime": "image/jpeg",
            "base64": b64 if include_image else None,
            "width": img.width,
            "height": img.height,
            "monitor": mon,
            "target": used,
            "window_title": _state.get("window_title") or "",
            "seq": _state["last_seq"],
            "mode": _state.get("mode"),
        }
        if include_image:
            out["markdown"] = f"![screen](data:image/jpeg;base64,{b64})"
        return out
    except Exception as e:
        # fallback live_vision
        try:
            from pocket.live_vision import latest_frame

            return {**latest_frame(include_image=include_image), "fallback": "live_vision", "error": str(e)[:120]}
        except Exception as e2:
            return {"ok": False, "error": str(e2)}


def fusion_context(*, max_ui: int = 280, agent: str = "") -> Dict[str, Any]:
    """Fusion sense for agents when share is on — diffusion across modalities."""
    if not agent_may_view(agent):
        return {
            "ok": False,
            "shared": False,
            "mode": _state.get("mode"),
            "message": "Screen not shared with agents. User must enable View or Control in Screen column.",
        }
    try:
        from pocket.perception import sense, agent_context

        page = sense(max_ui=max_ui, force=True, include_image=False)
        ctx = agent_context(max_ui=max_ui)
        brief = page.get("brief") or ctx.get("brief") or ""
        _state["last_brief"] = str(brief)[:400]
        _save()
        # optional frame thumb
        frame = grab_frame(include_image=True)
        return {
            "ok": True,
            "shared": True,
            "mode": _state.get("mode"),
            "can_control": agent_may_control(agent),
            "brief": brief,
            "counts": page.get("counts") or ctx.get("counts"),
            "symbols_sample": [
                (s.get("text") or "")[:60]
                for s in (page.get("symbols") or [])[:24]
                if s.get("text")
            ],
            "action_hints": page.get("action_hints") or ctx.get("action_hints") or [],
            "page_text_head": (page.get("page_text") or "")[:1200],
            "frame": {
                "ok": frame.get("ok"),
                "seq": frame.get("seq"),
                "mime": frame.get("mime"),
                "base64": (frame.get("base64") or "")[:200] + "…" if frame.get("base64") else None,
                "markdown_len": len(frame.get("markdown") or ""),
            },
            "monitor": _state.get("monitor"),
            "vcomp": _state.get("vcomp"),
            "fusion": "uia+ocr+visual",
            "diffusion": "symbols→IR→remake available via POST /v1/fusion/remake",
        }
    except Exception as e:
        return {"ok": False, "shared": True, "error": str(e)[:200]}


def prompt_inject_block(*, agent: str = "", max_chars: int = 900) -> str:
    """Compact block for Codex/Grok/Claude when screen share is on."""
    if not agent_may_view(agent):
        return ""
    ctx = fusion_context(max_ui=200, agent=agent)
    if not ctx.get("ok"):
        return ""
    names = ", ".join(ctx.get("symbols_sample") or [])[:400]
    ctrl = "CONTROL granted (mouse/type via vcomp act)" if ctx.get("can_control") else "VIEW only (no mouse)"
    block = (
        f"[SCREEN SHARE · {ctrl} · monitor={ctx.get('monitor')}]\n"
        f"brief: {ctx.get('brief') or '—'}\n"
        f"ui: {names or '—'}\n"
        f"hints: {', '.join(str(h) for h in (ctx.get('action_hints') or [])[:5])}\n"
        f"policy: use fusion symbols; if CONTROL, act via vcomp click/type — do not invent UI.\n"
    )
    return block[:max_chars]


def act_for_agent(action: str, *, agent: str = "", **params) -> Dict[str, Any]:
    """Mouse/keyboard only when user enabled control mode."""
    if not agent_may_control(agent or "agent"):
        return {
            "ok": False,
            "error": "control denied — user must set Screen column to Control",
            "mode": _state.get("mode"),
        }
    from pocket.virtual_computer import act, open_computer

    if _state.get("vcomp") or True:
        try:
            open_computer(label="screen-control")
        except Exception:
            pass
    return act(action, **params)
