"""Executable doctrine laws for POCKET communication and execution.

These laws constrain agents, foundation models, voice, tools, memory, devices,
proof systems, and transports. They are architectural invariants, not claims
about consciousness or literal physics.
"""
from __future__ import annotations

from typing import Any, Dict, List

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
    {"id":"L16","name":"Temporal Coherence Law","rule":"Every consequential envelope carries creation time, freshness/expiry policy, and monotonic state progression so stale messages cannot overwrite newer truth."},
    {"id":"L17","name":"Backpressure Law","rule":"Channels must expose bounded queue, budget, or flow-control behavior; overload is a visible state and may not become unbounded fan-out."},
    {"id":"L18","name":"Lease and Ownership Law","rule":"Long-running work has an explicit owner or renewable lease; competing workers may not execute the same consequence-bearing step without takeover evidence."},
    {"id":"L19","name":"Replay Safety Law","rule":"Every side-effecting operation carries idempotency identity or an explicit non-replayable marker; recovery must not duplicate external consequences."},
    {"id":"L20","name":"Capability Disclosure Law","rule":"Agents, models, devices, and transports declare supported actions, limits, locality, readiness, and evidence level before they are selected by a router."},
    {"id":"L21","name":"Intent Preservation Law","rule":"Translation, summarization, model routing, and agent delegation may refine representation but may not silently broaden the user's approved objective or consequence scope."},
    {"id":"L22","name":"Proof Convergence Law","rule":"A consequential operation reaches verified success only when execution state and independent proof state converge on the same request, artifact lineage, and version."},
    {"id":"L23","name":"Channel Failover Law","rule":"Transport failover preserves the same envelope identity and discloses changed trust, latency, privacy, or durability semantics; transport change cannot create new authority."},
)


def manifest() -> Dict[str, Any]:
    return {
        "schema": "pocket.doctrine-laws.v2",
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
        violations.append("L5/L7/L22: success lacks converged evidence")
    if message.get("fallback") and not message.get("fallback_disclosed"):
        violations.append("L14/L23: fallback or failover was not disclosed")
    if message.get("side_effect") and not (message.get("idempotency_key") or message.get("non_replayable")):
        violations.append("L19: side effect lacks replay-safety declaration")
    if message.get("lease_required") and not (message.get("lease_id") or message.get("owner")):
        violations.append("L18: long-running work lacks lease/owner")
    if message.get("expires_at") is None and message.get("freshness_required"):
        violations.append("L16: freshness-required envelope lacks expiry")
    if message.get("capability_selected") and not message.get("capability_descriptor"):
        violations.append("L20: selected capability lacks descriptor")
    return {"ok": not violations, "violations": violations, "law_count": len(LAW_SET)}
