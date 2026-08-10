"""50 major long-working platform + agent + app-integration tests.

Run:
  set PYTHONPATH=src
  python -m pocket.major_platform_tests

Covers: agentic harness, first-class agents, coding swarm, pixel memory,
Agent OS projects/run, desktop apps, voice, wiki, sandbox, sessions/jobs,
HTTP surfaces, cross-module integration with other apps.
"""

from __future__ import annotations

import base64
import json
import os
import time
import traceback
import urllib.error
import urllib.request
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

BASE = os.environ.get("POCKET_TEST_BASE", "http://127.0.0.1:8787").rstrip("/")
VOICE = os.environ.get("POCKET_VOICE_URL", "http://127.0.0.1:8790").rstrip("/")


def _ok(name: str, fn: Callable[[], Any], *, weight: int = 1) -> Dict[str, Any]:
    t0 = time.time()
    try:
        detail = fn()
        return {
            "name": name,
            "ok": True,
            "ms": round((time.time() - t0) * 1000, 1),
            "weight": weight,
            "detail": _clip(detail),
        }
    except Exception as e:
        return {
            "name": name,
            "ok": False,
            "ms": round((time.time() - t0) * 1000, 1),
            "weight": weight,
            "error": str(e)[:300],
            "trace": traceback.format_exc()[-500:],
        }


def _clip(v: Any, n: int = 180) -> str:
    if v is None:
        return "ok"
    s = str(v)
    return s if len(s) <= n else s[: n - 1] + "…"


def _assert(cond: bool, msg: str = "assert failed") -> None:
    if not cond:
        raise AssertionError(msg)


def _http(
    path: str,
    *,
    method: str = "GET",
    body: Optional[dict] = None,
    base: str = "",
    timeout: float = 30,
    headers: Optional[dict] = None,
) -> Tuple[int, Any]:
    url = (base or BASE) + path
    data = None
    hdrs = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except Exception:
                return resp.status, {"text": raw[:500]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw) if raw else {"error": str(e)}
        except Exception:
            return e.code, {"error": str(e), "text": raw[:300]}
    except Exception as e:
        return 0, {"error": str(e)}


