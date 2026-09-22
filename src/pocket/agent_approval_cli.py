"""CLI for POCKET agentic approval (POCKET-AGENTIC-APPROVAL/1.0).

Usage:
    PYTHONPATH=src python -m pocket.agent_approval_cli issue --device ID --app ID \\
        --scope SCOPE --capability CAP
    PYTHONPATH=src python -m pocket.agent_approval_cli list
    PYTHONPATH=src python -m pocket.agent_approval_cli approve --code XXXXXX
    PYTHONPATH=src python -m pocket.agent_approval_cli deny --code XXXXXX --reason R
    PYTHONPATH=src python -m pocket.agent_approval_cli revoke --device ID [--app ID]
    PYTHONPATH=src python -m pocket.agent_approval_cli bindings
    PYTHONPATH=src python -m pocket.agent_approval_cli check --device ID --app ID --scope S

Exit 0 on ok, 1 on failure. Output is JSON on stdout.
"""

from __future__ import annotations

import argparse
import json
import sys

from pocket import agent_approval as aa


def _emit(res: dict) -> int:
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pocket-approvals",
                                description="Agentic approval: issue/list/approve capability requests")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("issue", help="issue a new approval request (prints the code)")
    pi.add_argument("--device", required=True)
    pi.add_argument("--app", required=True)
    pi.add_argument("--scope", required=True)
    pi.add_argument("--capability", required=True)
    pi.add_argument("--ttl", type=int, default=600)
    pi.add_argument("--requested-by", default="")
    pi.add_argument("--note", default="")
    pi.add_argument("--approvers", default="", help="comma-separated approver allowlist")

    sub.add_parser("list", help="list pending requests (codes masked)")

    pa = sub.add_parser("approve", help="approve a pending request by EXACT code")
    pa.add_argument("--code", required=True)
    pa.add_argument("--approver", default="owner-agent")

    pd = sub.add_parser("deny", help="deny a pending request by EXACT code")
    pd.add_argument("--code", required=True)
    pd.add_argument("--approver", default="owner-agent")
    pd.add_argument("--reason", default="")

    pr = sub.add_parser("revoke", help="revoke binding(s)")
    pr.add_argument("--binding", default="")
    pr.add_argument("--device", default="")
    pr.add_argument("--app", default="")
    pr.add_argument("--approver", default="owner-agent")

    sub.add_parser("bindings", help="list bindings")

    pc = sub.add_parser("check", help="check a live binding")
    pc.add_argument("--device", required=True)
    pc.add_argument("--app", required=True)
    pc.add_argument("--scope", required=True)
    pc.add_argument("--capability", default="")

    a = p.parse_args(argv)
    if a.cmd == "issue":
        approvers = [x.strip() for x in a.approvers.split(",") if x.strip()] or None
        return _emit(aa.issue(device_id=a.device, app_id=a.app, scope=a.scope,
                              capability=a.capability, ttl_s=a.ttl,
                              requested_by=a.requested_by, note=a.note,
                              approvers=approvers))
    if a.cmd == "list":
        return _emit(aa.list_pending())
    if a.cmd == "approve":
        return _emit(aa.approve(code=a.code, approver=a.approver))
    if a.cmd == "deny":
        return _emit(aa.deny(code=a.code, approver=a.approver, reason=a.reason))
    if a.cmd == "revoke":
        return _emit(aa.revoke_binding(binding_id=a.binding, device_id=a.device,
                                       app_id=a.app, approver=a.approver))
    if a.cmd == "bindings":
        return _emit(aa.list_bindings())
    if a.cmd == "check":
        return _emit(aa.check(device_id=a.device, app_id=a.app,
                              scope=a.scope, capability=a.capability))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
