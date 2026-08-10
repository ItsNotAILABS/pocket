"""Access control for POCKET — required password when exposed to the internet."""

from __future__ import annotations

import base64
import hmac
import os
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Mapping, Optional, Tuple

# Prefer user home (survives repo moves); fall back to repo .pocket
HOME_AUTH = Path.home() / ".pocket"
REPO_AUTH = Path(__file__).resolve().parents[2] / ".pocket"
AUTH_DIR = HOME_AUTH
AUTH_FILE = AUTH_DIR / "access.env"
ACCESS_NOTE = AUTH_DIR / "ACCESS.txt"
AUTH_USER_ENV = "POCKET_BASIC_AUTH_USER"
AUTH_PASS_ENV = "POCKET_BASIC_AUTH_PASSWORD"
DEFAULT_USER = "pocket"

# ---------------------------------------------------------------------------
# Public surface policy
# - ALWAYS public: marketing + health + login (never the live desk product)
# - LOCAL public: full desk/phone shells only on loopback (this PC)
# - Internet / Cloudflare clients never get desk HTML without auth
# Override: POCKET_PUBLIC_LOCK=0 restores old "desk shell is public" behavior
# ---------------------------------------------------------------------------
ALWAYS_PUBLIC_PATHS = frozenset({
    "/",
    "/tour",
    "/product",
    "/present",
    "/landing",
    "/home",
    "/health",
    "/v1/health",
    "/v1/production",
    "/v1/prod/status",
    "/v1/hardware",
    "/v1/aether",
    "/v1/phone/hardware",
    "/v1/phone/ready",
    "/v1/phone/status",
    "/v1/runtime/heartbeat",
    "/v1/heartbeat",
    "/v1/status",
    "/v1/ready",
    "/v1/auth/login",
    "/v1/auth/register",
    "/v1/auth/desktop",
    "/v1/auth/local",
    # Shared browser login client (all surfaces)
    "/auth/client.js",
    "/v1/auth/client.js",
    # Protocol catalog + identity (read-only; agents & public docs)
    "/v1/protocols",
    "/v1/protocols/status",
    "/v1/platform/protocols",
    "/v1/identity",
    "/v1/whoami",
    "/v1/pocket/identity",
    "/v1/rah",
    "/v1/rah/status",
    "/v1/rah/plan",
    "/v1/protocols/rah",
    "/v1/internal-models",
    "/v1/internal_models",
    "/v1/models/internal",
    "/v1/genetic",
    "/v1/genetic/status",
    "/v1/economy",
    "/v1/economy/status",
    "/v1/economy/protocols",
    "/v1/economy/twins",
    "/v1/economy/wallets",
    "/v1/economy/fees",
    "/install",
    "/install/",
    "/v1/install",
    "/v1/install/slices",
    # Pairing redeem is token-gated inside the handler (not owner password)
    "/v1/node/redeem",
    "/v1/node/hello",
    # Marketing / docs / downloads (no host control)
    "/developers",
    "/api",
    "/docs/api",
    "/docs",
    "/docs/hub",
    "/get",
    "/start",
    "/install",
    "/updates",
    "/changelog",
    "/whats-new",
    "/download",
    "/download/desktop",
    "/download/windows",
    "/license",
    "/license/text",
    "/v1/license",
    "/v1/license/accept",
    "/v1/legal",
    "/v1/ai",
    "/v1/ai/agents",
    "/v1/ai/pricing",
    "/v1/ai/openapi",
    "/v1/product/channels",
    "/v1/channels",
    "/v1/desktop/releases",
    "/v1/class",
    "/v1/first-class",
    "/v1/grade",
    "/v1/novae",
    "/v1/novae/status",
    "/v1/novae/list",
    "/v1/use-cases",
    "/v1/usecases",
    "/v1/parity",
    "/v1/emergent",
    "/forge",
    "/git",
    "/auro",
    # Phone PWA shell must load on public domain (pair + unlock UI inside).
    # Agent / host-control APIs remain auth-gated — only HTML + manifest are public.
    "/phone",
    "/m",
    "/mobile",
    "/phone/",
    "/m/",
    "/mobile/",
    "/phone/manifest.webmanifest",
    "/m/manifest.webmanifest",
    # Product HTML shells on the public domain (Cloudflare / phone browser).
    # Browsers cannot send Authorization on a plain navigation to /desk, so the
    # full app JS must load first; it uses localStorage pocket_token + in-app gate.
    # APIs (/v1/sessions, /v1/*/run, etc.) stay auth-gated.
    "/desk",
    "/app",
    "/desktop",
    "/chat",
    "/os",
    "/agent-os",
    "/systems",
    "/studio",
    "/studio/voice",
    "/voice-studio",
    "/v2v-studio",
    "/work",
    "/work-studio",
    "/studio/work",
    "/curiosities",
    "/weird",
    "/studio/create",
    "/studio/creative",
    "/creative",
    "/studio/chat",
    "/create",
    "/community",
    "/studio/community",
    "/share",
    "/studio/share",
    "/loomgraph",
    "/graph",
    "/graph-loop",
    "/harness/loomgraph",
    "/mail",
    # Lab readiness map (shell only; APIs auth-gated)
    "/lab",
    "/lab/",
    # Pair seat unlock is token-gated inside handler
    "/v1/node/pair-login",
    "/v1/node/seat",
})

