"""POCKET Live companion + tech atlas."""

from pocket.live_companion import chat, status
from pocket.tech_atlas import catalog


def test_atlas_includes_phoneai_and_apps():
    c = catalog()
    ids = [p["id"] for p in c["products"]]
    assert "phoneai" in ids
    assert "pocket" in ids
    urls = {a["url"] for a in c["apps"]}
    assert "/phoneai" in urls
    assert "/desk" in urls
    assert c["stack"]


def test_local_companion_lists_tech():
    r = chat("list all my technology and repos")
    assert r.get("ok") is True
    assert "POCKET" in (r.get("reply") or "")
    assert r.get("companion") == "POCKET Live"


def test_companion_can_open_phoneai():
    r = chat("open PhoneAI kernel")
    assert r.get("ok")
    assert r.get("open") == "/phoneai"


def test_companion_status():
    s = status()
    assert s.get("ok")
    assert s.get("name") == "POCKET Live"


def test_companion_uses_host_for_status():
    r = chat("status of CLIs and engines")
    assert r.get("ok")
    body = (r.get("reply") or "").lower()
    assert "cli" in body or "engine" in body or r.get("used")
