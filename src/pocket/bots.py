"""POCKET Bots — Grok-Bot-style teammates powered by pocket-agent.

Each bot is a named persistent teammate with:
  · its own computer (workspace under ~/.pocket/bots/<id>/computer)
  · a message thread you pick up later
  · pocket-agent harness + RLM (internal, not a third-party bot API)
  · optional always-on pulse so work continues after you step away
  · ability to hand work to other Pocket bots

Create by describing the job in plain language, or pick a starter.
"""

from __future__ import annotations

import json
import re
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "bots"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_pulses: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}

STARTERS: List[Dict[str, str]] = [
    {
        "name": "Ops",
        "job": "Office operations — follow-ups, checklists, keep work moving",
        "color": "#34d399",
        "engine": "genetic",
    },
    {
        "name": "Research",
        "job": "Look things up, brief you, leave notes on the bot computer",
        "color": "#38bdf8",
        "engine": "genetic",
    },
    {
        "name": "Coder",
        "job": "Ship patches and plans in this bot's computer",
        "color": "#22c55e",
        "engine": "genetic",
    },
    {
        "name": "Math",
        "job": "Internal proofs, gcd, primes, hashes — zero third-party CAS",
        "color": "#c4b5fd",
        "engine": "ghost",
    },
    {
        "name": "Chief",
        "job": "Coordinate other Pocket bots and only ping you for judgment calls",
        "color": "#a78bfa",
        "engine": "genetic",
    },
]


def _slug(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (name or "bot").strip()).strip("-").lower()
    return (s or "bot")[:40]


def _bot_dir(bid: str) -> Path:
    p = ROOT / bid
    (p / "computer" / "files").mkdir(parents=True, exist_ok=True)
    (p / "computer" / "notes").mkdir(parents=True, exist_ok=True)
    (p / "thread").mkdir(parents=True, exist_ok=True)
    return p


def _meta_path(bid: str) -> Path:
    return _bot_dir(bid) / "bot.json"


def _thread_path(bid: str) -> Path:
    return _bot_dir(bid) / "thread" / "messages.jsonl"


def _load_meta(bid: str) -> Optional[Dict[str, Any]]:
    fp = _meta_path(bid)
    if not fp.is_file():
        return None
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_meta(rec: Dict[str, Any]) -> None:
    bid = rec.get("id") or ""
    if not bid:
        return
    rec["updated_at"] = time.time()
    _meta_path(bid).write_text(json.dumps(rec, indent=2), encoding="utf-8")


