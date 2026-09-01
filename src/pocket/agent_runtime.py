"""Stronger agent infra: personas, agent↔agent talk, long-term work, PhoneAI sessions.

Agents were failing from the phone because /v1/sessions requires a desk principal.
This module lets PhoneAI mint Pocket sessions (owner=phoneai) or standalone
PhoneAI sessions, with personas and mail so agents talk to each other.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "phoneai"
SESS = ROOT / "sessions.json"
PERSONA_DIR = Path.home() / ".pocket" / "personas"

PERSONAS: List[Dict[str, Any]] = [
    {
        "id": "coder",
        "mode": "grok",
        "engine": "grok",
        "long_term": True,
        "keep": True,
        "seat": "phoneai",
        "blurb": "Grok coding agent — long-term, whole-repo, PhoneAI-native",
    },
    {
        "id": "pocket",
        "mode": "rah",
        "engine": "grok",
        "long_term": True,
        "keep": True,
        "seat": "pocket",
        "blurb": "POCKET host agent — parallel harnesses, workspace, PhoneAI",
    },
    {"id": "researcher", "mode": "grok", "engine": "grok", "long_term": False, "blurb": "Research and explain"},
    {"id": "reviewer", "mode": "claude", "engine": "claude", "long_term": False, "blurb": "Review diffs, short notes"},
    {"id": "shipper", "mode": "build", "engine": "grok", "long_term": False, "blurb": "Package and ship"},
    {"id": "keeper", "mode": "grok", "engine": "grok", "long_term": True, "blurb": "Keeps working until the chat ends"},
    {"id": "anti", "mode": "antigravity", "engine": "antigravity", "long_term": True, "blurb": "Live Antigravity thread"},
    {"id": "spectral", "mode": "grok", "engine": "spectral-agi", "long_term": False, "blurb": "Spectral AGI lane"},
    {"id": "twin", "mode": "grok", "engine": "grok", "long_term": True, "blurb": "Workspace CLI agent in the minted twin"},
    {"id": "claude", "mode": "claude", "engine": "claude", "long_term": False, "blurb": "Claude Code on this PC"},
    {"id": "gemini", "mode": "gemini", "engine": "gemini", "long_term": False, "blurb": "Gemini CLI on this PC"},
    {"id": "auro", "mode": "grok", "engine": "auro", "long_term": False, "blurb": "Local Auro meaning model"},
    {"id": "ghost", "mode": "grok", "engine": "ghost", "long_term": False, "blurb": "Local Ghost math"},
]


def route_think(text: str, engine: str = "auto") -> Dict[str, Any]:
    """Think first. Pick one engine and at most one tool. Do not scan/ship/mint unless asked."""
    e = (engine or "auto").strip().lower()
    low = (text or "").lower()
    if e not in ("", "auto"):
        return {"engine": e, "tool": None, "why": "explicit engine"}
    if any(w in low for w in ("new session", "start a session", "new pocket session")):
        return {"engine": "session", "tool": "session_new", "why": "asked for a session"}
    if "talk to" in low or low.startswith("tell "):
        return {"engine": "talk", "tool": "agent_talk", "why": "agent-to-agent"}
    if any(w in low for w in ("antigravity", "new chat", "agy ")):
        return {"engine": "antigravity", "tool": None, "why": "anti thread"}
    if "ship agent" in low or "package this agent" in low:
        return {"engine": "ship", "tool": "studio_ship", "why": "ship asked"}
    if "mint" in low and "twin" in low:
        return {"engine": "twin", "tool": "twin_mint", "why": "mint asked"}
    if any(w in low for w in ("remind me", "note this", "directions to", "draft a text")):
        return {"engine": "life", "tool": None, "why": "phone life"}
    if any(
        w in low
        for w in ("in parallel", "parallel agents", "fan out", "fan-out", "split the work", "several agents")
    ):
        return {"engine": "rah", "tool": "subagent_steer", "why": "parallel agents"}
    if any(w in low for w in ("portal", "touch the pc", "remote desktop", "stream my screen")):
        return {"engine": "portal", "tool": None, "why": "pc stream"}
    if any(w in low for w in ("prove ", "theorem", "logic prover", "q.e.d")):
        return {"engine": "logic", "tool": None, "why": "logic prover"}
    if any(w in low for w in ("ghost math", "phi ", "hash this", "prime ")):
        return {"engine": "ghost", "tool": None, "why": "ghost math"}
    if any(w in low for w in ("pattern forge", "spectral decompose", "z-depth")):
        return {"engine": "pattern", "tool": None, "why": "pattern forge"}
    if any(w in low for w in ("meaning", "embed this", "auro ")):
        return {"engine": "auro", "tool": None, "why": "auro meaning"}
    if any(w in low for w in ("generate image", "draw ", "imagine ")):
        return {"engine": "imagine", "tool": None, "why": "imagine"}
    if "claude" in low:
        return {"engine": "claude", "tool": None, "why": "claude"}
    if "gemini" in low:
        return {"engine": "gemini", "tool": None, "why": "gemini"}
    if "qwen" in low:
        return {"engine": "qwen", "tool": None, "why": "qwen"}
    if "copilot" in low:
        return {"engine": "copilot", "tool": None, "why": "copilot"}
    if "opencode" in low:
        return {"engine": "opencode", "tool": None, "why": "opencode"}
    if "codex" in low:
        return {"engine": "codex", "tool": None, "why": "codex asked"}
    if any(
        w in low
        for w in (
            "implement",
            "fix this",
            "write code",
            "patch ",
            "test file",
            "coder",
            "maintain repo",
            "large repo",
            "refactor",
        )
    ):
        return {"engine": "grok", "tool": None, "why": "coder grok — long-term family repos"}
    return {"engine": "grok", "tool": None, "why": "think then grok — no extra tools"}


def personas() -> List[Dict[str, Any]]:
    try:
        from pocket.coder_persona import ensure as ensure_coder

        ensure_coder()
    except Exception:
        pass
    overlay: Dict[str, Dict[str, Any]] = {}
    if PERSONA_DIR.is_dir():
        for p in PERSONA_DIR.glob("*.json"):
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(j, dict) and j.get("id"):
                    overlay[str(j["id"])] = j
            except Exception:
                continue
    out: List[Dict[str, Any]] = []
    seen = set()
    for r in PERSONAS:
        i = r.get("id")
        if not i or i in seen:
            continue
        if i in overlay:
            r = {**r, **overlay[i]}
        seen.add(i)
        out.append(r)
    for i, j in overlay.items():
        if i not in seen:
            seen.add(i)
            out.append(j)
    return out


def persona(pid: str) -> Dict[str, Any]:
    p = next((x for x in personas() if x.get("id") == pid), None)
    return p or PERSONAS[0]


def _load_local() -> List[Dict[str, Any]]:
    ROOT.mkdir(parents=True, exist_ok=True)
    if SESS.is_file():
        try:
            data = json.loads(SESS.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def _save_local(rows: List[Dict[str, Any]]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    SESS.write_text(json.dumps(rows[:80], indent=2, default=str), encoding="utf-8")


def talk(from_agent: str, to_agent: str, text: str, *, subject: str = "") -> Dict[str, Any]:
    """Agent ↔ agent: local mail + mesh bus."""
    mail = {}
    mesh = {}
    try:
        from pocket.agent_mail import send as mail_send

        mail = mail_send(from_agent=from_agent, to=to_agent, subject=subject or "talk", body=text)
    except Exception as e:
        mail = {"ok": False, "error": str(e)[:160]}
    try:
        from pocket.mesh_disk import send_message

        mesh = send_message(from_agent, to_agent, text, kind="talk", encrypt=True)
    except Exception as e:
        mesh = {"ok": False, "error": str(e)[:160]}
    return {
        "ok": bool(mail.get("ok") or mesh.get("ok")),
        "mail": mail,
        "mesh": mesh,
        "from": from_agent,
        "to": to_agent,
    }


def create_phoneai_session(
    *,
    persona_id: str = "researcher",
    title: str = "",
    kind: str = "pocket",
    long_term: Optional[bool] = None,
) -> Dict[str, Any]:
    """New session from PhoneAI: Pocket desk session and/or PhoneAI-local."""
    per = persona(persona_id)
    mode = per.get("mode") or "grok"
    engine = per.get("engine") or "grok"
    keep = per.get("long_term") if long_term is None else bool(long_term)
    if per.get("id") == "coder":
        keep = True if long_term is None else bool(long_term)
        try:
            from pocket.coder_persona import ensure as ensure_coder

            ensure_coder()
        except Exception:
            pass
    kind = (kind or "pocket").lower()
    title = (title or f"PhoneAI · {per.get('id')} · {mode}")[:80]
    out: Dict[str, Any] = {"ok": True, "persona": per, "kind": kind}

    try:
        from pocket.twin_mint import mint

        mint("phoneai")
    except Exception:
        pass

    if kind in ("pocket", "both", "desk"):
        try:
            from pocket.sessions import create_session
            from pocket.platform_space import tenant_cwd

            cwd = tenant_cwd("phoneai", "twin")
            sess = create_session(
                mode=mode if mode != "antigravity" else "grok",
                title=title,
                workspace="tenant:phoneai",
                cwd=cwd,
                owner="phoneai",
            )
            out["pocket_session"] = sess
            if keep:
                try:
                    from pocket.keep_agents import start as keep_start

                    keep_start(session_id=sess.get("id") or "", goal=title, with_browser=False)
                    out["keep"] = True
                except Exception as e:
                    out["keep"] = str(e)[:120]
        except Exception as e:
            out["pocket_session"] = {"ok": False, "error": str(e)[:200]}
            out["ok"] = False

    if kind in ("phoneai", "both", "local"):
        row = {
            "id": "pa-" + uuid.uuid4().hex[:10],
            "kind": "phoneai",
            "persona": per.get("id"),
            "engine": engine,
            "title": title,
            "created": time.time(),
            "status": "idle",
            "long_term": keep,
        }
        rows = _load_local()
        rows.insert(0, row)
        _save_local(rows)
        out["phoneai_session"] = row

    return out


def list_phoneai_sessions(limit: int = 30) -> Dict[str, Any]:
    local = _load_local()[:limit]
    pocket = []
    try:
        from pocket.sessions import list_sessions

        pocket = [s for s in list_sessions(limit, owner="phoneai", admin=False)]
    except Exception:
        pass
    return {"ok": True, "phoneai": local, "pocket": pocket, "personas": personas()}
