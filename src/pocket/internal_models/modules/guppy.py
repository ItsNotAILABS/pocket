"""Guppy — local desktop/web actuator internal model."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class GuppyModel(InternalModel):
    id = "guppy"
    name = "Guppy Desk"
    kind = "actuator"
    tags = ["guppy", "desktop", "open", "fetch", "lookup", "act", "browser"]
    cost = "host"

    def status(self) -> Dict[str, Any]:
        try:
            from pocket.guppy import identity

            return {"ok": True, "id": self.id, "ready": True, **identity()}
        except Exception as e:
            return {"ok": False, "id": self.id, "ready": False, "error": str(e)[:200]}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("open ", "fetch", "lookup", "desktop", "edge", "navigate", "guppy", "bring back")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.16 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        # Genetic flow default: identity + plan only unless strategy=act
        strategy = genome.strategy() if genome else "brief"
        try:
            from pocket.guppy import identity, run_guppy

            if strategy in ("brief", "memory", "math") and "open" not in (goal or "").lower():
                idn = identity()
                body = (
                    f"## Guppy (genetic brief)\n\n"
                    f"**{idn.get('full')}** — {idn.get('tagline')}\n\n"
                    f"Capabilities: {', '.join((idn.get('capabilities') or [])[:6])}\n\n"
                    f"_Not actuating in strategy={strategy}. Use strategy=act to run desk steps._\n"
                    f"**Goal:** {goal[:400]}\n"
                )
                ms = (time.perf_counter() - t0) * 1000
                return ModelResult(
                    ok=True,
                    text=body,
                    engine="guppy",
                    model_id=self.id,
                    latency_ms=ms,
                    meta={"strategy": strategy, "actuated": False},
                )
            text, err, eng = run_guppy(goal or "", cwd=kwargs.get("cwd") or "", job=kwargs.get("job"))
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=not bool(err) or bool(text),
                text=text or "",
                engine=eng or "guppy",
                model_id=self.id,
                error=err or "",
                latency_ms=ms,
                meta={"strategy": strategy, "actuated": True},
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=False,
                text="",
                engine="guppy",
                model_id=self.id,
                error=str(e)[:300],
                latency_ms=ms,
            )
