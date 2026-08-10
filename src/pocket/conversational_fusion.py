"""Conversational Fusion / Deep Fusion — industry layer in the POCKET host.

Public pocket-voice-to-text emits a clean fusion_metadata.v1 vector.
This module owns DFW airline+hospitality priors, expert routing, patience
callbacks, and multi-domain recovery patterns — without polluting the OSS voice repo.

Mirrors visual Fusion-Sense: normalize input → fuse → act (route / patience / preload).
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

SCHEMA = "pocket.voice.fusion_metadata.v1"
FUSION_SCHEMA = "pocket.conversational_fusion.v1"
VERSION = "1.0"

# DFW airline + hospitality priors (narrow vertical, expandable)
DFW_EXPERTS = {
    "airport_guide": {
        "id": "airport_guide",
        "domain": "airport",
        "label": "Airport Guide",
        "personality": "aria",
        "patience_boost_ms": 200,
        "priors": [
            "delays often chain into hotel hold + dining",
            "gates move; bags lag behind passenger",
            "connections at DFW need terminal + shuttle awareness",
        ],
    },
    "hotel_host": {
        "id": "hotel_host",
        "domain": "hotel",
        "label": "Hotel Host",
        "personality": "aria",
        "patience_boost_ms": 250,
        "priors": [
            "late check-in after delayed flights is common",
            "hold room language reduces re-explain",
            "airport lodging graph connects to shuttles",
        ],
    },
    "transit_concierge": {
        "id": "transit_concierge",
        "domain": "transit",
        "label": "Transit Concierge",
        "personality": "aria",
        "patience_boost_ms": 150,
        "priors": [
            "shuttle times couple hotel and terminal",
            "rideshare surge after mass delays",
        ],
    },
    "dining_diplomat": {
        "id": "dining_diplomat",
        "domain": "dining",
        "label": "Dining Diplomat",
        "personality": "aria",
        "patience_boost_ms": 100,
        "priors": [
            "hungry stressed travelers need short options",
            "terminal food vs hotel restaurant tradeoffs",
        ],
    },
    "support": {
        "id": "support",
        "domain": "support",
        "label": "Call center / CS",
        "personality": "support",
        "patience_boost_ms": 300,
        "priors": ["escalate only after domain facts captured"],
    },
}

# Recovery patterns for multi-domain prestress (early fusion heads)
_RECOVERY_PATTERNS: List[Tuple[re.Pattern[str], List[str], str]] = [
    (
        re.compile(r"delay|delayed|missed connection|cancelled|canceled", re.I),
        ["airport_guide", "hotel_host", "transit_concierge"],
        "flight_disruption_recovery",
    ),
    (
        re.compile(r"hold (my )?room|late check[- ]?in|hotel", re.I),
        ["hotel_host", "airport_guide"],
        "hotel_recovery",
    ),
    (
        re.compile(r"shuttle|rideshare|uber|lyft|taxi", re.I),
        ["transit_concierge", "hotel_host", "airport_guide"],
        "transit_bridge",
    ),
    (
        re.compile(r"restaurant|dining|hungry|eat|food", re.I),
        ["dining_diplomat", "hotel_host"],
        "dining_assist",
    ),
    (
        re.compile(r"bag|baggage|luggage|claim", re.I),
        ["airport_guide", "transit_concierge"],
        "baggage_assist",
    ),
]


def schema() -> Dict[str, Any]:
    return {
        "ok": True,
        "voice_metadata_schema": SCHEMA,
        "fusion_schema": FUSION_SCHEMA,
        "version": VERSION,
        "industry": "dfw_airline_hospitality",
        "experts": list(DFW_EXPERTS.values()),
        "input": {
            "acoustic": ["stress", "speaking_rate", "energy_mean", "pause_pattern"],
            "linguistic": ["transcript", "incomplete", "entities", "entity_density"],
            "turn": ["scenario", "threshold_ms", "decision"],
            "domain": ["active_expert", "candidate_experts", "confidence"],
            "context_buffer": ["airport", "hotel", "transit", "dining"],
            "session": ["history_length", "dominant_domain", "user_state"],
        },
        "outputs": {
            "primary_expert": "expert id to weight",
            "expert_weights": "soft blend over experts",
            "patience_delta_ms": "add to turn silence threshold",
            "listening": "scenario/stress/expert/barge_in callback to voice stack",
            "preload_context": "facts to put into cross-domain buffer",
            "prompt_boost": "short system nudge for multi-domain reply",
            "pattern": "matched recovery pattern id",
        },
        "doctrine": "Voice OSS emits metadata; POCKET fuses industry intelligence.",
    }


def _clamp01(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, v))


def _as_meta(body: Dict[str, Any]) -> Dict[str, Any]:
    """Accept full vector, or nested under fusion / metadata / raw turn fields."""
    if not isinstance(body, dict):
        return {}
    if body.get("version") and (body.get("acoustic") or body.get("linguistic")):
        return body
    for k in ("fusion", "metadata", "fusion_metadata", "vector"):
        inner = body.get(k)
        if isinstance(inner, dict) and (inner.get("acoustic") or inner.get("linguistic") or inner.get("transcript")):
            return inner
    # Build a minimal vector from flat turn body
    text = str(body.get("transcript") or body.get("text") or body.get("utterance") or "")
    return {
        "version": "1.0",
        "schema": SCHEMA,
        "session_id": body.get("session_id"),
        "timestamp": int(time.time()),
        "turn_id": body.get("turn_id") or f"t_{int(time.time())}",
        "acoustic": {
            "stress": _clamp01(body.get("stress"), 0.35),
            "speaking_rate": _clamp01(body.get("speaking_rate"), 0.85),
            "energy_mean": _clamp01(body.get("energy"), 0.3),
            "energy_var": 0.1,
            "pause_pattern": body.get("pause_pattern") or "normal",
            "speech_active_ratio": 0.5,
        },
        "linguistic": {
            "transcript": text,
            "is_final": body.get("is_final", True),
            "incomplete": bool(body.get("incomplete")),
            "complete": bool(body.get("complete", True)),
            "reason": body.get("reason") or "flat_input",
            "entity_density": 0.0,
            "entities": body.get("entities") or [],
            "trailing_cues": [],
        },
        "turn": {
            "scenario": body.get("scenario") or "patient",
            "threshold_ms": int(body.get("threshold_ms") or 1400),
            "silence_ms": int(body.get("silence_ms") or 0),
            "decision": body.get("decision") or "end",
            "barge_in_sensitivity": body.get("barge_in") or "medium",
        },
        "domain": {
            "active_expert": body.get("expert") or body.get("active_expert") or "hotel_host",
            "candidate_experts": body.get("candidate_experts") or [],
            "confidence": _clamp01(body.get("confidence"), 0.5),
            "industry": body.get("industry") or "dfw_airline_hospitality",
        },
        "context_buffer": body.get("context_buffer") or body.get("context") or {},
        "session": {
            "history_length": int(body.get("history_length") or 0),
            "dominant_domain": body.get("dominant_domain") or "general",
            "user_state": body.get("user_state") or "active_guest",
        },
    }


def _entity_types(meta: Dict[str, Any]) -> List[str]:
    ling = meta.get("linguistic") or {}
    ents = ling.get("entities") or []
    out: List[str] = []
    for e in ents:
        if isinstance(e, dict) and e.get("type"):
            out.append(str(e["type"]))
        elif isinstance(e, str):
            out.append(e)
    return out


def _text(meta: Dict[str, Any]) -> str:
    ling = meta.get("linguistic") or {}
    return str(ling.get("transcript") or "")


def _expert_scores(meta: Dict[str, Any]) -> Dict[str, float]:
    """Late fusion: parallel lightweight domain heads → confidence weights."""
    scores = {k: 0.05 for k in DFW_EXPERTS}
    text = _text(meta)
    low = text.lower()
    types = set(_entity_types(meta))
    acoustic = meta.get("acoustic") or {}
    domain = meta.get("domain") or {}
    ctx = meta.get("context_buffer") or {}
    session = meta.get("session") or {}

    # Linguistic heads
    if re.search(r"flight|gate|delay|baggage|terminal|boarding|connection|dfw", low):
        scores["airport_guide"] += 1.8
    if re.search(r"hotel|room|check[- ]?in|hold my room|lodging", low):
        scores["hotel_host"] += 1.8
    if re.search(r"shuttle|rideshare|uber|lyft|taxi|transit", low):
        scores["transit_concierge"] += 1.6
    if re.search(r"restaurant|dining|food|hungry|eat", low):
        scores["dining_diplomat"] += 1.5
    if re.search(r"refund|cancel|agent|manager|billing", low):
        scores["support"] += 1.4

    # Entity heads
    for t in types:
        if t in ("flight", "flight_status", "gate", "bag", "airport_code"):
            scores["airport_guide"] += 1.1
        if t in ("room", "hotel", "check_in", "confirmation"):
            scores["hotel_host"] += 1.1
        if t == "shuttle":
            scores["transit_concierge"] += 1.0
        if t == "dining":
            scores["dining_diplomat"] += 1.0
        if t == "need" and "hotel" in low:
            scores["hotel_host"] += 0.6

    # Context buffer occupancy
    for domain_name, expert_id in (
        ("airport", "airport_guide"),
        ("hotel", "hotel_host"),
        ("transit", "transit_concierge"),
        ("dining", "dining_diplomat"),
    ):
        bag = ctx.get(domain_name) or {}
        if isinstance(bag, dict) and bag:
            scores[expert_id] += 0.35 * min(3, len(bag))
        elif isinstance(bag, list) and bag:
            scores[expert_id] += 0.35 * min(3, len(bag))

    # Active expert prior + candidates from voice stack
    active = str(domain.get("active_expert") or "")
    if active in scores:
        scores[active] += 0.45
    for c in domain.get("candidate_experts") or []:
        if c in scores:
            scores[c] += 0.35

    # Acoustic stress → airport/hotel recovery more than dining sales
    stress = _clamp01(acoustic.get("stress"), 0.35)
    if stress >= 0.55:
        scores["airport_guide"] += 0.5
        scores["hotel_host"] += 0.45
        scores["support"] += 0.25

    # Session user state
    ust = str(session.get("user_state") or "")
    if "stress" in ust or "disrupt" in ust:
        scores["airport_guide"] += 0.4
        scores["hotel_host"] += 0.35

    # Multi-domain recovery patterns boost blends
    for pat, experts, _pid in _RECOVERY_PATTERNS:
        if pat.search(text):
            for ex in experts:
                if ex in scores:
                    scores[ex] += 0.55

    return scores


def _normalize_weights(scores: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(0.0, v) for v in scores.values()) or 1.0
    return {k: round(max(0.0, v) / total, 4) for k, v in scores.items()}


def _match_pattern(meta: Dict[str, Any]) -> Optional[str]:
    text = _text(meta)
    for pat, _experts, pid in _RECOVERY_PATTERNS:
        if pat.search(text):
            return pid
    return None


def _patience_delta(meta: Dict[str, Any], primary: str, weights: Dict[str, float]) -> int:
    acoustic = meta.get("acoustic") or {}
    ling = meta.get("linguistic") or {}
    stress = _clamp01(acoustic.get("stress"), 0.35)
    incomplete = bool(ling.get("incomplete"))
    rate = _clamp01(acoustic.get("speaking_rate"), 0.85)
    base = int(round(stress * 400))
    if incomplete:
        base += 350
    if rate < 0.75:
        base += int(round((0.75 - rate) * 300))
    expert = DFW_EXPERTS.get(primary) or {}
    base += int(expert.get("patience_boost_ms") or 0)
    # multi-domain blend needs more patience
    active_n = sum(1 for w in weights.values() if w >= 0.18)
    if active_n >= 2:
        base += 150
    pause = str(acoustic.get("pause_pattern") or "")
    if pause in ("long_thinking", "fragmented"):
        base += 200
    return max(0, min(900, base))


def _preload_context(meta: Dict[str, Any], primary: str, pattern: Optional[str]) -> List[Dict[str, Any]]:
    """Facts Fusion wants the voice buffer to hold for the next turn."""
    puts: List[Dict[str, Any]] = []
    text = _text(meta)
    ling = meta.get("linguistic") or {}
    ents = ling.get("entities") or []
    for e in ents:
        if not isinstance(e, dict):
            continue
        t = str(e.get("type") or "")
        v = e.get("value")
        if t == "flight" and v:
            puts.append({"domain": "airport", "key": "flight", "value": v, "confidence": 0.85})
        elif t == "flight_status" and v:
            puts.append({"domain": "airport", "key": "status", "value": v, "confidence": 0.8})
        elif t == "gate" and v:
            puts.append({"domain": "airport", "key": "gate", "value": v, "confidence": 0.8})
        elif t == "room" and v:
            puts.append({"domain": "hotel", "key": "room", "value": v, "confidence": 0.85})
        elif t == "hotel" and v:
            puts.append({"domain": "hotel", "key": "name", "value": v, "confidence": 0.6})
        elif t == "check_in":
            puts.append({"domain": "hotel", "key": "late_check_in_needed", "value": True, "confidence": 0.7})
        elif t == "shuttle":
            puts.append({"domain": "transit", "key": "mode", "value": v, "confidence": 0.65})

    if pattern == "flight_disruption_recovery":
        puts.append(
            {
                "domain": "airport",
                "key": "disruption",
                "value": "delay_or_missed",
                "confidence": 0.75,
            }
        )
        puts.append(
            {
                "domain": "hotel",
                "key": "recovery_mode",
                "value": "hold_room_late_arrival",
                "confidence": 0.7,
            }
        )
    if pattern == "hotel_recovery":
        puts.append(
            {
                "domain": "hotel",
                "key": "intent",
                "value": "late_hold_or_checkin",
                "confidence": 0.75,
            }
        )
    if primary == "dining_diplomat" or re.search(r"hungry|restaurant|dining", text, re.I):
        puts.append(
            {
                "domain": "dining",
                "key": "intent",
                "value": "recommend_near_stay_or_terminal",
                "confidence": 0.65,
            }
        )

    # Dedup by domain+key
    seen = set()
    out: List[Dict[str, Any]] = []
    for p in puts:
        k = f"{p.get('domain')}:{p.get('key')}"
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out[:12]


def _prompt_boost(
    primary: str,
    weights: Dict[str, float],
    pattern: Optional[str],
    meta: Dict[str, Any],
) -> str:
    session = meta.get("session") or {}
    user_state = session.get("user_state") or "active_guest"
    blend = [f"{k}={weights[k]:.2f}" for k in sorted(weights, key=lambda x: -weights[x]) if weights[k] >= 0.12][:4]
    lines = [
        f"Conversational Fusion ({FUSION_SCHEMA}): primary={primary}; blend={', '.join(blend) or primary}.",
        f"User state: {user_state}. Industry: DFW airline + hospitality graph.",
    ]
    if pattern:
        lines.append(f"Recovery pattern: {pattern} — keep cross-domain facts; do not force re-explain.")
    if weights.get("airport_guide", 0) >= 0.18 and weights.get("hotel_host", 0) >= 0.18:
        lines.append(
            "Multi-domain: cover flight status AND hotel late hold in one coherent reply; "
            "offer shuttle/dining only if relevant."
        )
    expert = DFW_EXPERTS.get(primary) or {}
    priors = expert.get("priors") or []
    if priors:
        lines.append("Prior: " + priors[0])
    acoustic = meta.get("acoustic") or {}
    if _clamp01(acoustic.get("stress")) >= 0.55:
        lines.append("Tone: calm, short sentences, extra patience; acknowledge disruption first.")
    return " ".join(lines)


def fuse(body: Dict[str, Any] | None = None, **kwargs: Any) -> Dict[str, Any]:
    """Deep Fusion over conversational metadata → routing + patience + preload."""
    raw = dict(body or {})
    raw.update(kwargs)
    meta = _as_meta(raw)
    scores = _expert_scores(meta)
    weights = _normalize_weights(scores)
    primary = max(weights, key=lambda k: weights[k])
    # Soft protect: if voice active expert is close, keep continuity
    domain = meta.get("domain") or {}
    active = str(domain.get("active_expert") or "")
    if active in weights and weights[active] >= weights[primary] * 0.85:
        primary = active
    pattern = _match_pattern(meta)
    patience = _patience_delta(meta, primary, weights)
    preload = _preload_context(meta, primary, pattern)
    stress = _clamp01((meta.get("acoustic") or {}).get("stress"), 0.35)
    # Slight stress up if incomplete (user still mid-thought)
    if (meta.get("linguistic") or {}).get("incomplete"):
        stress = min(1.0, stress + 0.08)

    expert_info = DFW_EXPERTS.get(primary) or DFW_EXPERTS["hotel_host"]
    scenario = str((meta.get("turn") or {}).get("scenario") or "patient")
    if patience >= 400 or stress >= 0.55:
        scenario = "patient"
    if patience >= 700:
        scenario = "dictation" if (meta.get("linguistic") or {}).get("entity_density", 0) > 0.5 else "patient"

    listening = {
        "scenario": scenario,
        "stress": round(min(1.0, stress + patience / 2000.0), 3),
        "expert": primary,
        "barge_in": "low" if stress >= 0.6 or patience >= 500 else str((meta.get("turn") or {}).get("barge_in_sensitivity") or "medium"),
        "threshold_ms": int((meta.get("turn") or {}).get("threshold_ms") or 1400) + patience,
        "patience_delta_ms": patience,
    }

    secondary = [k for k, w in sorted(weights.items(), key=lambda kv: -kv[1]) if k != primary and w >= 0.15][:3]
    fusion_apply = {
        "stress": listening["stress"],
        "expert": primary,
        "scenario": scenario,
        "barge_in": listening["barge_in"],
        "personality": expert_info.get("personality") or "aria",
        "context_puts": [{"domain": p["domain"], "key": p["key"], "value": p["value"]} for p in preload],
    }

    return {
        "ok": True,
        "schema": FUSION_SCHEMA,
        "version": VERSION,
        "industry": "dfw_airline_hospitality",
        "input_schema": meta.get("schema") or SCHEMA,
        "session_id": meta.get("session_id"),
        "turn_id": meta.get("turn_id"),
        "primary_expert": primary,
        "secondary_experts": secondary,
        "expert_weights": weights,
        "expert_scores": {k: round(v, 3) for k, v in scores.items()},
        "pattern": pattern,
        "patience_delta_ms": patience,
        "listening": listening,
        "fusion_apply": fusion_apply,
        "preload_context": preload,
        "prompt_boost": _prompt_boost(primary, weights, pattern, meta),
        "user_state": (meta.get("session") or {}).get("user_state"),
        "mode": "early+late_fusion",
        "ts": time.time(),
    }


def fuse_and_pack_for_voice(body: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Fuse + return only fields safe to POST back into voice /v1/listening + context."""
    out = fuse(body)
    return {
        "ok": True,
        "fusion": out,
        "listening": out.get("listening"),
        "fusion_apply": out.get("fusion_apply"),
        "prompt_boost": out.get("prompt_boost"),
    }


# In-memory last fusion per session (desk / work mode can poll)
_LAST: Dict[str, Dict[str, Any]] = {}


def remember(session_id: str, result: Dict[str, Any]) -> None:
    if not session_id:
        return
    _LAST[str(session_id)] = result
    if len(_LAST) > 64:
        # drop oldest keys arbitrarily
        for k in list(_LAST.keys())[:16]:
            _LAST.pop(k, None)


def last(session_id: str) -> Optional[Dict[str, Any]]:
    return _LAST.get(str(session_id)) if session_id else None
