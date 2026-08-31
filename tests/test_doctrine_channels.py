from pocket.channel_fabric import CHANNELS, envelope, manifest as channel_manifest, route_for
from pocket.doctrine_laws import LAW_SET, manifest as law_manifest, validate_message
from pocket.hz_mesh import HZ_LANES, list_lanes


def test_doctrine_law_count_and_core_laws():
    m = law_manifest()
    assert m["count"] == 15
    names = {x["name"] for x in LAW_SET}
    assert "Continuity Law" in names
    assert "Model Non-Authority Law" in names
    assert "Envelope Truth Law" in names


def test_channel_fabric_has_all_required_planes():
    required = {"user", "heartbeat", "design", "security", "ship", "intel", "model", "memory", "proof", "voice", "deploy", "recovery"}
    assert required <= set(CHANNELS)
    assert len(CHANNELS) >= 12
    assert len({v["hz"] for v in CHANNELS.values()}) == len(CHANNELS)


def test_channel_envelope_is_addressed_and_lineaged():
    msg = envelope(sender="ARCHON", recipient="AURO_MESIE", channel_name="model", kind="spectral.embed", body={"record":"x"}, request_id="req-1")
    assert msg["schema"] == "pocket.channel-envelope.v1"
    assert msg["request_id"] == "req-1"
    assert msg["from"] == "ARCHON"
    assert msg["to"] == "AURO_MESIE"
    assert msg["logical_hz"] == 6
    assert msg["law_validation"]["ok"] is True


def test_side_effect_requires_explicit_approval_semantics():
    msg = envelope(sender="VOICE", recipient="FORGE", channel_name="deploy", kind="deploy", body={}, side_effect=True)
    assert msg["approval"] == "confirm"
    assert msg["risk"] == "high"


def test_success_without_evidence_is_rejected():
    msg = {
        "schema":"pocket.channel-envelope.v1", "request_id":"r", "from":"A", "to":"B",
        "channel":"proof", "kind":"verify", "state":"succeeded"
    }
    result = validate_message(msg)
    assert result["ok"] is False
    assert any("success lacks evidence" in x for x in result["violations"])


def test_hz_is_explicitly_logical_not_rf():
    h = list_lanes()
    assert h["logical_hz"] is True
    assert h["physical_frequency_claim"] is False
    assert h["physical_hz_reference"] == "AURO/MESIE mesie.edge.hz_ladder"
    assert HZ_LANES["proof"]["hz"] == 8


def test_routing_maps_model_and_deploy_consequences():
    assert route_for("spectral embedding")["name"] == "model"
    assert route_for("release", consequence="external")["name"] == "deploy"


def test_transport_manifest_is_multi_transport():
    m = channel_manifest()
    assert "mcp" in m["transports"]
    assert "websocket" in m["transports"]
    assert "mesh-disk" in m["transports"]
