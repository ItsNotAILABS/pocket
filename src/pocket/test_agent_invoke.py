"""Every first-class agent is on the roster and resolvable."""

from pocket.agent_invoke import _resolve, invoke, roster
from pocket.first_class_agents import build_registry


def test_roster_covers_first_class():
    fc = build_registry()
    r = roster()
    assert r["ok"]
    assert r["first_class"] == fc["count"]
    assert r["count"] >= fc["count"]
    assert fc["count"] >= 120


def test_every_first_class_id_resolves():
    fc = build_registry()
    missing = []
    for a in fc["agents"]:
        if _resolve(a["id"]) is None:
            missing.append(a["id"])
    assert missing == [], missing[:20]


def test_invoke_archon_help():
    out = invoke("ARCHON", job="help", prompt="")
    assert out.get("ok") is True
    blob = str(out.get("markdown") or "") + str(out.get("agent") or "") + str(out.get("resolved") or "")
    assert "ARCHON" in blob.upper()


def test_invoke_catalog_researcher_async():
    out = invoke("researcher", prompt="one-line what is POCKET", sync=False)
    assert out.get("ok") is True
    assert out.get("agent", "").endswith("researcher") or "researcher" in str(out.get("agent_id") or out.get("agent"))


def test_invoke_guppy_identity():
    out = invoke("guppy", job="identity")
    assert out.get("ok") is True