# Only available without credentials when the client is this machine (loopback / LAN).
# Prefer HTML shells in ALWAYS_PUBLIC above so Cloudflare web works.
# Keep data/API helpers here for local/LAN convenience only.
LOCAL_PUBLIC_PATHS = frozenset({
    "/v1/work-studio",
    "/v1/work-studio/assist",
    "/v1/assistant",
    "/v1/assistant/chat",
    "/v1/integrations",
    "/v1/integrations/catalog",
    "/v1/integrations/readiness",
    "/v1/integrations/status",
    "/v1/connectors",
    "/v1/connectors/readiness",
    "/v1/creative",
    "/v1/creative/catalog",
    "/v1/creative/status",
    "/v1/creative/self_test",
    "/v1/creative/audit",
    "/v1/creative/live",
    "/v1/community",
    "/v1/community/feed",
    "/v1/community/status",
    "/v1/shares",
    "/v1/loomgraph",
    "/v1/loomgraph/catalog",
    "/v1/loomgraph/live",
    "/v1/loomgraph/runs",
    "/v1/loomgraph/self_test",
    "/v1/loomgraph/audit",
    "/v1/graph",
    "/v1/harness/loomgraph",
    "/v1/keep",
    "/v1/keep/status",
    "/v1/keep/list",
    "/v1/isolate",
    "/v1/isolate/status",
    "/v1/isolate/list",
    "/v1/docker-browser",
    "/v1/recall",
    "/v1/recall/status",
    "/v1/recall/list",
    "/v1/mail",
    "/v1/mail/status",
    "/v1/mail/templates",
    "/v1/mail/outbox",
    "/v1/pocket-mail",
    "/v1/agent-mail",
    "/v1/agent-mail/status",
    "/v1/agent-mail/accounts",
    "/v1/agent-mail/inbox",
    "/v1/web-ui",
    "/v1/web-ui/status",
    "/v1/python-engine",
    "/v1/python-engines",
    "/v1/catalog",
    "/v1/platform/catalog",
    "/v1/platform-catalog",
    "/mail",
    "/agent-mail",
    "/docs",
    "/docs/hub",
    "/v1/iot",
    "/v1/iot/home",
    "/v1/iot/devices",
    "/v1/iot/discover",
    "/v1/iot/phone",
    "/v1/iot/presence",
    "/v1/iot/control",
    "/v1/home/iot",
    "/v1/home/devices",
    "/v1/phone/bridge",
    "/v1/node/hello",
})

# Back-compat name used by auth_summary / older callers
PUBLIC_PATHS = ALWAYS_PUBLIC_PATHS | LOCAL_PUBLIC_PATHS

# Prefixes that remain public (file downloads under /download/files/…)
PUBLIC_PREFIXES = (
    "/download/files/",
    "/download/desktop/",
    "/auro/",
    # One-line install slices (scripts, slices.json, README) — public downloads
    "/install/",
    # Docs hub how-to pages (markdown rendered)
    "/docs/view/",
    "/docs/md/",
)

# Loopback-only prefixes (in-chat app preview iframes need cookie-less same-origin GET)
LOCAL_PUBLIC_PREFIXES = (
    "/v1/preview/",
    # Voice mic / Aria — same-origin proxy must work without blocking Edge app
    "/v1/pocket-voice/",
    "/v1/voice/",
)

