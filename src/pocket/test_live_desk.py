"""Live desk lists real Grok/Codex threads."""

from pocket.live_desk import desk, grok_threads, pick_thread


def test_desk_lists_engines():
    d = desk(limit=5)
    assert d.get("ok") is True
    assert "you_are_working_on" in d
    assert "grok" in d and "codex" in d
    assert "antigravity_threads" in d
    live = d.get("you_are_working_on")
    if live:
        assert live.get("id")
        assert "phoneai_ws" not in (live.get("cwd") or "").replace("\\", "/").lower() or not grok_threads(3)


def test_pick_thread_returns_something_or_none():
    t = pick_thread("grok")
    if t:
        assert t.get("engine") in ("grok", "codex", "pocket") or t.get("id")
