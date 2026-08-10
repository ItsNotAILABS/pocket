"""Concrete internal model modules."""

from pocket.internal_models.modules.ghost import GhostMathModel
from pocket.internal_models.modules.world import WorldModelModule
from pocket.internal_models.modules.auro import AuroModel
from pocket.internal_models.modules.guppy import GuppyModel
from pocket.internal_models.modules.heuristic import HeuristicModel
from pocket.internal_models.modules.identity import IdentityModel

ALL_MODULES = [
    GhostMathModel,
    WorldModelModule,
    AuroModel,
    GuppyModel,
    HeuristicModel,
    IdentityModel,
]

__all__ = [
    "GhostMathModel",
    "WorldModelModule",
    "AuroModel",
    "GuppyModel",
    "HeuristicModel",
    "IdentityModel",
    "ALL_MODULES",
]
