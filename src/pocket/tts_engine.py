"""TTS for Aria — free Edge neural voices when edge-tts is installed; else browser.

edge-tts uses Microsoft free online voices (no API key).
  pip install edge-tts

Also writes cache under ~/.pocket/tts/
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

TTS_DIR = Path.home() / ".pocket" / "tts"
TTS_DIR.mkdir(parents=True, exist_ok=True)

# Natural female English voice (free Edge catalog)
DEFAULT_VOICE = os.environ.get("POCKET_TTS_VOICE") or "en-US-JennyNeural"


def edge_tts_available() -> bool:
    try:
        import edge_tts  # noqa: F401

        return True
    except Exception:
        return bool(shutil.which("edge-tts"))


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "edge_tts": edge_tts_available(),
        "browser_fallback": True,
        "voice": DEFAULT_VOICE,
        "cache": str(TTS_DIR),
        "hint": "pip install edge-tts  # free Microsoft neural voices, no API key",
    }


def _cache_path(text: str, voice: str) -> Path:
    h = hashlib.sha256(f"{voice}|{text}".encode("utf-8")).hexdigest()[:24]
    return TTS_DIR / f"{h}.mp3"


async def _synthesize_async(text: str, voice: str, out: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(out))


def synthesize(
    text: str,
    *,
    voice: str = "",
    max_chars: int = 500,
) -> Dict[str, Any]:
    """Return {ok, path, url_path, mime, engine} or error."""
    t = (text or "").strip()
    if not t:
        return {"ok": False, "error": "empty text"}
    t = t[:max_chars]
    voice = (voice or DEFAULT_VOICE).strip()
    out = _cache_path(t, voice)
    if out.is_file() and out.stat().st_size > 100:
        return {
            "ok": True,
            "path": str(out),
            "url_path": f"/v1/voice/tts/file?name={out.name}",
            "mime": "audio/mpeg",
            "engine": "edge-tts-cache",
            "bytes": out.stat().st_size,
            "voice": voice,
        }

    if not edge_tts_available():
        return {
            "ok": False,
            "error": "edge_tts_not_installed",
            "fallback": "browser_speech_synthesis",
            "hint": "pip install edge-tts",
        }

    t0 = time.time()
    try:
        asyncio.run(_synthesize_async(t, voice, out))
    except RuntimeError:
        # nested loop
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_synthesize_async(t, voice, out))
            loop.close()
        except Exception as e:
            return {"ok": False, "error": str(e)[:200], "fallback": "browser_speech_synthesis"}
    except Exception as e:
        # CLI fallback
        if shutil.which("edge-tts"):
            try:
                subprocess.run(
                    ["edge-tts", "--voice", voice, "--text", t, "--write-media", str(out)],
                    check=True,
                    capture_output=True,
                    timeout=60,
                )
            except Exception as e2:
                return {"ok": False, "error": str(e2)[:200], "fallback": "browser_speech_synthesis"}
        else:
            return {"ok": False, "error": str(e)[:200], "fallback": "browser_speech_synthesis"}

    if not out.is_file() or out.stat().st_size < 50:
        return {"ok": False, "error": "tts_empty_file", "fallback": "browser_speech_synthesis"}

    return {
        "ok": True,
        "path": str(out),
        "url_path": f"/v1/voice/tts/file?name={out.name}",
        "mime": "audio/mpeg",
        "engine": "edge-tts",
        "bytes": out.stat().st_size,
        "voice": voice,
        "ms": int((time.time() - t0) * 1000),
    }
