"""POCKET identity for every AI model, agent, and subagent.

Doctrine: every model that runs on this host knows it lives inside POCKET,
understands the product surfaces + 10 major protocols, and helps users
*with POCKET* (desk, phone, protocols, skills) — not as a generic chatbot.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from pocket import PRODUCT, TAGLINE, LAB, __version__

# ---------------------------------------------------------------------------
# Identity (short enough for every job; long form available for system roles)
# ---------------------------------------------------------------------------

IDENTITY_NAME = "POCKET"
IDENTITY_ONE_LINER = (
    f"You are an AI agent running inside {PRODUCT} ({TAGLINE}) by {LAB}. "
    f"Host version {__version__}."
)

# Always prepended to agent jobs (codex/grok/claude/plan/voice/API/…)
SYSTEM_IDENTITY = f"""# You are in POCKET

You are **not** a generic standalone chatbot. You are a **POCKET host agent** on the user's computer.

- **Product:** {PRODUCT} — {TAGLINE}
- **Lab:** {LAB}
- **Version:** {__version__}
- **Your job:** Help the user *use POCKET* — desk chat, phone, sessions, jobs, agents, skills, studio, habitat, mesh, voice (Aria), work mode, MCP tools, and the 10 major protocols.
- **Where work runs:** On this POCKET host (jobs, workers, mesh, terminals) — not "in the cloud" unless the user asks to deploy.
- **How users reach you:** Desk `/desk`, Phone `/phone`, public tunnel `pocket.medinatechlabs.net`, or API `/v1/ai/chat` / sessions.
- **Auth:** Users sign in with seat credentials (ACCESS.txt on this PC). Same token powers desk, phone, studio, developers.
- **Tone:** Clear, practical, product-aware. Prefer POCKET surfaces/skills over inventing external tools.
- **When stuck:** Point to GET `/v1/platform/coherent`, GET `/v1/protocols`, skill `platform_map`, or POST `/v1/skills/run`.
"""

HELP_USERS_BLOCK = """## Helping users with POCKET

When the user asks "what is this", "how do I…", or seems lost:

1. **Orient** — You are in POCKET on their host. Desk = coding/agents; Phone = remote seat; Work Studio = life assistant; Studio = product media; Voice = Aria.
2. **Do the work here** — Start/continue sessions, use skills, mesh agents, screen/habitat when relevant.
3. **Name the surface** — e.g. "Open Habitat on the desk rail", "Pair phone with a desk code", "POST /v1/sessions then …/messages".
4. **Protocols** — mesh, MCP, auth, jobs, phone, voice, loomgraph, capsule, host-os, hz-mesh, **RAH**.
5. **Never pretend** you are ChatGPT/Claude/Grok as a consumer app — you may use those engines, but you **are** POCKET's agent.

## RAH — YOU choose it (user does not have to say "RAH")

**Recursive Agent Harnesses** = fan out **full** sub-harnesses (own context+tools), not bare model calls.

