"""POCKET Power console — one screen that runs the lab."""


def power_html() -> str:
    return HTML


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · Power</title>
<script src="/auth/client.js"></script>
<style>
:root{--bg:#07070a;--panel:#121218;--line:rgba(255,255,255,.1);--fg:#f4f4f8;--mut:#8b8b9a;--ok:#6ee7b7;--acc:#10a37f}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 ui-sans-serif,system-ui}
a{color:var(--ok);text-decoration:none}
.wrap{max-width:1080px;margin:0 auto;padding:20px 16px 80px}
h1{font-size:28px;letter-spacing:-.04em;margin:0 0 6px}
.sub{color:var(--mut);margin:0 0 18px}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
input,textarea{flex:1;min-width:220px;background:#0c0c10;border:1px solid var(--line);color:var(--fg);border-radius:10px;padding:10px 12px}
button{background:var(--acc);color:#041;border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}
button.ghost{background:transparent;color:var(--fg);border:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin:14px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 12px}
.card b{display:block;font-size:12px;color:var(--mut);font-weight:600}
.card span{font-size:18px}
.fam{margin:18px 0}
.fam h2{font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em}
.wf{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line);font-size:13px}
.wf button{padding:6px 10px;font-size:12px}
pre{background:#0c0c10;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;max-height:280px;font-size:12px}
.vs td{padding:6px 8px;border-bottom:1px solid var(--line);font-size:13px}
</style>
</head>
<body>
<div class="wrap">
  <div class="row" style="margin:0 0 10px">
    <a href="/os">Platform</a>
    <a href="/power">Power</a>
    <a href="/desk">Desk</a>
    <a href="/work">Work</a>
  </div>
  <h1>POCKET Power</h1>
  <p class="sub">Same APIs as Platform: GO holds working workflows and active states. Do it runs Power. This page is the command plane, not a second product.</p>
  <div class="row">
    <input id="goal" placeholder="e.g. morning seatbelt · trade prep · billing plans · phone pair"/>
    <button onclick="doGoal()">Do it</button>
    <button onclick="goLab()">GO</button>
    <button class="ghost" onclick="pulse()">Pulse</button>
    <button class="ghost" onclick="vs()">Vs theirs</button>
    <button class="ghost" onclick="recall()">Recall</button>
    <a class="ghost" href="/desk" style="padding:10px 14px;border-radius:10px;border:1px solid var(--line)">Desk</a>
  </div>
  <div class="grid" id="pulse"></div>
  <div class="fam" id="goBoard"></div>
  <pre id="out">Pulse the lab, hit GO, or type a goal.</pre>
  <div id="families"></div>
</div>
<script>
async function api(path, opt){
  const r = await fetch(path, Object.assign({credentials:'include', headers:{'Content-Type':'application/json'}}, opt||{}));
  const t = await r.text();
  try{ return JSON.parse(t); }catch(e){ throw new Error(t.slice(0,200)); }
}
function card(l,v){ return '<div class="card"><b>'+l+'</b><span>'+v+'</span></div>'; }
async function pulse(){
  const j = await api('/v1/power');
  const g=j.go||{};
  $('pulse').innerHTML = card('Clouds', j.clouds)+card('Tools', j.tools)+card('Universal', j.universal_tools)+card('Workflows', j.workflows)+card('GO active', g.active_count||0)+card('Working', (g.working||[]).length)+card('Armed', (g.armed||[]).length)+card('Listening', (j.listening||[]).length);
  $('out').textContent = JSON.stringify({listening:j.listening, go:g, last:j.last_run&&j.last_run.goal}, null, 2);
  try{ await drawGo(); }catch(_){}
}
async function goLab(){
  $('out').textContent='GO…';
  const j = await api('/v1/go',{method:'POST', body:JSON.stringify({arm_daily:true})});
  $('out').textContent = JSON.stringify({go_count:j.go_count, active:j.active_count, working:j.working, armed:j.armed, workflow_status:j.workflow_status}, null, 2);
  await pulse();
}
async function drawGo(){
  const j = await api('/v1/go');
  const sur = Object.values(j.surfaces||{});
  const working = (j.working||[]);
  const armed = (j.armed||[]);
  const wfs = Object.values(j.workflows||{}).filter(w=>w.status && w.status!=='idle').slice(0,24);
  $('goBoard').innerHTML = '<h2>GO · active states</h2>'+
    sur.map(s=>'<div class="wf"><div><b>'+s.id+'</b> · '+(s.status||'')+'</div><span>'+(s.active?'live':'')+'</span></div>').join('')+
    '<h2>Working / armed workflows</h2>'+
    (working.concat(armed).length? working.concat(armed).map(id=>'<div class="wf"><code>'+id+'</code></div>').join('') : '<div class="wf">None working — hit GO to arm daily + triple</div>')+
    (wfs.length? ('<h2>Recent workflow states</h2>'+wfs.map(w=>'<div class="wf"><div><code>'+w.id+'</code> '+ (w.status||'')+' · runs '+(w.runs||0)+'</div></div>').join('')) : '');
}
async function doGoal(){
  const goal = $('goal').value.trim();
  if(!goal){ $('out').textContent='Type a goal.'; return; }
  $('out').textContent='Running…';
  const j = await api('/v1/power/do',{method:'POST', body:JSON.stringify({goal})});
  $('out').textContent = JSON.stringify(j, null, 2);
}
async function vs(){
  const j = await api('/v1/power/vs');
  $('out').textContent = j.score+'\n'+j.note;
}
async function recall(){
  const j = await api('/v1/power/recall');
  $('out').textContent = JSON.stringify(j.runs||[], null, 2);
}
async function loadWf(){
  const j = await api('/v1/workflows/multi');
  const by={};
  (j.workflows||[]).forEach(w=>{ (by[w.family]=by[w.family]||[]).push(w); });
  $('families').innerHTML = Object.keys(by).map(f=>{
    const rows = by[f].map(w=>'<div class="wf"><div><code>'+w.id+'</code> '+w.title+' · '+w.steps+' steps</div><button class="ghost" onclick="runWf(\''+w.id+'\')">Run</button></div>').join('');
    return '<div class="fam"><h2>'+f+' · '+by[f].length+'</h2>'+rows+'</div>';
  }).join('');
}
async function runWf(id){
  $('out').textContent='Running '+id+'…';
  const j = await api('/v1/power/do',{method:'POST', body:JSON.stringify({workflow_id:id, goal:id})});
  $('out').textContent = JSON.stringify(j, null, 2);
}
function $(id){ return document.getElementById(id); }
pulse(); loadWf();
</script>
</body>
</html>
"""
