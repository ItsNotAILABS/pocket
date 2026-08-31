"""Public signup + Novae platform map."""

from __future__ import annotations

import os
from pathlib import Path

import pocket.users as users
from pocket.platform_coherence import coherent, find_feature, run_platform_skill


def test_public_signup_creates_member(tmp_path, monkeypatch):
    monkeypatch.setattr(users, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(users, "ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    monkeypatch.setenv("POCKET_PUBLIC_SIGNUP", "1")
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    res = users.register(
        "alice_public",
        "hunter22",
        "",
        display="Alice",
        accepted_terms=True,
        email="alice@example.com",
        channel="public",
    )
    assert res.get("ok") is True
    assert res.get("role") == "member"
    assert res.get("user") == "alice_public"
    rec = users.verify("alice_public", "hunter22")
    assert rec and rec["user"] == "alice_public"
    assert rec.get("is_owner") is False


def test_public_signup_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(users, "USERS_FILE", tmp_path / "users.json")
    monkeypatch.setattr(users, "ROOT", tmp_path)
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    monkeypatch.setenv("POCKET_PUBLIC_SIGNUP", "0")
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    res = users.register("bob", "hunter22", "", accepted_terms=True)
    assert res.get("ok") is False
    assert "invite" in (res.get("error") or "").lower()


def test_imagine_on_platform_map():
    c = coherent()
    ids = {s["id"] for s in c.get("surfaces") or []}
    assert "imagine" in ids
    assert "foundations" in ids


def test_novae_on_platform_map():
    c = coherent()
    ids = {s["id"] for s in c.get("surfaces") or []}
    assert "novae" in ids
    skill_ids = {s["id"] for s in c.get("skills") or []}
    assert "novae_activate" in skill_ids
    hit = find_feature("novae")
    assert hit.get("ok")
    listed = run_platform_skill("novae_list")
    assert listed.get("ok")
    assert listed.get("count", 0) >= 2
