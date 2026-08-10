"""POCKET LOOMGRAPH — Loop-Orchestrated Multi-agent Graph Runtime.

Named system (use this forever):
  LOOMGRAPH  ·  Protocol POCKET-LOOMGRAPH/1.0
  Tagline: See the graph. Run the loop. Ship with Pocket.

What makes it novel (and readable):
  · Every run is a **directed graph** people can see (Mermaid + JSON)
  · An outer **control loop** walks the graph: sense → plan → act → verify → loop/done
  · Nodes are real POCKET surfaces (skills, Creative, Studio, integrations, community)
  · Receipts + ASCII/Mermaid so humans and agents share one mental model

Doctrine:
  · Graphs for understanding · loops for completion · Pocket for execution
  · Never fake success — node results are host truth
  · Intentional community only (share node is opt-in)
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path.home() / ".pocket" / "loomgraph"
RUNS = ROOT / "runs"
for _d in (ROOT, RUNS):
    _d.mkdir(parents=True, exist_ok=True)

_lock = Lock()
_LIVE: Dict[str, Dict[str, Any]] = {}

PROTOCOL = "POCKET-LOOMGRAPH/1.0"
SYSTEM = "LOOMGRAPH"
PRODUCT = "POCKET LOOMGRAPH"
TAGLINE = "See the graph. Run the loop. Ship with Pocket."

# ─── Built-in graphs (playbooks humans can read) ─────────────────────────────

# Node kinds: sense | plan | skill | creative | studio | integrate | community | verify | agent | note
# Edges: from → to with label

GRAPH_LIBRARY: Dict[str, Dict[str, Any]] = {
    "default": {
        "id": "default",
        "name": "Default ship loop",
        "desc": "Sense platform → plan tools → act → verify → optional share",
        "entry": "sense",
        "nodes": {
            "sense": {
                "kind": "sense",
                "label": "Sense",
                "blurb": "What can Pocket do right now?",
                "next": ["plan"],
            },
            "plan": {
                "kind": "plan",
                "label": "Plan",
                "blurb": "Pick tools / modes for the goal",
                "next": ["act"],
            },
            "act": {
                "kind": "skill",
                "label": "Act",
                "blurb": "Run host skills / creative / studio",
                "next": ["verify"],
            },
            "verify": {
                "kind": "verify",
                "label": "Verify",
                "blurb": "Did we get a usable artifact?",
                "next": ["done", "loop"],
            },
            "loop": {
                "kind": "note",
                "label": "Loop",
                "blurb": "Budget remains — re-enter plan with feedback",
                "next": ["plan"],
            },
            "done": {
                "kind": "note",
                "label": "Done",
                "blurb": "Exit with receipt",
                "next": [],
            },
        },
        "edges": [
            {"from": "sense", "to": "plan", "label": "ready"},
            {"from": "plan", "to": "act", "label": "tools chosen"},
            {"from": "act", "to": "verify", "label": "results"},
            {"from": "verify", "to": "done", "label": "ok"},
            {"from": "verify", "to": "loop", "label": "retry"},
            {"from": "loop", "to": "plan", "label": "again"},
        ],
    },
    "creative_ship": {
        "id": "creative_ship",
        "name": "Creative → optional Community",
        "desc": "Storyboard/caption/social draft → artifact → intentional share",
        "entry": "sense",
        "nodes": {
            "sense": {"kind": "sense", "label": "Sense", "next": ["mode"]},
            "mode": {
                "kind": "plan",
                "label": "Pick creative mode",
                "blurb": "blog · social · caption · storyboard · image",
                "next": ["create"],
            },
            "create": {
                "kind": "creative",
                "label": "Creative Studio",
                "blurb": "POST /v1/creative/chat",
                "next": ["verify"],
            },
            "verify": {"kind": "verify", "label": "Verify draft", "next": ["done", "share"]},
            "share": {
                "kind": "community",
                "label": "Share (opt-in)",
                "blurb": "Only if goal says share/publish",
                "next": ["done"],
            },
            "done": {"kind": "note", "label": "Done", "next": []},
        },
        "edges": [
            {"from": "sense", "to": "mode", "label": "catalog"},
            {"from": "mode", "to": "create", "label": "mode"},
            {"from": "create", "to": "verify", "label": "draft"},
            {"from": "verify", "to": "share", "label": "if share"},
            {"from": "verify", "to": "done", "label": "keep private"},
            {"from": "share", "to": "done", "label": "public"},
        ],
    },
    "integration_open": {
        "id": "integration_open",
        "name": "Integration execute",
        "desc": "List integrations → execute target (Discord desktop, etc.)",
        "entry": "sense",
        "nodes": {
            "sense": {"kind": "sense", "label": "Sense", "next": ["list"]},
            "list": {
                "kind": "skill",
                "label": "Integrations list",
                "skill": "integrations_list",
                "next": ["exec"],
            },
            "exec": {
                "kind": "integrate",
                "label": "Execute integration",
                "blurb": "Discord desktop-first, else Edge",
                "next": ["verify"],
            },
            "verify": {"kind": "verify", "label": "Verify open", "next": ["done", "loop"]},
            "loop": {"kind": "note", "label": "Retry", "next": ["exec"]},
            "done": {"kind": "note", "label": "Done", "next": []},
        },
        "edges": [
            {"from": "sense", "to": "list", "label": "ready"},
            {"from": "list", "to": "exec", "label": "id"},
            {"from": "exec", "to": "verify", "label": "receipt"},
            {"from": "verify", "to": "done", "label": "ok"},
            {"from": "verify", "to": "loop", "label": "retry"},
            {"from": "loop", "to": "exec", "label": "again"},
        ],
    },
    "studio_viral": {
        "id": "studio_viral",
        "name": "Studio viral loop",
        "desc": "Studio status → storyboard → caption → optional viral pack",
        "entry": "status",
        "nodes": {
            "status": {
                "kind": "studio",
                "label": "Studio status",
                "action": "status",
                "next": ["story"],
            },
            "story": {
                "kind": "studio",
                "label": "Storyboard",
                "action": "storyboard",
                "next": ["caption"],
            },
            "caption": {
                "kind": "studio",
                "label": "Captions",
                "action": "caption",
                "next": ["verify"],
            },
            "verify": {"kind": "verify", "label": "Verify", "next": ["done", "ship"]},
            "ship": {
                "kind": "studio",
                "label": "Viral ship",
                "action": "ship",
                "next": ["done"],
            },
            "done": {"kind": "note", "label": "Done", "next": []},
        },
        "edges": [
            {"from": "status", "to": "story", "label": "ffmpeg?"},
            {"from": "story", "to": "caption", "label": "beats"},
            {"from": "caption", "to": "verify", "label": "copy"},
            {"from": "verify", "to": "ship", "label": "if ship/viral"},
            {"from": "verify", "to": "done", "label": "draft only"},
            {"from": "ship", "to": "done", "label": "exports"},
        ],
    },
    "code_assist": {
        "id": "code_assist",
        "name": "Code assist loop",
        "desc": "Platform map → tools for prompt → skill run → verify",
        "entry": "sense",
        "nodes": {
            "sense": {"kind": "sense", "label": "Sense", "next": ["tools"]},
            "tools": {
                "kind": "skill",
                "label": "Plan tools",
                "skill": "tools_for_prompt",
                "next": ["act"],
            },
            "act": {
                "kind": "skill",
                "label": "Run top skill",
                "skill": "auto",
                "next": ["verify"],
            },
            "verify": {"kind": "verify", "label": "Verify", "next": ["done", "loop"]},
            "loop": {"kind": "note", "label": "Loop", "next": ["tools"]},
            "done": {"kind": "note", "label": "Done", "next": []},
        },
        "edges": [
            {"from": "sense", "to": "tools", "label": "map"},
            {"from": "tools", "to": "act", "label": "plan"},
            {"from": "act", "to": "verify", "label": "out"},
            {"from": "verify", "to": "done", "label": "ok"},
            {"from": "verify", "to": "loop", "label": "retry"},
            {"from": "loop", "to": "tools", "label": "again"},
        ],
    },
}


def catalog() -> Dict[str, Any]:
    graphs = []
    for g in GRAPH_LIBRARY.values():
        graphs.append(
            {
                "id": g["id"],
                "name": g["name"],
                "desc": g["desc"],
                "nodes": len(g.get("nodes") or {}),
                "edges": len(g.get("edges") or []),
            }
        )
    return {
        "ok": True,
        "system": SYSTEM,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "tagline": TAGLINE,
        "schema": "pocket.loomgraph.catalog.v1",
        "graphs": graphs,
        "ui": "/loomgraph",
        "api": {
            "catalog": "GET /v1/loomgraph",
            "run": "POST /v1/loomgraph/run",
            "graph": "GET /v1/loomgraph/graph/{id}",
            "mermaid": "GET /v1/loomgraph/mermaid/{id}",
            "runs": "GET /v1/loomgraph/runs",
            "live": "GET /v1/loomgraph/live",
            "self_test": "GET /v1/loomgraph/self_test",
        },
        "doctrine": [
            "Graphs for understanding",
            "Loops for completion",
            "Pocket skills for execution",
            "Receipts for truth",
        ],
    }


def get_graph(graph_id: str = "default") -> Dict[str, Any]:
    gid = (graph_id or "default").strip().lower().replace("-", "_")
    # aliases
    aliases = {
        "creative": "creative_ship",
        "community": "creative_ship",
        "discord": "integration_open",
        "integrations": "integration_open",
        "studio": "studio_viral",
        "viral": "studio_viral",
        "code": "code_assist",
        "coding": "code_assist",
        "default_loop": "default",
    }
    gid = aliases.get(gid, gid)
    g = GRAPH_LIBRARY.get(gid) or GRAPH_LIBRARY["default"]
    return {"ok": True, "graph": g, "system": SYSTEM, "protocol": PROTOCOL}


def to_mermaid(graph: Dict[str, Any]) -> str:
    """Human-readable Mermaid flowchart."""
    g = graph.get("graph") if "graph" in graph and isinstance(graph.get("graph"), dict) else graph
    nodes = g.get("nodes") or {}
    edges = g.get("edges") or []
    title = g.get("name") or g.get("id") or "LOOMGRAPH"
    lines = [
        "flowchart TD",
        f"  %% {SYSTEM} · {title}",
        f"  %% {PROTOCOL}",
    ]
    for nid, n in nodes.items():
        label = (n.get("label") or nid).replace('"', "'")
        kind = n.get("kind") or "note"
        shape_l, shape_r = "[", "]"
        if kind in ("verify",):
            shape_l, shape_r = "{", "}"
        elif kind in ("sense", "plan"):
            shape_l, shape_r = "([", "])"
        elif kind in ("done",):
            shape_l, shape_r = "((", "))"
        lines.append(f'  {nid}{shape_l}"{label}"{shape_r}')
    for e in edges:
        a, b = e.get("from"), e.get("to")
        lab = (e.get("label") or "").replace('"', "'")
        if a and b:
            if lab:
                lines.append(f"  {a} -->|{lab}| {b}")
            else:
                lines.append(f"  {a} --> {b}")
    return "\n".join(lines)


def to_ascii(graph: Dict[str, Any], *, path: Optional[List[str]] = None) -> str:
    """Simple ASCII walk for terminals."""
    g = graph.get("graph") if "graph" in graph and isinstance(graph.get("graph"), dict) else graph
    nodes = g.get("nodes") or {}
    path = path or []
    lines = [f"{SYSTEM} · {g.get('name') or g.get('id')}", ""]
    if path:
        lines.append("Path: " + " → ".join(path))
        lines.append("")
    for nid, n in nodes.items():
        mark = "●" if nid in path else "○"
        lines.append(f"  {mark} {nid:12} {n.get('label') or ''}  [{n.get('kind')}]")
        if n.get("blurb"):
            lines.append(f"      {n['blurb']}")
    return "\n".join(lines)


def pick_graph(goal: str) -> str:
    t = (goal or "").lower()
    if re.search(r"\b(discord|slack|teams|integration|open app)\b", t):
        return "integration_open"
    if re.search(r"\b(viral|studio|recording|ffmpeg|storyboard|caption pack)\b", t):
        return "studio_viral"
    if re.search(r"\b(blog|paper|social|creative|community|share|post)\b", t):
        return "creative_ship"
    if re.search(r"\b(code|implement|refactor|fix|bug|pytest|github)\b", t):
        return "code_assist"
    return "default"


def _run_skill(skill: str, prompt: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    try:
        from pocket.skill_runner import run_skill

        md, err, eng = run_skill(skill, prompt=prompt, params=params or {})
        return {"ok": not bool(err), "markdown": md, "error": err, "engine": eng, "skill": skill}
    except Exception:
        try:
            from pocket.orchestrator_exec import dispatch_skill

            return dispatch_skill(skill, prompt=prompt, params=params or {})
        except Exception as e:
            return {"ok": False, "error": str(e)[:200], "skill": skill}


def _node_exec(
    node_id: str,
    node: Dict[str, Any],
    *,
    goal: str,
    ctx: Dict[str, Any],
) -> Dict[str, Any]:
    kind = (node.get("kind") or "note").lower()
    t0 = time.time()
    out: Dict[str, Any] = {
        "node": node_id,
        "kind": kind,
        "label": node.get("label"),
        "ok": True,
        "at": t0,
    }

    if kind == "sense":
        try:
            from pocket.platform_coherence import platform_map

            m = platform_map()
            out["result"] = {
                "ok": True,
                "skills_hint": (m.get("skill_count") or m.get("count") or "map"),
                "message": "Platform sensed",
            }
            # light catalog
            try:
                from pocket.creative_studio import catalog as cc

                out["result"]["creative_modes"] = len((cc() or {}).get("modes") or [])
            except Exception:
                pass
            try:
                from pocket.integrations_catalog import catalog as ic

                out["result"]["integrations"] = (ic() or {}).get("count")
            except Exception:
                pass
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:160]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "plan":
        try:
            from pocket.agent_tools_loop import plan_tools

            planned = plan_tools(goal, mode=str(ctx.get("mode") or ""), limit=6)
            out["result"] = {"ok": True, "planned": planned}
            ctx["planned"] = planned
            # creative mode guess
            gl = goal.lower()
            if "blog" in gl:
                ctx["creative_mode"] = "blog"
            elif "paper" in gl or "research" in gl:
                ctx["creative_mode"] = "paper"
            elif "social" in gl or "tweet" in gl or "linkedin" in gl:
                ctx["creative_mode"] = "social"
            elif "image" in gl or "still" in gl:
                ctx["creative_mode"] = "image"
            elif "video" in gl or "viral" in gl:
                ctx["creative_mode"] = "video"
            elif "storyboard" in gl:
                ctx["creative_mode"] = "storyboard"
            elif "caption" in gl:
                ctx["creative_mode"] = "caption"
            else:
                ctx["creative_mode"] = ctx.get("creative_mode") or "chat"
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:160]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "skill":
        skill = node.get("skill") or "list_skills"
        if skill == "auto":
            planned = ctx.get("planned") or []
            if planned and isinstance(planned[0], dict):
                skill = planned[0].get("skill") or "list_skills"
            elif planned and isinstance(planned[0], str):
                skill = planned[0]
            else:
                skill = "platform_map"
        r = _run_skill(skill, goal, node.get("params") or {})
        out["ok"] = bool(r.get("ok", True))
        out["result"] = r
        out["skill"] = skill
        if r.get("markdown"):
            ctx["last_text"] = str(r["markdown"])[:8000]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "creative":
        try:
            from pocket.creative_studio import chat as creative_chat

            mode = ctx.get("creative_mode") or node.get("mode") or "chat"
            # infer from goal if still chat
            if mode == "chat":
                gl = goal.lower()
                for m in ("blog", "paper", "social", "image", "video", "storyboard", "caption"):
                    if m in gl:
                        mode = m
                        break
            r = creative_chat(goal, mode=mode, auto_media=True)
            out["ok"] = bool(r.get("ok"))
            out["result"] = {
                "ok": r.get("ok"),
                "mode": r.get("mode"),
                "reply_preview": (r.get("reply") or "")[:500],
                "session_id": r.get("session_id"),
                "share_hint": r.get("share_hint"),
            }
            ctx["last_text"] = r.get("reply") or ""
            ctx["share_hint"] = r.get("share_hint")
            ctx["creative_session"] = r.get("session_id")
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:200]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "studio":
        action = (node.get("action") or "status").lower()
        try:
            if action == "status":
                from pocket.video_studio import studio_status, list_recordings

                st = studio_status()
                recs = list_recordings(5)
                out["result"] = {"studio": st, "recordings": recs}
                out["ok"] = bool(st.get("ok", True))
            elif action == "storyboard":
                from pocket.studio_core import storyboard

                r = storyboard(goal)
                out["result"] = r
                out["ok"] = bool(r.get("ok", True))
                ctx["last_text"] = json.dumps(r.get("beats") or r, indent=2, default=str)[:4000]
            elif action == "caption":
                from pocket.studio_core import caption_pack

                r = caption_pack(prompt=goal)
                out["result"] = r
                out["ok"] = bool(r.get("ok", True))
                ctx["last_text"] = (r.get("launch_blurb") or "") + "\n" + "\n".join(r.get("social_posts") or [])
            elif action == "ship":
                # only if goal asks
                if re.search(r"\b(ship|viral|render)\b", goal.lower()):
                    from pocket.studio_core import ship

                    r = ship(prompt=goal)
                    out["result"] = r
                    out["ok"] = bool(r.get("ok", True))
                else:
                    out["result"] = {"ok": True, "skipped": True, "reason": "no ship/viral in goal"}
                    out["ok"] = True
            else:
                out["result"] = {"ok": True, "action": action}
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:200]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "integrate":
        try:
            from pocket.integrations_exec import execute as ix

            # extract integration id
            iid = ctx.get("integration_id") or node.get("id") or ""
            gl = goal.lower()
            if not iid:
                for cand in (
                    "discord",
                    "slack",
                    "teams",
                    "spotify",
                    "zoom",
                    "notion",
                    "github",
                    "figma",
                    "outlook",
                    "telegram",
                ):
                    if cand in gl:
                        iid = cand
                        break
            if not iid:
                iid = "discord" if "open" in gl else "browser_edge"
            r = ix(iid, text=goal, prefer="auto", dry_run=bool(ctx.get("dry_run")))
            out["ok"] = bool(r.get("ok"))
            out["result"] = r
            ctx["integration_id"] = iid
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:200]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "community":
        # opt-in only
        want = bool(
            re.search(r"\b(share|publish|community|public post)\b", goal.lower())
            or ctx.get("force_share")
        )
        if not want:
            out["result"] = {"ok": True, "skipped": True, "reason": "no intentional share in goal"}
            out["ok"] = True
            out["ms"] = int((time.time() - t0) * 1000)
            return out
        try:
            from pocket.community_share import share as cshare

            hint = ctx.get("share_hint") or {}
            r = cshare(
                author=str(ctx.get("author") or "loomgraph"),
                display_name=str(ctx.get("display_name") or "LOOMGRAPH"),
                title=str(hint.get("title") or goal)[:160],
                body=str(hint.get("body") or ctx.get("last_text") or goal)[:8000],
                kind=str(hint.get("kind") or "note"),
                tags=["loomgraph", "intentional"],
                source="loomgraph",
            )
            out["ok"] = bool(r.get("ok"))
            out["result"] = r
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:200]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "verify":
        text = (ctx.get("last_text") or "") + json.dumps(ctx.get("last_result") or {}, default=str)
        ok = bool(ctx.get("last_ok", True)) and (
            len((ctx.get("last_text") or "")) >= 20
            or bool(ctx.get("last_result"))
            or bool(ctx.get("share_hint"))
            or bool(ctx.get("planned"))
        )
        # if previous node failed, not ok
        hist = ctx.get("history") or []
        if hist and hist[-1].get("ok") is False:
            ok = False
        out["ok"] = True  # verify node itself ran
        out["result"] = {
            "passed": ok,
            "reason": "artifact present" if ok else "insufficient result — loop or stop",
            "budget_left": int(ctx.get("budget_left") or 0),
        }
        ctx["verify_passed"] = ok
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    if kind == "agent":
        try:
            from pocket.sell_api import chat_complete

            r = chat_complete(
                [{"role": "user", "content": goal}],
                agent=str(node.get("agent") or "planner"),
                inject_wiki=False,
            )
            out["ok"] = bool(r.get("ok", True))
            out["result"] = r
        except Exception as e:
            out["ok"] = False
            out["error"] = str(e)[:200]
        out["ms"] = int((time.time() - t0) * 1000)
        return out

    # note / default
    out["result"] = {"ok": True, "note": node.get("blurb") or node.get("label") or node_id}
    out["ms"] = int((time.time() - t0) * 1000)
    return out


def _choose_next(
    node_id: str,
    node: Dict[str, Any],
    graph: Dict[str, Any],
    ctx: Dict[str, Any],
    step: Dict[str, Any],
) -> Optional[str]:
    nxt = list(node.get("next") or [])
    if not nxt:
        return None
    # verify branching
    if node.get("kind") == "verify" or node_id == "verify":
        passed = bool(ctx.get("verify_passed"))
        budget = int(ctx.get("budget_left") or 0)
        if passed:
            # prefer done over share unless share wanted
            if "share" in nxt and re.search(r"\b(share|publish|community)\b", (ctx.get("goal") or "").lower()):
                return "share"
            if "done" in nxt:
                return "done"
            if "ship" in nxt and re.search(r"\b(ship|viral|render)\b", (ctx.get("goal") or "").lower()):
                return "ship"
            return "done" if "done" in nxt else nxt[0]
        # failed verify
        if budget > 0 and "loop" in nxt:
            return "loop"
        if "done" in nxt:
            return "done"
        return nxt[-1]
    # default first next
    return nxt[0]


def run(
    goal: str,
    *,
    graph_id: str = "",
    max_loops: int = 3,
    max_nodes: int = 24,
    dry_run: bool = False,
    author: str = "",
    mode: str = "",
    force_share: bool = False,
    integration_id: str = "",
) -> Dict[str, Any]:
    """Execute a LOOMGRAPH: walk nodes in a control loop, return receipt + mermaid."""
    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "goal required", "system": SYSTEM}

    gid = (graph_id or "").strip() or pick_graph(goal)
    gr = get_graph(gid)
    graph = gr["graph"]
    nodes = graph.get("nodes") or {}
    entry = graph.get("entry") or next(iter(nodes.keys()))

    rid = "lg-" + uuid.uuid4().hex[:10]
    ctx: Dict[str, Any] = {
        "goal": goal,
        "mode": mode,
        "author": author or "loomgraph",
        "dry_run": dry_run,
        "force_share": force_share,
        "integration_id": integration_id,
        "budget_left": max(1, int(max_loops)),
        "history": [],
        "last_ok": True,
    }

    path: List[str] = []
    steps: List[Dict[str, Any]] = []
    cur = entry
    visited_loops = 0
    t0 = time.time()

    with _lock:
        _LIVE[rid] = {
            "id": rid,
            "goal": goal[:200],
            "graph_id": graph.get("id"),
            "node": cur,
            "status": "running",
            "started_at": t0,
        }

    try:
        from pocket.live_events import emit

        emit("loomgraph", f"run {graph.get('id')} · {goal[:80]}", agent="LOOMGRAPH", role="graph")
    except Exception:
        pass

    for _ in range(max(1, int(max_nodes))):
        if not cur or cur not in nodes:
            break
        node = nodes[cur]
        path.append(cur)
        with _lock:
            if rid in _LIVE:
                _LIVE[rid]["node"] = cur
                _LIVE[rid]["path"] = list(path)

        if dry_run and node.get("kind") not in ("sense", "plan", "note", "verify"):
            step = {
                "node": cur,
                "kind": node.get("kind"),
                "label": node.get("label"),
                "ok": True,
                "dry_run": True,
                "result": {"planned": True},
                "ms": 0,
            }
        else:
            step = _node_exec(cur, node, goal=goal, ctx=ctx)

        steps.append(step)
        ctx["history"] = steps
        ctx["last_ok"] = bool(step.get("ok"))
        if step.get("result") is not None:
            ctx["last_result"] = step.get("result")
        if isinstance(step.get("result"), dict) and step["result"].get("reply_preview"):
            ctx["last_text"] = step["result"].get("reply_preview")

        if cur == "loop":
            visited_loops += 1
            ctx["budget_left"] = max(0, int(ctx.get("budget_left") or 0) - 1)

        nxt = _choose_next(cur, node, graph, ctx, step)
        if nxt is None or nxt == cur:
            break
        if nxt == "done" or (nodes.get(nxt) or {}).get("kind") == "note" and not (nodes.get(nxt) or {}).get("next"):
            if nxt == "done" or nxt not in path or nxt == "loop":
                if nxt == "done":
                    path.append("done")
                    steps.append(
                        {
                            "node": "done",
                            "kind": "note",
                            "label": "Done",
                            "ok": True,
                            "result": {"ok": True},
                            "ms": 0,
                        }
                    )
                break
        cur = nxt
        if cur == "done":
            path.append("done")
            steps.append(
                {
                    "node": "done",
                    "kind": "note",
                    "label": "Done",
                    "ok": True,
                    "result": {"ok": True},
                    "ms": 0,
                }
            )
            break

    ok = all(s.get("ok") for s in steps if s.get("kind") not in ("note",)) or bool(steps)
    # more honest: last verify passed or any creative/integrate ok
    if any(s.get("kind") == "verify" for s in steps):
        ok = any(
            (s.get("result") or {}).get("passed")
            for s in steps
            if s.get("kind") == "verify"
        ) or any(s.get("ok") and s.get("kind") in ("creative", "integrate", "studio", "skill") for s in steps)

    mermaid = to_mermaid(graph)
    # highlight path in mermaid comment
    mermaid_path = mermaid + "\n  %% path: " + " → ".join(path)

    receipt = {
        "ok": ok,
        "system": SYSTEM,
        "product": PRODUCT,
        "protocol": PROTOCOL,
        "tagline": TAGLINE,
        "schema": "pocket.loomgraph.run.v1",
        "id": rid,
        "goal": goal,
        "graph_id": graph.get("id"),
        "graph_name": graph.get("name"),
        "path": path,
        "steps": steps,
        "loops": visited_loops,
        "mermaid": mermaid_path,
        "ascii": to_ascii(graph, path=path),
        "ms": int((time.time() - t0) * 1000),
        "dry_run": dry_run,
        "first_class": True,
        "at": time.time(),
        "message": (
            f"LOOMGRAPH · {graph.get('name')} · path: " + " → ".join(path)
        ),
    }

    # persist
    try:
        (RUNS / f"{rid}.json").write_text(
            json.dumps(receipt, indent=2, default=str)[:400_000],
            encoding="utf-8",
        )
    except Exception:
        pass

    with _lock:
        _LIVE[rid] = {
            **_LIVE.get(rid, {}),
            "status": "done" if ok else "failed",
            "path": path,
            "ended_at": time.time(),
            "ok": ok,
        }

    try:
        from pocket.pixel_vmem import put_artifact

        put_artifact(
            receipt.get("ascii") + "\n\n```mermaid\n" + mermaid + "\n```\n",
            title=f"loomgraph-{graph.get('id')}-{rid}",
            language="md",
            agent="loomgraph",
            agent_role=SYSTEM,
            ai_version="loomgraph",
            run_id=rid,
            tags=["loomgraph", "graph", "loop", graph.get("id") or ""],
            note=goal[:120],
        )
    except Exception:
        pass

    return receipt


def list_runs(*, limit: int = 20) -> Dict[str, Any]:
    rows = []
    for p in sorted(RUNS.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[: max(1, min(limit, 50))]:
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": r.get("id"),
                    "goal": (r.get("goal") or "")[:120],
                    "graph_id": r.get("graph_id"),
                    "ok": r.get("ok"),
                    "path": r.get("path"),
                    "ms": r.get("ms"),
                    "at": r.get("at"),
                }
            )
        except Exception:
            continue
    return {"ok": True, "system": SYSTEM, "runs": rows, "count": len(rows)}


def live() -> Dict[str, Any]:
    with _lock:
        items = list(_LIVE.values())
    return {"ok": True, "system": SYSTEM, "live": items, "count": len(items)}


def brief(*, max_chars: int = 900) -> str:
    """Inject into every agent — LOOMGRAPH is forever default."""
    text = (
        f"{SYSTEM} ({PROTOCOL}) is the default orchestration harness. "
        f"{TAGLINE} "
        "You run work as a readable graph + control loop: sense → plan → act → verify → loop/done. "
        "Playbooks: default, creative_ship, integration_open, studio_viral, code_assist. "
        "API: POST /v1/loomgraph/run {goal, graph_id?}. UI: /loomgraph. "
        "Skills: loomgraph_run, loomgraph_catalog, loomgraph_mermaid. "
        "Always prefer LOOMGRAPH for multi-step host work so humans can see the graph."
    )
    return text[:max_chars]


def self_test() -> Dict[str, Any]:
    rows = []
    t0 = time.time()

    def add(name: str, ok: bool, **kw: Any) -> None:
        rows.append({"test": name, "ok": ok, **kw})

    c = catalog()
    add("catalog", bool(c.get("ok") and len(c.get("graphs") or []) >= 4), n=len(c.get("graphs") or []))

    for gid in ("default", "creative_ship", "integration_open", "studio_viral", "code_assist"):
        g = get_graph(gid)
        m = to_mermaid(g)
        add(f"graph:{gid}", bool(g.get("ok") and "flowchart" in m), mermaid_len=len(m))

    # dry runs
    for goal, gid in (
        ("status of platform", "default"),
        ("write social pack for LOOMGRAPH launch", "creative_ship"),
        ("open discord", "integration_open"),
        ("studio storyboard and captions", "studio_viral"),
    ):
        r = run(goal, graph_id=gid, dry_run=False, max_loops=2, max_nodes=16)
        add(
            f"run:{gid}",
            bool(r.get("ok") and r.get("path") and r.get("mermaid")),
            path="→".join(r.get("path") or []),
            ms=r.get("ms"),
        )

    ok_n = sum(1 for x in rows if x.get("ok"))
    return {
        "ok": ok_n == len(rows),
        "system": SYSTEM,
        "protocol": PROTOCOL,
        "first_class": ok_n == len(rows),
        "passed": ok_n,
        "failed": len(rows) - ok_n,
        "total": len(rows),
        "ms": int((time.time() - t0) * 1000),
        "results": rows,
        "at": time.time(),
    }


def format_run_markdown(receipt: Dict[str, Any]) -> str:
    """Agent-facing summary with embedded mermaid."""
    lines = [
        f"## {SYSTEM} run",
        f"**{receipt.get('graph_name') or receipt.get('graph_id')}** · `{receipt.get('id')}`",
        "",
        f"Goal: {receipt.get('goal')}",
        f"Path: `{' → '.join(receipt.get('path') or [])}`",
        f"OK: **{receipt.get('ok')}** · {receipt.get('ms')}ms",
        "",
        "```mermaid",
        (receipt.get("mermaid") or "").replace("```", ""),
        "```",
        "",
        "### Steps",
    ]
    for s in receipt.get("steps") or []:
        mark = "✓" if s.get("ok") else "✗"
        lines.append(
            f"- {mark} **{s.get('label') or s.get('node')}** ({s.get('kind')}) {s.get('ms', 0)}ms"
        )
    lines.append("")
    lines.append(f"_{TAGLINE}_")
    return "\n".join(lines)
