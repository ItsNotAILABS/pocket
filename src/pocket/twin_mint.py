"""Per-account digital twin: files, vault, Pocket vault, embedded CLIs, PhoneAI agents.

On signup/login we mint a workspace on THIS PC (the account's files — never founder
OneDrive). PhoneAI agents live inside it and talk through `bin/` CLI shims.
Vaults are encrypted at rest. A second vault copies envelopes into Pocket.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.platform_space import tenant_root

SUBS = ("twin", "vault", "pocket_vault", "agents", "bin", "files", "local")


def _key(user: str) -> bytes:
    secret = (os.environ.get("POCKET_TWIN_SECRET") or "pocket-twin-v1").encode()
    return hashlib.pbkdf2_hmac("sha256", (user or "seat").encode(), secret, 80_000, dklen=32)


def encrypt_bytes(user: str, raw: bytes) -> Dict[str, str]:
    nonce = secrets.token_bytes(16)
    key = _key(user)
    # stream from HMAC(key, nonce||counter)
    out = bytearray()
    i = 0
    while len(out) < len(raw):
        block = hmac.new(key, nonce + i.to_bytes(8, "big"), hashlib.sha256).digest()
        out.extend(block)
        i += 1
    ct = bytes(a ^ b for a, b in zip(raw, bytes(out[: len(raw)])))
    import base64

    return {
        "alg": "hmac-sha256-ctr-v1",
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ct": base64.b64encode(ct).decode("ascii"),
    }


def decrypt_bytes(user: str, blob: Dict[str, Any]) -> bytes:
    import base64

    nonce = base64.b64decode(blob.get("nonce") or "")
    ct = base64.b64decode(blob.get("ct") or "")
    key = _key(user)
    out = bytearray()
    i = 0
    while len(out) < len(ct):
        block = hmac.new(key, nonce + i.to_bytes(8, "big"), hashlib.sha256).digest()
        out.extend(block)
        i += 1
    return bytes(a ^ b for a, b in zip(ct, bytes(out[: len(ct)])))


def mint(user: str) -> Dict[str, Any]:
    """Create (or refresh) the account's twin workspace + embedded CLIs."""
    user = (user or "").strip().lower()
    if not user:
        return {"ok": False, "error": "user required"}
    root = tenant_root(user)
    for sub in SUBS:
        (root / sub).mkdir(parents=True, exist_ok=True)
    clis: Dict[str, Any] = {}
    try:
        from pocket.model_clis import provision_seat_clis

        clis = provision_seat_clis(user)
    except Exception as e:
        clis = {"ok": False, "error": str(e)[:160]}
    agents_md = root / "AGENTS.md"
    if not agents_md.exists():
        agents_md.write_text(
            f"# {user} — PhoneAI agents in this twin\n\n"
            "Agents here talk through `bin/` (Grok, Codex, Claude, Gemini, OpenCode, Copilot, …).\n"
            "They never leave this workspace unless you ship them to Pocket vault.\n",
            encoding="utf-8",
        )
    opener = root / ("OPEN.cmd" if os.name == "nt" else "OPEN.sh")
    if os.name == "nt":
        opener.write_text(f'@echo off\r\nexplorer "{root}"\r\n', encoding="utf-8")
    else:
        opener.write_text(f"#!/bin/sh\nopen '{root}' 2>/dev/null || xdg-open '{root}'\n", encoding="utf-8")
    meta = {
        "schema": "pocket.twin.v1",
        "user": user,
        "root": str(root),
        "twin": str(root / "twin"),
        "vault": str(root / "vault"),
        "pocket_vault": str(root / "pocket_vault"),
        "agents": str(root / "agents"),
        "bin": str(root / "bin"),
        "files": str(root / "files"),
        "minted": time.time(),
        "encrypted": True,
        "alg": "hmac-sha256-ctr-v1",
        "clis": clis.get("ready") if isinstance(clis, dict) else None,
    }
    (root / "twin.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    # Pocket-side vault directory for this seat
    pv = Path.home() / ".pocket" / "vaults" / user
    pv.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "twin": meta, "clis": clis, "pocket_vault": str(pv)}


def snapshot(user: str) -> Dict[str, Any]:
    m = mint(user)
    root = Path((m.get("twin") or {}).get("root") or tenant_root(user))
    agents = []
    ad = root / "agents"
    if ad.is_dir():
        for p in sorted(ad.glob("*.json")):
            try:
                agents.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue
    bins = []
    bdir = root / "bin"
    if bdir.is_dir():
        bins = [x.name for x in bdir.iterdir() if x.is_file()][:40]
    return {
        "ok": True,
        **m,
        "agents": agents,
        "embedded_clis": bins,
        "open": str(root / ("OPEN.cmd" if os.name == "nt" else "OPEN.sh")),
    }


def open_on_pc(user: str) -> Dict[str, Any]:
    """Open the twin on this machine's file explorer (their files)."""
    m = mint(user)
    root = Path(m["twin"]["root"])
    try:
        if os.name == "nt":
            os.startfile(str(root))  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", str(root)])
        return {"ok": True, "opened": str(root), "how": "explorer"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200], "path": str(root)}


