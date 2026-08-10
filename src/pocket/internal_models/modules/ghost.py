"""Ghost Math — deterministic pure-math internal model."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class GhostMathModel(InternalModel):
    id = "ghost"
    name = "Ghost Math"
    kind = "math"
    tags = ["math", "hash", "phi", "stats", "checksum", "deterministic", "ghost"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "id": self.id, "ready": True, "tokens": 0}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("math", "hash", "phi", "golden", "stats", "checksum", "digest", "number")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.15 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        try:
            from pocket.ghost_math import run_ghost

            text, err, eng = run_ghost(goal or "")
            ms = (time.perf_counter() - t0) * 1000
            ok = not err
            return ModelResult(
                ok=ok,
                text=text or "",
                engine=eng or "ghost-math",
                model_id=self.id,
                error=err or "",
                latency_ms=ms,
                meta={"strategy": genome.strategy() if genome else "brief"},
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=False,
                text="",
                engine="ghost-math",
                model_id=self.id,
                error=str(e)[:300],
                latency_ms=ms,
            )
