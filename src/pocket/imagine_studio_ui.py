"""Imagine Studio UI — device stills + fusion remake (real host APIs)."""

from __future__ import annotations


def imagine_studio_html() -> str:
    return IMAGINE_HTML


IMAGINE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#050508"/>
<title>POCKET · Imagine Studio</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#09090b;--panel:#121214;--panel2:#18181c;--line:rgba(255,255,255,.08);
  --text:#fafafa;--muted:#a1a1aa;--accent:#34d399;--accent2:#10b981;--violet:#a78bfa;
  --red:#f87171;--amber:#fbbf24;
  --font:ui-sans-serif,system-ui,"Segoe UI",sans-serif;
  --shadow:0 16px 48px rgba(0,0,0,.45);
  --ease:cubic-bezier(.22,1,.36,1);
}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;}
body{font-family:var(--font);background:
  radial-gradient(900px 500px at 0% 0%,rgba(52,211,153,.08),transparent 50%),
  radial-gradient(800px 400px at 100% 0%,rgba(167,139,250,.08),transparent 45%),
  var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.pnav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line);background:rgba(0,0,0,.72);position:sticky;top:0;z-index:30;backdrop-filter:blur(22px) saturate(1.3)}
.pnav .brand{display:flex;align-items:center;gap:10px;font-weight:600;letter-spacing:-.03em;font-size:14px;color:#f5f5f5;text-decoration:none;margin-right:8px}
.pnav .brand i{width:22px;height:22px;border-radius:6px;background:#10a37f;display:grid;place-items:center;font-size:11px;font-weight:800;color:#041;font-style:normal}
.pnav .links{display:flex;gap:2px;flex-wrap:wrap}
.pnav .links a{color:#8e8e8e;text-decoration:none;font-size:13px;font-weight:500;padding:7px 12px;border-radius:8px}
.pnav .links a:hover{color:#ececec;background:#111}
.pnav .links a.on{color:#f5f5f5;background:#161616}
.pnav .sp{flex:1}
.pnav .pill{font-size:11px;color:#8e8e8e;border:1px solid var(--line);padding:5px 10px;border-radius:999px}
.pnav .back{font-size:13px;font-weight:600;color:#e4e4e7;background:transparent;border:1px solid rgba(255,255,255,.12);padding:7px 12px;border-radius:8px;cursor:pointer}
.pnav .back:hover{background:#111}
main{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:18px;padding:18px 16px 48px;max-width:1280px;margin:0 auto}
@media(max-width:900px){main{grid-template-columns:1fr;padding:12px 12px 96px}}
.card{background:linear-gradient(180deg,rgba(255,255,255,.035),transparent),var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px;box-shadow:var(--shadow)}
.card h2{margin:0 0 10px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.hero{border-color:rgba(52,211,153,.28);background:linear-gradient(145deg,rgba(16,163,127,.08),transparent 55%),var(--panel);margin-bottom:16px}
.hero h1{margin:0 0 6px;font-size:22px;letter-spacing:-.04em}
.hero p{margin:0;font-size:13px;color:var(--muted);line-height:1.55}
.badge{font-size:10px;font-weight:700;padding:3px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
.badge.on{color:#86efac;border-color:#14532d;background:#052e16}
.badge.warn{color:#fde68a;border-color:#854d0e;background:#1c1408}
.badge.err{color:#fecaca;border-color:#7f1d1d;background:#1c0a0a}
.presets{display:grid;gap:8px}
.preset{border:1px solid var(--line);border-radius:12px;padding:12px;cursor:pointer;background:transparent;text-align:left;color:inherit;width:100%}
.preset:hover,.preset.on{border-color:var(--accent);background:rgba(52,211,153,.06)}
.preset b{display:block;font-size:13px}
.preset small{color:var(--muted);font-size:11px;line-height:1.4}
label{display:block;font-size:11px;color:var(--muted);margin:10px 0 4px;font-weight:650}
input,textarea,select{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:#0c0c0e;color:var(--text);font:inherit}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:10px;padding:12px 16px;font-weight:750;cursor:pointer;font-size:13px;font-family:inherit}
.btn.primary{background:linear-gradient(180deg,#34d399,#10b981);color:#052e16;width:100%;margin-top:12px;box-shadow:0 4px 20px rgba(16,185,129,.3)}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text);width:100%;margin-top:8px}
.btn:disabled{opacity:.45;cursor:not-allowed}
.row{display:flex;flex-wrap:wrap;gap:8px}
.row .btn{width:auto;margin:0}
.preview{min-height:280px;border-radius:14px;border:1px dashed var(--line);background:#050506;display:grid;place-items:center;overflow:hidden;position:relative}
.preview img{max-width:100%;max-height:min(70vh,720px);object-fit:contain;display:block}
.empty{padding:28px 18px;text-align:center;color:var(--muted);max-width:420px}
.empty h3{margin:0 0 8px;color:var(--text);font-size:16px}
.empty p{margin:0;font-size:13px;line-height:1.5}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
.gitem{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#0c0c0e;cursor:pointer;text-decoration:none;color:inherit;display:flex;flex-direction:column}
.gitem:hover{border-color:rgba(52,211,153,.4)}
.gitem img{width:100%;height:120px;object-fit:cover;background:#050506}
.gitem span{font-size:10px;color:var(--muted);padding:6px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.notice{font-size:12px;color:var(--muted);line-height:1.5;padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:rgba(167,139,250,.06);margin:10px 0}
.errbox{display:none;margin-top:10px;padding:10px 12px;border-radius:12px;border:1px solid rgba(248,113,113,.4);background:rgba(127,29,29,.2);color:#fecaca;font-size:13px;line-height:1.45}
.errbox.show{display:block}
.log{font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;max-height:180px;overflow:auto;background:#050506;border-radius:10px;padding:12px;color:#86efac;border:1px solid var(--line)}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#18181b;border:1px solid var(--line);padding:10px 16px;border-radius:10px;display:none;z-index:99;font-size:13px;max-width:90vw}
.toast.show{display:block}
.toast.err{border-color:rgba(248,113,113,.45)}
.filepick{font-size:12px;color:var(--muted)}
.sticky-actions{display:none}
@media(max-width:900px){
  .sticky-actions{display:flex;position:fixed;bottom:0;left:0;right:0;gap:8px;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(9,9,11,.92);border-top:1px solid var(--line);z-index:40;backdrop-filter:blur(16px)}
  .sticky-actions .btn{flex:1;margin:0}
  .pnav .links a{padding:7px 8px;font-size:12px}
}
</style>
</head>
<body>
<header class="pnav">
  <button type="button" class="back" onclick="goBack()">← Desk</button>
  <a class="brand" href="/desk"><i>P</i>Imagine</a>
  <nav class="links" aria-label="Product">
    <a href="/desk">Desk</a>
    <a href="/studio">Product Studio</a>
    <a class="on" href="/imagine">Imagine</a>
    <a href="/studio/create">Creative</a>
    <a href="/phone">Phone</a>
    <a href="/login">Sign in</a>
    <a href="/signup">Sign up</a>
  </nav>
  <div class="sp"></div>
  <span class="badge" id="countBadge">— stills</span>
  <span class="pill" id="authPill">auth…</span>
</header>
<main>
  <section>
    <div class="card hero">
      <div class="row" style="margin-bottom:10px">
        <span class="badge on">letterbox glass</span>
        <span class="badge" id="srcBadge">source: host screen</span>
      </div>
      <h1>Imagine Studio</h1>
      <p>Compose a real host screenshot into Rotato-style phone glass, a MacBook frame, or a clean still. Fusion remake rebuilds the last understood page as HTML — not a fake picture generator.</p>
      <div class="notice">No DALL·E path here. Compose uses <code>POST /v1/imagine/compose</code>. Remake uses <code>POST /v1/fusion/remake</code>.</div>
    </div>
    <div class="card" style="margin-bottom:16px">
      <h2>Preview</h2>
      <div class="preview" id="preview">
        <div class="empty" id="emptyPreview">
          <h3>Nothing composed yet</h3>
          <p>Pick a mode, then Compose live screen — or upload a PNG. Phone and laptop frames contain the UI; they never stretch-crop it.</p>
        </div>
      </div>
      <div class="errbox" id="errbox"></div>
    </div>
    <div class="card">
      <h2>Gallery</h2>
      <div id="gallery"><div class="empty"><p>Loading stills…</p></div></div>
      <button class="btn ghost" type="button" onclick="loadGallery()">Refresh gallery</button>
    </div>
    <div class="card" style="margin-top:16px">
      <h2>Fusion remakes</h2>
      <div id="remakes"><div class="empty"><p>Loading remakes…</p></div></div>
    </div>
  </section>
  <aside>
    <div class="card">
      <h2>Compose</h2>
      <div class="presets" id="presets"></div>
      <label>Title</label>
      <input id="title" value="POCKET"/>
      <label>Subtitle</label>
      <input id="subtitle" value="Host co-pilot"/>
      <label>Source</label>
      <select id="source">
        <option value="live">Live host screenshot</option>
        <option value="last">Last vision frame on disk</option>
        <option value="novae">Latest Novae workspace PNG</option>
      </select>
      <label>Or upload PNG / JPG</label>
      <input class="filepick" id="file" type="file" accept="image/png,image/jpeg,image/webp"/>
      <button class="btn primary" id="btnCompose" type="button" onclick="doCompose()">Compose still</button>
      <button class="btn ghost" type="button" onclick="doRemake()">Fusion remake last page</button>
      <div class="row" style="margin-top:8px">
        <button class="btn ghost" type="button" onclick="seatNovae()">Seat Grok Novae</button>
        <button class="btn ghost" type="button" onclick="downloadLast()">Download still</button>
      </div>
      <button class="btn ghost" type="button" onclick="openProduct()">Product Studio (video)</button>
    </div>
    <div class="card" style="margin-top:16px">
      <h2>Job</h2>
      <div class="log" id="log">Ready. Compose uses the host screen.</div>
    </div>
  </aside>
</main>
<div class="sticky-actions">
  <button class="btn primary" type="button" onclick="doCompose()">Compose</button>
  <button class="btn ghost" type="button" onclick="doRemake()">Remake</button>
</div>
<div class="toast" id="toast"></div>
<script>
const auth = {
  user: sessionStorage.getItem('pocket_user') || localStorage.getItem('pocket_user') || '',
  pass: sessionStorage.getItem('pocket_pass') || localStorage.getItem('pocket_pass') || '',
  token: sessionStorage.getItem('pocket_token') || localStorage.getItem('pocket_token') || '',
};
let mode = 'rotato_phone';
let modes = [];
let lastUrl = '';
let pendingB64 = '';
let pendingName = '';

function storeAuth(user, token){
  auth.user = user || auth.user || 'pocket';
  auth.token = token || '';
  sessionStorage.setItem('pocket_user', auth.user);
  sessionStorage.setItem('pocket_token', auth.token);
  localStorage.setItem('pocket_user', auth.user);
  localStorage.setItem('pocket_token', auth.token);
  const pill = document.getElementById('authPill');
  paintAuthPill();
}
function paintAuthPill(){
  const pill = document.getElementById('authPill');
  if (!pill) return;
  if (auth.token) {
    pill.textContent = auth.user || 'signed in';
    pill.classList.add('on');
  } else {
    pill.innerHTML = '<a href="/login" style="color:#86efac">Sign in</a> · <a href="/signup" style="color:#86efac">Sign up</a>';
  }
}
function headers(){
  const h = {'Content-Type':'application/json'};
  if (auth.token) h['Authorization'] = 'Bearer ' + auth.token;
  else if (auth.user && auth.pass) h['Authorization'] = 'Basic ' + btoa(auth.user + ':' + auth.pass);
  if (auth.pass) h['X-Pocket-Access'] = auth.pass;
  return h;
}
async function ensureDesktopAuth(force){
  // Phone / LAN: generate stills without a password prompt.
  var host = location.hostname || '';
  var phoneish = host === '127.0.0.1' || host === 'localhost' || /^(192\.168\.|10\.|172\.)/.test(host) || /phoneai/i.test(location.pathname+location.hash);
  if (phoneish) {
    try {
      const r = await fetch('/v1/auth/desktop', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'});
      if (r.ok) {
        const j = await r.json();
        if (j.ok && j.token) storeAuth((j.user && j.user.user) || 'pocket', j.token);
      }
    } catch(_){}
    return true;
  }
  if (!force) {
    if (!sessionStorage.getItem('pocket_token') && localStorage.getItem('pocket_token')) {
      sessionStorage.setItem('pocket_token', localStorage.getItem('pocket_token'));
      sessionStorage.setItem('pocket_user', localStorage.getItem('pocket_user') || 'pocket');
      auth.token = sessionStorage.getItem('pocket_token');
      auth.user = sessionStorage.getItem('pocket_user') || 'pocket';
    }
    if (auth.token) {
      try {
        const r = await fetch('/v1/auth/me', {method:'POST', headers: headers(), body:'{}'});
        if (r.ok) {
          const j = await r.json();
          if (j && j.user) storeAuth((j.user.user || j.user.display || auth.user), auth.token);
          return true;
        }
      } catch(_){}
    }
  }
  const host = location.hostname;
  if (host === '127.0.0.1' || host === 'localhost') {
    try {
      const r = await fetch('/v1/auth/desktop', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'});
      if (r.ok) {
        const j = await r.json();
        if (j.ok && j.token) { storeAuth((j.user && j.user.user) || 'pocket', j.token); return true; }
      }
    } catch(_) {}
  }
  if (auth.token) return true;
  if (window.PocketAuth) {
    return new Promise(function(resolve){
      PocketAuth.showPasswordGate({
        device: 'imagine-studio',
        onSuccess: function(res){
          storeAuth((res.user && res.user.user) || 'pocket', res.token || PocketAuth.getToken());
          resolve(true);
        }
      });
    });
  }
  return false;
}
async function api(path, opt={}){
  const r = await fetch(path, {...opt, headers:{...headers(), ...(opt.headers||{})}});
  if (r.status === 401) {
    const ok = await ensureDesktopAuth(true);
    if (ok) {
      const r2 = await fetch(path, {...opt, headers:{...headers(), ...(opt.headers||{})}});
      const j2 = await r2.json().catch(()=>({}));
      if (!r2.ok) throw new Error(j2.error || j2.hint || r2.statusText);
      return j2;
    }
    location.href = '/login?next=/imagine';
    throw new Error('Sign in or create an account to compose.');
  }
  const j = await r.json().catch(()=>({}));
  if (!r.ok) throw new Error(j.error || j.hint || r.statusText || 'request failed');
  return j;
}
function toast(m, kind){
  const t=document.getElementById('toast');
  t.textContent=m;
  t.className='toast show'+(kind==='err'?' err':'');
  setTimeout(()=>t.classList.remove('show'), 2800);
}
function log(m){
  const el=document.getElementById('log');
  el.textContent = (typeof m==='string'?m:JSON.stringify(m,null,2)).slice(0,8000);
}
function showErr(m){
  const el=document.getElementById('errbox');
  if(!m){ el.classList.remove('show'); el.textContent=''; return; }
  el.textContent=m;
  el.classList.add('show');
}
function goBack(){
  try{
    if (history.length > 1 && document.referrer && document.referrer.indexOf(location.origin) === 0) {
      history.back(); return;
    }
  }catch(_){}
  location.href = '/desk';
}
function openProduct(){ location.href='/studio'; }
async function seatNovae(){
  log('Seating Grok Novae in POCKET…');
  try{
    const j = await api('/v1/novae/activate', {method:'POST', body: JSON.stringify({id:'GROK_NOVAE', goal:'Imagine Studio compose'})});
    log(j);
    toast(j.title ? (j.title+' seated') : (j.ok ? 'Novae seated' : (j.error||'Novae failed')), j.ok?undefined:'err');
  }catch(e){
    showErr(String(e.message||e));
    toast(String(e.message||e),'err');
  }
}
function downloadLast(){
  if(!lastUrl){ toast('Compose a still first','err'); return; }
  const a=document.createElement('a');
  a.href=lastUrl;
  a.download='imagine-still.png';
  a.click();
}

function renderPresets(){
  const box = document.getElementById('presets');
  const arr = modes.length ? modes : [
    {id:'rotato_phone', label:'Rotato phone', desc:'9:16 letterboxed glass'},
    {id:'macbook_web', label:'MacBook web', desc:'16:9 laptop + chrome'},
    {id:'clean', label:'Clean still', desc:'No fake device'}
  ];
  box.innerHTML = arr.map(p=>`
    <button type="button" class="preset ${mode===p.id?'on':''}" data-id="${p.id}">
      <b>${p.label||p.id}</b><small>${p.desc||''}</small>
    </button>`).join('');
  box.querySelectorAll('.preset').forEach(btn=>{
    btn.onclick=()=>{ mode=btn.dataset.id; renderPresets(); };
  });
}

function setPreview(url){
  lastUrl = url;
  const box = document.getElementById('preview');
  if(!url){
    box.innerHTML = `<div class="empty" id="emptyPreview">
      <h3>Nothing composed yet</h3>
      <p>Pick a mode, then Compose live screen — or upload a PNG.</p>
    </div>`;
    return;
  }
  box.innerHTML = `<img alt="Imagine compose" src="${url}"/>`;
}

function renderGallery(items){
  const box = document.getElementById('gallery');
  const badge = document.getElementById('countBadge');
  if (badge) badge.textContent = (items||[]).length + ' stills';
  if (!items || !items.length){
    box.innerHTML = `<div class="empty"><h3>Gallery is empty</h3><p>Compose a phone or laptop still from the host screen. Files land in ~/.pocket/imagine/composites.</p></div>`;
    return;
  }
  box.innerHTML = '<div class="gallery">' + items.map(e=>`
    <a class="gitem" href="${e.url}" data-url="${e.url}">
      <img src="${e.url}" alt="${e.name}" loading="lazy"/>
      <span>${e.name}</span>
    </a>`).join('') + '</div>';
  box.querySelectorAll('.gitem').forEach(a=>{
    a.addEventListener('click', function(ev){
      ev.preventDefault();
      setPreview(a.getAttribute('data-url'));
    });
  });
}

function renderRemakes(items){
  const box = document.getElementById('remakes');
  if (!items || !items.length){
    box.innerHTML = `<div class="empty"><h3>No remakes yet</h3><p>Fusion remake reads OCULUS page symbols and writes HTML + 3D scene JSON. It can take a while on a dense desktop.</p></div>`;
    return;
  }
  box.innerHTML = '<ul style="margin:0;padding-left:18px;font-size:13px">' + items.map(e=>
    `<li style="margin:6px 0"><a href="${e.url}" target="_blank" rel="noopener" style="color:var(--accent)">${e.name}</a> <span style="color:var(--muted);font-size:11px">${e.kind} · ${e.size_mb} MB</span></li>`
  ).join('') + '</ul>';
}

async function loadGallery(){
  try{
    const j = await api('/v1/imagine/gallery');
    renderGallery(j.composites||[]);
    renderRemakes(j.remakes||[]);
    if ((j.composites||[])[0] && !lastUrl) setPreview((j.composites[0].url));
  }catch(e){
    document.getElementById('gallery').innerHTML = `<div class="empty"><h3>Could not load gallery</h3><p>${String(e.message||e)}</p></div>`;
    showErr(String(e.message||e));
  }
}

async function loadStatus(){
  try{
    const j = await api('/v1/imagine');
    log(j.note || 'Imagine Studio ready.');
    const m = await api('/v1/imagine/modes');
    modes = m.modes || [];
    renderPresets();
  }catch(e){
    log(String(e.message||e));
    renderPresets();
  }
}

document.getElementById('file').addEventListener('change', function(){
  const f = this.files && this.files[0];
  if(!f){ pendingB64=''; pendingName=''; return; }
  const reader = new FileReader();
  reader.onload = ()=>{ pendingB64 = String(reader.result||''); pendingName = f.name; toast('Upload ready: '+f.name); };
  reader.readAsDataURL(f);
});

async function doCompose(){
  const btn = document.getElementById('btnCompose');
  btn.disabled = true;
  showErr('');
  log('Composing '+mode+'…');
  const srcBadge = document.getElementById('srcBadge');
  try{
    const body = {
      mode,
      title: document.getElementById('title').value || 'POCKET',
      subtitle: document.getElementById('subtitle').value || 'Host co-pilot',
      source: document.getElementById('source').value || 'live',
    };
    if (pendingB64){ body.image_b64 = pendingB64; body.filename = pendingName; }
    const j = await api('/v1/imagine/compose', {method:'POST', body: JSON.stringify(body)});
    if (!j.ok){
      showErr((j.error||'Compose failed') + (j.hint? '\n'+j.hint : ''));
      log(j);
      toast(j.error||'Compose failed','err');
      return;
    }
    if (srcBadge) srcBadge.textContent = 'source: '+(j.source_kind||'host');
    if (j.file_url) setPreview(j.file_url);
    log(j);
    toast(j.message||'Composed');
    pendingB64=''; pendingName='';
    document.getElementById('file').value='';
    loadGallery();
  }catch(e){
    showErr(String(e.message||e));
    log(String(e));
    toast(String(e.message||e),'err');
  }finally{
    btn.disabled = false;
  }
}

async function doRemake(){
  showErr('');
  log('Fusion remake… this can take a minute on a dense desktop.');
  toast('Remake started');
  try{
    const j = await api('/v1/fusion/remake', {method:'POST', body: JSON.stringify({refresh:true})});
    log(j);
    if (!j.ok){
      showErr(j.error || 'Remake failed');
      toast(j.error||'Remake failed','err');
      return;
    }
    toast(j.brief || 'Remake ready');
    loadGallery();
  }catch(e){
    showErr(String(e.message||e));
    log(String(e));
    toast(String(e.message||e),'err');
  }
}

(async function boot(){
  await ensureDesktopAuth(false);
  storeAuth(auth.user, auth.token);
  paintAuthPill();
  renderPresets();
  await loadStatus();
  await loadGallery();
})();
</script>
</body>
</html>
"""
