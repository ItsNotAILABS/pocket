"""One coherent POCKET platform map — today's surfaces as one product.

Agents discover this via:
  GET /v1/platform/coherent
  GET /v1/skills  (platform skills tagged)
  POST /v1/skills/run  skill=platform_map | habitat_* | fusion_voice | …
  MCP pocket.* tools
  harness brief (agentic_harness.platform_brief)

Doctrine: Habitat · Chat · Screen · Workspace · Working · Phone · Fusion · MCP
are not separate products — one host co-pilot with agent-callable skills.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from pocket import __version__, PRODUCT, TAGLINE

# ---------------------------------------------------------------------------
# Product map (user-facing + agent-facing)
# ---------------------------------------------------------------------------

SURFACES: List[Dict[str, Any]] = [
    {
        "id": "loomgraph",
        "name": "LOOMGRAPH",
        "where": "/loomgraph · skill loomgraph_run · default forever harness",
        "api": [
            "/v1/loomgraph",
            "/v1/loomgraph/run",
            "/v1/loomgraph/self_test",
            "/v1/loomgraph/mermaid/{id}",
        ],
        "skills": [
            "loomgraph_run",
            "loomgraph_catalog",
            "loomgraph_mermaid",
            "loomgraph_status",
        ],
        "for": "Loop-Orchestrated Multi-agent Graph — see the graph, run the loop, ship with Pocket",
    },
    {
        "id": "keep",
        "name": "KEEP agents",
        "where": "POST /v1/keep/start · bound to chat session until chat ends",
        "api": ["/v1/keep", "/v1/keep/start", "/v1/keep/stop", "/v1/keep/end"],
        "skills": ["keep_start", "keep_status", "keep_stop"],
        "for": "Self-hosted agents that keep working until the chat ends; Docker/profile browsers",
    },
    {
        "id": "isolate",
        "name": "ISOLATE browsers",
        "where": "POST /v1/isolate/start · Docker Chromium or Edge profile",
        "api": ["/v1/isolate", "/v1/isolate/start", "/v1/isolate/stop"],
        "skills": ["isolate_start", "isolate_status"],
        "for": "Isolated browsers per agent session — torn down when chat ends",
    },
    {
        "id": "recall",
        "name": "RECALL codes",
        "where": "POST /v1/recall/mint · redeem to reattach KEEP/session",
        "api": ["/v1/recall", "/v1/recall/mint", "/v1/recall/redeem"],
        "skills": ["recall_mint", "recall_redeem"],
        "for": "Official recall-code software for work continuity",
    },
    {
        "id": "mail",
        "name": "POCKET MAIL + Agent Mail",
        "where": "Agent accounts @agents.pocket.local · inboxes · SMTP outbox",
        "api": [
            "/v1/mail",
            "/v1/mail/draft",
            "/v1/mail/send",
            "/v1/agent-mail",
            "/v1/agent-mail/accounts",
            "/v1/agent-mail/inbox",
            "/v1/agent-mail/send",
        ],
        "skills": [
            "mail_draft",
            "mail_send",
            "mail_status",
            "mail_accounts",
            "mail_account_create",
            "mail_inbox",
            "mail_read",
        ],
        "for": "Our own agent email accounts + official SMTP; models use Python engines/MCP",
    },
    {
        "id": "web_ui",
        "name": "Website UI Engine",
        "where": "Python MCP web_ui_* · remote browser · models run engines",
        "api": ["/v1/web-ui", "/v1/web-ui/open", "/v1/web-ui/sense", "/v1/python-engine"],
        "skills": [
            "web_ui_open",
            "web_ui_sense",
            "web_ui_act",
            "web_ui_browse",
            "web_ui_fetch",
            "python_engine",
            "python_engines_list",
        ],
        "for": "Models drive website interfaces via Python agents/engines + MCP (no user tabs)",
    },
    {
        "id": "habitat",
        "name": "Habitat",
        "where": "desk right of chat · tab Habitat",
        "api": ["/v1/habitat", "/v1/habitat/pulse", "/v1/habitat/assign"],
        "skills": ["habitat_status", "habitat_open", "habitat_pulse", "habitat_assign"],
        "for": "Agents live and work on the hybrid GUI floor",
    },
    {
        "id": "chat",
        "name": "Desk chat",
        "where": "desk center · tab Desk",
        "api": ["/v1/sessions", "/v1/jobs"],
        "skills": ["list_agents", "platform_map", "pocket_identity", "protocols_map"],
        "for": "One seated conversation at a time — every agent knows it is POCKET",
    },
    {
        "id": "protocols",
        "name": "Major protocols (+ RAH)",
        "where": "GET /v1/protocols · skill protocols_map · wired into every agent prompt",
        "api": [
            "/v1/protocols",
            "/v1/protocols/status",
            "/v1/protocols/{slug}",
            "/v1/identity",
            "/v1/rah/run",
        ],
        "skills": ["protocols_map", "protocols_status", "pocket_identity", "rah_run", "rah_plan"],
        "for": "mesh · mcp · session · jobs · phone · voice · loom · capsule · host-os · hz · RAH harness recursion",
    },
    {
        "id": "rah",
        "name": "Recursive Agent Harnesses",
        "where": "desk mode RAH · skill rah_run · ~/.pocket/rah/<run_id>/",
        "api": ["/v1/rah/run", "/v1/rah/plan", "/v1/rah/status", "/v1/protocols/rah"],
        "skills": ["rah_run", "rah_plan", "rah_status"],
        "for": "Large parallel independent work — parent script fans out full sub-harnesses",
    },
    {
        "id": "genetic",
        "name": "Internal models · genetic flow",
        "where": "mode=genetic · skill genetic_flow · modules under pocket.internal_models",
        "api": [
            "/v1/internal-models",
            "/v1/genetic/run",
            "/v1/internal-models/express",
            "/v1/genetic/status",
        ],
        "skills": ["internal_models", "genetic_flow", "genetic_status", "express_model"],
        "for": "Local internal models as modules; genetic flow evolves which ones express a goal",
    },
    {
        "id": "economy",
        "name": "Economic domain",
        "where": "desk rail Economy · GET /v1/economy · twin wallets",
        "api": [
            "/v1/economy",
            "/v1/economy/twins",
            "/v1/economy/transfer",
            "/v1/economy/escrow",
            "/v1/economy/parallax",
            "/v1/billing",
            "/v1/billing/webhook",
        ],
        "skills": ["economy_map", "economy_twins", "billing_status"],
        "for": "POCK wallets, digital twin wallets, escrow, clearing, Parallax paper rails, RevenueCat seats",
    },
    {
        "id": "screen",
        "name": "Screen · VComputer",
        "where": "desk column · tab Screen",
        "api": ["/v1/screen", "/v1/screen/context", "/v1/screen/act", "/v1/vcomp"],
        "skills": ["screen_status", "screen_view", "screen_control", "screen_sense", "vcomp_open"],
        "for": "Optional eyes / control + virtual computer for all agents",
    },
    {
        "id": "workspace",
        "name": "Workspace rail",
        "where": "desk right rail · pair codes · pixel memory",
        "api": ["/v1/node/pair", "/v1/vmem", "/v1/work-surface"],
        "skills": ["pair_mint", "pair_status", "vmem_status"],
        "for": "Summary, files, devices, pair phone",
    },
    {
        "id": "working",
        "name": "Working mode",
        "where": "desk Agents · phone Working tab",
        "api": ["/v1/work", "/v1/work/start", "/v1/work/package", "/v1/work/handoff"],
        "skills": ["work_start", "work_status", "work_package", "work_handoff"],
        "for": "Persistent voice + screen + package → artifacts",
    },
    {
        "id": "voice",
        "name": "Aria · Voice ↔ Voice",
        "where": "desk Voice agent · phone Aria first-class",
        "api": ["/v1/fusion/voice", "voice :8790 /v1/turn"],
        "skills": ["fusion_voice", "fusion_schema", "voice_skills_list", "aria_turn"],
        "for": "Patient VAD + Conversational Fusion (DFW hospitality graph)",
    },
    {
        "id": "voice_studio",
        "name": "Voice Studio (V2V multi-sensory)",
        "where": "/studio/voice · desk tab Voice Studio",
        "api": ["/studio/voice", "/v1/fusion/voice", "/v1/sessions"],
        "skills": ["voice_studio_open", "fusion_voice", "aria_turn", "platform_map"],
        "for": "60fps canvas · persona×mindset · code snap · fusion — paper home in product",
    },
    {
        "id": "remote_browser",
        "name": "Our remote browser (must beat theirs)",
        "where": "Browser agent · Screen · VComp · /v1/remote-browser",
        "api": [
            "/v1/remote-browser",
            "/v1/remote-browser/open",
            "/v1/remote-browser/sense",
            "/v1/remote-browser/act",
            "/v1/remote-browser/benchmark",
        ],
        "skills": [
            "remote_browser_status",
            "remote_browser_open",
            "remote_browser_sense",
            "remote_browser_benchmark",
        ],
        "for": "Signed-in Edge + Fusion on host — remote via tunnel still executes here",
    },
    {
        "id": "iot_home",
        "name": "Phone + home IoT",
        "where": "/phone · /v1/iot · HZ mesh",
        "api": ["/v1/iot", "/v1/iot/devices", "/v1/iot/phone", "/v1/node/pair"],
        "skills": ["iot_status", "iot_list", "iot_register", "iot_phone", "iot_hz_status"],
        "for": "Phone works; pair desk; register home devices; BLE/HZ adjacency",
    },
    {
        "id": "our_cloud",
        "name": "Our computing clouds",
        "where": "GET /v1/sovereign · /v1/computing-clouds",
        "api": ["/v1/sovereign", "/v1/computing-clouds", "/v1/platform"],
        "skills": ["sovereign_stack", "computing_clouds"],
        "for": "Host + tunnel + deploys + Auro + NEXUS + mesh — work in our perimeter",
    },
    {
        "id": "phone",
        "name": "POCKET Phone",
        "where": "/phone · desk tab Phone (in-app)",
        "api": ["/phone", "/v1/node/redeem", "/v1/sessions"],
        "skills": ["phone_surface", "pair_mint", "pair_status"],
        "for": "Remote desk · Aria/Working · pair seamless",
    },
    {
        "id": "fusion_visual",
        "name": "Visual Fusion · RFE",
        "where": "Screen column · vision workers",
        "api": ["/v1/fusion/remake", "/v1/rfe/synthesize", "/v1/vision/page"],
        "skills": ["fusion_remake", "rfe_synthesize", "screen_sense", "page_render"],
        "for": "UIA+OCR+visual → remake / 3D",
    },
    {
        "id": "mcp_cli",
        "name": "MCP · CLI (agent-only)",
        "where": "no user tabs — agents invoke",
        "api": ["/v1/mcp", "/v1/mcp/invoke", "/v1/cli/run"],
        "skills": ["mcp_catalog", "mcp_invoke", "cli_list", "cli_run"],
        "for": "10 MCPs + host CLIs headlessly",
    },
    {
        "id": "novae",
        "name": "NOVAE hands",
        "where": "desk Grok Novae · Codex Novae · /v1/novae",
        "api": [
            "/v1/novae",
            "/v1/novae/list",
            "/v1/novae/status",
            "/v1/novae/activate",
        ],
        "skills": ["novae_list", "novae_activate", "novae_status"],
        "for": "Nova lives inside POCKET — Grok research hands + Codex coding hands, same habitat/workspace",
    },
    {
        "id": "imagine",
        "name": "Imagine Studio",
        "where": "/imagine · /studio/imagine · desk More → Imagine",
        "api": [
            "/imagine",
            "/v1/imagine",
            "/v1/imagine/gallery",
            "/v1/imagine/compose",
            "/v1/imagine/file",
            "/v1/fusion/remake",
        ],
        "skills": ["imagine_status", "imagine_gallery", "imagine_compose"],
        "for": "Letterboxed device stills from the host screen + fusion remake — not a prompt-to-image generator",
    },
    {
        "id": "foundations",
        "name": "Internal AI foundations",
        "where": "GET /v1/foundations · skill foundations_map",
        "api": ["/v1/foundations", "/v1/internal-models", "/v1/genetic", "/v1/identity"],
        "skills": ["foundations_map", "internal_models", "genetic_flow", "express_model"],
        "for": "Computational AI + math + self + intelligence world — all internal, no third-party inference required",
    },
    {
        "id": "bots",
        "name": "POCKET Bots",
        "where": "/bots · desk tab Bots · pocket-agent teammates",
        "api": ["/bots", "/v1/bots", "/v1/bots/hire", "/v1/bots/{id}/message", "/v1/bots/{id}/pulse"],
        "skills": ["bots_list", "bots_hire", "bots_message"],
        "for": "Grok-Bot-style named teammates with their own computer, threads, and always-on pulse — powered by pocket-agent",
    },
]

FLOW = [
    "1. Habitat — agents live on the floor (open by default on desk)",
    "2. Seat an agent in Chat (Codex · Grok · Aria · Working · …)",
    "3. Screen optional — View/Control + VComp so agents see/drive host",
    "4. Workspace — files, helpers, Get pair code for phone",
    "5. Phone — same host · Aria/Working first-class · redeem pair code",
    "6. Voice turns → Conversational Fusion (POCKET) → expert/patience/preload",
    "7. Working packages conversation → handoff artifacts",
    "8. Agents call skills/MCP/CLI — never need separate apps for core loops",
    "9. Seat Novae (Grok / Codex) for research or coding hands in the same workspace",
    "10. Imagine Studio — compose host UI into phone/laptop stills at /imagine",
]

# Agent-callable platform skills (id → definition)
PLATFORM_SKILLS: Dict[str, Dict[str, Any]] = {
    "platform_map": {
        "worker": "ARCHON",
        "desc": "Full coherent platform map (surfaces, flow, findability)",
        "tags": ["platform", "discover"],
        "kind": "atomic",
    },
    "platform_health": {
        "worker": "ARCHON",
        "desc": "Domain health for habitat/screen/work/fusion/mcp/agents/novae",
        "tags": ["platform", "health"],
        "kind": "atomic",
    },
    "novae_list": {
        "worker": "ARCHON",
        "desc": "List Grok Novae + Codex Novae hands and workspace",
        "tags": ["platform", "novae", "agents"],
        "kind": "atomic",
    },
    "novae_status": {
        "worker": "ARCHON",
        "desc": "Novae activation + last goal",
        "tags": ["platform", "novae"],
        "kind": "atomic",
    },
    "novae_activate": {
        "worker": "ARCHON",
        "desc": "Activate Grok Novae or Codex Novae in platform workspace",
        "tags": ["platform", "novae", "agents"],
        "kind": "atomic",
    },
    "protocols_map": {
        "worker": "ARCHON",
        "desc": "Ten major POCKET protocols catalog (mesh, MCP, auth, jobs, phone, voice…)",
        "tags": ["platform", "protocols", "discover"],
        "kind": "atomic",
    },
    "protocols_status": {
        "worker": "ARCHON",
        "desc": "Health of all 10 major protocols",
        "tags": ["platform", "protocols", "health"],
        "kind": "atomic",
    },
    "pocket_identity": {
        "worker": "ARCHON",
        "desc": "Who we are: POCKET host agents — help users with POCKET",
        "tags": ["platform", "identity"],
        "kind": "atomic",
    },
    "rah_run": {
        "worker": "ARCHON",
        "desc": "Recursive Agent Harnesses — fan out full sub-harnesses in parallel (expensive)",
        "tags": ["platform", "rah", "harness", "orchestration"],
        "kind": "composite",
    },
    "rah_plan": {
        "worker": "ARCHON",
        "desc": "Plan RAH leaf fan-out without executing (preview independence)",
        "tags": ["platform", "rah", "harness"],
        "kind": "atomic",
    },
    "rah_status": {
        "worker": "ARCHON",
        "desc": "RAH live/recent runs and defaults",
        "tags": ["platform", "rah", "health"],
        "kind": "atomic",
    },
    "internal_models": {
        "worker": "ARCHON",
        "desc": "List internal models as modules (ghost, world, auro, guppy, heuristic, identity)",
        "tags": ["platform", "models", "genetic", "internal"],
        "kind": "atomic",
    },
    "genetic_flow": {
        "worker": "ARCHON",
        "desc": "Run genetic flow — evolve which internal model modules execute for a goal",
        "tags": ["platform", "genetic", "models", "orchestration"],
        "kind": "composite",
    },
    "genetic_status": {
        "worker": "ARCHON",
        "desc": "Recent genetic flow runs + module readiness",
        "tags": ["platform", "genetic", "health"],
        "kind": "atomic",
    },
    "express_model": {
        "worker": "ARCHON",
        "desc": "Express one internal model module on a goal (no full genetic loop)",
        "tags": ["platform", "models", "internal"],
        "kind": "atomic",
    },
    "mail_status": {
        "worker": "SCRIBE",
        "desc": "Agent mail + POCKET MAIL status (accounts, inboxes, SMTP)",
        "tags": ["mail", "agents", "inbox"],
        "kind": "atomic",
    },
    "mail_accounts": {
        "worker": "SCRIBE",
        "desc": "List our agent email accounts (@agents.pocket.local)",
        "tags": ["mail", "agents"],
        "kind": "atomic",
    },
    "mail_account_create": {
        "worker": "SCRIBE",
        "desc": "Create our own email account for an agent",
        "tags": ["mail", "agents"],
        "kind": "atomic",
    },
    "mail_inbox": {
        "worker": "SCRIBE",
        "desc": "Read an agent inbox",
        "tags": ["mail", "inbox"],
        "kind": "atomic",
    },
    "mail_send": {
        "worker": "SCRIBE",
        "desc": "Send agent↔agent or external mail",
        "tags": ["mail", "send"],
        "kind": "atomic",
    },
    "mail_read": {
        "worker": "SCRIBE",
        "desc": "Open one agent mail message",
        "tags": ["mail", "inbox"],
        "kind": "atomic",
    },
    "mail_draft": {
        "worker": "SCRIBE",
        "desc": "Official POCKET MAIL draft (SMTP path)",
        "tags": ["mail", "draft"],
        "kind": "atomic",
    },
    "web_ui_open": {
        "worker": "NAVIGATOR",
        "desc": "Open website in host browser (Python engine)",
        "tags": ["web", "browser", "mcp"],
        "kind": "atomic",
    },
    "web_ui_sense": {
        "worker": "NAVIGATOR",
        "desc": "Sense open website UI for agents",
        "tags": ["web", "browser", "mcp"],
        "kind": "atomic",
    },
    "web_ui_act": {
        "worker": "NAVIGATOR",
        "desc": "Act on website interface (click/type when armed)",
        "tags": ["web", "browser", "mcp"],
        "kind": "atomic",
    },
    "web_ui_browse": {
        "worker": "NAVIGATOR",
        "desc": "Open website + sense (MCP website interface session)",
        "tags": ["web", "browser", "mcp"],
        "kind": "composite",
    },
    "web_ui_fetch": {
        "worker": "SCRUTATOR",
        "desc": "Fetch URL text headlessly",
        "tags": ["web", "fetch"],
        "kind": "atomic",
    },
    "web_ui_search": {
        "worker": "SCRUTATOR",
        "desc": "Host web search for models",
        "tags": ["web", "search"],
        "kind": "atomic",
    },
    "web_ui_status": {
        "worker": "NAVIGATOR",
        "desc": "Website UI engine + Python engines catalog",
        "tags": ["web", "engines"],
        "kind": "atomic",
    },
    "python_engine": {
        "worker": "ARCHON",
        "desc": "Run a named Python agent/engine (browser, mail, genetic, auro…)",
        "tags": ["engines", "python", "models", "mcp"],
        "kind": "composite",
    },
    "python_engines_list": {
        "worker": "ARCHON",
        "desc": "List Python agents/engines models can invoke",
        "tags": ["engines", "python", "discover"],
        "kind": "atomic",
    },
    "engine_uses": {
        "worker": "ARCHON",
        "desc": "20 named uses for web_ui + python_engine (research, browse, mail, forge…)",
        "tags": ["engines", "web", "uses"],
        "kind": "atomic",
    },
    "engine_use": {
        "worker": "ARCHON",
        "desc": "Run one named use id (or auto-pick from prompt)",
        "tags": ["engines", "web", "uses"],
        "kind": "composite",
    },
    "model_build": {
        "worker": "ARCHON",
        "desc": "Build a new internal model and register it on the platform",
        "tags": ["models", "forge", "platform"],
        "kind": "composite",
    },
    "model_list_built": {
        "worker": "ARCHON",
        "desc": "List agent-built models on this host",
        "tags": ["models", "forge"],
        "kind": "atomic",
    },
    "model_register": {
        "worker": "ARCHON",
        "desc": "Register built models into genetic/express registry",
        "tags": ["models", "forge"],
        "kind": "atomic",
    },
    "model_suggest": {
        "worker": "ARCHON",
        "desc": "Suggest a model blueprint from a free-text goal",
        "tags": ["models", "forge"],
        "kind": "atomic",
    },
    "agents_toolkit": {
        "worker": "ARCHON",
        "desc": "Full agent toolkit: internal MCP tools, 20 uses, skills, engines, model forge",
        "tags": ["platform", "mcp", "agents", "discover"],
        "kind": "atomic",
    },
    "agent_invoke": {
        "worker": "ARCHON",
        "desc": "Call any named being (ARCHON, OCULUS, KEEP, SOLUS, Aria…) — the AI invoke path",
        "tags": ["platform", "agents", "invoke"],
        "kind": "composite",
    },
    "agent_roster": {
        "worker": "ARCHON",
        "desc": "List every invocable sub-agent / organism and how to call it",
        "tags": ["platform", "agents", "discover"],
        "kind": "atomic",
    },
    "autonomous_status": {
        "worker": "ARCHON",
        "desc": "Status of KEEP, swarm, dream, organism, mesh hook, RAH, Damian",
        "tags": ["platform", "agents", "autonomous"],
        "kind": "atomic",
    },
    "autonomous_ensure": {
        "worker": "ARCHON",
        "desc": "Arm mesh hook + swarm + dreams + Damian so autonomous agents actually run",
        "tags": ["platform", "agents", "autonomous"],
        "kind": "composite",
    },
    "keep_start": {
        "worker": "ARCHON",
        "desc": "Start a KEEP agent bound to this chat until the session ends",
        "tags": ["platform", "keep", "autonomous"],
        "kind": "composite",
    },
    "keep_status": {
        "worker": "ARCHON",
        "desc": "KEEP agents currently running",
        "tags": ["platform", "keep"],
        "kind": "atomic",
    },
    "keep_stop": {
        "worker": "ARCHON",
        "desc": "Stop a KEEP agent (or end_chat for a session)",
        "tags": ["platform", "keep"],
        "kind": "atomic",
    },
    "kernel_status": {
        "worker": "ARCHON",
        "desc": "Neuro-Silicon userspace driver status (honest lanes, no slide FLOPS)",
        "tags": ["platform", "kernel", "neuro"],
        "kind": "atomic",
    },
    "kernel_calibrate": {
        "worker": "ARCHON",
        "desc": "Measure slab + matmul + 5-stage cognitive loop on this host",
        "tags": ["platform", "kernel", "neuro"],
        "kind": "composite",
    },
    "kernel_slab": {
        "worker": "ARCHON",
        "desc": "SLUB-shaped userspace slab status or bench",
        "tags": ["platform", "kernel"],
        "kind": "atomic",
    },
    "cognitive_loop": {
        "worker": "ARCHON",
        "desc": "Run 5 cognitive stages against the real agent roster",
        "tags": ["platform", "kernel", "agents"],
        "kind": "composite",
    },
    "workflow_start": {
        "worker": "ARCHON",
        "desc": "Start a long-running workflow (days). Host-bound context + ticks + compact.",
        "tags": ["platform", "kernel", "workflow", "long"],
        "kind": "composite",
    },
    "workflow_tick": {
        "worker": "ARCHON",
        "desc": "Force one long-workflow tick (cognitive loop + extras + checkpoint)",
        "tags": ["platform", "kernel", "workflow"],
        "kind": "composite",
    },
    "workflow_status": {
        "worker": "ARCHON",
        "desc": "List or get long workflows",
        "tags": ["platform", "kernel", "workflow"],
        "kind": "atomic",
    },
    "workflow_stop": {
        "worker": "ARCHON",
        "desc": "Pause/resume/stop a long workflow",
        "tags": ["platform", "kernel", "workflow"],
        "kind": "atomic",
    },
    "multi_plan": {
        "worker": "ARCHON",
        "desc": "Reason → task list + sub-agents → execute with live sovereign terminal in chat",
        "tags": ["platform", "plan", "subagents", "orchestration"],
        "kind": "composite",
    },
    "mcp_stream": {
        "worker": "ARCHON",
        "desc": "Live MCP JSON-RPC protocol stream — every tools/call frame in/out",
        "tags": ["platform", "mcp", "protocol", "stream", "jsonrpc"],
        "kind": "atomic",
    },
    "call_status": {
        "worker": "ARCHON",
        "desc": "Agent virtual numbers + call status (softphone / optional PSTN)",
        "tags": ["phone", "calls", "virtual"],
        "kind": "atomic",
    },
    "call_numbers": {
        "worker": "ARCHON",
        "desc": "List agent virtual numbers (+p-XXX-XXXX)",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "call_assign": {
        "worker": "ARCHON",
        "desc": "Assign a virtual number to an agent",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "call_dial": {
        "worker": "ARCHON",
        "desc": "Dial from agent virtual number (soft call or PSTN if Twilio set)",
        "tags": ["phone", "calls", "dial"],
        "kind": "composite",
    },
    "call_answer": {
        "worker": "ARCHON",
        "desc": "Answer a ringing agent call",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "call_hangup": {
        "worker": "ARCHON",
        "desc": "Hang up an agent call",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "call_speak": {
        "worker": "ARCHON",
        "desc": "Speak/text on an active soft call",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "call_list": {
        "worker": "ARCHON",
        "desc": "List recent agent calls",
        "tags": ["phone", "calls"],
        "kind": "atomic",
    },
    "economy_map": {
        "worker": "ARCHON",
        "desc": "Economic domain: wallets, twin wallets, escrow, clearing, Parallax bridge",
        "tags": ["platform", "economy", "wallet"],
        "kind": "atomic",
    },
    "economy_twins": {
        "worker": "ARCHON",
        "desc": "List digital twin wallets for agents",
        "tags": ["economy", "twin", "wallet"],
        "kind": "atomic",
    },
    "billing_status": {
        "worker": "ARCHON",
        "desc": "RevenueCat entitlements + POCK refill status (never auto-pay)",
        "tags": ["economy", "billing", "revenuecat"],
        "kind": "atomic",
    },
    "billing_sync": {
        "worker": "ARCHON",
        "desc": "Pull a RevenueCat subscriber and apply seats / plan",
        "tags": ["economy", "billing", "revenuecat"],
        "kind": "atomic",
    },
    "list_agents": {
        "worker": "ARCHON",
        "desc": "First-class desk + phone agents",
        "tags": ["platform", "agents"],
        "kind": "atomic",
    },
    "habitat_status": {
        "worker": "ARCHON",
        "desc": "Habitat residents, rooms, activity",
        "tags": ["habitat"],
        "kind": "atomic",
    },
    "habitat_open": {
        "worker": "ARCHON",
        "desc": "Mark habitat open for desk session",
        "tags": ["habitat"],
        "kind": "atomic",
    },
    "habitat_pulse": {
        "worker": "ARCHON",
        "desc": "Pulse a resident status/line",
        "tags": ["habitat"],
        "kind": "atomic",
    },
    "habitat_assign": {
        "worker": "ARCHON",
        "desc": "Assign task to habitat resident",
        "tags": ["habitat"],
        "kind": "atomic",
    },
    "screen_status": {
        "worker": "OCULUS",
        "desc": "Screen share mode status",
        "tags": ["screen"],
        "kind": "atomic",
    },
    "screen_view": {
        "worker": "OCULUS",
        "desc": "Enable View mode (agents see fusion screen)",
        "tags": ["screen"],
        "kind": "atomic",
    },
    "screen_control": {
        "worker": "OCULUS",
        "desc": "Enable Control mode (agents may drive mouse/keyboard)",
        "tags": ["screen"],
        "kind": "atomic",
    },
    "screen_off": {
        "worker": "OCULUS",
        "desc": "Turn screen share off",
        "tags": ["screen"],
        "kind": "atomic",
    },
    "screen_sense": {
        "worker": "OCULUS",
        "desc": "Fusion context brief from shared screen",
        "tags": ["screen", "fusion"],
        "kind": "atomic",
    },
    "vcomp_open": {
        "worker": "ARCHON",
        "desc": "Open virtual computer workspace",
        "tags": ["vcomp"],
        "kind": "atomic",
    },
    "work_start": {
        "worker": "ARCHON",
        "desc": "Start Working mode session",
        "tags": ["work", "voice"],
        "kind": "atomic",
    },
    "work_status": {
        "worker": "ARCHON",
        "desc": "Live Working sessions",
        "tags": ["work"],
        "kind": "atomic",
    },
    "work_package": {
        "worker": "ARCHON",
        "desc": "Package working conversation",
        "tags": ["work"],
        "kind": "atomic",
    },
    "work_handoff": {
        "worker": "ARCHON",
        "desc": "Handoff package → artifacts",
        "tags": ["work"],
        "kind": "atomic",
    },
    "fusion_voice": {
        "worker": "ARCHON",
        "desc": "Conversational Fusion: route expert/patience/preload (DFW)",
        "tags": ["fusion", "voice", "phone"],
        "kind": "atomic",
    },
    "fusion_schema": {
        "worker": "ARCHON",
        "desc": "Conversational Fusion schema + experts",
        "tags": ["fusion", "voice"],
        "kind": "atomic",
    },
    "fusion_last": {
        "worker": "ARCHON",
        "desc": "Last fusion result for session_id",
        "tags": ["fusion"],
        "kind": "atomic",
    },
    "voice_skills_list": {
        "worker": "ARCHON",
        "desc": "Aria everyday skills (time, lists, travel…)",
        "tags": ["voice"],
        "kind": "atomic",
    },
    "aria_turn": {
        "worker": "ARCHON",
        "desc": "Local Aria skill try + fusion hint (no mic)",
        "tags": ["voice"],
        "kind": "atomic",
    },
    "phone_surface": {
        "worker": "ARCHON",
        "desc": "Phone surface URLs + pair instructions",
        "tags": ["phone"],
        "kind": "atomic",
    },
    "pair_mint": {
        "worker": "ARCHON",
        "desc": "Mint desk pair code for phone",
        "tags": ["phone", "pair"],
        "kind": "atomic",
    },
    "pair_status": {
        "worker": "ARCHON",
        "desc": "Node identity + peers + open codes",
        "tags": ["phone", "pair"],
        "kind": "atomic",
    },
    "mcp_catalog": {
        "worker": "ARCHON",
        "desc": "10 embedded MCPs catalog",
        "tags": ["mcp"],
        "kind": "atomic",
    },
    "mcp_invoke": {
        "worker": "ARCHON",
        "desc": "Invoke MCP server.tool (params.server + params.tool)",
        "tags": ["mcp"],
        "kind": "atomic",
    },
    "cli_list": {
        "worker": "ARCHON",
        "desc": "CLI inventory for agents",
        "tags": ["cli"],
        "kind": "atomic",
    },
    "cli_run": {
        "worker": "ARCHON",
        "desc": "Run allowlisted CLI (params.bin + args)",
        "tags": ["cli"],
        "kind": "atomic",
    },
    "find_feature": {
        "worker": "ARCHON",
        "desc": "Find where a feature lives (desk tab, phone, API, skill)",
        "tags": ["platform", "discover"],
        "kind": "atomic",
    },
    "voice_studio_open": {
        "worker": "ARCHON",
        "desc": "Voice Studio URL + map paper → product (canvas, snap, fusion)",
        "tags": ["voice", "studio"],
        "kind": "atomic",
    },
    "sovereign_stack": {
        "worker": "ARCHON",
        "desc": "Doctrine: our remote browser, remote, phone IoT, our clouds",
        "tags": ["platform", "sovereign"],
        "kind": "atomic",
    },
    "computing_clouds": {
        "worker": "ARCHON",
        "desc": "Inventory OUR computing clouds (host, tunnel, deploys, Auro, NEXUS, HZ)",
        "tags": ["cloud", "sovereign"],
        "kind": "atomic",
    },
    "remote_browser_status": {
        "worker": "NAVIGATOR",
        "desc": "Our remote browser status vs theirs",
        "tags": ["browser", "remote"],
        "kind": "atomic",
    },
    "remote_browser_open": {
        "worker": "NAVIGATOR",
        "desc": "Open URL in signed-in Edge (our remote browser)",
        "tags": ["browser", "remote"],
        "kind": "atomic",
    },
    "remote_browser_sense": {
        "worker": "OCULUS",
        "desc": "Fusion sense pack for remote browser",
        "tags": ["browser", "fusion"],
        "kind": "atomic",
    },
    "remote_browser_benchmark": {
        "worker": "ARCHON",
        "desc": "Run suite: our remote browser must pass every axis",
        "tags": ["browser", "benchmark"],
        "kind": "atomic",
    },
    "iot_status": {
        "worker": "ARCHON",
        "desc": "Home IoT + phone bridge status",
        "tags": ["iot", "phone"],
        "kind": "atomic",
    },
    "iot_list": {
        "worker": "ARCHON",
        "desc": "List home IoT devices",
        "tags": ["iot"],
        "kind": "atomic",
    },
    "iot_register": {
        "worker": "ARCHON",
        "desc": "Register a home IoT device (name, kind, room, address)",
        "tags": ["iot"],
        "kind": "atomic",
    },
    "iot_phone": {
        "worker": "ARCHON",
        "desc": "Phone LAN/remote/pair bridge for home",
        "tags": ["iot", "phone"],
        "kind": "atomic",
    },
    "iot_hz_status": {
        "worker": "ARCHON",
        "desc": "HZ offline mesh status for phone BLE / home adjacency",
        "tags": ["iot", "mesh"],
        "kind": "atomic",
    },
    # --- Everyday life (embedded for all agents) ---
    "life_catalog": {
        "worker": "ARCHON",
        "desc": "Catalog of everyday life skills (food, flights, shop, web, reserve)",
        "tags": ["life", "discover"],
        "kind": "atomic",
    },
    "life_status": {
        "worker": "ARCHON",
        "desc": "Working board + life ops status",
        "tags": ["life", "work"],
        "kind": "atomic",
    },
    "life_classify": {
        "worker": "ARCHON",
        "desc": "Classify text into food/flight/shop/browse/reservation",
        "tags": ["life", "route"],
        "kind": "atomic",
    },
    "food_order": {
        "worker": "NAVIGATOR",
        "desc": "Food delivery options in Edge — you pay (never auto-checkout)",
        "tags": ["life", "food"],
        "kind": "atomic",
    },
    "flight_search": {
        "worker": "NAVIGATOR",
        "desc": "Flight search (Google Flights) — you book & pay",
        "tags": ["life", "travel"],
        "kind": "atomic",
    },
    "shop_search": {
        "worker": "NAVIGATOR",
        "desc": "Shopping search (Amazon etc.) — you checkout",
        "tags": ["life", "shop"],
        "kind": "atomic",
    },
    "web_browse": {
        "worker": "NAVIGATOR",
        "desc": "Open/search web in Edge + light page sense",
        "tags": ["life", "web"],
        "kind": "atomic",
    },
    "reservation": {
        "worker": "NAVIGATOR",
        "desc": "Restaurant reservation drive (OpenTable) — you confirm",
        "tags": ["life", "dining"],
        "kind": "atomic",
    },
    "web_search": {
        "worker": "SCRUTATOR",
        "desc": "Host web search (DDG/Brave multi-backend) without leaving POCKET",
        "tags": ["web", "research"],
        "kind": "atomic",
    },
    "web_fetch": {
        "worker": "SCRUTATOR",
        "desc": "Fetch a URL and return cleaned text",
        "tags": ["web", "research"],
        "kind": "atomic",
    },
    "integrations_list": {
        "worker": "ARCHON",
        "desc": "54 life integrations catalog (Discord, OpenTable, DoorDash…)",
        "tags": ["integrations", "life"],
        "kind": "atomic",
    },
    "loomgraph_run": {
        "worker": "ARCHON",
        "desc": "LOOMGRAPH — run loop-orchestrated multi-agent graph (default harness)",
        "tags": ["loomgraph", "harness", "graph", "loop", "orchestrate"],
        "kind": "composite",
    },
    "loomgraph_catalog": {
        "worker": "ARCHON",
        "desc": "LOOMGRAPH playbook graphs catalog + mermaid",
        "tags": ["loomgraph", "graph"],
        "kind": "atomic",
    },
    "loomgraph_mermaid": {
        "worker": "ARCHON",
        "desc": "LOOMGRAPH mermaid diagram for a playbook graph",
        "tags": ["loomgraph", "graph", "mermaid"],
        "kind": "atomic",
    },
    "loomgraph_status": {
        "worker": "ARCHON",
        "desc": "LOOMGRAPH live runs + recent receipts",
        "tags": ["loomgraph", "harness"],
        "kind": "atomic",
    },
    "integrations_execute": {
        "worker": "ARCHON",
        "desc": "Execute any integration for real (Discord desktop, Edge SaaS, board)",
        "tags": ["integrations", "life", "desktop", "discord"],
        "kind": "atomic",
    },
    "integrations_readiness": {
        "worker": "ARCHON",
        "desc": "Per-integration executable readiness (desktop installed? url? board?)",
        "tags": ["integrations", "health"],
        "kind": "atomic",
    },
    "assist_route": {
        "worker": "ARCHON",
        "desc": "Route a request to the right digital-assistant engine",
        "tags": ["assist", "life"],
        "kind": "atomic",
    },
    "list_skills": {
        "worker": "ARCHON",
        "desc": "Full skill suite for agents (platform + life + host)",
        "tags": ["platform", "discover"],
        "kind": "atomic",
    },
    "wsl_status": {
        "worker": "ARCHON",
        "desc": "WSL / Linux distro status for integrated console",
        "tags": ["console", "wsl"],
        "kind": "atomic",
    },
    "auro_status": {
        "worker": "ARCHON",
        "desc": "Local Auro meaning model status",
        "tags": ["auro", "model"],
        "kind": "atomic",
    },
    "muse_status": {
        "worker": "ARCHON",
        "desc": "Muse Spark multimodal assist surface",
        "tags": ["muse", "assist"],
        "kind": "atomic",
    },
    "tools_for_prompt": {
        "worker": "ARCHON",
        "desc": "Plan which host tools match a natural-language prompt",
        "tags": ["platform", "tools"],
        "kind": "atomic",
    },
    # --- PROTO-CAPSULE-WASM-009 · Multi-Sandbox + WebGPU ---
    "capsule_status": {
        "worker": "ARCHON",
        "desc": "Multi-sandbox capsule protocol status (PROTO-CAPSULE-WASM-009)",
        "tags": ["capsule", "sandbox", "wasm"],
        "kind": "atomic",
    },
    "capsule_allocate": {
        "worker": "ARCHON",
        "desc": "Allocate isolated capsule (tier 256/512/1024MB, optional WebGPU)",
        "tags": ["capsule", "sandbox"],
        "kind": "atomic",
    },
    "capsule_execute": {
        "worker": "ARCHON",
        "desc": "Execute command inside a capsule (HostWorker / WASI)",
        "tags": ["capsule", "sandbox"],
        "kind": "atomic",
    },
    "capsule_commit": {
        "worker": "ARCHON",
        "desc": "Commit capsule OverlayFS → ChangeSet merge",
        "tags": ["capsule", "sandbox"],
        "kind": "atomic",
    },
    "capsule_terminate": {
        "worker": "ARCHON",
        "desc": "Terminate capsule and release memory reservation",
        "tags": ["capsule", "sandbox"],
        "kind": "atomic",
    },
    "capsule_list": {
        "worker": "ARCHON",
        "desc": "List live multi-sandbox capsules",
        "tags": ["capsule", "sandbox"],
        "kind": "atomic",
    },
    "webgpu_probe": {
        "worker": "ARCHON",
        "desc": "Host WebGPU/GPU adapter probe + acceleration doctrine",
        "tags": ["webgpu", "gpu", "capsule"],
        "kind": "atomic",
    },
    # --- Product Studio first-class (agents) ---
    "studio_map": {
        "worker": "STUDIO",
        "desc": "First-class Product Studio map for agents (features + playbooks)",
        "tags": ["studio", "discover"],
        "kind": "atomic",
    },
    "studio_status": {
        "worker": "STUDIO",
        "desc": "Studio health: ffmpeg, recordings, exports, surfaces",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "studio_open": {
        "worker": "STUDIO",
        "desc": "Studio URLs for desk / phone / LAN",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "studio_playbooks": {
        "worker": "STUDIO",
        "desc": "Agent playbooks: viral ship, record+polish, storyboard, caption",
        "tags": ["studio", "agents"],
        "kind": "atomic",
    },
    "studio_storyboard": {
        "worker": "STUDIO",
        "desc": "Plan hook→proof→CTA demo beats agents can execute",
        "tags": ["studio", "agents"],
        "kind": "atomic",
    },
    "studio_caption": {
        "worker": "STUDIO",
        "desc": "Launch blurb + social posts for demo exports",
        "tags": ["studio", "marketing"],
        "kind": "atomic",
    },
    "studio_list_recordings": {
        "worker": "STUDIO",
        "desc": "List host recordings in ~/.pocket/recordings",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "studio_list_exports": {
        "worker": "STUDIO",
        "desc": "List polished studio exports",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "studio_presets": {
        "worker": "STUDIO",
        "desc": "Viral presets (rotato_phone, x_screencast, macbook_web…)",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "studio_record_start": {
        "worker": "SPECULUM",
        "desc": "Start full-desktop record for studio polish",
        "tags": ["studio", "record"],
        "kind": "atomic",
    },
    "studio_record_stop": {
        "worker": "SPECULUM",
        "desc": "Stop record and save mp4",
        "tags": ["studio", "record"],
        "kind": "atomic",
    },
    "studio_render": {
        "worker": "STUDIO",
        "desc": "Render one preset from recording",
        "tags": ["studio", "export"],
        "kind": "atomic",
    },
    "studio_viral": {
        "worker": "STUDIO",
        "desc": "Viral pack: phone remake + web + screencast",
        "tags": ["studio", "export"],
        "kind": "atomic",
    },
    "studio_batch": {
        "worker": "STUDIO",
        "desc": "Multi-preset batch render",
        "tags": ["studio", "export"],
        "kind": "atomic",
    },
    "studio_ship": {
        "worker": "STUDIO",
        "desc": "End-to-end ship: viral pack + caption + next steps",
        "tags": ["studio", "ship"],
        "kind": "atomic",
    },
    "studio_full_loop": {
        "worker": "STUDIO",
        "desc": "One intent: record and ship / stop and ship full demo loop",
        "tags": ["studio", "ship", "agents"],
        "kind": "playbook",
    },
    "lab_status": {
        "worker": "ARCHON",
        "desc": "Lab readiness: host · studio · capsules · life · phone",
        "tags": ["lab", "platform"],
        "kind": "atomic",
    },
    "voice_status": {
        "worker": "ARCHON",
        "desc": "Aria voice product status · skills · API",
        "tags": ["voice", "aria"],
        "kind": "atomic",
    },
    "voice_turn": {
        "worker": "ARCHON",
        "desc": "Run one Aria product turn (skills + host actions + speak)",
        "tags": ["voice", "aria"],
        "kind": "atomic",
    },
    "studio_auto": {
        "worker": "STUDIO",
        "desc": "Alias studio_viral — polish latest recording",
        "tags": ["studio", "export"],
        "kind": "atomic",
    },
    "viral_pack": {
        "worker": "STUDIO",
        "desc": "Alias studio_viral",
        "tags": ["studio"],
        "kind": "atomic",
    },
    "imagine_compose": {
        "worker": "STUDIO",
        "desc": "Compose device still (rotato phone / macbook web)",
        "tags": ["studio", "imagine"],
        "kind": "atomic",
    },
    "imagine_status": {
        "worker": "STUDIO",
        "desc": "Imagine Studio status + UI path",
        "tags": ["studio", "imagine"],
        "kind": "atomic",
    },
    "imagine_gallery": {
        "worker": "STUDIO",
        "desc": "List Imagine stills and fusion remakes",
        "tags": ["studio", "imagine"],
        "kind": "atomic",
    },
    "foundations_map": {
        "worker": "ARCHON",
        "desc": "Internal AI/math/self/intelligence foundations catalog",
        "tags": ["platform", "models", "math", "internal"],
        "kind": "atomic",
    },
    "bots_list": {
        "worker": "ARCHON",
        "desc": "List POCKET Bots teammates",
        "tags": ["bots", "agents"],
        "kind": "atomic",
    },
    "bots_hire": {
        "worker": "ARCHON",
        "desc": "Hire a Pocket bot from a plain-language job",
        "tags": ["bots", "agents"],
        "kind": "atomic",
    },
    "bots_message": {
        "worker": "ARCHON",
        "desc": "Message a Pocket bot like a colleague",
        "tags": ["bots", "agents"],
        "kind": "atomic",
    },
    "neuro_think": {
        "worker": "ARCHON",
        "desc": "Spherical neuro pass for Grok/Claude/Codex/Spark/Auro",
        "tags": ["neuro", "engines"],
        "kind": "atomic",
    },
}


def surfaces() -> List[Dict[str, Any]]:
    return list(SURFACES)


def platform_skills() -> List[Dict[str, Any]]:
    return [{"id": k, **v} for k, v in PLATFORM_SKILLS.items()]


def coherent() -> Dict[str, Any]:
    """Single discover payload for agents + desk."""
    health = {}
    try:
        from pocket.platform_api import health_domains

        health = health_domains()
    except Exception as e:
        health = {"ok": False, "error": str(e)[:120]}

    # Enrich fusion/phone in health
    try:
        from pocket.conversational_fusion import schema as cf_schema

        health.setdefault("domains", {})["conversational_fusion"] = {
            "ok": True,
            **{k: cf_schema().get(k) for k in ("version", "industry", "fusion_schema")},
        }
    except Exception as e:
        health.setdefault("domains", {})["conversational_fusion"] = {"ok": False, "error": str(e)[:80]}

    try:
        from pocket.node_transfer import hello

        h = hello()
        health.setdefault("domains", {})["phone_pair"] = {
            "ok": True,
            "node_id": h.get("node_id"),
            "label": h.get("label"),
        }
    except Exception as e:
        health.setdefault("domains", {})["phone_pair"] = {"ok": False, "error": str(e)[:80]}

    return {
        "ok": True,
        "schema": "pocket.platform_coherent.v1",
        "product": PRODUCT,
        "version": __version__,
        "tagline": TAGLINE,
        "doctrine": (
            "One host co-pilot. Habitat + Chat + Screen + Workspace + Working + "
            "Phone + Voice Fusion + MCP/CLI. Agents use skills; users stay in POCKET shell."
        ),
        "flow": FLOW,
        "surfaces": SURFACES,
        "skills": platform_skills(),
        "skill_count": len(PLATFORM_SKILLS),
        "find": {
            "desk": "/desk",
            "phone": "/phone",
            "os": "/os",
            "studio": "/studio",
            "voice_studio": "/studio/voice",
            "api_catalog": "/v1/api",
            "this": "/v1/platform/coherent",
            "skills": "/v1/skills",
            "skills_run": "POST /v1/skills/run",
            "mcp": "/v1/mcp",
            "fusion_voice": "/v1/fusion/voice",
            "habitat": "/v1/habitat",
            "screen": "/v1/screen",
            "work": "/v1/work",
            "novae": "/v1/novae",
            "imagine": "/imagine",
            "foundations": "/v1/foundations",
            "bots": "/bots",
            "login": "/login",
            "signup": "/signup",
        },
        "user_tabs_in_app": [
            "Desk", "Habitat", "Screen", "Agent OS", "Work Studio",
            "Studio", "Imagine", "Voice Studio", "API · MCP", "Curiosities", "Phone", "Browser", "Novae",
        ],
        "agent_entry": [
            "POST /v1/skills/run {skill, prompt, params}",
            "POST /v1/mcp/invoke {server:pocket, tool, …}",
            "GET /v1/platform/coherent",
            "GET /v1/agents/first-class",
        ],
        "health": health,
        "ts": time.time(),
    }


def platform_brief(*, max_chars: int = 1800) -> str:
    """Short system brief for harness / agent prompts."""
    lines = [
        "YOU ARE IN POCKET — host co-pilot agents (not a generic chatbot).",
        "POCKET platform (coherent):",
        "· Habitat = agents live (GET/POST /v1/habitat; skill habitat_*)",
        "· Screen = View/Control + VComp (skill screen_* / vcomp_open)",
        "· Aria/Working = first-class voice on desk + phone (skill fusion_voice, work_*)",
        "· Voice Studio = /studio/voice — canvas FFT, persona×mindset, code snap",
        "· OUR remote browser must BEAT theirs — skill remote_browser_benchmark",
        "· Phone + home IoT — pair + /v1/iot + HZ mesh (skill iot_status)",
        "· Remote always — tunnel pocket.medinatechlabs.net + LAN",
        "· OUR computing clouds — host+deploys+Auro+NEXUS+mesh+Forge+MESIE+Engine (skill computing_clouds)",
        "· Cloud models = our perimeter when work runs here (not Connected-Apps vendor)",
        "· Fusion voice = DFW multi-domain routing (POST /v1/fusion/voice)",
        "· Life ops: food_order · flight_search · shop_search · web_browse · reservation (never auto-pay)",
        "· Capsules: multi-sandbox + WebGPU (skill capsule_* / webgpu_probe)",
        "· Product Studio FIRST-CLASS: studio_map · studio_viral · studio_ship · /studio",
        "· LOOMGRAPH: skill loomgraph_run · /loomgraph · POST /v1/loomgraph/run",
        "· KEEP / ISOLATE / RECALL / POCKET MAIL — continuity + mail skills",
        "· 11 major protocols: mesh · mcp-colony · bearer-session · job-session · phone-pair · voice-fusion · loomgraph · capsule · host-os · hz-mesh · rah",
        "· RAH AUTO: host auto-runs Recursive Agent Harnesses on large independent parallel work (user need not say RAH). skill rah_run · POST /v1/rah/run · POCKET_RAH_AUTO=1",
        "· Economy: operator + seat wallets, digital twin wallets per agent, escrow, clearing receipts, Parallax paper bridge — GET /v1/economy · skill economy_map",
        "· Protocols API: GET /v1/protocols · /v1/protocols/status · skill protocols_map · protocols_status",
        "· Identity: GET /v1/identity — every agent knows it is POCKET",
        "· GO = live active states + 100 workflow slots (skill go / go_state · POST /v1/go · GET /v1/go)",
        "· Power = do a goal on this host (skill power_do · POST /v1/power/do · UI /power)",
        "· 200 MCP pack tools (60 universal) · 100 multi-workflows · Platform UI /os uses those APIs",
        "· Discover: skill platform_map / list_skills or GET /v1/platform/coherent · /v1/sovereign",
        "· Run skills: POST /v1/skills/run — enrich_prompt injects identity+tools for ALL agents",
        "· NOVAE: Grok Novae + Codex Novae hands live in POCKET (skill novae_activate · /v1/novae)",
        "· IMAGINE: /imagine · skill imagine_compose (rotato_phone / macbook_web / clean) — host screenshot, not DALL·E",
        "· FOUNDATIONS: internal math/self/world/Auro (GET /v1/foundations) — no third-party AI required",
        "· Help users operate POCKET (desk, phone, Platform, Power, GO, sessions, skills).",
    ]
    text = "\n".join(lines)
    return text[:max_chars]


def find_feature(query: str) -> Dict[str, Any]:
    q = (query or "").lower().strip()
    hits = []
    for s in SURFACES:
        blob = " ".join(
            [
                s["id"],
                s["name"],
                s["where"],
                s["for"],
                " ".join(s.get("skills") or []),
                " ".join(s.get("api") or []),
            ]
        ).lower()
        if not q or q in blob or any(tok in blob for tok in q.split()):
            hits.append(s)
    skill_hits = []
    for sid, meta in PLATFORM_SKILLS.items():
        blob = f"{sid} {meta.get('desc','')} {' '.join(meta.get('tags') or [])}".lower()
        if not q or q in blob or any(tok in blob for tok in q.split()):
            skill_hits.append({"id": sid, **meta})
    return {
        "ok": True,
        "query": query,
        "surfaces": hits[:12],
        "skills": skill_hits[:20],
        "hint": "Use POST /v1/skills/run with skill id, or open surface where listed",
    }


def run_platform_skill(
    skill_id: str,
    *,
    prompt: str = "",
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a platform skill; returns structured result."""
    sid = (skill_id or "").strip().lower().replace("-", "_")
    params = params or {}
    p = prompt or params.get("text") or params.get("prompt") or ""

    if sid in ("platform_map", "platform", "coherent", "where_is_everything"):
        return coherent()

    if sid in ("platform_health", "platform_ready"):
        from pocket.platform_api import health_domains

        return health_domains()

    if sid in ("novae_list", "novae", "nova", "novae_status"):
        from pocket.novae import list_novae

        items = list_novae()
        return {"ok": True, "novae": items, "count": len(items)}

    if sid in ("novae_activate", "activate_novae", "nova_activate"):
        from pocket.novae import activate

        nid = str(params.get("id") or params.get("novae") or p or "GROK_NOVAE")
        return activate(nid, goal=str(params.get("goal") or p or "platform activate"))

    if sid in ("foundations_map", "foundations", "ai_foundations", "internal_foundations"):
        from pocket.foundations import catalog as foundations_catalog

        return foundations_catalog()

    if sid in ("bots_list", "bots", "pocket_bots"):
        from pocket.bots import catalog as bots_catalog

        return bots_catalog()

    if sid in ("bots_hire", "hire_bot"):
        from pocket.bots import create_from_prompt

        return create_from_prompt(p or params.get("job") or params.get("prompt") or "")

    if sid in ("bots_message", "message_bot"):
        from pocket.bots import message as bot_message

        return bot_message(str(params.get("id") or params.get("bot") or ""), p or params.get("text") or "")

    if sid in ("neuro_think", "neuro", "sphere", "neuro_sphere"):
        from pocket.neuro_think import think as neuro_think

        return neuro_think(p or params.get("prompt") or "", mode=str(params.get("mode") or "grok"))

    if sid in ("imagine_status", "imagine", "imagine_studio"):
        from pocket.imagine_studio import status as imagine_status

        return imagine_status()

    if sid in ("imagine_gallery", "imagine_stills"):
        from pocket.imagine_studio import gallery as imagine_gallery

        return imagine_gallery(limit=int(params.get("limit") or 24))

    if sid in ("imagine_compose", "imagine_still", "compose_device"):
        from pocket.imagine_studio import compose as imagine_compose

        return imagine_compose(
            mode=str(params.get("mode") or params.get("preset") or "rotato_phone"),
            image=str(params.get("image") or params.get("path") or ""),
            title=str(params.get("title") or "POCKET"),
            subtitle=str(params.get("subtitle") or p or "Host co-pilot"),
            image_b64=str(params.get("image_b64") or ""),
            source=str(params.get("source") or "live"),
        )

    if sid in ("list_agents", "agents_catalog"):
        from pocket.first_class_agents import desk_catalog, summary

        return {"ok": True, "summary": summary(), "desk": desk_catalog()}

    if sid in ("protocols_map", "protocols", "protocol_catalog", "major_protocols"):
        from pocket.protocols.platform_protocols import manifest

        return manifest()

    if sid in ("protocols_status", "protocol_health", "protocols_health"):
        from pocket.protocols.platform_protocols import platform_protocols_status

        return platform_protocols_status()

    if sid in ("pocket_identity", "who_am_i", "identity", "whoami"):
        from pocket.pocket_identity import agent_self_description

        return agent_self_description()

    if sid in ("rah_plan", "rah_preview", "plan_rah"):
        from pocket.rah import plan_fanout, manifest as rah_manifest

        return {
            **plan_fanout(
                p or params.get("task") or params.get("prompt") or "preview",
                max_leaves=int(params.get("max_leaves") or 12),
                hint=str(params.get("hint") or ""),
            ),
            "protocol": rah_manifest().get("protocol"),
        }

    if sid in ("rah_status", "rah_health"):
        from pocket.rah import status as rah_status, list_runs

        return {**rah_status(), "runs": list_runs(limit=12)}

    if sid in ("rah_run", "rah", "recursive_harness", "rah_fanout"):
        from pocket.rah import run_rah, format_result_markdown

        task = p or params.get("task") or params.get("prompt") or ""
        if not task:
            return {"ok": False, "error": "task required for rah_run"}
        run = run_rah(
            task,
            max_leaves=int(params.get("max_leaves") or 8),
            max_parallel=params.get("max_parallel"),
            max_depth=params.get("max_depth") or 2,
            verify=params.get("verify", True) is not False,
            hint=str(params.get("hint") or ""),
            cwd=str(params.get("cwd") or ""),
            session_id=str(params.get("session_id") or ""),
        )
        return {
            "ok": run.get("ok"),
            "run_id": run.get("run_id"),
            "completed": run.get("completed"),
            "failed": run.get("failed"),
            "duration_sec": run.get("duration_sec"),
            "artifact_root": run.get("artifact_root"),
            "synthesis": format_result_markdown(run)[:12000],
            "cost_note": run.get("cost_note"),
            "protocol": run.get("protocol"),
        }

    if sid in ("internal_models", "list_internal_models", "model_modules"):
        from pocket.internal_models import list_models, pick_for_goal

        return {
            "ok": True,
            "schema": "pocket.internal_models.v1",
            "models": list_models(),
            "pick": pick_for_goal(p or params.get("goal") or "general", limit=4),
            "doctrine": "Internal models are modules; genetic flow evolves which ones execute.",
        }

    if sid in ("genetic_status", "genetic_flow_status", "gene_status"):
        from pocket.internal_models import list_models, list_runs

        return {
            "ok": True,
            "schema": "pocket.genetic_flow.status.v1",
            "models": list_models(),
            "runs": list_runs(limit=12),
        }

    if sid in ("genetic_flow", "genetic", "gene_flow", "run_genetic", "eugenetic"):
        from pocket.internal_models import run_genetic_flow

        task = p or params.get("task") or params.get("prompt") or params.get("goal") or ""
        if not task:
            return {"ok": False, "error": "goal required for genetic_flow"}
        models = params.get("models")
        if isinstance(models, str):
            models = [m.strip() for m in models.split(",") if m.strip()]
        run = run_genetic_flow(
            task,
            generations=int(params.get("generations") or params.get("gens") or 3),
            population=int(params.get("population") or params.get("pop") or 6),
            models=models,
            cwd=str(params.get("cwd") or ""),
        )
        return {
            "ok": run.get("ok"),
            "run_id": run.get("run_id"),
            "fitness": run.get("fitness"),
            "elapsed_ms": run.get("elapsed_ms"),
            "best_models": ((run.get("best") or {}).get("genes") or {}).get("models"),
            "markdown": (run.get("markdown") or "")[:14000],
            "history": run.get("history"),
            "path": run.get("path"),
            "engine": "genetic-flow",
        }

    if sid in ("express_model", "express_internal", "run_internal_model"):
        from pocket.internal_models import express_one, list_models

        mid = str(params.get("model") or params.get("model_id") or params.get("id") or "").strip()
        if not mid:
            return {"ok": False, "error": "model id required", "models": [m["id"] for m in list_models()]}
        goal = p or params.get("goal") or params.get("prompt") or ""
        res = express_one(mid, goal)
        return res.as_dict() if hasattr(res, "as_dict") else res

    if sid in ("economy_map", "economy", "wallets", "economic_domain"):
        from pocket.economy import snapshot

        return snapshot()

    if sid in ("economy_twins", "twin_wallets", "digital_twins"):
        from pocket.economy import list_twins

        return list_twins()

    if sid in ("billing_status", "revenuecat", "billing"):
        from pocket.revenuecat import status as rc_status

        return rc_status()

    if sid in ("billing_sync", "revenuecat_sync"):
        from pocket.revenuecat import apply_subscriber

        uid = str(params.get("app_user_id") or params.get("user") or p or "").strip()
        if not uid:
            return {"ok": False, "error": "app_user_id required"}
        return apply_subscriber(uid, source="skill")

    if sid == "find_feature":
        return find_feature(p or params.get("query") or "")

    if sid in ("habitat_status", "habitat"):
        from pocket.agent_habitat import status

        return status()

    if sid == "habitat_open":
        from pocket.agent_habitat import set_open

        open_flag = params.get("open")
        if open_flag is None:
            open_flag = True
        return set_open(bool(open_flag))

    if sid == "habitat_pulse":
        from pocket.agent_habitat import pulse

        return pulse(
            agent_id=params.get("agent") or params.get("id") or params.get("agent_id") or "aria",
            status=params.get("status") or "working",
            line=p or params.get("line") or "Pulsed from skill",
        )

    if sid == "habitat_assign":
        from pocket.agent_habitat import assign

        return assign(
            agent_id=params.get("agent") or params.get("id") or params.get("agent_id") or "aria",
            task=p or params.get("task") or "Assigned task",
        )

    if sid in ("screen_status", "screen"):
        from pocket.screen_share import status

        return status()

    if sid in ("screen_view", "screen_control", "screen_off"):
        from pocket.screen_share import set_share

        mode = "view" if sid == "screen_view" else ("control" if sid == "screen_control" else "off")
        return set_share(mode=mode, vcomp=params.get("vcomp"))

    if sid in ("screen_sense", "fusion_screen"):
        from pocket.screen_share import fusion_context

        return fusion_context(agent=params.get("agent") or "skill")

    if sid == "vcomp_open":
        from pocket.virtual_computer import open_computer

        return open_computer(label=params.get("label") or "skill")

    if sid in ("work_status", "work"):
        from pocket.work_mode import status

        return status(params.get("session_id") or "")

    if sid == "work_start":
        from pocket.work_mode import start_work

        return start_work(
            session_id=params.get("session_id") or "",
            voice=params.get("voice", True) is not False,
            screen=params.get("screen") or "control",
            chrome=params.get("chrome", True) is not False,
            goal=p or params.get("goal") or "",
        )

    if sid == "work_package":
        from pocket.work_mode import package_session

        return package_session(params.get("session_id") or params.get("id") or "")

    if sid == "work_handoff":
        from pocket.work_mode import handoff_artifacts

        return handoff_artifacts(
            params.get("session_id") or params.get("id") or "",
            kinds=params.get("kinds") or ["html", "md", "pixel"],
        )

    if sid in ("fusion_schema", "fusion_voice_schema"):
        from pocket.conversational_fusion import schema

        return schema()

    if sid in ("fusion_voice", "conversational_fusion", "fuse_voice"):
        from pocket.conversational_fusion import fuse, remember

        body = dict(params)
        if p and not body.get("text") and not body.get("transcript"):
            body["text"] = p
        r = fuse(body)
        sid_s = str(body.get("session_id") or r.get("session_id") or "")
        if sid_s:
            remember(sid_s, r)
        return r

    if sid == "fusion_last":
        from pocket.conversational_fusion import last

        return {"ok": True, "fusion": last(params.get("session_id") or "")}

    if sid == "voice_skills_list":
        from pocket.voice_skills import list_skills

        return {"ok": True, "skills": list_skills()}

    if sid in ("aria_turn", "voice_skill"):
        from pocket.voice_skills import try_skill
        from pocket.conversational_fusion import fuse

        sk = try_skill(p) if p else None
        fusion = fuse({"text": p, "stress": 0.4, "session_id": params.get("session_id") or "skill"})
        return {
            "ok": True,
            "skill_reply": sk[0] if sk else None,
            "skill_id": sk[1] if sk else None,
            "fusion": {
                "primary_expert": fusion.get("primary_expert"),
                "pattern": fusion.get("pattern"),
                "patience_delta_ms": fusion.get("patience_delta_ms"),
                "prompt_boost": fusion.get("prompt_boost"),
            },
        }

    if sid == "phone_surface":
        from pocket.live import lan_ip

        ip = lan_ip()
        return {
            "ok": True,
            "phone": "/phone",
            "local": "http://127.0.0.1:8787/phone",
            "lan": f"http://{ip}:8787/phone" if ip else None,
            "pair": "Desk Workspace → Get pair code → phone More → Pair",
            "skills": ["pair_mint", "pair_status", "fusion_voice", "work_start"],
            "first_class_voice": ["voice", "work"],
        }

    if sid == "pair_mint":
        from pocket.node_transfer import mint_pair_code

        return mint_pair_code(label=params.get("label") or "phone", ttl_sec=int(params.get("ttl_sec") or 900))

    if sid == "pair_status":
        from pocket.node_transfer import status, hello

        return {"ok": True, "hello": hello(), "status": status()}

    if sid == "mcp_catalog":
        from pocket.mcp_bundle import catalog

        return catalog()

    if sid == "mcp_invoke":
        from pocket.mcp_bundle import invoke

        return invoke(
            params.get("server") or "pocket",
            params.get("tool") or "screen_status",
            **{k: v for k, v in params.items() if k not in ("server", "tool")},
        )

    if sid == "cli_list":
        from pocket.cli_tools import inventory

        return inventory()

    if sid == "cli_run":
        from pocket.cli_tools import run_cli

        return run_cli(
            params.get("bin") or params.get("command") or "gh",
            params.get("args") or [],
            timeout=int(params.get("timeout") or 60),
        )

    if sid in ("voice_studio_open", "voice_studio", "v2v_studio"):
        from pocket.live import lan_ip

        ip = lan_ip()
        return {
            "ok": True,
            "skill": "voice_studio_open",
            "url": "/studio/voice",
            "local": "http://127.0.0.1:8787/studio/voice",
            "lan": f"http://{ip}:8787/studio/voice" if ip else None,
            "desk_tab": "Voice Studio",
            "implements": {
                "canvas_fft_5_styles": True,
                "persona_x_mindset": True,
                "code_to_voice_snap": True,
                "fusion_voice": True,
                "pocket_voice_patient_vad": True,
                "native_multimodal_sub_140ms": False,
                "note": "Sub-140ms RTT requires native multimodal duplex engine; studio measures cascade turn RTT and ships multi-sensory UI today.",
            },
            "stack": {
                "ui": "pocket.voice_studio_ui",
                "audio_oss": "pocket-voice-to-text",
                "fusion": "pocket.conversational_fusion",
                "sessions": "POST /v1/sessions mode=voice",
            },
            "paper": "Ultra-Low-Latency Multi-Sensory Voice-to-Voice Agent Studio",
        }

    if sid in ("sovereign_stack", "sovereign"):
        from pocket.sovereign_stack import stack_status

        return stack_status()

    if sid in ("computing_clouds", "our_clouds", "clouds"):
        from pocket.sovereign_stack import computing_clouds

        return computing_clouds()

    if sid in ("remote_browser_status", "remote_browser"):
        from pocket.remote_browser import status as rb_status

        return rb_status()

    if sid == "remote_browser_open":
        from pocket.remote_browser import open_url

        return open_url(p or params.get("url") or "https://example.com")

    if sid == "remote_browser_sense":
        from pocket.remote_browser import sense

        return sense(max_ui=int(params.get("max_ui") or 400))

    if sid in ("remote_browser_benchmark", "browser_benchmark"):
        from pocket.remote_browser import run_benchmarks

        return run_benchmarks()

    if sid in ("iot_status", "iot_home"):
        from pocket.iot_home import status as iot_status

        return iot_status()

    if sid == "iot_list":
        from pocket.iot_home import list_devices

        return list_devices()

    if sid == "iot_register":
        from pocket.iot_home import register_device

        return register_device(
            name=params.get("name") or p or "device",
            kind=params.get("kind") or "generic",
            address=params.get("address") or "",
            room=params.get("room") or "",
            protocol=params.get("protocol") or "lan",
        )

    if sid == "iot_phone":
        from pocket.iot_home import phone_bridge

        return phone_bridge()

    if sid in ("iot_hz_status", "hz_status"):
        from pocket.iot_home import hz_status

        return hz_status()

    # --- Everyday life skills (food · flights · shop · web · reserve) ---
    try:
        from pocket.life_ops import is_life_skill, run_life_skill

        if is_life_skill(sid):
            open_browser = params.get("open_browser")
            if open_browser is None:
                open_browser = params.get("open", True) is not False
            return run_life_skill(
                sid,
                prompt=p,
                params=params,
                open_browser=bool(open_browser),
            )
    except Exception as e:
        if sid.startswith("life") or sid in (
            "food_order",
            "flight_search",
            "shop_search",
            "web_browse",
            "reservation",
        ):
            return {"ok": False, "error": f"life skill error: {e}", "skill": sid}

    if sid in ("web_search", "lookup_web", "search_web"):
        from pocket.web_research import search_web

        q = p or params.get("query") or params.get("q") or ""
        return search_web(q, max_results=int(params.get("max_results") or params.get("n") or 6))

    if sid in ("web_fetch", "fetch_url"):
        from pocket.web_research import fetch_url

        url = p or params.get("url") or ""
        return fetch_url(url, max_chars=int(params.get("max_chars") or 14000))

    if sid in ("integrations_list", "integrations", "integrations_catalog"):
        from pocket.integrations_catalog import catalog

        return catalog()

    if sid in (
        "loomgraph_run",
        "loomgraph",
        "run_loomgraph",
        "graph_loop",
        "orchestrate_graph",
    ):
        from pocket.loomgraph import format_run_markdown, run as loomgraph_run

        gid = params.get("graph_id") or params.get("graph") or params.get("playbook") or ""
        r = loomgraph_run(
            p or params.get("goal") or params.get("text") or "",
            graph_id=str(gid or ""),
            max_loops=int(params.get("max_loops") or 3),
            dry_run=bool(params.get("dry_run")),
            author=str(params.get("author") or ""),
            mode=str(params.get("mode") or ""),
            force_share=bool(params.get("force_share") or params.get("share")),
            integration_id=str(params.get("integration_id") or params.get("integration") or ""),
        )
        r["markdown"] = format_run_markdown(r)
        return r

    if sid in ("loomgraph_catalog", "loomgraph_graphs", "list_loomgraph"):
        from pocket.loomgraph import catalog as loomgraph_catalog

        return loomgraph_catalog()

    if sid in ("loomgraph_mermaid", "loomgraph_diagram"):
        from pocket.loomgraph import get_graph, to_mermaid

        gid = params.get("graph_id") or params.get("graph") or p or "default"
        g = get_graph(str(gid))
        return {
            "ok": True,
            "graph_id": (g.get("graph") or {}).get("id"),
            "mermaid": to_mermaid(g),
            "ascii": __import__("pocket.loomgraph", fromlist=["to_ascii"]).to_ascii(g),
        }

    if sid in ("loomgraph_status", "loomgraph_live", "loomgraph_runs"):
        from pocket.loomgraph import live, list_runs, catalog as loomgraph_catalog

        return {
            "ok": True,
            "catalog": loomgraph_catalog(),
            "live": live(),
            "runs": list_runs(limit=int(params.get("limit") or 15)),
        }

    if sid in (
        "integrations_execute",
        "integration_execute",
        "integration_run",
        "run_integration",
        "open_integration",
        "discord",
        "open_discord",
    ):
        from pocket.integrations_exec import execute as integration_execute

        iid = (
            params.get("id")
            or params.get("integration")
            or params.get("name")
            or params.get("app")
            or ""
        )
        if not iid and sid in ("discord", "open_discord"):
            iid = "discord"
        if not iid and p:
            # allow "discord", "open slack", free text
            pl = p.strip().lower()
            if pl in ("discord", "slack", "teams", "spotify", "zoom", "github", "notion"):
                iid = pl
            elif pl.startswith("open "):
                iid = pl[5:].strip().split()[0] if pl[5:].strip() else ""
            else:
                iid = pl.split()[0] if pl else ""
        return integration_execute(
            iid,
            text=p or params.get("text") or params.get("prompt") or "",
            dry_run=bool(params.get("dry_run")),
            prefer=str(params.get("prefer") or "auto"),
            open_browser=bool(params.get("open_browser", True)),
            open_desktop=bool(params.get("open_desktop", True)),
        )

    if sid in (
        "integrations_readiness",
        "integrations_status",
        "integrations_smoke",
        "integrations_execute_all",
    ):
        from pocket.integrations_exec import execute_all, readiness

        if sid in ("integrations_execute_all", "integrations_smoke") or params.get("execute_all"):
            return execute_all(
                dry_run=bool(params.get("dry_run", True)),
                only=params.get("only") or params.get("ids"),
            )
        return readiness()

    if sid in ("assist_route", "digital_assist", "assistant_route"):
        from pocket.digital_assistant import route_intent

        engine = route_intent(p)
        return {
            "ok": True,
            "skill": "assist_route",
            "engine": engine,
            "prompt": (p or "")[:200],
            "hint": "Run via Work Studio / assist mode or Working board for life ops",
        }

    if sid in ("list_skills", "skills_list", "skill_suite"):
        try:
            from pocket.skill_suite import all_skills, skill_count

            skills = all_skills()
            return {
                "ok": True,
                "skill": "list_skills",
                "count": skill_count(),
                "skills": [
                    {"id": s["id"], "worker": s.get("worker"), "desc": s.get("desc"), "tags": s.get("tags")}
                    for s in skills[:200]
                ],
                "truncated": len(skills) > 200,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)[:160]}

    if sid in ("wsl_status", "linux_status"):
        from pocket.wsl_agent import status as wsl_status

        return wsl_status()

    if sid in ("auro_status", "auro"):
        from pocket.auro14b_bridge import status as auro_status

        return auro_status()

    if sid in ("muse_status", "muse_spark"):
        return {
            "ok": True,
            "skill": "muse_status",
            "engine": "muse_spark",
            "desk": "Chat agent Muse / Assist",
            "hint": "Say muse or use mode muse_spark — multimodal plan + web + screen",
            "api": "POST /v1/jobs mode=muse_spark",
        }

    if sid in ("tools_for_prompt", "plan_tools"):
        from pocket.agent_tools_loop import plan_tools

        planned = plan_tools(p, mode=str(params.get("mode") or ""), limit=int(params.get("limit") or 6))
        return {"ok": True, "skill": "tools_for_prompt", "planned": planned, "prompt": (p or "")[:200]}

    if sid in ("multi_plan", "multiplan", "plan_exec", "agentic_plan", "task_plan"):
        from pocket.multi_plan import run_multi_plan

        r = run_multi_plan(
            p or params.get("goal") or params.get("text") or "",
            job_id=str(params.get("job_id") or ""),
            session_id=str(params.get("session_id") or ""),
            max_tasks=int(params.get("max_tasks") or 24),
        )
        r["skill"] = "multi_plan"
        return r

    if sid in ("mcp_stream", "mcp_rpc_stream", "protocol_stream", "jsonrpc_stream"):
        from pocket.mcp_stream import list_frames, snapshot, format_term_view, clear as mcp_clear

        action = str(params.get("action") or params.get("mode") or "").lower()
        if action in ("clear", "reset"):
            r = mcp_clear()
            r["skill"] = "mcp_stream"
            return r
        after = int(params.get("after") or params.get("seq") or 0)
        limit = int(params.get("limit") or 50)
        fmt = str(params.get("format") or params.get("fmt") or "json").lower()
        if fmt in ("term", "markdown", "md") or (p and ("term" in p.lower() or "markdown" in p.lower())):
            return {
                "ok": True,
                "skill": "mcp_stream",
                "format": "term",
                "markdown": format_term_view(after_seq=after, limit=limit),
            }
        return {
            "ok": True,
            "skill": "mcp_stream",
            **snapshot(),
            "frames": list_frames(after_seq=after, limit=limit),
        }

    # --- Agent mail + website UI + Python engines (models use these via MCP) ---
    if sid in (
        "mail_status", "mail_accounts", "mail_account_create",
        "mail_inbox", "mail_send", "mail_read", "mail_draft",
        "web_ui_open", "web_ui_sense", "web_ui_act", "web_ui_browse",
        "web_ui_fetch", "web_ui_search", "web_ui_status",
        "python_engine", "python_engines_list",
        "engine_uses", "engine_use",
        "model_build", "model_list_built", "model_register", "model_suggest",
        "build_model", "forge_model",
        "agents_toolkit", "agents_tools", "tools_manifest",
        "mcp_stream", "mcp_rpc_stream", "protocol_stream",
        "call_status", "call_numbers", "call_assign",
        "call_dial", "call_answer", "call_hangup", "call_speak", "call_list",
    ):
        from pocket.mcp_bundle import _invoke_mail_web

        merged = dict(params or {})
        if p:
            merged.setdefault("text", p)
            merged.setdefault("prompt", p)
            # bare prompt with no engine → treat as goal for default engine
            if sid == "python_engine" and not merged.get("engine"):
                merged.setdefault("prompt", p)
            if sid in ("model_build", "build_model", "forge_model") and not merged.get("kind"):
                # free-text build path uses model_forge auto-suggest
                merged.setdefault("description", p)
            if sid == "engine_use" and not merged.get("use") and not merged.get("use_id"):
                # auto-pick use from prompt
                from pocket.web_ui_engine import pick_use, run_use

                pick = pick_use(p)
                best = (pick.get("best") or {}).get("id") or ""
                if best:
                    return run_use(best, p, params=merged)
                return pick
            if sid in ("agents_toolkit", "agents_tools", "tools_manifest"):
                if "md" in p.lower() or "markdown" in p.lower():
                    merged["format"] = "markdown"
                if "write" in p.lower() or "file" in p.lower():
                    merged["format"] = "write"
        return _invoke_mail_web(sid, merged)

    if sid in (
        "agent_invoke",
        "agent_roster",
        "autonomous_status",
        "autonomous_ensure",
        "keep_start",
        "keep_status",
        "keep_stop",
        "kernel_status",
        "kernel_calibrate",
        "kernel_slab",
        "cognitive_loop",
        "workflow_start",
        "workflow_tick",
        "workflow_status",
        "workflow_stop",
    ):
        from pocket.agent_invoke import autonomous_status, ensure_autonomous, invoke, roster

        if sid == "agent_roster":
            return roster()
        if sid == "autonomous_status":
            return autonomous_status()
        if sid == "autonomous_ensure":
            return ensure_autonomous()
        if sid == "kernel_status":
            from pocket.kernels.neuro_silicon import driver_status

            return driver_status()
        if sid == "kernel_calibrate":
            from pocket.kernels.neuro_silicon import calibrate

            return calibrate(run_loop=True, goal=p)
        if sid == "kernel_slab":
            from pocket.kernels.slab import bench_slab, slab_status

            if "bench" in (p or "").lower():
                return bench_slab()
            return slab_status()
        if sid == "cognitive_loop":
            from pocket.kernels.cognitive_loop import run_loop

            return run_loop(p or "cognitive loop")
        if sid == "workflow_start":
            from pocket.kernels.long_workflow import start as wf_start

            return wf_start(
                p or str((params or {}).get("goal") or ""),
                session_id=str((params or {}).get("session_id") or ""),
                interval_sec=float((params or {}).get("interval_sec") or 90),
                max_hours=float((params or {}).get("max_hours") or 168),
                keep=bool((params or {}).get("keep")),
                host_bound=(params or {}).get("host_bound", True) is not False,
            )
        if sid == "workflow_tick":
            from pocket.kernels.long_workflow import tick as wf_tick

            return wf_tick(str((params or {}).get("id") or p))
        if sid == "workflow_status":
            from pocket.kernels.long_workflow import get as wf_get, list_runs

            wid = str((params or {}).get("id") or "").strip()
            return wf_get(wid) if wid else list_runs()
        if sid == "workflow_stop":
            from pocket.kernels.long_workflow import pause, resume, stop as wf_stop

            wid = str((params or {}).get("id") or p)
            act = str((params or {}).get("action") or "stop").lower()
            if act == "pause":
                return pause(wid)
            if act == "resume":
                return resume(wid)
            return wf_stop(wid)
        if sid == "keep_status":
            from pocket.keep_agents import status as ks

            return ks()
        if sid == "keep_stop":
            from pocket.keep_agents import end_chat, stop as kstop

            kid = str((params or {}).get("id") or (params or {}).get("keep_id") or "")
            sid_ = str((params or {}).get("session_id") or "")
            if sid_:
                return end_chat(sid_)
            if kid:
                return kstop(kid)
            return {"ok": False, "error": "id or session_id required"}
        if sid == "keep_start":
            return invoke("keep", prompt=p, session_id=str((params or {}).get("session_id") or ""), params=params)
        return invoke(
            str((params or {}).get("name") or (params or {}).get("agent") or p.split()[0] if p else ""),
            prompt=p if (params or {}).get("name") or (params or {}).get("agent") else " ".join(p.split()[1:]),
            job=str((params or {}).get("job") or (params or {}).get("action") or ""),
            session_id=str((params or {}).get("session_id") or ""),
            params=params,
        )

    # --- Multi-Sandbox Capsule + WebGPU (PROTO-CAPSULE-WASM-009) ---
    try:
        from pocket.protocols.multi_sandbox_capsule import is_capsule_skill, run_capsule_skill

        if is_capsule_skill(sid):
            return run_capsule_skill(sid, prompt=p, params=params)
    except Exception as e:
        if sid.startswith("capsule") or sid.startswith("webgpu"):
            return {"ok": False, "error": f"capsule skill error: {e}", "skill": sid}

    # --- Product Studio first-class ---
    try:
        from pocket.studio_core import is_studio_skill, run_studio_skill

        if is_studio_skill(sid):
            return run_studio_skill(sid, prompt=p, params=params)
    except Exception as e:
        if sid.startswith("studio") or sid in ("viral_pack", "imagine_compose", "storyboard"):
            return {"ok": False, "error": f"studio skill error: {e}", "skill": sid}

    if sid in ("lab_status", "lab", "lab_ready", "lab_hub"):
        from pocket.lab_hub import lab_status

        return lab_status()

    if sid in ("voice_status", "aria_status", "voice_product"):
        from pocket.voice_product import product_status
        from pocket.voice_proxy import ensure_voice

        try:
            ensure_voice(wait_sec=1.0)
        except Exception:
            pass
        return product_status()

    if sid in ("voice_turn", "aria_turn_product", "aria_act"):
        from pocket.voice_product import run_voice_turn

        return run_voice_turn(p, session_id=str(params.get("session_id") or "skill"), job_id="")

    return {
        "ok": False,
        "error": f"unknown platform skill: {sid}",
        "available": list(PLATFORM_SKILLS.keys()),
        "hint": "GET /v1/platform/coherent",
    }


