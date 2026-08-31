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

# 20 named uses — agents pick a use id so the right tool/engine runs
ENGINE_USES: List[Dict[str, Any]] = [
    {
        "id": "research_topic",
        "title": "Research a topic",
        "tool": "web_ui_search",
        "engine": "web_research",
        "improves": "Fast host search without opening a browser tab",
        "example": "edge multi-agent hosts 2026",
    },
    {
        "id": "read_page",
        "title": "Read a page (headless)",
        "tool": "web_ui_fetch",
        "engine": "web_research",
        "improves": "Pull page text for summarization / evidence",
        "example": "https://example.com",
    },
    {
        "id": "open_site",
        "title": "Open a website (signed-in Edge)",
        "tool": "web_ui_open",
        "engine": "remote_browser",
        "improves": "Use real cookies/profile for authenticated sites",
        "example": "https://github.com",
    },
    {
        "id": "browse_sense",
        "title": "Open + sense website UI",
        "tool": "web_ui_browse",
        "engine": "web_ui",
        "improves": "Start a website session and see what's on screen",
        "example": "https://news.ycombinator.com",
    },
    {
        "id": "sense_ui",
        "title": "Sense open UI",
        "tool": "web_ui_sense",
        "engine": "screen",
        "improves": "Fusion/OCR brief of current page or desk",
        "example": "(current screen)",
    },
    {
        "id": "act_ui",
        "title": "Act on website UI",
        "tool": "web_ui_act",
        "engine": "remote_browser",
        "improves": "Click/type when Control or VComp is armed (never auto-pay)",
        "example": "click Save",
    },
    {
        "id": "life_ops",
        "title": "Life ops (food/flight/shop/reserve)",
        "tool": "python_engine",
        "engine": "life_ops",
        "improves": "Route real-life requests; user always confirms payment",
        "example": "find flights SFO to JFK next Friday",
    },
    {
        "id": "assist_route",
        "title": "Digital assistant route",
        "tool": "python_engine",
        "engine": "assist",
        "improves": "Pick the right life/coding engine for free text",
        "example": "draft an email reschedule",
    },
    {
        "id": "agent_mail",
        "title": "Agent Mail inbox/send",
        "tool": "python_engine",
        "engine": "scribe",
        "improves": "Our own agents.pocket.local accounts + inboxes",
        "example": "inbox",
    },
    {
        "id": "genetic_evolve",
        "title": "Genetic flow over models",
        "tool": "python_engine",
        "engine": "genetic",
        "improves": "Evolve which internal models run for a goal",
        "example": "hash the plan and next steps",
    },
    {
        "id": "math_local",
        "title": "Local math / ghost",
        "tool": "python_engine",
        "engine": "ghost",
        "improves": "Zero-token deterministic math / hash / phi",
        "example": "phi 8",
    },
    {
        "id": "memory_world",
        "title": "World-model memory",
        "tool": "python_engine",
        "engine": "world",
        "improves": "Facts and memory brief from host world model",
        "example": "brief",
    },
    {
        "id": "local_llm",
        "title": "Local LMR (Auro)",
        "tool": "python_engine",
        "engine": "auro",
        "improves": "On-host meaning model without cloud round-trip",
        "example": "explain local agents simply",
    },
    {
        "id": "mcp_tool",
        "title": "Invoke MCP tool",
        "tool": "python_engine",
        "engine": "mcp",
        "improves": "Any pocket MCP tool headlessly",
        "example": "mail_accounts",
    },
    {
        "id": "integration",
        "title": "Run integration",
        "tool": "python_engine",
        "engine": "integrations",
        "improves": "Open/execute catalog integrations (Discord, etc.)",
        "example": "discord",
    },
    {
        "id": "loom_loop",
        "title": "LOOMGRAPH loop",
        "tool": "python_engine",
        "engine": "loomgraph",
        "improves": "See the graph · run the multi-step loop",
        "example": "ship desk polish loop",
    },
    {
        "id": "coding_swarm",
        "title": "Coding swarm",
        "tool": "python_engine",
        "engine": "coding_swarm",
        "improves": "Multi-agent code + pixel artifacts",
        "example": "add health endpoint tests",
    },
    {
        "id": "build_model",
        "title": "Build a platform model",
        "tool": "python_engine",
        "engine": "model_forge",
        "improves": "Create a new internal model and register it when missing",
        "example": "build a math formula model for ROI",
    },
    {
        "id": "use_built_model",
        "title": "Express a built model",
        "tool": "python_engine",
        "engine": "express_model",
        "improves": "Run a forged/registered model by id",
        "example": "model=user-math-helper goal=phi 3",
    },
    {
        "id": "vcomp_shell",
        "title": "Virtual computer shell",
        "tool": "python_engine",
        "engine": "vcomp",
        "improves": "Isolated shell on host virtual computer",
        "example": "!echo ok",
    },
    {
        "id": "phone_call",
        "title": "Agent phone call (virtual number)",
        "tool": "call_dial",
        "engine": "call_dial",
        "improves": "Dial from agent +p virtual line (softphone; PSTN if Twilio set)",
        "example": "call assist about status",
    },
]


