"""MCP apps inside PhoneAI — each embedded MCP is a phone app, not a browser tab."""

from __future__ import annotations

from typing import Any, Dict, List

ICONS = {
    "pocket": "⌂",
    "nexus": "✦",
    "loom": "◎",
    "github": "⌥",
    "filesystem": "📁",
    "universal": "50",
}

SAFE_EXACT = frozenset({
    "platform_map",
    "platform_health",
    "find_feature",
    "sovereign_stack",
    "list_skills",
    "tools_for_prompt",
    "agents_toolkit",
    "agents_tools",
    "tools_manifest",
    "agent_roster",
    "search",
    "read",
    "fs_list",
    "fs_stat",
    "fs_read",
    "repo_list",
    "pr_list",
    "issue_list",
    "webmcp_list",
    "webmcp_find",
    "python_engines_list",
    "engine_uses",
    "mcp_catalog",
    "studio_map",
    "studio_status",
    "studio_playbooks",
    "mail_inbox",
    "mail_accounts",
    "iot_list",
    "computing_clouds",
})

SAFE_SUFFIXES = (
    "_status",
    "_list",
    "_catalog",
    "_map",
    "_health",
    "_schema",
    "_roster",
    "_tools",
    "_modes",
)

BLOCK_PARTS = frozenset({
    "shell",
    "touch",
    "click",
    "type",
    "act",
    "install",
    "send",
    "write",
    "execute",
    "invoke",
    "dial",
    "hangup",
    "mint",
    "delete",
    "remove",
    "ensure",
    "open",
    "run",
    "use",
    "speak",
    "commit",
    "allocate",
    "terminate",
})


def icon_for(sid: str) -> str:
    sid = (sid or "").lower()
    if sid in ICONS:
        return ICONS[sid]
    if "cloudflare" in sid:
        return "☁"
    return "⬡"


def tool_is_safe(tool: str) -> bool:
    t = (tool or "").strip().lower()
    if not t or t == "*":
        return False
    if t in SAFE_EXACT:
        return True
    parts = set(t.replace("-", "_").split("_"))
    if parts & BLOCK_PARTS:
        return False
    return t.endswith(SAFE_SUFFIXES)


def phone_apps() -> Dict[str, Any]:
    from pocket.mcp_bundle import catalog

    cat = catalog()
    apps: List[Dict[str, Any]] = []
    for s in cat.get("servers") or []:
        sid = str(s.get("id") or "")
        tools = [str(t) for t in (s.get("tools") or []) if t and t != "*"]
        safe = [t for t in tools if tool_is_safe(t)]
        apps.append({
            "id": sid,
            "name": s.get("name") or sid,
            "kind": s.get("kind") or "external",
            "blurb": s.get("blurb") or "",
            "transport": s.get("transport") or "",
            "icon": icon_for(sid),
            "url": f"/phoneai/mcp#{sid}",
            "tools": tools[:80],
            "safe_tools": safe[:40],
            "tool_count": len(tools),
        })
    return {
        "ok": True,
        "schema": "pocket.phoneai.mcp_apps.v1",
        "count": len(apps),
        "apps": apps,
        "doctrine": "MCP apps live inside PhoneAI. Catalog is public to the paired seat. Invoke stays read-safe on the phone.",
        "docs": "/docs/view/how-to/PHONEAI_MCP",
        "paper": "/docs/view/research/PHONEAI_MCP_APPS_PAPER",
    }


