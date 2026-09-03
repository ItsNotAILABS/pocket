"""Homogeneous 3×3 maps for Portal contain/cover — same math on phone and host.

Touch is a matrix multiply, not a CSS guess. MESIE-style affine: column vector
[nx, ny, 1] through M → desktop pixels. No extra round-trips.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

Matrix = List[List[float]]


def mul(m: Sequence[Sequence[float]], nx: float, ny: float) -> Tuple[float, float]:
    x = float(m[0][0]) * nx + float(m[0][1]) * ny + float(m[0][2])
    y = float(m[1][0]) * nx + float(m[1][1]) * ny + float(m[1][2])
    return x, y


def identity() -> Matrix:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def desktop_from_unit(geom: Dict[str, Any]) -> Matrix:
    """nx,ny in [0,1] of the streamed rectangle → desktop pixels."""
    x = float(geom.get("x") or 0)
    y = float(geom.get("y") or 0)
    w = float(geom.get("w") or 1)
    h = float(geom.get("h") or 1)
    return [[w, 0.0, x], [0.0, h, y], [0.0, 0.0, 1.0]]


def apply_int(m: Sequence[Sequence[float]], nx: float, ny: float) -> Tuple[int, int]:
    nx = 0.0 if nx < 0 else 1.0 if nx > 1 else float(nx)
    ny = 0.0 if ny < 0 else 1.0 if ny > 1 else float(ny)
    x, y = mul(m, nx, ny)
    return int(x), int(y)


def snapshot(geom: Dict[str, Any]) -> Dict[str, Any]:
    m = desktop_from_unit(geom)
    return {
        "ok": True,
        "schema": "pocket.screen.matrix.v1",
        "matrix": m,
        "geom": {
            "x": int(geom.get("x") or 0),
            "y": int(geom.get("y") or 0),
            "w": int(geom.get("w") or 0),
            "h": int(geom.get("h") or 0),
        },
        "note": "Phone nx,ny of the contained image × M = desktop pixel. Same contract as SCREEN-KERNEL.",
    }
