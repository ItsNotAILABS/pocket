"""PhoneAI Kernel OS — phone-native home served by the POCKET host.

App grid, status bar, kernel services, and the same Live companion FAB
(via ui kit). Works as a PWA on the handset today; Expo PhoneAI is the
native twin.
"""

from __future__ import annotations

PHONEAI_OS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-title" content="PhoneAI"/>
<link rel="manifest" href="/phoneai/manifest.json"/>
<title>PhoneAI</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86;--c:#58a6ff;--p:#14141c}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:430px;margin:0 auto;display:flex;flex-direction:column;min-height:100%;
  padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom);
  background:radial-gradient(700px 380px at 90% -8%,rgba(0,255,134,.1),transparent 50%),#05060a}
.status{display:flex;justify-content:space-between;padding:10px 18px 0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.view{display:none;flex:1;flex-direction:column;min-height:0}
.view.on{display:flex}
.hero{padding:14px 18px 6px}
h1{margin:4px 0;font-size:26px;letter-spacing:-.04em}
.lead{color:var(--muted);font-size:14px;line-height:1.4}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 8px;padding:12px 16px 8px}
.app{display:flex;flex-direction:column;align-items:center;gap:6px;text-decoration:none;color:var(--fg);background:none;border:0;font:inherit;padding:0}
.icon{width:56px;height:56px;border-radius:16px;display:grid;place-items:center;font-size:22px;
  border:1px solid var(--line);background:linear-gradient(160deg,rgba(255,255,255,.1),rgba(255,255,255,.02))}
.app span{font-size:11px;color:var(--muted)}
.dock{margin:8px 14px 12px;padding:8px;border-radius:22px;display:flex;justify-content:space-around;
  background:rgba(18,18,24,.88);border:1px solid var(--line);backdrop-filter:blur(16px)}
.quick{display:flex;gap:8px;padding:0 16px 10px;overflow:auto}
.quick button{flex:0 0 auto;border:1px solid var(--line);background:var(--p);color:var(--fg);border-radius:999px;padding:8px 12px;font-size:12px}
.log{flex:1;overflow:auto;padding:12px 14px}
.m{margin:0 0 10px;max-width:92%}
.m.me{margin-left:auto}
.m .b{padding:10px 12px;border-radius:14px;background:var(--p);line-height:1.45;font-size:15px;white-space:pre-wrap}
.m.me .b{background:#0b3d32;color:#d1fae5}
.form{display:flex;gap:8px;padding:10px 12px;border-top:1px solid var(--line)}
.form textarea,.form input,select{flex:1;min-height:44px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);padding:10px;font:inherit}
.form button, .go{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px;min-height:44px}
.item{padding:12px;border-bottom:1px solid var(--line);font-size:15px}
.item small{display:block;color:var(--muted);margin-top:4px}
video,canvas,.shot{width:100%;border-radius:16px;background:#000}
.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:10px}
.gallery img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px}
.more{padding:8px 16px 20px;color:var(--muted);font-size:12px}
.more a{color:var(--c)}
</style>
</head>
<body>
<div class="status"><span id="clk">PHONEAI</span><span id="host">GLIMMER</span></div>

<section class="view on" id="v-home">
  <div class="hero"><h1>PhoneAI</h1><p class="lead">Chat, camera, maps, notes, reminders — the stuff you actually do on a phone. Spark is Muse Glimmer on this PC.</p></div>
  <div class="quick">
    <button type="button" data-go="chat" data-pre="Remind me to ">Remind me</button>
    <button type="button" data-go="maps">Directions</button>
    <button type="button" data-go="chat" data-pre="Draft a text: ">Text</button>
    <button type="button" data-go="list">List</button>
  </div>
  <div class="grid">
    <button class="app" data-go="chat"><div class="icon">💬</div><span>Chat</span></button>
    <button class="app" data-go="camera"><div class="icon">📷</div><span>Camera</span></button>
    <button class="app" data-go="photos"><div class="icon">🖼</div><span>Photos</span></button>
    <button class="app" data-go="maps"><div class="icon">🗺</div><span>Maps</span></button>
    <button class="app" data-go="notes"><div class="icon">📝</div><span>Notes</span></button>
    <button class="app" data-go="remind"><div class="icon">⏰</div><span>Remind</span></button>
    <button class="app" data-go="list"><div class="icon">☑</div><span>List</span></button>
    <a class="app" href="/studio/voice"><div class="icon">🎙</div><span>Voice</span></a>
    <a class="app" href="sms:"><div class="icon">✉️</div><span>Messages</span></a>
    <a class="app" href="tel:"><div class="icon">📞</div><span>Phone</span></a>
    <a class="app" href="/imagine"><div class="icon">✨</div><span>Imagine</span></a>
    <a class="app" href="/phoneai/work"><div class="icon">✦</div><span>Code desk</span></a>
    <a class="app" href="/phoneai/anti"><div class="icon">🪐</div><span>Anti</span></a>
    <a class="app" href="/phoneai/portal"><div class="icon">🖥</div><span>Portal</span></a>
    <a class="app" href="/phoneai/glasses"><div class="icon">👓</div><span>Glasses</span></a>
    <a class="app" href="/phoneai/web"><div class="icon">🌐</div><span>Web live</span></a>
    <a class="app" href="/phoneai/runtime"><div class="icon">⏻</div><span>Runtime</span></a>
    <button class="app" data-go="settings"><div class="icon">⚙</div><span>Settings</span></button>
  </div>
  <p class="more">Portal is the live PC stream (watch + touch). Anti is the Antigravity desktop app. They are separate. <a href="/phoneai">Website</a> · <a href="/setup">Setup</a> · <a href="/login">Seat</a></p>
</section>

<section class="view" id="v-chat">
  <div class="hero"><h1>Chat</h1><p class="lead">Grok on this PC. Reminders, texts, maps, or just ask.</p></div>
  <div class="log" id="clog"></div>
  <form class="form" id="cf"><textarea id="ct" placeholder="Remind me, draft a text, where is…" rows="1"></textarea><button>Send</button></form>
</section>

<section class="view" id="v-camera">
  <div class="hero"><h1>Camera</h1><p class="lead">Snap a photo. It lands in Photos and the sovereign explorer.</p></div>
  <div style="padding:0 14px"><video id="vid" autoplay playsinline></video><canvas id="cv" hidden></canvas></div>
  <div class="form"><button class="go" type="button" id="snap">Shutter</button><button class="go" type="button" data-go="photos" style="background:#222;color:#fff">Photos</button></div>
