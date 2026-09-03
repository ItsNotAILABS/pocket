"""Local port maintainer — Pocket hosts local services without killing strangers.

Watchdog may only attest and restart *its* listeners. Other processes on other
ports are listed, never force-killed.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from typing import Any, Dict, List

OWNED = {
    int(os.environ.get("POCKET_PORT") or "8787"): "pocket-host",
}


def _listen_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if sys.platform != "win32":
        return rows
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        return rows
    seen = set()
    for line in out.splitlines():
        u = line.upper()
        if "LISTENING" not in u:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        local = parts[1] if parts[0].upper().startswith("TCP") else parts[1]
        try:
            port = int(local.rsplit(":", 1)[-1])
            pid = int(parts[-1])
        except Exception:
            continue
        key = (port, pid)
        if key in seen:
            continue
        seen.add(key)
        owned = OWNED.get(port)
        rows.append(
            {
                "port": port,
                "pid": pid,
                "owned": owned,
                "ours": bool(owned),
            }
        )
    return rows


def snapshot() -> Dict[str, Any]:
    rows = _listen_rows()
    pocket = [r for r in rows if r.get("ours")]
    foreign = [r for r in rows if not r.get("ours")]
    return {
        "ok": True,
        "schema": "pocket.local_ports.v1",
        "owned": OWNED,
        "listeners": rows,
        "pocket": pocket,
        "foreign_count": len(foreign),
        "note": "Maintain Pocket ports only. Foreign listeners are listed, never killed.",
    }


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=0.25):
            return True
    except Exception:
        return False


def maintain() -> Dict[str, Any]:
    """Ensure owned Pocket ports answer. Do not touch foreign PIDs."""
    from pocket.host_runtime import ensure

    snap = snapshot()
    actions: List[Dict[str, Any]] = []
    for port, name in OWNED.items():
        if name == "pocket-host" and not port_open(port):
            actions.append({"port": port, "name": name, **ensure("pocket")})
        else:
            actions.append({"port": port, "name": name, "up": port_open(port), "already": True})
    snap["maintained"] = actions
    return snap
