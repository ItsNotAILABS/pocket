"""Registry of internal model modules."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from pocket.internal_models.base import InternalModel

_REGISTRY: Dict[str, InternalModel] = {}
_BOOTED = False


def _boot() -> None:
    global _BOOTED
    if _BOOTED:
        return
    from pocket.internal_models.modules import ALL_MODULES

    for cls in ALL_MODULES:
        try:
            inst = cls() if isinstance(cls, type) else cls
            _REGISTRY[inst.id] = inst
        except Exception:
            continue
    _BOOTED = True


def register(model: InternalModel) -> None:
    _boot()
    _REGISTRY[model.id] = model


def get_model(model_id: str) -> Optional[InternalModel]:
    _boot()
    return _REGISTRY.get((model_id or "").strip().lower())


def list_models() -> List[Dict[str, Any]]:
    _boot()
    out = []
    for mid, m in sorted(_REGISTRY.items()):
        info = m.info()
        try:
            st = m.status()
            info["status"] = st
            info["ready"] = bool(st.get("ready") if "ready" in st else st.get("ok"))
        except Exception as e:
            info["status"] = {"ok": False, "error": str(e)[:120]}
            info["ready"] = False
        out.append(info)
    return out


def pick_for_goal(goal: str, *, limit: int = 4) -> List[Dict[str, Any]]:
    """Rank internal models by fit for a goal."""
    _boot()
    scored = []
    for mid, m in _REGISTRY.items():
        try:
            s = float(m.score_fit(goal or ""))
        except Exception:
            s = 0.0
        scored.append({"id": mid, "name": m.name, "kind": m.kind, "score": round(s, 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def express_one(model_id: str, goal: str, **kwargs: Any):
    m = get_model(model_id)
    if not m:
        from pocket.internal_models.base import ModelResult

        return ModelResult(ok=False, text="", engine="none", model_id=model_id or "", error="unknown model")
    return m.express(goal, **kwargs)
