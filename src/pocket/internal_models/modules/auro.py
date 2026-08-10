"""Auro — local meaning / native LLM internal model."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class AuroModel(InternalModel):
    id = "auro"
    name = "Auro Meaning"
    kind = "local_llm"
    tags = ["auro", "meaning", "local", "lmr", "native", "model"]
    cost = "host"

    def status(self) -> Dict[str, Any]:
        try:
            from pocket.auro_meaning import status as meaning_status

            st = meaning_status()
            return {"ok": bool(st.get("ok") or st.get("ready") or True), "id": self.id, **(st if isinstance(st, dict) else {})}
        except Exception:
            try:
                from pocket.auro14b_bridge import auro_root

                root = auro_root()
                return {"ok": bool(root), "id": self.id, "ready": bool(root), "root": str(root) if root else None}
            except Exception as e:
                return {"ok": False, "id": self.id, "ready": False, "error": str(e)[:200]}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("auro", "meaning", "local model", "lmr", "explain", "compose", "reason")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.14 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        strategy = genome.strategy() if genome else "brief"
        # Genetic flow default (brief): status-only — full Auro job is expensive
        if strategy in ("brief", "math", "memory"):
            try:
                st = self.status()
                body = (
                    f"## Auro (genetic brief)\n\n"
                    f"**ready:** {st.get('ready', st.get('ok'))}\n"
                    f"**status keys:** {', '.join(list(st.keys())[:12])}\n\n"
                    f"**Goal held for deep pass:** { (goal or '')[:400] }\n\n"
                    f"_Use strategy=deep to invoke full Auro meaning/job path._\n"
                )
                ms = (time.perf_counter() - t0) * 1000
                return ModelResult(
                    ok=True,
                    text=body,
                    engine="auro-brief",
                    model_id=self.id,
                    latency_ms=ms,
                    meta={"strategy": strategy, "full_run": False},
                )
            except Exception as e:
                ms = (time.perf_counter() - t0) * 1000
                return ModelResult(
                    ok=False, text="", engine="auro", model_id=self.id, error=str(e)[:300], latency_ms=ms
                )
        try:
            from pocket.auro14b_bridge import run_auro_job

            text, err, eng = run_auro_job(goal or "", job=kwargs.get("job"))
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=not bool(err) or bool(text),
                text=text or "",
                engine=eng or "auro",
                model_id=self.id,
                error=err or "",
                latency_ms=ms,
                meta={"strategy": strategy, "full_run": True},
            )
        except Exception as e:
            ms = (time.perf_counter() - t0) * 1000
            return ModelResult(
                ok=False,
                text="",
                engine="auro",
                model_id=self.id,
                error=str(e)[:300],
                latency_ms=ms,
            )
