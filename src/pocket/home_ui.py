"""TV, doorbell, and laptop-camera approval pages for PhoneAI."""

from __future__ import annotations


def tv_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PhoneAI TV</title>
<meta name="theme-color" content="#000"/>
<style>
html,body{margin:0;height:100%;background:#000;color:#f4f4f5;font-family:ui-sans-serif,system-ui;overflow:hidden}
body{display:flex;flex-direction:column}
.top{display:flex;gap:16px;align-items:center;padding:10px 18px;font-size:18px}
.top a{color:#8b8b98;text-decoration:none}
.stage{flex:1;position:relative;background:#000;min-height:0}
img{width:100%;height:100%;object-fit:contain;touch-action:none}
.bar{display:flex;gap:12px;padding:12px 16px;background:#0a0a10}
.bar button{min-height:56px;min-width:120px;border:0;border-radius:14px;background:#14141c;color:#fff;font-size:20px;font-weight:800}
.bar button.go{background:#00ff86;color:#042}
</style></head>
<body>
<div class="top"><b>PhoneAI TV</b><span id="h">Same Wi-Fi · watch + touch the PC</span><a href="/phoneai/portal">Phone Portal</a></div>
<div class="stage" id="stage"><img id="f" alt="PC" src="/v1/phoneai/portal/frame?max_w=1280&t=1" draggable="false"/></div>
<div class="bar">
  <button type="button" class="go" id="l">Click</button>
  <button type="button" id="r">Right</button>
  <button type="button" id="u">Scroll ▲</button>
  <button type="button" id="d">Scroll ▼</button>
  <button type="button" id="m">Max window</button>
</div>
<script>
let nx=0.5, ny=0.5, busy=false;
const img=document.getElementById('f'), stage=document.getElementById('stage');
function pt(ev){
  const t=(ev.touches&&ev.touches[0])||(ev.changedTouches&&ev.changedTouches[0])||ev;
  const r=img.getBoundingClientRect();
  nx=Math.max(0,Math.min(1,(t.clientX-r.left)/Math.max(1,r.width)));
  ny=Math.max(0,Math.min(1,(t.clientY-r.top)/Math.max(1,r.height)));
}
function send(kind, extra){
  fetch('/v1/phoneai/portal/touch',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({kind,nx,ny,target:'desktop'}, extra||{}))})
    .then(r=>r.json()).then(j=>{ document.getElementById('h').textContent=(j.focus&&j.focus.title)||j.kind||'TV'; }).catch(()=>{});
}
function tick(){
  if(document.hidden||busy){ setTimeout(tick,500); return; }
  busy=true; img.onload=()=>{busy=false;setTimeout(tick,400)}; img.onerror=()=>{busy=false;setTimeout(tick,900)};
  img.src='/v1/phoneai/portal/frame?max_w=1280&t='+Date.now();
}
tick();
stage.addEventListener('touchstart', ev=>{ ev.preventDefault(); pt(ev); send('tap'); }, {passive:false});
stage.addEventListener('click', ev=>{ pt(ev); send('tap'); });
let lastY=null;
stage.addEventListener('touchmove', ev=>{
  ev.preventDefault(); const t=ev.touches[0]; pt(ev);
  if(lastY!=null) send('scroll',{dy:(t.clientY-lastY)/70});
  lastY=t.clientY;
}, {passive:false});
stage.addEventListener('touchend', ()=>{ lastY=null; });
document.getElementById('l').onclick=()=>send('tap');
document.getElementById('r').onclick=()=>send('right');
document.getElementById('u').onclick=()=>send('scroll',{dy:-0.5});
document.getElementById('d').onclick=()=>send('scroll',{dy:0.5});
document.getElementById('m').onclick=()=>send('maximize');
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
