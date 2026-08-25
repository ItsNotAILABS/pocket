#!/usr/bin/env python3
"""Validate POCKET / MESIE multi-AI agent protocol files.

This validator keeps AGENTS.md from becoming only prose. It checks that the
repository-level operating contract names the required protocols, preserves
multi-AI assumptions, and keeps safety boundaries visible for future agents.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
MANIFEST = ROOT / "protocols" / "pocket-agent-protocol.manifest.json"
OUT = ROOT / "dist" / "agents-protocol" / "validation-receipt.json"


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def require(condition: bool, code: str, detail: str, checks: list[dict[str, Any]]) -> None:
    checks.append({"code": code, "ok": bool(condition), "detail": detail})


def main() -> int:
    checks: list[dict[str, Any]] = []
    agents_text = AGENTS.read_text(encoding="utf-8") if AGENTS.exists() else ""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}

    require(AGENTS.exists(), "agents_file_exists", "AGENTS.md exists at repository root", checks)
    require(MANIFEST.exists(), "manifest_exists", "Machine-readable protocol manifest exists", checks)
    require(manifest.get("schema") == "pocket.agent_protocol_manifest.v1", "manifest_schema", "Manifest schema is pocket.agent_protocol_manifest.v1", checks)
    require("Multiple AIs" in agents_text or "multiple AIs" in agents_text, "multi_ai_assumption", "AGENTS.md explicitly names multiple AIs", checks)
    require("POCKET is not a single-chat project" in agents_text, "not_single_chat", "AGENTS.md rejects single-chat framing", checks)
    require("MESIE-EVIDENCE" in agents_text, "mesie_evidence_named", "MESIE evidence protocol is named", checks)
    require("MEDINA-SUBAGENT-MESH" in agents_text, "mesh_protocol_named", "MEDINA Subagent Mesh protocol is named", checks)
    require("POCKET-POLICY" in agents_text, "policy_protocol_named", "POCKET policy protocol is named", checks)
    require("No raw card data" in agents_text or "raw card data" in agents_text, "raw_card_boundary", "Raw card data boundary is present", checks)
    require("private keys" in agents_text or "private key" in agents_text, "private_key_boundary", "Private key boundary is present", checks)
    require("HANDOFF" in agents_text, "handoff_block", "Handoff block is present", checks)
    require("DONE / OPEN / BLOCKED" in agents_text, "reporting_contract", "Final status reporting contract is present", checks)

    required_protocols = manifest.get("required_protocols", [])
    protocol_ids = {p.get("id") for p in required_protocols if isinstance(p, dict)}
    for required in ["MEDINA-SUBAGENT-MESH", "MESIE-EVIDENCE", "POCKET-PRODUCT", "POCKET-POLICY", "POCKET-HANDOFF"]:
        require(required in protocol_ids, f"manifest_protocol_{required.lower().replace('-', '_')}", f"Manifest includes {required}", checks)

    for field in ["agent_classes", "protected_surfaces", "deny_patterns", "confirm_required_for"]:
        require(isinstance(manifest.get(field), list) and len(manifest.get(field, [])) > 0, f"manifest_{field}", f"Manifest has non-empty {field}", checks)

    ok = all(check["ok"] for check in checks)
    receipt = {
        "schema": "mesie.receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "subject": "pocket.agent_protocol_manifest",
        "mode": "repository_protocol_validation",
        "inputs": [str(AGENTS.relative_to(ROOT)), str(MANIFEST.relative_to(ROOT))],
        "outputs": [str(OUT.relative_to(ROOT))],
        "checks": checks,
        "decision": "pass" if ok else "fail",
        "hashes": {
            "AGENTS.md": sha256_text(agents_text),
            "protocols/pocket-agent-protocol.manifest.json": sha256_text(stable_json(manifest)),
        },
    }
    receipt["hash"] = sha256_text(stable_json({k: v for k, v in receipt.items() if k != "hash"}))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"decision": receipt["decision"], "checks": len(checks), "receipt": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
