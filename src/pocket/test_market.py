"""Sold POCKET SKU — customer product, not founder lab."""

from pocket.market import HIDDEN_TABS_FOR_SEATS, SOLD_VERSION, catalog, seat_flags


def test_catalog_is_sellable():
    c = catalog()
    assert c["ok"] is True
    assert c["sku"] == "pocket-sold"
    assert c["version"] == SOLD_VERSION
    ids = {p["id"] for p in c["plans"]}
    assert "pocket_pro" in ids
    assert c["join"] == "/join"


def test_seat_flags_hide_founder_tabs():
    member = {"user": "alice", "role": "member", "is_owner": False}
    flags = seat_flags(member)
    assert flags["sold"] is True
    assert flags["edition"] == "market"
    assert "lab" in flags["hide_tabs"]
    assert set(HIDDEN_TABS_FOR_SEATS).issubset(set(flags["hide_tabs"]))


def test_owner_keeps_full_desk():
    owner = {"user": "pocket", "role": "admin", "is_owner": True}
    flags = seat_flags(owner)
    assert flags["sold"] is False
    assert flags["hide_tabs"] == []


def test_join_and_seats_pages():
    from pocket.market_ui import join_html, seats_html

    j = join_html()
    assert "Create your seat" in j
    assert "pk_seat_" in j
    s = seats_html()
    assert "Mint seat key" in s
    assert "/v1/admin/invites" in s
