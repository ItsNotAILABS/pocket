"""POCKET Economic Domain — wallets, digital twin wallets, clearing, escrow.

Parallax-inspired posture (paper/testnet-first):
  · Operator wallet meters host POCK credits
  · Seat wallets per user
  · Digital twin wallets per agent (Aria, Codex, …) for twin economics
  · Escrow for multi-agent / RAH runs
  · Clearing receipts (settlement journal, not live chain until bridged)
  · Bridge hooks toward Parallax Exchange / future rails

Doctrine: local-first ledger, receipts for audit, no live money movement
unless a bridge is explicitly configured. Same pattern as Parallax paper mode.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket"
ECON_DIR = ROOT / "economy"
STATE_FILE = ECON_DIR / "economy_state.json"
_lock = Lock()

UNIT = "POCK"
SCHEMA = "pocket.economy.v2"
DOMAIN = "economic"

# Major economic protocols (POCKET + Parallax-shaped)
ECONOMIC_PROTOCOLS: List[Dict[str, Any]] = [
    {
        "id": "MEDINA-POCK-LEDGER/1.0",
        "slug": "pock-ledger",
        "name": "POCK Host Ledger",
        "summary": "Host-level credit mint/burn for sessions, jobs, deploys, RAH.",
        "rails": ["host", "paper"],
    },
    {
        "id": "MEDINA-WALLET/1.0",
        "slug": "wallet",
        "name": "Operator & Seat Wallets",
        "summary": "Named wallets for operator host and user seats (ACCESS seats).",
        "rails": ["host", "seat"],
    },
    {
        "id": "MEDINA-TWIN-WALLET/1.0",
        "slug": "twin-wallet",
        "name": "Digital Twin Wallets",
        "summary": "Per-agent twin balances — Aria, Codex, Claude, mesh heads meter work.",
        "rails": ["twin", "agent"],
    },
    {
        "id": "MEDINA-ESCROW/1.0",
        "slug": "escrow",
        "name": "Multi-Agent Escrow",
        "summary": "Lock POCK for RAH / swarm / dual runs; release or slash on verify.",
        "rails": ["escrow", "rah"],
    },
    {
        "id": "MEDINA-CLEARING/1.0",
        "slug": "clearing",
        "name": "Clearing & Receipts",
        "summary": "Journal of settlements with receipt hashes (Parallax-style paper trail).",
        "rails": ["clearing", "paper"],
    },
    {
        "id": "MEDINA-SETTLEMENT/1.0",
        "slug": "settlement",
        "name": "Settlement Rails",
        "summary": "paper | testnet | live — default paper; live requires bridge config.",
        "rails": ["paper", "testnet", "live"],
    },
    {
        "id": "MEDINA-PARALLAX-BRIDGE/1.0",
        "slug": "parallax-bridge",
        "name": "Parallax Bridge Hook",
        "summary": "Optional link to Parallax Exchange/Clearinghouse workspace (no live funds by default).",
        "rails": ["parallax", "bridge"],
    },
    {
        "id": "MEDINA-FEE-SCHEDULE/1.0",
        "slug": "fee-schedule",
        "name": "Agent Fee Schedule",
        "summary": "POCK price table for modes, API agents, RAH leaves, twin pulses.",
        "rails": ["pricing"],
    },
    {
        "id": "MEDINA-REVENUECAT/1.0",
        "slug": "revenuecat",
        "name": "RevenueCat Billing",
        "summary": "Paid entitlements via RevenueCat. Webhooks mint POCK; never auto-pay.",
        "rails": ["billing", "subscription", "pock"],
    },
]

# Twin agents that get wallets by default
DEFAULT_TWINS = [
    ("operator", "Operator", "host"),
    ("aria", "Aria · Voice", "voice"),
    ("codex", "Codex", "code"),
    ("claude", "Claude", "code"),
    ("grok", "Grok", "code"),
    ("archon", "ARCHON", "mesh"),
    ("plan", "Planner", "plan"),
    ("rah", "RAH Orchestrator", "harness"),
    ("assist", "Digital Assist", "life"),
    ("novae", "Novae", "research"),
]


def _default_state() -> Dict[str, Any]:
    wallets: Dict[str, Any] = {}
    # Host operator wallet mirrors tokenomics grant seed
    wallets["wallet_operator"] = {
        "id": "wallet_operator",
        "kind": "operator",
        "label": "Host operator",
        "owner": "pocket",
        "balance": 10_000,
        "currency": UNIT,
        "rail": "paper",
        "created_at": time.time(),
    }
    twins: Dict[str, Any] = {}
    for tid, label, role in DEFAULT_TWINS:
        if tid == "operator":
            continue
        twins[f"twin_{tid}"] = {
            "id": f"twin_{tid}",
            "agent_id": tid,
            "label": label,
            "role": role,
            "kind": "digital_twin",
            "balance": 500,
            "lifetime_earned": 0,
            "lifetime_spent": 0,
            "currency": UNIT,
            "rail": "paper",
            "created_at": time.time(),
        }
    return {
        "schema": SCHEMA,
        "domain": DOMAIN,
        "unit": UNIT,
        "settlement_rail": "paper",  # paper | testnet | live
        "parallax": {
            "bridge_enabled": False,
            "workspace": r"E:\PARALLAX-Exchange-Clearinghouse",
            "mode": "paper",
            "note": "No live settlement until bridge_enabled + explicit live rail",
        },
        "wallets": wallets,
        "twins": twins,
        "escrows": {},
        "receipts": [],
        "transfers": [],
        "created_at": time.time(),
        "updated_at": time.time(),
    }


def _load() -> Dict[str, Any]:
    ECON_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            st = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            # ensure twins exist
            base = _default_state()
            for k, v in (base.get("twins") or {}).items():
                st.setdefault("twins", {}).setdefault(k, v)
            st.setdefault("wallets", base["wallets"])
            st.setdefault("escrows", {})
            st.setdefault("receipts", [])
            st.setdefault("transfers", [])
            st.setdefault("parallax", base["parallax"])
            return st
        except Exception:
            pass
    st = _default_state()
    _save(st)
    return st


def _save(st: Dict[str, Any]) -> None:
    st["updated_at"] = time.time()
    # cap journals
    for key, n in (("receipts", 300), ("transfers", 300)):
        arr = st.get(key) or []
        if len(arr) > n:
            st[key] = arr[-n:]
    STATE_FILE.write_text(json.dumps(st, indent=2, default=str), encoding="utf-8")


def _receipt(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    body = json.dumps(payload, sort_keys=True, default=str)
    h = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "id": f"rcpt-{uuid.uuid4().hex[:12]}",
        "kind": kind,
        "hash": h[:32],
        "sha256": h,
        "at": time.time(),
        "rail": payload.get("rail") or "paper",
        "payload": payload,
    }


def protocols() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": "pocket.economy.protocols.v1",
        "domain": DOMAIN,
        "count": len(ECONOMIC_PROTOCOLS),
        "protocols": list(ECONOMIC_PROTOCOLS),
        "settlement_rails": ["paper", "testnet", "live"],
        "default_rail": "paper",
        "parallax_bridge": True,
    }


def snapshot() -> Dict[str, Any]:
    """Full economy view for desk UI + agents."""
    with _lock:
        st = _load()
        # Sync operator wallet with tokenomics when available
        try:
            from pocket.tokenomics import snapshot as tok_snap

            ts = tok_snap()
            op = st["wallets"].get("wallet_operator") or {}
            op["balance"] = int(ts.get("balance") or op.get("balance") or 0)
            op["tokenomics_lifetime_burned"] = ts.get("lifetime_burned")
            op["tokenomics_lifetime_minted"] = ts.get("lifetime_minted")
            st["wallets"]["wallet_operator"] = op
            _save(st)
        except Exception:
            pass

        wallets = list((st.get("wallets") or {}).values())
        twins = list((st.get("twins") or {}).values())
        escrows = list((st.get("escrows") or {}).values())
        open_escrow = [e for e in escrows if e.get("status") == "open"]
        twin_total = sum(int(t.get("balance") or 0) for t in twins)
        return {
            "ok": True,
            "schema": SCHEMA,
            "domain": DOMAIN,
            "unit": UNIT,
            "settlement_rail": st.get("settlement_rail") or "paper",
            "operator": (st.get("wallets") or {}).get("wallet_operator"),
            "wallets": wallets,
            "twins": sorted(twins, key=lambda t: -int(t.get("balance") or 0)),
            "twin_total": twin_total,
            "escrows_open": open_escrow,
            "escrow_locked": sum(int(e.get("amount") or 0) for e in open_escrow),
            "receipts_recent": list(reversed((st.get("receipts") or [])[-8:])),
            "transfers_recent": list(reversed((st.get("transfers") or [])[-8:])),
            "parallax": st.get("parallax") or {},
            "protocols": ECONOMIC_PROTOCOLS,
            "ui": {
                "title": "Economy",
                "subtitle": "Wallets · digital twins · clearing · paper-first",
            },
        }


def list_wallets() -> Dict[str, Any]:
    s = snapshot()
    return {
        "ok": True,
        "wallets": s.get("wallets"),
        "operator": s.get("operator"),
        "unit": UNIT,
    }


def list_twins() -> Dict[str, Any]:
    s = snapshot()
    return {
        "ok": True,
        "twins": s.get("twins"),
        "twin_total": s.get("twin_total"),
        "unit": UNIT,
        "note": "Digital twin wallets meter agent work; paper rail by default",
    }


def ensure_twin(agent_id: str, *, label: str = "") -> Dict[str, Any]:
    aid = (agent_id or "agent").strip().lower().replace(" ", "_")[:40]
    wid = f"twin_{aid}"
    with _lock:
        st = _load()
        twins = st.setdefault("twins", {})
        if wid not in twins:
            twins[wid] = {
                "id": wid,
                "agent_id": aid,
                "label": label or aid,
                "role": "agent",
                "kind": "digital_twin",
                "balance": 250,
                "lifetime_earned": 0,
                "lifetime_spent": 0,
                "currency": UNIT,
                "rail": st.get("settlement_rail") or "paper",
                "created_at": time.time(),
            }
            _save(st)
        return {"ok": True, "twin": twins[wid]}


def ensure_seat_wallet(user: str) -> Dict[str, Any]:
    user = (user or "seat").strip().lower()[:40]
    wid = f"wallet_seat_{user}"
    with _lock:
        st = _load()
        w = st.setdefault("wallets", {})
        if wid not in w:
            w[wid] = {
                "id": wid,
                "kind": "seat",
                "label": f"Seat · {user}",
                "owner": user,
                "balance": 1_000,
                "currency": UNIT,
                "rail": st.get("settlement_rail") or "paper",
                "created_at": time.time(),
            }
            _save(st)
        return {"ok": True, "wallet": w[wid]}


def transfer(
    *,
    from_id: str,
    to_id: str,
    amount: int,
    memo: str = "",
    rail: Optional[str] = None,
) -> Dict[str, Any]:
    amount = max(0, int(amount))
    if amount <= 0:
        return {"ok": False, "error": "amount must be > 0"}
    with _lock:
        st = _load()
        rail = rail or st.get("settlement_rail") or "paper"
        if rail == "live" and not (st.get("parallax") or {}).get("bridge_enabled"):
            return {
                "ok": False,
                "error": "live rail blocked — enable parallax bridge or use paper/testnet",
                "rail": rail,
            }

        def _get(cid: str) -> Optional[Dict[str, Any]]:
            if cid in (st.get("wallets") or {}):
                return st["wallets"][cid]
            if cid in (st.get("twins") or {}):
                return st["twins"][cid]
            # short twin id
            if f"twin_{cid}" in (st.get("twins") or {}):
                return st["twins"][f"twin_{cid}"]
            if cid == "operator":
                return st["wallets"].get("wallet_operator")
            return None

        src = _get(from_id)
        dst = _get(to_id)
        if not src or not dst:
            return {"ok": False, "error": "unknown wallet/twin id", "from": from_id, "to": to_id}
        src["balance"] = int(src.get("balance") or 0) - amount
        dst["balance"] = int(dst.get("balance") or 0) + amount
        if src.get("kind") == "digital_twin":
            src["lifetime_spent"] = int(src.get("lifetime_spent") or 0) + amount
        if dst.get("kind") == "digital_twin":
            dst["lifetime_earned"] = int(dst.get("lifetime_earned") or 0) + amount

        tx = {
            "id": f"tx-{uuid.uuid4().hex[:12]}",
            "from": src.get("id"),
            "to": dst.get("id"),
            "amount": amount,
            "unit": UNIT,
            "memo": (memo or "")[:200],
            "rail": rail,
            "at": time.time(),
        }
        st.setdefault("transfers", []).append(tx)
        rcpt = _receipt("transfer", tx)
        st.setdefault("receipts", []).append(rcpt)
        # Mirror host operator burns into tokenomics when burning from operator
        if src.get("id") == "wallet_operator":
            try:
                from pocket.tokenomics import burn

                burn("economy_transfer", meta={"to": dst.get("id"), "tx": tx["id"]}, amount=amount)
            except Exception:
                pass
        _save(st)
        return {"ok": True, "transfer": tx, "receipt": rcpt}


def twin_pulse(agent_id: str, *, amount: int = 5, reason: str = "job") -> Dict[str, Any]:
    """Spend twin wallet for agent work (digital twin metering)."""
    ensure_twin(agent_id)
    amount = max(1, int(amount))
    with _lock:
        st = _load()
        tid = f"twin_{(agent_id or 'agent').lower()}"
        twin = (st.get("twins") or {}).get(tid)
        if not twin:
            return {"ok": False, "error": "twin missing"}
        twin["balance"] = int(twin.get("balance") or 0) - amount
        twin["lifetime_spent"] = int(twin.get("lifetime_spent") or 0) + amount
        # fund from operator paper allocation
        op = st["wallets"].get("wallet_operator")
        if op:
            # accounting only — twin spent is host cost
            pass
        ev = {
            "id": f"pulse-{uuid.uuid4().hex[:10]}",
            "twin": tid,
            "amount": amount,
            "reason": reason,
            "balance_after": twin["balance"],
            "at": time.time(),
        }
        rcpt = _receipt("twin_pulse", ev)
        st.setdefault("receipts", []).append(rcpt)
        _save(st)
        return {"ok": True, "pulse": ev, "receipt": rcpt, "twin": twin}


def escrow_open(
    *,
    amount: int,
    purpose: str = "multi-agent",
    holder: str = "wallet_operator",
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    amount = max(0, int(amount))
    with _lock:
        st = _load()
        src = (st.get("wallets") or {}).get(holder) or (st.get("twins") or {}).get(holder)
        if not src:
            return {"ok": False, "error": "holder not found"}
        src["balance"] = int(src.get("balance") or 0) - amount
        eid = f"esc-{uuid.uuid4().hex[:12]}"
        esc = {
            "id": eid,
            "amount": amount,
            "purpose": purpose[:120],
            "holder": src.get("id"),
            "status": "open",
            "meta": meta or {},
            "rail": st.get("settlement_rail") or "paper",
            "created_at": time.time(),
        }
        st.setdefault("escrows", {})[eid] = esc
        rcpt = _receipt("escrow_open", esc)
        st.setdefault("receipts", []).append(rcpt)
        _save(st)
        return {"ok": True, "escrow": esc, "receipt": rcpt}


def escrow_close(escrow_id: str, *, release_to: str = "wallet_operator", slash: bool = False) -> Dict[str, Any]:
    with _lock:
        st = _load()
        esc = (st.get("escrows") or {}).get(escrow_id)
        if not esc:
            return {"ok": False, "error": "escrow not found"}
        if esc.get("status") != "open":
            return {"ok": False, "error": "escrow not open"}
        amt = int(esc.get("amount") or 0)
        if not slash:
            dst = (st.get("wallets") or {}).get(release_to) or (st.get("twins") or {}).get(release_to)
            if dst:
                dst["balance"] = int(dst.get("balance") or 0) + amt
        esc["status"] = "slashed" if slash else "released"
        esc["closed_at"] = time.time()
        esc["release_to"] = release_to if not slash else None
        rcpt = _receipt("escrow_close", esc)
        st.setdefault("receipts", []).append(rcpt)
        _save(st)
        return {"ok": True, "escrow": esc, "receipt": rcpt}


def set_rail(rail: str) -> Dict[str, Any]:
    rail = (rail or "paper").strip().lower()
    if rail not in ("paper", "testnet", "live"):
        return {"ok": False, "error": "rail must be paper|testnet|live"}
    with _lock:
        st = _load()
        if rail == "live" and not (st.get("parallax") or {}).get("bridge_enabled"):
            return {
                "ok": False,
                "error": "enable parallax bridge before live rail",
                "hint": "POST /v1/economy/parallax {enabled:true} after configuring workspace",
            }
        st["settlement_rail"] = rail
        _save(st)
        return {"ok": True, "settlement_rail": rail}


def parallax_config(
    *,
    enabled: Optional[bool] = None,
    workspace: Optional[str] = None,
    mode: Optional[str] = None,
) -> Dict[str, Any]:
    with _lock:
        st = _load()
        p = st.setdefault(
            "parallax",
            {
                "bridge_enabled": False,
                "workspace": r"E:\PARALLAX-Exchange-Clearinghouse",
                "mode": "paper",
            },
        )
        if enabled is not None:
            p["bridge_enabled"] = bool(enabled)
        if workspace:
            p["workspace"] = str(workspace)[:500]
        if mode in ("paper", "testnet", "live"):
            p["mode"] = mode
        p["workspace_exists"] = Path(p.get("workspace") or "").exists()
        _save(st)
        return {"ok": True, "parallax": p, "settlement_rail": st.get("settlement_rail")}


def mint_to_wallet(wallet_id: str, amount: int, *, reason: str = "grant") -> Dict[str, Any]:
    amount = max(0, int(amount))
    with _lock:
        st = _load()
        w = (st.get("wallets") or {}).get(wallet_id) or (st.get("twins") or {}).get(wallet_id)
        if not w:
            return {"ok": False, "error": "wallet not found"}
        w["balance"] = int(w.get("balance") or 0) + amount
        if w.get("kind") == "digital_twin":
            w["lifetime_earned"] = int(w.get("lifetime_earned") or 0) + amount
        if wallet_id == "wallet_operator":
            try:
                from pocket.tokenomics import mint

                mint(amount, reason=reason)
            except Exception:
                pass
        tx = {
            "id": f"mint-{uuid.uuid4().hex[:10]}",
            "to": wallet_id,
            "amount": amount,
            "reason": reason,
            "at": time.time(),
        }
        rcpt = _receipt("mint", tx)
        st.setdefault("receipts", []).append(rcpt)
        _save(st)
        return {"ok": True, "mint": tx, "receipt": rcpt, "wallet": w}


def fee_schedule() -> Dict[str, Any]:
    try:
        from pocket.tokenomics import COSTS, USD_HINTS, UNIT as U
    except Exception:
        COSTS, USD_HINTS, U = {}, {}, UNIT
    return {
        "ok": True,
        "unit": U,
        "costs": COSTS,
        "usd_hints": USD_HINTS,
        "rah_leaf_hint": 8,
        "twin_pulse_default": 5,
        "escrow_rah_default": 40,
        "note": "Paper economics — live Parallax bridge optional",
    }


def domain_status() -> Dict[str, Any]:
    s = snapshot()
    return {
        "ok": True,
        "domain": DOMAIN,
        "schema": SCHEMA,
        "settlement_rail": s.get("settlement_rail"),
        "operator_balance": (s.get("operator") or {}).get("balance"),
        "twins": len(s.get("twins") or []),
        "twin_total": s.get("twin_total"),
        "escrow_locked": s.get("escrow_locked"),
        "protocols": len(ECONOMIC_PROTOCOLS),
        "parallax": s.get("parallax"),
        "healthy": True,
    }


def brief(*, max_chars: int = 700) -> str:
    s = snapshot()
    op = (s.get("operator") or {}).get("balance")
    lines = [
        "POCKET economic domain (paper-first, Parallax-shaped):",
        f"· Operator wallet: {op} {UNIT} · rail={s.get('settlement_rail')}",
        f"· Digital twin wallets: {len(s.get('twins') or [])} agents · pool {s.get('twin_total')} {UNIT}",
        f"· Escrow locked: {s.get('escrow_locked')} · protocols: pock-ledger, wallet, twin-wallet, escrow, clearing, settlement, parallax-bridge, fee-schedule",
        "· APIs: GET /v1/economy · /v1/economy/twins · POST /v1/economy/transfer · /v1/economy/escrow",
        "· Live chain settlement requires parallax bridge enable — default is paper receipts only",
        "· Parallax AI wallets: export twins as @parallax/ai-wallet contracts (paper/testnet)",
    ]
    return "\n".join(lines)[:max_chars]


# ---------------------------------------------------------------------------
# Parallax AI Wallet bridge (@parallax/ai-wallet contract shape)
# ---------------------------------------------------------------------------

def _iso(ts: Optional[float] = None) -> str:
    import datetime as _dt

    t = ts if ts is not None else time.time()
    return _dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _default_ai_policy(mode: str = "paper") -> Dict[str, Any]:
    """Mirror Parallax AiWalletPolicy — live blocked until bridge + human gates."""
    return {
        "policyId": "pocket-twin-policy-v1",
        "version": "1.0.0",
        "allowedModes": ["paper", "testnet"] if mode != "live" else ["paper", "testnet", "live"],
        "allowedCommandKinds": [
            "transfer",
            "research_mint",
            "operator_note",
            "approve_signal",
        ],
        "allowedAssets": [UNIT, "POCK", "USD_PAPER"],
        "allowedCounterparties": ["wallet_operator", "escrow", "twin_*"],
        "maxCommandNotional": 5000,
        "dailyNotionalLimit": 25000,
        "requireHumanApprovalAbove": 1000,
        "requireHumanApprovalFor": ["order"],
        "scopes": [
            {
                "id": "desk-work",
                "description": "POCKET desk job metering and internal transfers",
                "allowedCommandKinds": ["transfer", "research_mint", "operator_note"],
                "allowedAssets": [UNIT, "POCK"],
                "maxCommandNotional": 2000,
                "dailyNotionalLimit": 10000,
                "requireHumanApprovalAbove": 500,
            }
        ],
        "liveModeBlocked": mode != "live",
    }


def twin_as_parallax_ai_wallet(twin: Dict[str, Any], *, mode: str = "paper") -> Dict[str, Any]:
    """Export a POCKET digital twin as Parallax AiWallet JSON."""
    aid = twin.get("agent_id") or "agent"
    now = _iso()
    bal = int(twin.get("balance") or 0)
    return {
        "id": twin.get("id") or f"aiw_{aid}",
        "agentId": aid,
        "displayName": twin.get("label") or aid,
        "ownerPrincipal": "pocket-host-operator",
        "controllerPrincipal": "pocket-economy-controller",
        "status": "active",
        "mode": mode if mode in ("paper", "testnet", "live") else "paper",
        "policy": _default_ai_policy(mode),
        "balances": [
            {
                "asset": UNIT,
                "available": max(0, bal),
                "locked": 0,
                "mode": mode,
                "updatedAt": now,
            }
        ],
        "createdAt": _iso(float(twin.get("created_at") or time.time())),
        "updatedAt": now,
        "metadata": {
            "source": "POCKET",
            "kind": "digital_twin",
            "role": str(twin.get("role") or "agent"),
            "schema": SCHEMA,
            "parallax_package": "@parallax/ai-wallet",
        },
    }


def export_parallax_ai_wallets() -> Dict[str, Any]:
    """Snapshot all twin wallets as Parallax AI wallet contracts + receipt chain head."""
    with _lock:
        st = _load()
        mode = (st.get("settlement_rail") or "paper")
        if mode == "live" and not (st.get("parallax") or {}).get("bridge_enabled"):
            mode = "paper"
        wallets = [
            twin_as_parallax_ai_wallet(t, mode=mode)
            for t in (st.get("twins") or {}).values()
        ]
        chain = []
        prev = None
        for w in wallets:
            rid = f"AI_WALLET_CREATED:{w['id']}:{w['createdAt']}"
            payload = {"wallet": w["id"], "agentId": w["agentId"], "prev": prev}
            h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            rec = {
                "receiptId": rid,
                "kind": "AI_WALLET_CREATED",
                "walletId": w["id"],
                "agentId": w["agentId"],
                "actor": "pocket-host-operator",
                "mode": mode,
                "reasonCodes": ["VALID"],
                "payloadHash": h[:32],
                "previousReceiptId": prev,
                "createdAt": w["createdAt"],
            }
            chain.append(rec)
            prev = rid
        # verify chain linkage
        ok_chain = True
        for i in range(1, len(chain)):
            if chain[i].get("previousReceiptId") != chain[i - 1].get("receiptId"):
                ok_chain = False
                break
        return {
            "ok": True,
            "schema": "parallax.ai_wallet.export.v1",
            "package": "@parallax/ai-wallet",
            "mode": mode,
            "count": len(wallets),
            "wallets": wallets,
            "receipts": chain,
            "receipt_chain_valid": ok_chain,
            "workspace": (st.get("parallax") or {}).get("workspace"),
            "bridge_enabled": bool((st.get("parallax") or {}).get("bridge_enabled")),
            "note": "Paper/testnet alpha — live blocked until custody gates (Parallax AI_WALLET_ALPHA)",
        }


def sync_parallax_bridge(*, write_export: bool = True) -> Dict[str, Any]:
    """Probe Parallax workspace + optionally write AI wallet export for the bridge."""
    with _lock:
        st = _load()
        p = st.setdefault("parallax", {})
        ws = Path(p.get("workspace") or r"E:\PARALLAX-Exchange-Clearinghouse")
        p["workspace"] = str(ws)
        p["workspace_exists"] = ws.exists()
        ai_wallet_pkg = ws / "src" / "ai-wallet"
        p["ai_wallet_package"] = str(ai_wallet_pkg)
        p["ai_wallet_package_exists"] = ai_wallet_pkg.is_dir()
        docs = ws / "docs" / "AI_WALLET_ALPHA.md"
        p["ai_wallet_docs"] = str(docs) if docs.is_file() else None
        _save(st)

    export = export_parallax_ai_wallets()
    written = None
    if write_export and ws.exists():
        out_dir = ECON_DIR / "parallax_export"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "ai_wallets.json"
        out_path.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
        # Mirror into Parallax EXTERNAL if present
        try:
            ext = ws / "EXTERNAL" / "pocket"
            ext.mkdir(parents=True, exist_ok=True)
            mirror = ext / "pocket_ai_wallets.json"
            mirror.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
            written = {"local": str(out_path), "parallax_mirror": str(mirror)}
        except Exception as e:
            written = {"local": str(out_path), "mirror_error": str(e)[:120]}
    return {
        "ok": True,
        "parallax": st.get("parallax") if "st" in dir() else parallax_config().get("parallax"),
        "export_count": export.get("count"),
        "receipt_chain_valid": export.get("receipt_chain_valid"),
        "written": written,
        "mode": export.get("mode"),
    }


def evaluate_command(
    *,
    agent_id: str,
    kind: str = "transfer",
    amount: float = 0,
    asset: str = UNIT,
    mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Policy gate aligned with Parallax AiWalletPolicy (paper/testnet first)."""
    ensure_twin(agent_id)
    with _lock:
        st = _load()
        rail = mode or st.get("settlement_rail") or "paper"
        twin = (st.get("twins") or {}).get(f"twin_{agent_id.lower()}") or {}
        policy = _default_ai_policy(rail)
        reasons: List[str] = []
        decision = "approved"
        if rail == "live" and policy.get("liveModeBlocked", True):
            decision = "rejected"
            reasons.append("LIVE_MODE_BLOCKED")
        if kind not in (policy.get("allowedCommandKinds") or []):
            decision = "rejected"
            reasons.append("COMMAND_KIND_NOT_ALLOWED")
        if asset not in (policy.get("allowedAssets") or []):
            decision = "rejected"
            reasons.append("ASSET_NOT_ALLOWED")
        if float(amount) > float(policy.get("maxCommandNotional") or 0):
            decision = "rejected"
            reasons.append("NOTIONAL_LIMIT_EXCEEDED")
        if float(amount) > float(policy.get("requireHumanApprovalAbove") or 0) and decision == "approved":
            decision = "requires_human_approval"
            reasons.append("HUMAN_APPROVAL_REQUIRED")
        if decision == "approved":
            reasons.append("VALID")
        return {
            "ok": True,
            "decision": decision,
            "reasonCodes": reasons,
            "agentId": agent_id,
            "kind": kind,
            "amount": amount,
            "asset": asset,
            "mode": rail,
            "twin_balance": twin.get("balance"),
            "policyId": policy.get("policyId"),
            "evaluatedAt": _iso(),
            "package": "@parallax/ai-wallet",
        }
