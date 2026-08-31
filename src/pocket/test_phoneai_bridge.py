"""PhoneAI client contract on the POCKET host."""

from pocket.phoneai_bridge import health, pair_auto, execute, TOOLS


def test_health_ready_without_mongo():
    h = health()
    assert h["status"] == "ready"
    assert h["pocket"] is True
    assert h["mongo"] is False
    assert "hostname" in h["substrate"]


def test_auto_pair_and_execute_status(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_bridge.ROOT", tmp_path / "phoneai")
    monkeypatch.setattr("pocket.phoneai_bridge.WS", tmp_path / "ws")
    monkeypatch.setattr("pocket.phoneai_bridge.STATE", tmp_path / "phoneai" / "state.json")
    sess = pair_auto(allow=True)
    assert sess.get("token", "").startswith("phoneai_")
    doc = execute(
        {"session_id": sess["session_id"]},
        {"tool_id": "list_directory", "params": {"path": "."}},
    )
    assert doc.get("ok") is True
    assert doc.get("status") == "succeeded"
    ids = {t["id"] for t in TOOLS}
    assert "pocket_status" in ids
    assert {"grok_ask", "codex_ask", "antigravity", "spark_ask"} <= ids


def test_pick_engine_auto():
    from pocket.phoneai_bridge import _pick_engine

    assert _pick_engine("open this in antigravity", "auto") == "antigravity"
    assert _pick_engine("fix this file with tests", "auto") == "codex"
    assert _pick_engine("explain the kernel", "auto") == "grok"
    assert _pick_engine("use muse spark on this", "auto") == "spark"
    assert _pick_engine("hello", "spark") == "spark"
    assert _pick_engine("run ollama", "auto") == "spark"
    assert _pick_engine("remind me to call mom", "auto") == "life"


def test_ask_engine_does_not_resume_live_grok(monkeypatch):
    from pocket.phoneai_bridge import _attach_thread

    monkeypatch.setenv("GROK_SESSION_ID", "01a045ce-13bd-7033-858b-0f96ba27a20f")
    assert _attach_thread("grok", "") is None
    assert _attach_thread("grok", "01a045ce-13bd-7033-858b-0f96ba27a20f") is None
    assert _attach_thread("grok", "s-abc") is None
    assert _attach_thread("grok", "pa-abc") is None
