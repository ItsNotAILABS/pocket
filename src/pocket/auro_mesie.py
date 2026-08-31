"""POCKET bridge for the AURO/MESIE runtime family.

Supports installed MESIE Python SDK first, then installed CLI. It never silently
changes to a cloud provider. Results can be wrapped into POCKET channel envelopes.
"""
from __future__ import annotations

import json
import shutil
from typing import Any, Dict

from pocket.channel_fabric import envelope
from pocket.cli_tools import run_cli


def status() -> Dict[str, Any]:
    sdk = False
    version = ""
    try:
        import mesie  # type: ignore
        sdk = True
        version = str(getattr(mesie, "__version__", ""))
    except Exception:
        pass
    return {
        "ok": sdk or bool(shutil.which("mesie")) or bool(shutil.which("auro")),
        "sdk": sdk,
        "version": version,
        "mesie_cli": shutil.which("mesie"),
        "auro_cli": shutil.which("auro"),
        "authority": "compute-only; POCKET Host retains policy/side-effect authority",
    }


def capabilities() -> Dict[str, Any]:
    return {
        "schema": "pocket.auro-mesie.capabilities.v1",
        "actions": [
            "spectral.load", "spectral.match", "spectral.rank", "spectral.embed",
            "spectral.generate.psd", "spectral.generate.fas", "spectral.generate.rotdnn",
            "spectral.validate", "spectral.normalize", "model.foundation.describe",
            "benchmark.run", "health.describe",
        ],
        "channels": ["model", "intel", "proof"],
        "runtime": status(),
    }


def _sdk_describe() -> Dict[str, Any]:
    from mesie.sdk import SpectralIntelligenceSDK  # type: ignore
    engine = SpectralIntelligenceSDK()
    return {
        "ok": True,
        "engine": "MESIE SpectralIntelligenceSDK",
        "version": engine.version,
        "capabilities": capabilities()["actions"],
        "transport": "in-process",
    }


def invoke(action: str, payload: Dict[str, Any] | None = None, *, request_id: str = "") -> Dict[str, Any]:
    payload = dict(payload or {})
    action = (action or "health.describe").strip().lower()
    result: Dict[str, Any]
    try:
        if action in {"health.describe", "model.foundation.describe"}:
            result = _sdk_describe()
        elif action == "spectral.validate":
            from mesie.sdk import SpectralIntelligenceSDK  # type: ignore
            report = SpectralIntelligenceSDK().validate(payload.get("record"))
            result = {"ok": True, "result": getattr(report, "to_dict", lambda: str(report))()}
        elif action == "spectral.embed":
            from mesie.sdk import SpectralIntelligenceSDK  # type: ignore
            vec = SpectralIntelligenceSDK().embed(payload.get("record"))
            result = {"ok": True, "embedding": vec.tolist(), "shape": list(vec.shape)}
        else:
            result = {"ok": False, "error": f"POCKET bridge action not yet exposed safely: {action}"}
    except Exception as sdk_error:
        if shutil.which("auro"):
            cli = run_cli("auro", ["invoke", action, "--json", json.dumps(payload)], timeout=180)
            result = {"ok": bool(cli.get("ok")), "transport": "auro-cli", "cli": cli, "sdk_error": str(sdk_error)[:200]}
        elif shutil.which("mesie") and action in {"health.describe", "model.foundation.describe"}:
            cli = run_cli("mesie", ["--help"], timeout=30)
            result = {"ok": bool(cli.get("ok")), "transport": "mesie-cli", "cli": cli, "sdk_error": str(sdk_error)[:200]}
        else:
            result = {"ok": False, "error": str(sdk_error)[:400], "transport": "none"}

    ch = "proof" if "benchmark" in action or "validate" in action else "model"
    result["message"] = envelope(
        sender="AURO_MESIE",
        recipient="POCKET_HOST",
        channel_name=ch,
        kind=action,
        body={"ok": result.get("ok"), "transport": result.get("transport", "in-process")},
        request_id=request_id,
    )
    return result
