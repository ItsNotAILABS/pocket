"""POCKET Phone — simplified mobile web app for agentic day ops.

Coding · planning · real-world tasks on the go. Uses same auth + sessions API.
Does not expose founder personal disk to market seats.
"""

PHONE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1"/>
<meta name="theme-color" content="#050508"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="mobile-web-app-capable" content="yes"/>
<meta name="description" content="POCKET Phone — Aria, assistant, Working, Muse, Auro · same-WiFi IoT · pairs with desk"/>
<link rel="manifest" href="/phone/manifest.webmanifest"/>
<title>POCKET · Phone</title>
<script src="/auth/client.js"></script>
<style>
:root{
  --bg:#06060a;--panel:#121218;--panel2:#1a1a22;--line:rgba(255,255,255,.08);
  --text:#e8e8ed;--muted:#8b8b98;--fg:#fafafa;--accent:#10a37f;--accent2:#34d399;
  --violet:#a78bfa;--blue:#60a5fa;--amber:#fbbf24;--red:#f87171;
  --safe-b:env(safe-area-inset-bottom,0px);--safe-t:env(safe-area-inset-top,0px);
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --ease:cubic-bezier(.22,1,.36,1);--t:180ms var(--ease);
  --glow:0 0 0 1px rgba(16,163,127,.25),0 8px 24px rgba(16,163,127,.15);
}
.top,.composer,.dock,.tabbar{
  backdrop-filter:blur(22px) saturate(1.3);
  -webkit-backdrop-filter:blur(22px) saturate(1.3)
}
.modes button{transition:transform var(--t),background var(--t),border-color var(--t),color var(--t),box-shadow var(--t)}
.modes button:active{transform:scale(.96)}
.chat{scroll-behavior:smooth;-webkit-overflow-scrolling:touch}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0}
body{
  font-family:var(--font);
  background:radial-gradient(800px 400px at 50% -10%,rgba(16,163,127,.08),transparent 50%),var(--bg);
  color:var(--text);overflow:hidden;-webkit-font-smoothing:antialiased;color-scheme:dark;
  padding:var(--safe-t) 0 0;letter-spacing:-.01em
}
button,input,textarea{font:inherit;color:inherit}
button{cursor:pointer;border:0;background:none}
button:disabled{opacity:.4}
.app{display:flex;flex-direction:column;height:100dvh;height:100vh;max-width:520px;margin:0 auto;position:relative}
.face-ribbon{flex:0 0 auto;display:flex;align-items:center;gap:8px;padding:6px 14px;font-size:10px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;border-bottom:1px solid var(--line)}
.face-ribbon.owner{background:rgba(234,179,8,.16);color:#fbbf24}
.face-ribbon.seat{background:rgba(16,163,127,.14);color:#6ee7b7}
.face-ribbon.local{background:rgba(255,255,255,.04);color:var(--muted)}
.face-ribbon a{color:inherit;margin-left:auto}
.top{
  flex:0 0 auto;display:flex;align-items:center;gap:10px;padding:12px 16px 10px;
  border-bottom:1px solid var(--line);background:rgba(6,6,10,.9);backdrop-filter:blur(20px) saturate(1.15);z-index:5
}
.brand{display:flex;align-items:center;gap:9px;font-weight:750;letter-spacing:-.04em;color:var(--fg);font-size:15px}
.mark{
  width:30px;height:30px;border-radius:10px;display:grid;place-items:center;font-size:13px;font-weight:800;color:#041;
  background:linear-gradient(145deg,#34d399,var(--accent),#0a7a5f);
  box-shadow:0 0 0 1px rgba(16,163,127,.4),0 6px 20px rgba(16,163,127,.25)
}
.chip{font-size:10px;font-weight:650;padding:4px 9px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:rgba(255,255,255,.02)}
.chip.on{color:#6ee7b7;border-color:rgba(16,163,127,.45);background:rgba(16,163,127,.12)}
.grow{flex:1}
/* Aether hardware card — paper-thin hybrid E-Ink aesthetic */
.hw-card{
  margin:10px 14px 0;padding:12px 14px;border-radius:16px;
  border:1px solid rgba(148,163,184,.25);
  background:linear-gradient(160deg,rgba(248,250,252,.08),rgba(15,23,42,.9) 40%,rgba(6,8,12,.98));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 8px 28px rgba(0,0,0,.35)
}
.hw-card .hw-title{font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#94a3b8;margin-bottom:8px}
.hw-card .hw-row{display:grid;grid-template-columns:72px 1fr;gap:6px 10px;font-size:12px;line-height:1.35;margin:0 0 6px}
.hw-card .hw-row:last-child{margin:0}
.hw-card .hw-k{color:#64748b;font-weight:700;font-size:10px;letter-spacing:.04em;text-transform:uppercase;padding-top:2px}
.hw-card .hw-v{color:#e2e8f0;font-weight:600;letter-spacing:-.02em}
.hw-card .hw-v small{display:block;font-weight:500;color:#94a3b8;font-size:11px;margin-top:2px}
.icon-btn{
  width:42px;height:42px;border-radius:13px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),transparent),var(--panel);
  color:var(--text);font-size:16px;transition:all var(--t)
}
.icon-btn:active{transform:scale(.96)}
.modes{
  flex:0 0 auto;display:flex;gap:8px;padding:12px 14px 8px;overflow-x:auto;scrollbar-width:none;
  -webkit-overflow-scrolling:touch
}
.modes::-webkit-scrollbar{display:none}
.modes button{
  flex:0 0 auto;padding:10px 15px;border-radius:999px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.03),transparent),var(--panel);
  color:var(--muted);font-size:12.5px;font-weight:650;white-space:nowrap;transition:all var(--t)
}
.modes button.on{color:#041;background:linear-gradient(180deg,#34d399,var(--accent));border-color:transparent;box-shadow:var(--glow)}
.modes button.novae{border-color:rgba(167,139,250,.35);color:#c4b5fd}
.modes button.novae.on{background:linear-gradient(135deg,#7c3aed,#10a37f);color:#fff;box-shadow:0 4px 16px rgba(124,58,237,.3)}
.modes button.voice{border-color:rgba(11,132,254,.4);color:#7dd3fc}
.modes button.voice.on{background:linear-gradient(135deg,#0b84fe,#10a37f);color:#fff;box-shadow:0 4px 16px rgba(11,132,254,.3)}
.modes button.work{border-color:rgba(244,114,182,.4);color:#f9a8d4}
.modes button.work.on{background:linear-gradient(135deg,#db2777,#10a37f);color:#fff;box-shadow:0 4px 16px rgba(219,39,119,.3)}
.modes button.assist{border-color:rgba(45,212,191,.4);color:#5eead4}
.modes button.assist.on{background:linear-gradient(135deg,#0d9488,#10a37f);color:#fff;box-shadow:0 4px 16px rgba(13,148,136,.3)}
.modes button.muse{border-color:rgba(168,85,247,.45);color:#d8b4fe}
.modes button.muse.on{background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff}
.hw-card.collapsed .hw-row{display:none}
.hw-card .hw-toggle{float:right;font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:8px;padding:3px 8px}
.iot-scan-spin{opacity:.7}
.composer .row textarea{transition:min-height .15s ease}
.mic{
  width:50px;height:50px;border-radius:15px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.04),transparent),var(--panel);
  color:var(--text);font-size:18px;flex:0 0 auto;transition:all var(--t)
}
.mic.live{background:rgba(11,132,254,.22);border-color:rgba(11,132,254,.55);color:#7dd3fc;box-shadow:0 0 0 4px rgba(11,132,254,.15)}
.mic.voice-mode{border-color:rgba(16,163,127,.45)}
.pair-ok{color:#6ee7b7!important;border-color:rgba(16,163,127,.45)!important;background:rgba(16,163,127,.12)!important}
.fusion-chip{font-size:10px;color:#a5b4fc;border:1px solid rgba(167,139,250,.35);border-radius:999px;padding:2px 8px;margin-left:4px;background:rgba(167,139,250,.08)}
.voice-hint{font-size:11px;color:var(--muted);padding:0 6px 8px;line-height:1.4}
.composer .row{align-items:flex-end}
.chat{
  flex:1;min-height:0;overflow:auto;padding:14px 16px 18px;
  display:flex;flex-direction:column;gap:12px;-webkit-overflow-scrolling:touch
}
.empty{margin:auto;text-align:center;padding:28px 18px;color:var(--muted);max-width:340px}
.empty h2{margin:0 0 10px;color:var(--fg);font-size:22px;font-weight:750;letter-spacing:-.04em}
.empty p{margin:0;font-size:14px;line-height:1.55}
.quick{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:18px}
.quick button{
  border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.04),transparent),var(--panel);
  color:var(--text);border-radius:999px;padding:9px 14px;font-size:12.5px;font-weight:600;transition:all var(--t)
}
.quick button:active{transform:scale(.97)}
.bubble{max-width:92%;animation:rise .32s var(--ease) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.bubble.user{align-self:flex-end}
.bubble.agent{align-self:flex-start}
.bubble .body{
  padding:13px 15px;border-radius:18px;font-size:15.5px;line-height:1.5;white-space:pre-wrap;word-break:break-word
}
.bubble.user .body{
  background:linear-gradient(145deg,#0b84fe,#0066d6);border:0;color:#fff;
  border-bottom-right-radius:6px;box-shadow:0 4px 16px rgba(11,132,254,.25)
}
.bubble.agent .body{background:transparent;padding:4px 2px;color:var(--text)}
.bubble.agent .meta{font-size:11px;color:var(--muted);margin-bottom:4px;display:flex;align-items:center;gap:6px}
.bubble.agent .body pre,.bubble.agent .body code{font-family:var(--mono);font-size:12.5px}
.bubble.agent .body pre{
  background:#0a0a0c;border:1px solid var(--line);border-radius:10px;padding:10px;overflow:auto;max-height:240px;color:#b7f0c6
}
/* Thinking animation */
.think{
  align-self:flex-start;display:flex;align-items:center;gap:10px;padding:8px 4px;
  color:var(--muted);font-size:12.5px;font-weight:500
}
.think-orb{
  width:28px;height:28px;border-radius:50%;position:relative;
  background:radial-gradient(circle at 35% 35%,#6ee7b7,var(--accent) 45%,#0a7a5f 80%);
  box-shadow:0 0 0 0 rgba(16,163,127,.45);animation:pulse 1.4s ease-in-out infinite
}
.think-orb::after{
  content:"";position:absolute;inset:-4px;border-radius:50%;
  border:2px solid transparent;border-top-color:var(--violet);border-right-color:var(--accent2);
  animation:spin 1s linear infinite
}
.think-dots span{
  display:inline-block;width:5px;height:5px;margin:0 2px;border-radius:50%;background:var(--accent2);
  animation:dot 1.2s ease-in-out infinite
}
.think-dots span:nth-child(2){animation-delay:.15s}
.think-dots span:nth-child(3){animation-delay:.3s}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(16,163,127,.4);transform:scale(1)}50%{box-shadow:0 0 0 10px rgba(16,163,127,0);transform:scale(1.05)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes dot{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}
.composer{
  flex:0 0 auto;padding:10px 14px calc(12px + var(--safe-b));
  border-top:1px solid var(--line);background:rgba(6,6,10,.94);backdrop-filter:blur(18px) saturate(1.1)
}
.composer .row{display:flex;gap:8px;align-items:flex-end}
.composer textarea{
  flex:1;min-height:48px;max-height:120px;resize:none;border-radius:16px;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.03),transparent),var(--panel);
  padding:13px 15px;font-size:16px;line-height:1.4;outline:none;transition:border-color var(--t),box-shadow var(--t)
}
.composer textarea:focus{border-color:rgba(16,163,127,.5);box-shadow:0 0 0 3px rgba(16,163,127,.15)}
.send{
  width:50px;height:50px;border-radius:15px;
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;font-weight:800;font-size:16px;
  box-shadow:0 4px 16px rgba(16,163,127,.3);transition:transform var(--t)
}
.send:active{transform:scale(.95)}
.nav{
  flex:0 0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2px;
  padding:8px 10px calc(10px + var(--safe-b));border-top:1px solid var(--line);
  background:rgba(8,8,12,.98)
}
.nav button{padding:8px 4px;border-radius:14px;color:var(--muted);font-size:10px;font-weight:650;transition:all var(--t)}
.nav button span{display:block;font-size:18px;margin-bottom:3px}
.nav button.on{color:var(--accent2);background:rgba(16,163,127,.12)}
/* gate */
.gate{
  position:fixed;inset:0;z-index:50;display:flex;align-items:flex-end;justify-content:center;
  background:rgba(0,0,0,.72);backdrop-filter:blur(8px);padding:16px
}
.gate.hidden{display:none}
.gate .card{
  width:100%;max-width:400px;background:var(--panel);border:1px solid var(--line);
  border-radius:20px 20px 16px 16px;padding:22px 18px calc(18px + var(--safe-b))
}
.gate h2{margin:0 0 6px;font-size:22px;color:var(--fg);letter-spacing:-.04em;font-weight:750}
.gate p{margin:0 0 14px;font-size:13.5px;color:var(--muted);line-height:1.5}
.gate label{display:block;font-size:10.5px;font-weight:700;color:var(--muted);margin:12px 0 5px;text-transform:uppercase;letter-spacing:.05em}
.gate input{
  width:100%;padding:13px 15px;border-radius:13px;border:1px solid var(--line);background:#0a0a0e;font-size:16px
}
.gate .primary{
  width:100%;margin-top:16px;padding:15px;border-radius:13px;
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;font-weight:750;font-size:15px;
  box-shadow:0 4px 20px rgba(16,163,127,.3)
}
.gate .err{color:var(--red);font-size:12.5px;margin-top:10px;min-height:1.2em}
.sheet{
  position:fixed;inset:0;z-index:40;display:none;align-items:flex-end;background:rgba(0,0,0,.6);backdrop-filter:blur(6px)
}
.sheet.open{display:flex}
.sheet .panel{
  width:100%;max-width:520px;margin:0 auto;
  background:linear-gradient(180deg,rgba(255,255,255,.03),transparent 30%),var(--panel);
  border-radius:22px 22px 0 0;padding:16px 16px calc(18px + var(--safe-b));max-height:72dvh;overflow:auto;
  border:1px solid var(--line);box-shadow:0 -12px 40px rgba(0,0,0,.4)
}
.sheet h3{margin:0 0 12px;font-size:15px;color:var(--fg);font-weight:750;letter-spacing:-.02em}
.novae-card{
  border:1px solid var(--line);border-radius:16px;padding:14px;margin-bottom:10px;
  background:linear-gradient(165deg,rgba(255,255,255,.03),transparent 50%),#0c0c12
}
.novae-card b{display:block;color:var(--fg);font-size:14.5px;font-weight:700;letter-spacing:-.02em}
.novae-card small{color:var(--muted);font-size:12px;line-height:1.45}
.novae-card .row{display:flex;gap:8px;margin-top:12px}
.novae-card .row button{
  flex:1;padding:11px;border-radius:11px;border:1px solid var(--line);font-weight:650;font-size:12.5px;
  background:rgba(255,255,255,.02)
}
.novae-card .row button.go{
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;border:0;box-shadow:0 4px 14px rgba(16,163,127,.25)
}
/* IoT device cards — shared desk/phone registry on same Wi‑Fi */
.iot-dev{
  display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)
}
.iot-dev:last-child{border-bottom:0}
.iot-ico{
  width:36px;height:36px;border-radius:11px;display:grid;place-items:center;font-size:15px;
  background:rgba(255,255,255,.04);border:1px solid var(--line);flex:0 0 auto
}
.iot-dev .iot-body{flex:1;min-width:0}
.iot-dev .iot-body b{display:block;font-size:13px;color:var(--fg);font-weight:700;letter-spacing:-.02em}
.iot-dev .iot-body small{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.iot-dev .iot-state{
  font-size:10px;font-weight:750;padding:4px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted)
}
.iot-dev .iot-state.on{color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.12)}
.iot-dev .iot-state.off{color:#fca5a5;border-color:rgba(248,113,113,.35);background:rgba(248,113,113,.08)}
.iot-dev .iot-tog{
  border:1px solid rgba(16,163,127,.35);background:rgba(16,163,127,.12);color:#6ee7b7;
  border-radius:9px;padding:7px 10px;font-size:11px;font-weight:700
}
.iot-lan{
  margin-top:8px;padding:8px 10px;border-radius:10px;background:rgba(16,163,127,.08);
  border:1px solid rgba(16,163,127,.22);font-size:11.5px;color:#a7f3d0;line-height:1.4;word-break:break-all
}
.toast{
  position:fixed;left:50%;bottom:calc(96px + var(--safe-b));transform:translateX(-50%);
  background:rgba(26,26,34,.96);border:1px solid var(--line);color:var(--fg);padding:11px 16px;border-radius:14px;
  font-size:13px;font-weight:550;z-index:60;opacity:0;pointer-events:none;transition:opacity .25s var(--ease);max-width:90%;
  backdrop-filter:blur(12px);box-shadow:0 8px 28px rgba(0,0,0,.4)
}
.toast.show{opacity:1}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
}
</style>
</head>
<body>
<div class="app">
  <div class="face-ribbon local" id="faceRibbon">POCKET · <a href="/which">two products</a></div>
  <header class="top">
    <div class="brand"><div class="mark">P</div><span id="brandName">POCKET</span></div>
    <span class="chip on" id="modeChip" title="Active agent">Aria</span>
    <span class="chip" id="pairChip" title="Desk pair status">Unpaired</span>
    <span class="chip" id="hostChip" title="Host path" style="max-width:7.5rem;overflow:hidden;text-overflow:ellipsis">…</span>
    <div class="grow"></div>
    <span class="chip" id="userChip">…</span>
    <button class="icon-btn" type="button" onclick="openSheet()" title="More" aria-label="More">☰</button>
  </header>

  <div class="hw-card collapsed" id="hwCard" aria-label="Device hardware">
    <div class="hw-title">POCKET Phone · Aether <button type="button" class="hw-toggle" onclick="toggleHwCard()">Details</button></div>
    <div class="hw-row">
      <div class="hw-k">Processor</div>
      <div class="hw-v">Aether Neural Core ANC-1<small>Dedicated Tensor processing cluster</small></div>
    </div>
    <div class="hw-row">
      <div class="hw-k">Display</div>
      <div class="hw-v">6.7″ Paper-thin Hybrid E-Ink<small>Readable · low power · always-on glance</small></div>
    </div>
  </div>

  <div class="modes" id="modes" role="tablist">
    <button type="button" class="voice on" data-mode="voice" onclick="pickMode(this)">Aria</button>
    <button type="button" class="assist" data-mode="assist" onclick="pickMode(this)">Assistant</button>
    <button type="button" class="work" data-mode="work" onclick="pickMode(this)">Working</button>
    <button type="button" class="muse" data-mode="muse_spark" onclick="pickMode(this)">Muse Spark</button>
    <button type="button" data-mode="auro" onclick="pickMode(this)">Auro</button>
    <button type="button" data-mode="plan" onclick="pickMode(this)">Plan</button>
    <button type="button" data-mode="codex" onclick="pickMode(this)">Codex</button>
    <button type="button" data-mode="grok" onclick="pickMode(this)">Grok</button>
    <button type="button" data-mode="genetic" onclick="pickMode(this)">Genetic</button>
    <button type="button" data-mode="web" onclick="pickMode(this)">Web</button>
    <button type="button" class="novae" data-mode="novae_grok" onclick="pickMode(this)">Grok Novae</button>
    <button type="button" class="novae" data-mode="novae_codex" onclick="pickMode(this)">Codex Novae</button>
  </div>

  <main class="chat" id="chat" aria-live="polite">
    <div class="empty" id="empty">
      <div class="mark" style="margin:0 auto 14px">P</div>
      <h2>Your host co‑pilot</h2>
      <p><b style="color:var(--fg)">Aria</b> · <b style="color:var(--fg)">Assist</b> · <b style="color:var(--fg)">Working</b> · Muse · Auro. Pair the desk for handoffs. Agents run on the PC — never auto‑pay.</p>
      <div class="quick">
        <button type="button" onclick="pickModeBtn('voice');quick('Hey Aria — help me with my day')">Talk to Aria</button>
        <button type="button" onclick="pickModeBtn('assist');quick('Plan my morning with three priorities')">Quick assist</button>
        <button type="button" onclick="pickModeBtn('work');quick('Reserve dinner Friday 7pm for 2')">Life ops</button>
        <button type="button" onclick="openPairSheet()">Pair desk</button>
        <button type="button" onclick="openSheet();setTimeout(discoverIot,200)">Scan Wi‑Fi</button>
      </div>
    </div>
  </main>

  <div class="composer">
    <div class="voice-hint" id="voiceHint">Aria · hold 🎙 to talk · Assist is snappy life help</div>
    <div class="row">
      <button class="mic voice-mode" id="micBtn" type="button" title="Microphone" onclick="toggleMic()" disabled>🎙</button>
      <textarea id="input" rows="1" placeholder="Talk or type… Aria · Assist · Working · Muse · Auro" disabled></textarea>
      <button class="send" id="sendBtn" type="button" disabled onclick="sendMsg()">↑</button>
    </div>
  </div>

  <nav class="nav" aria-label="Phone nav">
    <button type="button" class="on" id="navChat" onclick="focusChat()"><span>💬</span>Chat</button>
    <button type="button" id="navVoice" onclick="pickModeBtn('voice')"><span>🎙</span>Aria</button>
    <button type="button" id="navAssist" onclick="pickModeBtn('assist')"><span>✦</span>Assist</button>
    <button type="button" id="navWork" onclick="pickModeBtn('work')"><span>⚡</span>Work</button>
    <button type="button" onclick="openSheet()"><span>⚙</span>More</button>
  </nav>
</div>

<div class="gate" id="gate">
  <div class="card">
    <h2 id="phoneAuthTitle">Unlock phone</h2>
    <p id="gateHint">Same seat as the desk — pair with a desk code, then sign in. New? Sign up. Works on LAN or <b style="color:var(--fg)">pocket.medinatechlabs.net</b>.</p>
    <label>Pair code (from desk → Workspace → Get pair code)</label>
    <input id="gatePairCode" autocomplete="one-time-code" placeholder="6-char code" style="text-transform:uppercase;letter-spacing:.12em"/>
    <button class="primary" type="button" id="gatePairBtn" style="margin-top:10px;background:var(--panel2);color:var(--fg);border:1px solid var(--line)">Pair with desk</button>
    <button class="primary" type="button" id="gateSeatBtn" style="margin-top:8px;display:none">Continue as linked phone</button>
    <div class="tabs" style="display:flex;gap:6px;margin:14px 0 10px">
      <button type="button" class="on" id="phoneTabLogin">Sign in</button>
      <button type="button" id="phoneTabSignup">Sign up</button>
    </div>
    <div id="phoneLoginPane">
      <label>Username</label>
      <input id="loginUser" autocomplete="username" placeholder="your username"/>
      <label>Password</label>
      <input id="loginPass" type="password" autocomplete="current-password"/>
      <button class="primary" type="button" id="loginBtn">Sign in</button>
    </div>
    <div id="phoneSignupPane" style="display:none">
      <label>Username</label>
      <input id="regUser" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="pick a username"/>
      <label>Password (min 8)</label>
      <input id="regPass" type="password" autocomplete="new-password"/>
      <label>Confirm password</label>
      <input id="regPass2" type="password" autocomplete="new-password"/>
      <label>Invite (optional)</label>
      <input id="regInvite" autocomplete="off" placeholder="pk_seat_… if you have one"/>
      <label style="display:flex;gap:8px;align-items:flex-start;margin-top:8px;text-transform:none;letter-spacing:0"><input type="checkbox" id="regTerms"/> I accept the terms</label>
      <button class="primary" type="button" id="regBtn">Create account</button>
    </div>
    <div class="err" id="loginErr"></div>
  </div>
</div>

<div class="sheet" id="sheet" onclick="if(event.target===this)closeSheet()">
  <div class="panel">
    <h3>Phone · pair · voice</h3>
    <div class="novae-card" id="pairCard">
      <b>Pair with desk</b>
      <small id="pairStatus">Get a code on the PC desk (Workspace → Get pair code), enter it here. Seamless handoff + transfers.</small>
      <label style="display:block;font-size:11px;color:var(--muted);margin:10px 0 4px">Pair code</label>
      <input id="pairCodeIn" placeholder="ABCDEF" style="width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:#0a0a0c;font-size:18px;letter-spacing:.15em;text-transform:uppercase"/>
      <div class="row" style="margin-top:10px">
        <button type="button" class="go" onclick="redeemPair()">Pair now</button>
        <button type="button" onclick="refreshPair()">Refresh</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button type="button" onclick="sendPairNote()">Send note to desk</button>
        <button type="button" onclick="unpairDevice()">Unpair</button>
      </div>
    </div>
    <div class="novae-card">
      <b>Voice agents (first-class)</b>
      <small>Aria · patient VAD + Fusion (DFW travel graph). Working · live voice + package handoff on host.</small>
      <div class="row">
        <button type="button" class="go" onclick="pickModeBtn('voice');closeSheet()">Aria</button>
        <button type="button" onclick="pickModeBtn('work');closeSheet()">Working</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button type="button" onclick="fusionDemo()">Fusion demo</button>
        <button type="button" onclick="toggleSpeakReplies()">TTS: <span id="ttsFlag">on</span></button>
      </div>
    </div>
    <div class="novae-card" id="iotCard">
      <b>Home IoT · same Wi‑Fi</b>
      <small id="iotStatus">Phone + desk share one device list on this network.</small>
      <div class="iot-lan" id="iotLanHint" style="display:none"></div>
      <div id="iotList" style="margin-top:8px;font-size:12px;color:var(--muted)"></div>
      <div class="row" style="margin-top:10px">
        <button type="button" class="go" onclick="discoverIot()">Scan Wi‑Fi</button>
        <button type="button" onclick="refreshIot()">Refresh</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button type="button" onclick="seedIot()">Seed rooms</button>
        <button type="button" onclick="addIotDevice()">Add device</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button type="button" onclick="announcePhone()">Register this phone</button>
        <button type="button" onclick="location.href='/studio/voice'">Voice Studio</button>
      </div>
    </div>
    <div class="novae-card">
      <b>Desk · Studio · Phone</b>
      <small>Full desk UI · Product Studio demos · this phone PWA.</small>
      <div class="row">
        <button type="button" class="go" onclick="location.href='/desk'">Desk</button>
        <button type="button" onclick="location.href='/studio'">Studio</button>
        <button type="button" onclick="location.href='/imagine'">Imagine</button>
        <button type="button" onclick="location.href='/bots'">Bots</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button type="button" onclick="location.href='/studio/voice'">Voice Studio</button>
        <button type="button" onclick="location.href='/work'">Work Studio</button>
      </div>
    </div>
    <div id="novaeList"><div class="novae-card"><small>Loading Novae…</small></div></div>
    <div class="novae-card">
      <b>Status</b>
      <small id="statusLine">—</small>
      <small id="fusionLine" style="display:block;margin-top:6px;color:#a5b4fc">Fusion —</small>
      <div class="row">
        <button type="button" onclick="refreshStatus()">Refresh</button>
        <button type="button" onclick="doLogout()">Sign out</button>
      </div>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const $ = id => document.getElementById(id);
let token = localStorage.getItem('pocket_token') || '';
let pairToken = localStorage.getItem('pocket_pair_token') || '';
let pairMeta = {};
try{ pairMeta = JSON.parse(localStorage.getItem('pocket_pair_meta')||'{}')||{}; }catch(_){ pairMeta={}; }
let activeId = null;
let mode = localStorage.getItem('pocket_phone_mode') || 'voice';
let pollTimer = null;
let me = null;
let speakReplies = localStorage.getItem('pocket_phone_tts') !== '0';
let lastSpokenKey = '';
let recog = null;
let micLive = false;
const VOICE_MODES = new Set(['voice','v2v','voice_agent','voice2voice','work','working','live_work']);

function toast(t){
  const el=$('toast'); el.textContent=t; el.classList.add('show');
  setTimeout(()=>el.classList.remove('show'), 2400);
}
function esc(s){
  return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function devicePayload(){
  return {
    kind:'phone',
    label: pairMeta.host_label ? ('Phone · '+pairMeta.host_label) : 'Phone',
    remote:true,
    paired: !!pairToken,
    peer_id: pairMeta.peer_id || '',
    host_node_id: pairMeta.host_node_id || '',
    fusion: true
  };
}
function authHeaders(){
  const h={'Content-Type':'application/json','X-Pocket-Device':'phone'};
  if(token){
    h['Authorization']='Bearer '+token;
    h['X-Pocket-Token']=token;
  }
  if(pairToken) h['X-Pocket-Node-Token']=pairToken;
  return h;
}
async function api(path, opts={}){
  const r = await fetch(path,{...opts, headers:{...authHeaders(), ...(opts.headers||{})}});
  const text = await r.text();
  let j={}; try{ j=text?JSON.parse(text):{}; }catch(_){ j={raw:text}; }
  if(!r.ok) throw new Error(j.error||j.message||('HTTP '+r.status));
  return j;
}

function paintPairChip(){
  const c=$('pairChip');
  if(!c) return;
  if(pairToken){
    c.textContent = pairMeta.host_label ? ('Linked · '+(pairMeta.host_label||'').slice(0,12)) : 'Linked';
    c.classList.add('pair-ok','on');
  } else {
    c.textContent='Unpaired';
    c.classList.remove('pair-ok','on');
  }
  const ps=$('pairStatus');
  if(ps){
    ps.textContent = pairToken
      ? ('Paired as '+(pairMeta.peer_id||'peer')+' → host '+(pairMeta.host_label||pairMeta.host_node_id||'desk')+'. Voice + Fusion share this host.')
      : 'Get a code on the PC desk (Workspace → Get pair code), enter it here. Seamless handoff + transfers.';
  }
  const tf=$('ttsFlag'); if(tf) tf.textContent = speakReplies ? 'on' : 'off';
}

function unlockUi(){
  $('gate').classList.add('hidden');
  $('input').disabled=false;
  $('sendBtn').disabled=false;
  const mic=$('micBtn'); if(mic) mic.disabled=false;
  paintPairChip();
  updateVoiceHint();
  try{ announcePhone(); }catch(_){}
  try{ refreshIot(); }catch(_){}
}

function phoneHostHint(){
  const h = (location.hostname||'').toLowerCase();
  const remote = h.includes('medinatech') || h.includes('trycloudflare') || h.includes('cloudflare');
  const lan = /^(192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.)/.test(h);
  const el = $('gateHint');
  const hc = $('hostChip');
  if(hc){
    hc.textContent = remote ? 'tunnel' : (lan ? 'LAN' : (h==='127.0.0.1'||h==='localhost' ? 'local' : h.slice(0,14)));
    hc.classList.toggle('on', true);
    hc.title = location.origin + '/phone';
  }
  if(el){
    if(remote){
      el.innerHTML = 'You are on the <b style="color:var(--fg)">public tunnel</b> ('+h+'). Pair with a desk code from the PC, then sign in — agents run on the host.';
    }else if(lan){
      el.innerHTML = 'Same Wi‑Fi as the desk ('+h+'). Pair for handoff + IoT, then sign in for agents.';
    }else{
      el.innerHTML = 'Same seat as the desk — pair with a desk code, then sign in for agents. Also works at <b style="color:var(--fg)">https://pocket.medinatechlabs.net/phone</b>.';
    }
  }
  return {remote, lan, host:h};
}

async function tryMe(){
  paintPairChip();
  phoneHostHint();
  try{
    me = await api('/v1/auth/me');
    const u = me && (me.user || (me.ok!==false && me.display));
    if(u || (me && me.user)){
      const user = me.user || me;
      $('userChip').textContent = (user.display || user.user || 'signed in');
      $('userChip').classList.add('on');
      try{
        const users = String(location.port||'')==='8788';
        const ribbon=$('faceRibbon');
        const brand=$('brandName');
        if(users){
          if(brand) brand.textContent='POCKET for Users';
          if(ribbon){ ribbon.className='face-ribbon seat'; ribbon.innerHTML='Users product · :8788 · <a href="/which">two products</a>'; }
          document.title='POCKET for Users · Phone';
        }else{
          if(brand) brand.textContent='POCKET Owner';
          if(ribbon){ ribbon.className='face-ribbon owner'; ribbon.innerHTML='Owner · :8787 · <a href="/which">two products</a>'; }
          document.title='POCKET Owner · Phone';
        }
      }catch(_){}
      unlockUi();
      await refreshStatus();
      await loadNovae();
      await refreshPair();
      try{ await refreshIot(); }catch(_){}
      return true;
    }
  }catch(_){}
  // Paired-only soft unlock for transfer UI, but agents still need seat login
  if(pairToken){
    $('userChip').textContent='paired';
    paintPairChip();
  }
  $('gate').classList.remove('hidden');
  if(!token) $('userChip').textContent = pairToken ? 'pair · sign in' : 'signed out';
  return false;
}

function setPhoneAuthTab(t){
  const join=t==='register';
  const tl=$('phoneTabLogin'), tr=$('phoneTabSignup');
  if(tl) tl.classList.toggle('on', !join);
  if(tr) tr.classList.toggle('on', join);
  const lp=$('phoneLoginPane'), rp=$('phoneSignupPane');
  if(lp) lp.style.display=join?'none':'block';
  if(rp) rp.style.display=join?'block':'none';
  const title=$('phoneAuthTitle');
  if(title) title.textContent=join?'Create your account':'Unlock phone';
  if($('loginErr')) $('loginErr').textContent='';
}
if($('phoneTabLogin')) $('phoneTabLogin').onclick=()=>setPhoneAuthTab('login');
if($('phoneTabSignup')) $('phoneTabSignup').onclick=()=>setPhoneAuthTab('register');
async function phoneSignup(){
  if($('loginErr')) $('loginErr').textContent='Creating account…';
  try{
    let res;
    if(window.PocketAuth && PocketAuth.register){
      res=await PocketAuth.register({
        user:($('regUser')&&$('regUser').value)||'',
        password:($('regPass')&&$('regPass').value)||'',
        password2:($('regPass2')&&$('regPass2').value)||'',
        invite:($('regInvite')&&$('regInvite').value)||'',
        accepted_terms:!!($('regTerms')&&$('regTerms').checked),
        device:'phone',
        channel:'public'
      });
      if(!res.ok) throw new Error(res.error||'Sign up failed');
      token=res.token||'';
    }else{
      throw new Error('Sign-up client missing — refresh');
    }
    if(token) localStorage.setItem('pocket_token', token);
    try{ sessionStorage.setItem('pocket_token', token); }catch(_){}
    if($('loginErr')) $('loginErr').textContent='';
    toast('Account ready');
    await tryMe();
    showEmpty();
  }catch(e){
    if($('loginErr')) $('loginErr').textContent=e.message||String(e);
  }
}
if($('regBtn')) $('regBtn').onclick=phoneSignup;
async function phonePasswordLogin(){
  $('loginErr').textContent='Signing in…';
  try{
    let u=($('loginUser').value||'').trim();
    const p=$('loginPass').value||'';
    let res;
    if(window.PocketAuth && PocketAuth.login){
      res=await PocketAuth.login(u, p, {device:'phone'});
      if(!res.ok) throw new Error(res.error||'Login failed');
      token=res.token||'';
    }else{
      const j=await fetch('/v1/auth/login',{
        method:'POST',
        credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-Pocket-Device':'phone'},
        body:JSON.stringify({username:u,user:u,password:p,remember:true})
      }).then(r=>r.json());
      if(!j.ok && !j.token && !j.session_token) throw new Error(j.error||'Login failed');
      token=j.token||j.session_token||j.access_token||'';
    }
    if(token) localStorage.setItem('pocket_token', token);
    try{ sessionStorage.setItem('pocket_token', token); }catch(_){}
    $('loginErr').textContent='';
    toast(pairToken ? 'Unlocked + desk paired' : 'Unlocked');
    await tryMe();
    showEmpty();
  }catch(e){
    $('loginErr').textContent=e.message||String(e);
  }
}
$('loginBtn').onclick = phonePasswordLogin;
if($('loginPass')) $('loginPass').addEventListener('keydown', e=>{ if(e.key==='Enter'){ e.preventDefault(); phonePasswordLogin(); }});
if($('loginUser')) $('loginUser').addEventListener('keydown', e=>{ if(e.key==='Enter'){ e.preventDefault(); ($('loginPass')||{}).focus&&$('loginPass').focus(); }});
try{ if(window.PocketAuth && PocketAuth.wantsJoinTab && PocketAuth.wantsJoinTab()) setPhoneAuthTab('register'); }catch(_){}

async function seatFromPair(){
  if(!pairToken){ toast('Pair with desk first'); return; }
  try{
    const j = await fetch('/v1/node/pair-login',{
      method:'POST',
      headers:{'Content-Type':'application/json','X-Pocket-Device':'phone','X-Pocket-Node-Token':pairToken},
      body:JSON.stringify({pair_token:pairToken})
    }).then(r=>r.json());
    if(!j.ok || !(j.token||j.session_token)) throw new Error(j.error||'Seat unlock failed');
    token = j.token || j.session_token || '';
    localStorage.setItem('pocket_token', token);
    toast(j.message||'Seat unlocked');
    if($('loginErr')) $('loginErr').textContent='';
    await tryMe();
    showEmpty();
  }catch(e){
    if($('loginErr')) $('loginErr').textContent=e.message||String(e);
    toast(e.message||'Seat unlock failed');
  }
}
function paintSeatBtn(){
  const b=$('gateSeatBtn');
  if(!b) return;
  b.style.display = pairToken ? 'block' : 'none';
}
async function redeemPair(codeOpt){
  const code = String(codeOpt || ($('pairCodeIn')&&$('pairCodeIn').value) || ($('gatePairCode')&&$('gatePairCode').value) || '').trim().toUpperCase();
  if(!code){ toast('Enter pair code from desk'); return; }
  try{
    const j = await fetch('/v1/node/redeem',{
      method:'POST',
      headers:{'Content-Type':'application/json','X-Pocket-Device':'phone'},
      body:JSON.stringify({code, label:'phone', peer_label:'POCKET Phone'})
    }).then(r=>r.json());
    if(!j.ok) throw new Error(j.error||'Pair failed');
    pairToken = j.pair_token || '';
    pairMeta = {
      peer_id: j.peer_id,
      host_node_id: j.host_node_id,
      host_fingerprint: j.host_fingerprint,
      host_label: j.host_label || 'desk',
      paired_at: Date.now()
    };
    localStorage.setItem('pocket_pair_token', pairToken);
    localStorage.setItem('pocket_pair_meta', JSON.stringify(pairMeta));
    paintPairChip();
    paintSeatBtn();
    toast('Paired with '+(pairMeta.host_label||'desk'));
    if($('loginErr')) $('loginErr').textContent='';
    // Soft presence ping
    try{ await fetch('/v1/node/hello').then(r=>r.json()); }catch(_){}
    await refreshPair();
    // One-tap seat: auto unlock after successful pair
    try{ await seatFromPair(); }catch(_){}
  }catch(e){
    if($('loginErr')) $('loginErr').textContent=e.message||String(e);
    toast(e.message||'Pair failed');
  }
}
if($('gatePairBtn')) $('gatePairBtn').onclick=()=>redeemPair();
if($('gateSeatBtn')) $('gateSeatBtn').onclick=()=>seatFromPair();
paintSeatBtn();

function unpairDevice(){
  pairToken=''; pairMeta={};
  localStorage.removeItem('pocket_pair_token');
  localStorage.removeItem('pocket_pair_meta');
  paintPairChip();
  toast('Unpaired');
}

async function refreshPair(){
  paintPairChip();
  try{
    const h = await fetch('/v1/node/hello').then(r=>r.json());
    if(h && h.ok && $('pairStatus') && pairToken){
      $('pairStatus').textContent = 'Paired → '+(pairMeta.host_label||h.label||'host')+' · node '+(h.node_id||'').slice(0,12)+' · transfers ok';
    }
  }catch(_){}
  try{
    if(token || pairToken){
      const st = await api('/v1/node/status');
      if(st && st.me && $('statusLine')){
        /* keep health line; pair info in pairStatus */
      }
    }
  }catch(_){}
}

async function sendPairNote(){
  const text = prompt('Note to desk tray:','From phone: ');
  if(text==null||!String(text).trim()) return;
  try{
    await api('/v1/node/offer',{method:'POST',body:JSON.stringify({
      name:'phone-note.txt',
      text:String(text),
      note:'phone',
      to_peer:''
    })});
    toast('Note queued for desk');
  }catch(e){ toast(e.message||'Need sign-in + pair'); }
}

function openPairSheet(){
  openSheet();
  const el=$('pairCodeIn'); if(el) el.focus();
}

function isVoiceMode(){ return VOICE_MODES.has(String(mode||'').toLowerCase()) || mode==='work' || mode==='working'; }
function isAssistMode(){ return mode==='assist' || mode==='assistant' || mode==='digital'; }
function toggleHwCard(){
  const c=$('hwCard'); if(!c) return;
  c.classList.toggle('collapsed');
  const b=c.querySelector('.hw-toggle');
  if(b) b.textContent=c.classList.contains('collapsed')?'Details':'Hide';
}

function updateVoiceHint(){
  const h=$('voiceHint');
  const mic=$('micBtn');
  if(!h) return;
  if(mode==='voice'||mode==='v2v'||mode==='voice_agent'){
    h.textContent = 'Aria · 🎙 talk · Fusion · pairs with desk';
    if(mic){ mic.classList.add('voice-mode'); mic.disabled=false; }
  } else if(mode==='work'||mode==='working'){
    h.textContent = 'Working · life ops + voice · package → handoff';
    if(mic){ mic.classList.add('voice-mode'); mic.disabled=false; }
  } else if(isAssistMode()){
    h.textContent = 'Assist · fast life help · research · plans · life ops on host';
    if(mic){ mic.classList.remove('voice-mode'); }
  } else if(mode==='muse_spark'||mode==='auro'){
    h.textContent = mode==='auro'?'Auro · local meaning (fast) · native with “native …”':'Muse Spark · multi-lane reasoning';
    if(mic) mic.classList.remove('voice-mode');
  } else {
    h.textContent = 'Type a task · 🎙 dictation · Aria / Assist / Working first-class';
    if(mic) mic.classList.remove('voice-mode');
  }
  document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('on'));
  if(mode==='voice'){ const n=$('navVoice'); if(n) n.classList.add('on'); }
  else if(mode==='work'){ const n=$('navWork'); if(n) n.classList.add('on'); }
  else if(isAssistMode()){ const n=$('navAssist'); if(n) n.classList.add('on'); }
  else { const n=$('navChat'); if(n) n.classList.add('on'); }
}

function pickMode(btn){
  document.querySelectorAll('.modes button').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
  mode = btn.dataset.mode || 'voice';
  try{ localStorage.setItem('pocket_phone_mode', mode); }catch(_){}
  $('modeChip').textContent = btn.textContent.trim();
  activeId = null;
  updateVoiceHint();
  showEmpty();
}
function pickModeBtn(m){
  const b=document.querySelector('.modes button[data-mode="'+m+'"]');
  if(b) pickMode(b);
}
function focusChat(){ $('input').focus(); const n=$('navChat'); document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('on')); if(n) n.classList.add('on'); }
function openSheet(){ $('sheet').classList.add('open'); loadNovae(); refreshStatus(); refreshPair(); refreshIot(); }
function closeSheet(){ $('sheet').classList.remove('open'); }

function showEmpty(){
  const chat=$('chat');
  const voice = isVoiceMode();
  const title = modeLabel();
  let blurb = 'Send a message. Agents work on the lab host.';
  let q = '';
  if(mode==='voice'||mode==='v2v'){
    blurb = 'Aria · patient listening + Fusion. Pair desk for handoff.';
    q = `<button type="button" onclick="quick('Hey Aria, who are you?')">Meet Aria</button>
      <button type="button" onclick="quick('My flight is delayed and I need the hotel to hold my room')">DFW delay</button>
      <button type="button" onclick="toggleMic()">🎙 Talk</button>
      <button type="button" onclick="openPairSheet()">Pair desk</button>`;
  } else if(mode==='work'){
    blurb = 'Working · buy · reserve · real tools on the board. Best when paired.';
    q = `<button type="button" onclick="quick('Reserve dinner Friday 7pm for 2')">Reserve</button>
      <button type="button" onclick="quick('Buy noise-cancelling headphones under $100')">Buy research</button>
      <button type="button" onclick="toggleMic()">🎙 Talk</button>`;
  } else if(isAssistMode()){
    blurb = 'Fast digital assistant — plans, research, life ops on this host.';
    q = `<button type="button" onclick="quick('Plan my morning with three priorities')">Morning plan</button>
      <button type="button" onclick="quick('Research weekend trip ideas under budget')">Research</button>
      <button type="button" onclick="quick('Draft a short email to reschedule Tuesday')">Email draft</button>
      <button type="button" onclick="location.href='/work'">Work Studio</button>`;
  } else if(mode==='muse_spark'){
    blurb = 'Muse Spark · multi-lane reasoning on host.';
    q = `<button type="button" onclick="quick('Muse Spark: compare local coding agent desks')">Compare desks</button>
      <button type="button" onclick="quick('open meta')">Open meta.ai</button>`;
  } else if(mode==='auro'){
    blurb = 'Auro · fast meaning model · prefix native for full LMR.';
    q = `<button type="button" onclick="quick('Explain local language models simply')">Explain LLMs</button>
      <button type="button" onclick="quick('status')">Status</button>`;
  } else {
    q = `<button type="button" onclick="quick('What should I do next? Be concrete.')">Next step</button>
      <button type="button" onclick="quick('Break this into a 5-step plan')">5-step plan</button>
      <button type="button" onclick="ensureSession()">Start ${esc(title)}</button>
      <button type="button" onclick="pickModeBtn('assist')">Assist</button>`;
  }
  chat.innerHTML=`<div class="empty" id="empty">
    <div class="mark" style="margin:0 auto 14px">P</div>
    <h2>${esc(title)}${voice?' <span class="fusion-chip">Fusion</span>':''}</h2>
    <p>${esc(blurb)}</p>
    <div class="quick">${q}</div>
  </div>`;
}
function modeLabel(){
  return ({
    voice:'Aria', v2v:'Aria', voice_agent:'Aria', voice2voice:'Aria',
    work:'Working', working:'Working',
    assist:'Assistant', assistant:'Assistant', digital:'Assistant',
    muse_spark:'Muse Spark', muse:'Muse Spark',
    auro:'Auro', auro14b:'Auro',
    plan:'Plan',codex:'Codex',grok:'Grok',novae_grok:'Grok Novae',novae_codex:'Codex Novae',
    genetic:'Genetic', genetic_flow:'Genetic', internal:'Genetic',
    web:'Web',offload:'Real-world',claude:'Claude',build:'Build'
  }[mode]||mode);
}

function quick(t){
  $('input').value=t;
  $('input').focus();
  if(t.endsWith(': ')||t.endsWith('about: ')) return;
  sendMsg();
}

function phoneSessionTitle(){
  const link = pairMeta.host_label ? (' · '+pairMeta.host_label) : '';
  return modeLabel()+' · phone'+link;
}

async function ensureSession(){
  if(activeId) return activeId;
  if(mode==='novae_grok'||mode==='novae_codex'){
    const id = mode==='novae_grok'?'GROK_NOVAE':'CODEX_NOVAE';
    try{
      const n = await api('/v1/novae/activate',{method:'POST',body:JSON.stringify({id, goal:'phone activate', device:devicePayload()})});
      if(n.session_id){ activeId=n.session_id; return activeId; }
    }catch(e){ toast(e.message); }
  }
  const j = await api('/v1/sessions',{method:'POST',body:JSON.stringify({
    mode,
    title: phoneSessionTitle(),
    device: devicePayload(),
    meta: {
      phone: true,
      paired: !!pairToken,
      peer_id: pairMeta.peer_id || '',
      fusion: isVoiceMode(),
      industry: isVoiceMode() ? 'dfw_airline_hospitality' : ''
    }
  })});
  activeId = j.id || j.session_id;
  return activeId;
}

function thinkingEl(engine){
  const d=document.createElement('div');
  d.className='think'; d.id='thinking';
  d.innerHTML=`<div class="think-orb"></div><span>${esc(engine||mode)} thinking</span><span class="think-dots"><span></span><span></span><span></span></span>`;
  return d;
}

function stripTtsFence(raw){
  return String(raw||'').replace(/```tts[\s\S]*?```/gi,'').replace(/_Fusion[^\n]*/g,'').trim();
}
function extractSpoken(raw){
  const s=String(raw||'');
  const m=s.match(/```tts\n[\s\S]*?\n([\s\S]*?)```/i) || s.match(/```tts\nrate=[^\n]+\npitch=[^\n]+\n([\s\S]*?)```/i);
  if(m) return m[1].trim();
  return stripTtsFence(s).slice(0,480);
}
function speakText(text){
  if(!speakReplies || !text) return;
  try{
    if(!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u=new SpeechSynthesisUtterance(String(text).slice(0,500));
    u.rate = isVoiceMode() ? 0.94 : 1;
    u.pitch = isVoiceMode() ? 1.05 : 1;
    window.speechSynthesis.speak(u);
  }catch(_){}
}
function toggleSpeakReplies(){
  speakReplies=!speakReplies;
  try{ localStorage.setItem('pocket_phone_tts', speakReplies?'1':'0'); }catch(_){}
  const tf=$('ttsFlag'); if(tf) tf.textContent=speakReplies?'on':'off';
  toast('TTS '+(speakReplies?'on':'off'));
}

function formatBody(raw){
  const s=String(raw||'');
  // hide raw tts fence in display; keep fusion footnote subtle
  let display = s.replace(/```tts[\s\S]*?```/gi, '').trim();
  if(s.includes('```')){
    return esc(display).replace(/```(\w*)\n([\s\S]*?)```/g,(_,lang,code)=>'<pre>'+code+'</pre>');
  }
  return esc(display);
}

function toggleMic(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ toast('Speech recognition not available in this browser'); return; }
  if(micLive && recog){
    try{ recog.stop(); }catch(_){}
    micLive=false;
    $('micBtn').classList.remove('live');
    return;
  }
  recog = new SR();
  recog.lang='en-US';
  recog.interimResults=true;
  recog.continuous=false;
  recog.onstart=()=>{ micLive=true; $('micBtn').classList.add('live'); toast(isVoiceMode()?'Listening… Aria':'Dictating…'); };
  recog.onerror=()=>{ micLive=false; $('micBtn').classList.remove('live'); };
  recog.onend=()=>{ micLive=false; $('micBtn').classList.remove('live'); };
  recog.onresult=(ev)=>{
    let interim='', final='';
    for(let i=ev.resultIndex;i<ev.results.length;i++){
      const t=ev.results[i][0].transcript;
      if(ev.results[i].isFinal) final+=t;
      else interim+=t;
    }
    if(interim) $('input').value=interim;
    if(final){
      $('input').value=final.trim();
      if(isVoiceMode() || final.trim().length>1) sendMsg();
    }
  };
  try{ recog.start(); }catch(e){ toast(e.message||'Mic failed'); }
}

async function sendMsg(){
  const text = ($('input').value||'').trim();
  if(!text) return;
  $('input').value='';
  if($('empty')) $('empty').remove();
  const chat=$('chat');
  const u=document.createElement('div');
  u.className='bubble user';
  u.innerHTML=`<div class="body">${esc(text)}</div>`;
  chat.appendChild(u);
  chat.appendChild(thinkingEl(mode));
  chat.scrollTop=chat.scrollHeight;

  // Fast path: Assist uses digital assistant API (snappy plans/research/life ops)
  if(isAssistMode()){
    try{
      const j=await api('/v1/work-studio/assist',{
        method:'POST',
        body:JSON.stringify({text, engine:'auto', voice: !!speakReplies})
      });
      const th=chat.querySelector('.think'); if(th) th.remove();
      const a=document.createElement('div');
      a.className='bubble agent';
      a.innerHTML=`<div class="meta">${esc(j.engine||'assist')}${(j.ms!=null)?(' · '+j.ms+'ms'):''}</div><div class="body">${formatBody(j.reply||'Done.')}</div>`;
      chat.appendChild(a);
      chat.scrollTop=chat.scrollHeight;
      if(speakReplies) try{ speakText(j.reply||''); }catch(_){}
      toast((j.engine||'assist')+(j.ms!=null?(' · '+j.ms+'ms'):''));
    }catch(e){
      const th=chat.querySelector('.think'); if(th) th.remove();
      toast(e.message||'assist failed');
    }
    return;
  }

  try{
    await ensureSession();
  }catch(e){ toast('Start failed: '+e.message); const th=chat.querySelector('.think'); if(th) th.remove(); return; }
  try{
    await api('/v1/sessions/'+activeId+'/messages',{
      method:'POST',
      body:JSON.stringify({
        text,
        device: devicePayload(),
        meta: {
          phone: true,
          voice: isVoiceMode(),
          paired: !!pairToken,
          fusion: isVoiceMode(),
          source: micLive ? 'mic' : 'type'
        }
      })
    });
    // Fire-and-forget Fusion preview for voice (signed-in)
    if(isVoiceMode()){
      try{
        api('/v1/fusion/voice',{method:'POST',body:JSON.stringify({
          text, stress:0.45, expert:'hotel_host', scenario:'patient',
          session_id:'phone-'+(activeId||'x'),
          industry:'dfw_airline_hospitality',
          device: devicePayload()
        })}).then(f=>{
          if(f && f.primary_expert && $('fusionLine')){
            $('fusionLine').textContent = 'Fusion · '+(f.primary_expert)+' · '+(f.pattern||'—')+' · +'+(f.patience_delta_ms||0)+'ms';
          }
        }).catch(()=>{});
      }catch(_){}
    }
    startPoll();
  }catch(e){
    const t=$('thinking'); if(t) t.remove();
    toast(e.message);
  }
}

function startPoll(){
  if(pollTimer) clearInterval(pollTimer);
  pollTimer=setInterval(refreshTranscript, 900);
  refreshTranscript();
}

async function refreshTranscript(){
  if(!activeId) return;
  try{
    const s = await api('/v1/sessions/'+activeId);
    const chat=$('chat');
    const stick = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 100;
    chat.innerHTML='';
    const msgs=s.messages||[];
    if(!msgs.length){ showEmpty(); return; }
    let anyRun=false;
    let lastDone='';
    msgs.forEach(m=>{
      const u=document.createElement('div');
      u.className='bubble user';
      u.innerHTML=`<div class="body">${esc(m.text||'')}</div>`;
      chat.appendChild(u);
      const streaming = m.status==='running'||m.status==='queued';
      if(streaming) anyRun=true;
      if(streaming && !(m.result||m.error)){
        chat.appendChild(thinkingEl(m.engine||s.mode));
      } else if(m.result||m.error||m.status==='done'||m.status==='failed'||m.status==='cancelled'){
        const a=document.createElement('div');
        a.className='bubble agent';
        const raw=m.result||m.error||(m.status==='cancelled'?'Stopped.':'');
        const eng=m.engine||s.mode;
        const fusionNote = /_Fusion/i.test(String(raw)) ? ' · fusion' : '';
        a.innerHTML=`<div class="meta"><span class="chip ${streaming?'on':''}">${esc(eng)}</span> ${esc(m.status||'')}${fusionNote}${m.stream_tokens?(' · ~'+m.stream_tokens+' tok'):''}</div>
          <div class="body">${formatBody(raw)}</div>`;
        chat.appendChild(a);
        if(!streaming && m.status==='done') lastDone = raw;
      }
    });
    if(!anyRun && pollTimer){
      clearInterval(pollTimer); pollTimer=null;
      if(lastDone && isVoiceMode()){
        const key = activeId+':'+(lastDone||'').slice(0,80);
        if(key !== lastSpokenKey){
          lastSpokenKey = key;
          speakText(extractSpoken(lastDone));
        }
      }
    }
    if(stick) chat.scrollTop=chat.scrollHeight;
  }catch(e){ /* keep polling */ }
}

async function fusionDemo(){
  pickModeBtn('voice');
  closeSheet();
  quick('My flight is delayed and I need the hotel to hold my room, then maybe dinner near the airport');
}

function _iotIcon(kind){
  return ({light:'💡',plug:'🔌',climate:'🌡',phone:'📱',desk:'🖥',router:'📡',hub:'🏠',cast:'📺',camera:'📷',lan_device:'📶',lan_host:'🖧'})[kind]||'•';
}
async function announcePhone(){
  try{
    const j = await api('/v1/iot/presence',{method:'POST',body:JSON.stringify({
      label: pairMeta.host_label ? ('Phone · '+pairMeta.host_label) : 'POCKET Phone',
      peer_id: pairMeta.peer_id||'',
      pair_token: pairToken||''
    })});
    toast(j.message||'Phone on home IoT');
    await refreshIot();
  }catch(e){ toast(e.message||'presence failed'); }
}
async function refreshIot(){
  try{
    const j = await api('/v1/iot');
    const st = $('iotStatus');
    const box = $('iotList');
    const lan = $('iotLanHint');
    const phone = j.phone||{};
    if(st){
      const hz = (j.hz||{}).status || '?';
      st.textContent = (j.device_count||0)+' devices · '+esc(j.subnet||'LAN')+' · pair '+(pairToken?'on':'off')+' · HZ '+hz;
    }
    if(lan){
      if(phone.phone_lan){
        lan.style.display='block';
        lan.innerHTML = '<b style="color:#6ee7b7">Same Wi‑Fi URL</b><br>'+esc(phone.phone_lan)+
          '<br><span style="opacity:.85">Open this on your phone while on the house network.</span>';
      } else lan.style.display='none';
    }
    if(box){
      const devs = j.devices||[];
      if(!devs.length){
        box.innerHTML = '<div style="padding:8px 0;line-height:1.45">No devices yet. Tap <b style="color:var(--fg)">Scan Wi‑Fi</b> to find items on this network, or Seed rooms.</div>';
      } else {
        box.innerHTML = devs.slice(0,16).map(d=>{
          const stt = String(d.state|| (d.reachable?'online':'?')).toLowerCase();
          const on = stt==='on'||stt==='online';
          const id = esc(d.id||'');
          return '<div class="iot-dev" data-id="'+id+'">'+
            '<span class="iot-ico">'+_iotIcon(d.kind)+'</span>'+
            '<div class="iot-body"><b>'+esc(d.name||'?')+'</b><small>'+
            esc(d.kind||'')+(d.room?' · '+esc(d.room):'')+(d.address?' · '+esc(d.address):'')+
            '</small></div>'+
            '<span class="iot-state '+(on?'on':(stt==='off'?'off':''))+'">'+esc(stt)+'</span>'+
            (d.kind==='desk'||d.kind==='router'?'':
              '<button type="button" class="iot-tog" data-id="'+id+'">Toggle</button>')+
            '</div>';
        }).join('');
        box.querySelectorAll('.iot-tog').forEach(btn=>{
          btn.onclick=async()=>{
            try{
              await api('/v1/iot/control',{method:'POST',body:JSON.stringify({id:btn.getAttribute('data-id'),action:'toggle'})});
              toast('Toggled');
              await refreshIot();
            }catch(e){ toast(e.message||'control failed'); }
          };
        });
      }
    }
  }catch(e){
    if($('iotStatus')) $('iotStatus').textContent = 'IoT: '+(e.message||e)+' — open phone via same-WiFi URL if needed';
  }
}
async function discoverIot(){
  toast('Scanning Wi‑Fi…');
  try{
    // Presence first so this phone is on the list
    try{ await announcePhone(); }catch(_){}
    const j = await api('/v1/iot/discover',{method:'POST',body:JSON.stringify({deep:false})});
    toast('Found '+(j.found||0)+' · registry '+(j.registry_count||0));
    await refreshIot();
  }catch(e){ toast(e.message||'scan failed'); }
}
async function seedIot(){
  try{
    const j = await api('/v1/iot/devices',{method:'POST',body:JSON.stringify({seed:true})});
    toast('Home ready · '+(j.count||0)+' devices');
    await refreshIot();
  }catch(e){ toast(e.message||'seed failed'); }
}
async function addIotDevice(){
  const name = prompt('Device name','Kitchen light');
  if(!name) return;
  const room = prompt('Room','kitchen')||'';
  const address = prompt('IP on this Wi‑Fi (optional)','')||'';
  try{
    await api('/v1/iot/devices',{method:'POST',body:JSON.stringify({name, kind:'light', room, protocol:'lan', address})});
    toast('Added '+name);
    await refreshIot();
  }catch(e){ toast(e.message||'add failed'); }
}

async function activateNovae(id){
  try{
    const n = await api('/v1/novae/activate',{method:'POST',body:JSON.stringify({id, goal:'phone hands', device:devicePayload()})});
    toast((n.title||id)+' active');
    if(n.mode){
      const b=document.querySelector('.modes button[data-mode="'+n.mode+'"]');
      if(b) pickMode(b);
    }
    if(n.session_id) activeId=n.session_id;
    closeSheet();
  }catch(e){ toast(e.message); }
}

async function loadNovae(){
  const box=$('novaeList');
  if(!box) return;
  try{
    const j = await api('/v1/novae');
    const agents=j.agents||[];
    box.innerHTML='';
    agents.forEach(a=>{
      const el=document.createElement('div');
      el.className='novae-card';
      el.innerHTML=`<b style="color:${esc(a.color||'#a78bfa')}">${esc(a.title||a.id)}</b>
        <small>${esc(a.tagline||'')} · ${a.active?'active':'standby'} · runs ${a.runs||0}</small>
        <div class="row">
          <button type="button" class="go" onclick="activateNovae('${esc(a.id)}')">Activate</button>
          <button type="button" onclick="pickModeBtn('${esc(a.mode)}');closeSheet()">Chat</button>
        </div>`;
      box.appendChild(el);
    });
  }catch(e){
    box.innerHTML='<div class="novae-card"><small>Sign in to load Novae hands.</small></div>';
  }
}

async function refreshStatus(){
  try{
    const h = await fetch('/health').then(r=>r.json());
    const heart = (h.heartbeat&&h.heartbeat.ok)?'heart ok':'heart warm';
    const pair = pairToken ? ' · paired' : '';
    $('statusLine').textContent = `v${h.version||'?'} · ${heart} · ${location.host}${pair}`;
    $('modeChip').classList.add('on');
  }catch(_){
    $('statusLine').textContent='Host unreachable — same Wi‑Fi as lab PC, or tunnel';
  }
  try{
    if(token){
      const f = await api('/v1/fusion/voice');
      if($('fusionLine') && f){
        $('fusionLine').textContent = 'Fusion · '+(f.industry||'dfw')+' · '+(f.version||'1.0')+' · voice metadata → host Deep Fusion';
      }
    }
  }catch(_){
    if($('fusionLine')) $('fusionLine').textContent='Fusion · sign in to query';
  }
}

async function doLogout(){
  try{ await api('/v1/auth/logout',{method:'POST',body:'{}'}); }catch(_){}
  token=''; localStorage.removeItem('pocket_token');
  location.reload();
}

$('input').addEventListener('keydown', e=>{
  if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendMsg(); }
});
$('input').addEventListener('input', function(){
  this.style.height='auto'; this.style.height=Math.min(120, this.scrollHeight)+'px';
});

(async function boot(){
  // Restore mode button
  const b=document.querySelector('.modes button[data-mode="'+mode+'"]');
  if(b){
    document.querySelectorAll('.modes button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    $('modeChip').textContent=b.textContent.trim();
  }
  updateVoiceHint();
  paintPairChip();
  const ok = await tryMe();
  if(ok || $('gate').classList.contains('hidden')) showEmpty();
  else showEmpty();
})();
</script>
</body>
</html>
"""

PHONE_MANIFEST = """{
  "name": "POCKET Phone",
  "short_name": "POCKET",
  "description": "Aria · assistant · Working · Muse · Auro — pairs with desk on pocket.medinatechlabs.net",
  "start_url": "/phone",
  "scope": "/phone",
  "id": "/phone",
  "display": "standalone",
  "display_override": ["standalone", "browser"],
  "background_color": "#050508",
  "theme_color": "#050508",
  "orientation": "portrait-primary",
  "lang": "en",
  "categories": ["productivity", "utilities"],
  "icons": [
    {
      "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 128'%3E%3Crect width='128' height='128' rx='28' fill='%2310a37f'/%3E%3Ctext x='64' y='84' text-anchor='middle' font-size='64' font-family='system-ui' font-weight='800' fill='%23041'%3EP%3C/text%3E%3C/svg%3E",
      "sizes": "128x128",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
"""


def phone_html() -> str:
    return PHONE_HTML


def phone_manifest() -> str:
    return PHONE_MANIFEST


def phone_ready() -> dict:
    """Live readiness for desk + phone (LAN + public tunnel)."""
    out = {
        "ok": True,
        "product": "POCKET Phone",
        "shell_public": True,
        "doctrine": "Phone HTML loads on public domain; agents need login; pair for desk handoff",
        "urls": {},
        "checks": {},
    }
    try:
        from pocket.live import lan_ip

        ip = lan_ip()
    except Exception:
        ip = ""
    out["urls"] = {
        "local": "http://127.0.0.1:8787/phone",
        "lan": f"http://{ip}:8787/phone" if ip else None,
        "remote": "https://pocket.medinatechlabs.net/phone",
        "manifest": "/phone/manifest.webmanifest",
    }
    try:
        from pocket.node_transfer import hello, status as node_status

        out["checks"]["node"] = hello()
        out["checks"]["pair"] = node_status()
    except Exception as e:
        out["checks"]["node_error"] = str(e)[:120]
    try:
        from pocket.iot_home import phone_bridge

        out["checks"]["bridge"] = phone_bridge()
    except Exception as e:
        out["checks"]["bridge_error"] = str(e)[:120]
    out["how"] = [
        "1. Open phone URL (LAN or https://pocket.medinatechlabs.net/phone)",
        "2. Desk → Workspace → Get pair code",
        "3. Phone → enter code → Pair",
        "4. Sign in with seat password for agents",
        "5. Aria / Assist / Working / Muse / Auro",
    ]
    return out
