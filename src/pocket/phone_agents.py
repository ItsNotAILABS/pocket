"""Phone agents: Muse Glimmer open weights + other strong CLIs."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from pocket.phoneai_space import dual_write

OLLAMA_HOST = (os.environ.get("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")
GLIMMER_PULL = "muse-glimmer"
PHONE_SYS = (
    "You are PhoneAI on the user's phone. Short, useful replies for real phone life: "
    "messages, notes, reminders, maps, photos, lists, plans, translations. "
    "Do the thing. 4-8 lines unless they ask for more. No preamble."
)


def _to_wsl(path: str) -> str:
    p = (path or "").replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        return f"/mnt/{p[0].lower()}{p[2:]}"
    return p


def _ollama_bin() -> str:
    return shutil.which("ollama") or str(
        Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"
    )


def ensure_ollama() -> bool:
    try:
        urllib.request.urlopen(OLLAMA_HOST + "/api/tags", timeout=2).read()
        return True
    except Exception:
        b = _ollama_bin()
        if not Path(b).is_file():
            return False
        try:
            subprocess.Popen(
                [b, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            time.sleep(1.4)
            urllib.request.urlopen(OLLAMA_HOST + "/api/tags", timeout=3).read()
            return True
        except Exception:
            return False


def glimmer_model() -> str:
    try:
        raw = urllib.request.urlopen(OLLAMA_HOST + "/api/tags", timeout=5).read()
        names = [str(m.get("name") or "") for m in (json.loads(raw).get("models") or [])]
    except Exception:
        return ""
    for n in names:
        low = n.lower()
        if "glimmer" in low or "muse-spark" in low:
            return n
    return ""


def pull_glimmer_bg() -> None:
    b = _ollama_bin()
    if not Path(b).is_file():
        return
    try:
        subprocess.Popen(
            [b, "pull", GLIMMER_PULL],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        pass


def glimmer_ask(text: str) -> Dict[str, Any]:
    """Meta Muse Glimmer 30B open weights (Apache 2.0) via local Ollama."""
    if not ensure_ollama():
        return {
            "ok": False,
            "engine": "spark",
            "via": "muse-glimmer",
            "error": "Ollama is not running. Install from https://ollama.com/download then: ollama pull muse-glimmer",
        }
    model = glimmer_model()
    if not model:
        pull_glimmer_bg()
        return {
            "ok": False,
            "engine": "spark",
            "via": "muse-glimmer",
            "error": (
                "Pulling Muse Glimmer open weights (~18GB) on this PC. "
                "Need a current Ollama. Then send again."
            ),
            "install": "ollama pull muse-glimmer",
        }
    body = json.dumps(
        {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": PHONE_SYS},
                {"role": "user", "content": (text or "")[:8000]},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_HOST + "/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        reply = str((data.get("message") or {}).get("content") or "").strip()
        return {
            "ok": bool(reply),
            "engine": "spark",
            "via": "muse-glimmer",
            "model": model,
            "reply": reply[-8000:] or "empty glimmer reply",
        }
    except urllib.error.HTTPError as e:
        return {"ok": False, "engine": "spark", "via": "muse-glimmer", "error": f"ollama {e.code}"}
    except Exception as e:
        return {"ok": False, "engine": "spark", "via": "muse-glimmer", "error": str(e)[:200]}


def which_muse() -> str:
    """Muse Code CLI if present (paid Spark). Open weights go through glimmer_ask."""
    for n in ("muse", "muse-code", "muse.exe"):
        w = shutil.which(n) or ""
        if w and "ollama" not in w.lower():
            return w
    wsl = shutil.which("wsl")
    if wsl:
        try:
            r = subprocess.run(
                [wsl, "-e", "bash", "-lc", "export PATH=$HOME/.local/bin:$PATH; command -v muse"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            hit = (r.stdout or "").strip()
            if r.returncode == 0 and hit and "ollama" not in hit.lower():
                return "wsl-muse"
        except Exception:
            pass
    return ""


def spark_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    """Muse Glimmer open weights locally; Muse Code CLI if the paid Spark binary is here."""
    g = glimmer_ask(text)
    if g.get("ok"):
        return g
    muse = which_muse()
    work = cwd or str(Path.home() / ".pocket" / "phoneai_ws")
    Path(work).mkdir(parents=True, exist_ok=True)
    if not muse:
        return g or {
            "ok": False,
            "engine": "spark",
            "via": "muse-glimmer",
            "error": "Muse Glimmer open weights are not ready yet. ollama pull muse-glimmer",
            "install": "ollama pull muse-glimmer",
        }
    prompt = (text or "")[:6000]
    if muse == "wsl-muse":
        wdir = _to_wsl(work)
        cmd = [
            "wsl",
            "-e",
            "bash",
            "-lc",
            f"export PATH=$HOME/.local/bin:$PATH; cd {wdir!s} && muse exec {prompt!r}",
        ]
    else:
        cmd = [muse, "exec", prompt]
    try:
        r = subprocess.run(
            cmd,
            cwd=work,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return {
            "ok": r.returncode == 0,
            "engine": "spark",
            "reply": out[-8000:] or f"muse exit {r.returncode}",
            "via": "muse-code",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "engine": "spark", "error": "Muse Spark timed out"}
    except Exception as e:
        return {"ok": False, "engine": "spark", "error": str(e)[:200]}


def _bin(names: List[str], extra: Optional[List[Path]] = None) -> str:
    for n in names:
        w = shutil.which(n) or ""
        if w.lower().endswith(".ps1"):
            cmd = w[:-4] + ".cmd"
            if os.path.isfile(cmd):
                return cmd
            continue
        if w:
            return w
        cmd = shutil.which(n + ".cmd") or ""
        if cmd:
            return cmd
    npm = Path(os.environ.get("APPDATA") or "") / "npm"
    for n in names:
        for cand in (npm / f"{n}.cmd", npm / n):
            if cand.is_file():
                return str(cand)
    for p in extra or []:
        if p and Path(p).is_file():
            return str(p)
    return ""


def _run(cmd: List[str], *, cwd: str = "", timeout: float = 90, stdin: str = "") -> Dict[str, Any]:
    work = cwd or str(Path.home() / ".pocket" / "phoneai_ws")
    Path(work).mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            cmd,
            cwd=work,
            input=stdin or None,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return {"ok": r.returncode == 0, "reply": out[-8000:] or f"exit {r.returncode}", "returncode": r.returncode}
    except FileNotFoundError:
        return {"ok": False, "error": f"missing {cmd[0]}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def claude_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(["claude"])
    if not b:
        return {"ok": False, "engine": "claude", "error": "Claude Code CLI missing"}
    r = _run([b, "-p", (text or "")[:6000]], cwd=cwd, timeout=90)
    return {"engine": "claude", **r}


def gemini_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(["gemini"])
    if not b:
        return {"ok": False, "engine": "gemini", "error": "Gemini CLI missing"}
    r = _run([b, "-p", (text or "")[:6000]], cwd=cwd, timeout=90)
    return {"engine": "gemini", **r}


def qwen_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    q = _bin(["qwen"], extra=[Path(os.environ.get("APPDATA") or "") / "npm" / "qwen.cmd"])
    if not q:
        return {"ok": False, "engine": "qwen", "error": "Qwen CLI missing"}
    r = _run([q, str(text)[:4000]], cwd=cwd, timeout=60)
    return {"engine": "qwen", **r}


def opencode_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(["opencode"])
    if not b:
        return {"ok": False, "engine": "opencode", "error": "OpenCode CLI missing — npm i -g opencode-ai"}
    r = _run([b, "run", (text or "")[:6000]], cwd=cwd, timeout=120)
    return {"engine": "opencode", **r}


def cursor_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(
        ["cursor-agent", "agent"],
        extra=[
            Path.home() / ".local" / "bin" / "cursor-agent",
            Path.home() / "AppData" / "Local" / "cursor-agent" / "cursor-agent.exe",
        ],
    )
    if not b:
        return {"ok": False, "engine": "cursor", "error": "Cursor Agent CLI missing"}
    r = _run([b, "-p", (text or "")[:6000]], cwd=cwd, timeout=120)
    return {"engine": "cursor", **r}


def aider_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(["aider"])
    if not b:
        return {"ok": False, "engine": "aider", "error": "Aider CLI missing — pip install aider-chat"}
    r = _run(
        [b, "--yes-always", "--no-git", "--message", (text or "")[:4000]],
        cwd=cwd,
        timeout=120,
    )
    return {"engine": "aider", **r}


def copilot_ask(text: str, *, cwd: str = "") -> Dict[str, Any]:
    b = _bin(["copilot"])
    if not b:
        return {"ok": False, "engine": "copilot", "error": "GitHub Copilot CLI missing — npm i -g @github/copilot"}
    r = _run([b, "-p", (text or "")[:6000]], cwd=cwd, timeout=90)
    return {"engine": "copilot", **r}


def spectral_ask(text: str) -> Dict[str, Any]:
    """MESIE spectral lane + local harmonics — short working answer."""
    bits: List[str] = []
    try:
        from pocket.mesie_bridge import mesie_available

        st = mesie_available()
        bits.append(
            f"MESIE {'ready' if st.get('ok') else 'offline'} engines={','.join((st.get('engines') or [])[:6]) or '—'}"
        )
    except Exception as e:
        bits.append(f"MESIE: {e}"[:80])
    s = (text or "pocket")[:400]
    hist = [0] * 26
    for ch in s.lower():
        if "a" <= ch <= "z":
            hist[ord(ch) - 97] += 1
    n = max(sum(hist), 1)
    peak = max(range(26), key=lambda i: hist[i])
    energy = sum(v * v for v in hist) / n
    bits.append(f"Local spectrum peak='{chr(97 + peak)}' energy={energy:.2f} n={n}")
    bits.append("Use this as a fingerprint of the ask; MESIE match/embed if the engine root is on disk.")
    reply = " · ".join(bits)
    dual_write("spectral/last.md", f"# spectral\n\n{s}\n\n{reply}\n", message="spectral note")
    return {"ok": True, "engine": "spectral", "reply": reply}


def physics_ask(text: str) -> Dict[str, Any]:
    """Working physics: parse simple kinematics / constants, else Ghost math."""
    low = (text or "").lower()
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", text or "")[:8]]
    lines = ["Physics agent — compute, don't lecture."]
    if "free fall" in low or "drop" in low:
        g = 9.80665
        t = nums[0] if nums else 1.0
        lines.append(f"Δy = ½gt² = {0.5 * g * t * t:.4f} m for t={t}s (g={g}).")
    elif "kinetic" in low or "½mv" in low or "1/2 m" in low:
        m = nums[0] if len(nums) > 0 else 1
        v = nums[1] if len(nums) > 1 else 1
        lines.append(f"KE = ½mv² = {0.5 * m * v * v:.6g} J (m={m}, v={v}).")
    elif "wavelength" in low or "frequency" in low or "c =" in low:
        c = 299_792_458
        f = nums[0] if nums else 1e9
        lines.append(f"λ = c/f = {c / f:.6g} m (f={f} Hz).")
    else:
        try:
            from pocket.ghost_math import run_ghost

            md, err, _ = run_ghost(text or "phi")
            lines.append((md or err or "ghost")[:900])
        except Exception:
            lines.append("Try: free fall 2s · kinetic 2 10 · wavelength 2.4e9")
    reply = "\n".join(lines)
    dual_write("physics/last.md", reply, message="physics note")
    return {"ok": True, "engine": "physics", "reply": reply}


def agi_ask(text: str) -> Dict[str, Any]:
    """Short, dense, working — Grok one-shot with a tight contract, else local."""
    contract = (
        "You are POCKET AGI on the operator's phone. Reply in 4-8 short lines. "
        "Do the work: next action, file to touch, command to run. No preamble.\n\n"
        f"{text}"
    )
    grok = shutil.which("grok") or str(Path.home() / ".grok" / "bin" / "grok.exe")
    if Path(grok).exists():
        try:
            r = subprocess.run(
                [grok, "--single", contract[:5000], "--max-turns", "3", "--always-approve", "--output-format", "plain"],
                capture_output=True,
                text=True,
                timeout=45,
                encoding="utf-8",
                errors="replace",
            )
            out = (r.stdout or "").strip()
            if out:
                dual_write("agi/last.md", out, message="agi note")
                return {"ok": True, "engine": "agi", "reply": out[-2500:]}
        except Exception:
            pass
    reply = f"Do: {text[:160]}\nNext: write it to explorer+git, then verify.\nStop when one artifact exists."
    dual_write("agi/last.md", reply, message="agi note")
    return {"ok": True, "engine": "agi", "reply": reply}


def generate_image(prompt: str) -> Dict[str, Any]:
    """Generate a still (Imagine composite) and dual-write the path. No cap."""
    from PIL import Image, ImageDraw, ImageFont

    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (12, 14, 22))
    d = ImageDraw.Draw(img)
    for i in range(h):
        c = int(12 + 40 * (i / h))
        d.line([(0, i), (w, i)], fill=(c, 18, 40 + c // 2))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 36)
        fs = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
        fs = font
    title = (prompt or "POCKET")[:48]
    d.text((48, h // 2 - 40), title, fill=(255, 255, 255), font=font)
    d.text((48, h // 2 + 12), "PhoneAI · Imagine", fill=(52, 211, 153), font=fs)
    out_dir = Path.home() / ".pocket" / "imagine" / "composites"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"phone_{int(time.time())}.png"
    fp = out_dir / name
    img.save(fp, "PNG")
    dual_write(f"imagine/{name}.txt", f"{prompt}\n{fp}\n", message="imagine still")
    try:
        from pocket.imagine_studio import compose

        c = compose(mode="clean", image=str(fp), title=title[:40], subtitle="PhoneAI")
    except Exception:
        c = {}
    url = f"/v1/imagine/file?name={name}&kind=composite"
    return {
        "ok": True,
        "engine": "imagine",
        "reply": f"Generated still {name}",
        "image_url": url,
        "path": str(fp),
        "compose": c,
    }


DISPATCH = {
    "spark": spark_ask,
    "glimmer": spark_ask,
    "muse": spark_ask,
    "muse-spark": spark_ask,
    "claude": claude_ask,
    "gemini": gemini_ask,
    "qwen": qwen_ask,
    "opencode": opencode_ask,
    "cursor": cursor_ask,
    "aider": aider_ask,
    "copilot": copilot_ask,
    "spectral": lambda text, cwd="": spectral_ask(text),
    "physics": lambda text, cwd="": physics_ask(text),
    "agi": lambda text, cwd="": agi_ask(text),
    "imagine": lambda text, cwd="": generate_image(text),
    "image": lambda text, cwd="": generate_image(text),
}


def run_agent(engine: str, text: str, *, cwd: str = "") -> Dict[str, Any]:
    fn = DISPATCH.get((engine or "").strip().lower())
    if not fn:
        return {"ok": False, "error": f"unknown engine {engine}"}
    return fn(text, cwd=cwd)
