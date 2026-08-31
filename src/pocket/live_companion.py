"""POCKET Live — Gemini-backed seat agent in the floating chat.

Lives to work, explain, help, and use the platform. Gemini API when a key
is set; otherwise answers from the local technology atlas so the chat
never goes dark.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from pocket.gemini_voice import DEFAULT_MODEL, get_gemini_key
from pocket.tech_atlas import catalog, compact_context

SYSTEM = """You are POCKET Live, the always-on seat agent inside POCKET / PhoneAI kernel OS (ItsNotAI Labs).
You live to work, explain, help, and use the platform.
Keep replies concise (2–8 sentences) unless the user asks for a full list.
You know: Desk, Phone, PhoneAI kernel OS, Imagine, Voice/Aria, Work Studio, Agent Mail, Novae, Grok/Codex/Claude/Gemini/Qwen CLIs, MCP, NEXUS receipts.
When listing technology, use the atlas context. Never invent APIs that are not in context.
If they want to open a surface, name the path (e.g. /desk, /phoneai, /imagine).
Be a coworker, not a brochure."""


def _gemini_turn(text: str, history: Optional[List[Dict[str, str]]], context: str) -> Dict[str, Any]:
    key = get_gemini_key()
    if not key:
        return {"ok": False, "error": "no_gemini_key"}
    contents: List[Dict[str, Any]] = []
    for h in (history or [])[-10:]:
        role = "user" if h.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": str(h.get("text") or h.get("content") or "")[:2500]}]})
    blob = text
    if context:
        blob = f"[Platform atlas]\n{context}\n\n[User]\n{text}"
    contents.append({"role": "user", "parts": [{"text": blob[:6000]}]})
    model = DEFAULT_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={urllib.parse.quote(key)}"
    )
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 700},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "POCKET-Live/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace") or "{}")
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            detail = str(e)
        return {"ok": False, "error": f"gemini_http_{e.code}", "detail": detail}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
    reply = ""
    for cand in data.get("candidates") or []:
        for part in ((cand.get("content") or {}).get("parts") or []):
            if part.get("text"):
                reply += str(part.get("text"))
    reply = (reply or "").strip()
    if not reply:
        return {"ok": False, "error": "empty_gemini_reply"}
    return {"ok": True, "reply": reply, "engine": "gemini", "model": model}


def _platform_use(text: str) -> Dict[str, Any]:
    """Actually read the live host so the agent can work, not just talk."""
    used: List[str] = []
    bits: List[str] = []
    low = (text or "").lower()

    try:
        from pocket.model_clis import inventory as cli_inventory

        clis = cli_inventory()
        if any(w in low for w in ("cli", "model", "grok", "codex", "claude", "gemini", "qwen", "status", "ready", "work")):
            ready = [t["id"] for t in clis.get("tools") or [] if t.get("available")]
            bits.append("CLIs ready: " + (", ".join(ready) if ready else "none"))
            used.append("clis")
    except Exception:
        clis = {}

    try:
        from pocket.executor import available_engines

        eng = available_engines()
        if any(w in low for w in ("engine", "status", "work", "run", "codex", "grok", "claude")):
            on = [k for k, v in eng.items() if v is True and k in ("codex", "claude", "grok", "shell", "wsl")]
            bits.append("Engines: " + ", ".join(on or ["shell"]))
            used.append("engines")
    except Exception:
        eng = {}

    try:
        from pocket.users import list_users

        if any(w in low for w in ("seat", "user", "who", "signup", "login")):
            names = [u.get("user") for u in list_users() if u.get("user")]
            bits.append("Seats: " + ", ".join(names[:12]) + (f" (+{len(names)-12})" if len(names) > 12 else ""))
            used.append("seats")
    except Exception:
        pass

    try:
        from pocket.sessions import list_sessions

        if any(w in low for w in ("session", "job", "running", "work")):
            sess = list_sessions(limit=8, admin=True)
            bits.append("Recent sessions: " + str(len(sess)))
            used.append("sessions")
    except Exception:
        pass

    if any(w in low for w in ("health", "up", "status", "alive")):
        bits.append("Host heart is beating on :8787.")
        used.append("health")

    return {"used": used, "notes": bits, "clis": clis if isinstance(clis, dict) else {}, "engines": eng if isinstance(eng, dict) else {}}


def _local_reply(text: str) -> Dict[str, Any]:
    data = catalog()
    low = (text or "").lower()
    if any(w in low for w in ("open", "go", "launch", "show")):
        apps = sorted(data["apps"], key=lambda a: -len(a["name"]))
        for a in apps:
            if a["id"] in low or a["name"].lower() in low:
                return {
                    "ok": True,
                    "reply": f"Opening {a['name']} — {a['role']}. Path {a['url']}.",
                    "engine": "local",
                    "open": a["url"],
                }
    if any(w in low for w in ("tech", "stack", "repos", "apps", "list", "atlas", "what do i have", "technology")):
        lines = ["Here is your POCKET × PhoneAI technology:"]
        for layer in data["stack"]:
            lines.append(f"• {layer['layer']}: " + ", ".join(layer["items"]))
        lines.append("")
        lines.append("Repos on this PC:")
        for p in data["products"]:
            mark = "ready" if p.get("on_disk") else "missing"
            langs = ", ".join(p.get("languages") or []) or "—"
            lines.append(f"• {p['name']} ({mark}) — {langs}")
        use = _platform_use("cli status")
        if use.get("notes"):
            lines.append("")
            lines.extend("• " + n if not n.startswith("CLIs") else "• " + n for n in use["notes"])
        lines.append("Ask me to open Desk, PhoneAI Kernel, Imagine, or Voice.")
        return {"ok": True, "reply": "\n".join(lines), "engine": "local", "used": use.get("used") or []}
    if any(w in low for w in ("webmcp", "what can i click", "every action", "list actions", "functions on")):
        try:
            from pocket.webmcp import catalog as webmcp_cat

            c = webmcp_cat()
            src = ", ".join(c.get("sources") or [])
            sample = ", ".join((a.get("name") or "")[:40] for a in (c.get("actions") or [])[:12])
            return {
                "ok": True,
                "reply": f"WebMCP has {c.get('count')} actions from {src}. Sample: {sample}. Open /webmcp or ask PhoneAI to webmcp_list.",
                "engine": "local",
                "open": "/webmcp",
            }
        except Exception:
            pass
    if "phoneai" in low or "kernel" in low:
        return {
            "ok": True,
            "reply": "PhoneAI is the phone-native kernel OS: pair the handset, run typed capabilities, NEXUS receipts. Open /phoneai for the kernel home (apps grid + live agent).",
            "engine": "local",
            "open": "/phoneai",
        }
    if "gemini" in low:
        return {
            "ok": True,
            "reply": "I use the Gemini API when GEMINI_API_KEY is in ~/.pocket/keys.env. The Gemini CLI is also installed for seats. Without a key I still explain and route from the local atlas.",
            "engine": "local",
        }
    use = _platform_use(text)
    if use.get("notes") and any(w in low for w in ("status", "health", "cli", "engine", "seat", "session", "ready", "work")):
        return {
            "ok": True,
            "reply": "Live host check:\n• " + "\n• ".join(use["notes"]),
            "engine": "local",
            "used": use.get("used") or [],
        }
    if any(w in low for w in ("help", "what can you", "who are you")):
        return {
            "ok": True,
            "reply": "I'm POCKET Live. I work, explain, help, and use this platform. Ask me to list your technology, check status/CLIs, open Desk / PhoneAI Kernel / Imagine, or walk a repo.",
            "engine": "local",
        }
    # topic search
    hits = []
    for p in data["products"]:
        blob = " ".join([p.get("name", ""), " ".join(p.get("technology") or []), " ".join(p.get("languages") or [])]).lower()
        if any(tok in blob for tok in re.findall(r"[a-z0-9-]{3,}", low)):
            hits.append(p["name"] + ": " + ", ".join((p.get("technology") or [])[:6]))
    if hits:
        return {"ok": True, "reply": "Related to that:\n• " + "\n• ".join(hits[:6]), "engine": "local"}
    return {
        "ok": True,
        "reply": "I can list all your technology, explain PhoneAI kernel OS, or open Desk, Phone, Imagine, Voice, Mail. What should we do?",
        "engine": "local",
    }


def chat(text: str, *, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "say something"}
    local = _local_reply(text)
    use = _platform_use(text)
    extra = compact_context()
    if use.get("notes"):
        extra = extra + "\n\n[Live host]\n" + "\n".join(use["notes"])
    # Prefer Gemini when configured, but keep local open-action if we detected one
    g = _gemini_turn(text, history, extra)
    if g.get("ok"):
        out = {
            "ok": True,
            "reply": g["reply"],
            "engine": "gemini",
            "model": g.get("model"),
            "companion": "POCKET Live",
        }
        if local.get("open"):
            out["open"] = local["open"]
        if use.get("used"):
            out["used"] = use["used"]
        return out
    local["companion"] = "POCKET Live"
    local["gemini"] = g
    if use.get("used") and not local.get("used"):
        local["used"] = use["used"]
    return local


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "name": "POCKET Live",
        "gemini": bool(get_gemini_key()),
        "model": DEFAULT_MODEL if get_gemini_key() else "local-atlas",
        "hint": "Set GEMINI_API_KEY in ~/.pocket/keys.env for the Gemini brain. Chat still works from the atlas without it.",
    }
