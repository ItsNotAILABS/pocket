"""OAuth identity seats + ecosystem catalog."""

from __future__ import annotations

import pocket.users as users
from pocket.ecosystem import catalog
from pocket.oauth_login import PROVIDERS, list_providers, redeem_login_code


def test_upsert_github_creates_member(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setattr(users, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(users, "ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    first = users.upsert_from_oauth(
        "github",
        "123",
        login="alice-dev",
        display="Alice",
        email="alice@example.com",
    )
    assert first.get("ok") is True
    assert first["user"] == "alice-dev"
    assert first.get("is_owner") is False
    again = users.upsert_from_oauth("github", "123", login="alice-dev")
    assert again["user"] == "alice-dev"


def test_github_owner_links_admin(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setattr(users, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(users, "ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    users.register("memberx", "hunter22", "", accepted_terms=True)
    rec = users.upsert_from_oauth(
        "github",
        "999",
        login="FreddyCreates",
        prefer_owner=True,
    )
    assert rec.get("ok")
    assert rec.get("is_owner") is True


def test_providers_include_github_google_microsoft_x():
    ids = set(PROVIDERS)
    assert {"github", "google", "microsoft", "x"} <= ids
    listed = list_providers(loopback=False)
    names = {p["id"] for p in listed["providers"]}
    assert names == ids
    assert listed["password"] is True
    assert listed["one_time_code"] is True


def test_bad_code_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.oauth_login.ROOT", tmp_path)
    bad = redeem_login_code("000000")
    assert bad.get("ok") is False


def test_ecosystem_includes_phoneai():
    c = catalog()
    assert c["ok"] is True
    ids = [r["id"] for r in c["family"]]
    assert "phoneai" in ids
    assert "pocket-phone-agent" in ids
    assert all(r.get("canonical") for r in c["family"])
    sibs = {s["name"] for s in c["siblings"]}
    assert "PhoneAI" not in sibs
    assert "ResearchersHub" in sibs
    phone = next(r for r in c["family"] if r["id"] == "phoneai")
    assert phone.get("on_disk") is True
