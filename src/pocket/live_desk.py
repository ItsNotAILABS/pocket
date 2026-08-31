"""Real desk — Grok / Codex / Antigravity / Pocket threads that already exist.

PhoneAI was talking to an empty sandbox. This module lists the live
conversations and project folders so the phone continues the same work.
"""

from __future__ import annotations

import json
import time
import re
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
        if (
            "worktrees/" in s
            or "github.com/" in s
            or "file://" in s
            or s.startswith("C:\\")
            or s.startswith("{")
            or (" " in s and not s.startswith("sessionID"))
        ):
            out.append(s)
    return out[:40]


def _humanize_app(raw: str) -> str:
    from urllib.parse import unquote

    s = unquote((raw or "").replace("\\", "/")).strip().strip('"')
    s = re.sub(r"[:\]]+[a-z]{0,8}file:?$", "", s, flags=re.I)
    s = s.split("?")[0].rstrip("/")
    if "worktrees/" in s:
        s = s.split("worktrees/", 1)[-1]
    if "github.com/" in s:
        s = s.split("github.com/", 1)[-1]
        if s.endswith(".git"):
            s = s[:-4]
        s = s.split("/")[-1]
    s = Path(s).name if (":" in s or s.startswith("/")) and "/" in s else s
    s = s.replace("(Never Delete)", "").replace("%20", " ")
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip(" .")
    drop = {"build", "src", "app", "main"}
    words = [w for w in s.split(" ") if w and w.lower() not in drop]
    titled = []
    for w in words:
        if w.isupper() or w[:1].isupper() and w[1:].islower() is False and len(w) <= 6:
            titled.append(w)
        else:
            titled.append(w[:1].upper() + w[1:].lower() if w else w)
    name = " ".join(titled) or "Antigravity"
    return name[:72]


def _name_antigravity(strings: List[str], db_id: str) -> Dict[str, str]:
    """AI-style name from the real app (worktree / GitHub), not the hex db id."""
    import re

    app = ""
    leaf = ""
    github = ""
    cwd = ""
    for s in strings:
        t = s.replace("\\", "/")
        if "worktrees/" in t:
            rest = t.split("worktrees/", 1)[-1]
            parts = [p for p in rest.split("/") if p and p not in ("#",)]
            if parts:
                app = re.split(r"[#?\"]", parts[0])[0]
            if len(parts) > 1:
                leaf = re.split(r"[#?\"]", parts[1])[0]
            path = t.split("file:///", 1)[-1] if "file:///" in t else ""
            if path:
                cwd = path.replace("/", "\\")
        if "github.com/" in t:
            github = t.split("github.com/", 1)[-1]
            github = re.split(r"[#?\"\s]", github)[0].removesuffix(".git")
        if not cwd and ("Users/" in t or ":/" in t.lower()) and "file://" in t:
            cwd = t.replace("file:///", "").replace("/", "\\")
    app_h = _humanize_app(app) if app else ""
    leaf_h = _humanize_app(leaf) if leaf else ""
    gh_h = _humanize_app(github.split("/")[-1]) if github else ""
    if app_h and leaf_h and leaf_h.lower() not in app_h.lower():
        title = f"{app_h} — {leaf_h}"
    elif app_h:
        title = app_h
    elif gh_h:
        title = gh_h
    elif cwd:
        title = _humanize_app(Path(cwd).name)
    else:
        title = f"Antigravity {db_id[:8]}"
    return {"title": title[:120], "app": app_h or title, "github": github, "cwd": cwd[:260]}


def real_antigravity_apps() -> List[Dict[str, str]]:
    root = Path.home() / ".gemini" / "antigravity" / "worktrees"
    rows: List[Dict[str, str]] = []
    if not root.is_dir():
        return rows
    for p in sorted(root.iterdir(), key=_mtime, reverse=True):
        if not p.is_dir():
            continue
        rows.append(
            {
                "id": p.name,
                "name": _humanize_app(p.name),
                "path": str(p),
                "updated": _mtime(p),
            }
        )
    return rows[:24]


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
            named = _name_antigravity(strings, db.stem)
            cwd = named.get("cwd") or ""
            snippet = named.get("title") or ""
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
                "title": named.get("title") or db.stem,
                "app": named.get("app") or "",
                "github": named.get("github") or "",
                "cwd": cwd,
                "updated": _mtime(db),
                "kind": "conversation",
                "steps": nsteps,
                "snippet": snippet,
                "file": str(db),
                "named": True,
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
        "antigravity_apps": real_antigravity_apps(),
        "you_are_building": (agy[0] if agy else None),
        "note": (
            "Antigravity desk is a direct view of the real Antigravity window and worktree. "
            "Threads are named from the app, not hex ids."
        ),
    }


def pick_thread(engine: str = "", thread_id: str = "") -> Optional[Dict[str, Any]]:
    import os

    live = (os.environ.get("GROK_SESSION_ID") or "").strip()
    d = desk(limit=20)
    if thread_id:
        if live and thread_id == live:
            return None
        if str(thread_id).startswith(("s-", "pa-")):
            return None
        for bucket in ("grok", "codex", "pocket", "antigravity_threads"):
            for t in d.get(bucket) or []:
                if t.get("id") == thread_id:
                    return t
        return None
    # Do not auto-attach the newest Grok thread — that is often the live
    # operator session and resuming it from PhoneAI deadlocks both UIs.
    return None
