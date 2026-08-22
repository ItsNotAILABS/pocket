# POCKET Alpha Program

**Release channel:** Alpha  
**Audience:** technical founders, internal teams, design partners, and controlled enterprise evaluations.

POCKET Alpha is the coordinated pre-GA release train for the POCKET product family:

- **POCKET Host** — identity, tenancy, routing, governance, cloud account, desktop/edge surfaces, product APIs.
- **Pocket Voice** — patient turn-taking, voice/session control, Studio contracts, STT/VAD scaffolding, personas and voice context.
- **POCKET Agent** — long-running execution, RLM, continual harness, RAH, schedules, goals, capsules, execution receipts.

## Alpha operating principles

1. **No capability inflation.** Source, local tests, hosted previews, production deployment, and third-party validation are separate evidence states.
2. **Tenant boundaries are load-bearing.** User, organization, device, agent, session, artifact, and execution scopes must remain explicit through every hop.
3. **Provider-neutral contracts first.** Product logic should not depend on a single model, speech provider, cloud vendor, or client shell.
4. **Receipts over hidden state.** Execution surfaces emit bounded status, timestamps, hashes, provenance, and policy decisions—never private model reasoning.
5. **Governed execution.** Local execution, remote execution, capsules, and privileged tools must have distinct risk and authorization boundaries.
6. **Reversible releases.** Every Alpha feature needs a rollback path or an explicit statement when data changes are not reversible.
7. **Compatibility is tested across repos.** Family protocol changes require coordinated contract fixtures across POCKET Host, Pocket Voice, and POCKET Agent.

## Enterprise Alpha gates

| Gate | Requirement |
|---|---|
| Identity | authenticated principal and explicit tenant/org scope |
| Authorization | role/capability checks on privileged mutations |
| Isolation | no cross-tenant session, artifact, receipt, or device access |
| Secrets | server-side only; never embedded in browser bundles or public repos |
| Audit | request ID + actor + action + result + timestamp for privileged operations |
| Receipts | stable schema and hashable evidence for agent/execution operations |
| Rate limits | per tenant/key/device boundary where externally reachable |
| Recovery | code rollback + data recovery documented separately |
| Observability | health/readiness plus structured errors without secret leakage |
| API stability | versioned public contracts; incompatible changes require a new version |
| CI | syntax/import/tests plus family contract validation |
| Documentation | operator boundary, deployment, security, support and known limits |

## Alpha maturity labels

- `alpha-local` — reproducible local execution only.
- `alpha-preview` — deployed preview/staging evidence exists.
- `alpha-hosted` — controlled hosted environment exists; not GA/SLA-backed.
- `alpha-enterprise` — tenant, auth, audit, recovery and compatibility gates are satisfied for design-partner use.

No repository should claim `alpha-enterprise` solely because this document exists. Each repo must publish its own evidence receipt.

## Family protocol

Current shared envelopes:

- `pocket.family.v1`
- `pocket.context-snap.v1`
- `pocket.execution-receipt.v1`

The host owns principal/tenant routing. Voice owns conversational timing and voice context. Agent owns execution lifecycle. No repo should silently absorb another repo's responsibility.

## Release posture

Alpha is deliberately useful but explicit about limits. Design partners should be able to install, evaluate, integrate, report defects, and understand the security boundary without reading internal implementation history.
