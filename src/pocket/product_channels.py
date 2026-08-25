"""Canonical POCKET product channels.

Research papers specify the architecture. This module describes how people buy,
open, and operate its three product bodies without conflating a local server, a
Cloudflare account, and a browser shell.
"""
from __future__ import annotations

from typing import Any, Dict

from pocket import LAB, PRODUCT, __version__
from pocket.corpus_architecture import product_contract, validate_contract


def channels() -> Dict[str, Any]:
    contract = product_contract()
    errors = validate_contract(contract)
    return {
        "ok": not errors,
        "product": PRODUCT,
        "version": __version__,
        "lab": LAB,
        "schema": "pocket.product-channels.v3",
        "corpus_contract": "medina.corpus-architectura.v2@2.1.0",
        "validation_errors": errors,
        "architecture": contract,
        "decision": {
            "for_you_now": "Install POCKET Desktop once. Open POCKET, POCKET Local, POCKET Edge, or POCKET Cloud from ordinary Windows shortcuts.",
            "for_users": [
                "POCKET Cloud account for organizations, seats, entitlements, downloads, durable tasks, and paired devices",
                "POCKET Desktop for a bundled local execution engine, files, models, agents, and private computation",
                "POCKET Edge for an app-style Microsoft Edge surface over the local runtime or cloud account",
            ],
            "not": "The product must not depend on a developer terminal, a manually started source checkout, or one laptop remaining online.",
        },
        "bodies": contract["triform_product"]["bodies"],
        "channels": [
            {
                "id": "cloud_account",
                "body_id": "cloud-account",
                "name": "POCKET Cloud",
                "who": "Organizations, teams, account holders, and paired devices",
                "what": "Independent Cloudflare account plane for identity, organizations, entitlements, releases, durable queues, and device coordination.",
                "how_start": ["Create or join an organization", "Sign in from any device", "Download an entitled desktop release", "Optionally pair a local computer with a one-time code"],
                "url_hint": "https://app.pocket.medinatechlabs.net",
                "availability": "independent of local desktop uptime",
                "status": "source-implemented; production deployment receipt required",
                "claim_boundary": "Cloud source and D1/R2 schemas do not prove a live production route.",
            },
            {
                "id": "desktop",
                "body_id": "desktop-runtime",
                "name": "POCKET Desktop",
                "who": "Owners, operators, and users who install POCKET on Windows",
                "what": "Electron application with a bundled loopback POCKET engine, tray mode, start-at-login, private local files, models, agents, and runtime cells.",
                "how_start": ["Install POCKET-Setup for x64 or ARM64", "Open the POCKET shortcut", "Use POCKET Local for the bundled local body", "Use POCKET Cloud for the independent account body"],
                "url_local": "http://127.0.0.1:8787/desk",
                "download": {"account_page": "/get", "release_api": "/api/releases", "legacy_host_page": "/download"},
                "lifecycle": "reuse healthy engine; start when absent; never kill an unknown listener",
                "status": "packaging-and-source-verified; signed public release evidence required",
            },
            {
                "id": "web_edge",
                "body_id": "edge-app",
                "name": "POCKET Edge",
                "who": "Windows users who prefer Microsoft Edge app mode",
                "what": "Dedicated app-style Edge window. It starts or reuses the bundled local engine, or opens the Cloud account; it is not a separate product brain.",
                "how_start": ["Open the POCKET Edge desktop or Start-menu shortcut", "The launcher verifies or starts the local body", "Microsoft Edge opens with --app against the selected trusted origin"],
                "url_local": "http://127.0.0.1:8787/desk",
                "url_cloud_hint": "https://app.pocket.medinatechlabs.net/desk",
                "status": "installer-contract-implemented; clean-install evidence required",
            },
            {
                "id": "api",
                "name": "POCKET API and Device Relay",
                "who": "Applications, automations, approved agents, and paired computers",
                "what": "Versioned HTTP capabilities with tenant-aware sessions, scoped API keys, quotas, durable task references, and receipts.",
                "how_start": ["Use a user session, scoped API key, or restricted device credential", "Discover capabilities before invoking them", "Use the cloud relay for queued paired-device work"],
                "url_local": "http://127.0.0.1:8787/v1/api",
                "status": "source-implemented; route-specific deployment and integration evidence required",
            },
            {
                "id": "phone",
                "name": "POCKET Phone",
                "who": "Mobile users and phone-native clients",
                "what": "Responsive account and task surface. Local device execution remains a separately authorized body.",
                "how_start": ["Open the Cloud account or an authorized local/LAN body", "Sign in with your own account"],
                "status": "product-surface; native mobile capability evidence is separate",
            },
        ],
        "presentation_for_users": {
            "primary": "Account -> entitlement -> installer -> POCKET / POCKET Local / POCKET Edge / POCKET Cloud shortcuts",
            "secondary": "Scoped API keys and paired-device work for integrations",
            "avoid": "Leading with a research journal, a localhost command, or a tunnel that dies with the operator machine",
            "demo_path": "Create account -> download installer -> open POCKET Edge -> complete a local task -> inspect its receipt from the Cloud account",
        },
        "api": {
            "channels_and_architecture": "GET /v1/product/channels",
            "catalog": "GET /v1/api",
            "health": "GET /health",
            "desktop_releases": "GET /v1/desktop/releases",
            "cloud_releases": "GET /api/releases",
        },
    }


def user_home_brief() -> Dict[str, Any]:
    value = channels()
    return {
        "ok": value["ok"],
        "headline": "POCKET Cloud + Desktop + Edge",
        "for_you": value["decision"]["for_you_now"],
        "open": {"local_desk": "http://127.0.0.1:8787/desk", "cloud_account": "https://app.pocket.medinatechlabs.net", "channels_and_architecture": "/v1/product/channels"},
        "version": __version__,
    }
