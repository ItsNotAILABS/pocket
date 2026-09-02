from pocket.phoneai_portal import geom, map_touch, primary_screen, snapshot


def test_portal_snapshot_has_both_modes():
    s = snapshot()
    assert s["ok"] is True
    assert s.get("first_class") is True
    assert s.get("grade") == "production"
    assert s.get("separate_from") == "antigravity"
    assert "watch" in s["modes"] and "touch" in s["modes"]
    assert "desktop" in s["targets"]


def test_map_touch_corners():
    ps = primary_screen()
    tl = map_touch(0, 0, target="desktop")
    br = map_touch(1, 1, target="desktop")
    assert tl["x"] == ps["x"]
    assert tl["y"] == ps["y"]
    assert br["x"] == ps["x"] + ps["w"]
    assert br["y"] == ps["y"] + ps["h"]
    g = geom("desktop")
    assert g["w"] == ps["w"] and g["h"] == ps["h"]
    # A window tab hwnd must not remap desktop taps into that window.
    shifted = map_touch(0, 0, target="desktop", hwnd=999999)
    assert shifted["x"] == ps["x"] and shifted["y"] == ps["y"]
    assert shifted["hwnd"] == 999999
