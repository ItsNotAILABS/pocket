# POCKET / MESIE Agent Protocols

Live toolkit: `GET /v1/agents/tools` · [docs/AGENTS_MCP_TOOLS.md](docs/AGENTS_MCP_TOOLS.md) · PhoneAI sessions: `POST /v1/phoneai/sessions`. Architecture plane: `GET /v1/agents/arch` · `POST /v1/agents/turn`. Think first via `pocket.agent_runtime.route_think` — one engine, at most one tool.

### Agent architecture (do not fork)

```text
identity → seat → route → authority → execute → receipt
```

Desk, PhoneAI, RAH, and invoke share `pocket.agent_arch`. Execute leaves stay where they are (`work_harness`, `rah`, `agent_invoke`). Do not add a parallel agent OS. RAH execute still needs a WorkGrant.

This repository is a multi-agent workstation and enterprise control plane. Treat this `AGENTS.md` as the local operating contract for every AI, coding agent, cloud agent, desktop agent, voice agent, and human operator working in POCKET.

POCKET is not a single-chat project. Multiple AIs may be working here at the same time. Every agent must assume concurrent work, preserve evidence, avoid destructive edits, and leave machine-readable traces for the next agent.

## 0. Operating identity

```text
System: POCKET
Lane: MESIE + POCKET
Role: multi-agent workstation / control plane / enterprise operator shell
Primary doctrine: mesh-first coordination, receipt-bearing work, policy-bound execution
```

POCKET coordinates people, devices, tools, voice, APIs, local models, cloud account state, and agent work. MESIE is the compute/evaluation lane used when work requires benchmarking, measurement, model/runtime evaluation, transformation, or reproducible evidence.

## 1. Non-negotiable rules

1. Never assume you are the only AI working in this repository.
2. Do not rewrite broad surfaces without first narrowing the target and preserving current behavior.
3. Do not delete files, rename files, or collapse protocols unless the task explicitly requires it.
4. Prefer additive protocol, adapter, test, and documentation changes over sweeping rewrites.
5. Preserve POCKET's product frame: desktop, edge, cloud account, teams, policy, devices, agents, voice, and APIs.
6. Preserve MESIE's evidence frame: evaluation, receipts, measurement, reproducibility, and bounded experiments.
7. Do not commit secrets, API keys, tokens, seed phrases, private keys, customer credentials, raw card data, or hidden production endpoints.
8. Any privileged action must route through policy, approval, audit, and receipt surfaces.
9. Any finance, identity, device, messaging, or external connector change must state whether it is local, sandbox, testnet, simulated, or production-bound.
10. A task is not done until the next agent can understand what changed, why, and how to verify it.

## 2. Multi-AI coordination model

Assume these AI classes may be active:

| AI class | Purpose | Expected outputs |
|---|---|---|
| Founder/operator agent | Turns Alfredo's intent into work packages | plans, decisions, acceptance notes |
| Coding agent | Edits code and tests | branches, PRs, patches, validators |
| Research agent | Converts docs/web/source material into grounded summaries | cited notes, research docs, assumptions |
| MESIE evaluator | Runs or defines measurement/evaluation loops | benchmarks, receipts, scorecards |
| Pocket UI agent | Improves desk, voice, mail, work, and install surfaces | UI patches, routes, screenshots, UX notes |
| Policy/security agent | Checks boundaries, secrets, permissions, and approvals | deny/allow/confirm decisions, risk notes |
| Release agent | Packages, verifies, and documents ship state | release notes, manifests, build receipts |
| Memory/continuity agent | Preserves doctrine and context across turns/repos | protocol notes, maps, changelog entries |

When in doubt, write in a way that another agent can pick up the work without chat history.

## 3. Mesh-first protocol

POCKET already frames itself around a subagent mesh. Use that doctrine by default.

```text
Protocol ID: MEDINA-SUBAGENT-MESH/1.0
Alias: MSMP-1.0
Default posture: mesh-first, transcript-second
```

### MSMP rules

1. Treat the chat transcript as intake, not durable shared state.
2. Put durable work in files, tests, receipts, docs, manifests, and PR descriptions.
3. Use agent-specific notes when work spans more than one step.
4. Leave explicit handoff markers when a task is incomplete.
5. Do not hide important state in a final response only.
6. Prefer signed, hashed, or deterministic receipts for claims that affect releases, finance, identity, policy, devices, or external systems.

### Standard handoff marker

Use this block in docs, PRs, or issue comments when work remains:

```text
HANDOFF
Status: <done | partial | blocked>
Changed: <files or surfaces>
Verified: <commands or checks>
Blocked by: <missing access / failing test / missing secret / unknown>
Next agent: <recommended next action>
```

## 4. MESIE evidence protocol

MESIE work must be reproducible. Do not make performance, model, runtime, or production-readiness claims without evidence.

```text
Protocol ID: MESIE-EVIDENCE/1.0
Scope: evaluation, benchmark, runtime, model, receipt, release, and measurement work
```

### MESIE rules

