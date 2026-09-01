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


def test_vault_scan_clean_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_github.LOCAL", tmp_path)
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "ok.md").write_text("hello", encoding="utf-8")
    assert scan_vault().get("ok") is True
    (tmp_path / "notes" / "bad.md").write_text("BEGIN PRIVATE KEY", encoding="utf-8")
    assert scan_vault().get("ok") is False
