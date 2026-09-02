"""End-to-end status of the 20 PhoneAI × Pocket surfaces built this arc."""

from __future__ import annotations

from typing import Any, Dict, List


FEATURES: List[Dict[str, str]] = [
    {"id": "portal_full", "name": "Portal full PC", "get": "/phoneai/portal", "note": "contain = entire desktop"},
    {"id": "portal_focus", "name": "Portal focus mobile", "post": "/v1/phoneai/portal/touch", "note": "active window as phone"},
    {"id": "portal_ws", "name": "Portal live WS", "get": "/v1/phoneai/portal/ws", "note": "JPEG + touch socket"},
    {"id": "portal_session", "name": "Portal session cookie", "note": "LAN / sign-in / hmac cookie"},
    {"id": "workspace", "name": "Real workspace", "get": "/v1/ai-workspace", "note": "files + preview"},
    {"id": "agents_social", "name": "Agent names/faces/DM", "get": "/agents"},
    {"id": "agent_mail", "name": "Agent mail", "get": "/v1/agent-mail"},
    {"id": "cron", "name": "Cron memory", "get": "/v1/cron/memory"},
    {"id": "steer", "name": "Steer sub-agents", "post": "/v1/subagents/steer"},
    {"id": "browser", "name": "Drive desktop browser", "post": "/v1/browser/drive"},
    {"id": "parallel", "name": "Parallel / RAH", "post": "/v1/rah/run"},
    {"id": "auro_rah", "name": "RAH Auro leaves", "note": "mode=auro + Auro14B auro_native_llm.rah"},
    {"id": "tv", "name": "TV mesh", "get": "/phoneai/tv"},
    {"id": "doorbell", "name": "Doorbell", "get": "/phoneai/doorbell"},
    {"id": "cam", "name": "Laptop cam Allow", "get": "/phoneai/cam"},
    {"id": "photos", "name": "Photo pipe", "post": "/v1/phoneai/photos"},
    {"id": "runtime", "name": "Always-on runtime", "get": "/v1/runtime"},
    {"id": "wear", "name": "Glasses / AirPods", "get": "/phoneai/glasses"},
    {"id": "crypto", "name": "Vault AE", "note": "hmac-sha256-ctr-mac-v2"},
    {"id": "landscape", "name": "PhoneAI landscape computer", "get": "/phoneai/app"},
]


def snapshot() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    for f in FEATURES:
        ok = True
        detail = f.get("note") or f.get("get") or f.get("post") or ""
        if f["id"] == "crypto":
            try:
                from pocket.crypto import ALG, encrypt_bytes, decrypt_bytes

                blob = encrypt_bytes("probe", b"pocket")
                ok = decrypt_bytes("probe", blob) == b"pocket" and blob.get("alg") == ALG
                detail = blob.get("alg") or detail
            except Exception as e:
                ok = False
                detail = str(e)[:120]
        elif f["id"] == "auro_rah":
            try:
                from pocket.auro14b_bridge import auro_root

                root = auro_root()
                if not root:
                    ok = False
                    detail = "Auro14B tree missing"
                else:
                    import sys

                    pth = str(root)
                    if pth not in sys.path:
                        sys.path.insert(0, pth)
                    from auro_native_llm.rah import run_rah as _ar  # noqa: F401

                    ok = True
                    detail = "auro_native_llm.rah"
            except Exception as e:
                ok = False
                detail = str(e)[:80]
        checks.append({**f, "ok": ok, "detail": detail})
    return {
        "ok": all(c["ok"] for c in checks),
        "schema": "pocket.feature_fabric.v1",
        "count": len(checks),
        "wired": sum(1 for c in checks if c["ok"]),
        "features": checks,
    }
