"""RevenueCat adapter — no live network."""

import uuid

from pocket.revenuecat import PLANS, handle_webhook, status, verify_webhook_auth


def test_status_unconfigured():
    st = status()
    assert st["ok"] is True
    assert st["provider"] == "revenuecat"
    assert "pocket_pro" in PLANS
    assert st["surfaces"]["webhook"]


def test_webhook_rejects_without_auth(monkeypatch):
    monkeypatch.delenv("REVENUECAT_WEBHOOK_AUTH", raising=False)
    monkeypatch.delenv("REVENUECAT_WEBHOOK_TOKEN", raising=False)
    out = handle_webhook({"event": {"type": "INITIAL_PURCHASE", "id": "evt_x"}}, authorization="")
    assert out["ok"] is False
    assert out.get("status") == 401


def test_webhook_accepts_matching_token(monkeypatch, tmp_path):
    monkeypatch.setenv("REVENUECAT_WEBHOOK_AUTH", "test-hook-secret")
    monkeypatch.delenv("REVENUECAT_API_KEY", raising=False)
    eid = "evt_" + uuid.uuid4().hex
    payload = {
        "event": {
            "type": "CANCELLATION",
            "id": eid,
            "app_user_id": "user_demo",
            "entitlement_ids": ["pocket_pro"],
        }
    }
    out = handle_webhook(payload, authorization="Bearer test-hook-secret")
    assert out["ok"] is True
    assert out.get("type") == "CANCELLATION" or out.get("duplicate")
    dup = handle_webhook(payload, authorization="test-hook-secret")
    assert dup.get("duplicate") is True


def test_verify_webhook_auth(monkeypatch):
    monkeypatch.setenv("REVENUECAT_WEBHOOK_AUTH", "abc")
    assert verify_webhook_auth("Bearer abc") is True
    assert verify_webhook_auth("abc") is True
    assert verify_webhook_auth("nope") is False
