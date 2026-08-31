"""PhoneAI writes to GitHub the same way Pocket does — public vault + product repo."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

ORG = "ItsNotAILABS"
FALLBACK_OWNER = "FreddyCreates"
REPO = "phoneai-desk"
PRODUCT = "PhoneAI"
LOCAL = Path.home() / ".pocket" / "tenants" / "phoneai" / "github"
STATE = Path.home() / ".pocket" / "phoneai" / "github.json"
_lock = threading.Lock()
_pending = False


def _run(args: list, *, cwd: Optional[Path] = None, timeout: float = 40) -> Dict[str, Any]:
    try:
        r = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return {"ok": r.returncode == 0, "code": r.returncode, "out": out[-2000:]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _gh() -> str:
    return "gh"


def _save_state(d: Dict[str, Any]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d, indent=2, default=str), encoding="utf-8")


def snapshot() -> Dict[str, Any]:
    st = {}
    if STATE.is_file():
        try:
            st = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            st = {}
    return {
        "ok": True,
        "org": ORG,
        "repo": f"{ORG}/{REPO}",
        "product": f"{ORG}/{PRODUCT}",
        "local": str(LOCAL),
        "url": st.get("url") or f"https://github.com/{ORG}/{REPO}",
        "last_push": st.get("last_push"),
        "last_out": (st.get("out") or "")[:240],
    }


def ensure_repo() -> Dict[str, Any]:
    LOCAL.mkdir(parents=True, exist_ok=True)
    if not (LOCAL / ".git").is_dir():
        _run(["git", "init", "-b", "main"], cwd=LOCAL)
        _run(["git", "-c", "user.email=phoneai@pocket.local", "-c", "user.name=PhoneAI", "commit", "--allow-empty", "-m", "PhoneAI desk vault"], cwd=LOCAL)
    readme = LOCAL / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# PhoneAI desk\n\nLive vault from the PhoneAI seat on POCKET. Notes, work, photos, sessions.\n",
            encoding="utf-8",
        )
    rem = _run(["git", "remote", "get-url", "origin"], cwd=LOCAL)
    if rem.get("ok") and rem.get("out"):
        url = rem["out"].strip().replace(".git", "")
        if url.endswith(".git"):
            url = url[:-4]
        _save_state({"url": url})
        return {"ok": True, "url": url, "local": str(LOCAL)}
    for spec in (f"{ORG}/{REPO}", f"{FALLBACK_OWNER}/{REPO}"):
        view = _run([_gh(), "repo", "view", spec, "--json", "url", "-q", ".url"], timeout=20)
        if view.get("ok") and "github.com" in (view.get("out") or ""):
            url = view["out"].strip().splitlines()[0]
            if url.startswith("git@"):
                # gh may print ssh; HTTPS works with gh credentials on this PC
                url = "https://github.com/" + url.split(":", 1)[-1]
            url = url.replace(".git", "")
            _run(["git", "remote", "remove", "origin"], cwd=LOCAL)
            _run(["git", "remote", "add", "origin", url + ".git"], cwd=LOCAL)
            _save_state({"url": url})
            return {"ok": True, "url": url, "local": str(LOCAL)}
    created = _run(
        [
            _gh(),
            "repo",
            "create",
            f"{ORG}/{REPO}",
            "--public",
            "--description",
            "PhoneAI seat vault — notes, work, sessions from the phone kernel",
            "--source",
            str(LOCAL),
            "--remote",
            "origin",
            "--push",
        ],
        cwd=LOCAL,
        timeout=90,
    )
    if not created.get("ok"):
        created = _run(
            [_gh(), "repo", "create", f"{FALLBACK_OWNER}/{REPO}", "--public", "--source", str(LOCAL), "--remote", "origin", "--push"],
            cwd=LOCAL,
            timeout=90,
        )
    out = created.get("out") or ""
    url = next((ln.strip() for ln in out.splitlines() if "github.com/" in ln), f"https://github.com/{FALLBACK_OWNER}/{REPO}")
    _save_state({"url": url, "created": created})
    return {"ok": bool(created.get("ok")), "url": url, "create": created, "local": str(LOCAL)}


def stage_file(rel: str, content: str) -> Path:
    rel = (rel or "notes/from-phone.md").replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        rel = "notes/from-phone.md"
    fp = LOCAL / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    text = content if content.endswith("\n") else content + "\n"
    fp.write_text(text, encoding="utf-8")
    return fp


def push(*, message: str = "phoneai") -> Dict[str, Any]:
    with _lock:
        ready = ensure_repo()
        _run(["git", "add", "-A"], cwd=LOCAL)
        c = _run(
            ["git", "-c", "user.email=phoneai@pocket.local", "-c", "user.name=PhoneAI", "commit", "-m", (message or "phoneai")[:120]],
            cwd=LOCAL,
        )
        p = _run(["git", "push", "-u", "origin", "HEAD"], cwd=LOCAL, timeout=60)
        url = ready.get("url") or f"https://github.com/{ORG}/{REPO}"
        st = {"ok": bool(p.get("ok")), "url": url, "commit": c.get("out"), "out": p.get("out") or p.get("error"), "last_push": time.time()}
        _save_state(st)
        return st


def push_later(*, message: str = "phoneai") -> None:
    global _pending
    if _pending:
        return
    _pending = True

    def _go() -> None:
        global _pending
        time.sleep(2.5)
        try:
            push(message=message)
        except Exception:
            pass
        _pending = False

    threading.Thread(target=_go, daemon=True, name="phoneai-gh").start()


def write_and_push(rel: str, content: str, *, message: str = "") -> Dict[str, Any]:
    fp = stage_file(rel, content)
    push_later(message=message or f"phoneai: {rel}")
    return {"ok": True, "path": str(fp), "queued": True, "repo": f"{ORG}/{REPO}"}
