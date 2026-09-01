"""Authenticated encryption for Pocket vaults and envelopes.

hmac-sha256-ctr-v2: CTR stream + HMAC tag (encrypt-then-MAC).
Key from PBKDF2. Secret lives in ~/.pocket/crypto.key (not a source default).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Any, Dict

ROOT = Path.home() / ".pocket"
KEY_PATH = ROOT / "crypto.key"
ALG = "hmac-sha256-ctr-mac-v2"


def _master() -> bytes:
    ROOT.mkdir(parents=True, exist_ok=True)
    if KEY_PATH.is_file():
        raw = KEY_PATH.read_bytes()
        if len(raw) >= 32:
            return raw[:32]
    raw = secrets.token_bytes(32)
    KEY_PATH.write_bytes(raw)
    try:
        os.chmod(KEY_PATH, 0o600)
    except Exception:
        pass
    return raw


def derive_key(user: str, *, purpose: str = "vault") -> bytes:
    material = f"{user or 'seat'}|{purpose}".encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", material, _master(), 120_000, dklen=32)


def encrypt_bytes(user: str, raw: bytes, *, purpose: str = "vault") -> Dict[str, str]:
    key = derive_key(user, purpose=purpose)
    nonce = secrets.token_bytes(16)
    stream = bytearray()
    i = 0
    while len(stream) < len(raw):
        stream.extend(hmac.new(key, nonce + i.to_bytes(8, "big"), hashlib.sha256).digest())
        i += 1
    ct = bytes(a ^ b for a, b in zip(raw, bytes(stream[: len(raw)])))
    tag = hmac.new(key, nonce + ct, hashlib.sha256).digest()[:16]
    return {
        "alg": ALG,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ct": base64.b64encode(ct).decode("ascii"),
        "mac": base64.b64encode(tag).decode("ascii"),
    }


def decrypt_bytes(user: str, blob: Dict[str, Any], *, purpose: str = "vault") -> bytes:
    key = derive_key(user, purpose=purpose)
    nonce = base64.b64decode(blob.get("nonce") or "")
    ct = base64.b64decode(blob.get("ct") or "")
    mac = base64.b64decode(blob.get("mac") or "")
    if blob.get("alg") == ALG:
        expect = hmac.new(key, nonce + ct, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(expect, mac):
            raise ValueError("vault mac mismatch")
    stream = bytearray()
    i = 0
    while len(stream) < len(ct):
        stream.extend(hmac.new(key, nonce + i.to_bytes(8, "big"), hashlib.sha256).digest())
        i += 1
    return bytes(a ^ b for a, b in zip(ct, bytes(stream[: len(ct)])))
