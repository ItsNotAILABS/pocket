"""Persistent Working Mode — live voice + screen/hardware agent.

A real working session (not a one-shot chat):
  · Optional Aria voice (live talk)
  · Screen share View/Control (fusion eyes + mouse)
  · Chrome / Edge automation for the *agent* (not user tab spam)
  · Hardware VComputer (desktop, shell)
  · Continuous turn log → package → hand off artifacts (html, md, pixel, github)

Desk mode: `work` / `working` / `live_work`
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "work_mode"
ROOT.mkdir(parents=True, exist_ok=True)

_sessions: Dict[str, Dict[str, Any]] = {}


def _path(sid: str) -> Path:
    return ROOT / f"{sid}.json"


def _save(sess: Dict[str, Any]) -> None:
    sid = sess["id"]
    _sessions[sid] = sess
    _path(sid).write_text(json.dumps(sess, indent=2, default=str), encoding="utf-8")


def _load(sid: str) -> Optional[Dict[str, Any]]:
    if sid in _sessions:
        return _sessions[sid]
    p = _path(sid)
    if p.exists():
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            _sessions[sid] = s
            return s
        except Exception:
            return None
    return None


def start_work(
    *,
    session_id: str = "",
    voice: bool = True,
    screen: str = "control",
    chrome: bool = True,
    goal: str = "",
) -> Dict[str, Any]:
    """Boot persistent working mode."""
    sid = (session_id or "").strip() or f"work-{uuid.uuid4().hex[:10]}"
    screen = (screen or "view").lower()
    if screen not in ("off", "view", "control"):
        screen = "view"

    # Arm screen share for all agents
    try:
        from pocket.screen_share import set_share

        set_share(mode=screen, vcomp=True, label="work-mode")
    except Exception as e:
        emit("work", f"screen arm fail: {e}", agent="WORK", role="host", level="warn")

    # Arm VComputer
    try:
        from pocket.virtual_computer import open_computer

        open_computer(label="work-mode")
    except Exception:
        pass

    sess = {
        "id": sid,
        "status": "live",
        "voice": bool(voice),
        "screen": screen,
        "chrome": bool(chrome),
        "goal": (goal or "").strip()[:500],
        "turns": [],
        "senses": [],
        "actions": [],
        "packages": [],
        "artifacts": [],
        "created_at": time.time(),
        "updated_at": time.time(),
        "persistent": True,
        "engine": "work",
    }
    # Opening note
    sess["turns"].append({
        "role": "system",
        "text": (
            "Working mode live. Voice=" + ("on" if voice else "off")
            + f" · screen={screen} · chrome_agent={chrome}. "
            "I execute on hardware/Chrome as the agent — not by opening tabs for you. "
            "Say ‘package’ to bag this convo; ‘handoff’ to make artifacts."
        ),
        "at": time.time(),
    })
    _save(sess)
    emit("work", f"working mode ON {sid}", agent="WORK", role="host")
    return {"ok": True, "session": sess, "message": f"Working mode live · {sid}"}


def status(session_id: str = "") -> Dict[str, Any]:
    if session_id:
        s = _load(session_id)
        if not s:
            return {"ok": False, "error": "session not found"}
        return {"ok": True, "session": s}
    # list recent
    items = []
    for p in sorted(ROOT.glob("work-*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            items.append({
                "id": s.get("id"),
                "status": s.get("status"),
                "goal": s.get("goal"),
                "turns": len(s.get("turns") or []),
                "updated_at": s.get("updated_at"),
            })
        except Exception:
            continue
    return {"ok": True, "sessions": items, "live": sum(1 for i in items if i.get("status") == "live")}


def append_turn(session_id: str, *, role: str = "user", text: str = "") -> Dict[str, Any]:
    s = _load(session_id)
    if not s:
        return {"ok": False, "error": "start work mode first"}
    s.setdefault("turns", []).append({
        "role": role,
        "text": (text or "")[:8000],
        "at": time.time(),
    })
    s["updated_at"] = time.time()
    _save(s)
    return {"ok": True, "turns": len(s["turns"])}


def tick(session_id: str = "") -> Dict[str, Any]:
    """One persistent step: sense screen if shared, log fusion brief."""
    # pick latest live if empty
    if not session_id:
        st = status()
        for it in st.get("sessions") or []:
            if it.get("status") == "live":
                session_id = it["id"]
                break
    s = _load(session_id or "")
    if not s or s.get("status") != "live":
        return {"ok": False, "error": "no live work session"}

    sense_rec: Dict[str, Any] = {"at": time.time()}
    try:
        from pocket.screen_share import fusion_context, status as sc_st

        sc = sc_st()
        if sc.get("can_view"):
            cx = fusion_context(agent="work")
            sense_rec["brief"] = cx.get("brief")
            sense_rec["symbols"] = (cx.get("symbols_sample") or [])[:12]
            sense_rec["mode"] = cx.get("mode")
        else:
            sense_rec["brief"] = "screen share off"
    except Exception as e:
        sense_rec["error"] = str(e)[:160]

    s.setdefault("senses", []).append(sense_rec)
    s["senses"] = s["senses"][-40:]
    s["updated_at"] = time.time()
    _save(s)
    return {"ok": True, "session_id": s["id"], "sense": sense_rec}


def package_session(session_id: str) -> Dict[str, Any]:
    """Bag conversation + senses into a handoff package (details for artifacts)."""
    s = _load(session_id)
    if not s:
        return {"ok": False, "error": "session not found"}

    turns = s.get("turns") or []
    senses = s.get("senses") or []
    user_bits = [t.get("text") for t in turns if t.get("role") == "user" and t.get("text")]
    agent_bits = [t.get("text") for t in turns if t.get("role") in ("assistant", "agent", "aria", "work") and t.get("text")]
    goal = s.get("goal") or (user_bits[0] if user_bits else "Working session")

    # Extract likely artifact intents
    blob = " ".join(user_bits + agent_bits).lower()
    wants = []
    if any(w in blob for w in ("html", "website", "ui", "page", "landing", "app")):
        wants.append("html")
    if any(w in blob for w in ("readme", "doc", "spec", "plan", "notes")):
        wants.append("md")
    if any(w in blob for w in ("github", "pr", "repo", "commit")):
        wants.append("github")
    if any(w in blob for w in ("pixel", "artifact", "memory")):
        wants.append("pixel")
    if any(w in blob for w in ("simulate", "demo", "preview")):
        wants.append("simulation")
    if not wants:
        wants = ["md", "html"]

    package = {
        "id": f"pkg-{uuid.uuid4().hex[:10]}",
        "session_id": s["id"],
        "goal": goal[:400],
        "created_at": time.time(),
        "voice": s.get("voice"),
        "screen": s.get("screen"),
        "chrome": s.get("chrome"),
        "turn_count": len(turns),
        "sense_count": len(senses),
        "user_turns": user_bits[-20:],
        "agent_turns": agent_bits[-20:],
        "last_sense": (senses[-1] if senses else {}),
        "artifact_kinds": wants,
        "summary": _summarize(goal, user_bits, agent_bits, senses),
    }
    s.setdefault("packages", []).append(package)
    s["last_package"] = package
    s["updated_at"] = time.time()
    _save(s)
    # persist package file
    (ROOT / f"{package['id']}.json").write_text(json.dumps(package, indent=2), encoding="utf-8")
    emit("work", f"package {package['id']}", agent="WORK", role="host")
    return {"ok": True, "package": package}


def _summarize(goal: str, user: List[str], agent: List[str], senses: List[Dict]) -> str:
    lines = [f"Goal: {goal}", ""]
    lines.append("## Conversation highlights")
    for u in user[-8:]:
        lines.append(f"- User: {u[:200]}")
    for a in agent[-6:]:
        lines.append(f"- Agent: {a[:200]}")
    if senses:
        lines.append("")
        lines.append("## Screen senses")
        for sn in senses[-5:]:
            lines.append(f"- {sn.get('brief') or sn.get('error') or '—'}")
    return "\n".join(lines)


def handoff_artifacts(
    session_id: str,
    *,
    kinds: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create artifacts from last package (or package now)."""
    s = _load(session_id)
    if not s:
        return {"ok": False, "error": "session not found"}
    pkg = s.get("last_package")
    if not pkg:
        packed = package_session(session_id)
        if not packed.get("ok"):
            return packed
        pkg = packed["package"]
        s = _load(session_id) or s

    kinds = kinds or pkg.get("artifact_kinds") or ["md", "html"]
    made: List[Dict[str, Any]] = []
    summary = pkg.get("summary") or pkg.get("goal") or "Work package"
    title = re.sub(r"[^\w\s-]", "", (pkg.get("goal") or "work")[:48]).strip() or "work-package"

    if "md" in kinds or "markdown" in kinds:
        try:
            from pocket.pixel_vmem import put_artifact

            a = put_artifact(
                f"# Work package\n\n{summary}\n\n```json\n{json.dumps(pkg, indent=2)[:6000]}\n```\n",
                title=f"{title}-notes",
                language="md",
                agent="work",
                agent_role="handoff",
                run_id=pkg.get("id") or session_id,
                tags=["work_mode", "handoff", "package"],
            )
            made.append({"kind": "pixel_md", **a})
        except Exception as e:
            made.append({"kind": "md", "ok": False, "error": str(e)})

    if "html" in kinds or "simulation" in kinds or "preview" in kinds:
        try:
            from pocket.work_surface import create_draft

            html = (
                f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title>"
                f"<style>body{{font-family:system-ui;margin:24px;background:#0a0a0c;color:#e4e4e7}}"
                f"pre{{background:#141416;padding:12px;border-radius:8px;overflow:auto}}"
                f"h1{{color:#fafafa}}</style></head><body>"
                f"<h1>{title}</h1><p>Packaged from working mode session "
                f"<code>{session_id}</code>.</p>"
                f"<h2>Summary</h2><pre>{_esc(summary[:4000])}</pre>"
                f"<p>Promote this draft when ready → folder or GitHub.</p>"
                f"</body></html>"
            )
            d = create_draft(
                title=title,
                kind="html" if "html" in kinds else "simulation",
                content=html,
                layer="preview",
                source=f"work_mode:{session_id}",
                meta={"package_id": pkg.get("id"), "goal": pkg.get("goal")},
            )
            made.append({"kind": "draft_html", **d})
        except Exception as e:
            made.append({"kind": "html", "ok": False, "error": str(e)})

    if "pixel" in kinds:
        try:
            from pocket.pixel_vmem import put_artifact

            a = put_artifact(
                summary[:8000],
                title=f"{title}-pixel",
                language="md",
                agent="work",
                run_id=pkg.get("id") or "",
                tags=["work_mode", "pixel"],
            )
            made.append({"kind": "pixel", **a})
        except Exception as e:
            made.append({"kind": "pixel", "ok": False, "error": str(e)})

    if "github" in kinds:
        made.append({
            "kind": "github",
            "ok": True,
            "message": "Package ready — promote draft or run github agent `create repo` when you confirm.",
            "next": "POST /v1/drafts/promote {target:github} or pick GitHub agent",
        })

    s.setdefault("artifacts", []).extend(made)
    s["updated_at"] = time.time()
    # assistant turn
    s.setdefault("turns", []).append({
        "role": "assistant",
        "text": f"Handoff complete — made {len(made)} artifact surface(s): "
                + ", ".join(m.get("kind") or "?" for m in made),
        "at": time.time(),
    })
    _save(s)
    emit("work", f"handoff {session_id} n={len(made)}", agent="WORK", role="host")

    # fence for desk bubble if any preview
    fence = ""
    for m in made:
        if m.get("fence"):
            fence = m["fence"]
            break
        if m.get("preview_url"):
            fence = f"```preview\ntitle: {title}\nurl: {m['preview_url']}\n```\n"
            break

    return {
        "ok": True,
        "session_id": session_id,
        "package_id": pkg.get("id"),
        "artifacts": made,
        "fence": fence,
        "message": "Artifacts packaged from working conversation",
    }


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def stop_work(session_id: str) -> Dict[str, Any]:
    s = _load(session_id)
    if not s:
        return {"ok": False, "error": "not found"}
    s["status"] = "stopped"
    s["updated_at"] = time.time()
    _save(s)
    return {"ok": True, "id": session_id, "status": "stopped"}


