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


def discover_tvs(timeout: float = 1.1) -> Dict[str, Any]:
    """SSDP on the LAN: smart TVs, renderers, Roku, Dial."""
    import socket

    found: Dict[str, Dict[str, Any]] = {}
    payloads = [
        "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n",
        "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: urn:dial-multiscreen-org:service:dial:1\r\n\r\n",
        "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: roku:ecp\r\n\r\n",
    ]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(max(0.4, min(timeout, 2.0)))
    try:
        for msg in payloads:
            try:
                sock.sendto(msg.encode("utf-8"), ("239.255.255.250", 1900))
            except Exception:
                continue
        deadline = time.time() + max(0.4, min(timeout, 2.0))
        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(4096)
            except Exception:
                break
            text = data.decode("utf-8", errors="ignore")
            ip = addr[0]
            st = ""
            loc = ""
            for line in text.splitlines():
                low = line.lower()
                if low.startswith("st:"):
                    st = line.split(":", 1)[-1].strip()
                if low.startswith("location:"):
                    loc = line.split(":", 1)[-1].strip()
            found[ip] = {
                "ip": ip,
                "st": st[:120],
                "location": loc[:240],
                "kind": "roku" if "roku" in (st + loc).lower() else ("tv" if "renderer" in (st + loc).lower() or "dial" in (st + loc).lower() else "upnp"),
            }
    finally:
        sock.close()
    rows = list(found.values())
    return {"ok": True, "tvs": rows, "count": len(rows), "note": "HDMI TVs also appear as extra Windows displays."}


VIEW_NODES = ROOT / "view_nodes.json"


def register_view_node(
    *,
    kind: str = "tv",
    label: str = "",
    ip: str = "",
    ua: str = "",
) -> Dict[str, Any]:
    """Wi-Fi TV / phone / glasses join as mesh view nodes. No HDMI."""
    kind = (kind or "tv").lower()
    if kind not in ("tv", "phone", "glasses", "pc"):
        kind = "tv"
    nid = f"{kind}-{(ip or 'lan').replace('.', '')[-8:] or 'x'}-{int(time.time()) % 100000}"
    rec = {
        "schema": "pocket.node.view.v1",
        "id": nid,
        "kind": kind,
        "label": (label or kind)[:80],
        "ip": (ip or "")[:64],
        "ua": (ua or "")[:160],
        "join": "/phoneai/tv",
        "stream": "/v1/phoneai/portal/ws",
        "seen": time.time(),
    }
    with _lock:
        rows = []
        if VIEW_NODES.is_file():
            try:
                rows = json.loads(VIEW_NODES.read_text(encoding="utf-8"))
            except Exception:
                rows = []
        if not isinstance(rows, list):
            rows = []
        key = f"{kind}|{ip}"
        rows = [r for r in rows if f"{r.get('kind')}|{r.get('ip')}" != key]
        rows.append(rec)
        cut = time.time() - 600
        rows = [r for r in rows if float(r.get("seen") or 0) > cut][-24:]
        ROOT.mkdir(parents=True, exist_ok=True)
        VIEW_NODES.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return {"ok": True, "node": rec, "nodes": rows}


def grab_tv_to_phone(node_id: str = "") -> Tuple[bytes, Dict[str, Any]]:
    """What a Wi-Fi TV node is showing: the laptop desktop stream, plus optional TV snapshot."""
    nodes = list_view_nodes().get("nodes") or []
    node = None
    if node_id:
        node = next((n for n in nodes if n.get("id") == node_id or n.get("ip") == node_id), None)
    if not node:
        node = next((n for n in nodes if n.get("kind") == "tv"), None)
    snap = None
    ip = (node or {}).get("ip") or ""
    if ip and ip not in ("127.0.0.1", "localhost"):
        for url in (
            f"http://{ip}:8080/snapshot",
            f"http://{ip}/live.jpg",
            f"http://{ip}:8001/api/v2/images/tv.jpg",
        ):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "PhoneAI-tv"})
                with urllib.request.urlopen(req, timeout=0.8) as r:
                    blob = r.read(500_000)
                if blob[:2] == b"\xff\xd8":
                    snap = blob
                    break
            except Exception:
                continue
    if snap:
        return snap, {"ok": True, "via": "tv-snapshot", "node": node, "ip": ip}
    from pocket.phoneai_portal import grab_jpeg, list_monitors

    mons = (list_monitors().get("monitors") or [])
    target = "tv" if len(mons) > 1 else "desktop"
    data, meta = grab_jpeg(target=target, max_w=1280, quality=68)
    meta = {
        **meta,
        "via": "tv-monitor" if target == "tv" else "tv-primary",
        "node": node,
        "note": "TV → phone. Second display if present; otherwise this PC. Phone taps control that screen.",
    }
    return data, meta


def list_view_nodes() -> Dict[str, Any]:
    rows = []
    if VIEW_NODES.is_file():
        try:
            rows = json.loads(VIEW_NODES.read_text(encoding="utf-8"))
        except Exception:
            rows = []
    if not isinstance(rows, list):
        rows = []
    cut = time.time() - 600
    live = [r for r in rows if float(r.get("seen") or 0) > cut]
    return {"ok": True, "schema": "pocket.node.view.v1", "nodes": live, "count": len(live)}


def snapshot() -> Dict[str, Any]:
    mons = {}
    try:
        from pocket.phoneai_portal import list_monitors

        mons = list_monitors()
    except Exception:
        mons = {"monitors": []}
    tvs = {"tvs": []}
    try:
        tvs = discover_tvs(0.8)
    except Exception:
        pass
    return {
        "ok": True,
        "product": "PhoneAI home mesh",
        "tv": {
            "url": "/phoneai/tv",
            "note": "Wi-Fi node. Open this URL on the TV browser — no HDMI. Laptop stream at laptop aspect.",
            "hdmi": False,
            "join": "/phoneai/tv",
            "nodes": list_view_nodes().get("nodes") or [],
            "lan": tvs.get("tvs") or [],
            "monitors": mons.get("monitors") or [],
        },
        "doorbell": {"url": "/phoneai/doorbell", "cameras": _load_cams()},
        "laptop_cam": {
            "request": "POST /v1/phoneai/cam/request",
            "approve": "/phoneai/cam/approve",
            "frame": "/v1/phoneai/cam/frame",
            **cameras()["laptop"],
        },
    }
