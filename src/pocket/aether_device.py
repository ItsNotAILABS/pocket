"""POCKET Phone hardware identity — Aether Neural Core + hybrid E-Ink.

First-class product profile so phone UI, APIs, and agents share one truth:

  PROCESSOR  Aether Neural Core ANC-1 (Dedicated Tensor processing cluster)
  DISPLAY    6.7" Paper-thin Hybrid E-Ink
"""

from __future__ import annotations

from typing import Any, Dict, List

HARDWARE: Dict[str, Any] = {
    "product": "POCKET Phone",
    "codename": "Aether",
    "schema": "pocket.hardware.aether.v1",
    "first_class": True,
    "processor": {
        "id": "ANC-1",
        "name": "Aether Neural Core ANC-1",
        "class": "Dedicated Tensor processing cluster",
        "role": "On-device neural inference for voice, vision fusion, and agent skills",
        "traits": [
            "tensor cluster",
            "low-latency local inference",
            "voice + vision co-processing",
            "sovereign (runs on-device when paired skills allow)",
        ],
    },
    "display": {
        "id": "hybrid-eink-6.7",
        "name": '6.7" Paper-thin Hybrid E-Ink',
        "size_in": 6.7,
        "form": "paper-thin",
        "type": "hybrid_e_ink",
        "role": "Readable outdoors · low power · dual-mode ink + active panel",
        "traits": [
            "hybrid e-ink",
            "paper-thin stack",
            "always-on glance surface",
            "agent status without OLED burn",
        ],
    },
    "software": {
        "shell": "POCKET Phone (/phone)",
        "pair": "Desk pair + Fusion",
        "agents": ["Aria voice", "Working board", "Plan", "Code", "Grok"],
        "consoles": ["WSL", "Python host", "Python WSL"],
    },
    "doctrine": (
        "Hardware identity is product truth — ANC-1 + hybrid E-Ink define the phone "
        "experience. Host (desk) and phone share agents; tensor work prefers on-device "
        "when available, falls back to lab host."
    ),
}


def profile() -> Dict[str, Any]:
    return {
        "ok": True,
        **HARDWARE,
        "summary": (
            f"{HARDWARE['processor']['name']} · {HARDWARE['display']['name']}"
        ),
        "api": {
            "hardware": "GET /v1/hardware",
            "device": "GET /v1/device",
            "phone": "GET /phone",
        },
    }


def spec_lines() -> List[str]:
    p = HARDWARE["processor"]
    d = HARDWARE["display"]
    return [
        f"PROCESSOR  {p['name']} ({p['class']})",
        f"DISPLAY    {d['name']}",
    ]


def markdown_card() -> str:
    p = HARDWARE["processor"]
    d = HARDWARE["display"]
    return (
        f"# {HARDWARE['product']}\n\n"
        f"| | |\n|---|---|\n"
        f"| **Processor** | {p['name']}<br><span style='opacity:.8'>{p['class']}</span> |\n"
        f"| **Display** | {d['name']} |\n\n"
        f"_{HARDWARE['doctrine']}_\n"
    )


def for_device_payload(base: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Merge hardware identity into a client device dict."""
    out = dict(base or {})
    out["hardware"] = {
        "processor": HARDWARE["processor"],
        "display": HARDWARE["display"],
        "codename": HARDWARE["codename"],
        "product": HARDWARE["product"],
    }
    if out.get("kind") == "phone":
        out["label"] = out.get("label") or "POCKET Phone"
        out["product_line"] = HARDWARE["product"]
    return out
