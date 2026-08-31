"""Voice-to-Voice Agent Studio — multi-sensory desk for POCKET.

Implements the practical core of the Ultra-Low-Latency Multi-Sensory V2V paper
inside the POCKET host (not a separate product):

  · 60fps HTML5 Canvas visualizer (5 styles) — emerald user / indigo agent
  · Dual-axis Persona (voice) × Mindset (cognitive)
  · Code-to-Voice context snap (editor → agent session buffer)
  · Client energy/FFT telemetry + patient listening via existing voice stack
  · Conversational Fusion on host for multi-domain routing

Paper claims for native multimodal <140ms RTT require a realtime multimodal
engine; this studio uses pocket-voice + POCKET fusion as the production path
and surfaces telemetry so quality is visible.
"""

from __future__ import annotations

VOICE_STUDIO_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="theme-color" content="#050508"/>
<title>POCKET · Voice Studio</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#06060a;--panel:#121218;--panel2:#1a1a24;--line:rgba(255,255,255,.08);
  --fg:#fafafa;--muted:#8b8b98;--accent:#10a37f;--emerald:#34d399;--indigo:#818cf8;
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --ease:cubic-bezier(.22,1,.36,1);--t:180ms var(--ease);
  --glow:0 0 0 1px rgba(16,163,127,.3),0 8px 28px rgba(16,163,127,.15);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{
  font-family:var(--font);
  background:radial-gradient(1000px 500px at 20% -10%,rgba(16,163,127,.08),transparent 50%),
    radial-gradient(800px 400px at 100% 0%,rgba(129,140,248,.06),transparent 45%),var(--bg);
  color:var(--fg);overflow:hidden;letter-spacing:-.01em;-webkit-font-smoothing:antialiased
}
a{color:var(--accent);text-decoration:none}
button,select,textarea,input{font:inherit;color:inherit}
button{cursor:pointer;border:0;background:none}
.app{display:grid;grid-template-rows:52px 1fr;height:100dvh;height:100vh}
.top{
  display:flex;align-items:center;gap:10px;padding:0 16px;border-bottom:1px solid var(--line);
  background:rgba(6,6,10,.78);backdrop-filter:blur(22px) saturate(1.35);z-index:5
}
.brand{display:flex;align-items:center;gap:9px;font-weight:750;letter-spacing:-.04em;font-size:14px}
.mark{
  width:28px;height:28px;border-radius:9px;background:linear-gradient(145deg,#34d399,var(--accent),#0a7a5f);
  color:#041;display:grid;place-items:center;font-size:12px;font-weight:800;
  box-shadow:0 0 0 1px rgba(16,163,127,.4),0 4px 16px rgba(16,163,127,.25)
}
.chip{font-size:10px;font-weight:700;padding:4px 10px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:rgba(255,255,255,.02)}
.chip.on{color:#6ee7b7;border-color:rgba(16,163,127,.45);background:rgba(16,163,127,.12)}
.grow{flex:1}
.top a.btn,.top button.btn{
  border:1px solid var(--line);border-radius:10px;padding:7px 12px;font-size:12px;font-weight:650;color:var(--muted);
  transition:all var(--t)
}
.top a.btn:hover,.top button.btn:hover{color:var(--fg);background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.14)}
.main{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(280px,0.9fr) minmax(260px,0.85fr);min-height:0}
@media(max-width:1100px){.main{grid-template-columns:1fr;grid-template-rows:auto auto 1fr;overflow:auto}}
.col{display:flex;flex-direction:column;min-height:0;border-right:1px solid var(--line);background:rgba(0,0,0,.15)}
.col:last-child{border-right:0}
.col-h{
  flex:0 0 auto;padding:12px 14px;border-bottom:1px solid var(--line);font-size:10.5px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--muted);font-weight:700;display:flex;align-items:center;gap:8px
}
.col-h b{color:var(--fg);text-transform:none;letter-spacing:-.03em;font-size:13.5px;font-weight:700}
.col-b{flex:1;min-height:0;overflow:auto;padding:14px}
.viz-wrap{
  position:relative;height:min(44vh,380px);min-height:240px;border-radius:18px;border:1px solid var(--line);
  background:radial-gradient(ellipse at 50% 60%,rgba(16,163,127,.1),transparent 55%),
    radial-gradient(ellipse at 80% 20%,rgba(129,140,248,.06),transparent 40%),#08080e;
  overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.04)
}
#viz{display:block;width:100%;height:100%}
.viz-badge{position:absolute;left:12px;top:12px;display:flex;gap:6px;flex-wrap:wrap}
.viz-badge span{
  font-size:10px;font-weight:700;padding:4px 9px;border-radius:999px;border:1px solid var(--line);
  background:rgba(0,0,0,.55);backdrop-filter:blur(8px)
}
.viz-badge .u{color:var(--emerald);border-color:rgba(52,211,153,.4)}
.viz-badge .a{color:var(--indigo);border-color:rgba(129,140,248,.45)}
.styles{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.styles button{
  padding:8px 12px;border-radius:999px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.03),transparent),var(--panel);
  color:var(--muted);font-size:11px;font-weight:650;transition:all var(--t)
}
.styles button.on{color:#041;background:linear-gradient(180deg,#34d399,var(--accent));border-color:transparent;box-shadow:var(--glow)}
.tele{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px}
.tele .t{
  background:linear-gradient(165deg,rgba(255,255,255,.03),transparent),var(--panel);
  border:1px solid var(--line);border-radius:12px;padding:10px 11px
}
.tele .t b{display:block;font-size:15px;font-variant-numeric:tabular-nums;color:var(--fg);font-weight:700;letter-spacing:-.02em}
.tele .t span{font-size:9.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:650}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
label.f{display:block;font-size:10.5px;color:var(--muted);font-weight:700;margin:0 0 5px;letter-spacing:.04em;text-transform:uppercase}
select,textarea,input[type=text]{
  width:100%;padding:10px 12px;border-radius:11px;border:1px solid var(--line);
  background:#0a0a0e;color:var(--fg);transition:border-color var(--t),box-shadow var(--t)
}
select:focus,textarea:focus,input[type=text]:focus{outline:0;border-color:rgba(16,163,127,.5);box-shadow:0 0 0 3px rgba(16,163,127,.12)}
textarea{min-height:72px;resize:vertical;font-family:var(--mono);font-size:12px;line-height:1.45}
.actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.actions button{
  padding:11px 15px;border-radius:11px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.03),transparent),var(--panel);
  font-weight:700;font-size:12.5px;transition:all var(--t)
}
.actions button.primary{
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;border:0;box-shadow:var(--glow)
}
.actions button.hot{background:rgba(248,113,113,.12);border-color:rgba(248,113,113,.4);color:#fca5a5}
.actions button:disabled{opacity:.4}
.hint{font-size:11.5px;color:var(--muted);line-height:1.5;margin-top:10px}
.log{font-size:12.5px;line-height:1.45;display:flex;flex-direction:column;gap:8px}
.log .m{
  padding:11px 13px;border-radius:14px;border:1px solid var(--line);
  background:linear-gradient(165deg,rgba(255,255,255,.02),transparent),var(--panel)
}
.log .m.user{border-color:rgba(52,211,153,.3)}
.log .m.agent{border-color:rgba(129,140,248,.3)}
.log .m .who{font-size:10px;font-weight:750;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin-bottom:5px}
.log .m.user .who{color:var(--emerald)}
.log .m.agent .who{color:var(--indigo)}
.code-h{display:flex;gap:6px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.code-h button{
  padding:7px 12px;border-radius:9px;border:1px solid var(--line);
  background:var(--panel2);font-size:11px;font-weight:700;transition:all var(--t)
}
.code-h button:hover{border-color:rgba(16,163,127,.4);color:#6ee7b7}
#codeSnap{min-height:180px}
.snap-banner{
  display:none;margin-top:10px;padding:10px 12px;border-radius:12px;
  border:1px solid rgba(16,163,127,.4);background:rgba(16,163,127,.1);font-size:12px;color:#6ee7b7;line-height:1.4
}
.snap-banner.on{display:block}
.fusion{
  margin-top:12px;padding:12px 13px;border-radius:12px;border:1px solid rgba(129,140,248,.3);
  background:linear-gradient(135deg,rgba(129,140,248,.1),rgba(16,163,127,.04));
  font-size:12px;color:#c7d2fe;line-height:1.45
}
</style>
</head>
<body>
<div class="app">
  <header class="top">
    <div class="brand"><div class="mark">P</div>Voice Studio</div>
    <span class="chip on" id="liveChip">idle</span>
    <span class="chip" id="styleChip">Quantum Core</span>
    <div class="grow"></div>
    <a class="btn" href="/desk">← Desk</a>
    <a class="btn" href="/phone">Phone</a>
    <a class="btn" href="/v1/platform/coherent" target="_blank" rel="noopener">Platform map</a>
    <button type="button" class="btn" id="authBtn" onclick="doAuth()">Sign in</button>
  </header>
  <div class="main">
    <!-- Visualizer + telemetry -->
    <section class="col">
      <div class="col-h"><b>Canvas · 60fps FFT</b><span class="grow"></span><span class="chip" id="fpsChip">— fps</span></div>
      <div class="col-b">
        <div class="viz-wrap">
          <canvas id="viz"></canvas>
          <div class="viz-badge">
            <span class="u">● You · emerald</span>
            <span class="a">● Agent · indigo</span>
          </div>
        </div>
        <div class="styles" id="styles">
          <button type="button" class="on" data-style="quantum">Quantum Core</button>
          <button type="button" data-style="synapse">Neural Synapse</button>
          <button type="button" data-style="waves">Harmonic Waves</button>
          <button type="button" data-style="matrix">Digital Matrix</button>
          <button type="button" data-style="lotus">Zen Lotus</button>
        </div>
        <div class="tele">
          <div class="t"><b id="tUser">0.00</b><span>User level</span></div>
          <div class="t"><b id="tAgent">0.00</b><span>Agent level</span></div>
          <div class="t"><b id="tRtt">—</b><span>Turn RTT ms</span></div>
          <div class="t"><b id="tSr">16k / 24k</b><span>PCM targets</span></div>
        </div>
        <p class="hint">Visualizer maps bass/mid/treble from AnalyserNode FFT (N=2048). Emerald = mic energy; indigo = TTS / agent speak. Production path uses Web Speech + POCKET Fusion (native multimodal &lt;140ms needs a realtime engine when available).</p>
      </div>
    </section>

    <!-- Controls + conversation -->
    <section class="col">
      <div class="col-h"><b>Persona × Mindset</b><span class="grow"></span><span class="chip" id="fusionChip">Fusion —</span></div>
      <div class="col-b">
        <div class="row2">
          <div>
            <label class="f">Voice persona</label>
            <select id="persona">
              <option value="aria" selected>Aria (warm · patient)</option>
              <option value="coder">Coder pair (terse)</option>
              <option value="support">Support</option>
              <option value="sales">Sales</option>
              <option value="executive">Executive brief</option>
              <option value="zephyr">Zephyr · soft analytic</option>
              <option value="puck">Puck · playful builder</option>
              <option value="kore">Kore · steady mentor</option>
              <option value="charon">Charon · deep systems</option>
              <option value="fenrir">Fenrir · intense ship</option>
            </select>
          </div>
          <div>
            <label class="f">Mindset</label>
            <select id="mindset">
              <option value="coding_architect" selected>Senior Coding Architect</option>
              <option value="strategic">Strategic Mind Partner</option>
              <option value="founder">Founder Sanctuary</option>
              <option value="travel_dfw">DFW Travel · hospitality</option>
              <option value="debug">Debug · root cause</option>
            </select>
          </div>
        </div>
        <div class="row2" style="margin-top:10px">
          <div>
            <label class="f">Listening</label>
            <select id="scenario">
              <option value="patient" selected>Patient 1400ms</option>
              <option value="standard">Standard 650ms</option>
              <option value="fast_command">Fast 300ms</option>
              <option value="dictation">Dictation 2000ms</option>
            </select>
          </div>
          <div>
            <label class="f">Domain expert</label>
            <select id="expert">
              <option value="hotel_host">Hotel Host</option>
              <option value="airport_guide">Airport Guide</option>
              <option value="transit_concierge">Transit</option>
              <option value="dining_diplomat">Dining</option>
              <option value="support">Support</option>
            </select>
          </div>
        </div>
        <div class="actions">
          <button type="button" class="primary" id="btnTalk" onclick="toggleTalk()">🎙 Talk</button>
          <button type="button" id="btnSend" onclick="sendText()">Send text</button>
          <button type="button" id="btnSnap" onclick="snapContext()">Snap code → agent</button>
          <button type="button" class="hot" id="btnStop" onclick="stopAll()" disabled>Stop</button>
        </div>
        <label class="f" style="margin-top:12px">Type or dictate</label>
        <textarea id="input" placeholder="Speak or type… code context snaps in below"></textarea>
        <div class="fusion" id="fusionOut">Conversational Fusion idle — will route after each turn.</div>
        <div class="col-h" style="margin:14px -12px 0;border-top:1px solid var(--line);border-bottom:0;padding-top:12px"><b>Session</b></div>
        <div class="log" id="log"></div>
      </div>
    </section>

    <!-- Code context snap -->
    <section class="col">
      <div class="col-h"><b>Code-to-Voice snap</b><span class="grow"></span><span class="chip" id="snapChip">buffer empty</span></div>
      <div class="col-b">
        <div class="code-h">
          <button type="button" onclick="loadSample()">Sample</button>
          <button type="button" onclick="snapContext()">Snap into voice</button>
          <button type="button" onclick="clearSnap()">Clear buffer</button>
        </div>
        <label class="f">Workspace buffer (AST-lite: path + selection + lines)</label>
        <textarea id="codeSnap" spellcheck="false">// Snap this into the agent mid-conversation
function mergeSessions(a, b) {
  return { ...a, ...b, turns: [...(a.turns||[]), ...(b.turns||[])] };
}
</textarea>
        <label class="f" style="margin-top:10px">Path label</label>
        <input type="text" id="codePath" value="src/session.ts"/>
        <div class="snap-banner" id="snapBanner">Context armed — next turn includes snapped buffer.</div>
        <p class="hint" style="margin-top:12px">
          <b style="color:var(--fg)">Where this lives:</b> POCKET host <code style="color:var(--emerald)">/studio/voice</code>
          · audio stack <code style="color:var(--emerald)">pocket-voice-to-text</code>
          · Fusion <code style="color:var(--emerald)">conversational_fusion.py</code>
          · desk Aria / phone / Working share the same agents.
        </p>
        <p class="hint">Paper target RTT &lt;140ms = native multimodal duplex. This studio measures turn RTT (speech→reply start) over the current cascade and keeps the multi-sensory UI you can ship today.</p>
      </div>
    </section>
  </div>
</div>
<script>
const $ = id => document.getElementById(id);
let token = localStorage.getItem('pocket_token') || '';
let sessionId = null;
let talking = false;
let recog = null;
let audioCtx = null, analyser = null, micStream = null, raf = 0;
let style = 'quantum';
let userLevel = 0, agentLevel = 0, agentDecay = 0;
let fps = 0, frames = 0, lastFpsT = performance.now();
let contextBuffer = null;
let lastSpeakAt = 0;

const MINDSETS = {
  coding_architect: 'You are a senior coding architect. Prefer concrete files, functions, tradeoffs. Short spoken answers.',
  strategic: 'You are a strategic mind partner. Clarify goals, options, next bets. No fluff.',
  founder: 'You are a founder sanctuary — calm, protective of focus, help ship. Warm but direct.',
  travel_dfw: 'You help with DFW airline + hotel + transit + dining. Multi-domain; never force re-explain.',
  debug: 'You debug: reproduce, isolate, hypothesis, fix. One step at a time when speaking.'
};
const VOICE_ALIAS = {
  zephyr: 'aria', puck: 'coder', kore: 'support', charon: 'executive', fenrir: 'coder'
};

function authHeaders(){
  const h = {'Content-Type':'application/json','X-Pocket-Device':'voice-studio'};
  if(token){ h['Authorization']='Bearer '+token; h['X-Pocket-Token']=token; }
  return h;
}
async function api(path, opts={}){
  const r = await fetch(path, {...opts, headers:{...authHeaders(), ...(opts.headers||{})}});
  const t = await r.text();
  let j={}; try{ j=t?JSON.parse(t):{}; }catch(_){ j={raw:t}; }
  if(!r.ok) throw new Error(j.error||j.message||('HTTP '+r.status));
  return j;
}
async function doAuth(){
  // Prefer existing token, then desktop (localhost), then password gate (web)
  try{
    if(window.PocketAuth){
      token = PocketAuth.getToken() || token;
      if(token){
        $('authBtn').textContent = 'Signed in';
        $('liveChip').textContent = 'ready';
        $('liveChip').classList.add('on');
        return true;
      }
      const ens = await PocketAuth.ensureAuth({device:'voice-studio'});
      if(ens.ok && ens.token){
        token = ens.token;
        $('authBtn').textContent = 'Signed in';
        $('liveChip').textContent = 'ready';
        $('liveChip').classList.add('on');
        return true;
      }
      return new Promise(function(resolve){
        PocketAuth.showPasswordGate({
          device:'voice-studio',
          onSuccess: function(res){
            token = res.token || PocketAuth.getToken();
            $('authBtn').textContent = 'Signed in';
            $('liveChip').textContent = 'ready';
            $('liveChip').classList.add('on');
            resolve(true);
          }
        });
      });
    }
    const j = await fetch('/v1/auth/desktop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.json());
    token = j.token || '';
    if(token) localStorage.setItem('pocket_token', token);
    $('authBtn').textContent = 'Signed in';
    $('liveChip').textContent = 'ready';
    $('liveChip').classList.add('on');
    return !!token;
  }catch(e){ alert(e.message||e); return false; }
}
async function ensureAuth(){
  if(token) return true;
  try{
    const me = await api('/v1/auth/me');
    if(me && (me.user||me.ok!==false)){ $('authBtn').textContent='Signed in'; return true; }
  }catch(_){}
  await doAuth();
  return !!token;
}

/* ---- Canvas FFT visualizer (5 styles) ---- */
const canvas = $('viz');
const ctx = canvas.getContext('2d');
function resize(){
  const r = canvas.parentElement.getBoundingClientRect();
  const dpr = Math.min(2, window.devicePixelRatio||1);
  canvas.width = Math.floor(r.width * dpr);
  canvas.height = Math.floor(r.height * dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
window.addEventListener('resize', resize);
resize();

document.querySelectorAll('#styles button').forEach(b=>{
  b.onclick = ()=>{
    document.querySelectorAll('#styles button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    style = b.dataset.style;
    $('styleChip').textContent = b.textContent;
  };
});

function bandsFromAnalyser(){
  if(!analyser) return {bass:userLevel, mid:userLevel*0.8, treble:userLevel*0.5, wave:null};
  const n = analyser.frequencyBinCount;
  const data = new Uint8Array(n);
  analyser.getByteFrequencyData(data);
  const sr = audioCtx ? audioCtx.sampleRate : 48000;
  const binHz = sr / (analyser.fftSize || 2048);
  let bass=0, mid=0, treble=0, bc=0, mc=0, tc=0;
  for(let i=0;i<n;i++){
    const hz = i * binHz;
    const v = data[i]/255;
    if(hz < 250){ bass+=v; bc++; }
    else if(hz < 2000){ mid+=v; mc++; }
    else { treble+=v; tc++; }
  }
  bass = bc?bass/bc:0; mid=mc?mid/mc:0; treble=tc?treble/tc:0;
  const wave = new Uint8Array(analyser.fftSize);
  analyser.getByteTimeDomainData(wave);
  return {bass, mid, treble, wave};
}

function drawFrame(){
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if(!w||!h){ raf=requestAnimationFrame(drawFrame); return; }
  const {bass, mid, treble, wave} = bandsFromAnalyser();
  const u = Math.max(userLevel, bass*0.9 + mid*0.5);
  const a = Math.max(agentLevel, agentDecay);
  userLevel = u * 0.85;
  agentDecay *= 0.94;
  agentLevel = a * 0.92;
  $('tUser').textContent = u.toFixed(2);
  $('tAgent').textContent = a.toFixed(2);

  ctx.clearRect(0,0,w,h);
  // subtle grid
  ctx.fillStyle = '#0a0a0e';
  ctx.fillRect(0,0,w,h);

  const cx = w/2, cy = h*0.55;
  if(style==='quantum') drawQuantum(cx,cy,w,h,u,a,bass,mid,treble);
  else if(style==='synapse') drawSynapse(cx,cy,w,h,u,a,mid,treble);
  else if(style==='waves') drawWaves(w,h,u,a,wave,mid);
  else if(style==='matrix') drawMatrix(w,h,u,a,treble);
  else drawLotus(cx,cy,w,h,u,a,bass,mid);

  frames++;
  const now = performance.now();
  if(now - lastFpsT > 500){
    fps = Math.round(frames * 1000 / (now - lastFpsT));
    frames = 0; lastFpsT = now;
    $('fpsChip').textContent = fps + ' fps';
  }
  raf = requestAnimationFrame(drawFrame);
}

function drawQuantum(cx,cy,w,h,u,a,bass,mid,treble){
  const R = Math.min(w,h)*0.22;
  // agent indigo rings
  for(let i=5;i>=1;i--){
    const rr = R*(1.2 + i*0.28 + a*0.9);
    ctx.beginPath();
    ctx.arc(cx, cy, rr, 0, Math.PI*2);
    ctx.strokeStyle = `rgba(129,140,248,${0.08 + a*0.18})`;
    ctx.lineWidth = 1.5 + a*2;
    ctx.stroke();
  }
  // user emerald aura
  const g = ctx.createRadialGradient(cx,cy,R*0.2, cx,cy, R*(1.4+u*1.2));
  g.addColorStop(0, `rgba(52,211,153,${0.35+u*0.45})`);
  g.addColorStop(0.55, `rgba(16,163,127,${0.12+u*0.2})`);
  g.addColorStop(1, 'rgba(16,163,127,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(cx,cy,R*(1.5+u),0,Math.PI*2); ctx.fill();
  // core
  ctx.beginPath();
  ctx.arc(cx,cy,R*(0.55+bass*0.35),0,Math.PI*2);
  ctx.fillStyle = `rgba(6,78,59,${0.85})`;
  ctx.fill();
  ctx.strokeStyle = `rgba(52,211,153,${0.5+mid*0.4})`;
  ctx.lineWidth = 2;
  ctx.stroke();
  // particles
  const n = 24;
  for(let i=0;i<n;i++){
    const ang = (i/n)*Math.PI*2 + performance.now()/2000 + mid;
    const rad = R*(1.1 + treble*0.8 + (i%3)*0.12);
    ctx.beginPath();
    ctx.arc(cx+Math.cos(ang)*rad, cy+Math.sin(ang)*rad, 1.5+u*2, 0, Math.PI*2);
    ctx.fillStyle = i%2?`rgba(52,211,153,${0.4+u})`:`rgba(129,140,248,${0.35+a})`;
    ctx.fill();
  }
}
function drawSynapse(cx,cy,w,h,u,a,mid,treble){
  const nodes = 14;
  const pts = [];
  for(let i=0;i<nodes;i++){
    const ang = (i/nodes)*Math.PI*2 + performance.now()/3000;
    const rad = Math.min(w,h)*0.28*(0.7+0.3*Math.sin(i+mid*4));
    pts.push([cx+Math.cos(ang)*rad, cy+Math.sin(ang)*rad]);
  }
  ctx.lineWidth = 1;
  for(let i=0;i<nodes;i++){
    for(let j=i+1;j<nodes;j++){
      if((i+j)%3!==0) continue;
      ctx.beginPath();
      ctx.moveTo(pts[i][0], pts[i][1]);
      ctx.lineTo(pts[j][0], pts[j][1]);
      ctx.strokeStyle = `rgba(129,140,248,${0.08+a*0.25+treble*0.15})`;
      ctx.stroke();
    }
  }
  pts.forEach((p,i)=>{
    ctx.beginPath();
    ctx.arc(p[0],p[1], 2.5+u*4, 0, Math.PI*2);
    ctx.fillStyle = i%2?`rgba(52,211,153,${0.5+u})`:`rgba(167,139,250,${0.45+a})`;
    ctx.fill();
  });
}
function drawWaves(w,h,u,a,wave,mid){
  const rows = 3;
  for(let r=0;r<rows;r++){
    ctx.beginPath();
    const y0 = h*(0.35 + r*0.18);
    const col = r===0 ? `rgba(52,211,153,${0.45+u*0.4})` : `rgba(129,140,248,${0.3+a*0.4})`;
    ctx.strokeStyle = col;
    ctx.lineWidth = 1.5 + (r===0?u:a)*2;
    for(let x=0;x<w;x+=3){
      let y = y0;
      if(wave && wave.length){
        const idx = Math.floor((x/w)*wave.length);
        y += (wave[idx]-128)/128 * h * 0.12 * (1+mid);
      } else {
        y += Math.sin(x*0.02 + performance.now()/400 + r) * (8+u*20);
      }
      if(x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke();
  }
}
function drawMatrix(w,h,u,a,treble){
  const cols = 28, rows = 16;
  const cw = w/cols, rh = h/rows;
  for(let i=0;i<cols;i++){
    for(let j=0;j<rows;j++){
      const n = Math.sin(i*0.7+j*0.4+performance.now()/500) * 0.5 + 0.5;
      const v = n * (0.3 + treble*0.5 + ((i+j)%2?u:a)*0.5);
      if(v < 0.2) continue;
      ctx.fillStyle = (i+j)%2
        ? `rgba(52,211,153,${v*0.55})`
        : `rgba(129,140,248,${v*0.5})`;
      ctx.fillRect(i*cw+1, j*rh+1, cw-2, rh-2);
    }
  }
}
function drawLotus(cx,cy,w,h,u,a,bass,mid){
  const petals = 8;
  for(let i=0;i<petals;i++){
    const ang = (i/petals)*Math.PI*2 + performance.now()/4000;
    ctx.save();
    ctx.translate(cx,cy);
    ctx.rotate(ang);
    ctx.beginPath();
    const L = Math.min(w,h)*0.18*(1+bass*0.5+u*0.4);
    ctx.ellipse(0, -L*0.9, L*0.35*(1+mid*0.3), L, 0, 0, Math.PI*2);
    ctx.fillStyle = i%2
      ? `rgba(52,211,153,${0.12+u*0.25})`
      : `rgba(129,140,248,${0.1+a*0.22})`;
    ctx.fill();
    ctx.restore();
  }
  ctx.beginPath();
  ctx.arc(cx,cy, Math.min(w,h)*0.06*(1+u*0.3), 0, Math.PI*2);
  ctx.fillStyle = 'rgba(6,78,59,0.9)';
  ctx.fill();
}

async function ensureMicAnalyser(){
  if(analyser) return;
  micStream = await navigator.mediaDevices.getUserMedia({audio:true, video:false});
  audioCtx = new (window.AudioContext||window.webkitAudioContext)();
  const src = audioCtx.createMediaStreamSource(micStream);
  analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  analyser.smoothingTimeConstant = 0.75;
  src.connect(analyser);
}

function pulseAgent(level){
  agentLevel = Math.max(agentLevel, level||0.55);
  agentDecay = Math.max(agentDecay, level||0.55);
}

/* ---- Session / talk ---- */
function logLine(who, text){
  const el = document.createElement('div');
  el.className = 'm '+(who==='you'?'user':'agent');
  el.innerHTML = '<div class="who">'+(who==='you'?'You':'Agent')+'</div><div></div>';
  el.lastChild.textContent = text;
  $('log').appendChild(el);
  $('log').scrollTop = $('log').scrollHeight;
}

function personaId(){
  const p = $('persona').value;
  return VOICE_ALIAS[p] || p;
}
function systemBoost(){
  const mind = MINDSETS[$('mindset').value] || '';
  const snap = contextBuffer
    ? `\n\n[SNAPPED CODE CONTEXT path=${contextBuffer.path}]\n${contextBuffer.text.slice(0,4000)}\n[/SNAPPED]`
    : '';
  return mind + snap;
}

async function ensureSession(){
  await ensureAuth();
  if(sessionId) return sessionId;
  const j = await api('/v1/sessions',{method:'POST',body:JSON.stringify({
    mode:'voice',
    title:'Voice Studio · '+($('persona').selectedOptions[0].textContent||'Aria'),
    device:{kind:'voice-studio', label:'Voice Studio', remote:false},
    meta:{
      studio:true,
      persona: $('persona').value,
      mindset: $('mindset').value,
      visualizer: style,
      fusion: true
    }
  })});
  sessionId = j.id || j.session_id;
  return sessionId;
}

async function runTurn(text){
  const t0 = performance.now();
  $('liveChip').textContent = 'thinking';
  await ensureSession();
  // Fusion pre-route
  try{
    const f = await api('/v1/fusion/voice',{method:'POST',body:JSON.stringify({
      text,
      stress: talking ? 0.45 : 0.3,
      expert: $('expert').value,
      scenario: $('scenario').value,
      session_id: 'studio-'+(sessionId||'x'),
      industry: $('mindset').value==='travel_dfw' ? 'dfw_airline_hospitality' : 'general',
      context_buffer: contextBuffer ? {code:{path:contextBuffer.path, preview:contextBuffer.text.slice(0,200)}} : {}
    })});
    $('fusionChip').textContent = (f.primary_expert||'?')+(f.pattern?(' · '+f.pattern):'');
    $('fusionOut').textContent = (f.prompt_boost||'Fusion ok')+' · patience +'+(f.patience_delta_ms||0)+'ms · weights '+JSON.stringify(f.expert_weights||{}).slice(0,120);
    if(f.listening && f.listening.expert) $('expert').value = f.listening.expert;
  }catch(e){
    $('fusionOut').textContent = 'Fusion offline: '+(e.message||e);
  }
  const payload = {
    text: systemBoost() ? (text + '\n\n'+systemBoost()) : text,
    device:{kind:'voice-studio',label:'Voice Studio'},
    meta:{
      studio:true,
      persona: personaId(),
      mindset: $('mindset').value,
      snapped: !!contextBuffer,
      visualizer: style
    }
  };
  await api('/v1/sessions/'+sessionId+'/messages',{method:'POST',body:JSON.stringify(payload)});
  // poll
  let reply = '';
  for(let i=0;i<40;i++){
    await new Promise(r=>setTimeout(r, 450));
    const s = await api('/v1/sessions/'+sessionId);
    const msgs = s.messages||[];
    const last = msgs[msgs.length-1];
    if(last && (last.status==='done'||last.status==='failed') && (last.result||last.error)){
      reply = String(last.result||last.error||'');
      break;
    }
    if(last && (last.status==='running'||last.status==='queued')) pulseAgent(0.25+Math.random()*0.2);
  }
  const rtt = Math.round(performance.now()-t0);
  $('tRtt').textContent = String(rtt);
  $('liveChip').textContent = talking ? 'listening' : 'ready';
  // strip tts fence for display/speak
  let spoken = reply;
  const m = reply.match(/```tts[\s\S]*?\n([\s\S]*?)```/i);
  if(m) spoken = m[1].trim();
  spoken = spoken.replace(/_Fusion[^\n]*/g,'').replace(/```[\s\S]*?```/g,'').trim();
  logLine('agent', spoken.slice(0,2000) || reply.slice(0,500));
  speak(spoken.slice(0,500));
  return reply;
}

function speak(text){
  if(!text || !window.speechSynthesis) return;
  try{ speechSynthesis.cancel(); }catch(_){}
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 0.94; u.pitch = 1.05;
  u.onstart = ()=>{ pulseAgent(0.7); lastSpeakAt = performance.now(); };
  u.onboundary = ()=>{ pulseAgent(0.55 + Math.random()*0.25); };
  u.onend = ()=>{ agentDecay = 0.2; };
  speechSynthesis.speak(u);
}

async function sendText(){
  const text = ($('input').value||'').trim();
  if(!text) return;
  $('input').value = '';
  logLine('you', text);
  userLevel = 0.4;
  try{ await runTurn(text); }
  catch(e){ logLine('agent', 'Error: '+(e.message||e)); $('liveChip').textContent='error'; }
}

function toggleTalk(){
  if(talking){ stopTalk(); return; }
  startTalk();
}
async function startTalk(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ alert('Speech recognition not available — use Send text'); return; }
  try{ await ensureMicAnalyser(); }catch(e){ alert('Mic: '+(e.message||e)); return; }
  talking = true;
  $('btnTalk').textContent = '■ Stop mic';
  $('btnStop').disabled = false;
  $('liveChip').textContent = 'listening';
  $('liveChip').classList.add('on');
  recog = new SR();
  recog.lang = 'en-US';
  recog.interimResults = true;
  recog.continuous = false;
  recog.onresult = async (ev)=>{
    let interim='', final='';
    for(let i=ev.resultIndex;i<ev.results.length;i++){
      const t = ev.results[i][0].transcript;
      if(ev.results[i].isFinal) final += t; else interim += t;
    }
    if(interim){ $('input').value = interim; userLevel = Math.max(userLevel, 0.45); }
    if(final){
      $('input').value = final.trim();
      userLevel = 0.7;
      logLine('you', final.trim());
      $('input').value = '';
      try{ await runTurn(final.trim()); }catch(e){ logLine('agent', e.message||String(e)); }
      if(talking){ try{ recog.start(); }catch(_){ } }
    }
  };
  recog.onerror = ()=>{ if(talking) setTimeout(()=>{ try{recog.start();}catch(_){} }, 400); };
  recog.onend = ()=>{ if(talking) setTimeout(()=>{ try{recog.start();}catch(_){} }, 250); };
  try{ recog.start(); }catch(e){ alert(e.message); talking=false; }
}
function stopTalk(){
  talking = false;
  try{ if(recog) recog.stop(); }catch(_){}
  $('btnTalk').textContent = '🎙 Talk';
  $('liveChip').textContent = 'ready';
}
function stopAll(){
  stopTalk();
  try{ speechSynthesis.cancel(); }catch(_){}
  agentDecay = 0;
  $('btnStop').disabled = true;
}

function snapContext(){
  const text = ($('codeSnap').value||'').trim();
  const path = ($('codePath').value||'buffer').trim();
  if(!text){ alert('Nothing to snap'); return; }
  // AST-lite: line count, exports, function names
  const lines = text.split(/\n/).length;
  const fns = [...text.matchAll(/function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(/g)].map(m=>m[1]||m[2]).filter(Boolean);
  contextBuffer = {
    path,
    text,
    lines,
    functions: fns.slice(0,20),
    snapped_at: Date.now(),
    schema: 'pocket.voice_studio.context_snap.v1'
  };
  $('snapChip').textContent = lines+' lines · armed';
  $('snapChip').classList.add('on');
  $('snapBanner').classList.add('on');
  $('snapBanner').textContent = 'Snapped '+path+' ('+lines+' lines'+(fns.length?', fns: '+fns.slice(0,5).join(', '):'')+') — next voice turn includes this buffer.';
}
function clearSnap(){
  contextBuffer = null;
  $('snapChip').textContent = 'buffer empty';
  $('snapChip').classList.remove('on');
  $('snapBanner').classList.remove('on');
}
function loadSample(){
  $('codePath').value = 'src/pocket/platform_coherence.py';
  $('codeSnap').value = [
    'def fuse_voice_turn(text: str, session_id: str = "") -> dict:',
    '    # Route multi-domain travel recovery from a single utterance.',
    '    from pocket.conversational_fusion import fuse, remember',
    '    r = fuse({"text": text, "session_id": session_id, "stress": 0.55})',
    '    if session_id:',
    '        remember(session_id, r)',
    '    return r',
    ''
  ].join('\\n');
}

$('input').addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendText(); }
});

(async function boot(){
  drawFrame();
  try{
    const me = await fetch('/v1/auth/me',{headers:authHeaders()}).then(r=>r.json());
    if(me && me.user){ $('authBtn').textContent='Signed in'; $('liveChip').textContent='ready'; $('liveChip').classList.add('on'); }
  }catch(_){}
})();
</script>
</body>
</html>
"""


def voice_studio_html() -> str:
    return VOICE_STUDIO_HTML
