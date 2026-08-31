"""POCKET as a network ecosystem + agent develop/ship studios.

Nodes (host, phone, PhoneAI, MCP, mesh, public URL, desktop) plus two
studios: Develop (scaffold/test) and Ship (package to git/mesh/phone/desktop).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "network"
AGENTS_FILE = ROOT / "agents.json"


def _load() -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    if AGENTS_FILE.is_file():
        try:
            data = json.loads(AGENTS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("agents", [])
                return data
        except Exception:
            pass
    return {"agents": [], "updated": time.time()}


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    data["updated"] = time.time()
    AGENTS_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def nodes() -> List[Dict[str, Any]]:
    lan = ""
    try:
        from pocket.live import lan_ip

        lan = lan_ip() or ""
    except Exception:
        pass
    host = "http://127.0.0.1:8787"
    phone = f"http://{lan}:8787" if lan else host
    return [
        {"id": "host", "kind": "runtime", "name": "POCKET host", "url": host, "role": "Desk, API, MCP, auth"},
        {"id": "public", "kind": "edge", "name": "Public network", "url": "https://pocket.medinatechlabs.net", "role": "Signup, desk, PhoneAI PWA"},
        {"id": "phoneai", "kind": "phone", "name": "PhoneAI kernel", "url": f"{phone}/phoneai", "role": "Talk + control any app from the phone"},
        {"id": "desk", "kind": "studio", "name": "Desk", "url": f"{host}/desk", "role": "Live Grok / Codex / agents"},
        {"id": "develop", "kind": "studio", "name": "Agent Develop Studio", "url": f"{host}/studio/agents", "role": "Scaffold, test, skills, MCP tools"},
        {"id": "ship", "kind": "studio", "name": "Agent Ship Studio", "url": f"{host}/studio/ship", "role": "Package to git, mesh, phone, desktop"},
        {"id": "mcp", "kind": "protocol", "name": "MCP + WebMCP", "url": f"{host}/webmcp", "role": "Every action on pages and apps"},
        {"id": "mesh", "kind": "fabric", "name": "Mesh / mini-git", "url": f"{host}/forge", "role": "Sovereign git vault + E: mesh disk"},
        {"id": "imagine", "kind": "studio", "name": "Imagine Studio", "url": f"{host}/imagine", "role": "Stills and fusion remake"},
        {"id": "voice", "kind": "studio", "name": "Voice Studio", "url": f"{host}/studio/voice", "role": "STT / TTS / Aria"},
        {"id": "work", "kind": "studio", "name": "Work Studio", "url": f"{host}/work", "role": "Loops, swarm, dual-loop design"},
        {"id": "product", "kind": "studio", "name": "Product Studio", "url": f"{host}/studio", "role": "Recordings → demos → ship"},
        {"id": "desktop", "kind": "runtime", "name": "Desktop app", "url": f"{host}/download", "role": "Electron / Edge packaged host"},
    ]


def studios() -> List[Dict[str, Any]]:
    return [
        {
            "id": "develop",
            "name": "Agent Develop",
            "path": "/studio/agents",
            "api": ["GET /v1/network", "POST /v1/network/agents", "POST /v1/network/agents/run"],
            "job": "Create agents with a role, tools, and a test prompt. Run once on the host.",
        },
        {
            "id": "ship",
            "name": "Agent Ship",
            "path": "/studio/ship",
            "api": ["POST /v1/network/agents/ship"],
            "job": "Package an agent to sovereign git, mesh disk, PhoneAI seat, or desktop checklist.",
        },
        {
            "id": "product",
            "name": "Product Studio",
            "path": "/studio",
            "api": ["POST /v1/studio/ship"],
            "job": "Turn recordings into phone/web demos.",
        },
        {
            "id": "work",
            "name": "Work Studio",
            "path": "/work",
            "api": ["GET /v1/work-studio"],
            "job": "Design how agents work: types, loops, swarm.",
        },
    ]


def list_catalog_agents() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        from pocket.first_class_agents import build_registry

        pack = build_registry(live=False)
        rows = pack.get("agents") or pack.get("items") or []
        if isinstance(rows, dict):
            rows = list(rows.values())
        for a in rows[:80]:
            if isinstance(a, dict) and a.get("id"):
                out.append(
                    {
                        "id": a.get("id"),
                        "name": a.get("name") or a.get("id"),
                        "role": a.get("role") or a.get("blurb") or "",
                        "source": "first_class",
                        "group": a.get("group") or "",
                    }
                )
    except Exception:
        pass
    try:
        from pocket.ship_agents import list_ship_agents

        for a in list_ship_agents():
            out.append({**a, "source": a.get("source") or "ship"})
    except Exception:
        pass
    seen = set()
    uniq = []
    for a in out:
        i = str(a.get("id") or "")
        if not i or i in seen:
            continue
        seen.add(i)
        uniq.append(a)
    return uniq


def list_developed() -> List[Dict[str, Any]]:
    return list(_load().get("agents") or [])


def develop(body: Dict[str, Any]) -> Dict[str, Any]:
    aid = "".join(ch for ch in str(body.get("id") or body.get("name") or "").lower() if ch.isalnum() or ch in "-_")[:40]
    if len(aid) < 2:
        return {"ok": False, "error": "agent id required (letters, numbers, - _)"}
    rec = {
        "id": aid,
        "name": str(body.get("name") or aid)[:60],
        "role": str(body.get("role") or "worker")[:120],
        "blurb": str(body.get("blurb") or body.get("prompt") or "")[:800],
        "tools": body.get("tools") if isinstance(body.get("tools"), list) else ["webmcp", "git", "desk"],
        "engine": str(body.get("engine") or "grok")[:32],
        "targets": body.get("targets") if isinstance(body.get("targets"), list) else ["desk", "phoneai"],
        "created": time.time(),
        "status": "developed",
        "shipped": [],
    }
    data = _load()
    agents = [a for a in data.get("agents") or [] if a.get("id") != aid]
    agents.insert(0, rec)
    data["agents"] = agents[:80]
    _save(data)
    try:
        from pocket.phoneai_space import dual_write

        dual_write(
            f"agents/{aid}.md",
            f"# {rec['name']}\n\nrole: {rec['role']}\nengine: {rec['engine']}\n\n{rec['blurb']}\n",
            message=f"develop {aid}",
        )
    except Exception:
        pass
    return {"ok": True, "agent": rec, "studio": "develop"}


def run_developed(aid: str, prompt: str = "") -> Dict[str, Any]:
    rec = next((a for a in list_developed() if a.get("id") == aid), None)
    if not rec:
        return {"ok": False, "error": f"unknown developed agent {aid}"}
    text = (prompt or rec.get("blurb") or rec.get("role") or aid).strip()
    try:
        from pocket.phoneai_bridge import ask_engine

        r = ask_engine(text, engine=str(rec.get("engine") or "grok"))
        rec["last_run"] = {"ok": r.get("ok"), "at": time.time(), "engine": r.get("engine")}
        data = _load()
        data["agents"] = [rec if a.get("id") == aid else a for a in data.get("agents") or []]
        _save(data)
        return {"ok": bool(r.get("ok")), "agent": rec, "result": r, "studio": "develop"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "agent": rec}


def ship(aid: str, target: str = "git") -> Dict[str, Any]:
    rec = next((a for a in list_developed() if a.get("id") == aid), None)
    if not rec:
        return {"ok": False, "error": f"unknown developed agent {aid}"}
    t = (target or "git").lower()
    artifact = {
        "id": aid,
        "target": t,
        "at": time.time(),
        "name": rec.get("name"),
        "role": rec.get("role"),
    }
    if t in ("git", "mesh", "phone", "phoneai"):
        try:
            from pocket.phoneai_space import dual_write

            dual_write(
                f"ship/{aid}-{t}.md",
                json.dumps(rec, indent=2, default=str),
                message=f"ship {aid} → {t}",
            )
            artifact["via"] = "phoneai-desk git + explorer"
        except Exception as e:
            artifact["error"] = str(e)[:160]
    if t in ("mesh", "desktop"):
        try:
            from pocket.ship_agents import run_ship_agent

            run_ship_agent("ELECTRON" if t == "desktop" else "MARKETING", prompt=f"ship agent {aid}: {rec.get('role')}")
            artifact["via_ship_pack"] = True
        except Exception:
            try:
                from pocket.mesh_disk import leave_artifact

                leave_artifact("SHIP", f"agent-{aid}.md", json.dumps(rec, indent=2, default=str)[:4000])
                artifact["via"] = "mesh disk"
            except Exception as e:
                artifact["mesh_error"] = str(e)[:120]
    rec.setdefault("shipped", []).insert(0, artifact)
    rec["status"] = "shipped"
    data = _load()
    data["agents"] = [rec if a.get("id") == aid else a for a in data.get("agents") or []]
    _save(data)
    return {"ok": True, "agent": rec, "ship": artifact, "studio": "ship"}


def snapshot() -> Dict[str, Any]:
    return {
        "ok": True,
        "product": "POCKET Network",
        "promise": "Whole-network ecosystem and full develop + ship studios for agents.",
        "nodes": nodes(),
        "studios": studios(),
        "developed": list_developed(),
        "catalog": list_catalog_agents()[:40],
        "phoneai": "http://127.0.0.1:8787/phoneai",
        "public": "https://pocket.medinatechlabs.net/",
    }


def html() -> str:
    data = snapshot()
    node_cards = "".join(
        f'<a class="card" href="{n["url"]}"><div class="k">{n["kind"]}</div><h3>{n["name"]}</h3><p>{n["role"]}</p></a>'
        for n in data["nodes"]
    )
    studio_cards = "".join(
        f'<a class="card" href="{s["path"]}"><div class="k">studio</div><h3>{s["name"]}</h3><p>{s["job"]}</p></a>'
        for s in data["studios"]
    )
    developed = data.get("developed") or []
    rows = "".join(
        f'<div class="item"><b>{a.get("name")}</b> <code>{a.get("id")}</code><small>{a.get("role")} · {a.get("status")} · {a.get("engine")}</small></div>'
        for a in developed[:20]
    ) or '<div class="item">No custom agents yet — develop one below.</div>'
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Network · Agent studios</title>
<style>
:root{{--bg:#07070b;--fg:#fafafa;--muted:#a1a1aa;--line:rgba(255,255,255,.1);--g:#10a37f;--p:#121218}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0 -10%,rgba(16,163,127,.14),transparent 50%),var(--bg);color:#e4e4e7}}
.wrap{{max-width:980px;margin:0 auto;padding:28px 16px 80px}}
h1{{letter-spacing:-.04em;margin:8px 0}}
.lead{{color:var(--muted);max-width:40rem;line-height:1.5}}
nav a{{color:var(--g);margin-right:12px;font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:16px 0 28px}}
.card{{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--p)}}
.k{{font-size:10px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#34d399}}
h3{{margin:6px 0;color:var(--fg);font-size:16px}}
p{{margin:0;color:var(--muted);font-size:13px;line-height:1.45}}
.item{{padding:10px 0;border-bottom:1px solid var(--line)}}
.item small{{display:block;color:var(--muted);margin-top:4px}}
form{{display:grid;gap:8px;max-width:520px;margin:12px 0 24px}}
input,textarea,select{{background:#0c0c0e;border:1px solid var(--line);border-radius:10px;color:#fff;padding:10px;font:inherit}}
button{{border:0;border-radius:10px;background:var(--g);color:#042;font-weight:800;padding:10px 14px}}
code{{color:#86efac}}
</style></head>
<body><div class="wrap">
<nav><a href="/">Home</a><a href="/ecosystem">Family</a><a href="/desk">Desk</a><a href="/phoneai">PhoneAI</a><a href="/studio/agents">Develop</a><a href="/studio/ship">Ship</a></nav>
<p class="k">POCKET NETWORK</p>
<h1>Whole-network ecosystem for agents</h1>
<p class="lead">One host, many doors: desk, PhoneAI, public URL, MCP, mesh, desktop. Develop an agent here, test it, then ship it to git, the mesh, the phone seat, or the desktop pack.</p>
<h2>Studios</h2>
<div class="grid">{studio_cards}</div>
<h2>Network nodes</h2>
<div class="grid">{node_cards}</div>
<h2>Developed agents</h2>
{rows}
<h2>New agent</h2>
<form id="f">
<input name="id" placeholder="id (e.g. night-watch)" required/>
<input name="name" placeholder="display name"/>
<input name="role" placeholder="role (reviewer, shipper, researcher…)"/>
<textarea name="blurb" rows="3" placeholder="What it does in one paragraph"></textarea>
<select name="engine"><option value="grok">Grok</option><option value="codex">Codex</option><option value="claude">Claude</option><option value="spectral-agi">Spectral AGI</option></select>
<button type="submit">Develop</button>
</form>
<p class="lead">Then Ship: <code>POST /v1/network/agents/ship</code> with <code>{{"id":"night-watch","target":"git"}}</code> — targets: git · mesh · phoneai · desktop.</p>
<script>
document.getElementById('f').onsubmit=async ev=>{{
  ev.preventDefault();
  const fd=new FormData(ev.target);
  const body=Object.fromEntries(fd.entries());
  const r=await fetch('/v1/network/agents',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
  const j=await r.json();
  alert(j.ok ? ('Developed '+j.agent.id) : (j.error||'failed'));
  if(j.ok) location.reload();
}};
</script>
</div></body></html>
"""


