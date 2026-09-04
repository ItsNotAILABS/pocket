"""PhoneAI Code desk — wired CLIs + GitHub repos. Not agents.

Choices on the phone:
  1. CLI: Grok CLI · Codex CLI · Meta (Muse Code) · Gemini CLI (Antigravity)
  2. Repo: every GitHub the host `gh` can see, plus local clones
  3. Session: a desk session is (cli + repo). New session starts a fresh CLI
     turn in that repo. It does not attach Pocket agents, personas, or the
     live Grok Build operator session.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / ".pocket" / "phoneai"
SESS_FILE = ROOT / "code_desk_sessions.json"
WS = Path.home() / ".pocket" / "workspaces"
PHONE_WS = Path.home() / ".pocket" / "phoneai_ws"

ORGS = ("ItsNotAILABS", "FreddyCreates")

CODE_CLIS: List[Dict[str, Any]] = [
    {
        "id": "grok",
        "label": "Grok CLI",
        "bins": ["grok"],
        "extra": [Path.home() / ".grok" / "bin" / "grok.exe", Path.home() / ".grok" / "bin" / "grok"],
        "note": "Headless grok --single in the chosen repo. Never the live Grok Build session.",
    },
    {
        "id": "codex",
        "label": "Codex CLI",
        "bins": ["codex"],
        "note": "OpenAI Codex exec in the chosen repo.",
    },
    {
        "id": "meta",
        "label": "Meta (Muse Code)",
        "bins": ["muse", "muse-code", "muse.exe"],
        "note": "Meta Muse Code CLI. Coding desk — not Ollama Glimmer chat.",
    },
    {
        "id": "gemini",
        "label": "Gemini CLI",
        "bins": ["gemini"],
        "extra": [
            Path(os.environ.get("APPDATA") or "") / "npm" / "gemini.cmd",
            Path.home() / "AppData" / "Local" / "Programs" / "Antigravity" / "gemini.exe",
        ],
        "note": "Gemini CLI from the Antigravity platform, run in the chosen repo.",
    },
    {
        "id": "spark",
        "label": "Spark API",
        "bins": [],
        "note": "Reagent Spark · OpenAI-compatible · qwen3.8-27b",
    },
]

CLI_IDS = tuple(c["id"] for c in CODE_CLIS)
ALIASES = {
    "muse": "meta",
    "muse-code": "meta",
    "spark-code": "meta",
    "reagent": "spark",
    "qwen-spark": "spark",
    "antigravity": "gemini",
    "anti": "gemini",
    "agy": "gemini",
    "gemini-cli": "gemini",
}


def _which(spec: Dict[str, Any]) -> str:
    extra = list(spec.get("extra") or [])
    if spec.get("id") == "spark":
        try:
            from pocket.spark_api import status as spark_status

            st = spark_status()
            return str(st.get("base_url") or "") if st.get("configured") else ""
        except Exception:
            return ""
    for n in spec.get("bins") or []:
        w = shutil.which(n) or ""
        if w.lower().endswith(".ps1"):
            cmd = w[:-4] + ".cmd"
            if os.path.isfile(cmd):
                return cmd
            continue
        if w:
            return w
        cmd = shutil.which(n + ".cmd") or ""
        if cmd:
            return cmd
    npm = Path(os.environ.get("APPDATA") or "") / "npm"
    for n in spec.get("bins") or []:
        for cand in (npm / f"{n}.cmd", npm / n):
            if cand.is_file():
                return str(cand)
    for p in extra:
        if p and Path(p).is_file():
            return str(p)
    return ""


def detect_clis() -> List[Dict[str, Any]]:
    out = []
    for spec in CODE_CLIS:
        path = _which(spec)
        out.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "available": bool(path),
                "path": path or None,
                "note": spec.get("note") or "",
                "kind": "cli",
            }
        )
    return out


def _cli_env() -> Dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GROK_")}
    env.pop("GROK_SESSION_ID", None)
    env.pop("GROK_AGENT", None)
    env["CI"] = "1"
    grok = Path.home() / ".grok" / "bin"
    if grok.is_dir():
        env["PATH"] = str(grok) + os.pathsep + env.get("PATH", "")
    return env


def _gh(*args: str, timeout: float = 45) -> Tuple[int, str, str]:
    exe = shutil.which("gh") or ""
    if not exe:
        return 127, "", "gh CLI not installed"
    try:
        r = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except Exception as e:
        return 1, "", str(e)


def _local_roots() -> List[Path]:
    home = Path.home()
    return [
        Path(r"E:\repos"),
        Path(r"E:\KILN"),
        Path(r"E:\workspaces"),
        Path(r"E:\sovereign"),
        home / "OneDrive",
        home / "Documents" / "GitHub",
        home / ".pocket" / "workspaces",
        home / "OneDrive" / "pocket-os",
        home / "OneDrive" / "pocket-mailbox",
        home / "OneDrive" / "pocket-agent",
        home / "OneDrive" / "pocket-voice-to-text",
    ]


def _git_remote(path: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=8,
            encoding="utf-8",
            errors="replace",
        )
        url = (r.stdout or "").strip()
        if "github.com" in url:
            url = url.replace("git@github.com:", "").replace("https://github.com/", "").replace(".git", "")
            return url.strip("/")
    except Exception:
        pass
    return ""


def local_repos() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for root in _local_roots():
        if not root.exists():
            continue
        candidates = []
        if root.is_dir() and ((root / ".git").exists() or (root / ".git").is_file()):
            candidates.append(root)
        if root.is_dir() and root.name.lower() != "onedrive":
            try:
                kids = list(root.iterdir())
            except Exception:
                kids = []
            for child in kids[:80]:
                if child.is_dir() and ((child / ".git").exists() or (child / ".git").is_file()):
                    candidates.append(child)
        for p in candidates:
            key = str(p.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "id": p.name,
                    "name": p.name,
                    "full": p.name,
                    "local": str(p),
                    "source": "local",
                    "url": "",
                }
            )
    return rows


_GH_CACHE: Dict[str, Any] = {"t": 0.0, "rows": []}


def github_repos(limit: int = 80) -> List[Dict[str, Any]]:
    now = time.time()
    if _GH_CACHE["rows"] and now - float(_GH_CACHE["t"] or 0) < 45:
        return list(_GH_CACHE["rows"])
    fields = "name,nameWithOwner,url,description,isPrivate,updatedAt"
    n = str(max(10, min(int(limit or 80), 100)))
    rows: List[Dict[str, Any]] = []
    seen = set()
    queries: List[List[str]] = [["repo", "list", "--limit", n, "--json", fields]]
    for org in ORGS:
        queries.append(["repo", "list", org, "--limit", n, "--json", fields])
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _one(q: List[str]) -> Tuple[int, str, str]:
        return _gh(*q, timeout=25)

    results: List[Tuple[int, str, str]] = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = [pool.submit(_one, q) for q in queries]
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception:
                continue
    for code, out, _err in results:
        if code != 0:
            continue
        try:
            items = json.loads(out or "[]")
        except Exception:
            items = []
        if not isinstance(items, list):
            continue
        for it in items:
            full = str(it.get("nameWithOwner") or "")
            if not full or full in seen:
                continue
            seen.add(full)
            rows.append(
                {
                    "id": full,
                    "name": it.get("name") or full.split("/")[-1],
                    "full": full,
                    "url": it.get("url") or f"https://github.com/{full}",
                    "description": (it.get("description") or "")[:160],
                    "private": bool(it.get("isPrivate")),
                    "updated": it.get("updatedAt") or "",
                    "source": "github",
                    "local": "",
                }
            )
    _GH_CACHE["t"] = now
    _GH_CACHE["rows"] = rows
    return rows


def list_repos(limit: int = 80) -> Dict[str, Any]:
    gh = github_repos(limit)
    loc = local_repos()
    by_full: Dict[str, Dict[str, Any]] = {}
    by_name: Dict[str, Dict[str, Any]] = {}
    for r in gh:
        by_full[r["full"].lower()] = r
        by_name.setdefault(str(r.get("name") or "").lower(), r)
    for r in loc:
        name = str(r.get("name") or "").lower()
        hit = by_name.get(name)
        if hit:
            hit["local"] = r["local"]
            hit["source"] = "github+local"
        else:
            by_full[name or str(r.get("local") or "local")] = r
    repos = sorted(
        by_full.values(),
        key=lambda x: (0 if x.get("local") else 1, str(x.get("full") or x.get("name") or "").lower()),
    )
    return {
        "ok": True,
        "repos": repos,
        "count": len(repos),
        "github": len(gh),
        "local": sum(1 for r in repos if r.get("local")),
        "gh": shutil.which("gh") or "",
    }


def _load_sessions() -> List[Dict[str, Any]]:
    if not SESS_FILE.is_file():
        return []
    try:
        data = json.loads(SESS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_sessions(rows: List[Dict[str, Any]]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    SESS_FILE.write_text(json.dumps(rows[:80], indent=2, default=str), encoding="utf-8")


def list_sessions(limit: int = 40) -> List[Dict[str, Any]]:
    return _load_sessions()[: max(1, min(int(limit or 40), 80))]


def get_session(sid: str) -> Optional[Dict[str, Any]]:
    sid = (sid or "").strip()
    if not sid:
        return None
    for s in _load_sessions():
        if s.get("id") == sid:
            return s
    return None


def ensure_repo_cwd(repo: str) -> Dict[str, Any]:
    """Resolve owner/name or a local path to a writable git cwd."""
    raw = (repo or "").strip()
    if not raw:
        PHONE_WS.mkdir(parents=True, exist_ok=True)
        return {"ok": True, "cwd": str(PHONE_WS), "repo": "", "cloned": False}
    p = Path(raw)
    if p.is_dir() and ((p / ".git").exists() or (p / ".git").is_file() or any(p.iterdir())):
        return {"ok": True, "cwd": str(p), "repo": raw, "cloned": False}
    listed = list_repos(100)
    hit = None
    low = raw.lower().replace("https://github.com/", "").replace(".git", "").strip("/")
    for r in listed.get("repos") or []:
        full = str(r.get("full") or "").lower()
        name = str(r.get("name") or "").lower()
        if low in (full, name) or full.endswith("/" + low) or low.endswith(full):
            hit = r
            break
    if hit and hit.get("local") and Path(hit["local"]).is_dir():
        return {"ok": True, "cwd": hit["local"], "repo": hit.get("full") or raw, "cloned": False}
    spec = hit.get("full") if hit else low
    if "/" not in spec:
        return {"ok": False, "error": f"repo not found locally and not owner/name: {raw}", "cwd": str(PHONE_WS)}
    try:
        from pocket.repos import clone_repo

        cl = clone_repo(spec)
        if cl.get("ok") and cl.get("path"):
            return {"ok": True, "cwd": cl["path"], "repo": spec, "cloned": not cl.get("already")}
        return {"ok": False, "error": cl.get("error") or "clone failed", "cwd": str(PHONE_WS), "clone": cl}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "cwd": str(PHONE_WS)}


def new_session(*, cli: str = "grok", repo: str = "", title: str = "") -> Dict[str, Any]:
    """Start a fresh Code-desk session. Not an agent persona. Not keep-alive."""
    cli = ALIASES.get((cli or "grok").strip().lower(), (cli or "grok").strip().lower())
    if cli not in CLI_IDS:
        cli = "grok"
    wired = {c["id"]: c for c in detect_clis()}
    tool = wired.get(cli) or {}
    loc = ensure_repo_cwd(repo)
    cwd = loc.get("cwd") or str(PHONE_WS)
    Path(cwd).mkdir(parents=True, exist_ok=True)
    sid = "cd-" + uuid.uuid4().hex[:10]
    row = {
        "id": sid,
        "kind": "code-desk",
        "cli": cli,
        "repo": loc.get("repo") or repo or "",
        "cwd": cwd,
        "title": (title or f"{cli} · {Path(cwd).name}")[:80],
        "created": time.time(),
        "updated": time.time(),
        "cli_available": bool(tool.get("available")),
        "cli_path": tool.get("path") or "",
        "cloned": bool(loc.get("cloned")),
    }
    rows = _load_sessions()
    rows.insert(0, row)
    _save_sessions(rows)
    return {
        "ok": True,
        "session": row,
        "repo_ok": bool(loc.get("ok")),
        "repo_error": loc.get("error") or "",
        "note": "New Code-desk session. This is a CLI+repo, not an attached agent.",
    }


def snapshot() -> Dict[str, Any]:
    clis = detect_clis()
    repos = list_repos(80)
    sessions = list_sessions()
    live = sessions[0] if sessions else None
    return {
        "ok": True,
        "product": "PhoneAI Code desk",
        "schema": "phoneai.code-desk.v1",
        "clis": clis,
        "cli_ids": list(CLI_IDS),
        "wired": [c["id"] for c in clis if c.get("available")],
        "repos": repos.get("repos") or [],
        "repo_count": repos.get("count") or 0,
        "sessions": sessions,
        "you_are_working_on": live,
        "not_agents": True,
        "note": (
            "Pick a wired CLI and a GitHub/local repo, then New session. "
            "Send talks to that CLI in that repo. Personas and Pocket agents stay off this surface."
        ),
    }


def _run_cli(cli: str, text: str, cwd: str) -> Dict[str, Any]:
    prompt = (text or "").strip()
    if not prompt:
        return {"ok": False, "engine": cli, "error": "say something"}
    Path(cwd).mkdir(parents=True, exist_ok=True)
    timeout = float(os.environ.get("POCKET_CODE_DESK_TIMEOUT") or "180")

    if cli == "spark":
        from pocket.spark_work import work as spark_work

        r = spark_work(prompt, cwd=cwd)
        r["cwd"] = cwd
        return r

    if cli == "grok":
        from pocket.grok_bridge import run_grok_phone, which_grok

        if not which_grok():
            return {"ok": False, "engine": "grok", "error": "Grok CLI is not on PATH", "cwd": cwd}
        md, err, _eng = run_grok_phone(prompt, cwd)
        ok = bool((md or "").strip()) and "CLI not found" not in (md or "")
        return {
            "ok": ok,
            "engine": "grok",
            "reply": (md or err or "")[-8000:],
            "error": "" if ok else (err or "grok empty"),
            "cwd": cwd,
        }

    if cli == "codex":
        from pocket.executor import _codex_argv, which_codex

        codex = which_codex()
        if not codex:
            return {"ok": False, "engine": "codex", "error": "Codex CLI is not installed on the host", "cwd": cwd}
        cmd = _codex_argv(codex) + ["exec", "--skip-git-repo-check", "-C", cwd, "-s", "workspace-write", "-"]
        try:
            r = subprocess.run(
                cmd,
                cwd=cwd,
                input=prompt[:8000],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=_cli_env(),
            )
            reply = ((r.stdout or "") + ("\n" + r.stderr if r.stderr else "")).strip()
            return {
                "ok": r.returncode == 0,
                "engine": "codex",
                "reply": (reply or f"codex exit {r.returncode}")[-8000:],
                "returncode": r.returncode,
                "cwd": cwd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "engine": "codex", "error": "Codex timed out", "cwd": cwd}

    if cli == "meta":
        spec = next(c for c in CODE_CLIS if c["id"] == "meta")
        muse = _which(spec)
        if not muse:
            return {
                "ok": False,
                "engine": "meta",
                "error": "Meta Muse Code CLI is not on PATH (muse). This desk does not use Ollama Glimmer.",
                "cwd": cwd,
            }
        if muse == "wsl-muse":
            from pocket.phone_agents import _to_wsl

            wdir = _to_wsl(cwd)
            cmd = [
                "wsl",
                "-e",
                "bash",
                "-lc",
                f"export PATH=$HOME/.local/bin:$PATH; cd {wdir!s} && muse exec {prompt[:4000]!r}",
            ]
        else:
            cmd = [muse, "exec", prompt[:6000]]
        try:
            r = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=_cli_env(),
            )
            reply = ((r.stdout or "") + ("\n" + r.stderr if r.stderr else "")).strip()
            return {
                "ok": r.returncode == 0,
                "engine": "meta",
                "via": "muse-code",
                "reply": (reply or f"muse exit {r.returncode}")[-8000:],
                "cwd": cwd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "engine": "meta", "error": "Muse Code timed out", "cwd": cwd}

    if cli == "gemini":
        spec = next(c for c in CODE_CLIS if c["id"] == "gemini")
        gem = _which(spec)
        if not gem:
            return {
                "ok": False,
                "engine": "gemini",
                "error": "Gemini CLI is not on PATH. Install @google/gemini-cli (Antigravity platform).",
                "cwd": cwd,
            }
        try:
            r = subprocess.run(
                [gem, "-p", prompt[:6000]],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=_cli_env(),
            )
            reply = ((r.stdout or "") + ("\n" + r.stderr if r.stderr else "")).strip()
            return {
                "ok": r.returncode == 0,
                "engine": "gemini",
                "via": "gemini-cli",
                "reply": (reply or f"gemini exit {r.returncode}")[-8000:],
                "cwd": cwd,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "engine": "gemini", "error": "Gemini CLI timed out", "cwd": cwd}

    return {"ok": False, "engine": cli, "error": f"CLI not wired on the code desk: {cli}"}


def run(
    text: str,
    *,
    cli: str = "grok",
    session_id: str = "",
    repo: str = "",
    cwd: str = "",
    new: bool = False,
) -> Dict[str, Any]:
    """Talk to a wired CLI in a chosen repo. Never attaches Pocket agents."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "say something"}
    cli = ALIASES.get((cli or "grok").strip().lower(), (cli or "grok").strip().lower())
    if cli not in CLI_IDS:
        cli = "grok"

    sess = get_session(session_id) if session_id else None
    if new or not sess:
        made = new_session(cli=cli, repo=repo or (sess or {}).get("repo") or "", title="")
        sess = made.get("session") or {}
    else:
        if repo:
            loc = ensure_repo_cwd(repo)
            if loc.get("ok"):
                sess["repo"] = loc.get("repo") or repo
                sess["cwd"] = loc.get("cwd") or sess.get("cwd")
        if cli and cli != sess.get("cli"):
            sess["cli"] = cli
        sess["updated"] = time.time()
        rows = [sess] + [s for s in _load_sessions() if s.get("id") != sess.get("id")]
        _save_sessions(rows)

    workdir = cwd or (sess or {}).get("cwd") or str(PHONE_WS)
    Path(workdir).mkdir(parents=True, exist_ok=True)
    result = _run_cli(sess.get("cli") or cli, text, workdir)
    result["session_id"] = sess.get("id") or ""
    result["repo"] = sess.get("repo") or ""
    result["cwd"] = workdir
    result["companion"] = "PhoneAI Code desk"
    result["not_agents"] = True
    try:
        note = f"# {result.get('engine')}\n\n{text}\n\n{result.get('reply') or result.get('error') or ''}\n"
        dest = Path(workdir) / ".phoneai-desk"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f"{int(time.time())}.md").write_text(note, encoding="utf-8")
    except Exception:
        pass
    return result


def run_stream(text: str, **kwargs):
    yield ("status", "running")
    r = run(text, **kwargs)
    reply = str(r.get("reply") or r.get("error") or "")
    step = 120
    for i in range(0, len(reply), step):
        yield ("token", reply[i : i + step])
    yield ("done", r)
