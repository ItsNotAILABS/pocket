"""Work Studio — first-class digital assistant surface (separate from desk coding chat).

Agentic help for real human digital life: research, plans, email drafts, buy/reserve,
calendar, Muse Spark, Auro, screen — plus optional work loops for power users.
"""

from __future__ import annotations


def work_studio_html() -> str:
    return STUDIO_HTML


STUDIO_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#07070a"/>
<meta name="description" content="POCKET Work Studio — agentic digital assistant for real life, separate from the coding desk."/>
<title>POCKET · Work Studio</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#07070a;--bg2:#0c0c10;--panel:#121218;--panel2:#18181f;
  --line:rgba(255,255,255,.08);--line2:rgba(255,255,255,.14);--text:#e8e8ed;--muted:#8b8b9a;--fg:#fafafa;
  --accent:#10a37f;--violet:#a78bfa;--pink:#f472b6;--blue:#60a5fa;--amber:#fbbf24;--teal:#2dd4bf;--purple:#a855f7;
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --r:14px;--glow:0 0 0 1px rgba(16,163,127,.25),0 8px 28px rgba(16,163,127,.12);
  --ease:cubic-bezier(.22,1,.36,1);--t:180ms var(--ease);
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0}
body{
  font-family:var(--font);background:
    radial-gradient(900px 480px at 15% -10%,rgba(45,212,191,.07),transparent 50%),
    radial-gradient(800px 400px at 100% 0%,rgba(168,85,247,.05),transparent 45%),
    var(--bg);
  color:var(--text);-webkit-font-smoothing:antialiased;color-scheme:dark
}
a{color:var(--accent);text-decoration:none}
button,input,textarea,select{font:inherit;color:inherit}
button{cursor:pointer;border:0;background:none}
button:disabled{opacity:.4;cursor:not-allowed}
.app{min-height:100%;display:flex;flex-direction:column}
.top{
  display:flex;align-items:center;gap:12px;padding:11px 18px;flex-wrap:wrap;
  border-bottom:1px solid var(--line);background:rgba(7,7,10,.78);backdrop-filter:blur(22px) saturate(1.3);position:sticky;top:0;z-index:20
}
.mark{
  width:28px;height:28px;border-radius:9px;display:grid;place-items:center;font-weight:800;font-size:13px;color:#041;
  background:linear-gradient(145deg,#2dd4bf,var(--accent),#0a7a5f);box-shadow:0 0 0 1px rgba(16,163,127,.35)
}
.brand{font-weight:700;letter-spacing:-.03em;color:var(--fg);font-size:14px}
.brand small{display:block;font-weight:500;font-size:11px;color:var(--muted);letter-spacing:0}
.nav{display:flex;gap:3px;margin-left:8px;flex-wrap:wrap;background:rgba(255,255,255,.03);padding:3px;border-radius:11px;border:1px solid var(--line)}
.nav a{
  padding:7px 12px;border-radius:8px;font-size:12.5px;font-weight:600;color:var(--muted)
}
.nav a:hover{color:var(--fg);background:rgba(255,255,255,.05)}
.nav a.on{color:var(--fg);background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.03));box-shadow:inset 0 0 0 1px rgba(255,255,255,.04)}
.grow{flex:1;min-width:8px}
.pill{
  font-size:11px;font-weight:650;padding:5px 10px;border-radius:999px;border:1px solid var(--line);color:var(--muted)
}
.pill.on{color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
.wrap{max-width:1120px;width:100%;margin:0 auto;padding:20px 18px 100px}
.hero{margin-bottom:18px}
.hero h1{margin:0 0 8px;font-size:clamp(24px,3.2vw,34px);letter-spacing:-.04em;color:var(--fg);font-weight:650}
.hero p{margin:0;max-width:620px;color:var(--muted);line-height:1.55;font-size:14.5px}
.assist-shell{
  display:grid;grid-template-columns:1fr;gap:0;border:1px solid var(--line);border-radius:18px;
  background:rgba(12,12,16,.9);box-shadow:0 20px 50px rgba(0,0,0,.35);overflow:hidden;min-height:min(62vh,560px)
}
.assist-main{display:flex;flex-direction:column;min-height:min(62vh,560px)}
.assist-bar{
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 14px;border-bottom:1px solid var(--line);
  background:rgba(7,7,10,.6)
}
.assist-bar select{
  background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:12.5px;font-weight:600
}
.eng-chip{
  border:1px solid var(--line);background:rgba(255,255,255,.02);color:var(--muted);border-radius:999px;
  padding:5px 10px;font-size:11.5px;font-weight:650
}
.eng-chip:hover,.eng-chip.on{color:#5eead4;border-color:rgba(45,212,191,.4);background:rgba(45,212,191,.1)}
.assist-stream{
  flex:1;min-height:280px;overflow:auto;padding:16px 18px;display:flex;flex-direction:column;gap:12px
}
.bubble{max-width:min(920px,100%);animation:rise .28s var(--ease) both}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.bubble.user{align-self:flex-end}
.bubble.agent{align-self:flex-start;width:100%}
.bubble.user .body{
  padding:12px 14px;border-radius:16px 16px 6px 16px;background:linear-gradient(145deg,#0d9488,#0f766e);
  color:#ecfdf5;font-size:14.5px;line-height:1.5;white-space:pre-wrap
}
.bubble.agent .meta{font-size:11px;color:var(--muted);margin-bottom:6px;display:flex;gap:8px;flex-wrap:wrap}
.bubble.agent .body{
  padding:4px 2px;font-size:14.5px;line-height:1.55;color:var(--text)
}
.bubble.agent .body h1,.bubble.agent .body h2,.bubble.agent .body h3{color:var(--fg);letter-spacing:-.02em;margin:12px 0 6px}
.bubble.agent .body h1{font-size:18px}.bubble.agent .body h2{font-size:16px}.bubble.agent .body h3{font-size:14.5px}
.bubble.agent .body p{margin:0 0 8px}
.bubble.agent .body ul{margin:0 0 10px;padding-left:18px}
.bubble.agent .body code{font-family:var(--mono);font-size:12.5px;background:rgba(0,0,0,.35);padding:1px 5px;border-radius:4px}
.bubble.agent .body pre{
  background:#0a0a0e;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;max-height:280px;
  font-family:var(--mono);font-size:12px;color:#b7f0c6
}
.bubble.agent .body a{color:#5eead4}
.empty-assist{margin:auto;text-align:center;padding:28px 16px;max-width:440px;color:var(--muted)}
.empty-assist h2{margin:0 0 8px;color:var(--fg);font-size:20px;letter-spacing:-.03em}
.empty-assist p{margin:0 0 14px;line-height:1.5;font-size:13.5px}
.quick{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.quick button{
  border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);
  border-radius:999px;padding:8px 12px;font-size:12px;font-weight:600
}
.quick button:hover{border-color:rgba(45,212,191,.4);color:#5eead4}
.composer{
  border-top:1px solid var(--line);padding:12px 14px 14px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.25))
}
.composer .box{
  display:flex;gap:8px;align-items:flex-end;background:var(--bg2);border:1px solid var(--line);
  border-radius:14px;padding:8px 10px
}
.composer textarea{
  flex:1;border:0;background:transparent;resize:none;min-height:44px;max-height:160px;padding:8px 6px;outline:none;font-size:14.5px;line-height:1.45
}
.composer .send{
  border-radius:10px;padding:10px 16px;font-weight:700;font-size:13px;
  background:linear-gradient(180deg,#2dd4bf,var(--accent));color:#041;box-shadow:var(--glow);transition:transform var(--t),filter var(--t)
}
.composer .send:hover{filter:brightness(1.05);transform:translateY(-1px)}
.composer .send:active{transform:none}
.composer-meta{display:flex;align-items:center;gap:8px;margin-top:8px;flex-wrap:wrap}
.composer-meta .hint{font-size:11px;color:var(--muted);margin-left:auto}
.assist-bar select:focus{outline:none;box-shadow:0 0 0 2px rgba(45,212,191,.25)}
.route-pill{
  font-size:10.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
  color:#5eead4;background:rgba(45,212,191,.1);border:1px solid rgba(45,212,191,.28);
  padding:3px 8px;border-radius:999px
}
.btn{
  display:inline-flex;align-items:center;gap:6px;padding:8px 12px;border-radius:10px;
  font-size:12.5px;font-weight:700;border:1px solid transparent
}
.btn-ghost{border-color:var(--line);color:var(--fg)}
.btn-ghost:hover{background:rgba(255,255,255,.05)}
.btn-primary{background:var(--accent);color:#041}
.btn-voice.on{color:#7dd3fc;border-color:rgba(11,132,254,.45);background:rgba(11,132,254,.12)}
.grid{display:grid;grid-template-columns:1.05fr .95fr;gap:14px;margin-top:18px}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
.card{
  background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px
}
.card h2{margin:0 0 4px;font-size:14px;font-weight:650;color:var(--fg);letter-spacing:-.02em}
.card .sub{font-size:12px;color:var(--muted);margin-bottom:12px;line-height:1.4}
.dual{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px}
.sys{border-radius:12px;padding:12px;border:1px solid var(--line);background:var(--bg2);min-height:100px}
.sys.cortex{border-color:rgba(96,165,250,.3);background:linear-gradient(160deg,rgba(96,165,250,.08),transparent)}
.sys.sub{border-color:rgba(167,139,250,.3);background:linear-gradient(160deg,rgba(167,139,250,.08),transparent)}
.sys b{display:block;font-size:12px;margin-bottom:6px}
.sys.cortex b{color:var(--blue)}.sys.sub b{color:var(--violet)}
.sys p{margin:0;font-size:12px;color:var(--muted);line-height:1.45}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:10px}
input,textarea,select{
  width:100%;background:var(--bg2);border:1px solid var(--line);border-radius:10px;
  padding:10px 12px;font-size:13.5px;outline:none
}
input:focus,textarea:focus{border-color:rgba(16,163,127,.45)}
label{display:block;font-size:11px;font-weight:650;color:var(--muted);margin:10px 0 5px;letter-spacing:.04em;text-transform:uppercase}
.types{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.type{border:1px solid var(--line);border-radius:12px;padding:10px;background:var(--bg2)}
.type .ic{font-size:16px;margin-bottom:4px}
.type b{display:block;font-size:12.5px;color:var(--fg)}
.type span{font-size:11px;color:var(--muted);line-height:1.35}
.loop{border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:8px;background:var(--bg2)}
.loop .head{display:flex;justify-content:space-between;gap:8px;align-items:center}
.loop b{color:var(--fg);font-size:13px}
.loop .actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.loop .actions button{font-size:11.5px;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);cursor:pointer;font-weight:650}
.loop .actions button.primary{background:var(--accent);border-color:transparent;color:#042}
.steps{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.chip-step{font-size:11px;padding:4px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.mono{font-family:var(--mono);font-size:11.5px;color:var(--muted);white-space:pre-wrap;max-height:160px;overflow:auto}
.stat{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat div{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:10px}
.stat span{display:block;font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.stat b{display:block;margin-top:4px;font-size:16px;color:var(--fg)}
.toast{
  position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--panel2);
  border:1px solid var(--line);padding:10px 14px;border-radius:12px;font-size:13px;opacity:0;transition:opacity .2s;z-index:50;
  max-width:90%;text-align:center
}
.toast.show{opacity:1}
.thinking{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:12.5px;padding:6px 0}
.think-orb{
  width:22px;height:22px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#5eead4,var(--accent));
  animation:pulse 1.2s ease-in-out infinite
}
@keyframes pulse{50%{transform:scale(.92);opacity:.75}}
.section-label{
  margin:28px 0 12px;font-size:11px;font-weight:750;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)
}
</style>
</head>
<body>
<div class="app">
  <header class="top">
    <div class="mark">P</div>
    <div class="brand">Work Studio<small>digital assistant · agentic life ops</small></div>
    <nav class="nav" aria-label="Surfaces">
      <a href="/desk">Desk</a>
      <a href="/work" class="on">Work Studio</a>
      <a href="/studio">Product Studio</a>
      <a href="/imagine">Imagine</a>
      <a href="/phone">Phone</a>
      <a href="/updates">Updates</a>
    </nav>
    <div class="grow"></div>
    <span class="pill" id="statusPill">assistant ready</span>
    <a class="btn btn-primary" href="/desk" style="text-decoration:none;margin-left:6px">Coding desk</a>
  </header>

  <main class="wrap">
    <div class="hero">
      <h1>Your agentic digital assistant</h1>
      <p>Separate from the coding desk. Ask for research, plans, drafts, reservations, shopping research, screen help, Muse Spark, or Auro — engines route automatically or you pick one.</p>
    </div>

    <div class="assist-shell">
      <div class="assist-main">
        <div class="assist-bar">
          <select id="enginePick" title="Engine" aria-label="Assistant engine">
            <option value="auto">Auto route</option>
            <option value="plan">Plan</option>
            <option value="web">Research</option>
            <option value="work">Life ops (buy · reserve · notify)</option>
            <option value="muse_spark">Muse Spark</option>
            <option value="auro">Auro</option>
            <option value="codex">Codex</option>
            <option value="grok">Grok</option>
            <option value="claude">Claude</option>
            <option value="vision">Vision</option>
            <option value="browser">Browser</option>
          </select>
          <button type="button" class="eng-chip" data-e="auto">Auto</button>
          <button type="button" class="eng-chip" data-e="work">Life ops</button>
          <button type="button" class="eng-chip" data-e="web">Research</button>
          <button type="button" class="eng-chip" data-e="muse_spark">Muse</button>
          <button type="button" class="eng-chip" data-e="auro">Auro</button>
          <button type="button" class="eng-chip" data-e="plan">Plan</button>
          <span class="grow"></span>
          <span class="route-pill" id="routePill" style="display:none"></span>
          <button type="button" class="btn btn-ghost btn-voice" id="voiceBtn" onclick="toggleVoice()">🎙 Voice</button>
          <button type="button" class="btn btn-ghost" onclick="clearChat()">Clear</button>
        </div>
        <div class="assist-stream" id="stream" aria-live="polite">
          <div class="empty-assist" id="emptyAssist">
            <h2>What do you need done?</h2>
            <p>Real digital life help — research, plans, email drafts, dinner reservations, shopping research, screen eyes. Coding stays on the desk.</p>
            <div class="quick">
              <button type="button" data-q="Research three good date-night restaurants near me and compare vibe and price">Dinner research</button>
              <button type="button" data-q="Reserve a table Friday 7pm for 2 — help me book">Reserve table</button>
              <button type="button" data-q="Draft a short email to reschedule a meeting to next Tuesday afternoon">Email draft</button>
              <button type="button" data-q="Plan my morning: priorities, time blocks, and first actions">Morning plan</button>
              <button type="button" data-q="Buy noise-cancelling headphones under $100 — research options">Buy research</button>
              <button type="button" data-q="Muse Spark: compare local coding agent desks">Muse Spark</button>
              <button type="button" data-q="Auro: explain local language models simply">Auro</button>
              <button type="button" data-q="What's on my screen? Summarize what you see">Screen</button>
            </div>
          </div>
        </div>
        <div class="composer">
          <div class="box">
            <textarea id="input" rows="2" placeholder="Ask your assistant… multi-part OK (buy X, reserve Y, research Z)"></textarea>
            <button type="button" class="send" id="sendBtn" onclick="sendAssist()">Send</button>
          </div>
          <div class="composer-meta">
            <button type="button" class="btn btn-ghost" onclick="sendToDesk('assist',$('input').value||'Continue this assist on the desk')">Open on desk</button>
            <button type="button" class="btn btn-ghost" onclick="location.href='/desk?agent=work'">Working board</button>
            <span class="hint" id="routeHint">Auto routes · engines work hard on this host</span>
          </div>
        </div>
      </div>
    </div>

    <div class="section-label">Power tools · design loops (optional)</div>
    <div class="grid">
      <section class="card">
        <h2>Cortex · Subcortex</h2>
        <div class="sub">System 1 talks. System 2 can work quietly while you read.</div>
        <div class="dual">
          <div class="sys cortex"><b>Cortex</b><p>Dialogue, explanations, narratives for you.</p></div>
          <div class="sys sub"><b>Subcortex</b><p>World-model writes, silent structure, facts.</p></div>
        </div>
        <label>Dual-loop goal</label>
        <textarea id="dualGoal" rows="2" placeholder="Product story, explain a concept, update world model…"></textarea>
        <div class="row">
          <button class="btn btn-primary" type="button" onclick="runDual()">Talk + silent work</button>
          <button class="btn btn-ghost" type="button" onclick="refreshWorld()">World model</button>
        </div>
        <pre class="mono" id="dualOut" style="margin-top:12px"></pre>
      </section>

      <section class="card">
        <h2>Always-on swarm</h2>
        <div class="sub">Background pulses across use cases and loops.</div>
        <div class="stat" id="swarmStats">
          <div><span>Status</span><b id="sOn">—</b></div>
          <div><span>Pulses</span><b id="sPulses">—</b></div>
          <div><span>Interval</span><b id="sIv">—</b></div>
        </div>
        <div class="row">
          <button class="btn btn-primary" type="button" onclick="swarmStart()">Start</button>
          <button class="btn btn-ghost" type="button" onclick="swarmPulse()">Pulse</button>
          <button class="btn btn-ghost" type="button" onclick="swarmStop()">Stop</button>
        </div>
        <pre class="mono" id="swarmOut" style="margin-top:12px"></pre>
      </section>

      <section class="card">
        <h2>Work types</h2>
        <div class="sub">Reusable labor units for loops.</div>
        <div class="types" id="types"></div>
        <label>Create type</label>
        <input id="typeName" placeholder="Name"/>
        <input id="typeDesc" placeholder="Description" style="margin-top:8px"/>
        <div class="row">
          <select id="typeLayer" style="width:auto;min-width:140px">
            <option value="cortex">Cortex</option>
            <option value="subcortex">Subcortex</option>
          </select>
          <button class="btn btn-primary" type="button" onclick="createType()">Add</button>
        </div>
      </section>

      <section class="card">
        <h2>Work loops</h2>
        <div class="sub">Chains of types. Generate from English.</div>
        <div id="loops"></div>
        <label>Generate from goal</label>
        <textarea id="loopGoal" rows="2" placeholder="Research, write, check, ship…"></textarea>
        <div class="row">
          <button class="btn btn-primary" type="button" onclick="genLoop()">Generate</button>
          <button class="btn btn-ghost" type="button" onclick="refreshStudio()">Refresh</button>
        </div>
        <pre class="mono" id="loopOut" style="margin-top:10px"></pre>
      </section>

      <section class="card" style="grid-column:1/-1">
        <h2>World model</h2>
        <div class="sub">Archetypes · prose · facts · syntax specs.</div>
        <div class="stat" id="wmStats"></div>
        <label>Search</label>
        <div class="row">
          <input id="wmQ" placeholder="hero journey · pathlib · Hamlet" style="flex:1"/>
          <button class="btn btn-primary" type="button" onclick="wmSearch()">Search</button>
        </div>
        <pre class="mono" id="wmOut" style="margin-top:10px"></pre>
      </section>
    </div>
  </main>
</div>
<div class="toast" id="toast"></div>
<script>
const $ = id => document.getElementById(id);
let token = localStorage.getItem('pocket_token') || sessionStorage.getItem('pocket_token') || '';
let voiceOn = localStorage.getItem('pocket_ws_voice') === '1';
let history = [];
try{ history = JSON.parse(localStorage.getItem('pocket_ws_history')||'[]')||[]; }catch(_){ history=[]; }

function toast(t){const el=$('toast');el.textContent=t;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2400)}
function headers(){
  const h={'Content-Type':'application/json'};
  if(window.PocketAuth) return Object.assign(h, PocketAuth.authHeaders());
  if(token){ h['Authorization']='Bearer '+token; h['X-Pocket-Token']=token; }
  return h;
}
async function ensureWorkAuth(){
  if(token) return true;
  if(window.PocketAuth){
    token = PocketAuth.getToken() || '';
    if(token) return true;
    const ens = await PocketAuth.ensureAuth({device:'work-studio'});
    if(ens.ok){ token = ens.token; return true; }
    return new Promise(function(resolve){
      PocketAuth.showPasswordGate({
        device:'work-studio',
        onSuccess: function(res){ token = res.token || PocketAuth.getToken(); resolve(!!token); }
      });
    });
  }
  return false;
}
async function api(path, opts={}){
  if(!token){ try{ await ensureWorkAuth(); }catch(_){ } }
  const r = await fetch(path, {...opts, headers:{...headers(), ...(opts.headers||{})}, credentials:'same-origin'});
  const text = await r.text();
  let j={}; try{j=text?JSON.parse(text):{}}catch(_){j={raw:text}}
  if(r.status===401){
    token='';
    try{ await ensureWorkAuth(); }catch(_){}
    throw new Error(j.error||'Sign in required');
  }
  if(!r.ok) throw new Error(j.error||j.message||('HTTP '+r.status));
  return j;
}
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function mdLite(raw){
  let t=esc(raw||'');
  t=t.replace(/```([\s\S]*?)```/g,(_,c)=>'<pre>'+c+'</pre>');
  t=t.replace(/^### (.*)$/gm,'<h3>$1</h3>');
  t=t.replace(/^## (.*)$/gm,'<h2>$1</h2>');
  t=t.replace(/^# (.*)$/gm,'<h1>$1</h1>');
  t=t.replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>');
  t=t.replace(/`([^`]+)`/g,'<code>$1</code>');
  t=t.replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
  t=t.replace(/^- (.*)$/gm,'<li>$1</li>');
  t=t.replace(/(<li>.*<\/li>\n?)+/g,m=>'<ul>'+m+'</ul>');
  t=t.replace(/\n\n/g,'</p><p>');
  return '<p>'+t+'</p>';
}
function sendToDesk(mode, prompt){
  try{
    localStorage.setItem('pocket_work_handoff', JSON.stringify({
      mode: mode||'assist', prompt: prompt||'', from:'work-studio', at:Date.now(), voice: voiceOn
    }));
  }catch(_){}
  location.href='/desk?agent='+encodeURIComponent(mode||'assist');
}
function loopDeskMode(L){
  const id=String((L&&L.id)||'').toLowerCase();
  const name=String((L&&L.name)||'').toLowerCase();
  if(id.includes('code')||name.includes('code')||id.includes('sprint')) return 'build';
  if(id.includes('swarm')||name.includes('swarm')) return 'coding_swarm';
  if(id.includes('research')||name.includes('research')) return 'assist';
  if(id.includes('gene')||name.includes('genetic')) return 'genetic';
  return 'build';
}
function runLoopOnDesk(L){
  const steps=(L.steps||[]).map(s=>'  - '+s).join('\\n');
  const prompt=[
    '# Work loop · '+(L.name||L.id||'loop'),
    '',
    L.description||'',
    '',
    '## Steps',
    steps||'  - (no steps listed)',
    '',
    'Execute this loop on the POCKET desk. Report progress per step.',
  ].join('\\n');
  sendToDesk(loopDeskMode(L), prompt);
  toast('Opening desk with loop: '+(L.name||L.id));
}
function toggleVoice(){
  voiceOn=!voiceOn;
  localStorage.setItem('pocket_ws_voice', voiceOn?'1':'0');
  paintVoice();
  toast(voiceOn?'Voice on — replies can speak':'Voice off');
}
function paintVoice(){
  const b=$('voiceBtn');
  if(b){ b.classList.toggle('on', voiceOn); b.classList.toggle('btn-voice', true); b.textContent=voiceOn?'🎙 Voice on':'🎙 Voice'; }
}
function clearChat(){
  history=[];
  try{ localStorage.removeItem('pocket_ws_history'); }catch(_){}
  renderHistory();
}
function saveHist(){
  try{ localStorage.setItem('pocket_ws_history', JSON.stringify(history.slice(-40))); }catch(_){}
}
function renderHistory(){
  const box=$('stream');
  if(!history.length){
    box.innerHTML=`<div class="empty-assist" id="emptyAssist">
      <h2>What do you need done?</h2>
      <p>Real digital life help — research, plans, drafts, reservations, shopping research, screen eyes. Coding stays on the desk.</p>
      <div class="quick" id="quickRow"></div>
    </div>`;
    const qr=$('quickRow');
    if(qr){
      document.querySelectorAll('[data-q]').forEach(()=>{});
      // re-bind from template buttons via static list
      const qs=[
        ['Dinner research','Research three good date-night restaurants and compare vibe and price'],
        ['Reserve table','Reserve a table Friday 7pm for 2 — help me book'],
        ['Email draft','Draft a short email to reschedule a meeting to next Tuesday afternoon'],
        ['Morning plan','Plan my morning: priorities, time blocks, and first actions'],
        ['Buy research','Buy noise-cancelling headphones under $100 — research options'],
        ['Muse Spark','Muse Spark: compare local coding agent desks'],
        ['Auro','Auro: explain local language models simply'],
        ['Screen','What is on my screen? Summarize what you see'],
      ];
      qr.innerHTML=qs.map(([l,q])=>'<button type="button" data-fill="'+esc(q)+'">'+esc(l)+'</button>').join('');
      qr.querySelectorAll('button').forEach(b=>b.onclick=()=>{ $('input').value=b.getAttribute('data-fill')||''; sendAssist(); });
    }
    return;
  }
  box.innerHTML='';
  history.forEach(turn=>{
    if(turn.role==='user'){
      const d=document.createElement('div');
      d.className='bubble user';
      d.innerHTML='<div class="body">'+esc(turn.text)+'</div>';
      box.appendChild(d);
    }else{
      const d=document.createElement('div');
      d.className='bubble agent';
      d.innerHTML='<div class="meta"><span>'+esc(turn.engine||'assist')+'</span><span>'+esc(turn.intent||'')+'</span><span>'+(turn.ms||0)+'ms</span></div><div class="body">'+mdLite(turn.text||'')+'</div>';
      box.appendChild(d);
    }
  });
  box.scrollTop=box.scrollHeight;
  // speak last agent if voice
  if(voiceOn){
    const last=[...history].reverse().find(t=>t.role==='agent');
    if(last && last.text && !last._spoke){
      last._spoke=true;
      speak(last.text);
    }
  }
}
function speak(raw){
  if(!window.speechSynthesis) return;
  try{ window.speechSynthesis.cancel(); }catch(_){}
  let t=String(raw||'').replace(/```[\s\S]*?```/g,' ').replace(/[#*_`]/g,' ').replace(/\s+/g,' ').trim().slice(0,500);
  if(t.length<8) return;
  const u=new SpeechSynthesisUtterance(t);
  u.rate=0.96; u.pitch=1.02;
  window.speechSynthesis.speak(u);
}
let _assistBusy=false;
function autosizeInput(){
  const el=$('input'); if(!el) return;
  el.style.height='auto';
  el.style.height=Math.min(160, Math.max(44, el.scrollHeight))+'px';
}
function setRouteUI(engine, intent, ms){
  const hint=$('routeHint'), pill=$('routePill');
  const label=(engine||'assist')+(intent?(' · '+intent):'')+(ms!=null?(' · '+ms+'ms'):'');
  if(hint) hint.textContent='Routed → '+label;
  if(pill){
    pill.style.display='inline-flex';
    pill.textContent=engine||'assist';
  }
  document.querySelectorAll('.eng-chip').forEach(x=>{
    const e=x.getAttribute('data-e');
    x.classList.toggle('on', e===engine || (engine==='plan'&&e==='plan') || (engine==='web'&&e==='web') || (engine==='work'&&e==='work') || (engine==='muse_spark'&&e==='muse_spark') || (engine==='auro'&&e==='auro'));
  });
}
async function sendAssist(){
  if(_assistBusy) return;
  const el=$('input');
  const text=(el&&el.value||'').trim();
  if(!text) return;
  const engine=($('enginePick')&&$('enginePick').value)||'auto';
  el.value=''; autosizeInput();
  history.push({role:'user', text});
  renderHistory();
  const box=$('stream');
  const think=document.createElement('div');
  think.className='thinking'; think.id='thinking';
  think.innerHTML='<span class="think-orb"></span><span id="thinkLabel">Assistant working…</span>';
  box.appendChild(think);
  box.scrollTop=box.scrollHeight;
  _assistBusy=true;
  $('sendBtn').disabled=true;
  $('statusPill').textContent='working…';
  $('statusPill').className='pill on';
  // progressive status labels while waiting
  const labels=['Routing…','Working on host…','Gathering results…','Almost ready…'];
  let li=0;
  const tick=setInterval(()=>{
    const lab=$('thinkLabel');
    if(lab) lab.textContent=labels[li++%labels.length];
  }, 900);
  try{
    const j=await api('/v1/work-studio/assist',{
      method:'POST',
      body:JSON.stringify({text, engine, voice: voiceOn})
    });
    history.push({
      role:'agent',
      text: j.reply||j.result||'Done.',
      engine: j.engine||engine,
      intent: j.intent||'',
      ms: j.ms||0
    });
    saveHist();
    setRouteUI(j.engine||engine, j.intent, j.ms);
    toast('Done · '+(j.engine||'assist')+(j.ms?(' · '+j.ms+'ms'):''));
  }catch(e){
    history.push({role:'agent', text:'# Error\n\n'+(e.message||e)+'\n\n_Tip: sign in on /desk if this PC requires auth, then return._', engine:'assist', intent:'error', ms:0});
    toast(e.message||'failed');
  }
  clearInterval(tick);
  _assistBusy=false;
  $('sendBtn').disabled=false;
  $('statusPill').textContent='assistant ready';
  $('statusPill').className='pill';
  renderHistory();
  try{ $('input').focus(); }catch(_){}
}
$('input').addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendAssist(); }
});
$('input').addEventListener('input', autosizeInput);
document.querySelectorAll('.eng-chip').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.eng-chip').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    if($('enginePick')) $('enginePick').value=b.getAttribute('data-e')||'auto';
    try{ $('input').focus(); }catch(_){}
  };
});
if($('enginePick')){
  $('enginePick').addEventListener('change', ()=>{
    const v=$('enginePick').value||'auto';
    document.querySelectorAll('.eng-chip').forEach(x=>x.classList.toggle('on', x.getAttribute('data-e')===v));
  });
}
document.querySelectorAll('[data-q]').forEach(b=>{
  b.onclick=()=>{ $('input').value=b.getAttribute('data-q')||''; autosizeInput(); sendAssist(); };
});

async function refreshStudio(){
  try{
    const cat = await api('/v1/work-studio');
    const types = cat.types||[];
    $('types').innerHTML = types.map(t=>`
      <div class="type" style="border-color:${esc(t.color||'#333')}33">
        <div class="ic">${esc(t.icon||'●')}</div>
        <b>${esc(t.name)}</b>
        <span>${esc(t.layer)} · ${esc(t.description||'')}</span>
      </div>`).join('');
    const loops = cat.loops||[];
    window.__workLoops = loops;
    $('loops').innerHTML = loops.map((L,i)=>`
      <div class="loop">
        <div class="head">
          <b style="color:${esc(L.color||'#10a37f')}">${esc(L.name)}</b>
          <span class="pill ${L.always_on_eligible?'on':''}">${L.always_on_eligible?'swarm-ready':'manual'}</span>
        </div>
        <div class="sub" style="margin:4px 0 0;font-size:12px;color:var(--muted)">${esc(L.description||'')}</div>
        <div class="steps">${(L.steps||[]).map(s=>`<span class="chip-step">${esc(s)}</span>`).join('')}</div>
        <div class="actions">
          <button type="button" class="primary" data-loop-ix="${i}">Run on desk</button>
          <button type="button" data-assist-ix="${i}">Assist first</button>
        </div>
      </div>`).join('') || '<div class="sub">No loops yet</div>';
    $('loops').querySelectorAll('[data-loop-ix]').forEach(b=>{
      b.onclick=()=>{ const L=window.__workLoops[Number(b.getAttribute('data-loop-ix'))]; if(L) runLoopOnDesk(L); };
    });
    $('loops').querySelectorAll('[data-assist-ix]').forEach(b=>{
      b.onclick=()=>{
        const L=window.__workLoops[Number(b.getAttribute('data-assist-ix'))];
        if(!L) return;
        $('input').value='Run work loop "'+(L.name||L.id)+'": '+(L.description||'')+'. Steps: '+(L.steps||[]).join(' → ');
        sendAssist();
      };
    });
  }catch(e){
    $('types').innerHTML = '<div class="sub">Sign in on /desk first if this is empty — assist may still work on this PC.</div>';
  }
  refreshSwarm();
  refreshWorld();
}
async function refreshSwarm(){
  try{
    const s = await api('/v1/swarm');
    $('sOn').textContent = s.running ? 'ON' : 'off';
    $('sPulses').textContent = s.pulses||0;
    $('sIv').textContent = (s.interval_sec||90)+'s';
  }catch(e){}
}
async function refreshWorld(){
  try{
    const w = await api('/v1/world-model');
    const c = w.counts||{};
    $('wmStats').innerHTML = `
      <div><span>Archetypes</span><b>${c.archetypes||0}</b></div>
      <div><span>Prose</span><b>${c.prose_standards||0}</b></div>
      <div><span>Facts</span><b>${c.facts||0}</b></div>
      <div><span>Syntax</span><b>${c.syntax_specs||0}</b></div>
      <div><span>Narrative</span><b>${c.narrative_state||0}</b></div>
      <div><span>Sub logs</span><b>${c.subcortex_log||0}</b></div>`;
  }catch(e){}
}
async function runDual(){
  const goal=($('dualGoal').value||'').trim();
  if(!goal) return toast('Enter a goal');
  $('dualOut').textContent='Running…';
  try{
    const j=await api('/v1/dual/run',{method:'POST',body:JSON.stringify({goal})});
    $('dualOut').textContent=JSON.stringify(j,null,2).slice(0,3000);
  }catch(e){
    try{
      const j=await api('/v1/work-studio/assist',{method:'POST',body:JSON.stringify({text:goal, engine:'plan'})});
      $('dualOut').textContent=j.reply||e.message;
    }catch(e2){ $('dualOut').textContent=e.message||String(e); }
  }
}
async function swarmStart(){ try{ await api('/v1/swarm/start',{method:'POST',body:'{}'}); toast('Swarm on'); refreshSwarm(); }catch(e){ toast(e.message);} }
async function swarmStop(){ try{ await api('/v1/swarm/stop',{method:'POST',body:'{}'}); toast('Swarm off'); refreshSwarm(); }catch(e){ toast(e.message);} }
async function swarmPulse(){ try{ const j=await api('/v1/swarm/pulse',{method:'POST',body:'{}'}); $('swarmOut').textContent=JSON.stringify(j,null,2).slice(0,1200); refreshSwarm(); }catch(e){ toast(e.message);} }
async function createType(){
  try{
    await api('/v1/work-types',{method:'POST',body:JSON.stringify({
      name:$('typeName').value, description:$('typeDesc').value, layer:$('typeLayer').value
    })});
    toast('Type added'); $('typeName').value=''; $('typeDesc').value=''; refreshStudio();
  }catch(e){ toast(e.message); }
}
async function genLoop(){
  const goal=($('loopGoal').value||'').trim();
  if(!goal) return toast('Enter a goal');
  try{
    const j=await api('/v1/work-loops/generate',{method:'POST',body:JSON.stringify({goal})});
    $('loopOut').textContent=JSON.stringify(j,null,2).slice(0,2000);
    refreshStudio();
  }catch(e){ toast(e.message); }
}
async function wmSearch(){
  const q=($('wmQ').value||'').trim();
  if(!q) return;
  try{
    const j=await api('/v1/world-model/search?q='+encodeURIComponent(q));
    $('wmOut').textContent=JSON.stringify(j,null,2).slice(0,2500);
  }catch(e){
    try{
      const j=await api('/v1/world/search',{method:'POST',body:JSON.stringify({q})});
      $('wmOut').textContent=JSON.stringify(j,null,2).slice(0,2500);
    }catch(e2){ $('wmOut').textContent=e.message||String(e); }
  }
}

paintVoice();
renderHistory();
refreshStudio();
// consume desk handoff reverse
try{
  const h=JSON.parse(localStorage.getItem('pocket_ws_seed')||'null');
  if(h && h.prompt && Date.now()-(h.at||0)<3600000){
    $('input').value=h.prompt;
    if(h.engine) $('enginePick').value=h.engine;
    localStorage.removeItem('pocket_ws_seed');
  }
}catch(_){}
</script>
</body>
</html>
"""