def run_work_turn(prompt: str, *, session_id: str = "", job_id: str = "") -> Dict[str, Any]:
    """Working-state turn: multi-intent → board rows → real tools → table.

    This is NOT coding chat. User can say:
      buy this · analyze my business · reserve a restaurant
    and get a live Working board with tools actually run.
    """
    text = (prompt or "").strip()
    low = text.lower()

    # Ensure a live session
    st = status()
    live_id = session_id
    if not live_id:
        for it in st.get("sessions") or []:
            if it.get("status") == "live":
                live_id = it["id"]
                break
    if not live_id or low in ("start", "begin", "work on", "start work", "working"):
        goal = text if low not in ("start", "begin", "start work", "working") else ""
        boot = start_work(session_id=live_id or "", voice=True, screen="control", chrome=True, goal=goal)
        live_id = boot.get("session", {}).get("id") or live_id
        if low in ("start", "begin", "start work", "working") or not text:
            try:
                from pocket.working_board import board_table, load_board, save_board

                b = load_board()
                b["session_id"] = live_id or ""
                if goal:
                    b["goal"] = goal[:400]
                b["status"] = "live"
                save_board(b)
                table = board_table(b)
            except Exception:
                table = ""
            return {
                **boot,
                "reply": (
                    "**Working state is live** — not coding chat.\n\n"
                    "Tell me real work in plain language, e.g.:\n"
                    "- *Buy wireless headphones for under $100*\n"
                    "- *Look at this analysis for my business today*\n"
                    "- *Make a restaurant reservation for Friday 7pm*\n\n"
                    "I’ll split multi-part asks into a **board table**, run host tools "
                    "(research, screen, open), and stop at **needs you** for pay/book/send.\n\n"
                    + (table or "Board is empty — send your first ask.")
                ),
                "board_table": table,
            }

    append_turn(live_id, role="user", text=text)

    # Explicit board / package commands
    if low in ("package", "bag", "summarize work"):
        p = package_session(live_id)
        reply = f"Packaged session. Kinds: {p.get('package', {}).get('artifact_kinds')}. Say **handoff** to make artifacts."
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "package": p.get("package"), "session_id": live_id}

    if low in ("handoff", "make artifacts", "ship package", "create artifacts"):
        h = handoff_artifacts(live_id)
        reply = h.get("message") or "Handoff done."
        if h.get("fence"):
            reply += "\n\n" + h["fence"]
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "handoff": h, "session_id": live_id}

    if low in ("tick", "sense", "look", "what's on my screen", "whats on my screen"):
        t = tick(live_id)
        brief = (t.get("sense") or {}).get("brief") or "sensed"
        try:
            from pocket.working_board import ingest_and_run

            br = ingest_and_run(f"capture: {brief}", session_id=live_id, execute=True)
            reply = f"Sense: {brief}\n\n" + (br.get("table") or "")
        except Exception:
            reply = f"Sense: {brief}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "tick": t, "session_id": live_id}

    if low in ("stop", "end work", "stop work"):
        stop_work(live_id)
        reply = "Working mode stopped. Board kept — say **board** anytime."
        return {"ok": True, "reply": reply, "session_id": live_id}

    # Low-level actuators still available
    if low.startswith("click "):
        from pocket.screen_share import act_for_agent

        r = act_for_agent("click", agent="work", name=text.split(None, 1)[1].strip())
        reply = f"Click → ok={r.get('ok')} {r.get('matched') or r.get('error') or ''}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "act": r, "session_id": live_id}

    if low.startswith("type "):
        from pocket.screen_share import act_for_agent

        r = act_for_agent("type", agent="work", text=text.split(None, 1)[1])
        reply = f"Type → ok={r.get('ok')}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "act": r, "session_id": live_id}

    if low.startswith("cli ") or low.startswith("run "):
        from pocket.cli_tools import run_cli

        rest = text.split(None, 1)[1]
        parts = rest.split()
        r = run_cli(parts[0], parts[1:] if len(parts) > 1 else [])
        reply = f"CLI `{parts[0]}` → rc={r.get('returncode')} · {(r.get('stdout') or r.get('error') or '')[:400]}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "cli": r, "session_id": live_id}

    if low.startswith("mcp "):
        from pocket.mcp_bundle import invoke

        bits = text.split(None, 3)
        server = bits[1] if len(bits) > 1 else "pocket"
        tool = bits[2] if len(bits) > 2 else "screen_status"
        r = invoke(server, tool)
        reply = f"MCP {server}.{tool} → ok={r.get('ok')}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply + f"\n\n```json\n{json.dumps(r, indent=2)[:2000]}\n```", "mcp": r, "session_id": live_id}

    if low.startswith("chrome ") or low.startswith("open url "):
        url = text.split(None, 2)[-1] if low.startswith("open url") else text.split(None, 1)[1]
        try:
            from pocket.virtual_computer import act

            r = act("open_url", url=url)
            reply = f"Agent opened URL (single controlled navigation): {url} · ok={r.get('ok')}"
        except Exception as e:
            reply = f"Chrome agent failed: {e}"
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": True, "reply": reply, "session_id": live_id}

    # === Primary path: Working board (multi-intent + tools + table) ===
    try:
        from pocket.working_board import ingest_and_run

        tick(live_id)
        br = ingest_and_run(text, session_id=live_id, goal="", execute=True, job_id=job_id or "")
        reply = br.get("reply") or br.get("table") or "Board updated."
        append_turn(live_id, role="assistant", text=reply[:8000])
        # Link board into work session
        s = _load(live_id)
        if s:
            s.setdefault("actions", []).append({
                "at": time.time(),
                "kind": "board",
                "ran": br.get("ran"),
                "items": len(br.get("items_added") or []),
            })
            s["updated_at"] = time.time()
            _save(s)
        return {
            "ok": True,
            "reply": reply,
            "session_id": live_id,
            "board": br.get("board"),
            "table": br.get("table"),
            "items_added": br.get("items_added"),
            "working": True,
        }
    except Exception as e:
        tick(live_id)
        s = _load(live_id) or {}
        last = (s.get("senses") or [{}])[-1]
        reply = (
            f"Working board error: {e}. "
            f"Screen: {last.get('brief') or '—'}. Try again with a clear ask."
        )
        append_turn(live_id, role="assistant", text=reply)
        return {"ok": False, "reply": reply, "session_id": live_id, "error": str(e)[:200]}
