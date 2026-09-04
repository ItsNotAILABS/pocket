from pocket.crew import MAX_SEATS, board, close_seat, spawn, steer


def test_spawn_two_seats_side_by_side(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.crew.STATE", tmp_path / "crew.json")
    monkeypatch.setattr("pocket.crew.ROOT", tmp_path)
    monkeypatch.setattr(
        "pocket.phoneai_code_desk.ensure_repo_cwd",
        lambda repo: {"ok": True, "cwd": str(tmp_path / "repo"), "repo": repo, "cloned": False},
    )
    r = spawn(repo="ItsNotAILABS/pocket", clis=["grok", "codex"], parts=["portal", "auth"], goal="ship")
    assert r["ok"] is True
    assert len(r["lane"]["seats"]) == 2
    assert r["lane"]["seats"][0]["cli"] == "grok"
    assert r["lane"]["seats"][0]["part"] == "portal"
    assert r["lane"]["seats"][1]["cli"] == "codex"
    assert r["lane"]["seats"][1]["part"] == "auth"
    again = spawn(repo="ItsNotAILABS/pocket", clis=["gemini"], parts=["tests"])
    assert again["ok"] is False
    assert "2 seats" in (again.get("error") or "")
    b = board()
    assert b["layout"] == "side-by-side"
    assert b["max_seats"] == MAX_SEATS
    assert len(b["lanes"]) == 1


def test_steer_wait_calls_cli(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.crew.STATE", tmp_path / "crew.json")
    monkeypatch.setattr("pocket.crew.ROOT", tmp_path)
    monkeypatch.setattr(
        "pocket.phoneai_code_desk.ensure_repo_cwd",
        lambda repo: {"ok": True, "cwd": str(tmp_path), "repo": repo, "cloned": False},
    )

    def fake_run(text, *, cli="grok", repo="", cwd="", new=False, session_id=""):
        assert "portal" in text
        assert "Steer: fix lag" in text
        return {"ok": True, "engine": cli, "reply": "fixed"}

    monkeypatch.setattr("pocket.phoneai_code_desk.run", fake_run)
    r = spawn(repo="ItsNotAILABS/pocket", clis=["grok"], parts=["portal"])
    sid = r["added"][0]["id"]
    out = steer(sid, "fix lag", wait=True)
    assert out["ok"] is True
    assert "fixed" in (out.get("reply") or "")
    closed = close_seat(sid)
    assert closed["ok"] is True


def test_crew_html_is_side_by_side():
    from pocket.crew_ui import crew_html

    html = crew_html()
    assert "grid-template-columns:1fr 1fr" in html
    assert "/v1/crew/spawn" in html
    assert "/v1/crew/steer" in html
    assert "No extra OS windows" in html or "side by side" in html.lower()
