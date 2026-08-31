"""Super skill suite — 100+ named skills the platform knows.

Skills are catalog entries. Execution goes through Orchestrator → skill_runner / skills_real.
Long-horizon skills are multi-step playbooks; short skills are atomic.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Each skill: id, worker, kind (atomic|playbook), desc, tags
def _s(id: str, worker: str, desc: str, kind: str = "atomic", tags: str = "") -> Dict[str, Any]:
    return {"id": id, "worker": worker, "desc": desc, "kind": kind, "tags": tags.split() if tags else []}


SUITE: List[Dict[str, Any]] = [
    # --- Platform coherence (discoverable · agent skills · one product) ---
    _s("platform_map", "ARCHON", "Full coherent platform map (Habitat→Phone→Fusion→MCP)", tags="platform discover"),
    _s("platform_health", "ARCHON", "Domain health habitat/screen/work/fusion/mcp/novae", tags="platform health"),
    _s("novae_list", "ARCHON", "List Grok Novae + Codex Novae hands", tags="platform novae agents"),
    _s("novae_status", "ARCHON", "Novae activation status", tags="platform novae"),
    _s("novae_activate", "ARCHON", "Activate Novae hands in POCKET workspace", tags="platform novae agents"),
    _s("imagine_status", "STUDIO", "Imagine Studio status + /imagine UI", tags="imagine studio"),
    _s("imagine_gallery", "STUDIO", "Imagine stills and fusion remakes", tags="imagine studio"),
    _s("foundations_map", "ARCHON", "Internal AI + math + self + world catalog", tags="platform models math internal"),
    _s("bots_list", "ARCHON", "List POCKET Bots teammates", tags="bots agents"),
    _s("bots_hire", "ARCHON", "Hire a Pocket bot from a job description", tags="bots agents"),
    _s("bots_message", "ARCHON", "Message a Pocket bot", tags="bots agents"),
    _s("neuro_think", "ARCHON", "Spherical neuro pass for primary engines", tags="neuro engines"),
    _s("find_feature", "ARCHON", "Find desk tab / phone / API / skill for a feature", tags="platform discover"),
    _s("list_agents", "ARCHON", "First-class desk + phone agents", tags="platform agents"),
    _s("habitat_status", "ARCHON", "Habitat residents + rooms", tags="habitat"),
    _s("habitat_open", "ARCHON", "Open habitat floor", tags="habitat"),
    _s("habitat_pulse", "ARCHON", "Pulse resident status", tags="habitat"),
    _s("habitat_assign", "ARCHON", "Assign task to habitat resident", tags="habitat"),
    _s("screen_status", "OCULUS", "Screen share status", tags="screen"),
    _s("screen_view", "OCULUS", "Screen View mode (agents see)", tags="screen"),
    _s("screen_control", "OCULUS", "Screen Control mode (agents drive)", tags="screen"),
    _s("screen_off", "OCULUS", "Turn screen share off", tags="screen"),
    _s("screen_sense", "OCULUS", "Fusion brief of shared screen", tags="screen fusion"),
    _s("work_start", "ARCHON", "Start Working mode (voice+screen+package)", tags="work voice phone"),
    _s("work_status", "ARCHON", "Working sessions status", tags="work"),
    _s("work_package", "ARCHON", "Package working conversation", tags="work"),
    _s("work_handoff", "ARCHON", "Handoff package → artifacts", tags="work"),
    _s("fusion_voice", "ARCHON", "Conversational Fusion (DFW expert/patience/preload)", tags="fusion voice phone"),
    _s("fusion_schema", "ARCHON", "Conversational Fusion schema", tags="fusion voice"),
    _s("fusion_last", "ARCHON", "Last fusion for session_id", tags="fusion"),
    _s("voice_skills_list", "ARCHON", "Aria everyday skills list", tags="voice"),
    _s("aria_turn", "ARCHON", "Aria local skill + fusion hint", tags="voice phone"),
    _s("phone_surface", "ARCHON", "Phone URLs + pair instructions", tags="phone"),
    _s("pair_mint", "ARCHON", "Mint desk pair code for phone", tags="phone pair"),
    _s("pair_status", "ARCHON", "Node pair status + peers", tags="phone pair"),
    _s("mcp_catalog", "ARCHON", "10 embedded MCPs", tags="mcp"),
    _s("mcp_invoke", "ARCHON", "Invoke MCP server.tool", tags="mcp"),
    _s("cli_list", "ARCHON", "CLI inventory for agents", tags="cli"),
    _s("cli_run", "ARCHON", "Run allowlisted CLI", tags="cli"),
    _s("voice_studio_open", "ARCHON", "Voice Studio URL + paper→product map", tags="voice studio"),
    # --- Everyday life (all agents · never auto-pay) ---
    _s("life_catalog", "ARCHON", "Catalog of food/flights/shop/web/reserve skills", tags="life discover"),
    _s("life_status", "ARCHON", "Working board + life ops status", tags="life work"),
    _s("life_classify", "ARCHON", "Classify prompt into food/flight/shop/browse/reservation", tags="life route"),
    _s("food_order", "NAVIGATOR", "Food delivery options — you pay", tags="life food"),
    _s("flight_search", "NAVIGATOR", "Flight search Google Flights — you book", tags="life travel"),
    _s("shop_search", "NAVIGATOR", "Shopping search Amazon etc — you checkout", tags="life shop"),
    _s("web_browse", "NAVIGATOR", "Open/search web in Edge + sense", tags="life web"),
    _s("reservation", "NAVIGATOR", "Restaurant reservation OpenTable — you confirm", tags="life dining"),
    _s("web_search", "SCRUTATOR", "Host multi-backend web search", tags="web research"),
    _s("web_fetch", "SCRUTATOR", "Fetch URL cleaned text", tags="web research"),
    _s("integrations_list", "ARCHON", "50+ life integrations catalog", tags="integrations life"),
    _s("assist_route", "ARCHON", "Route request to digital-assistant engine", tags="assist life"),
    _s("wsl_status", "ARCHON", "WSL / Linux status for integrated console", tags="console wsl"),
    _s("auro_status", "ARCHON", "Local Auro meaning model status", tags="auro model"),
    _s("muse_status", "ARCHON", "Muse Spark multimodal assist surface", tags="muse assist"),
    _s("tools_for_prompt", "ARCHON", "Plan which host tools match a prompt", tags="platform tools"),
    # --- PROTO-CAPSULE-WASM-009 Multi-Sandbox + WebGPU ---
    _s("capsule_status", "ARCHON", "Multi-sandbox capsule protocol status", tags="capsule sandbox wasm"),
    _s("capsule_allocate", "ARCHON", "Allocate capsule tier+WebGPU+repo", tags="capsule sandbox"),
    _s("capsule_execute", "ARCHON", "Execute command in capsule", tags="capsule sandbox"),
    _s("capsule_commit", "ARCHON", "Commit OverlayFS ChangeSet", tags="capsule sandbox"),
    _s("capsule_terminate", "ARCHON", "Terminate capsule release memory", tags="capsule sandbox"),
    _s("capsule_list", "ARCHON", "List live capsules", tags="capsule sandbox"),
    _s("webgpu_probe", "ARCHON", "Host GPU/WebGPU probe + doctrine", tags="webgpu gpu capsule"),
    # --- SPECULUM / OCULUS (vision & record) ---
    _s("record_start", "SPECULUM", "Start full-desktop video record", tags="vision record"),
    _s("record_stop", "SPECULUM", "Stop record and save mp4", tags="vision record"),
    _s("record_status", "SPECULUM", "Is recording active?", tags="vision"),
    _s("screenshot", "OCULUS", "Single screenshot paste-back", tags="vision"),
    _s("screenshot_series", "OCULUS", "Take N screenshots over time", kind="playbook", tags="vision"),
    _s("vision_latest", "OCULUS", "Get latest live vision frame", tags="vision"),
    _s("vision_start", "OCULUS", "Start live vision daemon", tags="vision"),
    _s("snip_open", "OCULUS", "Open Windows Snipping Tool", tags="vision"),
    _s("understand", "OCULUS", "Pixel translator: visual+semantic+OCR fuse", tags="vision"),
    _s("pixel_translate", "OCULUS", "Alias understand — optimal modality", tags="vision"),
    _s("pixel_text", "OCULUS", "Force pixel→text (UI + OCR)", tags="vision"),
    _s("see_screen", "OCULUS", "Agent brief of what is on glass", tags="vision"),
    _s("page_render", "OCULUS", "Full page micro-detail → symbol graph", tags="vision"),
    _s("full_page", "OCULUS", "Alias page_render", tags="vision"),
    _s("page_symbols", "OCULUS", "Alias page_render symbols", tags="vision"),
    _s("stream_start", "OCULUS", "Start real-time page understanding stream", tags="vision"),
    _s("stream_stop", "OCULUS", "Stop understanding stream", tags="vision"),
    _s("stream_latest", "OCULUS", "Poll latest stream frame", tags="vision"),
    # Product Studio first-class (agents)
    _s("studio_map", "STUDIO", "First-class Studio map for agents", tags="studio discover"),
    _s("studio_status", "STUDIO", "Studio health ffmpeg/recordings/exports", tags="studio"),
    _s("studio_open", "STUDIO", "Studio surface URLs", tags="studio"),
    _s("studio_playbooks", "STUDIO", "Agent playbooks viral/record/caption/ship", tags="studio agents"),
    _s("studio_storyboard", "STUDIO", "Hook→proof→CTA demo storyboard", tags="studio agents"),
    _s("studio_caption", "STUDIO", "Launch + social caption pack", tags="studio marketing"),
    _s("studio_list_recordings", "STUDIO", "List host recordings", tags="studio"),
    _s("studio_list_exports", "STUDIO", "List polished exports", tags="studio"),
    _s("studio_presets", "STUDIO", "Viral presets catalog", tags="studio"),
    _s("studio_record_start", "SPECULUM", "Start desktop record for studio", tags="studio record"),
    _s("studio_record_stop", "SPECULUM", "Stop record save mp4", tags="studio record"),
    _s("studio_auto", "STUDIO", "Viral pack: phone remake + web + screencast", tags="studio"),
    _s("studio_viral", "STUDIO", "Alias studio_auto viral pack", tags="studio export"),
    _s("studio_render", "STUDIO", "Render preset rotato_phone|x_screencast|macbook_web|clean_demo", tags="studio"),
    _s("studio_batch", "STUDIO", "Multi-preset batch render", tags="studio export"),
    _s("studio_ship", "STUDIO", "End-to-end viral + caption ship", tags="studio ship"),
    _s("viral_pack", "STUDIO", "Alias studio_viral", tags="studio"),
    _s("fusion_remake", "OCULUS", "Symbols → IR → HTML remake + 3D scene graph", tags="vision imagine"),
    _s("rfe_synthesize", "OCULUS", "RFE-v1 FULL_SYNTHESIS: packet+HTML+3D+GLSL", tags="rfe vision"),
    _s("rfe_v1", "OCULUS", "Alias rfe_synthesize (Recursive Fusion Engine)", tags="rfe"),
    _s("imagine_compose", "STUDIO", "Imagine Studio still: rotato phone / macbook web", tags="imagine studio"),
    _s("compose_device", "STUDIO", "Alias imagine_compose", tags="imagine"),
    _s("vcomp_open", "ARCHON", "Open virtual computer (workspace+terminal+fusion)", tags="vcomp alpha"),
    _s("vcomp_sense", "OCULUS", "Virtual computer full fusion sense", tags="vcomp vision"),
    _s("vcomp_act", "PORTARIUS", "Virtual computer act (click/type/app/url/skill)", tags="vcomp"),
    _s("mission_start", "ARCHON", "Start multi-hour mission loop (chain prompts)", tags="mission alpha"),
    _s("workflow_run", "ARCHON", "Run alpha workflow wf1..wf5", tags="workflow alpha"),
    _s("workflow_all", "ARCHON", "Run all 5 alpha multimodal workflows", tags="workflow alpha"),
    # --- PORTARIUS open apps ---
    _s("open_notepad", "PORTARIUS", "Open Notepad"),
    _s("open_explorer", "PORTARIUS", "Open File Explorer"),
    _s("open_calc", "PORTARIUS", "Open Calculator"),
    _s("open_edge", "PORTARIUS", "Open Edge"),
    _s("open_chrome", "PORTARIUS", "Open Chrome"),
    _s("open_code", "PORTARIUS", "Open VS Code"),
    _s("open_cursor", "PORTARIUS", "Open Cursor"),
    _s("open_antigravity", "PORTARIUS", "Open Antigravity"),
    _s("open_copilot", "PORTARIUS", "Open Windows Copilot"),
    _s("open_teams", "PORTARIUS", "Open Teams"),
    _s("open_word", "PORTARIUS", "Open Word"),
    _s("open_excel", "PORTARIUS", "Open Excel"),
    _s("open_powerpoint", "PORTARIUS", "Open PowerPoint"),
    _s("open_outlook", "PORTARIUS", "Open Outlook"),
    _s("open_discord", "PORTARIUS", "Open Discord"),
    _s("open_slack", "PORTARIUS", "Open Slack"),
    _s("open_spotify", "PORTARIUS", "Open Spotify"),
    _s("open_github_desktop", "PORTARIUS", "Open GitHub Desktop"),
    _s("open_docker", "PORTARIUS", "Open Docker Desktop"),
    _s("open_terminal", "PORTARIUS", "Open Windows Terminal"),
    _s("open_settings", "PORTARIUS", "Open Windows Settings"),
    _s("open_taskmgr", "PORTARIUS", "Open Task Manager"),
    _s("open_paint", "PORTARIUS", "Open Paint"),
    _s("open_snip", "PORTARIUS", "Open Snipping Tool"),
    _s("open_tradingview_app", "PORTARIUS", "Open TradingView desktop"),
    _s("open_metatrader", "PORTARIUS", "Open MetaTrader 5"),
    _s("open_claude_app", "PORTARIUS", "Open Claude desktop"),
    _s("open_chatgpt_app", "PORTARIUS", "Open ChatGPT app"),
    _s("maximize_window", "PORTARIUS", "Maximize foreground window", tags="ui"),
    _s("close_window", "PORTARIUS", "Alt+F4 foreground window", tags="ui"),
    _s("scroll_down", "PORTARIUS", "Page-down scroll", tags="ui"),
    _s("scroll_up", "PORTARIUS", "Page-up scroll", tags="ui"),
    _s("scroll_read", "PORTARIUS", "Human-like multi scroll read", kind="playbook", tags="ui"),
    _s("type_hello", "PORTARIUS", "Type text via clipboard paste", tags="ui"),
    _s("notepad_write", "PORTARIUS", "Notepad + paste full message", kind="playbook"),
    _s("explorer_new_file", "PORTARIUS", "Create file on Desktop + select", kind="playbook"),
    _s("calc_sum", "PORTARIUS", "Calculator run expression", kind="playbook"),
    _s("powershell_cmd", "PORTARIUS", "Open PowerShell with command", kind="playbook"),
    _s("powershell_codex", "PORTARIUS", "PowerShell launch codex", kind="playbook"),
    # --- NAVIGATOR / Edge web ---
    _s("edge_url", "NAVIGATOR", "Open URL in signed-in Edge"),
    _s("edge_spacex", "NAVIGATOR", "Open spacex.com + scroll", kind="playbook"),
    _s("edge_tradingview", "NAVIGATOR", "Open tradingview.com + scroll", kind="playbook"),
    _s("edge_github_home", "NAVIGATOR", "Open github.com"),
    _s("edge_x_home", "NAVIGATOR", "Open x.com/home"),
    _s("edge_google", "NAVIGATOR", "Open google.com"),
    _s("edge_bing", "NAVIGATOR", "Open bing.com"),
    _s("edge_hn", "NAVIGATOR", "Open news.ycombinator.com"),
    _s("edge_reddit", "NAVIGATOR", "Open reddit.com"),
    _s("edge_linkedin", "NAVIGATOR", "Open linkedin.com"),
    _s("edge_youtube", "NAVIGATOR", "Open youtube.com"),
    _s("edge_docs_ms", "NAVIGATOR", "Open docs.microsoft.com"),
    _s("tweet_compose", "NAVIGATOR", "Open X intent with text", kind="playbook"),
    _s("tweet_hi_world", "NAVIGATOR", "Compose hi-world tweet", kind="playbook"),
    # --- REPOSITOR / SCRUTATOR ---
    _s("github_one_page", "REPOSITOR", "ONE repo page UI scroll/click", kind="playbook", tags="github"),
    _s("github_desktop_peek", "REPOSITOR", "GitHub Desktop tour", kind="playbook", tags="github"),
    _s("github_list", "REPOSITOR", "List top repos via gh"),
    _s("github_open_top3", "REPOSITOR", "Open 3 repos (explicit multi)", kind="playbook"),
    _s("github_clone", "REPOSITOR", "HTTPS shallow clone"),
    _s("github_analyze", "SCRUTATOR", "Analyze repo for POCKET hooks", kind="playbook"),
    _s("research_interest", "SCRUTATOR", "What interests us in a repo", kind="playbook"),
    _s("lookup_web", "SCRUTATOR", "Web lookup + bring back", kind="playbook"),
    _s("research_company", "SCRUTATOR", "Research a company/topic brief", kind="playbook"),
    _s("new_folder", "REPOSITOR", "Create workspace folder"),
    _s("new_git_repo", "REPOSITOR", "Local git init"),
    _s("zip_folder", "REPOSITOR", "Zip a folder under home"),
    # --- TABELLARIUS / CONSILIARIUS / SCRIPTOR ---
    _s("email_hi_world", "TABELLARIUS", "Draft hi-world email max", kind="playbook"),
    _s("email_draft", "TABELLARIUS", "Draft custom email", kind="playbook"),
    _s("email_research", "TABELLARIUS", "Draft email from research body", kind="playbook"),
    _s("copilot_open", "CONSILIARIUS", "Open Windows Copilot"),
    _s("copilot_chat_send", "CONSILIARIUS", "Paste+Enter to Copilot", kind="playbook"),
    _s("copilot_introduce", "CONSILIARIUS", "Introduce POCKET to Copilot", kind="playbook"),
    _s("compose_tweet_llm", "SCRIPTOR", "LLM draft a tweet", kind="playbook"),
    # --- ARCHON / HYDRA / GUPPY playbooks ---
    _s("focused_demo", "ARCHON", "Recorded one-GitHub focused demo", kind="playbook"),
    _s("wow_demo", "ARCHON", "Impressive multi-surface recorded demo", kind="playbook"),
    _s("morning_desk", "ARCHON", "Morning: vision, outlook draft, calendar sites", kind="playbook"),
    _s("ship_pulse", "ARCHON", "Ship pulse: github one page + tweet + screenshot", kind="playbook"),
    _s("dev_warm", "ARCHON", "Warm dev tools: cursor, terminal, explorer", kind="playbook"),
    _s("market_glance", "ARCHON", "TradingView web scroll + MT5 peek", kind="playbook"),
    _s("hydra_fanout", "HYDRA", "Parallel multi-head open burst", kind="playbook"),
    _s("guppy_steps", "GUPPY", "Multi-step then-chain up to 10", kind="playbook"),
    # --- more web destinations ---
    _s("edge_wikipedia", "NAVIGATOR", "Open wikipedia.org"),
    _s("edge_arxiv", "NAVIGATOR", "Open arxiv.org"),
    _s("edge_github_trending", "NAVIGATOR", "Open github.com/trending"),
    _s("edge_cloudflare", "NAVIGATOR", "Open dash.cloudflare.com"),
    _s("edge_vercel", "NAVIGATOR", "Open vercel.com"),
    _s("edge_openai", "NAVIGATOR", "Open platform.openai.com"),
    _s("edge_xai", "NAVIGATOR", "Open x.ai"),
    _s("edge_anthropic", "NAVIGATOR", "Open anthropic.com"),
    # --- system / desk ---
    _s("list_apps", "PORTARIUS", "List allowlisted apps"),
    _s("list_skills", "ARCHON", "List skill suite"),
    _s("list_workers", "ARCHON", "List Latin workers"),
    _s("subagents_list", "ARCHON", "Unified subagents registry for desk UI"),
    _s("subagents_dispatch", "ARCHON", "Dispatch @mentions to Latin/headless mesh agents"),
    _s("mesh_bootstrap", "ARCHON", "Bootstrap E: mesh disk + 4 headless agents"),
    _s("daemon_status", "ARCHON", "Worker daemon live status"),
    _s("learn_list", "ARCHON", "List learned skills"),
    _s("create_worker", "ARCHON", "Create ephemeral worker definition", kind="playbook"),
    _s("run_playbook", "ARCHON", "Run named playbook steps", kind="playbook"),
    # expand to 100+ with patterned micro-skills
]

# Pattern bulk: open + scroll for many sites
_SITES = [
    ("stripe", "https://stripe.com"),
    ("notion", "https://www.notion.so"),
    ("figma_web", "https://www.figma.com"),
    ("linear_web", "https://linear.app"),
    ("producthunt", "https://www.producthunt.com"),
    ("techcrunch", "https://techcrunch.com"),
    ("bloomberg", "https://www.bloomberg.com"),
    ("coindesk", "https://www.coindesk.com"),
    ("polygonscan", "https://polygonscan.com"),
    ("etherscan", "https://etherscan.io"),
    ("monad", "https://www.monad.xyz"),
    ("cloudflare_docs", "https://developers.cloudflare.com"),
    ("python_org", "https://www.python.org"),
    ("rust_lang", "https://www.rust-lang.org"),
    ("mdn", "https://developer.mozilla.org"),
    ("stackoverflow", "https://stackoverflow.com"),
    ("github_skills", "https://skills.github.com"),
    ("aws", "https://aws.amazon.com"),
    ("azure", "https://azure.microsoft.com"),
    ("gcp", "https://cloud.google.com"),
    ("docker_hub", "https://hub.docker.com"),
    ("npm", "https://www.npmjs.com"),
    ("pypi", "https://pypi.org"),
    ("huggingface", "https://huggingface.co"),
    ("kaggle", "https://www.kaggle.com"),
    ("twitch", "https://www.twitch.tv"),
    ("instagram", "https://www.instagram.com"),
    ("tiktok", "https://www.tiktok.com"),
    ("whatsapp_web", "https://web.whatsapp.com"),
    ("gmail", "https://mail.google.com"),
    ("calendar_google", "https://calendar.google.com"),
    ("maps_google", "https://maps.google.com"),
    ("drive", "https://drive.google.com"),
    ("dropbox", "https://www.dropbox.com"),
    ("zoom_web", "https://zoom.us"),
    ("canva", "https://www.canva.com"),
    ("miro", "https://miro.com"),
    ("airtable", "https://airtable.com"),
    ("asana", "https://asana.com"),
    ("trello", "https://trello.com"),
    ("jira", "https://www.atlassian.com/software/jira"),
    ("gitlab", "https://gitlab.com"),
    ("bitbucket", "https://bitbucket.org"),
    ("digitalocean", "https://www.digitalocean.com"),
    ("heroku", "https://www.heroku.com"),
    ("netlify", "https://www.netlify.com"),
    ("supabase", "https://supabase.com"),
    ("firebase", "https://firebase.google.com"),
    ("openai_chat", "https://chat.openai.com"),
    ("claude_web", "https://claude.ai"),
    ("grok_web", "https://grok.com"),
    ("perplexity_web", "https://www.perplexity.ai"),
    ("midjourney", "https://www.midjourney.com"),
    ("runway", "https://runwayml.com"),
    ("elevenlabs", "https://elevenlabs.io"),
    ("replicate", "https://replicate.com"),
    ("langchain", "https://www.langchain.com"),
    ("llamaindex", "https://www.llamaindex.ai"),
]

for _name, _url in _SITES:
    SUITE.append(
        _s(f"edge_{_name}", "NAVIGATOR", f"Open {_url} in Edge (+ optional scroll)", kind="atomic", tags="web")
    )

# App open aliases already partial — add more playbooks
for _p in (
    "warmup_office",
    "warmup_comms",
    "warmup_ai_ides",
    "cleanup_foreground",
    "screenshot_then_notepad",
    "research_then_email",
    "research_then_tweet",
    "clone_then_analyze",
    "vision_burst",
    "fundable_showcase",
):
    SUITE.append(_s(_p, "ARCHON", f"Playbook: {_p.replace('_', ' ')}", kind="playbook", tags="playbook"))


def all_skills() -> List[Dict[str, Any]]:
    # dedupe by id — merge platform coherence skills first
    seen = set()
    out = []
    try:
        from pocket.platform_coherence import platform_skills

        for s in platform_skills():
            if s["id"] in seen:
                continue
            seen.add(s["id"])
            out.append(
                {
                    "id": s["id"],
                    "worker": s.get("worker") or "ARCHON",
                    "desc": s.get("desc") or "",
                    "kind": s.get("kind") or "atomic",
                    "tags": s.get("tags") or ["platform"],
                }
            )
    except Exception:
        pass
    for s in SUITE:
        if s["id"] in seen:
            continue
        seen.add(s["id"])
        out.append(s)
    return out


def skill_count() -> int:
    return len(all_skills())


def get_skill(skill_id: str) -> Dict[str, Any] | None:
    sid = (skill_id or "").lower().replace("-", "_")
    for s in all_skills():
        if s["id"] == sid:
            return s
    return None
