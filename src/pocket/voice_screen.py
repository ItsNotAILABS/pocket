"""Voice → screen action. Fusion click, Portal/Anti touch, open web."""

from __future__ import annotations

import re
from typing import Any, Dict


def act(text: str, *, which: str = "portal") -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "error": "say something"}
    low = raw.lower()
    w = "antigravity" if "anti" in (which or "").lower() else "portal"

    url_m = re.search(r"https?://[^\s]+", raw)
    if url_m or low.startswith("open ") and ("." in low or "http" in low):
        url = url_m.group(0) if url_m else raw.split(" ", 1)[-1].strip()
        if not url.startswith("http"):
            url = "https://" + url
        try:
            from pocket.web_ui_engine import act as web_act

            opened = web_act("open", url=url)
        except Exception:
            from pocket.desktop import open_app

            opened = open_app("edge", url)
        return {"ok": True, "kind": "open_web", "url": url, "opened": opened, "reply": f"Opened {url} on the PC."}

    if any(k in low for k in ("scroll down", "page down", "swipe up")):
        from pocket.agent_eyes import act as eyes_act

        return {"ok": True, "kind": "scroll", **eyes_act("scroll", which=w, nx=0.5, ny=0.5)}
    if any(k in low for k in ("scroll up", "page up", "swipe down")):
        from pocket.agent_eyes import act as eyes_act

        r = eyes_act("scroll", which=w, nx=0.5, ny=0.5)
        r["kind"] = "scroll_up"
        return r
    if "right click" in low or "context menu" in low:
        from pocket.agent_eyes import act as eyes_act

        return {"ok": True, "kind": "right", **eyes_act("right", which=w, nx=0.5, ny=0.5)}

    m = re.search(r"\b(click|tap|press)\s+(.+)$", low)
    if m:
        name = m.group(2).strip(" .")
        from pocket.sanity import guard_click

        hit = guard_click(name, min_score=0.55)
        return {"ok": bool(hit.get("ok")), "kind": "click_name", "name": name, "hit": hit, "reply": hit.get("message") or f"Clicked {name}."}

    if any(k in low for k in ("show screen", "look", "what do you see", "screenshot")):
        from pocket.agent_eyes import see

        s = see(which=w)
        s.pop("base64", None)
        return {"ok": True, "kind": "see", **s, "reply": f"Seeing {s.get('which')} · {s.get('bytes')} bytes."}

    # default: type the utterance onto the focused screen
    from pocket.agent_eyes import act as eyes_act

    return {"ok": True, "kind": "type", **eyes_act("type", which=w, nx=0.5, ny=0.5, text=raw), "reply": "Typed on screen."}
