"""POCKET Agent OS — native first-class fabric for every agent system.

Parity target (2026): Claude Code Desktop · Antigravity · Emergent · Replit
— but **on your host**, no cloud IDE lock-in.

What this layer does:
  - Registers every major POCKET system as a first-class **screen + API**
  - Binds agents to AI versions (codex / grok / claude / plan / local)
  - Project workspaces (Replit-like folders + run)
  - Artifact execution (run code from pixel memory)
  - Live parity matrix + readiness for the desk
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from pocket import __version__, LAB, PRODUCT, TAGLINE

ROOT = Path.home() / ".pocket" / "agent_os"
PROJECTS = ROOT / "projects"
RUNS = ROOT / "runs"
TIMELINE = ROOT / "timeline.jsonl"
for d in (ROOT, PROJECTS, RUNS):
    d.mkdir(parents=True, exist_ok=True)

_lock = Lock()

# ---------------------------------------------------------------------------
# First-class system registry
# ---------------------------------------------------------------------------

SYSTEMS: List[Dict[str, Any]] = [
    {
        "id": "desk",
        "name": "Agent Desk",
        "kind": "screen",
        "route": "/desk",
        "api": ["/v1/sessions", "/v1/status"],
        "parity": ["claude_code", "antigravity"],
        "blurb": "Multi-agent chat · live streams · iMessage bubbles · Stop/End",
        "tier": "core",
    },
    {
        "id": "coding_swarm",
        "name": "Coding Swarm Harness",
        "kind": "agent_system",
        "route": "/desk",
        "mode": "coding_swarm",
        "api": ["/v1/swarm", "/v1/vmem/artifacts"],
        "parity": ["emergent", "antigravity", "claude_code"],
        "blurb": "Sophia · Solver · Twin — multi-agent code with pixel artifacts",
        "tier": "class",
    },
    {
        "id": "pixel_memory",
        "name": "Pixel Memory Lattice",
        "kind": "memory",
        "route": "/desk",
        "api": ["/v1/vmem", "/v1/vmem/artifacts", "/v1/vmem/look", "/v1/vmem/recreate", "/v1/vmem/pass"],
        "parity": ["replit", "claude_code"],
        "blurb": "Store · look · recreate · pass · map — visual agent memory",
        "tier": "class",
    },
    {
        "id": "claude_sdk",
        "name": "Claude Agent SDK Loop",
        "kind": "engine",
        "route": "/desk",
        "mode": "claude",
        "api": [],
        "parity": ["claude_code"],
        "blurb": "Embedded Claude Code tool loop + sandbox receipts",
        "tier": "class",
    },
    {
        "id": "codex",
        "name": "Codex Engine",
        "kind": "engine",
        "route": "/desk",
        "mode": "codex",
        "api": [],
        "parity": ["claude_code", "replit"],
        "blurb": "Host coding agent with thread resume",
        "tier": "core",
    },
    {
        "id": "grok",
        "name": "Grok Engine",
        "kind": "engine",
        "route": "/desk",
        "mode": "grok",
        "api": [],
        "parity": ["claude_code"],
        "blurb": "Grok CLI coding + research on host",
        "tier": "core",
    },
    {
        "id": "voice",
        "name": "Voice ↔ Voice Agent",
        "kind": "agent_system",
        "route": "/phone",
        "mode": "voice",
        "api": ["/v1/fusion/voice", "/v1/node/redeem", "/v1/node/pair"],
        "parity": ["replit"],
        "blurb": "Aria · first-class on phone + desk · Fusion · pair seamless",
        "tier": "class",
        "surfaces": ["desk", "phone"],
    },
    {
        "id": "phone",
        "name": "POCKET Phone",
        "kind": "surface",
        "route": "/phone",
        "mode": "voice",
        "api": ["/v1/node/redeem", "/v1/node/pair", "/v1/fusion/voice", "/v1/sessions"],
        "parity": [],
        "blurb": "Mobile remote desk · Aria/Working first-class · desk pair codes",
        "tier": "class",
        "surfaces": ["phone"],
    },
    {
        "id": "vision",
        "name": "OCULUS Vision",
        "kind": "agent_system",
        "route": "/desk",
        "mode": "vision",
        "api": [
            "/v1/vision/understand",
            "/v1/vision/ui_map",
            "/v1/vision/observe",
            "/v1/vision/stream",
            "/v1/live/vision",
        ],
        "parity": ["claude_code", "antigravity", "emergent"],
        "blurb": "First-class eyes — observe · UI map · OCR · click-by-name",
        "tier": "class",
    },
    {
        "id": "github",
        "name": "GitHub",
        "kind": "integration",
        "route": "/desk",
        "mode": "github",
        "api": [
            "/v1/github",
            "/v1/github/repos",
            "/v1/github/issues",
            "/v1/github/prs",
            "/v1/github/clone",
            "/v1/github/create",
            "/v1/github/pr",
        ],
        "parity": ["claude_code", "replit", "antigravity"],
        "blurb": "Signed-in gh — repos, issues, PRs, clone, create",
        "tier": "class",
    },
    {
        "id": "app_preview",
        "name": "In-chat App Previews",
        "kind": "ui",
        "route": "/desk",
        "api": ["/v1/preview", "/v1/preview/{id}"],
        "parity": ["replit", "emergent", "claude_code"],
        "blurb": "Agents render live HTML/URL/simulation previews inside chat bubbles",
        "tier": "class",
    },
    {
        "id": "work_surface",
        "name": "Work Surface Hierarchy",
        "kind": "infra",
        "route": "/desk",
        "api": ["/v1/work-surface", "/v1/drafts", "/v1/drafts/promote"],
        "parity": ["replit", "claude_code", "emergent"],
        "blurb": "Preview → draft → local/browser → promote folder or GitHub",
        "tier": "class",
    },
    {
        "id": "screen_share",
        "name": "Screen · Fusion · VComputer",
        "kind": "agent_system",
        "route": "/desk",
        "api": ["/v1/screen", "/v1/screen/frame", "/v1/screen/context", "/v1/screen/act", "/v1/vcomp", "/v1/fusion/remake"],
        "parity": ["claude_code", "antigravity", "emergent"],
        "blurb": "Side column: share any screen, fusion eyes, mouse when Control",
        "tier": "class",
    },
    {
        "id": "habitat",
        "name": "Agent Habitat",
        "kind": "ui",
        "route": "/desk",
        "api": ["/v1/habitat", "/v1/habitat/pulse", "/v1/habitat/assign"],
        "parity": ["claude_code", "antigravity"],
        "blurb": "Hybrid GUI floor — agents live and work beside chat",
        "tier": "class",
    },
    {
        "id": "work_mode",
        "name": "Working Mode",
        "kind": "agent_system",
        "route": "/desk",
        "mode": "work",
        "api": ["/v1/work", "/v1/work/start", "/v1/work/package", "/v1/work/handoff"],
        "parity": ["emergent", "claude_code"],
        "blurb": "Persistent voice + screen + package → artifacts",
        "tier": "class",
    },
    {
        "id": "mcp_bundle",
        "name": "MCP Bundle",
        "kind": "infra",
        "route": "/desk",
        "mode": "mcp",
        "api": ["/v1/mcp", "/v1/mcp/invoke", "/v1/cli", "/v1/cli/run"],
        "parity": ["claude_code", "antigravity"],
        "blurb": "3 internal + 7 external MCPs · agent CLI (no user tabs)",
        "tier": "class",
    },
    {
        "id": "sandbox",
        "name": "Capability Sandbox",
        "kind": "security",
        "route": "/desk",
        "api": ["/v1/sandbox", "/v1/sandbox/profiles"],
        "parity": ["claude_code", "replit"],
        "blurb": "Wasm-shaped grants + receipts — zero ambient authority",
        "tier": "class",
    },
    {
        "id": "wiki",
        "name": "Infinite Wiki",
        "kind": "codebase",
        "route": "/desk",
        "mode": "wiki",
        "api": ["/v1/wiki/profile", "/v1/wiki/search"],
        "parity": ["claude_code", "antigravity"],
        "blurb": "Hierarchical code navigation — never dump whole files",
        "tier": "class",
    },
    {
        "id": "work_studio",
        "name": "Work Studio",
        "kind": "screen",
        "route": "/work",
        "api": [],
        "parity": ["emergent", "antigravity"],
        "blurb": "Design agent loops → hand off to desk",
        "tier": "product",
    },
    {
        "id": "product_studio",
        "name": "Product Studio",
        "kind": "screen",
        "route": "/studio",
        "api": [],
        "parity": ["emergent", "replit"],
        "blurb": "Demos, exports, ship surfaces",
        "tier": "product",
    },
    {
        "id": "projects",
        "name": "Native Projects",
        "kind": "workspace",
        "route": "/os",
        "api": ["/v1/os/projects", "/v1/os/run"],
        "parity": ["replit", "claude_code"],
        "blurb": "Host folders, scaffold, run code, export artifacts",
        "tier": "class",
    },
    {
        "id": "phone",
        "name": "Phone Desk",
        "kind": "screen",
        "route": "/phone",
        "api": [],
        "parity": ["replit"],
        "blurb": "Remote founder desk on your phone",
        "tier": "edge",
    },
    {
        "id": "mesh",
        "name": "Agent Mesh Bus",
        "kind": "infra",
        "route": "/desk",
        "api": [],
        "parity": ["antigravity", "emergent"],
        "blurb": "Hashed multi-agent envelopes + channels",
        "tier": "class",
    },
    {
        "id": "build_loop",
        "name": "Build / Ship Loop",
        "kind": "agent_system",
        "route": "/desk",
        "mode": "build",
        "api": [],
        "parity": ["emergent"],
        "blurb": "Plan → code → test → ship multi-agent use cases",
        "tier": "class",
    },
]


# What the big four do — mapped to native POCKET depth
PARITY: Dict[str, Dict[str, Any]] = {
    "claude_code": {
        "name": "Claude Code Desktop",
        "native": [
            "agent tool loop (Claude Agent SDK + Codex/Grok)",
            "workspace cwd + file edits via engines",
            "terminal / shell modes",
            "session threads + interrupt",
            "sandbox receipts",
            "pixel artifact memory",
        ],
        "deeper": [
            "multi-engine bind (not one vendor model)",
            "coding swarm multi-persona",
            "pixel lattice recreate/pass",
            "founder isolation + mesh",
        ],
    },
    "antigravity": {
        "name": "Antigravity",
        "native": [
            "clean multi-agent desk UI",
            "live stream thinking + bubbles",
            "right rail workspace summary",
            "subagent dispatch",
            "agent picker + resume",
        ],
        "deeper": [
            "local host sovereignty",
            "pixel visual memory",
            "OCULUS first-class vision (observe/map/OCR/click)",
            "capability sandbox profiles",
        ],
    },
    "emergent": {
        "name": "Emergent",
        "native": [
            "use-case / build loops",
            "multi-agent ship factory",
            "coding swarm harness",
            "work studio handoff",
        ],
        "deeper": [
            "always-on swarm pulses",
            "artifacts forced into pixel lattice",
            "AI-version binding per persona",
        ],
    },
    "replit": {
        "name": "Replit",
        "native": [
            "native projects on disk",
            "run code (py/js/ts/sh) from OS",
            "artifact export / recreate",
            "multi-user seats (market edition)",
            "phone remote",
        ],
        "deeper": [
            "no cloud sandbox tax for local work",
            "pixel memory as product memory",
            "voice specialized agent",
            "desktop app embodiment",
        ],
    },
}


def _probe_system(sys: Dict[str, Any]) -> Dict[str, Any]:
    """Live health for one first-class system."""
    sid = sys["id"]
    ok = True
    detail = "ready"
    try:
        if sid == "desk":
            ok = True
            detail = "HTML desk"
        elif sid == "coding_swarm":
            from pocket.coding_swarm import list_roster

            r = list_roster()
            ok = bool(r.get("ok"))
            detail = f"{len(r.get('agents') or [])} personas"
        elif sid == "pixel_memory":
            from pocket.pixel_vmem import status

            st = status()
            ok = bool(st.get("ok"))
            detail = f"{st.get('symbols', 0)} symbols · {st.get('pages', 0)} pages"
        elif sid == "claude_sdk":
            from pocket.claude_agent_bridge import status as cs

            st = cs()
            ok = bool(st.get("sdk_installed"))
            detail = f"sdk={st.get('sdk_installed')} ready={st.get('ready')}"
        elif sid == "codex":
            from pocket.executor import which_codex

            ok = bool(which_codex())
            detail = which_codex() or "not on PATH"
        elif sid == "grok":
            from pocket.executor import which_grok_cli

            ok = bool(which_grok_cli())
            detail = which_grok_cli() or "not on PATH"
        elif sid == "voice":
            # voice mode always registered; API optional
            detail = "Aria persona · specialized voice"
        elif sid == "vision":
            from pocket.vision_core import LAST_OBS, UI_MAP_PATH
            from pocket.live_vision import FRAME_PATH

            bits = []
            if FRAME_PATH.exists():
                bits.append("live-frame")
            if UI_MAP_PATH.exists():
                bits.append("ui-map")
            if LAST_OBS.exists():
                bits.append("last-obs")
            ok = True
            detail = " · ".join(bits) if bits else "ready (no frame yet)"
        elif sid == "github":
            from pocket.github_hub import status as gh_status

            st = gh_status()
            ok = bool(st.get("gh"))
            detail = (
                f"@{st.get('user')}" if st.get("authenticated") else ("gh ready" if st.get("gh") else "gh missing")
            )
        elif sid == "app_preview":
            from pocket.app_preview import status as prev_st

            ps = prev_st()
            ok = True
            detail = f"{ps.get('previews', 0)} stored"
        elif sid == "work_surface":
            from pocket.work_surface import list_drafts

            d = list_drafts(5)
            ok = True
            detail = f"{d.get('count', 0)} drafts"
        elif sid == "habitat":
            from pocket.agent_habitat import status as hab

            h = hab()
            ok = True
            detail = f"{len(h.get('residents') or [])} residents"
        elif sid == "work_mode":
            from pocket.work_mode import status as ws

            w = ws()
            ok = True
            detail = f"live={w.get('live')}"
        elif sid == "mcp_bundle":
            from pocket.mcp_bundle import catalog as mc

            c = mc()
            ok = True
            detail = f"{c.get('total')} servers"
        elif sid == "sandbox":
            from pocket.agent_sandbox import list_profiles

            p = list_profiles()
            ok = bool(p.get("ok"))
            detail = f"{len(p.get('profiles') or {})} profiles"
        elif sid == "wiki":
            from pocket.infinite_wiki import status as ws

            w = ws()
            ok = bool(w.get("ok"))
            detail = f"nodes={w.get('nodes')}"
        elif sid == "projects":
            n = len([p for p in PROJECTS.iterdir() if p.is_dir()]) if PROJECTS.is_dir() else 0
            detail = f"{n} projects"
        elif sid == "mesh":
            from pocket.mesh_disk import mesh_root

            ok = Path(mesh_root()).is_dir()
            detail = str(mesh_root())
        elif sid == "build_loop":
            from pocket.use_cases import list_use_cases

            uc = list_use_cases()
            ok = len(uc) > 0
            detail = f"{len(uc)} use cases"
    except Exception as e:
        ok = False
        detail = str(e)[:120]
    return {**sys, "ok": ok, "detail": detail, "probed_at": time.time()}


def list_systems(*, live: bool = True) -> Dict[str, Any]:
    systems = [_probe_system(s) if live else dict(s) for s in SYSTEMS]
    ready = sum(1 for s in systems if s.get("ok"))
    return {
        "ok": True,
        "schema": "pocket.agent_os.v1",
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "tagline": TAGLINE,
        "systems": systems,
        "ready": ready,
        "total": len(systems),
        "parity": PARITY,
        "doctrine": (
            "Every agent system is a first-class screen or mode — "
            "native host depth beyond cloud agent desktops."
        ),
        "screens": {
            "os": "/os",
            "desk": "/desk",
            "work": "/work",
            "studio": "/studio",
            "phone": "/phone",
        },
    }


def parity_report() -> Dict[str, Any]:
    """Side-by-side: what POCKET does natively vs the 2026 class."""
    live = list_systems(live=True)
    rows = []
    for key, meta in PARITY.items():
        rows.append(
            {
                "competitor": meta["name"],
                "id": key,
                "pocket_native": meta["native"],
                "pocket_deeper": meta["deeper"],
                "systems_touching": [
                    s["id"]
                    for s in live["systems"]
                    if key in (s.get("parity") or [])
                ],
            }
        )
    return {
        "ok": True,
        "version": __version__,
        "rows": rows,
        "summary": (
            f"POCKET {__version__} covers Claude Code / Antigravity / Emergent / Replit "
            "workflows natively on-host with multi-engine bind, pixel artifacts, "
            "coding swarm, and capability sandbox."
        ),
        "systems_ready": f"{live['ready']}/{live['total']}",
    }


# ---------------------------------------------------------------------------
# Native projects (Replit-like, on disk)
# ---------------------------------------------------------------------------

def list_projects() -> Dict[str, Any]:
    items = []
    if PROJECTS.is_dir():
        for p in sorted(PROJECTS.iterdir(), key=lambda x: -x.stat().st_mtime):
            if not p.is_dir():
                continue
            meta_path = p / "pocket.project.json"
            meta = {}
            if meta_path.is_file():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    pass
            files = [f.name for f in p.iterdir() if f.is_file()][:40]
            items.append(
                {
                    "id": p.name,
                    "path": str(p),
                    "title": meta.get("title") or p.name,
                    "template": meta.get("template") or "blank",
                    "files": files,
                    "updated_at": p.stat().st_mtime,
                }
            )
    return {"ok": True, "projects": items, "root": str(PROJECTS)}


def create_project(
    name: str = "",
    *,
    template: str = "typescript",
    title: str = "",
    seed: str = "",
) -> Dict[str, Any]:
    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", (name or title or f"proj-{uuid.uuid4().hex[:8]}").lower())
    slug = slug.strip("-")[:48] or f"proj-{uuid.uuid4().hex[:8]}"
    path = PROJECTS / slug
    if path.exists():
        return {"ok": False, "error": "project exists", "id": slug, "path": str(path)}
    path.mkdir(parents=True, exist_ok=True)
    tpl = (template or "typescript").lower()
    files_written = []
    if tpl in ("ts", "typescript"):
        body = seed.strip() or (
            "// POCKET native project\n"
            "export function main(): string {\n"
            "  return 'hello from pocket agent os';\n"
            "}\n"
            "console.log(main());\n"
        )
        (path / "index.ts").write_text(body, encoding="utf-8")
        files_written.append("index.ts")
        (path / "package.json").write_text(
            json.dumps({"name": slug, "private": True, "type": "module"}, indent=2),
            encoding="utf-8",
        )
        files_written.append("package.json")
    elif tpl in ("py", "python"):
        body = seed.strip() or 'print("hello from pocket agent os")\n'
        (path / "main.py").write_text(body, encoding="utf-8")
        files_written.append("main.py")
    elif tpl in ("js", "javascript"):
        body = seed.strip() or 'console.log("hello from pocket agent os");\n'
        (path / "index.js").write_text(body, encoding="utf-8")
        files_written.append("index.js")
    else:
        (path / "README.md").write_text(f"# {title or slug}\n\nPOCKET native project.\n", encoding="utf-8")
        files_written.append("README.md")
        if seed.strip():
            (path / "main.txt").write_text(seed, encoding="utf-8")
            files_written.append("main.txt")

    meta = {
        "id": slug,
        "title": title or slug,
        "template": tpl,
        "created_at": time.time(),
        "version": __version__,
        "files": files_written,
    }
    (path / "pocket.project.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    _timeline("project.create", {"id": slug, "template": tpl})
    # Also land seed in pixel memory
    try:
        from pocket.pixel_vmem import put_artifact

        put_artifact(
            seed or json.dumps(meta, indent=2),
            title=f"project-{slug}",
            language="json" if not seed else tpl,
            agent="agent_os",
            agent_role="Native Projects",
            ai_version="agent_os",
            run_id=slug,
            tags=["project", "agent_os", tpl],
            note=f"project {slug}",
        )
    except Exception:
        pass
    return {"ok": True, "project": meta, "path": str(path)}


def get_project(project_id: str) -> Dict[str, Any]:
    path = PROJECTS / re.sub(r"[^a-zA-Z0-9_\-]+", "", project_id or "")
    if not path.is_dir():
        return {"ok": False, "error": "not found"}
    files = []
    for f in sorted(path.iterdir()):
        if f.is_file() and f.name != "pocket.project.json":
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                text = ""
            files.append({"name": f.name, "bytes": f.stat().st_size, "preview": text[:400], "text": text[:20000]})
    meta = {}
    mp = path / "pocket.project.json"
    if mp.is_file():
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"ok": True, "id": path.name, "path": str(path), "meta": meta, "files": files}


def write_project_file(project_id: str, filename: str, content: str) -> Dict[str, Any]:
    path = PROJECTS / re.sub(r"[^a-zA-Z0-9_\-]+", "", project_id or "")
    if not path.is_dir():
        return {"ok": False, "error": "project not found"}
    name = Path(filename or "file.txt").name
    if name in (".", "..") or "/" in name or "\\" in name:
        return {"ok": False, "error": "bad filename"}
    fp = path / name
    fp.write_text(content or "", encoding="utf-8")
    _timeline("project.write", {"id": path.name, "file": name})
    return {"ok": True, "path": str(fp), "bytes": fp.stat().st_size}


def run_project(project_id: str, *, entry: str = "", timeout: float = 20) -> Dict[str, Any]:
    """Run a native project entry (py / js / ts / sh) sandboxed by time + cwd."""
    path = PROJECTS / re.sub(r"[^a-zA-Z0-9_\-]+", "", project_id or "")
    if not path.is_dir():
        return {"ok": False, "error": "project not found"}
    entry_name = entry
    if not entry_name:
        for cand in ("main.py", "index.ts", "index.js", "main.js", "run.sh"):
            if (path / cand).is_file():
                entry_name = cand
                break
    if not entry_name or not (path / entry_name).is_file():
        return {"ok": False, "error": "no entry file"}
    return run_code_file(path / entry_name, cwd=path, timeout=timeout)


def run_code_file(file_path: Path, *, cwd: Optional[Path] = None, timeout: float = 20) -> Dict[str, Any]:
    """Execute one file with host tools — deeper than cloud preview sandboxes for local work."""
    fp = Path(file_path)
    if not fp.is_file():
        return {"ok": False, "error": "file missing"}
    suf = fp.suffix.lower()
    work = str(cwd or fp.parent)
    cmd: List[str]
    if suf == ".py":
        cmd = [os.environ.get("PYTHON", "python"), str(fp)]
    elif suf in (".js", ".mjs", ".cjs"):
        node = shutil.which("node")
        if not node:
            return {"ok": False, "error": "node not found"}
        cmd = [node, str(fp)]
    elif suf in (".ts", ".tsx"):
        # Prefer tsx/ts-node; else strip-run via node --experimental if available
        tsx = shutil.which("tsx") or shutil.which("ts-node")
        node = shutil.which("node")
        if tsx:
            cmd = [tsx, str(fp)]
        elif node:
            # transpile-free: run as JS if pure enough, else error with install hint
            cmd = [node, "--experimental-strip-types", str(fp)]
        else:
            return {"ok": False, "error": "node/tsx not found for TypeScript"}
    elif suf in (".sh", ".bash"):
        shell = shutil.which("bash") or shutil.which("sh")
        if not shell:
            return {"ok": False, "error": "bash not found"}
        cmd = [shell, str(fp)]
    else:
        return {"ok": False, "error": f"unsupported extension {suf}"}

    try:
        p = subprocess.run(
            cmd,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=max(2.0, min(float(timeout), 60.0)),
            env={**os.environ, "POCKET_AGENT_OS": "1"},
        )
        out = (p.stdout or "")[-20000:]
        err = (p.stderr or "")[-8000:]
        rec = {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "stdout": out,
            "stderr": err,
            "cmd": cmd,
            "cwd": work,
            "file": str(fp),
            "at": time.time(),
        }
        run_id = uuid.uuid4().hex[:12]
        (RUNS / f"{run_id}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
        _timeline("run", {"run_id": run_id, "file": str(fp), "rc": p.returncode})
        # Pixel artifact of run output
        try:
            from pocket.pixel_vmem import put_artifact

            put_artifact(
                f"# Run {run_id}\n\n```\n{out or err}\n```\n",
                title=f"run-{fp.name}-{run_id}",
                language="md",
                agent="agent_os",
                agent_role="Native Run",
                ai_version="agent_os",
                run_id=run_id,
                tags=["run", "agent_os"],
                note=f"rc={p.returncode}",
            )
        except Exception:
            pass
        rec["run_id"] = run_id
        return rec
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "file": str(fp)}
    except Exception as e:
        return {"ok": False, "error": str(e), "file": str(fp)}


def run_artifact_symbol(symbol: str, *, timeout: float = 20) -> Dict[str, Any]:
    """Recreate a pixel code artifact to a temp project file and run it."""
    from pocket.pixel_vmem import get_symbol, recreate

    g = get_symbol(symbol)
    if not g.get("ok"):
        return g
    text = g.get("text") or ""
    # peel fences
    m = re.search(r"```([a-zA-Z0-9_+#.\-]*)\n([\s\S]*?)```", text)
    lang, code = "txt", text
    if m:
        lang = (m.group(1) or "txt").lower()
        code = m.group(2)
    ext = {
        "typescript": ".ts",
        "ts": ".ts",
        "javascript": ".js",
        "js": ".js",
        "python": ".py",
        "py": ".py",
        "bash": ".sh",
        "sh": ".sh",
    }.get(lang, ".txt")
    run_dir = RUNS / f"art-{uuid.uuid4().hex[:10]}"
    run_dir.mkdir(parents=True, exist_ok=True)
    fp = run_dir / f"main{ext}"
    fp.write_text(code, encoding="utf-8")
    if ext == ".txt":
        return {
            "ok": True,
            "skipped": True,
            "reason": "not executable language",
            "path": str(fp),
            "preview": code[:500],
        }
    return run_code_file(fp, cwd=run_dir, timeout=timeout)


def import_artifact_to_project(symbol: str, project_id: str = "", filename: str = "") -> Dict[str, Any]:
    from pocket.pixel_vmem import get_symbol

    g = get_symbol(symbol)
    if not g.get("ok"):
        return g
    text = g.get("text") or ""
    m = re.search(r"```([a-zA-Z0-9_+#.\-]*)\n([\s\S]*?)```", text)
    lang, code = "md", text
    if m:
        lang = (m.group(1) or "md").lower()
        code = m.group(2)
    if not project_id:
        pr = create_project(
            name=f"from-{(symbol or 'art')[-20:]}",
            template="typescript" if lang in ("ts", "typescript") else (
                "python" if lang in ("py", "python") else "blank"
            ),
            title=f"Import {symbol}",
            seed=code if lang not in ("md", "text", "") else "",
        )
        if not pr.get("ok"):
            return pr
        project_id = pr["project"]["id"]
        if lang in ("md", "text", "") and code:
            write_project_file(project_id, filename or "imported.md", code)
        return {"ok": True, "project_id": project_id, "imported": True, "symbol": symbol}
    ext = { "typescript": "ts", "ts": "ts", "python": "py", "py": "py", "javascript": "js", "js": "js" }.get(lang, "txt")
    fn = filename or f"imported.{ext}"
    return write_project_file(project_id, fn, code)


def _timeline(kind: str, payload: Dict[str, Any]) -> None:
    try:
        with _lock:
            with TIMELINE.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"at": time.time(), "kind": kind, **payload}, default=str) + "\n")
    except Exception:
        pass


def timeline(limit: int = 40) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    if TIMELINE.is_file():
        try:
            lines = TIMELINE.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines[-max(1, min(limit, 200)) :]:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
        except Exception:
            pass
    rows.reverse()
    return {"ok": True, "events": rows, "count": len(rows)}


def dashboard() -> Dict[str, Any]:
    """Single first-class dashboard payload for /os screen + API."""
    systems = list_systems(live=True)
    projects = list_projects()
    try:
        from pocket.pixel_vmem import list_artifacts, status as vmem_status

        arts = list_artifacts(limit=12)
        vmem = vmem_status()
    except Exception as e:
        arts = {"ok": False, "error": str(e), "artifacts": []}
        vmem = {}
    try:
        from pocket.coding_swarm import list_roster

        roster = list_roster()
    except Exception:
        roster = {"agents": []}
    try:
        from pocket.executor import available_engines

        engines = available_engines()
    except Exception:
        engines = {}
    try:
        from pocket.first_class_agents import build_registry, desk_catalog, ensure_modes_aligned

        ensure_modes_aligned()
        fc = build_registry(live=False)
        catalog = desk_catalog()
    except Exception:
        fc = {"count": 0, "agents": [], "by_group": {}}
        catalog = {"groups": [], "count": 0}
    return {
        "ok": True,
        "schema": "pocket.agent_os.dashboard.v1",
        "version": __version__,
        "product": PRODUCT,
        "tagline": TAGLINE,
        "systems": systems,
        "parity": parity_report(),
        "projects": projects,
        "artifacts": arts,
        "pixel": vmem,
        "swarm_roster": roster,
        "first_class_agents": {
            "count": fc.get("count"),
            "by_group": fc.get("by_group"),
            "catalog_count": catalog.get("count"),
            "harness_parents": fc.get("harness_parents"),
        },
        "engines": {
            "codex": engines.get("codex"),
            "grok": engines.get("grok"),
            "claude": engines.get("claude"),
            "claude_agent_sdk": engines.get("claude_agent_sdk"),
        },
        "timeline": timeline(20),
        "open": {
            "desk": "/desk",
            "os": "/os",
            "work": "/work",
            "studio": "/studio",
            "phone": "/phone",
        },
    }
