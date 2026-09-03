import inspect
from pathlib import Path

from pocket.rbac import FOUNDER_ONLY_PATH_PREFIXES, allow_host_path
from pocket.team_workspace import bind_workflow, get, invite, list_teams, note, open_team, snapshot


def _home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda *a, **k: tmp_path)


def test_open_team_is_on_disk(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    t = open_team("ship the protocol", agents=["codex", "grok"], label="proto", principal="pocket")
    assert t["ok"] is True
    assert t["schema"] == "pocket.team.workspace.v1"
    assert t["owner"] == "pocket"
    assert "codex" in t["engines"] or "codex" in t["agents"]
    cwd = Path(t["cwd"])
    assert cwd.is_dir()
    assert str(cwd.resolve()).startswith(str((tmp_path / ".pocket" / "tenants" / "pocket" / "teams").resolve()))
    assert (cwd / "README.md").is_file()
    n = note(t["id"], "first handoff", agent="codex", principal="pocket")
    assert n["ok"] is True
    inv = invite(t["id"], "auro-endure", principal="pocket")
    assert "auro-endure" in inv["agents"]
    bind_workflow(t["id"], "wf-test", principal="pocket")
    again = get(t["id"], principal="pocket")
    assert "wf-test" in again["workflows"]
    listed = list_teams(principal="pocket")
    assert listed["count"] >= 1
    snap = snapshot(principal="pocket")
    assert snap["protocol"] == "POCKET-TEAM-WORKSPACE/1.0"
    assert snap["founder_only"] is True


def test_path_escape_rejected(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    for bad in ("../escaped", "..\\escaped", "foo/../../escaped", "team/../x", "a" * 40):
        r = open_team("x", team_id=bad, principal="pocket")
        assert r.get("ok") is False
        assert r.get("error")
    assert not (tmp_path / "escaped").exists()
    assert not list(tmp_path.glob("escaped/**"))
    goods = list((tmp_path / ".pocket" / "tenants").rglob("TEAM.json"))
    assert goods == []


def test_tenant_isolation(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    a = open_team("alice work", principal="alice")
    b = open_team("bob work", principal="bob")
    assert a["ok"] and b["ok"]
    assert get(a["id"], principal="bob").get("ok") is False
    assert get(b["id"], principal="alice").get("ok") is False
    assert list_teams(principal="alice")["count"] == 1
    assert list_teams(principal="bob")["count"] == 1
    assert "alice" in a["cwd"] and "bob" in b["cwd"]


def test_market_cannot_open_team_routes():
    market = {"user": "alice", "role": "member", "edition": "market", "principal": "user"}
    founder = {"user": "pocket", "role": "admin", "edition": "founder", "is_owner": True, "principal": "legacy"}
    for p in ("/v1/team", "/v1/team/workspace", "/v1/team/open", "/v1/team/invite", "/v1/teams", "/v1/teams/open"):
        ok, _ = allow_host_path(market, p)
        assert ok is False, p
        ok_f, _ = allow_host_path(founder, p)
        assert ok_f is True, p
    assert "/v1/team" in FOUNDER_ONLY_PATH_PREFIXES
    assert "/v1/teams" in FOUNDER_ONLY_PATH_PREFIXES


def test_mcp_team_open_is_not_nested_in_screen():
    from pocket import mcp_bundle
    from pocket.mcp_dispatch import handles

    src = inspect.getsource(mcp_bundle._invoke_pocket)
    gate_pos = src.find("gate_handles")
    screen_pos = src.find('if t in ("screen_embody"')
    assert 0 <= gate_pos < screen_pos
    assert handles("team_open")
    assert handles("endure_run")
    assert not handles("screen_embody")


def test_mcp_team_open_runs(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    from pocket.mcp_bundle import _invoke_pocket

    r = _invoke_pocket("team_open", {"goal": "ship", "principal": "pocket"})
    assert r.get("ok") is True
    assert Path(r["cwd"]).is_dir()
    listed = _invoke_pocket("team_list", {"principal": "pocket"})
    assert listed.get("count") >= 1


def test_jobs_carry_team_id():
    from pocket.jobs import create_job, get as job_get

    j = create_job("tick team", mode="plan", team_id="team-abc", cwd="C:/tmp", owner="pocket")
    assert j["team_id"] == "team-abc"
    assert j["owner"] == "pocket"
    again = job_get(j["id"])
    assert again["team_id"] == "team-abc"
