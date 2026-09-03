"""Device pair codes — work on Pocket from any network after pairing at home.

WebAuthn Face ID is bound to a hostname. A Cloudflare tunnel host is not
the LAN IP and not always medinatechlabs.net. A 6-digit code minted on
this PC lets the same phone mint a session + Portal cookie on the tunnel.
"""

from __future__ import annotations

import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path.home() / ".pocket" / "device_pair"
FILE = ROOT / "code.json"
TTL = 600


def mint(*, client_ip: str = "") -> Dict[str, Any]:
    ip = (client_ip or "").strip()
    if ip not in ("127.0.0.1", "::1", "localhost") and not ip.startswith("192.168.") and not ip.startswith("10."):
        return {"ok": False, "error": "mint the pair code on this PC or home Wi-Fi"}
    code = f"{secrets.randbelow(1_000_000):06d}"
    rec = {"code": code, "exp": time.time() + TTL, "at": time.time()}
    ROOT.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(rec), encoding="utf-8")
    note = ROOT / "PAIR.txt"
    note.write_text(
        f"POCKET pair code (10 minutes)\n{code}\n\n"
        "On the phone (any network / tunnel): Portal → Pair code → enter this.\n",
        encoding="utf-8",
    )
    return {"ok": True, "code": code, "expires_sec": TTL, "file": str(note)}


def redeem(code: str) -> Dict[str, Any]:
    from pocket.users import issue_token

    raw = "".join(ch for ch in (code or "") if ch.isdigit())
    if len(raw) != 6:
        return {"ok": False, "error": "enter the 6-digit code from the PC"}
    if not FILE.is_file():
        return {"ok": False, "error": "no code — open Portal on the PC or home Wi-Fi first"}
    try:
        rec = json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": False, "error": "code unreadable"}
    if time.time() > float(rec.get("exp") or 0):
        return {"ok": False, "error": "code expired — mint a new one on the PC"}
    if raw != str(rec.get("code") or ""):
        return {"ok": False, "error": "wrong code"}
    try:
        FILE.unlink()
    except Exception:
        pass
    tok = issue_token("pocket")
    return {"ok": True, "token": tok, "user": "pocket", "via": "device-pair"}
