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


def test_pick_thread_does_not_auto_attach():
    t = pick_thread("grok")
    assert t is None
    t2 = pick_thread("grok", "s-not-a-real-thread")
    assert t2 is None


def test_antigravity_threads_get_human_names():
    from pocket.live_desk import _name_antigravity, real_antigravity_apps

    n = _name_antigravity(
        [
            "file:///C:/Users/Medin/.gemini/antigravity/worktrees/AIEOSpro/build-sovereign-crypto-platform",
            "https://github.com/FreddyCreates/pegasus-battleops.git",
        ],
        "d060938c-0680-49c8-9dcf-87b31c81ee51",
    )
    assert "Sovereign" in n["title"] or "Aieospro" in n["title"] or "AIEOS" in n["title"]
    assert "wfile" not in n["title"].lower()
    assert n["title"] != "d060938c-0680-49c8-9dcf-87b31c81ee51"
    apps = real_antigravity_apps()
    if apps:
        assert apps[0]["name"]
        assert " " in apps[0]["name"] or apps[0]["name"][0].isupper()
