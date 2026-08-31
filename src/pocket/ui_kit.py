"""POCKET Fluid UI kit — one design + motion layer for every HTML surface.

Injected by server._html so Desk, Phone, Studios, Lab, Mail, OS, Docs,
and marketing pages share tokens, View Transitions, command palette,
and spring motion without rewriting each 100KB template.
"""

from __future__ import annotations

KIT_VERSION = "4.1.0"
KIT_CSS_HREF = "/ui/kit.css"
KIT_JS_HREF = "/ui/kit.js"

# ---------------------------------------------------------------------------
# CSS — additive, namespaced where aggressive. Never resets display/grid.
# ---------------------------------------------------------------------------

KIT_CSS = r"""
/* POCKET Fluid 4.0 — shared design + motion across every module */
:root{
  --pk-ease:cubic-bezier(.22,1,.36,1);
  --pk-ease-out:cubic-bezier(.16,1,.3,1);
  --pk-ease-spring:cubic-bezier(.34,1.56,.64,1);
  --pk-t:180ms var(--pk-ease);
  --pk-t-slow:320ms var(--pk-ease-out);
  --pk-glass:rgba(10,10,14,.72);
  --pk-glass-border:rgba(255,255,255,.08);
  --pk-lift:0 18px 48px rgba(0,0,0,.42),0 0 0 1px rgba(255,255,255,.05);
  --pk-glow:0 0 0 1px rgba(16,163,127,.32),0 12px 36px rgba(16,163,127,.16);
  --pk-focus:0 0 0 2px rgba(6,6,10,.9),0 0 0 4px rgba(16,163,127,.55);
  --ease:var(--pk-ease);
  --t:var(--pk-t);
}
html{color-scheme:dark;interpolate-size:allow-keywords}
html,body{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility}
@media (prefers-reduced-motion:no-preference){
  @view-transition{navigation:auto}
  ::view-transition-old(root){animation:pk-vt-out 180ms var(--pk-ease-out) both}
  ::view-transition-new(root){animation:pk-vt-in 280ms var(--pk-ease-out) both}
}
@keyframes pk-vt-out{to{opacity:0;filter:blur(4px);transform:scale(.992)}}
@keyframes pk-vt-in{from{opacity:0;filter:blur(6px);transform:translateY(6px) scale(1.006)}}
@keyframes pk-rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes pk-fade{from{opacity:0}to{opacity:1}}
@keyframes pk-pop{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
@keyframes pk-shimmer{0%{background-position:120% 0}100%{background-position:-120% 0}}
@keyframes pk-pulse{0%,100%{opacity:.45}50%{opacity:1}}
@keyframes pk-bar{0%{transform:translateX(-40%)}100%{transform:translateX(140%)}}

body{letter-spacing:-.011em}
::selection{background:rgba(16,163,127,.38);color:#fafafa}
:focus-visible{outline:none;box-shadow:var(--pk-focus);border-radius:8px}
button,a.btn,.btn,input,textarea,select,.chip,.pill,.icon,.icon-btn{
  transition:background var(--pk-t),border-color var(--pk-t),color var(--pk-t),
    box-shadow var(--pk-t),transform 140ms var(--pk-ease),filter var(--pk-t),opacity var(--pk-t)
}
button:active:not(:disabled),a.btn:active,.btn:active,.icon-btn:active,.modes button:active{
  transform:scale(.975)
}
@media (hover:hover) and (pointer:fine){
  .card:hover,.hab-card:hover,.rec:hover,.preset:hover,.gbtn:hover,.acct:hover{
    border-color:rgba(255,255,255,.16);
    box-shadow:var(--pk-lift);
    transform:translateY(-1px)
  }
}

/* Glass chrome — headers/navs already present */
.pnav,.top,header.top,header.pnav{
  backdrop-filter:blur(22px) saturate(1.35);
  -webkit-backdrop-filter:blur(22px) saturate(1.35)
}
.pnav .links a,.nav a,.top-links a{
  transition:color var(--pk-t),background var(--pk-t),box-shadow var(--pk-t),transform 140ms var(--pk-ease)
}

/* Scrollbars */
*{scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.14) transparent}
*::-webkit-scrollbar{width:8px;height:8px}
*::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:99px;border:2px solid transparent;background-clip:padding-box}
*::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.28);background-clip:padding-box}

/* Primary buttons — keep existing colors, add depth */
.btn.primary,button.primary,a.cta,.pnav .cta,button.btn.p,a.btn.p{
  box-shadow:inset 0 1px 0 rgba(255,255,255,.22),0 8px 22px rgba(16,163,127,.22)
}
.btn.primary:hover,button.primary:hover,a.cta:hover{
  filter:brightness(1.06)
}

/* Inputs */
input,textarea,select{
  transition:border-color var(--pk-t),box-shadow var(--pk-t),background var(--pk-t)
}
input:focus,textarea:focus,select:focus{
  border-color:rgba(16,163,127,.55)!important;
  box-shadow:0 0 0 3px rgba(16,163,127,.16)
}

/* Chat / messages — fluid enter */
.msg,.bubble,.think{animation:pk-rise 320ms var(--pk-ease-out) both}
.msg.user .mb,.bubble.user .body{box-shadow:0 6px 18px rgba(11,132,254,.22)}
.msg.agent .mb{box-shadow:0 6px 18px rgba(0,0,0,.22)}

/* Boot splash polish */
.boot-splash{transition:opacity .45s var(--pk-ease-out),visibility .45s,filter .45s var(--pk-ease-out)!important}
.boot-splash.done{filter:blur(8px)}
.boot-splash .m{animation:pk-pop .5s var(--pk-ease-out) both}

/* Command palette + toast (kit-owned) */
#pk-live-fab{
  position:fixed;right:max(16px,env(safe-area-inset-right));bottom:max(18px,env(safe-area-inset-bottom));
  z-index:3500;width:56px;height:56px;border-radius:18px;border:1px solid rgba(16,163,127,.45);
  background:linear-gradient(145deg,#34d399,#10a37f);color:#042f24;font-weight:800;font-size:18px;
  box-shadow:0 12px 32px rgba(16,163,127,.35);cursor:pointer
}
#pk-live-panel{
  position:fixed;right:max(12px,env(safe-area-inset-right));bottom:max(84px,calc(env(safe-area-inset-bottom) + 72px));
  z-index:3501;width:min(360px,calc(100vw - 24px));height:min(480px,70vh);display:none;flex-direction:column;
  background:#121218;border:1px solid rgba(255,255,255,.12);border-radius:18px;overflow:hidden;
  box-shadow:0 24px 70px #0008
}
#pk-live-panel.open{display:flex}
#pk-live-panel header{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid rgba(255,255,255,.08);font-size:13px;font-weight:700}
#pk-live-panel header small{color:#71717a;font-weight:500;margin-left:8px}
#pk-live-log{flex:1;overflow:auto;padding:10px 12px;font-size:13px;line-height:1.45;color:#e4e4e7}
#pk-live-log .u{color:#6ee7b7;margin:8px 0 2px}
#pk-live-log .a{color:#e4e4e7;white-space:pre-wrap}
#pk-live-form{display:flex;gap:6px;padding:10px;border-top:1px solid rgba(255,255,255,.08)}
#pk-live-form input{flex:1;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#0c0c0e;color:#fafafa;padding:10px}
#pk-live-form button{border:0;border-radius:10px;background:#10a37f;color:#042f24;font-weight:700;padding:0 12px;cursor:pointer}

#pk-cmdk{
  position:fixed;inset:0;z-index:4000;display:none;align-items:flex-start;justify-content:center;
  padding:12vh 16px 24px;background:rgba(4,4,8,.55);backdrop-filter:blur(10px) saturate(1.2)
}
#pk-cmdk.open{display:flex;animation:pk-fade 140ms var(--pk-ease-out)}
#pk-cmdk .pk-box{
  width:min(560px,100%);background:linear-gradient(180deg,rgba(255,255,255,.05),transparent 28%),#121218;
  border:1px solid rgba(255,255,255,.1);border-radius:18px;box-shadow:0 32px 80px rgba(0,0,0,.55);
  overflow:hidden;animation:pk-pop 200ms var(--pk-ease-out)
}
#pk-cmdk input{
  width:100%;border:0;background:transparent;color:#fafafa;padding:16px 18px;font-size:15.5px;outline:none
}
#pk-cmdk .pk-hint{
  display:flex;gap:8px;align-items:center;padding:0 16px 10px;font-size:11px;color:#71717a
}
#pk-cmdk .pk-hint kbd{
  font:600 10px ui-monospace,Menlo,Consolas,monospace;border:1px solid rgba(255,255,255,.12);
  border-radius:5px;padding:1px 5px;color:#a1a1aa
}
#pk-cmdk ul{list-style:none;margin:0;padding:6px;max-height:min(52vh,420px);overflow:auto;border-top:1px solid rgba(255,255,255,.06)}
#pk-cmdk li{
  display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;cursor:pointer;color:#e4e4e7
}
#pk-cmdk li .k{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:#71717a;min-width:72px}
#pk-cmdk li .n{font-weight:650;letter-spacing:-.02em}
#pk-cmdk li .d{font-size:12px;color:#71717a;margin-left:auto;text-align:right;max-width:46%}
#pk-cmdk li.on,#pk-cmdk li:hover{background:rgba(16,163,127,.12)}
#pk-cmdk li.on .n{color:#6ee7b7}
#pk-toast-host{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);z-index:4100;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.pk-toast{
  pointer-events:auto;min-width:180px;max-width:min(92vw,420px);
  background:rgba(18,18,24,.92);border:1px solid rgba(255,255,255,.1);
  color:#f4f4f5;padding:10px 14px;border-radius:12px;font-size:13px;font-weight:550;
  box-shadow:var(--pk-lift);backdrop-filter:blur(16px);animation:pk-rise 220ms var(--pk-ease-out)
}
.pk-toast.ok{border-color:rgba(16,163,127,.4)}
.pk-toast.bad{border-color:rgba(248,113,113,.4)}
#pk-progress{
  position:fixed;top:0;left:0;right:0;height:2px;z-index:4200;pointer-events:none;overflow:hidden;
  display:none;background:transparent
}
#pk-progress.on{display:block}
#pk-progress i{
  display:block;height:100%;width:36%;
  background:linear-gradient(90deg,transparent,#34d399,var(--accent,#10a37f),transparent);
  animation:pk-bar .9s linear infinite
}

@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
  #pk-cmdk.open,#pk-cmdk .pk-box,.msg,.bubble{animation:none!important}
}
"""

