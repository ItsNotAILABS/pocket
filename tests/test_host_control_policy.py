from pocket.auth import path_is_public
from pocket.host_control import allow
from pocket.phoneai_github import scan_vault
from pocket.phoneai_os_ui import phoneai_portal_html
from pocket.shell_exec import run as sh_run


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
    assert path_is_public("/phoneai/app") is True
    assert path_is_public("/v1/auth/passkey/begin") is True


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
    from pocket.work_grant import contracts

    c = contracts()
    assert c["ok"] is True
    assert "rah" in c["roles"]
    assert "pocket.work_grant.v1" in c["objects"]
    assert "rah_run" in c["agent_tools"]


def test_portal_html_glass_fill():
    from pocket.phoneai_os_ui import phoneai_portal_html

    html = phoneai_portal_html()
    assert 'data-f="fill"' in html
    assert "fitMode='fill'" in html or 'fitMode="fill"' in html


def test_tv_html_is_fullscreen():
    from pocket.home_ui import tv_html

    html = tv_html()
    assert "object-fit:fill" in html
    assert "/v1/phoneai/home" in html
    assert "WebSocket" in html


def test_auro_adapter_does_not_crash():
    from pocket.auro_rah_adapter import ADAPTER, run_auro_rah

    r = run_auro_rah("say ok", max_parallel=2, depth=1, grant_id="wg-test", tenant="t")
    assert r.get("adapter") == ADAPTER
    assert "via" in r


def test_vault_scan_clean_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_github.LOCAL", tmp_path)
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "ok.md").write_text("hello", encoding="utf-8")
    assert scan_vault().get("ok") is True
    (tmp_path / "notes" / "bad.md").write_text("BEGIN PRIVATE KEY", encoding="utf-8")
    assert scan_vault().get("ok") is False
