#!/usr/bin/env python3
"""Validate POCKET beta domain and Cloudflare route contract."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "deploy" / "cloudflare" / "pocket-beta-domain.json"
README = ROOT / "README.md"
OUT = ROOT / "dist" / "pocket-beta-domain" / "validation-receipt.json"

REQUIRED_HOST = "beta.pocketnova.app"
REQUIRED_ROUTE = "beta.pocketnova.app/*"
REQUIRED_SCHEMA = "pocket.cloudflare_domain.v1"
REQUIRED_PUBLIC_PATHS = [
    "/",
    "/desk",
    "/work",
    "/mail",
    "/docs",
    "/install",
    "/get",
    "/developers",
    "/health",
    "/v1/catalog",
    "/v1/ready",
    "/v1/class",
]
REQUIRED_BOUNDARY_FLAGS = {
    "secrets_in_git": False,
    "production_claim": False,
    "beta_public_surface": True,
    "customer_data_export": False,
    "payment_or_wallet_execution": False,
}


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def fail(message: str) -> dict:
    return {"ok": False, "message": message}


def ok(message: str, detail: object | None = None) -> dict:
    result = {"ok": True, "message": message}
    if detail is not None:
        result["detail"] = detail
    return result


def main() -> int:
    checks: list[dict] = []

    if not CONTRACT.exists():
        checks.append(fail("missing deploy/cloudflare/pocket-beta-domain.json"))
        contract: dict = {}
    else:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        checks.append(ok("domain contract exists"))

    checks.append(ok("README exists") if README.exists() else fail("README.md missing"))

    checks.append(
        ok("schema is correct")
        if contract.get("schema") == REQUIRED_SCHEMA
        else fail("schema mismatch")
    )
    checks.append(
        ok("canonical host is beta.pocketnova.app")
        if contract.get("canonical_host") == REQUIRED_HOST
        else fail("canonical host mismatch")
    )
    checks.append(
        ok("canonical origin is https beta host")
        if contract.get("canonical_origin") == f"https://{REQUIRED_HOST}"
        else fail("canonical origin mismatch")
    )

    route_patterns = [route.get("pattern") for route in contract.get("cloudflare", {}).get("routes", [])]
    checks.append(
        ok("Cloudflare beta route is declared", route_patterns)
        if REQUIRED_ROUTE in route_patterns
        else fail("missing beta.pocketnova.app/* Cloudflare route")
    )

    public_paths = [route.get("path") for route in contract.get("public_routes", [])]
    missing_paths = [path for path in REQUIRED_PUBLIC_PATHS if path not in public_paths]
    checks.append(
        ok("required beta public routes are declared", public_paths)
        if not missing_paths
        else fail(f"missing public routes: {', '.join(missing_paths)}")
    )

    required_secrets = set(contract.get("required_secrets", []))
    missing_required_secret_refs = [
        secret for secret in ["CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"] if secret not in required_secrets
    ]
    checks.append(
        ok("Cloudflare secret references are declared without values")
        if not missing_required_secret_refs
        else fail(f"missing secret references: {', '.join(missing_required_secret_refs)}")
    )

    boundaries = contract.get("boundaries", {})
    boundary_failures = [
        key for key, expected in REQUIRED_BOUNDARY_FLAGS.items() if boundaries.get(key) is not expected
    ]
    checks.append(
        ok("domain boundaries are explicit and safe", boundaries)
        if not boundary_failures
        else fail(f"boundary mismatch: {', '.join(boundary_failures)}")
    )

    raw_contract = CONTRACT.read_text(encoding="utf-8") if CONTRACT.exists() else ""
    forbidden_secret_shapes = ["sk-", "ghp_", "gho_", "-----BEGIN", "api_key=", "API_KEY="]
    leaked = [shape for shape in forbidden_secret_shapes if shape in raw_contract]
    checks.append(
        ok("no obvious secret material in domain contract")
        if not leaked
        else fail(f"possible secret material present: {', '.join(leaked)}")
    )

    passed = all(check["ok"] for check in checks)
    receipt = {
        "schema": "pocket.beta_domain.validation_receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "subject": REQUIRED_HOST,
        "mode": "beta-domain-contract",
        "passed": passed,
        "checks": checks,
        "contract_hash": stable_hash(contract),
    }
    receipt["receipt_hash"] = stable_hash(receipt)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"pocket beta domain validation: {'PASS' if passed else 'FAIL'}")
    print(f"receipt: {OUT.relative_to(ROOT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
