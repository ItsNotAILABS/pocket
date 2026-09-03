"""POCKET HTTP host - desk, PhoneAI, API, MCP."""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path  # used for PUBLIC_URL + docs
from typing import Optional
from urllib.parse import parse_qs, urlparse  # studio file query

from pocket.app_ui import HTML
from pocket.studio_ui import STUDIO_HTML
from pocket.agent_os_ui import OS_HTML
from pocket.phone_ui import phone_html, phone_manifest
from pocket.work_studio_ui import work_studio_html
from pocket.curiosities_ui import curiosities_html
from pocket.auth import (
    auth_summary,
    clear_auth_failures,
    is_app_shell,
    is_authorized,
    is_rate_limited,
    path_is_public,
    public_gate_html,
    record_auth_failure,
    security_headers,
)
from pocket.rbac import (
    allow_admin_action,
    allow_agent,
    allow_host_path,
    allow_mode,
    can_access_owned,
    is_admin,
    is_founder,
    is_host_power,
    principal as rbac_principal,
)
from pocket.executor import available_engines
from pocket.grok_bridge import can_codex_start_grok, write_pull_package
from pocket.jobs import WORK_DIR, create_job, get, list_jobs
from pocket.live import connect_all_down, connect_service, lan_ip, probe_all
from pocket.platform import (
    deploy_log_tail,
    deploy_process,
    deploy_static,
    list_deploys,
    platform_manifest,
    stop_deploy,
    workspace_tools,
)
from pocket.sessions import (
    add_user_message,
    bind_job,
    complete_message,
    create_session,
    delete_session,
    get as get_session,
    get_usage,
    list_sessions,
    rename,
)
from pocket.terminals import (
    create_terminal,
    get_terminal,
    list_terminals,
    send_terminal,
    stop_terminal,
)
from pocket.tokenomics import (
    cost_analysis_20_users,
    estimate_session_cost,
    mint,
    snapshot as token_snapshot,
)
from pocket.organism import snapshot as organism_snapshot
from pocket.uploads import upload_file
from pocket.worker import ensure_pool, process_one

PORT = int(os.environ.get("POCKET_PORT", "8787"))
DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs" / "research"
_worker_started = False
_worker_lock = threading.Lock()

DOC_MAP = {
    "tokenomics": "POCKET_TOKENOMICS_PAPER.md",
    "usage-cost": "POCKET_USAGE_COST_PAPER.md",
    "platform": "POCKET_PLATFORM_PAPER.md",
    "ship": "POCKET_SHIP_STORY_PAPER.md",
    "guppy": "POCKET_GUPPY_DESK_AGENT_PAPER.md",
    "desktop-autonomy": "POCKET_DESKTOP_AUTONOMY_PAPER.md",
    "engines-beyond-code": "POCKET_ENGINES_BEYOND_CODE_PAPER.md",
    "lab-claims": "POCKET_LAB_SYSTEMS_CLAIMS_PAPER.md",
    "host-copilot": "POCKET_HOST_COPILOT_VISION_PAPER.md",
    "browser": "POCKET_BROWSER_MODE_PAPER.md",
    "live-desk": "POCKET_LIVE_DESK_PRODUCTION.md",
    "agents-named": "POCKET_NAMED_AGENTS_REGISTER.md",
    "latin": "POCKET_LATIN_WORKERS.md",
    "alive": "POCKET_ALIVE_AUTONOMOUS.md",
    "skills": "POCKET_SKILLS_AND_DAEMON.md",
    "orchestrator": "POCKET_ORCHESTRATOR_VISION.md",
    "real-skills": "POCKET_REAL_SKILLS.md",
    "vision-workers": "POCKET_VISION_WORKERS_FIRST_CLASS.md",
    "pixel": "POCKET_PIXEL_TRANSLATOR.md",
    "api-first": "POCKET_PLATFORM_API_FIRST.md",
}
DOCS_ROOT_MAIN = Path(__file__).resolve().parents[2] / "docs"


def _organism_status(n: int, eng: dict, pub, tok: dict) -> dict:
    try:
        from pocket.platform import list_deploys

        deploys = len([d for d in list_deploys() if d.get("status") == "running"])
    except Exception:
        deploys = 0
    try:
        modes = [s.get("mode") or "?" for s in list_sessions(20)]
        jobs_running = sum(1 for s in list_sessions(30) if s.get("status") == "running")
    except Exception:
        modes, jobs_running = [], 0
    return organism_snapshot(
        worker_alive=_worker_started,
        sessions=n,
        jobs_running=jobs_running,
        deploys=deploys,
        pock=int(tok.get("balance") or 0),
        public=bool(pub and str(pub).startswith("http")),
        codex=bool(eng.get("codex")),
        grok=bool(eng.get("grok")),
        modes=modes,
    )


def _openapi_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "POCKET AI API",
            "version": __import__("pocket").__version__,
            "description": "POCKET platform API — orchestrator, vision, workers, campaigns. Auth: Basic or Bearer sk_pocket_…",
        },
        "paths": {
            "/v1/ai": {"get": {"summary": "Product catalog"}},
            "/v1/ai/agents": {"get": {"summary": "List headless agents"}},
            "/v1/ai/agents/{id}/run": {"post": {"summary": "Run headless agent"}},
            "/v1/ai/chat": {"post": {"summary": "Chat completion (OpenAI-shaped)"}},
            "/v1/ai/jobs": {"post": {"summary": "Async job"}},
            "/v1/ai/jobs/{id}": {"get": {"summary": "Poll job"}},
            "/v1/ai/keys": {"post": {"summary": "Create API key (admin)"}},
            "/v1/ai/usage": {"get": {"summary": "Key usage"}},
            "/v1/ready": {"get": {"summary": "Production A-Z readiness"}},
            "/health": {"get": {"summary": "Liveness"}},
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "sk_pocket_"}
            }
        },
        "security": [{"bearerAuth": []}],
    }


def ensure_embedded_worker() -> None:
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        _worker_started = True
        ensure_pool()
        try:
            from pocket.autonomy import ensure_runner

            ensure_runner()
        except Exception:
            pass
        try:
            from pocket.worker_daemon import ensure_daemon

            ensure_daemon()
        except Exception:
            pass
        try:
            from pocket.live_vision import ensure_vision

            ensure_vision()
        except Exception:
            pass
        try:
            from pocket.world_model import ensure_db

            ensure_db()
        except Exception:
            pass
        try:
            from pocket.agent_hook import ensure_mesh_hook

            ensure_mesh_hook()
            print("[POCKET] mesh hook armed — @mentions + headless pack", flush=True)
        except Exception as e:
            print(f"[POCKET] mesh hook skipped: {e}", flush=True)
        try:
            from pocket.always_on_swarm import ensure_running as ensure_swarm

            # Always-on swarm — continuous multi-agent pulses
            ensure_swarm()
            print("[POCKET] always-on swarm armed", flush=True)
        except Exception as e:
            print(f"[POCKET] swarm arm skipped: {e}", flush=True)
        try:
            from pocket.kernels.long_workflow import ensure_running as ensure_wfs

            wst = ensure_wfs()
            print(f"[POCKET] long workflows armed n={len(wst.get('armed') or [])}", flush=True)
        except Exception as e:
            print(f"[POCKET] long workflows skipped: {e}", flush=True)
        try:
            from pocket.damian_fleet import ensure_running as ensure_damians

            # Internal Damian keepers (up to 100) — user-invisible background
            st = ensure_damians()
            print(
                f"[POCKET] damian fleet armed n={st.get('count')} "
                f"hearts={st.get('hearts')} brains={st.get('brains')} headless={st.get('headless')}",
                flush=True,
            )
        except Exception as e:
            print(f"[POCKET] damian fleet skipped: {e}", flush=True)
        try:
            from pocket.infinite_wiki import ensure_db as wiki_db, ensure_watcher as wiki_watch

            from pocket.infinite_wiki import ensure_default_index

            wiki_db()
            wiki_watch(interval_sec=10)
            # background index if empty — don't block HTTP
            threading.Thread(
                target=ensure_default_index,
                name="wiki-boot-index",
                daemon=True,
            ).start()
            print("[POCKET] infinite wiki watcher armed", flush=True)
        except Exception as e:
            print(f"[POCKET] infinite wiki skipped: {e}", flush=True)
        try:
            from pocket.dream_mode import ensure_running as ensure_dreams
            from pocket.time_capsules import ensure_running as ensure_capsules

            ensure_dreams()
            ensure_capsules()
            print("[POCKET] dream mode + time capsules armed", flush=True)
        except Exception as e:
            print(f"[POCKET] curiosities arm skipped: {e}", flush=True)
        try:
            from pocket.platform_api import bootstrap_platform

            boot = bootstrap_platform()
            print(f"[POCKET] platform surface: {'; '.join(boot.get('notes') or [])}", flush=True)
        except Exception as e:
            print(f"[POCKET] platform bootstrap skipped: {e}", flush=True)

        def _loop():
            while True:
                try:
                    # Drain up to pool capacity each tick so queued desk messages
                    # start within ~100ms instead of stacking behind a 0.5s poll.
                    progressed = False
                    for _ in range(8):
                        if process_one():
                            progressed = True
                        else:
                            break
                    time.sleep(0.08 if progressed else 0.25)
                except Exception as e:
                    print(f"[embedded worker] {e}", flush=True)
                    time.sleep(1.0)

        n_dispatch = max(2, min(4, int(os.environ.get("POCKET_DISPATCH_THREADS") or "3")))
        for i in range(n_dispatch):
            t = threading.Thread(target=_loop, name=f"pocket-dispatch-{i}", daemon=True)
            t.start()
        print(
            f"[POCKET] multi-agent worker pool started dispatch={n_dispatch}",
            flush=True,
        )


