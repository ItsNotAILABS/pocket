"""Neuro-Silicon driver — userspace, measured, no slide FLOPS.

The calibration report format is kept. Numbers are filled from probe_host()
and timed loops on THIS machine. We never emit 512 TFLOPS or 1,450 tok/s
unless a real device measurement produced them.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from pocket.kernels.probe import probe_host
from pocket.kernels.slab import bench_slab

ROOT = Path.home() / ".pocket" / "kernels"
ROOT.mkdir(parents=True, exist_ok=True)
CAL = ROOT / "neuro_silicon_calibration.json"

DRIVER = "pocket.neuro-silicon.userspace"
VERSION = "1.0.0"


def driver_status() -> Dict[str, Any]:
    host = probe_host()
    return {
        "ok": True,
        "schema": "pocket.neuro_silicon.v1",
        "driver": DRIVER,
        "version": VERSION,
        "registered": True,
        "kind": "userspace",
        "not": [
            "Linux kmem_cache_create module",
            "custom wait-free NMI allocator",
            "undocumented 32-unit NPU unless cuda/webgpu enumerates devices",
        ],
        "lanes": host.get("logical_lanes"),
        "silicon_tensor_units": host.get("silicon_tensor_units"),
        "backends": host.get("backends"),
        "host": {k: host[k] for k in ("os", "cpus", "machine", "python") if k in host},
    }


def _token_proxy(*, n: int = 4000) -> Dict[str, Any]:
    """Cheap stand-in for tok/s: slab alloc + tiny transform. Not a language model."""
    from pocket.kernels.slab import get_cache

    c = get_cache("tokproxy", size=64)
    t0 = time.perf_counter()
    acc = 0
    for i in range(n):
        b = c.alloc()
        acc += b[0]
        b[0] = i & 255
        c.free(b)
    dt = time.perf_counter() - t0
    return {
        "ok": True,
        "proxy": "slab_touch",
        "ops": n,
        "sec": round(dt, 6),
        "ops_per_sec": int(n / dt) if dt else 0,
        "not_llm_tokens": True,
    }


def calibrate(*, run_loop: bool = True, goal: str = "") -> Dict[str, Any]:
    from pocket.kernels.cognitive_loop import run_loop as cloop

    t0 = time.perf_counter()
    host = probe_host()
    slab = bench_slab(n=8000)
    tok = _token_proxy()
    loop = None
    if run_loop:
        loop = cloop(goal or "calibrate neuro-silicon lanes", parallel=True)
    gflops = float((host.get("numpy_matmul") or {}).get("gflops") or 0.0)
    report = {
        "ok": True,
        "schema": "pocket.neuro_silicon.calibration.v1",
        "date": time.strftime("%Y-%m-%d"),
        "title": "Neuro-Silicon AI Acceleration Engine Calibration Report",
        "system_target": "POCKET Native Agent OS — swarm & agent framework",
        "hardware_driver": f"{DRIVER} {VERSION}",
        "executive": (
            f"Registered {host.get('logical_lanes')} software lanes on {host.get('cpus')} CPUs. "
            f"Silicon tensor units detected: {host.get('silicon_tensor_units')}. "
            f"Backends: {', '.join(host.get('backends') or [])}. "
            "All figures below are measured on this host. "
            "Marketing numbers (1450 tok/s, 512 TFLOPS, 12.4 ms cognitive) are NOT copied."
        ),
        "benchmarks": {
            "cpu_matmul_gflops": gflops,
            "slab_ops_per_sec": slab.get("ops_per_sec"),
            "slab_fast_ratio": slab.get("fast_ratio"),
            "token_proxy_ops_per_sec": tok.get("ops_per_sec"),
            "cognitive_loop_ms": (loop or {}).get("loop_ms"),
            "power_w": None,
            "power_note": "Not measured on this host (no RAPL/NVML hook wired).",
        },
        "vs_slide": {
            "tokens_per_sec_slide": 1450,
            "tokens_per_sec_measured_proxy": tok.get("ops_per_sec"),
            "vector_tflops_slide": 512,
            "vector_gflops_measured": gflops,
            "loop_ms_slide": 12.4,
            "loop_ms_measured": (loop or {}).get("loop_ms"),
            "honest": True,
        },
        "integration": {
            "cognitive_stages": 5,
            "mapped_to": "GET /v1/agents/invoke per stage",
            "telemetry": "GET /v1/kernels + ~/.pocket/kernels/neuro_silicon_calibration.json",
            "agents": ["gemini-coder", "sprint-orchestrator"],
        },
        "host": host,
        "slab": slab,
        "token_proxy": tok,
        "cognitive_loop": loop,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 3),
    }
    try:
        CAL.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        report["saved"] = str(CAL)
    except Exception as e:
        report["saved_error"] = str(e)
    return report
