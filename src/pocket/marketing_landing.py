"""Customer marketing pages — plain product language, no lab jargon."""

from __future__ import annotations

from pocket import COMPANY, LAB, __version__
from pocket.product_shell import SHELL_CSS, shell_nav

GITHUB = "https://github.com/ItsNotAILABS/pocket"


def get_app_html() -> str:
    """Get started — how someone opens POCKET for the first time."""
    nav = shell_nav(active="start")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Get started with POCKET</title>
<meta name="description" content="Open POCKET in the browser, install the desktop app, or invite your team."/>
<meta name="theme-color" content="#09090b"/>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f;--accent2:#0d8c6c}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:radial-gradient(1000px 480px at 8% -12%,rgba(16,163,127,.1),transparent 52%),var(--bg);color:var(--text);line-height:1.55;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
{SHELL_CSS}
.wrap{{max-width:880px;margin:0 auto;padding:48px 22px 80px}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
h1{{font-size:clamp(28px,4vw,40px);letter-spacing:-.04em;margin:0 0 12px;color:var(--fg)}}
.lead{{color:var(--muted);max-width:560px;margin:0 0 32px;font-size:16px}}
.step{{border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--panel);margin-bottom:14px}}
.step h2{{margin:0 0 8px;font-size:17px;color:var(--fg);letter-spacing:-.02em}}
.step p{{margin:0 0 12px;color:var(--muted);font-size:14px}}
.step ol{{margin:0 0 12px;padding-left:18px;color:var(--muted);font-size:13.5px}}
.step li{{margin:4px 0}}
.btn{{display:inline-flex;align-items:center;padding:11px 16px;border-radius:10px;font-weight:700;font-size:13.5px;border:1px solid transparent;margin-right:8px;margin-top:4px}}
.btn-primary{{background:var(--accent);color:#041}}
.btn-primary:hover{{background:var(--accent2)}}
.btn-ghost{{border-color:var(--line);color:var(--fg)}}
.btn-ghost:hover{{background:rgba(255,255,255,.06)}}
.note{{font-size:13px;color:var(--muted);border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:#0c0c0e;margin-top:20px}}
.foot{{margin-top:36px;font-size:12px;color:var(--muted)}}
.foot a{{color:var(--muted);margin-right:12px}}
.foot a:hover{{color:var(--fg)}}
</style>
</head>
<body>
{nav}
<main class="wrap">
  <div class="eyebrow">Get started</div>
  <h1>Open POCKET in a few minutes</h1>
  <p class="lead">Pick how you work — browser, desktop window, or Windows app. Same account either way. Your files stay on this computer.</p>

  <div class="step" id="web">
    <h2>1 · Open in the browser</h2>
    <p>Sign in, then start a chat. This is the fastest way to try POCKET on a machine that already has it running.</p>
    <a class="btn btn-primary" href="/desk">Open the app</a>
    <a class="btn btn-ghost" href="/">Back to home</a>
  </div>

  <div class="step" id="edge">
    <h2>2 · Keep it as a desktop window</h2>
    <p>In Microsoft Edge: open the app → menu → Apps → <strong>Install this site as an app</strong>. It opens like a normal program from your taskbar.</p>
    <a class="btn btn-primary" href="/desk">Open app, then install</a>
  </div>

  <div class="step" id="exe">
    <h2>3 · Download for Windows</h2>
    <p>For a packaged desktop install — same workspace, same sign-in.</p>
    <a class="btn btn-primary" href="/download">Download</a>
    <a class="btn btn-ghost" href="{GITHUB}/releases" target="_blank" rel="noopener">Releases</a>
  </div>

  <div class="step" id="team">
    <h2>Invite your team</h2>
    <p>Admins send an invite. Each person creates their own username and password and works in their own space. They never use the admin password.</p>
    <a class="btn btn-ghost" href="/desk">Sign in or join with invite</a>
  </div>

  <div class="step" id="api">
    <h2>For developers</h2>
    <p>Automate with API keys — separate from day-to-day chat.</p>
    <a class="btn btn-ghost" href="/developers">Developer docs</a>
  </div>

  <div class="note">
    <strong>Every day:</strong> open the app → pick Code, Research, or Plan → type what you need.
    Share a file with another of your devices from Devices in the side panel after you sign in.
  </div>

  <div class="foot">
    <a href="/">Home</a>
    <a href="/desk">App</a>
    <a href="/updates">Updates</a>
    <a href="/download">Download</a>
    <span>v{__version__}</span>
  </div>
</main>
</body>
</html>
"""


def updates_html() -> str:
    """Product updates feed — what shipped and how to use it."""
    nav = shell_nav(active="updates")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Updates</title>
<meta name="description" content="What is new in POCKET — desk, Working board, voice, remote browser, Aether phone."/>
<meta name="theme-color" content="#09090b"/>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f;--accent2:#0d8c6c}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:radial-gradient(1000px 480px at 8% -12%,rgba(16,163,127,.1),transparent 52%),var(--bg);color:var(--text);line-height:1.55;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
{SHELL_CSS}
.wrap{{max-width:820px;margin:0 auto;padding:48px 22px 80px}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
h1{{font-size:clamp(28px,4vw,40px);letter-spacing:-.04em;margin:0 0 12px;color:var(--fg)}}
.lead{{color:var(--muted);max-width:560px;margin:0 0 36px;font-size:16px}}
.timeline{{position:relative;padding-left:0}}
.item{{
  border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--panel);margin-bottom:14px;
  transition:border-color .15s,box-shadow .15s,transform .12s
}}
.item:hover{{border-color:rgba(16,163,127,.35);box-shadow:0 0 0 1px rgba(16,163,127,.08);transform:translateY(-1px)}}
.item .when{{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}}
.item h2{{margin:0 0 8px;font-size:17px;color:var(--fg);letter-spacing:-.02em}}
.item p{{margin:0 0 10px;color:var(--muted);font-size:14px}}
.item ul{{margin:0;padding-left:18px;color:var(--muted);font-size:13.5px}}
.item li{{margin:4px 0}}
.item .actions{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.item .go{{display:inline-flex;align-items:center;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:700;background:var(--accent);color:#041}}
.item .go:hover{{background:var(--accent2)}}
.item .ghost{{display:inline-flex;align-items:center;padding:8px 14px;border-radius:8px;font-size:13px;font-weight:650;border:1px solid var(--line);color:var(--fg)}}
.item .ghost:hover{{background:rgba(255,255,255,.05)}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 28px}}
.chips span{{font-size:11.5px;color:var(--muted);border:1px solid var(--line);padding:5px 10px;border-radius:999px}}
.note{{font-size:13px;color:var(--muted);border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:#0c0c0e;margin-top:24px}}
.note code{{color:var(--fg);font-size:12px}}
.foot{{margin-top:36px;font-size:12px;color:var(--muted)}}
.foot a{{color:var(--muted);margin-right:12px}}
.foot a:hover{{color:var(--fg)}}
</style>
</head>
<body>
{nav}
<main class="wrap">
  <div class="eyebrow">Product updates</div>
  <h1>What is new in POCKET</h1>
  <p class="lead">Every tab is its own surface. Primary ops on the bar; studios under More. Each panel has actions that do real work.</p>
  <div class="chips">
    <span>Desk</span><span>Working</span><span>Habitat</span><span>Screen</span>
    <span>Remote</span><span>Phone</span><span>Platform</span><span>More → Studios</span>
  </div>

  <div class="timeline">
  <article class="item">
    <div class="when">Latest · v{__version__}</div>
    <h2>Studio · Phone · Capsules · life tools</h2>
    <p><strong>POCKET 3.5</strong> upgrades the host for agents and phone: Product Studio is first-class (record → viral pack → caption → ship), the phone PWA loads fully on <code>pocket.medinatechlabs.net</code>, multi-sandbox capsules + WebGPU, and everyday life skills for every agent.</p>
    <ul>
      <li><strong>Product Studio</strong> — agent skills, storyboard, viral pack, desk Studio agent</li>
      <li><strong>Phone PWA</strong> — public shell + pair + Bearer login on the tunnel domain</li>
      <li><strong>Capsules</strong> — PROTO-CAPSULE-WASM-009 isolated HostWorker / WASI / WebGPU</li>
      <li><strong>Life ops</strong> — food, flights, shop, reserve, web (never auto-pay)</li>
      <li><strong>Auth fix</strong> — session Bearer tokens work for phone + desk APIs</li>
    </ul>
    <div class="actions">
      <a class="go" href="/studio">Product Studio →</a>
      <a class="ghost" href="/phone">Phone</a>
      <a class="ghost" href="/desk">Desk</a>
    </div>
  </article>

  <article class="item">
    <div class="when">v3.4</div>
    <h2>Work Studio · digital assistant</h2>
    <p><strong>Work Studio</strong> is a first-class surface separate from the coding desk — research, plans, life ops (buy / reserve), Muse Spark, Auro, and auto-routing engines. Desk agents gain a <strong>Voice engine</strong> toggle so any chat can talk and listen.</p>
    <ul>
      <li><strong>Work Studio</strong> at <code>/work</code> — assistant chat + power loops</li>
      <li><strong>Voice engine</strong> on any desk agent (Codex, Grok, Claude, …)</li>
      <li><strong>Muse Spark</strong> + <strong>Auro</strong> first-class models</li>
      <li><strong>Same-WiFi IoT</strong> shared phone + desk registry</li>
    </ul>
    <div class="actions">
      <a class="go" href="/work">Open Work Studio →</a>
      <a class="ghost" href="/desk">Coding desk</a>
    </div>
  </article>

  <article class="item">
    <div class="when">Platform</div>
    <h2>First-class tabs, better organized</h2>
    <p>Primary tabs stay on the top bar for daily ops. Studios and systems live under <strong>More</strong> — full panels with their own action strip, not merged into one page.</p>
    <ul>
      <li><strong>Working</strong> — ops board for buy / analyze / reserve with live tools</li>
      <li><strong>Remote</strong> — host Edge + Screen View + Fusion sense</li>
      <li><strong>Phone</strong> — Aether device, pair codes, IoT home</li>
      <li><strong>Platform</strong> — sovereign stack status and ship loop</li>
      <li><strong>More</strong> — Voice Studio, Work Studio, Agent OS, API · MCP</li>
    </ul>
    <div class="actions">
      <a class="go" href="/desk">Open the desk →</a>
      <a class="ghost" href="/get">Get started</a>
    </div>
  </article>

  <article class="item">
    <div class="when">Ops</div>
    <h2>Working board — real work, not chat stack</h2>
    <p>Working mode is a multi-intent ops board. Split buy, analyze, and reserve into table rows with tools — agents use host PowerShell, WSL, and Python consoles when needed.</p>
    <div class="actions"><a class="go" href="/desk">Start Working on desk →</a></div>
  </article>

  <article class="item">
    <div class="when">Voice &amp; devices</div>
    <h2>Voice, Edge shell, Aether phone</h2>
    <p>Mic and voice proxy run with the desk. Open as an Edge app for a real window. Phone tab pairs mobile and IoT; hardware profile targets Aether (ANC-1 hybrid E-Ink).</p>
    <ul>
      <li>Seat <strong>Aria</strong> or open <strong>Voice Studio</strong> from More</li>
      <li>Use <strong>Open-POCKET-Edge</strong> for the desktop shell</li>
      <li><strong>Phone · IoT</strong> workflow seeds rooms and issues a pair code</li>
    </ul>
    <div class="actions">
      <a class="go" href="/phone">Phone surface →</a>
      <a class="ghost" href="/studio/voice">Voice Studio</a>
    </div>
  </article>

  <article class="item">
    <div class="when">Platform</div>
    <h2>Agents on your machine</h2>
    <p>Codex, Grok, Claude, Build, Habitat floor, Screen eyes, Remote browser, and internal Damian keepers stay host-local. API and MCP are under Developers.</p>
    <div class="actions">
      <a class="go" href="/developers">Developer docs →</a>
      <a class="ghost" href="/os">Agent OS</a>
    </div>
  </article>
  </div>

  <div class="note">
    <strong>How to stay current:</strong> open this page anytime at <code>/updates</code>, or check the marketing nav. The desk itself never leaves your machine.
  </div>

  <div class="foot">
    <a href="/">Home</a>
    <a href="/desk">App</a>
    <a href="/get">Get started</a>
    <a href="/download">Download</a>
    <span>v{__version__}</span>
  </div>
</main>
</body>
</html>
"""


def landing_html() -> str:
    nav = shell_nav(active="overview")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET — AI workspace on your machine</title>
<meta name="description" content="Chat with coding agents, invite your team, keep work private on your computer. Browser, desktop, and API."/>
<meta name="theme-color" content="#09090b"/>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f;--accent2:#0d8c6c}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:radial-gradient(1000px 480px at 8% -12%,rgba(16,163,127,.1),transparent 52%),var(--bg);color:var(--text);line-height:1.55;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none;cursor:pointer}}
{SHELL_CSS}
.pnav a,.pnav .cta,.pnav .ghost,.btn,.card-link,.go{{pointer-events:auto!important;position:relative;z-index:2}}
.hero{{padding:64px 22px 48px;border-bottom:1px solid var(--line);position:relative}}
.hero-inner{{max-width:1040px;margin:0 auto;position:relative;z-index:1}}
.eyebrow{{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:14px}}
h1{{font-size:clamp(32px,5vw,48px);line-height:1.08;letter-spacing:-.04em;margin:0 0 14px;color:var(--fg);max-width:16ch}}
.lead{{font-size:17px;color:var(--muted);max-width:520px;margin:0 0 24px}}
.cta-row{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:28px}}
.btn{{display:inline-flex;align-items:center;padding:12px 18px;border-radius:10px;font-weight:700;font-size:14px;border:1px solid transparent}}
.btn-primary{{background:var(--accent);color:#041}}
.btn-primary:hover{{background:var(--accent2)}}
.btn-ghost{{border-color:var(--line);color:var(--fg)}}
.btn-ghost:hover{{background:rgba(255,255,255,.06)}}
.proof{{display:flex;flex-wrap:wrap;gap:8px}}
.proof span{{font-size:12px;color:var(--muted);border:1px solid var(--line);padding:6px 11px;border-radius:999px}}
.section{{max-width:1040px;margin:0 auto;padding:56px 22px}}
.section h2{{font-size:28px;letter-spacing:-.03em;margin:0 0 8px;color:var(--fg)}}
.section .sub{{color:var(--muted);margin:0 0 24px;max-width:520px}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
@media(max-width:1000px){{.grid4,.grid3{{grid-template-columns:1fr 1fr}}}}
@media(max-width:640px){{.grid4,.grid3{{grid-template-columns:1fr}}}}
a.card-link{{
  display:flex;flex-direction:column;min-height:200px;padding:22px;border-radius:16px;
  border:1px solid var(--line);background:var(--panel);transition:border-color .15s,transform .12s;
  color:inherit
}}
a.card-link:hover{{border-color:rgba(16,163,127,.45);transform:translateY(-2px);background:#16161a}}
a.card-link .tag{{font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}}
a.card-link h3{{margin:0 0 8px;font-size:18px;color:var(--fg)}}
a.card-link p{{margin:0;font-size:13.5px;color:var(--muted);flex:1}}
a.card-link .go{{margin-top:16px;font-weight:700;font-size:13px;color:var(--accent)}}
.day{{border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--panel);margin-bottom:12px}}
.day h3{{margin:0 0 6px;font-size:16px;color:var(--fg)}}
.day p{{margin:0;font-size:14px;color:var(--muted)}}
.live{{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);margin-top:20px}}
.live i{{width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block;animation:pulse 1.2s infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
.foot{{border-top:1px solid var(--line);padding:22px;font-size:12px;color:var(--muted)}}
.foot-inner{{max-width:1040px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between}}
.foot a{{color:var(--muted);margin-left:12px}}
.foot a:hover{{color:var(--fg)}}
</style>
</head>
<body>
{nav}
<section class="hero">
  <div class="hero-inner">
    <div class="eyebrow">POCKET</div>
    <h1>AI that works where you work.</h1>
    <p class="lead">Chat with coding agents, plan projects, and keep team workspaces on your machine — not in a black-box cloud.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="/join">Create my seat</a>
      <a class="btn btn-ghost" href="/billing">See plans</a>
      <a class="btn btn-ghost" href="/desk">Sign in</a>
      <a class="btn btn-ghost" href="/download">Download for Windows</a>
    </div>
    <div class="proof">
      <span>Browser</span>
      <span>Desktop window</span>
      <span>Windows app</span>
      <span>Team invites</span>
      <span>v{__version__}</span>
    </div>
    <div class="live"><i></i> <span id="heartLabel">Checking connection…</span></div>
  </div>
</section>

<section class="section" id="day">
  <h2>A normal day with POCKET</h2>
  <p class="sub">Open it like any work app. Ask for code, research, or a plan. Invite teammates when you need them.</p>
  <div class="day">
    <h3>Morning — open and ask</h3>
    <p>Launch the app, start <strong>Code</strong> or <strong>Research</strong>, and describe the task. Results land in the same conversation.</p>
  </div>
  <div class="day">
    <h3>Afternoon — hand off work</h3>
    <p>Start a new chat for a different project. Upload a file. Keep sessions organized in the left sidebar.</p>
  </div>
  <div class="day">
    <h3>With a teammate</h3>
    <p>Send an invite. They create their own login and work in their own space. Your private files stay private.</p>
  </div>
  <div class="day">
    <h3>On another device</h3>
    <p>Pair with a short code, then send a file or note securely — without opening the whole workspace to the internet.</p>
  </div>
</section>

<section class="section" id="start">
  <h2>Start here</h2>
  <p class="sub">Choose how you want to open POCKET.</p>
  <div class="grid4">
    <a class="card-link" href="/desk">
      <div class="tag">Fastest</div>
      <h3>Open in browser</h3>
      <p>Sign in and start chatting right away on this machine.</p>
      <span class="go">Open the app →</span>
    </a>
    <a class="card-link" href="/get#edge">
      <div class="tag">Daily use</div>
      <h3>Install as an app</h3>
      <p>Pin POCKET to your taskbar with Edge’s Install as app.</p>
      <span class="go">See steps →</span>
    </a>
    <a class="card-link" href="/download">
      <div class="tag">Windows</div>
      <h3>Download</h3>
      <p>Packaged install for people who prefer a desktop program.</p>
      <span class="go">Download →</span>
    </a>
    <a class="card-link" href="/developers">
      <div class="tag">Builders</div>
      <h3>API</h3>
      <p>Keys and docs for scripts and product integrations.</p>
      <span class="go">Developer docs →</span>
    </a>
  </div>
</section>

<section class="section" id="product">
  <h2>What you get</h2>
  <p class="sub">One product. Clear jobs.</p>
  <div class="grid3">
    <a class="card-link" href="/desk">
      <div class="tag">People</div>
      <h3>Workspace app</h3>
      <p>Chat, agents, files, and team invites in one place.</p>
      <span class="go">Open →</span>
    </a>
    <a class="card-link" href="/developers">
      <div class="tag">Automation</div>
      <h3>Developer API</h3>
      <p>Same host, machine-readable access with API keys.</p>
      <span class="go">Docs →</span>
    </a>
    <a class="card-link" href="/studio">
      <div class="tag">Marketing</div>
      <h3>Studio</h3>
      <p>Clean demos and product captures for launches.</p>
      <span class="go">Open Studio →</span>
    </a>
  </div>
</section>

<footer class="foot">
  <div class="foot-inner">
    <div>© {COMPANY}</div>
    <div>
      <a href="/desk">App</a>
      <a href="/updates">Updates</a>
      <a href="/get">Get started</a>
      <a href="/download">Download</a>
      <a href="/developers">Developers</a>
      <a href="/studio">Studio</a>
    </div>
  </div>
</footer>
<script>
(async function(){{
  try{{
    const r=await fetch('/health');
    const j=await r.json();
    const el=document.getElementById('heartLabel');
    if(el) el.textContent = (j && (j.ok!==false)) ? 'Online — ready when you are' : 'Starting…';
  }}catch(e){{
    const el=document.getElementById('heartLabel');
    if(el) el.textContent='Offline — open POCKET on this computer first';
  }}
}})();
</script>
</body>
</html>
"""
