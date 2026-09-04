"""Crew board HTML — side-by-side seats per repo lane."""


def crew_html() -> str:
    return HTML


HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Crew · POCKET</title>
<style>
:root{--bg:#07070b;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#10a37f;--p:#14141c}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{padding:16px 16px 48px;max-width:1200px;margin:0 auto}
a{color:var(--muted);text-decoration:none}
h1{font-size:22px;letter-spacing:-.04em;margin:8px 0 4px}
.lead{color:var(--muted);font-size:14px;margin:0 0 16px;max-width:40em}
.spawn{display:flex;flex-wrap:wrap;gap:8px;padding:12px;border:1px solid var(--line);border-radius:14px;background:var(--p);margin-bottom:18px}
.spawn select,.spawn input{background:#0c0c0e;color:#fff;border:1px solid var(--line);border-radius:10px;padding:8px 10px;min-width:140px}
.spawn button{border:0;border-radius:10px;background:var(--g);color:#042;font-weight:800;padding:8px 14px}
.lane{border:1px solid var(--line);border-radius:16px;margin:0 0 16px;background:#0c0c10;overflow:hidden}
.lane h2{margin:0;padding:12px 14px;font-size:14px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center}
.lane h2 span{color:var(--muted);font-weight:500;font-size:12px}
.seats{display:grid;grid-template-columns:1fr;min-height:280px}
@media(min-width:800px){.seats.two{grid-template-columns:1fr 1fr}}
.seat{padding:12px;border-right:1px solid var(--line);display:flex;flex-direction:column;min-width:0}
.seat:last-child{border-right:0}
.seat .who{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--g);margin-bottom:6px}
.seat .part{font-size:13px;color:var(--muted);margin-bottom:8px}
.log{flex:1;overflow:auto;font-size:13px;line-height:1.45;white-space:pre-wrap;background:#08080c;border-radius:10px;padding:10px;min-height:140px;max-height:280px}
.steer{display:flex;gap:6px;margin-top:8px}
.steer textarea{flex:1;min-height:44px;border-radius:10px;border:1px solid var(--line);background:#0c0c0e;color:#fff;padding:8px;font:inherit}
.steer button{border:0;border-radius:10px;background:#222;color:#fff;font-weight:700;padding:0 12px}
.x{margin-left:auto;border:0;background:transparent;color:var(--muted);cursor:pointer}
.run{color:#fbbf24}
</style></head>
<body>
<p><a href="/phoneai/app">Kernel</a> · <a href="/phoneai/work">Code desk</a> · <a href="/desk">Desk</a></p>
<h1>Crew</h1>
<p class="lead">One lane per repo. Spawn 1–2 agents side by side on different parts. You steer each seat. They share notes — they do not share a window pile.</p>
<form class="spawn" id="sp">
  <select id="repo"></select>
  <select id="c1"><option value="grok">Grok</option><option value="codex">Codex</option><option value="spark">Spark</option><option value="meta">Meta</option><option value="gemini">Gemini</option></select>
  <input id="p1" placeholder="Part A (e.g. portal)"/>
  <select id="c2"><option value="">(one seat)</option><option value="codex">Codex</option><option value="spark">Spark</option><option value="grok">Grok</option><option value="gemini">Gemini</option><option value="meta">Meta</option></select>
  <input id="p2" placeholder="Part B (e.g. auth)"/>
  <input id="goal" placeholder="Lane goal (optional)" style="flex:1;min-width:180px"/>
  <button>Spawn</button>
</form>
<div id="board"></div>
<script>
const $=id=>document.getElementById(id);
function esc(s){return String(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
async function api(path, body){
  const opt=body?{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{credentials:'include'};
  return (await fetch(path,opt)).json();
}
function paint(j){
  const rs=j.repos||[];
  if(!$('repo').dataset.ready){
    $('repo').innerHTML=rs.map(r=>'<option value="'+esc(r.full||r.id||r.name)+'">'+esc(r.full||r.name)+(r.local?' · disk':'')+'</option>').join('')||'<option>no repos</option>';
    $('repo').dataset.ready='1';
  }
  const wired=new Set(j.wired||[]);
  [...$('c1').options].forEach(o=>{ if(o.value) o.textContent=o.value+(wired.has(o.value)?'':' · off'); });
  const lanes=j.lanes||[];
  $('board').innerHTML=lanes.map(ln=>{
    const seats=ln.seats||[];
    const cols=seats.map(st=>{
      const log=(st.log||[]).map(m=> (m.role||'?')+': '+(m.text||'')).join('\n\n')||'(idle — steer this seat)';
      return '<div class="seat" data-seat="'+st.id+'"><div class="who">'+(st.status==='running'?'<span class="run">● </span>':'')+esc(st.cli)+' <button class="x" data-close="'+st.id+'">close</button></div><div class="part">'+esc(st.part)+'</div><div class="log">'+esc(log)+'</div><form class="steer"><textarea placeholder="Steer this seat…"></textarea><button>Go</button></form></div>';
    }).join('');
    return '<div class="lane"><h2>'+esc(ln.repo)+' <span>'+esc(ln.goal||ln.cwd||'')+'</span></h2><div class="seats'+(seats.length>1?' two':'')+'">'+cols+'</div></div>';
  }).join('') || '<p class="lead">No lanes yet. Pick a repo, name the parts, spawn.</p>';
}
async function refresh(){ paint(await api('/v1/crew')); }
$('sp').onsubmit=async ev=>{
  ev.preventDefault();
  const clis=[$('c1').value]; if($('c2').value) clis.push($('c2').value);
  const parts=[$('p1').value||'part A']; if($('c2').value) parts.push($('p2').value||'part B');
  const j=await api('/v1/crew/spawn',{repo:$('repo').value,clis,parts,goal:$('goal').value});
  if(!j.ok) alert(j.error||'spawn failed');
  refresh();
};
$('board').addEventListener('submit', async ev=>{
  const f=ev.target.closest('.steer'); if(!f) return;
  ev.preventDefault();
  const seat=f.closest('[data-seat]').getAttribute('data-seat');
  const text=f.querySelector('textarea').value.trim(); if(!text) return;
  f.querySelector('textarea').value='';
  const j=await api('/v1/crew/steer',{seat_id:seat,text});
  if(!j.ok) alert(j.error||'steer failed');
  refresh();
});
$('board').addEventListener('click', async ev=>{
  const b=ev.target.closest('[data-close]'); if(!b) return;
  await api('/v1/crew/close',{seat_id:b.getAttribute('data-close')});
  refresh();
});
refresh(); setInterval(refresh, 4000);
</script>
</body></html>
"""
