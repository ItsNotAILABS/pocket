"""Agent virtual numbers + phone calls (sovereign softphone).

Every agent can own a virtual number on the POCKET dial plan:

  +p-XXX-XXXX   (sovereign, always works on-host)
  e.g. assist → +p-201-0001

Calls are first-class sessions under ~/.pocket/agent_calls/:
  · agent ↔ agent soft calls
  · agent → user (rings phone-agent app)
  · optional real PSTN via Twilio when POCKET_TWILIO_* is set

Doctrine:
  · Virtual numbers are free, local, sovereign
  · Real PSTN is opt-in and never silent (explicit dial only)
  · Agents reason then dial through skills / phone SDK
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "agent_calls"
NUMBERS = ROOT / "numbers.json"
CALLS = ROOT / "calls"
ROOT.mkdir(parents=True, exist_ok=True)
CALLS.mkdir(parents=True, exist_ok=True)

_lock = Lock()

PRODUCT = "POCKET Agent Calls"
PROTOCOL = "POCKET-AGENT-CALLS/1.0"
SCHEMA = "pocket.agent_calls.v1"
DIAL_PREFIX = "+p"  # sovereign virtual

# Default agent → virtual line mapping (area 201 = agents)
DEFAULT_LINES = [
    ("assist", "201", "0001", "Assistant"),
    ("aria", "201", "0002", "Aria Voice"),
    ("scribe", "201", "0003", "Scribe Mail"),
    ("codex", "201", "0010", "Codex"),
    ("claude", "201", "0011", "Claude"),
    ("grok", "201", "0012", "Grok"),
    ("navigator", "201", "0020", "Navigator"),
    ("archon", "201", "0100", "ARCHON"),
    ("system", "201", "9999", "POCKET System"),
    ("phone_agent", "201", "1000", "Phone Agent App"),
]


def _safe_agent(a: str) -> str:
    s = re.sub(r"[^a-z0-9._\-]+", "-", (a or "").strip().lower())
    return (s.strip("-._") or f"agent-{uuid.uuid4().hex[:6]}")[:40]


def format_number(area: str, line: str) -> str:
    return f"{DIAL_PREFIX}-{area}-{line}"


def _load_numbers() -> Dict[str, Any]:
    if NUMBERS.is_file():
        try:
            return json.loads(NUMBERS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "numbers": {}, "by_agent": {}}


def _save_numbers(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = NUMBERS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.replace(NUMBERS)


def ensure_defaults() -> None:
    with _lock:
        data = _load_numbers()
        nums = data.setdefault("numbers", {})
        by_a = data.setdefault("by_agent", {})
        changed = False
        for agent, area, line, name in DEFAULT_LINES:
            if agent in by_a:
                continue
            num = format_number(area, line)
            if num in nums:
                # collision — skip
                continue
            rec = {
                "number": num,
                "agent": agent,
                "name": name,
                "kind": "virtual",
                "created_at": time.time(),
                "active": True,
            }
            nums[num] = rec
            by_a[agent] = num
            changed = True
        if changed:
            data["updated_at"] = time.time()
            _save_numbers(data)


def assign_number(
    agent: str,
    *,
    name: str = "",
    area: str = "201",
    line: str = "",
) -> Dict[str, Any]:
    """Give an agent its own virtual number (or return existing)."""
    ensure_defaults()
    aid = _safe_agent(agent)
    with _lock:
        data = _load_numbers()
        by_a = data.setdefault("by_agent", {})
        nums = data.setdefault("numbers", {})
        if aid in by_a and by_a[aid] in nums:
            return {"ok": True, "created": False, "number": nums[by_a[aid]]}
        # allocate line
        if not line:
            used = {r.get("number", "").split("-")[-1] for r in nums.values()}
            for n in range(1000, 9999):
                cand = f"{n:04d}"
                if cand not in used:
                    line = cand
                    break
            if not line:
                line = uuid.uuid4().hex[:4]
        area = re.sub(r"\D", "", area or "201")[:3] or "201"
        line = re.sub(r"\D", "", line)[:4].zfill(4)
        num = format_number(area, line)
        # ensure unique
        while num in nums:
            line = f"{(int(line) + 1) % 10000:04d}"
            num = format_number(area, line)
        rec = {
            "number": num,
            "agent": aid,
            "name": (name or aid).strip()[:80],
            "kind": "virtual",
            "created_at": time.time(),
            "active": True,
        }
        nums[num] = rec
        by_a[aid] = num
        data["updated_at"] = time.time()
        _save_numbers(data)
    return {"ok": True, "created": True, "number": rec, "message": f"Assigned {num} → {aid}"}


def list_numbers(*, limit: int = 100) -> Dict[str, Any]:
    ensure_defaults()
    with _lock:
        data = _load_numbers()
        rows = list((data.get("numbers") or {}).values())
    rows = [r for r in rows if r.get("active") is not False]
    rows.sort(key=lambda r: str(r.get("number") or ""))
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "dial_plan": f"{DIAL_PREFIX}-XXX-XXXX",
        "count": len(rows),
        "numbers": rows[:limit],
        "doctrine": "Sovereign virtual numbers for agents — free on-host softphone.",
    }


def get_number(agent_or_number: str) -> Dict[str, Any]:
    ensure_defaults()
    s = (agent_or_number or "").strip()
    with _lock:
        data = _load_numbers()
        if s in (data.get("numbers") or {}):
            return {"ok": True, "number": data["numbers"][s]}
        aid = _safe_agent(s)
        num = (data.get("by_agent") or {}).get(aid)
        if num and num in (data.get("numbers") or {}):
            return {"ok": True, "number": data["numbers"][num]}
    # auto-assign on first lookup by agent id
    if s and not s.startswith("+") and "@" not in s:
        return assign_number(s)
    return {"ok": False, "error": f"no number for {s}"}


def _resolve_endpoint(who: str) -> Dict[str, Any]:
    """Resolve agent id or virtual number to call endpoint."""
    s = (who or "").strip()
    if not s:
        return {"ok": False, "error": "empty endpoint"}
    # external E.164-ish
    if re.match(r"^\+?[1-9]\d{6,14}$", s.replace("-", "").replace(" ", "")) and not s.startswith("+p"):
        digits = re.sub(r"\D", "", s)
        if not digits.startswith("+"):
            e164 = "+" + digits
        else:
            e164 = s
        return {
            "ok": True,
            "kind": "pstn",
            "number": e164 if e164.startswith("+") else "+" + digits,
            "agent": "",
            "label": e164,
        }
    # virtual or agent
    g = get_number(s)
    if g.get("ok"):
        n = g["number"]
        return {
            "ok": True,
            "kind": "virtual",
            "number": n.get("number"),
            "agent": n.get("agent"),
            "label": n.get("name") or n.get("agent"),
        }
    # mint for bare agent name
    a = assign_number(s)
    n = a.get("number") or {}
    return {
        "ok": True,
        "kind": "virtual",
        "number": n.get("number"),
        "agent": n.get("agent"),
        "label": n.get("name") or n.get("agent"),
    }


def twilio_configured() -> bool:
    return bool(
        os.environ.get("POCKET_TWILIO_ACCOUNT_SID")
        and os.environ.get("POCKET_TWILIO_AUTH_TOKEN")
        and os.environ.get("POCKET_TWILIO_FROM")
    )


def _save_call(rec: Dict[str, Any]) -> Path:
    cid = rec.get("id") or ("call-" + uuid.uuid4().hex[:12])
    rec["id"] = cid
    path = CALLS / f"{cid}.json"
    path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    return path


def _load_call(call_id: str) -> Optional[Dict[str, Any]]:
    p = CALLS / f"{call_id}.json"
    if not p.is_file():
        # try prefix
        for f in CALLS.glob("*.json"):
            if call_id in f.stem:
                p = f
                break
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def dial(
    *,
    from_agent: str = "phone_agent",
    to: str = "",
    purpose: str = "",
    text: str = "",
    mode: str = "soft",  # soft | pstn
    session_id: str = "",
) -> Dict[str, Any]:
    """Place a call from an agent's virtual number.

    soft  — sovereign on-host call session (agent↔agent or ring phone app)
    pstn  — real telephony if Twilio configured; else falls back to soft with note
    """
    ensure_defaults()
    if not to:
        return {"ok": False, "error": "to required (agent id, +p-XXX-XXXX, or E.164)"}

    fr = _resolve_endpoint(from_agent)
    if not fr.get("ok"):
        return fr
    # ensure from is virtual agent line
    if fr.get("kind") != "virtual":
        fr = _resolve_endpoint(assign_number(from_agent)["number"]["agent"])

    to_ep = _resolve_endpoint(to)
    if not to_ep.get("ok"):
        return to_ep

    cid = "call-" + uuid.uuid4().hex[:12]
    now = time.time()
    rec: Dict[str, Any] = {
        "id": cid,
        "schema": SCHEMA,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "status": "ringing",
        "mode": "soft",
        "from": {
            "agent": fr.get("agent") or from_agent,
            "number": fr.get("number"),
            "label": fr.get("label"),
        },
        "to": {
            "agent": to_ep.get("agent") or "",
            "number": to_ep.get("number"),
            "label": to_ep.get("label"),
            "kind": to_ep.get("kind"),
        },
        "purpose": (purpose or text or "agent call")[:300],
        "transcript": [],
        "events": [],
        "created_at": now,
        "answered_at": None,
        "ended_at": None,
        "session_id": session_id or "",
        "pstn": None,
    }

    def evt(kind: str, msg: str) -> None:
        rec["events"].append({"t": time.strftime("%H:%M:%S"), "kind": kind, "msg": msg[:200]})
        rec["events"] = rec["events"][-40:]

    evt("dial", f"{rec['from']['number']} → {rec['to']['number']}")

    # PSTN path
    want_pstn = (mode or "soft").lower() == "pstn" or to_ep.get("kind") == "pstn"
    if want_pstn and to_ep.get("kind") == "pstn":
        if twilio_configured():
            pstn = _twilio_dial(rec["from"]["number"], rec["to"]["number"], rec["purpose"])
            rec["pstn"] = pstn
            if pstn.get("ok"):
                rec["mode"] = "pstn"
                rec["status"] = "ringing"
                evt("pstn", f"Twilio sid={pstn.get('sid')}")
            else:
                rec["status"] = "soft_fallback"
                rec["mode"] = "soft"
                evt("pstn_fail", str(pstn.get("error") or "twilio failed")[:120])
        else:
            rec["mode"] = "soft"
            rec["status"] = "soft_fallback"
            evt(
                "pstn_skip",
                "Twilio not configured — soft call only (set POCKET_TWILIO_*)",
            )

    # Soft answer immediately for virtual endpoints (agent-to-agent)
    if rec["mode"] == "soft" or rec["status"] == "soft_fallback":
        if to_ep.get("kind") == "virtual":
            rec["status"] = "active"
            rec["answered_at"] = time.time()
            evt("answer", f"soft answer · {to_ep.get('label')}")
            # seed transcript with purpose
            if purpose or text:
                rec["transcript"].append(
                    {
                        "role": "system",
                        "text": f"Call purpose: {purpose or text}",
                        "at": time.time(),
                    }
                )
        else:
            # external without twilio — stay ringing in soft ring queue for phone app
            rec["status"] = "ringing"
            evt("ring", "ringing user phone-agent app")

    # live event
    try:
        from pocket.live_events import emit

        emit(
            "agent_call",
            f"dial {rec['from']['number']} → {rec['to']['number']} ({rec['status']})",
            agent=rec["from"]["agent"],
            role="phone",
            session_id=session_id,
            meta={"call_id": cid, "status": rec["status"]},
        )
    except Exception:
        pass

    # optional agent mail receipt
    try:
        from pocket.agent_mail import send as mail_send

        mail_send(
            from_agent=rec["from"]["agent"] or "system",
            to=to_ep.get("agent") or "assist",
            subject=f"Call {rec['status']}: {rec['from']['number']} → {rec['to']['number']}",
            body=f"Purpose: {rec['purpose']}\nCall id: {cid}\nMode: {rec['mode']}",
        )
    except Exception:
        pass

    path = _save_call(rec)
    return {
        "ok": True,
        "call": rec,
        "path": str(path),
        "message": (
            f"Calling {rec['to']['number']} from {rec['from']['number']} "
            f"({rec['status']}, mode={rec['mode']})"
        ),
        "ui_hint": "Phone Agent app shows live call under /v1/calls",
    }


def _twilio_dial(from_virtual: str, to_e164: str, purpose: str) -> Dict[str, Any]:
    """Optional real PSTN via Twilio REST (no SDK required)."""
    import base64
    import urllib.error
    import urllib.parse
    import urllib.request

    sid = os.environ.get("POCKET_TWILIO_ACCOUNT_SID") or ""
    token = os.environ.get("POCKET_TWILIO_AUTH_TOKEN") or ""
    from_num = os.environ.get("POCKET_TWILIO_FROM") or ""
    # TwiML: say purpose then hang up (or use URL if set)
    twiml_url = os.environ.get("POCKET_TWILIO_TWIML_URL") or ""
    if not (sid and token and from_num):
        return {"ok": False, "error": "Twilio env incomplete"}
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
        data = {
            "To": to_e164,
            "From": from_num,
        }
        if twiml_url:
            data["Url"] = twiml_url
        else:
            # inline twiml via Twiml param not always supported — use say via bin
            say = urllib.parse.quote(
                f"<Response><Say>POCKET agent call. {purpose[:120]}</Say></Response>"
            )
            data["Twiml"] = f"<Response><Say>POCKET agent call. {purpose[:120]}</Say></Response>"
        body = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        auth = base64.b64encode(f"{sid}:{token}".encode()).decode()
        req.add_header("Authorization", f"Basic {auth}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            j = json.loads(raw) if raw else {}
            return {
                "ok": True,
                "sid": j.get("sid"),
                "status": j.get("status"),
                "to": to_e164,
                "from": from_num,
                "note": f"virtual caller id {from_virtual} mapped via Twilio From {from_num}",
            }
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "error": err or str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def answer(call_id: str, *, by: str = "user") -> Dict[str, Any]:
    rec = _load_call(call_id)
    if not rec:
        return {"ok": False, "error": "call not found"}
    if rec.get("status") in ("ended", "failed"):
        return {"ok": False, "error": f"call already {rec.get('status')}", "call": rec}
    rec["status"] = "active"
    rec["answered_at"] = time.time()
    rec["answered_by"] = by
    rec.setdefault("events", []).append(
        {"t": time.strftime("%H:%M:%S"), "kind": "answer", "msg": f"answered by {by}"}
    )
    _save_call(rec)
    return {"ok": True, "call": rec, "message": "Call active"}


def hangup(call_id: str, *, reason: str = "hangup") -> Dict[str, Any]:
    rec = _load_call(call_id)
    if not rec:
        return {"ok": False, "error": "call not found"}
    rec["status"] = "ended"
    rec["ended_at"] = time.time()
    rec["end_reason"] = reason
    if rec.get("answered_at"):
        rec["duration_sec"] = round(rec["ended_at"] - float(rec["answered_at"]), 1)
    rec.setdefault("events", []).append(
        {"t": time.strftime("%H:%M:%S"), "kind": "hangup", "msg": reason[:80]}
    )
    _save_call(rec)
    return {"ok": True, "call": rec, "message": "Call ended"}


def speak(call_id: str, text: str, *, role: str = "agent") -> Dict[str, Any]:
    """Add spoken/text turn to active call transcript (softphone)."""
    rec = _load_call(call_id)
    if not rec:
        return {"ok": False, "error": "call not found"}
    if rec.get("status") not in ("active", "ringing", "soft_fallback"):
        return {"ok": False, "error": f"call not active ({rec.get('status')})"}
    if rec.get("status") == "ringing":
        rec["status"] = "active"
        rec["answered_at"] = rec.get("answered_at") or time.time()
    rec.setdefault("transcript", []).append(
        {"role": role, "text": (text or "")[:4000], "at": time.time()}
    )
    rec["transcript"] = rec["transcript"][-100:]
    rec.setdefault("events", []).append(
        {"t": time.strftime("%H:%M:%S"), "kind": "speak", "msg": f"{role}: {(text or '')[:80]}"}
    )
    _save_call(rec)
    return {"ok": True, "call": rec}


def list_calls(*, limit: int = 30, status: str = "") -> Dict[str, Any]:
    rows = []
    for p in sorted(CALLS.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[: max(limit * 2, 40)]:
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            if status and r.get("status") != status:
                continue
            rows.append(
                {
                    "id": r.get("id"),
                    "status": r.get("status"),
                    "mode": r.get("mode"),
                    "from": (r.get("from") or {}).get("number"),
                    "from_agent": (r.get("from") or {}).get("agent"),
                    "to": (r.get("to") or {}).get("number"),
                    "to_agent": (r.get("to") or {}).get("agent"),
                    "purpose": r.get("purpose"),
                    "created_at": r.get("created_at"),
                    "duration_sec": r.get("duration_sec"),
                }
            )
        except Exception:
            continue
        if len(rows) >= limit:
            break
    return {"ok": True, "count": len(rows), "calls": rows}


def get_call(call_id: str) -> Dict[str, Any]:
    rec = _load_call(call_id)
    if not rec:
        return {"ok": False, "error": "not found"}
    return {"ok": True, "call": rec}


def status() -> Dict[str, Any]:
    ensure_defaults()
    nums = list_numbers()
    active = list_calls(limit=20, status="active")
    ringing = list_calls(limit=20, status="ringing")
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "dial_plan": f"{DIAL_PREFIX}-XXX-XXXX",
        "numbers": nums.get("count"),
        "active_calls": active.get("count"),
        "ringing": ringing.get("count"),
        "twilio": twilio_configured(),
        "api": {
            "numbers": "GET /v1/calls/numbers",
            "assign": "POST /v1/calls/numbers",
            "dial": "POST /v1/calls/dial",
            "answer": "POST /v1/calls/answer",
            "hangup": "POST /v1/calls/hangup",
            "speak": "POST /v1/calls/speak",
            "list": "GET /v1/calls",
        },
        "env_pstn": [
            "POCKET_TWILIO_ACCOUNT_SID",
            "POCKET_TWILIO_AUTH_TOKEN",
            "POCKET_TWILIO_FROM",
            "POCKET_TWILIO_TWIML_URL",
        ],
        "doctrine": (
            "Agents own virtual +p numbers. Soft calls always work on-host. "
            "Real PSTN only with Twilio env + explicit mode=pstn."
        ),
    }