</section>

<section class="view" id="v-photos">
  <div class="hero"><h1>Photos</h1></div>
  <div class="gallery" id="gal"></div>
</section>

<section class="view" id="v-maps">
  <div class="hero"><h1>Maps</h1><p class="lead">Opens Google Maps on the phone.</p></div>
  <form class="form" id="mf"><input id="mq" placeholder="Coffee near me, 123 Main…"/><button>Go</button></form>
  <div class="form"><button class="go" type="button" id="here">Use my location</button></div>
</section>

<section class="view" id="v-notes">
  <div class="hero"><h1>Notes</h1></div>
  <form class="form" id="nf"><input id="nt" placeholder="Quick note"/><button>Save</button></form>
  <div id="nl"></div>
</section>

<section class="view" id="v-remind">
  <div class="hero"><h1>Reminders</h1></div>
  <form class="form" id="rf"><input id="rt" placeholder="Remind me to…"/><button>Set</button></form>
  <div id="rl"></div>
</section>

<section class="view" id="v-list">
  <div class="hero"><h1>List</h1></div>
  <form class="form" id="lf"><input id="lt" placeholder="Milk, charger…"/><button>Add</button></form>
  <div id="ll"></div>
</section>

<section class="view" id="v-settings">
  <div class="hero"><h1>Settings</h1><p class="lead">Main chat is Grok. Toggle extra CLIs for the code desk.</p></div>
  <div id="srows"></div>
</section>

<nav class="dock">
  <button class="app" data-go="home"><div class="icon">▦</div><span>Home</span></button>
  <button class="app" data-go="chat"><div class="icon">💬</div><span>Chat</span></button>
  <a class="app" href="/phoneai/work"><div class="icon">✦</div><span>Desk</span></a>
  <a class="app" href="/phoneai/anti"><div class="icon">🪐</div><span>Anti</span></a>
  <a class="app" href="/phoneai/portal"><div class="icon">🖥</div><span>PC</span></a>
  <button class="app" data-go="settings"><div class="icon">⚙</div><span>Set</span></button>
