# POCKET Technology Garden Hardening

## Decision

The technology family is not one flat list. It is a dependency garden with three crowns:

1. **MRCF — Medina Resonant Channel Fabric** is the best overall platform technology because it is the substrate that lets agents, models, memory, proof, voice and deployment communicate under one governed semantic fabric.
2. **ECE — Envelope-Coupled Execution** is the best correctness primitive because it keeps one causal truth object across intent, approval, execution, verification and receipt.
3. **VRC — Voice Reality Compiler** is the best market-facing technology because it turns ordinary speech into governed executable work while preserving ECE truth.

The strongest defensible system story is the composition: **MRCF + ECE + CCL + TNHE + CACR** form the core. VRC, BIP, MWR and the next-generation technologies grow on that core.

## Production ranking

| Rank | Technology | Role | Why it matters |
|---:|---|---|---|
| 1 | MRCF | Fabric | Governs semantic communication across the whole POCKET family. |
| 2 | ECE | Execution truth | Prevents UI/model/agent state from diverging from actual operation state. |
| 3 | CCL | Causality | Makes distributed agent work reconstructable and attributable. |
| 4 | TNHE | Protocol | Lets the same semantic envelope survive transport changes. |
| 5 | CACR | Governance routing | Separates low-consequence compute from externally consequential actions. |
| 6 | MWR | Model proof | Makes model/scientific compute attributable without granting authority. |
| 7 | MLC | Model lineage | Binds checkpoint, tokenizer, runtime, evaluation and serving policy. |
| 8 | ECMR | Model routing | Chooses models by evidence/privacy/cost requirements, not capability alone. |
| 9 | SPE | Spectral proof | Makes AURO/MESIE spectral claims reproducible and hash-bound. |
| 10 | RER | Proof routing | Keeps proof traffic distinct from conversational traffic. |
| 11 | BIP | Model boundary | Gives AURO/MESIE and other intelligence bounded compute ports. |
| 12 | VRC | Human interface | Converts spoken intent into governed executable envelopes. |
| 13 | RCS | Scheduling | Adds fairness, priority aging, backpressure and deadlines. |
| 14 | SCC | Context | Compiles provenance-preserving context into spectral/model representations. |
| 15 | DHS | Semantics | Keeps logical HZ and physical spectral Hz scientifically separate. |
| 16 | RHT | Translation | Lets physical/network metrics influence transport choice without changing logical meaning. |

This ranking is architectural priority, not marketing value. VRC is intentionally lower in dependency priority because it depends on ECE/CACR/CCL; as a product story it is one of the strongest technologies.

## Hardening contract applied to all 16

Every technology has four required production classes:

- **Invariants:** what must always remain true.
- **Failure modes:** what must be detected or contained.
- **Dependencies:** lower-level technologies it may rely on; the graph must remain acyclic.
- **Evidence:** tests, receipts, manifests or conformance vectors required before a maturity claim is promoted.

No technology may be called production-ready solely because code exists.

## CI replacement

GitHub Actions is not the validation authority for this technology family. The canonical proof gate is repository-native and deterministic:

```bash
python scripts/validate_technology_garden.py
```

It is local and network-independent and emits:

- `dist/proof/technology-garden-receipt.json`
- `dist/proof/technology-garden-manifest.json`

The production threshold is at least **128 assertions**. The hardened release validator currently executes **300 assertions**. CI may mirror this validator in the future, but the validator and its receipts remain the source of proof.

## Runtime hardening

`pocket.technology_garden` adds:

- canonical JSON SHA-256 hashing;
- bounded envelope TTL;
- nonce generation;
- replay detection hooks;
- tamper detection;
- explicit side-effect approval validation;
- acyclic technology dependency validation;
- machine-readable maturity, invariant, failure and evidence profiles.

`pocket.channel_fabric` now applies the hardened envelope at creation time and exposes transport-ingress validation.

## Technology garden rings

Develop the family in dependency rings rather than as sixteen independent products:

**Root layer:** TNHE, DHS  
**Causal core:** CCL, ECE  
**Fabric/governance:** MRCF, CACR  
**Intelligence boundary:** BIP, MWR, MLC, ECMR  
**Evidence/spectral:** SPE, RER, SCC, RHT  
**Runtime dynamics:** RCS  
**Human surface:** VRC

This order prevents interface and automation layers from outrunning the truth, policy and proof substrate beneath them.

## Claims boundary

These are internal ITSNotAI Labs architecture names and compositions. The names do not themselves assert patent novelty or absence of prior art. Logical HZ remains semantic/cadence coordination, not a claim of literal RF behavior. No consciousness claim is made.
