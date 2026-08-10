# How-to: RAH (Recursive Agent Harnesses)

RAH fans out **full sub-harnesses** (own context + tools), not bare model calls. Expensive — use for independent parallel slices.

## When

- Audit every endpoint / package / protocol  
- Large migration across many files  
- Security fleet review  
- 4+ independent bullets  

## When not

- Hello / status  
- Single-file fix  
- Strict sequential chains  

## Run

```http
POST /v1/rah/run
{"task":"Assess and improve all 10 POCKET protocols for RAH readiness"}
```

```json
{"skill":"rah_run","prompt":"…"}
{"skill":"rah_plan","prompt":"…"}  // plan only
{"skill":"rah_status"}
```

Desk: mode `rah` when available.

State: `~/.pocket/rah/<run_id>/`  
Host can auto-detect RAH-fit (`POCKET_RAH_AUTO=1`).
