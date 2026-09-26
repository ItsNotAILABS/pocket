"""POCKET LIGHT page. Pocket colors. Antigravity-shaped regions."""

from __future__ import annotations


def pocket_light_html() -> str:
    return HTML


HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET LIGHT</title>
<style>
:root{--bg:#06060a;--bg2:#0b0b10;--panel:#111118;--panel2:#181822;--line:rgba(255,255,255,.08);--text:#e8e8ed;--muted:#8b8b98;--accent:#10a37f;--accent-ink:#042f24}
*{box-sizing:border-box}
html,body{height:100%;margin:0;background:var(--bg);color:var(--text);font-family:ui-sans-serif,system-ui,sans-serif}
body{display:grid;grid-template-rows:48px 1fr 132px;height:100%}
a{color:var(--accent);text-decoration:none}
button,select,textarea{font:inherit;color:inherit}
.top{display:flex;align-items:center;gap:14px;padding:0 14px;border-bottom:1px solid var(--line);background:var(--bg2)}
.top b{letter-spacing:-.03em}
.top span{color:var(--muted);font-size:12px}
.mid{display:grid;grid-template-columns:240px 1fr 260px;min-height:0}
.side,.rail{background:var(--panel);overflow:auto;padding:10px}
.side{border-right:1px solid var(--line)}
.rail{border-left:1px solid var(--line)}
h3{margin:12px 8px 6px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}
.thread{display:block;width:100%;text-align:left;background:transparent;border:0;border-radius:8px;padding:8px;margin:0 0 4px;cursor:pointer}
.thread.on{background:var(--panel2);outline:1px solid var(--line)}
.thread b{display:block;font-size:13px}
.thread i{display:block;font-style:normal;color:var(--muted);font-size:11px}
.center{display:flex;flex-direction:column;min-width:0;min-height:0}
.log{flex:1;overflow:auto;padding:14px 16px}
.m{margin:0 0 10px;padding:10px 12px;border-radius:12px;background:var(--panel);white-space:pre-wrap;line-height:1.45;font-size:14px}
.m.you{background:#14352c}
.m .who{display:block;color:var(--muted);font-size:11px;margin-bottom:4px}
.form{display:flex;gap:8px;padding:10px 12px;border-top:1px solid var(--line)}
textarea{flex:1;min-height:52px;resize:vertical;border-radius:10px;border:1px solid var(--line);background:var(--bg);padding:8px}
select{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:0 8px}
button.go{border:0;border-radius:10px;background:var(--accent);color:var(--accent-ink);font-weight:700;padding:0 14px}
button.quiet{background:transparent;border:1px solid var(--line);border-radius:8px;padding:6px 8px;color:var(--muted);cursor:pointer}
.sub{padding:8px;border-radius:8px;background:var(--panel2);margin:0 0 6px;font-size:12px}
.sub b{color:var(--accent)}
.bottom{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid var(--line);background:var(--bg2);min-height:0}
.pane{overflow:auto;padding:8px 12px;font-size:12px}
.pane + .pane{border-left:1px solid var(--line)}
.pane h3{margin-top:0}
.file{display:flex;justify-content:space-between;gap:8px;padding:3px 0;color:var(--muted)}
.file b{color:var(--text);font-weight:500}
pre{margin:0;white-space:pre-wrap;color:var(--muted)}
@media(max-width:900px){
  .mid{grid-template-columns:1fr}
  .side,.rail{max-height:180px}
  body{grid-template-rows:48px auto 1fr 160px}
}
</style></head>
<body>
<header class="top">
  <b>POCKET LIGHT</b>
  <span id="st">Workspace shell</span>
  <span style="flex:1"></span>
  <a href="/desk">Desk</a>
  <a href="/spark-group">Spark Group</a>
</header>
<div class="mid">
  <aside class="side">
    <button class="quiet" type="button" id="newChat">New chat</button>
    <h3>Projects</h3>
    <div id="projects"></div>
    <h3>Chats</h3>
    <div id="loose"></div>
  </aside>
  <section class="center">
    <div class="log" id="log"></div>
    <form class="form" id="f">
      <select id="agent" aria-label="Agent"></select>
      <textarea id="t" placeholder="Talk in this thread. The seat reads the checkout." rows="2"></textarea>
      <button class="go" type="submit">Send</button>
    </form>
  </section>
  <aside class="rail" id="rail">
    <h3>Agent</h3>
    <div id="seat" class="sub">Pick a thread.</div>
    <h3>Subagents</h3>
    <div id="subs"></div>
  </aside>
</div>
<div class="bottom">
  <div class="pane">
    <h3>Files</h3>
    <div id="files"></div>
  </div>
  <div class="pane">
    <h3>Preview</h3>
    <pre id="preview"></pre>
  </div>
</div>
<script>
let current='';
const log=document.getElementById('log');
const agent=document.getElementById('agent');
function api(path, body){
  const opt=body?{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{credentials:'include'};
  return fetch(path,opt).then(r=>r.json());
}
function btn(row){
  const b=document.createElement('button');
  b.type='button'; b.className='thread'+(row.id===current?' on':'');
  b.innerHTML='<b></b><i></i>';
  b.querySelector('b').textContent=row.title;
  b.querySelector('i').textContent=(row.present?'on disk':'missing')+' · '+row.messages;
  b.onclick=()=>openThread(row.id);
  return b;
}
function paintList(rows){
  const projects=document.getElementById('projects');
  const loose=document.getElementById('loose');
  projects.replaceChildren(); loose.replaceChildren();
  rows.forEach(row=>{(row.kind==='loose'?loose:projects).appendChild(btn(row));});
}
function paintThread(j){
  const th=j.thread||{};
  current=th.id||current;
  document.getElementById('st').textContent=(th.title||'')+(th.cwd?' · '+th.cwd:'');
  document.getElementById('seat').textContent=(j.agent||'grok')+' · '+(th.title||'');
  if(j.agent) agent.value=j.agent;
  log.replaceChildren();
  (j.messages||[]).forEach(m=>{
    const d=document.createElement('div');
    d.className='m'+(m.role==='you'?' you':'');
    const w=document.createElement('span'); w.className='who'; w.textContent=m.agent||m.role;
    d.appendChild(w); d.appendChild(document.createTextNode(m.text||''));
    log.appendChild(d);
  });
  log.scrollTop=log.scrollHeight;
  const subs=document.getElementById('subs');
  subs.replaceChildren();
  (j.subagents||[]).slice().reverse().forEach(s=>{
    const d=document.createElement('div'); d.className='sub';
    d.innerHTML='<b></b> ';
    d.querySelector('b').textContent=s.role+' · '+s.status;
    d.appendChild(document.createTextNode(s.detail||''));
    subs.appendChild(d);
  });
  const files=document.getElementById('files');
  files.replaceChildren();
  (j.artifacts||[]).forEach(f=>{
    const d=document.createElement('div'); d.className='file';
    const name=document.createElement('b'); name.textContent=f.name;
    const kind=document.createElement('span'); kind.textContent=f.kind;
    d.appendChild(name); d.appendChild(kind); files.appendChild(d);
  });
  if(!(j.artifacts||[]).length){
    const empty=document.createElement('div'); empty.className='file'; empty.textContent='No checkout files.';
    files.appendChild(empty);
  }
  document.getElementById('preview').textContent=j.preview||'';
}
async function openThread(id){
  const j=await api('/v1/pocket-light/thread?id='+encodeURIComponent(id));
  if(!j.ok) return;
  paintThread(j);
  document.querySelectorAll('.thread').forEach(el=>el.classList.toggle('on', el.querySelector('b').textContent===(j.thread||{}).title));
}
async function boot(){
  const j=await api('/v1/pocket-light');
  document.getElementById('st').textContent=j.note||'POCKET LIGHT';
  (j.agents||[]).forEach(name=>{
    const o=document.createElement('option'); o.value=name; o.textContent=name; agent.appendChild(o);
  });
  paintList(j.threads||[]);
  const first=(j.threads||[])[0];
  if(first) openThread(first.id);
}
document.getElementById('f').onsubmit=async ev=>{
  ev.preventDefault();
  const t=document.getElementById('t');
  const text=(t.value||'').trim();
  if(!text||!current) return;
  t.value='';
  const j=await api('/v1/pocket-light/chat',{thread:current,text,agent:agent.value});
  if(j.ok){ paintThread(j); const st=await api('/v1/pocket-light'); paintList(st.threads||[]); }
};
document.getElementById('newChat').onclick=async()=>{
  const title=prompt('Chat title','New chat');
  if(!title) return;
  const made=await api('/v1/pocket-light/threads',{title});
  const st=await api('/v1/pocket-light');
  paintList(st.threads||[]);
  if(made.id) openThread(made.id);
};
boot();
</script>
</body></html>
"""
