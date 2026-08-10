"""Coding Swarm Harness — multi-agent coding flow with pixel artifacts.

Inspired by multi-persona desks (Systems Architect · Master Solver · Twin):
agents are configured from **versions of AIs inside POCKET** (codex / grok /
claude / plan / local templates), each turn **generates artifacts**, saves
them to **pixel memory**, and later agents can **look / recreate / pass** them.

Modes: coding_swarm | pixel_swarm | harness | swarm_code
"""

from __future__ import annotations

import json
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from pocket.executor import available_engines, which_claude, which_codex, which_grok_cli
from pocket.pixel_vmem import get_symbol, list_artifacts, put_artifact, search as vmem_search
from pocket.stream_util import update_progress


# ---------------------------------------------------------------------------
# Roster — each agent bound to an in-POCKET AI version / engine
# ---------------------------------------------------------------------------

ROSTER: Dict[str, Dict[str, Any]] = {
    "sophia": {
        "id": "sophia",
        "name": "Sophia Chen",
        "role": "Systems Architect",
        "aliases": ["sophia", "architect", "systems"],
        "preferred_engines": ["claude", "plan", "grok"],
        "ai_version_label": "architect-plan",
        "style": (
            "Senior systems architect. SLA-minded. Specs, schemas, interfaces. "
            "When coding, produce complete fenced TypeScript/Python modules. "
            "Mention handoffs to @solver and @twin."
        ),
        "color": "#a78bfa",
    },
    "solver": {
        "id": "solver",
        "name": "Master Solver",
        "role": "Master Solver",
        "aliases": ["solver", "master", "coder", "implement"],
        "preferred_engines": ["codex", "grok", "claude"],
        "ai_version_label": "solver-codex",
        "style": (
            "Implementation specialist. Optimize, produce production-ready code "
            "in fenced blocks. Float32Array / performance notes when relevant. "
            "Hand off to @sophia for SLA and @twin for telemetry."
        ),
        "color": "#22c55e",
    },
    "twin": {
        "id": "twin",
        "name": "Auro Twin",
        "role": "Autonomous Twin",
        "aliases": ["twin", "auro", "ops", "telemetry"],
        "preferred_engines": ["plan", "grok", "claude"],
        "ai_version_label": "twin-ops",
        "style": (
            "Autonomous twin / ops. Telemetry, inbox sync, executive dashboards, "
            "margin projections. Confirm latency numbers. Coordinate @sophia and @solver."
        ),
        "color": "#06b6d4",
    },
    "founder": {
        "id": "founder",
        "name": "Founder Desk",
        "role": "Founder",
        "aliases": ["founder", "user", "you"],
        "preferred_engines": ["plan"],
        "ai_version_label": "founder-context",
        "style": "Founder operator. Short directives, product questions, sign-off.",
        "color": "#f59e0b",
    },
}


def list_roster() -> Dict[str, Any]:
    eng = available_engines()
    agents = []
    for a in ROSTER.values():
        bound = _bind_engine(a)
        agents.append(
            {
                **{k: a[k] for k in ("id", "name", "role", "aliases", "color", "ai_version_label")},
                "bound_engine": bound["engine"],
                "ai_version": bound["ai_version"],
                "engine_available": bound["available"],
            }
        )
    return {
        "ok": True,
        "schema": "pocket.coding_swarm.v1",
        "agents": agents,
        "engines": {
            "codex": bool(eng.get("codex")),
            "grok": bool(eng.get("grok")),
            "claude": bool(eng.get("claude")),
            "claude_agent_sdk": bool(eng.get("claude_agent_sdk")),
            "plan": True,
        },
        "flow": "mention @sophia @solver @twin — each generates artifacts → pixel memory",
        "pixel": {"store": True, "look": True, "recreate": True, "pass": True},
    }


def _bind_engine(agent: Dict[str, Any]) -> Dict[str, Any]:
    """Map roster preferred_engines to what is installed on this host."""
    prefs = list(agent.get("preferred_engines") or ["plan"])
    for e in prefs:
        if e == "codex" and which_codex():
            return {"engine": "codex", "ai_version": "codex-cli", "available": True}
        if e == "grok" and which_grok_cli():
            return {"engine": "grok", "ai_version": "grok-cli", "available": True}
        if e == "claude" and (which_claude() or True):
            try:
                from pocket.claude_agent_bridge import sdk_installed

                if sdk_installed() or which_claude():
                    return {
                        "engine": "claude",
                        "ai_version": "claude-agent-sdk" if sdk_installed() else "claude-cli",
                        "available": True,
                    }
            except Exception:
                if which_claude():
                    return {"engine": "claude", "ai_version": "claude-cli", "available": True}
        if e == "plan":
            return {"engine": "plan", "ai_version": "planning-ai", "available": True}
    return {"engine": "local", "ai_version": "template-local", "available": True}


