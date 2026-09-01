"""Phone Face ID / Touch ID via WebAuthn — no password dialog.

LAN: Portal works immediately; first visit can save this phone.
Tunnel: Unlock with Face ID (assertion). New phones pair only during an
owner-presence window (open Portal on the PC / home Wi-Fi, or POST allow).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import struct
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

ROOT = Path.home() / ".pocket" / "webauthn"
CREDS = ROOT / "credentials.json"
CHALS = ROOT / "challenges.json"
PAIR = ROOT / "pair.json"
COOKIE = "pocket_passkey"

_CHAL_TTL = 120
_PAIR_TTL = 600
_TOKEN_TTL = 86400 * 14


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    s = (raw or "").strip()
    s += "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s.encode("ascii"))


def _load(path: Path) -> Dict[str, Any]:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(path: Path, data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def _cbor(buf: bytes, i: int = 0) -> Tuple[Any, int]:
    if i >= len(buf):
        raise ValueError("cbor eof")
    b = buf[i]
    i += 1
    mt, ai = b >> 5, b & 31

    def uint(n: int, j: int) -> Tuple[int, int]:
        if n == 24:
            return buf[j], j + 1
        if n == 25:
            return int.from_bytes(buf[j : j + 2], "big"), j + 2
        if n == 26:
            return int.from_bytes(buf[j : j + 4], "big"), j + 4
        if n == 27:
            return int.from_bytes(buf[j : j + 8], "big"), j + 8
        if n < 24:
            return n, j
        raise ValueError("cbor int")

    if mt == 0:
        v, i = uint(ai, i)
        return v, i
    if mt == 1:
        v, i = uint(ai, i)
        return -1 - v, i
    if mt in (2, 3):
        n, i = uint(ai, i)
        chunk = buf[i : i + n]
        i += n
        return (chunk if mt == 2 else chunk.decode("utf-8")), i
    if mt == 4:
        n, i = uint(ai, i)
        arr = []
        for _ in range(n):
            x, i = _cbor(buf, i)
            arr.append(x)
        return arr, i
    if mt == 5:
        n, i = uint(ai, i)
        m: Dict[Any, Any] = {}
        for _ in range(n):
            k, i = _cbor(buf, i)
            v, i = _cbor(buf, i)
            m[k] = v
        return m, i
    if mt == 6:
        _, i = uint(ai, i)
        v, i = _cbor(buf, i)
        return v, i
    if mt == 7:
        if ai == 20:
            return False, i
        if ai == 21:
            return True, i
        if ai == 22:
            return None, i
    raise ValueError("cbor major")


def rp_id_from_host(host: str) -> str:
    h = (host or "").split(":")[0].strip().lower()
    return h or "localhost"


def origin_allowed(origin: str, host: str) -> bool:
    o = (origin or "").strip()
    if not o:
        return False
    oh = (urlparse(o).hostname or "").lower()
    hh = rp_id_from_host(host)
    if oh == hh:
        return True
    if oh in ("127.0.0.1", "localhost"):
        return True
    if oh.startswith("192.168.") or oh.startswith("10."):
        return True
    pub = os.environ.get("POCKET_PUBLIC_URL") or "https://pocket.medinatechlabs.net"
    ph = (urlparse(pub).hostname or "").lower()
    if ph and oh == ph:
        return True
    if oh.endswith(".medinatechlabs.net") or oh.endswith(".trycloudflare.com"):
        return True
    return False


def _put_challenge(kind: str, rp_id: str) -> str:
    chal = secrets.token_urlsafe(32)
    data = _load(CHALS)
    data[chal] = {"kind": kind, "rp_id": rp_id, "at": time.time()}
    cut = time.time() - _CHAL_TTL
    data = {k: v for k, v in data.items() if (v.get("at") or 0) > cut}
    _save(CHALS, data)
    return chal


def _take_challenge(chal: str, kind: str, rp_id: str) -> bool:
    data = _load(CHALS)
    rec = data.pop(chal, None)
    _save(CHALS, data)
    if not rec:
        return False
    if rec.get("kind") != kind:
        return False
    if rec.get("rp_id") != rp_id:
        return False
    if time.time() - float(rec.get("at") or 0) > _CHAL_TTL:
        return False
    return True


def pairing_open(*, minutes: float = 10) -> Dict[str, Any]:
    until = time.time() + max(60, minutes * 60)
    _save(PAIR, {"until": until, "at": time.time()})
    return {"ok": True, "until": until, "seconds": int(until - time.time())}


def pairing_active() -> bool:
    rec = _load(PAIR)
    return float(rec.get("until") or 0) > time.time()


def can_register(*, lan: bool, authed: bool) -> bool:
    return bool(lan or authed or pairing_active())


def begin_register(*, host: str, user: str = "") -> Dict[str, Any]:
    from pocket.auth import expected_user

    rp_id = rp_id_from_host(host)
    chal = _put_challenge("create", rp_id)
    uid = (user or expected_user() or "pocket").encode("utf-8")[:64]
    return {
        "ok": True,
        "publicKey": {
            "challenge": chal,
            "rp": {"name": "POCKET PhoneAI", "id": rp_id},
            "user": {
                "id": _b64url(uid),
                "name": (user or expected_user() or "pocket"),
                "displayName": "PhoneAI on this phone",
            },
            "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
            "timeout": 60000,
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "preferred",
                "requireResidentKey": False,
            },
            "attestation": "none",
        },
    }


def begin_login(*, host: str) -> Dict[str, Any]:
    rp_id = rp_id_from_host(host)
    chal = _put_challenge("get", rp_id)
    creds = _load(CREDS).get("credentials") or []
    allow = [{"type": "public-key", "id": c["id"]} for c in creds if c.get("id")]
    return {
        "ok": True,
        "paired": bool(allow),
        "publicKey": {
            "challenge": chal,
            "rpId": rp_id,
            "timeout": 60000,
            "userVerification": "required",
            "allowCredentials": allow,
        },
    }


def _parse_auth_data(raw: bytes) -> Dict[str, Any]:
    if len(raw) < 37:
        raise ValueError("authData short")
    flags = raw[32]
    out: Dict[str, Any] = {
        "rpIdHash": raw[:32],
        "flags": flags,
        "signCount": int.from_bytes(raw[33:37], "big"),
        "userPresent": bool(flags & 0x01),
        "userVerified": bool(flags & 0x04),
        "attested": bool(flags & 0x40),
    }
    if out["attested"]:
        if len(raw) < 55:
            raise ValueError("attested short")
        L = int.from_bytes(raw[53:55], "big")
        cred_id = raw[55 : 55 + L]
        cose, _ = _cbor(raw, 55 + L)
        x = cose.get(-2)
        y = cose.get(-3)
        if not isinstance(x, (bytes, bytearray)) or not isinstance(y, (bytes, bytearray)):
            raise ValueError("cose xy")
        out["cred_id"] = bytes(cred_id)
        out["x"] = bytes(x)
        out["y"] = bytes(y)
    return out


def _verify_origin_challenge(client_data_json: bytes, *, kind: str, chal: str, host: str) -> Dict[str, Any]:
    data = json.loads(client_data_json.decode("utf-8"))
    if data.get("type") != kind:
        raise ValueError("clientData type")
    got = data.get("challenge") or ""
    if got != chal and _b64url(_b64url_decode(got) if False else b"") != chal:
        # browsers send challenge as base64url of the raw challenge string we issued as JSON string
        try:
            decoded = _b64url_decode(got).decode("utf-8")
        except Exception:
            decoded = ""
        if got != chal and decoded != chal:
            # also accept raw bytes of chal
            if _b64url(chal.encode("utf-8")) != got and chal != got:
                raise ValueError("challenge")
    origin = str(data.get("origin") or "")
    if not origin_allowed(origin, host):
        raise ValueError("origin")
    return data


def _ecdsa_verify(x: bytes, y: bytes, message: bytes, signature: bytes) -> bool:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
    from cryptography.hazmat.primitives import hashes
    from cryptography.exceptions import InvalidSignature

    if len(signature) != 64:
        # DER or concat; try raw 64
        if len(signature) > 64:
            # likely DER — cryptography can load
            sig = signature
            numbers = ec.EllipticCurvePublicNumbers(
                int.from_bytes(x, "big"), int.from_bytes(y, "big"), ec.SECP256R1()
            )
            key = numbers.public_key()
            try:
                key.verify(sig, message, ec.ECDSA(hashes.SHA256()))
                return True
            except InvalidSignature:
                return False
        return False
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:], "big")
    der = encode_dss_signature(r, s)
    numbers = ec.EllipticCurvePublicNumbers(
        int.from_bytes(x, "big"), int.from_bytes(y, "big"), ec.SECP256R1()
    )
    key = numbers.public_key()
    try:
        key.verify(der, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


def finish_register(body: Dict[str, Any], *, host: str, user: str = "") -> Dict[str, Any]:
    from pocket.auth import expected_user
    from pocket.users import issue_token

    rp_id = rp_id_from_host(host)
    cred = body.get("credential") or body
    raw_id = str(cred.get("id") or cred.get("rawId") or "")
    resp = cred.get("response") or {}
    cjson = _b64url_decode(str(resp.get("clientDataJSON") or ""))
    att = _b64url_decode(str(resp.get("attestationObject") or ""))
    client = json.loads(cjson.decode("utf-8"))
    chal = str(client.get("challenge") or "")
    try:
        chal_plain = _b64url_decode(chal).decode("utf-8")
    except Exception:
        chal_plain = chal
    if not _take_challenge(chal_plain, "create", rp_id) and not _take_challenge(chal, "create", rp_id):
        return {"ok": False, "error": "challenge expired — tap Face ID again"}
    if client.get("type") != "webauthn.create":
        return {"ok": False, "error": "clientData"}
    if not origin_allowed(str(client.get("origin") or ""), host):
        return {"ok": False, "error": "origin"}
    att_map, _ = _cbor(att, 0)
    auth_raw = att_map.get("authData")
    if not isinstance(auth_raw, (bytes, bytearray)):
        return {"ok": False, "error": "attestation"}
    parsed = _parse_auth_data(bytes(auth_raw))
    if not parsed.get("userVerified"):
        return {"ok": False, "error": "Face ID required"}
    if hashlib.sha256(rp_id.encode("utf-8")).digest() != parsed["rpIdHash"]:
        return {"ok": False, "error": "rpId"}
    creds = _load(CREDS)
    lst = creds.setdefault("credentials", [])
    rec = {
        "id": raw_id or _b64url(parsed["cred_id"]),
        "x": _b64url(parsed["x"]),
        "y": _b64url(parsed["y"]),
        "signCount": parsed["signCount"],
        "user": user or expected_user() or "pocket",
        "at": time.time(),
        "rp_id": rp_id,
    }
    lst = [c for c in lst if c.get("id") != rec["id"]]
    lst.append(rec)
    creds["credentials"] = lst[-16:]
    _save(CREDS, creds)
    tok = issue_token(rec["user"])
    return {"ok": True, "token": tok, "user": rec["user"], "face": True, "registered": True}


def finish_login(body: Dict[str, Any], *, host: str) -> Dict[str, Any]:
    from pocket.users import issue_token

    rp_id = rp_id_from_host(host)
    cred = body.get("credential") or body
    raw_id = str(cred.get("id") or cred.get("rawId") or "")
    resp = cred.get("response") or {}
    cjson = _b64url_decode(str(resp.get("clientDataJSON") or ""))
    ad = _b64url_decode(str(resp.get("authenticatorData") or ""))
    sig = _b64url_decode(str(resp.get("signature") or ""))
    client = json.loads(cjson.decode("utf-8"))
    chal = str(client.get("challenge") or "")
    try:
        chal_plain = _b64url_decode(chal).decode("utf-8")
    except Exception:
        chal_plain = chal
    if not _take_challenge(chal_plain, "get", rp_id) and not _take_challenge(chal, "get", rp_id):
        return {"ok": False, "error": "challenge expired — Face ID again"}
    origin = str(client.get("origin") or "")
    if not origin_allowed(origin, host):
        return {"ok": False, "error": "origin"}
    if client.get("type") != "webauthn.get":
        return {"ok": False, "error": "clientData"}
    creds = _load(CREDS).get("credentials") or []
    rec = next((c for c in creds if c.get("id") == raw_id), None)
    if not rec:
        return {"ok": False, "error": "this phone is not paired"}
    parsed = _parse_auth_data(ad)
    if not parsed.get("userVerified"):
        return {"ok": False, "error": "Face ID required"}
    if hashlib.sha256(rp_id.encode("utf-8")).digest() != parsed["rpIdHash"]:
        return {"ok": False, "error": "rpId"}
    msg = ad + hashlib.sha256(cjson).digest()
    if not _ecdsa_verify(_b64url_decode(rec["x"]), _b64url_decode(rec["y"]), msg, sig):
        return {"ok": False, "error": "signature"}
    rec["signCount"] = parsed["signCount"]
    rec["last"] = time.time()
    blob = _load(CREDS)
    blob["credentials"] = [rec if c.get("id") == raw_id else c for c in (blob.get("credentials") or [])]
    _save(CREDS, blob)
    tok = issue_token(str(rec.get("user") or "pocket"))
    return {"ok": True, "token": tok, "user": rec.get("user"), "face": True}


def token_from_headers(headers=None) -> str:
    headers = headers or {}
    cookie = headers.get("Cookie") or headers.get("cookie") or ""
    for part in cookie.split(";"):
        k, _, v = part.strip().partition("=")
        if k == COOKIE:
            return v.strip()
    return ""


def session_user(headers=None) -> Optional[str]:
    """Passkey finish stores a normal pocket_session token; also accept pocket_passkey."""
    from pocket.users import user_from_token

    tok = token_from_headers(headers)
    if not tok:
        return None
    rec = user_from_token(tok)
    if rec:
        return str(rec.get("user") or "")
    return None


def snapshot() -> Dict[str, Any]:
    creds = _load(CREDS).get("credentials") or []
    return {
        "ok": True,
        "paired_phones": len(creds),
        "pairing_open": pairing_active(),
        "how": "Face ID on the phone. Pair once on home Wi-Fi or tap Allow on the PC.",
    }
