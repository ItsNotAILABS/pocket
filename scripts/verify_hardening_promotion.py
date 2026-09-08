from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROOF = ROOT / "dist" / "proof"
VALIDATOR = ROOT / "scripts" / "validate_technology_garden.py"
RECEIPT = PROOF / "technology-garden-receipt.json"
PRODUCT_GATE = PROOF / "product-gate-receipt.json"


def fail(reason: str) -> None:
    print(json.dumps({"schema": "pocket.hardening-promotion.v1", "promote": False, "reason": reason}, sort_keys=True))
    raise SystemExit(2)


def current_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


if not RECEIPT.exists():
    fail("missing_technology_garden_receipt: run python scripts/validate_technology_garden.py")
receipt = json.loads(RECEIPT.read_text())
validator_hash = hashlib.sha256(VALIDATOR.read_bytes()).hexdigest()
if receipt.get("status") != "passed":
    fail("technology_garden_not_passed")
if receipt.get("validator_sha256") != validator_hash:
    fail("validator_hash_mismatch")
if int(receipt.get("assertions", 0)) < int(receipt.get("minimum", 128)):
    fail("assertion_threshold_not_met")
if receipt.get("integration_roundtrip_tested") is not True:
    fail("channel_roundtrip_not_attested")
if receipt.get("authorization_semantics_tested") is not True:
    fail("authorization_semantics_not_attested")

if not PRODUCT_GATE.exists():
    fail("missing_product_gate_receipt")
product = json.loads(PRODUCT_GATE.read_text())
if product.get("schema") != "pocket.product-gate-receipt.v1":
    fail("product_gate_schema")
if product.get("status") != "passed":
    fail("product_gate_not_passed")
head = current_head()
if not head:
    fail("cannot_resolve_git_head")
if product.get("head_sha") != head:
    fail("product_gate_wrong_head")

print(json.dumps({
    "schema": "pocket.hardening-promotion.v1",
    "promote": True,
    "head_sha": head,
    "validator_sha256": validator_hash,
    "technology_assertions": receipt["assertions"],
    "product_gate_receipt": str(PRODUCT_GATE.relative_to(ROOT)),
}, indent=2, sort_keys=True))
