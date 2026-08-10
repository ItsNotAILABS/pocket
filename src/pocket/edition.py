"""Founder (internal) vs public product face.

Founder tree (this machine, your daily POCKET):
  - Runs for you on localhost
  - Git is local-only (never origin → public GitHub)
  - Default links stay local

Public face (marketing / customers):
  - github.com/ItsNotAILABS/pocket  — only when YOU deliberately ship
  - pocket.medinatechlabs.net       — optional public host, not your daily desk

Never mix “I’m building” with “users see this.” Ship is a deliberate promote step.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

HOME = Path.home() / ".pocket"
FOUNDER_ENV = HOME / "founder.env"
ACCESS_ENV = HOME / "access.env"

# Public product face (customers / marketing) — not where you work day to day
PUBLIC_GITHUB = "https://github.com/ItsNotAILABS/pocket"
PUBLIC_MARKETING_HOST = "https://pocket.medinatechlabs.net"
LOCAL_APP = "http://127.0.0.1:8787"


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception:
        pass


def ensure_founder_env() -> Path:
    """Write default founder.env once so this tree stays internal-first."""
    HOME.mkdir(parents=True, exist_ok=True)
    if not FOUNDER_ENV.is_file():
        FOUNDER_ENV.write_text(
            "# POCKET founder (internal) — not the public product face\n"
            "# This file is loaded on host start. Do not commit secrets.\n"
            "POCKET_EDITION=founder\n"
            "POCKET_PUBLIC_URL=http://127.0.0.1:8787\n"
            "POCKET_MARKETING_URL=https://pocket.medinatechlabs.net\n"
            "POCKET_HIDE_PUBLIC_GITHUB=1\n"
            "POCKET_PUBLIC_LOCK=1\n"
            "# Keep daily desk local. Enable tunnel only when you choose:\n"
            "# POCKET_PUBLIC_URL=https://pocket.medinatechlabs.net\n",
            encoding="utf-8",
        )
    return FOUNDER_ENV


def bootstrap_edition() -> None:
    """Load founder + access env without overriding already-set process env."""
    ensure_founder_env()
    _load_env_file(FOUNDER_ENV)
    _load_env_file(ACCESS_ENV)
    # Default edition if still unset
    if not (os.environ.get("POCKET_EDITION") or "").strip():
        os.environ["POCKET_EDITION"] = "founder"
    # Founder default: app URL is local unless they explicitly set public
    if not (os.environ.get("POCKET_PUBLIC_URL") or "").strip():
        os.environ["POCKET_PUBLIC_URL"] = LOCAL_APP


def is_founder() -> bool:
    v = (os.environ.get("POCKET_EDITION") or "founder").strip().lower()
    return v in ("founder", "internal", "owner", "private", "lab")


def is_public_face() -> bool:
    return not is_founder()


def app_url() -> str:
    """Where THIS running instance is (founder desk = almost always localhost)."""
    return (os.environ.get("POCKET_PUBLIC_URL") or LOCAL_APP).strip().rstrip("/") or LOCAL_APP


def marketing_url() -> str:
    """Customer-facing host — separate from your daily desk."""
    return (
        (os.environ.get("POCKET_MARKETING_URL") or PUBLIC_MARKETING_HOST).strip().rstrip("/")
        or PUBLIC_MARKETING_HOST
    )


def public_github() -> Optional[str]:
    """Public product repo for marketing pages. Hidden on founder desk by default."""
    if is_founder() and (os.environ.get("POCKET_HIDE_PUBLIC_GITHUB") or "1").strip() not in (
        "0",
        "false",
        "no",
        "off",
    ):
        return None
    return (os.environ.get("POCKET_PUBLIC_GITHUB") or PUBLIC_GITHUB).strip() or PUBLIC_GITHUB


def desk_url() -> str:
    return app_url().rstrip("/") + "/desk"


def summary() -> Dict[str, Any]:
    return {
        "ok": True,
        "edition": "founder" if is_founder() else "public",
        "app_url": app_url(),
        "desk_url": desk_url(),
        "marketing_url": marketing_url(),
        "public_github": public_github(),
        "public_github_visible": public_github() is not None,
        "founder_env": str(FOUNDER_ENV),
        "doctrine": (
            "Founder tree = your daily product. "
            "Public GitHub + marketing host = customer face only. "
            "Ship is deliberate; daily work is not auto-published."
        ),
        "links_separated": app_url().rstrip("/") != marketing_url().rstrip("/"),
    }
