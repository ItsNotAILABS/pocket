"""POCKET work surface hierarchy — not files-only.

Layers (high → low commitment):
  1. simulation / preview  — see it before anything is committed
  2. browser               — live web editing / research surfaces
  3. cloud                 — GitHub drafts, PRs (review before merge)
  4. local                 — host disk projects, pixel artifacts
  5. hardware              — desktop apps, vision, capture, shell

Drafts live under ~/.pocket/drafts/ until explicitly promoted to
folder or GitHub. Agents should prefer draft → preview → promote.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "drafts"
ROOT.mkdir(parents=True, exist_ok=True)
INDEX = ROOT / "index.json"

# Execution hierarchy — harness + desk use this order of preference
LAYERS: List[Dict[str, Any]] = [
    {
        "id": "hardware",
        "name": "Hardware",
        "rank": 1,
        "blurb": "This PC: desktop apps, vision eyes, capture, terminals",
        "modes": ["desktop", "vision", "oculus", "capture", "term", "shell", "wsl", "wsl_native"],
        "agents": ["desktop", "vision", "capture", "term"],
        "commit": "irreversible host actions — confirm high-risk opens",
    },
    {
        "id": "local",
        "name": "Local disk",
        "rank": 2,
        "blurb": "Host folders, native projects, pixel memory, coding swarm",
        "modes": ["codex", "claude", "grok", "coding_swarm", "wiki", "plan", "build"],
        "agents": ["codex", "claude", "grok", "coding_swarm"],
        "commit": "writes under workspace / ~/.pocket — review diffs",
    },
    {
        "id": "browser",
        "name": "Browser",
        "rank": 3,
        "blurb": "Edge/session web work, live URLs, in-pane browser",
        "modes": ["browser", "web", "copilot"],
        "agents": ["browser", "web"],
        "commit": "no host files until export/save",
    },
    {
        "id": "cloud",
        "name": "Cloud / GitHub",
        "rank": 4,
        "blurb": "Repos, issues, PRs — promote drafts when ready",
        "modes": ["github", "gh", "repos", "git"],
        "agents": ["github", "repos"],
        "commit": "remote side-effects — PR/push needs intent",
    },
    {
        "id": "preview",
        "name": "Preview / simulation",
        "rank": 0,
        "blurb": "In-chat bubbles: HTML apps, URLs, simulations — before commit",
        "modes": ["preview", "studio"],
        "agents": ["*"],
        "commit": "ephemeral — nothing shipped until promote",
    },
]


def hierarchy() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.work_surface.v1",
        "doctrine": (
            "Preview → Browser/Local draft → Review → Promote to folder or GitHub. "
            "Hardware is for embodiment; cloud is for publish."
        ),
        "layers": LAYERS,
        "drafts_root": str(ROOT),
        "promote": ["folder", "github", "pixel"],
    }


def _load_index() -> Dict[str, Any]:
    if INDEX.exists():
        try:
            return json.loads(INDEX.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"drafts": [], "updated": 0}


def _save_index(idx: Dict[str, Any]) -> None:
    idx["updated"] = time.time()
    INDEX.write_text(json.dumps(idx, indent=2), encoding="utf-8")


def list_drafts(limit: int = 40) -> Dict[str, Any]:
    idx = _load_index()
    items = list(reversed(idx.get("drafts") or []))[: max(1, min(int(limit or 40), 100))]
    return {"ok": True, "count": len(items), "drafts": items, "root": str(ROOT)}


def create_draft(
    *,
    title: str = "Untitled draft",
    kind: str = "html",
    content: str = "",
    layer: str = "preview",
    source: str = "agent",
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    did = uuid.uuid4().hex[:12]
    title = (title or "Untitled draft").strip()[:120]
    kind = re.sub(r"[^a-z0-9_-]", "", (kind or "html").lower())[:20] or "html"
    layer = (layer or "preview").lower()
    body = content or ""
    if kind in ("html", "htm", "app", "sim", "simulation") and body and "<html" not in body.lower():
        body = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{_esc(title)}</title>"
            f"<style>body{{font-family:system-ui,sans-serif;margin:16px;background:#0a0a0c;color:#e4e4e7}}"
            f"button,input{{font:inherit}}</style></head><body>\n{body}\n</body></html>"
        )
    ext = {
        "html": ".html",
        "htm": ".html",
        "app": ".html",
        "sim": ".html",
        "simulation": ".html",
        "md": ".md",
        "markdown": ".md",
        "js": ".js",
        "ts": ".ts",
        "py": ".py",
        "json": ".json",
        "txt": ".txt",
    }.get(kind, ".txt")
    path = ROOT / f"{did}{ext}"
    path.write_text(body, encoding="utf-8")
    rec = {
        "id": did,
        "title": title,
        "kind": kind,
        "layer": layer,
        "path": str(path),
        "bytes": path.stat().st_size,
        "source": source,
        "meta": meta or {},
        "created_at": time.time(),
        "status": "draft",
    }
    # Wire HTML drafts into in-chat preview serve
    if ext == ".html":
        try:
            from pocket.app_preview import put_html

            prev = put_html(body, title=title, source=f"draft:{did}")
            if prev.get("ok"):
                rec["preview_id"] = prev["id"]
                rec["preview_url"] = prev["url"]
                rec["fence"] = prev.get("fence") or (
                    f"```preview\ntitle: {title}\nurl: {prev['url']}\n```\n"
                )
        except Exception:
            rec["fence"] = f"```html-preview\n{body[:12000]}\n```\n"
    else:
        rec["fence"] = f"```{kind}\n{body[:8000]}\n```\n"

    idx = _load_index()
    drafts = idx.get("drafts") or []
    drafts.append(rec)
    idx["drafts"] = drafts[-200:]
    _save_index(idx)
    return {"ok": True, **rec}


def get_draft(draft_id: str) -> Dict[str, Any]:
    did = re.sub(r"[^a-zA-Z0-9_-]", "", draft_id or "")[:32]
    idx = _load_index()
    for d in idx.get("drafts") or []:
        if d.get("id") == did:
            p = Path(d.get("path") or "")
            content = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
            return {"ok": True, "draft": d, "content": content}
    return {"ok": False, "error": "draft not found"}


def update_draft(draft_id: str, content: str, *, title: str = "") -> Dict[str, Any]:
    g = get_draft(draft_id)
    if not g.get("ok"):
        return g
    d = g["draft"]
    p = Path(d["path"])
    p.write_text(content or "", encoding="utf-8")
    d["bytes"] = p.stat().st_size
    d["updated_at"] = time.time()
    if title:
        d["title"] = title[:120]
    if d.get("kind") in ("html", "app", "sim", "simulation", "htm"):
        try:
            from pocket.app_preview import put_html

            prev = put_html(content or "", title=d.get("title") or "Draft", source=f"draft:{d['id']}")
            if prev.get("ok"):
                d["preview_id"] = prev["id"]
                d["preview_url"] = prev["url"]
                d["fence"] = prev.get("fence")
        except Exception:
            pass
    idx = _load_index()
    drafts = []
    for x in idx.get("drafts") or []:
        drafts.append(d if x.get("id") == d["id"] else x)
    idx["drafts"] = drafts
    _save_index(idx)
    return {"ok": True, "draft": d}


def promote_draft(
    draft_id: str,
    *,
    target: str = "folder",
    name: str = "",
    public: bool = True,
) -> Dict[str, Any]:
    """Promote draft → local folder or GitHub (explicit commit step)."""
    g = get_draft(draft_id)
    if not g.get("ok"):
        return g
    d = g["draft"]
    content = g.get("content") or ""
    title = name or d.get("title") or f"draft-{d['id']}"
    target = (target or "folder").lower()

    if target in ("folder", "local", "disk"):
        from pocket.repos import create_folder

        folder = create_folder(title)
        if not folder.get("ok"):
            return folder
        dest = Path(folder["path"])
        # pick extension from kind
        ext = Path(d.get("path") or "x.html").suffix or ".txt"
        out = dest / f"main{ext}"
        out.write_text(content, encoding="utf-8")
        (dest / "DRAFT.json").write_text(json.dumps(d, indent=2), encoding="utf-8")
        d["status"] = "promoted_folder"
        d["promoted_path"] = str(dest)
        _touch_draft(d)
        return {
            "ok": True,
            "promoted": "folder",
            "path": str(dest),
            "file": str(out),
            "draft": d,
            "message": f"Promoted draft → {dest}",
        }

    if target in ("github", "gh", "cloud"):
        from pocket.repos import create_github_repo, init_git_repo

        local = init_git_repo(title)
        if not local.get("ok"):
            return local
        path = Path(local["path"])
        ext = Path(d.get("path") or "x.html").suffix or ".txt"
        (path / f"main{ext}").write_text(content, encoding="utf-8")
        (path / "README.md").write_text(
            f"# {title}\n\nPromoted from POCKET draft `{d['id']}`.\n",
            encoding="utf-8",
        )
        gh = create_github_repo(title, public=public, source_path=str(path))
        d["status"] = "promoted_github" if gh.get("ok") else "promote_github_failed"
        d["promoted_path"] = str(path)
        d["github"] = gh
        _touch_draft(d)
        return {
            "ok": bool(gh.get("ok")),
            "promoted": "github",
            "path": str(path),
            "github": gh,
            "draft": d,
            "message": gh.get("message") or "GitHub promote attempted",
            "error": gh.get("error") or "",
        }

    if target in ("pixel", "vmem", "artifact"):
        from pocket.pixel_vmem import put_artifact

        a = put_artifact(
            content,
            title=title,
            language=(d.get("kind") or "md")[:12],
            agent="draft",
            run_id=d.get("id") or "",
            tags=["draft", "promoted", d.get("layer") or "preview"],
        )
        d["status"] = "promoted_pixel"
        d["pixel"] = a
        _touch_draft(d)
        return {"ok": bool(a.get("ok")), "promoted": "pixel", "artifact": a, "draft": d}

    return {"ok": False, "error": f"unknown promote target: {target}"}


def _touch_draft(d: Dict[str, Any]) -> None:
    idx = _load_index()
    drafts = []
    for x in idx.get("drafts") or []:
        drafts.append(d if x.get("id") == d.get("id") else x)
    idx["drafts"] = drafts
    _save_index(idx)


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def layer_for_mode(mode: str) -> str:
    m = (mode or "").lower()
    for layer in LAYERS:
        if m in (layer.get("modes") or []):
            return layer["id"]
    return "local"


def harness_layers() -> Dict[str, Any]:
    """How harness maps onto the hierarchy — for desk + docs."""
    return {
        "ok": True,
        "schema": "pocket.harness.layers.v1",
        "map": {
            "hardware": {
                "subagents": ["PORTARIUS", "OCULUS"],
                "when": "open apps, click UI, screenshot, shell",
            },
            "local": {
                "subagents": ["FORGE_HEADLESS", "DESIGN", "SENTINEL_HEADLESS"],
                "when": "code, tests, security, ship on host disk",
            },
            "browser": {
                "subagents": ["NAVIGATOR", "RESEARCH_HEADLESS"],
                "when": "web research, live site work",
            },
            "cloud": {
                "subagents": ["ARCHON", "SHIP_HEADLESS"],
                "when": "GitHub PR, release, multi-agent orchestration",
            },
            "preview": {
                "subagents": ["DESIGN"],
                "when": "HTML/app/sim bubbles before promote",
            },
        },
        "policy": (
            "Auto-plan helpers by task keywords; @mentions always win; "
            "prefer draft+preview before cloud promote."
        ),
    }
