"""Node-to-node pairing + encrypted local file transfer.

Design:
  - Each POCKET host is a **node** with a durable id + fingerprint (mesh salt).
  - Owner mints short-lived **pair codes** (not the ACCESS password).
  - Paired peers may offer/claim encrypted file packages on a transfer tray.
  - Transport is intentional: no open public file dump. Random visitors cannot
    list or pull trays. Redeem needs the one-time code; pull needs a pair token
    or a logged-in session that owns the offer.

Local-first: packages live under mesh `vdisk/transfers/` (prefer E:) so big files
stay off C: when the mesh root is on a high-capacity volume.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from pocket.mesh_disk import MESH, VDISK, encrypt_body, decrypt_body, sign_payload, verify_payload, agent_sha

ROOT = Path.home() / ".pocket" / "nodes"
ROOT.mkdir(parents=True, exist_ok=True)
IDENTITY_PATH = ROOT / "identity.json"
PEERS_PATH = ROOT / "peers.json"
CODES_PATH = ROOT / "pair_codes.json"
TRAY = VDISK / "transfers"
TRAY.mkdir(parents=True, exist_ok=True)

_lock = Lock()

PAIR_TTL_SEC = 15 * 60  # pair codes live 15 min
OFFER_TTL_SEC = 24 * 3600
MAX_OFFER_BYTES = 32 * 1024 * 1024  # 32 MiB per package (raise via env)


def _max_bytes() -> int:
    try:
        return max(1_000_000, int(os.environ.get("POCKET_NODE_MAX_BYTES") or MAX_OFFER_BYTES))
    except Exception:
        return MAX_OFFER_BYTES


def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def ensure_identity() -> Dict[str, Any]:
    with _lock:
        data = _load_json(IDENTITY_PATH, None)
        if isinstance(data, dict) and data.get("node_id") and data.get("secret"):
            return data
        node_id = "node_" + secrets.token_hex(6)
        secret = secrets.token_urlsafe(32)
        label = (os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or "pocket-host").strip()
        fp = hashlib.sha256((secret + str(MESH)).encode("utf-8")).hexdigest()[:24]
        data = {
            "node_id": node_id,
            "secret": secret,
            "fingerprint": fp,
            "label": label,
            "created_at": time.time(),
            "mesh_root": str(MESH),
        }
        _save_json(IDENTITY_PATH, data)
        return data


def _peer_token(peer_id: str, secret: str) -> str:
    raw = hmac.new(secret.encode("utf-8"), peer_id.encode("utf-8"), hashlib.sha256).digest()
    return "pn_" + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def hello() -> Dict[str, Any]:
    """Public-ish presence (no secrets). Used by redeem handshake."""
    me = ensure_identity()
    return {
        "ok": True,
        "node_id": me["node_id"],
        "fingerprint": me["fingerprint"],
        "label": me.get("label") or "",
        "transfer": "encrypted-tray",
        "pair_ttl_sec": PAIR_TTL_SEC,
        "max_bytes": _max_bytes(),
        "policy": "no anonymous tray access",
    }


def status() -> Dict[str, Any]:
    me = ensure_identity()
    peers = _load_json(PEERS_PATH, {"peers": []})
    codes = _load_json(CODES_PATH, {"codes": []})
    now = time.time()
    live_codes = [c for c in codes.get("codes") or [] if float(c.get("exp") or 0) > now and not c.get("used")]
    offers = []
    for p in sorted(TRAY.glob("*.meta.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:40]:
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            offers.append(
                {
                    "offer_id": meta.get("offer_id"),
                    "name": meta.get("name"),
                    "bytes": meta.get("bytes"),
                    "from_node": meta.get("from_node"),
                    "to_peer": meta.get("to_peer"),
                    "created_at": meta.get("created_at"),
                    "claimed": bool(meta.get("claimed")),
                }
            )
        except Exception:
            continue
    return {
        "ok": True,
        "me": {
            "node_id": me["node_id"],
            "fingerprint": me["fingerprint"],
            "label": me.get("label"),
            "mesh_root": str(MESH),
            "tray": str(TRAY),
        },
        "peers": peers.get("peers") or [],
        "open_pair_codes": len(live_codes),
        "offers": offers,
        "max_bytes": _max_bytes(),
    }


def mint_pair_code(*, label: str = "", ttl_sec: int = PAIR_TTL_SEC) -> Dict[str, Any]:
    """Owner mints a one-time code another device types to pair."""
    me = ensure_identity()
    code = secrets.token_hex(3).upper()  # 6 hex chars
    exp = time.time() + max(60, min(int(ttl_sec or PAIR_TTL_SEC), 3600))
    entry = {
        "code": code,
        "exp": exp,
        "label": (label or "").strip()[:80],
        "created_at": time.time(),
        "used": False,
        "from_node": me["node_id"],
    }
    with _lock:
        data = _load_json(CODES_PATH, {"codes": []})
        codes = [c for c in (data.get("codes") or []) if float(c.get("exp") or 0) > time.time()]
        codes.append(entry)
        data["codes"] = codes[-40:]
        _save_json(CODES_PATH, data)
    return {
        "ok": True,
        "code": code,
        "expires_at": exp,
        "ttl_sec": int(exp - time.time()),
        "node_id": me["node_id"],
        "fingerprint": me["fingerprint"],
        "how": "On the other node: POST /v1/node/redeem {code, label}. Or paste code into Nodes panel.",
    }


def redeem_pair_code(code: str, *, peer_label: str = "", peer_node_id: str = "") -> Dict[str, Any]:
    """Redeem a pair code → peer token (works without owner ACCESS password)."""
    code_n = (code or "").strip().upper().replace(" ", "")
    if not code_n or len(code_n) < 4:
        return {"ok": False, "error": "invalid code"}
    me = ensure_identity()
    now = time.time()
    with _lock:
        data = _load_json(CODES_PATH, {"codes": []})
        codes = data.get("codes") or []
        hit = None
        for c in codes:
            if (c.get("code") or "").upper() == code_n and not c.get("used") and float(c.get("exp") or 0) > now:
                hit = c
                break
        if not hit:
            return {"ok": False, "error": "code expired or unknown"}
        hit["used"] = True
        hit["used_at"] = now
        peer_id = (peer_node_id or "").strip() or ("peer_" + secrets.token_hex(4))
        token = _peer_token(peer_id, me["secret"])
        peers = _load_json(PEERS_PATH, {"peers": []})
        plist = peers.get("peers") or []
        plist = [p for p in plist if p.get("peer_id") != peer_id]
        rec = {
            "peer_id": peer_id,
            "label": (peer_label or hit.get("label") or peer_id)[:80],
            "token_fp": hashlib.sha256(token.encode()).hexdigest()[:16],
            "paired_at": now,
            "via": "pair_code",
            "code_label": hit.get("label") or "",
        }
        plist.append(rec)
        peers["peers"] = plist[-100:]
        _save_json(PEERS_PATH, peers)
        _save_json(CODES_PATH, data)
    return {
        "ok": True,
        "peer_id": peer_id,
        "pair_token": token,
        "host_node_id": me["node_id"],
        "host_fingerprint": me["fingerprint"],
        "host_label": me.get("label"),
        "note": "Store pair_token; send as X-Pocket-Node-Token for transfers",
    }


def verify_pair_token(token: str) -> Optional[Dict[str, Any]]:
    tok = (token or "").strip()
    if not tok.startswith("pn_"):
        return None
    me = ensure_identity()
    peers = (_load_json(PEERS_PATH, {"peers": []}).get("peers") or [])
    for p in peers:
        pid = p.get("peer_id") or ""
        expect = _peer_token(pid, me["secret"])
        if hmac.compare_digest(expect, tok):
            return p
    return None


def pair_seat_login(pair_token: str) -> Dict[str, Any]:
    """One-tap seat unlock for a verified phone peer (no password retype).

    Pair already proved physical/operator intent via desk-minted code.
    Issues a normal user session token for the host owner seat.
    """
    peer = verify_pair_token(pair_token)
    if not peer:
        return {"ok": False, "error": "invalid or expired pair token — pair again from desk"}
    try:
        from pocket.auth import expected_user
        from pocket.users import issue_token, list_users

        user = (expected_user() or "pocket").lower()
        users = {u["user"]: u for u in list_users()}
        role = "admin"
        display = "Phone (paired)"
        if user in users:
            role = users[user].get("role") or "admin"
            display = (users[user].get("display") or display) + " · phone"
        tok = issue_token(user)
        return {
            "ok": True,
            "token": tok,
            "user": {"user": user, "role": role, "display": display, "via": "pair_seat"},
            "peer_id": peer.get("peer_id"),
            "peer_label": peer.get("label"),
            "message": "Seat unlocked from desk pair — agents available",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def offer_file(
    *,
    name: str,
    data: bytes,
    to_peer: str = "",
    from_user: str = "owner",
    note: str = "",
) -> Dict[str, Any]:
    """Encrypt + stage a file for a paired peer (or any paired claimer if to_peer empty)."""
    raw = data or b""
    if len(raw) > _max_bytes():
        return {"ok": False, "error": f"file too large (max {_max_bytes()} bytes)"}
    me = ensure_identity()
    offer_id = uuid.uuid4().hex
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in (name or "file.bin"))[:120]
    # Encrypt as base64 text for existing mesh cipher
    b64 = base64.b64encode(raw).decode("ascii")
    cipher = encrypt_body(b64)
    payload = {
        "offer_id": offer_id,
        "name": safe_name,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "cipher": cipher,
        "from_node": me["node_id"],
        "from_user": from_user,
        "to_peer": (to_peer or "").strip(),
        "note": (note or "")[:500],
        "created_at": time.time(),
        "exp": time.time() + OFFER_TTL_SEC,
        "claimed": False,
    }
    sig = sign_payload({k: v for k, v in payload.items() if k != "hmac_sha256"})
    payload["hmac_sha256"] = sig
    meta_path = TRAY / f"{offer_id}.meta.json"
    blob_path = TRAY / f"{offer_id}.bin.json"
    blob_path.write_text(json.dumps({"cipher": cipher}, indent=2), encoding="utf-8")
    meta_public = {k: v for k, v in payload.items() if k != "cipher"}
    meta_path.write_text(json.dumps(meta_public, indent=2), encoding="utf-8")
    # mesh bus notify
    try:
        from pocket.mesh_disk import send_message

        send_message(
            "TABELLARIUS",
            "USER",
            f"transfer offer {safe_name} ({len(raw)} B) id={offer_id[:12]}",
            channel="freq-0",
            kind="node_transfer",
            encrypt=True,
        )
    except Exception:
        pass
    return {
        "ok": True,
        "offer_id": offer_id,
        "name": safe_name,
        "bytes": len(raw),
        "sha256": payload["sha256"],
        "to_peer": payload["to_peer"] or None,
        "tray": str(TRAY),
    }


def claim_offer(offer_id: str, *, peer: Optional[Dict[str, Any]] = None, as_user: str = "") -> Dict[str, Any]:
    oid = (offer_id or "").strip()
    meta_path = TRAY / f"{oid}.meta.json"
    blob_path = TRAY / f"{oid}.bin.json"
    if not meta_path.is_file() or not blob_path.is_file():
        return {"ok": False, "error": "offer not found"}
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        blob = json.loads(blob_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": f"corrupt offer: {e}"}
    if float(meta.get("exp") or 0) < time.time():
        return {"ok": False, "error": "offer expired"}
    target = (meta.get("to_peer") or "").strip()
    if target and peer and peer.get("peer_id") != target:
        return {"ok": False, "error": "offer reserved for another peer"}
    # logged-in owner can always claim; paired peer if open or matching
    cipher = blob.get("cipher") or {}
    plain_b64 = decrypt_body(cipher)
    try:
        raw = base64.b64decode(plain_b64.encode("ascii"))
    except Exception:
        return {"ok": False, "error": "decrypt failed"}
    expect = meta.get("sha256") or ""
    got = hashlib.sha256(raw).hexdigest()
    if expect and not hmac.compare_digest(expect, got):
        return {"ok": False, "error": "integrity check failed"}
    meta["claimed"] = True
    meta["claimed_at"] = time.time()
    meta["claimed_by"] = (peer or {}).get("peer_id") or as_user or "session"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "offer_id": oid,
        "name": meta.get("name"),
        "bytes": len(raw),
        "sha256": got,
        "data_b64": base64.b64encode(raw).decode("ascii"),
        "note": meta.get("note") or "",
    }


def list_offers(*, include_claimed: bool = False) -> Dict[str, Any]:
    out = []
    for p in sorted(TRAY.glob("*.meta.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:80]:
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            if meta.get("claimed") and not include_claimed:
                continue
            if float(meta.get("exp") or 0) < time.time() and not meta.get("claimed"):
                meta["expired"] = True
            out.append(
                {
                    "offer_id": meta.get("offer_id"),
                    "name": meta.get("name"),
                    "bytes": meta.get("bytes"),
                    "from_node": meta.get("from_node"),
                    "to_peer": meta.get("to_peer"),
                    "created_at": meta.get("created_at"),
                    "claimed": bool(meta.get("claimed")),
                    "expired": bool(meta.get("expired")),
                    "note": meta.get("note") or "",
                }
            )
        except Exception:
            continue
    return {"ok": True, "offers": out, "tray": str(TRAY)}


def drop_local_copy(rel_path: str, *, agent_id: str = "USER") -> Dict[str, Any]:
    """Copy a local path into the mesh transfer tray as an open offer (same host)."""
    p = Path(rel_path).expanduser()
    if not p.is_file():
        return {"ok": False, "error": "file not found"}
    try:
        data = p.read_bytes()
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
    return offer_file(name=p.name, data=data, from_user=agent_id, note=f"local:{p}")
