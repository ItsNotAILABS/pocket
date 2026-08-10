"""World Model — SQLite memory / fact / archetype internal model."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class WorldModelModule(InternalModel):
    id = "world"
    name = "World Model"
    kind = "memory"
    tags = ["memory", "fact", "world", "knowledge", "archetype", "syntax", "recall"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        try:
            from pocket import world_model as wm

            path = wm.ensure_db()
            return {"ok": True, "id": self.id, "ready": True, "db": str(path)}
        except Exception as e:
            return {"ok": False, "id": self.id, "ready": False, "error": str(e)[:200]}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("remember", "fact", "what is", "knowledge", "world", "archetype", "syntax", "recall")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.12 * hit + 0.1)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        try:
            from pocket import world_model as wm

            wm.ensure_db()
            brief = wm.cortex_context(goal or "", limit=8)
            hits = wm.search(goal or "", kind="all", limit=6)
            fc = wm.fact_check(goal or "")
            n = len(hits.get("results") or [])
            body = (
                f"## World Model\n\n"
                f"{brief or '_No stored brief yet._'}\n\n"
                f"**search hits:** {n} · **fact supported:** {fc.get('supported')}\n"
            )
            if fc.get("matches"):
                body += "\n### Fact matches\n"
                for m in (fc.get("matches") or [])[:5]:
                    body += f"- {m}\n"
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=True,
                text=body,
                engine="world-model",
                model_id=self.id,
                latency_ms=ms,
                meta={"hits": n, "fact_check": fc.get("supported"), "strategy": genome.strategy() if genome else "brief"},
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=False,
                text="",
                engine="world-model",
                model_id=self.id,
                error=str(e)[:300],
                latency_ms=ms,
            )
