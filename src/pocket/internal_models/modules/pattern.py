"""Internal pattern forge — local spectral-ish decompose, no third-party math API."""

from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


def _decompose(goal: str) -> str:
    raw = (goal or "").encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    n = max(1, len(raw))
    # Cheap local spectrum: byte histogram energy + phi scale
    hist = [0] * 16
    for b in raw:
        hist[b % 16] += 1
    energy = sum(c * c for c in hist) / n
    phi = (1 + math.sqrt(5)) / 2
    bands = [{"bin": i, "count": hist[i], "share": round(hist[i] / n, 4)} for i in range(16) if hist[i]]
    bands.sort(key=lambda x: x["count"], reverse=True)
    return (
        "## Pattern Forge (internal)\n\n"
        f"**sha256:** `{digest}`\n"
        f"**bytes:** {n} · **energy:** {energy:.4f} · **phi:** {phi:.6f}\n"
        f"**top bins:** {bands[:6]}\n\n"
        "Local decompose only. No third-party spectral API.\n"
    )


class PatternForgeModel(InternalModel):
    id = "pattern"
    name = "Pattern Forge"
    kind = "math"
    tags = ["math", "pattern", "spectral", "xray", "phi", "internal"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "id": self.id, "ready": True, "tokens": 0, "third_party": False}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("pattern", "spectral", "decompose", "xray", "forge", "fft", "harmonic")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.16 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        return ModelResult(
            ok=True,
            text=_decompose(goal or ""),
            engine="pattern-internal",
            model_id=self.id,
            latency_ms=(time.perf_counter() - t0) * 1000,
            meta={"third_party": False, "internal": True},
        )
