"""Fluid UI kit — injects into every HTML surface."""

from pocket.ui_kit import KIT_CSS, KIT_JS, KIT_VERSION, enhance


def test_enhance_injects_once():
    html = "<!DOCTYPE html><html><head><title>t</title></head><body>hi</body></html>"
    out = enhance(html)
    assert f'data-pocket-kit="{KIT_VERSION}"' in out
    assert "/ui/kit.css" in out
    assert "/ui/kit.js" in out
    again = enhance(out)
    assert again.count("/ui/kit.css") == 1
    assert again.count("/ui/kit.js") == 1


def test_kit_assets_have_motion():
    assert "view-transition" in KIT_CSS
    assert "pk-cmdk" in KIT_CSS
    assert "prefers-reduced-motion" in KIT_CSS
    assert "pocketCommand" in KIT_JS
    assert "pk-live-fab" in KIT_CSS
    assert "mountLive" in KIT_JS
    assert "POCKET Live" in KIT_JS
    assert "startViewTransition" in KIT_JS
    assert "Ctrl" in KIT_JS or "ctrlKey" in KIT_JS


def test_enhance_empty_passthrough():
    assert enhance("") == ""
