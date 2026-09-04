"""Reagent Spark — OpenAI-compatible inference on this host.

Config lives in ~/.pocket/spark.json (never the git tree).
Public: https://spark.reagent-systems.com/v1
Tailnet: http://100.85.119.35:8000/v1
Model: qwen3.8-27b
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
CFG = ROOT / "spark.json"
DEFAULT_PUBLIC = "https://spark.reagent-systems.com/v1"
DEFAULT_TAILNET = "http://100.85.119.35:8000/v1"
DEFAULT_MODEL = "qwen3.8-27b"


def _load() -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if CFG.is_file():
        try:
            data = json.loads(CFG.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    key = (os.environ.get("SPARK_API_KEY") or data.get("api_key") or "").strip()
    public = (os.environ.get("SPARK_BASE_URL") or data.get("base_url") or DEFAULT_PUBLIC).rstrip("/")
    tail = (os.environ.get("SPARK_TAILNET") or data.get("tailnet") or DEFAULT_TAILNET).rstrip("/")
    model = (os.environ.get("SPARK_MODEL") or data.get("model") or DEFAULT_MODEL).strip()
    return {
        "api_key": key,
        "base_url": public,
        "tailnet": tail,
        "model": model,
        "protocol": "openai",
        "configured": bool(key),
        "path": str(CFG),
    }


def save(
    *,
    api_key: str = "",
    base_url: str = "",
    tailnet: str = "",
    model: str = "",
) -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    cur = _load()
    rec = {
        "schema": "pocket.spark.v1",
        "api_key": (api_key or cur.get("api_key") or "").strip(),
        "base_url": (base_url or cur.get("base_url") or DEFAULT_PUBLIC).rstrip("/"),
        "tailnet": (tailnet or cur.get("tailnet") or DEFAULT_TAILNET).rstrip("/"),
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
        "schema": "pocket.spark.v1",
        "configured": bool(key),
        "model": c.get("model"),
        "base_url": c.get("base_url"),
        "tailnet": c.get("tailnet"),
        "protocol": "openai",
        "key_prefix": (key[:12] + "…") if key else "",
        "limits": "20 req/min · 2 concurrent · 500K tokens/day (Spark fair use)",
        "note": "Inference is open on announced free days. Key stays in ~/.pocket/spark.json.",
    }


def _post(base: str, path: str, body: Dict[str, Any], key: str, timeout: float) -> Dict[str, Any]:
    url = base.rstrip("/") + path
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PocketSpark/3.16.8",
        },
        method="POST",
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
    """One OpenAI-compatible chat turn. Public URL first, tailnet fallback."""
    c = _load()
    key = c.get("api_key") or ""
    if not key:
        return {"ok": False, "engine": "spark", "error": "Spark API key not configured (~/.pocket/spark.json)"}
    if messages is None:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": (prompt or "")[:12000]})
    payload: Dict[str, Any] = {
        "model": (model or c.get("model") or DEFAULT_MODEL),
        "messages": messages,
        "max_tokens": max(64, min(int(max_tokens or 2048), 8192)),
        "enable_thinking": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    bases = [c.get("base_url") or DEFAULT_PUBLIC]
    tail = c.get("tailnet") or DEFAULT_TAILNET
    if tail and tail not in bases:
        bases.append(tail)
    last: Dict[str, Any] = {"ok": False, "error": "no endpoint"}
    for base in bases:
        last = _post(base, "/chat/completions", payload, key, timeout)
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
                "engine": "spark",
                "via": last.get("via"),
                "model": data.get("model") or payload["model"],
                "reply": (reply or ("" if tcs else "Spark returned no text"))[-12000:],
                "tool_calls": tcs,
                "usage": data.get("usage") or {},
                "id": data.get("id"),
            }
        http = int(last.get("http") or 0)
        err = str(last.get("error") or "")
        # Cloudflare 1010 is not a bad key — fall through to Tailscale.
        if http in (401, 403) and "cloudflare" not in err.lower() and "1010" not in err:
            break
    last["engine"] = "spark"
    last["model"] = payload["model"]
    return last


def ping() -> Dict[str, Any]:
    return chat("Reply with the single word: pong", max_tokens=64, timeout=60)
