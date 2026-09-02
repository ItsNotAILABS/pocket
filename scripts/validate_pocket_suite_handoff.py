#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "deploy" / "cloudflare" / "pocket-suite-handoff.json"
SHOWCASE = ROOT / "web" / "pocket-suite" / "index.html"
SDK = ROOT / "sdk" / "pocket-suite-client.js"
OUT = ROOT / "dist" / "pocket-suite-handoff" / "validation-receipt.json"

REQUIRED_ACTIONS = {"agent_task", "production_claim", "data_export", "payment_execution", "wallet_execution"}


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    checks = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks.append({"check": "manifest_exists", "ok": MANIFEST.exists()})
    checks.append({"check": "canonical_beta_url", "ok": manifest.get("canonical_beta_url") == "https://beta.pocketnova.app"})
    checks.append({"check": "all_suite_repos", "ok": set(manifest.get("repos", {})) >= {"platform", "voice_to_text", "agent"}})
    checks.append({"check": "actions_complete", "ok": REQUIRED_ACTIONS.issubset(set(manifest.get("action_contracts", [])))})
    checks.append({"check": "showcase_exists", "ok": SHOWCASE.exists() and "POCKET Suite" in SHOWCASE.read_text(encoding="utf-8")})
    sdk_text = SDK.read_text(encoding="utf-8")
    checks.append({"check": "sdk_blocks_sensitive_fields", "ok": "forbidSensitive" in sdk_text and "requestPaymentExecution" in sdk_text and "requestWalletExecution" in sdk_text})
    checks.append({"check": "deployment_prompt_present", "ok": "deployment_prompt_for_claude_or_cloud" in manifest})
    ok = all(item["ok"] for item in checks)
    receipt = {
        "schema": "pocket.suite_handoff.validation_receipt.v1",
        "ok": ok,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_beta_url": manifest.get("canonical_beta_url"),
        "checks": checks,
        "artifacts": {
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "showcase": str(SHOWCASE.relative_to(ROOT)),
            "sdk": str(SDK.relative_to(ROOT)),
        },
        "hash": sha256_text(json.dumps(checks, sort_keys=True)),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
