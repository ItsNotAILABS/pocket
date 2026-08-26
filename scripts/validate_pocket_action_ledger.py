#!/usr/bin/env python3
"""Validate POCKET executable action ledger behavior."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "pocket" / "action_ledger.py"
OUT_DIR = ROOT / "dist" / "pocket-action-ledger"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_module():
    spec = importlib.util.spec_from_file_location("pocket_action_ledger", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable_to_load_action_ledger_module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pocket_action_ledger"] = mod
    spec.loader.exec_module(mod)
    return mod


def digest(value):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    mod = load_module()
    output = mod.demo_ledger()
    receipts = output["receipts"]
    wallet_packet = output["wallet_packet"]

    checks = []
    def check(name, ok, detail=None):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    check("receipt_count", len(receipts) == 4, len(receipts))
    check("agent_task_allowed", receipts[0]["decision"]["decision"] == "allow", receipts[0]["decision"])
    check("production_claim_has_evidence", receipts[1]["decision"]["decision"] == "allow", receipts[1]["decision"])
    check("data_export_has_approval", receipts[2]["decision"]["decision"] == "allow", receipts[2]["decision"])
    check("wallet_execution_provider_ready", receipts[3]["decision"]["decision"] == "allow", receipts[3]["decision"])
    check("receipt_chain_linked", receipts[1]["previous_hash"] == receipts[0]["receipt_hash"] and receipts[3]["previous_hash"] == receipts[2]["receipt_hash"])
    check("provider_packet_no_raw_secret_policy", wallet_packet["secret_policy"] == "references_only_no_raw_secret_material", wallet_packet)
    check("export_files_written", all(Path(path).exists() for path in output["export_paths"].values()), output["export_paths"])

    denied = mod.PocketAction(
        kind="payment_execution",
        title="Bad payment with raw card",
        requested_by="validator",
        mode="production",
        body={"card": "4111111111111111", "cvv": "123"},
        evidence={"provider": "x", "provider_reference": "x", "amount": "1.00", "currency": "USD"},
    )
    ledger = mod.PocketActionLedger(OUT_DIR / "negative")
    denied_receipt = ledger.record(denied)
    check("raw_card_denied", denied_receipt["decision"]["decision"] == "deny", denied_receipt["decision"])

    missing = mod.PocketAction(
        kind="wallet_execution",
        title="Missing approval wallet action",
        requested_by="validator",
        mode="provider_ready",
        body={"instruction": "wallet action"},
        evidence={"provider": "operator_configured_provider", "wallet_reference": "wallet_ref", "network_or_rail": "provider_rail", "amount_or_asset": "operator_defined"},
    )
    confirm_receipt = ledger.record(missing)
    check("wallet_missing_approval_confirm", confirm_receipt["decision"]["decision"] == "confirm", confirm_receipt["decision"])

    passed = all(item["ok"] for item in checks)
    validation = {
        "schema": "pocket.action_ledger.validation.v1",
        "passed": passed,
        "module": str(MODULE.relative_to(ROOT)),
        "checks": checks,
        "receipt_count": len(receipts),
        "wallet_packet_hash": digest(wallet_packet),
    }
    validation["receipt_hash"] = digest(validation)
    receipt_path = OUT_DIR / "validation-receipt.json"
    receipt_path.write_text(json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