def vault_put(user: str, name: str, text: str, *, to_pocket: bool = True) -> Dict[str, Any]:
    user = (user or "").strip().lower()
    name = Path(name or "note.md").name
    if ".." in name:
        return {"ok": False, "error": "bad name"}
    raw = (text or "").encode("utf-8")
    blob = encrypt_bytes(user, raw)
    root = tenant_root(user)
    dest = root / "vault" / (name + ".vault.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(blob, indent=2), encoding="utf-8")
    pocket = None
    if to_pocket:
        pdir = Path.home() / ".pocket" / "vaults" / user
        pdir.mkdir(parents=True, exist_ok=True)
        pdest = pdir / dest.name
        pdest.write_text(dest.read_text(encoding="utf-8"), encoding="utf-8")
        twin_p = root / "pocket_vault" / dest.name
        twin_p.parent.mkdir(parents=True, exist_ok=True)
        twin_p.write_text(dest.read_text(encoding="utf-8"), encoding="utf-8")
        pocket = str(pdest)
    return {"ok": True, "vault": str(dest), "pocket_vault": pocket, "bytes": len(raw)}


def vault_get(user: str, name: str) -> Dict[str, Any]:
    name = Path(name or "").name
    if not name.endswith(".vault.json"):
        name = name + ".vault.json"
    fp = tenant_root(user) / "vault" / name
    if not fp.is_file():
        alt = Path.home() / ".pocket" / "vaults" / user / name
        fp = alt if alt.is_file() else fp
    if not fp.is_file():
        return {"ok": False, "error": "not found"}
    blob = json.loads(fp.read_text(encoding="utf-8"))
    raw = decrypt_bytes(user, blob)
    return {"ok": True, "name": name, "text": raw.decode("utf-8", errors="replace")}


def create_agent(user: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """PhoneAI agent that talks through embedded workspace CLIs."""
    mint(user)
    aid = "".join(ch for ch in str(body.get("id") or body.get("name") or "").lower() if ch.isalnum() or ch in "-_")[:40]
    if len(aid) < 2:
        return {"ok": False, "error": "agent id required"}
    rec = {
        "id": aid,
        "name": str(body.get("name") or aid)[:60],
        "role": str(body.get("role") or "workspace-agent")[:120],
        "blurb": str(body.get("blurb") or body.get("prompt") or "")[:800],
        "engine": str(body.get("engine") or "grok")[:32],
        "cli": str(body.get("cli") or body.get("engine") or "grok")[:32],
        "talks_to": "phoneai",
        "workspace": str(tenant_root(user)),
        "created": time.time(),
    }
    fp = tenant_root(user) / "agents" / f"{aid}.json"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    try:
        from pocket.agent_network import develop

        develop({**rec, "id": aid})
    except Exception:
        pass
    return {"ok": True, "agent": rec, "path": str(fp)}


def run_agent(user: str, aid: str, prompt: str = "") -> Dict[str, Any]:
    """Run an agent with PATH = twin/bin so it uses embedded CLIs."""
    root = tenant_root(user)
    fp = root / "agents" / f"{aid}.json"
    if not fp.is_file():
        return {"ok": False, "error": "agent not in twin"}
    rec = json.loads(fp.read_text(encoding="utf-8"))
    text = (prompt or rec.get("blurb") or rec.get("role") or aid).strip()
    bindir = str(root / "bin")
    env = {**os.environ, "PATH": bindir + os.pathsep + os.environ.get("PATH", ""), "POCKET_TWIN": str(root), "POCKET_USER": user}
    engine = rec.get("cli") or rec.get("engine") or "grok"
    shim = root / "bin" / (engine + (".cmd" if os.name == "nt" else ""))
    if shim.is_file() and engine in ("grok", "claude", "gemini"):
        cmd = [str(shim), "-p", text[:4000]] if engine != "grok" else None
        if engine == "grok":
            cmd = [str(shim), "--single", text[:4000], "--cwd", str(root / "twin"), "--max-turns", "3", "--always-approve", "--output-format", "plain"]
        try:
            r = subprocess.run(
                cmd,
                cwd=str(root / "twin"),
                capture_output=True,
                text=True,
                timeout=90,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            out = ((r.stdout or "") + (r.stderr or "")).strip()
            vault_put(user, f"agent-{aid}-last.md", out[:8000], to_pocket=True)
            return {"ok": r.returncode == 0, "reply": out[-6000:], "via": "embedded-cli", "cli": str(shim), "agent": rec}
        except Exception as e:
            return {"ok": False, "error": str(e)[:200], "agent": rec}
    try:
        from pocket.phoneai_bridge import ask_engine

        r = ask_engine(text, engine=engine)
        vault_put(user, f"agent-{aid}-last.md", str(r.get("reply") or r.get("error") or ""), to_pocket=True)
        r["via"] = "host-engine"
        r["agent"] = rec
        return r
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
