"""Heuristic synthesizer — always-on local model for genetic flow evaluation."""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


class HeuristicModel(InternalModel):
    id = "heuristic"
    name = "Heuristic Synthesizer"
    kind = "fusion"
    tags = ["plan", "outline", "structure", "steps", "heuristic", "local"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "id": self.id, "ready": True, "tokens": 0}

    def score_fit(self, goal: str) -> float:
        # Always modest baseline so population has a reliable citizen
        return 0.45 + 0.1 * min(1.0, len(goal or "") / 200)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        g = (goal or "").strip()
        words = re.findall(r"[A-Za-z0-9_\-]{3,}", g)
        uniq = []
        for w in words:
            lw = w.lower()
            if lw not in uniq:
                uniq.append(lw)
        digest = hashlib.sha256(g.encode("utf-8")).hexdigest()[:16]
        strategy = genome.strategy() if genome else "brief"
        models = genome.models() if genome else []
        steps = [
            "Clarify objective and success criteria",
            "Gather host state (identity, protocols, economy if needed)",
            "Select internal models by fitness for sub-tasks",
            "Express selected modules (genetic generation)",
            "Score phenotypes and keep elites",
            "Synthesize final answer + lineage receipt",
        ]
        body = [
            "## Heuristic plan (internal model)",
            "",
            f"**Goal digest:** `{digest}`",
            f"**Strategy gene:** `{strategy}`",
            f"**Co-models:** {', '.join(models) if models else '—'}",
            f"**Key terms:** {', '.join(uniq[:12]) if uniq else '—'}",
            "",
            "### Genetic flow steps",
        ]
        for i, s in enumerate(steps, 1):
            body.append(f"{i}. {s}")
        body.append("")
        body.append("### Decomposition")
        if not uniq:
            body.append("- (empty goal)")
        else:
            for term in uniq[:8]:
                body.append(f"- Handle **{term}** via best-fit internal model")
        body.append("")
        body.append("_Zero external tokens — pure host heuristic._")
        text = "\n".join(body)
        ms = (time.perf_counter() - t0) * 1000
        return ModelResult(
            ok=True,
            text=text,
            engine="heuristic",
            model_id=self.id,
            latency_ms=ms,
            meta={"terms": uniq[:12], "digest": digest, "strategy": strategy},
        )
