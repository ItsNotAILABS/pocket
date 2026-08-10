"""Everyday skills for Aria (Voice ↔ Voice) — general day-to-day help.

Local, instant, no network required. Covers the tasks people actually need
while talking: time, lists, reminders, travel, food, focus, math, drafts.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# In-memory day lists (also soft-persisted lightly)
_LISTS: Dict[str, List[str]] = {
    "todo": [],
    "grocery": [],
    "shopping": [],
    "ideas": [],
}
_REMINDERS: List[Dict[str, Any]] = []


def list_skills() -> List[Dict[str, str]]:
    return [
        {"id": "time", "blurb": "What time is it / day of week"},
        {"id": "timer", "blurb": "Quick focus or kitchen timers (spoken)"},
        {"id": "todo", "blurb": "Add / list / clear todos"},
        {"id": "grocery", "blurb": "Grocery and shopping lists"},
        {"id": "remind", "blurb": "Remember something for later today"},
        {"id": "math", "blurb": "Quick arithmetic"},
        {"id": "convert", "blurb": "Simple unit tips (spoken)"},
        {"id": "travel", "blurb": "Packing / commute / flight phrasing"},
        {"id": "food", "blurb": "Meal ideas / water / coffee cues"},
        {"id": "focus", "blurb": "Pomodoro-style focus coaching"},
        {"id": "mood", "blurb": "Grounding / calm check-in"},
        {"id": "draft", "blurb": "Dictate a short note or message"},
        {"id": "weather_talk", "blurb": "How to check weather (no fake forecast)"},
        {"id": "calendar_talk", "blurb": "How to plan the day out loud"},
    ]


def try_skill(text: str) -> Optional[Tuple[str, str]]:
    """Return (reply, skill_id) if a skill matches; else None."""
    u = (text or "").strip()
    if not u:
        return None
    low = u.lower()

    # Time / date
    if re.search(r"\b(what time|current time|time is it|what'?s the time)\b", low):
        now = datetime.now()
        return (
            f"It's {now.strftime('%I:%M %p').lstrip('0')} on {now.strftime('%A, %B %d')}.",
            "time",
        )
    if re.search(r"\b(what day|what'?s today|date today)\b", low):
        now = datetime.now()
        return (f"Today is {now.strftime('%A, %B %d, %Y')}.", "time")

    # Math
    m = re.search(
        r"(?:what(?:'s| is)|calculate|compute|how much is)\s+([\d\.\s\+\-\*\/x×÷\(\)]+)\??\s*$",
        low,
    ) or re.search(r"^([\d\.\s]+)([\+\-\*\/x×÷])([\d\.\s]+)\??\s*$", low)
    if m:
        expr = u
        expr = re.sub(r"(?i)what(?:'s| is)|calculate|compute|how much is", "", expr)
        expr = expr.replace("×", "*").replace("x", "*").replace("÷", "/").replace("?", "")
        expr = re.sub(r"[^0-9\.\+\-\*\/\(\)\s]", "", expr)
        try:
            # Safe tiny eval
            if re.fullmatch(r"[\d\.\s\+\-\*\/\(\)]+", expr.strip()):
                val = eval(expr.strip(), {"__builtins__": {}}, {})  # noqa: S307 — constrained
                return (f"That comes out to {val}.", "math")
        except Exception:
            pass

    # Todo
    add_todo = re.search(r"\b(?:add|remember to|put)\s+(.+?)\s+(?:to|on)\s+(?:my\s+)?(?:to-?do|todo|list)\b", low)
    if not add_todo:
        add_todo = re.search(r"\b(?:to-?do|todo)[:\s]+(.+)$", low)
    if add_todo:
        item = add_todo.group(1).strip(" .")
        if item:
            _LISTS["todo"].append(item)
            return (f"Got it — I added “{item}” to your to-do list. You have {len(_LISTS['todo'])} item(s).", "todo")
    if re.search(r"\b(what'?s on my to-?do|list (my )?to-?dos?|show (my )?to-?do)\b", low):
        if not _LISTS["todo"]:
            return ("Your to-do list is empty. Say “add … to my todo” to put something on it.", "todo")
        lines = "; ".join(f"{i+1}. {t}" for i, t in enumerate(_LISTS["todo"][:12]))
        return (f"Here’s your to-do: {lines}.", "todo")
    if re.search(r"\b(clear|empty)\s+(my\s+)?to-?do", low):
        n = len(_LISTS["todo"])
        _LISTS["todo"].clear()
        return (f"Cleared {n} to-do item(s).", "todo")

    # Grocery / shopping
    g = re.search(r"\b(?:add|put)\s+(.+?)\s+(?:to|on)\s+(?:my\s+)?(?:grocery|shopping)\s*list\b", low)
    if g:
        item = g.group(1).strip(" .")
        key = "grocery" if "grocery" in low else "shopping"
        _LISTS[key].append(item)
        return (f"Added “{item}” to your {key} list. {len(_LISTS[key])} item(s) now.", key)
    if re.search(r"\b(grocery|shopping)\s+list\b", low) and re.search(r"\b(show|list|read|what)\b", low):
        key = "grocery" if "grocery" in low else "shopping"
        if not _LISTS[key]:
            return (f"Your {key} list is empty.", key)
        return (f"Your {key} list: " + ", ".join(_LISTS[key][:20]) + ".", key)

    # Reminders (session memory)
    rem = re.search(r"\bremind me (?:to |that )?(.+)$", low)
    if rem:
        thing = rem.group(1).strip(" .")
        _REMINDERS.append({"text": thing, "at": time.time()})
        return (f"I’ll keep that in mind for this session: “{thing}”. Ask “what are my reminders?” anytime.", "remind")
    if re.search(r"\b(my reminders|what did i ask you to remember|reminders)\b", low):
        if not _REMINDERS:
            return ("No reminders yet. Say “remind me to …” and I’ll hold it.", "remind")
        bits = "; ".join(r["text"] for r in _REMINDERS[-8:])
        return (f"Reminders: {bits}.", "remind")

    # Focus / pomodoro
    if re.search(r"\b(pomodoro|focus (mode|session)|deep work|help me focus)\b", low):
        return (
            "Alright — focus mode. Twenty-five minutes on one thing, then a five-minute break. "
            "What’s the single task for this block?",
            "focus",
        )
    if re.search(r"\b(break time|i need a break)\b", low):
        return ("Take five. Stand up, water, look away from the screen. I’ll be here when you’re back.", "focus")

    # Food / hydration
    if re.search(r"\b(what should i (eat|cook)|meal idea|i'?m hungry)\b", low):
        return (
            "Keep it simple: protein plus something fresh — eggs and toast, a bowl with rice and veg, "
            "or a big salad with leftovers. What do you already have in the kitchen?",
            "food",
        )
    if re.search(r"\b(drink water|hydrat|i'?m thirsty)\b", low):
        return ("Good call — grab water now. Little and often beats chugging later.", "food")
    if re.search(r"\b(coffee|caffeine)\b", low) and re.search(r"\b(should|too much|late)\b", low):
        return ("If it’s after mid-afternoon, maybe switch to water or tea so sleep stays okay.", "food")

    # Travel
    if re.search(r"\b(pack|packing list|what should i pack)\b", low):
        return (
            "Core pack: ID, charger, meds, one outfit extra, weather layer, and anything you can’t buy there. "
            "How many days and what’s the climate?",
            "travel",
        )
    if re.search(r"\b(commute|traffic|running late)\b", low):
        return (
            "Breathe. Text ahead if you can, pick the simplest route, and don’t stack errands. "
            "Want a short “I’m late” message drafted?",
            "travel",
        )
    if re.search(r"\b(flight|airport|boarding)\b", low):
        return (
            "Airport rule of thumb: be there early enough that security is boring. "
            "Have boarding pass offline and a water bottle empty for security. What’s your departure window?",
            "travel",
        )

    # Mood / calm
    if re.search(r"\b(i'?m (stressed|anxious|overwhelmed)|calm me|panic)\b", low):
        return (
            "I’m here. Feet on the floor, longer exhale than inhale — four in, six out, three times. "
            "You don’t have to solve everything this minute. What’s the one next tiny step?",
            "mood",
        )
    if re.search(r"\b(i'?m tired|exhausted|burned? out)\b", low):
        return (
            "That counts. If you can, short rest beats pushing empty. "
            "Otherwise pick the smallest useful task and let the rest wait. Want me to hold a short to-do?",
            "mood",
        )

    # Weather honesty
    if re.search(r"\b(weather|forecast|rain today|temperature outside)\b", low):
        return (
            "I can’t see live weather from here without a data feed — check your phone weather widget "
            "or say “open weather” to the desktop agent. Want a packing tip for rain or heat instead?",
            "weather_talk",
        )

    # Day plan
    if re.search(r"\b(plan my day|what should i do today|daily plan)\b", low):
        return (
            "Let’s sketch three blocks: one must-do, one should-do, one nice-to-do. "
            "What’s the must-do before lunch?",
            "calendar_talk",
        )

    # Draft a message
    draft = re.search(r"\b(?:draft|write)\s+(?:a\s+)?(?:text|message|email|note)\s*(?:to\s+[\w\s]+)?[:\-]?\s*(.+)$", low)
    if draft:
        body = draft.group(1).strip()
        return (
            f"Here’s a clean version you can send: “{body[0].upper() + body[1:] if body else ''}” "
            "Want it shorter or warmer?",
            "draft",
        )
    if re.search(r"\b(help me say|how do i say|word this)\b", low):
        return (
            "Tell me who it’s for and the one thing they need to know — I’ll phrase it simply.",
            "draft",
        )

    # Timer (spoken only — no background daemon)
    t = re.search(r"\b(?:set\s+)?(?:a\s+)?timer\s+(?:for\s+)?(\d+)\s*(min|minute|minutes|sec|second|seconds|m|s)\b", low)
    if t:
        n = int(t.group(1))
        unit = t.group(2)
        secs = n * 60 if unit.startswith("m") else n
        if secs > 7200:
            return ("That’s a long timer — maybe break it into shorter focus blocks?", "timer")
        mins = max(1, round(secs / 60)) if secs >= 60 else 0
        if mins:
            return (
                f"Okay — mentally mark {mins} minute(s). I’ll stay with you; "
                "when it feels done, just say “timer done” or start the next thing.",
                "timer",
            )
        return (f"Short timer for {secs} seconds — count it down and I’ll be here after.", "timer")

    return None


def skill_help() -> str:
    skills = list_skills()
    lines = [
        "I'm Aria — your voice product on this host. I can:",
        "",
        "**Talk & organize**",
    ]
    for s in skills:
        lines.append(f"- {s['blurb']}")
    lines.extend(
        [
            "",
            "**Do real host work** (you confirm pay)",
            "- Order food options — “order sushi delivery”",
            "- Flights — “flights to NYC next Friday”",
            "- Shop — “buy headphones under 100”",
            "- Reserve tables — “reserve dinner Friday for 2”",
            "- Read your screen — “what’s on my screen”",
            "- Plan the day — “plan my morning”",
            "",
            "Just say it naturally. Mic + speak-back on desk and phone.",
        ]
    )
    return "\n".join(lines)
