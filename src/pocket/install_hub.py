"""Public install hub — one-line slice links for users and AI agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Prefer sibling pocket-agent repo (public distribution)
CANDIDATES = [
    Path.home() / "OneDrive" / "pocket-agent",
    Path(__file__).resolve().parents[3] / "pocket-agent",
    Path(__file__).resolve().parents[2] / "pocket-agent",
]

# Map slice id → script paths under /install/ on this host
HOST_SCRIPTS = {
    "agent": ("agent.sh", "agent.ps1"),
    "sdk": ("sdk.sh", "sdk.ps1"),
    "skills": ("skills.sh", "skills.ps1"),
    "knowledge": ("knowledge.sh", "knowledge.ps1"),
    "capsules": ("capsules.sh", "capsules.ps1"),
    "plug": ("plug.sh", "plug.ps1"),
    "host": ("host.sh", "host.ps1"),
    "mail": ("mail.sh", "mail.ps1"),
}

# Aliases served from repo root (not install/)
ROOT_ALIASES = {
    "agent.sh": "install.sh",
    "agent.ps1": "install.ps1",
    "install.sh": "install.sh",
    "install.ps1": "install.ps1",
}


def _agent_root() -> Path | None:
    for p in CANDIDATES:
        if (p / "install" / "slices.json").is_file():
            return p
    return None


def slices_json(host_base: str = "") -> Dict[str, Any]:
    root = _agent_root()
    base = (host_base or "").rstrip("/")
    if root:
        try:
            data = json.loads((root / "install" / "slices.json").read_text(encoding="utf-8"))
            data["served_from"] = str(root)
            data["ok"] = True
            if base:
                data["host_base"] = base
                for s in data.get("slices") or []:
                    sid = s.get("id") or ""
                    scripts = HOST_SCRIPTS.get(sid)
                    if scripts:
                        sh, ps = scripts
                        s["one_liner_host_sh"] = f"curl -fsSL {base}/install/{sh} | sh"
                        s["one_liner_host_ps1"] = f"irm {base}/install/{ps} | iex"
            return data
        except Exception as e:
            return {"ok": False, "error": str(e)[:200]}
    # Embedded fallback catalog
    return {
        "ok": True,
        "schema": "pocket.install.slices.v1",
        "base_url_hint": "https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main",
        "slices": [
            {
                "id": "agent",
                "name": "POCKET Agent",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install.ps1 | iex",
            },
            {
                "id": "sdk",
                "name": "POCKET Python SDK",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/sdk.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/sdk.ps1 | iex",
            },
            {
                "id": "skills",
                "name": "Skills pack",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/skills.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/skills.ps1 | iex",
            },
            {
                "id": "knowledge",
                "name": "App knowledge",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/knowledge.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/knowledge.ps1 | iex",
            },
            {
                "id": "plug",
                "name": "Agent plug-n-play",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/plug.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/plug.ps1 | iex",
            },
            {
                "id": "mail",
                "name": "POCKET Agent Mail",
                "one_liner_sh": "curl -fsSL https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/mail.sh | sh",
                "one_liner_ps1": "irm https://raw.githubusercontent.com/ItsNotAILABS/pocket-agent/main/install/mail.ps1 | iex",
            },
        ],
        "note": "Full slices live in pocket-agent/install when checked out beside pocket-os",
    }


def install_hub_html(host_base: str = "") -> str:
    data = slices_json(host_base=host_base)
    rows = []
    for s in data.get("slices") or []:
        name = s.get("name") or s.get("id")
        sh = s.get("one_liner_sh") or ""
        ps = s.get("one_liner_ps1") or ""
        host_sh = s.get("one_liner_host_sh") or ""
        host_ps = s.get("one_liner_host_ps1") or ""
        provides = ", ".join(s.get("provides") or [])[:140]
        extra = ""
        if host_sh:
            extra = f"""
  <label>This host (mirror)</label>
  <pre class="cmd">{_esc(host_sh)}</pre>
  <label>This host · Windows</label>
  <pre class="cmd">{_esc(host_ps)}</pre>"""
        rows.append(
            f"""
