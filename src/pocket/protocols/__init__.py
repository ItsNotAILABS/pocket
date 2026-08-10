"""POCKET protocol modules — OS bridges, Hz mesh, Subagent Mesh, Capsule/WebGPU."""

from __future__ import annotations

from pocket.protocols.microsoft_protocol import (
    click_ui,
    maximize_window,
    open_host_app,
    render_page,
    scroll_ui,
    status as microsoft_status,
)
from pocket.protocols.bluetooth_hz import (
    channel_for_hz,
    hz_for_channel,
    list_channels,
    mesh_broadcast,
    mesh_leave,
    status as bluetooth_status,
)
from pocket.protocols.subagent_mesh_protocol import (
    PROTOCOL_ID,
    manifest as mesh_protocol_manifest,
    status as mesh_protocol_status,
    resolve_lane,
)
from pocket.protocols.multi_sandbox_capsule import (
    PROTOCOL_ID as CAPSULE_PROTOCOL_ID,
    manager as capsule_manager,
    protocol_manifest as capsule_protocol_manifest,
    probe_webgpu,
    run_capsule_skill,
    status as capsule_status,
)
from pocket.protocols.platform_protocols import (
    MAJOR_PROTOCOLS,
    list_protocols,
    manifest as major_protocols_manifest,
    platform_protocols_status,
    get_protocol,
)

# RAH is first-class (also listed in MAJOR_PROTOCOLS)
try:
    from pocket.rah import (
        PROTOCOL_ID as RAH_PROTOCOL_ID,
        manifest as rah_manifest,
        status as rah_status,
        run_rah,
        plan_fanout as rah_plan_fanout,
    )
except Exception:  # pragma: no cover
    RAH_PROTOCOL_ID = "MEDINA-RAH/1.0"
    rah_manifest = rah_status = run_rah = rah_plan_fanout = None  # type: ignore

__all__ = [
    "click_ui",
    "maximize_window",
    "open_host_app",
    "render_page",
    "scroll_ui",
    "microsoft_status",
    "channel_for_hz",
    "hz_for_channel",
    "list_channels",
    "mesh_broadcast",
    "mesh_leave",
    "bluetooth_status",
    "PROTOCOL_ID",
    "mesh_protocol_manifest",
    "mesh_protocol_status",
    "resolve_lane",
    "CAPSULE_PROTOCOL_ID",
    "capsule_manager",
    "capsule_protocol_manifest",
    "probe_webgpu",
    "run_capsule_skill",
    "capsule_status",
    "MAJOR_PROTOCOLS",
    "list_protocols",
    "major_protocols_manifest",
    "platform_protocols_status",
    "get_protocol",
    "RAH_PROTOCOL_ID",
    "rah_manifest",
    "rah_status",
    "run_rah",
    "rah_plan_fanout",
]
