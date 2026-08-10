"""First-class Product Studio for agents — record · polish · export · ship.

Unifies video_studio + imagine_studio + screen record into one agent-callable
surface. Agents use skills / POST /v1/studio/* — users open /studio UI.

Doctrine:
  · Studio is first-class (not a buried demo tool)
  · Agents can plan, record, render, caption, ship without human clicking
  · Never fake marketing claims; exports are real ffmpeg/device remakes
  · Contain glass (no stretch-crop of UI)
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

PROTOCOL_ID = "POCKET-STUDIO-FIRST-CLASS/1.0"
PRODUCT = "POCKET Product Studio"

# Agent playbooks — what agents should do, in order
PLAYBOOKS: List[Dict[str, Any]] = [
    {
        "id": "viral_ship",
        "name": "Viral ship pack",
        "desc": "Latest recording → phone remake + web + screencast polish",
        "steps": ["studio_status", "studio_list_recordings", "studio_viral"],
        "say": "Make a viral pack from the latest recording",
        "skills": ["studio_viral", "studio_auto", "viral_pack"],
    },
    {
        "id": "record_polish",
        "name": "Record then polish",
        "desc": "Start host record → agent demos → stop → viral pack",
        "steps": ["studio_record_start", "(demo)", "studio_record_stop", "studio_viral"],
        "say": "Record a demo and polish it",
        "skills": ["studio_record_start", "studio_record_stop", "studio_viral"],
    },
    {
        "id": "preset_export",
        "name": "Single preset export",
        "desc": "Render one preset (rotato_phone | x_screencast | macbook_web | clean_demo)",
        "steps": ["studio_list_recordings", "studio_render"],
        "say": "Render rotato_phone from latest",
        "skills": ["studio_render"],
    },
    {
        "id": "storyboard",
        "name": "Demo storyboard",
        "desc": "Plan hook → proof → CTA beats for a product demo",
        "steps": ["studio_storyboard"],
        "say": "Storyboard a POCKET demo for X",
        "skills": ["studio_storyboard"],
    },
    {
        "id": "caption_handoff",
        "name": "Caption → Desk",
        "desc": "Write launch copy + social posts; hand to Grok on desk",
        "steps": ["studio_caption", "studio_handoff_desk"],
        "say": "Write captions for this demo and open Desk",
        "skills": ["studio_caption"],
    },
    {
        "id": "imagine_still",
        "name": "Imagine still",
        "desc": "Compose device-frame still (phone/web) from screenshot",
        "steps": ["screenshot", "imagine_compose"],
        "say": "Compose a rotato phone still",
        "skills": ["imagine_compose", "compose_device"],
    },
    {
        "id": "full_agent_demo",
        "name": "Full agent demo loop",
        "desc": "One intent: record and ship → demo → stop and ship",
        "steps": [
            "studio_full_loop (record and ship)",
            "(demo on desk)",
            "studio_full_loop (stop and ship)",
        ],
        "say": "Record and ship a POCKET demo",
        "skills": ["studio_full_loop", "studio_ship"],
    },
]

AGENT_FEATURES: List[Dict[str, str]] = [
    {"id": "status", "skill": "studio_status", "use": "Health: ffmpeg, counts, surfaces"},
    {"id": "map", "skill": "studio_map", "use": "Full studio map for agents"},
    {"id": "record", "skill": "studio_record_start", "use": "Start SPECULUM full-desktop record"},
    {"id": "stop", "skill": "studio_record_stop", "use": "Stop record → mp4 in ~/.pocket/recordings"},
    {"id": "list_rec", "skill": "studio_list_recordings", "use": "List host recordings"},
    {"id": "list_exp", "skill": "studio_list_exports", "use": "List polished exports"},
    {"id": "presets", "skill": "studio_presets", "use": "Viral presets catalog"},
    {"id": "render", "skill": "studio_render", "use": "One preset ffmpeg polish"},
    {"id": "viral", "skill": "studio_viral", "use": "Phone remake + web + screencast pack"},
    {"id": "batch", "skill": "studio_batch", "use": "Multi-preset batch from one source"},
    {"id": "storyboard", "skill": "studio_storyboard", "use": "Hook/proof/CTA demo plan"},
    {"id": "caption", "skill": "studio_caption", "use": "Launch + social copy for exports"},
    {"id": "ship", "skill": "studio_ship", "use": "End-to-end: viral pack + caption + paths"},
    {"id": "full_loop", "skill": "studio_full_loop", "use": "One prompt: record and ship / stop and ship"},
    {"id": "compose", "skill": "imagine_compose", "use": "Still device composition"},
    {"id": "open", "skill": "studio_open", "use": "Studio surface URLs for desk/phone"},
    {"id": "playbooks", "skill": "studio_playbooks", "use": "Agent playbook catalog"},
]


def studio_map() -> Dict[str, Any]:
    """First-class discover payload for every agent."""
    return {
        "ok": True,
        "protocol": PROTOCOL_ID,
        "product": PRODUCT,
        "first_class": True,
        "doctrine": [
            "Studio is a first-class agent surface — not only a human export page",
            "Record on host → polish with real ffmpeg / device remake",
            "Glass CONTAIN — never stretch-crop product UI",
            "Agents call skills; users can also use /studio UI",
        ],
        "surfaces": [
            {"id": "product_studio", "where": "/studio", "for": "Recordings · presets · viral exports"},
            {
                "id": "loomgraph",
                "where": "/loomgraph",
                "for": "LOOMGRAPH — default graph+loop harness (see the graph, run the loop)",
            },
            {
                "id": "creative_studio",
                "where": "/studio/create",
                "for": "Friendly chat · image · video · blog · paper · social",
            },
            {
                "id": "community",
                "where": "/community",
                "for": "Intentional public shares from Pocket users (opt-in only)",
            },
            {"id": "voice_studio", "where": "/studio/voice", "for": "V2V canvas · persona · code snap"},
            {"id": "work_studio", "where": "/work", "for": "Digital assistant loops (separate)"},
            {"id": "imagine", "where": "POST /v1/imagine/compose", "for": "Still device frames"},
        ],
        "agent_features": AGENT_FEATURES,
        "playbooks": PLAYBOOKS,
        "api": {
            "status": "GET /v1/studio",
            "first_class": "GET /v1/studio/first-class",
            "agent": "POST /v1/studio/agent",
            "recordings": "GET /v1/studio/recordings",
            "exports": "GET /v1/studio/exports",
            "presets": "GET /v1/studio/presets",
            "render": "POST /v1/studio/render",
            "batch": "POST /v1/studio/batch",
            "auto": "POST /v1/studio/auto",
            "storyboard": "POST /v1/studio/storyboard",
            "caption": "POST /v1/studio/caption",
            "ship": "POST /v1/studio/ship",
            "creative": "GET /v1/creative · POST /v1/creative/chat",
            "community": "GET /v1/community · POST /v1/community/share",
        },
        "skills": [f["skill"] for f in AGENT_FEATURES],
        "desk_agent": "studio",
        "latin": "STUDIO",
        "say_examples": [p["say"] for p in PLAYBOOKS],
    }


def first_class_status() -> Dict[str, Any]:
    """Unified studio health for desk rail + agents."""
    out: Dict[str, Any] = {
        "ok": True,
        "first_class": True,
        "protocol": PROTOCOL_ID,
        "product": PRODUCT,
        "ts": time.time(),
    }
    try:
        from pocket.video_studio import studio_status, list_recordings, list_exports, list_presets

        vs = studio_status()
        out["video"] = vs
        out["recordings"] = list_recordings(8)
        out["exports"] = list_exports(8)
        out["presets"] = [p.get("id") for p in list_presets()]
    except Exception as e:
        out["video"] = {"ok": False, "error": str(e)[:160]}
    try:
        from pocket.imagine_studio import status as imagine_status

        out["imagine"] = imagine_status()
    except Exception as e:
        out["imagine"] = {"ok": False, "error": str(e)[:120]}
    try:
        from pocket.screen_record import record_status

        out["recording"] = record_status() if callable(record_status) else {}
    except Exception:
        try:
            from pocket.screen_record import status as rec_status

            out["recording"] = rec_status()
        except Exception:
            out["recording"] = {"active": None}
    try:
        from pocket.live import lan_ip

        ip = lan_ip()
        out["urls"] = {
            "local": "http://127.0.0.1:8787/studio",
            "lan": f"http://{ip}:8787/studio" if ip else None,
            "voice": "http://127.0.0.1:8787/studio/voice",
            "work": "http://127.0.0.1:8787/work",
            "creative": "http://127.0.0.1:8787/studio/create",
            "community": "http://127.0.0.1:8787/community",
        }
    except Exception:
        out["urls"] = {
            "local": "/studio",
            "creative": "/studio/create",
            "community": "/community",
        }
    try:
        from pocket.creative_studio import status as creative_status

        out["creative"] = creative_status()
    except Exception as e:
        out["creative"] = {"ok": False, "error": str(e)[:120]}
    try:
        from pocket.community_share import status as community_status

        out["community"] = community_status()
    except Exception as e:
        out["community"] = {"ok": False, "error": str(e)[:120]}
    out["playbooks"] = len(PLAYBOOKS)
    out["agent_features"] = len(AGENT_FEATURES)
    out["ready"] = bool((out.get("video") or {}).get("ffmpeg"))
    creative_ok = bool((out.get("creative") or {}).get("ok"))
    community_ok = bool((out.get("community") or {}).get("ok"))
    out["creative_first_class"] = creative_ok
    out["community_first_class"] = community_ok
    out["message"] = (
        "Studio first-class · ffmpeg · Creative chat · Community shares"
        if out["ready"] and creative_ok
        else (
            "Studio first-class · install ffmpeg for full export polish"
            if not out["ready"]
            else "Studio first-class · Creative/Community surfaces online"
        )
    )
    return out


def storyboard(prompt: str = "", *, product: str = "POCKET") -> Dict[str, Any]:
    """Plan a product demo storyboard agents can execute."""
    p = (prompt or "").strip() or f"Show {product} as a host co-pilot"
    low = p.lower()
    beats: List[Dict[str, Any]] = [
        {
            "beat": 1,
            "name": "Hook",
            "seconds": "0–3",
            "on_screen": f"{product} desk opens · one clear product shot",
            "agent_action": "studio_record_start + open /desk",
            "caption": "Your PC already has a co-pilot.",
        },
        {
            "beat": 2,
            "name": "Proof",
            "seconds": "3–12",
            "on_screen": "Real host action (screen sense / life op / code)",
            "agent_action": "screen_sense or life skill or codex demo",
            "caption": "Agents run tools on the host — not just chat.",
        },
        {
            "beat": 3,
            "name": "Polish",
            "seconds": "export",
            "on_screen": "Rotato phone + X screencast + MacBook web",
            "agent_action": "studio_viral",
            "caption": "Ship-ready demos from the same recording.",
        },
        {
            "beat": 4,
            "name": "CTA",
            "seconds": "end card",
            "on_screen": "Brand + try URL",
            "agent_action": "studio_caption + handoff desk",
            "caption": "ItsNotAI Labs · pocket.local",
        },
    ]
    if re.search(r"\b(voice|aria|v2v)\b", low):
        beats[1]["on_screen"] = "Voice Studio canvas · Aria · fusion"
        beats[1]["agent_action"] = "seat voice + open /studio/voice"
    if re.search(r"\b(food|flight|shop|life)\b", low):
        beats[1]["on_screen"] = "Working board life ops (never auto-pay)"
        beats[1]["agent_action"] = "food_order / flight_search demo"
    if re.search(r"\b(capsule|wasm|webgpu|sandbox)\b", low):
        beats[1]["on_screen"] = "Capsule allocate + WebGPU probe"
        beats[1]["agent_action"] = "capsule_allocate enableWebGPU + execute"
    return {
        "ok": True,
        "skill": "studio_storyboard",
        "product": product,
        "prompt": p[:300],
        "beats": beats,
        "presets_for_export": ["rotato_phone", "x_screencast", "macbook_web"],
        "next": "studio_record_start → demo → studio_record_stop → studio_viral",
        "message": f"Storyboard ready · {len(beats)} beats for {product}",
    }


def caption_pack(
    prompt: str = "",
    *,
    title: str = "POCKET",
    subtitle: str = "Host co-pilot",
    cta: str = "ItsNotAI Labs",
    brand: str = "ItsNotAI Labs",
) -> Dict[str, Any]:
    """Marketing copy agents can attach to exports (no LLM required)."""
    focus = (prompt or subtitle or "real host agents").strip()[:120]
    launch = (
        f"{title} is a host co-pilot: agents that actually run tools on your PC. "
        f"{focus}. Record → polish → ship from Product Studio."
    )
    posts = [
        f"Stop chatting about tools. {title} runs them on the host.\n\n{cta}",
        f"New demo: {subtitle}\n\n· Real screen\n· Real agents\n· Viral export pack\n\n{brand}",
        f"Product Studio just polished a host recording into phone + web + screencast.\n\n{title} · {cta}",
    ]
    hashtags = ["#AI", "#Agents", "#BuildInPublic", "#ItsNotAILabs", "#POCKET"]
    return {
        "ok": True,
        "skill": "studio_caption",
        "title": title,
        "subtitle": subtitle,
        "cta": cta,
        "brand": brand,
        "launch_blurb": launch,
        "social_posts": posts,
        "hashtags": hashtags,
        "x_compose_hint": posts[0][:260],
        "handoff_prompt": (
            f"Product Studio handoff — polish this demo copy:\n"
            f"Title: {title}\nSubtitle: {subtitle}\nCTA: {cta}\n\n{launch}\n\n"
            "Write a short launch blurb and 3 social posts."
        ),
        "message": "Caption pack ready for Desk / X",
    }


def studio_open() -> Dict[str, Any]:
    try:
        from pocket.live import lan_ip

        ip = lan_ip()
    except Exception:
        ip = ""
    return {
        "ok": True,
        "skill": "studio_open",
        "studio": "/studio",
        "voice_studio": "/studio/voice",
        "work_studio": "/work",
        "local": "http://127.0.0.1:8787/studio",
        "lan": f"http://{ip}:8787/studio" if ip else None,
        "desk_tab": "Product Studio",
        "agent": "studio",
        "skills": [f["skill"] for f in AGENT_FEATURES],
        "message": "Open Product Studio — first-class for agents and humans",
    }


def full_loop(
    prompt: str = "",
    *,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """One-intent studio pipeline for agents.

    - record and ship / full demo → start record + storyboard (user demos, then stop+ship)
    - stop and ship / finish demo → stop record + viral + caption ship
    - ship / viral only → ship latest recording
    """
    params = params or {}
    low = (prompt or "").lower()
    title = params.get("title") or "POCKET"
    subtitle = params.get("subtitle") or "Host co-pilot"
    cta = params.get("cta") or "ItsNotAI Labs"
    brand = params.get("brand") or "ItsNotAI Labs"
    t0 = time.time()
    steps: List[Dict[str, Any]] = []

    want_start = bool(
        re.search(
            r"\b(record and ship|full (demo|loop)|start (a )?demo|demo then ship|"
            r"record then (ship|polish)|begin full)\b",
            low,
        )
    )
    want_finish = bool(
        re.search(
            r"\b(stop and ship|finish (the )?demo|end (and )?ship|stop record(ing)? and ship|"
            r"done recording|wrap (the )?demo)\b",
            low,
        )
    )
    want_ship_only = bool(re.search(r"\b(ship|viral|polish)\b", low)) and not want_start

    if want_start and not want_finish:
        board = storyboard(prompt or f"{title} demo", product=title)
        steps.append({"step": "storyboard", "ok": True, "beats": [b.get("name") for b in board.get("beats") or []]})
        try:
            from pocket.screen_record import record_status, record_start

            st = record_status() if callable(record_status) else {}
            if st.get("active") or st.get("recording"):
                steps.append({"step": "record_start", "ok": True, "already": True})
            else:
                rs = record_start(label=params.get("label") or "studio-full-loop")
                steps.append({"step": "record_start", "ok": bool(rs.get("ok", True)), "result": rs})
        except Exception as e:
            steps.append({"step": "record_start", "ok": False, "error": str(e)[:160]})
        return {
            "ok": True,
            "skill": "studio_full_loop",
            "phase": "recording",
            "steps": steps,
            "storyboard": board,
            "message": (
                "Recording armed + storyboard ready. Demo on the desk (Hook → Proof). "
                "When finished say: **stop and ship** (or skill studio_full_loop finish)."
            ),
            "next": "stop and ship",
            "ms": int((time.time() - t0) * 1000),
        }

    if want_finish or (want_ship_only and re.search(r"\bstop\b", low)):
        try:
            from pocket.screen_record import record_stop, record_status

            st = record_status() if callable(record_status) else {}
            if st.get("active") or st.get("recording") or want_finish:
                rs = record_stop()
                steps.append({"step": "record_stop", "ok": bool(rs.get("ok", True)), "result": rs})
            else:
                steps.append({"step": "record_stop", "ok": True, "skipped": True})
        except Exception as e:
            steps.append({"step": "record_stop", "ok": False, "error": str(e)[:160]})

    if want_finish or want_ship_only:
        shipped = ship(
            source=params.get("source") or "",
            title=title,
            subtitle=subtitle,
            caption=params.get("caption") or "",
            cta=cta,
            brand=brand,
            prompt=prompt,
        )
        steps.append({"step": "ship", "ok": bool(shipped.get("ok")), "exports": shipped.get("exports")})
        return {
            "ok": bool(shipped.get("ok")),
            "skill": "studio_full_loop",
            "phase": "shipped",
            "steps": steps,
            "ship": shipped,
            "message": shipped.get("message") or "Full loop ship complete",
            "ms": int((time.time() - t0) * 1000),
        }

    # Default: status + how to run full loop
    st = first_class_status()
    return {
        "ok": True,
        "skill": "studio_full_loop",
        "phase": "idle",
        "status": st,
        "message": "Say **record and ship** to arm recording, or **stop and ship** to polish latest.",
        "say": ["record and ship", "stop and ship", "viral pack", "storyboard a demo"],
        "ms": int((time.time() - t0) * 1000),
    }


def ship(
    *,
    source: str = "",
    title: str = "POCKET",
    subtitle: str = "Host co-pilot",
    caption: str = "",
    cta: str = "ItsNotAI Labs",
    brand: str = "ItsNotAI Labs",
    prompt: str = "",
) -> Dict[str, Any]:
    """End-to-end agent ship: viral pack + caption + storyboard summary."""
    t0 = time.time()
    from pocket.video_studio import auto_viral_pack, list_recordings

    if not source:
        recs = list_recordings(1)
        if not recs:
            return {
                "ok": False,
                "error": "no recordings — run studio_record_start first, demo, then studio_record_stop",
                "hint": "skill studio_record_start",
            }
        source = recs[0]["path"]
    pack = auto_viral_pack(
        source,
        title=title,
        subtitle=subtitle,
        caption=caption or subtitle,
        cta=cta,
        brand=brand,
    )
    caps = caption_pack(prompt or subtitle, title=title, subtitle=subtitle, cta=cta, brand=brand)
    board = storyboard(prompt or f"{title} demo", product=title)
    exports = []
    for e in pack.get("exports") or []:
        if isinstance(e, dict) and e.get("ok"):
            exports.append(
                {
                    "name": e.get("name") or Path(str(e.get("output") or "")).name,
                    "output": e.get("output") or e.get("path") or "",
                    "preset": e.get("preset") or e.get("method"),
                }
            )
    return {
        "ok": bool(pack.get("ok")),
        "skill": "studio_ship",
        "source": source,
        "viral": pack,
        "caption": caps,
        "storyboard_summary": [b["name"] for b in board.get("beats") or []],
        "exports": exports,
        "ms": int((time.time() - t0) * 1000),
        "message": pack.get("message") or "Studio ship complete",
        "next_steps": [
            "Open /studio to preview exports",
            "Post with caption pack social_posts",
            "Or seat Grok with handoff_prompt",
        ],
    }


def run_studio_skill(
    skill_id: str,
    *,
    prompt: str = "",
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Dispatch any first-class studio skill for agents."""
    sid = (skill_id or "").strip().lower().replace("-", "_")
    params = params or {}
    p = prompt or params.get("text") or params.get("prompt") or ""

    if sid in ("studio_map", "studio_first_class", "product_studio_map"):
        return studio_map()

    if sid in ("studio_status", "studio", "product_studio"):
        return first_class_status()

    if sid in ("studio_open", "open_studio", "studio_surface"):
        return studio_open()

    if sid in ("studio_playbooks", "studio_playbook", "studio_features"):
        return {
            "ok": True,
            "playbooks": PLAYBOOKS,
            "features": AGENT_FEATURES,
            "count": len(PLAYBOOKS),
        }

    if sid in ("studio_storyboard", "storyboard", "demo_storyboard"):
        return storyboard(
            p,
            product=params.get("product") or params.get("title") or "POCKET",
        )

    if sid in ("studio_caption", "studio_copy", "demo_caption"):
        return caption_pack(
            p,
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or p[:80] or "Host co-pilot",
            cta=params.get("cta") or "ItsNotAI Labs",
            brand=params.get("brand") or "ItsNotAI Labs",
        )

    if sid in ("studio_list_recordings", "list_recordings", "studio_recordings"):
        from pocket.video_studio import list_recordings

        recs = list_recordings(int(params.get("limit") or 40))
        return {"ok": True, "recordings": recs, "count": len(recs)}

    if sid in ("studio_list_exports", "list_exports", "studio_exports"):
        from pocket.video_studio import list_exports

        ex = list_exports(int(params.get("limit") or 40))
        return {"ok": True, "exports": ex, "count": len(ex)}

    if sid in ("studio_presets", "list_presets"):
        from pocket.video_studio import list_presets

        return {"ok": True, "presets": list_presets()}

    if sid in ("studio_record_start", "record_start", "start_record"):
        from pocket.screen_record import record_start

        return record_start(label=params.get("label") or "studio-agent")

    if sid in ("studio_record_stop", "record_stop", "stop_record"):
        from pocket.screen_record import record_stop

        return record_stop()

    if sid in ("studio_render",):
        from pocket.video_studio import render, list_recordings

        source = params.get("source") or params.get("path") or ""
        if not source or not Path(str(source)).is_file():
            # allow preset name only in prompt
            recs = list_recordings(1)
            source = recs[0]["path"] if recs else ""
        if not source:
            return {"ok": False, "error": "no recording source"}
        preset = params.get("preset") or "rotato_phone"
        # parse preset from prompt
        for key in (
            "rotato_phone",
            "x_screencast",
            "macbook_web",
            "clean_demo",
            "story_stack",
            "viral_phone",
            "viral_web",
            "square_social",
        ):
            if key.replace("_", " ") in p.lower() or key in p.lower():
                preset = key
                break
        return render(
            source,
            preset=preset,
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or p[:80] or "Host co-pilot",
            caption=params.get("caption") or params.get("subtitle") or "",
            cta=params.get("cta") or "ItsNotAI Labs",
        )

    if sid in ("studio_viral", "studio_auto", "viral_pack", "studio_polish"):
        from pocket.video_studio import auto_viral_pack

        return auto_viral_pack(
            params.get("source") or p if (p and Path(p).is_file()) else params.get("source") or "",
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or "Real host co-pilot",
            caption=params.get("caption") or "Studio polish",
            cta=params.get("cta") or "ItsNotAI Labs",
            brand=params.get("brand") or "ItsNotAI Labs",
        )

    if sid in ("studio_batch", "batch_render"):
        from pocket.video_studio import render_batch, list_recordings

        source = params.get("source") or ""
        if not source:
            recs = list_recordings(1)
            source = recs[0]["path"] if recs else ""
        if not source:
            return {"ok": False, "error": "no recording"}
        return render_batch(
            source,
            presets=params.get("presets"),
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or "Host co-pilot",
            caption=params.get("caption") or "",
            cta=params.get("cta") or "ItsNotAI Labs",
        )

    if sid in ("studio_ship", "ship_studio", "studio_demo_ship"):
        return ship(
            source=params.get("source") or "",
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or "Host co-pilot",
            caption=params.get("caption") or "",
            cta=params.get("cta") or "ItsNotAI Labs",
            brand=params.get("brand") or "ItsNotAI Labs",
            prompt=p,
        )

    if sid in ("studio_full_loop", "full_loop", "demo_loop", "studio_loop"):
        return full_loop(p, params=params)

    if sid in ("imagine_compose", "imagine_still", "compose_device"):
        from pocket.imagine_studio import compose

        return compose(
            mode=params.get("mode") or params.get("preset") or "rotato_phone",
            image=params.get("image") or params.get("path") or "",
            title=params.get("title") or "POCKET",
            subtitle=params.get("subtitle") or p or "Host co-pilot",
        )

    return {
        "ok": False,
        "error": f"unknown studio skill: {sid}",
        "available": [f["skill"] for f in AGENT_FEATURES],
        "hint": "GET /v1/studio/first-class",
    }


