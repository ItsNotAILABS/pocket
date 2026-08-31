from pocket.phone_life import act, classify


def test_classify_phone_tasks():
    assert classify("remind me to call mom") == "remind"
    assert classify("directions to the grocery store") == "maps"
    assert classify("draft a text: running late") == "sms"
    assert classify("add milk to the shopping list") == "list"
    assert classify("explain recursion") == "chat"


def test_note_and_reminder(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phone_life.ROOT", tmp_path)
    monkeypatch.setattr("pocket.phone_life.NOTES", tmp_path / "notes.json")
    monkeypatch.setattr("pocket.phone_life.REMIND", tmp_path / "reminders.json")
    monkeypatch.setattr("pocket.phone_life.LISTS", tmp_path / "lists.json")
    monkeypatch.setattr("pocket.phone_life.dual_write", lambda *a, **k: {"ok": True})
    n = act("note", "buy batteries")
    assert n["ok"] is True
    r = act("remind", "remind me to stretch")
    assert "stretch" in r["reply"]
    m = act("maps", "directions to Austin")
    assert "maps.google.com" in (m.get("url") or "")
