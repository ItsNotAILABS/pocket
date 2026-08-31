"""Imagine Studio — image / composition product bridge for the POCKET platform.

Product home (not stuffed into desk UI):
  C:\\Users\\Medin\\OneDrive\\imagine-studio\\

Seeds:
  seed-creative-muse/  (from organism-ai creative-muse.zip)

Runtime jobs:
  · still compositions (studio gradient + device glass + content)
  · fusion remake handoff
  · gallery + file serve for the /imagine UI
"""

from __future__ import annotations

import base64
import io
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pocket.live_events import emit

HOME = Path.home() / ".pocket" / "imagine"
EXPORTS = HOME / "exports"
COMPOSITES = HOME / "composites"
UPLOADS = HOME / "uploads"
REMAKES = HOME / "remakes"
SCENES = HOME / "scenes"
for d in (HOME, EXPORTS, COMPOSITES, UPLOADS, REMAKES, SCENES):
    d.mkdir(parents=True, exist_ok=True)

PRODUCT_DIR = Path.home() / "OneDrive" / "imagine-studio"
RESEARCH_DIR = (
    Path.home()
    / "OneDrive"
    / "Documents"
    / "POCKET_Research"
    / "ImagineStudio_ViralDemos_FusionRemake"
)
VISION_DIR = Path.home() / ".pocket" / "vision"

MODES: List[Dict[str, Any]] = [
    {
        "id": "rotato_phone",
        "label": "Rotato phone",
        "desc": "Portrait 9:16 device glass. Screen is letterboxed — never stretch-cropped.",
        "aspect": "9:16",
        "aliases": ["phone", "viral_phone"],
        "default_size": [1080, 1920],
    },
    {
        "id": "macbook_web",
        "label": "MacBook web",
        "desc": "Landscape 16:9 laptop + browser chrome. UI stays readable.",
        "aspect": "16:9",
        "aliases": ["web", "viral_web"],
        "default_size": [1920, 1080],
    },
    {
        "id": "clean",
        "label": "Clean still",
        "desc": "Letterboxed product frame on studio gradient. No fake device.",
        "aspect": "16:9",
        "aliases": ["flat", "minimal"],
        "default_size": [1920, 1080],
    },
]


def _mode_ids() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for m in MODES:
        out[m["id"]] = m["id"]
        for a in m.get("aliases") or []:
            out[str(a).lower()] = m["id"]
    return out


def list_modes() -> Dict[str, Any]:
    return {
        "ok": True,
        "modes": MODES,
        "doctrine": "Contain / letterbox product UI into glass — never force-fill.",
        "note": "Compose uses a real host screenshot or an uploaded PNG. There is no text-to-image model on this path.",
    }


def status() -> Dict[str, Any]:
    seed = PRODUCT_DIR / "seed-creative-muse"
    comps = list_composites(limit=6)
    remakes = list_remakes(limit=4)
    return {
        "ok": True,
        "product": "Imagine Studio",
        "ui": "/imagine",
        "product_dir": str(PRODUCT_DIR),
        "research_dir": str(RESEARCH_DIR),
        "seed_creative_muse": seed.is_dir(),
        "exports": str(EXPORTS),
        "composites": str(COMPOSITES),
        "counts": {
            "composites": comps.get("count") or 0,
            "remakes": remakes.get("count") or 0,
        },
        "recent": comps.get("items") or [],
        "api": {
            "status": "GET /v1/imagine",
            "gallery": "GET /v1/imagine/gallery",
            "modes": "GET /v1/imagine/modes",
            "compose": "POST /v1/imagine/compose",
            "file": "GET /v1/imagine/file?name=",
            "remake": "POST /v1/fusion/remake",
            "studio_render": "POST /v1/studio/render",
        },
        "note": "Device stills from host capture. Not a prompt-to-pixel generator.",
    }


def gallery(*, limit: int = 24) -> Dict[str, Any]:
    comps = list_composites(limit=limit)
    rem = list_remakes(limit=limit)
    return {
        "ok": True,
        "product": "Imagine Studio",
        "ui": "/imagine",
        "composites": comps.get("items") or [],
        "remakes": rem.get("items") or [],
        "counts": {
            "composites": comps.get("count") or 0,
            "remakes": rem.get("count") or 0,
        },
        "empty_hint": (
            "No stills yet. Compose a rotato phone or MacBook frame from the host screen, "
            "or upload a PNG. Fusion remake rebuilds the last understood page as HTML."
        ),
    }


