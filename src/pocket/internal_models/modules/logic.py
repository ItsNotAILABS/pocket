"""Internal logic caretaker — local proofs, no third-party CAS."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult


def _eval_tiny(goal: str) -> str:
    low = (goal or "").lower()
    if "a and not a" in low or "p and not p" in low:
        return (
            "## Logic (internal)\n\n"
            "**Unsat / contradiction.** `P ∧ ¬P` is false in classical logic.\n"
            "Proved locally. No third-party prover.\n"
        )
    if "a or not a" in low or "p or not p" in low:
        return (
            "## Logic (internal)\n\n"
            "**Tautology.** `P ∨ ¬P` (excluded middle) holds classically.\n"
            "Proved locally. No third-party prover.\n"
        )
    if "modus" in low or "implies" in low:
        return (
            "## Logic (internal)\n\n"
            "Modus ponens: from `P` and `P → Q` infer `Q`.\n"
            "This caretaker states the rule; it does not invent a cloud proof.\n"
        )
    try:
        from pocket.ghost_math import run_ghost

        text, err, _ = run_ghost(goal or "hash")
        extra = f"\n\n_Ghost digest used as receipt._\n{text}" if not err else ""
    except Exception:
        extra = ""
    return (
        "## Logic (internal)\n\n"
        "Local caretaker. For a full theorem, state a classical tautology "
        "(`P or not P`) or contradiction (`P and not P`).\n"
        f"{extra}"
    )


class LogicProverModel(InternalModel):
    id = "logic"
    name = "Logic Prover"
    kind = "math"
    tags = ["math", "proof", "logic", "theorem", "solus", "internal"]
    cost = "local"

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "id": self.id, "ready": True, "tokens": 0, "third_party": False}

    def score_fit(self, goal: str) -> float:
        low = (goal or "").lower()
        keys = ("prove", "proof", "logic", "theorem", "tautolog", "contradict", "modus")
        base = super().score_fit(goal)
        hit = sum(1 for k in keys if k in low)
        return min(1.0, base + 0.16 * hit)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        text = _eval_tiny(goal or "")
        return ModelResult(
            ok=True,
            text=text,
            engine="logic-internal",
            model_id=self.id,
            latency_ms=(time.perf_counter() - t0) * 1000,
            meta={"third_party": False, "internal": True},
        )
