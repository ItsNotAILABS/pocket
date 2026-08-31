import json
from pathlib import Path

from pocket import __version__
from pocket.corpus_architecture import (
    CLAIM_BOUNDARIES,
    EVIDENCE_CLASSES,
    EXECUTION_SEQUENCE,
    PRINCIPAL_TYPES,
    RUNTIME_CELLS,
    classify_claim,
    evidence_satisfies,
    product_contract,
    validate_contract,
)
from pocket.product import VERSION, doctor, feature_matrix
from pocket.product_channels import channels

ROOT = Path(__file__).resolve().parents[1]


def test_triform_product_is_complete_and_valid():
    contract = product_contract()
    assert validate_contract(contract) == []
    bodies = contract["triform_product"]["bodies"]
    assert [body["id"] for body in bodies] == ["cloud-account", "desktop-runtime", "edge-app"]
    assert bodies[0]["availability"] == "independent-of-user-device"
    assert "founder-local-files" in bodies[0]["does_not_own"]
    assert "local-models" in bodies[1]["owns"]
    assert "independent-model-brain" in bodies[2]["does_not_own"]


def test_identity_execution_and_runtime_cells_match_corpus():
    assert PRINCIPAL_TYPES == ("human", "organization", "agent", "model", "device", "api-client", "runtime-cell")
    assert EXECUTION_SEQUENCE == ("discover", "classify-risk", "plan", "approve", "execute", "validate", "receipt")
    assert RUNTIME_CELLS == ("agent-sandbox", "app-bottle", "mini-os")
    approval = product_contract()["governed_execution"]["approval"]
    assert approval["one_time"] is True
    assert approval["nonempty_approval_id_is_insufficient"] is True
    assert "arguments_hash" in approval["must_bind"]
    assert "nonce" in approval["must_bind"]


def test_evidence_classes_do_not_promote_unsupported_claims():
    assert EVIDENCE_CLASSES[0] == "E0-assertion"
    assert EVIDENCE_CLASSES[-1] == "E5-external-custody-and-reproduction"
    assert evidence_satisfies("E3-validated-output", "E2-execution-log") is True
    assert evidence_satisfies("E1-source", "E3-validated-output") is False
    result = classify_claim("cloud-production", "E1-source", "E3-validated-output", ["cloudflare/pocket-cloud/src/index.js"])
    assert result["decision"] == "insufficient-evidence"
    assert set(CLAIM_BOUNDARIES).issubset(set(product_contract()["claim_boundaries"]))


def test_product_channels_present_cloud_desktop_and_edge_without_conflation():
    catalog = channels()
    assert catalog["ok"] is True
    by_id = {item["id"]: item for item in catalog["channels"]}
    assert by_id["cloud_account"]["availability"] == "independent of local desktop uptime"
    assert "bundled local" in by_id["desktop"]["what"].lower()
    assert "not a separate product brain" in by_id["web_edge"]["what"].lower()
    assert "developer terminal" in catalog["decision"]["not"].lower()


def test_product_catalog_uses_package_version_and_exposes_new_contracts():
    assert VERSION == __version__
    features = {item["id"]: item for item in feature_matrix()}
    for feature in ("triform_product", "multi_user_organizations", "device_federation", "governed_execution", "evidence_classes"):
        assert feature in features
    report = doctor()
    assert report["version"] == __version__
    assert report["architecture"]["triform_product"]["schema"] == "pocket.triform-product.v1"


def test_ecosystem_surface_declares_corpus_contracts():
    surface = json.loads((ROOT / "ecosystem.surface.json").read_text(encoding="utf-8"))
    assert surface["product_contract"]["bodies"] == ["cloud-account", "desktop-runtime", "edge-app"]
    assert surface["execution_contract"]["runtime_cells"] == ["agent-sandbox", "app-bottle", "mini-os"]
    for contract in ("pocket.triform-product.v1", "nexus.device-federation.v1", "nexus.runtime-cell.v1", "nexus.evidence-classification.v1"):
        assert contract in surface["produces"]
