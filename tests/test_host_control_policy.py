from pocket.auth import path_is_public
from pocket.host_control import allow
from pocket.phoneai_github import scan_vault
from pocket.phoneai_os_ui import phoneai_portal_html
from pocket.shell_exec import run as sh_run


def test_new_control_paths_are_not_anonymous():
    remote = {"CF-Connecting-IP": "8.8.8.8"}
    addr = ("1.2.3.4", 443)
    for p in (
        "/v1/screen/touch",
        "/v1/screen/type",
        "/v1/vcomp/act",
        "/v1/vcomp/shell",
        "/v1/rah/run",
        "/v1/agents/invoke",
        "/v1/agent-mail/send",
        "/v1/webmcp/scan",
        "/v1/engines",
    ):
        assert path_is_public(p, headers=remote, client_address=addr) is False
    assert path_is_public("/v1/phoneai/tv/frame", headers=remote, client_address=addr) is False
    assert path_is_public("/phoneai/portal") is True
    assert path_is_public("/phoneai/tv") is True
    g = allow(headers=remote, client_address=addr, consequence="vcomp")
    assert g.get("ok") is False
    g = allow(headers=remote, client_address=addr, consequence="mail")
    assert g.get("ok") is False
    g = allow(headers=remote, client_address=addr, consequence="rah")
    assert g.get("ok") is False


def test_prefixes_do_not_open_host_control():
    assert path_is_public("/api/phoneai/harness") is False
    assert path_is_public("/v1/phoneai/shell") is False
    assert path_is_public("/v1/phoneai/harness") is False
    assert path_is_public("/v1/eyes/touch") is False
    assert path_is_public("/v1/runtime/ensure") is False
    assert path_is_public("/v1/runtime/install") is False
    assert path_is_public("/v1/twin/agent/run") is False
    assert path_is_public("/v1/twin/vault") is False
    assert path_is_public(
        "/v1/twin/vault",
        headers={"CF-Connecting-IP": "8.8.8.8"},
        client_address=("127.0.0.1", 443),
    ) is False
    assert path_is_public(
        "/v1/phoneai/shell",
        headers={"CF-Connecting-IP": "8.8.8.8"},
        client_address=("127.0.0.1", 443),
    ) is False
    assert path_is_public(
        "/v1/phoneai/shell",
        headers={},
        client_address=("192.168.1.40", 9),
    ) is True


def test_static_shells_and_login_stay_public():
    assert path_is_public("/health") is True
    assert path_is_public("/login") is True
    assert path_is_public("/phoneai") is True
    assert path_is_public("/phoneai/portal") is True
    assert path_is_public("/phoneai/pair") is True
    assert path_is_public("/phoneai/computer") is True
    assert path_is_public("/phoneai/app") is True
    assert path_is_public("/v1/auth/passkey/begin") is True
    assert path_is_public("/v1/auth/device/begin") is True
    assert path_is_public("/v1/auth/device/list") is False


def test_portal_frame_needs_lan_or_device():
    assert path_is_public("/v1/phoneai/portal/frame") is False
    assert path_is_public(
        "/v1/phoneai/portal/frame",
        headers={},
        client_address=("192.168.1.40", 443),
    ) is True
    assert path_is_public(
        "/v1/phoneai/portal/frame",
        headers={"CF-Connecting-IP": "8.8.8.8"},
        client_address=("127.0.0.1", 443),
    ) is False


def test_shell_ignores_destructive_override():
    r = sh_run("echo pocket-ok", allow_destructive=True)
    assert r.get("ok") is True
    blocked = sh_run("Remove-Item -Recurse C:\\Windows", allow_destructive=True)
    assert blocked.get("ok") is False
    assert blocked.get("blocked") is True


def test_anonymous_host_control_denied():
    g = allow(headers={"CF-Connecting-IP": "1.2.3.4"}, client_address=("1.2.3.4", 443), consequence="shell")
    assert g.get("ok") is False
    vis = allow(headers={"CF-Connecting-IP": "1.2.3.4"}, client_address=("1.2.3.4", 443), consequence="portal")
    assert vis.get("ok") is False


def test_portal_html_has_face_id():
    html = phoneai_portal_html()
    assert "Face ID" in html
    assert "/v1/auth/passkey" in html
    assert 'id="faceBtn"' in html


def test_exact_origin_rejects_sibling_and_trycloudflare():
    from pocket.origin_policy import origin_allowed, rp_id_for_host
    from pocket.passkey import origin_allowed as pk_origin, rp_id_from_host
    from pocket.phoneai_portal import origin_ok

    host = "pocket.medinatechlabs.net"
    assert origin_allowed("https://pocket.medinatechlabs.net", host) is True
    assert origin_allowed("https://evil.medinatechlabs.net", host) is False
    assert origin_allowed("https://random.trycloudflare.com", host) is False
    assert pk_origin("https://evil.medinatechlabs.net", host) is False
    assert rp_id_from_host("evil.medinatechlabs.net") == "evil.medinatechlabs.net"
    assert rp_id_for_host("pocket.medinatechlabs.net") == "pocket.medinatechlabs.net"
    assert origin_ok(
        {"Origin": "https://evil.medinatechlabs.net", "Host": host, "CF-Connecting-IP": "8.8.8.8"},
        ("8.8.8.8", 443),
    ) is False
    assert origin_ok(
        {"Origin": "https://pocket.medinatechlabs.net", "Host": host},
        ("8.8.8.8", 443),
    ) is True


