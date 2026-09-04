"""Move HWNDs to another Windows virtual desktop via COM — no keyboard chords.

Uses IVirtualDesktopManagerInternal when the IID matches this build.
Fails closed (moved=0) instead of sending Win+Ctrl+D, which froze PhoneAI.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Build-specific IIDs (Win10 20H2 … Win11 24H2/25H2). First match wins.
_INTERNAL_IIDS = (
    "{53F5CA0B-85F1-4350-B8C4-E06267CDF8F0}",  # 22H2 / common 24H2
    "{A3175F2D-239C-4BD2-8AA0-EEBA8B6B91A2}",  # 23H2
    "{B2F925B9-5A0F-4D2E-9F4D-2B0E955A4E5F}",  # older 11
    "{F31574D6-B682-4CDC-BD31-2675C09C0DEC}",  # Win10
)
_CLSID_IMMERSIVE = "{C2F03A33-21F5-47FA-B4BB-156362A2F239}"
_IID_SERVICE_PROVIDER = "{6D5140C1-7436-11CE-8034-00AA006009FA}"
_CLSID_VDM = "{AA509086-5CA9-4C25-8F86-DEC3D5316495}"
_IID_VDM = "{A5CD92FF-29BE-454C-8D04-D82879FB3F1B}"


def move_hwnds_to_other_desktop(hwnds: List[int]) -> Dict[str, Any]:
    """Park windows on virtual desktop 2. Never synthesizes keyboard input."""
    clean = [int(h) for h in hwnds if int(h or 0) > 0]
    if not clean:
        return {"ok": True, "moved": 0, "parked": [], "via": "none"}
    try:
        r = _via_internal(clean)
        if r.get("moved") or r.get("via"):
            return r
    except Exception as e:
        return {"ok": False, "moved": 0, "parked": [], "via": "error", "error": str(e)[:200]}
    return {"ok": True, "moved": 0, "parked": [], "via": "unavailable", "note": "COM virtual-desktop API not on this build"}


def _via_internal(hwnds: List[int]) -> Dict[str, Any]:
    import ctypes
    from ctypes import POINTER, byref, c_uint, c_void_p, HRESULT

    ole32 = ctypes.windll.ole32
    ole32.CoInitialize(None)

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    def parse_guid(s: str) -> GUID:
        g = GUID()
        ole32.CLSIDFromString(ctypes.c_wchar_p(s), byref(g))
        return g

    CLSCTX = 23
    shell_clsid = parse_guid(_CLSID_IMMERSIVE)
    sp_iid = parse_guid(_IID_SERVICE_PROVIDER)
    shell = c_void_p()
    hr = ole32.CoCreateInstance(byref(shell_clsid), None, CLSCTX, byref(sp_iid), byref(shell))
    if hr != 0 or not shell.value:
        return {"ok": False, "moved": 0, "via": "immersive-fail"}

    class Vtbl(ctypes.Structure):
        _fields_ = [("fn", c_void_p * 24)]

    class Obj(ctypes.Structure):
        _fields_ = [("lpVtbl", POINTER(Vtbl))]

    # IServiceProvider::QueryService is vtable index 3
    QueryService = ctypes.WINFUNCTYPE(
        HRESULT, c_void_p, POINTER(GUID), POINTER(GUID), POINTER(c_void_p)
    )(ctypes.cast(shell, POINTER(Obj)).contents.lpVtbl.contents.fn[3])

    internal = c_void_p()
    used_iid = ""
    for iid_s in _INTERNAL_IIDS:
        iid = parse_guid(iid_s)
        internal = c_void_p()
        hr = QueryService(shell, byref(iid), byref(iid), byref(internal))
        if hr == 0 and internal.value:
            used_iid = iid_s
            break
    if not internal.value:
        return {"ok": False, "moved": 0, "via": "internal-iid-miss"}

    obj = ctypes.cast(internal, POINTER(Obj))
    # GetCount=3, MoveViewToDesktop varies; GetDesktops=4 on most builds
    GetCount = ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_uint))(obj.contents.lpVtbl.contents.fn[3])
    n = c_uint(0)
    if GetCount(internal, byref(n)) != 0:
        return {"ok": False, "moved": 0, "via": "getcount-fail", "iid": used_iid}

    # Documented manager can move if we already know a desktop GUID from a window
    # on another desktop. Create extra desktops is Internal-only and build-fragile,
    # so we only move when a second desktop already exists (count>=2).
    if int(n.value) < 2:
        return {
            "ok": True,
            "moved": 0,
            "via": "internal",
            "desktops": int(n.value),
            "note": "Only one virtual desktop — create Desktop 2 once (Win+Tab), then Vision will park there.",
        }

    mgr = c_void_p()
    vdm_clsid = parse_guid(_CLSID_VDM)
    vdm_iid = parse_guid(_IID_VDM)
    hr = ole32.CoCreateInstance(byref(vdm_clsid), None, CLSCTX, byref(vdm_iid), byref(mgr))
    if hr != 0 or not mgr.value:
        return {"ok": False, "moved": 0, "via": "vdm-fail", "desktops": int(n.value)}

    vdm = ctypes.cast(mgr, POINTER(Obj))
    GetWindowDesktopId = ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_void_p, POINTER(GUID))(
        vdm.contents.lpVtbl.contents.fn[4]
    )
    MoveWindowToDesktop = ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_void_p, POINTER(GUID))(
        vdm.contents.lpVtbl.contents.fn[5]
    )
    cur = GUID()
    if GetWindowDesktopId(mgr, hwnds[0], byref(cur)) != 0:
        return {"ok": False, "moved": 0, "via": "get-id-fail"}

    # Probe other top-level windows for a different desktop id (desktop 2).
    other = _find_other_desktop_guid(GetWindowDesktopId, mgr, cur, hwnds[0])
    if other is None:
        return {
            "ok": True,
            "moved": 0,
            "via": "internal",
            "desktops": int(n.value),
            "note": "Desktop 2 exists but no window on it yet to read its id.",
        }
    parked = []
    moved = 0
    for h in hwnds:
        if MoveWindowToDesktop(mgr, h, byref(other)) == 0:
            moved += 1
            parked.append({"hwnd": h, "ok": True})
    return {"ok": True, "moved": moved, "parked": parked, "via": "IVirtualDesktopManager", "desktops": int(n.value), "iid": used_iid}


def _find_other_desktop_guid(GetWindowDesktopId, mgr, cur, skip_hwnd: int):
    import ctypes
    from ctypes import POINTER, byref, wintypes

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    user32 = ctypes.windll.user32
    found = {}

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _lp):
        if int(hwnd) == int(skip_hwnd):
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        g = GUID()
        if GetWindowDesktopId(mgr, hwnd, byref(g)) != 0:
            return True
        if bytes(g) != bytes(cur):
            found["g"] = g
            return False
        return True

    user32.EnumWindows(cb, 0)
    return found.get("g")



