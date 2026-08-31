"""WebMCP — stable action catalog from Pocket diffusion.

Fusion work (symbols → IR → remake) plus host apps, PhoneAI tools, engine
uses, and page HTML are diffused into one list of functions / actions /
tasks. Agents and PhoneAI both consume that list.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "webmcp"
ROOT.mkdir(parents=True, exist_ok=True)
CATALOG = ROOT / "catalog.json"
SCHEMA = "pocket.webmcp.v1"


def _act(
    *,
    source: str,
    kind: str,
    name: str,
    how_agents: str,
    how_phoneai: str,
    invoke: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    slug = re.sub(r"[^a-z0-9]+", "_", (source + "_" + name).lower()).strip("_")[:80]
    rec = {
        "id": slug or f"{source}_{kind}",
        "source": source,
        "kind": kind,  # action | task | function | app | surface | control
        "name": (name or "")[:160],
        "how_agents": how_agents,
        "how_phoneai": how_phoneai,
        "invoke": invoke,
    }
    if extra:
        rec.update(extra)
    return rec


class _PageActions(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.actions: List[Dict[str, str]] = []
        self._href = ""
        self._tag = ""
        self._buf = ""
        self._attrs: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        d = {k.lower(): (v or "") for k, v in attrs}
        self._attrs = d
        if tag == "a" and d.get("href"):
            self._href = d["href"]
            self._tag = "a"
            self._buf = ""
        elif tag == "button":
            self._tag = "button"
            self._buf = ""
        elif tag == "input":
            label = d.get("value") or d.get("name") or d.get("aria-label") or d.get("placeholder") or d.get("type")
            if label:
                self.actions.append({"kind": "control", "name": label, "href": "", "tag": "input"})
        elif tag == "textarea":
            label = d.get("name") or d.get("aria-label") or "textarea"
            self.actions.append({"kind": "control", "name": label, "href": "", "tag": "textarea"})
        elif d.get("role") in ("button", "link", "menuitem", "tab"):
            self._tag = d["role"]
            self._buf = d.get("aria-label") or ""

    def handle_data(self, data: str) -> None:
        if self._tag:
            self._buf += data

    def handle_endtag(self, tag: str) -> None:
        if tag in ("a", "button") or self._tag in ("button", "link", "menuitem", "tab"):
            name = (self._buf or self._attrs.get("aria-label") or self._href or tag).strip()
            if name:
                self.actions.append(
                    {"kind": "action" if tag in ("a", "button") else "control", "name": name[:120], "href": self._href, "tag": tag}
                )
        self._tag = ""
        self._href = ""
        self._buf = ""


def parse_page_html(html: str, *, url: str = "") -> List[Dict[str, Any]]:
    p = _PageActions()
    try:
        p.feed(html or "")
    except Exception:
        pass
    out = []
    seen = set()
    for a in p.actions:
        key = (a["tag"], a["name"].lower(), a.get("href") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append(
            _act(
                source="web",
                kind=a["kind"],
                name=a["name"],
                how_agents=f"web_ui_act name={a['name']!r}" + (f" or open {a['href']}" if a.get("href") else ""),
                how_phoneai="PhoneAI cannot click remote DOM; host agent uses web_ui_act / web_ui_open. Twin can ask Grok/Codex to drive it.",
                invoke="web_ui_act" if a["tag"] != "a" else "web_ui_open",
                extra={"href": a.get("href") or "", "page": url, "tag": a["tag"]},
            )
        )
    return out[:400]


def _from_url(url: str) -> List[Dict[str, Any]]:
    url = (url or "").strip()
    if not url.startswith("http"):
        return []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "POCKET-WebMCP/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read(400_000).decode("utf-8", errors="replace")
    except Exception:
        return [
            _act(
                source="web",
                kind="task",
                name=f"Open {url}",
                how_agents="web_ui_open / web_ui_browse",
                how_phoneai="Open via Pocket host; PhoneAI kernel Work can request browse.",
                invoke="web_ui_browse",
                extra={"href": url},
            )
        ]
    return parse_page_html(raw, url=url)


def _from_fusion() -> List[Dict[str, Any]]:
    try:
        from pocket.fusion_remake import symbols_to_ir
        from pocket.perception import sense

        page = sense(max_ui=400, force=True, include_image=False)
        ir = symbols_to_ir(page, max_nodes=300)
    except Exception:
        return []
    out = []
    for n in ir.get("nodes") or []:
        name = (n.get("text") or "").strip()
        if not name:
            continue
        kind = n.get("kind") or "control"
        out.append(
            _act(
                source="fusion",
                kind="control" if kind not in ("button", "link", "input") else "action",
                name=name,
                how_agents=f"ui_click / web_ui_act / fusion remake · kind={kind}",
                how_phoneai="PhoneAI reads this list; host clicks via fusion. Phone asks Work twin to act.",
                invoke="web_ui_act",
                extra={"fusion_kind": kind, "bbox": n.get("bbox")},
            )
        )
    return out[:300]


def _from_desktop_apps() -> List[Dict[str, Any]]:
    try:
        from pocket.safety import ALLOWED_APPS
    except Exception:
        return []
    out = []
    for aid, meta in (ALLOWED_APPS or {}).items():
        label = (meta.get("label") if isinstance(meta, dict) else None) or aid
        out.append(
            _act(
                source="app",
                kind="app",
                name=str(label),
                how_agents=f"desktop open_app {aid}",
                how_phoneai=f"PhoneAI tool antigravity-style: execute app open; Work twin engine Anti for Antigravity.",
                invoke="open_app",
                extra={"app_id": aid},
            )
        )
    return out


def _from_phoneai() -> List[Dict[str, Any]]:
    try:
        from pocket.phoneai_bridge import TOOLS
    except Exception:
        return []
    out = []
    for t in TOOLS:
        out.append(
            _act(
                source="phoneai",
                kind="function",
                name=t.get("name") or t.get("id"),
                how_agents=f"POST /api/execute tool_id={t.get('id')}",
                how_phoneai=f"Native tool {t.get('id')} — PhoneAI reads params and runs typed execute + receipt.",
                invoke="phoneai_execute",
                extra={"tool_id": t.get("id"), "risk": t.get("risk")},
            )
        )
    out.append(
        _act(
            source="phoneai",
            kind="task",
            name="Work twin (Grok/Codex/Antigravity)",
            how_agents="POST /v1/phoneai/work",
            how_phoneai="Kernel Work chat — message like Pocket twin.",
            invoke="phoneai_work",
            extra={"url": "/phoneai/work"},
        )
    )
    return out


def _from_engines() -> List[Dict[str, Any]]:
    try:
        from pocket.web_ui_engine import ENGINE_USES
    except Exception:
        return []
    out = []
    for u in ENGINE_USES:
        out.append(
            _act(
                source="engine",
                kind="task",
                name=u.get("title") or u.get("id"),
                how_agents=f"engine_use {u.get('id')} tool={u.get('tool')}",
                how_phoneai="Ask Work twin or companion; host runs the named use.",
                invoke="engine_use",
                extra={"use_id": u.get("id"), "tool": u.get("tool")},
            )
        )
    return out


def _from_mcp() -> List[Dict[str, Any]]:
    try:
        from pocket.mcp_bundle import list_tools

        pack = list_tools()
        names = [t.get("tool") for t in (pack.get("tools") or []) if isinstance(t, dict) and t.get("tool")]
    except Exception:
        names = []
    out = []
    for n in names[:120]:
        out.append(
            _act(
                source="mcp",
                kind="function",
                name=n,
                how_agents=f"mcp invoke {n}",
                how_phoneai="PhoneAI does not run MCP locally; Pocket Live / host invoke.",
                invoke="mcp_invoke",
                extra={"tool": n},
            )
        )
    return out


def _from_work() -> List[Dict[str, Any]]:
    """Studios, twin, Antigravity, GO — as agent tools, not separate screens."""
    tools = [
        ("Develop agent", "studio_develop", "POST /v1/network/agents", "Create an agent in the network/twin and run it from Work."),
        ("Ship agent", "studio_ship", "POST /v1/network/agents/ship", "Package an agent to git, mesh, PhoneAI, or desktop."),
        ("Mint twin", "twin_mint", "POST /v1/twin/mint", "Mint the account workspace + embedded CLIs + vaults on this PC."),
        ("Open twin files", "twin_open", "POST /v1/twin/open", "Open the twin folder in Explorer (their files)."),
        ("Twin vault", "twin_vault", "POST /v1/twin/vault", "Encrypt a note into the twin vault and copy it to Pocket."),
        ("Twin agent", "twin_agent", "POST /v1/twin/agent", "PhoneAI agent that talks via workspace CLIs."),
        ("Twin agent run", "twin_agent_run", "POST /v1/twin/agent/run", "Run a twin agent with PATH=bin."),
        ("Anti new chat", "anti_new", "POST /v1/phoneai/anti action=new", "New Antigravity chat on the PC from the phone."),
        ("Anti send", "anti_send", "POST /v1/phoneai/anti action=send", "Paste+send into the live Antigravity thread."),
        ("Anti continue", "anti_continue", "POST /v1/phoneai/anti action=continue", "Click Continue/Allow via WebMCP fusion."),
        ("Anti read thread", "anti_read", "POST /v1/phoneai/anti action=read", "Stream the visible Antigravity conversation."),
        ("GO plane", "go_sync", "GO sync", "Arm every live surface (desk, phone, twin, MCP) as one plane."),
        ("WebMCP scan", "webmcp_scan", "POST /v1/webmcp/scan", "Refresh the action catalog including fusion."),
        ("PhoneAI work", "phoneai_work", "POST /v1/phoneai/work", "Continue Grok/Codex/Anti from the same work loop."),
        ("New PhoneAI session", "session_new", "POST /v1/phoneai/sessions", "Mint a Pocket or PhoneAI session from a persona."),
        ("Engine catalog", "engines_list", "GET /v1/engines", "Live CLIs + internal models on this PC."),
        ("Portal stream", "portal_open", "GET /phoneai/portal", "First-class Watch/Touch of the real desktop."),
        ("Bounded shell", "shell_exec", "POST /v1/phoneai/shell", "PowerShell in Pocket/PhoneAI/sovereign workspaces."),
        ("Work harness", "harness_run", "POST /v1/phoneai/harness", "Think → shell → one engine → receipt."),
        ("Agent talk", "agent_talk", "POST /v1/phoneai/talk", "Agent mail + encrypted mesh so agents talk to each other."),
    ]
    out = []
    for name, inv, how, blurb in tools:
        out.append(
            _act(
                source="work",
                kind="function",
                name=name,
                how_agents=how,
                how_phoneai=blurb,
                invoke=inv,
            )
        )
    return out


def _from_surfaces() -> List[Dict[str, Any]]:
    try:
        from pocket.tech_atlas import APPS
    except Exception:
        APPS = []
    out = []
    for a in APPS:
        out.append(
            _act(
                source="surface",
                kind="surface",
                name=a.get("name") or a.get("id"),
                how_agents=f"open {a.get('url')}",
                how_phoneai=f"Kernel app grid opens {a.get('url')} on Pocket.",
                invoke="open_surface",
                extra={"url": a.get("url")},
            )
        )
    return out


def scan(*, url: str = "", fusion: bool = False) -> Dict[str, Any]:
    """Diffuse host + optional page/screen into the WebMCP catalog."""
    actions: List[Dict[str, Any]] = []
    actions.extend(_from_work())
    actions.extend(_from_surfaces())
    actions.extend(_from_desktop_apps())
    actions.extend(_from_phoneai())
    actions.extend(_from_engines())
    actions.extend(_from_mcp())
    if url:
        actions.extend(_from_url(url))
    if fusion:
        actions.extend(_from_fusion())
    # de-dupe by id
    seen = set()
    uniq = []
    for a in actions:
        i = a.get("id")
        if i in seen:
            continue
        seen.add(i)
        uniq.append(a)
    cat = {
        "ok": True,
        "schema": SCHEMA,
        "at": time.time(),
        "count": len(uniq),
        "url": url or "",
        "fusion": bool(fusion),
        "sources": sorted({a["source"] for a in uniq}),
        "actions": uniq,
        "doctrine": "Nothing is separate. Studios, twin, Antigravity, GO are WebMCP functions agents invoke while they work.",
    }
    CATALOG.write_text(json.dumps(cat, indent=2, default=str)[:2_000_000], encoding="utf-8")
    return cat


def catalog(*, refresh: bool = False, url: str = "", fusion: bool = False) -> Dict[str, Any]:
    if refresh or url or fusion or not CATALOG.is_file():
        return scan(url=url, fusion=fusion)
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("actions"):
            return data
    except Exception:
        pass
    return scan()


def find_actions(query: str) -> List[Dict[str, Any]]:
    q = (query or "").lower().strip()
    cat = catalog()
    if not q:
        return (cat.get("actions") or [])[:80]
    hits = []
    for a in cat.get("actions") or []:
        blob = " ".join([a.get("id", ""), a.get("name", ""), a.get("source", ""), a.get("invoke", "")]).lower()
        if q in blob:
            hits.append(a)
    return hits[:80]


def use_action(name: str, *, prompt: str = "") -> Dict[str, Any]:
    """Agents and PhoneAI call this to actually run a cataloged action."""
    hits = find_actions(name)
    if not hits:
        return {"ok": False, "error": f"no WebMCP action matching {name!r}"}
    a = hits[0]
    inv = a.get("invoke") or ""
    extra = a
    try:
        if inv == "open_app":
            from pocket.desktop import open_app

            return {"ok": True, "used": a, "result": open_app(str(a.get("app_id") or name))}
        if inv == "open_surface":
            return {"ok": True, "used": a, "open": a.get("url") or "/desk"}
        if inv == "phoneai_execute":
            from pocket.phoneai_bridge import execute, pair_auto

            sess = pair_auto(allow=True)
            return {
                "ok": True,
                "used": a,
                "result": execute({"session_id": sess.get("session_id")}, {"tool_id": a.get("tool_id"), "params": {"prompt": prompt}}),
            }
        if inv == "phoneai_work":
            from pocket.phoneai_bridge import work

            return {"ok": True, "used": a, "result": work(prompt or name, engine="auto")}
        if inv == "engine_use":
            from pocket.web_ui_engine import run_use

            return {"ok": True, "used": a, "result": run_use(str(a.get("use_id") or ""), prompt or a.get("name") or "")}
        if inv == "mcp_invoke":
            from pocket.mcp_bundle import invoke

            return {"ok": True, "used": a, "result": invoke("pocket", str(a.get("tool") or name))}
        if inv == "studio_develop":
            from pocket.agent_network import develop

            return {"ok": True, "used": a, "result": develop({"id": name, "blurb": prompt, "role": prompt or "worker"})}
        if inv == "studio_ship":
            from pocket.agent_network import ship

            aid = (prompt or name).split()[0]
            return {"ok": True, "used": a, "result": ship(aid, "git")}
        if inv == "twin_mint":
            from pocket.twin_mint import mint

            return {"ok": True, "used": a, "result": mint((prompt or "phoneai").split()[0])}
        if inv == "twin_open":
            from pocket.twin_mint import open_on_pc

            return {"ok": True, "used": a, "result": open_on_pc((prompt or "phoneai").split()[0])}
        if inv == "twin_vault":
            from pocket.twin_mint import vault_put

            return {"ok": True, "used": a, "result": vault_put("phoneai", "from-agent.md", prompt or name, to_pocket=True)}
        if inv == "twin_agent":
            from pocket.twin_mint import create_agent

            return {"ok": True, "used": a, "result": create_agent("phoneai", {"id": name, "blurb": prompt, "engine": "grok"})}
        if inv == "twin_agent_run":
            from pocket.twin_mint import run_agent

            return {"ok": True, "used": a, "result": run_agent("phoneai", (prompt or name).split()[0], prompt)}
        if inv in ("anti_new", "anti_send", "anti_continue", "anti_read"):
            from pocket.antigravity_chat import handle

            action = inv.split("_", 1)[-1]
            return {"ok": True, "used": a, "result": handle(action, prompt)}
        if inv == "go_sync":
            from pocket.go_plane import go

            return {"ok": True, "used": a, "result": go(arm_daily=False)}
        if inv == "webmcp_scan":
            return {"ok": True, "used": a, "result": scan(fusion=True)}
        if inv == "session_new":
            from pocket.agent_runtime import create_phoneai_session

            return {"ok": True, "used": a, "result": create_phoneai_session(persona_id=(prompt or "researcher").split()[0], kind="both")}
        if inv == "agent_talk":
            from pocket.agent_runtime import talk

            parts = (prompt or "").split(" ", 2)
            frm = parts[0] if parts else "phoneai"
            to = parts[1] if len(parts) > 1 else "grok"
            body = parts[2] if len(parts) > 2 else name
            return {"ok": True, "used": a, "result": talk(frm, to, body)}
        if inv in ("web_ui_act", "web_ui_open", "web_ui_browse"):
            from pocket.web_ui_engine import act, browse, open_url

            if inv == "web_ui_browse" or (a.get("href") or "").startswith("http"):
                fn = browse if inv == "web_ui_browse" else open_url
                return {"ok": True, "used": a, "result": fn(a.get("href") or prompt or "")}
            return {"ok": True, "used": a, "result": act(prompt or a.get("name") or "")}
    except Exception as e:
        return {"ok": False, "used": a, "error": str(e)[:240]}
    return {"ok": True, "used": a, "note": "cataloged; invoke recorded", "extra": extra}


def html() -> str:
    cat = catalog()
    rows = []
    for a in (cat.get("actions") or [])[:250]:
        rows.append(
            f"<tr><td>{a.get('source')}</td><td>{a.get('kind')}</td><td>{a.get('name')}</td>"
            f"<td>{a.get('how_agents')}</td><td>{a.get('how_phoneai')}</td></tr>"
        )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>WebMCP catalog</title>
<style>
body{{margin:0;font-family:ui-sans-serif,system-ui;background:#07070b;color:#e4e4e7}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px 16px 80px}}
h1{{letter-spacing:-.04em}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th,td{{border-bottom:1px solid rgba(255,255,255,.08);padding:8px 6px;vertical-align:top}}
th{{color:#34d399;text-align:left}}
a{{color:#10a37f}}
.muted{{color:#a1a1aa}}
</style></head>
<body><div class="wrap">
<p><a href="/phoneai">PhoneAI</a> · <a href="/phoneai/work">Work</a> · <a href="/desk">Desk</a></p>
<h1>WebMCP</h1>
<p class="muted">Diffusion catalog: {cat.get("count")} actions from {", ".join(cat.get("sources") or [])}. Agents invoke; PhoneAI reads the same list.</p>
<table>
<thead><tr><th>Source</th><th>Kind</th><th>Name</th><th>Agents</th><th>PhoneAI</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div></body></html>
"""
