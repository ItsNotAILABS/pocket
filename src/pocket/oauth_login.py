"""Multi-provider sign-in for POCKET.

Username/password stays. Extra doors:

  · GitHub OAuth (when GITHUB_OAUTH_CLIENT_ID is set)
  · GitHub on this PC via `gh` (loopback — no OAuth app)
  · Google / Microsoft / X OAuth (when their client ids are set)
  · One-time host code (minted on this PC, redeemed on phone/web)

OAuth client secrets live in env or ``~/.pocket/oauth.env`` — never in the repo.
"""

from __future__ import annotations

import json
import os
import secrets
import ssl
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / ".pocket"
OAUTH_ENV = ROOT / "oauth.env"
CODE_FILE = ROOT / "LOGIN_CODE.txt"
STATE_FILE = ROOT / "oauth_states.json"
OWNER_GITHUB_ENV = "POCKET_OWNER_GITHUB"

_STATE_LOCK = Lock()
_CODE_LOCK = Lock()
_HTTP_CTX = ssl.create_default_context()

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "github": {
        "id": "github",
        "name": "GitHub",
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_url": "https://api.github.com/user",
        "scope": "read:user user:email",
        "id_env": ("GITHUB_OAUTH_CLIENT_ID", "GITHUB_CLIENT_ID"),
        "secret_env": ("GITHUB_OAUTH_CLIENT_SECRET", "GITHUB_CLIENT_SECRET"),
        "pkce": True,
    },
    "google": {
        "id": "google",
        "name": "Google",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
        "id_env": ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_CLIENT_ID"),
        "secret_env": ("GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET"),
        "pkce": True,
        "extra_auth": {"access_type": "online", "prompt": "select_account"},
    },
    "microsoft": {
        "id": "microsoft",
        "name": "Microsoft",
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "user_url": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid profile email User.Read",
        "id_env": ("MICROSOFT_OAUTH_CLIENT_ID", "MS_OAUTH_CLIENT_ID", "AZURE_CLIENT_ID"),
        "secret_env": ("MICROSOFT_OAUTH_CLIENT_SECRET", "MS_OAUTH_CLIENT_SECRET", "AZURE_CLIENT_SECRET"),
        "pkce": True,
    },
    "x": {
        "id": "x",
        "name": "X",
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "user_url": "https://api.twitter.com/2/users/me",
        "scope": "users.read tweet.read",
        "id_env": ("X_OAUTH_CLIENT_ID", "TWITTER_OAUTH_CLIENT_ID", "TWITTER_CLIENT_ID"),
        "secret_env": ("X_OAUTH_CLIENT_SECRET", "TWITTER_OAUTH_CLIENT_SECRET", "TWITTER_CLIENT_SECRET"),
        "pkce": True,
    },
}


def _load_oauth_env() -> None:
    if not OAUTH_ENV.is_file():
        return
    try:
        for raw in OAUTH_ENV.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        pass


def _env_first(names: Tuple[str, ...]) -> str:
    _load_oauth_env()
    for n in names:
        v = (os.environ.get(n) or "").strip()
        if v:
            return v
    return ""


def owner_github() -> str:
    return (_env_first((OWNER_GITHUB_ENV,)) or "FreddyCreates").strip().lstrip("@")


def _client(spec: Dict[str, Any]) -> Tuple[str, str]:
    return _env_first(tuple(spec["id_env"])), _env_first(tuple(spec["secret_env"]))


def github_local_available() -> bool:
    try:
        r = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        return r.returncode == 0 and bool((r.stdout or "").strip())
    except Exception:
        return False


def list_providers(*, loopback: bool = False) -> Dict[str, Any]:
    out: List[Dict[str, Any]] = []
    for pid, spec in PROVIDERS.items():
        cid, secret = _client(spec)
        ready = bool(cid and (secret or spec.get("pkce")))
        item = {
            "id": pid,
            "name": spec["name"],
            "ready": ready,
            "start": f"/v1/auth/oauth/{pid}/start",
        }
        if pid == "github":
            item["local"] = bool(loopback and github_local_available())
            item["ready"] = item["ready"] or item["local"]
        out.append(item)
    return {
        "ok": True,
        "providers": out,
        "password": True,
        "one_time_code": True,
        "signup": "/signup",
        "loopback": bool(loopback),
        "owner_github_hint": bool(loopback),
    }


def _load_states() -> Dict[str, Any]:
    if not STATE_FILE.is_file():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        now = time.time()
        return {k: v for k, v in (data or {}).items() if float((v or {}).get("exp") or 0) > now}
    except Exception:
        return {}


def _save_states(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data), encoding="utf-8")


def _put_state(rec: Dict[str, Any]) -> str:
    st = secrets.token_urlsafe(24)
    rec = {**rec, "exp": time.time() + 600}
    with _STATE_LOCK:
        data = _load_states()
        data[st] = rec
        _save_states(data)
    return st


def _pop_state(state: str) -> Optional[Dict[str, Any]]:
    with _STATE_LOCK:
        data = _load_states()
        rec = data.pop(state, None)
        _save_states(data)
        return rec


