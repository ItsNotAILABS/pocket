from pocket.phoneai_os_ui import phoneai_anti_html, phoneai_portal_html
from pocket.phoneai_portal import map_touch, snapshot


def test_map_touch_clamps_and_orders():
    a = map_touch(-2, -2)
    b = map_touch(0, 0)
    c = map_touch(1, 1)
    d = map_touch(3, 3)
    assert a["x"] == b["x"] and a["y"] == b["y"]
    assert d["x"] == c["x"] and d["y"] == c["y"]
    assert c["x"] >= b["x"] and c["y"] >= b["y"]


def test_portal_html_phone_zoom_and_controls():
    html = phoneai_portal_html()
    assert "scale(" in html
    assert 'id="joy"' in html
    assert 'id="lmb"' in html and 'id="rmb"' in html
    assert "kind==='drag'" in html or "gest==='drag'" in html
    assert "vk:8" in html
    assert "Pinch zooms the phone only" in html
    assert "/v1/phoneai/portal/touch" in html


def test_anti_html_has_working_gestures():
    html = phoneai_anti_html()
    assert "sendTouch('tap'" in html
    assert "sendTouch('right'" in html
    assert "sendTouch('drag'" in html


def test_snapshot_documents_phone_zoom():
    s = snapshot()
    assert s["phone_zoom"].startswith("view-only")
    assert "joystick" in s["controls"]
