"""Identity model — injects POCKET self-knowledge into the genetic flow."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class IdentityModel(InternalModel):
    id = "identity"
    name = "POCKET Identity"
    kind = "fusion"
    tags = ["pocket", "identity", "protocol", "who", "platform", "help"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        try:
            from pocket.pocket_identity import identity_payload

            p = identity_payload()
            return {"ok": True, "id": self.id, "ready": True, "product": p.get("product")}
        except Exception as e:
            return {"ok": True, "id": self.id, "ready": True, "note": str(e)[:80]}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("who are you", "pocket", "protocol", "identity", "what can you", "help me use")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, max(base, 0.35) + 0.18 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        try:
            from pocket.pocket_identity import identity_brief, protocols_brief

            text = (
                "## POCKET Identity (internal model)\n\n"
                + identity_brief(max_chars=1400, mode="genetic")
                + "\n\n"
                + protocols_brief(max_chars=500)
                + f"\n\n**User goal for genetic flow:** {goal[:500]}\n"
            )
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=True,
                text=text,
                engine="identity",
                model_id=self.id,
                latency_ms=ms,
                meta={"strategy": genome.strategy() if genome else "brief"},
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=False,
                text="",
                engine="identity",
                model_id=self.id,
                error=str(e)[:300],
                latency_ms=ms,
            )
