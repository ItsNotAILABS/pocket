"""PhoneAI public website — intro before the kernel OS."""

from __future__ import annotations

from pocket import COMPANY, LAB, __version__


def landing_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>PhoneAI — the phone that lives on your computer</title>
<meta name="description" content="PhoneAI is a phone kernel with its own seat. Chat, Portal, Antigravity, glasses HUD — running on the POCKET host you own."/>
<meta name="theme-color" content="#05060a"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-title" content="PhoneAI"/>
<link rel="manifest" href="/phoneai/manifest.json"/>
<style>
:root{{--bg:#05060a;--ink:#f7f7f4;--muted:#9a9aa6;--line:rgba(255,255,255,.1);--g:#00ff86;--g2:#00c96a;--panel:#101018;--card:#14141c}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}}
body{{min-height:100vh;background:
  radial-gradient(900px 480px at 88% -10%,rgba(0,255,134,.16),transparent 55%),
  radial-gradient(700px 380px at -10% 110%,rgba(88,166,255,.08),transparent 50%),
  var(--bg)}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 22px}}
nav{{display:flex;align-items:center;justify-content:space-between;padding:18px 0;gap:12px}}
.mark{{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:-.04em}}
.mark i{{width:28px;height:28px;border-radius:9px;background:var(--g);color:#042;display:grid;place-items:center;font-style:normal;font-size:13px}}
.nav-a{{display:flex;gap:8px;flex-wrap:wrap}}
.ghost,.cta{{display:inline-flex;align-items:center;justify-content:center;padding:10px 16px;border-radius:999px;font-weight:700;font-size:13px}}
.ghost{{border:1px solid var(--line);color:var(--ink)}}
.ghost:hover{{background:rgba(255,255,255,.05)}}
.cta{{background:var(--g);color:#042}}
.cta:hover{{background:var(--g2)}}
.hero{{padding:48px 0 36px}}
.kicker{{font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--g);margin:0 0 14px}}
h1{{font-size:clamp(36px,7vw,64px);line-height:.98;letter-spacing:-.055em;margin:0 0 16px;max-width:14ch}}
.lead{{font-size:18px;line-height:1.5;color:var(--muted);max-width:36em;margin:0 0 28px}}
.row{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px}}
.live{{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted)}}
.live b{{width:8px;height:8px;border-radius:50%;background:#555;display:inline-block}}
.live.on b{{background:var(--g);box-shadow:0 0 10px var(--g)}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:8px 0 48px}}
.card{{background:linear-gradient(180deg,rgba(255,255,255,.04),transparent 40%),var(--card);border:1px solid var(--line);border-radius:18px;padding:20px 18px;min-height:160px}}
.card h3{{margin:0 0 8px;font-size:16px;letter-spacing:-.03em}}
.card p{{margin:0;color:var(--muted);font-size:13.5px;line-height:1.45}}
.tag{{font-size:10px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--g);margin-bottom:10px}}
.band{{border-top:1px solid var(--line);padding:48px 0}}
.band h2{{font-size:28px;letter-spacing:-.04em;margin:0 0 8px}}
.band .sub{{color:var(--muted);margin:0 0 22px;max-width:40em}}
ol.flow{{margin:0;padding:0;list-style:none;display:grid;gap:10px}}
ol.flow li{{border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:var(--panel)}}
ol.flow strong{{display:block;margin-bottom:4px}}
ol.flow span{{color:var(--muted);font-size:13.5px}}
.foot{{border-top:1px solid var(--line);padding:22px 0 40px;display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;color:var(--muted);font-size:12px}}
.foot a{{color:var(--muted)}}
.foot a:hover{{color:var(--ink)}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr}}.hero{{padding-top:28px}}h1{{font-size:40px}}}}
</style>
</head>
<body>
<div class="wrap">
  <nav>
    <div class="mark"><i>P</i> PhoneAI</div>
    <div class="nav-a">
      <a class="ghost" href="/setup">Setup</a>
      <a class="ghost" href="/signup">Sign up</a>
      <a class="ghost" href="/desk">POCKET</a>
      <a class="cta" href="/phoneai/app">Enter PhoneAI</a>
    </div>
  </nav>

  <section class="hero">
    <p class="kicker">{LAB}</p>
    <h1>A phone kernel. On the machine you already own.</h1>
    <p class="lead">PhoneAI is not a chat widget. It is a phone seat — chat, camera, Portal to your PC, Antigravity as its own desktop stream, glasses HUD, and agents that can see the screen and bring the host up themselves.</p>
    <div class="row">
      <a class="cta" href="/phoneai/app">Enter the phone</a>
      <a class="ghost" href="/setup">Full installation</a>
      <a class="ghost" href="/signup">Create a seat</a>
    </div>
    <div class="live" id="live"><b></b> Checking host…</div>
  </section>

  <div class="grid">
    <article class="card"><div class="tag">Seat</div><h3>Own kernel</h3><p>PhoneAI has its own user, not a guest tab on the desk. Sign in once. The phone keeps working.</p></article>
    <article class="card"><div class="tag">Portal</div><h3>Watch + touch the PC</h3><p>One primary screen. Tap, long-press, two-finger scroll. LAN-only touch. No recursive stream of the stream.</p></article>
    <article class="card"><div class="tag">Anti</div><h3>Antigravity attached</h3><p>A separate desktop-app surface. HWND stream of the real window, not a fake iframe.</p></article>
    <article class="card"><div class="tag">Eyes</div><h3>Agents can see</h3><p>Same frames Pocket agents use. Voice to screen: click a name, scroll, open a URL.</p></article>
    <article class="card"><div class="tag">Always on</div><h3>Host stays up</h3><p>Runtime watchdog lives in the product. PhoneAI and Pocket agents can bring :8787 back themselves.</p></article>
    <article class="card"><div class="tag">Setup</div><h3>Install once</h3><p>Account, host, always-on task, then open the phone. One flow. Tunnel this page.</p></article>
  </div>

  <section class="band">
    <h2>How you actually use it</h2>
    <p class="sub">This page is the intro. The app is the kernel. Tunnel the intro; bookmark the phone.</p>
    <ol class="flow">
      <li><strong>1 · Create a seat</strong><span>Username and password on this host. PhoneAI is a market seat, separate from the owner desk.</span></li>
      <li><strong>2 · Keep the PC awake</strong><span>Install always-on so the host restarts if serve dies. Agents call <code>runtime_ensure</code>.</span></li>
      <li><strong>3 · Open the phone</strong><span>Enter PhoneAI. Chat, Portal, Anti, glasses, live web — all on this computer.</span></li>
    </ol>
    <div class="row" style="margin-top:22px">
      <a class="cta" href="/phoneai/app">Enter PhoneAI</a>
      <a class="ghost" href="/phoneai/portal">Portal</a>
      <a class="ghost" href="/phoneai/anti">Antigravity</a>
      <a class="ghost" href="/phoneai/glasses">Glasses HUD</a>
    </div>
  </section>

  <footer class="foot">
    <div>{COMPANY} · {LAB} · v{__version__}</div>
    <div>
      <a href="/">POCKET</a>
      · <a href="/setup">Setup</a>
      · <a href="/install">Install</a>
      · <a href="/signup">Sign up</a>
      · <a href="/claims">Claims</a>
    </div>
  </footer>
