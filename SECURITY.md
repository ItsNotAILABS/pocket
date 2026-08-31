# Security Policy — POCKET Alpha

POCKET Host is the identity, tenancy, routing, governance and product-control plane for the POCKET family. Its security boundary is broader than any individual agent or voice service.

## Core security principles

- Authenticate before privileged mutation.
- Authorize against explicit user/org/device/agent scope.
- Preserve tenant identity through every downstream request.
- Keep secrets server-side and out of client bundles, receipts and logs.
- Treat local founder/operator authority separately from hosted organization roles.
- Prefer explicit deny behavior over implicit fallback.
- Record bounded audit evidence for privileged actions.

## Tenant isolation

Organization members, local market users, paired devices, agent sessions, artifacts, receipts and cloud tasks must remain scoped to the owning principal/tenant. A valid identifier alone must never grant cross-tenant access.

## Device pairing

Paired devices should receive restricted device/service credentials rather than founder or owner sessions. Pairing, revocation and credential expiration are separate lifecycle operations and should be auditable.

## Execution boundary

POCKET Host decides whether an action may be routed. POCKET Agent executes long-running work. Pocket Voice handles conversational timing and voice context. Host policy must not be bypassed by calling an internal execution surface directly in a hosted deployment.

## Secrets and credentials

- Do not commit Cloudflare, provider, signing, bootstrap, release-admin or customer credentials.
- Production secrets belong in the deployment platform's secret store.
- API/service keys should be scoped and revocable.
- Logs and receipts must redact authentication material.

## Audit and receipts

Privileged actions should produce structured evidence containing request ID, actor/principal, tenant/org, action, target, result, timestamp and relevant digest/version metadata. Do not store private chain-of-thought or unnecessary customer payloads as audit evidence.

## Vulnerability reporting

Do not disclose exploitable vulnerabilities through public issues. Contact maintainers privately through the organization’s available security/contact channel with affected version, prerequisites, reproduction, impact and a minimal proof-of-concept.

## Alpha truth boundary

POCKET Alpha does not claim SOC 2, ISO 27001, FedRAMP, HIPAA eligibility, PCI DSS, formal penetration testing, or third-party security certification. Deployment-specific evidence is required for any compliance or certification claim.
