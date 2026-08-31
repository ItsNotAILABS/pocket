"""Seat model CLIs are provisioned without extra user installs."""

from __future__ import annotations

from pocket.model_clis import MODEL_CLIS, ensure_seat, inventory, provision_seat_clis


def test_catalog_covers_all_models():
    ids = {t["id"] for t in MODEL_CLIS}
    assert {"grok", "codex", "claude", "gemini", "qwen", "spark", "opencode", "cursor", "aider", "copilot", "pocket-agent"} <= ids
    spark = next(t for t in MODEL_CLIS if t["id"] == "spark")
    assert spark["bin"] == "ollama"
    assert "glimmer" in spark["label"].lower()
    inv = inventory()
    assert inv["count"] == len(MODEL_CLIS)
    assert inv["ok"] is True


def test_signup_seat_gets_cli_shims(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    seat = provision_seat_clis("alicecli")
    assert seat.get("ok") is True
    bindir = tmp_path / "tenants" / "alicecli" / "bin"
    assert bindir.is_dir()
    readme = tmp_path / "tenants" / "alicecli" / "files" / "CLI.md"
    assert readme.is_file()
    text = readme.read_text(encoding="utf-8")
    assert "Grok" in text
    assert "Codex" in text
    bundled = ensure_seat("alicecli", install_host=False)
    assert bundled.get("ok") is True
    assert bundled["seat"]["user"] == "alicecli"
