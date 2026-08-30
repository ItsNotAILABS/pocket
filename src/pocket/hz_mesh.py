"""HZ mesh — governed logical coordination channels for POCKET.

The HZ values in this module are *logical semantic/cadence labels*. They are
not literal RF frequencies. Physical frequency models, when needed, live in
AURO/MESIE (``mesie.edge.hz_ladder``) and device-specific protocols.

The default transport remains POCKET's encrypted mesh-disk file bus, while the
channel contract is transport-neutral and can also be carried over HTTP, MCP,
WebSocket, in-process calls, or governed device bridges.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pocket.channel_fabric import CHANNELS as FABRIC_CHANNELS, envelope as channel_envelope
from pocket.mesh_disk import channel_tail, leave_artifact, send_message, CHANNELS, PROTOCOLS
from pocket.protocols import bluetooth_hz as _bt

HZ_LANES: Dict[str, Dict[str, Any]] = {
    name: {
        "channel": f"freq-{meta['hz']}",
        "hz": meta["hz"],
        "purpose": meta["class"],
        "risk": meta["risk"],
        "retention": meta["retention"],
    }
    for name, meta in FABRIC_CHANNELS.items()
}


def list_lanes() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.hz-mesh.v2",
        "lanes": HZ_LANES,
        "channels_dir": str(CHANNELS),
        "protocols": str(PROTOCOLS / "hz"),
        "transport": "encrypted-mesh-disk-default",
        "transport_options": ["mesh-disk", "http", "mcp", "websocket", "in-process", "device-bridge"],
        "logical_hz": True,
        "physical_frequency_claim": False,
        "physical_hz_reference": "AURO/MESIE mesie.edge.hz_ladder",
        "ble": "optional-device-transport",
        "ble_map": _bt.status().get("ble_map"),
        "channels": _bt.list_channels(),
    }


def resolve_channel(lane_or_freq: str) -> str:
    key = (lane_or_freq or "user").lower().strip()
    if key in HZ_LANES:
        return HZ_LANES[key]["channel"]
    if key.startswith("freq-"):
        return key
    if key.isdigit():
        return f"freq-{key}"
    return "freq-0"


def publish(
    from_agent: str,
    body: str,
    *,
    lane: str = "user",
    to_agent: str = "ARCHON",
    kind: str = "hz",
    hz: Optional[float] = None,
    request_id: str = "",
) -> Dict[str, Any]:
    # Numeric `hz` remains compatibility-only for the BLE mapping. New code
    # should publish by named logical lane.
    if hz is not None:
        ch = _bt.channel_for_hz(hz)
        logical_lane = lane
    else:
        ch = resolve_channel(lane)
        logical_lane = lane if lane in HZ_LANES else "user"
    msg = channel_envelope(
        sender=from_agent,
        recipient=to_agent,
        channel_name=logical_lane,
        kind=kind,
        body=body,
        request_id=request_id,
        transport="mesh-disk",
    )
    sent = send_message(from_agent, to_agent, body, channel=ch, kind=kind, encrypt=True)
    return {"ok": bool(sent.get("ok", True)), "mesh": sent, "envelope": msg}


def listen(lane: str = "user", *, limit: int = 40) -> Dict[str, Any]:
    ch = resolve_channel(lane)
    return channel_tail(ch, limit=limit)


def bluetooth_stub_scan() -> Dict[str, Any]:
    note = (
        "# Bluetooth / HZ transport note\n\n"
        "POCKET logical HZ lanes do not require Bluetooth and do not represent literal RF carriers.\n"
        "Agents coordinate through encrypted transport-neutral channel envelopes; mesh-disk is default.\n"
        "BLE may be attached later as a governed device transport.\n"
        f"Compatibility BLE map: {_bt.status().get('ble_map')}\n"
    )
    art = leave_artifact("TABELLARIUS", "bt_scan_stub.md", note, notify=["ARCHON", "RESEARCH_HEADLESS"])
    publish("TABELLARIUS", "BLE transport probe complete", lane="intel", kind="bluetooth")
    return {"ok": True, "artifact": art, "devices": [], "note": "logical HZ + mesh-disk default", "ble_map": _bt.status().get("ble_map")}


# Compatibility re-exports from protocols.bluetooth_hz.
channel_for_hz = _bt.channel_for_hz
hz_for_channel = _bt.hz_for_channel
mesh_broadcast = _bt.mesh_broadcast
mesh_leave = _bt.mesh_leave
tune = _bt.tune
