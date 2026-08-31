"""Honest kernels — no slide FLOPS, SLUB-shaped slab, real probe."""

from pocket.kernels.neuro_silicon import calibrate, driver_status
from pocket.kernels.probe import probe_host
from pocket.kernels.slab import bench_slab, get_cache, slab_status


def test_slab_fast_path_and_honesty():
    c = get_cache("test", size=128)
    a = c.alloc()
    assert len(a) == 128
    c.free(a)
    st = bench_slab(n=2000, size=128)
    assert st["ok"] and st["ops_per_sec"] > 0
    assert st["lock_free_design"] is False
    assert st["lockless_fast_path"] is True
    assert "Treiber" in (slab_status().get("doctrine") or "") or "not a novel" in (
        slab_status().get("doctrine") or ""
    ).lower()


def test_probe_does_not_invent_tflops():
    h = probe_host()
    assert h["ok"]
    assert h["logical_lanes"] <= 32
    assert "512 TFLOPS" in " ".join(h["claims_forbidden"])
    g = float((h.get("numpy_matmul") or {}).get("gflops") or 0)
    assert g < 500_000  # GFLOPS ceiling; 512 TFLOPS = 512000 GFLOPS


def test_calibrate_honest_vs_slide():
    r = calibrate(run_loop=False)
    assert r["ok"]
    assert r["vs_slide"]["honest"] is True
    assert r["vs_slide"]["vector_tflops_slide"] == 512
    measured = r["vs_slide"]["vector_gflops_measured"]
    assert measured < 512_000
    d = driver_status()
    assert d["kind"] == "userspace"
    assert d.get("silicon_tensor_units") is not None
