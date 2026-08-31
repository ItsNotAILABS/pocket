"""Internal AI foundations + math models."""

from pocket.foundations import catalog, ready
from pocket.internal_models import list_models, express_one
from pocket.platform_coherence import coherent, run_platform_skill


def test_foundations_internal_only():
    c = catalog()
    assert c.get("ok")
    assert c.get("internal") is True
    assert c.get("third_party_required") is False
    ids = {m.get("id") for m in c.get("models") or [] if m.get("id")}
    assert {"ghost", "logic", "pattern", "identity", "world"} <= ids
    assert (c.get("math") or {}).get("ready", 0) >= 1
    r = ready()
    assert r.get("ok")
    assert r.get("third_party_required") is False


def test_logic_and_pattern_express():
    logic = express_one("logic", "P or not P")
    assert logic.ok
    assert "Tautology" in logic.text or "tautology" in logic.text.lower()
    pat = express_one("pattern", "decompose this pattern spectral")
    assert pat.ok
    assert "internal" in pat.text.lower()


def test_foundations_on_platform():
    ids = {s["id"] for s in coherent().get("surfaces") or []}
    assert "foundations" in ids
    assert "imagine" in ids
    hit = run_platform_skill("foundations_map")
    assert hit.get("ok")
    assert hit.get("doctrine")


def test_world_has_pocket_foundations():
    from pocket.world_model import ensure_db, status

    ensure_db()
    st = status()
    assert int((st.get("counts") or {}).get("facts") or 0) >= 8


def test_ghost_gcd_internal():
    from pocket.ghost_math import gcd_pair, run_ghost

    assert gcd_pair(12, 18)["gcd"] == 6
    text, err, eng = run_ghost("gcd 48 18")
    assert err == ""
    assert "6" in text
    assert eng == "ghost-math"


def test_internal_models_list_ready():
    rows = list_models()
    kinds = {r.get("kind") for r in rows}
    assert "math" in kinds
    math_rows = [r for r in rows if r.get("kind") == "math"]
    assert len(math_rows) >= 2
