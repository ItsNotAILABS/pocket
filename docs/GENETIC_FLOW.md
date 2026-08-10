# Internal models · genetic flow

Doctrine: **internal models are modules**; the **genetic flow** evolves which ones execute for a goal.

## Modules (`pocket.internal_models`)

| id | kind | role |
|----|------|------|
| `ghost` | math | Deterministic hash / phi / stats (zero tokens) |
| `world` | memory | World-model SQLite brief + fact check |
| `auro` | local_llm | Auro meaning / native (brief=status; deep=full job) |
| `guppy` | actuator | Desk fish (brief=identity; act=desktop steps) |
| `heuristic` | fusion | Always-on plan/decompose synthesizer |
| `identity` | fusion | POCKET identity + protocols inject |

Each implements `InternalModel.express(goal, genome=…)` and `score_fit(goal)`.

## Genetic flow

1. **Seed** — population of genomes (`models[]`, `strategy`, `mutate`)
2. **Express** — run selected modules → phenotype text
3. **Fitness** — structure · relevance · speed · strategy alignment (0–100)
4. **Select** — tournament + elites
5. **Crossover / mutate** — breed next generation
6. **Return** — best phenotype + lineage markdown

## Use

```bash
# Desk / job mode
mode=genetic   # aliases: genetic_flow, internal, internal_models

# Skills
POST /v1/skills/run {"skill":"genetic_flow","prompt":"hash goal and plan"}
POST /v1/skills/run {"skill":"internal_models"}
POST /v1/skills/run {"skill":"express_model","params":{"model":"ghost"},"prompt":"phi 8"}

# API
GET  /v1/internal-models
POST /v1/genetic/run   {"goal":"…","generations":3,"population":6}
POST /v1/internal-models/express  {"model":"world","goal":"…"}
```

```python
from pocket.internal_models import list_models, run_genetic_flow, express_one

list_models()
run_genetic_flow("Plan mesh health and ghost-hash the receipt", generations=3)
express_one("ghost", "chain |a|b|c")
```

Receipts: `~/.pocket/genetic_flow/<run_id>.json`
