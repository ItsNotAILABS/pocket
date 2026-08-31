from pocket.phoneai_portal import geom, map_touch, snapshot, virtual_screen


def test_portal_snapshot_has_both_modes():
    s = snapshot()
    assert s["ok"] is True
    assert "watch" in s["modes"] and "touch" in s["modes"]
    assert "desktop" in s["targets"]


def test_map_touch_corners():
    vs = virtual_screen()
    tl = map_touch(0, 0, target="desktop")
    br = map_touch(1, 1, target="desktop")
    assert tl["x"] == vs["x"]
    assert tl["y"] == vs["y"]
    assert br["x"] == vs["x"] + vs["w"]
    assert br["y"] == vs["y"] + vs["h"]
    g = geom("desktop")
    assert g["w"] > 0 and g["h"] > 0
