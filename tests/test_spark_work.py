from pathlib import Path

from pocket.spark_work import run_tool, work


def test_write_and_read_local_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.spark_work._roots", lambda: [tmp_path])
    p = tmp_path / "hello.md"
    out = run_tool("write_file", {"path": str(p), "content": "from spark\n"}, cwd=str(tmp_path))
    assert '"wrote": true' in out.replace(" ", "") or '"wrote":true' in out.replace(" ", "")
    assert p.read_text(encoding="utf-8") == "from spark\n"
    rd = run_tool("read_file", {"path": str(p)}, cwd=str(tmp_path))
    assert "from spark" in rd


def test_path_outside_roots_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.spark_work._roots", lambda: [tmp_path])
    out = run_tool("write_file", {"path": r"C:\Windows\Temp\nope.txt", "content": "x"}, cwd=str(tmp_path))
    assert "not in allowed roots" in out


def test_work_uses_text_tool_protocol(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.spark_work._roots", lambda: [tmp_path])
    calls = {"n": 0}

    def fake_chat(prompt, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return {
                "ok": True,
                "reply": '```json\n{"tool":"write_file","path":"note.txt","content":"hi from spark"}\n```',
                "tool_calls": [],
            }
        return {"ok": True, "reply": "Wrote note.txt on disk.", "tool_calls": []}

    monkeypatch.setattr("pocket.spark_work.spark_chat", fake_chat)
    r = work("write note.txt", cwd=str(tmp_path))
    assert r["ok"] is True
    assert (tmp_path / "note.txt").read_text(encoding="utf-8") == "hi from spark"
    assert "note.txt" in (r.get("reply") or "")