</nav>
<script>
function tick(){document.getElementById('clk').textContent=new Date().toTimeString().slice(0,5)}
tick();setInterval(tick,30000);
function show(id){
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on', v.id==='v-'+id));
  location.hash=id==='home'?'':id;
  if(id==='camera') cam();
  if(id==='photos'||id==='notes'||id==='remind'||id==='list') life();
  if(id==='settings') settings();
}
document.body.addEventListener('click',e=>{
  const b=e.target.closest('[data-go]'); if(!b) return;
  const pre=b.getAttribute('data-pre'); if(pre){ document.getElementById('ct').value=pre; }
  show(b.getAttribute('data-go'));
});
if(location.hash) show(location.hash.replace('#',''));
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function add(log, who, text){
  const d=document.createElement('div'); d.className='m'+(who==='me'?' me':'');
  d.innerHTML='<div class="b"></div>'; d.querySelector('.b').textContent=text; log.appendChild(d); log.scrollTop=log.scrollHeight;
}
async function sendLife(kind,text,extra){
  const r=await fetch('/v1/phoneai/life',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,text,extra})});
  return r.json();
}
document.getElementById('cf').onsubmit=async ev=>{
  ev.preventDefault(); const t=document.getElementById('ct'); const text=(t.value||'').trim(); if(!text) return;
  t.value=''; const log=document.getElementById('clog'); add(log,'me',text); add(log,'bot','…');
  try{
    const j=await sendLife('auto',text);
    log.lastChild.querySelector('.b').textContent=j.reply||j.error||'ok';
    if(j.open && j.open.indexOf('http')===0){ const a=document.createElement('a'); a.href=j.open; a.textContent=' Open'; a.style.color='#58a6ff'; log.lastChild.querySelector('.b').appendChild(a); }
  }catch(e){ log.lastChild.querySelector('.b').textContent='Host unreachable. Keep the PC awake on this Wi-Fi.'; }
};
document.getElementById('nf').onsubmit=async ev=>{ev.preventDefault(); const t=document.getElementById('nt'); await sendLife('note',t.value); t.value=''; life();};
document.getElementById('rf').onsubmit=async ev=>{ev.preventDefault(); const t=document.getElementById('rt'); await sendLife('remind',t.value); t.value=''; life();};
document.getElementById('lf').onsubmit=async ev=>{ev.preventDefault(); const t=document.getElementById('lt'); await sendLife('list',t.value); t.value=''; life();};
document.getElementById('mf').onsubmit=async ev=>{
  ev.preventDefault(); const q=document.getElementById('mq').value; const j=await sendLife('maps',q); if(j.open) location.href=j.open;
};
document.getElementById('here').onclick=()=>{
  navigator.geolocation.getCurrentPosition(p=>{
    location.href='https://maps.google.com/?q='+p.coords.latitude+','+p.coords.longitude;
  },()=>alert('Location permission needed'));
};
let stream;
async function cam(){
  try{ stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false}); document.getElementById('vid').srcObject=stream; }catch(e){}
}
document.getElementById('snap').onclick=async()=>{
  const v=document.getElementById('vid'), c=document.getElementById('cv');
  c.width=v.videoWidth||720; c.height=v.videoHeight||960;
  c.getContext('2d').drawImage(v,0,0); const img=c.toDataURL('image/jpeg',0.85);
  const j=await sendLife('camera','photo',{image:img});
  alert(j.reply||j.error||'saved'); show('photos');
};
async function life(){
  const j=await fetch('/v1/phoneai/life').then(r=>r.json());
  document.getElementById('nl').innerHTML=(j.notes||[]).map(n=>'<div class="item">'+esc(n.text)+'<small>note</small></div>').join('')||'<div class="item">No notes yet</div>';
  document.getElementById('rl').innerHTML=(j.reminders||[]).map(n=>'<div class="item">'+esc(n.text)+'<small>reminder</small></div>').join('')||'<div class="item">Nothing due</div>';
  document.getElementById('ll').innerHTML=(j.list||[]).map(n=>'<div class="item">'+esc(n.text)+'</div>').join('')||'<div class="item">List is empty</div>';
  document.getElementById('gal').innerHTML=(j.photos||[]).map(p=>'<img src="'+esc(p.url)+'"/>').join('')||'<div class="item">No photos yet</div>';
}
life().catch(()=>{});
async function settings(){
  const j=await fetch('/v1/phoneai/settings').then(r=>r.json());
  const box=document.getElementById('srows');
  box.innerHTML=(j.tools||[]).map(t=>{
    const on=t.enabled?'on':'';
    const st=t.available?'ready':(t.can_make_now?'install now':'later');
    return '<div class="item"><b>'+esc(t.label)+'</b><small>'+esc(t.id)+' · '+st+'</small>'
      +(t.optional?'<div class="form" style="border:0;padding:8px 0"><button class="go" type="button" data-cli="'+esc(t.id)+'" data-on="'+(t.enabled?0:1)+'">'+(t.enabled?'On':'Off')+'</button>'
        +(t.available?'':'<button class="go" type="button" data-inst="'+esc(t.id)+'" style="background:#222;color:#fff">Install</button>')+'</div>':'')
      +'</div>';
  }).join('')+'<p class="more">'+esc(j.note||'')+'</p>'
    +'<div class="item"><b>Always-on host</b><small>Agents can bring :8787 up</small>'
    +'<div class="form" style="border:0;padding:8px 0"><button class="go" type="button" id="rt-up">Bring up</button>'
    +'<a class="go" href="/phoneai/runtime" style="display:inline-grid;place-items:center;background:#222;color:#fff;text-decoration:none">Runtime</a>'
    +'<a class="go" href="/setup" style="display:inline-grid;place-items:center;background:#222;color:#fff;text-decoration:none">Setup</a></div></div>';
}
document.getElementById('srows').addEventListener('click', async e=>{
  if(e.target && e.target.id==='rt-up'){
    await fetch('/v1/runtime/ensure',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"which":"all"}'});
    settings();
    return;
  }
  const b=e.target.closest('[data-cli],[data-inst]'); if(!b) return;
  const id=b.getAttribute('data-cli')||b.getAttribute('data-inst');
  const body=b.hasAttribute('data-inst')?{id,install:true}:{id,enabled:b.getAttribute('data-on')==='1'};
  await fetch('/v1/phoneai/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  settings();
});
</script>
</body></html>
"""


def phoneai_os_html() -> str:
    return PHONEAI_OS_HTML


PHONEAI_TWIN_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="theme-color" content="#07070b"/>
<title>PhoneAI Code desk</title>
<style>
:root{--bg:#07070b;--panel:#141418;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#10a37f;--c:#58a6ff}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{display:flex;flex-direction:column;max-width:480px;margin:0 auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.top{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line)}
.top a{color:var(--muted);text-decoration:none;font-size:13px}
.engines{display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px}
.engines button{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:999px;padding:8px 10px;font-weight:700;font-size:11px}
.engines button.on{color:#042f24;background:var(--g);border-color:transparent}
.log{flex:1;overflow:auto;padding:12px 14px}
.m{margin:0 0 12px;max-width:92%}
.m.me{margin-left:auto}
.m .b{padding:10px 12px;border-radius:14px;background:var(--panel);line-height:1.45;font-size:14px;white-space:pre-wrap}
.m.me .b{background:#0b3d32;color:#d1fae5}
.m img{max-width:100%;border-radius:12px;margin-top:8px;display:block}
.eng{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--c);margin:0 0 4px}
.form{display:flex;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));border-top:1px solid var(--line)}
.form textarea{flex:1;min-height:44px;max-height:120px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);padding:10px;font:inherit}
.form button{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px}
</style></head>
<body>
<div class="top"><a href="/phoneai">Home</a><b style="flex:1">Code desk</b><a href="/phoneai/anti">Anti</a></div>
<div id="now" style="padding:8px 14px;font-size:12px;color:#a1a1aa;border-bottom:1px solid var(--line)">Loading your live Grok/Codex/Antigravity threads…</div>
<div style="display:flex;gap:8px;padding:8px 12px;flex-wrap:wrap">
<select id="thr" style="flex:1;min-width:140px;padding:8px;border-radius:10px;background:#0c0c0e;color:#fafafa;border:1px solid var(--line)"></select>
<select id="per" style="padding:8px;border-radius:10px;background:#0c0c0e;color:#fafafa;border:1px solid var(--line)"></select>
<button type="button" id="ns" style="border:0;border-radius:10px;background:#10a37f;color:#042;font-weight:800;padding:8px 12px">New session</button>
</div>
<div class="engines" id="eng"></div>
<div class="log" id="log"></div>
<form class="form" id="f">
  <textarea id="t" placeholder="Work from the phone…" rows="1"></textarea>
  <button type="submit">Send</button>
</form>
<form class="form" id="sh" style="border-top:0">
  <input id="sc" placeholder="Shell (pytest, python, git)…" style="flex:1;min-height:44px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:10px;font:inherit"/>
  <button type="submit" style="background:#222;color:#fff">Harness</button>
</form>
<script>
let engine='grok';
let threadId='';
const LABELS={auto:'Auto',grok:'Grok',codex:'Codex',claude:'Claude',gemini:'Gemini',qwen:'Qwen',spark:'Glimmer',opencode:'OpenCode',cursor:'Cursor',aider:'Aider',copilot:'Copilot',antigravity:'Anti',auro:'Auro',ghost:'Ghost',logic:'Logic',portal:'Portal'};
fetch('/v1/engines').then(r=>r.json()).then(cat=>{
  const desk=cat.desk||[];
  const fast=cat.phone_fast||[];
  const ids=['auto',...desk.filter(x=>x!=='spark'),...fast.slice(0,4),'antigravity','portal'];
  const uniq=[...new Set(ids)];
  document.getElementById('eng').innerHTML=uniq.map(i=>'<button type="button" data-e="'+i+'"'+(i===engine?' class="on"':'')+'>'+(LABELS[i]||i)+'</button>').join('');
}).catch(()=>{ document.getElementById('eng').innerHTML='<button type="button" data-e="auto" class="on">Auto</button><button type="button" data-e="codex">Codex</button><button type="button" data-e="claude">Claude</button><button type="button" data-e="antigravity">Anti</button>'; });
fetch('/v1/phoneai/sessions').then(r=>r.json()).then(s=>{
  const per=document.getElementById('per');
  per.innerHTML=(s.personas||[]).map(p=>'<option value="'+p.id+'">'+p.id+' · '+(p.blurb||p.mode)+'</option>').join('');
}).catch(()=>{});
document.getElementById('ns').onclick=async()=>{
  const persona=document.getElementById('per').value||'researcher';
  const j=await fetch('/v1/phoneai/sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({persona,kind:'both',title:'PhoneAI '+persona})}).then(r=>r.json());
  const id=(j.pocket_session&&j.pocket_session.id)||(j.phoneai_session&&j.phoneai_session.id)||'';
  if(id){ threadId=id; document.getElementById('now').textContent='New session '+id+' · '+persona; }
  else alert(j.error||'could not create session');
};
fetch('/v1/phoneai/desk').then(r=>r.json()).then(d=>{
  const live=d.you_are_working_on||{};
  threadId=live.id||'';
  const now=document.getElementById('now');
  now.textContent=live.title
    ? ('You are working on: '+live.title+' · '+(live.engine||'')+' · '+(live.cwd||''))
    : 'No live threads found.';
  const sel=document.getElementById('thr');
  const all=[...(d.grok||[]),...(d.codex||[]),...(d.antigravity_threads||[])];
  sel.innerHTML=all.map(t=>'<option value="'+t.id+'" data-e="'+t.engine+'">'+t.engine+' · '+(t.title||t.id).slice(0,70)+'</option>').join('');
  if(threadId) sel.value=threadId;
  sel.onchange=()=>{ threadId=sel.value; const o=sel.selectedOptions[0]; if(o) now.textContent='Attached: '+o.textContent; };
  add('bot', now.textContent, 'desk');
}).catch(()=>add('bot','Could not load live desk. Is Pocket up?','err'));
document.getElementById('eng').onclick=e=>{
  const b=e.target.closest('button'); if(!b) return;
  engine=b.getAttribute('data-e');
  [...document.getElementById('eng').children].forEach(x=>x.classList.toggle('on',x===b));
};
const log=document.getElementById('log');
function add(who, text, eng){
  const d=document.createElement('div');
  d.className='m'+(who==='me'?' me':'');
  d.innerHTML='<div class="eng">'+(eng||who)+'</div><div class="b"></div>';
  d.querySelector('.b').textContent=text;
  log.appendChild(d); log.scrollTop=log.scrollHeight;
  return d;
}
document.getElementById('sh').onsubmit=async ev=>{
  ev.preventDefault();
  const cmd=document.getElementById('sc').value.trim();
  const text=(document.getElementById('t').value||'').trim();
  if(!cmd && !text) return;
  add('me', (cmd?('$ '+cmd+'\n'):'')+text, 'harness');
  add('bot','Harness…', 'harness');
  try{
    const j=await fetch('/v1/phoneai/harness',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({goal:text||cmd,shell:cmd,engine})}).then(r=>r.json());
    log.lastChild.remove();
    const out=(j.reply||(j.shell&&j.shell.stdout)||j.error||'done');
    add('bot', out, (j.engine&&j.engine.engine)||'harness');
  }catch(e){ log.lastChild.remove(); add('bot','Harness unreachable','err'); }
};
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault();
  const t=document.getElementById('t');
  const text=(t.value||'').trim(); if(!text) return;
  t.value=''; add('me', text, 'you');
  add('bot','Working…', engine);
  try{
    const r=await fetch('/v1/phoneai/work/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,engine,thread_id:threadId})});
    if(!r.ok || !r.body){
      const j=await fetch('/v1/phoneai/work',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,engine,thread_id:threadId})}).then(x=>x.json());
      log.lastChild.remove();
      const n=add('bot', j.reply||j.error||'no reply', j.engine||engine);
      if(j.image_url){ const img=document.createElement('img'); img.src=j.image_url; n.querySelector('.b').appendChild(img); }
      return;
    }
    const reader=r.body.getReader(); const dec=new TextDecoder();
    let buf='', reply='', eng=engine, last=log.lastChild, imageUrl='';
    last.querySelector('.b').textContent='';
    while(true){
      const {done,value}=await reader.read(); if(done) break;
      buf+=dec.decode(value,{stream:true});
      const parts=buf.split('\n\n'); buf=parts.pop()||'';
      for(const block of parts){
        const ev=(block.match(/^event:\s*(.+)$/m)||[])[1]||'';
        const data=(block.match(/^data:\s*([\s\S]+)$/m)||[])[1]||'';
        if(ev==='token'){ reply+=data; last.querySelector('.b').textContent=reply; log.scrollTop=log.scrollHeight; }
        if(ev==='done'){
          try{ const j=JSON.parse(data); eng=j.engine||eng; if(j.image_url) imageUrl=j.image_url; if(!reply) reply=j.reply||j.error||''; }catch(_){}
        }
      }
    }
    last.querySelector('.eng').textContent=eng;
    last.querySelector('.b').textContent=reply||'no reply';
    if(imageUrl){ const img=document.createElement('img'); img.src=imageUrl; last.querySelector('.b').appendChild(img); }
  }catch(e){
    log.lastChild.remove();
    add('bot','Cannot reach POCKET host. Keep the PC awake on this Wi-Fi.','err');
  }
};
</script>
</body></html>
"""


def phoneai_twin_html() -> str:
    return PHONEAI_TWIN_HTML


PHONEAI_ANTI_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="theme-color" content="#05060a"/>
<title>Antigravity · PhoneAI</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86;--p:#14141c}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{display:flex;flex-direction:column;max-width:480px;margin:0 auto;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.top{display:flex;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--line)}
.top a{color:var(--muted);text-decoration:none}
.now{padding:10px 14px 6px;font-size:13px;color:#a1a1aa}
.now b{color:var(--fg);display:block;font-size:16px;margin-bottom:4px}
.chips{display:flex;gap:8px;overflow:auto;padding:0 12px 10px}
.chips button{flex:0 0 auto;border:1px solid var(--line);background:var(--p);color:var(--fg);border-radius:999px;padding:8px 12px;font-size:12px}
.chips button.on{border-color:var(--g);color:#042;background:var(--g)}
.view{margin:0 12px;border-radius:14px;overflow:hidden;background:#000;min-height:220px;border:1px solid var(--line);flex:1}
.view img{width:100%;display:block;min-height:220px;object-fit:contain;background:#000}
.row{display:flex;gap:8px;padding:10px 12px;flex-wrap:wrap}
.row button{flex:1;min-height:44px;border:0;border-radius:12px;background:#1c1c24;color:#fff;font-weight:700}
.row button.g{background:var(--g);color:#042}
.form{display:flex;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom))}
textarea{flex:1;min-height:48px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:10px;font:inherit}
.form button{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px}
</style></head>
<body>
<div class="top"><a href="/phoneai">Home</a><b style="flex:1">Antigravity</b><a href="/phoneai/portal">Portal</a></div>
<div class="now" id="now"><b>Antigravity desktop app</b>Named threads, send, continue. The PC stream is Portal — a separate first-class surface.</div>
<div class="chips" id="chips"></div>
<img id="frame" alt="Antigravity" src="/v1/phoneai/anti/frame?t=1" style="width:calc(100% - 24px);margin:0 12px 8px;border-radius:14px;background:#000;touch-action:none;max-height:42vh;object-fit:contain"/>
<div class="row">
  <button type="button" id="o">Open app</button>
  <button type="button" id="touch" class="g">Touch</button>
  <button type="button" id="n">New chat</button>
  <button type="button" id="c">Continue</button>
</div>
<form class="form" id="f"><textarea id="t" placeholder="Type into the real Antigravity chat…"></textarea><button>Send</button></form>
<script>
const now=document.getElementById('now');
const chips=document.getElementById('chips');
const frame=document.getElementById('frame');
let mode='watch', down=false, busy=false, lastDrag=0;
async function anti(action,text){
  const r=await fetch('/v1/phoneai/anti',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,text})});
  return r.json();
}
function paint(j){
  const y=j.you_are_building||{};
  const title=y.title||j.title||'Antigravity';
  const cwd=y.cwd||j.cwd||'';
  now.innerHTML='<b>'+title.replace(/</g,'')+'</b>'+(cwd?cwd+' · ':'')+'Attached to the Antigravity desktop app. Touch maps onto that window.';
  const th=j.threads||[];
  chips.innerHTML=th.map(t=>'<button type="button" data-id="'+t.id+'">'+(t.title||t.app||t.id).slice(0,42)+'</button>').join('');
}
fetch('/v1/phoneai/anti').then(r=>r.json()).then(paint).catch(()=>{ now.innerHTML='<b>Host unreachable</b>'; });
function tick(){
  if(document.hidden || busy){ setTimeout(tick, 500); return; }
  busy=true;
  const done=()=>{ busy=false; setTimeout(tick, 900); };
  frame.onload=done; frame.onerror=done;
  frame.src='/v1/phoneai/anti/frame?t='+Date.now();
}
tick();
function clamp(v){return Math.max(0,Math.min(1,v))}
function norm(ev){
  const r=frame.getBoundingClientRect();
  const src=ev.touches&&ev.touches[0]?ev.touches[0]:(ev.changedTouches&&ev.changedTouches[0]?ev.changedTouches[0]:ev);
  return {nx:clamp((src.clientX-r.left)/Math.max(1,r.width)), ny:clamp((src.clientY-r.top)/Math.max(1,r.height))};
}
function sendTouch(kind, nx, ny, extra){
  if(mode!=='touch' && kind!=='type') return;
  fetch('/v1/phoneai/anti/touch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({kind,nx,ny}, extra||{}))}).catch(()=>{});
}
document.getElementById('touch').onclick=()=>{
  mode=mode==='touch'?'watch':'touch';
  document.getElementById('touch').textContent=mode==='touch'?'Touch on':'Touch';
  document.getElementById('touch').classList.toggle('g', mode==='touch');
};
let gest=null, startAt=null, longTimer=null;
frame.addEventListener('pointerdown', ev=>{
  if(mode!=='touch') return; ev.preventDefault(); down=true;
  const p=norm(ev); startAt={x:ev.clientX,y:ev.clientY,nx:p.nx,ny:p.ny}; gest='pending';
  longTimer=setTimeout(()=>{ if(gest==='pending'){ gest='right'; sendTouch('right', startAt.nx, startAt.ny); } }, 480);
}, {passive:false});
frame.addEventListener('pointermove', ev=>{
  if(!down||mode!=='touch') return; ev.preventDefault();
  const p=norm(ev);
  if(gest==='pending' && startAt && Math.hypot(ev.clientX-startAt.x, ev.clientY-startAt.y)>14){
    if(longTimer) clearTimeout(longTimer); gest='drag'; sendTouch('down', startAt.nx, startAt.ny); sendTouch('drag', p.nx, p.ny);
  } else if(gest==='drag'){
    const n=Date.now(); if(n-lastDrag<32) return; lastDrag=n; sendTouch('drag', p.nx, p.ny);
  }
}, {passive:false});
frame.addEventListener('pointerup', ev=>{
  if(mode!=='touch') return; ev.preventDefault();
  if(longTimer) clearTimeout(longTimer);
  const p=norm(ev);
  if(gest==='pending') sendTouch('tap', p.nx, p.ny);
  else if(gest==='drag') sendTouch('up', p.nx, p.ny);
  down=false; gest=null;
}, {passive:false});
frame.addEventListener('contextmenu', ev=>{ ev.preventDefault(); if(mode==='touch'){ const p=norm(ev); sendTouch('right', p.nx, p.ny);} });
setInterval(()=>{ if(!document.hidden) fetch('/v1/phoneai/anti').then(r=>r.json()).then(paint).catch(()=>{}); }, 12000);
document.getElementById('o').onclick=()=>anti('open','');
document.getElementById('n').onclick=async()=>{ paint(await anti('new','')); };
document.getElementById('c').onclick=async()=>{ paint(await anti('continue','')); };
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault(); const t=document.getElementById('t'); const text=t.value.trim(); if(!text) return;
  if(mode==='touch'){ sendTouch('key', 0.5, 0.85, {text}); sendTouch('key', 0.5, 0.85, {vk:13}); t.value=''; return; }
  t.value=''; await anti('send',text); paint(await fetch('/v1/phoneai/anti').then(r=>r.json()));
};
</script>
</body></html>
"""


def phoneai_anti_html() -> str:
    return PHONEAI_ANTI_HTML


PHONEAI_PORTAL_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="theme-color" content="#05060a"/>
<title>Portal · PhoneAI</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.12);--g:#00ff86}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0;background:#000;color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif;overflow:hidden;touch-action:none}
body{display:flex;flex-direction:column;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.top{display:flex;align-items:center;gap:8px;padding:8px 10px;background:#05060a;border-bottom:1px solid var(--line);flex-wrap:wrap}
.top a{color:var(--muted);text-decoration:none;font-size:13px}
.top b{flex:1}
.seg{display:flex;border:1px solid var(--line);border-radius:999px;overflow:hidden}
.seg button{border:0;background:transparent;color:var(--muted);padding:8px 12px;font-weight:800;font-size:12px}
.seg button.on{background:var(--g);color:#042}
.stage{flex:1;position:relative;background:#000;min-height:0;overflow:hidden;touch-action:none}
.view{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;transform-origin:0 0;will-change:transform}
.view img{max-width:100%;max-height:100%;width:auto;height:auto;touch-action:none;user-select:none;-webkit-user-drag:none}
.dot{position:absolute;width:22px;height:22px;border-radius:50%;border:2px solid #00ff86;pointer-events:none;transform:translate(-50%,-50%);display:none;z-index:4}
.joy{position:absolute;left:10px;bottom:10px;width:92px;height:92px;border-radius:50%;border:1px solid var(--line);background:rgba(8,10,18,.62);z-index:6;touch-action:none}
.knob{position:absolute;left:50%;top:50%;width:38px;height:38px;margin:-19px 0 0 -19px;border-radius:50%;background:var(--g);pointer-events:none}
.btns{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:8px;z-index:6}
.btns button{width:48px;height:48px;border-radius:50%;border:1px solid var(--line);background:rgba(20,20,28,.85);color:#fff;font-weight:800}
.btns button.held{background:var(--g);color:#042}
.bar{display:flex;gap:8px;padding:8px 10px;background:#05060a;border-top:1px solid var(--line)}
.bar input{flex:1;min-height:44px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:10px;font:inherit}
.bar button{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px}
.hint{position:absolute;left:108px;right:68px;bottom:12px;font-size:11px;color:#a1a1aa;background:rgba(0,0,0,.55);padding:6px 8px;border-radius:8px;pointer-events:none;z-index:5}
</style></head>
<body>
<div class="top">
  <a href="/phoneai/app">Home</a>
  <b>Portal</b>
  <div class="seg" id="mode">
    <button type="button" data-m="watch" class="on">Watch</button>
    <button type="button" data-m="touch">Touch</button>
  </div>
</div>
<div class="stage" id="stage">
  <div class="view" id="view">
    <img id="frame" alt="PC" src="/v1/phoneai/portal/frame?target=desktop&t=1" draggable="false"/>
  </div>
  <div class="dot" id="dot"></div>
  <div class="joy" id="joy"><div class="knob" id="knob"></div></div>
  <div class="btns">
    <button type="button" id="lmb">L</button>
    <button type="button" id="rmb">R</button>
  </div>
  <div class="hint" id="hint">Pinch zooms the phone only. Tap · hold=right · drag=drop. Stick is the mouse.</div>
</div>
<form class="bar" id="kb">
  <input id="keys" placeholder="Tap a field, then type here — live on the PC" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="enter"/>
  <button>Enter</button>
</form>
<script>
let mode='watch', target='desktop', busy=false;
let zoom=1, panX=0, panY=0;
let lastNx=0.5, lastNy=0.5, lastDrag=0, lastTyped='';
const img=document.getElementById('frame');
const view=document.getElementById('view');
const stage=document.getElementById('stage');
const dot=document.getElementById('dot');
const hint=document.getElementById('hint');
const keys=document.getElementById('keys');
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function applyView(){
  if(zoom<=1.02){ zoom=1; panX=0; panY=0; }
  const s=stage.getBoundingClientRect();
  panX=clamp(panX, s.width*(1-zoom), 0);
  panY=clamp(panY, s.height*(1-zoom), 0);
  view.style.transform='translate('+panX+'px,'+panY+'px) scale('+zoom+')';
}
function ptFrom(src){
  const r=img.getBoundingClientRect();
  const w=r.width||1, h=r.height||1;
  const nx=clamp((src.clientX-r.left)/w,0,1), ny=clamp((src.clientY-r.top)/h,0,1);
  lastNx=nx; lastNy=ny;
  return {nx, ny, cx:src.clientX, cy:src.clientY};
}
function showDot(cx,cy){ const s=stage.getBoundingClientRect(); dot.style.display='block'; dot.style.left=(cx-s.left)+'px'; dot.style.top=(cy-s.top)+'px'; }
function send(kind, nx, ny, extra){
  if(mode!=='touch' && kind!=='type' && kind!=='key') return;
  fetch('/v1/phoneai/portal/touch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({kind,nx,ny,target}, extra||{}))}).catch(()=>{});
}
function tick(){
  if(document.hidden || busy){ setTimeout(tick, 400); return; }
  busy=true;
  const done=()=>{ busy=false; setTimeout(tick, 280); };
  img.onload=done; img.onerror=done;
  img.src='/v1/phoneai/portal/frame?target='+encodeURIComponent(target)+'&t='+Date.now();
}
tick();
document.getElementById('mode').onclick=e=>{
  const b=e.target.closest('button'); if(!b) return;
  mode=b.getAttribute('data-m');
  [...document.getElementById('mode').children].forEach(x=>x.classList.toggle('on',x===b));
  hint.textContent=mode==='touch'?'Touch on. Pinch=phone zoom (PC stays 1:1). Hold L + stick = drag.':'Watch. Open on the phone so it does not film itself.';
  if(mode==='touch') setTimeout(()=>keys.focus(), 50);
};
const fingers=new Map();
let gest=null, longTimer=null, pinch=null, startAt=null;
function clearLong(){ if(longTimer){ clearTimeout(longTimer); longTimer=null; } }
stage.addEventListener('pointerdown', ev=>{
  if(ev.target.closest('.joy,.btns,.bar')) return;
  ev.preventDefault();
  stage.setPointerCapture(ev.pointerId);
  fingers.set(ev.pointerId, {x:ev.clientX, y:ev.clientY});
  if(fingers.size>=2){
    clearLong(); gest='pinch';
    const pts=[...fingers.values()];
    pinch={d:Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y)||1, z:zoom, px:panX, py:panY, mx:(pts[0].x+pts[1].x)/2, my:(pts[0].y+pts[1].y)/2};
    return;
  }
  if(mode!=='touch') return;
  const p=ptFrom(ev); showDot(p.cx,p.cy);
  startAt={x:ev.clientX, y:ev.clientY, nx:p.nx, ny:p.ny};
  gest='pending';
  longTimer=setTimeout(()=>{
    if(gest==='pending'){ gest='right'; send('right', startAt.nx, startAt.ny); hint.textContent='Right-click'; }
  }, 480);
}, {passive:false});
stage.addEventListener('pointermove', ev=>{
  if(!fingers.has(ev.pointerId)) return;
  ev.preventDefault();
  fingers.set(ev.pointerId, {x:ev.clientX, y:ev.clientY});
  if(fingers.size>=2 && pinch){
    const pts=[...fingers.values()];
    const d=Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y)||1;
    const mx=(pts[0].x+pts[1].x)/2, my=(pts[0].y+pts[1].y)/2;
    const nz=clamp(pinch.z*(d/pinch.d), 1, 5);
    const cx=(pinch.mx-pinch.px)/pinch.z, cy=(pinch.my-pinch.py)/pinch.z;
    zoom=nz; panX=mx-cx*nz; panY=my-cy*nz; applyView();
    return;
  }
  if(mode!=='touch') return;
  const p=ptFrom(ev); showDot(p.cx,p.cy);
  if(gest==='pending' && startAt && Math.hypot(ev.clientX-startAt.x, ev.clientY-startAt.y)>14){
    clearLong(); gest='drag';
    send('down', startAt.nx, startAt.ny, {button:'left'});
    send('drag', p.nx, p.ny);
  } else if(gest==='drag'){
    const now=Date.now(); if(now-lastDrag<32) return; lastDrag=now;
    send('drag', p.nx, p.ny);
  }
}, {passive:false});
function endPtr(ev){
  fingers.delete(ev.pointerId);
  if(fingers.size<2) pinch=null;
  if(mode!=='touch'){ if(!fingers.size) gest=null; return; }
  const p=ptFrom(ev);
  clearLong();
  if(gest==='pending'){ send('tap', p.nx, p.ny); setTimeout(()=>keys.focus(), 20); }
  else if(gest==='drag') send('up', p.nx, p.ny, {button:'left'});
  if(!fingers.size){ gest=null; startAt=null; setTimeout(()=>dot.style.display='none', 220); }
}
stage.addEventListener('pointerup', endPtr);
stage.addEventListener('pointercancel', endPtr);
stage.addEventListener('contextmenu', ev=>{ ev.preventDefault(); if(mode!=='touch') return; const p=ptFrom(ev); send('right', p.nx, p.ny); });
stage.addEventListener('wheel', ev=>{
  ev.preventDefault();
  if(ev.ctrlKey || ev.metaKey){
    const z0=zoom, nz=clamp(zoom*(ev.deltaY<0?1.12:0.9),1,5);
    const s=stage.getBoundingClientRect();
    const cx=ev.clientX-s.left, cy=ev.clientY-s.top;
    const ox=(cx-panX)/z0, oy=(cy-panY)/z0;
    zoom=nz; panX=cx-ox*nz; panY=cy-oy*nz; applyView();
    return;
  }
  if(mode==='touch'){ const p=ptFrom(ev); send('scroll', p.nx, p.ny, {dy: ev.deltaY/400}); }
}, {passive:false});
img.addEventListener('dblclick', ev=>{
  ev.preventDefault();
  if(zoom>1.2){ zoom=1; panX=0; panY=0; }
  else { const s=stage.getBoundingClientRect(); const cx=ev.clientX-s.left, cy=ev.clientY-s.top; zoom=2.4; panX=cx-cx*zoom; panY=cy-cy*zoom; }
  applyView();
});

const joy=document.getElementById('joy'), knob=document.getElementById('knob');
let joyOn=false, joyDx=0, joyDy=0, joyLast=0;
function joyLoop(){
  if(!joyOn) return;
  const now=Date.now();
  if(now-joyLast>28 && (Math.abs(joyDx)>1 || Math.abs(joyDy)>1)){
    joyLast=now; send('joy', lastNx, lastNy, {dx:joyDx, dy:joyDy});
  }
  requestAnimationFrame(joyLoop);
}
joy.addEventListener('pointerdown', ev=>{
  if(mode!=='touch') return;
  ev.preventDefault(); ev.stopPropagation(); joy.setPointerCapture(ev.pointerId); joyOn=true; joyLoop();
}, {passive:false});
joy.addEventListener('pointermove', ev=>{
  if(!joyOn) return;
  ev.preventDefault();
  const r=joy.getBoundingClientRect();
  const x=clamp(ev.clientX-r.left-r.width/2, -36, 36);
  const y=clamp(ev.clientY-r.top-r.height/2, -36, 36);
  knob.style.transform='translate('+x+'px,'+y+'px)';
  joyDx=x*0.55; joyDy=y*0.55;
}, {passive:false});
function joyEnd(){ joyOn=false; joyDx=0; joyDy=0; knob.style.transform=''; }
joy.addEventListener('pointerup', joyEnd); joy.addEventListener('pointercancel', joyEnd);

const lmb=document.getElementById('lmb'), rmb=document.getElementById('rmb');
lmb.addEventListener('pointerdown', ev=>{
  if(mode!=='touch') return; ev.preventDefault(); ev.stopPropagation();
  lmb.classList.add('held'); send('down', lastNx, lastNy, {button:'left'});
}, {passive:false});
lmb.addEventListener('pointerup', ev=>{ lmb.classList.remove('held'); send('up', lastNx, lastNy, {button:'left'}); });
rmb.addEventListener('pointerdown', ev=>{
  if(mode!=='touch') return; ev.preventDefault(); ev.stopPropagation();
  rmb.classList.add('held'); send('down', lastNx, lastNy, {button:'right'});
}, {passive:false});
rmb.addEventListener('pointerup', ev=>{ rmb.classList.remove('held'); send('up', lastNx, lastNy, {button:'right'}); });
rmb.addEventListener('click', ev=>{ ev.preventDefault(); });

keys.addEventListener('input', ()=>{
  const v=keys.value; let i=0;
  while(i<v.length && i<lastTyped.length && v[i]===lastTyped[i]) i++;
  const back=lastTyped.length-i, add=v.slice(i);
  lastTyped=v;
  if(mode!=='touch') return;
  if(back) send('key', lastNx, lastNy, {vk:8, n:back});
  if(add) send('key', lastNx, lastNy, {text:add});
});
keys.addEventListener('keydown', ev=>{
  const map={Enter:13, Tab:9, Escape:27, ArrowLeft:37, ArrowUp:38, ArrowRight:39, ArrowDown:40, Delete:46};
  if(ev.key==='Enter'){
    ev.preventDefault();
    send('key', lastNx, lastNy, {vk:13});
    lastTyped=''; keys.value='';
  } else if(map[ev.key] && ev.key!=='Backspace'){
    ev.preventDefault();
    send('key', lastNx, lastNy, {vk:map[ev.key]});
  }
});
document.getElementById('kb').onsubmit=ev=>{ ev.preventDefault(); send('key', lastNx, lastNy, {vk:13}); lastTyped=''; keys.value=''; };
</script>
</body></html>
"""


def phoneai_portal_html() -> str:
    return PHONEAI_PORTAL_HTML


PHONEAI_GLASSES_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<title>PhoneAI Glasses</title>
<style>
html,body{margin:0;height:100%;background:#05060a;color:#f4f4f5;font-family:ui-sans-serif,system-ui}
body{display:flex;flex-direction:column}
.top{padding:8px 12px;display:flex;gap:10px;align-items:center}
.top a{color:#8b8b98;text-decoration:none}
img{width:100%;flex:1;object-fit:contain;background:#000;max-height:62vh}
.bar{display:flex;gap:8px;padding:10px}
input,button{min-height:44px;border-radius:12px;border:0;font:inherit}
input{flex:1;background:#14141c;color:#fff;padding:10px}
button{background:#00ff86;color:#042;font-weight:800;padding:0 14px}
.note{padding:0 12px 12px;color:#8b8b98;font-size:12px}
</style></head>
<body>
<div class="top"><a href="/phoneai">Home</a><b>Glasses HUD</b><a href="/phoneai/portal">Portal</a></div>
<img id="f" alt="stream" src="/v1/phoneai/portal/frame?t=1"/>
<form class="bar" id="v"><input id="t" placeholder="Voice → screen: click File, scroll down, open github.com…"/><button>Go</button></form>
<p class="note">Meta glasses / any HUD: open this URL in the glasses browser. Same Wi-Fi as the PC. Stream is one primary screen. Voice uses fusion + eyes.</p>
<script>
const img=document.getElementById('f'); let busy=false;
function tick(){ if(document.hidden||busy){ setTimeout(tick,600); return;} busy=true; img.onload=()=>{busy=false;setTimeout(tick,900)}; img.onerror=()=>{busy=false;setTimeout(tick,1200)}; img.src='/v1/phoneai/portal/frame?t='+Date.now(); }
tick();
document.getElementById('v').onsubmit=async ev=>{
  ev.preventDefault(); const t=document.getElementById('t'); const text=t.value.trim(); if(!text) return;
  await fetch('/v1/phoneai/voice-screen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
  t.value='';
};
</script>
</body></html>
"""


PHONEAI_WEB_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Live web · PhoneAI</title>
<style>
html,body{margin:0;height:100%;background:#05060a;color:#f4f4f5;font-family:ui-sans-serif,system-ui;display:flex;flex-direction:column}
.top{padding:10px 12px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.top a{color:#8b8b98;text-decoration:none}
form{display:flex;gap:8px;padding:0 12px 8px}
input,button{min-height:40px;border-radius:10px;border:0;font:inherit}
input{flex:1;background:#14141c;color:#fff;padding:8px}
button{background:#00ff86;color:#042;font-weight:800;padding:0 12px}
iframe{flex:1;border:0;background:#fff;margin:0 12px 12px;border-radius:12px;min-height:50vh}
.chips{display:flex;gap:8px;overflow:auto;padding:0 12px 8px}
.chips button{background:#14141c;color:#fff;flex:0 0 auto}
</style></head>
<body>
<div class="top"><a href="/phoneai">Home</a><b>Live web</b><a href="/phoneai/work">Desk</a></div>
<form id="f"><input id="u" placeholder="https://… or project preview id"/><button>Show</button><button type="button" id="pc">Open on PC</button></form>
<div class="chips" id="chips"></div>
<iframe id="v" title="live" src="about:blank"></iframe>
<script>
const v=document.getElementById('v');
function show(url){ v.src=url; }
document.getElementById('f').onsubmit=ev=>{
  ev.preventDefault(); let u=document.getElementById('u').value.trim(); if(!u) return;
  if(!u.startsWith('http') && !u.startsWith('/')) u='/v1/preview/'+u;
  show(u);
};
document.getElementById('pc').onclick=async()=>{
  const u=document.getElementById('u').value.trim(); if(!u) return;
  await fetch('/v1/phoneai/voice-screen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:'open '+u})});
};
fetch('/v1/preview').then(r=>r.json()).then(j=>{
  const items=j.previews||j.items||j.ids||[];
  const chips=document.getElementById('chips');
  chips.innerHTML=(Array.isArray(items)?items:[]).slice(0,12).map(p=>{
    const id=p.id||p; return '<button type="button" data-id="'+id+'">'+(p.title||id)+'</button>';
  }).join('') || '<span style="color:#8b8b98">No agent previews yet. Agents POST /v1/preview.</span>';
  chips.onclick=e=>{ const b=e.target.closest('[data-id]'); if(!b) return; show('/v1/preview/'+b.getAttribute('data-id')); };
}).catch(()=>{});
</script>
</body></html>
"""


def phoneai_glasses_html() -> str:
    return PHONEAI_GLASSES_HTML


def phoneai_web_html() -> str:
    return PHONEAI_WEB_HTML


def kernel_manifest() -> dict:
    from pocket.live_companion import status as live_status
    from pocket.phoneai_space import ensure_user_seat
    from pocket.tech_atlas import APPS

    seat = ensure_user_seat()
    return {
        "ok": True,
        "os": "PhoneAI Kernel",
        "version": "1.0.0",
        "landing": "/phoneai",
        "app": "/phoneai/app",
        "pocket": "http://127.0.0.1:8787",
        "seat": {"user": "phoneai", "ok": seat.get("ok"), "explorer": seat.get("explorer")},
        "companion": live_status(),
        "apps": APPS,
        "services": [
            "Pairing handshake",
            "Typed capabilities + NEXUS receipts",
            "POCKET Live (Gemini + atlas)",
            "Grok chat · camera · maps · notes · code desk · Antigravity",
            "Always-on runtime — agents bring the host up",
            "MCP · Agent Mail · Novae",
        ],
    }
