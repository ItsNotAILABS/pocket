"""Wearables — Meta glasses HUD + AirPods listen/speak on PhoneAI.

Wake word, glance cards, glasses camera → Coder, spatial window cues,
connection HUD, and dictation lock live in this one loop.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

STATE = Path.home() / ".pocket" / "wear" / "state.json"
WAKE = ("phoneai", "phone ai", "hey phoneai", "ok phoneai", "okay phoneai")

USES: List[Dict[str, str]] = [
    {"id": "wake", "how": "Always listen only runs after 'PhoneAI …'", "device": "airpods"},
    {"id": "glance", "how": "2–3 line cards: focused window, host, app count — no JPEG required", "device": "glasses"},
    {"id": "camera", "how": "Glasses/phone camera → PhoneAI photos; say 'what is this error' for Coder", "device": "glasses"},
    {"id": "spatial", "how": "Say left window / right window / first window using the tab strip", "device": "both"},
    {"id": "hud", "how": "AirPods in-ear + glasses online + host up", "device": "both"},
    {"id": "dictation", "how": "Say dictation — type until you say send", "device": "airpods"},
    {"id": "listen", "how": "AirPods mic → command", "device": "airpods"},
    {"id": "speak", "how": "Reply spoken through AirPods", "device": "airpods"},
    {"id": "focus", "how": "Switch to / focus a named window", "device": "both"},
    {"id": "open", "how": "Open an allowlisted desktop app", "device": "both"},
    {"id": "scroll", "how": "Scroll the focused PC window", "device": "both"},
    {"id": "coder", "how": "Long-term Grok agent on the family repos", "device": "both"},
]


def _load() -> Dict[str, Any]:
    if STATE.is_file():
        try:
            data = json.loads(STATE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"dictation": False, "buffer": "", "heartbeat": {}}


def _save(data: Dict[str, Any]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, default=str)[:80_000], encoding="utf-8")


def strip_wake(text: str) -> Tuple[str, bool]:
    raw = (text or "").strip()
    low = raw.lower()
    for w in WAKE:
        if low.startswith(w):
            rest = raw[len(w) :].lstrip(" ,.-:")
            return rest, True
        i = low.find(w)
        if 0 <= i <= 16:
            rest = raw[i + len(w) :].lstrip(" ,.-:")
            return rest, True
    return raw, False


def glance_card() -> Dict[str, Any]:
    focused = "desktop"
    n = 0
    tabs: List[Dict[str, Any]] = []
    try:
        from pocket.phoneai_portal import windows

        win = windows(limit=12)
        focused = (win.get("title") or "desktop")[:60]
        tabs = win.get("windows") or []
        n = len(tabs)
    except Exception:
        pass
    host_up = False
    try:
        from pocket.host_runtime import status

        host_up = bool(status().get("up"))
    except Exception:
        pass
    st = _load()
    dictation = bool(st.get("dictation"))
    lines = [
        focused or "desktop",
        "Host up" if host_up else "Host down",
        ("Dictation on" if dictation else f"{n} windows"),
    ]
    return {
        "ok": True,
        "kind": "glance",
        "lines": lines,
        "focused": focused,
        "windows": n,
        "host": host_up,
        "tabs": tabs[:12],
        "reply": " · ".join(lines),
    }


def heartbeat(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    extra = extra or {}
    data = _load()
    hb = dict(data.get("heartbeat") or {})
    now = time.time()
    if extra.get("battery") is not None:
        try:
            hb["battery"] = float(extra["battery"])
        except Exception:
            pass
    for k in ("online", "inEar", "glasses", "airpods"):
        if k in extra:
            hb[k] = bool(extra.get(k))
    hb["ts"] = now
    data["heartbeat"] = hb
    _save(data)
    age = now - float(hb.get("ts") or now)
    glasses_online = bool(hb.get("glasses")) and age < 20
    airpods = bool(hb.get("airpods") or hb.get("inEar"))
    return {
        "ok": True,
        "host": True,
        "glasses": glasses_online,
        "airpods": airpods,
        "inEar": bool(hb.get("inEar")),
        "battery": hb.get("battery"),
        "age_s": round(age, 1),
    }


def snapshot() -> Dict[str, Any]:
    card = glance_card()
    st = _load()
    hud = heartbeat()
    return {
        "ok": True,
        "schema": "pocket.wear.v2",
        "wake": "PhoneAI",
        "glasses": {
            "url": "/phoneai/glasses",
            "tunnel": "https://pocket.medinatechlabs.net/phoneai/glasses",
            "note": "Glance cards by default. Stream is optional. Same Wi-Fi or tunnel.",
        },
        "airpods": {
            "url": "/phoneai/airpods",
            "note": "Pair AirPods to the phone. Always listen waits for PhoneAI …",
        },
        "glance": card,
        "focused": card.get("focused"),
        "tabs": card.get("tabs") or [],
        "hud": hud,
        "dictation": bool(st.get("dictation")),
        "buffer": (st.get("buffer") or "")[:200],
        "uses": USES,
        "pair": [
            "AirPods on the phone, not the PC.",
            "Always listen: say PhoneAI then the command.",
            "Dictation: say dictation, speak, then send.",
            "Glasses: glance cards; say stream if you need the JPEG.",
        ],
    }


def _focus_index(tabs: List[Dict[str, Any]], offset: int) -> Optional[Dict[str, Any]]:
    if not tabs:
        return None
    ix = 0
    for i, t in enumerate(tabs):
        if t.get("focused") or t.get("main"):
            ix = i
            break
    nxt = ix + offset
    if nxt < 0:
        nxt = 0
    if nxt >= len(tabs):
        nxt = len(tabs) - 1
    return tabs[nxt]


def _spatial(low: str) -> Optional[Dict[str, Any]]:
    try:
        from pocket.phoneai_portal import windows

        tabs = windows(limit=16).get("windows") or []
    except Exception:
        tabs = []
    if not tabs:
        return None
    hit = None
    if "left window" in low or "window on the left" in low:
        hit = _focus_index(tabs, -1) or tabs[0]
    elif "right window" in low or "window on the right" in low:
        hit = _focus_index(tabs, 1) or (tabs[1] if len(tabs) > 1 else tabs[0])
    else:
        m = re.search(r"\b(first|second|third|1st|2nd|3rd|window (\d+))\b", low)
        if m:
            word = (m.group(1) or "").lower()
            num = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2}.get(word)
            if num is None and m.group(2):
                num = max(0, int(m.group(2)) - 1)
            if num is not None and num < len(tabs):
                hit = tabs[num]
    if not hit:
        return None
    from pocket.phoneai_portal import focus_hwnd

    r = focus_hwnd(int(hit.get("hwnd") or 0), make_main=True)
    title = hit.get("title") or "window"
    return {
        "ok": bool(r.get("ok")),
        "kind": "spatial",
        "reply": f"Main window: {title[:48]}",
        "focus": r,
        "title": title,
    }


def _dictation_cmd(low: str, raw: str) -> Optional[Dict[str, Any]]:
    data = _load()
    if low in ("dictation", "start dictation", "dictate", "dictation lock"):
        data["dictation"] = True
        data["buffer"] = ""
        _save(data)
        return {"ok": True, "kind": "dictation", "on": True, "reply": "Dictation on. Speak. Say send when done."}
    if low in ("stop dictation", "end dictation", "cancel dictation"):
        data["dictation"] = False
        data["buffer"] = ""
        _save(data)
        return {"ok": True, "kind": "dictation", "on": False, "reply": "Dictation off."}
    if data.get("dictation"):
        if low in ("send", "send that", "that's all", "thats all", "done"):
            buf = str(data.get("buffer") or "").strip()
            data["dictation"] = False
            data["buffer"] = ""
            _save(data)
            if not buf:
                return {"ok": True, "kind": "dictation", "reply": "Nothing to send."}
            from pocket.phoneai_portal import touch

            touch("key", nx=0.5, ny=0.5, text=buf, target="desktop")
            return {"ok": True, "kind": "dictation", "sent": True, "reply": f"Sent {len(buf)} characters.", "text": buf[:200]}
        data["buffer"] = (str(data.get("buffer") or "") + (" " if data.get("buffer") else "") + raw).strip()[:4000]
        _save(data)
        return {"ok": True, "kind": "dictation", "on": True, "reply": "Noted.", "buffer": data["buffer"][:120]}
    return None


def ingest(body: Optional[Dict[str, Any]] = None, *, which: str = "portal") -> Dict[str, Any]:
    body = body or {}
    extra = {}
    for k in ("battery", "online", "inEar", "glasses", "airpods"):
        if k in body:
            extra[k] = body.get(k)
    hud = heartbeat(extra) if extra else heartbeat()
    image = str(body.get("image") or "")
    text = str(body.get("text") or body.get("prompt") or body.get("say") or "")
    always = bool(body.get("always"))
    out: Dict[str, Any] = {"hud": hud, "glance": glance_card()}
    if image:
        from pocket.phone_life import save_photo

        photo = save_photo(image, caption=text or "glasses")
        out["photo"] = photo
        if any(k in (text or "").lower() for k in ("error", "coder", "what is this", "fix", "bug")):
            from pocket.phoneai_bridge import work

            asked = text or "What is this error? Read the screenshot context from PhoneAI photos."
            code = work(asked + f"\nPhoto: {photo.get('url')}", engine="grok")
            out.update({"ok": True, "kind": "camera-coder", "reply": str(code.get("reply") or "Saved the photo and asked Coder.")[:400], "coder": code})
            return out
        out.update({"ok": True, "kind": "camera", "reply": photo.get("reply") or "Photo saved."})
        if not text.strip():
            return out
    if not text.strip():
        out.update({"ok": True, "kind": "hud", "reply": out["glance"].get("reply") or "HUD updated."})
        return out
    cmd = command(text, which=which, always=always)
    cmd["hud"] = hud
    cmd["glance"] = out["glance"]
    if out.get("photo"):
        cmd["photo"] = out["photo"]
    return cmd


def command(text: str, *, which: str = "portal", always: bool = False) -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "error": "say something", "reply": "Say PhoneAI look, left window, dictation, or coder plus a task."}
    rest, woke = strip_wake(raw)
    if always and not woke:
        d = _load()
        if d.get("dictation"):
            rest, woke = raw, True
        else:
            return {"ok": True, "kind": "ignore", "reply": "", "wake": False}
    if not rest:
        return {"ok": True, "kind": "wake", "reply": "Listening.", "wake": True}
    low = rest.lower().strip()
    w = "antigravity" if "anti" in (which or "").lower() else "portal"

    dcmd = _dictation_cmd(low, rest)
    if dcmd:
        return dcmd

    if any(k in low for k in ("what can you", "help", "uses", "what do you do")):
        return {"ok": True, "kind": "help", "reply": "Say PhoneAI then look, left window, open Edge, dictation, or coder."}

    if any(k in low for k in ("look", "glance", "what do you see", "what's on screen", "whats on screen", "read screen", "status")):
        card = glance_card()
        return {**card, "wake": woke}

    spat = _spatial(low)
    if spat:
        spat["wake"] = woke
        return spat

    if low.startswith("open ") or low.startswith("launch ") or low.startswith("start "):
        name = rest.split(" ", 1)[-1].strip()
        from pocket.desktop import list_apps, open_app

        apps = list_apps()
        hit = None
        nlow = name.lower()
        for a in apps:
            blob = f"{a.get('id')} {a.get('label')}".lower()
            if nlow in blob or (a.get("id") or "") in nlow:
                if a.get("available"):
                    hit = a
                    break
        if not hit:
            return {"ok": False, "kind": "open", "reply": f"No allowlisted app matching {name}."}
        launched = open_app(str(hit["id"]))
        return {"ok": bool(launched.get("ok")), "kind": "open", "reply": f"Opening {hit.get('label')} on the PC.", "app": hit}

    if low.startswith("focus ") or low.startswith("switch to ") or (" main" in low and low.startswith("make ")):
        title = rest.split(" ", 2)[-1].replace(" main", "").strip()
        if low.startswith("switch to "):
            title = rest[10:].strip()
        from pocket.ui_maneuver import focus_window_title

        r = focus_window_title(title)
        return {"ok": bool(r.get("ok")), "kind": "focus", "focus": r, "reply": f"Making {title} the main window."}

    if "scroll down" in low or "page down" in low:
        from pocket.phoneai_portal import touch

        touch("scroll", nx=0.5, ny=0.5, dy=0.5, target="desktop")
        return {"ok": True, "kind": "scroll", "reply": "Scrolling down."}
    if "scroll up" in low or "page up" in low:
        from pocket.phoneai_portal import touch

        touch("scroll", nx=0.5, ny=0.5, dy=-0.5, target="desktop")
        return {"ok": True, "kind": "scroll", "reply": "Scrolling up."}

    if low.startswith("type ") or low.startswith("enter "):
        from pocket.screen_kernel import type_into

        msg = rest.split(" ", 1)[-1] if " " in rest else rest
        r = type_into(msg, nx=0.5, ny=0.5, click_first=True)
        return {"ok": bool(r.get("ok")), "kind": "type", "reply": "Typed into the field on screen.", "typed": r}
    if "see the screen" in low or low in ("see", "stream", "show screen"):
        from pocket.screen_kernel import see as sk_see

        s = sk_see(which="desktop")
        return {"ok": True, "kind": "see", "reply": "Laptop screen on your glasses.", "see": {"bytes": s.get("bytes"), "title": s.get("title")}}
    if low.startswith("coder ") or low.startswith("code ") or low.startswith("fix ") or low.startswith("implement "):
        from pocket.phoneai_bridge import work

        task = rest.split(" ", 1)[-1] if " " in rest else rest
        r = work(task, engine="grok")
        return {"ok": bool(r.get("ok")), "kind": "coder", "reply": str(r.get("reply") or "Coder is on it.")[:400], "persona": "coder"}

    if low.startswith("remind me") or low.startswith("note "):
        from pocket.phone_life import act as life

        kind = "remind" if low.startswith("remind") else "note"
        r = life(kind, rest)
        return {"ok": True, "kind": kind, "reply": r.get("reply") or "Saved."}

    if "bring" in low and "host" in low:
        from pocket.host_runtime import ensure

        st = ensure("all")
        return {"ok": bool(st.get("ok")), "kind": "runtime", "reply": "Bringing the host up."}

    if "host" in low or "runtime" in low or "is pocket up" in low:
        from pocket.host_runtime import status

        st = status()
        return {"ok": True, "kind": "runtime", "reply": "Host is up." if st.get("up") else "Host is down."}

    if "windows" in low or "tabs" in low or "what's open" in low or "whats open" in low:
        card = glance_card()
        names = ", ".join((x.get("title") or "")[:24] for x in (card.get("tabs") or [])[:8])
        return {"ok": True, "kind": "tabs", "reply": "Open: " + (names or "nothing visible")}

    from pocket.voice_screen import act as vs

    r = vs(rest, which=w)
    r.setdefault("reply", r.get("reply") or "Done.")
    r["via"] = "voice-screen"
    r["wake"] = woke
    return r
