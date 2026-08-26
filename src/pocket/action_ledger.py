"""POCKET executable action ledger.

This module turns agent/task work into explicit, receipt-bearing actions.
It is intentionally small, stdlib-only, and safe to run in local, CI, or beta
Cloudflare-adjacent workflows.

It does not infer production state. Claims are accepted only when evidence is
provided. Data export, payment, and wallet actions are represented as explicit
operator-approved execution packets with receipts and policy decisions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional

ActionKind = Literal[
    "agent_task",
    "production_claim",
    "data_export",
    "payment_execution",
    "wallet_execution",
]
Decision = Literal["allow", "deny", "confirm"]
Mode = Literal["local", "beta", "sandbox", "provider_ready", "production"]

RAW_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{20,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PRIVATE )?PRIVATE KEY-----"),
    re.compile(r"\b(?:card|pan|cvv|cvc)\s*[:=]\s*\d{3,19}\b", re.IGNORECASE),
    re.compile(r"\bseed phrase\b", re.IGNORECASE),
]

RESTRICTED_KINDS = {"production_claim", "data_export", "payment_execution", "wallet_execution"}
REQUIRED_APPROVAL_FIELDS = {"operator_id", "approval_id", "approved_at"}
REQUIRED_EVIDENCE_FOR_KIND = {
    "production_claim": {"deploy_target", "verification_url_or_run_id", "operator_assertion"},
    "data_export": {"dataset_id", "export_scope", "destination"},
    "payment_execution": {"provider", "provider_reference", "amount", "currency"},
    "wallet_execution": {"provider", "wallet_reference", "network_or_rail", "amount_or_asset"},
}


def _stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _stable(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_stable(v) for v in value]
    return value


def sha256(value: Any) -> str:
    text = json.dumps(_stable(value), separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_ms() -> int:
    return int(time.time() * 1000)


def has_raw_secret(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False, default=str)
    return any(pattern.search(text) for pattern in RAW_SECRET_PATTERNS)


@dataclass(frozen=True)
class OperatorApproval:
    operator_id: str
    approval_id: str
    approved_at: str
    reason: str = "operator-approved"

    def as_dict(self) -> Dict[str, str]:
        return {
            "operator_id": self.operator_id,
            "approval_id": self.approval_id,
            "approved_at": self.approved_at,
            "reason": self.reason,
        }


@dataclass
class PocketAction:
    kind: ActionKind
    title: str
    requested_by: str
    mode: Mode = "beta"
    body: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    approval: Optional[OperatorApproval] = None
    created_at_ms: int = field(default_factory=now_ms)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "pocket.action.v1",
            "kind": self.kind,
            "title": self.title,
            "requested_by": self.requested_by,
            "mode": self.mode,
            "body": _stable(self.body),
            "evidence": _stable(self.evidence),
            "approval": self.approval.as_dict() if self.approval else None,
            "created_at_ms": self.created_at_ms,
        }


class PocketActionLedger:
    def __init__(self, root: str | Path = "dist/pocket-action-ledger") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.actions: List[Dict[str, Any]] = []
        self.receipts: List[Dict[str, Any]] = []

    def decide(self, action: PocketAction) -> Dict[str, Any]:
        action_dict = action.as_dict()
        missing: List[str] = []
        reasons: List[str] = []

        if has_raw_secret(action_dict):
            return {
                "decision": "deny",
                "reasons": ["raw_secret_or_sensitive_material_detected"],
                "missing": [],
            }

        if action.kind in RESTRICTED_KINDS:
            if action.approval is None:
                missing.append("approval")
            else:
                approval = action.approval.as_dict()
                for field_name in REQUIRED_APPROVAL_FIELDS:
                    if not approval.get(field_name):
                        missing.append(f"approval.{field_name}")
            for field_name in REQUIRED_EVIDENCE_FOR_KIND.get(action.kind, set()):
                if field_name not in action.evidence or action.evidence.get(field_name) in (None, ""):
                    missing.append(f"evidence.{field_name}")

        if action.kind in {"payment_execution", "wallet_execution"}:
            if action.mode not in {"provider_ready", "production"}:
                missing.append("mode.provider_ready_or_production")
            if not action.evidence.get("provider_reference") and not action.evidence.get("wallet_reference"):
                reasons.append("provider_or_wallet_reference_required")

        if missing:
            return {"decision": "confirm", "reasons": reasons or ["restricted_action_requires_more_evidence"], "missing": sorted(set(missing))}
        return {"decision": "allow", "reasons": reasons or ["policy_requirements_satisfied"], "missing": []}

    def record(self, action: PocketAction) -> Dict[str, Any]:
        action_dict = action.as_dict()
        decision = self.decide(action)
        previous_hash = self.receipts[-1]["receipt_hash"] if self.receipts else None
        receipt = {
            "schema": "pocket.action_receipt.v1",
            "recorded_at_ms": now_ms(),
            "action": action_dict,
            "decision": decision,
            "previous_hash": previous_hash,
        }
        receipt["receipt_hash"] = sha256(receipt)
        self.actions.append(action_dict)
        self.receipts.append(receipt)
        return receipt

    def export_records(self, name: str = "ledger") -> Dict[str, str]:
        json_path = self.root / f"{name}.json"
        csv_path = self.root / f"{name}.csv"
        receipt_path = self.root / f"{name}.receipt.json"
        json_path.write_text(json.dumps(self.receipts, indent=2, sort_keys=True), encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["receipt_hash", "kind", "title", "decision", "mode", "previous_hash"])
            writer.writeheader()
            for item in self.receipts:
                writer.writerow({
                    "receipt_hash": item["receipt_hash"],
                    "kind": item["action"]["kind"],
                    "title": item["action"]["title"],
                    "decision": item["decision"]["decision"],
                    "mode": item["action"]["mode"],
                    "previous_hash": item["previous_hash"] or "",
                })
        export_receipt = {
            "schema": "pocket.data_export_receipt.v1",
            "exported_at_ms": now_ms(),
            "json_path": str(json_path),
            "csv_path": str(csv_path),
            "record_count": len(self.receipts),
            "json_hash": sha256(json.loads(json_path.read_text(encoding="utf-8"))),
        }
        export_receipt["receipt_hash"] = sha256(export_receipt)
        receipt_path.write_text(json.dumps(export_receipt, indent=2, sort_keys=True), encoding="utf-8")
        return {"json": str(json_path), "csv": str(csv_path), "receipt": str(receipt_path)}


def build_provider_packet(action: PocketAction) -> Dict[str, Any]:
    """Build a provider execution packet without hiding missing proof.

    This is the shape that a real provider adapter can receive. It never stores
    raw secrets or raw card data. The caller must configure credentials outside
    git and pass only references.
    """
    if action.kind not in {"payment_execution", "wallet_execution"}:
        raise ValueError("provider_packet_requires_payment_or_wallet_action")
    if has_raw_secret(action.as_dict()):
        raise ValueError("raw_secret_or_sensitive_material_detected")
    return {
        "schema": "pocket.provider_execution_packet.v1",
        "kind": action.kind,
        "mode": action.mode,
        "title": action.title,
        "requested_by": action.requested_by,
        "provider": action.evidence.get("provider"),
        "provider_reference": action.evidence.get("provider_reference"),
        "wallet_reference": action.evidence.get("wallet_reference"),
        "network_or_rail": action.evidence.get("network_or_rail"),
        "amount": action.evidence.get("amount") or action.evidence.get("amount_or_asset"),
        "currency": action.evidence.get("currency"),
        "approval": action.approval.as_dict() if action.approval else None,
        "body_hash": sha256(action.body),
        "secret_policy": "references_only_no_raw_secret_material",
    }


def demo_ledger() -> Dict[str, Any]:
    ledger = PocketActionLedger()
    approval = OperatorApproval(
        operator_id="alfredo",
        approval_id="operator-approval-demo-001",
        approved_at="2026-08-26T01:16:00-05:00",
        reason="prove restricted action path with explicit evidence",
    )
    ledger.record(PocketAction(
        kind="agent_task",
        title="Prepare beta route task",
        requested_by="pocket-agent",
        mode="beta",
        body={"task": "validate beta.pocketnova.app route contract"},
        evidence={"source": "git", "route_contract": "deploy/cloudflare/pocket-beta-domain.json"},
    ))
    ledger.record(PocketAction(
        kind="production_claim",
        title="Claim beta route is operator-connected",
        requested_by="pocket-agent",
        mode="beta",
        body={"claim": "beta.pocketnova.app is recorded as connected by operator"},
        evidence={
            "deploy_target": "beta.pocketnova.app",
            "verification_url_or_run_id": "operator-provided-domain-route",
            "operator_assertion": "domain and routes already connected on Cloudflare",
        },
        approval=approval,
    ))
    ledger.record(PocketAction(
        kind="data_export",
        title="Export action ledger records",
        requested_by="pocket-agent",
        mode="beta",
        body={"format": ["json", "csv"]},
        evidence={"dataset_id": "pocket-action-ledger", "export_scope": "receipts_only", "destination": "dist/pocket-action-ledger"},
        approval=approval,
    ))
    wallet = PocketAction(
        kind="wallet_execution",
        title="Build provider wallet execution packet",
        requested_by="pocket-agent",
        mode="provider_ready",
        body={"instruction": "provider executes wallet action; POCKET stores receipt"},
        evidence={
            "provider": "operator_configured_provider",
            "wallet_reference": "wallet_ref_operator_managed",
            "network_or_rail": "provider_rail",
            "amount_or_asset": "operator_defined",
        },
        approval=approval,
    )
    wallet_receipt = ledger.record(wallet)
    paths = ledger.export_records()
    return {"receipts": ledger.receipts, "wallet_packet": build_provider_packet(wallet), "export_paths": paths, "last_receipt": wallet_receipt}


if __name__ == "__main__":
    output = demo_ledger()
    print(json.dumps(output, indent=2, sort_keys=True))
