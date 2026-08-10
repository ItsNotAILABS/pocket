"""Everyday life ops — food order, flights, shopping, web navigation.

Designed for a human digital assistant on the host (Edge + Working board).
Never auto-pay or finalize bookings; always stop at needs_you for confirm.
"""

from __future__ import annotations

import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple


LIFE_KINDS = frozenset({"food_order", "flight", "shop", "browse", "buy", "reservation"})


def classify_life(text: str) -> Optional[Tuple[str, str]]:
    """Return (kind, title) if this is everyday life, else None."""
    t = (text or "").strip()
    low = t.lower()
    if not t:
        return None

    def strip_lead(s: str) -> str:
        return re.sub(
            r"^(hey|hi|can you|could you|please|pls|i want you to|i need you to|help me|"
            r"i want to|i wanna|i'd like to|i would like to)\s+",
            "",
            s,
            flags=re.I,
        ).strip()

    title = strip_lead(t)[:200]

    # Food delivery / order
    if re.search(
        r"\b(order food|food delivery|deliver|doordash|uber ?eats|grubhub|postmates|"
        r"seamless|order (me )?(pizza|sushi|thai|chinese|burger|tacos|coffee)|"
        r"get (me )?(food|dinner|lunch) delivered|hungry)\b",
        low,
    ):
        return "food_order", title

    # Flights
    if re.search(
        r"\b(flight|flights|fly to|fly from|airfare|airline|book (a )?flight|"
        r"google flights|kayak|expedia|southwest|united|delta|american airlines|"
        r"round ?trip|one way ticket|airport)\b",
        low,
    ):
        return "flight", title

    # Shopping (broader than buy — includes "find me headphones")
    if re.search(
        r"\b(shop|shopping|amazon|walmart|target|best buy|ebay|add to cart|"
        r"buy |purchase|order (me )?(a |an |the )?|"
        r"find (me )?(cheap |good )?(headphones|laptop|shoes|gift|phone))\b",
        low,
    ) and not re.search(r"\b(food|pizza|sushi|doordash|flight)\b", low):
        return "shop", title

    # Web navigation
    if re.search(
        r"\b(open |go to |navigate|browse |visit |show me |look up on (the )?web|"
        r"search (google|bing|the web) for|web search)\b",
        low,
    ):
        return "browse", title

    return None


def parse_food(text: str) -> Dict[str, Any]:
    low = (text or "").lower()
    cuisine = ""
    for c in (
        "pizza",
        "sushi",
        "thai",
        "chinese",
        "mexican",
        "indian",
        "burger",
        "tacos",
        "coffee",
        "bbq",
        "ramen",
        "vegan",
    ):
        if c in low:
            cuisine = c
            break
    service = "doordash"
    if "uber" in low:
        service = "ubereats"
    elif "grubhub" in low:
        service = "grubhub"
    place = re.sub(
        r"\b(order|food|delivery|deliver|from|via|on|me|a|an|the|please|hungry)\b",
        " ",
        text or "",
        flags=re.I,
    )
    place = re.sub(r"\s+", " ", place).strip(" ,.") or cuisine or "food near me"
    return {"cuisine": cuisine, "service": service, "query": place[:120], "raw": text}


def parse_flight(text: str) -> Dict[str, Any]:
    t = text or ""
    # "fly to NYC from DFW" / "flights to London"
    to_m = re.search(r"\b(?:to|into)\s+([A-Za-z][A-Za-z\s]{1,40}?)(?:\s+from|\s+on|\s+for|$)", t, re.I)
    from_m = re.search(r"\bfrom\s+([A-Za-z][A-Za-z\s]{1,40}?)(?:\s+to|\s+on|$)", t, re.I)
    dest = (to_m.group(1).strip() if to_m else "") or ""
    origin = (from_m.group(1).strip() if from_m else "") or ""
    if not dest:
        m2 = re.search(r"\bflights?\s+(?:to\s+)?([A-Za-z][A-Za-z\s]{1,30})", t, re.I)
        dest = (m2.group(1).strip() if m2 else "") or "destination"
    date_m = re.search(
        r"\b(tomorrow|tonight|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b",
        t,
        re.I,
    )
    when = date_m.group(0) if date_m else ""
    return {"origin": origin, "destination": dest, "when": when, "raw": text}


