"""Home IoT + phone mesh — phone must work and connect devices on the same Wi‑Fi.

Surfaces:
  · POCKET phone pair (desk codes) + LAN presence
  · Node peers / tray
  · HZ offline mesh (BLE / offline chat adjacency)
  · Device registry (lights, plugs, hubs — extensible)
  · Same-WiFi LAN discovery (ARP + port probe + SSDP-lite)
  · Device control (toggle state; HTTP ping when address known)

Agents use skills: iot_status, iot_list, iot_pair_phone, iot_hz_status, iot_discover
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path.home() / ".pocket" / "iot"
ROOT.mkdir(parents=True, exist_ok=True)
REGISTRY = ROOT / "devices.json"
_lock = Lock()

HZ_CANDIDATES = [
    Path.home() / "OneDrive" / "hz-offline",
    Path(r"C:\Users\Medin\OneDrive\hz-offline"),
    Path(os.environ.get("HZ_ROOT") or ""),
]

# Common home / IoT / cast ports on same Wi‑Fi
_PROBE_PORTS = (80, 443, 8080, 8443, 8008, 8009, 1883, 5000, 8123, 6052, 554)


def _load_devices() -> List[Dict[str, Any]]:
    try:
        if REGISTRY.is_file():
            data = json.loads(REGISTRY.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return list(data.get("devices") or [])
    except Exception:
        pass
    return []


def _save_devices(devices: List[Dict[str, Any]]) -> None:
    REGISTRY.write_text(json.dumps({"devices": devices, "updated_at": time.time()}, indent=2), encoding="utf-8")


def hz_root() -> Optional[Path]:
    for p in HZ_CANDIDATES:
        if p and p.is_dir() and (p / "src" / "hz").is_dir():
            return p
    return None


def hz_status() -> Dict[str, Any]:
    root = hz_root()
    if not root:
        return {
            "ok": False,
            "status": "missing",
            "hint": "Install/clone hz-offline next to lab stack for BLE/mesh",
        }
    return {
        "ok": True,
        "status": "ready",
        "path": str(root),
        "docs": str(root / "docs" / "PHONE_MCP.md"),
        "suite": "python -m hz  (from hz-offline)",
        "role": "Phone BLE dual-role · offline mesh · home adjacency",
    }


def register_device(
    *,
    name: str,
    kind: str = "generic",
    address: str = "",
    room: str = "",
    protocol: str = "lan",
    meta: Optional[Dict[str, Any]] = None,
    state: str = "unknown",
    reachable: Optional[bool] = None,
) -> Dict[str, Any]:
    name = (name or "").strip()
    if not name:
        return {"ok": False, "error": "name required"}
    with _lock:
        devices = _load_devices()
        # upsert by name or address
        addr = (address or "").strip()
        kept: List[Dict[str, Any]] = []
        existing: Optional[Dict[str, Any]] = None
        for d in devices:
            same_name = (d.get("name") or "").lower() == name.lower()
            same_addr = addr and (d.get("address") or "") == addr
            if same_name or same_addr:
                existing = d
            else:
                kept.append(d)
        rec = dict(existing or {})
        rec.update(
            {
                "id": rec.get("id") or f"iot_{int(time.time())}_{len(kept)}",
                "name": name[:80],
                "kind": (kind or rec.get("kind") or "generic")[:40],
                "address": addr[:120] if addr else (rec.get("address") or ""),
                "room": (room or rec.get("room") or "")[:40],
                "protocol": (protocol or rec.get("protocol") or "lan")[:32],
                "meta": {**(rec.get("meta") or {}), **(meta or {})},
                "state": state or rec.get("state") or "unknown",
                "created_at": rec.get("created_at") or time.time(),
                "last_seen": time.time(),
            }
        )
        if reachable is not None:
            rec["reachable"] = bool(reachable)
        kept.append(rec)
        _save_devices(kept[-200:])
    return {"ok": True, "device": rec, "updated": bool(existing)}


def list_devices() -> Dict[str, Any]:
    devices = _load_devices()
    # Sort: phones & reachable first
    devices = sorted(
        devices,
        key=lambda d: (
            0 if d.get("kind") == "phone" else 1,
            0 if d.get("reachable") else 1,
            (d.get("room") or ""),
            (d.get("name") or ""),
        ),
    )
    return {"ok": True, "count": len(devices), "devices": devices}


def remove_device(device_id: str = "", name: str = "") -> Dict[str, Any]:
    with _lock:
        devices = _load_devices()
        before = len(devices)
        if device_id:
            devices = [d for d in devices if d.get("id") != device_id]
        elif name:
            devices = [d for d in devices if (d.get("name") or "").lower() != name.lower()]
        _save_devices(devices)
    return {"ok": True, "removed": before - len(devices), "count": len(devices)}


def _host_lan_ip() -> str:
    try:
        from pocket.live import lan_ip

        return lan_ip()
    except Exception:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


def _subnet_prefix(ip: str) -> str:
    parts = (ip or "").split(".")
    if len(parts) == 4:
        return ".".join(parts[:3])
    return "192.168.1"


def _arp_neighbors() -> List[Dict[str, str]]:
    """Windows/Linux ARP table → same-LAN hosts."""
    out: List[Dict[str, str]] = []
    try:
        r = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=8,
            encoding="utf-8",
            errors="replace",
        )
        text = (r.stdout or "") + "\n" + (r.stderr or "")
        for m in re.finditer(
            r"(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F]{2}(?:[-:][0-9a-fA-F]{2}){5})",
            text,
        ):
            ip, mac = m.group(1), m.group(2).replace("-", ":").lower()
            if ip.endswith(".255") or ip.endswith(".0"):
                continue
            out.append({"ip": ip, "mac": mac})
    except Exception:
        pass
    # dedupe
    seen: Set[str] = set()
    uniq = []
    for h in out:
        if h["ip"] in seen:
            continue
        seen.add(h["ip"])
        uniq.append(h)
    return uniq


def _probe_host(ip: str, ports: Tuple[int, ...] = _PROBE_PORTS, timeout: float = 0.35) -> Dict[str, Any]:
    open_ports: List[int] = []
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
            s.close()
        except Exception:
            pass
        if len(open_ports) >= 4:
            break
    return {"ip": ip, "open_ports": open_ports, "reachable": bool(open_ports)}


def _guess_kind(ports: List[int], name: str = "") -> str:
    low = (name or "").lower()
    if "phone" in low:
        return "phone"
    if 8123 in ports:
        return "hub"  # Home Assistant
    if 1883 in ports:
        return "hub"  # MQTT
    if 8008 in ports or 8009 in ports:
        return "cast"
    if 554 in ports:
        return "camera"
    if 80 in ports or 443 in ports or 8080 in ports:
        return "lan_device"
    return "lan_host"


def discover_lan(*, deep: bool = False, register: bool = True) -> Dict[str, Any]:
    """Discover devices on the same Wi‑Fi/LAN as the desk host.

    Uses ARP neighbors (fast) + optional limited subnet port probe.
    Registers/updates the IoT registry so phone and desk share the same items.
    """
    t0 = time.time()
    host_ip = _host_lan_ip()
    prefix = _subnet_prefix(host_ip)
    neighbors = _arp_neighbors()
    # Prefer same /24 as host
    same_subnet = [n for n in neighbors if n["ip"].startswith(prefix + ".")]
    others = [n for n in neighbors if n not in same_subnet]
    targets = same_subnet + others
    # Always include host itself
    if not any(n["ip"] == host_ip for n in targets):
        targets.insert(0, {"ip": host_ip, "mac": "local"})

    # Optional deep: probe a handful of .1 gateway and sequential neighbors
    if deep:
        for last in (1, 2, 50, 100, 101, 150, 200, 254):
            ip = f"{prefix}.{last}"
            if not any(t["ip"] == ip for t in targets):
                targets.append({"ip": ip, "mac": ""})

    found: List[Dict[str, Any]] = []
    # Cap concurrent probes so we stay snappy (prefer ARP-known hosts)
    probe_list = targets[:36]

    def work(item: Dict[str, str]) -> Dict[str, Any]:
        ip = item["ip"]
        # Lighter probe: fewer ports for speed; deep scan uses full set
        ports = _PROBE_PORTS if deep else (80, 443, 8080, 8123, 8008, 1883)
        pr = _probe_host(ip, ports=ports, timeout=0.28 if not deep else 0.35)
        pr["mac"] = item.get("mac") or ""
        return pr

    with ThreadPoolExecutor(max_workers=20) as pool:
        futs = {pool.submit(work, t): t for t in probe_list}
        for fut in as_completed(futs):
            try:
                pr = fut.result()
            except Exception:
                continue
            if not pr.get("reachable") and pr.get("ip") != host_ip:
                # Keep ARP-only hosts as offline-known neighbors
                if not pr.get("mac"):
                    continue
            ip = pr["ip"]
            ports = pr.get("open_ports") or []
            is_host = ip == host_ip
            name = "POCKET desk" if is_host else f"LAN {ip}"
            kind = "desk" if is_host else _guess_kind(ports)
            rec = {
                "name": name,
                "kind": kind,
                "address": ip,
                "room": "network",
                "protocol": "lan",
                "reachable": bool(pr.get("reachable") or is_host),
                "meta": {
                    "mac": pr.get("mac") or "",
                    "ports": ports,
                    "discovered": True,
                    "same_wifi": ip.startswith(prefix + ".") or is_host,
                },
                "state": "online" if (pr.get("reachable") or is_host) else "offline",
            }
            found.append(rec)
            if register:
                register_device(
                    name=rec["name"] if not is_host else "POCKET desk",
                    kind=rec["kind"],
                    address=ip,
                    room="network" if not is_host else "desk",
                    protocol="lan",
                    meta=rec["meta"],
                    state=rec["state"],
                    reachable=rec["reachable"],
                )

    # Gateway as router
    gw = f"{prefix}.1"
    if register and not any(f.get("address") == gw for f in found):
        pr = _probe_host(gw)
        if pr.get("reachable"):
            register_device(
                name="Home router",
                kind="router",
                address=gw,
                room="network",
                protocol="lan",
                meta={"ports": pr.get("open_ports") or [], "discovered": True, "same_wifi": True},
                state="online",
                reachable=True,
            )
            found.append({"name": "Home router", "address": gw, "kind": "router"})

    ms = int((time.time() - t0) * 1000)
    return {
        "ok": True,
        "schema": "pocket.iot_home.discover.v1",
        "host_ip": host_ip,
        "subnet": prefix + ".0/24",
        "arp_neighbors": len(neighbors),
        "probed": len(probe_list),
        "found": len(found),
        "devices": found[:40],
        "registry_count": list_devices().get("count"),
        "ms": ms,
        "note": "Same Wi‑Fi devices share this registry on desk + phone",
    }


def control_device(
    *,
    device_id: str = "",
    name: str = "",
    action: str = "toggle",
) -> Dict[str, Any]:
    """Toggle / on / off a registered device.

    For LAN devices with an HTTP port we try a lightweight probe; state is always
    recorded on the shared registry so phone + desk stay in sync.
    """
    action = (action or "toggle").lower().strip()
    if action not in ("toggle", "on", "off", "ping", "status"):
        return {"ok": False, "error": "action must be toggle|on|off|ping|status"}
    devices = _load_devices()
    target = None
    for d in devices:
        if device_id and d.get("id") == device_id:
            target = d
            break
        if name and (d.get("name") or "").lower() == name.lower():
            target = d
            break
    if not target:
        return {"ok": False, "error": "device not found"}

    addr = (target.get("address") or "").strip()
    prev = (target.get("state") or "unknown").lower()
    new_state = prev
    http_ok = None

    if action == "ping" or action == "status":
        if addr:
            pr = _probe_host(addr, ports=(80, 443, 8080, 8123), timeout=0.5)
            http_ok = pr.get("reachable")
            new_state = "online" if http_ok else "offline"
        else:
            new_state = prev or "unknown"
    else:
        if action == "toggle":
            new_state = "off" if prev in ("on", "online") else "on"
        else:
            new_state = action  # on|off
        # Best-effort HTTP nudge for simple devices (never claims Matter/cloud success)
        if addr and new_state in ("on", "off"):
            for path in (f"/cm?cmnd=Power%20{new_state}", f"/relay?state={new_state}", "/"):
                try:
                    url = f"http://{addr}{path}"
                    req = urllib.request.Request(url, method="GET")
                    with urllib.request.urlopen(req, timeout=1.2) as r:
                        http_ok = r.status < 500
                    if http_ok:
                        break
                except Exception:
                    http_ok = False

    with _lock:
        devices = _load_devices()
        for d in devices:
            if d.get("id") == target.get("id"):
                d["state"] = new_state
                d["last_seen"] = time.time()
                d["reachable"] = True if http_ok is True else d.get("reachable")
                if http_ok is False and action in ("ping", "status"):
                    d["reachable"] = False
                d.setdefault("meta", {})["last_action"] = action
                d.setdefault("meta", {})["last_action_at"] = time.time()
                target = d
                break
        _save_devices(devices)

    return {
        "ok": True,
        "device": target,
        "action": action,
        "state": new_state,
        "http": http_ok,
        "shared": "desk + phone registry",
    }


def phone_presence(
    *,
    label: str = "POCKET Phone",
    peer_id: str = "",
    client_ip: str = "",
    pair_token: str = "",
) -> Dict[str, Any]:
    """Phone on same Wi‑Fi announces itself into the shared IoT registry."""
    name = (label or "POCKET Phone").strip()[:80] or "POCKET Phone"
    if peer_id:
        name = f"{name} · {peer_id[:8]}"
    r = register_device(
        name=name,
        kind="phone",
        address=client_ip or "",
        room="carry",
        protocol="pair" if pair_token else "lan",
        meta={
            "peer_id": peer_id,
            "paired": bool(pair_token),
            "same_wifi": True,
            "client_ip": client_ip,
        },
        state="online",
        reachable=True,
    )
    return {
        "ok": True,
        "device": r.get("device"),
        "host_ip": _host_lan_ip(),
        "phone_lan": f"http://{_host_lan_ip()}:8787/phone",
        "message": "Phone registered on home IoT — same Wi‑Fi as desk",
    }


def phone_bridge() -> Dict[str, Any]:
    """How phone connects into home + desk on the same Wi‑Fi."""
    try:
        from pocket.node_transfer import hello, status as node_status

        node = {"hello": hello(), "status": node_status()}
    except Exception as e:
        node = {"error": str(e)[:100]}
    ip = _host_lan_ip()
    pub = ""
    try:
        from pocket.sovereign_stack import _read_public_url

        pub = _read_public_url()
    except Exception:
        pass
    phones = [d for d in _load_devices() if d.get("kind") == "phone"]
    return {
        "ok": True,
        "phone_local": "http://127.0.0.1:8787/phone",
        "phone_lan": f"http://{ip}:8787/phone" if ip else None,
        "phone_remote": f"{pub}/phone" if pub else None,
        "host_ip": ip,
        "same_wifi": (
            "Open phone_lan on your phone while on this Wi‑Fi. "
            "Pair with desk code for transfers; IoT registry is shared."
        ),
        "pair": "Desk Workspace → Get pair code → Phone redeem",
        "discover": "POST /v1/iot/discover  ·  GET /v1/iot",
        "control": "POST /v1/iot/control {id|name, action:toggle|on|off}",
        "node": node,
        "phones_seen": len(phones),
        "iot": "Devices on this Wi‑Fi appear on desk + phone Home",
        "hz": hz_status(),
    }


def status() -> Dict[str, Any]:
    devs = list_devices()
    host_ip = _host_lan_ip()
    return {
        "ok": True,
        "schema": "pocket.iot_home.v2",
        "doctrine": "Phone + desk share IoT on the same Wi‑Fi",
        "devices": devs.get("devices") or [],
        "device_count": devs.get("count") or 0,
        "host_ip": host_ip,
        "subnet": _subnet_prefix(host_ip) + ".0/24",
        "hz": hz_status(),
        "phone": phone_bridge(),
        "protocols_supported": ["lan", "pair_token", "ble_hz", "http_control", "mqtt_future", "matter_future"],
        "skills": [
            "iot_status",
            "iot_list",
            "iot_register",
            "iot_phone",
            "iot_hz_status",
            "iot_discover",
            "iot_control",
        ],
        "endpoints": {
            "status": "GET /v1/iot",
            "discover": "POST /v1/iot/discover",
            "control": "POST /v1/iot/control",
            "presence": "POST /v1/iot/presence",
            "phone": "GET /v1/iot/phone",
        },
    }


def seed_home_defaults() -> Dict[str, Any]:
    """Seed rooms + run a light same-WiFi discover so registry is shared."""
    existing = {d.get("name") for d in _load_devices()}
    seeds = [
        ("Living room lamp", "light", "lan", "living"),
        ("Hall plug", "plug", "lan", "hall"),
        ("Thermostat", "climate", "lan", "hall"),
        ("POCKET desk", "desk", "lan", "desk"),
    ]
    added = []
    host_ip = _host_lan_ip()
    for name, kind, proto, room in seeds:
        if name in existing:
            continue
        addr = host_ip if kind == "desk" else ""
        r = register_device(
            name=name,
            kind=kind,
            protocol=proto,
            room=room,
            address=addr,
            state="online" if kind == "desk" else "unknown",
            reachable=kind == "desk",
        )
        if r.get("ok"):
            added.append(r["device"])
    disc = discover_lan(deep=False, register=True)
    return {
        "ok": True,
        "added": added,
        "discovered": disc.get("found"),
        "count": list_devices().get("count"),
        "host_ip": host_ip,
        "phone_lan": f"http://{host_ip}:8787/phone",
    }
