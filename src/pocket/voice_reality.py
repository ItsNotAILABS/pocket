"""Voice Reality bridge: speech becomes a typed, executable POCKET envelope."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
from typing import Any, Dict

from pocket.model_mesh import route as route_model

_PENDING: Dict[str, Dict[str, Any]] = {}


def _workspace() -> str:
    return os.environ.get("POCKET_WORKSPACE", str(Path.home() / ".pocket" / "workspace"))


def _go_binary() -> str:
    explicit = os.environ.get("POCKET_ENVELOPE_BIN", "").strip()
    if explicit and Path(explicit).exists():
        return explicit
    for name in ("pocket-envelope", "pocket-envelope.exe"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def compile_envelope(text: str, *, project: str = "default", request_id: str = "") -> Dict[str, Any]:
    request_id = request_id or f"voice-{uuid.uuid4().hex[:16]}"
    payload = {"transcript": text, "request_id": request_id, "project": project, "workspace": _workspace()}
    binary = _go_binary()
    if binary:
        try:
            proc = subprocess.run([binary, "compile"], input=json.dumps(payload), capture_output=True, text=True, timeout=4, check=False)
            if proc.returncode == 0:
                env = json.loads(proc.stdout)
                env["control_runtime"] = "go"
                env["model_route"] = route_model(text)
                return env
        except Exception:
            pass
    low = text.lower()
    intent, action, agent, risk = "assist", "agent.run", "pocket-agent", "low"
    if any(x in low for x in ("deploy", "publish", "ship")):
        intent, action, agent, risk = "deploy", "deploy.plan", "sovereign-forge-os", "high"
    elif any(x in low for x in ("build", "make", "create")):
        intent, action, risk = "build", "build.execute", "medium"
    elif any(x in low for x in ("code", "fix", "refactor", "test")):
        intent, action, risk = "code", "agent.run", "medium"
    return {
        "schema": "pocket.voice-reality-envelope.v1",
        "request_id": request_id,
        "origin": "voice",
        "transcript": text,
        "intent": intent,
        "action": action,
        "agent": agent,
        "scope": {"tenant": "", "project": project, "session": request_id, "workspace": _workspace()},
        "risk": risk,
        "approval": "confirm" if risk == "high" else "allow",
        "parameters": {"prompt": text},
        "acceptance": ["execution receipt exists", "artifacts are hashed when produced", "verification result is attached"],
        "state": "compiled",
        "events": [{"type": "compiled", "at": time.time(), "message": f"voice compiled to {action}"}],
        "artifacts": [],
        "verification": [],
        "control_runtime": "python-fallback",
        "model_route": route_model(text),
    }


def executable_intent(text: str) -> bool:
    low = (text or "").lower()
    return any(v in low for v in ("code", "build", "make", "create", "fix", "refactor", "test", "deploy", "publish", "ship", "benchmark"))


def _execute_envelope(env: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from pocket.orchestrator_exec import dispatch_skill
        result = dispatch_skill(
            "mission_start",
            prompt=env["transcript"],
            params={"name": f"VOICE-{env['request_id'][-8:]}", "max_hours": 1.0},
        )
    except Exception as exc:
        env["state"] = "failed"
        env["events"].append({"type": "execution_failed", "at": time.time(), "error": str(exc)[:300]})
        return {"ok": False, "envelope": env, "state": "failed", "error": str(exc)[:300]}
    ok = isinstance(result, dict) and result.get("ok", True)
    env["state"] = "executing" if ok else "failed"
    env["events"].append({"type": "execution_started" if ok else "execution_failed", "at": time.time(), "state": env["state"]})
    env["result"] = result
    return {"ok": ok, "envelope": env, "state": env["state"]}


def dispatch(text: str, *, project: str = "default", execute: bool = False) -> Dict[str, Any]:
    env = compile_envelope(text, project=project)
    if not execute:
        return {"ok": True, "envelope": env, "state": "compiled"}
    if env.get("approval") == "confirm":
        env["state"] = "awaiting_confirmation"
        _PENDING[project] = env
        return {"ok": True, "envelope": env, "state": "awaiting_confirmation", "needs_confirmation": True}
    return _execute_envelope(env)


def pending(project: str = "default") -> Dict[str, Any] | None:
    return _PENDING.get(project)


def confirm_pending(project: str = "default") -> Dict[str, Any]:
    env = _PENDING.pop(project, None)
    if not env:
        return {"ok": False, "state": "no_pending", "error": "no pending voice operation"}
    env["approval"] = "approved"
    env["events"].append({"type": "approved", "at": time.time(), "state": "approved"})
    return _execute_envelope(env)


def cancel_pending(project: str = "default") -> Dict[str, Any]:
    env = _PENDING.pop(project, None)
    if not env:
        return {"ok": False, "state": "no_pending"}
    env["state"] = "cancelled"
    env["events"].append({"type": "cancelled", "at": time.time(), "state": "cancelled"})
    return {"ok": True, "state": "cancelled", "envelope": env}


def spoken_summary(run: Dict[str, Any]) -> str:
    env = run.get("envelope") or {}
    state = run.get("state") or env.get("state") or "unknown"
    if state == "awaiting_confirmation":
        return f"I compiled the {env.get('intent')} operation. Say confirm to execute it or cancel to discard it."
    if state == "executing":
        return f"Confirmed. I started {env.get('action')} through {env.get('agent')}. I will keep the execution state and verification results attached to this work."
    if state == "succeeded":
        artifacts = len(env.get("artifacts") or [])
        return f"Done. {env.get('action')} succeeded. {artifacts} artifacts are attached to the execution envelope."
    if state == "cancelled":
        return "Cancelled. I discarded the pending voice operation."
    if state == "no_pending":
        return "There is no pending voice operation to confirm."
    if state == "failed":
        return "The operation failed. I kept the execution envelope and error so it can be repaired instead of pretending it completed."
    return f"I compiled your voice into {env.get('action')} through {env.get('agent')}."
