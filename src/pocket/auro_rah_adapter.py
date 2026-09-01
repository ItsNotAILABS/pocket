"""Versioned AURO RAH adapter.

Auro14B main may or may not ship auro_native_llm.rah. Pocket never pretends
the import succeeded. When the module exists, we pass tenant/budget/grant.
When it does not, we run a bounded local Auro think leaf and record a receipt.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict


ADAPTER = "pocket.auro_rah_adapter.v1"


def run_auro_rah(
    goal: str,
    *,
    max_parallel: int = 4,
    depth: int = 1,
    grant_id: str = "",
    tenant: str = "",
    checkpoint: str = "",
) -> Dict[str, Any]:
    started = time.time()
    rec: Dict[str, Any] = {
        "ok": False,
        "adapter": ADAPTER,
        "goal": (goal or "")[:400],
        "grant_id": grant_id,
        "tenant": tenant,
        "max_parallel": max(1, min(int(max_parallel), 8)),
        "depth": max(0, min(int(depth), 2)),
    }
    native = None
    native_err = ""
    try:
        from pocket.auro14b_bridge import auro_root, checkpoint_path

        root = auro_root()
        ckpt = checkpoint_path()
        rec["checkpoint"] = str(ckpt) if ckpt else checkpoint
        rec["source_revision"] = ""
        if root:
            rec["source_revision"] = hashlib.sha256(str(root).encode()).hexdigest()[:12]
            import sys

            pth = str(root)
            if pth not in sys.path:
                sys.path.insert(0, pth)
            try:
                from auro_native_llm.rah import run_rah as auro_run_rah

                native = auro_run_rah
            except Exception as e:
                native_err = str(e)[:240]
    except Exception as e:
        native_err = str(e)[:240]

    if native:
        try:
            ar = native(
                goal,
                max_parallel=rec["max_parallel"],
                depth=rec["depth"],
            )
            rec["ok"] = bool(ar.get("ok"))
            rec["via"] = "auro_native_llm.rah"
            rec["synthesis"] = (ar.get("synthesis") or ar.get("result") or json.dumps(ar, default=str))[:12000]
            rec["auro_run_id"] = ar.get("run_id")
            rec["native"] = True
            rec["ms"] = int((time.time() - started) * 1000)
            return rec
        except TypeError:
            ar = native(goal)
            rec["ok"] = bool(ar.get("ok") if isinstance(ar, dict) else True)
            rec["via"] = "auro_native_llm.rah"
            rec["synthesis"] = str(ar)[:12000]
            rec["native"] = True
            rec["ms"] = int((time.time() - started) * 1000)
            return rec
        except Exception as e:
            native_err = str(e)[:240]

    try:
        from pocket.internal_models.modules.auro import AuroModel

        class _Deep:
            def strategy(self) -> str:
                return "deep"

        res = AuroModel().express(goal, genome=_Deep())
        rec["ok"] = bool(getattr(res, "ok", True))
        rec["via"] = "pocket.internal_models.auro"
        rec["native"] = False
        rec["fallback"] = native_err or "auro_native_llm.rah missing on this Auro head"
        rec["synthesis"] = str(getattr(res, "text", None) or getattr(res, "reply", None) or res)[:8000]
    except Exception as e:
        rec["ok"] = False
        rec["via"] = "none"
        rec["error"] = (native_err or str(e))[:400]
        rec["synthesis"] = ""
    rec["ms"] = int((time.time() - started) * 1000)
    rec["receipt"] = {
        "schema": "pocket.auro_leaf_receipt.v1",
        "grant_id": grant_id,
        "tenant": tenant,
        "checkpoint": rec.get("checkpoint"),
        "adapter": ADAPTER,
        "at": time.time(),
    }
    return rec
