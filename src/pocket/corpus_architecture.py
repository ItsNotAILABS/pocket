"""POCKET implementation contract for Corpus de Architectura v2.1.

This module is intentionally declarative. It tells product surfaces, tests, and
operators which body owns which state and which evidence is required. It does
not claim that a Cloudflare deployment, desktop installer, or paired execution
occurred merely because their source is present.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable

CORPUS_ID = "Corpus-de-Architectura-Intelligentiae-Sui-Iuris"
CORPUS_VERSION = "2.1.0"
CORPUS_SCHEMA = "medina.corpus-architectura.v2"

PRINCIPAL_TYPES = (
    "human",
    "organization",
    "agent",
    "model",
    "device",
    "api-client",
    "runtime-cell",
)

RUNTIME_CELLS = ("agent-sandbox", "app-bottle", "mini-os")
EXECUTION_SEQUENCE = (
    "discover",
    "classify-risk",
    "plan",
    "approve",
    "execute",
    "validate",
    "receipt",
)
EVIDENCE_CLASSES = (
    "E0-assertion",
    "E1-source",
    "E2-execution-log",
    "E3-validated-output",
    "E4-signed-receipt",
    "E5-external-custody-and-reproduction",
)

TRIFORM_PRODUCT: Dict[str, Any] = {
    "schema": "pocket.triform-product.v1",
    "product_id": "POCKET",
    "corpus": f"{CORPUS_SCHEMA}@{CORPUS_VERSION}",
    "bodies": [
        {
            "id": "cloud-account",
            "kind": "persistent-account-and-coordination-plane",
            "availability": "independent-of-user-device",
            "owns": [
                "organizations",
                "users-and-roles",
                "invites-and-sessions",
                "entitlements",
                "release-metadata",
                "device-identities",
                "durable-task-queues",
            ],
            "does_not_own": [
                "founder-local-files",
                "desktop-host-authority",
                "unreturned-local-execution-results",
            ],
            "evidence_required": ["deployment-receipt", "D1-migration-receipt", "route-health", "tenant-isolation-tests"],
        },
        {
            "id": "desktop-runtime",
            "kind": "installable-local-execution-body",
            "availability": "starts-or-reuses-bundled-loopback-engine",
            "owns": [
                "local-files",
                "local-models",
                "local-agents",
                "local-runtime-cells",
                "device-private-credentials",
            ],
            "does_not_own": ["global-organization-state", "cloud-entitlements", "other-user-devices"],
            "evidence_required": ["installer-hash", "clean-install-test", "local-health", "uninstall-and-recovery-test"],
        },
        {
            "id": "edge-app",
            "kind": "microsoft-edge-application-surface",
            "availability": "opens-local-runtime-or-cloud-account",
            "owns": ["presentation-state", "selected-product-body"],
            "does_not_own": ["independent-model-brain", "authoritative-identity-store", "local-host-lifecycle"],
            "evidence_required": ["launcher-test", "origin-policy-test", "local-and-cloud-route-test"],
        },
    ],
    "state_ownership": "explicit-by-body",
    "synchronization": "references-and-receipts; never silent full-state replication",
    "availability": "cloud may remain online while devices are offline; local bodies remain useful during cloud failure",
    "claim_boundary": "source code is E1 evidence and does not establish a live cloud deployment or clean desktop installation",
}

DEVICE_FEDERATION: Dict[str, Any] = {
    "schema": "nexus.device-federation.v1",
    "federation_id": "pocket-user-owned-compute",
    "owner": {"principal_type": "organization-or-human"},
    "devices": {
        "identity": "separate-principal",
        "credentials": "restricted-revocable-device-credential",
        "capabilities": "explicit-advertisement",
        "trust": "policy-and-evidence-derived",
        "availability": "intermittent",
    },
    "scheduling_policy": "authority + capability + locality + trust + availability + cost + risk",
    "created_at": "runtime-generated",
    "claim_boundary": "pairing a device does not grant unrestricted remote desktop or founder-session authority",
}

GOVERNED_EXECUTION: Dict[str, Any] = {
    "schema": "pocket.governed-execution.v1",
    "sequence": list(EXECUTION_SEQUENCE),
    "runtime_cells": list(RUNTIME_CELLS),
    "approval": {
        "schema": "nexus.approval.v1",
        "must_bind": [
            "operator_id",
            "agent_id",
            "tool",
            "arguments_hash",
            "runtime_cell_id",
            "filesystem_scope",
            "egress_scope",
            "expiry",
            "nonce",
        ],
        "one_time": True,
        "nonempty_approval_id_is_insufficient": True,
    },
    "validation": "independent-evidence-when-available",
    "receipts": "required-for-consequential-actions",
}

CLAIM_BOUNDARIES = (
    "architecture-configuration-is-not-a-trained-checkpoint",
    "accepted-context-is-not-dense-attention",
    "named-agent-is-not-a-separately-trained-model",
    "source-code-is-not-deployment-evidence",
    "local-hash-chain-is-not-external-custody",
    "same-session-recall-is-not-persistent-memory",
    "successful-build-is-not-clean-install-proof",
    "generated-answer-is-not-experimental-validation",
)


def product_contract() -> Dict[str, Any]:
    return {
        "schema": "pocket.corpus-architecture.v2",
        "corpus_id": CORPUS_ID,
        "corpus_version": CORPUS_VERSION,
        "triform_product": deepcopy(TRIFORM_PRODUCT),
        "device_federation": deepcopy(DEVICE_FEDERATION),
        "governed_execution": deepcopy(GOVERNED_EXECUTION),
        "principal_types": list(PRINCIPAL_TYPES),
        "evidence_classes": list(EVIDENCE_CLASSES),
        "claim_boundaries": list(CLAIM_BOUNDARIES),
        "papers": [
            "tres-formae-una-mens",
            "nubes-perennis-corpus-intermittens",
            "computatio-sui-iuris",
            "identitas-potestas-et-fines",
            "foedus-machinarum",
            "agentes-sub-lege",
            "probatio-ante-assertionem",
            "mercatus-facultatum-agentium",
            "civitas-intelligentiarum",
        ],
    }


def validate_contract(contract: Dict[str, Any] | None = None) -> list[str]:
    value = contract or product_contract()
    errors: list[str] = []
    bodies = value.get("triform_product", {}).get("bodies", [])
    if [body.get("id") for body in bodies] != ["cloud-account", "desktop-runtime", "edge-app"]:
        errors.append("product bodies must be cloud-account, desktop-runtime, edge-app")
    if tuple(value.get("principal_types", ())) != PRINCIPAL_TYPES:
        errors.append("principal type order differs from canonical contract")
    if tuple(value.get("governed_execution", {}).get("sequence", ())) != EXECUTION_SEQUENCE:
        errors.append("governed execution sequence mismatch")
    if tuple(value.get("governed_execution", {}).get("runtime_cells", ())) != RUNTIME_CELLS:
        errors.append("runtime cell classes mismatch")
    if tuple(value.get("evidence_classes", ())) != EVIDENCE_CLASSES:
        errors.append("evidence classes must preserve E0-E5 order")
    if not value.get("governed_execution", {}).get("approval", {}).get("one_time"):
        errors.append("computer-use approvals must be one-time")
    if len(value.get("claim_boundaries", ())) != len(CLAIM_BOUNDARIES):
        errors.append("all truth boundaries must remain explicit")
    return errors


def evidence_rank(evidence_class: str) -> int:
    try:
        return EVIDENCE_CLASSES.index(evidence_class)
    except ValueError as exc:
        raise ValueError(f"unknown evidence class: {evidence_class}") from exc


def evidence_satisfies(observed: str, required: str) -> bool:
    return evidence_rank(observed) >= evidence_rank(required)


def classify_claim(claim_id: str, observed: str, required: str, evidence: Iterable[str]) -> Dict[str, Any]:
    items = [str(item) for item in evidence if str(item).strip()]
    allowed = evidence_satisfies(observed, required) and bool(items or observed == "E0-assertion")
    return {
        "schema": "nexus.evidence-classification.v1",
        "claim_id": claim_id,
        "required_class": required,
        "observed_class": observed,
        "evidence": items,
        "decision": "supported" if allowed else "insufficient-evidence",
        "observed_at": "runtime-generated",
    }
