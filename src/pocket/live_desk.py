"""Real desk — Grok / Codex / Antigravity / Pocket threads that already exist.

PhoneAI was talking to an empty sandbox. This module lists the live
conversations and project folders so the phone continues the same work.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

GROK_SESS = Path.home() / ".grok" / "sessions"
CODEX_SESS = Path.home() / ".codex" / "sessions"


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except Exception:
        return 0.0


def grok_threads(limit: int = 12) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not GROK_SESS.is_dir():
        return out
    sums = sorted(GROK_SESS.rglob("summary.json"), key=_mtime, reverse=True)
    for sm in sums:
        if len(out) >= limit:
            break
        try:
            j = json.loads(sm.read_text(encoding="utf-8"))
        except Exception:
            continue
        info = j.get("info") or {}
        sid = str(info.get("id") or sm.parent.name)
        cwd = str(info.get("cwd") or "")
        title = str(j.get("session_summary") or sid)[:120]
        out.append(
            {
                "engine": "grok",
                "id": sid,
                "title": title,
                "cwd": cwd,
                "messages": j.get("num_messages") or j.get("num_chat_messages") or 0,
                "updated": _mtime(sm),
                "kind": "conversation",
            }
        )
    return out


def codex_threads(limit: int = 12) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not CODEX_SESS.is_dir():
        return out
    files = sorted(
        [p for p in CODEX_SESS.rglob("*") if p.is_file() and "rollout" in p.name.lower()],
        key=_mtime,
        reverse=True,
    )
    for fp in files:
        if len(out) >= limit:
            break
        sid = ""
        cwd = ""
        title = fp.stem
        try:
            with fp.open(encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh):
                    if i > 40:
                        break
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("type") == "session_meta":
                        pl = rec.get("payload") or {}
                        sid = str(pl.get("session_id") or pl.get("id") or "")
                        cwd = str(pl.get("cwd") or "")
                    if rec.get("type") in ("event_msg", "response_item") and not title:
                        pass
        except Exception:
            continue
        if not sid:
            # filename rollout-...-UUID.json
            parts = fp.stem.split("-")
            if len(parts) >= 5:
                sid = "-".join(parts[-5:])
        out.append(
            {
                "engine": "codex",
                "id": sid or fp.stem,
                "title": title[:120],
                "cwd": cwd,
                "updated": _mtime(fp),
                "kind": "conversation",
                "file": str(fp),
            }
        )
    return out


def pocket_threads(limit: int = 8) -> List[Dict[str, Any]]:
    try:
        from pocket.sessions import list_sessions

        rows = list_sessions(limit, admin=True)
    except Exception:
        rows = []
    out = []
    for s in rows:
        out.append(
            {
                "engine": s.get("mode") or "pocket",
                "id": s.get("id"),
                "title": s.get("title") or s.get("id"),
                "cwd": s.get("cwd") or "",
                "updated": s.get("updated") or s.get("created") or 0,
                "kind": "pocket-session",
                "thread": s.get("engine_thread_id") or s.get("codex_session_id") or "",
            }
        )
    return out


def _agy_strings(blob: bytes, min_len: int = 18) -> List[str]:
    import re

    out = []
    for m in re.findall(rb"[\x20-\x7e]{" + str(min_len).encode() + rb",}", blob or b""):
        try:
            s = m.decode("ascii")
        except Exception:
            continue
        if s.startswith("file://") or s.startswith("C:\\") or s.startswith("{"):
            out.append(s)
        elif " " in s and not s.startswith("sessionID"):
            out.append(s)
    return out[:40]


def antigravity_threads(limit: int = 12) -> List[Dict[str, Any]]:
    """Read live Antigravity conversations from ~/.gemini/antigravity/conversations."""
    conv = Path.home() / ".gemini" / "antigravity" / "conversations"
    out: List[Dict[str, Any]] = []
    if not conv.is_dir():
        return out
    dbs = sorted(conv.glob("*.db"), key=_mtime, reverse=True)
    import sqlite3

    for db in dbs:
        if len(out) >= limit:
            break
        try:
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
            cur = con.cursor()
            blob = b""
            try:
                row = cur.execute("SELECT data FROM trajectory_metadata_blob LIMIT 1").fetchone()
                blob = row[0] if row and row[0] else b""
            except Exception:
                pass
            strings = _agy_strings(blob, 12)
            cwd = ""
            title = db.stem[:12]
            for s in strings:
                if s.startswith("file:///"):
                    cwd = s.replace("file:///", "").replace("/", "\\")
                    if cwd[1:2] == ":":
                        pass
                    title = Path(cwd).name or title
                    break
                if ":\\" in s and "Users" in s:
                    cwd = s
                    title = Path(s).name or title
                    break
            snippet = ""
            try:
                gen = cur.execute("SELECT data FROM gen_metadata ORDER BY idx DESC LIMIT 8").fetchall()
                for (g,) in gen:
                    for s in _agy_strings(g or b"", 24):
                        if len(s) > 28 and not s.startswith("{") and "sessionID" not in s:
                            snippet = s[:160]
                            break
                    if snippet:
                        break
            except Exception:
                pass
            try:
                nsteps = cur.execute("SELECT COUNT(*) FROM steps").fetchone()[0]
            except Exception:
                nsteps = 0
            con.close()
        except Exception:
            continue
        out.append(
            {
                "engine": "antigravity",
                "id": db.stem,
                "title": (title or db.stem)[:120],
                "cwd": cwd,
                "updated": _mtime(db),
                "kind": "conversation",
                "steps": nsteps,
                "snippet": snippet,
                "file": str(db),
            }
        )
    return out


def antigravity_state() -> Dict[str, Any]:
    p = Path.home() / "AppData" / "Roaming" / "Antigravity" / "app_storage.json"
    data: Dict[str, Any] = {"installed": p.exists() or (Path.home() / "AppData" / "Local" / "Programs" / "Antigravity").exists()}
    if p.is_file():
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            data["last_project_id"] = j.get("lastCreatedProjectId")
            data["running"] = True
        except Exception:
            pass
    exe = Path.home() / "AppData" / "Local" / "Programs" / "Antigravity" / "Antigravity.exe"
    data["exe"] = str(exe) if exe.is_file() else ""
    return data


def desk(*, limit: int = 8) -> Dict[str, Any]:
    grok = grok_threads(limit)
    codex = codex_threads(limit)
    pocket = pocket_threads(limit)
    agy = antigravity_threads(limit)
    anti = antigravity_state()
    anti["threads"] = len(agy)
    # Default live thread: newest grok not in empty phoneai sandbox if others exist
    live = None
    for t in grok:
        cwd = (t.get("cwd") or "").replace("\\", "/").lower()
        if "phoneai_ws" in cwd and any("phoneai_ws" not in (x.get("cwd") or "").replace("\\", "/").lower() for x in grok):
            continue
        live = t
        break
    if not live and grok:
        live = grok[0]
    if not live and agy:
        live = agy[0]
    if not live and codex:
        live = codex[0]
    return {
        "ok": True,
        "you_are_working_on": live,
        "grok": grok,
        "codex": codex,
        "pocket": pocket,
        "antigravity": anti,
        "antigravity_threads": agy,
        "note": (
            "PhoneAI must attach to these threads — not ~/.pocket/phoneai_ws unless you pick it. "
            "Grok resume --resume ID; Codex exec resume ID; Antigravity opens the PC app on that cwd."
        ),
    }


def pick_thread(engine: str = "", thread_id: str = "") -> Optional[Dict[str, Any]]:
    d = desk(limit=20)
    if thread_id:
        for bucket in ("grok", "codex", "pocket", "antigravity_threads"):
            for t in d.get(bucket) or []:
                if t.get("id") == thread_id:
                    return t
    if engine in ("grok", "codex"):
        rows = d.get(engine) or []
        return rows[0] if rows else d.get("you_are_working_on")
    if engine in ("antigravity", "anti", "agy"):
        rows = d.get("antigravity_threads") or []
        return rows[0] if rows else d.get("you_are_working_on")
    return d.get("you_are_working_on")
