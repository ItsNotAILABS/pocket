# POCKET Multi-AI Operations Runbook

This runbook converts the repository-level `AGENTS.md` doctrine into an operator workflow for multiple AIs working in POCKET at the same time.

## Operating posture

```text
POCKET = operator envelope and control plane
MESIE = evidence, benchmark, receipt, and evaluation lane
NEXUS = federation and tool/capability routing layer
Agents = bounded workers that leave artifacts and handoffs
```

The default is not one assistant holding everything in chat memory. The default is a mesh of workers that coordinate through files, manifests, receipts, tests, issues, PRs, channels, and handoff blocks.

## Daily multi-AI rhythm

### 1. Intake

Capture the operator request and classify it:

```text
docs/protocol
runtime/code
UI/product
policy/security
MESIE/evaluation
release/package
research/architecture
```

### 2. Claim a narrow surface

The active AI should name the files or directories it intends to touch. Avoid broad rewrites.

```text
Claimed surface: AGENTS.md + protocols + scripts
Do not touch: runtime routes, secrets, deploy configs
```

### 3. Create evidence

Any meaningful claim should have one of:

```text
test
validator
receipt
manifest
PR body
issue note
research doc with source citations
```

### 4. Leave a handoff

For incomplete work, use:

```text
HANDOFF
Status: partial
Changed: <files>
Verified: <commands>
Blocked by: <missing access/test/fact/secret>
Next agent: <next action>
```

## Conflict avoidance

Multiple AIs should avoid editing the same high-churn file at once. Prefer additive files under precise directories.

| Surface | Safer additive path |
|---|---|
| Repository-wide agent rules | `AGENTS.md`, then protocol manifest |
| Research doctrine | `docs/research/*` |
| Validation | `scripts/validate_*.py` or product-specific validators |
| Receipts | `dist/<surface>/validation-receipt.json` |
| Product plans | `docs/POCKET_*_PLAN.md` |
| Runtime adapters | narrow module under `src/` or `pocket/` |

## Validator workflow

Run the protocol validator after changing agent rules:

```bash
python scripts/validate_agents_protocol.py
```

Expected output:

```text
dist/agents-protocol/validation-receipt.json
```

The receipt should show:

```text
decision: pass
schema: mesie.receipt.v1
checks: protocol, manifest, safety, handoff, reporting contract
```

## Escalation rules

Require operator confirmation before:

```text
production deploy
secret configuration
external message send
device control
billing/payment/wallet change
auth/RBAC/policy change
destructive filesystem operation
release publication
```

Deny or stop when a request asks for:

```text
hard-coded secrets
private keys or seed phrases
raw card data storage
hidden exfiltration
unlogged privileged action
silent production money movement
bypassing auth or rate limits
```

## Final status format

Every AI should report in this shape:

```text
DONE / OPEN / BLOCKED
Repo:
Branch:
PR:
Changed:
Verified:
Not verified:
Next:
```

This makes POCKET legible when multiple AIs are operating at the same time.
