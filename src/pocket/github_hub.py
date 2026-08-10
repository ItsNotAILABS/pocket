"""First-class GitHub integration for POCKET desk + agents.

Uses signed-in `gh` CLI on the host (no tokens stored in POCKET).
Surfaces: status, repos, issues, PRs, clone, create, view.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple


def _gh(*args: str, timeout: float = 45, cwd: str = "") -> Tuple[int, str, str]:
    exe = shutil.which("gh") or ""
    if not exe:
        return 127, "", "gh CLI not installed — install GitHub CLI and run `gh auth login`"
    try:
        r = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or None,
        )
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except Exception as e:
        return 1, "", str(e)


def status() -> Dict[str, Any]:
    from pocket.repos import gh_available

    st = gh_available()
    user = ""
    if st.get("authenticated"):
        code, out, err = _gh("api", "user", "--jq", ".login", timeout=20)
        if code == 0:
            user = (out or "").strip()
    return {
        "ok": bool(st.get("authenticated")),
        "schema": "pocket.github.v1",
        "first_class": True,
        "gh": st.get("gh"),
        "authenticated": bool(st.get("authenticated")),
        "user": user or None,
        "path": st.get("path"),
        "status_snip": (st.get("status") or "")[:400],
        "error": st.get("error") if not st.get("authenticated") else None,
        "desk_mode": "github",
        "api": [
            "GET /v1/github",
            "GET /v1/github/repos",
            "GET /v1/github/issues",
            "GET /v1/github/prs",
            "POST /v1/github/clone",
            "POST /v1/github/create",
            "POST /v1/github/pr",
        ],
        "hint": "gh auth login on host once — POCKET uses your signed-in session",
    }


def list_repos(limit: int = 20) -> Dict[str, Any]:
    from pocket.repos import list_github_repos

    r = list_github_repos(limit=max(1, min(int(limit or 20), 50)))
    r["schema"] = "pocket.github.repos.v1"
    r["first_class"] = True
    return r


def list_issues(limit: int = 15, *, repo: str = "") -> Dict[str, Any]:
    args = ["issue", "list", "--limit", str(max(1, min(int(limit or 15), 40))), "--json", "number,title,url,state,updatedAt,labels"]
    if repo:
        args.extend(["--repo", repo.strip()])
    code, out, err = _gh(*args, timeout=40)
    if code != 0:
        return {"ok": False, "error": (err or out or "gh issue list failed")[:800]}
    try:
        items = json.loads(out or "[]")
    except Exception:
        items = []
    return {"ok": True, "issues": items, "count": len(items), "repo": repo or "default"}


def list_prs(limit: int = 15, *, repo: str = "") -> Dict[str, Any]:
    args = ["pr", "list", "--limit", str(max(1, min(int(limit or 15), 40))), "--json", "number,title,url,state,updatedAt,headRefName,author"]
    if repo:
        args.extend(["--repo", repo.strip()])
    code, out, err = _gh(*args, timeout=40)
    if code != 0:
        return {"ok": False, "error": (err or out or "gh pr list failed")[:800]}
    try:
        items = json.loads(out or "[]")
    except Exception:
        items = []
    return {"ok": True, "prs": items, "count": len(items), "repo": repo or "default"}


def create_pr(
    title: str,
    *,
    body: str = "",
    base: str = "main",
    head: str = "",
    draft: bool = False,
    cwd: str = "",
    repo: str = "",
) -> Dict[str, Any]:
    title = (title or "POCKET update").strip()[:200]
    args = ["pr", "create", "--title", title, "--body", body or "Opened from POCKET desk.", "--base", base or "main"]
    if head:
        args.extend(["--head", head])
    if draft:
        args.append("--draft")
    if repo:
        args.extend(["--repo", repo.strip()])
    code, out, err = _gh(*args, timeout=90, cwd=cwd)
    text = ((out or "") + (err or "")).strip()
    url_m = re.search(r"https://github\.com/[^\s]+/pull/\d+", text)
    return {
        "ok": code == 0,
        "url": url_m.group(0) if url_m else None,
        "out": text[:2000],
        "error": "" if code == 0 else text[:800],
        "message": "PR created" if code == 0 else "PR create failed",
    }


def run_github_job(prompt: str, *, cwd: str = "") -> Tuple[str, str, str]:
    """Desk agent entry — first-class GitHub mode."""
    text = (prompt or "").strip()
    low = text.lower()

    if not text or low in ("help", "?", "commands"):
        return (
            "# GitHub · first-class\n\n"
            "Uses your signed-in `gh` CLI on this host.\n\n"
            "| Command | Action |\n"
            "|---|---|\n"
            "| `status` / `gh status` | Auth + user |\n"
            "| `list repos` / `repos` | Your repositories |\n"
            "| `issues` / `list issues` | Open issues |\n"
            "| `prs` / `list prs` | Open pull requests |\n"
            "| `clone owner/repo` | Shallow clone to ~/.pocket/workspaces |\n"
            "| `create repo name` | New GitHub repo + push |\n"
            "| `pr title: …` | Open a PR from current git cwd |\n"
            "| `open my 5 repos` | Open top repos in Edge |\n"
            "| `analyze <name>` | SCRUTATOR + clone notes |\n\n"
            "_Also: Repos agent · GET /v1/github · agents can link PRs in chat._\n",
            "",
            "github",
        )

    if low in ("status", "gh status", "github status", "auth", "whoami"):
        st = status()
        lines = [
            "# GitHub status",
            "",
            f"- **authenticated:** {st.get('authenticated')}",
            f"- **user:** {st.get('user') or '—'}",
            f"- **gh on PATH:** {st.get('gh')}",
        ]
        if st.get("error"):
            lines.append(f"- **error:** {st['error']}")
        if st.get("status_snip"):
            lines.extend(["", "```", st["status_snip"], "```"])
        return "\n".join(lines), "" if st.get("ok") else (st.get("error") or "not authenticated"), "github"

    if low in ("list repos", "repos", "my repos", "list github", "github list"):
        r = list_repos(20)
        if not r.get("ok"):
            return "", r.get("error") or "list failed", "github"
        lines = [f"# Your GitHub repos ({r.get('count')})", ""]
        for repo in r.get("repos") or []:
            priv = " 🔒" if repo.get("isPrivate") else ""
            lines.append(f"- **{repo.get('name')}**{priv} — {repo.get('url')}")
            if repo.get("description"):
                lines.append(f"  _{repo.get('description')}_")
        return "\n".join(lines), "", "github"

    if low in ("issues", "list issues", "my issues"):
        r = list_issues(15)
        if not r.get("ok"):
            return "", r.get("error") or "issues failed", "github"
        lines = [f"# Issues ({r.get('count')})", ""]
        for it in r.get("issues") or []:
            lines.append(f"- **#{it.get('number')}** {it.get('title')} — {it.get('url')}")
        if not r.get("issues"):
            lines.append("_No open issues in default repo context._")
        return "\n".join(lines), "", "github"

    if low in ("prs", "list prs", "pulls", "pull requests"):
        r = list_prs(15)
        if not r.get("ok"):
            return "", r.get("error") or "prs failed", "github"
        lines = [f"# Pull requests ({r.get('count')})", ""]
        for pr in r.get("prs") or []:
            lines.append(f"- **#{pr.get('number')}** {pr.get('title')} — {pr.get('url')}")
        if not r.get("prs"):
            lines.append("_No open PRs in default repo context._")
        return "\n".join(lines), "", "github"

    if low.startswith("clone "):
        from pocket.repos import clone_repo

        r = clone_repo(text[6:].strip())
        msg = r.get("message") or str(r)
        return f"# Clone\n\n{msg}\n\nPath: `{r.get('path') or '—'}`\n", "" if r.get("ok") else r.get("error", ""), "github"

    if low.startswith("create repo ") or low.startswith("github create ") or low.startswith("gh create "):
        from pocket.repos import create_github_repo

        name = re.sub(r"^(create repo|github create|gh create)\s+", "", text, flags=re.I).strip()
        r = create_github_repo(name)
        return f"# Create repo\n\n{r.get('message') or r}\n\n```\n{(r.get('out') or '')[:1200]}\n```\n", "" if r.get("ok") else r.get("error", ""), "github"

    if low.startswith("pr ") or low.startswith("pull request ") or low.startswith("create pr"):
        title = re.sub(r"^(pr|pull request|create pr)\s*:?\s*", "", text, flags=re.I).strip() or "POCKET update"
        r = create_pr(title, cwd=cwd)
        out = f"# Pull request\n\n{r.get('message')}\n"
        if r.get("url"):
            out += f"\n{r['url']}\n"
        if r.get("out"):
            out += f"\n```\n{r['out'][:800]}\n```\n"
        return out, "" if r.get("ok") else r.get("error", ""), "github"

    # Delegate analyze / open / folder ops to repos agent
    from pocket.repos import run_repos_job

    return run_repos_job(prompt)