def is_studio_skill(skill_id: str) -> bool:
    sid = (skill_id or "").strip().lower().replace("-", "_")
    known = {
        "studio_map",
        "studio_first_class",
        "product_studio_map",
        "studio_status",
        "studio",
        "product_studio",
        "studio_open",
        "open_studio",
        "studio_surface",
        "studio_playbooks",
        "studio_playbook",
        "studio_features",
        "studio_storyboard",
        "storyboard",
        "demo_storyboard",
        "studio_caption",
        "studio_copy",
        "demo_caption",
        "studio_list_recordings",
        "list_recordings",
        "studio_recordings",
        "studio_list_exports",
        "list_exports",
        "studio_exports",
        "studio_presets",
        "list_presets",
        "studio_record_start",
        "studio_record_stop",
        "studio_render",
        "studio_viral",
        "studio_auto",
        "viral_pack",
        "studio_polish",
        "studio_batch",
        "batch_render",
        "studio_ship",
        "ship_studio",
        "studio_demo_ship",
        "studio_full_loop",
        "full_loop",
        "demo_loop",
        "studio_loop",
        "imagine_compose",
        "imagine_still",
        "compose_device",
    }
    return sid in known or sid.startswith("studio_")


def agent_brief(*, max_chars: int = 700) -> str:
    lines = [
        "POCKET Product Studio (first-class for agents):",
        "· Skills: studio_map, studio_status, studio_record_start/stop, studio_viral, studio_render, studio_ship, studio_storyboard, studio_caption",
        "· UI: /studio · Voice: /studio/voice · API: GET /v1/studio/first-class",
        "· Flow: record → demo → stop → viral pack → caption → ship",
        "· Glass CONTAIN only — never stretch-crop UI into bezels",
        "· Seat desk agent `studio` or call POST /v1/skills/run",
    ]
    return "\n".join(lines)[:max_chars]
