from pocket.phoneai_settings import OPTIONAL, snapshot
from pocket.phone_life import classify


def test_optional_clis_are_settings():
    assert {"opencode", "cursor", "aider", "copilot"} <= set(OPTIONAL)
    snap = snapshot()
    ids = {t["id"] for t in snap["tools"]}
    assert {"opencode", "cursor", "aider", "copilot"} <= ids
    assert snap.get("chat") == "grok"


def test_chat_not_life_for_plain_ask():
    assert classify("what should I eat tonight") == "chat"
    assert classify("remind me to stretch") == "remind"
