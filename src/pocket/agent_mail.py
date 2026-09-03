"""POCKET Agent Mail — our own email accounts + inboxes for every agent.

Product: POCKET AGENT MAIL
Protocol: POCKET-AGENT-MAIL/1.0

Doctrine:
  · Every desk/phone agent can own an address on agents.pocket.local
  · Inboxes are first-class (not just SMTP outbox)
  · Agent↔agent mail is local and free (no third party)
  · External SMTP still goes through POCKET MAIL when configured
  · Models / engines / MCP all call the same Python APIs

Addresses:
  {agent_id}@agents.pocket.local
  e.g. assist@agents.pocket.local, codex@agents.pocket.local

Storage:
  ~/.pocket/agent_mail/
    accounts.json
    {agent_id}/inbox/*.json
    {agent_id}/sent/*.json
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "agent_mail"
ACCOUNTS = ROOT / "accounts.json"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = Lock()

PRODUCT = "POCKET AGENT MAIL"
PROTOCOL = "POCKET-AGENT-MAIL/1.0"
SCHEMA = "pocket.agent_mail.v1"
DOMAIN = "agents.pocket.local"

# Seed accounts for first-class agents (created on first status)
DEFAULT_AGENTS = [
    ("assist", "Assistant", "Digital life · research · drafts"),
    ("codex", "Codex", "Coding agent"),
    ("claude", "Claude", "Claude Agent SDK"),
    ("grok", "Grok", "Grok coding & research"),
    ("auro", "Auro", "Local LMR · meaning"),
    ("muse_spark", "Muse Spark", "Multimodal · research lanes"),
    ("voice", "Aria", "Voice product · speak-back"),
    ("work", "Working", "Life ops · working board"),
    ("browser", "Browser", "Website interface engine"),
    ("genetic", "Genetic Flow", "Internal model evolution"),
    ("archon", "ARCHON", "Platform orchestrator"),
    ("navigator", "Navigator", "Web · life · travel"),
    ("scribe", "Scribe", "Compose · email · drafts"),
    ("system", "POCKET System", "Official system notices"),
    ("coder", "Coder", "PhoneAI Grok coding agent"),
    ("pocket", "POCKET", "Host orchestrator"),
    ("phoneai", "PhoneAI", "Phone seat"),
]


def _safe_id(agent_id: str) -> str:
    s = re.sub(r"[^a-z0-9._\-]+", "-", (agent_id or "").strip().lower())
    s = s.strip("-._")[:48]
    return s or f"agent-{uuid.uuid4().hex[:8]}"


def address_for(agent_id: str) -> str:
    return f"{_safe_id(agent_id)}@{DOMAIN}"


def _agent_dirs(agent_id: str) -> Dict[str, Path]:
    aid = _safe_id(agent_id)
    base = ROOT / aid
    inbox = base / "inbox"
    sent = base / "sent"
    for d in (base, inbox, sent):
        d.mkdir(parents=True, exist_ok=True)
    return {"base": base, "inbox": inbox, "sent": sent}


def _load_accounts() -> Dict[str, Any]:
    if ACCOUNTS.is_file():
        try:
            return json.loads(ACCOUNTS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "domain": DOMAIN, "accounts": {}}


def _save_accounts(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = ACCOUNTS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.replace(ACCOUNTS)


def ensure_defaults() -> None:
    """Create default agent accounts if missing."""
    with _lock:
        data = _load_accounts()
        acc = data.setdefault("accounts", {})
        changed = False
        for aid, name, blurb in DEFAULT_AGENTS:
            if aid not in acc:
                acc[aid] = {
                    "id": aid,
                    "name": name,
                    "blurb": blurb,
                    "address": address_for(aid),
                    "created_at": time.time(),
                    "kind": "agent",
                    "active": True,
                }
                _agent_dirs(aid)
                changed = True
        if changed:
            data["updated_at"] = time.time()
            _save_accounts(data)


def create_account(
    agent_id: str,
    *,
    name: str = "",
    blurb: str = "",
    kind: str = "agent",
    owner: str = "",
) -> Dict[str, Any]:
    """Create our own agent email account (inbox + sent)."""
    aid = _safe_id(agent_id)
    if not aid:
        return {"ok": False, "error": "agent_id required"}
    with _lock:
        data = _load_accounts()
        acc = data.setdefault("accounts", {})
        if aid in acc and acc[aid].get("active") is not False:
            rec = acc[aid]
            _agent_dirs(aid)
            return {
                "ok": True,
                "created": False,
                "account": rec,
                "message": f"Account already exists: {rec.get('address')}",
            }
        rec = {
            "id": aid,
            "name": (name or aid).strip()[:80],
            "blurb": (blurb or f"POCKET agent {aid}")[:200],
            "address": address_for(aid),
            "created_at": time.time(),
            "kind": (kind or "agent").strip().lower()[:32],
            "owner": (owner or "").strip().lower()[:64],
            "active": True,
        }
        acc[aid] = rec
        data["updated_at"] = time.time()
        _save_accounts(data)
        _agent_dirs(aid)
    return {
        "ok": True,
        "created": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "account": rec,
        "message": f"Created {rec['address']}",
    }


def list_accounts(*, limit: int = 100) -> Dict[str, Any]:
    ensure_defaults()
    with _lock:
        data = _load_accounts()
        rows = list((data.get("accounts") or {}).values())
    rows = [r for r in rows if r.get("active") is not False]
    rows.sort(key=lambda r: str(r.get("id") or ""))
    # attach unread counts
    out = []
    for r in rows[:limit]:
        aid = r.get("id") or ""
        unread = _count_unread(aid)
        out.append({**r, "unread": unread})
    return {
        "ok": True,
        "product": PRODUCT,
        "domain": DOMAIN,
        "count": len(out),
        "accounts": out,
    }


def get_account(agent_id: str) -> Dict[str, Any]:
    ensure_defaults()
    aid = _safe_id(agent_id)
    # allow lookup by full address
    if "@" in (agent_id or ""):
        local = (agent_id or "").split("@", 1)[0]
        aid = _safe_id(local)
    with _lock:
        data = _load_accounts()
        rec = (data.get("accounts") or {}).get(aid)
    if not rec:
        return {"ok": False, "error": f"no account for {aid}", "hint": "POST /v1/agent-mail/accounts"}
    return {
        "ok": True,
        "account": {**rec, "unread": _count_unread(aid)},
        "paths": {k: str(v) for k, v in _agent_dirs(aid).items()},
    }


def _count_unread(agent_id: str) -> int:
    d = _agent_dirs(agent_id)["inbox"]
    n = 0
    for p in d.glob("*.json"):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            if not r.get("read"):
                n += 1
        except Exception:
            continue
    return n


def _resolve_agent(addr_or_id: str) -> str:
    s = (addr_or_id or "").strip().lower()
    if "@" in s:
        local, _, dom = s.partition("@")
        if dom and dom not in (DOMAIN, "localhost", "pocket.local"):
            # external address — not a local agent id
            return ""
        return _safe_id(local)
    return _safe_id(s)


def send(
    *,
    from_agent: str,
    to: str,
    subject: str = "",
    body: str = "",
    cc: str = "",
    tags: Optional[List[str]] = None,
    external: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Send agent mail: local inbox delivery + optional external SMTP.

    - Local @agents.pocket.local → writes into recipient inbox
    - External addresses → POCKET MAIL SMTP when external=True
    """
    ensure_defaults()
    from_id = _resolve_agent(from_agent) or _safe_id(from_agent)
    # ensure sender account
    create_account(from_id)
    sender = get_account(from_id).get("account") or {}
    from_addr = sender.get("address") or address_for(from_id)

    to_raw = (to or "").strip()
    if not to_raw:
        return {"ok": False, "error": "to required"}

    mid = "am-" + uuid.uuid4().hex[:12]
    now = time.time()
    rec: Dict[str, Any] = {
        "id": mid,
        "schema": SCHEMA,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "from": from_addr,
        "from_agent": from_id,
        "to": to_raw,
        "cc": (cc or "").strip(),
        "subject": (subject or "(no subject)")[:200],
        "body": (body or "")[:50000],
        "tags": list(tags or [])[:12],
        "created_at": now,
        "read": False,
        "folder": "sent",
    }

    to_id = _resolve_agent(to_raw)
    delivered_local = False
    external_result: Optional[Dict[str, Any]] = None

    if dry_run:
        rec["status"] = "dry_run"
        return {"ok": True, "dry_run": True, "mail": rec, "message": "Dry-run — not delivered"}

    # Local agent delivery
    if to_id:
        create_account(to_id)
        dirs = _agent_dirs(to_id)
        inbox_rec = {**rec, "folder": "inbox", "status": "delivered", "delivered_at": now}
        (dirs["inbox"] / f"{mid}.json").write_text(
            json.dumps(inbox_rec, indent=2, default=str), encoding="utf-8"
        )
        delivered_local = True
        rec["status"] = "delivered_local"
        rec["to_agent"] = to_id
    elif external or ("@" in to_raw and not to_raw.endswith(DOMAIN)):
        # External via POCKET MAIL
        try:
            from pocket.pocket_mail import send as mail_send

            external_result = mail_send(
                to=to_raw,
                subject=rec["subject"],
                body=rec["body"],
                template="custom",
                owner=from_id,
                dry_run=False,
            )
            rec["external"] = {
                "ok": external_result.get("ok"),
                "message": external_result.get("message"),
                "mail_id": (external_result.get("mail") or {}).get("id"),
            }
            rec["status"] = "sent_external" if external_result.get("ok") else "external_failed"
        except Exception as e:
            external_result = {"ok": False, "error": str(e)[:200]}
            rec["status"] = "external_failed"
            rec["external"] = external_result
    else:
        # Unknown local — create recipient account and deliver
        create_account(to_raw)
        to_id = _safe_id(to_raw)
        dirs = _agent_dirs(to_id)
        inbox_rec = {**rec, "folder": "inbox", "status": "delivered", "delivered_at": now, "to": address_for(to_id)}
        (dirs["inbox"] / f"{mid}.json").write_text(
            json.dumps(inbox_rec, indent=2, default=str), encoding="utf-8"
        )
        delivered_local = True
        rec["status"] = "delivered_local"
        rec["to_agent"] = to_id
        rec["to"] = address_for(to_id)

    # Always keep sender sent copy
    sent_dir = _agent_dirs(from_id)["sent"]
    (sent_dir / f"{mid}.json").write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")

    ok = delivered_local or bool((external_result or {}).get("ok"))
    if ok:
        try:
            from pocket.live_events import emit

            emit("mail", f"{from_id} → {rec.get('to_agent') or to_raw}: {rec['subject']}", agent=from_id[:24].upper(), role="mail")
        except Exception:
            pass
        try:
            from pocket.mesh_disk import send_message

            send_message(from_id, rec.get("to_agent") or to_raw, rec["body"][:2000], kind="mail", encrypt=True)
        except Exception:
            pass
    return {
        "ok": ok,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "mail": rec,
        "delivered_local": delivered_local,
        "external": external_result,
        "message": (
            f"Delivered to {rec.get('to_agent') or to_raw} inbox"
            if delivered_local
            else (rec.get("status") or "queued")
        ),
    }