def safe_invoke(server: str, tool: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    tool = (tool or "").strip()
    if not tool_is_safe(tool):
        return {
            "ok": False,
            "error": "this tool is not a PhoneAI MCP app action — owner desk only",
            "tool": tool,
            "server": server,
        }
    from pocket.mcp_bundle import invoke

    return invoke(server or "pocket", tool, **(params or {}))


def mcp_apps_html() -> str:
    return PHONEAI_MCP_HTML


PHONEAI_MCP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<meta name="apple-mobile-web-app-title" content="MCP"/>
<title>MCP apps · PhoneAI</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86;--p:#14141c;--c:#58a6ff}
*{box-sizing:border-box}
html,body{margin:0;min-height:100dvh;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:430px;margin:0 auto;padding:calc(12px + env(safe-area-inset-top)) 16px calc(88px + env(safe-area-inset-bottom))}
.bar{display:flex;justify-content:space-between;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font-size:26px;letter-spacing:-.04em;margin:10px 0 6px}
.lead{color:var(--muted);font-size:14px;line-height:1.45;margin:0 0 14px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 8px}
.app{display:flex;flex-direction:column;align-items:center;gap:6px;background:none;border:0;color:inherit;font:inherit;padding:0}
.icon{width:56px;height:56px;border-radius:16px;display:grid;place-items:center;font-size:22px;border:1px solid var(--line);background:linear-gradient(160deg,rgba(255,255,255,.1),rgba(255,255,255,.02))}
.app span{font-size:11px;color:var(--muted);text-align:center}
.back{border:1px solid var(--line);background:var(--p);color:var(--fg);border-radius:999px;padding:8px 12px;font-size:12px}
.item{padding:12px;border-bottom:1px solid var(--line)}
.item b{display:block}
.item small{color:var(--muted)}
.go{border:0;border-radius:10px;background:var(--g);color:#042;font-weight:800;padding:8px 12px;margin-top:8px}
pre{white-space:pre-wrap;word-break:break-word;background:#0c0c0e;border:1px solid var(--line);border-radius:12px;padding:10px;font-size:12px;max-height:240px;overflow:auto}
.more{color:var(--muted);font-size:12px;margin-top:16px}
a{color:var(--c)}
.dock{position:fixed;left:14px;right:14px;bottom:calc(6px + env(safe-area-inset-bottom));display:flex;justify-content:space-around;padding:10px;border-radius:22px;background:rgba(18,18,24,.92);border:1px solid var(--line)}
.dock a{color:var(--muted);text-decoration:none;font-size:11px;font-weight:800}
</style>
</head>
<body>
<div class="bar"><span>PHONEAI</span><span>MCP APPS</span></div>
<div id="home">
  <h1>MCP apps</h1>
  <p class="lead">Each MCP on this host is an app on the phone. Tools run on the PC. Random visitors never see this folder.</p>
  <div class="grid" id="grid"></div>
  <p class="more"><a href="/docs/view/how-to/PHONEAI_MCP">How-to</a> · <a href="/docs/view/research/PHONEAI_MCP_APPS_PAPER">White paper</a> · <a href="/docs">Docs hub</a></p>
</div>
<div id="srv" style="display:none">
  <button class="back" type="button" id="back">← Apps</button>
  <h1 id="sn">Server</h1>
  <p class="lead" id="sb"></p>
  <div id="tools"></div>
  <pre id="out" hidden></pre>
</div>
<nav class="dock">
  <a href="/phoneai/app">Home</a>
  <a href="/phoneai/mcp">MCP</a>
  <a href="/phoneai/portal">PC</a>
  <a href="/docs">Docs</a>
</nav>
<script>
const grid=document.getElementById('grid');
const home=document.getElementById('home');
const srv=document.getElementById('srv');
const out=document.getElementById('out');
let APPS=[];
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function paintHome(){
  home.style.display='block'; srv.style.display='none';
  grid.innerHTML=APPS.map(a=>'<button class="app" data-id="'+esc(a.id)+'"><div class="icon">'+esc(a.icon)+'</div><span>'+esc(a.name)+'</span></button>').join('')
    || '<p class="lead">No MCP servers on this host.</p>';
}
function openSrv(id){
  const a=APPS.find(x=>x.id===id); if(!a) return;
  home.style.display='none'; srv.style.display='block';
  document.getElementById('sn').textContent=a.name;
  document.getElementById('sb').textContent=(a.kind||'')+' · '+(a.blurb||'')+' · '+(a.tool_count||0)+' tools';
  const tools=a.safe_tools&&a.safe_tools.length?a.safe_tools:a.tools||[];
  document.getElementById('tools').innerHTML=tools.map(t=>'<div class="item"><b>'+esc(t)+'</b><small>runs on this PC</small><div><button class="go" type="button" data-run="'+esc(t)+'">Open</button></div></div>').join('')
    || '<div class="item">No phone-safe tools on this server.</div>';
  out.hidden=true; location.hash=id;
}
grid.addEventListener('click',e=>{ const b=e.target.closest('[data-id]'); if(b) openSrv(b.getAttribute('data-id')); });
document.getElementById('back').onclick=()=>{ location.hash=''; paintHome(); };
document.getElementById('tools').addEventListener('click', async e=>{
  const b=e.target.closest('[data-run]'); if(!b) return;
  const id=(location.hash||'').replace('#','');
  out.hidden=false; out.textContent='running '+b.getAttribute('data-run')+'…';
  try{
    const r=await fetch('/v1/phoneai/mcp/invoke',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({server:id,tool:b.getAttribute('data-run')})});
    const j=await r.json();
    out.textContent=JSON.stringify(j,null,2).slice(0,8000);
  }catch(err){ out.textContent=String(err); }
});
fetch('/v1/phoneai/mcp',{credentials:'include'}).then(r=>r.json()).then(j=>{
  APPS=j.apps||[];
  paintHome();
  const h=(location.hash||'').replace('#','');
  if(h) openSrv(h);
}).catch(()=>{ grid.innerHTML='<p class="lead">Sign in + Face ID to open MCP apps.</p>'; });
</script>
</body></html>
"""
