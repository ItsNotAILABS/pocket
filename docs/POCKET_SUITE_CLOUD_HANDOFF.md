# POCKET Suite Cloud Handoff

Canonical beta URL:

```text
https://beta.pocketnova.app
```

This handoff makes the POCKET suite deployable as four coordinated surfaces:

```text
Pocket Platform  -> control plane, routes, action ledger, SDK, beta host
Pocket App       -> web showcase, desk/work/docs/install entry
Voice Pocket     -> speech-to-task and transcript receipt surface
Agent Pocket     -> task execution, policy decision, result receipt surface
```

## Give this to Claude / Cloud / Cloudflare deploy agent

```text
Deploy the POCKET suite beta using ItsNotAILABS/pocket as the platform source.
Use https://beta.pocketnova.app as the canonical beta host.
Mount web/pocket-suite/index.html as the beta showcase.
Expose sdk/pocket-suite-client.js as the browser SDK.
Preserve the action ledger contract for agent_task, production_claim, data_export, payment_execution, and wallet_execution.
Do not infer production state. Only show production status from explicit deployment receipts or verification evidence.
Do not commit or print Cloudflare secrets, payment credentials, wallet private keys, seed phrases, raw card data, CVC/CVV, or customer exports.
```

## Files added

```text
deploy/cloudflare/pocket-suite-handoff.json
web/pocket-suite/index.html
sdk/pocket-suite-client.js
scripts/validate_pocket_suite_handoff.py
```

## SDK links after deploy

```text
https://beta.pocketnova.app/sdk/pocket-suite-client.js
https://beta.pocketnova.app/web/pocket-suite/index.html
```

## Local validation

```bash
python scripts/validate_pocket_suite_handoff.py
```

Receipt:

```text
dist/pocket-suite-handoff/validation-receipt.json
```

## Production posture

The suite can execute production-shaped actions only through explicit action contracts. Claims, data exports, payments, and wallet actions must be bound to operator approval and receipts. The app must not infer a production deployment, export, payment, or wallet execution from a chat message alone.