def _http_json(url: str, *, method: str = "GET", data: Optional[bytes] = None,
               headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "POCKET-host")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=_HTTP_CTX, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        try:
            j = json.loads(raw) if raw else {}
        except Exception:
            j = {"error": raw[:300] or str(e)}
        j.setdefault("ok", False)
        j["_http"] = e.code
        return j
    try:
        return json.loads(raw) if raw else {}
    except Exception:
        return {"raw": raw[:500]}


def callback_url(base: str, provider: str) -> str:
    return f"{base.rstrip('/')}/v1/auth/oauth/{provider}/callback"


def start_oauth(provider: str, *, base: str, next_path: str = "/desk") -> Dict[str, Any]:
    spec = PROVIDERS.get((provider or "").strip().lower())
    if not spec:
        return {"ok": False, "error": "unknown provider"}
    cid, secret = _client(spec)
    if not cid:
        setup = {
            "github": "https://github.com/settings/developers",
            "google": "https://console.cloud.google.com/apis/credentials",
            "microsoft": "https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps",
            "x": "https://developer.x.com/en/portal/dashboard",
        }.get(spec["id"], "")
        return {
            "ok": False,
            "error": f"{spec['name']} login is not configured on this host yet.",
            "setup": setup,
            "env": spec["id_env"][0],
        }
    verifier = secrets.token_urlsafe(48)
    # S256 challenge
    import hashlib
    import base64

    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    redirect = callback_url(base, spec["id"])
    state = _put_state(
        {
            "provider": spec["id"],
            "verifier": verifier,
            "next": next_path or "/desk",
            "redirect": redirect,
        }
    )
    q = {
        "client_id": cid,
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": spec["scope"],
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    q.update(spec.get("extra_auth") or {})
    url = spec["auth_url"] + "?" + urllib.parse.urlencode(q)
    return {"ok": True, "url": url, "provider": spec["id"]}


def _normalize_profile(provider: str, payload: Dict[str, Any]) -> Dict[str, str]:
    if provider == "github":
        return {
            "subject": str(payload.get("id") or ""),
            "login": str(payload.get("login") or ""),
            "display": str(payload.get("name") or payload.get("login") or ""),
            "email": str(payload.get("email") or ""),
            "avatar": str(payload.get("avatar_url") or ""),
        }
    if provider == "google":
        return {
            "subject": str(payload.get("sub") or ""),
            "login": str(payload.get("email") or "").split("@")[0],
            "display": str(payload.get("name") or ""),
            "email": str(payload.get("email") or ""),
            "avatar": str(payload.get("picture") or ""),
        }
    if provider == "microsoft":
        mail = str(payload.get("mail") or payload.get("userPrincipalName") or "")
        return {
            "subject": str(payload.get("id") or ""),
            "login": mail.split("@")[0] or str(payload.get("displayName") or "ms"),
            "display": str(payload.get("displayName") or ""),
            "email": mail,
            "avatar": "",
        }
    if provider == "x":
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        return {
            "subject": str(data.get("id") or ""),
            "login": str(data.get("username") or data.get("name") or ""),
            "display": str(data.get("name") or data.get("username") or ""),
            "email": "",
            "avatar": "",
        }
    return {"subject": "", "login": "", "display": "", "email": "", "avatar": ""}


def finish_oauth(provider: str, *, code: str, state: str) -> Dict[str, Any]:
    spec = PROVIDERS.get((provider or "").strip().lower())
    if not spec:
        return {"ok": False, "error": "unknown provider"}
    rec = _pop_state(state or "")
    if not rec or rec.get("provider") != spec["id"]:
        return {"ok": False, "error": "sign-in expired — try again"}
    cid, secret = _client(spec)
    body = urllib.parse.urlencode(
        {
            "client_id": cid,
            "client_secret": secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": rec.get("redirect") or "",
            "code_verifier": rec.get("verifier") or "",
        }
    ).encode("utf-8")
    tok = _http_json(
        spec["token_url"],
        method="POST",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access = tok.get("access_token") or ""
    if not access:
        return {"ok": False, "error": tok.get("error_description") or tok.get("error") or "oauth token failed"}
    headers = {"Authorization": f"Bearer {access}"}
    if provider == "github":
        headers["Accept"] = "application/vnd.github+json"
    user = _http_json(spec["user_url"], headers=headers)
    if provider == "github" and not user.get("email"):
        mails = _http_json("https://api.github.com/user/emails", headers=headers)
        if isinstance(mails, list):
            primary = next((m for m in mails if m.get("primary") and m.get("email")), None) or next(
                (m for m in mails if m.get("email")), None
            )
            if primary:
                user["email"] = primary.get("email")
        elif isinstance(mails, dict) and isinstance(mails.get("raw"), str):
            pass
    prof = _normalize_profile(spec["id"], user if isinstance(user, dict) else {})
    if not prof.get("subject"):
        return {"ok": False, "error": "provider did not return a user id"}
    from pocket.users import issue_token, upsert_from_oauth

    u = upsert_from_oauth(
        spec["id"],
        prof["subject"],
        login=prof.get("login") or "",
        display=prof.get("display") or "",
        email=prof.get("email") or "",
        avatar=prof.get("avatar") or "",
        prefer_owner=(spec["id"] == "github" and (prof.get("login") or "").lower() == owner_github().lower()),
    )
    if not u.get("ok"):
        return u
    token = issue_token(u["user"])
    return {
        "ok": True,
        "token": token,
        "user": u,
        "next": rec.get("next") or "/desk",
        "provider": spec["id"],
    }


def github_local_login(*, client_ip: str = "") -> Dict[str, Any]:
    ip = (client_ip or "").strip()
    if ip not in ("127.0.0.1", "::1", "localhost"):
        return {"ok": False, "error": "GitHub on this PC only works from this computer"}
    try:
        r = subprocess.run(
            ["gh", "api", "user"],
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except FileNotFoundError:
        return {"ok": False, "error": "GitHub CLI (gh) is not installed"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "gh api user failed").strip()[:240]
        return {"ok": False, "error": err or "gh is not signed in — run: gh auth login"}
    try:
        payload = json.loads(r.stdout or "{}")
    except Exception:
        return {"ok": False, "error": "could not read GitHub user"}
    prof = _normalize_profile("github", payload)
    if not prof.get("subject"):
        return {"ok": False, "error": "GitHub did not return a user"}
    from pocket.users import issue_token, upsert_from_oauth

    u = upsert_from_oauth(
        "github",
        prof["subject"],
        login=prof.get("login") or "",
        display=prof.get("display") or "",
        email=prof.get("email") or "",
        avatar=prof.get("avatar") or "",
        prefer_owner=(prof.get("login") or "").lower() == owner_github().lower(),
    )
    if not u.get("ok"):
        return u
    token = issue_token(u["user"])
    return {"ok": True, "token": token, "user": u, "provider": "github", "local": True}


def mint_login_code(*, client_ip: str = "") -> Dict[str, Any]:
    ip = (client_ip or "").strip()
    if ip not in ("127.0.0.1", "::1", "localhost"):
        return {"ok": False, "error": "one-time codes are minted on this computer only"}
    code = f"{secrets.randbelow(1_000_000):06d}"
    rec = {"code": code, "hash": code, "exp": time.time() + 600, "at": time.time()}
    with _CODE_LOCK:
        ROOT.mkdir(parents=True, exist_ok=True)
        CODE_FILE.write_text(
            "POCKET one-time sign-in code (10 minutes)\n"
            f"{code}\n\n"
            "Enter this on /login → One-time code. Do not share.\n",
            encoding="utf-8",
        )
        (ROOT / "login_code.json").write_text(json.dumps(rec), encoding="utf-8")
    return {"ok": True, "code": code, "expires_sec": 600, "file": str(CODE_FILE)}


def redeem_login_code(code: str) -> Dict[str, Any]:
    raw = "".join(ch for ch in (code or "") if ch.isdigit())
    if len(raw) != 6:
        return {"ok": False, "error": "enter the 6-digit code from this PC"}
    with _CODE_LOCK:
        p = ROOT / "login_code.json"
        if not p.is_file():
            return {"ok": False, "error": "no code is active — mint one on this PC"}
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"ok": False, "error": "code file unreadable"}
        if time.time() > float(rec.get("exp") or 0):
            try:
                p.unlink()
            except Exception:
                pass
            return {"ok": False, "error": "that code expired"}
        if rec.get("code") != raw:
            return {"ok": False, "error": "that code is wrong"}
        try:
            p.unlink()
        except Exception:
            pass
        try:
            CODE_FILE.write_text("used\n", encoding="utf-8")
        except Exception:
            pass
    from pocket.auth import expected_user
    from pocket.users import issue_token

    user = (expected_user() or "pocket").lower()
    token = issue_token(user)
    return {
        "ok": True,
        "token": token,
        "user": {"user": user, "role": "admin", "display": "Owner", "is_owner": True},
        "provider": "code",
    }


def finish_html(*, ok: bool, token: str = "", next_path: str = "/desk", error: str = "") -> str:
    nxt = next_path or "/desk"
    if not ok:
        err = (error or "sign-in failed").replace("<", "")
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'/><title>Sign-in failed</title></head>"
            "<body style='font-family:system-ui;background:#07070b;color:#fafafa;padding:40px'>"
            f"<h1>Could not sign in</h1><p>{err}</p>"
            "<p><a href='/login' style='color:#34d399'>Back to sign in</a></p></body></html>"
        )
    tok = (token or "").replace("</", "")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>Signing in…</title></head>
<body style="font-family:system-ui;background:#07070b;color:#fafafa;padding:40px">
<p>Signing you in…</p>
<script>
try {{
  sessionStorage.setItem('pocket_token', {json.dumps(tok)});
  localStorage.setItem('pocket_token', {json.dumps(tok)});
}} catch (e) {{}}
location.replace({json.dumps(nxt + ("&" if "?" in nxt else "?") + "authed=1")});
</script>
</body></html>
"""
