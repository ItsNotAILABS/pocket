"""POCKET + PhoneAI actual setup — account, host, always-on, open."""

from __future__ import annotations

from pocket import COMPANY, LAB, __version__
from pocket.host_runtime import ROOT, urls


def setup_html() -> str:
    u = urls()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Setup POCKET + PhoneAI</title>
<meta name="description" content="Install the host, keep it always on, create a seat, open the desk or PhoneAI."/>
<meta name="theme-color" content="#09090b"/>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--fg:#fafafa;--muted:#a1a1aa;--accent:#10a37f;--g:#00ff86}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0% 0%,rgba(16,163,127,.12),transparent 50%),var(--bg);color:var(--fg);line-height:1.5}}
a{{color:var(--accent);text-decoration:none}}
.wrap{{max-width:760px;margin:0 auto;padding:36px 20px 80px}}
.kicker{{font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}}
h1{{letter-spacing:-.04em;font-size:clamp(28px,5vw,40px);margin:8px 0 10px}}
.lead{{color:var(--muted);max-width:40em}}
.step{{border:1px solid var(--line);border-radius:16px;padding:20px;background:var(--panel);margin:14px 0}}
.step h2{{margin:0 0 8px;font-size:17px}}
.step p,.step pre{{margin:0 0 10px;color:var(--muted);font-size:14px}}
pre{{background:#0c0c0e;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;color:#d1fae5;font-size:12.5px}}
.btn{{display:inline-flex;align-items:center;padding:11px 16px;border-radius:10px;font-weight:700;font-size:13.5px;border:0;margin:4px 8px 0 0;cursor:pointer}}
.pri{{background:var(--accent);color:#041}}
.ghost{{background:transparent;color:var(--fg);border:1px solid var(--line)}}
.ok{{color:var(--accent);font-weight:700}}
.bad{{color:#fca5a5;font-weight:700}}
.urls a{{display:inline-block;margin:4px 12px 4px 0}}
.foot{{margin-top:28px;color:var(--muted);font-size:12px}}
</style>
</head>
<body>
<main class="wrap">
  <div class="kicker">{LAB} · setup</div>
  <h1>Install POCKET and PhoneAI on this PC</h1>
  <p class="lead">One host. Two products. Pocket is the desk. PhoneAI is the phone kernel. The runtime watchdog keeps :8787 up so agents can bring the servers back themselves.</p>
  <p id="pulse">Checking host…</p>

  <div class="step" id="s1">
    <h2>1 · Create your seat</h2>
    <p>Public signup. PhoneAI uses its own seat. Desk uses yours. Never share the operator password.</p>
    <a class="btn pri" href="/signup">Sign up</a>
    <a class="btn ghost" href="/login">Sign in</a>
  </div>

  <div class="step" id="s2">
    <h2>2 · Bring the host up</h2>
    <p>If this page loaded, the host is answering. If it dies later, agents run <code>python -m pocket ensure</code> or POST <code>/v1/runtime/ensure</code>.</p>
    <pre>cd {ROOT}
set PYTHONPATH=src
python -m pocket ensure
python -m pocket install</pre>
    <button class="btn pri" id="ensure" type="button">Bring host up now</button>
    <button class="btn ghost" id="install" type="button">Install always-on</button>
    <p id="act"></p>
  </div>

  <div class="step" id="s3">
    <h2>3 · Keep it always on</h2>
    <p>Install writes a logon scheduled task and a Startup shortcut. Sleep still kills the host — keep the PC awake. Tunnel stays operator-owned.</p>
    <pre>python -m pocket install
# or
powershell -File scripts/Install-AlwaysOn.ps1</pre>
  </div>

  <div class="step" id="s4">
    <h2>4 · Open the products</h2>
    <p class="urls">
      <a href="/desk">POCKET desk</a>
      <a href="/phoneai">PhoneAI website</a>
      <a href="/phoneai/app">PhoneAI kernel</a>
      <a href="/phoneai/portal">Portal</a>
      <a href="/install">Install slices</a>
    </p>
  </div>

  <div class="step">
    <h2>Tunnel these URLs</h2>
    <p>Point your named tunnel at this host. Full PhoneAI intro:</p>
    <pre>{u["tunnel_phoneai"]}
{u["phoneai"]}

Setup: {u["tunnel_setup"]}
Sign up: {u["tunnel_signup"]}
Kernel: {u["public"].rstrip("/")}/phoneai/app</pre>
  </div>

  <p class="foot">{COMPANY} · v{__version__} · agents: runtime_status · runtime_ensure · runtime_install</p>
</main>
<script>
async function pulse(){{
  const el=document.getElementById('pulse');
  try{{
    const j=await fetch('/v1/runtime').then(r=>r.json());
    el.innerHTML = (j.up?'<span class="ok">Host is up.</span>':'<span class="bad">Host is down.</span>')
      + (j.always_on?' Always-on watchdog is running.':' Watchdog is not running — install always-on.');
  }}catch(_){{ el.innerHTML='<span class="bad">Cannot reach /v1/runtime.</span>'; }}
}}
pulse();
async function post(path, label){{
  const act=document.getElementById('act');
  act.textContent=label+'…';
  try{{
    const j=await fetch(path,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:'{{}}'}}).then(r=>r.json());
    act.textContent = (j.ok?'ok · ':'error · ')+JSON.stringify(j.notes||j.ensured||j.urls||j).slice(0,280);
  }}catch(e){{ act.textContent=String(e); }}
  pulse();
}}
document.getElementById('ensure').onclick=()=>post('/v1/runtime/ensure','Bringing up');
document.getElementById('install').onclick=()=>post('/v1/runtime/install','Installing');
</script>
</body>
</html>
"""
