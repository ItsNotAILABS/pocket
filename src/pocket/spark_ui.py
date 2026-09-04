"""Visible Spark chat — Reagent OpenAI-compatible qwen on this host."""


def spark_html() -> str:
    return HTML


HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Spark · POCKET</title>
<style>
:root{--bg:#07070b;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#a855f7}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{display:flex;flex-direction:column;max-width:720px;margin:0 auto}
a{color:var(--muted);text-decoration:none}
.top{padding:14px 16px;border-bottom:1px solid var(--line)}
.top b{display:block;font-size:18px}
.st{font-size:12px;color:var(--muted);margin-top:4px}
.log{flex:1;overflow:auto;padding:14px 16px}
.m{margin:0 0 12px;padding:10px 12px;border-radius:14px;background:#14141c;white-space:pre-wrap;line-height:1.45}
.m.me{background:#2e1064}
.form{display:flex;gap:8px;padding:12px 16px calc(12px + env(safe-area-inset-bottom));border-top:1px solid var(--line)}
textarea{flex:1;min-height:48px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:10px;font:inherit}
button{border:0;border-radius:12px;background:var(--g);color:#fff;font-weight:800;padding:0 16px}
</style></head>
<body>
<div class="top">
  <a href="/phoneai/app">Kernel</a> · <a href="/crew">Crew</a> · <a href="/desk">Desk</a>
  <b>Spark</b>
  <div class="st" id="st">Checking…</div>
</div>
<div class="log" id="log"></div>
<form class="form" id="f">
  <textarea id="t" placeholder="Spark writes files on this PC. Try: write hello.md in the pocket repo…" rows="1"></textarea>
  <button>Send</button>
</form>
<script>
const log=document.getElementById('log');
function add(who, text){
  const d=document.createElement('div'); d.className='m'+(who==='me'?' me':''); d.textContent=text; log.appendChild(d); log.scrollTop=log.scrollHeight;
}
fetch('/v1/spark',{credentials:'include'}).then(r=>r.json()).then(j=>{
  document.getElementById('st').textContent=(j.configured?'Ready · ':'NOT CONFIGURED · ')+(j.model||'')+' · '+(j.base_url||'');
  add('bot', j.configured?'Spark can write local files, git/GitHub, and the virtual computer. Ask it to create a file.':'Key missing in ~/.pocket/spark.json');
}).catch(()=>add('bot','Host not reachable'));
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault();
  const t=document.getElementById('t'); const text=(t.value||'').trim(); if(!text) return;
  t.value=''; add('me', text); add('bot','…');
  try{
    const j=await fetch('/v1/spark/chat',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})}).then(r=>r.json());
    const acts=(j.actions||[]).map(a=>a.tool+(a.path?(' '+a.path):'')).filter(Boolean);
    log.lastChild.textContent=(j.reply||j.error||JSON.stringify(j))+(acts.length?'\n\n[tools: '+acts.join(', ')+']':'');
  }catch(e){ log.lastChild.textContent='Spark request failed'; }
};
</script>
</body></html>
"""
