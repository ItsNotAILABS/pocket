"""POCKET LIGHT — workspace shell. One thread per checkout. Not the desk."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / ".pocket" / "pocket-light"
STATE = ROOT / "state.json"
SCHEMA = "pocket.light.v1"
APP = "/pocket-light"

AGENTS = ("grok", "codex", "claude", "spark", "rah", "jev")

THREADS: List[Dict[str, str]] = [
    {
        "id": "senda",
        "title": "Senda / Stocklana",
        "cwd": r"C:\Users\Medin\Stocklana",
        "blurb": "Senda is the public front. Stocklana keeps the books.",
    },
    {
        "id": "launch-desk",
        "title": "Launch desk",
        "cwd": r"C:\Users\Medin\Documents\GitHub\launch-desk",
        "blurb": "Pons launches and the PreStocks mark desk.",
    },
    {
        "id": "metropolis",
        "title": "Monad Metropolis",
        "cwd": r"C:\Users\Medin\Documents\GitHub\Monad-Hackaton",
        "blurb": "MonadBuilder+ and THESIS. Branch ship-metropolis.",
    },
    {
        "id": "parallax",
        "title": "PARALLAX",
        "cwd": r"E:\PARALLAX-Exchange-Clearinghouse",
        "blurb": "Clearing, netting, and receipt-linked ledgers.",
    },
    {
        "id": "pocket",
        "title": "Pocket",
        "cwd": r"C:\Users\Medin\OneDrive\pocket-os",
        "blurb": "The host OS. This shell is a second app on it.",
    },
    {
        "id": "self-tools",
        "title": "self.tools",
        "cwd": r"C:\Users\Medin\.pocket\workspaces\self.tools",
        "blurb": "Taskmanager board on the subdomain fork.",
    },
    {
        "id": "spark",
        "title": "Spark Group",
        "cwd": r"C:\Users\Medin\.pocket\workspaces\spark-group",
        "blurb": "Group model app. Handoffs, not the desk.",
    },
    {
        "id": "auro",
        "title": "AURO",
        "cwd": r"C:\Users\Medin\Auro14B",
        "blurb": "Local model family and organism lanes.",
    },
    {
        "id": "kiln",
        "title": "KILN",
        "cwd": r"E:\KILN",
        "blurb": "Forge workspace with Grok and Codex lanes.",
    },
    {
        "id": "loom",
        "title": "LOOM",
        "cwd": r"C:\Users\Medin\.pocket\loomgraph",
        "blurb": "Pocket loomgraph. Open it from the desk at /loomgraph.",
    },
    {
        "id": "vaul",
        "title": "VAUL",
        "cwd": r"C:\Users\Medin\NOVASVAUL",
        "blurb": "NOVASVAUL is the owner-held vault. Its exit bundle is a CAPSULA sealed-transfer contract (ciphertext only).",
    },
]

_SKIP = {".git", "node_modules", "__pycache__", ".venv", "dist"}


def _blank() -> Dict[str, Any]:
    return {"threads": {}, "loose": []}


def _load() -> Dict[str, Any]:
    ROOT.mkdir(parents=True, exist_ok=True)
    if not STATE.is_file():
        return _blank()
    try:
        data = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return _blank()
    data.setdefault("threads", {})
    data.setdefault("loose", [])
    return data


def _save(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def catalog() -> List[Dict[str, Any]]:
    data = _load()
    rows = []
    for spec in THREADS:
        bucket = data["threads"].get(spec["id"]) or {}
        msgs = bucket.get("messages") or []
        rows.append({**spec, "kind": "project", "messages": len(msgs), "present": Path(spec["cwd"]).is_dir()})
    for spec in data["loose"]:
        bucket = data["threads"].get(spec["id"]) or {}
        rows.append({
            "id": spec["id"],
            "title": spec.get("title") or "Chat",
            "cwd": "",
            "blurb": "Not tied to a checkout.",
            "kind": "loose",
            "messages": len(bucket.get("messages") or []),
            "present": False,
        })
    return rows


def _find(thread_id: str) -> Optional[Dict[str, str]]:
    for spec in THREADS:
        if spec["id"] == thread_id:
            return spec
    for spec in _load()["loose"]:
        if spec.get("id") == thread_id:
            return {"id": spec["id"], "title": spec.get("title") or "Chat", "cwd": "", "blurb": "Not tied to a checkout."}
    return None


def _preview(cwd: str) -> str:
    path = Path(cwd)
    if not cwd or not path.is_dir():
        return "Checkout is not on this machine."
    readme = path / "README.md"
    if readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8", errors="replace").strip()
        except Exception:
            text = ""
        if text:
            return text[:500]
    return "No README in that checkout."


def artifacts(cwd: str) -> List[Dict[str, str]]:
    path = Path(cwd) if cwd else None
    if path is None or not path.is_dir():
        return []
    rows: List[Dict[str, str]] = []
    try:
        names = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except Exception:
        return []
    for child in names:
        if child.name in _SKIP or child.name.startswith("."):
            continue
        rows.append({"name": child.name, "kind": "dir" if child.is_dir() else "file"})
        if len(rows) >= 12:
            break
    return rows


def status() -> Dict[str, Any]:
    return {
        "ok": True,
        "schema": SCHEMA,
        "product": "POCKET LIGHT",
        "app": APP,
        "agents": list(AGENTS),
        "threads": catalog(),
        "note": "Separate shell. One thread per project. Files and previews stay in this page.",
    }


def thread(thread_id: str) -> Dict[str, Any]:
    spec = _find(thread_id)
    if not spec:
        return {"ok": False, "error": "unknown thread"}
    data = _load()
    bucket = data["threads"].get(thread_id) or {}
    cwd = spec.get("cwd") or ""
    return {
        "ok": True,
        "thread": {**spec, "kind": "loose" if not cwd else "project", "present": bool(cwd) and Path(cwd).is_dir()},
        "agent": bucket.get("agent") or "grok",
        "messages": bucket.get("messages") or [],
        "subagents": bucket.get("subagents") or [],
        "artifacts": artifacts(cwd),
        "preview": _preview(cwd) if cwd else "",
    }


def open_loose(title: str) -> Dict[str, Any]:
    title = (title or "").strip()[:80] or "New chat"
    data = _load()
    tid = "chat-" + time.strftime("%H%M%S") + f"{int(time.time() * 1000) % 1000:03d}"
    data["loose"].append({"id": tid, "title": title})
    data["threads"][tid] = {"agent": "grok", "messages": [], "subagents": []}
    _save(data)
    return {"ok": True, "id": tid, "title": title}


def post(thread_id: str, text: str, *, agent: str = "grok") -> Dict[str, Any]:
    spec = _find(thread_id)
    text = (text or "").strip()
    if not spec:
        return {"ok": False, "error": "unknown thread"}
    if not text:
        return {"ok": False, "error": "say something"}
    agent = (agent or "grok").strip().lower()
    if agent not in AGENTS:
        agent = "grok"
    data = _load()
    bucket = data["threads"].setdefault(thread_id, {"agent": agent, "messages": [], "subagents": []})
    bucket["agent"] = agent
    stamp = time.strftime("%H:%M")
    bucket["messages"].append({"role": "you", "agent": "you", "text": text[:4000], "at": stamp})
    cwd = spec.get("cwd") or ""
    preview = _preview(cwd) if cwd else "Loose chat. No checkout."
    files = artifacts(cwd)
    n = len(bucket["subagents"]) + 1
    bucket["subagents"].append({"id": f"files-{n}", "role": "files", "status": "done", "detail": f"{len(files)} names"})
    bucket["subagents"].append({"id": f"preview-{n}", "role": "preview", "status": "done", "detail": preview[:180]})
    reply = f"{agent} seated on {spec.get('title')}.\n{cwd or 'no checkout'}\n{preview}"
    bucket["messages"].append({"role": "agent", "agent": agent, "text": reply[:2000], "at": stamp})
    bucket["messages"] = bucket["messages"][-80:]
    bucket["subagents"] = bucket["subagents"][-24:]
    _save(data)
    view = thread(thread_id)
    view["reply"] = reply[:2000]
    return view
