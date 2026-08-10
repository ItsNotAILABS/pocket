# How-to: Internal models · Genetic flow

**Doctrine:** internal models are **modules**. The **genetic flow** evolves which ones execute for a goal.

## Modules

| id | Role |
|----|------|
| ghost | Pure math / hash / phi (zero tokens) |
| world | World-model memory + facts |
| auro | Local LMR / meaning |
| guppy | Desk actuator |
| heuristic | Always-on plan synthesizer |
| identity | POCKET identity + protocols |

## Desk

1. Open `/desk`  
2. Pick agent **Genetic** (or create session `mode=genetic`)  
3. Send a goal: `hash the plan and prepare next steps`  

Aliases: `genetic_flow`, `internal`, `internal_models`.

## API

```http
GET  /v1/internal-models
POST /v1/genetic/run
{
  "goal": "Plan mesh health and ghost-hash the receipt",
  "generations": 3,
  "population": 6
}
POST /v1/internal-models/express
{"model":"ghost","goal":"phi 8"}
```

## Skills

```json
{"skill":"genetic_flow","prompt":"hash goal and plan"}
{"skill":"internal_models"}
{"skill":"express_model","params":{"model":"world"},"prompt":"brief"}
{"skill":"genetic_status"}
```

## Python

```python
from pocket.internal_models import list_models, run_genetic_flow, express_one

list_models()
run_genetic_flow("hash and plan identity", generations=2, population=4)
express_one("ghost", "chain |a|b|c")
```

## Receipts

`~/.pocket/genetic_flow/<run_id>.json`

## Via python_engine

```http
POST /v1/python-engine
{"engine":"genetic","prompt":"hash and plan","generations":2,"population":4}
```

Full doctrine: [../GENETIC_FLOW.md](../GENETIC_FLOW.md)
