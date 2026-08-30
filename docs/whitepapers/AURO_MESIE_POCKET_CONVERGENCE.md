# AURO / MESIE / POCKET Convergence

## A bounded native-intelligence port for spectral compute, foundation models, agents and evidence

**ITSNotAI Labs / Medina Architecture Series**  
**Components:** POCKET Host, AURO/MESIE Runtime, NEXUS Federation  
**Status:** Engineering white paper  
**Version:** 2026.08

## Abstract

AURO/MESIE is integrated into POCKET as a native local intelligence family rather than another untyped chatbot provider. MESIE already supplies spectral matching, generation, embeddings, validation, transformer intelligence, internal routing, edge frequency mathematics and multi-language bindings. POCKET supplies identity, policy, execution envelopes, model selection, voice, durable work and consequence governance. NEXUS supplies federation contracts.

This paper defines the boundary between those systems and introduces a stable `AuroSDK` plus the `auro` command-line facade. The boundary allows POCKET agents to use AURO/MESIE through a small versioned surface without coupling the product to dozens of internal research modules.

## 1. Existing MESIE capabilities

The repository already contains substantial runtime technology, including:

- `SpectralIntelligenceSDK` for loading, matching, ranking, generation, embeddings, normalization and validation;
- PSD, FAS and RotDnn spectral generation;
- spectral vectorization and embeddings;
- transformer and inference infrastructure;
- intelligence protocols, memory structures and attention components;
- an internal message bus/router;
- edge and satellite abstractions;
- a physical `HzLadder` and link-budget mathematics;
- Python, Julia, Rust, TypeScript and Motoko integration work;
- benchmark, chaos and release-evidence tooling;
- Cloudflare/API experiments and model-family integration surfaces.

The integration problem is therefore not lack of capability. It is excessive coupling risk. A product host should not import arbitrary research internals every time those internals evolve.

## 2. Bounded Intelligence Port

The **Bounded Intelligence Port (BIP)** is the stable boundary:

```text
POCKET / NEXUS
     |
     | versioned request + budget + context
     v
AuroSDK / `auro` CLI
     |
     +--> MESIE spectral SDK
     +--> foundation/model runtime
     +--> validation / benchmark
     +--> channel contract
     |
     v
result + evidence digest + runtime identity
```

The port intentionally refuses to own user authorization or arbitrary external side effects.

## 3. SDK surface

`mesie.auro_sdk:AuroSDK` provides a narrow product surface:

```python
from mesie.auro_sdk import AuroSDK

auro = AuroSDK()
print(auro.health())
print(auro.capabilities())
print(auro.channels())
result = auro.invoke("spectral.embed", {"record": record})
```

Initial stable actions include:

- `health`
- `capabilities`
- `channels.describe`
- `foundation.describe`
- `spectral.validate`
- `spectral.embed`
- `spectral.generate.psd`
- `spectral.generate.fas`
- `spectral.generate.rotdnn`

The facade can expand without forcing POCKET to depend on unstable internal package paths.

## 4. CLI surface

The MESIE package now exposes a product facade:

```bash
auro health
auro capabilities
auro channels
auro invoke spectral.validate --json '{"record":"record.json"}' --pretty
auro invoke spectral.embed --json '{"record":"record.json"}' --pretty
```

The legacy `mesie` CLI remains useful for scientific corpus inspection and REPL work. The `auro` command is the preferred integration interface for POCKET/NEXUS product calls.

## 5. Receipt semantics

Each bounded `AuroSDK.invoke()` call produces `auro.execution-receipt.v1` with:

- action;
- success state;
- runtime identity;
- MESIE version;
- timestamp;
- SHA-256 evidence digest.

This receipt is a **model witness**, not authorization. It establishes what bounded compute reported. POCKET or another governed executor remains responsible for any downstream side effect.

## 6. Channel semantics

AURO/MESIE publishes a transport-neutral channel contract:

| POCKET lane | Logical HZ | AURO/MESIE role |
|---|---:|---|
| `intel` | 5 | research and spectral intelligence |
| `model` | 6 | embeddings, model/foundation compute |
| `proof` | 8 | validation, benchmark and evidence |
| `recovery` | 11 | runtime failure and bounded repair |

The AURO channel contract explicitly references `mesie.edge.hz_ladder` as the physical frequency model while describing POCKET HZ as semantic/cadence routing. This is the Dual-HZ Semantics boundary.

