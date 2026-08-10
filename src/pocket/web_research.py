"""Web research product — search + fetch + research (no API keys required)."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

from pocket.safety import allow_url, audit
from pocket.tokenomics import burn

MAX_BYTES = 900_000
UA = "POCKET/1.0 (desktop-agent; +https://pocket.medinatechlabs.net)"


def _strip_html(raw: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_url(url: str, *, max_chars: int = 14000) -> Dict[str, Any]:
    ok, msg = allow_url(url)
    if not ok:
        return {"ok": False, "error": msg}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,*/*"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read(MAX_BYTES)
            ctype = r.headers.get("Content-Type", "")
            final = r.geturl()
        text = data.decode("utf-8", errors="replace")
        if "json" in ctype.lower():
            try:
                text = json.dumps(json.loads(text), indent=2)
            except Exception:
                pass
        elif "html" in ctype.lower() or "<html" in text[:300].lower() or text.lstrip().lower().startswith("<!doctype"):
            text = _strip_html(text)
        text = text[:max_chars]
        audit("web_fetch", url=url[:200], bytes=len(data))
        burn("web_fetch", meta={"url": url[:120]}) if "web_fetch" in __import__("pocket.tokenomics", fromlist=["COSTS"]).COSTS else burn("job_ask", meta={"web": "fetch"})
        return {"ok": True, "url": final, "chars": len(text), "content_type": ctype, "text": text, "at": time.time()}
    except Exception as e:
        audit("web_fetch_fail", url=url[:200], error=str(e))
        return {"ok": False, "error": str(e), "url": url}


def _browser_ua() -> str:
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )


def _normalize_href(href: str) -> str:
    """Unwrap DDG redirects and protocol-relative URLs so results are kept."""
    h = (href or "").strip()
    if not h:
        return ""
    h = html.unescape(h)
    if "uddg=" in h:
        try:
            m = re.search(r"uddg=([^&]+)", h)
            if m:
                h = urllib.parse.unquote(m.group(1))
        except Exception:
            pass
    if h.startswith("//"):
        h = "https:" + h
    if h.startswith("/l/?") or h.startswith("/l?"):
        # leftover relative DDG redirect
        try:
            m = re.search(r"uddg=([^&]+)", h)
            if m:
                h = urllib.parse.unquote(m.group(1))
        except Exception:
            return ""
    if not h.startswith("http://") and not h.startswith("https://"):
        return ""
    # Drop search-engine chrome
    low = h.lower()
    if any(x in low for x in ("duckduckgo.com", "brave.com/search", "bing.com/search", "google.com/search")):
        if "uddg=" not in (href or ""):
            # keep real destination pages only
            if "duckduckgo.com/l/" in low:
                return ""
            if "brave.com/search" in low or "bing.com/search" in low:
                return ""
    return h[:400]


def _dedupe_results(results: List[Dict[str, str]], max_results: int) -> List[Dict[str, str]]:
    seen = set()
    uniq: List[Dict[str, str]] = []
    for r in results:
        u = _normalize_href(r.get("url") or "")
        if not u or u in seen:
            continue
        seen.add(u)
        title = _strip_html(r.get("title") or "")[:160] or u
        snip = _strip_html(r.get("snippet") or "")[:300]
        uniq.append({"title": title, "url": u, "snippet": snip})
        if len(uniq) >= max_results:
            break
    return uniq


def _search_ddg_html(q: str, max_results: int) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for base in (
        "https://html.duckduckgo.com/html/",
        "https://lite.duckduckgo.com/lite/",
    ):
        try:
            html_url = base + "?" + urllib.parse.urlencode({"q": q})
            ok, _ = allow_url(html_url)
            if not ok:
                continue
            req = urllib.request.Request(
                html_url,
                headers={
                    "User-Agent": _browser_ua(),
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            with urllib.request.urlopen(req, timeout=25) as r:
                raw = r.read(MAX_BYTES).decode("utf-8", errors="replace")
            if "anomaly" in raw[:800].lower() and "result__a" not in raw:
                continue
            # class before or after href
            for m in re.finditer(
                r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
                r'|<a[^>]*href="([^"]+)"[^>]*class="[^"]*result__a[^"]*"[^>]*>(.*?)</a>',
                raw,
                re.I | re.S,
            ):
                href = m.group(1) or m.group(3) or ""
                title = _strip_html(m.group(2) or m.group(4) or "")
                href = _normalize_href(href)
                if not href:
                    continue
                out.append({"title": title[:160] or href, "url": href, "snippet": ""})
                if len(out) >= max_results + 4:
                    break
            # lite: plain result links
            if len(out) < 2:
                for m in re.finditer(
                    r'href="(https?://[^"]+)"[^>]*>(.*?)</a>',
                    raw,
                    re.I | re.S,
                ):
                    href = _normalize_href(m.group(1))
                    if not href:
                        continue
                    title = _strip_html(m.group(2))
                    if len(title) < 3:
                        continue
                    out.append({"title": title[:160], "url": href, "snippet": ""})
                    if len(out) >= max_results + 4:
                        break
            if out:
                break
        except Exception:
            continue
    return out


def _search_brave_html(q: str, max_results: int) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    try:
        url = "https://search.brave.com/search?" + urllib.parse.urlencode({"q": q, "source": "web"})
        ok, _ = allow_url(url)
        if not ok:
            return out
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _browser_ua(),
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read(MAX_BYTES).decode("utf-8", errors="replace")
        # Brave result cards often use cite + anchor pairs
        for m in re.finditer(
            r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>',
            raw,
            re.I | re.S,
        ):
            href = _normalize_href(m.group(1))
            if not href:
                continue
            title = _strip_html(m.group(2))
            if len(title) < 4 or len(title) > 180:
                continue
            # filter chrome
            low = href.lower()
            if any(
                x in low
                for x in (
                    "brave.com",
                    "duckduckgo.com",
                    "microsoft.com/en-us/bing",
                    "accounts.google",
                )
            ):
                continue
            out.append({"title": title[:160], "url": href, "snippet": ""})
            if len(out) >= max_results + 6:
                break
    except Exception:
        pass
    return out


def search_web(query: str, *, max_results: int = 6) -> Dict[str, Any]:
    """Product search — multi-backend (DDG IA + HTML + Brave + Wikipedia).

    Note: Instant Answer alone is empty for local restaurants; HTML/Brave carry those.
    """
    q = (query or "").strip()
    if not q or len(q) > 300:
        return {"ok": False, "error": "query required (max 300 chars)"}

    results: List[Dict[str, str]] = []
    backends: List[str] = []

    # 1) DuckDuckGo Instant Answer JSON (good for encyclopedic; weak for local dining)
    try:
        ddg = "https://api.duckduckgo.com/?" + urllib.parse.urlencode(
            {"q": q, "format": "json", "no_html": 1, "skip_disambig": 1}
        )
        ok, _ = allow_url(ddg)
        if ok:
            req = urllib.request.Request(ddg, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8", errors="replace"))
            if data.get("AbstractText"):
                results.append(
                    {
                        "title": data.get("Heading") or "Summary",
                        "url": data.get("AbstractURL") or ddg,
                        "snippet": (data.get("AbstractText") or "")[:400],
                    }
                )
            for t in (data.get("RelatedTopics") or [])[: max_results]:
                if isinstance(t, dict) and t.get("FirstURL"):
                    results.append(
                        {
                            "title": _strip_html(t.get("Text") or t.get("FirstURL"))[:160],
                            "url": t.get("FirstURL"),
                            "snippet": _strip_html(t.get("Text") or "")[:300],
                        }
                    )
                elif isinstance(t, dict) and t.get("Topics"):
                    for tt in t["Topics"][:3]:
                        if tt.get("FirstURL"):
                            results.append(
                                {
                                    "title": _strip_html(tt.get("Text") or "")[:160],
                                    "url": tt.get("FirstURL"),
                                    "snippet": _strip_html(tt.get("Text") or "")[:300],
                                }
                            )
            if results:
                backends.append("ddg_ia")
    except Exception:
        pass

    # 2) DuckDuckGo HTML — real SERP for restaurants/products (fix protocol-relative //)
    if len(results) < max_results:
        html_hits = _search_ddg_html(q, max_results)
        if html_hits:
            results.extend(html_hits)
            backends.append("ddg_html")

    # 3) Brave HTML — strong for local venues when DDG is thin/blocked
    if len(_dedupe_results(results, max_results)) < max(2, max_results // 2):
        brave_hits = _search_brave_html(q, max_results)
        if brave_hits:
            results.extend(brave_hits)
            backends.append("brave_html")

    # 4) Wikipedia OpenSearch (always useful supplemental)
    try:
        wiki = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {
                "action": "opensearch",
                "search": q,
                "limit": min(4, max_results),
                "namespace": 0,
                "format": "json",
            }
        )
        ok, _ = allow_url(wiki)
        if ok:
            req = urllib.request.Request(wiki, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8", errors="replace"))
            if isinstance(data, list) and len(data) >= 4:
                titles, descs, urls = data[1], data[2], data[3]
                for i, title in enumerate(titles):
                    results.append(
                        {
                            "title": title,
                            "url": urls[i] if i < len(urls) else "",
                            "snippet": descs[i] if i < len(descs) else "",
                        }
                    )
                backends.append("wikipedia")
    except Exception:
        pass

    uniq = _dedupe_results(results, max_results)
    audit("web_search", query=q[:200], n=len(uniq), backends=",".join(backends) or "none")
    try:
        burn("web_search", meta={"q": q[:80], "n": len(uniq)})
    except Exception:
        burn("job_ask", meta={"web": "search"})

    return {
        "ok": bool(uniq),
        "query": q,
        "results": uniq,
        "count": len(uniq),
        "backends": backends,
        "at": time.time(),
        "error": "" if uniq else "no search hits — try a more specific query",
    }


def run_web_job(prompt: str) -> Tuple[str, str, str]:
    text = (prompt or "").strip()
    low = text.lower()

    if low.startswith("fetch "):
        res = fetch_url(text[6:].strip())
        if not res.get("ok"):
            return "", res.get("error") or "fetch failed", "web"
        return (
            f"## Fetch\n**URL:** {res.get('url')}\n**chars:** {res.get('chars')}\n\n{res.get('text')}",
            "",
            "web",
        )

    if low.startswith("search "):
        res = search_web(text[7:].strip())
        if not res.get("ok"):
            return "", res.get("error") or "search failed", "web"
        lines = [f"## Search: {res.get('query')}", f"Results: {res.get('count')}", ""]
        for i, r in enumerate(res.get("results") or [], 1):
            lines.append(f"{i}. **{r.get('title')}**\n   {r.get('url')}\n   {r.get('snippet') or ''}")
        if not res.get("results"):
            lines.append("_No results — try a different query._")
        return "\n".join(lines), "", "web"

    if low.startswith("research "):
        q = text[9:].strip()
        s = search_web(q, max_results=4)
        if not s.get("ok"):
            return "", s.get("error") or "search failed", "web"
        lines = [f"## Research: {q}", "", "### Sources"]
        for i, r in enumerate(s.get("results") or [], 1):
            lines.append(f"{i}. {r.get('title')} — {r.get('url')}")
        top = (s.get("results") or [{}])[0].get("url")
        if top:
            f = fetch_url(top, max_chars=7000)
            lines.append("\n### Extract from top source\n")
            lines.append(f.get("text") if f.get("ok") else f"(fetch failed: {f.get('error')})")
        return "\n".join(lines), "", "web"

    return (
        "## Web research (product)\n\n"
        "Commands:\n"
        "- `search <query>` — multi-source search\n"
        "- `fetch https://…` — page text extract\n"
        "- `research <query>` — search + top page extract\n",
        "",
        "web",
    )
