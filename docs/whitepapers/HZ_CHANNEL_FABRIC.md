# HZ Channel Fabric

## Logical resonance, causal routing and multi-transport communication for POCKET agents and models

**ITSNotAI Labs / Medina Architecture Series**  
**Protocol:** `pocket.hz-mesh.v2` + `pocket.channel-envelope.v1`  
**Status:** Engineering white paper  
**Version:** 2026.08

## Abstract

POCKET originally used six logical HZ lanes backed by an encrypted file-bus. That mechanism was useful for local subagent coordination but did not fully describe the communication needs of voice, foundation models, durable memory, proof, deployment and recovery. The revised HZ Channel Fabric expands the system to twelve governed semantic lanes and separates the meaning of a channel from the transport that carries it.

The critical distinction is **Dual-HZ Semantics**. POCKET HZ values are logical coordination labels. AURO/MESIE separately contains a physical `HzLadder` with electromagnetic frequency tiers and link-budget mathematics. The two structures may inform one another but are not conflated. A message on POCKET logical HZ 6 is not claimed to be transmitted at six cycles per second or by radio.

## 1. Why channels are architecture

Ordinary topic systems answer: *where should this message go?* POCKET channels additionally answer:

- what kind of meaning is carried;
- what consequence class applies;
- who may participate;
- how long the information should persist;
- whether evidence is required;
- what recovery behavior is valid;
- which operation and causal parent the message belongs to.

This turns a channel from a string into a governed semantic boundary.

## 2. Canonical lane map

| Lane | Logical HZ | Semantic class | Typical risk | Retention |
|---|---:|---|---|---|
| `user` | 0 | command | mixed | session |
| `heartbeat` | 1 | liveness | read | short |
| `design` | 2 | creation | compute | project |
| `security` | 3 | audit | privileged-read | audit |
| `ship` | 4 | release | high | release |
| `intel` | 5 | research | compute | project |
| `model` | 6 | inference | compute | bounded |
| `memory` | 7 | continuity | write-bounded | durable |
| `proof` | 8 | evidence | append-only | durable |
| `voice` | 9 | speech-state | mixed | session |
| `deploy` | 10 | external-change | high | release |
| `recovery` | 11 | failure-repair | bounded | incident |

The numbering preserves the original lanes while extending the lattice rather than rewriting its lineage.

## 3. Multi-transport model

The semantic envelope can be carried by:

- encrypted mesh disk;
- HTTP;
- MCP;
- WebSocket;
- in-process calls;
- governed device bridges.

The transport is deliberately not the protocol authority. A WebSocket reconnect or broker migration should not alter the request ID, sender, destination, consequence class or operation state.

## 4. Dual-HZ Semantics

### Logical HZ - POCKET
Logical HZ expresses coordination meaning and cadence. It can be used to prioritize, group and route traffic.

### Physical Hz - AURO/MESIE
`mesie.edge.hz_ladder` models actual frequency ranges including ELF/Schumann, VLF, HF, terrestrial UHF, satellite SHF, EHF crosslinks and optical communication. It includes physical quantities such as wavelength, Shannon capacity, free-space path loss, Doppler shift and link budgets.

### Law
No logical POCKET HZ label should be represented as a physical carrier unless a real device/transport implementation and measured evidence establish that fact.

This separation makes the architecture scientifically cleaner and operationally more useful.

## 5. Causal Channel Lattice

Messages form a graph through `request_id` and `parent_id`.

```text
USER voice request
      |
      v
voice@HZ9 ---- transcript / state
      |
      v
model@HZ6 ---- AURO / MESIE / model provider
      |
      +------> intel@HZ5 research
      |
      v
agent execution
      |
      +------> memory@HZ7 continuity
      |
      +------> proof@HZ8 evidence
      |
      v
deploy@HZ10 ---- gated external change
      |
      v
proof@HZ8 ---- deployment receipt
```