def _file_stat(fp: Path, *, kind: str) -> Dict[str, Any]:
    st = fp.stat()
    return {
        "name": fp.name,
        "kind": kind,
        "path": str(fp),
        "bytes": st.st_size,
        "size_mb": round(st.st_size / (1024 * 1024), 2),
        "mtime": st.st_mtime,
        "url": f"/v1/imagine/file?name={fp.name}&kind={kind}",
    }


def list_composites(*, limit: int = 24) -> Dict[str, Any]:
    items = [_file_stat(p, kind="composite") for p in COMPOSITES.glob("*.png") if p.is_file()]
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return {"ok": True, "count": len(items), "items": items[: max(1, min(limit, 80))]}


def list_remakes(*, limit: int = 16) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for p in REMAKES.glob("*"):
        if p.suffix.lower() in {".html", ".json"} and p.is_file():
            items.append(_file_stat(p, kind="remake"))
    for p in SCENES.glob("*.json"):
        if p.is_file():
            items.append(_file_stat(p, kind="scene"))
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return {"ok": True, "count": len(items), "items": items[: max(1, min(limit, 80))]}


def resolve_file(name: str, *, kind: str = "") -> Optional[Path]:
    """Basename-only resolve under imagine home trees."""
    safe = Path(name or "").name
    if not safe or safe in {".", ".."} or ".." in safe:
        return None
    k = (kind or "").lower().strip()
    candidates: List[Path] = []
    if k in ("composite", "composites", "png", "still"):
        candidates = [COMPOSITES / safe]
    elif k in ("remake", "html", "ir"):
        candidates = [REMAKES / safe]
    elif k in ("scene", "scene3d"):
        candidates = [SCENES / safe]
    elif k in ("upload", "uploads"):
        candidates = [UPLOADS / safe]
    else:
        candidates = [COMPOSITES / safe, REMAKES / safe, SCENES / safe, UPLOADS / safe, EXPORTS / safe]
    for fp in candidates:
        try:
            if fp.is_file() and str(fp.resolve()).startswith(str(HOME.resolve())):
                return fp
        except Exception:
            continue
    return None


def _latest_vision_png() -> Optional[Path]:
    if not VISION_DIR.is_dir():
        return None
    pngs = [p for p in VISION_DIR.glob("*.png") if p.is_file()]
    if not pngs:
        return None
    pngs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs[0]


def _latest_novae_png() -> Optional[Path]:
    """Newest PNG left in a Novae workspace (Grok / Codex hands)."""
    root = Path.home() / ".pocket" / "novae" / "workspaces"
    if not root.is_dir():
        return None
    pngs = [p for p in root.rglob("*.png") if p.is_file()]
    if not pngs:
        return None
    pngs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs[0]


def save_upload(*, filename: str = "", image_b64: str = "") -> Dict[str, Any]:
    raw_b64 = (image_b64 or "").split(",", 1)[-1].strip()
    if not raw_b64:
        return {"ok": False, "error": "image_b64 required"}
    try:
        raw = base64.b64decode(raw_b64, validate=False)
    except Exception:
        return {"ok": False, "error": "invalid base64 image"}
    if len(raw) > 12 * 1024 * 1024:
        return {"ok": False, "error": "image too large (max 12MB)"}
    name = Path(filename or "upload.png").name
    if not name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        name = (name or "upload") + ".png"
    dest = UPLOADS / f"up_{uuid.uuid4().hex[:8]}_{name}"
    dest.write_bytes(raw)
    return {"ok": True, "path": str(dest), "name": dest.name, "bytes": len(raw)}


