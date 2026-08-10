"""Shared product chrome — same nav across marketing pages."""

from __future__ import annotations

SHELL_CSS = """
.pnav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:11px 18px;border-bottom:1px solid rgba(255,255,255,.07);background:rgba(9,9,11,.94);position:sticky;top:0;z-index:30;backdrop-filter:blur(16px) saturate(1.1)}
.pnav .brand{display:flex;align-items:center;gap:9px;font-weight:650;letter-spacing:-.03em;font-size:13.5px;color:#fafafa;text-decoration:none;margin-right:6px}
.pnav .brand i{width:22px;height:22px;border-radius:7px;background:linear-gradient(145deg,#10a37f,#0a7a5f);display:grid;place-items:center;font-size:11px;font-weight:800;color:#041;font-style:normal;box-shadow:0 0 0 1px rgba(16,163,127,.3)}
.pnav .links{display:flex;gap:1px;flex-wrap:wrap;background:rgba(255,255,255,.03);padding:2px;border-radius:10px;border:1px solid rgba(255,255,255,.07)}
.pnav .links a{color:#71717a;text-decoration:none;font-size:12.5px;font-weight:550;padding:6px 12px;border-radius:8px;transition:color .15s,background .15s}
.pnav .links a:hover{color:#e4e4e7;background:rgba(255,255,255,.05)}
.pnav .links a.on{color:#fafafa;background:#1a1a1e;box-shadow:0 0 0 1px rgba(255,255,255,.05)}
.pnav .sp{flex:1}
.pnav .pill{font-size:11px;color:#71717a;border:1px solid rgba(255,255,255,.07);padding:5px 10px;border-radius:999px}
.pnav .cta{font-size:12.5px;font-weight:650;color:#041;background:#10a37f;padding:8px 14px;border-radius:8px;text-decoration:none;transition:background .15s}
.pnav .cta:hover{background:#0d8c6c;text-decoration:none}
.pnav .ghost{font-size:12.5px;color:#71717a;border:1px solid rgba(255,255,255,.07);padding:7px 12px;border-radius:8px;text-decoration:none;transition:color .15s,background .15s}
.pnav .ghost:hover{color:#e4e4e7;background:rgba(255,255,255,.04);text-decoration:none}
@media(max-width:720px){.pnav .pill,.pnav .ghost{display:none}}
"""


def shell_nav(*, active: str = "overview") -> str:
    """active: overview | app | start | download | api | studio | updates | work"""

    def cls(name: str) -> str:
        return ' class="on"' if name == active else ""

    return f"""
<header class="pnav">
  <a class="brand" href="/"><i>P</i>POCKET</a>
  <nav class="links" aria-label="Product">
    <a href="/"{cls("overview")}>Home</a>
    <a href="/desk"{cls("app")}>Desk</a>
    <a href="/work"{cls("work")}>Work Studio</a>
    <a href="/updates"{cls("updates")}>Updates</a>
    <a href="/get"{cls("start")}>Get started</a>
    <a href="/studio"{cls("studio")}>Studio</a>
    <a href="/loomgraph"{cls("loomgraph")}>LOOMGRAPH</a>
    <a href="/studio/create"{cls("creative")}>Creative</a>
    <a href="/developers"{cls("api")}>Developers</a>
  </nav>
  <div class="sp"></div>
  <span class="pill">Runs on your machine</span>
  <a class="ghost" href="/get">Get started</a>
  <a class="cta" href="/desk">Open app</a>
</header>
"""