## 7. Foundation-model integration

POCKET's model mesh treats AURO and MESIE as `native-intelligence-runtime` lanes alongside local and external model tools.

A task involving spectral signals, embeddings, benchmark work or AURO/MESIE can route toward the native intelligence lane. General coding tasks can continue to route toward coding agents such as OpenCode, Qwen Code, Gemini CLI, Codex, Claude or local coding models.

The router should not flatten these into one undifferentiated score. A spectral engine, a coding agent and a conversational model have different evidence and capability semantics.

## 8. Auro14B relationship

Auro14B represents model-family/checkpoint architecture and training/serving work. AURO/MESIE is the provider-neutral runtime/evaluation plane. POCKET should therefore consume model/checkpoint descriptors rather than assuming that a repository name is itself a verified production checkpoint.

Required descriptor fields for future Auro-family registration should include:

```text
model_id
architecture_version
parameter_count_verified_or_label
checkpoint_digest
Tokenizer digest/version
context length
precision/quantization
runtime compatibility
training/evaluation receipt references
license
maturity state
```

This preserves the distinction between a research architecture, a dev geometry and a verified checkpoint.

## 9. Doctrine alignment

The integration maps directly onto POCKET laws:

- **Model Non-Authority:** AURO/MESIE cannot authorize external changes.
- **Evidence Law:** bounded compute creates receipts/evidence digests.
- **No Silent Substitution:** loss of AURO does not silently route to a cloud model when privacy/evidence semantics would change.
- **Translation Law:** POCKET envelopes and AURO channel envelopes translate across the boundary.
- **Lineage Law:** request IDs and evidence references remain attributable.
- **Failure Truth:** absent dependencies fail as absent; they are not presented as successful inference.

## 10. Proposed technical expansions

### Spectral Context Compiler (SCC)
Convert a bounded POCKET context pack into MESIE spectral/embedding representations while retaining provenance back to the source context objects.

### Evidence-Coupled Model Router (ECMR)
Select a model lane not only by capability/cost/latency but by whether the task requires a particular evidence class, reproducible local runtime or checkpoint lineage.

### Reciprocal HZ Translator (RHT)
Use physical-channel metrics from MESIE's `HzLadder` as one input to device/network transport selection while keeping POCKET logical HZ semantics unchanged.

### Model Lineage Capsule (MLC)
A signed capsule binding model descriptor, tokenizer, checkpoint hashes, runtime profile, evaluation receipts and serving policy into one model-consumption object.

### Spectral Proof Envelope (SPE)
A proof-plane artifact that binds spectral inputs, configuration, derived outputs and evaluation metrics under deterministic hashes for repeatable scientific/model claims.

These are internal design proposals. Their novelty should be evaluated against technical prior art before any external intellectual-property claim.

## 11. Missing production work

The integration is structurally useful but should not be overstated. Remaining hardening includes:

1. complete typed payload schemas for each AURO action;
2. streaming/batch request limits and memory quotas;
3. uniform benchmark receipt schema mapped to NEXUS release evidence;
4. stable checkpoint/model descriptor registry;
5. channel signature verification across process boundaries;
6. explicit circuit-breaker behavior for unavailable MESIE optional dependencies;
7. multi-version compatibility tests between POCKET and AURO;
8. MCP tool exposure for the stable facade;
9. HTTP adapter with the same action schema when process separation is desired;
10. reproducible package build/release receipts.

## 12. Operator model

Recommended local product path:

```text
install MESIE/AURO package
        |
        +--> `auro health`
        +--> `auro capabilities`
        +--> POCKET discovers AURO lane
        |
POCKET request
        |
        +--> AuroSDK in-process when available
        |         or
        +--> `auro` bounded CLI
        |
result -> HZ6 model / HZ8 proof -> POCKET envelope
```

The design supports local-first operation without making local installation mandatory for the entire POCKET product.

## 13. Conclusion

AURO/MESIE is most valuable to POCKET when it is treated as a rich scientific/model runtime with a disciplined product boundary. The SDK and CLI facade make that boundary explicit. POCKET gains native intelligence without surrendering host authority; MESIE gains a stable route into voice, agents and production workflows without becoming coupled to POCKET's UI or tenant logic.

The result is a composable architecture: intelligence can evolve rapidly behind AURO while the envelope, policy and evidence contract remains stable at the system boundary.
