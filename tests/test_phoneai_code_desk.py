"""PhoneAI Code desk is CLIs + GitHubs, not attached agents."""

from pathlib import Path

from pocket.phoneai_code_desk import ALIASES, CLI_IDS, detect_clis, new_session, run, snapshot
from pocket.phoneai_bridge import work
from pocket.phoneai_os_ui import PHONEAI_TWIN_HTML


def test_wired_clis_are_the_five():
    assert CLI_IDS == ("grok", "codex", "meta", "gemini", "spark")
    ids = [c["id"] for c in detect_clis()]
    assert ids == list(CLI_IDS)


def test_aliases_map_to_wired_clis():
    assert ALIASES["muse"] == "meta"
    assert ALIASES["antigravity"] == "gemini"
    assert ALIASES["gemini-cli"] == "gemini"


def test_new_session_is_code_desk_not_agent(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_code_desk.SESS_FILE", tmp_path / "sess.json")
    monkeypatch.setattr("pocket.phoneai_code_desk.PHONE_WS", tmp_path / "ws")
    monkeypatch.setattr("pocket.phoneai_code_desk.ensure_repo_cwd", lambda repo: {"ok": True, "cwd": str(tmp_path / "ws"), "repo": repo, "cloned": False})
    r = new_session(cli="codex", repo="ItsNotAILABS/pocket", title="t")
    s = r["session"]
    assert r["ok"] is True
    assert s["id"].startswith("cd-")
    assert s["kind"] == "code-desk"
    assert s["cli"] == "codex"
    assert s["repo"] == "ItsNotAILABS/pocket"
    assert "persona" not in s
    assert "pocket_session" not in r


def test_work_does_not_fan_out_agents(monkeypatch):
    called = {}

    def fake_run(text, *, cli="grok", session_id="", repo="", cwd="", new=False):
        called.update(cli=cli, text=text, repo=repo, new=new, session_id=session_id)
        return {"ok": True, "engine": cli, "reply": "wired", "not_agents": True}

    monkeypatch.setattr("pocket.phoneai_code_desk.run", fake_run)
    r = work("fix the tests @codex @grok in parallel", engine="codex", repo="ItsNotAILABS/pocket")
    assert r["not_agents"] is True
    assert called["cli"] == "codex"
    assert "agents" not in r
    assert r.get("persona") is None


def test_run_empty_prompt():
    r = run("")
    assert r["ok"] is False


def test_snapshot_schema(monkeypatch):
    monkeypatch.setattr("pocket.phoneai_code_desk.github_repos", lambda limit=80: [])
    monkeypatch.setattr("pocket.phoneai_code_desk.local_repos", lambda: [{"id": "x", "name": "x", "full": "ItsNotAILABS/x", "local": "E:/repos/x", "source": "local", "url": ""}])
    monkeypatch.setattr("pocket.phoneai_code_desk.list_sessions", lambda limit=40: [])
    s = snapshot()
    assert s["schema"] == "phoneai.code-desk.v1"
    assert s["not_agents"] is True
    assert "grok" in s["cli_ids"]
    assert s["repo_count"] >= 1


def test_html_is_cli_and_repo_not_personas():
    html = PHONEAI_TWIN_HTML
    assert "/v1/phoneai/code-desk" in html
    assert "New session" in html
    assert "persona" not in html.lower()
    assert "/v1/phoneai/sessions" not in html
    assert "Glimmer" not in html
    assert "PhoneAI coder" not in html
    assert "data-e=\"auto\"" not in html
    assert "id=\"per\"" not in html
