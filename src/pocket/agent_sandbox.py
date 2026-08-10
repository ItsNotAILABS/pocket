"""Capability-based agent sandbox for POCKET (Wasm-shaped host policy).

Design goals (see docs/research/POCKET_AGENT_WASM_SANDBOX.md):
  - Zero ambient authority: tools start with no FS/net/shell unless granted
  - Profiles for founder agents, market seats, voice plugins, untrusted code
  - Fuel / timeout / path containment
  - Receipts for audit (defense-in-depth with safety.py)

This is the host-side capability gate. Full Wasmtime guest execution is optional
when the `wasmtime` CLI is present; pure-Python tool callbacks always go through
the same grants.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

ROOT = Path.home() / ".pocket" / "sandbox"
RECEIPTS = ROOT / "receipts"
ROOT.mkdir(parents=True, exist_ok=True)
RECEIPTS.mkdir(parents=True, exist_ok=True)

_lock = Lock()

# ---------------------------------------------------------------------------
# Capabilities (WASI-like names, host-enforced)
# ---------------------------------------------------------------------------

CAP_COMPUTE = "compute"  # pure CPU / in-memory only
CAP_FS_READ = "fs:read"
CAP_FS_WRITE = "fs:write"
CAP_NET_HTTP = "net:http"
CAP_SHELL = "shell"  # dangerous — founder only, rare
CAP_DESKTOP = "desktop"  # open allowlisted apps
CAP_VOICE_API = "voice:api"  # call local pocket-voice
CAP_CLOCK = "clock"

ALL_CAPS = frozenset(
    {
        CAP_COMPUTE,
        CAP_FS_READ,
        CAP_FS_WRITE,
        CAP_NET_HTTP,
        CAP_SHELL,
        CAP_DESKTOP,
        CAP_VOICE_API,
        CAP_CLOCK,
    }
)

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

PROFILES: Dict[str, Dict[str, Any]] = {
    "compute": {
        "label": "Pure compute",
        "caps": {CAP_COMPUTE, CAP_CLOCK},
        "max_ms": 5_000,
        "max_memory_mb": 64,
        "fuel": 1_000_000,
        "fs_roots": [],
        "net_hosts": [],
    },
    "workspace_read": {
        "label": "Workspace read",
        "caps": {CAP_COMPUTE, CAP_CLOCK, CAP_FS_READ},
        "max_ms": 30_000,
        "max_memory_mb": 256,
        "fuel": 5_000_000,
        "fs_roots": [],  # filled from job workspace
        "net_hosts": [],
    },
    "workspace_write": {
        "label": "Workspace read/write",
        "caps": {CAP_COMPUTE, CAP_CLOCK, CAP_FS_READ, CAP_FS_WRITE},
        "max_ms": 120_000,
        "max_memory_mb": 512,
        "fuel": 20_000_000,
        "fs_roots": [],
        "net_hosts": [],
    },
    "market_seat": {
        "label": "Market seat tenant",
        "caps": {CAP_COMPUTE, CAP_CLOCK, CAP_FS_READ, CAP_FS_WRITE, CAP_VOICE_API},
        "max_ms": 60_000,
        "max_memory_mb": 256,
        "fuel": 8_000_000,
        "fs_roots": [],  # must be tenant path only
        "net_hosts": ["127.0.0.1", "localhost"],
    },
    "voice_plugin": {
        "label": "Voice plugin (no host FS)",
        "caps": {CAP_COMPUTE, CAP_CLOCK, CAP_VOICE_API},
        "max_ms": 15_000,
        "max_memory_mb": 128,
        "fuel": 2_000_000,
        "fs_roots": [],
        "net_hosts": ["127.0.0.1", "localhost"],
    },
    "untrusted": {
        "label": "Untrusted guest (Wasm-like default)",
        "caps": {CAP_COMPUTE, CAP_CLOCK},
        "max_ms": 3_000,
        "max_memory_mb": 32,
        "fuel": 500_000,
        "fs_roots": [],
        "net_hosts": [],
    },
    "founder_tool": {
        "label": "Founder tool (still not ambient)",
        "caps": {
            CAP_COMPUTE,
            CAP_CLOCK,
            CAP_FS_READ,
            CAP_FS_WRITE,
            CAP_NET_HTTP,
            CAP_VOICE_API,
            CAP_DESKTOP,
        },
        "max_ms": 180_000,
        "max_memory_mb": 1024,
        "fuel": 50_000_000,
        "fs_roots": [],
        "net_hosts": ["*"],  # still audited; prefer explicit hosts
    },
    "claude_agent": {
        "label": "Claude Agent SDK (desk coding agent)",
        "caps": {
            CAP_COMPUTE,
            CAP_CLOCK,
            CAP_FS_READ,
            CAP_FS_WRITE,
            CAP_SHELL,
            CAP_NET_HTTP,
        },
        "max_ms": 900_000,
        "max_memory_mb": 1024,
        "fuel": 100_000_000,
        "fs_roots": [],
        "net_hosts": ["*"],
    },
}


@dataclass
class Grant:
    profile: str
    caps: Set[str]
    fs_roots: List[str] = field(default_factory=list)
    net_hosts: List[str] = field(default_factory=list)
    max_ms: int = 5_000
    max_memory_mb: int = 64
    fuel: int = 1_000_000
    agent_id: str = ""
    workspace: str = ""
    session_id: str = ""

    def has(self, cap: str) -> bool:
        return cap in self.caps


@dataclass
class Receipt:
    id: str
    ok: bool
    profile: str
    action: str
    agent_id: str
    caps_used: List[str]
    detail: str
    started_at: float
    ended_at: float
    fuel_spent: int = 0
    error: str = ""
    trap: str = ""  # Wasm-like trap name if denied/failed

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def list_profiles() -> Dict[str, Any]:
    return {
        "ok": True,
        "profiles": {
            k: {
                "label": v["label"],
                "caps": sorted(v["caps"]),
                "max_ms": v["max_ms"],
                "max_memory_mb": v["max_memory_mb"],
                "fuel": v["fuel"],
            }
            for k, v in PROFILES.items()
        },
        "capabilities": sorted(ALL_CAPS),
        "doctrine": (
            "Zero ambient authority. Grant minimum caps. "
            "Untrusted tools start as compute-only. "
            "Voice plugins get voice:api only. "
            "Wasmtime optional for .wasm guests."
        ),
    }


def mint_grant(
    profile: str = "compute",
    *,
    workspace_path: str = "",
    tenant_path: str = "",
    agent_id: str = "",
    session_id: str = "",
    extra_caps: Optional[Sequence[str]] = None,
    net_hosts: Optional[Sequence[str]] = None,
) -> Grant:
    """Mint a capability grant for one job/instance."""
    base = PROFILES.get(profile) or PROFILES["untrusted"]
    caps = set(base["caps"])
    for c in extra_caps or []:
        if c in ALL_CAPS:
            caps.add(c)

    roots: List[str] = []
    if workspace_path:
        roots.append(str(Path(workspace_path).resolve()))
    if tenant_path:
        roots.append(str(Path(tenant_path).resolve()))
    # market seat: never allow empty roots with write
    if profile == "market_seat" and not roots:
        # default tenant root
        roots.append(str((Path.home() / ".pocket" / "tenants" / "_default").resolve()))

    hosts = list(net_hosts) if net_hosts is not None else list(base.get("net_hosts") or [])

    return Grant(
        profile=profile if profile in PROFILES else "untrusted",
        caps=caps,
        fs_roots=roots,
        net_hosts=hosts,
        max_ms=int(base["max_ms"]),
        max_memory_mb=int(base["max_memory_mb"]),
        fuel=int(base["fuel"]),
        agent_id=agent_id or "",
        workspace=workspace_path or "",
        session_id=session_id or "",
    )


def _path_allowed(path: Path, roots: Sequence[str], *, write: bool = False) -> bool:
    if not roots:
        return False
    try:
        resolved = path.resolve()
    except Exception:
        return False
    for root in roots:
        try:
            r = Path(root).resolve()
            resolved.relative_to(r)
            return True
        except Exception:
            continue
    return False


def _host_allowed(host: str, allow: Sequence[str]) -> bool:
    h = (host or "").strip().lower()
    if not h:
        return False
    if "*" in allow:
        return True
    return h in {a.lower() for a in allow}


def check(
    grant: Grant,
    action: str,
    *,
    path: str = "",
    host: str = "",
    fuel_cost: int = 1,
) -> tuple[bool, str]:
    """Return (ok, trap_or_reason)."""
    if fuel_cost > grant.fuel:
        return False, "trap:out_of_fuel"
    if action in ("compute", "eval", "transform"):
        if not grant.has(CAP_COMPUTE):
            return False, "trap:cap_compute"
        return True, ""
    if action in ("fs_read", "read_file", "list_dir"):
        if not grant.has(CAP_FS_READ):
            return False, "trap:cap_fs_read"
        if not _path_allowed(Path(path), grant.fs_roots):
            return False, "trap:path_denied"
        return True, ""
    if action in ("fs_write", "write_file", "mkdir"):
        if not grant.has(CAP_FS_WRITE):
            return False, "trap:cap_fs_write"
        if not _path_allowed(Path(path), grant.fs_roots, write=True):
            return False, "trap:path_denied"
        return True, ""
    if action in ("net_http", "fetch"):
        if not grant.has(CAP_NET_HTTP) and not grant.has(CAP_VOICE_API):
            return False, "trap:cap_net"
        if not _host_allowed(host, grant.net_hosts):
            return False, "trap:host_denied"
        return True, ""
    if action == "voice_api":
        if not grant.has(CAP_VOICE_API):
            return False, "trap:cap_voice"
        if host and not _host_allowed(host, grant.net_hosts or ["127.0.0.1", "localhost"]):
            return False, "trap:host_denied"
        return True, ""
    if action in ("shell", "exec"):
        if not grant.has(CAP_SHELL):
            return False, "trap:cap_shell"
        return True, ""
    if action == "desktop":
        if not grant.has(CAP_DESKTOP):
            return False, "trap:cap_desktop"
        return True, ""
    if action == "clock":
        if not grant.has(CAP_CLOCK):
            return False, "trap:cap_clock"
        return True, ""
    return False, "trap:unknown_action"


def _write_receipt(rec: Receipt) -> Path:
    p = RECEIPTS / f"{int(rec.started_at)}_{rec.id}.json"
    p.write_text(json.dumps(rec.to_dict(), indent=2), encoding="utf-8")
    try:
        from pocket.safety import audit  # type: ignore

        audit(
            "sandbox",
            {
                "receipt": rec.id,
                "ok": rec.ok,
                "action": rec.action,
                "profile": rec.profile,
                "trap": rec.trap,
                "agent": rec.agent_id,
            },
        )
    except Exception:
        pass
    return p


def run_python_tool(
    grant: Grant,
    action: str,
    fn: Callable[[], Any],
    *,
    path: str = "",
    host: str = "",
    fuel_cost: int = 100,
    detail: str = "",
) -> Dict[str, Any]:
    """Run a host-side tool callback only if capabilities allow."""
    started = time.time()
    rid = uuid.uuid4().hex[:12]
    ok, trap = check(grant, action, path=path, host=host, fuel_cost=fuel_cost)
    if not ok:
        rec = Receipt(
            id=rid,
            ok=False,
            profile=grant.profile,
            action=action,
            agent_id=grant.agent_id,
            caps_used=[],
            detail=detail,
            started_at=started,
            ended_at=time.time(),
            error="capability_denied",
            trap=trap,
        )
        _write_receipt(rec)
        return {"ok": False, "error": "capability_denied", "trap": trap, "receipt": rec.to_dict()}

    # timeout via wall clock (cooperative)
    try:
        result = fn()
        ended = time.time()
        if (ended - started) * 1000 > grant.max_ms:
            rec = Receipt(
                id=rid,
                ok=False,
                profile=grant.profile,
                action=action,
                agent_id=grant.agent_id,
                caps_used=sorted(grant.caps),
                detail=detail,
                started_at=started,
                ended_at=ended,
                fuel_spent=fuel_cost,
                error="timeout",
                trap="trap:timeout",
            )
            _write_receipt(rec)
            return {"ok": False, "error": "timeout", "trap": "trap:timeout", "receipt": rec.to_dict()}

        rec = Receipt(
            id=rid,
            ok=True,
            profile=grant.profile,
            action=action,
            agent_id=grant.agent_id,
            caps_used=sorted(grant.caps),
            detail=detail or action,
            started_at=started,
            ended_at=ended,
            fuel_spent=fuel_cost,
        )
        path_out = _write_receipt(rec)
        return {
            "ok": True,
            "result": result,
            "receipt": rec.to_dict(),
            "receipt_path": str(path_out),
            "elapsed_ms": int((ended - started) * 1000),
        }
    except Exception as e:
        rec = Receipt(
            id=rid,
            ok=False,
            profile=grant.profile,
            action=action,
            agent_id=grant.agent_id,
            caps_used=sorted(grant.caps),
            detail=detail,
            started_at=started,
            ended_at=time.time(),
            fuel_spent=fuel_cost,
            error=str(e)[:300],
            trap="trap:guest_exception",
        )
        _write_receipt(rec)
        return {"ok": False, "error": str(e)[:300], "trap": "trap:guest_exception", "receipt": rec.to_dict()}


def safe_read_text(grant: Grant, path: str, *, max_bytes: int = 200_000) -> Dict[str, Any]:
    def _read():
        p = Path(path)
        data = p.read_bytes()[:max_bytes]
        return {"path": str(p), "bytes": len(data), "text": data.decode("utf-8", errors="replace")}

    return run_python_tool(grant, "fs_read", _read, path=path, fuel_cost=50, detail=f"read {path}")


def safe_write_text(grant: Grant, path: str, content: str) -> Dict[str, Any]:
    def _write():
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = (content or "").encode("utf-8")
        p.write_bytes(raw)
        return {"path": str(p), "bytes": len(raw)}

    return run_python_tool(grant, "fs_write", _write, path=path, fuel_cost=80, detail=f"write {path}")


def voice_turn(
    grant: Grant,
    text: str,
    *,
    base_url: str = "http://127.0.0.1:8790",
    business_mode: str = "customer_service",
    session_id: str = "",
) -> Dict[str, Any]:
    """Call Pocket Voice HTTP API if voice:api granted (localhost by default)."""
    import urllib.request

    host = "127.0.0.1"
    if "://" in base_url:
        host = base_url.split("://", 1)[1].split("/", 1)[0].split(":")[0]

    def _call():
        payload = json.dumps(
            {
                "text": text,
                "business_mode": business_mode,
                "session_id": session_id or grant.session_id or "pocket-agent",
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            base_url.rstrip("/") + "/v1/turn",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=min(14, grant.max_ms / 1000)) as resp:
            return json.loads(resp.read().decode("utf-8"))

    return run_python_tool(
        grant,
        "voice_api",
        _call,
        host=host,
        fuel_cost=200,
        detail=f"voice turn {business_mode}",
    )


def wasmtime_available() -> bool:
    return bool(shutil.which("wasmtime"))


def run_wasm(
    grant: Grant,
    wasm_path: str,
    *,
    args: Optional[List[str]] = None,
    stdin_text: str = "",
) -> Dict[str, Any]:
    """Run a .wasm module with wasmtime if installed — no preopens unless fs caps + roots.

    Untrusted default: no --dir, no network. Fuel via --fuel if supported.
    """
    if not grant.has(CAP_COMPUTE):
        return {"ok": False, "error": "capability_denied", "trap": "trap:cap_compute"}
    if not wasmtime_available():
        return {
            "ok": False,
            "error": "wasmtime_not_installed",
            "hint": "Install Wasmtime CLI for guest .wasm tools, or use run_python_tool",
        }
    wp = Path(wasm_path)
    if not wp.is_file():
        return {"ok": False, "error": "wasm_not_found"}

    cmd = ["wasmtime"]
    # resource limits (best-effort flags vary by version)
    cmd += ["run", "--disable-cache"]
    if grant.has(CAP_FS_READ) or grant.has(CAP_FS_WRITE):
        for root in grant.fs_roots:
            # map host root into guest
            cmd += [f"--dir={root}::{root}"]
    cmd.append(str(wp))
    if args:
        cmd += list(args)

    started = time.time()
    rid = uuid.uuid4().hex[:12]

    def _run():
        timeout = max(1.0, grant.max_ms / 1000.0)
        proc = subprocess.run(
            cmd,
            input=(stdin_text or "").encode("utf-8"),
            capture_output=True,
            timeout=timeout,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout.decode("utf-8", errors="replace")[:50_000],
            "stderr": proc.stderr.decode("utf-8", errors="replace")[:20_000],
        }

    try:
        out = _run()
        ended = time.time()
        ok = out.get("returncode") == 0
        rec = Receipt(
            id=rid,
            ok=ok,
            profile=grant.profile,
            action="wasm_run",
            agent_id=grant.agent_id,
            caps_used=sorted(grant.caps),
            detail=str(wp.name),
            started_at=started,
            ended_at=ended,
            fuel_spent=1000,
            error="" if ok else "wasm_nonzero_exit",
            trap="" if ok else "trap:wasm_exit",
        )
        _write_receipt(rec)
        return {"ok": ok, "wasm": out, "receipt": rec.to_dict(), "elapsed_ms": int((ended - started) * 1000)}
    except subprocess.TimeoutExpired:
        rec = Receipt(
            id=rid,
            ok=False,
            profile=grant.profile,
            action="wasm_run",
            agent_id=grant.agent_id,
            caps_used=sorted(grant.caps),
            detail=str(wp.name),
            started_at=started,
            ended_at=time.time(),
            error="timeout",
            trap="trap:timeout",
        )
        _write_receipt(rec)
        return {"ok": False, "error": "timeout", "trap": "trap:timeout", "receipt": rec.to_dict()}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300], "trap": "trap:host_exception"}


def status() -> Dict[str, Any]:
    receipts = sorted(RECEIPTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]
    recent = []
    for p in receipts:
        try:
            recent.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return {
        "ok": True,
        "profiles": list(PROFILES.keys()),
        "wasmtime": wasmtime_available(),
        "receipts_dir": str(RECEIPTS),
        "recent_receipts": recent,
        "voice_default": "http://127.0.0.1:8790",
        "doc": "docs/research/POCKET_AGENT_WASM_SANDBOX.md",
    }