</div>
<script>
(async()=>{{
  const el=document.getElementById('live');
  try{{
    const r=await fetch('/v1/runtime',{{cache:'no-store'}});
    const j=await r.json();
    el.classList.toggle('on', !!j.up);
    el.lastChild.textContent = j.up
      ? (' Host up'+(j.always_on?' · always-on':'')+' · tunnel this URL')
      : ' Host down — open Setup to bring it up';
  }}catch(_){{
    el.lastChild.textContent=' Host unreachable — keep the PC awake';
  }}
}})();
</script>
</body>
</html>
"""


def runtime_html() -> str:
    return """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>PhoneAI runtime</title>
<meta name="theme-color" content="#05060a"/>
<style>
:root{--bg:#05060a;--fg:#f4f4f5;--muted:#8b8b98;--line:rgba(255,255,255,.1);--g:#00ff86}
body{margin:0;background:var(--bg);color:var(--fg);font-family:ui-sans-serif,system-ui,sans-serif;max-width:480px;margin:0 auto;padding:18px}
h1{letter-spacing:-.04em;margin:8px 0}
.muted{color:var(--muted)}
.item{border:1px solid var(--line);border-radius:14px;padding:14px;margin:10px 0}
.item b{display:block}
.go{border:0;border-radius:12px;background:var(--g);color:#042;font-weight:800;padding:12px 16px;margin:6px 6px 0 0}
a{color:#58a6ff}
</style></head>
<body>
<p><a href="/phoneai">Landing</a> · <a href="/phoneai/app">Phone</a> · <a href="/setup">Setup</a></p>
<h1>Runtime</h1>
<p class="muted">Servers that stay in Pocket and PhoneAI. Agents can bring them up.</p>
<div id="box">Loading…</div>
<button class="go" id="up">Bring host up</button>
<button class="go" id="ins" style="background:#222;color:#fff">Install always-on</button>
<script>
async function draw(){
  const j=await fetch('/v1/runtime').then(r=>r.json());
  document.getElementById('box').innerHTML=(j.servers||[]).map(s=>
    '<div class="item"><b>'+s.name+'</b><small class="muted">'+(s.up?'up':'down')+' · '+s.kind+'</small><div class="muted">'+(s.note||s.how||'')+'</div></div>'
  ).join('');
}
draw().catch(()=>{ document.getElementById('box').textContent='Host down'; });
document.getElementById('up').onclick=async()=>{
  await fetch('/v1/runtime/ensure',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"which":"all"}'});
  draw();
};
document.getElementById('ins').onclick=async()=>{
  await fetch('/v1/runtime/install',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
  draw();
};
</script>
</body></html>
"""
