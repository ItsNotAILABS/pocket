"""Product-gate MCP dispatch — team and endure tools are first-class, not nested.

Call this before screen-tool handlers. Team tools are tenant-jailed.
Endure tools never advertise learning without native stateful evaluation.
"""

from __future__ import annotations

from typing import Any, Dict

TEAM_TOOLS = frozenset(
    {
        "team_open",
        "team_list",
        "team_note",
        "team_invite",
        "team_workspace",
        "team_tick",
        "team_bind",
        "team_status",
        "team_worker",
    }
)
ENDURE_TOOLS = frozenset({"endure_run", "endure_status", "auro_endure", "endure_enqueue"})


def handles(tool: str) -> bool:
    t = (tool or "").strip().lower()
    return t in TEAM_TOOLS or t in ENDURE_TOOLS


def _owner(params: Dict[str, Any]) -> str:
    from pocket.tenant_jail import owner_from_user

    return owner_from_user({"user": str(params.get("owner") or params.get("principal") or "pocket")})


def dispatch(tool: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    t = (tool or "").strip().lower()
    p = params or {}
    if t in TEAM_TOOLS:
        return _team(t, p)
    if t in ENDURE_TOOLS:
        return _endure(t, p)
    return {"ok": False, "error": f"unknown gate tool {tool}"}


def _team(t: str, params: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.team_workspace import get as team_get, invite as team_invite, list_teams, note as team_note, open_team, snapshot as team_snap
    from pocket.team_worker import bind_seat, status as tw_status, tick as tw_tick

    try:
        owner = _owner(params)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    if t in ("team_status", "team_worker"):
        return tw_status()
    if t == "team_tick":
        return tw_tick(principal=owner)
    if t == "team_list":
        return list_teams(principal=owner)
    if t == "team_workspace":
        return team_snap(principal=owner) if not params.get("id") else team_get(str(params.get("id")), principal=owner)
    if t == "team_invite" or t == "team_bind":
        tid = str(params.get("id") or params.get("team") or "")
        agent = str(params.get("agent") or params.get("name") or "")
        return bind_seat(tid, agent, principal=owner) if t == "team_bind" else team_invite(tid, agent, principal=owner)
    if t == "team_note":
        return team_note(
            str(params.get("id") or ""),
            str(params.get("text") or params.get("note") or ""),
            agent=str(params.get("agent") or "mcp"),
            principal=owner,
        )
    return open_team(
        str(params.get("goal") or params.get("prompt") or ""),
        team_id=str(params.get("id") or ""),
        agents=list(params.get("agents") or []) or None,
        label=str(params.get("label") or ""),
        principal=owner,
    )


def _endure(t: str, params: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.endure_worker import enqueue, run, status

    if t == "endure_status":
        return status()
    if t == "endure_enqueue":
        return enqueue(
            str(params.get("goal") or params.get("prompt") or params.get("text") or ""),
            experiments=int(params.get("experiments") or 2),
            cycles=int(params.get("cycles") or 1),
        )
    return run(
        str(params.get("goal") or params.get("prompt") or params.get("text") or ""),
        experiments=int(params.get("experiments") or 2),
        cycles=int(params.get("cycles") or 1),
    )
