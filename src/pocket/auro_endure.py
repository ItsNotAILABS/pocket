"""Auro Endure — experiment variants, keep going, write receipts.

Pocket adapter. Prefers Auro14B organism.endure; falls back to internal Auro
meaning so the mode still exists when the native runtime is not on path.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

SCHEMA = "pocket.auro.endure.v1"
OUT = Path.home() / ".pocket" / "auro_endure"


def _native(goal: str, *, experiments: int, cycles: int) -> Dict[str, Any]:
    from pocket.auro14b_bridge import auro_root

    root = auro_root()
    if not root:
        raise RuntimeError("Auro14B root not found")
    import sys

    p = str(root)
    if p not in sys.path:
        sys.path.insert(0, p)
    from auro_native_llm.organism.endure import run_endure

    return run_endure(goal, experiments=experiments, cycles=cycles)


def _fallback(goal: str, *, experiments: int, cycles: int) -> Dict[str, Any]:
    from pocket.internal_models.registry import express_one

    receipts: List[Dict[str, Any]] = []
    best: Dict[str, Any] = {}
    t0 = time.time()
    n = max(1, experiments) + max(0, cycles)
    for i in range(n):
        tag = "experiment" if i < experiments else "endure"
        prompt = f"{goal}\n[{tag} {i + 1}/{n} — try a different angle, keep going]"
        r = express_one("auro", prompt)
        d = r.as_dict() if hasattr(r, "as_dict") else {"ok": False, "text": str(r)}
        rec = {
            "i": i,
            "tag": tag,
            "ok": bool(d.get("ok", True)),
            "text": (d.get("text") or "")[:800],
            "reward": 0.7 if d.get("ok") and (d.get("text") or "").strip() else 0.2,
        }
        receipts.append(rec)
        if rec["reward"] >= float(best.get("reward") or -1):
            best = rec
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": True,
        "schema": SCHEMA,
        "via": "pocket.internal.auro",
        "native": False,
        "goal": (goal or "")[:400],
        "experiments": experiments,
        "endure_cycles": cycles,
        "best": best,
        "receipts": receipts,
        "ms": int((time.time() - t0) * 1000),
    }
    (OUT / "LAST.json").write_text(json.dumps(payload, indent=2, default=str)[:80_000], encoding="utf-8")
    payload["summary"] = (
        f"Auro Endure (internal): {experiments} experiments + {cycles} endure cycles. "
        f"Best reward {best.get('reward')} on {best.get('tag')} #{best.get('i')}."
    )
    return payload


def run(goal: str, *, experiments: int = 4, cycles: int = 6) -> Dict[str, Any]:
    g = (goal or "").strip() or "Keep a useful experiment alive and write a receipt."
    try:
        r = _native(g, experiments=experiments, cycles=cycles)
        r.setdefault("schema", SCHEMA)
        r.setdefault("ok", True)
        return r
    except Exception as e:
        r = _fallback(g, experiments=experiments, cycles=cycles)
        r["native_error"] = str(e)[:240]
        return r
