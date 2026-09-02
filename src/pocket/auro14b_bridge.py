"""Auro14B / RO14B native LMR bridge for POCKET.

Ships the user's native runtime (auro_native_llm), not a third-party API model.
Silent train tick is opt-in via POCKET_AURO_TRAIN=1: heartbeat plus a
bounded meaning/scriptural step. It is not a 14B weight job unless that
step actually returns a train receipt. Never shown as a chat surface.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_AURO_ROOTS = [
    os.environ.get("AURO14B_ROOT"),
    os.environ.get("POCKET_AURO_ROOT"),
    str(Path.home() / "Documents" / "GitHub" / "Auro14B"),
    r"C:\Users\Medin\Documents\GitHub\Auro14B",
]

_DEFAULT_CKPT = "checkpoints/auro_minds/Auro-2B_physics"
_train_thread: Optional[threading.Thread] = None
_train_stop = threading.Event()
_train_state: Dict[str, Any] = {"ticks": 0, "last": None, "errors": []}


def auro_root() -> Optional[Path]:
    for r in _AURO_ROOTS:
        if not r:
            continue
        p = Path(r)
        if p.is_dir() and (p / "auro_native_llm").is_dir():
            return p.resolve()
    return None


def checkpoint_path() -> Optional[Path]:
    env = os.environ.get("POCKET_AURO_CKPT")
    root = auro_root()
    if not root:
        return None
    if env:
        p = Path(env)
        if not p.is_absolute():
            p = root / env
        return p if p.exists() else root / _DEFAULT_CKPT
    # prefer physics then base Auro-2B
    for rel in (
        _DEFAULT_CKPT,
        "checkpoints/auro_minds/Auro-2B",
        "checkpoints/auro_minds/Auro-2B_continual",
    ):
        p = root / rel
        if p.exists():
            return p
    return root / _DEFAULT_CKPT


def status() -> Dict[str, Any]:
    root = auro_root()
    ckpt = checkpoint_path()
    return {
        "ok": root is not None,
        "product": "Auro14B / RO14B native LMR",
        "repo": "https://github.com/ItsNotAILABS/Auro14B",
        "root": str(root) if root else None,
        "checkpoint": str(ckpt) if ckpt else None,
        "checkpoint_exists": bool(ckpt and ckpt.exists()),
        "family": "Auro-2B live cores → Auro-14B architecture target",
        "ui_visible": False,  # silent training not a product surface
        "train_silent": os.environ.get("POCKET_AURO_TRAIN", "0") in ("1", "true", "yes"),
        "train_state": dict(_train_state),
        "use": "Session mode auro / ro14b · python -m auro_native_llm.use --resume <ckpt>",
    }


def _ensure_path(root: Path) -> None:
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)


def try_generate(prompt: str, *, max_tokens: int = 160, timeout: int = 75) -> Dict[str, Any]:
    """One-shot native LMR — shorter default timeout for snappy desk UX."""
    root = auro_root()
    ckpt = checkpoint_path()
    if not root:
        return {"ok": False, "error": "Auro14B root not found", **status()}
    _ensure_path(root)
    prompt = (prompt or "What is MESIE?").strip()
    import subprocess

    # Cap prompt for speed on first response
    short = prompt[:700]
    cmd = [
        sys.executable,
        "-m",
        "auro_native_llm.use",
        "--resume",
        str(ckpt) if ckpt else _DEFAULT_CKPT,
        short,
    ]
    t0 = time.time()
    try:
        r = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=max(25, int(timeout)),
            env={**os.environ, "PYTHONPATH": str(root) + os.pathsep + os.environ.get("PYTHONPATH", "")},
        )
        out = (r.stdout or "")[-6000:]
        err = (r.stderr or "")[-1500:]
        ok = r.returncode == 0 or (bool(out.strip()) and "traceback" not in (err or "").lower())
        return {
            "ok": ok,
            "stdout": out,
            "stderr": err,
            "checkpoint": str(ckpt),
            "returncode": r.returncode,
            "ms": int((time.time() - t0) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "native timed out — meaning model still works; retry with `native ` or shorter ask",
            "checkpoint": str(ckpt),
            "ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "checkpoint": str(ckpt)}


def run_auro_job(prompt: str, *, job: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
    """Fast-by-default Auro: meaning model first; native only when asked or meaning fails."""
    job = job or {}
    jid = str(job.get("id") or "")
    low = (prompt or "").lower().strip()

    def _prog(msg: str) -> None:
        if not jid:
            return
        try:
            from pocket.stream_util import update_progress

            update_progress(jid, msg, engine="auro")
        except Exception:
            pass

    # Explicit meaning path
    if low.startswith("meaning") or low.startswith("web ") or low.startswith("ids ") or low in (
        "meaning",
        "browser",
        "model.json",
    ):
        try:
            from pocket.auro_meaning import run_auro_meaning_job

            p = prompt.split(" ", 1)[1] if " " in prompt and low.split()[0] in ("meaning", "web") else prompt
            _prog("Auro meaning…")
            return run_auro_meaning_job(p)
        except Exception:
            pass

    st = status()
    force_native = low.startswith("native ")
    native_prompt = prompt.replace("native ", "", 1).strip() if force_native else (prompt or "").strip()

    # Status / help — instant, no model load thrash
    if low in ("", "status", "help", "who"):
        try:
            from pocket.auro_meaning import run_auro_meaning_job

            text, err, eng = run_auro_meaning_job("status")
        except Exception:
            text, err, eng = "# Auro\n\n", "", "auro"
        text += (
            f"\n---\n## Host Auro14B\n"
            f"**Root:** `{st.get('root')}` · ckpt={st.get('checkpoint_exists')}\n"
            f"**Family:** {st.get('family')}\n\n"
            f"- Default: **fast meaning model**\n"
            f"- Full checkpoint: prefix `native ` (slower, richer)\n"
            f"- Browser demo: `/auro/`\n"
        )
        return text, err, eng or "auro"

    meaning_text = ""
    meaning_ok = False
    if not force_native:
        try:
            from pocket.auro_meaning import run_auro_meaning_job, status as meaning_status

            if meaning_status().get("ok"):
                _prog("Auro meaning (fast)…")
                meaning_text, m_err, _ = run_auro_meaning_job(prompt)
                meaning_ok = bool((meaning_text or "").strip()) and not m_err
        except Exception:
            pass

    # Default product path: return meaning immediately when it works
    if meaning_ok and not force_native:
        body = meaning_text
        if not body.lstrip().startswith("#"):
            body = "# Auro\n\n" + body
        body += "\n\n_Fast meaning model · prefix `native ` for full Auro-2B LMR._\n"
        return body, "", "auro"

    if not st.get("ok"):
        if meaning_ok:
            return meaning_text, "", "auro"
        return (
            "# Auro\n\nAuro14B root not found and meaning model unavailable.\n\n"
            "Clone Auro14B or set `AURO14B_ROOT`. Meaning model needs `vendor/auro_meaning`.\n",
            "Auro14B not found",
            "auro",
        )

    # Native path (explicit or meaning failed)
    _prog("Auro native LMR…")
    gen = try_generate(native_prompt or prompt, max_tokens=160, timeout=70)
    lines = [
        "# Auro14B · native LMR\n\n",
        f"**Checkpoint:** `{st.get('checkpoint')}`\n",
        f"**{gen.get('ms') or '?'}ms**\n\n",
    ]
    if meaning_ok and meaning_text:
        mt = meaning_text
        if mt.lstrip().startswith("#"):
            mt = "\n".join(mt.split("\n")[1:]).strip()
        lines.append("## Meaning (fast)\n\n")
        lines.append(mt[:1800])
        lines.append("\n\n")
    if gen.get("ok") and (gen.get("stdout") or "").strip():
        lines.append("## Native output\n\n```\n")
        lines.append((gen.get("stdout") or "").strip())
        lines.append("\n```\n")
        return "".join(lines), "", "auro"
    if meaning_ok:
        lines.append(
            f"## Native note\n`{gen.get('error') or gen.get('stderr') or 'incomplete'}` — "
            f"meaning answer above is usable.\n"
        )
        return "".join(lines), "", "auro"
    lines.append(f"## Run note\n`{gen.get('error') or gen.get('stderr') or 'failed'}`\n")
    if gen.get("stdout"):
        lines.append("```\n" + gen["stdout"][:1500] + "\n```\n")
    return "".join(lines), gen.get("error") or "auro run incomplete", "auro"


def _silent_train_tick() -> None:
    """Heartbeat plus one bounded train step. Log JSON; never fake a 14B update."""
    import json

    root = auro_root()
    out_dir = Path.home() / ".pocket" / "auro_train"
    out_dir.mkdir(parents=True, exist_ok=True)
    rec: Dict[str, Any] = {
        "kind": "heartbeat",
        "tick": int(_train_state.get("ticks") or 0) + 1,
        "at": time.time(),
        "ckpt": str(checkpoint_path() or ""),
        "root": str(root or ""),
        "trained": False,
    }
    if root:
        try:
            from pocket.auro_meaning import train_text_if_available

            step = train_text_if_available(
                "Auro meaning stays honest. One silent tick is a few steps, not a 14B job.",
                steps=3,
            )
            rec["meaning"] = {
                "ok": bool(step.get("ok")),
                "error": (step.get("error") or "")[:160],
            }
            rec["trained"] = bool(step.get("ok"))
            rec["kind"] = "meaning-step" if step.get("ok") else "heartbeat"
        except Exception as e:
            rec["meaning"] = {"ok": False, "error": str(e)[:160]}
        if not rec["trained"]:
            try:
                _ensure_path(root)
                from auro_native_llm.scripture.train_hooks import run_scriptural_training

                sr = run_scriptural_training(model_id="Auro-2B", steps=1)
                rec["scriptural"] = {"ok": bool(sr.get("ok")), "steps": sr.get("steps") or 1}
                rec["trained"] = bool(sr.get("ok"))
                if rec["trained"]:
                    rec["kind"] = "scriptural-step"
            except Exception as e:
                rec["scriptural"] = {"ok": False, "error": str(e)[:160]}
    (out_dir / "silent_ticks.log").open("a", encoding="utf-8").write(json.dumps(rec) + "\n")
    _train_state["last"] = rec
    _train_state["ticks"] = rec["tick"]
    if not rec.get("trained"):
        _train_state.setdefault("note", "heartbeat — no weight update this tick")


def start_silent_training(*, interval_sec: float = 600.0) -> Dict[str, Any]:
    global _train_thread
    if os.environ.get("POCKET_AURO_TRAIN", "0") not in ("1", "true", "yes"):
        return {"ok": True, "started": False, "reason": "POCKET_AURO_TRAIN not set"}
    if _train_thread and _train_thread.is_alive():
        return {"ok": True, "already": True, "state": _train_state}
    _train_stop.clear()

    def loop():
        while not _train_stop.is_set():
            try:
                _silent_train_tick()
            except Exception as e:
                _train_state.setdefault("errors", []).append(str(e)[:200])
            _train_stop.wait(interval_sec)

    _train_thread = threading.Thread(target=loop, name="pocket-auro-silent", daemon=True)
    _train_thread.start()
    return {"ok": True, "started": True, "interval_sec": interval_sec, "ui_visible": False}


def stop_silent_training() -> Dict[str, Any]:
    _train_stop.set()
    return {"ok": True, "stopped": True}
