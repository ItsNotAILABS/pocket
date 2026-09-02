from pocket.phoneai_os_ui import phoneai_anti_html, phoneai_portal_html
from pocket.phoneai_portal import (
    check_portal_token,
    map_touch,
    mint_portal_token,
    origin_ok,
    snapshot,
    touch_allowed,
)


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
    assert 'id="lmb"' in html and 'id="rmb"' in html
    assert 'id="sup"' in html and 'id="sdn"' in html
    assert "L click" in html
    assert 'id="focusBtn"' in html
    assert 'id="moveBtn"' in html
    assert 'id="joy"' in html
    assert "layout()" in html
    assert "setPhoneFocus" in html
    assert "phoneFocus" in html
    assert "Entire PC" in html or "full computer" in html.lower() or "full PC" in html or "Laptop" in html
    assert "WebSocket" in html
    assert "netProfile" in html
    assert "data-f=\"contain\"" in html or "data-f='contain'" in html
    assert "maximize" in html
    assert "vk:8" in html
    assert "move_window" in html
    assert "/v1/phoneai/portal/touch" in html
    assert "/v1/phoneai/portal/ws" in html
    assert "touchstart" in html
    assert "hud-off" in html
    assert "position:fixed" in html
    assert 'id="hudbtn"' in html
    assert "visualViewport" in html
    assert "credentials:'include'" in html or 'credentials:"include"' in html
    assert "emitScroll" in html or "kind:'scroll'" in html or 'kind,"scroll"' in html or "send('scroll'" in html


def test_anti_html_has_working_gestures():
    html = phoneai_anti_html()
    assert "sendTouch('tap'" in html
    assert "sendTouch('right'" in html
    assert "sendTouch('drag'" in html


def test_snapshot_documents_phone_zoom():
    s = snapshot()
    assert s["phone_zoom"].startswith("view-only")
    assert "window-focus" in s["controls"]
    assert "scroll" in s["controls"]
    assert "open-app" in s["controls"]


def test_touch_allowed_on_named_tunnel():
    assert touch_allowed({}, ("127.0.0.1", 1)) is True
    tok = mint_portal_token("phoneai")
    assert check_portal_token(tok)
    assert check_portal_token("123.abc") is False
    assert touch_allowed({"Cookie": "pocket_portal=" + tok, "CF-Connecting-IP": "1.2.3.4"}, ("1.2.3.4", 443)) is True
    assert touch_allowed({"Host": "evil.example", "CF-Connecting-IP": "1.2.3.4"}, ("1.2.3.4", 443)) is False


def test_origin_and_token_security():
    assert origin_ok({}, ("127.0.0.1", 1)) is True
    assert origin_ok({"CF-Connecting-IP": "8.8.8.8"}, ("127.0.0.1", 1)) is False
    assert origin_ok({"Origin": "https://pocket.medinatechlabs.net", "Host": "pocket.medinatechlabs.net"}) is True
    assert origin_ok({"Origin": "https://evil.example", "Host": "pocket.medinatechlabs.net"}) is False
    assert check_portal_token("nope") is False
    html = phoneai_portal_html()
    assert "Fit is 1:1" in html or "layout()" in html
    assert "5G" in html


def test_windows_list_and_html_tabs():
    from pocket.phoneai_portal import windows

    w = windows()
    assert w["ok"] is True
    assert "windows" in w
    html = phoneai_portal_html()
    assert 'id="tabs"' in html
    assert 'id="apps"' in html
    assert 'id="sup"' in html and 'id="sdn"' in html
    assert "portal/windows" in html
    assert "portal/apps" in html
    assert "kind==='focus'" in html or "focus" in html
    assert "kind==='open'" in html or "send('open'" in html
