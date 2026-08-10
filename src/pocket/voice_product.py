"""Voice product brain — Aria (and any voice-engine agent) does useful host work.

Order of operations (always local-first, never fake pay):
  1. Everyday skills (time, lists, math, focus…)
  2. Host life ops (food / flights / shop / reserve / web) — opens Edge, needs_you for pay
  3. Screen / vision brief when user asks what they see
  4. Digital assistant routing for day-ops plans
  5. Pocket Voice API turn when available
  6. Warm Aria local reply
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple


PRODUCT = {
    "name": "Aria · Voice product",
    "id": "pocket.voice.product.v1",
    "first_class": True,
    "doctrine": [
        "Voice is a real product agent — not a demo widget",
        "Host tools run before small-talk when intent is actionable",
        "Never auto-pay or finalize bookings",
        "Works offline via local skills when :8790 is down",
    ],
}


def product_status() -> Dict[str, Any]:
    voice_ok = False
    voice_detail: Dict[str, Any] = {}
    try:
        from pocket.voice_proxy import health, ensure_voice

        voice_detail = health()
        voice_ok = bool(voice_detail.get("ok"))
        if not voice_ok:
            ensure_voice(wait_sec=1.5)
            voice_detail = health()
            voice_ok = bool(voice_detail.get("ok"))
    except Exception as e:
        voice_detail = {"error": str(e)[:160]}
    skills = []
    try:
        from pocket.voice_skills import list_skills

        skills = list_skills()
    except Exception:
        pass
    gemini: Dict[str, Any] = {}
    tts: Dict[str, Any] = {}
    try:
        from pocket.gemini_voice import status as gemini_status

        gemini = gemini_status()
    except Exception as e:
        gemini = {"configured": False, "error": str(e)[:80]}
    try:
        from pocket.tts_engine import status as tts_status

        tts = tts_status()
    except Exception as e:
        tts = {"edge_tts": False, "error": str(e)[:80]}

    brain = "gemini" if gemini.get("configured") else ("pocket-voice" if voice_ok else "local")
    speak = "edge-tts" if tts.get("edge_tts") else "browser"
    return {
        "ok": True,
        "product": PRODUCT,
        "voice_api": voice_ok,
        "voice_detail": voice_detail,
        "gemini": gemini,
        "tts": tts,
        "brain": brain,
        "speak": speak,
        "real_convo": {
            "listen": "browser Web Speech (Edge/Chrome mic)",
            "think": brain,
            "talk": speak,
            "duplex": "turn-based (you speak → Aria thinks → Aria speaks)",
            "full_native_live": False,
            "note": "Real conversation works turn-by-turn on desk/phone. Not Gemini Live bidirectional yet.",
        },
        "skills_count": len(skills),
        "skills": skills,
        "host_actions": [
            "food_order",
            "flight_search",
            "shop_search",
            "reservation",
            "web_browse",
            "screen_sense",
            "life_catalog",
        ],
        "surfaces": {
            "desk": "seat Aria / Voice engine on any agent",
            "phone": "/phone · Aria mode",
            "voice_studio": "/studio/voice",
            "api": "POST /v1/jobs mode=voice",
            "tts": "POST /v1/voice/tts",
        },
        "message": f"Aria ready · brain={brain} · speak={speak}",
    }


def _life_action(text: str) -> Optional[Dict[str, Any]]:
    """Run real life_ops when user asks to order/book/shop/browse (no auto-pay)."""
    try:
        from pocket.life_ops import classify_life, run_life_skill
    except Exception:
        return None
    hit = classify_life(text)
    if not hit:
        # soft map common spoken forms
        low = (text or "").lower()
        if re.search(r"\b(order|get me|deliver)\b", low) and re.search(
            r"\b(pizza|sushi|food|dinner|lunch|coffee|burger)\b", low
        ):
            hit = ("food_order", text)
        elif re.search(r"\b(fly|flight|flights)\b", low):
            hit = ("flight", text)
        elif re.search(r"\b(buy|purchase|shop for)\b", low):
            hit = ("shop", text)
        elif re.search(r"\b(reserv|book (a )?table|opentable)\b", low):
            hit = ("reservation", text)
        elif re.search(r"\b(open |go to |search (for )?)\b", low):
            hit = ("browse", text)
        else:
            return None
    kind, _title = hit
    skill_map = {
        "food_order": "food_order",
        "flight": "flight_search",
        "shop": "shop_search",
        "buy": "shop_search",
        "browse": "web_browse",
        "reservation": "reservation",
    }
    skill = skill_map.get(kind) or kind
    # Don't open browser on pure "list options" without action verbs? Prefer open for real product feel
    r = run_life_skill(skill, prompt=text, open_browser=True)
    if not r.get("ok"):
        return None
    links = r.get("links") or r.get("choices") or []
    gate = r.get("gate_message") or r.get("message") or ""
    spoken_bits = [gate or f"I started {kind.replace('_', ' ')} for you."]
    if r.get("confirm_blocked"):
        spoken_bits.append("You confirm and pay yourself — I never checkout for you.")
    if links:
        titles = ", ".join((L.get("title") or "option") for L in links[:3])
        spoken_bits.append(f"Options: {titles}.")
    return {
        "kind": "life",
        "skill": skill,
        "reply": " ".join(spoken_bits),
        "result": r,
        "source": "life_ops",
    }


def _screen_action(text: str) -> Optional[Dict[str, Any]]:
    low = (text or "").lower()
    if not re.search(
        r"\b(what.?s on (my |the )?screen|see (my )?screen|look at (the )?screen|"
        r"screen sense|describe (the )?screen|what do you see)\b",
        low,
    ):
        return None
    try:
        from pocket.screen_share import fusion_context, set_share, status as screen_status

        st = screen_status()
        if not st.get("can_view"):
            set_share(mode="view", reset_target=True, target="desktop")
        ctx = fusion_context(agent="aria", max_ui=200)
        brief = (ctx.get("brief") or ctx.get("message") or "I looked at the screen.").strip()
        # Spoken: shorter
        spoken = brief
        if len(spoken) > 280:
            spoken = spoken[:260].rsplit(" ", 1)[0] + "…"
        return {
            "kind": "screen",
            "skill": "screen_sense",
            "reply": spoken,
            "result": ctx,
            "source": "screen_share",
        }
    except Exception as e:
        return {
            "kind": "screen",
            "skill": "screen_sense",
            "reply": f"I couldn't read the screen just now ({str(e)[:80]}). Open Screen → View and try again.",
            "result": {"ok": False},
            "source": "screen_share",
        }


def _assist_plan(text: str) -> Optional[Dict[str, Any]]:
    low = (text or "").lower()
    if not re.search(
        r"\b(plan my (day|morning|week)|what should i do today|help me plan|"
        r"priorit|roadmap for)\b",
        low,
    ):
        return None
    try:
        from pocket.digital_assistant import _fast_plan

        plan = _fast_plan(text)
        # Speak condensed
        spoken = re.sub(r"[#*_`]", "", plan)
        spoken = re.sub(r"\n+", ". ", spoken)
        spoken = re.sub(r"\s+", " ", spoken).strip()
        if len(spoken) > 420:
            spoken = spoken[:400].rsplit(" ", 1)[0] + "…"
        return {
            "kind": "plan",
            "skill": "assist_plan",
            "reply": spoken,
            "result": {"plan_md": plan},
            "source": "digital_assistant",
        }
    except Exception:
        return None


def _host_status(text: str) -> Optional[Dict[str, Any]]:
    low = (text or "").lower()
    if not re.search(
        r"\b(are you (up|online|working)|voice status|pocket status|is voice (up|ready))\b",
        low,
    ):
        return None
    st = product_status()
    return {
        "kind": "status",
        "skill": "voice_status",
        "reply": st.get("message")
        + f". I have {st.get('skills_count')} everyday skills and can open food, flights, shop, or read your screen.",
        "result": st,
        "source": "voice_product",
    }


def try_host_action(text: str) -> Optional[Dict[str, Any]]:
    """Actionable host paths for voice — before chatty API."""
    for fn in (_host_status, _screen_action, _life_action, _assist_plan):
        try:
            hit = fn(text)
            if hit:
                return hit
        except Exception:
            continue
    return None


def run_voice_turn(
    text: str,
    *,
    session_id: str = "",
    job_id: str = "",
) -> Dict[str, Any]:
    """Full product turn: skills → host actions → voice API → local Aria."""
    t0 = time.time()
    text = (text or "").strip()
    if not text:
        return {
            "ok": False,
            "error": "empty",
            "reply": "I'm listening — say something when you're ready.",
            "source": "empty",
        }

    # 1) Everyday local skills
    try:
        from pocket.voice_skills import try_skill, skill_help

        if re.search(r"\b(what can you (do|help)|your skills|help me with|capabilities)\b", text, re.I):
            help_txt = skill_help()
            help_txt += (
                "\n\nI can also order food options, search flights, shop, reserve tables "
                "(you pay), read your screen, and plan your day — just say it."
            )
            out = {
                "ok": True,
                "reply": help_txt,
                "source": "skill_help",
                "skill_id": "help",
                "ms": int((time.time() - t0) * 1000),
            }
            out.update(_attach_tts(help_txt))
            return out
        sk = try_skill(text)
        if sk:
            out = {
                "ok": True,
                "reply": sk[0],
                "source": "voice_skill",
                "skill_id": sk[1],
                "ms": int((time.time() - t0) * 1000),
            }
            out.update(_attach_tts(sk[0]))
            return out
    except Exception:
        pass

    # 2) Host actions (life / screen / plan)
    host = try_host_action(text)
    if host:
        out = {
            "ok": True,
            "reply": host["reply"],
            "source": host.get("source") or "host",
            "skill_id": host.get("skill"),
            "host": host,
            "ms": int((time.time() - t0) * 1000),
        }
        out.update(_attach_tts(host["reply"]))
        return out

    # 3) Gemini brain (real LLM) when API key is configured
    fusion_meta: Dict[str, Any] = {}
    try:
        from pocket.conversational_fusion import fuse, remember

        fusion_meta = fuse(
            {
                "text": text,
                "stress": 0.4,
                "session_id": session_id or f"voice-{job_id or 'desk'}",
                "is_final": True,
            }
        )
        remember(session_id or "voice", fusion_meta)
    except Exception:
        fusion_meta = {}

    try:
        from pocket.gemini_voice import gemini_chat, gemini_configured

        if gemini_configured():
            g = gemini_chat(
                text,
                context=(
                    f"fusion_pattern={fusion_meta.get('pattern') or '—'}; "
                    f"expert={fusion_meta.get('primary_expert') or 'aria'}"
                ),
            )
            if g.get("ok") and g.get("reply"):
                out = {
                    "ok": True,
                    "reply": g["reply"],
                    "source": "gemini",
                    "model": g.get("model"),
                    "fusion": {
                        "pattern": fusion_meta.get("pattern"),
                        "primary_expert": fusion_meta.get("primary_expert"),
                    },
                    "ms": int((time.time() - t0) * 1000),
                }
                out.update(_attach_tts(g["reply"]))
                return out
    except Exception:
        pass

    # 4) Pocket Voice API (:8790) if running
    api_reply = ""
    api_err = ""
    try:
        from pocket.voice_proxy import ensure_voice, proxy_request, health

        ensure_voice(wait_sec=2.0)
        h = health()
        if h.get("ok"):
            code, data = proxy_request(
                "POST",
                "/v1/turn",
                body={
                    "text": text,
                    "session_id": session_id or f"pocket-{job_id or 'desk'}",
                    "persona_name": "Aria",
                    "business_mode": "customer_service",
                    "agentic": True,
                    "scenario": "patient",
                    "stress": 0.38,
                },
                timeout=8.0,
            )
            if code < 400 and isinstance(data, dict):
                api_reply = str(data.get("reply") or data.get("text") or "").strip()
            else:
                api_err = str((data or {}).get("error") or f"voice http {code}")[:160]
        else:
            api_err = str(h.get("error") or "voice api down")[:160]
    except Exception as e:
        api_err = str(e)[:160]

    if api_reply and not _looks_like_cold_support_bot(api_reply, text):
        out = {
            "ok": True,
            "reply": api_reply,
            "source": "pocket-voice-api",
            "fusion": {
                "pattern": fusion_meta.get("pattern"),
                "primary_expert": fusion_meta.get("primary_expert"),
            },
            "ms": int((time.time() - t0) * 1000),
        }
        out.update(_attach_tts(api_reply))
        return out
    if api_reply and _looks_like_cold_support_bot(api_reply, text):
        api_err = (api_err or "") + " · discarded_cold_support_copy"

    # 5) Local Aria (always on-brand)
    try:
        from pocket.executor import _aria_local_reply

        reply = _aria_local_reply(text)
    except Exception:
        reply = (
            "I heard you. Try “what can you do”, “order pizza”, or “what’s on my screen”. "
            "For smarter chat, add GEMINI_API_KEY to ~/.pocket/keys.env"
        )
    out = {
        "ok": True,
        "reply": reply,
        "source": "aria-local",
        "error": api_err or None,
        "fusion": {
            "pattern": fusion_meta.get("pattern"),
            "primary_expert": fusion_meta.get("primary_expert"),
        },
        "ms": int((time.time() - t0) * 1000),
    }
    out.update(_attach_tts(reply))
    return out


def _looks_like_cold_support_bot(reply: str, user_text: str) -> bool:
    """Pocket-voice default often returns generic CS scripts — reject for Aria product."""
    r = (reply or "").lower()
    u = (user_text or "").lower()
    # Identity should be Aria on greeting / who are you
    if re.search(r"\b(hi|hello|hey|who are you|what.?s your name)\b", u):
        if "aria" not in r and re.search(
            r"\b(someone else|order number|transfer you|customer service|hold please|ticket)\b",
            r,
        ):
            return True
    if re.search(
        r"\b(i can get someone else|could i get your (order|account)|escalate to a specialist)\b",
        r,
    ):
        return True
    return False


def _attach_tts(reply: str) -> Dict[str, Any]:
    """Best-effort free neural TTS (edge-tts); desk falls back to browser speak."""
    try:
        from pocket.tts_engine import synthesize

        # Strip markdown-ish for speech
        spoken = re.sub(r"[#*_`>]+", "", reply or "")
        spoken = re.sub(r"\s+", " ", spoken).strip()
        tts = synthesize(spoken[:480])
        if tts.get("ok"):
            return {"tts_audio": tts.get("url_path"), "tts_engine": tts.get("engine"), "tts": tts}
    except Exception:
        pass
    return {}
