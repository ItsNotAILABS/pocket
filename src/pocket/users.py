"""Multi-user seats for POCKET.

Owner (admin) stays owner. Invited people create THEIR OWN accounts —
they never log into the operator account.

Seat invites are single-use (or limited-use) cryptographic keys.
We store only SHA-256 hashes of invite keys; the raw key is shown once when minted.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
USERS_FILE = ROOT / "users.json"
_lock = Lock()

INVITE_ENV = "POCKET_INVITE_CODE"
MAX_SEATS = int(os.environ.get("POCKET_MAX_SEATS") or "25")
TOKEN_TTL_SEC = 86400 * 7
TOKEN_IDLE_SEC = 86400 * 2
PUBLIC_SIGNUP_ENV = "POCKET_PUBLIC_SIGNUP"


def public_signup_enabled() -> bool:
    """Public visitors can create their own member seat without a pk_seat_ key.

    Default ON so the public URL has Sign in + Sign up. Set POCKET_PUBLIC_SIGNUP=0
    to require invites again. Invite keys still work when provided.
    """
    v = (os.environ.get(PUBLIC_SIGNUP_ENV) or "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    return True


def _hash(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()


def _sha_key(raw: str) -> str:
    return hashlib.sha256((raw or "").encode("utf-8")).hexdigest()


def _load() -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    if USERS_FILE.exists():
        try:
            data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
            return _migrate(data)
        except Exception:
            pass
    data = _bootstrap()
    _save(data)
    _write_invite_readme(data)
    return data


def _bootstrap() -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "schema": "pocket.users.v2",
        "users": {},
        "seat_invites": [],
        "tokens": {},
        "created_at": time.time(),
    }
    # seed owner/admin from host ACCESS — never overwritten on later loads
    try:
        from pocket.auth import expected_password, expected_user

        admin = (expected_user() or "pocket").strip().lower()
        salt = secrets.token_hex(8)
        data["users"][admin] = {
            "user": admin,
            "salt": salt,
            "hash": _hash(expected_password(), salt),
            "role": "admin",
            "created_at": time.time(),
            "display": "Owner",
            "is_owner": True,
        }
    except Exception:
        pass
    # one open seat invite for first ship (raw written to file once)
    raw = os.environ.get(INVITE_ENV) or ("pk_seat_" + secrets.token_urlsafe(18))
    data["seat_invites"].append(
        {
            "id": "inv_" + secrets.token_hex(6),
            "hash": _sha_key(raw),
            "prefix": raw[:12] + "…",
            "label": "bootstrap",
            "max_uses": 10,
            "uses": 0,
            "created_at": time.time(),
            "expires_at": time.time() + 86400 * 90,
            "created_by": "system",
            "_bootstrap_raw": raw,  # stripped after first write
        }
    )
    return data


def _migrate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Upgrade v1 single shared invite → seat_invites without logging anyone out."""
    changed = False
    if "seat_invites" not in data:
        data["seat_invites"] = []
        changed = True
    # legacy single invite string → one multi-use seat key (hash only; raw unknown if already shared)
    legacy = (data.get("invite") or "").strip()
    if legacy and not data["seat_invites"]:
        data["seat_invites"].append(
            {
                "id": "inv_legacy",
                "hash": _sha_key(legacy),
                "prefix": legacy[:12] + "…",
                "label": "legacy-shared",
                "max_uses": 25,
                "uses": 0,
                "created_at": time.time(),
                "expires_at": time.time() + 86400 * 90,
                "created_by": "migrate",
                "note": "Migrated from old single invite. Prefer mint_seat_invite for new users.",
            }
        )
        changed = True
    # mark first admin as owner
    users = data.get("users") or {}
    for u, rec in users.items():
        if (rec.get("role") or "") == "admin" and "is_owner" not in rec:
            rec["is_owner"] = True
            changed = True
            break
    data["schema"] = "pocket.users.v2"
    if changed:
        _save(data)
        _write_invite_readme(data)
    return data


