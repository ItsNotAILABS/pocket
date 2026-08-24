# POCKET Voice Reality + Model Mesh

POCKET Voice is an execution surface, not only a conversational UI.

## Voice Reality flow

```text
speech
  -> transcript
  -> pocket.voice-reality-envelope.v1
  -> agent/model routing
  -> approval when required
  -> POCKET mission/job runtime
  -> execution events
  -> verification
  -> artifacts + receipt
  -> spoken state summary
```

The Go control runtime lives at `cmd/pocket-envelope` and compiles/seals the canonical envelope. Python `pocket.voice_reality` uses that binary when installed and preserves the same contract with a Python fallback.

High-impact deploy/publish/ship requests enter `awaiting_confirmation`. A follow-up `confirm` can resume the pending operation; a cancellation discards it. Starting a long job reports `executing`, not `succeeded`.

## Production agent constellation

`pocket.agent_constellation` defines explicit roles:

- architect
- builder
- tester
- reviewer
- deployer
- researcher
- security
- model-router
- memory
- device
- voice

These are routing roles over the existing POCKET/NEXUS runtimes. Each role declares actions and what it must verify.

## Foundation/model lanes

`pocket.model_mesh` discovers and ranks local, open-source and account/free-usage CLI lanes. Current registered lanes include:

- Ollama
- llama.cpp
- LM Studio
- OpenCode
- Aider
- Gemini CLI
- Qwen Code
- Codex CLI
- Claude Code CLI
- Grok CLI
- Continue CLI
- Goose
- OpenHands

POCKET prefers local/free-capable lanes when the requested capability matches. Authentication remains in each CLI's existing host session; POCKET does not copy provider credentials into the mesh.

Stable bounded headless adapters are implemented in `pocket.model_cli_exec` for Gemini CLI, Qwen Code, OpenCode and Ollama. Other lanes remain discoverable until their installed version exposes a compatible noninteractive contract.

## Verification

```bash
go test ./...
PYTHONPATH=src python -m pytest -q tests/test_model_mesh.py tests/test_voice_reality.py
PYTHONPATH=src python -m py_compile src/pocket/model_mesh.py src/pocket/model_cli_exec.py src/pocket/agent_constellation.py src/pocket/voice_reality.py
```

The POCKET Product Gate runs these checks on pull requests and `main` pushes.
