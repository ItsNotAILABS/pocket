"""Real PC agent execution — Codex / Claude / shell / WSL / Grok handoff."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pocket.jobs import WORK_DIR

PARALLAX_ROOT = r"E:\PARALLAX-Exchange-Clearinghouse"
AURO_ROOT = str(Path.home() / "Documents" / "GitHub" / "Auro14B")

KNOWN_WORKSPACES: List[Dict[str, str]] = [
    {
        "id": "parallax",
        "label": "PARALLAX Exchange Clearinghouse",
        "path": PARALLAX_ROOT,
    },
    {
        "id": "pocket",
        "label": "POCKET itself",
        "path": str(Path.home() / "OneDrive" / "pocket-os"),
    },
    {
        "id": "auro",
        "label": "Auro14B / RO14B",
        "path": AURO_ROOT,
    },
    {
        "id": "hz",
        "label": "HZ Offline mesh",
        "path": str(Path.home() / "OneDrive" / "hz-offline"),
    },
    {
        "id": "monad",
        "label": "MonadBuilder / Hackaton",
        "path": str(Path.home() / "Documents" / "GitHub" / "Monad-Hackaton"),
    },
    {
        "id": "mesie",
        "label": "MESIE engine",
        "path": str(Path.home() / "Multi-Element-Spectral-Intelligence-Engine-MESIE-"),
    },
    {
        "id": "tokenomics",
        "label": "Tokenomics desk",
        "path": str(WORK_DIR / "tokenomics"),
    },
    {
        "id": "workspace",
        "label": "POCKET scratch workspace",
        "path": str(WORK_DIR),
    },
]

# Ensure tokenomics desk exists with a seed README
_tok = WORK_DIR / "tokenomics"
_tok.mkdir(parents=True, exist_ok=True)
_seed = _tok / "README.md"
if not _seed.exists():
    _seed.write_text(
        "# Tokenomics desk\n\nUse POCKET multi-agent sessions to design supply, "
        "vesting, utility sinks, and on-chain token contracts here.\n",
        encoding="utf-8",
    )

_SUBST_CACHE: Dict[str, str] = {}
_SUBST_LETTERS = "PQRSTUVWXYZ"


def which_codex() -> str:
    """Prefer node → codex.js (reliable stdin/argv). Never codex.ps1 (Notepad / broken args)."""
    # Direct node entry — most reliable on Windows for multi-line prompts via stdin
    npm_codex_js = (
        Path(os.environ.get("APPDATA") or "")
        / "npm"
        / "node_modules"
        / "@openai"
        / "codex"
        / "bin"
        / "codex.js"
    )
    if npm_codex_js.is_file():
        node = shutil.which("node") or ""
        if node:
            return f"node+{npm_codex_js}"
    # Explicit Windows cmd shim (stdin works; avoid .ps1)
    for p in (
        Path(os.environ.get("APPDATA") or "") / "npm" / "codex.cmd",
        Path(os.environ.get("ProgramFiles") or "") / "nodejs" / "codex.cmd",
    ):
        if p.is_file():
            return str(p)
    w = shutil.which("codex") or ""
    if w.lower().endswith(".ps1"):
        cmd = w[:-4] + ".cmd"
        if os.path.isfile(cmd):
            return cmd
        # Never return .ps1 — Notepad / broken argv
        return ""
    return w


def which_claude() -> str:
    return shutil.which("claude") or ""


def which_wsl() -> str:
    return shutil.which("wsl") or ""


def which_grok_cli() -> str:
    g = shutil.which("grok") or ""
    if g:
        return g
    cand = Path.home() / ".grok" / "bin" / "grok.exe"
    return str(cand) if cand.exists() else ""


def _needs_onedrive_bridge(path: str) -> bool:
    p = path.replace("/", "\\").lower()
    return "onedrive" in p


def _list_subst() -> Dict[str, str]:
    out: Dict[str, str] = {}
    try:
        p = subprocess.run(["subst"], capture_output=True, text=True, timeout=10, shell=True)
        for line in (p.stdout or "").splitlines():
            m = re.match(r"^([A-Za-z]):\\:\s*=>\s*(.+)\s*$", line.strip())
            if not m:
                continue
            letter, target = m.group(1).upper(), m.group(2).strip()
            key = os.path.normcase(os.path.normpath(target))
            out[key] = f"{letter}:\\"
    except Exception:
        pass
    return out


def _free_drive_letter() -> Optional[str]:
    used = set()
    for d in range(ord("A"), ord("Z") + 1):
        if os.path.exists(f"{chr(d)}:\\"):
            used.add(chr(d))
    for ch in _SUBST_LETTERS:
        if ch not in used:
            return ch
    return None


def bridge_path_for_codex(path: str) -> Tuple[str, str]:
    real = str(Path(path).resolve()) if Path(path).exists() else path
    if not _needs_onedrive_bridge(real):
        return real, ""
    key = os.path.normcase(os.path.normpath(real))
    if key in _SUBST_CACHE and os.path.isdir(_SUBST_CACHE[key]):
        return _SUBST_CACHE[key], f"OneDrive bridge via {_SUBST_CACHE[key]}"
    existing = _list_subst()
    if key in existing:
        _SUBST_CACHE[key] = existing[key]
        return existing[key], f"OneDrive bridge via {existing[key]}"
    letter = _free_drive_letter()
    if not letter:
        return real, "No free drive letter for OneDrive bridge"
    try:
        p = subprocess.run(
            ["subst", f"{letter}:", real],
            capture_output=True,
            text=True,
            timeout=15,
            shell=True,
        )
        if p.returncode != 0:
            return real, f"SUBST failed: {(p.stderr or p.stdout or '')[:200]}"
        mapped = f"{letter}:\\"
        _SUBST_CACHE[key] = mapped
        return mapped, f"OneDrive bridge via {mapped} → {real}"
    except Exception as e:
        return real, f"SUBST error: {e}"


def _is_scratch_workspace(path: str) -> bool:
    n = (path or "").replace("/", "\\").lower()
    return (not n) or n.rstrip("\\").endswith("\\.pocket\\workspace") or n.rstrip("\\").endswith("\\.pocket\\workspace\\")


def prefer_product_cwd(path: str = "") -> str:
    """Prefer real product trees over empty ~/.pocket/workspace scratch."""
    if path and not _is_scratch_workspace(path) and Path(path).is_dir():
        return str(Path(path).resolve())
    for cand in (
        os.environ.get("POCKET_CODEX_CWD") or "",
        PARALLAX_ROOT,
        AURO_ROOT,
        str(Path.home() / "OneDrive" / "pocket-os"),
        path,
    ):
        if cand and Path(cand).is_dir():
            return str(Path(cand).resolve())
    Path(WORK_DIR).mkdir(parents=True, exist_ok=True)
    return str(WORK_DIR)


def resolve_cwd(job: Dict) -> str:
    """Resolve job working directory.

    Founder edition (host_power): full local product trees on THIS machine.
    Market edition: only tenants/<user> (their local sandbox + virtual).
    Never allow market jobs into founder deny paths.
    """
    from pocket.platform_space import (
        is_under_tenant,
        path_is_founder_private,
        tenant_cwd,
    )

    owner = (job.get("owner") or "").strip().lower()
    host_power = bool(job.get("host_power"))
    edition = (job.get("edition") or ("founder" if host_power else "market")).lower()
    ws = (job.get("workspace") or "").strip()
    team_id = (job.get("team_id") or "").strip()
    if team_id and owner:
        try:
            from pocket.team_workspace import get as team_get

            tw = team_get(team_id, principal=owner)
            cwd_t = tw.get("cwd") or ""
            if tw.get("ok") and cwd_t and Path(cwd_t).is_dir():
                return str(Path(cwd_t).resolve())
        except Exception:
            pass

    # Market / non-founder: jail to their space
    if edition == "market" or (owner and not host_power):
        if not owner:
            owner = "anonymous"
            try:
                return tenant_cwd("market", "files")
            except Exception:
                p = Path.home() / ".pocket" / "tenants" / "_anon" / "files"
                p.mkdir(parents=True, exist_ok=True)
                return str(p)
        cwd0 = (job.get("cwd") or "").strip()
        if cwd0 and is_under_tenant(owner, cwd0) and not path_is_founder_private(cwd0):
            return str(Path(cwd0).resolve())
        # local vs virtual surface inside tenant
        surface = "local" if ws in ("local",) else (ws if ws.startswith("tenant") else ws or "files")
        return tenant_cwd(owner, surface)

    # Founder: normal host paths
    cwd = (job.get("cwd") or "").strip()
    if ws and ws not in ("workspace", "default", "scratch") and not ws.startswith("tenant:"):
        for w in KNOWN_WORKSPACES:
            if w["id"] == ws or w["path"] == ws:
                p = Path(w["path"])
                if p.is_dir():
                    return str(p.resolve())
        p = Path(ws)
        if p.is_dir():
            return str(p.resolve())
    if cwd and Path(cwd).is_dir() and not _is_scratch_workspace(cwd):
        return str(Path(cwd).resolve())
    return prefer_product_cwd(cwd)


def available_engines() -> Dict[str, object]:
    codex = which_codex()
    claude = which_claude()
    wsl = which_wsl()
    claude_sdk = False
    try:
        from pocket.claude_agent_bridge import sdk_installed

        claude_sdk = sdk_installed()
    except Exception:
        claude_sdk = False
    return {
        "codex": bool(codex),
        "codex_path": codex or None,
        "claude": bool(claude) or claude_sdk,
        "claude_path": claude or None,
        "claude_agent_sdk": claude_sdk,
        "shell": True,
        "wsl": bool(wsl),
        "wsl_path": wsl or None,
        "grok": bool(which_grok_cli()),
        "grok_path": which_grok_cli() or None,
        "handoff": True,
        "term": True,
        "desktop": True,
        "web": True,
        "nexus": True,
        "agent": True,
        "doer": True,
        "guppy": True,
        "genetic": True,
        "genetic_flow": True,
        "internal_models": True,
        "multi_plan": True,
        "multiplan": True,
        "plan_exec": True,
        "agentic_plan": True,
        "browser": True,
        "capture": True,
        "vision": True,
        "github": True,
        "repos": True,
        "copilot": True,
        "archon": True,
        "alpha": True,
        "autonomy": True,
        "streaming": True,
        "headless_agents": True,
        "ai_api": True,
        "session_resume": True,
        "default": "codex" if codex else ("claude" if (claude or claude_sdk) else "shell"),
        "workspaces": [{**w, "exists": Path(w["path"]).is_dir()} for w in KNOWN_WORKSPACES],
        "note": "AI for the whole computer — desk UI + headless sellable API. One session tab = one Codex thread.",
        "value": [
            "Codex/Grok/Claude (Claude Agent SDK embedded loop + CLI fallback)",
            "Headless doer · multi-step desktop (≤5) without chat",
            "15+ headless agents (researcher, squad, security…)",
            "Desktop 40+ apps (native + third-party + Copilot)",
            "Sellable AI API with sk_pocket_ keys + metering",
            "Phone remote + POCK credits + safety allowlists",
        ],
    }


def run_job(job: Dict) -> Tuple[str, str, str]:
    mode = (job.get("mode") or "codex").lower()
    prompt = (job.get("prompt") or "").strip()
    cwd = resolve_cwd(job)
    Path(cwd).mkdir(parents=True, exist_ok=True)
    jid = job.get("id") or ""
    sid = str(job.get("session_id") or "")

    # --- Auto RAH: agents escalate without the user naming RAH ---
    # Independent large parallel work → full harness fan-out (not bare RLM).
    # Twin wallet pulse — every real job meters the digital twin for this mode
    if mode not in ("shell",) and not job.get("_twin_pulsed"):
        try:
            from pocket.economy import twin_pulse, ensure_twin

            ensure_twin(mode if mode not in ("ask",) else "plan", label=mode)
            twin_pulse(mode if mode not in ("ask",) else "plan", amount=3, reason=f"job:{mode}")
            job = dict(job)
            job["_twin_pulsed"] = True
        except Exception:
            pass

    if (
        prompt
        and not job.get("_rah_done")
        and not job.get("rah_skip")
        and mode not in ("shell", "term", "rah", "recursive_harness", "rah_fanout", "rah_audit")
        and str(os.environ.get("POCKET_RAH_AUTO", "1")).strip().lower()
        not in ("0", "false", "no", "off")
    ):
        try:
            from pocket.rah import maybe_auto_rah, score_rah_fit

            fit = score_rah_fit(prompt, mode=mode)
            if fit.get("use_rah"):
                try:
                    from pocket.stream_util import update_progress

                    update_progress(
                        jid,
                        f"[RAH auto] score={fit.get('score')} ≥ {fit.get('threshold')} — "
                        f"spawning recursive harnesses (user need not ask)\n",
                        engine="rah",
                    )
                except Exception:
                    pass
                auto = maybe_auto_rah(prompt, mode=mode, job=job, cwd=cwd, execute=True)
                if auto and auto.get("execute") and auto.get("markdown") is not None:
                    err = "" if auto.get("ok") else "rah auto completed with failures"
                    head = (
                        f"[engine=rah auto=true score={fit.get('score')} "
                        f"run={((auto.get('run') or {}).get('run_id') or '—')}]\n"
                        f"[POCKET selected Recursive Agent Harnesses — independent parallel work]\n\n"
                    )
                    return head + str(auto.get("markdown") or ""), err, "rah"
        except Exception as e:
            try:
                from pocket.stream_util import update_progress

                update_progress(jid, f"[RAH auto skipped] {e}\n", engine=mode)
            except Exception:
                pass

    # Host tools loop — run matching platform skills BEFORE the LLM so agents
    # actually use screenshot / screen_sense / platform_map / etc.
    # Always inject POCKET identity so every model knows it is in POCKET.
    tool_meta: Dict = {}
    if (
        prompt
        and not job.get("_tools_done")
        and str(os.environ.get("POCKET_AGENT_TOOLS", "1")).strip().lower()
        not in ("0", "false", "no")
        and mode not in ("shell",)  # ask/plan/voice get identity+tools too
    ):
        try:
            from pocket.agent_tools_loop import enrich_prompt

            prompt, tool_meta = enrich_prompt(prompt, mode=mode)
            job = dict(job)
            job["prompt"] = prompt
            job["_tools_done"] = True
            # If tools already executed a full RAH run, short-circuit to that result
            if tool_meta.get("rah_auto_result"):
                rr = tool_meta["rah_auto_result"]
                return (
                    f"[engine=rah auto=true via tools]\n\n{rr.get('markdown') or ''}",
                    "" if rr.get("ok") else "rah tool path failures",
                    "rah",
                )
            # Assist/Power: host already ran GO/Power — return that, don't overwrite with a generic plan
            if mode in ("assist", "assistant", "digital", "life", "plan", "power") and tool_meta.get("command_md"):
                skills = [str(r.get("skill") or "") for r in (tool_meta.get("results") or [])]
                if any(s in ("go", "go_state", "power_do", "power_vs", "multi_workflows") for s in skills):
                    return (
                        "[engine=power via host tools]\n\n" + str(tool_meta.get("command_md") or ""),
                        "",
                        "power",
                    )
            if jid and tool_meta.get("ran"):
                try:
                    from pocket.stream_util import update_progress

                    skills = ", ".join(
                        str(r.get("skill")) for r in (tool_meta.get("results") or []) if r.get("skill")
                    )
                    update_progress(
                        jid,
                        f"[tools] ran host skills: {skills}\n",
                        engine=mode,
                    )
                except Exception:
                    pass
        except Exception:
            tool_meta = {}
    elif prompt and not job.get("_identity_done") and mode not in ("shell",):
        # Tools disabled — still stamp POCKET identity + protocols
        try:
            from pocket.pocket_identity import wrap_user_prompt

            prompt = wrap_user_prompt(prompt, mode=mode)
            job = dict(job)
            job["prompt"] = prompt
            job["_identity_done"] = True
        except Exception:
            pass

    # Universal agentic harness: Codex/Grok/Claude/plan/build get real subagents
    # (animated on desk). Skip nested systems that already multi-agent.
    _harness_parents = {
        "codex",
        "grok",
        "claude",
        "plan",
        "build",
        "ship",
        "wiki",
        "infinite_wiki",
        "codebase",
        "agent",
        "doer",
        "custom_agent",
        "use_case",
        "emergent",
        "loop",
        "work",
        "working",
        "live_work",
        "muse_spark",
        "muse",
        "spark",
        "assist",
        "assistant",
        "digital",
    }
    use_harness = (
        mode in _harness_parents
        and job.get("harness") is not False
        and str(os.environ.get("POCKET_HARNESS", "1")).strip().lower() not in ("0", "false", "no")
    )
    if use_harness and not job.get("_harness_inner"):
        from pocket.agentic_harness import run_with_harness

        inner = dict(job)
        inner["_harness_inner"] = True  # prevent re-entry
        return run_with_harness(
            mode,
            prompt,
            job_id=jid,
            session_id=sid,
            cwd=cwd,
            main=lambda: run_job(inner),
            sub_agents=job.get("sub_agents") or job.get("subagents"),
            parallel_subs=True,
        )

    if mode == "shell":
        return _run_shell(prompt, cwd, job_id=jid)
    if mode in ("wsl", "wsl_native", "wsl-native", "linux"):
        from pocket.wsl_agent import run_wsl_job

        return run_wsl_job(prompt, cwd=cwd, job=job)
    if mode == "claude":
        return _run_claude(prompt, cwd, job_id=jid)
    if mode in ("voice", "v2v", "voice_agent", "voice2voice"):
        return _run_voice_agent(prompt, cwd, job_id=jid)
    if mode == "ask":
        return _run_ask(prompt, cwd)
    if mode == "plan":
        return _run_planning_ai(prompt, cwd, job_id=jid)
    if mode == "handoff":
        return _run_plan_handoff(prompt, cwd)
    if mode == "grok":
        return _run_grok_agent(prompt, cwd, job_id=jid)
    if mode in ("novae_grok", "novae-grok", "novae"):
        from pocket.novae import run_novae_job

        return run_novae_job(prompt, cwd=cwd, job=job, kind="grok")
    if mode in ("novae_codex", "novae-codex"):
        from pocket.novae import run_novae_job

        return run_novae_job(prompt, cwd=cwd, job=job, kind="codex")
    if mode in ("wiki", "infinite_wiki", "codebase"):
        from pocket.infinite_wiki import run_wiki_job

        return run_wiki_job(prompt, cwd=cwd, job=job)
    if mode in ("dream",):
        from pocket.dream_mode import dream_once, list_dreams, status as dream_status

        low = (prompt or "").strip().lower()
        if low in ("status", "list", ""):
            return json.dumps({"status": dream_status(), "recent": list_dreams(8)}, indent=2), "", "dream"
        return json.dumps(dream_once(force=True), indent=2, default=str), "", "dream"
    if mode in ("duel",):
        from pocket.agent_duels import duel

        r = duel((prompt or "").strip() or "How should we ship the next slice?")
        return (r.get("verdict") or {}).get("winning_plan") or json.dumps(r, indent=2), "", "duel"
    if mode in ("capsule",):
        from pocket.time_capsules import create_capsule, status as cap_status

        low = (prompt or "").strip()
        if low.lower() in ("list", "status", ""):
            return json.dumps(cap_status(), indent=2, default=str), "", "capsule"
        # "in 120s: message" or "capsule message"
        m = re.match(r"(?:in\s+)?(\d+)\s*(?:s|sec|seconds)?\s*[:\-]?\s*(.+)$", low, re.I)
        if m:
            return json.dumps(create_capsule(m.group(2), after_sec=int(m.group(1))), indent=2), "", "capsule"
        return json.dumps(create_capsule(low, after_sec=300), indent=2), "", "capsule"
    if mode in ("serendipity",):
        from pocket.serendipity import find_links

        return json.dumps(find_links(limit=10), indent=2), "", "serendipity"
    if mode in ("proof",):
        from pocket.proof_chain import list_receipts, mint_receipt, status as proof_status, verify_chain

        low = (prompt or "").strip().lower()
        if low in ("verify", "check"):
            return json.dumps(verify_chain(), indent=2), "", "proof"
        if low in ("list", "status", ""):
            return json.dumps({"status": proof_status(), "recent": list_receipts(10)}, indent=2), "", "proof"
        return json.dumps(mint_receipt("manual", prompt or "manual"), indent=2), "", "proof"
    if mode in ("dual", "cortex", "subcortex"):
        from pocket.cortex_subcortex import run_dual_job

        return run_dual_job(prompt, cwd=cwd, job=job)
    if mode in ("swarm",):
        from pocket.always_on_swarm import pulse_now, start as swarm_start, status as swarm_status

        low = (prompt or "").strip().lower()
        if low in ("start", "on", "enable"):
            return json.dumps(swarm_start(), indent=2), "", "swarm"
        if low in ("status", "help", "always-on", "daemon"):
            return json.dumps(swarm_status(), indent=2), "", "swarm"
        if low in ("pulse", "tick"):
            return json.dumps(pulse_now(), indent=2), "", "swarm"
        # Coding tasks → multi-agent harness (Sophia / Solver / Twin) + pixel artifacts
        from pocket.coding_swarm import run_coding_swarm

        return run_coding_swarm(prompt, cwd, job_id=jid)
    if mode in ("coding_swarm", "pixel_swarm", "harness", "swarm_code", "code_swarm"):
        from pocket.coding_swarm import run_coding_swarm

        return run_coding_swarm(prompt, cwd, job_id=jid)
    # Recursive Agent Harnesses — full harness recursion (not bare model RLM)
    if mode in ("rah", "recursive_harness", "rah_fanout", "rah_audit"):
        from pocket.rah import run_rah_job

        return run_rah_job(prompt, cwd=cwd, job=job)
    if mode in ("build", "ship", "use_case", "emergent", "loop"):
        from pocket.build_loop import manage_until_done, run_use_case, start_loop
        from pocket.use_cases import get_use_case, list_use_cases

        text = (prompt or "").strip()
        low = text.lower()
        # list use cases
        if low in ("help", "list", "use cases", "usecases", "parity"):
            from pocket.use_cases import parity_report

            if "parity" in low:
                return json.dumps(parity_report(), indent=2), "", "build"
            lines = ["# POCKET real use cases (Emergent+)\n"]
            for u in list_use_cases():
                lines.append(f"- **{u['id']}**: {u['title']}")
            lines.append("\nStart: `use_case:fullstack_web_app` or describe the app to ship.")
            return "\n".join(lines), "", "build"
        # explicit use case
        uc_id = ""
        m = re.match(r"(?:use[_-]?case|uc|run)[:\s]+([a-z0-9_]+)", low)
        if m:
            uc_id = m.group(1)
        elif get_use_case(text.split()[0] if text else ""):
            uc_id = text.split()[0].lower()
        owner = (job.get("owner") or "pocket") if job else "pocket"
        if uc_id:
            started = run_use_case(uc_id, goal=text, owner=owner)
        else:
            started = start_loop(text, owner=owner, template="web_static", loop_kind="ship")
        if not started.get("ok"):
            return "", started.get("error") or "loop failed to start", "build"
        lid = started.get("id") or ""
        final = manage_until_done(lid, timeout_sec=120.0)
        loop = final.get("loop") or started
        summary = (
            f"# Build loop {'DONE' if final.get('ok') else loop.get('status','').upper()}\n\n"
            f"**id:** `{lid}`\n"
            f"**goal:** {loop.get('goal')}\n"
            f"**phase:** {loop.get('phase')} · **status:** {loop.get('status')}\n"
            f"**project:** `{loop.get('project')}`\n"
            f"**progress:** {loop.get('progress')}\n\n"
            f"Poll: `/v1/build-loops/{lid}`\n"
            f"History phases: {len(loop.get('history') or [])}\n"
        )
        return summary, "" if final.get("ok") or loop.get("status") == "done" else (loop.get("error") or "incomplete"), "build"
    if mode == "custom_agent":
        from pocket.custom_agents import create_agent, list_agents, run_custom_agent

        text = (prompt or "").strip()
        low = text.lower()
        if low.startswith("create ") or low.startswith("new "):
            # create name: Role — personality
            body = text.split(" ", 1)[-1]
            name = body.split(":")[0].strip() or "CustomAgent"
            rest = body.split(":", 1)[-1].strip() if ":" in body else "specialist"
            rec = create_agent(name=name, role=rest, owner=(job or {}).get("owner") or "pocket")
            return json.dumps(rec, indent=2), "", "custom_agent"
        if low in ("list", "help"):
            return json.dumps({"agents": list_agents()}, indent=2), "", "custom_agent"
        # run: AgentId task...
        parts = text.split(None, 1)
        aid = parts[0] if parts else "AGENT"
        task = parts[1] if len(parts) > 1 else text
        r = run_custom_agent(aid, task, cwd=cwd, job=job)
        return r.get("summary") or json.dumps(r, indent=2), "" if r.get("ok") else r.get("error", ""), "custom_agent"
    if mode == "desktop":
        from pocket.desktop import run_desktop_job

        return run_desktop_job(prompt)
    if mode == "web":
        from pocket.web_research import run_web_job

        return run_web_job(prompt)
    if mode == "nexus":
        from pocket.nexus_bridge import run_nexus_job

        return run_nexus_job(prompt)
    if mode == "mesie":
        from pocket.mesie_bridge import run_mesie_job

        return run_mesie_job(prompt)
    if mode in ("auro", "auro14b", "ro14b", "him"):
        from pocket.auro14b_bridge import run_auro_job

        return run_auro_job(prompt, job=job)
    if mode in ("assist", "assistant", "digital", "life", "day", "personal"):
        from pocket.digital_assistant import run_assistant_turn

        r = run_assistant_turn(
            prompt,
            engine="auto",
            session_id=sid,
            job_id=jid,
            voice=bool(job.get("voice_engine") or job.get("voice")),
        )
        return r.get("reply") or "", "" if r.get("ok") else str(r.get("error") or ""), r.get("engine") or "assist"
    if mode in ("agent", "doer"):
        from pocket.step_agent import run_step_agent

        return run_step_agent(prompt, cwd=cwd, job=job, max_steps=10)
    if mode == "guppy":
        from pocket.guppy import run_guppy

        return run_guppy(prompt, cwd=cwd, job=job)
    if mode == "browser":
        from pocket.browser_mode import run_browser_job

        return run_browser_job(prompt, cwd=cwd, job=job)
    if mode == "capture":
        from pocket.capture import run_capture_job

        return run_capture_job(prompt)
    if mode in ("studio", "product_studio", "video_studio", "viral"):
        return _run_studio_agent(prompt, cwd, job_id=jid)
    if mode in ("vision", "oculus", "see", "pixel_see"):
        return _run_vision_agent(prompt, cwd, job_id=jid)
    if mode in ("work", "working", "live_work", "work_mode", "persistent"):
        return _run_work_mode(prompt, cwd, job_id=jid, session_id=sid)
    if mode in ("muse_spark", "muse", "spark", "muse-spark", "musespark"):
        from pocket.muse_spark import run_muse_spark_job

        return run_muse_spark_job(prompt, cwd=cwd, job=job)
    if mode in ("screen", "screen_share", "share"):
        return _run_screen_agent(prompt, cwd, job_id=jid)
    if mode in ("vcomp", "vcomputer", "virtual_computer", "computer"):
        return _run_vcomp_agent(prompt, cwd, job_id=jid)
    if mode in ("mcp", "tools"):
        return _run_mcp_agent(prompt, cwd, job_id=jid)
    if mode in ("github", "gh"):
        from pocket.github_hub import run_github_job

        return run_github_job(prompt, cwd=cwd)
    if mode == "repos":
        from pocket.repos import run_repos_job

        return run_repos_job(prompt)
    if mode in ("team", "team-workspace"):
        from pocket.team_workspace import snapshot as team_snap

        owner = str(job.get("owner") or job.get("team_owner") or "pocket")
        r = team_snap(principal=owner)
        return (
            str(r.get("note") or json.dumps({k: r.get(k) for k in ("ok", "count", "owner", "root")}, default=str)),
            "" if r.get("ok") else str(r.get("error") or "team"),
            "team",
        )
    if mode in ("auro-endure", "endure", "auro_endure"):
        from pocket.endure_worker import run as endure_run

        r = endure_run(prompt)
        return str(r.get("summary") or r.get("error") or ""), "" if r.get("ok") else str(r.get("error") or "endure"), "auro-endure"
    if mode == "copilot":
        from pocket.copilot_agent import run_copilot_job

        return run_copilot_job(prompt, cwd=cwd, job=job)
    if mode in ("archon", "alpha", "workers"):
        from pocket.alpha_workers import run_alpha_job

        return run_alpha_job(prompt, cwd=cwd, job=job)
    if mode in ("woa", "wrapped-orch", "wrapped_orch", "orchestrator-llm"):
        from pocket.wrapped_orchestrator import run_woa_job

        return run_woa_job(prompt, cwd=cwd, job=job)
    if mode in ("offload", "embody", "embodiment", "realworld"):
        from pocket.offload_queue import enqueue, ensure_worker

        ensure_worker()
        # "offload: ..." or free text → queue and return ticket
        goal = prompt
        if goal.lower().startswith("offload:"):
            goal = goal.split(":", 1)[1].strip()
        r = enqueue(
            goal,
            agent=(job.get("mode") or "AI").upper(),
            session_id=job.get("session_id") or "",
            workspace=job.get("workspace") or "parallax",
        )
        body = (
            f"## Offload accepted\n\n"
            f"**Ticket:** `{r.get('ticket')}`\n"
            f"**Goal:** {goal[:500]}\n\n"
            f"Chat turn is free. Poll `GET /v1/offload/{r.get('ticket')}` or right-rail previews.\n"
            f"Worker runs embodiment steps + proof pack in background.\n"
        )
        return body, ("" if r.get("ok") else r.get("error") or "offload failed"), "offload"
    # "work" is Working mode (earlier) — cowork uses cowork/demo only
    if mode in ("cowork", "demo", "embody-desk"):
        from pocket.cowork import run_cowork_job

        return run_cowork_job(prompt, cwd=cwd, job=job)
    if mode in ("git", "forge", "sovereign-git", "sovereign_git"):
        from pocket.sovereign_git import run_git_job

        return run_git_job(prompt)
    if mode in ("bot", "bots", "teammate"):
        from pocket.bots import create_from_prompt, list_bots, message as bot_message

        low = (prompt or "").lower()
        if low.startswith("hire ") or low.startswith("create bot"):
            return str(create_from_prompt(prompt)), "", "bots"
        bots = list_bots()
        if bots:
            r = bot_message(bots[0]["id"], prompt or "")
            return r.get("reply") or "", "", "bots"
        r = create_from_prompt(prompt or "general teammate")
        if r.get("id"):
            m = bot_message(r["id"], prompt or "hello")
            return m.get("reply") or r.get("job") or "", "", "bots"
        return "No bots yet — open /bots to hire a teammate.", "", "bots"
    if mode in ("ghost", "ghost-math", "math"):
        from pocket.ghost_math import run_ghost

        return run_ghost(prompt)
    if mode in ("logic", "logic_prover", "prove"):
        from pocket.internal_models import express_one

        r = express_one("logic", prompt or "")
        return (r.text or r.error or ""), "", "logic-internal"
    if mode in ("pattern", "pattern_forge", "xray"):
        from pocket.internal_models import express_one

        r = express_one("pattern", prompt or "")
        return (r.text or r.error or ""), "", "pattern-internal"
    if mode in ("world", "world_model", "intelligence_world"):
        from pocket.internal_models import express_one

        r = express_one("world", prompt or "")
        return (r.text or r.error or ""), "", "world-model"
    if mode in ("imagine", "imagine_studio", "visua"):
        from pocket.imagine_studio import compose as imagine_compose

        out = imagine_compose(mode="rotato_phone", source="live", subtitle=prompt or "Host co-pilot")
        if not out.get("ok"):
            return out.get("error") or "imagine failed", "", "imagine"
        return (
            f"Imagine still `{out.get('name')}` → {out.get('file_url')} (source={out.get('source_kind')})",
            "",
            "imagine",
        )
    if mode in (
        "genetic",
        "genetic_flow",
        "gene",
        "internal",
        "internal_models",
        "internal-models",
        "eugenetic",
        "foundations",
    ):
        from pocket.internal_models import run_job as run_genetic_job

        return run_genetic_job(prompt, cwd=cwd, job=job)
    if mode in (
        "multi_plan",
        "multiplan",
        "multi-plan",
        "plan_exec",
        "plan_execute",
        "agentic_plan",
        "task_plan",
    ):
        from pocket.multi_plan import run_job as run_multi_plan_job

        return run_multi_plan_job(prompt, cwd=cwd, job=job)
    if mode in ("term", "python", "python_wsl", "py"):
        return _run_agent_console(prompt, mode=mode, session_id=sid, job_id=jid, cwd=cwd)
    return _run_codex(prompt, cwd, job_id=jid, job=job)


def _run_agent_console(
    prompt: str,
    *,
    mode: str = "term",
    session_id: str = "",
    job_id: str = "",
    cwd: str = "",
) -> Tuple[str, str, str]:
    """Send user text to the integrated console bound to this session (WSL / Python / PS)."""
    from pocket.stream_util import update_progress
    from pocket.terminals import agent_run, ensure_agent_console, catalog

    text = (prompt or "").strip()
    kind_map = {
        "term": "powershell",
        "shell": "powershell",
        "python": "python",
        "py": "python",
        "python_wsl": "python_wsl",
        "wsl": "wsl",
        "wsl_native": "wsl",
        "linux": "wsl",
    }
    kind = kind_map.get((mode or "term").lower(), "powershell")

    # Meta commands
    low = text.lower()
    if not text or low in ("help", "?", "status", "console"):
        cat = catalog()
        lines = [
            f"# Integrated agent console · `{kind}`",
            "",
            cat.get("doctrine") or "",
            "",
            "## Available kinds",
        ]
        for k in cat.get("kinds") or []:
            mark = "✓" if k.get("available") else "✗"
            lines.append(f"- {mark} **{k.get('id')}** — {k.get('label')}")
        lines.append("")
        lines.append("Type shell/Python lines here — they run in the **hidden integrated console**.")
        lines.append("Switch: `use wsl` · `use python` · `use python_wsl` · `use powershell`")
        return "\n".join(lines), "", kind

    if low.startswith("use "):
        want = low.split(None, 1)[1].strip().replace("-", "_")
        kind = kind_map.get(want, want if want in ("powershell", "cmd", "wsl", "python", "python_wsl") else kind)
        ens = ensure_agent_console(session_id, kind=kind)
        return (
            f"Console ready · **{ens.get('kind')}** · alive={ens.get('alive')} · pid={ens.get('pid')}\n\n"
            f"```\n{(ens.get('log_tail') or '')[-2500:]}\n```",
            "" if ens.get("ok") or ens.get("alive") else str(ens.get("error") or "start failed"),
            ens.get("kind") or kind,
        )

    if job_id:
        update_progress(job_id, f"console [{kind}] «{text[:80]}»…", engine=kind)

    # Strip accidental code fences for paste
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    r = agent_run(text, session_id=session_id, kind=kind, wait_ms=800)
    tail = (r.get("log_tail") or "")[-6000:]
    out = (
        f"[console={r.get('kind') or kind} · integrated · pid={r.get('pid') or '—'} · "
        f"alive={r.get('alive')}]\n\n```text\n{tail}\n```\n"
    )
    if job_id:
        update_progress(job_id, out[-2000:], engine=kind)
    err = "" if r.get("ok") else str(r.get("error") or "console error")
    return out, err, r.get("kind") or kind


def _run_shell(cmd: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    try:
        from pocket.safety import allow_shell

        ok, msg = allow_shell(cmd)
        if not ok:
            return "", msg, "shell"
    except Exception:
        pass
    blocked = (
        "rm -rf /",
        "format c:",
        "format c ",
        "del /s /q c:\\",
        "shutdown",
        "mkfs",
        "rd /s /q c:\\",
        "reg delete",
        "net user",
    )
    low = cmd.lower()
    if any(b in low for b in blocked):
        return "", "Blocked dangerous shell command", "shell"
    from pocket.stream_util import run_streaming

    out, rc, err = run_streaming(
        cmd,
        job_id=job_id,
        cwd=cwd,
        timeout=300,
        engine="shell",
        shell=True,
    )
    out = (out or "").strip()[-50000:]
    if err:
        return out, err, "shell"
    if rc != 0:
        return out or f"(exit {rc})", f"exit {rc}", "shell"
    return out or "(no output)", "", "shell"


def _run_wsl(cmd: str, job_id: str = "") -> Tuple[str, str, str]:
    if not which_wsl():
        return "", "WSL not installed", "wsl"
    distro_args: List[str] = ["wsl"]
    try:
        p = subprocess.run(
            ["wsl", "-l", "-q"],
            capture_output=True,
            timeout=8,
            text=True,
            encoding="utf-16-le",
            errors="replace",
        )
        names = [n.strip() for n in (p.stdout or "").splitlines() if n.strip()]
        if any(n.lower() == "debian" for n in names):
            distro_args = ["wsl", "-d", "Debian"]
    except Exception:
        pass
    full = distro_args + ["--", "bash", "-lc", cmd]
    from pocket.stream_util import run_streaming

    out, rc, err = run_streaming(full, job_id=job_id, timeout=300, engine="wsl")
    out = (out or "").strip()[-50000:]
    if err:
        return out, err, "wsl"
    if rc != 0:
        return out or f"(exit {rc})", f"wsl exit {rc}", "wsl"
    return out or "(no output)", "", "wsl"


def _run_ask(prompt: str, cwd: str) -> Tuple[str, str, str]:
    """Lightweight POCKET-aware reply (no shell). Prefer plan/codex for real models."""
    engines = available_engines()
    # Strip identity blocks for display of user request head
    user_head = prompt or ""
    for marker in ("[POCKET IDENTITY]", "# You are in POCKET", "[POCKET PLATFORM]", "[POCKET PROTOCOLS]"):
        if marker in user_head:
            user_head = user_head.split(marker)[0].strip()
    user_head = (user_head or prompt or "")[:1200]
    try:
        from pocket.pocket_identity import IDENTITY_ONE_LINER
        from pocket.protocols.platform_protocols import list_protocols

        protos = ", ".join(p["slug"] for p in list_protocols())
        who = IDENTITY_ONE_LINER
    except Exception:
        protos = "mesh, mcp-colony, bearer-session, job-session, phone-pair, …"
        who = "You are a POCKET host agent."
    return (
        f"## POCKET · Ask\n\n"
        f"{who}\n\n"
        f"**You asked:** {user_head}\n\n"
        f"**Host:** engines Codex={engines.get('codex')} · Claude={engines.get('claude')} · "
        f"Grok={engines.get('grok', engines.get('wsl'))} · workspace `{cwd}`\n\n"
        f"**Protocols wired:** {protos}\n\n"
        "### How I can help in POCKET\n"
        "1. **Desk** `/desk` — Codex / Claude / Grok / Plan sessions\n"
        "2. **Phone** `/phone` — pair code + same seat agents\n"
        "3. **Skills** — POST `/v1/skills/run` or say “platform map” / “protocols”\n"
        "4. **Protocols** — GET `/v1/protocols` · skill `protocols_map`\n"
        "5. **Identity** — GET `/v1/identity` (every agent knows it is POCKET)\n\n"
        "Open a **Codex**, **Claude**, **Grok**, or **Plan** session for deep work. "
        "Ask mode stays read-only guidance on this host.\n",
        "",
        "ask",
    )


def _run_planning_ai(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Planning AI chat — real model, no code edits."""
    from pocket.stream_util import run_streaming
    from pocket.grok_bridge import which_grok

    grok = which_grok()
    plan_prompt = (
        "You are a POCKET host planning agent (not a generic chatbot). PLAN ONLY.\n"
        "Help the user plan work *inside POCKET* (desk sessions, agents, skills, protocols).\n"
        "Do not write full production code or edit files. Do not run shell.\n"
        "Format like a clear chat reply (iMessage-style scannable):\n"
        "- Short paragraphs and numbered steps\n"
        "- Use **bold** for section labels\n"
        "- When you show example APIs, schemas, or pseudo-code, put them in fenced "
        "markdown code blocks with a language tag (```python, ```ts, ```json, ```bash)\n"
        "- Prefer small snippets over walls of text\n"
        "Cover: goals, constraints, ordered steps, risks, open questions, success metrics.\n"
        "If useful, mention POCKET surfaces (desk, phone, loomgraph, mesh, skills).\n"
        f"Workspace context: {cwd}\n\n"
        f"User:\n{prompt}"
    )
    if grok:
        cmd = [
            grok,
            "--single",
            plan_prompt[:12000],
            "--cwd",
            cwd,
            "--max-turns",
            "6",
            "--permission-mode",
            "plan",
            "--output-format",
            "plain",
        ]
        env = {**os.environ}
        env["PATH"] = str(Path(grok).parent) + os.pathsep + env.get("PATH", "")
        out, rc, err = run_streaming(
            cmd, job_id=job_id, cwd=cwd, env=env, timeout=300, engine="plan"
        )
        text = (out or "").strip()
        header = f"[engine=planning-ai · no code · cwd={cwd}]\n\n"
        if text:
            return header + text[-50000:], ("" if rc == 0 else (err or f"exit {rc}")), "plan"
        # fall through to template if empty
    plan, _, _ = _run_ask(prompt, cwd)
    return (
        "[engine=planning-ai-template]\n\n"
        + plan
        + "\n\n_(Install/use Grok CLI for live Planning AI chat.)_",
        "",
        "plan",
    )


