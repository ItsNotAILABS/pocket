"""POCKET first-party STT bridge — own speech stack, not a vendor black box.

Backends (in order of preference when available):
  · pocket_host — accept client hybrid transcript + energy (always)
  · whisper_cli — local `whisper` / faster-whisper if installed
  · passthrough — trust client final text from PocketVoice STT

Audio uploads optional; browser hybrid STT remains primary UX.
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


def engines() -> Dict[str, Any]:
    whisper = bool(shutil.which("whisper") or shutil.which("faster-whisper"))
    return {
        "ok": True,
        "schema": "pocket.stt.v1",
        "own_stack": True,
        "engines": [
            {
                "id": "hybrid",
                "label": "Hybrid (energy VAD + Web Speech)",
                "available": True,
                "default": True,
            },
            {
                "id": "pocket",
                "label": "Pocket energy + optional host ASR",
                "available": True,
            },
            {
                "id": "webspeech",
                "label": "Browser SpeechRecognition",
                "available": True,
            },
            {
                "id": "whisper_cli",
                "label": "Local Whisper CLI",
                "available": whisper,
            },
        ],
        "host": "POST /v1/voice/stt",
        "voice_api": "http://127.0.0.1:8790/v1/stt/engines",
    }


def transcribe(
    *,
    text: str = "",
    lang: str = "en",
    engine: str = "hybrid",
    energy: Optional[float] = None,
    speech_active: Optional[bool] = None,
    audio_path: str = "",
    session_id: str = "",
) -> Dict[str, Any]:
    """Transcribe or accept client transcript on the sovereign stack."""
    t0 = time.time()
    text = (text or "").strip()
    engine = (engine or "hybrid").lower()
    used = engine

    if audio_path and Path(audio_path).is_file() and not text:
        w = _whisper_file(audio_path, lang=lang)
        if w.get("ok") and w.get("text"):
            text = str(w["text"]).strip()
            used = "whisper_cli"
        else:
            return {
                "ok": False,
                "error": w.get("error") or "asr_failed",
                "hint": "Install whisper CLI or send hybrid text from browser STT",
                "engines": engines(),
            }

    if not text:
        return {
            "ok": False,
            "error": "empty_transcript",
            "hint": "Client hybrid STT should send text; or upload audio with whisper installed",
            "schema": "pocket.stt.v1",
            "engine": used,
        }

    return {
        "ok": True,
        "schema": "pocket.stt.v1",
        "own_stack": True,
        "engine": used,
        "text": text,
        "lang": lang,
        "energy": energy,
        "speech_active": speech_active,
        "session_id": session_id or None,
        "ms": int((time.time() - t0) * 1000),
        "product": "pocket",
    }


def _whisper_file(path: str, *, lang: str = "en") -> Dict[str, Any]:
    bin_w = shutil.which("whisper") or shutil.which("faster-whisper")
    if not bin_w:
        return {"ok": False, "error": "whisper_not_installed"}
    try:
        out_dir = ROOT / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        # openai-whisper CLI style
        cmd = [
            bin_w,
            path,
            "--model",
            os.environ.get("POCKET_WHISPER_MODEL") or "base",
            "--language",
            lang or "en",
            "--output_format",
            "txt",
            "--output_dir",
            str(out_dir),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            return {"ok": False, "error": (r.stderr or r.stdout or "whisper_failed")[:300]}
        # Find matching txt
        stem = Path(path).stem
        cand = list(out_dir.glob(f"{stem}*.txt")) or list(out_dir.glob("*.txt"))
        if not cand:
            # sometimes text is only on stdout
            if r.stdout and r.stdout.strip():
                return {"ok": True, "text": r.stdout.strip()[:4000]}
            return {"ok": False, "error": "no_transcript_file"}
        text = max(cand, key=lambda p: p.stat().st_mtime).read_text(encoding="utf-8", errors="replace")
        return {"ok": True, "text": text.strip()[:4000]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
