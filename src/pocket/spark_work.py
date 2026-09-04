"""Spark does real host work — local files, git/GitHub, virtual computer.

The model is OpenAI-compatible. We send tools, run them on this PC, and
loop until Spark answers in text. Paths stay inside allowed roots.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.spark_api import chat as spark_chat

MAX_TURNS = 8
MAX_FILE = 400_000

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 file on this PC.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a UTF-8 file on this PC (local disk).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List a directory (names only).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Bounded PowerShell on this PC. git and gh are allowed. No rm -rf / format / shutdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "cwd": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github",
            "description": "GitHub via signed-in gh: status, list repos, clone, create_pr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["status", "repos", "clone", "pr", "inspect"]},
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "vcomp",
            "description": "POCKET virtual computer: open, shell, or act (click/type/open_url).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "command": {"type": "string"},
                    "name": {"type": "string"},
                    "text": {"type": "string"},
                    "url": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    },
]


def _roots() -> List[Path]:
    home = Path.home()
    out = [
        home / ".pocket",
        home / "OneDrive" / "pocket-os",
        home / "OneDrive" / "PhoneAI",
        home / "OneDrive" / "pocket-mailbox",
        home / "OneDrive" / "sovereign_forge_os",
        home / ".pocket" / "vcomp" / "workspace",
        home / ".pocket" / "workspaces",
        Path(r"E:\repos"),
        Path(r"E:\KILN"),
        Path(r"E:\workspaces"),
    ]
    return [p for p in out if p.exists()]


def _safe_path(raw: str, cwd: str = "") -> Path:
    p = Path(raw or "").expanduser()
    if not p.is_absolute():
        base = Path(cwd).resolve() if cwd else Path.home() / ".pocket" / "phoneai_ws"
        p = (base / p).resolve()
    else:
        p = p.resolve()
    low = str(p).lower()
    for root in _roots():
        try:
            r = str(root.resolve()).lower()
        except Exception:
            continue
        if low == r or low.startswith(r + os.sep) or low.startswith(r + "/"):
            return p
    raise PermissionError(f"path not in allowed roots: {p}")


def _json(ok: bool, **extra: Any) -> str:
    extra["ok"] = ok
    return json.dumps(extra, default=str)[:12000]


def run_tool(name: str, args: Dict[str, Any], *, cwd: str = "") -> str:
    name = (name or "").strip()
    args = args if isinstance(args, dict) else {}
    try:
        if name == "read_file":
            p = _safe_path(str(args.get("path") or ""), cwd)
            if not p.is_file():
                return _json(False, error="not a file", path=str(p))
            text = p.read_text(encoding="utf-8", errors="replace")
            return _json(True, path=str(p), content=text[:MAX_FILE], bytes=p.stat().st_size)
        if name == "write_file":
            p = _safe_path(str(args.get("path") or ""), cwd)
            p.parent.mkdir(parents=True, exist_ok=True)
            body = str(args.get("content") or "")
            if len(body.encode("utf-8")) > MAX_FILE:
                return _json(False, error="file too large")
            p.write_text(body, encoding="utf-8")
            return _json(True, path=str(p), bytes=p.stat().st_size, wrote=True)
        if name == "list_dir":
            p = _safe_path(str(args.get("path") or cwd or "."), cwd)
            if not p.is_dir():
                return _json(False, error="not a directory", path=str(p))
            names = sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())[:80]
            return _json(True, path=str(p), names=names)
        if name == "shell":
            from pocket.shell_exec import run as sh

            cmd = str(args.get("command") or "")
            work = str(args.get("cwd") or cwd or "")
            r = sh(cmd, cwd=work, timeout=40)
            return _json(bool(r.get("ok")), **{k: r.get(k) for k in ("stdout", "stderr", "error", "cwd", "returncode")})
        if name == "github":
            action = str(args.get("action") or "status").lower()
            from pocket.github_hub import create_pr, list_repos, status as gh_status

            if action == "status":
                return _json(True, **gh_status())
            if action == "repos":
                return _json(True, **list_repos(40))
            if action == "clone":
                from pocket.repos import clone_repo

                r = clone_repo(str(args.get("repo") or ""))
                return _json(bool(r.get("ok")), **r)
            if action in ("pr", "create_pr"):
                r = create_pr(str(args.get("title") or "Spark update"), cwd=cwd)
                return _json(bool(r.get("ok")), **r)
            if action in ("inspect", "readme", "tree", "file", "view"):
                return _json(True, **inspect_github(str(args.get("repo") or args.get("path") or "")))
            return _json(False, error=f"unknown github action {action}")
        if name == "vcomp":
            from pocket.virtual_computer import act, open_computer, shell as vc_shell, status as vc_status

            action = str(args.get("action") or "status").lower()
            if action in ("open", "boot"):
                return _json(True, **open_computer())
            if action == "status":
                return _json(True, **vc_status())
            if action == "shell":
                return _json(True, **vc_shell(str(args.get("command") or "echo spark")))
            r = act(
                action,
                command=args.get("command"),
                name=args.get("name"),
                text=args.get("text"),
                url=args.get("url"),
            )
            return _json(bool(r.get("ok")), **r)
        return _json(False, error=f"unknown tool {name}")
    except PermissionError as e:
        return _json(False, error=str(e))
    except Exception as e:
        return _json(False, error=str(e)[:240])


_TOOL_RE = re.compile(
    r"```(?:json)?\s*(\{[\s\S]*?\"tool\"\s*:\s*\"(?:read_file|write_file|list_dir|shell|github|vcomp)\"[\s\S]*?\})\s*```",
    re.I,
)


def _parse_text_tool(text: str) -> Optional[Dict[str, Any]]:
    m = _TOOL_RE.search(text or "")
    blob = m.group(1) if m else ""
    if not blob:
        t = (text or "").strip()
        if t.startswith("{") and '"tool"' in t[:80]:
            blob = t
    if not blob:
        return None
    try:
        j = json.loads(blob)
    except Exception:
        return None
    if isinstance(j, dict) and j.get("tool"):
        return j
    return None


SYS = (
    "You are Spark on POCKET, a Native Agent OS on the operator's Windows PC. "
    "You CAN write files and you CAN read GitHub through host tools (gh). "
    "NEVER say you cannot browse GitHub, cannot open a URL, or cannot write files. "
    "If a GitHub URL is in the prompt, the host may already have fetched README + file tree — use that. "
    "If not, call github with action=inspect and repo=owner/name.\n"
    "Tools: read_file, write_file, list_dir, shell (git/gh), github (status/repos/clone/pr/inspect), vcomp.\n"
    "If native tool_calls are missing, emit ONE JSON object in a fenced block, then wait for TOOL_RESULT.\n"
    '{"tool":"github","action":"inspect","repo":"owner/name"}\n'
    "After tools run, answer with a concrete lane: files to touch, what to write, commands to run."
)


_GH_URL = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", re.I)
_GH_SHORT = re.compile(r"\b([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\b")


def _local_repo_dir(repo: str) -> Optional[Path]:
    name = (repo or "").split("/")[-1]
    aliases = {
        "pocket": Path.home() / "OneDrive" / "pocket-os",
        "pocket-os": Path.home() / "OneDrive" / "pocket-os",
        "phoneai": Path.home() / "OneDrive" / "PhoneAI",
        "pocket-mailbox": Path.home() / "OneDrive" / "pocket-mailbox",
        "kiln-workspace": Path(r"E:\KILN"),
        "kiln": Path(r"E:\repos") / "KILN",
        "sovereign-engine": Path(r"E:\repos") / "sovereign-engine",
    }
    cands = [aliases.get(name.lower())]
    cands += [
        Path.home() / "OneDrive" / name,
        Path(r"E:\repos") / name,
        Path.home() / ".pocket" / "workspaces" / name,
    ]
    for p in cands:
        if p and p.is_dir() and ((p / ".git").exists() or (p / "README.md").is_file()):
            return p
    return None


def inspect_github(spec: str) -> Dict[str, Any]:
    """README + file tree: local clone first, then signed-in gh. Never 'I cannot browse'."""
    import base64

    raw = (spec or "").strip()
    m = _GH_URL.search(raw)
    if m:
        repo = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    elif "/" in raw and " " not in raw.strip():
        repo = raw.replace("https://", "").replace("github.com/", "").strip("/").removesuffix(".git")
    else:
        m2 = _GH_SHORT.search(raw)
        repo = f"{m2.group(1)}/{m2.group(2)}" if m2 else ""
    if not repo or repo.count("/") != 1:
        return {"ok": False, "error": "need owner/name", "repo": repo}

    local = _local_repo_dir(repo)
    if local:
        readme = ""
        for n in ("README.md", "README.MD", "readme.md"):
            fp = local / n
            if fp.is_file():
                readme = fp.read_text(encoding="utf-8", errors="replace")[:8000]
                break
        skip = {".git", "node_modules", "__pycache__", ".venv", "dist", ".pytest_cache"}
        paths: List[str] = []
        for dirpath, dirnames, filenames in os.walk(local):
            dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
            rel = Path(dirpath).relative_to(local)
            for fn in filenames:
                item = fn if str(rel) == "." else str(rel / fn).replace("\\", "/")
                paths.append(item)
                if len(paths) >= 80:
                    break
            if len(paths) >= 80:
                break
        return {
            "ok": True,
            "repo": repo,
            "local": str(local),
            "readme": readme,
            "tree": paths,
            "tree_count": len(paths),
            "via": "local",
        }

    from pocket.github_hub import _gh

    code, readme_b64, err = _gh("api", f"repos/{repo}/readme", "--jq", ".content", timeout=60)
    readme = ""
    if code == 0 and (readme_b64 or "").strip():
        try:
            readme = base64.b64decode(readme_b64.replace("\n", "")).decode("utf-8", errors="replace")
        except Exception:
            readme = readme_b64[:4000]
    code2, tree_raw, err2 = _gh("api", f"repos/{repo}/git/trees/HEAD?recursive=1", timeout=60)
    paths = []
    if code2 == 0:
        try:
            tree = json.loads(tree_raw or "{}")
            for t in (tree.get("tree") or [])[:120]:
                if t.get("type") == "blob":
                    paths.append(str(t.get("path") or ""))
        except Exception:
            paths = []
    return {
        "ok": bool(readme or paths),
        "repo": repo,
        "readme": (readme or "")[:8000],
        "tree": paths[:80],
        "tree_count": len(paths),
        "via": "gh",
        "error": "" if (readme or paths) else (err or err2 or "gh failed")[:400],
    }


def _github_in_prompt(prompt: str) -> str:
    m = _GH_URL.search(prompt or "")
    if m:
        return f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    return ""


def work(prompt: str, *, cwd: str = "", max_turns: int = MAX_TURNS) -> Dict[str, Any]:
    prompt = (prompt or "").strip()
    if not prompt:
        return {"ok": False, "engine": "spark", "error": "say something"}
    cwd = cwd or str(Path.home() / ".pocket" / "phoneai_ws")
    Path(cwd).mkdir(parents=True, exist_ok=True)
    user = prompt[:8000]
    gh_repo = _github_in_prompt(prompt)
    inspected = None
    if gh_repo:
        inspected = inspect_github(gh_repo)
        if inspected.get("ok"):
            user = (
                prompt[:4000]
                + "\n\n--- HOST FETCHED THIS REPO VIA gh (you already have it; do not say you cannot browse) ---\n"
                + f"repo: {inspected.get('repo')}\n"
                + "README:\n"
                + str(inspected.get("readme") or "")[:5000]
                + "\n\nFILE TREE:\n"
                + "\n".join(inspected.get("tree") or [])
            )
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYS + f"\nWorking directory: {cwd}"},
        {"role": "user", "content": user},
    ]
    actions: List[Dict[str, Any]] = []
    last_text = ""
    for _ in range(max(1, min(int(max_turns or MAX_TURNS), 12))):
        r = spark_chat(
            "",
            messages=messages,
            tools=TOOLS,
            max_tokens=2048,
            timeout=90,
        )
        if not r.get("ok") and not r.get("tool_calls") and not r.get("reply"):
            return {**r, "engine": "spark", "cwd": cwd, "actions": actions, "github": inspected}
        tcs = r.get("tool_calls") or []
        text = str(r.get("reply") or "")
        last_text = text
        if tcs:
            messages.append(
                {
                    "role": "assistant",
                    "content": text or None,
                    "tool_calls": tcs,
                }
            )
            for tc in tcs:
                fn = ((tc.get("function") or {}) if isinstance(tc, dict) else {})
                name = str(fn.get("name") or tc.get("name") or "")
                raw_args = fn.get("arguments") or tc.get("arguments") or "{}"
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {"path": raw_args}
                else:
                    args = raw_args if isinstance(raw_args, dict) else {}
                out = run_tool(name, args, cwd=cwd)
                actions.append({"tool": name, "args": {k: args.get(k) for k in args if k != "content"}, "ok": '"ok": true' in out.lower() or '"ok":true' in out.replace(" ", "")})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(tc.get("id") or name),
                        "content": out[:8000],
                    }
                )
            continue
        parsed = _parse_text_tool(text)
        if parsed:
            name = str(parsed.get("tool") or "")
            args = {k: v for k, v in parsed.items() if k != "tool"}
            out = run_tool(name, args, cwd=cwd)
            actions.append({"tool": name, "ok": True, "path": args.get("path")})
            messages.append({"role": "assistant", "content": text[:4000]})
            messages.append({"role": "user", "content": "TOOL_RESULT:\n" + out[:8000] + "\nContinue or finish."})
            continue
        wrote = [a for a in actions if a.get("tool") == "write_file"]
        summary = last_text or "done"
        if wrote and "wrote" not in summary.lower() and "wrote" not in summary.lower():
            summary = summary + "\n\nFiles: " + ", ".join(str(a.get("path") or "") for a in wrote)
        return {
            "ok": True,
            "engine": "spark",
            "reply": summary[-12000:],
            "cwd": cwd,
            "actions": actions,
            "via": r.get("via"),
            "model": r.get("model"),
            "github": inspected,
        }
    return {
        "ok": True,
        "engine": "spark",
        "reply": last_text or "Spark hit the tool-turn limit.",
        "cwd": cwd,
        "actions": actions,
        "github": inspected,
    }