# ---------------------------------------------------------------------------
# JS — View Transitions, command palette, toast, progress, same-origin nav
# ---------------------------------------------------------------------------

KIT_JS = r"""
(() => {
  if (window.__POCKET_KIT__) return;
  window.__POCKET_KIT__ = "4.0.0";

  const SURFACES = [
    {k:"Desk", n:"Desk", d:"Chat · agents · sessions", href:"/desk"},
    {k:"Habitat", n:"Habitat floor", d:"Agents live beside chat", href:"/desk#habitat"},
    {k:"Work", n:"Work Studio", d:"Digital assistant loops", href:"/work"},
    {k:"Studio", n:"Product Studio", d:"Record · viral · ship", href:"/studio"},
    {k:"Imagine", n:"Imagine Studio", d:"Device stills · remake", href:"/imagine"},
    {k:"Create", n:"Creative Studio", d:"Image · video · blog", href:"/studio/create"},
    {k:"Voice", n:"Voice Studio", d:"V2V canvas · fusion", href:"/studio/voice"},
    {k:"Graph", n:"LOOMGRAPH", d:"See the graph · run the loop", href:"/loomgraph"},
    {k:"Phone", n:"Phone", d:"Aria · Working · pair", href:"/phone"},
    {k:"Mail", n:"Agent Mail", d:"@agents.pocket.local", href:"/mail"},
    {k:"Join", n:"Create a seat", d:"Sold POCKET — your username", href:"/join"},
    {k:"Seats", n:"Sell seats", d:"Mint pk_seat_ keys (owner)", href:"/seats"},
    {k:"Pay", n:"Billing", d:"RevenueCat seats · POCK refill", href:"/billing"},
    {k:"OS", n:"Agent OS", d:"Systems hub", href:"/os"},
    {k:"Lab", n:"Lab", d:"Readiness map", href:"/lab"},
    {k:"API", n:"Developers", d:"Keys · /v1/api", href:"/developers"},
    {k:"Docs", n:"Docs hub", d:"How-tos + papers", href:"/docs"},
    {k:"Community", n:"Community", d:"Opt-in shares", href:"/community"},
    {k:"Curious", n:"Curiosities", d:"Weird first-class toys", href:"/curiosities"},
    {k:"Install", n:"Get started", d:"Install + slices", href:"/get"},
  ];

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function toast(msg, kind) {
    let host = document.getElementById("pk-toast-host");
    if (!host) {
      host = document.createElement("div");
      host.id = "pk-toast-host";
      document.body.appendChild(host);
    }
    const el = document.createElement("div");
    el.className = "pk-toast " + (kind || "");
    el.textContent = String(msg || "");
    host.appendChild(el);
    setTimeout(() => { el.style.opacity = "0"; el.style.transform = "translateY(8px)"; }, 2600);
    setTimeout(() => el.remove(), 3000);
  }
  window.pocketToast = toast;

  function progress(on) {
    let bar = document.getElementById("pk-progress");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "pk-progress";
      bar.innerHTML = "<i></i>";
      document.body.appendChild(bar);
    }
    bar.classList.toggle("on", !!on);
  }
  window.pocketProgress = progress;

  function go(href) {
    if (!href) return;
    const run = () => { location.href = href; };
    if (reduce || !document.startViewTransition) return run();
    try { document.startViewTransition(run); } catch { run(); }
  }

  function filterSurfaces(q) {
    const s = (q || "").trim().toLowerCase();
    if (!s) return SURFACES;
    return SURFACES.filter((x) =>
      (x.k + " " + x.n + " " + x.d + " " + x.href).toLowerCase().includes(s)
    );
  }

  function mountCmdk() {
    if (document.getElementById("pk-cmdk")) return;
    const wrap = document.createElement("div");
    wrap.id = "pk-cmdk";
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-label", "Jump to a POCKET surface");
    wrap.innerHTML = `
      <div class="pk-box">
        <input id="pk-cmdk-q" type="search" autocomplete="off" spellcheck="false"
          placeholder="Jump to Desk, Studio, Phone, Mail…" />
        <div class="pk-hint"><kbd>↑↓</kbd> move <kbd>Enter</kbd> open <kbd>Esc</kbd> close · every module</div>
        <ul id="pk-cmdk-list"></ul>
      </div>`;
    document.body.appendChild(wrap);
    const input = wrap.querySelector("#pk-cmdk-q");
    const list = wrap.querySelector("#pk-cmdk-list");
    let idx = 0;
    let rows = SURFACES;

    function paint() {
      rows = filterSurfaces(input.value);
      if (idx >= rows.length) idx = 0;
      list.innerHTML = rows.map((r, i) =>
        `<li class="${i===idx?"on":""}" data-href="${r.href}"><span class="k">${r.k}</span><span class="n">${r.n}</span><span class="d">${r.d}</span></li>`
      ).join("") || `<li class="on"><span class="n">No match</span></li>`;
    }
    function open() {
      wrap.classList.add("open");
      input.value = "";
      idx = 0;
      paint();
      setTimeout(() => input.focus(), 10);
    }
    function close() { wrap.classList.remove("open"); }
    window.pocketCommand = { open, close };

    input.addEventListener("input", () => { idx = 0; paint(); });
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); idx = Math.min(idx + 1, Math.max(rows.length - 1, 0)); paint(); }
      if (e.key === "ArrowUp") { e.preventDefault(); idx = Math.max(idx - 1, 0); paint(); }
      if (e.key === "Enter") {
        e.preventDefault();
        const hit = rows[idx];
        if (hit) { close(); go(hit.href); }
      }
      if (e.key === "Escape") { e.preventDefault(); close(); }
    });
    list.addEventListener("click", (e) => {
      const li = e.target.closest("li[data-href]");
      if (!li) return;
      close();
      go(li.getAttribute("data-href"));
    });
    wrap.addEventListener("click", (e) => { if (e.target === wrap) close(); });

    document.addEventListener("keydown", (e) => {
      const t = e.target;
      const typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        wrap.classList.contains("open") ? close() : open();
        return;
      }
      if (e.key === "/" && !typing && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        open();
      }
      if (e.key === "Escape" && wrap.classList.contains("open")) close();
    });
  }

  function wireNav() {
    document.addEventListener("click", (e) => {
      const a = e.target.closest && e.target.closest("a[href]");
      if (!a) return;
      const href = a.getAttribute("href") || "";
      if (!href.startsWith("/") || href.startsWith("//")) return;
      if (a.target === "_blank" || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (href.startsWith("/v1/") || href.startsWith("/download/")) return;
      if (a.hasAttribute("download")) return;
      e.preventDefault();
      progress(true);
      go(href);
    });
  }

  function markReady() {
    document.body.classList.add("pk-ready");
    const splash = document.getElementById("bootSplash");
    if (splash && !splash.classList.contains("done")) {
      requestAnimationFrame(() => splash.classList.add("done"));
    }
  }

  function mountLive() {
    if (document.getElementById("pk-live-fab")) return;
    if (location.pathname.indexOf("/v1/") === 0) return;
    const fab = document.createElement("button");
    fab.id = "pk-live-fab";
    fab.type = "button";
    fab.title = "POCKET Live";
    fab.setAttribute("aria-label", "POCKET Live companion");
    fab.textContent = "P";
    const panel = document.createElement("div");
    panel.id = "pk-live-panel";
    panel.innerHTML = '<header>POCKET Live <small>work · explain · help</small><button type="button" id="pk-live-x" style="background:none;border:0;color:#a1a1aa;cursor:pointer">close</button></header>'
      + '<div id="pk-live-log"><div class="a">I live on this platform. Ask me to list your technology, open PhoneAI Kernel, or explain Desk / Voice / Imagine.</div></div>'
      + '<form id="pk-live-form"><input id="pk-live-in" autocomplete="off" placeholder="Ask POCKET Live…"/><button type="submit">Send</button></form>';
    document.body.appendChild(panel);
    document.body.appendChild(fab);
    const log = panel.querySelector("#pk-live-log");
    const inp = panel.querySelector("#pk-live-in");
    const hist = [];
    fab.addEventListener("click", () => {
      panel.classList.toggle("open");
      if (panel.classList.contains("open") && inp) inp.focus();
    });
    panel.querySelector("#pk-live-x").addEventListener("click", () => panel.classList.remove("open"));
    panel.querySelector("#pk-live-form").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const text = (inp.value || "").trim();
      if (!text) return;
      inp.value = "";
      log.innerHTML += '<div class="u">You</div><div class="a">' + text.replace(/[&<>]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[s])) + '</div>';
      log.scrollTop = log.scrollHeight;
      try {
        const headers = { "Content-Type": "application/json" };
        try {
          const tok = sessionStorage.getItem("pocket_token") || localStorage.getItem("pocket_token");
          if (tok) headers.Authorization = "Bearer " + tok;
        } catch (_) {}
        hist.push({ role: "user", text: text });
        const r = await fetch("/v1/companion/chat", { method: "POST", credentials: "same-origin", headers, body: JSON.stringify({ text, history: hist.slice(-8) }) });
        const j = await r.json();
        const reply = String(j.reply || j.error || "no reply");
        hist.push({ role: "model", text: reply });
        log.innerHTML += '<div class="u">Live' + (j.engine ? ' · '+j.engine : '') + '</div><div class="a">' + reply.replace(/[&<>]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[s])) + '</div>';
        if (j.open) setTimeout(() => { location.href = j.open; }, 400);
      } catch (e) {
        log.innerHTML += '<div class="u">Live</div><div class="a">Cannot reach host.</div>';
      }
      log.scrollTop = log.scrollHeight;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { mountCmdk(); wireNav(); mountLive(); markReady(); });
  } else {
    mountCmdk(); wireNav(); mountLive(); markReady();
  }
})();
"""


def enhance(html: str) -> str:
    """Inject Fluid kit into a full HTML document. Idempotent."""
    if not html or "data-pocket-kit=" in html or KIT_CSS_HREF in html:
        return html
    head = (
        f'<meta name="pocket-kit" content="{KIT_VERSION}"/>\n'
        f'<link rel="stylesheet" href="{KIT_CSS_HREF}"/>\n'
    )
    if "</head>" in html:
        html = html.replace("</head>", head + "</head>", 1)
    elif "<html" in html:
        html = html.replace("<html", f"{head}<html", 1)
    if "<html" in html and "data-pocket-kit=" not in html:
        html = html.replace("<html", f'<html data-pocket-kit="{KIT_VERSION}"', 1)
    script = f'<script defer src="{KIT_JS_HREF}"></script>\n'
    if "</body>" in html:
        html = html.replace("</body>", script + "</body>", 1)
    else:
        html += script
    return html


def kit_headers_css() -> tuple[str, str]:
    return "text/css; charset=utf-8", KIT_CSS


def kit_headers_js() -> tuple[str, str]:
    return "text/javascript; charset=utf-8", KIT_JS
