"""Model Forge — AI agents build internal models and register them on the platform.

When a goal needs a specialist that does not exist yet, agents call:

  POST /v1/models/build
  skill model_build
  python_engine engine=model_forge

Kinds (safe by default):
  · template   — fill a text template with {goal} / fields
  · heuristic  — keyword → response rules
  · formula    — simple math expression (restricted)
  · wrap       — call an existing python_engine / internal model
  · code       — restricted Python body (no import/os/open by default)
  · auro       — local LMR prompt wrapper (if available)

Persisted under ~/.pocket/user_models/ and hot-registered into
pocket.internal_models so genetic flow can pick them.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from pocket.internal_models.base import Genome, InternalModel, ModelResult

ROOT = Path.home() / ".pocket" / "user_models"
ROOT.mkdir(parents=True, exist_ok=True)
INDEX = ROOT / "index.json"
_lock = Lock()

PRODUCT = "POCKET Model Forge"
SCHEMA = "pocket.model_forge.v1"
PROTOCOL = "POCKET-MODEL-FORGE/1.0"

KINDS = ("template", "heuristic", "formula", "wrap", "code", "auro")


def _safe_id(raw: str) -> str:
    s = re.sub(r"[^a-z0-9._\-]+", "-", (raw or "").strip().lower())
    s = s.strip("-._")[:48]
    return s or f"m-{uuid.uuid4().hex[:8]}"


def _load_index() -> Dict[str, Any]:
    if INDEX.is_file():
        try:
            return json.loads(INDEX.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": SCHEMA, "models": {}}


def _save_index(data: Dict[str, Any]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = INDEX.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    tmp.replace(INDEX)


def list_built(*, limit: int = 50) -> Dict[str, Any]:
    with _lock:
        data = _load_index()
        rows = list((data.get("models") or {}).values())
    rows.sort(key=lambda r: float(r.get("updated_at") or r.get("created_at") or 0), reverse=True)
    return {
        "ok": True,
        "product": PRODUCT,
        "count": len(rows),
        "models": rows[:limit],
        "kinds": list(KINDS),
        "path": str(ROOT),
    }


def get_built(model_id: str) -> Dict[str, Any]:
    mid = _safe_id(model_id)
    with _lock:
        rec = (_load_index().get("models") or {}).get(mid)
    if not rec:
        return {"ok": False, "error": f"no built model {mid}"}
    return {"ok": True, "model": rec}


class BuiltInternalModel(InternalModel):
    """Runtime wrapper for a forged model record."""

    def __init__(self, rec: Dict[str, Any]):
        self.id = str(rec.get("id") or "built")
        self.name = str(rec.get("name") or self.id)
        self.kind = str(rec.get("kind") or "template")
        self.tags = list(rec.get("tags") or ["built", "forge"])
        self.cost = str(rec.get("cost") or "local")
        self._rec = rec

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "ready": True,
            "built": True,
            "kind": self.kind,
            "id": self.id,
            "source": "model_forge",
        }

    def score_fit(self, goal: str) -> float:
        base = super().score_fit(goal)
        low = (goal or "").lower()
        for kw in self._rec.get("fit_keywords") or []:
            if str(kw).lower() in low:
                base += 0.15
        return min(1.0, base)

    def express(self, goal: str, *, genome: Optional[Genome] = None, **kwargs: Any) -> ModelResult:
        t0 = time.perf_counter()
        kind = (self.kind or "template").lower()
        rec = self._rec
        try:
            text = _express_kind(kind, rec, goal or "", genome=genome, **kwargs)
            ok = bool(text) and not str(text).startswith("ERROR:")
            return ModelResult(
                ok=ok,
                text=str(text)[:50000],
                engine=f"forge:{kind}",
                model_id=self.id,
                fitness=0.7 if ok else 0.1,
                error="" if ok else str(text)[:200],
                meta={"built": True, "kind": kind},
                latency_ms=round((time.perf_counter() - t0) * 1000, 1),
            )
        except Exception as e:
            return ModelResult(
                ok=False,
                text="",
                engine=f"forge:{kind}",
                model_id=self.id,
                error=str(e)[:240],
                latency_ms=round((time.perf_counter() - t0) * 1000, 1),
            )


def _express_kind(
    kind: str,
    rec: Dict[str, Any],
    goal: str,
    *,
    genome: Optional[Genome] = None,
    **kwargs: Any,
) -> str:
    if kind == "template":
        tpl = rec.get("template") or "Result for {goal}"
        ctx = {"goal": goal, **{k: str(v) for k, v in (kwargs or {}).items() if isinstance(v, (str, int, float))}}
        try:
            return tpl.format(**ctx)
        except Exception:
            return tpl.replace("{goal}", goal)

    if kind == "heuristic":
        rules = rec.get("rules") or []
        low = goal.lower()
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            when = str(rule.get("when") or rule.get("match") or "").lower()
            if when and when in low:
                return str(rule.get("then") or rule.get("reply") or "").replace("{goal}", goal)
        return str(rec.get("default") or f"(no rule matched) goal={goal[:200]}")

    if kind == "formula":
        expr = str(rec.get("formula") or rec.get("expr") or "0")
        # pull numbers from goal
        nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", goal)]
        env = {
            "x": nums[0] if nums else 0.0,
            "y": nums[1] if len(nums) > 1 else 0.0,
            "z": nums[2] if len(nums) > 2 else 0.0,
            "n": len(nums),
            "nums": nums,
            "pi": math.pi,
            "e": math.e,
            "phi": (1 + 5**0.5) / 2,
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "sqrt": math.sqrt,
            "log": math.log,
            "sin": math.sin,
            "cos": math.cos,
        }
        # safe AST eval
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Call,)):
                if not isinstance(node.func, ast.Name) or node.func.id not in (
                    "abs", "min", "max", "round", "sqrt", "log", "sin", "cos"
                ):
                    raise ValueError("formula: only abs/min/max/round/sqrt/log/sin/cos allowed")
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Attribute, ast.Subscript, ast.Lambda)):
                raise ValueError("formula: disallowed syntax")
        val = eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, env)  # noqa: S307
        return f"# Formula `{expr}`\n\n**result:** `{val}`\n\ngoal: {goal[:200]}\n"

    if kind == "wrap":
        target = str(rec.get("wrap_engine") or rec.get("engine") or "web_research")
        from pocket.web_ui_engine import run_python_engine

        r = run_python_engine(target, goal, params=dict(rec.get("wrap_params") or {}))
        return (r.get("text") or r.get("result") or json.dumps(r, default=str)[:4000])

    if kind == "code":
        body = str(rec.get("code") or rec.get("body") or "return goal")
        # Restricted: no import, open, exec, eval of user beyond body as function
        if re.search(r"\b(import|open|exec|eval|__|os\.|sys\.|subprocess|pathlib)\b", body):
            return "ERROR: code model disallows import/open/exec/eval/dunder"
        # Wrap as function
        src = "def _run(goal, params=None):\n"
        for line in body.splitlines() or ["return goal"]:
            src += "    " + line + "\n"
        if "return" not in body:
            src += "    return goal\n"
        local: Dict[str, Any] = {}
        # compile check
        compile(src, f"<model:{rec.get('id')}>", "exec")
        exec(src, {"__builtins__": {"str": str, "int": int, "float": float, "len": len, "range": range, "list": list, "dict": dict, "min": min, "max": max, "sum": sum, "abs": abs, "round": round, "True": True, "False": False, "None": None}}, local)  # noqa: S102
        fn = local.get("_run")
        out = fn(goal, kwargs if kwargs else {})
        return str(out)

    if kind == "auro":
        prefix = str(rec.get("system") or rec.get("prefix") or "Answer briefly as a specialist.")
        prompt = f"{prefix}\n\nGoal: {goal}"
        try:
            from pocket.auro14b_bridge import run_auro_job

            text, err, _eng = run_auro_job(prompt)
            if err:
                return f"ERROR: {err}"
            return text or ""
        except Exception as e:
            return f"ERROR: auro unavailable: {e}"

    return f"ERROR: unknown kind {kind}"


def build_model(
    *,
    model_id: str = "",
    name: str = "",
    kind: str = "template",
    description: str = "",
    tags: Optional[List[str]] = None,
    template: str = "",
    rules: Optional[List[Dict[str, Any]]] = None,
    default: str = "",
    formula: str = "",
    wrap_engine: str = "",
    wrap_params: Optional[Dict[str, Any]] = None,
    code: str = "",
    system: str = "",
    fit_keywords: Optional[List[str]] = None,
    register_now: bool = True,
    author: str = "agent",
) -> Dict[str, Any]:
    """Build (or update) a model and optionally register it on the platform."""
    kind = (kind or "template").strip().lower()
    if kind not in KINDS:
        return {"ok": False, "error": f"kind must be one of {KINDS}"}

    mid = _safe_id(model_id or name or f"built-{uuid.uuid4().hex[:8]}")
    if mid in ("ghost", "world", "auro", "guppy", "heuristic", "identity"):
        mid = f"user-{mid}"

    # validate kind payload
    if kind == "template" and not template:
        template = "## {name}\n\nGoal: {goal}\n\n_(built model)_"
    if kind == "code" and code:
        if re.search(r"\b(import|open|exec|eval|__|os\.|sys\.|subprocess)\b", code):
            return {"ok": False, "error": "code model disallows import/open/exec/eval/dunder"}
    if kind == "formula" and not formula:
        return {"ok": False, "error": "formula required for formula kind"}
    if kind == "wrap" and not wrap_engine:
        return {"ok": False, "error": "wrap_engine required for wrap kind"}

    now = time.time()
    rec: Dict[str, Any] = {
        "id": mid,
        "name": (name or mid).strip()[:80],
        "kind": kind,
        "description": (description or "")[:400],
        "tags": list(tags or ["built", "forge", kind])[:16],
        "fit_keywords": list(fit_keywords or [])[:24],
        "cost": "local",
        "author": (author or "agent")[:64],
        "created_at": now,
        "updated_at": now,
        "schema": SCHEMA,
        "product": PRODUCT,
    }
    if kind == "template":
        rec["template"] = (template or "").replace("{name}", rec["name"])
    elif kind == "heuristic":
        rec["rules"] = list(rules or [])[:40]
        rec["default"] = default or f"No heuristic matched for: {{goal}}"
    elif kind == "formula":
        rec["formula"] = formula
    elif kind == "wrap":
        rec["wrap_engine"] = wrap_engine
        rec["wrap_params"] = dict(wrap_params or {})
    elif kind == "code":
        rec["code"] = code
    elif kind == "auro":
        rec["system"] = system or f"You are specialist model {rec['name']}."

    path = ROOT / f"{mid}.json"
    with _lock:
        data = _load_index()
        prev = (data.get("models") or {}).get(mid)
        if prev:
            rec["created_at"] = prev.get("created_at") or now
        data.setdefault("models", {})[mid] = rec
        data["updated_at"] = now
        _save_index(data)
        path.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")

    registered = False
    if register_now:
        registered = bool(register_built(mid).get("ok"))

    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "model": rec,
        "path": str(path),
        "registered": registered,
        "use": {
            "express": f'POST /v1/internal-models/express {{"model":"{mid}","goal":"…"}}',
            "genetic": "genetic flow can pick this model if tags match",
            "skill": f'{{"skill":"express_model","params":{{"model":"{mid}"}},"prompt":"…"}}',
            "engine": f'python_engine engine={mid} (if wrap) or express_model',
        },
        "message": f"Built model `{mid}` ({kind})" + (" · registered" if registered else ""),
    }


def register_built(model_id: str = "") -> Dict[str, Any]:
    """Register one or all built models into internal_models registry."""
    from pocket.internal_models.registry import register

    with _lock:
        data = _load_index()
        models = data.get("models") or {}
        if model_id:
            mid = _safe_id(model_id)
            items = {mid: models[mid]} if mid in models else {}
        else:
            items = models

    if not items:
        # also load from disk files
        for p in ROOT.glob("*.json"):
            if p.name == "index.json":
                continue
            try:
                rec = json.loads(p.read_text(encoding="utf-8"))
                if rec.get("id"):
                    items[rec["id"]] = rec
            except Exception:
                continue

    if not items:
        return {"ok": False, "error": "no built models to register"}

    registered = []
    for mid, rec in items.items():
        try:
            register(BuiltInternalModel(rec))
            registered.append(mid)
        except Exception as e:
            return {"ok": False, "error": f"register {mid}: {e}", "partial": registered}

    return {
        "ok": True,
        "registered": registered,
        "count": len(registered),
        "message": f"Registered {len(registered)} built model(s) on platform",
    }


def boot_user_models() -> Dict[str, Any]:
    """Called on host start / first list_models — load forged models."""
    return register_built()


def delete_built(model_id: str) -> Dict[str, Any]:
    mid = _safe_id(model_id)
    with _lock:
        data = _load_index()
        if mid not in (data.get("models") or {}):
            return {"ok": False, "error": "not found"}
        del data["models"][mid]
        _save_index(data)
    p = ROOT / f"{mid}.json"
    try:
        p.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception:
        pass
    return {"ok": True, "deleted": mid}


def suggest_from_goal(goal: str) -> Dict[str, Any]:
    """Suggest a model blueprint from a free-text goal (for agents)."""
    low = (goal or "").lower()
    kind = "template"
    name = "specialist"
    tags = ["built"]
    fit = []
    blueprint: Dict[str, Any] = {}

    if any(w in low for w in ("math", "formula", "phi", "hash", "compute", "calculate")):
        kind = "formula"
        name = "math-helper"
        tags += ["math", "formula"]
        fit = ["math", "calc", "phi"]
        blueprint["formula"] = "x * phi if x else phi"
    elif any(w in low for w in ("wrap", "delegate", "use engine", "search", "browse")):
        kind = "wrap"
        name = "web-specialist"
        tags += ["web", "research"]
        fit = ["search", "web", "research"]
        blueprint["wrap_engine"] = "web_research"
    elif any(w in low for w in ("code", "function", "transform", "parse")):
        kind = "code"
        name = "transform"
        tags += ["code", "transform"]
        fit = ["transform", "parse"]
        blueprint["code"] = "return (goal or '').upper()[:500]"
    elif any(w in low for w in ("rule", "if ", "when ", "heuristic", "keyword")):
        kind = "heuristic"
        name = "ruleset"
        tags += ["heuristic"]
        blueprint["rules"] = [{"when": "status", "then": "All systems nominal for: {goal}"}]
        blueprint["default"] = "Acknowledged: {goal}"
    elif any(w in low for w in ("llm", "auro", "meaning", "reason")):
        kind = "auro"
        name = "local-reasoner"
        tags += ["auro", "llm"]
        blueprint["system"] = "You are a concise local specialist for this host."
    else:
        kind = "template"
        name = re.sub(r"[^a-z0-9]+", "-", low.split()[0] if low.split() else "specialist")[:24] or "specialist"
        tags += ["general"]
        blueprint["template"] = (
            f"# {name}\n\n**Goal:** {{goal}}\n\n"
            "Specialist response (built on demand).\n"
        )

    return {
        "ok": True,
        "suggestion": {
            "model_id": f"user-{name}",
            "name": name,
            "kind": kind,
            "description": f"Auto-suggested for: {(goal or '')[:120]}",
            "tags": tags,
            "fit_keywords": fit or tags,
            **blueprint,
        },
        "next": "POST /v1/models/build with this suggestion (or skill model_build)",
    }


def status() -> Dict[str, Any]:
    built = list_built()
    return {
        "ok": True,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "kinds": list(KINDS),
        "built_count": built.get("count"),
        "path": str(ROOT),
        "api": {
            "build": "POST /v1/models/build",
            "list": "GET /v1/models/built",
            "register": "POST /v1/models/register",
            "suggest": "POST /v1/models/suggest",
            "express": "POST /v1/internal-models/express",
        },
        "skills": ["model_build", "model_list_built", "model_register", "model_suggest", "engine_uses"],
        "doctrine": (
            "Agents build models when needed, register them, then genetic flow / express_model "
            "can use them on the platform."
        ),
    }
