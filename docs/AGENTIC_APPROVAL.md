# POCKET-AGENTIC-APPROVAL/1.0

Status: implemented on branch `agentic-approval` (2026-09-22).
Implementation: `src/pocket/agent_approval.py` · CLI: `src/pocket/agent_approval_cli.py`
Tests: `tests/test_agent_approval.py` (11/11).

## What it is

A general authorization primitive: an untrusted surface (device, website,
app) that cannot prove identity shows a short-lived code; a trusted
approver — by default the owner's agent, acting from a trusted channel —
approves the EXACT code match; approval writes a persistent, revocable
binding (device/app → granted scope/capability). Approve-once.

```
surface --(shows code)--> human --(reads code)--> trusted agent
trusted agent --(approve exact code)--> POCKET --> binding persisted
surface --(presents device/app id)--> check() --> granted / denied
```

## Relation to POCKET-DEVICE-PAIR/1.0

Device-pair redeems a 6-digit LAN code with a WebAuthn ceremony into a
`portal_device` principal (visual only). Agentic approval keeps the same
posture — short code, 10-minute TTL, single-use, exact match, revocable
grant, file-backed JSON store — but redeems the code with an approver's
explicit decision into a scoped capability binding. It is an extension,
not a fork: `device_pair.py` is untouched, and a future device-pair flow
can issue through this service.

## Protocol rules

1. Codes: 6 chars, unambiguous alphabet (`ABCDEFGHJKMNPQRSTUVWXYZ23456789`),
   `secrets`-generated, 10-minute default TTL (configurable per request).
2. Exact match only. Comparison is `secrets.compare_digest` after
   documented normalization (strip whitespace, uppercase). Mismatch is a
   denial, never fuzzy, never a hint about which request it was close to.
3. Single-use: approving or denying consumes the request. Expired requests
   can never be approved (swept on every read).
4. Policy: each request carries `policy.approvers` (default
   `["owner-agent"]`) and `quorum` (1). `approve()` refuses approvers not on
   the allowlist. Future approvers (`human-confirm`, quorum > 1) extend the
   allowlist and quorum accounting; the match + receipt mechanics stay.
5. Bindings: `{device_id, app_id, scope, capability}` with `scope: "*"` as
   wildcard. `check()` returns granted only for live (non-revoked) bindings.
6. Audit: every issuance, approval, denial, and revocation writes a MESIE
   receipt (`mesie.receipt.v1`) under `~/.pocket/agent_approval/receipts/`.
   Receipts record `code_sha256`, never the raw code. `list` masks codes.

## Storage

`~/.pocket/agent_approval/` (`POCKET_AGENT_APPROVAL_HOME` overrides for tests):

- `requests.json` — request records (pending/approved/denied/expired)
- `bindings.json` — persistent bindings (revocable)
- `receipts/` — one MESIE receipt per event

Files are 0600, writes are atomic (tmp + rename).

## Agent interface

```
PYTHONPATH=src python -m pocket.agent_approval_cli issue --device ID --app ID \
    --scope SCOPE --capability CAP [--ttl 600] [--note TEXT]
PYTHONPATH=src python -m pocket.agent_approval_cli list        # codes masked
PYTHONPATH=src python -m pocket.agent_approval_cli approve --code XXXXXX
PYTHONPATH=src python -m pocket.agent_approval_cli deny --code XXXXXX --reason R
PYTHONPATH=src python -m pocket.agent_approval_cli revoke --device ID [--app ID]
PYTHONPATH=src python -m pocket.agent_approval_cli bindings
PYTHONPATH=src python -m pocket.agent_approval_cli check --device ID --app ID \
    --scope SCOPE [--capability CAP]
```

Chat-side wrapper: `~/workspace/skills/pocket-approvals/` (SKILL.md).

## Security notes

- The code is the only human check; the approver must match it carefully
  against the code the requester relays. Never approve on description alone.
- At scale, requests should carry device attestation so a random screen
  cannot social-engineer a code relay (open item, not implemented).
- This service grants capabilities; it does not authenticate the requester.
  The trust anchor is the approver's channel (the owner's agent in chat).

## HANDOFF

```text
HANDOFF
Status: done (service + CLI + tests + live e2e + docs)
Changed: src/pocket/agent_approval.py, src/pocket/agent_approval_cli.py,
         tests/test_agent_approval.py, docs/AGENTIC_APPROVAL.md,
         receipts/agentic-approval-e2e.receipt.json,
         ~/workspace/skills/pocket-approvals/
Verified: 11/11 unit tests; live e2e issue->list->approve->check(granted)->
          revoke->check(denied) via CLI on 2026-09-22
Blocked by: none
Next agent: (1) consider HTTP routes in server.py next to /v1/auth/device/*
            following the existing RBAC pattern; (2) device attestation on
            requests; (3) consumer migration (e.g. Photo Digest unlock) is a
            separate owner decision — do not migrate unasked.
```
