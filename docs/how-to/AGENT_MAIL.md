# How-to: Agent Mail

**Our own** email for every POCKET agent — domain `agents.pocket.local`.  
Not Gmail. Local inboxes under `~/.pocket/agent_mail/`. External SMTP via POCKET MAIL when configured.

## Concepts

| Term | Meaning |
|------|---------|
| Account | `{id}@agents.pocket.local` with inbox + sent |
| Local send | Agent → agent (instant file delivery) |
| External send | `"external": true` → SMTP (`POCKET_SMTP_*`) |
| Draft | Official templates / never auto-send |

Default accounts: assist, codex, claude, grok, auro, muse_spark, voice, work, browser, genetic, archon, navigator, scribe, system.

## UI

Open **http://127.0.0.1:8787/mail** — list accounts, inbox, compose.

## Create an account

```http
POST /v1/agent-mail/accounts
{"agent":"mybot","name":"My Bot","blurb":"Custom agent"}
```

→ `mybot@agents.pocket.local`

## Send agent ↔ agent

```http
POST /v1/agent-mail/send
{
  "from": "scribe",
  "to": "assist",
  "subject": "Research pack ready",
  "body": "See pixel symbol artifacts/…"
}
```

## Read inbox

```http
GET /v1/agent-mail/inbox?agent=assist
POST /v1/agent-mail/read
{"agent":"assist","id":"am-…"}
```

## Skill / MCP

```json
{"skill":"mail_inbox","params":{"agent":"assist"}}
{"skill":"mail_send","params":{"from":"scribe","to":"codex","subject":"PR","body":"…"}}
{"skill":"mail_accounts"}
```

MCP: `invoke("pocket", "mail_send", from="scribe", to="assist", …)`

## Python

```python
from pocket.agent_mail import create_account, send, inbox, status

status()
create_account("research", name="Researcher")
send(from_agent="scribe", to="research", subject="hi", body="hello")
print(inbox("research"))
```

## External SMTP

Set env: `POCKET_SMTP_HOST`, `POCKET_SMTP_USER`, `POCKET_SMTP_PASSWORD`, `POCKET_SMTP_FROM`.

```http
POST /v1/agent-mail/send
{"from":"system","to":"you@example.com","subject":"Notice","body":"…","external":true}
```

Or official product mail: `POST /v1/mail/draft` · `POST /v1/mail/send`.

## Models

Engines can use mail:

```http
POST /v1/python-engine
{"engine":"scribe","prompt":"inbox","params":{"agent":"assist"}}
```
