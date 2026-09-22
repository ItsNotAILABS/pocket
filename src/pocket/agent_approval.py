"""Agentic approval: short-code authorization primitive for POCKET.

Protocol: POCKET-AGENTIC-APPROVAL/1.0

An untrusted surface (device, website, app) that cannot prove identity shows
a short-lived code. A trusted approver — by default the owner's agent,
acting from a trusted channel — approves the EXACT code match. Approval
writes a persistent binding (device/app -> granted scope/capability) so the
flow is approve-once. Bindings are revocable.

Posture extends POCKET-DEVICE-PAIR/1.0 (code + expiry + revocable grant).
Where device-pair redeems a code with a WebAuthn ceremony into a
``portal_device`` principal, agentic approval redeems a code with an
approver's explicit decision into a scoped capability binding. The code
mechanics (6 chars, 10-minute TTL, single-use, exact match, file-backed
JSON store at ~/.pocket/<surface>/) are intentionally parallel so a future
device-pair flow can issue through this service without a fork.

Policy: who can approve what.
  - Each request carries ``policy: {"approvers": [...], "quorum": 1}``.
  - Default approvers: ["owner-agent"]. approve() refuses any approver not
    on the request's list.
  - Designed for future approvers ("human-confirm", quorum > 1): the
    exact-match + receipt mechanics do not change; only the approver
    allowlist and quorum accounting extend.

Security rules (mirrored from the artifact-owner-unlock reference):
  - Exact code match only. Mismatch is a denial, never fuzzy, never a hint
    about which request it was close to.
  - Codes are normalized (strip whitespace, uppercase) then compared with
    secrets.compare_digest. Normalization is documented, not fuzzy.
  - Expired or already-decided requests can never be approved.
  - Receipts record a sha256 of the code, never the code itself.
  - list_pending() masks codes (first2 + "**" + last2).

Storage: ~/.pocket/agent_approval/ (override with POCKET_AGENT_APPROVAL_HOME)
  requests.json  — approval request records
  bindings.json  — persistent capability bindings
  receipts/      — MESIE receipts (mesie.receipt.v1), one per event

Stdlib only. Atomic renames for concurrent-agent safety.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROTOCOL = "POCKET-AGENTIC-APPROVAL/1.0"
CODE_LEN = 6
DEFAULT_TTL_S = 600
# Unambiguous alphabet: no 0/O, no 1/I/L.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
DEFAULT_APPROVERS = ["owner-agent"]
RECEIPT_SCHEMA = "mesie.receipt.v1"


def _root() -> Path:
    override = os.environ.get("POCKET_AGENT_APPROVAL_HOME", "").strip()
    base = Path(override) if override else Path.home() / ".pocket" / "agent_approval"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _receipts_dir() -> Path:
    d = _root() / "receipts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_list(name: str) -> List[Dict[str, Any]]:
    path = _root() / name
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_list(name: str, rows: List[Dict[str, Any]]) -> None:
    path = _root() / name
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except Exception:
        pass
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def _now() -> float:
    return time.time()


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _sha256(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _new_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LEN))


def _normalize_code(code: str) -> str:
    return "".join((code or "").split()).upper()


def _code_hint(code: str) -> str:
    c = _normalize_code(code)
    return (c[:2] + "**" + c[-2:]) if len(c) == CODE_LEN else "******"


def _write_receipt(event: str, inputs: Dict[str, Any], outputs: Dict[str, Any],
                   checks: List[str]) -> Dict[str, Any]:
    body = {
        "schema": RECEIPT_SCHEMA,
        "generated_at": _iso(_now()),
        "subject": "pocket.agent-approval." + event,
        "protocol": PROTOCOL,
        "mode": "local",
        "inputs": inputs,
        "outputs": outputs,
        "checks": checks,
    }
    body["hash"] = _sha256({k: v for k, v in body.items() if k != "hash"})
    name = "%s-%s-%s.json" % (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"),
        event.replace(".", "-"),
        secrets.token_hex(4),
    )
    (_receipts_dir() / name).write_text(json.dumps(body, indent=2), encoding="utf-8")
    return body


# ---------------------------------------------------------------- requests


def issue(*, device_id: str, app_id: str, scope: str, capability: str,
          requested_by: str = "", ttl_s: int = DEFAULT_TTL_S,
          approvers: Optional[List[str]] = None, note: str = "") -> Dict[str, Any]:
    """Issue a new approval request. Returns the code (issuance channel)."""
    device_id = (device_id or "").strip()
    app_id = (app_id or "").strip()
    scope = (scope or "").strip()
    capability = (capability or "").strip()
    if not device_id or not app_id or not scope or not capability:
        return {"ok": False, "error": "device_id, app_id, scope, capability are all required"}
    ttl = max(1, int(ttl_s or DEFAULT_TTL_S))
    now = _now()
    code = _new_code()
    rec = {
        "id": str(uuid.uuid4()),
        "code": code,
        "code_sha256": _sha256(code),
        "device_id": device_id,
        "app_id": app_id,
        "scope": scope,
        "capability": capability,
        "status": "pending",
        "requested_by": requested_by or "",
        "note": note or "",
        "policy": {"approvers": list(approvers) if approvers else list(DEFAULT_APPROVERS),
                   "quorum": 1},
        "created_at": now,
        "created_at_iso": _iso(now),
        "expires_at": now + ttl,
        "expires_at_iso": _iso(now + ttl),
        "ttl_s": ttl,
        "decided_at": None,
        "approved_by": None,
    }
    rows = _load_list("requests.json")
    rows.append(rec)
    _save_list("requests.json", rows)
    _write_receipt(
        "request.issued",
        {"device_id": device_id, "app_id": app_id, "scope": scope,
         "capability": capability, "code_sha256": rec["code_sha256"],
         "code_hint": _code_hint(code), "ttl_s": ttl},
        {"request_id": rec["id"], "expires_at_iso": rec["expires_at_iso"]},
        ["code is %d chars from unambiguous alphabet" % CODE_LEN,
         "single-use pending request persisted",
         "raw code never written to receipts"],
    )
    return {"ok": True, "id": rec["id"], "code": code,
            "expires_at_iso": rec["expires_at_iso"], "ttl_s": ttl,
            "device_id": device_id, "app_id": app_id,
            "scope": scope, "capability": capability}


def sweep() -> Dict[str, Any]:
    """Mark pending requests past expiry as expired. Returns count."""
    now = _now()
    rows = _load_list("requests.json")
    n = 0
    for r in rows:
        if r.get("status") == "pending" and now > float(r.get("expires_at") or 0):
            r["status"] = "expired"
            r["decided_at"] = now
            n += 1
    if n:
        _save_list("requests.json", rows)
    return {"ok": True, "expired": n}


def list_pending() -> Dict[str, Any]:
    """Pending, non-expired requests. Codes are masked."""
    sweep()
    rows = []
    for r in _load_list("requests.json"):
        if r.get("status") != "pending":
            continue
        rows.append({
            "id": r.get("id"),
            "code_hint": _code_hint(str(r.get("code") or "")),
            "device_id": r.get("device_id"),
            "app_id": r.get("app_id"),
            "scope": r.get("scope"),
            "capability": r.get("capability"),
            "requested_by": r.get("requested_by"),
            "note": r.get("note"),
            "approvers": (r.get("policy") or {}).get("approvers"),
            "created_at_iso": r.get("created_at_iso"),
            "expires_at_iso": r.get("expires_at_iso"),
        })
    return {"ok": True, "requests": rows, "count": len(rows)}


def _find_pending(rows: List[Dict[str, Any]], code: str) -> Optional[Dict[str, Any]]:
    norm = _normalize_code(code)
    if len(norm) != CODE_LEN:
        return None
    for r in rows:
        if r.get("status") != "pending":
            continue
        if secrets.compare_digest(_normalize_code(str(r.get("code") or "")), norm):
            return r
    return None


def approve(*, code: str, approver: str = "owner-agent") -> Dict[str, Any]:
    """Approve the pending request whose code matches EXACTLY.

    Mismatch, expiry, or wrong approver => denial. Never fuzzy.
    """
    approver = (approver or "").strip() or "owner-agent"
    sweep()
    rows = _load_list("requests.json")
    rec = _find_pending(rows, code)
    if rec is None:
        _write_receipt(
            "request.denied",
            {"attempt_code_sha256": _sha256(_normalize_code(code)),
             "attempt_code_hint": _code_hint(code), "approver": approver,
             "reason": "no pending request matches that code"},
            {"matched": False},
            ["exact-match only: mismatch is a denial",
             "attempted code recorded as hash, never plaintext"],
        )
        return {"ok": False, "error": "no pending request matches that code"}
    allowed = (rec.get("policy") or {}).get("approvers") or list(DEFAULT_APPROVERS)
    if approver not in allowed:
        _write_receipt(
            "request.denied",
            {"request_id": rec["id"], "approver": approver,
             "allowed_approvers": allowed, "reason": "approver not authorized"},
            {"matched": True, "authorized": False},
            ["policy: approver must be on the request allowlist"],
        )
        return {"ok": False, "error": "approver '%s' is not authorized for this request" % approver}
    now = _now()
    rec["status"] = "approved"
    rec["decided_at"] = now
    rec["approved_by"] = approver
    binding = {
        "id": str(uuid.uuid4()),
        "request_id": rec["id"],
        "device_id": rec["device_id"],
        "app_id": rec["app_id"],
        "scope": rec["scope"],
        "capability": rec["capability"],
        "approved_by": approver,
        "approved_at": now,
        "approved_at_iso": _iso(now),
        "revoked": False,
        "revoked_at": None,
    }
    _save_list("requests.json", rows)
    brows = _load_list("bindings.json")
    brows.append(binding)
    _save_list("bindings.json", brows)
    _write_receipt(
        "request.approved",
        {"request_id": rec["id"], "device_id": rec["device_id"],
         "app_id": rec["app_id"], "scope": rec["scope"],
         "capability": rec["capability"], "approver": approver,
         "code_sha256": rec["code_sha256"]},
        {"binding_id": binding["id"], "approved_at_iso": binding["approved_at_iso"]},
        ["exact code match via constant-time compare",
         "request consumed (single-use)",
         "persistent binding written"],
    )
    return {"ok": True, "request_id": rec["id"], "binding_id": binding["id"],
            "device_id": binding["device_id"], "app_id": binding["app_id"],
            "scope": binding["scope"], "capability": binding["capability"],
            "approved_by": approver}


def deny(*, code: str, approver: str = "owner-agent", reason: str = "") -> Dict[str, Any]:
    """Explicitly deny a pending request (exact code match)."""
    approver = (approver or "").strip() or "owner-agent"
    sweep()
    rows = _load_list("requests.json")
    rec = _find_pending(rows, code)
    if rec is None:
        return {"ok": False, "error": "no pending request matches that code"}
    now = _now()
    rec["status"] = "denied"
    rec["decided_at"] = now
    rec["approved_by"] = approver
    _save_list("requests.json", rows)
    _write_receipt(
        "request.denied",
        {"request_id": rec["id"], "approver": approver,
         "reason": reason or "explicit denial"},
        {"matched": True},
        ["explicit denial recorded; no binding written"],
    )
    return {"ok": True, "request_id": rec["id"], "status": "denied"}


# ---------------------------------------------------------------- bindings


def list_bindings(*, include_revoked: bool = True) -> Dict[str, Any]:
    rows = []
    for b in _load_list("bindings.json"):
        if b.get("revoked") and not include_revoked:
            continue
        rows.append({
            "id": b.get("id"),
            "device_id": b.get("device_id"),
            "app_id": b.get("app_id"),
            "scope": b.get("scope"),
            "capability": b.get("capability"),
            "approved_by": b.get("approved_by"),
            "approved_at_iso": b.get("approved_at_iso"),
            "revoked": bool(b.get("revoked")),
            "revoked_at_iso": _iso(b["revoked_at"]) if b.get("revoked_at") else None,
        })
    return {"ok": True, "bindings": rows, "count": len(rows)}


def revoke_binding(*, binding_id: str = "", device_id: str = "",
                   app_id: str = "", approver: str = "owner-agent") -> Dict[str, Any]:
    """Revoke bindings by id, or all live bindings for a device (+optional app)."""
    approver = (approver or "").strip() or "owner-agent"
    bid = (binding_id or "").strip()
    did = (device_id or "").strip()
    aid = (app_id or "").strip()
    if not bid and not did:
        return {"ok": False, "error": "binding_id or device_id is required"}
    now = _now()
    rows = _load_list("bindings.json")
    revoked: List[str] = []
    for b in rows:
        if b.get("revoked"):
            continue
        hit = (bid and b.get("id") == bid) or (
            did and b.get("device_id") == did and (not aid or b.get("app_id") == aid))
        if hit:
            b["revoked"] = True
            b["revoked_at"] = now
            b["revoked_by"] = approver
            revoked.append(str(b.get("id")))
    if revoked:
        _save_list("bindings.json", rows)
        _write_receipt(
            "binding.revoked",
            {"approver": approver, "binding_id": bid, "device_id": did, "app_id": aid},
            {"revoked_ids": revoked, "count": len(revoked)},
            ["revoked bindings no longer satisfy check()"],
        )
    return {"ok": True, "revoked": revoked, "count": len(revoked)}


def check(*, device_id: str, app_id: str, scope: str,
          capability: str = "") -> Dict[str, Any]:
    """Does a live binding grant this device/app the scope (+capability)?"""
    did = (device_id or "").strip()
    aid = (app_id or "").strip()
    sc = (scope or "").strip()
    cap = (capability or "").strip()
    for b in _load_list("bindings.json"):
        if b.get("revoked"):
            continue
        if b.get("device_id") != did or b.get("app_id") != aid:
            continue
        bscope = str(b.get("scope") or "")
        if bscope != "*" and bscope != sc:
            continue
        if cap and str(b.get("capability") or "") != cap:
            continue
        return {"ok": True, "granted": True, "binding_id": b.get("id"),
                "scope": b.get("scope"), "capability": b.get("capability"),
                "approved_by": b.get("approved_by")}
    return {"ok": True, "granted": False}
