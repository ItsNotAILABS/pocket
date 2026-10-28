"""POCKET personal-AI surface on the Nebius/Nemotron lane.

The surface ported for the Nebius × NVIDIA hackathon increment: the
memory-grounded brief and the approval explainer. Both take grounded context
that already exists in POCKET — Medina Memory facts supplied by the caller
and pending agentic-approval requests from pocket.agent_approval (codes are
masked there by design) — and reason over it with the Nebius-hosted NVIDIA
Nemotron model when the lane is configured.

Boundaries, kept honest in code:
- Grounding: the model is instructed to use ONLY the facts given and to say
  what is not known. It never invents memory.
- Approvals unchanged: this module explains and summarizes; it cannot
  approve, deny, or issue anything. Every consequential action still routes
  through pocket.agent_approval's human short-code flow.
- No key, no fake answer: when the Nebius lane is not configured (or a call
  fails), the same surface returns a deterministic local brief composed from
  the identical facts, labeled engine="local-fallback". Local Auro models
  keep their existing lanes untouched; this lane is additive.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

GROUNDING_SYSTEM = (
    "You are POCKET's personal brief writer. Use ONLY the facts and pending "
    "approval requests provided. Never invent events, people, balances, or "
    "outcomes. If something is not in the provided context, say it is not in "
    "today's brief. Be concise, warm, and concrete. End with the single most "
    "useful next action for the owner."
)

EXPLAIN_SYSTEM = (
    "You explain agent approval requests to the owner in plain language. Use "
    "ONLY the request fields provided. State: who is asking, what capability "
    "they want, on which device/app and scope, what granting it would allow, "
    "and what denying it prevents. Never recommend granting anything with "
    "real-world consequence without naming the consequence. Never invent "
    "fields that were not provided."
)


def _clean_facts(facts: Optional[List[Any]]) -> List[str]:
    out: List[str] = []
    for f in facts or []:
        s = str(f or "").strip()
        if s:
            out.append(s[:500])
    return out[:50]


def _clean_pending(pending: Optional[List[Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in pending or []:
        if isinstance(r, dict):
            out.append(
                {
                    "device_id": r.get("device_id"),
                    "app_id": r.get("app_id"),
                    "scope": r.get("scope"),
                    "capability": r.get("capability"),
                    "requested_by": r.get("requested_by"),
                    "note": r.get("note"),
                    "expires_at_iso": r.get("expires_at_iso"),
                }
            )
    return out[:20]


def pending_from_state() -> List[Dict[str, Any]]:
    """Pending approval requests from the live approval store (codes masked)."""
    try:
        from pocket.agent_approval import list_pending

        res = list_pending()
        rows = res.get("requests") if isinstance(res, dict) else []
        return _clean_pending(rows if isinstance(rows, list) else [])
    except Exception:
        return []


def _local_brief(facts: List[str], pending: List[Dict[str, Any]], *, reason: str = "") -> Dict[str, Any]:
    lines: List[str] = []
    if facts:
        lines.append("From memory:")
        lines.extend(f"- {f}" for f in facts)
    else:
        lines.append("No memory facts were supplied for this brief.")
    if pending:
        lines.append("")
        lines.append(f"Waiting on your approval ({len(pending)}):")
        for r in pending:
            lines.append(
                "- {cap} on {dev} (app {app}, scope {scope})".format(
                    cap=r.get("capability") or "capability",
                    dev=r.get("device_id") or "device",
                    app=r.get("app_id") or "—",
                    scope=r.get("scope") or "—",
                )
            )
    out: Dict[str, Any] = {
        "ok": True,
        "engine": "local-fallback",
        "model": None,
        "brief": "\n".join(lines),
        "facts_used": len(facts),
        "pending_count": len(pending),
        "approval_boundary": "Explanations only — approvals still require the human short-code flow.",
    }
    if reason:
        out["fallback_reason"] = reason
    return out


def daily_brief(
    facts: Optional[List[Any]] = None,
    pending: Optional[List[Any]] = None,
    *,
    include_state_pending: bool = False,
) -> Dict[str, Any]:
    """Memory-grounded daily brief. Nebius/Nemotron when configured, else local."""
    clean_facts = _clean_facts(facts)
    clean_pending = _clean_pending(pending)
    if include_state_pending and not clean_pending:
        clean_pending = pending_from_state()

    from pocket.nebius_api import chat as nebius_chat, status as nebius_status

    if not nebius_status().get("configured"):
        return _local_brief(clean_facts, clean_pending, reason="nebius-not-configured")

    ctx: List[str] = ["FACTS FROM MEMORY:"]
    ctx.extend(f"- {f}" for f in clean_facts) if clean_facts else ctx.append("- (none supplied)")
    ctx.append("")
    ctx.append("PENDING APPROVAL REQUESTS:")
    if clean_pending:
        for r in clean_pending:
            ctx.append(
                "- capability={cap} device={dev} app={app} scope={scope} requested_by={by} note={note} expires={exp}".format(
                    cap=r.get("capability"), dev=r.get("device_id"), app=r.get("app_id"),
                    scope=r.get("scope"), by=r.get("requested_by"), note=r.get("note"),
                    exp=r.get("expires_at_iso"),
                )
            )
    else:
        ctx.append("- (none pending)")
    ctx.append("")
    ctx.append("Write today's brief from exactly this context.")

    r = nebius_chat("\n".join(ctx), system=GROUNDING_SYSTEM, max_tokens=1200, timeout=60)
    if not r.get("ok"):
        return _local_brief(clean_facts, clean_pending, reason="nebius-call-failed: " + str(r.get("error") or "unknown")[:160])
    return {
        "ok": True,
        "engine": "nebius",
        "via": r.get("via"),
        "model": r.get("model"),
        "brief": r.get("reply") or "",
        "facts_used": len(clean_facts),
        "pending_count": len(clean_pending),
        "usage": r.get("usage") or {},
        "approval_boundary": "Explanations only — approvals still require the human short-code flow.",
    }


def explain_approval(request: Dict[str, Any]) -> Dict[str, Any]:
    """Plain-language explanation of one approval request (masked fields only)."""
    clean = _clean_pending([request])
    if not clean:
        return {"ok": False, "engine": "nebius-brief", "error": "request must be a dict with approval fields"}
    r0 = clean[0]

    local_text = (
        "{by} is asking for the '{cap}' capability on {dev} (app {app}, scope {scope}). "
        "Granting it allows exactly that capability under that scope until it expires or is revoked; "
        "denying it leaves the request unexecuted. The decision is made with the short code in the "
        "approval flow — this explanation changes nothing by itself."
    ).format(
        by=r0.get("requested_by") or "An agent",
        cap=r0.get("capability") or "—",
        dev=r0.get("device_id") or "—",
        app=r0.get("app_id") or "—",
        scope=r0.get("scope") or "—",
    )

    from pocket.nebius_api import chat as nebius_chat, status as nebius_status

    if not nebius_status().get("configured"):
        return {
            "ok": True,
            "engine": "local-fallback",
            "model": None,
            "explanation": local_text,
            "request": r0,
            "fallback_reason": "nebius-not-configured",
        }
    prompt = (
        "APPROVAL REQUEST FIELDS:\n"
        f"capability={r0.get('capability')}\n"
        f"device_id={r0.get('device_id')}\n"
        f"app_id={r0.get('app_id')}\n"
        f"scope={r0.get('scope')}\n"
        f"requested_by={r0.get('requested_by')}\n"
        f"note={r0.get('note')}\n"
        f"expires_at={r0.get('expires_at_iso')}\n\n"
        "Explain this request to the owner."
    )
    r = nebius_chat(prompt, system=EXPLAIN_SYSTEM, max_tokens=700, timeout=60)
    if not r.get("ok"):
        return {
            "ok": True,
            "engine": "local-fallback",
            "model": None,
            "explanation": local_text,
            "request": r0,
            "fallback_reason": "nebius-call-failed: " + str(r.get("error") or "unknown")[:160],
        }
    return {
        "ok": True,
        "engine": "nebius",
        "via": r.get("via"),
        "model": r.get("model"),
        "explanation": r.get("reply") or "",
        "request": r0,
        "usage": r.get("usage") or {},
    }