# App shells that should get a friendly lock HTML instead of raw 401 JSON
APP_SHELL_PATHS = frozenset({
    "/desk",
    "/app",
    "/desktop",
    "/chat",
    "/os",
    "/agent-os",
    "/systems",
    "/phone",
    "/m",
    "/mobile",
    "/studio",
    "/studio/voice",
    "/voice-studio",
    "/v2v-studio",
    "/lab",
    "/work",
    "/work-studio",
    "/mail",
    "/agent-mail",
    "/curiosities",
    "/lab",
    "/weird",
})

# Rate limit failed logins: max N failures per IP per window
_fail_lock = Lock()
_fail_log: dict[str, list[float]] = defaultdict(list)
MAX_FAILS = 40  # higher: tunnel + live tests share IPs; real attacks still throttle
FAIL_WINDOW = 300.0  # 5 minutes


@dataclass(frozen=True)
class BasicAuth:
    user: str
    password: str
    source: Path


def _random_password() -> str:
    return secrets.token_urlsafe(24).rstrip("=")


def _parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def _write_env_file(path: Path, user: str, password: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# POCKET access — do not commit or share\n"
        f"{AUTH_USER_ENV}={user}\n"
        f"{AUTH_PASS_ENV}={password}\n",
        encoding="utf-8",
    )
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def load_basic_auth() -> BasicAuth:
    user = (os.environ.get(AUTH_USER_ENV) or DEFAULT_USER).strip() or DEFAULT_USER
    password = (os.environ.get(AUTH_PASS_ENV) or "").strip()
    source = AUTH_FILE

    # Load from home, then repo
    for candidate in (HOME_AUTH / "access.env", REPO_AUTH / "access.env"):
        if password:
            break
        if candidate.exists():
            try:
                data = _parse_env_file(candidate)
                user = (data.get(AUTH_USER_ENV) or user).strip() or DEFAULT_USER
                password = (data.get(AUTH_PASS_ENV) or "").strip()
                if password:
                    source = candidate
            except Exception:
                pass

    created = False
    if not password:
        password = _random_password()
        created = True
        source = AUTH_FILE
        _write_env_file(AUTH_FILE, user, password)
        # mirror to repo .pocket for discoverability
        try:
            _write_env_file(REPO_AUTH / "access.env", user, password)
        except Exception:
            pass

    os.environ[AUTH_USER_ENV] = user
    os.environ[AUTH_PASS_ENV] = password

    if created or not ACCESS_NOTE.exists():
        try:
            ACCESS_NOTE.parent.mkdir(parents=True, exist_ok=True)
            ACCESS_NOTE.write_text(
                "POCKET ACCESS (required on phone / public URL)\n"
                "================================================\n"
                f"Username: {user}\n"
                f"Password: {password}\n"
                "\n"
                "Phone: open https://pocket.medinatechlabs.net/\n"
                "Browser will prompt for login, or use the in-app password field.\n"
                "\n"
                f"Stored in: {source}\n"
                "Do not post this password publicly.\n"
                "================================================\n",
                encoding="utf-8",
            )
        except Exception:
            pass

    return BasicAuth(user=user, password=password, source=source)


_AUTH = load_basic_auth()


def reload_auth() -> BasicAuth:
    global _AUTH
    _AUTH = load_basic_auth()
    return _AUTH


