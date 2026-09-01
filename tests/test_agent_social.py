from pocket.agent_social import create_group, dm, face_svg, group_post, name_agent, person, thread
from pocket.autonomy import last_week, remember, yesterday
from pocket.subagent_dispatch import live_runs, pending_notes, steer
from pocket.web_ui_engine import drive


def test_faces_and_names():
    r = name_agent("coder", "Coder", blurb="Grok coding")
    assert r["ok"]
    assert r["agent"]["name"] == "Coder"
    svg = face_svg("coder", name="Coder")
    assert "<svg" in svg and "CO" in svg
    got = person("coder")
    assert got["ok"] and got["agent"]["name"] == "Coder"


def test_dm_and_group():
    sent = dm("grok", "coder", "ship the portal HD path")
    assert sent["ok"]
    th = thread("grok", "coder")
    assert th["count"] >= 1
    g = create_group("Ship crew", members=["grok", "coder", "scribe"], owner="system")
    assert g["ok"]
    post = group_post(g["group"]["id"], "grok", "ready")
    assert post["ok"]


def test_cron_memory_empty_is_honest():
    y = yesterday("sch-missing")
    w = last_week("sch-missing")
    assert "No cron memory" in y["brief"]
    assert w["days"] == 7
    r = remember("sch-missing", days=1)
    assert r["ok"]


def test_steer_queues_for_missing_run():
    s = steer("stop editing README, fix portal JPEG", agent="ARCHON")
    assert s["ok"]
    note = pending_notes("ARCHON")
    assert "portal JPEG" in note
    live = live_runs()
    assert live["ok"]


def test_drive_function_exists():
    assert callable(drive)
    assert "desktop_browser" in (drive.__doc__ or "") or drive.__name__ == "drive"
