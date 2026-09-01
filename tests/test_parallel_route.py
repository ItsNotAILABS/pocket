from pocket.agent_runtime import persona, route_think


def test_parallel_prompt_routes_to_rah():
    r = route_think("split the work in parallel across the family repos")
    assert r["engine"] == "rah"


def test_pocket_persona_exists():
    p = persona("pocket")
    assert p["id"] == "pocket"
    assert p.get("long_term") is True