def _run_plan_handoff(prompt: str, cwd: str) -> Tuple[str, str, str]:
    """Deferred planning package only — no coding agent."""
    from pocket.grok_bridge import run_plan_handoff

    return run_plan_handoff(prompt, cwd)


def _run_grok_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Real Grok coding agent via grok --single (streamed)."""
    from pocket.grok_bridge import run_grok_exec

    return run_grok_exec(prompt, cwd, job_id=job_id)


def _codex_argv(codex: str) -> List[str]:
    """Build argv prefix for codex binary (handles node+path form)."""
    if codex.startswith("node+"):
        js = codex[5:]
        node = shutil.which("node") or "node"
        return [node, js]
    return [codex]


def _codex_cmd_base(codex: str, agent_cwd: str) -> List[str]:
    return _codex_argv(codex) + [
        "exec",
        "--skip-git-repo-check",
        "-C",
        agent_cwd,
        "-s",
        "workspace-write",
    ]


def _parse_codex_thread_id(text: str) -> str:
    """Extract Codex conversation/session UUID from CLI output."""
    if not text:
        return ""
    # Common lines: "session id: 019f…" or "thread id: …" or UUID alone near session
    patterns = (
        r"(?:session|thread|conversation)\s*id[:\s]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b",
    )
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1)
    return ""


def _bind_codex_thread(session_id: str, thread_id: str, *, resumed: bool = False) -> None:
    if not session_id or not thread_id:
        return
    try:
        from pocket.sessions import bind_engine_thread

        bind_engine_thread(session_id, thread_id, engine="codex", resumed=resumed)
    except Exception:
        pass


_IDLE_ASK_RE = re.compile(
    r"what (?:do you want me to|would you like me to) work on"
    r"|what (?:do you want|would you like) me to (?:work on|do)"
    r"|what should i (?:work on|do)(?:\s+next)?"
    r"|how can i help you today"
    r"|ready for (?:your |a )?task"
    r"|awaiting (?:your )?(?:task|instructions?)",
    re.I,
)


def _strip_device_prefix(text: str) -> str:
    """Pull the real user task out from [Client device: …] wrappers."""
    t = (text or "").strip()
    t = re.sub(
        r"^\[Client device:[^\]]*\]\s*",
        "",
        t,
        count=1,
        flags=re.I | re.S,
    ).strip()
    return t or (text or "").strip()


def _wants_research_only(task: str) -> bool:
    """True only when the user explicitly asked for a paper / research writeup."""
    low = (task or "").lower()
    explicit = (
        "research paper",
        "write a paper",
        "write the paper",
        "draft a paper",
        "literature review",
        "write docs only",
        "documentation only",
        "markdown paper",
        "zenodo",
        "latex manuscript",
    )
    if any(p in low for p in explicit):
        return True
    # "research X" alone is often product research — still prefer code when ship words present
    ship = ("ship", "production", "implement", "fix", "code", "test", "alpha", "paradise", "overnight")
    if any(w in low for w in ship):
        return False
    return False


def _build_codex_prompt(
    prompt: str,
    agent_cwd: str,
    cwd: str,
    bridge_note: str = "",
    *,
    resumed: bool = False,
) -> str:
    """Lean Codex prompt — TASK-first, minimal policy, max signal per token.

    Design (deep-tech token economics):
      1. TASK on line 1 (survives Windows argv truncation)
      2. Micro-policy ≤4 short lines (not a system essay)
      3. Resume threads: TASK only — thread memory already holds prior turns
      4. Full user message only when multi-line / device-wrapped
    """
    raw = (prompt or "").strip()
    task = _strip_device_prefix(raw)
    if not task:
        task = "Continue current task; if idle, ship one concrete verified fix."
    task_one_line = " ".join(task.split())
    # Resume = zero policy re-tax (thread already conditioned)
    if resumed:
        return f"TASK: {task_one_line}\n"

    research_only = _wants_research_only(task_one_line)
    if research_only:
        policy = "Research mode: tight docs + one verify/next-code note. No repo-wide scans."
    else:
        policy = (
            "Code-first host agent. Edit+verify in cwd. "
            "No essays; no full-tree walks when PATHS given. "
            "Reply: changed · verify · next. "
            "GitHub via `gh` on host. Hierarchy: preview/draft → local or browser → "
            "promote to folder or GitHub (never jump straight to remote). "
            "Web UIs & simulations: end with ```preview (title+url), ```html-preview, "
            "or ```simulation so the desk shows an in-chat bubble before commit."
        )
    parts = [
        f"TASK: {task_one_line}",
        policy,
        f"cwd={agent_cwd}",
    ]
    if bridge_note:
        parts.append(f"bridge={bridge_note}; real={cwd}")
    # Only re-attach multi-line body when it carries structure beyond the one-liner
    if raw and raw != task and ("\n" in raw or len(raw) > len(task_one_line) + 40):
        # Cap long pastes — operator can attach files; don't blow the context window
        body = raw if len(raw) <= 2400 else (raw[:1200] + "\n…\n" + raw[-800:])
        parts.extend(["---", body])
    return "\n".join(parts) + "\n"


def _codex_looks_idle(text: str) -> bool:
    """True when Codex ignored the task and only asked what to work on."""
    if not text:
        return False
    low = text.lower()
    if _IDLE_ASK_RE.search(low):
        # If it also did real work (exec/edit), not idle
        if "```" in text or "\nexec\n" in low or "succeeded in" in low:
            return False
        return True
    return False


def _run_codex(prompt: str, cwd: str, job_id: str = "", job: Optional[Dict] = None) -> Tuple[str, str, str]:
    codex = which_codex()
    if not codex:
        if which_claude():
            result, err, _ = _run_claude(prompt, cwd, job_id=job_id)
            return result + "\n\n_(Codex missing — Claude.)_", err, "claude-fallback"
        plan, _, _ = _run_ask(prompt, cwd)
        return plan + "\n\nInstall Codex CLI.", "codex not installed", "ask-fallback"

    job = job or {}
    pocket_sid = (job.get("session_id") or "").strip()
    # Prefer explicit job field, else load from POCKET session (one button = one Codex thread)
    engine_thread = ""
    if not job.get("_no_resume"):
        engine_thread = (job.get("engine_thread_id") or job.get("codex_session_id") or "").strip()
        if not engine_thread and pocket_sid:
            try:
                from pocket.sessions import get as get_sess

                s = get_sess(pocket_sid) or {}
                engine_thread = (s.get("engine_thread_id") or s.get("codex_session_id") or "").strip()
            except Exception:
                engine_thread = ""

    product_cwd = prefer_product_cwd(cwd)
    agent_cwd, bridge_note = bridge_path_for_codex(product_cwd)
    if _is_scratch_workspace(agent_cwd):
        agent_cwd = prefer_product_cwd("")
        bridge_note = bridge_note or "product cwd remap"

    resumed = bool(engine_thread)
    full_prompt = _build_codex_prompt(
        prompt, agent_cwd, product_cwd, bridge_note, resumed=resumed
    )
    # Token gate: on resume, thread already has history — skip workspace reinject.
    # Fresh threads get a locus digest (~900 chars), not the full AI_WORKSPACE essay.
    if not resumed:
        try:
            from pocket.ai_workspace import inject_for_prompt

            full_prompt = inject_for_prompt(
                full_prompt,
                workspace=(job.get("workspace") or "parallax"),
                session_id=(job.get("session_id") or ""),
                cwd=product_cwd,
                lean=True,
                engine="codex",
            )
        except Exception:
            pass

    # Always pass prompt via stdin ("-") — multi-line argv is unreliable on Windows cmd shims
    if resumed:
        # codex exec resume [OPTIONS] SESSION_ID [PROMPT]
        # OPTIONS before SESSION_ID; prompt last as "-"
        cmd = _codex_argv(codex) + [
            "exec",
            "resume",
            "--skip-git-repo-check",
            engine_thread,
            "-",
        ]
    else:
        cmd = _codex_cmd_base(codex, agent_cwd) + ["-"]

    from pocket.stream_util import estimate_tokens, run_streaming

    out, rc, err = run_streaming(
        cmd,
        job_id=job_id,
        cwd=agent_cwd if os.path.isdir(agent_cwd) else product_cwd,
        env={**os.environ, "CI": "1"},
        timeout=900,
        engine="codex",
        stdin_text=full_prompt,
    )
    combined = (out or "").strip()
    thread_id = _parse_codex_thread_id(combined) or engine_thread
    if thread_id and pocket_sid and not _codex_looks_idle(combined):
        _bind_codex_thread(pocket_sid, thread_id, resumed=resumed)

    header = f"[engine=codex cwd={agent_cwd}"
    if bridge_note:
        header += f" · {bridge_note}"
    if resumed and engine_thread:
        header += f" · resume={engine_thread[:13]}…"
    elif thread_id:
        header += f" · new_thread={thread_id[:13]}…"
    header += f"]\n[pocket_session={pocket_sid or '—'} · one POCKET tab = one Codex thread]\n"
    header += f"[stream_tokens≈{estimate_tokens(combined)}]\n\n"

    def _fallback_fresh(reason: str) -> Tuple[str, str, str]:
        try:
            from pocket.sessions import clear_engine_thread

            if pocket_sid:
                clear_engine_thread(pocket_sid)
        except Exception:
            pass
        fresh_job = {
            **job,
            "engine_thread_id": "",
            "codex_session_id": "",
            "_no_resume": True,
            "_idle_retry": True,
        }
        result2, err2, eng2 = _run_codex(prompt, product_cwd, job_id=job_id, job=fresh_job)
        return (
            header
            + f"(fresh thread: {reason})\n\n"
            + result2,
            err2,
            eng2,
        )

    if job.get("_no_resume"):
        pass  # already in fresh path — do not recurse on idle
    elif resumed and (err or rc != 0):
        reason = err or f"exit {rc}"
        return _fallback_fresh(f"resume failed for {engine_thread}: {reason[:100]}")
    elif (not job.get("_idle_retry")) and _codex_looks_idle(combined):
        # Poisoned/empty first turn or truncated prompt — one hard fresh retry
        return _fallback_fresh("idle ask-what-to-work-on; clearing thread")

    try:
        from pocket.reply_format import polish_agent_output

        polished = polish_agent_output(combined[-60000:], engine="codex")
    except Exception:
        polished = combined[-60000:]

    if err:
        return header + (polished or combined[-60000:]), err, "codex"
    if rc != 0:
        e = f"codex exit {rc}"
        if "os error 2" in combined.lower():
            e += f" (path/sandbox bridge={bridge_note or 'none'})"
        return header + (polished or combined[-60000:]), e, "codex"
    # record parsed tokens
    try:
        from pocket.sessions import record_llm_tokens
        from pocket.stream_util import _parse_tokens

        t = _parse_tokens(combined) or estimate_tokens(combined)
        if t:
            record_llm_tokens(t, engine="codex")
    except Exception:
        pass
    note = ""
    if thread_id and not _codex_looks_idle(combined):
        note = (
            f"\n\n[POCKET] Codex thread `{thread_id}` bound to this session. "
            "Next messages resume it — press +Codex for a separate session."
        )
    elif _codex_looks_idle(combined):
        note = (
            "\n\n[POCKET] Codex returned an idle prompt. Thread was not bound. "
            "Send again or press +Codex for a fresh session."
        )
    body = polished or "(empty)"
    if note and note.strip() not in body:
        body = body + note
    return header + body, "", "codex"


def _run_work_mode(
    prompt: str, cwd: str, job_id: str = "", session_id: str = ""
) -> Tuple[str, str, str]:
    """Working state: multi-intent board + real tools (not coding chat)."""
    from pocket.stream_util import update_progress
    from pocket.work_mode import run_work_turn

    if job_id:
        update_progress(
            job_id,
            f"Working board · live · {(prompt or '')[:140]}\n\nParsing tasks + running search…",
            engine="work",
        )
    r = run_work_turn(prompt, session_id=session_id or "", job_id=job_id)
    reply = r.get("reply") or json.dumps(r, indent=2)[:6000]
    # Light TTS — first choice / summary, not full markdown dump
    spoken = re.sub(r"\s+", " ", reply.split("## Working board")[0].split("```")[0]).strip()
    spoken = re.sub(r"[#*_`]", "", spoken)[:260]
    if len(spoken) > 40 and not spoken.startswith("|"):
        out = (
            f"[engine=work · Working board · live tools]\n\n{reply}\n\n"
            f"```tts\nrate=0.94\npitch=1.04\n{spoken}\n```"
        )
    else:
        out = f"[engine=work · Working board · live tools]\n\n{reply}\n"
    if job_id:
        update_progress(job_id, out[:8000], engine="work")
    return out, "" if r.get("ok", True) else str(r.get("error") or ""), "work"

def _run_mcp_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Agent MCP catalog / invoke — CLIs and tools without user tabs."""
    from pocket.mcp_bundle import catalog, invoke, list_tools
    from pocket.stream_util import update_progress

    text = (prompt or "").strip()
    low = text.lower()
    if job_id:
        update_progress(job_id, "MCP bundle…", engine="mcp")
    if not text or low in ("help", "?", "list", "catalog"):
        c = catalog()
        lines = [
            "# Embedded MCP (10) · agent access only",
            "",
            c.get("doctrine") or "",
            "",
            "## Internal (3)",
        ]
        for s in c.get("servers") or []:
            if s.get("kind") == "internal":
                lines.append(f"- **{s['id']}** — {s.get('blurb')}")
        lines.append("")
        lines.append("## External (7)")
        for s in c.get("servers") or []:
            if s.get("kind") == "external":
                lines.append(f"- **{s['id']}** — {s.get('blurb')}")
        lines.append("")
        lines.append("Invoke: `mcp pocket screen_sense` · `mcp github repos` · `cli gh --version`")
        return "\n".join(lines), "", "mcp"
    if low.startswith("mcp "):
        parts = text.split()
        server = parts[1] if len(parts) > 1 else "pocket"
        tool = parts[2] if len(parts) > 2 else "screen_status"
        r = invoke(server, tool)
        return f"```json\n{json.dumps(r, indent=2, default=str)[:5000]}\n```", "", "mcp"
    if low.startswith("invoke "):
        parts = text.split()
        r = invoke(parts[1] if len(parts) > 1 else "pocket", parts[2] if len(parts) > 2 else "cli_list")
        return f"```json\n{json.dumps(r, indent=2, default=str)[:5000]}\n```", "", "mcp"
    if low in ("tools",):
        return f"```json\n{json.dumps(list_tools(), indent=2)[:5000]}\n```", "", "mcp"
    r = invoke("pocket", "cli_list")
    return f"```json\n{json.dumps(r, indent=2, default=str)[:4000]}\n```", "", "mcp"


