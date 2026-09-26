"""Pocket Names — you own the root; people claim handles (me.me style).

Not a GoDaddy cart per user. Zones you operate: toolbox, toolset, aiapps, pocketweb.
Public DNS later = one parent you control (Cloudflare / Handshake). Until then the
registry is local and Pocket-issued.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path.home() / ".pocket"
REG = ROOT / "names.json"
SCHEMA = "pocket.names.v1"
ZONES = ("toolbox", "toolset", "aiapps", "pocketweb")
_NAME = re.compile(r"^[a-z][a-z0-9-]{0,31}$")


def _load() -> Dict[str, Any]:
    if REG.is_file():
        try:
            return json.loads(REG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "zones": {z: {} for z in ZONES}}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(data, indent=2), encoding="utf-8")


def status() -> Dict[str, Any]:
    data = _load()
    counts = {z: len(data.get("zones", {}).get(z) or {}) for z in ZONES}
    return {
        "ok": True,
        "schema": SCHEMA,
        "product": "Pocket Names",
        "ui": "/names",
        "zones": list(ZONES),
        "counts": counts,
        "model": "You own the root. People claim name.zone — they do not buy a domain.",
        "fqdn_examples": ["you.toolbox", "lab.aiapps", "desk.pocketweb"],
        "public_dns": "Point one real parent (or Handshake TLD) at Pocket; until then names are Pocket-issued.",
    }


def list_names(zone: str = "") -> Dict[str, Any]:
    data = _load()
    if zone:
        z = zone.strip().lower()
        return {"ok": z in ZONES, "zone": z, "names": data.get("zones", {}).get(z) or {}}
    return {"ok": True, "zones": data.get("zones") or {}}


def claim(name: str, zone: str, *, owner: str = "pocket") -> Dict[str, Any]:
    n = (name or "").strip().lower()
    z = (zone or "").strip().lower()
    if z not in ZONES:
        return {"ok": False, "error": f"zone must be one of {', '.join(ZONES)}"}
    if not _NAME.match(n) or n in ("www", "mail", "ns", "api"):
        return {"ok": False, "error": "name: start with a letter, 1–32 chars, no www/mail/ns/api"}
    data = _load()
    bucket = data.setdefault("zones", {}).setdefault(z, {})
    if n in bucket:
        return {"ok": False, "error": f"{n}.{z} already claimed", "record": bucket[n]}
    rec = {
        "name": n,
        "zone": z,
        "fqdn": f"{n}.{z}",
        "owner": (owner or "pocket").strip().lower(),
        "created_at": time.time(),
        "kind": "handle",
    }
    bucket[n] = rec
    _save(data)
    return {"ok": True, "claimed": rec, "note": f"{n}.{z} is yours on Pocket Names"}
