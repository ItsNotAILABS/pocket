"""Measure what this host actually has. No invented tensor units."""

from __future__ import annotations

import os
import platform
import time
from typing import Any, Dict


def _numpy_gflops(n: int = 384) -> Dict[str, Any]:
    try:
        import numpy as np

        a = np.random.randn(n, n).astype(np.float32)
        b = np.random.randn(n, n).astype(np.float32)
        # warmup
        a @ b
        t0 = time.perf_counter()
        c = a @ b
        dt = time.perf_counter() - t0
        flops = 2.0 * n * n * n
        gflops = (flops / dt) / 1e9 if dt else 0.0
        return {
            "ok": True,
            "backend": "numpy",
            "n": n,
            "sec": round(dt, 6),
            "gflops": round(gflops, 3),
            "checksum": float(c[0, 0]),
        }
    except Exception as e:
        return {"ok": False, "backend": "numpy", "error": str(e), "gflops": 0.0}


def _webgpu() -> Dict[str, Any]:
    try:
        from pocket.protocols.multi_sandbox_capsule import probe_webgpu

        return probe_webgpu()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _cuda() -> Dict[str, Any]:
    try:
        import torch

        if torch.cuda.is_available():
            return {
                "ok": True,
                "devices": torch.cuda.device_count(),
                "name": torch.cuda.get_device_name(0),
            }
        return {"ok": False, "reason": "torch present, cuda not available"}
    except Exception:
        return {"ok": False, "reason": "no torch.cuda"}


def _directml() -> Dict[str, Any]:
    try:
        import importlib.util

        return {"ok": bool(importlib.util.find_spec("torch_directml")), "name": "torch_directml"}
    except Exception:
        return {"ok": False}


def probe_host() -> Dict[str, Any]:
    cpus = os.cpu_count() or 1
    lanes = min(32, max(1, cpus))
    npb = _numpy_gflops()
    wg = _webgpu()
    cu = _cuda()
    backends = ["cpu"]
    if npb.get("ok"):
        backends.append("numpy")
    if wg.get("ok"):
        backends.append("webgpu")
    if cu.get("ok"):
        backends.append("cuda")
    return {
        "ok": True,
        "schema": "pocket.kernel.probe.v1",
        "os": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cpus": cpus,
        "logical_lanes": lanes,
        "lane_note": "Software dispatch lanes = min(32, cpu_count). Not claimed silicon tensor units.",
        "silicon_tensor_units": 0 if not cu.get("ok") else int(cu.get("devices") or 0),
        "backends": backends,
        "numpy_matmul": npb,
        "webgpu": wg,
        "cuda": cu,
        "directml": _directml(),
        "claims_forbidden": [
            "512 TFLOPS unless a real device reports it",
            "32 NPU tensor units unless a driver enumerates them",
            "sub-1.5ms per-token unless measured on a live model",
        ],
    }
