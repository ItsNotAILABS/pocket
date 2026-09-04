from pocket.phoneai_os_ui import phoneai_anti_html, phoneai_portal_html
from pocket.phoneai_portal import (
    check_portal_token,
    map_touch,
    mint_portal_token,
    origin_ok,
    snapshot,
    touch_allowed,
)


def test_virtual_desktop_module_no_keybd():
    import inspect
    from pocket import virtual_desktop as vd

    src = inspect.getsource(vd)
    assert "keybd_event" not in src
    r = vd.move_hwnds_to_other_desktop([])
    assert r.get("moved") == 0


def test_park_moves_pocket_off_work_display(monkeypatch):
    from pocket import screen_share as ss

    mons = [
        {"id": 0, "x": 0, "y": 0, "w": 1920, "h": 1080, "primary": True},
        {"id": 1, "x": 1920, "y": 0, "w": 1080, "h": 1920, "primary": False},
    ]
    views = [{"hwnd": 42, "title": "Portal · PhoneAI", "x": 40, "y": 40, "w": 700, "h": 500}]
    moved = []
    monkeypatch.setattr(ss, "monitor_rects", lambda: mons)
    monkeypatch.setattr(ss, "viewer_rects", lambda: views)
    monkeypatch.setattr(ss, "_move_hwnd", lambda hwnd, x, y, w, h: moved.append((hwnd, x, y, w, h)) or True)
    monkeypatch.setattr(
        ss,
        "set_share",
        lambda **k: {"ok": True, "mode": k.get("mode"), "target": k.get("target"), "monitor": 0, "label": k.get("label")},
    )
    r = ss.park_pocket_for_vision()
    assert r["ok"] is True
    assert r["displays"] == 2
    assert moved and moved[0][0] == 42
    assert moved[0][1] >= 1920
    assert str(r.get("target") or "").startswith("monitor:")


def test_viewer_titles_catch_portal_and_desk():
    from pocket.screen_share import is_viewer_title

    assert is_viewer_title("Portal · PhoneAI · 3.13.3")
    assert is_viewer_title("POCKET Desk")
    assert is_viewer_title("http://127.0.0.1:8787/desk")
    assert not is_viewer_title("Visual Studio Code")
    assert not is_viewer_title("Microsoft Copilot: Your AI companion")


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
    assert 'id="scL"' in html and 'id="scR"' in html
    assert "L click" in html
    assert 'id="focusBtn"' in html
    assert 'id="moveBtn"' in html
    assert 'id="desk2Btn"' in html
    assert "holdPad" in html
    assert "padMode" in html
    assert "maybeLayout" in html
    assert "lastFrameAt" in html
    assert "visibilitychange" in html
    assert "noteFrame" in html
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
    assert 'id="modeBadge"' in html
    assert 'data-act="minimize"' in html
    assert 'data-act="maximize"' in html
    assert 'data-act="close"' in html
    assert "gest='hold'" in html or 'gest="hold"' in html
    assert "setScreenMode" in html
    assert "drag-mode" in html
    assert 'id="typeform"' in html
    assert 'id="typeBtn"' in html
    assert "setTypePad" in html
    assert "keys.blur()" in html
    assert "send('tap', p.nx, p.ny)" in html
    assert "send('hover'" in html
    assert "4500" not in html


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
    assert "hold" in s["controls"]
    assert "minimize" in s["controls"]
    assert "close" in s["controls"]


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
    assert "minimize" in html and "close" in html
