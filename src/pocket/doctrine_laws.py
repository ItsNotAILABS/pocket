"""Executable doctrine laws for POCKET communication and execution.

These laws constrain agents, foundation models, voice, tools, and transports.
They are architectural invariants, not claims about consciousness or physics.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

LAW_SET: tuple[Dict[str, Any], ...] = (
    {"id":"L1","name":"Continuity Law","rule":"Every consequential operation preserves request, session, project, and causal parent identifiers across hops."},
    {"id":"L2","name":"Addressability Law","rule":"Every speaking or acting node has an explicit identity and destination; anonymous privileged broadcast is invalid."},
    {"id":"L3","name":"Channel Sovereignty Law","rule":"A channel carries a declared semantic class, risk tier, retention rule, and allowed participants."},
    {"id":"L4","name":"Translation Law","rule":"Cross-plane messages are translated into versioned envelopes; transports may change while meaning and identifiers remain stable."},
    {"id":"L5","name":"Evidence Law","rule":"Execution, benchmark, deployment, and release claims require attributable evidence or must remain proposal/state language."},
    {"id":"L6","name":"Bounded Authority Law","rule":"No agent, model, channel, or transport gains authority merely by producing a recommendation or message."},
    {"id":"L7","name":"Failure Truth Law","rule":"Failure, timeout, denial, uncertainty, and partial completion remain first-class states and cannot be rewritten as success."},
    {"id":"L8","name":"Recurrence Law","rule":"Unresolved work may recur only with preserved state, bounded retry policy, and visible ownership."},
    {"id":"L9","name":"Model Non-Authority Law","rule":"Foundation models propose or compute; POCKET policy and governed executors authorize side effects."},
    {"id":"L10","name":"Cross-Plane Compatibility Law","rule":"Voice, agent, model, memory, device, deployment, and proof planes communicate through versioned compatibility contracts."},
    {"id":"L11","name":"Resonant Routing Law","rule":"HZ names are logical coordination frequencies: routing may optimize cadence, salience, locality, and urgency without claiming literal RF transport."},
    {"id":"L12","name":"Lineage Law","rule":"Artifacts, model outputs, memories, and receipts preserve origin, version, parentage, and transformation history."},
    {"id":"L13","name":"Consequence Law","rule":"Actions that can change code, infrastructure, accounts, devices, or external state must carry consequence class and approval policy."},
    {"id":"L14","name":"No Silent Substitution Law","rule":"A failed or unavailable primary model/runtime cannot be silently replaced when the substitution changes privacy, cost, authority, or evidence semantics."},
    {"id":"L15","name":"Envelope Truth Law","rule":"The envelope is the shared truth object: speech, UI, agents, models, and receipts are views of the same operation state."},
)


def manifest() -> Dict[str, Any]:
    return {
        "schema": "pocket.doctrine-laws.v1",
        "authority": "POCKET Host",
        "laws": [dict(x) for x in LAW_SET],
        "count": len(LAW_SET),
        "claims_boundary": "architectural invariants; no consciousness claim; logical HZ is not literal radio",
    }


def validate_message(message: Dict[str, Any]) -> Dict[str, Any]:
    required = ("schema", "request_id", "from", "to", "channel", "kind", "state")
    missing = [k for k in required if not message.get(k)]
    violations: List[str] = []
    if missing:
        violations.append("L1/L2/L3: missing " + ", ".join(missing))
    if message.get("side_effect") and not message.get("approval"):
        violations.append("L6/L13: side effect lacks approval policy")
    if message.get("state") == "succeeded" and not (message.get("receipt") or message.get("evidence")):
        violations.append("L5/L7: success lacks evidence")
    if message.get("fallback") and not message.get("fallback_disclosed"):
        violations.append("L14: fallback was not disclosed")
    return {"ok": not violations, "violations": violations, "law_count": len(LAW_SET)}
