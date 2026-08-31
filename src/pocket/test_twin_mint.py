from pocket.twin_mint import create_agent, mint, vault_get, vault_put


def test_mint_embed_clis_and_vault(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.platform_space.TENANTS_ROOT", tmp_path / "tenants")
    monkeypatch.setenv("POCKET_SKIP_CLI_INSTALL", "1")
    monkeypatch.setenv("POCKET_TWIN_SECRET", "test-secret")
    r = mint("alice")
    assert r["ok"] is True
    root = tmp_path / "tenants" / "alice"
    assert (root / "twin").is_dir()
    assert (root / "vault").is_dir()
    assert (root / "pocket_vault").is_dir()
    assert (root / "agents").is_dir()
    assert (root / "bin").is_dir()
    put = vault_put("alice", "secret.md", "hello twin", to_pocket=False)
    assert put["ok"] is True
    got = vault_get("alice", "secret.md")
    assert got["ok"] is True
    assert "hello twin" in got["text"]
    ag = create_agent("alice", {"id": "desk-buddy", "role": "talks to phoneai", "engine": "grok"})
    assert ag["ok"] is True
    assert (root / "agents" / "desk-buddy.json").is_file()
    assert ag["agent"]["talks_to"] == "phoneai"
