"""Governed communications fabric spanning agents, models, voice, memory and proof.

HZ lanes are logical semantic/cadence channels layered over transports such as
POCKET mesh disk, HTTP, MCP, WebSocket, or future device links.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Iterable, List

from pocket.doctrine_laws import validate_message

CHANNELS: Dict[str, Dict[str, Any]] = {
    "user": {"hz":0,"class":"command","risk":"mixed","retention":"session","participants":["user","voice","host","agent"]},
    "heartbeat": {"hz":1,"class":"liveness","risk":"read","retention":"short","participants":["agent","model-runtime","host"]},
    "design": {"hz":2,"class":"creation","risk":"compute","retention":"project","participants":["design","builder","voice"]},
    "security": {"hz":3,"class":"audit","risk":"privileged-read","retention":"audit","participants":["security","host","proof"]},
    "ship": {"hz":4,"class":"release","risk":"high","retention":"release","participants":["deployer","host","proof"]},
    "intel": {"hz":5,"class":"research","risk":"compute","retention":"project","participants":["researcher","model-runtime","mesie","auro"]},
    "model": {"hz":6,"class":"inference","risk":"compute","retention":"bounded","participants":["model-router","auro","mesie","foundation-model"]},
    "memory": {"hz":7,"class":"continuity","risk":"write-bounded","retention":"durable","participants":["memory","host","agent"]},
    "proof": {"hz":8,"class":"evidence","risk":"append-only","retention":"durable","participants":["verifier","host","receipt","mesie"]},
    "voice": {"hz":9,"class":"speech-state","risk":"mixed","retention":"session","participants":["voice","host","agent"]},
    "deploy": {"hz":10,"class":"external-change","risk":"high","retention":"release","participants":["deployer","host","forge"]},
    "recovery": {"hz":11,"class":"failure-repair","risk":"bounded","retention":"incident","participants":["host","agent","security","verifier"]},
}

TRANSPORTS = ("mesh-disk", "http", "mcp", "websocket", "in-process", "device-bridge")


def channel(name: str) -> Dict[str, Any]:
    key = (name or "user").strip().lower()
    return {"name": key, **CHANNELS.get(key, CHANNELS["user"])}


def envelope(*, sender: str, recipient: str, channel_name: str, kind: str, body: Any,
             request_id: str = "", state: str = "published", transport: str = "mesh-disk",
             parent_id: str = "", side_effect: bool = False, approval: str = "") -> Dict[str, Any]:
    ch = channel(channel_name)
    msg = {
        "schema": "pocket.channel-envelope.v1",
        "message_id": f"msg-{uuid.uuid4().hex[:16]}",
        "request_id": request_id or f"req-{uuid.uuid4().hex[:16]}",
        "parent_id": parent_id or None,
        "from": sender,
        "to": recipient,
        "channel": ch["name"],
        "logical_hz": ch["hz"],
        "semantic_class": ch["class"],
        "risk": ch["risk"],
        "kind": kind,
        "transport": transport if transport in TRANSPORTS else "mesh-disk",
        "body": body,
        "state": state,
        "side_effect": bool(side_effect),
        "approval": approval or ("confirm" if side_effect else "allow"),
        "created_at": time.time(),
        "lineage": {"parent_id": parent_id or None},
    }
    msg["law_validation"] = validate_message(msg)
    return msg


def route_for(kind: str, *, consequence: str = "") -> Dict[str, Any]:
    low = (kind or "").lower()
    if consequence in {"external", "deploy", "high"} or any(x in low for x in ("deploy", "publish", "release")):
        name = "deploy"
    elif any(x in low for x in ("receipt", "verify", "evidence", "benchmark")):
        name = "proof"
    elif any(x in low for x in ("infer", "model", "embed", "spectral", "auro", "mesie")):
        name = "model"
    elif any(x in low for x in ("research", "discover", "intel")):
        name = "intel"
    elif any(x in low for x in ("memory", "resume", "context")):
        name = "memory"
    elif any(x in low for x in ("voice", "speak", "listen")):
        name = "voice"
    else:
        name = "user"
    return channel(name)


def manifest() -> Dict[str, Any]:
    return {
        "schema": "pocket.channel-fabric.v1",
        "channels": {k: dict(v) for k, v in CHANNELS.items()},
        "transports": list(TRANSPORTS),
        "invariant": "logical HZ labels carry semantics/cadence; they do not imply literal RF transport",
    }
