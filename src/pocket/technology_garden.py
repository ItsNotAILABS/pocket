from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from pocket.envelope_hardening import canonical_digest, hardened_envelope, validate_hardened_envelope

@dataclass(frozen=True)
class Technology:
    id: str
    name: str
    layer: str
    maturity: str
    priority: int
    dependencies: tuple[str, ...]
    invariants: tuple[str, ...]
    failure_modes: tuple[str, ...]
    evidence: tuple[str, ...]

TECHNOLOGIES: tuple[Technology, ...] = (
    Technology("MRCF","Medina Resonant Channel Fabric","fabric","implemented-core",100,("TNHE","CCL"),("named channels","bounded participants","risk/retention declared","transport independence"),("broadcast bypass","channel confusion","unbounded backlog"),("channel manifest","routing tests","ACL tests","backpressure receipt")),
    Technology("ECE","Envelope-Coupled Execution","execution","implemented-core",99,("CCL","TNHE"),("one causal truth object","state monotonicity","approval before side effects","evidence before success"),("split-brain state","silent success","approval bypass"),("state-machine tests","approval tests","receipt correlation")),
    Technology("CCL","Causal Channel Lattice","causality","implemented-core",96,("TNHE",),("request id preserved","parentage preserved","acyclic lineage","bounded fan-out"),("orphan events","cycles","duplicate causal roots"),("lineage graph tests","duplicate detection")),
    Technology("TNHE","Transport-Neutral HZ Envelope","protocol","implemented-core",95,(),("versioned schema","canonical serialization","transport cannot alter meaning","expiry/replay metadata"),("schema drift","transport-specific semantics","replay"),("conformance vectors","canonical hash","replay tests")),
    Technology("CACR","Consequence-Aware Channel Routing","governance","implemented-foundation",93,("MRCF","ECE"),("consequence class required","high consequence isolated","policy decision attached"),("under-classification","routing around policy"),("policy matrix tests","deny receipts")),
    Technology("MWR","Model Witness Receipt","proof","implemented-foundation",91,("BIP","CCL"),("compute is not authority","input/config/output digests","runtime identity bound"),("receipt without provenance","model impersonation"),("digest vectors","runtime identity tests")),
    Technology("MLC","Model Lineage Capsule","model-lineage","proposed-hardened",90,("MWR",),("checkpoint/tokenizer/runtime bound","evaluation references immutable","serving policy explicit"),("checkpoint substitution","tokenizer drift","eval mismatch"),("capsule signature","artifact hashes","eval linkage")),
    Technology("ECMR","Evidence-Coupled Model Router","routing","proposed-hardened",89,("MWR","MLC","CACR"),("route by evidence need","fallback disclosed","privacy/cost constraints preserved"),("silent fallback","weak model for high evidence task"),("route decision receipt","fallback tests")),
    Technology("SPE","Spectral Proof Envelope","proof","proposed-hardened",88,("MWR","DHS"),("spectral input/config/output bound","units explicit","reproducibility metadata"),("unit ambiguity","non-reproducible transform"),("known-vector tests","hash manifest")),
    Technology("RER","Resonant Evidence Routing","proof-routing","implemented-foundation",86,("MRCF","SPE"),("proof lane is append-oriented","evidence class preserved","verification separate from execution"),("proof loss","evidence routed as chat"),("proof-lane tests","artifact retention receipt")),
    Technology("BIP","Bounded Intelligence Port","model-boundary","implemented-core",85,("ECE",),("compute-only authority","explicit capability set","bounded payload/time","no silent cloud substitution"),("authority leakage","unbounded invocation","hidden provider switch"),("capability tests","timeout tests","substitution denial")),
    Technology("VRC","Voice Reality Compiler","interface","implemented-core",84,("ECE","CACR","CCL"),("speech compiles to typed intent","spoken state matches envelope state","confirmation grammar explicit"),("false executable intent","premature success speech"),("intent corpus","confirmation tests","state-to-speech tests")),
    Technology("RCS","Resonant Channel Scheduler","scheduler","proposed-hardened",82,("MRCF","CACR"),("bounded queues","priority aging","fairness","backpressure","deadline awareness"),("starvation","priority inversion","queue explosion"),("scheduler simulation","load receipt")),
    Technology("SCC","Spectral Context Compiler","context","proposed-hardened",80,("DHS","MLC"),("source provenance preserved","bounded context","reversible references","unit/schema explicit"),("provenance loss","context overcompression"),("round-trip tests","provenance manifest")),
    Technology("DHS","Dual-HZ Semantics","semantics","implemented-core",78,(),("logical HZ never implies RF","physical spectral units explicit","translation boundary explicit"),("metaphor/physics conflation","unit collision"),("semantic boundary tests","unit tests")),
    Technology("RHT","Reciprocal HZ Translator","translation","proposed-hardened",74,("DHS","RCS"),("physical metrics are advisory inputs","logical channel identity preserved","device transport policy remains governed"),("physical metric becomes authority","semantic remapping"),("translation fixtures","policy tests")),
)

BY_ID = {t.id: t for t in TECHNOLOGIES}


def ranked() -> List[Dict[str, Any]]:
    return [asdict(x) for x in sorted(TECHNOLOGIES, key=lambda x: (-x.priority, x.id))]


def validate_dependency_graph() -> Dict[str, Any]:
    missing: List[str] = []
    cycles: List[List[str]] = []
    for t in TECHNOLOGIES:
        for dep in t.dependencies:
            if dep not in BY_ID:
                missing.append(f"{t.id}->{dep}")
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: List[str] = []
    def visit(node: str) -> None:
        if node in visiting:
            i = stack.index(node) if node in stack else 0
            cycles.append(stack[i:] + [node])
            return
        if node in visited:
            return
        visiting.add(node); stack.append(node)
        for dep in BY_ID[node].dependencies:
            if dep in BY_ID:
                visit(dep)
        stack.pop(); visiting.remove(node); visited.add(node)
    for node in BY_ID:
        visit(node)
    return {"ok": not missing and not cycles, "missing": missing, "cycles": cycles}


def hardening_manifest() -> Dict[str, Any]:
    graph = validate_dependency_graph()
    return {
        "schema":"pocket.technology-garden.v1",
        "count":len(TECHNOLOGIES),
        "best_overall":"MRCF",
        "best_correctness_primitive":"ECE",
        "best_market_interface":"VRC",
        "graph":graph,
        "technologies":ranked(),
        "proof_policy":{
            "ci_required":False,
            "local_deterministic_gate":True,
            "minimum_assertions":128,
            "hash_manifest":True,
            "signed_receipt_optional":True,
            "integration_roundtrip_required":True,
            "exact_validator_hash_required":True,
        },
    }
