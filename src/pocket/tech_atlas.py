"""Walk POCKET family repos and apps and list the technology in use."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ONEDRIVE = Path.home() / "OneDrive"

TREES: List[Dict[str, str]] = [
    {"id": "pocket", "name": "POCKET host", "path": str(ONEDRIVE / "pocket-os"), "kind": "host"},
    {"id": "pocket-agent", "name": "POCKET Agent", "path": str(ONEDRIVE / "pocket-agent"), "kind": "cli"},
    {"id": "pocket-voice", "name": "POCKET Voice", "path": str(ONEDRIVE / "pocket-voice-to-text"), "kind": "voice"},
    {"id": "pocket-app", "name": "POCKET App hub", "path": str(ONEDRIVE / "pocket-app"), "kind": "docs"},
    {"id": "pocket-phone-agent", "name": "POCKET Phone Agent", "path": str(ONEDRIVE / "pocket-phone-agent"), "kind": "phone"},
    {"id": "phoneai", "name": "PhoneAI kernel OS", "path": str(ONEDRIVE / "PhoneAI"), "kind": "phone-os"},
]

# Surfaces the companion can open / explain
APPS: List[Dict[str, str]] = [
    {"id": "desk", "name": "Desk", "url": "/desk", "role": "Coding + agents"},
    {"id": "phone", "name": "POCKET Phone", "url": "/phone", "role": "Mobile web seat"},
    {"id": "phoneai", "name": "PhoneAI Kernel", "url": "/phoneai/app", "role": "Native phone OS surface"},
    {"id": "phoneai-mcp", "name": "MCP apps", "url": "/phoneai/mcp", "role": "Embedded MCP servers as phone apps"},
    {"id": "registry", "name": "Registry", "url": "/registry", "role": "Every app, MCP, doc, and paper"},
    {"id": "docs", "name": "Docs + papers", "url": "/docs", "role": "How-to and white papers"},
    {"id": "imagine", "name": "Imagine Studio", "url": "/imagine", "role": "Stills / remakes"},
    {"id": "voice", "name": "Voice Studio", "url": "/studio/voice", "role": "Aria STT/TTS"},
    {"id": "work", "name": "Work Studio", "url": "/work", "role": "Life assistant"},
    {"id": "mail", "name": "Agent Mail", "url": "/mail", "role": "Agent inboxes"},
    {"id": "lab", "name": "Lab", "url": "/lab", "role": "Readiness map"},
    {"id": "ecosystem", "name": "Ecosystem", "url": "/ecosystem", "role": "Repo family"},
    {"id": "login", "name": "Sign in", "url": "/login", "role": "GitHub + seats"},
    {"id": "developers", "name": "Developers", "url": "/developers", "role": "API keys"},
    {"id": "forge", "name": "Forge", "url": "/forge", "role": "Sovereign git"},
]


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _scan_tree(root: Path) -> Dict[str, Any]:
    tech: List[str] = []
    langs: List[str] = []
    if (root / "pyproject.toml").is_file() or (root / "src").is_dir() or (root / "backend").is_dir():
        langs.append("Python")
        tech.append("Python 3.11+")
    if (root / "package.json").is_file():
        langs.append("JavaScript/TypeScript")
        pkg = _read_json(root / "package.json") or {}
        deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
        for name, label in (
            ("expo", "Expo / React Native"),
            ("react-native", "React Native"),
            ("react", "React"),
            ("fastapi", "FastAPI"),
            ("electron", "Electron"),
            ("wrangler", "Cloudflare Workers"),
        ):
            if name in deps:
                tech.append(label)
    if (root / "frontend" / "package.json").is_file():
        langs.append("TypeScript")
        pkg = _read_json(root / "frontend" / "package.json") or {}
        deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
        if "expo" in deps:
            tech.append("Expo")
        if "react-native" in deps:
            tech.append("React Native")
        if "expo-router" in deps:
            tech.append("Expo Router")
    if (root / "backend").is_dir():
        req = root / "backend" / "requirements.txt"
        if req.is_file():
            body = req.read_text(encoding="utf-8", errors="replace").lower()
            if "fastapi" in body:
                tech.append("FastAPI")
            if "motor" in body or "mongo" in body:
                tech.append("MongoDB")
            if "uvicorn" in body:
                tech.append("Uvicorn")
    if (root / "desktop-electron").is_dir():
        tech.append("Electron desktop")
    if (root / "cloudflare").is_dir():
        tech.append("Cloudflare")
    if (root / "src" / "pocket").is_dir():
        tech.extend(
            [
                "Threading HTTP host :8787",
                "MCP tools",
                "Agent Mail",
                "Novae (Grok/Codex)",
                "WASM capsules",
            ]
        )
    # Motoko / ICP
    if (root / "src").is_dir() and any(root.joinpath("src").glob("*.mo")):
        langs.append("Motoko")
        tech.append("Internet Computer")
    # de-dupe preserve order
    seen = set()
    tech_u = []
    for t in tech:
        if t not in seen:
            seen.add(t)
            tech_u.append(t)
    langs_u = []
    seen.clear()
    for t in langs:
        if t not in seen:
            seen.add(t)
            langs_u.append(t)
    return {"languages": langs_u, "technology": tech_u, "on_disk": True}


def catalog() -> Dict[str, Any]:
    products = []
    for row in TREES:
        p = Path(row["path"])
        item = dict(row)
        if p.exists():
            item.update(_scan_tree(p))
        else:
            item["on_disk"] = False
            item["languages"] = []
            item["technology"] = []
        products.append(item)
    stack = [
        {"layer": "Kernel / host", "items": ["POCKET :8787", "PhoneAI substrate", "pocket-phone-agent :8795"]},
        {"layer": "Models / CLIs", "items": ["Grok", "Codex", "Claude Code", "Gemini API + CLI", "Qwen", "Auro (internal)"]},
        {"layer": "Agents", "items": ["POCKET Live companion", "Novae", "Digital assistant", "Coding swarm", "RAH"]},
        {"layer": "Phone", "items": ["PhoneAI Kernel OS (Expo)", "POCKET Phone PWA", "Phone Agent SDK"]},
        {"layer": "Voice", "items": ["pocket-voice-to-text", "Aria", "Gemini voice brain"]},
        {"layer": "Desktop", "items": ["Electron POCKET", "Edge app mode"]},
        {"layer": "Cloud", "items": ["Cloudflare tunnel / Pages", "Named tunnel pocket.medinatechlabs.net"]},
        {"layer": "Protocols", "items": ["MCP", "NEXUS receipts", "Agent Mail", "WASM capsules"]},
    ]
    return {
        "ok": True,
        "product": "POCKET × PhoneAI kernel OS",
        "apps": APPS,
        "products": products,
        "stack": stack,
        "companion": {
            "name": "POCKET Live",
            "job": "Work, explain, help, and use the platform from a floating chat.",
            "engine": "gemini",
            "fallback": "local atlas",
        },
    }


def compact_context(limit: int = 3500) -> str:
    data = catalog()
    lines = ["POCKET technology atlas", ""]
    lines.append("Apps:")
    for a in data["apps"]:
        lines.append(f"- {a['name']} {a['url']} — {a['role']}")
    lines.append("")
    lines.append("Repos:")
    for p in data["products"]:
        langs = ", ".join(p.get("languages") or []) or "?"
        tech = ", ".join((p.get("technology") or [])[:8])
        lines.append(f"- {p['name']} ({p['id']}) langs={langs} tech={tech}")
    lines.append("")
    for layer in data["stack"]:
        lines.append(f"{layer['layer']}: " + ", ".join(layer["items"]))
    text = "\n".join(lines)
    return text[:limit]


def tech_html() -> str:
    data = catalog()
    cards = []
    for p in data["products"]:
        langs = ", ".join(p.get("languages") or []) or "—"
        tech = "".join(f"<li>{t}</li>" for t in (p.get("technology") or [])[:12]) or "<li>not cloned</li>"
        disk = "on this PC" if p.get("on_disk") else "missing"
        cards.append(
            f"<article class='card'><div class='k'>{p['kind']}</div><h2>{p['name']}</h2>"
            f"<p>{langs} · {disk}</p><ul>{tech}</ul></article>"
        )
    apps = "".join(
        f"<a class='app' href='{a['url']}'><b>{a['name']}</b><span>{a['role']}</span></a>"
        for a in data["apps"]
    )
    stack = "".join(
        f"<tr><th>{s['layer']}</th><td>{', '.join(s['items'])}</td></tr>" for s in data["stack"]
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET technology</title>
<style>
:root{{--bg:#07070b;--fg:#fafafa;--muted:#a1a1aa;--line:rgba(255,255,255,.1);--accent:#10a37f}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:#07070b;color:#e4e4e7}}
.wrap{{max-width:980px;margin:0 auto;padding:28px 18px 88px}}
h1{{color:var(--fg);letter-spacing:-.04em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}
.card{{border:1px solid var(--line);border-radius:14px;padding:14px;background:#121218}}
.k{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#34d399;font-weight:800}}
ul{{color:var(--muted);padding-left:18px;font-size:13px}}
.apps{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 28px}}
.app{{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;padding:10px 12px;color:#fff;text-decoration:none;min-width:140px;background:#121218}}
.app span{{color:var(--muted);font-size:12px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;color:#34d399;padding:8px 8px 8px 0;width:28%}}
td{{color:var(--muted);padding:8px 0;border-bottom:1px solid var(--line)}}
a{{color:var(--accent)}}
</style></head>
<body><div class="wrap">
<p><a href="/ecosystem">Ecosystem</a> · <a href="/phoneai">PhoneAI Kernel</a> · <a href="/desk">Desk</a></p>
<h1>All technology</h1>
<p>Repos, apps, and the stack the floating POCKET Live agent can explain and use.</p>
<div class="apps">{apps}</div>
<div class="grid">{''.join(cards)}</div>
<h2>Stack</h2>
<table>{stack}</table>
</div></body></html>
"""
