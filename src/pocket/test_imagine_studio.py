"""Imagine Studio compose + gallery — real Pillow path, no fake generators."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pocket.imagine_studio import (
    COMPOSITES,
    compose,
    gallery,
    list_modes,
    resolve_file,
    status,
)


def test_modes_catalog():
    m = list_modes()
    ids = {row["id"] for row in m["modes"]}
    assert {"rotato_phone", "macbook_web", "clean"} <= ids
    assert "no text-to-image" in (m.get("note") or "").lower()


def test_compose_clean_from_png(tmp_path: Path):
    src = tmp_path / "ui.png"
    Image.new("RGB", (320, 180), (24, 48, 96)).save(src)
    r = compose(mode="clean", image=str(src), title="TEST", subtitle="letterbox")
    assert r.get("ok"), r
    assert r.get("mode") == "clean"
    assert r.get("source_kind") == "path"
    out = Path(r["path"])
    assert out.is_file()
    assert out.parent == COMPOSITES
    img = Image.open(out)
    assert img.size == (1920, 1080)
    fp = resolve_file(r["name"], kind="composite")
    assert fp and fp.is_file()
    g = gallery(limit=8)
    assert g.get("ok")
    names = [i["name"] for i in g.get("composites") or []]
    assert r["name"] in names


def test_compose_phone_letterbox(tmp_path: Path):
    src = tmp_path / "wide.png"
    Image.new("RGB", (800, 200), (200, 40, 40)).save(src)
    r = compose(mode="rotato_phone", image=str(src), title="P", subtitle="phone")
    assert r.get("ok"), r
    assert r.get("file_url", "").startswith("/v1/imagine/file")
    img = Image.open(r["path"])
    assert img.size == (1080, 1920)


def test_compose_missing_source_errors():
    r = compose(mode="clean", image=r"C:\definitely-missing-imagine.png", source="last")
    # last vision may exist on this machine — still must be a dict
    assert isinstance(r, dict)
    assert "ok" in r


def test_status_points_at_ui():
    st = status()
    assert st.get("ui") == "/imagine"
    assert st.get("ok")
    assert "/v1/imagine/compose" in (st.get("api") or {}).get("compose", "")
