# Coding Swarm + Pixel Memory (POCKET 2.3)

## Coding Swarm harness

Multi-agent coding flow (like a multi-persona desk: **Sophia · Solver · Twin**).

| Agent | Role | Preferred AI versions (bound at runtime) |
|-------|------|------------------------------------------|
| **Sophia Chen** | Systems Architect | claude → plan → grok |
| **Master Solver** | Implementation | codex → grok → claude |
| **Auro Twin** | Ops / telemetry | plan → grok → claude |

Each turn:
1. Runs on the best **available** in-POCKET engine for that agent  
2. Falls back to high-quality **local templates** if CLI/SDK offline  
3. **Saves artifacts** into pixel lattice (`artifacts/{run}/{agent}/…`)  

### Desk

1. Open **Coding Swarm** (or **Swarm** with a coding prompt)  
2. Example: `solver sophia Write a TypeScript module for pixel synapse index`  
3. Watch multi-agent transcript + code snippets  
4. Open **Workspace → Pixel memory · artifacts**

Mentions: `@sophia` `@solver` `@twin` (or bare names). Default pipeline = all three.

## Pixel memory (first-class agentic)

| Action | What |
|--------|------|
| **Store** | Manual note or auto from every finished agent job |
| **Look** | Open symbol text + pixel map |
| **Search** | Find by name / preview / tags |
| **Recreate** | Export original file + envelope |
| **Pass** | To context / agent / device / clipboard |
| **Artifacts** | List agent-generated artifacts only |
| **Bring back** | Pull pixel content into the composer |

### APIs

- `GET /v1/vmem` — lattice status  
- `GET /v1/vmem/artifacts` — agent artifacts  
- `POST /v1/vmem/artifact` — put artifact  
- `POST /v1/vmem/bring-back` — look + payload  
- `GET /v1/swarm` — roster + bound AI versions  

All agent jobs (worker finish) also call `store_agent_run` so **every run can be looked up as pixels**.
