"""Digital assistant — agentic real-life help for Work Studio (separate from coding desk).

Routes natural language to the right host engine:
  plan · research · calendar · email · buy · reserve · open · screen ·
  muse · auro · working board · multi-step assist.

Designed for humans as a day-to-day digital assistant, not only developers.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple


ASSISTANT_ENGINES = (
    "assist",
    "assistant",
    "digital",
    "life",
    "day",
    "personal",
)


def _progress(job_id: str, text: str, engine: str = "assist") -> None:
    if not job_id:
        return
    try:
        from pocket.stream_util import update_progress

        update_progress(job_id, text, engine=engine)
    except Exception:
        pass


def route_intent(text: str) -> str:
    """Pick best engine for everyday life + digital assistant asks."""
    t = (text or "").strip()
    low = t.lower()
    if not t:
        return "plan"
    # Everyday life always → Working board life ops
    try:
        from pocket.life_ops import classify_life

        if classify_life(t):
            return "work"
    except Exception:
        pass
    if re.search(
        r"\b(buy|purchase|order|shop|amazon|checkout|doordash|uber ?eats|flight|flights|"
        r"fly to|reserv|restaurant|eat at|opentable|deliver)\b",
        low,
    ):
        return "work"
    if re.search(r"\b(email|draft message|notify|slack|write to)\b", low):
        return "work"
    if re.search(r"\b(schedule|calendar|remind|meeting|appointment)\b", low):
        return "work"
    if re.search(r"\b(research|look up|search|what is|who is|find out|news)\b", low):
        return "web"
    if re.search(r"\b(muse|spark|meta\.ai|multimodal reason)\b", low):
        return "muse_spark"
    if re.search(r"\b(auro|meaning model|local model|lmr)\b", low):
        return "auro"
    if re.search(r"\b(screen|what.?s on|screenshot|see my|click )\b", low):
        return "vision"
    if re.search(r"\b(code|implement|refactor|bug|repo|git|pr |pull request)\b", low):
        return "codex"
    if re.search(
        r"\b(hit go|press go|go plane|what.?s working|active states|"
        r"morning seatbelt|power do|do it on (the )?host|100 workflows)\b",
        low,
    ):
        return "power"
    if re.search(r"\b(plan|roadmap|outline|break down|steps for)\b", low):
        return "plan"
    if re.search(r"\b(open |browse |edge |browser|navigate|go to )\b", low):
        return "work"  # browse via life board + Edge
    # default: life-friendly plan
    return "plan"


def _fast_plan(prompt: str) -> str:
    """Instant structured plan for common day-ops asks (no heavy LLM wait)."""
    low = (prompt or "").lower()
    title = (prompt or "Your plan").strip()[:120]
    lines = [
        "# Plan",
        "",
        f"**Goal:** {title}",
        "",
        "## Success looks like",
        "- You know the next 3 actions",
        "- Time boxed enough to start today",
        "- Blockers listed, not ignored",
        "",
        "## Steps",
    ]
    if re.search(r"\b(morning|today|day)\b", low):
        lines += [
            "1. **Triage (10 min)** — list must-do vs nice-to-do",
            "2. **Deep work block (45–90 min)** — hardest high-leverage task first",
            "3. **Comms batch (20 min)** — email / messages in one pass",
            "4. **Admin / errands (20 min)** — calendar, pay, ship, book",
            "5. **Close the loop (10 min)** — note wins + tomorrow’s #1",
        ]
    elif re.search(r"\b(trip|travel|weekend)\b", low):
        lines += [
            "1. Fix dates + budget ceiling",
            "2. Pick 2–3 destination options (research)",
            "3. Book stay + transport",
            "4. Hold one dinner / activity reservation",
            "5. Share itinerary with travel partners",
        ]
    else:
        lines += [
            "1. Clarify the outcome in one sentence",
            "2. List constraints (time, money, tools, people)",
            "3. Break into 3–5 actions under 30 minutes each",
            "4. Do the first action now",
            "5. Review and adjust",
        ]
    lines += [
        "",
        "## First action (do next)",
        f"- Start: **{(title.split()[:8] and ' '.join(title.split()[:8])) or 'the first step'}** — 15 minutes, no perfect setup.",
        "",
        "## Optional engines",
        "- **Life ops** for buy / reserve / notify",
        "- **Research** for sources",
        "- **Muse Spark** for multi-lane reasoning",
        "- **Auro** for local model answers",
        "",
        "_Fast plan · host digital assistant_",
    ]
    return "\n".join(lines)


def run_assistant_turn(
    text: str,
    *,
    engine: str = "auto",
    session_id: str = "",
    job_id: str = "",
    voice: bool = False,
) -> Dict[str, Any]:
    """One agentic digital-assistant turn. Returns reply + routing metadata."""
    t0 = time.time()
    prompt = (text or "").strip()
    if not prompt or prompt.lower() in ("help", "?", "hi", "hello", "hey"):
        return {
            "ok": True,
            "reply": _welcome(),
            "engine": "assist",
            "intent": "welcome",
            "ms": int((time.time() - t0) * 1000),
        }

    eng = (engine or "auto").lower().strip()
    if eng in ("auto", "assist", "assistant", "digital", "life", ""):
        eng = route_intent(prompt)

    intent = route_intent(prompt)
    _progress(job_id, f"Digital assistant · → {eng}…", eng)

    if eng == "power":
        try:
            from pocket.agent_tools_loop import run_tools_for_prompt

            meta = run_tools_for_prompt(prompt, mode="assist")
            body = meta.get("command_md") or meta.get("inject") or "GO/Power ran. Open /power."
            return _pack("[engine=power · digital assistant]\n\n" + body, "power", "go_power", t0)
        except Exception as e:
            _progress(job_id, f"Power path failed ({e})")
            eng = "plan"

    # Fast path: simple plans without multi-agent harness lag
    if eng == "plan" and len(prompt) < 280 and not re.search(
        r"\b(code|repo|implement|architecture|system design)\b", prompt, re.I
    ):
        body = f"[engine=plan · digital assistant · fast]\n\n{_fast_plan(prompt)}"
        if voice:
            spoken = f"Here's a quick plan for {prompt[:80]}."
            body += f"\n\n```tts\nrate=0.96\npitch=1.02\n{spoken}\n```"
        return _pack(body, "plan", "plan_fast", t0)

    # Life ops → Working board (buy / reserve / notify / schedule)
    if eng in ("work", "working", "live_work"):
        try:
            from pocket.working_board import ingest_and_run

            br = ingest_and_run(prompt, session_id=session_id or "", execute=True, job_id=job_id)
            reply = br.get("reply") or br.get("table") or "Board updated."
            reply = (
                "# Digital assistant · real-world work\n\n"
                + reply
                + "\n\n_Handled on the Working board — confirm pay/book steps yourself when marked needs_you._"
            )
            return _pack(reply, eng, "life_ops", t0, extra={"board": br.get("board"), "ran": br.get("ran")})
        except Exception as e:
            eng = "plan"
            _progress(job_id, f"Board fallback → plan ({e})")

    # Fast research path — direct web, skip harness
    if eng == "web":
        try:
            from pocket.web_research import search_web

            _progress(job_id, "Researching…", "web")
            sr = search_web(prompt[:200], max_results=8)
            hits = sr.get("results") or []
            lines = [
                "# Research",
                "",
                f"**Query:** {prompt[:200]}",
                "",
                f"_{len(hits)} sources · {(sr.get('backends') or ['web'])}_",
                "",
            ]
            for i, h in enumerate(hits[:8], 1):
                lines.append(f"{i}. **{(h.get('title') or 'result')[:110]}**")
                if h.get("snippet"):
                    lines.append(f"   {h['snippet'][:180]}")
                if h.get("url"):
                    lines.append(f"   {h['url']}")
            if not hits:
                lines.append("_No hits — try a more specific query or Muse Spark._")
            else:
                lines.append("")
                lines.append("**Next:** open a link, or ask Life ops to book / buy.")
            body = f"[engine=web · digital assistant]\n\n" + "\n".join(lines)
            if voice and hits:
                body += f"\n\n```tts\nrate=0.96\npitch=1.02\nFound {len(hits)} sources. See the list for details.\n```"
            return _pack(body, "web", "research", t0, extra={"count": len(hits)})
        except Exception as e:
            _progress(job_id, f"Research failed · {e}")

    # Delegate to host executor modes (heavier engines)
    result_text = ""
    err = ""
    used = eng
    try:
        from pocket.executor import run_job

        # Skip nested harness for assist-driven turns — keep latency sane
        job = {
            "id": job_id or f"assist-{int(time.time())}",
            "mode": eng,
            "prompt": prompt,
            "session_id": session_id or "",
            "harness": False,
            "_tools_done": eng in ("plan", "web"),
        }
        result_text, err, used = run_job(job)
    except Exception as e:
        result_text = ""
        err = str(e)[:300]
        used = eng

    if not result_text and err:
        _progress(job_id, "Recovering with web research…")
        try:
            from pocket.web_research import search_web

            sr = search_web(prompt[:200], max_results=6)
            hits = sr.get("results") or []
            lines = [
                "# Digital assistant",
                "",
                f"Primary engine **{eng}** had trouble (`{err[:120]}`). Research fallback:",
                "",
            ]
            for i, h in enumerate(hits[:6], 1):
                lines.append(f"{i}. **{(h.get('title') or 'result')[:100]}**")
                if h.get("snippet"):
                    lines.append(f"   {h['snippet'][:160]}")
                if h.get("url"):
                    lines.append(f"   {h['url']}")
            lines.append("")
            lines.append("**Next:** rephrase, or pick Muse Spark / Auro / Codex on the desk.")
            result_text = "\n".join(lines)
            err = ""
            used = "web"
        except Exception as e2:
            result_text = f"# Digital assistant\n\nCouldn't complete that yet.\n\n`{err or e2}`\n"
            used = "assist"

    header = f"[engine={used} · digital assistant]\n\n"
    body = header + (result_text or "Done.")
    if voice and "```tts" not in body:
        spoken = re.sub(r"\s+", " ", re.sub(r"[#*_`\[\]]+", " ", body.split("\n\n")[0]))[:220]
        if len(spoken) > 30:
            body += f"\n\n```tts\nrate=0.96\npitch=1.02\n{spoken}\n```"

    return _pack(body, used, intent, t0, extra={"error": err or None})


def _pack(reply: str, engine: str, intent: str, t0: float, extra: Optional[Dict] = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": True,
        "reply": reply,
        "engine": engine,
        "intent": intent,
        "ms": int((time.time() - t0) * 1000),
        "surface": "work_studio",
        "schema": "pocket.digital_assistant.v1",
    }
    if extra:
        out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _welcome() -> str:
    try:
        from pocket.life_ops import life_welcome

        return life_welcome()
    except Exception:
        return (
            "# Everyday life assistant\n\n"
            "- **Order food** — *Order sushi delivery*\n"
            "- **Flights** — *Flights to NYC next Friday*\n"
            "- **Shop** — *Buy headphones under $100*\n"
            "- **Web** — *Open google flights* / *Search hotels in Austin*\n"
            "- **Dinner out** — *Reserve Del Frisco 8:30 for 2*\n"
        )


def catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.digital_assistant.catalog.v1",
        "focus": "everyday life · food · flights · shopping · web",
        "engines": [
            {"id": "auto", "name": "Auto", "blurb": "Route to the best engine"},
            {"id": "work", "name": "Life ops", "blurb": "Food · flights · shop · reserve · web"},
            {"id": "web", "name": "Research", "blurb": "Search + fetch"},
            {"id": "plan", "name": "Plan", "blurb": "Break down goals"},
            {"id": "muse_spark", "name": "Muse Spark", "blurb": "Multimodal multi-lane reasoning"},
            {"id": "auro", "name": "Auro", "blurb": "Local LMR / meaning model"},
            {"id": "browser", "name": "Browser", "blurb": "Host Edge"},
            {"id": "vision", "name": "Vision", "blurb": "Screen eyes"},
            {"id": "codex", "name": "Codex", "blurb": "Code when you need it"},
            {"id": "grok", "name": "Grok", "blurb": "Code + research"},
            {"id": "claude", "name": "Claude", "blurb": "Agent tools loop"},
        ],
        "intents": [
            "food_order",
            "flight",
            "shop",
            "browse",
            "reservation",
            "research",
            "plan",
            "email",
            "calendar",
        ],
    }
