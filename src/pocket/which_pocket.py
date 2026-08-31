"""Two POCKET products — not two faces of one window.

  POCKET Owner        = your machine on :8787
  POCKET for Users    = customer product on :8788 (local test) or the public host

They do not share a port, a launcher, or a login screen.
"""

from __future__ import annotations

import ipaddress
from typing import Any, Dict

from pocket.edition import (
    is_founder,
    marketing_url,
    owner_url,
    product_id,
    users_local_url,
)


OPERATOR_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "[::1]"})


def host_name(host_header: str) -> str:
    h = (host_header or "").strip().lower()
    if h.startswith("["):
        end = h.find("]")
        inner = h[1:end] if end > 0 else h.strip("[]")
        return inner
    return h.split(":", 1)[0]


def _is_private_host(name: str) -> bool:
    if not name or name in OPERATOR_HOSTS:
        return True
    try:
        ip = ipaddress.ip_address(name)
    except ValueError:
        return False
    return bool(ip.is_private or ip.is_loopback or ip.is_link_local)


def request_face(host_header: str) -> str:
    """Kept for tests. Prefer product_id() — these are two products now."""
    return "operator" if product_id() == "owner" else "public"


def is_operator_face(host_header: str) -> bool:
    return product_id() == "owner"


def is_loopback_host(host_header: str) -> bool:
    name = host_name(host_header)
    if name in OPERATOR_HOSTS:
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        return False


def summary(host_header: str = "") -> Dict[str, Any]:
    product = product_id()
    owner = owner_url().rstrip("/")
    users_local = users_local_url().rstrip("/")
    users_public = marketing_url().rstrip("/")
    here = host_name(host_header) if host_header else ""
    return {
        "ok": True,
        "product": product,
        "face": "operator" if product == "owner" else "public",
        "host": here,
        "loopback": is_loopback_host(host_header) if host_header else True,
        "lan": False,
        "separated": True,
        "your_pocket": {
            "product": "POCKET Owner",
            "name": "POCKET Owner",
            "who": "You — this machine only",
            "url": owner + "/desk",
            "which": owner + "/which",
            "port": 8787,
            "shortcut": "POCKET Owner",
            "electron_role": "operator",
            "profile": r"%APPDATA%\POCKET-Owner",
            "edition": "founder",
            "files": "this machine (host power)",
            "chrome": "gold · YOUR POCKET",
        },
        "user_facing": {
            "product": "POCKET for Users",
            "name": "POCKET for Users",
            "who": "Customers / invite seats",
            "url": users_public + "/join",
            "desk": users_local + "/desk",
            "join_here": users_local + "/join",
            "which": users_local + "/which",
            "port": 8788,
            "shortcut": "POCKET for Users",
            "electron_role": "user",
            "profile": r"%APPDATA%\POCKET-User",
            "files": r"~/.pocket/tenants/<user>/ only",
            "chrome": "green · POCKET FOR USERS",
        },
        "rule": (
            "These are two products. POCKET Owner is :8787 on this PC. "
            "POCKET for Users is :8788 (local test) or the public host. "
            "They do not share a window, a port, or a login."
        ),
        "founder": is_founder(),
    }


def which_html(host_header: str = "") -> str:
    data = summary(host_header)
    mine = data["your_pocket"]
    users = data["user_facing"]
    on_owner = data["product"] == "owner"
    banner = (
        "This process is POCKET Owner (:8787). Users are a different product on :8788."
        if on_owner
        else "This process is POCKET for Users (:8788). Your machine desk is the other product on :8787."
    )
    you_mine = " you-are-here" if on_owner else ""
    you_users = "" if on_owner else " you-are-here"
    title = "POCKET Owner" if on_owner else "POCKET for Users"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title} · two products</title>
<style>
:root{{--bg:#07070b;--line:rgba(255,255,255,.08);--text:#e4e4e7;--muted:#9b9ba8;--fg:#fafafa;--gold:#eab308;--teal:#10a37f}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,Segoe UI,sans-serif;background:
  radial-gradient(900px 420px at 0% -10%,rgba(234,179,8,.09),transparent 50%),
  radial-gradient(800px 380px at 100% 0%,rgba(16,163,127,.1),transparent 46%),var(--bg);
  color:var(--text);line-height:1.5}}
