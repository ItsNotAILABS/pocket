"""TV, doorbell, and laptop-camera approval pages for PhoneAI."""

from __future__ import annotations


def tv_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>PhoneAI TV</title>
<meta name="theme-color" content="#000"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<style>
html,body{margin:0;width:100%;height:100%;height:100dvh;background:#000;color:#f4f4f5;font-family:ui-sans-serif,system-ui;overflow:hidden}
body{position:fixed;inset:0}
.stage{position:fixed;inset:0;background:#000}
img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;touch-action:none}
.hud{position:fixed;left:0;right:0;bottom:0;display:flex;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:linear-gradient(transparent,rgba(0,0,0,.75));z-index:4;overflow:auto}
.hud button,select{min-height:44px;border:0;border-radius:12px;background:#14141c;color:#fff;font-weight:800;padding:0 12px}
.hud button.go{background:#00ff86;color:#042}
.top{position:fixed;top:8px;left:12px;z-index:4;font-size:13px;color:#a1a1aa}
.top a{color:#a1a1aa;text-decoration:none;margin-left:10px}
</style></head>
<body>
<div class="top"><b id="h">TV</b><a href="/phoneai/portal">Phone</a></div>
<div class="stage" id="stage"><img id="f" alt="TV" src="/v1/phoneai/portal/frame?target=tv&max_w=1280&t=1" draggable="false"/></div>
<div class="hud">
  <select id="src"></select>
  <button class="go" type="button" id="l">Click</button>
  <button type="button" id="r">Right</button>
  <button type="button" id="u">▲</button>
  <button type="button" id="d">▼</button>
</div>
<script>
let nx=0.5, ny=0.5, live=null, liveOk=false, src='tv', hwnd=0;
const img=document.getElementById('f');
function pt(ev){
  const t=(ev.touches&&ev.touches[0])||ev;
  const r=img.getBoundingClientRect();
  nx=Math.max(0,Math.min(1,(t.clientX-r.left)/Math.max(1,r.width)));
  ny=Math.max(0,Math.min(1,(t.clientY-r.top)/Math.max(1,r.height)));
}
function send(kind, extra){
  const payload=Object.assign({kind,nx,ny,target:src,hwnd:hwnd}, extra||{});
  if(liveOk && live && live.readyState===1){ live.send(JSON.stringify(payload)); return; }
  fetch('/v1/phoneai/portal/touch',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
    .then(r=>r.json()).then(j=>{ document.getElementById('h').textContent=(j.focus&&j.focus.title)||src; }).catch(()=>{});
}
function openLive(){
  try{ live=new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/v1/phoneai/portal/ws'); }
  catch(_){ return; }
  live.binaryType='blob';
  live.onopen=()=>{ liveOk=true; live.send(JSON.stringify({kind:'cfg',target:src,hwnd:hwnd,max_w:1280,q:68,fps:18})); };
  live.onclose=()=>{ liveOk=false; setTimeout(openLive,800); };
  live.onmessage=ev=>{ if(typeof ev.data==='string') return; const u=URL.createObjectURL(ev.data); img.onload=()=>URL.revokeObjectURL(u); img.src=u; };
}
openLive();
fetch('/v1/phoneai/home').then(r=>r.json()).then(j=>{
  const m=((j.tv&&j.tv.monitors)||[]);
  const lan=((j.tv&&j.tv.lan)||[]);
  const sel=document.getElementById('src');
  sel.innerHTML=m.map(x=>'<option value="monitor:'+x.id+'">'+(x.label||('Display '+x.id))+'</option>').join('')
    + lan.map(t=>'<option value="lan:'+t.ip+'">'+(t.kind||'TV')+' '+t.ip+'</option>').join('');
  if(m.length>1){ const tv=m.find(x=>!x.primary)||m[m.length-1]; src='tv'; hwnd=tv.id; sel.value='monitor:'+tv.id; }
});
document.getElementById('src').onchange=()=>{
  const v=document.getElementById('src').value;
  if(v.startsWith('monitor:')){ src='monitor'; hwnd=parseInt(v.split(':')[1],10)||0; }
  else { src='tv'; hwnd=0; }
  if(liveOk) live.send(JSON.stringify({kind:'cfg',target:src,hwnd:hwnd,max_w:1280,q:68,fps:18}));
};
const stage=document.getElementById('stage');
stage.addEventListener('touchstart', ev=>{ ev.preventDefault(); pt(ev); send('tap'); }, {passive:false});
stage.addEventListener('click', ev=>{ pt(ev); send('tap'); });
document.getElementById('l').onclick=()=>send('tap');
document.getElementById('r').onclick=()=>send('right');
document.getElementById('u').onclick=()=>send('scroll',{dy:-0.5});
document.getElementById('d').onclick=()=>send('scroll',{dy:0.5});
</script>
</body></html>
"""


def doorbell_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>Doorbell · PhoneAI</title>
<style>
body{margin:0;background:#05060a;color:#f4f4f5;font-family:ui-sans-serif,system-ui;max-width:480px;margin:0 auto;padding:12px}
a{color:#8b8b98;text-decoration:none}
img{width:100%;border-radius:16px;background:#000;min-height:220px;object-fit:contain}
input,button,select{font:inherit;min-height:44px;border-radius:12px;border:1px solid rgba(255,255,255,.12);background:#14141c;color:#fff;padding:8px 10px}
button.go{background:#00ff86;color:#042;border:0;font-weight:800}
.row{display:flex;gap:8px;margin:8px 0;flex-wrap:wrap}
</style></head>
<body>
<p><a href="/phoneai/app">Home</a> · <a href="/phoneai/cam">Laptop cam</a></p>
<h1>Doorbell</h1>
<p id="st" style="color:#8b8b98">LAN cameras. Add an MJPEG/HTTP snapshot URL, or use the laptop cam with approval.</p>
<img id="f" alt="doorbell" src="/v1/phoneai/doorbell/frame?t=1"/>
<div class="row">
  <select id="cam"></select>
  <button class="go" type="button" id="go">Watch</button>
</div>
<form class="row" id="add">
  <input id="n" placeholder="Front door" style="flex:1"/>
  <input id="u" placeholder="http://192.168.x.x/jpg" style="flex:1"/>
  <button class="go">Add</button>
</form>
<script>
let id='';
async function cams(){
  const j=await fetch('/v1/phoneai/home').then(r=>r.json());
  const list=(j.doorbell&&j.doorbell.cameras)||[];
  document.getElementById('cam').innerHTML=list.map(c=>'<option value="'+c.id+'">'+(c.name||c.id)+'</option>').join('');
  if(!id && list[0]) id=list[0].id;
}
cams();
let busy=false;
function tick(){
  if(document.hidden||busy){ setTimeout(tick,700); return; }
  busy=true; const img=document.getElementById('f');
  img.onload=()=>{busy=false;setTimeout(tick,900)}; img.onerror=()=>{busy=false;setTimeout(tick,1400)};
  img.src='/v1/phoneai/doorbell/frame?id='+encodeURIComponent(id)+'&t='+Date.now();
}
tick();
document.getElementById('go').onclick=()=>{ id=document.getElementById('cam').value; };
document.getElementById('add').onsubmit=async ev=>{
  ev.preventDefault();
  await fetch('/v1/phoneai/doorbell',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('n').value,url:document.getElementById('u').value,kind:'mjpeg'})});
  cams();
};
</script>
</body></html>
"""


def cam_phone_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>Laptop camera · PhoneAI</title>
<style>
body{margin:0;background:#05060a;color:#f4f4f5;font-family:ui-sans-serif,system-ui;max-width:480px;margin:0 auto;padding:16px}
a{color:#8b8b98}
img{width:100%;border-radius:16px;background:#000;min-height:240px}
button{min-height:48px;border:0;border-radius:12px;background:#00ff86;color:#042;font-weight:800;width:100%;margin:10px 0}
.muted{color:#8b8b98}
</style></head>
<body>
<p><a href="/phoneai/app">Home</a></p>
<h1>Laptop camera</h1>
<p class="muted">The PC must tap Allow. The camera never turns on from the phone alone.</p>
<p id="st">Not requested.</p>
<img id="f" alt="cam"/>
<button type="button" id="ask">Request camera</button>
<script>
let live=false, busy=false;
async function st(){
  const j=await fetch('/v1/phoneai/home').then(r=>r.json());
  const c=j.laptop_cam||{};
  document.getElementById('st').textContent=c.approved?'Approved — streaming':(c.pending?'Waiting for Allow on the PC':'Not requested');
  live=!!c.approved;
}
st(); setInterval(st, 2000);
document.getElementById('ask').onclick=async()=>{
  await fetch('/v1/phoneai/cam/request',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
  st();
};
function tick(){
  if(!live||document.hidden||busy){ setTimeout(tick,800); return; }
  busy=true; const img=document.getElementById('f');
  img.onload=()=>{busy=false;setTimeout(tick,700)}; img.onerror=()=>{busy=false;setTimeout(tick,1200)};
  img.src='/v1/phoneai/cam/frame?t='+Date.now();
}
tick();
</script>
</body></html>
"""


def cam_approve_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Allow laptop camera?</title>
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#09090b;color:#fafafa;font-family:ui-sans-serif,system-ui}
.card{width:min(420px,92vw);background:#141416;border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px}
h1{margin:0 0 8px;letter-spacing:-.04em}
p{color:#a1a1aa}
button{min-height:48px;width:100%;border:0;border-radius:12px;font-weight:800;margin:8px 0;font-size:16px}
.go{background:#00ff86;color:#042} .no{background:#3f1d1d;color:#fecaca}
</style></head>
<body>
<div class="card">
  <h1>Laptop camera</h1>
  <p id="st">PhoneAI is asking to see this PC’s webcam. Allow only if you requested it.</p>
  <button class="go" id="yes">Allow 10 minutes</button>
  <button class="no" id="no">Deny</button>
</div>
<script>
async function st(){ const j=await fetch('/v1/phoneai/home').then(r=>r.json()); const c=j.laptop_cam||{}; document.getElementById('st').textContent=c.pending?'Phone is waiting.':(c.approved?'Currently allowed.':'No pending request.'); }
st(); setInterval(st,1500);
function dec(allow){ fetch('/v1/phoneai/cam/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({allow:allow,minutes:10})}).then(()=>st()); }
document.getElementById('yes').onclick=()=>dec(true);
document.getElementById('no').onclick=()=>dec(false);
</script>
</body></html>
"""
