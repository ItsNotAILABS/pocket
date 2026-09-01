"""Desk + phone UI for named agents, faces, DMs, group chats, and mail."""

from __future__ import annotations


def agents_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Agents</title>
<meta name="theme-color" content="#09090b"/>
<style>
:root{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--fg:#fafafa;--muted:#a1a1aa;--accent:#10a37f}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0% 0%,rgba(16,163,127,.08),transparent 50%),var(--bg);color:#e4e4e7}
header{display:flex;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(9,9,11,.8);backdrop-filter:blur(18px);z-index:4}
header h1{margin:0;font-size:15px;color:var(--fg)}
header nav{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
header nav a{font-size:12px;font-weight:600;color:var(--muted);border:1px solid var(--line);padding:6px 10px;border-radius:8px;text-decoration:none}
.wrap{max-width:1100px;margin:0 auto;padding:18px 14px 80px;display:grid;grid-template-columns:280px 1fr;gap:14px}
@media(max-width:860px){.wrap{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:14px}
.person{display:flex;gap:10px;align-items:center;width:100%;text-align:left;border:1px solid var(--line);background:#1c1c1f;color:inherit;padding:8px;border-radius:12px;margin:0 0 6px;cursor:pointer}
.person.on{border-color:rgba(16,163,127,.5)}
.person img,.face{width:36px;height:36px;border-radius:12px}
.person b{display:block;color:var(--fg);font-size:13px}
.person span{color:var(--muted);font-size:11px}
.log{max-height:360px;overflow:auto;display:flex;flex-direction:column;gap:8px}
.bubble{align-self:flex-start;background:#1c1c1f;border:1px solid var(--line);padding:8px 10px;border-radius:12px;max-width:80%;font-size:13px}
.bubble.me{align-self:flex-end;background:rgba(16,163,127,.18)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
input,textarea,select{width:100%;background:#09090b;border:1px solid var(--line);border-radius:10px;padding:10px;color:var(--fg)}
button{border:1px solid var(--line);background:#1c1c1f;color:var(--fg);padding:8px 12px;border-radius:9px;font-weight:650;cursor:pointer}
button.primary{background:var(--accent);border:0;color:#042}
.pill{font-size:11px;border:1px solid var(--line);padding:3px 8px;border-radius:999px;color:var(--muted)}
h2{margin:0 0 8px;font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--fg)}
</style>
</head>
<body>
<header>
  <h1>Agents <span class="pill">names · faces · DMs · mail · groups</span></h1>
  <nav>
    <a href="/desk">Desk</a>
    <a href="/mail">Mail</a>
    <a href="/phoneai/app">PhoneAI</a>
    <a href="/docs">Docs</a>
  </nav>
</header>
<div class="wrap">
  <aside class="card">
    <h2>People</h2>
    <p id="meta" style="color:var(--muted);font-size:12px">Loading…</p>
    <div id="people"></div>
  </aside>
  <main>
    <div class="card" style="margin-bottom:12px">
      <h2 id="who">Select an agent</h2>
      <div class="log" id="log"></div>
      <div class="row">
        <input id="msg" placeholder="DM this agent…"/>
        <button class="primary" id="sendDm">DM</button>
        <button id="sendMail">Email</button>
      </div>
    </div>
    <div class="card">
      <h2>Group chats</h2>
      <div id="groups"></div>
      <div class="row">
        <input id="gname" placeholder="New group name"/>
        <button id="mkGroup">Create group</button>
      </div>
      <div class="row">
        <select id="gpick"></select>
        <input id="gmsg" placeholder="Post to group"/>
        <button class="primary" id="gpost">Post</button>
      </div>
      <div class="log" id="glog"></div>
    </div>
  </main>
</div>
<script>
let me='system', them='', people=[];
function face(a){ return a.face || ('/v1/agents/face/'+(a.id||'agent')+'.svg'); }
async function j(url, opt){ const r=await fetch(url, opt); return r.json(); }
async function load(){
  const s=await j('/v1/agents/social');
  document.getElementById('meta').textContent=(s.agents||0)+' named · '+(s.groups||0)+' groups · '+(s.dm_threads||0)+' DMs';
  const p=await j('/v1/agents/people');
  people=p.agents||[];
  document.getElementById('people').innerHTML=people.map(a=>
    '<button class="person" data-id="'+a.id+'"><img class="face" src="'+face(a)+'" alt=""/><div><b>'+(a.name||a.id)+'</b><span>'+a.address+'</span></div></button>'
  ).join('');
  const g=await j('/v1/agents/groups');
  const gs=g.groups||[];
  document.getElementById('groups').innerHTML=gs.map(x=>'<div class="pill">'+x.name+' · '+(x.members||[]).length+' members</div>').join(' ') || '<span class="pill">no groups yet</span>';
  document.getElementById('gpick').innerHTML=gs.map(x=>'<option value="'+x.id+'">'+x.name+'</option>').join('');
}
document.getElementById('people').onclick=async e=>{
  const b=e.target.closest('[data-id]'); if(!b) return;
  them=b.getAttribute('data-id');
  [...document.querySelectorAll('.person')].forEach(x=>x.classList.toggle('on', x===b));
  const a=people.find(x=>x.id===them)||{id:them};
  document.getElementById('who').textContent=(a.name||them)+' · '+a.address;
  const t=await j('/v1/agents/dm?a='+encodeURIComponent(me)+'&b='+encodeURIComponent(them));
  paint(document.getElementById('log'), t.messages||[], them);
};
function paint(el, msgs, other){
  el.innerHTML=(msgs||[]).map(m=>{
    const mine=m.from===me;
    return '<div class="bubble '+(mine?'me':'')+'"><b>'+m.from+'</b><div>'+(m.text||m.body||'')+'</div></div>';
  }).join('') || '<div class="bubble">No messages yet</div>';
  el.scrollTop=el.scrollHeight;
}
document.getElementById('sendDm').onclick=async()=>{
  const text=document.getElementById('msg').value.trim(); if(!them||!text) return;
  await j('/v1/agents/dm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from:me,to:them,text})});
  document.getElementById('msg').value='';
  const t=await j('/v1/agents/dm?a='+me+'&b='+them); paint(document.getElementById('log'), t.messages||[]);
};
document.getElementById('sendMail').onclick=async()=>{
  const text=document.getElementById('msg').value.trim(); if(!them||!text) return;
  await j('/v1/agents/email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from:me,to:them,subject:'From '+me,body:text})});
  document.getElementById('msg').value='';
  alert('Mailed '+them+'@agents.pocket.local');
};
document.getElementById('mkGroup').onclick=async()=>{
  const name=document.getElementById('gname').value.trim(); if(!name) return;
  await j('/v1/agents/groups',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name, members: people.slice(0,8).map(a=>a.id), owner:me})});
  document.getElementById('gname').value=''; load();
};
document.getElementById('gpost').onclick=async()=>{
  const gid=document.getElementById('gpick').value; const text=document.getElementById('gmsg').value.trim();
  if(!gid||!text) return;
  await j('/v1/agents/groups/post',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({group:gid,from:me,text})});
  document.getElementById('gmsg').value='';
  const m=await j('/v1/agents/groups/messages?id='+encodeURIComponent(gid));
  paint(document.getElementById('glog'), m.messages||[]);
};
load();
</script>
</body></html>
"""
