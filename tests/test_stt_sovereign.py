"""Sovereign STT tests — local Whisper is the default; cloud is explicit opt-in.

Deterministic tests run without a model. The end-to-end transcription test
only runs when faster-whisper and a model are present (scripts/setup-sovereign-stt.sh).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pocket import stt_engine


def test_local_whisper_is_default_engine():
    e = stt_engine.engines()
    assert e["ok"] is True
    assert e["default"] == "local_whisper"
    first = e["engines"][0]
    assert first["id"] == "local_whisper"
    assert first["default"] is True
    assert "on-device" in first["label"] or "local" in first["label"].lower()


def test_webspeech_is_labeled_cloud_fallback():
    e = stt_engine.engines()
    ws = next(x for x in e["engines"] if x["id"] == "webspeech")
    assert "cloud" in ws["label"].lower()


def test_explicit_webspeech_opt_out_accepts_text_only():
    r = stt_engine.transcribe(text="hello pocket", engine="webspeech")
    assert r["ok"] is True
    assert r["engine"] == "webspeech"
    assert r["cloud"] is True
    assert r["own_stack"] is False


def test_webspeech_opt_out_rejects_empty_without_audio():
    r = stt_engine.transcribe(engine="webspeech")
    assert r["ok"] is False
    assert r["error"] == "empty_transcript"


def test_missing_audio_path_returns_clear_error():
    r = stt_engine.transcribe(audio_path="/nonexistent/utterance.webm")
    assert r["ok"] is False
    assert r["error"] == "audio_not_found"


def test_text_passthrough_still_works_for_hybrid_clients():
    r = stt_engine.transcribe(text="  turn on the lights  ", engine="hybrid")
    assert r["ok"] is True
    assert r["text"] == "turn on the lights"
    assert r["engine"] == "hybrid"


def test_env_opt_out_respected(monkeypatch):
    monkeypatch.setenv("POCKET_STT_ENGINE", "webspeech")
    assert stt_engine.default_engine() == "webspeech"
    r = stt_engine.transcribe(text="hi")
    assert r["engine"] == "webspeech"
    assert r["cloud"] is True


def test_model_name_env_override(monkeypatch):
    monkeypatch.setenv("POCKET_STT_MODEL", "tiny")
    assert stt_engine.model_name() == "tiny"


def test_missing_whisper_gives_setup_hint(monkeypatch):
    # Simulate a host without faster-whisper and without the CLI.
    monkeypatch.setattr(stt_engine, "faster_whisper_available", lambda: False)
    monkeypatch.setattr("shutil.which", lambda *a, **k: None)
    r = stt_engine.transcribe_audio_file(__file__, lang="en")  # any real file
    assert r["ok"] is False
    assert "setup-sovereign-stt" in r.get("hint", "")


fw = pytest.importorskip("faster_whisper", reason="faster-whisper not installed")


def _tiny_model_ready():
    try:
        from faster_whisper import WhisperModel

        WhisperModel("tiny", device="cpu", compute_type="int8")
        return True
    except Exception:
        return False

@pytest.mark.skipif(not _tiny_model_ready(), reason="tiny model not downloaded")
def test_end_to_end_local_transcription(tmp_path, monkeypatch):
    """Real faster-whisper transcription of a synthesized speech-like sample."""
    import wave

    import numpy as np

    # Honest synthetic sample: NOT real speech — a 440Hz tone gated like
    # speech bursts. Validates the full pipeline (load -> decode -> segments),
    # not word accuracy.
    sr = 16000
    t = np.arange(sr * 2) / sr
    gate = ((t % 0.5) < 0.3).astype(float)
    pcm = (np.sin(2 * np.pi * 440 * t) * gate * 12000).astype(np.int16)
    wav = tmp_path / "sample.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())

    monkeypatch.setenv("POCKET_STT_MODEL", "tiny")
    monkeypatch.setenv("POCKET_STT_DEVICE", "cpu")
    monkeypatch.setenv("POCKET_STT_COMPUTE_TYPE", "int8")
    stt_engine._MODEL_SINGLETON.clear()
    r = stt_engine.transcribe(audio_path=str(wav), lang="en")
    assert r["engine"] == "local_whisper"
    assert r["ok"] in (True, False)  # tone may yield empty text; pipeline must not crash
    assert "duration" in r or "error" in r


def _real_sample_wav():
    p = os.environ.get("POCKET_STT_TEST_WAV", "")
    return p if p and os.path.isfile(p) else None


@pytest.mark.skipif(not (_tiny_model_ready() and _real_sample_wav()),
                    reason="needs tiny model + POCKET_STT_TEST_WAV real speech sample")
def test_end_to_end_real_speech_transcription(monkeypatch):
    """Real spoken audio through the sovereign pipeline.

    Sample: POCKET_STT_TEST_WAV (e.g. OSR_us_000_0010_8k.wav, Harvard sentences,
    public test recording). Asserts real English words come back from the
    LOCAL engine — no browser, no cloud.
    """
    monkeypatch.setenv("POCKET_STT_MODEL", "tiny")
    monkeypatch.setenv("POCKET_STT_DEVICE", "cpu")
    monkeypatch.setenv("POCKET_STT_COMPUTE_TYPE", "int8")
    stt_engine._MODEL_SINGLETON.clear()
    r = stt_engine.transcribe(audio_path=_real_sample_wav(), lang="en")
    assert r["ok"] is True
    assert r["engine"] == "local_whisper"
    assert r["own_stack"] is True
    assert r.get("cloud", False) is False
    words = set(r["text"].lower().split())
    # Harvard sentences vocabulary; tiny model on 8kHz should recover several.
    assert len(words & {"the", "glue", "sheet", "dark", "blue", "rice", "bowls",
                        "lemon", "punch", "hogs", "corn", "hours", "work"}) >= 3
