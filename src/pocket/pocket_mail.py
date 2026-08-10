"""POCKET MAIL — official self-hosted mailing system for the POCKET app.

Product name: POCKET MAIL
Protocol: POCKET-MAIL/1.0

Capabilities:
  · Official templates (welcome, invite, recall, keep-status, system)
  · Outbox queue with receipts under ~/.pocket/mail/
  · SMTP send when configured (POCKET_SMTP_*)
  · Local file + optional Outlook draft (never silent send without intent)
  · Status / dry-run for operator proof

Doctrine:
  · Explicit send only — draft is default
  · No third-party “magic” without SMTP config on your host
  · Messages are first-class product artifacts
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import time
import uuid
from email.message import EmailMessage
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "mail"
OUTBOX = ROOT / "outbox"
SENT = ROOT / "sent"
DRAFTS = ROOT / "drafts"
for _d in (ROOT, OUTBOX, SENT, DRAFTS):
    _d.mkdir(parents=True, exist_ok=True)

_lock = Lock()
PRODUCT = "POCKET MAIL"
PROTOCOL = "POCKET-MAIL/1.0"
SCHEMA = "pocket.mail.v1"

TEMPLATES: Dict[str, Dict[str, str]] = {
    "welcome": {
        "subject": "Welcome to POCKET",
        "body": (
            "Welcome to POCKET — your host co-pilot.\n\n"
            "Open the desk: {desk_url}\n"
            "LOOMGRAPH (default harness): {loomgraph_url}\n"
            "Creative Studio: {creative_url}\n\n"
            "— ItsNotAI Labs / POCKET MAIL\n"
        ),
    },
    "invite": {
        "subject": "You're invited to POCKET",
        "body": (
            "You've been invited to a POCKET workspace.\n\n"
            "Invite / seat note: {note}\n"
            "Open: {desk_url}\n\n"
            "Use the invite flow your admin shared — not the founder password.\n\n"
            "— POCKET MAIL\n"
        ),
    },
    "recall": {
        "subject": "Your POCKET RECALL code",
        "body": (
            "A recall code was minted for your POCKET work.\n\n"
            "Code: {code}\n"
            "Label: {label}\n"
            "Expires (unix): {expires_at}\n\n"
            "Redeem: POST /v1/recall/redeem with this code, or paste in Desk → RECALL.\n"
            "This reattaches KEEP agents and session context.\n\n"
            "— POCKET RECALL · POCKET MAIL\n"
        ),
    },
    "keep_status": {
        "subject": "POCKET KEEP agent update",
        "body": (
            "KEEP agent status for chat session {session_id}:\n\n"
            "Agent: {keep_id}\n"
            "Status: {status}\n"
            "Pulses: {pulses}\n"
            "Goal: {goal}\n\n"
            "— POCKET KEEP · POCKET MAIL\n"
        ),
    },
    "system": {
        "subject": "POCKET system notice",
        "body": "{body}\n\n— POCKET MAIL (official)\n",
    },
    "custom": {
        "subject": "{subject}",
        "body": "{body}\n\n— POCKET MAIL\n",
    },
}


def _urls() -> Dict[str, str]:
    base = os.environ.get("POCKET_PUBLIC_URL") or "http://127.0.0.1:8787"
    base = base.rstrip("/")
    return {
        "desk_url": f"{base}/desk",
        "loomgraph_url": f"{base}/loomgraph",
        "creative_url": f"{base}/studio/create",
        "mail_url": f"{base}/mail",
        "base_url": base,
    }


def _smtp_config() -> Dict[str, Any]:
    host = os.environ.get("POCKET_SMTP_HOST") or os.environ.get("SMTP_HOST") or ""
    port = int(os.environ.get("POCKET_SMTP_PORT") or os.environ.get("SMTP_PORT") or "587")
    user = os.environ.get("POCKET_SMTP_USER") or os.environ.get("SMTP_USER") or ""
    password = os.environ.get("POCKET_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or ""
    from_addr = (
        os.environ.get("POCKET_SMTP_FROM")
        or os.environ.get("SMTP_FROM")
        or user
        or "pocket@localhost"
    )
    use_tls = (os.environ.get("POCKET_SMTP_TLS") or "1").strip() not in ("0", "false", "no")
    use_ssl = (os.environ.get("POCKET_SMTP_SSL") or "0").strip() in ("1", "true", "yes")
    return {
        "configured": bool(host and from_addr),
        "host": host,
        "port": port,
        "user": user,
        "password_set": bool(password),
        "from_addr": from_addr,
        "tls": use_tls,
        "ssl": use_ssl,
    }


def status() -> Dict[str, Any]:
    smtp = _smtp_config()
    outbox_n = len(list(OUTBOX.glob("*.json")))
    sent_n = len(list(SENT.glob("*.json")))
    draft_n = len(list(DRAFTS.glob("*.json")))
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "official": True,
        "smtp": {k: v for k, v in smtp.items() if k != "password"},
        "can_send": bool(smtp.get("configured") and smtp.get("password_set")),
        "counts": {"outbox": outbox_n, "sent": sent_n, "drafts": draft_n},
        "templates": list(TEMPLATES.keys()),
        "paths": {"root": str(ROOT), "outbox": str(OUTBOX), "sent": str(SENT)},
        "urls": _urls(),
        "api": {
            "status": "GET /v1/mail",
            "draft": "POST /v1/mail/draft",
            "send": "POST /v1/mail/send",
            "templates": "GET /v1/mail/templates",
            "outbox": "GET /v1/mail/outbox",
        },
        "env": [
            "POCKET_SMTP_HOST",
            "POCKET_SMTP_PORT",
            "POCKET_SMTP_USER",
            "POCKET_SMTP_PASSWORD",
            "POCKET_SMTP_FROM",
            "POCKET_SMTP_TLS",
        ],
        "doctrine": "Official POCKET MAIL — draft by default; SMTP send only when configured + explicit.",
        "agent_mail": {
            "hint": "Per-agent inboxes on agents.pocket.local — GET /v1/agent-mail",
            "domain": "agents.pocket.local",
            "api": "GET /v1/agent-mail · POST /v1/agent-mail/send · GET /v1/agent-mail/inbox?agent=assist",
        },
    }


def templates() -> Dict[str, Any]:
    return {
        "ok": True,
        "templates": [
            {"id": k, "subject": v["subject"], "body_preview": v["body"][:120]}
            for k, v in TEMPLATES.items()
        ],
    }


def _render(template_id: str, fields: Dict[str, Any]) -> Dict[str, str]:
    tid = (template_id or "custom").lower()
    tpl = TEMPLATES.get(tid) or TEMPLATES["custom"]
    ctx = {**_urls(), **{k: str(v) if v is not None else "" for k, v in (fields or {}).items()}}
    # defaults
    ctx.setdefault("subject", fields.get("subject") or "POCKET message")
    ctx.setdefault("body", fields.get("body") or fields.get("text") or "")
    ctx.setdefault("note", fields.get("note") or "")
    try:
        subject = tpl["subject"].format(**ctx)
        body = tpl["body"].format(**ctx)
    except Exception:
        subject = str(fields.get("subject") or tpl["subject"])
        body = str(fields.get("body") or fields.get("text") or tpl["body"])
    return {"subject": subject[:200], "body": body[:50000]}


def draft(
    *,
    to: str = "",
    subject: str = "",
    body: str = "",
    template: str = "custom",
    fields: Optional[Dict[str, Any]] = None,
    from_addr: str = "",
    cc: str = "",
    owner: str = "",
) -> Dict[str, Any]:
    """Create an official mail draft (never sends)."""
    f = dict(fields or {})
    if subject:
        f["subject"] = subject
    if body:
        f["body"] = body
    rendered = _render(template, f)
    mid = "mail-" + uuid.uuid4().hex[:12]
    rec = {
        "id": mid,
        "schema": SCHEMA,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "status": "draft",
        "to": (to or "").strip(),
        "cc": (cc or "").strip(),
        "from": from_addr or _smtp_config().get("from_addr"),
        "subject": rendered["subject"],
        "body": rendered["body"],
        "template": template,
        "owner": (owner or "pocket").strip().lower(),
        "created_at": time.time(),
        "sent": False,
    }
    path = DRAFTS / f"{mid}.json"
    path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    # also HTML preview for desk
    html_path = DRAFTS / f"{mid}.html"
    html_path.write_text(
        f"<!DOCTYPE html><html><body style='font-family:system-ui;padding:24px'>"
        f"<p><b>To:</b> {_esc(rec['to'])}<br/><b>Subject:</b> {_esc(rec['subject'])}</p>"
        f"<pre style='white-space:pre-wrap'>{_esc(rec['body'])}</pre>"
        f"<p style='color:#71717a;font-size:12px'>{PRODUCT} draft — not sent</p>"
        f"</body></html>",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "mail": rec,
        "path": str(path),
        "html": str(html_path),
        "message": "POCKET MAIL draft created (not sent)",
    }


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _smtp_send(rec: Dict[str, Any]) -> Dict[str, Any]:
    cfg = _smtp_config()
    if not cfg.get("configured"):
        return {"ok": False, "error": "SMTP not configured — set POCKET_SMTP_HOST and POCKET_SMTP_FROM"}
    if not cfg.get("password_set") and cfg.get("user"):
        return {"ok": False, "error": "POCKET_SMTP_PASSWORD not set"}
    to = rec.get("to") or ""
    if not to or "@" not in to:
        return {"ok": False, "error": "valid to address required"}
    msg = EmailMessage()
    msg["Subject"] = rec.get("subject") or "POCKET"
    msg["From"] = rec.get("from") or cfg["from_addr"]
    msg["To"] = to
    if rec.get("cc"):
        msg["Cc"] = rec["cc"]
    msg.set_content(rec.get("body") or "")
    try:
        if cfg.get("ssl"):
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg["host"], int(cfg["port"]), context=context, timeout=30) as s:
                if cfg.get("user"):
                    s.login(cfg["user"], os.environ.get("POCKET_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or "")
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], int(cfg["port"]), timeout=30) as s:
                s.ehlo()
                if cfg.get("tls"):
                    s.starttls(context=ssl.create_default_context())
                    s.ehlo()
                if cfg.get("user"):
                    s.login(
                        cfg["user"],
                        os.environ.get("POCKET_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or "",
                    )
                s.send_message(msg)
        return {"ok": True, "method": "smtp", "host": cfg["host"]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:240], "method": "smtp"}


def send(
    *,
    to: str = "",
    subject: str = "",
    body: str = "",
    template: str = "custom",
    fields: Optional[Dict[str, Any]] = None,
    draft_id: str = "",
    dry_run: bool = False,
    also_outlook_draft: bool = False,
    owner: str = "",
) -> Dict[str, Any]:
    """Send via SMTP (or dry-run / queue). Explicit only."""
    rec: Dict[str, Any]
    if draft_id:
        p = DRAFTS / f"{draft_id}.json"
        if not p.is_file():
            return {"ok": False, "error": "draft not found"}
        rec = json.loads(p.read_text(encoding="utf-8"))
        if to:
            rec["to"] = to
    else:
        d = draft(
            to=to,
            subject=subject,
            body=body,
            template=template,
            fields=fields,
            owner=owner,
        )
        rec = d["mail"]

    mid = rec.get("id") or ("mail-" + uuid.uuid4().hex[:12])
    rec["id"] = mid
    out_path = OUTBOX / f"{mid}.json"

    if dry_run:
        rec["status"] = "dry_run"
        out_path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
        return {
            "ok": True,
            "dry_run": True,
            "mail": rec,
            "message": "Dry-run — not sent. Set SMTP and call send without dry_run.",
        }

    smtp_res = _smtp_send(rec)
    rec["smtp"] = smtp_res
    if smtp_res.get("ok"):
        rec["status"] = "sent"
        rec["sent"] = True
        rec["sent_at"] = time.time()
        (SENT / f"{mid}.json").write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
        # remove from drafts if present
        try:
            (DRAFTS / f"{mid}.json").unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass
        msg = "POCKET MAIL sent via SMTP"
    else:
        rec["status"] = "queued_failed_smtp"
        rec["sent"] = False
        out_path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
        msg = f"SMTP failed — queued in outbox: {smtp_res.get('error')}"

    if also_outlook_draft:
        try:
            from pocket.outlook_agent import create_draft

            od = create_draft(subject=rec.get("subject") or "", body=rec.get("body") or "", to=rec.get("to") or "")
            rec["outlook"] = od
        except Exception as e:
            rec["outlook"] = {"ok": False, "error": str(e)[:120]}

    return {
        "ok": bool(smtp_res.get("ok")),
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "mail": rec,
        "smtp": smtp_res,
        "message": msg,
        "official": True,
    }


def list_outbox(*, limit: int = 30) -> Dict[str, Any]:
    rows = []
    for folder, status in ((OUTBOX, "outbox"), (SENT, "sent"), (DRAFTS, "draft")):
        for p in sorted(folder.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            try:
                r = json.loads(p.read_text(encoding="utf-8"))
                rows.append(
                    {
                        "id": r.get("id"),
                        "to": r.get("to"),
                        "subject": r.get("subject"),
                        "status": r.get("status") or status,
                        "sent": r.get("sent"),
                        "at": r.get("sent_at") or r.get("created_at"),
                        "folder": status,
                    }
                )
            except Exception:
                continue
    rows.sort(key=lambda x: float(x.get("at") or 0), reverse=True)
    return {"ok": True, "items": rows[:limit], "count": len(rows[:limit])}
