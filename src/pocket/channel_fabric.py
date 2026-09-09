"""Governed communications fabric spanning agents, models, voice, memory and proof.

HZ lanes are logical semantic/cadence channels layered over transports such as
POCKET mesh disk, HTTP, MCP, WebSocket, or governed device links. The channel
envelope is the causal truth object across those transports.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict

from pocket.doctrine_laws import validate_message
from pocket.technology_garden import hardened_envelope, validate_hardened_envelope

CHANNELS: Dict[str, Dict[str, Any]] = {
    "user": {"hz":0,"class":"command","risk":"mixed","retention":"session","max_inflight":128,"participants":["user","voice","host","agent"]},
    "heartbeat": {"hz":1,"class":"liveness","risk":"read","retention":"short","max_inflight":256,"participants":["agent","model-runtime","host"]},
    "design": {"hz":2,"class":"creation","risk":"compute","retention":"project","max_inflight":64,"participants":["design","builder","voice"]},
    "security": {"hz":3,"class":"audit","risk":"privileged-read","retention":"audit","max_inflight":128,"participants":["security","host","proof"]},
    "ship": {"hz":4,"class":"release","risk":"high","retention":"release","max_inflight":32,"participants":["deployer","host","proof"]},
    "intel": {"hz":5,"class":"research","risk":"compute","retention":"project","max_inflight":128,"participants":["researcher","model-runtime","mesie","auro"]},
    "model": {"hz":6,"class":"inference","risk":"compute","retention":"bounded","max_inflight":128,"participants":["model-router","auro","mesie","foundation-model"]},
    "memory": {"hz":7,"class":"continuity","risk":"write-bounded","retention":"durable","max_inflight":64,"participants":["memory","host","agent"]},
    "proof": {"hz":8,"class":"evidence","risk":"append-only","retention":"durable","max_inflight":128,"participants":["verifier","host","receipt","mesie","auro"]},
    "voice": {"hz":9,"class":"speech-state","risk":"mixed","retention":"session","max_inflight":64,"participants":["voice","host","agent"]},
    "deploy": {"hz":10,"class":"external-change","risk":"high","retention":"release","max_inflight":16,"participants":["deployer","host","forge"]},
    "recovery": {"hz":11,"class":"failure-repair","risk":"bounded","retention":"incident","max_inflight":32,"participants":["host","agent","security","verifier"]},
}

TRANSPORTS = ("mesh-disk", "http", "mcp", "websocket", "in-process", "device-bridge")
RETENTION_TTL_SECONDS = {
    "short": 60, "session": 3600, "bounded": 900, "project": 14400,
    "incident": 21600, "audit": 86400, "release": 86400, "durable": 86400,
}


def channel(name: str) -> Dict[str, Any]:
    key = (name or "user").strip().lower()
    return {"name": key, **CHANNELS.get(key, CHANNELS["user"])}


def envelope(*, sender: str, recipient: str, channel_name: str, kind: str, body: Any,
             request_id: str = "", state: str = "published", transport: str = "mesh-disk",
             parent_id: str = "", side_effect: bool = False, approval: str = "",
             idempotency_key: str = "", non_replayable: bool = False,
             owner: str = "", lease_id: str = "", capability_descriptor: Dict[str, Any] | None = None,
             fallback: str = "", fallback_disclosed: bool = False) -> Dict[str, Any]:
    ch = channel(channel_name)
    now = time.time()
    ttl = RETENTION_TTL_SECONDS.get(ch["retention"], 300)
    msg_id = f"msg-{uuid.uuid4().hex[:16]}"
    req_id = request_id or f"req-{uuid.uuid4().hex[:16]}"
    msg = {
        "schema": "pocket.channel-envelope.v2",
        "message_id": msg_id,
        "request_id": req_id,
        "parent_id": parent_id or None,
        "from": sender,
        "to": recipient,
        "channel": ch["name"],
        "logical_hz": ch["hz"],
        "semantic_class": ch["class"],
        "risk": ch["risk"],
        "retention": ch["retention"],
        "max_inflight": ch["max_inflight"],
        "kind": kind,
        "transport": transport if transport in TRANSPORTS else "mesh-disk",
        "body": body,
        "state": state,
        "side_effect": bool(side_effect),
        "approval": approval or ("confirm" if side_effect else "allow"),
        "idempotency_key": idempotency_key or (req_id if side_effect and not non_replayable else ""),
        "non_replayable": bool(non_replayable),
        "owner": owner or sender,
        "lease_id": lease_id or None,
        "capability_selected": bool(capability_descriptor),
        "capability_descriptor": capability_descriptor or None,
        "fallback": fallback or None,
        "fallback_disclosed": bool(fallback_disclosed),
        "created_at": now,
        "expires_at": now + ttl,
        "freshness_required": True,
        "lineage": {"parent_id": parent_id or None},
    }
    msg["law_validation"] = validate_message(msg)
    secured = hardened_envelope(msg, ttl_s=ttl)
    if not secured.get("ok"):
        msg["hardening_validation"] = secured
        return msg
    out = secured["envelope"]
    out["hardening_validation"] = {"ok": True, "ttl_s": ttl}
    return out


def validate_envelope(message: Dict[str, Any], *, now: float | None = None, seen_nonces: tuple[str, ...] = ()) -> Dict[str, Any]:
    """Validate tamper/expiry/replay protections at transport ingress."""
    hard = validate_hardened_envelope(message, now=now, seen_nonces=seen_nonces)
    laws = validate_message(message)
    return {"ok": bool(hard.get("ok")) and bool(laws.get("ok")), "hardening": hard, "laws": laws}


def route_for(kind: str, *, consequence: str = "") -> Dict[str, Any]:
    low = (kind or "").lower()
    if consequence in {"external", "deploy", "high"} or any(x in low for x in ("deploy", "publish", "release")):
        name = "deploy"
    elif any(x in low for x in ("receipt", "verify", "evidence", "benchmark", "attest")):
        name = "proof"
    elif any(x in low for x in ("infer", "model", "embed", "spectral", "auro", "mesie", "foundation")):
        name = "model"
    elif any(x in low for x in ("research", "discover", "intel")):
        name = "intel"
    elif any(x in low for x in ("memory", "resume", "context")):
        name = "memory"
    elif any(x in low for x in ("voice", "speak", "listen")):
        name = "voice"
    elif any(x in low for x in ("recover", "retry", "repair", "failover")):
        name = "recovery"
    else:
        name = "user"
    return channel(name)


def manifest() -> Dict[str, Any]:
    return {
        "schema": "pocket.channel-fabric.v2",
        "channels": {k: dict(v) for k, v in CHANNELS.items()},
        "transports": list(TRANSPORTS),
        "retention_ttl_seconds": dict(RETENTION_TTL_SECONDS),
        "hardening": [
            "canonical-digest", "bounded-ttl", "nonce", "replay-hook", "side-effect-approval",
            "idempotency", "ownership", "capability-disclosure", "backpressure-contract",
        ],
        "invariant": "logical HZ labels carry semantics/cadence; they do not imply literal RF transport",
    }
