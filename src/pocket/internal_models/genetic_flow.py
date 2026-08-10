"""Genetic flow — evolve which internal model modules run for a goal.

Pipeline (one run):
  1. Seed population of genomes (model combos + strategy genes)
  2. Express each genome through registered InternalModel modules
  3. Score fitness (quality · relevance · speed · confidence)
  4. Select elites → crossover + mutate → next generation
  5. Return best phenotype + lineage receipt

Internal models are modules; the genetic flow is the executor.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from pocket.internal_models.base import Genome, ModelResult
from pocket.internal_models.registry import get_model, list_models, pick_for_goal

ROOT = Path.home() / ".pocket" / "genetic_flow"
ROOT.mkdir(parents=True, exist_ok=True)

STRATEGIES = ("brief", "deep", "math", "memory", "act")
DEFAULT_POP = 6
DEFAULT_GENS = 3
ELITE_N = 2


def _gid() -> str:
    return uuid.uuid4().hex[:10]


def _seed_population(goal: str, *, pop_size: int = DEFAULT_POP, models: Optional[Sequence[str]] = None) -> List[Genome]:
    catalog = list_models()
    ids = [m["id"] for m in catalog]
    if models:
        ids = [m for m in models if m in ids] or ids
    ranked = pick_for_goal(goal, limit=min(4, len(ids)))
    top = [r["id"] for r in ranked] or ids[:3]

    pop: List[Genome] = []
    # Always include pure elites of top models
    for mid in top[:3]:
        pop.append(
            Genome(
                id=_gid(),
                genes={
                    "models": [mid],
                    "strategy": "math" if mid == "ghost" else ("memory" if mid == "world" else "brief"),
                    "weight": 0.8,
                    "mutate": 0.2,
                    "elite": True,
                },
                generation=0,
            )
        )
    # Identity + heuristic fusion genome
    if "identity" in ids and "heuristic" in ids:
        pop.append(
            Genome(
                id=_gid(),
                genes={
                    "models": ["identity", "heuristic"],
                    "strategy": "brief",
                    "weight": 0.7,
                    "mutate": 0.15,
                    "elite": True,
                },
                generation=0,
            )
        )
    # Random combos fill the rest
    rng = random.Random(hashlib.sha256((goal or "").encode()).hexdigest())
    while len(pop) < pop_size:
        k = rng.randint(1, min(3, len(ids)))
        chosen = rng.sample(ids, k=k)
        pop.append(
            Genome(
                id=_gid(),
                genes={
                    "models": chosen,
                    "strategy": rng.choice(STRATEGIES),
                    "weight": rng.random(),
                    "mutate": rng.uniform(0.1, 0.4),
                    "elite": False,
                },
                generation=0,
            )
        )
    return pop[:pop_size]


def _express_genome(
    genome: Genome,
    goal: str,
    *,
    cwd: str = "",
    job: Optional[Dict] = None,
) -> Genome:
    parts: List[str] = []
    errors: List[str] = []
    engines: List[str] = []
    total_ms = 0.0
    any_ok = False
    for mid in genome.models():
        mod = get_model(mid)
        if not mod:
            errors.append(f"unknown model:{mid}")
            continue
        res = mod.express(goal, genome=genome, cwd=cwd, job=job)
        total_ms += res.latency_ms
        engines.append(res.engine)
        if res.ok and res.text:
            any_ok = True
            parts.append(f"### Module `{mid}` ({res.engine})\n\n{res.text.strip()}\n")
        elif res.error:
            errors.append(f"{mid}:{res.error[:120]}")
            if res.text:
                parts.append(f"### Module `{mid}` (partial)\n\n{res.text.strip()}\n")
    text = "\n".join(parts) if parts else "(no phenotype)"
    combined = ModelResult(
        ok=any_ok,
        text=text,
        engine="+".join(engines) if engines else "genetic",
        model_id=",".join(genome.models()),
        error="; ".join(errors),
        latency_ms=total_ms,
        meta={"models": genome.models(), "strategy": genome.strategy()},
    )
    genome.result = combined
    genome.fitness = score_fitness(goal, combined, genome)
    combined.fitness = genome.fitness
    return genome


def score_fitness(goal: str, result: ModelResult, genome: Optional[Genome] = None) -> float:
    """Fitness in 0..100 — quality · relevance · structure · speed."""
    if not result:
        return 0.0
    text = (result.text or "").strip()
    if not text or text == "(no phenotype)":
        return 0.0 if not result.ok else 5.0

    score = 20.0 if result.ok else 5.0
    # Length utility (not too short, not spam)
    n = len(text)
    if n >= 80:
        score += 15
    if n >= 250:
        score += 10
    if n > 12000:
        score -= 10
    # Structure
    if "##" in text or "###" in text:
        score += 8
    if "```" in text:
        score += 4
    if "- " in text or any(f"{i}." in text for i in range(1, 6)):
        score += 6
    # Relevance: goal terms appear
    terms = [t.lower() for t in (goal or "").split() if len(t) > 3][:12]
    low = text.lower()
    if terms:
        hit = sum(1 for t in terms if t.lower() in low)
        score += 20.0 * (hit / max(1, len(terms)))
    # Speed bonus (local models)
    if result.latency_ms and result.latency_ms < 500:
        score += 8
    elif result.latency_ms and result.latency_ms < 2000:
        score += 4
    # Strategy alignment
    if genome:
        strat = genome.strategy()
        if strat == "math" and ("hash" in low or "phi" in low or "ghost" in low or "sha256" in low):
            score += 10
        if strat == "memory" and ("world" in low or "fact" in low):
            score += 8
        if strat == "brief" and n < 4000:
            score += 4
        # Prefer multi-model elites slightly
        if len(genome.models()) >= 2 and result.ok:
            score += 5
    if result.error:
        score -= min(20, 5 + len(result.error) // 40)
    return max(0.0, min(100.0, round(score, 2)))


def _tournament(pop: List[Genome], k: int = 3) -> Genome:
    contenders = random.sample(pop, k=min(k, len(pop)))
    return max(contenders, key=lambda g: g.fitness)


def _crossover(a: Genome, b: Genome, generation: int) -> Genome:
    models_a = a.models()
    models_b = b.models()
    cut = max(1, len(models_a) // 2) if models_a else 0
    child_models = list(dict.fromkeys((models_a[:cut] + models_b[cut:]) or models_a or models_b))
    if not child_models:
        child_models = ["heuristic"]
    strategy = random.choice([a.strategy(), b.strategy(), random.choice(STRATEGIES)])
    return Genome(
        id=_gid(),
        genes={
            "models": child_models[:3],
            "strategy": strategy,
            "weight": (float(a.genes.get("weight") or 0.5) + float(b.genes.get("weight") or 0.5)) / 2,
            "mutate": (float(a.genes.get("mutate") or 0.2) + float(b.genes.get("mutate") or 0.2)) / 2,
            "elite": False,
        },
        generation=generation,
        parent_ids=[a.id, b.id],
    )


def _mutate(genome: Genome, catalog_ids: List[str]) -> Genome:
    rate = float(genome.genes.get("mutate") or 0.25)
    if random.random() > rate:
        return genome
    genes = dict(genome.genes)
    models = list(genome.models())
    op = random.choice(["swap", "add", "drop", "strategy"])
    if op == "swap" and catalog_ids:
        models = [random.choice(catalog_ids)]
    elif op == "add" and catalog_ids:
        extra = random.choice(catalog_ids)
        if extra not in models:
            models.append(extra)
        models = models[:3]
    elif op == "drop" and len(models) > 1:
        models.pop(random.randrange(len(models)))
    elif op == "strategy":
        genes["strategy"] = random.choice(STRATEGIES)
    genes["models"] = models or ["heuristic"]
    genome.genes = genes
    return genome


def run_genetic_flow(
    goal: str,
    *,
    generations: int = DEFAULT_GENS,
    population: int = DEFAULT_POP,
    models: Optional[Sequence[str]] = None,
    cwd: str = "",
    job: Optional[Dict] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """Execute the full genetic flow using internal model modules."""
    t0 = time.perf_counter()
    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "empty goal", "schema": "pocket.genetic_flow.v1"}

    gens = max(1, min(8, int(generations or DEFAULT_GENS)))
    pop_n = max(3, min(12, int(population or DEFAULT_POP)))
    catalog_ids = [m["id"] for m in list_models()]

    pop = _seed_population(goal, pop_size=pop_n, models=models)
    history: List[Dict[str, Any]] = []
    best: Optional[Genome] = None

    for gen in range(gens):
        # Express
        for g in pop:
            g.generation = gen
            _express_genome(g, goal, cwd=cwd, job=job)
        pop.sort(key=lambda g: g.fitness, reverse=True)
        if not best or pop[0].fitness > best.fitness:
            best = pop[0]
        history.append(
            {
                "generation": gen,
                "best_fitness": pop[0].fitness,
                "best_id": pop[0].id,
                "best_models": pop[0].models(),
                "mean_fitness": round(sum(g.fitness for g in pop) / len(pop), 2),
                "population": [
                    {
                        "id": g.id,
                        "fitness": g.fitness,
                        "models": g.models(),
                        "strategy": g.strategy(),
                    }
                    for g in pop
                ],
            }
        )
        if gen >= gens - 1:
            break
        # Next generation: elites + offspring
        elites = pop[:ELITE_N]
        next_pop: List[Genome] = []
        for e in elites:
            child = Genome(
                id=_gid(),
                genes=dict(e.genes),
                generation=gen + 1,
                parent_ids=[e.id],
                fitness=0.0,
            )
            child.genes["elite"] = True
            next_pop.append(child)
        while len(next_pop) < pop_n:
            p1 = _tournament(pop)
            p2 = _tournament(pop)
            child = _crossover(p1, p2, gen + 1)
            child = _mutate(child, catalog_ids)
            next_pop.append(child)
        pop = next_pop

    assert best is not None
    # Re-express best if result missing (shouldn't)
    if not best.result:
        _express_genome(best, goal, cwd=cwd, job=job)

    elapsed = (time.perf_counter() - t0) * 1000
    run_id = uuid.uuid4().hex[:12]
    out: Dict[str, Any] = {
        "ok": bool(best.result and best.result.ok),
        "schema": "pocket.genetic_flow.v1",
        "run_id": run_id,
        "goal": goal[:2000],
        "generations": gens,
        "population": pop_n,
        "best": best.as_dict(),
        "fitness": best.fitness,
        "history": history,
        "modules": list_models(),
        "elapsed_ms": round(elapsed, 1),
        "engine": "genetic-flow",
    }
    out["markdown"] = format_markdown(out)
    if persist:
        try:
            fp = ROOT / f"{run_id}.json"
            slim = {k: v for k, v in out.items() if k != "markdown"}
            # trim texts in history for disk
            fp.write_text(json.dumps(slim, indent=2, default=str)[:500_000], encoding="utf-8")
            out["path"] = str(fp)
        except Exception:
            pass
    return out


def format_markdown(run: Dict[str, Any]) -> str:
    best = run.get("best") or {}
    res = best.get("result") or {}
    hist = run.get("history") or []
    lines = [
        "# Genetic flow · internal models",
        "",
        f"**run:** `{run.get('run_id')}` · **fitness:** {run.get('fitness')} · "
        f"**gens:** {run.get('generations')} · **pop:** {run.get('population')} · "
        f"**{run.get('elapsed_ms')} ms**",
        "",
        f"**goal:** {run.get('goal')}",
        "",
        f"**elite genome:** models=`{','.join((best.get('genes') or {}).get('models') or [])}` "
        f"strategy=`{(best.get('genes') or {}).get('strategy')}` id=`{best.get('id')}`",
        "",
        "## Phenotype (best internal model expression)",
        "",
        (res.get("text") or "_(empty)_").strip(),
        "",
        "## Lineage",
        "",
    ]
    for h in hist:
        lines.append(
            f"- gen {h.get('generation')}: best={h.get('best_fitness')} "
            f"models={','.join(h.get('best_models') or [])} mean={h.get('mean_fitness')}"
        )
    lines.append("")
    lines.append("## Module catalog")
    for m in run.get("modules") or []:
        lines.append(f"- `{m.get('id')}` — {m.get('name')} ({m.get('kind')})")
    lines.append("")
    lines.append("_Internal models are modules; genetic flow selects and evolves which ones run._")
    return "\n".join(lines)


def run_job(prompt: str, *, cwd: str = "", job: Optional[Dict] = None) -> Tuple[str, str, str]:
    """Executor entry: mode=genetic / genetic_flow / internal."""
    j = job or {}
    gens = int(j.get("generations") or j.get("gens") or DEFAULT_GENS)
    pop = int(j.get("population") or j.get("pop") or DEFAULT_POP)
    models = j.get("models") or j.get("internal_models")
    if isinstance(models, str):
        models = [m.strip() for m in models.split(",") if m.strip()]
    # Parse "genetic:3x8 goal..." or "gens=2 pop=4 ..."
    goal = prompt or ""
    low = goal.lower().strip()
    if low.startswith("genetic:") or low.startswith("gene:"):
        goal = goal.split(":", 1)[1].strip()
    run = run_genetic_flow(
        goal,
        generations=gens,
        population=pop,
        models=models,
        cwd=cwd,
        job=j,
    )
    md = run.get("markdown") or format_markdown(run)
    err = "" if run.get("ok") else (run.get("error") or "genetic flow incomplete")
    return md, err, "genetic-flow"


def list_runs(limit: int = 20) -> List[Dict[str, Any]]:
    items = []
    for fp in sorted(ROOT.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            items.append(
                {
                    "run_id": data.get("run_id"),
                    "fitness": data.get("fitness"),
                    "goal": (data.get("goal") or "")[:120],
                    "ok": data.get("ok"),
                    "path": str(fp),
                }
            )
        except Exception:
            continue
    return items