A failure can route to `recovery@HZ11` while keeping the same request lineage.

## 6. Resonant routing

“Resonance” in this protocol means a routing fit between message semantics and channel properties. It is not a claim that software agents literally oscillate as physical resonators.

A routing score can eventually include:

- semantic affinity;
- consequence class;
- urgency;
- expected cadence;
- required durability;
- participant locality;
- privacy boundary;
- current channel load;
- proof requirement;
- dependency state.

This suggests a future **Resonant Channel Scheduler** that selects both channel and transport under policy while retaining deterministic explanation of the route.

## 7. Communication with foundation models

Foundation models participate on the `model` lane. They can emit derived results to `intel` or `proof`, but they do not move directly onto `deploy` with external-change authority.

A model request should carry:

```text
request_id
model lane / checkpoint
bounded context reference
budget
privacy class
fallback policy
expected output contract
```

A model response should carry:

```text
provider/runtime identity
model/checkpoint identity where known
result or artifact reference
latency / usage telemetry where available
failure state
receipt/evidence reference when required
```

POCKET Host remains responsible for turning model output into authorized work.

## 8. AURO/MESIE communication

AURO/MESIE participates on four core lanes:

- HZ5 `intel` - research and spectral intelligence;
- HZ6 `model` - embeddings and model/foundation compute;
- HZ8 `proof` - validation, benchmark and evidence;
- HZ11 `recovery` - bounded failure and runtime repair.

The AURO-side `auro.pocket-channel-contract.v1` mirrors these semantics without importing POCKET's host authority into the model runtime.

## 9. Voice as a channel participant

Voice is not a separate truth source. The Voice Reality Compiler publishes state transitions on HZ9 while the underlying work uses the same request lineage.

Example:

```text
VOICE/HZ9: heard
VOICE/HZ9: compiled
MODEL/HZ6: route selected
AGENT: executing
PROOF/HZ8: verification produced
VOICE/HZ9: speaks verified result
```

This is how “the voice itself is the coding/making/deploying envelope” becomes technically precise: voice compiles and narrates the same operation state, while governed agents and deployment runtimes perform side effects.

## 10. Comparison boundary

The HZ Channel Fabric can sit above established messaging systems. DDS has sophisticated QoS; MQTT 5 carries correlation and request-response properties; NATS offers high-performance messaging; Zenoh unifies publish/subscribe, query and storage. Those systems solve transport/distribution problems well.

POCKET's layer adds a domain-specific governance contract: causal identity, consequence, approval, model non-authority, lineage and proof semantics. At scale, replacing mesh-disk with one of these mature transports may be preferable to reimplementing broker mechanics.

## 11. Scale-out requirements

Before high-volume or multi-host production, the fabric should gain uniform implementations for:

1. channel ACL enforcement;
2. signed envelope verification;
3. expiry and replay windows;
4. idempotent side-effect keys;
5. durable consumer offsets;
6. backpressure and per-lane quotas;
7. dead-letter/denial lanes or explicit denial receipts;
8. cross-host clock/ordering policy;
9. transport adapter conformance tests;
10. recovery replay that cannot duplicate external side effects.

## 12. Novel internal technology registry

The architecture gives names to several compositional patterns:

- **MRCF - Medina Resonant Channel Fabric**
- **DHS - Dual-HZ Semantics**
- **CCL - Causal Channel Lattice**
- **TNHE - Transport-Neutral HZ Envelope**
- **RER - Resonant Evidence Routing**
- **CACR - Consequence-Aware Channel Routing**
- **RCS - Resonant Channel Scheduler** (proposed)

These names describe the ITSNotAI Labs design vocabulary and do not by themselves assert patent novelty.

## 13. Conclusion

The HZ mesh is now a communication architecture rather than a handful of frequency-named files. Its purpose is to let every agent and model communicate while preserving who spoke, to whom, about what, under which consequence policy, with what lineage and with what proof. The transport can evolve independently. The truth contract cannot.
