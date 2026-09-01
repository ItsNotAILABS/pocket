"""Home mesh — TV on LAN, doorbell cameras, laptop webcam with phone approval."""

from __future__ import annotations

import io
import json
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / ".pocket" / "home"
CAMS = ROOT / "cameras.json"
APPROVE = ROOT / "cam_approval.json"
_lock = threading.Lock()
_last_cam: Dict[str, Any] = {"t": 0.0, "data": b""}


def _load_cams() -> List[Dict[str, Any]]:
    if CAMS.is_file():
        try:
            data = json.loads(CAMS.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return [
        {
            "id": "laptop",
            "name": "Laptop camera",
            "kind": "usb",
            "url": "",
            "note": "Needs phone request + PC Allow",
        }
    ]


def _save_cams(rows: List[Dict[str, Any]]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    CAMS.write_text(json.dumps(rows, indent=2)[:40_000], encoding="utf-8")


def _approve_state() -> Dict[str, Any]:
    if APPROVE.is_file():
        try:
            data = json.loads(APPROVE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"pending": False, "approved": False, "until": 0.0, "by": ""}


def _save_approve(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    APPROVE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cameras() -> Dict[str, Any]:
    rows = _load_cams()
    st = _approve_state()
    live = bool(st.get("approved") and time.time() < float(st.get("until") or 0))
    return {
        "ok": True,
        "cameras": rows,
        "laptop": {
            "pending": bool(st.get("pending")),
            "approved": live,
            "until": st.get("until") or 0,
            "approve_url": "/phoneai/cam/approve",
        },
        "tv": "/phoneai/tv",
        "doorbell": "/phoneai/doorbell",
    }


def add_camera(*, name: str, url: str, kind: str = "mjpeg") -> Dict[str, Any]:
    rows = _load_cams()
    cid = (name or "cam").lower().replace(" ", "-")[:32] or f"cam{int(time.time())}"
    rec = {"id": cid, "name": (name or cid)[:80], "kind": (kind or "mjpeg")[:16], "url": (url or "")[:400]}
    rows = [r for r in rows if r.get("id") != cid] + [rec]
    _save_cams(rows[-20:])
    return {"ok": True, "camera": rec, "cameras": rows[-20:]}


def request_laptop_cam(*, who: str = "phoneai") -> Dict[str, Any]:
    st = _approve_state()
    st.update({"pending": True, "approved": False, "until": 0.0, "by": who, "at": time.time()})
    _save_approve(st)
    return {
        "ok": True,
        "pending": True,
        "reply": "Waiting for this PC to tap Allow.",
        "approve": "/phoneai/cam/approve",
    }


def decide_laptop_cam(allow: bool, *, minutes: float = 10) -> Dict[str, Any]:
    st = _approve_state()
    if allow:
        st.update({"pending": False, "approved": True, "until": time.time() + max(1.0, minutes) * 60})
    else:
        st.update({"pending": False, "approved": False, "until": 0.0})
    _save_approve(st)
    return {"ok": True, "approved": bool(allow), "until": st.get("until"), "reply": "Laptop camera on." if allow else "Denied."}


def laptop_allowed() -> bool:
    st = _approve_state()
    return bool(st.get("approved") and time.time() < float(st.get("until") or 0))


def _placeholder(msg: str) -> bytes:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (960, 540), (12, 14, 22))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, 920, 500], outline=(0, 255, 134), width=2)
    d.text((60, 240), msg[:90], fill=(244, 244, 245))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


def grab_webcam() -> Tuple[bytes, Dict[str, Any]]:
    now = time.time()
    with _lock:
        if now - float(_last_cam.get("t") or 0) < 0.35 and _last_cam.get("data"):
            return _last_cam["data"], {"ok": True, "cached": True}
    data = b""
    via = "none"
    try:
        import cv2  # type: ignore

        cap = cv2.VideoCapture(0, getattr(cv2, "CAP_DSHOW", 0))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        ok, frame = cap.read()
        cap.release()
        if ok and frame is not None:
            from PIL import Image

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=55)
            data = buf.getvalue()
            via = "opencv"
    except Exception:
        data = b""
    if not data:
        data = _placeholder("Laptop camera — allow on the PC first")
        via = "placeholder"
    with _lock:
        _last_cam.update({"t": now, "data": data})
    return data, {"ok": True, "via": via, "bytes": len(data)}


def grab_doorbell(cam_id: str = "") -> Tuple[bytes, Dict[str, Any]]:
    rows = _load_cams()
    cam = None
    cid = (cam_id or "").strip()
    if cid:
        cam = next((c for c in rows if c.get("id") == cid), None)
    if not cam:
        cam = next((c for c in rows if c.get("kind") != "usb"), rows[0] if rows else None)
    if not cam:
        return _placeholder("Add a doorbell URL"), {"ok": False, "error": "no camera"}
    kind = (cam.get("kind") or "").lower()
    url = (cam.get("url") or "").strip()
    if kind in ("usb", "laptop") or not url:
        if not laptop_allowed():
            return _placeholder("Laptop cam needs Allow on the PC"), {"ok": False, "need_approval": True}
        return grab_webcam()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PhoneAI-doorbell"})
        with urllib.request.urlopen(req, timeout=2.5) as r:
            blob = r.read(400_000)
        if blob[:2] == b"\xff\xd8":
            return blob, {"ok": True, "via": "http-jpeg", "id": cam.get("id")}
        # maybe mjpeg — take first jpeg marker
        i = blob.find(b"\xff\xd8")
        j = blob.find(b"\xff\xd9", i + 2) if i >= 0 else -1
        if i >= 0 and j > i:
            return blob[i : j + 2], {"ok": True, "via": "mjpeg", "id": cam.get("id")}
    except Exception as e:
        return _placeholder(str(e)[:80]), {"ok": False, "error": str(e)[:160], "id": cam.get("id")}
    return _placeholder(cam.get("name") or "doorbell"), {"ok": False, "id": cam.get("id")}


def snapshot() -> Dict[str, Any]:
    return {
        "ok": True,
        "product": "PhoneAI home mesh",
        "tv": {"url": "/phoneai/tv", "note": "Same Wi-Fi. Stream + touch the PC on a TV browser."},
        "doorbell": {"url": "/phoneai/doorbell", "cameras": _load_cams()},
        "laptop_cam": {
            "request": "POST /v1/phoneai/cam/request",
            "approve": "/phoneai/cam/approve",
            "frame": "/v1/phoneai/cam/frame",
            **cameras()["laptop"],
        },
    }