def _save(data: Dict[str, Any]) -> None:
    # never persist bootstrap raw keys
    for inv in data.get("seat_invites") or []:
        inv.pop("_bootstrap_raw", None)
    USERS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_invite_readme(data: Dict[str, Any], *, last_raw: str = "") -> None:
    """Operator-facing instructions — not a shared login password."""
    lines = [
        "POCKET multi-user (OWNER stays owner)",
        "====================================",
        "",
        "Users do NOT log into your operator account.",
        "They create THEIR OWN username + password with a seat invite key.",
        "",
        "Mint new single-use keys (admin API or desk later):",
        "  POST /v1/admin/invites  { \"label\": \"alice\", \"max_uses\": 1 }",
        "",
    ]
    if last_raw:
        lines += [
            "NEW SEAT KEY (show once — store SHA only on server):",
            last_raw,
            "",
            "Give this key to ONE person. They open Register and create their account.",
            "",
        ]
    # bootstrap raw if present in memory before strip
    for inv in data.get("seat_invites") or []:
        raw = inv.get("_bootstrap_raw")
        if raw:
            lines += [
                "Bootstrap seat key (rotate after first users):",
                raw,
                f"  uses {inv.get('uses')}/{inv.get('max_uses')}  id={inv.get('id')}",
                "",
            ]
    lines += [
        "Your owner login remains ACCESS.txt / admin user — separate from member seats.",
        f"Max seats: {MAX_SEATS}",
    ]
    try:
        (ROOT / "INVITE.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        pass


def list_users() -> List[Dict[str, Any]]:
    with _lock:
        data = _load()
        out = []
        for u, rec in (data.get("users") or {}).items():
            out.append(
                {
                    "user": u,
                    "role": rec.get("role") or "member",
                    "display": rec.get("display") or u,
                    "is_owner": bool(rec.get("is_owner")),
                    "created_at": rec.get("created_at"),
                    "edition": rec.get("edition") or ("founder" if rec.get("is_owner") else "market"),
                    "plan": rec.get("plan") or "",
                    "channel": rec.get("channel") or "",
                }
            )
        return out


def mint_seat_invite(
    *,
    label: str = "",
    max_uses: int = 1,
    expires_days: int = 30,
    created_by: str = "admin",
) -> Dict[str, Any]:
    """Create a cryptographic seat key. Raw key returned once; server stores SHA-256 only."""
    max_uses = max(1, min(50, int(max_uses or 1)))
    expires_days = max(1, min(365, int(expires_days or 30)))
    raw = "pk_seat_" + secrets.token_urlsafe(24)
    rec = {
        "id": "inv_" + secrets.token_hex(8),
        "hash": _sha_key(raw),
        "prefix": raw[:14] + "…",
        "label": (label or "seat")[:40],
        "max_uses": max_uses,
        "uses": 0,
        "created_at": time.time(),
        "expires_at": time.time() + 86400 * expires_days,
        "created_by": (created_by or "admin")[:40],
    }
    with _lock:
        data = _load()
        data.setdefault("seat_invites", []).append(rec)
        _save(data)
        _write_invite_readme(data, last_raw=raw)
    return {
        "ok": True,
        "invite_key": raw,
        "id": rec["id"],
        "label": rec["label"],
        "max_uses": max_uses,
        "expires_at": rec["expires_at"],
        "message": "Give invite_key to the new user. They register THEIR own account. You stay owner.",
    }


def list_invites() -> List[Dict[str, Any]]:
    """Admin view — never returns raw keys or hashes."""
    with _lock:
        data = _load()
        out = []
        now = time.time()
        for inv in data.get("seat_invites") or []:
            out.append(
                {
                    "id": inv.get("id"),
                    "prefix": inv.get("prefix"),
                    "label": inv.get("label"),
                    "max_uses": inv.get("max_uses"),
                    "uses": inv.get("uses"),
                    "remaining": max(0, int(inv.get("max_uses") or 0) - int(inv.get("uses") or 0)),
                    "expired": now > float(inv.get("expires_at") or 0),
                    "created_at": inv.get("created_at"),
                    "expires_at": inv.get("expires_at"),
                    "created_by": inv.get("created_by"),
                }
            )
        return out


def _consume_invite(data: Dict[str, Any], raw_invite: str) -> Optional[str]:
    """Validate seat key by SHA-256; increment uses. Returns invite id or None."""
    raw = (raw_invite or "").strip()
    if not raw:
        return None
    h = _sha_key(raw)
    now = time.time()
    for inv in data.get("seat_invites") or []:
        stored = str(inv.get("hash") or "")
        if not stored or not hmac.compare_digest(stored, h):
            continue
        if now > float(inv.get("expires_at") or 0):
            return None
        uses = int(inv.get("uses") or 0)
        max_u = int(inv.get("max_uses") or 1)
        if uses >= max_u:
            return None
        inv["uses"] = uses + 1
        inv["last_used_at"] = now
        return str(inv.get("id") or "")
    # legacy v1 plaintext invite field
    legacy = (data.get("invite") or "").strip()
    if legacy and hmac.compare_digest(raw, legacy):
        return "legacy"
    return None


def register(
    user: str,
    password: str,
    invite: str,
    display: str = "",
    *,
    accepted_terms: bool = False,
    plan: str = "",
    channel: str = "sold",
    email: str = "",
) -> Dict[str, Any]:
    """Create a NEW member seat. Never becomes owner. Never touches owner password.

    Invite is optional when public signup is on (public URL /join /signup).
    """
    user = (user or "").strip().lower()
    password = password or ""
    invite = (invite or "").strip()
    email = (email or "").strip().lower()
    if len(user) < 2:
        return {"ok": False, "error": "username needs at least 2 characters"}
    if not user.replace("_", "").replace("-", "").isalnum():
        return {"ok": False, "error": "username: letters, numbers, _ and - only"}
    if len(password) < 8:
        return {"ok": False, "error": "password needs at least 8 characters"}
    if not accepted_terms:
        return {"ok": False, "error": "accept the terms to create a seat"}
    if user in ("admin", "root", "system", "owner", "operator", "founder"):
        return {"ok": False, "error": "reserved username"}
    if email and ("@" not in email or "." not in email.split("@")[-1] or len(email) > 120):
        return {"ok": False, "error": "that email does not look valid"}
    with _lock:
        data = _load()
        # block registering as existing owner username
        existing = (data.get("users") or {}).get(user)
        if existing:
            return {"ok": False, "error": "that username is taken — sign in, or pick another"}
        n = len(data.get("users") or {})
        if n >= MAX_SEATS:
            return {"ok": False, "error": f"seat limit reached ({MAX_SEATS})"}
        inv_id = _consume_invite(data, invite) if invite else None
        if invite and not inv_id:
            return {"ok": False, "error": "that invite is invalid, used up, or mistyped"}
        if not inv_id and not public_signup_enabled():
            return {"ok": False, "error": "signup needs a seat invite (pk_seat_…) from the operator"}
        salt = secrets.token_hex(8)
        data.setdefault("users", {})[user] = {
            "user": user,
            "salt": salt,
            "hash": _hash(password, salt),
            "role": "member",
            "is_owner": False,
            "display": (display or user)[:40],
            "email": email[:120],
            "created_at": time.time(),
            "accepted_terms_at": time.time(),
            "seat_invite_id": inv_id or "public",
            "edition": "market",
            "channel": (channel or ("public" if not inv_id else "sold"))[:24],
            "plan": (plan or ("public" if not inv_id else ""))[:40],
        }
        _save(data)
    tenant = ""
    clis: Dict[str, Any] = {}
    try:
        from pocket.platform_space import tenant_cwd, tenant_root

        tenant = str(tenant_root(user))
        tenant_cwd(user, "files")
    except Exception:
        pass
    try:
        from pocket.model_clis import ensure_seat

        clis = ensure_seat(user, install_host=False)
    except Exception:
        clis = {}
    twin: Dict[str, Any] = {}
    try:
        from pocket.twin_mint import mint as mint_twin

        twin = mint_twin(user)
    except Exception as e:
        twin = {"ok": False, "error": str(e)[:160]}
    return {
        "ok": True,
        "user": user,
        "role": "member",
        "edition": "market",
        "channel": channel or "sold",
        "plan": plan or "",
        "tenant": tenant,
        "twin": twin.get("twin") if isinstance(twin, dict) else twin,
        "clis": clis.get("seat") if isinstance(clis, dict) else clis,
        "message": "Your seat is minted on this PC: files, encrypted vault, Pocket vault, and CLIs inside your workspace.",
    }


def _safe_oauth_username(login: str) -> str:
    raw = "".join(ch if ch.isalnum() or ch in "-_" else "" for ch in (login or "").lower())
    raw = raw.strip("-_")[:32]
    if len(raw) < 2:
        raw = "user" + secrets.token_hex(3)
    if raw in ("admin", "root", "system", "owner", "operator", "founder", "pocket"):
        return "gh-" + raw
    return raw


def upsert_from_oauth(
    provider: str,
    subject: str,
    *,
    login: str = "",
    display: str = "",
    email: str = "",
    avatar: str = "",
    prefer_owner: bool = False,
) -> Dict[str, Any]:
    """Find or create a seat from a verified OAuth identity. Never overwrites owner password."""
    provider = (provider or "").strip().lower()
    subject = str(subject or "").strip()
    if not provider or not subject:
        return {"ok": False, "error": "provider identity missing"}
    ident_key = f"{provider}:{subject}"
    email = (email or "").strip().lower()
    display = (display or login or provider)[:40]
    with _lock:
        data = _load()
        idx = data.setdefault("oauth_identities", {})
        existing_user = idx.get(ident_key)
        users = data.setdefault("users", {})
        if existing_user and existing_user in users:
            rec = users[existing_user]
        elif prefer_owner:
            owner_name = None
            for u, rec0 in users.items():
                if rec0.get("is_owner") or rec0.get("role") == "admin":
                    owner_name = u
                    rec = rec0
                    break
            if not owner_name:
                try:
                    from pocket.auth import expected_user

                    owner_name = (expected_user() or "pocket").lower()
                except Exception:
                    owner_name = "pocket"
                rec = users.get(owner_name) or {
                    "user": owner_name,
                    "role": "admin",
                    "is_owner": True,
                    "display": "Owner",
                    "created_at": time.time(),
                }
                users[owner_name] = rec
            existing_user = owner_name
        else:
            rec = None
            existing_user = ""
        if rec is None:
            base = _safe_oauth_username(login)
            name = base
            n = 2
            while name in users:
                name = f"{base}{n}"
                n += 1
                if n > 99:
                    name = base + secrets.token_hex(2)
                    break
            salt = secrets.token_hex(8)
            rec = {
                "user": name,
                "salt": salt,
                "hash": _hash(secrets.token_urlsafe(24), salt),
                "passwordless": True,
                "role": "member",
                "is_owner": False,
                "display": display or name,
                "email": email[:120],
                "avatar": (avatar or "")[:240],
                "created_at": time.time(),
                "accepted_terms_at": time.time(),
                "seat_invite_id": f"oauth:{provider}",
                "edition": "market",
                "channel": "oauth",
                "plan": "public",
                "identities": [],
            }
            users[name] = rec
            existing_user = name
        ids = rec.setdefault("identities", [])
        if not any(i.get("provider") == provider and str(i.get("subject")) == subject for i in ids):
            ids.append(
                {
                    "provider": provider,
                    "subject": subject,
                    "login": (login or "")[:80],
                    "at": time.time(),
                }
            )
        if email and not rec.get("email"):
            rec["email"] = email[:120]
        if display and not rec.get("display"):
            rec["display"] = display
        if avatar:
            rec["avatar"] = avatar[:240]
        idx[ident_key] = existing_user
        _save(data)
    clis: Dict[str, Any] = {}
    try:
        from pocket.model_clis import ensure_seat

        clis = ensure_seat(existing_user, install_host=False)
    except Exception:
        clis = {}
    return {
        "ok": True,
        "user": existing_user,
        "role": rec.get("role") or "member",
        "display": rec.get("display") or existing_user,
        "is_owner": bool(rec.get("is_owner")),
        "provider": provider,
        "new": rec.get("created_at") and (time.time() - float(rec.get("created_at") or 0) < 5),
        "clis": clis.get("seat") if isinstance(clis, dict) else clis,
    }


def verify(user: str, password: str) -> Optional[Dict[str, Any]]:
    """Accept username aliases (pocket / owner / admin empty→pocket) + ACCESS password."""
    user = (user or "").strip().lower()
    password = password if password is not None else ""
    # Blank username on many gates — treat as founder seat when password present
    if not user and password:
        user = "pocket"
    # Common aliases people type on phone / web
    if user in ("owner", "admin", "root", "operator", "founder"):
        try:
            from pocket.auth import expected_user

            user = (expected_user() or "pocket").lower()
        except Exception:
            user = "pocket"
    if not password:
        return None
    with _lock:
        data = _load()
        rec = (data.get("users") or {}).get(user)
        if not rec:
            try:
                from pocket.auth import expected_password, expected_user

                exp_u = (expected_user() or "pocket").lower()
                exp_p = expected_password()
                # Match founder ACCESS password for pocket or alias
                if user in (exp_u, "pocket") and hmac.compare_digest(password, exp_p):
                    return {
                        "user": exp_u,
                        "role": "admin",
                        "display": "Owner",
                        "is_owner": True,
                    }
            except Exception:
                pass
            return None
        if hmac.compare_digest(rec.get("hash") or "", _hash(password, rec.get("salt") or "")):
            return {
                "user": user,
                "role": rec.get("role") or "member",
                "display": rec.get("display") or user,
                "is_owner": bool(rec.get("is_owner")),
            }
        # Founder password still wins if user row exists but was re-keyed from ACCESS
        try:
            from pocket.auth import expected_password, expected_user

            exp_u = (expected_user() or "pocket").lower()
            if user == exp_u and hmac.compare_digest(password, expected_password()):
                return {
                    "user": exp_u,
                    "role": "admin",
                    "display": rec.get("display") or "Owner",
                    "is_owner": True,
                }
        except Exception:
            pass
    return None


def issue_token(user: str) -> str:
    tok = secrets.token_urlsafe(24)
    now = time.time()
    with _lock:
        data = _load()
        data.setdefault("tokens", {})[tok] = {"user": user, "at": now, "last": now}
        cut = now - TOKEN_TTL_SEC
        data["tokens"] = {k: v for k, v in data["tokens"].items() if (v.get("at") or 0) > cut}
        _save(data)
    return tok


def revoke_token(token: str) -> bool:
    if not token:
        return False
    with _lock:
        data = _load()
        toks = data.setdefault("tokens", {})
        if token in toks:
            del toks[token]
            _save(data)
            return True
    return False


def revoke_all_for_user(user: str) -> int:
    user = (user or "").strip().lower()
    n = 0
    with _lock:
        data = _load()
        toks = data.setdefault("tokens", {})
        drop = [k for k, v in toks.items() if (v.get("user") or "").lower() == user]
        for k in drop:
            del toks[k]
            n += 1
        _save(data)
    return n


def change_password(user: str, old_password: str, new_password: str) -> Dict[str, Any]:
    user = (user or "").strip().lower()
    if len(new_password or "") < 8:
        return {"ok": False, "error": "new password min 8"}
    with _lock:
        data = _load()
        rec = (data.get("users") or {}).get(user)
        if not rec:
            try:
                from pocket.auth import expected_password, expected_user

                if user == (expected_user() or "pocket").lower() and hmac.compare_digest(
                    old_password, expected_password()
                ):
                    salt = secrets.token_hex(8)
                    data.setdefault("users", {})[user] = {
                        "user": user,
                        "salt": salt,
                        "hash": _hash(new_password, salt),
                        "role": "admin",
                        "display": "Owner",
                        "is_owner": True,
                        "created_at": time.time(),
                    }
                    _save(data)
                    return {"ok": True, "user": user}
            except Exception:
                pass
            return {"ok": False, "error": "user not found"}
        if not hmac.compare_digest(rec.get("hash") or "", _hash(old_password, rec.get("salt") or "")):
            return {"ok": False, "error": "old password incorrect"}
        salt = secrets.token_hex(8)
        rec["salt"] = salt
        rec["hash"] = _hash(new_password, salt)
        rec["password_changed_at"] = time.time()
        _save(data)
    revoke_all_for_user(user)
    return {"ok": True, "user": user, "note": "your sessions revoked — sign in again with new password"}


def rotate_invite() -> Dict[str, Any]:
    """Mint a fresh multi-use operator invite (legacy alias → mint_seat_invite)."""
    return mint_seat_invite(label="rotated", max_uses=10, expires_days=60, created_by="rotate")


def invite_code() -> str:
    """Deprecated: do not expose raw keys via API. Returns empty; use list_invites."""
    return ""


def user_from_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    now = time.time()
    with _lock:
        data = _load()
        rec = (data.get("tokens") or {}).get(token)
        if not rec:
            return None
        created = float(rec.get("at") or 0)
        last = float(rec.get("last") or created)
        if now - created > TOKEN_TTL_SEC or now - last > TOKEN_IDLE_SEC:
            try:
                del data["tokens"][token]
                _save(data)
            except Exception:
                pass
            return None
        # Do not rewrite users.json on every /v1/auth/me — Edge fires several
        # at once and a locked save made a valid login look like 401.
        if now - last > 30:
            rec["last"] = now
            _save(data)
        u = rec.get("user")
        urec = (data.get("users") or {}).get(u) or {}
        role = urec.get("role") or "member"
        if not urec:
            try:
                from pocket.auth import expected_user

                if (u or "").lower() == (expected_user() or "pocket").lower():
                    role = "admin"
                    return {"user": u, "role": role, "display": "Owner", "is_owner": True}
            except Exception:
                pass
        return {
            "user": u,
            "role": role,
            "display": urec.get("display") or u,
            "is_owner": bool(urec.get("is_owner")),
            "edition": urec.get("edition") or ("founder" if urec.get("is_owner") or role == "admin" else "market"),
            "plan": urec.get("plan") or "",
            "channel": urec.get("channel") or "",
        }


def set_user_plan(user: str, plan: str, *, source: str = "revenuecat") -> Dict[str, Any]:
    """Attach a paid plan to an existing seat (RevenueCat webhook / sync)."""
    user = (user or "").strip().lower()
    plan = (plan or "").strip()[:40]
    if not user:
        return {"ok": False, "error": "user required"}
    with _lock:
        data = _load()
        rec = (data.get("users") or {}).get(user)
        if not rec:
            return {"ok": False, "error": "no such seat"}
        rec["plan"] = plan
        rec["plan_source"] = source
        rec["plan_at"] = time.time()
        _save(data)
    return {"ok": True, "user": user, "plan": plan, "source": source}
