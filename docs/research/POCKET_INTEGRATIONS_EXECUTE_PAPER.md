# Executable Integrations on POCKET: Desktop-First Connectors, Browser Fallbacks, and Intentional Life Ops

**Working Paper**  
**System:** POCKET Integrations Execute  
**Schema:** `pocket.integrations.execute.v1`  
**Lab:** ItsNotAI Labs  
**Product:** POCKET  
**Date:** 2026-08-08  
**Status:** First-class — 55 catalog entries, live execute path  

---

## Abstract

Integration catalogs that only open marketing URLs are **directory UX**, not agency. This paper specifies and evaluates **POCKET Integrations Execute**: a uniform execute surface where every catalog entry can produce a **structured receipt** via desktop app launch, signed-in Edge remote browser, Working board intent, agent seat, or host tab.

On the operator Windows host we measure **55/55 dry-run execute**, desktop resolution for Discord (latest `app-*`), Teams, Edge, GitHub Desktop, and Copilot, and board+browser paths for dining/commerce/productivity SaaS. We document the safety allowlist, Discord Squirrel/`Update.exe` handling, and the doctrine that **execute is first-class**—list is not enough.

**Keywords:** desktop automation, connectors, OAuth-less signed-in browser, integration catalog, POCKET, host agents

---

## 1. Introduction

Agent products frequently list “50+ integrations” that merely deep-link to websites. Users discover that “Discord integration” means a tab to `discord.com/app`, not launching their installed client with their real sessions.

POCKET’s requirement is different: **agents and the desk must be able to act**. This paper defines the execute contract, maps actions to host surfaces, and reports live host results.

### 1.1 Contributions

1. Unified **execute** engine (`integrations_exec.execute`) for all catalog entries  
2. **Desktop-first** mapping for installed apps with browser fallback  
3. **Board intents** for reserve/buy/research/notify without auto-pay  
4. Live operator-host evaluation (55-entry catalog)  
5. Wiring to desk UI, MCP skills, and LOOMGRAPH `integrate` nodes  

---

## 2. Design

### 2.1 Catalog model

Each integration:

```text
id, name, category, icon, blurb, action, url?, desktop_app?, prefer?, agent?, tab?, prompt?, featured?, executable
```

**Actions:** `open | reserve | buy | research | notify | schedule | errand | analysis | agent | remote | screen | tab | working`

### 2.2 Execute modes

| Mode | Behavior |
|------|----------|
| Desktop | `desktop.open_app` under safety allowlist |
| Browser | `remote_browser.open_url` (signed-in Edge profile) |
| Board | Start Working board intent + optional browser/desktop |
| Agent | Seat agent + optional browser warm |
| Host | Screen control / MCP tab / working board |

### 2.3 Discord special case

Discord on Windows often resolves to `Update.exe`. POCKET:

1. Prefers newest `%LOCALAPPDATA%\Discord\app-*\Discord.exe`  
2. Falls back to `Update.exe --processStart Discord.exe`  
3. Else opens `https://discord.com/app` in Edge  

### 2.4 Safety

- Only `safety.ALLOWED_APPS` keys may launch  
- Audit log on open  
- No arbitrary executable paths from the agent  

### 2.5 API

```http
GET  /v1/integrations
GET  /v1/integrations/readiness
POST /v1/integrations/execute
     {"id":"discord","prefer":"desktop"}
POST /v1/integrations/execute_all
     {"dry_run":true}
```

Skills: `integrations_list`, `integrations_execute`, `integrations_readiness`

---

## 3. Catalog composition (v1)

**Count:** 55 executable entries  

Categories include AI, Dining, Productivity, Dev, Cloud, Commerce, Social, Media, Design, Files, Meetings, CRM, Automation, Host.

**Desktop-mapped examples:** Discord, Slack, Teams, Spotify, Zoom, Notion, Figma, GitHub Desktop, Outlook, Linear, Edge, Telegram, ChatGPT, Copilot, Obsidian  

**Featured:** Muse Spark, OpenTable, GitHub, Cloudflare, Amazon, Edge, Screen Control, MCP, Working board, Discord, Copilot  

---

## 4. Evaluation

### 4.1 Dry-run matrix

`execute_all(dry_run=True)` → **55/55 ok**  
Every integration produces a non-empty step plan (desktop planned and/or browser planned and/or host ready).

### 4.2 Readiness (operator host)

| Metric | Value |
|--------|-------|
| Catalog count | 55 |
| Browser URL surfaces | 50 |
| Desktop available (installed) | 5+ (Copilot, Discord, GitHub Desktop, Teams, Edge) |
| Board intents | 15 |

### 4.3 Live execute samples

| id | Result |
|----|--------|
| discord | desktop:done → Discord.exe |
| teams | desktop:done |
| browser_edge | remote_browser:done |
| github | pick_agent:ready |
| working_board | working_board:ready |
| screen_control | screen_control:ready |
| mcp_tools | show_tab:ready |
| spotify | desktop unavailable → browser:done |
| notion | desktop unavailable → browser:done |
| opentable | working_board + browser:done |
| gmail | working_board + browser:done |
| slack | board path; browser warm when URL present |

### 4.4 Desk UX

`useIntegration(id)` POSTs execute first, then seeds prompts / Working board / tabs. Failures toast with receipt messages.

---

## 5. Discussion

### 5.1 “Working” definition

An integration is **working** if execute returns `ok=true` with at least one of:

1. Desktop process started  
2. Browser navigation started  
3. Host surface ready (board/tab/screen/agent)  

Missing install is **not** a catalog failure if browser/board fallback succeeds.

### 5.2 Why not OAuth for everything

Host Edge already carries user sessions for Gmail, Notion, dashboards. Desktop apps carry native sessions. OAuth multiplies key management for operators; POCKET prefers **session reuse** with explicit safety allowlists. Enterprise OAuth bridges remain future work.

### 5.3 Composition with LOOMGRAPH

LOOMGRAPH graph `integration_open` calls `integrations_exec.execute` as an `integrate` node, so Discord open appears as a path segment humans can see:

`sense → list → exec → verify → done`

---

## 6. Threats and mitigations

| Threat | Mitigation |
|--------|------------|
| Arbitrary exe launch | Allowlist only |
| Silent public share | Community is separate; integrations never auto-post |
| Auto-purchase | Board intents require human confirm; never auto-pay |
| Stale Discord path | Dynamic `app-*` discovery |

---

## 7. Conclusion

POCKET Integrations Execute turns a connector directory into **agency**. With 55 executable entries, desktop-first Discord/Teams, Edge fallbacks, and board intents for life ops, the host can honestly claim **working integrations**—backed by receipts, not marketing URLs alone.

---

## Appendix A — Live smoke (2026-08-08)

```
count 55 desktop 5 browser 50
dry_all 55 / 55 fail 0
discord          ok=True desktop:done
browser_edge     ok=True remote_browser:done
teams            ok=True desktop:done
github           ok=True pick_agent:ready
working_board    ok=True working_board:ready
```

## Appendix B — Citation

ItsNotAI Labs (2026). *Executable Integrations on POCKET.* Working Paper. Schema `pocket.integrations.execute.v1`.

---

*End of working paper.*
