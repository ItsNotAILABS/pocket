"""POCKET Community Share — intentional public posts only.

Doctrine:
  · Nothing is public by default
  · Users must explicitly Share to Community
  · No private chats, keys, or host paths leak into the feed
  · Feed is host-local (this Pocket instance's users)
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "community"
FEED_FILE = ROOT / "shares.jsonl"
META_FILE = ROOT / "meta.json"
_lock = Lock()

KINDS = frozenset(
    {
        "chat",
        "image",
        "video",
        "blog",
        "paper",
        "social",
        "storyboard",
        "caption",
        "export",
        "note",
        "other",
    }
)

# Block accidental secret / private path leaks in public text
_SECRET_RE = re.compile(
    r"(sk_pocket_|sk-|api[_-]?key|password\s*[:=]|Bearer\s+\S+|"
    r"LOCALAPPDATA|\\\\Users\\\\|/home/\w+/\.ssh)",
    re.I,
)


def _ensure() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    if not FEED_FILE.exists():
        FEED_FILE.write_text("", encoding="utf-8")
    if not META_FILE.exists():
        META_FILE.write_text(
            json.dumps({"schema": "pocket.community.v1", "created_at": time.time()}, indent=2),
            encoding="utf-8",
        )


def _sanitize_text(text: str, *, max_len: int = 8000) -> str:
    t = (text or "").strip()
    if _SECRET_RE.search(t):
        t = _SECRET_RE.sub("[redacted]", t)
    # strip absolute home paths
    home = str(Path.home())
    if home and home in t:
        t = t.replace(home, "~")
    return t[:max_len]


def _safe_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if u.startswith(("/", "https://", "http://", "data:image/")):
        # disallow file:// and localhost secrets
        if "file:" in u.lower():
            return ""
        return u[:2000]
    return ""


def share(
    *,
    author: str = "anonymous",
    display_name: str = "",
    title: str = "",
    body: str = "",
    kind: str = "note",
    tags: Optional[List[str]] = None,
    media_url: str = "",
    preview: str = "",
    source: str = "creative_studio",
    artifact: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Publish one intentional share to the community feed."""
    _ensure()
    kind_n = (kind or "note").strip().lower()
    if kind_n not in KINDS:
        kind_n = "other"
    author_n = re.sub(r"[^a-zA-Z0-9_\-\.]", "", (author or "anonymous").strip())[:40] or "anonymous"
    title_n = _sanitize_text(title or kind_n.title(), max_len=160)
    body_n = _sanitize_text(body, max_len=8000)
    if not body_n and not media_url:
        return {"ok": False, "error": "body or media_url required to share"}

    rec: Dict[str, Any] = {
        "id": "shr-" + uuid.uuid4().hex[:12],
        "schema": "pocket.community.share.v1",
        "author": author_n,
        "display_name": _sanitize_text(display_name or author_n, max_len=80),
        "title": title_n,
        "body": body_n,
        "preview": _sanitize_text(preview or body_n[:280], max_len=320),
        "kind": kind_n,
        "tags": [str(t)[:32] for t in (tags or []) if str(t).strip()][:12],
        "media_url": _safe_url(media_url),
        "source": (source or "creative_studio")[:64],
        "at": time.time(),
        "intentional": True,
        "public": True,
    }
    if artifact and isinstance(artifact, dict):
        # only allow small public-safe metadata
        rec["artifact"] = {
            k: artifact.get(k)
            for k in ("mode", "preset", "export_name", "media_kind", "agent")
            if artifact.get(k) is not None
        }

    line = json.dumps(rec, ensure_ascii=False, default=str)
    with _lock:
        with open(FEED_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    return {"ok": True, "share": rec, "message": "Shared to Pocket community (intentional)"}


def list_shares(
    *,
    limit: int = 40,
    kind: str = "",
    author: str = "",
    q: str = "",
) -> Dict[str, Any]:
    """Newest-first public intentional shares."""
    _ensure()
    limit = max(1, min(int(limit or 40), 100))
    rows: List[Dict[str, Any]] = []
    try:
        raw = FEED_FILE.read_text(encoding="utf-8")
    except OSError:
        raw = ""
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if not rec.get("intentional") or rec.get("public") is False:
            continue
        if kind and rec.get("kind") != kind:
            continue
        if author and rec.get("author") != author:
            continue
        if q:
            blob = f"{rec.get('title','')} {rec.get('body','')} {rec.get('preview','')} {' '.join(rec.get('tags') or [])}".lower()
            if q.lower() not in blob:
                continue
        rows.append(rec)
    rows.sort(key=lambda r: float(r.get("at") or 0), reverse=True)
    total = len(rows)
    rows = rows[:limit]
    return {
        "ok": True,
        "schema": "pocket.community.feed.v1",
        "count": len(rows),
        "total_matched": total,
        "shares": rows,
        "doctrine": "Only intentional public shares appear here — nothing auto-posts.",
        "at": time.time(),
    }


def get_share(share_id: str) -> Dict[str, Any]:
    sid = (share_id or "").strip()
    if not sid:
        return {"ok": False, "error": "id required"}
    feed = list_shares(limit=100)
    for s in feed.get("shares") or []:
        if s.get("id") == sid:
            return {"ok": True, "share": s}
    # scan full file for older items
    _ensure()
    try:
        for line in FEED_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("id") == sid:
                return {"ok": True, "share": rec}
    except OSError:
        pass
    return {"ok": False, "error": "not found", "id": sid}


def unshare(share_id: str, *, author: str = "") -> Dict[str, Any]:
    """Soft-remove: rewrite feed without this share (author must match if set)."""
    _ensure()
    sid = (share_id or "").strip()
    if not sid:
        return {"ok": False, "error": "id required"}
    kept: List[str] = []
    removed = None
    with _lock:
        try:
            lines = FEED_FILE.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                kept.append(line)
                continue
            if rec.get("id") == sid:
                if author and rec.get("author") != author and author not in ("pocket", "admin", "owner"):
                    return {"ok": False, "error": "not your share"}
                removed = rec
                continue
            kept.append(line)
        FEED_FILE.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    if not removed:
        return {"ok": False, "error": "not found", "id": sid}
    return {"ok": True, "removed": removed.get("id"), "message": "Share removed from community feed"}


def status() -> Dict[str, Any]:
    feed = list_shares(limit=5)
    return {
        "ok": True,
        "product": "POCKET Community Share",
        "path": str(FEED_FILE),
        "recent": feed.get("count") or 0,
        "total_sample": feed.get("total_matched") or 0,
        "kinds": sorted(KINDS),
        "api": {
            "feed": "GET /v1/community",
            "share": "POST /v1/community/share",
            "get": "GET /v1/community/{id}",
            "unshare": "POST /v1/community/unshare",
        },
        "ui": "/studio/create#community",
        "doctrine": "Opt-in only. Users share on purpose.",
    }