<div class="card">
  <h2>{_esc(name)}</h2>
  <p class="muted">{_esc(provides or s.get("for") or "")}</p>
  <label>macOS / Linux (GitHub)</label>
  <pre class="cmd">{_esc(sh)}</pre>
  <label>Windows PowerShell (GitHub)</label>
  <pre class="cmd">{_esc(ps)}</pre>{extra}
</div>"""
        )
    body = "\n".join(rows)
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Install POCKET · slices</title>
<style>
  :root {{ --bg:#07070a; --card:#121218; --fg:#fafafa; --muted:#a1a1aa; --accent:#10a37f; --line:rgba(255,255,255,.1); }}
  body {{ margin:0; font-family:ui-sans-serif,system-ui,sans-serif; background:var(--bg); color:var(--fg); padding:32px 20px 64px; }}
  h1 {{ font-size:1.75rem; letter-spacing:-.03em; margin:0 0 8px; }}
  .sub {{ color:var(--muted); margin:0 0 28px; line-height:1.5; max-width:640px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:20px 22px; margin:0 0 16px; max-width:720px; }}
  h2 {{ margin:0 0 8px; font-size:1.1rem; }}
  .muted {{ color:var(--muted); font-size:13px; margin:0 0 12px; }}
  label {{ display:block; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin:10px 0 6px; font-weight:700; }}
  pre.cmd {{ margin:0; padding:12px 14px; background:#0a0a0e; border-radius:10px; border:1px solid var(--line);
    overflow:auto; font-size:12px; line-height:1.45; color:#86efac; white-space:pre-wrap; word-break:break-all; }}
  a {{ color:var(--accent); }}
  .top {{ max-width:720px; margin-bottom:8px; font-size:13px; }}
</style></head><body>
<p class="top"><a href="/desk">← Desk</a> · <a href="/v1/install/slices">JSON catalog</a> · <a href="/developers">API</a></p>
<h1>Install POCKET — one-line slices</h1>
<p class="sub">Plug-and-play for users and AI agents: agent CLI, Python SDK, skills pack, app knowledge, WASM capsules. JSON: <code>/v1/install/slices</code></p>
{body}
<p class="muted">Warning: agent slices run with your user permissions. Use <code>capsule spin --reason untrusted_eval</code> for untrusted code.</p>
</body></html>"""


def _esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _resolve_install_file(root: Path, rel: str) -> Optional[Path]:
    """Resolve a safe path under pocket-agent for public install downloads."""
    rel = (rel or "").lstrip("/").replace("\\", "/")
    if not rel or ".." in rel.split("/"):
        return None
    # Root-level install aliases
    if rel in ROOT_ALIASES:
        fp = root / ROOT_ALIASES[rel]
        return fp if fp.is_file() else None
    # Prefer install/ tree
    fp = root / "install" / rel
    if fp.is_file():
        return fp
    # knowledge / skills / sdk packages (downloadable zip-less tree)
    for prefix in ("knowledge/", "skills/", "sdk/", "docs/"):
        if rel.startswith(prefix) or rel == prefix.rstrip("/"):
            fp = root / rel
            if fp.is_file():
                return fp
    # top-level install scripts
    if rel in ("install.sh", "install.ps1"):
        fp = root / rel
        return fp if fp.is_file() else None
    return None


def serve_install_asset(handler, path: str):
    """Serve raw install scripts and knowledge assets from pocket-agent."""
    root = _agent_root()
    if not root:
        return handler._json(404, {"ok": False, "error": "pocket-agent install tree not found"})
    rel = path[len("/install/") :].lstrip("/") if path.startswith("/install/") else path.lstrip("/")
    fp = _resolve_install_file(root, rel)
    if not fp:
        return handler._json(404, {"ok": False, "error": "not found", "path": rel})
    data = fp.read_bytes()
    ctype = "text/plain; charset=utf-8"
    if rel.endswith(".json"):
        ctype = "application/json"
    elif rel.endswith(".md"):
        ctype = "text/markdown; charset=utf-8"
    handler.send_response(200)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "public, max-age=60")
    handler._sec_headers()
    handler.end_headers()
    handler.wfile.write(data)
    return None
