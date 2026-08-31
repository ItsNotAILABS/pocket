"""POCKET Bots — Grok-Bot-style teammates on pocket-agent."""

from pocket.bots import create_bot, create_from_prompt, list_bots, message
from pocket.platform_coherence import coherent, run_platform_skill


def test_hire_and_message(tmp_path, monkeypatch):
    import pocket.bots as bots

    monkeypatch.setattr(bots, "ROOT", tmp_path / "bots")
    (tmp_path / "bots").mkdir()
    hired = create_from_prompt("I need a math bot named Euclid for gcd and primes", owner="test")
    assert hired.get("ok")
    assert hired.get("engine") == "ghost"
    assert "euclid" in (hired.get("id") or hired.get("name") or "").lower() or hired.get("id")
    mid = hired["id"]
    r = message(mid, "gcd 48 18")
    assert r.get("ok")
    assert "reply" in r
    listed = list_bots(owner="test")
    assert any(b["id"] == mid for b in listed)


def test_bots_on_platform():
    ids = {s["id"] for s in coherent().get("surfaces") or []}
    assert "bots" in ids
    cat = run_platform_skill("bots_list")
    assert cat.get("ok")
    assert cat.get("ui") == "/bots"