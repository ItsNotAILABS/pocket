"""Internal Pocket contracts — the objects agents and surfaces must speak.

These are first-class. HTTP, WebMCP, RAH, nodes, and vaults all name them.
"""

from __future__ import annotations

from typing import Any, Dict


CATALOG: Dict[str, Any] = {
    "ok": True,
    "schema": "pocket.contracts.v1",
    "protocol": "MEDINA-RAH/1.0",
    "roles": {
        "pocket": "Orchestrator. Plans. Does not silently execute fan-out from wording.",
        "nexus": "Authority. Issues WorkGrant (principal, tenant, capability, budget, deadline, tools, parent, idempotency).",
        "auro": "Cognition. Recalls a MemoryLease. Never self-authorizes tools.",
        "rah": "Execution fabric. Concurrent leaves only after a valid grant.",
        "verifier": "Independent judge. Required for shell, code, browser, persistence. Synthesis is not proof.",
        "pixel": "Evidence. Visual/pixel is source of truth. Episodic / semantic / procedural are other kinds.",
        "node": "Mesh seat. Phone, TV, glasses, PC. Presence + capability, not hostname authority.",
    },
    "objects": {
        "pocket.work_grant.v1": "Scoped, expiring approval before RAH execute.",
        "pocket.memory_lease.v1": "Read rights for selected memory kinds. Not raw host lattice.",
        "pocket.recall_capsule.v1": "AURO-facing excerpts, hashes, citations.",
        "pocket.rah.plan.v1": "Fan-out plan. Harmless without a grant.",
        "pocket.rah.v1": "A RAH run bound to grant_id, tenant, budget.",
        "pocket.rah.leaf.v1": "One isolated job: tools, deadline, parent, idempotency.",
        "pocket.verifier.v1": "Required leaf for consequence classes.",
        "pocket.action_receipt.v1": "Signed consequence record.",
        "pocket.auro_leaf_receipt.v1": "Adapter + checkpoint digest + grant.",
        "pocket.node.v1": "Mesh node (pc|phone|tv|glasses).",
        "pocket.node.view.v1": "Wi-Fi viewer that receives the laptop stream.",
        "pocket.portal.session.v1": "Identity-bound Portal capability (not a timestamp cookie).",
        "pocket.twin.vault.v1": "Tenant vault. Identity is the signed-in principal.",
        "pocket.pixel.page.v1": "Encrypted pixel page. No reconstructable sidecar.",
        "pocket.pixel.kind.v1": "episodic | semantic | procedural | visual",
    },
    "agent_tools": [
        "rah_plan",
        "rah_grant",
        "rah_run",
        "rah_status",
        "rah_lease",
        "rah_contracts",
        "node_hello",
        "node_tv_join",
        "eyes_see",
        "eyes_touch",
    ],
    "http": [
        "GET /v1/contracts",
        "GET /v1/rah/contracts",
        "POST /v1/rah/grant",
        "POST /v1/rah/plan",
        "POST /v1/rah/run",
        "GET /v1/nodes/view",
        "POST /v1/nodes/view",
        "GET /phoneai/tv",
    ],
    "memory_kinds": ["episodic", "semantic", "procedural", "visual"],
    "nodes": ["pc", "phone", "tv", "glasses"],
}


def catalog() -> Dict[str, Any]:
    return dict(CATALOG)
