"""PhoneAI dual write: sovereign file explorer + mini-git vault."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from pocket.platform_space import list_space, tenant_root
from pocket.sovereign_git import _run_git, create_repo, list_repos


REPO = "phoneai-desk"
USER = "phoneai"


def explorer_root() -> Path:
    return tenant_root(USER) / "files"


def vault_repo() -> Dict[str, Any]:
    return create_repo(REPO, description="PhoneAI sovereign desk — mini GitHub inside POCKET")


def dual_write(rel: str, content: str, *, message: str = "") -> Dict[str, Any]:
    """Write into the virtual explorer AND commit into sovereign git."""
    rel = (rel or "notes/from-phone.md").replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return {"ok": False, "error": "path escape"}
    text = content if content.endswith("\n") else content + "\n"
    exp = explorer_root() / rel
    exp.parent.mkdir(parents=True, exist_ok=True)
    exp.write_text(text, encoding="utf-8")
    git = vault_repo()
    gp = Path(git.get("path") or "")
    gfile = gp / rel
    gfile.parent.mkdir(parents=True, exist_ok=True)
    gfile.write_text(text, encoding="utf-8")
    msg = (message or f"phoneai: {rel}")[:120]
    if gp.is_dir():
        _run_git(["add", rel], gp)
        _run_git(
            ["-c", "user.email=phoneai@pocket.local", "-c", "user.name=PhoneAI", "commit", "-m", msg],
            gp,
        )
    gh = {}
    try:
        from pocket.phoneai_github import write_and_push

        gh = write_and_push(rel, text, message=msg)
    except Exception as e:
        gh = {"ok": False, "error": str(e)[:160]}
    return {
        "ok": True,
        "explorer": str(exp),
        "git": str(gfile),
        "repo": git.get("name"),
        "clone": git.get("clone") or git.get("path"),
        "github": gh,
        "list": list_space(USER, "files"),
        "repos": list_repos(),
    }


def dual_write_bytes(rel: str, data: bytes, *, message: str = "") -> Dict[str, Any]:
    """Binary twin write (photos) into explorer + git."""
    rel = (rel or "photos/from-phone.jpg").replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return {"ok": False, "error": "path escape"}
    blob = data or b""
    exp = explorer_root() / rel
    exp.parent.mkdir(parents=True, exist_ok=True)
    exp.write_bytes(blob)
    git = vault_repo()
    gp = Path(git.get("path") or "")
    gfile = gp / rel
    gfile.parent.mkdir(parents=True, exist_ok=True)
    gfile.write_bytes(blob)
    msg = (message or f"phoneai: {rel}")[:120]
    if gp.is_dir():
        _run_git(["add", rel], gp)
        _run_git(
            ["-c", "user.email=phoneai@pocket.local", "-c", "user.name=PhoneAI", "commit", "-m", msg],
            gp,
        )
    return {"ok": True, "explorer": str(exp), "git": str(gfile), "bytes": len(blob)}


def ensure_user_seat() -> Dict[str, Any]:
    """PhoneAI is its own market seat — not the founder `pocket` login."""
    import secrets

    from pocket.model_clis import provision_seat_clis
    from pocket.users import list_users, register

    names = {u.get("user") for u in list_users()}
    if USER in names:
        provision_seat_clis(USER)
        vault_repo()
        twin = {}
        try:
            from pocket.twin_mint import mint as mint_twin

            twin = mint_twin(USER)
        except Exception as e:
            twin = {"ok": False, "error": str(e)[:160]}
        return {"ok": True, "user": USER, "created": False, "explorer": str(explorer_root()), "twin": twin}
    note = Path.home() / ".pocket" / "phoneai" / "ACCESS.txt"
    pw = ""
    if note.is_file():
        for line in note.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("password:"):
                pw = line.split(":", 1)[-1].strip()
                break
    if len(pw) < 8:
        pw = secrets.token_urlsafe(18)
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            "PHONEAI SEAT (separate from owner `pocket`)\n"
            "================================================\n"
            f"Username: {USER}\n"
            f"Password: {pw}\n\n"
            "This seat owns ~/.pocket/tenants/phoneai and git repo phoneai-desk.\n"
            "Owner login stays ACCESS.txt.\n",
            encoding="utf-8",
        )
    res = register(
        USER,
        pw,
        "",
        display="PhoneAI",
        accepted_terms=True,
        plan="phone",
        channel="phoneai",
    )
    provision_seat_clis(USER)
    vault_repo()
    explorer_root().mkdir(parents=True, exist_ok=True)
    twin = {}
    try:
        from pocket.twin_mint import mint as mint_twin

        twin = mint_twin(USER)
    except Exception as e:
        twin = {"ok": False, "error": str(e)[:160]}
    return {**res, "user": USER, "created": bool(res.get("ok")), "explorer": str(explorer_root()), "twin": twin}


def snapshot() -> Dict[str, Any]:
    seat = ensure_user_seat()
    vault_repo()
    return {
        "ok": True,
        "seat": {"user": USER, "created": seat.get("created"), "ok": seat.get("ok")},
        "explorer": str(explorer_root()),
        "space": list_space(USER, "files"),
        "git": list_repos(),
        "repo": REPO,
    }
