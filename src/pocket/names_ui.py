"""Pocket Names — me.me style handles on roots you operate."""

from pocket.names import ZONES


def names_html() -> str:
    opts = "".join(f'<option value="{z}">{z}</option>' for z in ZONES)
    return HTML.replace("__ZONES__", opts)


HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Pocket Names</title>
<style>
:root{--bg:#08080c;--fg:#f4f4f5;--muted:#a1a1aa;--line:rgba(255,255,255,.12);--g:#22d3ee}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:640px;margin:0 auto;padding:28px 18px 64px}
a{color:var(--muted)}
h1{letter-spacing:-.04em;margin:8px 0}
.muted{color:var(--muted);line-height:1.5}
form{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}
input,select,button{border-radius:12px;border:1px solid var(--line);background:#111;color:#fff;padding:10px 12px;font:inherit}
button{background:var(--g);color:#041016;font-weight:800;border:0}
#out{white-space:pre-wrap;font-size:13px;color:var(--muted)}
</style></head>
<body>
<div style="font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--g);font-weight:800">Pocket Names</div>
<h1>you.toolbox</h1>
<p class="muted">Like me.me — you own the root. People claim a handle. They do not buy a domain. Zones you operate: toolbox, toolset, aiapps, pocketweb.</p>
<p class="muted">Public internet later: one parent you control (Cloudflare or Handshake). Until then Pocket issues the name.</p>
<form id="f">
  <input id="n" placeholder="you" autocomplete="off"/>
  <select id="z">__ZONES__</select>
  <button>Claim</button>
</form>
<pre id="out"></pre>
<p><a href="/desk">Desk</a> · <a href="/webgpu">IOChain WebGPU</a> · <a href="/loomgraph">LOOMGRAPH</a></p>
<script>
const out=document.getElementById('out');
fetch('/v1/names',{credentials:'include'}).then(r=>r.json()).then(j=>{
  out.textContent=(j.model||'')+'\n'+JSON.stringify(j.counts||{},null,2);
});
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault();
  const name=document.getElementById('n').value.trim();
  const zone=document.getElementById('z').value;
  const j=await fetch('/v1/names/claim',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,zone})}).then(r=>r.json());
  out.textContent=j.ok?('claimed '+j.claimed.fqdn): (j.error||JSON.stringify(j));
};
</script>
</body></html>
"""
