from pocket.crypto import ALG, decrypt_bytes, encrypt_bytes
from pocket.feature_fabric import snapshot
from pocket.rah import _RAH_ESCALATE_MODES


def test_vault_roundtrip_mac():
    blob = encrypt_bytes("founder", b"secret-note")
    assert blob["alg"] == ALG
    assert "mac" in blob
    assert decrypt_bytes("founder", blob) == b"secret-note"


def test_fabric_wires_twenty():
    s = snapshot()
    assert s["count"] >= 20
    assert s["ok"] is True
    assert "auro" in _RAH_ESCALATE_MODES
