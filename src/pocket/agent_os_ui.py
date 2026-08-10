"""Agent OS screen — first-class hub for every POCKET system."""

OS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Agent OS</title>
<style>
:root{
  --bg:#07070a; --panel:#121216; --line:rgba(255,255,255,.08); --fg:#f4f4f5;
  --muted:#a1a1aa; --accent:#10a37f; --violet:#a78bfa; --blue:#60a5fa; --amber:#fbbf24;
}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:var(--bg);color:var(--fg);min-height:100vh}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.top{display:flex;align-items:center;gap:12px;padding:14px 20px;border-bottom:1px solid var(--line);background:rgba(7,7,10,.9);position:sticky;top:0;backdrop-filter:blur(12px);z-index:10}
.brand{font-weight:700;letter-spacing:-.03em}
.brand span{color:var(--accent)}
.nav{display:flex;gap:8px;flex-wrap:wrap;margin-left:12px}
.nav a{color:var(--muted);font-size:13px;padding:6px 10px;border-radius:8px;border:1px solid transparent}
.nav a:hover{color:var(--fg);background:rgba(255,255,255,.04);text-decoration:none}
.nav a.on{color:var(--fg);border-color:var(--line);background:var(--panel)}
.wrap{max-width:1180px;margin:0 auto;padding:22px 18px 64px}
h1{font-size:28px;letter-spacing:-.04em;margin:0 0 8px}
.sub{color:var(--muted);font-size:14px;line-height:1.5;margin:0 0 22px;max-width:720px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;min-height:120px;display:flex;flex-direction:column;gap:8px}
.card h3{margin:0;font-size:15px;font-weight:650}
.card p{margin:0;font-size:12.5px;color:var(--muted);line-height:1.45;flex:1}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:600;padding:3px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted);width:fit-content}
.badge.ok{color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
.badge.bad{color:#fca5a5;border-color:rgba(248,113,113,.35);background:rgba(248,113,113,.08)}
.card .actions{display:flex;flex-wrap:wrap;gap:6px}
.card button,.card a.btn{
  border:1px solid var(--line);background:transparent;color:var(--fg);border-radius:8px;
  padding:6px 10px;font-size:12px;font-weight:600;cursor:pointer;text-decoration:none
}
.card button.primary,.card a.btn.primary{background:var(--accent);color:#041;border-color:transparent}
.section{margin-top:28px}
.section h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 12px}
.parity{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}
.parity .card h3{font-size:14px;color:var(--violet)}
.parity ul{margin:0;padding-left:16px;font-size:12px;color:var(--muted);line-height:1.45}
.parity li{margin:3px 0}
.parity .deeper{color:#86efac}
.row{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
input,select,textarea{background:#0c0c0e;border:1px solid var(--line);border-radius:8px;color:var(--fg);padding:8px 10px;font:inherit;font-size:13px}
textarea{width:100%;min-height:90px}
pre{background:#0a0a0c;border:1px solid var(--line);border-radius:10px;padding:12px;font-size:11.5px;overflow:auto;max-height:280px;color:#c8f0d4}
.meta{font-size:12px;color:var(--muted)}
.chip{font-size:11px;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
</style>
</head>
<body>
<header class="top">
  <div class="brand">POCKET <span>Agent OS</span></div>
  <nav class="nav">
    <a class="on" href="/os">Systems</a>
    <a href="/desk">Desk</a>
    <a href="/work">Work Studio</a>
    <a href="/studio">Product Studio</a>
    <a href="/phone">Phone</a>
    <a href="/developers">API</a>
  </nav>
  <div style="flex:1"></div>
  <span class="chip" id="ver">…</span>
</header>
<div class="wrap">
  <h1>Native Agent OS</h1>
  <p class="sub">
    Every POCKET agent system is first-class — desk, swarm, pixel memory, engines, sandbox, wiki, projects.
    Depth that 2026 cloud agent desktops sell as products, running <b style="color:var(--fg)">natively on your host</b>.
  </p>
  <div class="row">
    <span class="chip" id="readyChip">probing…</span>
    <button class="btn" onclick="load()" style="border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:8px;padding:7px 12px;font-weight:600;cursor:pointer">Refresh</button>
    <a class="btn primary" href="/desk" style="border:0;background:var(--accent);color:#041;border-radius:8px;padding:7px 12px;font-weight:700">Open Desk</a>
  </div>

  <div class="section">
    <h2>First-class systems</h2>
    <div class="grid" id="systems"></div>
  </div>

  <div class="section">
    <h2>2026 parity — what we cover natively · deeper</h2>
    <div class="parity" id="parity"></div>
  </div>

  <div class="section">
    <h2>Native project (Replit-class on disk)</h2>
    <div class="row">
      <input id="projName" placeholder="project-name" style="min-width:160px"/>
      <select id="projTpl">
        <option value="typescript">TypeScript</option>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="blank">Blank</option>
      </select>
      <button onclick="createProj()" style="border:0;background:var(--accent);color:#041;border-radius:8px;padding:8px 12px;font-weight:700;cursor:pointer">Create project</button>
      <button onclick="runSel()" style="border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:8px;padding:8px 12px;font-weight:600;cursor:pointer">Run selected</button>
    </div>
    <div class="grid" id="projects"></div>
    <pre id="runOut" style="display:none;margin-top:12px"></pre>
  </div>

  <div class="section">
    <h2>Pixel artifacts (agent memory)</h2>
    <div class="grid" id="arts"></div>
  </div>

  <div class="section">
    <h2>Swarm roster (AI-version bound)</h2>
    <div class="grid" id="roster"></div>
  </div>

  <div class="section">
    <h2>All first-class agents</h2>
    <p class="meta" id="fcMeta">Loading registry…</p>
    <div class="grid" id="fcAgents"></div>
  </div>

  <div class="section">
    <h2>OS timeline</h2>
    <pre id="timeline">…</pre>
  </div>
</div>
<script>
const $=id=>document.getElementById(id);
let DASH=null, SEL=null;
function authHeaders(){
  const h={'Content-Type':'application/json'};
  try{
    const tok=sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'';
    const u=sessionStorage.getItem('pocket_user')||localStorage.getItem('pocket_user')||'';
    if(tok){ h['X-Pocket-Token']=tok; h['Authorization']='Bearer '+tok; }
    if(u) h['X-Pocket-User']=u;
  }catch(_){}
  return h;
}
async function api(path, opts){
  opts=opts||{};
  opts.headers=Object.assign({}, authHeaders(), opts.headers||{});
  const r=await fetch(path, opts);
  if(r.status===401){ location.href='/desk'; throw new Error('login required — open Desk once to sign in'); }
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
function esc(s){ return String(s??'').replace(/[&<>"']/g,c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])); }
async function load(){
  DASH=await api('/v1/os');
  $('ver').textContent='v'+(DASH.version||'');
  $('readyChip').textContent=(DASH.systems&&DASH.systems.ready)+'/'+(DASH.systems&&DASH.systems.total)+' systems ready';
  // systems
  const box=$('systems'); box.innerHTML='';
  (DASH.systems.systems||[]).forEach(s=>{
    const el=document.createElement('div'); el.className='card';
    const href=s.route||'/desk';
    const mode=s.mode?('?mode='+encodeURIComponent(s.mode)):'';
    el.innerHTML=`<span class="badge ${s.ok?'ok':'bad'}">${s.ok?'live':'degraded'} · ${esc(s.kind||'')}</span>
      <h3>${esc(s.name)}</h3>
      <p>${esc(s.blurb||'')}</p>
      <div class="meta">${esc(s.detail||'')}</div>
      <div class="actions">
        <a class="btn primary" href="${href}">Open</a>
        ${s.mode?`<a class="btn" href="/desk" onclick="sessionStorage.setItem('pocket_os_mode','${esc(s.mode)}')">Desk · ${esc(s.mode)}</a>`:''}
      </div>`;
    box.appendChild(el);
  });
  // parity
  const pbox=$('parity'); pbox.innerHTML='';
  ((DASH.parity&&DASH.parity.rows)||[]).forEach(row=>{
    const el=document.createElement('div'); el.className='card';
    el.innerHTML=`<h3>${esc(row.competitor)}</h3>
      <div class="meta">Touches: ${(row.systems_touching||[]).map(esc).join(', ')||'—'}</div>
      <ul>${(row.pocket_native||[]).map(x=>'<li>'+esc(x)+'</li>').join('')}</ul>
      <ul class="deeper">${(row.pocket_deeper||[]).map(x=>'<li>↑ '+esc(x)+'</li>').join('')}</ul>`;
    pbox.appendChild(el);
  });
  // projects
  const pjs=$('projects'); pjs.innerHTML='';
  ((DASH.projects&&DASH.projects.projects)||[]).forEach(p=>{
    const el=document.createElement('div'); el.className='card';
    el.innerHTML=`<h3>${esc(p.title||p.id)}</h3>
      <p>${esc(p.template)} · ${(p.files||[]).slice(0,6).map(esc).join(', ')}</p>
      <div class="actions">
        <button class="primary" data-id="${esc(p.id)}">Select &amp; run</button>
      </div>`;
    el.querySelector('button').onclick=()=>{ SEL=p.id; runSel(); };
    pjs.appendChild(el);
  });
  if(!((DASH.projects&&DASH.projects.projects)||[]).length){
    pjs.innerHTML='<div class="card"><p>No projects yet — create one above.</p></div>';
  }
  // artifacts
  const ab=$('arts'); ab.innerHTML='';
  const arts=(DASH.artifacts&&DASH.artifacts.artifacts)||[];
  if(!arts.length) ab.innerHTML='<div class="card"><p>No artifacts — run Coding Swarm from desk.</p></div>';
  arts.slice(0,12).forEach(a=>{
    const el=document.createElement('div'); el.className='card';
    el.innerHTML=`<h3 style="font-size:12px;word-break:break-all">${esc(a.symbol)}</h3>
      <p>${esc((a.note||a.preview||'').slice(0,120))}</p>
      <div class="actions">
        <button data-s="${esc(a.symbol)}" class="runA">Run code</button>
        <button data-s="${esc(a.symbol)}" class="impA">→ Project</button>
      </div>`;
    el.querySelector('.runA').onclick=()=>runArt(a.symbol);
    el.querySelector('.impA').onclick=()=>impArt(a.symbol);
    ab.appendChild(el);
  });
  // roster
  const rb=$('roster'); rb.innerHTML='';
  ((DASH.swarm_roster&&DASH.swarm_roster.agents)||[]).forEach(a=>{
    const el=document.createElement('div'); el.className='card';
    el.innerHTML=`<span class="badge ok">${esc(a.bound_engine||'?')} · ${esc(a.ai_version||'')}</span>
      <h3>${esc(a.name)}</h3><p>${esc(a.role)}</p>`;
    rb.appendChild(el);
  });
  // first-class agents registry
  try{
    const fc=await api('/v1/agents/first-class');
    const meta=$('fcMeta');
    if(meta) meta.textContent=(fc.count||0)+' first-class agents · groups: '+Object.keys(fc.by_group||{}).join(', ');
    const box=$('fcAgents'); if(box){
      box.innerHTML='';
      const groups=fc.groups||{};
      Object.keys(groups).forEach(g=>{
        (groups[g]||[]).slice(0,24).forEach(a=>{
          const el=document.createElement('div'); el.className='card';
          const mode=a.desk_mode||'';
          el.innerHTML=`<span class="badge ok">${esc(a.kind)} · ${esc(a.group)}</span>
            <h3>${esc(a.name)}</h3>
            <p>${esc(a.blurb||a.role||'')}</p>
            <div class="meta">${a.harness?'harness · ':''}${a.pixel?'pixel · ':''}${esc(a.engine||'')}</div>
            <div class="actions">
              ${mode?`<a class="btn primary" href="/desk" onclick="sessionStorage.setItem('pocket_os_mode','${esc(mode)}')">Open</a>`:''}
              ${a.mention?`<span class="chip">@${esc(a.mention)}</span>`:''}
            </div>`;
          box.appendChild(el);
        });
      });
    }
  }catch(e){ const m=$('fcMeta'); if(m) m.textContent=String(e.message||e); }
  // timeline
  const ev=((DASH.timeline&&DASH.timeline.events)||[]).slice(0,30);
  $('timeline').textContent=ev.length?ev.map(e=>JSON.stringify(e)).join('\n'):'No OS events yet';
}
async function createProj(){
  const name=$('projName').value||'';
  const template=$('projTpl').value;
  const j=await api('/v1/os/projects',{method:'POST',body:JSON.stringify({name,template,title:name})});
  if(!j.ok){ alert(j.error||'failed'); return; }
  SEL=j.project&&j.project.id;
  await load();
  alert('Created '+SEL);
}
async function runSel(){
  if(!SEL){ alert('Select or create a project first'); return; }
  const j=await api('/v1/os/run',{method:'POST',body:JSON.stringify({project_id:SEL})});
  const out=$('runOut'); out.style.display='block';
  out.textContent=(j.stdout||'')+(j.stderr?('\n[stderr]\n'+j.stderr):'')+(j.error?('\n[error] '+j.error):'');
  await load();
}
async function runArt(sym){
  const j=await api('/v1/os/run-artifact',{method:'POST',body:JSON.stringify({symbol:sym})});
  const out=$('runOut'); out.style.display='block';
  out.textContent=JSON.stringify(j,null,2).slice(0,8000);
  await load();
}
async function impArt(sym){
  const j=await api('/v1/os/import-artifact',{method:'POST',body:JSON.stringify({symbol:sym})});
  alert(j.ok?('Project '+j.project_id): (j.error||'fail'));
  await load();
}
load().catch(e=>{ $('readyChip').textContent=String(e.message||e); });
</script>
</body>
</html>
"""
