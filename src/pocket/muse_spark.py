"""Muse Spark desk agent — Meta Muse Spark style multimodal reasoning on host.

Runs a parallel multi-agent research pass (contemplating mode), synthesizes a
single answer, and can open meta.ai for the hosted Muse Spark surface.

Mode ids: muse_spark | muse | spark | muse-spark
"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple


def _progress(job_id: str, text: str) -> None:
    if not job_id:
        return
    try:
        from pocket.stream_util import update_progress

        update_progress(job_id, text, engine="muse_spark")
    except Exception:
        pass


def _web_hits(q: str, n: int = 5) -> List[Dict[str, str]]:
    try:
        from pocket.web_research import search_web

        sr = search_web(q[:200], max_results=n)
        return list(sr.get("results") or [])[:n]
    except Exception:
        return []


def _screen_brief() -> str:
    try:
        from pocket.skill_runner import run_skill

        md, err, _ = run_skill("screen_sense", prompt="muse spark context", params={})
        if err:
            return ""
        return (md or "")[:600]
    except Exception:
        return ""


def _plan_lanes(prompt: str) -> List[Tuple[str, str]]:
    """Parallel research lanes — Muse Spark-style multi-agent contemplate."""
    p = (prompt or "").strip() or "general"
    return [
        ("Research", f"{p} key facts sources"),
        ("Reasoning", f"{p} tradeoffs risks options"),
        ("Action", f"{p} concrete next steps checklist"),
        ("Multimodal", f"{p} visual UI product examples"),
        ("Neuro", f"{p} memory critic verify-when-done"),
    ]


def run_muse_spark_job(
    prompt: str,
    *,
    cwd: str = "",
    job: Dict[str, Any] | None = None,
) -> Tuple[str, str, str]:
    """Product Muse Spark turn on the desk host."""
    job = job or {}
    jid = job.get("id") or ""
    text = (prompt or "").strip()
    low = text.lower()
    t0 = time.time()

    if not text or low in ("help", "?", "about", "what is muse spark"):
        body = (
            "# Muse Spark\n\n"
            "Meta Superintelligence Labs multimodal reasoning agent on your desk.\n\n"
            "**Modes**\n"
            "- Freeform ask → parallel research lanes + synthesis\n"
            "- `open meta` / `open muse` → open hosted Muse Spark (meta.ai)\n"
            "- Activate **Voice engine** in the header to talk with this agent\n\n"
            "**Examples**\n"
            "- Compare agent frameworks for a local desk product\n"
            "- Plan a restaurant night and research options\n"
            "- open meta\n"
        )
        return body, "", "muse_spark"

    if re.search(r"\b(open meta|open muse|meta\.ai|launch muse)\b", low):
        _progress(jid, "Opening Muse Spark surface (meta.ai)…")
        url = "https://www.meta.ai/"
        try:
            from pocket.virtual_computer import act

            r = act("open_url", url=url)
            ok = bool(r.get("ok"))
        except Exception as e:
            ok = False
            r = {"error": str(e)[:160]}
        body = (
            f"# Muse Spark · hosted surface\n\n"
            f"{'Opened' if ok else 'Tried to open'} [{url}]({url}) in host Edge.\n\n"
            f"Use the hosted Muse Spark chat there, or keep talking here for "
            f"**local multi-lane synthesis** on this machine.\n"
        )
        return body, "" if ok else str(r.get("error") or "open failed"), "muse_spark"

    # Reagent Spark (OpenAI-compatible qwen) if the host key is set.
    try:
        from pocket.spark_api import chat as spark_chat, status as spark_status

        st = spark_status()
        if st.get("configured"):
            _progress(jid, f"Spark · {st.get('model')} via {st.get('base_url')}…")
            from pocket.spark_work import work as spark_work

            r = spark_work(text, cwd=cwd or str(__import__("pathlib").Path.home() / ".pocket" / "phoneai_ws"))
            if r.get("reply"):
                body = (
                    f"# Spark\n\n_{r.get('model')} · {r.get('via')}_\n\n"
                    f"{r.get('reply')}\n"
                )
                return body, "" if r.get("ok") else str(r.get("error") or ""), "muse_spark"
            return (
                f"# Spark\n\nCould not get a reply.\n\n`{r.get('error') or r.get('http') or 'empty'}`\n"
                f"Check http://127.0.0.1:8787/spark\n",
                str(r.get("error") or "empty"),
                "muse_spark",
            )
    except Exception as e:
        _progress(jid, f"Spark skip: {e}"[:160])

    _progress(jid, "Muse Spark · contemplating (parallel lanes)…")
    lanes = _plan_lanes(text)
    lane_out: Dict[str, List[Dict[str, str]]] = {}
    errors: List[str] = []

    def one(name: str, q: str) -> Tuple[str, List[Dict[str, str]], str]:
        try:
            hits = _web_hits(q, 4)
            return name, hits, ""
        except Exception as e:
            return name, [], str(e)[:120]

    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = [pool.submit(one, n, q) for n, q in lanes]
        for fut in as_completed(futs):
            name, hits, err = fut.result()
            lane_out[name] = hits
            if err:
                errors.append(f"{name}: {err}")
            _progress(jid, f"Muse Spark · {name} · {len(hits)} hits")

    screen = _screen_brief()
    if screen:
        _progress(jid, "Muse Spark · screen context captured")

    # Synthesis
    lines: List[str] = [
        "# Muse Spark",
        "",
        f"_Multimodal reasoning · {(prompt or '')[:160]}_",
        "",
        "## Synthesis",
        "",
        f"You asked: **{(prompt or '').strip()[:300]}**",
        "",
        "Parallel lanes finished. Combined view:",
        "",
    ]

    bullets: List[str] = []
    all_links: List[Dict[str, str]] = []
    for name, _q in lanes:
        hits = lane_out.get(name) or []
        if not hits:
            lines.append(f"### {name}\n_No hits — try a sharper query._\n")
            continue
        lines.append(f"### {name}")
        for i, h in enumerate(hits[:4], 1):
            title = (h.get("title") or "result")[:100]
            url = (h.get("url") or "")[:200]
            snip = (h.get("snippet") or "")[:160]
            lines.append(f"{i}. **{title}**" + (f" — {snip}" if snip else ""))
            if url:
                lines.append(f"   {url}")
                all_links.append(h)
            bullets.append(f"- ({name}) {title}")
        lines.append("")

    if screen:
        lines.append("### On your screen")
        lines.append(screen[:500])
        lines.append("")

    lines.append("## Recommended next steps")
    lines.append("1. Pick one source above and dig deeper (`fetch <url>` via Web agent).")
    lines.append("2. Say **open meta** to use hosted Muse Spark at meta.ai.")
    lines.append("3. Activate **Voice engine** to continue this agent by voice.")
    if all_links:
        lines.append("")
        lines.append("## Top links")
        seen = set()
        for h in all_links:
            u = h.get("url") or ""
            if not u or u in seen:
                continue
            seen.add(u)
            lines.append(f"- [{(h.get('title') or 'link')[:80]}]({u})")
            if len(seen) >= 8:
                break

    ms = int((time.time() - t0) * 1000)
    lines.append("")
    lines.append(f"_Muse Spark · {ms}ms · lanes={len(lanes)} · host-local_")
    if errors:
        lines.append("")
        lines.append("Notes: " + "; ".join(errors[:3]))

    out = "\n".join(lines)
    # Short TTS-friendly preamble for voice engine
    spoken = re.sub(r"\s+", " ", f"Muse Spark finished. {(prompt or '')[:80]}. See the synthesis and next steps.")[:240]
    if len(spoken) > 40:
        out = out + f"\n\n```tts\nrate=0.96\npitch=1.02\n{spoken}\n```"
    _progress(jid, out[:3500])
    return out, "", "muse_spark"
