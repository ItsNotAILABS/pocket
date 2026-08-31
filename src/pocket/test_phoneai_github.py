from pocket.phoneai_github import stage_file, snapshot


def test_stage_file_writes_vault(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.phoneai_github.LOCAL", tmp_path / "gh")
    monkeypatch.setattr("pocket.phoneai_github.STATE", tmp_path / "github.json")
    fp = stage_file("notes/hello.md", "from phone")
    assert fp.is_file()
    assert "from phone" in fp.read_text(encoding="utf-8")
    snap = snapshot()
    assert snap["repo"].endswith("phoneai-desk")
