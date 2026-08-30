# POCKET Doctrine and Communication Laws

## A governed architecture for persistent agents, foundation models, voice execution, memory, deployment and proof

**ITSNotAI Labs / Medina Architecture Series**  
**Protocol family:** POCKET / NEXUS / AURO / MESIE  
**Status:** Engineering white paper - implemented laws and bounded proposals  
**Version:** 2026.08

---

## Abstract

POCKET is defined here as an envelope operating system: the host boundary that contains identity, scope, teams, policy, model routing, agents, devices, artifacts, execution and proof. The central problem is not merely how to call a model or transmit a message. It is how to preserve meaning, authority, consequence, identity, lineage and truth while work crosses heterogeneous agents and transports.

This paper formalizes fifteen communication and execution laws. The laws are implemented in `pocket.doctrine-laws.v1` and applied to `pocket.channel-envelope.v1`. They constrain human voice, autonomous agents, foundation models, local runtimes, deployment systems and evidence producers without assigning any model independent authority.

The architecture adopts continuity, consequence and recurrence as system properties. A task may move between voice, models, agents, memory and deployment, but the causal operation is expected to remain identifiable as the same operation. The envelope is therefore treated as the shared truth object; individual UIs, spoken replies, model completions and receipts are views of that state rather than separate realities.

## 1. Doctrine boundary

POCKET follows five load-bearing principles.

1. **Envelope before subsystem.** Identity, scope, policy and consequence wrap model or agent execution rather than being optional middleware afterward.
2. **Continuity before stateless cleverness.** Long-running work preserves request lineage, unresolved state, memory and recovery information.
3. **Consequence before action.** Any operation that changes code, infrastructure, accounts, devices or an external environment carries an explicit consequence and approval class.
4. **Evidence before success language.** A completion claim is different from an execution request, process start, benchmark assertion or deployment intention.
5. **Models compute; the host authorizes.** Foundation models, AURO/MESIE and third-party model CLIs are intelligence providers, not policy principals.

These are architecture rules. They do not depend on claims of consciousness or biological equivalence.

## 2. The fifteen laws

### L1 - Continuity Law
Every consequential operation preserves request, session, project and causal parent identifiers across hops. A transport boundary cannot silently create a new history.

### L2 - Addressability Law
Every speaking or acting node has an explicit identity and destination. Anonymous privileged broadcast is invalid.

### L3 - Channel Sovereignty Law
A channel carries a declared semantic class, risk tier, retention rule and allowed participant set. A channel name is therefore a governance object, not just a string topic.

### L4 - Translation Law
Cross-plane messages are translated into versioned envelopes. The underlying carrier may change between in-process calls, mesh disk, HTTP, MCP or WebSocket while the request identity and semantic contract remain stable.

### L5 - Evidence Law
Execution, benchmark, deployment and release claims require attributable evidence. A system without evidence may say *planned*, *queued*, *executing*, *unknown* or *failed*, but it may not promote itself to verified success.

### L6 - Bounded Authority Law
No agent, model, channel or transport gains authority merely by producing a recommendation, completion or message. Authority is separately scoped and governed.

### L7 - Failure Truth Law
Failure, timeout, denial, uncertainty and partial completion are first-class states. They cannot be rewritten into success for conversational smoothness.

### L8 - Recurrence Law
Unresolved work may recur only with preserved state, bounded retry policy and visible ownership. Recurrence without lineage becomes uncontrolled repetition.

### L9 - Model Non-Authority Law
Foundation models propose or compute. POCKET policy and governed executors authorize side effects. This applies to AURO, MESIE, Auro model-family checkpoints, local models and external model providers.

### L10 - Cross-Plane Compatibility Law
Voice, agent, model, memory, device, deployment and proof planes communicate through versioned compatibility contracts. Internal implementation details do not substitute for a public contract.

### L11 - Resonant Routing Law
POCKET HZ names are logical coordination frequencies. Routing may optimize semantic class, cadence, salience, locality and urgency; logical HZ labels do **not** claim literal RF transmission.

### L12 - Lineage Law
Artifacts, model outputs, memories and receipts preserve origin, version, parentage and transformation history.

### L13 - Consequence Law
Any action capable of changing code, infrastructure, accounts, devices or an external system declares consequence class and approval policy before execution.

### L14 - No Silent Substitution Law
A failed or unavailable primary model/runtime cannot be silently replaced when substitution changes privacy, cost, authority or evidence semantics.

