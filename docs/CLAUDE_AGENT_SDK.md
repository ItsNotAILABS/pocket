# Claude Agent SDK in POCKET

POCKET’s **Claude** desk agent prefers the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) (`claude-agent-sdk`) — the same autonomous tool loop as Claude Code — and falls back to the `claude` CLI if needed.

## What you get

| Piece | Behavior |
|-------|----------|
| **Agent loop** | Claude plans → calls tools → reads results → repeats |
| **Tools** | Read, Write, Edit, Glob, Grep, (+ Bash by default) |
| **Streaming** | Partial text + tool lines land in the desk transcript (iMessage bubbles) |
| **Sandbox receipts** | Each tool event writes under `~/.pocket/sandbox/receipts/` (profile `claude_agent`) |
| **Fallback** | Classic `claude -p` CLI, then Codex if nothing Claude-related is available |

## Install

```bash
pip install claude-agent-sdk
# Auth (one of):
#   set ANTHROPIC_API_KEY=...
#   or install/login Claude Code CLI (`claude`)
```

## Desk use

1. Open `http://127.0.0.1:8787/desk`
2. Pick **Claude** (Agent SDK · tools)
3. Send a coding task — watch stream + final bubble

## Env flags

| Variable | Default | Meaning |
|----------|---------|---------|
| `POCKET_CLAUDE_SDK` | `1` | Use SDK first; set `0` / `cli` to force CLI |
| `POCKET_CLAUDE_BASH` | `1` | Allow Bash tool in the SDK loop |
| `ANTHROPIC_API_KEY` | — | SDK / Claude API auth |

## Code map

- `pocket/claude_agent_bridge.py` — SDK query loop, stream, receipts  
- `pocket/executor.py` → `_run_claude` — prefers bridge, then CLI  
- `pocket/agent_sandbox.py` — profile `claude_agent`  

## Status check

```python
from pocket.claude_agent_bridge import status
print(status())
# {'sdk_installed': True, 'auth': True/False, 'cli': True/False, 'ready': ...}
```
