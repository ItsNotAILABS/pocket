"""Concrete internal model modules."""

from pocket.internal_models.modules.ghost import GhostMathModel
from pocket.internal_models.modules.world import WorldModelModule
from pocket.internal_models.modules.auro import AuroModel
from pocket.internal_models.modules.guppy import GuppyModel
from pocket.internal_models.modules.heuristic import HeuristicModel
from pocket.internal_models.modules.identity import IdentityModel
from pocket.internal_models.modules.logic import LogicProverModel
from pocket.internal_models.modules.pattern import PatternForgeModel

ALL_MODULES = [
    GhostMathModel,
    LogicProverModel,
    PatternForgeModel,
    WorldModelModule,
    AuroModel,
    GuppyModel,
    HeuristicModel,
    IdentityModel,
]

__all__ = [
    "GhostMathModel",
    "LogicProverModel",
    "PatternForgeModel",
    "WorldModelModule",
    "AuroModel",
    "GuppyModel",
    "HeuristicModel",
    "IdentityModel",
    "ALL_MODULES",
]
