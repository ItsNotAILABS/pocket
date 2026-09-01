"""Named agents with faces, DMs, group chats, and mail.

Every first-class agent gets a display name, a deterministic face, a
@agents.pocket.local mailbox, and a DM thread. Group rooms are local
JSONL chats. Email still goes through pocket.agent_mail.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "agent_social"
ROSTER = ROOT / "roster.json"
ROOMS = ROOT / "rooms"
DMS = ROOT / "dm"
FACES = ROOT / "faces"
for _d in (ROOT, ROOMS, DMS, FACES):
    _d.mkdir(parents=True, exist_ok=True)

_lock = Lock()
PRODUCT = "POCKET Agents"
SCHEMA = "pocket.agent_social.v1"
DOMAIN = "agents.pocket.local"


def _safe(aid: str) -> str:
    s = re.sub(r"[^a-z0-9._\-]+", "-", (aid or "").strip().lower())
    return (s.strip("-._") or f"agent-{uuid.uuid4().hex[:8]}")[:48]


def _hue(aid: str) -> int:
    h = hashlib.sha256(aid.encode("utf-8")).hexdigest()
    return int(h[:4], 16) % 360


def _initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s_\-]+", (name or "").strip()) if p]
    if not parts:
        return "A"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def face_svg(agent_id: str, *, name: str = "") -> str:
    aid = _safe(agent_id)
    hue = _hue(aid)
    hue2 = (hue + 42) % 360
    label = _initials(name or aid)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{aid}">'
        f'<defs><linearGradient id="g{aid[:8]}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="hsl({hue},72%,48%)"/>'
        f'<stop offset="100%" stop-color="hsl({hue2},64%,28%)"/>'
        f"</linearGradient></defs>"
        f'<rect width="64" height="64" rx="20" fill="url(#g{aid[:8]})"/>'
        f'<circle cx="32" cy="22" r="11" fill="#f8fafc" opacity=".95"/>'
        f'<ellipse cx="32" cy="48" rx="18" ry="14" fill="#f8fafc" opacity=".95"/>'
        f'<text x="32" y="62" text-anchor="middle" font-family="ui-sans-serif,system-ui" '
        f'font-size="9" font-weight="700" fill="#0f172a">{label}</text>'
        f"</svg>"
    )


def face_url(agent_id: str) -> str:
    return f"/v1/agents/face/{_safe(agent_id)}.svg"


def _load_roster() -> Dict[str, Any]:
    if ROSTER.is_file():
        try:
            data = json.loads(ROSTER.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("agents", {})
                return data
        except Exception:
            pass
    return {"schema": SCHEMA, "agents": {}}


def _save_roster(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = ROSTER.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.replace(ROSTER)


def _seed_from_catalog() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        from pocket.agent_mail import DEFAULT_AGENTS

        for aid, name, blurb in DEFAULT_AGENTS:
            rows.append({"id": aid, "name": name, "blurb": blurb, "kind": "mail"})
    except Exception:
        pass
    try:
        from pocket.first_class_agents import build_registry

        for a in (build_registry().get("agents") or [])[:80]:
            rows.append(
                {
                    "id": a.get("id"),
                    "name": a.get("name") or a.get("id"),
                    "blurb": a.get("blurb") or a.get("role") or "",
                    "kind": a.get("kind") or "desk",
                    "color": a.get("color") or "",
                    "group": a.get("group") or "",
                    "engine": a.get("engine") or "",
                }
            )
    except Exception:
        pass
    return rows


def ensure_roster() -> Dict[str, Any]:
    """Give every known agent a name, face, mailbox, and DM identity."""
    with _lock:
        data = _load_roster()
        acc = data.setdefault("agents", {})
        changed = False
        for row in _seed_from_catalog():
            aid = _safe(str(row.get("id") or ""))
            if not aid:
                continue
            rec = acc.get(aid) or {}
            if not rec.get("name"):
                rec["name"] = str(row.get("name") or aid)[:80]
                changed = True
            rec.setdefault("id", aid)
            rec.setdefault("blurb", str(row.get("blurb") or "")[:200])
            rec.setdefault("kind", row.get("kind") or "agent")
            rec.setdefault("group", row.get("group") or "")
            rec.setdefault("engine", row.get("engine") or "")
            rec.setdefault("color", row.get("color") or f"hsl({_hue(aid)},70%,48%)")
            rec["face"] = face_url(aid)
            rec["address"] = f"{aid}@{DOMAIN}"
            rec.setdefault("created_at", time.time())
            rec["active"] = True
            acc[aid] = rec
        if changed or not data.get("updated_at"):
            data["updated_at"] = time.time()
            _save_roster(data)
    try:
        from pocket.agent_mail import create_account, ensure_defaults

        ensure_defaults()
        for aid, rec in list((_load_roster().get("agents") or {}).items())[:80]:
            create_account(aid, name=rec.get("name") or aid, blurb=rec.get("blurb") or "")
    except Exception:
        pass
    with _lock:
        n = len(_load_roster().get("agents") or {})
    return {"ok": True, "seeded": n}


def name_agent(agent_id: str, name: str, *, blurb: str = "", face_note: str = "") -> Dict[str, Any]:
    aid = _safe(agent_id)
    if not aid:
        return {"ok": False, "error": "agent_id required"}
    with _lock:
        data = _load_roster()
        rec = data.setdefault("agents", {}).get(aid) or {"id": aid}
        rec["name"] = (name or aid).strip()[:80]
        if blurb:
            rec["blurb"] = blurb[:200]
        if face_note:
            rec["face_note"] = face_note[:120]
        rec["face"] = face_url(aid)
        rec["address"] = f"{aid}@{DOMAIN}"
        rec["active"] = True
        rec["updated_at"] = time.time()
        data["agents"][aid] = rec
        data["updated_at"] = time.time()
        _save_roster(data)
    try:
        from pocket.agent_mail import create_account

        create_account(aid, name=rec["name"], blurb=rec.get("blurb") or "")
    except Exception:
        pass
    return {"ok": True, "agent": rec}


def list_people(*, limit: int = 80) -> Dict[str, Any]:
    with _lock:
        empty = not (_load_roster().get("agents") or {})
    if empty:
        ensure_roster()
    with _lock:
        rows = list((_load_roster().get("agents") or {}).values())
    rows = [r for r in rows if r.get("active") is not False]
    rows.sort(key=lambda r: str(r.get("name") or r.get("id") or ""))
    return {"ok": True, "product": PRODUCT, "count": len(rows[:limit]), "agents": rows[:limit]}


def person(agent_id: str) -> Dict[str, Any]:
    aid = _safe(agent_id)
    with _lock:
        rec = (_load_roster().get("agents") or {}).get(aid)
    if not rec:
        ensure_roster()
        with _lock:
            rec = (_load_roster().get("agents") or {}).get(aid)
    if not rec:
        return {"ok": False, "error": f"no agent {aid}"}
    return {"ok": True, "agent": rec, "svg": face_svg(aid, name=rec.get("name") or aid)}


def _thread_id(a: str, b: str) -> str:
    x, y = sorted((_safe(a), _safe(b)))
    return f"{x}__{y}"


def _append_jsonl(path: Path, rec: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def _read_jsonl(path: Path, *, limit: int = 80) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    out: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    for line in lines[-limit:]:
        try:
            rec = json.loads(line)
            if isinstance(rec, dict):
                out.append(rec)
        except Exception:
            continue
    return out


def dm(from_agent: str, to: str, text: str, *, also_email: bool = False) -> Dict[str, Any]:
    """Instant DM between two agents. Optional copy into Agent Mail."""
    src = _safe(from_agent)
    dst = _safe(to)
    body = (text or "").strip()[:8000]
    if not body:
        return {"ok": False, "error": "text required"}
    if src == dst:
        return {"ok": False, "error": "cannot DM yourself"}
    mid = "dm-" + uuid.uuid4().hex[:12]
    rec = {
        "id": mid,
        "schema": SCHEMA,
        "kind": "dm",
        "from": src,
        "to": dst,
        "text": body,
        "created_at": time.time(),
    }
    tid = _thread_id(src, dst)
    _append_jsonl(DMS / f"{tid}.jsonl", rec)
    mail: Optional[Dict[str, Any]] = None
    if also_email:
        try:
            from pocket.agent_mail import send as mail_send

            mail = mail_send(
                from_agent=src,
                to=dst,
                subject=f"DM from {src}",
                body=body,
            )
        except Exception as e:
            mail = {"ok": False, "error": str(e)[:160]}
    return {"ok": True, "dm": rec, "thread": tid, "mail": mail}


def thread(a: str, b: str, *, limit: int = 80) -> Dict[str, Any]:
    tid = _thread_id(a, b)
    msgs = _read_jsonl(DMS / f"{tid}.jsonl", limit=limit)
    return {"ok": True, "thread": tid, "count": len(msgs), "messages": msgs}


def email_agents(from_agent: str, to: str, *, subject: str = "", body: str = "") -> Dict[str, Any]:
    from pocket.agent_mail import send as mail_send

    return mail_send(from_agent=from_agent, to=to, subject=subject or "(no subject)", body=body)


def create_group(
    name: str,
    *,
    members: Optional[List[str]] = None,
    owner: str = "system",
) -> Dict[str, Any]:
    gid = "g-" + uuid.uuid4().hex[:10]
    mem = [_safe(m) for m in (members or []) if _safe(m)]
    owner_id = _safe(owner)
    if owner_id and owner_id not in mem:
        mem.insert(0, owner_id)
    rec = {
        "id": gid,
        "schema": SCHEMA,
        "kind": "group",
        "name": (name or "group").strip()[:80],
        "members": mem[:32],
        "owner": owner_id,
        "created_at": time.time(),
    }
    (ROOMS / f"{gid}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return {"ok": True, "group": rec}


def list_groups(*, limit: int = 40) -> Dict[str, Any]:
    rows = []
    for fp in sorted(ROOMS.glob("g-*.json")):
        try:
            rec = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(rec, dict):
                rec["messages"] = len(_read_jsonl(ROOMS / f"{rec.get('id')}.jsonl", limit=500))
                rows.append(rec)
        except Exception:
            continue
    return {"ok": True, "count": len(rows[:limit]), "groups": rows[:limit]}


def group_post(group_id: str, from_agent: str, text: str) -> Dict[str, Any]:
    gid = (group_id or "").strip()
    meta_path = ROOMS / f"{gid}.json"
    if not meta_path.is_file():
        return {"ok": False, "error": "group not found"}
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": False, "error": "bad group"}
    src = _safe(from_agent)
    members = [str(m) for m in (meta.get("members") or [])]
    if src not in members:
        members.append(src)
        meta["members"] = members
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    body = (text or "").strip()[:8000]
    if not body:
        return {"ok": False, "error": "text required"}
    rec = {
        "id": "gm-" + uuid.uuid4().hex[:12],
        "kind": "group",
        "group": gid,
        "from": src,
        "text": body,
        "created_at": time.time(),
    }
    _append_jsonl(ROOMS / f"{gid}.jsonl", rec)
    return {"ok": True, "message": rec, "group": meta}


def group_messages(group_id: str, *, limit: int = 80) -> Dict[str, Any]:
    gid = (group_id or "").strip()
    meta_path = ROOMS / f"{gid}.json"
    if not meta_path.is_file():
        return {"ok": False, "error": "group not found"}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "group": meta,
        "messages": _read_jsonl(ROOMS / f"{gid}.jsonl", limit=limit),
    }


def status() -> Dict[str, Any]:
    people = list_people(limit=200)
    groups = list_groups(limit=80)
    dms = list(DMS.glob("*.jsonl"))
    return {
        "ok": True,
        "product": PRODUCT,
        "schema": SCHEMA,
        "agents": people.get("count") or 0,
        "groups": groups.get("count") or 0,
        "dm_threads": len(dms),
        "mail_domain": DOMAIN,
        "ui": "/agents",
        "doctrine": (
            "Agents have names and faces. They DM and email each other. "
            "Group chats are first-class rooms on this host."
        ),
    }
