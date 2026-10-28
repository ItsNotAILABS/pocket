# Nebius / Nemotron lane — POCKET personal-AI increment

Built 2026-10-28 (Wed) for the Nebius × NVIDIA Global AI Hackathon,
**Personal AI** track, on branch `nebius-nemotron-lane`. Not merged, not
deployed; the live POCKET host on :8787 is untouched until the owner merges
and restarts it himself.

## What this is

An additive reasoning lane that serves an **NVIDIA Nemotron** model from
**Nebius Token Factory** (OpenAI-compatible API,
`https://api.tokenfactory.nebius.com/v1`) as the brain for one existing
POCKET personal-AI surface: the **memory-grounded brief** and the
**approval explainer**.

Everything else about POCKET is unchanged: local Auro models keep their
lanes, Medina Memory stays the store, and the agentic-approval layer keeps
its rule — agents propose, the human decides with a short code. This lane
explains and summarizes; it cannot approve, deny, or issue anything.

## Files

| File | Role |
|---|---|
| `src/pocket/nebius_api.py` | Token Factory client (config/status/save/models/chat/ping), mirroring `pocket.spark_api` conventions. Schema `pocket.nebius.v1`. |
| `src/pocket/nebius_brief.py` | The ported surface: `daily_brief()` + `explain_approval()` with strict grounding prompts and a labeled local fallback. |
| `src/pocket/server.py` | Routes: `GET /v1/nebius` (status), `POST /v1/nebius/chat`, `POST /v1/nebius/brief`, `POST /v1/nebius/explain` (+ `/api/...` aliases), adjacent to the Spark routes. |
| `tests/test_nebius_api.py` | Config seam, key gate, env override, and wire format against a **local mock** Token Factory server. |
| `tests/test_nebius_brief.py` | Grounding (facts reach the prompt verbatim), fallback honesty, failure degradation, approval boundary. |
| `nebius.env.example` | The env seam, documented; the filled values never live in the tree. |

## The key seam (the one remaining gate)

The lane is key-gated by design (POCKET-SECRET-REF: secrets are references,
never source-controlled values). The account owner creates the key at
**tokenfactory.nebius.com**, then either:

```bash
# option A — env (preferred for the host service)
export NEBIUS_API_KEY=…        # created at tokenfactory.nebius.com
export NEBIUS_MODEL=nvidia/nemotron-3-nano-30b-a3b   # optional override

# option B — config file (0600, outside the git tree)
python3 -c "from pocket.nebius_api import save; print(save(api_key='…'))"
# writes ~/.pocket/nebius.json
```

Default model id in code is `nvidia/nemotron-3-nano-30b-a3b` (the catalog id
in Nebius's own Token Factory examples). **After the key lands, run
`pocket.nebius_api.models()` (GET /models) and set NEBIUS_MODEL to the exact
id the account serves** — the submission's "model as deployed" line comes
from that list, never from a guess. Then `pocket.nebius_api.ping()` proves
the live path end to end.

## Honest behavior without the key

- `chat()` / `models()` return `{"ok": false, "error": "Nebius API key not
  configured …"}` — deterministic refusal, zero network calls.
- `daily_brief()` / `explain_approval()` return a deterministic brief
  composed from the same grounded facts, labeled `engine="local-fallback"`
  with `fallback_reason="nebius-not-configured"` (or
  `"nebius-call-failed: …"` when a configured call fails). Nothing is ever
  presented as a model answer that a model did not write.

## Verification (2026-10-28)

```text
PYTHONPATH=src <venv python> -m pytest \
  tests/test_nebius_api.py tests/test_nebius_brief.py \
  tests/test_spark_api.py tests/test_agent_approval.py -q
→ 27 passed
```

What that proves: config file/env seam, key-prefix-only status, the key
gate, the exact OpenAI-compatible wire format (Bearer header, payload,
response parsing, /models listing, HTTP-error surfacing) against a local
mock server, grounding of the brief surface, and fallback honesty.
What it does **not** prove: anything about the real Token Factory — latency,
the account's actual model catalog, or response quality. Those exist only
after the owner's key lands; see the gate above.

## HANDOFF

```text
HANDOFF
Status: partial (key-gated)
Changed: src/pocket/nebius_api.py, src/pocket/nebius_brief.py,
  src/pocket/server.py (4 routes), tests/test_nebius_api.py,
  tests/test_nebius_brief.py, docs/NEBIUS_NEMOTRON_LANE.md, nebius.env.example
Verified: 27/27 pytest (new lane + spark + approval neighbors); py_compile clean
Blocked by: NEBIUS_API_KEY — account creation at tokenfactory.nebius.com is
  the owner's step (no agent sign-ups, per standing rule)
Next agent: once the key exists → models() to pin the exact Nemotron id,
  ping() for the live receipt, then fill the submission draft's model name
  and demo URL from real output only.
```
