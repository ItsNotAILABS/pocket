#!/usr/bin/env python3
from pocket.ecosystem_intelligence import aggregate_health, classify_release_truth, policy_decision, route_intent

caps = [
    {"component": "pocket-agent", "role": "long running execution", "actions": ["agent.run", "agent.capsule"], "status": "active"},
    {"component": "pocket-voice", "role": "voice conversation control", "actions": ["voice.turn", "voice.snap"], "status": "active"},
]
r = route_intent("run a long agent task", caps)
assert r["selected"] == "pocket-agent", r
assert r["needs_review"] is False, r

p = policy_decision(request_id="r1", action="agent.run", risk_tier="execute", authenticated=True, tenant_match=True)
assert p["decision"] == "confirm", p
p2 = policy_decision(request_id="r2", action="voice.turn", risk_tier="read", authenticated=False, tenant_match=True)
assert p2["decision"] == "deny", p2

h = aggregate_health([
    {"component": "pocket-agent", "status": "healthy"},
    {"component": "pocket-voice", "status": "degraded"},
], required=["pocket-agent", "pocket-voice"])
assert h["status"] == "degraded", h

truth = classify_release_truth({"component": "demo", "version": "1", "source": True, "tests_green": True, "preview_verified": False})
assert truth["truth_state"] == "tested", truth

print("POCKET ecosystem intelligence gate: PASS")
