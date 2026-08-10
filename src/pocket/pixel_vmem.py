"""Pixel Lattice — working memory you can store, look into, recreate, and pass.

Model (product language):
  - Memory is stored as RGB pixel pages (tile × tile × 3 bytes).
  - Named **symbols** point at one or more pages (a chain).
  - You can search, open (look into), recreate the original text/file,
    and pass a symbol to another agent, device, or chat context.

Not GPU VRAM — private, visualizable, content-addressed storage on this host
(with optional mesh + node-transfer handoff).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import math
import os
import re
import time
import zlib
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from pocket.mesh_disk import MESH, VDISK, encrypt_body, decrypt_body, leave_artifact, send_message

ROOT = Path.home() / ".pocket" / "vmem"
PAGES = ROOT / "pages"
EXPORTS = ROOT / "exports"
INDEX = ROOT / "index.json"
LATTICE = VDISK / "pixel_lattice"
HANDOFF = VDISK / "vmem_handoff"
for d in (ROOT, PAGES, EXPORTS, LATTICE, HANDOFF):
    d.mkdir(parents=True, exist_ok=True)

_lock = Lock()

TILE = int(os.environ.get("POCKET_VMEM_TILE") or 64)
PAGE_BYTES = TILE * TILE * 3  # 64² × 3 = 12_288
MAX_PAGES = int(os.environ.get("POCKET_VMEM_MAX_PAGES") or 512)


def page_capacity() -> int:
    return PAGE_BYTES


def _safe_sym(symbol: str) -> str:
    s = (symbol or "").strip().replace("\\", "/")
    s = re.sub(r"[^A-Za-z0-9._/\-]+", "_", s)
    return s[:120] or f"mem/{int(time.time())}"


def _load_index() -> Dict[str, Any]:
    try:
        if INDEX.is_file():
            return json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {
        "pages": {},
        "symbols": {},
        "workspaces": {},
        "recent": [],
        "created_at": time.time(),
    }


def _save_index(idx: Dict[str, Any]) -> None:
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    tmp = INDEX.with_suffix(".tmp")
    tmp.write_text(json.dumps(idx, indent=2, default=str), encoding="utf-8")
    tmp.replace(INDEX)


def _bytes_to_pixels(data: bytes) -> bytes:
    if len(data) > PAGE_BYTES:
        data = data[:PAGE_BYTES]
    if len(data) < PAGE_BYTES:
        data = data + b"\x00" * (PAGE_BYTES - len(data))
    return data


def _page_id(pix: bytes) -> str:
    return hashlib.sha256(pix).hexdigest()[:32]


def _text_preview(data: bytes, n: int = 240) -> str:
    try:
        return data[:n].decode("utf-8")
    except Exception:
        return data[:n].decode("utf-8", errors="replace")


def _looks_text(data: bytes) -> bool:
    if not data:
        return True
    sample = data[:800]
    # high ratio of printable / whitespace
    ok = sum(1 for b in sample if 32 <= b < 127 or b in (9, 10, 13))
    return ok / max(1, len(sample)) > 0.85


def status() -> Dict[str, Any]:
    idx = _load_index()
    pages = idx.get("pages") or {}
    symbols = idx.get("symbols") or {}
    total = sum(int(p.get("stored_bytes") or 0) for p in pages.values())
    return {
        "ok": True,
        "kind": "pixel-lattice",
        "product": "Private pixel memory",
        "tile": TILE,
        "page_bytes": PAGE_BYTES,
        "pages": len(pages),
        "symbols": len(symbols),
        "workspaces": len(idx.get("workspaces") or {}),
        "stored_bytes": total,
        "recent": (idx.get("recent") or [])[:8],
        "root": str(ROOT),
        "lattice": str(LATTICE),
        "exports": str(EXPORTS),
        "mesh_root": str(MESH),
        "can": [
            "store (text/files as pixel pages)",
            "look into (open / search)",
            "recreate (rebuild original text or file)",
            "pass (agent, device, clipboard handoff)",
        ],
        "doctrine": "Work memory as pixels — store, look up, recreate, pass on.",
    }


def put_bytes(
    data: bytes,
    *,
    symbol: str = "",
    workspace: str = "default",
    kind: str = "",
    tags: Optional[List[str]] = None,
    replicate_mesh: bool = True,
    note: str = "",
    pass_to: str = "",
) -> Dict[str, Any]:
    """Store bytes as pixel pages under a symbol. Returns handles + optional pass result."""
    raw = data or b""
    if not raw:
        return {"ok": False, "error": "empty"}
    n_pages = max(1, math.ceil(len(raw) / PAGE_BYTES))
    if n_pages > MAX_PAGES:
        return {"ok": False, "error": f"too large ({n_pages} pages); max {MAX_PAGES}"}

    if not kind:
        kind = "text" if _looks_text(raw) else "binary"
    ws = (workspace or "default").strip()[:64] or "default"
    tag_list = [str(t).strip()[:40] for t in (tags or []) if str(t).strip()][:12]
    preview = _text_preview(raw) if kind == "text" else f"[{kind} {len(raw)} bytes]"

    handles: List[Dict[str, Any]] = []
    with _lock:
        idx = _load_index()
        for i in range(n_pages):
            chunk = raw[i * PAGE_BYTES : (i + 1) * PAGE_BYTES]
            pix = _bytes_to_pixels(chunk)
            pid = _page_id(pix)
            packed = zlib.compress(pix, 6)
            cipher = encrypt_body(base64.b64encode(packed).decode("ascii"))
            path = PAGES / f"{pid}.page.json"
            rec = {
                "page_id": pid,
                "tile": TILE,
                "stored_bytes": len(chunk),
                "page_bytes": PAGE_BYTES,
                "cipher": cipher,
                "sha256": hashlib.sha256(chunk).hexdigest(),
                "created_at": time.time(),
                "note": (note or "")[:200],
                "index": i,
                "kind": kind,
            }
            path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
            rgb_path = LATTICE / f"{pid}.rgb"
            rgb_path.write_bytes(pix)
            idx["pages"][pid] = {
                "page_id": pid,
                "path": str(path),
                "rgb": str(rgb_path),
                "stored_bytes": len(chunk),
                "sha256": rec["sha256"],
                "created_at": rec["created_at"],
                "index": i,
                "kind": kind,
            }
            handles.append({"page_id": pid, "bytes": len(chunk), "index": i})

        chain_id = hashlib.sha256(("".join(h["page_id"] for h in handles)).encode()).hexdigest()[:24]
        sym = _safe_sym(symbol or f"{ws}/{chain_id[:10]}")
        entry = {
            "chain_id": chain_id,
            "pages": [h["page_id"] for h in handles],
            "total_bytes": len(raw),
            "kind": kind,
            "workspace": ws,
            "tags": tag_list,
            "note": (note or "")[:300],
            "preview": preview[:240],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "updated_at": time.time(),
            "created_at": time.time(),
        }
        # preserve first created_at if updating
        old = (idx.get("symbols") or {}).get(sym)
        if old and old.get("created_at"):
            entry["created_at"] = old["created_at"]
        idx.setdefault("symbols", {})[sym] = entry
        # workspace index
        wset = idx.setdefault("workspaces", {}).setdefault(ws, {"symbols": []})
        if sym not in wset["symbols"]:
            wset["symbols"] = ([sym] + list(wset.get("symbols") or []))[:200]
        # recent
        recent = [r for r in (idx.get("recent") or []) if r.get("symbol") != sym]
        recent.insert(
            0,
            {
                "symbol": sym,
                "kind": kind,
                "bytes": len(raw),
                "preview": preview[:120],
                "at": time.time(),
            },
        )
        idx["recent"] = recent[:40]
        idx["updated_at"] = time.time()
        _save_index(idx)

    if replicate_mesh:
        try:
            leave_artifact(
                "REPOSITOR",
                f"vmem_{sym.replace('/', '_')[:40]}.md",
                (
                    f"# Memory saved\n\n"
                    f"- symbol: `{sym}`\n"
                    f"- bytes: {len(raw)}\n"
                    f"- pages: {len(handles)}\n"
                    f"- workspace: {ws}\n"
                    f"- kind: {kind}\n"
                    f"- preview: {preview[:160]}\n"
                ),
                notify=["ARCHON", "USER"],
            )
        except Exception:
            pass

    out: Dict[str, Any] = {
        "ok": True,
        "symbol": sym,
        "chain_id": chain_id,
        "pages": handles,
        "total_bytes": len(raw),
        "kind": kind,
        "workspace": ws,
        "tags": tag_list,
        "preview": preview[:200],
        "tile": TILE,
        "how": {
            "look": f"GET /v1/vmem/look?symbol={sym}",
            "recreate": f"POST /v1/vmem/recreate {{symbol:'{sym}'}}",
            "pass": f"POST /v1/vmem/pass {{symbol:'{sym}', to:'agent|device|context'}}",
        },
    }

    if pass_to:
        out["pass"] = pass_info(sym, to=pass_to)

    return out


def put_text(text: str, *, symbol: str = "", **kw: Any) -> Dict[str, Any]:
    kw.setdefault("kind", "text")
    return put_bytes((text or "").encode("utf-8"), symbol=symbol, **kw)


def put_json(obj: Any, *, symbol: str = "", **kw: Any) -> Dict[str, Any]:
    kw.setdefault("kind", "json")
    raw = json.dumps(obj, indent=2, default=str).encode("utf-8")
    return put_bytes(raw, symbol=symbol, **kw)


def put_artifact(
    content: str,
    *,
    title: str = "",
    language: str = "text",
    agent: str = "",
    agent_role: str = "",
    ai_version: str = "",
    run_id: str = "",
    tags: Optional[List[str]] = None,
    workspace: str = "artifacts",
    note: str = "",
) -> Dict[str, Any]:
    """First-class agent artifact → pixel lattice (store · look · recreate · pass).

    Symbols live under ``artifacts/{run_id}/{agent}/{slug}`` so the desk can
    list, open pixel maps, recreate files, and pass into other agents.
    """
    body = (content or "").strip()
    if not body:
        return {"ok": False, "error": "empty artifact"}
    lang = re.sub(r"[^a-z0-9+#.\-]", "", (language or "text").lower())[:24] or "text"
    slug_src = title or f"artifact-{int(time.time())}"
    slug = re.sub(r"[^A-Za-z0-9._\-]+", "-", slug_src).strip("-")[:64] or "artifact"
    rid = re.sub(r"[^A-Za-z0-9_\-]+", "", (run_id or str(int(time.time()))))[:20] or "run"
    agent_slug = re.sub(r"[^A-Za-z0-9_\-]+", "", (agent or "agent").lower())[:32] or "agent"
    symbol = f"artifacts/{rid}/{agent_slug}/{slug}"
    # Envelope so recreate/look know agent provenance
    header = (
        f"<!-- pocket.artifact.v1 agent={agent_slug} role={agent_role} "
        f"ai={ai_version or 'local'} lang={lang} title={title or slug} -->\n"
    )
    if lang in ("ts", "typescript", "js", "javascript", "py", "python", "json", "md", "bash", "sh"):
        fence = "typescript" if lang in ("ts", "typescript") else (
            "javascript" if lang in ("js", "javascript") else (
                "python" if lang in ("py", "python") else lang
            )
        )
        if f"```{fence}" not in body and "```" not in body[:20]:
            packed = f"{header}```{fence}\n{body}\n```\n"
        else:
            packed = header + body + ("\n" if not body.endswith("\n") else "")
    else:
        packed = header + body + ("\n" if not body.endswith("\n") else "")

    tag_list = list(tags or [])
    for t in ("artifact", lang, agent_slug, "swarm"):
        if t and t not in tag_list:
            tag_list.append(t)
    r = put_text(
        packed,
        symbol=symbol,
        workspace=workspace or "artifacts",
        kind="artifact",
        tags=tag_list[:12],
        note=(note or title or f"by {agent_slug}")[:300],
        replicate_mesh=True,
    )
    if r.get("ok"):
        r["artifact"] = {
            "title": title or slug,
            "language": lang,
            "agent": agent_slug,
            "agent_role": agent_role,
            "ai_version": ai_version or "",
            "run_id": rid,
            "symbol": r.get("symbol"),
            "view": f"/v1/vmem/look?symbol={r.get('symbol')}",
            "recreate": f"/v1/vmem/recreate",
            "map": (r.get("how") or {}).get("look"),
        }
    return r


def list_artifacts(*, limit: int = 40, agent: str = "", run_id: str = "") -> Dict[str, Any]:
    """List pixel symbols that are agent artifacts (multi-way memory browser)."""
    idx = _load_index()
    items = []
    for sym, meta in (idx.get("symbols") or {}).items():
        kind = (meta.get("kind") or "").lower()
        tags = [str(t).lower() for t in (meta.get("tags") or [])]
        is_art = kind == "artifact" or "artifact" in tags or sym.startswith("artifacts/")
        if not is_art:
            continue
        if agent and agent.lower() not in sym.lower() and agent.lower() not in tags:
            continue
        if run_id and run_id not in sym:
            continue
        items.append(
            {
                "symbol": sym,
                "kind": meta.get("kind") or "artifact",
                "bytes": meta.get("total_bytes"),
                "preview": meta.get("preview"),
                "note": meta.get("note"),
                "tags": meta.get("tags") or [],
                "workspace": meta.get("workspace"),
                "updated_at": meta.get("updated_at"),
                "pages": meta.get("pages") or [],
            }
        )
    items.sort(key=lambda h: -(h.get("updated_at") or 0))
    return {
        "ok": True,
        "count": len(items),
        "artifacts": items[: max(1, min(limit, 100))],
        "can": ["store", "look", "recreate", "pass", "map"],
    }


def store_agent_run(
    *,
    agent: str,
    mode: str,
    prompt: str,
    result: str,
    job_id: str = "",
    language: str = "md",
) -> Dict[str, Any]:
    """Persist any agent turn into pixel memory (first-class agentic loop)."""
    title = (prompt or "run").strip().split("\n")[0][:80] or "agent-run"
    # Prefer fenced code language if present
    lang = language
    m = re.search(r"```([a-zA-Z0-9_+#.\-]*)", result or "")
    if m and m.group(1):
        lang = m.group(1)
    return put_artifact(
        result or "",
        title=title,
        language=lang,
        agent=agent or mode or "agent",
        agent_role=mode or "agent",
        ai_version=mode or "",
        run_id=job_id or f"job{int(time.time())}",
        tags=["agent-run", mode or "agent"],
        note=f"auto-saved from {mode or agent}",
    )


def get_page(page_id: str) -> Dict[str, Any]:
    pid = (page_id or "").strip()
    path = PAGES / f"{pid}.page.json"
    if not path.is_file():
        return {"ok": False, "error": "page not found"}
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
        packed_b64 = decrypt_body(rec.get("cipher") or {})
        packed = base64.b64decode(packed_b64.encode("ascii"))
        pix = zlib.decompress(packed)
        stored = int(rec.get("stored_bytes") or PAGE_BYTES)
        data = pix[:stored]
        return {
            "ok": True,
            "page_id": pid,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "data_b64": base64.b64encode(data).decode("ascii"),
            "tile": rec.get("tile") or TILE,
            "kind": rec.get("kind") or "binary",
            "preview": _text_preview(data, 160),
        }
    except Exception as e:
        return {"ok": False, "error": f"read failed: {e}"}


def _load_chain(pages: List[str]) -> Dict[str, Any]:
    chunks: List[bytes] = []
    for pid in pages:
        g = get_page(pid)
        if not g.get("ok"):
            return {"ok": False, "error": f"missing page {pid}", "partial": True, "got": len(chunks)}
        chunks.append(base64.b64decode(g["data_b64"]))
    data = b"".join(chunks)
    return {"ok": True, "data": data}


def get_symbol(symbol: str) -> Dict[str, Any]:
    idx = _load_index()
    sym = _safe_sym(symbol) if symbol else ""
    # exact then case-insensitive
    meta = (idx.get("symbols") or {}).get(sym)
    if not meta:
        for k, v in (idx.get("symbols") or {}).items():
            if k.lower() == (symbol or "").strip().lower():
                sym, meta = k, v
                break
    if not meta:
        return {"ok": False, "error": "symbol not found", "symbol": symbol}
    loaded = _load_chain(meta.get("pages") or [])
    if not loaded.get("ok"):
        return {**loaded, "symbol": sym}
    data: bytes = loaded["data"]
    text = None
    if (meta.get("kind") or "text") in ("text", "json") or _looks_text(data):
        text = data.decode("utf-8", errors="replace")
    return {
        "ok": True,
        "symbol": sym,
        "chain_id": meta.get("chain_id"),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "data_b64": base64.b64encode(data).decode("ascii"),
        "pages": meta.get("pages") or [],
        "kind": meta.get("kind") or "text",
        "workspace": meta.get("workspace") or "default",
        "tags": meta.get("tags") or [],
        "note": meta.get("note") or "",
        "preview": meta.get("preview") or _text_preview(data),
        "text": text,
        "text_preview": (text or _text_preview(data))[:400],
        "updated_at": meta.get("updated_at"),
    }


def look(symbol: str = "", page_id: str = "", q: str = "") -> Dict[str, Any]:
    """Look into memory: open a symbol/page or search."""
    if q:
        return search(q)
    if symbol:
        g = get_symbol(symbol)
        if not g.get("ok"):
            return g
        return {
            "ok": True,
            "action": "look",
            "symbol": g["symbol"],
            "kind": g.get("kind"),
            "bytes": g.get("bytes"),
            "workspace": g.get("workspace"),
            "tags": g.get("tags"),
            "note": g.get("note"),
            "preview": g.get("preview"),
            "text": g.get("text"),
            "pages": g.get("pages"),
            "chain_id": g.get("chain_id"),
            "map": f"/v1/vmem/map?page={g['pages'][0]}" if g.get("pages") else None,
        }
    if page_id:
        g = get_page(page_id)
        if not g.get("ok"):
            return g
        return {
            "ok": True,
            "action": "look",
            "page_id": page_id,
            "bytes": g.get("bytes"),
            "preview": g.get("preview"),
            "kind": g.get("kind"),
        }
    # default: recent list
    return {
        "ok": True,
        "action": "look",
        "recent": list_recent().get("recent") or [],
        "symbols": list_symbols().get("symbols") or [],
    }


def search(query: str, *, limit: int = 20) -> Dict[str, Any]:
    q = (query or "").strip().lower()
    if not q:
        return {"ok": False, "error": "empty query"}
    idx = _load_index()
    hits = []
    for sym, meta in (idx.get("symbols") or {}).items():
        blob = " ".join(
            [
                sym,
                str(meta.get("preview") or ""),
                str(meta.get("note") or ""),
                str(meta.get("kind") or ""),
                str(meta.get("workspace") or ""),
                " ".join(meta.get("tags") or []),
            ]
        ).lower()
        score = 0
        if q in sym.lower():
            score += 5
        if q in blob:
            score += 2
        for part in q.split():
            if part in blob:
                score += 1
        if score:
            hits.append(
                {
                    "symbol": sym,
                    "score": score,
                    "kind": meta.get("kind"),
                    "bytes": meta.get("total_bytes"),
                    "preview": meta.get("preview"),
                    "workspace": meta.get("workspace"),
                    "updated_at": meta.get("updated_at"),
                }
            )
    hits.sort(key=lambda h: (-h["score"], -(h.get("updated_at") or 0)))
    return {"ok": True, "query": query, "hits": hits[: max(1, min(limit, 50))], "count": len(hits)}


def recreate(
    symbol: str = "",
    *,
    page_id: str = "",
    export: bool = True,
    filename: str = "",
) -> Dict[str, Any]:
    """Rebuild original content from pixel pages; optionally write an export file."""
    if symbol:
        g = get_symbol(symbol)
    elif page_id:
        p = get_page(page_id)
        if not p.get("ok"):
            return p
        data = base64.b64decode(p["data_b64"])
        g = {
            "ok": True,
            "symbol": f"page/{page_id[:12]}",
            "data_b64": p["data_b64"],
            "bytes": len(data),
            "kind": p.get("kind") or "binary",
            "text": data.decode("utf-8", errors="replace") if _looks_text(data) else None,
            "sha256": p.get("sha256"),
            "pages": [page_id],
        }
    else:
        return {"ok": False, "error": "symbol or page_id required"}

    if not g.get("ok"):
        return g

    data = base64.b64decode(g["data_b64"])
    kind = g.get("kind") or ("text" if _looks_text(data) else "binary")
    out: Dict[str, Any] = {
        "ok": True,
        "action": "recreate",
        "symbol": g.get("symbol"),
        "bytes": len(data),
        "kind": kind,
        "sha256": g.get("sha256") or hashlib.sha256(data).hexdigest(),
        "pages": g.get("pages") or [],
        "recreated": True,
    }

    if kind in ("text", "json") or _looks_text(data):
        text = data.decode("utf-8", errors="replace")
        out["text"] = text
        out["text_preview"] = text[:500]
    else:
        out["data_b64"] = g["data_b64"]

    # Always attach a pixel map of first page for visual recreate
    pages = g.get("pages") or []
    if pages:
        mp = map_png(page_id=pages[0], max_side=256)
        if mp.get("ok"):
            out["pixel_map"] = {"mime": mp.get("mime"), "base64": mp.get("base64"), "page_id": pages[0]}

    if export:
        EXPORTS.mkdir(parents=True, exist_ok=True)
        base = filename or _safe_sym(str(g.get("symbol") or "export")).replace("/", "_")
        if kind in ("text", "json") or _looks_text(data):
            ext = ".json" if kind == "json" else ".txt"
            path = EXPORTS / f"{base}{ext}"
            path.write_text(data.decode("utf-8", errors="replace"), encoding="utf-8")
        else:
            path = EXPORTS / f"{base}.bin"
            path.write_bytes(data)
        out["export_path"] = str(path)
        # also write a small handoff envelope for agents
        env_path = HANDOFF / f"{base}.envelope.json"
        env_path.write_text(
            json.dumps(
                {
                    "symbol": g.get("symbol"),
                    "kind": kind,
                    "bytes": len(data),
                    "sha256": out["sha256"],
                    "export_path": str(path),
                    "at": time.time(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        out["envelope_path"] = str(env_path)

    return out


def pass_info(
    symbol: str,
    *,
    to: str = "context",
    agent: str = "ARCHON",
    peer: str = "",
    workspace: str = "",
) -> Dict[str, Any]:
    """Pass memory to agent / device tray / session context / handoff file."""
    g = get_symbol(symbol)
    if not g.get("ok"):
        return g

    target = (to or "context").strip().lower()
    text = g.get("text") or g.get("text_preview") or g.get("preview") or ""
    summary = (
        f"[pixel-memory] symbol={g['symbol']} kind={g.get('kind')} "
        f"bytes={g.get('bytes')}\n{text[:2000]}"
    )
    result: Dict[str, Any] = {
        "ok": True,
        "action": "pass",
        "symbol": g["symbol"],
        "to": target,
        "bytes": g.get("bytes"),
    }

    if target in ("agent", "mesh", "helper"):
        try:
            r = send_message(
                "USER",
                (agent or "ARCHON").upper(),
                summary,
                channel="freq-0",
                kind="vmem_pass",
                encrypt=True,
            )
            result["agent"] = (agent or "ARCHON").upper()
            result["message_id"] = r.get("message_id")
            result["channel"] = r.get("channel")
        except Exception as e:
            result["ok"] = False
            result["error"] = str(e)[:200]
        return result

    if target in ("device", "node", "transfer"):
        from pocket.node_transfer import offer_file

        raw = base64.b64decode(g["data_b64"])
        name = _safe_sym(g["symbol"]).replace("/", "_") + (".txt" if g.get("kind") == "text" else ".bin")
        off = offer_file(
            name=name,
            data=raw,
            to_peer=peer or "",
            note=f"vmem pass {g['symbol']}",
            from_user="vmem",
        )
        result["offer"] = off
        return result

    if target in ("context", "workspace", "session"):
        ws = (workspace or g.get("workspace") or "default").strip()
        with _lock:
            idx = _load_index()
            ctx = idx.setdefault("workspaces", {}).setdefault(ws, {"symbols": [], "context": []})
            ctx_list = [c for c in (ctx.get("context") or []) if c.get("symbol") != g["symbol"]]
            ctx_list.insert(
                0,
                {
                    "symbol": g["symbol"],
                    "preview": (text or "")[:200],
                    "at": time.time(),
                    "bytes": g.get("bytes"),
                },
            )
            ctx["context"] = ctx_list[:30]
            if g["symbol"] not in (ctx.get("symbols") or []):
                ctx["symbols"] = [g["symbol"]] + list(ctx.get("symbols") or [])
                ctx["symbols"] = ctx["symbols"][:200]
            _save_index(idx)
        result["workspace"] = ws
        result["context_size"] = len(ctx_list)
        result["context_block"] = context_block(ws)
        return result

    if target in ("file", "handoff", "export"):
        rec = recreate(g["symbol"], export=True)
        result["recreate"] = {
            "export_path": rec.get("export_path"),
            "envelope_path": rec.get("envelope_path"),
        }
        return result

    if target in ("clipboard", "copy"):
        # server cannot write user clipboard; return text for UI
        result["clipboard_text"] = text or g.get("preview") or g["symbol"]
        result["note"] = "UI should copy clipboard_text"
        return result

    return {"ok": False, "error": f"unknown pass target: {to}", "allowed": ["agent", "device", "context", "file", "clipboard"]}


def context_block(workspace: str = "default", *, limit: int = 6) -> str:
    """Text block agents can inject: recent memory for a workspace."""
    idx = _load_index()
    ws = (workspace or "default").strip()
    ctx = ((idx.get("workspaces") or {}).get(ws) or {}).get("context") or []
    lines = [f"# Working memory ({ws})"]
    for c in ctx[:limit]:
        lines.append(f"- `{c.get('symbol')}` ({c.get('bytes') or '?'} B): {c.get('preview') or ''}")
    if len(lines) == 1:
        # fall back to recent symbols in workspace
        for sym, meta in list((idx.get("symbols") or {}).items())[:limit]:
            if (meta.get("workspace") or "default") == ws:
                lines.append(f"- `{sym}`: {meta.get('preview') or ''}")
    return "\n".join(lines) + "\n"


def list_symbols(*, workspace: str = "") -> Dict[str, Any]:
    idx = _load_index()
    syms = []
    for k, v in sorted(
        (idx.get("symbols") or {}).items(),
        key=lambda kv: -(kv[1].get("updated_at") or 0),
    ):
        if workspace and (v.get("workspace") or "default") != workspace:
            continue
        syms.append(
            {
                "symbol": k,
                "chain_id": v.get("chain_id"),
                "pages": len(v.get("pages") or []),
                "total_bytes": v.get("total_bytes"),
                "kind": v.get("kind"),
                "workspace": v.get("workspace"),
                "tags": v.get("tags") or [],
                "preview": v.get("preview"),
                "updated_at": v.get("updated_at"),
            }
        )
    return {"ok": True, "symbols": syms, "page_count": len(idx.get("pages") or {})}


def list_recent(*, limit: int = 12) -> Dict[str, Any]:
    idx = _load_index()
    return {"ok": True, "recent": (idx.get("recent") or [])[: max(1, min(limit, 40))]}


def map_png(*, page_id: str = "", symbol: str = "", max_side: int = 256) -> Dict[str, Any]:
    """Render a page (or composite) as PNG base64."""
    try:
        from PIL import Image
    except Exception:
        return {"ok": False, "error": "PIL not available"}

    if symbol and not page_id:
        g = get_symbol(symbol)
        if g.get("ok") and g.get("pages"):
            page_id = g["pages"][0]

    if page_id:
        rgb_path = LATTICE / f"{page_id}.rgb"
        if not rgb_path.is_file():
            g = get_page(page_id)
            if not g.get("ok"):
                return g
            raw = base64.b64decode(g["data_b64"])
            pix = _bytes_to_pixels(raw)
        else:
            pix = rgb_path.read_bytes()
            if len(pix) < PAGE_BYTES:
                pix = pix + b"\x00" * (PAGE_BYTES - len(pix))
        img = Image.frombytes("RGB", (TILE, TILE), pix[:PAGE_BYTES])
        if max_side and max_side != TILE:
            img = img.resize((max_side, max_side), Image.Resampling.NEAREST)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return {
            "ok": True,
            "mime": "image/png",
            "base64": base64.b64encode(buf.getvalue()).decode("ascii"),
            "page_id": page_id,
            "tile": TILE,
        }

    idx = _load_index()
    pids = list((idx.get("pages") or {}).keys())[:16]
    if not pids:
        img = Image.new("RGB", (max_side, max_side), (12, 16, 28))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return {
            "ok": True,
            "mime": "image/png",
            "base64": base64.b64encode(buf.getvalue()).decode("ascii"),
            "empty": True,
        }
    cells = []
    for pid in pids:
        rgb_path = LATTICE / f"{pid}.rgb"
        if rgb_path.is_file():
            pix = rgb_path.read_bytes()
        else:
            pix = b"\x10\x14\x22" * (TILE * TILE)
        if len(pix) < PAGE_BYTES:
            pix = pix + b"\x00" * (PAGE_BYTES - len(pix))
        cells.append(Image.frombytes("RGB", (TILE, TILE), pix[:PAGE_BYTES]))
    cols = min(4, len(cells))
    rows = math.ceil(len(cells) / cols)
    canvas = Image.new("RGB", (cols * TILE, rows * TILE), (7, 10, 18))
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        canvas.paste(cell, (c * TILE, r * TILE))
    if max_side and canvas.width > max_side:
        scale = max_side / float(canvas.width)
        canvas = canvas.resize((max_side, max(1, int(canvas.height * scale))), Image.Resampling.NEAREST)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return {
        "ok": True,
        "mime": "image/png",
        "base64": base64.b64encode(buf.getvalue()).decode("ascii"),
        "pages_shown": len(cells),
        "tile": TILE,
    }


def share_page_to_node(page_id: str, *, to_peer: str = "") -> Dict[str, Any]:
    g = get_page(page_id)
    if not g.get("ok"):
        return g
    from pocket.node_transfer import offer_file

    raw = base64.b64decode(g["data_b64"])
    return offer_file(
        name=f"vmem_{page_id[:12]}.page",
        data=raw,
        to_peer=to_peer,
        note=f"pixel-vmem page {page_id}",
        from_user="vmem",
    )


def delete_symbol(symbol: str) -> Dict[str, Any]:
    """Remove symbol index entry (pages kept if shared)."""
    sym = _safe_sym(symbol)
    with _lock:
        idx = _load_index()
        if sym not in (idx.get("symbols") or {}):
            return {"ok": False, "error": "not found"}
        del idx["symbols"][sym]
        idx["recent"] = [r for r in (idx.get("recent") or []) if r.get("symbol") != sym]
        for ws, meta in (idx.get("workspaces") or {}).items():
            meta["symbols"] = [s for s in (meta.get("symbols") or []) if s != sym]
            meta["context"] = [c for c in (meta.get("context") or []) if c.get("symbol") != sym]
        _save_index(idx)
    return {"ok": True, "deleted": sym}
