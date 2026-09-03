"""Away-from-home device pair: code + WebAuthn → revocable device capability.

A 6-digit LAN code is not a founder credential. Redeem requires a
device-generated WebAuthn key on the exact page origin. The session is
principal `device:<id>` with role `portal_device` (Portal/visual only).
Owner/admin is never minted from the code. Devices are revocable.
"""

from __future__ import annotations

import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path.home() / ".pocket" / "device_pair"
FILE = ROOT / "code.json"
DEVICES = ROOT / "devices.json"
TTL = 600
CAPABILITY = "portal"


def _load_json(path: Path) -> Dict[str, Any]:
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        import os

        os.chmod(path, 0o600)
    except Exception:
        pass


def mint(*, client_ip: str = "") -> Dict[str, Any]:
    ip = (client_ip or "").strip()
    if ip not in ("127.0.0.1", "::1", "localhost") and not ip.startswith("192.168.") and not ip.startswith("10."):
        return {"ok": False, "error": "mint the pair code on this PC or home Wi-Fi"}
    code = f"{secrets.randbelow(1_000_000):06d}"
    rec = {"code": code, "exp": time.time() + TTL, "at": time.time(), "used": False}
    _save_json(FILE, rec)
    note = ROOT / "PAIR.txt"
    note.write_text(
        f"POCKET pair code (10 minutes)\n{code}\n\n"
        "On the phone (named tunnel / exact origin): Portal → Pair → enter this,\n"
        "then complete Face ID / passkey on THIS phone. Code alone does nothing.\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "code": code,
        "expires_sec": TTL,
        "file": str(note),
        "need": "webauthn",
        "hint": "Phone must create a passkey on the exact origin after entering this code.",
    }


def begin(*, host: str) -> Dict[str, Any]:
    """WebAuthn create options for this phone. rpId is the exact host."""
    from pocket.passkey import begin_register

    if not FILE.is_file():
        return {"ok": False, "error": "no code — mint on the PC first"}
    rec = _load_json(FILE)
    if time.time() > float(rec.get("exp") or 0):
        return {"ok": False, "error": "code expired — mint a new one on the PC"}
    device_name = "phone-" + secrets.token_hex(4)
    opts = begin_register(host=host, user=device_name)
    opts["need"] = "webauthn.create"
    opts["principal_hint"] = "device"
    opts["user"] = device_name
    return opts


def _check_code(code: str, *, consume: bool) -> Dict[str, Any]:
    raw = "".join(ch for ch in (code or "") if ch.isdigit())
    if len(raw) != 6:
        return {"ok": False, "error": "enter the 6-digit code from the PC"}
    if not FILE.is_file():
        return {"ok": False, "error": "no code — open Portal on the PC or home Wi-Fi first"}
    rec = _load_json(FILE)
    if time.time() > float(rec.get("exp") or 0):
        return {"ok": False, "error": "code expired — mint a new one on the PC"}
    if raw != str(rec.get("code") or ""):
        return {"ok": False, "error": "wrong code"}
    if rec.get("used"):
        return {"ok": False, "error": "code already used"}
    if consume:
        rec["used"] = True
        _save_json(FILE, rec)
        try:
            FILE.unlink()
        except Exception:
            pass
    return {"ok": True, "code": raw}


def _store_device(rec: Dict[str, Any]) -> Dict[str, Any]:
    blob = _load_json(DEVICES)
    lst = blob.get("devices") or []
    lst = [d for d in lst if d.get("id") != rec["id"] and d.get("cred_id") != rec.get("cred_id")]
    lst.append(rec)
    blob["devices"] = lst[-32:]
    _save_json(DEVICES, blob)
    return rec


def list_devices() -> Dict[str, Any]:
    blob = _load_json(DEVICES)
    rows = []
    for d in blob.get("devices") or []:
        rows.append(
            {
                "id": d.get("id"),
                "principal": d.get("principal"),
                "rp_id": d.get("rp_id"),
                "origin": d.get("origin"),
                "revoked": bool(d.get("revoked")),
                "at": d.get("at"),
                "capability": d.get("capability") or CAPABILITY,
            }
        )
    return {"ok": True, "devices": rows, "count": len(rows)}


def revoke(device_id: str) -> Dict[str, Any]:
    did = (device_id or "").strip()
    blob = _load_json(DEVICES)
    found = False
    for d in blob.get("devices") or []:
        if d.get("id") == did or d.get("principal") == did:
            d["revoked"] = True
            d["revoked_at"] = time.time()
            found = True
            try:
                from pocket.users import revoke_all_for_user

                revoke_all_for_user(str(d.get("principal") or ""))
            except Exception:
                pass
    if found:
        _save_json(DEVICES, blob)
    return {"ok": found, "id": did, "revoked": found}


def device_live(principal: str) -> bool:
    p = (principal or "").strip()
    for d in (_load_json(DEVICES).get("devices") or []):
        if str(d.get("principal") or "") == p or str(d.get("id") or "") == p:
            return not bool(d.get("revoked"))
    return False


def _issue_capability(device: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.phoneai_portal import mint_portal_token
    from pocket.users import issue_token
    from pocket.work_grant import issue as grant_issue

    principal = str(device["principal"])
    tok = issue_token(
        principal,
        role="portal_device",
        is_owner=False,
        device_id=str(device["id"]),
        capability=CAPABILITY,
    )
    portal = mint_portal_token(principal)
    grant = grant_issue(
        principal=principal,
        tenant="phoneai-device",
        capability=CAPABILITY,
        tools=["portal", "observe", "input"],
        deadline_s=86400 * 14,
        idempotency_key="device-" + str(device["id"]),
    )
    return {
        "ok": True,
        "token": tok,
        "portal": portal,
        "user": principal,
        "role": "portal_device",
        "is_owner": False,
        "device_id": device["id"],
        "capability": CAPABILITY,
        "grant_id": grant.get("id"),
        "via": "device-pair+webauthn",
    }


def redeem(
    code: str,
    *,
    credential: Optional[Dict[str, Any]] = None,
    host: str = "",
    origin: str = "",
) -> Dict[str, Any]:
    from pocket.origin_policy import origin_allowed
    from pocket.passkey import verify_create

    if not credential:
        return {
            "ok": False,
            "error": "pair requires the 6-digit code AND a passkey from this phone",
            "need": "webauthn",
        }
    if host and origin and not origin_allowed(origin, host):
        return {"ok": False, "error": "origin not exact — use the configured public host, not a sibling subdomain"}
    peeked = _check_code(code, consume=False)
    if not peeked.get("ok"):
        return peeked
    attested = verify_create({"credential": credential}, host=host, user="device")
    if not attested.get("ok"):
        return {"ok": False, "error": attested.get("error") or "passkey failed", "need": "webauthn"}
    consumed = _check_code(code, consume=True)
    if not consumed.get("ok"):
        return consumed
    did = "dev_" + secrets.token_hex(8)
    principal = "device:" + did
    rec = {
        "id": did,
        "principal": principal,
        "cred_id": attested.get("cred_id"),
        "rp_id": attested.get("rp_id"),
        "origin": origin or attested.get("origin") or "",
        "capability": CAPABILITY,
        "role": "portal_device",
        "revoked": False,
        "at": time.time(),
        "grant_via": "local-workgrant",
    }
    _store_device(rec)
    out = _issue_capability(rec)
    out["device"] = {"id": did, "principal": principal, "capability": CAPABILITY}
    return out
