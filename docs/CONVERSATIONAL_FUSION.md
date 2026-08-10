# Conversational Fusion (voice metadata → POCKET Deep Fusion)

**Doctrine:** Public [pocket-voice-to-text](https://github.com/ItsNotAILABS/pocket-voice-to-text) stays clean (patient VAD, multi-personality, cross-domain buffer, **metadata emitter**). Industry Deep Fusion, DFW priors, and recovery routing live in the **POCKET host**.

Same mental model as visual Fusion-Sense: normalize → fuse → act.

## Metadata schema (`pocket.voice.fusion_metadata.v1`)

Voice stack emits on every turn / decide:

| Block | Fields |
|-------|--------|
| `acoustic` | stress, speaking_rate, energy_mean/var, pause_pattern, speech_active_ratio |
| `linguistic` | transcript, incomplete/complete, entities, entity_density, trailing_cues |
| `turn` | scenario, threshold_ms, silence_ms, decision |
| `domain` | active_expert, candidate_experts, confidence, industry |
| `context_buffer` | flat airport/hotel/transit/dining facts |
| `session` | history_length, dominant_domain, user_state |

### Voice API (OSS)

- `POST /v1/turn` → response includes `fusion`
- `POST /v1/turn/decide` → includes `fusion`
- `POST /v1/fusion/metadata` → build vector only

## POCKET Fusion (`pocket.conversational_fusion.v1`)

| Route | Role |
|-------|------|
| `GET /v1/fusion/voice` | Schema + DFW experts |
| `POST /v1/fusion/voice` | Fuse metadata → expert weights, patience, preload, prompt_boost |
| `GET /v1/fusion/voice/last?session_id=` | Last result for a session |

### Outputs

- `primary_expert` / `expert_weights` — soft multi-expert blend
- `patience_delta_ms` + `listening` — callback into voice stack
- `preload_context` / `fusion_apply.context_puts` — buffer facts
- `prompt_boost` — multi-domain reply guidance
- `pattern` — e.g. `flight_disruption_recovery`

## DFW vertical (start narrow)

Airlines/gates/bags/delays ↔ airport lodging ↔ shuttles ↔ dining ↔ call-center recovery.

Example stressed traveler:

1. Voice keeps listening (`semantic_incomplete` + patient threshold).
2. Metadata shows rising stress + airport domain + incomplete.
3. POCKET Fusion boosts `airport_guide` + `hotel_host`, raises patience, preloads delay→hotel hold.
4. Final turn fuses both domains into one coherent reply without re-explain.

## Code

| Layer | Path |
|-------|------|
| Metadata emitter | `pocket-voice-to-text/src/turn-detection.js` (`buildFusionMetadata`) |
| Engine attach | `pocket-voice-to-text/src/engine.js` |
| Host fusion | `pocket-os/src/pocket/conversational_fusion.py` |
| Voice agent path | `executor._run_voice_agent` (pre + post fuse) |