def _load_content(
    image_path: Optional[str] = None,
    *,
    image_b64: str = "",
    source: str = "live",
) -> Tuple[Any, str]:
    from PIL import Image

    src = (source or "live").lower().strip()
    if image_b64:
        raw_b64 = image_b64.split(",", 1)[-1].strip()
        raw = base64.b64decode(raw_b64, validate=False)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        return img, "upload"
    if image_path and Path(image_path).is_file():
        return Image.open(image_path).convert("RGB"), "path"
    if src in ("last", "vision", "last_vision"):
        last = _latest_vision_png()
        if last:
            return Image.open(last).convert("RGB"), "vision"
        raise RuntimeError("No vision PNG on disk. Capture the host screen first.")
    if src in ("novae", "nova", "novae_workspace"):
        last = _latest_novae_png()
        if last:
            return Image.open(last).convert("RGB"), "novae"
        raise RuntimeError(
            "No PNG in Novae workspaces yet. Seat Grok Novae, drop a still in its workspace, or compose from live screen."
        )
    capture_err = ""
    try:
        from pocket.pixel_translator import _capture_pil

        return _capture_pil(max_width=1600), "capture"
    except Exception as e:
        capture_err = str(e)[:160]
    last = _latest_vision_png()
    if last:
        return Image.open(last).convert("RGB"), "vision_fallback"
    raise RuntimeError(
        "No screen to compose. Host capture failed"
        + (f" ({capture_err})" if capture_err else "")
        + ". Upload a PNG or run this on the desktop host."
    )


def _gradient(size: Tuple[int, int], colors=None):
    from PIL import Image

    w, h = size
    colors = colors or [(15, 12, 41), (48, 43, 99), (36, 36, 62)]
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            u = t * 2
            c0, c1 = colors[0], colors[1]
        else:
            u = (t - 0.5) * 2
            c0, c1 = colors[1], colors[2]
        r = int(c0[0] + (c1[0] - c0[0]) * u)
        g = int(c0[1] + (c1[1] - c0[1]) * u)
        b = int(c0[2] + (c1[2] - c0[2]) * u)
        for x in range(w):
            vx = 1.0 - abs(x / w - 0.5) * 0.35
            px[x, y] = (int(r * vx), int(g * vx), int(b * vx))
    return img


