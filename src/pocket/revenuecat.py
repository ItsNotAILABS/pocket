"""RevenueCat billing adapter for POCKET.

Doctrine
--------
RevenueCat is the *paid subscription source of truth*.
POCK is the *usage meter*. They are not the same thing.

  App Store / Play / Web Billing / Stripe  →  RevenueCat
       │
       ├─ webhook  POST /v1/billing/webhook
       └─ REST     GET  /v1/subscribers/{app_user_id}
              │
              ▼
       POCKET host
         · grant entitlements (pro / team / api)
         · mint POCK on INITIAL_PURCHASE / RENEWAL / NON_RENEWING_PURCHASE
         · revoke on EXPIRATION / REFUND
         · never auto-pay; checkout is user-initiated

Do **not** embed purchases-ios / purchases-android in this Python host.
Those SDKs live in a future native phone / store build.
This module is: REST + webhook + Web Billing page (`/billing`).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
BILLING_DIR = ROOT / "billing"
STATE_FILE = BILLING_DIR / "revenuecat.json"
_lock = Lock()

SCHEMA = "pocket.billing.revenuecat.v1"
RC_V1 = "https://api.revenuecat.com/v1"

try:
    from itsnotai_internal.billing_sdk import CANONICAL_PLANS, SCHEMA as _SHARED_SCHEMA

    SCHEMA = _SHARED_SCHEMA
    PLANS: Dict[str, Dict[str, Any]] = CANONICAL_PLANS
except Exception:
    # Entitlement id in RevenueCat dashboard  →  what POCKET grants
    PLANS = {
        "pocket_starter": {
            "name": "Starter",
            "seats": 1,
            "pock_monthly": 10_000,
            "edition": "market",
            "api_tier": "starter",
            "usd": 29,
        },
        "pocket_pro": {
            "name": "Pro",
            "seats": 5,
            "pock_monthly": 50_000,
            "edition": "company",
            "api_tier": "pro",
            "usd": 99,
        },
        "pocket_team": {
            "name": "Team",
            "seats": 20,
            "pock_monthly": 200_000,
            "edition": "company",
            "api_tier": "enterprise",
            "usd": 299,
        },
        "pock_refill": {
            "name": "POCK refill",
            "seats": 0,
            "pock_once": 50_000,
            "consumable": True,
            "api_tier": "",
            "usd": 19,
        },
    }

# Events that should mint monthly/consumable credits (once per event id)
MINT_EVENTS = {
    "INITIAL_PURCHASE",
    "RENEWAL",
    "NON_RENEWING_PURCHASE",
    "PRODUCT_CHANGE",
    "UNCANCELLATION",
}
REVOKE_EVENTS = {"EXPIRATION", "CANCELLATION", "BILLING_ISSUE", "REFUND"}


def _empty_state() -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "app_user_id": "",
        "entitlements": {},
        "plan": "",
        "seats": 0,
        "api_tier": "",
        "events": [],
        "seen_event_ids": [],
        "last_sync": 0,
        "last_error": "",
    }


def _load() -> Dict[str, Any]:
    BILLING_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.is_file():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                base = _empty_state()
                base.update(data)
                return base
        except Exception:
            pass
    return _empty_state()


def _save(st: Dict[str, Any]) -> None:
    BILLING_DIR.mkdir(parents=True, exist_ok=True)
    ev = st.get("events") or []
    if len(ev) > 80:
        st["events"] = ev[-80:]
    seen = st.get("seen_event_ids") or []
    if len(seen) > 400:
        st["seen_event_ids"] = seen[-400:]
    STATE_FILE.write_text(json.dumps(st, indent=2), encoding="utf-8")


def config() -> Dict[str, Any]:
    secret = (os.environ.get("REVENUECAT_API_KEY") or os.environ.get("REVENUECAT_SECRET_KEY") or "").strip()
    public = (os.environ.get("REVENUECAT_PUBLIC_API_KEY") or os.environ.get("REVENUECAT_WEB_KEY") or "").strip()
    hook = (os.environ.get("REVENUECAT_WEBHOOK_AUTH") or os.environ.get("REVENUECAT_WEBHOOK_TOKEN") or "").strip()
    app_id = (os.environ.get("REVENUECAT_APP_ID") or "").strip()
    project = (os.environ.get("REVENUECAT_PROJECT_ID") or "").strip()
    return {
        "ok": True,
        "configured": bool(secret or public),
        "rest_ready": bool(secret),
        "web_billing_ready": bool(public),
        "webhook_ready": bool(hook),
        "has_secret_key": bool(secret),
        "has_public_key": bool(public),
        "has_webhook_auth": bool(hook),
        "app_id": app_id,
        "project_id": project,
        "public_api_key": public,
        "env_hint": [
            "REVENUECAT_API_KEY=sk_…          # secret REST (server only)",
            "REVENUECAT_PUBLIC_API_KEY=pk_…  # Web Billing (Purchases.js)",
            "REVENUECAT_WEBHOOK_AUTH=…       # Authorization header RC sends",
            "REVENUECAT_APP_ID=app…          # optional",
        ],
    }


def verify_webhook_auth(header_value: str) -> bool:
    """RevenueCat dashboard → Authorization header value (Bearer optional)."""
    expected = (os.environ.get("REVENUECAT_WEBHOOK_AUTH") or os.environ.get("REVENUECAT_WEBHOOK_TOKEN") or "").strip()
    if not expected:
        # Unconfigured: refuse live money events
        return False
    got = (header_value or "").strip()
    if got.lower().startswith("bearer "):
        got = got[7:].strip()
    exp = expected
    if exp.lower().startswith("bearer "):
        exp = exp[7:].strip()
    if len(got) != len(exp):
        return False
    return hmac.compare_digest(got, exp)


def _rc_get(path: str) -> Dict[str, Any]:
    key = (os.environ.get("REVENUECAT_API_KEY") or os.environ.get("REVENUECAT_SECRET_KEY") or "").strip()
    if not key:
        return {"ok": False, "error": "REVENUECAT_API_KEY not set"}
    url = RC_V1 + path
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "X-Platform": "other",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "data": body}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "error": f"revenuecat {e.code}", "detail": raw}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def fetch_subscriber(app_user_id: str) -> Dict[str, Any]:
    uid = (app_user_id or "").strip()
    if not uid:
        return {"ok": False, "error": "app_user_id required"}
    res = _rc_get("/subscribers/" + urllib.parse.quote(uid, safe=""))
    if not res.get("ok"):
        return res
    sub = ((res.get("data") or {}).get("subscriber") or res.get("data") or {})
    ents = sub.get("entitlements") or {}
    active: List[str] = []
    now = time.time() * 1000
    for eid, ent in ents.items():
        exp = ent.get("expires_date")
        # Active if no expiry or expiry in the future (ISO) — also accept expires_date_ms
        exp_ms = ent.get("expires_date_ms")
        live = True
        if exp_ms is not None:
            try:
                live = float(exp_ms) > now
            except Exception:
                live = True
        if live:
            active.append(str(eid))
    return {
        "ok": True,
        "app_user_id": uid,
        "entitlements": ents,
        "active": active,
        "subscriber": {
            "original_app_user_id": sub.get("original_app_user_id"),
            "first_seen": sub.get("first_seen"),
            "management_url": sub.get("management_url"),
        },
    }


def _best_plan(active: List[str]) -> str:
    order = ["pocket_team", "pocket_pro", "pocket_starter"]
    for p in order:
        if p in active:
            return p
    for a in active:
        if a in PLANS and not PLANS[a].get("consumable"):
            return a
    return ""


def _apply_plan(st: Dict[str, Any], active: List[str]) -> None:
    plan = _best_plan(active)
    spec = PLANS.get(plan) or {}
    st["plan"] = plan
    st["seats"] = int(spec.get("seats") or 0)
    st["api_tier"] = str(spec.get("api_tier") or "")
    st["entitlements"] = {k: True for k in active}


def _mint_pock(amount: int, *, reason: str, event_id: str) -> Optional[Dict[str, Any]]:
    amount = int(amount or 0)
    if amount <= 0:
        return None
    try:
        from pocket.tokenomics import mint

        return mint(amount, reason=reason)
    except Exception as e:
        return {"ok": False, "error": str(e)[:160], "event_id": event_id}


def apply_subscriber(app_user_id: str, *, source: str = "sync") -> Dict[str, Any]:
    fetched = fetch_subscriber(app_user_id)
    with _lock:
        st = _load()
        st["app_user_id"] = app_user_id
        st["last_sync"] = time.time()
        if not fetched.get("ok"):
            st["last_error"] = str(fetched.get("error") or "fetch failed")
            _save(st)
            return {**fetched, "state": snapshot_unlocked(st)}
        st["last_error"] = ""
        _apply_plan(st, list(fetched.get("active") or []))
        st.setdefault("events", []).append(
            {
                "id": f"sync-{int(time.time())}",
                "type": source,
                "active": fetched.get("active"),
                "plan": st.get("plan"),
                "at": time.time(),
            }
        )
        _save(st)
        return {"ok": True, "source": source, "active": fetched.get("active"), "state": snapshot_unlocked(st), "subscriber": fetched.get("subscriber")}


def handle_webhook(payload: Dict[str, Any], *, authorization: str = "") -> Dict[str, Any]:
    if not verify_webhook_auth(authorization):
        return {"ok": False, "error": "unauthorized webhook", "status": 401}

    event = payload.get("event") if isinstance(payload.get("event"), dict) else payload
    etype = str(event.get("type") or payload.get("type") or "").upper()
    app_user = str(event.get("app_user_id") or event.get("original_app_user_id") or "").strip()
    event_id = str(event.get("id") or event.get("event_timestamp_ms") or "")
    if not event_id:
        raw = json.dumps(event, sort_keys=True, default=str)
        event_id = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    product_id = str(event.get("product_id") or "")
    ent_ids = [str(x) for x in (event.get("entitlement_ids") or []) if x]

    mint_receipt = None
    with _lock:
        st = _load()
        seen = st.setdefault("seen_event_ids", [])
        if event_id in seen:
            return {"ok": True, "duplicate": True, "event_id": event_id, "state": snapshot_unlocked(st)}
        seen.append(event_id)
        if app_user:
            st["app_user_id"] = app_user

        # Prefer live subscriber snapshot when we have a key
        active = list(ent_ids)
        if app_user and (os.environ.get("REVENUECAT_API_KEY") or "").strip():
            fetched = fetch_subscriber(app_user)
            if fetched.get("ok"):
                active = list(fetched.get("active") or active)

        if etype in REVOKE_EVENTS and etype != "CANCELLATION":
            # Cancellation still has access until period end — keep plan, note it
            if etype in ("EXPIRATION", "REFUND"):
                st["plan"] = ""
                st["seats"] = 0
                st["api_tier"] = ""
                st["entitlements"] = {}
        else:
            _apply_plan(st, active)

        amount = 0
        reason = f"revenuecat:{etype.lower()}"
        if etype in MINT_EVENTS:
            if "pock_refill" in ent_ids or product_id.endswith("refill"):
                amount = int(PLANS["pock_refill"].get("pock_once") or 0)
                reason = "revenuecat_refill"
            else:
                plan = st.get("plan") or _best_plan(active)
                amount = int((PLANS.get(plan) or {}).get("pock_monthly") or 0)
                reason = f"revenuecat_{plan or 'grant'}"

        st.setdefault("events", []).append(
            {
                "id": event_id,
                "type": etype or "UNKNOWN",
                "app_user_id": app_user,
                "product_id": product_id,
                "entitlement_ids": ent_ids,
                "pock": amount,
                "at": time.time(),
            }
        )
        st["last_sync"] = time.time()
        _save(st)

    if amount > 0:
        mint_receipt = _mint_pock(amount, reason=reason, event_id=event_id)

    if app_user:
        try:
            from pocket.users import set_user_plan

            plan_id = (status().get("state") or {}).get("plan") or _best_plan(ent_ids)
            if etype in ("EXPIRATION", "REFUND"):
                plan_id = ""
            set_user_plan(app_user, plan_id, source=f"webhook:{etype.lower()}")
        except Exception:
            pass

    return {
        "ok": True,
        "event_id": event_id,
        "type": etype,
        "app_user_id": app_user,
        "mint": mint_receipt,
        "state": status(),
    }


def snapshot_unlocked(st: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "app_user_id": st.get("app_user_id") or "",
        "plan": st.get("plan") or "",
        "seats": int(st.get("seats") or 0),
        "api_tier": st.get("api_tier") or "",
        "entitlements": st.get("entitlements") or {},
        "last_sync": st.get("last_sync") or 0,
        "last_error": st.get("last_error") or "",
        "recent": list(reversed((st.get("events") or [])[-8:])),
    }


def status() -> Dict[str, Any]:
    cfg = config()
    with _lock:
        st = snapshot_unlocked(_load())
    return {
        "ok": True,
        "provider": "revenuecat",
        "doctrine": [
            "RevenueCat owns paid entitlements.",
            "POCK remains the local usage meter.",
            "Never auto-pay. Checkout is a user click.",
            "Native Purchases SDK stays in phone/store apps — host uses REST + webhooks.",
        ],
        "config": {k: v for k, v in cfg.items() if k != "public_api_key" or True},
        "plans": PLANS,
        "state": st,
        "surfaces": {
            "page": "/billing",
            "status": "GET /v1/billing",
            "sync": "POST /v1/billing/sync  {app_user_id}",
            "webhook": "POST /v1/billing/webhook",
        },
    }


def billing_html() -> str:
    cfg = config()
    pk = cfg.get("public_api_key") or ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · Billing</title>
<script src="/auth/client.js"></script>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.08);--text:#e4e4e7;--muted:#71717a;--fg:#fafafa;--accent:#10a37f;--ease:cubic-bezier(.22,1,.36,1)}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 420px at 8% -10%,rgba(16,163,127,.1),transparent 52%),var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}}
.pnav{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid var(--line);background:rgba(9,9,11,.78);backdrop-filter:blur(22px);position:sticky;top:0}}
.pnav a{{color:#a1a1aa;text-decoration:none;font-size:13px;padding:7px 11px;border-radius:8px}}
.pnav a.on,.pnav a:hover{{color:#fff;background:#1a1a1e}}
.brand{{display:flex;align-items:center;gap:8px;font-weight:700;color:#fff;text-decoration:none;margin-right:6px}}
.brand i{{width:22px;height:22px;border-radius:7px;background:linear-gradient(145deg,#34d399,#10a37f);display:grid;place-items:center;font-style:normal;color:#041;font-size:11px;font-weight:800}}
.wrap{{max-width:880px;margin:0 auto;padding:36px 18px 80px}}
h1{{letter-spacing:-.04em;margin:0 0 8px;color:var(--fg)}}
.lead{{color:var(--muted);max-width:560px;line-height:1.55}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:24px 0}}
.card{{border:1px solid var(--line);border-radius:16px;padding:18px;background:linear-gradient(165deg,rgba(255,255,255,.04),transparent 48%),var(--panel);transition:transform .2s var(--ease),box-shadow .2s}}
.card h3{{margin:0 0 6px;color:var(--fg)}}
.card p{{margin:0;font-size:13px;color:var(--muted);line-height:1.45}}
.price{{font-size:22px;font-weight:700;color:var(--fg);margin:10px 0 12px;letter-spacing:-.03em}}
.btn{{border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer;background:linear-gradient(180deg,#34d399,#10a37f);color:#041}}
.btn[disabled]{{opacity:.4;cursor:not-allowed}}
.note{{font-size:13px;color:var(--muted);border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:#0c0c0e}}
#st{{margin-top:18px;font-size:13px;color:var(--muted)}}
code{{font-size:12px;color:#86efac}}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/desk"><i>P</i>POCKET</a>
  <a href="/desk">Desk</a>
  <a class="on" href="/billing">Billing</a>
  <a href="/developers">API</a>
  <a href="/docs">Docs</a>
</header>
<main class="wrap">
  <h1>RevenueCat billing</h1>
  <p class="lead">Subscriptions live in RevenueCat. This host grants seats and mints POCK after a paid event. Nothing charges until you click.</p>
  <div class="grid">
    <div class="card"><h3>Starter</h3><p>1 seat · 10k POCK / month</p><div class="price">$29</div><button class="btn" data-ent="pocket_starter" disabled>Buy Starter</button></div>
    <div class="card"><h3>Pro</h3><p>5 seats · 50k POCK / month</p><div class="price">$99</div><button class="btn" data-ent="pocket_pro" disabled>Buy Pro</button></div>
    <div class="card"><h3>Team</h3><p>20 seats · 200k POCK / month</p><div class="price">$299</div><button class="btn" data-ent="pocket_team" disabled>Buy Team</button></div>
    <div class="card"><h3>POCK refill</h3><p>One-time 50k credits</p><div class="price">$19</div><button class="btn" data-ent="pock_refill" disabled>Buy refill</button></div>
  </div>
  <div class="note">
    Set <code>REVENUECAT_PUBLIC_API_KEY</code> + offerings in the RevenueCat dashboard to enable Web Billing.
    Point the webhook at <code>POST /v1/billing/webhook</code> with <code>REVENUECAT_WEBHOOK_AUTH</code>.
    Secret key stays on the host only.
  </div>
  <div id="st">Loading status…</div>
</main>
<script>
const PUBLIC_KEY = {json.dumps(pk)};
async function load() {{
  try {{
    const r = await fetch('/v1/billing', {{credentials:'same-origin'}});
    const j = await r.json();
    const s = j.state || {{}};
    document.getElementById('st').innerHTML =
      'Plan: <b style="color:#fafafa">' + (s.plan || 'none') + '</b> · seats ' + (s.seats||0) +
      ' · REST ' + (j.config && j.config.rest_ready ? 'ready' : 'not configured') +
      ' · webhook ' + (j.config && j.config.webhook_ready ? 'ready' : 'not configured');
  }} catch (e) {{
    document.getElementById('st').textContent = 'Sign in to see host entitlements.';
  }}
}}
load();
if (PUBLIC_KEY) {{
  document.querySelectorAll('.btn').forEach(b => {{ b.disabled = false; b.title = 'Opens RevenueCat Web Billing when offerings are mapped'; }});
}}
</script>
</body></html>
"""
