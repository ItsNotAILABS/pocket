"""Screen family protocols — kernel, stream, body, pair, origin, runtime.

Live at GET /v1/protocols/{slug}. Doctrine: protocols are the intelligence.
"""

from __future__ import annotations

from typing import Any, Dict, List

FAMILY = "pocket.screen.family.v1"

SLUGS: List[Dict[str, Any]] = [
    {
        "id": "SCREEN-KERNEL/1.1",
        "slug": "screen-kernel",
        "schema": "pocket.screen.kernel.v1",
        "name": "Screen kernel",
        "tier": "major",
        "domain": "screen",
        "summary": "see · touch · type · click · cursor. Unit-square of the visible frame. Humans and agents.",
        "apis": [
            "GET /v1/screen/kernel",
            "POST /v1/screen/see",
            "POST /v1/screen/touch",
            "POST /v1/screen/type",
            "POST /v1/screen/click",
        ],
        "module": "pocket.screen_kernel",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-STREAM/1.0",
        "slug": "stream",
        "schema": "pocket.stream.v1",
        "name": "Portal multiplexed stream",
        "tier": "major",
        "domain": "screen",
        "summary": "WS hello + JSON envelope (seq, geom, 3×3 matrix) then JPEG. Same socket for touch.",
        "apis": ["WS /v1/phoneai/portal/ws", "GET /phoneai/portal"],
        "module": "pocket.phoneai_portal",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-SCREEN-BODY/1.0",
        "slug": "screen-body",
        "schema": "pocket.screen.body.v1",
        "name": "Agent screen body",
        "tier": "major",
        "domain": "screen",
        "summary": "Agent inhabits the live pointer. Occupant + verbs, not a screenshot sidecar.",
        "apis": [
            "POST /v1/screen/embody",
            "GET /v1/screen/body",
            "POST /v1/screen/body",
        ],
        "module": "pocket.screen_body",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-DEVICE-PAIR/1.0",
        "slug": "device-pair",
        "schema": "pocket.device.pair.v1",
        "name": "Device pair (code + WebAuthn)",
        "tier": "major",
        "domain": "security",
        "summary": "LAN mint + phone passkey → revocable portal_device. Code alone is not owner.",
        "apis": [
            "POST /v1/auth/device/mint",
            "GET /v1/auth/device/begin",
            "POST /v1/auth/device/redeem",
            "GET /v1/auth/device/list",
            "POST /v1/auth/device/revoke",
        ],
        "module": "pocket.device_pair",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-ORIGIN/1.0",
        "slug": "origin",
        "schema": "pocket.origin.v1",
        "name": "Exact origin trust",
        "tier": "major",
        "domain": "security",
        "summary": "No wildcard subdomains. rpId is the exact host. POCKET_PUBLIC_URL + POCKET_ALLOWED_ORIGINS.",
        "apis": ["GET /v1/protocols/origin"],
        "module": "pocket.origin_policy",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-RUNTIME-SINGLETON/1.0",
        "slug": "runtime",
        "schema": "pocket.runtime.singleton.v1",
        "name": "Attested watchdog + local ports",
        "tier": "major",
        "domain": "runtime",
        "summary": "One process lock. Startup VBS only. Kill only python on Pocket port. Maintain owned listeners.",
        "apis": [
            "GET /v1/runtime",
            "GET /v1/runtime/ports",
            "POST /v1/runtime/ensure",
            "POST /v1/runtime/ports/maintain",
        ],
        "module": "pocket.host_runtime",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-AGENT-ARCH/1.0",
        "slug": "agent-arch",
        "schema": "pocket.agent.arch.v1",
        "name": "Agent architecture plane",
        "tier": "major",
        "domain": "agents",
        "summary": "identity → seat → route → authority → execute → receipt. Screen is an execute lane.",
        "apis": ["GET /v1/agents/arch", "POST /v1/agents/turn"],
        "module": "pocket.agent_arch",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
    {
        "id": "POCKET-SCREEN-MATRIX/1.0",
        "slug": "screen-matrix",
        "schema": "pocket.screen.matrix.v1",
        "name": "Contain affine map",
        "tier": "major",
        "domain": "screen",
        "summary": "Homogeneous 3×3: unit square of the contained image → desktop pixels.",
        "apis": ["GET /v1/screen/kernel"],
        "module": "pocket.screen_math",
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
    },
]


def list_family() -> List[Dict[str, Any]]:
    return [dict(p) for p in SLUGS]


def status() -> Dict[str, Any]:
    from pocket.screen_kernel import snapshot as ksnap
    from pocket.screen_body import occupant
    from pocket.origin_policy import configured_hosts
    from pocket.host_runtime import status as rst

    k = ksnap()
    occ = occupant()
    rt = rst()
    return {
        "ok": True,
        "schema": FAMILY,
        "family": FAMILY,
        "count": len(SLUGS),
        "kernel": k.get("protocol"),
        "stream": "pocket.stream.v1",
        "occupant": occ.get("occupant"),
        "origins": sorted(configured_hosts()),
        "runtime_up": bool(rt.get("up")),
        "singleton": rt.get("singleton"),
        "protocols": list_family(),
        "spec": "/docs/POCKET_SCREEN_FAMILY_PROTOCOL.md",
        "http": "GET /v1/protocols/screen-family",
    }


def catalog_entries() -> List[Dict[str, Any]]:
    """Entries to merge into the major protocol catalog."""
    rows = []
    for p in SLUGS:
        rows.append(
            {
                "id": p["id"],
                "slug": p["slug"],
                "name": p["name"],
                "tier": p["tier"],
                "domain": p["domain"],
                "summary": p["summary"],
                "apis": list(p["apis"]),
                "module": p["module"],
                "schema": p.get("schema"),
                "family": FAMILY,
            }
        )
    rows.append(
        {
            "id": "POCKET-SCREEN-FAMILY/1.0",
            "slug": "screen-family",
            "name": "Screen family (umbrella)",
            "tier": "major",
            "domain": "screen",
            "summary": "Kernel + stream + body + pair + origin + runtime + arch.",
            "apis": ["GET /v1/protocols/screen-family", "GET /docs/POCKET_SCREEN_FAMILY_PROTOCOL.md"],
            "module": "pocket.protocols.screen_family",
            "family": FAMILY,
        }
    )
    return rows