### L15 - Envelope Truth Law
The envelope is the shared truth object. Speech, UI, agents, models and receipts are projections of the same operation state.

## 3. Communication planes

POCKET separates responsibilities into cooperating planes:

| Plane | Primary responsibility | May authorize external side effects? |
|---|---|---:|
| User / team | identity, membership, intent, rooms, mission ownership | through policy |
| Voice | listen, turn timing, compile intent, speak operation state | no |
| Model | inference, embeddings, research, transformation | no |
| Agent | decomposition and bounded execution work | only under granted policy |
| Memory | durable context, outcomes, unresolved state | no independent execution |
| Device | sensing and governed device operations | only under granted policy |
| Deployment | packaging and external state change | yes, confirmation/policy gated |
| Proof | validation, receipts, hashes, benchmark/release evidence | no |
| Federation | protocol routing and compatibility | no user authority |

The separation prevents intelligence from becoming implicit authorization.

## 4. The causal envelope

A canonical communication unit carries at minimum:

```json
{
  "schema": "pocket.channel-envelope.v1",
  "message_id": "msg-...",
  "request_id": "req-...",
  "parent_id": "msg-parent-or-null",
  "from": "VOICE",
  "to": "POCKET_AGENT",
  "channel": "model",
  "logical_hz": 6,
  "semantic_class": "inference",
  "risk": "compute",
  "kind": "model.request",
  "state": "published",
  "side_effect": false,
  "approval": "allow",
  "lineage": {"parent_id": null}
}
```

This is deliberately more opinionated than ordinary publish/subscribe metadata because it couples communication to governance and causal history.

## 5. Voice Reality and the Envelope Truth Law

The Voice Reality Compiler introduced in POCKET converts speech into a typed execution envelope. The important property is not speech recognition itself. It is continuity between what was said and what actually happens.

A spoken operation can move through the state sequence:

```text
HEARD -> COMPILED -> ROUTED -> QUEUED -> EXECUTING
      -> VERIFYING -> SUCCEEDED | FAILED | DENIED | CANCELLED
```

High-consequence work can enter `AWAITING_CONFIRMATION` without discarding the original operation. The spoken response is expected to reflect that same state. Starting a background mission is therefore described as *executing*, not *done*.

## 6. Foundation-model law

All foundation-model lanes are treated as replaceable compute providers only at a bounded runtime interface. They are not interchangeable at the evidence boundary.

A provider selection therefore carries at least:

- explicit lane/model identity;
- locality/privacy classification;
- cost class;
- task capabilities;
- budget and timeout;
- fallback policy;
- output provenance;
- receipt or evidence linkage when consequential.

A local model may be preferred for privacy and cost, but it cannot silently replace a different requested provider when the substitution changes semantics.

## 7. AURO / MESIE position

AURO/MESIE participates as a native intelligence runtime. It may perform spectral processing, embeddings, foundation-model operations, scientific inference, validation and benchmarking. It has no independent user-policy authority and no implicit external side-effect authority.

POCKET therefore routes AURO/MESIE results primarily through:

- `intel` - research and spectral intelligence;
- `model` - model inference and embeddings;
- `proof` - validation, benchmark and evidence;
- `recovery` - runtime failure and bounded repair.

This maintains the same doctrine whether intelligence comes from MESIE, AURO model-family work, Ollama, llama.cpp, Gemini CLI, Qwen Code, Codex, Claude or another future lane.

## 8. Newly named internal architecture patterns

These names describe the present ITSNotAI Labs architecture. They should not be interpreted as claims that no similar technique exists elsewhere.

### Medina Resonant Channel Fabric (MRCF)
A semantic/cadence channel system in which logical HZ labels bind message purpose, risk, retention and participants while remaining transport-neutral.

### Dual-HZ Semantics (DHS)
The explicit separation between **logical coordination HZ** in POCKET and **physical spectral Hz** modeled by AURO/MESIE. This prevents a useful coordination abstraction from becoming a false RF claim.

### Envelope-Coupled Execution (ECE)
A design in which the request envelope remains the causal truth object across voice, models, agents, execution and receipts.

### Causal Channel Lattice (CCL)
A channel graph in which every consequential message carries request and parent lineage, allowing a distributed action to be reconstructed as a causal tree rather than a flat log.

### Bounded Intelligence Port (BIP)
A stable product facade that exposes intelligence capabilities while explicitly denying policy and external-side-effect authority. `AuroSDK` and the `auro` CLI are implementations of this pattern.

