"""POCKET internal models as modules that execute the genetic flow.

Doctrine:
  · Every internal model is a pluggable module (InternalModel).
  · The genetic flow evolves genomes (which modules + strategy) over generations.
  · Best phenotype is the answer — with lineage receipt.

Usage:
  from pocket.internal_models import list_models, run_genetic_flow, run_job
  run_genetic_flow("hash this goal and plan next steps")
"""

from pocket.internal_models.base import Genome, InternalModel, ModelResult
from pocket.internal_models.genetic_flow import (
    format_markdown,
    list_runs,
    run_genetic_flow,
    run_job,
    score_fitness,
)
from pocket.internal_models.registry import express_one, get_model, list_models, pick_for_goal, register

__all__ = [
    "Genome",
    "InternalModel",
    "ModelResult",
    "list_models",
    "get_model",
    "register",
    "pick_for_goal",
    "express_one",
    "run_genetic_flow",
    "run_job",
    "score_fitness",
    "format_markdown",
    "list_runs",
]