def _append_msg(bid: str, role: str, text: str, **extra: Any) -> Dict[str, Any]:
    msg = {
        "id": uuid.uuid4().hex[:12],
        "role": role,
        "text": (text or "")[:20000],
        "ts": time.time(),
        **extra,
    }
    with _lock:
        fp = _thread_path(bid)
        with fp.open("a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    return msg


def _read_thread(bid: str, *, limit: int = 80) -> List[Dict[str, Any]]:
    fp = _thread_path(bid)
    if not fp.is_file():
        return []
    lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    for ln in lines[-max(1, min(limit, 200)) :]:
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out


def list_computer(bid: str, *, limit: int = 24) -> List[Dict[str, Any]]:
    root = _bot_dir(bid) / "computer"
    items = []
    for p in sorted(root.rglob("*"), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".json", ".py", ".html"}:
            st = p.stat()
            items.append(
                {
                    "name": p.name,
                    "rel": str(p.relative_to(root)).replace("\\", "/"),
                    "bytes": st.st_size,
                    "mtime": st.st_mtime,
                }
            )
        if len(items) >= limit:
            break
    return items


def public_view(rec: Dict[str, Any]) -> Dict[str, Any]:
    bid = rec.get("id") or ""
    return {
        "id": bid,
        "name": rec.get("name"),
        "job": rec.get("job"),
        "color": rec.get("color") or "#34d399",
        "engine": rec.get("engine") or "genetic",
        "always_on": bool(rec.get("always_on")),
        "status": rec.get("status") or "ready",
        "runs": int(rec.get("runs") or 0),
        "last_at": rec.get("last_at") or 0,
        "last_goal": rec.get("last_goal") or "",
        "owner": rec.get("owner") or "",
        "computer": str(_bot_dir(bid) / "computer"),
        "pulsing": bid in _threads and _threads[bid].is_alive(),
        "ui": "/bots",
    }


def list_bots(*, owner: str = "") -> List[Dict[str, Any]]:
    ensure_starters(owner=owner or "pocket")
    out = []
    for fp in sorted(ROOT.glob("*/bot.json")):
        try:
            rec = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if owner and rec.get("owner") and rec.get("owner") != owner:
            continue
        out.append(public_view(rec))
    out.sort(key=lambda x: x.get("last_at") or 0, reverse=True)
    return out


def get_bot(bid: str) -> Optional[Dict[str, Any]]:
    rec = _load_meta(_slug(bid))
    return public_view(rec) if rec else None


def ensure_starters(*, owner: str = "pocket") -> None:
    existing = {p.parent.name for p in ROOT.glob("*/bot.json")}
    if existing:
        return
    for s in STARTERS:
        create_bot(name=s["name"], job=s["job"], color=s["color"], engine=s["engine"], owner=owner)


def create_bot(
    *,
    name: str,
    job: str = "",
    color: str = "",
    engine: str = "genetic",
    always_on: bool = False,
    owner: str = "pocket",
    system: str = "",
) -> Dict[str, Any]:
    bid = _slug(name)
    if not bid:
        return {"ok": False, "error": "name required"}
    rec = _load_meta(bid) or {}
    rec.update(
        {
            "id": bid,
            "name": (name or bid).strip()[:80],
            "job": (job or "Teammate on this host")[:400],
            "color": color or rec.get("color") or "#34d399",
            "engine": engine or "genetic",
            "always_on": bool(always_on),
            "owner": owner,
            "system": (system or "")[:4000],
            "status": "ready",
            "runs": int(rec.get("runs") or 0),
            "created_at": rec.get("created_at") or time.time(),
        }
    )
    _bot_dir(bid)
    readme = _bot_dir(bid) / "computer" / "COMPUTER.md"
    if not readme.exists():
        readme.write_text(
            f"# {rec['name']} computer\n\n"
            f"This is this bot's machine inside POCKET — files, notes, plans.\n"
            f"Job: {rec['job']}\nEngine: {rec['engine']} (pocket-agent + internal models)\n",
            encoding="utf-8",
        )
    _save_meta(rec)
    if always_on:
        start_pulse(bid)
    return {"ok": True, **public_view(rec)}


def create_from_prompt(prompt: str, *, owner: str = "pocket") -> Dict[str, Any]:
    """Grok-Bot style: describe the teammate in plain language."""
    text = (prompt or "").strip()
    if not text:
        return {"ok": False, "error": "describe the bot you want"}
    low = text.lower()
    engine = "genetic"
    color = "#34d399"
    if any(k in low for k in ("math", "proof", "gcd", "prime", "hash")):
        engine, color = "ghost", "#c4b5fd"
    elif any(k in low for k in ("code", "patch", "bug", "repo")):
        engine, color = "genetic", "#22c55e"
    elif any(k in low for k in ("research", "brief", "lookup")):
        engine, color = "genetic", "#38bdf8"
    elif any(k in low for k in ("chief", "coordinate", "manage bots")):
        engine, color = "genetic", "#a78bfa"
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", text)
    name = " ".join(words[:2]) if words else "Teammate"
    if "named" in low:
        m = re.search(r"named\s+([A-Za-z][A-Za-z0-9_-]+)", text, re.I)
        if m:
            name = m.group(1)
    rec = create_bot(name=name, job=text[:400], engine=engine, color=color, owner=owner)
    if rec.get("ok"):
        _append_msg(rec["id"], "system", f"Hired as a Pocket bot. Job: {text[:400]}")
    return rec


def delete_bot(bid: str) -> Dict[str, Any]:
    bid = _slug(bid)
    stop_pulse(bid)
    d = ROOT / bid
    if not d.exists():
        return {"ok": False, "error": "not found"}
    import shutil

    shutil.rmtree(d, ignore_errors=True)
    return {"ok": True, "deleted": bid}


def _ensure_pocket_agent_path() -> None:
    src = Path.home() / "OneDrive" / "pocket-agent" / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _run_engine(rec: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Run pocket-agent first; fall back to internal models."""
    bid = rec["id"]
    computer = str(_bot_dir(bid) / "computer" / "files")
    engine = (rec.get("engine") or "genetic").lower()
    system = (
        f"You are {rec.get('name')}, a POCKET Bot teammate. "
        f"Job: {rec.get('job')}. You work on your own computer at {computer}. "
        f"You are not a generic chatbot. Use internal POCKET models. "
        f"{rec.get('system') or ''}"
    ).strip()
    summary = ""
    meta: Dict[str, Any] = {"engine": engine}

    _ensure_pocket_agent_path()
    try:
        from pocket_agent.agent import Agent
        from pocket_agent.harness import Harness

        h = Harness(project=f"bot-{bid}")
        h.set_goal(rec.get("job") or text)
        if rec.get("job"):
            h.remember(f"job={rec.get('job')}")
        agent = Agent(cwd=computer, project=f"bot-{bid}")
        agent.harness = h
        full = f"{system}\n\nUSER:\n{text}"
        result = agent.run(full)
        summary = result.summary or ""
        meta.update(result.meta or {})
        meta["runtime"] = "pocket-agent"
    except Exception as e:
        meta["pocket_agent_error"] = str(e)[:200]
        try:
            from pocket.internal_models import express_one, run_job

            model_id = "ghost" if engine in ("ghost", "math", "logic") else "heuristic"
            if engine in ("logic",):
                model_id = "logic"
            if engine in ("pattern",):
                model_id = "pattern"
            if engine in ("world",):
                model_id = "world"
            if engine in ("genetic", "coder", "ops", "research"):
                r = run_job(f"{system}\n\n{text}", cwd=computer)
                summary = (r.get("text") or r.get("markdown") or json.dumps(r)[:8000]) if isinstance(r, dict) else str(r)
                meta["runtime"] = "genetic"
            else:
                r = express_one(model_id, text)
                summary = r.text or r.error or ""
                meta["runtime"] = f"internal:{model_id}"
        except Exception as e2:
            summary = f"Bot computer noted the task. Runtime unavailable: {e2}"[:800]
            meta["runtime"] = "note"

    note = _bot_dir(bid) / "computer" / "notes" / f"run-{int(time.time())}.md"
    note.write_text(
        f"# {rec.get('name')} run\n\n**task:** {text[:800]}\n\n{summary[:12000]}\n",
        encoding="utf-8",
    )
    return {"ok": True, "reply": (summary or "Noted on my computer.").strip()[:16000], "meta": meta, "note": str(note)}


def message(bid: str, text: str, *, owner: str = "") -> Dict[str, Any]:
    bid = _slug(bid)
    rec = _load_meta(bid)
    if not rec:
        return {"ok": False, "error": "bot not found"}
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty message"}
    _append_msg(bid, "user", text, owner=owner)
    # Chief can fan out to other bots
    extra = ""
    if "chief" in (rec.get("name") or "").lower() or "coordinate" in (rec.get("job") or "").lower():
        others = [b for b in list_bots(owner=owner or rec.get("owner") or "") if b["id"] != bid][:4]
        if others and any(k in text.lower() for k in ("all bots", "team", "everyone", "coordinate")):
            for other in others:
                try:
                    message(other["id"], f"[from {rec.get('name')}] {text}", owner=owner)
                except Exception:
                    pass
            extra = f"\n\n_Also pinged {len(others)} teammate(s)._"
    run = _run_engine(rec, text)
    reply = (run.get("reply") or "") + extra
    _append_msg(bid, "bot", reply, meta=run.get("meta") or {})
    rec["runs"] = int(rec.get("runs") or 0) + 1
    rec["last_at"] = time.time()
    rec["last_goal"] = text[:400]
    rec["status"] = "ready"
    _save_meta(rec)
    return {
        "ok": True,
        "bot": public_view(rec),
        "reply": reply,
        "meta": run.get("meta") or {},
        "thread": _read_thread(bid, limit=40),
        "computer": list_computer(bid),
    }


def thread(bid: str, *, limit: int = 80) -> Dict[str, Any]:
    rec = _load_meta(_slug(bid))
    if not rec:
        return {"ok": False, "error": "bot not found"}
    return {
        "ok": True,
        "bot": public_view(rec),
        "messages": _read_thread(rec["id"], limit=limit),
        "computer": list_computer(rec["id"]),
    }


def start_pulse(bid: str, *, interval_sec: int = 180) -> Dict[str, Any]:
    bid = _slug(bid)
    rec = _load_meta(bid)
    if not rec:
        return {"ok": False, "error": "bot not found"}
    stop_pulse(bid)
    ev = threading.Event()
    _pulses[bid] = ev

    def loop() -> None:
        while not ev.wait(max(60, interval_sec)):
            goal = rec.get("last_goal") or rec.get("job") or "standby on my computer"
            try:
                message(bid, f"[always-on pulse] Continue: {goal}")
            except Exception:
                pass

    t = threading.Thread(target=loop, name=f"pocket-bot-{bid}", daemon=True)
    _threads[bid] = t
    rec["always_on"] = True
    rec["status"] = "pulsing"
    _save_meta(rec)
    t.start()
    return {"ok": True, **public_view(rec)}


def stop_pulse(bid: str) -> Dict[str, Any]:
    bid = _slug(bid)
    ev = _pulses.pop(bid, None)
    if ev:
        ev.set()
    rec = _load_meta(bid)
    if rec:
        rec["always_on"] = False
        rec["status"] = "ready"
        _save_meta(rec)
        return {"ok": True, **public_view(rec)}
    return {"ok": True, "id": bid, "always_on": False}


def catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "product": "POCKET Bots",
        "schema": "pocket.bots.v1",
        "like": "Grok Bot teammates — named, own computer, message like a colleague, keep working",
        "runtime": "pocket-agent + internal models (no third-party bot API)",
        "ui": "/bots",
        "starters": STARTERS,
        "bots": list_bots(),
        "api": {
            "list": "GET /v1/bots",
            "create": "POST /v1/bots",
            "from_prompt": "POST /v1/bots/hire",
            "message": "POST /v1/bots/{id}/message",
            "thread": "GET /v1/bots/{id}",
            "always_on": "POST /v1/bots/{id}/pulse",
        },
    }
