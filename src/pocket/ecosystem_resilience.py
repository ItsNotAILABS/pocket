"""Enterprise control-plane resilience helpers for POCKET Host."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets
from typing import Any, Mapping


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def quota_status(*, subject: Mapping[str, Any], window: str, limits: Mapping[str, int | float], usage: Mapping[str, int | float]) -> dict[str, Any]:
    exceeded: list[str] = []
    remaining: dict[str, float] = {}
    for name, raw_limit in limits.items():
        limit = float(raw_limit)
        used = float(usage.get(name, 0))
        if limit < 0:
            raise ValueError(f"invalid_quota:{name}")
        remaining[name] = max(0.0, limit - used)
        if used > limit:
            exceeded.append(name)
    return {
        "schema": "nexus.quota.v1",
        "subject": dict(subject),
        "window": window,
        "limits": dict(limits),
        "usage": dict(usage),
        "remaining": remaining,
        "exceeded": exceeded,
        "allowed": not exceeded,
        "observed_at": _iso(_now()),
    }


def approval_request(*, request_id: str, actor: Mapping[str, Any], scope: Mapping[str, Any], decision: str = "pending", ttl_seconds: int = 300) -> dict[str, Any]:
    if decision not in {"pending", "approved", "denied"}:
        raise ValueError("invalid_approval_decision")
    if ttl_seconds <= 0 or ttl_seconds > 86400:
        raise ValueError("invalid_approval_ttl")
    start = _now()
    return {
        "schema": "nexus.approval.v1",
        "approval_id": "apr_" + secrets.token_hex(12),
        "request_id": request_id,
        "actor": dict(actor),
        "decision": decision,
        "scope": dict(scope),
        "created_at": _iso(start),
        "expires_at": _iso(start + timedelta(seconds=ttl_seconds)),
    }


def idempotency_key(*, tenant_id: str, principal_id: str, action: str, client_key: str) -> str:
    if not all((tenant_id, principal_id, action, client_key)):
        raise ValueError("idempotency_scope_required")
    raw = "|".join((tenant_id, principal_id, action, client_key)).encode("utf-8")
    return "idem_" + hashlib.sha256(raw).hexdigest()


def audit_event(*, request_id: str, actor: Mapping[str, Any], component: str, action: str, target: Mapping[str, Any], outcome: str, policy_id: str | None = None) -> dict[str, Any]:
    if outcome not in {"allowed", "denied", "confirmed", "succeeded", "failed", "cancelled"}:
        raise ValueError("invalid_audit_outcome")
    return {
        "schema": "nexus.audit-event.v1",
        "event_id": "aud_" + secrets.token_hex(12),
        "request_id": request_id,
        "actor": dict(actor),
        "component": component,
        "action": action,
        "target": dict(target),
        "outcome": outcome,
        "policy_id": policy_id,
        "observed_at": _iso(_now()),
    }


def secret_ref(*, provider: str, ref: str, purpose: str, scope: Mapping[str, Any]) -> dict[str, Any]:
    if not provider or not ref or not purpose:
        raise ValueError("secret_reference_fields_required")
    banned = ("sk-", "token=", "password=", "secret=")
    if any(marker in ref.lower() for marker in banned):
        raise ValueError("secret_ref_looks_like_secret_value")
    return {
        "schema": "nexus.secret-ref.v1",
        "provider": provider,
        "ref": ref,
        "purpose": purpose,
        "scope": dict(scope),
    }


def incident(*, severity: str, components: list[str], summary: str, request_id: str | None = None) -> dict[str, Any]:
    if severity not in {"sev1", "sev2", "sev3", "sev4"}:
        raise ValueError("invalid_incident_severity")
    at = _iso(_now())
    return {
        "schema": "nexus.incident.v1",
        "incident_id": "inc_" + secrets.token_hex(10),
        "severity": severity,
        "status": "detected",
        "components": list(dict.fromkeys(components)),
        "summary": summary,
        "request_id": request_id,
        "detected_at": at,
        "timeline": [{"at": at, "event": "detected", "summary": summary}],
    }
