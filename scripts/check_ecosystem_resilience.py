#!/usr/bin/env python3
from pocket.ecosystem_resilience import approval_request, audit_event, idempotency_key, incident, quota_status, secret_ref

q = quota_status(
    subject={"tenant_id": "t1", "api_key": "key-ref"},
    window="1h",
    limits={"requests": 100, "cost_usd": 5},
    usage={"requests": 90, "cost_usd": 2},
)
assert q["schema"] == "nexus.quota.v1"
assert q["allowed"] is True
assert q["remaining"]["requests"] == 10

a = approval_request(request_id="r1", actor={"id": "u1", "type": "user"}, scope={"tenant_id": "t1", "action": "deploy"})
assert a["schema"] == "nexus.approval.v1"
assert a["decision"] == "pending"

k1 = idempotency_key(tenant_id="t1", principal_id="u1", action="host.deploy", client_key="abc")
k2 = idempotency_key(tenant_id="t1", principal_id="u1", action="host.deploy", client_key="abc")
assert k1 == k2 and k1.startswith("idem_")

aud = audit_event(request_id="r1", actor={"id": "u1"}, component="pocket", action="host.deploy", target={"project_id": "p1"}, outcome="confirmed", policy_id="p1")
assert aud["schema"] == "nexus.audit-event.v1"

ref = secret_ref(provider="cloudflare", ref="binding:OPENAI_API_KEY", purpose="voice-provider", scope={"tenant_id": "t1"})
assert ref["schema"] == "nexus.secret-ref.v1"
assert "OPENAI_API_KEY" in ref["ref"]

inc = incident(severity="sev3", components=["pocket", "pocket-voice"], summary="provider degradation", request_id="r1")
assert inc["schema"] == "nexus.incident.v1"
assert inc["status"] == "detected"

print("POCKET ecosystem resilience gate: PASS")