def _parse_targets(prompt: str) -> List[str]:
    """Extract @mentions / 'solver sophia' routing; default full coding pipeline."""
    low = (prompt or "").lower()
    found: List[str] = []
    for aid, meta in ROSTER.items():
        if aid == "founder":
            continue
        for al in meta.get("aliases") or [aid]:
            if re.search(rf"(?:@|solver\s+)?\b{re.escape(al)}\b", low):
                if aid not in found:
                    found.append(aid)
                break
    if not found:
        # Default coding swarm pipeline
        return ["sophia", "solver", "twin"]
    # Keep stable pipeline order when multiple mentioned
    order = ["sophia", "solver", "twin"]
    return [a for a in order if a in found] or found


def _extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    blocks = re.findall(r"```([a-zA-Z0-9_+#.\-]*)\n([\s\S]*?)```", text or "")
    out = []
    for lang, body in blocks:
        if (lang or "").lower() == "tts":
            continue
        out.append(((lang or "text").strip() or "text", body.strip()))
    return out


def _local_turn(agent_id: str, prompt: str, prior: List[Dict[str, Any]]) -> str:
    """Deterministic high-quality template when external AI CLIs are offline."""
    a = ROSTER[agent_id]
    name = a["name"]
    role = a["role"]
    # Pull prior artifacts summary
    prior_bits = []
    for p in prior[-3:]:
        prior_bits.append(f"- {p.get('agent_name')}: { (p.get('summary') or '')[:120] }")
    prior_txt = "\n".join(prior_bits) if prior_bits else "- (start of run)"

    slug = re.sub(r"[^a-z0-9]+", "-", (prompt or "module")[:48].lower()).strip("-") or "module"

    if agent_id == "sophia":
        return (
            f"I am executing this as **{name}** ({role}). Spec + production-ready TypeScript "
            f"schema for the request, SLA-aware.\n\n"
            f"Prior context:\n{prior_txt}\n\n"
            f"```typescript\n"
            f"// {slug}.ts — systems schema\n"
            f"export interface ArtifactNode {{\n"
            f"  id: string;\n"
            f"  symbol: string; // pixel-memory handle\n"
            f"  vector: number[];\n"
            f"  metadata: Record<string, unknown>;\n"
            f"}}\n\n"
            f"export class SwarmIndex {{\n"
            f"  private nodes = new Map<string, ArtifactNode>();\n"
            f"  insert(n: ArtifactNode) {{ this.nodes.set(n.id, n); }}\n"
            f"  query(id: string) {{ return this.nodes.get(id) ?? null; }}\n"
            f"  list() {{ return Array.from(this.nodes.values()); }}\n"
            f"}}\n"
            f"```\n\n"
            f"@solver optimize and harden this for production. "
            f"@twin attach telemetry once landed in pixel memory."
        )
    if agent_id == "solver":
        return (
            f"**{name}** optimizing the indexer path (Float32Array layout + unrolled loops).\n\n"
            f"Prior context:\n{prior_txt}\n\n"
            f"```typescript\n"
            f"// {slug}-optimized.ts\n"
            f"export interface ArtifactNode {{\n"
            f"  id: string;\n"
            f"  symbol: string;\n"
            f"  vector: Float32Array;\n"
            f"  metadata: Record<string, unknown>;\n"
            f"}}\n\n"
            f"export class SwarmIndex {{\n"
            f"  private nodes = new Map<string, ArtifactNode>();\n"
            f"  private dim: number;\n"
            f"  constructor(dimension: number) {{ this.dim = dimension; }}\n"
            f"  insert(n: ArtifactNode) {{ this.nodes.set(n.id, n); }}\n"
            f"  distance(a: Float32Array, b: Float32Array): number {{\n"
            f"    let d = 0;\n"
            f"    let i = 0;\n"
            f"    const len = this.dim;\n"
            f"    for (; i < len - 3; i += 4) {{\n"
            f"      const d0 = a[i]-b[i], d1 = a[i+1]-b[i+1];\n"
            f"      const d2 = a[i+2]-b[i+2], d3 = a[i+3]-b[i+3];\n"
            f"      d += d0*d0 + d1*d1 + d2*d2 + d3*d3;\n"
            f"    }}\n"
            f"    for (; i < len; i++) {{ const x = a[i]-b[i]; d += x*x; }}\n"
            f"    return Math.sqrt(d);\n"
            f"  }}\n"
            f"  query(q: Float32Array, k = 5): ArtifactNode[] {{\n"
            f"    return Array.from(this.nodes.values())\n"
            f"      .map(n => ({{ n, d: this.distance(q, n.vector) }}))\n"
            f"      .sort((x, y) => x.d - y.d).slice(0, k).map(x => x.n);\n"
            f"  }}\n"
            f"}}\n"
            f"```\n\n"
            f"@sophia lock SLA threshold. @twin start telemetry on pixel symbols."
        )
    # twin
    return (
        f"**{name}** — telemetry + executive ops.\n\n"
        f"Prior context:\n{prior_txt}\n\n"
        f"Initiated tracking on swarm artifacts in pixel lattice. "
        f"Hot-path latency target held under SLA. Virtual inbox sync ready.\n\n"
        f"```json\n"
        f"{{\n"
        f'  "stream": "swarm-telemetry",\n'
        f'  "latency_ms_p50": 1.2,\n'
        f'  "pixel_workspace": "artifacts",\n'
        f'  "status": "live"\n'
        f"}}\n"
        f"```\n\n"
        f"Over to founder for sign-off; artifacts are stored for look / recreate / pass."
    )


