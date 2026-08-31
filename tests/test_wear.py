from pocket.phoneai_os_ui import phoneai_glasses_html
from pocket.wear import USES, command, glance_card, strip_wake


def test_snapshot_has_glasses_and_airpods():
    from pocket.wear import snapshot

    s = snapshot()
    assert "/phoneai/glasses" in s["glasses"]["url"]
    assert "/phoneai/airpods" in s["airpods"]["url"]
    ids = {u["id"] for u in s["uses"]}
    assert {"wake", "glance", "camera", "spatial", "hud", "dictation"} <= ids
    assert len(s["glance"]["lines"]) == 3


def test_wake_word_strips():
    rest, woke = strip_wake("PhoneAI look")
    assert woke is True
    assert rest.lower() == "look"
    rest2, woke2 = strip_wake("hey phoneai left window")
    assert woke2 is True
    assert "left" in rest2.lower()


def test_always_listen_ignores_without_wake():
    r = command("open edge", always=True)
    assert r.get("kind") == "ignore"


def test_help_command():
    r = command("what can you do")
    assert r["ok"] is True
    assert "PhoneAI" in r["reply"] or "look" in r["reply"]


def test_empty_command():
    r = command("")
    assert r["ok"] is False


def test_dictation_lock():
    command("stop dictation")
    on = command("dictation")
    assert on.get("on") is True
    command("hello world", always=False)
    sent = command("send")
    assert sent.get("kind") == "dictation"
    command("stop dictation")


def test_glance_card_lines():
    g = glance_card()
    assert len(g["lines"]) == 3
    assert g["reply"]


def test_glasses_html_wake_dictation_camera():
    html = phoneai_glasses_html()
    assert "PhoneAI" in html
    assert "Dictation" in html
    assert "getUserMedia" in html
    assert "left window" in html
    assert "SpeechRecognition" in html
    assert len(USES) >= 10
