"""Unified POCKET / PhoneAI registry — apps, MCP, systems, docs, papers, tech.

Live: GET /v1/registry
Phone: /phoneai/registry
File: docs/whitepapers/POCKET_FULL_REGISTRY.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pocket import COMPANY, LAB, PRODUCT, __version__

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

KERNEL_APPS: List[Dict[str, str]] = [
    {"id": "chat", "name": "Chat", "url": "/phoneai/app#chat", "icon": "💬", "group": "life"},
    {"id": "camera", "name": "Camera", "url": "/phoneai/app#camera", "icon": "📷", "group": "life"},
    {"id": "photos", "name": "Photos", "url": "/phoneai/app#photos", "icon": "🖼", "group": "life"},
    {"id": "maps", "name": "Maps", "url": "/phoneai/app#maps", "icon": "🗺", "group": "life"},
    {"id": "notes", "name": "Notes", "url": "/phoneai/app#notes", "icon": "📝", "group": "life"},
    {"id": "remind", "name": "Remind", "url": "/phoneai/app#remind", "icon": "⏰", "group": "life"},
    {"id": "list", "name": "List", "url": "/phoneai/app#list", "icon": "☑", "group": "life"},
    {"id": "voice", "name": "Voice", "url": "/studio/voice", "icon": "🎙", "group": "studio"},
    {"id": "imagine", "name": "Imagine", "url": "/imagine", "icon": "✨", "group": "studio"},
    {"id": "work", "name": "Code desk", "url": "/phoneai/work", "icon": "✦", "group": "work"},
    {"id": "anti", "name": "Anti", "url": "/phoneai/anti", "icon": "🪐", "group": "stream"},
    {"id": "portal", "name": "Portal", "url": "/phoneai/portal", "icon": "🖥", "group": "stream"},
    {"id": "computer", "name": "Computer", "url": "/phoneai/computer", "icon": "💻", "group": "stream"},
    {"id": "glasses", "name": "Glasses", "url": "/phoneai/glasses", "icon": "👓", "group": "wear"},
    {"id": "airpods", "name": "AirPods", "url": "/phoneai/airpods", "icon": "🎧", "group": "wear"},
    {"id": "web", "name": "Web live", "url": "/phoneai/web", "icon": "🌐", "group": "stream"},
    {"id": "mcp", "name": "MCP", "url": "/phoneai/app#mcp", "icon": "⬡", "group": "mcp"},
    {"id": "mcp-apps", "name": "MCP apps", "url": "/phoneai/mcp", "icon": "⌂", "group": "mcp"},
    {"id": "registry", "name": "Registry", "url": "/phoneai/registry", "icon": "▣", "group": "docs"},
    {"id": "docs", "name": "Docs", "url": "/docs", "icon": "📄", "group": "docs"},
    {"id": "runtime", "name": "Runtime", "url": "/phoneai/runtime", "icon": "⏻", "group": "host"},
    {"id": "agents", "name": "Agents", "url": "/agents", "icon": "🙂", "group": "agents"},
    {"id": "tv", "name": "TV node", "url": "/phoneai/tv", "icon": "📺", "group": "home"},
    {"id": "doorbell", "name": "Doorbell", "url": "/phoneai/doorbell", "icon": "🔔", "group": "home"},
    {"id": "cam", "name": "PC cam", "url": "/phoneai/cam", "icon": "💻", "group": "home"},
    {"id": "claims", "name": "Claims", "url": "/claims", "icon": "®", "group": "legal"},
    {"id": "pair", "name": "Pair", "url": "/phoneai/pair", "icon": "🔗", "group": "auth"},
    {"id": "settings", "name": "Settings", "url": "/phoneai/app#settings", "icon": "⚙", "group": "host"},
]


def _docs_root() -> Path:
    return DOCS if DOCS.is_dir() else Path(__file__).resolve().parents[2] / "docs"


def _title_from_md(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
            s = line.strip()
            if s.startswith("# "):
                return s[2:].strip()
    except Exception:
        pass
    return path.stem.replace("_", " ")


def _scan_docs() -> Dict[str, List[Dict[str, str]]]:
    root = _docs_root()
    how: List[Dict[str, str]] = []
    papers: List[Dict[str, str]] = []
    white: List[Dict[str, str]] = []
    other: List[Dict[str, str]] = []
    if not root.is_dir():
        return {"how_tos": how, "papers": papers, "whitepapers": white, "docs": other}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".md", ".json"):
            continue
        rel = p.relative_to(root).as_posix()
        rec = {
            "id": rel.rsplit(".", 1)[0].replace("/", "."),
            "name": _title_from_md(p) if p.suffix.lower() == ".md" else p.stem,
            "path": "docs/" + rel,
            "url": "/docs/view/" + rel.rsplit(".", 1)[0],
        }
        if rel.startswith("how-to/"):
            how.append(rec)
        elif rel.startswith("research/"):
            papers.append(rec)
        elif rel.startswith("whitepapers/"):
            white.append(rec)
        elif p.suffix.lower() == ".md":
            other.append(rec)
    return {"how_tos": how, "papers": papers, "whitepapers": white, "docs": other}


def _tech() -> List[Dict[str, Any]]:
    fp = _docs_root() / "whitepapers" / "TECHNOLOGY_REGISTRY.json"
    if not fp.is_file():
        return []
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return list(data.get("technologies") or [])
    except Exception:
        return []


def snapshot(*, write: bool = False) -> Dict[str, Any]:
    """One registry for PhoneAI apps, MCP servers, systems, docs, and papers."""
    docs = _scan_docs()
    mcp_apps: List[Dict[str, Any]] = []
    try:
        from pocket.phoneai_mcp import phone_apps

        mcp_apps = phone_apps().get("apps") or []
    except Exception:
        pass
    systems: List[Dict[str, Any]] = []
    try:
        from pocket.platform_catalog import systems as plat_systems

        systems = plat_systems()
    except Exception:
        pass
    surfaces: List[Dict[str, str]] = []
    try:
        from pocket.tech_atlas import APPS

        surfaces = list(APPS)
    except Exception:
        pass
    agents_n = 0
    try:
        from pocket.first_class_agents import build_registry

        agents_n = int(build_registry(live=False).get("count") or 0)
    except Exception:
        pass
    skills_n = 0
    try:
        from pocket.platform_coherence import PLATFORM_SKILLS

        skills_n = len(PLATFORM_SKILLS)
    except Exception:
        pass
    tech = _tech()
    entries: List[Dict[str, Any]] = []
    for a in KERNEL_APPS:
        entries.append({**a, "kind": "phoneai-app"})
    for a in mcp_apps:
        entries.append({
            "id": "mcp." + str(a.get("id")),
            "name": a.get("name"),
            "url": a.get("url"),
            "icon": a.get("icon"),
            "kind": "mcp-app",
            "group": "mcp",
            "blurb": a.get("blurb"),
            "tool_count": a.get("tool_count"),
        })
    for s in systems:
        entries.append({
            "id": "sys." + str(s.get("id")),
            "name": s.get("name"),
            "url": s.get("where") if str(s.get("where") or "").startswith("/") else "/docs",
            "kind": "system",
            "group": "platform",
            "how_to": s.get("how_to"),
            "for": s.get("for"),
        })
    for bucket, kind in (
        ("how_tos", "how-to"),
        ("papers", "paper"),
        ("whitepapers", "whitepaper"),
        ("docs", "doc"),
    ):
        for d in docs[bucket]:
            entries.append({**d, "kind": kind, "group": "docs"})
    for t in tech:
        entries.append({
            "id": "tech." + str(t.get("id")),
            "name": t.get("name") or t.get("id"),
            "kind": "technology",
            "group": "tech",
            "status": t.get("status"),
            "description": t.get("description"),
        })

    counts = {
        "phoneai_apps": len(KERNEL_APPS),
        "mcp_apps": len(mcp_apps),
        "systems": len(systems),
        "how_tos": len(docs["how_tos"]),
        "papers": len(docs["papers"]),
        "whitepapers": len(docs["whitepapers"]),
        "docs": len(docs["docs"]),
        "technologies": len(tech),
        "surfaces": len(surfaces),
        "agents": agents_n,
        "skills": skills_n,
        "entries": len(entries),
    }
    out = {
        "ok": True,
        "schema": "pocket.full_registry.v1",
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "company": COMPANY,
        "doctrine": (
            "One registry for everything on this host: PhoneAI kernel apps, MCP servers as phone apps, "
            "platform systems, how-tos, research papers, white papers, and named technologies."
        ),
        "urls": {
            "json": "/v1/registry",
            "phone": "/phoneai/registry",
            "docs": "/docs/view/whitepapers/POCKET_FULL_REGISTRY",
            "mcp": "/phoneai/mcp",
            "kernel": "/phoneai/app",
        },
        "counts": counts,
        "phoneai_apps": KERNEL_APPS,
        "mcp_apps": mcp_apps,
        "systems": systems,
        "surfaces": surfaces,
        "how_tos": docs["how_tos"],
        "papers": docs["papers"],
        "whitepapers": docs["whitepapers"],
        "docs": docs["docs"],
        "technologies": tech,
        "entries": entries,
    }
    if write:
        write_snapshot(out)
    return out


def write_snapshot(data: Dict[str, Any] | None = None) -> Path:
    data = data or snapshot(write=False)
    slim = {k: data[k] for k in data if k != "entries"}
    slim["entry_count"] = len(data.get("entries") or [])
    dest = _docs_root() / "whitepapers" / "POCKET_FULL_REGISTRY.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(slim, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def registry_html() -> str:
    return REGISTRY_HTML


REGISTRY_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<title>Registry · PhoneAI</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86;--p:#14141c;--c:#58a6ff}
*{box-sizing:border-box}
html,body{margin:0;min-height:100dvh;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:480px;margin:0 auto;padding:calc(12px + env(safe-area-inset-top)) 16px calc(88px + env(safe-area-inset-bottom))}
.bar{display:flex;justify-content:space-between;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font-size:26px;letter-spacing:-.04em;margin:10px 0 6px}
.lead{color:var(--muted);font-size:14px;line-height:1.45}
.tabs{display:flex;gap:6px;overflow:auto;padding:10px 0 14px}
.tabs button{flex:0 0 auto;border:1px solid var(--line);background:var(--p);color:var(--fg);border-radius:999px;padding:8px 12px;font-size:12px}
.tabs button.on{background:var(--g);color:#042;border-color:var(--g)}
.item{display:block;padding:12px 0;border-bottom:1px solid var(--line);color:inherit;text-decoration:none}
.item b{display:block}
.item small{color:var(--muted)}
.counts{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 4px}
.counts i{font-style:normal;font-size:11px;border:1px solid var(--line);border-radius:999px;padding:4px 8px;color:var(--muted)}
a{color:var(--c)}
.dock{position:fixed;left:14px;right:14px;bottom:calc(6px + env(safe-area-inset-bottom));display:flex;justify-content:space-around;padding:10px;border-radius:22px;background:rgba(18,18,24,.92);border:1px solid var(--line)}
.dock a{color:var(--muted);text-decoration:none;font-size:11px;font-weight:800}
</style>
</head>
<body>
<div class="bar"><span>PHONEAI</span><span>REGISTRY</span></div>
<h1>Everything on this host</h1>
<p class="lead">Kernel apps, MCP servers, systems, how-tos, white papers. One list.</p>
<div class="counts" id="counts"></div>
<div class="tabs" id="tabs"></div>
<div id="list"></div>
<p class="lead" style="margin-top:16px"><a href="/v1/registry">JSON</a> · <a href="/docs">Docs hub</a> · <a href="/phoneai/mcp">MCP apps</a></p>
<nav class="dock">
  <a href="/phoneai/app">Home</a>
  <a href="/phoneai/mcp">MCP</a>
  <a href="/phoneai/registry">Registry</a>
  <a href="/docs">Docs</a>
</nav>
<script>
const TABS=[
  ['phoneai-app','Apps'],
  ['mcp-app','MCP'],
  ['system','Systems'],
  ['how-to','How-to'],
  ['paper','Papers'],
  ['whitepaper','White papers'],
  ['technology','Tech'],
  ['doc','Docs']
];
let DATA={entries:[]};
let KIND='phoneai-app';
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function paint(){
  const tabs=document.getElementById('tabs');
  tabs.innerHTML=TABS.map(([id,label])=>'<button type="button" data-k="'+id+'" class="'+(id===KIND?'on':'')+'">'+label+'</button>').join('');
  const items=(DATA.entries||[]).filter(e=>e.kind===KIND);
  document.getElementById('list').innerHTML=items.map(e=>{
    const href=e.url||('#');
    const sub=e.blurb||e.for||e.description||e.path||e.group||'';
    return '<a class="item" href="'+esc(href)+'"><b>'+esc(e.icon?e.icon+' ':'')+esc(e.name||e.id)+'</b><small>'+esc(sub)+'</small></a>';
  }).join('') || '<p class="lead">Empty in this lane.</p>';
}
document.getElementById('tabs').onclick=e=>{ const b=e.target.closest('[data-k]'); if(!b) return; KIND=b.getAttribute('data-k'); paint(); };
fetch('/v1/registry',{credentials:'include'}).then(r=>r.json()).then(j=>{
  DATA=j;
  const c=j.counts||{};
  document.getElementById('counts').innerHTML=Object.keys(c).map(k=>'<i>'+k.replace(/_/g,' ')+' '+c[k]+'</i>').join('');
  paint();
}).catch(()=>{ document.getElementById('list').innerHTML='<p class="lead">Sign in + Face ID to load the live registry.</p>'; });
</script>
</body></html>
"""
