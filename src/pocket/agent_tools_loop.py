"""Host tool loop — agents actually run POCKET skills before/with the LLM.

Without this, agents only chat about tools. With it, matching intents execute
real host skills (life ops, screenshot, screen sense, platform map, open apps,
web search, IoT, etc.) and results are injected into the job prompt.

All chat agents (Assist, Auro, Muse, Aria, coding modes) go through enrich_prompt.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

# (regex, skill_id, params factory or None)
# Order matters: more specific life intents before generic web/platform.
_TOOL_RULES: List[Tuple[re.Pattern, str, Optional[Dict[str, Any]]]] = [
    # --- Discover / platform ---
    (
        re.compile(
            r"\b(platform map|list skills|what can (you|agents) do|capability map|"
            r"what skills|skill catalog|tools catalog|embedded tools)\b",
            re.I,
        ),
        "list_skills",
        None,
    ),
    (re.compile(r"\b(platform map|coherent platform|where is everything)\b", re.I), "platform_map", None),
    (
        re.compile(
            r"\b(what (are )?protocols|list protocols|protocol(s)? (map|catalog|status|health)|"
            r"ten major protocols|10 protocols|major protocols)\b",
            re.I,
        ),
        "protocols_map",
        None,
    ),
    (re.compile(r"\b(protocol status|protocols healthy|protocol health)\b", re.I), "protocols_status", None),
    (
        re.compile(
            r"\b(who are you|who am i talking to|what is pocket|what is this|"
            r"are you (chatgpt|claude|grok)|your identity|pocket identity)\b",
            re.I,
        ),
        "pocket_identity",
        None,
    ),
    # Explicit RAH mention → execute (not just plan)
    (
        re.compile(
            r"\b(recursive agent harness|run rah|rah fan-?out|harness recursion|"
            r"parallel sub-?harness|fan ?out harnesses)\b",
            re.I,
        ),
        "rah_run",
        None,
    ),
    # Implicit large parallel work — agents auto-select RAH (user need not say RAH)
    (
        re.compile(
            r"\b(audit|scan|review)\b.{0,40}\b(every|all|each|entire)\b.{0,40}"
            r"\b(endpoint|route|api|module|package|file|service|auth)\b",
            re.I,
        ),
        "rah_run",
        None,
    ),
    (
        re.compile(
            r"\b(every|all|each)\b.{0,24}\b(endpoint|api route|module|package)\b.{0,40}"
            r"\b(auth|security|missing|audit)\b",
            re.I,
        ),
        "rah_run",
        None,
    ),
    (
        re.compile(
            r"\b(port|migrate|rewrite)\b.{0,40}\b(entire|whole|all|codebase|every)\b",
            re.I,
        ),
        "rah_run",
        None,
    ),
    (
        re.compile(
            r"\b(large-?scale|massive|bulk|fleet)\b.{0,30}\b(audit|refactor|migration|scan)\b",
            re.I,
        ),
        "rah_run",
        None,
    ),
    (re.compile(r"\b(habitat|agent floor|who.?s on the floor|residents)\b", re.I), "habitat_status", None),
    (re.compile(r"\b(find feature|where is|how do i open)\b", re.I), "find_feature", None),
    (re.compile(r"\b(list workers|worker status|subagents|list agents)\b", re.I), "list_agents", None),
    (re.compile(r"\b(sovereign|remote browser status|our stack)\b", re.I), "sovereign", None),
    (re.compile(r"\b(computing clouds|our clouds)\b", re.I), "computing_clouds", None),
    (
        re.compile(
            r"\b(hit go|press go|start go|go plane|arm (the )?workflows|"
            r"what('?s| is) working|active states|working workflows|"
            r"sync (the )?(lab|stack)|go status)\b",
            re.I,
        ),
        "go",
        None,
    ),
    (re.compile(r"\b(go state|go board|live board)\b", re.I), "go_state", None),
    (
        re.compile(
            r"\b(power do|run (this |the )?goal|do it on (the )?host|"
            r"morning seatbelt|run (a )?multi[- ]?workflow|use power)\b",
            re.I,
        ),
        "power_do",
        None,
    ),
    (re.compile(r"\b(vs theirs|beat (chatgpt|claude|them)|why (are )?we better)\b", re.I), "power_vs", None),
    (
        re.compile(
            r"\b(100 workflows|multi workflows|list workflows|workflow catalog)\b",
            re.I,
        ),
        "multi_workflows",
        None,
    ),
    (re.compile(r"\b(mcp catalog|list mcp|embedded mcp|200 tools)\b", re.I), "mcp_catalog", None),
    (re.compile(r"\b(integrations|opentable|doordash catalog|50 integrations|54 integrations)\b", re.I), "integrations_list", None),
    (
        re.compile(
            r"\b(loomgraph|run (the )?graph|graph loop|orchestrate(d)? (with )?loom|"
            r"see the graph|control loop|playbook graph)\b",
            re.I,
        ),
        "loomgraph_run",
        None,
    ),
    (re.compile(r"\b(loomgraph catalog|list (loomgraph )?graphs|graph playbooks)\b", re.I), "loomgraph_catalog", None),
    (re.compile(r"\b(open discord|launch discord|start discord)\b", re.I), "integrations_execute", {"id": "discord"}),
    (re.compile(r"\b(open slack|launch slack)\b", re.I), "integrations_execute", {"id": "slack"}),
    (re.compile(r"\b(open teams|launch teams)\b", re.I), "integrations_execute", {"id": "teams"}),
    (re.compile(r"\b(open zoom|launch zoom)\b", re.I), "integrations_execute", {"id": "zoom"}),
    (re.compile(r"\b(open spotify|launch spotify)\b", re.I), "integrations_execute", {"id": "spotify"}),
    (re.compile(r"\b(open notion|launch notion)\b", re.I), "integrations_execute", {"id": "notion"}),
    (re.compile(r"\bintegrations?\s+(ready|readiness|status|smoke)\b", re.I), "integrations_readiness", None),
    # --- Everyday life ---
    (
        re.compile(
            r"\b(life skills|life catalog|everyday life|what can you (order|book|shop)|"
            r"food flights shop|digital life)\b",
            re.I,
        ),
        "life_catalog",
        None,
    ),
    (
        re.compile(
            r"\b(order food|food delivery|deliver|doordash|uber ?eats|grubhub|"
            r"order (me )?(pizza|sushi|thai|chinese|burger|tacos|coffee)|"
            r"get (me )?(food|dinner|lunch) delivered|hungry)\b",
            re.I,
        ),
        "food_order",
        None,
    ),
    (
        re.compile(
            r"\b(flight|flights|fly to|fly from|airfare|airline|book (a )?flight|"
            r"google flights|kayak|expedia|round ?trip|one way ticket)\b",
            re.I,
        ),
        "flight_search",
        None,
    ),
    (
        re.compile(
            r"\b(shop|shopping|amazon|walmart|target|best buy|ebay|add to cart|"
            r"buy |purchase |find (me )?(cheap |good )?(headphones|laptop|shoes|gift|phone))\b",
            re.I,
        ),
        "shop_search",
        None,
    ),
    (
        re.compile(
            r"\b(reserv(e|ation)|opentable|book (a )?table|dinner (for|at)|"
            r"table for \d|eat at )\b",
            re.I,
        ),
        "reservation",
        None,
    ),
    (
        re.compile(
            r"\b(open |go to |navigate|browse |visit |look up on (the )?web|"
            r"search (google|bing|the web) for)\b",
            re.I,
        ),
        "web_browse",
        None,
    ),
    (
        re.compile(
            r"\b(web search|search the web|look up|research |what is |who is |"
            r"find out about|news about)\b",
            re.I,
        ),
        "web_search",
        None,
    ),
    (
        re.compile(r"\b(life status|working board|board status|life ops)\b", re.I),
        "life_status",
        None,
    ),
    # --- Screen / vision ---
    (
        re.compile(
            r"\b(screen sense|what.?s on (my )?screen|describe (the )?screen|"
            r"see (my )?screen|ui map)\b",
            re.I,
        ),
        "screen_sense",
        None,
    ),
    (re.compile(r"\b(screenshot|capture (the )?screen|snip)\b", re.I), "screenshot", None),
    (
        re.compile(r"\b(understand (the )?pixels|ocr|read (the )?screen|pixel translate)\b", re.I),
        "understand",
        None,
    ),
    # --- Work / voice / phone ---
    (re.compile(r"\b(working mode|start work(ing)?|package handoff)\b", re.I), "work_start", None),
    (re.compile(r"\b(pair phone|phone pair|pair code)\b", re.I), "pair_mint", None),
    (re.compile(r"\b(phone surface|phone url|phone link)\b", re.I), "phone_surface", None),
    (re.compile(r"\b(fusion voice|conversational fusion)\b", re.I), "fusion_voice", None),
    # --- IoT / home ---
    (re.compile(r"\b(iot|home devices|smart home|list devices)\b", re.I), "iot_status", None),
    (re.compile(r"\b(hz mesh|offline mesh|ble mesh)\b", re.I), "iot_hz_status", None),
    # --- Console / models ---
    (re.compile(r"\b(wsl status|linux status|list distros)\b", re.I), "wsl_status", None),
    (re.compile(r"\b(auro status|auro model|meaning model status)\b", re.I), "auro_status", None),
    (re.compile(r"\b(muse status|muse spark)\b", re.I), "muse_status", None),
    # --- Desk apps ---
    (re.compile(r"\b(open notepad|launch notepad)\b", re.I), "notepad_hello", None),
    (re.compile(r"\b(remote browser|browser sense)\b", re.I), "remote_browser_status", None),
    # --- Agent mail (our own accounts + inboxes) ---
    (
        re.compile(
            r"\b(agent mail|agent inbox|my inbox|check (my )?mail|email account|"
            r"mail accounts|create (an? )?email account|agents\.pocket\.local)\b",
            re.I,
        ),
        "mail_status",
        None,
    ),
    (
        re.compile(r"\b(list (agent )?mail accounts|mail accounts)\b", re.I),
        "mail_accounts",
        None,
    ),
    (
        re.compile(
            r"\b(read (my |the )?inbox|check inbox|inbox for |mail inbox|"
            r"unread (mail|messages|email))\b",
            re.I,
        ),
        "mail_inbox",
        None,
    ),
    (
        re.compile(
            r"\b(send (an? )?(email|mail|message) to |email (the )?agent|"
            r"mail (assist|codex|grok|claude|scribe))\b",
            re.I,
        ),
        "mail_send",
        None,
    ),
    # --- Website UI via Python engines / MCP ---
    (
        re.compile(
            r"\b(website (ui|interface)|web ui|open (the )?site|use (the )?website|"
            r"drive (the )?browser|click on (the )?page)\b",
            re.I,
        ),
        "web_ui_browse",
        None,
    ),
    (
        re.compile(
            r"\b(webmcp|list (all )?(actions|functions|tasks) on (the )?(page|app|site|screen)|"
            r"what can (i|we|agents) click|diffuse (the )?(ui|page|screen))\b",
            re.I,
        ),
        "webmcp_scan",
        None,
    ),
    (
        re.compile(r"\b(python engine|list engines|run engine|named engine)\b", re.I),
        "python_engines_list",
        None,
    ),
    (
        re.compile(
            r"\b(engine uses|20 uses|named uses|list uses for engines|"
            r"web ui uses)\b",
            re.I,
        ),
        "engine_uses",
        None,
    ),
    (
        re.compile(
            r"\b(build (a |an )?(platform )?model|forge (a )?model|"
            r"create (a )?model for|register model)\b",
            re.I,
        ),
        "model_build",
        None,
    ),
    (
        re.compile(
            r"\b(multi.?plan|plan (this|the) (task|work)|break (this )?down|"
            r"sub.?agents? (for|to)|task list for)\b",
            re.I,
        ),
        "multi_plan",
        None,
    ),
    (
        re.compile(r"\b(list built models|built models|model forge status)\b", re.I),
        "model_list_built",
        None,
    ),
    # --- Multi-Sandbox Capsule + WebGPU (PROTO-CAPSULE-WASM-009) ---
    (
        re.compile(
            r"\b(capsule status|multi.?sandbox|sandbox capsule|wasm capsule|"
            r"PROTO-CAPSULE|capsule protocol)\b",
            re.I,
        ),
        "capsule_status",
        None,
    ),
    (
        re.compile(
            r"\b(allocate capsule|create capsule|new capsule|spin up (a )?capsule|"
            r"capsule (with )?(webgpu|gpu)|wasm (sandbox|guest)|isolate (this|the) (code|run|eval))\b",
            re.I,
        ),
        "capsule_allocate",
        None,
    ),
    (
        re.compile(
            r"\b(why (use )?capsules|capsule reasons|when (to|should) (i |agents )?use (a )?capsule|"
            r"20 reasons|wasm reasons)\b",
            re.I,
        ),
        "capsule_reasons",
        None,
    ),
    (
        re.compile(r"\b(list capsules|capsule list|running capsules)\b", re.I),
        "capsule_list",
        None,
    ),
    (
        re.compile(
            r"\b(webgpu|gpu probe|gpu adapters?|webgpu (status|probe|ready)|"
            r"enable webgpu|compute shaders?)\b",
            re.I,
        ),
        "webgpu_probe",
        None,
    ),
    # --- Product Studio first-class ---
    (
        re.compile(
            r"\b(studio map|product studio|what can studio|studio (features|playbooks)|"
            r"studio first.?class)\b",
            re.I,
        ),
        "studio_map",
        None,
    ),
    (
        re.compile(r"\b(studio status|ffmpeg|list (studio )?exports|list recordings)\b", re.I),
        "studio_status",
        None,
    ),
    (
        re.compile(
            r"\b(viral pack|studio viral|polish (the )?recording|auto viral|"
            r"make (a )?demo export|product pack)\b",
            re.I,
        ),
        "studio_viral",
        None,
    ),
    (
        re.compile(
            r"\b(studio ship|ship (the )?demo|ship studio|export and caption)\b",
            re.I,
        ),
        "studio_ship",
        None,
    ),
    (
        re.compile(
            r"\b(storyboard|demo beats|hook proof cta|plan (a )?demo)\b",
            re.I,
        ),
        "studio_storyboard",
        None,
    ),
    (
        re.compile(
            r"\b(studio caption|demo caption|launch blurb|social posts? for (the )?demo)\b",
            re.I,
        ),
        "studio_caption",
        None,
    ),
    (
        re.compile(r"\b(start (screen )?record|record (the )?desktop|begin recording)\b", re.I),
        "studio_record_start",
        None,
    ),
    (
        re.compile(r"\b(stop (screen )?record|stop recording|end recording)\b", re.I),
        "studio_record_stop",
        None,
    ),
    (
        re.compile(
            r"\b(render (rotato|phone|screencast|macbook|clean_demo)|studio render)\b",
            re.I,
        ),
        "studio_render",
        None,
    ),
    (
        re.compile(r"\b(open (product )?studio|studio url)\b", re.I),
        "studio_open",
        None,
    ),
    (
        re.compile(
            r"\b(record and ship|stop and ship|full (demo|loop)|studio full loop)\b",
            re.I,
        ),
        "studio_full_loop",
        None,
    ),
    (
        re.compile(r"\b(lab status|lab ready|lab hub|build better tech)\b", re.I),
        "lab_status",
        None,
    ),
    (
        re.compile(
            r"\b(allocate capsule|new capsule|capsule allocate|spin up (a )?(wasm )?capsule|"
            r"wasm capsule|sandbox (the )?code|untrusted (code|eval)|run in (a )?capsule)\b",
            re.I,
        ),
        "capsule_allocate",
        None,
    ),
]

# Console intents handled specially (run real integrated terminal)
_CONSOLE_RULES = [
    (re.compile(r"^\s*!\s*(.+)$", re.S), "wsl"),  # !cmd → wsl
    (re.compile(r"^\s*>>>\s*(.+)$", re.S), "python"),  # >>> code → host python
    (re.compile(r"^\s*wsl>\s*(.+)$", re.I | re.S), "wsl"),
    (re.compile(r"^\s*py>\s*(.+)$", re.I | re.S), "python"),
    (re.compile(r"^\s*wslpy>\s*(.+)$", re.I | re.S), "python_wsl"),
    (re.compile(r"\brun in wsl[:\s]+(.+)$", re.I | re.S), "wsl"),
    (re.compile(r"\brun (?:with )?python[:\s]+(.+)$", re.I | re.S), "python"),
    (re.compile(r"\bpython in wsl[:\s]+(.+)$", re.I | re.S), "python_wsl"),
]

# Skills that need the full user prompt as skill input (not just match)
_PROMPT_SKILLS = frozenset(
    {
        "find_feature",
        "food_order",
        "flight_search",
        "shop_search",
        "web_browse",
        "reservation",
        "web_search",
        "web_fetch",
        "assist_route",
        "life_classify",
        "tools_for_prompt",
        "fusion_voice",
        "aria_turn",
        "notepad_hello",
        "remote_browser_open",
        "mail_inbox",
        "mail_send",
        "mail_account_create",
        "web_ui_browse",
        "web_ui_open",
        "web_ui_act",
        "python_engine",
        "engine_use",
        "model_build",
        "model_suggest",
        "capsule_allocate",
        "capsule_execute",
        "capsule_commit",
        "capsule_terminate",
        "studio_storyboard",
        "studio_caption",
        "studio_render",
        "studio_ship",
        "studio_viral",
    }
)


def plan_tools(prompt: str, *, mode: str = "", limit: int = 5) -> List[Dict[str, Any]]:
    """Which host tools should run for this user turn."""
    p = prompt or ""
    out: List[Dict[str, Any]] = []
    seen = set()
    for rx, skill, params in _TOOL_RULES:
        if not rx.search(p):
            continue
        if skill in seen:
            continue
        # Avoid double food+shop when both match weakly
        if skill == "shop_search" and "food_order" in seen:
            continue
        if skill == "web_browse" and any(
            s in seen for s in ("food_order", "flight_search", "shop_search", "reservation")
        ):
            continue
        if skill == "web_search" and any(
            s in seen for s in ("food_order", "flight_search", "shop_search", "reservation", "web_browse")
        ):
            continue
        seen.add(skill)
        item: Dict[str, Any] = {"skill": skill}
        if params:
            item["params"] = dict(params)
        if skill in _PROMPT_SKILLS:
            item["prompt"] = p
        out.append(item)
        if len(out) >= limit:
            break
    # Always give coding modes a skill list if they ask for tools/skills
    if not out and re.search(r"\b(use (your |the )?tools|run skill|host tools|what tools)\b", p, re.I):
        out.append({"skill": "list_skills"})
        out.append({"skill": "life_catalog"})
    # Life-mode / assist-mode: classify if nothing else matched
    if not out and mode in ("assist", "assistant", "life", "work", "digital", "day", "personal"):
        try:
            from pocket.life_ops import classify_life

            hit = classify_life(p)
            if hit:
                kind_to_skill = {
                    "food_order": "food_order",
                    "flight": "flight_search",
                    "shop": "shop_search",
                    "buy": "shop_search",
                    "browse": "web_browse",
                    "reservation": "reservation",
                }
                sk = kind_to_skill.get(hit[0])
                if sk:
                    out.append({"skill": sk, "prompt": p})
        except Exception:
            pass
    return out


def _run_one(skill: str, *, prompt: str = "", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = params or {}
    t0 = time.time()
    try:
        from pocket.skill_runner import run_skill

        md, err, eng = run_skill(skill, prompt=prompt, params=params)
        return {
            "ok": not bool(err),
            "skill": skill,
            "engine": eng,
            "error": (err or "")[:400],
            "markdown": (md or "")[:6000],
            "ms": int((time.time() - t0) * 1000),
        }
    except Exception:
        pass
    try:
        from pocket.orchestrator_exec import dispatch_skill

        r = dispatch_skill(skill, prompt=prompt, params=params)
        if not isinstance(r, dict):
            r = {"ok": True, "result": r}
        return {
            "ok": bool(r.get("ok", True)),
            "skill": skill,
            "result": r,
            "markdown": _compact_md(skill, r),
            "ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        return {"ok": False, "skill": skill, "error": str(e)[:300], "ms": int((time.time() - t0) * 1000)}


def _compact_md(skill: str, r: Dict[str, Any]) -> str:
    import json

    body = json.dumps(r, default=str)[:4000]
    return f"### Tool `{skill}`\n\n```json\n{body}\n```\n"


def _run_console_intents(prompt: str, *, mode: str = "") -> List[Dict[str, Any]]:
    """If the user pasted console syntax, run integrated WSL/Python consoles."""
    out: List[Dict[str, Any]] = []
    text = prompt or ""
    for rx, kind in _CONSOLE_RULES:
        m = rx.search(text)
        if not m:
            continue
        cmd = (m.group(1) or "").strip()
        if not cmd:
            continue
        try:
            from pocket.terminals import agent_run

            r = agent_run(cmd, kind=kind, wait_ms=900)
            tail = (r.get("log_tail") or "")[-2500:]
            out.append(
                {
                    "ok": bool(r.get("ok")),
                    "skill": f"console:{kind}",
                    "markdown": (
                        f"### Console `{kind}`\n\n```text\n{tail}\n```\n"
                        f"_pid={r.get('pid')} alive={r.get('alive')}_\n"
                    ),
                    "result": {"kind": kind, "alive": r.get("alive"), "pid": r.get("pid")},
                }
            )
        except Exception as e:
            out.append({"ok": False, "skill": f"console:{kind}", "error": str(e)[:200]})
        break  # one console run per turn is enough
    return out


def run_tools_for_prompt(
    prompt: str,
    *,
    mode: str = "",
    limit: int = 5,
) -> Dict[str, Any]:
    """Execute planned tools; return inject block + raw results."""
    results: List[Dict[str, Any]] = list(_run_console_intents(prompt, mode=mode))
    planned = plan_tools(prompt, mode=mode, limit=limit)
    rah_auto_result: Optional[Dict[str, Any]] = None

    # Auto RAH before other tools when score says so (user need not say "RAH")
    try:
        from pocket.rah import score_rah_fit, maybe_auto_rah

        fit = score_rah_fit(prompt, mode=mode)
        if fit.get("use_rah") and mode not in ("shell", "term", "rah", "recursive_harness"):
            # Prefer full execute once; inject synthesis so the model doesn't re-do linear work
            auto = maybe_auto_rah(prompt, mode=mode, execute=True)
            if auto and auto.get("execute"):
                rah_auto_result = auto
                md = str(auto.get("markdown") or "")[:12000]
                results.append(
                    {
                        "ok": bool(auto.get("ok")),
                        "skill": "rah_run",
                        "markdown": (
                            "### Tool `rah_run` (AUTO — agent selected RAH)\n\n"
                            f"score={fit.get('score')} threshold={fit.get('threshold')}\n\n"
                            f"{md}\n"
                        ),
                        "result": {
                            "run_id": (auto.get("run") or {}).get("run_id"),
                            "auto": True,
                            "fit": fit,
                        },
                    }
                )
                # Skip duplicate rah_run from regex planned list
                planned = [p for p in planned if (p.get("skill") or "") not in ("rah_run", "rah_plan")]
    except Exception:
        pass

    for item in planned:
        skill = item.get("skill") or ""
        if not skill:
            continue
        # Cap expensive rah_run if we already auto-ran
        if skill == "rah_run" and rah_auto_result:
            continue
        params = item.get("params") if isinstance(item.get("params"), dict) else {}
        # Auto-tune leaf count for rah_run from detector
        if skill == "rah_run":
            try:
                from pocket.rah import score_rah_fit

                fit = score_rah_fit(prompt, mode=mode)
                params = {
                    **params,
                    "max_leaves": params.get("max_leaves") or fit.get("suggested_leaves") or 8,
                    "max_depth": params.get("max_depth") or fit.get("suggested_depth") or 2,
                    "max_parallel": params.get("max_parallel") or 6,
                }
            except Exception:
                pass
        results.append(
            _run_one(
                skill,
                prompt=str(item.get("prompt") or prompt or "")[:2000],
                params=params,
            )
        )
    parts = []
    for r in results:
        if r.get("markdown"):
            parts.append(str(r["markdown"]))
        elif r.get("error"):
            parts.append(f"### Tool `{r.get('skill')}` failed\n{r.get('error')}\n")
    inject = ""
    if parts:
        inject = (
            "\n\n---\n## Host tools already run (use these results — do not pretend you cannot)\n\n"
            + "\n".join(parts)
            + "\n---\n"
        )
        if rah_auto_result:
            inject += (
                "\n[INSTRUCTION] RAH already executed for this turn. "
                "Summarize the synthesis for the user; do not re-plan the same fan-out linearly.\n"
            )
        cmd_skills = {str(r.get("skill") or "") for r in results}
        if cmd_skills & {"go", "go_state", "go_tick", "power_do", "power_vs", "multi_workflows"}:
            inject += (
                "\n[INSTRUCTION] GO/Power already ran on this host. "
                "Summarize the skill block for the user in plain language. "
                "Do not invent a generic morning plan or say you lack access.\n"
            )
    command_md = "\n".join(parts) if parts else ""
    return {
        "ok": True,
        "planned": planned,
        "results": results,
        "inject": inject,
        "ran": len(results),
        "rah_auto_result": rah_auto_result,
        "command_md": command_md,
    }


def enrich_prompt(prompt: str, *, mode: str = "") -> Tuple[str, Dict[str, Any]]:
    """Return (prompt + POCKET identity + tools + platform + protocols, meta)."""
    meta = run_tools_for_prompt(prompt, mode=mode)
    # Identity first — every model knows it is in POCKET and can help with POCKET
    try:
        from pocket.pocket_identity import wrap_user_prompt

        base = wrap_user_prompt(
            prompt or "",
            mode=mode,
            include_protocols=True,
            include_platform=True,
            max_identity=1400,
        )
        meta["pocket_identity"] = True
    except Exception:
        base = (prompt or "").rstrip()
        brief = ""
        try:
            from pocket.agentic_harness import platform_brief

            brief = platform_brief(max_chars=900)
        except Exception:
            try:
                from pocket.platform_coherence import platform_brief as pc_brief

                brief = pc_brief(max_chars=900)
            except Exception:
                brief = ""
        if brief:
            base = base + "\n\n[POCKET PLATFORM]\n" + brief
    # LOOMGRAPH forever — default loop/graph harness for all agents
    try:
        from pocket.loomgraph import brief as loomgraph_brief

        lg = loomgraph_brief(max_chars=420)
        if lg and "LOOMGRAPH" not in base:
            base = base.rstrip() + "\n\n[LOOMGRAPH]\n" + lg
            meta["loomgraph"] = True
    except Exception:
        pass
    chunks = [base.rstrip()]
    if meta.get("inject"):
        chunks.append(meta["inject"].strip())
    # Instruct model to act on tool results
    if meta.get("ran"):
        chunks.append(
            "[INSTRUCTION] Host tools above already executed. Cite their outputs. "
            "Life tools never auto-pay — if status is needs_you, tell the user to confirm/pay themselves. "
            "If a skill failed, say so and propose the next skill id to run via /v1/skills/run. "
            "Multi-step work: prefer LOOMGRAPH (skill loomgraph_run) so the path is a readable graph. "
            "You are a POCKET host agent — help the user operate POCKET."
        )
    # Spherical neuro pass for Grok / Claude / Codex / Spark / Auro
    try:
        from pocket.neuro_think import inject as neuro_inject

        joined = "\n\n".join(chunks)
        joined, nmeta = neuro_inject(joined, mode=mode)
        meta["neuro"] = {k: nmeta.get(k) for k in ("ok", "kind", "ms", "spherical", "already", "skipped") if k in nmeta}
        return joined + ("\n" if not joined.endswith("\n") else ""), meta
    except Exception as e:
        meta["neuro_error"] = str(e)[:120]
    return "\n\n".join(chunks) + "\n", meta


def embedded_tools_summary() -> Dict[str, Any]:
    """For desk/API: which tool rules + life skills are wired for all agents."""
    rules = []
    for rx, skill, _ in _TOOL_RULES:
        rules.append({"skill": skill, "pattern": rx.pattern[:80]})
    life = []
    try:
        from pocket.life_ops import life_skill_catalog

        life = life_skill_catalog()
    except Exception:
        pass
    return {
        "ok": True,
        "tool_rules": len(_TOOL_RULES),
        "rules": rules,
        "life_skills": life,
        "prompt_skills": sorted(_PROMPT_SKILLS),
        "entry": "enrich_prompt → skill_runner → platform / life_ops",
    }
