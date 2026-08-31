# POCKET Family Protocol v1

POCKET is a family of cooperating products, not three independent repos.

## Canonical roles

- `ItsNotAILABS/pocket` — host/control plane: users, organizations, device pairing, desk/phone/work surfaces, routing, governance, receipts, deployment.
- `ItsNotAILABS/pocket-voice-to-text` — voice control plane: patient VAD, semantic turn detection, STT scaffolding, personas, agentic flows, context buffer, Studio contract, voice API.
- `ItsNotAILABS/pocket-agent` — long-running execution plane: RLM, continual harness, RAH, goals, schedules, capsules, project-local execution.

## Shared protocol envelope

All cross-repo messages should carry a compact envelope:

```json
{
  "schema": "pocket.family.v1",
  "request_id": "uuid-or-stable-id",
  "source": "pocket|pocket-voice|pocket-agent",
  "target": "pocket|pocket-voice|pocket-agent",
  "principal": {"id": "...", "role": "...", "tenant": "..."},
  "session": {"id": "...", "channel": "voice|desk|phone|agent"},
  "capability": "voice.turn|voice.snap|agent.run|agent.attach|host.route",
  "payload": {},
  "timestamp": "RFC3339",
  "receipt": {"parent": null, "hash": null}
}
```

The envelope is intentionally provider-neutral. Provider-specific configuration belongs inside the destination adapter, never in the family protocol.

## Voice-to-Agent flow

1. Voice Studio captures speech and/or a context snap.
2. Pocket Voice decides turn boundaries, maintains voice context, and emits a normalized Studio/session event.
3. POCKET host authorizes the principal and routes the request.
4. For long-running or project-local work, POCKET dispatches to POCKET Agent with the same `request_id` and session linkage.
5. Agent result returns through POCKET; Voice Studio may speak the result while preserving the text/receipt artifact.

## Context snap contract

A snap should be explicit and bounded:

```json
{
  "schema": "pocket.context-snap.v1",
  "kind": "code|document|selection|screen-state",
  "name": "app.js",
  "language": "javascript",
  "content": "...",
  "selection": {"start_line": 1, "end_line": 20},
  "metadata": {"cursor_line": 8}
}
```

Never silently ingest an entire filesystem or workspace when a user snaps one buffer.

## Capability map

| Capability | Owner | Typical consumers |
|---|---|---|
| `voice.turn` | Pocket Voice | POCKET desk/phone/studio |
| `voice.turn.decide` | Pocket Voice | browser/audio clients |
| `voice.snap` | Pocket Voice contract + POCKET routing | Studio, coding surfaces |
| `voice.session` | Pocket Voice | host, browser SDKs |
| `host.route` | POCKET | all family repos |
| `host.account` | POCKET Cloud | hosted products |
| `agent.run` | POCKET Agent | host, Studio, SDK |
| `agent.attach` | POCKET Agent | host desk, CLI |
| `agent.schedule` | POCKET Agent | host automation |
| `agent.capsule` | POCKET Agent | untrusted/isolated execution |

## Receipts

Every cross-repo request should become inspectable without exposing private model reasoning. Receipts should record:

- request/session IDs
- principal/tenant scope
- capability invoked
- source and target
- start/end timestamps
- status
- input/output hashes where appropriate
- parent receipt for multi-hop work
- provider/runtime identity when relevant

Receipts are execution evidence, not chain-of-thought.

## Compatibility rule

Repos may advance independently, but public family contracts must be versioned. A repo must advertise supported family schema/capabilities through a machine-readable capability endpoint or manifest before another repo depends on them.

## Current integration targets

### POCKET host

- expose Pocket Voice capabilities in the platform catalog
- include Voice Studio capability status in readiness/coherence checks
- route Studio context snaps to agent-capable sessions
- preserve request IDs across proxy hops

### Pocket Voice

- ship `pocket.studio.v1` capability contract
- add `/v1/studio/capabilities`
- add normalized context-snap validation
- emit session/usage receipts
- keep provider adapters separate from patient-listening logic

### POCKET Agent

- add provider-neutral host client
- accept `pocket.family.v1` execution envelopes
- return bounded execution receipts
- expose a voice-friendly run mode for short commands without weakening project sandbox rules

## Product doctrine

Pocket Voice owns conversation timing. POCKET owns identity, routing, governance, and product surfaces. POCKET Agent owns long-running execution. None should duplicate the other's core responsibility.
