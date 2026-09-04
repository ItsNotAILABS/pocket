"""Public documentation + how-to hub (research + operator surface)."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any, Dict, Optional

from pocket.license_gate import license_meta


def _docs_root() -> Path:
    return Path(__file__).resolve().parents[2] / "docs"


def _md_to_html_simple(md: str) -> str:
    """Minimal markdown → HTML for how-to pages (no external deps)."""
    lines = (md or "").replace("\r\n", "\n").split("\n")
    out: list[str] = []
    in_code = False
    in_ul = False
    in_table = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>")
            in_table = False

    for raw in lines:
        line = raw
        if line.strip().startswith("```"):
            close_ul()
            close_table()
            if not in_code:
                in_code = True
                out.append("<pre><code>")
            else:
                in_code = False
                out.append("</code></pre>")
            continue
        if in_code:
            out.append(html.escape(line) + "\n")
            continue
        # tables
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c or "") for c in cells):
                continue  # separator
            if not in_table:
                close_ul()
                in_table = True
                out.append("<table><tbody>")
            tds = "".join(f"<td>{_inline(c)}</td>" for c in cells)
            out.append(f"<tr>{tds}</tr>")
            continue
        else:
            close_table()
        if line.startswith("# "):
            close_ul()
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            close_ul()
            out.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("### "):
            close_ul()
            out.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline(line[2:])}</li>")
        elif line.strip() == "":
            close_ul()
            out.append("")
        else:
            close_ul()
            out.append(f"<p>{_inline(line)}</p>")
    close_ul()
    close_table()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def _inline(s: str) -> str:
    t = html.escape(s or "")
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def resolve_doc(rel: str) -> Optional[Path]:
    """Resolve a docs path safely under docs/."""
    root = _docs_root().resolve()
    rel = (rel or "").replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return None
    # allow how-to/FOO.md or INDEX.md
    p = (root / rel).resolve()
    try:
        p.relative_to(root)
    except Exception:
        return None
    if p.is_file() and p.suffix.lower() in (".md", ".txt"):
        return p
    if not p.suffix and (root / f"{rel}.md").is_file():
        return root / f"{rel}.md"
    return None


def render_doc_page(rel: str) -> Optional[str]:
    p = resolve_doc(rel)
    if not p:
        return None
    md = p.read_text(encoding="utf-8", errors="replace")
    body = _md_to_html_simple(md)
    title = p.stem.replace("_", " ")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{html.escape(title)} · POCKET Docs</title>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0% 0%,rgba(16,163,127,.08),transparent 50%),var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}}
a{{color:var(--accent)}}
.wrap{{max-width:820px;margin:0 auto;padding:28px 18px 80px}}
nav{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}}
nav a{{border:1px solid var(--line);padding:6px 10px;border-radius:8px;color:var(--muted);font-size:12px;font-weight:600;text-decoration:none}}
h1,h2,h3{{color:var(--fg);letter-spacing:-.02em}}
h1{{font-size:1.6rem}} h2{{font-size:1.15rem;margin-top:1.6em}}
code{{background:#0a0a0a;padding:1px 6px;border-radius:5px;font-size:.9em}}
pre{{background:#0a0a0a;border:1px solid var(--line);border-radius:12px;padding:14px;overflow:auto;font-size:12.5px}}
pre code{{background:none;padding:0}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0}}
td{{border:1px solid var(--line);padding:8px 10px;vertical-align:top}}
ul{{padding-left:1.2em}}
.muted{{color:var(--muted);font-size:13px}}
</style>
</head>
<body>
<main class="wrap">
  <nav>
    <a href="/docs">Docs hub</a>
    <a href="/docs/view/INDEX">Index</a>
    <a href="/docs/view/HOW_TO">How-to</a>
    <a href="/docs/view/how-to/PHONEAI">PhoneAI</a>
    <a href="/phoneai/mcp">MCP apps</a>
    <a href="/mail">Mail</a>
    <a href="/desk">Desk</a>
    <a href="/install">Install</a>
  </nav>
  <p class="muted">{html.escape(str(p.relative_to(_docs_root())))}</p>
  {body}
</main>
</body>
</html>
"""


