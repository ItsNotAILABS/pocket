"""Live MCP JSON-RPC Protocol Stream.

Captures every JSON-RPC frame on the POCKET MCP surface (stdio + in-process invoke)
so desks, phone agents, and operators can watch the protocol live:

  GET  /v1/mcp/stream?after=<seq>
  GET  /v1/mcp/stream/page     — sovereign terminal UI
  skill mcp_stream
  MCP  pocket_mcp_stream

Frame shape (JSON-RPC 2.0 + pocket envelope):
  {
    "jsonrpc": "2.0",
    "seq": 42,
    "dir": "in" | "out" | "internal",
    "channel": "stdio" | "invoke" | "http",
    "method": "tools/call",
    "id": ...,
    "payload": { ... },   # request or result (truncated)
    "ts": "HH:MM:SS",
    "at": 1710000000.0
  }
"""

from __future__ import annotations

import json
import time
import uuid
from collections import deque
from threading import Lock
from typing import Any, Deque, Dict, List, Optional

_lock = Lock()
_FRAMES: Deque[Dict[str, Any]] = deque(maxlen=800)
_SEQ = 0

PRODUCT = "POCKET MCP Protocol Stream"
SCHEMA = "pocket.mcp.stream.v1"
MAX_PAYLOAD = 4000


def _truncate(obj: Any, limit: int = MAX_PAYLOAD) -> Any:
    try:
        s = json.dumps(obj, default=str)
    except Exception:
        s = str(obj)
    if len(s) <= limit:
        try:
            return json.loads(s)
        except Exception:
            return s
    # keep readable head
    return {"_truncated": True, "preview": s[:limit], "bytes": len(s)}


