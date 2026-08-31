"""Spark uses Muse Glimmer open weights."""

from pocket.phone_agents import DISPATCH, glimmer_ask, spark_ask
from pocket.model_clis import MODEL_CLIS


def test_spark_uses_glimmer_open_weights():
    assert "open weights" in (spark_ask.__doc__ or "").lower()
    assert "glimmer" in (glimmer_ask.__doc__ or "").lower()
    spark = next(t for t in MODEL_CLIS if t["id"] == "spark")
    assert spark["bin"] == "ollama"
    assert "glimmer" in spark["label"].lower()
    assert "open weights" in (spark.get("note") or "").lower()


def test_strong_engines_registered():
    for e in ("spark", "glimmer", "claude", "gemini", "opencode", "cursor", "aider", "copilot", "spectral", "physics", "agi"):
        assert e in DISPATCH
