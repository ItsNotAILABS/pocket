"""Skills packs for Latin workers — multi-skill agents (not single-job).

Each worker has many skills. Skills are callable by id for demos, API, and ARCHON.
"""

from __future__ import annotations

from typing import Any, Dict, List

# skill_id → definition
SKILLS: Dict[str, Dict[str, Any]] = {
    # Platform coherence (also in skill_suite / platform_coherence)
    "platform_map": {"worker": "ARCHON", "desc": "Full coherent platform map"},
    "novae_list": {"worker": "ARCHON", "desc": "List Nova hands in POCKET"},
    "novae_activate": {"worker": "ARCHON", "desc": "Activate Grok/Codex Novae"},
    "find_feature": {"worker": "ARCHON", "desc": "Find desk/phone/API/skill for a feature"},
    "habitat_status": {"worker": "ARCHON", "desc": "Habitat residents"},
    "habitat_pulse": {"worker": "ARCHON", "desc": "Pulse habitat resident"},
    "screen_sense": {"worker": "OCULUS", "desc": "Screen fusion brief"},
    "work_start": {"worker": "ARCHON", "desc": "Start Working mode"},
    "fusion_voice": {"worker": "ARCHON", "desc": "Conversational Fusion route"},
    "pair_mint": {"worker": "ARCHON", "desc": "Mint phone pair code"},
    "phone_surface": {"worker": "ARCHON", "desc": "Phone URLs + pair help"},
    "mcp_catalog": {"worker": "ARCHON", "desc": "10 MCP catalog"},
    # Everyday life (all agents)
    "life_catalog": {"worker": "ARCHON", "desc": "Everyday life skills catalog"},
    "life_status": {"worker": "ARCHON", "desc": "Working board + life ops status"},
    "life_classify": {"worker": "ARCHON", "desc": "Classify life intent"},
    "food_order": {"worker": "NAVIGATOR", "desc": "Food delivery — you pay"},
    "flight_search": {"worker": "NAVIGATOR", "desc": "Flights — you book"},
    "shop_search": {"worker": "NAVIGATOR", "desc": "Shop — you checkout"},
    "web_browse": {"worker": "NAVIGATOR", "desc": "Browse web in Edge"},
    "reservation": {"worker": "NAVIGATOR", "desc": "Reserve table — you confirm"},
    "web_search": {"worker": "SCRUTATOR", "desc": "Host web search"},
    "web_fetch": {"worker": "SCRUTATOR", "desc": "Fetch URL text"},
    "integrations_list": {"worker": "ARCHON", "desc": "Integrations catalog"},
    "assist_route": {"worker": "ARCHON", "desc": "Digital assistant route"},
    "list_skills": {"worker": "ARCHON", "desc": "Full skill suite"},
    "wsl_status": {"worker": "ARCHON", "desc": "WSL status"},
    "auro_status": {"worker": "ARCHON", "desc": "Auro model status"},
    "internal_models": {"worker": "ARCHON", "desc": "List internal model modules"},
    "genetic_flow": {"worker": "ARCHON", "desc": "Run genetic flow over internal models"},
    "genetic_status": {"worker": "ARCHON", "desc": "Genetic flow status + recent runs"},
    "express_model": {"worker": "ARCHON", "desc": "Express one internal model module"},
    "muse_status": {"worker": "ARCHON", "desc": "Muse Spark status"},
    "iot_status": {"worker": "ARCHON", "desc": "Home IoT status"},
    "tools_for_prompt": {"worker": "ARCHON", "desc": "Plan host tools for a prompt"},
    # Agent mail (our own accounts + inboxes)
    "mail_status": {"worker": "SCRIBE", "desc": "Agent mail + POCKET MAIL status"},
    "mail_accounts": {"worker": "SCRIBE", "desc": "List agent email accounts"},
    "mail_account_create": {"worker": "SCRIBE", "desc": "Create agent email account"},
    "mail_inbox": {"worker": "SCRIBE", "desc": "Read agent inbox"},
    "mail_send": {"worker": "SCRIBE", "desc": "Send agent mail"},
    "mail_read": {"worker": "SCRIBE", "desc": "Read one agent mail"},
    "mail_draft": {"worker": "SCRIBE", "desc": "POCKET MAIL draft"},
    # Website UI + Python engines for models
    "web_ui_open": {"worker": "NAVIGATOR", "desc": "Open website in host browser"},
    "web_ui_sense": {"worker": "NAVIGATOR", "desc": "Sense website UI"},
    "web_ui_act": {"worker": "NAVIGATOR", "desc": "Act on website UI"},
    "web_ui_browse": {"worker": "NAVIGATOR", "desc": "Open + sense website"},
    "web_ui_fetch": {"worker": "SCRUTATOR", "desc": "Fetch URL text"},
    "web_ui_search": {"worker": "SCRUTATOR", "desc": "Web search"},
    "web_ui_status": {"worker": "NAVIGATOR", "desc": "Web UI engine status"},
    "webmcp_scan": {"worker": "NAVIGATOR", "desc": "Diffuse page/app/host into WebMCP action catalog"},
    "webmcp_list": {"worker": "NAVIGATOR", "desc": "List WebMCP actions"},
    "webmcp_use": {"worker": "NAVIGATOR", "desc": "Run a WebMCP catalog action"},
    "webmcp_find": {"worker": "NAVIGATOR", "desc": "Search WebMCP actions"},
    "python_engine": {"worker": "ARCHON", "desc": "Run named Python agent/engine"},
    "python_engines_list": {"worker": "ARCHON", "desc": "List Python engines models can use"},
    "engine_uses": {"worker": "ARCHON", "desc": "20 named uses for web_ui + engines"},
    "engine_use": {"worker": "ARCHON", "desc": "Run one named engine use"},
    "model_build": {"worker": "ARCHON", "desc": "Build and register a platform model"},
    "model_list_built": {"worker": "ARCHON", "desc": "List agent-built models"},
    "model_register": {"worker": "ARCHON", "desc": "Register built models"},
    "model_suggest": {"worker": "ARCHON", "desc": "Suggest model blueprint from goal"},
    "agents_toolkit": {"worker": "ARCHON", "desc": "Full MCP tools + 20 uses + skills manifest for agents"},
    "multi_plan": {"worker": "ARCHON", "desc": "Multi-plan: reason, task list, sub-agents, live terminal in chat"},
    "mcp_stream": {"worker": "ARCHON", "desc": "Live MCP JSON-RPC protocol stream (poll frames)"},
    "call_status": {"worker": "ARCHON", "desc": "Agent virtual numbers + calls status"},
    "call_numbers": {"worker": "ARCHON", "desc": "List agent virtual numbers"},
    "call_assign": {"worker": "ARCHON", "desc": "Assign virtual number to agent"},
    "call_dial": {"worker": "ARCHON", "desc": "Dial from agent virtual number"},
    "call_answer": {"worker": "ARCHON", "desc": "Answer agent call"},
    "call_hangup": {"worker": "ARCHON", "desc": "Hang up agent call"},
    "call_speak": {"worker": "ARCHON", "desc": "Speak on active soft call"},
    "call_list": {"worker": "ARCHON", "desc": "List agent calls"},
    "go": {"worker": "ARCHON", "desc": "GO — sync all active states and arm working workflows"},
    "go_state": {"worker": "ARCHON", "desc": "GO live board: surfaces + 100 workflow states"},
    "go_tick": {"worker": "ARCHON", "desc": "Refresh GO active states from the lab"},
    "power_do": {"worker": "ARCHON", "desc": "Do a goal on the host (route + run + receipt)"},
    "power_pulse": {"worker": "ARCHON", "desc": "Live lab pulse: clouds · tools · workflows"},
    "power_vs": {"worker": "ARCHON", "desc": "Us vs vendor chat apps"},
    "multi_workflows": {"worker": "ARCHON", "desc": "100 multi-agent workflow catalog"},
    "multi_workflow_run": {"worker": "ARCHON", "desc": "Run one multi workflow by id"},
    "universal_catalog": {"worker": "ARCHON", "desc": "200-tool MCP pack catalog"},
    "universal_health": {"worker": "ARCHON", "desc": "Health of POCKET + Forge + Engine + MESIE"},
    "universal_ping": {"worker": "ARCHON", "desc": "Universal liveness"},
    "universal_route": {"worker": "ARCHON", "desc": "Route a goal to pocket|forge|engine|mesie"},
    "universal_billing_plans": {"worker": "ARCHON", "desc": "Shared billing catalog"},
    "universal_clouds": {"worker": "ARCHON", "desc": "Sovereign computing clouds"},
    "billing_lookup": {"worker": "ARCHON", "desc": "Lookup shared plan (aliases ok)"},
    "mesie_embed": {"worker": "ARCHON", "desc": "Embed a series via MESIE"},
    "forge_strategies": {"worker": "ARCHON", "desc": "Forge strategy catalog"},
    "engine_cores": {"worker": "ARCHON", "desc": "Sovereign Engine cores"},
    # Multi-sandbox capsules + WebGPU
    "capsule_status": {"worker": "ARCHON", "desc": "PROTO-CAPSULE-WASM-009 status"},
    "capsule_allocate": {"worker": "ARCHON", "desc": "Allocate isolated capsule"},
    "capsule_execute": {"worker": "ARCHON", "desc": "Run command in capsule"},
    "capsule_commit": {"worker": "ARCHON", "desc": "Commit capsule ChangeSet"},
    "capsule_terminate": {"worker": "ARCHON", "desc": "Terminate capsule"},
    "capsule_list": {"worker": "ARCHON", "desc": "List capsules"},
    "webgpu_probe": {"worker": "ARCHON", "desc": "WebGPU/GPU host probe"},
    # Product Studio first-class
    "studio_map": {"worker": "STUDIO", "desc": "Studio first-class map"},
    "studio_status": {"worker": "STUDIO", "desc": "Studio health"},
    "studio_open": {"worker": "STUDIO", "desc": "Studio URLs"},
    "studio_playbooks": {"worker": "STUDIO", "desc": "Agent studio playbooks"},
    "studio_storyboard": {"worker": "STUDIO", "desc": "Demo storyboard"},
    "studio_caption": {"worker": "STUDIO", "desc": "Marketing captions"},
    "studio_list_recordings": {"worker": "STUDIO", "desc": "List recordings"},
    "studio_list_exports": {"worker": "STUDIO", "desc": "List exports"},
    "studio_presets": {"worker": "STUDIO", "desc": "Presets catalog"},
    "studio_record_start": {"worker": "SPECULUM", "desc": "Start record"},
    "studio_record_stop": {"worker": "SPECULUM", "desc": "Stop record"},
    "studio_render": {"worker": "STUDIO", "desc": "Render preset"},
    "studio_viral": {"worker": "STUDIO", "desc": "Viral pack"},
    "studio_batch": {"worker": "STUDIO", "desc": "Batch render"},
    "studio_ship": {"worker": "STUDIO", "desc": "Ship pack + caption"},
    "studio_auto": {"worker": "STUDIO", "desc": "Auto viral pack"},
    "viral_pack": {"worker": "STUDIO", "desc": "Viral pack alias"},
    "imagine_compose": {"worker": "STUDIO", "desc": "Device still compose"},
    # PORTARIUS
    "open_app": {"worker": "PORTARIUS", "desc": "Open allowlisted desktop app"},
    "open_edge_url": {"worker": "PORTARIUS", "desc": "Open URL in signed-in Edge"},
    "open_spacex": {"worker": "PORTARIUS", "desc": "Open spacex.com"},
    "open_tradingview_web": {"worker": "PORTARIUS", "desc": "Open tradingview.com"},
    "open_tradingview_app": {"worker": "PORTARIUS", "desc": "Open TradingView desktop"},
    "open_metatrader": {"worker": "PORTARIUS", "desc": "Open MetaTrader 5"},
    "open_cursor": {"worker": "PORTARIUS", "desc": "Open Cursor"},
    "open_antigravity": {"worker": "PORTARIUS", "desc": "Open Antigravity"},
    "close_edge": {"worker": "PORTARIUS", "desc": "Close Edge windows only"},
    # SCRUTATOR / REPOSITOR
    "github_open_top5": {"worker": "REPOSITOR", "desc": "Open first 5 GitHub repos in Edge"},
    "github_explore_tabs": {"worker": "REPOSITOR", "desc": "Click/open all major GitHub project tabs"},
    "github_research": {"worker": "SCRUTATOR", "desc": "Full research bring-back on a repo"},
    "clone_https": {"worker": "REPOSITOR", "desc": "Shallow HTTPS clone under workspaces"},
    # NAVIGATOR / SCRIPTOR
    "tweet_research": {"worker": "NAVIGATOR", "desc": "Open X compose with research text"},
    "research_to_tweet": {"worker": "SCRIPTOR", "desc": "Compose tweet from research"},
    # CONSILIARIUS
    "copilot_chat_send": {"worker": "CONSILIARIUS", "desc": "Paste into Copilot chat and Enter"},
    "copilot_search_bar": {"worker": "CONSILIARIUS", "desc": "Win search / Copilot search skill (fallback)"},
    # TABELLARIUS / OCULUS / SPECULUM
    "outlook_draft_research": {"worker": "TABELLARIUS", "desc": "Draft email with research body"},
    "notepad_hello": {"worker": "PORTARIUS", "desc": "Notepad + type hello world message"},
    "explorer_new_file": {"worker": "PORTARIUS", "desc": "Explorer + create a file"},
    "calc_run": {"worker": "PORTARIUS", "desc": "Calculator + run a sum"},
    "powershell_run": {"worker": "PORTARIUS", "desc": "PowerShell + run a command"},
    "screenshot": {"worker": "OCULUS", "desc": "Screenshot paste-back"},
    "record_start": {"worker": "SPECULUM", "desc": "Start screen record"},
    "record_stop": {"worker": "SPECULUM", "desc": "Stop screen record"},
    # ARCHON
    "grand_demo": {"worker": "ARCHON", "desc": "Legacy multi-surface demo"},
    "focused_demo": {"worker": "ARCHON", "desc": "Real one-GitHub + record + discrete skills"},
    "github_one_page": {"worker": "REPOSITOR", "desc": "ONE GitHub page, scroll/UI only"},
    "antigravity_explore": {"worker": "PORTARIUS", "desc": "Open Antigravity and explore UI"},
    "github_desktop_peek": {"worker": "REPOSITOR", "desc": "GitHub Desktop peek"},
    "email_hi_world": {"worker": "TABELLARIUS", "desc": "Draft hi-to-the-world email"},
    "research_interest": {"worker": "SCRUTATOR", "desc": "What interests us in a repo"},
    "record_start": {"worker": "SPECULUM", "desc": "Start full-screen record"},
    "record_stop": {"worker": "SPECULUM", "desc": "Stop record and save"},
}

