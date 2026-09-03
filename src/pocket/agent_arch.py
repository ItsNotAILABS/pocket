"""Agent architecture plane — one spine for Pocket, PhoneAI, RAH, invoke.

Layers (not extra products):

  identity → seat → route → authority → execute → receipt

Existing modules stay the execute leaves. This module does not invent
agents; it resolves them and runs one turn through the same contract.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.agent.arch.v1"
TURN = "pocket.agent.turn.v1"
RECEIPT = "pocket.action_receipt.v1"

LAYERS = ("identity", "seat", "route", "authority", "execute", "receipt")
SEATS = ("pocket", "phoneai", "node", "screen")

# Tools that may not run from wording alone.
CONSEQUENCE = frozenset({"rah_run", "studio_ship", "twin_mint", "shell"})

EXECUTE = ("harness", "rah", "invoke", "talk", "session", "plan", "screen")


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "-").replace("_", "-").lstrip("@")


def snapshot() -> Dict[str, Any]:
    personas: List[Dict[str, Any]] = []
    roster_n = 0
    first_n = 0
    try:
        from pocket.agent_runtime import personas as list_personas

        personas = list_personas()
    except Exception:
        personas = []
    try:
        from pocket.agent_invoke import roster

        roster_n = int(roster().get("count") or 0)
    except Exception:
        pass
    try:
        from pocket.first_class_agents import build_registry

        first_n = len(build_registry(live=False).get("agents") or [])
    except Exception:
        pass
    return {
        "ok": True,
        "schema": SCHEMA,
        "layers": list(LAYERS),
        "seats": list(SEATS),
        "execute": list(EXECUTE),
        "route": "pocket.agent_runtime.route_think — one engine, at most one tool",
        "authority": "pocket.work_grant.v1 before consequence tools",
        "receipt": RECEIPT,
        "counts": {"personas": len(personas), "first_class": first_n, "roster": roster_n},
        "http": ["GET /v1/agents/arch", "POST /v1/agents/turn", "POST /v1/phoneai/harness", "POST /v1/agents/invoke"],
        "mcp": ["agent_arch", "agent_turn"],
        "note": "Desk, PhoneAI, RAH, and invoke share this plane. Do not add a parallel agent OS.",
    }


def resolve(name: str = "") -> Dict[str, Any]:
    """Unify PhoneAI personas + first-class roster into one identity record."""
    n = _norm(name)
    rec: Dict[str, Any] = {
        "id": n or "coder",
        "name": n or "coder",
        "kind": "persona",
        "engine": "grok",
        "seat": "phoneai" if not n or n in ("coder", "phoneai") else "pocket",
        "first_class": False,
        "persona": False,
        "invoke": "",
        "blurb": "",
        "surfaces": ["desk", "phone"],
    }
    if n:
        try:
            from pocket.agent_runtime import persona

            p = persona(n)
            if p and (p.get("id") == n or n in {str(p.get("id") or "").lower()}):
                rec.update(
                    {
                        "id": p.get("id") or n,
                        "name": p.get("id") or n,
                        "kind": "persona",
                        "engine": p.get("engine") or p.get("mode") or "grok",
                        "seat": p.get("seat") or rec["seat"],
                        "persona": True,
                        "keep": bool(p.get("keep") or p.get("long_term")),
                        "blurb": p.get("blurb") or "",
                        "mode": p.get("mode") or "",
                    }
                )
        except Exception:
            pass
        try:
            from pocket.agent_invoke import _resolve as inv_resolve

            inv = inv_resolve(n)
            if inv:
                rec.update(
                    {
                        "id": inv.get("id") or rec["id"],
                        "name": inv.get("name") or rec["name"],
                        "kind": inv.get("kind") or rec["kind"],
                        "engine": inv.get("engine") or rec["engine"],
                        "first_class": True,
                        "invoke": inv.get("invoke") or "dispatch",
                        "blurb": inv.get("blurb") or rec.get("blurb") or "",
                        "mention": inv.get("mention") or "",
                    }
                )
        except Exception:
            pass
    rec["resolved"] = rec["id"]
    rec["schema"] = "pocket.agent.identity.v1"
    return rec


def _receipt(*, turn_id: str, identity: Dict[str, Any], thought: Dict[str, Any], execute: str, ok: bool) -> Dict[str, Any]:
    return {
        "schema": RECEIPT,
        "id": "rc-" + turn_id,
        "turn_id": turn_id,
        "agent": identity.get("id"),
        "engine": thought.get("engine"),
        "tool": thought.get("tool"),
        "execute": execute,
        "ok": bool(ok),
        "at": time.time(),
    }


def turn(
    text: str,
    *,
    agent: str = "",
    seat: str = "pocket",
    engine: str = "auto",
    grant_id: str = "",
    shell: str = "",
    cwd: str = "",
    use: str = "auto",
    timeout: float = 25,
    dry: bool = False,
) -> Dict[str, Any]:
    """One agent turn through the architecture plane."""
    t0 = time.time()
    turn_id = uuid.uuid4().hex[:12]
    goal = (text or "").strip()
    who = resolve(agent)
    seat_n = (seat or who.get("seat") or "pocket").lower()
    if seat_n not in SEATS:
        seat_n = "pocket"
    from pocket.agent_runtime import route_think

    thought = route_think(goal or shell, engine)
    if (engine in ("", "auto")) and who.get("engine") and thought.get("why") == "think then grok — no extra tools":
        thought = {**thought, "engine": who["engine"], "why": "identity engine"}
    tool = thought.get("tool")
    lane = (use or "auto").lower()
    if lane == "auto":
        if tool == "rah_run":
            lane = "rah"
        elif tool == "session_new":
            lane = "session"
        elif tool == "agent_talk":
            lane = "talk"
        elif tool == "screen_embody" or thought.get("engine") == "screen":
            lane = "screen"
        elif who.get("first_class") and who.get("invoke") and agent and not who.get("persona"):
            lane = "invoke"
        else:
            lane = "harness"

    authority: Dict[str, Any] = {"ok": True, "required": False}
    if tool in CONSEQUENCE or lane == "rah" or (shell and lane == "harness"):
        authority["required"] = True
        if grant_id:
            try:
                from pocket.work_grant import valid as grant_valid

                authority = {**grant_valid(grant_id, capability="rah" if lane == "rah" else "harness"), "required": True}
            except Exception as e:
                authority = {"ok": False, "required": True, "error": str(e)[:160]}
        elif lane == "rah" or tool == "rah_run":
            authority = {"ok": False, "required": True, "error": "WorkGrant required for RAH execute"}

    result: Dict[str, Any] = {}
    phase = "execute"
    if dry:
        phase = "dry"
        result = {"ok": True, "dry": True, "lane": lane}
    elif lane == "rah" and not authority.get("ok"):
        phase = "plan"
        try:
            from pocket.rah import plan_fanout

            result = plan_fanout(goal)
        except Exception as e:
            result = {"ok": False, "error": str(e)[:200]}
        result["hint"] = "POST /v1/rah/grant then POST /v1/agents/turn with grant_id"
    elif lane == "rah":
        from pocket.rah import run_rah

        result = run_rah(goal, grant_id=grant_id, session_id=seat_n, cwd=cwd)
    elif lane == "session":
        from pocket.agent_runtime import create_phoneai_session

        pid = who.get("id") or "researcher"
        result = create_phoneai_session(persona_id=str(pid), title=goal[:80], kind="both")
    elif lane == "talk":
        from pocket.agent_runtime import talk

        result = talk(who.get("id") or "phoneai", "grok", goal)
    elif lane == "invoke":
        from pocket.agent_invoke import invoke

        result = invoke(str(who.get("id") or agent), prompt=goal)
    elif lane == "screen":
        from pocket.screen_body import act as body_act, inhabit

        low = goal.lower()
        if "leave" in low or "stop embodying" in low:
            result = body_act("leave", agent=who.get("id") or agent or "coder")
        elif any(w in low for w in ("type ", "type into")):
            result = body_act("type_into", agent=who.get("id") or agent or "coder", text=goal[:400])
        elif "click" in low:
            result = body_act("click_name", agent=who.get("id") or agent or "coder", name=goal[:80])
        elif "tap" in low or "touch" in low:
            result = body_act("touch", agent=who.get("id") or agent or "coder", kind="tap")
        else:
            result = inhabit(str(who.get("id") or agent or "coder"), which="desktop")
            if "see" in low or "look" in low:
                seen = body_act("see", agent=who.get("id") or agent or "coder")
                result = {**result, "see": {k: seen.get(k) for k in ("ok", "bytes", "which", "via")}}
    else:
        from pocket.work_harness import run as harness_run

        result = harness_run(
            goal,
            engine=str(thought.get("engine") or engine or "auto"),
            shell=shell,
            cwd=cwd,
            timeout=timeout,
        )
        lane = "harness"

    ok = bool(result.get("ok") if isinstance(result, dict) else True)
    receipt = _receipt(turn_id=turn_id, identity=who, thought=thought, execute=lane, ok=ok)
    return {
        "ok": ok if phase == "execute" else True,
        "schema": TURN,
        "arch": SCHEMA,
        "id": turn_id,
        "phase": phase,
        "layers": {
            "identity": who,
            "seat": seat_n,
            "route": thought,
            "authority": authority,
            "execute": lane,
            "receipt": receipt,
        },
        "thought": thought,
        "result": result,
        "reply": (result.get("reply") or result.get("synthesis") or result.get("result") or "") if isinstance(result, dict) else "",
        "ms": int((time.time() - t0) * 1000),
    }