def list_uses() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.engine_uses.v1",
        "count": len(ENGINE_USES),
        "uses": ENGINE_USES,
        "doctrine": (
            "Pick a use id so agents call the right web_ui_* or python_engine. "
            "When no model fits, use build_model then use_built_model."
        ),
    }


def pick_use(goal: str) -> Dict[str, Any]:
    """Rank ENGINE_USES for a free-text goal."""
    low = (goal or "").lower()
    scored = []
    for u in ENGINE_USES:
        score = 0.05
        for token in (u["id"] + " " + u["title"] + " " + u.get("improves", "")).lower().split():
            if len(token) > 3 and token in low:
                score += 0.12
        # hard hints
        if u["id"] == "read_page" and low.startswith("http"):
            score += 0.8
        if u["id"] == "open_site" and ("open " in low or "signed" in low):
            score += 0.4
        if u["id"] == "research_topic" and any(w in low for w in ("search", "research", "look up", "what is")):
            score += 0.45
        if u["id"] == "agent_mail" and any(w in low for w in ("inbox", "email", "mail", "send message")):
            score += 0.5
        if u["id"] == "build_model" and (
            any(w in low for w in ("build model", "create model", "forge model", "new model", "forge a model"))
            or ("build" in low and "model" in low)
            or ("create" in low and "model" in low)
        ):
            score += 0.85
        if u["id"] == "genetic_evolve" and any(w in low for w in ("genetic", "evolve", "internal model")):
            score += 0.55
        # demote pure math when user is building a model
        if u["id"] == "math_local" and any(w in low for w in ("phi", "hash", "calculate", "math")):
            score += 0.4
            if "model" in low and ("build" in low or "create" in low or "forge" in low):
                score -= 0.35
        scored.append({**u, "score": round(min(1.0, score), 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    best = scored[0] if scored else None
    return {"ok": True, "goal": (goal or "")[:200], "best": best, "ranked": scored[:8]}


def run_use(use_id: str, prompt: str = "", *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute one of the 20 named uses."""
    uid = (use_id or "").strip().lower().replace("-", "_")
    use = next((u for u in ENGINE_USES if u["id"] == uid), None)
    if not use:
        return {"ok": False, "error": f"unknown use {use_id}", "uses": [u["id"] for u in ENGINE_USES]}
    p = (prompt or "").strip()
    params = dict(params or {})
    tool = use["tool"]
    engine = use["engine"]

    if tool == "web_ui_search":
        return {**search(p or params.get("query") or ""), "use": uid}
    if tool == "web_ui_fetch":
        return {**fetch(p or params.get("url") or ""), "use": uid}
    if tool == "web_ui_open":
        return {**open_url(p or params.get("url") or ""), "use": uid}
    if tool == "web_ui_browse":
        return {**browse(p or params.get("url") or ""), "use": uid}
    if tool == "web_ui_sense":
        return {**sense(agent=params.get("agent") or "web_ui"), "use": uid}
    if tool == "web_ui_act":
        return {**act(p or params.get("action") or "sense", **params), "use": uid}
    if tool in ("call_dial", "dial") or engine in ("call_dial", "phone_call"):
        from pocket.agent_calls import dial, assign_number

        to = params.get("to") or params.get("number") or ""
        if not to and p:
            # "call assist about X" or just agent name
            parts = p.strip().split()
            if parts and parts[0].lower() in ("call", "dial"):
                parts = parts[1:]
            to = parts[0] if parts else "assist"
            purpose = " ".join(parts[1:]) if len(parts) > 1 else p
        else:
            purpose = p or params.get("purpose") or ""
        assign_number(params.get("from") or params.get("from_agent") or "phone_agent")
        return {
            **dial(
                from_agent=str(params.get("from") or params.get("from_agent") or "phone_agent"),
                to=str(to),
                purpose=str(purpose or params.get("purpose") or ""),
                mode=str(params.get("mode") or "soft"),
            ),
            "use": uid,
        }
    # python_engine path
    if engine == "model_forge":
        return {**run_python_engine("model_forge", p, params=params), "use": uid}
    if engine == "express_model":
        mid = params.get("model") or params.get("model_id") or ""
        if not mid and "model=" in p:
            # parse model=id goal=...
            import re as _re

            m = _re.search(r"model=([a-zA-Z0-9._\-]+)", p)
            if m:
                mid = m.group(1)
                p = _re.sub(r"model=[a-zA-Z0-9._\-]+", "", p).strip()
                p = _re.sub(r"^goal=", "", p).strip()
        return {**run_python_engine("express_model", p, params={**params, "model": mid}), "use": uid}
    return {**run_python_engine(engine, p, params=params), "use": uid}


def status() -> Dict[str, Any]:
    rb = {}
    try:
        from pocket.remote_browser import status as rb_status

        rb = rb_status()
    except Exception as e:
        rb = {"ok": False, "error": str(e)[:100]}
    built_n = 0
    try:
        from pocket.model_forge import list_built

        built_n = list_built().get("count") or 0
    except Exception:
        pass
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
            "engine_uses",
            "engine_use",
            "model_build",
            "model_list_built",
        ],
        "uses": len(ENGINE_USES),
        "built_models": built_n,
        "engines": list_engines().get("engines") or [],
        "doctrine": (
            "Python MCP drives website interfaces — models use engines, not user tabs. "
            "20 uses map goals → tools. Agents build models via model_forge when needed."
        ),
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
        {"id": "model_forge", "module": "pocket.model_forge", "for": "build + register platform models"},
        {"id": "express_model", "module": "pocket.internal_models", "for": "express any registered model id"},
        {"id": "engine_uses", "module": "pocket.web_ui_engine", "for": "list/run the 20 named uses"},
    ]
    # include built models as engines
    try:
        from pocket.model_forge import list_built

        for m in (list_built().get("models") or [])[:30]:
            engines.append(
                {
                    "id": m.get("id"),
                    "module": "pocket.model_forge",
                    "for": f"built {m.get('kind')}: {m.get('description') or m.get('name')}",
                    "built": True,
                }
            )
    except Exception:
        pass
    return {"ok": True, "count": len(engines), "engines": engines, "uses": len(ENGINE_USES)}


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
        # --- Model forge + 20 uses + express any registered model ---
        if eid in ("engine_uses", "uses", "list_uses"):
            return _wrap(eid, list_uses(), t0)
        if eid in ("engine_use", "run_use"):
            uid = params.get("use") or params.get("use_id") or (p.split()[0] if p else "")
            rest = p
            if p and p.split()[0].replace("-", "_") == uid.replace("-", "_"):
                rest = p.split(None, 1)[1] if len(p.split()) > 1 else ""
            return _wrap(eid, run_use(uid, rest or params.get("prompt") or "", params=params), t0)
        if eid in ("model_forge", "forge", "build_model"):
            from pocket import model_forge as mf

            low = p.lower()
            if low.startswith("list") or low == "status":
                return _wrap(eid, mf.list_built() if "list" in low else mf.status(), t0)
            if low.startswith("suggest"):
                goal = p.split(None, 1)[1] if " " in p else params.get("goal") or ""
                return _wrap(eid, mf.suggest_from_goal(goal), t0)
            if low.startswith("register"):
                mid = params.get("model") or (p.split()[1] if len(p.split()) > 1 else "")
                return _wrap(eid, mf.register_built(mid), t0)
            # build from params or suggest+build
            if params.get("kind") or params.get("model_id") or params.get("name"):
                return _wrap(
                    eid,
                    mf.build_model(
                        model_id=str(params.get("model_id") or params.get("id") or ""),
                        name=str(params.get("name") or ""),
                        kind=str(params.get("kind") or "template"),
                        description=str(params.get("description") or p or ""),
                        tags=params.get("tags") if isinstance(params.get("tags"), list) else None,
                        template=str(params.get("template") or ""),
                        rules=params.get("rules") if isinstance(params.get("rules"), list) else None,
                        default=str(params.get("default") or ""),
                        formula=str(params.get("formula") or ""),
                        wrap_engine=str(params.get("wrap_engine") or ""),
                        wrap_params=params.get("wrap_params") if isinstance(params.get("wrap_params"), dict) else None,
                        code=str(params.get("code") or ""),
                        system=str(params.get("system") or ""),
                        fit_keywords=params.get("fit_keywords") if isinstance(params.get("fit_keywords"), list) else None,
                        register_now=params.get("register_now", True) is not False,
                        author=str(params.get("author") or "agent"),
                    ),
                    t0,
                )
            # free text → suggest then build
            sug = mf.suggest_from_goal(p or "general specialist")
            bp = (sug.get("suggestion") or {}) if sug.get("ok") else {}
            if bp:
                return _wrap(
                    eid,
                    mf.build_model(
                        model_id=str(bp.get("model_id") or ""),
                        name=str(bp.get("name") or ""),
                        kind=str(bp.get("kind") or "template"),
                        description=str(bp.get("description") or ""),
                        tags=bp.get("tags"),
                        template=str(bp.get("template") or ""),
                        rules=bp.get("rules"),
                        default=str(bp.get("default") or ""),
                        formula=str(bp.get("formula") or ""),
                        wrap_engine=str(bp.get("wrap_engine") or ""),
                        code=str(bp.get("code") or ""),
                        system=str(bp.get("system") or ""),
                        fit_keywords=bp.get("fit_keywords"),
                        register_now=True,
                        author="agent-auto",
                    ),
                    t0,
                )
            return _wrap(eid, mf.status(), t0)

        if eid in ("express_model", "express"):
            from pocket.internal_models import express_one

            mid = params.get("model") or params.get("model_id") or params.get("id") or ""
            er = express_one(str(mid), p or params.get("goal") or "status")
            if hasattr(er, "as_dict"):
                return _wrap(eid, er.as_dict(), t0)
            return _wrap(eid, er if isinstance(er, dict) else {"ok": True, "text": str(er)}, t0)

        # built model id as engine
        if eid.startswith("user-") or eid.startswith("m-"):
            from pocket.internal_models import express_one

            er = express_one(eid, p or "status")
            if hasattr(er, "as_dict"):
                return _wrap(eid, er.as_dict(), t0)
            return _wrap(eid, er if isinstance(er, dict) else {"ok": True, "text": str(er)}, t0)

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
