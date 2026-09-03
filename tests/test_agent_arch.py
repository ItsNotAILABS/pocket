from pocket.agent_arch import LAYERS, SCHEMA, TURN, resolve, snapshot, turn
from pocket.agent_runtime import route_think


def test_arch_snapshot_has_six_layers():
    s = snapshot()
    assert s["ok"] is True
    assert s["schema"] == SCHEMA
    assert s["layers"] == list(LAYERS)
    assert "pocket" in s["seats"] and "phoneai" in s["seats"]
    assert "screen" in s["execute"]
    assert s["counts"]["personas"] >= 1
    assert "GET /v1/agents/arch" in s["http"]


def test_resolve_coder_persona_and_grok_first_class():
    c = resolve("coder")
    assert c["persona"] is True
    assert c["engine"] in ("grok", "coder")
    g = resolve("grok")
    assert g["first_class"] is True
    assert g["id"] == "grok"


def test_turn_think_does_not_silently_fanout():
    r = turn("explain a mutex", agent="researcher", seat="phoneai", engine="heuristic", dry=True)
    assert r["schema"] == TURN
    assert r["layers"]["seat"] == "phoneai"
    assert r["layers"]["route"]["engine"]
    assert r["layers"]["receipt"]["schema"] == "pocket.action_receipt.v1"
    assert r["phase"] == "dry"
    assert r["layers"]["execute"] == "harness"


def test_rah_wording_is_plan_without_grant():
    r = turn("split the work in parallel across several agents", seat="pocket")
    assert r["phase"] == "plan"
    assert r["layers"]["authority"]["required"] is True
    assert r["ok"] is True
    assert "grant" in (r["result"].get("hint") or "").lower()


def test_route_still_one_engine():
    t = route_think("write a pytest for the arch plane")
    assert t["engine"] == "grok"
    assert t.get("tool") in (None, "rah_run")