def inbox(
    agent_id: str,
    *,
    limit: int = 30,
    unread_only: bool = False,
) -> Dict[str, Any]:
    """List inbox for an agent account."""
    ensure_defaults()
    aid = _resolve_agent(agent_id) or _safe_id(agent_id)
    create_account(aid)
    d = _agent_dirs(aid)["inbox"]
    rows: List[Dict[str, Any]] = []
    for p in sorted(d.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[: max(limit * 2, 40)]:
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            if unread_only and r.get("read"):
                continue
            rows.append(
                {
                    "id": r.get("id"),
                    "from": r.get("from"),
                    "from_agent": r.get("from_agent"),
                    "to": r.get("to"),
                    "subject": r.get("subject"),
                    "preview": (r.get("body") or "")[:160],
                    "read": bool(r.get("read")),
                    "at": r.get("delivered_at") or r.get("created_at"),
                    "tags": r.get("tags") or [],
                    "status": r.get("status"),
                }
            )
        except Exception:
            continue
        if len(rows) >= limit:
            break
    return {
        "ok": True,
        "agent": aid,
        "address": address_for(aid),
        "unread": _count_unread(aid),
        "count": len(rows),
        "items": rows,
    }


def read_message(agent_id: str, mail_id: str, *, mark_read: bool = True) -> Dict[str, Any]:
    """Read one message from agent inbox (or sent)."""
    aid = _resolve_agent(agent_id) or _safe_id(agent_id)
    mid = (mail_id or "").strip()
    if not mid:
        return {"ok": False, "error": "mail_id required"}
    dirs = _agent_dirs(aid)
    path = None
    for folder in ("inbox", "sent"):
        p = dirs[folder] / f"{mid}.json"
        if p.is_file():
            path = p
            break
    if path is None:
        return {"ok": False, "error": "message not found"}
    rec = json.loads(path.read_text(encoding="utf-8"))
    if mark_read and path.parent.name == "inbox" and not rec.get("read"):
        rec["read"] = True
        rec["read_at"] = time.time()
        path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    return {"ok": True, "agent": aid, "mail": rec}


def list_sent(agent_id: str, *, limit: int = 20) -> Dict[str, Any]:
    aid = _resolve_agent(agent_id) or _safe_id(agent_id)
    d = _agent_dirs(aid)["sent"]
    rows = []
    for p in sorted(d.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": r.get("id"),
                    "to": r.get("to"),
                    "subject": r.get("subject"),
                    "status": r.get("status"),
                    "at": r.get("created_at"),
                }
            )
        except Exception:
            continue
    return {"ok": True, "agent": aid, "count": len(rows), "items": rows}


