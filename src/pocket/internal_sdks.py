"""Re-export lab internal SDKs when the OneDrive pack is installed."""

from __future__ import annotations

import sys
from pathlib import Path

_PACK = Path.home() / "OneDrive" / "internal-sdks"
if _PACK.is_dir() and str(_PACK) not in sys.path:
    sys.path.insert(0, str(_PACK))

try:
    from itsnotai_internal import catalog, ping_all
    from itsnotai_internal.bus import catalog as sdk_catalog
except Exception:  # pack not on path yet
    def catalog():
        return {"ok": False, "error": "itsnotai_internal not installed", "hint": "pip install -e OneDrive/internal-sdks"}

    def ping_all():
        return catalog()

    sdk_catalog = catalog

__all__ = ["catalog", "ping_all", "sdk_catalog"]
