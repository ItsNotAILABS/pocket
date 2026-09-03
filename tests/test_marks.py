from pocket.auth import path_is_public
from pocket.marks import MARKS, claims_payload, page_html, snapshot
from pocket.screen_kernel import snapshot as kernel_snap


def test_marks_snapshot_has_fileable_and_never():
    s = snapshot()
    assert s["ok"] is True
    assert s["schema"] == "inl.marks.v1"
    names = {m["mark"] for m in s["file"]}
    assert "PHONEAI KERNEL" in names
    assert "VLAPTOP" in names
    assert "SCREEN-KERNEL" in names
    assert "PHONE.AI" in s["never"]
    assert "WEBMCP" in s["never"]
    assert "FACE ID" in s["never"]


def test_claims_payload_includes_002_and_marks():
    d = claims_payload()
    nums = {c["n"] for c in d["claims"]}
    assert 1 in nums and 14 in nums and 28 in nums
    assert d["id"].endswith("002")
    assert "PHONEAI KERNEL" in d["file_marks"]
    assert d["marks"]["ok"] is True


def test_claims_pages_are_public():
    remote = {"CF-Connecting-IP": "8.8.8.8"}
    addr = ("1.2.3.4", 443)
    for p in ("/v1/claims", "/v1/marks", "/claims", "/marks"):
        assert path_is_public(p, headers=remote, client_address=addr) is True
    html = page_html(kind="claims")
    assert "PhoneAI Kernel" in html
    assert "PHONE.AI" in html or "Do not brand" in html


def test_screen_kernel_cites_claim():
    s = kernel_snap()
    assert s["protocol"].startswith("SCREEN-KERNEL/")
    assert "002" in s.get("claims", "")


def test_never_brand_phone_dot_ai():
    never = {m["mark"] for m in MARKS if m.get("status") == "never"}
    assert "PHONE.AI" in never
    assert "ANTIGRAVITY" in never
