from pocket.agent_runtime import route_think
from pocket.engines import catalog, internal_reply


def test_catalog_lists_real_clis_and_internals():
    c = catalog()
    assert c["ok"] is True
    ids = {x["id"] for x in c["cli"]}
    assert "grok" in ids and "codex" in ids
    assert "auro" in {x["id"] for x in c["internal"]}
    assert "portal" in {x["id"] for x in c["surfaces"]}
    assert "antigravity" in {x["id"] for x in c["surfaces"]}


def test_internal_reply_runs():
    r = internal_reply("what is a mutex", prefer="heuristic")
    assert r.get("ok") is True
    assert r.get("internal") is True
    assert len(r.get("reply") or "") > 20


def test_route_think_picks_local_math():
    assert route_think("run the logic prover on this theorem")["engine"] == "logic"
    assert route_think("touch the pc from my phone")["engine"] == "portal"
