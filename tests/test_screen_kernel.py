from pocket.screen_kernel import PROTOCOL, SCHEMA, snapshot


def test_screen_kernel_snapshot():
    s = snapshot()
    assert s["ok"] is True
    assert s["schema"] == SCHEMA
    assert s["protocol"] == PROTOCOL
    assert PROTOCOL.startswith("SCREEN-KERNEL/")
    assert "see" in s["verbs"] and "type_into" in s["verbs"] and "click_name" in s["verbs"]
    assert "embody" in s["verbs"]
    assert any("screen/kernel" in x for x in s["http"])
    assert s.get("stream") == "pocket.stream.v1"


def test_screen_body_inhabit(tmp_path, monkeypatch):
    from pocket import screen_body as sb

    monkeypatch.setattr(sb, "ROOT", tmp_path / "screen_body.json")
    monkeypatch.setattr("pocket.screen_kernel.see", lambda **k: {"ok": True, "bytes": 4, "which": "desktop", "via": "test"})
    monkeypatch.setattr("pocket.screen_kernel.snapshot", lambda: {"ok": True, "protocol": "SCREEN-KERNEL/1.1"})
    r = sb.inhabit("coder", which="desktop")
    assert r["ok"] is True
    assert r["inhabited"] is True
    assert r["agent"] == "coder"
    occ = sb.occupant()
    assert occ["occupant"]["agent"] == "coder"
    left = sb.leave("coder")
    assert left["ok"] is True


def test_route_think_screen_embody():
    from pocket.agent_runtime import route_think

    t = route_think("embody the screen and see the desktop")
    assert t["engine"] == "screen"
    assert t["tool"] == "screen_embody"
