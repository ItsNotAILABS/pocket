"""POCKET bridge for the AURO/MESIE runtime family.

Selection order is the stable AuroSDK facade, then the scientific MESIE SDK,
then the installed ``auro`` CLI. The bridge never silently changes to a cloud
provider. POCKET Host retains policy and side-effect authority.
"""
from __future__ import annotations

import json
import shutil
from typing import Any, Dict

from pocket.channel_fabric import envelope
from pocket.cli_tools import run_cli


def status() -> Dict[str, Any]:
    sdk = False
    auro_sdk = False
    version = ""
    try:
        import mesie  # type: ignore
        sdk = True
        version = str(getattr(mesie, "__version__", ""))
        try:
            from mesie.auro_sdk import AuroSDK  # type: ignore  # noqa: F401
            auro_sdk = True
        except Exception:
            pass
    except Exception:
        pass
    return {
        "ok": sdk or bool(shutil.which("mesie")) or bool(shutil.which("auro")),
        "sdk": sdk,
        "auro_sdk": auro_sdk,
        "version": version,
        "mesie_cli": shutil.which("mesie"),
        "auro_cli": shutil.which("auro"),
        "channel_contract": "auro.pocket-channel-contract.v2",
        "pocket_envelope": "pocket.channel-envelope.v2",
        "authority": "compute-only; POCKET Host retains policy/side-effect authority",
    }


def capabilities() -> Dict[str, Any]:
    return {
        "schema": "pocket.auro-mesie.capabilities.v2",
        "actions": [
            "health", "capabilities", "channels.describe",
            "spectral.load", "spectral.match", "spectral.rank", "spectral.embed",
            "spectral.generate.psd", "spectral.generate.fas", "spectral.generate.rotdnn",
            "spectral.validate", "spectral.normalize", "foundation.describe",
            "benchmark.run", "health.describe",
        ],
        "channels": ["model", "intel", "proof", "recovery"],
        "authority": {"compute_only": True, "external_side_effects": False},
        "runtime": status(),
    }


def _channel(action: str, ok: bool) -> str:
    if not ok:
        return "recovery"
    if any(x in action for x in ("benchmark", "validate", "receipt", "evidence")):
        return "proof"
    if any(x in action for x in ("research", "intel")):
        return "intel"
    return "model"


def _invoke_auro_sdk(action: str, payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    from mesie.auro_sdk import AuroSDK  # type: ignore
    sdk = AuroSDK()
    mapped = {"health.describe": "health", "model.foundation.describe": "foundation.describe"}.get(action, action)
    out = sdk.invoke(mapped, payload, request_id=request_id)
    out["transport"] = "auro-sdk"
    return out


def _invoke_legacy_sdk(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.sdk import SpectralIntelligenceSDK  # type: ignore
    engine = SpectralIntelligenceSDK()
    if action in {"health.describe", "model.foundation.describe"}:
        return {"ok": True, "engine": "MESIE SpectralIntelligenceSDK", "version": engine.version, "transport": "mesie-sdk"}
    if action == "spectral.validate":
        report = engine.validate(payload.get("record"))
        return {"ok": True, "result": getattr(report, "to_dict", lambda: str(report))(), "transport": "mesie-sdk"}
    if action == "spectral.embed":
        vec = engine.embed(payload.get("record"))
        return {"ok": True, "embedding": vec.tolist(), "shape": list(vec.shape), "transport": "mesie-sdk"}
    raise ValueError(f"legacy MESIE SDK action not exposed safely: {action}")


def invoke(action: str, payload: Dict[str, Any] | None = None, *, request_id: str = "") -> Dict[str, Any]:
    payload = dict(payload or {})
    action = (action or "health.describe").strip().lower()
    request_id = request_id or ""
    result: Dict[str, Any]
    first_error = ""
    try:
        result = _invoke_auro_sdk(action, payload, request_id)
    except Exception as auro_error:
        first_error = str(auro_error)[:240]
        try:
            result = _invoke_legacy_sdk(action, payload)
        except Exception as mesie_error:
            if shutil.which("auro"):
                args = ["invoke", {"health.describe":"health", "model.foundation.describe":"foundation.describe"}.get(action, action), "--json", json.dumps(payload)]
                if request_id:
                    args += ["--request-id", request_id]
                cli = run_cli("auro", args, timeout=180)
                result = {"ok": bool(cli.get("ok")), "transport": "auro-cli", "cli": cli, "sdk_error": first_error, "mesie_sdk_error": str(mesie_error)[:200]}
            elif shutil.which("mesie") and action in {"health.describe", "model.foundation.describe"}:
                cli = run_cli("mesie", ["--help"], timeout=30)
                result = {"ok": bool(cli.get("ok")), "transport": "mesie-cli", "cli": cli, "sdk_error": first_error}
            else:
                result = {"ok": False, "error": str(mesie_error)[:400], "auro_sdk_error": first_error, "transport": "none"}

    ch = _channel(action, bool(result.get("ok")))
    if not result.get("message"):
        descriptor = {
            "schema": "nexus.capability-descriptor.v1",
            "component": "auro-mesie-runtime",
            "locality": "local-or-explicit-runtime",
            "authority": "compute-only",
            "external_side_effects": False,
            "evidence_level": "runtime-receipt" if result.get("receipt") else "source",
        }
        result["message"] = envelope(
            sender="AURO_MESIE",
            recipient="POCKET_HOST",
            channel_name=ch,
            kind=action,
            body={"ok": result.get("ok"), "transport": result.get("transport", "in-process"), "version": status().get("version")},
            request_id=request_id,
            state="succeeded" if result.get("ok") else "failed",
            capability_descriptor=descriptor,
        )
    result["channel"] = ch
    return result
