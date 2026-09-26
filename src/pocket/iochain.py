"""IOChain — idle WebGPU / GPU inference, settled on Solana. Prep inside Pocket."""

from __future__ import annotations

from typing import Any, Dict

PITCH = (
    "AI is racing to build new data centres while the GPUs we already have sit at 5% utilisation. "
    "IOChain turns that idle hardware into a trustable AI inference infrastructure, settled on Solana. "
    "Developers publish models, deployers run them, investors hold fractional shares in the models they back. "
    "Pay-per-call, on-chain, peer to peer. Ships with a CLI, Tauri desktop, web app, and TS + Python SDKs."
)

SCHEMA = "pocket.iochain.v1"


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "product": "IOChain",
        "settlement": "solana",
        "pitch": PITCH,
        "surfaces": ["cli", "tauri", "web", "sdk-ts", "sdk-python"],
        "roles": ["developer", "deployer", "investor"],
        "ui": "/webgpu",
        "webgpu": True,
        "note": "Prep inside Pocket WebGPU. Separate from Monad Metropolis and self.tools.",
    }