def status() -> dict:
    try:
        from pocket.edition import bootstrap_edition, summary as edition_summary, is_founder, app_url, marketing_url

        bootstrap_edition()
        ed = edition_summary()
    except Exception:
        ed = {}
        is_founder = lambda: True  # type: ignore
        app_url = lambda: f"http://127.0.0.1:{PORT}"  # type: ignore
        marketing_url = lambda: "https://pocket.medinatechlabs.net"  # type: ignore

    eng = available_engines()
    # Founder desk: app URL is localhost. Marketing host is separate and optional.
    pub = (os.environ.get("POCKET_PUBLIC_URL") or "").strip() or None
    if is_founder() and (not pub or "medinatechlabs" in (pub or "")):
        if (os.environ.get("POCKET_FORCE_PUBLIC_URL") or "").strip() not in ("1", "true", "yes"):
            pub = f"http://127.0.0.1:{PORT}"
    # Only load tunnel / PUBLIC_URL.txt when NOT founder (or force public)
    if (not pub or pub.startswith("http://127.0.0.1")) and not is_founder():
        root_pocket = Path(__file__).resolve().parents[2] / ".pocket"
        envf = root_pocket / "cloudflare-named.env"
        if envf.exists():
            try:
                for line in envf.read_text(encoding="utf-8").splitlines():
                    if line.startswith("POCKET_PUBLIC_URL="):
                        pub = line.split("=", 1)[1].strip() or None
                        break
            except Exception:
                pass
        if not pub:
            puf = Path(__file__).resolve().parents[2] / "PUBLIC_URL.txt"
            if puf.exists():
                try:
                    import re as _re

                    m = _re.search(r"https://[^\s]+", puf.read_text(encoding="utf-8"))
                    if m:
                        pub = m.group(0).rstrip("/")
                except Exception:
                    pass
    ip = lan_ip()
    n = len(list_sessions(100))
    tok = token_snapshot()
    klass = {}
    try:
        from pocket.first_class import health_enrichment

        klass = health_enrichment()
    except Exception:
        pass
    from pocket import __version__ as _ver, TAGLINE

    desk_local = f"http://127.0.0.1:{PORT}/desk"
    sandbox_info: dict = {}
    try:
        from pocket.agent_sandbox import status as _sb_status

        sandbox_info = _sb_status()
    except Exception as _se:
        sandbox_info = {"ok": False, "error": str(_se)[:120]}

    return {
        "ok": True,
        "product": "POCKET",
        "version": _ver,
        "tagline": TAGLINE,
        "edition": ed.get("edition") or ("founder" if is_founder() else "public"),
        "class": klass.get("grade") or "?",
        "first_class": bool(klass.get("first_class")),
        "class_score": klass.get("score"),
        "full": "POCKET",
        "schema": "pocket.status.v1",
        "lan_ip": ip,
        "port": PORT,
        "url": f"http://{ip}:{PORT}/",
        "local": f"http://127.0.0.1:{PORT}/",
        "public_url": pub,
        "app_url": app_url() if callable(app_url) else pub,
        "marketing_url": marketing_url() if callable(marketing_url) else None,
        "edition_info": ed,
        "access": auth_summary(),
        "surfaces": {
            "desk": f"http://127.0.0.1:{PORT}/desk",
            "work_studio": f"http://127.0.0.1:{PORT}/work",
            "product_studio": f"http://127.0.0.1:{PORT}/studio",
            "doc": "docs/STUDIOS.md",
        },
        "sandbox": sandbox_info,
        "engine": {
            **eng,
            "worker_alive": _worker_started,
            "workspace": str(WORK_DIR),
            "grok_cli": can_codex_start_grok(),
        },
        "usage": get_usage(),
        "tokenomics": {
            "balance": tok.get("balance"),
            "unit": tok.get("unit"),
            "lifetime_burned": tok.get("lifetime_burned"),
        },
        "organism": _organism_status(n, eng, pub, tok),
        "sessions_open": n,
        "session_cost_estimate": estimate_session_cost(n),
        "cost_20_users": cost_analysis_20_users(),
        "public_url_file": str(Path(__file__).resolve().parents[2] / "PUBLIC_URL.txt"),
        "how": {
            "desktop": desk_local,
            "phone_same_wifi": f"http://{ip}:{PORT}/",
            "phone_anywhere": (
                "Optional — enable tunnel when you want remote; founder desk is local"
                if is_founder()
                else (pub or "Configure public host when ready")
            ),
            "docs": list(DOC_MAP.keys()),
            "value": "AI workspace on your machine — code, research, plan, team seats.",
            "modes": {
                "codex": "Code",
                "grok": "Research",
                "plan": "Plan",
            },
            "founder": is_founder(),
            "marketing_url": marketing_url() if callable(marketing_url) else None,
        },
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        # Quiet high-frequency live polls so logging never stalls request threads
        try:
            msg = fmt % a
            if any(
                x in msg
                for x in (
                    "/v1/live/",
                    "/health",
                    "/favicon",
                    "/v1/workers/",
                    "/v1/subagents",
                )
            ):
                return
            print("[http]", msg, flush=True)
        except Exception:
            pass

    def log_error(self, fmt, *a):
        try:
            print("[http-error]", fmt % a, flush=True)
        except Exception:
            pass

    def _sec_headers(self):
        for k, v in security_headers():
            self.send_header(k, v)

    def _client_ip(self) -> str:
        from pocket.auth import _client_ip

        return _client_ip(self.headers, getattr(self, "client_address", None))

    def _reject_unauthorized(self, reason: str = "authentication required"):
        raw = json.dumps({"error": reason, "auth": True}).encode("utf-8")
        self.send_response(401)
        # Do not send WWW-Authenticate: Basic — Edge/Chrome intercept it with a
        # native password dialog and the web/Edge app never finishes sign-in.
        self.send_header("Content-Type", "application/json")
        self._sec_headers()
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _reject_limited(self):
        raw = json.dumps({"error": "too many failed logins — wait 5 minutes"}).encode("utf-8")
        self.send_response(429)
        self.send_header("Content-Type", "application/json")
        self._sec_headers()
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _require_auth(self, path: str = "/") -> bool:
        # Local desk shells stay public on this PC; remote tunnel visitors are locked out
        if path_is_public(
            path,
            headers=self.headers,
            client_address=getattr(self, "client_address", None),
        ):
            return True
        # Node pair token can access transfer-only routes without owner password
        if path.startswith("/v1/node/"):
            try:
                from pocket.node_transfer import verify_pair_token

                nt = (
                    self.headers.get("X-Pocket-Node-Token")
                    or self.headers.get("x-pocket-node-token")
                    or ""
                ).strip()
                if nt and verify_pair_token(nt):
                    return True
            except Exception:
                pass
        ip = self._client_ip()
        if is_rate_limited(ip):
            self._reject_limited()
            return False
        if is_authorized(self.headers):
            clear_auth_failures(ip)
            # Market seats cannot call founder-host control APIs
            p = rbac_principal(self.headers)
            ok_h, msg_h = allow_host_path(p, path)
            if not ok_h:
                self._json(403, {"ok": False, "error": msg_h, "edition": "market"})
                return False
            return True
        # Random public visitors: friendly lock page for desk/phone (not raw JSON 401)
        if is_app_shell(path):
            accept = (self.headers.get("Accept") or "").lower()
            if "application/json" not in accept:
                self._html(public_gate_html(reason="public-lock"))
                return False  # stop — do not fall through to real desk HTML
        record_auth_failure(ip)
        self._reject_unauthorized()
        return False

    def _cors_origin(self) -> str:
        """Allow local desk + Electron + medinatech tunnel phone; never bare wildcard."""
        origin = (self.headers.get("Origin") or "").strip()
        if not origin or origin == "null":
            return "http://127.0.0.1:8787"
        allowed_exact = {
            "http://127.0.0.1:8787",
            "http://localhost:8787",
            "https://pocket.medinatechlabs.net",
            "https://www.pocket.medinatechlabs.net",
            "https://medinatechlabs.net",
            "https://www.medinatechlabs.net",
        }
        if origin in allowed_exact:
            return origin
        if origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:"):
            return origin
        # Same-LAN phone talking to host IP (http://192.168.x.x:8787)
        # Use module-level urlparse — local import would shadow and crash handlers.
        try:
            host = (urlparse(origin).hostname or "").lower()
            if host.startswith("192.168.") or host.startswith("10.") or host.startswith("172."):
                return origin
        except Exception:
            pass
        if "medinatechlabs.net" in origin and origin.startswith("https://"):
            return origin
        return "http://127.0.0.1:8787"

    def _json(self, code: int, obj: dict, extra_headers: Optional[list] = None):
        raw = json.dumps(obj, default=str).encode("utf-8")
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", self._cors_origin())
            self.send_header("Access-Control-Allow-Credentials", "true")
            self._sec_headers()
            if extra_headers:
                for hk, hv in extra_headers:
                    self.send_header(hk, hv)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
            # Client hung up (health poll timeout, Edge nav) — not a server fault
            try:
                self.close_connection = True
            except Exception:
                pass

    def _session_cookie(self, token: str, *, clear: bool = False) -> str:
        """HttpOnly cookie so Cloudflare /desk navigations stay signed in."""
        if clear or not token:
            return "pocket_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"
        # Secure on public HTTPS; local http must omit Secure or cookie never sticks
        host = (self.headers.get("Host") or "").lower()
        xf_proto = (self.headers.get("X-Forwarded-Proto") or self.headers.get("x-forwarded-proto") or "").lower()
        secure = xf_proto == "https" or "medinatechlabs.net" in host
        parts = [
            f"pocket_session={token}",
            "Path=/",
            "Max-Age=2592000",
            "HttpOnly",
            "SameSite=Lax",
        ]
        if secure:
            parts.append("Secure")
        return "; ".join(parts)

    def _text(self, code: int, text: str, ctype: str = "text/markdown; charset=utf-8"):
        raw = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self._sec_headers()
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, html: str, extra_headers: Optional[list] = None):
        try:
            from pocket.ui_kit import enhance

            html = enhance(html)
        except Exception:
            pass
        raw = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._sec_headers()
        if extra_headers:
            for hk, hv in extra_headers:
                self.send_header(hk, hv)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        # Cap body size 2MB
        if n > 2_000_000:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        # Preflight for local desk / Electron
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization, X-Pocket-Access, X-Pocket-Token, X-API-Key, X-Pocket-Device",
        )
        self._sec_headers()
        self.end_headers()

    def do_GET(self):
        try:
            self._do_GET_inner()
        except Exception as e:
            import traceback

            print("[do_GET crash]", e, flush=True)
            traceback.print_exc()
            try:
                self._json(500, {"ok": False, "error": str(e)[:300]})
            except Exception:
                try:
                    self.close_connection = True
                except Exception:
                    pass

    def _do_GET_inner(self):
        u = urlparse(self.path)
        path = u.path.rstrip("/") or "/"
        q = parse_qs(u.query)
        # Fluid kit is public — lock page + every module share one CSS/JS layer
        if path in ("/ui/kit.css", "/assets/ui-kit.css"):
            from pocket.ui_kit import KIT_CSS

            raw = KIT_CSS.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=120")
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return
        if path in ("/ui/kit.js", "/assets/ui-kit.js"):
            from pocket.ui_kit import KIT_JS

            raw = KIT_JS.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=120")
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return
        if not self._require_auth(path):
            return

        if path in ("/which", "/which/", "/which-pocket", "/faces"):
            from pocket.which_pocket import which_html

            return self._html(which_html(self.headers.get("Host", "")))
        if path in ("/", "/tour", "/product", "/present", "/landing", "/home"):
            # Loopback = YOUR POCKET map. Public host = user-facing marketing.
            try:
                from pocket.which_pocket import is_operator_face

                if is_operator_face(self.headers.get("Host", "")):
                    from pocket.which_pocket import which_html

                    return self._html(which_html(self.headers.get("Host", "")))
            except Exception:
                pass
            try:
                from pocket.marketing_landing import landing_html

                return self._html(landing_html())
            except Exception:
                from pocket.product_tour import tour_html

                return self._html(tour_html())
        # Sovereign forge companion site (git vault vision)
        if path in ("/forge", "/forge/", "/git", "/git/"):
            from pocket.forge_web import forge_landing_html

            return self._html(forge_landing_html())
        # Auro meaning browser piece (auro.js + model.json)
        if path in ("/auro", "/auro/"):
            from pocket.auro_meaning import meaning_root

            index = meaning_root() / "auro_web" / "index.html"
            if index.is_file():
                return self._html(index.read_text(encoding="utf-8"))
            return self._html("<h1>Auro web piece missing</h1><p>Unpack vendor/auro_meaning</p>")
        if path.startswith("/auro/"):
            from pocket.auro_meaning import meaning_root

            rel = path[len("/auro/") :].lstrip("/")
            if ".." in rel or rel.startswith("/"):
                return self._json(400, {"error": "bad path"})
            fp = meaning_root() / "auro_web" / rel
            if not fp.is_file():
                return self._json(404, {"error": "not found", "path": rel})
            data = fp.read_bytes()
            ctype = "application/octet-stream"
            if rel.endswith(".js"):
                ctype = "text/javascript; charset=utf-8"
            elif rel.endswith(".json"):
                ctype = "application/json"
            elif rel.endswith(".html"):
                ctype = "text/html; charset=utf-8"
            elif rel.endswith(".mjs"):
                ctype = "text/javascript; charset=utf-8"
            elif rel.endswith(".css"):
                ctype = "text/css; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", self._cors_origin())
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/setup", "/setup/", "/onboard", "/onboard/", "/phoneai/setup"):
            from pocket.setup_flow import setup_html

            return self._html(setup_html())
        # Get / install guide (shareable marketing URL)
        if path in ("/get", "/get/", "/start", "/install", "/install/"):
            from pocket.marketing_landing import get_app_html

            return self._html(get_app_html())
        # Product updates feed (marketing)
        if path in ("/updates", "/updates/", "/changelog", "/changelog/", "/whats-new", "/whats-new/"):
            from pocket.marketing_landing import updates_html

            return self._html(updates_html())
        # --- Docs hub + Researcher License ---
        if path in ("/docs", "/docs/", "/docs/hub", "/docs/hub/"):
            from pocket.docs_hub import docs_hub_html

            return self._html(docs_hub_html())
        if path.startswith("/docs/view/") or path.startswith("/docs/md/"):
            from pocket.docs_hub import render_doc_page

            rel = path.split("/docs/view/", 1)[-1] if "/docs/view/" in path else path.split("/docs/md/", 1)[-1]
            # allow how-to nested paths
            page = render_doc_page(rel)
            if not page:
                return self._json(404, {"ok": False, "error": "doc not found", "path": rel})
            return self._html(page)
        if path in ("/mail", "/mail/", "/agent-mail", "/agent-mail/"):
            from pocket.mail_ui import mail_html

            return self._html(mail_html())
        if path in ("/billing", "/billing/", "/subscribe", "/pay"):
            from pocket.revenuecat import billing_html

            return self._html(billing_html())
        if path in ("/pricing", "/pricing/", "/plans"):
            from pocket.market_ui import join_html

            return self._html(join_html())
        if path in ("/join", "/sold", "/create-seat", "/signup", "/sign-up", "/register"):
            from pocket.market_ui import join_html

            return self._html(join_html())
        if path in ("/login", "/signin", "/sign-in"):
            return self._html(public_gate_html(reason="login"))
        if path in ("/v1/auth/desktop/enter", "/enter-desk"):
            ip = self._client_ip()
            if ip not in ("127.0.0.1", "::1", "localhost"):
                return self._json(403, {"ok": False, "error": "open this on the Pocket PC"})
            from pocket.auth import expected_user
            from pocket.oauth_login import finish_html
            from pocket.users import issue_token

            user = (expected_user() or "pocket").lower()
            tok = issue_token(user)
            html = finish_html(ok=True, token=tok, next_path="/desk")
            raw = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Set-Cookie", self._session_cookie(tok))
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return None
        if path in ("/ecosystem", "/ecosystem/", "/repos", "/family"):
            from pocket.ecosystem import ecosystem_html

            return self._html(ecosystem_html())
        if path in ("/v1/twin", "/api/twin"):
            from pocket.twin_mint import snapshot as twin_snap
            from pocket.rbac import principal as rbac_p

            q = parse_qs(urlparse(self.path).query)
            p = rbac_p(self.headers)
            user = (q.get("user") or [p.get("user") or "phoneai"])[0]
            if (p.get("role") or "none") not in ("admin", "member", "none"):
                user = p.get("user") or user
            if p.get("role") == "member":
                user = p.get("user") or user
            return self._json(200, twin_snap(str(user)))
        if path in ("/network", "/network/", "/v1/network"):
            from pocket.agent_network import html as network_html, snapshot as network_snap

            accept = (self.headers.get("Accept") or "").lower()
            if "json" in accept or path.startswith("/v1/"):
                return self._json(200, network_snap())
            return self._html(network_html())
        if path in ("/studio/agents", "/studio/develop", "/agents/studio"):
            from pocket.agent_network import html as network_html

            return self._html(network_html())
        if path in ("/studio/ship", "/studio/ship-agents", "/agents/ship"):
            from pocket.agent_network import ship_html

            return self._html(ship_html())
        if path in ("/phoneai", "/phoneai/", "/phoneai/site", "/phoneai/www"):
            from pocket.phoneai_landing import landing_html as phoneai_landing_html

            return self._html(phoneai_landing_html())
        if path in ("/phoneai/app", "/phoneai/os", "/phoneai/home", "/kernel", "/kernel/os"):
            from pocket.phoneai_os_ui import phoneai_os_html

            return self._html(phoneai_os_html())
        if path in ("/phoneai/runtime", "/runtime"):
            from pocket.phoneai_landing import runtime_html as phoneai_runtime_html

            return self._html(phoneai_runtime_html())
        if path in ("/tech", "/tech/", "/atlas", "/technology"):
            from pocket.tech_atlas import tech_html

            return self._html(tech_html())
        if path in ("/v1/tech", "/v1/atlas", "/v1/technology"):
            from pocket.tech_atlas import catalog as tech_catalog

            return self._json(200, tech_catalog())
        if path in ("/v1/companion/status", "/v1/live/status"):
            from pocket.live_companion import status as live_status

            return self._json(200, live_status())
        if path in ("/v1/phoneai/kernel", "/v1/kernel"):
            from pocket.phoneai_os_ui import kernel_manifest

            return self._json(200, kernel_manifest())
        if path in ("/v1/phoneai/desk", "/v1/live-desk"):
            from pocket.live_desk import desk as live_desk

            return self._json(200, live_desk())
        if path in ("/v1/phoneai/sessions", "/api/phoneai/sessions"):
            from pocket.agent_runtime import list_phoneai_sessions

            return self._json(200, list_phoneai_sessions())
        if path in ("/v1/phoneai/personas",):
            from pocket.agent_runtime import personas

            return self._json(200, {"ok": True, "personas": personas()})
        if path in ("/v1/phoneai/coder", "/v1/coder", "/api/coder"):
            from pocket.coder_persona import snapshot as coder_snap

            return self._json(200, coder_snap())
        if path in ("/v1/phoneai/space", "/api/phoneai/space"):
            from pocket.phoneai_space import snapshot as phoneai_space

            return self._json(200, phoneai_space())
        if path in ("/v1/phoneai/life", "/api/phoneai/life"):
            from pocket.phone_life import snapshot as phone_life_snap

            return self._json(200, phone_life_snap())
        if path in ("/phoneai/manifest.json", "/phoneai/manifest"):
            return self._json(
                200,
                {
                    "name": "PhoneAI",
                    "short_name": "PhoneAI",
                    "start_url": "/phoneai/app",
                    "display": "standalone",
                    "background_color": "#05060a",
                    "theme_color": "#05060a",
                },
            )
        if path == "/v1/phoneai/photo":
            from pocket.phone_life import PHOTOS

            q = parse_qs(urlparse(self.path).query)
            name = Path((q.get("name") or [""])[0]).name
            fp = PHOTOS / name
            if not name.endswith(".jpg") or not fp.is_file():
                return self._json(404, {"error": "photo not found"})
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "private, max-age=60")
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return None
        if path in ("/phoneai/how", "/phoneai/use", "/how-phoneai"):
            from pocket.phoneai_bridge import how_html

            return self._html(how_html())
        if path in ("/phoneai/work", "/phoneai/twin", "/twin", "/phoneai/desk-code"):
            from pocket.phoneai_os_ui import phoneai_twin_html

            return self._html(phoneai_twin_html())
        if path in ("/phoneai/anti", "/phoneai/antigravity"):
            from pocket.phoneai_os_ui import phoneai_anti_html

            return self._html(phoneai_anti_html())
        if path in ("/phoneai/portal", "/phoneai/pc", "/portal"):
            from pocket.auth import current_user, is_home_lan_client
            from pocket.phoneai_os_ui import phoneai_portal_html
            from pocket.phoneai_portal import mint_portal_token, portal_cookie

            extra = []
            lan = is_home_lan_client(self.headers, getattr(self, "client_address", None))
            seated = bool(current_user(self.headers))
            if lan:
                try:
                    from pocket.passkey import pairing_open

                    pairing_open(minutes=10)
                except Exception:
                    pass
            who = ""
            if seated:
                rec = current_user(self.headers) or {}
                who = str(rec.get("user") or "seat")
            elif lan:
                who = "lan"
            if who:
                tok = mint_portal_token(who)
                host = (self.headers.get("Host") or "").lower()
                xf = (self.headers.get("X-Forwarded-Proto") or "").lower()
                secure = xf == "https" or "medinatechlabs.net" in host or "trycloudflare.com" in host
                extra.append(("Set-Cookie", portal_cookie(tok, secure=secure)))
            return self._html(phoneai_portal_html(), extra_headers=extra or None)
        if path in ("/phoneai/glasses", "/glasses", "/phoneai/hud", "/phoneai/airpods", "/airpods", "/phoneai/wear"):
            from pocket.phoneai_os_ui import phoneai_glasses_html

            return self._html(phoneai_glasses_html())
        if path in ("/phoneai/web", "/phoneai/live-web", "/live-web"):
            from pocket.phoneai_os_ui import phoneai_web_html

            return self._html(phoneai_web_html())
        if path in ("/phoneai/tv", "/tv"):
            from pocket.home_ui import tv_html

            return self._html(tv_html())
        if path in ("/phoneai/doorbell", "/doorbell"):
            from pocket.home_ui import doorbell_html

            return self._html(doorbell_html())
        if path in ("/phoneai/cam", "/phoneai/camera-pc"):
            from pocket.home_ui import cam_phone_html

            return self._html(cam_phone_html())
        if path in ("/phoneai/cam/approve", "/phoneai/cam-approve"):
            from pocket.home_ui import cam_approve_html

            return self._html(cam_approve_html())
        if path in ("/v1/phoneai/home", "/api/phoneai/home"):
            from pocket.home_mesh import snapshot as home_snap

            return self._json(200, home_snap())
        if path in ("/v1/nodes/view", "/v1/node/view"):
            from pocket.home_mesh import list_view_nodes

            return self._json(200, list_view_nodes())
        if path in ("/v1/contracts", "/v1/pocket/contracts"):
            from pocket.contracts import catalog

            return self._json(200, catalog())
        if path in ("/v1/phoneai/tv/frame", "/v1/tv/frame"):
            from pocket.home_mesh import grab_tv_to_phone

            q = parse_qs(urlparse(self.path).query)
            data, meta = grab_tv_to_phone((q.get("id") or [""])[0])
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self._sec_headers()
            self.end_headers()
            try:
                self.wfile.write(data)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                self.close_connection = True
            return None
        if path in ("/v1/phoneai/doorbell/frame", "/v1/doorbell/frame"):
            from pocket.home_mesh import grab_doorbell

            q = parse_qs(urlparse(self.path).query)
            data, meta = grab_doorbell((q.get("id") or [""])[0])
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self._sec_headers()
            self.end_headers()
            try:
                self.wfile.write(data)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                self.close_connection = True
            return None
        if path in ("/v1/phoneai/cam/frame", "/v1/cam/frame"):
            from pocket.home_mesh import grab_webcam, laptop_allowed

            if not laptop_allowed():
                return self._json(403, {"ok": False, "error": "laptop camera needs Allow on the PC"})
            data, meta = grab_webcam()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self._sec_headers()
            self.end_headers()
            try:
                self.wfile.write(data)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                self.close_connection = True
            return None
        if path in ("/v1/phoneai/photos", "/api/phoneai/photos"):
            from pocket.photo_pipe import catalog as photo_cat

            return self._json(200, photo_cat())
        if path in ("/v1/phoneai/portal", "/api/phoneai/portal"):
            from pocket.phoneai_portal import snapshot as portal_snap

            return self._json(200, portal_snap())
        if path in ("/v1/phoneai/portal/windows", "/api/phoneai/portal/windows"):
            from pocket.phoneai_portal import windows as portal_windows

            return self._json(200, portal_windows())
        if path in ("/v1/phoneai/portal/apps", "/api/phoneai/portal/apps"):
            from pocket.desktop import list_apps

            apps = [a for a in list_apps() if a.get("available")]
            return self._json(200, {"ok": True, "apps": apps, "count": len(apps)})
        if path in ("/v1/phoneai/portal/ws", "/api/phoneai/portal/ws"):
            from pocket.phoneai_portal import origin_ok, run_portal_ws, touch_allowed, ws_accept_key
            from pocket.ratelimit import hit as rl_hit

            if not touch_allowed(self.headers, getattr(self, "client_address", None), parse_qs(urlparse(self.path).query)):
                return self._json(403, {"ok": False, "error": "portal session required"})
            if not origin_ok(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "origin blocked"})
            key = (self.headers.get("Sec-WebSocket-Key") or "").strip()
            if (self.headers.get("Upgrade") or "").lower() != "websocket" or not key:
                return self._json(426, {"ok": False, "error": "WebSocket upgrade required"})
            ok_rl, reason = rl_hit("portal_ws", self._client_ip(), kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", ws_accept_key(key))
            self.end_headers()
            try:
                run_portal_ws(self.connection, self.headers, getattr(self, "client_address", None))
            except Exception:
                pass
            self.close_connection = True
            return None
        if path in ("/v1/phoneai/portal/frame", "/api/phoneai/portal/frame"):
            from pocket.phoneai_portal import grab_jpeg, touch_allowed
            from pocket.ratelimit import hit as rl_hit

            q = parse_qs(urlparse(self.path).query)
            if not touch_allowed(self.headers, getattr(self, "client_address", None), q):
                return self._json(403, {"ok": False, "error": "portal session required to view the PC"})
            ok_rl, reason = rl_hit("portal_frame", self._client_ip(), kind="portal_frame")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            target = (q.get("target") or ["desktop"])[0]
            try:
                max_w = int((q.get("max_w") or ["1280"])[0])
            except Exception:
                max_w = 1280
            try:
                quality = int((q.get("q") or q.get("quality") or ["0"])[0])
            except Exception:
                quality = 0
            try:
                hwnd = int((q.get("hwnd") or ["0"])[0])
            except Exception:
                hwnd = 0
            data, meta = grab_jpeg(target=target, max_w=max(640, min(max_w, 1920)), quality=quality, hwnd=hwnd)
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Pocket-Target", str(meta.get("target") or target))
            self._sec_headers()
            self.end_headers()
            try:
                self.wfile.write(data)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                self.close_connection = True
            return None
        if path in ("/v1/phoneai/settings", "/api/phoneai/settings"):
            from pocket.phoneai_settings import snapshot as phoneai_settings

            return self._json(200, phoneai_settings())
        if path in ("/v1/phoneai/anti", "/api/phoneai/anti", "/v1/phoneai/anti/app"):
            from pocket.antigravity_chat import real_app as anti_app

            return self._json(200, anti_app())
        if path in ("/v1/phoneai/anti/frame", "/api/phoneai/anti/frame"):
            from pocket.antigravity_chat import live_frame_jpeg
            from pocket.phoneai_portal import touch_allowed

            if not touch_allowed(self.headers, getattr(self, "client_address", None), parse_qs(urlparse(self.path).query)):
                return self._json(403, {"ok": False, "error": "portal session required"})
            data = live_frame_jpeg()
            if not data:
                # Tiny JPEG so the page does not look "down" when the desktop app is closed.
                data = bytes(
                    b"\xff\xd8\xff\xdb\x00C\x00"
                    + b"\x08" * 64
                    + b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
                    + b"\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08"
                    + b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\xff\xd9"
                )
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self._sec_headers()
            self.end_headers()
            try:
                self.wfile.write(data)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                self.close_connection = True
            return None
        if path in ("/v1/phoneai/github", "/api/phoneai/github"):
            from pocket.phoneai_github import snapshot as gh_snap

            return self._json(200, gh_snap())
        if path in ("/webmcp", "/web-mcp", "/v1/webmcp"):
            from pocket.webmcp import catalog as webmcp_catalog, html as webmcp_html

            accept = (self.headers.get("Accept") or "").lower()
            if "json" in accept or path.startswith("/v1/"):
                q = parse_qs(urlparse(self.path).query)
                return self._json(
                    200,
                    webmcp_catalog(
                        refresh=(q.get("refresh") or [""])[0] in ("1", "true"),
                        url=(q.get("url") or [""])[0],
                        fusion=(q.get("fusion") or [""])[0] in ("1", "true"),
                    ),
                )
            return self._html(webmcp_html())
        if path in ("/api/health",):
            from pocket.phoneai_bridge import health as phoneai_health

            return self._json(200, phoneai_health())
        if path == "/api/substrate":
            from pocket.phoneai_bridge import session_from_bearer, substrate as phoneai_sub

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            return self._json(200, {"substrate": phoneai_sub(), "session_id": sess.get("session_id")})
        if path == "/api/tools":
            from pocket.phoneai_bridge import TOOLS, session_from_bearer

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            return self._json(200, {"session_id": sess.get("session_id"), "tools": TOOLS})
        if path in ("/api/sessions/history", "/api/executions"):
            from pocket.phoneai_bridge import history, session_from_bearer

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            return self._json(200, history(sess))
        if path.startswith("/api/executions/"):
            from pocket.phoneai_bridge import execution_detail, session_from_bearer

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            eid = path.rsplit("/", 1)[-1]
            doc = execution_detail(sess, eid)
            return self._json(404 if doc.get("error") else 200, doc)
        if path in ("/v1/ecosystem", "/v1/repos", "/v1/family"):
            from pocket.ecosystem import catalog

            return self._json(200, catalog())
        if path in ("/v1/clis", "/v1/auth/clis", "/v1/model-clis"):
            from pocket.model_clis import inventory

            return self._json(200, inventory())
        if path == "/v1/auth/providers":
            from pocket.oauth_login import list_providers

            ip = self._client_ip()
            loop = ip in ("127.0.0.1", "::1", "localhost")
            return self._json(200, list_providers(loopback=loop))
        if path.startswith("/v1/auth/oauth/") and path.endswith("/start"):
            from pocket.oauth_login import start_oauth

            provider = path.split("/v1/auth/oauth/", 1)[-1].split("/")[0]
            q = parse_qs(urlparse(self.path).query)
            nxt = (q.get("next") or ["/desk"])[0]
            host = self.headers.get("Host") or "127.0.0.1:8787"
            xf = (self.headers.get("X-Forwarded-Proto") or "").split(",")[0].strip()
            scheme = xf or ("https" if "medinatech" in host.lower() else "http")
            res = start_oauth(provider, base=f"{scheme}://{host}", next_path=nxt)
            return self._json(200 if res.get("ok") else 400, res)
        if path.startswith("/v1/auth/oauth/") and path.endswith("/callback"):
            from pocket.oauth_login import finish_html, finish_oauth

            provider = path.split("/v1/auth/oauth/", 1)[-1].split("/")[0]
            q = parse_qs(urlparse(self.path).query)
            res = finish_oauth(
                provider,
                code=(q.get("code") or [""])[0],
                state=(q.get("state") or [""])[0],
            )
            if res.get("ok") and res.get("token"):
                html = finish_html(ok=True, token=res["token"], next_path=res.get("next") or "/desk")
                raw = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Set-Cookie", self._session_cookie(res["token"]))
                self.send_header("Content-Length", str(len(raw)))
                self._sec_headers()
                self.end_headers()
                self.wfile.write(raw)
                return
            return self._html(finish_html(ok=False, error=res.get("error") or "oauth failed"))
        if path in ("/seats", "/seats/", "/admin/seats", "/sell"):
            from pocket.market_ui import seats_html

            return self._html(seats_html())
        if path in ("/v1/product/sold", "/v1/sold", "/v1/market"):
            from pocket.market import catalog

            return self._json(200, catalog())
        if path in ("/v1/catalog", "/v1/platform/catalog", "/v1/platform-catalog"):
            from pocket.platform_catalog import catalog

            return self._json(200, catalog())
        if path in (
            "/v1/agents/tools",
            "/v1/agent/tools",
            "/v1/agents/toolkit",
            "/v1/mcp/tools",
            "/v1/tools/manifest",
        ):
            from pocket.agents_toolkit import manifest, markdown, write_docs_file

            fmt = (q.get("format") or q.get("fmt") or [""])[0].lower()
            if fmt in ("md", "markdown"):
                return self._text(200, markdown(), content_type="text/markdown; charset=utf-8")
            if fmt in ("write", "file"):
                return self._json(200, write_docs_file())
            return self._json(200, manifest())
        if path in ("/license", "/license/"):
            from pocket.docs_hub import license_page_html

            return self._html(license_page_html())
        if path in ("/license/text", "/license/text/"):
            from pocket.docs_hub import license_text

            return self._text(200, license_text())
        if path in ("/v1/license", "/v1/license/"):
            from pocket.license_gate import license_meta

            return self._json(200, license_meta())

        # --- Desktop Electron package downloads (Researcher License gate) ---
        if path in ("/download", "/download/"):
            from pocket.desktop_releases import download_page_html

            return self._html(download_page_html())
        if path in ("/v1/desktop/releases", "/v1/releases/desktop"):
            from pocket.desktop_releases import catalog

            return self._json(200, catalog())
        if path in ("/download/desktop", "/download/windows", "/download/desktop/windows"):
            from pocket.desktop_releases import preferred_artifact, list_artifacts
            from pocket.license_gate import download_allowed

            qtok = (q.get("license_token") or q.get("token") or [""])[0]
            if not download_allowed(self.headers, qtok):
                return self._json(
                    403,
                    {
                        "ok": False,
                        "error": "Researcher License required",
                        "accept": "POST /v1/license/accept or open /download",
                        "license": "/license",
                    },
                )
            qkind = (q.get("kind") or ["portable"])[0]
            qarch = (q.get("arch") or [None])[0]
            art = preferred_artifact(arch=qarch, kind=qkind)
            if not art:
                arts = list_artifacts()
                return self._json(
                    404,
                    {
                        "error": "no desktop package built yet",
                        "hint": "On host: cd desktop-electron && npm run dist && python -m pocket desktop-pack",
                        "page": "/download",
                        "artifacts": arts,
                    },
                )
            # Redirect to file URL so browsers get Content-Disposition attachment
            loc = art.get("url") or f"/download/files/{art.get('name')}"
            if qtok:
                sep = "&" if "?" in loc else "?"
                loc = f"{loc}{sep}license_token={qtok}"
            self.send_response(302)
            self.send_header("Location", loc)
            self._sec_headers()
            self.end_headers()
            return
        if path.startswith("/download/files/"):
            from pocket.desktop_releases import resolve_file
            from pocket.license_gate import download_allowed
            import mimetypes

            qtok = (q.get("license_token") or q.get("token") or [""])[0]
            if not download_allowed(self.headers, qtok):
                return self._json(
                    403,
                    {
                        "ok": False,
                        "error": "Researcher License required before binary download",
                        "accept": "POST /v1/license/accept",
                        "page": "/download",
                    },
                )
            name = path.split("/download/files/", 1)[-1]
            fp = resolve_file(name)
            if not fp:
                return self._json(404, {"error": "release file not found", "name": name})
            data = fp.read_bytes()
            ctype = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
            if fp.suffix.lower() == ".exe":
                ctype = "application/vnd.microsoft.portable-executable"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{fp.name}"',
            )
            self.send_header("Cache-Control", "private, max-age=300")
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/ui/kit.css", "/assets/ui-kit.css"):
            from pocket.ui_kit import KIT_CSS

            raw = KIT_CSS.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=120")
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return
        if path in ("/ui/kit.js", "/assets/ui-kit.js"):
            from pocket.ui_kit import KIT_JS

            raw = KIT_JS.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=120")
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return
        if path in ("/desk", "/app", "/desktop", "/chat"):
            return self._html(HTML)
        if path in ("/os", "/agent-os", "/systems", "/os/", "/agent-os/", "/systems/"):
            return self._html(OS_HTML)
        if path in ("/phone", "/m", "/mobile", "/phone/", "/m/", "/mobile/"):
            return self._html(phone_html())
        if path in ("/lab", "/lab/", "/lab-hub"):
            from pocket.lab_ui import lab_html

            return self._html(lab_html())
        if path in ("/work", "/work-studio", "/studio/work", "/work/", "/work-studio/"):
            return self._html(work_studio_html())
        if path in ("/power", "/power/", "/command", "/v1/power/ui"):
            from pocket.power_ui import power_html

            return self._html(power_html())
        if path in ("/curiosities", "/lab", "/weird", "/curiosities/"):
            return self._html(curiosities_html())
        if path in ("/phone/manifest.webmanifest", "/m/manifest.webmanifest"):
            data = phone_manifest().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/manifest+json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/developers", "/api", "/docs/api"):
            from pocket.developers_ui import developers_html

            return self._html(developers_html())
        if path in ("/loomgraph", "/loomgraph/", "/graph", "/graph-loop", "/harness/loomgraph"):
            from pocket.loomgraph_ui import loomgraph_html

            return self._html(loomgraph_html())
        if path in ("/studio", "/studio/"):
            return self._html(STUDIO_HTML)
        if path in (
            "/imagine",
            "/imagine/",
            "/studio/imagine",
            "/imagine-studio",
            "/imagine-studio/",
            "/visual",
        ):
            from pocket.imagine_studio_ui import imagine_studio_html

            return self._html(imagine_studio_html())
        if path in ("/bots", "/bots/", "/bot", "/teammates"):
            from pocket.bots_ui import bots_html

            return self._html(bots_html())
        if path in (
            "/studio/create",
            "/studio/creative",
            "/creative",
            "/studio/chat",
            "/create",
        ):
            from pocket.creative_studio_ui import creative_studio_html

            return self._html(creative_studio_html())
        if path in (
            "/community",
            "/studio/community",
            "/share",
            "/studio/share",
        ):
            # Same UI, deep-link to community panel
            from pocket.creative_studio_ui import creative_studio_html

            html = creative_studio_html()
            if "#community" not in html:
                html = html.replace("</body>", "<script>location.hash='community'</script></body>")
            else:
                html = html.replace(
                    "if(location.hash==='#community') showCommunity(true);",
                    "showCommunity(true);",
                )
            return self._html(html)
        if path in (
            "/studio/voice",
            "/voice-studio",
            "/v2v-studio",
            "/studio/voice/",
            "/voice-studio/",
            "/v2v-studio/",
        ):
            from pocket.voice_studio_ui import voice_studio_html

            return self._html(voice_studio_html())
        if path in ("/v1/engines", "/api/engines"):
            from pocket.engines import catalog as engines_catalog

            return self._json(200, engines_catalog())
        if path in ("/v1/eyes", "/api/eyes"):
            from pocket.agent_eyes import catalog as eyes_cat, see as eyes_see
            from pocket.host_control import allow as host_ok

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="eyes")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            q = parse_qs(urlparse(self.path).query)
            which = (q.get("which") or [""])[0]
            if which:
                return self._json(200, eyes_see(which=which))
            return self._json(200, eyes_cat())
        if path in ("/v1/phoneai/shell", "/api/phoneai/shell", "/v1/shell"):
            from pocket.shell_exec import allowed_roots

            return self._json(200, {"ok": True, "roots": allowed_roots(), "post": "POST command,cwd"})
        if path in ("/v1/phoneai/harness", "/api/phoneai/harness", "/v1/harness"):
            return self._json(200, {"ok": True, "product": "POCKET work harness", "arch": "pocket.agent.arch.v1", "post": "POST goal,shell,cwd,engine,agent,seat,grant_id"})
        if path in ("/v1/phoneai/voice-screen", "/api/phoneai/voice-screen", "/v1/voice-screen"):
            return self._json(200, {"ok": True, "product": "voice to screen", "post": "POST text,which"})
        if path in ("/v1/phoneai/wear", "/api/phoneai/wear", "/v1/wear"):
            from pocket.wear import snapshot as wear_snap

            return self._json(200, wear_snap())
        if path in ("/v1/claims", "/v1/invention", "/claims"):
            from pathlib import Path

            root = Path(__file__).resolve().parents[2]
            js = root / "docs" / "research" / "invention_claims.v1.json"
            md = "/docs/research/INVENTION_CLAIMS_2026.md"
            data = {}
            if js.is_file():
                data = json.loads(js.read_text(encoding="utf-8"))
            data.setdefault("ok", True)
            data["markdown"] = md
            data["pdf"] = "/docs/research/INVENTION_CLAIMS_2026.pdf"
            data["inventor"] = data.get("inventor") or {"name": "Alfredo Medina", "lab": "ItsNotAI Labs"}
            return self._json(200, data)
        if path in ("/health", "/v1/health"):
            # Pure liveness — no score()/pillars (14s) and no background work.
            # Class grades live on /v1/class and /v1/ready so Edge/desk stay snappy.
            from pocket import __version__ as _pv, TAGLINE, LAB

            heart = {"ok": True, "interval_ms": 873, "serve_pid": os.getpid()}
            try:
                # module-level Path + time — never re-import (shadows crash do_GET)
                hf = Path.home() / ".pocket" / "runtime_heartbeat.json"
                if hf.exists():
                    raw_h = hf.read_text(encoding="utf-8")
                    # Cap read so a huge/corrupt file cannot stall the handler
                    if len(raw_h) < 200_000:
                        heart = json.loads(raw_h)
                        age = time.time() - float(heart.get("ts") or 0)
                        heart["stale"] = age > 3.0
                        heart["age_ms"] = int(age * 1000)
                        heart["serve_alive"] = True
                        heart["serve_pid"] = os.getpid()
                else:
                    heart["worker"] = False
                    heart["serve_alive"] = True
                    heart["stale"] = False
                    heart["note"] = "runtime-worker optional; serve is answering"
            except Exception:
                pass
            voice_ok = False
            try:
                from pocket.voice_proxy import health as _vh

                voice_ok = bool((_vh() or {}).get("ok"))
            except Exception:
                voice_ok = False
            return self._json(
                200,
                {
                    "ok": True,
                    "service": "pocket",
                    "version": _pv,
                    "upgrade": "3.5",
                    "highlights": [
                        "product_studio_first_class",
                        "phone_pwa_domain",
                        "capsule_webgpu",
                        "life_skills_all_agents",
                        "bearer_session_auth",
                    ],
                    "tagline": TAGLINE,
                    "lab": LAB,
                    "heart": "beating",
                    "heartbeat": heart,
                    "brain": "online",
                    "voice": {"ok": voice_ok, "proxy": "/v1/pocket-voice/health"},
                    "auth": "required-for-app",
                    "product": True,
                    "production": True,
                    "api": "platform",
                    "surfaces": [
                        "landing",
                        "desk",
                        "phone",
                        "work",
                        "working",
                        "api",
                        "studio",
                        "wiki",
                        "swarm",
                        "download",
                    ],
                    "default_codex_cwd": "E:\\PARALLAX-Exchange-Clearinghouse",
                },
            )
        if path in ("/v1/production", "/v1/prod/status"):
            from pocket import __version__ as _pv

            voice = {}
            board = {}
            try:
                from pocket.voice_proxy import health as _vh, ensure_voice

                voice = _vh()
                if not voice.get("ok"):
                    ensure_voice(wait_sec=1.5)
                    voice = _vh()
            except Exception as e:
                voice = {"ok": False, "error": str(e)[:120]}
            try:
                from pocket.working_board import status as board_status

                board = board_status()
            except Exception as e:
                board = {"ok": False, "error": str(e)[:120]}
            damians = {}
            try:
                from pocket.damian_fleet import status as damian_status

                damians = damian_status()
            except Exception as e:
                damians = {"ok": False, "error": str(e)[:120]}
            return self._json(
                200,
                {
                    "ok": True,
                    "production": True,
                    "version": _pv,
                    "host": {"ok": True, "desk": "/desk", "port": 8787},
                    "voice": voice,
                    "working_board": {
                        "ok": board.get("ok"),
                        "counts": board.get("counts"),
                        "goal": board.get("goal"),
                    },
                    "damians": {
                        "ok": damians.get("ok"),
                        "count": damians.get("count"),
                        "running": damians.get("running"),
                        "hearts": damians.get("hearts"),
                        "brains": damians.get("brains"),
                        "headless": damians.get("headless"),
                        "internal": True,
                    },
                    "doctrine": (
                        "Host=API · Edge=product UI · Working=board+tools · "
                        "Voice=proxied · Damians=internal keepers · Coding agents=separate"
                    ),
                },
            )
        if path in ("/v1/runtime", "/api/runtime", "/v1/host", "/v1/runtime/status"):
            from pocket.host_runtime import status as runtime_status

            return self._json(200, runtime_status())
        if path in ("/v1/setup", "/api/setup"):
            from pocket.host_runtime import setup_snapshot

            return self._json(200, setup_snapshot())
        if path in ("/v1/runtime/heartbeat", "/v1/heartbeat"):
            # module-level Path/time only — local pathlib import shadows Path for all of do_GET
            hf = Path.home() / ".pocket" / "runtime_heartbeat.json"
            if not hf.exists():
                return self._json(
                    200,
                    {
                        "ok": True,
                        "worker": False,
                        "serve_alive": True,
                        "serve_pid": os.getpid(),
                        "note": "start: python -m pocket runtime-worker (optional keep-alive)",
                    },
                )
            try:
                data = json.loads(hf.read_text(encoding="utf-8"))
                data["age_ms"] = int((time.time() - float(data.get("ts") or 0)) * 1000)
                data["alive"] = data["age_ms"] < 2500
                data["serve_alive"] = True
                data["serve_pid"] = os.getpid()
                return self._json(200, data)
            except Exception as e:
                return self._json(200, {"ok": False, "error": str(e)[:120]})
        if path == "/v1/ready":
            from pocket.production import checklist

            out = checklist()
            try:
                from pocket.first_class import report as fc_report

                out["first_class"] = fc_report().get("score")
            except Exception:
                pass
            try:
                from pocket.platform_api import health_domains, catalog as api_catalog

                out["platform_surface"] = health_domains()
                out["api_route_count"] = api_catalog().get("route_count")
            except Exception:
                pass
            return self._json(200, out)
        if path in ("/v1/platform/api", "/v1/api/surface", "/v1/surface"):
            from pocket.platform_api import catalog as api_catalog, health_domains

            c = api_catalog()
            c["health"] = health_domains()
            return self._json(200, c)
        if path in ("/v1/benchmarks", "/v1/benchmarks/official", "/v1/class/benchmarks"):
            from pocket.official_benchmarks import run_official_suite

            return self._json(200, run_official_suite())
        if path in ("/v1/class", "/v1/first-class", "/v1/grade"):
            from pocket.first_class import report as fc_report

            return self._json(200, fc_report())
        if path in ("/v1/dreams", "/v1/dream"):
            from pocket.dream_mode import list_dreams, status as dream_status

            st = dream_status()
            st["recent"] = list_dreams(12)
            return self._json(200, st)
        if path in ("/v1/duels",):
            from pocket.agent_duels import list_duels

            return self._json(200, {"ok": True, "duels": list_duels()})
        if path.startswith("/v1/duels/"):
            from pocket.agent_duels import get_duel

            did = path.rstrip("/").split("/")[-1]
            d = get_duel(did)
            if not d:
                return self._json(404, {"ok": False, "error": "duel not found"})
            return self._json(200, d)
        if path in ("/v1/capsules", "/v1/time-capsules"):
            from pocket.time_capsules import status as cap_status

            return self._json(200, cap_status())
        if path in ("/v1/serendipity", "/v1/links"):
            from pocket.serendipity import find_links

            return self._json(200, find_links(limit=10))
        if path in ("/v1/proofs", "/v1/receipts"):
            from pocket.proof_chain import status as proof_status

            return self._json(200, proof_status())
        if path in ("/v1/proofs/verify", "/v1/receipts/verify"):
            from pocket.proof_chain import verify_chain

            return self._json(200, verify_chain())
        if path == "/v1/legal":
            legal = DOCS_ROOT_MAIN / "LEGAL.md"
            if legal.exists():
                return self._text(200, legal.read_text(encoding="utf-8"))
            return self._json(404, {"ok": False, "error": "LEGAL.md missing"})
        if path == "/v1/ai/openapi":
            return self._json(200, _openapi_spec())
        if path == "/v1/product":
            from pocket.product import doctor

            return self._json(200, doctor())
        if path == "/v1/doctor":
            from pocket.product import doctor

            return self._json(200, doctor())
        if path == "/v1/organism":
            st = status()
            return self._json(200, st.get("organism") or organism_snapshot())
        if path == "/v1/cost/20-users":
            return self._json(200, cost_analysis_20_users())
        if path in ("/v1/terminals", "/v1/console", "/v1/consoles"):
            # list_terminals is module-level — only import catalog (local list_terminals
            # would UnboundLocalError every other terminal route in do_GET)
            from pocket.terminals import catalog as term_catalog

            return self._json(200, {"terminals": list_terminals(), **term_catalog()})
        if path.startswith("/v1/terminals/"):
            tid = path.split("/v1/terminals/", 1)[-1].split("/")[0]
            if path.endswith("/log") or path.endswith(tid):
                t = get_terminal(tid)
                if not t:
                    return self._json(404, {"error": "terminal not found"})
                return self._json(200, t)
        if path.startswith("/v1/deploys/") and path.endswith("/log"):
            did = path.split("/v1/deploys/", 1)[-1].replace("/log", "")
            return self._json(200, deploy_log_tail(did))
        if path == "/v1/status":
            try:
                return self._json(200, status())
            except Exception as e:
                return self._json(
                    200,
                    {
                        "ok": True,
                        "product": "POCKET",
                        "version": __import__("pocket").__version__,
                        "degraded": True,
                        "error": str(e)[:300],
                        "local": f"http://127.0.0.1:{PORT}/desk",
                        "engine": {"worker_alive": _worker_started},
                    },
                )
        if path in ("/v1/auth/device/mint", "/v1/auth/pair/mint"):
            from pocket.device_pair import mint as device_mint

            r = device_mint(client_ip=self._client_ip())
            return self._json(200 if r.get("ok") else 403, r)
        if path in ("/v1/auth/passkey", "/v1/auth/passkey/begin"):
            from pocket.auth import is_home_lan_client
            from pocket.passkey import begin_login, begin_register, can_register, snapshot as pk_snap

            q = parse_qs(urlparse(self.path).query)
            kind = (q.get("kind") or ["login"])[0]
            host = (self.headers.get("Host") or "127.0.0.1:8787")
            if kind in ("register", "create"):
                lan = is_home_lan_client(self.headers, getattr(self, "client_address", None))
                seated = bool(rbac_principal(self.headers).get("user"))
                if not can_register(lan=lan, authed=seated):
                    return self._json(
                        403,
                        {
                            "ok": False,
                            "error": "pair_required",
                            "hint": "Open Portal on home Wi-Fi once, or on the PC tap Allow this phone, then Face ID.",
                        },
                    )
                return self._json(200, begin_register(host=host))
            data = begin_login(host=host)
            data.update(pk_snap())
            return self._json(200, data)
        if path == "/v1/auth/me":
            u = rbac_principal(self.headers)
            if (u.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            try:
                from pocket.market import seat_flags

                u = {**u, **seat_flags(u)}
            except Exception:
                pass
            return self._json(200, {"ok": True, "user": u})
        if path in ("/v1/admin/invites", "/v1/auth/invites"):
            from pocket.users import list_invites, list_users

            p = rbac_principal(self.headers)
            if not is_admin(p):
                return self._json(403, {"ok": False, "error": "admin only"})
            return self._json(
                200,
                {
                    "ok": True,
                    "invites": list_invites(),
                    "users": list_users(),
                    "note": "Users create their OWN accounts with a seat key. Owner stays owner.",
                },
            )
        if path == "/v1/live":
            return self._json(200, probe_all())
        if path == "/v1/usage":
            return self._json(200, get_usage())
        if path == "/v1/tokenomics":
            return self._json(200, token_snapshot())
        if path == "/v1/platform":
            return self._json(200, platform_manifest())
        if path == "/v1/deploys":
            return self._json(200, {"deploys": list_deploys()})
        if path == "/v1/workspace/tools":
            p = rbac_principal(self.headers)
            if not is_founder(p):
                # Market: tools list for their space only — no founder product roots
                from pocket.platform_space import space_summary

                return self._json(
                    200,
                    {
                        "ok": True,
                        "edition": "market",
                        "founder_files": False,
                        "space": space_summary(p.get("user") or "anonymous"),
                    },
                )
            ws = (q.get("workspace") or ["workspace"])[0]
            return self._json(200, workspace_tools(ws))
        # Market virtual + local sandbox explorer (never founder disk)
        if path in ("/v1/space", "/v1/space/me"):
            from pocket.platform_space import space_summary

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if is_founder(p):
                return self._json(
                    200,
                    {
                        "ok": True,
                        "edition": "founder",
                        "note": "Founder POCKET uses full local host paths; /v1/space is for market seats.",
                        "user": p.get("user"),
                    },
                )
            return self._json(200, space_summary(p.get("user") or ""))
        if path == "/v1/space/list":
            from pocket.platform_space import list_space

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            user = p.get("user") or ""
            if is_founder(p) and (q.get("user") or [None])[0]:
                user = (q.get("user") or [user])[0]
            elif is_founder(p):
                return self._json(
                    400,
                    {"ok": False, "error": "founder: pass ?user= for tenant peek, or use host paths"},
                )
            rel = (q.get("path") or q.get("rel") or ["files"])[0]
            return self._json(200, list_space(user, rel))
        if path == "/v1/grok/can-start":
            return self._json(200, can_codex_start_grok())
        if path == "/v1/safety":
            from pocket.safety import policy_summary

            return self._json(200, policy_summary())
        if path == "/v1/device":
            from pocket.device import device_from_request

            # Public-ish after auth: report how server sees this client
            dev = device_from_request(self.headers, {})
            try:
                from pocket.aether_device import profile as hw_profile

                return self._json(200, {"ok": True, "device": dev, "hardware": hw_profile()})
            except Exception:
                return self._json(200, {"ok": True, "device": dev})
        if path in ("/v1/hardware", "/v1/phone/hardware", "/v1/aether"):
            from pocket.aether_device import profile as hw_profile

            return self._json(200, hw_profile())

        # --- Sellable AI API (headless agents product) ---
        if path in ("/v1/ai", "/v1/ai/pricing"):
            from pocket.sell_api import product_manifest

            return self._json(200, product_manifest())
        if path == "/v1/ai/agents":
            from pocket.agents import list_agents

            agents = list_agents(sellable_only=True)
            return self._json(200, {"ok": True, "agents": agents, "count": len(agents)})
        if path.startswith("/v1/ai/agents/"):
            from pocket.agents import get_agent

            aid = path.split("/v1/ai/agents/", 1)[-1].split("/")[0]
            a = get_agent(aid)
            if not a:
                return self._json(404, {"ok": False, "error": "agent not found"})
            return self._json(200, {"ok": True, "agent": a})
        if path == "/v1/ai/keys":
            from pocket.sell_api import keys_list

            p = rbac_principal(self.headers)
            if is_admin(p):
                return self._json(200, keys_list())
            return self._json(200, keys_list(owner=p.get("user") or ""))
        if path == "/v1/ai/usage":
            from pocket.api_keys import extract_bearer, usage_for, verify_key

            p = rbac_principal(self.headers)
            raw = extract_bearer(self.headers)
            kid = ""
            if raw:
                rec = verify_key(raw)
                kid = (rec or {}).get("id") or ""
            if kid:
                return self._json(200, usage_for(kid))
            if is_admin(p):
                return self._json(200, usage_for(""))
            return self._json(200, usage_for(owner=p.get("user") or ""))
        if path.startswith("/v1/ai/jobs/"):
            jid = path.split("/v1/ai/jobs/", 1)[-1].split("/")[0]
            job = get(jid)
            if not job:
                return self._json(404, {"ok": False, "error": "job not found"})
            p = rbac_principal(self.headers)
            if job.get("owner") and not can_access_owned(p, job.get("owner") or ""):
                return self._json(403, {"ok": False, "error": "not your job"})
            return self._json(
                200,
                {
                    "ok": True,
                    "id": job.get("id"),
                    "status": job.get("status"),
                    "agent_id": job.get("agent_id"),
                    "mode": job.get("mode"),
                    "engine": job.get("engine"),
                    "result": job.get("result") or "",
                    "error": job.get("error") or "",
                    "created_at": job.get("created_at"),
                    "finished_at": job.get("finished_at"),
                },
            )

        if path == "/v1/desktop/apps":
            from pocket.desktop import list_apps

            return self._json(200, {"apps": list_apps()})
        # --- First-class GitHub ---
        if path in ("/v1/github", "/v1/github/status"):
            from pocket.github_hub import status as gh_status

            return self._json(200, gh_status())
        if path in ("/v1/github/repos",):
            from pocket.github_hub import list_repos

            q = parse_qs(urlparse(self.path).query)
            lim = int((q.get("limit") or ["20"])[0] or 20)
            return self._json(200, list_repos(lim))
        if path in ("/v1/github/issues",):
            from pocket.github_hub import list_issues

            q = parse_qs(urlparse(self.path).query)
            lim = int((q.get("limit") or ["15"])[0] or 15)
            repo = (q.get("repo") or [""])[0]
            return self._json(200, list_issues(lim, repo=repo))
        if path in ("/v1/github/prs", "/v1/github/pulls"):
            from pocket.github_hub import list_prs

            q = parse_qs(urlparse(self.path).query)
            lim = int((q.get("limit") or ["15"])[0] or 15)
            repo = (q.get("repo") or [""])[0]
            return self._json(200, list_prs(lim, repo=repo))
        # --- In-chat app previews ---
        if path in ("/v1/preview", "/v1/previews"):
            from pocket.app_preview import status as preview_status

            return self._json(200, preview_status())
        if path in ("/v1/work-surface", "/v1/hierarchy", "/v1/layers"):
            from pocket.work_surface import hierarchy, list_drafts, harness_layers

            h = hierarchy()
            h["drafts"] = list_drafts(12)
            h["harness"] = harness_layers()
            return self._json(200, h)
        if path in ("/v1/drafts",):
            from pocket.work_surface import list_drafts

            q = parse_qs(urlparse(self.path).query)
            lim = int((q.get("limit") or ["40"])[0] or 40)
            return self._json(200, list_drafts(lim))
        if path.startswith("/v1/drafts/"):
            from pocket.work_surface import get_draft

            did = path.split("/v1/drafts/", 1)[-1].split("/")[0]
            return self._json(200, get_draft(did))
        if path.startswith("/v1/preview/"):
            from pocket.app_preview import get_preview, read_html_file

            pid = path.split("/v1/preview/", 1)[-1].split("/")[0].split("?")[0]
            # Prefer HTML document for iframe src; ?json=1 for metadata
            q = parse_qs(urlparse(self.path).query)
            if (q.get("json") or ["0"])[0] in ("1", "true", "yes"):
                return self._json(200, get_preview(pid))
            html = read_html_file(pid)
            if html is None:
                return self._json(404, {"error": "preview not found", "id": pid})
            return self._html(html)
        if path == "/v1/guppy":
            from pocket.guppy import identity
            from pocket.autonomy import list_schedules, runner_status

            return self._json(
                200,
                {
                    **identity(),
                    "schedules": list_schedules(),
                    "runner": runner_status(),
                },
            )
        if path == "/v1/autonomy/schedules":
            from pocket.autonomy import list_schedules, runner_status

            return self._json(200, {"schedules": list_schedules(), "runner": runner_status()})
        if path == "/v1/live/events":
            from pocket.live_events import list_events, snapshot

            after = int((q.get("after") or ["0"])[0] or 0)
            return self._json(
                200,
                {
                    "events": list_events(after_seq=after, limit=100),
                    "snapshot": snapshot(),
                },
            )
        if path in ("/v1/live/vision", "/v1/vision"):
            from pocket.live_vision import latest_frame, ensure_vision

            ensure_vision()
            include = (q.get("image") or ["1"])[0] != "0"
            return self._json(200, latest_frame(include_image=include))
        if path in ("/v1/vision/observe", "/v1/observe"):
            from pocket.vision_core import observe

            force = (q.get("force") or ["0"])[0] in ("1", "true", "yes")
            return self._json(
                200,
                observe(with_ui_map=True, with_ocr=True, with_understand=True, force=force),
            )
        if path == "/v1/vision/ui_map":
            from pocket.vision_core import build_ui_map

            return self._json(200, build_ui_map())
        if path in ("/v1/vision/understand", "/v1/pixel/understand", "/v1/pixel/translate"):
            force = (q.get("force") or ["0"])[0] in ("1", "true", "yes")
            if not force:
                from pocket.vision_core import last_observation

                cached = last_observation(max_age=1e9)
                return self._json(
                    200,
                    {
                        "ok": bool(cached.get("ok")),
                        "cached": True,
                        "source": "last_observation",
                        "brief": cached.get("brief"),
                        "page_hint": cached.get("page_hint"),
                        "error": cached.get("error"),
                        "hint": "GET ?force=1 to walk; default is cache-only",
                    },
                )
            from pocket.pixel_translator import understand

            return self._json(200, understand(include_image=False))
        if path in ("/v1/pixel/text", "/v1/vision/ocr"):
            force = (q.get("force") or ["0"])[0] in ("1", "true", "yes")
            if not force:
                from pocket.vision_core import last_observation

                cached = last_observation(max_age=1e9)
                return self._json(
                    200,
                    {
                        "ok": bool(cached.get("ok")),
                        "cached": True,
                        "plain_text": cached.get("ocr_plain") or "",
                        "lines": cached.get("ocr_lines") or [],
                        "error": cached.get("error"),
                    },
                )
            from pocket.pixel_translator import translate_to_text_only

            return self._json(200, translate_to_text_only())
        if path in ("/v1/vision/page", "/v1/page/render", "/v1/vision/full"):
            from pocket.page_renderer import render_full_page

            q = parse_qs(urlparse(self.path).query)
            max_ui = int((q.get("max_ui") or ["800"])[0] or 800)
            grid = int((q.get("grid") or ["5"])[0] or 5)
            want_img = (q.get("image") or ["0"])[0] == "1"
            force = (q.get("force") or ["0"])[0] in ("1", "true", "yes")
            return self._json(
                200,
                render_full_page(
                    max_ui=max_ui,
                    include_ocr=True,
                    include_visual=True,
                    include_image=want_img,
                    visual_grid=grid,
                    force=force,
                ),
            )
        if path in ("/v1/vision/stream", "/v1/vision/stream/latest"):
            from pocket.page_renderer import stream_latest, stream_status

            q = parse_qs(urlparse(self.path).query)
            after = int((q.get("after") or ["0"])[0] or 0)
            return self._json(200, {**stream_latest(after_seq=after), "status": stream_status()})
        if path == "/v1/vision/stream/status":
            from pocket.page_renderer import stream_status

            return self._json(200, stream_status())
        if path == "/v1/vision/find":
            from pocket.page_renderer import find_symbols

            q = parse_qs(urlparse(self.path).query)
            query = (q.get("q") or q.get("query") or [""])[0]
            return self._json(200, {"ok": True, "query": query, "hits": find_symbols(query)})
        if path == "/v1/api":
            # Single catalog — platform_api is source of truth for new surface
            from pocket.platform_api import catalog as api_catalog
            from pocket.skill_suite import skill_count

            cat = api_catalog()
            # Legacy nested groups kept for older clients
            return self._json(
                200,
                {
                    **cat,
                    "skill_count": skill_count(),
                    "legacy_groups": {
                        "vision": {
                            "understand": "GET /v1/vision/understand",
                            "page_full": "GET /v1/vision/page?max_ui=800&grid=5",
                            "page_post": "POST /v1/vision/page  body:{max_ui,ocr,visual,image,grid}",
                            "pixel_text": "GET /v1/pixel/text",
                            "live_frame": "GET /v1/live/vision",
                            "stream": "GET /v1/vision/stream?after=0",
                            "stream_start": "POST /v1/vision/stream/start  body:{interval,max_ui}",
                            "stream_stop": "POST /v1/vision/stream/stop",
                            "stream_status": "GET /v1/vision/stream/status",
                            "find": "GET /v1/vision/find?q=Save  or  POST /v1/vision/find",
                            "click": "POST /v1/vision/click",
                            "observe": "GET /v1/vision/observe",
                            "ui_map": "GET /v1/vision/ui_map",
                        },
                        "agents": {
                            "chat": "POST /v1/orchestrator/chat",
                            "plan": "POST /v1/orchestrator/plan",
                            "skill": "POST /v1/skills/run  body:{skill:page_render|stream_start|…}",
                            "spawn": "POST /v1/workers/spawn",
                            "campaign": "POST /v1/campaigns/run",
                            "bridge_open": "POST /v1/bridge/open",
                        },
                        "studio": {
                            "ui": "GET /studio",
                            "status": "GET /v1/studio",
                            "auto": "POST /v1/studio/auto",
                            "render": "POST /v1/studio/render  presets: rotato_phone|x_screencast|macbook_web|clean_demo",
                            "batch": "POST /v1/studio/batch",
                        },
                        "imagine": {
                            "ui": "GET /imagine",
                            "status": "GET /v1/imagine",
                            "gallery": "GET /v1/imagine/gallery",
                            "compose": "POST /v1/imagine/compose  body:{mode:rotato_phone|macbook_web|clean, source:live|last, image_b64?}",
                            "file": "GET /v1/imagine/file?name=",
                            "product_dir": "OneDrive/imagine-studio (Creative Muse seed)",
                        },
                        "fusion": {
                            "remake": "POST /v1/fusion/remake  → RFE-v1 FULL_SYNTHESIS",
                            "page": "GET /v1/vision/page",
                        },
                        "rfe": {
                            "status": "GET /v1/rfe",
                            "synthesize": "POST /v1/rfe/synthesize  body:{instruction_set,refresh,max_ui}",
                            "verify": "POST /v1/rfe/verify",
                            "research": "Documents/POCKET_Research/RFE_Recursive_Fusion_Engine/",
                            "gold_standard": "wf1 ≥600 symbols → HTML + 3D + GLSL + signed packet",
                        },
                        "record": {
                            "start": "POST /v1/record/start",
                            "stop": "POST /v1/record/stop",
                            "status": "GET /v1/record/status",
                        },
                    },
                    "skills_vision": [
                        "page_render",
                        "full_page",
                        "page_symbols",
                        "stream_start",
                        "stream_stop",
                        "stream_latest",
                        "understand",
                        "pixel_text",
                        "see_screen",
                        "fusion_remake",
                        "imagine_compose",
                    ],
                    "skills_studio": [
                        "studio_auto",
                        "studio_render",
                        "viral_pack",
                    ],
                    "vcomp": {
                        "open": "POST /v1/vcomp/open",
                        "status": "GET /v1/vcomp",
                        "sense": "POST /v1/vcomp/sense",
                        "act": "POST /v1/vcomp/act",
                        "shell": "POST /v1/vcomp/shell",
                        "term": "POST /v1/vcomp/term",
                    },
                    "missions": {
                        "start": "POST /v1/missions/start  body:{goal,queue,max_hours}",
                        "list": "GET /v1/missions",
                        "enqueue": "POST /v1/missions/enqueue",
                        "stop": "POST /v1/missions/stop",
                    },
                    "workflows": {
                        "catalog": "GET /v1/workflows",
                        "run": "POST /v1/workflows/run  body:{id:wf1|wf2|wf3|wf4|wf5|all}",
                    },
                    "note": "Fusion-Sense is the baseline (wf1). RFE remake, vcomp/missions, product-native phone/web, NEXUS, tour at /tour. Not a CLI paste.",
                },
            )
        if path == "/v1/workers/dynamic":
            from pocket.dynamic_worker import list_active

            return self._json(200, {"workers": list_active()})
        if path == "/v1/subagents":
            from pocket.subagents_panel import list_subagents
            from pocket.mesh_disk import status as mesh_status

            r = list_subagents()
            r["mesh"] = mesh_status()
            return self._json(200, r)
        if path in ("/v1/harness", "/v1/agentic-harness"):
            from pocket.agentic_harness import harness_status

            return self._json(200, harness_status())
        if path in ("/v1/harness/live", "/v1/subagents/live"):
            from pocket.agentic_harness import list_live

            q = parse_qs(urlparse(self.path).query)
            return self._json(
                200,
                list_live(
                    session_id=(q.get("session") or q.get("session_id") or [""])[0],
                    job_id=(q.get("job") or q.get("job_id") or [""])[0],
                ),
            )
        if path == "/v1/subagents/running":
            from pocket.subagents_panel import list_running

            return self._json(200, list_running())
        if path == "/v1/mesh":
            from pocket.mesh_disk import status as mesh_status
            from pocket.agent_hook import ensure_mesh_hook

            ensure_mesh_hook()
            return self._json(200, mesh_status())
        # --- Node-to-node transfer + pixel virtual memory ---
        if path in ("/v1/node", "/v1/node/status", "/v1/nodes"):
            from pocket.node_transfer import status as node_status

            return self._json(200, node_status())
        if path in ("/v1/node/hello",):
            from pocket.node_transfer import hello

            return self._json(200, hello())
        if path in ("/v1/node/offers", "/v1/node/tray"):
            from pocket.node_transfer import list_offers, verify_pair_token

            nt = (self.headers.get("X-Pocket-Node-Token") or self.headers.get("x-pocket-node-token") or "").strip()
            peer = verify_pair_token(nt) if nt else None
            if not peer and not is_authorized(self.headers):
                return self._json(401, {"ok": False, "error": "auth or pair token required"})
            q = parse_qs(urlparse(self.path).query)
            inc = (q.get("all") or ["0"])[0] in ("1", "true", "yes")
            return self._json(200, list_offers(include_claimed=inc))
        if path in ("/v1/sandbox", "/v1/agent-sandbox"):
            from pocket.agent_sandbox import status as sandbox_status, list_profiles

            st = sandbox_status()
            st["profiles_detail"] = list_profiles().get("profiles")
            return self._json(200, st)
        # PROTO-CAPSULE-WASM-009 multi-sandbox + WebGPU
        if path in ("/v1/capsule", "/v1/capsules/sandbox", "/v1/multi-sandbox"):
            from pocket.protocols.multi_sandbox_capsule import status as capsule_status

            return self._json(200, capsule_status())
        if path in ("/v1/capsule/webgpu", "/v1/webgpu", "/v1/webgpu/probe"):
            from pocket.protocols.multi_sandbox_capsule import probe_webgpu

            return self._json(200, probe_webgpu())
        if path in ("/v1/capsule/list", "/v1/capsules/live"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            return self._json(200, capsule_manager().list())
        if path in ("/v1/protocols/capsule", "/v1/protocol/capsule", "/v1/protocols/wasm-capsule"):
            from pocket.protocols.multi_sandbox_capsule import protocol_manifest

            return self._json(200, protocol_manifest())
        # --- Ten major protocols + POCKET identity (every agent / model) ---
        if path in (
            "/v1/protocols",
            "/v1/protocol",
            "/v1/platform/protocols",
            "/v1/protocols/catalog",
        ):
            from pocket.protocols.platform_protocols import manifest

            return self._json(200, manifest())
        if path in (
            "/v1/protocols/status",
            "/v1/protocol/status",
            "/v1/platform/protocols/status",
        ):
            from pocket.protocols.platform_protocols import platform_protocols_status

            return self._json(200, platform_protocols_status())
        if path in ("/v1/identity", "/v1/whoami", "/v1/pocket/identity", "/v1/agents/identity"):
            from pocket.pocket_identity import agent_self_description

            return self._json(200, agent_self_description())
        if path in ("/v1/doctrine", "/v1/pocket/doctrine", "/v1/laws"):
            from pocket.doctrine import manifesto

            return self._json(200, manifesto())
        if path in ("/v1/doctrine/beings", "/v1/beings", "/v1/doctrine/agents", "/v1/doctrine/organisms"):
            from pocket.being_doctrine import catalog

            return self._json(200, catalog())
        if path.startswith("/v1/doctrine/") and path.count("/") >= 3:
            from pocket.being_doctrine import being_payload

            slug = path.split("/v1/doctrine/", 1)[-1].strip("/")
            if slug and slug not in ("beings", "agents", "organisms"):
                payload = being_payload(slug)
                return self._json(200 if payload.get("ok") else 404, payload)
        if path in ("/v1/which", "/v1/which-pocket"):
            from pocket.which_pocket import summary

            return self._json(200, summary(self.headers.get("Host", "")))
        # --- Recursive Agent Harnesses (RAH) ---
        if path in ("/v1/rah", "/v1/rah/status", "/v1/recursive-harness", "/v1/rah/health"):
            from pocket.rah import status as rah_status, list_runs, manifest as rah_manifest
            from pocket.work_grant import contracts as rah_contracts

            return self._json(
                200,
                {**rah_status(), "manifest": rah_manifest(), "contracts": rah_contracts(), "runs": list_runs(limit=20)},
            )
        if path in ("/v1/rah/contracts", "/v1/contracts/rah"):
            from pocket.work_grant import contracts as rah_contracts

            return self._json(200, rah_contracts())
        if path in ("/v1/protocols/rah", "/v1/protocol/rah"):
            from pocket.rah import manifest as rah_manifest

            return self._json(200, rah_manifest())
        if path.startswith("/v1/rah/runs/"):
            from pocket.rah import get_run

            rid = path.split("/v1/rah/runs/", 1)[-1].strip("/")
            run = get_run(rid)
            if not run:
                return self._json(404, {"ok": False, "error": "rah run not found", "run_id": rid})
            return self._json(200, run)
        if path in ("/v1/neuro", "/v1/neuro/think", "/v1/neuro-think"):
            from pocket.neuro_think import think as neuro_think

            qg = (q.get("q") or q.get("prompt") or [""])[0]
            mode = (q.get("mode") or [""])[0]
            return self._json(200, neuro_think(qg or "status", mode=mode or "grok"))
        if path in ("/v1/foundations", "/v1/ai/foundations", "/v1/models/foundations"):
            from pocket.foundations import catalog as foundations_catalog

            return self._json(200, foundations_catalog())
        # --- Internal models as modules + genetic flow ---
        if path in (
            "/v1/internal-models",
            "/v1/internal_models",
            "/v1/models/internal",
            "/v1/genetic",
            "/v1/genetic/status",
        ):
            from pocket.internal_models import list_models, list_runs, pick_for_goal

            return self._json(
                200,
                {
                    "ok": True,
                    "schema": "pocket.internal_models.v1",
                    "doctrine": "Internal models are modules that execute the genetic flow.",
                    "models": list_models(),
                    "pick": pick_for_goal("general", limit=4),
                    "runs": list_runs(limit=12),
                    "modes": ["genetic", "genetic_flow", "internal", "internal_models"],
                    "skills": ["internal_models", "genetic_flow", "genetic_status", "express_model"],
                    "apis": {
                        "catalog": "GET /v1/internal-models",
                        "run": "POST /v1/genetic/run",
                        "express": "POST /v1/internal-models/express",
                    },
                },
            )
        if path.startswith("/v1/genetic/runs/"):
            rid = path.split("/v1/genetic/runs/", 1)[-1].strip("/")
            from pathlib import Path
            import json as _json

            fp = Path.home() / ".pocket" / "genetic_flow" / f"{rid}.json"
            if not fp.is_file():
                return self._json(404, {"ok": False, "error": "genetic run not found", "run_id": rid})
            try:
                return self._json(200, _json.loads(fp.read_text(encoding="utf-8")))
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)[:200]})
        # --- Economic domain (wallets · twins · clearing · Parallax hooks) ---
        if path in ("/v1/economy", "/v1/economy/status", "/v1/econ"):
            from pocket.economy import snapshot

            return self._json(200, snapshot())
        if path in ("/v1/billing", "/v1/revenuecat", "/v1/billing/status"):
            from pocket.revenuecat import status as rc_status

            return self._json(200, rc_status())
        if path in ("/v1/economy/protocols", "/v1/economy/protocol"):
            from pocket.economy import protocols as econ_protocols

            return self._json(200, econ_protocols())
        if path in ("/v1/economy/wallets", "/v1/wallets"):
            from pocket.economy import list_wallets

            return self._json(200, list_wallets())
        if path in ("/v1/economy/twins", "/v1/twins", "/v1/twin-wallets"):
            from pocket.economy import list_twins

            return self._json(200, list_twins())
        if path in ("/v1/economy/fees", "/v1/economy/schedule"):
            from pocket.economy import fee_schedule

            return self._json(200, fee_schedule())
        # --- Install slices (one-line install hub for users & AI agents) ---
        if path in ("/install", "/install/", "/v1/install", "/v1/install/slices"):
            from pocket.install_hub import slices_json, install_hub_html

            host = (self.headers.get("Host") or "127.0.0.1:8787").strip()
            scheme = "https" if host.endswith(":443") or "medinatech" in host else "http"
            if "x-forwarded-proto" in {k.lower() for k in self.headers.keys()}:
                scheme = (self.headers.get("X-Forwarded-Proto") or scheme).split(",")[0].strip()
            host_base = f"{scheme}://{host}"
            if path.endswith("slices") or "application/json" in (
                self.headers.get("Accept") or ""
            ).lower():
                return self._json(200, slices_json(host_base=host_base))
            return self._html(install_hub_html(host_base=host_base))
        if path.startswith("/install/") and path not in ("/install/",):
            from pocket.install_hub import serve_install_asset

            return serve_install_asset(self, path)
        if path in (
            "/v1/economy/parallax/wallets",
            "/v1/economy/ai-wallets",
            "/v1/parallax/ai-wallets",
        ):
            from pocket.economy import export_parallax_ai_wallets

            return self._json(200, export_parallax_ai_wallets())
        if path in ("/v1/economy/parallax/sync", "/v1/parallax/sync"):
            from pocket.economy import sync_parallax_bridge

            return self._json(200, sync_parallax_bridge(write_export=True))
        if path.startswith("/v1/protocols/") and path not in (
            "/v1/protocols/capsule",
            "/v1/protocols/mesh",
            "/v1/protocols/status",
            "/v1/protocols/catalog",
            "/v1/protocols/wasm-capsule",
        ):
            from pocket.protocols.platform_protocols import get_protocol, _health_one

            slug = path.split("/v1/protocols/", 1)[-1].strip("/")
            if slug and slug not in ("capsule", "mesh", "status", "catalog", "wasm-capsule"):
                p = get_protocol(slug)
                if not p:
                    return self._json(404, {"ok": False, "error": "unknown protocol", "slug": slug})
                return self._json(200, {"ok": True, "protocol": p, "health": _health_one(p)})
        if path in ("/auth/client.js", "/v1/auth/client.js"):
            from pocket.auth_client import auth_client_js

            raw = auth_client_js().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=120")
            self.send_header("Content-Length", str(len(raw)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(raw)
            return
        if path in ("/v1/sandbox/profiles",):
            from pocket.agent_sandbox import list_profiles

            return self._json(200, list_profiles())
        if path in ("/v1/vmem", "/v1/pixel-memory", "/v1/pixel_vmem"):
            from pocket.pixel_vmem import status as vmem_status

            return self._json(200, vmem_status())
        if path in ("/v1/vmem/symbols",):
            from pocket.pixel_vmem import list_symbols

            q = parse_qs(urlparse(self.path).query)
            ws = (q.get("workspace") or [""])[0]
            return self._json(200, list_symbols(workspace=ws))
        if path in ("/v1/vmem/recent",):
            from pocket.pixel_vmem import list_recent

            return self._json(200, list_recent())
        if path in ("/v1/vmem/artifacts", "/v1/pixel-memory/artifacts"):
            from pocket.pixel_vmem import list_artifacts

            q = parse_qs(urlparse(self.path).query)
            return self._json(
                200,
                list_artifacts(
                    limit=int((q.get("limit") or ["40"])[0] or 40),
                    agent=(q.get("agent") or [""])[0],
                    run_id=(q.get("run") or q.get("run_id") or [""])[0],
                ),
            )
        if path in ("/v1/swarm", "/v1/coding-swarm", "/v1/swarm/roster"):
            from pocket.coding_swarm import list_roster

            return self._json(200, list_roster())
        if path in ("/v1/workflows", "/v1/kernels/workflows"):
            from pocket.kernels.long_workflow import list_runs

            q = parse_qs(urlparse(self.path).query)
            return self._json(200, list_runs(limit=int((q.get("limit") or ["40"])[0] or 40)))
        if path.startswith("/v1/workflows/") and path.count("/") == 3:
            from pocket.kernels.long_workflow import get as wf_get

            return self._json(200, wf_get(path.rsplit("/", 1)[-1]))
        if path in ("/v1/kernels", "/v1/neuro-silicon", "/v1/kernels/status"):
            from pocket.kernels.neuro_silicon import driver_status

            return self._json(200, driver_status())
        if path in ("/v1/kernels/probe",):
            from pocket.kernels.probe import probe_host

            return self._json(200, probe_host())
        if path in ("/v1/kernels/slab",):
            from pocket.kernels.slab import slab_status

            return self._json(200, slab_status())
        if path in ("/v1/kernels/calibrate", "/v1/neuro-silicon/calibrate"):
            from pocket.kernels.neuro_silicon import calibrate

            return self._json(200, calibrate(run_loop=True))
        if path in ("/v1/kernels/loop", "/v1/cognitive/loop"):
            from pocket.kernels.cognitive_loop import run_loop

            q = parse_qs(urlparse(self.path).query)
            goal = (q.get("goal") or q.get("q") or ["status"])[0]
            return self._json(200, run_loop(goal))
        if path in ("/v1/agents/arch", "/v1/agent/arch", "/v1/architecture/agents"):
            from pocket.agent_arch import snapshot as arch_snap

            return self._json(200, arch_snap())
        if path in ("/v1/agents/roster", "/v1/agents/invocable"):
            from pocket.agent_invoke import roster

            return self._json(200, roster())
        if path in ("/v1/agents/autonomous", "/v1/autonomous"):
            from pocket.agent_invoke import autonomous_status

            return self._json(200, autonomous_status())
        if path in ("/v1/agents/first-class", "/v1/first-class/agents", "/v1/agents"):
            from pocket.first_class_agents import build_registry, ensure_modes_aligned, summary

            ensure_modes_aligned()
            q = parse_qs(urlparse(self.path).query)
            live = (q.get("live") or ["0"])[0] in ("1", "true", "yes")
            if path.endswith("/summary") or (q.get("summary") or [""])[0]:
                return self._json(200, summary())
            return self._json(200, build_registry(live=live))
        if path in ("/agents", "/agents/", "/phoneai/agents"):
            from pocket.agent_social_ui import agents_html

            return self._html(agents_html())
        if path in ("/v1/agents/social", "/v1/agent-social"):
            from pocket.agent_social import status as social_status

            return self._json(200, social_status())
        if path in ("/v1/agents/people", "/v1/agents/faces"):
            from pocket.agent_social import list_people

            return self._json(200, list_people())
        if path.startswith("/v1/agents/face/") and path.endswith(".svg"):
            from pocket.agent_social import face_svg, _safe as social_safe

            aid = path.rsplit("/", 1)[-1][:-4]
            data = face_svg(social_safe(aid), name=aid).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return None
        if path in ("/v1/agents/groups",):
            from pocket.agent_social import list_groups, group_messages

            q = parse_qs(urlparse(self.path).query)
            if (q.get("id") or [""])[0]:
                return self._json(200, group_messages((q.get("id") or [""])[0]))
            return self._json(200, list_groups())
        if path in ("/v1/agents/groups/messages",):
            from pocket.agent_social import group_messages

            q = parse_qs(urlparse(self.path).query)
            return self._json(200, group_messages((q.get("id") or q.get("group") or [""])[0]))
        if path in ("/v1/agents/dm",):
            from pocket.agent_social import thread as dm_thread

            q = parse_qs(urlparse(self.path).query)
            return self._json(200, dm_thread((q.get("a") or ["system"])[0], (q.get("b") or [""])[0]))
        if path in ("/v1/cron/memory", "/v1/autonomy/memory", "/v1/agents/cron"):
            from pocket.autonomy import last_week, yesterday

            q = parse_qs(urlparse(self.path).query)
            sid = (q.get("id") or q.get("schedule") or [""])[0]
            days = (q.get("days") or ["1"])[0]
            if days in ("7", "week"):
                return self._json(200, last_week(sid))
            return self._json(200, yesterday(sid))
        if path in ("/v1/subagents/live", "/v1/agents/steer"):
            from pocket.subagent_dispatch import live_runs

            return self._json(200, live_runs())
        if path in ("/v1/agents/catalog", "/v1/desk/catalog"):
            from pocket.first_class_agents import desk_catalog, ensure_modes_aligned

            ensure_modes_aligned()
            return self._json(200, desk_catalog())
        if path in ("/v1/os", "/v1/agent-os", "/v1/os/dashboard"):
            from pocket.agent_os import dashboard
            from pocket.first_class_agents import ensure_modes_aligned, summary as agent_summary

            ensure_modes_aligned()
            d = dashboard()
            d["first_class_agents"] = agent_summary()
            return self._json(200, d)
        if path in ("/v1/os/systems", "/v1/systems"):
            from pocket.agent_os import list_systems

            return self._json(200, list_systems(live=True))
        if path in ("/v1/os/parity", "/v1/parity"):
            from pocket.agent_os import parity_report

            return self._json(200, parity_report())
        if path in ("/v1/os/projects",):
            from pocket.agent_os import list_projects

            return self._json(200, list_projects())
        if path in ("/v1/os/timeline",):
            from pocket.agent_os import timeline

            return self._json(200, timeline())
        if path in ("/v1/vmem/look", "/v1/vmem/search"):
            from pocket.pixel_vmem import look, search

            q = parse_qs(urlparse(self.path).query)
            if path.endswith("/search") or (q.get("q") or [""])[0]:
                return self._json(200, search((q.get("q") or q.get("query") or [""])[0]))
            return self._json(
                200,
                look(
                    symbol=(q.get("symbol") or [""])[0],
                    page_id=(q.get("page") or q.get("page_id") or [""])[0],
                    q=(q.get("q") or [""])[0],
                ),
            )
        if path in ("/v1/vmem/context",):
            from pocket.pixel_vmem import context_block

            q = parse_qs(urlparse(self.path).query)
            ws = (q.get("workspace") or ["default"])[0]
            return self._json(200, {"ok": True, "workspace": ws, "block": context_block(ws)})
        if path.startswith("/v1/vmem/page/"):
            from pocket.pixel_vmem import get_page

            pid = path.split("/v1/vmem/page/", 1)[-1].split("/")[0]
            return self._json(200, get_page(pid))
        if path.startswith("/v1/vmem/symbol/"):
            from pocket.pixel_vmem import get_symbol

            sym = path.split("/v1/vmem/symbol/", 1)[-1]
            from urllib.parse import unquote

            return self._json(200, get_symbol(unquote(sym)))
        if path in ("/v1/vmem/map", "/v1/vmem/png"):
            from pocket.pixel_vmem import map_png

            q = parse_qs(urlparse(self.path).query)
            pid = (q.get("page") or q.get("page_id") or [""])[0]
            sym = (q.get("symbol") or [""])[0]
            try:
                side = int((q.get("size") or ["256"])[0])
            except Exception:
                side = 256
            r = map_png(page_id=pid, symbol=sym, max_side=max(32, min(side, 1024)))
            return self._json(200, r)
        if path in ("/v1/protocols/mesh", "/v1/protocol/mesh", "/v1/hooks/mesh"):
            from pocket.agent_hook import protocol_report

            return self._json(200, protocol_report())
        if path.startswith("/v1/mesh/inbox/"):
            from pocket.mesh_disk import read_inbox

            aid = path.split("/v1/mesh/inbox/", 1)[-1].split("/")[0]
            return self._json(200, read_inbox(aid))
        if path == "/v1/mesh/channel":
            from pocket.mesh_disk import channel_tail

            q = parse_qs(urlparse(self.path).query)
            ch = (q.get("name") or ["freq-0"])[0]
            return self._json(200, channel_tail(ch))
        if path == "/v1/bridge":
            from pocket.realtime_bridge import list_bridges

            return self._json(200, {"bridges": list_bridges()})
        if path.startswith("/v1/bridge/"):
            from pocket.realtime_bridge import get_bridge

            bid = path.split("/v1/bridge/", 1)[-1].split("/")[0]
            br = get_bridge(bid)
            if not br:
                return self._json(404, {"error": "bridge not found"})
            return self._json(
                200,
                {
                    "id": br.get("id"),
                    "status": br.get("status"),
                    "steps": br.get("steps"),
                    "recording_path": br.get("recording_path"),
                    "last_observe_summary": br.get("last_observe_summary"),
                },
            )
        if path == "/v1/long_workers":
            # Alias import — never shadow module-level status() in this method
            from pocket.long_workers import status as long_workers_status

            return self._json(200, long_workers_status())
        if path == "/v1/purchase/playbooks":
            from pocket.purchase_playbooks import list_playbooks

            return self._json(200, {"playbooks": list_playbooks(), "auto_pay": False})
        if path == "/v1/campaigns":
            from pocket.campaigns import list_campaigns

            return self._json(200, {"campaigns": list_campaigns()})
        if path in ("/v1/imagine", "/v1/imagine/status"):
            from pocket.imagine_studio import status as imagine_status

            return self._json(200, imagine_status())
        if path in ("/v1/imagine/gallery", "/v1/imagine/composites"):
            from pocket.imagine_studio import gallery as imagine_gallery

            q = parse_qs(urlparse(self.path).query)
            try:
                lim = int((q.get("limit") or ["24"])[0] or 24)
            except Exception:
                lim = 24
            return self._json(200, imagine_gallery(limit=lim))
        if path in ("/v1/imagine/modes",):
            from pocket.imagine_studio import list_modes

            return self._json(200, list_modes())
        if path == "/v1/imagine/file":
            from pocket.imagine_studio import resolve_file

            q = parse_qs(urlparse(self.path).query)
            name = (q.get("name") or [""])[0]
            kind = (q.get("kind") or [""])[0]
            fp = resolve_file(name, kind=kind)
            if not fp:
                return self._json(404, {"error": "file not found", "name": name})
            data = fp.read_bytes()
            suf = fp.suffix.lower()
            ctype = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".html": "text/html; charset=utf-8",
                ".json": "application/json; charset=utf-8",
            }.get(suf, "application/octet-stream")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", f'inline; filename="{fp.name}"')
            self.send_header("Cache-Control", "private, max-age=60")
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/v1/rfe", "/v1/rfe/status"):
            from pocket.rfe_kernel import status as rfe_status

            return self._json(200, rfe_status())
        if path in (
            "/v1/fusion/voice",
            "/v1/fusion/voice/schema",
            "/v1/fusion/conversational",
            "/v1/conversational-fusion",
        ):
            from pocket.conversational_fusion import schema as cf_schema

            return self._json(200, cf_schema())
        if path in ("/v1/fusion/voice/last", "/v1/conversational-fusion/last"):
            from pocket.conversational_fusion import last as cf_last

            qs = parse_qs(urlparse(self.path).query)
            sid = (qs.get("session_id") or qs.get("sid") or [""])[0]
            row = cf_last(sid)
            return self._json(200, {"ok": True, "session_id": sid, "fusion": row})
        if path in ("/v1/product/presentation", "/v1/presentation", "/v1/tour"):
            from pocket.product_tour import presentation

            return self._json(200, presentation())
        if path in ("/v1/product/channels", "/v1/channels"):
            from pocket.product_channels import channels

            return self._json(200, channels())
        if path in ("/v1/product/home", "/v1/home"):
            from pocket.product_channels import user_home_brief

            return self._json(200, user_home_brief())
        if path in ("/v1/sense/intent", "/v1/fusion/intent"):
            from pocket.sanity import intent_buffer

            return self._json(200, intent_buffer())
        if path in ("/v1/nexus", "/v1/nexus/status"):
            from pocket.nexus_bridge import nexus_available, list_capabilities

            info = nexus_available()
            caps = list_capabilities() if info.get("ok") else info
            return self._json(200, {"ok": True, "nexus": info, "capabilities": caps})
        if path in ("/v1/mesie", "/v1/mesie/status"):
            from pocket.mesie_bridge import status as mesie_status

            return self._json(200, mesie_status())
        if path in ("/v1/auro", "/v1/auro14b", "/v1/ro14b"):
            from pocket.auro14b_bridge import status as auro_status

            return self._json(200, auro_status())
        if path in ("/v1/stack", "/v1/lab/stack"):
            # Unified POCKET + NEXUS + MESIE + mesh status for left rail
            from pocket.nexus_bridge import nexus_available
            from pocket.mesie_bridge import mesie_available
            from pocket.mesh_disk import status as mesh_status
            from pocket.agent_hook import hook_status

            return self._json(
                200,
                {
                    "ok": True,
                    "pocket": {"product": "POCKET", "version": "2.0.1-alpha"},
                    "nexus": nexus_available(),
                    "mesie": mesie_available(),
                    "mesh": mesh_status(),
                    "hook": hook_status(),
                    "swarm": {
                        "novasbrain": r"E:\NOVASBRAIN",
                        "studio": r"E:\NOVASBRAIN\swarm_studio",
                        "phase": 31,
                        "note": "Stratum + gas ledger verified in NOVASBRAIN; not auto-mined from desk",
                    },
                },
            )
        if path in ("/v1/vcomp", "/v1/virtual-computer", "/v1/computer"):
            from pocket.virtual_computer import status as vcomp_status

            return self._json(200, vcomp_status())
        if path in ("/v1/screen", "/v1/screen-share", "/v1/share"):
            from pocket.screen_share import status as screen_status

            return self._json(200, screen_status())
        if path in ("/v1/screen/kernel", "/v1/kernel/screen", "/v1/vlaptop"):
            from pocket.screen_kernel import snapshot as sk_snap

            return self._json(200, sk_snap())
        if path in ("/v1/mcp", "/v1/mcp/catalog", "/v1/tools/mcp"):
            from pocket.mcp_bundle import catalog

            return self._json(200, catalog())
        if path in ("/v1/mcp/tools",):
            from pocket.mcp_bundle import list_tools

            return self._json(200, list_tools())
        if path in ("/v1/mcp/fifty", "/v1/mcp/universal", "/v1/tools/fifty"):
            from pocket.mcp_fifty import catalog as fifty_catalog

            return self._json(200, fifty_catalog())
        # Live MCP JSON-RPC Protocol Stream
        if path in ("/v1/mcp/stream", "/v1/mcp/rpc/stream", "/v1/protocol/stream"):
            from pocket.mcp_stream import list_frames, snapshot

            after = int((q.get("after") or q.get("seq") or ["0"])[0] or 0)
            limit = int((q.get("limit") or ["100"])[0] or 100)
            fmt = (q.get("format") or q.get("fmt") or [""])[0].lower()
            if fmt in ("ndjson", "nd"):
                from pocket.mcp_stream import format_ndjson

                return self._text(200, format_ndjson(after_seq=after, limit=limit), ctype="application/x-ndjson; charset=utf-8")
            if fmt in ("term", "markdown", "md"):
                from pocket.mcp_stream import format_term_view

                return self._text(200, format_term_view(after_seq=after, limit=limit), ctype="text/markdown; charset=utf-8")
            snap = snapshot()
            return self._json(
                200,
                {
                    **snap,
                    "after": after,
                    "frames": list_frames(after_seq=after, limit=limit),
                },
            )
        if path in ("/v1/mcp/stream/page", "/mcp/stream", "/mcp/stream/", "/protocol/stream"):
            from pocket.mcp_stream import stream_page_html

            return self._html(stream_page_html())
        if path in ("/v1/work", "/v1/work-mode", "/v1/working"):
            from pocket.work_mode import status as work_status

            out = work_status()
            try:
                from pocket.working_board import status as board_status

                out["board"] = board_status()
            except Exception:
                pass
            return self._json(200, out)
        if path in ("/v1/working/board", "/v1/work/board", "/v1/board"):
            from pocket.working_board import status as board_status

            return self._json(200, board_status())
        if path in ("/v1/integrations", "/v1/integrations/catalog", "/v1/connectors"):
            from pocket.integrations_catalog import catalog as integrations_catalog

            return self._json(200, integrations_catalog())
        if path in (
            "/v1/integrations/readiness",
            "/v1/connectors/readiness",
            "/v1/integrations/status",
        ):
            from pocket.integrations_exec import readiness as integrations_readiness

            return self._json(200, integrations_readiness())
        if path.startswith("/v1/integrations/"):
            from pocket.integrations_catalog import get as integration_get

            iid = path.rstrip("/").split("/")[-1]
            if iid in ("readiness", "status", "catalog", "execute", "execute_all"):
                pass  # handled above / via POST
            return self._json(200, integration_get(iid))
        # Pocket Voice same-origin proxy (mic / Aria never blocked by CORS or dead :8790)
        if path in (
            "/v1/pocket-voice/health",
            "/v1/voice/health",
            "/v1/pocket-voice/health/",
        ):
            from pocket.voice_proxy import health as voice_health, ensure_voice

            h = voice_health()
            if not h.get("ok"):
                ensure_voice(wait_sec=2.5)
                h = voice_health()
            return self._json(200 if h.get("ok") else 503, h)
        if path in ("/v1/voice/product", "/v1/voice/status", "/v1/aria/status"):
            from pocket.voice_product import product_status
            from pocket.voice_proxy import ensure_voice

            ensure_voice(wait_sec=1.2)
            return self._json(200, product_status())
        if path in ("/v1/voice/gemini", "/v1/gemini/status"):
            from pocket.gemini_voice import status as gemini_status

            return self._json(200, gemini_status())
        if path.startswith("/v1/voice/tts/file"):
            from pocket.tts_engine import TTS_DIR
            from pathlib import Path as _P

            # use module-level parse_qs/urlparse — do not re-import parse_qs here
            # (re-import would make parse_qs local to entire _do_GET_inner and break line 605)
            qq = parse_qs(urlparse(self.path).query)
            name = _P((qq.get("name") or [""])[0]).name
            fp = TTS_DIR / name
            if not name or not fp.is_file() or not str(fp.resolve()).startswith(str(TTS_DIR.resolve())):
                return self._json(404, {"error": "tts file not found"})
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "private, max-age=3600")
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path.startswith("/v1/pocket-voice/") and path not in (
            "/v1/pocket-voice/ensure",
            "/v1/pocket-voice/health",
        ):
            # GET proxy for any subpath e.g. /v1/pocket-voice/v1/...
            from pocket.voice_proxy import proxy_request

            sub = path[len("/v1/pocket-voice") :] or "/health"
            code, obj = proxy_request("GET", sub)
            return self._json(code, obj)
        if path in ("/v1/cli", "/v1/cli/inventory"):
            from pocket.cli_tools import inventory

            return self._json(200, inventory())
        if path in ("/v1/habitat", "/v1/agents/habitat", "/v1/hybrid"):
            from pocket.agent_habitat import status as habitat_status

            return self._json(200, habitat_status())
        if path in ("/v1/screen/frame", "/v1/share/frame"):
            from pocket.screen_share import grab_frame, status as screen_status

            st = screen_status()
            if not st.get("can_view"):
                return self._json(200, {"ok": False, "shared": False, "message": "enable View or Control in Screen column"})
            fr = grab_frame(include_image=True)
            # strip huge base64 from default if ?meta=1
            q = parse_qs(urlparse(self.path).query)
            if (q.get("meta") or ["0"])[0] in ("1", "true"):
                fr = {k: v for k, v in fr.items() if k not in ("base64", "markdown")}
            return self._json(200, {**fr, "share": st})
        if path in ("/v1/screen/context", "/v1/share/context"):
            from pocket.screen_share import fusion_context

            q = parse_qs(urlparse(self.path).query)
            agent = (q.get("agent") or ["desk"])[0]
            return self._json(200, fusion_context(agent=agent))
        if path in ("/v1/missions", "/v1/mission"):
            from pocket.mission_loop import list_missions

            return self._json(200, {"missions": list_missions()})
        if path.startswith("/v1/missions/"):
            from pocket.mission_loop import get_mission

            mid = path.split("/v1/missions/", 1)[-1].split("/")[0]
            m = get_mission(mid)
            if not m:
                return self._json(404, {"error": "mission not found"})
            return self._json(200, m)
        if path in ("/v1/workflows", "/v1/workflows/catalog"):
            from pocket.workflows_alpha import catalog
            from pocket.multi_workflows import catalog as multi_catalog

            return self._json(200, {"workflows": catalog(), "alpha": True, "multi": multi_catalog()})
        if path in ("/v1/go", "/v1/go/state"):
            from pocket.go_plane import snapshot

            return self._json(200, snapshot())
        if path in ("/v1/power", "/v1/power/pulse"):
            from pocket.power import pulse

            return self._json(200, pulse())
        if path in ("/v1/power/vs", "/v1/power/theirs"):
            from pocket.power import vs_theirs

            return self._json(200, vs_theirs())
        if path in ("/v1/power/recall",):
            from pocket.power import recall

            lim = int((q.get("limit") or ["8"])[0] or 8)
            return self._json(200, recall(limit=lim))
        if path in ("/v1/workflows/multi", "/v1/multi-workflows"):
            from pocket.multi_workflows import catalog as multi_catalog

            fam = (q.get("family") or [""])[0]
            return self._json(200, multi_catalog(family=fam))
        # LOOMGRAPH — Loop-Orchestrated Multi-agent Graph (default harness forever)
        if path in ("/v1/loomgraph", "/v1/loomgraph/catalog", "/v1/graph", "/v1/harness/loomgraph"):
            from pocket.loomgraph import catalog as loomgraph_catalog

            return self._json(200, loomgraph_catalog())
        if path in ("/v1/loomgraph/live",):
            from pocket.loomgraph import live as loomgraph_live

            return self._json(200, loomgraph_live())
        if path in ("/v1/loomgraph/runs",):
            from pocket.loomgraph import list_runs as loomgraph_runs

            return self._json(200, loomgraph_runs(limit=30))
        if path in ("/v1/loomgraph/self_test", "/v1/loomgraph/audit"):
            from pocket.loomgraph import self_test as loomgraph_self_test

            return self._json(200, loomgraph_self_test())
        if path.startswith("/v1/loomgraph/mermaid/"):
            from pocket.loomgraph import get_graph, to_mermaid

            gid = path.rstrip("/").split("/")[-1]
            g = get_graph(gid)
            return self._json(
                200,
                {
                    "ok": True,
                    "graph_id": (g.get("graph") or {}).get("id"),
                    "mermaid": to_mermaid(g),
                    "system": "LOOMGRAPH",
                },
            )
        if path.startswith("/v1/loomgraph/graph/"):
            from pocket.loomgraph import get_graph

            gid = path.rstrip("/").split("/")[-1]
            return self._json(200, get_graph(gid))

        # Creative Studio + Community Share (friendly chat + intentional feed)
        # POCKET KEEP · ISOLATE · RECALL · MAIL (self-hosted agents until chat ends)
        if path in ("/v1/keep", "/v1/keep/status"):
            from pocket.keep_agents import status as keep_status

            return self._json(200, keep_status())
        if path in ("/v1/keep/list",):
            from pocket.keep_agents import list_agents as keep_list

            return self._json(200, keep_list())
        if path.startswith("/v1/keep/") and path.count("/") >= 3:
            from pocket.keep_agents import get_agent as keep_get

            kid = path.rstrip("/").split("/")[-1]
            if kid not in ("list", "status", "start", "stop", "tick", "end"):
                return self._json(200, keep_get(kid))
        if path in ("/v1/isolate", "/v1/isolate/status", "/v1/docker-browser"):
            from pocket.docker_browser import status as isolate_status

            return self._json(200, isolate_status())
        if path in ("/v1/isolate/list",):
            from pocket.docker_browser import list_browsers

            return self._json(200, list_browsers())
        if path in ("/v1/recall", "/v1/recall/status"):
            from pocket.recall_codes import status as recall_status

            return self._json(200, recall_status())
        if path in ("/v1/recall/list",):
            from pocket.recall_codes import list_codes

            return self._json(200, list_codes(limit=50))
        if path in ("/v1/mail", "/v1/mail/status", "/v1/pocket-mail"):
            from pocket.pocket_mail import status as mail_status
            from pocket.agent_mail import status as agent_mail_status

            ms = mail_status()
            am = agent_mail_status()
            ms["agent_mail"] = {
                "ok": am.get("ok"),
                "domain": am.get("domain"),
                "accounts": am.get("accounts"),
                "total_unread": am.get("total_unread"),
                "sample": am.get("sample"),
            }
            return self._json(200, ms)
        if path in ("/v1/agent-mail", "/v1/agent-mail/status"):
            from pocket.agent_mail import status as agent_mail_status

            return self._json(200, agent_mail_status())
        if path in ("/v1/agent-mail/accounts",):
            from pocket.agent_mail import list_accounts

            return self._json(200, list_accounts())
        if path in ("/v1/agent-mail/inbox",):
            from pocket.agent_mail import inbox as agent_inbox

            agent = (q.get("agent") or q.get("id") or ["assist"])[0]
            unread = (q.get("unread") or ["0"])[0] in ("1", "true", "yes")
            return self._json(200, agent_inbox(agent, unread_only=unread))
        if path in ("/v1/web-ui", "/v1/web-ui/status"):
            from pocket.web_ui_engine import status as web_ui_status

            return self._json(200, web_ui_status())
        if path in ("/v1/python-engines", "/v1/python-engine"):
            from pocket.web_ui_engine import list_engines

            return self._json(200, list_engines())
        if path in ("/v1/engine-uses", "/v1/engines/uses", "/v1/web-ui/uses"):
            from pocket.web_ui_engine import list_uses

            return self._json(200, list_uses())
        if path in ("/v1/models/built", "/v1/model-forge", "/v1/models/forge"):
            from pocket.model_forge import list_built, status as forge_status

            if path.endswith("/built"):
                return self._json(200, list_built())
            return self._json(200, forge_status())
        # Agent virtual numbers + calls
        if path in ("/v1/calls", "/v1/calls/status", "/v1/agent-calls"):
            from pocket.agent_calls import status as calls_status, list_calls

            if path == "/v1/calls":
                st = (q.get("status") or [""])[0]
                return self._json(200, list_calls(status=st))
            return self._json(200, calls_status())
        if path in ("/v1/calls/numbers", "/v1/agent-calls/numbers"):
            from pocket.agent_calls import list_numbers

            return self._json(200, list_numbers())
        if path.startswith("/v1/calls/") and path.count("/") >= 3:
            # GET /v1/calls/{id}
            cid = path.split("/v1/calls/", 1)[-1].strip("/")
            if cid and cid not in ("dial", "answer", "hangup", "speak", "numbers", "status"):
                from pocket.agent_calls import get_call

                return self._json(200, get_call(cid))
        if path in ("/v1/mail/templates",):
            from pocket.pocket_mail import templates as mail_templates

            return self._json(200, mail_templates())
        if path in ("/v1/mail/outbox", "/v1/mail/list"):
            from pocket.pocket_mail import list_outbox

            return self._json(200, list_outbox(limit=40))

        if path in ("/v1/creative", "/v1/creative/catalog", "/v1/studio/creative"):
            from pocket.creative_studio import catalog as creative_catalog

            return self._json(200, creative_catalog())
        if path in ("/v1/creative/status",):
            from pocket.creative_studio import status as creative_status

            return self._json(200, creative_status())
        if path in ("/v1/creative/self_test", "/v1/creative/audit", "/v1/creative/live"):
            from pocket.creative_studio import self_test as creative_self_test

            return self._json(200, creative_self_test())
        if path in ("/v1/creative/sessions",):
            from pocket.creative_studio import list_sessions as creative_sessions

            return self._json(200, creative_sessions(limit=40))
        if path.startswith("/v1/creative/session/"):
            from pocket.creative_studio import get_session as creative_get_session

            sid = path.rstrip("/").split("/")[-1]
            return self._json(200, creative_get_session(sid))
        if path in ("/v1/creative/artifacts",):
            from pocket.creative_studio import list_artifacts as creative_artifacts

            qs = parse_qs(urlparse(self.path).query)
            return self._json(
                200,
                creative_artifacts(
                    limit=int((qs.get("limit") or ["40"])[0] or 40),
                    kind=(qs.get("kind") or [""])[0],
                ),
            )
        if path in ("/v1/community", "/v1/community/feed", "/v1/shares"):
            from pocket.community_share import list_shares

            qs = parse_qs(urlparse(self.path).query)
            return self._json(
                200,
                list_shares(
                    limit=int((qs.get("limit") or ["40"])[0] or 40),
                    kind=(qs.get("kind") or [""])[0],
                    author=(qs.get("author") or [""])[0],
                    q=(qs.get("q") or [""])[0],
                ),
            )
        if path in ("/v1/community/status",):
            from pocket.community_share import status as community_status

            return self._json(200, community_status())
        if path.startswith("/v1/community/") and path.count("/") >= 3:
            from pocket.community_share import get_share

            sid = path.rstrip("/").split("/")[-1]
            if sid not in ("feed", "share", "status", "unshare"):
                return self._json(200, get_share(sid))

        if path == "/v1/studio":
            from pocket.video_studio import studio_status, list_recordings, list_exports, list_presets

            st = studio_status()
            st["recordings_list"] = list_recordings(30)
            st["exports_list"] = list_exports(30)
            st["presets"] = list_presets()
            try:
                from pocket.studio_core import first_class_status, studio_map

                st["first_class"] = True
                st["agent"] = first_class_status()
                st["map"] = {
                    "skills": studio_map().get("skills"),
                    "playbooks": studio_map().get("playbooks"),
                    "say_examples": studio_map().get("say_examples"),
                }
            except Exception:
                st["first_class"] = False
            return self._json(200, st)
        if path in ("/v1/studio/first-class", "/v1/studio/map", "/v1/studio/agent/catalog"):
            from pocket.studio_core import studio_map, first_class_status

            m = studio_map()
            st = first_class_status()
            m["status"] = st
            # Promote first-class flags so agents/desk see Creative + Community at top level
            m["creative_first_class"] = bool(st.get("creative_first_class"))
            m["community_first_class"] = bool(st.get("community_first_class"))
            m["ready"] = bool(st.get("ready"))
            m["urls"] = st.get("urls") or m.get("urls")
            m["message"] = st.get("message") or m.get("message")
            return self._json(200, m)
        if path in ("/v1/studio/playbooks",):
            from pocket.studio_core import PLAYBOOKS, AGENT_FEATURES

            return self._json(200, {"ok": True, "playbooks": PLAYBOOKS, "features": AGENT_FEATURES})
        if path == "/v1/studio/recordings":
            from pocket.video_studio import list_recordings

            return self._json(200, {"recordings": list_recordings()})
        if path == "/v1/studio/exports":
            from pocket.video_studio import list_exports

            return self._json(200, {"exports": list_exports()})
        if path == "/v1/studio/presets":
            from pocket.video_studio import list_presets

            return self._json(200, {"presets": list_presets()})
        if path == "/v1/studio/file":
            from pocket.video_studio import EXPORTS

            q = parse_qs(urlparse(self.path).query)
            name = (q.get("name") or [""])[0]
            # only basename under exports
            safe = Path(name).name
            fp = EXPORTS / safe
            if not fp.is_file() or not str(fp.resolve()).startswith(str(EXPORTS.resolve())):
                return self._json(404, {"error": "file not found"})
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", f'inline; filename="{safe}"')
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path.startswith("/v1/campaigns/"):
            from pocket.campaigns import get_campaign

            cid = path.split("/v1/campaigns/", 1)[-1].split("/")[0]
            c = get_campaign(cid)
            if not c:
                return self._json(404, {"error": "campaign not found"})
            return self._json(200, c)
        if path == "/v1/platform/capabilities":
            from pocket.skill_suite import skill_count
            from pocket import __version__ as _pv

            return self._json(
                200,
                {
                    "version": _pv,
                    "skill_count": skill_count(),
                    "entrypoints": {
                        "chat": "POST /v1/orchestrator/chat",
                        "skill": "POST /v1/skills/run",
                        "spawn_worker": "POST /v1/workers/spawn",
                        "campaign": "POST /v1/campaigns/run",
                        "observe": "GET /v1/vision/observe",
                        "vision": "GET /v1/live/vision",
                        "plan": "POST /v1/orchestrator/plan",
                        "bridge_open": "POST /v1/bridge/open",
                        "bridge_observe": "POST /v1/bridge/{id}/observe",
                        "bridge_act": "POST /v1/bridge/{id}/act",
                        "bridge_close": "POST /v1/bridge/{id}/close",
                        "pixel_understand": "GET /v1/vision/understand",
                        "pixel_text": "GET /v1/pixel/text",
                        "studio": "GET /studio  ·  POST /v1/studio/auto",
                    },
                    "value_vs_chat_only": [
                        "Real desktop control with signed-in browser",
                        "Vision + UI map click-by-name",
                        "Pixel translator: semantic + OCR + pure visual fusion",
                        "Dynamic workers with memory brains",
                        "Screen record commercial demos",
                        "Multi-repo research campaigns",
                        "Same API for local host and remote VM",
                    ],
                    "clients": ["pocket-ui", "codex", "grok-build", "phone", "sk_pocket_ api keys"],
                },
            )
        if path == "/v1/host":
            from pocket.host_backend import get_host

            h = get_host()
            return self._json(200, {"backend": h.kind(), "note": "Local now; set ~/.pocket/host.json for remote VM"})
        if path == "/v1/cli/tools":
            from pocket.cli_tools import inventory

            return self._json(200, inventory())
        if path in ("/v1/workers", "/v1/alpha"):
            from pocket.alpha_workers import list_workers
            from pocket.skill_suite import all_skills, skill_count
            from pocket.worker_daemon import live_state, ensure_daemon
            from pocket.orchestrator import get_orchestrator

            ensure_daemon()
            return self._json(
                200,
                {
                    "workers": list_workers(),
                    "skills": all_skills(),
                    "skill_count": skill_count(),
                    "live": live_state(),
                    "orchestrator": get_orchestrator().catalog()["architecture"],
                    "guppy": "kept",
                },
            )
        if path in ("/v1/skills", "/v1/skill_suite"):
            from pocket.skill_suite import all_skills, skill_count

            plat = []
            try:
                from pocket.platform_coherence import platform_skills

                plat = platform_skills()
            except Exception:
                pass
            return self._json(
                200,
                {
                    "ok": True,
                    "count": skill_count(),
                    "skills": all_skills(),
                    "platform_skills": plat,
                    "platform_skill_count": len(plat),
                    "discover": "/v1/platform/coherent",
                    "run": "POST /v1/skills/run {skill, prompt, params}",
                },
            )
        if path in ("/v1/skills/platform", "/v1/platform/skills"):
            from pocket.platform_coherence import platform_skills, coherent

            return self._json(
                200,
                {
                    "ok": True,
                    "count": len(platform_skills()),
                    "skills": platform_skills(),
                    "map": coherent().get("find"),
                    "flow": coherent().get("flow"),
                },
            )
        if path in ("/v1/platform/coherent", "/v1/coherent", "/v1/platform/map"):
            from pocket.platform_coherence import coherent

            return self._json(200, coherent())
        if path in (
            "/v1/sovereign",
            "/v1/sovereign/stack",
            "/v1/platform/sovereign",
            "/v1/computing-clouds",
            "/v1/clouds",
        ):
            from pocket.sovereign_stack import stack_status, computing_clouds, doctrine

            if path in ("/v1/computing-clouds", "/v1/clouds"):
                return self._json(200, computing_clouds())
            if "doctrine" in (urlparse(self.path).query or ""):
                return self._json(200, doctrine())
            return self._json(200, stack_status())
        if path in ("/v1/remote-browser", "/v1/browser/remote", "/v1/remote_browser"):
            from pocket.remote_browser import status as rb_status, parity_matrix, run_benchmarks

            q = parse_qs(urlparse(self.path).query)
            if (q.get("benchmark") or [""])[0] in ("1", "true", "yes"):
                return self._json(200, run_benchmarks())
            if (q.get("parity") or [""])[0] in ("1", "true", "yes"):
                return self._json(200, parity_matrix())
            return self._json(200, rb_status())
        if path in ("/v1/remote-browser/benchmark", "/v1/browser/benchmark"):
            from pocket.remote_browser import run_benchmarks

            return self._json(200, run_benchmarks())
        if path in ("/v1/iot", "/v1/iot/home", "/v1/home/iot"):
            from pocket.iot_home import status as iot_status

            return self._json(200, iot_status())
        if path in ("/v1/iot/discover", "/v1/home/discover", "/v1/iot/scan"):
            from pocket.iot_home import discover_lan

            qs = {k: (v[0] if v else "") for k, v in parse_qs(urlparse(self.path).query).items()}
            deep = str(qs.get("deep") or "").lower() in ("1", "true", "yes")
            return self._json(200, discover_lan(deep=deep, register=True))
        if path in ("/v1/voice/stt/engines", "/v1/stt/engines"):
            from pocket.stt_engine import engines as stt_engines

            return self._json(200, stt_engines())
        if path in ("/v1/iot/devices", "/v1/home/devices"):
            from pocket.iot_home import list_devices

            return self._json(200, list_devices())
        if path in ("/v1/phone/ready", "/v1/phone/status"):
            from pocket.phone_ui import phone_ready

            return self._json(200, phone_ready())
        if path in ("/v1/lab", "/v1/lab/status", "/v1/lab/ready"):
            from pocket.lab_hub import lab_status

            return self._json(200, lab_status())
        if path in ("/v1/iot/phone", "/v1/phone/bridge"):
            from pocket.iot_home import phone_bridge

            return self._json(200, phone_bridge())
        if path == "/v1/orchestrator":
            from pocket.orchestrator import get_orchestrator

            return self._json(200, get_orchestrator().catalog())
        if path in ("/v1/fabric", "/v1/features", "/v1/wired"):
            from pocket.feature_fabric import snapshot as fabric_snap

            return self._json(200, fabric_snap())
        if path in ("/v1/ai-workspace", "/v1/ai_workspace", "/v1/workspace/ai"):
            from pocket.ai_workspace import get_workspace_view, refresh_index

            # use module-level urlparse/parse_qs — local import shadows and crashes do_GET
            qs = {k: (v[0] if v else "") for k, v in parse_qs(urlparse(self.path).query).items()}
            p = rbac_principal(self.headers)
            if not is_founder(p):
                # Market never indexes founder Parallax / OneDrive
                from pocket.platform_space import list_space, tenant_cwd

                user = p.get("user") or "anonymous"
                return self._json(
                    200,
                    {
                        "ok": True,
                        "edition": "market",
                        "founder_files": False,
                        "cwd": tenant_cwd(user, "files"),
                        "space": list_space(user, "files"),
                    },
                )
            ws = qs.get("workspace") or "parallax"
            sid = qs.get("session_id") or qs.get("session") or ""
            if qs.get("refresh") in ("1", "true", "yes"):
                refresh_index(ws, qs.get("cwd") or "")
            return self._json(200, get_workspace_view(ws, session_id=sid))
        if path in ("/v1/ai-workspace/file", "/v1/workspace/file"):
            from pocket.ai_workspace import read_workspace_file

            qs = {k: (v[0] if v else "") for k, v in parse_qs(urlparse(self.path).query).items()}
            p = rbac_principal(self.headers)
            if not is_founder(p):
                return self._json(403, {"ok": False, "error": "workspace files are founder-host"})
            return self._json(
                200,
                read_workspace_file(qs.get("path") or "", workspace=qs.get("workspace") or "parallax"),
            )
        if path in ("/v1/capabilities", "/v1/capability-map", "/v1/caps"):
            from pocket.capability_map import build_capability_map, capability_markdown

            cmap = build_capability_map()
            return self._json(200, {"ok": True, "map": cmap, "markdown": capability_markdown(cmap)})
        if path == "/v1/offload" and self.command == "GET":
            from pocket.offload_queue import list_tasks

            qs = {k: (v[0] if v else "") for k, v in parse_qs(urlparse(self.path).query).items()}
            return self._json(
                200,
                {
                    "ok": True,
                    "tasks": list_tasks(status=qs.get("status") or "", limit=int(qs.get("limit") or 40)),
                },
            )
        if path.startswith("/v1/offload/") and self.command == "GET":
            from pocket.offload_queue import get_task

            tid = path.split("/v1/offload/", 1)[-1].strip("/")
            t = get_task(tid)
            if not t:
                return self._json(404, {"ok": False, "error": "ticket not found"})
            return self._json(200, {"ok": True, "task": t})
        if path in ("/v1/task-market", "/v1/market"):
            from pocket.task_market import list_open

            return self._json(200, {"ok": True, "open": list_open()})
        if path in ("/v1/git/repos", "/v1/forge/repos"):
            from pocket.sovereign_git import list_repos

            return self._json(200, list_repos())
        if path.startswith("/v1/git/repos/") and path.endswith("/zip"):
            from pocket.sovereign_git import export_zip

            name = path[len("/v1/git/repos/") : -len("/zip")].strip("/")
            r = export_zip(name)
            if not r.get("ok"):
                return self._json(404, r)
            try:
                data = Path(r["path"]).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{r["name"]}"')
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", self._cors_origin())
                self._sec_headers()
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)})
        if path.startswith("/v1/git/exports/"):
            name = path.split("/v1/git/exports/", 1)[-1]
            fp = Path.home() / ".pocket" / "git_exports" / name
            if not fp.is_file() or ".." in name or "/" in name or "\\" in name:
                return self._json(404, {"ok": False, "error": "export not found"})
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{fp.name}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", self._cors_origin())
            self._sec_headers()
            self.end_headers()
            self.wfile.write(data)
            return
        if path in ("/v1/record/status", "/v1/screen/status"):
            from pocket.screen_record import record_status

            return self._json(200, record_status())
        if path in ("/v1/auro", "/v1/auro/status", "/v1/auro/meaning"):
            from pocket.auro_meaning import status as auro_meaning_status
            from pocket.auro14b_bridge import status as auro_host_status

            return self._json(
                200,
                {"ok": True, "meaning": auro_meaning_status(), "host": auro_host_status()},
            )
        if path in ("/v1/agent-bus", "/v1/mesh/bus"):
            from pocket.mesh_disk import channel_tail, decrypt_body

            qs = {k: (v[0] if v else "") for k, v in parse_qs(urlparse(self.path).query).items()}
            ch = qs.get("channel") or "freq-coding"
            tail = channel_tail(ch, limit=int(qs.get("limit") or 20))
            msgs = []
            for m in tail.get("messages") or []:
                body = m.get("body") or ""
                if m.get("body_cipher"):
                    try:
                        body = decrypt_body(m["body_cipher"])
                    except Exception:
                        pass
                msgs.append(
                    {
                        "from": m.get("from"),
                        "to": m.get("to"),
                        "kind": m.get("kind"),
                        "body": (body or "")[:400],
                        "hmac": (m.get("hmac_sha256") or "")[:16],
                        "at": m.get("at"),
                    }
                )
            return self._json(200, {"ok": True, "channel": ch, "messages": msgs})
        if path == "/v1/workers/live":
            from pocket.worker_daemon import live_state, ensure_daemon

            ensure_daemon()
            return self._json(200, live_state())
        if path == "/v1/github/repos":
            from pocket.repos import list_github_repos, gh_available

            return self._json(200, {**list_github_repos(5), "auth": gh_available()})
        if path == "/v1/nexus/status":
            from pocket.nexus_bridge import nexus_available

            return self._json(200, nexus_available())
        if path.startswith("/v1/docs/"):
            key = path.split("/v1/docs/", 1)[-1]
            fname = DOC_MAP.get(key)
            if not fname:
                return self._json(404, {"error": "doc not found", "keys": list(DOC_MAP)})
            fp = DOCS_ROOT / fname
            if not fp.exists():
                return self._json(404, {"error": "file missing", "path": str(fp)})
            return self._text(200, fp.read_text(encoding="utf-8"))
        if path in ("/v1/wsl", "/v1/wsl/status", "/v1/wsl/probe"):
            from pocket.wsl_agent import status as wsl_status

            # Public-ish probe is host-sensitive — require auth
            if not self._require_auth(path):
                return
            return self._json(200, wsl_status())
        if path in ("/v1/use-cases", "/v1/usecases", "/v1/parity", "/v1/emergent"):
            from pocket.use_cases import list_use_cases, parity_report

            if path.endswith("parity") or path.endswith("emergent"):
                return self._json(200, parity_report())
            return self._json(200, {"ok": True, "use_cases": list_use_cases(), "parity": "/v1/parity"})
        if path in ("/v1/work-studio", "/v1/work/types", "/v1/work-types"):
            from pocket.work_types import catalog, list_types

            if path.endswith("types") or path.endswith("work-types"):
                return self._json(200, {"ok": True, "types": list_types()})
            return self._json(200, catalog())
        if path in ("/v1/work-studio/catalog", "/v1/assistant/catalog", "/v1/digital-assistant"):
            from pocket.digital_assistant import catalog as assist_catalog

            return self._json(200, assist_catalog())
        if path in ("/v1/work-loops",):
            from pocket.work_types import list_loops

            return self._json(200, {"ok": True, "loops": list_loops()})
        if path in ("/v1/swarm", "/v1/swarm/status"):
            from pocket.always_on_swarm import status as swarm_status

            return self._json(200, swarm_status())
        # Internal Damian fleet (operator-facing; not user product surface)
        if path in ("/v1/damians", "/v1/damian", "/v1/damian/fleet"):
            from pocket.damian_fleet import status as damian_status

            q = parse_qs(urlparse(self.path).query)
            full = (q.get("all") or ["0"])[0] in ("1", "true", "yes")
            return self._json(200, damian_status(include_all=full))
        if path in ("/v1/world-model", "/v1/world"):
            from pocket.world_model import status as wm_status

            return self._json(200, wm_status())
        if path in ("/v1/wiki", "/v1/infinite-wiki", "/v1/wiki/status"):
            from pocket.infinite_wiki import status as wiki_status

            return self._json(200, wiki_status())
        if path in ("/v1/wiki/profile", "/v1/wiki/get_file_profile"):
            from pocket.infinite_wiki import get_file_profile
            from urllib.parse import unquote

            qs = parse_qs(urlparse(self.path).query)
            pth = unquote((qs.get("path") or qs.get("p") or [""])[0])
            refresh = (qs.get("refresh") or ["0"])[0] in ("1", "true", "yes")
            return self._json(200, get_file_profile(pth, refresh=refresh))
        if path in ("/v1/wiki/lines", "/v1/wiki/read_file_lines"):
            from pocket.infinite_wiki import read_file_lines
            from urllib.parse import unquote

            qs = parse_qs(urlparse(self.path).query)
            pth = unquote((qs.get("path") or qs.get("p") or [""])[0])
            start = int((qs.get("start") or qs.get("s") or ["1"])[0])
            end = (qs.get("end") or qs.get("e") or [None])[0]
            end_i = int(end) if end not in (None, "") else None
            return self._json(200, read_file_lines(pth, start, end_i))
        if path in ("/v1/wiki/symbol", "/v1/wiki/find_symbol"):
            from pocket.infinite_wiki import find_symbol
            from urllib.parse import unquote

            qs = parse_qs(urlparse(self.path).query)
            name = unquote((qs.get("name") or qs.get("q") or [""])[0])
            root = unquote((qs.get("root") or [""])[0])
            return self._json(200, find_symbol(name, root=root))
        if path in ("/v1/wiki/search"):
            from pocket.infinite_wiki import search_profiles
            from urllib.parse import unquote

            qs = parse_qs(urlparse(self.path).query)
            q = unquote((qs.get("q") or qs.get("query") or [""])[0])
            return self._json(200, search_profiles(q))
        if path.startswith("/v1/world-model/search") or path == "/v1/world/search":
            from pocket.world_model import search as wm_search

            # use module-level urlparse/parse_qs — never local-import (shadows + crashes do_GET)
            qs = parse_qs(urlparse(self.path).query)
            q = (qs.get("q") or qs.get("query") or [""])[0]
            kind = (qs.get("kind") or ["all"])[0]
            return self._json(200, wm_search(q, kind=kind, limit=int((qs.get("limit") or ["8"])[0])))
        if path.startswith("/v1/dual/"):
            from pocket.cortex_subcortex import get_job

            jid = path.rstrip("/").split("/")[-1]
            j = get_job(jid)
            if not j:
                return self._json(404, {"ok": False, "error": "dual job not found"})
            return self._json(200, {"ok": True, **j})
        if path in ("/v1/build-loops", "/v1/loops"):
            from pocket.build_loop import list_loops

            return self._json(200, {"ok": True, "loops": list_loops()})
        if path.startswith("/v1/build-loops/") or path.startswith("/v1/loops/"):
            from pocket.build_loop import get_loop

            lid = path.rstrip("/").split("/")[-1]
            m = get_loop(lid)
            if not m:
                return self._json(404, {"ok": False, "error": "loop not found"})
            return self._json(200, {"ok": True, **m})
        if path in ("/v1/custom-agents", "/v1/agents/custom"):
            from pocket.custom_agents import list_agents, tools_catalog

            return self._json(200, {"ok": True, "agents": list_agents(), "tools": tools_catalog().get("tools")})
        if path in ("/v1/bots", "/v1/bots/"):
            from pocket.bots import catalog as bots_catalog

            p = rbac_principal(self.headers)
            data = bots_catalog()
            data["bots"] = [b for b in data.get("bots") or [] if not p.get("user") or b.get("owner") in ("", p.get("user"), "pocket")]
            return self._json(200, data)
        if path.startswith("/v1/bots/"):
            from pocket.bots import thread as bot_thread

            bid = path.split("/v1/bots/", 1)[-1].strip("/").split("/")[0]
            if bid in ("hire", "pulse", "message"):
                return self._json(404, {"ok": False, "error": "use POST"})
            return self._json(200, bot_thread(bid))
        if path in ("/v1/novae", "/v1/novae/status", "/v1/novae/list"):
            from pocket.novae import status as novae_status

            return self._json(200, novae_status())
        if path.startswith("/v1/novae/"):
            from pocket.novae import get_novae

            nid = path.split("/v1/novae/", 1)[-1].split("/")[0]
            if nid in ("activate", "deactivate", "status", "list"):
                pass  # POST only
            else:
                n = get_novae(nid)
                if not n:
                    return self._json(404, {"ok": False, "error": "novae not found"})
                return self._json(200, {"ok": True, **n})
        if path == "/v1/sessions":
            p = rbac_principal(self.headers)
            lim = int((q.get("limit") or ["40"])[0])
            return self._json(
                200,
                {
                    "sessions": list_sessions(
                        lim, owner=p.get("user") or "", admin=is_admin(p)
                    )
                },
            )
        if path.startswith("/v1/sessions/"):
            sid = path.split("/v1/sessions/", 1)[-1].split("/")[0]
            sess = get_session(sid)
            if not sess:
                return self._json(404, {"error": "session not found"})
            p = rbac_principal(self.headers)
            if not can_access_owned(p, sess.get("owner") or "pocket"):
                return self._json(403, {"ok": False, "error": "not your session"})
            if sess.get("terminal_id"):
                t = get_terminal(sess["terminal_id"])
                if t:
                    sess = {**sess, "terminal": t}
            return self._json(200, sess)
        if path == "/v1/jobs":
            p = rbac_principal(self.headers)
            jobs = list_jobs(int((q.get("limit") or ["20"])[0]))
            if not is_admin(p):
                own = (p.get("user") or "").lower()
                jobs = [j for j in jobs if (j.get("owner") or "").lower() in ("", own)]
            return self._json(200, {"jobs": jobs})
        if path.startswith("/v1/jobs/"):
            jid = path.split("/v1/jobs/", 1)[-1].split("/")[0]
            job = get(jid)
            if not job:
                return self._json(404, {"error": "job not found"})
            p = rbac_principal(self.headers)
            if job.get("owner") and not can_access_owned(p, job.get("owner") or ""):
                return self._json(403, {"ok": False, "error": "not your job"})
            return self._json(200, job)
        return self._json(404, {"error": "not found"})

    def do_DELETE(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if not self._require_auth(path):
            return
        if path.startswith("/v1/sessions/"):
            sid = path.split("/v1/sessions/", 1)[-1].split("/")[0]
            sess = get_session(sid)
            p = rbac_principal(self.headers)
            if sess and not can_access_owned(p, sess.get("owner") or "pocket"):
                return self._json(403, {"ok": False, "error": "not your session"})
            try:
                from pocket.jobs import cancel_session_jobs

                cancel_session_jobs(sid, reason="session ended")
            except Exception:
                pass
            ok = delete_session(sid)
            return self._json(200 if ok else 404, {"ok": ok, "id": sid})
        if path.startswith("/v1/deploys/"):
            p = rbac_principal(self.headers)
            ok, msg = allow_admin_action(p, "deploy")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            did = path.split("/v1/deploys/", 1)[-1]
            return self._json(200, stop_deploy(did))
        if path.startswith("/v1/terminals/"):
            p = rbac_principal(self.headers)
            ok, msg = allow_mode(p, "term")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            tid = path.split("/v1/terminals/", 1)[-1]
            return self._json(200, stop_terminal(tid))
        if path.startswith("/v1/ai/keys/"):
            from pocket.api_keys import list_keys
            from pocket.sell_api import keys_revoke

            kid = path.split("/v1/ai/keys/", 1)[-1].split("/")[0]
            p = rbac_principal(self.headers)
            if not is_admin(p):
                mine = {k.get("id") for k in list_keys(owner=p.get("user") or "")}
                if kid not in mine:
                    return self._json(403, {"ok": False, "error": "not your key"})
            return self._json(200, keys_revoke(kid))
        return self._json(404, {"error": "not found"})

    def _api_key_id(self) -> str:
        try:
            from pocket.api_keys import extract_bearer, verify_key

            raw = extract_bearer(self.headers)
            if not raw:
                return ""
            rec = verify_key(raw)
            return (rec or {}).get("id") or ""
        except Exception:
            return ""

    def do_POST(self):
        try:
            self._do_POST_inner()
        except Exception as e:
            import traceback

            print("[do_POST crash]", e, flush=True)
            traceback.print_exc()
            try:
                self._json(500, {"ok": False, "error": str(e)[:300]})
            except Exception:
                try:
                    self.close_connection = True
                except Exception:
                    pass

    def _do_POST_inner(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        if not self._require_auth(path):
            return
        body = self._body()
        ensure_embedded_worker()

        # --- Sellable AI API ---
        if path in ("/v1/ai/chat", "/v1/ai/complete", "/v1/ai/jobs") or (
            path.startswith("/v1/ai/agents/") and path.endswith("/run")
        ):
            from pocket.ratelimit import hit

            p = rbac_principal(self.headers)
            rk = self._api_key_id() or p.get("user") or self._client_ip()
            heavy = path.endswith("/run") or path == "/v1/ai/jobs"
            ok_rl, reason = hit("api", rk, kind="api_heavy" if heavy else "api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})

        if path == "/v1/ai/chat":
            from pocket.sell_api import chat_complete

            p = rbac_principal(self.headers)
            agent = body.get("agent") or body.get("model") or "planner"
            if agent == "auto":
                agent = "planner"
            ok, msg = allow_agent(p, agent)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            return self._json(
                200,
                chat_complete(
                    body.get("messages") or [],
                    agent=agent,
                    workspace=body.get("workspace") or "workspace",
                    api_key_id=self._api_key_id(),
                    sync=body.get("sync", True) is not False,
                    cwd=body.get("cwd") or "",
                    inject_wiki=body.get("inject_wiki", True) is not False,
                ),
            )
        if path == "/v1/ai/route":
            from pocket.agents import route_task

            return self._json(200, route_task(body.get("task") or body.get("text") or body.get("prompt") or ""))
        if path == "/v1/ai/jobs":
            from pocket.sell_api import run_agent_api

            p = rbac_principal(self.headers)
            aid = body.get("agent") or body.get("agent_id") or "planner"
            ok, msg = allow_agent(p, aid)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            task = body.get("task") or body.get("text") or body.get("prompt") or ""
            if not task:
                return self._json(400, {"ok": False, "error": "task required"})
            return self._json(
                200,
                run_agent_api(
                    aid,
                    task,
                    workspace=body.get("workspace") or "workspace",
                    sync=False,
                    api_key_id=self._api_key_id(),
                    extra=body.get("extra") or "",
                    cwd=body.get("cwd") or "",
                    inject_wiki=body.get("inject_wiki", True) is not False,
                ),
            )
        if path.startswith("/v1/ai/agents/") and path.endswith("/run"):
            from pocket.sell_api import run_agent_api

            p = rbac_principal(self.headers)
            aid = path.split("/v1/ai/agents/", 1)[-1].replace("/run", "").strip("/")
            ok, msg = allow_agent(p, aid)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            task = body.get("task") or body.get("text") or body.get("prompt") or ""
            if not task:
                return self._json(400, {"ok": False, "error": "task required"})
            return self._json(
                200,
                run_agent_api(
                    aid,
                    task,
                    workspace=body.get("workspace") or "workspace",
                    sync=body.get("sync", True) is not False,
                    api_key_id=self._api_key_id(),
                    extra=body.get("extra") or "",
                ),
            )
        if path == "/v1/ai/keys":
            from pocket.sell_api import create_api_key_admin

            p = rbac_principal(self.headers)
            # Members may create a key for themselves only; admin can set owner
            owner = body.get("owner") or p.get("user") or "pocket"
            if not is_admin(p):
                owner = p.get("user") or "pocket"
                # members limited to starter tier by default
                if (body.get("tier") or "pro") not in ("starter", "pro"):
                    body = {**body, "tier": "starter"}
            return self._json(200, create_api_key_admin({**body, "owner": owner}, owner=owner))
        if path == "/v1/ai/complete":
            from pocket.sell_api import chat_complete

            p = rbac_principal(self.headers)
            agent = body.get("agent") or "planner"
            ok, msg = allow_agent(p, agent)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            prompt = body.get("prompt") or body.get("text") or body.get("task") or ""
            return self._json(
                200,
                chat_complete(
                    [{"role": "user", "content": prompt}],
                    agent=agent,
                    workspace=body.get("workspace") or "workspace",
                    api_key_id=self._api_key_id(),
                ),
            )

        if path in ("/v1/auth/passkey/allow",):
            from pocket.auth import is_home_lan_client
            from pocket.passkey import pairing_open

            if not is_home_lan_client(self.headers, getattr(self, "client_address", None)):
                who = rbac_principal(self.headers)
                if not (who.get("user") and who.get("role") in ("admin", "owner", "founder")):
                    return self._json(403, {"ok": False, "error": "Allow this phone from the PC (home Wi-Fi)."})
            return self._json(200, pairing_open(minutes=float(body.get("minutes") or 10)))
        if path in ("/v1/auth/passkey/register", "/v1/auth/passkey/finish"):
            from pocket.auth import is_home_lan_client
            from pocket.passkey import can_register, finish_register
            from pocket.phoneai_portal import mint_portal_token, portal_cookie

            lan = is_home_lan_client(self.headers, getattr(self, "client_address", None))
            seated = bool(rbac_principal(self.headers).get("user"))
            if not can_register(lan=lan, authed=seated):
                return self._json(403, {"ok": False, "error": "pair_required", "hint": "Open Portal on the PC first."})
            host = self.headers.get("Host") or "127.0.0.1:8787"
            res = finish_register(body if isinstance(body, dict) else {}, host=host)
            if not res.get("ok"):
                return self._json(401, res)
            xf = (self.headers.get("X-Forwarded-Proto") or "").lower()
            secure = xf == "https" or "medinatechlabs.net" in host.lower() or "trycloudflare.com" in host.lower()
            extra = [
                ("Set-Cookie", self._session_cookie(res["token"])),
                ("Set-Cookie", portal_cookie(mint_portal_token(str(res.get("user") or "face")), secure=secure)),
            ]
            return self._json(200, res, extra_headers=extra)
        if path in ("/v1/auth/device/mint", "/v1/auth/pair/mint"):
            from pocket.device_pair import mint as device_mint

            r = device_mint(client_ip=self._client_ip())
            return self._json(200 if r.get("ok") else 403, r)
        if path in ("/v1/auth/device/redeem", "/v1/auth/pair"):
            from pocket.device_pair import redeem as device_redeem
            from pocket.phoneai_portal import mint_portal_token, portal_cookie
            from pocket.ratelimit import hit as rl_hit

            ip = self._client_ip()
            ok_rl, reason = rl_hit("login", ip, kind="login")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            res = device_redeem(str((body or {}).get("code") or (body or {}).get("pair") or ""))
            if not res.get("ok"):
                return self._json(401, res)
            host = (self.headers.get("Host") or "").lower()
            xf = (self.headers.get("X-Forwarded-Proto") or "").lower()
            secure = xf == "https" or "medinatechlabs.net" in host or "trycloudflare.com" in host
            extra = [
                ("Set-Cookie", self._session_cookie(res["token"])),
                ("Set-Cookie", portal_cookie(mint_portal_token(str(res.get("user") or "pocket")), secure=secure)),
            ]
            return self._json(200, res, extra_headers=extra)
        if path in ("/v1/auth/passkey/login",):
            from pocket.passkey import finish_login
            from pocket.phoneai_portal import mint_portal_token, portal_cookie

            host = self.headers.get("Host") or "127.0.0.1:8787"
            res = finish_login(body if isinstance(body, dict) else {}, host=host)
            if not res.get("ok"):
                return self._json(401, res)
            xf = (self.headers.get("X-Forwarded-Proto") or "").lower()
            secure = xf == "https" or "medinatechlabs.net" in host.lower() or "trycloudflare.com" in host.lower()
            extra = [
                ("Set-Cookie", self._session_cookie(res["token"])),
                ("Set-Cookie", portal_cookie(mint_portal_token(str(res.get("user") or "face")), secure=secure)),
            ]
            return self._json(200, res, extra_headers=extra)
        if path == "/v1/auth/login":
            from pocket.ratelimit import hit
            from pocket.users import issue_token, verify

            ip = self._client_ip()
            ok_rl, reason = hit("login", ip, kind="login")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            # Accept every gate's field names: user | username | email | login
            uname = (
                body.get("user")
                or body.get("username")
                or body.get("email")
                or body.get("login")
                or body.get("name")
                or ""
            )
            pw = body.get("password") or body.get("pass") or body.get("pwd") or ""
            if isinstance(uname, str):
                uname = uname.strip()
            if not uname and pw:
                uname = "pocket"  # blank user on phone/public gates
            u = verify(str(uname or ""), str(pw or ""))
            if not u:
                record_auth_failure(ip)
                return self._json(
                    401,
                    {
                        "ok": False,
                        "error": "Username or password is wrong. Create an account on Sign up if you are new.",
                        "signup": "/signup",
                    },
                )
            clear_auth_failures(ip)
            tok = issue_token(u["user"])
            clis = {}
            try:
                from pocket.model_clis import ensure_seat

                clis = ensure_seat(u["user"], install_host=False)
            except Exception:
                clis = {}
            return self._json(
                200,
                {
                    "ok": True,
                    "token": tok,
                    "user": u,
                    "session": True,
                    "clis": (clis.get("seat") if isinstance(clis, dict) else clis) or {},
                },
                extra_headers=[("Set-Cookie", self._session_cookie(tok))],
            )

        # Desktop-only: trusted local auto-login (127.0.0.1 only). Real apps embed runtime.
        if path in ("/v1/auth/desktop", "/v1/auth/local"):
            from pocket.edition import product_id

            if product_id() == "users":
                return self._json(
                    403,
                    {
                        "ok": False,
                        "error": "POCKET for Users has no owner unlock. Sign in as a seat, or open Owner on :8787.",
                        "product": "users",
                    },
                )
            ip = self._client_ip()
            if ip not in ("127.0.0.1", "::1", "localhost"):
                return self._json(403, {"ok": False, "error": "desktop login only on localhost"})
            try:
                from pocket.auth import expected_user
                from pocket.users import issue_token, verify, list_users

                user = (expected_user() or "pocket").lower()
                # Prefer existing user record; else mint token for operator name
                users = {u["user"]: u for u in list_users()}
                if user in users:
                    rec = users[user]
                    u = {"user": user, "role": rec.get("role") or "admin", "display": rec.get("display") or "Operator"}
                else:
                    u = {"user": user, "role": "admin", "display": "Operator"}
                tok = issue_token(u["user"])
                return self._json(
                    200,
                    {"ok": True, "token": tok, "user": u, "desktop": True},
                    extra_headers=[("Set-Cookie", self._session_cookie(tok))],
                )
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)[:200]})

        if path in ("/v1/webmcp/scan", "/api/webmcp/scan"):
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.webmcp import scan as webmcp_scan

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="webmcp")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ok_rl, reason = rl_hit("webmcp_scan", self._client_ip(), kind="webmcp_scan")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                webmcp_scan(url=str(body.get("url") or ""), fusion=bool(body.get("fusion") or body.get("screen"))),
            )
        if path in ("/v1/webmcp/use", "/api/webmcp/use"):
            from pocket.host_control import allow as host_ok
            from pocket.webmcp import use_action

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="webmcp")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(
                200,
                use_action(str(body.get("name") or body.get("id") or body.get("action") or ""), prompt=str(body.get("prompt") or body.get("text") or "")),
            )
        if path in ("/v1/webmcp/find",):
            from pocket.webmcp import find_actions

            return self._json(200, {"ok": True, "hits": find_actions(str(body.get("q") or body.get("query") or ""))})

        if path in ("/v1/phoneai/settings", "/api/phoneai/settings"):
            from pocket.phoneai_settings import apply as phoneai_settings_apply

            return self._json(200, phoneai_settings_apply(body if isinstance(body, dict) else {}))
        if path in ("/v1/phoneai/anti", "/api/phoneai/anti"):
            from pocket.antigravity_chat import handle as anti_handle
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            action = str(body.get("action") or body.get("kind") or "send")
            text = str(body.get("text") or body.get("prompt") or body.get("message") or "")
            cwd = str(body.get("cwd") or "")
            return self._json(200, anti_handle(action, text, cwd=cwd))
        if path in ("/v1/phoneai/github", "/api/phoneai/github"):
            from pocket.phoneai_github import push as gh_push, snapshot as gh_snap

            if str(body.get("action") or "") in ("status", "snap", ""):
                return self._json(200, gh_snap())
            return self._json(200, gh_push(message=str(body.get("message") or "phoneai")))
        if path in ("/v1/phoneai/shell", "/api/phoneai/shell", "/v1/shell"):
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.shell_exec import run as sh_run

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="shell")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ip = self._client_ip()
            ok_rl, reason = rl_hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                sh_run(
                    str(body.get("command") or body.get("cmd") or body.get("shell") or ""),
                    cwd=str(body.get("cwd") or ""),
                    timeout=float(body.get("timeout") or 25),
                    allow_destructive=False,
                ),
            )
        if path in ("/v1/phoneai/harness", "/api/phoneai/harness", "/v1/harness"):
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="harness")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ip = self._client_ip()
            ok_rl, reason = rl_hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            from pocket.agent_arch import turn as arch_turn

            return self._json(
                200,
                arch_turn(
                    str(body.get("goal") or body.get("text") or body.get("prompt") or ""),
                    agent=str(body.get("agent") or body.get("persona") or ""),
                    seat=str(body.get("seat") or "phoneai"),
                    engine=str(body.get("engine") or "auto"),
                    grant_id=str(body.get("grant_id") or body.get("grant") or ""),
                    shell=str(body.get("shell") or body.get("command") or ""),
                    cwd=str(body.get("cwd") or ""),
                    use=str(body.get("use") or "auto"),
                    dry=bool(body.get("dry")),
                ),
            )
        if path in ("/v1/phoneai/voice-screen", "/api/phoneai/voice-screen", "/v1/voice-screen"):
            from pocket.voice_screen import act as voice_screen_act

            return self._json(
                200,
                voice_screen_act(
                    str(body.get("text") or body.get("prompt") or body.get("say") or ""),
                    which=str(body.get("which") or "portal"),
                ),
            )
        if path in ("/v1/phoneai/wear", "/api/phoneai/wear", "/v1/wear"):
            from pocket.host_control import allow as host_ok
            from pocket.wear import ingest as wear_ingest

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="wear")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(200, wear_ingest(body, which=str(body.get("which") or "portal")))
        if path in ("/v1/runtime/ensure", "/api/runtime/ensure", "/v1/host/ensure"):
            from pocket.auth import is_home_lan_client
            from pocket.host_runtime import ensure as runtime_ensure

            if not is_home_lan_client(self.headers, getattr(self, "client_address", None)):
                who = rbac_principal(self.headers)
                if not (who.get("user") or who.get("principal") in ("user", "api_key")):
                    return self._json(401, {"ok": False, "error": "sign in or use LAN to bring the host up"})
            return self._json(200, runtime_ensure(str(body.get("which") or body.get("id") or "all")))
        if path in ("/v1/runtime/install", "/api/runtime/install", "/v1/host/install"):
            from pocket.auth import is_home_lan_client
            from pocket.host_runtime import install as runtime_install

            if not is_home_lan_client(self.headers, getattr(self, "client_address", None)):
                who = rbac_principal(self.headers)
                if not (who.get("user") or who.get("principal") in ("user", "api_key")):
                    return self._json(401, {"ok": False, "error": "sign in or use LAN to install always-on"})
            return self._json(200, runtime_install())
        if path in ("/v1/phoneai/anti/touch", "/api/phoneai/anti/touch"):
            from pocket.antigravity_chat import anti_touch
            from pocket.phoneai_portal import touch_allowed
            from pocket.ratelimit import hit as rl_hit

            ip = self._client_ip()
            if not touch_allowed(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "sign in, use LAN, or open the PhoneAI tunnel URL"})
            ok_rl, reason = rl_hit("portal_touch", ip, kind="portal_touch")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                anti_touch(
                    str(body.get("kind") or "tap"),
                    nx=float(body.get("nx") if body.get("nx") is not None else 0.5),
                    ny=float(body.get("ny") if body.get("ny") is not None else 0.5),
                    dy=float(body.get("dy") or 0),
                    dx=float(body.get("dx") or 0),
                    text=str(body.get("text") or ""),
                    button=str(body.get("button") or "left"),
                    vk=int(body.get("vk") or 0),
                    n=int(body.get("n") or 1),
                ),
            )
        if path in ("/v1/eyes/touch", "/api/eyes/touch"):
            from pocket.agent_eyes import act as eyes_act
            from pocket.host_control import allow as host_ok

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="eyes")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(
                200,
                eyes_act(
                    str(body.get("kind") or "tap"),
                    which=str(body.get("which") or "portal"),
                    nx=float(body.get("nx") if body.get("nx") is not None else 0.5),
                    ny=float(body.get("ny") if body.get("ny") is not None else 0.5),
                    text=str(body.get("text") or ""),
                ),
            )
        if path in ("/v1/phoneai/portal/touch", "/api/phoneai/portal/touch"):
            from pocket.phoneai_portal import origin_ok, touch as portal_touch
            from pocket.phoneai_portal import touch_allowed
            from pocket.ratelimit import hit as rl_hit

            ip = self._client_ip()
            if not touch_allowed(self.headers, getattr(self, "client_address", None)):
                return self._json(
                    403,
                    {"ok": False, "error": "Touch blocked. Open Portal on this phone so a session cookie is set, or use LAN / sign in."},
                )
            if not origin_ok(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "origin blocked"})
            ok_rl, reason = rl_hit("portal_touch", ip, kind="portal_touch")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            kind = str(body.get("kind") or body.get("action") or "tap")
            result = portal_touch(
                kind,
                nx=float(body.get("nx") if body.get("nx") is not None else 0.5),
                ny=float(body.get("ny") if body.get("ny") is not None else 0.5),
                dy=float(body.get("dy") or 0),
                dx=float(body.get("dx") or 0),
                text=str(body.get("text") or body.get("app") or ""),
                target=str(body.get("target") or "desktop"),
                button=str(body.get("button") or "left"),
                vk=int(body.get("vk") or 0),
                n=int(body.get("n") or 1),
                hwnd=int(body.get("hwnd") or 0),
            )
            if kind in ("drag", "scroll", "joy", "nudge", "stick", "move", "hover", "down", "up", "hold", "press", "release", "move_window"):
                return self._json(200, {"ok": True, "kind": kind, "fast": True})
            return self._json(200, result)
        if path in ("/v1/phoneai/photos", "/api/phoneai/photos", "/v1/phoneai/photos/send"):
            from pocket.photo_pipe import send as photo_send

            return self._json(
                200,
                photo_send(
                    image=str(body.get("image") or ""),
                    name=str(body.get("name") or ""),
                    dest=str(body.get("dest") or "all"),
                    caption=str(body.get("caption") or body.get("text") or ""),
                ),
            )
        if path in ("/v1/nodes/view", "/v1/node/view"):
            from pocket.home_mesh import register_view_node

            return self._json(
                200,
                register_view_node(
                    kind=str(body.get("kind") or "tv"),
                    label=str(body.get("label") or ""),
                    ip=self._client_ip(),
                    ua=str(self.headers.get("User-Agent") or "")[:160],
                ),
            )
        if path in ("/v1/phoneai/doorbell", "/api/phoneai/doorbell"):
            from pocket.home_mesh import add_camera

            return self._json(
                200,
                add_camera(
                    name=str(body.get("name") or "doorbell"),
                    url=str(body.get("url") or ""),
                    kind=str(body.get("kind") or "mjpeg"),
                ),
            )
        if path in ("/v1/phoneai/cam/request", "/api/phoneai/cam/request"):
            from pocket.home_mesh import request_laptop_cam

            return self._json(200, request_laptop_cam(who=str(body.get("who") or "phoneai")))
        if path in ("/v1/phoneai/cam/decide", "/api/phoneai/cam/decide"):
            from pocket.home_mesh import decide_laptop_cam
            from pocket.phoneai_portal import touch_allowed

            if not touch_allowed(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "approve laptop camera on this PC (LAN or signed in)"})
            return self._json(
                200,
                decide_laptop_cam(bool(body.get("allow")), minutes=float(body.get("minutes") or 10)),
            )

        if path in ("/v1/phoneai/life", "/api/phoneai/life"):
            from pocket.phone_life import act as phone_life_act
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            kind = str(body.get("kind") or body.get("engine") or "auto")
            text = str(body.get("text") or body.get("prompt") or body.get("message") or "")
            extra = body.get("extra") if isinstance(body.get("extra"), dict) else {}
            if body.get("image") and "image" not in extra:
                extra["image"] = body.get("image")
            return self._json(200, phone_life_act(kind, text, extra=extra))
        if path in ("/v1/phoneai/sessions", "/api/phoneai/sessions"):
            from pocket.agent_runtime import create_phoneai_session

            return self._json(
                200,
                create_phoneai_session(
                    persona_id=str(body.get("persona") or body.get("persona_id") or "researcher"),
                    title=str(body.get("title") or ""),
                    kind=str(body.get("kind") or "both"),
                    long_term=body.get("long_term"),
                ),
            )
        if path in ("/v1/phoneai/talk", "/api/phoneai/talk"):
            from pocket.agent_runtime import talk

            return self._json(
                200,
                talk(
                    str(body.get("from") or body.get("from_agent") or "phoneai"),
                    str(body.get("to") or body.get("to_agent") or "grok"),
                    str(body.get("text") or body.get("body") or body.get("message") or ""),
                    subject=str(body.get("subject") or "talk"),
                ),
            )
        if path in ("/v1/phoneai/work", "/api/phoneai/work"):
            from pocket.phoneai_bridge import work as phoneai_work
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            text = str(body.get("text") or body.get("prompt") or body.get("message") or "")
            engine = str(body.get("engine") or "auto")
            thread_id = str(body.get("thread_id") or body.get("session_id") or "")
            return self._json(200, phoneai_work(text, engine=engine, thread_id=thread_id))
        if path in ("/v1/phoneai/work/stream", "/api/phoneai/work/stream"):
            from pocket.phoneai_bridge import work_stream_chunks
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("phoneai_work", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            text = str(body.get("text") or body.get("prompt") or body.get("message") or "")
            engine = str(body.get("engine") or "auto")
            thread_id = str(body.get("thread_id") or body.get("session_id") or "")
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            for ev, payload in work_stream_chunks(text, engine=engine, thread_id=thread_id):
                data = payload if isinstance(payload, str) else json.dumps(payload, default=str)
                chunk = f"event: {ev}\ndata: {data}\n\n".encode("utf-8")
                self.wfile.write(chunk)
                try:
                    self.wfile.flush()
                except Exception:
                    break
            self.close_connection = True
            return None

        if path == "/api/pair/init":
            from pocket.phoneai_bridge import pair_init

            return self._json(200, pair_init())
        if path == "/api/pair/confirm":
            from pocket.phoneai_bridge import pair_confirm

            res = pair_confirm(str(body.get("pairing_code") or ""), str(body.get("device_label") or "phone"))
            return self._json(int(res.get("http") or 200), res)
        if path == "/api/pair/auto":
            from pocket.phoneai_bridge import pair_auto

            res = pair_auto(allow=True)
            return self._json(int(res.get("http") or 200), res)
        if path == "/api/pair/revoke":
            from pocket.phoneai_bridge import pair_revoke, session_from_bearer

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            return self._json(200, pair_revoke(sess))
        if path == "/api/execute":
            from pocket.phoneai_bridge import execute as phoneai_execute, session_from_bearer

            sess = session_from_bearer(self.headers.get("Authorization") or self.headers.get("authorization") or "")
            if not sess:
                return self._json(401, {"ok": False, "detail": "missing_bearer_token"})
            doc = phoneai_execute(sess, body)
            return self._json(int(doc.get("http") or 200), doc)

        if path in ("/v1/companion/chat", "/v1/live/chat"):
            from pocket.live_companion import chat as live_chat
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("companion", ip, kind="api")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            text = str(body.get("text") or body.get("message") or body.get("q") or "")
            hist = body.get("history") if isinstance(body.get("history"), list) else []
            return self._json(200, live_chat(text, history=hist))

        if path == "/v1/auth/github/local":
            from pocket.oauth_login import github_local_login

            res = github_local_login(client_ip=self._client_ip())
            if not res.get("ok"):
                return self._json(401, res)
            return self._json(
                200,
                res,
                extra_headers=[("Set-Cookie", self._session_cookie(res["token"]))],
            )

        if path == "/v1/auth/code/mint":
            from pocket.oauth_login import mint_login_code

            res = mint_login_code(client_ip=self._client_ip())
            return self._json(200 if res.get("ok") else 403, res)

        if path == "/v1/auth/code":
            from pocket.oauth_login import redeem_login_code
            from pocket.ratelimit import hit

            ip = self._client_ip()
            ok_rl, reason = hit("login", ip, kind="login")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            res = redeem_login_code(str(body.get("code") or ""))
            if not res.get("ok"):
                record_auth_failure(ip)
                return self._json(401, res)
            clear_auth_failures(ip)
            return self._json(
                200,
                res,
                extra_headers=[("Set-Cookie", self._session_cookie(res["token"]))],
            )

        if path == "/v1/auth/register":
            from pocket.ratelimit import hit
            from pocket.users import issue_token, register

            ip = self._client_ip()
            ok_rl, reason = hit("register", ip, kind="register")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            res = register(
                body.get("user") or body.get("username") or "",
                body.get("password") or "",
                body.get("invite") or body.get("invite_code") or "",
                display=body.get("display") or body.get("name") or "",
                accepted_terms=bool(body.get("accepted_terms") or body.get("terms")),
                plan=str(body.get("plan") or ""),
                channel=str(body.get("channel") or "public"),
                email=str(body.get("email") or ""),
            )
            if not res.get("ok"):
                record_auth_failure(ip)
                return self._json(400, res)
            tok = issue_token(res["user"])
            return self._json(
                200,
                {**res, "token": tok},
                extra_headers=[("Set-Cookie", self._session_cookie(tok))],
            )

        if path == "/v1/auth/logout":
            from pocket.users import revoke_token

            tok = (
                self.headers.get("X-Pocket-Token")
                or self.headers.get("x-pocket-token")
                or body.get("token")
                or ""
            )
            return self._json(
                200,
                {"ok": revoke_token(tok.strip())},
                extra_headers=[("Set-Cookie", self._session_cookie("", clear=True))],
            )

        if path == "/v1/auth/password":
            from pocket.users import change_password

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            user = body.get("user") or p.get("user") or ""
            if not is_admin(p) and user != p.get("user"):
                return self._json(403, {"ok": False, "error": "can only change own password"})
            return self._json(
                200,
                change_password(user, body.get("old_password") or "", body.get("new_password") or ""),
            )

        if path == "/v1/auth/invite/rotate":
            from pocket.users import rotate_invite

            p = rbac_principal(self.headers)
            ok, msg = allow_admin_action(p, "rotate_invite")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            return self._json(200, rotate_invite())

        if path in ("/v1/admin/invites", "/v1/auth/invites/mint"):
            # Mint a cryptographic seat key — raw key returned once; users create OWN accounts
            from pocket.users import mint_seat_invite

            p = rbac_principal(self.headers)
            ok, msg = allow_admin_action(p, "rotate_invite")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            return self._json(
                200,
                mint_seat_invite(
                    label=body.get("label") or body.get("name") or "seat",
                    max_uses=int(body.get("max_uses") or 1),
                    expires_days=int(body.get("expires_days") or 30),
                    created_by=p.get("user") or "admin",
                ),
            )

        if path == "/v1/auth/me":
            u = rbac_principal(self.headers)
            if (u.get("role") or "none") == "none":
                return self._json(401, {"ok": False})
            return self._json(200, {"ok": True, "user": u})

        if path == "/v1/live/connect":
            sid = (body.get("service") or body.get("id") or "").strip()
            if sid == "all" or not sid:
                return self._json(200, connect_all_down())
            return self._json(200, connect_service(sid))

        if path == "/v1/files/upload":
            p = rbac_principal(self.headers)
            if not is_founder(p):
                # Market: only their tenant tree (never founder disk)
                import base64
                import re as _re
                from pocket.platform_space import tenant_root

                user = (p.get("user") or "anonymous").strip().lower()
                name = (body.get("filename") or "upload.bin").replace("\\", "/").split("/")[-1]
                if not name or ".." in name or not _re.match(r"^[\w.\- ()\[\]]+$", name):
                    return self._json(400, {"ok": False, "error": "invalid filename"})
                try:
                    raw = base64.b64decode(body.get("content_base64") or "", validate=False)
                except Exception:
                    return self._json(400, {"ok": False, "error": "bad base64"})
                up = tenant_root(user) / "uploads"
                up.mkdir(parents=True, exist_ok=True)
                dest = up / name
                dest.write_bytes(raw)
                return self._json(
                    200,
                    {
                        "ok": True,
                        "edition": "market",
                        "founder_files": False,
                        "path": f"uploads/{name}",
                        "bytes": len(raw),
                    },
                )
            return self._json(
                200,
                upload_file(
                    workspace=body.get("workspace") or "workspace",
                    filename=body.get("filename") or "",
                    content_base64=body.get("content_base64") or "",
                    size=int(body.get("size") or 0),
                ),
            )

        if path in ("/v1/space/write", "/v1/space/read"):
            from pocket.platform_space import read_text, write_text

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            user = p.get("user") or ""
            if is_founder(p) and body.get("user"):
                user = body.get("user")
            elif is_founder(p):
                return self._json(400, {"ok": False, "error": "founder uses host paths; market uses /v1/space"})
            rel = body.get("path") or body.get("rel") or ""
            if path.endswith("/write"):
                return self._json(200, write_text(user, rel, body.get("content") or body.get("text") or ""))
            return self._json(200, read_text(user, rel))

        if path == "/v1/desktop/open":
            p = rbac_principal(self.headers)
            if not is_founder(p):
                return self._json(
                    403,
                    {
                        "ok": False,
                        "error": "Founder-host desktop only. Market POCKET uses /v1/space (your files).",
                        "edition": "market",
                    },
                )
            from pocket.desktop import open_app

            return self._json(
                200,
                open_app(
                    body.get("app") or body.get("id") or "",
                    args=body.get("args") or "",
                    path=body.get("path") or "",
                ),
            )

        # KEEP — self-hosted agents until chat ends
        if path in ("/v1/keep/start",):
            from pocket.keep_agents import start as keep_start

            p = rbac_principal(self.headers)
            return self._json(
                200,
                keep_start(
                    session_id=str((body or {}).get("session_id") or (body or {}).get("session") or ""),
                    goal=str((body or {}).get("goal") or (body or {}).get("prompt") or (body or {}).get("text") or ""),
                    graph_id=str((body or {}).get("graph_id") or (body or {}).get("graph") or "default"),
                    interval_sec=float((body or {}).get("interval_sec") or 45),
                    max_hours=float((body or {}).get("max_hours") or 4),
                    with_browser=bool((body or {}).get("with_browser", True)),
                    browser_url=str((body or {}).get("browser_url") or (body or {}).get("url") or "about:blank"),
                    label=str((body or {}).get("label") or ""),
                    owner=str(p.get("user") or (body or {}).get("owner") or ""),
                ),
            )
        if path in ("/v1/keep/stop",):
            from pocket.keep_agents import stop as keep_stop

            return self._json(
                200,
                keep_stop(
                    str((body or {}).get("id") or (body or {}).get("keep_id") or ""),
                    session_id=str((body or {}).get("session_id") or ""),
                ),
            )
        if path in ("/v1/keep/end", "/v1/chat/end", "/v1/session/end"):
            from pocket.keep_agents import end_chat

            return self._json(
                200,
                end_chat(str((body or {}).get("session_id") or (body or {}).get("session") or "")),
            )
        if path in ("/v1/keep/tick",):
            from pocket.keep_agents import tick as keep_tick

            return self._json(
                200,
                keep_tick(str((body or {}).get("id") or (body or {}).get("keep_id") or "")),
            )
        # ISOLATE — Docker / profile browsers
        if path in ("/v1/isolate/start", "/v1/docker-browser/start"):
            from pocket.docker_browser import start as isolate_start

            return self._json(
                200,
                isolate_start(
                    session_id=str((body or {}).get("session_id") or ""),
                    keep_id=str((body or {}).get("keep_id") or ""),
                    url=str((body or {}).get("url") or "about:blank"),
                    label=str((body or {}).get("label") or ""),
                    prefer=str((body or {}).get("prefer") or "auto"),
                ),
            )
        if path in ("/v1/isolate/stop", "/v1/docker-browser/stop"):
            from pocket.docker_browser import stop as isolate_stop

            return self._json(
                200,
                isolate_stop(
                    str((body or {}).get("id") or (body or {}).get("browser_id") or ""),
                    session_id=str((body or {}).get("session_id") or ""),
                    keep_id=str((body or {}).get("keep_id") or ""),
                ),
            )
        # RECALL codes
        if path in ("/v1/recall/mint",):
            from pocket.recall_codes import mint as recall_mint

            p = rbac_principal(self.headers)
            return self._json(
                200,
                recall_mint(
                    keep_id=str((body or {}).get("keep_id") or ""),
                    session_id=str((body or {}).get("session_id") or ""),
                    mission_id=str((body or {}).get("mission_id") or ""),
                    loomgraph_run_id=str((body or {}).get("loomgraph_run_id") or (body or {}).get("run_id") or ""),
                    label=str((body or {}).get("label") or ""),
                    ttl_sec=int((body or {}).get("ttl_sec") or 0),
                    single_use=bool((body or {}).get("single_use", True)),
                    owner=str(p.get("user") or (body or {}).get("owner") or ""),
                    note=str((body or {}).get("note") or ""),
                ),
            )
        if path in ("/v1/recall/redeem",):
            from pocket.recall_codes import redeem as recall_redeem

            p = rbac_principal(self.headers)
            return self._json(
                200,
                recall_redeem(str((body or {}).get("code") or ""), peer=str(p.get("user") or "")),
            )
        if path in ("/v1/recall/revoke",):
            from pocket.recall_codes import revoke as recall_revoke

            return self._json(
                200,
                recall_revoke(
                    str((body or {}).get("id") or (body or {}).get("code_id") or ""),
                    code=str((body or {}).get("code") or ""),
                ),
            )
        # POCKET MAIL official
        if path in ("/v1/mail/draft",):
            from pocket.pocket_mail import draft as mail_draft

            p = rbac_principal(self.headers)
            return self._json(
                200,
                mail_draft(
                    to=str((body or {}).get("to") or ""),
                    subject=str((body or {}).get("subject") or ""),
                    body=str((body or {}).get("body") or (body or {}).get("text") or ""),
                    template=str((body or {}).get("template") or "custom"),
                    fields=(body or {}).get("fields") if isinstance((body or {}).get("fields"), dict) else body,
                    from_addr=str((body or {}).get("from") or ""),
                    cc=str((body or {}).get("cc") or ""),
                    owner=str(p.get("user") or ""),
                ),
            )
        if path in ("/v1/mail/send",):
            from pocket.pocket_mail import send as mail_send

            p = rbac_principal(self.headers)
            return self._json(
                200,
                mail_send(
                    to=str((body or {}).get("to") or ""),
                    subject=str((body or {}).get("subject") or ""),
                    body=str((body or {}).get("body") or (body or {}).get("text") or ""),
                    template=str((body or {}).get("template") or "custom"),
                    fields=(body or {}).get("fields") if isinstance((body or {}).get("fields"), dict) else None,
                    draft_id=str((body or {}).get("draft_id") or (body or {}).get("id") or ""),
                    dry_run=bool((body or {}).get("dry_run")),
                    also_outlook_draft=bool((body or {}).get("outlook") or (body or {}).get("also_outlook_draft")),
                    owner=str(p.get("user") or ""),
                ),
            )
        # Agent Mail — our own accounts + inboxes for agents
        if path in ("/v1/agent-mail/accounts", "/v1/agent-mail/create"):
            from pocket.agent_mail import create_account

            b = body or {}
            return self._json(
                200,
                create_account(
                    str(b.get("agent") or b.get("agent_id") or b.get("id") or b.get("name") or ""),
                    name=str(b.get("name") or ""),
                    blurb=str(b.get("blurb") or b.get("desc") or ""),
                    kind=str(b.get("kind") or "agent"),
                    owner=str(b.get("owner") or ""),
                ),
            )
        if path in ("/v1/agent-mail/send",):
            from pocket.auth import is_home_lan_client
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.agent_mail import send as agent_mail_send

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="mail")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ok_rl, reason = rl_hit("mail_send", self._client_ip(), kind="mail_send")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            b = body or {}
            who = rbac_principal(self.headers)
            from_agent = str(b.get("from") or b.get("from_agent") or b.get("agent") or "")
            if not is_home_lan_client(self.headers, getattr(self, "client_address", None)):
                from_agent = str(who.get("user") or from_agent or "scribe")
            if not from_agent:
                from_agent = "scribe"
            return self._json(
                200,
                agent_mail_send(
                    from_agent=from_agent,
                    to=str(b.get("to") or ""),
                    subject=str(b.get("subject") or "POCKET agent mail"),
                    body=str(b.get("body") or b.get("text") or "")[:20000],
                    cc=str(b.get("cc") or ""),
                    external=bool(b.get("external")),
                    dry_run=bool(b.get("dry_run")),
                ),
            )
        if path in ("/v1/agent-mail/read",):
            from pocket.agent_mail import read_message

            b = body or {}
            return self._json(
                200,
                read_message(
                    str(b.get("agent") or b.get("agent_id") or "assist"),
                    str(b.get("id") or b.get("mail_id") or b.get("message_id") or ""),
                    mark_read=b.get("mark_read", True) is not False,
                ),
            )
        if path in ("/v1/agent-mail/inbox",):
            from pocket.agent_mail import inbox as agent_inbox

            b = body or {}
            return self._json(
                200,
                agent_inbox(
                    str(b.get("agent") or b.get("agent_id") or "assist"),
                    limit=int(b.get("limit") or 30),
                    unread_only=bool(b.get("unread_only") or b.get("unread")),
                ),
            )
        # Website UI + Python engines for models
        if path in ("/v1/web-ui/open",):
            from pocket.web_ui_engine import open_url

            b = body or {}
            return self._json(
                200,
                open_url(str(b.get("url") or b.get("text") or ""), profile=str(b.get("profile") or "Default")),
            )
        if path in ("/v1/web-ui/sense",):
            from pocket.web_ui_engine import sense

            b = body or {}
            return self._json(200, sense(agent=str(b.get("agent") or "api")))
        if path in ("/v1/web-ui/act",):
            from pocket.web_ui_engine import act

            b = body or {}
            return self._json(
                200,
                act(
                    str(b.get("action") or b.get("text") or "sense"),
                    agent=str(b.get("agent") or "api"),
                    **{k: v for k, v in b.items() if k not in ("action", "text", "agent")},
                ),
            )
        if path in ("/v1/web-ui/browse",):
            from pocket.web_ui_engine import browse

            b = body or {}
            return self._json(
                200,
                browse(str(b.get("url") or b.get("text") or ""), profile=str(b.get("profile") or "Default")),
            )
        if path in ("/v1/web-ui/fetch",):
            from pocket.web_ui_engine import fetch

            b = body or {}
            return self._json(
                200,
                fetch(str(b.get("url") or b.get("text") or ""), max_chars=int(b.get("max_chars") or 14000)),
            )
        if path in ("/v1/web-ui/search",):
            from pocket.web_ui_engine import search

            b = body or {}
            return self._json(
                200,
                search(
                    str(b.get("query") or b.get("q") or b.get("text") or ""),
                    max_results=int(b.get("max_results") or 6),
                ),
            )
        if path in ("/v1/python-engine", "/v1/python-engine/run"):
            from pocket.web_ui_engine import run_python_engine

            b = body or {}
            return self._json(
                200,
                run_python_engine(
                    str(b.get("engine") or b.get("name") or b.get("id") or "web_research"),
                    str(b.get("prompt") or b.get("text") or b.get("goal") or ""),
                    params=b if isinstance(b, dict) else {},
                ),
            )
        if path in ("/v1/multi-plan", "/v1/multi-plan/run", "/v1/multiplan/run", "/v1/plan/exec"):
            from pocket.multi_plan import run_multi_plan

            b = body or {}
            return self._json(
                200,
                run_multi_plan(
                    str(b.get("goal") or b.get("prompt") or b.get("text") or b.get("task") or ""),
                    job_id=str(b.get("job_id") or ""),
                    session_id=str(b.get("session_id") or ""),
                    max_tasks=int(b.get("max_tasks") or 24),
                ),
            )
        # Agent calls — virtual numbers + softphone / optional PSTN
        if path in ("/v1/calls/numbers", "/v1/agent-calls/numbers", "/v1/calls/assign"):
            from pocket.agent_calls import assign_number, list_numbers

            b = body or {}
            if b.get("agent") or b.get("agent_id") or path.endswith("/assign"):
                return self._json(
                    200,
                    assign_number(
                        str(b.get("agent") or b.get("agent_id") or b.get("id") or ""),
                        name=str(b.get("name") or ""),
                        area=str(b.get("area") or "201"),
                        line=str(b.get("line") or ""),
                    ),
                )
            return self._json(200, list_numbers())
        if path in ("/v1/calls/dial", "/v1/agent-calls/dial"):
            from pocket.agent_calls import dial

            b = body or {}
            return self._json(
                200,
                dial(
                    from_agent=str(b.get("from") or b.get("from_agent") or b.get("agent") or "phone_agent"),
                    to=str(b.get("to") or b.get("number") or ""),
                    purpose=str(b.get("purpose") or b.get("reason") or ""),
                    text=str(b.get("text") or b.get("prompt") or ""),
                    mode=str(b.get("mode") or "soft"),
                    session_id=str(b.get("session_id") or ""),
                ),
            )
        if path in ("/v1/calls/answer", "/v1/agent-calls/answer"):
            from pocket.agent_calls import answer

            b = body or {}
            return self._json(
                200,
                answer(
                    str(b.get("id") or b.get("call_id") or ""),
                    by=str(b.get("by") or b.get("agent") or "user"),
                ),
            )
        if path in ("/v1/calls/hangup", "/v1/agent-calls/hangup"):
            from pocket.agent_calls import hangup

            b = body or {}
            return self._json(
                200,
                hangup(
                    str(b.get("id") or b.get("call_id") or ""),
                    reason=str(b.get("reason") or "hangup"),
                ),
            )
        if path in ("/v1/calls/speak", "/v1/agent-calls/speak"):
            from pocket.agent_calls import speak

            b = body or {}
            return self._json(
                200,
                speak(
                    str(b.get("id") or b.get("call_id") or ""),
                    str(b.get("text") or b.get("message") or ""),
                    role=str(b.get("role") or "agent"),
                ),
            )
        if path in ("/v1/engine-uses", "/v1/engines/uses"):
            from pocket.web_ui_engine import list_uses, pick_use, run_use

            b = body or {}
            if b.get("use") or b.get("use_id"):
                return self._json(
                    200,
                    run_use(
                        str(b.get("use") or b.get("use_id") or ""),
                        str(b.get("prompt") or b.get("text") or b.get("goal") or ""),
                        params=b,
                    ),
                )
            if b.get("goal") or b.get("prompt") or b.get("text"):
                return self._json(
                    200,
                    pick_use(str(b.get("goal") or b.get("prompt") or b.get("text") or "")),
                )
            return self._json(200, list_uses())
        # Model Forge — AI builds models and registers on platform
        if path in ("/v1/models/build", "/v1/model-forge/build"):
            from pocket.model_forge import build_model

            b = body or {}
            return self._json(
                200,
                build_model(
                    model_id=str(b.get("model_id") or b.get("id") or ""),
                    name=str(b.get("name") or ""),
                    kind=str(b.get("kind") or "template"),
                    description=str(b.get("description") or b.get("text") or b.get("prompt") or ""),
                    tags=b.get("tags") if isinstance(b.get("tags"), list) else None,
                    template=str(b.get("template") or ""),
                    rules=b.get("rules") if isinstance(b.get("rules"), list) else None,
                    default=str(b.get("default") or ""),
                    formula=str(b.get("formula") or ""),
                    wrap_engine=str(b.get("wrap_engine") or ""),
                    wrap_params=b.get("wrap_params") if isinstance(b.get("wrap_params"), dict) else None,
                    code=str(b.get("code") or ""),
                    system=str(b.get("system") or ""),
                    fit_keywords=b.get("fit_keywords") if isinstance(b.get("fit_keywords"), list) else None,
                    register_now=b.get("register_now", True) is not False,
                    author=str(b.get("author") or "agent"),
                ),
            )
        if path in ("/v1/models/register", "/v1/model-forge/register"):
            from pocket.model_forge import register_built

            b = body or {}
            return self._json(
                200,
                register_built(str(b.get("model") or b.get("model_id") or b.get("id") or "")),
            )
        if path in ("/v1/models/suggest", "/v1/model-forge/suggest"):
            from pocket.model_forge import suggest_from_goal

            b = body or {}
            return self._json(
                200,
                suggest_from_goal(str(b.get("goal") or b.get("prompt") or b.get("text") or "")),
            )

        # LOOMGRAPH run — default multi-step graph loop
        if path in (
            "/v1/loomgraph/run",
            "/v1/graph/run",
            "/v1/harness/loomgraph/run",
            "/v1/loomgraph/execute",
        ):
            from pocket.loomgraph import format_run_markdown, run as loomgraph_run

            p = rbac_principal(self.headers)
            r = loomgraph_run(
                (body or {}).get("goal")
                or (body or {}).get("prompt")
                or (body or {}).get("text")
                or (body or {}).get("message")
                or "",
                graph_id=str((body or {}).get("graph_id") or (body or {}).get("graph") or (body or {}).get("playbook") or ""),
                max_loops=int((body or {}).get("max_loops") or 3),
                max_nodes=int((body or {}).get("max_nodes") or 24),
                dry_run=bool((body or {}).get("dry_run")),
                author=str(p.get("user") or (body or {}).get("author") or ""),
                mode=str((body or {}).get("mode") or ""),
                force_share=bool((body or {}).get("force_share") or (body or {}).get("share")),
                integration_id=str((body or {}).get("integration_id") or (body or {}).get("integration") or ""),
            )
            if bool((body or {}).get("markdown", True)):
                r["markdown"] = format_run_markdown(r)
            return self._json(200, r)

        # Creative Studio chat (OpenAI-style multi-mode)
        if path in ("/v1/creative/chat", "/v1/studio/creative/chat", "/v1/creative/generate"):
            from pocket.creative_studio import chat as creative_chat

            p = rbac_principal(self.headers)
            return self._json(
                200,
                creative_chat(
                    (body or {}).get("message")
                    or (body or {}).get("text")
                    or (body or {}).get("prompt")
                    or "",
                    mode=str((body or {}).get("mode") or "chat"),
                    session_id=str((body or {}).get("session_id") or (body or {}).get("session") or ""),
                    agent=str((body or {}).get("agent") or ""),
                    author=str(p.get("user") or (body or {}).get("author") or ""),
                    auto_media=bool((body or {}).get("auto_media", True)),
                ),
            )
        # Community — intentional public shares only
        if path in ("/v1/community/share", "/v1/shares", "/v1/community/post"):
            from pocket.community_share import share as community_share

            p = rbac_principal(self.headers)
            tags = (body or {}).get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            return self._json(
                200,
                community_share(
                    author=str(p.get("user") or (body or {}).get("author") or "anonymous"),
                    display_name=str((body or {}).get("display_name") or p.get("user") or ""),
                    title=str((body or {}).get("title") or ""),
                    body=str((body or {}).get("body") or (body or {}).get("content") or ""),
                    kind=str((body or {}).get("kind") or "note"),
                    tags=tags,
                    media_url=str((body or {}).get("media_url") or ""),
                    preview=str((body or {}).get("preview") or ""),
                    source=str((body or {}).get("source") or "creative_studio"),
                    artifact=(body or {}).get("artifact") if isinstance((body or {}).get("artifact"), dict) else None,
                ),
            )
        if path in ("/v1/community/unshare", "/v1/shares/delete"):
            from pocket.community_share import unshare as community_unshare

            p = rbac_principal(self.headers)
            return self._json(
                200,
                community_unshare(
                    str((body or {}).get("id") or (body or {}).get("share_id") or ""),
                    author=str(p.get("user") or (body or {}).get("author") or ""),
                ),
            )

        # Integrations execute — Discord desktop, Edge SaaS, working board, agents
        if path in (
            "/v1/integrations/execute",
            "/v1/connectors/execute",
            "/v1/integrations/run",
        ):
            from pocket.integrations_exec import execute as integration_execute

            return self._json(
                200,
                integration_execute(
                    (body or {}).get("id")
                    or (body or {}).get("integration")
                    or (body or {}).get("name")
                    or "",
                    text=(body or {}).get("text") or (body or {}).get("prompt") or "",
                    prompt=(body or {}).get("prompt") or "",
                    dry_run=bool((body or {}).get("dry_run")),
                    prefer=str((body or {}).get("prefer") or "auto"),
                    profile=str((body or {}).get("profile") or "Default"),
                    open_browser=bool((body or {}).get("open_browser", True)),
                    open_desktop=bool((body or {}).get("open_desktop", True)),
                ),
            )
        if path in (
            "/v1/integrations/execute_all",
            "/v1/integrations/smoke",
            "/v1/connectors/execute_all",
        ):
            from pocket.integrations_exec import execute_all as integration_execute_all

            only = (body or {}).get("only") or (body or {}).get("ids")
            if isinstance(only, str):
                only = [x.strip() for x in only.split(",") if x.strip()]
            return self._json(
                200,
                integration_execute_all(
                    dry_run=bool((body or {}).get("dry_run", True)),
                    only=only,
                    prefer=str((body or {}).get("prefer") or "auto"),
                ),
            )
        if path.startswith("/v1/integrations/") and path.rstrip("/").endswith("/execute"):
            from pocket.integrations_exec import execute as integration_execute

            iid = path.rstrip("/").rsplit("/", 2)[-2] if path.count("/") >= 3 else ""
            # /v1/integrations/{id}/execute
            parts = [p for p in path.strip("/").split("/") if p]
            # ["v1", "integrations", "{id}", "execute"]
            if len(parts) >= 4 and parts[-1] == "execute":
                iid = parts[-2]
            return self._json(
                200,
                integration_execute(
                    iid or (body or {}).get("id") or "",
                    text=(body or {}).get("text") or (body or {}).get("prompt") or "",
                    prompt=(body or {}).get("prompt") or "",
                    dry_run=bool((body or {}).get("dry_run")),
                    prefer=str((body or {}).get("prefer") or "auto"),
                    profile=str((body or {}).get("profile") or "Default"),
                    open_browser=bool((body or {}).get("open_browser", True)),
                    open_desktop=bool((body or {}).get("open_desktop", True)),
                ),
            )

        if path in ("/v1/preview", "/v1/previews", "/v1/preview/put"):
            from pocket.app_preview import put_html

            return self._json(
                200,
                put_html(
                    body.get("html") or body.get("content") or "",
                    title=body.get("title") or "App preview",
                    source=body.get("source") or "api",
                    job_id=body.get("job_id") or "",
                ),
            )
        if path in ("/v1/drafts", "/v1/drafts/create"):
            from pocket.work_surface import create_draft

            return self._json(
                200,
                create_draft(
                    title=body.get("title") or "Untitled draft",
                    kind=body.get("kind") or body.get("type") or "html",
                    content=body.get("content") or body.get("html") or body.get("body") or "",
                    layer=body.get("layer") or "preview",
                    source=body.get("source") or "api",
                    meta=body.get("meta") if isinstance(body.get("meta"), dict) else {},
                ),
            )
        if path in ("/v1/drafts/update",):
            from pocket.work_surface import update_draft

            return self._json(
                200,
                update_draft(
                    body.get("id") or body.get("draft_id") or "",
                    body.get("content") or body.get("html") or "",
                    title=body.get("title") or "",
                ),
            )
        if path in ("/v1/drafts/promote", "/v1/promote"):
            from pocket.work_surface import promote_draft

            return self._json(
                200,
                promote_draft(
                    body.get("id") or body.get("draft_id") or "",
                    target=body.get("target") or body.get("to") or "folder",
                    name=body.get("name") or body.get("title") or "",
                    public=body.get("public", True) is not False,
                ),
            )
        if path in ("/v1/github/clone",):
            from pocket.repos import clone_repo

            return self._json(200, clone_repo(body.get("repo") or body.get("url") or body.get("name") or ""))
        if path in ("/v1/github/create",):
            from pocket.repos import create_github_repo

            return self._json(
                200,
                create_github_repo(
                    body.get("name") or "pocket-app",
                    public=body.get("public", True) is not False,
                    source_path=body.get("path") or body.get("source") or "",
                ),
            )
        if path in ("/v1/github/pr", "/v1/github/pull"):
            from pocket.github_hub import create_pr

            return self._json(
                200,
                create_pr(
                    body.get("title") or "POCKET update",
                    body=body.get("body") or "",
                    base=body.get("base") or "main",
                    head=body.get("head") or "",
                    draft=bool(body.get("draft")),
                    cwd=body.get("cwd") or "",
                    repo=body.get("repo") or "",
                ),
            )

        if path == "/v1/web/fetch":
            from pocket.web_research import fetch_url

            return self._json(200, fetch_url(body.get("url") or ""))

        if path == "/v1/web/search":
            from pocket.web_research import search_web

            return self._json(200, search_web(body.get("query") or body.get("q") or ""))

        if path == "/v1/nexus/run":
            from pocket.nexus_bridge import run_worker

            return self._json(
                200,
                run_worker(
                    body.get("worker") or "Bridge",
                    body.get("task") or "list_servers",
                    body.get("params") or {},
                ),
            )

        if path == "/v1/nexus/list":
            from pocket.nexus_bridge import list_capabilities

            return self._json(200, list_capabilities())

        if path == "/v1/tokenomics/mint":
            p = rbac_principal(self.headers)
            ok, msg = allow_admin_action(p, "mint")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            return self._json(200, mint(int(body.get("amount") or 0), reason=body.get("reason") or "topup"))

        if path == "/v1/deploy":
            p = rbac_principal(self.headers)
            ok, msg = allow_admin_action(p, "deploy")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            kind = (body.get("kind") or "static").lower()
            ws = body.get("workspace") or "workspace"
            title = body.get("title") or ""
            port = int(body.get("port") or 0)
            if kind == "static":
                return self._json(
                    200,
                    deploy_static(
                        workspace=ws,
                        subpath=body.get("subpath") or "",
                        title=title,
                        port=port,
                    ),
                )
            if kind in ("npm", "python", "py", "process"):
                return self._json(
                    200,
                    deploy_process(
                        kind="python" if kind in ("python", "py") else ("npm" if kind == "npm" else "npm"),
                        workspace=ws,
                        command=body.get("command") or "",
                        title=title,
                        port=port,
                        cwd_subpath=body.get("subpath") or "",
                    ),
                )
            return self._json(400, {"error": "kind must be static|npm|python", "hint": "optional command= override"})

        if path in ("/v1/terminals", "/v1/console", "/v1/consoles"):
            p = rbac_principal(self.headers)
            ok, msg = allow_mode(p, "term")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            # Agent convenience: run a line without managing terminal id
            if body.get("command") or body.get("text") or body.get("run"):
                from pocket.terminals import agent_run

                return self._json(
                    200,
                    agent_run(
                        body.get("command") or body.get("text") or body.get("run") or "",
                        session_id=body.get("session_id") or "",
                        kind=body.get("kind") or "powershell",
                        wait_ms=int(body.get("wait_ms") or 700),
                    ),
                )
            return self._json(
                200,
                {
                    "ok": True,
                    **create_terminal(
                        kind=body.get("kind") or "powershell",
                        workspace=body.get("workspace") or "workspace",
                        session_id=body.get("session_id") or "",
                        distro=body.get("distro") or "",
                        label=body.get("label") or "",
                    ),
                },
            )
        if path in ("/v1/console/ensure", "/v1/terminals/ensure"):
            from pocket.terminals import ensure_agent_console

            return self._json(
                200,
                ensure_agent_console(
                    body.get("session_id") or "",
                    kind=body.get("kind") or "powershell",
                    workspace=body.get("workspace") or "workspace",
                ),
            )
        if path.startswith("/v1/terminals/") and path.endswith("/send"):
            tid = path.split("/v1/terminals/", 1)[-1].replace("/send", "")
            return self._json(200, send_terminal(tid, body.get("text") or body.get("command") or ""))

        if path == "/v1/grok/pull":
            # Force a full research plan package (no wait for session)
            path_md, pkg = write_pull_package(
                body.get("prompt") or body.get("text") or "status pull",
                body.get("cwd") or str(WORK_DIR),
            )
            return self._json(200, {"ok": True, "path": str(path_md), "package": pkg})

        if path in ("/v1/license/accept", "/v1/license/accept/"):
            from pocket.license_gate import accept_response, LICENSE_ID

            if not body.get("accept") and body.get("license") not in (None, "", LICENSE_ID):
                # still allow explicit accept:true
                pass
            if body.get("accept") is False:
                return self._json(400, {"ok": False, "error": "accept must be true"})
            ip = self._client_ip()
            ua = self.headers.get("User-Agent") or self.headers.get("user-agent") or ""
            out = accept_response(ip=ip, user_agent=ua)
            # Set cookie on response
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            if out.get("cookie"):
                self.send_header("Set-Cookie", out["cookie"])
            body_b = json.dumps({k: v for k, v in out.items() if k != "cookie"}).encode("utf-8")
            self.send_header("Content-Length", str(len(body_b)))
            self._sec_headers()
            self.end_headers()
            self.wfile.write(body_b)
            return

        if path in ("/v1/wsl/run", "/v1/wsl/ensure"):
            from pocket.wsl_agent import ensure_workspace, run_wsl

            p = rbac_principal(self.headers)
            if not is_founder(p):
                return self._json(
                    403,
                    {
                        "ok": False,
                        "error": "WSL native agent is founder-host only on this machine",
                        "edition": "market",
                    },
                )
            if path.endswith("/ensure"):
                return self._json(200, ensure_workspace(body.get("distro") or ""))
            out, err, eng = run_wsl(
                body.get("prompt") or body.get("text") or body.get("cmd") or "status",
                distro=body.get("distro") or "",
                cwd=body.get("cwd") or "",
                job_id=body.get("job_id") or "",
            )
            return self._json(
                200,
                {"ok": not bool(err), "output": out, "error": err, "engine": eng},
            )

        if path in ("/v1/build-loops", "/v1/loops", "/v1/use-cases/run", "/v1/usecases/run"):
            from pocket.build_loop import manage_until_done, run_use_case, start_loop, stop_loop

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            owner = p.get("user") or "pocket"
            wait = bool(body.get("wait") or body.get("until_done"))
            timeout = float(body.get("timeout") or 120)
            if body.get("stop") and body.get("id"):
                return self._json(200, stop_loop(body.get("id"), reason=body.get("reason") or "api stop"))
            uc = body.get("use_case") or body.get("usecase") or body.get("id") or ""
            goal = body.get("goal") or body.get("prompt") or body.get("text") or ""
            if path.endswith("/run") or uc:
                started = run_use_case(uc or "fullstack_web_app", goal=goal, owner=owner)
            else:
                started = start_loop(
                    goal or "Ship a real app",
                    use_case=uc,
                    template=body.get("template") or "web_static",
                    loop_kind=body.get("loop") or body.get("loop_kind") or "ship",
                    owner=owner,
                    name=body.get("name") or "",
                    max_retries=int(body.get("max_retries") or 3),
                )
            if not started.get("ok"):
                return self._json(400, started)
            if wait:
                final = manage_until_done(started["id"], timeout_sec=timeout)
                return self._json(200, {"ok": bool(final.get("ok")), "started": started, "final": final})
            return self._json(200, started)

        if path in ("/v1/dual", "/v1/cortex", "/v1/subcortex"):
            from pocket.cortex_subcortex import start_dual

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            goal = body.get("goal") or body.get("prompt") or body.get("text") or ""
            return self._json(
                200,
                start_dual(
                    goal,
                    session_id=body.get("session_id") or "",
                    mode=body.get("mode") or "dialogue",
                    wait_subcortex_ms=int(body.get("wait_ms") or 120),
                ),
            )

        if path in ("/v1/dreams/now", "/v1/dream/now"):
            from pocket.dream_mode import dream_once

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(200, dream_once(force=True))
        if path in ("/v1/dreams/start", "/v1/dreams/stop"):
            from pocket.dream_mode import start as dream_start, stop as dream_stop

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if path.endswith("stop"):
                return self._json(200, dream_stop())
            return self._json(200, dream_start(interval_sec=body.get("interval_sec")))

        if path in ("/v1/duels", "/v1/duel"):
            from pocket.agent_duels import duel

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                duel(
                    body.get("challenge") or body.get("prompt") or body.get("text") or "",
                    contenders=body.get("contenders"),
                ),
            )

        if path in ("/v1/capsules", "/v1/time-capsules"):
            from pocket.time_capsules import cancel_capsule, create_capsule

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if body.get("cancel") or body.get("id") and body.get("action") == "cancel":
                return self._json(200, cancel_capsule(body.get("id") or body.get("cancel")))
            return self._json(
                200,
                create_capsule(
                    body.get("message") or body.get("text") or "",
                    after_sec=int(body.get("after_sec") or body.get("in") or 0),
                    at_ts=float(body.get("at_ts") or 0),
                    file_changed=body.get("file_changed") or body.get("path") or "",
                    idle_sec=int(body.get("idle_sec") or 0),
                    keyword=body.get("keyword") or "",
                    action=body.get("action") or "note",
                    owner=p.get("user") or "pocket",
                ),
            )

        if path in ("/v1/proofs/mint", "/v1/receipts/mint"):
            from pocket.proof_chain import mint_receipt

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                mint_receipt(
                    body.get("kind") or "manual",
                    body.get("summary") or body.get("text") or "manual receipt",
                    meta=body.get("meta") or {},
                ),
            )

        if path in ("/v1/swarm/start", "/v1/swarm/stop", "/v1/swarm/pulse", "/v1/swarm/config"):
            from pocket.always_on_swarm import configure, pulse_now, start as swarm_start, stop as swarm_stop

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if not is_founder(p) and path.endswith("/start"):
                return self._json(403, {"ok": False, "error": "swarm start is founder-host only"})
            if path.endswith("/stop"):
                return self._json(200, swarm_stop())
            if path.endswith("/pulse"):
                return self._json(200, pulse_now())
            if path.endswith("/config"):
                return self._json(200, configure(**{k: body[k] for k in body if k in (
                    "interval_sec", "max_parallel", "work_loops", "use_cases", "warm_dual", "world_model_tick"
                )}))
            return self._json(200, swarm_start(interval_sec=body.get("interval_sec")))

        # Damian fleet control (founder/operator internal)
        if path in (
            "/v1/damians/arm",
            "/v1/damians/pulse",
            "/v1/damians/stop",
            "/v1/damians/scale",
            "/v1/damian/arm",
            "/v1/damian/pulse",
        ):
            from pocket.damian_fleet import arm, pulse_now, scale, stop as damian_stop, status as damian_status

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if path.endswith("/stop"):
                return self._json(200, damian_stop())
            if path.endswith("/pulse"):
                return self._json(200, pulse_now(n=body.get("n")))
            if path.endswith("/scale"):
                n = int(body.get("count") or body.get("n") or 48)
                return self._json(200, scale(n))
            # arm
            return self._json(
                200,
                arm(
                    count=body.get("count") or body.get("n"),
                    force_rebuild=bool(body.get("rebuild")),
                ),
            )

        if path in (
            "/v1/work-studio/assist",
            "/v1/assistant",
            "/v1/assistant/chat",
            "/v1/digital-assistant/chat",
            "/v1/life/assist",
        ):
            from pocket.digital_assistant import run_assistant_turn

            b = body if isinstance(body, dict) else {}
            text = (b.get("text") or b.get("prompt") or b.get("message") or "").strip()
            return self._json(
                200,
                run_assistant_turn(
                    text,
                    engine=b.get("engine") or b.get("mode") or "auto",
                    session_id=b.get("session_id") or "",
                    job_id=b.get("job_id") or "",
                    voice=bool(b.get("voice") or b.get("voice_engine")),
                ),
            )
        if path in ("/v1/work-types", "/v1/work-types/"):
            from pocket.work_types import create_type

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                create_type(
                    name=body.get("name") or "Work",
                    description=body.get("description") or "",
                    engine=body.get("engine") or "plan",
                    layer=body.get("layer") or "cortex",
                    color=body.get("color") or "#10a37f",
                    icon=body.get("icon") or "●",
                    subcortex=body.get("subcortex"),
                ),
            )
        if path in ("/v1/work-loops", "/v1/work-loops/generate"):
            from pocket.work_types import create_loop, generate_from_goal

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if path.endswith("generate") or body.get("goal") or body.get("from_prompt"):
                return self._json(
                    200,
                    generate_from_goal(body.get("goal") or body.get("from_prompt") or body.get("prompt") or ""),
                )
            return self._json(
                200,
                create_loop(
                    name=body.get("name") or "Loop",
                    steps=body.get("steps"),
                    description=body.get("description") or "",
                    color=body.get("color") or "#10a37f",
                    max_retries=int(body.get("max_retries") or 3),
                    always_on_eligible=bool(body.get("always_on_eligible", True)),
                    from_prompt=body.get("from_prompt") or "",
                ),
            )
        if path in ("/v1/world-model/ingest", "/v1/world/ingest"):
            from pocket.world_model import ingest_fact

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                ingest_fact(
                    body.get("subject") or "",
                    body.get("predicate") or "",
                    body.get("object") or body.get("obj") or "",
                    source=body.get("source") or "user",
                ),
            )

        if path in (
            "/v1/wiki/profile",
            "/v1/wiki/get_file_profile",
            "/v1/wiki/lines",
            "/v1/wiki/read_file_lines",
            "/v1/wiki/symbol",
            "/v1/wiki/find_symbol",
            "/v1/wiki/goto",
            "/v1/wiki/definition",
            "/v1/wiki/search",
            "/v1/wiki/index",
            "/v1/wiki/reindex",
            "/v1/wiki/inject",
        ):
            from pocket.infinite_wiki import (
                find_symbol,
                get_file_profile,
                goto_definition,
                index_tree,
                inject_wiki_context,
                read_file_lines,
                reindex_if_stale,
                search_profiles,
            )

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if path.endswith("index"):
                return self._json(
                    200,
                    index_tree(
                        body.get("root") or body.get("path") or "",
                        label=body.get("label") or "",
                        max_files=int(body.get("max_files") or 2000),
                    ),
                )
            if path.endswith("reindex"):
                return self._json(200, reindex_if_stale(body.get("path") or ""))
            if path.endswith("inject"):
                return self._json(
                    200,
                    {
                        "ok": True,
                        "prompt": inject_wiki_context(
                            body.get("prompt") or body.get("text") or "",
                            cwd=body.get("cwd") or "",
                        ),
                    },
                )
            if "profile" in path or path.endswith("get_file_profile"):
                return self._json(
                    200,
                    get_file_profile(
                        body.get("path") or body.get("file") or "",
                        refresh=bool(body.get("refresh")),
                    ),
                )
            if "lines" in path or path.endswith("read_file_lines"):
                end_v = body.get("end") if body.get("end") is not None else body.get("e")
                return self._json(
                    200,
                    read_file_lines(
                        body.get("path") or body.get("file") or "",
                        start=int(body.get("start") or body.get("s") or 1),
                        end=int(end_v) if end_v is not None else None,
                        max_lines=int(body.get("max_lines") or 200),
                    ),
                )
            if path.endswith("goto") or path.endswith("definition"):
                return self._json(
                    200,
                    goto_definition(
                        body.get("name") or body.get("symbol") or body.get("q") or "",
                        from_path=body.get("from_path") or body.get("path") or "",
                    ),
                )
            if "symbol" in path:
                return self._json(
                    200,
                    find_symbol(body.get("name") or body.get("q") or "", root=body.get("root") or ""),
                )
            if path.endswith("search"):
                return self._json(200, search_profiles(body.get("q") or body.get("query") or ""))
            return self._json(404, {"error": "wiki route"})

        if path in ("/v1/bots", "/v1/bots/"):
            from pocket.bots import create_bot

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                create_bot(
                    name=body.get("name") or "Teammate",
                    job=body.get("job") or body.get("role") or "",
                    color=body.get("color") or "",
                    engine=body.get("engine") or "genetic",
                    always_on=bool(body.get("always_on")),
                    owner=p.get("user") or "pocket",
                    system=body.get("system") or "",
                ),
            )
        if path in ("/v1/bots/hire", "/v1/bots/from-prompt"):
            from pocket.bots import create_from_prompt

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                create_from_prompt(body.get("prompt") or body.get("text") or body.get("job") or "", owner=p.get("user") or "pocket"),
            )
        if path.startswith("/v1/bots/") and path.endswith("/message"):
            from pocket.bots import message as bot_message

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            bid = path.split("/v1/bots/", 1)[-1].split("/")[0]
            return self._json(
                200,
                bot_message(bid, body.get("text") or body.get("prompt") or body.get("message") or "", owner=p.get("user") or ""),
            )
        if path.startswith("/v1/bots/") and path.endswith("/pulse"):
            from pocket.bots import start_pulse, stop_pulse

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            bid = path.split("/v1/bots/", 1)[-1].split("/")[0]
            if body.get("on") is False or body.get("stop"):
                return self._json(200, stop_pulse(bid))
            return self._json(200, start_pulse(bid, interval_sec=int(body.get("interval_sec") or 180)))
        if path in ("/v1/custom-agents", "/v1/agents/custom"):
            from pocket.custom_agents import create_agent, run_custom_agent

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            if body.get("run") or body.get("prompt"):
                return self._json(
                    200,
                    run_custom_agent(
                        body.get("id") or body.get("agent") or "AGENT",
                        body.get("prompt") or body.get("text") or body.get("run") or "",
                        cwd=body.get("cwd") or "",
                    ),
                )
            return self._json(
                200,
                create_agent(
                    name=body.get("name") or body.get("id") or "CustomAgent",
                    role=body.get("role") or "",
                    personality=body.get("personality") or "",
                    tools=body.get("tools"),
                    sub_agents=body.get("sub_agents") or body.get("subagents"),
                    system=body.get("system") or "",
                    owner=p.get("user") or "pocket",
                ),
            )

        if path in ("/v1/novae/activate", "/v1/novae"):
            from pocket.novae import activate as novae_activate, list_novae

            if path == "/v1/novae" and self.command == "POST" and not (body.get("id") or body.get("novae")):
                return self._json(200, {"ok": True, "agents": list_novae()})
            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            nid = body.get("id") or body.get("novae") or body.get("name") or "GROK_NOVAE"
            out = novae_activate(
                nid,
                owner=p.get("user") or "pocket",
                edition="founder" if is_founder(p) else "market",
                goal=body.get("goal") or body.get("prompt") or "",
                host_power=bool(is_founder(p) and body.get("host_power", True)),
            )
            return self._json(200 if out.get("ok") else 400, out)
        if path == "/v1/novae/deactivate":
            from pocket.novae import deactivate as novae_deactivate

            p = rbac_principal(self.headers)
            if (p.get("role") or "none") == "none":
                return self._json(401, {"ok": False, "error": "auth required"})
            return self._json(
                200,
                novae_deactivate(body.get("id") or body.get("novae") or ""),
            )

        if path == "/v1/sessions":
            from pocket.device import device_from_request
            from pocket.platform_space import ensure_job_isolation, tenant_cwd
            from pocket.novae import _ws_root as novae_ws_root

            p = rbac_principal(self.headers)
            mode = body.get("mode") or "codex"
            ok, msg = allow_mode(p, mode)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            dev = device_from_request(self.headers, body)
            owner = p.get("user") or "pocket"
            ws = body.get("workspace") or "workspace"
            cwd = body.get("cwd") or ""
            # Novae modes always work in platform novae workspace (not founder home tree by default)
            if (mode or "").lower().replace("-", "_") in (
                "novae_grok",
                "novae_codex",
                "novae",
            ):
                nid = "GROK_NOVAE" if "codex" not in (mode or "").lower() else "CODEX_NOVAE"
                if (mode or "").lower().replace("-", "_") == "novae_codex":
                    nid = "CODEX_NOVAE"
                nroot = novae_ws_root(nid)
                ws = str(nroot)
                cwd = str(nroot / ("code" if nid == "CODEX_NOVAE" else "files"))
            if not is_founder(p):
                ws = f"tenant:{owner}"
                cwd = tenant_cwd(owner, "files")
            sess = create_session(
                mode=mode,
                title=body.get("title") or "",
                workspace=ws,
                cwd=cwd,
                client_device=dev,
                owner=owner,
            )
            sess["edition"] = "founder" if is_founder(p) else "market"
            sess["founder_files"] = bool(is_founder(p))
            return self._json(200, {"ok": True, **sess})

        if path.startswith("/v1/sessions/") and path.endswith("/rename"):
            sid = path.split("/v1/sessions/", 1)[-1].replace("/rename", "")
            sess = rename(sid, body.get("title") or "")
            if not sess:
                return self._json(404, {"error": "not found"})
            return self._json(200, sess)

        if path.startswith("/v1/sessions/") and (
            path.endswith("/voice-engine")
            or path.endswith("/voice_engine")
            or path.endswith("/voice")
        ):
            # get_session is module-level — NEVER re-import as get_session here.
            # Local "get as get_session" makes every other do_POST path (messages!)
            # crash with UnboundLocalError before this branch runs.
            from pocket.sessions import set_voice_engine

            sid = (
                path.split("/v1/sessions/", 1)[-1]
                .replace("/voice-engine", "")
                .replace("/voice_engine", "")
                .replace("/voice", "")
                .strip("/")
            )
            sess = get_session(sid)
            if not sess:
                return self._json(404, {"error": "session not found"})
            p = rbac_principal(self.headers)
            if not can_access_owned(p, sess.get("owner") or "pocket"):
                return self._json(403, {"ok": False, "error": "not your session"})
            b = body if isinstance(body, dict) else {}
            # enable=true by default; toggle if "toggle"
            if str(b.get("toggle") or "").lower() in ("1", "true", "yes"):
                enabled = not bool(sess.get("voice_engine"))
            elif "enabled" in b or "on" in b or "voice_engine" in b:
                enabled = bool(b.get("enabled") if "enabled" in b else b.get("on", b.get("voice_engine")))
            else:
                enabled = True
            updated = set_voice_engine(sid, enabled)
            return self._json(
                200,
                {
                    "ok": True,
                    "session": updated,
                    "voice_engine": bool((updated or {}).get("voice_engine")),
                    "mode": (updated or {}).get("mode"),
                    "message": (
                        "Voice engine ON — mic auto-sends and this agent speaks back"
                        if (updated or {}).get("voice_engine")
                        else "Voice engine OFF — mic is dictation only"
                    ),
                },
            )

        if path.startswith("/v1/sessions/") and path.endswith("/messages"):
            from pocket.device import agent_context_line, device_from_request, should_inject_context
            from pocket.sessions import save as save_sess

            sid = path.split("/v1/sessions/", 1)[-1].replace("/messages", "")
            sess = get_session(sid)
            if not sess:
                return self._json(404, {"error": "session not found"})
            p = rbac_principal(self.headers)
            if not can_access_owned(p, sess.get("owner") or "pocket"):
                return self._json(403, {"ok": False, "error": "not your session"})
            ok, msg = allow_mode(p, sess.get("mode") or "codex")
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            text = (body.get("text") or body.get("prompt") or "").strip()
            if not text:
                return self._json(400, {"error": "text required"})
            dev = device_from_request(self.headers, body)
            sess["client_device"] = dev
            save_sess(sess)
            msg = add_user_message(sid, text)
            if not msg:
                return self._json(500, {"error": "message failed"})

            # Interactive terminal: send to long-lived PTY-like shell
            if (sess.get("mode") or "") == "term":
                tid = sess.get("terminal_id")
                if not tid:
                    term = create_terminal(
                        kind=body.get("term_kind") or "powershell",
                        workspace=sess.get("workspace") or "workspace",
                        session_id=sid,
                    )
                    tid = term.get("id")
                    sess["terminal_id"] = tid
                    save_sess(sess)
                res = send_terminal(tid, text)
                complete_message(
                    sid,
                    msg["id"],
                    result=res.get("log_tail") or res.get("error") or "",
                    error="" if res.get("ok") else (res.get("error") or "term error"),
                    engine="term",
                    status="done" if res.get("ok") else "failed",
                )
                return self._json(
                    200,
                    {
                        "ok": True,
                        "session_id": sid,
                        "message": msg,
                        "terminal": res,
                        "client_device": dev,
                        "poll_session": f"/v1/sessions/{sid}",
                    },
                )

            mode = sess.get("mode") or "codex"
            # One tab = one active agent turn: stop prior Grok/Codex/etc. so the new
            # prompt takes the floor instead of leaving the first job running forever.
            superseded: list = []
            interrupt = body.get("interrupt")
            if interrupt is None:
                interrupt = True  # default: new message ends prior work on this session
            if interrupt and mode not in ("term",):
                try:
                    from pocket.jobs import cancel_session_jobs

                    superseded = cancel_session_jobs(
                        sid,
                        reason="superseded by new message — reorganize on latest prompt",
                    )
                except Exception:
                    superseded = []
            job_prompt = text
            if should_inject_context(mode):
                job_prompt = (agent_context_line(dev) + text)[:20000]
            # Infinite Wiki: auto Profile Cards for paths/symbols (context-window saver)
            if (mode or "").lower() in {
                "codex",
                "claude",
                "grok",
                "plan",
                "novae_grok",
                "novae_codex",
                "novae",
                "archon",
                "build",
                "wiki",
                "infinite_wiki",
                "codebase",
            }:
                try:
                    from pocket.infinite_wiki import inject_wiki_context

                    job_prompt = inject_wiki_context(
                        job_prompt,
                        cwd=body.get("cwd") or sess.get("cwd") or "",
                    )[:20000]
                except Exception:
                    pass
            from pocket.platform_space import ensure_job_isolation

            job = create_job(
                job_prompt,
                name=body.get("name") or "desk",
                mode=mode,
                workspace=body.get("workspace") or sess.get("workspace") or "workspace",
                cwd=body.get("cwd") or sess.get("cwd") or "",
                session_id=sid,
                message_id=msg["id"],
                client_device=dev,
                owner=sess.get("owner") or p.get("user") or "",
            )
            job = ensure_job_isolation(job, founder=is_founder(p))
            from pocket.jobs import save as save_job

            save_job(job)
            bind_job(sid, msg["id"], job["id"])
            # Kick dispatch immediately so the reply starts without waiting for the
            # 0.5s embedded-worker poll (this was the "typed but nothing happens" lag).
            try:
                threading.Thread(
                    target=process_one,
                    name="pocket-kick-job",
                    daemon=True,
                ).start()
            except Exception:
                pass
            return self._json(
                200,
                {
                    "ok": True,
                    "session_id": sid,
                    "message": msg,
                    "job": job,
                    "superseded_jobs": superseded,
                    "client_device": dev,
                    "poll_session": f"/v1/sessions/{sid}",
                },
            )

        if path in ("/v1/jobs", "/v1/code"):
            from pocket.platform_space import ensure_job_isolation
            from pocket.jobs import save as save_job

            p = rbac_principal(self.headers)
            mode = body.get("mode") or "codex"
            ok, msg = allow_mode(p, mode)
            if not ok:
                return self._json(403, {"ok": False, "error": msg})
            try:
                job = create_job(
                    body.get("prompt") or body.get("text") or "",
                    name=body.get("name") or "desk",
                    mode=mode,
                    cwd=body.get("cwd") or "",
                    workspace=body.get("workspace") or "",
                    owner=p.get("user") or "",
                )
            except ValueError as e:
                return self._json(400, {"error": str(e)})
            job = ensure_job_isolation(job, founder=is_founder(p))
            save_job(job)
            return self._json(200, {"ok": True, **job})

        # Stop a single job (Grok/Codex/etc.) — kills process tree when pid known
        if path.startswith("/v1/jobs/") and path.endswith("/cancel"):
            from pocket.jobs import cancel_job, get as get_job

            jid = path.split("/v1/jobs/", 1)[-1].replace("/cancel", "").strip("/")
            job = get_job(jid)
            if not job:
                return self._json(404, {"ok": False, "error": "job not found"})
            p = rbac_principal(self.headers)
            if job.get("owner") and not can_access_owned(p, job.get("owner") or ""):
                return self._json(403, {"ok": False, "error": "not your job"})
            out = cancel_job(jid, reason=(body.get("reason") or "cancelled by user"))
            return self._json(200, {"ok": True, "job": out})

        # Stop all work on a session tab without deleting the transcript
        if path.startswith("/v1/sessions/") and path.endswith("/stop"):
            from pocket.jobs import cancel_session_jobs

            sid = path.split("/v1/sessions/", 1)[-1].replace("/stop", "").strip("/")
            sess = get_session(sid)
            if not sess:
                return self._json(404, {"ok": False, "error": "session not found"})
            p = rbac_principal(self.headers)
            if not can_access_owned(p, sess.get("owner") or "pocket"):
                return self._json(403, {"ok": False, "error": "not your session"})
            cancelled = cancel_session_jobs(
                sid, reason=(body.get("reason") or "stopped by user")
            )
            try:
                from pocket.sessions import save as save_sess

                sess["status"] = "idle"
                save_sess(sess)
            except Exception:
                pass
            return self._json(
                200,
                {"ok": True, "session_id": sid, "cancelled_jobs": cancelled, "status": "idle"},
            )

        if path == "/v1/autonomy/schedules":
            from pocket.autonomy import create_schedule, ensure_runner

            prompt = (body.get("prompt") or body.get("text") or body.get("task") or "").strip()
            if not prompt:
                return self._json(400, {"error": "prompt required"})
            ensure_runner()
            rec = create_schedule(
                prompt=prompt,
                interval=body.get("interval") or "daily",
                title=body.get("title") or "",
                owner=(rbac_principal(self.headers).get("user") or "pocket"),
            )
            return self._json(200, {"ok": True, **rec})

        if path == "/v1/guppy/run":
            from pocket.guppy import run_guppy

            result, error, engine = run_guppy(
                body.get("prompt") or body.get("text") or "help",
                cwd=body.get("cwd") or "",
            )
            return self._json(
                200,
                {"ok": not bool(error), "result": result, "error": error, "engine": engine},
            )

        if path == "/v1/browser/run":
            from pocket.browser_mode import run_browser_job

            result, error, engine = run_browser_job(
                body.get("prompt") or body.get("text") or "help",
                cwd=body.get("cwd") or "",
                job={"browser_engine": body.get("engine") or body.get("browser_engine") or "auto"},
            )
            return self._json(
                200,
                {"ok": not bool(error), "result": result, "error": error, "engine": engine},
            )

        # Easy desk API — phone/desktop same shape as talking to an agent
        if path in ("/v1/desk", "/v1/desk/run", "/v1/archon"):
            from pocket.alpha_workers import run_alpha_job, run_worker, list_workers
            from pocket.worker_daemon import ensure_daemon, enqueue

            ensure_daemon()
            action = (body.get("action") or body.get("worker") or body.get("agent") or "").strip()
            prompt = (body.get("prompt") or body.get("text") or body.get("task") or "").strip()
            job_name = (body.get("job") or body.get("skill") or "orchestrate").strip()
            if body.get("async"):
                cmd = enqueue(action or "ARCHON", job_name if job_name != "orchestrate" else "grand_demo", prompt=prompt)
                return self._json(200, {"ok": True, "queued": cmd, "api": "desk-async"})
            if (body.get("list") or prompt.lower() in ("workers", "list", "help names")) and not action:
                return self._json(200, {"ok": True, "workers": list_workers()})
            if prompt.lower() in (
                "grand demo", "demo", "full demo", "interface demo", "ui demo",
                "focused demo",
            ) or job_name in ("grand_demo", "demo", "interface_demo", "focused_demo"):
                from pocket.skills_real import run_focused_demo

                r = run_focused_demo()
                return self._json(200, {"ok": r.get("ok"), "result": r, "engine": "archon", "api": "desk"})
            if action:
                result, error, engine = run_worker(
                    action,
                    job_name,
                    prompt=prompt,
                    params=body.get("params") or {},
                    cwd=body.get("cwd") or "",
                )
            else:
                result, error, engine = run_alpha_job(prompt or "help", cwd=body.get("cwd") or "")
            return self._json(
                200,
                {
                    "ok": not bool(error),
                    "result": result,
                    "error": error,
                    "engine": engine,
                    "api": "desk",
                    "hint": "POST {\"prompt\":\"interface demo\"} or {\"skill\":\"copilot_chat_send\",\"prompt\":\"…\"}",
                },
            )

        if path in ("/v1/live/vision", "/v1/vision"):
            from pocket.live_vision import latest_frame, ensure_vision

            ensure_vision()
            return self._json(200, latest_frame(include_image=True))
        if path in ("/v1/skills/run", "/v1/skill"):
            skill = body.get("skill") or body.get("id") or body.get("job") or ""
            prompt = body.get("prompt") or body.get("text") or ""
            params = body.get("params") or {}
            # Fast path: platform coherence skills skip vision tape / daemon warm
            try:
                from pocket.platform_coherence import is_platform_skill, run_platform_skill

                if is_platform_skill(skill):
                    r = run_platform_skill(skill, prompt=prompt, params=params)
                    return self._json(
                        200,
                        {
                            "ok": bool(r.get("ok", True)) if isinstance(r, dict) else True,
                            "result": r,
                            "engine": "platform",
                            "discover": "/v1/platform/coherent",
                        },
                    )
            except Exception as e:
                return self._json(200, {"ok": False, "error": str(e)[:300], "engine": "platform"})
            from pocket.orchestrator import get_orchestrator
            from pocket.worker_daemon import ensure_daemon

            ensure_daemon()
            r = get_orchestrator().execute(
                skill,
                prompt=prompt,
                params=params,
            )
            return self._json(200, {"ok": r.get("ok"), "result": r, "engine": "orchestrator"})

        # --- Recursive Agent Harnesses ---
        if path in ("/v1/rah/grant", "/v1/work-grant"):
            from pocket.rbac import principal as rbac_p
            from pocket.work_grant import issue as grant_issue

            who = rbac_p(self.headers)
            user = str(who.get("user") or "")
            if not user:
                return self._json(401, {"ok": False, "error": "sign in to issue a WorkGrant"})
            return self._json(
                200,
                grant_issue(
                    principal=user,
                    tenant=str(body.get("tenant") or user),
                    capability=str(body.get("capability") or "rah"),
                    budget=int(body.get("budget") or 6),
                    deadline_s=float(body.get("deadline_s") or 180),
                    tools=body.get("tools") if isinstance(body.get("tools"), list) else ["rah", "think", "verify", "memory"],
                    parent_run=str(body.get("parent_run") or body.get("job_id") or ""),
                    idempotency_key=str(body.get("idempotency_key") or "")[:80],
                ),
            )
        if path in ("/v1/rah/plan", "/v1/rah/preview", "/v1/rah/score"):
            from pocket.rah import plan_fanout, manifest as rah_manifest, score_rah_fit

            task = body.get("task") or body.get("prompt") or body.get("text") or ""
            fit = score_rah_fit(task, mode=str(body.get("mode") or ""))
            if path.endswith("/score"):
                return self._json(200, {"ok": True, "fit": fit, "protocol": rah_manifest().get("protocol")})
            return self._json(
                200,
                {
                    **plan_fanout(
                        task,
                        max_leaves=int(body.get("max_leaves") or fit.get("suggested_leaves") or 16),
                        hint=str(body.get("hint") or ""),
                    ),
                    "fit": fit,
                    "auto_would_run": bool(fit.get("use_rah")),
                    "protocol": rah_manifest().get("protocol"),
                },
            )
        # --- Genetic flow · internal model modules ---
        if path in (
            "/v1/genetic/run",
            "/v1/genetic/flow",
            "/v1/internal-models/run",
            "/v1/internal_models/run",
        ):
            from pocket.internal_models import run_genetic_flow

            task = body.get("goal") or body.get("task") or body.get("prompt") or body.get("text") or ""
            if not task:
                return self._json(400, {"ok": False, "error": "goal required"})
            models = body.get("models") or body.get("internal_models")
            if isinstance(models, str):
                models = [m.strip() for m in models.split(",") if m.strip()]
            run = run_genetic_flow(
                task,
                generations=int(body.get("generations") or body.get("gens") or 3),
                population=int(body.get("population") or body.get("pop") or 6),
                models=models,
                cwd=str(body.get("cwd") or ""),
                job=body if isinstance(body, dict) else None,
            )
            return self._json(
                200,
                {
                    "ok": run.get("ok"),
                    "run_id": run.get("run_id"),
                    "fitness": run.get("fitness"),
                    "elapsed_ms": run.get("elapsed_ms"),
                    "best": run.get("best"),
                    "history": run.get("history"),
                    "markdown": run.get("markdown"),
                    "path": run.get("path"),
                    "engine": "genetic-flow",
                    "poll": f"/v1/genetic/runs/{run.get('run_id')}",
                },
            )
        if path in (
            "/v1/internal-models/express",
            "/v1/internal_models/express",
            "/v1/genetic/express",
        ):
            from pocket.internal_models import express_one, list_models

            mid = str(body.get("model") or body.get("model_id") or body.get("id") or "").strip()
            goal = body.get("goal") or body.get("prompt") or body.get("text") or ""
            if not mid:
                return self._json(
                    400,
                    {"ok": False, "error": "model required", "models": [m["id"] for m in list_models()]},
                )
            res = express_one(mid, goal, job=body if isinstance(body, dict) else None)
            return self._json(200, res.as_dict() if hasattr(res, "as_dict") else res)

        if path in ("/v1/rah/run", "/v1/rah/execute", "/v1/recursive-harness/run"):
            from pocket.host_control import allow as host_ok
            from pocket.rah import run_rah, format_result_markdown
            from pocket.ratelimit import hit as rl_hit

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="rah")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ok_rl, reason = rl_hit("rah", self._client_ip(), kind="rah")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})

            task = body.get("task") or body.get("prompt") or body.get("text") or ""
            plan = body.get("plan") if isinstance(body.get("plan"), dict) else None
            if not task and not plan:
                return self._json(400, {"ok": False, "error": "task or plan required"})
            from pocket.rbac import principal as rbac_p
            from pocket.work_grant import issue as grant_issue, valid as grant_valid

            gid = str(body.get("grant_id") or "")
            if not grant_valid(gid, capability="rah").get("ok"):
                who = rbac_p(self.headers)
                user = str(who.get("user") or "")
                if not user:
                    return self._json(403, {"ok": False, "error": "RAH execute needs a WorkGrant or a signed-in seat"})
                g = grant_issue(
                    principal=user,
                    tenant=user,
                    capability="rah",
                    tools=["rah", "think", "verify", "memory"],
                    parent_run=str(body.get("job_id") or ""),
                    idempotency_key=str(body.get("idempotency_key") or "")[:80],
                )
                gid = str(g.get("id") or "")
            run = run_rah(
                task or (plan or {}).get("task") or "",
                plan=plan,
                max_leaves=int(body.get("max_leaves") or 12),
                max_parallel=body.get("max_parallel"),
                max_depth=body.get("max_depth") or 2,
                verify=body.get("verify", True) is not False,
                synthesize=body.get("synthesize", True) is not False,
                hint=str(body.get("hint") or ""),
                cwd=str(body.get("cwd") or ""),
                session_id=str(body.get("session_id") or body.get("session") or ""),
                parent_job_id=str(body.get("job_id") or ""),
                grant_id=gid,
            )
            # Economic: escrow + twin pulse for RAH
            try:
                from pocket.economy import escrow_open, twin_pulse, escrow_close

                esc = escrow_open(
                    amount=int(body.get("escrow") or 40),
                    purpose=f"rah:{run.get('run_id')}",
                    meta={"run_id": run.get("run_id")},
                )
                twin_pulse("rah", amount=8, reason="rah_orchestrate")
                if run.get("ok") and esc.get("ok"):
                    escrow_close(esc["escrow"]["id"], release_to="wallet_operator", slash=False)
                elif esc.get("ok"):
                    escrow_close(esc["escrow"]["id"], slash=True)
                run["economy"] = {"escrow": esc.get("escrow"), "receipt": (esc.get("receipt") or {}).get("hash")}
            except Exception:
                pass
            return self._json(
                200,
                {
                    "ok": run.get("ok"),
                    "run_id": run.get("run_id"),
                    "completed": run.get("completed"),
                    "failed": run.get("failed"),
                    "duration_sec": run.get("duration_sec"),
                    "artifact_root": run.get("artifact_root"),
                    "verify": run.get("verify"),
                    "synthesis": format_result_markdown(run)[:20000],
                    "cost_note": run.get("cost_note"),
                    "protocol": run.get("protocol"),
                    "economy": run.get("economy"),
                    "poll": f"/v1/rah/runs/{run.get('run_id')}",
                },
            )

        # RevenueCat — webhook is public (verified by REVENUECAT_WEBHOOK_AUTH)
        if path in ("/v1/billing/webhook", "/v1/billing/revenuecat", "/v1/revenuecat/webhook"):
            from pocket.revenuecat import handle_webhook

            authz = self.headers.get("Authorization") or self.headers.get("authorization") or ""
            result = handle_webhook(body if isinstance(body, dict) else {}, authorization=authz)
            code = int(result.pop("status", 200) or 200)
            if not result.get("ok") and code == 200:
                code = 400
            return self._json(code, result)
        if path in ("/v1/billing/sync", "/v1/revenuecat/sync"):
            from pocket.revenuecat import apply_subscriber

            uid = str(body.get("app_user_id") or body.get("user") or "").strip()
            if not uid:
                return self._json(400, {"ok": False, "error": "app_user_id required"})
            return self._json(200, apply_subscriber(uid, source="api"))
        # Economy mutations
        if path in ("/v1/economy/transfer", "/v1/wallet/transfer"):
            from pocket.economy import transfer

            return self._json(
                200,
                transfer(
                    from_id=str(body.get("from") or body.get("from_id") or "wallet_operator"),
                    to_id=str(body.get("to") or body.get("to_id") or ""),
                    amount=int(body.get("amount") or 0),
                    memo=str(body.get("memo") or ""),
                    rail=body.get("rail"),
                ),
            )
        if path in ("/v1/economy/mint", "/v1/wallet/mint"):
            from pocket.economy import mint_to_wallet

            return self._json(
                200,
                mint_to_wallet(
                    str(body.get("wallet") or body.get("wallet_id") or "wallet_operator"),
                    int(body.get("amount") or 0),
                    reason=str(body.get("reason") or "grant"),
                ),
            )
        if path in ("/v1/economy/twin", "/v1/economy/twin/ensure"):
            from pocket.economy import ensure_twin

            return self._json(
                200,
                ensure_twin(str(body.get("agent") or body.get("agent_id") or "agent"), label=str(body.get("label") or "")),
            )
        if path in ("/v1/economy/twin/pulse", "/v1/twin/pulse"):
            from pocket.economy import twin_pulse

            return self._json(
                200,
                twin_pulse(
                    str(body.get("agent") or body.get("agent_id") or "agent"),
                    amount=int(body.get("amount") or 5),
                    reason=str(body.get("reason") or "job"),
                ),
            )
        if path in ("/v1/economy/seat", "/v1/economy/seat/ensure"):
            from pocket.economy import ensure_seat_wallet

            p = rbac_principal(self.headers)
            user = str(body.get("user") or p.get("user") or "pocket")
            return self._json(200, ensure_seat_wallet(user))
        if path in ("/v1/economy/escrow", "/v1/economy/escrow/open"):
            from pocket.economy import escrow_open

            return self._json(
                200,
                escrow_open(
                    amount=int(body.get("amount") or 0),
                    purpose=str(body.get("purpose") or "multi-agent"),
                    holder=str(body.get("holder") or "wallet_operator"),
                    meta=body.get("meta") if isinstance(body.get("meta"), dict) else {},
                ),
            )
        if path in ("/v1/economy/escrow/close", "/v1/economy/escrow/release"):
            from pocket.economy import escrow_close

            return self._json(
                200,
                escrow_close(
                    str(body.get("id") or body.get("escrow_id") or ""),
                    release_to=str(body.get("to") or "wallet_operator"),
                    slash=bool(body.get("slash")),
                ),
            )
        if path in ("/v1/economy/rail", "/v1/economy/settlement"):
            from pocket.economy import set_rail

            return self._json(200, set_rail(str(body.get("rail") or body.get("settlement_rail") or "paper")))
        if path in ("/v1/economy/parallax", "/v1/parallax/bridge"):
            from pocket.economy import parallax_config, sync_parallax_bridge

            cfg = parallax_config(
                enabled=body.get("enabled") if "enabled" in body else None,
                workspace=body.get("workspace"),
                mode=body.get("mode"),
            )
            sync = {}
            if body.get("sync") or body.get("enabled"):
                try:
                    sync = sync_parallax_bridge(write_export=True)
                except Exception as e:
                    sync = {"ok": False, "error": str(e)[:200]}
            return self._json(200, {**cfg, "sync": sync})
        if path in ("/v1/economy/parallax/sync", "/v1/parallax/sync"):
            from pocket.economy import sync_parallax_bridge

            return self._json(200, sync_parallax_bridge(write_export=body.get("write", True) is not False))
        if path in ("/v1/economy/policy", "/v1/economy/evaluate"):
            from pocket.economy import evaluate_command

            return self._json(
                200,
                evaluate_command(
                    agent_id=str(body.get("agent") or body.get("agent_id") or "codex"),
                    kind=str(body.get("kind") or "transfer"),
                    amount=float(body.get("amount") or 0),
                    asset=str(body.get("asset") or "POCK"),
                    mode=body.get("mode") or body.get("rail"),
                ),
            )

        if path in ("/v1/orchestrator/chat", "/v1/chat/workflow", "/v1/desk/chat"):
            from pocket.orchestrator import get_orchestrator
            from pocket.worker_daemon import ensure_daemon

            ensure_daemon()
            text = body.get("prompt") or body.get("text") or body.get("message") or ""
            r = get_orchestrator().chat(text, record=bool(body.get("record")))
            return self._json(200, {"ok": r.get("ok"), "result": r, "engine": "orchestrator"})

        if path in ("/v1/orchestrator/plan", "/v1/plan/run"):
            from pocket.orchestrator import get_orchestrator

            steps = body.get("steps") or body.get("plan") or []
            r = get_orchestrator().execute_plan(steps, record=bool(body.get("record")))
            return self._json(200, {"ok": r.get("ok"), "result": r})

        if path in ("/v1/woa", "/v1/wrapped-orch", "/v1/orchestrator/woa"):
            from pocket.wrapped_orchestrator import run_wrapped

            text = body.get("prompt") or body.get("text") or body.get("goal") or body.get("message") or ""
            remote = body.get("remote")
            if remote is None:
                remote = True
            r = run_wrapped(
                text,
                remote=bool(remote),
                cwd=body.get("cwd") or "",
                job_id=body.get("job_id") or "",
            )
            return self._json(200, {"ok": r.get("ok"), "result": r, "engine": "wrapped-orch"})

        if path in ("/v1/ai-workspace/refresh", "/v1/ai_workspace/refresh"):
            from pocket.ai_workspace import get_workspace_view, refresh_index, touch_from_job

            ws = body.get("workspace") or "parallax"
            refresh_index(ws, body.get("cwd") or "")
            if body.get("job"):
                touch_from_job(body["job"])
            return self._json(
                200,
                get_workspace_view(ws, session_id=body.get("session_id") or body.get("session") or ""),
            )

        if path in ("/v1/agent-bus/send", "/v1/mesh/send"):
            from pocket.mesh_disk import send_message

            r = send_message(
                body.get("from") or body.get("from_agent") or "USER",
                body.get("to") or body.get("to_agent") or "ARCHON",
                body.get("body") or body.get("text") or body.get("message") or "",
                channel=body.get("channel") or "freq-coding",
                kind=body.get("kind") or "note",
                encrypt=body.get("encrypt", True),
            )
            return self._json(200, r)

        if path in ("/v1/git/create", "/v1/forge/create"):
            from pocket.sovereign_git import create_repo

            r = create_repo(
                body.get("name") or body.get("repo") or "project",
                description=body.get("description") or body.get("desc") or "",
                private=bool(body.get("private", True)),
                bare=bool(body.get("bare")),
            )
            return self._json(200, r)

        if path in ("/v1/record/start", "/v1/screen/start"):
            from pocket.screen_record import record_start

            return self._json(200, record_start(label=body.get("label") or "demo"))

        if path in ("/v1/record/stop", "/v1/screen/stop"):
            from pocket.screen_record import record_stop

            return self._json(200, record_stop())

        if path in ("/v1/cowork", "/v1/work"):
            from pocket.cowork import run_cowork

            r = run_cowork(
                body.get("prompt") or body.get("text") or body.get("goal") or "",
                record=body.get("record"),
                agent=body.get("agent") or "COWORK",
            )
            return self._json(200, {"ok": r.get("ok"), "result": r})

        if path in ("/v1/ghost", "/v1/ghost/math"):
            from pocket.ghost_math import run_ghost

            text, err, eng = run_ghost(body.get("prompt") or body.get("text") or "")
            return self._json(200, {"ok": not bool(err), "result": text, "error": err, "engine": eng})

        if path in ("/v1/auro/generate", "/v1/auro/meaning/generate"):
            from pocket.auro_meaning import generate_bytes_greedy, generate_ids

            if body.get("ids") is not None:
                ids = body.get("ids") or []
                r = generate_ids([int(x) for x in ids], max_new=int(body.get("max_new") or 16))
            else:
                r = generate_bytes_greedy(body.get("prompt") or body.get("text") or "abc", max_new=int(body.get("max_new") or 32))
            return self._json(200, r)

        if path in ("/v1/auro/train", "/v1/auro/meaning/train"):
            from pocket.auro_meaning import train_text_if_available

            r = train_text_if_available(
                body.get("corpus") or body.get("text") or body.get("prompt") or "",
                steps=int(body.get("steps") or 200),
            )
            return self._json(200, r)

        if path in ("/v1/offload", "/v1/offload/enqueue", "/v1/embody"):
            from pocket.offload_queue import enqueue, ensure_worker

            ensure_worker()
            goal = body.get("goal") or body.get("prompt") or body.get("text") or body.get("message") or ""
            r = enqueue(
                goal,
                steps=body.get("steps"),
                agent=body.get("agent") or body.get("from") or "USER",
                session_id=body.get("session_id") or "",
                workspace=body.get("workspace") or "parallax",
                priority=int(body.get("priority") or 5),
                kind=body.get("kind") or "embodiment",
            )
            return self._json(200, r)

        if path in ("/v1/embodiment/run", "/v1/embody/run"):
            from pocket.embodiment import run_embodiment_plan

            r = run_embodiment_plan(
                body.get("goal") or body.get("prompt") or body.get("text") or "capability snapshot",
                steps=body.get("steps"),
                agent=body.get("agent") or "USER",
                workspace=body.get("workspace") or "parallax",
            )
            return self._json(200, {"ok": r.get("ok"), "result": r})

        if path in ("/v1/task-market/post", "/v1/market/post"):
            from pocket.task_market import post_task

            r = post_task(
                body.get("title") or body.get("goal") or "untitled",
                body=body.get("body") or body.get("text") or "",
                from_agent=body.get("from") or body.get("agent") or "GROK",
                tags=body.get("tags"),
            )
            return self._json(200, r)

        if path in ("/v1/task-market/claim", "/v1/market/claim"):
            from pocket.task_market import claim

            r = claim(body.get("id") or body.get("task_id") or "", agent=body.get("agent") or "CODEX")
            return self._json(200, r)

        if path == "/v1/workers/create":
            from pocket.orchestrator import get_orchestrator

            r = get_orchestrator().create_worker(
                body.get("name") or "CUSTOM",
                body.get("skills") or ["screenshot", "scroll_read"],
                role=body.get("role") or "custom",
            )
            return self._json(200, r)

        if path in ("/v1/workers/spawn", "/v1/dynamic/spawn"):
            from pocket.dynamic_worker import spawn_worker

            r = spawn_worker(
                body.get("goal") or body.get("prompt") or body.get("text") or "explore screen",
                name=body.get("name") or "AUTON",
                max_steps=int(body.get("max_steps") or 10),
                async_=bool(body.get("async")),
            )
            return self._json(200, r)

        if path == "/v1/vision/click":
            from pocket.vision_core import click_by_name

            return self._json(200, click_by_name(body.get("name") or body.get("text") or ""))

        if path == "/v1/vision/observe":
            from pocket.vision_core import observe

            return self._json(
                200,
                observe(
                    with_ui_map=bool(body.get("ui_map", True)),
                    with_ocr=bool(body.get("ocr", True)),
                    with_understand=bool(body.get("understand", True)),
                    force=bool(body.get("force", False)),
                ),
            )
        if path in ("/v1/vision/understand", "/v1/pixel/understand", "/v1/pixel/translate"):
            from pocket.pixel_translator import understand

            return self._json(
                200,
                understand(
                    want_ocr=bool(body.get("ocr", True)),
                    want_semantic=bool(body.get("semantic", True)),
                    want_visual=bool(body.get("visual", True)),
                    include_image=bool(body.get("image", False)),
                ),
            )
        if path in ("/v1/pixel/text", "/v1/vision/ocr"):
            from pocket.pixel_translator import translate_to_text_only

            return self._json(200, translate_to_text_only())
        if path in ("/v1/vision/page", "/v1/page/render", "/v1/vision/full"):
            from pocket.page_renderer import render_full_page

            return self._json(
                200,
                render_full_page(
                    max_ui=int(body.get("max_ui") or 800),
                    include_ocr=bool(body.get("ocr", True)),
                    include_visual=bool(body.get("visual", True)),
                    include_image=bool(body.get("image", False)),
                    visual_grid=int(body.get("grid") or 5),
                ),
            )
        if path == "/v1/vision/stream/start":
            from pocket.page_renderer import stream_start

            return self._json(
                200,
                stream_start(
                    interval_sec=float(body.get("interval") or 1.5),
                    max_ui=int(body.get("max_ui") or 500),
                ),
            )
        if path == "/v1/vision/stream/stop":
            from pocket.page_renderer import stream_stop

            return self._json(200, stream_stop())
        if path == "/v1/vision/find":
            from pocket.page_renderer import find_symbols, render_full_page

            q = body.get("q") or body.get("query") or body.get("name") or ""
            if body.get("refresh"):
                render_full_page(max_ui=int(body.get("max_ui") or 600))
            return self._json(200, {"ok": True, "query": q, "hits": find_symbols(q)})

        if path == "/v1/long_workers/start":
            from pocket.long_workers import start_folder_watch, start_always_on_pulse, start_daily_research

            kind = (body.get("kind") or "always_on").lower()
            if kind == "folder_watch":
                return self._json(200, start_folder_watch())
            if kind == "daily_research":
                return self._json(200, start_daily_research(body.get("topic") or "AI agents"))
            return self._json(200, start_always_on_pulse(interval_sec=int(body.get("interval") or 120)))

        if path == "/v1/purchase/scaffold":
            from pocket.purchase_playbooks import run_playbook_scaffold

            return self._json(200, run_playbook_scaffold(body.get("id") or "generic_checkout_scaffold"))

        # Real-time synchronous bridge (outer agent drives each step after observe)
        if path == "/v1/bridge/open":
            from pocket.realtime_bridge import open_bridge

            return self._json(
                200,
                open_bridge(
                    title=body.get("title") or "live",
                    record=bool(body.get("record", True)),
                ),
            )
        if path.startswith("/v1/bridge/") and path.endswith("/observe"):
            from pocket.realtime_bridge import observe_bridge

            bid = path.split("/v1/bridge/", 1)[-1].replace("/observe", "").strip("/")
            return self._json(200, observe_bridge(bid))
        if path.startswith("/v1/bridge/") and path.endswith("/act"):
            from pocket.realtime_bridge import act_bridge

            bid = path.split("/v1/bridge/", 1)[-1].replace("/act", "").strip("/")
            action = body.get("action") or body.get("act") or ""
            kw = {k: v for k, v in body.items() if k not in ("action", "act")}
            return self._json(200, act_bridge(bid, action, **kw))
        if path.startswith("/v1/bridge/") and path.endswith("/close"):
            from pocket.realtime_bridge import close_bridge

            bid = path.split("/v1/bridge/", 1)[-1].replace("/close", "").strip("/")
            return self._json(200, close_bridge(bid))

        if path in ("/v1/campaigns", "/v1/campaigns/run"):
            from pocket.campaigns import run_research_campaign, list_campaigns

            if (body.get("list") or body.get("action") == "list") and not (
                body.get("topic") or body.get("prompt")
            ):
                return self._json(200, {"campaigns": list_campaigns()})
            topic = body.get("topic") or body.get("prompt") or body.get("text") or "POCKET host co-pilot"
            repos = body.get("repos")
            r = run_research_campaign(
                topic,
                repos=repos,
                record=bool(body.get("record", True)),
                commercial_polish=bool(body.get("commercial", True)),
            )
            return self._json(200, {"ok": True, "campaign": r, "api": "campaigns"})

        if path in ("/v1/studio/agent", "/v1/studio/skill"):
            from pocket.studio_core import run_studio_skill

            return self._json(
                200,
                run_studio_skill(
                    body.get("skill") or body.get("id") or "studio_status",
                    prompt=body.get("prompt") or body.get("text") or "",
                    params=body if isinstance(body, dict) else {},
                ),
            )
        if path in ("/v1/studio/storyboard",):
            from pocket.studio_core import storyboard

            return self._json(
                200,
                storyboard(
                    body.get("prompt") or body.get("text") or "",
                    product=body.get("product") or body.get("title") or "POCKET",
                ),
            )
        if path in ("/v1/studio/caption",):
            from pocket.studio_core import caption_pack

            return self._json(
                200,
                caption_pack(
                    body.get("prompt") or body.get("text") or "",
                    title=body.get("title") or "POCKET",
                    subtitle=body.get("subtitle") or "Host co-pilot",
                    cta=body.get("cta") or "ItsNotAI Labs",
                    brand=body.get("brand") or "ItsNotAI Labs",
                ),
            )
        if path in ("/v1/twin/mint", "/api/twin/mint"):
            from pocket.twin_mint import mint as twin_mint
            from pocket.rbac import principal as rbac_p

            p = rbac_p(self.headers)
            user = str(p.get("user") or "").strip()
            if not user:
                return self._json(401, {"ok": False, "error": "vault identity from signed-in seat only"})
            return self._json(200, twin_mint(user))
        if path in ("/v1/twin/open", "/api/twin/open"):
            from pocket.twin_mint import open_on_pc
            from pocket.rbac import principal as rbac_p

            p = rbac_p(self.headers)
            user = str(p.get("user") or "").strip()
            if not user:
                return self._json(401, {"ok": False, "error": "vault identity from signed-in seat only"})
            return self._json(200, open_on_pc(user))
        if path in ("/v1/twin/vault", "/api/twin/vault"):
            from pocket.twin_mint import vault_get, vault_put
            from pocket.rbac import principal as rbac_p

            p = rbac_p(self.headers)
            user = str(p.get("user") or "").strip()
            if not user:
                return self._json(401, {"ok": False, "error": "vault identity from signed-in seat only"})
            name = str(body.get("name") or body.get("path") or "note.md")
            if body.get("text") is not None or body.get("content") is not None:
                return self._json(
                    200,
                    vault_put(user, name, str(body.get("text") or body.get("content") or ""), to_pocket=body.get("to_pocket", True)),
                )
            return self._json(200, vault_get(user, name))
        if path in ("/v1/twin/agent", "/api/twin/agent"):
            from pocket.twin_mint import create_agent
            from pocket.rbac import principal as rbac_p

            p = rbac_p(self.headers)
            user = str(p.get("user") or "").strip()
            if not user:
                return self._json(401, {"ok": False, "error": "vault identity from signed-in seat only"})
            return self._json(200, create_agent(user, body if isinstance(body, dict) else {}))
        if path in ("/v1/twin/agent/run", "/api/twin/agent/run"):
            from pocket.twin_mint import run_agent as twin_run
            from pocket.rbac import principal as rbac_p

            p = rbac_p(self.headers)
            user = str(p.get("user") or "").strip()
            if not user:
                return self._json(401, {"ok": False, "error": "vault identity from signed-in seat only"})
            return self._json(
                200,
                twin_run(user, str(body.get("id") or body.get("agent") or ""), str(body.get("prompt") or body.get("text") or "")),
            )
        if path in ("/v1/network/agents",):
            from pocket.agent_network import develop as network_develop

            return self._json(200, network_develop(body if isinstance(body, dict) else {}))
        if path in ("/v1/network/agents/run",):
            from pocket.agent_network import run_developed

            return self._json(
                200,
                run_developed(str(body.get("id") or body.get("agent") or ""), str(body.get("prompt") or body.get("text") or "")),
            )
        if path in ("/v1/network/agents/ship",):
            from pocket.agent_network import ship as network_ship

            return self._json(
                200,
                network_ship(str(body.get("id") or body.get("agent") or ""), str(body.get("target") or "git")),
            )
        if path in ("/v1/studio/ship",):
            from pocket.studio_core import ship

            return self._json(
                200,
                ship(
                    source=body.get("source") or "",
                    title=body.get("title") or "POCKET",
                    subtitle=body.get("subtitle") or "Host co-pilot",
                    caption=body.get("caption") or "",
                    cta=body.get("cta") or "ItsNotAI Labs",
                    brand=body.get("brand") or "ItsNotAI Labs",
                    prompt=body.get("prompt") or body.get("text") or "",
                ),
            )
        if path == "/v1/studio/render":
            from pocket.video_studio import render

            r = render(
                body.get("source") or body.get("path") or "",
                preset=body.get("preset") or "rotato_phone",
                title=body.get("title") or "POCKET",
                subtitle=body.get("subtitle") or "Host co-pilot demo",
                caption=body.get("caption") or "",
                cta=body.get("cta") or "Try POCKET",
                brand=body.get("brand") or "ItsNotAI Labs",
                max_seconds=float(body.get("max_seconds") or 0),
                start_seconds=float(body.get("start_seconds") or 0),
                speed=float(body.get("speed") or 1.0),
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/imagine/compose", "/v1/imagine/render"):
            from pocket.imagine_studio import compose

            r = compose(
                mode=body.get("mode") or body.get("preset") or "rotato_phone",
                image=body.get("image") or body.get("path") or "",
                title=body.get("title") or "POCKET",
                subtitle=body.get("subtitle") or "Host co-pilot",
                width=int(body.get("width") or 0),
                height=int(body.get("height") or 0),
                image_b64=body.get("image_b64") or body.get("b64") or "",
                source=body.get("source") or "live",
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/fusion/remake", "/v1/vision/remake", "/v1/imagine/remake"):
            from pocket.fusion_remake import remake

            r = remake(
                refresh_page=bool(body.get("refresh", True)),
                max_ui=int(body.get("max_ui") or 500),
                styled=bool(body.get("styled", True)),
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in (
            "/v1/fusion/voice",
            "/v1/fusion/conversational",
            "/v1/conversational-fusion",
            "/v1/fusion/voice/fuse",
        ):
            from pocket.conversational_fusion import fuse, remember

            r = fuse(body if isinstance(body, dict) else {})
            sid = str((body or {}).get("session_id") or r.get("session_id") or "")
            if sid:
                remember(sid, r)
            return self._json(200 if r.get("ok") else 400, r)
        if path in (
            "/v1/remote-browser/open",
            "/v1/browser/remote/open",
            "/v1/remote_browser/open",
        ):
            from pocket.remote_browser import open_url

            return self._json(
                200,
                open_url(
                    (body or {}).get("url") or (body or {}).get("href") or "",
                    profile=(body or {}).get("profile") or "Default",
                ),
            )
        if path in (
            "/v1/remote-browser/sense",
            "/v1/browser/remote/sense",
            "/v1/remote_browser/sense",
        ):
            from pocket.remote_browser import sense

            return self._json(200, sense(max_ui=int((body or {}).get("max_ui") or 400)))
        if path in (
            "/v1/remote-browser/act",
            "/v1/browser/remote/act",
            "/v1/remote_browser/act",
        ):
            from pocket.remote_browser import act

            b = body if isinstance(body, dict) else {}
            return self._json(
                200,
                act(
                    b.get("action") or b.get("op") or "sense",
                    **{k: v for k, v in b.items() if k not in ("action", "op")},
                ),
            )
        if path in (
            "/v1/remote-browser/evidence",
            "/v1/browser/remote/evidence",
        ):
            from pocket.remote_browser import evidence_pack

            return self._json(200, evidence_pack((body or {}).get("url") or ""))
        if path in ("/v1/iot/devices", "/v1/home/devices"):
            from pocket.iot_home import register_device, remove_device, seed_home_defaults

            b = body if isinstance(body, dict) else {}
            if b.get("seed"):
                return self._json(200, seed_home_defaults())
            if b.get("remove") or b.get("delete"):
                return self._json(
                    200,
                    remove_device(device_id=b.get("id") or "", name=b.get("name") or ""),
                )
            return self._json(
                200,
                register_device(
                    name=b.get("name") or "",
                    kind=b.get("kind") or "generic",
                    address=b.get("address") or b.get("ip") or "",
                    room=b.get("room") or "",
                    protocol=b.get("protocol") or "lan",
                    meta=b.get("meta") if isinstance(b.get("meta"), dict) else {},
                ),
            )
        if path in ("/v1/iot/discover", "/v1/home/discover", "/v1/iot/scan"):
            from pocket.iot_home import discover_lan

            b = body if isinstance(body, dict) else {}
            return self._json(
                200,
                discover_lan(deep=bool(b.get("deep")), register=b.get("register", True) is not False),
            )
        if path in ("/v1/iot/control", "/v1/home/control", "/v1/iot/act"):
            from pocket.iot_home import control_device

            b = body if isinstance(body, dict) else {}
            return self._json(
                200,
                control_device(
                    device_id=b.get("id") or b.get("device_id") or "",
                    name=b.get("name") or "",
                    action=b.get("action") or b.get("cmd") or "toggle",
                ),
            )
        if path in ("/v1/iot/presence", "/v1/phone/presence", "/v1/iot/phone/presence"):
            from pocket.iot_home import phone_presence

            b = body if isinstance(body, dict) else {}
            # Client IP for same-WiFi registry
            try:
                cip = (self.client_address or ("",))[0]
            except Exception:
                cip = ""
            return self._json(
                200,
                phone_presence(
                    label=b.get("label") or b.get("name") or "POCKET Phone",
                    peer_id=b.get("peer_id") or "",
                    client_ip=b.get("ip") or b.get("address") or cip,
                    pair_token=b.get("pair_token")
                    or (self.headers.get("X-Pocket-Node-Token") or ""),
                ),
            )
        if path in ("/v1/voice/stt", "/v1/stt", "/v1/stt/transcribe"):
            from pocket.stt_engine import transcribe

            b = body if isinstance(body, dict) else {}
            return self._json(
                200,
                transcribe(
                    text=b.get("text") or b.get("transcript") or "",
                    lang=b.get("lang") or "en",
                    engine=b.get("engine") or "hybrid",
                    energy=b.get("energy"),
                    speech_active=b.get("speech_active"),
                    audio_path=b.get("audio_path") or b.get("path") or "",
                    session_id=b.get("session_id") or "",
                ),
            )
        if path in ("/v1/voice/flows", "/v1/voice/flows/advance"):
            # Proxy agentic flows to pocket-voice when up; else local fusion coach
            import json as _json
            import urllib.request

            b = body if isinstance(body, dict) else {}
            base = (os.environ.get("POCKET_VOICE_URL") or "http://127.0.0.1:8790").rstrip("/")
            try:
                raw = _json.dumps(b).encode("utf-8")
                req = urllib.request.Request(
                    base + "/v1/flows/advance",
                    data=raw,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = _json.loads(resp.read().decode("utf-8", errors="replace") or "{}")
                return self._json(200, data)
            except Exception as e:
                # Local fallback via fusion pattern
                from pocket.conversational_fusion import fuse

                text = b.get("text") or b.get("utterance") or ""
                f = fuse({"text": text, "stress": 0.4})
                return self._json(
                    200,
                    {
                        "ok": True,
                        "active": bool(f.get("pattern")),
                        "flow_id": f.get("pattern") or "local_fusion",
                        "expert": f.get("primary_expert"),
                        "coach": f.get("prompt_boost"),
                        "source": "pocket-fusion-fallback",
                        "error_voice_api": str(e)[:120],
                    },
                )
        if path in ("/v1/rfe/synthesize", "/v1/rfe/run", "/v1/fusion/synthesize"):
            from pocket.rfe_kernel import materialize

            r = materialize(
                instruction_set=body.get("instruction_set")
                or body.get("instruction")
                or body.get("mode")
                or "FULL_SYNTHESIS",
                refresh=bool(body.get("refresh", True)),
                max_ui=int(body.get("max_ui") or 500),
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path == "/v1/rfe/verify":
            from pocket.rfe_kernel import verify_packet

            pkt = body.get("fusion_packet") or body
            return self._json(200, {"ok": True, "valid": verify_packet({"fusion_packet": pkt} if "uuid" in pkt else body)})
        if path == "/v1/studio/batch":
            from pocket.video_studio import render_batch

            r = render_batch(
                body.get("source") or "",
                presets=body.get("presets"),
                title=body.get("title") or "POCKET",
                subtitle=body.get("subtitle") or "Host co-pilot",
                caption=body.get("caption") or "",
                cta=body.get("cta") or "ItsNotAI Labs",
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path == "/v1/studio/auto":
            from pocket.video_studio import auto_viral_pack

            r = auto_viral_pack(
                body.get("source") or "",
                title=body.get("title") or "POCKET",
                subtitle=body.get("subtitle") or "Real host co-pilot",
                caption=body.get("caption") or "Recorded live · Studio polish",
                cta=body.get("cta") or "ItsNotAI Labs",
            )
            return self._json(200 if r.get("ok") else 400, r)

        # --- Virtual computer (Caster-class) ---
        if path in ("/v1/screen", "/v1/screen-share", "/v1/share", "/v1/screen/share", "/v1/share/set"):
            from pocket.screen_share import set_share

            return self._json(
                200,
                set_share(
                    mode=body.get("mode") or "",
                    monitor=body.get("monitor") if body.get("monitor") is not None else None,
                    label=body.get("label") or "",
                    vcomp=body.get("vcomp") if "vcomp" in body else None,
                    agents=body.get("agents") if isinstance(body.get("agents"), list) else None,
                    target=body.get("target") or "",
                    window_title=body.get("window_title") or body.get("window") or "",
                    window_hwnd=body.get("window_hwnd") if body.get("window_hwnd") is not None else None,
                    reset_target=bool(body.get("reset_target") or body.get("desktop") or body.get("heal")),
                ),
            )
        if path in ("/v1/screen/sense", "/v1/share/sense", "/v1/screen/fusion"):
            from pocket.screen_share import fusion_context, set_share

            # Ensure share is on so sense returns real fusion (not "not shared")
            mode = body.get("mode") or ""
            if mode in ("view", "control") or body.get("ensure") is not False:
                try:
                    st_now = __import__("pocket.screen_share", fromlist=["status"]).status()
                    if not st_now.get("can_view"):
                        set_share(mode="view", reset_target=True)
                except Exception:
                    pass
            return self._json(
                200,
                fusion_context(agent=body.get("agent") or "desk", max_ui=int(body.get("max_ui") or 280)),
            )
        if path in ("/v1/screen/heal", "/v1/share/heal"):
            from pocket.screen_share import heal_share_target, status as screen_status

            h = heal_share_target(force_desktop=bool(body.get("force") or body.get("desktop") or True))
            return self._json(200, {"ok": True, **h, "status": screen_status()})
        if path in ("/v1/voice/tts", "/v1/tts"):
            from pocket.tts_engine import synthesize

            r = synthesize(
                body.get("text") or body.get("speech") or body.get("prompt") or "",
                voice=body.get("voice") or "",
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/voice/turn", "/v1/aria/turn"):
            from pocket.voice_product import run_voice_turn

            r = run_voice_turn(
                body.get("text") or body.get("prompt") or body.get("transcript") or "",
                session_id=str(body.get("session_id") or "api"),
                job_id=str(body.get("job_id") or ""),
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/mcp/invoke", "/v1/tools/invoke"):
            from pocket.mcp_bundle import invoke

            return self._json(
                200,
                invoke(
                    body.get("server") or "pocket",
                    body.get("tool") or "screen_status",
                    **(body.get("params") if isinstance(body.get("params"), dict) else {
                        k: v for k, v in body.items() if k not in ("server", "tool", "params")
                    }),
                ),
            )
        if path in ("/v1/mcp/stream/clear", "/v1/mcp/stream/reset"):
            from pocket.mcp_stream import clear as mcp_stream_clear

            return self._json(200, mcp_stream_clear())
        if path in ("/v1/cli/run", "/v1/tools/cli"):
            from pocket.cli_tools import run_cli

            args = body.get("args") or []
            if isinstance(args, str):
                args = args.split()
            return self._json(
                200,
                run_cli(
                    body.get("bin") or body.get("tool") or "",
                    args,
                    cwd=body.get("cwd") or "",
                    timeout=float(body.get("timeout") or 60),
                ),
            )
        if path in ("/v1/work/start", "/v1/work-mode/start"):
            from pocket.work_mode import start_work

            return self._json(
                200,
                start_work(
                    session_id=body.get("session_id") or "",
                    voice=body.get("voice", True) is not False,
                    screen=body.get("screen") or "control",
                    chrome=body.get("chrome", True) is not False,
                    goal=body.get("goal") or body.get("prompt") or "",
                ),
            )
        if path in ("/v1/work/package",):
            from pocket.work_mode import package_session

            return self._json(200, package_session(body.get("session_id") or body.get("id") or ""))
        if path in ("/v1/work/handoff",):
            from pocket.work_mode import handoff_artifacts

            return self._json(
                200,
                handoff_artifacts(
                    body.get("session_id") or body.get("id") or "",
                    kinds=body.get("kinds") if isinstance(body.get("kinds"), list) else None,
                ),
            )
        if path in ("/v1/work/turn",):
            from pocket.work_mode import run_work_turn

            return self._json(
                200,
                run_work_turn(
                    body.get("text") or body.get("prompt") or "",
                    session_id=body.get("session_id") or "",
                ),
            )
        if path in ("/v1/pocket-voice/ensure", "/v1/voice/ensure"):
            from pocket.voice_proxy import ensure_voice

            return self._json(200, ensure_voice(wait_sec=4.0))
        if path.startswith("/v1/pocket-voice/") and path not in ("/v1/pocket-voice/ensure",):
            from pocket.voice_proxy import proxy_request, ensure_voice

            sub = path[len("/v1/pocket-voice") :] or "/health"
            code, obj = proxy_request("POST", sub, body=body if isinstance(body, dict) else {})
            if code >= 500 or (isinstance(obj, dict) and not obj.get("ok") and "error" in (obj or {})):
                # Wake voice once and retry
                ensure_voice(wait_sec=2.0)
                code, obj = proxy_request("POST", sub, body=body if isinstance(body, dict) else {})
            return self._json(code if code < 600 else 502, obj)
        if path in ("/v1/working/board", "/v1/work/board", "/v1/board"):
            from pocket.working_board import (
                ingest_and_run,
                load_board,
                save_board,
                board_table,
                set_item_status,
            )

            text = (body.get("text") or body.get("prompt") or body.get("ask") or "").strip()
            # Row actions: done / dismiss / re-queue
            if body.get("item_id") and body.get("status"):
                return self._json(
                    200,
                    set_item_status(
                        str(body.get("item_id")),
                        status=str(body.get("status") or ""),
                        note=str(body.get("note") or ""),
                    ),
                )
            if body.get("clear"):
                b = load_board()
                b["items"] = []
                b["goal"] = ""
                b["last_activity"] = "cleared"
                save_board(b)
                return self._json(200, {"ok": True, "board": b, "table": board_table(b)})
            if text:
                return self._json(
                    200,
                    ingest_and_run(
                        text,
                        session_id=body.get("session_id") or "",
                        goal=body.get("goal") or "",
                        execute=body.get("execute", True) is not False,
                    ),
                )
            from pocket.working_board import status as board_status

            return self._json(200, board_status())
        if path in ("/v1/habitat", "/v1/habitat/open"):
            from pocket.agent_habitat import set_open, status as habitat_status

            if "open" in body:
                return self._json(200, set_open(bool(body.get("open"))))
            return self._json(200, habitat_status())
        if path in ("/v1/habitat/pulse", "/v1/habitat/assign"):
            from pocket.agent_habitat import pulse, assign

            if body.get("task") and path.endswith("assign"):
                return self._json(
                    200,
                    assign(body.get("agent") or body.get("id") or "", body.get("task") or ""),
                )
            return self._json(
                200,
                pulse(
                    body.get("agent") or body.get("id") or "",
                    status=body.get("status") or "working",
                    task=body.get("task") or "",
                    line=body.get("line") or body.get("message") or "",
                ),
            )
        if path in ("/v1/screen/act", "/v1/share/act"):
            from pocket.screen_share import act_for_agent

            return self._json(
                200,
                act_for_agent(
                    body.get("action") or body.get("act") or "sense",
                    agent=body.get("agent") or "desk",
                    **{k: v for k, v in body.items() if k not in ("action", "act", "agent")},
                ),
            )
        if path in ("/v1/vcomp/open", "/v1/computer/open"):
            from pocket.host_control import allow as host_ok
            from pocket.virtual_computer import open_computer

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="vcomp")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(200, open_computer(label=body.get("label") or "main"))
        if path in ("/v1/vcomp/close", "/v1/computer/close"):
            from pocket.virtual_computer import close_computer

            return self._json(200, close_computer())
        if path in ("/v1/vcomp/sense", "/v1/computer/sense"):
            from pocket.virtual_computer import sense_computer

            return self._json(200, sense_computer(max_ui=int(body.get("max_ui") or 500)))
        if path in ("/v1/screen/see", "/v1/vlaptop/see"):
            from pocket.host_control import allow as host_ok
            from pocket.screen_kernel import see as sk_see

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="observe")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(200, sk_see(which=str(body.get("which") or body.get("target") or "desktop")))
        if path in ("/v1/screen/touch", "/v1/vlaptop/touch"):
            from pocket.host_control import allow as host_ok
            from pocket.phoneai_portal import origin_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.screen_kernel import touch as sk_touch

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="portal")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            if not origin_ok(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "origin blocked"})
            ok_rl, reason = rl_hit("portal_touch", self._client_ip(), kind="portal_touch")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                sk_touch(
                    str(body.get("kind") or "tap"),
                    nx=float(body.get("nx") if body.get("nx") is not None else 0.5),
                    ny=float(body.get("ny") if body.get("ny") is not None else 0.5),
                    text=str(body.get("text") or ""),
                    dx=float(body.get("dx") or 0),
                    dy=float(body.get("dy") or 0),
                    target=str(body.get("target") or "desktop"),
                    hwnd=int(body.get("hwnd") or 0),
                    button=str(body.get("button") or "left"),
                ),
            )
        if path in ("/v1/screen/type", "/v1/vlaptop/type"):
            from pocket.host_control import allow as host_ok
            from pocket.phoneai_portal import origin_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.screen_kernel import type_into

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="portal")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            if not origin_ok(self.headers, getattr(self, "client_address", None)):
                return self._json(403, {"ok": False, "error": "origin blocked"})
            ok_rl, reason = rl_hit("portal_touch", self._client_ip(), kind="portal_touch")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                type_into(
                    str(body.get("text") or body.get("prompt") or ""),
                    nx=float(body.get("nx") if body.get("nx") is not None else 0.5),
                    ny=float(body.get("ny") if body.get("ny") is not None else 0.5),
                    target=str(body.get("target") or "desktop"),
                    click_first=body.get("click_first", True) is not False,
                    submit=bool(body.get("submit")),
                ),
            )
        if path in ("/v1/screen/click", "/v1/vlaptop/click"):
            from pocket.host_control import allow as host_ok
            from pocket.screen_kernel import click_name

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="portal")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(200, click_name(str(body.get("name") or body.get("text") or "")))
        if path in ("/v1/vcomp/act", "/v1/computer/act"):
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit
            from pocket.virtual_computer import act

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="vcomp")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ok_rl, reason = rl_hit("vcomp", self._client_ip(), kind="vcomp")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            action = body.get("action") or body.get("op") or "sense"
            params = {k: v for k, v in body.items() if k not in ("action", "op")}
            return self._json(200, act(action, **params))
        if path in ("/v1/vcomp/shell", "/v1/computer/shell"):
            from pocket.host_control import allow as host_ok
            from pocket.virtual_computer import shell

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="shell")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(
                200,
                shell(body.get("command") or body.get("cmd") or "", timeout=int(body.get("timeout") or 60)),
            )
        if path in ("/v1/vcomp/term", "/v1/computer/term"):
            from pocket.virtual_computer import open_terminal

            # send_terminal is module-level — do not re-import (shadows entire do_POST)
            if body.get("command") and body.get("id"):
                return self._json(200, send_terminal(body["id"], body["command"]))
            return self._json(200, open_terminal(kind=body.get("kind") or "powershell"))

        # --- Long missions ---
        if path in ("/v1/missions/start", "/v1/mission/start"):
            from pocket.mission_loop import start_mission

            return self._json(
                200,
                start_mission(
                    body.get("goal") or body.get("prompt") or "host work",
                    queue=body.get("queue") or body.get("steps"),
                    max_hours=float(body.get("max_hours") or 3.0),
                    step_pause_sec=float(body.get("pause") or 1.0),
                    name=body.get("name") or "MISSION",
                ),
            )
        if path in ("/v1/missions/enqueue", "/v1/mission/enqueue"):
            from pocket.mission_loop import enqueue

            return self._json(
                200,
                enqueue(body.get("id") or body.get("mission_id") or "", body.get("steps") or body.get("queue") or []),
            )
        if path in ("/v1/missions/stop", "/v1/mission/stop"):
            from pocket.mission_loop import stop_mission

            return self._json(200, stop_mission(body.get("id") or body.get("mission_id") or ""))

        # --- Alpha workflows ---
        if path in ("/v1/go", "/v1/go/start"):
            from pocket.go_plane import go as go_start

            return self._json(
                200,
                go_start(
                    arm_daily=body.get("arm_daily", True) is not False,
                    run_morning=bool(body.get("morning") or body.get("run_morning")),
                ),
            )
        if path in ("/v1/go/tick", "/v1/go/sync"):
            from pocket.go_plane import tick as go_tick

            return self._json(200, go_tick())
        if path in ("/v1/power/do", "/v1/power/run"):
            from pocket.power import do as power_do, morning

            if body.get("morning"):
                return self._json(200, morning())
            return self._json(
                200,
                power_do(
                    body.get("goal") or body.get("text") or body.get("prompt") or "",
                    dry=bool(body.get("dry")),
                    workflow_id=str(body.get("workflow_id") or body.get("id") or ""),
                ),
            )
        if path in ("/v1/workflows/multi/run", "/v1/multi-workflows/run"):
            from pocket.multi_workflows import run as run_multi

            return self._json(
                200,
                run_multi(
                    body.get("id") or body.get("workflow") or body.get("name") or "",
                    dry=bool(body.get("dry")),
                    params=body if isinstance(body, dict) else {},
                ),
            )
        if path in ("/v1/workflows/run", "/v1/workflow/run"):
            from pocket.workflows_alpha import run_workflow, run_all

            wid = body.get("id") or body.get("workflow") or ""
            if (body.get("all") or wid in ("all", "*")):
                return self._json(200, run_all())
            return self._json(200, run_workflow(wid, **{k: v for k, v in body.items() if k not in ("id", "workflow")}))
        if path in ("/v1/workflows/real", "/v1/workflows/real/run"):
            from pocket.workflows_real import run as run_real, run_all_real, catalog as real_catalog

            if body.get("all"):
                return self._json(200, run_all_real())
            wid = body.get("id") or body.get("workflow") or "real1"
            if body.get("list"):
                return self._json(200, {"workflows": real_catalog()})
            return self._json(200, run_real(wid, **{k: v for k, v in body.items() if k not in ("id", "workflow", "all", "list")}))
        if path in ("/v1/studio/product_phone", "/v1/studio/device_phone"):
            from pocket.device_remake import product_phone_from_recording, product_phone_from_image

            src = body.get("source") or body.get("path") or ""
            if src:
                r = product_phone_from_recording(
                    src,
                    title=body.get("title") or "POCKET",
                    caption=body.get("caption") or "Host co-pilot",
                    max_seconds=float(body.get("max_seconds") or 12),
                    n_frames=int(body.get("n_frames") or 10),
                )
            else:
                r = product_phone_from_image(
                    body.get("image"),
                    title=body.get("title") or "POCKET",
                    caption=body.get("caption") or "Host co-pilot",
                )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/studio/product_web", "/v1/studio/device_web"):
            from pocket.device_remake import product_web_from_image

            r = product_web_from_image(
                body.get("image") or body.get("path"),
                title=body.get("title") or "POCKET",
                brand=body.get("brand") or "pocket.local",
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/video/watch", "/v1/watch"):
            from pocket.video_watch import watch

            r = watch(
                body.get("source") or body.get("url") or body.get("path") or "",
                n_frames=int(body.get("n_frames") or 8),
                max_seconds=float(body.get("max_seconds") or 45),
                want_ocr=bool(body.get("ocr", True)),
            )
            return self._json(200 if r.get("ok") else 400, r)
        if path in ("/v1/nexus/run",):
            from pocket.nexus_bridge import run_worker

            r = run_worker(
                body.get("worker") or body.get("name") or "Bridge",
                body.get("tool") or body.get("action") or "list_servers",
                body.get("params") or body.get("args") or {},
            )
            return self._json(200 if r.get("ok", True) else 400, r)

        if path in ("/v1/workflows/start", "/v1/kernels/workflows/start"):
            from pocket.kernels.long_workflow import start as wf_start

            return self._json(
                200,
                wf_start(
                    str(body.get("goal") or body.get("prompt") or ""),
                    session_id=str(body.get("session_id") or ""),
                    interval_sec=float(body.get("interval_sec") or 90),
                    max_hours=float(body.get("max_hours") or 168),
                    keep=bool(body.get("keep")),
                    agents=body.get("agents"),
                    label=str(body.get("label") or ""),
                    host_bound=body.get("host_bound", True) is not False,
                ),
            )
        if path in ("/v1/workflows/tick",):
            from pocket.kernels.long_workflow import tick as wf_tick

            return self._json(200, wf_tick(str(body.get("id") or body.get("workflow_id") or "")))
        if path in ("/v1/workflows/pause",):
            from pocket.kernels.long_workflow import pause as wf_pause

            return self._json(200, wf_pause(str(body.get("id") or "")))
        if path in ("/v1/workflows/resume",):
            from pocket.kernels.long_workflow import resume as wf_resume

            return self._json(200, wf_resume(str(body.get("id") or "")))
        if path in ("/v1/workflows/stop",):
            from pocket.kernels.long_workflow import stop as wf_stop

            return self._json(200, wf_stop(str(body.get("id") or ""), reason=str(body.get("reason") or "stop")))
        if path in ("/v1/kernels/calibrate", "/v1/neuro-silicon/calibrate"):
            from pocket.kernels.neuro_silicon import calibrate

            return self._json(
                200,
                calibrate(
                    run_loop=bool(body.get("loop", True)),
                    goal=str(body.get("goal") or body.get("prompt") or ""),
                ),
            )
        if path in ("/v1/kernels/loop", "/v1/cognitive/loop"):
            from pocket.kernels.cognitive_loop import run_loop

            return self._json(
                200,
                run_loop(
                    str(body.get("goal") or body.get("prompt") or ""),
                    parallel=bool(body.get("parallel", True)),
                ),
            )
        if path in ("/v1/agents/turn", "/v1/agent/turn"):
            from pocket.agent_arch import turn as arch_turn
            from pocket.host_control import allow as host_ok

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="harness")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            return self._json(
                200,
                arch_turn(
                    str(body.get("text") or body.get("goal") or body.get("prompt") or body.get("message") or ""),
                    agent=str(body.get("agent") or body.get("name") or body.get("persona") or ""),
                    seat=str(body.get("seat") or "pocket"),
                    engine=str(body.get("engine") or "auto"),
                    grant_id=str(body.get("grant_id") or body.get("grant") or ""),
                    shell=str(body.get("shell") or body.get("command") or ""),
                    cwd=str(body.get("cwd") or ""),
                    use=str(body.get("use") or "auto"),
                    dry=bool(body.get("dry")),
                ),
            )
        if path in ("/v1/agents/invoke", "/v1/agent/invoke", "/v1/beings/invoke"):
            from pocket.agent_invoke import invoke
            from pocket.host_control import allow as host_ok
            from pocket.ratelimit import hit as rl_hit

            gate = host_ok(headers=self.headers, client_address=getattr(self, "client_address", None), consequence="invoke")
            if not gate.get("ok"):
                return self._json(403, {"ok": False, "error": gate.get("error")})
            ok_rl, reason = rl_hit("invoke", self._client_ip(), kind="invoke")
            if not ok_rl:
                return self._json(429, {"ok": False, "error": reason})
            return self._json(
                200,
                invoke(
                    str(body.get("name") or body.get("agent") or body.get("id") or ""),
                    prompt=str(body.get("prompt") or body.get("message") or body.get("text") or ""),
                    job=str(body.get("job") or body.get("action") or ""),
                    session_id=str(body.get("session_id") or ""),
                    params=body if isinstance(body, dict) else {},
                ),
            )
        if path in ("/v1/agents/autonomous/ensure", "/v1/autonomous/ensure"):
            from pocket.agent_invoke import ensure_autonomous

            return self._json(200, ensure_autonomous())
        if path in ("/v1/subagents/dispatch", "/v1/agents/dispatch"):
            from pocket.agent_hook import ensure_mesh_hook
            from pocket.subagent_dispatch import dispatch

            ensure_mesh_hook()

            msg = body.get("message") or body.get("text") or body.get("prompt") or ""
            agents = body.get("agents") or body.get("names")
            if body.get("name") and not agents:
                agents = [body.get("name")]
            return self._json(
                200,
                dispatch(
                    msg,
                    from_agent=body.get("from") or "USER",
                    agents=agents,
                    channel=body.get("channel") or "freq-0",
                ),
            )
        if path in ("/v1/subagents/steer", "/v1/agents/steer"):
            from pocket.subagent_dispatch import steer

            return self._json(
                200,
                steer(
                    str(body.get("instruction") or body.get("text") or body.get("prompt") or ""),
                    run_id=str(body.get("run_id") or body.get("id") or ""),
                    agent=str(body.get("agent") or body.get("name") or ""),
                ),
            )
        if path in ("/v1/agents/dm", "/v1/agents/message"):
            from pocket.agent_social import dm

            return self._json(
                200,
                dm(
                    str(body.get("from") or body.get("from_agent") or "system"),
                    str(body.get("to") or body.get("agent") or ""),
                    str(body.get("text") or body.get("body") or body.get("message") or ""),
                    also_email=bool(body.get("email") or body.get("also_email")),
                ),
            )
        if path in ("/v1/agents/email", "/v1/agents/mail"):
            from pocket.agent_social import email_agents

            return self._json(
                200,
                email_agents(
                    str(body.get("from") or body.get("from_agent") or "system"),
                    str(body.get("to") or ""),
                    subject=str(body.get("subject") or ""),
                    body=str(body.get("body") or body.get("text") or ""),
                ),
            )
        if path in ("/v1/agents/groups",):
            from pocket.agent_social import create_group

            return self._json(
                200,
                create_group(
                    str(body.get("name") or "group"),
                    members=list(body.get("members") or []),
                    owner=str(body.get("owner") or "system"),
                ),
            )
        if path in ("/v1/agents/groups/post", "/v1/agents/group"):
            from pocket.agent_social import group_post

            return self._json(
                200,
                group_post(
                    str(body.get("group") or body.get("id") or ""),
                    str(body.get("from") or body.get("from_agent") or "system"),
                    str(body.get("text") or body.get("body") or ""),
                ),
            )
        if path in ("/v1/agents/name", "/v1/agents/rename"):
            from pocket.agent_social import name_agent

            return self._json(
                200,
                name_agent(
                    str(body.get("id") or body.get("agent") or ""),
                    str(body.get("name") or ""),
                    blurb=str(body.get("blurb") or ""),
                ),
            )
        if path in ("/v1/browser/drive", "/v1/agents/browser", "/v1/web_ui/drive"):
            from pocket.web_ui_engine import drive as browser_drive

            return self._json(
                200,
                browser_drive(
                    str(body.get("url") or ""),
                    goal=str(body.get("goal") or body.get("prompt") or body.get("text") or ""),
                    steps=body.get("steps") if isinstance(body.get("steps"), list) else None,
                    profile=str(body.get("profile") or "Default"),
                ),
            )
        if path in ("/v1/mesh/send",):
            from pocket.mesh_disk import send_message

            return self._json(
                200,
                send_message(
                    body.get("from") or "USER",
                    body.get("to") or "ARCHON",
                    body.get("body") or body.get("message") or "",
                    channel=body.get("channel") or "freq-0",
                    kind=body.get("kind") or "note",
                ),
            )
        if path in ("/v1/mesh/bootstrap", "/v1/headless/start", "/v1/hooks/mesh"):
            from pocket.agent_hook import ensure_mesh_hook

            h = ensure_mesh_hook(force=True, interval_sec=float(body.get("interval") or 120))
            return self._json(200, {"ok": True, "hook": h, "protocol": "MEDINA-SUBAGENT-MESH/1.0"})
        if path == "/v1/headless/stop":
            from pocket.subagent_dispatch import stop_headless_pack

            return self._json(200, stop_headless_pack())

        # --- Node-to-node pair + transfer ---
        if path in ("/v1/node/pair", "/v1/node/mint"):
            from pocket.node_transfer import mint_pair_code

            return self._json(
                200,
                mint_pair_code(label=body.get("label") or "", ttl_sec=int(body.get("ttl_sec") or 900)),
            )
        if path in ("/v1/node/pair-login", "/v1/node/seat", "/v1/node/pair_login"):
            from pocket.node_transfer import pair_seat_login

            pt = (
                body.get("pair_token")
                or body.get("token")
                or self.headers.get("X-Pocket-Node-Token")
                or self.headers.get("x-pocket-node-token")
                or ""
            )
            r = pair_seat_login(pt)
            code = 200 if r.get("ok") else 401
            return self._json(code, r)
        if path in ("/v1/node/redeem",):
            from pocket.node_transfer import redeem_pair_code

            return self._json(
                200,
                redeem_pair_code(
                    body.get("code") or "",
                    peer_label=body.get("label") or body.get("peer_label") or "",
                    peer_node_id=body.get("peer_id") or body.get("node_id") or "",
                ),
            )
        if path in ("/v1/node/offer", "/v1/node/push"):
            from pocket.node_transfer import offer_file, verify_pair_token
            import base64 as _b64

            nt = (self.headers.get("X-Pocket-Node-Token") or self.headers.get("x-pocket-node-token") or "").strip()
            peer = verify_pair_token(nt) if nt else None
            if not peer and not is_authorized(self.headers):
                return self._json(401, {"ok": False, "error": "auth or pair token required"})
            name = body.get("name") or body.get("filename") or "file.bin"
            if body.get("path"):
                from pocket.node_transfer import drop_local_copy

                return self._json(200, drop_local_copy(body.get("path"), agent_id=body.get("from") or "USER"))
            b64 = body.get("data_b64") or body.get("content_b64") or ""
            text = body.get("text") or body.get("content")
            try:
                raw = _b64.b64decode(b64) if b64 else (text or "").encode("utf-8")
            except Exception:
                return self._json(400, {"ok": False, "error": "invalid data_b64"})
            return self._json(
                200,
                offer_file(
                    name=name,
                    data=raw,
                    to_peer=body.get("to_peer") or body.get("peer_id") or "",
                    from_user=body.get("from") or (peer or {}).get("peer_id") or "owner",
                    note=body.get("note") or "",
                ),
            )
        if path in ("/v1/node/claim", "/v1/node/pull"):
            from pocket.node_transfer import claim_offer, verify_pair_token

            nt = (self.headers.get("X-Pocket-Node-Token") or self.headers.get("x-pocket-node-token") or "").strip()
            peer = verify_pair_token(nt) if nt else None
            if not peer and not is_authorized(self.headers):
                return self._json(401, {"ok": False, "error": "auth or pair token required"})
            oid = body.get("offer_id") or body.get("id") or ""
            return self._json(
                200,
                claim_offer(oid, peer=peer, as_user=(peer or {}).get("peer_id") or "session"),
            )

        # --- Pixel lattice virtual memory ---
        if path in ("/v1/vmem/put", "/v1/pixel-memory/put", "/v1/vmem/store"):
            from pocket.pixel_vmem import put_bytes, put_text, put_json
            import base64 as _b64

            sym = body.get("symbol") or body.get("name") or ""
            common = dict(
                symbol=sym,
                workspace=body.get("workspace") or "default",
                tags=body.get("tags") or [],
                note=body.get("note") or "",
                replicate_mesh=bool(body.get("mesh", True)),
                pass_to=body.get("pass_to") or body.get("pass") or "",
            )
            if body.get("json") is not None:
                return self._json(200, put_json(body.get("json"), **common))
            if body.get("text") is not None or body.get("content") is not None:
                return self._json(
                    200,
                    put_text(
                        body.get("text") if body.get("text") is not None else body.get("content") or "",
                        kind=body.get("kind") or "text",
                        **common,
                    ),
                )
            b64 = body.get("data_b64") or body.get("content_b64") or ""
            try:
                raw = _b64.b64decode(b64) if b64 else b""
            except Exception:
                return self._json(400, {"ok": False, "error": "invalid data_b64"})
            return self._json(
                200,
                put_bytes(raw, kind=body.get("kind") or "", **common),
            )
        if path in ("/v1/vmem/get", "/v1/vmem/look"):
            from pocket.pixel_vmem import get_page, get_symbol, look

            if body.get("q") or body.get("query"):
                from pocket.pixel_vmem import search

                return self._json(200, search(body.get("q") or body.get("query") or ""))
            if body.get("symbol") and not body.get("page_id"):
                if body.get("full") is False:
                    return self._json(200, look(symbol=body.get("symbol")))
                return self._json(200, get_symbol(body.get("symbol")))
            if body.get("page_id") or body.get("page"):
                return self._json(200, get_page(body.get("page_id") or body.get("page") or ""))
            return self._json(200, look(symbol=body.get("symbol") or "", q=body.get("q") or ""))
        if path in ("/v1/vmem/search",):
            from pocket.pixel_vmem import search

            return self._json(200, search(body.get("q") or body.get("query") or body.get("text") or ""))
        if path in ("/v1/vmem/recreate", "/v1/vmem/export"):
            from pocket.pixel_vmem import recreate

            return self._json(
                200,
                recreate(
                    body.get("symbol") or "",
                    page_id=body.get("page_id") or body.get("page") or "",
                    export=bool(body.get("export", True)),
                    filename=body.get("filename") or body.get("name") or "",
                ),
            )
        if path in ("/v1/vmem/pass", "/v1/vmem/handoff"):
            from pocket.pixel_vmem import pass_info

            return self._json(
                200,
                pass_info(
                    body.get("symbol") or "",
                    to=body.get("to") or body.get("target") or "context",
                    agent=body.get("agent") or "ARCHON",
                    peer=body.get("peer") or body.get("to_peer") or "",
                    workspace=body.get("workspace") or "",
                ),
            )
        if path in ("/v1/vmem/share", "/v1/vmem/node-share"):
            from pocket.pixel_vmem import share_page_to_node, pass_info

            if body.get("symbol"):
                return self._json(
                    200,
                    pass_info(body.get("symbol"), to="device", peer=body.get("to_peer") or ""),
                )
            return self._json(
                200,
                share_page_to_node(body.get("page_id") or body.get("page") or "", to_peer=body.get("to_peer") or ""),
            )
        if path in ("/v1/vmem/delete",):
            from pocket.pixel_vmem import delete_symbol

            return self._json(200, delete_symbol(body.get("symbol") or ""))
        if path in ("/v1/vmem/artifact", "/v1/vmem/put-artifact"):
            from pocket.pixel_vmem import put_artifact

            return self._json(
                200,
                put_artifact(
                    body.get("content") or body.get("text") or body.get("code") or "",
                    title=body.get("title") or body.get("name") or "",
                    language=body.get("language") or body.get("lang") or "text",
                    agent=body.get("agent") or "",
                    agent_role=body.get("role") or body.get("agent_role") or "",
                    ai_version=body.get("ai_version") or body.get("engine") or "",
                    run_id=body.get("run_id") or body.get("run") or "",
                    tags=body.get("tags") or [],
                    workspace=body.get("workspace") or "artifacts",
                    note=body.get("note") or "",
                ),
            )
        if path in ("/v1/vmem/bring-back", "/v1/swarm/bring-back"):
            from pocket.coding_swarm import bring_back

            return self._json(200, bring_back(body.get("symbol") or body.get("id") or ""))
        if path in ("/v1/os/projects",) and self.command == "POST":
            from pocket.agent_os import create_project

            return self._json(
                200,
                create_project(
                    body.get("name") or body.get("id") or "",
                    template=body.get("template") or "typescript",
                    title=body.get("title") or "",
                    seed=body.get("seed") or body.get("code") or "",
                ),
            )
        if path in ("/v1/os/run",):
            from pocket.agent_os import run_project

            return self._json(
                200,
                run_project(
                    body.get("project_id") or body.get("id") or "",
                    entry=body.get("entry") or "",
                    timeout=float(body.get("timeout") or 20),
                ),
            )
        if path in ("/v1/os/run-artifact",):
            from pocket.agent_os import run_artifact_symbol

            return self._json(
                200,
                run_artifact_symbol(body.get("symbol") or "", timeout=float(body.get("timeout") or 20)),
            )
        if path in ("/v1/os/import-artifact",):
            from pocket.agent_os import import_artifact_to_project

            return self._json(
                200,
                import_artifact_to_project(
                    body.get("symbol") or "",
                    project_id=body.get("project_id") or "",
                    filename=body.get("filename") or "",
                ),
            )
        if path in ("/v1/os/write",):
            from pocket.agent_os import write_project_file

            return self._json(
                200,
                write_project_file(
                    body.get("project_id") or body.get("id") or "",
                    body.get("filename") or body.get("file") or "file.txt",
                    body.get("content") or body.get("text") or "",
                ),
            )

        # --- PROTO-CAPSULE-WASM-009 Multi-Sandbox Capsule + WebGPU ---
        if path in ("/v1/capsule/allocate", "/v1/capsules/allocate"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            return self._json(200, capsule_manager().allocate(body if isinstance(body, dict) else {}))
        if path in ("/v1/capsule/execute", "/v1/capsules/execute"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            return self._json(
                200,
                capsule_manager().execute(
                    body.get("id") or body.get("capsule_id") or body.get("capsule") or "",
                    body.get("command") or body.get("cmd") or body.get("prompt") or "",
                    timeout_sec=float(body["timeout_sec"]) if body.get("timeout_sec") is not None else None,
                ),
            )
        if path in ("/v1/capsule/commit", "/v1/capsules/commit"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            return self._json(
                200,
                capsule_manager().commit(body.get("id") or body.get("capsule_id") or body.get("capsule") or ""),
            )
        if path in ("/v1/capsule/terminate", "/v1/capsules/terminate"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            return self._json(
                200,
                capsule_manager().terminate(body.get("id") or body.get("capsule_id") or body.get("capsule") or ""),
            )
        if path in ("/v1/capsule/mount", "/v1/capsules/mount"):
            from pocket.protocols.multi_sandbox_capsule import manager as capsule_manager

            cap = capsule_manager().get(body.get("id") or body.get("capsule_id") or "")
            if not cap:
                return self._json(404, {"ok": False, "error": "capsule not found"})
            return self._json(
                200,
                cap.mount(body.get("repo") or body.get("path") or body.get("repoSource") or body.get("source") or ""),
            )

        # --- Agent capability sandbox (Wasm-shaped grants) ---
        if path in ("/v1/sandbox/grant", "/v1/agent-sandbox/grant"):
            from pocket.agent_sandbox import mint_grant

            g = mint_grant(
                body.get("profile") or "compute",
                workspace_path=body.get("workspace_path") or body.get("workspace") or "",
                tenant_path=body.get("tenant_path") or "",
                agent_id=body.get("agent_id") or body.get("agent") or "",
                session_id=body.get("session_id") or body.get("session") or "",
                extra_caps=body.get("extra_caps") or body.get("caps") or [],
                net_hosts=body.get("net_hosts"),
            )
            return self._json(
                200,
                {
                    "ok": True,
                    "grant": {
                        "profile": g.profile,
                        "caps": sorted(g.caps),
                        "fs_roots": g.fs_roots,
                        "net_hosts": g.net_hosts,
                        "max_ms": g.max_ms,
                        "max_memory_mb": g.max_memory_mb,
                        "fuel": g.fuel,
                        "agent_id": g.agent_id,
                        "session_id": g.session_id,
                    },
                },
            )
        if path in ("/v1/sandbox/check",):
            from pocket.agent_sandbox import mint_grant, check

            g = mint_grant(
                body.get("profile") or "compute",
                workspace_path=body.get("workspace_path") or "",
                tenant_path=body.get("tenant_path") or "",
                agent_id=body.get("agent_id") or "",
                session_id=body.get("session_id") or "",
                extra_caps=body.get("extra_caps") or [],
                net_hosts=body.get("net_hosts"),
            )
            ok, trap = check(
                g,
                body.get("action") or "compute",
                path=body.get("path") or "",
                host=body.get("host") or "",
                fuel_cost=int(body.get("fuel_cost") or 1),
            )
            return self._json(200, {"ok": ok, "trap": trap or None, "profile": g.profile, "caps": sorted(g.caps)})
        if path in ("/v1/sandbox/read",):
            from pocket.agent_sandbox import mint_grant, safe_read_text

            g = mint_grant(
                body.get("profile") or "workspace_read",
                workspace_path=body.get("workspace_path") or body.get("root") or "",
                tenant_path=body.get("tenant_path") or "",
                agent_id=body.get("agent_id") or "",
                session_id=body.get("session_id") or "",
            )
            return self._json(200, safe_read_text(g, body.get("path") or "", max_bytes=int(body.get("max_bytes") or 200_000)))
        if path in ("/v1/sandbox/write",):
            from pocket.agent_sandbox import mint_grant, safe_write_text

            g = mint_grant(
                body.get("profile") or "workspace_write",
                workspace_path=body.get("workspace_path") or body.get("root") or "",
                tenant_path=body.get("tenant_path") or "",
                agent_id=body.get("agent_id") or "",
                session_id=body.get("session_id") or "",
            )
            return self._json(
                200,
                safe_write_text(g, body.get("path") or "", body.get("content") or body.get("text") or ""),
            )
        if path in ("/v1/sandbox/voice", "/v1/agent/voice"):
            from pocket.agent_sandbox import mint_grant, voice_turn

            g = mint_grant(
                body.get("profile") or "voice_plugin",
                agent_id=body.get("agent_id") or "voice",
                session_id=body.get("session_id") or "",
                net_hosts=body.get("net_hosts") or ["127.0.0.1", "localhost"],
            )
            return self._json(
                200,
                voice_turn(
                    g,
                    body.get("text") or body.get("utterance") or "",
                    base_url=body.get("base_url") or "http://127.0.0.1:8790",
                    business_mode=body.get("business_mode") or body.get("mode") or "customer_service",
                    session_id=body.get("session_id") or "",
                ),
            )
        if path in ("/v1/sandbox/wasm",):
            from pocket.agent_sandbox import mint_grant, run_wasm

            g = mint_grant(
                body.get("profile") or "untrusted",
                workspace_path=body.get("workspace_path") or "",
                agent_id=body.get("agent_id") or "wasm",
                session_id=body.get("session_id") or "",
                extra_caps=body.get("extra_caps") or [],
            )
            return self._json(
                200,
                run_wasm(
                    g,
                    body.get("wasm_path") or body.get("path") or "",
                    args=body.get("args") or [],
                    stdin_text=body.get("stdin") or body.get("input") or "",
                ),
            )

        return self._json(404, {"error": "not found"})


class PocketHTTPServer(ThreadingHTTPServer):
    """Hardened host: reuse address, daemon request threads, deeper backlog.

    Also applies a per-request socket timeout so a hung client cannot pin a
    worker thread forever (common cause of 'desk freezes / replies never send').
    """

    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 128
    # Idle clients (Edge app backgrounded, half-closed TCP) get cut loose
    timeout = float(os.environ.get("POCKET_REQUEST_TIMEOUT", "120"))

    def server_bind(self):
        # Windows: SO_REUSEADDR alone is enough; avoid SO_REUSEPORT (not always present)
        try:
            import socket as _socket

            self.socket.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        except Exception:
            pass
        super().server_bind()

    def finish_request(self, request, client_address):
        try:
            request.settimeout(self.timeout)
        except Exception:
            pass
        super().finish_request(request, client_address)


def _serve_heartbeat_loop(port: int, stop: threading.Event) -> None:
    """Write a local heartbeat even when runtime-worker is not running.

    Desk/Edge read ~/.pocket/runtime_heartbeat.json; without this file health
    reports stale and the UI looks dead even when serve is fine.
    """
    heart = Path.home() / ".pocket" / "runtime_heartbeat.json"
    beat = 0
    started = time.time()
    while not stop.is_set():
        beat += 1
        try:
            heart.parent.mkdir(parents=True, exist_ok=True)
            # If a real runtime-worker is alive (fresh file from other pid), don't fight it
            other_fresh = False
            if heart.exists():
                try:
                    prev = json.loads(heart.read_text(encoding="utf-8"))
                    age = time.time() - float(prev.get("ts") or 0)
                    wpid = prev.get("worker_pid")
                    if age < 2.0 and wpid and int(wpid) != os.getpid():
                        other_fresh = True
                except Exception:
                    other_fresh = False
            if not other_fresh:
                payload = {
                    "ok": True,
                    "ts": time.time(),
                    "beat": beat,
                    "interval_ms": 873,
                    "uptime_sec": round(time.time() - started, 2),
                    "host": "127.0.0.1",
                    "port": port,
                    "serve_pid": os.getpid(),
                    "worker_pid": os.getpid(),
                    "source": "serve-embedded",
                    "desk": f"http://127.0.0.1:{port}/desk",
                    "landing": f"http://127.0.0.1:{port}/",
                    "port_open": True,
                    "http_ok": True,
                }
                heart.write_text(json.dumps(payload), encoding="utf-8")
        except Exception:
            pass
        stop.wait(0.873)


def serve(host: str = "0.0.0.0", port: int = PORT) -> None:
    global PORT
    PORT = port
    try:
        from pocket.edition import bootstrap_edition, summary as edition_summary

        bootstrap_edition()
        ed = edition_summary()
        print(
            f"[POCKET] edition={ed.get('edition')} app={ed.get('app_url')} "
            f"marketing={ed.get('marketing_url')} github_visible={ed.get('public_github_visible')}",
            flush=True,
        )
    except Exception as e:
        print(f"[POCKET] edition bootstrap warn: {e}", flush=True)
    try:
        from pocket.jobs import reclaim_orphans

        n = reclaim_orphans()
        if n:
            print(f"[POCKET] reclaimed {n} orphan running jobs", flush=True)
    except Exception as e:
        print(f"[POCKET] reclaim warn: {e}", flush=True)
    # Mesh / auro arm AFTER bind — never block first HTTP (login/desk)
    def _bg_hooks():
        try:
            from pocket.agent_hook import ensure_mesh_hook

            hook = ensure_mesh_hook()
            print(
                f"[POCKET] mesh hook armed={hook.get('armed')} "
                f"errors={len(hook.get('errors') or [])}",
                flush=True,
            )
        except Exception as e:
            print(f"[POCKET] mesh hook warn: {e}", flush=True)
        try:
            from pocket.auro14b_bridge import start_silent_training, status as auro_status

            print(
                f"[POCKET] auro14b {auro_status().get('ok')} "
                f"ckpt={auro_status().get('checkpoint_exists')}",
                flush=True,
            )
            start_silent_training()
        except Exception as e:
            print(f"[POCKET] auro14b warn: {e}", flush=True)

    ensure_embedded_worker()
    # Wake Pocket Voice in background so mic/Aria never start cold
    def _wake_voice():
        try:
            from pocket.voice_proxy import ensure_voice

            r = ensure_voice(wait_sec=5.0)
            print(f"[POCKET] voice api ok={r.get('ok')} started={r.get('started')} already={r.get('already')}", flush=True)
        except Exception as e:
            print(f"[POCKET] voice ensure skip: {e}", flush=True)

    threading.Thread(target=_wake_voice, name="pocket-voice-wake", daemon=True).start()
    try:
        from pocket.model_clis import start_host_cli_install_bg

        start_host_cli_install_bg()
    except Exception as e:
        print(f"[POCKET] model cli bg skip: {e}", flush=True)
    stop_heart = threading.Event()
    threading.Thread(
        target=_serve_heartbeat_loop,
        args=(port, stop_heart),
        name="pocket-serve-heart",
        daemon=True,
    ).start()
    httpd = PocketHTTPServer((host, port), Handler)
    threading.Thread(target=_bg_hooks, name="pocket-bg-hooks", daemon=True).start()
    from pocket.auth import ACCESS_NOTE, expected_user

    print("=" * 62, flush=True)
    print("POCKET host online", flush=True)
    print(f"  DESK:    http://127.0.0.1:{port}/desk", flush=True)
    print(f"  LANDING: http://127.0.0.1:{port}/", flush=True)
    print(f"  AUTH:    user={expected_user()}  file={ACCESS_NOTE}", flush=True)
    print(f"  HEART:   serve-embedded 873ms + optional runtime-worker", flush=True)
    print(f"  STACK:   PocketHTTPServer backlog={httpd.request_queue_size} timeout={httpd.timeout}s", flush=True)
    print("=" * 62, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("stopped", flush=True)
    finally:
        stop_heart.set()
        try:
            httpd.server_close()
        except Exception:
            pass


def main(argv: Optional[list] = None) -> None:
    p = argparse.ArgumentParser(prog="pocket")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("serve", help="HTTP multi-agent desk")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--port", type=int, default=PORT)
    sub.add_parser("worker", help="Job worker only")
    r = sub.add_parser("runtime", help="Full Python runtime + watchdog (leave this on)")
    r.add_argument("--once", action="store_true", help="Serve once without watchdog")
    sub.add_parser(
        "runtime-worker",
        help="Keep-alive worker: 873ms heartbeat + auto-restart serve (use with Electron)",
    )
    e = sub.add_parser("ensure", help="Bring POCKET host + watchdog up (agents call this)")
    e.add_argument("which", nargs="?", default="all")
    sub.add_parser("install", help="Whole always-on install (logon task + Startup + ensure)")
    sub.add_parser("doctor", help="Product readiness report")
    sub.add_parser("desktop", help="POCKET Desktop app (native window + local host)")
    sub.add_parser("channels", help="Print product channels (Desktop vs API)")
    sub.add_parser(
        "desktop-pack",
        help="Copy electron-builder output into releases/desktop for web download",
    )
    args = p.parse_args(argv)
    if args.cmd == "worker":
        from pocket.worker import run_loop

        run_loop()
        return
    if args.cmd == "runtime-worker":
        from pocket.runtime_worker import run as runtime_worker_run

        runtime_worker_run()
        return
    if args.cmd == "runtime":
        # One hidden watchdog: heartbeat + at most one serve child.
        from pocket.runtime_worker import run as runtime_worker_run

        runtime_worker_run()
        return
    if args.cmd == "ensure":
        from pocket.host_runtime import ensure as runtime_ensure
        import json as _json

        print(_json.dumps(runtime_ensure(getattr(args, "which", "all") or "all"), indent=2, default=str))
        return
    if args.cmd == "install":
        from pocket.host_runtime import install as runtime_install
        import json as _json

        print(_json.dumps(runtime_install(), indent=2, default=str))
        return
    if args.cmd == "doctor":
        from pocket.product import doctor
        import json as _json

        print(_json.dumps(doctor(), indent=2, default=str))
        return
    if args.cmd == "desktop":
        from pocket.desktop_app import run_desktop

        raise SystemExit(run_desktop())
    if args.cmd == "desktop-pack":
        from pocket.desktop_pack import pack_releases
        import json as _json

        print(_json.dumps(pack_releases(), indent=2, default=str))
        return
    if args.cmd == "channels":
        from pocket.product_channels import channels
        import json as _json

        print(_json.dumps(channels(), indent=2, default=str))
        return
    if args.cmd == "serve" or args.cmd is None:
        serve(getattr(args, "host", "0.0.0.0"), getattr(args, "port", PORT))
        return
    p.print_help()


if __name__ == "__main__":
    main()




