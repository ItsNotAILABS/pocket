"""First-class agent registry — every POCKET agent elevated and discoverable.

Unifies:
  - Desk session modes (Codex, Grok, Claude, Voice, Swarm, …)
  - Headless product catalog (researcher, coder, …)
  - Coding swarm personas (Sophia, Solver, Twin)
  - Latin workers, DESIGN, headless mesh, ship pack
  - Custom agents on disk
  - Agent OS systems

Each entry is first_class=True with: id, name, role, kind, group, color,
desk_mode, engine, mention, api, blurb, status probe.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set

# ---------------------------------------------------------------------------
# Colors by family
# ---------------------------------------------------------------------------
C = {
    "engine": "#22c55e",
    "research": "#06b6d4",
    "plan": "#eab308",
    "voice": "#0b84fe",
    "swarm": "#c084fc",
    "build": "#f472b6",
    "host": "#a78bfa",
    "mesh": "#34d399",
    "design": "#22d3ee",
    "ship": "#fb7185",
    "latin": "#10a37f",
    "local": "#fbbf24",
    "security": "#f87171",
    "wiki": "#a78bfa",
    "default": "#94a3b8",
}


def _e(
    id: str,
    name: str,
    role: str,
    *,
    kind: str,
    group: str,
    color: str = "",
    desk_mode: str = "",
    engine: str = "",
    mention: str = "",
    blurb: str = "",
    harness: bool = False,
    pixel: bool = True,
    first_class: bool = True,
    aliases: Optional[List[str]] = None,
    surfaces: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "id": id,
        "name": name,
        "role": role,
        "kind": kind,  # desk | catalog | swarm | latin | design | headless | ship | mesh | custom | system
        "group": group,
        "color": color or C["default"],
        "desk_mode": desk_mode or (id if kind == "desk" else ""),
        "engine": engine or desk_mode or id,
        "mention": mention or (id.upper() if kind in ("latin", "design", "headless", "ship") else ""),
        "blurb": blurb or role,
        "harness": harness,  # parent agents that spawn subagents
        "pixel": pixel,  # writes/reads pixel memory
        "first_class": first_class,
        "aliases": aliases or [],
        "surfaces": surfaces or (["desk", "phone"] if id in ("voice", "work", "plan", "codex", "grok") else ["desk"]),
    }


def _desk_agents() -> List[Dict[str, Any]]:
    """All desk session agents — first-class IDE / chat modes."""
    return [
        # Primary engines
        _e(
            "codex",
            "Codex",
            "First-class host coding agent",
            kind="desk",
            group="Primary",
            color=C["engine"],
            desk_mode="codex",
            engine="codex",
            harness=True,
            blurb="OpenAI Codex CLI on this PC — desk, PhoneAI OS, harness, RAH leaf",
            surfaces=["desk", "phone"],
            aliases=["@codex", "openai-codex"],
        ),
        _e("grok", "Grok", "Code + research agent", kind="desk", group="Primary", color=C["research"], desk_mode="grok", engine="grok", harness=True, blurb="Code, research, reorganize · harnessed"),
        _e(
            "gemini_coder",
            "gemini-coder",
            "Neuro-Silicon coding lane",
            kind="desk",
            group="Primary",
            color="#34d399",
            desk_mode="grok",
            engine="grok",
            harness=True,
            blurb="Calibration alias → Grok/Codex job on measured host lanes",
            aliases=["gemini-coder", "gemini", "@gemini-coder"],
        ),
        _e(
            "sprint_orchestrator",
            "sprint-orchestrator",
            "Neuro-Silicon swarm orchestrator",
            kind="desk",
            group="Build",
            color="#f43f5e",
            desk_mode="rah",
            engine="rah",
            harness=True,
            blurb="Calibration alias → RAH/HYDRA fan-out",
            aliases=["sprint-orchestrator", "sprint", "@sprint-orchestrator"],
        ),
        _e("claude", "Claude", "Agent SDK tool loop", kind="desk", group="Primary", color=C["plan"], desk_mode="claude", engine="claude", harness=True, blurb="Claude Agent SDK · tools · receipts"),
        _e("plan", "Plan", "Planning only", kind="desk", group="Primary", color=C["plan"], desk_mode="plan", engine="plan", harness=True, blurb="Outline only — no file writes"),
        _e("voice", "Voice ↔ Voice", "Specialized voice agent", kind="desk", group="Primary", color=C["voice"], desk_mode="voice", engine="voice", harness=False, blurb="Aria · first-class desk + phone · patient VAD · Fusion", surfaces=["desk","phone"]),
        _e(
            "mailbox",
            "Mailbox",
            "First-class agent mail",
            kind="desk",
            group="Primary",
            color="#34d399",
            desk_mode="mail",
            engine="mail",
            harness=False,
            blurb="Own repo ItsNotAILABS/pocket-mailbox · agents.pocket.local · threads · search · :8792",
            surfaces=["desk", "phone"],
            aliases=["mail", "agent-mail", "@mailbox"],
        ),
        _e(
            "muse_spark",
            "Muse Spark",
            "Meta multimodal reasoning",
            kind="desk",
            group="Primary",
            color="#a855f7",
            desk_mode="muse_spark",
            engine="muse_spark",
            harness=True,
            blurb="Muse Spark · parallel lanes · multimodal · open meta.ai · voice engine OK",
            surfaces=["desk", "phone"],
            aliases=["muse", "spark", "muse-spark", "musespark"],
        ),
        # Build / ship
        _e("coding_swarm", "Coding Swarm", "Sophia · Solver · Twin", kind="desk", group="Build", color=C["swarm"], desk_mode="coding_swarm", engine="coding_swarm", harness=False, blurb="Multi-agent code → pixel artifacts"),
        _e("build", "Build", "Multi-agent ship loop", kind="desk", group="Build", color=C["build"], desk_mode="build", engine="build", harness=True, blurb="Plan → code → test → ship"),
        _e("ship", "Ship", "Release ship loop", kind="desk", group="Build", color=C["build"], desk_mode="ship", engine="build", harness=True, blurb="Same multi-step ship factory"),
        _e("use_case", "Use cases", "Playbook runner", kind="desk", group="Build", color=C["build"], desk_mode="use_case", engine="build", harness=True, blurb="Real product use cases"),
        _e("emergent", "Emergent", "Ship factory", kind="desk", group="Build", color=C["build"], desk_mode="emergent", engine="build", harness=True, blurb="Emergent-parity multi-agent ship"),
        _e("loop", "Agent loop", "Managed loop", kind="desk", group="Build", color=C["build"], desk_mode="loop", engine="build", harness=True, blurb="Managed multi-step agent loop"),
        _e("wiki", "Infinite Wiki", "Codebase navigator", kind="desk", group="Build", color=C["wiki"], desk_mode="wiki", engine="wiki", harness=True, blurb="Profile cards · never dump whole files"),
        _e("dual", "Dual loop", "Cortex + Subcortex", kind="desk", group="Build", color="#818cf8", desk_mode="dual", engine="dual", harness=False, blurb="Chat while background work runs"),
        _e("custom_agent", "Custom agent", "Builder + tools", kind="desk", group="Build", color=C["swarm"], desk_mode="custom_agent", engine="custom_agent", harness=True, blurb="Your tools, roles, sub-agents"),
        # Host / embodiment
        _e("web", "Web", "Search + fetch", kind="desk", group="Host", color="#38bdf8", desk_mode="web", engine="web", harness=False, blurb="Search and fetch the web"),
        _e("git", "Git", "Vault repos", kind="desk", group="Host", color="#94a3b8", desk_mode="git", engine="git", harness=False, blurb="Sovereign git / forge"),
        _e("desktop", "Desktop", "Open apps", kind="desk", group="Host", color=C["host"], desk_mode="desktop", engine="desktop", harness=False, blurb="Open apps on this PC"),
        _e("browser", "Browser agent", "Real-world browser", kind="desk", group="Host", color="#f97316", desk_mode="browser", engine="browser", harness=False, blurb="Edge · X · Copilot automation"),
        _e("capture", "Capture", "Screenshots", kind="desk", group="Host", color="#a3e635", desk_mode="capture", engine="capture", harness=False, blurb="Screenshot / snip"),
        _e(
            "studio",
            "Product Studio",
            "Record · polish · viral ship",
            kind="desk",
            group="Host",
            color="#34d399",
            desk_mode="studio",
            engine="studio",
            harness=True,
            blurb="First-class Studio · record · storyboard · viral pack · caption · ship",
            surfaces=["desk", "studio"],
            aliases=["product_studio", "video_studio", "viral"],
        ),
        _e("vision", "Vision", "OCULUS sensory layer", kind="desk", group="Host", color="#22d3ee", desk_mode="vision", engine="vision", harness=False, blurb="Observe · UI map · OCR · click-by-name"),
        _e("screen", "Screen share", "Fusion + VComputer", kind="desk", group="Host", color="#67e8f9", desk_mode="screen", engine="screen", harness=False, blurb="Share screen View/Control · all agents see fusion"),
        _e("vcomp", "VComputer", "Virtual computer", kind="desk", group="Host", color="#a5f3fc", desk_mode="vcomp", engine="vcomp", harness=False, blurb="Host machine surface · sense · click · type · shell"),
        _e("work", "Working mode", "Live voice + hardware", kind="desk", group="Primary", color="#f472b6", desk_mode="work", engine="work", harness=True, blurb="Persistent: Aria voice · screen Control · package→artifacts · phone+desk", surfaces=["desk","phone"]),
        _e("power", "Power", "GO + host command plane", kind="desk", group="Primary", color="#10a37f", desk_mode="assist", engine="assist", harness=True, blurb="Do a goal · GO active states · 100 workflows on this host", surfaces=["desk"], aliases=["go", "command"]),
        _e("working", "Working mode", "Work alias", kind="desk", group="Primary", color="#f472b6", desk_mode="working", engine="work", blurb="Alias → work"),
        _e("mcp", "MCP tools", "10 embedded MCPs", kind="desk", group="Advanced", color="#c4b5fd", desk_mode="mcp", engine="mcp", harness=False, blurb="3 internal + 7 external · agent CLI access (no user tabs)"),
        _e("oculus", "Vision", "OCULUS alias", kind="desk", group="Host", color="#22d3ee", desk_mode="oculus", engine="vision", harness=False, blurb="Alias → vision"),
        _e("see", "Vision", "See alias", kind="desk", group="Host", color="#22d3ee", desk_mode="see", engine="vision", harness=False, blurb="Alias → vision"),
        _e("cowork", "Cowork", "Desk + record", kind="desk", group="Host", color=C["build"], desk_mode="cowork", engine="cowork", harness=False, blurb="Cowork desk demo + record"),
        _e("offload", "Offload", "Background tickets", kind="desk", group="Host", color=C["local"], desk_mode="offload", engine="offload", harness=False, blurb="Background real-world queue"),
        _e("repos", "Repos", "GitHub links", kind="desk", group="Host", color="#94a3b8", desk_mode="repos", engine="repos", harness=False, blurb="Repo listing and open"),
        _e("github", "GitHub", "First-class GitHub", kind="desk", group="Host", color="#e6edf3", desk_mode="github", engine="github", harness=False, blurb="gh status · repos · issues · PRs · clone · create"),
        _e("gh", "GitHub", "gh alias", kind="desk", group="Host", color="#e6edf3", desk_mode="gh", engine="github", harness=False, blurb="Alias → github"),
        _e("term", "Term", "Live terminal", kind="desk", group="Host", color=C["mesh"], desk_mode="term", engine="term", harness=False, blurb="Long-lived host terminal"),
        _e("shell", "Shell", "One-shot shell", kind="desk", group="Host", color=C["mesh"], desk_mode="shell", engine="shell", harness=False, blurb="One-shot PowerShell (admin)"),
        _e("wsl_native", "WSL", "Linux hands", kind="desk", group="Host", color="#8b5cf6", desk_mode="wsl_native", engine="wsl", harness=False, blurb="Native Linux workspace"),
        # Intelligence / local
        _e("nexus", "NEXUS", "Intelligence tools", kind="desk", group="Advanced", color=C["build"], desk_mode="nexus", engine="nexus", harness=False, blurb="NEXUS intelligence bridge"),
        _e("mesie", "MESIE", "Spectral compute", kind="desk", group="Advanced", color=C["host"], desk_mode="mesie", engine="mesie", harness=False, blurb="MESIE spectral / compute"),
        _e("auro", "Auro14B", "Local LMR + meaning", kind="desk", group="Internal", color=C["local"], desk_mode="auro", engine="auro", harness=False, blurb="Native Auro LMR + meaning model · prefix native for full ckpt"),
        _e(
            "auro-endure",
            "Auro Endure",
            "Experiment and endure",
            kind="desk",
            group="Internal",
            color=C["local"],
            desk_mode="auro-endure",
            engine="auro-endure",
            harness=True,
            blurb="Auro14B adapter: experiment variants and keep looping. Not learning until native stateful evaluation exists.",
            surfaces=["desk", "phone"],
            aliases=["endure", "auro_endure", "experiment-endure"],
        ),
        _e(
            "team-workspace",
            "Team workspace",
            "Tenant-jailed long work",
            kind="desk",
            group="Host",
            color=C["host"],
            desk_mode="team",
            engine="team",
            harness=True,
            blurb="Founder-only team folder under ~/.pocket/tenants/<principal>/teams. Jobs inherit jailed cwd.",
            surfaces=["desk"],
            aliases=["team", "long-work", "team_workspace"],
        ),
        _e(
            "assist",
            "Digital assistant",
            "Real-life help",
            kind="desk",
            group="Primary",
            color="#2dd4bf",
            desk_mode="assist",
            engine="assist",
            harness=True,
            blurb="Day-to-day assistant · research · life ops · routes engines",
            surfaces=["desk", "phone", "work"],
        ),
        _e("guppy", "Guppy", "Local helper", kind="desk", group="Internal", color="#38bdf8", desk_mode="guppy", engine="guppy", harness=False, blurb="Local fish helper"),
        _e("archon", "ARCHON", "Orchestrator", kind="desk", group="Advanced", color=C["security"], desk_mode="archon", engine="archon", harness=True, blurb="Desk alpha orchestrator"),
        _e("copilot", "Copilot", "Windows Copilot", kind="desk", group="Advanced", color="#818cf8", desk_mode="copilot", engine="copilot", harness=False, blurb="Consiliarius · Copilot intro"),
        _e("agent", "Doer", "Headless multi-step", kind="desk", group="Advanced", color=C["build"], desk_mode="agent", engine="agent", harness=True, blurb="≤10 step headless doer"),
        _e("doer", "Doer+", "Headless multi-step", kind="desk", group="Advanced", color=C["build"], desk_mode="doer", engine="agent", harness=True, blurb="Headless multi-step runner"),
        _e("swarm", "Swarm", "Coding or always-on", kind="desk", group="Advanced", color=C["mesh"], desk_mode="swarm", engine="swarm", harness=False, blurb="Coding swarm or status/pulse daemon"),
        _e("novae_grok", "Grok Novae", "Nova · research hands", kind="desk", group="Primary", color=C["host"], desk_mode="novae_grok", engine="novae_grok", harness=False, blurb="Nova in POCKET: research, plan, browser, real-world assist", surfaces=["desk","phone","imagine"]),
        _e("novae_codex", "Codex Novae", "Nova · coding hands", kind="desk", group="Primary", color=C["mesh"], desk_mode="novae_codex", engine="novae_codex", harness=False, blurb="Nova in POCKET: coding, forge, workspace patches", surfaces=["desk","phone"]),
        _e("dream", "Dream", "Idle consolidator", kind="desk", group="Advanced", color="#a78bfa", desk_mode="dream", engine="dream", harness=False, blurb="Dream mode · idle consolidation"),
        _e("duel", "Duels", "Propose & judge", kind="desk", group="Advanced", color="#fb7185", desk_mode="duel", engine="duel", harness=False, blurb="Agent duels"),
        _e("capsule", "Time Capsules", "Future instructions", kind="desk", group="Advanced", color="#94a3b8", desk_mode="capsule", engine="capsule", harness=False, blurb="Time capsules"),
        _e("serendipity", "Serendipity", "Unexpected links", kind="desk", group="Advanced", color="#fbbf24", desk_mode="serendipity", engine="serendipity", harness=False, blurb="Serendipitous connections"),
        _e("proof", "Proof chain", "Work receipts", kind="desk", group="Advanced", color="#86efac", desk_mode="proof", engine="proof", harness=False, blurb="Proof / receipt chain"),
        _e("workers", "Workers", "Latin roster", kind="desk", group="Advanced", color=C["latin"], desk_mode="workers", engine="workers", harness=False, blurb="List Latin workers"),
        _e("ask", "Ask", "Quick plan", kind="desk", group="Advanced", color=C["plan"], desk_mode="ask", engine="ask", harness=False, blurb="Quick planning ask"),
        _e("handoff", "Handoff", "Plan package", kind="desk", group="Advanced", color="#a1a1aa", desk_mode="handoff", engine="handoff", harness=False, blurb="Deferred plan handoff"),
        _e("ghost", "Ghost Math", "Internal math", kind="desk", group="Internal", color="#c4b5fd", desk_mode="ghost", engine="ghost", harness=False, blurb="Internal math: hash, gcd, primes, phi — no third-party"),
        _e("logic", "Logic Prover", "Internal proofs", kind="desk", group="Internal", color="#86efac", desk_mode="logic", engine="logic", harness=False, blurb="Local tautologies and contradictions — no CAS cloud"),
        _e("pattern", "Pattern Forge", "Internal spectral", kind="desk", group="Internal", color="#a78bfa", desk_mode="pattern", engine="pattern", harness=False, blurb="Local pattern decompose — no third-party math API"),
        _e("world", "World Model", "Intelligence world", kind="desk", group="Internal", color="#fbbf24", desk_mode="world", engine="world", harness=False, blurb="Internal memory: facts, archetypes, syntax"),
        _e("imagine", "Imagine Studio", "Visual stills", kind="desk", group="Internal", color="#34d399", desk_mode="imagine", engine="imagine", harness=False, blurb="Letterboxed phone/laptop stills from host screen", surfaces=["desk","phone","imagine"]),
        _e("genetic", "Genetic flow", "Internal models", kind="desk", group="Internal", color="#34d399", desk_mode="genetic", engine="genetic", harness=False, blurb="Express internal AI modules on a goal"),
        _e("bots", "POCKET Bots", "Teammates", kind="desk", group="Primary", color="#10a37f", desk_mode="bots", engine="bots", harness=True, blurb="Grok-Bot-style teammates · own computer · pocket-agent", surfaces=["desk","phone","bots"]),
        _e("woa", "Wrapped Orch", "Orchestrator LLM", kind="desk", group="Advanced", color="#f472b6", desk_mode="woa", engine="woa", harness=False, blurb="Wrapped orchestrator"),
        # Aliases as first-class desk modes (same agent, different id)
        _e("pixel_swarm", "Coding Swarm", "Pixel swarm alias", kind="desk", group="Build", color=C["swarm"], desk_mode="pixel_swarm", engine="coding_swarm", blurb="Alias → coding swarm"),
        _e("harness", "Coding Swarm", "Harness alias", kind="desk", group="Build", color=C["swarm"], desk_mode="harness", engine="coding_swarm", blurb="Alias → coding swarm"),
        _e("v2v", "Voice ↔ Voice", "Voice alias", kind="desk", group="Primary", color=C["voice"], desk_mode="v2v", engine="voice", blurb="Alias → voice agent"),
        _e("infinite_wiki", "Infinite Wiki", "Wiki alias", kind="desk", group="Build", color=C["wiki"], desk_mode="infinite_wiki", engine="wiki", blurb="Alias → wiki"),
        _e("codebase", "Infinite Wiki", "Wiki alias", kind="desk", group="Build", color=C["wiki"], desk_mode="codebase", engine="wiki", blurb="Alias → wiki"),
        _e("alpha", "ARCHON", "Alpha alias", kind="desk", group="Advanced", color=C["security"], desk_mode="alpha", engine="archon", harness=True, blurb="Alias → ARCHON"),
        _e("wsl", "WSL", "WSL alias", kind="desk", group="Host", color="#8b5cf6", desk_mode="wsl", engine="wsl", blurb="Alias → WSL"),
        _e("linux", "WSL", "Linux alias", kind="desk", group="Host", color="#8b5cf6", desk_mode="linux", engine="wsl", blurb="Alias → WSL"),
        _e("novae", "Grok Novae", "Novae alias", kind="desk", group="Advanced", color=C["host"], desk_mode="novae", engine="novae_grok", blurb="Alias → Grok Novae"),
        _e("auro14b", "Auro14B", "Auro alias", kind="desk", group="Advanced", color=C["local"], desk_mode="auro14b", engine="auro", blurb="Alias → Auro"),
        _e("forge", "Git Forge", "Forge alias", kind="desk", group="Host", color="#94a3b8", desk_mode="forge", engine="git", blurb="Alias → git/forge"),
        _e("demo", "Cowork Demo", "Demo alias", kind="desk", group="Host", color=C["build"], desk_mode="demo", engine="cowork", blurb="Alias → cowork"),
        _e("work", "Cowork", "Work alias", kind="desk", group="Host", color=C["build"], desk_mode="work", engine="cowork", blurb="Alias → cowork"),
        _e("cortex", "Dual loop", "Cortex alias", kind="desk", group="Build", color="#818cf8", desk_mode="cortex", engine="dual", blurb="Alias → dual"),
        _e("subcortex", "Dual loop", "Subcortex alias", kind="desk", group="Build", color="#818cf8", desk_mode="subcortex", engine="dual", blurb="Alias → dual"),
        _e("math", "Ghost Math", "Math alias", kind="desk", group="Advanced", color="#c4b5fd", desk_mode="math", engine="ghost", blurb="Alias → ghost"),
        _e("ghost-math", "Ghost Math", "Math alias", kind="desk", group="Advanced", color="#c4b5fd", desk_mode="ghost-math", engine="ghost", blurb="Alias → ghost"),
        _e("sovereign-git", "Git", "Git alias", kind="desk", group="Host", color="#94a3b8", desk_mode="sovereign-git", engine="git", blurb="Alias → git"),
        _e("embody", "Offload", "Embody alias", kind="desk", group="Host", color=C["local"], desk_mode="embody", engine="offload", blurb="Alias → offload"),
        _e("embodiment", "Offload", "Embody alias", kind="desk", group="Host", color=C["local"], desk_mode="embodiment", engine="offload", blurb="Alias → offload"),
        _e("realworld", "Offload", "Realworld alias", kind="desk", group="Host", color=C["local"], desk_mode="realworld", engine="offload", blurb="Alias → offload"),
        _e("wrapped_orch", "Wrapped Orch", "WOA alias", kind="desk", group="Advanced", color="#f472b6", desk_mode="wrapped_orch", engine="woa", blurb="Alias → woa"),
        _e("wrapped-orch", "Wrapped Orch", "WOA alias", kind="desk", group="Advanced", color="#f472b6", desk_mode="wrapped-orch", engine="woa", blurb="Alias → woa"),
        _e("code_swarm", "Coding Swarm", "Swarm alias", kind="desk", group="Build", color=C["swarm"], desk_mode="code_swarm", engine="coding_swarm", blurb="Alias → coding swarm"),
        _e("swarm_code", "Coding Swarm", "Swarm alias", kind="desk", group="Build", color=C["swarm"], desk_mode="swarm_code", engine="coding_swarm", blurb="Alias → coding swarm"),
        _e("voice_agent", "Voice ↔ Voice", "Voice alias", kind="desk", group="Primary", color=C["voice"], desk_mode="voice_agent", engine="voice", blurb="Alias → voice"),
        _e("voice2voice", "Voice ↔ Voice", "Voice alias", kind="desk", group="Primary", color=C["voice"], desk_mode="voice2voice", engine="voice", blurb="Alias → voice"),
        _e("novae-grok", "Grok Novae", "Novae alias", kind="desk", group="Advanced", color=C["host"], desk_mode="novae-grok", engine="novae_grok", blurb="Alias → novae grok"),
        _e("novae-codex", "Codex Novae", "Novae alias", kind="desk", group="Advanced", color=C["mesh"], desk_mode="novae-codex", engine="novae_codex", blurb="Alias → novae codex"),
        _e("wsl-native", "WSL", "WSL alias", kind="desk", group="Host", color="#8b5cf6", desk_mode="wsl-native", engine="wsl", blurb="Alias → WSL"),
    ]


def _catalog_agents() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    # Only map catalog SKUs onto real desk modes when engine is a desk runner
    desk_engines = {
        "codex", "grok", "claude", "plan", "web", "shell", "nexus", "desktop",
        "agent", "guppy", "browser", "capture", "repos", "copilot", "build",
    }
    try:
        from pocket.agents import AGENTS

        for aid, meta in (AGENTS or {}).items():
            eng = str(meta.get("engine") or aid)
            out.append(
                _e(
                    f"catalog:{aid}",
                    str(meta.get("name") or aid),
                    str(meta.get("role") or meta.get("description") or "headless"),
                    kind="catalog",
                    group="Headless catalog",
                    color=C["research"] if eng == "web" else C["engine"],
                    desk_mode=eng if eng in desk_engines else "",
                    engine=eng,
                    blurb=str(meta.get("description") or meta.get("role") or ""),
                    harness=eng in ("codex", "grok", "claude", "plan", "build", "agent"),
                    pixel=True,
                )
            )
    except Exception:
        pass
    return out


def _swarm_personas() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        from pocket.coding_swarm import ROSTER, list_roster

        live = {a["id"]: a for a in (list_roster().get("agents") or [])}
        for aid, meta in ROSTER.items():
            bound = live.get(aid) or {}
            out.append(
                _e(
                    f"swarm:{aid}",
                    str(meta.get("name") or aid),
                    str(meta.get("role") or "swarm"),
                    kind="swarm",
                    group="Coding Swarm",
                    color=str(meta.get("color") or C["swarm"]),
                    desk_mode="coding_swarm",
                    engine=str(bound.get("bound_engine") or meta.get("ai_version_label") or "plan"),
                    mention=aid,
                    blurb=f"AI-bound · {bound.get('ai_version') or meta.get('ai_version_label') or 'local'}",
                    aliases=list(meta.get("aliases") or []),
                    harness=False,
                    pixel=True,
                )
            )
    except Exception:
        pass
    return out


def _latin() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        from pocket.alpha_workers import list_workers

        for w in list_workers():
            wid = str(w.get("id") or w.get("latin") or "").upper()
            if not wid:
                continue
            out.append(
                _e(
                    f"latin:{wid}",
                    wid,
                    str(w.get("role") or w.get("meaning") or "latin worker"),
                    kind="latin",
                    group="Latin workers",
                    color=C["latin"],
                    mention=wid,
                    engine="latin",
                    blurb=str(w.get("meaning") or w.get("role") or "mesh latin"),
                    harness=False,
                )
            )
    except Exception:
        pass
    return out


def _mesh_pack() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    design = ("DESIGN", "AESTHETE", "LAYOUT", "MOTION")
    headless = {
        "FORGE_HEADLESS": "Build/test/package",
        "SENTINEL_HEADLESS": "Security + audit",
        "RESEARCH_HEADLESS": "Research packs",
        "SHIP_HEADLESS": "Release / beta ship",
    }
    ship = ("MARKETING", "DEMO", "ELECTRON")
    for d in design:
        out.append(
            _e(
                f"design:{d}",
                d,
                "design specialist",
                kind="design",
                group="Design mesh",
                color=C["design"],
                mention=d,
                engine="design",
                blurb="UI/product craft · @mention from any chat",
            )
        )
    for h, role in headless.items():
        out.append(
            _e(
                f"headless:{h}",
                h,
                role,
                kind="headless",
                group="Headless mesh",
                color=C["mesh"],
                mention=h,
                engine="headless",
                blurb=f"{role} · harness auto-spawn",
            )
        )
    for s in ship:
        out.append(
            _e(
                f"ship:{s}",
                s,
                "ship pack",
                kind="ship",
                group="Ship mesh",
                color=C["ship"],
                mention=s,
                engine="ship",
                blurb="Marketing / demo / desktop ship",
            )
        )
    return out


def _custom() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        from pocket.custom_agents import list_agents

        for a in list_agents() or []:
            if not isinstance(a, dict):
                continue
            cid = str(a.get("id") or a.get("name") or "").strip()
            if not cid:
                continue
            out.append(
                _e(
                    f"custom:{cid}",
                    str(a.get("name") or cid),
                    str(a.get("role") or "custom"),
                    kind="custom",
                    group="Custom",
                    color=C["swarm"],
                    desk_mode="custom_agent",
                    engine="custom_agent",
                    blurb=str(a.get("personality") or a.get("role") or "user-defined"),
                    harness=True,
                    pixel=True,
                )
            )
    except Exception:
        pass
    return out


def build_registry(*, live: bool = False) -> Dict[str, Any]:
    agents: List[Dict[str, Any]] = []
    agents.extend(_desk_agents())
    agents.extend(_catalog_agents())
    agents.extend(_swarm_personas())
    agents.extend(_latin())
    agents.extend(_mesh_pack())
    agents.extend(_custom())

    # Dedupe by id
    seen: Set[str] = set()
    uniq: List[Dict[str, Any]] = []
    for a in agents:
        i = a["id"]
        if i in seen:
            continue
        seen.add(i)
        if live:
            a = {**a, "status": _probe(a)}
        uniq.append(a)

    by_group: Dict[str, List[Dict[str, Any]]] = {}
    for a in uniq:
        by_group.setdefault(a["group"], []).append(a)

    desk_modes = sorted({a["desk_mode"] for a in uniq if a.get("desk_mode")})
    harness_parents = [a["id"] for a in uniq if a.get("harness") and a.get("kind") == "desk"]

    return {
        "ok": True,
        "schema": "pocket.first_class_agents.v1",
        "first_class": True,
        "count": len(uniq),
        "agents": uniq,
        "by_group": {g: len(v) for g, v in by_group.items()},
        "groups": by_group,
        "desk_modes": desk_modes,
        "harness_parents": harness_parents,
        "at": time.time(),
        "doctrine": "Every agent is first-class — desk mode, mesh worker, or catalog SKU.",
    }


def _probe(a: Dict[str, Any]) -> str:
    kind = a.get("kind")
    try:
        if a.get("id") == "codex":
            from pocket.executor import which_codex

            return "ready" if which_codex() else "cli-missing"
        if kind == "desk":
            return "ready"
        if kind == "swarm":
            return "ready"
        if kind in ("latin", "design", "headless", "ship"):
            return "ready"
        if kind == "catalog":
            return "catalog"
        if kind == "custom":
            return "ready"
    except Exception:
        return "unknown"
    return "ready"


def desk_catalog() -> Dict[str, Any]:
    """Shape for desk AGENT_CATALOG — Primary/Build/Host/Advanced only (no aliases dump)."""
    reg = build_registry(live=False)
    # Prefer non-alias desk agents for picker (skip pure aliases with same name as another)
    primary_ids = {"codex", "grok", "claude", "voice", "plan", "novae_grok", "novae_codex", "assist", "bots"}
    internal_ids = {
        "ghost",
        "logic",
        "pattern",
        "world",
        "imagine",
        "genetic",
        "auro",
        "guppy",
    }
    build_ids = {
        "coding_swarm",
        "build",
        "ship",
        "use_case",
        "emergent",
        "loop",
        "wiki",
        "dual",
        "custom_agent",
    }
    host_ids = {
        "web",
        "git",
        "desktop",
        "browser",
        "capture",
        "studio",
        "vision",
        "screen",
        "vcomp",
        "cowork",
        "offload",
        "repos",
        "github",
        "term",
        "shell",
        "wsl_native",
        "power",
    }
    advanced_ids = {
        "swarm",
        "nexus",
        "mesie",
        "archon",
        "copilot",
        "agent",
        "doer",
        "dream",
        "duel",
        "capsule",
        "serendipity",
        "proof",
        "workers",
        "ask",
        "handoff",
        "woa",
    }
    by_id = {a["desk_mode"] or a["id"]: a for a in reg["agents"] if a.get("kind") == "desk"}

    def items(ids: Set[str]) -> List[Dict[str, Any]]:
        out = []
        for i in ids:
            a = by_id.get(i)
            if not a:
                continue
            out.append(
                {
                    "id": a["desk_mode"] or a["id"],
                    "name": a["name"],
                    "blurb": a["blurb"],
                    "color": a["color"],
                    "harness": a.get("harness"),
                    "first_class": True,
                }
            )
        return out

    groups = [
        {"group": "Primary", "items": items(primary_ids)},
        {"group": "Internal", "items": items(internal_ids)},
        {"group": "Build", "items": items(build_ids)},
        {"group": "Host", "items": items(host_ids)},
        {"group": "Advanced", "items": items(advanced_ids)},
        {
            "group": "Coding Swarm",
            "items": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "blurb": a["blurb"],
                    "color": a["color"],
                    "desk_mode": "coding_swarm",
                    "mention": a.get("mention"),
                    "first_class": True,
                }
                for a in reg["agents"]
                if a.get("kind") == "swarm"
            ],
        },
        {
            "group": "Mesh helpers",
            "items": [
                {
                    "id": a["mention"] or a["id"],
                    "name": a["name"],
                    "blurb": a["blurb"],
                    "color": a["color"],
                    "mention": a.get("mention"),
                    "first_class": True,
                }
                for a in reg["agents"]
                if a.get("kind") in ("latin", "design", "headless", "ship")
            ],
        },
        {
            "group": "Headless catalog",
            "items": [
                {
                    "id": a["id"].replace("catalog:", ""),
                    "name": a["name"],
                    "blurb": a["blurb"],
                    "color": a["color"],
                    "engine": a.get("engine"),
                    "first_class": True,
                }
                for a in reg["agents"]
                if a.get("kind") == "catalog"
            ],
        },
        {
            "group": "Custom",
            "items": [
                {
                    "id": a["id"].replace("custom:", ""),
                    "name": a["name"],
                    "blurb": a["blurb"],
                    "color": a["color"],
                    "desk_mode": "custom_agent",
                    "first_class": True,
                }
                for a in reg["agents"]
                if a.get("kind") == "custom"
            ],
        },
    ]
    return {
        "ok": True,
        "schema": "pocket.desk_catalog.v1",
        "first_class": True,
        "groups": groups,
        "count": sum(len(g["items"]) for g in groups),
        "registry_count": reg["count"],
    }


def session_titles() -> Dict[str, str]:
    """Default session titles for every desk mode."""
    reg = build_registry(live=False)
    titles: Dict[str, str] = {}
    for a in reg["agents"]:
        if a.get("kind") != "desk":
            continue
        mode = a.get("desk_mode") or ""
        if mode:
            titles[mode] = a["name"] if "alias" not in (a.get("blurb") or "").lower() else a["name"]
            # Prefer longer product titles
            if a.get("blurb") and "Alias" not in a["blurb"]:
                titles[mode] = f"{a['name']}"
    # Richer titles for key modes
    titles.update(
        {
            "codex": "Codex agent",
            "grok": "Grok coding agent",
            "claude": "Claude Agent SDK",
            "voice": "Aria · Voice persona",
            "vision": "OCULUS Vision",
            "oculus": "OCULUS Vision",
            "github": "GitHub",
            "gh": "GitHub",
            "coding_swarm": "Coding Swarm · pixel artifacts",
            "plan": "Planning AI chat",
            "build": "Build loop · multi-agent ship",
        }
    )
    return titles


def ensure_modes_aligned() -> Dict[str, Any]:
    """Ensure sessions.MODES and jobs.VALID_MODES include every desk agent."""
    reg = build_registry(live=False)
    desk_modes = {a["desk_mode"] for a in reg["agents"] if a.get("desk_mode")}
    from pocket import sessions as sess_mod
    from pocket import jobs as jobs_mod

    missing_sess = sorted(desk_modes - set(sess_mod.MODES))
    missing_jobs = sorted(desk_modes - set(jobs_mod.VALID_MODES))
    # Runtime extend (frozenset → new frozenset)
    if missing_sess:
        sess_mod.MODES = frozenset(set(sess_mod.MODES) | desk_modes)
    if missing_jobs:
        jobs_mod.VALID_MODES = frozenset(set(jobs_mod.VALID_MODES) | desk_modes)
    return {
        "ok": True,
        "desk_modes": len(desk_modes),
        "added_sessions": missing_sess,
        "added_jobs": missing_jobs,
    }


def summary() -> Dict[str, Any]:
    reg = build_registry(live=True)
    cat = desk_catalog()
    ensure_modes_aligned()
    return {
        "ok": True,
        "first_class": True,
        "total_agents": reg["count"],
        "desk_catalog_items": cat["count"],
        "groups": reg["by_group"],
        "harness_parents": reg["harness_parents"],
        "doctrine": reg["doctrine"],
    }
