"""WebMCP diffusion catalog."""

from pocket.webmcp import catalog, find_actions, parse_page_html, scan


def test_scan_host_without_fusion():
    c = scan(fusion=False)
    assert c["ok"] is True
    assert c["count"] > 20
    sources = set(c["sources"])
    assert "phoneai" in sources
    assert "surface" in sources
    assert "work" in sources
    work = [a for a in c["actions"] if a["source"] == "work"]
    assert any(a.get("invoke") == "studio_develop" for a in work)
    assert any(a.get("invoke") == "anti_send" for a in work)
    phone = [a for a in c["actions"] if a["source"] == "phoneai"]
    assert any(a.get("how_phoneai") for a in phone)


def test_parse_page_html_extracts_controls():
    html = """<html><body>
    <a href="/login">Sign in</a>
    <button>Save</button>
    <input name="q" placeholder="Search"/>
    </body></html>"""
    acts = parse_page_html(html, url="https://example.com")
    names = " ".join(a["name"] for a in acts).lower()
    assert "sign in" in names
    assert "save" in names


def test_find_actions_phoneai_work():
    scan(fusion=False)
    hits = find_actions("phoneai")
    assert isinstance(hits, list)
    assert hits