PRODUCT_HUB_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET — AI workspace on your machine</title>
<meta name="description" content="Chat with coding agents, invite your team, keep work on your computer."/>
<meta name="theme-color" content="#000"/>
<style>
:root{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.07);--text:#e4e4e7;--muted:#71717a;--accent:#10a37f;--fg:#fafafa}
*{box-sizing:border-box}body{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}
__SHELL_CSS__
.wrap{max-width:980px;margin:0 auto;padding:48px 22px 88px}
h1{font-size:clamp(28px,4.2vw,40px);letter-spacing:-.04em;font-weight:600;margin:0 0 12px;line-height:1.1;color:var(--fg)}
.lead{font-size:15.5px;color:var(--muted);max-width:540px;margin:0 0 32px;line-height:1.55}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:14px;padding:22px;background:var(--panel);display:flex;flex-direction:column;min-height:210px;transition:border-color .15s,box-shadow .15s}
.card:hover{border-color:rgba(16,163,127,.28);box-shadow:0 0 0 1px rgba(16,163,127,.08)}
.card h3{margin:0 0 8px;font-size:16px;font-weight:600;letter-spacing:-.02em;color:var(--fg)}
.card p{margin:0;font-size:13px;color:var(--muted);flex:1;line-height:1.5}
.card .go{margin-top:16px;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:650;color:#041;background:var(--accent);padding:9px 14px;border-radius:8px;text-decoration:none;width:fit-content}
.card .go:hover{background:#0d8c6c}
.card .meta{font-size:11px;color:var(--muted);margin-top:10px}
.note{border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:#0c0c0e;margin-top:28px;font-size:13px;color:var(--muted)}
.note strong{color:var(--fg)}
.foot{margin-top:40px;font-size:12px;color:var(--muted)}
</style>
</head>
<body>
__SHELL_NAV__
<main class="wrap">
  <h1>Three ways to use POCKET</h1>
  <p class="lead">Open the app, automate with the API, or package demos in Studio. Same account. Same workspace.</p>

  <div class="grid">
    <div class="card">
      <h3>App</h3>
      <p>Chat with coding agents, plan work, run tools on this computer. Browser or desktop window — same experience.</p>
      <a class="go" href="/desk">Open the app →</a>
      <div class="meta">Daily home for people</div>
    </div>
    <div class="card">
      <h3>LOOMGRAPH</h3>
      <p>Default forever harness — readable graphs + control loops. Sense → plan → act → verify. See the path. Ship with Pocket.</p>
      <a class="go" href="/loomgraph">Open LOOMGRAPH →</a>
      <div class="meta">Protocol POCKET-LOOMGRAPH/1.0</div>
    </div>
    <div class="card">
      <h3>Studio</h3>
      <p>Product demos, Creative chat, Community shares. Turn recordings into clean launches.</p>
      <a class="go" href="/studio">Open Studio →</a>
      <div class="meta">Product · Creative · Community</div>
    </div>
  </div>
  <div class="grid" style="margin-top:0">
    <div class="card">
      <h3>API</h3>
      <p>Connect scripts and other tools with an API key. Built for automation and product integrations.</p>
      <a class="go" href="/developers">Developer docs →</a>
      <div class="meta">Keys from the Developers page</div>
    </div>
    <div class="card">
      <h3>Creative Studio</h3>
      <p>Friendly multi-mode chat — image, video, blog, paper, social — with intentional community share.</p>
      <a class="go" href="/studio/create">Open Creative →</a>
      <div class="meta">Share only on purpose</div>
    </div>
    <div class="card">
      <h3>Integrations</h3>
      <p>55 executable connectors (Discord desktop, Edge SaaS, Working board). Agents open real apps.</p>
      <a class="go" href="/desk">Open Desk integrations →</a>
      <div class="meta">POST /v1/integrations/execute</div>
    </div>
  </div>
  <div class="grid" style="margin-top:0">
    <div class="card">
      <h3>KEEP agents</h3>
      <p>Self-hosted agents that keep working until the chat ends — with isolated browsers.</p>
      <a class="go" href="/developers">API · /v1/keep →</a>
      <div class="meta">POCKET-KEEP/1.0</div>
    </div>
    <div class="card">
      <h3>RECALL codes</h3>
      <p>Official recall-code software — reattach KEEP + session work after you leave.</p>
      <a class="go" href="/developers">API · /v1/recall →</a>
      <div class="meta">pk_rcl_… · hash-stored</div>
    </div>
    <div class="card">
      <h3>POCKET MAIL</h3>
      <p>Official mailing for this app — templates, outbox, SMTP when you configure it.</p>
      <a class="go" href="/developers">API · /v1/mail →</a>
      <div class="meta">POCKET-MAIL/1.0</div>
    </div>
  </div>

  <div class="note">
    <strong>Sign in</strong> with the username and password for this workspace.
    Teammates use the invite link their admin sent — not the admin password.
  </div>

  <p class="foot">POCKET · runs on your infrastructure</p>
</main>
</body>
</html>
"""


def hub_html() -> str:
    return (
        PRODUCT_HUB_HTML.replace("__SHELL_CSS__", SHELL_CSS)
        .replace("__SHELL_NAV__", shell_nav(active="overview"))
    )
