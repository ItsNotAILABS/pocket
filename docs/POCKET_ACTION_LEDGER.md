# POCKET Action Ledger

POCKET now has an executable action ledger for real agentic work and restricted task paths.

This is not another prose-only protocol. The ledger records explicit actions, evaluates policy requirements, writes receipts, exports machine-readable action history, and builds provider execution packets for payment and wallet workflows without guessing state.

## Runtime

```text
src/pocket/action_ledger.py
```

## Validator

```bash
python scripts/validate_pocket_action_ledger.py
```

Expected output:

```text
dist/pocket-action-ledger/validation-receipt.json
```

## What it executes

The ledger currently supports these action kinds:

```text
agent_task
production_claim
data_export
payment_execution
wallet_execution
```

## Core rule

POCKET does not infer restricted state. A restricted action is accepted only when it includes explicit evidence and operator approval.

Restricted actions:

```text
production_claim
data_export
payment_execution
wallet_execution
```

## Production claim contract

A production claim must include:

```text
deploy_target
verification_url_or_run_id
operator_assertion
operator approval
```

Without that, the ledger returns `confirm`, not `allow`.

## Data export contract

A data export must include:

```text
dataset_id
export_scope
destination
operator approval
```

The runtime writes JSON and CSV exports plus an export receipt. The validator writes these under:

```text
dist/pocket-action-ledger/
```

## Payment execution contract

A payment execution must include:

```text
provider
provider_reference
amount
currency
operator approval
mode = provider_ready or production
```

Raw card data, CVV/CVC, or secret material is denied.

## Wallet execution contract

A wallet execution must include:

```text
provider
wallet_reference
network_or_rail
amount_or_asset
operator approval
mode = provider_ready or production
```

The runtime builds `pocket.provider_execution_packet.v1` packets for provider adapters. The packet stores references and hashes only. Provider credentials belong outside git.

## Decision model

```text
allow   = all policy and evidence requirements satisfied
confirm = restricted action is missing approval/evidence/mode
 deny   = raw secret, raw card, seed phrase, private key, or sensitive material detected
```

## Receipt model

Every recorded action emits:

```text
pocket.action_receipt.v1
```

Receipts include:

```text
action
decision
previous_hash
receipt_hash
```

This creates a chain that the next AI or operator can inspect without relying on chat history.

## What this changes

POCKET now has a concrete path for agentic task execution with receipts:

```text
agent request
-> PocketAction
-> policy decision
-> action receipt
-> optional data export
-> optional provider execution packet
```

## What this does not hide

This module does not silently claim a live deploy, payment, wallet transfer, export, or production status. It requires evidence and approval and then records the exact decision. That is the only acceptable path for restricted work.