def emit_frame(
    *,
    direction: str,
    method: str = "",
    msg_id: Any = None,
    payload: Any = None,
    channel: str = "invoke",
    error: Any = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Append one live JSON-RPC protocol frame."""
    global _SEQ
    with _lock:
        _SEQ += 1
        frame = {
            "jsonrpc": "2.0",
            "schema": SCHEMA,
            "seq": _SEQ,
            "id": msg_id if msg_id is not None else f"ev-{uuid.uuid4().hex[:8]}",
            "dir": (direction or "internal")[:12],
            "channel": (channel or "invoke")[:16],
            "method": (method or "")[:80],
            "payload": _truncate(payload),
            "error": error,
            "meta": meta or {},
            "at": time.time(),
            "ts": time.strftime("%H:%M:%S"),
            "frame_id": f"mcp-{uuid.uuid4().hex[:10]}",
        }
        _FRAMES.append(frame)
    # also mirror short note to live_events
    try:
        from pocket.live_events import emit

        emit(
            "mcp_rpc",
            f"{direction} {method or 'frame'} #{frame['seq']}",
            agent="MCP",
            role="protocol",
            meta={"seq": frame["seq"], "channel": channel, "method": method},
        )
    except Exception:
        pass
    return frame


def list_frames(*, after_seq: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    with _lock:
        items = [f for f in _FRAMES if int(f.get("seq") or 0) > int(after_seq or 0)]
    return items[-limit:]


def snapshot() -> Dict[str, Any]:
    with _lock:
        recent = list(_FRAMES)[-20:]
        seq = _SEQ
        n = len(_FRAMES)
    return {
        "ok": True,
        "product": PRODUCT,
        "schema": SCHEMA,
        "seq": seq,
        "count": n,
        "recent": recent,
        "api": {
            "poll": "GET /v1/mcp/stream?after=<seq>",
            "page": "GET /v1/mcp/stream/page",
            "clear": "POST /v1/mcp/stream/clear",
        },
        "doctrine": "Live JSON-RPC 2.0 frames for internal MCP — tools/list, tools/call, invoke.",
    }


def clear() -> Dict[str, Any]:
    global _SEQ
    with _lock:
        _FRAMES.clear()
        _SEQ = 0
    return {"ok": True, "cleared": True, "seq": 0}


def format_ndjson(*, after_seq: int = 0, limit: int = 100) -> str:
    """Newline-delimited JSON for stream consumers."""
    frames = list_frames(after_seq=after_seq, limit=limit)
    return "\n".join(json.dumps(f, default=str) for f in frames) + ("\n" if frames else "")


def format_term_view(*, after_seq: int = 0, limit: int = 40) -> str:
    """Human + machine view for sovereign terminal style consumers."""
    frames = list_frames(after_seq=after_seq, limit=limit)
    lines = [
        "# Live MCP JSON-RPC Protocol Stream",
        f"**seq:** {_SEQ} · **frames:** {len(frames)} (showing last {limit})",
        "",
    ]
    for f in frames:
        arrow = "→" if f.get("dir") == "in" else ("←" if f.get("dir") == "out" else "·")
        lines.append(
            f"`{f.get('ts')}` {arrow} **{f.get('method') or f.get('dir')}** "
            f"ch={f.get('channel')} id={f.get('id')} #{f.get('seq')}"
        )
        if f.get("error"):
            lines.append(f"  error: {json.dumps(f.get('error'), default=str)[:200]}")
        elif f.get("payload") is not None:
            prev = json.dumps(f.get("payload"), default=str)[:180]
            lines.append(f"  {prev}")
    payload = {
        "schema": SCHEMA,
        "seq": _SEQ,
        "frames": frames,
    }
    return (
        "\n".join(lines)
        + "\n\n[[POCKET_TERM:mcp_stream]]\n"
        + json.dumps(payload, ensure_ascii=False, default=str)
        + "\n[[/POCKET_TERM]]\n"
    )


def stream_page_html() -> str:
    """Sovereign live terminal page for MCP JSON-RPC."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Live MCP JSON-RPC Stream · POCKET</title>
<meta name="theme-color" content="#050807"/>
<style>
:root{--bg:#050807;--panel:#0b1210;--line:rgba(16,163,127,.28);--fg:#ecfdf5;--muted:#6b7280;--accent:#34d399;--in:#38bdf8;--out:#a3e635;--err:#f87171}
*{box-sizing:border-box}
body{margin:0;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--bg);color:var(--fg);min-height:100vh}
header{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,rgba(16,163,127,.12),transparent)}
header .dots{display:flex;gap:6px}
header .dots i{width:10px;height:10px;border-radius:50%;display:block}
header .dots i:nth-child(1){background:#ff5f57}
header .dots i:nth-child(2){background:#febc2e}
header .dots i:nth-child(3){background:#28c840}
header b{color:var(--accent);letter-spacing:.04em}
header .pill{margin-left:auto;font-size:11px;border:1px solid var(--line);padding:3px 10px;border-radius:999px;color:var(--accent)}
header .pill.live{animation:pulse 1.1s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.meta{display:flex;gap:14px;padding:8px 16px;font-size:11px;color:var(--muted);border-bottom:1px solid rgba(255,255,255,.05)}
.meta span b{color:var(--accent);font-weight:600}
#log{padding:12px 16px 80px;font-size:12px;line-height:1.55;max-height:calc(100vh - 100px);overflow:auto}
.row{margin:0 0 10px;padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,.06);background:var(--panel)}
.row .h{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:4px}
.row .dir{font-weight:700;font-size:11px}
.row .dir.in{color:var(--in)}
.row .dir.out{color:var(--out)}
.row .dir.internal{color:var(--accent)}
.row .method{color:#fde68a}
.row .ts{color:var(--muted);font-size:10.5px}
.row .ch{color:var(--muted);font-size:10.5px}
.row pre{margin:4px 0 0;white-space:pre-wrap;word-break:break-word;color:#86efac;font-size:11px;max-height:120px;overflow:auto}
.row.err pre{color:var(--err)}
.foot{position:fixed;bottom:0;left:0;right:0;padding:8px 16px;background:rgba(5,8,7,.92);border-top:1px solid var(--line);
  display:flex;gap:10px;font-size:11px;color:var(--muted)}
.foot a{color:var(--accent);text-decoration:none}
button{border:1px solid var(--line);background:transparent;color:var(--accent);border-radius:8px;padding:4px 10px;cursor:pointer;font-family:inherit;font-size:11px}
</style>
</head>
<body>
<header>
  <div class="dots" aria-hidden="true"><i></i><i></i><i></i></div>
  <b>wsl · mcp json-rpc</b>
  <span class="pill live" id="livePill">LIVE</span>
</header>
<div class="meta">
  <span>seq <b id="seq">0</b></span>
  <span>frames <b id="count">0</b></span>
  <span>poll 800ms</span>
  <button type="button" onclick="clearStream()">clear</button>
  <a href="/desk" style="color:var(--accent);margin-left:auto;font-size:11px">desk</a>
</div>
<div id="log"></div>
<div class="foot">
  <span>GET /v1/mcp/stream?after=&lt;seq&gt;</span>
  <span>·</span>
  <span>stdio: python -m pocket.mcp_server</span>
  <span>·</span>
  <a href="/v1/agents/tools">agents tools</a>
</div>
<script>
let after = 0;
const log = document.getElementById('log');
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function row(f){
  const d=document.createElement('div');
  const dir=f.dir||'internal';
  d.className='row'+(f.error?' err':'');
  const payload = f.error!=null ? f.error : f.payload;
  let body='';
  try{ body = JSON.stringify(payload, null, 2); }catch(_){ body=String(payload); }
  d.innerHTML=`<div class="h">
    <span class="ts">${esc(f.ts)}</span>
    <span class="dir ${esc(dir)}">${esc(dir==='in'?'→ IN':dir==='out'?'← OUT':'· RPC')}</span>
    <span class="method">${esc(f.method||'—')}</span>
    <span class="ch">#${esc(f.seq)} · ${esc(f.channel)} · id=${esc(f.id)}</span>
  </div>
  <pre>${esc((body||'').slice(0,2500))}</pre>`;
  return d;
}
async function poll(){
  try{
    const r = await fetch('/v1/mcp/stream?after='+after+'&limit=50');
    const j = await r.json();
    document.getElementById('seq').textContent = j.seq||0;
    document.getElementById('count').textContent = j.count||0;
    const frames = j.frames||[];
    if(frames.length){
      const stick = log.scrollHeight - log.scrollTop - log.clientHeight < 80;
      frames.forEach(f=>{
        log.appendChild(row(f));
        after = Math.max(after, f.seq||0);
      });
      // keep DOM bounded
      while(log.children.length > 200) log.removeChild(log.firstChild);
      if(stick) log.scrollTop = log.scrollHeight;
    }
  }catch(e){
    document.getElementById('livePill').textContent = 'OFFLINE';
    document.getElementById('livePill').classList.remove('live');
  }
}
async function clearStream(){
  await fetch('/v1/mcp/stream/clear',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
  log.innerHTML='';
  after=0;
  poll();
}
poll();
setInterval(poll, 800);
</script>
</body>
</html>
"""
