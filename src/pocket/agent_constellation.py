"""Production agent constellation for the POCKET envelope.

This is a routing registry over existing POCKET/NEXUS capabilities. Agents are
roles with explicit actions and verification responsibilities, not pretend
background processes.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class AgentSpec:
    id: str
    role: str
    actions: tuple[str, ...]
    verifies: tuple[str, ...]
    preferred_lane: str = ""


AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec("architect", "plan and decompose", ("plan", "architecture", "scope"), ("plan_complete", "dependencies")),
    AgentSpec("builder", "implement code and artifacts", ("code", "build", "refactor", "file"), ("changed_files", "compile"), "coding-agent"),
    AgentSpec("tester", "execute deterministic verification", ("test", "lint", "typecheck", "benchmark"), ("tests", "exit_code")),
    AgentSpec("reviewer", "review correctness and regressions", ("review", "diff", "compatibility"), ("findings", "acceptance")),
    AgentSpec("deployer", "package and deploy through adapters", ("package", "deploy", "preview", "release"), ("health", "deployment_receipt")),
    AgentSpec("researcher", "retrieve and synthesize evidence", ("research", "search", "evidence"), ("sources", "artifact")),
    AgentSpec("security", "defensive review and policy", ("security", "threat_model", "dependency_audit"), ("denials", "findings")),
    AgentSpec("model-router", "select model/runtime lane", ("model", "route", "fallback"), ("availability", "capability_match")),
    AgentSpec("memory", "persist durable outcomes and context", ("memory", "context", "recall"), ("tenant_scope", "retention")),
    AgentSpec("device", "operate paired device capabilities", ("device", "screen", "filesystem", "process"), ("device_receipt", "session")),
    AgentSpec("voice", "compile speech into work envelopes", ("voice", "intent", "handoff"), ("transcript", "execution_state")),
)


def roster() -> List[Dict[str, Any]]:
    rows = []
    for agent in AGENTS:
        row = asdict(agent)
        row["actions"] = list(agent.actions)
        row["verifies"] = list(agent.verifies)
        rows.append(row)
    return rows


def route(intent: str) -> Dict[str, Any]:
    low = (intent or "").lower()
    scores = []
    for agent in AGENTS:
        score = sum(3 for action in agent.actions if action in low)
        if agent.id == "builder" and any(x in low for x in ("code", "fix", "make", "create", "build")):
            score += 5
        if agent.id == "tester" and any(x in low for x in ("test", "verify", "lint", "benchmark")):
            score += 5
        if agent.id == "deployer" and any(x in low for x in ("deploy", "publish", "ship", "release")):
            score += 6
        if agent.id == "researcher" and any(x in low for x in ("research", "find", "source")):
            score += 5
        scores.append((score, agent))
    scores.sort(key=lambda x: (-x[0], x[1].id))
    best = scores[0][1]
    return {
        "agent": best.id,
        "role": best.role,
        "verification": list(best.verifies),
        "alternates": [a.id for score, a in scores[1:4] if score > 0],
    }


def execution_team(intent: str) -> List[str]:
    """Return the minimum useful team for an end-to-end work request."""
    primary = route(intent)["agent"]
    team = ["architect", primary]
    low = intent.lower()
    if any(x in low for x in ("code", "build", "fix", "create", "refactor")):
        team += ["tester", "reviewer"]
    if any(x in low for x in ("deploy", "publish", "ship", "release")):
        team += ["deployer"]
    team += ["memory"]
    return list(dict.fromkeys(team))
