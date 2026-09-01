"""Phone photos → chat, text boxes, files, promo, Imagine. One pipe."""

from __future__ import annotations

import base64
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from pocket.phone_life import PHOTOS, save_photo


DESTS = ("files", "chat", "box", "promo", "imagine")


def _decode(data_url: str) -> bytes:
    raw = data_url or ""
    if "," in raw:
        raw = raw.split(",", 1)[1]
    return base64.b64decode(raw)


def _copy_file(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    return str(dest)


def _paste_image(path: Path) -> Dict[str, Any]:
    """Put the JPEG on the Windows clipboard and paste into the focused box."""
    p = str(path).replace("'", "''")
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img=[System.Drawing.Image]::FromFile('{p}'); "
        "[System.Windows.Forms.Clipboard]::SetImage($img); "
        "$img.Dispose(); "
        "Start-Sleep -Milliseconds 200; "
        "[System.Windows.Forms.SendKeys]::SendWait('^v'); "
        "'ok'"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return {"ok": r.returncode == 0, "out": (r.stdout or "")[:80]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:160]}


def send(
    *,
    image: str = "",
    name: str = "",
    dest: str = "all",
    caption: str = "",
) -> Dict[str, Any]:
    """Entangle a phone photo into Pocket surfaces.

    dest: all | files | chat | box | promo | imagine  (comma-separated ok)
    """
    saved: Dict[str, Any] = {}
    fp: Path | None = None
    if image:
        saved = save_photo(image, caption=caption or "phone")
        if not saved.get("ok"):
            return saved
        fp = Path(saved.get("path") or "")
    elif name:
        cand = PHOTOS / Path(name).name
        if cand.is_file():
            fp = cand
            saved = {"ok": True, "name": cand.name, "url": f"/v1/phoneai/photo?name={cand.name}", "path": str(cand)}
    if not fp or not fp.is_file():
        return {"ok": False, "error": "no photo"}

    want = {x.strip() for x in (dest or "all").lower().replace(";", ",").split(",") if x.strip()}
    if "all" in want:
        want = set(DESTS)
    if "paste" in want:
        want.add("box")

    routed: Dict[str, Any] = {}
    blob = fp.read_bytes()
    stamp = fp.name

    if "files" in want:
        try:
            from pocket.phoneai_space import dual_write_bytes

            routed["files"] = dual_write_bytes(f"photos/{stamp}", blob, message="phone photo")
        except Exception as e:
            routed["files"] = {"ok": False, "error": str(e)[:160]}

    if "chat" in want:
        try:
            from pocket.phone_life import add_note

            url = saved.get("url") or f"/v1/phoneai/photo?name={stamp}"
            routed["chat"] = add_note(f"{caption or 'Photo'}\n{url}")
        except Exception as e:
            routed["chat"] = {"ok": False, "error": str(e)[:160]}

    if "promo" in want:
        try:
            promo = Path.home() / ".pocket" / "drafts" / "promo" / stamp
            routed["promo"] = {"ok": True, "path": _copy_file(fp, promo)}
            creative = Path.home() / ".pocket" / "creative" / "photos" / stamp
            _copy_file(fp, creative)
        except Exception as e:
            routed["promo"] = {"ok": False, "error": str(e)[:160]}

    if "imagine" in want:
        try:
            imag = Path.home() / ".pocket" / "imagine" / "gallery" / stamp
            routed["imagine"] = {"ok": True, "path": _copy_file(fp, imag), "ui": "/imagine"}
        except Exception as e:
            routed["imagine"] = {"ok": False, "error": str(e)[:160]}

    if "box" in want:
        routed["box"] = _paste_image(fp)

    return {
        "ok": True,
        "schema": "pocket.photo_pipe.v1",
        "photo": saved,
        "dest": sorted(want),
        "routed": routed,
        "url": saved.get("url"),
        "reply": "Photo sent to " + ", ".join(sorted(want)) + ".",
    }


def catalog() -> Dict[str, Any]:
    from pocket.phone_life import list_photos

    return {
        "ok": True,
        "destinations": list(DESTS) + ["all"],
        "photos": list_photos(40),
        "post": "POST /v1/phoneai/photos  {image|name, dest, caption}",
    }
