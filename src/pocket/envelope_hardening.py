from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Iterable, List

# Derived diagnostics are intentionally outside the signed/canonical envelope body.
# They may be attached after sealing without invalidating the message digest.
DIGEST_EXCLUDED_FIELDS = frozenset({"canonical_digest", "hardening_validation"})
SIDE_EFFECT_APPROVALS = frozenset({"confirm", "approved", "deny"})


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def digest_payload(message: Dict[str, Any]) -> Dict[str, Any]:
    """Return the exact semantic envelope body covered by canonical_digest."""
    return {k: v for k, v in message.items() if k not in DIGEST_EXCLUDED_FIELDS}


def hardened_envelope(message: Dict[str, Any], *, ttl_s: int = 300, now: float | None = None) -> Dict[str, Any]:
    now = float(time.time() if now is None else now)
    required = ("schema", "message_id", "request_id", "from", "to", "channel", "kind", "state")
    missing = [k for k in required if not message.get(k)]
    if missing:
        return {"ok": False, "authorized": False, "terminal": False, "violations": ["missing:" + ",".join(missing)]}
    if ttl_s < 1 or ttl_s > 86400:
        return {"ok": False, "authorized": False, "terminal": False, "violations": ["ttl_out_of_bounds"]}

    out = dict(message)
    out.pop("hardening_validation", None)
    out.setdefault("created_at", now)
    out["expires_at"] = float(out["created_at"]) + ttl_s
    out.setdefault(
        "nonce",
        hashlib.sha256(f"{out['message_id']}:{out['request_id']}:{out['created_at']}".encode()).hexdigest()[:24],
    )

    side_effect = bool(out.get("side_effect"))
    approval = str(out.get("approval") or "")
    if side_effect and approval not in SIDE_EFFECT_APPROVALS:
        return {
            "ok": False,
            "authorized": False,
            "terminal": False,
            "violations": ["side_effect_requires_explicit_approval"],
        }

    out["canonical_digest"] = canonical_digest(digest_payload(out))
    return {
        "ok": True,
        "authorized": bool(side_effect and approval == "approved") if side_effect else True,
        "terminal": bool(side_effect and approval == "deny"),
        "envelope": out,
    }


def validate_hardened_envelope(
    message: Dict[str, Any],
    *,
    now: float | None = None,
    seen_nonces: Iterable[str] = (),
) -> Dict[str, Any]:
    """Validate integrity, freshness, replay state, and side-effect authorization state.

    `ok` means the envelope is structurally/integrity valid and is not a terminal denial.
    `authorized` is the separate execution decision. Consequential execution MUST require
    both `ok is True` and `authorized is True`.
    """
    now = float(time.time() if now is None else now)
    violations: List[str] = []
    for key in (
        "schema",
        "message_id",
        "request_id",
        "from",
        "to",
        "channel",
        "kind",
        "state",
        "created_at",
        "expires_at",
        "nonce",
        "canonical_digest",
    ):
        if message.get(key) in (None, ""):
            violations.append(f"missing:{key}")
    if violations:
        return {"ok": False, "authorized": False, "terminal": False, "violations": violations}

    if float(message["expires_at"]) < now:
        violations.append("expired")
    if message["nonce"] in set(seen_nonces):
        violations.append("replay")

    side_effect = bool(message.get("side_effect"))
    approval = str(message.get("approval") or "")
    terminal = False
    authorized = not side_effect
    if side_effect:
        if approval not in SIDE_EFFECT_APPROVALS:
            violations.append("approval_invalid")
        elif approval == "deny":
            violations.append("approval_denied")
            terminal = True
        elif approval == "approved":
            authorized = True
        elif approval == "confirm":
            authorized = False

    expected = canonical_digest(digest_payload(message))
    if expected != message["canonical_digest"]:
        violations.append("digest_mismatch")

    return {
        "ok": not violations,
        "authorized": bool(not violations and authorized),
        "terminal": terminal,
        "violations": violations,
    }


def execution_allowed(validation: Dict[str, Any]) -> bool:
    """Single guard for consequential routing."""
    return bool(validation.get("ok") and validation.get("authorized") and not validation.get("terminal"))