def status() -> Dict[str, Any]:
    ensure_defaults()
    with _lock:
        data = _load_accounts()
        accounts = list((data.get("accounts") or {}).values())
    active = [a for a in accounts if a.get("active") is not False]
    total_unread = sum(_count_unread(a.get("id") or "") for a in active)
    # also surface official POCKET MAIL
    smtp = {}
    try:
        from pocket.pocket_mail import status as mail_status

        smtp = mail_status()
    except Exception as e:
        smtp = {"ok": False, "error": str(e)[:80]}
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "domain": DOMAIN,
        "accounts": len(active),
        "total_unread": total_unread,
        "sample": [
            {"id": a.get("id"), "address": a.get("address"), "unread": _count_unread(a.get("id") or "")}
            for a in sorted(active, key=lambda x: str(x.get("id")))[:8]
        ],
        "pocket_mail": {
            "ok": smtp.get("ok"),
            "can_send": smtp.get("can_send"),
            "counts": smtp.get("counts"),
        },
        "api": {
            "status": "GET /v1/agent-mail",
            "accounts": "GET /v1/agent-mail/accounts",
            "create": "POST /v1/agent-mail/accounts",
            "inbox": "GET /v1/agent-mail/inbox?agent=assist",
            "send": "POST /v1/agent-mail/send",
            "read": "POST /v1/agent-mail/read",
        },
        "mcp_tools": [
            "mail_accounts",
            "mail_account_create",
            "mail_inbox",
            "mail_send",
            "mail_read",
            "mail_status",
        ],
        "doctrine": (
            "Our own agent email on agents.pocket.local — inboxes for models, "
            "Python engines, and MCP. External SMTP via POCKET MAIL when configured."
        ),
    }