def parse_shop(text: str) -> Dict[str, Any]:
    t = text or ""
    budget = ""
    bm = re.search(r"\$\s*(\d+(?:\.\d+)?)|under\s+(\d+)|less than\s+(\d+)", t, re.I)
    if bm:
        budget = bm.group(1) or bm.group(2) or bm.group(3) or ""
    q = re.sub(
        r"\b(buy|purchase|shop for|find me|order me|get me|please|a|an|the)\b",
        " ",
        t,
        flags=re.I,
    )
    q = re.sub(r"\s+", " ", q).strip(" ,.") or t[:80]
    return {"query": q[:140], "budget": budget, "raw": text}


def urls_for_food(info: Dict[str, Any]) -> List[Dict[str, str]]:
    q = info.get("query") or "food near me"
    enc = urllib.parse.quote(q)
    svc = info.get("service") or "doordash"
    links = [
        {"title": "DoorDash search", "url": f"https://www.doordash.com/search/store/{enc}/", "snippet": "delivery"},
        {"title": "Uber Eats", "url": f"https://www.ubereats.com/search?q={enc}", "snippet": "delivery"},
        {"title": "Google food near me", "url": f"https://www.google.com/search?q={enc}+delivery+near+me", "snippet": "options"},
    ]
    if svc == "grubhub":
        links.insert(0, {"title": "Grubhub", "url": f"https://www.grubhub.com/search?queryText={enc}", "snippet": "delivery"})
    return links


def urls_for_flight(info: Dict[str, Any]) -> List[Dict[str, str]]:
    dest = info.get("destination") or ""
    origin = info.get("origin") or ""
    when = info.get("when") or ""
    q = f"flights {origin + ' to ' if origin else 'to '}{dest} {when}".strip()
    enc = urllib.parse.quote(q)
    # Google Flights deep-ish search
    gf_q = urllib.parse.quote(f"{origin or 'Your city'} to {dest}")
    return [
        {
            "title": "Google Flights",
            "url": f"https://www.google.com/travel/flights?q={gf_q}",
            "snippet": f"{origin or '?'} → {dest}",
        },
        {"title": "Kayak", "url": f"https://www.kayak.com/flights/{enc}", "snippet": "compare"},
        {"title": "Google search", "url": f"https://www.google.com/search?q={enc}", "snippet": "options"},
        {"title": "Expedia", "url": f"https://www.expedia.com/Flights-Search?q={enc}", "snippet": "book"},
    ]


def urls_for_shop(info: Dict[str, Any]) -> List[Dict[str, str]]:
    q = info.get("query") or "product"
    if info.get("budget"):
        q = f"{q} under ${info['budget']}"
    enc = urllib.parse.quote(q)
    return [
        {"title": "Amazon", "url": f"https://www.amazon.com/s?k={enc}", "snippet": "shop"},
        {"title": "Google Shopping", "url": f"https://www.google.com/search?tbm=shop&q={enc}", "snippet": "compare prices"},
        {"title": "Walmart", "url": f"https://www.walmart.com/search?q={enc}", "snippet": "shop"},
        {"title": "Best Buy", "url": f"https://www.bestbuy.com/site/searchpage.jsp?st={enc}", "snippet": "electronics"},
    ]


def urls_for_browse(text: str) -> List[Dict[str, str]]:
    t = (text or "").strip()
    # bare URL
    m = re.search(r"https?://\S+", t)
    if m:
        return [{"title": "Open link", "url": m.group(0).rstrip(".,)"), "snippet": "direct"}]
    # domain-ish
    m2 = re.search(r"\b((?:www\.)?[a-z0-9-]+\.(?:com|org|net|io|co|gov|edu)(?:/\S*)?)\b", t, re.I)
    if m2:
        host = m2.group(1)
        if not host.startswith("http"):
            host = "https://" + host
        return [{"title": "Open site", "url": host, "snippet": "site"}]
    q = re.sub(r"\b(open|go to|navigate|browse|visit|search|google|for|the|web)\b", " ", t, flags=re.I)
    q = re.sub(r"\s+", " ", q).strip() or t
    enc = urllib.parse.quote(q[:120])
    return [
        {"title": "Google", "url": f"https://www.google.com/search?q={enc}", "snippet": "search"},
        {"title": "Bing", "url": f"https://www.bing.com/search?q={enc}", "snippet": "search"},
        {"title": "DuckDuckGo", "url": f"https://duckduckgo.com/?q={enc}", "snippet": "search"},
    ]


