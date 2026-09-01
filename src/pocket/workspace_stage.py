"""Real Pocket workspace interior — files, editor, live preview.

Not a character. Not skeleton bars. The square pane is the workspace:
sidebar of real files, editor of the open file, preview of HTML/output.
While agents build, the pane polls /v1/ai-workspace and lights the live badge.
"""

from __future__ import annotations

CSS = r"""
.ws-stage{
  --ws-line:rgba(255,255,255,.1);
  position:relative;margin:8px 10px 0;aspect-ratio:1/1;width:calc(100% - 20px);
  max-height:min(48vh,420px);border-radius:12px;overflow:hidden;
  border:1px solid var(--ws-line);background:#08080d;
  display:flex;flex-direction:column;min-height:200px
}
.ws-chrome{
  flex:0 0 28px;display:flex;align-items:center;gap:8px;padding:0 10px;
  border-bottom:1px solid var(--ws-line);background:#0e0e14;z-index:2
}
.ws-dots{display:flex;gap:5px}
.ws-dots i{width:7px;height:7px;border-radius:50%;background:#3f3f46;display:block}
.ws-title{flex:1;font-size:10.5px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;color:#a1a1aa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ws-live{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#52525b}
.ws-stage.on .ws-live{color:#34d399}
.ws-body{flex:1;display:grid;grid-template-columns:28% 1fr;min-height:0;position:relative}
.ws-stage.wide .ws-body{grid-template-columns:22% 1fr 36%}
.ws-side,.ws-main,.ws-prev{min-width:0;min-height:0;overflow:auto}
.ws-side{border-right:1px solid var(--ws-line);padding:6px;font-size:10.5px;color:#a1a1aa;font-family:ui-monospace,Menlo,Consolas,monospace}
.ws-side button{
  display:block;width:100%;text-align:left;border:0;background:transparent;color:#d4d4d8;
  padding:4px 6px;border-radius:6px;font:inherit;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}
.ws-side button:hover,.ws-side button.on{background:rgba(16,163,127,.12);color:#ecfdf5}
.ws-main{display:flex;flex-direction:column}
.ws-tabs{display:flex;gap:4px;padding:4px 6px;border-bottom:1px solid var(--ws-line);overflow:auto}
.ws-tabs em{
  flex:0 0 auto;font-style:normal;font-size:10px;padding:3px 7px;border-radius:6px;
  border:1px solid var(--ws-line);color:#a1a1aa;max-width:9em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap
}
.ws-tabs em.on{color:#ecfdf5;border-color:rgba(16,163,127,.45);background:rgba(16,163,127,.1)}
.ws-code{
  flex:1;margin:0;padding:8px;overflow:auto;font:11px/1.45 ui-monospace,Menlo,Consolas,monospace;
  color:#bbf7d0;background:#07070c;white-space:pre-wrap;word-break:break-word
}
.ws-prev{border-left:1px solid var(--ws-line);background:#050508}
.ws-prev iframe,.ws-prev img{display:block;width:100%;height:100%;border:0;background:#000;object-fit:contain}
.ws-stage.cover .ws-prev img,.ws-stage.cover .ws-prev iframe{object-fit:cover}
.ws-stage.fill{aspect-ratio:auto;max-height:none;width:100%;height:100%;margin:0;border:0;border-radius:0}
.ws-stage.fill .ws-chrome,.ws-stage.fill .ws-side,.ws-stage.fill .ws-main,.ws-stage.fill .ws-scan{display:none!important}
.ws-stage.fill .ws-body{display:block;position:absolute;inset:0}
.ws-stage.fill .ws-prev{position:absolute;inset:0;border:0;height:100%;width:100%}
.ws-stage.fill .ws-prev iframe,.ws-stage.fill .ws-prev img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.ws-empty{padding:16px;color:#71717a;font-size:12px;line-height:1.45}
.ws-scan{
  pointer-events:none;position:absolute;left:0;right:0;height:14%;
  background:linear-gradient(180deg,transparent,rgba(16,163,127,.1),transparent);opacity:0
}
.ws-stage.on .ws-scan{animation:wsScan 2.8s linear infinite;opacity:1}
@keyframes wsScan{from{top:-14%}to{top:100%}}
@media (prefers-reduced-motion:reduce){.ws-stage.on .ws-scan{animation:none;opacity:0}}
"""

HTML = """
<div class="ws-stage idle" id="buildStage" aria-live="polite">
  <div class="ws-chrome">
    <span class="ws-dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="ws-title" id="buildCap">Workspace</span>
    <span class="ws-live" id="wsLive">idle</span>
  </div>
  <div class="ws-body">
    <div class="ws-side" id="wsFiles"><div class="ws-empty">No files yet</div></div>
    <div class="ws-main">
      <div class="ws-tabs" id="wsTabs"></div>
      <pre class="ws-code" id="wsCode">Open a file. Agent output lands here.</pre>
    </div>
    <div class="ws-prev" id="wsPrev" hidden></div>
    <div class="ws-scan"></div>
  </div>
</div>
"""

