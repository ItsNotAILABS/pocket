"""Per-being oaths / vows / laws."""

from pocket.being_doctrine import (
    BEINGS,
    COMMON_AI_OATH,
    being_brief,
    being_payload,
    catalog,
    get_being,
)


def test_roster_has_organism_engines_latin_solus():
    for bid in (
        "pocket-organism",
        "mini-heart",
        "mini-brain",
        "codex",
        "grok",
        "aria",
        "archon",
        "guppy",
        "aesthete",
        "solus",
        "logic-prover",
        "pattern-forge",
        "keep",
        "nexus-scribe",
    ):
        assert bid in BEINGS, bid
        b = BEINGS[bid]
        assert b["oath"] and b["vows"] and b["doctrine"]
        assert b["laws"]


def test_aliases_resolve():
    assert get_being("voice")["id"] == "aria"
    assert get_being("ARCHON")["id"] == "archon"
    assert get_being("fish")["id"] == "guppy"
    assert get_being("cipher")["id"] == "nexus-cipher"


def test_payload_and_catalog():
    c = catalog()
    assert c["ok"] and c["count"] == len(BEINGS)
    assert len(COMMON_AI_OATH) == 6
    p = being_payload("solus")
    assert p["ok"] and p["being"]["laws"][0]["id"] == "C-SOL-1"
    assert being_payload("not-a-being")["ok"] is False
    brief = being_brief("aria")
    assert "Aria" in brief and "POCKET" in brief


def test_aesthete_bans_muted_in_doctrine():
    text = BEINGS["aesthete"]["doctrine"] + " ".join(BEINGS["aesthete"]["oath"])
    assert "#8b8b98" in text or "banned" in text.lower()