def _run_studio_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """First-class Product Studio agent — record · polish · viral · caption · ship."""
    import json
    import re
    from pocket.stream_util import update_progress
    from pocket.studio_core import run_studio_skill, studio_map, first_class_status, agent_brief

    text = (prompt or "").strip()
    low = text.lower()
    if job_id:
        update_progress(job_id, "Product Studio…", engine="studio")

    if not text or low in ("help", "?", "map", "status", "what can you do"):
        m = studio_map()
        st = first_class_status()
        lines = [
            "# Product Studio · first-class agent",
            "",
            agent_brief(),
            "",
            f"**Ready:** {st.get('ready')} · **ffmpeg:** {(st.get('video') or {}).get('ffmpeg')}",
            f"**Recordings:** {(st.get('video') or {}).get('recordings')} · **Exports:** {(st.get('video') or {}).get('exports')}",
            "",
            "## Say",
        ]
        for s in m.get("say_examples") or []:
            lines.append(f"- _{s}_")
        lines.append("")
        lines.append("## Skills")
        for f in (m.get("agent_features") or [])[:14]:
            lines.append(f"- `{f['skill']}` — {f['use']}")
        lines.append("")
        lines.append("UI: `/studio` · API: `GET /v1/studio/first-class`")
        return "\n".join(lines), "", "studio"

    # One-intent full loop first
    if re.search(
        r"\b(record and ship|stop and ship|full (demo|loop)|finish (the )?demo|"
        r"demo then ship|wrap (the )?demo|end (and )?ship)\b",
        low,
    ):
        skill = "studio_full_loop"
    elif re.search(r"\b(viral|polish|auto pack|product pack)\b", low):
        skill = "studio_viral"
    elif re.search(r"\b(ship)\b", low):
        skill = "studio_ship"
    elif re.search(r"\b(storyboard|beats|hook)\b", low):
        skill = "studio_storyboard"
    elif re.search(r"\b(caption|blurb|social post)\b", low):
        skill = "studio_caption"
    elif re.search(r"\b(start record|begin record|record (the )?(desk|screen|desktop))\b", low):
        skill = "studio_record_start"
    elif re.search(r"\b(stop record|end record)\b", low):
        skill = "studio_record_stop"
    elif re.search(r"\b(render|rotato|screencast|macbook|clean_demo)\b", low):
        skill = "studio_render"
    elif re.search(r"\b(list recording|recordings)\b", low):
        skill = "studio_list_recordings"
    elif re.search(r"\b(list export|exports)\b", low):
        skill = "studio_list_exports"
    elif re.search(r"\b(playbook|features)\b", low):
        skill = "studio_playbooks"
    elif re.search(r"\b(map|open studio)\b", low):
        skill = "studio_map" if "map" in low else "studio_open"
    elif re.search(r"\b(compose|imagine|still)\b", low):
        skill = "imagine_compose"
    elif re.search(r"\b(batch)\b", low):
        skill = "studio_batch"
    else:
        skill = "studio_status"

    if job_id:
        update_progress(job_id, f"Studio · {skill}", engine="studio")
    r = run_studio_skill(skill, prompt=text, params={})
    ok = bool(r.get("ok", True))
    md = f"## Studio · `{skill}`\n\n**{r.get('message') or ''}**\n\n```json\n{json.dumps(r, indent=2, default=str)[:5500]}\n```\n"
    if skill == "studio_full_loop":
        phase = r.get("phase") or ""
        md = f"## Studio full loop · `{phase}`\n\n**{r.get('message') or ''}**\n\n"
        if r.get("storyboard") and r["storyboard"].get("beats"):
            md += "### Storyboard\n" + "\n".join(
                f"- **{b.get('name')}**: {b.get('caption')}" for b in r["storyboard"]["beats"]
            ) + "\n\n"
        if r.get("next"):
            md += f"**Next:** {r.get('next')}\n\n"
        if r.get("ship") and r["ship"].get("exports"):
            md += "### Exports\n" + "\n".join(
                f"- {e.get('name') or e.get('preset') or e}" for e in (r["ship"].get("exports") or [])[:8]
            ) + "\n"
        md += f"\n```json\n{json.dumps({'steps': r.get('steps'), 'ok': r.get('ok')}, indent=2, default=str)[:2500]}\n```\n"
    if skill == "studio_storyboard" and r.get("beats"):
        md = "## Demo storyboard\n\n" + "\n".join(
            f"**{b.get('beat')}. {b.get('name')}** ({b.get('seconds')})\n"
            f"- On screen: {b.get('on_screen')}\n"
            f"- Agent: `{b.get('agent_action')}`\n"
            f"- Caption: _{b.get('caption')}_\n"
            for b in r["beats"]
        ) + f"\n**Next:** {r.get('next')}\n"
    if skill == "studio_caption" and r.get("social_posts"):
        md = (
            f"## Caption pack\n\n{r.get('launch_blurb')}\n\n### Social\n"
            + "\n\n".join(f"{i}. {p}" for i, p in enumerate(r["social_posts"], 1))
            + f"\n\nHashtags: {' '.join(r.get('hashtags') or [])}\n"
        )
    return md, "" if ok else str(r.get("error") or "studio failed"), "studio"


