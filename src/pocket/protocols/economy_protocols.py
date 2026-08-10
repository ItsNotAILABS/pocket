"""Economic domain protocols — registered alongside platform majors."""

from __future__ import annotations

from typing import Any, Dict

from pocket.economy import ECONOMIC_PROTOCOLS, domain_status, protocols as economy_protocols_catalog


def manifest() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.economy.protocol_domain.v1",
        "domain": "economic",
        "name": "POCKET Economic Domain",
        "count": len(ECONOMIC_PROTOCOLS),
        "protocols": ECONOMIC_PROTOCOLS,
        "status": domain_status(),
        "catalog": economy_protocols_catalog(),
    }


def status() -> Dict[str, Any]:
    st = domain_status()
    return {"ok": bool(st.get("ok")), **st}
