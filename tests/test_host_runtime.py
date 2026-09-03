from pocket.host_runtime import catalog, setup_snapshot, status, urls
from pocket.phoneai_landing import landing_html, runtime_html
from pocket.setup_flow import setup_html
from pocket.voice_screen import act as voice_act


def test_catalog_has_pocket_and_watchdog():
    ids = {s["id"] for s in catalog()}
    assert {"pocket", "watchdog", "tunnel"} <= ids


def test_status_schema():
    st = status()
    assert st["schema"] == "pocket.host_runtime.v1"
    assert "runtime_ensure" in st["agents"]["bring_up"]
    assert "/phoneai" in st["urls"]["phoneai"]
    assert "singleton" in st
    assert "ports" in st


def test_runtime_singleton_lock(tmp_path, monkeypatch):
    from pocket import runtime_worker as rw

    monkeypatch.setattr(rw, "STATE_DIR", tmp_path)
    monkeypatch.setattr(rw, "LOCK_FILE", tmp_path / "runtime.lock")
    monkeypatch.setattr(rw, "PID_FILE", tmp_path / "runtime_worker.pid")
    rw._lock_fh = None
    a = rw.acquire_singleton()
    assert a.get("ok") is True
    b = rw.acquire_singleton()
    assert b.get("ok") is False
    assert b.get("already") is True


def test_screen_matrix_maps_unit_square():
    from pocket.screen_math import apply_int, desktop_from_unit

    m = desktop_from_unit({"x": 100, "y": 200, "w": 1000, "h": 500})
    x, y = apply_int(m, 0.5, 0.5)
    assert x == 600
    assert y == 450


def test_urls_include_tunnel_phoneai():
    u = urls()
    assert u["tunnel_phoneai"].endswith("/phoneai")
    assert u["phoneai_app"].endswith("/phoneai/app")


def test_setup_snapshot_steps():
    snap = setup_snapshot()
    ids = [s["id"] for s in snap["steps"]]
    assert ids == ["account", "host", "always_on", "desk", "phoneai"]


def test_phoneai_landing_is_intro_not_kernel():
    html = landing_html()
    assert "Enter PhoneAI" in html
    assert 'href="/phoneai/app"' in html
    assert "Always on" in html


def test_setup_and_runtime_pages():
    s = setup_html()
    assert "python -m pocket install" in s
    assert "/signup" in s
    r = runtime_html()
    assert "Bring host up" in r


def test_voice_screen_empty():
    assert voice_act("")["ok"] is False
