# POCKET LOOMGRAPH

**System name:** LOOMGRAPH  
**Protocol:** `POCKET-LOOMGRAPH/1.0`  
**Tagline:** *See the graph. Run the loop. Ship with Pocket.*

## Why it exists

Generic agent “harnesses” are opaque prompt piles.  
**LOOMGRAPH** is a **Loop-Orchestrated Multi-agent Graph Runtime**:

1. **Graph** — every multi-step job is a directed graph people can *see* (Mermaid + ASCII).
2. **Loop** — an outer control loop walks nodes: sense → plan → act → verify → loop/done.
3. **Pocket** — nodes call real host tech (skills, Creative Studio, Product Studio, integrations, community).

This is the **default forever** orchestration model for:

- Grok / coding agents on the desk  
- Skills (`loomgraph_run`)  
- HTTP automations  
- Humans at `/loomgraph`

## Playbook graphs

| id | Name | Use when |
|----|------|----------|
| `default` | Default ship loop | General multi-step |
| `creative_ship` | Creative → optional Community | Blog / social / captions + intentional share |
| `integration_open` | Integration execute | Discord / Slack / desktop apps |
| `studio_viral` | Studio viral loop | Storyboard · captions · optional ship |
| `code_assist` | Code assist loop | Tools plan + skill run |

Auto-pick from the goal text if `graph_id` omitted.

## API

```http
GET  /v1/loomgraph
GET  /v1/loomgraph/mermaid/{graph_id}
GET  /v1/loomgraph/graph/{graph_id}
POST /v1/loomgraph/run
     {"goal":"write social pack for LOOMGRAPH","graph_id":"creative_ship"}
GET  /v1/loomgraph/runs
GET  /v1/loomgraph/live
GET  /v1/loomgraph/self_test
```

UI: **`/loomgraph`**

## Skills

- `loomgraph_run` — execute a graph loop  
- `loomgraph_catalog` — list playbooks  
- `loomgraph_mermaid` — diagram only  
- `loomgraph_status` — live + recent runs  

## Doctrine

- Graphs for understanding  
- Loops for completion  
- Pocket skills for execution  
- Receipts for truth  
- Community share is **opt-in only**

## Receipt shape

Every run returns:

- `path` — node ids walked (`sense → plan → act → verify → done`)  
- `steps` — per-node ok / ms / result  
- `mermaid` — flowchart with path comment  
- `ascii` — terminal view  
- `id` — `lg-…` receipt under `~/.pocket/loomgraph/runs/`

## Forever default

Injected into:

- `platform_brief` / agentic harness  
- `enrich_prompt` for **all** chat agents  
- Desk/tool rules when you say “loomgraph”, “graph loop”, “orchestrate”

Do not replace LOOMGRAPH with an opaque chain. Extend **graphs**, not silent glue.
