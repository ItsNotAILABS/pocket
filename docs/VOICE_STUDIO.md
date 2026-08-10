# Voice-to-Voice Agent Studio

**Product home:** `http://127.0.0.1:8787/studio/voice`  
**Desk tab:** Voice Studio (in-app)  
**Code:** `pocket/voice_studio_ui.py`  
**Skill:** `voice_studio_open`

## Paper → product map

The research paper *Ultra-Low-Latency Multi-Sensory Voice-to-Voice Agent Studio* describes an ideal architecture. **Where it is implemented for us:**

| Paper component | Status | Location |
|-----------------|--------|----------|
| 60fps canvas · 5 styles · emerald/indigo | **Shipped (UI)** | `/studio/voice` canvas engine |
| Persona × mindset matrix | **Shipped** | Voice Studio selectors → session meta + system boost |
| Code-to-Voice context snap | **Shipped (AST-lite)** | Snap buffer → next turn prompt |
| Patient VAD / turn machine | **Shipped (OSS)** | `pocket-voice-to-text` turn-detection + STT |
| Multi-personality | **Shipped** | `personalities.js` · Aria · desk/phone |
| Conversational Fusion | **Shipped (POCKET)** | `conversational_fusion.py` · `/v1/fusion/voice` |
| Dual PCM 16k/24k AudioWorklet | **Targeted / partial** | Telemetry labels; browser path uses Web Speech today |
| Native multimodal RTT &lt;140ms | **Not yet** | Needs realtime duplex engine; studio measures cascade turn RTT |
| Monaco full AST | **AST-lite** | Text buffer + function harvest (Monaco optional later) |

## Useful loop (today)

1. Open **Voice Studio** (desk tab or `/studio/voice`).  
2. Pick **persona** + **mindset** + canvas style.  
3. **Snap code** into the agent buffer.  
4. **Talk** or type — turn runs `mode=voice` + Fusion.  
5. Canvas shows user (emerald) vs agent (indigo); RTT shows turn latency.

## Related surfaces (same platform)

- Desk **Aria** / **Working**  
- **Phone** Aria first-class  
- `GET /v1/platform/coherent`  
- OSS: https://github.com/ItsNotAILABS/pocket-voice-to-text  
