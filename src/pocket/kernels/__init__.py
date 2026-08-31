"""POCKET userspace kernels — honest SLUB-shaped slab + Neuro-Silicon lanes.

This is not a Linux kernel module and not a novel Treiber-stack allocator.
Fast path = per-thread freelist (SLUB-shaped). Slow path = lock.
Neuro-Silicon = measured host lanes (CPU / WebGPU / CUDA if present), never slide FLOPS.
"""

from pocket.kernels.cognitive_loop import STAGES, run_loop
from pocket.kernels.long_workflow import ensure_running as ensure_workflows
from pocket.kernels.long_workflow import list_runs, start as start_workflow
from pocket.kernels.neuro_silicon import calibrate, driver_status
from pocket.kernels.probe import probe_host
from pocket.kernels.slab import SlabCache, slab_status

__all__ = [
    "STAGES",
    "SlabCache",
    "calibrate",
    "driver_status",
    "ensure_workflows",
    "list_runs",
    "probe_host",
    "run_loop",
    "slab_status",
    "start_workflow",
]