.banner{{padding:13px 22px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;font-size:11.5px;border-bottom:1px solid var(--line)}}
.banner.mine{{background:rgba(234,179,8,.16);color:#fbbf24}}
.banner.users{{background:rgba(16,163,127,.14);color:#6ee7b7}}
.wrap{{max-width:1040px;margin:0 auto;padding:36px 22px 88px}}
h1{{margin:0 0 8px;font-size:clamp(26px,4vw,34px);letter-spacing:-.045em;color:var(--fg)}}
.lead{{color:var(--muted);max-width:720px;margin:0 0 26px;font-size:15px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}
.card{{border:1px solid var(--line);border-radius:18px;padding:22px;background:rgba(18,18,24,.92);min-height:300px;display:flex;flex-direction:column;position:relative;opacity:.55}}
.card.you-are-here{{opacity:1}}
.card.mine.you-are-here{{box-shadow:0 0 0 1px rgba(234,179,8,.45),0 18px 44px rgba(0,0,0,.4)}}
.card.users.you-are-here{{box-shadow:0 0 0 1px rgba(16,163,127,.45),0 18px 44px rgba(0,0,0,.4)}}
.here{{position:absolute;top:14px;right:14px;font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:4px 8px;border-radius:999px}}
.mine .here{{background:rgba(234,179,8,.18);color:#fbbf24}}
.users .here{{background:rgba(16,163,127,.18);color:#6ee7b7}}
.kicker{{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin:0 0 8px}}
.card.mine .kicker{{color:#fbbf24}}
.card.users .kicker{{color:#34d399}}
h2{{margin:0 0 8px;font-size:24px;letter-spacing:-.03em;color:var(--fg)}}
.port{{font-variant-numeric:tabular-nums;font-weight:800}}
.who{{margin:0 0 6px;color:var(--muted);font-size:14px}}
dl{{margin:8px 0 0;font-size:13px}}
dt{{color:var(--muted);margin-top:10px;font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
dd{{margin:2px 0 0;color:var(--fg);word-break:break-all}}
.actions{{margin-top:auto;padding-top:18px;display:flex;gap:8px;flex-wrap:wrap}}
a.go{{display:inline-flex;padding:10px 14px;border-radius:10px;font-weight:700;font-size:13px;text-decoration:none}}
.mine a.go{{background:var(--gold);color:#1c1400}}
.users a.go{{background:var(--teal);color:#041}}
a.ghost{{color:var(--muted);font-size:13px;align-self:center}}
.rule{{margin:28px 0 0;padding:14px 16px;border-radius:12px;border:1px solid var(--line);color:var(--muted);font-size:13.5px}}
</style>
</head>
<body>
<div class="banner {"mine" if on_owner else "users"}">{banner}</div>
<div class="wrap">
  <h1>Two products. Not two modes.</h1>
  <p class="lead">{data["rule"]}</p>
  <div class="grid">
    <article class="card mine{you_mine}">
      {"<span class='here'>This process</span>" if on_owner else ""}
      <p class="kicker">Yours</p>
      <h2>{mine["name"]}</h2>
      <p class="who">{mine["who"]}</p>
      <dl>
        <dt>Port</dt><dd class="port">:{mine["port"]}</dd>
        <dt>Open</dt><dd>{mine["url"]}</dd>
        <dt>Shortcut</dt><dd>{mine["shortcut"]}</dd>
        <dt>Files</dt><dd>{mine["files"]}</dd>
      </dl>
      <div class="actions">
        <a class="go" href="{mine["url"]}">Open Owner desk</a>
      </div>
    </article>
    <article class="card users{you_users}">
      {"" if on_owner else "<span class='here'>This process</span>"}
      <p class="kicker">Customers</p>
      <h2>{users["name"]}</h2>
      <p class="who">{users["who"]}</p>
      <dl>
        <dt>Port</dt><dd class="port">:{users["port"]}</dd>
        <dt>Local test</dt><dd>{users["desk"]}</dd>
        <dt>Public</dt><dd>{users["url"]}</dd>
        <dt>Shortcut</dt><dd>{users["shortcut"]}</dd>
        <dt>Files</dt><dd>{users["files"]}</dd>
      </dl>
      <div class="actions">
        <a class="go" href="{users["join_here"]}">Open Users product</a>
      </div>
    </article>
  </div>
  <p class="rule">Do not tunnel :8787 to the customer hostname. Owner stays on this PC. Users is :8788 or the public host. Shortcut <b>POCKET Owner</b> vs <b>POCKET for Users</b>.</p>
</div>
</body>
</html>"""
