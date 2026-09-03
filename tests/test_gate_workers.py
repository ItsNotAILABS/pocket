from pathlib import Path

from pocket.rbac import allow_host_path
from pocket.tenant_jail import attach_team_to_job, jail, owner_from_user, safe_team_id, team_root


def _home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda *a, **k: tmp_path)


def test_tenant_jail_rejects_escape(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    root = team_root("pocket")
    root.mkdir(parents=True, exist_ok=True)
    try:
        jail(root, tmp_path / "escaped")
        raised = False
    except ValueError:
        raised = True
    assert raised
    try:
        safe_team_id("../escaped")
        bad = False
    except ValueError:
        bad = True
    assert bad
    assert owner_from_user({"user": "pocket"}) == "pocket"


def test_attach_job_sets_jailed_cwd(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    from pocket.team_workspace import open_team

    t = open_team("work", principal="pocket")
    job = {"team_id": t["id"], "owner": "pocket", "cwd": ""}
    attach_team_to_job(job)
    assert job.get("jailed") is True
    assert str(job["cwd"]).startswith(str(team_root("pocket")))


def test_team_worker_tick_and_status(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    from pocket.team_workspace import open_team
    from pocket.team_worker import status, tick

    open_team("pulse me", principal="pocket")
    r = tick(principal="pocket")
    assert r["ok"] is True
    assert r["teams"] >= 1
    assert status()["worker"] == "team"


def test_endure_worker_never_claims_learning(monkeypatch):
    from pocket.endure_worker import run, status

    class Fake:
        def as_dict(self):
            return {"ok": True, "text": "cycle"}

    monkeypatch.setattr("pocket.auro_endure._native", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no native")))
    monkeypatch.setattr("pocket.internal_models.registry.express_one", lambda *a, **k: Fake())
    r = run("keep going", experiments=1, cycles=0)
    assert r["learning"] is False
    assert r["native"] is False
    assert status()["learning"] is False


def test_mcp_dispatch_team_and_endure(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    from pocket.mcp_dispatch import dispatch, handles

    assert handles("team_open") and handles("endure_status")
    r = dispatch("team_open", {"goal": "ship", "principal": "pocket"})
    assert r.get("ok") is True
    st = dispatch("endure_status", {})
    assert st.get("learning") is False


def test_market_blocked_from_endure_and_team_tick():
    market = {"user": "alice", "role": "member", "edition": "market", "principal": "user"}
    for p in ("/v1/endure", "/v1/endure/run", "/v1/team/tick", "/v1/team/workers"):
        ok, _ = allow_host_path(market, p)
        assert ok is False, p


def test_create_job_attaches_team(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    from pocket.jobs import create_job
    from pocket.team_workspace import open_team

    t = open_team("job cwd", principal="pocket")
    j = create_job("hello", mode="plan", team_id=t["id"], owner="pocket")
    assert j["team_id"] == t["id"]
    assert j.get("jailed") is True
    assert Path(j["cwd"]).is_dir()
