"""Everyday phone tasks — notes, reminders, maps, texts, camera, lists."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.phoneai_space import dual_write, explorer_root

ROOT = Path.home() / ".pocket" / "phoneai"
NOTES = ROOT / "notes.json"
REMIND = ROOT / "reminders.json"
LISTS = ROOT / "lists.json"
PHOTOS = ROOT / "photos"
STATE = ROOT / "life.json"


def _load(path: Path, default):
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def classify(text: str) -> str:
    low = (text or "").lower()
    if re.search(r"\b(remind me|reminder|alarm|in \d+ (min|hour)|tomorrow at)\b", low):
        return "remind"
    if re.search(r"\b(note this|take a note|remember that|save this)\b", low):
        return "note"
    if re.search(r"\b(directions|navigate|where is|map of|how do i get)\b", low):
        return "maps"
    if re.search(r"\b(text |sms |message |draft (a )?text)\b", low):
        return "sms"
    if re.search(r"\b(call |dial |phone )\b", low) and re.search(r"\d{3}", low):
        return "call"
    if re.search(r"\b(weather|forecast|rain today|temperature)\b", low):
        return "weather"
    if re.search(r"\b(translate|in spanish|in french|in japanese)\b", low):
        return "translate"
    if re.search(r"\b(shopping list|add to list|grocery|to-?do)\b", low):
        return "list"
    if re.search(r"\b(take a (photo|pic|picture)|open camera|scan)\b", low):
        return "camera"
    if re.search(r"\b(calendar|add event|schedule)\b", low):
        return "calendar"
    return "chat"


def add_note(text: str) -> Dict[str, Any]:
    body = (text or "").strip()
    if not body:
        return {"ok": False, "error": "empty note"}
    rows = _load(NOTES, [])
    row = {"id": f"n{int(time.time())}", "text": body[:4000], "at": time.time()}
    rows.insert(0, row)
    _save(NOTES, rows[:200])
    dual_write(f"notes/{row['id']}.md", body, message="phone note")
    return {"ok": True, "kind": "note", "reply": f"Saved note.\n{body[:280]}", "item": row, "open": "/phoneai#notes"}


def add_reminder(text: str) -> Dict[str, Any]:
    body = re.sub(r"^(remind me to|remind me|reminder:?)\s+", "", (text or "").strip(), flags=re.I)
    rows = _load(REMIND, [])
    row = {"id": f"r{int(time.time())}", "text": body[:500], "at": time.time(), "done": False}
    rows.insert(0, row)
    _save(REMIND, rows[:200])
    dual_write("reminders.md", "\n".join(f"- {r['text']}" for r in rows if not r.get("done")), message="reminders")
    return {"ok": True, "kind": "remind", "reply": f"Reminder set: {body[:200]}", "item": row}


def add_list_item(text: str) -> Dict[str, Any]:
    body = re.sub(r"^(add |put )?(to (my )?(list|shopping list):?)\s*", "", (text or "").strip(), flags=re.I)
    data = _load(LISTS, {"shopping": []})
    data.setdefault("shopping", []).insert(0, {"text": body[:200], "at": time.time()})
    data["shopping"] = data["shopping"][:80]
    _save(LISTS, data)
    dual_write("lists/shopping.md", "\n".join(f"- {i['text']}" for i in data["shopping"]), message="shopping list")
    return {"ok": True, "kind": "list", "reply": f"Added to list: {body[:200]}", "items": data["shopping"][:20]}


def maps(text: str) -> Dict[str, Any]:
    q = re.sub(r"^(directions to|navigate to|where is|map of|how do i get to)\s+", "", (text or "").strip(), flags=re.I)
    url = "https://maps.google.com/?q=" + urllib.parse.quote(q[:160])
    return {
        "ok": True,
        "kind": "maps",
        "reply": f"Open maps for: {q[:120]}",
        "url": url,
        "open": url,
    }


def sms_draft(text: str) -> Dict[str, Any]:
    body = re.sub(r"^(text|sms|message|draft (a )?text( (to \S+)?)?:?)\s+", "", (text or "").strip(), flags=re.I)
    url = "sms:?&body=" + urllib.parse.quote(body[:300])
    return {"ok": True, "kind": "sms", "reply": f"Draft ready:\n{body[:300]}", "url": url, "open": url}


def call_link(text: str) -> Dict[str, Any]:
    digits = re.sub(r"[^\d+]", "", text or "")
    if len(digits) < 7:
        return {"ok": False, "kind": "call", "error": "no number"}
    url = "tel:" + digits
    return {"ok": True, "kind": "call", "reply": f"Call {digits}", "url": url, "open": url}


def weather(text: str) -> Dict[str, Any]:
    q = (text or "weather").strip()
    url = "https://www.google.com/search?q=" + urllib.parse.quote(q[:120])
    return {"ok": True, "kind": "weather", "reply": "Open forecast.", "url": url, "open": url}


def calendar_link(text: str) -> Dict[str, Any]:
    title = re.sub(r"^(add (an? )?event|schedule|calendar:?)\s+", "", (text or "event").strip(), flags=re.I)
    url = "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + urllib.parse.quote(title[:120])
    return {"ok": True, "kind": "calendar", "reply": f"Calendar draft: {title[:120]}", "url": url, "open": url}


def save_photo(data_url: str, *, caption: str = "") -> Dict[str, Any]:
    import base64

    raw = data_url or ""
    if "," in raw:
        raw = raw.split(",", 1)[1]
    try:
        blob = base64.b64decode(raw)
    except Exception:
        return {"ok": False, "error": "bad image"}
    if len(blob) > 12 * 1024 * 1024:
        return {"ok": False, "error": "photo too large"}
    PHOTOS.mkdir(parents=True, exist_ok=True)
    name = f"cam_{int(time.time())}.jpg"
    fp = PHOTOS / name
    fp.write_bytes(blob)
    dual_write(f"photos/{name}.txt", caption or name, message="phone photo")
    url = f"/v1/phoneai/photo?name={name}"
    return {"ok": True, "kind": "camera", "reply": "Photo saved.", "url": url, "path": str(fp), "name": name}


def list_photos(limit: int = 40) -> List[Dict[str, Any]]:
    PHOTOS.mkdir(parents=True, exist_ok=True)
    files = sorted(PHOTOS.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    return [{"name": p.name, "url": f"/v1/phoneai/photo?name={p.name}", "mtime": p.stat().st_mtime} for p in files]


def snapshot() -> Dict[str, Any]:
    return {
        "ok": True,
        "notes": _load(NOTES, [])[:30],
        "reminders": _load(REMIND, [])[:30],
        "list": _load(LISTS, {"shopping": []}).get("shopping")[:30],
        "photos": list_photos(24),
        "explorer": str(explorer_root()),
    }


def act(kind: str, text: str, *, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    extra = extra or {}
    raw = (kind or "auto").strip().lower()
    k = classify(text) if raw in ("auto", "", "chat") else raw
    if k == "note":
        return add_note(text)
    if k == "remind":
        return add_reminder(text)
    if k == "list":
        return add_list_item(text)
    if k == "maps":
        return maps(text)
    if k == "sms":
        return sms_draft(text)
    if k == "call":
        return call_link(text)
    if k == "weather":
        return weather(text)
    if k == "calendar":
        return calendar_link(text)
    if k == "camera":
        if extra.get("image"):
            return save_photo(str(extra.get("image") or ""), caption=text)
        return {"ok": True, "kind": "camera", "reply": "Open the camera.", "open": "/phoneai#camera"}
    if k in ("translate", "chat", "auto", ""):
        prompt = text if k != "translate" else f"Translate clearly, keep it short:\n{text}"
        try:
            from pocket.phoneai_settings import chat_engine
            from pocket.phoneai_bridge import ask_engine

            engine = str(extra.get("engine") or "") or (chat_engine() if k != "translate" else "grok")
            r = ask_engine(prompt, engine=engine or "grok")
        except Exception as e:
            r = {"ok": False, "error": str(e)[:200], "engine": "grok"}
        r["kind"] = "chat" if k != "translate" else "translate"
        r.setdefault("via", r.get("engine") or "grok")
        return r
    try:
        from pocket.phoneai_bridge import ask_engine

        r = ask_engine(text, engine="grok")
    except Exception as e:
        r = {"ok": False, "error": str(e)[:200], "engine": "grok"}
    r["kind"] = "chat"
    return r
