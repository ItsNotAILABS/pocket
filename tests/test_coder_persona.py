from pocket.agent_runtime import persona, personas, route_think
from pocket.coder_persona import context, record, wrap_task


def test_coder_is_grok_long_term_phoneai():
    p = persona("coder")
    assert p["engine"] == "grok"
    assert p["long_term"] is True
    assert p.get("seat") == "phoneai"


def test_coder_first_in_roster():
    assert personas()[0]["id"] == "coder"


def test_code_routes_to_grok_not_codex():
    r = route_think("implement the auth header test")
    assert r["engine"] == "grok"
    assert "coder" in r["why"]


def test_wrap_includes_family_and_phoneai():
    t = wrap_task("fix Portal tap focus")
    assert "CODER" in t
    assert "PhoneAI" in t
    assert "pocket-os" in t or "ItsNotAILABS/pocket" in t
    assert "fix Portal tap focus" in t


def test_record_aliases():
    rec = record()
    assert "grok_coder" in rec["aliases"]
    assert rec["keep"] is True


def test_context_mentions_family():
    c = context()
    assert "pocket" in c
    assert "phoneai" in c
