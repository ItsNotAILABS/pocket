"""POCKET LIGHT shell: threads, seat receipt, page regions."""

from pocket.pocket_light import AGENTS, THREADS, open_loose, post, status, thread
from pocket.pocket_light_ui import HTML


def test_pocket_light_catalog_and_page():
    st = status()
    assert st["product"] == "POCKET LIGHT"
    assert st["app"] == "/pocket-light"
    ids = [row["id"] for row in st["threads"] if row["kind"] == "project"]
    assert [spec["id"] for spec in THREADS] == ids
    assert "senda" in ids and "loom" in ids and "metropolis" in ids and "vaul" in ids
    assert set(AGENTS) <= set(st["agents"])
    assert "POCKET LIGHT" in HTML
    assert 'id="projects"' in HTML
    assert 'id="rail"' in HTML
    assert 'id="preview"' in HTML
    assert "/v1/pocket-light/chat" in HTML


def test_pocket_light_loose_chat_seats_agent(monkeypatch, tmp_path):
    monkeypatch.setattr("pocket.pocket_light.ROOT", tmp_path)
    monkeypatch.setattr("pocket.pocket_light.STATE", tmp_path / "state.json")
    made = open_loose("scratch")
    assert made["ok"] is True
    view = post(made["id"], "look at the desk", agent="jev")
    assert view["ok"] is True
    assert view["agent"] == "jev"
    assert view["messages"][-1]["agent"] == "jev"
    assert "seated on scratch" in view["reply"]
    roles = [s["role"] for s in view["subagents"]]
    assert roles == ["files", "preview"]
    again = thread(made["id"])
    assert again["messages"][0]["text"] == "look at the desk"
