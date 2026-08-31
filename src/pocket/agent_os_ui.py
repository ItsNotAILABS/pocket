"""Agent OS / Platform screen — interactive hub using Power, GO, workflows, clouds."""

OS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · Platform</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#07070a; --panel:#121216; --line:rgba(255,255,255,.08); --fg:#f4f4f5;
  --muted:#a1a1aa; --accent:#10a37f; --ok:#6ee7b7;
}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 420px at 10% -10%,rgba(16,163,127,.08),transparent 50%),var(--bg);color:var(--fg);min-height:100vh;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
.top{display:flex;align-items:center;gap:12px;padding:14px 20px;border-bottom:1px solid var(--line);background:rgba(7,7,10,.8);position:sticky;top:0;backdrop-filter:blur(18px);z-index:10;flex-wrap:wrap}
.brand{font-weight:700;letter-spacing:-.03em}
.brand span{color:var(--accent)}
.nav{display:flex;gap:6px;flex-wrap:wrap}
.nav a{color:var(--muted);font-size:13px;padding:6px 10px;border-radius:8px}
.nav a:hover,.nav a.on{color:var(--fg);background:rgba(255,255,255,.05)}
.wrap{max-width:1180px;margin:0 auto;padding:22px 18px 72px}
h1{font-size:26px;letter-spacing:-.04em;margin:0 0 6px}
.sub{color:var(--muted);font-size:14px;margin:0 0 16px;max-width:740px;line-height:1.5}
.row{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
input{flex:1;min-width:200px;background:#0c0c0e;border:1px solid var(--line);border-radius:10px;color:var(--fg);padding:10px 12px;font:inherit}
button,.btn{border:1px solid var(--line);background:transparent;color:var(--fg);border-radius:10px;padding:9px 12px;font-size:13px;font-weight:650;cursor:pointer}
button.primary,.btn.primary{background:var(--accent);color:#041;border-color:transparent}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:6px}
.card h3{margin:0;font-size:14px}
.card p,.meta{margin:0;font-size:12px;color:var(--muted);line-height:1.4}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted);width:fit-content}
.badge.ok{color:var(--ok);border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
.badge.bad{color:#fca5a5;border-color:rgba(248,113,113,.3)}
.section{margin-top:26px}
.section h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 10px}
.stat{font-size:20px;font-weight:650}
.actions{display:flex;flex-wrap:wrap;gap:6px}
.wf{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:7px 0;border-bottom:1px solid var(--line);font-size:13px}
pre{background:#0a0a0c;border:1px solid var(--line);border-radius:10px;padding:12px;font-size:11.5px;overflow:auto;max-height:240px}
.chip{font-size:11px;padding:3px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.parity{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.parity ul{margin:0;padding-left:16px;font-size:12px;color:var(--muted)}
</style>
</head>
<body>
<header class="top">
  <div class="brand">POCKET <span>Platform</span></div>
  <nav class="nav">
    <a class="on" href="/os">Platform</a>
    <a href="/power">Power</a>
    <a href="/desk">Desk</a>
    <a href="/work">Work</a>
    <a href="/studio">Studio</a>
    <a href="/phone">Phone</a>
  </nav>
  <div style="flex:1"></div>
  <span class="chip" id="ver">…</span>
</header>
<div class="wrap">
  <h1>Platform</h1>
  <p class="sub">Live lab board. GO holds active states and all 100 workflow slots. Power runs a goal on this host. These controls call those APIs — not a separate demo.</p>
  <div class="row">
    <input id="goal" placeholder="Goal — morning seatbelt, trade prep, billing, phone pair…"/>
    <button class="primary" onclick="doGoal()">Do it</button>
    <button class="primary" onclick="goLab()">GO</button>
    <button onclick="tickGo()">Tick</button>
    <button onclick="load()">Refresh</button>
  </div>
  <div class="grid" id="stats"></div>
  <pre id="out">Hit GO to arm daily + triple workflows, or type a goal.</pre>

  <div class="section">
    <h2>GO · active surfaces</h2>
    <div class="grid" id="surfaces"></div>
  </div>
  <div class="section">
    <h2>Working / armed workflows</h2>
    <div id="working"></div>
  </div>
  <div class="section">
    <h2>First-class systems</h2>
    <div class="grid" id="systems"></div>
  </div>
  <div class="section">
    <h2>100 multi workflows</h2>
    <div id="families"></div>
  </div>
  <div class="section">
    <h2>2026 parity</h2>
    <div class="parity" id="parity"></div>
  </div>
  <div class="section">
    <h2>Native project</h2>
    <div class="row">
      <input id="projName" placeholder="project-name"/>
      <select id="projTpl" style="background:#0c0c0e;border:1px solid var(--line);color:var(--fg);border-radius:10px;padding:8px">
        <option value="typescript">TypeScript</option>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="blank">Blank</option>
      </select>
      <button class="primary" onclick="createProj()">Create</button>
      <button onclick="runSel()">Run selected</button>
    </div>
    <div class="grid" id="projects"></div>
    <pre id="runOut" style="display:none;margin-top:12px"></pre>
  </div>
  <div class="section">
    <h2>Pixel artifacts</h2>
    <div class="grid" id="arts"></div>
  </div>
  <div class="section">
    <h2>Swarm + first-class agents</h2>
    <p class="meta" id="fcMeta"></p>
    <div class="grid" id="roster"></div>
    <div class="grid" id="fcAgents" style="margin-top:10px"></div>
  </div>
</div>
<script>
const $=id=>document.getElementById(id);
let SEL=null;
function esc(s){ return String(s??'').replace(/[&<>"']/g,c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])); }
async function api(path, opt){
  const r=await fetch(path, Object.assign({credentials:'include', headers:{'Content-Type':'application/json'}}, opt||{}));
  if(r.status===401){ location.href='/desk'; throw new Error('sign in on Desk first'); }
  const t=await r.text();
  try{ return JSON.parse(t); }catch(e){ throw new Error(t.slice(0,200)); }
}
function card(l,v){ return '<div class="card"><p>'+esc(l)+'</p><div class="stat">'+esc(v)+'</div></div>'; }

async function load(){
  const [dash, power, go, wfs] = await Promise.all([
    api('/v1/os'),
    api('/v1/power').catch(()=>({})),
    api('/v1/go').catch(()=>({})),
    api('/v1/workflows/multi').catch(()=>({})),
  ]);
  $('ver').textContent='v'+(dash.version||'');
  const g=power.go||{};
  $('stats').innerHTML =
    card('Systems ready', (dash.systems&&dash.systems.ready)+'/'+(dash.systems&&dash.systems.total))+
    card('Tools', power.tools||0)+
    card('Workflows', power.workflows||100)+
    card('GO active', g.active_count||go.active_count||0)+
    card('Working', (g.working||go.working||[]).length)+
    card('Armed', (g.armed||go.armed||[]).length)+
    card('Clouds', power.clouds||0)+
    card('Listening', (power.listening||[]).length);

  const sur=Object.values(go.surfaces||{});
  $('surfaces').innerHTML = sur.length ? sur.map(s=>`
    <div class="card">
      <span class="badge ${s.active?'ok':'bad'}">${esc(s.status||'?')}</span>
      <h3>${esc(s.id)}</h3>
      <p>${esc(typeof s.detail==='string'?s.detail:(s.url||''))}</p>
    </div>`).join('') : '<div class="card"><p>No GO board yet — press GO.</p></div>';

  const live=(go.working||[]).concat(go.armed||[]);
  $('working').innerHTML = live.length
    ? live.map(id=>`<div class="wf"><code>${esc(id)}</code><button onclick="runWf('${esc(id)}')">Run</button></div>`).join('')
    : '<div class="meta">None armed. Press GO to arm daily + triple.</div>';

  const box=$('systems'); box.innerHTML='';
  ((dash.systems&&dash.systems.systems)||[]).forEach(s=>{
    const href=s.route||'/desk';
    box.insertAdjacentHTML('beforeend', `<div class="card">
      <span class="badge ${s.ok?'ok':'bad'}">${s.ok?'live':'off'} · ${esc(s.kind||'')}</span>
      <h3>${esc(s.name)}</h3>
      <p>${esc(s.blurb||'')}</p>
      <p class="meta">${esc(s.detail||'')}</p>
      <div class="actions"><a class="btn primary" href="${href}">Open</a></div>
    </div>`);
  });

  const by={};
  (wfs.workflows||[]).forEach(w=>{ (by[w.family]=by[w.family]||[]).push(w); });
  $('families').innerHTML = Object.keys(by).map(f=>{
    const rows=by[f].map(w=>`<div class="wf"><div><code>${esc(w.id)}</code> ${esc(w.title)} · ${w.steps} steps</div><button onclick="runWf('${esc(w.id)}')">Run</button></div>`).join('');
    return `<div class="section" style="margin-top:14px"><h2>${esc(f)} · ${by[f].length}</h2>${rows}</div>`;
  }).join('') || '<div class="meta">Workflow catalog not loaded.</div>';

  const pbox=$('parity'); pbox.innerHTML='';
  ((dash.parity&&dash.parity.rows)||[]).forEach(row=>{
    pbox.insertAdjacentHTML('beforeend', `<div class="card">
      <h3>${esc(row.competitor)}</h3>
      <ul>${(row.pocket_native||[]).slice(0,6).map(x=>'<li>'+esc(x)+'</li>').join('')}</ul>
    </div>`);
  });

  const pjs=$('projects'); pjs.innerHTML='';
  const projs=(dash.projects&&dash.projects.projects)||[];
  if(!projs.length) pjs.innerHTML='<div class="card"><p>No projects yet.</p></div>';
  projs.forEach(p=>{
    const el=document.createElement('div'); el.className='card';
    el.innerHTML=`<h3>${esc(p.title||p.id)}</h3><p>${esc(p.template||'')}</p><div class="actions"><button class="primary">Run</button></div>`;
    el.querySelector('button').onclick=()=>{ SEL=p.id; runSel(); };
    pjs.appendChild(el);
  });

  const ab=$('arts'); ab.innerHTML='';
  const arts=(dash.artifacts&&dash.artifacts.artifacts)||[];
  if(!arts.length) ab.innerHTML='<div class="card"><p>No pixel artifacts yet.</p></div>';
  arts.slice(0,8).forEach(a=>{
    ab.insertAdjacentHTML('beforeend', `<div class="card"><h3 style="font-size:12px">${esc(a.symbol)}</h3><p>${esc((a.note||'').slice(0,100))}</p></div>`);
  });

  const rb=$('roster'); rb.innerHTML='';
  ((dash.swarm_roster&&dash.swarm_roster.agents)||[]).forEach(a=>{
    rb.insertAdjacentHTML('beforeend', `<div class="card"><span class="badge ok">${esc(a.bound_engine||'')}</span><h3>${esc(a.name)}</h3><p>${esc(a.role||'')}</p></div>`);
  });
  try{
    const fc=await api('/v1/agents/first-class');
    $('fcMeta').textContent=(fc.count||0)+' first-class agents';
    const box=$('fcAgents'); box.innerHTML='';
    Object.values(fc.groups||{}).flat().slice(0,16).forEach(a=>{
      box.insertAdjacentHTML('beforeend', `<div class="card"><h3>${esc(a.name)}</h3><p>${esc(a.blurb||'')}</p></div>`);
    });
  }catch(e){ $('fcMeta').textContent=String(e.message||e); }
}

async function doGoal(){
  const goal=$('goal').value.trim();
  if(!goal){ $('out').textContent='Type a goal.'; return; }
  $('out').textContent='Power…';
  const j=await api('/v1/power/do',{method:'POST',body:JSON.stringify({goal})});
  $('out').textContent=JSON.stringify({ok:j.ok, pick:j.pick, run:j.run},null,2);
  await load();
}
async function goLab(){
  $('out').textContent='GO…';
  const j=await api('/v1/go',{method:'POST',body:JSON.stringify({arm_daily:true})});
  $('out').textContent=JSON.stringify({go_count:j.go_count, active:j.active_count, working:j.working, armed:j.armed, workflow_status:j.workflow_status},null,2);
  await load();
}
async function tickGo(){
  const j=await api('/v1/go/tick',{method:'POST',body:'{}'});
  $('out').textContent='Ticked · active '+(j.active_count||0);
  await load();
}
async function runWf(id){
  $('out').textContent='Running '+id+'…';
  const j=await api('/v1/power/do',{method:'POST',body:JSON.stringify({workflow_id:id,goal:id})});
  $('out').textContent=JSON.stringify(j.run||j,null,2);
  await load();
}
async function createProj(){
  const j=await api('/v1/os/projects',{method:'POST',body:JSON.stringify({name:$('projName').value,template:$('projTpl').value})});
  SEL=j.project&&j.project.id; await load();
}
async function runSel(){
  if(!SEL){ $('out').textContent='Create or pick a project.'; return; }
  const j=await api('/v1/os/run',{method:'POST',body:JSON.stringify({project_id:SEL})});
  const out=$('runOut'); out.style.display='block';
  out.textContent=(j.stdout||'')+(j.stderr||'')+(j.error||'');
}
load().catch(e=>{ $('out').textContent=String(e.message||e); });
</script>
</body>
</html>
"""
