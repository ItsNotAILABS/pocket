"""Drive Antigravity from the phone: new chat, paste+send, stream the thread, WebMCP."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from pocket.desktop import open_app
from pocket.ui_click import click_named_element
from pocket.ui_maneuver import focus_window_title, send_keys, set_clipboard

STATE = Path.home() / ".pocket" / "phoneai" / "antigravity.json"


def _focus(cwd: str = "") -> Dict[str, Any]:
    opened = open_app("antigravity", path=cwd or "")
    time.sleep(0.8)
    focus = focus_window_title("Antigravity")
    if not focus.get("ok"):
        focus = focus_window_title("anti")
    return {"opened": opened, "focus": focus}


def new_chat(text: str = "", *, cwd: str = "") -> Dict[str, Any]:
    """Open Antigravity and start a fresh chat, then optionally send."""
    ctx = _focus(cwd)
    # Composer / new agent chat — try named buttons then shortcuts.
    click = (
        click_named_element("New Chat")
        or click_named_element("New chat")
        or click_named_element("New Agent")
        or click_named_element("New conversation")
        or {}
    )
    send_keys("^l", settle_ms=180)
    send_keys("^+l", settle_ms=180)
    send_keys("^+a", settle_ms=180)
    sent = {}
    if (text or "").strip():
        sent = paste_send(text, cwd=cwd, already_open=True)
    return {
        "ok": True,
        "engine": "antigravity",
        "action": "new_chat",
        "click": click,
        "sent": sent,
        **ctx,
        "reply": "Opened a new Antigravity chat on the PC."
        + (" First message sent." if sent else " Type and send from the phone."),
    }


def paste_send(text: str, *, cwd: str = "", already_open: bool = False) -> Dict[str, Any]:
    """Paste into the live chat and press send. Scan UI via WebMCP."""
    msg = (text or "").strip()
    if not msg:
        return {"ok": False, "error": "empty message"}
    ctx = {} if already_open else _focus(cwd)
    set_clipboard(msg)
    time.sleep(0.2)
    click = click_named_element("chat") or click_named_element("Ask") or click_named_element("Message") or {}
    send_keys("^v", settle_ms=220)
    time.sleep(0.15)
    send_keys("{ENTER}", settle_ms=160)
    send_keys("^{ENTER}", settle_ms=160)
    send_btn = click_named_element("Send")
    notice = _webmcp_notice()
    thread = read_thread()
    return {
        "ok": True,
        "engine": "antigravity",
        "action": "send",
        "click": click,
        "send": send_btn,
        "webmcp": notice,
        "thread": thread.get("text") or "",
        "reply": thread.get("text") or "Sent to Antigravity. Stream the thread on this page.",
        **ctx,
    }


def read_thread() -> Dict[str, Any]:
    """Read the visible Antigravity conversation (UIA + OCR fusion)."""
    names: List[str] = []
    ocr = ""
    try:
        from pocket.perception import sense

        page = sense(max_ui=500, force=True, include_image=False)
        ocr = str(page.get("ocr_plain") or page.get("ocr_head") or "")[:12000]
        for s in page.get("symbols") or []:
            t = (s.get("text") or "").strip()
            if t and len(t) > 1:
                names.append(t)
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "text": ""}
    # Prefer OCR blob; fall back to named controls.
    text = (ocr or "\n".join(names[:80])).strip()
    return {
        "ok": True,
        "engine": "antigravity",
        "text": text[-8000:],
        "controls": names[:40],
        "at": time.time(),
    }


def continue_mcp(text: str = "") -> Dict[str, Any]:
    """Click live notifications / buttons via WebMCP, then optionally send more."""
    _focus("")
    notice = _webmcp_notice()
    clicks = []
    for label in ("Continue", "Retry", "Allow", "Run", "Accept", "Apply", "Keep", "Yes"):
        hit = click_named_element(label)
        if hit.get("ok"):
            clicks.append(label)
            time.sleep(0.2)
    sent = paste_send(text, already_open=True) if (text or "").strip() else {}
    thread = read_thread()
    return {
        "ok": True,
        "engine": "antigravity",
        "action": "continue",
        "clicked": clicks,
        "webmcp": notice,
        "sent": sent,
        "thread": thread.get("text") or "",
        "reply": (
            ("Clicked: " + ", ".join(clicks) + ". ") if clicks else "No extra buttons. "
        )
        + (thread.get("text") or "Thread refreshed."),
    }


def _webmcp_notice() -> Dict[str, Any]:
    try:
        from pocket.webmcp import scan

        notice = scan(fusion=True)
        return {
            "count": notice.get("count"),
            "fusion_sample": [
                a.get("name")
                for a in (notice.get("actions") or [])
                if a.get("source") == "fusion"
            ][:16],
        }
    except Exception as e:
        return {"error": str(e)[:160]}


def handle(action: str, text: str = "", *, cwd: str = "") -> Dict[str, Any]:
    a = (action or "send").strip().lower()
    if a in ("new", "new_chat", "new-chat"):
        return new_chat(text, cwd=cwd)
    if a in ("continue", "mcp", "click"):
        return continue_mcp(text)
    if a in ("read", "thread", "stream"):
        return read_thread()
    return paste_send(text, cwd=cwd)
