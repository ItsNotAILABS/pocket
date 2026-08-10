"""POCKET product catalog — features that actually ship (not scaffold claims)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

VERSION = "2.1.0"
PRODUCT_NAME = "POCKET"
PRODUCT_LINE = "AI workspace on your machine · app, team seats, developer API"
COMPANY = "Medina Tech Labs"
LAB = "ItsNotAI Labs"
ORG = "ItsNotAILABS"
EDITION = "company"


def feature_matrix() -> List[Dict[str, Any]]:
    """Every feature with status and how to use it."""
    return [
        {
            "id": "auth",
            "name": "Sign-in & team invites",
            "status": "product",
            "use": "Sign in · join with invite",
            "api": ["POST /v1/auth/login", "POST /v1/auth/register"],
        },
        {
            "id": "codex",
            "name": "Code (Codex)",
            "status": "product",
            "use": "New chat → Code → describe the task",
            "requires": "codex CLI on PATH",
        },
        {
            "id": "grok",
            "name": "Research & code (Grok)",
            "status": "product",
            "use": "New chat → Grok → describe the task",
            "requires": "grok CLI (~/.grok/bin)",
        },
        {
            "id": "plan",
            "name": "Plan",
            "status": "product",
            "use": "New chat → Plan → outline only",
        },
        {
            "id": "desktop",
            "name": "Open apps on this PC",
            "status": "product",
            "use": "Ask the agent to open apps or links",
            "apps": 14,
        },
        {
            "id": "web",
            "name": "Web research",
            "status": "product",
            "use": "Search and summarize the web",
        },
        {
            "id": "nexus",
            "name": "Intelligence tools",
            "status": "product",
            "use": "Optional advanced tools catalog",
            "api": ["GET /v1/nexus", "POST /v1/nexus/run", "GET /v1/stack"],
        },
        {
            "id": "mesie",
            "name": "Compute engines",
            "status": "product",
            "use": "Optional scientific / spectral compute",
            "api": ["GET /v1/mesie", "GET /v1/stack"],
        },
        {
            "id": "fusion_rfe",
            "name": "Screen understanding",
            "status": "product",
            "use": "Read the live desktop for agent actions",
            "api": ["GET /v1/vision/page", "POST /v1/rfe/synthesize"],
        },
        {
            "id": "subagent_mesh",
            "name": "Background helpers",
            "status": "product",
            "use": "Helpers that coordinate work in the background",
            "api": [
                "GET /v1/protocols/mesh",
                "POST /v1/hooks/mesh",
                "POST /v1/subagents/dispatch",
                "GET /v1/mesh",
            ],
        },
        {
            "id": "vcomp",
            "name": "Long-running jobs",
            "status": "product",
            "use": "Queue multi-step work and leave it running",
            "api": ["POST /v1/vcomp/open", "POST /v1/missions/start"],
        },
        {
            "id": "product_studio",
            "name": "Studio demos",
            "status": "product",
            "use": "Product phone and web demo frames",
            "api": ["POST /v1/studio/product_phone", "POST /v1/studio/product_web"],
        },
        {
            "id": "video_watch",
            "name": "Video review",
            "status": "product",
            "use": "Have agents review a video or recording",
            "api": ["POST /v1/video/watch"],
        },
        {
            "id": "tour",
            "name": "Product tour",
            "status": "product",
            "use": "Guided overview at /tour",
            "api": ["GET /tour", "GET /v1/product/presentation"],
        },
        {
            "id": "term",
            "name": "Terminal",
            "status": "product",
            "use": "Interactive shell for admins",
        },
        {
            "id": "deploy",
            "name": "Local deploys",
            "status": "product",
            "use": "Ship static sites and small services on this host",
        },
        {
            "id": "upload",
            "name": "File upload",
            "status": "product",
            "use": "Upload files into the workspace",
        },
        {
            "id": "stream",
            "name": "Live responses",
            "status": "product",
            "use": "Watch answers update while work runs",
        },
        {
            "id": "node_transfer",
            "name": "Device transfer",
            "status": "product",
            "use": "Pair devices with a code · send encrypted files",
            "api": ["POST /v1/node/pair", "POST /v1/node/offer", "POST /v1/node/claim"],
        },
        {
            "id": "pixel_vmem",
            "name": "Private memory",
            "status": "product",
            "use": "Store notes in private content-addressed memory",
            "api": ["POST /v1/vmem/put", "GET /v1/vmem/map"],
        },
        {
            "id": "phone",
            "name": "POCKET Phone",
            "status": "product",
            "use": (
                "Aether Neural Core ANC-1 · 6.7\" paper-thin hybrid E-Ink · "
                "Aria + Working + desk pair"
            ),
            "hardware": {
                "processor": "Aether Neural Core ANC-1 (Dedicated Tensor processing cluster)",
                "display": '6.7" Paper-thin Hybrid E-Ink',
            },
            "api": ["GET /phone", "GET /v1/hardware", "GET /v1/device"],
        },
        {
            "id": "safety",
            "name": "Safety layer",
            "status": "product",
            "use": "Auth, allowlists, audit log, rate limits",
        },
        {
            "id": "credits",
            "name": "POCK / NEXUS metering",
            "status": "product",
            "use": "Burn on jobs; refill = subscription hook",
        },
        {
            "id": "headless_agents",
            "name": "Headless agent fleet",
            "status": "product",
            "use": "15 agents: researcher, planner, coder, squad, security…",
            "api": ["GET /v1/ai/agents", "POST /v1/ai/agents/{id}/run"],
        },
        {
            "id": "ai_api",
            "name": "POCKET AI API (sellable)",
            "status": "product",
            "use": "API keys + chat + jobs + metering for third parties",
            "api": [
                "GET /v1/ai",
                "POST /v1/ai/chat",
                "POST /v1/ai/keys",
                "POST /v1/ai/jobs",
            ],
            "sell": {"starter_usd": 29, "pro_usd": 99, "enterprise_usd": 299},
        },
    ]


def doctor() -> Dict[str, Any]:
    """Product readiness report."""
    from pocket.auth import ACCESS_NOTE, expected_user
    from pocket.nexus_bridge import nexus_available
    from pocket.safety import policy_summary

    checks = []

    def add(name: str, ok: bool, detail: str = ""):
        checks.append({"name": name, "ok": ok, "detail": detail})

    py = os.environ.get("POCKET_PYTHON") or shutil.which("python") or ""
    add("python", bool(py), py)
    add("codex_cli", bool(shutil.which("codex")), shutil.which("codex") or "missing")
    g = shutil.which("grok") or ""
    if not g:
        gp = Path.home() / ".grok" / "bin" / "grok.exe"
        g = str(gp) if gp.exists() else ""
    add("grok_cli", bool(g), g or "missing")
    add("access_file", ACCESS_NOTE.exists(), str(ACCESS_NOTE))
    nx = nexus_available()
    add("nexus", bool(nx.get("ok")), nx.get("root") or "")
    add("cloudflared", bool(shutil.which("cloudflared") or Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe").exists()), "service or CLI")
    pub = (os.environ.get("POCKET_PUBLIC_URL") or "").strip()
    add("public_url_env", pub.startswith("http"), pub or "unset")

    ok_n = sum(1 for c in checks if c["ok"])
    return {
        "ok": ok_n >= 4,
        "product": PRODUCT_NAME,
        "version": VERSION,
        "line": PRODUCT_LINE,
        "company": COMPANY,
        "lab": LAB,
        "org": ORG,
        "edition": EDITION,
        "ready_score": f"{ok_n}/{len(checks)}",
        "checks": checks,
        "features": feature_matrix(),
        "safety": policy_summary(),
        "auth_user": expected_user(),
        "start": "python -m pocket serve   OR   Desktop → POCKET",
        "github": "https://github.com/ItsNotAILABS/pocket",
        "phone": pub or "https://pocket.medinatechlabs.net/",
    }
