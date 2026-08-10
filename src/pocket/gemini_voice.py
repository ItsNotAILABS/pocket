"""Gemini brain for Aria — optional real LLM when GEMINI_API_KEY is set.

Free tier: Google AI Studio key (https://aistudio.google.com/apikey)
Loads from env or ~/.pocket/keys.env (never commit keys).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

KEYS_PATH = Path.home() / ".pocket" / "keys.env"
DEFAULT_MODEL = os.environ.get("POCKET_GEMINI_MODEL") or "gemini-2.0-flash"


def _load_keys_file() -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not KEYS_PATH.is_file():
        return out
    try:
        for line in KEYS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return out


def get_gemini_key() -> str:
    for name in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_AI_API_KEY",
        "POCKET_GEMINI_KEY",
        "GOOGLE_GENERATIVE_AI_API_KEY",
    ):
        v = (os.environ.get(name) or "").strip()
        if v:
            return v
    file_keys = _load_keys_file()
    for name in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_AI_API_KEY",
        "POCKET_GEMINI_KEY",
    ):
        v = (file_keys.get(name) or "").strip()
        if v:
            return v
    return ""


def gemini_configured() -> bool:
    return bool(get_gemini_key())


def status() -> Dict[str, Any]:
    key = get_gemini_key()
    return {
        "ok": True,
        "configured": bool(key),
        "key_source": "env_or_keys.env" if key else "none",
        "key_len": len(key) if key else 0,
        "model": DEFAULT_MODEL,
        "keys_file": str(KEYS_PATH),
        "hint": (
            "Set GEMINI_API_KEY in environment or write ~/.pocket/keys.env "
            "with GEMINI_API_KEY=... from https://aistudio.google.com/apikey"
        ),
    }


_ARIA_SYSTEM = """You are Aria, the voice co-pilot inside POCKET (local host product by ItsNotAI Labs).
You speak out loud — keep replies SHORT (1–3 sentences) unless the user asks for detail.
Be warm, clear, useful. Never invent that you already paid or booked something.
You can help with everyday life, lists, planning, and host actions the system already ran.
If host tools already ran (food/flights/screen), acknowledge results and tell the user what to do next.
Do not use markdown code fences. Plain spoken English."""


def gemini_chat(
    text: str,
    *,
    history: Optional[List[Dict[str, str]]] = None,
    context: str = "",
    model: str = "",
) -> Dict[str, Any]:
    """One conversational turn via Gemini generateContent (free-tier friendly flash models)."""
    key = get_gemini_key()
    if not key:
        return {"ok": False, "error": "no_gemini_key", "hint": status()["hint"]}

    model = (model or DEFAULT_MODEL).strip()
    # Build contents
    contents: List[Dict[str, Any]] = []
    for h in (history or [])[-8:]:
        role = "user" if h.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": str(h.get("text") or "")[:2000]}]})
    user_blob = text
    if context:
        user_blob = f"[Host context]\n{context[:1500]}\n\n[User]\n{text}"
    contents.append({"role": "user", "parts": [{"text": user_blob[:4000]}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={urllib.parse.quote(key)}"
    )

    body = {
        "systemInstruction": {"parts": [{"text": _ARIA_SYSTEM}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 256,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "POCKET-Aria/3.5"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw) if raw else {}
        # Extract text
        reply = ""
        for cand in data.get("candidates") or []:
            content = cand.get("content") or {}
            for part in content.get("parts") or []:
                if part.get("text"):
                    reply += str(part.get("text"))
        reply = re.sub(r"\s+", " ", (reply or "").strip())
        if not reply:
            return {
                "ok": False,
                "error": "empty_gemini_reply",
                "raw_keys": list(data.keys())[:8],
            }
        # Cap for speech
        if len(reply) > 500:
            reply = reply[:480].rsplit(" ", 1)[0] + "…"
        return {
            "ok": True,
            "reply": reply,
            "model": model,
            "engine": "gemini",
            "usage": data.get("usageMetadata") or {},
        }
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:400]
        except Exception:
            err_body = str(e)
        return {"ok": False, "error": f"gemini_http_{e.code}", "detail": err_body}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
