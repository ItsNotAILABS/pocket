"""IOChain WebGPU app — exact product pitch + browser GPU probe."""

from pocket.iochain import PITCH


def iochain_html() -> str:
    return HTML.replace("__PITCH__", PITCH.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;"))


HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>IOChain · WebGPU</title>
<style>
:root{--bg:#07080a;--fg:#eef2f6;--muted:#8b98a8;--line:rgba(255,255,255,.12);--g:#22d3ee}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif}
body{max-width:720px;margin:0 auto;padding:28px 18px 64px}
a{color:var(--muted)}
.eyebrow{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--g);font-weight:800}
h1{font-size:clamp(28px,5vw,44px);letter-spacing:-.04em;margin:8px 0 16px}
.pitch{font-size:18px;line-height:1.55;margin:0 0 24px}
.panel{border:1px solid var(--line);border-radius:14px;padding:16px;background:#0e1116}
.ok{color:#4ade80}.bad{color:#f87171}
pre{white-space:pre-wrap;font-size:12px;color:var(--muted)}
</style></head>
<body>
<div class="eyebrow">WebGPU · IOChain</div>
<h1>IOChain</h1>
<p class="pitch" id="pitch">__PITCH__</p>
<div class="panel">
  <b>This browser GPU</b>
  <div id="gpu">Probing WebGPU…</div>
  <pre id="info"></pre>
</div>
<p><a href="/desk">Desk</a> · <a href="/loomgraph">LOOMGRAPH</a> · <a href="/spark-group">Spark Group</a></p>
<script>
(async()=>{
  const el=document.getElementById('gpu');
  const info=document.getElementById('info');
  try{
    if(!navigator.gpu){ el.className='bad'; el.textContent='navigator.gpu unavailable — Chrome/Edge, HTTPS or localhost'; return; }
    const ad=await navigator.gpu.requestAdapter();
    if(!ad){ el.className='bad'; el.textContent='No WebGPU adapter'; return; }
    let label='adapter';
    try{ const i=await ad.requestAdapterInfo(); label=i.description||i.device||i.vendor||label; info.textContent=JSON.stringify(i,null,2); }catch(_){}
    el.className='ok'; el.textContent='WebGPU ON · '+label+' · idle capacity for IOChain inference';
  }catch(e){ el.className='bad'; el.textContent=String(e); }
})();
</script>
</body></html>
"""
