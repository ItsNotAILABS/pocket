from pocket.agent_network import develop, list_developed, nodes, ship, snapshot, studios
from pocket.agent_runtime import route_think


def test_network_has_studios_and_nodes():
    n = {x["id"] for x in nodes()}
    assert {"host", "phoneai", "develop", "ship", "mcp", "public"} <= n
    s = {x["id"] for x in studios()}
    assert {"develop", "ship"} <= s
    snap = snapshot()
    assert snap["ok"] is True
    assert snap["product"] == "POCKET Network"


def test_develop_and_ship_agent(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.agent_network.ROOT", tmp_path)
    monkeypatch.setattr("pocket.agent_network.AGENTS_FILE", tmp_path / "agents.json")
    monkeypatch.setattr("pocket.phoneai_space.dual_write", lambda *a, **k: {"ok": True})
    r = develop({"id": "night-watch", "role": "watcher", "blurb": "watch the desk"})
    assert r.get("ok") is True
    assert r["agent"]["id"] == "night-watch"
    ids = {a["id"] for a in list_developed()}
    assert "night-watch" in ids
    sh = ship("night-watch", "git")
    assert sh.get("ok") is True
    assert sh["ship"]["target"] == "git"


def test_route_think_does_not_overuse_tools():
    r = route_think("what is a mutex")
    assert r["engine"] == "grok"
    assert r["tool"] is None
    r2 = route_think("implement a mutex in this file")
    assert r2["engine"] == "codex"
    assert r2["tool"] is None
    r3 = route_think("mint the twin workspace")
    assert r3["tool"] == "twin_mint"
    r4 = route_think("new pocket session")
    assert r4["tool"] == "session_new"
    r5 = route_think("prove this theorem with the logic prover")
    assert r5["engine"] == "logic"
