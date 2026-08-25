"""POCKET product catalog - implemented features and explicit evidence state."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from pocket import __version__
from pocket.corpus_architecture import product_contract, validate_contract

VERSION = __version__
PRODUCT_NAME = "POCKET"
PRODUCT_LINE = "AI workspace on your machine - cloud account, desktop runtime, Edge app, team seats, and developer API"
COMPANY = "Medina Tech Labs"
LAB = "ItsNotAI Labs"
ORG = "ItsNotAILABS"
EDITION = "company"


def feature_matrix() -> List[Dict[str, Any]]:
    """Every user-visible capability with its source-level status and entrypoint."""
    return [
        {
            "id": "triform_product",
            "name": "POCKET Cloud + Desktop + Edge",
            "status": "source-implemented-evidence-gated",
            "use": "Create an account, download POCKET Desktop, then open POCKET, POCKET Local, POCKET Edge, or POCKET Cloud",
            "contract": "pocket.triform-product.v1",
            "claim_boundary": "source presence does not prove live cloud deployment or clean installation",
        },
        {
            "id": "multi_user_organizations",
            "name": "Organizations, roles, seats, and tenant isolation",
            "status": "product",
            "use": "Owners invite people; each person creates their own account and receives a bounded role",
            "api": ["POST /v1/auth/register", "POST /v1/admin/invites", "GET /v1/auth/me"],
        },
        {
            "id": "device_federation",
            "name": "User-owned compute federation",
            "status": "source-implemented-evidence-gated",
            "use": "Pair a computer as a separate device principal and advertise bounded capabilities",
            "contract": "nexus.device-federation.v1",
            "claim_boundary": "device pairing is not unrestricted remote control",
        },
        {
            "id": "governed_execution",
            "name": "Approval-bound computer access",
            "status": "contract-and-runtime-surface",
            "use": "Discover, classify risk, plan, approve, execute, validate, and receipt",
            "runtime_cells": ["agent-sandbox", "app-bottle", "mini-os"],
            "contract": "nexus.runtime-cell.v1",
        },
        {
            "id": "evidence_classes",
            "name": "Evidence-native product operations",
            "status": "contract-and-validation-surface",
            "use": "Classify claims from E0 assertion through E5 external custody and reproduction",
            "contract": "nexus.evidence-classification.v1",
        },
        {
            "id": "auth",
            "name": "Sign-in and team invites",
            "status": "product",
            "use": "Sign in or join with an invite",
            "api": ["POST /v1/auth/login", "POST /v1/auth/register"],
        },
        {
            "id": "codex",
            "name": "Code (Codex)",
            "status": "product",
            "use": "New chat -> Code -> describe the task",
            "requires": "codex CLI on PATH",
        },
        {
            "id": "grok",
            "name": "Research and code (Grok)",
            "status": "product",
            "use": "New chat -> Grok -> describe the task",
            "requires": "grok CLI (~/.grok/bin)",
        },
        {
            "id": "plan",
            "name": "Plan",
            "status": "product",
            "use": "New chat -> Plan -> outline only",
        },
        {
            "id": "desktop",
            "name": "Open apps on this PC",
            "status": "product",
            "use": "Ask an authorized agent to open apps or links",
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
            "use": "Optional scientific and spectral compute",
            "api": ["GET /v1/mesie", "GET /v1/stack"],
        },
        {
            "id": "fusion_rfe",
            "name": "Screen understanding",
            "status": "product",
            "use": "Read the live desktop for authorized agent actions",
            "api": ["GET /v1/vision/page", "POST /v1/rfe/synthesize"],
        },
        {
            "id": "subagent_mesh",
            "name": "Background helpers",
            "status": "product",
            "use": "Helpers coordinate bounded work in the background",
            "api": ["GET /v1/protocols/mesh", "POST /v1/hooks/mesh", "POST /v1/subagents/dispatch", "GET /v1/mesh"],
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
        {"id": "term", "name": "Terminal", "status": "product", "use": "Interactive shell for authorized administrators"},
        {"id": "deploy", "name": "Local deploys", "status": "product", "use": "Ship static sites and small services on an authorized host"},
        {"id": "upload", "name": "File upload", "status": "product", "use": "Upload files into the caller's workspace"},
        {"id": "stream", "name": "Live responses", "status": "product", "use": "Watch answers update while work runs"},
        {
            "id": "node_transfer",
            "name": "Device transfer",
            "status": "product",
            "use": "Pair devices with a code and send encrypted files",
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
            "status": "product-surface-hardware-claims-separate",
            "use": "Responsive phone surface and separately evidenced hardware concepts",
            "api": ["GET /phone", "GET /v1/hardware", "GET /v1/device"],
        },
        {"id": "safety", "name": "Safety layer", "status": "product", "use": "Auth, allowlists, audit log, rate limits, approvals, and evidence boundaries"},
        {"id": "credits", "name": "POCK / NEXUS metering", "status": "product", "use": "Meter jobs and connect entitlements or subscriptions"},
        {
            "id": "headless_agents",
            "name": "Headless agent fleet",
            "status": "product",
            "use": "Researcher, planner, coder, squad, security, and other bounded agents",
            "api": ["GET /v1/ai/agents", "POST /v1/ai/agents/{id}/run"],
        },
        {
            "id": "ai_api",
            "name": "POCKET AI API",
            "status": "product",
            "use": "Scoped API keys, chat, jobs, quotas, and metering for integrations",
            "api": ["GET /v1/ai", "POST /v1/ai/chat", "POST /v1/ai/keys", "POST /v1/ai/jobs"],
            "sell": {"starter_usd": 29, "pro_usd": 99, "enterprise_usd": 299},
        },
    ]


def doctor() -> Dict[str, Any]:
    """Product readiness report with source, local, and deployment evidence separated."""
    from pocket.auth import ACCESS_NOTE, expected_user
    from pocket.nexus_bridge import nexus_available
    from pocket.safety import policy_summary

    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "", evidence_class: str = "E1-source"):
        checks.append({"name": name, "ok": ok, "detail": detail, "evidence_class": evidence_class})

    py = os.environ.get("POCKET_PYTHON") or shutil.which("python") or ""
    add("python", bool(py), py, "E2-execution-log" if py else "E0-assertion")
    add("codex_cli", bool(shutil.which("codex")), shutil.which("codex") or "missing", "E2-execution-log" if shutil.which("codex") else "E0-assertion")
    g = shutil.which("grok") or ""
    if not g:
        gp = Path.home() / ".grok" / "bin" / "grok.exe"
        g = str(gp) if gp.exists() else ""
    add("grok_cli", bool(g), g or "missing", "E2-execution-log" if g else "E0-assertion")
    add("access_file", ACCESS_NOTE.exists(), str(ACCESS_NOTE), "E1-source")
    nx = nexus_available()
    add("nexus", bool(nx.get("ok")), nx.get("root") or "", "E2-execution-log" if nx.get("ok") else "E1-source")
    add("cloudflared_legacy_tunnel", bool(shutil.which("cloudflared") or Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe").exists()), "optional legacy tunnel; independent Cloud account is a separate deployment", "E2-execution-log")
    pub = (os.environ.get("POCKET_PUBLIC_URL") or "").strip()
    add("public_url_env", pub.startswith("http"), pub or "unset", "E1-source")
    contract = product_contract()
    contract_errors = validate_contract(contract)
    add("corpus_architecture_contract", not contract_errors, "; ".join(contract_errors) or "pocket.triform-product.v1", "E3-validated-output")

    ok_n = sum(1 for check in checks if check["ok"])
    return {
        "ok": ok_n >= 5 and not contract_errors,
        "product": PRODUCT_NAME,
        "version": VERSION,
        "line": PRODUCT_LINE,
        "company": COMPANY,
        "lab": LAB,
        "org": ORG,
        "edition": EDITION,
        "corpus": "medina.corpus-architectura.v2@2.1.0",
        "ready_score": f"{ok_n}/{len(checks)}",
        "checks": checks,
        "architecture": contract,
        "features": feature_matrix(),
        "safety": policy_summary(),
        "auth_user": expected_user(),
        "start": "Installed: POCKET / POCKET Local / POCKET Edge / POCKET Cloud. Source checkout: python -m pocket serve.",
        "github": "https://github.com/ItsNotAILABS/pocket",
        "phone": pub or "Cloud account or authorized local/LAN body",
        "claim_boundary": "doctor reports observed local state; it does not prove a production Cloudflare deployment or clean customer installation",
    }
