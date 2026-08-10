# How-to: API recipes

Base: `http://127.0.0.1:8787`  
Auth: `Authorization: Bearer <token>` when required (desk login).

## Catalog

```http
GET /v1/catalog
GET /v1/platform/coherent
GET /v1/protocols
GET /health
```

## Agent mail

```http
GET  /v1/agent-mail
GET  /v1/agent-mail/accounts
POST /v1/agent-mail/accounts  {"agent":"bot","name":"Bot"}
GET  /v1/agent-mail/inbox?agent=assist
POST /v1/agent-mail/send
{"from":"scribe","to":"assist","subject":"hi","body":"hello"}
POST /v1/agent-mail/read  {"agent":"assist","id":"am-…"}
```

## Genetic

```http
GET  /v1/internal-models
POST /v1/genetic/run  {"goal":"…","generations":2,"population":4}
POST /v1/internal-models/express  {"model":"ghost","goal":"phi 4"}
```

## Web UI + engines

```http
GET  /v1/web-ui
GET  /v1/python-engines
POST /v1/web-ui/browse  {"url":"https://example.com"}
POST /v1/web-ui/search  {"query":"…"}
POST /v1/python-engine  {"engine":"web_research","prompt":"…"}
```

## Skills

```http
POST /v1/skills/run
{"skill":"platform_map"}
{"skill":"mail_inbox","params":{"agent":"assist"}}
{"skill":"genetic_flow","prompt":"plan + hash"}
{"skill":"python_engine","params":{"engine":"ghost","prompt":"phi 2"}}
```

## Sessions

```http
POST /v1/sessions  {"mode":"assist","title":"Life"}
POST /v1/sessions/{id}/messages  {"text":"…"}
```

## Install slices

```http
GET /install
GET /v1/install/slices
```

## Python one-liners

```python
from pocket.platform_catalog import catalog
from pocket.agent_mail import send, inbox
from pocket.internal_models import run_genetic_flow
from pocket.web_ui_engine import run_python_engine
from pocket.mcp_bundle import invoke

catalog()["system_count"]
send(from_agent="scribe", to="assist", subject="ping", body="hi")
run_genetic_flow("hash and plan", generations=2)
run_python_engine("web_research", "edge agents")
invoke("pocket", "mail_accounts")
```
