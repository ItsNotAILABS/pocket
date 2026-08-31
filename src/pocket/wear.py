"""Wearables — Meta glasses HUD + AirPods listen/speak on PhoneAI.

Glasses show the live PC. AirPods are the mic and speaker. Same command
loop as Portal: look, focus a window, open a desktop app, scroll, coder.
"""

from __future__ import annotations

from typing import Any, Dict, List

USES: List[Dict[str, str]] = [
    {"id": "glance", "how": "Look — HUD shows the PC + focused window title", "device": "glasses"},
    {"id": "listen", "how": "AirPods mic → SpeechRecognition → command", "device": "airpods"},
    {"id": "speak", "how": "Reply spoken through AirPods (speechSynthesis / TTS)", "device": "airpods"},
    {"id": "focus", "how": "Say switch to Edge / focus Code — that window becomes main", "device": "both"},
    {"id": "open", "how": "Say open Explorer / open Cursor — launches the desktop app", "device": "both"},
    {"id": "scroll", "how": "Say scroll down / scroll up — wheel on the focused PC window", "device": "both"},
    {"id": "click", "how": "Say click File — fusion click on the live screen", "device": "glasses"},
    {"id": "coder", "how": "Say coder … — long-term Grok agent on the family repos", "device": "both"},
    {"id": "type", "how": "Anything else is typed into the focused field on the PC", "device": "airpods"},
    {"id": "life", "how": "Remind me / note this — PhoneAI seat life", "device": "airpods"},
]


def snapshot() -> Dict[str, Any]:
    focused = ""
    try:
        from pocket.phoneai_portal import windows

        w = windows(limit=8)
        focused = w.get("title") or ""
        tabs = w.get("windows") or []
    except Exception:
        w, tabs = {}, []
    return {
        "ok": True,
        "schema": "pocket.wear.v1",
        "glasses": {
            "url": "/phoneai/glasses",
            "tunnel": "https://pocket.medinatechlabs.net/phoneai/glasses",
            "note": "Open this URL in the Meta glasses browser on the same Wi-Fi.",
        },
        "airpods": {
            "url": "/phoneai/airpods",
            "note": "Pair AirPods to the phone. Mic + speaker become listen and speak-back.",
        },
        "focused": focused,
        "tabs": tabs[:8],
        "uses": USES,
        "pair": [
            "AirPods connected to the iPhone / Android, not the PC.",
            "Glasses browser: same LAN as :8787, or the named tunnel.",
            "Tap Listen (or Always listen). Speak. Hear the reply in the buds.",
        ],
    }


def command(text: str, *, which: str = "portal") -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        return {"ok": False, "error": "say something", "reply": "Say look, open Edge, scroll down, or coder plus a task."}
    low = raw.lower().strip()
    w = "antigravity" if "anti" in (which or "").lower() else "portal"

    if any(k in low for k in ("what can you", "help", "uses", "what do you do")):
        names = ", ".join(u["id"] for u in USES)
        return {"ok": True, "kind": "help", "reply": "Glasses plus AirPods. I can " + names + "."}

    if any(k in low for k in ("look", "glance", "what do you see", "what's on screen", "whats on screen", "read screen")):
        from pocket.agent_eyes import see
        from pocket.phoneai_portal import windows

        s = see(which=w)
        s.pop("base64", None)
        win = windows(limit=6)
        title = win.get("title") or "desktop"
        reply = f"Looking at {title}. {len(win.get('windows') or [])} windows."
        return {"ok": True, "kind": "glance", "reply": reply, "see": {"which": s.get("which"), "bytes": s.get("bytes")}, "focus": title}

    if low.startswith("open ") or low.startswith("launch ") or low.startswith("start "):
        name = raw.split(" ", 1)[-1].strip()
        from pocket.desktop import list_apps, open_app

        apps = list_apps()
        hit = None
        nlow = name.lower()
        for a in apps:
            blob = f"{a.get('id')} {a.get('label')}".lower()
            if nlow in blob or blob in nlow or (a.get("id") or "") in nlow:
                if a.get("available"):
                    hit = a
                    break
        if not hit:
            return {"ok": False, "kind": "open", "reply": f"I don't have an allowlisted app matching {name}."}
        launched = open_app(str(hit["id"]))
        return {
            "ok": bool(launched.get("ok")),
            "kind": "open",
            "app": hit,
            "launched": launched,
            "reply": f"Opening {hit.get('label')} on the PC.",
        }

    if low.startswith("focus ") or low.startswith("switch to ") or low.startswith("make ") and " main" in low:
        title = raw.split(" ", 2)[-1].replace(" main", "").strip()
        if low.startswith("switch to "):
            title = raw[10:].strip()
        from pocket.ui_maneuver import focus_window_title

        r = focus_window_title(title)
        return {"ok": bool(r.get("ok")), "kind": "focus", "focus": r, "reply": f"Making {title} the main window."}

    if "scroll down" in low or "page down" in low:
        from pocket.phoneai_portal import touch

        r = touch("scroll", nx=0.5, ny=0.5, dy=0.5, target="desktop")
        return {"ok": True, "kind": "scroll", "reply": "Scrolling down.", **r}
    if "scroll up" in low or "page up" in low:
        from pocket.phoneai_portal import touch

        r = touch("scroll", nx=0.5, ny=0.5, dy=-0.5, target="desktop")
        return {"ok": True, "kind": "scroll", "reply": "Scrolling up.", **r}

    if low.startswith("coder ") or low.startswith("code ") or low.startswith("fix ") or low.startswith("implement "):
        from pocket.phoneai_bridge import work

        task = raw.split(" ", 1)[-1] if " " in raw else raw
        r = work(task, engine="grok")
        reply = str(r.get("reply") or r.get("error") or "Coder is on it.")[:400]
        return {"ok": bool(r.get("ok")), "kind": "coder", "reply": reply, "persona": "coder"}

    if low.startswith("remind me") or low.startswith("note "):
        from pocket.phone_life import act as life

        kind = "remind" if low.startswith("remind") else "note"
        r = life(kind, raw)
        return {"ok": True, "kind": kind, "reply": r.get("reply") or "Saved.", "life": r}

    if "host" in low or "runtime" in low or "is pocket up" in low:
        from pocket.host_runtime import status

        st = status()
        reply = "Host is up." if st.get("up") else "Host is down. Say bring the host up."
        return {"ok": True, "kind": "runtime", "reply": reply, "runtime": {"up": st.get("up"), "always_on": st.get("always_on")}}

    if "bring" in low and "host" in low:
        from pocket.host_runtime import ensure

        st = ensure("all")
        return {"ok": bool(st.get("ok")), "kind": "runtime", "reply": "Bringing the host up.", "runtime": st}

    if "windows" in low or "tabs" in low or "what's open" in low or "whats open" in low:
        from pocket.phoneai_portal import windows

        w = windows(limit=10)
        names = ", ".join((x.get("title") or "")[:28] for x in (w.get("windows") or [])[:8])
        return {"ok": True, "kind": "tabs", "reply": "Open: " + (names or "nothing visible"), "windows": w}

    from pocket.voice_screen import act as vs

    r = vs(raw, which=w)
    r.setdefault("reply", r.get("reply") or "Done.")
    r["via"] = "voice-screen"
    return r