def _run_screen_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Screen share agent — view/control policy + fusion context for all agents."""
    from pocket.stream_util import update_progress

    text = (prompt or "").strip()
    low = text.lower()
    if job_id:
        update_progress(job_id, "Screen share · fusion…", engine="screen")
    try:
        from pocket.screen_share import status, set_share, fusion_context, act_for_agent, grab_frame
    except Exception as e:
        return "", f"screen share unavailable: {e}", "screen"

    if not text or low in ("help", "?", "status"):
        st = status()
        return (
            "# Screen · Fusion · VComputer\n\n"
            f"**mode:** `{st.get('mode')}` · **monitor:** {st.get('monitor')} · **vcomp:** {st.get('vcomp')}\n\n"
            "| Command | Effect |\n|---|---|\n"
            "| `view` / `control` / `off` | Share policy for all agents |\n"
            "| `sense` / `look` | Fusion context + frame |\n"
            "| `click Name` | Mouse (control mode only) |\n"
            "| `type hello` | Keyboard (control mode only) |\n"
            "| `vcomp on` / `vcomp off` | Virtual computer surface |\n\n"
            "_Open the **Screen** column on the desk for the live side panel._\n"
        ), "", "screen"

    if low in ("off", "stop share", "share off"):
        return f"```json\n{json.dumps(set_share(mode='off'), indent=2)[:1200]}\n```", "", "screen"
    if low in ("view", "share", "share on", "view only"):
        return f"```json\n{json.dumps(set_share(mode='view'), indent=2)[:1200]}\n```", "", "screen"
    if low in ("control", "control on", "let agents control"):
        return f"```json\n{json.dumps(set_share(mode='control', vcomp=True), indent=2)[:1200]}\n```", "", "screen"
    if low in ("vcomp on", "vcomputer on"):
        return f"```json\n{json.dumps(set_share(mode='view', vcomp=True), indent=2)[:1200]}\n```", "", "screen"
    if low in ("vcomp off",):
        return f"```json\n{json.dumps(set_share(vcomp=False), indent=2)[:1200]}\n```", "", "screen"
    if low in ("sense", "look", "observe", "context"):
        cx = fusion_context(agent="screen")
        fr = grab_frame(include_image=True) if cx.get("shared") else {}
        lines = [
            "# Screen sense",
            "",
            f"**shared:** {cx.get('shared')} · **mode:** {cx.get('mode')}",
            f"**brief:** {cx.get('brief') or cx.get('message') or '—'}",
            f"**symbols:** {', '.join(cx.get('symbols_sample') or [])[:400]}",
            "",
        ]
        if fr.get("markdown"):
            lines.append(fr["markdown"][:80000])
        return "\n".join(lines), "", "screen"
    if low.startswith("click "):
        r = act_for_agent("click", agent="screen", name=text.split(None, 1)[1].strip())
        return f"```json\n{json.dumps(r, indent=2)[:2000]}\n```", "" if r.get("ok") else r.get("error", ""), "screen"
    if low.startswith("type "):
        r = act_for_agent("type", agent="screen", text=text.split(None, 1)[1])
        return f"```json\n{json.dumps(r, indent=2)[:2000]}\n```", "" if r.get("ok") else r.get("error", ""), "screen"
    # default: sense + answer
    cx = fusion_context(agent="screen")
    return (
        f"# Screen\n\n{cx.get('brief') or cx.get('message')}\n\n"
        f"UI: {', '.join(cx.get('symbols_sample') or [])[:300]}\n"
    ), "", "screen"


def _run_vcomp_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Virtual computer agent — sense/act/shell on host machine surface."""
    from pocket.stream_util import update_progress

    text = (prompt or "").strip()
    low = text.lower()
    if job_id:
        update_progress(job_id, "VComputer…", engine="vcomp")
    try:
        from pocket.virtual_computer import status, open_computer, sense_computer, act, shell
    except Exception as e:
        return "", f"vcomp unavailable: {e}", "vcomp"

    if not text or low in ("help", "?"):
        st = status()
        return (
            "# POCKET Virtual Computer\n\n"
            f"**status:** {((st.get('state') or {}).get('status'))}\n"
            f"**workspace:** `{st.get('workspace')}`\n\n"
            "Commands: `open` · `sense` · `click Name` · `type …` · `shell …` · `status`\n"
            "Pairs with **Screen** column Control mode for mouse.\n"
        ), "", "vcomp"
    if low in ("open", "boot", "start"):
        return f"```json\n{json.dumps(open_computer(label='agent'), indent=2)[:2000]}\n```", "", "vcomp"
    if low in ("status",):
        return f"```json\n{json.dumps(status(), indent=2)[:2500]}\n```", "", "vcomp"
    if low in ("sense", "look"):
        return f"```json\n{json.dumps(sense_computer(), indent=2, default=str)[:4000]}\n```", "", "vcomp"
    if low.startswith("click "):
        r = act("click", name=text.split(None, 1)[1].strip())
        return f"```json\n{json.dumps(r, indent=2, default=str)[:2000]}\n```", "", "vcomp"
    if low.startswith("type "):
        r = act("type", text=text.split(None, 1)[1])
        return f"```json\n{json.dumps(r, indent=2, default=str)[:2000]}\n```", "", "vcomp"
    if low.startswith("shell ") or low.startswith("run "):
        cmd = text.split(None, 1)[1]
        r = shell(cmd)
        return f"```json\n{json.dumps(r, indent=2, default=str)[:3000]}\n```", "", "vcomp"
    open_computer(label="agent")
    s = sense_computer()
    return (
        f"# VComputer\n\n{s.get('brief')}\n\n"
        f"Hints: {s.get('action_hints')}\n"
        f"Say `click …` or `type …` to act.\n"
    ), "", "vcomp"


