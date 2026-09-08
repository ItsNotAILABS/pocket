from __future__ import annotations
import json, sys, hashlib, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pocket.technology_garden import TECHNOLOGIES, BY_ID, ranked, validate_dependency_graph, hardened_envelope, validate_hardened_envelope, hardening_manifest, canonical_digest

checks = []
def check(cond, name):
    checks.append((bool(cond), name))
    if not cond:
        raise AssertionError(name)

check(len(TECHNOLOGIES) == 16, "technology_count")
check(len(BY_ID) == 16, "unique_ids")
check(validate_dependency_graph()["ok"], "dependency_graph")
check(ranked()[0]["id"] == "MRCF", "best_overall")
check(hardening_manifest()["best_correctness_primitive"] == "ECE", "best_correctness")
check(hardening_manifest()["best_market_interface"] == "VRC", "best_market")

for t in TECHNOLOGIES:
    check(bool(t.id), f"{t.id}:id")
    check(bool(t.name), f"{t.id}:name")
    check(bool(t.layer), f"{t.id}:layer")
    check(bool(t.maturity), f"{t.id}:maturity")
    check(1 <= t.priority <= 100, f"{t.id}:priority")
    check(len(t.invariants) >= 2, f"{t.id}:invariants")
    check(len(t.failure_modes) >= 1, f"{t.id}:failure_modes")
    check(len(t.evidence) >= 1, f"{t.id}:evidence")
    for dep in t.dependencies:
        check(dep in BY_ID, f"{t.id}:dep:{dep}")

base = {"schema":"pocket.channel-envelope.v1","message_id":"msg-1","request_id":"req-1","from":"VOICE","to":"HOST","channel":"deploy","kind":"deploy","state":"published","side_effect":True,"approval":"confirm"}
sealed = hardened_envelope(base, ttl_s=60, now=1000)
check(sealed["ok"], "seal_ok")
env = sealed["envelope"]
check(env["expires_at"] == 1060, "expiry")
check(len(env["nonce"]) == 24, "nonce_len")
check(len(env["canonical_digest"]) == 64, "digest_len")
check(validate_hardened_envelope(env, now=1001)["ok"], "validate_ok")
check(not validate_hardened_envelope(env, now=2000)["ok"], "expiry_rejected")
check(not validate_hardened_envelope(env, now=1001, seen_nonces=[env["nonce"]])["ok"], "replay_rejected")
mut = dict(env); mut["state"] = "succeeded"
check(not validate_hardened_envelope(mut, now=1001)["ok"], "tamper_rejected")
check(not hardened_envelope({"schema":"x"}, now=1000)["ok"], "missing_fields_rejected")
bad = dict(base); bad["approval"] = "allow"
check(not hardened_envelope(bad, now=1000)["ok"], "side_effect_approval_rejected")

for i in range(64):
    d = canonical_digest({"i":i,"technology":TECHNOLOGIES[i % len(TECHNOLOGIES)].id})
    check(len(d) == 64, f"digest_vector_{i}")
    check(all(c in "0123456789abcdef" for c in d), f"digest_hex_{i}")

assertions = len(checks)
receipt = {
    "schema":"pocket.local-validation-receipt.v1",
    "suite":"technology-garden-hardening",
    "status":"passed",
    "assertions":assertions,
    "minimum":128,
    "ci_used":False,
    "validator_sha256":hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    "manifest_sha256":canonical_digest(hardening_manifest()),
    "generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
check(assertions >= 128, "minimum_assertions")
receipt["assertions"] = len(checks)
OUT = ROOT / "dist" / "proof"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "technology-garden-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
(OUT / "technology-garden-manifest.json").write_text(json.dumps(hardening_manifest(), indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, indent=2, sort_keys=True))
