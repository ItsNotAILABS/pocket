from pocket.phoneai_os_ui import phoneai_glasses_html
from pocket.wear import USES, command, snapshot


def test_snapshot_has_glasses_and_airpods():
    s = snapshot()
    assert "/phoneai/glasses" in s["glasses"]["url"]
    assert "/phoneai/airpods" in s["airpods"]["url"]
    ids = {u["id"] for u in s["uses"]}
    assert {"glance", "listen", "speak", "focus", "open", "coder"} <= ids


def test_help_command():
    r = command("what can you do")
    assert r["ok"] is True
    assert "look" in r["reply"] or "glance" in r["reply"]


def test_empty_command():
    r = command("")
    assert r["ok"] is False


def test_glasses_html_listen_and_tts():
    html = phoneai_glasses_html()
    assert "SpeechRecognition" in html
    assert "speechSynthesis" in html
    assert "/v1/phoneai/wear" in html
    assert "AirPods" in html
    assert len(USES) >= 8
