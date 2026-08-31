"""Ghost math agents — pure deterministic compute, zero LLM tokens.

Offload "guessing" to actual math: hashes, checksums, rolling stats, phi-ish scales.
"""

from __future__ import annotations

import hashlib
import math
import statistics
import time
from typing import Any, Dict, List, Sequence, Tuple


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def chain_hash(parts: Sequence[str]) -> Dict[str, Any]:
    """Hash-chain like receipt roots — mathematical, not guessed."""
    prev = "0" * 64
    links = []
    for i, p in enumerate(parts):
        payload = f"{prev}|{i}|{p}"
        h = sha256_hex(payload)
        links.append({"i": i, "prev": prev[:16], "hash": h, "snip": str(p)[:80]})
        prev = h
    return {"ok": True, "root": prev, "n": len(links), "links": links, "agent": "GHOST_MATH"}


def series_stats(nums: List[float]) -> Dict[str, Any]:
    if not nums:
        return {"ok": False, "error": "empty series"}
    return {
        "ok": True,
        "n": len(nums),
        "mean": statistics.fmean(nums),
        "stdev": statistics.pstdev(nums) if len(nums) > 1 else 0.0,
        "min": min(nums),
        "max": max(nums),
        "sum": sum(nums),
        "agent": "GHOST_MATH",
    }


def phi_scale(x: float) -> Dict[str, Any]:
    phi = (1 + math.sqrt(5)) / 2
    return {
        "ok": True,
        "x": x,
        "phi": phi,
        "x_over_phi": x / phi,
        "x_times_phi": x * phi,
        "nearest_fib_approx": round(x * phi),
        "agent": "GHOST_MATH",
    }


def gcd_pair(a: int, b: int) -> Dict[str, Any]:
    x, y = abs(int(a)), abs(int(b))
    while y:
        x, y = y, x % y
    return {"ok": True, "a": a, "b": b, "gcd": x, "agent": "GHOST_MATH"}


def is_prime(n: int) -> Dict[str, Any]:
    n = int(n)
    if n < 2:
        return {"ok": True, "n": n, "prime": False, "agent": "GHOST_MATH"}
    if n in (2, 3):
        return {"ok": True, "n": n, "prime": True, "agent": "GHOST_MATH"}
    if n % 2 == 0:
        return {"ok": True, "n": n, "prime": False, "agent": "GHOST_MATH"}
    i = 3
    while i * i <= n:
        if n % i == 0:
            return {"ok": True, "n": n, "prime": False, "divides": i, "agent": "GHOST_MATH"}
        i += 2
    return {"ok": True, "n": n, "prime": True, "agent": "GHOST_MATH"}


def run_ghost(prompt: str) -> Tuple[str, str, str]:
    """Deterministic router for math tasks."""
    import re

    low = (prompt or "").lower()
    if "chain" in low or "hash" in low:
        parts = [p.strip() for p in (prompt or "").split("|") if p.strip()] or ["a", "b", "c"]
        r = chain_hash(parts[:32])
        body = f"## Ghost hash chain\n\n**root:** `{r['root']}`\n**links:** {r['n']}\n"
        return body, "", "ghost-math"
    if "phi" in low or "golden" in low:
        m = re.search(r"[-+]?\d*\.?\d+", prompt or "")
        x = float(m.group(0)) if m else 1.0
        r = phi_scale(x)
        return f"## Phi scale\n\n```json\n{r}\n```\n", "", "ghost-math"
    if "gcd" in low or "greatest common" in low:
        nums = [int(x) for x in re.findall(r"-?\d+", prompt or "")][:2]
        if len(nums) < 2:
            nums = [12, 18]
        r = gcd_pair(nums[0], nums[1])
        return f"## GCD (internal)\n\n`gcd({r['a']},{r['b']}) = {r['gcd']}`\n", "", "ghost-math"
    if "prime" in low:
        m = re.search(r"-?\d+", prompt or "")
        n = int(m.group(0)) if m else 17
        r = is_prime(n)
        return f"## Prime test (internal)\n\n```json\n{r}\n```\n", "", "ghost-math"
    nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", prompt or "")]
    if "mean" in low or "stdev" in low or "stats" in low:
        r = series_stats(nums or [1.0, 2.0, 3.0])
        return f"## Series stats (internal)\n\n```json\n{r}\n```\n", "", "ghost-math"
    h = sha256_hex(prompt or "")
    return f"## Ghost digest\n\n`sha256` = `{h}`\n\n_No LLM — pure internal math._\n", "", "ghost-math"
