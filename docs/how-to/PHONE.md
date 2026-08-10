# How-to: Phone

Surface: **http://127.0.0.1:8787/phone** (or tunnel URL)

## Pair

1. Desk → pair / phone surface → mint code  
2. Phone opens pair flow with code  
3. Same seat token powers phone agents  

```http
POST /v1/pair/mint   # or skill pair_mint
GET  /v1/pair/status
```

## Modes (aligned with desk)

Aria · Assistant · Working · Muse Spark · Auro · Plan · Codex · Grok · Web · Novae variants

## Tips

- Agents run on the **PC**, not the phone CPU  
- Never auto-pay from life ops  
- Pair for handoffs between phone and desk  
