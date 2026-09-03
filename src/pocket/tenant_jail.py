"""Tenant jail helpers — one path rule for teams, jobs, workers, MCP.

Canonical root: ~/.pocket/tenants/<principal>/teams/<safe-id>/
IDs: [a-z0-9][a-z0-9_-]{0,31}. Principals: [a-z0-9][a-z0-9._-]{0,63}.
Market seats never resolve founder team trees.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
SAFE_PRINCIPAL = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
BLOCKED_PRINCIPALS = frozenset({"", "anonymous", "none", "market"})


def safe_principal(raw: str) -> str:
    p = (raw or "").strip().lower()
    if not p or not SAFE_PRINCIPAL.match(p) or ".." in p or "/" in p or "\\" in p:
        raise ValueError("invalid principal")
    return p


def owner_from_user(user: Optional[Dict[str, Any]] = None) -> str:
    raw = ""
    if user:
        raw = str(user.get("user") or "")
    s = re.sub(r"[^a-z0-9._-]+", "-", (raw or "").strip().lower()).strip("-.")[:64]
    if s in BLOCKED_PRINCIPALS:
        raise ValueError("unauthenticated principal")
    return safe_principal(s)


def safe_team_id(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not SAFE_ID.match(s) or ".." in s or "/" in s or "\\" in s:
        raise ValueError("invalid team id")
    return s


def jail(root: Path, child: Path) -> Path:
    r = root.resolve()
    c = child.resolve()
    c.relative_to(r)
    return c


def is_jailed(root: Path, child: Path) -> bool:
    try:
        jail(root, child)
        return True
    except (ValueError, OSError):
        return False


def tenants_home() -> Path:
    return (Path.home() / ".pocket" / "tenants").resolve()


def team_root(principal: str) -> Path:
    who = safe_principal(principal)
    return (tenants_home() / who / "teams").resolve()


def team_dir(tid: str, principal: str) -> Path:
    root = team_root(principal)
    return jail(root, root / safe_team_id(tid))


def attach_team_to_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Bind job cwd to the owner's jailed team workspace when team_id is set."""
    tid = (job.get("team_id") or "").strip().lower()
    owner = (job.get("owner") or job.get("team_owner") or "").strip().lower()
    if not tid or not owner:
        return job
    try:
        owner = safe_principal(owner)
        safe_team_id(tid)
    except ValueError:
        job["team_id"] = ""
        job["jail_error"] = "invalid team binding"
        return job
    try:
        from pocket.team_workspace import get as team_get

        tw = team_get(tid, principal=owner)
        cwd = tw.get("cwd") or ""
        if tw.get("ok") and cwd:
            d = Path(cwd)
            jail(team_dir(tid, owner), d)
            job["cwd"] = str(d)
            job["team_owner"] = owner
            job["jailed"] = True
    except Exception as e:
        job["jail_error"] = str(e)[:160]
    return job
