from pocket.contracts import catalog
from pocket.protocols.platform_protocols import get_protocol, list_protocols, manifest
from pocket.protocols.screen_family import FAMILY, status


def test_screen_family_status():
    s = status()
    assert s["ok"] is True
    assert s["schema"] == FAMILY
    slugs = {p["slug"] for p in s["protocols"]}
    assert {
        "screen-kernel",
        "stream",
        "screen-body",
        "device-pair",
        "origin",
        "runtime",
        "agent-arch",
        "screen-matrix",
    } <= slugs


def test_major_catalog_includes_screen_family():
    slugs = {p["slug"] for p in list_protocols()}
    assert "screen-family" in slugs
    assert "screen-kernel" in slugs
    assert "device-pair" in slugs
    assert "origin" in slugs
    m = manifest()
    assert m["ok"] is True
    p = get_protocol("stream")
    assert p is not None
    assert p["schema"] == "pocket.stream.v1" if "schema" in p else p["slug"] == "stream"


def test_contracts_name_stream_and_body():
    c = catalog()
    objs = c["objects"]
    assert "pocket.stream.v1" in objs
    assert "pocket.screen.body.v1" in objs
    assert "pocket.device.pair.v1" in objs
    assert "pocket.origin.v1" in objs
    assert "screen_embody" in c["agent_tools"]