def _run_vision_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """First-class OCULUS vision agent — observe · map · OCR · find · click."""
    from pocket.stream_util import update_progress

    text = (prompt or "").strip()
    low = text.lower()
    if job_id:
        update_progress(job_id, "OCULUS vision · sensing host screen…", engine="vision")

    try:
        from pocket.vision_core import (
            observe,
            build_ui_map,
            find_in_map,
            click_by_name,
            windows_ocr_lines,
            grab_frame,
        )
    except Exception as e:
        return "", f"vision core unavailable: {e}", "vision"

    def _help() -> str:
        return (
            "# OCULUS · first-class vision\n\n"
            "Sensory layer for the host desk — not a screenshot toy.\n\n"
            "| Command | What it does |\n"
            "|---|---|\n"
            "| `observe` / `see` / `look` | Full observation (UI map + OCR brief + windows) |\n"
            "| `map` / `ui map` | Enumerate interactive UI elements |\n"
            "| `ocr` / `read screen` | OCR plain text from the screen |\n"
            "| `find <name>` | Search UI map for a control |\n"
            "| `click <name>` | Vision→action: map, match, click center |\n"
            "| `frame` / `shot` | Capture current frame metadata |\n"
            "| `status` | Last observation + live feed health |\n"
            "| `help` | This card |\n\n"
            "_Wired to `/v1/vision/*` · pixel_translator · live_vision · UI Automation._\n"
        )

    if not text or low in ("help", "?", "commands"):
        return _help(), "", "vision"

    try:
        if low in ("status", "health"):
            from pocket.live_vision import latest_frame
            from pathlib import Path

            live = latest_frame(include_image=False)
            last = Path.home() / ".pocket" / "vision" / "last_observation.json"
            brief = ""
            if last.exists():
                try:
                    import json as _json

                    o = _json.loads(last.read_text(encoding="utf-8"))
                    brief = str(o.get("brief") or "")[:400]
                except Exception:
                    pass
            out = (
                f"# Vision status\n\n"
                f"- **live seq:** {live.get('seq')}\n"
                f"- **frame path:** `{live.get('path') or '—'}`\n"
                f"- **last brief:** {brief or '—'}\n"
            )
            return out, "", "vision"

        if low in ("observe", "see", "look", "look around", "what do you see"):
            obs = observe(with_ui_map=True, with_ocr=True, with_understand=True)
            names = obs.get("ui_names") or []
            titles = obs.get("window_titles") or []
            lines = [
                "# OCULUS observe",
                "",
                f"**primary:** {obs.get('primary_modality') or obs.get('source') or '—'}",
                f"**why:** {obs.get('why_primary') or '—'}",
                f"**brief:** {obs.get('brief') or '—'}",
                f"**ui elements:** {obs.get('ui_map_count') or len(names)}",
                "",
                "### Windows",
            ]
            for t in titles[:12]:
                lines.append(f"- {t}")
            if not titles:
                lines.append("- _(none)_")
            lines.append("")
            lines.append("### UI sample")
            for n in names[:20]:
                lines.append(f"- {n}")
            ocr = (obs.get("ocr_plain") or "")[:1200]
            if ocr:
                lines.extend(["", "### OCR", "```", ocr, "```"])
            hints = obs.get("action_hints") or []
            if hints:
                lines.extend(["", "### Action hints"])
                for h in hints[:8]:
                    lines.append(f"- {h}")
            out = "\n".join(lines)
            if job_id:
                update_progress(job_id, out, engine="vision")
            return out, "", "vision"

        if low in ("map", "ui map", "ui_map", "elements"):
            ui = build_ui_map()
            els = ui.get("elements") or []
            lines = [f"# UI map · {ui.get('count') or len(els)} elements", ""]
            for e in els[:40]:
                lines.append(
                    f"- **{e.get('name')}** · {e.get('type','')} @ ({e.get('x')},{e.get('y')}) "
                    f"{e.get('w')}×{e.get('h')}"
                )
            return "\n".join(lines), "", "vision"

        if low in ("ocr", "read", "read screen", "readscreen", "text"):
            o = windows_ocr_lines()
            plain = o.get("plain_text") or ""
            if not plain and o.get("lines"):
                plain = "\n".join(
                    (ln.get("text") if isinstance(ln, dict) else str(ln)) for ln in o["lines"][:80]
                )
            out = f"# Screen OCR\n\n```\n{(plain or '(no text)')[:4000]}\n```\n"
            return out, "", "vision"

        if low.startswith("find ") or low.startswith("search "):
            q = text.split(None, 1)[1].strip()
            hits = find_in_map(q)
            if not hits:
                build_ui_map()
                hits = find_in_map(q)
            lines = [f"# Find `{q}` · {len(hits)} hit(s)", ""]
            for h in hits[:15]:
                lines.append(
                    f"- **{h.get('name')}** @ ({h.get('x')},{h.get('y')}) · {h.get('type','')}"
                )
            if not hits:
                lines.append("_No matches — try `map` or a shorter name._")
            return "\n".join(lines), "", "vision"

        if low.startswith("click "):
            name = text.split(None, 1)[1].strip().strip("\"'")
            r = click_by_name(name)
            out = (
                f"# Click `{name}`\n\n"
                f"- **ok:** {r.get('ok')}\n"
                f"- **method:** {r.get('method')}\n"
                f"- **matched:** {r.get('matched') or '—'}\n"
                f"- **candidates:** {r.get('candidates')}\n"
            )
            if r.get("error"):
                out += f"- **error:** {r.get('error')}\n"
            return out, "", "vision"

        if low in ("frame", "shot", "screenshot", "grab"):
            fr = grab_frame()
            out = (
                f"# Frame grab\n\n"
                f"- **ok:** {fr.get('ok')}\n"
                f"- **mime:** {fr.get('mime')}\n"
                f"- **live:** {fr.get('live')}\n"
            )
            b64 = fr.get("base64") or ""
            if b64:
                mime = fr.get("mime") or "image/jpeg"
                out += f"\n![frame](data:{mime};base64,{b64[:120000]})\n"
            return out, "", "vision"

        # Free-form: treat as observe + find if query-like
        if any(w in low for w in ("where", "what", "button", "window", "on screen", "do you see")):
            obs = observe(with_ui_map=True, with_ocr=True, with_understand=True)
            brief = obs.get("brief") or "Screen observed."
            names = ", ".join((obs.get("ui_names") or [])[:12])
            out = f"# OCULUS\n\n{brief}\n\n**UI:** {names or '—'}\n"
            return out, "", "vision"

        return _help() + f"\n_Unknown command:_ `{text[:120]}`\n", "", "vision"
    except Exception as e:
        return "", f"vision agent failed: {e}", "vision"