def open_best(url: str) -> Dict[str, Any]:
    try:
        from pocket.virtual_computer import act

        r = act("open_url", url=url)
        return {"ok": bool(r.get("ok")), "url": url, "result": r}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)[:160]}


def execute_life_item(
    item: Dict[str, Any],
    *,
    search_fn=None,
    stream_fn=None,
    job_id: str = "",
) -> Dict[str, Any]:
    """Mutate board item for food / flight / shop / browse."""
    kind = item.get("kind") or "errand"
    raw = item.get("raw") or item.get("title") or ""
    tools: List[Dict[str, Any]] = []
    evidence: List[str] = []
    links: List[Dict[str, str]] = []
    choices: List[Dict[str, str]] = []
    next_steps: List[str] = []

    def log(msg: str) -> None:
        if stream_fn:
            try:
                stream_fn(msg)
            except Exception:
                pass

    def do_search(q: str, n: int = 6, label: str = "Findings") -> None:
        if not search_fn:
            return
        try:
            sr = search_fn(q, n, label=label)
            return sr
        except TypeError:
            try:
                search_fn(q, n)
            except Exception:
                pass

    t0 = time.time()
    item["status"] = "running"
    item["updated_at"] = time.time()

    if kind == "food_order":
        info = parse_food(raw)
        item["life"] = info
        log(f"Food order · {info.get('query')} via {info.get('service')}")
        do_search(f"{info.get('query')} delivery near me", 6, "Food options")
        do_search(f"best {info.get('cuisine') or info.get('query')} delivery", 4, "Top picks")
        for L in urls_for_food(info):
            links.append(L)
            choices.append(L)
        best = links[0]["url"] if links else ""
        log("Opening delivery surface…")
        op = open_best(best)
        tools.append({"ok": op.get("ok"), "skill": "open_url", "url": best})
        if op.get("ok"):
            log("Delivery site opened in Edge")
        item["status"] = "needs_you"
        item["gate_message"] = (
            f"Food delivery options for **{info.get('query')}**. "
            "I opened a delivery site — **you place the order and pay**. I won't click checkout."
        )
        item["result_summary"] = f"Food · {info.get('query')[:40]} · choose & pay"
        next_steps = ["Pick restaurant in Edge", "Add items", "Checkout yourself", "Mark Done"]
        evidence.insert(
            0,
            "**Food order choices**\n"
            + "\n".join(f"{i}. [{c.get('title')}]({c.get('url')})" for i, c in enumerate(choices[:6], 1)),
        )

    elif kind == "flight":
        info = parse_flight(raw)
        item["life"] = info
        dest = info.get("destination") or "?"
        origin = info.get("origin") or "your city"
        log(f"Flights · {origin} → {dest}" + (f" · {info.get('when')}" if info.get("when") else ""))
        do_search(
            f"flights {origin} to {dest} {info.get('when') or ''}".strip(),
            6,
            "Flight options",
        )
        for L in urls_for_flight(info):
            links.append(L)
            choices.append(L)
        best = links[0]["url"] if links else ""
        log("Opening Google Flights…")
        op = open_best(best)
        tools.append({"ok": op.get("ok"), "skill": "open_url", "url": best})
        item["status"] = "needs_you"
        item["gate_message"] = (
            f"Flight search **{origin} → {dest}**. "
            "I opened Google Flights — **you pick seats and pay**. I never finalize a ticket."
        )
        item["result_summary"] = f"Flights · {origin}→{dest}" + (f" · {info.get('when')}" if info.get("when") else "")
        next_steps = ["Compare fares", "Choose flight", "Book & pay yourself", "Mark Done"]
        evidence.insert(
            0,
            f"**Flight search:** {origin} → {dest}\n"
            + "\n".join(f"{i}. [{c.get('title')}]({c.get('url')})" for i, c in enumerate(choices[:5], 1)),
        )

    elif kind in ("shop", "buy"):
        info = parse_shop(raw)
        item["life"] = info
        log(f"Shopping · {info.get('query')}" + (f" under ${info.get('budget')}" if info.get("budget") else ""))
        do_search(f"buy {info.get('query')} best options price", 6, "Products")
        for L in urls_for_shop(info):
            links.append(L)
            choices.append(L)
        best = links[0]["url"] if links else ""
        log("Opening shop search…")
        op = open_best(best)
        tools.append({"ok": op.get("ok"), "skill": "open_url", "url": best})
        try:
            from pocket.purchase_playbooks import run_playbook_scaffold

            pb = run_playbook_scaffold("generic_checkout_scaffold")
            tools.append({"ok": True, "skill": "purchase_scaffold"})
            evidence.append(pb.get("message") or "Checkout scaffold (no payment)")
        except Exception:
            pass
        item["status"] = "needs_you"
        item["gate_message"] = (
            f"Shopping options for **{info.get('query')}**. "
            "I opened Amazon/shopping search — **you checkout and pay**."
        )
        item["result_summary"] = f"Shop · {info.get('query')[:40]}" + (
            f" · <${info.get('budget')}" if info.get("budget") else ""
        )
        next_steps = ["Compare products", "Add to cart", "Pay yourself", "Mark Done"]
        evidence.insert(
            0,
            "**Shop choices**\n"
            + "\n".join(f"{i}. [{c.get('title')}]({c.get('url')})" for i, c in enumerate(choices[:6], 1)),
        )

    elif kind == "browse":
        log(f"Web · {(raw or '')[:80]}")
        do_search(raw, 5, "Web results")
        for L in urls_for_browse(raw):
            links.append(L)
            choices.append(L)
        best = links[0]["url"] if links else "https://www.google.com"
        log(f"Opening {best[:60]}…")
        op = open_best(best)
        tools.append({"ok": op.get("ok"), "skill": "open_url", "url": best})
        # Light sense after open
        try:
            time.sleep(1.2)
            from pocket.virtual_computer import act

            s = act("sense", max_ui=300)
            tools.append({"ok": bool(s.get("ok", True)), "skill": "sense"})
            if s.get("brief") or s.get("after_sense"):
                evidence.append("**On page**\n" + str(s.get("brief") or s.get("after_sense") or "")[:400])
                log("Page sensed")
        except Exception:
            pass
        item["status"] = "done" if op.get("ok") else "needs_you"
        item["gate_message"] = "" if op.get("ok") else "Could not open browser — try again"
        item["result_summary"] = f"Opened · {(best or '')[:50]}"
        next_steps = ["Continue in Edge", "Ask a follow-up", "Say: scroll / click …"]
        evidence.insert(
            0,
            "**Web**\n" + "\n".join(f"- [{c.get('title')}]({c.get('url')})" for c in choices[:5]),
        )

    else:
        return item

    item["tools"] = (item.get("tools") or []) + tools[-10:]
    item["evidence"] = (evidence + list(item.get("evidence") or []))[:10]
    item["links"] = (links + list(item.get("links") or []))[:10]
    item["choices"] = (choices + list(item.get("choices") or []))[:12]
    item["next_steps"] = next_steps[:6]
    item["ms"] = int((time.time() - t0) * 1000)
    item["updated_at"] = time.time()
    item["booking"] = {
        "url": (links[0]["url"] if links else ""),
        "kind": kind,
        "confirm_blocked": True,
    }
    return item


