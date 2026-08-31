"""Spherical neuro thinking for primary engines."""

from pocket.neuro_think import NEURO_ENGINES, inject, think


def test_sphere_runs_internal():
    r = think("fix the login button in app_ui.py", mode="codex")
    assert r.get("ok")
    assert r.get("spherical") is True
    assert r.get("third_party") is False
    assert r.get("kind") == "code"
    assert "critic" in (r.get("regions") or {})
    assert "verify=" in (r.get("compact") or "")


def test_math_engages_cerebellum():
    r = think("gcd 48 18 and is 17 prime", mode="grok")
    assert r.get("kind") == "math"
    cer = (r.get("regions") or {}).get("cerebellum") or {}
    assert cer.get("engaged") is True


def test_inject_codex_is_compact():
    p, meta = inject("edit src/pocket/auth.py", mode="codex")
    assert meta.get("ok")
    assert "NEURO: class=" in p
    assert "[NEURO SPHERE]" not in p  # compact only for Codex tokens


def test_inject_grok_gets_sphere():
    p, meta = inject("research pocket bots vs grok bot", mode="grok")
    assert "[NEURO SPHERE]" in p
    assert meta.get("kind") == "research"


def test_engines_covered():
    assert {"grok", "claude", "codex", "muse_spark", "auro"} <= NEURO_ENGINES