def _aria_local_reply(text: str) -> str:
    """Always-available Aria brain: everyday skills first, then warm fallback."""
    u = (text or "").strip()
    low = u.lower()
    if not u:
        return "I'm here — take your time."
    # Embedded everyday skills (todo, time, travel, focus, …)
    try:
        from pocket.voice_skills import try_skill, skill_help

        if re.search(r"\b(what can you (do|help)|your skills|help me with)\b", low):
            return skill_help()
        hit = try_skill(u)
        if hit:
            return hit[0]
    except Exception:
        pass
    if re.search(r"\b(who are you|what'?s your name|introduce yourself|are you (an? )?(ai|bot))\b", low):
        return (
            "Hey — I'm Aria. I help with everyday stuff while we talk — lists, reminders, "
            "time, focus, travel, quick drafts — and I'm patient if you need a second. What do you need?"
        )
    if re.search(r"\b(hello|hi|hey|good (morning|afternoon|evening))\b", low):
        return "Hey — good to hear you. What's going on?"
    if re.search(r"\b(thank|thanks|thx)\b", low):
        return "Anytime. I'm right here if you need anything else."
    if re.search(r"\b(refund|charge|billing|money back)\b", low):
        return "Sure — I can look at the billing with you. Was it a recent charge, and do you have an order number?"
    if re.search(r"\b(cancel|unsubscribe)\b", low):
        return "Got it. Is this a subscription or a one-time order? I'll walk you through canceling."
    if re.search(r"\b(broken|not work|bug|error|issue)\b", low):
        return "Ah, sorry about that. What were you trying to do, and what happens instead?"
    if re.search(r"\b(help|support|stuck)\b", low):
        return "I'm with you. Tell me the sticky part in one sentence and we'll unpack it."
    if re.search(r"\b(bye|goodbye|see you|later)\b", low):
        return "Take care — talk soon."
    snip = u if len(u) <= 90 else u[:87] + "…"
    return f"Okay, I heard you — “{snip}”. Want to dig into that, or is there something more urgent?"