# Life skills every Latin worker can call (embedded platform tools)
_LIFE_FOR_ALL = [
    "life_catalog",
    "life_status",
    "life_classify",
    "food_order",
    "flight_search",
    "shop_search",
    "web_browse",
    "reservation",
    "web_search",
    "list_skills",
    "assist_route",
    "tools_for_prompt",
]

# Capsule / WebGPU skills for all workers (PROTO-CAPSULE-WASM-009)
_CAPSULE_FOR_ALL = [
    "capsule_status",
    "capsule_list",
    "capsule_allocate",
    "capsule_execute",
    "capsule_commit",
    "capsule_terminate",
    "webgpu_probe",
]

# Product Studio first-class for all agents
_STUDIO_FOR_ALL = [
    "studio_map",
    "studio_status",
    "studio_open",
    "studio_playbooks",
    "studio_storyboard",
    "studio_caption",
    "studio_list_recordings",
    "studio_list_exports",
    "studio_presets",
    "studio_record_start",
    "studio_record_stop",
    "studio_render",
    "studio_viral",
    "studio_batch",
    "studio_ship",
    "imagine_compose",
]

WORKER_SKILLS: Dict[str, List[str]] = {
    "ARCHON": [
        "platform_map", "find_feature", "habitat_status", "habitat_pulse", "screen_sense",
        "work_start", "fusion_voice", "pair_mint", "phone_surface", "mcp_catalog",
        "grand_demo", "github_open_top5", "github_explore_tabs", "github_research", "tweet_research",
        "outlook_draft_research", "copilot_chat_send", "open_tradingview_web", "open_tradingview_app",
        "open_metatrader", "calc_run", "powershell_run", "close_edge", "record_start", "record_stop",
        "integrations_list", "iot_status", "wsl_status", "auro_status", "muse_status", "web_fetch",
        *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL,
    ],
    "HYDRA": [
        "github_open_top5", "open_cursor", "open_antigravity", "copilot_chat_send", "calc_run",
        *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL,
    ],
    "SCRUTATOR": ["github_research", "clone_https", "web_search", "web_fetch", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "SCRIPTOR": ["research_to_tweet", "web_search", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "PORTARIUS": [
        "open_app", "open_edge_url", "open_spacex", "open_tradingview_web", "open_tradingview_app",
        "open_metatrader", "open_cursor", "open_antigravity", "close_edge", "notepad_hello",
        "explorer_new_file", "calc_run", "powershell_run", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL,
    ],
    "OCULUS": ["screenshot", "screen_sense", "web_browse", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "SPECULUM": ["record_start", "record_stop", "studio_record_start", "studio_record_stop", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "REPOSITOR": ["github_open_top5", "github_explore_tabs", "clone_https", "web_search", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "CONSILIARIUS": ["copilot_chat_send", "copilot_search_bar", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "TABELLARIUS": ["outlook_draft_research", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "NAVIGATOR": [
        "tweet_research", "open_spacex", "open_tradingview_web",
        "food_order", "flight_search", "shop_search", "web_browse", "reservation", "web_search",
        *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL,
    ],
    "GUPPY": ["open_app", "github_open_top5", "screenshot", *_LIFE_FOR_ALL, *_CAPSULE_FOR_ALL, *_STUDIO_FOR_ALL],
    "STUDIO": list(_STUDIO_FOR_ALL) + ["screenshot", "screen_sense", "record_start", "record_stop", "platform_map"],
}


def skills_for(worker: str) -> List[Dict[str, Any]]:
    w = (worker or "").upper()
    ids = WORKER_SKILLS.get(w) or []
    return [{"id": i, **SKILLS[i]} for i in ids if i in SKILLS]


def all_skills() -> List[Dict[str, Any]]:
    return [{"id": k, **v} for k, v in SKILLS.items()]
