"""POCKET RECALL — official recall-code software.

Recall codes reattach humans/agents to:
  · KEEP agent state (self-hosted workers bound to a chat)
  · Mission / LOOMGRAPH run context
  · Isolated browser handle (if still running)
  · Optional session snapshot pointer

Unlike pair codes (device pairing), RECALL is for **work continuity**:
leave a chat, come back with a code, resume the same KEEP service.

Format: pk_rcl_<token>
Doctrine: single-use by default; never embed secrets in the code itself.
"""

from __future__ import annotations

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

ROOT = Path.home() / ".pocket" / "recall"
STORE = ROOT / "codes.json"
HMAC_KEY_FILE = ROOT / "recall_hmac.key"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = Lock()
PRODUCT = "POCKET RECALL"
SCHEMA = "pocket.recall.v1"
PROTOCOL = "POCKET-RECALL/1.0"
DEFAULT_TTL = int(os.environ.get("POCKET_RECALL_TTL_SEC") or str(7 * 86400))
PREFIX = "pk_rcl_"


def _hmac_key() -> bytes:
    if HMAC_KEY_FILE.exists():
        return HMAC_KEY_FILE.read_bytes()
    key = secrets.token_bytes(32)
    HMAC_KEY_FILE.write_bytes(key)
    try:
        os.chmod(HMAC_KEY_FILE, 0o600)
    except Exception:
        pass
    return key


def _load() -> Dict[str, Any]:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "codes": []}


def _save(data: Dict[str, Any]) -> None:
    STORE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _hash_raw(raw: str) -> str:
    return hmac.new(_hmac_key(), (raw or "").encode("utf-8"), hashlib.sha256).hexdigest()


def status() -> Dict[str, Any]:
    with _lock:
        data = _load()
        codes = data.get("codes") or []
        live = [c for c in codes if not c.get("used") and float(c.get("exp") or 0) > time.time()]
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "active_codes": len(live),
        "total_records": len(codes),
        "default_ttl_sec": DEFAULT_TTL,
        "prefix": PREFIX,
        "api": {
            "status": "GET /v1/recall",
            "mint": "POST /v1/recall/mint",
            "redeem": "POST /v1/recall/redeem",
            "list": "GET /v1/recall/list",
            "revoke": "POST /v1/recall/revoke",
        },
        "doctrine": "Recall codes reattach KEEP agents + session work — single-use by default.",
    }


def mint(
    *,
    keep_id: str = "",
    session_id: str = "",
    mission_id: str = "",
    loomgraph_run_id: str = "",
    label: str = "",
    ttl_sec: int = 0,
    single_use: bool = True,
    owner: str = "",
    note: str = "",
) -> Dict[str, Any]:
    """Mint a recall code. Raw code shown once."""
    if not any([keep_id, session_id, mission_id, loomgraph_run_id]):
        return {
            "ok": False,
            "error": "need keep_id, session_id, mission_id, or loomgraph_run_id",
        }
    ttl = int(ttl_sec or DEFAULT_TTL)
    ttl = max(300, min(ttl, 30 * 86400))
    raw = PREFIX + secrets.token_urlsafe(18)
    rid = "rcl-" + uuid.uuid4().hex[:10]
    now = time.time()
    entry = {
        "id": rid,
        "hash": _hash_raw(raw),
        "prefix_hint": raw[:12] + "…",
        "keep_id": (keep_id or "").strip(),
        "session_id": (session_id or "").strip(),
        "mission_id": (mission_id or "").strip(),
        "loomgraph_run_id": (loomgraph_run_id or "").strip(),
        "label": (label or note or "recall")[:80],
        "owner": (owner or "pocket").strip().lower(),
        "single_use": bool(single_use),
        "used": False,
        "used_at": None,
        "created_at": now,
        "exp": now + ttl,
        "revoked": False,
    }
    with _lock:
        data = _load()
        codes = data.get("codes") or []
        # prune very old
        codes = [c for c in codes if float(c.get("exp") or 0) > now - 86400 * 14]
        codes.append(entry)
        data["codes"] = codes[-200:]
        _save(data)
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "id": rid,
        "code": raw,  # show once
        "expires_at": entry["exp"],
        "ttl_sec": ttl,
        "single_use": single_use,
        "binds": {
            "keep_id": entry["keep_id"],
            "session_id": entry["session_id"],
            "mission_id": entry["mission_id"],
            "loomgraph_run_id": entry["loomgraph_run_id"],
        },
        "message": "Save this recall code now — raw value is not stored, only a hash.",
        "how": "POST /v1/recall/redeem {\"code\":\"pk_rcl_…\"} to reattach KEEP / session context",
    }


