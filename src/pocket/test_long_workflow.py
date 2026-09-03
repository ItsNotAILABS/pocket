"""Long workflows persist context and compact."""

from pocket.kernels import long_workflow as lw


def test_start_tick_stop_persists():
    r = lw.start("hold a long context about POCKET desk", interval_sec=99999, max_hours=1, keep=False, auto_arm=False)
    assert r["ok"] and r["id"].startswith("wf-")
    assert r["host_bound"] is True
    assert r.get("team_id")
    assert r.get("cwd")
    assert r["max_hours"] >= 1
    wid = r["id"]
    t = lw.tick(wid)
    assert t["ok"]
    assert t["tick"]["n"] == 1
    g = lw.get(wid)
    assert g["tick_count"] == 1
    assert g["context_chars"] > 0
    # disk
    assert lw._path(wid).exists()
    s = lw.stop(wid, reason="test")
    assert s["status"] == "done"


def test_compact_keeps_tail():
    r = lw.start("compact me", interval_sec=99999, max_hours=1, keep=False, auto_arm=False)
    wid = r["id"]
    wf = lw._load(wid)
    wf["ticks"] = [{"n": i, "ok": True, "note": f"tick {i}"} for i in range(1, 90)]
    wf["tick_count"] = 89
    lw._compact(wf)
    assert len(wf["ticks"]) == lw.KEEP_TICKS_FULL
    assert wf["compacted"]
    lw.stop(wid, reason="test")
