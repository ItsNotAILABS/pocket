"""Edge/web login: /v1/auth/me must see Bearer tokens, not only X-Pocket-Token."""

from pocket.auth import current_user, path_is_public
from pocket.users import issue_token, register


def test_current_user_accepts_bearer(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setattr("pocket.users.USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr("pocket.users.ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    rec = register("edgeuser", "hunter22xx", "", accepted_terms=True)
    assert rec.get("ok") is True
    tok = issue_token("edgeuser")
    u = current_user({"Authorization": f"Bearer {tok}"})
    assert u is not None
    assert u.get("user") == "edgeuser"


def test_current_user_accepts_cookie(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setattr("pocket.users.USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr("pocket.users.ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    rec = register("cookieuser", "hunter22xx", "", accepted_terms=True)
    assert rec.get("ok") is True
    tok = issue_token("cookieuser")
    u = current_user({"Cookie": f"pocket_session={tok}"})
    assert u is not None
    assert u.get("user") == "cookieuser"


def test_phoneai_sessions_are_not_anonymous():
    assert path_is_public("/v1/phoneai/sessions") is False
    assert path_is_public("/v1/phoneai/talk") is False
    assert path_is_public("/v1/auth/desktop/enter") is True


def test_host_control_not_public():
    assert path_is_public("/v1/phoneai/shell") is False
    assert path_is_public("/api/phoneai/shell") is False
    assert path_is_public("/v1/eyes") is False
    assert path_is_public("/v1/eyes/touch") is False
    assert path_is_public("/v1/runtime/install") is False
    assert path_is_public("/v1/webmcp/use") is False
    assert path_is_public("/phoneai/portal") is False
    assert path_is_public("/phoneai") is True
    assert path_is_public("/health") is True
