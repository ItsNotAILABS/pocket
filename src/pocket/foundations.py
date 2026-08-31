"""POCKET AI foundations — internal computational, math, self, and intelligence models.

Doctrine:
  Computational AI and math in POCKET are INTERNAL modules on this host.
  They do not call OpenAI / Anthropic / Gemini / a third-party CAS.
  Codex / Grok / Claude are optional *seated engines* (host CLIs), not the foundation.
  Nova hands sit on the same internal workspace.

Discover:
  GET /v1/foundations
  skill foundations_map
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from pocket import PRODUCT, TAGLINE, __version__

DOCTRINE = (
    "All computational AI and math models in POCKET are internal. "
    "Ghost Math, Logic, Pattern, Auro, World, Identity, Heuristic, Guppy, genetic flow "
    "run on this host with zero third-party inference. "
    "Codex/Grok/Claude seats are optional host engines, never required for math or self-models."
)

# Canonical internal families. Third-party APIs are not listed here.
INTERNAL_FAMILIES: List[Dict[str, Any]] = [
    {
        "id": "math",
        "name": "Internal math",
        "internal": True,
        "third_party": False,
        "models": ["ghost", "logic", "pattern"],
        "for": "Hashes, proofs, phi, stats, pattern decompose — no CAS cloud",
    },
    {
        "id": "self",
        "name": "Self models",
        "internal": True,
        "third_party": False,
        "models": ["identity", "heuristic"],
        "for": "Who we are, protocols, local planning without a vendor brain",
    },
    {
        "id": "intelligence",
        "name": "Intelligence world",
        "internal": True,
        "third_party": False,
        "models": ["world", "auro", "guppy"],
        "for": "World model memory, local meaning (Auro), Guppy desk helper",
    },
    {
        "id": "compute",
        "name": "Internal compute fabric",
        "internal": True,
        "third_party": False,
        "models": ["genetic_flow", "novae", "imagine"],
        "for": "Genetic expression of internal models, Novae workspace, Imagine stills",
    },
]


def _model_rows() -> List[Dict[str, Any]]:
    try:
        from pocket.internal_models import list_models

        rows = list_models()
        for r in rows:
            r["internal"] = True
            r["third_party"] = False
        return rows
    except Exception as e:
        return [{"ok": False, "error": str(e)[:160]}]


def _world() -> Dict[str, Any]:
    try:
        from pocket.world_model import status as wm

        s = wm()
        return {"ok": bool(s.get("ok")), "internal": True, "counts": s.get("counts") or s}
    except Exception as e:
        return {"ok": False, "internal": True, "error": str(e)[:120]}


def _novae() -> Dict[str, Any]:
    try:
        from pocket.novae import list_novae

        items = list_novae()
        return {
            "ok": True,
            "internal_workspace": True,
            "count": len(items),
            "ids": [n.get("id") for n in items],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}


def _imagine() -> Dict[str, Any]:
    try:
        from pocket.imagine_studio import status as st

        s = st()
        return {"ok": True, "ui": s.get("ui"), "counts": s.get("counts"), "internal": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}


def _signup() -> Dict[str, Any]:
    try:
        from pocket.users import public_signup_enabled

        return {"ok": True, "public_signup": public_signup_enabled(), "login": "/login", "signup": "/signup"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}


def catalog() -> Dict[str, Any]:
    models = _model_rows()
    math_ids = {"ghost", "logic", "pattern"}
    ready_math = [m for m in models if m.get("id") in math_ids and m.get("ready") is not False]
    return {
        "ok": True,
        "schema": "pocket.foundations.v1",
        "product": PRODUCT,
        "version": __version__,
        "tagline": TAGLINE,
        "doctrine": DOCTRINE,
        "internal": True,
        "third_party_required": False,
        "families": INTERNAL_FAMILIES,
        "models": models,
        "model_count": len([m for m in models if m.get("id")]),
        "math": {
            "internal": True,
            "ids": sorted(math_ids),
            "ready": len(ready_math),
        },
        "world": _world(),
        "novae": _novae(),
        "imagine": _imagine(),
        "auth": _signup(),
        "first_class_features": [
            "habitat",
            "desk",
            "screen",
            "phone",
            "studio",
            "imagine",
            "novae",
            "work",
            "fusion",
            "mcp",
            "internal_models",
            "genetic_flow",
            "world_model",
            "ghost_math",
            "public_signup",
        ],
        "api": {
            "this": "GET /v1/foundations",
            "internal_models": "GET /v1/internal-models",
            "express": "POST /v1/internal-models/express",
            "genetic": "POST /v1/genetic/run",
            "novae": "GET /v1/novae",
            "imagine": "GET /v1/imagine",
            "identity": "GET /v1/identity",
        },
        "ts": time.time(),
    }


def brief(*, max_chars: int = 900) -> str:
    lines = [
        "POCKET AI FOUNDATIONS (internal):",
        "· Math: Ghost Math · Logic · Pattern — zero third-party CAS",
        "· Self: Identity · Heuristic — who we are, local plans",
        "· Intelligence world: World model · Auro meaning · Guppy",
        "· Compute: genetic flow · Novae workspaces · Imagine stills",
        "· Optional seats (not foundations): Codex / Grok / Claude host CLIs",
        "· Discover: GET /v1/foundations · skill foundations_map",
    ]
    return "\n".join(lines)[:max_chars]


def ready() -> Dict[str, Any]:
    c = catalog()
    models = [m for m in (c.get("models") or []) if m.get("id")]
    math_ok = (c.get("math") or {}).get("ready", 0) >= 1
    return {
        "ok": bool(models) and math_ok,
        "models": len(models),
        "math_ready": (c.get("math") or {}).get("ready"),
        "world": (c.get("world") or {}).get("ok"),
        "third_party_required": False,
        "doctrine": "internal",
    }
