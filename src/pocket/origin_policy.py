"""Exact-origin trust. Hostname wildcards never confer authority.

Allowed hosts are the request Host (exact), loopback/LAN, the configured
public URL hostname, and an explicit POCKET_ALLOWED_ORIGINS list.
Sibling subdomains (*.medinatechlabs.net, *.trycloudflare.com) are not trusted.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Set
from urllib.parse import urlparse


def _host_only(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return ""
    if "://" not in s:
        s = "https://" + s
    h = (urlparse(s).hostname or "").lower()
    return h


def configured_hosts() -> Set[str]:
    hosts: Set[str] = {"127.0.0.1", "localhost"}
    pub = os.environ.get("POCKET_PUBLIC_URL") or "https://pocket.medinatechlabs.net"
    ph = _host_only(pub)
    if ph:
        hosts.add(ph)
    extra = os.environ.get("POCKET_ALLOWED_ORIGINS") or ""
    for part in extra.split(","):
        h = _host_only(part)
        if h:
            hosts.add(h)
    return hosts


def is_loopback_or_lan(host: str) -> bool:
    h = (host or "").split(":")[0].strip().lower()
    if h in ("127.0.0.1", "localhost", "::1"):
        return True
    if h.startswith("192.168.") or h.startswith("10."):
        return True
    if h.startswith("172."):
        try:
            n = int(h.split(".")[1])
            if 16 <= n <= 31:
                return True
        except Exception:
            pass
    return False


def rp_id_for_host(host: str) -> str:
    """WebAuthn rpId is the exact host. Never collapse to a parent domain."""
    h = (host or "").split(":")[0].strip().lower()
    return h or "localhost"


def origin_host(origin: str) -> str:
    return _host_only(origin)


def origin_allowed(origin: str, host: str, *, extra: Iterable[str] = ()) -> bool:
    o = (origin or "").strip()
    if not o:
        return False
    oh = origin_host(o)
    if not oh:
        return False
    hh = (host or "").split(":")[0].strip().lower()
    if oh == hh:
        return True
    if is_loopback_or_lan(oh):
        return True
    allowed = configured_hosts()
    for item in extra:
        h = _host_only(item)
        if h:
            allowed.add(h)
    return oh in allowed


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.origin.v1",
        "hosts": sorted(configured_hosts()),
        "wildcards": False,
        "rpId": "exact-request-host",
        "env": ["POCKET_PUBLIC_URL", "POCKET_ALLOWED_ORIGINS"],
    }