def _voice_pack_reply(
    reply: str,
    *,
    thr: int = 1400,
    rate: float = 0.92,
    pitch: float = 1.06,
    source: str = "pocket-voice",
    listen: Optional[Dict] = None,
    buf: Optional[Dict] = None,
    err: str = "",
) -> Tuple[str, str, str]:
    spoken = re.sub(r"\s+", " ", (reply or "")).strip()
    if len(spoken) > 480:
        spoken = spoken[:460].rsplit(" ", 1)[0] + "…"
    try:
        rate_f = float(rate)
    except Exception:
        rate_f = 0.92
    rate_f = max(0.82, min(1.05, rate_f if rate_f else 0.92))
    try:
        pitch_f = float(pitch)
    except Exception:
        pitch_f = 1.06
    listen = listen or {}
    lines = [
        f"[engine=voice · Aria · patient {thr}ms · {source}]",
        "",
        reply,
        "",
        f"_listening: Aria · scenario={listen.get('scenario') or 'patient'} · "
        f"expert={listen.get('expert') or 'hotel_host'} · barge={listen.get('barge_in') or 'medium'}_",
    ]
    if buf and isinstance(buf, dict):
        try:
            bits = []
            for dom, entries in buf.items():
                if isinstance(entries, list) and entries:
                    bits.append(
                        f"{dom}: "
                        + ", ".join(
                            f"{e.get('key')}={e.get('value')}" for e in entries[:4] if isinstance(e, dict)
                        )
                    )
            if bits:
                lines.append("")
                lines.append("**Context buffer:** " + "; ".join(bits))
        except Exception:
            pass
    lines.append("")
    lines.append(f"```tts\nrate={rate_f}\npitch={pitch_f}\n{spoken}\n```")
    return "\n".join(lines), err, "voice"


