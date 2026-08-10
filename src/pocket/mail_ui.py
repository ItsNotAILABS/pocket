"""POCKET Mail UI — agent accounts + inboxes (our own domain)."""

from __future__ import annotations


def mail_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Agent Mail</title>
<meta name="theme-color" content="#09090b"/>
<style>
:root{--bg:#09090b;--panel:#141416;--panel2:#1c1c1f;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f;--warn:#f59e0b}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.5}
a{color:var(--accent);text-decoration:none}
header{display:flex;align-items:center;gap:12px;padding:14px 18px;border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(9,9,11,.92);backdrop-filter:blur(10px);z-index:5}
header .mark{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#10a37f,#0b6e4f);display:grid;place-items:center;font-weight:800;color:#fff;font-size:13px}
header h1{margin:0;font-size:15px;color:var(--fg);letter-spacing:-.02em}
header nav{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
header nav a{font-size:12px;font-weight:600;color:var(--muted);border:1px solid var(--line);padding:6px 10px;border-radius:8px}
header nav a:hover{color:var(--fg)}
.wrap{max-width:1100px;margin:0 auto;padding:20px 16px 80px;display:grid;grid-template-columns:240px 1fr;gap:16px}
@media(max-width:800px){.wrap{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:14px}
.card h2{margin:0 0 10px;font-size:13px;color:var(--fg);letter-spacing:.02em;text-transform:uppercase}
.sub{font-size:12px;color:var(--muted);margin:0 0 10px}
.acct{display:block;width:100%;text-align:left;border:1px solid var(--line);background:var(--panel2);color:var(--text);padding:10px;border-radius:10px;margin-bottom:6px;cursor:pointer;font-size:12.5px}
.acct.on{border-color:rgba(16,163,127,.5);background:rgba(16,163,127,.08)}
.acct b{display:block;color:var(--fg);font-size:12.5px}
.acct span{color:var(--muted);font-size:11px}
.badge{float:right;background:var(--accent);color:#042;font-size:10px;font-weight:700;padding:2px 7px;border-radius:999px}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
input,textarea,select{width:100%;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px 12px;color:var(--fg);font-size:13px}
label{display:block;font-size:11px;font-weight:650;color:var(--muted);margin:8px 0 4px;text-transform:uppercase;letter-spacing:.04em}
button{border:1px solid var(--line);background:var(--panel2);color:var(--fg);padding:8px 12px;border-radius:9px;font-size:12.5px;font-weight:650;cursor:pointer}
button.primary{background:var(--accent);border-color:transparent;color:#042}
button:hover{filter:brightness(1.08)}
.msg{border-top:1px solid var(--line);padding:10px 0;cursor:pointer}
.msg:first-child{border-top:0}
.msg .s{font-weight:650;color:var(--fg)}
.msg .m{font-size:12px;color:var(--muted)}
.msg.unread .s::before{content:"● ";color:var(--accent)}
pre{white-space:pre-wrap;font-size:12.5px;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px;max-height:280px;overflow:auto}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:var(--panel2);border:1px solid var(--line);padding:10px 14px;border-radius:12px;font-size:13px;opacity:0;transition:.2s;z-index:20}
.toast.show{opacity:1}
.pill{display:inline-block;font-size:11px;border:1px solid var(--line);padding:3px 8px;border-radius:999px;color:var(--muted)}
</style>
</head>
<body>
<header>
  <div class="mark">P</div>
  <h1>Agent Mail <span class="pill">agents.pocket.local</span></h1>
  <nav>
    <a href="/desk">Desk</a>
    <a href="/docs">Docs</a>
    <a href="/install">Install</a>
    <a href="/developers">API</a>
  </nav>
</header>
<div class="wrap">
  <aside class="card">
    <h2>Accounts</h2>
    <p class="sub" id="statusLine">Loading…</p>
    <div id="accounts"></div>
    <div class="row" style="margin-top:12px">
      <button type="button" class="primary" onclick="createAcct()">+ Create</button>
      <button type="button" onclick="refresh()">↻</button>
    </div>
  </aside>
  <main>
    <div class="card" style="margin-bottom:12px">
      <h2>Inbox · <span id="curAddr">—</span></h2>
      <p class="sub">Agent↔agent mail is local. External SMTP via POCKET MAIL when configured.</p>
      <div id="inbox"><div class="sub">Select an account</div></div>
      <pre id="body" style="display:none;margin-top:10px"></pre>
    </div>
    <div class="card">
      <h2>Compose</h2>
      <label>From agent</label>
      <input id="from" value="scribe" placeholder="scribe"/>
      <label>To (agent id or address)</label>
      <input id="to" value="assist" placeholder="assist"/>
      <label>Subject</label>
      <input id="subject" value="" placeholder="Subject"/>
      <label>Body</label>
      <textarea id="bodyIn" rows="4" placeholder="Message…"></textarea>
      <div class="row">
        <button type="button" class="primary" onclick="sendMail()">Send</button>
        <button type="button" onclick="document.getElementById('bodyIn').value=''">Clear</button>
      </div>
    </div>
  </main>
</div>
<div class="toast" id="toast"></div>
<script>
let token = sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'';
let cur = 'assist';
function $(id){return document.getElementById(id)}
function toast(m){const t=$('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
async function api(path, opts={}){
  const headers=Object.assign({'Content-Type':'application/json'}, opts.headers||{});
  if(token) headers['Authorization']='Bearer '+token;
  const r=await fetch(path,{...opts,headers});
  const j=await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(j.error||('HTTP '+r.status));
  return j;
}
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){
  try{
    const st=await api('/v1/agent-mail');
    $('statusLine').textContent=(st.accounts||0)+' accounts · '+(st.total_unread||0)+' unread · '+ (st.domain||'');
    const acc=await api('/v1/agent-mail/accounts');
    const box=$('accounts');
    box.innerHTML=(acc.accounts||[]).map(a=>`
      <button type="button" class="acct ${a.id===cur?'on':''}" data-id="${esc(a.id)}">
        ${a.unread?`<span class="badge">${a.unread}</span>`:''}
        <b>${esc(a.name||a.id)}</b>
        <span>${esc(a.address)}</span>
      </button>`).join('')||'<div class="sub">No accounts</div>';
    box.querySelectorAll('.acct').forEach(b=>b.onclick=()=>{cur=b.getAttribute('data-id'); loadInbox(); refresh();});
    loadInbox();
  }catch(e){ $('statusLine').textContent=e.message; }
}
async function loadInbox(){
  $('curAddr').textContent=cur+'@agents.pocket.local';
  $('from').value=cur==='assist'?'scribe':cur;
  try{
    const j=await api('/v1/agent-mail/inbox?agent='+encodeURIComponent(cur));
    const items=j.items||[];
    if(!items.length){ $('inbox').innerHTML='<div class="sub">Empty inbox</div>'; $('body').style.display='none'; return; }
    $('inbox').innerHTML=items.map(m=>`
      <div class="msg ${m.read?'':'unread'}" data-id="${esc(m.id)}">
        <div class="s">${esc(m.subject||'(no subject)')}</div>
        <div class="m">from ${esc(m.from)} · ${esc((m.preview||'').slice(0,100))}</div>
      </div>`).join('');
    $('inbox').querySelectorAll('.msg').forEach(el=>el.onclick=()=>openMsg(el.getAttribute('data-id')));
  }catch(e){ $('inbox').innerHTML='<div class="sub">'+esc(e.message)+'</div>'; }
}
async function openMsg(id){
  try{
    const j=await api('/v1/agent-mail/read',{method:'POST',body:JSON.stringify({agent:cur,id})});
    const m=j.mail||{};
    $('body').style.display='block';
    $('body').textContent='From: '+(m.from||'')+'\\nTo: '+(m.to||'')+'\\nSubject: '+(m.subject||'')+'\\n\\n'+(m.body||'');
    loadInbox();
  }catch(e){ toast(e.message); }
}
async function sendMail(){
  try{
    const j=await api('/v1/agent-mail/send',{method:'POST',body:JSON.stringify({
      from:$('from').value||'scribe',
      to:$('to').value||'assist',
      subject:$('subject').value||'(no subject)',
      body:$('bodyIn').value||''
    })});
    toast(j.message|| (j.ok?'Sent':'Failed'));
    if(j.ok){ $('bodyIn').value=''; $('subject').value=''; refresh(); }
  }catch(e){ toast(e.message); }
}
async function createAcct(){
  const id=prompt('New agent id (e.g. research):','');
  if(!id||!id.trim()) return;
  try{
    const j=await api('/v1/agent-mail/accounts',{method:'POST',body:JSON.stringify({agent:id.trim(),name:id.trim()})});
    toast(j.message||'Created');
    cur=id.trim().toLowerCase();
    refresh();
  }catch(e){ toast(e.message); }
}
refresh();
</script>
</body>
</html>
"""