def format_inbox_markdown(agent_id: str, *, limit: int = 10) -> str:
    r = inbox(agent_id, limit=limit)
    lines = [
        f"# Agent inbox · {r.get('address')}",
        f"**Unread:** {r.get('unread')} · **showing:** {r.get('count')}",
        "",
    ]
    for it in r.get("items") or []:
        flag = "●" if not it.get("read") else "○"
        lines.append(f"- {flag} **{it.get('subject')}** ← `{it.get('from')}`")
        if it.get("preview"):
            lines.append(f"  _{it['preview'][:100]}_")
    if not (r.get("items") or []):
        lines.append("_Empty inbox_")
    return "\n".join(lines)


# --- convenience for engines / tools_for_prompt ---

def tools_catalog() -> List[Dict[str, str]]:
    return [
        {"id": "mail_accounts", "desc": "List agent email accounts on agents.pocket.local"},
        {"id": "mail_account_create", "desc": "Create our own email account for an agent"},
        {"id": "mail_inbox", "desc": "Read agent inbox"},
        {"id": "mail_send", "desc": "Send agent↔agent or external mail"},
        {"id": "mail_read", "desc": "Open one message and mark read"},
        {"id": "mail_status", "desc": "Agent mail + POCKET MAIL SMTP status"},
        {"id": "web_ui_open", "desc": "Open website in host browser (Python engine)"},
        {"id": "web_ui_sense", "desc": "Sense open website UI (Fusion/OCR)"},
        {"id": "web_ui_act", "desc": "Act on website interface (click/type when armed)"},
        {"id": "web_ui_fetch", "desc": "Fetch URL text without browser tab"},
        {"id": "python_engine", "desc": "Run a named Python agent/engine on a prompt"},
    ]