def life_welcome() -> str:
    return (
        "# Everyday life assistant\n\n"
        "I help with **real digital life** on this computer:\n\n"
        "| Need | Say |\n|------|-----|\n"
        "| **Order food** | *Order sushi delivery* / *DoorDash pizza* |\n"
        "| **Book flights** | *Flights to NYC next Friday* |\n"
        "| **Shop** | *Buy headphones under $100* |\n"
        "| **Web** | *Open google flights* / *Search best hotels in Austin* |\n"
        "| **Dinner out** | *Reserve Del Frisco Dallas 8:30 for 2* |\n\n"
        "I open the right sites in Edge, research options, and **stop before you pay or confirm**.\n"
    )


# ---------------------------------------------------------------------------
# Agent-callable life skills (embedded platform tools for ALL agents)
# Never auto-pay; always confirm_blocked=True when a checkout surface is opened.
# ---------------------------------------------------------------------------

LIFE_SKILL_IDS = frozenset(
    {
        "life_catalog",
        "life_welcome",
        "life_status",
        "life_classify",
        "food_order",
        "food",
        "flight_search",
        "flight",
        "flights",
        "shop_search",
        "shop",
        "buy",
        "web_browse",
        "browse",
        "reservation",
        "reserve",
        "dining",
    }
)


