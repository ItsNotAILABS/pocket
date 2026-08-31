"""Doctrine machine form — 30 stable laws, public card."""

from pocket.doctrine import CARD, FORBIDDEN, LAWS, OATH, manifesto


def test_thirty_laws_stable_ids():
    ids = [x["id"] for x in LAWS]
    assert ids == [f"L{i}" for i in range(1, 31)]
    assert len(set(ids)) == 30


def test_manifesto_shape():
    m = manifesto()
    assert m["ok"] is True
    assert m["schema"] == "pocket.doctrine.v1"
    assert m["binding"] is True
    assert m["law_count"] == 30
    assert "Desk is home" in CARD
    assert len(OATH) == 10
    assert len(FORBIDDEN) >= 20
    assert any(f["id"] == "owner" for f in m["faces"])
