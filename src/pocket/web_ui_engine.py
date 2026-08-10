"""Website interface engine — Python agents drive real web UIs via MCP.

Models and engines call these from skills / MCP / agent tools loop:

  web_ui_open   → open URL in signed-in Edge (host browser)
  web_ui_sense  → Fusion sense of what's on screen / page
  web_ui_act    → click / type / navigate when control is armed
  web_ui_fetch  → headless fetch page text (no browser tab)
  web_ui_search → host web search
  python_engine → run a named Python agent/engine on a prompt

Doctrine:
  · MCP tools are Python — agents never need a user to click through MCP UIs
  · Website interfaces = our remote browser + browser_mode + life web_browse
  · Explicit act only — never auto-pay
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

SCHEMA = "pocket.web_ui_engine.v1"
PRODUCT = "POCKET Web UI Engine"


def status() -> Dict[str, Any]:
    rb = {}
    try:
        from pocket.remote_browser import status as rb_status

        rb = rb_status()
    except Exception as e:
        rb = {"ok": False, "error": str(e)[:100]}
    return {
        "ok": True,
        "product": PRODUCT,
        "schema": SCHEMA,
        "remote_browser": rb.get("ok"),
        "tools": [
            "web_ui_open",
            "web_ui_sense",
            "web_ui_act",
            "web_ui_fetch",
            "web_ui_search",
            "web_ui_browse",
            "python_engine",
            "python_engines_list",
        ],
        "engines": list_engines().get("engines") or [],
        "doctrine": "Python MCP drives website interfaces on the host — models use engines, not user tabs.",
    }


def list_engines() -> Dict[str, Any]:
    """Named Python agents/engines models can invoke."""
    engines = [
        {"id": "browser", "module": "pocket.browser_mode", "for": "Edge · X · Copilot · lookups"},
        {"id": "remote_browser", "module": "pocket.remote_browser", "for": "Open · sense · act · benchmark"},
        {"id": "web_research", "module": "pocket.web_research", "for": "search_web · fetch_url"},
        {"id": "life_ops", "module": "pocket.life_ops", "for": "food · flights · shop · reserve"},
        {"id": "navigator", "module": "pocket.life_ops", "for": "alias of life web actions"},
        {"id": "assist", "module": "pocket.digital_assistant", "for": "route digital life intents"},
        {"id": "scribe", "module": "pocket.agent_mail", "for": "agent email · inbox · send"},
        {"id": "mail", "module": "pocket.pocket_mail", "for": "official SMTP mail"},
        {"id": "genetic", "module": "pocket.internal_models", "for": "internal models genetic flow"},
        {"id": "ghost", "module": "pocket.ghost_math", "for": "pure math / hash"},
        {"id": "guppy", "module": "pocket.guppy", "for": "desk actuator fish"},
        {"id": "world", "module": "pocket.world_model", "for": "memory / facts"},
        {"id": "auro", "module": "pocket.auro14b_bridge", "for": "local LMR"},
        {"id": "mcp", "module": "pocket.mcp_bundle", "for": "invoke any MCP tool"},
        {"id": "integrations", "module": "pocket.integrations_exec", "for": "execute integrations"},
        {"id": "loomgraph", "module": "pocket.loomgraph", "for": "graph loop harness"},
        {"id": "keep", "module": "pocket.keep_agents", "for": "KEEP background agents"},
        {"id": "coding_swarm", "module": "pocket.coding_swarm", "for": "multi-agent code"},
        {"id": "screen", "module": "pocket.screen_share", "for": "Fusion sense · control"},
        {"id": "vcomp", "module": "pocket.virtual_computer", "for": "virtual computer shell"},
    ]
    return {"ok": True, "count": len(engines), "engines": engines}


def open_url(url: str = "", *, profile: str = "Default") -> Dict[str, Any]:
    """Open a website interface in signed-in Edge."""
    u = (url or "").strip()
    if not u:
        return {"ok": False, "error": "url required"}
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    try:
        from pocket.remote_browser import open_url as rb_open

        r = rb_open(u, profile=profile)
        r["tool"] = "web_ui_open"
        r["engine"] = "remote_browser"
        return r
    except Exception:
        pass
    try:
        from pocket.browser_mode import open_edge_url

        r = open_edge_url(u, profile=profile)
        if isinstance(r, dict):
            r.setdefault("ok", True)
            r["tool"] = "web_ui_open"
            r["engine"] = "browser_mode"
            r["url"] = u
            return r
        return {"ok": True, "tool": "web_ui_open", "engine": "browser_mode", "url": u, "result": r}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "tool": "web_ui_open"}


def sense(*, agent: str = "web_ui") -> Dict[str, Any]:
    """Sense the current website / screen UI for agents."""
    try:
        from pocket.remote_browser import sense as rb_sense

        r = rb_sense(agent=agent)
        if isinstance(r, dict):
            r["tool"] = "web_ui_sense"
            return r
    except TypeError:
        try:
            from pocket.remote_browser import sense as rb_sense

            r = rb_sense()
            if isinstance(r, dict):
                r["tool"] = "web_ui_sense"
                r["agent"] = agent
                return r
        except Exception as e:
            err = str(e)[:120]
    except Exception as e:
        err = str(e)[:120]
    else:
        err = "sense failed"
    try:
        from pocket.screen_share import fusion_context

        r = fusion_context(agent=agent)
        r["tool"] = "web_ui_sense"
        r["engine"] = "screen_share"
        return r
    except Exception as e2:
        return {"ok": False, "error": f"{err}; {e2}"[:240], "tool": "web_ui_sense"}


def act(action: str = "sense", **kwargs: Any) -> Dict[str, Any]:
    """Act on website interface (click-by-name / control when armed)."""
    agent = kwargs.pop("agent", "web_ui") or "web_ui"
    a = (action or "sense").strip().lower()
    try:
        from pocket.remote_browser import act as rb_act

        try:
            r = rb_act(a, agent=agent, **kwargs)
        except TypeError:
            r = rb_act(a, **kwargs)
        if isinstance(r, dict):
            r["tool"] = "web_ui_act"
            return r
    except Exception:
        pass
    try:
        from pocket.screen_share import act_for_agent

        r = act_for_agent(a, agent=agent, **kwargs)
        r["tool"] = "web_ui_act"
        r["engine"] = "screen_share"
        return r
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)[:200],
            "tool": "web_ui_act",
            "hint": "Arm screen Control or VComp for precise acts",
        }


def fetch(url: str = "", *, max_chars: int = 14000) -> Dict[str, Any]:
    """Headless fetch — no browser tab."""
    from pocket.web_research import fetch_url

    r = fetch_url(url, max_chars=max_chars)
    if isinstance(r, dict):
        r["tool"] = "web_ui_fetch"
        r["engine"] = "web_research"
    return r


def search(query: str = "", *, max_results: int = 6) -> Dict[str, Any]:
    from pocket.web_research import search_web

    r = search_web(query, max_results=max_results)
    if isinstance(r, dict):
        r["tool"] = "web_ui_search"
        r["engine"] = "web_research"
    return r


def browse(url: str = "", *, profile: str = "Default") -> Dict[str, Any]:
    """Open + return brief sense (website interface session start)."""
    opened = open_url(url, profile=profile)
    time.sleep(0.4)
    sensed = sense(agent="web_ui")
    return {
        "ok": bool(opened.get("ok")),
        "tool": "web_ui_browse",
        "open": opened,
        "sense": {
            "ok": sensed.get("ok"),
            "brief": (sensed.get("brief") or sensed.get("text") or sensed.get("summary") or "")[:1200],
            "keys": list(sensed.keys())[:20],
        },
        "url": url,
        "message": "Website opened on host browser — model can sense/act via MCP",
    }


def run_python_engine(
    engine: str,
    prompt: str = "",
    *,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a named Python agent/engine so models can use host capabilities."""
    eid = (engine or "").strip().lower().replace("-", "_")
    p = (prompt or "").strip()
    params = dict(params or {})
    t0 = time.perf_counter()

    try:
        if eid in ("browser", "browser_mode"):
            from pocket.browser_mode import handle as bm_handle

            if hasattr(bm_handle, "__call__"):
                r = bm_handle(p)
            else:
                from pocket import browser_mode as bm

                r = bm.open_edge_url(p) if p.startswith("http") else {"ok": True, "help": getattr(bm, "HELP", "")[:800]}
            return _wrap(eid, r, t0)

        if eid in ("remote_browser", "remote"):
            if p.startswith("http") or "." in p.split()[0] if p else False:
                return _wrap(eid, open_url(p), t0)
            return _wrap(eid, sense(), t0)

        if eid in ("web_research", "research", "web"):
            if p.startswith("http"):
                return _wrap(eid, fetch(p), t0)
            return _wrap(eid, search(p), t0)

        if eid in ("web_ui", "website", "webui"):
            if p.startswith("http") or p.startswith("www."):
                return _wrap(eid, browse(p), t0)
            return _wrap(eid, search(p), t0)

        if eid in ("life_ops", "life", "navigator"):
            from pocket.life_ops import classify_and_run, status as life_status

            if not p:
                return _wrap(eid, life_status() if callable(life_status) else {"ok": True}, t0)
            try:
                return _wrap(eid, classify_and_run(p, **params), t0)
            except TypeError:
                try:
                    from pocket.life_ops import run as life_run

                    return _wrap(eid, life_run(p), t0)
                except Exception as e:
                    return _wrap(eid, {"ok": False, "error": str(e)[:200]}, t0)

        if eid in ("assist", "digital_assistant", "assistant"):
            from pocket.digital_assistant import route

            return _wrap(eid, route(p, **params) if params else route(p), t0)

        if eid in ("scribe", "agent_mail", "mail_agent"):
            from pocket import agent_mail as am

            if p.lower().startswith("inbox"):
                agent = params.get("agent") or "assist"
                return _wrap(eid, am.inbox(agent), t0)
            if p.lower().startswith("send ") or params.get("to"):
                return _wrap(
                    eid,
                    am.send(
                        from_agent=params.get("from") or params.get("from_agent") or "scribe",
                        to=params.get("to") or "",
                        subject=params.get("subject") or "POCKET agent note",
                        body=params.get("body") or p,
                    ),
                    t0,
                )
            return _wrap(eid, am.status(), t0)

        if eid in ("mail", "pocket_mail"):
            from pocket.pocket_mail import status as ms, draft

            if params.get("to") or params.get("body"):
                return _wrap(
                    eid,
                    draft(
                        to=params.get("to") or "",
                        subject=params.get("subject") or "POCKET",
                        body=params.get("body") or p,
                    ),
                    t0,
                )
            return _wrap(eid, ms(), t0)

        if eid in ("genetic", "genetic_flow", "internal_models"):
            from pocket.internal_models import run_genetic_flow, list_models

            if not p:
                return _wrap(eid, {"ok": True, "models": list_models()}, t0)
            return _wrap(
                eid,
                run_genetic_flow(
                    p,
                    generations=int(params.get("generations") or 2),
                    population=int(params.get("population") or 4),
                ),
                t0,
            )

        if eid in ("ghost", "ghost_math"):
            try:
                from pocket.internal_models import express_one

                er = express_one("ghost", p or "phi 1")
                if isinstance(er, dict):
                    return _wrap(eid, er, t0)
                # ModelResult-like
                return _wrap(
                    eid,
                    {
                        "ok": True,
                        "text": getattr(er, "text", None) or str(er),
                        "engine": getattr(er, "engine", "ghost"),
                    },
                    t0,
                )
            except Exception as e:
                return _wrap(eid, {"ok": False, "error": str(e)[:200]}, t0)

        if eid in ("guppy",):
            from pocket.internal_models import express_one

            er = express_one("guppy", p or "status")
            return _wrap(eid, er if isinstance(er, dict) else {"ok": True, "text": str(er)}, t0)

        if eid in ("world", "world_model"):
            from pocket.internal_models import express_one

            er = express_one("world", p or "brief")
            return _wrap(eid, er if isinstance(er, dict) else {"ok": True, "text": str(er)}, t0)

        if eid in ("auro", "auro14b"):
            try:
                from pocket.auro14b_bridge import run_auro_job

                text, err, eng = run_auro_job(p or "status briefly")
                return _wrap(eid, {"ok": not bool(err), "text": text, "error": err, "engine": eng}, t0)
            except Exception as e:
                return _wrap(eid, {"ok": False, "error": str(e)[:200]}, t0)

        if eid in ("mcp", "mcp_bundle"):
            from pocket.mcp_bundle import invoke, catalog

            if not p:
                return _wrap(eid, catalog(), t0)
            server = params.get("server") or "pocket"
            tool = params.get("tool") or p.split()[0]
            return _wrap(eid, invoke(server, tool, **{k: v for k, v in params.items() if k not in ("server", "tool")}), t0)

        if eid in ("integrations", "integrations_exec"):
            from pocket.integrations_exec import execute

            return _wrap(eid, execute(params.get("id") or p, **params), t0)

        if eid in ("loomgraph", "loom"):
            from pocket.loomgraph import run as loom_run

            return _wrap(eid, loom_run(p or params.get("goal") or "status"), t0)

        if eid in ("keep", "keep_agents"):
            from pocket.keep_agents import status as keep_status

            return _wrap(eid, keep_status(), t0)

        if eid in ("coding_swarm", "swarm"):
            from pocket.coding_swarm import run as swarm_run

            try:
                return _wrap(eid, swarm_run(p), t0)
            except TypeError:
                return _wrap(eid, {"ok": True, "note": "use desk coding_swarm mode", "prompt": p[:200]}, t0)

        if eid in ("screen", "screen_share"):
            from pocket.screen_share import fusion_context

            return _wrap(eid, fusion_context(agent=params.get("agent") or "python_engine"), t0)

        if eid in ("vcomp", "virtual_computer"):
            from pocket import virtual_computer as vc

            if params.get("command") or p.startswith("!"):
                cmd = params.get("command") or p.lstrip("!").strip()
                return _wrap(eid, vc.shell(cmd), t0)
            return _wrap(eid, vc.open_computer(label=params.get("label") or "engine"), t0)

        return {
            "ok": False,
            "error": f"unknown engine {engine}",
            "available": [e["id"] for e in list_engines()["engines"]],
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
    except Exception as e:
        return {
            "ok": False,
            "engine": eid,
            "error": str(e)[:300],
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        }


def _wrap(engine: str, result: Any, t0: float) -> Dict[str, Any]:
    if not isinstance(result, dict):
        result = {"ok": True, "result": result}
    result.setdefault("ok", True)
    result["engine"] = engine
    result["python"] = True
    result["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    result["schema"] = SCHEMA
    return result
