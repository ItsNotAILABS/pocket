"""Nebius Token Factory — OpenAI-compatible inference for POCKET's reasoning lane.

Built for the Nebius × NVIDIA Global AI Hackathon (Personal AI track): this is
the additive lane that serves an NVIDIA Nemotron model from Nebius Token
Factory as a brain for POCKET's personal-AI surface (see nebius_brief.py).

Config lives in ~/.pocket/nebius.json (never the git tree), with environment
overrides NEBIUS_API_KEY / NEBIUS_BASE_URL / NEBIUS_MODEL — the same seam
shape as pocket.spark_api (POCKET-SECRET-REF: the key is a reference held
outside source control, never a value in it).

Endpoint: https://api.tokenfactory.nebius.com/v1 (OpenAI-compatible).
The API key is created by the account owner at tokenfactory.nebius.com;
without it every call returns a deterministic "not configured" result and
callers fall back to local behavior — nothing here fakes a model answer.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
CFG = ROOT / "nebius.json"
DEFAULT_BASE = "https://api.tokenfactory.nebius.com/v1"
# Catalog id as listed for Token Factory in Nebius's own examples; the exact
# deployed id for the account is confirmed post-key via models() and can be
# overridden with NEBIUS_MODEL / save(model=...) without a code change.
DEFAULT_MODEL = "nvidia/nemotron-3-nano-30b-a3b"


def _load() -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if CFG.is_file():
        try:
            data = json.loads(CFG.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    key = (os.environ.get("NEBIUS_API_KEY") or data.get("api_key") or "").strip()
    base = (os.environ.get("NEBIUS_BASE_URL") or data.get("base_url") or DEFAULT_BASE).rstrip("/")
    model = (os.environ.get("NEBIUS_MODEL") or data.get("model") or DEFAULT_MODEL).strip()
    return {
        "api_key": key,
        "base_url": base,
        "model": model,
        "protocol": "openai",
        "configured": bool(key),
        "path": str(CFG),
    }


def save(
    *,
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    cur = _load()
    rec = {
        "schema": "pocket.nebius.v1",
        "api_key": (api_key or cur.get("api_key") or "").strip(),
        "base_url": (base_url or cur.get("base_url") or DEFAULT_BASE).rstrip("/"),
        "model": (model or cur.get("model") or DEFAULT_MODEL).strip(),
        "protocol": "openai",
    }
    CFG.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    try:
        os.chmod(CFG, 0o600)
    except Exception:
        pass
    return status()


def status() -> Dict[str, Any]:
    c = _load()
    key = c.get("api_key") or ""
    return {
        "ok": bool(key),
        "schema": "pocket.nebius.v1",
        "provider": "nebius-token-factory",
        "configured": bool(key),
        "model": c.get("model"),
        "base_url": c.get("base_url"),
        "protocol": "openai",
        "key_prefix": (key[:12] + "…") if key else "",
        "note": "Key stays in ~/.pocket/nebius.json (0600) or NEBIUS_API_KEY. "
        "Create it at tokenfactory.nebius.com — account step is the owner's.",
    }


def _request(base: str, path: str, key: str, timeout: float, *, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = base.rstrip("/") + path
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PocketNebius/3.16.8",
        },
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw) if raw else {}
            return {"ok": True, "via": base, "http": resp.status, "data": data}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:800]
        return {"ok": False, "via": base, "http": e.code, "error": err or str(e)}
    except Exception as e:
        return {"ok": False, "via": base, "error": str(e)[:240]}


def _post(base: str, path: str, body: Dict[str, Any], key: str, timeout: float) -> Dict[str, Any]:
    return _request(base, path, key, timeout, body=body)


def models(timeout: float = 30) -> Dict[str, Any]:
    """List the account's served model ids (GET /models).

    This is the post-key confirmation step: the submission's deployed
    Nemotron model name comes from this list, never from a guess.
    """
    c = _load()
    key = c.get("api_key") or ""
    if not key:
        return {"ok": False, "engine": "nebius", "error": "Nebius API key not configured (~/.pocket/nebius.json)"}
    r = _request(c.get("base_url") or DEFAULT_BASE, "/models", key, timeout)
    if not r.get("ok"):
        r["engine"] = "nebius"
        return r
    rows = (r.get("data") or {}).get("data") or []
    ids = [str(m.get("id")) for m in rows if isinstance(m, dict) and m.get("id")]
    return {"ok": True, "engine": "nebius", "via": r.get("via"), "models": ids, "count": len(ids)}


def chat(
    prompt: str,
    *,
    system: str = "",
    model: str = "",
    max_tokens: int = 2048,
    timeout: float = 90,
    messages: Optional[List[Dict[str, Any]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """One OpenAI-compatible chat turn against Nebius Token Factory."""
    c = _load()
    key = c.get("api_key") or ""
    if not key:
        return {"ok": False, "engine": "nebius", "error": "Nebius API key not configured (~/.pocket/nebius.json)"}
    if messages is None:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": (prompt or "")[:12000]})
    payload: Dict[str, Any] = {
        "model": (model or c.get("model") or DEFAULT_MODEL),
        "messages": messages,
        "max_tokens": max(64, min(int(max_tokens or 2048), 8192)),
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    last = _post(c.get("base_url") or DEFAULT_BASE, "/chat/completions", payload, key, timeout)
    if last.get("ok"):
        data = last.get("data") or {}
        choice = ((data.get("choices") or [{}])[0]) if isinstance(data.get("choices"), list) else {}
        msg = (choice.get("message") or {}) if isinstance(choice, dict) else {}
        raw = msg.get("content") if isinstance(msg, dict) else None
        if raw is None:
            raw = choice.get("text") if isinstance(choice, dict) else ""
        if isinstance(raw, list):
            raw = "".join(
                str(p.get("text") or p.get("content") or "") if isinstance(p, dict) else str(p) for p in raw
            )
        reply = str(raw or "").strip()
        if not reply:
            reply = str((msg or {}).get("reasoning_content") or "").strip()
        tcs = (msg or {}).get("tool_calls") or []
        return {
            "ok": bool(reply or tcs),
            "engine": "nebius",
            "via": last.get("via"),
            "model": data.get("model") or payload["model"],
            "reply": (reply or ("" if tcs else "Nebius returned no text"))[-12000:],
            "tool_calls": tcs,
            "usage": data.get("usage") or {},
            "id": data.get("id"),
        }
    last["engine"] = "nebius"
    last["model"] = payload["model"]
    return last


def ping() -> Dict[str, Any]:
    return chat("Reply with the single word: pong", max_tokens=64, timeout=60)
