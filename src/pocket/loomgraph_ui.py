"""POCKET LOOMGRAPH UI — readable graphs + run loop for humans."""

from __future__ import annotations


def loomgraph_html() -> str:
    return HTML


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · LOOMGRAPH</title>
<script src="/auth/client.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root{
  --bg:#07070b;--panel:#12121a;--line:rgba(255,255,255,.08);--text:#f4f4f5;--muted:#a1a1aa;
  --accent:#34d399;--violet:#a78bfa;--blue:#60a5fa;--font:ui-sans-serif,system-ui,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font);background:
  radial-gradient(800px 400px at 0% 0%,rgba(52,211,153,.12),transparent 50%),
  radial-gradient(700px 400px at 100% 0%,rgba(167,139,250,.1),transparent 45%),
  var(--bg);color:var(--text);min-height:100vh}
.pnav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 16px;border-bottom:1px solid var(--line);background:rgba(0,0,0,.55);backdrop-filter:blur(12px);position:sticky;top:0;z-index:20}
.pnav a{color:#a1a1aa;text-decoration:none;font-size:13px;padding:7px 11px;border-radius:8px}
.pnav a:hover,.pnav a.on{color:#fff;background:#1a1a22}
.brand{font-weight:800;letter-spacing:-.03em;display:flex;gap:8px;align-items:center;margin-right:8px;color:#fff;text-decoration:none}
.brand i{width:26px;height:26px;border-radius:8px;background:linear-gradient(145deg,#34d399,#10a37f);display:grid;place-items:center;font-style:normal;color:#042;font-size:12px}
.sp{flex:1}
main{display:grid;grid-template-columns:280px 1fr 320px;gap:0;max-width:1400px;margin:0 auto;min-height:calc(100vh - 54px)}
@media(max-width:1000px){main{grid-template-columns:1fr}}
aside,section{padding:16px;border-right:1px solid var(--line);min-height:0}
aside:last-child{border-right:0;border-left:1px solid var(--line)}
h1{margin:0 0 6px;font-size:22px;letter-spacing:-.04em}
.tag{font-size:11px;color:var(--muted);line-height:1.45}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:10px}
.card h3{margin:0 0 8px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.gbtn{display:block;width:100%;text-align:left;padding:10px;border-radius:12px;border:1px solid transparent;background:transparent;color:inherit;cursor:pointer;margin-bottom:4px}
.gbtn:hover,.gbtn.on{border-color:rgba(52,211,153,.35);background:rgba(52,211,153,.08)}
.gbtn b{display:block;font-size:13px}
.gbtn small{color:var(--muted);font-size:11px}
textarea{width:100%;min-height:90px;border-radius:12px;border:1px solid var(--line);background:#0a0a0e;color:var(--text);padding:10px;font:inherit;resize:vertical}
.btn{border:0;border-radius:12px;padding:11px 14px;font-weight:700;cursor:pointer;font-size:13px}
.btn.primary{background:linear-gradient(180deg,#34d399,#10a37f);color:#042f1a;width:100%;margin-top:8px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text);width:100%;margin-top:6px}
#mermaid{background:#0c0c12;border:1px solid var(--line);border-radius:14px;padding:16px;overflow:auto;min-height:280px}
#log{font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;max-height:220px;overflow:auto;background:#050508;border-radius:10px;padding:10px;border:1px solid var(--line);color:#86efac}
.path{font-size:13px;color:var(--accent);font-weight:650;margin:8px 0}
.step{font-size:12px;padding:6px 0;border-bottom:1px solid var(--line);color:var(--muted)}
.step b{color:var(--text)}
.ok{color:#86efac}.bad{color:#fca5a5}
.pill{font-size:11px;border:1px solid var(--line);padding:4px 10px;border-radius:999px;color:var(--muted)}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/desk"><i>L</i>LOOMGRAPH</a>
  <a href="/desk">Desk</a>
  <a class="on" href="/loomgraph">LOOMGRAPH</a>
  <a href="/studio/create">Creative</a>
  <a href="/community">Community</a>
  <a href="/studio">Studio</a>
  <div class="sp"></div>
  <span class="pill" id="proto">POCKET-LOOMGRAPH/1.0</span>
</header>
<main>
  <aside>
    <div class="card">
      <h3>Playbook graphs</h3>
      <div id="graphs">Loading…</div>
    </div>
    <div class="card">
      <h3>Doctrine</h3>
      <div class="tag">Graphs for understanding<br/>Loops for completion<br/>Pocket for execution<br/>Receipts for truth</div>
    </div>
  </aside>
  <section>
    <h1>See the graph. Run the loop.</h1>
    <p class="tag" id="blurb">POCKET LOOMGRAPH — default multi-step harness for agents and you.</p>
    <div class="card">
      <h3>Goal</h3>
      <textarea id="goal" placeholder="e.g. write social pack for LOOMGRAPH and storyboard a demo"></textarea>
      <button class="btn primary" type="button" id="runBtn" onclick="runGraph()">Run LOOMGRAPH</button>
      <button class="btn ghost" type="button" onclick="loadMermaid()">Refresh graph view</button>
    </div>
    <div class="card">
      <h3>Graph</h3>
      <div id="mermaid">…</div>
    </div>
  </section>
  <aside>
    <div class="card">
      <h3>Path</h3>
      <div class="path" id="path">—</div>
      <div id="steps"></div>
    </div>
    <div class="card">
      <h3>Receipt</h3>
      <div id="log">Ready.</div>
    </div>
  </aside>
</main>
<script>
mermaid.initialize({startOnLoad:false, theme:'dark', securityLevel:'loose'});
const auth={
  user:sessionStorage.getItem('pocket_user')||localStorage.getItem('pocket_user')||'',
  pass:sessionStorage.getItem('pocket_pass')||localStorage.getItem('pocket_pass')||'',
  token:sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'',
};
let graphId='default';
let catalog=null;

function headers(){
  const h={'Content-Type':'application/json'};
  if(auth.token) h.Authorization='Bearer '+auth.token;
  else if(auth.user&&auth.pass) h.Authorization='Basic '+btoa(auth.user+':'+auth.pass);
  return h;
}
async function api(path, opts){
  const o=opts||{};
  const r=await fetch(path,{method:o.method||'GET',headers:headers(),body:o.body,credentials:'same-origin'});
  const j=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(j.error||r.statusText);
  return j;
}

async function boot(){
  catalog=await api('/v1/loomgraph');
  document.getElementById('blurb').textContent=(catalog.tagline||'')+' · '+(catalog.protocol||'');
  const box=document.getElementById('graphs');
  box.innerHTML='';
  (catalog.graphs||[]).forEach(g=>{
    const b=document.createElement('button');
    b.type='button'; b.className='gbtn'+(g.id===graphId?' on':'');
    b.innerHTML=`<b>${g.name}</b><small>${g.desc||''} · ${g.nodes} nodes</small>`;
    b.onclick=()=>{graphId=g.id; document.querySelectorAll('.gbtn').forEach(x=>x.classList.remove('on')); b.classList.add('on'); loadMermaid();};
    box.appendChild(b);
  });
  loadMermaid();
}

async function loadMermaid(){
  const j=await api('/v1/loomgraph/mermaid/'+encodeURIComponent(graphId));
  const el=document.getElementById('mermaid');
  const id='mmd-'+Date.now();
  el.innerHTML=`<pre class="mermaid" id="${id}">${(j.mermaid||'').replace(/</g,'&lt;')}</pre>`;
  try{ await mermaid.run({nodes:[document.getElementById(id)]}); }catch(e){ el.textContent=j.mermaid||String(e); }
}

async function runGraph(){
  const goal=document.getElementById('goal').value.trim();
  if(!goal){ alert('Enter a goal'); return; }
  document.getElementById('runBtn').disabled=true;
  document.getElementById('log').textContent='Running LOOMGRAPH…';
  try{
    const j=await api('/v1/loomgraph/run',{method:'POST',body:JSON.stringify({goal, graph_id:graphId})});
    document.getElementById('path').textContent=(j.path||[]).join(' → ')||'—';
    const steps=document.getElementById('steps');
    steps.innerHTML='';
    (j.steps||[]).forEach(s=>{
      const d=document.createElement('div');
      d.className='step';
      d.innerHTML=`<span class="${s.ok?'ok':'bad'}">${s.ok?'✓':'✗'}</span> <b>${s.label||s.node}</b> <span>${s.kind||''} · ${s.ms||0}ms</span>`;
      steps.appendChild(d);
    });
    document.getElementById('log').textContent=JSON.stringify({
      ok:j.ok,id:j.id,graph:j.graph_id,ms:j.ms,message:j.message,path:j.path
    },null,2);
    // show run mermaid with path
    if(j.mermaid){
      const el=document.getElementById('mermaid');
      const id='mmd-run-'+Date.now();
      el.innerHTML=`<pre class="mermaid" id="${id}">${j.mermaid.replace(/</g,'&lt;')}</pre>`;
      try{ await mermaid.run({nodes:[document.getElementById(id)]}); }catch(_){ el.textContent=j.mermaid; }
    }
  }catch(e){
    document.getElementById('log').textContent=String(e.message||e);
  }finally{
    document.getElementById('runBtn').disabled=false;
  }
}
boot();
</script>
</body>
</html>
"""
