"""Consequence-layer gate for host observation, input, shell, and persistence.

HTTP routes must still authenticate. This module is what agent tools and
internal callers hit so a forgotten public path cannot run PowerShell or
touch the desktop.

Visual Portal (frames/touch) may use LAN, a signed-in seat, Face ID, or the
Portal session cookie minted after Face ID / LAN. Shell, harness, eyes-touch,
runtime install, and vault push never accept the Portal cookie alone.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

VISUAL = frozenset({"observe", "input", "portal"})
EXEC = frozenset({"shell", "harness", "install", "eyes", "webmcp", "vault", "settings"})


def allow(
    *,
    headers=None,
    client_address=None,
    query: Optional[Dict[str, Any]] = None,
    consequence: str = "observe",
) -> Dict[str, Any]:
    from pocket.auth import current_user, is_home_lan_client
    from pocket.phoneai_portal import check_portal_token, token_from_headers

    kind = (consequence or "observe").lower()
    if is_home_lan_client(headers, client_address):
        return {"ok": True, "via": "lan"}
    user = None
    try:
        rec = current_user(headers or {})
        if rec:
            user = rec.get("user")
    except Exception:
        user = None
    if user:
        return {"ok": True, "via": "seat", "user": user}
    try:
        from pocket.passkey import session_user

        face = session_user(headers)
        if face:
            return {"ok": True, "via": "face", "user": face}
    except Exception:
        pass
    if kind in VISUAL or kind == "observe" or kind == "input" or kind == "portal":
        tok = token_from_headers(headers, query)
        if tok and check_portal_token(tok):
            return {"ok": True, "via": "portal-cookie"}
        return {
            "ok": False,
            "error": "Unlock with Face ID, use home Wi-Fi, or sign in. Anonymous tunnel cannot see or drive this PC.",
        }
    return {
        "ok": False,
        "error": "Host control (shell, install, agent eyes, vault) needs home Wi-Fi, Face ID, or a signed-in seat — not a public URL alone.",
    }