### Model Witness Receipt (MWR)
An evidence digest emitted for model or scientific compute that proves which bounded action produced a result without elevating that model into an authorization principal.

### Resonant Evidence Routing (RER)
Routing validation, benchmark and receipt events to a dedicated proof channel rather than mixing them with conversational/model output.

### Consequence-Aware Channel Routing (CACR)
Channel selection that incorporates consequence class so deployment/external-change messages are separated from ordinary model or research traffic.

### Transport-Neutral HZ Envelope (TNHE)
A logical HZ envelope that can cross mesh disk, HTTP, MCP, WebSocket, in-process or device transports while preserving semantic identity.

## 9. Prior-art boundary

POCKET does not claim to invent publish/subscribe, request/reply, QoS, correlation identifiers or distributed storage. Mature systems already provide strong primitives in these areas. The engineering distinction here is the integrated use of causal lineage, consequence/approval semantics, evidence requirements, model non-authority and voice/execution state under a shared envelope.

The design can therefore interoperate with mature messaging transports rather than replacing them. A future adapter may map POCKET channels onto DDS QoS, MQTT topics/properties, NATS subjects/JetStream or Zenoh key expressions while retaining POCKET's higher-level doctrine.

## 10. Missing-technology audit

The doctrine review identified the following elements as required for a complete production architecture. Current implementation status should remain explicit rather than aspirational.

| Requirement | POCKET posture |
|---|---|
| Identity / teams / scopes | host authority; existing product plane |
| Versioned channel schema | implemented in channel fabric v1 |
| HZ semantic lanes | implemented; expanded to 12 lanes |
| Causal request lineage | implemented in channel envelope |
| Side-effect approval semantics | implemented at envelope level; executor integration remains plane-specific |
| Model descriptors | model mesh implemented; deeper per-checkpoint evidence remains model-repo responsibility |
| AURO/MESIE SDK/CLI | integrated through stable facade |
| Local model adapters | Ollama/llama.cpp/LM Studio discovery plus existing model CLI lanes |
| MCP transport | supported transport class; adapter wiring remains subsystem-specific |
| Durable message broker | mesh disk exists; dedicated broker is an optional scale-out transport, not yet claimed |
| Cross-process leases/idempotency | exists in portions of NEXUS/POCKET execution; should be standardized across all channel consumers |
| Artifact diff / immutable evidence | proof plane exists; all artifact classes still need uniform sealing |
| RBAC/channel ACL enforcement | semantics defined; full channel-level enforcement remains a hardening target |
| Signed channel envelopes | existing mesh has HMAC mechanisms; channel-fabric signature normalization remains a hardening target |
| Quotas/backpressure | required before high-scale production channel fan-out |
| Recovery/replay | recovery channel defined; durable replay policy should be standardized per transport |
| Public proofroom | NEXUS release-evidence architecture exists; unified POCKET proofroom remains a product surface target |

## 11. Security and failure model

The architecture assumes that model output can be wrong, agent processes can die, transports can partition, stale messages can reappear and credentials can exist outside the model process.

Required controls include:

- explicit sender and recipient;
- channel ACL enforcement;
- message freshness / expiry;
- idempotency keys for side effects;
- bounded retry and circuit breaking;
- approval for high-consequence operations;
- immutable or append-only proof records for releases;
- secret references rather than secret propagation in envelopes;
- denial receipts for rejected privileged operations;
- no hidden reasoning or private chain-of-thought in receipts.

## 12. Production invariants

A production promotion should fail if any of the following becomes true:

1. a high-consequence action executes without policy/approval context;
2. a success state exists without evidence where evidence is required;
3. a model output is treated as authorization;
4. request identity is dropped between voice, model and agent hops;
5. a fallback changes privacy/cost/authority semantics without disclosure;
6. logical HZ is represented as proven physical radio transport;
7. an agent cannot be addressed or its message lineage reconstructed;
8. recovery silently duplicates an external side effect.

## 13. Conclusion

POCKET's doctrine is a systems architecture for preserving truth while intelligence moves. The system is strongest when every model, voice, agent and deployment action can change implementation without changing the causal contract. HZ provides the semantic channel lattice; NEXUS provides federation contracts; AURO/MESIE provides bounded native intelligence; POCKET remains the envelope and policy authority; receipts preserve what actually occurred.

The resulting objective is not an illusion of omniscience. It is a system in which computation can become action without losing lineage, authority, consequence or evidence.
