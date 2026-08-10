"""POCKET MCP server — stdio JSON-RPC-ish for agents (Grok/Claude/Cursor).

Run:
  PYTHONPATH=src python -m pocket.mcp_server

Exposes pocket + CLI tools without opening user browser tabs.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


def _tools_list() -> list:
    from pocket.mcp_bundle import catalog

    tools = []
    for s in catalog().get("servers") or []:
        if s.get("id") != "pocket":
            continue
        for t in s.get("tools") or []:
            tools.append(
                {
                    "name": f"pocket_{t}",
                    "description": f"POCKET agent tool: {t} — {s.get('blurb')}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string"},
                            "session_id": {"type": "string"},
                            "text": {"type": "string"},
                            "action": {"type": "string"},
                            "name": {"type": "string"},
                            "command": {"type": "string"},
                            "bin": {"type": "string"},
                            "args": {"type": "array", "items": {"type": "string"}},
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                            "kinds": {"type": "array", "items": {"type": "string"}},
                            "title": {"type": "string"},
                            "target": {"type": "string"},
                        },
                    },
                }
            )
    # generic invoke
    tools.append(
        {
            "name": "mcp_invoke",
            "description": "Invoke any embedded MCP (pocket|github|nexus|loom|filesystem|cloudflare-*)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "tool": {"type": "string"},
                    "params": {"type": "object"},
                },
                "required": ["server", "tool"],
            },
        }
    )
    tools.append(
        {
            "name": "mcp_catalog",
            "description": "List 3 internal + 7 external embedded MCPs",
            "inputSchema": {"type": "object", "properties": {}},
        }
    )
    return tools


def _call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.mcp_bundle import invoke, catalog

    args = arguments or {}
    if name == "mcp_catalog":
        return catalog()
    if name == "mcp_invoke":
        return invoke(
            args.get("server") or "pocket",
            args.get("tool") or "screen_status",
            **(args.get("params") if isinstance(args.get("params"), dict) else {}),
        )
    if name.startswith("pocket_"):
        tool = name[len("pocket_") :]
        return invoke("pocket", tool, **args)
    return {"ok": False, "error": f"unknown tool {name}"}


def _respond(msg_id: Any, result: Any = None, error: Any = None) -> None:
    out: Dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        mid = msg.get("id")
        method = msg.get("method") or ""
        params = msg.get("params") or {}

        if method == "initialize":
            _respond(
                mid,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "pocket", "version": "3.3.0"},
                },
            )
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            _respond(mid, {"tools": _tools_list()})
        elif method == "tools/call":
            name = (params.get("name") or "")
            arguments = params.get("arguments") or {}
            try:
                result = _call_tool(name, arguments)
                text = json.dumps(result, indent=2, default=str)[:50000]
                _respond(
                    mid,
                    {
                        "content": [{"type": "text", "text": text}],
                        "isError": not bool(result.get("ok", True)),
                    },
                )
            except Exception as e:
                _respond(mid, error={"code": -32000, "message": str(e)})
        elif method == "ping":
            _respond(mid, {})
        else:
            if mid is not None:
                _respond(mid, error={"code": -32601, "message": f"Method not found: {method}"})


if __name__ == "__main__":
    main()