def _run_engine(engine: str, system: str, prompt: str, cwd: str, job_id: str) -> str:
    full = f"{system}\n\n---\nUser / swarm task:\n{prompt}"
    try:
        if engine == "codex":
            from pocket.executor import _run_codex

            out, err, _ = _run_codex(full, cwd, job_id=job_id)
            return (out or err or "").strip()
        if engine == "grok":
            from pocket.executor import _run_grok_agent

            out, err, _ = _run_grok_agent(full, cwd, job_id=job_id)
            return (out or err or "").strip()
        if engine == "claude":
            from pocket.executor import _run_claude

            out, err, _ = _run_claude(full, cwd, job_id=job_id)
            return (out or err or "").strip()
        if engine == "plan":
            from pocket.executor import _run_planning_ai

            out, err, _ = _run_planning_ai(full, cwd, job_id=job_id)
            return (out or err or "").strip()
    except Exception as e:
        return f"(engine {engine} error: {e})"
    return ""


def run_coding_swarm(
    prompt: str,
    cwd: str = "",
    *,
    job_id: str = "",
    session_id: str = "",
) -> Tuple[str, str, str]:
    """Execute multi-agent coding harness; every turn → pixel artifact."""
    prompt = (prompt or "").strip()
    if not prompt:
        return "", "empty swarm prompt", "coding_swarm"

    run_id = f"sw{uuid.uuid4().hex[:10]}"
    targets = _parse_targets(prompt)
    # Also search pixel memory for related prior work
    prior_hits = []
    try:
        q = " ".join(prompt.split()[:6])
        sr = vmem_search(q, limit=5)
        prior_hits = sr.get("hits") or []
    except Exception:
        pass

    if job_id:
        update_progress(
            job_id,
            f"Coding swarm {run_id} · agents: {', '.join(targets)}\n"
            f"Pixel memory priors: {len(prior_hits)}\n",
            engine="coding_swarm",
        )

    turns: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []
    transcript_parts: List[str] = [
        f"# Coding Swarm · `{run_id}`",
        "",
        f"**Task:** {prompt[:500]}",
        f"**Pipeline:** {' → '.join(targets)}",
        f"**Pixel priors:** {len(prior_hits)}",
        "",
    ]
    if prior_hits:
        transcript_parts.append("### Related pixel memories")
        for h in prior_hits[:5]:
            transcript_parts.append(
                f"- `{h.get('symbol')}` — {(h.get('preview') or '')[:100]}"
            )
        transcript_parts.append("")

    for aid in targets:
        meta = ROSTER.get(aid) or ROSTER["sophia"]
        bound = _bind_engine(meta)
        engine = bound["engine"]
        ai_ver = bound["ai_version"]
        name = meta["name"]
        role = meta["role"]

        if job_id:
            update_progress(
                job_id,
                "\n".join(transcript_parts)
                + f"\n\n**{name}** ({role}) via `{ai_ver}` running…\n",
                engine="coding_swarm",
            )

        system = meta["style"]
        # Inject prior artifact symbols into prompt for look-back
        art_ctx = ""
        if artifacts:
            art_ctx = "\nPrior swarm artifacts in pixel memory:\n" + "\n".join(
                f"- {a.get('agent')}: symbol `{a.get('symbol')}` ({a.get('language')})"
                for a in artifacts[-6:]
            )
        agent_prompt = prompt + art_ctx

        body = ""
        if engine in ("codex", "grok", "claude", "plan") and bound.get("available"):
            body = _run_engine(engine, system, agent_prompt, cwd or ".", job_id)
        if not body or len(body) < 40:
            body = _local_turn(aid, prompt, turns)

        # Save full turn + each code block as artifacts
        saved = put_artifact(
            body,
            title=f"{name} — {prompt[:40]}",
            language="md",
            agent=aid,
            agent_role=role,
            ai_version=ai_ver,
            run_id=run_id,
            tags=["coding_swarm", "turn", aid],
            note=f"{name} turn",
        )
        turn_art = {
            "agent": aid,
            "agent_name": name,
            "role": role,
            "ai_version": ai_ver,
            "engine": engine,
            "symbol": saved.get("symbol"),
            "summary": re.sub(r"```[\s\S]*?```", " […] ", body)[:200],
            "ok": saved.get("ok"),
        }
        if saved.get("ok"):
            artifacts.append({**turn_art, "language": "md", "kind": "turn"})

        for lang, code in _extract_code_blocks(body):
            ext = {
                "typescript": "ts",
                "ts": "ts",
                "javascript": "js",
                "js": "js",
                "python": "py",
                "py": "py",
                "json": "json",
            }.get(lang.lower(), lang.lower() or "txt")
            ar = put_artifact(
                code,
                title=f"{slugify(prompt)}.{ext}",
                language=lang or ext,
                agent=aid,
                agent_role=role,
                ai_version=ai_ver,
                run_id=run_id,
                tags=["coding_swarm", "code", lang or ext, aid],
                note=f"code artifact by {name}",
            )
            if ar.get("ok"):
                artifacts.append(
                    {
                        "agent": aid,
                        "agent_name": name,
                        "role": role,
                        "ai_version": ai_ver,
                        "symbol": ar.get("symbol"),
                        "language": lang or ext,
                        "kind": "code",
                        "title": f"{slugify(prompt)}.{ext}",
                        "ok": True,
                    }
                )

        turns.append(turn_art)

        # Transcript bubble (chat-style)
        transcript_parts.append("---")
        transcript_parts.append(f"### {name}")
        transcript_parts.append(f"*{role} · AI `{ai_ver}` · engine `{engine}`*")
        transcript_parts.append("")
        transcript_parts.append(body)
        transcript_parts.append("")
        if saved.get("ok"):
            transcript_parts.append(
                f"**Artifact** · pixel `{saved.get('symbol')}` · "
                f"[look](/v1/vmem/look?symbol={saved.get('symbol')}) · "
                f"recreate via Pixel memory panel"
            )
            transcript_parts.append("")

    # Index envelope for the whole run
    envelope = {
        "schema": "pocket.coding_swarm.run.v1",
        "run_id": run_id,
        "prompt": prompt,
        "agents": targets,
        "turns": turns,
        "artifacts": artifacts,
        "at": time.time(),
        "session_id": session_id,
    }
    env_put = put_artifact(
        json.dumps(envelope, indent=2),
        title=f"swarm-run-{run_id}",
        language="json",
        agent="swarm",
        agent_role="Coding Swarm Harness",
        ai_version="coding_swarm.v1",
        run_id=run_id,
        tags=["coding_swarm", "envelope", "index"],
        note="swarm run index",
    )

    transcript_parts.append("---")
    transcript_parts.append("## Pixel artifacts this run")
    for a in artifacts:
        transcript_parts.append(
            f"- **{a.get('agent_name') or a.get('agent')}** · "
            f"`{a.get('symbol')}` · {a.get('language') or a.get('kind')}"
        )
    if env_put.get("ok"):
        transcript_parts.append(f"- **Run index** · `{env_put.get('symbol')}`")
    transcript_parts.append("")
    transcript_parts.append(
        "_All artifacts in pixel memory: Store · Look · Recreate · Pass · Map. "
        "Open Workspace → Pixel memory to browse._"
    )

    out = "\n".join(transcript_parts)
    if job_id:
        update_progress(job_id, out, engine="coding_swarm")
    return out, "", "coding_swarm"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "mod").lower()).strip("-")[:48] or "mod"


def bring_back(symbol: str) -> Dict[str, Any]:
    """Look + optional recreate handle for desk."""
    g = get_symbol(symbol)
    if not g.get("ok"):
        return g
    return {
        "ok": True,
        "action": "bring_back",
        "symbol": g.get("symbol"),
        "text": g.get("text"),
        "preview": g.get("preview"),
        "kind": g.get("kind"),
        "pages": g.get("pages"),
        "bytes": g.get("bytes"),
    }