def ship_html() -> str:
    data = snapshot()
    items = "".join(
        f'<div class="item"><b>{a.get("name")}</b> <code>{a.get("id")}</code>'
        f'<div class="row">'
        f'<button data-id="{a.get("id")}" data-t="git">Git</button>'
        f'<button data-id="{a.get("id")}" data-t="mesh">Mesh</button>'
        f'<button data-id="{a.get("id")}" data-t="phoneai">PhoneAI</button>'
        f'<button data-id="{a.get("id")}" data-t="desktop">Desktop</button>'
        f'<button data-id="{a.get("id")}" data-run="1">Test run</button>'
        f'</div></div>'
        for a in (data.get("developed") or [])
    ) or '<div class="item">Develop an agent first at <a href="/studio/agents">/studio/agents</a>.</div>'
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Ship Studio · POCKET</title>
<style>
:root{{--bg:#07070b;--fg:#fafafa;--muted:#a1a1aa;--line:rgba(255,255,255,.1);--g:#10a37f}}
body{{margin:0;font-family:ui-sans-serif,system-ui;background:var(--bg);color:#e4e4e7}}
.wrap{{max-width:720px;margin:0 auto;padding:28px 16px}}
a{{color:var(--g)}}
.item{{padding:14px 0;border-bottom:1px solid var(--line)}}
.row{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
button{{border:0;border-radius:10px;background:#1c1c24;color:#fff;padding:8px 12px;font-weight:700}}
h1{{letter-spacing:-.04em}}
.lead{{color:var(--muted)}}
</style></head>
<body><div class="wrap">
<p><a href="/network">Network</a> · <a href="/studio/agents">Develop</a> · <a href="/desk">Desk</a></p>
<h1>Agent Ship Studio</h1>
<p class="lead">Package a developed agent onto sovereign git, the mesh disk, the PhoneAI seat, or the desktop ship pack.</p>
{items}
<script>
document.body.addEventListener('click', async e=>{{
  const b=e.target.closest('button[data-id]'); if(!b) return;
  const id=b.getAttribute('data-id');
  if(b.hasAttribute('data-run')){{
    const j=await fetch('/v1/network/agents/run',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{id}})}}).then(r=>r.json());
    alert(j.ok ? ((j.result&&j.result.reply)||'ran') : (j.error||'fail'));
    return;
  }}
  const j=await fetch('/v1/network/agents/ship',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{id,target:b.getAttribute('data-t')}})}}).then(r=>r.json());
  alert(j.ok ? ('Shipped '+id+' → '+b.getAttribute('data-t')) : (j.error||'fail'));
}});
</script>
</div></body></html>
"""