def test_device_token_is_not_owner_and_cannot_shell(monkeypatch):
    from pocket.host_control import allow
    from pocket.users import issue_token, user_from_token

    monkeypatch.setattr("pocket.device_pair.device_live", lambda p: True)
    tok = issue_token("device:dev_test", role="portal_device", is_owner=False, device_id="dev_test", capability="portal")
    rec = user_from_token(tok)
    assert rec is not None
    assert rec["is_owner"] is False
    assert rec["role"] == "portal_device"
    headers = {"Authorization": "Bearer " + tok, "CF-Connecting-IP": "8.8.8.8"}
    addr = ("8.8.8.8", 443)
    vis = allow(headers=headers, client_address=addr, consequence="portal")
    assert vis.get("ok") is True
    sh = allow(headers=headers, client_address=addr, consequence="shell")
    assert sh.get("ok") is False


def test_empty_origin_ok_with_portal_cookie():
    from pocket.phoneai_portal import mint_portal_token, origin_ok

    tok = mint_portal_token("pocket")
    assert origin_ok({"Cookie": "pocket_portal=" + tok, "CF-Connecting-IP": "8.8.8.8"}, ("8.8.8.8", 443)) is True
    assert origin_ok({"CF-Connecting-IP": "8.8.8.8"}, ("8.8.8.8", 443)) is False


def test_device_pair_roundtrip(tmp_path, monkeypatch):
    from pocket import device_pair as dp

    monkeypatch.setattr(dp, "ROOT", tmp_path)
    monkeypatch.setattr(dp, "FILE", tmp_path / "code.json")
    monkeypatch.setattr(dp, "DEVICES", tmp_path / "devices.json")
    m = dp.mint(client_ip="127.0.0.1")
    assert m["ok"] is True
    assert len(m["code"]) == 6
    assert m.get("need") == "webauthn"
    bad = dp.mint(client_ip="8.8.8.8")
    assert bad["ok"] is False
    r = dp.redeem(m["code"])
    assert r["ok"] is False
    assert r.get("need") == "webauthn"
    assert r.get("user") != "pocket"


def test_anonymous_legacy_portal_token_is_dead():
    from pocket.phoneai_portal import check_portal_token, mint_portal_token

    assert check_portal_token("1710000000.deadbeef") is False
    tok = mint_portal_token("alice")
    assert check_portal_token(tok) is True


def test_work_grant_required_for_rah_execute():
    from pocket.rah import maybe_auto_rah
    from pocket.work_grant import issue, valid

    plan = maybe_auto_rah("split this into parallel research and code leaves", execute=True)
    assert plan is None or plan.get("execute") is False or plan.get("skipped")
    g = issue(principal="alice", capability="rah", tools=["rah", "think"])
    assert valid(g["id"], capability="rah").get("ok") is True


def test_rah_contracts_are_first_class():
    from pocket.contracts import catalog
    from pocket.work_grant import contracts

    c = contracts()
    assert c["ok"] is True
    assert "rah" in c["roles"]
    assert "node" in c["roles"]
    objs = c.get("objects") or {}
    assert "pocket.work_grant.v1" in objs or "pocket.work_grant.v1" in (objs if isinstance(objs, list) else [])
    assert "rah_run" in c["agent_tools"]
    cat = catalog()
    assert "pocket.node.view.v1" in cat["objects"]
    assert "tv" in cat["nodes"]


def test_portal_html_glass_fill():
    from pocket.phoneai_os_ui import phoneai_portal_html

    html = phoneai_portal_html()
    assert 'data-f="contain"' in html
    assert "fitMode='contain'" in html or 'fitMode="contain"' in html


def test_tv_html_is_wifi_node():
    from pocket.home_mesh import list_view_nodes, register_view_node
    from pocket.home_ui import tv_html

    html = tv_html()
    assert "object-fit:contain" in html
    assert "max-width:100%" in html or "object-fit:contain" in html
    assert "/v1/nodes/view" in html
    assert "target=desktop" in html or "target:'desktop'" in html or "target:tgt" in html or "TV → phone" in html
    r = register_view_node(kind="tv", label="test-tv", ip="192.168.1.50")
    assert r["ok"] is True
    assert r["node"]["kind"] == "tv"
    assert list_view_nodes()["count"] >= 1


def test_auro_adapter_does_not_crash():
    from pocket.auro14b_bridge import auro_root
    from pocket.auro_rah_adapter import ADAPTER, run_auro_rah

    r = run_auro_rah("say ok", max_parallel=1, depth=0, grant_id="wg-test", tenant="t")
    assert r.get("adapter") == ADAPTER
    assert "via" in r
    assert r.get("fanout") == "1:1"
    assert isinstance(r.get("receipt"), dict)
    assert r["receipt"].get("grant_id") == "wg-test"
    if auro_root():
        assert r.get("via") == "auro_native_llm.rah"
        assert r.get("native") is True
        assert r.get("engine") == "auro-rah"
    else:
        assert r.get("via") == "pocket.internal_models.auro"
        assert r.get("native") is False
        assert r.get("engine") != "auro-rah"


def test_vault_scan_clean_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_github.LOCAL", tmp_path)
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "ok.md").write_text("hello", encoding="utf-8")
    assert scan_vault().get("ok") is True
    (tmp_path / "notes" / "bad.md").write_text("BEGIN PRIVATE KEY", encoding="utf-8")
    assert scan_vault().get("ok") is False