1. Every benchmark must name its dataset/input, method, runtime, and limit.
2. Every generated receipt must include schema, timestamp, subject, inputs, outputs, and hash or deterministic identifier.
3. Never claim a model/runtime/test passed unless the command or evidence exists.
4. Separate source-derived facts, inference, and planned work.
5. Prefer small validators that can run in CI over vague claims in docs.
6. Store receipts under a predictable path such as `dist/`, `receipts/`, `evidence/`, or the product-specific artifact directory.

### MESIE receipt shape

```json
{
  "schema": "mesie.receipt.v1",
  "generated_at": "ISO-8601",
  "subject": "pocket.surface.or.test",
  "mode": "local|sandbox|testnet|production-bound",
  "inputs": [],
  "outputs": [],
  "checks": [],
  "hash": "sha256:<digest>"
}
```

## 5. POCKET product protocol

```text
Protocol ID: POCKET-PRODUCT/1.0
Scope: desktop, edge, cloud account, local host, devices, voice, mail, work, docs, APIs, teams, policy
```

### Product rules

1. Preserve the control-plane architecture: identity, organization, RBAC, policy, approvals, quotas, idempotency, audit, incidents, secret references, dependency health, and release state.
2. Local agent actions must remain bounded by policy and explicit user/operator intent.
3. Cloud account work must distinguish tenant state from local device state.
4. Device and voice surfaces must not silently escalate permissions.
5. API surfaces must have stable versioned paths and deterministic error shapes.
6. UI additions must have clear route ownership and not break core surfaces such as `/desk`, `/work`, `/mail`, `/docs`, `/health`, `/v1/catalog`, and `/v1/ready`.
7. Prefer capability discovery over hard-coded assumptions.

## 6. Policy and safety protocol

```text
Protocol ID: POCKET-POLICY/1.0
Default decision modes: allow, deny, confirm
```

Require `confirm` or stronger review for:

- production deploys;
- token or secret configuration;
- user data export;
- billing, payments, wallet, finance, or entitlement changes;
- destructive filesystem operations;
- device control;
- external messaging on behalf of a user;
- changes to policy, auth, RBAC, tenant isolation, or audit trails.

Deny by default when a task asks for:

- secrets in source control;
- bypassing auth or rate limits;
- hidden exfiltration;
- silent production money movement;
- raw card data storage;
- private key or seed phrase capture;
- unlogged privileged actions.

## 7. Repository work protocol

### Before editing

1. Identify the exact surface: docs, runtime, tests, UI, API, policy, release, or infrastructure.
2. Search for existing files before creating duplicates.
3. Prefer branch + PR workflow.
4. Keep changes small enough for another AI to review.

### While editing

1. Do not mix unrelated product lanes.
2. Keep protocol changes explicit and versioned.
3. Keep boundaries visible in code comments or docs when the surface touches finance, identity, devices, messaging, or external providers.
4. Add tests or a validator for new runtime behavior.
5. Do not silently relax tests to make a build pass.

### Before reporting done

Report:

```text
Changed: <files>
Verified: <commands/checks or not run>
Merged: <yes/no>
Open risk: <if any>
Next: <one next action>
```

## 8. Naming and file conventions

Use these names unless a local directory already defines a stronger convention:

```text
AGENTS.md                         repository-wide AI protocol
README.md                         product overview
/docs                             operator and architecture documentation
/docs/research                    research-grade doctrine and long-form protocols
/src or /pocket                   runtime code
/tests                            test files
/dist or /receipts                generated receipts and validation artifacts
/ecosystem.surface.json           ecosystem declarations
```

Recommended protocol file naming:

```text
POCKET_<SURFACE>_PROTOCOL.md
MESIE_<SURFACE>_EVIDENCE.md
<surface>.receipt.json
<surface>.manifest.json
```

## 9. Embedded protocol register

| Protocol | Version | Purpose |
|---|---:|---|
| `MEDINA-SUBAGENT-MESH` | 1.0 | Multi-agent mesh-first coordination |
| `MESIE-EVIDENCE` | 1.0 | Evaluation, benchmark, receipt, and reproducibility rules |
| `POCKET-PRODUCT` | 1.0 | Product surface and control-plane rules |
| `POCKET-POLICY` | 1.0 | Allow/deny/confirm policy posture |
| `POCKET-HANDOFF` | 1.0 | How agents leave work for other agents |
| `POCKET-SECRET-REF` | 1.0 | Secrets are references, never source-controlled values |
| `POCKET-RELEASE` | 1.0 | Release claims require evidence and receipt trail |

## 10. Pocket-aware final response style

When reporting to the operator, be direct:

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

Do not claim CI, tests, deploys, merges, or production status unless tool output proves it.

## 11. Current doctrine summary

POCKET is the operator envelope. MESIE is the evidence engine. NEXUS is the federation layer. Agents are not prompt costumes; they are bounded workers that should leave artifacts, receipts, and handoffs. Multiple AIs can work here at once, so every change must be legible, scoped, auditable, and safe for concurrent continuation.
