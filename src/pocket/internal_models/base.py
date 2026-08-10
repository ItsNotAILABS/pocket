"""Base contract for POCKET internal models (modules that run the genetic flow)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ModelResult:
    """Phenotype produced by one internal model expression."""

    ok: bool
    text: str
    engine: str
    model_id: str
    fitness: float = 0.0
    error: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "text": self.text,
            "engine": self.engine,
            "model_id": self.model_id,
            "fitness": self.fitness,
            "error": self.error,
            "meta": self.meta,
            "latency_ms": self.latency_ms,
        }


@dataclass
class Genome:
    """Genetic encoding of how to run internal models for a goal.

    genes:
      models   — ordered internal model ids to express
      weight   — selection bias (0..1)
      strategy — brief | deep | math | memory | act
      mutate   — mutation rate hint
      elite    — protected from death
    """

    id: str
    genes: Dict[str, Any]
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    fitness: float = 0.0
    result: Optional[ModelResult] = None

    def models(self) -> List[str]:
        m = self.genes.get("models") or []
        if isinstance(m, str):
            return [m]
        return [str(x) for x in m if x]

    def strategy(self) -> str:
        return str(self.genes.get("strategy") or "brief")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "genes": self.genes,
            "generation": self.generation,
            "parent_ids": list(self.parent_ids),
            "fitness": self.fitness,
            "result": self.result.as_dict() if self.result else None,
        }


class InternalModel(ABC):
    """One pluggable internal model module."""

    id: str = "base"
    name: str = "Base"
    kind: str = "internal"  # math | memory | local_llm | actuator | fusion
    tags: List[str] = []
    cost: str = "local"  # local | host | remote

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """Health / readiness without heavy work."""

    @abstractmethod
    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        """Run this model on a goal (express genes → phenotype)."""

    def score_fit(self, goal: str) -> float:
        """How well this model matches the goal (0..1) before full express."""
        low = (goal or "").lower()
        score = 0.15
        for t in self.tags:
            if t.lower() in low:
                score += 0.2
        return min(1.0, score)

    def info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "tags": list(self.tags),
            "cost": self.cost,
            "module": f"{self.__class__.__module__}.{self.__class__.__name__}",
        }
