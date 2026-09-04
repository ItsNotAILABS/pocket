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
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="apple-mobile-web-app-title" content="PhoneAI Kernel"/>
<link rel="manifest" href="/phoneai/manifest.json"/>
<title>PhoneAI Kernel</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86;--c:#58a6ff;--p:#14141c}
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;height:100dvh;min-height:100svh;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:430px;margin:0 auto;display:flex;flex-direction:column;min-height:100dvh;padding:0;
  background:radial-gradient(700px 380px at 90% -8%,rgba(0,255,134,.1),transparent 50%),#05060a}
.status{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:calc(10px + env(safe-area-inset-top)) 16px 0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.status .pulse{display:inline-flex;align-items:center;gap:6px;letter-spacing:.08em}
.status .pulse b{width:7px;height:7px;border-radius:50%;background:#555;display:inline-block}
.status .pulse.on b{background:var(--g);box-shadow:0 0 8px var(--g)}
.layers{display:flex;gap:8px;padding:10px 16px 0}
.layers a,.layers button{flex:1;text-align:center;padding:9px;border-radius:14px;border:1px solid var(--line);color:var(--fg);text-decoration:none;font-weight:800;font-size:13px;background:transparent}
.layers a.on,.layers button.on{background:var(--g);color:#042;border-color:var(--g)}
.find{margin:10px 16px 0;width:calc(100% - 32px);min-height:42px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);padding:10px 12px;font:inherit}
.pills{display:flex;gap:6px;padding:8px 16px 0;overflow:auto}
.pills i{flex:0 0 auto;font-style:normal;font-size:11px;border:1px solid var(--line);border-radius:999px;padding:5px 9px;color:var(--muted)}
.pills i.on{color:#042;background:var(--g);border-color:var(--g)}
.sec{padding:14px 16px 0;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.view{display:none;flex:1;flex-direction:column;min-height:0;padding-bottom:calc(92px + env(safe-area-inset-bottom));overflow:auto}
.view.on{display:flex}
.hero{padding:14px 18px 6px;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.hero h1{flex:1}
.back{border:1px solid var(--line);background:var(--p);color:var(--fg);border-radius:999px;padding:8px 12px;font-size:12px}
h1{margin:4px 0;font-size:26px;letter-spacing:-.04em}
.lead{color:var(--muted);font-size:14px;line-height:1.4;width:100%}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 8px;padding:12px 16px 8px}
.app{display:flex;flex-direction:column;align-items:center;gap:6px;text-decoration:none;color:var(--fg);background:none;border:0;font:inherit;padding:0}
.icon{width:56px;height:56px;border-radius:16px;display:grid;place-items:center;font-size:22px;
  border:1px solid var(--line);background:linear-gradient(160deg,rgba(255,255,255,.1),rgba(255,255,255,.02));transition:transform .08s ease}
.app:active .icon{transform:scale(.92)}
.app span{font-size:11px;color:var(--muted);text-align:center}
.app.hide{display:none}
.dock{position:fixed;left:14px;right:14px;bottom:calc(6px + env(safe-area-inset-bottom));z-index:20;margin:0;padding:8px;border-radius:22px;display:flex;justify-content:space-around;
  background:rgba(18,18,24,.92);border:1px solid var(--line);backdrop-filter:blur(16px)}
.dock .app span,.dock a span{font-size:10px}
.dock .on .icon{border-color:var(--g);box-shadow:0 0 0 1px var(--g)}
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
.engines{display:flex;gap:6px;padding:0 16px 10px;overflow:auto;-webkit-overflow-scrolling:touch}
.engines i{flex:0 0 auto;font-style:normal;font-size:11px;font-weight:800;letter-spacing:.04em;padding:7px 11px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.engines i.on{color:#042;background:var(--g);border-color:var(--g)}
.more a{color:var(--c)}
.ws-desk{display:none}
body.desk .dock{display:none!important;pointer-events:none}
@media (orientation:landscape){
  html,body{max-width:none!important;width:100%!important;height:100dvh!important;height:100svh!important;margin:0;overflow:hidden;padding:0}
  body.desk{
    display:block!important;
    height:100dvh;height:100svh;background:#000
  }
  body.desk .status,body.desk .hero,body.desk .quick,body.desk .more,body.desk .dock,body.desk .lead,
  body.desk .grid,body.desk .layers,body.desk .find,body.desk .pills,body.desk .sec,body.desk .engines,
  body.desk #v-chat{display:none!important}
  body.desk #v-home.view.on,body.desk #v-home{display:contents!important}
  body.desk .ws-desk{
    display:flex!important;flex-direction:column;
    position:fixed;inset:0;z-index:30;padding:0;margin:0;width:100%;height:100%;background:#000
  }
  body.desk .ws-stage{
    position:absolute;inset:0;aspect-ratio:auto;max-height:none;width:100%;height:100%;
    margin:0;border-radius:0;border:0;max-width:none
  }
  body.desk .view:not(#v-home):not(#v-chat).on{position:fixed;inset:0;z-index:4}
}
</style>
</head>
<body>
<div class="status"><span id="clk">PHONEAI</span><span class="pulse" id="pulse"><b></b> host</span><span id="host">POCKET</span></div>

<section class="view on" id="v-home">
  <div class="hero"><h1>PhoneAI Kernel</h1><p class="lead">This phone is a seat on the PC. Chat, Portal, and MCP run here — not in a cloud tab.</p></div>
  <div class="layers">
    <a class="on" href="/phoneai/app">Kernel</a>
    <a href="/phoneai/os">OS</a>
  </div>
  <div class="pills" id="pills"></div>
  <div class="engines" id="eng"></div>
  <input class="find" id="find" type="search" placeholder="Find an app" autocomplete="off"/>
  <div class="quick">
    <button type="button" data-go="chat" data-pre="Remind me to ">Remind me</button>
    <button type="button" data-go="maps">Directions</button>
    <button type="button" data-go="chat" data-pre="Draft a text: ">Text</button>
    <button type="button" data-go="mcp">MCP</button>
    <button type="button" data-go="list">List</button>
  </div>
  <div class="sec">Life</div>
  <div class="grid">
    <button class="app" data-go="chat"><div class="icon">💬</div><span>Chat</span></button>
    <button class="app" data-go="camera"><div class="icon">📷</div><span>Camera</span></button>
    <button class="app" data-go="photos"><div class="icon">🖼</div><span>Photos</span></button>
    <button class="app" data-go="maps"><div class="icon">🗺</div><span>Maps</span></button>
    <button class="app" data-go="notes"><div class="icon">📝</div><span>Notes</span></button>
    <button class="app" data-go="remind"><div class="icon">⏰</div><span>Remind</span></button>
    <button class="app" data-go="list"><div class="icon">☑</div><span>List</span></button>
    <a class="app" href="/studio/voice"><div class="icon">🎙</div><span>Voice</span></a>
    <a class="app" href="/mail"><div class="icon">✉️</div><span>Mailbox</span></a>
    <a class="app" href="sms:"><div class="icon">💬</div><span>SMS</span></a>
    <a class="app" href="tel:"><div class="icon">📞</div><span>Phone</span></a>
    <a class="app" href="/imagine"><div class="icon">✨</div><span>Imagine</span></a>
  </div>
  <div class="sec">Computer</div>
  <div class="grid">
    <a class="app" href="/phoneai/work"><div class="icon">✦</div><span>Code desk</span></a>
    <a class="app" href="/crew"><div class="icon">⧉</div><span>Crew</span></a>
    <a class="app" href="/phoneai/anti"><div class="icon">🪐</div><span>Anti</span></a>
    <a class="app" href="/phoneai/portal"><div class="icon">🖥</div><span>Portal</span></a>
    <a class="app" href="/phoneai/computer"><div class="icon">🖥</div><span>Computer</span></a>
    <a class="app" href="/phoneai/glasses"><div class="icon">👓</div><span>Glasses</span></a>
    <a class="app" href="/phoneai/airpods"><div class="icon">🎧</div><span>AirPods</span></a>
    <a class="app" href="/phoneai/web"><div class="icon">🌐</div><span>Web live</span></a>
  </div>
  <div class="sec">MCP &amp; knowledge</div>
  <div class="grid">
    <button class="app" data-go="mcp"><div class="icon">⬡</div><span>MCP</span></button>
    <a class="app" href="/phoneai/mcp"><div class="icon">⌂</div><span>MCP apps</span></a>
    <a class="app" href="/phoneai/registry"><div class="icon">▣</div><span>Registry</span></a>
    <a class="app" href="/docs"><div class="icon">📄</div><span>Docs</span></a>
    <a class="app" href="/agents"><div class="icon">🙂</div><span>Agents</span></a>
    <a class="app" href="/claims"><div class="icon">®</div><span>Claims</span></a>
  </div>
  <div class="sec">House</div>
  <div class="grid">
    <a class="app" href="/phoneai/runtime"><div class="icon">⏻</div><span>Runtime</span></a>
    <a class="app" href="/phoneai/tv"><div class="icon">📺</div><span>TV node</span></a>
    <a class="app" href="/phoneai/doorbell"><div class="icon">🔔</div><span>Doorbell</span></a>
    <a class="app" href="/phoneai/cam"><div class="icon">💻</div><span>PC cam</span></a>
    <button class="app" data-go="settings"><div class="icon">⚙</div><span>Settings</span></button>
  </div>
  <p class="more">PhoneAI Kernel™ is the phone seat on this PC — not a receptionist. Portal is the live PC stream. Anti is Antigravity. Rotate for a computer workspace. <a href="/phoneai">Website</a> · <a href="/phoneai/os">OS</a> · <a href="/setup">Setup</a> · <a href="/login">Seat</a></p>
  <div class="ws-desk" id="homeWs">__PHONEAI_WS_STAGE__</div>
</section>

<section class="view" id="v-chat">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Chat</h1><p class="lead">Talks to Grok or Codex on this computer — not a cloud toy.</p></div>
  <div class="engines" id="chatEng"></div>
  <div class="log" id="clog"></div>
  <form class="form" id="cf"><textarea id="ct" placeholder="Remind me, draft a text, where is…" rows="1"></textarea><button>Send</button></form>
</section>

<section class="view" id="v-camera">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Camera</h1><p class="lead">Snap a photo. It lands in Photos and the sovereign explorer.</p></div>
  <div style="padding:0 14px"><video id="vid" autoplay playsinline></video><canvas id="cv" hidden></canvas></div>
  <div class="form"><button class="go" type="button" id="snap">Shutter</button><button class="go" type="button" data-go="photos" style="background:#222;color:#fff">Photos</button></div>
</section>

<section class="view" id="v-photos">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Photos</h1></div>
  <div class="gallery" id="gal"></div>
</section>

<section class="view" id="v-maps">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Maps</h1><p class="lead">Opens Google Maps on the phone.</p></div>
  <form class="form" id="mf"><input id="mq" placeholder="Coffee near me, 123 Main…"/><button>Go</button></form>
  <div class="form"><button class="go" type="button" id="here">Use my location</button></div>
</section>

<section class="view" id="v-notes">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Notes</h1></div>
  <form class="form" id="nf"><input id="nt" placeholder="Quick note"/><button>Save</button></form>
  <div id="nl"></div>
</section>

<section class="view" id="v-remind">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Reminders</h1></div>
  <form class="form" id="rf"><input id="rt" placeholder="Remind me to…"/><button>Set</button></form>
  <div id="rl"></div>
</section>

<section class="view" id="v-list">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>List</h1></div>
  <form class="form" id="lf"><input id="lt" placeholder="Milk, charger…"/><button>Add</button></form>
  <div id="ll"></div>
</section>

<section class="view" id="v-mcp">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>MCP apps</h1><p class="lead">Every MCP on this PC is an app here. Open one, run a phone-safe tool. <a href="/phoneai/mcp" style="color:#58a6ff">Full folder</a> · <a href="/docs/view/how-to/PHONEAI_MCP" style="color:#58a6ff">Docs</a></p></div>
  <div class="grid" id="mcpGrid"></div>
  <div id="mcpPane" style="display:none;padding:0 8px 16px">
    <button class="quick" type="button" id="mcpBack" style="margin:8px 16px">← Apps</button>
    <div class="hero" style="padding-top:0"><h1 id="mcpName">Server</h1><p class="lead" id="mcpBlurb"></p></div>
    <div id="mcpTools"></div>
    <pre id="mcpOut" style="display:none;margin:10px 16px;white-space:pre-wrap;word-break:break-word;background:#0c0c0e;border:1px solid var(--line);border-radius:12px;padding:10px;font-size:12px;max-height:220px;overflow:auto"></pre>
  </div>
</section>

<section class="view" id="v-settings">
  <div class="hero"><button class="back" type="button" data-go="home">← Home</button><h1>Settings</h1><p class="lead">Main chat is Grok. Toggle extra CLIs for the code desk. Pair + Face ID live here.</p></div>
  <div id="srows"></div>
</section>

<nav class="dock">
  <button class="app on" data-go="home"><div class="icon">▦</div><span>Home</span></button>
  <button class="app" data-go="chat"><div class="icon">💬</div><span>Chat</span></button>
  <a class="app" href="/phoneai/os"><div class="icon">▣</div><span>OS</span></a>
  <a class="app" href="/phoneai/portal"><div class="icon">🖥</div><span>PC</span></a>
  <button class="app" data-go="mcp"><div class="icon">⬡</div><span>MCP</span></button>
  <button class="app" data-go="settings"><div class="icon">⚙</div><span>Set</span></button>
</nav>
<script>
function tick(){document.getElementById('clk').textContent=new Date().toTimeString().slice(0,5)}
tick();setInterval(tick,30000);
function show(id){
  id=id||'home';
  document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on', v.id==='v-'+id));
  location.hash=id==='home'?'':id;
  document.querySelectorAll('.dock [data-go]').forEach(el=>el.classList.toggle('on', el.getAttribute('data-go')===id));
  if(id==='camera') cam();
  if(id==='photos'||id==='notes'||id==='remind'||id==='list') life();
  if(id==='settings') settings();
  if(id==='mcp') mcpApps();
  if(document.body.classList.contains('desk')){
    document.getElementById('v-home').classList.add('on');
    document.getElementById('v-chat').classList.add('on');
    if(typeof setBuildStage==='function') setBuildStage(true,'Workspace');
  }
}
function layoutPhone(){
  const land=window.innerWidth>window.innerHeight;
  document.body.classList.toggle('desk', land);
  if(land){
    document.getElementById('v-home').classList.add('on');
    document.getElementById('v-chat').classList.add('on');
    if(typeof setBuildStage==='function') setBuildStage(true,'PC');
    if(typeof coverWorkspaceWith==='function') coverWorkspaceWith('/phoneai/portal');
  }
}
layoutPhone();
window.addEventListener('resize', layoutPhone);
window.addEventListener('orientationchange', ()=>setTimeout(layoutPhone, 120));
(function(){
  if(!window.PublicKeyCredential) return;
  const lan=/^(127\.0\.0\.1|localhost|192\.168\.|10\.)/.test(location.hostname);
  function buf(s){ return Uint8Array.from(String(s), c=>c.charCodeAt(0)).buffer; }
  function b64(s){ s=String(s).replace(/-/g,'+').replace(/_/g,'/'); while(s.length%4)s+='='; const b=atob(s); const u=new Uint8Array(b.length); for(let i=0;i<b.length;i++) u[i]=b.charCodeAt(i); return u.buffer; }
  function b64u(buf){ const u=new Uint8Array(buf); let s=''; for(let i=0;i<u.length;i++) s+=String.fromCharCode(u[i]); return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); }
  async function face(kind){
    const r=await fetch('/v1/auth/passkey/begin?kind='+kind,{credentials:'include'});
    const j=await r.json(); if(!j.ok) throw new Error(j.error||'face');
    const pk=j.publicKey; pk.challenge=buf(pk.challenge);
    if(pk.user&&pk.user.id) pk.user.id=b64(pk.user.id);
    if(pk.allowCredentials) pk.allowCredentials=pk.allowCredentials.map(c=>({type:'public-key',id:b64(c.id)}));
    const cred=kind==='register'? await navigator.credentials.create({publicKey:pk}): await navigator.credentials.get({publicKey:pk});
    const payload={id:cred.id,type:cred.type,response:{clientDataJSON:b64u(cred.response.clientDataJSON),attestationObject:cred.response.attestationObject?b64u(cred.response.attestationObject):undefined,authenticatorData:cred.response.authenticatorData?b64u(cred.response.authenticatorData):undefined,signature:cred.response.signature?b64u(cred.response.signature):undefined}};
    return fetch(kind==='register'?'/v1/auth/passkey/register':'/v1/auth/passkey/login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:payload})}).then(x=>x.json());
  }
  fetch('/v1/auth/me',{credentials:'include'}).then(r=>r.json()).then(async me=>{
    if(me && me.ok) return;
    if(lan){ try{ await face('register'); }catch(_){} return; }
    try{ await face('login'); }catch(_){ try{ await face('register'); }catch(_){ } }
  }).catch(()=>{});
})();
__PHONEAI_WS_JS__
document.body.addEventListener('click',e=>{
  const eng=e.target.closest('[data-eng]');
  if(eng){
    chatEngine=eng.getAttribute('data-eng')||'grok';
    try{ localStorage.setItem('phoneai_engine', chatEngine); }catch(_){}
    paintEngines();
    return;
  }
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
var chatEngine=(localStorage.getItem('phoneai_engine')||'grok');
async function paintEngines(){
  const j=await fetch('/v1/engines',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
  const desk=j.desk&&j.desk.length?j.desk:['grok','codex'];
  const ready=j.ready||[];
  const host=document.getElementById('host');
  if(host) host.textContent=(ready.includes('grok')?'GROK':(ready[0]||'POCKET')).toString().toUpperCase();
  const html=desk.slice(0,8).map(id=>'<i data-eng="'+id+'" class="'+(id===chatEngine?'on':'')+'">'+id+'</i>').join('');
  ['eng','chatEng'].forEach(id=>{ const el=document.getElementById(id); if(el) el.innerHTML=html; });
}
paintEngines();
async function pulse(){
  const el=document.getElementById('pulse');
  const pills=document.getElementById('pills');
  try{
    const h=await fetch('/v1/health',{credentials:'include',cache:'no-store'}).then(r=>r.json()).catch(()=>({}));
    const up=!!(h.ok||h.status==='ok'||h.up);
    if(el){ el.classList.toggle('on', up); el.lastChild.textContent=up?' host':' down'; }
    const mcp=await fetch('/v1/phoneai/mcp',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
    if(pills) pills.innerHTML=
      '<i class="'+(up?'on':'')+'">'+(up?'Host up':'Host')+'</i>'+
      '<i>'+(mcp.count||0)+' MCP</i>'+
      '<i>Kernel</i>'+
      '<i>Face ID</i>';
  }catch(_){ if(el) el.classList.remove('on'); }
}
pulse(); setInterval(pulse, 20000);
const find=document.getElementById('find');
if(find) find.addEventListener('input',()=>{
  const q=(find.value||'').toLowerCase().trim();
  document.querySelectorAll('#v-home .grid .app').forEach(a=>{
    const t=(a.textContent||'').toLowerCase();
    a.classList.toggle('hide', q && t.indexOf(q)<0);
  });
  document.querySelectorAll('#v-home .sec').forEach(sec=>{
    const grid=sec.nextElementSibling;
    if(!grid||!grid.classList.contains('grid')) return;
    const vis=[...grid.querySelectorAll('.app')].some(x=>!x.classList.contains('hide'));
    sec.style.display=(!q||vis)?'':'none';
    grid.style.display=(!q||vis)?'':'none';
  });
});
async function sendLife(kind,text,extra){
  extra=Object.assign({engine:chatEngine}, extra||{});
  const r=await fetch('/v1/phoneai/life',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,text,extra})});
  return r.json();
}
document.getElementById('cf').onsubmit=async ev=>{
  ev.preventDefault(); const t=document.getElementById('ct'); const text=(t.value||'').trim(); if(!text) return;
  t.value=''; const log=document.getElementById('clog'); add(log,'me',text); add(log,'bot',chatEngine+' · working on this PC…');
  try{
    const j=await sendLife('chat',text);
    const box=log.lastChild.querySelector('.b');
    box.textContent=(j.reply||j.error||'empty')+(j.engine?'  · '+j.engine:'');
    if(j.open && j.open.indexOf('http')===0){ const a=document.createElement('a'); a.href=j.open; a.textContent=' Open'; a.style.color='#58a6ff'; box.appendChild(a); }
  }catch(e){ log.lastChild.querySelector('.b').textContent='Host unreachable. Keep this PC awake on the same Wi-Fi.'; }
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
    +'<a class="go" href="/phoneai/os" style="display:inline-grid;place-items:center;background:#222;color:#fff;text-decoration:none">OS</a>'
    +'<a class="go" href="/phoneai/pair" style="display:inline-grid;place-items:center;background:#222;color:#fff;text-decoration:none">Pair</a>'
    +'<a class="go" href="/setup" style="display:inline-grid;place-items:center;background:#222;color:#fff;text-decoration:none">Setup</a></div></div>'
    +'<div class="item"><b>Registry</b><small>Every app, MCP, paper</small><div class="form" style="border:0;padding:8px 0"><a class="go" href="/phoneai/registry" style="display:inline-grid;place-items:center;text-decoration:none">Open</a></div></div>';
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
let MCP_APPS=[];
async function mcpApps(){
  const grid=document.getElementById('mcpGrid');
  const pane=document.getElementById('mcpPane');
  if(!grid) return;
  grid.style.display='grid'; if(pane) pane.style.display='none';
  try{
    const j=await fetch('/v1/phoneai/mcp',{credentials:'include'}).then(r=>r.json());
    MCP_APPS=j.apps||[];
    grid.innerHTML=MCP_APPS.map(a=>'<button class="app" data-mcp="'+esc(a.id)+'"><div class="icon">'+esc(a.icon)+'</div><span>'+esc(a.name)+'</span></button>').join('')
      || '<p class="lead" style="grid-column:1/-1">No MCP servers.</p>';
  }catch(_){ grid.innerHTML='<p class="lead" style="grid-column:1/-1">Sign in + Face ID to load MCP apps.</p>'; }
}
function openMcp(id){
  const a=MCP_APPS.find(x=>x.id===id); if(!a) return;
  const grid=document.getElementById('mcpGrid'); const pane=document.getElementById('mcpPane');
  if(grid) grid.style.display='none'; if(pane) pane.style.display='block';
  document.getElementById('mcpName').textContent=a.name;
  document.getElementById('mcpName').setAttribute('data-id', a.id);
  document.getElementById('mcpBlurb').textContent=(a.kind||'')+' · '+(a.blurb||'');
  const tools=a.safe_tools&&a.safe_tools.length?a.safe_tools:a.tools||[];
  document.getElementById('mcpTools').innerHTML=tools.map(t=>'<div class="item"><b>'+esc(t)+'</b><small>phone-safe · this PC</small><div class="form" style="border:0;padding:8px 0"><button class="go" type="button" data-mcp-run="'+esc(t)+'">Open</button></div></div>').join('')
    || '<div class="item">No phone-safe tools</div>';
  const out=document.getElementById('mcpOut'); if(out) out.style.display='none';
}
document.getElementById('mcpGrid').addEventListener('click',e=>{ const b=e.target.closest('[data-mcp]'); if(b) openMcp(b.getAttribute('data-mcp')); });
document.getElementById('mcpBack').onclick=()=>{ const grid=document.getElementById('mcpGrid'); const pane=document.getElementById('mcpPane'); if(grid) grid.style.display='grid'; if(pane) pane.style.display='none'; };
document.getElementById('mcpTools').addEventListener('click', async e=>{
  const b=e.target.closest('[data-mcp-run]'); if(!b) return;
  const sid=document.getElementById('mcpName').getAttribute('data-id');
  const a=MCP_APPS.find(x=>x.id===sid)||MCP_APPS[0];
  const out=document.getElementById('mcpOut'); out.style.display='block'; out.textContent='running…';
  try{
    const j=await fetch('/v1/phoneai/mcp/invoke',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({server:a&&a.id,tool:b.getAttribute('data-mcp-run')})}).then(r=>r.json());
    out.textContent=JSON.stringify(j,null,2).slice(0,8000);
  }catch(err){ out.textContent=String(err); }
});
</script>
</body></html>
"""


def phoneai_os_html() -> str:
    try:
        from pocket.workspace_stage import CSS, HTML as WS, JS
    except Exception:
        return (
            PHONEAI_OS_HTML.replace("__PHONEAI_WS_STAGE__", "")
            .replace("__PHONEAI_WS_JS__", "")
        )
    return (
        PHONEAI_OS_HTML.replace("</style>", CSS + "\n</style>")
        .replace("__PHONEAI_WS_STAGE__", WS)
        .replace("__PHONEAI_WS_JS__", JS)
    )


PHONEAI_PAIR_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<meta name="apple-mobile-web-app-title" content="PhoneAI Kernel"/>
<title>PhoneAI Kernel — Pair</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:#05060a;color:#f4f4f5;font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:430px;margin:0 auto;padding:calc(28px + env(safe-area-inset-top)) 22px 40px}
.kicker{letter-spacing:.18em;text-transform:uppercase;color:#00ff86;font-size:11px}
h1{font-size:32px;letter-spacing:-.04em;margin:10px 0 8px}
.lead{color:#8b8b98;line-height:1.45;font-size:15px}
input{width:100%;margin-top:22px;padding:16px;border-radius:14px;border:1px solid rgba(255,255,255,.12);background:#0c0c0e;color:#fff;font-size:28px;letter-spacing:.4em;text-align:center}
button{width:100%;margin-top:12px;min-height:48px;border:0;border-radius:14px;background:#00ff86;color:#042;font-weight:800}
.ghost{background:transparent;color:#00ff86;border:1px solid rgba(0,255,134,.4);margin-top:8px}
.hint{margin-top:16px;color:#8b8b98;font-size:13px;min-height:2.4em}
a{color:#58a6ff}
</style>
</head>
<body>
<p class="kicker">PhoneAI Kernel</p>
<h1>Pair this phone</h1>
<p class="lead">Not a receptionist. Not owner login. Six-digit code from the PC, then Face ID on <b>this</b> phone. You become a device seat.</p>
<input id="code" inputmode="numeric" maxlength="6" placeholder="000000" autocomplete="one-time-code"/>
<button type="button" id="go">Pair with Face ID</button>
<button type="button" class="ghost" id="mint">Mint a code (this PC / home Wi-Fi)</button>
<p class="hint" id="hint">LAN can skip Face ID. Tunnel needs code + passkey.</p>
<p class="hint">Then open <a href="/phoneai/computer">Computer</a> — Portal, contained.</p>
<script>
function b64urlToBuf(s){s=s.replace(/-/g,'+').replace(/_/g,'/');const pad=s.length%4;if(pad)s+='='.repeat(4-pad);const bin=atob(s);const u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);return u.buffer}
function bufToB64url(buf){const u=new Uint8Array(buf);let s='';for(const b of u)s+=String.fromCharCode(b);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
function strToBuf(s){if(typeof s!=='string')return s;try{return b64urlToBuf(s)}catch(_){const u=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u.buffer}}
const hint=document.getElementById('hint');
document.getElementById('mint').onclick=async()=>{
  const j=await fetch('/v1/auth/device/mint',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
  hint.textContent=j.code?('Code '+j.code+' — 10 min. Enter it on the tunnel, then Face ID.'):(j.error||'Mint on the PC');
  if(j.code) document.getElementById('code').value=j.code;
};
function tellNative(payload){
  try{ window.ReactNativeWebView && window.ReactNativeWebView.postMessage(JSON.stringify(payload)); }catch(_){}
}
function goComputer(principal){
  tellNative({ok:true,event:'paired',principal:principal||'device'});
  location.href='/phoneai/computer';
}
document.getElementById('code').addEventListener('input',e=>{
  e.target.value=(e.target.value||'').replace(/\D/g,'').slice(0,6);
});
document.getElementById('go').onclick=async()=>{
  const code=(document.getElementById('code').value||'').replace(/\D/g,'');
  const lan=/^(127\.0\.0\.1|localhost|192\.168\.|10\.)/.test(location.hostname);
  if(lan && !code){ goComputer('device:lan'); return; }
  if(code.length!==6){ hint.textContent='Enter the 6-digit code from the PC'; return; }
  if(!window.PublicKeyCredential){ hint.textContent='This phone needs Face ID / a passkey'; return; }
  try{
    const started=await fetch('/v1/auth/device/begin',{credentials:'include'}).then(r=>r.json());
    if(!started.ok){ hint.textContent=started.error||'Mint a code on the PC first'; return; }
    const pk=started.publicKey;
    pk.challenge=strToBuf(pk.challenge);
    if(pk.user&&pk.user.id) pk.user.id=b64urlToBuf(pk.user.id);
    const cred=await navigator.credentials.create({publicKey:pk});
    const payload={id:cred.id,rawId:bufToB64url(cred.rawId),type:cred.type,response:{clientDataJSON:bufToB64url(cred.response.clientDataJSON),attestationObject:cred.response.attestationObject?bufToB64url(cred.response.attestationObject):undefined}};
    const j=await fetch('/v1/auth/device/redeem',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({code,credential:payload})}).then(r=>r.json());
    if(j&&j.ok){ hint.textContent='Device seat paired. Opening Computer.'; goComputer((j.user||j.device&&j.device.principal)||'device'); }
    else hint.textContent=j.error||'Pair failed — code + Face ID';
  }catch(e){ hint.textContent=(e&&e.message)||'Pair cancelled'; }
};
</script>
</body></html>
"""


def phoneai_pair_html() -> str:
    return PHONEAI_PAIR_HTML


PHONEAI_SYSTEM_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#05060a"/>
<meta name="apple-mobile-web-app-title" content="PhoneAI OS"/>
<title>PhoneAI OS</title>
<style>
:root{--g:#00ff86;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--p:#14141c;--c:#58a6ff}
*{box-sizing:border-box}
html,body{margin:0;min-height:100dvh;background:#05060a;color:var(--fg);font:16px/1.45 ui-sans-serif,system-ui}
body{max-width:430px;margin:0 auto;padding:calc(12px + env(safe-area-inset-top)) 16px 88px;
  background:radial-gradient(640px 320px at -10% 0%,rgba(88,166,255,.1),transparent 50%),#05060a}
.bar{display:flex;justify-content:space-between;align-items:center;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.bar .pulse{display:inline-flex;align-items:center;gap:6px;letter-spacing:.08em}
.bar .pulse b{width:7px;height:7px;border-radius:50%;background:#555;display:inline-block}
.bar .pulse.on b{background:var(--g);box-shadow:0 0 8px var(--g)}
h1{font-size:28px;letter-spacing:-.04em;margin:10px 0 4px}
.lead{color:var(--muted);font-size:14px}
.layers{display:flex;gap:8px;margin:14px 0}
.layers a{flex:1;text-align:center;padding:10px;border-radius:14px;border:1px solid var(--line);color:var(--fg);text-decoration:none;font-weight:800;font-size:13px}
.layers a.on{background:var(--g);color:#042}
.pills{display:flex;gap:6px;overflow:auto;margin:0 0 12px}
.pills i{flex:0 0 auto;font-style:normal;font-size:11px;border:1px solid var(--line);border-radius:999px;padding:5px 9px;color:var(--muted)}
.pills i.on{color:#042;background:var(--g);border-color:var(--g)}
.find{width:100%;min-height:42px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);padding:10px 12px;font:inherit;margin:0 0 8px}
.sec{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:14px 0 6px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.card{display:block;padding:14px;border-radius:16px;border:1px solid var(--line);background:var(--p);color:var(--fg);text-decoration:none}
.card:active{transform:scale(.98)}
.card b{display:block;font-size:15px}
.card span{display:block;color:var(--muted);font-size:12px;margin-top:4px}
.card.hide{display:none}
.dock{position:fixed;left:14px;right:14px;bottom:calc(8px + env(safe-area-inset-bottom));display:flex;justify-content:space-around;padding:10px;border-radius:22px;background:rgba(18,18,24,.92);border:1px solid var(--line)}
.dock a{color:var(--muted);text-decoration:none;font-size:11px;font-weight:800}
.dock a.on{color:var(--g)}
</style></head><body>
<div class="bar"><span>PHONEAI OS</span><span class="pulse" id="pulse"><b></b> host</span><span id="clk"></span></div>
<h1>PhoneAI OS</h1>
<p class="lead">Services on this computer — Codex, Grok, Portal, MCP, agents. Kernel is the home screen. OS is the control plane.</p>
<div class="layers">
  <a href="/phoneai/app">Kernel</a>
  <a class="on" href="/phoneai/os">OS</a>
</div>
<div class="pills" id="pills"></div>
<input class="find" id="find" type="search" placeholder="Find a service" autocomplete="off"/>
<div class="sec">Work</div>
<div class="grid" data-sec="Work">
  <a class="card" href="/phoneai/app#chat"><b>Chat</b><span>Grok · Codex first-class</span></a>
  <a class="card" href="/phoneai/work"><b>Code desk</b><span>Grok · Codex · Meta · Gemini + your GitHubs</span></a>
  <a class="card" href="/v1/team/workspace"><b>Team workspace</b><span>Long work · shared disk</span></a>
  <a class="card" href="/agents"><b>Agents</b><span>Every first-class roster</span></a>
</div>
<div class="sec">Screen</div>
<div class="grid" data-sec="Screen">
  <a class="card" href="/phoneai/portal"><b>Screen</b><span>pocket.stream.v1 · embody</span></a>
  <a class="card" href="/phoneai/computer"><b>Computer</b><span>Portal contained on this phone</span></a>
  <a class="card" href="/phoneai/anti"><b>Antigravity</b><span>Desktop app stream</span></a>
  <a class="card" href="/phoneai/glasses"><b>Glasses HUD</b><span>Wear the same seat</span></a>
</div>
<div class="sec">MCP</div>
<div class="grid" data-sec="MCP">
  <a class="card" href="/phoneai/mcp"><b>MCP apps</b><span>Pocket · Nexus · GitHub · CF</span></a>
  <a class="card" href="/phoneai/registry"><b>Registry</b><span>Every app · MCP · paper</span></a>
  <a class="card" href="/webmcp"><b>WebMCP</b><span>Page actions for agents</span></a>
  <a class="card" href="/docs"><b>Docs</b><span>How-to + white papers</span></a>
</div>
<div class="sec">Host</div>
<div class="grid" data-sec="Host">
  <a class="card" href="/phoneai/app#settings"><b>Pair</b><span>Code + Face ID, not owner</span></a>
  <a class="card" href="/phoneai/runtime"><b>Runtime</b><span>One watchdog</span></a>
  <a class="card" href="/v1/engines"><b>Engines</b><span>JSON live catalog</span></a>
  <a class="card" href="/claims"><b>Claims</b><span>Kernel™ · SCREEN-KERNEL</span></a>
</div>
<p class="lead" style="margin-top:18px">Kernel = identity, screen, pair. OS = apps, agents, Codex, life. Future phones run this seat, not a receptionist.</p>
<nav class="dock">
  <a href="/phoneai/app">Kernel</a>
  <a class="on" href="/phoneai/os">OS</a>
  <a href="/phoneai/portal">Portal</a>
  <a href="/phoneai/mcp">MCP</a>
  <a href="/phoneai/work">Codex</a>
</nav>
<script>
document.getElementById('clk').textContent=new Date().toTimeString().slice(0,5);
setInterval(()=>{document.getElementById('clk').textContent=new Date().toTimeString().slice(0,5)},30000);
async function pulse(){
  const el=document.getElementById('pulse');
  const pills=document.getElementById('pills');
  try{
    const h=await fetch('/v1/health',{credentials:'include',cache:'no-store'}).then(r=>r.json()).catch(()=>({}));
    const up=!!(h.ok||h.status==='ok'||h.up);
    if(el){ el.classList.toggle('on', up); el.lastChild.textContent=up?' host':' down'; }
    const j=await fetch('/v1/registry',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
    const c=j.counts||{};
    pills.innerHTML=
      '<i class="'+(up?'on':'')+'">'+(up?'Host up':'Host')+'</i>'+
      '<i>'+(c.mcp_apps||0)+' MCP</i>'+
      '<i>'+(c.agents||0)+' agents</i>'+
      '<i>'+(c.skills||0)+' skills</i>'+
      '<i>'+(c.papers||0)+' papers</i>';
  }catch(_){}
}
pulse(); setInterval(pulse, 20000);
const find=document.getElementById('find');
find.addEventListener('input',()=>{
  const q=(find.value||'').toLowerCase().trim();
  document.querySelectorAll('.card').forEach(a=>{
    const t=(a.textContent||'').toLowerCase();
    a.classList.toggle('hide', q && t.indexOf(q)<0);
  });
  document.querySelectorAll('.sec').forEach(sec=>{
    const grid=sec.nextElementSibling;
    if(!grid) return;
    const vis=[...grid.querySelectorAll('.card')].some(x=>!x.classList.contains('hide'));
    sec.style.display=(!q||vis)?'':'none';
    grid.style.display=(!q||vis)?'':'none';
  });
});
</script>
</body></html>
"""


def phoneai_system_html() -> str:
    return PHONEAI_SYSTEM_HTML


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
.ws-desk{display:none}
@media (orientation:landscape){
  body{max-width:none;height:100dvh;display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,38vw);grid-template-rows:48px auto auto 1fr auto;padding:0}
  .top{grid-column:1/-1}
  .ws-desk{display:block;grid-column:1;grid-row:2/5;padding:8px;min-height:0}
  .ws-stage{height:100%;aspect-ratio:auto;max-height:none;width:100%;margin:0}
  .log{grid-column:2;grid-row:4;border-left:1px solid var(--line)}
  .form{grid-column:1/-1}
}
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
select.pick{flex:1;min-width:140px;padding:8px;border-radius:10px;background:#0c0c0e;color:#fafafa;border:1px solid var(--line)}
.engines button.off{opacity:.45}
</style></head>
<body>
<div class="top"><a href="/phoneai">Home</a><b style="flex:1">Code desk</b><a href="/phoneai/anti">Anti</a></div>
<div class="ws-desk" id="workWs">__PHONEAI_WS_STAGE__</div>
<div id="now" style="padding:8px 14px;font-size:12px;color:#a1a1aa;border-bottom:1px solid var(--line)">Pick a CLI and a GitHub, then New session. These are wired tools, not attached agents.</div>
<div class="engines" id="eng"></div>
<div style="display:flex;gap:8px;padding:8px 12px;flex-wrap:wrap">
<select id="repo" class="pick"></select>
</div>
<div style="display:flex;gap:8px;padding:0 12px 8px;flex-wrap:wrap">
<select id="thr" class="pick"></select>
<button type="button" id="ns" style="border:0;border-radius:10px;background:#10a37f;color:#042;font-weight:800;padding:8px 12px">New session</button>
</div>
<div class="log" id="log"></div>
<form class="form" id="f">
  <textarea id="t" placeholder="Talk to the chosen CLI in the chosen repo…" rows="1"></textarea>
  <button type="submit">Send</button>
</form>
<script>
let engine='grok';
let sessionId='';
let repo='';
const LABELS={grok:'Grok CLI',codex:'Codex CLI',meta:'Meta',gemini:'Gemini CLI'};
const log=document.getElementById('log');
function add(who, text, eng){
  const d=document.createElement('div');
  d.className='m'+(who==='me'?' me':'');
  d.innerHTML='<div class="eng">'+(eng||who)+'</div><div class="b"></div>';
  d.querySelector('.b').textContent=text;
  log.appendChild(d); log.scrollTop=log.scrollHeight;
  return d;
}
function paintSessions(sessions){
  const sel=document.getElementById('thr');
  const rows=sessions||[];
  sel.innerHTML=rows.length
    ? rows.map(s=>'<option value="'+s.id+'">'+(s.cli||'')+' · '+(s.repo||s.title||s.id).slice(0,70)+'</option>').join('')
    : '<option value="">No sessions yet — tap New session</option>';
  if(sessionId) sel.value=sessionId;
}
function paintNow(s){
  const now=document.getElementById('now');
  if(!s || !s.id){ now.textContent='No session. Pick CLI + GitHub, then New session.'; return; }
  now.textContent=(s.cli||engine)+' · '+(s.repo||s.cwd||'')+(s.cli_available===false?' · CLI missing on this PC':'');
}
fetch('/v1/phoneai/code-desk',{credentials:'include'}).then(r=>r.json()).then(d=>{
  const clis=d.clis||[];
  document.getElementById('eng').innerHTML=clis.map(c=>{
    const on=c.id===engine?' on':'';
    const miss=c.available?'':' off';
    return '<button type="button" data-e="'+c.id+'" class="'+(on+miss).trim()+'" title="'+(c.path||c.note||'')+'">'+(LABELS[c.id]||c.label)+(c.available?'':' · off')+'</button>';
  }).join('');
  const rs=d.repos||[];
  const rsel=document.getElementById('repo');
  rsel.innerHTML=rs.map(x=>{
    const id=x.full||x.id||x.name;
    const loc=x.local?' · disk':'';
    return '<option value="'+id+'">'+id+loc+'</option>';
  }).join('') || '<option value="">gh not signed in — local folders only</option>';
  const live=d.you_are_working_on||{};
  if(live.id){ sessionId=live.id; engine=live.cli||engine; repo=live.repo||''; }
  if(repo) rsel.value=repo;
  paintSessions(d.sessions||[]);
  paintNow(live);
  add('bot', d.note||'Code desk ready.', 'desk');
}).catch(()=>add('bot','Could not load code desk. Is Pocket up?','err'));
document.getElementById('eng').onclick=e=>{
  const b=e.target.closest('button'); if(!b) return;
  engine=b.getAttribute('data-e');
  [...document.getElementById('eng').children].forEach(x=>x.classList.toggle('on',x===b));
};
document.getElementById('repo').onchange=()=>{ repo=document.getElementById('repo').value; };
document.getElementById('thr').onchange=()=>{
  sessionId=document.getElementById('thr').value;
  const o=document.getElementById('thr').selectedOptions[0];
  if(o) document.getElementById('now').textContent='Session '+o.textContent;
};
document.getElementById('ns').onclick=async()=>{
  repo=document.getElementById('repo').value||repo;
  const j=await fetch('/v1/phoneai/code-desk/session',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({cli:engine,repo,title:engine+' · '+repo})}).then(r=>r.json());
  const s=j.session||{};
  if(!s.id){ alert(j.error||j.repo_error||'could not create session'); return; }
  sessionId=s.id;
  const sel=document.getElementById('thr');
  const opt=document.createElement('option');
  opt.value=s.id; opt.textContent=(s.cli||engine)+' · '+(s.repo||s.cwd||s.id);
  sel.insertBefore(opt, sel.firstChild); sel.value=s.id;
  paintNow(s);
  add('bot','New session '+s.id+' · '+(s.cli||engine)+' in '+(s.repo||s.cwd), s.cli||engine);
};
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault();
  const t=document.getElementById('t');
  const text=(t.value||'').trim(); if(!text) return;
  repo=document.getElementById('repo').value||repo;
  t.value=''; add('me', text, 'you');
  add('bot','Working…', engine);
  if(typeof setBuildStage==='function') setBuildStage(true, engine+' · '+(repo||'repo'));
  const body={text,engine,cli:engine,session_id:sessionId,thread_id:sessionId,repo,new:!sessionId};
  try{
    const r=await fetch('/v1/phoneai/work/stream',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!r.ok || !r.body){
      const j=await fetch('/v1/phoneai/work',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(x=>x.json());
      log.lastChild.remove();
      if(j.session_id) sessionId=j.session_id;
      add('bot', j.reply||j.error||'no reply', j.engine||engine);
      return;
    }
    const reader=r.body.getReader(); const dec=new TextDecoder();
    let buf='', reply='', eng=engine, last=log.lastChild;
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
          try{ const j=JSON.parse(data); eng=j.engine||eng; if(j.session_id) sessionId=j.session_id; if(!reply) reply=j.reply||j.error||''; }catch(_){}
        }
      }
    }
    last.querySelector('.eng').textContent=eng;
    last.querySelector('.b').textContent=reply||'no reply';
    if(typeof setBuildStage==='function') setBuildStage(false);
  }catch(e){
    log.lastChild.remove();
    add('bot','Cannot reach POCKET host. Keep the PC awake on this Wi-Fi.','err');
  }
};
</script>
</body></html>
"""


def phoneai_twin_html() -> str:
    from pocket.workspace_stage import CSS, HTML as WS, JS

    html = (
        PHONEAI_TWIN_HTML.replace("</style>", CSS + "\n</style>")
        .replace("__PHONEAI_WS_STAGE__", WS)
        .replace("</script>", JS + "\nsetBuildStage(false);\n</script>")
    )
    return html


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
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="mobile-web-app-capable" content="yes"/>
<meta name="theme-color" content="#000000"/>
<title>Portal · PhoneAI · 3.16.8</title>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.12);--g:#00ff86;--ctrl:118px}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{width:100%;height:100%;height:100dvh;height:100svh;margin:0;background:#000;color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif;overflow:hidden}
html{position:fixed;inset:0}
body{position:fixed;inset:0;padding:0;touch-action:manipulation}
/* Stage is the letterbox glass. Controls sit BELOW it so the whole PC is visible 1:1. */
.stage{position:fixed;left:0;right:0;top:0;bottom:calc(var(--ctrl) + env(safe-area-inset-bottom));background:#000;overflow:hidden;touch-action:none;z-index:1}
body:not(.hud-off) .stage{top:calc(132px + env(safe-area-inset-top));bottom:calc(var(--ctrl) + 56px + env(safe-area-inset-bottom))}
.stage img{background:#000}
.view{position:absolute;inset:0;transform-origin:0 0}
.view img{position:absolute;left:0;top:0;max-width:none;max-height:none;width:auto;height:auto;object-fit:fill;object-position:center;touch-action:none;user-select:none;-webkit-user-drag:none;image-rendering:auto}
.dot{position:absolute;width:22px;height:22px;border-radius:50%;border:2px solid #00ff86;pointer-events:none;transform:translate(-50%,-50%);display:none;z-index:4;box-shadow:0 0 0 5px rgba(0,255,134,.16)}
.dot.hold{width:28px;height:28px;background:rgba(0,255,134,.28);box-shadow:0 0 0 8px rgba(0,255,134,.18)}
.mode-badge{position:absolute;top:calc(12px + env(safe-area-inset-top));left:14px;z-index:13;display:none;align-items:center;gap:8px;background:rgba(5,6,10,.82);border:1px solid var(--g);color:var(--g);border-radius:999px;padding:8px 12px;font-weight:800;font-size:12px;letter-spacing:.04em;pointer-events:none;box-shadow:0 8px 24px rgba(0,0,0,.35)}
body.drag-mode .mode-badge,body.hold-mode .mode-badge{display:flex}
.mode-badge i{width:18px;height:18px;display:block;background:currentColor;mask-size:contain;mask-repeat:no-repeat;mask-position:center;-webkit-mask-size:contain;-webkit-mask-repeat:no-repeat;-webkit-mask-position:center}
body.drag-mode .mode-badge i{mask-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='black' d='M13 6.4L16.6 10H14v4h2.6L13 17.6 14.4 19 20 13.4 14.4 7.8 13 6.4zM11 6.4L9.6 7.8 4 13.4 9.6 19 11 17.6 7.4 14H10V10H7.4L11 6.4z'/></svg>");-webkit-mask-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='black' d='M13 6.4L16.6 10H14v4h2.6L13 17.6 14.4 19 20 13.4 14.4 7.8 13 6.4zM11 6.4L9.6 7.8 4 13.4 9.6 19 11 17.6 7.4 14H10V10H7.4L11 6.4z'/></svg>")}
body.hold-mode .mode-badge i{mask-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><circle cx='12' cy='12' r='7' fill='black'/></svg>");-webkit-mask-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><circle cx='12' cy='12' r='7' fill='black'/></svg>")}
.joy{position:absolute;left:12px;bottom:calc(12px + env(safe-area-inset-bottom));width:84px;height:84px;border-radius:50%;background:rgba(20,20,28,.45);border:1px solid var(--line);z-index:6;touch-action:none}
.joy i{position:absolute;left:50%;top:50%;width:36px;height:36px;margin:-18px 0 0 -18px;border-radius:50%;background:var(--g);box-shadow:0 4px 12px rgba(0,0,0,.4)}
.top,.tabs,.apps,.ctrl,.bar{position:fixed;left:0;right:0;z-index:8;background:rgba(5,6,10,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);transition:opacity .15s linear}
.top{top:0;display:flex;align-items:center;gap:8px;padding:calc(8px + env(safe-area-inset-top)) 10px 8px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.top a{color:var(--muted);text-decoration:none;font-size:13px}
.top b{flex:1}
.tabs{top:calc(48px + env(safe-area-inset-top));display:flex;gap:6px;overflow:auto;padding:6px 10px;border-bottom:1px solid var(--line);-webkit-overflow-scrolling:touch;touch-action:pan-x}
.apps{top:calc(88px + env(safe-area-inset-top));display:flex;gap:6px;overflow:auto;padding:6px 10px;border-bottom:1px solid var(--line);-webkit-overflow-scrolling:touch;touch-action:pan-x}
.bar{bottom:0;display:flex;gap:8px;padding:8px 10px calc(8px + env(safe-area-inset-bottom));border-top:1px solid var(--line)}
.ctrl{bottom:env(safe-area-inset-bottom);display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:auto auto;gap:8px;padding:8px 10px;border-top:1px solid var(--line);z-index:20;touch-action:manipulation;pointer-events:auto}
body:not(.hud-off) .ctrl{bottom:calc(56px + env(safe-area-inset-bottom))}
.seg{display:flex;border:1px solid var(--line);border-radius:999px;overflow:hidden}
.seg button{border:0;background:transparent;color:var(--muted);padding:8px 12px;font-weight:800;font-size:12px}
.seg button.on{background:var(--g);color:#042}
.ctrl button{min-height:52px;border:1px solid var(--line);border-radius:14px;background:#14141c;color:#fff;font-weight:800;font-size:13px;touch-action:manipulation;-webkit-user-select:none;user-select:none}
.ctrl button.held,.ctrl button.on{background:var(--g);color:#042}
.ctrl .pad-lab{grid-column:1 / -1;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:0 2px;min-height:0;border:0;background:transparent;text-align:left;pointer-events:none}
body.pad-move .ctrl .arrows{outline:1px solid var(--g)}
.bar input{flex:1;min-height:48px;border-radius:12px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:10px;font:inherit}
.bar button{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px}
.hint{position:absolute;left:10px;right:10px;bottom:10px;font-size:12px;color:#d4d4d8;background:rgba(0,0,0,.55);padding:8px 10px;border-radius:8px;pointer-events:none;z-index:5}
.tabs button,.apps button{flex:0 0 auto;border:1px solid var(--line);background:#14141c;color:#fff;border-radius:999px;padding:8px 12px;font-size:12px;max-width:46vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tabs button.on{background:var(--g);color:#042;border-color:var(--g);font-weight:800}
.wtab{display:flex;align-items:center;gap:4px;flex:0 0 auto;border:1px solid var(--line);background:#14141c;border-radius:14px;padding:4px 8px 4px 6px;max-width:64vw}
.wtab.on{border-color:var(--g);background:rgba(0,255,134,.14)}
.wtab .chrome{display:flex;gap:4px;flex:0 0 auto}
.wtab .chrome button{width:18px;height:18px;min-width:18px;min-height:18px;padding:0;border:0;border-radius:50%;font-size:10px;font-weight:900;line-height:18px;color:#1a1200}
.wtab .wmin{background:#f5c542}
.wtab .wmax{background:#3dd68c}
.wtab .wclose{background:#ff5f57;color:#3a0000}
.wtab .wtitle{border:0;background:transparent;color:#fff;font-size:11px;padding:4px 6px;max-width:34vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;border-radius:8px}
.wtab.on .wtitle{color:var(--g);font-weight:800}
.net{font-size:10px;font-weight:800;color:var(--muted);letter-spacing:.04em}
.pills{position:fixed;top:calc(8px + env(safe-area-inset-top));right:10px;z-index:12;display:flex;gap:6px}
.pills button{min-width:44px;min-height:36px;border-radius:999px;border:1px solid var(--line);background:rgba(5,6,10,.72);color:#fff;font-weight:800;font-size:11px;letter-spacing:.04em}
.pills button.on{background:var(--g);color:#042}
body.hud-off .top,body.hud-off .tabs,body.hud-off .apps{opacity:0;pointer-events:none;visibility:hidden}
body.hud-off .bar{opacity:0;pointer-events:none;visibility:hidden}
body.hud-off .hint{opacity:.55}
body.hud-off .joy{opacity:.9;pointer-events:auto}
body.hud-off .ctrl{opacity:1;pointer-events:auto;visibility:visible;background:rgba(5,6,10,.72)}
.typebox{position:fixed;left:10px;right:10px;bottom:calc(var(--ctrl) + 8px + env(safe-area-inset-bottom));z-index:15;display:none;gap:8px;align-items:center}
.typebox.on{display:flex}
.typebox input{flex:1;min-height:44px;border-radius:12px;border:1px solid var(--line);background:rgba(12,12,14,.88);color:#fff;padding:10px 12px;font:inherit;backdrop-filter:blur(10px)}
.typebox button{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:0 14px;min-height:44px}
.dot{display:block}
body.mobile .hint{left:10px;right:10px;transform:none}
@media (orientation:landscape){
  html,body{width:100%;height:100dvh;height:100svh;overflow:hidden}
  :root{--ctrl:96px}
  .ctrl button{min-height:40px;font-size:12px}
  .joy{width:72px;height:72px}
}
</style></head>
<body class="hud-off">
<div class="pills">
  <button type="button" id="faceBtn">Face ID</button>
  <button type="button" id="pairBtn">Pair</button>
  <button type="button" id="focusPill">Focus</button>
  <button type="button" id="desk2Btn">Desk 2</button>
  <button type="button" id="hudbtn">HUD</button>
  <button type="button" id="typeBtn">Type</button>
</div>
<div class="top">
  <a href="/phoneai/app">Home</a>
  <b>Portal</b>
  <span class="net" id="net">LAN</span>
  <div class="seg" id="fitseg">
    <button type="button" data-f="contain" class="on">Laptop</button>
    <button type="button" data-f="cover">Crop</button>
  </div>
  <div class="seg" id="mode">
    <button type="button" data-m="watch">Watch</button>
    <button type="button" data-m="touch" class="on">Touch</button>
  </div>
</div>
<div class="tabs" id="tabs"></div>
<div class="apps" id="apps"></div>
<div class="stage" id="stage">
  <div class="view" id="view">
    <img id="frame" alt="PC" src="/v1/phoneai/portal/frame?target=desktop&max_w=1280&q=72&t=1" draggable="false"/>
  </div>
  <div class="dot" id="dot"></div>
  <div class="mode-badge" id="modeBadge"><i></i><span id="modeBadgeText">MOVE</span></div>
  <div class="joy" id="joy"><i id="knob"></i></div>
  <div class="hint" id="hint">1:1 laptop in this pane. Entire PC is shown. Focus = active app.</div>
</div>
<div class="ctrl">
  <button type="button" id="lmb">L click</button>
  <button type="button" id="rmb">R click</button>
  <button type="button" id="moveBtn">Move</button>
  <button type="button" id="focusBtn">Focus</button>
  <button type="button" id="scL" class="arrows" aria-label="Left">◀</button>
  <button type="button" id="sup" class="arrows" aria-label="Up">▲</button>
  <button type="button" id="sdn" class="arrows" aria-label="Down">▼</button>
  <button type="button" id="scR" class="arrows" aria-label="Right">▶</button>
</div>
<form class="bar" id="kb">
  <input id="keysHud" placeholder="HUD type" autocomplete="off" autocapitalize="off" spellcheck="false"/>
  <button>Enter</button>
</form>
<form class="typebox" id="typeform">
  <input id="keys" placeholder="Type here — keyboard only when you tap Type" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="enter" inputmode="text" readonly tabindex="-1"/>
  <button type="button" id="typeHide">Done</button>
  <button>Send</button>
</form>
<script>
let mode='touch', target='desktop', busy=false, fitMode='contain', phoneFocus=false, fitLocked=false, padMode='scroll';
let zoom=1, panX=0, panY=0;
let lastNx=0.5, lastNy=0.5, lastDrag=0, lastTyped='', armed=false, lastTap=0, activeHwnd=0;
let tabTaps={hwnd:0,n:0,t:0}, streamTaps={n:0,t:0};
let live=null, liveOk=false, blobUrl='', net={label:'LAN', max_w:960, q:58, fps:12};
let netPinned=false;
const img=document.getElementById('frame');
const view=document.getElementById('view');
const stage=document.getElementById('stage');
const dot=document.getElementById('dot');
const hint=document.getElementById('hint');
const keys=document.getElementById('keys');
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function glass(){
  const r=stage.getBoundingClientRect();
  return {width:r.width, height:r.height, left:r.left, top:r.top};
}
let hudTimer=0;
function setHud(on){
  document.body.classList.toggle('hud-off', !on);
  const b=document.getElementById('hudbtn');
  if(b) b.classList.toggle('on', !!on);
  clearTimeout(hudTimer);
}
function goGlass(){
  const el=document.documentElement;
  const req=el.requestFullscreen||el.webkitRequestFullscreen;
  if(req){ try{ req.call(el); }catch(_){} }
}
function netProfile(){
  const c=navigator.connection||navigator.mozConnection||navigator.webkitConnection||{};
  const type=(c.effectiveType||'').toLowerCase();
  const downlink=Number(c.downlink||0);
  const rtt=Number(c.rtt||0);
  const save=!!c.saveData;
  const cellular=(c.type==='cellular') || /2g|3g|4g|5g/.test(type);
  if(save || type==='2g' || type==='slow-2g') return {label:'2G', max_w:640, q:48, fps:6};
  if(type==='3g') return {label:'3G', max_w:720, q:50, fps:7};
  if(cellular && (type==='4g' || type==='5g' || downlink>=8)){
    if(downlink>=20 || rtt && rtt<=40) return {label:'5G', max_w:880, q:56, fps:10};
    return {label:'LTE', max_w:800, q:54, fps:9};
  }
  if(cellular) return {label:'CELL', max_w:720, q:52, fps:8};
  return {label:'LAN', max_w:960, q:58, fps:12};
}
let fpsShow=0, fpsN=0, fpsT=0, lastFrameAt=0;
function noteFrame(){
  lastFrameAt=Date.now();
  fpsN++;
  if(lastFrameAt-fpsT>=1000){ fpsShow=fpsN; fpsN=0; fpsT=lastFrameAt; }
}
function applyNet(){
  const n=netProfile();
  if(!netPinned){ net=n; netPinned=true; }
  else {
    net.label=n.label;
    if(n.label==='2G' || n.label==='3G'){ net.max_w=n.max_w; net.q=n.q; net.fps=n.fps; }
  }
  const el=document.getElementById('net');
  if(el) el.textContent=net.label+(liveOk?' · LIVE':'')+' · '+(fpsShow||net.fps)+'fps';
  if(liveOk && live && live.readyState===1){
    try{ live.send(JSON.stringify({kind:'cfg', max_w:net.max_w, q:net.q, fps:net.fps, target:target, hwnd:activeHwnd||0})); }catch(_){}
  }
}
let lastLay='';
function layout(){
  /* Fit is 1:1 — letterbox (or crop) the PC aspect into the stage. Do not restyle the stage. */
  const s=stage.getBoundingClientRect();
  const iw=img.naturalWidth||16, ih=img.naturalHeight||9;
  const ar=iw/Math.max(1,ih);
  let w=s.width, h=w/ar;
  if(fitMode==='cover'){
    if(h<s.height){ h=s.height; w=h*ar; }
  } else {
    if(h>s.height){ h=s.height; w=h*ar; }
  }
  w=Math.round(w); h=Math.round(h);
  const left=Math.round((s.width-w)/2), top=Math.round((s.height-h)/2);
  const key=w+','+h+','+left+','+top+','+fitMode;
  if(key===lastLay) return;
  lastLay=key;
  img.style.left=left+'px';
  img.style.top=top+'px';
  img.style.width=w+'px';
  img.style.height=h+'px';
}
function maybeLayout(){ layout(); }
function applyView(){
  if(zoom<=1.02){ zoom=1; panX=0; panY=0; }
  const s=stage.getBoundingClientRect();
  panX=clamp(panX, s.width*(1-zoom), 0);
  panY=clamp(panY, s.height*(1-zoom), 0);
  view.style.transform='translate('+panX+'px,'+panY+'px) scale('+zoom+')';
  lastLay='';
  layout();
}
let layTimer=0;
function scheduleLayout(){
  clearTimeout(layTimer);
  layTimer=setTimeout(()=>{ autoFit(); applyView(); }, 160);
}
window.addEventListener('resize', scheduleLayout);
window.addEventListener('orientationchange', ()=>{ lastLay=''; setTimeout(()=>{ autoFit(); applyView(); }, 220); });
if(window.visualViewport){
  window.visualViewport.addEventListener('resize', scheduleLayout);
}
function autoFit(){
  if(phoneFocus){
    fitMode='contain';
    document.body.classList.add('mobile');
    if(hint) hint.textContent='Focus on · active window at its real size. Tap Focus to see the full laptop.';
    return;
  }
  document.body.classList.remove('mobile');
  if(!fitLocked) fitMode='contain';
  const fit=document.querySelector('#fitseg [data-f="'+fitMode+'"]');
  if(fit) [...document.getElementById('fitseg').children].forEach(x=>x.classList.toggle('on',x===fit));
  if(hint) hint.textContent='1:1 laptop in this pane. Crop zooms a region. Controls sit under the screen.';
}
function setPhoneFocus(on){
  phoneFocus=!!on;
  target=phoneFocus?'focus':'desktop';
  const fb=document.getElementById('focusBtn');
  const fp=document.getElementById('focusPill');
  if(fb) fb.classList.toggle('on', phoneFocus);
  if(fp) fp.classList.toggle('on', phoneFocus);
  autoFit(); applyView(); applyNet();
  if(phoneFocus){
    send('focus', lastNx, lastNy, activeHwnd?{hwnd:activeHwnd}:{});
  }
}
document.getElementById('fitseg').onclick=e=>{
  const b=e.target.closest('[data-f]'); if(!b) return;
  fitMode=b.getAttribute('data-f');
  fitLocked=true;
  [...document.getElementById('fitseg').children].forEach(x=>x.classList.toggle('on',x===b));
  applyView();
};
function finger(ev){
  if(ev.touches && ev.touches[0]) return ev.touches[0];
  if(ev.changedTouches && ev.changedTouches[0]) return ev.changedTouches[0];
  return ev;
}
function ptFrom(ev){
  const src=finger(ev);
  const r=img.getBoundingClientRect();
  const w=Math.max(1,r.width), h=Math.max(1,r.height);
  const nx=clamp((src.clientX-r.left)/w,0,1), ny=clamp((src.clientY-r.top)/h,0,1);
  lastNx=nx; lastNy=ny;
  return {nx, ny, cx:src.clientX, cy:src.clientY, id: ev.pointerId||src.identifier||0};
}
function showDot(cx,cy,hold){
  const s=stage.getBoundingClientRect();
  dot.style.display='block';
  dot.style.left=(cx-s.left)+'px';
  dot.style.top=(cy-s.top)+'px';
  dot.classList.toggle('hold', !!hold);
}
function setScreenMode(kind){
  document.body.classList.toggle('drag-mode', kind==='move');
  document.body.classList.toggle('hold-mode', kind==='hold');
  const t=document.getElementById('modeBadgeText');
  if(t) t.textContent=kind==='move'?'MOVE':(kind==='hold'?'HOLD':'');
}
function aim(p, why){
  armed=true; lastNx=p.nx; lastNy=p.ny; showDot(p.cx||p.x, p.cy||p.y, false);
  hint.textContent=(why||'Armed')+' — L / R / Scroll act here';
}
function send(kind, nx, ny, extra){
  extra=Object.assign({}, extra||{});
  const winOps=/^(focus|maximize|minimize|restore|close|move_window|scroll)$/.test(kind);
  if(activeHwnd && extra.hwnd==null && (phoneFocus || winOps)) extra.hwnd=activeHwnd;
  const payload=Object.assign({kind,nx:nx,ny:ny,target}, extra);
  if(liveOk && live && live.readyState===1){
    try{ live.send(JSON.stringify(payload)); return Promise.resolve({ok:true, via:'ws'}); }catch(_){}
  }
  const hot=/^(drag|scroll|joy|nudge|stick|move|hover|down|up|hold|press|release|move_window|type_field)$/.test(kind);
  const p=fetch('/v1/phoneai/portal/touch',{
    method:'POST',
    credentials:'include',
    keepalive:true,
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)
  });
  if(hot) return p.catch(()=>{});
  return p.then(async r=>{
    let j={};
    try{ j=await r.json(); }catch(_){ j={ok:false,error:'HTTP '+r.status}; }
    if(!r.ok){ hint.textContent=j.error||('Touch HTTP '+r.status); return j; }
    const hid=parseInt((j.focus&&j.focus.hwnd)||j.hwnd||0,10);
    if(hid) activeHwnd=hid;
    if(j && j.focus && j.focus.title) hint.textContent=(j.maximized?'Fullscreen: ':'Main: ')+j.focus.title;
    if(kind==='focus' || kind==='maximize' || kind==='minimize' || kind==='close' || kind==='restore' || (j && j.focus && j.focus.main)) loadWins();
    if(j && j.ok===false && j.error) hint.textContent=j.error;
    return j;
  }).catch(()=>{ hint.textContent='Touch failed — check host / tunnel'; });
}
let liveBackoff=400;
function openLive(){
  const proto=location.protocol==='https:'?'wss':'ws';
  try{ live=new WebSocket(proto+'://'+location.host+'/v1/phoneai/portal/ws'); }
  catch(_){ live=null; setTimeout(openLive, liveBackoff); return; }
  live.binaryType='blob';
  live.onopen=()=>{ liveOk=true; liveBackoff=400; applyNet(); hint.textContent='Live desk — 1:1 laptop in this pane · '+net.label+' · '+net.fps+'fps'; };
  live.onclose=()=>{ liveOk=false; applyNet(); liveBackoff=Math.min(liveBackoff*1.6, 4000); setTimeout(openLive, liveBackoff); };
  live.onerror=()=>{};
  live.onmessage=ev=>{
    if(typeof ev.data==='string') return;
    latestBlob=ev.data;
    if(!painting) requestAnimationFrame(flushFrame);
  };
}
let latestBlob=null, painting=false;
function flushFrame(){
  const blob=latestBlob; latestBlob=null;
  if(!blob){ painting=false; return; }
  painting=true;
  const url=URL.createObjectURL(blob);
  const prev=blobUrl;
  img.onload=()=>{
    noteFrame();
    layout();
    if(prev && prev!==url) URL.revokeObjectURL(prev);
    blobUrl=url;
    painting=false;
    if(latestBlob) requestAnimationFrame(flushFrame);
  };
  img.src=url;
}
function b64urlToBuf(s){
  s=String(s||'').replace(/-/g,'+').replace(/_/g,'/');
  while(s.length%4) s+='=';
  const bin=atob(s);
  const u=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
  return u.buffer;
}
function strToBuf(s){ return Uint8Array.from(String(s), c=>c.charCodeAt(0)).buffer; }
function bufToB64url(buf){
  const u=new Uint8Array(buf); let s='';
  for(let i=0;i<u.length;i++) s+=String.fromCharCode(u[i]);
  return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
async function faceStart(kind){
  const r=await fetch('/v1/auth/passkey/begin?kind='+kind,{credentials:'include'});
  const j=await r.json();
  if(!j.ok) throw new Error(j.error||j.hint||'Face ID not ready');
  const pk=j.publicKey;
  pk.challenge=strToBuf(pk.challenge);
  if(pk.user&&pk.user.id) pk.user.id=b64urlToBuf(pk.user.id);
  if(pk.allowCredentials) pk.allowCredentials=pk.allowCredentials.map(c=>({type:'public-key',id:b64urlToBuf(c.id)}));
  const cred=kind==='register'
    ? await navigator.credentials.create({publicKey:pk})
    : await navigator.credentials.get({publicKey:pk});
  const payload={
    id:cred.id,
    rawId:bufToB64url(cred.rawId),
    type:cred.type,
    response:{
      clientDataJSON:bufToB64url(cred.response.clientDataJSON),
      attestationObject:cred.response.attestationObject?bufToB64url(cred.response.attestationObject):undefined,
      authenticatorData:cred.response.authenticatorData?bufToB64url(cred.response.authenticatorData):undefined,
      signature:cred.response.signature?bufToB64url(cred.response.signature):undefined
    }
  };
  const path=kind==='register'?'/v1/auth/passkey/register':'/v1/auth/passkey/login';
  const done=await fetch(path,{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({credential:payload})});
  return done.json();
}
async function faceGate(){
  if(!window.PublicKeyCredential) return true;
  const lan=/^(127\.0\.0\.1|localhost|192\.168\.|10\.)/.test(location.hostname);
  try{
    const me=await fetch('/v1/auth/me',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
    if(me && me.ok) return true;
  }catch(_){}
  if(lan){
    try{ await faceStart('register'); }catch(_){}
    return true;
  }
  if(hint) hint.textContent='Face ID to open this PC on the tunnel — no password';
  try{
    const j=await faceStart('login');
    if(j && j.ok){ if(hint) hint.textContent='Face ID · live desk'; return true; }
  }catch(_){}
  try{
    const j=await faceStart('register');
    if(j && j.ok) return true;
  }catch(e){
    if(hint) hint.textContent='Pair this phone: open Portal on home Wi-Fi once (Face ID), then the tunnel works.';
    return false;
  }
  return true;
}
document.getElementById('faceBtn').onclick=()=>{ faceGate().then(()=>{ applyNet(); openLive(); applyView(); }); };
document.getElementById('pairBtn').onclick=async()=>{
  const lan=/^(127\.0\.0\.1|localhost|192\.168\.|10\.)/.test(location.hostname);
  if(lan){
    const j=await fetch('/v1/auth/device/mint',{credentials:'include'}).then(r=>r.json()).catch(()=>({}));
    hint.textContent=j.code?('Pair code '+j.code+' — 10 min. On the tunnel: Pair, enter code, then Face ID on this phone. Code alone is not a login.'):(j.error||'Could not mint');
    return;
  }
  const code=prompt('Pair code from the PC, then Face ID on this phone');
  if(!code) return;
  if(!window.PublicKeyCredential){ hint.textContent='This phone needs a passkey / Face ID to pair'; return; }
  try{
    const started=await fetch('/v1/auth/device/begin',{credentials:'include'}).then(r=>r.json());
    if(!started.ok){ hint.textContent=started.error||'Mint a code on the PC first'; return; }
    const pk=started.publicKey;
    pk.challenge=strToBuf(pk.challenge);
    if(pk.user&&pk.user.id) pk.user.id=b64urlToBuf(pk.user.id);
    const cred=await navigator.credentials.create({publicKey:pk});
    const payload={
      id:cred.id,
      rawId:bufToB64url(cred.rawId),
      type:cred.type,
      response:{
        clientDataJSON:bufToB64url(cred.response.clientDataJSON),
        attestationObject:cred.response.attestationObject?bufToB64url(cred.response.attestationObject):undefined
      }
    };
    const j=await fetch('/v1/auth/device/redeem',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({code,credential:payload})}).then(r=>r.json()).catch(()=>({}));
    if(j && j.ok){ hint.textContent='Paired phone (device seat) — not the owner login'; applyNet(); openLive(); applyView(); }
    else hint.textContent=j.error||'Pair failed — code + Face ID required';
  }catch(e){ hint.textContent=(e&&e.message)||'Pair cancelled'; }
};
faceGate().then(()=>{ openLive(); applyNet(); }).catch(()=>{ openLive(); applyNet(); });
if(navigator.connection){ navigator.connection.addEventListener('change', applyNet); }
function loadWins(){
  fetch('/v1/phoneai/portal/windows').then(r=>r.json()).then(j=>{
    const el=document.getElementById('tabs');
    const list=j.windows||[];
    el.innerHTML=list.map(w=>{
      const t=(w.title||('hwnd '+w.hwnd)).replace(/[<>]/g,'');
      const mark=w.minimized?'· ':'';
      const on=w.focused?' on':'';
      return '<div class="wtab'+on+'" data-hwnd="'+w.hwnd+'"><span class="chrome">'
        +'<button type="button" class="wmin" data-act="minimize" aria-label="Minimize">–</button>'
        +'<button type="button" class="wmax" data-act="maximize" aria-label="Maximize">□</button>'
        +'<button type="button" class="wclose" data-act="close" aria-label="Close">×</button>'
        +'</span><button type="button" class="wtitle">'+mark+t.slice(0,28)+'</button></div>';
    }).join('') || '<button type="button" disabled>No windows</button>';
  }).catch(()=>{});
}
loadWins(); setInterval(()=>{ if(!document.body.classList.contains('hud-off')) loadWins(); }, 4000);
document.getElementById('tabs').onclick=e=>{
  const tab=e.target.closest('[data-hwnd]'); if(!tab) return;
  e.preventDefault(); e.stopPropagation();
  const hwnd=parseInt(tab.getAttribute('data-hwnd'),10);
  const actEl=e.target.closest('[data-act]');
  activeHwnd=hwnd;
  if(actEl){
    const act=actEl.getAttribute('data-act');
    send(act, 0.5, 0.5, {hwnd:hwnd});
    hint.textContent=(act==='close'?'Closing':act==='minimize'?'Minimizing':'Max / restore')+' that window';
    setTimeout(loadWins, 350);
    return;
  }
  const now=Date.now();
  if(tabTaps.hwnd===hwnd && now-tabTaps.t<900) tabTaps.n+=1; else tabTaps={hwnd:hwnd,n:1,t:now};
  tabTaps.t=now;
  if(tabTaps.n>=3){
    tabTaps.n=0;
    send('maximize', 0.5, 0.5, {hwnd:hwnd});
    hint.textContent='Expanding that window to the whole screen';
  } else {
    send('focus', 0.5, 0.5, {hwnd:hwnd});
    hint.textContent=tabTaps.n===2?'Tap once more to fill the screen':'Focused — swipe to scroll this window';
  }
};
const PIN=['edge','explorer','code','cursor','wt','notepad','calc','settings','chrome','antigravity','discord','github','powershell','grok_app'];
function loadApps(){
  fetch('/v1/phoneai/portal/apps').then(r=>r.json()).then(j=>{
    const all=j.apps||[];
    const by={}; all.forEach(a=>by[a.id]=a);
    const ordered=[...PIN.filter(id=>by[id]), ...all.map(a=>a.id).filter(id=>PIN.indexOf(id)<0)].slice(0,28);
    document.getElementById('apps').innerHTML=ordered.map(id=>{
      const a=by[id]; if(!a) return '';
      return '<button type="button" data-app="'+a.id+'">'+(a.label||a.id)+'</button>';
    }).join('');
  }).catch(()=>{});
}
loadApps();
document.getElementById('apps').onclick=e=>{
  const b=e.target.closest('[data-app]'); if(!b) return;
  e.preventDefault(); e.stopPropagation();
  send('open', lastNx, lastNy, {text: b.getAttribute('data-app'), app: b.getAttribute('data-app')});
  hint.textContent='Opening '+b.textContent+'…';
  setTimeout(loadWins, 800);
};
function tick(){
  if(document.hidden){ setTimeout(tick, 800); return; }
  if(liveOk && lastFrameAt && (Date.now()-lastFrameAt)<2500){ setTimeout(tick, 700); return; }
  if(busy){ setTimeout(tick, 200); return; }
  busy=true;
  const im=new Image();
  im.onload=()=>{ img.src=im.src; layout(); noteFrame(); busy=false; setTimeout(tick, 400); };
  im.onerror=()=>{ busy=false; setTimeout(tick, 600); };
  im.src='/v1/phoneai/portal/frame?target='+encodeURIComponent(target)+'&hwnd='+(activeHwnd||0)+'&max_w='+net.max_w+'&q='+net.q+'&t='+Date.now();
}
document.addEventListener('visibilitychange', ()=>{
  if(!document.hidden){ lastFrameAt=0; if(!liveOk) openLive(); }
});
tick();
img.addEventListener('load', layout);
document.getElementById('mode').onclick=e=>{
  const b=e.target.closest('button'); if(!b) return;
  mode=b.getAttribute('data-m');
  [...document.getElementById('mode').children].forEach(x=>x.classList.toggle('on',x===b));
  hint.textContent=mode==='touch'?'Touch on. Press a spot, then L / R / Scroll.':'Watch only.';
};
const ios=/iP(hone|ad|od)|Android/i.test(navigator.userAgent||'');
const fingers=new Map();
let gest=null, longTimer=null, pinch=null, startAt=null, usingTouch=false;
function clearLong(){ if(longTimer){ clearTimeout(longTimer); longTimer=null; } }
function fid(ev){ return ev.pointerId!=null?ev.pointerId:(finger(ev).identifier||0); }
function syncFingers(ev){
  if(ev.touches && ev.touches.length){
    fingers.clear();
    for(let i=0;i<ev.touches.length;i++){
      const t=ev.touches[i];
      fingers.set(t.identifier, {x:t.clientX, y:t.clientY});
    }
    return fingers.size;
  }
  const p=ptFrom(ev);
  if(ev.type==='pointerup'||ev.type==='pointercancel'||ev.type==='mouseup'){
    fingers.delete(fid(ev));
  } else {
    fingers.set(fid(ev), {x:p.cx, y:p.cy});
  }
  return fingers.size;
}
function emitScroll(nx, ny, dx, dy){
  const now=Date.now();
  if(now-lastDrag<16) return;
  lastDrag=now;
  const extra=activeHwnd?{dy:dy, dx:dx, hwnd:activeHwnd}:{dy:dy, dx:dx};
  send('scroll', nx, ny, extra);
  hint.textContent=activeHwnd?'Scrolling this window':'Scrolling the PC';
}
function emitMoveWin(p){
  if(!startAt) return;
  if(!startAt.seeded){ startAt.lastX=p.cx; startAt.lastY=p.cy; startAt.seeded=true; return; }
  const now=Date.now();
  if(now-lastDrag<16) return;
  lastDrag=now;
  const r=img.getBoundingClientRect();
  const dx=(p.cx-startAt.lastX)/Math.max(1,r.width);
  const dy=(p.cy-startAt.lastY)/Math.max(1,r.height);
  startAt.lastX=p.cx; startAt.lastY=p.cy;
  send('move_window', startAt.nx, startAt.ny, {dx:dx, dy:dy, hwnd:activeHwnd||undefined});
  hint.textContent='Moving the desktop window';
  setScreenMode('move');
}
function onDown(ev){
  if(mode!=='touch') return;
  const n=syncFingers(ev);
  const p=ptFrom(ev); showDot(p.cx,p.cy,false);
  if(n>=2){
    clearLong(); gest='twoscroll'; setScreenMode('');
    const pts=[...fingers.values()];
    pinch={d:Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y)||1, z:zoom, px:panX, py:panY, mx:(pts[0].x+pts[1].x)/2, my:(pts[0].y+pts[1].y)/2};
    return;
  }
  const now=Date.now();
  startAt={x:p.cx, y:p.cy, nx:p.nx, ny:p.ny, cx:p.cx, cy:p.cy, lastX:p.cx, lastY:p.cy, moved:false};
  if(now-lastTap<360){
    lastTap=0; gest='move'; setScreenMode('move'); aim(p, 'Double-tap — drag to move this window'); clearLong(); return;
  }
  gest='pending';
  const holdMs=(ev.pressure&&ev.pressure>0.45)?140:220;
  longTimer=setTimeout(()=>{
    if(gest==='pending'){
      gest='hold';
      send('down', startAt.nx, startAt.ny);
      showDot(startAt.cx, startAt.cy, true);
      setScreenMode('hold');
      hint.textContent='Holding click — lift to release, slide to drag';
    }
  }, holdMs);
}
function onMove(ev){
  const n=syncFingers(ev);
  const p=ptFrom(ev);
  if(n>=2){
    const pts=[...fingers.values()];
    const d=Math.hypot(pts[0].x-pts[1].x, pts[0].y-pts[1].y)||1;
    const mx=(pts[0].x+pts[1].x)/2, my=(pts[0].y+pts[1].y)/2;
    if(!pinch){
      pinch={d:d, z:zoom, px:panX, py:panY, mx:mx, my:my};
    }
    const scaleChange=Math.abs(d/(pinch.d||1)-1);
    if(scaleChange<0.16){
      gest='twoscroll';
      emitScroll(lastNx, lastNy, (mx-pinch.mx)/70, (my-pinch.my)/50);
      pinch.mx=mx; pinch.my=my;
    } else {
      const nz=clamp(pinch.z*(d/pinch.d), 1, 5);
      const cx=(pinch.mx-pinch.px)/pinch.z, cy=(pinch.my-pinch.py)/pinch.z;
      zoom=nz; panX=mx-cx*nz; panY=my-cy*nz; applyView();
    }
    return;
  }
  if(mode!=='touch' || !startAt) return;
  showDot(p.cx,p.cy, gest==='hold');
  if(gest==='pending' || gest==='hold' || gest==='armed'){
    const nowH=Date.now();
    if(nowH-lastDrag>=16){ lastDrag=nowH; send('hover', p.nx, p.ny); }
  }
  const dist=Math.hypot(p.cx-startAt.x, p.cy-startAt.y);
  if(gest==='move' && dist>8){
    startAt.moved=true; emitMoveWin(p); return;
  }
  if(gest==='pending' && dist>10){
    clearLong(); gest='drag'; send('down', startAt.nx, startAt.ny);
  } else if(gest==='hold' && dist>10){
    gest='drag';
  }
  if(gest==='scroll'){
    const dy=(p.cy-startAt.lastY)/48;
    const dx=(p.cx-startAt.lastX)/64;
    startAt.lastY=p.cy; startAt.lastX=p.cx;
    emitScroll(startAt.nx, startAt.ny, dx, dy);
  } else if(gest==='drag' || gest==='hold'){
    const now=Date.now();
    if(now-lastDrag<16) return;
    lastDrag=now;
    send('drag', p.nx, p.ny);
  }
}
function onUp(ev){
  if(ev.touches) { /* remaining */ }
  else { fingers.delete(fid(ev)); }
  if((ev.touches?ev.touches.length:fingers.size)<2) pinch=null;
  if(mode!=='touch'){ if(!fingers.size) gest=null; return; }
  const p=ptFrom(ev);
  clearLong();
  const now=Date.now();
  const left=(ev.touches?ev.touches.length:0)===0;
  if(gest==='pending'){
    if(now-streamTaps.t<420) streamTaps.n+=1; else streamTaps={n:1,t:now};
    streamTaps.t=now;
    if(streamTaps.n>=3){
      streamTaps.n=0;
      aim(p, 'Triple-tap');
      send('maximize', p.nx, p.ny);
      hint.textContent='Expanding that window to the whole screen';
    } else {
      lastTap=now; aim(p, 'Tap'); send('hover', p.nx, p.ny); send('tap', p.nx, p.ny);
      try{ keys.blur(); }catch(_){}
    }
  } else if(gest==='drag' || gest==='hold'){
    send('up', p.nx, p.ny);
  } else if(gest==='move' && !startAt.moved){
    send('dbl', p.nx, p.ny);
  }
  if(left){ gest=null; startAt=null; fingers.clear(); setScreenMode(''); dot.classList.remove('hold'); }
}
stage.addEventListener('touchstart', ev=>{ usingTouch=true; ev.preventDefault(); onDown(ev); }, {passive:false});
stage.addEventListener('touchmove', ev=>{ ev.preventDefault(); onMove(ev); }, {passive:false});
stage.addEventListener('touchend', ev=>{ ev.preventDefault(); onUp(ev); }, {passive:false});
stage.addEventListener('touchcancel', ev=>{ onUp(ev); }, {passive:false});
stage.addEventListener('pointerdown', ev=>{
  if(usingTouch || ev.pointerType==='touch') return;
  ev.preventDefault();
  if(!ios){ try{ stage.setPointerCapture(ev.pointerId); }catch(_){} }
  onDown(ev);
}, {passive:false});
stage.addEventListener('pointermove', ev=>{
  if(usingTouch || ev.pointerType==='touch') return;
  onMove(ev);
}, {passive:false});
stage.addEventListener('pointerup', ev=>{ if(usingTouch || ev.pointerType==='touch') return; onUp(ev); });
stage.addEventListener('pointercancel', ev=>{ if(usingTouch || ev.pointerType==='touch') return; onUp(ev); });
stage.addEventListener('contextmenu', ev=>ev.preventDefault());

function bindPress(el, down, up){
  if(!el) return;
  let on=false;
  const s=ev=>{ ev.preventDefault(); ev.stopPropagation(); if(on) return; on=true; el.classList.add('held'); down(); };
  const e=ev=>{ if(!on) return; on=false; el.classList.remove('held'); if(up) up(); };
  el.addEventListener('touchstart', s, {passive:false});
  el.addEventListener('touchend', e);
  el.addEventListener('touchcancel', e);
  el.addEventListener('mousedown', s);
  el.addEventListener('mouseup', e);
  el.addEventListener('mouseleave', e);
}
bindPress(document.getElementById('lmb'), ()=>{ send('down', lastNx, lastNy); setScreenMode('hold'); hint.textContent='Holding left click'; }, ()=>{ send('up', lastNx, lastNy); setScreenMode(''); });
bindPress(document.getElementById('rmb'), ()=>send('right', lastNx, lastNy));
function setPadMode(m){
  padMode=m==='move'?'move':'scroll';
  document.body.classList.toggle('pad-move', padMode==='move');
  const mb=document.getElementById('moveBtn');
  if(mb) mb.classList.toggle('on', padMode==='move');
  setScreenMode(padMode==='move'?'move':'');
  hint.textContent=padMode==='move'?'Move pad — hold arrows to slide the window':'Scroll pad — hold arrows. Toggle Move for window drag.';
}
bindPress(document.getElementById('moveBtn'), ()=>{
  setPadMode(padMode==='move'?'scroll':'move');
  if(padMode==='move'){
    gest='move';
    startAt={x:lastNx, y:lastNy, nx:lastNx, ny:lastNy, cx:0, cy:0, lastX:0, lastY:0, moved:false};
  }
});
let padHold=null;
function holdPad(dx, dy){
  let n=0;
  const fire=()=>{
    n++;
    if(padMode==='move'){
      send('move_window', lastNx, lastNy, {dx:dx*0.035, dy:dy*0.035, hwnd:activeHwnd||undefined});
      hint.textContent='Moving window';
    } else {
      send('scroll', lastNx, lastNy, {dx:dx, dy:dy});
      hint.textContent=activeHwnd?'Scrolling this window':'Scrolling the PC';
    }
    padHold=setTimeout(fire, n>5?38:72);
  };
  fire();
}
function endPad(){ if(padHold){ clearTimeout(padHold); padHold=null; } }
bindPress(document.getElementById('sup'), ()=>holdPad(0, padMode==='move'?-1:-0.42), endPad);
bindPress(document.getElementById('sdn'), ()=>holdPad(0, padMode==='move'?1:0.42), endPad);
bindPress(document.getElementById('scL'), ()=>holdPad(padMode==='move'?-1:-0.42, 0), endPad);
bindPress(document.getElementById('scR'), ()=>holdPad(padMode==='move'?1:0.42, 0), endPad);
bindPress(document.getElementById('focusBtn'), ()=>{
  setPhoneFocus(!phoneFocus);
});
const desk2Btn=document.getElementById('desk2Btn');
if(desk2Btn) desk2Btn.onclick=()=>{
  const on=target!=='monitor:1';
  target=on?'monitor:1':'desktop';
  phoneFocus=false;
  desk2Btn.classList.toggle('on', on);
  applyNet();
  hint.textContent=on?'Desk 2 · secondary / virtual display':'Laptop · full desktop';
};
document.getElementById('hudbtn').onclick=()=>{
  const off=document.body.classList.contains('hud-off');
  if(off) goGlass();
  setHud(off);
};
document.getElementById('focusPill').onclick=()=>setPhoneFocus(!phoneFocus);
function setTypePad(on){
  const box=document.getElementById('typeform');
  const tb=document.getElementById('typeBtn');
  if(box) box.classList.toggle('on', !!on);
  if(tb) tb.classList.toggle('on', !!on);
  keys.readOnly=!on;
  keys.tabIndex=on?0:-1;
  if(on){ try{ keys.focus(); }catch(_){} }
  else { try{ keys.blur(); }catch(_){} lastTyped=''; keys.value=''; }
  hint.textContent=on?'Keyboard on — tap Done when finished':'Tap Type only when you need the keyboard.';
}
document.getElementById('typeBtn').onclick=()=>{
  const on=!document.getElementById('typeform').classList.contains('on');
  setTypePad(on);
};
document.getElementById('typeHide').onclick=ev=>{ ev.preventDefault(); setTypePad(false); };
setHud(false); autoFit(); applyView();

keys.addEventListener('input', ()=>{
  const v=keys.value; let i=0;
  while(i<v.length && i<lastTyped.length && v[i]===lastTyped[i]) i++;
  const back=lastTyped.length-i, add=v.slice(i);
  lastTyped=v;
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
function submitType(ev){ ev.preventDefault(); send('key', lastNx, lastNy, {vk:13}); lastTyped=''; keys.value=''; setTypePad(false); }
document.getElementById('kb').onsubmit=submitType;
document.getElementById('typeform').onsubmit=submitType;
(function(){
  const pad=document.getElementById('joy'), knob=document.getElementById('knob');
  if(!pad||!knob) return;
  let on=false, ox=0, oy=0, raf=0, jx=0, jy=0;
  function setKnob(dx,dy){
    const m=Math.hypot(dx,dy)||1, r=28;
    const nx=dx/m*Math.min(m,r), ny=dy/m*Math.min(m,r);
    knob.style.transform='translate('+nx+'px,'+ny+'px)';
    jx=Math.round(nx*3.2); jy=Math.round(ny*3.2);
    if(raf) return;
    raf=requestAnimationFrame(()=>{ raf=0; send('joy', lastNx, lastNy, {dx:jx, dy:jy}); });
  }
  function start(ev){ on=true; const t=finger(ev); const r=pad.getBoundingClientRect(); ox=r.left+r.width/2; oy=r.top+r.height/2; ev.preventDefault(); }
  function move(ev){ if(!on) return; ev.preventDefault(); const t=finger(ev); setKnob(t.clientX-ox, t.clientY-oy); }
  function end(ev){ on=false; knob.style.transform=''; }
  pad.addEventListener('touchstart', start, {passive:false});
  pad.addEventListener('touchmove', move, {passive:false});
  pad.addEventListener('touchend', end);
  pad.addEventListener('pointerdown', ev=>{ if(ev.pointerType==='touch') return; start(ev); });
  pad.addEventListener('pointermove', ev=>{ if(ev.pointerType==='touch') return; move(ev); });
  pad.addEventListener('pointerup', end);
})();
</script>
</body></html>
"""


def phoneai_portal_html() -> str:
    return PHONEAI_PORTAL_HTML


PHONEAI_GLASSES_HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="theme-color" content="#000"/>
<title>PhoneAI Glasses + AirPods</title>
<style>
:root{--g:#00ff86;--fg:#f7f7f4;--muted:#9a9aa6}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:#05060a;color:var(--fg);font-family:ui-sans-serif,system-ui}
body{display:flex;flex-direction:column;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.top{display:flex;gap:10px;align-items:center;padding:8px 12px;flex-wrap:wrap}
.top a{color:var(--muted);text-decoration:none}
.hud{display:flex;gap:8px;padding:0 12px 8px;flex-wrap:wrap}
.dot{width:10px;height:10px;border-radius:50%;background:#555;display:inline-block;margin-right:6px}
.dot.on{background:var(--g);box-shadow:0 0 8px var(--g)}
.pill{background:#101018;border:1px solid rgba(255,255,255,.1);border-radius:999px;padding:6px 10px;font-size:12px;font-weight:700}
.cards{margin:0 12px;border:1px solid rgba(0,255,134,.28);border-radius:16px;padding:14px 16px;background:#0b0c12;min-height:110px}
.cards b{display:block;font-size:22px;letter-spacing:-.03em;margin:0 0 6px}
.cards span{display:block;color:var(--muted);font-size:15px;line-height:1.35}
.stream{display:none;position:fixed;inset:0;z-index:1;background:#000;margin:0;border-radius:0}
.stream.on{display:block;z-index:10}
.stream img{width:100%;height:100%;object-fit:contain;touch-action:none}
.stream .peek{position:absolute;top:8px;left:8px;z-index:11;min-height:36px;border:0;border-radius:999px;background:rgba(5,6,10,.8);color:#00ff86;font-weight:800;padding:0 12px}
.typebox{position:fixed;left:10px;right:10px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:12;display:flex;gap:8px}
.typebox input{flex:1;min-height:44px;border-radius:12px;background:rgba(12,12,14,.9);color:#fff;border:1px solid rgba(255,255,255,.12);padding:10px}
.dot{position:absolute;width:22px;height:22px;border:2px solid #00ff86;border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;display:none;z-index:11}
.top,.hud,.cards,.row,.bar,.reply,.note{position:relative;z-index:2}
.reply{margin:8px 12px;font-size:16px;line-height:1.4;min-height:2.4em}
.row{display:flex;gap:8px;padding:8px 12px;overflow:auto;touch-action:pan-x}
.row button{flex:0 0 auto;min-height:44px;border:0;border-radius:12px;background:#14141c;color:#fff;font-weight:800;padding:0 12px}
.row button.go{background:var(--g);color:#042}
.bar{display:flex;gap:8px;padding:8px 12px}
input,button{font:inherit;border:0;border-radius:12px;min-height:48px}
input{flex:1;background:#14141c;color:#fff;padding:0 12px}
.bar button{background:var(--g);color:#042;font-weight:800;padding:0 14px}
.note{padding:0 12px 16px;color:var(--muted);font-size:12px}
.lis{outline:2px solid var(--g)}
video,canvas{display:none}
</style></head>
<body>
<div class="top">
  <a href="/phoneai/app">Home</a>
  <b id="modeLabel">Glasses</b>
  <a href="/phoneai/portal">Portal</a>
  <a href="/phoneai/airpods">AirPods</a>
</div>
<div class="hud">
  <span class="pill"><i class="dot" id="dHost"></i>Host</span>
  <span class="pill"><i class="dot" id="dGlass"></i>Glasses</span>
  <span class="pill"><i class="dot" id="dPods"></i>AirPods</span>
  <span class="pill" id="batt">Bat —</span>
</div>
<div class="cards" id="cards"><b>PhoneAI</b><span>Connecting…</span><span></span></div>
<div class="stream" id="stream"><button type="button" class="peek" id="peek">HUD</button><img id="f" alt="PC"/><div class="dot" id="gdot"></div></div>
<form class="typebox" id="gtf"><input id="gkeys" placeholder="Tap a field, type from glasses"/><button>Send</button></form>
<p class="reply" id="r">Always listen waits for “PhoneAI …”. Glance is 3 lines — no JPEG until you tap Stream. Dictation types until you say send.</p>
<div class="row" id="chips">
  <button type="button" class="go" id="listen">Listen</button>
  <button type="button" id="always">Always</button>
  <button type="button" id="dict">Dictation</button>
  <button type="button" id="streamBtn">Stream</button>
  <button type="button" id="cam">Camera</button>
  <button type="button" data-say="look">Look</button>
  <button type="button" data-say="left window">Left</button>
  <button type="button" data-say="right window">Right</button>
  <button type="button" data-say="scroll down">Scroll</button>
</div>
<form class="bar" id="v"><input id="t" placeholder="PhoneAI look · left window · dictation · send"/><button>Go</button></form>
<p class="note">AirPods on the phone. Glasses browser: /phoneai/glasses. Wake word: PhoneAI.</p>
<video id="vid" autoplay playsinline></video><canvas id="cv"></canvas>
<script>
const air=/airpods/.test(location.pathname); if(air) document.documentElement.classList.add('air');
document.getElementById('modeLabel').textContent=air?'AirPods':'Glasses HUD';
let rec=null, listening=false, always=false, streamOn=false, busy=false, dictOn=false;
const img=document.getElementById('f');
function speak(text){
  const s=String(text||'').trim().slice(0,240); if(!s) return;
  try{ window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(s); u.rate=1.04; const vs=speechSynthesis.getVoices()||[]; const v=vs.find(x=>/en/i.test(x.lang||'')); if(v) u.voice=v; speechSynthesis.speak(u);}catch(_){}
}
function paintHud(j){
  const h=j.hud||{}, g=j.glance||{};
  document.getElementById('dHost').classList.toggle('on', !!(g.host || h.host));
  document.getElementById('dGlass').classList.toggle('on', navigator.onLine);
  document.getElementById('dPods').classList.toggle('on', !!(h.inEar || h.airpods || listening));
  const lines=g.lines||[];
  document.getElementById('cards').innerHTML='<b>'+(lines[0]||j.focused||'desktop').replace(/</g,'')+'</b><span>'+(lines[1]||'')+'</span><span>'+(lines[2]||'')+'</span>';
  if(typeof j.dictation==='boolean') dictOn=j.dictation;
  document.getElementById('dict').classList.toggle('go', dictOn);
}
async function beat(extra){
  const body=Object.assign({glasses:!air, airpods:true, online:navigator.onLine, always:always}, extra||{});
  try{
    if(navigator.getBattery){ const b=await navigator.getBattery(); body.battery=b.level; document.getElementById('batt').textContent='Bat '+Math.round(b.level*100)+'%'; }
  }catch(_){}
  try{
    const j=await fetch('/v1/phoneai/wear',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());
    paintHud(j);
    return j;
  }catch(_){ document.getElementById('dHost').classList.remove('on'); return {}; }
}
beat(); setInterval(()=>beat(), 5000);
let glive=null, gnx=0.5, gny=0.5, gTyped='';
const gdot=document.getElementById('gdot');
const gkeys=document.getElementById('gkeys');
function gsend(kind, extra){
  const p=Object.assign({kind,nx:gnx,ny:gny,target:'desktop'}, extra||{});
  if(glive && glive.readyState===1){ glive.send(JSON.stringify(p)); return; }
  fetch('/v1/phoneai/portal/touch',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)}).catch(()=>{});
}
function openGLive(){
  try{ glive=new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/v1/phoneai/portal/ws'); }
  catch(_){ return; }
  glive.binaryType='blob';
  glive.onopen=()=>{ glive.send(JSON.stringify({kind:'cfg',target:'desktop',max_w:960,q:64,fps:10})); };
  glive.onclose=()=>{ if(streamOn) setTimeout(openGLive,800); };
  glive.onmessage=ev=>{ if(typeof ev.data==='string') return; const u=URL.createObjectURL(ev.data); img.onload=()=>URL.revokeObjectURL(u); img.src=u; };
}
function tick(){
  if(!streamOn || document.hidden){ setTimeout(tick, 800); return; }
  if(!glive || glive.readyState>1) openGLive();
  setTimeout(tick, 1200);
}
tick();
document.getElementById('peek').onclick=()=>{ streamOn=false; document.getElementById('stream').classList.remove('on'); };
const st=document.getElementById('stream');
st.addEventListener('touchstart', ev=>{ ev.preventDefault(); const t=ev.touches[0]; const r=img.getBoundingClientRect(); gnx=(t.clientX-r.left)/Math.max(1,r.width); gny=(t.clientY-r.top)/Math.max(1,r.height); gdot.style.display='block'; gdot.style.left=(t.clientX-st.getBoundingClientRect().left)+'px'; gdot.style.top=(t.clientY-st.getBoundingClientRect().top)+'px'; gsend('hover'); gsend('tap'); try{gkeys.blur();}catch(_){}; }, {passive:false});
gkeys.addEventListener('input', ()=>{ const v=gkeys.value; let i=0; while(i<v.length&&i<gTyped.length&&v[i]===gTyped[i]) i++; const back=gTyped.length-i, add=v.slice(i); gTyped=v; if(back) gsend('key',{vk:8,n:back}); if(add) gsend('key',{text:add}); });
document.getElementById('gtf').onsubmit=ev=>{ ev.preventDefault(); gsend('key',{vk:13}); gTyped=''; gkeys.value=''; };
async function run(text, extra){
  const t=(text||'').trim();
  if(!t && !extra) return;
  if(t) document.getElementById('r').textContent='…';
  const body=Object.assign({text:t, always:always, glasses:!air, airpods:true, online:navigator.onLine}, extra||{});
  try{
    const j=await fetch('/v1/phoneai/wear',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());
    paintHud(j);
    if(j.kind==='ignore'){ document.getElementById('r').textContent='Waiting for PhoneAI …'; return; }
    const reply=j.reply||j.error||'ok';
    document.getElementById('r').textContent=reply;
    if(reply) speak(reply);
  }catch(e){ document.getElementById('r').textContent='Host unreachable.'; }
}
document.getElementById('v').onsubmit=ev=>{ ev.preventDefault(); const i=document.getElementById('t'); run(i.value); i.value=''; };
document.getElementById('chips').onclick=e=>{
  const b=e.target.closest('button'); if(!b) return;
  if(b.id==='listen'){ armListen(false); return; }
  if(b.id==='always'){ always=!always; b.classList.toggle('go', always); armListen(true); document.getElementById('r').textContent=always?'Always on. Say PhoneAI then the command.':'Always off.'; return; }
  if(b.id==='dict'){ run(dictOn?'stop dictation':'dictation'); return; }
  if(b.id==='streamBtn'){ streamOn=!streamOn; document.getElementById('stream').classList.toggle('on', streamOn); b.classList.toggle('go', streamOn); if(streamOn) tick(); return; }
  if(b.id==='cam'){ snap(); return; }
  if(b.getAttribute('data-say')) run(b.getAttribute('data-say'));
};
function Rec(){ return window.SpeechRecognition||window.webkitSpeechRecognition; }
function armListen(){
  const C=Rec();
  if(!C){ document.getElementById('r').textContent='No speech engine — type instead.'; return; }
  if(rec){ try{ rec.stop(); }catch(_){} rec=null; }
  rec=new C(); rec.lang='en-US'; rec.interimResults=false; rec.continuous=!!always;
  rec.onresult=ev=>{
    const said=ev.results[ev.results.length-1][0].transcript||'';
    if(said) run(said);
  };
  rec.onend=()=>{ listening=false; document.getElementById('listen').classList.remove('lis'); if(always) setTimeout(()=>armListen(), 280); };
  rec.onerror=()=>{ listening=false; };
  try{ rec.start(); listening=true; document.getElementById('listen').classList.add('lis'); }catch(_){}
}
async function snap(){
  try{
    const v=document.getElementById('vid');
    if(!v.srcObject) v.srcObject=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});
    await new Promise(r=>setTimeout(r,400));
    const c=document.getElementById('cv'); c.width=v.videoWidth||720; c.height=v.videoHeight||960;
    c.getContext('2d').drawImage(v,0,0); const img=c.toDataURL('image/jpeg',0.82);
    run('what is this error', {image:img});
  }catch(e){ document.getElementById('r').textContent='Camera permission needed.'; }
}
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


def phoneai_airpods_html() -> str:
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
        "os_url": "/phoneai/os",
        "version": "1.1.0",
        "landing": "/phoneai",
        "app": "/phoneai/app",
        "mcp": "/phoneai/mcp",
        "registry": "/phoneai/registry",
        "docs": "/docs",
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
            "Code desk — Grok CLI · Codex CLI · Meta Muse · Gemini CLI in your GitHubs",
            "MCP apps inside the kernel (Pocket · Nexus · Loom · GitHub · Cloudflare · files)",
            "MCP · Agent Mail · Novae",
        ],
    }