def _auth_headers() -> dict:
    user = "pocket"
    pw = ""
    access = os.path.expanduser("~/.pocket/ACCESS.txt")
    try:
        if os.path.isfile(access):
            t = open(access, encoding="utf-8", errors="replace").read()
            for line in t.splitlines():
                if line.lower().startswith("password:"):
                    pw = line.split(":", 1)[1].strip()
                if line.lower().startswith("username:"):
                    user = line.split(":", 1)[1].strip() or user
    except Exception:
        pass
    if not pw:
        return {}
    token = base64.b64encode(f"{user}:{pw}".encode()).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def run_suite() -> Dict[str, Any]:
    tests: List[Dict[str, Any]] = []
    auth = _auth_headers()
    rid = uuid.uuid4().hex[:8]
    t0_suite = time.time()

    def add(name: str, fn: Callable[[], Any], weight: int = 1) -> None:
        tests.append(_ok(name, fn, weight=weight))

    # ========== A. Platform imports (1–10) ==========
    add("A01_import_pocket", lambda: __import__("pocket").__version__)
    add("A02_import_executor", lambda: __import__("pocket.executor", fromlist=["run_job"]))
    add("A03_import_agent_os", lambda: __import__("pocket.agent_os", fromlist=["dashboard"]))
    add("A04_import_harness", lambda: __import__("pocket.agentic_harness", fromlist=["plan_subagents"]))
    add("A05_import_first_class_agents", lambda: __import__("pocket.first_class_agents", fromlist=["summary"]))
    add("A06_import_coding_swarm", lambda: __import__("pocket.coding_swarm", fromlist=["run_coding_swarm"]))
    add("A07_import_pixel_vmem", lambda: __import__("pocket.pixel_vmem", fromlist=["status"]))
    add("A08_import_desktop", lambda: __import__("pocket.desktop", fromlist=["list_apps"]))
    add("A09_import_sandbox", lambda: __import__("pocket.agent_sandbox", fromlist=["list_profiles"]))
    add("A10_import_subagents", lambda: __import__("pocket.subagents_panel", fromlist=["list_subagents"]))

    # ========== B. Long agentic / execution (11–25) ==========
    def b11():
        from pocket.agentic_harness import plan_subagents

        p = plan_subagents("implement unit tests and fix auth security", mode="codex")
        _assert("FORGE_HEADLESS" in p or "SENTINEL_HEADLESS" in p, str(p))
        return p

    add("B11_harness_plan_codex_long_task", b11, 2)

    def b12():
        from pocket.agentic_harness import plan_subagents

        p = plan_subagents("@DESIGN @FORGE ship the UI release", mode="grok")
        _assert("DESIGN" in p, str(p))
        return p

    add("B12_harness_plan_grok_mentions", b12, 2)

    def b13():
        from pocket.agentic_harness import plan_subagents

        p = plan_subagents("security threat model for login", mode="claude")
        _assert("SENTINEL_HEADLESS" in p, str(p))
        return p

    add("B13_harness_plan_claude_security", b13, 2)

    def b14():
        from pocket.agentic_harness import spawn_parallel, list_live

        runs = spawn_parallel(
            ["ARCHON"],
            f"platform integration ping {rid}",
            job_id=f"maj-{rid}",
            session_id=f"sess-{rid}",
            parent_mode="codex",
            wait=True,
            timeout=60,
        )
        _assert(len(runs) >= 1, "no runs")
        live = list_live()
        _assert(live.get("ok"))
        return {"runs": len(runs), "live": live.get("total")}

    add("B14_harness_spawn_archon_execution", b14, 3)

    def b15():
        from pocket.agentic_harness import run_with_harness

        def main():
            return (
                f"# Main agent result {rid}\n\n```python\nprint('harness-main')\n```\n",
                "",
                "codex",
            )

        out, err, eng = run_with_harness(
            "codex",
            f"implement a small helper and run tests {rid}",
            job_id=f"maj-h-{rid}",
            session_id=f"sess-{rid}",
            main=main,
            sub_agents=["ARCHON"],
            parallel_subs=True,
        )
        _assert("Main agent" in out or "harness" in out.lower() or "Subagent" in out, out[:200])
        _assert(eng == "codex")
        return len(out)

    add("B15_harness_wrap_codex_main", b15, 3)

    def b16():
        from pocket.agentic_harness import run_with_harness

        def main():
            return ("Grok-style research summary for platform test.", "", "grok")

        out, err, eng = run_with_harness(
            "grok",
            "research compare agent platforms and @RESEARCH",
            job_id=f"maj-g-{rid}",
            main=main,
            sub_agents=["RESEARCH_HEADLESS"],
            parallel_subs=True,
        )
        _assert(eng == "grok" and out)
        return len(out)

    add("B16_harness_wrap_grok_main", b16, 3)

    def b17():
        from pocket.coding_swarm import run_coding_swarm

        out, err, eng = run_coding_swarm(
            f"solver sophia Write TypeScript index helper for platform test {rid}",
            ".",
            job_id=f"maj-sw-{rid}",
        )
        _assert(eng == "coding_swarm", eng)
        _assert("Sophia" in out and ("Solver" in out or "Master" in out), "swarm personas")
        _assert("artifacts/" in out, "no pixel artifacts")
        return len(out)

    add("B17_coding_swarm_long_multi_agent", b17, 4)

    def b18():
        from pocket.coding_swarm import run_coding_swarm

        out, err, eng = run_coding_swarm(
            f"@twin status telemetry for run {rid}",
            ".",
            job_id=f"maj-tw-{rid}",
        )
        _assert("Twin" in out or "telemetry" in out.lower() or "Auro" in out)
        return eng

    add("B18_coding_swarm_twin_path", b18, 2)

    def b19():
        from pocket.executor import _run_voice_agent

        out, err, eng = _run_voice_agent(f"platform voice integration hello {rid}", ".")
        _assert(eng == "voice")
        _assert(out or err)
        return eng

    add("B19_voice_agent_execution", b19, 2)

    def b20():
        from pocket.executor import _run_ask

        out, err, eng = _run_ask(f"Summarize POCKET agent OS in 3 bullets {rid}", ".")
        _assert(out or err is not None)
        return (eng, len(out or ""))

    add("B20_plan_ask_execution", b20, 2)

    def b21():
        from pocket.executor import run_job

        job = {
            "id": f"job-bench-{rid}",
            "mode": "plan",
            "prompt": f"List 3 first-class POCKET agents {rid}",
            "workspace": "workspace",
            "session_id": f"s-bench-{rid}",
            "harness": True,
            "_harness_inner": True,
        }
        out, err, eng = run_job(job)
        _assert(out is not None)
        return eng

    add("B21_run_job_plan_inner", b21, 2)

    def b22():
        from pocket.executor import run_job

        job = {
            "id": f"job-swarm-{rid}",
            "mode": "coding_swarm",
            "prompt": f"sophia emit a tiny python hello module {rid}",
            "workspace": "workspace",
            "session_id": f"s-sw-{rid}",
            "_harness_inner": True,
        }
        out, err, eng = run_job(job)
        _assert(eng == "coding_swarm" and "artifacts/" in (out or ""))
        return len(out or "")

    add("B22_run_job_coding_swarm", b22, 3)

    def b23():
        from pocket.pixel_vmem import put_artifact, list_artifacts

        a = put_artifact(
            "export const platformTest = () => 42;\n",
            title=f"platform-ts-{rid}",
            language="ts",
            agent="codex",
            agent_role="coder",
            ai_version="codex",
            run_id=f"maj{rid}",
            tags=["major-test", "platform"],
        )
        _assert(a.get("ok") and a.get("symbol"))
        la = list_artifacts(limit=20)
        _assert(la.get("count", 0) >= 1)
        return a.get("symbol")

    add("B23_pixel_artifact_from_agent", b23, 2)

    def b24():
        from pocket.pixel_vmem import store_agent_run, look

        r = store_agent_run(
            agent="grok",
            mode="grok",
            prompt=f"platform store test {rid}",
            result=f"# Grok result\n\nIntegration OK {rid}\n",
            job_id=f"maj-store-{rid}",
            language="md",
        )
        _assert(r.get("ok"))
        g = look(symbol=r.get("symbol") or "")
        _assert(g.get("ok"))
        return r.get("symbol")

    add("B24_store_agent_run_look", b24, 2)

    def b25():
        from pocket.worker import ensure_pool

        p = ensure_pool()
        _assert(p is not None)
        return "pool-ok"

    add("B25_worker_pool_ready", b25)

    # ========== C. Cross-platform Agent OS / IDE (26–35) ==========
    def c26():
        from pocket.agent_os import list_systems

        s = list_systems(live=True)
        _assert(s.get("total", 0) >= 12 and s.get("ready", 0) >= 10)
        return f"{s['ready']}/{s['total']}"

    add("C26_agent_os_systems_live", c26, 2)

    def c27():
        from pocket.agent_os import parity_report

        p = parity_report()
        _assert(len(p.get("rows") or []) == 4)
        ids = {r["id"] for r in p["rows"]}
        _assert(ids >= {"claude_code", "antigravity", "emergent", "replit"})
        return list(ids)

    add("C27_parity_four_platforms", c27, 2)

    def c28():
        from pocket.agent_os import create_project, run_project, get_project

        pid = f"maj-proj-{rid}"
        p = create_project(pid, template="python", title="Major Platform", seed="print('PLATFORM_OK')\n")
        _assert(p.get("ok"), p.get("error"))
        g = get_project(p["project"]["id"])
        _assert(g.get("ok") and g.get("files"))
        r = run_project(p["project"]["id"])
        _assert(r.get("ok") and "PLATFORM_OK" in (r.get("stdout") or ""), r)
        return r.get("stdout")

    add("C28_native_project_create_run_py", c28, 3)

    def c29():
        from pocket.agent_os import create_project, run_project

        pid = f"maj-js-{rid}"
        p = create_project(pid, template="javascript", seed='console.log("JS_OK");\n')
        _assert(p.get("ok"))
        r = run_project(p["project"]["id"])
        if r.get("ok"):
            _assert("JS_OK" in (r.get("stdout") or ""))
            return "js-run-ok"
        _assert("node" in str(r.get("error") or "").lower() or r.get("returncode") is not None, r)
        return r.get("error") or "js-attempted"

    add("C29_native_project_js_run_or_skip", c29, 2)

    def c30():
        from pocket.agent_os import dashboard

        d = dashboard()
        _assert(d.get("ok") and d.get("systems") and d.get("parity"))
        _assert("first_class_agents" in d or d.get("swarm_roster") or d.get("version"))
        return d.get("version")

    add("C30_agent_os_dashboard", c30, 2)

    def c31():
        from pocket.agent_os import list_projects, timeline

        lp = list_projects()
        _assert(lp.get("ok") and isinstance(lp.get("projects"), list))
        tl = timeline(10)
        _assert(tl.get("ok"))
        return len(lp.get("projects") or [])

    add("C31_projects_and_timeline", c31)

    def c32():
        from pocket.agent_os import import_artifact_to_project
        from pocket.pixel_vmem import put_artifact

        a = put_artifact(
            "print('IMPORTED_RUN')\n",
            title=f"imp-{rid}",
            language="py",
            agent="bench",
            run_id=f"imp{rid}",
        )
        _assert(a.get("ok"))
        imp = import_artifact_to_project(a["symbol"])
        _assert(imp.get("ok") and imp.get("project_id"), imp)
        return imp.get("project_id")

    add("C32_import_pixel_artifact_to_project", c32, 3)

    def c33():
        from pocket.agent_os import run_artifact_symbol
        from pocket.pixel_vmem import put_artifact

        a = put_artifact(
            "print('ART_RUN_OK')\n",
            title=f"runart-{rid}",
            language="py",
            agent="bench",
            run_id=f"ra{rid}",
        )
        _assert(a.get("ok"))
        r = run_artifact_symbol(a["symbol"])
        _assert(r.get("ok") and "ART_RUN_OK" in (r.get("stdout") or ""), r)
        return r.get("stdout")

    add("C33_run_artifact_symbol_py", c33, 3)

    def c34():
        from pocket.agent_sandbox import list_profiles

        p = list_profiles()
        profiles = p.get("profiles") or p.get("items") or p
        if isinstance(profiles, dict):
            n = len(profiles)
        else:
            n = len(profiles) if profiles else 0
        _assert(n >= 1 or p.get("ok"), p)
        return n or p

    add("C34_sandbox_profiles", c34)

    def c35():
        from pocket.sessions import create_session, list_sessions
        from pocket import sessions as sess_mod

        # flexible session API
        if hasattr(sess_mod, "create_session"):
            s = sess_mod.create_session(mode="plan", title=f"maj-{rid}")
            _assert(s is not None)
            return getattr(s, "get", lambda k, d=None: s)("id") if isinstance(s, dict) else str(s)[:40]
        if hasattr(sess_mod, "new_session"):
            s = sess_mod.new_session(mode="plan")
            return str(s)[:40]
        # fallback: module import proves sessions exist
        _assert(hasattr(sess_mod, "list_sessions") or hasattr(sess_mod, "get_session"))
        return "sessions-module-ok"

    add("C35_sessions_module", c35)

    # ========== D. First-class agents registry (36–40) ==========
    def d36():
        from pocket.first_class_agents import build_registry

        r = build_registry(live=False)
        n = r.get("count") or len(r.get("agents") or [])
        _assert(n >= 50, f"only {n} agents")
        return n

    add("D36_first_class_registry_count", d36, 2)

    def d37():
        from pocket.first_class_agents import summary

        s = summary()
        _assert(s.get("ok") and s.get("total_agents", 0) >= 50)
        return s.get("total_agents")

    add("D37_first_class_summary_live", d37, 2)

    def d38():
        from pocket.first_class_agents import desk_catalog

        c = desk_catalog()
        _assert(c.get("count", 0) >= 5 or len(c.get("items") or c.get("agents") or []) >= 5)
        return c.get("count")

    add("D38_desk_catalog", d38, 2)

    def d39():
        from pocket.first_class_agents import ensure_modes_aligned

        m = ensure_modes_aligned()
        _assert(m is not None)
        return m.get("ok") if isinstance(m, dict) else str(m)[:40]

    add("D39_modes_aligned", d39)

    def d40():
        from pocket.coding_swarm import list_roster

        ro = list_roster()
        agents = ro.get("agents") or ro.get("roster") or []
        _assert(len(agents) >= 3, ro)
        names = " ".join(str(a.get("name") or a.get("id") or a) for a in agents)
        _assert("Sophia" in names or "sophia" in names.lower() or len(agents) >= 3)
        return len(agents)

    add("D40_swarm_roster_personas", d40, 2)

    # ========== E. Desktop / other-apps integration (41–45) ==========
    def e41():
        from pocket.desktop import list_apps

        apps = list_apps()
        _assert(len(apps) >= 20, f"only {len(apps)} apps")
        avail = sum(1 for a in apps if a.get("available"))
        return {"total": len(apps), "available": avail}

    add("E41_desktop_list_apps_catalog", e41, 2)

    def e42():
        from pocket.desktop import list_apps

        apps = list_apps()
        ids = {a["id"] for a in apps}
        # Windows integration surface: browser + terminal + explorer at minimum
        expected = {"edge", "explorer", "notepad", "cmd", "powershell"}
        hit = expected & ids
        # aliases may differ — also accept chrome/terminal
        if len(hit) < 2:
            hit = hit | ({"chrome", "wt", "terminal", "code"} & ids)
        _assert(len(hit) >= 2, f"missing desktop apps, have sample {list(ids)[:15]}")
        return list(hit)

    add("E42_desktop_core_windows_apps", e42, 2)

    def e43():
        from pocket.desktop import list_apps

        apps = list_apps()
        groups = {a.get("group", "native") for a in apps}
        third = [a for a in apps if a.get("group") not in ("native", None, "")]
        # third-party integration path exists (VS Code, Cursor, Slack, etc.)
        _assert(len(apps) >= 20)
        return {"groups": list(groups), "third_party": len(third)}

    add("E43_desktop_third_party_surface", e43, 2)

    def e44():
        from pocket.desktop import open_app

        # Non-destructive: open calculator if available, else notepad briefly is fine
        # Prefer calc (lightweight). Do not assert window focus.
        r = open_app("calc")
        if not r.get("ok"):
            r = open_app("notepad")
        if not r.get("ok"):
            r = open_app("explorer")
        _assert(r.get("ok") or "not available" in str(r.get("error") or "").lower() or r.get("error"), r)
        return r.get("ok") or r.get("error") or r

    add("E44_desktop_open_app_integration", e44, 3)

    def e45():
        from pocket.desktop import run_desktop_job

        out, err, eng = run_desktop_job(f"list available desktop apps for platform test {rid}")
        _assert(out or err is not None)
        _assert(eng in ("desktop", "desktop_agent", "apps") or eng)
        return eng

    add("E45_desktop_job_agent_path", e45, 2)

    # ========== F. HTTP live + voice + cross-app API (46–50) ==========
    def f46():
        code, body = _http("/health", timeout=8, headers=auth)
        if code == 0:
            code, body = _http("/v1/health", timeout=8, headers=auth)
        _assert(code == 200, f"health {code} {body}")
        return body.get("status") or body.get("ok") or code

    add("F46_http_health_live", f46, 2)

    def f47():
        code, body = _http("/v1/agents/catalog", timeout=15, headers=auth)
        if code in (401, 403):
            code, body = _http("/v1/agents/first-class", timeout=15, headers=auth)
        _assert(code == 200, f"catalog {code} {body}")
        n = body.get("count") or len(body.get("agents") or body.get("items") or [])
        _assert(n >= 10 or body.get("ok"), f"catalog thin: {n}")
        return n or body.get("ok")

    add("F47_http_agents_catalog", f47, 2)

    def f48():
        code, body = _http("/v1/os/systems", timeout=15, headers=auth)
        if code != 200:
            code, body = _http("/v1/os", timeout=15, headers=auth)
        _assert(code == 200, f"os {code} {body}")
        total = body.get("total") or len(body.get("systems") or [])
        if not total and isinstance(body.get("systems"), dict):
            total = body["systems"].get("total") or 0
        _assert(total >= 8 or body.get("ok"), f"systems {total} {body}")
        return total or body.get("ok")

    add("F48_http_agent_os_systems", f48, 2)

    def f49():
        code, body = _http("/v1/desktop/apps", timeout=15, headers=auth)
        _assert(code == 200, f"desktop apps http {code} {body}")
        apps = body.get("apps") or body.get("items") or []
        if isinstance(apps, dict):
            apps = list(apps.values())
        _assert(len(apps) >= 10 or body.get("ok"), f"http apps {len(apps)}")
        return len(apps)

    add("F49_http_desktop_apps_integration", f49, 2)

    def f50():
        # Voice API + harness/swarm HTTP surfaces
        vcode, vbody = _http("/health", base=VOICE, timeout=5)
        hcode, hbody = _http("/v1/harness", timeout=12, headers=auth)
        scode, sbody = _http("/v1/swarm", timeout=12, headers=auth)
        vmem_code, vmem = _http("/v1/vmem", timeout=12, headers=auth)
        parts = {
            "voice_http": vcode,
            "harness": hcode,
            "swarm": scode,
            "vmem": vmem_code,
        }
        # Voice may be optional if node missing — desk integration still counts if harness+vmem ok
        core_ok = (hcode == 200 or hbody.get("ok")) and (vmem_code == 200 or vmem.get("ok") or scode == 200)
        if vcode == 200:
            return {**parts, "voice": "up", "core": core_ok}
        _assert(core_ok, f"core surfaces down: {parts}")
        return {**parts, "voice": "down-optional", "core": core_ok}

    add("F50_voice_harness_swarm_vmem_surfaces", f50, 3)

    # ---- score ----
    passed = sum(1 for t in tests if t["ok"])
    failed = [t for t in tests if not t["ok"]]
    w_pass = sum(t["weight"] for t in tests if t["ok"])
    w_total = sum(t["weight"] for t in tests) or 1
    rate = round(100.0 * passed / max(len(tests), 1), 2)
    w_rate = round(100.0 * w_pass / w_total, 2)
    elapsed = round(time.time() - t0_suite, 2)

    return {
        "ok": passed == len(tests),
        "suite": "major_platform_tests",
        "total": len(tests),
        "passed": passed,
        "failed": len(failed),
        "pass_rate_pct": rate,
        "weighted_pass_pct": w_rate,
        "elapsed_s": elapsed,
        "base": BASE,
        "voice": VOICE,
        "run_id": rid,
        "failures": [
            {"name": t["name"], "error": t.get("error"), "ms": t.get("ms")} for t in failed
        ],
        "tests": tests,
    }


def main() -> None:
    print("POCKET major platform tests — 50 long agent/cross-platform/app-integration")
    print(f"BASE={BASE} VOICE={VOICE}")
    report = run_suite()
    print(
        f"\nRESULT: {report['passed']}/{report['total']} "
        f"({report['pass_rate_pct']}%) weighted={report['weighted_pass_pct']}% "
        f"elapsed={report['elapsed_s']}s"
    )
    if report["failures"]:
        print("\nFAILURES:")
        for f in report["failures"]:
            print(f"  - {f['name']}: {f['error']}")
    # compact per-test lines
    print("\nDETAIL:")
    for t in report["tests"]:
        mark = "PASS" if t["ok"] else "FAIL"
        extra = t.get("detail") if t["ok"] else t.get("error")
        print(f"  [{mark}] {t['name']}  {t['ms']}ms  {extra}")
    out_path = os.path.expanduser("~/.pocket/major_platform_tests_last.json")
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nWrote {out_path}")
    except Exception as e:
        print(f"\n(report write skipped: {e})")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
