from pocket.team_workspace import bind_workflow, get, invite, list_teams, note, open_team, snapshot


def test_open_team_is_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.team_workspace.ROOT", tmp_path)
    t = open_team("ship the protocol", agents=["codex", "grok"], label="proto")
    assert t["ok"] is True
    assert t["schema"] == "pocket.team.workspace.v1"
    assert "codex" in t["engines"] or "codex" in t["agents"]
    cwd = t["cwd"]
    from pathlib import Path

    assert Path(cwd).is_dir()
    assert (Path(cwd) / "README.md").is_file()
    n = note(t["id"], "first handoff", agent="codex")
    assert n["ok"] is True
    inv = invite(t["id"], "auro-endure")
    assert "auro-endure" in inv["agents"]
    bind_workflow(t["id"], "wf-test")
    again = get(t["id"])
    assert "wf-test" in again["workflows"]
    listed = list_teams()
    assert listed["count"] >= 1
    snap = snapshot()
    assert snap["protocol"] == "POCKET-TEAM-WORKSPACE/1.0"
