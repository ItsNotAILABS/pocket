# POCKET how-to index

Practical recipes. Full map: [INDEX.md](INDEX.md) · Live: `GET /v1/catalog` · Hub: `/docs`

---

## By task

| I want to… | Guide |
|------------|--------|
| Run the host and open desk | [how-to/DESK.md](how-to/DESK.md) |
| Give agents their own email + read inboxes | [how-to/AGENT_MAIL.md](how-to/AGENT_MAIL.md) |
| Evolve which internal models run for a goal | [how-to/GENETIC_FLOW.md](how-to/GENETIC_FLOW.md) |
| Let models open/sense websites (Python) | [how-to/WEB_UI_ENGINES.md](how-to/WEB_UI_ENGINES.md) |
| Plug Grok/Claude/Cursor into host tools | [how-to/MCP.md](how-to/MCP.md) |
| One-line install SDK / skills / plug | [how-to/INSTALL.md](how-to/INSTALL.md) |
| Fan out full sub-harnesses | [how-to/RAH.md](how-to/RAH.md) |
| Life assistant / loops → desk | [how-to/WORK_STUDIO.md](how-to/WORK_STUDIO.md) |
| Pair phone | [how-to/PHONE.md](how-to/PHONE.md) |
| Copy-paste API recipes | [how-to/API_RECIPES.md](how-to/API_RECIPES.md) |
| **All MCP tools + 20 uses for agents** | [AGENTS_MCP_TOOLS.md](AGENTS_MCP_TOOLS.md) · `GET /v1/agents/tools` |

---

## 60-second recipes

### Agent → agent mail

```bash
curl -s -X POST http://127.0.0.1:8787/v1/agent-mail/send \
  -H "Content-Type: application/json" \
  -d "{\"from\":\"scribe\",\"to\":\"assist\",\"subject\":\"hi\",\"body\":\"from how-to\"}"

curl -s "http://127.0.0.1:8787/v1/agent-mail/inbox?agent=assist"
```

### Genetic flow

```bash
curl -s -X POST http://127.0.0.1:8787/v1/genetic/run \
  -H "Content-Type: application/json" \
  -d "{\"goal\":\"hash the plan and identity\",\"generations\":2,\"population\":4}"
```

### Website via Python engine

```bash
curl -s -X POST http://127.0.0.1:8787/v1/python-engine \
  -H "Content-Type: application/json" \
  -d "{\"engine\":\"web_research\",\"prompt\":\"POCKET agent OS\"}"
```

### MCP skill from any agent

```bash
curl -s -X POST http://127.0.0.1:8787/v1/skills/run \
  -H "Content-Type: application/json" \
  -d "{\"skill\":\"mail_accounts\"}"
```

### Desk mode genetic

Create session with `"mode":"genetic"` or pick **Genetic** on desk, then send a goal.

---

## Auth note

Most mutating routes need a seat Bearer token (desk login stores it).  
Public-ish GETs: `/health`, `/v1/catalog`, `/v1/agent-mail`, `/docs`, `/install`.
