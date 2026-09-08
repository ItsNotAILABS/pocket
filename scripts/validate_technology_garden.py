from __future__ import annotations
import json, sys, hashlib, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pocket.technology_garden import TECHNOLOGIES, BY_ID, ranked, validate_dependency_graph, hardened_envelope, validate_hardened_envelope, hardening_manifest, canonical_digest
from pocket.channel_fabric import envelope, validate_envelope, authorize_consequence

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

# Isolated hardening vectors.
base = {"schema":"pocket.channel-envelope.v1","message_id":"msg-1","request_id":"req-1","from":"VOICE","to":"HOST","channel":"deploy","kind":"deploy","state":"published","side_effect":True,"approval":"confirm"}
sealed = hardened_envelope(base, ttl_s=60, now=1000)
check(sealed["ok"], "seal_ok")
env = sealed["envelope"]
check(env["expires_at"] == 1060, "expiry")
check(len(env["nonce"]) == 24, "nonce_len")
check(len(env["canonical_digest"]) == 64, "digest_len")
pending = validate_hardened_envelope(env, now=1001)
check(pending["ok"], "pending_integrity_valid")
check(not pending["authorized"], "pending_not_authorized")
check(not validate_hardened_envelope(env, now=2000)["ok"], "expiry_rejected")
check(not validate_hardened_envelope(env, now=1001, seen_nonces=[env["nonce"]])["ok"], "replay_rejected")
mut = dict(env); mut["state"] = "succeeded"
check(not validate_hardened_envelope(mut, now=1001)["ok"], "tamper_rejected")
check(not hardened_envelope({"schema":"x"}, now=1000)["ok"], "missing_fields_rejected")
bad = dict(base); bad["approval"] = "allow"
check(not hardened_envelope(bad, now=1000)["ok"], "side_effect_approval_rejected")

denied = dict(base); denied["message_id"] = "msg-deny"; denied["approval"] = "deny"
denied_sealed = hardened_envelope(denied, ttl_s=60, now=1000)
check(denied_sealed["ok"], "denial_can_be_sealed_as_evidence")
denied_validation = validate_hardened_envelope(denied_sealed["envelope"], now=1001)
check(not denied_validation["ok"], "denial_is_terminal_refusal")
check(not denied_validation["authorized"], "denial_never_authorizes")
check(denied_validation["terminal"], "denial_terminal")
check("approval_denied" in denied_validation["violations"], "denial_reason")

approved = dict(base); approved["message_id"] = "msg-approved"; approved["approval"] = "approved"
approved_sealed = hardened_envelope(approved, ttl_s=60, now=1000)
approved_validation = validate_hardened_envelope(approved_sealed["envelope"], now=1001)
check(approved_validation["ok"], "approved_valid")
check(approved_validation["authorized"], "approved_authorized")

# Critical integration vectors: test the actual channel_fabric create -> transport -> ingress path.
roundtrip_read = envelope(sender="agent", recipient="host", channel_name="proof", kind="verify", body={"case":"roundtrip-read"})
read_validation = validate_envelope(roundtrip_read, now=float(roundtrip_read["created_at"]) + 1)
check(read_validation["ok"], "channel_roundtrip_read_ok")
check(read_validation["authorized"], "channel_roundtrip_read_authorized")
check("digest_mismatch" not in read_validation["violations"], "channel_diagnostic_not_in_digest")

roundtrip_pending = envelope(sender="voice", recipient="host", channel_name="deploy", kind="deploy", body={"case":"pending"}, side_effect=True, approval="confirm")
pending_gate = authorize_consequence(roundtrip_pending, now=float(roundtrip_pending["created_at"]) + 1)
check(pending_gate["ok"], "channel_pending_integrity_ok")
check(not pending_gate["authorized"], "channel_pending_not_authorized")
check(not pending_gate["execute"], "channel_pending_blocked")
check(pending_gate["decision"] == "blocked", "channel_pending_decision")

roundtrip_deny = envelope(sender="voice", recipient="host", channel_name="deploy", kind="deploy", body={"case":"deny"}, side_effect=True, approval="deny")
deny_gate = authorize_consequence(roundtrip_deny, now=float(roundtrip_deny["created_at"]) + 1)
check(not deny_gate["ok"], "channel_deny_not_ok")
check(not deny_gate["authorized"], "channel_deny_not_authorized")
check(not deny_gate["execute"], "channel_deny_no_execution")
check(deny_gate["decision"] == "denied", "channel_deny_terminal_decision")

roundtrip_approved = envelope(sender="voice", recipient="host", channel_name="deploy", kind="deploy", body={"case":"approved"}, side_effect=True, approval="approved")
approved_gate = authorize_consequence(roundtrip_approved, now=float(roundtrip_approved["created_at"]) + 1)
check(approved_gate["ok"], "channel_approved_ok")
check(approved_gate["authorized"], "channel_approved_authorized")
check(approved_gate["execute"], "channel_approved_executes")

roundtrip_tamper = dict(roundtrip_approved); roundtrip_tamper["body"] = {"case":"tampered"}
tamper_gate = authorize_consequence(roundtrip_tamper, now=float(roundtrip_tamper["created_at"]) + 1)
check(not tamper_gate["ok"], "channel_tamper_rejected")
check(not tamper_gate["execute"], "channel_tamper_no_execution")

roundtrip_replay = authorize_consequence(roundtrip_approved, now=float(roundtrip_approved["created_at"]) + 1, seen_nonces=(roundtrip_approved["nonce"],))
check(not roundtrip_replay["ok"], "channel_replay_rejected")
check(not roundtrip_replay["execute"], "channel_replay_no_execution")

for i in range(64):
    d = canonical_digest({"i":i,"technology":TECHNOLOGIES[i % len(TECHNOLOGIES)].id})
    check(len(d) == 64, f"digest_vector_{i}")
    check(all(c in "0123456789abcdef" for c in d), f"digest_hex_{i}")

assertions_before_minimum = len(checks)
check(assertions_before_minimum >= 128, "minimum_assertions")
validator_hash = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
receipt = {
    "schema":"pocket.local-validation-receipt.v2",
    "suite":"technology-garden-hardening",
    "status":"passed",
    "assertions":len(checks),
    "minimum":128,
    "ci_used":False,
    "integration_roundtrip_tested":True,
    "authorization_semantics_tested":True,
    "validator_sha256":validator_hash,
    "manifest_sha256":canonical_digest(hardening_manifest()),
    "generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
OUT = ROOT / "dist" / "proof"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "technology-garden-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
(OUT / "technology-garden-manifest.json").write_text(json.dumps(hardening_manifest(), indent=2, sort_keys=True) + "\n")
print(json.dumps(receipt, indent=2, sort_keys=True))
