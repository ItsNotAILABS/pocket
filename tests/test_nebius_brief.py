"""Nebius brief surface — grounding, fallback honesty, approval boundary.

No network and no key here: the configured path is exercised by stubbing
pocket.nebius_api's chat/status (nebius_brief imports them per-call), and
the unconfigured path must produce a deterministic local brief that is
labeled as a fallback — never a fake model answer.
"""

import pytest

import pocket.nebius_api as nebius_api
from pocket.nebius_brief import daily_brief, explain_approval

FACTS = ["Owner is at work until 14:00 CDT.", "KILN daemon recovered at 09:12."]
PENDING = [
    {
        "device_id": "phone-1",
        "app_id": "nuntius",
        "scope": "messages:send",
        "capability": "send_message",
        "requested_by": "phone-agent",
        "note": "reply to Rico",
        "expires_at_iso": "2026-10-28T17:00:00Z",
    }
]


@pytest.fixture(autouse=True)
def _no_key(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.nebius_api.CFG", tmp_path / "nebius.json")
    monkeypatch.setattr("pocket.nebius_api.ROOT", tmp_path)
    for var in ("NEBIUS_API_KEY", "NEBIUS_BASE_URL", "NEBIUS_MODEL"):
        monkeypatch.delenv(var, raising=False)


def test_daily_brief_fallback_is_labeled_and_grounded():
    r = daily_brief(FACTS, PENDING)
    assert r["ok"] is True
    assert r["engine"] == "local-fallback"
    assert r["fallback_reason"] == "nebius-not-configured"
    assert r["facts_used"] == 2
    assert r["pending_count"] == 1
    assert "KILN daemon recovered at 09:12." in r["brief"]
    assert "send_message" in r["brief"]
    assert "short-code" in r["approval_boundary"]


def test_daily_brief_configured_path_uses_nebius(monkeypatch):
    captured = {}

    def fake_status():
        return {"configured": True}

    def fake_chat(prompt, **kw):
        captured["prompt"] = prompt
        captured["system"] = kw.get("system") or ""
        return {"ok": True, "via": "mock", "model": "nvidia/nemotron-3-nano-30b-a3b", "reply": "Nemotron brief.", "usage": {"total_tokens": 42}}

    monkeypatch.setattr(nebius_api, "status", fake_status)
    monkeypatch.setattr(nebius_api, "chat", fake_chat)
    r = daily_brief(FACTS, PENDING)
    assert r["engine"] == "nebius"
    assert r["brief"] == "Nemotron brief."
    assert r["model"] == "nvidia/nemotron-3-nano-30b-a3b"
    # grounding: the facts and the pending request are in the prompt verbatim
    assert "KILN daemon recovered at 09:12." in captured["prompt"]
    assert "send_message" in captured["prompt"]
    assert "ONLY the facts" in captured["system"]


def test_daily_brief_call_failure_falls_back_honestly(monkeypatch):
    monkeypatch.setattr(nebius_api, "status", lambda: {"configured": True})
    monkeypatch.setattr(nebius_api, "chat", lambda prompt, **kw: {"ok": False, "error": "boom"})
    r = daily_brief(FACTS, [])
    assert r["engine"] == "local-fallback"
    assert r["fallback_reason"].startswith("nebius-call-failed")
    assert "Owner is at work until 14:00 CDT." in r["brief"]


def test_explain_approval_fallback_names_consequence():
    r = explain_approval(PENDING[0])
    assert r["ok"] is True
    assert r["engine"] == "local-fallback"
    assert "send_message" in r["explanation"]
    assert "phone-agent" in r["explanation"]
    assert "short code" in r["explanation"]


def test_explain_approval_configured_path(monkeypatch):
    monkeypatch.setattr(nebius_api, "status", lambda: {"configured": True})
    monkeypatch.setattr(
        nebius_api,
        "chat",
        lambda prompt, **kw: {"ok": True, "via": "mock", "model": "m", "reply": "Plain explanation.", "usage": {}},
    )
    r = explain_approval(PENDING[0])
    assert r["engine"] == "nebius"
    assert r["explanation"] == "Plain explanation."


def test_explain_approval_rejects_non_dict():
    r = explain_approval("not-a-dict")
    assert r["ok"] is False