def life_skill_catalog() -> List[Dict[str, Any]]:
    """Discoverable catalog of everyday life skills for agents."""
    return [
        {
            "id": "food_order",
            "desc": "Food delivery options (DoorDash/UberEats) — you pay",
            "say": "Order sushi delivery / DoorDash pizza",
            "tags": ["life", "food"],
        },
        {
            "id": "flight_search",
            "desc": "Flight search (Google Flights) — you book & pay",
            "say": "Flights to NYC next Friday",
            "tags": ["life", "travel"],
        },
        {
            "id": "shop_search",
            "desc": "Shopping search (Amazon etc.) — you checkout",
            "say": "Buy headphones under $100",
            "tags": ["life", "shop"],
        },
        {
            "id": "web_browse",
            "desc": "Open/search the web in Edge + light sense",
            "say": "Open google flights / Search hotels Austin",
            "tags": ["life", "web"],
        },
        {
            "id": "reservation",
            "desc": "Restaurant reservation drive (OpenTable) — you confirm",
            "say": "Reserve Del Frisco Dallas 8:30 for 2",
            "tags": ["life", "dining"],
        },
        {
            "id": "life_catalog",
            "desc": "List all everyday life skills",
            "say": "What life skills do you have?",
            "tags": ["life", "discover"],
        },
        {
            "id": "life_status",
            "desc": "Working board + life ops status",
            "say": "Life ops status / working board",
            "tags": ["life", "status"],
        },
        {
            "id": "life_classify",
            "desc": "Classify text into food/flight/shop/browse/reservation",
            "say": "(auto) on any everyday request",
            "tags": ["life", "route"],
        },
    ]


def _life_item_shell(kind: str, raw: str) -> Dict[str, Any]:
    return {
        "id": f"life-{kind}-{int(time.time() * 1000) % 10_000_000}",
        "kind": kind,
        "title": (raw or kind)[:200],
        "raw": raw or "",
        "status": "queued",
        "tools": [],
        "evidence": [],
        "links": [],
        "choices": [],
        "next_steps": [],
        "created_at": time.time(),
        "updated_at": time.time(),
    }