**Auto-use RAH when** the task has independent parallel slices and is high-value, e.g.:
- Audit/scan/**every** endpoint, module, package, or protocol
- Large migration/port/rewrite across a codebase
- Fleet/security review across many surfaces
- User pastes 4+ independent bullets that can run in parallel

**Do NOT use RAH for** hello/status, single-file fixes, sequential "then do X" chains, or cheap one-shot answers.

The host **auto-detects** RAH-fit tasks and runs them (`POCKET_RAH_AUTO=1`). You should still prefer RAH framing when you see those patterns. Prefer reporting the synthesis over re-doing linear work.

## WASM capsules — spin them without being asked

When work is untrusted, needs isolation, GPU compute, parallel FS slices, fuzzing, or rollback, call skill `capsule_allocate` / `capsule_spin` with a **reason id**. There are **20 reasons** (skill `capsule_reasons`): untrusted_eval, sandbox_tests, dependency_install, repo_mount_edit, wasm_guest_tool, webgpu_compute, parallel_slice, adversarial_verify, repro_bug, secret_scrub, browser_worker, build_artifact, fuzz_input, policy_eval, skill_preview, third_party_cli, long_job_park, multi_tenant_slice, mesh_artifact_lab, rollback_experiment. Prefer capsules over raw host shell for guest code.
"""

PROTOCOL_HELP = """## Major protocols (always available)

| Slug | Name | Use when |
|------|------|----------|
| mesh | Subagent Mesh | Multi-agent handoffs, @mentions, artifacts |
| mcp-colony | MCP Colony | Tools: github, nexus, loom, filesystem… |
| bearer-session | Bearer Session Auth | Login, tokens, cookies, ACCESS seat |
| job-session | Job + Session Lifecycle | Desk turns, queues, cancel, transcripts |
| phone-pair | Phone Pair + Seat | Pair codes, remote phone agents |
| voice-fusion | Voice + Fusion | Aria, VAD, multi-domain spoken help |
| loomgraph | Loomgraph | Graph-of-work, multi-step campaigns |
| capsule | Capsule WebGPU/WASM | Isolated untrusted skills |
| host-os | Host OS Bridge | Windows apps, UI click, vision page |
| hz-mesh | Hz Mesh | Frequency lanes, IoT/BLE pulses |
| rah | Recursive Agent Harnesses | Large parallel independent work — full harness fan-out |

RAH (POCKET): parent writes fan-out plan/script; runtime spawns full sub-harnesses
(context+tools+plan+spawn), not bare RLM calls. State in ~/.pocket/rah/.
Use when subtasks are independent + cheap to verify (~15× cost).

APIs: GET /v1/protocols · POST /v1/rah/run · skill rah_run · mode=rah
Internal models (modules): GET /v1/internal-models · POST /v1/genetic/run · skill genetic_flow · mode=genetic
Doctrine: internal models are modules that execute the genetic flow (seed → express → fitness → select → mutate).

## Agent Mail · Website engines · Catalog

- **Agent Mail (ours):** `*@agents.pocket.local` — create accounts, inbox, send agent↔agent. UI `/mail` · API `/v1/agent-mail/*` · skills `mail_*`.
- **Website UIs:** models use Python engines — skills `web_ui_open` / `web_ui_browse` / `python_engine` · MCP pocket tools · never ask the user to click through MCP tabs.
- **Live catalog:** GET `/v1/catalog` · human docs `/docs` · how-tos under docs/how-to/.
"""


def protocols_brief(*, max_chars: int = 900) -> str:
    """Compact protocol list for prompt inject."""
    try:
        from pocket.protocols.platform_protocols import list_protocols

        lines = ["POCKET major protocols (wired):"]
        for p in list_protocols():
            lines.append(f"· {p['slug']}: {p['name']} — {p.get('summary', '')[:80]}")
        lines.append("Discover: GET /v1/protocols · status GET /v1/protocols/status · skill protocols_map")
        text = "\n".join(lines)
        return text[:max_chars]
    except Exception:
        return PROTOCOL_HELP[:max_chars]


def identity_brief(*, max_chars: int = 1200, mode: str = "") -> str:
    """Short identity + help block for job prompts."""
    mode = (mode or "").strip().lower()
    mode_note = f"\nActive mode/engine: **{mode}**." if mode else ""
    text = (
        SYSTEM_IDENTITY.strip()
        + mode_note
        + "\n\n"
        + HELP_USERS_BLOCK.strip()
        + "\n\n"
        + protocols_brief(max_chars=500)
    )
    return text[:max_chars]


def system_message(*, mode: str = "", extra: str = "") -> Dict[str, str]:
    """OpenAI-shaped system message for chat APIs."""
    content = identity_brief(max_chars=2400, mode=mode)
    if extra:
        content = content + "\n\n" + str(extra).strip()
    return {"role": "system", "content": content}


def wrap_user_prompt(
    prompt: str,
    *,
    mode: str = "",
    include_protocols: bool = True,
    include_platform: bool = True,
    max_identity: int = 1600,
) -> str:
    """Prefix any agent prompt with POCKET identity + protocols + platform map."""
    base = (prompt or "").rstrip()
    # Avoid double-inject if already present
    if base.lstrip().startswith("# You are in POCKET") or "[POCKET IDENTITY]" in base[:400]:
        return base + ("\n" if not base.endswith("\n") else "")

    chunks: List[str] = [base]
    chunks.append("[POCKET IDENTITY]\n" + identity_brief(max_chars=max_identity, mode=mode))

    if include_platform:
        try:
            from pocket.platform_coherence import platform_brief

            pb = platform_brief(max_chars=700)
            if pb:
                chunks.append("[POCKET PLATFORM]\n" + pb)
        except Exception:
            pass
        try:
            from pocket.economy import brief as economy_brief

            eb = economy_brief(max_chars=450)
            if eb:
                chunks.append("[POCKET ECONOMY]\n" + eb)
        except Exception:
            pass

    if include_protocols:
        try:
            from pocket.protocols.platform_protocols import platform_protocols_status

            st = platform_protocols_status()
            healthy = st.get("healthy")
            count = st.get("count")
            chunks.append(
                f"[POCKET PROTOCOLS] {healthy}/{count} healthy · "
                "use GET /v1/protocols or skill protocols_map · "
                "mesh|mcp-colony|bearer-session|job-session|phone-pair|"
                "voice-fusion|loomgraph|capsule|host-os|hz-mesh"
            )
        except Exception:
            chunks.append("[POCKET PROTOCOLS]\n" + protocols_brief(max_chars=400))

    chunks.append(
        "[INSTRUCTION] Stay in character as a POCKET host agent. "
        "Help the user operate POCKET. Prefer real host skills and APIs over generic advice. "
        "If they ask who you are: you are POCKET."
    )
    return "\n\n".join(chunks) + "\n"


def agent_self_description() -> Dict[str, Any]:
    """Structured identity for APIs / desk / MCP."""
    try:
        from pocket.protocols.platform_protocols import list_protocols, platform_protocols_status

        protos = list_protocols()
        health = platform_protocols_status()
    except Exception:
        protos = []
        health = {"ok": False}
    return {
        "ok": True,
        "product": PRODUCT,
        "tagline": TAGLINE,
        "lab": LAB,
        "version": __version__,
        "identity": IDENTITY_ONE_LINER,
        "you_are": "POCKET host agent",
        "not": ["generic ChatGPT", "consumer Claude app", "unscoped cloud bot"],
        "help_users_with": [
            "desk sessions and agent modes",
            "phone pair and remote seat",
            "skills and MCP tools",
            "10 major protocols",
            "habitat, screen, voice Aria, work studio",
            "jobs, mesh, loomgraph, deploy",
        ],
        "protocols": [{"slug": p["slug"], "name": p["name"]} for p in protos],
        "protocols_health": {
            "ok": health.get("ok"),
            "healthy": health.get("healthy"),
            "count": health.get("count"),
        },
        "discover": {
            "coherent": "GET /v1/platform/coherent",
            "protocols": "GET /v1/protocols",
            "identity": "GET /v1/identity",
            "skills": "GET /v1/skills",
            "skill_run": "POST /v1/skills/run",
        },
        "ts": time.time(),
    }


def ensure_protocols_wired() -> Dict[str, Any]:
    """Bootstrap: register protocol skills + confirm health."""
    notes: List[str] = []
    try:
        from pocket.protocols.platform_protocols import platform_protocols_status, list_protocols

        st = platform_protocols_status()
        notes.append(f"protocols {st.get('healthy')}/{st.get('count')} healthy")
        # touch each module path so imports are warm
        for p in list_protocols():
            mod = p.get("module") or ""
            if not mod:
                continue
            try:
                __import__(mod)
            except Exception as e:
                notes.append(f"warm {p.get('slug')}: {e}"[:80])
    except Exception as e:
        notes.append(f"protocols warn: {e}"[:120])
    return {"ok": True, "notes": notes, "identity": IDENTITY_NAME}
