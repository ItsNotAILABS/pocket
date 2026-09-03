"""Concurrent worker pool — many agents/terminals at once."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Optional

from pocket.executor import run_job
from pocket.jobs import claim, finish, next_queued

_pool: Optional[ThreadPoolExecutor] = None
_inflight = 0
_inflight_lock = Lock()
# Parallel Codex/shell/WSL jobs — raise via POCKET_JOB_WORKERS (default 6)
_MAX = max(2, min(16, int(os.environ.get("POCKET_JOB_WORKERS") or "6")))


def _run_claimed(job: dict) -> None:
    global _inflight
    jid = job["id"]
    mode = str(job.get("mode") or "agent")
    print(f"[POCKET worker] running {jid} mode={mode} session={job.get('session_id')}", flush=True)
    try:
        from pocket.agent_habitat import pulse as habitat_pulse

        habitat_pulse(
            mode,
            status="working",
            task=str(job.get("prompt") or "")[:120],
            line=f"Job {jid[:12]}…",
        )
    except Exception:
        pass
    try:
        from pocket.tenant_jail import attach_team_to_job

        job = attach_team_to_job(dict(job))
    except Exception:
        pass
    try:
        result, error, engine = run_job(job)
        try:
            from pocket.reply_format import polish_agent_output

            # Final pass so stored session transcripts stay chat-readable
            result = polish_agent_output(result or "", engine=str(engine or job.get("mode") or ""))
        except Exception:
            pass
        finish(jid, result=result, error=error, engine=engine)
        try:
            from pocket.agent_habitat import pulse as habitat_pulse

            habitat_pulse(
                str(engine or mode),
                status="idle" if not error else "idle",
                task="",
                line=(("Done · " + str(result or "")[:100]) if not error else ("Failed · " + str(error)[:80])),
            )
        except Exception:
            pass
        # First-class: every finished agent run can land in pixel memory (artifacts)
        try:
            mode = str(job.get("mode") or engine or "agent")
            # coding_swarm already stores rich artifacts; still index the full transcript lightly
            if result and not error:
                from pocket.pixel_vmem import store_agent_run

                store_agent_run(
                    agent=str(engine or mode),
                    mode=mode,
                    prompt=str(job.get("prompt") or "")[:500],
                    result=str(result)[:120000],
                    job_id=jid,
                    language="md",
                )
        except Exception as pe:
            print(f"[POCKET worker] pixel store skip {jid}: {pe}", flush=True)
        print(f"[POCKET worker] {jid} -> done engine={engine} err={bool(error)}", flush=True)
    except Exception as e:
        finish(jid, result="", error=str(e), engine=job.get("mode") or "unknown")
        print(f"[POCKET worker] {jid} exception {e}", flush=True)
    finally:
        with _inflight_lock:
            _inflight -= 1


def ensure_pool() -> ThreadPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ThreadPoolExecutor(max_workers=_MAX, thread_name_prefix="pocket-job")
    return _pool


def process_one() -> bool:
    """Claim one job if capacity; return True if work scheduled or was available."""
    global _inflight
    with _inflight_lock:
        if _inflight >= _MAX:
            return True  # busy, keep loop warm
        capacity = True
    job = next_queued()
    if not job:
        return False
    claimed = claim(job["id"])
    if not claimed:
        return False
    with _inflight_lock:
        _inflight += 1
    ensure_pool().submit(_run_claimed, claimed)
    return True


def run_loop(poll: float = 0.6) -> None:
    print("POCKET worker pool — multi-agent concurrent executor", flush=True)
    ensure_pool()
    while True:
        try:
            # drain up to capacity each tick
            progressed = False
            for _ in range(_MAX):
                if process_one():
                    progressed = True
                else:
                    break
            if not progressed:
                time.sleep(poll)
            else:
                time.sleep(0.15)
        except KeyboardInterrupt:
            print("worker stop", flush=True)
            break
        except Exception as e:
            print(f"[worker error] {e}", flush=True)
            time.sleep(2)


if __name__ == "__main__":
    run_loop()
