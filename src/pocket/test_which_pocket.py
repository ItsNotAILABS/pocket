"""Two POCKET products — Owner :8787 vs Users :8788."""

import os

from pocket.edition import owner_url, product_id, users_local_url
from pocket.which_pocket import host_name, is_loopback_host, summary, which_html


def test_owner_and_users_are_different_urls():
    assert owner_url().endswith(":8787")
    assert users_local_url().endswith(":8788")
    assert owner_url() != users_local_url()


def test_default_process_is_owner_product():
    os.environ.pop("POCKET_PRODUCT", None)
    os.environ["POCKET_EDITION"] = "founder"
    assert product_id() == "owner"
    s = summary("127.0.0.1:8787")
    assert s["product"] == "owner"
    assert s["separated"] is True
    assert s["your_pocket"]["port"] == 8787
    assert s["user_facing"]["port"] == 8788


def test_public_edition_is_users_product():
    os.environ["POCKET_EDITION"] = "public"
    os.environ["POCKET_PRODUCT"] = "users"
    try:
        assert product_id() == "users"
        s = summary("127.0.0.1:8788")
        assert s["product"] == "users"
        html = which_html("127.0.0.1:8788")
        assert "POCKET for Users" in html
        assert "This process" in html
    finally:
        os.environ["POCKET_EDITION"] = "founder"
        os.environ.pop("POCKET_PRODUCT", None)


def test_which_html_names_two_products():
    os.environ["POCKET_EDITION"] = "founder"
    html = which_html("127.0.0.1:8787")
    assert "Two products" in html
    assert "POCKET Owner" in html
    assert "POCKET for Users" in html
    assert ":8787" in html
    assert ":8788" in html


def test_host_name_strips_port_and_brackets():
    assert host_name("127.0.0.1:8787") == "127.0.0.1"
    assert host_name("[::1]:8787") == "::1"
    assert is_loopback_host("127.0.0.1:8787")
    assert not is_loopback_host("192.168.12.127")