def is_platform_skill(skill_id: str) -> bool:
    sid = (skill_id or "").strip().lower().replace("-", "_")
    if sid in PLATFORM_SKILLS:
        return True
    try:
        from pocket.life_ops import is_life_skill

        if is_life_skill(sid):
            return True
    except Exception:
        pass
    try:
        from pocket.protocols.multi_sandbox_capsule import is_capsule_skill

        if is_capsule_skill(sid):
            return True
    except Exception:
        pass
    try:
        from pocket.studio_core import is_studio_skill

        if is_studio_skill(sid):
            return True
    except Exception:
        pass
    return sid in {
        "platform",
        "coherent",
        "where_is_everything",
        "fusion_screen",
        "conversational_fusion",
        "fuse_voice",
        "voice_skill",
        "agents_catalog",
        "platform_ready",
        "habitat",
        "screen",
        "work",
        "fusion_voice_schema",
        "voice_studio",
        "v2v_studio",
        "sovereign",
        "our_clouds",
        "clouds",
        "remote_browser",
        "browser_benchmark",
        "iot_home",
        "hz_status",
        "lookup_web",
        "search_web",
        "fetch_url",
        "mail_status",
        "mail_accounts",
        "mail_account_create",
        "mail_inbox",
        "mail_send",
        "mail_read",
        "mail_draft",
        "web_ui_open",
        "web_ui_sense",
        "web_ui_act",
        "web_ui_browse",
        "web_ui_fetch",
        "web_ui_search",
        "web_ui_status",
        "python_engine",
        "python_engines_list",
        "integrations",
        "integrations_catalog",
        "integrations_execute",
        "integration_execute",
        "integration_run",
        "run_integration",
        "open_integration",
        "integrations_readiness",
        "integrations_status",
        "integrations_smoke",
        "integrations_execute_all",
        "discord",
        "open_discord",
        "loomgraph",
        "loomgraph_run",
        "run_loomgraph",
        "graph_loop",
        "orchestrate_graph",
        "loomgraph_catalog",
        "loomgraph_graphs",
        "list_loomgraph",
        "loomgraph_mermaid",
        "loomgraph_diagram",
        "loomgraph_status",
        "loomgraph_live",
        "loomgraph_runs",
        "digital_assist",
        "assistant_route",
        "skills_list",
        "skill_suite",
        "linux_status",
        "auro",
        "muse_spark",
        "plan_tools",
        "food",
        "flight",
        "flights",
        "shop",
        "buy",
        "browse",
        "reserve",
        "dining",
        "lab",
        "lab_ready",
        "lab_hub",
        "lab_status",
    }
