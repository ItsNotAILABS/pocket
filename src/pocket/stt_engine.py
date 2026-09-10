"""POCKET sovereign STT — local-first speech stack. No cloud by default.

Engine order (default first):
  · local_whisper — faster-whisper ON THIS MACHINE (DEFAULT; private, on-device,
    no audio leaves the host). Lazy-loads the model on first use.
  · hybrid        — accept client transcript + energy (browser-assisted UX).
  · webspeech     — browser SpeechRecognition (CLOUD fallback — audio is sent to
    the browser vendor's speech service, e.g. Google). Explicit opt-in only.
  · whisper_cli   — legacy local `whisper`/`faster-whisper` CLI if installed.

Env:
  POCKET_STT_MODEL         tiny|base|small|medium|large-v3 (default: base)
  POCKET_STT_ENGINE        force engine: local_whisper|hybrid|webspeech|whisper_cli
                           (default: local_whisper; set to webspeech to opt OUT
                           of local ASR and use the browser cloud fallback)
  POCKET_STT_DEVICE        auto|cpu|cuda (default: auto)
  POCKET_STT_COMPUTE_TYPE  int8|float16|float32 (default: int8)

First-time setup:  scripts/setup-sovereign-stt.sh
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path.home() / ".pocket" / "stt"
ROOT.mkdir(parents=True, exist_ok=True)
MODEL_CACHE = ROOT / "models"
MODEL_CACHE.mkdir(parents=True, exist_ok=True)

SETUP_HINT = (
    "Local Whisper is not ready. Run scripts/setup-sovereign-stt.sh "
    "(pip installs faster-whisper and downloads POCKET_STT_MODEL) "
    "or set POCKET_STT_ENGINE=webspeech to fall back to browser cloud STT."
)

_MODEL_SINGLETON: Dict[str, Any] = {}


def _env(name: str, default: str = "") -> str:
    return str(os.environ.get(name) or default).strip()


def model_name() -> str:
    return _env("POCKET_STT_MODEL", "base") or "base"


def device() -> str:
    return _env("POCKET_STT_DEVICE", "auto") or "auto"


def compute_type() -> str:
    return _env("POCKET_STT_COMPUTE_TYPE", "int8") or "int8"


def default_engine() -> str:
    return (_env("POCKET_STT_ENGINE", "local_whisper") or "local_whisper").lower()


def faster_whisper_available() -> bool:
    try:
        import faster_whisper  # noqa: F401

        return True
    except Exception:
        return False


def _get_model():
    """Lazy-load (and download on first use) the faster-whisper model."""
    key = f"{model_name()}|{device()}|{compute_type()}"
    if key in _MODEL_SINGLETON:
        return _MODEL_SINGLETON[key]
    if not faster_whisper_available():
        raise RuntimeError(f"faster-whisper not installed. {SETUP_HINT}")
    from faster_whisper import WhisperModel

    try:
        m = WhisperModel(
            model_name(),
            device=device(),
            compute_type=compute_type(),
            download_root=str(MODEL_CACHE),
        )
    except Exception as e:
        raise RuntimeError(f"Whisper model '{model_name()}' failed to load: {e}. {SETUP_HINT}")
    _MODEL_SINGLETON[key] = m
    return m


def transcribe_audio_file(path: str, *, lang: str = "en") -> Dict[str, Any]:
    """Transcribe a local audio file with faster-whisper (on-device)."""
    t0 = time.time()
    p = Path(path)
    if not p.is_file():
        return {"ok": False, "error": "audio_not_found", "path": str(path)}
    try:
        model = _get_model()
    except RuntimeError as e:
        # Legacy CLI fallback is still local — prefer it over failing.
        cli = _whisper_cli_file(str(p), lang=lang)
        if cli.get("ok"):
            cli["engine"] = "whisper_cli"
            cli["note"] = "faster-whisper lib missing; used local CLI fallback"
            return cli
        return {"ok": False, "error": "whisper_not_installed", "hint": SETUP_HINT}
    try:
        segments, info = model.transcribe(str(p), language=(lang or "en"), beam_size=5)
        texts = []
        for s in segments:
            if s.text:
                texts.append(s.text.strip())
        text = " ".join(texts).strip()
        return {
            "ok": True,
            "schema": "pocket.stt.v1",
            "own_stack": True,
            "engine": "local_whisper",
            "model": model_name(),
            "text": text[:8000],
            "language": getattr(info, "language", lang or "en"),
            "duration": round(getattr(info, "duration", 0.0), 2),
            "ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        return {"ok": False, "error": f"transcribe_failed: {e}"[:300]}


def engines() -> Dict[str, Any]:
    local = faster_whisper_available()
    return {
        "ok": True,
        "schema": "pocket.stt.v1",
        "own_stack": True,
        "default": "local_whisper",
        "model": model_name(),
        "device": device(),
        "engines": [
            {
                "id": "local_whisper",
                "label": "Local Whisper (on-device, private — no audio leaves this host)",
                "available": local,
                "default": True,
            },
            {
                "id": "hybrid",
                "label": "Hybrid (client energy VAD + transcript)",
                "available": True,
            },
            {
                "id": "webspeech",
                "label": "Browser SpeechRecognition (CLOUD fallback — audio goes to the browser vendor, e.g. Google)",
                "available": True,
            },
            {
                "id": "whisper_cli",
                "label": "Local Whisper CLI (legacy)",
                "available": bool(shutil.which("whisper") or shutil.which("faster-whisper")),
            },
        ],
        "host": "POST /v1/voice/stt",
        "setup": "scripts/setup-sovereign-stt.sh",
    }


def transcribe(
    *,
    text: str = "",
    lang: str = "en",
    engine: str = "",
    energy: Optional[float] = None,
    speech_active: Optional[bool] = None,
    audio_path: str = "",
    audio_bytes: Optional[bytes] = None,
    audio_suffix: str = ".webm",
    session_id: str = "",
) -> Dict[str, Any]:
    """Transcribe on the sovereign stack. Audio always stays on this host."""
    t0 = time.time()
    text = (text or "").strip()
    eng = (engine or default_engine()).lower()

    if eng == "webspeech":
        # Explicit cloud opt-out: browser does the recognition; we only accept text.
        if not text:
            return {
                "ok": False,
                "error": "empty_transcript",
                "hint": "webspeech engine transcribes in the browser (cloud); send text",
                "schema": "pocket.stt.v1",
                "engine": "webspeech",
                "cloud": True,
            }
        return _text_result(text, lang, eng, energy, speech_active, session_id, t0, cloud=True)

    # Audio input -> local Whisper, no exceptions (never silently route to cloud).
    tmp_path = ""
    if audio_bytes:
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=audio_suffix, dir=str(ROOT))
            with os.fdopen(fd, "wb") as f:
                f.write(audio_bytes)
            audio_path = tmp_path
        except Exception as e:
            return {"ok": False, "error": f"audio_write_failed: {e}"[:200]}
    try:
        if audio_path and not Path(audio_path).is_file():
            return {
                "ok": False,
                "error": "audio_not_found",
                "path": audio_path,
                "schema": "pocket.stt.v1",
                "engine": eng,
            }
        if audio_path and not text:
            w = transcribe_audio_file(audio_path, lang=lang or "en")
            if w.get("ok") and w.get("text"):
                w.update(
                    {
                        "energy": energy,
                        "speech_active": speech_active,
                        "session_id": session_id or None,
                        "product": "pocket",
                    }
                )
                return w
            w["hint"] = SETUP_HINT
            return w
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

    if not text:
        err = {
            "ok": False,
            "error": "empty_transcript",
            "schema": "pocket.stt.v1",
            "engine": eng,
        }
        if eng == "local_whisper":
            err["hint"] = "Upload audio for local Whisper, or " + SETUP_HINT
        else:
            err["hint"] = "Client hybrid STT should send text"
        return err

    return _text_result(text, lang, eng, energy, speech_active, session_id, t0)


def _text_result(text, lang, eng, energy, speech_active, session_id, t0, cloud=False):
    return {
        "ok": True,
        "schema": "pocket.stt.v1",
        "own_stack": not cloud,
        "cloud": cloud,
        "engine": eng,
        "text": text,
        "lang": lang,
        "energy": energy,
        "speech_active": speech_active,
        "session_id": session_id or None,
        "ms": int((time.time() - t0) * 1000),
        "product": "pocket",
    }


def _whisper_cli_file(path: str, *, lang: str = "en") -> Dict[str, Any]:
    """Legacy local CLI fallback (still on-device, never cloud)."""
    bin_w = shutil.which("whisper") or shutil.which("faster-whisper")
    if not bin_w:
        return {"ok": False, "error": "whisper_not_installed"}
    try:
        out_dir = ROOT / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            bin_w,
            path,
            "--model",
            model_name(),
            "--language",
            lang or "en",
            "--output_format",
            "txt",
            "--output_dir",
            str(out_dir),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            return {"ok": False, "error": (r.stderr or r.stdout or "whisper_failed")[:300]}
        stem = Path(path).stem
        cand = list(out_dir.glob(f"{stem}*.txt")) or list(out_dir.glob("*.txt"))
        if not cand:
            if r.stdout and r.stdout.strip():
                return {"ok": True, "text": r.stdout.strip()[:8000]}
            return {"ok": False, "error": "no_transcript_file"}
        text = max(cand, key=lambda p: p.stat().st_mtime).read_text(encoding="utf-8", errors="replace")
        return {"ok": True, "text": text.strip()[:8000]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def ensure_model() -> Dict[str, Any]:
    """Download (if needed) and load the configured model. Used by setup."""
    try:
        _get_model()
        return {"ok": True, "model": model_name(), "cache": str(MODEL_CACHE)}
    except RuntimeError as e:
        return {"ok": False, "error": str(e)[:300], "hint": SETUP_HINT}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "ensure-model":
        print(json.dumps(ensure_model(), indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == "transcribe":
        print(json.dumps(transcribe_audio_file(sys.argv[2], lang=sys.argv[3] if len(sys.argv) > 3 else "en"), indent=2))
    else:
        print(json.dumps(engines(), indent=2))