def redeem(code: str, *, peer: str = "") -> Dict[str, Any]:
    """Redeem recall code → work context (KEEP agent, session, etc.)."""
    raw = (code or "").strip()
    if not raw.startswith(PREFIX) or len(raw) < len(PREFIX) + 8:
        return {"ok": False, "error": "invalid recall code format"}
    h = _hash_raw(raw)
    now = time.time()
    with _lock:
        data = _load()
        codes = data.get("codes") or []
        hit = None
        for c in codes:
            if c.get("hash") == h:
                hit = c
                break
        if not hit:
            return {"ok": False, "error": "unknown or already wiped code"}
        if hit.get("revoked"):
            return {"ok": False, "error": "code revoked"}
        if float(hit.get("exp") or 0) < now:
            return {"ok": False, "error": "code expired"}
        if hit.get("used") and hit.get("single_use"):
            return {"ok": False, "error": "code already used (single-use)"}
        hit["used"] = True
        hit["used_at"] = now
        hit["redeemed_by"] = (peer or "")[:80]
        data["codes"] = codes
        _save(data)

    context: Dict[str, Any] = {
        "recall_id": hit.get("id"),
        "label": hit.get("label"),
        "keep_id": hit.get("keep_id"),
        "session_id": hit.get("session_id"),
        "mission_id": hit.get("mission_id"),
        "loomgraph_run_id": hit.get("loomgraph_run_id"),
    }

    # Attach live KEEP state
    if hit.get("keep_id"):
        try:
            from pocket.keep_agents import get_agent

            context["keep"] = get_agent(hit["keep_id"])
        except Exception as e:
            context["keep"] = {"ok": False, "error": str(e)[:120]}

    if hit.get("session_id"):
        try:
            p = Path.home() / ".pocket" / "sessions" / f"{hit['session_id']}.json"
            if p.is_file():
                s = json.loads(p.read_text(encoding="utf-8"))
                context["session"] = {
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "mode": s.get("mode"),
                    "status": s.get("status"),
                    "messages": len(s.get("messages") or []),
                    "chat_ended": s.get("chat_ended"),
                }
        except Exception as e:
            context["session"] = {"ok": False, "error": str(e)[:80]}

    if hit.get("loomgraph_run_id"):
        try:
            rp = Path.home() / ".pocket" / "loomgraph" / "runs" / f"{hit['loomgraph_run_id']}.json"
            if rp.is_file():
                r = json.loads(rp.read_text(encoding="utf-8"))
                context["loomgraph"] = {
                    "id": r.get("id"),
                    "path": r.get("path"),
                    "ok": r.get("ok"),
                    "graph_id": r.get("graph_id"),
                }
        except Exception:
            pass

    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "context": context,
        "message": "Recall redeemed — resume KEEP or open session from context",
        "next": [
            "GET /v1/keep/{keep_id}" if hit.get("keep_id") else None,
            "POST /v1/keep/start with same session to continue" if hit.get("session_id") else None,
        ],
    }


def list_codes(*, owner: str = "", limit: int = 40) -> Dict[str, Any]:
    with _lock:
        data = _load()
        codes = data.get("codes") or []
    now = time.time()
    rows = []
    for c in reversed(codes):
        if owner and c.get("owner") != owner:
            continue
        rows.append(
            {
                "id": c.get("id"),
                "prefix_hint": c.get("prefix_hint"),
                "label": c.get("label"),
                "keep_id": c.get("keep_id"),
                "session_id": c.get("session_id"),
                "used": c.get("used"),
                "revoked": c.get("revoked"),
                "exp": c.get("exp"),
                "active": (not c.get("used") or not c.get("single_use"))
                and not c.get("revoked")
                and float(c.get("exp") or 0) > now,
                "created_at": c.get("created_at"),
            }
        )
        if len(rows) >= limit:
            break
    return {"ok": True, "codes": rows, "count": len(rows)}


def revoke(code_id: str = "", *, code: str = "") -> Dict[str, Any]:
    with _lock:
        data = _load()
        codes = data.get("codes") or []
        hit = None
        if code:
            h = _hash_raw(code.strip())
            for c in codes:
                if c.get("hash") == h:
                    hit = c
                    break
        elif code_id:
            for c in codes:
                if c.get("id") == code_id:
                    hit = c
                    break
        if not hit:
            return {"ok": False, "error": "not found"}
        hit["revoked"] = True
        hit["revoked_at"] = time.time()
        data["codes"] = codes
        _save(data)
    return {"ok": True, "id": hit.get("id"), "revoked": True, "product": PRODUCT}
