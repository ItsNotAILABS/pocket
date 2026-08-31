from pocket.model_mesh import LANES, inventory, route


def test_catalog_has_local_and_agent_lanes():
    ids = {x.id for x in LANES}
    assert {"ollama", "llama.cpp", "opencode", "aider", "gemini-cli", "qwen-code"} <= ids
    assert any(x.privacy == "local" for x in LANES)
    assert any(x.kind == "coding-agent" for x in LANES)


def test_inventory_is_stable_shape():
    rows = inventory()
    assert len(rows) == len(LANES)
    assert all("available" in row and "capabilities" in row for row in rows)


def test_route_returns_contract_even_without_installed_cli():
    out = route("code and test this repository")
    assert out["task"] == "code and test this repository"
    assert "code" in out["wanted"]
    assert "agent" in out["wanted"]
    assert isinstance(out["alternates"], list)
