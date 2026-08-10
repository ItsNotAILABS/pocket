"""Working board — the operational work surface (not coding chat).

User says things like:
  "Buy this for me, look at this analysis for my business today,
   and make a restaurant reservation."

We split that into board rows, run real host tools for each row, and keep
everything in one table the user can see and continue. Coding/chat agents
are separate; this is the Working state.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pocket.live_events import emit

ROOT = Path.home() / ".pocket" / "working_board"
ROOT.mkdir(parents=True, exist_ok=True)
BOARD_PATH = ROOT / "board.json"

# kind → how we execute
KIND_META = {
    "buy": {
        "label": "Purchase",
        "icon": "🛒",
        "risk": "high",
        "human_gate": True,
        "hint": "Research + cart scaffold only — you confirm any payment",
    },
    "shop": {
        "label": "Shopping",
        "icon": "🛍",
        "risk": "high",
        "human_gate": True,
        "hint": "Compare products · open Amazon/shopping — you pay",
    },
    "food_order": {
        "label": "Food delivery",
        "icon": "🛵",
        "risk": "high",
        "human_gate": True,
        "hint": "DoorDash / Uber Eats options — you place the order",
    },
    "flight": {
        "label": "Flights",
        "icon": "✈",
        "risk": "high",
        "human_gate": True,
        "hint": "Google Flights / Kayak — you book and pay",
    },
    "browse": {
        "label": "Web",
        "icon": "🌐",
        "risk": "low",
        "human_gate": False,
        "hint": "Open sites and search in host Edge",
    },
    "reservation": {
        "label": "Reservation",
        "icon": "🍽",
        "risk": "medium",
        "human_gate": True,
        "hint": "Search · open OpenTable · drive Find a table / time — you confirm final book",
    },
    "analysis": {
        "label": "Analysis",
        "icon": "📊",
        "risk": "low",
        "human_gate": False,
        "hint": "Research + notes on the board",
    },
    "research": {
        "label": "Research",
        "icon": "🔎",
        "risk": "low",
        "human_gate": False,
        "hint": "Web + screen sense → findings table",
    },
    "notify": {
        "label": "Notify",
        "icon": "📬",
        "risk": "medium",
        "human_gate": True,
        "hint": "Draft message — you send",
    },
    "schedule": {
        "label": "Schedule",
        "icon": "📅",
        "risk": "medium",
        "human_gate": True,
        "hint": "Draft calendar steps — you confirm",
    },
    "capture": {
        "label": "Capture",
        "icon": "👁",
        "risk": "low",
        "human_gate": False,
        "hint": "Screen sense / screenshot",
    },
    "open": {
        "label": "Open / navigate",
        "icon": "🌐",
        "risk": "low",
        "human_gate": False,
        "hint": "Agent-controlled single navigation",
    },
    "errand": {
        "label": "Errand",
        "icon": "✓",
        "risk": "medium",
        "human_gate": True,
        "hint": "General working task",
    },
}


def _empty_board() -> Dict[str, Any]:
    return {
        "id": "board-main",
        "schema": "pocket.working_board.v2",
        "title": "Working board",
        "status": "live",
        "items": [],
        "created_at": time.time(),
        "updated_at": time.time(),
        "session_id": "",
        "goal": "",
        "last_activity": "",
    }


def _hits_lines(sr: Dict[str, Any], *, n: int = 5) -> Tuple[List[str], List[Dict[str, str]]]:
    hits = sr.get("results") or sr.get("items") or []
    lines: List[str] = []
    links: List[Dict[str, str]] = []
    if not isinstance(hits, list):
        return lines, links
    for i, h in enumerate(hits[:n], 1):
        if isinstance(h, dict):
            title = str(h.get("title") or h.get("text") or "result")[:120]
            url = str(h.get("url") or "")[:240]
            snip = str(h.get("snippet") or "")[:160]
            lines.append(
                f"{i}. **{title}**"
                + (f" — {snip}" if snip else "")
                + (f"\n   {url}" if url else "")
            )
            if url:
                links.append({"title": title, "url": url, "snippet": snip})
        else:
            lines.append(f"{i}. {h}")
    return lines, links


def load_board() -> Dict[str, Any]:
    if BOARD_PATH.exists():
        try:
            d = json.loads(BOARD_PATH.read_text(encoding="utf-8"))
            if isinstance(d, dict) and isinstance(d.get("items"), list):
                return d
        except Exception:
            pass
    return _empty_board()


def save_board(board: Dict[str, Any]) -> None:
    board["updated_at"] = time.time()
    BOARD_PATH.write_text(json.dumps(board, indent=2, default=str), encoding="utf-8")
    # history snapshot
    try:
        snap = ROOT / f"snap-{int(time.time())}.json"
        snap.write_text(json.dumps(board, indent=2, default=str), encoding="utf-8")
        # keep last 30 snaps
        snaps = sorted(ROOT.glob("snap-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in snaps[30:]:
            try:
                old.unlink()
            except Exception:
                pass
    except Exception:
        pass


def board_table(board: Optional[Dict[str, Any]] = None) -> str:
    """Markdown table — the working surface users expect."""
    b = board or load_board()
    items = b.get("items") or []
    lines = [
        f"## Working board · {b.get('status', 'live')}",
        "",
        f"_Goal:_ {b.get('goal') or '— (say what you need done today)'}",
        "",
        "| # | Kind | Task | Status | Result |",
        "|---|------|------|--------|--------|",
    ]
    if not items:
        lines.append("| — | — | _empty — tell me what to do_ | — | — |")
    else:
        for i, it in enumerate(items, 1):
            kind = it.get("kind") or "errand"
            meta = KIND_META.get(kind) or {}
            icon = meta.get("icon") or "·"
            st = it.get("status") or "queued"
            title = (it.get("title") or "")[:60].replace("|", "/")
            res = (it.get("result_summary") or it.get("notes") or "—")[:80].replace("|", "/")
            lines.append(
                f"| {i} | {icon} {kind} | {title} | **{st}** | {res} |"
            )
    needs = [it for it in items if it.get("status") == "needs_you"]
    active = [it for it in items if it.get("status") in ("active", "queued", "running")]
    done = [it for it in items if it.get("status") == "done"]
    lines.append("")
    lines.append(
        f"**{len(active)}** in flight · **{len(needs)}** need you · **{len(done)}** done · "
        f"{len(items)} total"
    )
    if needs:
        lines.append("")
        lines.append("### Needs you")
        for it in needs:
            lines.append(
                f"- **{it.get('title')}** — {it.get('gate_message') or it.get('result_summary') or 'confirm'}"
            )
    return "\n".join(lines)


def parse_intents(text: str) -> List[Dict[str, Any]]:
    """Split a natural multi-request utterance into board items."""
    raw = (text or "").strip()
    if not raw:
        return []

    # Normalize connectors so multi-asks always split
    norm = re.sub(r"\s*,\s*(and\s+)?", " · ", raw, flags=re.I)
    norm = re.sub(r"\s+\band also\b\s+", " · ", norm, flags=re.I)
    norm = re.sub(r"\s+\balso\b\s+", " · ", norm, flags=re.I)
    norm = re.sub(r"\s+\bthen\b\s+", " · ", norm, flags=re.I)
    norm = re.sub(
        r"\s+\band\b\s+(?=(?:buy|book|make|look|grab|open|research|analy|schedule|email|notify|find|get|order|reserve|check|review))",
        " · ",
        norm,
        flags=re.I,
    )
    # Split on middot / semicolon / newline
    chunks = re.split(r"\s*[·;|\n]+\s*", norm)
    chunks = [c.strip(" ,.") for c in chunks if c and len(c.strip(" ,.")) > 2]
    if not chunks:
        chunks = [raw]
    # If still one blob with multiple intent verbs, force-split by verb
    if len(chunks) == 1:
        verb_split = re.split(
            r"(?=\b(?:buy|purchase|order|book|reserve|make a|look at|analyze|analys|research|find|schedule|email|notify|open|grab|screenshot)\b)",
            chunks[0],
            flags=re.I,
        )
        verb_split = [c.strip(" ,.") for c in verb_split if c and len(c.strip(" ,.")) > 3]
        if len(verb_split) >= 2:
            chunks = verb_split

    items: List[Dict[str, Any]] = []
    for ch in chunks:
        kind, title = _classify(ch)
        if not title:
            continue
        items.append(
            {
                "id": f"wi-{uuid.uuid4().hex[:10]}",
                "kind": kind,
                "title": title[:200],
                "raw": ch[:500],
                "status": "queued",
                "notes": "",
                "result_summary": "",
                "tools": [],
                "evidence": [],
                "gate_message": "",
                "created_at": time.time(),
                "updated_at": time.time(),
            }
        )
    return items


def _classify(text: str) -> Tuple[str, str]:
    t = (text or "").strip()
    low = t.lower()
    title = t[:200]

    def strip_lead(s: str) -> str:
        return re.sub(
            r"^(hey|hi|can you|could you|please|pls|i want you to|i need you to|help me|i want to|i wanna|i'd like to|i would like to)\s+",
            "",
            s,
            flags=re.I,
        ).strip()

    title = strip_lead(title)

    # Everyday life first (food · flights · shop · web)
    try:
        from pocket.life_ops import classify_life

        life = classify_life(t)
        if life:
            return life[0], life[1] or title
    except Exception:
        pass

    if re.search(r"\b(buy|purchase|order|checkout|add to cart|shop for)\b", low):
        return "buy", title
    # Dining out / reservation (not delivery — delivery handled by food_order)
    if re.search(
        r"\b(reserv|book a table|restaurant|steakhouse|dinner|lunch|brunch|eat at|go eat|"
        r"table for|make a reservation|get a table|dine at|del frisco|opentable|resy)\b",
        low,
    ) or (
        re.search(r"\b(eat|dinner|lunch|brunch)\b", low)
        and re.search(r"\b(\d{1,2}:\d{2}|\d{1,2}\s*(am|pm)|tonight|tomorrow|friday|saturday|sunday)\b", low)
    ):
        return "reservation", title
    if re.search(r"\b(analy[sz]e|analysis|business review|look at this|review this|metrics|kpi)\b", low):
        return "analysis", title
    if re.search(r"\b(research|find out|look up|search for|what is|who is|find me|options for)\b", low):
        return "research", title
    if re.search(r"\b(email|notify|message|tell|send (a )?note)\b", low):
        return "notify", title
    if re.search(r"\b(schedule|calendar|meeting|remind me)\b", low):
        return "schedule", title
    if re.search(r"\b(screenshot|capture|sense|what.?s on (my )?screen|grab (this|the) screen)\b", low):
        return "capture", title
    if re.search(r"\b(open |go to |navigate|browse )\b", low) and not re.search(
        r"\b(eat|dinner|restaurant|steakhouse)\b", low
    ):
        return "open", title
    return "errand", title


def _run_tool(skill: str, *, prompt: str = "", params: Optional[Dict] = None) -> Dict[str, Any]:
    params = params or {}
    try:
        from pocket.skill_runner import run_skill

        md, err, eng = run_skill(skill, prompt=prompt, params=params)
        return {
            "ok": not bool(err),
            "skill": skill,
            "engine": eng,
            "error": (err or "")[:300],
            "markdown": (md or "")[:4000],
        }
    except Exception as e1:
        try:
            from pocket.orchestrator_exec import dispatch_skill

            r = dispatch_skill(skill, prompt=prompt, params=params)
            if not isinstance(r, dict):
                r = {"ok": True, "result": r}
            return {"ok": bool(r.get("ok", True)), "skill": skill, "result": r, "markdown": str(r)[:2000]}
        except Exception as e2:
            return {"ok": False, "skill": skill, "error": f"{e1}; {e2}"[:300]}


def _progress(job_id: str, text: str) -> None:
    if not job_id:
        return
    try:
        from pocket.stream_util import update_progress

        update_progress(job_id, text, engine="work")
    except Exception:
        pass
    try:
        emit("work", text[:200], agent="WORK", role="host")
    except Exception:
        pass


def parse_dining_details(text: str) -> Dict[str, Any]:
    """Extract place, time, party size, date preference from natural language."""
    raw = (text or "").strip()
    low = raw.lower()
    out: Dict[str, Any] = {
        "place": "",
        "when": "",
        "time_24": "",
        "party": 2,
        "date_pref": "tonight",
        "date_iso": "",
    }

    # Party size
    m = re.search(
        r"\b(?:table for|party of|for)\s+(\d{1,2})\b|\b(\d{1,2})\s*(?:people|guests|of us)\b",
        low,
    )
    if m:
        try:
            out["party"] = max(1, min(20, int(m.group(1) or m.group(2) or 2)))
        except Exception:
            out["party"] = 2
    elif re.search(r"\b(just me|solo|for one)\b", low):
        out["party"] = 1
    elif re.search(r"\b(for two|date night|couple)\b", low):
        out["party"] = 2

    # Time
    tm = re.search(r"\b(\d{1,2}):(\d{2})\s*(am|pm)?\b", low)
    if tm:
        hh, mm = int(tm.group(1)), int(tm.group(2))
        ap = (tm.group(3) or "").lower()
        if ap == "pm" and hh < 12:
            hh += 12
        if ap == "am" and hh == 12:
            hh = 0
        # bare 8:30 dinner-ish → assume PM if 1–11
        if not ap and 1 <= hh <= 11:
            hh += 12
        out["when"] = tm.group(0).strip()
        out["time_24"] = f"{hh:02d}:{mm:02d}"
    else:
        tm2 = re.search(r"\b(\d{1,2})\s*(am|pm)\b", low)
        if tm2:
            hh = int(tm2.group(1))
            ap = tm2.group(2).lower()
            if ap == "pm" and hh < 12:
                hh += 12
            if ap == "am" and hh == 12:
                hh = 0
            out["when"] = tm2.group(0).strip()
            out["time_24"] = f"{hh:02d}:00"

    # Date preference
    if re.search(r"\btomorrow\b", low):
        out["date_pref"] = "tomorrow"
    elif re.search(r"\btonight\b", low):
        out["date_pref"] = "tonight"
    else:
        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            if re.search(rf"\b{day}\b", low):
                out["date_pref"] = day
                break

    # ISO date from preference
    try:
        from datetime import datetime, timedelta

        now = datetime.now()
        d = now.date()
        pref = out["date_pref"]
        if pref == "tomorrow":
            d = d + timedelta(days=1)
        elif pref in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            want = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ].index(pref)
            # Python weekday Mon=0
            delta = (want - d.weekday()) % 7
            if delta == 0 and (out.get("time_24") or "") < now.strftime("%H:%M"):
                delta = 7
            d = d + timedelta(days=delta or 0)
        out["date_iso"] = d.isoformat()
    except Exception:
        out["date_iso"] = ""

    # Place
    place = raw
    place = re.sub(
        r"\b(make|book|the|reservation|for me|please|restaurant|go eat at|go eat|eat at|dine at|"
        r"go to|table for|tonight|tomorrow|i want to|i wanna|get (me )?a table|"
        r"party of \d+|for \d+ (people|guests)?|complete (the )?reservation|finish booking)\b",
        " ",
        place,
        flags=re.I,
    )
    place = re.sub(r"\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b", " ", place, flags=re.I)
    place = re.sub(r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b", " ", place, flags=re.I)
    place = re.sub(r"\b\d{1,2}\s*(?:am|pm)\b", " ", place, flags=re.I)
    place = re.sub(r"^\s*at\s+", "", place, flags=re.I)
    place = re.sub(r"\s+", " ", place).strip(" ,.-")
    out["place"] = place or raw[:80]
    return out


def _opentable_datetime(date_iso: str, time_24: str) -> str:
    """OpenTable dateTime=YYYY-MM-DDTHH:MM"""
    t = time_24 or "19:00"
    d = date_iso or time.strftime("%Y-%m-%d")
    return f"{d}T{t}"


def drive_reservation_ui(
    *,
    open_url: str,
    place: str,
    when: str,
    time_24: str,
    party: int,
    date_iso: str,
    stream_fn=None,
) -> Dict[str, Any]:
    """Open booking page + attempt real UI steps toward a reservation.

    Never submits final confirm / payment — stops at needs_you with evidence.
    """
    steps: List[Dict[str, Any]] = []
    notes: List[str] = []

    def log(msg: str) -> None:
        notes.append(msg)
        if stream_fn:
            try:
                stream_fn(msg)
            except Exception:
                pass

    # 1) Arm screen Control so clicks are allowed
    try:
        from pocket.screen_share import set_share

        set_share(mode="control", vcomp=True, label="reservation-book")
        steps.append({"ok": True, "step": "arm_control"})
        log("Screen Control armed for booking")
    except Exception as e:
        steps.append({"ok": False, "step": "arm_control", "error": str(e)[:120]})

    # 2) Prefer OpenTable restaurant URL with covers + dateTime when possible
    url = open_url
    try:
        import urllib.parse

        low = (url or "").lower()
        dt = _opentable_datetime(date_iso, time_24)
        if "opentable.com/r/" in low:
            # append query if missing
            if "covers=" not in low and "datetime=" not in low.replace("datetime", "dateTime").lower():
                sep = "&" if "?" in url else "?"
                url = (
                    f"{url}{sep}"
                    + urllib.parse.urlencode({"covers": party, "dateTime": dt})
                )
        elif "opentable.com" in low and "/s?" in low:
            # search already — keep
            pass
        elif "opentable.com" not in low:
            # Build OT search with time params when we only have venue site
            url = "https://www.opentable.com/s?" + urllib.parse.urlencode(
                {
                    "term": place[:80],
                    "covers": party,
                    "dateTime": dt,
                }
            )
    except Exception:
        pass

    # 3) Open in signed-in Edge
    try:
        from pocket.virtual_computer import act

        log(f"Opening booking page · party {party}" + (f" · {when or time_24}" if (when or time_24) else ""))
        r = act("open_url", url=url)
        steps.append({"ok": bool(r.get("ok")), "step": "open_url", "url": url})
        time.sleep(2.2)
    except Exception as e:
        steps.append({"ok": False, "step": "open_url", "error": str(e)[:160]})
        return {"ok": False, "steps": steps, "notes": notes, "url": url, "error": str(e)[:160]}

    # 4) Sense page
    sense_brief = ""
    symbols: List[str] = []
    try:
        from pocket.virtual_computer import act

        log("Reading page (fusion sense)…")
        s = act("sense", max_ui=500)
        sense_brief = str(s.get("brief") or s.get("after_sense") or "")[:400]
        # collect clickable names if present
        after = s.get("after_counts") or s.get("counts") or {}
        steps.append({"ok": bool(s.get("ok", True)), "step": "sense", "brief": sense_brief[:160]})
        try:
            from pocket.perception import find_symbol, sense as perc_sense

            page = perc_sense(max_ui=500, force=True, include_image=False)
            for sym in (page.get("symbols") or page.get("ui") or [])[:80]:
                if isinstance(sym, dict):
                    t = str(sym.get("text") or sym.get("name") or "").strip()
                    if t and len(t) < 60:
                        symbols.append(t)
                elif isinstance(sym, str):
                    symbols.append(sym[:60])
        except Exception:
            pass
        if sense_brief:
            log(f"Page: {sense_brief[:100]}")
    except Exception as e:
        steps.append({"ok": False, "step": "sense", "error": str(e)[:120]})

    # 5) Try booking UI clicks in priority order
    click_targets = [
        "Find a table",
        "Find a Table",
        "Reserve",
        "Book a table",
        "Book Now",
        "Make a reservation",
        "Check availability",
        "Select a time",
        "Reservation",
    ]
    # Time-slot labels often show "8:30 PM"
    if time_24:
        try:
            hh, mm = map(int, time_24.split(":"))
            ap = "PM" if hh >= 12 else "AM"
            h12 = hh % 12 or 12
            click_targets.extend(
                [
                    f"{h12}:{mm:02d} {ap}",
                    f"{h12}:{mm:02d}{ap}",
                    f"{h12}:{mm:02d}",
                    time_24,
                ]
            )
        except Exception:
            pass

    clicked: List[str] = []
    try:
        from pocket.virtual_computer import act
        from pocket.screen_share import act_for_agent

        for name in click_targets:
            # skip if nothing remotely similar on page (when we have symbols)
            if symbols:
                low_syms = " ".join(symbols).lower()
                if not any(w.lower() in low_syms for w in name.split() if len(w) > 2):
                    # still try high-value buttons
                    if name not in (
                        "Find a table",
                        "Find a Table",
                        "Reserve",
                        "Book a table",
                        "Book Now",
                    ):
                        continue
            log(f"Trying UI: «{name}»")
            try:
                r = act_for_agent("click", agent="work", name=name, min_score=0.55)
            except Exception:
                r = act("click", name=name, min_score=0.55)
            steps.append(
                {
                    "ok": bool(r.get("ok")),
                    "step": "click",
                    "name": name,
                    "score": r.get("score"),
                    "message": (r.get("message") or r.get("error") or "")[:120],
                }
            )
            if r.get("ok"):
                clicked.append(name)
                log(f"Clicked «{name}»")
                time.sleep(1.1)
                # After find-table, try time slot
                if name.lower().startswith("find") or name.lower().startswith("book") or name.lower() == "reserve":
                    continue
                if ":" in name:  # time slot
                    break
            # Don't spam every target
            if len(clicked) >= 3:
                break
    except Exception as e:
        steps.append({"ok": False, "step": "click_loop", "error": str(e)[:160]})
        log(f"UI drive limited: {e}")

    # 6) Party size: try click covers / type
    if party and party != 2:
        try:
            from pocket.screen_share import act_for_agent

            for label in (f"{party} people", f"Party of {party}", str(party), "Guests", "Party size"):
                r = act_for_agent("click", agent="work", name=label, min_score=0.5)
                steps.append({"ok": bool(r.get("ok")), "step": "party_click", "name": label})
                if r.get("ok"):
                    log(f"Set party · «{label}»")
                    break
        except Exception as e:
            steps.append({"ok": False, "step": "party", "error": str(e)[:100]})

    # 7) Re-sense for available slots evidence
    slot_hints: List[str] = []
    try:
        from pocket.perception import sense as perc_sense

        time.sleep(0.8)
        page = perc_sense(max_ui=500, force=True, include_image=False)
        for sym in (page.get("symbols") or page.get("ui") or [])[:120]:
            t = str((sym.get("text") if isinstance(sym, dict) else sym) or "")
            if re.search(r"\d{1,2}:\d{2}\s*(AM|PM|am|pm)?", t):
                slot_hints.append(t.strip()[:40])
        slot_hints = list(dict.fromkeys(slot_hints))[:12]
        if slot_hints:
            log("Time slots visible: " + ", ".join(slot_hints[:6]))
            steps.append({"ok": True, "step": "slots", "slots": slot_hints})
    except Exception:
        pass

    ok = any(s.get("ok") for s in steps if s.get("step") in ("open_url", "click"))
    return {
        "ok": ok,
        "url": url,
        "steps": steps,
        "notes": notes,
        "clicked": clicked,
        "slots": slot_hints,
        "sense_brief": sense_brief,
        "party": party,
        "when": when,
        "time_24": time_24,
        "date_iso": date_iso,
        "confirm_blocked": True,  # never auto-confirm
        "message": (
            f"Booking drive · party {party}"
            + (f" · {when or time_24}" if (when or time_24) else "")
            + (f" · clicked {', '.join(clicked)}" if clicked else " · page open (confirm on screen)")
        ),
    }


def _choice_lines(links: List[Dict[str, str]], *, heading: str = "Choices") -> str:
    if not links:
        return ""
    lines = [f"**{heading}**"]
    for i, l in enumerate(links[:8], 1):
        title = (l.get("title") or "option")[:100]
        url = (l.get("url") or "")[:200]
        snip = (l.get("snippet") or "")[:120]
        bit = f"{i}. **{title}**"
        if snip:
            bit += f" — {snip}"
        if url:
            bit += f"\n   {url}"
        lines.append(bit)
    return "\n".join(lines)


def execute_item(item: Dict[str, Any], *, job_id: str = "") -> Dict[str, Any]:
    """Run host tools for one board row. High-risk kinds stop at needs_you."""
    kind = item.get("kind") or "errand"
    title = item.get("title") or item.get("raw") or ""
    raw = item.get("raw") or title
    item["status"] = "running"
    item["updated_at"] = time.time()
    item["started_at"] = item.get("started_at") or time.time()
    item["stream"] = item.get("stream") or []
    tools: List[Dict[str, Any]] = []
    evidence: List[str] = []
    links: List[Dict[str, str]] = []
    choices: List[Dict[str, str]] = []
    next_steps: List[str] = []
    meta = KIND_META.get(kind) or {}
    t0 = time.time()

    def _stream(msg: str) -> None:
        line = str(msg or "").strip()
        if not line:
            return
        item.setdefault("stream", []).append({"at": time.time(), "text": line[:400]})
        item["stream"] = (item.get("stream") or [])[-24:]
        item["result_summary"] = line[:120]
        item["updated_at"] = time.time()
        # Persist mid-flight so UI can poll live findings
        try:
            board = load_board()
            for it in board.get("items") or []:
                if it.get("id") == item.get("id"):
                    it.update(item)
                    break
            else:
                board.setdefault("items", []).append(item)
            save_board(board)
        except Exception:
            pass
        _progress(job_id, f"🔎 {line}")

    def _search(q: str, n: int = 6, *, label: str = "Findings") -> Dict[str, Any]:
        try:
            from pocket.web_research import search_web

            _stream(f"Searching: {q[:90]}")
            sr = search_web(q[:200], max_results=n)
            n_hits = int(sr.get("count") or len(sr.get("results") or []) or 0)
            tools.append(
                {
                    "ok": bool(sr.get("ok") and n_hits),
                    "skill": "web_search",
                    "query": q[:120],
                    "count": n_hits,
                    "backends": sr.get("backends") or [],
                }
            )
            hl, lk = _hits_lines(sr, n=n)
            if hl:
                evidence.append(f"**{label}**\n" + "\n".join(hl))
                for L in lk:
                    if L not in links:
                        links.append(L)
                    if L not in choices:
                        choices.append(L)
                _stream(f"Found {n_hits} result(s) for «{q[:60]}»")
            else:
                _stream(f"No hits yet for «{q[:60]}» — trying another source…")
            return sr
        except Exception as e:
            tools.append({"ok": False, "skill": "web_search", "error": str(e)[:160]})
            _stream(f"Search error: {e}")
            return {"ok": False, "error": str(e)}

    # Everyday life: food · flights · shopping · web
    life_done = False
    if kind in ("food_order", "flight", "shop", "browse", "buy"):
        try:
            from pocket.life_ops import execute_life_item

            if kind == "buy":
                item["kind"] = "shop"
            execute_life_item(
                item,
                search_fn=lambda q, n=6, label="Findings": _search(q, n, label=label),
                stream_fn=_stream,
                job_id=job_id,
            )
            # Prefer life_ops results as source of truth
            tools = list(item.get("tools") or tools)
            evidence = list(item.get("evidence") or evidence)
            links = list(item.get("links") or links)
            choices = list(item.get("choices") or choices)
            next_steps = list(item.get("next_steps") or [])
            life_done = True
        except Exception as e:
            _stream(f"Life ops error: {e}")
            item["status"] = "blocked"
            item["result_summary"] = str(e)[:120]

    # Capture is fast path
    elif kind == "capture":
        tr = _run_tool("screen_sense", prompt=raw)
        tools.append(tr)
        if tr.get("markdown"):
            evidence.append(str(tr["markdown"])[:900])
        fr = _run_tool("screenshot", prompt=raw)
        tools.append(fr)
        item["status"] = "done" if (tr.get("ok") or fr.get("ok")) else "blocked"
        item["result_summary"] = "Screen captured + sensed" if item["status"] == "done" else "capture failed"
        next_steps = ["Review Screen column", "Ask: analyze what you see"]

    elif kind in ("research", "analysis"):
        q = re.sub(r"\b(look at this|review this|analyze|analysis|for me|today)\b", " ", title, flags=re.I)
        q = re.sub(r"\s+", " ", q).strip() or title
        sr = _search(q if kind == "research" else f"{q} analysis insights", 6)
        # Optional light screen context for analysis
        if kind == "analysis":
            tr = _run_tool("screen_sense", prompt=raw)
            tools.append({"ok": tr.get("ok"), "skill": "screen_sense"})
            if tr.get("markdown"):
                evidence.append("**On screen**\n" + str(tr["markdown"])[:500])
        n = len(sr.get("results") or sr.get("items") or []) if isinstance(sr, dict) else 0
        item["status"] = "done" if (sr.get("ok") or n or evidence) else "blocked"
        item["result_summary"] = f"{n} sources · notes ready" if n else (sr.get("error") or "analysis complete")
        next_steps = [
            "Ask a follow-up on any finding",
            "Say: package — bag this analysis",
        ]

    elif kind == "buy_legacy_unused":
        # kept for reference — buy routes through life_ops shop
        pass

    elif kind == "reservation":
        import urllib.parse

        dining = parse_dining_details(raw or title)
        place = dining.get("place") or title
        when = dining.get("when") or ""
        time_24 = dining.get("time_24") or ""
        party = int(dining.get("party") or 2)
        date_iso = dining.get("date_iso") or ""
        item["dining"] = dining

        _stream(
            f"Dining: {place}"
            + (f" · {when or time_24}" if (when or time_24) else "")
            + f" · party {party}"
            + (f" · {date_iso}" if date_iso else "")
        )

        # Multi-query search so we stream real venue + booking options
        queries = [
            f"{place} restaurant reservation" + (f" {when}" if when else ""),
            f"{place} OpenTable book table",
            f"{place} official site reserve",
        ]
        for qi, qq in enumerate(queries):
            _search(qq, 6 if qi == 0 else 4, label=f"Search {qi + 1}")
            if len(choices) >= 5:
                break

        dt = _opentable_datetime(date_iso, time_24)
        ot = "https://www.opentable.com/s?" + urllib.parse.urlencode(
            {"term": place[:80], "covers": party, "dateTime": dt}
        )
        maps = "https://www.google.com/maps/search/" + urllib.parse.quote(place[:80])
        for title_l, url_l, snip in (
            (f"OpenTable · {party} · {when or time_24 or 'tonight'}", ot, "covers + time"),
            ("Google Maps", maps, "location"),
        ):
            links.append({"title": title_l, "url": url_l, "snippet": snip})
            if not any((c.get("url") or "") == url_l for c in choices):
                choices.append({"title": title_l, "url": url_l, "snippet": snip})

        # Prefer restaurant-specific OpenTable, then Resy, then official, then OT search
        open_url = ""
        for prefer in ("opentable.com/r/", "resy.com", "opentable.com", "delfriscos.com", "yelp.com/biz"):
            for c in choices:
                u = (c.get("url") or "").lower()
                if prefer in u:
                    open_url = c.get("url") or ""
                    break
            if open_url:
                break
        if not open_url:
            open_url = ot

        # Drive booking UI: open + sense + click Find a table / time slots
        _stream("Driving reservation on host browser…")
        drive = drive_reservation_ui(
            open_url=open_url,
            place=place,
            when=when,
            time_24=time_24,
            party=party,
            date_iso=date_iso,
            stream_fn=_stream,
        )
        tools.append(
            {
                "ok": bool(drive.get("ok")),
                "skill": "reservation_drive",
                "url": drive.get("url"),
                "clicked": drive.get("clicked") or [],
                "slots": (drive.get("slots") or [])[:8],
            }
        )
        if drive.get("url"):
            links.insert(0, {"title": "Booking page (opened)", "url": drive["url"], "snippet": "live"})
        if drive.get("notes"):
            evidence.append("**Booking drive**\n" + "\n".join(f"- {n}" for n in drive["notes"][-12:]))
        if drive.get("slots"):
            evidence.append(
                "**Time slots on screen**\n" + "\n".join(f"- {s}" for s in drive["slots"][:10])
            )
            for s in drive["slots"][:6]:
                choices.append({"title": f"Slot {s}", "url": drive.get("url") or open_url, "snippet": "visible on page"})

        choice_md = _choice_lines(choices, heading="Restaurant / booking choices")
        if choice_md:
            evidence.insert(0, choice_md)

        when_bit = f" at **{when or time_24}**" if (when or time_24) else ""
        clicked = drive.get("clicked") or []
        item["status"] = "needs_you"
        item["booking"] = {
            "url": drive.get("url") or open_url,
            "party": party,
            "when": when,
            "time_24": time_24,
            "date_iso": date_iso,
            "clicked": clicked,
            "slots": drive.get("slots") or [],
            "confirm_blocked": True,
        }
        item["gate_message"] = (
            f"Reservation in progress for **{place}**{when_bit}, party **{party}**. "
            + (
                f"I clicked: {', '.join(clicked)}. "
                if clicked
                else "Booking page is open. "
            )
            + "I will **not** press final Confirm / pay — finish the last step on screen, then mark Done. "
            + "Say **party of N** or **book 8:30** to adjust and re-drive."
        )
        n_ch = len(choices)
        item["result_summary"] = (
            f"Booking · {place[:28]} · p{party}"
            + (f" · {when or time_24}" if (when or time_24) else "")
            + (f" · {len(clicked)} UI steps" if clicked else " · page open")
        )
        item["choices"] = choices[:12]
        next_steps = [
            f"Check Edge — {when or time_24 or 'time'} for {party}",
            "Pick slot if not selected",
            "Confirm reservation yourself (I stop before confirm)",
            "Mark this row Done",
        ]
        _stream(item["result_summary"])

    elif kind == "notify":
        draft = re.sub(r"^(email|notify|message|tell|send)\s+", "", title, flags=re.I).strip() or title
        item["status"] = "needs_you"
        item["gate_message"] = "Draft ready — confirm before send"
        item["result_summary"] = "Draft only (not sent)"
        evidence.append(f"**Draft**\n{draft}")
        item["draft"] = draft
        next_steps = ["Edit draft", "Send yourself", "Mark Done"]

    elif kind == "schedule":
        item["status"] = "needs_you"
        item["gate_message"] = f"Calendar draft: «{title[:100]}» — confirm to place"
        item["result_summary"] = "Schedule draft · needs you"
        evidence.append(f"**Event draft**\n{title}")
        next_steps = ["Confirm time", "Add to calendar", "Mark Done"]

    elif kind == "open":
        m = re.search(r"https?://\S+", raw)
        url = m.group(0) if m else ""
        if not url:
            import urllib.parse

            url = "https://www.google.com/search?q=" + urllib.parse.quote(title[:100])
        try:
            from pocket.virtual_computer import act

            r = act("open_url", url=url)
            tools.append({"ok": r.get("ok"), "skill": "open_url", "url": url})
            item["status"] = "done" if r.get("ok") else "blocked"
            item["result_summary"] = f"Opened {url[:50]}"
            links.append({"title": "Opened", "url": url})
            next_steps = ["Continue in browser"]
        except Exception as e:
            item["status"] = "blocked"
            item["result_summary"] = str(e)[:120]

    else:
        # Generic errand — still search and surface findings (never empty "logged")
        sr = _search(title, 6, label="Findings")
        n = int(sr.get("count") or 0)
        if n < 2:
            _search(f"{title} options", 5, label="More options")
        if choices:
            evidence.insert(0, _choice_lines(choices, heading="What I found"))
        tr = _run_tool("screen_sense", prompt=raw)
        tools.append({"ok": tr.get("ok"), "skill": "screen_sense"})
        item["status"] = "done" if choices or evidence else "blocked"
        item["result_summary"] = (
            f"{len(choices)} finding(s)" if choices else (sr.get("error") or "No findings — rephrase")
        )
        item["choices"] = choices[:10]
        next_steps = ["Ask a follow-up", "Or rephrase with buy / reserve / research"]

    item["tools"] = [
        {k: v for k, v in t.items() if k != "result"} for t in tools[-12:]
    ]
    item["evidence"] = evidence[-10:]
    item["links"] = links[:10]
    item["choices"] = (item.get("choices") or choices)[:10]
    item["next_steps"] = next_steps[:6]
    item["ms"] = int((time.time() - t0) * 1000)
    item["updated_at"] = time.time()
    if meta.get("human_gate") and item.get("status") == "running":
        item["status"] = "needs_you"
    emit(
        "work",
        f"board item {item.get('kind')} → {item.get('status')}: {title[:80]}",
        agent="WORK",
        role="host",
    )
    _progress(
        job_id,
        f"✓ {item.get('kind')} → {item.get('status')}: {item.get('result_summary') or title[:60]}",
    )
    return item


def set_item_status(
    item_id: str,
    *,
    status: str = "",
    note: str = "",
) -> Dict[str, Any]:
    """Mark done / dismiss / re-queue from the UI."""
    st = (status or "").strip().lower()
    if st not in ("done", "dismissed", "queued", "needs_you", "blocked"):
        return {"ok": False, "error": "status must be done|dismissed|queued|needs_you|blocked"}
    board = load_board()
    found = None
    for it in board.get("items") or []:
        if it.get("id") == item_id:
            it["status"] = st
            if note:
                it["notes"] = (note or "")[:500]
            if st == "done":
                it["result_summary"] = it.get("result_summary") or "Marked done by you"
                it["gate_message"] = ""
            if st == "dismissed":
                it["result_summary"] = "Dismissed"
            it["updated_at"] = time.time()
            found = it
            break
    if not found:
        return {"ok": False, "error": "item not found"}
    board["last_activity"] = f"{st}: {(found.get('title') or '')[:60]}"
    save_board(board)
    return {"ok": True, "item": found, "table": board_table(board), "board": board}


def ingest_and_run(
    text: str,
    *,
    session_id: str = "",
    goal: str = "",
    execute: bool = True,
    job_id: str = "",
) -> Dict[str, Any]:
    """Main entry: natural language → board rows → tools → table."""
    board = load_board()
    if session_id:
        board["session_id"] = session_id
    if goal:
        board["goal"] = goal[:400]
    elif text and (
        not board.get("goal")
        or str(board.get("goal") or "").startswith("Working board")
        or str(board.get("goal") or "").startswith("Buy noise")
    ):
        board["goal"] = text[:200]
    _progress(job_id, f"Working board · parsing: {(text or '')[:120]}")

    # Board commands
    low = (text or "").strip().lower()
    if low in ("board", "table", "show board", "status", "working board"):
        return {
            "ok": True,
            "board": board,
            "table": board_table(board),
            "reply": board_table(board),
            "ran": 0,
        }
    if low in ("clear board", "reset board"):
        board = _empty_board()
        board["session_id"] = session_id or ""
        save_board(board)
        return {"ok": True, "board": board, "table": board_table(board), "reply": "Board cleared.\n\n" + board_table(board)}

    # Continue / refine an open reservation (party size, time, "book it", "get the reservation")
    cont = re.search(
        r"\b(book it|finish (the )?reservation|complete (the )?reservation|get (the )?reservation|"
        r"make the reservation|confirm (the )?table|drive (the )?booking|"
        r"party of \d+|table for \d+|covers?\s*\d+|"
        r"change (time|party)|try (again|opentable)|select (the )?time)\b",
        low,
    )
    if cont:
        target = None
        for it in reversed(board.get("items") or []):
            if it.get("kind") == "reservation" and it.get("status") in (
                "needs_you",
                "running",
                "queued",
                "blocked",
            ):
                target = it
                break
        if target:
            dining = parse_dining_details(
                (target.get("raw") or target.get("title") or "") + " " + text
            )
            # merge prior booking details
            prev = target.get("dining") or target.get("booking") or {}
            if not dining.get("place") and prev.get("place"):
                dining["place"] = prev.get("place")
            if not dining.get("time_24") and prev.get("time_24"):
                dining["time_24"] = prev.get("time_24")
                dining["when"] = prev.get("when") or dining.get("when")
            if prev.get("party") and "party of" not in low and "table for" not in low:
                # keep previous party unless user overrides
                if dining.get("party") == 2 and prev.get("party") not in (None, 2):
                    dining["party"] = prev.get("party")
            place = dining.get("place") or (target.get("title") or "restaurant")
            open_url = (target.get("booking") or {}).get("url") or ""
            if not open_url:
                for L in target.get("links") or target.get("choices") or []:
                    u = (L.get("url") or "") if isinstance(L, dict) else ""
                    if "opentable" in u.lower() or "resy" in u.lower():
                        open_url = u
                        break
            if not open_url:
                import urllib.parse

                open_url = "https://www.opentable.com/s?" + urllib.parse.urlencode(
                    {
                        "term": str(place)[:80],
                        "covers": dining.get("party") or 2,
                        "dateTime": _opentable_datetime(
                            dining.get("date_iso") or "", dining.get("time_24") or ""
                        ),
                    }
                )
            _progress(job_id, f"Continuing reservation · {place}…")
            stream_notes: List[str] = []

            def _s(msg: str) -> None:
                stream_notes.append(msg)
                _progress(job_id, f"🔎 {msg}")

            drive = drive_reservation_ui(
                open_url=open_url,
                place=str(place),
                when=str(dining.get("when") or ""),
                time_24=str(dining.get("time_24") or ""),
                party=int(dining.get("party") or 2),
                date_iso=str(dining.get("date_iso") or ""),
                stream_fn=_s,
            )
            target["status"] = "needs_you"
            target["dining"] = dining
            target["booking"] = {
                "url": drive.get("url") or open_url,
                "party": dining.get("party"),
                "when": dining.get("when"),
                "time_24": dining.get("time_24"),
                "date_iso": dining.get("date_iso"),
                "clicked": drive.get("clicked") or [],
                "slots": drive.get("slots") or [],
                "confirm_blocked": True,
            }
            target["result_summary"] = (
                f"Re-drove · p{dining.get('party')}"
                + (f" · {dining.get('when') or dining.get('time_24')}" if dining.get("time_24") or dining.get("when") else "")
                + (f" · {len(drive.get('clicked') or [])} clicks" if drive.get("clicked") else "")
            )
            target["gate_message"] = (
                f"Updated booking drive for **{place}**, party **{dining.get('party')}**. "
                "Finish Confirm on screen — I never auto-confirm. Mark Done when booked."
            )
            ev = list(target.get("evidence") or [])
            if stream_notes:
                ev.append("**Continue drive**\n" + "\n".join(f"- {n}" for n in stream_notes[-10:]))
            if drive.get("slots"):
                ev.append("**Slots**\n" + "\n".join(f"- {s}" for s in drive["slots"][:8]))
            target["evidence"] = ev[-12:]
            target["stream"] = (target.get("stream") or []) + [
                {"at": time.time(), "text": n} for n in stream_notes
            ]
            target["updated_at"] = time.time()
            # write back
            for i, it in enumerate(board.get("items") or []):
                if it.get("id") == target.get("id"):
                    board["items"][i] = target
                    break
            board["last_activity"] = f"continue reservation · {place[:40]}"
            save_board(board)
            reply = (
                f"### 🍽 Continued reservation — {place}\n"
                f"_{target.get('status')}_ · {target.get('result_summary')}\n\n"
                f"{target.get('gate_message')}\n\n"
                + ("\n".join(f"- {n}" for n in stream_notes[-8:]) + "\n\n" if stream_notes else "")
                + board_table(board)
            )
            _progress(job_id, reply[:3500])
            return {
                "ok": True,
                "board": board,
                "table": board_table(board),
                "items_added": [target],
                "ran": 1,
                "reply": reply,
                "continued": True,
            }

    new_items = parse_intents(text)
    if not new_items:
        return {
            "ok": True,
            "board": board,
            "table": board_table(board),
            "reply": "I didn't catch a work item. Try: buy X · analyze Y · reserve Z\n\n" + board_table(board),
            "ran": 0,
        }

    # Deduplicate against very recent identical titles
    existing_titles = {
        (i.get("title") or "").strip().lower()
        for i in (board.get("items") or [])[-15:]
        if i.get("status") not in ("dismissed",)
    }
    filtered = []
    for it in new_items:
        key = (it.get("title") or "").strip().lower()
        if key and key in existing_titles:
            it["status"] = "done"
            it["result_summary"] = "Already on board (skipped duplicate)"
            it["notes"] = "deduped"
        filtered.append(it)
        if key:
            existing_titles.add(key)
    new_items = filtered

    for it in new_items:
        board.setdefault("items", []).append(it)
    save_board(board)  # visible immediately while tools run
    _progress(
        job_id,
        "Added "
        + ", ".join(
            f"{(KIND_META.get(i.get('kind') or '') or {}).get('icon', '·')} {i.get('kind')}: {(i.get('title') or '')[:50]}"
            for i in new_items
        )
        + " — running tools…",
    )

    ran = 0
    if execute:
        # Sequential for live stream readability (parallel still ok for multi-pack)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        todo = [it for it in new_items if it.get("status") == "queued"]
        if todo:
            workers = 1 if len(todo) == 1 else min(3, len(todo))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futs = {pool.submit(execute_item, it, job_id=job_id): it for it in todo}
                for fut in as_completed(futs):
                    try:
                        fut.result()
                        ran += 1
                    except Exception as e:
                        it = futs[fut]
                        it["status"] = "blocked"
                        it["result_summary"] = str(e)[:120]
                        ran += 1
                    # merge finished item back into board snapshot
                    try:
                        board = load_board()
                    except Exception:
                        pass

    # keep last 80 items
    board = load_board()
    board["items"] = (board.get("items") or [])[-80:]
    board["status"] = "live"
    board["last_activity"] = f"+{len(new_items)} · {text[:80]}"
    save_board(board)

    # Human reply: streaming narrative + choices first (not just empty table)
    done_n = sum(1 for i in new_items if i.get("status") == "done")
    need_n = sum(1 for i in new_items if i.get("status") == "needs_you")
    blocked_n = sum(1 for i in new_items if i.get("status") == "blocked")
    bits = [f"Added **{len(new_items)}** work item(s) · tools ran on **{ran}**."]
    if done_n:
        bits.append(f"✓ {done_n} finished")
    if need_n:
        bits.append(f"⚠ {need_n} need you (pay / book / send)")
    if blocked_n:
        bits.append(f"✗ {blocked_n} blocked")
    bits.append("")
    for it in new_items:
        icon = (KIND_META.get(it.get("kind") or "") or {}).get("icon", "·")
        bits.append(f"### {icon} {it.get('title')}")
        bits.append(f"_{it.get('status')}_ · {it.get('result_summary') or ''}")
        if it.get("gate_message"):
            bits.append(it["gate_message"])
        # Live stream trail
        stream = it.get("stream") or []
        if stream:
            bits.append("")
            bits.append("**Live**")
            for s in stream[-8:]:
                bits.append(f"- {s.get('text') if isinstance(s, dict) else s}")
        if it.get("choices"):
            bits.append("")
            bits.append(_choice_lines(it["choices"], heading="Choices"))
        elif it.get("links"):
            bits.append(
                "**Links:** "
                + " · ".join(
                    f"[{l.get('title') or 'link'}]({l.get('url')})"
                    for l in (it.get("links") or [])[:6]
                )
            )
        if it.get("evidence"):
            # skip duplicate choice block already rendered
            for ev in it["evidence"][:3]:
                if isinstance(ev, str) and ev.startswith("**Restaurant"):
                    continue
                if isinstance(ev, str) and ev.startswith("**Choices"):
                    continue
                bits.append(str(ev)[:1200])
        if it.get("next_steps"):
            bits.append("**Next:** " + " → ".join(it["next_steps"][:4]))
        bits.append("")
    bits.append(board_table(board))

    reply = "\n".join(bits)
    _progress(job_id, reply[:3500])
    return {
        "ok": True,
        "board": board,
        "table": board_table(board),
        "items_added": new_items,
        "ran": ran,
        "reply": reply,
    }


def status() -> Dict[str, Any]:
    b = load_board()
    items = b.get("items") or []
    return {
        "ok": True,
        "schema": "pocket.working_board.v1",
        "board_id": b.get("id"),
        "goal": b.get("goal"),
        "counts": {
            "total": len(items),
            "queued": sum(1 for i in items if i.get("status") == "queued"),
            "running": sum(1 for i in items if i.get("status") in ("running", "active")),
            "needs_you": sum(1 for i in items if i.get("status") == "needs_you"),
            "done": sum(1 for i in items if i.get("status") == "done"),
            "blocked": sum(1 for i in items if i.get("status") == "blocked"),
        },
        "items": items[-40:],
        "table": board_table(b),
        "kinds": {k: v.get("label") for k, v in KIND_META.items()},
        "doctrine": (
            "Working state is a board of real tasks with tools — not coding chat. "
            "Multi-intent speech becomes rows. High-risk actions stop at needs_you."
        ),
    }