def docs_hub_html() -> str:
    lic = license_meta()
    try:
        from pocket.platform_catalog import catalog

        cat = catalog()
    except Exception:
        cat = {"systems": [], "how_tos": [], "version": "?", "quick_start": []}

    systems = cat.get("systems") or []
    how_tos = cat.get("how_tos") or []
    sys_cards = []
    for s in systems:
        ht = s.get("how_to") or ""
        link = "/docs/view/" + ht.replace("docs/", "").replace(".md", "") if ht.startswith("docs/") else "/docs"
        sys_cards.append(
            f'<a class="card" href="{html.escape(link)}"><h2>{html.escape(s.get("name") or s.get("id") or "")}</h2>'
            f'<p>{html.escape(s.get("for") or "")}</p>'
            f'<p class="meta">{html.escape(s.get("where") or "")}</p></a>'
        )
    how_cards = []
    for h in how_tos:
        path = (h.get("path") or "").replace("docs/", "").replace(".md", "")
        how_cards.append(
            f'<a class="card how" href="/docs/view/{html.escape(path)}"><h2>{html.escape(h.get("title") or "")}</h2>'
            f'<p class="meta">{html.escape(h.get("path") or "")}</p></a>'
        )
    qs = []
    for q in cat.get("quick_start") or []:
        if q.get("cmd"):
            qs.append(f"<li><b>{html.escape(q.get('title') or '')}</b> — <code>{html.escape(q['cmd'])}</code></li>")
        elif q.get("url"):
            qs.append(
                f'<li><b>{html.escape(q.get("title") or "")}</b> — <a href="{html.escape(q["url"])}">{html.escape(q["url"])}</a></li>'
            )
        else:
            qs.append(f"<li><b>{html.escape(q.get('title') or '')}</b> — {html.escape(q.get('note') or '')}</li>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET Docs Hub</title>
<meta name="theme-color" content="#09090b"/>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.1);--text:#e4e4e7;--muted:#a1a1aa;--fg:#fafafa;--accent:#10a37f}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0% 0%,rgba(16,163,127,.08),transparent 50%),var(--bg);color:var(--text);line-height:1.55;-webkit-font-smoothing:antialiased}}
a{{color:var(--accent);text-decoration:none}}
.wrap{{max-width:1040px;margin:0 auto;padding:36px 18px 80px}}
h1{{letter-spacing:-.03em;color:var(--fg);margin:0 0 8px;font-size:1.75rem}}
.lead{{color:var(--muted);max-width:640px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin-top:18px}}
.card{{border:1px solid var(--line);border-radius:14px;padding:16px;background:var(--panel);display:block;color:inherit}}
.card:hover{{border-color:rgba(16,163,127,.4)}}
.card h2{{margin:0 0 6px;font-size:14px;color:var(--fg)}}
.card p{{margin:0;font-size:12.5px;color:var(--muted)}}
.card .meta{{margin-top:8px;font-size:11px;font-family:ui-monospace,monospace}}
.card.how{{border-color:rgba(16,163,127,.2)}}
.nav{{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}}
.nav a{{border:1px solid var(--line);padding:8px 12px;border-radius:9px;color:var(--fg);font-size:13px;font-weight:600}}
.pill{{display:inline-block;font-size:11px;border:1px solid var(--line);padding:3px 8px;border-radius:999px;color:var(--muted)}}
h2.sec{{margin:28px 0 0;font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}
.qs{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-top:14px}}
.qs ul{{margin:0;padding-left:1.2em}}
.qs li{{margin:6px 0;font-size:13px}}
code{{background:#0a0a0a;padding:1px 6px;border-radius:5px;font-size:12px}}
</style>
</head>
<body>
<main class="wrap">
  <span class="pill">POCKET {html.escape(str(cat.get("version") or ""))} · ItsNotAI Labs</span>
  <h1>Documentation hub</h1>
  <p class="lead">Everything built — organized, wired, with how-to guides. Live catalog also at <code>GET /v1/catalog</code>.</p>
  <div class="nav">
    <a href="/desk">Desk</a>
    <a href="/mail">Agent Mail</a>
    <a href="/install">Install slices</a>
    <a href="/work">Work Studio</a>
    <a href="/loomgraph">LOOMGRAPH</a>
    <a href="/developers">API</a>
    <a href="/download">Downloads</a>
    <a href="/license">License</a>
    <a href="/docs/view/INDEX">Full index</a>
    <a href="/docs/view/HOW_TO">How-to index</a>
    <a href="/phoneai">PhoneAI</a>
    <a href="/phoneai/mcp">MCP apps</a>
    <a href="/registry">Registry</a>
    <a href="/v1/registry">Registry JSON</a>
    <a href="/docs/view/research/PHONEAI_MCP_APPS_PAPER">MCP paper</a>
    <a href="/docs/view/whitepapers/PHONEAI_PUBLIC_TUNNEL">Tunnel paper</a>
  </div>

  <h2 class="sec">Quick start</h2>
  <div class="qs"><ul>{"".join(qs) or "<li>Start host · open /desk</li>"}</ul></div>

  <h2 class="sec">How-to guides</h2>
  <div class="grid">{"".join(how_cards) or "<div class='card'><p>No how-tos loaded</p></div>"}</div>

  <h2 class="sec">Systems (built &amp; wired)</h2>
  <div class="grid">{"".join(sys_cards)}</div>

  <h2 class="sec">Also</h2>
  <div class="grid">
    <a class="card" href="/download"><h2>Downloads</h2><p>Windows packages after Researcher License. Id: {html.escape(str(lic.get("id") or ""))}</p></a>
    <a class="card" href="/license/text"><h2>Researcher License</h2><p>Non-commercial research &amp; evaluation.</p></a>
    <a class="card" href="/v1/catalog"><h2>Live JSON catalog</h2><p>Systems · skills · engines · agent mail status.</p></a>
    <a class="card" href="/docs/view/DOCTRINE"><h2>Doctrine</h2><p>30 laws · oath · forbidden · GET /v1/doctrine</p></a>
    <a class="card" href="/docs/view/SECURITY"><h2>Security</h2><p>Founder host ≠ market seat.</p></a>
  </div>
</main>
</body>
</html>
"""


def license_page_html() -> str:
    lic = license_meta()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{html.escape(str(lic.get("title") or "License"))}</title>
<style>
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(800px 360px at 0% 0%,rgba(16,163,127,.08),transparent 50%),#09090b;color:#e4e4e7;line-height:1.55;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:720px;margin:0 auto;padding:40px 20px}}
h1{{color:#fafafa;letter-spacing:-.03em}}
a{{color:#10a37f}}
.card{{border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:20px;background:#141416}}
</style>
</head>
<body>
<main class="wrap">
  <h1>POCKET Researcher License</h1>
  <div class="card">
    <p><strong>{html.escape(str(lic.get("id") or ""))}</strong> — {html.escape(str(lic.get("summary") or ""))}</p>
    <p><a href="/license/text">Full text</a> · <a href="/download">Downloads</a> · <a href="/docs">Docs hub</a></p>
  </div>
</main>
</body>
</html>
"""


def license_text() -> str:
    root = Path(__file__).resolve().parents[2]
    for p in (root / "LICENSE-RESEARCHER.md", root / "LICENSE"):
        if p.exists():
            return p.read_text(encoding="utf-8")
    return "LICENSE-RESEARCHER.md missing on host."
