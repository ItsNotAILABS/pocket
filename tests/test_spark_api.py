from pocket.spark_api import chat, save, status


def test_save_and_status_no_network(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.spark_api.CFG", tmp_path / "spark.json")
    monkeypatch.setattr("pocket.spark_api.ROOT", tmp_path)
    monkeypatch.delenv("SPARK_API_KEY", raising=False)
    st = save(api_key="sk-spark-test", model="qwen3.8-27b")
    assert st["configured"] is True
    assert st["model"] == "qwen3.8-27b"
    assert st["key_prefix"].startswith("sk-spark-tes")
    assert "sk-spark-test" not in str(st)


def test_chat_requires_key(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.spark_api.CFG", tmp_path / "spark.json")
    monkeypatch.setattr("pocket.spark_api.ROOT", tmp_path)
    monkeypatch.delenv("SPARK_API_KEY", raising=False)
    r = chat("hi")
    assert r["ok"] is False
    assert "not configured" in (r.get("error") or "")