JS = r"""
function setBuildStage(on, label){
  const el=document.getElementById('buildStage'); if(!el) return;
  el.classList.toggle('on', !!on);
  el.classList.toggle('idle', !on);
  const cap=document.getElementById('buildCap');
  const live=document.getElementById('wsLive');
  if(cap && label) cap.textContent=label;
  if(live) live.textContent=on?'building':'idle';
  if(on) fillRealWorkspace();
}
let _wsFiles=[], _wsTimer=0;
function fillRealWorkspace(){
  const filesEl=document.getElementById('wsFiles');
  const codeEl=document.getElementById('wsCode');
  const tabsEl=document.getElementById('wsTabs');
  const prevEl=document.getElementById('wsPrev');
  const stage=document.getElementById('buildStage');
  if(!filesEl) return;
  const sid=(typeof activeId!=='undefined' && activeId)||'';
  const ws=(document.getElementById('wsSelect')&&document.getElementById('wsSelect').value)||'parallax';
  fetch('/v1/ai-workspace?workspace='+encodeURIComponent(ws)+'&session_id='+encodeURIComponent(sid),{credentials:'include'})
    .then(r=>r.json()).then(j=>{
      const index=j.index||[];
      _wsFiles=index;
      if(!index.length){
        filesEl.innerHTML='<div class="ws-empty">Workspace empty until the first job writes a file</div>';
      } else {
        filesEl.innerHTML=index.slice(0,40).map((f,i)=>'<button type="button" data-i="'+i+'">'+(f.path||f.name||'file')+'</button>').join('');
      }
      const previews=j.previews||[];
      const first=previews[0]||null;
      if(first && codeEl && !(codeEl.dataset.locked==='1')){
        codeEl.textContent=(first.preview||first.body||'').slice(0,8000) || (j.brief||'');
        if(tabsEl) tabsEl.innerHTML='<em class="on">'+(first.name||'preview')+'</em>';
      } else if(j.brief && codeEl && !codeEl.dataset.locked){
        codeEl.textContent=j.brief;
      }
      const htmlPrev=previews.find(p=>/\.html?$/i.test(p.name||'') || /<html/i.test(p.preview||''));
      if(prevEl && htmlPrev){
        prevEl.hidden=false; stage.classList.add('wide');
        let ifr=prevEl.querySelector('iframe');
        if(!ifr){ ifr=document.createElement('iframe'); ifr.setAttribute('sandbox','allow-scripts allow-same-origin'); prevEl.innerHTML=''; prevEl.appendChild(ifr); }
        ifr.srcdoc=htmlPrev.preview||'';
      }
      const cap=document.getElementById('buildCap');
      if(cap && (j.cwd||j.workspace)) cap.textContent=(j.cwd||j.workspace||'Workspace').split(/[\\/]/).slice(-2).join('/');
    }).catch(()=>{});
}
function openWsFile(i){
  const f=_wsFiles[i]; if(!f) return;
  const path=f.path||f.name||'';
  const codeEl=document.getElementById('wsCode');
  const tabsEl=document.getElementById('wsTabs');
  if(tabsEl) tabsEl.innerHTML='<em class="on">'+path.split(/[\\/]/).pop()+'</em>';
  [...document.querySelectorAll('#wsFiles button')].forEach((b,n)=>b.classList.toggle('on', n===i));
  fetch('/v1/ai-workspace/file?path='+encodeURIComponent(path),{credentials:'include'}).then(r=>r.json()).then(j=>{
    if(codeEl){ codeEl.textContent=j.text||j.preview||j.error||''; codeEl.dataset.locked='1'; }
  }).catch(()=>{ if(codeEl) codeEl.textContent=path; });
}
document.addEventListener('click', e=>{
  const b=e.target.closest && e.target.closest('#wsFiles [data-i]');
  if(!b) return;
  openWsFile(parseInt(b.getAttribute('data-i'),10));
});
function coverWorkspaceWith(url, kind){
  const stage=document.getElementById('buildStage');
  const prev=document.getElementById('wsPrev');
  if(!stage||!prev||!url) return;
  stage.classList.add('wide','cover','fill');
  prev.hidden=false;
  if(kind==='img'){
    prev.innerHTML='<img alt="PC" src="'+url+'"/>';
  } else {
    prev.innerHTML='<iframe title="workspace" src="'+url+'" allow="fullscreen"></iframe>';
  }
}
if(!_wsTimer){ _wsTimer=setInterval(fillRealWorkspace, 4000); fillRealWorkspace(); }
"""
