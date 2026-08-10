# Voice for agents inside POCKET

How [Pocket Voice](https://github.com/ItsNotAILABS/pocket-voice-to-text) helps **agents**, without ambient host power.

## Agent jobs that get better with voice

| Job | Voice piece | Cap required |
|-----|-------------|--------------|
| Pair coding while Codex runs | STT dictate + coding commands | browser mic only |
| Spoken job status | TTS “tests passed” | browser / optional API |
| Support seat on phone | business mode + personality | `voice:api` → localhost:8790 |
| Sales demo | sales personality | `voice:api` |
| Mesh worker status | TTS or text→voice hint | optional |

## Sandbox profile: `voice_plugin`

From `agent_sandbox`:

- Caps: `compute`, `clock`, `voice:api`
- **No** filesystem, **no** shell, **no** desktop  
- Net hosts: `127.0.0.1`, `localhost` only  

So an agent can call Pocket Voice HTTP API without opening the founder disk.

```http
POST /v1/sandbox/voice
{ "text": "I need a refund", "business_mode": "customer_service", "profile": "voice_plugin" }
```

Under the hood: grant check → `http://127.0.0.1:8790/v1/turn` → receipt.

## Start voice API next to POCKET

```powershell
cd C:\Users\Medin\OneDrive\pocket-voice-to-text
npm start
# :8790
```

POCKET host: `:8787` (desk). Voice: `:8790` (friends + agents).

## Future: Wasm guest tools that speak

Untrusted tool modules run under `untrusted` / `compute` profiles.  
If they need voice, they only get it if the **host** injects a typed import (capability), never by ambient scrape of the mic.

See: `docs/research/POCKET_AGENT_WASM_SANDBOX.md`
