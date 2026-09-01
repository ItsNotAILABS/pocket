"""WorkGrant + MemoryLease — NEXUS-shaped authority before fan-out.

Pocket plans. A grant is required before RAH executes leaves or a leaf
reads Pixel Memory. Free-text “fan out” only produces a plan.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "grants"
ROOT.mkdir(parents=True, exist_ok=True)


def _path(gid: str) -> Path:
    return ROOT / f"{gid}.json"


def issue(
    *,
    principal: str,
    tenant: str = "",
    capability: str = "plan",
    budget: int = 6,
    deadline_s: float = 180,
    tools: Optional[List[str]] = None,
    parent_run: str = "",
    idempotency_key: str = "",
) -> Dict[str, Any]:
    key = (idempotency_key or "").strip()
    if key:
        hid = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        existing = _path("idemp-" + hid)
        if existing.is_file():
            try:
                return json.loads(existing.read_text(encoding="utf-8"))
            except Exception:
                pass
    gid = "wg-" + secrets.token_hex(8)
    rec = {
        "ok": True,
        "schema": "pocket.work_grant.v1",
        "id": gid,
        "principal": (principal or "unknown")[:80],
        "tenant": (tenant or principal or "local")[:80],
        "capability": capability,
        "budget": max(1, min(int(budget), 16)),
        "deadline": time.time() + max(15, float(deadline_s)),
        "tools": list(tools or ["think"]),
        "parent_run": parent_run,
        "idempotency_key": key,
        "issued_at": time.time(),
        "revoked": False,
    }
    _path(gid).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    if key:
        _path("idemp-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]).write_text(
            json.dumps(rec, indent=2), encoding="utf-8"
        )
    return rec


def load(grant_id: str) -> Optional[Dict[str, Any]]:
    p = _path((grant_id or "").strip())
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def valid(grant_id: str, *, capability: str = "") -> Dict[str, Any]:
    rec = load(grant_id)
    if not rec:
        return {"ok": False, "error": "no grant"}
    if rec.get("revoked"):
        return {"ok": False, "error": "revoked"}
    if time.time() > float(rec.get("deadline") or 0):
        return {"ok": False, "error": "expired"}
    cap = (capability or "").strip()
    if cap and cap not in (rec.get("tools") or []) and cap != rec.get("capability"):
        if rec.get("capability") not in ("execute", "rah", "all"):
            return {"ok": False, "error": f"capability {cap} not on grant"}
    return {"ok": True, "grant": rec}


def revoke(grant_id: str) -> Dict[str, Any]:
    rec = load(grant_id)
    if not rec:
        return {"ok": False, "error": "no grant"}
    rec["revoked"] = True
    rec["revoked_at"] = time.time()
    _path(grant_id).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return {"ok": True, "id": grant_id}


def memory_lease(grant_id: str, *, kinds: Optional[List[str]] = None) -> Dict[str, Any]:
    g = valid(grant_id, capability="memory")
    if not g.get("ok"):
        # execute grants may still lease memory
        g = valid(grant_id)
        if not g.get("ok"):
            return g
    rec = g["grant"]
    allow = kinds or ["episodic", "semantic"]
    lid = "ml-" + secrets.token_hex(6)
    lease = {
        "ok": True,
        "schema": "pocket.memory_lease.v1",
        "id": lid,
        "grant_id": rec["id"],
        "tenant": rec.get("tenant"),
        "kinds": allow,
        "expires": rec.get("deadline"),
    }
    return lease


CONTRACTS = {
    "schema": "pocket.contracts.v1",
    "framework": "RAH",
    "protocol": "MEDINA-RAH/1.0",
    "roles": {
        "pocket": "Orchestrator — plans work, cannot silently execute fan-out from wording",
        "nexus": "Authority — WorkGrant: principal, tenant, capability, budget, deadline, tools, parent, idempotency",
        "auro": "Cognition — analyze/recall a MemoryLease; never self-authorize tools",
        "rah": "Execution fabric — concurrent leaves only after a valid grant",
        "verifier": "Independent judge — required for shell/code/browser/persistence; synthesis is not proof",
        "pixel": "Evidence — visual/pixel source of truth; episodic/semantic/procedural are other kinds",
    },
    "objects": [
        "pocket.work_grant.v1",
        "pocket.memory_lease.v1",
        "pocket.rah.plan.v1",
        "pocket.rah.v1",
        "pocket.auro_leaf_receipt.v1",
        "pocket.action_receipt.v1",
    ],
    "agent_tools": ["rah_plan", "rah_run", "rah_status", "rah_grant", "rah_lease"],
    "http": [
        "GET /v1/rah",
        "GET /v1/rah/contracts",
        "POST /v1/rah/plan",
        "POST /v1/rah/run",
        "POST /v1/rah/grant",
    ],
}


def contracts() -> Dict[str, Any]:
    try:
        from pocket.contracts import catalog

        return catalog()
    except Exception:
        return {"ok": True, **CONTRACTS}


def recall_capsule(lease: Dict[str, Any], *, query: str = "", limit: int = 6) -> Dict[str, Any]:
    """AURO-facing excerpts only — hashes, provenance, short text. Not host memory."""
    if not lease or not lease.get("ok"):
        return {"ok": False, "error": "no lease"}
    if time.time() > float(lease.get("expires") or 0):
        return {"ok": False, "error": "lease expired"}
    from pocket.pixel_vmem import search as vmem_search

    hits = vmem_search(query or lease.get("tenant") or "", limit=limit)
    items = []
    for h in (hits.get("hits") or hits.get("items") or [])[:limit]:
        items.append(
            {
                "symbol": h.get("symbol"),
                "kind": h.get("kind") or h.get("memory_kind") or "episodic",
                "preview": str(h.get("preview") or h.get("note") or "")[:280],
                "sha256": h.get("sha256") or h.get("hash"),
                "classification": h.get("classification") or "internal",
                "citation": h.get("symbol"),
            }
        )
    return {
        "ok": True,
        "lease_id": lease.get("id"),
        "tenant": lease.get("tenant"),
        "excerpts": items,
        "unrestricted": False,
    }
