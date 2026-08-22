"""Deterministic ecosystem intelligence for the POCKET host control plane.

The host remains authority for identity, tenant scope, policy and routing. This
module provides inspectable helpers used before model or execution calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class RouteCandidate:
    component: str
    score: float
    actions: tuple[str, ...]
    status: str = "unknown"


def route_intent(intent: str, capabilities: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    tokens = {t for t in intent.lower().replace("_", " ").replace(".", " ").split() if len(t) > 2}
    candidates: list[RouteCandidate] = []
    for cap in capabilities:
        component = str(cap.get("component") or "")
        actions = tuple(map(str, cap.get("actions") or []))
        role = str(cap.get("role") or "")
        text = " ".join((component, role, *actions)).lower().replace("_", " ").replace(".", " ")
        hits = sum(1 for token in tokens if token in text)
        status = str((cap.get("health") or {}).get("status") or cap.get("status") or "unknown")
        health_factor = 1.0 if status in {"active", "healthy", "ready", "protocol-ready"} else 0.75
        score = (hits / max(1, len(tokens))) * health_factor
        candidates.append(RouteCandidate(component, score, actions, status))
    candidates.sort(key=lambda x: (-x.score, x.component))
    best = candidates[0] if candidates else None
    return {
        "selected": best.component if best else None,
        "confidence": round(best.score, 3) if best else 0.0,
        "needs_review": best is None or best.score < 0.25,
        "alternatives": [
            {"component": c.component, "score": round(c.score, 3), "status": c.status}
            for c in candidates[:4]
        ],
    }


def policy_decision(*, request_id: str, action: str, risk_tier: str, authenticated: bool,
                    tenant_match: bool, irreversible: bool = False) -> dict[str, Any]:
    reasons: list[str] = []
    if not authenticated:
        decision = "deny"
        reasons.append("authentication_required")
    elif not tenant_match:
        decision = "deny"
        reasons.append("tenant_scope_mismatch")
    elif risk_tier in {"execute", "write-sensitive", "privileged"} or irreversible:
        decision = "confirm"
        reasons.append("operator_confirmation_required")
    else:
        decision = "allow"
        reasons.append("policy_satisfied")
    return {
        "schema": "nexus.policy-decision.v1",
        "request_id": request_id,
        "action": action,
        "decision": decision,
        "policy_id": "pocket.alpha.default.v1",
        "reasons": reasons,
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }


def aggregate_health(component_health: Iterable[Mapping[str, Any]], *, required: Iterable[str] = ()) -> dict[str, Any]:
    checks = {str(x.get("component")): str(x.get("status") or "unknown") for x in component_health}
    required_set = set(map(str, required))
    unavailable = sorted(k for k, status in checks.items() if status in {"unavailable", "not_ready"})
    missing = sorted(required_set - set(checks))
    degraded = sorted(k for k, status in checks.items() if status == "degraded")
    if missing or unavailable:
        status = "not_ready"
    elif degraded:
        status = "degraded"
    else:
        status = "healthy"
    return {
        "schema": "nexus.health.v1",
        "component": "pocket",
        "status": status,
        "checks": checks,
        "missing_required": missing,
        "unavailable": unavailable,
        "degraded": degraded,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


def classify_release_truth(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Derive release truth from evidence rather than marketing labels."""
    source = bool(evidence.get("source"))
    tests = bool(evidence.get("tests_green"))
    preview = bool(evidence.get("preview_verified"))
    hosted = bool(evidence.get("hosted_verified"))
    if hosted and preview and tests and source:
        state = "hosted"
    elif preview and tests and source:
        state = "preview"
    elif tests and source:
        state = "tested"
    elif source:
        state = "source"
    else:
        state = "unverified"
    return {
        "schema": "nexus.release-evidence.v1",
        "component": str(evidence.get("component") or "unknown"),
        "version": str(evidence.get("version") or "unknown"),
        "truth_state": state,
        "evidence": dict(evidence),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
