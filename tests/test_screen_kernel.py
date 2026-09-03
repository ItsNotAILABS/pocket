from pocket.screen_kernel import PROTOCOL, SCHEMA, snapshot


def test_screen_kernel_snapshot():
    s = snapshot()
    assert s["ok"] is True
    assert s["schema"] == SCHEMA
    assert s["protocol"] == PROTOCOL
    assert "see" in s["verbs"] and "type_into" in s["verbs"] and "click_name" in s["verbs"]
    assert any("screen/kernel" in x for x in s["http"])
