"""POCKET sold product — the SKU customers buy.

Founder desk on this machine stays founder.
This module is the *customer* product: seats, plans, tenant space, commercial license.

Channel: POCKET_CHANNEL=sold  (does not flip POCKET_EDITION=founder)
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from pocket.revenuecat import PLANS as RC_PLANS

SOLD_VERSION = "1.0.0"
SKU = "pocket-sold"
CHANNEL = "sold"

# Tabs / surfaces customers do not see on a paid seat (founder host tools)
HIDDEN_TABS_FOR_SEATS = (
    "lab",
    "curiosities",
    "os",
    "screen",
    "remote",
    "platform",
)

SOLD_TABS = (
    "desk",
    "habitat",
    "working",
    "phone",
    "work",
    "studio",
    "creative",
    "voice_studio",
    "mcp",
)

COMMERCIAL_LICENSE = {
    "id": "POCKET-Commercial-1.0",
    "title": "POCKET Commercial License",
    "summary": (
        "Paid seats may run POCKET for their own business on their tenant space. "
        "No resale, no multi-tenant hosting of other companies, no founder-disk access. "
        "Subscriptions are billed via RevenueCat. POCK is a usage meter, not a refundable balance."
    ),
    "url": "/join#license",
}

PROMISE = [
    "Your own seat — username and password you choose",
    "Your files live under your tenant, never the operator's disk",
    "Desk + agents + phone + API on the plan you buy",
    "Cancel anytime in RevenueCat / store; access lasts through the paid period",
]


def channel() -> str:
    raw = (os.environ.get("POCKET_CHANNEL") or "").strip().lower()
    if raw in ("sold", "market", "customer", "retail"):
        return "sold"
    return "founder" if (os.environ.get("POCKET_EDITION") or "founder").lower() in (
        "founder",
        "internal",
        "owner",
        "private",
        "lab",
    ) else "sold"


def is_sold_channel() -> bool:
    return channel() == "sold"


def plans() -> List[Dict[str, Any]]:
    out = []
    for eid, spec in RC_PLANS.items():
        out.append(
            {
                "id": eid,
                "name": spec.get("name"),
                "usd": spec.get("usd"),
                "seats": spec.get("seats") or 0,
                "pock_monthly": spec.get("pock_monthly") or spec.get("pock_once") or 0,
                "consumable": bool(spec.get("consumable")),
                "api_tier": spec.get("api_tier") or "",
                "entitlement": eid,
            }
        )
    return out


def catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "sku": SKU,
        "version": SOLD_VERSION,
        "channel": channel(),
        "name": "POCKET",
        "tagline": "AI workspace on your machine — seats you buy, files that stay yours.",
        "promise": PROMISE,
        "plans": plans(),
        "license": COMMERCIAL_LICENSE,
        "hidden_tabs": list(HIDDEN_TABS_FOR_SEATS),
        "sold_tabs": list(SOLD_TABS),
        "join": "/join",
        "billing": "/billing",
        "desk": "/desk",
        "download": "/download",
        "doctrine": [
            "Sold SKU ≠ founder lab notebook.",
            "Invite creates a member seat, never the owner account.",
            "Tenant cwd is ~/.pocket/tenants/<user>/ only.",
            "RevenueCat owns paid entitlements; POCK meters usage.",
            "Never auto-pay.",
        ],
    }


def seat_flags(user: Dict[str, Any] | None) -> Dict[str, Any]:
    """What the desk JS should hide/show for this principal."""
    u = user or {}
    founder = bool(u.get("is_owner") or (u.get("role") or "") == "admin")
    edition = "founder" if founder else "market"
    return {
        "edition": edition,
        "sold": not founder,
        "hide_tabs": [] if founder else list(HIDDEN_TABS_FOR_SEATS),
        "plan": u.get("plan") or "",
        "tenant": "" if founder else (u.get("user") or ""),
    }
