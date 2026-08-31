"""Canonical POCKET family map — product repos vs the rest of the lab.

Source of truth for /ecosystem and REPOS.md. Other ItsNotAILABS products stay
linked, not dumped into POCKET.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

ONEDRIVE = Path.home() / "OneDrive"

POCKET_REPOS: List[Dict[str, Any]] = [
    {
        "id": "pocket",
        "name": "pocket",
        "github": "https://github.com/ItsNotAILABS/pocket",
        "local": str(ONEDRIVE / "pocket-os"),
        "role": "Host runtime — desk, phone, MCP, auth, Electron, Imagine",
        "port": 8787,
        "layer": "host",
        "canonical": True,
    },
    {
        "id": "pocket-agent",
        "name": "pocket-agent",
        "github": "https://github.com/ItsNotAILABS/pocket-agent",
        "local": str(ONEDRIVE / "pocket-agent"),
        "role": "Public CLI + RLM harness + install slices (sdk, skills, capsules, mail)",
        "layer": "agent",
        "canonical": True,
    },
    {
        "id": "pocket-voice",
        "name": "pocket-voice-to-text",
        "github": "https://github.com/ItsNotAILABS/pocket-voice-to-text",
        "local": str(ONEDRIVE / "pocket-voice-to-text"),
        "role": "Sovereign STT / TTS / voice agents for POCKET fusion",
        "layer": "voice",
        "canonical": True,
    },
    {
        "id": "pocket-app",
        "name": "pocket-app",
        "github": "https://github.com/FreddyCreates/pocket-app",
        "org_mirror": "ItsNotAILABS (optional)",
        "local": str(ONEDRIVE / "pocket-app"),
        "role": "User hub docs + Edge / Electron / Phone doors",
        "layer": "app",
        "canonical": True,
    },
    {
        "id": "pocket-phone-agent",
        "name": "pocket-phone-agent",
        "github": "",
        "local": str(ONEDRIVE / "pocket-phone-agent"),
        "role": "Separate agentic phone app · host API · port 8795",
        "port": 8795,
        "layer": "phone",
        "canonical": True,
    },
    {
        "id": "phoneai",
        "name": "PhoneAI",
        "github": "https://github.com/ItsNotAILABS/PhoneAI",
        "local": str(ONEDRIVE / "PhoneAI"),
        "role": "Phone-native kernel OS — app grid, POCKET Live (Gemini), typed capabilities, NEXUS receipts",
        "port": 8000,
        "layer": "phone",
        "canonical": True,
    },
]

SIBLINGS: List[Dict[str, str]] = [
    {"name": "ResearchersHub", "github": "https://github.com/ItsNotAILABS/ResearchersHub", "role": "Research desk + skills — sibling, not POCKET"},
    {"name": "nexus", "github": "https://github.com/ItsNotAILABS/nexus", "role": "MERIDIAN MCP workers"},
    {"name": "Auro14B", "github": "https://github.com/ItsNotAILABS/Auro14B", "role": "Native model — used by POCKET, owned separately"},
    {"name": "AURO", "github": "https://github.com/ItsNotAILABS/AURO", "role": "Auro line"},
    {"name": "sovereign-forge-os", "github": "https://github.com/ItsNotAILABS/sovereign-forge-os", "role": "Forge OS — dashboard :8788, POCKET keeps :8787"},
    {"name": "MedinaMemorySystems", "github": "https://github.com/ItsNotAILABS/MedinaMemorySystems", "role": "Memory systems"},
    {"name": "NEUROSWARMAI", "github": "https://github.com/ItsNotAILABS/NEUROSWARMAI", "role": "Swarm — Chimeria / NOVA"},
    {"name": "CAPSULA", "github": "https://github.com/ItsNotAILABS/CAPSULA", "role": "Capsula builder"},
    {"name": "cloudcolony", "github": "https://github.com/ItsNotAILABS/cloudcolony", "role": "ICP bridge"},
    {"name": "MatDaemon", "github": "https://github.com/ItsNotAILABS/MatDaemon", "role": "Matrix daemon"},
]

RULES = [
    "POCKET product surface is the canonical family above (host, agent, voice, app, phone agent, PhoneAI).",
    "Operator source of truth on this PC is OneDrive/pocket-os (public GitHub name: pocket).",
    "Do not dump MESIE, Auro, NEXUS, career forks, or stale.mesie-career clones into POCKET.",
    "Stale mesie-career-*.stale.* repos on the org are leftovers — archive, do not treat as POCKET.",
    "Runtime state is ~/.pocket — never commit it.",
    "Owner desk is :8787. Users product is :8788. They do not share a login.",
]


def catalog() -> Dict[str, Any]:
    family = []
    for row in POCKET_REPOS:
        item = dict(row)
        local = Path(item.get("local") or "")
        item["on_disk"] = local.exists()
        family.append(item)
    return {
        "ok": True,
        "product": "POCKET",
        "org": "ItsNotAILABS",
        "family": family,
        "siblings": SIBLINGS,
        "rules": RULES,
        "urls": {
            "owner": "http://127.0.0.1:8787/",
            "login": "http://127.0.0.1:8787/login",
            "which": "http://127.0.0.1:8787/which",
            "ecosystem": "http://127.0.0.1:8787/ecosystem",
            "network": "http://127.0.0.1:8787/network",
            "develop": "http://127.0.0.1:8787/studio/agents",
            "ship": "http://127.0.0.1:8787/studio/ship",
            "public": "https://pocket.medinatechlabs.net/",
        },
    }


def ecosystem_html() -> str:
    data = catalog()
    cards = []
    for r in data["family"]:
        gh = f'<a href="{r["github"]}">{r["github"].replace("https://github.com/","")}</a>' if r.get("github") else "<span>local only</span>"
        disk = "on this PC" if r.get("on_disk") else "not cloned here"
        port = f'<div class="meta">port {r["port"]}</div>' if r.get("port") else ""
        cards.append(
            f'<article class="card"><div class="k">{r["layer"]}</div><h2>{r["name"]}</h2>'
            f'<p>{r["role"]}</p>{port}<div class="meta">{gh} · {disk}</div>'
            f'<div class="path">{r.get("local") or ""}</div></article>'
        )
    sibs = "".join(
        f'<li><a href="{s["github"]}">{s["name"]}</a> — {s["role"]}</li>' for s in data["siblings"]
    )
    rules = "".join(f"<li>{x}</li>" for x in RULES)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET ecosystem</title>
<style>
:root{{--bg:#07070b;--fg:#fafafa;--muted:#a1a1aa;--line:rgba(255,255,255,.1);--accent:#10a37f}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 10% -10%,rgba(16,163,127,.12),transparent 50%),var(--bg);color:#e4e4e7}}
.wrap{{max-width:980px;margin:0 auto;padding:36px 20px 80px}}
h1{{color:var(--fg);letter-spacing:-.04em;margin:0 0 8px}}
.lead{{color:var(--muted);max-width:640px;line-height:1.55}}
nav a{{color:var(--accent);margin-right:12px;font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:22px 0}}
.card{{border:1px solid var(--line);border-radius:14px;padding:16px;background:#121218}}
.k{{font-size:10px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#34d399}}
h2{{margin:6px 0;color:var(--fg);font-size:1.1rem}}
p{{margin:0 0 8px;color:var(--muted);font-size:14px;line-height:1.45}}
.meta,.path{{font-size:12px;color:var(--muted)}}
.path{{word-break:break-all;margin-top:6px}}
a{{color:var(--accent)}}
ul{{color:var(--muted);line-height:1.55}}
</style></head>
<body><div class="wrap">
<nav><a href="/">Home</a><a href="/network">Network</a><a href="/studio/agents">Develop</a><a href="/studio/ship">Ship</a><a href="/which">Which POCKET</a><a href="/login">Sign in</a><a href="/desk">Desk</a></nav>
<h1>POCKET ecosystem</h1>
<p class="lead">Canonical family plus a whole-network layer: develop agents, ship them to git / mesh / PhoneAI / desktop. Siblings stay linked, not mixed in.</p>
<div class="grid">{''.join(cards)}</div>
<h2>Keep separate</h2>
<ul>{sibs}</ul>
<h2>Rules</h2>
<ul>{rules}</ul>
</div></body></html>
"""
