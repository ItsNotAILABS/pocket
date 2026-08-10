"""In-chat app previews — agents emit preview fences; desk renders bubble iframes.

Agents should end HTML/UI work with one of:

```preview
title: My app
url: http://127.0.0.1:5173/
```

```html-preview
<!DOCTYPE html><html>…</html>
```

```preview-html
…same…
```

Or POST /v1/preview {html,title} → use url: /v1/preview/{id}
"""

from __future__ import annotations

import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path.home() / ".pocket" / "previews"
ROOT.mkdir(parents=True, exist_ok=True)

# In-process registry (also mirrored on disk)
_REG: Dict[str, Dict[str, Any]] = {}


def put_html(
    html: str,
    *,
    title: str = "App preview",
    source: str = "agent",
    job_id: str = "",
) -> Dict[str, Any]:
    """Store HTML for same-origin iframe serve at /v1/preview/{id}."""
    body = (html or "").strip()
    if not body:
        return {"ok": False, "error": "empty html"}
    if len(body) > 2_000_000:
        body = body[:2_000_000]
    pid = uuid.uuid4().hex[:12]
    path = ROOT / f"{pid}.html"
    # Ensure document shell if fragment
    low = body.lower()
    if "<html" not in low:
        body = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{_esc(title)}</title>"
            f"<style>body{{font-family:system-ui,sans-serif;margin:16px;background:#0a0a0c;color:#e4e4e7}}</style>"
            f"</head><body>{body}</body></html>"
        )
    path.write_text(body, encoding="utf-8")
    rec = {
        "ok": True,
        "id": pid,
        "title": (title or "App preview")[:120],
        "path": str(path),
        "url": f"/v1/preview/{pid}",
        "absolute_url": f"http://127.0.0.1:8787/v1/preview/{pid}",
        "bytes": len(body.encode("utf-8")),
        "source": source,
        "job_id": job_id,
        "created_at": time.time(),
    }
    _REG[pid] = rec
    (ROOT / f"{pid}.json").write_text(
        __import__("json").dumps({k: v for k, v in rec.items() if k != "ok"}, indent=2),
        encoding="utf-8",
    )
    # fence for chat bubble
    rec["fence"] = (
        f"```preview\ntitle: {rec['title']}\nurl: {rec['url']}\n```\n"
    )
    return rec


def get_preview(pid: str, *, include_html: bool = True) -> Dict[str, Any]:
    pid = re.sub(r"[^a-zA-Z0-9_-]", "", pid or "")[:32]
    if not pid:
        return {"ok": False, "error": "id required"}
    path = ROOT / f"{pid}.html"
    meta = ROOT / f"{pid}.json"
    base: Dict[str, Any] = {}
    if pid in _REG:
        base = dict(_REG[pid])
    elif path.is_file():
        title = "App preview"
        if meta.is_file():
            try:
                import json

                m = json.loads(meta.read_text(encoding="utf-8"))
                title = m.get("title") or title
            except Exception:
                pass
        base = {
            "id": pid,
            "title": title,
            "path": str(path),
            "url": f"/v1/preview/{pid}",
        }
    else:
        return {"ok": False, "error": "not found"}
    base["ok"] = True
    base.setdefault("path", str(path))
    base.setdefault("url", f"/v1/preview/{pid}")
    if include_html and path.is_file():
        base["html"] = path.read_text(encoding="utf-8", errors="replace")
    return base


def read_html_file(pid: str) -> Optional[str]:
    path = ROOT / re.sub(r"[^a-zA-Z0-9_-]", "", pid or "")[:32]
    # allow bare id
    if not str(path).endswith(".html"):
        path = ROOT / f"{re.sub(r'[^a-zA-Z0-9_-]', '', pid or '')[:32]}.html"
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    g = get_preview(pid, include_html=True)
    return g.get("html") if g.get("ok") else None


def format_preview_fence(*, title: str = "App preview", url: str = "", html: str = "") -> str:
    """Helpers for agent replies."""
    if html and not url:
        r = put_html(html, title=title)
        if r.get("ok"):
            return r["fence"]
    if url:
        return f"```preview\ntitle: {title}\nurl: {url}\n```\n"
    return ""


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def status() -> Dict[str, Any]:
    n = len(list(ROOT.glob("*.html")))
    return {"ok": True, "previews": n, "root": str(ROOT), "first_class": True}
