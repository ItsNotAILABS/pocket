# POCKET KEEP · ISOLATE · RECALL · MAIL

Official product systems for **this app (POCKET)** — self-hosted agents, isolated browsers, recall codes, and mailing.

## 1. KEEP — agents until chat ends

**Product:** POCKET KEEP · Protocol `POCKET-KEEP/1.0`

Self-hosted background agents bound to a desk **session** (chat). They pulse LOOMGRAPH on an interval and **stop when the chat ends**.

```http
POST /v1/keep/start
{
  "session_id": "s-…",
  "goal": "Research and draft until I close this chat",
  "graph_id": "default",
  "interval_sec": 45,
  "max_hours": 4,
  "with_browser": true
}

POST /v1/keep/end   {"session_id":"s-…"}   # chat ended
POST /v1/keep/stop  {"id":"keep-…"}
GET  /v1/keep
```

## 2. ISOLATE — Docker / profile browsers

**Product:** POCKET ISOLATE

- **Docker** (when installed): Chromium container with dedicated port  
- **Fallback**: Edge with unique `--user-data-dir` under `~/.pocket/isolate/browser_profiles/{session}`

Browsers are torn down when KEEP stops or chat ends.

```http
GET  /v1/isolate
POST /v1/isolate/start  {"session_id":"s-…","url":"https://example.com"}
POST /v1/isolate/stop   {"session_id":"s-…"}
```

Env: `POCKET_DOCKER_BROWSER_IMAGE` (default `browserless/chrome:latest`)

## 3. RECALL — official recall-code software

**Product:** POCKET RECALL · Protocol `POCKET-RECALL/1.0`

Codes look like `pk_rcl_…`. Only a **hash** is stored. Redeem reattaches KEEP / session / LOOMGRAPH context.

```http
POST /v1/recall/mint
{
  "keep_id": "keep-…",
  "session_id": "s-…",
  "label": "my overnight run"
}
→ { "code": "pk_rcl_…", "expires_at": … }   # save once

POST /v1/recall/redeem  {"code":"pk_rcl_…"}
POST /v1/recall/revoke  {"id":"rcl-…"}
GET  /v1/recall
```

## 4. POCKET MAIL — official mailing

**Product:** POCKET MAIL · Protocol `POCKET-MAIL/1.0`

Templates: `welcome`, `invite`, `recall`, `keep_status`, `system`, `custom`  
Draft by default; SMTP send when configured.

```http
GET  /v1/mail
POST /v1/mail/draft  {"to":"a@b.com","template":"welcome"}
POST /v1/mail/send   {"to":"a@b.com","subject":"…","body":"…","dry_run":true}
GET  /v1/mail/templates
GET  /v1/mail/outbox
```

## 4b. AGENT MAIL — our own accounts + inboxes

**Product:** POCKET AGENT MAIL · Protocol `POCKET-AGENT-MAIL/1.0`  
**Domain:** `agents.pocket.local`

Every desk/phone agent can own an address (e.g. `assist@agents.pocket.local`).  
Agent↔agent delivery is local (inbox files under `~/.pocket/agent_mail/`).  
External addresses use POCKET MAIL SMTP when `external: true`.

Models, Python engines, and MCP all call the same APIs:

```http
GET  /v1/agent-mail
GET  /v1/agent-mail/accounts
POST /v1/agent-mail/accounts  {"agent":"mybot","name":"My Bot"}
GET  /v1/agent-mail/inbox?agent=assist
POST /v1/agent-mail/send  {"from":"scribe","to":"assist","subject":"hi","body":"…"}
POST /v1/agent-mail/read  {"agent":"assist","id":"am-…"}
```

**MCP / skills:** `mail_accounts`, `mail_account_create`, `mail_inbox`, `mail_send`, `mail_read`, `mail_status`

## 4c. Website UI engine + Python engines

Models use **Python** agents/engines (not user browser tabs) to drive website interfaces:

```http
GET  /v1/web-ui
POST /v1/web-ui/open    {"url":"https://example.com"}
POST /v1/web-ui/sense
POST /v1/web-ui/act     {"action":"sense"}
POST /v1/web-ui/browse  {"url":"https://example.com"}
POST /v1/python-engine  {"engine":"browser","prompt":"lookup AI agents"}
GET  /v1/python-engines
```

**MCP tools:** `web_ui_open`, `web_ui_sense`, `web_ui_act`, `web_ui_browse`, `web_ui_fetch`, `python_engine`, `python_engines_list`

```bash
# stdio MCP
PYTHONPATH=src python -m pocket.mcp_server
# tools/call → mail_inbox | web_ui_browse | python_engine
```

SMTP env:

```
POCKET_SMTP_HOST=
POCKET_SMTP_PORT=587
POCKET_SMTP_USER=
POCKET_SMTP_PASSWORD=
POCKET_SMTP_FROM=
POCKET_SMTP_TLS=1
```

## Chat-end contract

When a chat/session ends, call:

```http
POST /v1/keep/end  {"session_id":"<session>"}
```

This marks the session closed, stops KEEP agents, and kills isolated browsers.

## Together

1. Open chat → `keep/start` with `session_id` + `with_browser:true`  
2. Mint `recall` if you may leave and come back  
3. Optionally mail the recall code via `mail/send` template `recall`  
4. Close chat → `keep/end`  

All of this is **this app (POCKET)** — self-hosted on your machine.
