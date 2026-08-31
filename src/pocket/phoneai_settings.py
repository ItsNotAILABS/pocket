"""PhoneAI settings — which coding CLIs are on, and which can be installed now."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, List

from pocket.model_clis import MODEL_CLIS, detect, ensure_host_clis

ROOT = Path.home() / ".pocket" / "phoneai"
FILE = ROOT / "settings.json"

# Always on the coding desk when the binary exists.
CORE = ("grok", "codex", "claude", "gemini", "qwen", "spark")
# User asked these as Settings options.
OPTIONAL = ("opencode", "cursor", "aider", "copilot")


def _load() -> Dict[str, Any]:
    if FILE.is_file():
        try:
            data = json.loads(FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"enabled": {}, "chat": "grok"}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def chat_engine() -> str:
    return str(_load().get("chat") or "grok")


def enabled_ids() -> List[str]:
    data = _load()
    en = data.get("enabled") or {}
    out = []
    for spec in MODEL_CLIS:
        i = spec["id"]
        det = detect(spec)
        if i in OPTIONAL:
            if en.get(i, det.get("available")):
                out.append(i)
        else:
            if en.get(i, True) and (det.get("available") or i in CORE):
                out.append(i)
    return out


def snapshot() -> Dict[str, Any]:
    data = _load()
    en = data.get("enabled") or {}
    tools = []
    for spec in MODEL_CLIS:
        det = detect(spec)
        i = spec["id"]
        optional = i in OPTIONAL
        on = bool(en.get(i, det.get("available") if optional else True))
        can_now = bool(det.get("available") or spec.get("npm") or spec.get("pip") or spec.get("install_hint"))
        tools.append(
            {
                **det,
                "enabled": on,
                "optional": optional,
                "can_make_now": can_now,
                "now": "ready" if det.get("available") else ("installable" if can_now else "later"),
            }
        )
    return {
        "ok": True,
        "chat": data.get("chat") or "grok",
        "enabled": enabled_ids(),
        "tools": tools,
        "note": (
            "Ready now: Grok, Codex, Claude, Gemini, Qwen, OpenCode, Copilot. "
            "Install now from Settings: Aider (pip), Cursor Agent. "
            "Glimmer weights: ollama pull muse-glimmer (~18GB). Main chat is Grok."
        ),
    }


def set_enabled(cli_id: str, on: bool) -> Dict[str, Any]:
    data = _load()
    en = dict(data.get("enabled") or {})
    en[str(cli_id)] = bool(on)
    data["enabled"] = en
    _save(data)
    return snapshot()


def set_chat(engine: str) -> Dict[str, Any]:
    data = _load()
    data["chat"] = (engine or "grok").strip().lower() or "grok"
    _save(data)
    return snapshot()


def install(cli_id: str) -> Dict[str, Any]:
    """Install one optional CLI on the host (npm/pip)."""
    spec = next((s for s in MODEL_CLIS if s["id"] == cli_id), None)
    if not spec:
        return {"ok": False, "error": "unknown cli"}
    det = detect(spec)
    if det.get("available"):
        set_enabled(cli_id, True)
        return {"ok": True, "id": cli_id, "action": "present", **snapshot()}

    def _run():
        try:
            ensure_host_clis(install=True)
        except Exception:
            pass

    threading.Thread(target=_run, name=f"install-{cli_id}", daemon=True).start()
    set_enabled(cli_id, True)
    return {
        "ok": True,
        "id": cli_id,
        "action": "installing",
        "hint": spec.get("install_hint") or spec.get("npm") or spec.get("pip") or "",
        **snapshot(),
    }


def apply(body: Dict[str, Any]) -> Dict[str, Any]:
    if body.get("chat"):
        set_chat(str(body.get("chat")))
    if body.get("id") and "enabled" in body:
        set_enabled(str(body.get("id")), bool(body.get("enabled")))
    if body.get("id") and body.get("install"):
        return install(str(body.get("id")))
    return snapshot()
