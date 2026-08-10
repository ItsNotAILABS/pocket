"""POCKET Lab UI — readiness map for Studio · Capsules · Life · Phone (own panel)."""

from __future__ import annotations

LAB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Lab</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#09090b;--panel:#121214;--line:rgba(255,255,255,.08);--text:#fafafa;--muted:#a1a1aa;
  --accent:#34d399;--ok:#4ade80;--warn:#fbbf24;--font:ui-sans-serif,system-ui,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font);background:radial-gradient(900px 420px at 0% 0%,rgba(52,211,153,.07),transparent 50%),var(--bg);color:var(--text);min-height:100vh}
.pnav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid var(--line);background:rgba(0,0,0,.9);position:sticky;top:0;z-index:20;backdrop-filter:blur(12px)}
.pnav .brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;color:#f5f5f5;text-decoration:none}
.pnav .brand i{width:22px;height:22px;border-radius:6px;background:#10a37f;display:grid;place-items:center;font-size:11px;font-weight:800;color:#041;font-style:normal}
.pnav a{color:#8e8e8e;text-decoration:none;font-size:13px;padding:7px 11px;border-radius:8px}
.pnav a:hover,.pnav a.on{color:#f5f5f5;background:#161616}
.pnav .sp{flex:1}
.pill{font-size:11px;border:1px solid var(--line);padding:5px 10px;border-radius:999px;color:var(--muted)}
.pill.on{color:#86efac;border-color:#14532d;background:#052e16}
main{max-width:1100px;margin:0 auto;padding:20px 18px 48px}
.hero{margin-bottom:18px}
.hero h1{margin:0 0 8px;font-size:22px;letter-spacing:-.03em}
.hero p{margin:0;color:var(--muted);font-size:14px;line-height:1.5;max-width:52em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.card{background:linear-gradient(180deg,rgba(255,255,255,.02),transparent),var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:10px;min-height:180px}
.card.ok{border-color:rgba(74,222,128,.22)}
.card.warn{border-color:rgba(251,191,36,.28)}
.card h2{margin:0;font-size:15px;letter-spacing:-.02em;display:flex;align-items:center;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;background:#52525b}
.card.ok .dot{background:var(--ok);box-shadow:0 0 8px rgba(74,222,128,.5)}
.card.warn .dot{background:var(--warn)}
.blurb{font-size:13px;color:var(--muted);line-height:1.45;flex:1}
.meta{font-size:11px;color:#71717a;font-family:ui-monospace,Consolas,monospace;word-break:break-all}
.actions{display:flex;flex-wrap:wrap;gap:6px}
.btn{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:10px;padding:8px 11px;font-size:12px;font-weight:650;cursor:pointer}
.btn:hover{border-color:rgba(52,211,153,.45);background:rgba(52,211,153,.08)}
.btn.primary{background:linear-gradient(180deg,#34d399,#10b981);color:#052e16;border:0}
.flow{margin-top:22px;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.02)}
.flow h3{margin:0 0 8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.flow ol{margin:0;padding-left:18px;color:var(--muted);font-size:13px;line-height:1.55}
#log{margin-top:14px;font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;max-height:160px;overflow:auto;background:#050506;border:1px solid var(--line);border-radius:10px;padding:10px;color:#86efac}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#18181b;border:1px solid var(--line);padding:10px 14px;border-radius:10px;display:none;z-index:40;font-size:13px}
.toast.show{display:block}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/desk"><i>P</i>POCKET</a>
  <a href="/desk">Desk</a>
  <a class="on" href="/lab">Lab</a>
  <a href="/studio">Studio</a>
  <a href="/phone">Phone</a>
  <a href="/work">Work</a>
  <div class="sp"></div>
  <span class="pill" id="readyPill">…</span>
  <button type="button" class="btn" onclick="loadLab()">Refresh</button>
</header>
<main>
  <div class="hero">
    <h1>Lab · build better tech</h1>
    <p>First-class readiness map. Each card opens its own surface — Desk, Studio, Phone, Working stay separate. Host must stay online for the tunnel phone.</p>
  </div>
  <div class="grid" id="grid"><div class="card"><div class="blurb">Loading…</div></div></div>
  <div class="flow">
    <h3>Recommended loop</h3>
    <ol id="flowList">
      <li>Keep host serve running</li>
      <li>Studio agent: full demo loop</li>
      <li>Phone: pair → Continue as linked</li>
      <li>Capsules: allocate · exec · commit</li>
      <li>Life: Working board + Assist</li>
    </ol>
  </div>
  <div id="log"></div>
</main>
<div class="toast" id="toast"></div>
<script>
const auth = {
  token: sessionStorage.getItem('pocket_token') || localStorage.getItem('pocket_token') || '',
  user: sessionStorage.getItem('pocket_user') || localStorage.getItem('pocket_user') || 'pocket',
};
function headers(){
  const h={'Content-Type':'application/json'};
  if(auth.token){ h['Authorization']='Bearer '+auth.token; h['X-Pocket-Token']=auth.token; }
  return h;
}
function toast(m){ const t=document.getElementById('toast'); t.textContent=m; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2600); }
function log(m){ const el=document.getElementById('log'); el.textContent=(typeof m==='string'?m:JSON.stringify(m,null,2)).slice(0,6000); }
async function ensureAuth(){
  if(auth.token) return true;
  if(window.PocketAuth){
    auth.token = PocketAuth.getToken() || '';
    if(auth.token) return true;
    const ens = await PocketAuth.ensureAuth({device:'lab'});
    if(ens.ok){ auth.token=ens.token; return true; }
    return new Promise(function(resolve){
      PocketAuth.showPasswordGate({
        device:'lab',
        onSuccess: function(res){ auth.token=res.token||PocketAuth.getToken(); resolve(!!auth.token); }
      });
    });
  }
  try{
    const r=await fetch('/v1/auth/desktop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    const j=await r.json();
    if(j.token){
      auth.token=j.token;
      sessionStorage.setItem('pocket_token',j.token);
      localStorage.setItem('pocket_token',j.token);
      return true;
    }
  }catch(_){}
  return false;
}
async function api(path, opt={}){
  const r=await fetch(path,{...opt, headers:{...headers(), ...(opt.headers||{})}});
  const j=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(j.error||r.statusText);
  return j;
}
function openDesk(tab, agent){
  // Tell parent desk (iframe) when possible; else navigate
  try{
    if(window.parent && window.parent!==window){
      window.parent.postMessage({pocket:'lab', tab:tab||'', agent:agent||''}, '*');
      toast('Opening on desk…');
      return;
    }
  }catch(_){}
  if(agent) location.href='/desk?agent='+encodeURIComponent(agent);
  else if(tab==='studio') location.href='/studio';
  else if(tab==='phone') location.href='/phone';
  else if(tab==='work') location.href='/work';
  else location.href='/desk';
}
async function runAction(a, card){
  try{
    if(a.tab){ openDesk(a.tab); return; }
    if(a.agent){ openDesk('desk', a.agent); return; }
    if(a.workflow==='phone_iot'){ openDesk('phone'); return; }
    if(a.skill==='webgpu_probe' || (a.skill&&a.skill.indexOf('webgpu')>=0)){
      const j=await api('/v1/skills/run',{method:'POST',body:JSON.stringify({skill:'webgpu_probe'})});
      log(j); toast('WebGPU probe done'); return;
    }
    if((a.label||'').toLowerCase().indexOf('allocate')>=0 || (a.api||'').indexOf('allocate')>=0){
      const j=await api('/v1/capsule/allocate',{method:'POST',body:JSON.stringify({tier:'512MB',enableWebGPU:true,runtime:'HostWorker',label:'lab-ui'})});
      log(j); toast(j.message||('Capsule '+(j.capsule&&j.capsule.id))); return;
    }
    if((a.api||'').indexOf('studio/ship')>=0){
      const j=await api('/v1/studio/ship',{method:'POST',body:JSON.stringify({title:'POCKET',subtitle:'Lab ship',cta:'ItsNotAI Labs'})});
      log(j); toast(j.message||'Ship done'); return;
    }
    if(card && card.skill){
      const j=await api('/v1/skills/run',{method:'POST',body:JSON.stringify({skill:card.skill})});
      log(j); toast(card.skill+' ok'); return;
    }
    toast(a.label||'ok');
  }catch(e){ toast(e.message||String(e)); log(String(e)); }
}
function render(st){
  const pill=document.getElementById('readyPill');
  if(pill){
    pill.textContent=(st.ready||0)+'/'+(st.total||0)+' ready';
    pill.className='pill '+(st.all_first_class?'on':'');
  }
  const fl=document.getElementById('flowList');
  if(fl && st.flow) fl.innerHTML=(st.flow||[]).map(x=>'<li>'+x.replace(/^\d+\.\s*/,'')+'</li>').join('');
  const grid=document.getElementById('grid');
  grid.innerHTML=(st.cards||[]).map((c,i)=>{
    const cls=c.ok?'ok':'warn';
    const acts=(c.actions||[]).map((a,j)=>`<button type="button" class="btn ${j===0?'primary':''}" data-ci="${i}" data-ai="${j}">${a.label||'Go'}</button>`).join('');
    const meta=c.detail?JSON.stringify(c.detail).slice(0,140):'';
    return `<article class="card ${cls}" data-i="${i}">
      <h2><span class="dot"></span>${c.name||c.id}</h2>
      <div class="blurb">${c.blurb||''}</div>
      <div class="meta">${meta}</div>
      <div class="actions">${acts}</div>
    </article>`;
  }).join('');
  grid.querySelectorAll('button[data-ci]').forEach(btn=>{
    btn.onclick=()=>{
      const ci=+btn.getAttribute('data-ci');
      const ai=+btn.getAttribute('data-ai');
      const card=(st.cards||[])[ci];
      const act=(card.actions||[])[ai];
      runAction(act||{}, card);
    };
  });
}
async function loadLab(){
  await ensureAuth();
  try{
    const st=await api('/v1/lab');
    render(st);
    log({ready:st.ready,total:st.total,all_first_class:st.all_first_class});
  }catch(e){
    document.getElementById('grid').innerHTML=`<div class="card warn"><div class="blurb">${e.message||e}</div></div>`;
  }
}
loadLab();
</script>
</body>
</html>
"""


def lab_html() -> str:
    return LAB_HTML
