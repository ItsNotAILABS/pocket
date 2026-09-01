"""Production workspace stage — square pane that constructs while agents build.

This is the grok.com Build *workspace* (chrome, sidebar, editor, preview),
not a character. CSS-only; reduced-motion respected.
"""

from __future__ import annotations

CSS = r"""
.ws-stage{
  --ws-line:rgba(255,255,255,.1);
  --ws-fill:rgba(255,255,255,.06);
  position:relative;margin:8px 10px 0;aspect-ratio:1/1;width:calc(100% - 20px);
  max-height:min(42vh,360px);border-radius:12px;overflow:hidden;
  border:1px solid var(--ws-line);background:#08080d;
  display:flex;flex-direction:column;min-height:180px
}
.ws-chrome{
  flex:0 0 28px;display:flex;align-items:center;gap:8px;padding:0 10px;
  border-bottom:1px solid var(--ws-line);background:#0e0e14
}
.ws-dots{display:flex;gap:5px}
.ws-dots i{width:7px;height:7px;border-radius:50%;background:#3f3f46;display:block}
.ws-dots i:nth-child(1){background:#52525b}
.ws-title{flex:1;font-size:10.5px;font-weight:650;letter-spacing:.08em;text-transform:uppercase;color:#71717a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ws-live{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#52525b}
.ws-stage.on .ws-live{color:#34d399}
.ws-body{flex:1;display:grid;grid-template-columns:22% 1fr 28%;min-height:0;position:relative}
.ws-side,.ws-main,.ws-prev{min-width:0;min-height:0}
.ws-side{border-right:1px solid var(--ws-line);padding:8px 6px;display:flex;flex-direction:column;gap:6px}
.ws-side b{display:block;height:7px;border-radius:3px;background:var(--ws-fill);transform:scaleX(.2);transform-origin:left;opacity:.35}
.ws-stage.on .ws-side b{animation:wsBar .9s cubic-bezier(.22,1,.36,1) forwards}
.ws-stage.on .ws-side b:nth-child(1){animation-delay:.05s}
.ws-stage.on .ws-side b:nth-child(2){animation-delay:.14s;width:78%}
.ws-stage.on .ws-side b:nth-child(3){animation-delay:.22s;width:62%}
.ws-stage.on .ws-side b:nth-child(4){animation-delay:.3s;width:88%}
.ws-stage.on .ws-side b:nth-child(5){animation-delay:.38s;width:54%}
.ws-main{display:flex;flex-direction:column;border-right:1px solid var(--ws-line)}
.ws-tabs{display:flex;gap:4px;padding:6px 8px;border-bottom:1px solid var(--ws-line)}
.ws-tabs em{display:block;height:8px;width:28%;border-radius:3px;background:var(--ws-fill);opacity:.3}
.ws-stage.on .ws-tabs em{animation:wsTab .7s cubic-bezier(.22,1,.36,1) forwards}
.ws-stage.on .ws-tabs em:nth-child(1){animation-delay:.2s}
.ws-stage.on .ws-tabs em:nth-child(2){animation-delay:.32s}
.ws-stage.on .ws-tabs em:nth-child(3){animation-delay:.44s}
.ws-code{flex:1;padding:8px;display:flex;flex-direction:column;gap:5px}
.ws-code span{display:block;height:5px;border-radius:2px;background:var(--ws-fill);width:92%;transform:scaleX(0);transform-origin:left;opacity:.4}
.ws-code span:nth-child(2){width:74%}
.ws-code span:nth-child(3){width:86%}
.ws-code span:nth-child(4){width:58%}
.ws-code span:nth-child(5){width:80%}
.ws-code span:nth-child(6){width:46%}
.ws-stage.on .ws-code span{animation:wsBar .8s cubic-bezier(.22,1,.36,1) forwards}
.ws-stage.on .ws-code span:nth-child(1){animation-delay:.28s}
.ws-stage.on .ws-code span:nth-child(2){animation-delay:.38s}
.ws-stage.on .ws-code span:nth-child(3){animation-delay:.48s}
.ws-stage.on .ws-code span:nth-child(4){animation-delay:.58s}
.ws-stage.on .ws-code span:nth-child(5){animation-delay:.68s}
.ws-stage.on .ws-code span:nth-child(6){animation-delay:.78s}
.ws-prev{padding:8px}
.ws-frame{
  height:100%;border-radius:6px;border:1px solid var(--ws-line);background:
    linear-gradient(180deg,rgba(16,163,127,.08),transparent 40%),#0c0c12;
  opacity:.35
}
.ws-stage.on .ws-frame{animation:wsPrev 1.6s ease-in-out infinite;opacity:1}
.ws-scan{
  pointer-events:none;position:absolute;left:0;right:0;height:18%;
  background:linear-gradient(180deg,transparent,rgba(16,163,127,.12),transparent);
  opacity:0
}
.ws-stage.on .ws-scan{animation:wsScan 2.4s linear infinite;opacity:1}
@keyframes wsBar{from{transform:scaleX(0);opacity:.2}to{transform:scaleX(1);opacity:1}}
@keyframes wsTab{from{opacity:.2;transform:translateY(4px)}to{opacity:1;transform:none}}
@keyframes wsPrev{0%,100%{box-shadow:inset 0 0 0 1px rgba(16,163,127,.12)}50%{box-shadow:inset 0 0 24px rgba(16,163,127,.18)}}
@keyframes wsScan{from{top:-18%}to{top:100%}}
@media (prefers-reduced-motion:reduce){
  .ws-stage.on .ws-side b,.ws-stage.on .ws-code span,.ws-stage.on .ws-tabs em,.ws-stage.on .ws-frame,.ws-stage.on .ws-scan{animation:none;transform:none;opacity:1}
}
"""

HTML = """
<div class="ws-stage idle" id="buildStage" aria-live="polite">
  <div class="ws-chrome">
    <span class="ws-dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="ws-title" id="buildCap">Workspace</span>
    <span class="ws-live" id="wsLive">idle</span>
  </div>
  <div class="ws-body">
    <div class="ws-side" aria-hidden="true"><b></b><b></b><b></b><b></b><b></b></div>
    <div class="ws-main" aria-hidden="true">
      <div class="ws-tabs"><em></em><em></em><em></em></div>
      <div class="ws-code"><span></span><span></span><span></span><span></span><span></span><span></span></div>
    </div>
    <div class="ws-prev" aria-hidden="true"><div class="ws-frame"></div></div>
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
  if(cap) cap.textContent=on?(label||'Building workspace'):'Workspace';
  if(live) live.textContent=on?'building':'idle';
}
"""