def run_life_skill(
    skill_id: str,
    *,
    prompt: str = "",
    params: Optional[Dict[str, Any]] = None,
    open_browser: bool = True,
) -> Dict[str, Any]:
    """Execute an embedded life skill for any agent turn.

    Returns structured choices/links. Opens Edge when open_browser=True.
    Never finalizes payment or booking.
    """
    sid = (skill_id or "").strip().lower().replace("-", "_")
    params = params or {}
    raw = (prompt or params.get("text") or params.get("query") or params.get("prompt") or "").strip()
    t0 = time.time()

    if sid in ("life_catalog", "life_welcome", "life_skills"):
        cat = life_skill_catalog()
        return {
            "ok": True,
            "skill": "life_catalog",
            "message": "Everyday life skills embedded for all agents",
            "welcome": life_welcome(),
            "skills": cat,
            "count": len(cat),
            "doctrine": "Never auto-pay. Stop at needs_you for checkout/confirm.",
            "ms": int((time.time() - t0) * 1000),
        }

    if sid == "life_classify":
        hit = classify_life(raw)
        return {
            "ok": True,
            "skill": "life_classify",
            "kind": hit[0] if hit else None,
            "title": hit[1] if hit else None,
            "raw": raw[:200],
            "ms": int((time.time() - t0) * 1000),
        }

    if sid in ("life_status", "board_status", "working_board"):
        out: Dict[str, Any] = {"ok": True, "skill": "life_status", "catalog": life_skill_catalog()}
        try:
            from pocket.working_board import status as board_status

            out["board"] = board_status()
        except Exception as e:
            out["board_error"] = str(e)[:160]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    # Map aliases → kind
    kind_map = {
        "food_order": "food_order",
        "food": "food_order",
        "delivery": "food_order",
        "flight_search": "flight",
        "flight": "flight",
        "flights": "flight",
        "shop_search": "shop",
        "shop": "shop",
        "buy": "shop",
        "purchase": "shop",
        "web_browse": "browse",
        "browse": "browse",
        "web": "browse",
        "open_web": "browse",
        "reservation": "reservation",
        "reserve": "reservation",
        "dining": "reservation",
        "opentable": "reservation",
    }
    kind = kind_map.get(sid)
    if not kind:
        # Auto-classify when skill is generic life run
        if sid in ("life", "life_run", "life_ops"):
            hit = classify_life(raw)
            if hit:
                kind = hit[0]
            else:
                return {
                    "ok": False,
                    "skill": sid,
                    "error": "Could not classify life intent — try food_order, flight_search, shop_search, web_browse, reservation",
                    "catalog": life_skill_catalog(),
                }
        else:
            return {
                "ok": False,
                "skill": sid,
                "error": f"unknown life skill: {sid}",
                "available": sorted(LIFE_SKILL_IDS),
            }

    if not raw:
        return {
            "ok": False,
            "skill": sid,
            "error": f"prompt required for {kind}",
            "hint": f"POST /v1/skills/run skill={sid} with prompt describing the request",
        }

    # Reservation: OpenTable search + optional UI drive (never finalize)
    if kind == "reservation":
        place = raw[:80]
        party = 2
        when = ""
        time_24 = ""
        date_iso = ""
        try:
            from pocket.working_board import parse_dining_details, _opentable_datetime

            dining = parse_dining_details(raw)
            place = dining.get("place") or place
            when = dining.get("when") or ""
            time_24 = dining.get("time_24") or ""
            party = int(dining.get("party") or 2)
            date_iso = dining.get("date_iso") or ""
            dt = _opentable_datetime(date_iso, time_24)
        except Exception:
            dining = {"place": place, "party": party}
            dt = ""
        ot_params = {"term": place[:80], "covers": party}
        if dt:
            ot_params["dateTime"] = dt
        ot = "https://www.opentable.com/s?" + urllib.parse.urlencode(ot_params)
        maps = "https://www.google.com/maps/search/" + urllib.parse.quote(place[:80])
        links = [
            {
                "title": f"OpenTable · {party}" + (f" · {when or time_24}" if (when or time_24) else ""),
                "url": ot,
                "snippet": "reserve",
            },
            {"title": "Google Maps", "url": maps, "snippet": "location"},
            {
                "title": "Google reserve",
                "url": "https://www.google.com/search?q="
                + urllib.parse.quote(f"{place} reservation opentable"),
                "snippet": "options",
            },
        ]
        drive: Dict[str, Any] = {}
        if open_browser:
            try:
                from pocket.working_board import drive_reservation_ui

                drive = drive_reservation_ui(
                    open_url=ot,
                    place=place,
                    when=when,
                    time_24=time_24,
                    party=party,
                    date_iso=date_iso,
                    stream_fn=None,
                )
            except Exception as e:
                drive = {"ok": False, "error": str(e)[:160]}
                open_best(ot)
        return {
            "ok": True,
            "skill": "reservation",
            "kind": "reservation",
            "dining": dining if isinstance(dining, dict) else {"place": place},
            "message": f"Reservation · {place}" + (f" · {when or time_24}" if (when or time_24) else ""),
            "links": links,
            "choices": links,
            "drive": {
                "ok": drive.get("ok"),
                "url": drive.get("url"),
                "clicked": (drive.get("clicked") or [])[:8],
                "slots": (drive.get("slots") or [])[:8],
                "notes": (drive.get("notes") or [])[-8:],
            }
            if drive
            else {},
            "confirm_blocked": True,
            "gate_message": (
                f"Opened OpenTable for **{place}**. "
                "**You confirm the table** — I never finalize a reservation."
            ),
            "next_steps": ["Pick time slot", "Confirm yourself", "Mark Done on Working board"],
            "ms": int((time.time() - t0) * 1000),
        }

    item = _life_item_shell(kind, raw)
    # If caller does not want browser, still build links via parse only
    if not open_browser:
        if kind == "food_order":
            info = parse_food(raw)
            links = urls_for_food(info)
            return {
                "ok": True,
                "skill": "food_order",
                "kind": kind,
                "life": info,
                "links": links,
                "choices": links,
                "confirm_blocked": True,
                "gate_message": "Food options ready — you place the order and pay.",
                "ms": int((time.time() - t0) * 1000),
            }
        if kind == "flight":
            info = parse_flight(raw)
            links = urls_for_flight(info)
            return {
                "ok": True,
                "skill": "flight_search",
                "kind": kind,
                "life": info,
                "links": links,
                "choices": links,
                "confirm_blocked": True,
                "gate_message": "Flight options ready — you book and pay.",
                "ms": int((time.time() - t0) * 1000),
            }
        if kind in ("shop", "buy"):
            info = parse_shop(raw)
            links = urls_for_shop(info)
            return {
                "ok": True,
                "skill": "shop_search",
                "kind": kind,
                "life": info,
                "links": links,
                "choices": links,
                "confirm_blocked": True,
                "gate_message": "Shop options ready — you checkout and pay.",
                "ms": int((time.time() - t0) * 1000),
            }
        links = urls_for_browse(raw)
        return {
            "ok": True,
            "skill": "web_browse",
            "kind": "browse",
            "links": links,
            "choices": links,
            "ms": int((time.time() - t0) * 1000),
        }

    # Full execute (open Edge + structure)
    try:
        from pocket.web_research import search_web

        def _search(q: str, n: int = 6, label: str = "Findings") -> None:
            try:
                sr = search_web(q, max_results=n)
                if sr.get("ok") and sr.get("results"):
                    item.setdefault("evidence", []).append(
                        f"**{label}**\n"
                        + "\n".join(
                            f"- [{r.get('title')}]({r.get('url')}) — {(r.get('snippet') or '')[:120]}"
                            for r in (sr.get("results") or [])[:n]
                        )
                    )
            except Exception:
                pass

        item = execute_life_item(item, search_fn=_search)
    except Exception:
        item = execute_life_item(item, search_fn=None)

    return {
        "ok": True,
        "skill": sid if sid in LIFE_SKILL_IDS else kind,
        "kind": kind,
        "status": item.get("status"),
        "life": item.get("life"),
        "links": item.get("links") or [],
        "choices": item.get("choices") or [],
        "evidence": (item.get("evidence") or [])[:6],
        "tools": item.get("tools") or [],
        "next_steps": item.get("next_steps") or [],
        "result_summary": item.get("result_summary") or "",
        "gate_message": item.get("gate_message") or "",
        "confirm_blocked": True,
        "booking": item.get("booking") or {"confirm_blocked": True, "kind": kind},
        "message": item.get("result_summary") or item.get("gate_message") or f"Life skill {kind} ran",
        "ms": int((time.time() - t0) * 1000),
    }


def is_life_skill(skill_id: str) -> bool:
    sid = (skill_id or "").strip().lower().replace("-", "_")
    return sid in LIFE_SKILL_IDS or sid in (
        "life",
        "life_run",
        "life_ops",
        "life_skills",
        "delivery",
        "purchase",
        "web",
        "open_web",
        "opentable",
        "board_status",
        "working_board",
    )
