"""POCKET Creative Studio UI — friendly OpenAI-style chat + community feed."""

from __future__ import annotations


def creative_studio_html() -> str:
    return CREATIVE_HTML


CREATIVE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · Creative Studio</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#0b0b0f;--panel:#121218;--panel2:#18181f;--line:rgba(255,255,255,.08);
  --text:#f4f4f5;--muted:#a1a1aa;--accent:#10a37f;--accent2:#34d399;
  --violet:#a78bfa;--blue:#60a5fa;--pink:#f472b6;--amber:#fbbf24;
  --font:ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,Consolas,monospace;
  --radius:16px;--shadow:0 20px 50px rgba(0,0,0,.45);
  --ease:cubic-bezier(.22,1,.36,1);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{font-family:var(--font);background:
  radial-gradient(900px 500px at 10% -10%,rgba(16,163,127,.14),transparent 50%),
  radial-gradient(700px 400px at 100% 0%,rgba(167,139,250,.1),transparent 45%),
  var(--bg);color:var(--text);display:flex;flex-direction:column;min-height:100vh}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}

/* nav */
.pnav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 16px;border-bottom:1px solid var(--line);background:rgba(0,0,0,.55);backdrop-filter:blur(22px) saturate(1.3);position:sticky;top:0;z-index:40}
.pnav .brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:-.03em;font-size:14px;color:var(--text);text-decoration:none}
.pnav .brand i{width:26px;height:26px;border-radius:8px;background:linear-gradient(145deg,#10a37f,#0a7a5f);display:grid;place-items:center;font-size:12px;font-weight:800;color:#041;font-style:normal}
.pnav .links{display:flex;gap:2px;flex-wrap:wrap}
.pnav .links a{color:#8e8e8e;font-size:13px;font-weight:500;padding:7px 11px;border-radius:8px}
.pnav .links a:hover{color:#ececec;background:#111;text-decoration:none}
.pnav .links a.on{color:#f5f5f5;background:#1a1a1f}
.pnav .sp{flex:1}
.pill{font-size:11px;color:var(--muted);border:1px solid var(--line);padding:5px 10px;border-radius:999px}
.btn{border:0;border-radius:12px;padding:10px 14px;font-weight:700;font-size:13px;cursor:pointer;font-family:inherit}
.btn.primary{background:linear-gradient(180deg,#34d399,#10a37f);color:#042f1a}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text)}
.btn.soft{background:rgba(16,163,127,.12);border:1px solid rgba(16,163,127,.28);color:#86efac}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn.sm{padding:7px 10px;font-size:12px;border-radius:10px}

/* layout */
.shell{flex:1;display:grid;grid-template-columns:240px 1fr 320px;min-height:0;max-width:1500px;width:100%;margin:0 auto}
@media(max-width:1100px){.shell{grid-template-columns:1fr}.side,.community{display:none}.side.open,.community.open{display:flex;position:fixed;inset:52px 0 0 0;z-index:30;background:var(--bg)}}
.side,.community{display:flex;flex-direction:column;border-right:1px solid var(--line);background:rgba(0,0,0,.25);min-height:0}
.community{border-right:0;border-left:1px solid var(--line)}
.side h3,.community h3{margin:0;padding:14px 14px 8px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.side .scroll,.community .scroll{flex:1;overflow:auto;padding:0 10px 16px}
.mode{display:flex;align-items:flex-start;gap:10px;width:100%;text-align:left;padding:10px;border-radius:12px;border:1px solid transparent;background:transparent;color:inherit;cursor:pointer;margin-bottom:4px}
.mode:hover{background:rgba(255,255,255,.04)}
.mode.on{border-color:rgba(16,163,127,.35);background:rgba(16,163,127,.08)}
.mode .ic{font-size:16px;line-height:1.2}
.mode b{display:block;font-size:13px}
.mode small{display:block;font-size:11px;color:var(--muted);line-height:1.35;margin-top:2px}

/* chat */
.main{display:flex;flex-direction:column;min-height:0;min-width:0}
.hero{padding:18px 20px 8px}
.hero h1{margin:0;font-size:22px;letter-spacing:-.04em;font-weight:750}
.hero p{margin:6px 0 0;color:var(--muted);font-size:13px;line-height:1.5;max-width:52ch}
.chips{display:flex;flex-wrap:wrap;gap:6px;padding:8px 20px 0}
.chip{font-size:12px;padding:6px 10px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--muted);cursor:pointer}
.chip:hover,.chip.on{color:var(--text);border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
.messages{flex:1;overflow:auto;padding:12px 20px 20px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:820px;width:100%;margin:0 auto;display:flex;gap:12px;align-items:flex-start}
.msg .av{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:12px;font-weight:800;flex-shrink:0}
.msg.user .av{background:#27272a;color:#e4e4e7}
.msg.assistant .av{background:linear-gradient(145deg,#10a37f,#0a7a5f);color:#041}
.msg .bubble{flex:1;min-width:0}
.msg .bubble .who{font-size:11px;color:var(--muted);margin-bottom:4px;font-weight:650}
.msg .bubble .body{font-size:14.5px;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.msg .bubble .body code{font-family:var(--mono);font-size:12px;background:rgba(255,255,255,.06);padding:1px 5px;border-radius:5px}
.msg .actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.art{margin-top:10px;padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:rgba(255,255,255,.03);font-size:12px;color:var(--muted)}
.art b{color:var(--text)}
.art img{display:block;max-width:100%;max-height:360px;object-fit:contain;margin-top:8px;border-radius:10px;background:#050506}
.empty{flex:1;display:grid;place-items:center;padding:40px 20px;text-align:center;color:var(--muted)}
.empty .card{max-width:520px;padding:28px;border-radius:20px;border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.03),transparent),var(--panel);box-shadow:var(--shadow)}
.empty h2{margin:0 0 8px;color:var(--text);font-size:20px;letter-spacing:-.03em}
.empty p{margin:0 0 16px;font-size:13px;line-height:1.55}
.grid-modes{display:grid;grid-template-columns:1fr 1fr;gap:8px;text-align:left}
.grid-modes button{padding:12px;border-radius:12px;border:1px solid var(--line);background:rgba(0,0,0,.25);color:inherit;cursor:pointer}
.grid-modes button:hover{border-color:rgba(16,163,127,.4)}
.grid-modes b{display:block;font-size:13px}
.grid-modes small{font-size:11px;color:var(--muted)}

/* composer */
.composer-wrap{padding:10px 16px 18px;border-top:1px solid var(--line);background:linear-gradient(180deg,transparent,rgba(0,0,0,.35))}
.composer{max-width:820px;margin:0 auto;border:1px solid var(--line);border-radius:18px;background:var(--panel2);box-shadow:var(--shadow);padding:10px 12px;display:flex;flex-direction:column;gap:8px}
.composer textarea{width:100%;min-height:56px;max-height:180px;resize:vertical;border:0;outline:0;background:transparent;color:var(--text);font:inherit;font-size:14.5px;line-height:1.45;padding:4px 4px 0}
.composer .bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.composer .bar .mode-label{font-size:12px;color:var(--muted);padding:4px 8px;border-radius:999px;background:rgba(255,255,255,.04);border:1px solid var(--line)}
.composer .bar .sp{flex:1}
.hint{max-width:820px;margin:6px auto 0;font-size:11px;color:var(--muted);text-align:center}

/* community cards */
.share{border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:8px;background:rgba(255,255,255,.02)}
.share .top{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.share .av2{width:28px;height:28px;border-radius:999px;background:#27272a;display:grid;place-items:center;font-size:11px;font-weight:800}
.share .who{font-size:12px;font-weight:700}
.share .meta{font-size:10px;color:var(--muted)}
.share .title{font-size:13px;font-weight:700;margin:4px 0}
.share .body{font-size:12px;color:var(--muted);line-height:1.45;white-space:pre-wrap;max-height:120px;overflow:hidden}
.share .tag{display:inline-block;font-size:10px;padding:2px 7px;border-radius:999px;border:1px solid var(--line);margin:6px 4px 0 0;color:var(--muted)}
.notice{font-size:11px;color:var(--muted);padding:8px 12px;line-height:1.4;border-bottom:1px solid var(--line);background:rgba(167,139,250,.06)}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#18181b;border:1px solid var(--line);padding:10px 16px;border-radius:12px;display:none;z-index:99;font-size:13px;box-shadow:var(--shadow)}
.toast.show{display:block}
.toast.ok{border-color:rgba(16,163,127,.4)}
.toast.err{border-color:rgba(248,113,113,.45)}
.mob{display:none}
@media(max-width:1100px){.mob{display:inline-flex}}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/desk"><i>P</i>POCKET</a>
  <nav class="links">
    <a href="/desk">Desk</a>
    <a href="/studio">Product Studio</a>
    <a href="/imagine">Imagine</a>
    <a class="on" href="/studio/create">Creative</a>
    <a href="/studio/voice">Voice</a>
    <a href="/work">Work</a>
  </nav>
  <div class="sp"></div>
  <button class="btn ghost sm mob" type="button" onclick="toggleSide()">Modes</button>
  <button class="btn ghost sm mob" type="button" onclick="toggleCommunity()">Community</button>
  <span class="pill" id="authPill">…</span>
  <button class="btn soft sm" type="button" onclick="showCommunity(true)">Community feed</button>
</header>

<div class="shell">
  <aside class="side" id="side">
    <h3>Create modes</h3>
    <div class="scroll" id="modeList"></div>
    <div style="padding:10px;border-top:1px solid var(--line)">
      <button class="btn ghost" style="width:100%" type="button" onclick="newChat()">+ New chat</button>
    </div>
    <h3>Recent chats</h3>
    <div class="scroll" id="sessList" style="max-height:180px"></div>
  </aside>

  <section class="main">
    <div class="hero">
      <h1 id="heroTitle">Creative Studio</h1>
      <p id="heroBlurb">Chat like OpenAI — then switch modes for images, video packs, blogs, papers, and social. Share to Community only when you mean it.</p>
    </div>
    <div class="chips" id="quickChips"></div>
    <div class="messages" id="messages">
      <div class="empty" id="emptyState">
        <div class="card">
          <h2>What do you want to make?</h2>
          <p>Friendly multi-mode chat on your Pocket host. Community only shows what people share on purpose.</p>
          <div class="grid-modes" id="emptyModes"></div>
        </div>
      </div>
    </div>
    <div class="composer-wrap">
      <div class="composer">
        <textarea id="input" placeholder="Message Creative Studio…" rows="2"></textarea>
        <div class="bar">
          <span class="mode-label" id="modeLabel">💬 Chat</span>
          <button class="btn ghost sm" type="button" onclick="copyLast()" title="Copy last reply">Copy</button>
          <button class="btn ghost sm" type="button" onclick="shareLast()" title="Share last reply to community">Share</button>
          <div class="sp"></div>
          <button class="btn primary" id="sendBtn" type="button" onclick="send()">Generate</button>
        </div>
      </div>
      <div class="hint">Opt-in sharing only · Image uses Imagine · Video uses Product Studio · Blog/Paper/Social use host agents</div>
    </div>
  </section>

  <aside class="community" id="community">
    <div class="notice"><b style="color:var(--violet)">Community</b> — only intentional shares. Nothing from private chats is posted automatically.</div>
    <h3>What people shared</h3>
    <div style="padding:0 10px 8px;display:flex;gap:6px;flex-wrap:wrap">
      <button class="btn ghost sm" type="button" onclick="loadFeed()">Refresh</button>
      <select id="feedKind" class="btn ghost sm" style="appearance:auto" onchange="loadFeed()">
        <option value="">All kinds</option>
        <option value="blog">Blog</option>
        <option value="paper">Paper</option>
        <option value="social">Social</option>
        <option value="image">Image</option>
        <option value="video">Video</option>
        <option value="chat">Chat</option>
        <option value="export">Export</option>
      </select>
    </div>
    <div class="scroll" id="feedList"><div style="color:var(--muted);font-size:12px;padding:8px">Loading…</div></div>
  </aside>
</div>
<div class="toast" id="toast"></div>

<script>
const auth = {
  user: sessionStorage.getItem('pocket_user') || localStorage.getItem('pocket_user') || '',
  pass: sessionStorage.getItem('pocket_pass') || localStorage.getItem('pocket_pass') || '',
  token: sessionStorage.getItem('pocket_token') || localStorage.getItem('pocket_token') || '',
};
let modes = [];
let mode = 'chat';
let sessionId = localStorage.getItem('pocket_creative_session') || '';
let messages = [];
let lastShareHint = null;
let busy = false;

function toast(msg, kind){
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (kind||'');
  setTimeout(()=>t.classList.remove('show'), 2800);
}
function headers(){
  const h = {'Content-Type':'application/json'};
  if(auth.token) h['Authorization'] = 'Bearer ' + auth.token;
  else if(auth.user && auth.pass) h['Authorization'] = 'Basic ' + btoa(auth.user + ':' + auth.pass);
  return h;
}
async function api(path, opts){
  const o = opts || {};
  const r = await fetch(path, {
    method: o.method || 'GET',
    headers: headers(),
    body: o.body,
    credentials: 'same-origin',
  });
  const j = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(j.error || r.statusText || 'request failed');
  return j;
}

function toggleSide(){ document.getElementById('side').classList.toggle('open'); }
function toggleCommunity(){ document.getElementById('community').classList.toggle('open'); }
function showCommunity(on){
  const el = document.getElementById('community');
  if(on){ el.classList.add('open'); loadFeed(); location.hash = 'community'; }
}

function setMode(id){
  mode = id || 'chat';
  const m = modes.find(x=>x.id===mode) || {id:'chat',name:'Chat',icon:'💬',blurb:'',placeholder:'Message…'};
  document.getElementById('modeLabel').textContent = (m.icon||'') + ' ' + (m.name||mode);
  document.getElementById('input').placeholder = m.placeholder || 'Message Creative Studio…';
  document.getElementById('heroTitle').textContent = (m.icon?m.icon+' ':'') + (m.name||'Creative') + ' mode';
  document.getElementById('heroBlurb').textContent = m.blurb || 'Create with POCKET.';
  document.querySelectorAll('.mode').forEach(el=>el.classList.toggle('on', el.dataset.id===mode));
  document.querySelectorAll('.chip').forEach(el=>el.classList.toggle('on', el.dataset.id===mode));
}

function renderModes(){
  const list = document.getElementById('modeList');
  const empty = document.getElementById('emptyModes');
  const chips = document.getElementById('quickChips');
  list.innerHTML = '';
  empty.innerHTML = '';
  chips.innerHTML = '';
  modes.forEach(m=>{
    const b = document.createElement('button');
    b.type='button'; b.className='mode'+(m.id===mode?' on':''); b.dataset.id=m.id;
    b.innerHTML = `<span class="ic">${m.icon||'•'}</span><span><b>${esc(m.name)}</b><small>${esc(m.blurb||'')}</small></span>`;
    b.onclick = ()=>setMode(m.id);
    list.appendChild(b);

    const e = document.createElement('button');
    e.type='button';
    e.innerHTML = `<b>${m.icon||''} ${esc(m.name)}</b><small>${esc(m.blurb||'')}</small>`;
    e.onclick = ()=>{ setMode(m.id); document.getElementById('input').focus(); };
    empty.appendChild(e);

    const c = document.createElement('button');
    c.type='button'; c.className='chip'+(m.id===mode?' on':''); c.dataset.id=m.id;
    c.textContent = (m.icon?m.icon+' ':'') + m.name;
    c.onclick = ()=>setMode(m.id);
    chips.appendChild(c);
  });
}

function esc(s){
  return String(s||'').replace(/[&<>"']/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
}
function fmtBody(s){
  // light markdown: **bold**, `code`, keep newlines
  let t = esc(s);
  t = t.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>');
  t = t.replace(/`([^`]+)`/g,'<code>$1</code>');
  return t;
}

function renderMessages(){
  const box = document.getElementById('messages');
  const empty = document.getElementById('emptyState');
  if(!messages.length){
    box.innerHTML = '';
    box.appendChild(empty);
    empty.style.display = 'grid';
    return;
  }
  empty.style.display = 'none';
  box.innerHTML = '';
  messages.forEach(m=>{
    const row = document.createElement('div');
    row.className = 'msg ' + (m.role==='user'?'user':'assistant');
    const av = m.role==='user' ? 'You' : 'P';
    let arts = '';
    const imgUrl = m.media && m.media.image && m.media.image.file_url;
    if(imgUrl){
      arts += `<div class="art"><b>Imagine still</b><img src="${esc(imgUrl)}" alt="compose"/></div>`;
    } else if(m.media && m.media.image && m.media.image.error){
      arts += `<div class="art"><b>Imagine</b> · ${esc(m.media.image.error)}</div>`;
    }
    if(m.artifacts && m.artifacts.length){
      arts += m.artifacts.map(a=>`<div class="art"><b>${esc(a.kind)}</b> · ${esc(a.title||a.id)}</div>`).join('');
    }
    let actions = '';
    if(m.role==='assistant'){
      actions = `<div class="actions">
        <button class="btn ghost sm" type="button" data-act="copy">Copy</button>
        <button class="btn soft sm" type="button" data-act="share">Share to community</button>
      </div>`;
    }
    row.innerHTML = `<div class="av">${av}</div>
      <div class="bubble">
        <div class="who">${m.role==='user'?'You':'Creative Studio'}${m.mode?' · '+esc(m.mode):''}</div>
        <div class="body">${fmtBody(m.content||'')}</div>
        ${arts}${actions}
      </div>`;
    if(m.role==='assistant'){
      row.querySelector('[data-act="copy"]').onclick = ()=>{ navigator.clipboard.writeText(m.content||''); toast('Copied','ok'); };
      row.querySelector('[data-act="share"]').onclick = ()=>shareMessage(m);
    }
    box.appendChild(row);
  });
  box.scrollTop = box.scrollHeight;
}

async function loadCatalog(){
  try{
    const j = await api('/v1/creative');
    modes = j.modes || [];
  }catch(_){
    modes = [
      {id:'chat',name:'Chat',icon:'💬',blurb:'Friendly conversation',placeholder:'Ask anything…'},
      {id:'image',name:'Image',icon:'🖼',blurb:'Product stills',placeholder:'Describe an image…'},
      {id:'video',name:'Video',icon:'🎬',blurb:'Viral video packs',placeholder:'Viral pack from latest…'},
      {id:'blog',name:'Blog',icon:'✍',blurb:'Long-form posts',placeholder:'Blog topic…'},
      {id:'paper',name:'Paper',icon:'📄',blurb:'Research writeups',placeholder:'Research question…'},
      {id:'social',name:'Social',icon:'📣',blurb:'Posts & threads',placeholder:'What to post…'},
    ];
  }
  renderModes();
  setMode(mode);
}

async function loadSessions(){
  try{
    const j = await api('/v1/creative/sessions');
    const box = document.getElementById('sessList');
    box.innerHTML = '';
    (j.sessions||[]).forEach(s=>{
      const b = document.createElement('button');
      b.type='button'; b.className='mode';
      b.innerHTML = `<span class="ic">◌</span><span><b>${esc(s.title||s.id)}</b><small>${s.messages||0} msgs</small></span>`;
      b.onclick = ()=>openSession(s.id);
      box.appendChild(b);
    });
  }catch(_){}
}

async function openSession(id){
  try{
    const j = await api('/v1/creative/session/' + encodeURIComponent(id));
    const s = j.session || {};
    sessionId = s.id || id;
    localStorage.setItem('pocket_creative_session', sessionId);
    messages = s.messages || [];
    renderMessages();
    toast('Session loaded','ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}

function newChat(){
  sessionId = '';
  localStorage.removeItem('pocket_creative_session');
  messages = [];
  lastShareHint = null;
  renderMessages();
  document.getElementById('input').focus();
}

async function send(){
  if(busy) return;
  const el = document.getElementById('input');
  const text = (el.value||'').trim();
  if(!text) return;
  busy = true;
  document.getElementById('sendBtn').disabled = true;
  messages.push({role:'user', content:text, mode, at:Date.now()/1000});
  renderMessages();
  el.value = '';
  // optimistic typing bubble
  messages.push({role:'assistant', content:'Creating…', mode, at:Date.now()/1000, _tmp:true});
  renderMessages();
  try{
    const j = await api('/v1/creative/chat', {
      method:'POST',
      body: JSON.stringify({ message:text, mode, session_id: sessionId||undefined }),
    });
    sessionId = j.session_id || sessionId;
    if(sessionId) localStorage.setItem('pocket_creative_session', sessionId);
    lastShareHint = j.share_hint || { title:text.slice(0,80), kind:mode, body:j.reply||'' };
    // replace tmp
    messages = messages.filter(m=>!m._tmp);
    if(j.message){
      if(j.media && !j.message.media) j.message.media = {
        image: j.media.image ? {
          ok: j.media.image.ok,
          file_url: (j.media.image.result||{}).file_url,
          error: j.media.image.error || (j.media.image.result||{}).error
        } : undefined
      };
      messages.push(j.message);
    }
    else messages.push({role:'assistant', content:j.reply||'(no reply)', mode});
    renderMessages();
    loadSessions();
  }catch(e){
    messages = messages.filter(m=>!m._tmp);
    messages.push({role:'assistant', content:'Error: '+(e.message||e), mode});
    renderMessages();
    toast(String(e.message||e),'err');
  }finally{
    busy = false;
    document.getElementById('sendBtn').disabled = false;
  }
}

function copyLast(){
  const last = [...messages].reverse().find(m=>m.role==='assistant' && !m._tmp);
  if(!last){ toast('Nothing to copy'); return; }
  navigator.clipboard.writeText(last.content||'');
  toast('Copied','ok');
}

async function shareMessage(m){
  const body = (m && m.content) || '';
  if(!body || body==='Creating…'){ toast('Nothing to share'); return; }
  const title = (lastShareHint && lastShareHint.title) || body.slice(0,60);
  const kind = (m && m.mode) || mode || 'chat';
  try{
    const j = await api('/v1/community/share', {
      method:'POST',
      body: JSON.stringify({
        title,
        body,
        kind,
        author: auth.user || 'pocket',
        display_name: auth.user || 'Pocket user',
        tags: [kind, 'creative-studio'],
        source: 'creative_studio',
        intentional: true,
      }),
    });
    toast(j.message || 'Shared to community','ok');
    loadFeed();
  }catch(e){ toast(String(e.message||e),'err'); }
}
function shareLast(){
  const last = [...messages].reverse().find(m=>m.role==='assistant' && !m._tmp);
  shareMessage(last || { content: lastShareHint && lastShareHint.body, mode });
}

async function loadFeed(){
  const kind = document.getElementById('feedKind').value || '';
  const box = document.getElementById('feedList');
  try{
    const q = kind ? ('?kind='+encodeURIComponent(kind)+'&limit=40') : '?limit=40';
    const j = await api('/v1/community'+q);
    const shares = j.shares || [];
    if(!shares.length){
      box.innerHTML = '<div style="color:var(--muted);font-size:12px;padding:10px;line-height:1.45">No public shares yet. Create something in chat, then hit <b style="color:var(--text)">Share to community</b> — only intentional posts appear here.</div>';
      return;
    }
    box.innerHTML = '';
    shares.forEach(s=>{
      const d = document.createElement('div');
      d.className = 'share';
      const when = s.at ? new Date(s.at*1000).toLocaleString() : '';
      const tags = (s.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('');
      d.innerHTML = `<div class="top">
          <div class="av2">${esc((s.display_name||s.author||'?').slice(0,2).toUpperCase())}</div>
          <div><div class="who">${esc(s.display_name||s.author||'user')}</div>
          <div class="meta">${esc(s.kind||'note')} · ${esc(when)}</div></div>
        </div>
        <div class="title">${esc(s.title||'')}</div>
        <div class="body">${esc(s.preview||s.body||'')}</div>
        ${tags}`;
      box.appendChild(d);
    });
  }catch(e){
    box.innerHTML = '<div style="color:#fca5a5;font-size:12px;padding:8px">'+esc(e.message||e)+'</div>';
  }
}

document.getElementById('input').addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); }
});

(async function boot(){
  document.getElementById('authPill').textContent = auth.user ? ('@'+auth.user) : 'local';
  await loadCatalog();
  await loadSessions();
  if(sessionId){
    try{ await openSession(sessionId); }catch(_){ sessionId=''; }
  }else{
    renderMessages();
  }
  await loadFeed();
  if(location.hash==='#community') showCommunity(true);
})();
</script>
</body>
</html>
"""