def public_lock_enabled() -> bool:
    """When true (default), remote clients cannot load desk/phone without auth."""
    v = (os.environ.get("POCKET_PUBLIC_LOCK") or "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _is_private_ip(ip: str) -> bool:
    """RFC1918 / link-local / ULA — same-WiFi / home LAN peers (not public internet)."""
    ip = (ip or "").strip().lower()
    if not ip:
        return False
    if ip.startswith("::ffff:"):
        ip = ip[7:]
    if ip in ("127.0.0.1", "::1", "localhost"):
        return True
    if ip.startswith("10."):
        return True
    if ip.startswith("192.168."):
        return True
    if ip.startswith("169.254."):
        return True
    if ip.startswith("fc") or ip.startswith("fd"):  # IPv6 ULA
        return True
    # 172.16.0.0 – 172.31.255.255
    if ip.startswith("172."):
        try:
            second = int(ip.split(".")[1])
            if 16 <= second <= 31:
                return True
        except Exception:
            pass
    return False


def is_loopback_client(
    headers: Optional[Mapping[str, str]] = None,
    client_address: Optional[Tuple] = None,
) -> bool:
    """True only for direct local browser/Electron — not Cloudflare tunnel users.

    cloudflared connects as 127.0.0.1 but sets CF-Connecting-IP / X-Forwarded-For
    to the real remote client. Presence of those headers means NOT local.
    """
    headers = headers or {}
    # Tunnel / reverse-proxy: real client is remote
    for key in (
        "CF-Connecting-IP",
        "cf-connecting-ip",
        "Cf-Connecting-Ip",
        "X-Forwarded-For",
        "x-forwarded-for",
        "X-Real-IP",
        "x-real-ip",
    ):
        if (headers.get(key) or "").strip():
            return False
    peer = ""
    if client_address:
        peer = str(client_address[0] or "")
    return peer in ("127.0.0.1", "::1", "localhost", "::ffff:127.0.0.1")


def is_home_lan_client(
    headers: Optional[Mapping[str, str]] = None,
    client_address: Optional[Tuple] = None,
) -> bool:
    """Loopback or same private Wi‑Fi/LAN (phone ↔ desk on home network).

    Still blocks public internet and Cloudflare tunnel users (CF headers present).
    """
    if is_loopback_client(headers, client_address):
        return True
    headers = headers or {}
    for key in (
        "CF-Connecting-IP",
        "cf-connecting-ip",
        "Cf-Connecting-Ip",
        "X-Forwarded-For",
        "x-forwarded-for",
        "X-Real-IP",
        "x-real-ip",
    ):
        if (headers.get(key) or "").strip():
            return False
    peer = ""
    if client_address:
        peer = str(client_address[0] or "")
    return _is_private_ip(peer)


def auth_summary() -> dict:
    return {
        "enabled": True,
        "user": _AUTH.user,
        "file": str(_AUTH.source),
        "note_file": str(ACCESS_NOTE),
        "public_lock": public_lock_enabled(),
        "always_public": sorted(ALWAYS_PUBLIC_PATHS),
        "local_public": sorted(LOCAL_PUBLIC_PATHS),
        "public_paths": sorted(PUBLIC_PATHS),
        "hint": "Send Authorization: Basic … or header X-Pocket-Access: <password>",
        "remote_policy": "desk/phone require login when not on this PC",
    }


def expected_user() -> str:
    return _AUTH.user


def expected_password() -> str:
    return _AUTH.password


def path_is_public(
    path: str,
    headers: Optional[Mapping[str, str]] = None,
    client_address: Optional[Tuple] = None,
) -> bool:
    """Whether this path may be served without credentials.

    Remote (public URL) clients only get ALWAYS_PUBLIC paths.
    Loopback clients also get LOCAL_PUBLIC shells (desk on this PC).
    Set POCKET_PUBLIC_LOCK=0 to treat LOCAL_PUBLIC as always public (legacy).
    """
    raw = (path or "/").split("?")[0] or "/"
    p = raw.rstrip("/") or "/"
    check = raw if raw.startswith("/") else f"/{raw}"

    for pref in PUBLIC_PREFIXES:
        if check.startswith(pref):
            return True

    if p in ALWAYS_PUBLIC_PATHS or check in ALWAYS_PUBLIC_PATHS:
        return True

    # Local preview iframes (and similar) — loopback / home LAN only, never public internet
    for pref in LOCAL_PUBLIC_PREFIXES:
        if check.startswith(pref):
            if not public_lock_enabled():
                return True
            return is_home_lan_client(headers, client_address)

    local_shell = p in LOCAL_PUBLIC_PATHS or check in LOCAL_PUBLIC_PATHS
    if not local_shell:
        # legacy: full PUBLIC_PATHS union without lock context
        if not public_lock_enabled() and (p in PUBLIC_PATHS or check in PUBLIC_PATHS):
            return True
        return False

    # App shell: this PC + same-WiFi phone; remote public only if lock disabled
    if not public_lock_enabled():
        return True
    return is_home_lan_client(headers, client_address)


def is_app_shell(path: str) -> bool:
    raw = (path or "/").split("?")[0] or "/"
    p = raw.rstrip("/") or "/"
    return p in APP_SHELL_PATHS or raw in APP_SHELL_PATHS


def public_gate_html(*, reason: str = "owner-only") -> str:
    """Sign-in page for visitors who are not in the workspace yet."""
    return """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Sign in · POCKET</title>
<style>
  :root { --bg:#09090b; --card:#141416; --fg:#fafafa; --muted:#a1a1aa; --accent:#10a37f; --line:rgba(255,255,255,.1); }
  * { box-sizing:border-box; }
  body { margin:0; min-height:100vh; font-family:ui-sans-serif,system-ui,Segoe UI,sans-serif;
    background:var(--bg); color:var(--fg);
    display:flex; align-items:center; justify-content:center; padding:24px; }
  .card { width:min(420px,100%); background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:28px 26px 24px; box-shadow:0 20px 60px #0006; }
  h1 { margin:0 0 8px; font-size:1.35rem; letter-spacing:-0.02em; }
  p { margin:0 0 12px; color:var(--muted); line-height:1.5; font-size:14px; }
  label { display:block; font-size:12px; color:var(--muted); margin:12px 0 6px; }
  input { width:100%; padding:10px 12px; border-radius:10px; border:1px solid var(--line);
    background:#0c0c0e; color:var(--fg); font-size:14px; }
  button { margin-top:16px; width:100%; padding:12px; border:0; border-radius:10px; cursor:pointer;
    background:var(--accent); color:#041; font-weight:700; font-size:14px; }
  button:hover { filter:brightness(1.05); }
  .err { color:#f87171; font-size:13px; min-height:1.2em; margin-top:10px; }
  .hint { font-size:12px; color:var(--muted); margin-top:14px; line-height:1.45; }
  a { color:var(--accent); }
</style></head><body>
<div class="card">
  <h1>Sign in to POCKET</h1>
  <p>This workspace is private. Use the account your admin gave you, or your own login if you already joined.</p>
  <form id="f" autocomplete="on">
    <label for="u">Username</label>
    <input id="u" name="username" value="pocket" autocomplete="username" placeholder="pocket"/>
    <label for="p">Password</label>
    <input id="p" name="password" type="password" autocomplete="current-password" placeholder="your password"/>
    <button type="submit" id="loginBtn">Continue</button>
  </form>
  <div class="err" id="e"></div>
  <p class="hint">New to this team? Ask your admin for an invite, then choose <strong>Join with invite</strong> in the app.
  <a href="/">Learn about POCKET</a></p>
</div>
<script src="/auth/client.js"></script>
<script>
(function(){
  try{
    if(sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')){
      location.replace('/desk?authed=1');
      return;
    }
  }catch(_){}
  function goDesk(){ location.replace('/desk?authed=1'); }
  if(window.PocketAuth&&PocketAuth.bindLoginForm){
    PocketAuth.bindLoginForm({
      userId:'u', passId:'p', btnId:'loginBtn', errId:'e', formId:'f',
      device:'public-gate', defaultUser:'pocket', onSuccess:goDesk
    });
  }else{
    document.getElementById('f').onsubmit=async function(ev){
      ev.preventDefault();
      var e=document.getElementById('e');
      e.textContent='Signing in…';
      try{
        var u=(document.getElementById('u').value||'').trim()||'pocket';
        var p=document.getElementById('p').value||'';
        var r=await fetch('/v1/auth/login',{method:'POST',credentials:'same-origin',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({username:u,user:u,password:p})});
        var j=await r.json().catch(function(){return {};});
        var tok=j.token||j.session_token||'';
        if(!r.ok||(!j.ok&&!tok)){ e.textContent=j.error||('Could not sign in ('+r.status+')'); return; }
        try{ sessionStorage.setItem('pocket_token',tok); localStorage.setItem('pocket_token',tok); }catch(_){}
        goDesk();
      }catch(err){ e.textContent=String(err.message||err); }
    };
  }
})();
</script>
</body></html>
"""


def _client_ip(headers: Mapping[str, str], client_address: Optional[Tuple] = None) -> str:
    # Prefer CF / proxy headers only for rate-limit keying (not trust for auth)
    xff = headers.get("CF-Connecting-IP") or headers.get("cf-connecting-ip")
    if xff:
        return xff.strip()
    xff2 = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
    if xff2:
        return xff2.split(",")[0].strip()
    if client_address:
        return str(client_address[0])
    return "unknown"


def is_rate_limited(ip: str) -> bool:
    now = time.time()
    with _fail_lock:
        hits = [t for t in _fail_log.get(ip, []) if now - t < FAIL_WINDOW]
        _fail_log[ip] = hits
        return len(hits) >= MAX_FAILS


def record_auth_failure(ip: str) -> None:
    with _fail_lock:
        _fail_log[ip].append(time.time())


def clear_auth_failures(ip: str) -> None:
    with _fail_lock:
        _fail_log.pop(ip, None)


def clear_all_auth_failures() -> int:
    """Operator recovery after local live-test lockouts."""
    with _fail_lock:
        n = len(_fail_log)
        _fail_log.clear()
    return n


def session_token_from_headers(headers: Mapping[str, str]) -> str:
    """Resolve session token from headers or Cookie (web navigation)."""
    sess = (
        headers.get("X-Pocket-Token")
        or headers.get("x-pocket-token")
        or ""
    ).strip()
    if sess:
        return sess
    try:
        from pocket.api_keys import extract_bearer

        raw = extract_bearer(headers) or ""
        # session tokens are opaque; API keys use sk_pocket_ prefix
        if raw and not raw.startswith("sk_pocket_"):
            return raw.strip()
    except Exception:
        pass
    # Cookie set on /v1/auth/login so plain GET /desk after gate works on Cloudflare
    cookie = headers.get("Cookie") or headers.get("cookie") or ""
    if cookie:
        for part in cookie.split(";"):
            part = part.strip()
            if part.lower().startswith("pocket_session="):
                return part.split("=", 1)[-1].strip()
            if part.lower().startswith("pocket_token="):
                return part.split("=", 1)[-1].strip()
    return ""


def is_authorized(headers: Mapping[str, str]) -> bool:
    # Multi-user session token first (header / Bearer / cookie)
    sess = session_token_from_headers(headers)
    if sess:
        try:
            from pocket.users import user_from_token

            if user_from_token(sess.strip()):
                return True
        except Exception:
            pass

    # Sellable AI API keys (Bearer sk_pocket_… or X-API-Key)
    # Also accept Bearer session tokens (non sk_pocket_) via user_from_token
    try:
        from pocket.api_keys import extract_bearer, verify_key

        raw_key = extract_bearer(headers)
        if raw_key and raw_key.startswith("sk_pocket_") and verify_key(raw_key):
            return True
        if raw_key and not raw_key.startswith("sk_pocket_"):
            from pocket.users import user_from_token

            if user_from_token(raw_key.strip()):
                return True
    except Exception:
        pass

    candidate = headers.get("Authorization") or headers.get("authorization") or ""
    if candidate.startswith("Basic "):
        try:
            raw = base64.b64decode(candidate[6:].strip()).decode("utf-8")
            user, password = raw.split(":", 1)
        except Exception:
            return False
        # multi-user table OR legacy single password
        try:
            from pocket.users import verify

            if verify(user, password):
                return True
        except Exception:
            pass
        return hmac.compare_digest(user, _AUTH.user) and hmac.compare_digest(
            password, _AUTH.password
        )

    token = headers.get("X-Pocket-Access") or headers.get("x-pocket-access") or ""
    if token:
        if hmac.compare_digest(token.strip(), _AUTH.password):
            return True
        # treat access header as session token fallback
        try:
            from pocket.users import user_from_token

            if user_from_token(token.strip()):
                return True
        except Exception:
            pass

    return False


def current_user(headers: Mapping[str, str]) -> Optional[dict]:
    """Return logged-in user record if any."""
    sess = headers.get("X-Pocket-Token") or headers.get("x-pocket-token") or ""
    if sess:
        try:
            from pocket.users import user_from_token

            u = user_from_token(sess.strip())
            if u:
                return u
        except Exception:
            pass
    candidate = headers.get("Authorization") or headers.get("authorization") or ""
    if candidate.startswith("Basic "):
        try:
            raw = base64.b64decode(candidate[6:].strip()).decode("utf-8")
            user, password = raw.split(":", 1)
            from pocket.users import verify

            return verify(user, password)
        except Exception:
            return {"user": _AUTH.user, "role": "admin", "display": "Operator"}
    return None


def security_headers() -> list[tuple[str, str]]:
    return [
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
        ("Referrer-Policy", "no-referrer"),
        ("Cache-Control", "no-store"),
        ("X-Permitted-Cross-Domain-Policies", "none"),
        ("Cross-Origin-Opener-Policy", "same-origin"),
        ("Cross-Origin-Resource-Policy", "same-site"),
        # CSP for the app UI — tight default; inline needed for single-file desk/phone
        (
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; connect-src 'self'; "
            "media-src 'self' blob:; frame-src 'self'; frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'; object-src 'none'",
        ),
        # mic allowed for voice-to-text in desk UI
        (
            "Permissions-Policy",
            "camera=(), microphone=(self), geolocation=(), payment=(), usb=(), interest-cohort=()",
        ),
        ("X-Pocket-License", "Researcher-1.0"),
    ]
