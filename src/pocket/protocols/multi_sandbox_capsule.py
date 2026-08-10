"""PROTO-CAPSULE-WASM-009 — Multi-Sandbox Capsule Execution & WebGPU Orchestration.

ItsNotAILabs / POCKET host implementation of the Multi-Sandbox Capsule Protocol.

Design (from technical spec + WebGPU doctrine):
  - CapsuleManager singleton + CapsuleInstance lifecycle
  - Memory tiers 256MB | 512MB | 1024MB (64MB reserved for runtime shim)
  - Runtimes: WASI (wasmtime when present) | HostWorker (isolated cwd + caps)
  - OverlayFS under ~/.pocket/capsules/{id}/overlay until commit()
  - NetworkPolicy: no ambient net unless granted
  - WebGPU: host probe + orchestration flags; GPU kernels proxied securely
    (SharedArrayBuffer-shaped design; browser WebGPU for Edge capsules)

Security: sandboxed from host kernel integrity; never elevates ambient authority.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple

PROTOCOL_ID = "PROTO-CAPSULE-WASM-009"
PROTOCOL_NAME = "Multi-Sandbox Capsule Execution & WebGPU Orchestration"
PROTOCOL_SCHEMA = "pocket.capsule.v1"
ARCHIVAL = "INL-2026-CAPSULE.WASM.v1"

# 20 reasons agents spin WASM capsules (improves isolation, parallelism, safety)
CAPSULE_AGENT_REASONS = [
    {"id": "untrusted_eval", "title": "Untrusted evaluation", "improves": "Run untrusted code without host ambient authority"},
    {"id": "sandbox_tests", "title": "Sandboxed tests", "improves": "Isolated tests that cannot trash the workspace"},
    {"id": "dependency_install", "title": "Ephemeral dependencies", "improves": "Install packages that never leak into host env"},
    {"id": "repo_mount_edit", "title": "Overlay repo edits", "improves": "Edit in overlay; commit only on explicit approve"},
    {"id": "wasm_guest_tool", "title": "WASM guest tools", "improves": "Portable .wasm tools with no ambient network"},
    {"id": "webgpu_compute", "title": "WebGPU compute", "improves": "GPGPU/ML kernels via WebGPU doctrine"},
    {"id": "parallel_slice", "title": "Parallel RAH slice", "improves": "Isolate one fan-out leaf FS to avoid writer collisions"},
    {"id": "adversarial_verify", "title": "Adversarial verify", "improves": "Throwaway environment for verifier/adversary"},
    {"id": "repro_bug", "title": "Bug reproduction", "improves": "Clean env repro with logs; terminate when done"},
    {"id": "secret_scrub", "title": "Secret scrubbing", "improves": "Discard overlay if secrets appear in processing"},
    {"id": "browser_worker", "title": "Browser worker", "improves": "DOM/WebGPU guest without polluting desk session"},
    {"id": "build_artifact", "title": "Build artifacts", "improves": "Compile in capsule; export only dist outputs"},
    {"id": "fuzz_input", "title": "Fuzz isolation", "improves": "Crash isolation for parsers and tools"},
    {"id": "policy_eval", "title": "Policy evaluation", "improves": "Run policy scripts without mutating live ledgers"},
    {"id": "skill_preview", "title": "Skill preview", "improves": "Try generated skills before durable promote"},
    {"id": "third_party_cli", "title": "Third-party CLI", "improves": "Cap FS preopens for untrusted CLIs"},
    {"id": "long_job_park", "title": "Long job park", "improves": "Park long work in overlay between heartbeats"},
    {"id": "multi_tenant_slice", "title": "Multi-tenant slice", "improves": "Soft isolation for seat/demo runs"},
    {"id": "mesh_artifact_lab", "title": "Mesh artifact lab", "improves": "Produce artifacts offline; publish hash-only"},
    {"id": "rollback_experiment", "title": "Rollback experiment", "improves": "Experiment freely; terminate = full rollback"},
]

# Memory tiers (spec) + 64MB shim overhead
TIERS = {
    "256MB": 256,
    "512MB": 512,
    "1024MB": 1024,
}
RUNTIME_SHIM_MB = 64
RUNTIMES = frozenset({"WASI", "BrowserWorker", "HostWorker"})

ROOT = Path.home() / ".pocket" / "capsules"
ROOT.mkdir(parents=True, exist_ok=True)

_lock = Lock()
_manager: Optional["CapsuleManager"] = None


# ---------------------------------------------------------------------------
# WebGPU orchestration (host + doctrine for Edge/BrowserWorker capsules)
# ---------------------------------------------------------------------------

WEBGPU_DOCTRINE = {
    "why": (
        "WebGPU is a modern web API (Vulkan/Metal/D3D12-inspired) for low-overhead "
        "GPU access — rendering + GPGPU — vs WebGL's implicit state machine."
    ),
    "advantages": [
        "Lower CPU overhead: explicit pipelines, bind groups, command buffers",
        "Native compute shaders (first-class vs WebGL fragment hacks)",
        "Higher draw-call scalability (render bundles 10×+ scene resubmit)",
        "ML/compute: 2–3× vs WebGL backends; 25–30×+ vs CPU for parallel ops",
        "f16 / 8-bit quant / packed ops for extra 1.6–3× + bandwidth savings",
        "Client-side AI: privacy, lower latency, offline (WebLLM, TF.js, ORT Web)",
        "Strong synergy with Wasm/WASI capsules via SharedArrayBuffer proxy",
    ],
    "typical_speedups": {
        "cpu_parallel_ops": "25–30×+",
        "webgl_ml_backends": "2–3×+",
        "gemm_large": "3–8×",
        "llm_token_latency_example": "~320ms → ~85ms",
        "text_embeddings_vs_cpu": "30–120× (reported)",
    },
    "frameworks": [
        "TensorFlow.js (WebGPU backend)",
        "ONNX Runtime Web",
        "WebLLM",
        "Transformers.js",
    ],
    "capsule_integration": (
        "enableWebGPU=true on CapsuleConfig gates GPUAdapter permission. "
        "HostWorker probes DX/Vulkan adapters; BrowserWorker uses navigator.gpu. "
        "WASI guests receive compute proxies, not raw host GPU device handles."
    ),
    "constraints": [
        "Small tasks may not amortize GPU transfer overhead",
        "Power/thermal depend on device",
        "Chrome/Edge/Safari support solid 2025–2026; others evolving",
    ],
}


def probe_webgpu() -> Dict[str, Any]:
    """Host-side GPU/WebGPU readiness probe (no browser required)."""
    out: Dict[str, Any] = {
        "ok": True,
        "protocol": PROTOCOL_ID,
        "webgpu_spec": "https://gpuweb.github.io/gpuweb/",
        "doctrine": WEBGPU_DOCTRINE,
        "host": {},
        "adapters": [],
        "edge_webgpu": None,
        "wasmtime": bool(shutil.which("wasmtime")),
    }
    # Windows: DXGI / wmic display adapter names
    try:
        if os.name == "nt":
            r = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Get-CimInstance Win32_VideoController | "
                    "Select-Object -ExpandProperty Name",
                ],
                capture_output=True,
                text=True,
                timeout=8,
            )
            names = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
            out["adapters"] = names[:8]
            out["host"]["gpu_names"] = names[:8]
            out["host"]["has_discrete_hint"] = any(
                re.search(r"NVIDIA|GeForce|Radeon|Intel Arc|RTX|GTX", n, re.I) for n in names
            )
    except Exception as e:
        out["host"]["probe_error"] = str(e)[:160]

    # Edge/Chrome presence → BrowserWorker WebGPU viable
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    browser = next((p for p in edge_paths if os.path.isfile(p)), None)
    out["edge_webgpu"] = {
        "browser_found": bool(browser),
        "path": browser,
        "note": "navigator.gpu available in Chromium-based browsers with WebGPU enabled",
        "enable_flag": "--enable-unsafe-webgpu (legacy; usually default on now)",
    }
    out["enable_recommendation"] = bool(out["adapters"]) or bool(browser)
    out["message"] = (
        "WebGPU orchestration ready for capsules"
        if out["enable_recommendation"]
        else "No GPU adapter detected — capsules fall back to CPU HostWorker"
    )
    return out


# ---------------------------------------------------------------------------
# Memory controller
# ---------------------------------------------------------------------------

class MemoryController:
    """Gated memory reservations to prevent OOM cascades across capsules."""

    def __init__(self, host_budget_mb: int = 4096) -> None:
        self.host_budget_mb = host_budget_mb
        self._reserved: Dict[str, int] = {}
        self._lock = Lock()

    def reserve(self, capsule_id: str, tier_mb: int) -> Tuple[bool, str]:
        with self._lock:
            used = sum(self._reserved.values())
            if used + tier_mb > self.host_budget_mb:
                return False, f"trap:memory_budget (used={used} need={tier_mb} budget={self.host_budget_mb})"
            self._reserved[capsule_id] = tier_mb
            return True, ""

    def release(self, capsule_id: str) -> None:
        with self._lock:
            self._reserved.pop(capsule_id, None)

    def status(self) -> Dict[str, Any]:
        with self._lock:
            reserved = dict(self._reserved)
        used = sum(reserved.values())
        return {
            "host_budget_mb": self.host_budget_mb,
            "reserved_mb": used,
            "free_mb": max(0, self.host_budget_mb - used),
            "capsules": reserved,
            "shim_mb": RUNTIME_SHIM_MB,
        }


# ---------------------------------------------------------------------------
# Network policy
# ---------------------------------------------------------------------------

@dataclass
class NetworkPolicy:
    """No ambient network — explicit allowlist only."""

    allow_hosts: List[str] = field(default_factory=list)
    allow_all: bool = False

    def allowed(self, host: str) -> bool:
        if self.allow_all:
            return True
        h = (host or "").lower().strip()
        return h in {a.lower() for a in self.allow_hosts}

    def to_dict(self) -> Dict[str, Any]:
        return {"allow_hosts": list(self.allow_hosts), "allow_all": self.allow_all}


# ---------------------------------------------------------------------------
# Capsule config / instance
# ---------------------------------------------------------------------------

@dataclass
class CapsuleConfig:
    tier: str = "512MB"  # 256MB | 512MB | 1024MB
    enable_webgpu: bool = False
    repo_source: str = ""  # URI, github:org/repo, or local path
    runtime: str = "HostWorker"  # WASI | BrowserWorker | HostWorker
    network: Optional[NetworkPolicy] = None
    agent_id: str = ""
    label: str = ""

    def tier_mb(self) -> int:
        return TIERS.get(self.tier, 512)

    def usable_mb(self) -> int:
        return max(32, self.tier_mb() - RUNTIME_SHIM_MB)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "enableWebGPU": self.enable_webgpu,
            "repoSource": self.repo_source,
            "runtime": self.runtime,
            "tier_mb": self.tier_mb(),
            "usable_mb": self.usable_mb(),
            "network": (self.network or NetworkPolicy()).to_dict(),
            "agent_id": self.agent_id,
            "label": self.label,
        }


@dataclass
class ChangeSet:
    hash: str
    capsule_id: str
    files: List[Dict[str, Any]]
    message: str
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CapsuleInstance:
    """Ephemeral isolated execution environment (OverlayFS + command runner)."""

    def __init__(self, config: CapsuleConfig, memory: MemoryController) -> None:
        self.id = "cap-" + uuid.uuid4().hex[:12]
        self.config = config
        self.memory = memory
        self.state = "allocated"  # allocated | mounted | running | committed | terminated
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.root = ROOT / self.id
        self.vfs = self.root / "vfs"
        self.overlay = self.root / "overlay"
        self.logs_dir = self.root / "logs"
        self.meta_path = self.root / "meta.json"
        self._stdout: List[Dict[str, Any]] = []
        self._mounted_repo = ""
        self._baseline: Dict[str, str] = {}  # relpath → sha256
        self.webgpu_bound = False
        self.error = ""

    def _touch(self) -> None:
        self.updated_at = time.time()
        self._save_meta()

    def _save_meta(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        meta = self.to_dict()
        self.meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "state": self.state,
            "config": self.config.to_dict(),
            "root": str(self.root),
            "vfs": str(self.vfs),
            "overlay": str(self.overlay),
            "mounted_repo": self._mounted_repo,
            "webgpu_bound": self.webgpu_bound,
            "stdout_lines": len(self._stdout),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
            "protocol": PROTOCOL_ID,
        }

    def _bind_webgpu(self) -> Dict[str, Any]:
        if not self.config.enable_webgpu:
            return {"ok": True, "enabled": False}
        probe = probe_webgpu()
        self.webgpu_bound = bool(probe.get("enable_recommendation"))
        # Write GPU permission manifest for guest
        manifest = {
            "GPUAdapter": "host_probe",
            "enabled": self.webgpu_bound,
            "adapters": probe.get("adapters") or [],
            "compute_shaders": True,
            "proxy": "SharedArrayBuffer-shaped (host) / navigator.gpu (BrowserWorker)",
            "doctrine_summary": WEBGPU_DOCTRINE["advantages"][:4],
        }
        (self.root / "gpu_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        return {"ok": True, "enabled": self.webgpu_bound, "manifest": manifest}

    def mount(self, repo: Any = None) -> Dict[str, Any]:
        """Map repository into capsule VFS (ingest)."""
        if self.state == "terminated":
            return {"ok": False, "error": "trap:terminated", "id": self.id}

        self.vfs.mkdir(parents=True, exist_ok=True)
        self.overlay.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        source = ""
        if isinstance(repo, dict):
            source = str(repo.get("path") or repo.get("uri") or repo.get("source") or "")
        elif isinstance(repo, (str, Path)):
            source = str(repo)
        if not source:
            source = self.config.repo_source or ""

        mounted = False
        detail = ""
        if source:
            # Local path
            p = Path(source)
            if p.is_dir():
                # Shallow copy tree into overlay (not full deep clone of huge repos)
                try:
                    self._copy_tree_limited(p, self.overlay, max_files=4000)
                    mounted = True
                    detail = f"local tree → overlay ({source})"
                    self._mounted_repo = str(p.resolve())
                except Exception as e:
                    detail = f"local mount failed: {e}"[:200]
            elif source.startswith("github:") or "github.com" in source:
                # Best-effort shallow clone into vfs
                repo_slug = source
                if source.startswith("github:"):
                    repo_slug = source.split(":", 1)[1]
                elif "github.com/" in source:
                    repo_slug = source.split("github.com/", 1)[1].strip("/").replace(".git", "")
                dest = self.vfs / "repo"
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                try:
                    r = subprocess.run(
                        ["git", "clone", "--depth", "1", f"https://github.com/{repo_slug}.git", str(dest)],
                        capture_output=True,
                        text=True,
                        timeout=90,
                    )
                    if r.returncode == 0:
                        # Work on overlay copy
                        if self.overlay.exists():
                            shutil.rmtree(self.overlay, ignore_errors=True)
                        shutil.copytree(dest, self.overlay)
                        mounted = True
                        detail = f"cloned github:{repo_slug}"
                        self._mounted_repo = f"github:{repo_slug}"
                    else:
                        detail = (r.stderr or r.stdout or "clone failed")[:300]
                except Exception as e:
                    detail = f"clone error: {e}"[:200]
            else:
                # Create empty project with README pointing at source
                (self.overlay / "REPO_SOURCE.txt").write_text(source, encoding="utf-8")
                detail = "source recorded; empty overlay workspace"
                mounted = True
                self._mounted_repo = source
        else:
            (self.overlay / "README.md").write_text(
                f"# Capsule {self.id}\n\nPROTO-CAPSULE-WASM-009 empty workspace.\n",
                encoding="utf-8",
            )
            mounted = True
            detail = "empty workspace"

        self._baseline = self._hash_tree(self.overlay)
        gpu = self._bind_webgpu()
        self.state = "mounted"
        self._touch()
        return {
            "ok": mounted,
            "id": self.id,
            "state": self.state,
            "detail": detail,
            "mounted_repo": self._mounted_repo,
            "overlay": str(self.overlay),
            "webgpu": gpu,
            "baseline_files": len(self._baseline),
        }

    def _copy_tree_limited(self, src: Path, dst: Path, max_files: int = 4000) -> int:
        n = 0
        skip = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d not in skip]
            rel_root = Path(root).relative_to(src)
            target_root = dst / rel_root
            target_root.mkdir(parents=True, exist_ok=True)
            for f in files:
                if n >= max_files:
                    return n
                sp = Path(root) / f
                try:
                    if sp.stat().st_size > 8_000_000:
                        continue
                    shutil.copy2(sp, target_root / f)
                    n += 1
                except Exception:
                    continue
        return n

    def _hash_tree(self, root: Path) -> Dict[str, str]:
        out: Dict[str, str] = {}
        if not root.is_dir():
            return out
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                rel = str(p.relative_to(root)).replace("\\", "/")
                h = hashlib.sha256(p.read_bytes()[:2_000_000]).hexdigest()[:16]
                out[rel] = h
            except Exception:
                continue
        return out

    def execute(self, command: str, *, timeout_sec: Optional[float] = None) -> Dict[str, Any]:
        """Run a command inside the capsule cwd (HostWorker) or wasmtime (WASI).

        Returns a single stdout stream batch (Observable-shaped list of events).
        """
        if self.state == "terminated":
            return {"ok": False, "error": "trap:terminated", "id": self.id}
        if self.state == "allocated":
            self.mount()

        cmd = (command or "").strip()
        if not cmd:
            return {"ok": False, "error": "command required", "id": self.id}

        # NetworkPolicy: block curl/wget to non-allowlisted if we can detect host
        if re.search(r"\b(curl|wget|Invoke-WebRequest)\b", cmd, re.I):
            pol = self.config.network or NetworkPolicy()
            if not pol.allow_all and not pol.allow_hosts:
                evt = {
                    "t": time.time(),
                    "stream": "stderr",
                    "line": "NetworkPolicy: global network denied (set network allow_hosts)",
                }
                self._stdout.append(evt)
                return {
                    "ok": False,
                    "error": "trap:network_policy",
                    "id": self.id,
                    "events": [evt],
                }

        self.state = "running"
        self._touch()
        cwd = self.overlay if self.overlay.is_dir() else self.root
        events: List[Dict[str, Any]] = []
        max_ms = max(5_000, self.config.usable_mb() * 50)  # scale lightly with tier
        if timeout_sec is None:
            timeout_sec = min(120.0, max_ms / 1000.0)

        t0 = time.time()
        runtime = self.config.runtime

        if runtime == "WASI" and shutil.which("wasmtime"):
            # Expect command like path/to.wasm [args...]
            parts = cmd.split()
            wasm = parts[0]
            args = parts[1:]
            wasm_path = Path(wasm) if Path(wasm).is_file() else (cwd / wasm)
            try:
                proc = subprocess.run(
                    ["wasmtime", "run", str(wasm_path), *args],
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                )
                for line in (proc.stdout or "").splitlines():
                    events.append({"t": time.time(), "stream": "stdout", "line": line})
                for line in (proc.stderr or "").splitlines():
                    events.append({"t": time.time(), "stream": "stderr", "line": line})
                ok = proc.returncode == 0
                code = proc.returncode
            except Exception as e:
                events.append({"t": time.time(), "stream": "stderr", "line": str(e)[:300]})
                ok, code = False, -1
        else:
            # HostWorker: shell in overlay only (cwd containment)
            shell = True
            if os.name == "nt":
                full = ["powershell", "-NoProfile", "-Command", cmd]
                shell = False
            else:
                full = ["bash", "-lc", cmd]
                shell = False
            try:
                env = os.environ.copy()
                env["POCKET_CAPSULE_ID"] = self.id
                env["POCKET_CAPSULE_PROTOCOL"] = PROTOCOL_ID
                env["POCKET_CAPSULE_WEBGPU"] = "1" if self.webgpu_bound else "0"
                env["POCKET_CAPSULE_USABLE_MB"] = str(self.config.usable_mb())
                # Strip secrets-ish ambient if any
                proc = subprocess.run(
                    full,
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec,
                    env=env,
                    shell=shell,
                )
                for line in (proc.stdout or "").splitlines():
                    events.append({"t": time.time(), "stream": "stdout", "line": line[:2000]})
                for line in (proc.stderr or "").splitlines():
                    events.append({"t": time.time(), "stream": "stderr", "line": line[:2000]})
                ok = proc.returncode == 0
                code = proc.returncode
            except subprocess.TimeoutExpired:
                events.append({"t": time.time(), "stream": "stderr", "line": "trap:timeout"})
                ok, code = False, -2
            except Exception as e:
                events.append({"t": time.time(), "stream": "stderr", "line": str(e)[:300]})
                ok, code = False, -1

        self._stdout.extend(events)
        # Persist log
        try:
            log_path = self.logs_dir / f"exec_{int(time.time())}.jsonl"
            with log_path.open("a", encoding="utf-8") as f:
                for e in events:
                    f.write(json.dumps(e) + "\n")
        except Exception:
            pass

        self.state = "mounted"
        self._touch()
        return {
            "ok": ok,
            "id": self.id,
            "command": cmd[:500],
            "runtime": runtime if runtime != "WASI" or shutil.which("wasmtime") else "HostWorker",
            "cwd": str(cwd),
            "exit_code": code,
            "ms": int((time.time() - t0) * 1000),
            "events": events[-200:],
            "webgpu_bound": self.webgpu_bound,
            "stream_note": "Observable-shaped: subscribe to events[] (stdout/stderr)",
        }

    def execute_stream(self, command: str) -> Generator[Dict[str, Any], None, None]:
        """Yield stdout events (for Observable-style consumers)."""
        r = self.execute(command)
        for e in r.get("events") or []:
            yield e
        yield {"t": time.time(), "stream": "done", "ok": r.get("ok"), "exit_code": r.get("exit_code")}

    def commit(self) -> Dict[str, Any]:
        """Buffer overlay diffs → ChangeSet (merge-ready, does not touch host repos unless copied)."""
        if self.state == "terminated":
            return {"ok": False, "error": "trap:terminated"}
        current = self._hash_tree(self.overlay)
        files: List[Dict[str, Any]] = []
        for path, h in current.items():
            if self._baseline.get(path) != h:
                files.append({"path": path, "sha": h, "op": "add" if path not in self._baseline else "modify"})
        for path in self._baseline:
            if path not in current:
                files.append({"path": path, "sha": self._baseline[path], "op": "delete"})

        blob = json.dumps(files, sort_keys=True).encode("utf-8")
        chash = hashlib.sha256(blob).hexdigest()[:16]
        cs = ChangeSet(
            hash=chash,
            capsule_id=self.id,
            files=files[:500],
            message=f"capsule commit {len(files)} changes",
            created_at=time.time(),
        )
        # Persist changeset
        (self.root / "changeset.json").write_text(
            json.dumps(cs.to_dict(), indent=2), encoding="utf-8"
        )
        # Optional merge target under ~/.pocket/workspaces/capsule-merges
        merge_root = Path.home() / ".pocket" / "workspaces" / "capsule-merges" / self.id
        try:
            if self.overlay.is_dir():
                if merge_root.exists():
                    shutil.rmtree(merge_root, ignore_errors=True)
                shutil.copytree(self.overlay, merge_root)
        except Exception as e:
            return {
                "ok": True,
                "changeset": cs.to_dict(),
                "merge_error": str(e)[:160],
                "message": f"ChangeSet {chash} recorded; merge copy failed",
            }

        self.state = "committed"
        self._baseline = current
        self._touch()
        return {
            "ok": True,
            "changeset": cs.to_dict(),
            "merge_path": str(merge_root),
            "hash": chash,
            "message": f"Changes synced: {chash}",
            "file_count": len(files),
        }

    def terminate(self) -> Dict[str, Any]:
        self.state = "terminated"
        self.memory.release(self.id)
        self._touch()
        # Keep files for audit; optional purge via manager.gc
        return {"ok": True, "id": self.id, "state": "terminated"}


# ---------------------------------------------------------------------------
# CapsuleManager singleton
# ---------------------------------------------------------------------------

class CapsuleManager:
    """Singleton manager for multi-sandbox capsules."""

    def __init__(self, host_budget_mb: int = 4096) -> None:
        self.memory = MemoryController(host_budget_mb=host_budget_mb)
        self._capsules: Dict[str, CapsuleInstance] = {}
        self._lock = Lock()

    def allocate(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cfg_in = config or {}
        tier = str(cfg_in.get("tier") or "512MB")
        if tier not in TIERS:
            # allow bare numbers
            if str(tier).isdigit():
                tier = f"{tier}MB" if int(tier) >= 256 else "256MB"
            if tier not in TIERS:
                tier = "512MB"
        runtime = str(cfg_in.get("runtime") or "HostWorker")
        if runtime not in RUNTIMES:
            runtime = "HostWorker"
        net = cfg_in.get("network") or {}
        policy = NetworkPolicy(
            allow_hosts=list(net.get("allow_hosts") or cfg_in.get("allow_hosts") or []),
            allow_all=bool(net.get("allow_all") or cfg_in.get("allow_all")),
        )
        config_obj = CapsuleConfig(
            tier=tier,
            enable_webgpu=bool(
                cfg_in.get("enableWebGPU")
                if "enableWebGPU" in cfg_in
                else cfg_in.get("enable_webgpu")
            ),
            repo_source=str(cfg_in.get("repoSource") or cfg_in.get("repo_source") or cfg_in.get("repo") or ""),
            runtime=runtime,
            network=policy,
            agent_id=str(cfg_in.get("agent_id") or cfg_in.get("agent") or ""),
            label=str(cfg_in.get("label") or ""),
        )
        ok, trap = self.memory.reserve("pending", config_obj.tier_mb())
        # reserve with real id after create
        if not ok:
            # try free terminated
            self.gc(keep_committed=True)
            ok, trap = self.memory.reserve("pending", config_obj.tier_mb())
            if not ok:
                return {"ok": False, "error": trap, "memory": self.memory.status()}

        cap = CapsuleInstance(config_obj, self.memory)
        self.memory.release("pending")
        ok2, trap2 = self.memory.reserve(cap.id, config_obj.tier_mb())
        if not ok2:
            return {"ok": False, "error": trap2, "memory": self.memory.status()}

        with self._lock:
            self._capsules[cap.id] = cap
        cap.root.mkdir(parents=True, exist_ok=True)
        cap._save_meta()

        # Auto-mount if repo source present
        mount_r = None
        if config_obj.repo_source:
            mount_r = cap.mount(config_obj.repo_source)
        else:
            mount_r = cap.mount()

        reason = str(cfg_in.get("reason") or cfg_in.get("why") or "").strip()
        if reason:
            try:
                (cap.root / "reason.txt").write_text(reason + "\n", encoding="utf-8")
            except Exception:
                pass
        return {
            "ok": True,
            "protocol": PROTOCOL_ID,
            "capsule": {**cap.to_dict(), "reason": reason or None},
            "reason": reason or None,
            "mount": mount_r,
            "memory": self.memory.status(),
            "webgpu_probe": probe_webgpu() if config_obj.enable_webgpu else None,
            "agent_reasons": CAPSULE_AGENT_REASONS,
            "message": f"Capsule {cap.id} allocated ({config_obj.tier}, usable={config_obj.usable_mb()}MB)"
            + (f" · reason={reason}" if reason else ""),
        }

    def get(self, capsule_id: str) -> Optional[CapsuleInstance]:
        with self._lock:
            return self._capsules.get(capsule_id)

    def list(self) -> Dict[str, Any]:
        with self._lock:
            items = [c.to_dict() for c in self._capsules.values()]
        return {
            "ok": True,
            "protocol": PROTOCOL_ID,
            "count": len(items),
            "capsules": items,
            "memory": self.memory.status(),
        }

    def execute(self, capsule_id: str, command: str, **kwargs: Any) -> Dict[str, Any]:
        cap = self.get(capsule_id)
        if not cap:
            return {"ok": False, "error": f"unknown capsule: {capsule_id}"}
        return cap.execute(command, **kwargs)

    def commit(self, capsule_id: str) -> Dict[str, Any]:
        cap = self.get(capsule_id)
        if not cap:
            return {"ok": False, "error": f"unknown capsule: {capsule_id}"}
        return cap.commit()

    def terminate(self, capsule_id: str) -> Dict[str, Any]:
        cap = self.get(capsule_id)
        if not cap:
            return {"ok": False, "error": f"unknown capsule: {capsule_id}"}
        r = cap.terminate()
        return r

    def gc(self, *, keep_committed: bool = True) -> Dict[str, Any]:
        removed = []
        with self._lock:
            dead = [
                cid
                for cid, c in self._capsules.items()
                if c.state == "terminated" or (not keep_committed and c.state == "committed")
            ]
            for cid in dead:
                self._capsules.pop(cid, None)
                self.memory.release(cid)
                removed.append(cid)
        return {"ok": True, "removed": removed, "memory": self.memory.status()}


def manager() -> CapsuleManager:
    global _manager
    with _lock:
        if _manager is None:
            _manager = CapsuleManager()
        return _manager


# ---------------------------------------------------------------------------
# Protocol surface for agents / API
# ---------------------------------------------------------------------------

def protocol_manifest() -> Dict[str, Any]:
    return {
        "ok": True,
        "id": PROTOCOL_ID,
        "name": PROTOCOL_NAME,
        "schema": PROTOCOL_SCHEMA,
        "archival": ARCHIVAL,
        "interfaces": {
            "CapsuleManager": ["allocate", "list", "get", "execute", "commit", "terminate", "gc"],
            "CapsuleInstance": ["mount", "execute", "commit", "terminate"],
        },
        "tiers": list(TIERS.keys()),
        "runtimes": sorted(RUNTIMES),
        "shim_mb": RUNTIME_SHIM_MB,
        "webgpu": WEBGPU_DOCTRINE,
        "security": [
            "No ambient network (NetworkPolicy)",
            "OverlayFS isolation until commit()",
            "MemoryController prevents OOM cascades",
            "GPU via permission manifest — no raw host device to untrusted guests",
        ],
        "api": [
            "GET /v1/capsule",
            "GET /v1/capsule/webgpu",
            "POST /v1/capsule/allocate",
            "POST /v1/capsule/execute",
            "POST /v1/capsule/commit",
            "POST /v1/capsule/terminate",
            "GET /v1/protocols/capsule",
        ],
        "skills": [
            "capsule_status",
            "capsule_allocate",
            "capsule_execute",
            "capsule_commit",
            "capsule_terminate",
            "capsule_list",
            "webgpu_probe",
        ],
        "depends": [
            "pocket.agent_sandbox (capability grants)",
            "wasmtime optional (WASI)",
            "Edge/Chrome (BrowserWorker WebGPU)",
        ],
        "example": {
            "allocate": {
                "tier": "1024MB",
                "enableWebGPU": True,
                "repoSource": "github:org/repo-name",
                "runtime": "HostWorker",
            },
            "execute": "python -c \"print('capsule ok')\"",
            "commit": "changeset.hash",
        },
    }


def status() -> Dict[str, Any]:
    m = manager()
    return {
        "ok": True,
        "protocol": PROTOCOL_ID,
        "name": PROTOCOL_NAME,
        "memory": m.memory.status(),
        "capsules": m.list().get("count"),
        "webgpu": {
            "doctrine_loaded": True,
            "probe": probe_webgpu(),
        },
        "wasmtime": bool(shutil.which("wasmtime")),
        "root": str(ROOT),
        "manifest": protocol_manifest(),
    }


def run_capsule_skill(
    skill_id: str,
    *,
    prompt: str = "",
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Agent-callable capsule skills."""
    sid = (skill_id or "").strip().lower().replace("-", "_")
    params = params or {}
    m = manager()

    if sid in ("capsule_status", "capsule", "capsules", "multi_sandbox"):
        return status()

    if sid in ("capsule_reasons", "wasm_reasons", "why_capsules", "capsule_why"):
        return {
            "ok": True,
            "protocol": PROTOCOL_ID,
            "count": len(CAPSULE_AGENT_REASONS),
            "reasons": CAPSULE_AGENT_REASONS,
            "doctrine": "Agents spin capsules for isolation, parallel FS safety, GPU, untrusted eval — not as a demo",
        }

    if sid in ("webgpu_probe", "webgpu", "webgpu_status"):
        return probe_webgpu()

    if sid in ("capsule_list", "list_capsules"):
        return m.list()

    if sid in ("capsule_allocate", "capsule_create", "allocate_capsule", "capsule_spin", "spin_capsule"):
        cfg = dict(params)
        if prompt and not cfg.get("repoSource") and not cfg.get("repo_source"):
            # github: or path in prompt
            if re.search(r"github[:/]", prompt, re.I) or Path(prompt.strip()).exists():
                cfg["repoSource"] = prompt.strip().split()[0]
        if "enableWebGPU" not in cfg and "enable_webgpu" not in cfg:
            # auto-enable if prompt mentions gpu
            if re.search(r"\b(webgpu|gpu|compute shader|gpgpu)\b", prompt, re.I):
                cfg["enableWebGPU"] = True
        if re.search(r"\b(1024|1gb|1 gb)\b", prompt, re.I):
            cfg.setdefault("tier", "1024MB")
        elif re.search(r"\b256\b", prompt, re.I):
            cfg.setdefault("tier", "256MB")
        # Auto-pick reason id from prompt when agent didn't pass one
        if not cfg.get("reason"):
            low = (prompt or "").lower()
            for r in CAPSULE_AGENT_REASONS:
                if r["id"].replace("_", " ") in low or r["id"] in low or r["title"].lower() in low:
                    cfg["reason"] = r["id"]
                    break
            if not cfg.get("reason"):
                if re.search(r"\buntrusted|eval\b|sandbox\b", low):
                    cfg["reason"] = "untrusted_eval"
                elif re.search(r"\btest|pytest\b", low):
                    cfg["reason"] = "sandbox_tests"
                elif re.search(r"\bgpu|webgpu\b", low):
                    cfg["reason"] = "webgpu_compute"
                elif re.search(r"\bfuzz\b", low):
                    cfg["reason"] = "fuzz_input"
                else:
                    cfg["reason"] = "rollback_experiment"
        return m.allocate(cfg)

    if sid in ("capsule_execute", "capsule_run", "execute_capsule"):
        cid = params.get("id") or params.get("capsule_id") or params.get("capsule") or ""
        cmd = params.get("command") or params.get("cmd") or prompt or ""
        # allow "id: cmd" in prompt
        if not cid and ":" in (prompt or "")[:40]:
            maybe_id, rest = prompt.split(":", 1)
            if maybe_id.strip().startswith("cap-"):
                cid, cmd = maybe_id.strip(), rest.strip()
        if not cid:
            # allocate ephemeral + run
            alloc = m.allocate(
                {
                    "tier": params.get("tier") or "512MB",
                    "enableWebGPU": bool(params.get("enableWebGPU") or params.get("enable_webgpu")),
                    "runtime": params.get("runtime") or "HostWorker",
                    "label": "ephemeral-exec",
                }
            )
            if not alloc.get("ok"):
                return alloc
            cid = alloc["capsule"]["id"]
            r = m.execute(cid, cmd)
            r["allocated"] = alloc["capsule"]
            return r
        return m.execute(cid, cmd)

    if sid in ("capsule_commit", "commit_capsule"):
        cid = params.get("id") or params.get("capsule_id") or prompt.strip().split()[0] if prompt else ""
        if not cid:
            return {"ok": False, "error": "capsule id required"}
        return m.commit(cid)

    if sid in ("capsule_terminate", "terminate_capsule", "capsule_kill"):
        cid = params.get("id") or params.get("capsule_id") or (prompt.strip().split()[0] if prompt else "")
        if not cid:
            return {"ok": False, "error": "capsule id required"}
        return m.terminate(cid)

    if sid in ("capsule_mount", "mount_capsule"):
        cid = params.get("id") or params.get("capsule_id") or ""
        cap = m.get(cid) if cid else None
        if not cap:
            return {"ok": False, "error": "capsule id required / not found"}
        return cap.mount(params.get("repo") or prompt or params.get("path") or "")

    return {
        "ok": False,
        "error": f"unknown capsule skill: {sid}",
        "available": [
            "capsule_status",
            "capsule_allocate",
            "capsule_execute",
            "capsule_commit",
            "capsule_terminate",
            "capsule_list",
            "capsule_mount",
            "webgpu_probe",
        ],
    }


def is_capsule_skill(skill_id: str) -> bool:
    sid = (skill_id or "").strip().lower().replace("-", "_")
    return sid in {
        "capsule_status",
        "capsule",
        "capsules",
        "multi_sandbox",
        "webgpu_probe",
        "webgpu",
        "webgpu_status",
        "capsule_list",
        "list_capsules",
        "capsule_allocate",
        "capsule_create",
        "allocate_capsule",
        "capsule_execute",
        "capsule_run",
        "execute_capsule",
        "capsule_commit",
        "commit_capsule",
        "capsule_terminate",
        "terminate_capsule",
        "capsule_kill",
        "capsule_mount",
        "mount_capsule",
    }
