"""Live catalog of real engines on this host — CLIs, internals, PhoneAI surfaces."""

from __future__ import annotations

from typing import Any, Dict, List


def catalog() -> Dict[str, Any]:
    clis: List[Dict[str, Any]] = []
    try:
        from pocket.model_clis import MODEL_CLIS, detect

        for spec in MODEL_CLIS:
            d = detect(spec)
            clis.append(
                {
                    "id": spec["id"],
                    "label": spec.get("label") or spec["id"],
                    "kind": "cli",
                    "available": bool(d.get("available")),
                    "path": d.get("path") or "",
                    "group": spec.get("group") or "model",
                }
            )
    except Exception:
        pass

    internals: List[Dict[str, Any]] = []
    try:
        from pocket.internal_models.registry import list_models

        for m in list_models():
            internals.append(
                {
                    "id": m.get("id"),
                    "label": m.get("name") or m.get("id"),
                    "kind": "internal",
                    "available": bool(m.get("ready")),
                    "group": m.get("kind") or "internal",
                }
            )
    except Exception:
        pass

    surfaces = [
        {"id": "portal", "label": "Portal stream", "kind": "surface", "available": True, "path": "/phoneai/portal"},
        {"id": "antigravity", "label": "Antigravity app", "kind": "surface", "available": True, "path": "/phoneai/anti"},
        {"id": "imagine", "label": "Imagine", "kind": "surface", "available": True, "path": "/imagine"},
        {"id": "life", "label": "Phone life", "kind": "surface", "available": True, "path": "/phoneai"},
        {"id": "harness", "label": "Work harness", "kind": "surface", "available": True, "path": "/v1/phoneai/harness"},
        {"id": "shell", "label": "Bounded shell", "kind": "surface", "available": True, "path": "/v1/phoneai/shell"},
    ]
    from pathlib import Path

    forge = Path.home() / "OneDrive" / "sovereign_forge_os"
    if forge.is_dir():
        surfaces.append(
            {
                "id": "sovereign_forge",
                "label": "Sovereign Forge OS",
                "kind": "repo",
                "available": True,
                "path": str(forge),
            }
        )

    ready = [c["id"] for c in clis if c.get("available")] + [i["id"] for i in internals if i.get("available")]
    return {
        "ok": True,
        "product": "POCKET engines",
        "cli": clis,
        "internal": internals,
        "surfaces": surfaces,
        "ready": ready,
        "desk": [x for x in ready if x in ("grok", "codex", "claude", "gemini", "qwen", "opencode", "copilot", "spark")],
        "phone_fast": [x for x in ready if x in ("auro", "ghost", "logic", "pattern", "heuristic", "world", "guppy")],
    }


def internal_reply(text: str, prefer: str = "") -> Dict[str, Any]:
    """Run a real internal model now — no nested Grok CLI."""
    from pocket.internal_models.registry import express_one, pick_for_goal

    mid = (prefer or "").strip().lower()
    if mid not in ("auro", "ghost", "logic", "pattern", "heuristic", "world", "guppy", "identity"):
        picks = pick_for_goal(text or "", limit=1)
        mid = str((picks[0] or {}).get("id") or "heuristic") if picks else "heuristic"
    r = express_one(mid, text or "")
    d = r.as_dict() if hasattr(r, "as_dict") else {"ok": False, "text": "", "error": "no result"}
    reply = (d.get("text") or d.get("error") or "").strip()
    return {
        "ok": bool(d.get("ok", True) and reply),
        "engine": d.get("model_id") or mid,
        "reply": reply[-8000:] or "internal model empty",
        "internal": True,
        "latency_ms": d.get("latency_ms"),
    }