def _fit_contain(src, box_w: int, box_h: int, fill=(8, 8, 12)):
    """Letterbox content into box — never stretch to destroy UI."""
    from PIL import Image

    src = src.convert("RGB")
    sw, sh = src.size
    scale = min(box_w / sw, box_h / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (box_w, box_h), fill)
    canvas.paste(resized, ((box_w - nw) // 2, (box_h - nh) // 2))
    return canvas


def _draw_phone_chassis(draw, x0, y0, x1, y1, *, radius=48):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(18, 18, 22), outline=(70, 70, 78), width=3)
    draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=radius - 6, outline=(40, 40, 48), width=2)
    iw = int((x1 - x0) * 0.28)
    ih = 22
    ix = (x0 + x1 - iw) // 2
    draw.rounded_rectangle([ix, y0 + 14, ix + iw, y0 + 14 + ih], radius=12, fill=(5, 5, 8))
    bw = int((x1 - x0) * 0.28)
    draw.rounded_rectangle(
        [(x0 + x1 - bw) // 2, y1 - 22, (x0 + x1 + bw) // 2, y1 - 14],
        radius=4,
        fill=(220, 220, 230),
    )


def compose_device_still(
    image_path: Optional[str] = None,
    *,
    mode: str = "rotato_phone",
    title: str = "POCKET",
    subtitle: str = "Host co-pilot",
    width: int = 1080,
    height: int = 1920,
    image_b64: str = "",
    source: str = "live",
) -> Dict[str, Any]:
    """Compose a Rotato-style still: studio bg + real letterboxed screen + chassis."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    emit("imagine", f"compose {mode}", agent="STUDIO", role="python")
    t0 = time.time()
    content, source_kind = _load_content(image_path, image_b64=image_b64, source=source)

    bg = _gradient((width, height))
    draw = ImageDraw.Draw(bg)

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if mode in ("rotato_phone", "phone"):
        margin_x = int(width * 0.14)
        margin_y = int(height * 0.10)
        px0, py0 = margin_x, margin_y
        px1, py1 = width - margin_x, height - margin_y
        gd.ellipse([px0 + 40, py1 - 40, px1 - 40, py1 + 50], fill=(0, 0, 0, 110))
        glow = glow.filter(ImageFilter.GaussianBlur(28))
        bg = Image.alpha_composite(bg.convert("RGBA"), glow).convert("RGB")
        draw = ImageDraw.Draw(bg)

        _draw_phone_chassis(draw, px0, py0, px1, py1, radius=56)
        inset = 18
        sx0, sy0 = px0 + inset, py0 + 42
        sx1, sy1 = px1 - inset, py1 - 36
        sw, sh = sx1 - sx0, sy1 - sy0
        screen = _fit_contain(content, sw, sh, fill=(10, 10, 14))
        bg.paste(screen, (sx0, sy0))

        hi = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hi)
        hd.polygon(
            [(sx0, sy0), (sx0 + int(sw * 0.35), sy0), (sx0, sy0 + int(sh * 0.55))],
            fill=(255, 255, 255, 28),
        )
        bg = Image.alpha_composite(bg.convert("RGBA"), hi).convert("RGB")
        draw = ImageDraw.Draw(bg)

    elif mode in ("macbook_web", "web"):
        lx0, ly0 = int(width * 0.06), int(height * 0.12)
        lx1, ly1 = int(width * 0.94), int(height * 0.78)
        gd.ellipse([lx0 + 80, ly1 - 10, lx1 - 80, ly1 + 70], fill=(0, 0, 0, 100))
        glow = glow.filter(ImageFilter.GaussianBlur(24))
        bg = Image.alpha_composite(bg.convert("RGBA"), glow).convert("RGB")
        draw = ImageDraw.Draw(bg)
        draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=18, fill=(28, 28, 32), outline=(80, 80, 88), width=3)
        sx0, sy0 = lx0 + 16, ly0 + 16
        sx1, sy1 = lx1 - 16, ly1 - 40
        draw.rectangle([sx0, sy0, sx1, sy0 + 36], fill=(40, 40, 46))
        for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
            draw.ellipse([sx0 + 12 + i * 18, sy0 + 12, sx0 + 22 + i * 18, sy0 + 22], fill=col)
        sw, sh = sx1 - sx0, sy1 - (sy0 + 36)
        screen = _fit_contain(content, sw, sh, fill=(20, 20, 24))
        bg.paste(screen, (sx0, sy0 + 36))
        draw.rounded_rectangle([lx0 - 20, ly1, lx1 + 20, ly1 + 28], radius=6, fill=(50, 50, 56))

    else:
        pad = 48
        screen = _fit_contain(content, width - pad * 2, height - pad * 2)
        bg.paste(screen, (pad, pad))

    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 42)
        font_s = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    draw = ImageDraw.Draw(bg)
    draw.text((48, height - 100), title[:40], fill=(255, 255, 255), font=font)
    draw.text((48, height - 52), subtitle[:60], fill=(52, 211, 153), font=font_s)

    out = COMPOSITES / f"compose_{mode}_{uuid.uuid4().hex[:8]}.png"
    bg.save(out, "PNG", optimize=True)

    return {
        "ok": True,
        "product": "Imagine Studio",
        "mode": mode,
        "path": str(out),
        "name": out.name,
        "file_url": f"/v1/imagine/file?name={out.name}&kind=composite",
        "source_kind": source_kind,
        "size": [width, height],
        "ms": int((time.time() - t0) * 1000),
        "message": f"Compose {mode}: {out.name}",
        "api": {"compose": "POST /v1/imagine/compose", "studio": "POST /v1/studio/render"},
    }


def compose(
    *,
    mode: str = "rotato_phone",
    image: str = "",
    title: str = "POCKET",
    subtitle: str = "Host co-pilot",
    width: int = 0,
    height: int = 0,
    image_b64: str = "",
    source: str = "live",
) -> Dict[str, Any]:
    canon = _mode_ids().get((mode or "rotato_phone").lower(), "clean")
    if canon == "rotato_phone":
        w, h = width or 1080, height or 1920
        m = "rotato_phone"
    elif canon == "macbook_web":
        w, h = width or 1920, height or 1080
        m = "macbook_web"
    else:
        w, h = width or 1920, height or 1080
        m = "clean"
    try:
        return compose_device_still(
            image or None,
            mode=m,
            title=title,
            subtitle=subtitle,
            width=w,
            height=h,
            image_b64=image_b64 or "",
            source=source or "live",
        )
    except Exception as e:
        return {
            "ok": False,
            "product": "Imagine Studio",
            "mode": m,
            "error": str(e)[:280],
            "hint": (
                "Compose needs a real screenshot. Run on the desktop host, "
                "choose Last vision frame, or upload a PNG. This is not a text-to-image API."
            ),
            "ui": "/imagine",
            "api": {"compose": "POST /v1/imagine/compose", "gallery": "GET /v1/imagine/gallery"},
        }
