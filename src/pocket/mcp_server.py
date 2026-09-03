"""POCKET MCP server — stdio JSON-RPC for agents (Grok/Claude/Cursor).

Run:
  PYTHONPATH=src python -m pocket.mcp_server

Every request/response is mirrored to the Live MCP JSON-RPC Protocol Stream:
  GET /v1/mcp/stream
  GET /v1/mcp/stream/page
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
                            "prompt": {"type": "string"},
                            "goal": {"type": "string"},
                            "to": {"type": "string"},
                            "from": {"type": "string"},
                            "engine": {"type": "string"},
                            "use": {"type": "string"},
                            "server": {"type": "string"},
                            "tool": {"type": "string"},
                            "params": {"type": "object"},
                            "principal": {"type": "string"},
                            "owner": {"type": "string"},
                            "team_id": {"type": "string"},
                            "id": {"type": "string"},
                            "agent": {"type": "string"},
                            "experiments": {"type": "integer"},
                            "cycles": {"type": "integer"},
                        },
                    },
                }
            )
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
    try:
        from pocket.mcp_fifty import _tool_meta

        for t in _tool_meta():
            if not t.get("universal"):
                continue
            tools.append(
                {
                    "name": t["id"],
                    "description": f"UNIVERSAL MCP: {t['desc']}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "prompt": {"type": "string"},
                            "goal": {"type": "string"},
                            "name": {"type": "string"},
                            "tool": {"type": "string"},
                            "params": {"type": "object"},
                        },
                    },
                }
            )
    except Exception:
        pass
    tools.append(
        {
            "name": "mcp_catalog",
            "description": "List 3 internal + 7 external embedded MCPs",
            "inputSchema": {"type": "object", "properties": {}},
        }
    )
    tools.append(
        {
            "name": "mcp_stream",
            "description": "Live MCP JSON-RPC protocol stream (poll frames)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "after": {"type": "integer"},
                    "limit": {"type": "integer"},
                    "format": {"type": "string"},
                },
            },
        }
    )
    return tools


def _call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    from pocket.mcp_bundle import invoke, catalog

    args = arguments or {}
    if name == "mcp_catalog":
        return catalog()
    if name == "mcp_stream":
        from pocket.mcp_stream import list_frames, snapshot, format_term_view

        fmt = (args.get("format") or "json").lower()
        after = int(args.get("after") or 0)
        limit = int(args.get("limit") or 50)
        if fmt in ("term", "markdown", "md"):
            return {"ok": True, "format": "term", "markdown": format_term_view(after_seq=after, limit=limit)}
        return {
            "ok": True,
            **snapshot(),
            "frames": list_frames(after_seq=after, limit=limit),
        }
    if name == "mcp_invoke":
        return invoke(
            args.get("server") or "pocket",
            args.get("tool") or "screen_status",
            **(args.get("params") if isinstance(args.get("params"), dict) else {}),
        )
    if name.startswith("pocket_"):
        tool = name[len("pocket_") :]
        return invoke("pocket", tool, **args)
    try:
        from pocket.mcp_fifty import known

        if known(name):
            return invoke("universal", name, **args)
    except Exception:
        pass
    return {"ok": False, "error": f"unknown tool {name}"}


def _respond(msg_id: Any, result: Any = None, error: Any = None, *, method: str = "") -> None:
    out: Dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    try:
        from pocket.mcp_stream import emit_frame

        emit_frame(
            direction="out",
            method=method or "response",
            msg_id=msg_id,
            payload=result if error is None else None,
            error=error,
            channel="stdio",
        )
    except Exception:
        pass
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

        try:
            from pocket.mcp_stream import emit_frame

            emit_frame(
                direction="in",
                method=method,
                msg_id=mid,
                payload=msg,
                channel="stdio",
            )
        except Exception:
            pass

        if method == "initialize":
            _respond(
                mid,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "pocket", "version": "3.6.0"},
                },
                method="initialize",
            )
        elif method == "notifications/initialized":
            try:
                from pocket.mcp_stream import emit_frame

                emit_frame(
                    direction="internal",
                    method="notifications/initialized",
                    msg_id=mid,
                    payload={"ok": True},
                    channel="stdio",
                )
            except Exception:
                pass
            continue
        elif method == "tools/list":
            _respond(mid, {"tools": _tools_list()}, method="tools/list")
        elif method == "tools/call":
            name = params.get("name") or ""
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
                    method=f"tools/call:{name}",
                )
            except Exception as e:
                _respond(mid, error={"code": -32000, "message": str(e)}, method=f"tools/call:{name}")
        elif method == "ping":
            _respond(mid, {}, method="ping")
        else:
            if mid is not None:
                _respond(
                    mid,
                    error={"code": -32601, "message": f"Method not found: {method}"},
                    method=method,
                )


if __name__ == "__main__":
    main()
