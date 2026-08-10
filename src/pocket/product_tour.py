"""Product tour — customer-facing steps (no lab jargon)."""

from __future__ import annotations

from typing import Any, Dict, List

from pocket import LAB, PRODUCT, __version__


def tour_steps() -> List[Dict[str, Any]]:
    return [
        {
            "id": "open",
            "title": "Open the app",
            "body": "Sign in on this computer. Your workspace stays private — only you and people you invite can use it.",
            "try": "Open the app and sign in",
        },
        {
            "id": "chat",
            "title": "Start with a simple ask",
            "body": "Choose Code, Research, or Plan. Describe the task in plain language. Work stays in that conversation.",
            "try": "New chat → type what you need",
        },
        {
            "id": "files",
            "title": "Bring your files in",
            "body": "Upload docs or code into the workspace. Agents use what you share in that session.",
            "try": "Upload in the left sidebar",
        },
        {
            "id": "team",
            "title": "Invite your team",
            "body": "Send an invite. Each person creates their own login and works in their own space.",
            "try": "Create invite from admin settings",
        },
        {
            "id": "devices",
            "title": "Share with another of your devices",
            "body": "Mint a short pair code, redeem on the other device, then send a file or note securely.",
            "try": "Devices panel after sign-in",
        },
        {
            "id": "api",
            "title": "Automate when you’re ready",
            "body": "Developers connect scripts with API keys. People keep using the same app UI.",
            "try": "Developers page",
        },
    ]


def presentation() -> Dict[str, Any]:
    return {
        "ok": True,
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "tagline": "AI workspace on your machine — chat, agents, and team seats.",
        "seo": {
            "title": "POCKET — AI workspace on your machine",
            "description": "Chat with coding agents, invite your team, keep work on your computer.",
            "primary_keyword": "AI workspace desktop",
            "secondary_keywords": [
                "coding agents",
                "private AI workspace",
                "team AI seats",
                "on-prem AI",
            ],
        },
        "steps": tour_steps(),
        "positioning": {
            "is": "A workspace app for people and an API for builders — on infrastructure you control.",
            "not": "Not a public chat toy. Not a dump of every internal tool name.",
        },
    }


def tour_html() -> str:
    """Lightweight HTML tour if someone hits /tour without marketing landing."""
    from pocket.product_shell import SHELL_CSS, shell_nav

    steps = "".join(
        f"""
      <div class="step">
        <div class="n">{i+1:02d}</div>
        <div>
          <h3>{s['title']}</h3>
          <p>{s['body']}</p>
          <span class="try">{s.get('try') or ''}</span>
        </div>
      </div>"""
        for i, s in enumerate(tour_steps())
    )
    nav = shell_nav(active="overview")
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET tour</title>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f}}
*{{box-sizing:border-box}}body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.55}}
a{{color:inherit;text-decoration:none}}
{SHELL_CSS}
.wrap{{max-width:720px;margin:0 auto;padding:40px 22px 80px}}
h1{{font-size:32px;letter-spacing:-.03em;color:var(--fg);margin:0 0 8px}}
.lead{{color:var(--muted);margin:0 0 28px}}
.step{{display:flex;gap:16px;border:1px solid var(--line);border-radius:14px;padding:18px;background:var(--panel);margin-bottom:12px}}
.step .n{{font-weight:800;color:var(--accent);font-size:14px;min-width:28px}}
.step h3{{margin:0 0 6px;font-size:16px;color:var(--fg)}}
.step p{{margin:0;font-size:14px;color:var(--muted)}}
.try{{display:inline-block;margin-top:8px;font-size:12px;color:var(--accent)}}
.cta{{display:inline-flex;margin-top:20px;padding:12px 18px;border-radius:10px;background:var(--accent);color:#041;font-weight:700}}
</style></head><body>
{nav}
<main class="wrap">
  <h1>How POCKET works</h1>
  <p class="lead">Six short steps from open to daily use.</p>
  {steps}
  <a class="cta" href="/desk">Open the app</a>
</main>
</body></html>
"""
