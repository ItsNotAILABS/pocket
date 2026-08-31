"""POCKET Bots UI — Grok-Bot-style teammates on this host."""

from __future__ import annotations


def bots_html() -> str:
    return BOTS_HTML


BOTS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#07070b"/>
<title>POCKET · Bots</title>
<script src="/auth/client.js"></script>
<style>
:root{--bg:#07070b;--panel:#121214;--line:rgba(255,255,255,.08);--text:#f4f4f5;--muted:#a1a1aa;--accent:#10a37f;--ease:cubic-bezier(.22,1,.36,1)}
*{box-sizing:border-box}html,body{margin:0;height:100%;font-family:ui-sans-serif,system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--text)}
body{display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line);background:rgba(7,7,11,.9);backdrop-filter:blur(16px)}
.brand{display:flex;align-items:center;gap:8px;font-weight:700;text-decoration:none;color:inherit;letter-spacing:-.03em}
.brand i{width:22px;height:22px;border-radius:7px;background:#10a37f;color:#042f24;display:grid;place-items:center;font-style:normal;font-size:11px;font-weight:800}
.top a{color:#a1a1aa;text-decoration:none;font-size:13px;padding:6px 10px;border-radius:8px}
.top a:hover,.top a.on{color:#fff;background:#161616}
.sp{flex:1}
.pill{font-size:11px;color:var(--muted);border:1px solid var(--line);padding:4px 10px;border-radius:999px}
.shell{flex:1;display:grid;grid-template-columns:260px minmax(0,1fr) 280px;min-height:0}
@media(max-width:900px){.shell{grid-template-columns:1fr}.rail,.comp{display:none}.rail.open,.comp.open{display:flex}}
.rail,.comp{border-right:1px solid var(--line);display:flex;flex-direction:column;background:#0c0c10;min-height:0}
.comp{border-right:0;border-left:1px solid var(--line)}
.rail h2,.comp h2{margin:0;padding:14px 14px 8px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.list{flex:1;overflow:auto;padding:6px}
.bot{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:12px;cursor:pointer;border:1px solid transparent}
.bot:hover{background:#141418}
.bot.on{border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.08)}
.av{width:36px;height:36px;border-radius:12px;display:grid;place-items:center;font-weight:800;color:#042f24;flex:0 0 auto}
.bot b{display:block;font-size:13px}
.bot small{color:var(--muted);font-size:11px;line-height:1.3}
.btn{border:0;border-radius:10px;padding:10px 12px;font-weight:700;cursor:pointer;font:inherit}
.btn.primary{background:#10a37f;color:#042f24;width:calc(100% - 24px);margin:8px 12px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text)}
.chat{display:flex;flex-direction:column;min-height:0}
.chat-h{padding:14px 16px;border-bottom:1px solid var(--line)}
.chat-h h1{margin:0;font-size:18px;letter-spacing:-.03em}
.chat-h p{margin:4px 0 0;color:var(--muted);font-size:13px}
.msgs{flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
.bubble{max-width:min(640px,92%);padding:10px 12px;border-radius:14px;line-height:1.45;font-size:14px;white-space:pre-wrap}
.bubble.user{align-self:flex-end;background:#10a37f;color:#042f24}
.bubble.bot{align-self:flex-start;background:#18181c;border:1px solid var(--line)}
.bubble.system{align-self:center;color:var(--muted);font-size:12px;background:transparent}
.composer{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line)}
.composer textarea{flex:1;min-height:48px;max-height:140px;resize:vertical;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:var(--text);padding:10px 12px;font:inherit}
.hire{padding:12px;border-top:1px solid var(--line)}
.hire textarea,.hire input{width:100%;margin-top:6px;padding:10px;border-radius:10px;border:1px solid var(--line);background:#0c0c0e;color:var(--text);font:inherit}
.files{font-size:12px;padding:0 12px 12px}
.files a{display:block;color:#86efac;text-decoration:none;padding:6px 0;border-bottom:1px solid var(--line)}
.empty{padding:24px;color:var(--muted);line-height:1.5}
</style>
</head>
<body>
<header class="top">
  <a class="brand" href="/desk"><i>P</i>Bots</a>
  <a href="/desk">Desk</a>
  <a href="/phone">Phone</a>
  <a href="/imagine">Imagine</a>
  <a class="on" href="/bots">Bots</a>
  <div class="sp"></div>
  <span class="pill">pocket-agent teammates · own computer</span>
</header>
<div class="shell">
  <aside class="rail" id="rail">
    <h2>Team</h2>
    <div class="list" id="team"></div>
    <button class="btn primary" type="button" onclick="showHire()">New teammate</button>
  </aside>
  <main class="chat">
    <div class="chat-h" id="head">
      <h1>POCKET Bots</h1>
      <p>Named teammates with their own computer — message them like colleagues. Powered by pocket-agent + internal models, not a third-party bot cloud.</p>
    </div>
    <div class="msgs" id="msgs"><div class="empty">Pick a teammate, or hire one by describing the job.</div></div>
    <form class="composer" id="composer" onsubmit="sendMsg(event)">
      <textarea id="box" placeholder="Message like a colleague…" required></textarea>
      <button class="btn primary" type="submit" style="width:auto;margin:0">Send</button>
    </form>
  </main>
  <aside class="comp" id="comp">
    <h2>Computer</h2>
    <div class="files" id="files"><div class="empty">Each bot has a host workspace under ~/.pocket/bots.</div></div>
    <div style="padding:12px;display:flex;gap:8px;flex-wrap:wrap">
      <button class="btn ghost" type="button" onclick="togglePulse()">Always-on</button>
      <button class="btn ghost" type="button" onclick="loadTeam()">Refresh</button>
    </div>
    <div class="hire" id="hireBox" style="display:none">
      <b>Hire a teammate</b>
      <textarea id="hireText" rows="3" placeholder="I need a bot that handles sales follow-ups overnight…"></textarea>
      <button class="btn primary" type="button" style="width:100%;margin:10px 0 0" onclick="hire()">Create bot</button>
    </div>
  </aside>
</div>
<script>
let bots=[], active='', authed=false;
function headers(){
  const h={'Content-Type':'application/json'};
  const t=sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'';
  if(t){ h.Authorization='Bearer '+t; h['X-Pocket-Token']=t; }
  return h;
}
async function api(path, opt={}){
  const r=await fetch(path,{credentials:'same-origin',...opt, headers:{...headers(),...(opt.headers||{})}});
  if(r.status===401){ location.href='/login?next=/bots'; throw new Error('sign in'); }
  const j=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(j.error||r.statusText);
  return j;
}
function av(b){
  const c=b.color||'#10a37f';
  const l=(b.name||'B').slice(0,1).toUpperCase();
  return `<div class="av" style="background:${c}">${l}</div>`;
}
function renderTeam(){
  const box=document.getElementById('team');
  if(!bots.length){ box.innerHTML='<div class="empty">No bots yet.</div>'; return; }
  box.innerHTML=bots.map(b=>`
    <div class="bot ${b.id===active?'on':''}" data-id="${b.id}">
      ${av(b)}
      <div><b>${b.name}</b><small>${b.job||''}</small></div>
    </div>`).join('');
  box.querySelectorAll('.bot').forEach(el=>el.onclick=()=>openBot(el.dataset.id));
}
function showHire(){ document.getElementById('hireBox').style.display='block'; document.getElementById('hireText').focus(); }
async function hire(){
  const text=document.getElementById('hireText').value.trim();
  if(!text) return;
  const j=await api('/v1/bots/hire',{method:'POST', body:JSON.stringify({prompt:text})});
  await loadTeam();
  if(j.id) openBot(j.id);
  document.getElementById('hireText').value='';
}
async function loadTeam(){
  const j=await api('/v1/bots');
  bots=j.bots||[];
  renderTeam();
  if(!active && bots[0]) openBot(bots[0].id);
}
async function openBot(id){
  active=id;
  renderTeam();
  const j=await api('/v1/bots/'+encodeURIComponent(id));
  const b=j.bot||{};
  document.getElementById('head').innerHTML=`<h1>${b.name||id}</h1><p>${b.job||''} · ${b.engine||''}${b.always_on?' · always-on':''}</p>`;
  const msgs=j.messages||[];
  const box=document.getElementById('msgs');
  if(!msgs.length) box.innerHTML='<div class="empty">Say what you need. This bot keeps its own computer and thread.</div>';
  else{
    box.innerHTML=msgs.map(m=>`<div class="bubble ${m.role}">${esc(m.text||'')}</div>`).join('');
    box.scrollTop=box.scrollHeight;
  }
  const files=j.computer||[];
  document.getElementById('files').innerHTML=files.length?files.map(f=>`<div>${esc(f.rel)} · ${f.bytes}b</div>`).join(''):'<div class="empty">Computer is empty until the first task.</div>';
}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
async function sendMsg(ev){
  ev.preventDefault();
  if(!active){ showHire(); return; }
  const box=document.getElementById('box');
  const text=box.value.trim();
  if(!text) return;
  box.value='';
  document.getElementById('msgs').insertAdjacentHTML('beforeend', `<div class="bubble user">${esc(text)}</div>`);
  try{
    const j=await api('/v1/bots/'+encodeURIComponent(active)+'/message',{method:'POST',body:JSON.stringify({text})});
    document.getElementById('msgs').insertAdjacentHTML('beforeend', `<div class="bubble bot">${esc(j.reply||'')}</div>`);
    document.getElementById('msgs').scrollTop=99999;
    bots=bots.map(b=>b.id===active?(j.bot||b):b);
    renderTeam();
  }catch(e){
    document.getElementById('msgs').insertAdjacentHTML('beforeend', `<div class="bubble system">${esc(e.message)}</div>`);
  }
}
async function togglePulse(){
  if(!active) return;
  const b=bots.find(x=>x.id===active);
  const path='/v1/bots/'+encodeURIComponent(active)+'/pulse';
  await api(path,{method:'POST',body:JSON.stringify({on: !(b&&b.always_on)})});
  await loadTeam();
  openBot(active);
}
(async function(){
  if(window.PocketAuth && PocketAuth.ensureAuth) await PocketAuth.ensureAuth({device:'bots'});
  await loadTeam();
})();
</script>
</body></html>
"""