def _run_voice_agent(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Voice product turn — Aria does real host work (skills, life ops, screen) + speak-back.

    Browser still does STT/TTS duplex; this path is the agent brain for typed or
    transcribed turns. Prefer host actions over empty small-talk.
    """
    from pocket.stream_util import update_progress

    text = (prompt or "").strip()
    if not text:
        return "", "Say something — voice agent needs a transcript or text.", "voice"

    if job_id:
        update_progress(job_id, "Aria · listening · acting…", engine="voice")

    session_id = f"pocket-{job_id or 'desk'}"
    try:
        from pocket.voice_product import run_voice_turn

        turn = run_voice_turn(text, session_id=session_id, job_id=job_id or "")
    except Exception as e:
        turn = {
            "ok": True,
            "reply": _aria_local_reply(text),
            "source": "aria-local-fallback",
            "error": str(e)[:160],
        }

    reply = str(turn.get("reply") or "").strip() or _aria_local_reply(text)
    source = str(turn.get("source") or "voice")
    thr = 1400
    fusion_result: Dict = turn.get("fusion") if isinstance(turn.get("fusion"), dict) else {}
    # Host action appendix (links) for desk display — keep spoken clean via tts fence
    extra_md = ""
    host = turn.get("host") if isinstance(turn.get("host"), dict) else None
    if host and isinstance(host.get("result"), dict):
        res = host["result"]
        links = res.get("links") or res.get("choices") or []
        if links:
            extra_md = "\n\n**Opened / options**\n" + "\n".join(
                f"- [{L.get('title') or 'link'}]({L.get('url')})" for L in links[:6] if isinstance(L, dict)
            )
        if res.get("gate_message"):
            extra_md += f"\n\n_{res.get('gate_message')}_"

    out, err, eng = _voice_pack_reply(
        reply + extra_md,
        thr=thr,
        rate=0.93,
        pitch=1.05,
        source=source,
        listen={"scenario": "patient", "expert": fusion_result.get("primary_expert") or "aria"},
        err=str(turn.get("error") or ""),
    )
    # Neural TTS URL for desk/phone Audio() player (edge-tts free)
    audio = turn.get("tts_audio") or ""
    if audio and "```tts" in out:
        out = out.rstrip() + f"\n\n```audio\n{audio}\n```\n"
    elif audio:
        out = out.rstrip() + f"\n\n```audio\n{audio}\n```\n"
    if job_id:
        update_progress(job_id, out, engine="voice")
    return out, err, eng


def _run_claude(prompt: str, cwd: str, job_id: str = "") -> Tuple[str, str, str]:
    """Prefer Claude Agent SDK (embedded agent loop); fall back to `claude` CLI."""
    # 1) Claude Agent SDK — same loop as Claude Code, streams into desk + sandbox receipts
    last_sdk = ""
    prefer_sdk = os.environ.get("POCKET_CLAUDE_SDK", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "cli",
    )
    if prefer_sdk:
        try:
            from pocket.claude_agent_bridge import run_claude_agent, sdk_installed

            if sdk_installed():
                sid = ""
                try:
                    from pocket.jobs import get as get_job

                    j = get_job(job_id) if job_id else None
                    if j:
                        sid = str(j.get("session_id") or "")
                except Exception:
                    pass
                out, err, eng = run_claude_agent(
                    prompt,
                    cwd,
                    job_id=job_id or "",
                    session_id=sid,
                )
                if out and not err:
                    return out, "", eng or "claude-agent-sdk"
                last_sdk = err or ""
                if out and err:
                    return out, err, eng or "claude-agent-sdk"
        except Exception as e:
            # never block desk if SDK path crashes
            last_sdk = str(e)

    # 2) Classic Claude Code CLI
    claude = which_claude()
    if not claude:
        if which_codex():
            result, err, _ = _run_codex(prompt, cwd, job_id=job_id)
            note = "_(Claude Agent SDK/CLI missing — Codex.)_"
            if last_sdk:
                note = f"_(Claude SDK: {last_sdk[:120]} — Codex.)_"
            return result + "\n\n" + note, err, "codex-fallback"
        msg = "claude CLI not installed and claude-agent-sdk unavailable"
        if last_sdk:
            msg += f" ({last_sdk[:200]})"
        return (
            "",
            msg + " — pip install claude-agent-sdk or install Claude Code CLI",
            "claude",
        )
    from pocket.stream_util import run_streaming

    last = ""
    for cmd in (
        [claude, "-p", prompt, "--output-format", "text"],
        [claude, "--print", prompt],
        [claude, "-p", prompt],
    ):
        out, rc, err = run_streaming(
            cmd, job_id=job_id, cwd=cwd, timeout=900, engine="claude"
        )
        text = (out or "").strip()
        if rc == 0 and text:
            try:
                from pocket.reply_format import polish_agent_output

                body = polish_agent_output(text[-60000:], engine="claude")
            except Exception:
                body = text[-60000:]
            return f"[engine=claude-cli cwd={cwd}]\n\n{body}", "", "claude"
        if "login" in text.lower() or "auth" in text.lower():
            return "", f"claude failed: {text[:2000]}", "claude"
        last = text or err or f"exit {rc}"
    return "", f"claude failed: {last[:2000]}", "claude"
