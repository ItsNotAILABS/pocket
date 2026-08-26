# POCKET Beta Cloudflare Domain

## Canonical beta domain

```text
https://beta.pocketnova.app
```

The operator has already connected the POCKET beta route in Cloudflare. This repository now records the domain and route contract so future POCKET, MESIE, and Cloudflare work can reference the same canonical beta surface.

## Git-owned contract

```text
deploy/cloudflare/pocket-beta-domain.json
```

This file records:

- canonical beta host: `beta.pocketnova.app`;
- canonical beta origin: `https://beta.pocketnova.app`;
- expected Cloudflare route pattern: `beta.pocketnova.app/*`;
- public POCKET beta routes;
- required Cloudflare secret references;
- explicit boundary flags.

## Route posture

```text
Cloudflare zone: pocketnova.app
Beta host: beta.pocketnova.app
Route pattern: beta.pocketnova.app/*
Target: pocket-beta
Mode: Cloudflare Worker or Pages project
Status: operator-connected
```

The repo records the route target as `operator-managed` because actual Cloudflare project IDs, route IDs, account IDs, deploy hooks, API tokens, and zone IDs must not be committed to git.

## Public beta routes

The beta domain should expose the same POCKET product surfaces documented in the README:

```text
/
/desk
/work
/mail
/docs
/install
/get
/developers
/health
/v1/catalog
/v1/ready
/v1/class
```

## Required secret references

These are references only. Do not commit actual values.

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Optional references:

```text
CLOUDFLARE_ZONE_ID
CLOUDFLARE_PAGES_DEPLOY_HOOK
POCKET_BETA_TOKEN
```

## Validator

Run:

```bash
python scripts/validate_pocket_beta_domain.py
```

Expected output:

```text
dist/pocket-beta-domain/validation-receipt.json
```

The validator checks that:

- the domain contract exists;
- `beta.pocketnova.app` is the canonical host;
- `https://beta.pocketnova.app` is the canonical origin;
- `beta.pocketnova.app/*` is declared as the Cloudflare route;
- the expected beta product routes are declared;
- Cloudflare secret references exist without raw secret values;
- boundary flags prevent secrets, production overclaiming, customer data export, and payment/wallet execution claims.

## Boundary

This commit does not deploy Cloudflare and does not claim the route is live from CI. It records the operator-provided domain/route contract in git and gives future agents a validator so POCKET beta domain work does not drift.

```text
No secrets in git
No raw Cloudflare tokens in git
No production claim
No customer data export
No payment or wallet execution
Beta route only
```

## Handoff

```text
HANDOFF
Status: domain contract recorded
Changed: deploy/cloudflare/pocket-beta-domain.json, scripts/validate_pocket_beta_domain.py, docs/POCKET_BETA_CLOUDFLARE_DOMAIN.md
Verified: validator script added; run locally or in CI with python scripts/validate_pocket_beta_domain.py
Blocked by: no Cloudflare API call made from this commit
Next agent: wire validator into CI and, separately, deploy/update Cloudflare using operator-managed secrets
```
