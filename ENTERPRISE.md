# POCKET — Enterprise Alpha Architecture

POCKET is the product and governance plane around the wider POCKET family. Enterprise value lives here: organizations, users, devices, entitlements, policy, audit, deployment, managed integrations and support boundaries.

## Recommended enterprise topology

```text
Users / Teams / IDEs / Voice / Automation
                 |
                 v
            POCKET Host
 identity · orgs · RBAC · policy · audit
 devices · entitlements · routing · receipts
          /                   \
         v                     v
 Pocket Voice             POCKET Agent
 conversation             long-running
 control                  execution
```

## Enterprise control domains

### Identity and organization
- owner/admin/member/viewer or equivalent explicit roles;
- invite lifecycle and expiration;
- device/service identities separate from human sessions;
- revocation without requiring code changes.

### Authorization
- capability-based checks on privileged routes;
- tenant ownership validation on every referenced resource;
- separate founder/local operator authority from hosted customer authority;
- deny-by-default behavior for unknown or unsupported scopes.

### Data and artifacts
- explicit tenant namespaces;
- retention/export/delete behavior documented by artifact class;
- private user lanes separate from shared team lanes;
- receipts and audit events treated as governed artifacts.

### Execution
- POCKET Host authorizes and routes;
- POCKET Agent owns long-running work;
- capsules/sandboxes are explicit execution classes;
- cancel, timeout, quota and recovery controls remain available to the operator.

### Voice
- Pocket Voice owns turn timing, VAD/STT scaffolding and voice context;
- provider secrets stay in server-side broker boundaries;
- voice sessions inherit authenticated POCKET tenant/session identity.

### Deployment
- source merge, preview deployment and production promotion are separate evidence states;
- Cloudflare Worker rollback and D1/R2 data recovery are documented separately;
- production secrets are managed outside source control.

## Design-partner acceptance suite

An `alpha-enterprise` evaluation should cover:

1. organization create/join/invite/revoke lifecycle;
2. role escalation denial;
3. cross-tenant resource denial across sessions, artifacts, devices and receipts;
4. restricted paired-device credentials;
5. API key/service-account revocation;
6. host → voice request identity propagation;
7. host → agent request identity propagation;
8. governed execution denial receipt;
9. execution cancellation and recovery;
10. audit/request-ID correlation across services;
11. secret redaction in errors/logs/receipts;
12. preview → production promotion controls;
13. Worker rollback procedure;
14. D1/R2 backup/recovery procedure;
15. rate/quota enforcement;
16. export/delete behavior for customer-owned data;
17. dependency/provider failure behavior;
18. documented support and incident ownership.

## Commercial model

The family can preserve open runtimes while POCKET monetizes managed enterprise infrastructure: hosted organizations, policy, audit retention, deployment, observability, managed voice/realtime brokerage, usage metering, team collaboration, connectors, support and governed execution.

## Alpha limitation

This architecture describes the target enterprise operating contract. A feature is not considered proven solely because it appears in this document; each release must provide matching implementation and validation evidence.
