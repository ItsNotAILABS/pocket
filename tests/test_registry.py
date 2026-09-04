from pocket.auth import path_is_public
from pocket.registry import KERNEL_APPS, snapshot, write_snapshot


def test_full_registry_has_all_lanes():
    s = snapshot(write=True)
    assert s["ok"] is True
    assert s["schema"] == "pocket.full_registry.v1"
    c = s["counts"]
    assert c["phoneai_apps"] == len(KERNEL_APPS)
    assert c["mcp_apps"] >= 3
    assert c["how_tos"] >= 10
    assert c["papers"] >= 5
    assert c["whitepapers"] >= 3
    assert c["entries"] >= 40
    kinds = {e["kind"] for e in s["entries"]}
    for k in ("phoneai-app", "mcp-app", "system", "how-to", "paper", "whitepaper", "technology"):
        assert k in kinds
    ids = {a["id"] for a in s["phoneai_apps"]}
    assert "mcp-apps" in ids
    assert "registry" in ids
    mcp_ids = {a["id"] for a in s["mcp_apps"]}
    assert "pocket" in mcp_ids
    dest = write_snapshot(s)
    assert dest.is_file()
    assert dest.name == "POCKET_FULL_REGISTRY.json"


def test_registry_json_is_public():
    remote = {"CF-Connecting-IP": "8.8.8.8"}
    addr = ("1.2.3.4", 443)
    assert path_is_public("/v1/registry", headers=remote, client_address=addr) is True
    assert path_is_public("/registry", headers=remote, client_address=addr) is True
    assert path_is_public("/phoneai/registry", headers=remote, client_address=addr) is False
    assert path_is_public("/phoneai/registry", headers={}, client_address=("192.168.1.40", 9)) is True
