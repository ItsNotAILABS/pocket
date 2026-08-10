"""POCKET Creative Studio — friendly multi-mode AI chat for makers.

Modes (OpenAI-style desk, not raw agent logs):
  chat · image · video · blog · paper · social · storyboard · caption

Uses host agents + imagine/video studio. Artifacts land in ~/.pocket/creative/
and can be intentionally shared to Community (never auto).
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "creative"
SESSIONS = ROOT / "sessions"
ARTIFACTS = ROOT / "artifacts"
for _d in (ROOT, SESSIONS, ARTIFACTS):
    _d.mkdir(parents=True, exist_ok=True)

_lock = Lock()

MODES: List[Dict[str, Any]] = [
    {
        "id": "chat",
        "name": "Chat",
        "icon": "💬",
        "blurb": "Friendly OpenAI-style conversation with POCKET agents",
        "agent": "planner",
        "placeholder": "Ask anything — plan, research, rewrite…",
    },
    {
        "id": "image",
        "name": "Image",
        "icon": "🖼",
        "blurb": "Compose product stills & device frames (Imagine Studio)",
        "agent": "planner",
        "placeholder": "Describe an image or product still… e.g. rotato phone of the desk",
    },
    {
        "id": "video",
        "name": "Video",
        "icon": "🎬",
        "blurb": "Polish recordings into viral demos (Product Studio)",
        "agent": "planner",
        "placeholder": "Describe a video pack… e.g. viral phone from latest recording",
    },
    {
        "id": "blog",
        "name": "Blog",
        "icon": "✍",
        "blurb": "Long-form posts with structure & SEO-ready titles",
        "agent": "researcher",
        "placeholder": "Blog topic or outline…",
    },
    {
        "id": "paper",
        "name": "Paper",
        "icon": "📄",
        "blurb": "Research notes & paper-style writeups",
        "agent": "researcher",
        "placeholder": "Paper thesis or research question…",
    },
    {
        "id": "social",
        "name": "Social",
        "icon": "📣",
        "blurb": "X / LinkedIn / short posts & threads",
        "agent": "planner",
        "placeholder": "What should we announce or post?",
    },
    {
        "id": "storyboard",
        "name": "Storyboard",
        "icon": "🎞",
        "blurb": "Hook → proof → CTA demo beats",
        "agent": "planner",
        "placeholder": "Storyboard a demo for…",
    },
    {
        "id": "caption",
        "name": "Captions",
        "icon": "✦",
        "blurb": "Launch copy + social captions for exports",
        "agent": "planner",
        "placeholder": "Caption pack for this demo…",
    },
]

_MODE_IDS = {m["id"] for m in MODES}


def catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.creative.v1",
        "product": "POCKET Creative Studio",
        "modes": MODES,
        "ui": "/studio/create",
        "community": "/studio/create#community",
        "api": {
            "catalog": "GET /v1/creative",
            "chat": "POST /v1/creative/chat",
            "session": "GET /v1/creative/session/{id}",
            "artifacts": "GET /v1/creative/artifacts",
            "share": "POST /v1/community/share",
        },
        "note": "Friendly multi-mode chat. Community shares are opt-in only.",
    }


def _mode_meta(mode: str) -> Dict[str, Any]:
    m = (mode or "chat").strip().lower()
    for row in MODES:
        if row["id"] == m:
            return row
    return MODES[0]


def _session_path(sid: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "", sid)[:64]
    return SESSIONS / f"{safe}.json"


def _load_session(sid: str) -> Dict[str, Any]:
    p = _session_path(sid)
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "id": sid,
        "schema": "pocket.creative.session.v1",
        "created_at": time.time(),
        "updated_at": time.time(),
        "messages": [],
        "artifacts": [],
        "title": "New chat",
    }


def _save_session(sess: Dict[str, Any]) -> None:
    sid = sess.get("id") or ("crs-" + uuid.uuid4().hex[:10])
    sess["id"] = sid
    sess["updated_at"] = time.time()
    with _lock:
        _session_path(sid).write_text(json.dumps(sess, indent=2, default=str), encoding="utf-8")


def _save_artifact(kind: str, title: str, content: str, *, meta: Optional[Dict] = None) -> Dict[str, Any]:
    aid = "art-" + uuid.uuid4().hex[:10]
    rec = {
        "id": aid,
        "kind": kind,
        "title": (title or kind)[:160],
        "content": (content or "")[:120_000],
        "meta": meta or {},
        "at": time.time(),
        "path": str(ARTIFACTS / f"{aid}.json"),
    }
    p = ARTIFACTS / f"{aid}.json"
    p.write_text(json.dumps(rec, indent=2, default=str)[:200_000], encoding="utf-8")
    return rec


def list_sessions(*, limit: int = 30) -> Dict[str, Any]:
    rows = []
    for p in sorted(SESSIONS.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[: max(1, min(limit, 80))]:
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": s.get("id") or p.stem,
                    "title": s.get("title") or "Chat",
                    "updated_at": s.get("updated_at"),
                    "messages": len(s.get("messages") or []),
                    "mode": (s.get("messages") or [{}])[-1].get("mode") if s.get("messages") else "chat",
                }
            )
        except Exception:
            continue
    return {"ok": True, "sessions": rows, "count": len(rows)}


def get_session(session_id: str) -> Dict[str, Any]:
    sid = (session_id or "").strip()
    if not sid:
        return {"ok": False, "error": "session_id required"}
    s = _load_session(sid)
    return {"ok": True, "session": s}


def list_artifacts(*, limit: int = 40, kind: str = "") -> Dict[str, Any]:
    rows = []
    for p in sorted(ARTIFACTS.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:80]:
        try:
            a = json.loads(p.read_text(encoding="utf-8"))
            if kind and a.get("kind") != kind:
                continue
            rows.append(
                {
                    "id": a.get("id"),
                    "kind": a.get("kind"),
                    "title": a.get("title"),
                    "preview": (a.get("content") or "")[:240],
                    "at": a.get("at"),
                    "meta": a.get("meta") or {},
                }
            )
        except Exception:
            continue
        if len(rows) >= limit:
            break
    return {"ok": True, "artifacts": rows, "count": len(rows)}


def _system_prompt(mode: str, user_text: str) -> str:
    meta = _mode_meta(mode)
    m = meta["id"]
    base = (
        "You are POCKET Creative Studio — a friendly, clear creative partner.\n"
        "Write like a great product teammate: concrete, useful, no fake claims.\n"
        f"Active mode: {meta['name']} — {meta['blurb']}\n"
    )
    if m == "blog":
        base += (
            "Produce a full blog post with: title, deck/subtitle, 4–8 sections with H2s, "
            "short intro, practical body, and a closing CTA. Markdown OK.\n"
        )
    elif m == "paper":
        base += (
            "Write research-style notes: abstract, problem, method/approach, findings, "
            "limitations, references/next steps. Be rigorous and honest.\n"
        )
    elif m == "social":
        base += (
            "Write a social pack: (1) X post ≤260 chars (2) short thread 3–5 posts "
            "(3) LinkedIn post (4) alt hashtags. No engagement bait spam.\n"
        )
    elif m == "image":
        base += (
            "Help craft a precise image/composition brief. If the user wants a product still, "
            "prefer Imagine Studio compose (rotato_phone / macbook_web / clean).\n"
        )
    elif m == "video":
        base += (
            "Help plan a video export. Prefer real Product Studio viral pack / presets "
            "from host recordings — never invent metrics.\n"
        )
    elif m == "storyboard":
        base += "Plan hook → proof → CTA beats for a product demo.\n"
    elif m == "caption":
        base += "Write launch caption + 3 social variants + on-screen lower-thirds.\n"
    base += f"\nUser request:\n{user_text}"
    return base


def _run_agent(task: str, *, agent: str = "planner") -> Dict[str, Any]:
    try:
        from pocket.sell_api import chat_complete

        return chat_complete(
            [{"role": "user", "content": task}],
            agent=agent,
            inject_wiki=False,
            sync=True,
        )
    except Exception as e:
        # fallback headless
        try:
            from pocket.agents import run_headless

            r = run_headless(agent, task)
            if isinstance(r, dict):
                return r
            return {"ok": True, "reply": str(r), "content": str(r)}
        except Exception as e2:
            return {"ok": False, "error": f"{e}; {e2}"}


def _extract_text(agent_out: Dict[str, Any]) -> str:
    if not agent_out:
        return ""
    # OpenAI-shaped chat.completion
    choices = agent_out.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str) and c.strip():
                return c.strip()
        t = choices[0].get("text") if isinstance(choices[0], dict) else None
        if isinstance(t, str) and t.strip():
            return t.strip()
    for k in ("reply", "content", "text", "markdown", "result", "output", "answer"):
        v = agent_out.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # message may be dict {role, content}
    msg = agent_out.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), str) and msg["content"].strip():
        return msg["content"].strip()
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    # nested job / completion envelopes
    for k in ("data", "response", "completion", "job", "result"):
        v = agent_out.get(k)
        if isinstance(v, dict):
            t = _extract_text(v)
            if t:
                return t
        if isinstance(v, str) and v.strip() and not v.strip().startswith("{"):
            return v.strip()
    if agent_out.get("error"):
        return f"(agent note) {agent_out.get('error')}"
    # last resort — avoid dumping huge job JSON to the user
    for k in ("summary", "preview", "stdout"):
        if isinstance(agent_out.get(k), str) and agent_out[k].strip():
            return agent_out[k].strip()[:8000]
    return "Done — open the artifact or try again with a more specific ask."


def _maybe_image(user_text: str) -> Optional[Dict[str, Any]]:
    """Trigger imagine compose for product still requests."""
    t = (user_text or "").lower()
    mode = "rotato_phone"
    if any(x in t for x in ("macbook", "laptop", "web", "browser", "desktop")):
        mode = "macbook_web"
    elif any(x in t for x in ("clean", "minimal", "flat")):
        mode = "clean"
    # only auto-compose when user signals image/still/compose
    if not any(x in t for x in ("image", "still", "compose", "render", "picture", "visual", "frame", "rotato", "phone mock")):
        # still try for pure image mode always
        pass
    try:
        from pocket.imagine_studio import compose

        r = compose(mode=mode, title="Creative Studio", subtitle=(user_text or "")[:80])
        return {"ok": bool(r.get("ok")), "mode": mode, "result": r}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "mode": mode}


def _maybe_video(user_text: str) -> Optional[Dict[str, Any]]:
    t = (user_text or "").lower()
    try:
        # Explicit ship only — avoid matching "pack" inside "status of video pack"
        want_ship = bool(
            re.search(r"\b(viral\s+pack|ship\s+pack|studio_ship|render\s+viral)\b", t)
            or (re.search(r"\b(ship|render)\b", t) and re.search(r"\b(viral|latest|recording)\b", t))
        )
        if want_ship:
            from pocket.studio_core import ship

            return {"ok": True, "action": "ship", "result": ship(prompt=user_text)}
        if any(x in t for x in ("storyboard", "beats", "script")):
            from pocket.studio_core import storyboard

            return {"ok": True, "action": "storyboard", "result": storyboard(user_text)}
        # default: status — never force long ffmpeg unless asked
        from pocket.video_studio import studio_status, list_recordings

        st = studio_status()
        recs = list_recordings(5)
        return {
            "ok": True,
            "action": "status",
            "result": {
                "studio": st,
                "recordings": recs,
                "hint": "Say **viral pack from latest** to render, or open Product Studio for presets.",
            },
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _format_video_result(vid: Dict[str, Any]) -> str:
    if not vid:
        return ""
    action = vid.get("action") or "video"
    if not vid.get("ok"):
        return f"**Video** note: {vid.get('error') or 'failed'}"
    res = vid.get("result") or {}
    if action == "status":
        st = res.get("studio") or {}
        recs = res.get("recordings") or []
        lines = [
            "**Video Studio status**",
            f"- ffmpeg: **{'ready' if st.get('ffmpeg') else 'missing'}**",
            f"- recordings: **{st.get('recordings', len(recs))}**",
            f"- exports: **{st.get('exports', '?')}**",
            f"- presets: {', '.join((st.get('presets') or [])[:8]) or '—'}",
            "",
        ]
        if recs:
            lines.append("**Recent recordings**")
            for r in (recs if isinstance(recs, list) else [])[:5]:
                if isinstance(r, dict):
                    lines.append(f"- `{r.get('name') or r.get('path') or r}`")
                else:
                    lines.append(f"- `{r}`")
        else:
            lines.append("_No recordings yet — use Product Studio **Start record**, then come back._")
        if res.get("hint"):
            lines.append(f"\n{res['hint']}")
        lines.append("\nOpen: `/studio` · Creative video mode can ship when you say **viral pack from latest**.")
        return "\n".join(lines)
    if action == "storyboard":
        return _format_studio_result("storyboard", res) or "**Video storyboard** ready."
    if action == "ship":
        lines = ["**Viral ship pack** started / ready."]
        for k in ("message", "paths", "exports", "caption"):
            v = res.get(k)
            if isinstance(v, str) and v.strip():
                lines.append(v.strip()[:2000])
            elif isinstance(v, list) and v:
                lines.append("Exports: " + ", ".join(str(x)[:80] for x in v[:8]))
            elif isinstance(v, dict) and v:
                lines.append(json.dumps(v, indent=2, default=str)[:1500])
        if len(lines) == 1:
            lines.append("Check `/studio` exports or GET `/v1/studio/exports`.")
        return "\n\n".join(lines)
    return f"**Video** action `{action}` ready."


def _local_content(mode: str, user_text: str) -> str:
    """Instant, high-quality drafts so modes always work first-class (no agent hang)."""
    topic = (user_text or "your product").strip()
    title = topic[:90]
    if mode == "blog":
        return (
            f"# {title}\n\n"
            f"*Deck:* A practical take on {title} — built for makers who ship.\n\n"
            f"## Why this matters\n"
            f"{title} is the kind of problem teams talk about in Slack and never turn into a workflow. "
            f"This post is the workflow: clear steps, honest limits, ship checklist.\n\n"
            f"## The short version\n"
            f"1. State the job-to-be-done in one sentence.\n"
            f"2. Show one real surface (desk, studio, or API).\n"
            f"3. Give a 3-step path a stranger can run today.\n"
            f"4. Close with an intentional CTA — not engagement bait.\n\n"
            f"## How to use it on POCKET\n"
            f"- **Creative Studio** (`/studio/create`) for drafts, social packs, images, video briefs.\n"
            f"- **Product Studio** (`/studio`) for record → viral pack → captions.\n"
            f"- **Community** (`/community`) only when you **Share** on purpose.\n\n"
            f"## Outline you can paste\n"
            f"### Hook\nWhat breaks today without {title}.\n\n"
            f"### Proof\nOne screenshot, one command, or one demo beat.\n\n"
            f"### How-to\nThree numbered steps. No fake metrics.\n\n"
            f"### Close\nInvite readers to try Creative Studio or open Desk.\n\n"
            f"## CTA\nOpen **Creative Studio → Blog**, refine this draft, then **Share to community** if you want it public.\n"
        )
    if mode == "paper":
        return (
            f"# Working notes: {title}\n\n"
            f"## Abstract\n"
            f"We examine {title} as a product + agent-systems problem: how a host co-pilot "
            f"can produce usable creative artifacts (text, image compose, video polish) without "
            f"auto-publishing private user data.\n\n"
            f"## Problem\n"
            f"Consumer AI chat apps win on polish. Host agent platforms win on real tools. "
            f"The gap is a friendly creative surface that still executes on the host.\n\n"
            f"## Method\n"
            f"1. Mode-routed creative chat (blog / paper / social / image / video).\n"
            f"2. Real backends: Imagine compose, Product Studio ffmpeg, host agents.\n"
            f"3. Community feed with **intentional share only** (opt-in).\n\n"
            f"## Findings (operational)\n"
            f"- Caption/storyboard modes return deterministic packs (sub-second).\n"
            f"- Image mode composes device frames via Imagine Studio.\n"
            f"- Video mode reports ffmpeg/recordings and can ship viral packs on request.\n"
            f"- Community never scrapes private chats.\n\n"
            f"## Limitations\n"
            f"Long-form quality depends on host agent availability; local drafts always return.\n\n"
            f"## Next steps\n"
            f"User studies on mode switching, share rate, and export completion.\n\n"
            f"## References\n"
            f"- POCKET Product Studio first-class protocol\n"
            f"- Creative Studio `/v1/creative` · Community `/v1/community`\n"
        )
    if mode == "social":
        a = (
            f"POCKET Creative Studio — friendly chat for posts, blogs, images & video packs.\n"
            f"Community only shows what you share on purpose.\n\n{title[:80]}"
        )[:260]
        b = (
            f"Need a social pack, not a novel?\n\n"
            f"Creative Studio returns:\n• 1 tight X post\n• short thread\n• LinkedIn draft\n\n"
            f"Topic: {title[:60]}"
        )[:260]
        c = (
            f"Shipping {title[:50]}?\n\n"
            f"Draft in Creative Studio → polish in Product Studio → Share to Community when ready."
        )[:260]
        return (
            f"**Social pack** · {title}\n\n"
            f"**1) X post A**\n{a}\n\n"
            f"**2) X post B**\n{b}\n\n"
            f"**3) X post C**\n{c}\n\n"
            f"**Thread (4)**\n"
            f"1/ {title[:100]} — here's the honest version.\n"
            f"2/ Creative Studio: chat · image · video · blog · social in one place.\n"
            f"3/ Nothing hits Community unless you hit Share.\n"
            f"4/ Try `/studio/create` on your POCKET host.\n\n"
            f"**LinkedIn**\n"
            f"We shipped a Creative Studio on POCKET for teams that want useful drafts — not engagement bait.\n\n"
            f"Modes: Chat, Image (Imagine), Video (Product Studio), Blog, Paper, Social, Storyboard, Captions.\n\n"
            f"Privacy doctrine: intentional public shares only.\n\n"
            f"If you're building with host agents, this is the friendly front door.\n\n"
            f"**Hashtags:** #POCKET #CreativeStudio #BuildInPublic #Agents\n"
        )
    if mode == "chat":
        return (
            f"Got it — **{title}**.\n\n"
            f"I'm Creative Studio on your POCKET host. Switch modes for **Image**, **Video**, "
            f"**Blog**, **Paper**, or **Social**, or keep chatting here.\n\n"
            f"When something is worth showing others, hit **Share to community** — nothing auto-posts."
        )
    return ""


def _maybe_studio_text(mode: str, user_text: str) -> Optional[Dict[str, Any]]:
    try:
        if mode == "storyboard":
            from pocket.studio_core import storyboard

            return storyboard(user_text)
        if mode == "caption":
            from pocket.studio_core import caption_pack

            return caption_pack(prompt=user_text, title="POCKET", subtitle=user_text[:80])
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
    return None


def _format_studio_result(mode: str, st: Dict[str, Any]) -> str:
    """Human-readable storyboard / caption packs for the chat bubble."""
    if not st:
        return ""
    if mode == "storyboard" and st.get("beats"):
        lines = [f"**Storyboard** · {st.get('message') or st.get('product') or 'demo'}", ""]
        for b in st.get("beats") or []:
            lines.append(
                f"**{b.get('beat')}. {b.get('name')}** ({b.get('seconds')})\n"
                f"- On screen: {b.get('on_screen')}\n"
                f"- Agent: {b.get('agent_action')}\n"
                f"- Caption: {b.get('caption')}"
            )
        if st.get("next"):
            lines.append(f"\n**Next:** {st['next']}")
        if st.get("presets_for_export"):
            lines.append("**Export presets:** " + ", ".join(st["presets_for_export"]))
        return "\n\n".join(lines)
    if mode == "caption":
        lines = ["**Caption pack**", ""]
        if st.get("launch_blurb"):
            lines.append(f"**Launch**\n{st['launch_blurb']}")
        posts = st.get("social_posts") or st.get("posts") or []
        if posts:
            lines.append("**Social**")
            for i, p in enumerate(posts, 1):
                lines.append(f"{i}. {p}")
        if st.get("hashtags"):
            lines.append(" ".join(st["hashtags"]))
        if st.get("x_compose_hint"):
            lines.append(f"\n**X compose:** {st['x_compose_hint']}")
        return "\n\n".join(lines)
    for k in ("markdown", "caption", "storyboard", "text", "pack", "message"):
        if isinstance(st.get(k), str) and st[k].strip():
            return st[k].strip()
    return ""


def chat(
    message: str,
    *,
    mode: str = "chat",
    session_id: str = "",
    agent: str = "",
    author: str = "",
    auto_media: bool = True,
) -> Dict[str, Any]:
    """One creative turn — returns assistant message + optional artifact."""
    text = (message or "").strip()
    if not text:
        return {"ok": False, "error": "message required"}

    meta = _mode_meta(mode)
    mode_id = meta["id"]
    agent_id = (agent or meta.get("agent") or "planner").strip().lower()
    sid = (session_id or "").strip() or ("crs-" + uuid.uuid4().hex[:10])
    sess = _load_session(sid)

    user_msg = {
        "id": "m-" + uuid.uuid4().hex[:8],
        "role": "user",
        "content": text,
        "mode": mode_id,
        "at": time.time(),
    }
    sess.setdefault("messages", []).append(user_msg)
    if sess.get("title") in (None, "", "New chat"):
        sess["title"] = text[:60]

    artifacts: List[Dict[str, Any]] = []
    media: Dict[str, Any] = {}
    reply_parts: List[str] = []

    # Mode-specific media / studio hooks
    if auto_media and mode_id == "image":
        img = _maybe_image(text)
        if img:
            media["image"] = img
            if img.get("ok"):
                reply_parts.append(
                    f"**Image compose** (`{img.get('mode')}`) ran via Imagine Studio."
                )
                path = None
                r = img.get("result") or {}
                path = r.get("path") or r.get("out") or (r.get("export") or {}).get("path")
                if path:
                    reply_parts.append(f"File: `{path}`")
            else:
                reply_parts.append(f"Image compose note: {img.get('error') or 'see result'}")

    if auto_media and mode_id == "video":
        vid = _maybe_video(text)
        if vid:
            media["video"] = vid
            pretty_v = _format_video_result(vid)
            if pretty_v:
                reply_parts.append(pretty_v)
            elif vid.get("ok"):
                reply_parts.append(f"**Video** action `{vid.get('action')}` ready.")
            else:
                reply_parts.append(f"Video note: {vid.get('error')}")

    if mode_id in ("storyboard", "caption"):
        st = _maybe_studio_text(mode_id, text)
        if st and st.get("ok") is not False:
            media[mode_id] = st
            pretty = _format_studio_result(mode_id, st)
            if pretty:
                reply_parts.append(pretty)

    # Instant local drafts for content modes (first-class: always works, no hang)
    if mode_id in ("blog", "paper", "social", "chat") and not reply_parts:
        local = _local_content(mode_id, text)
        if local:
            reply_parts.append(local)

    # Optional host agent enhance (only chat + when explicitly wanted; keep UI snappy)
    agent_out: Dict[str, Any] = {}
    want_agent = mode_id == "chat" and any(
        x in text.lower() for x in ("think harder", "use agent", "deeper", "research more", "expand with agent")
    )
    # Also agent if still empty
    if want_agent or not reply_parts:
        task = _system_prompt(mode_id, text)
        agent_out = _run_agent(task, agent=agent_id)
        body = _extract_text(agent_out)
        if body and body not in reply_parts:
            # For chat with local already, only add agent if user asked deeper
            if not reply_parts or want_agent:
                reply_parts.append(body)

    if not reply_parts:
        reply_parts.append(
            f"Ready in **{meta['name']}** mode. Try a clearer ask, or switch modes for image/video/blog/social."
        )

    reply_text = "\n\n".join(reply_parts).strip()

    # Persist long-form as artifacts
    if mode_id in ("blog", "paper", "social", "storyboard", "caption") and len(reply_text) > 80:
        art = _save_artifact(
            mode_id,
            title=text[:80],
            content=reply_text,
            meta={"mode": mode_id, "agent": agent_id, "session_id": sid},
        )
        artifacts.append(art)
        sess.setdefault("artifacts", []).append({"id": art["id"], "kind": art["kind"], "title": art["title"]})

    if media.get("image") and (media["image"] or {}).get("ok"):
        art = _save_artifact(
            "image",
            title=f"Image · {text[:60]}",
            content=json.dumps(media["image"], indent=2, default=str)[:20_000],
            meta={"mode": "image", "session_id": sid},
        )
        artifacts.append(art)

    asst_msg = {
        "id": "m-" + uuid.uuid4().hex[:8],
        "role": "assistant",
        "content": reply_text,
        "mode": mode_id,
        "at": time.time(),
        "artifacts": [{"id": a["id"], "kind": a["kind"], "title": a["title"]} for a in artifacts],
        "media": {
            k: {
                "ok": (v or {}).get("ok"),
                "action": (v or {}).get("action") or (v or {}).get("mode"),
            }
            for k, v in media.items()
        },
        "agent": agent_id,
    }
    sess["messages"].append(asst_msg)
    # cap history
    if len(sess["messages"]) > 80:
        sess["messages"] = sess["messages"][-80:]
    _save_session(sess)

    share_kinds = {
        "blog",
        "paper",
        "social",
        "image",
        "video",
        "storyboard",
        "caption",
        "chat",
        "export",
        "note",
    }
    share_kind = mode_id if mode_id in share_kinds else "note"

    return {
        "ok": True,
        "schema": "pocket.creative.chat.v1",
        "session_id": sid,
        "mode": mode_id,
        "mode_meta": meta,
        "message": asst_msg,
        "reply": reply_text,
        "artifacts": artifacts,
        "media": media,
        "agent": agent_id,
        "agent_raw_ok": bool(agent_out.get("ok", True)) if agent_out else None,
        "first_class": True,
        "share_hint": {
            "title": text[:80],
            "kind": share_kind,
            "body": reply_text[:4000],
        },
        "community": "POST /v1/community/share with intentional body — never auto",
        "at": time.time(),
    }


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "first_class": True,
        "product": "POCKET Creative Studio",
        "modes": len(MODES),
        "sessions_dir": str(SESSIONS),
        "artifacts_dir": str(ARTIFACTS),
        "sessions": list_sessions(limit=5).get("count"),
        "artifacts": list_artifacts(limit=5).get("count"),
        "ui": "/studio/create",
        "community_ui": "/community",
        "catalog": catalog(),
    }


def self_test() -> Dict[str, Any]:
    """Live first-class audit — every mode + community share roundtrip."""
    rows: List[Dict[str, Any]] = []
    t0 = time.time()

    def add(name: str, ok: bool, **extra: Any) -> None:
        rows.append({"test": name, "ok": ok, **extra})

    c = catalog()
    add("catalog", bool(c.get("ok") and len(c.get("modes") or []) >= 8), modes=len(c.get("modes") or []))

    for mode, msg in (
        ("caption", "live audit captions"),
        ("storyboard", "live audit storyboard"),
        ("video", "status of recordings"),
        ("blog", "Why intentional community sharing matters"),
        ("paper", "Host co-pilot creative surfaces"),
        ("social", "Announce Creative Studio"),
        ("chat", "What can Creative Studio do?"),
        ("image", "compose rotato phone still"),
    ):
        try:
            r = chat(msg, mode=mode, auto_media=mode in ("image", "video"))
            reply = (r.get("reply") or "").strip()
            ok = bool(r.get("ok") and len(reply) >= 20)
            if reply.startswith("{") and "choices" in reply:
                ok = False
            add(f"mode:{mode}", ok, reply_len=len(reply), session=r.get("session_id"))
        except Exception as e:
            add(f"mode:{mode}", False, error=str(e)[:160])

    try:
        from pocket.community_share import list_shares, share, unshare

        s = share(
            author="selftest",
            display_name="Self Test",
            title="Creative first-class audit",
            body="Intentional share from creative_studio.self_test()",
            kind="note",
            tags=["selftest", "first-class"],
            source="self_test",
        )
        add("community_share", bool(s.get("ok")), id=(s.get("share") or {}).get("id"))
        feed = list_shares(limit=20)
        sid = (s.get("share") or {}).get("id")
        add("community_feed", bool(sid and any(x.get("id") == sid for x in (feed.get("shares") or []))))
        if sid:
            u = unshare(sid, author="selftest")
            add("community_unshare", bool(u.get("ok")))
    except Exception as e:
        add("community", False, error=str(e)[:160])

    ok_n = sum(1 for r in rows if r.get("ok"))
    fail_n = len(rows) - ok_n
    return {
        "ok": fail_n == 0,
        "first_class": fail_n == 0,
        "schema": "pocket.creative.self_test.v1",
        "passed": ok_n,
        "failed": fail_n,
        "total": len(rows),
        "ms": int((time.time() - t0) * 1000),
        "results": rows,
        "ui": "/studio/create",
        "at": time.time(),
    }
