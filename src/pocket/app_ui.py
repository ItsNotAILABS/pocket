"""POCKET production UI — multi-agent desk (not a demo shell)."""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="theme-color" content="#000000"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="description" content="POCKET — host co-pilot. Fusion Sense, agents, API."/>
<title>POCKET</title>
<style>
:root{
  --bg:#06060a; --bg2:#0b0b10; --panel:#111118; --panel2:#181822;
  --line:rgba(255,255,255,.08); --line2:rgba(255,255,255,.15); --text:#e8e8ed; --muted:#8b8b98;
  --fg:#fafafa; --accent:#10a37f; --accent2:#0d8c6c; --blue:#60a5fa;
  --amber:#eab308; --red:#f87171; --violet:#a78bfa; --cyan:#22d3ee; --gold:#f0c674;
  --radius:14px; --radius-sm:10px; --radius-lg:18px;
  --font:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --shadow:0 0 0 1px rgba(255,255,255,.055);
  --shadow-lg:0 16px 48px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.05);
  --glow:0 0 0 1px rgba(16,163,127,.28),0 10px 32px rgba(16,163,127,.14);
  --focus:0 0 0 2px rgba(16,163,127,.45);
  --side-w:256px; --rail-w:300px; --screen-w:0px;
  --ease:cubic-bezier(.22,1,.36,1);
  --t:160ms var(--ease);
}
/* Contractor-grade surfaces */
.card{
  border-radius:var(--radius)!important;
  border:1px solid var(--line)!important;
  background:linear-gradient(165deg,rgba(255,255,255,.035),transparent 48%),var(--panel)!important;
  box-shadow:var(--shadow);
}
.card h3{letter-spacing:.04em;font-size:11px!important;text-transform:uppercase;font-weight:700!important;color:var(--muted)!important}
.chip.wallet-chip{
  background:linear-gradient(135deg,rgba(240,198,116,.14),rgba(16,163,127,.1));
  border:1px solid rgba(240,198,116,.28);color:var(--gold);font-variant-numeric:tabular-nums;font-weight:700
}
.econ-row{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:12px}
.econ-row:last-child{border-bottom:0}
.econ-row b{font-variant-numeric:tabular-nums;font-weight:700;color:var(--fg)}
.econ-twins{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.econ-twin{
  font-size:10px;padding:5px 8px;border-radius:999px;border:1px solid var(--line);
  background:rgba(255,255,255,.03);color:var(--muted);font-variant-numeric:tabular-nums
}
.econ-twin strong{color:var(--accent);font-weight:700;margin-left:4px}
.econ-rail{
  display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:700;
  letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:999px;
  border:1px solid rgba(16,163,127,.35);color:var(--accent);background:rgba(16,163,127,.08)
}
.econ-rail.paper{border-color:rgba(240,198,116,.35);color:var(--gold);background:rgba(240,198,116,.08)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0}
body{
  font-family:var(--font);background:
    radial-gradient(1200px 600px at 10% -10%,rgba(16,163,127,.07),transparent 55%),
    radial-gradient(900px 500px at 100% 0%,rgba(99,102,241,.05),transparent 50%),
    var(--bg);
  color:var(--text);overflow:hidden;-webkit-font-smoothing:antialiased;font-size:13.5px;color-scheme:dark;
  letter-spacing:-.005em;
}
button,input,textarea,select{font:inherit;color:inherit}
button{cursor:pointer}
button:disabled,textarea:disabled,select:disabled{opacity:.4;cursor:not-allowed}
button:focus-visible,a:focus-visible,select:focus-visible,textarea:focus-visible,.icon:focus-visible,.sitem:focus-visible{outline:none;box-shadow:var(--focus);border-radius:6px}
::selection{background:rgba(16,163,127,.35);color:var(--fg)}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
  .live-dot,.sa-dot.run{animation:none!important}
}
a{color:var(--accent);text-decoration:none}
a:hover{color:var(--accent2)}
/* scrollbars — product density (left side + right rail match) */
.side-scroll,.slist,.transcript,.rr-body,.wt-body,.rail-scroll,.rail > div{scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.12) transparent}
.side-scroll::-webkit-scrollbar,.slist::-webkit-scrollbar,.transcript::-webkit-scrollbar,.rr-body::-webkit-scrollbar,.rail-scroll::-webkit-scrollbar{width:6px;height:6px}
.side-scroll::-webkit-scrollbar-thumb,.slist::-webkit-scrollbar-thumb,.transcript::-webkit-scrollbar-thumb,.rail-scroll::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:99px}
/* Claude-style multi-column: agents | chat | screen/vcomp | workspace */
.app{display:grid;grid-template-columns:var(--side-w) minmax(0,1fr) var(--screen-w) var(--rail-w);grid-template-rows:48px 1fr;height:100vh;height:100dvh;transition:grid-template-columns .2s ease}
body.screen-col-open{--screen-w:min(380px,32vw)}
body.screen-col-open.screen-col-wide{--screen-w:min(480px,40vw)}
/* Hybrid habitat: agents live/work in a GUI floor next to chat */
.main{display:flex;flex-direction:column;min-height:0;min-width:0;background:var(--bg)}
.main-stage{flex:1;min-height:0;display:flex;flex-direction:row;min-width:0}
.main-stage .transcript{flex:1;min-width:0;min-height:0}
.habitat{
  display:none;flex-direction:column;width:min(320px,38vw);min-width:240px;
  border-left:1px solid var(--line);background:linear-gradient(180deg,#0c0c10 0%,#09090b 100%);
  min-height:0
}
body.habitat-open .habitat{display:flex}
body.habitat-open .main-stage.habitat-wide .habitat{width:min(420px,46vw)}
.habitat .hb-h{
  flex:0 0 auto;padding:10px 12px;display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--line);font-size:11px;font-weight:650;
  letter-spacing:.05em;text-transform:uppercase;color:var(--muted)
}
.habitat .hb-h b{color:var(--fg);font-weight:700;letter-spacing:-.01em;text-transform:none;font-size:13px}
.habitat .hb-h .grow{flex:1}
.habitat .hb-floor{
  flex:1;min-height:0;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:8px
}
.habitat .hb-room{
  font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  padding:6px 4px 2px;font-weight:650
}
.hab-card{
  display:flex;align-items:flex-start;gap:10px;padding:11px 12px;border-radius:14px;
  border:1px solid var(--line);background:linear-gradient(165deg,rgba(255,255,255,.03),transparent 55%),var(--panel);
  cursor:pointer;transition:border-color var(--t),background var(--t),box-shadow var(--t),transform var(--t)
}
.hab-card:hover{border-color:var(--line2);background:rgba(255,255,255,.04);transform:translateY(-1px);box-shadow:var(--shadow-lg)}
.hab-card.live{
  border-color:rgba(16,163,127,.45);box-shadow:var(--glow)
}
.hab-card .hb-av{
  width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
  font-weight:800;font-size:13px;color:#041;flex:0 0 auto;position:relative
}
.hab-card .hb-av .hb-dot{
  position:absolute;right:-2px;bottom:-2px;width:10px;height:10px;border-radius:50%;
  border:2px solid var(--panel);background:#52525b
}
.hab-card.live .hb-av .hb-dot{background:#22c55e;animation:pulse 1.2s infinite}
.hab-card.sensing .hb-av .hb-dot{background:#22d3ee}
.hab-card.speaking .hb-av .hb-dot{background:#0b84fe}
.hab-card .hb-meta{min-width:0;flex:1}
.hab-card .hb-meta .hb-name{font-size:13px;font-weight:650;color:var(--fg);letter-spacing:-.01em}
.hab-card .hb-meta .hb-role{font-size:11px;color:var(--muted);margin-top:1px}
.hab-card .hb-meta .hb-line{
  font-size:11.5px;color:var(--text);margin-top:5px;line-height:1.35;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden
}
.hab-card .hb-st{
  font-size:10px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;
  color:var(--muted);flex:0 0 auto;padding-top:2px
}
.hab-card.live .hb-st{color:#6ee7b7}
.habitat .hb-feed{
  flex:0 0 auto;max-height:110px;overflow:auto;padding:8px 12px 12px;
  border-top:1px solid var(--line);font-size:11px;color:var(--muted);line-height:1.4
}
.habitat .hb-feed .hf{padding:3px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.habitat .hb-feed b{color:var(--accent);font-weight:600}
.top{
  grid-column:1/-1;display:flex;align-items:center;gap:8px;padding:0 12px 0 14px;
  border-bottom:1px solid var(--line);
  background:rgba(7,7,10,.88);backdrop-filter:blur(22px) saturate(1.2);z-index:20;
  box-shadow:0 1px 0 rgba(255,255,255,.03)
}
.brand{display:flex;align-items:center;gap:9px;font-weight:700;letter-spacing:-.04em;font-size:13.5px;color:var(--fg);user-select:none;transition:opacity var(--t)}
.brand:hover{opacity:.9}
.brand .mark{
  width:24px;height:24px;border-radius:8px;background:linear-gradient(145deg,#34d399,var(--accent) 45%,#0a7a5f);
  display:grid;place-items:center;font-size:11px;font-weight:800;color:#041;
  box-shadow:0 0 0 1px rgba(16,163,127,.35),0 4px 14px rgba(16,163,127,.25)
}
.top .grow{flex:1;min-width:6px}
.top-meta{display:flex;gap:5px;flex-wrap:wrap;align-items:center}
.top-links{
  display:flex;gap:0;align-items:center;flex-wrap:nowrap;max-width:min(66vw,760px);overflow-x:auto;
  background:rgba(255,255,255,.02);padding:2px;border-radius:12px;border:1px solid var(--line);
  scrollbar-width:none;-webkit-overflow-scrolling:touch;position:relative
}
.top-links::-webkit-scrollbar{display:none;height:0}
.top-links a,.top-links .tab-more-btn{
  position:relative;color:var(--muted);font-size:11.5px;font-weight:600;padding:6px 9px;border-radius:9px;
  text-decoration:none;white-space:nowrap;letter-spacing:-.015em;border:0;background:transparent;cursor:pointer;
  transition:color var(--t),background var(--t),box-shadow var(--t)
}
.top-links a:hover,.top-links .tab-more-btn:hover{color:var(--fg);background:rgba(255,255,255,.055);text-decoration:none}
.top-links a:focus-visible,.top-links .tab-more-btn:focus-visible{outline:none;box-shadow:var(--focus)}
.top-links a.on-desk,.top-links a.on,.top-links .tab-more-btn.on{
  color:var(--fg);background:linear-gradient(180deg,rgba(255,255,255,.09),rgba(255,255,255,.03));
  box-shadow:0 1px 0 rgba(255,255,255,.06),inset 0 0 0 1px rgba(255,255,255,.05)
}
.top-links a.on::after,.top-links a.on-desk::after{
  content:"";position:absolute;left:18%;right:18%;bottom:2px;height:2px;border-radius:99px;
  background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:.85
}
.top-links a[data-tab="working"].on,.top-links a[data-tab="remote"].on,.top-links a[data-tab="voice_studio"].on,
.top-links a[data-tab="phone"].on,.top-links a[data-tab="platform"].on{
  color:#6ee7b7;box-shadow:inset 0 0 0 1px rgba(16,163,127,.22)
}
.top-links a[data-tab="working"].on::after,.top-links a[data-tab="remote"].on::after,
.top-links a[data-tab="phone"].on::after,.top-links a[data-tab="platform"].on::after{
  background:linear-gradient(90deg,transparent,#34d399,transparent)
}
.top-links .tab-sep{width:1px;height:14px;background:var(--line2);margin:0 4px;flex:0 0 auto;opacity:.7}
.tab-more-wrap{position:relative;flex:0 0 auto}
.tab-more-btn .chev{display:inline-block;margin-left:2px;transition:transform .18s var(--ease);font-size:9px;opacity:.75}
.tab-more-btn[aria-expanded="true"] .chev{transform:rotate(180deg)}
.tab-more-menu{
  display:none;position:absolute;top:calc(100% + 8px);right:0;min-width:248px;z-index:90;
  background:rgba(12,12,16,.98);border:1px solid var(--line2);border-radius:14px;padding:8px;
  box-shadow:0 16px 48px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.04);
  backdrop-filter:blur(20px) saturate(1.15);
  animation:moreIn .16s var(--ease)
}
@keyframes moreIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.tab-more-menu.open{display:flex;flex-direction:column;gap:2px}
.tab-more-menu a{
  display:grid;grid-template-columns:1fr auto;grid-template-rows:auto auto;column-gap:10px;row-gap:1px;
  align-items:center;padding:9px 11px;border-radius:10px;
  color:var(--muted);text-decoration:none;font-size:12.5px;font-weight:650;transition:background var(--t),color var(--t)
}
.tab-more-menu a span{grid-column:1;color:inherit}
.tab-more-menu a small{grid-column:1;font-size:10.5px;font-weight:500;color:var(--muted);opacity:.88;line-height:1.3}
.tab-more-menu a .mm-go{grid-column:2;grid-row:1/span 2;font-size:11px;opacity:0;color:var(--accent);transition:opacity var(--t)}
.tab-more-menu a:hover{background:rgba(255,255,255,.055);color:var(--fg);text-decoration:none}
.tab-more-menu a:hover .mm-go{opacity:1}
.tab-more-menu a.on{background:rgba(16,163,127,.12);color:#6ee7b7}
.tab-more-menu a.on small{color:rgba(110,231,183,.75)}
.tab-more-menu .mm-label{
  font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);
  padding:8px 11px 4px;opacity:.65
}
.tab-more-menu .mm-foot{
  margin-top:4px;padding:8px 11px 4px;border-top:1px solid var(--line);font-size:10.5px;color:var(--muted);line-height:1.4
}
/* Per-tab action strip inside product panels */
.app-panel-actions{
  display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:8px 14px;
  border-bottom:1px solid var(--line);background:linear-gradient(180deg,rgba(10,10,14,.98),rgba(7,7,10,.96))
}
.app-panel-actions:empty{display:none;padding:0;border:0}
.app-panel-actions .ap-blurb{
  font-size:11.5px;color:var(--muted);margin-right:4px;max-width:min(320px,42vw);line-height:1.35;
  padding-right:8px;border-right:1px solid var(--line)
}
.app-panel-actions button{
  border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--fg);
  border-radius:8px;padding:5px 11px;font-size:11.5px;font-weight:650;cursor:pointer;
  transition:border-color var(--t),background var(--t),color var(--t),transform var(--t)
}
.app-panel-actions button:hover{border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.12);color:#6ee7b7;transform:translateY(-1px)}
.app-panel-actions button:active{transform:none}
.app-panel-actions button.primary{
  border-color:rgba(16,163,127,.5);background:linear-gradient(180deg,rgba(16,163,127,.22),rgba(16,163,127,.12));color:#6ee7b7
}
.app-panel-actions button.primary:hover{background:rgba(16,163,127,.28);color:#fff}
@media(max-width:1100px){
  .top-links a[data-tab="browser"],.top-links a[data-tab="remote"]{padding:6px 7px}
  .app-panel-actions .ap-blurb{display:none}
}
.menu-btn{
  border:1px solid var(--line)!important;background:rgba(255,255,255,.02)!important;color:var(--muted)!important;
  border-radius:9px!important;padding:6px 10px!important;font-size:11.5px!important;font-weight:650!important;
  transition:all var(--t)!important
}
.menu-btn:hover{color:var(--fg)!important;border-color:var(--line2)!important;background:rgba(255,255,255,.05)!important}
.menu-btn.on{color:#6ee7b7!important;background:rgba(16,163,127,.14)!important;border-color:rgba(16,163,127,.4)!important;box-shadow:var(--glow)!important}
/* In-app product panels (never leave the POCKET window) */
.app-panel-layer{
  position:fixed;left:0;right:0;top:48px;bottom:0;z-index:55;display:none;flex-direction:column;
  background:var(--bg);border-top:1px solid var(--line);
  animation:panelIn .2s var(--ease)
}
@keyframes panelIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
.app-panel-layer.open{display:flex}
.app-panel-bar{
  flex:0 0 auto;display:flex;align-items:center;gap:10px;padding:9px 14px;
  border-bottom:1px solid var(--line);background:rgba(7,7,10,.97);backdrop-filter:blur(18px) saturate(1.1)
}
.app-panel-bar .ap-back{
  border:1px solid rgba(16,163,127,.45);background:linear-gradient(180deg,rgba(16,163,127,.2),rgba(16,163,127,.1));
  color:#6ee7b7;border-radius:10px;padding:7px 13px;font-size:12.5px;font-weight:700;cursor:pointer;
  transition:background var(--t),transform var(--t),box-shadow var(--t)
}
.app-panel-bar .ap-back:hover{background:rgba(16,163,127,.3);color:#fff;transform:translateY(-1px);box-shadow:var(--glow)}
.app-panel-bar .ap-meta{display:flex;flex-direction:column;gap:1px;min-width:0}
.app-panel-bar .ap-title-row{display:flex;align-items:center;gap:8px;min-width:0}
.app-panel-bar .ap-title{font-size:13.5px;font-weight:700;color:var(--fg);letter-spacing:-.03em}
.app-panel-bar .ap-path{font-size:10.5px;color:var(--muted);font-family:var(--mono);opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:42vw}
.app-panel-bar .ap-group{
  font-size:9.5px;font-weight:750;letter-spacing:.06em;text-transform:uppercase;color:#6ee7b7;
  background:rgba(16,163,127,.12);border:1px solid rgba(16,163,127,.28);padding:2px 7px;border-radius:999px
}
.app-panel-bar .ap-tools{display:flex;align-items:center;gap:6px;margin-left:auto}
.app-panel-bar .ap-tools .icon{
  border:1px solid var(--line);background:rgba(255,255,255,.02);color:var(--muted);
  border-radius:8px;padding:5px 10px;font-size:12px;font-weight:650;cursor:pointer;transition:all var(--t)
}
.app-panel-bar .ap-tools .icon:hover{color:var(--fg);border-color:var(--line2);background:rgba(255,255,255,.05)}
.app-panel-stage{flex:1;min-height:0;position:relative;background:#08080c}
.app-panel-stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:var(--bg)}
.app-panel-stage.loading::before{
  content:"";position:absolute;top:0;left:0;right:0;height:2px;z-index:2;
  background:linear-gradient(90deg,transparent,var(--accent),#34d399,transparent);
  background-size:200% 100%;animation:apLoad 1.1s linear infinite
}
@keyframes apLoad{0%{background-position:100% 0}100%{background-position:-100% 0}}
/* Empty home tab map */
.empty-map{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:18px;max-width:420px}
.empty-map button{
  border:1px solid var(--line);background:rgba(255,255,255,.02);color:var(--muted);
  border-radius:999px;padding:5px 11px;font-size:11px;font-weight:650;cursor:pointer;transition:all var(--t)
}
.empty-map button:hover{color:var(--fg);border-color:rgba(16,163,127,.35);background:rgba(16,163,127,.1);color:#6ee7b7}
.empty-map button b{font-weight:700;color:inherit}
.top-back{
  border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:9px;
  padding:6px 11px;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:4px;
  transition:all var(--t)
}
.top-back:hover{color:var(--fg);background:rgba(255,255,255,.05);border-color:var(--line2)}
/* Production boot splash */
.boot-splash{position:fixed;inset:0;z-index:200;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#050508;transition:opacity .45s ease,visibility .45s;pointer-events:none}
.boot-splash.done{opacity:0;visibility:hidden;pointer-events:none}
.boot-splash .boot-mark{width:52px;height:52px;border-radius:14px;background:linear-gradient(145deg,#10a37f,#0a7a5f);color:#041;display:grid;place-items:center;font-size:22px;font-weight:800;box-shadow:0 0 0 1px rgba(16,163,127,.4),0 12px 40px rgba(16,163,127,.25);animation:bootPop .7s cubic-bezier(.2,1.2,.4,1) both}
.boot-splash .boot-title{margin-top:18px;font-size:20px;font-weight:650;letter-spacing:-.04em;color:#fafafa;animation:bootFade .6s .15s both}
.boot-splash .boot-sub{margin-top:6px;font-size:12.5px;color:#71717a;animation:bootFade .6s .25s both}
.boot-splash .boot-bar{width:120px;height:3px;border-radius:99px;background:rgba(255,255,255,.08);margin-top:22px;overflow:hidden;animation:bootFade .5s .3s both}
.boot-splash .boot-bar i{display:block;height:100%;width:40%;border-radius:99px;background:linear-gradient(90deg,#10a37f,#34d399);animation:bootSlide 1.1s ease-in-out infinite}
@keyframes bootPop{from{transform:scale(.6);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes bootFade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes bootSlide{0%{transform:translateX(-100%)}100%{transform:translateX(280%)}}
/* Browser mode: stays INSIDE POCKET — chrome always has ← Desk (never hijacks whole app) */
.browser-layer{position:fixed;inset:0;z-index:70;display:none;flex-direction:column;background:var(--bg)}
.browser-layer.open{display:flex}
.browser-chrome{flex:0 0 auto;display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid var(--line);background:rgba(9,9,11,.96);backdrop-filter:blur(14px)}
.browser-chrome .b-back{border:1px solid rgba(16,163,127,.45);background:rgba(16,163,127,.12);color:#6ee7b7;border-radius:8px;padding:7px 12px;font-size:12.5px;font-weight:700;cursor:pointer;white-space:nowrap}
.browser-chrome .b-back:hover{background:rgba(16,163,127,.22);color:#fff}
.browser-chrome button.b-ico{border:1px solid var(--line);background:var(--panel);color:var(--text);border-radius:8px;padding:7px 10px;font-size:12px;font-weight:600;cursor:pointer}
.browser-chrome button.b-ico:hover{border-color:var(--line2);color:var(--fg)}
.browser-chrome input{flex:1;min-width:0;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);border-radius:8px;padding:8px 12px;font-size:13px}
.browser-chrome .b-go{border:0;background:var(--accent);color:#041;border-radius:8px;padding:8px 14px;font-size:12.5px;font-weight:700;cursor:pointer}
.browser-chrome .b-go:hover{background:var(--accent2)}
.browser-quick{flex:0 0 auto;display:flex;flex-wrap:wrap;gap:6px;padding:8px 12px;border-bottom:1px solid var(--line);background:var(--bg2)}
.browser-quick button{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:999px;padding:5px 10px;font-size:11px;font-weight:550;cursor:pointer}
.browser-quick button:hover{color:var(--fg);border-color:var(--line2)}
.browser-stage{flex:1;min-height:0;position:relative;background:#000}
.browser-stage iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:#0a0a0a}
.browser-blocked{position:absolute;inset:0;display:none;align-items:center;justify-content:center;flex-direction:column;gap:12px;padding:32px;text-align:center;color:var(--muted);background:rgba(9,9,11,.94)}
.browser-blocked.show{display:flex}
.browser-blocked h3{margin:0;color:var(--fg);font-size:16px;font-weight:650}
.browser-blocked p{margin:0;max-width:420px;font-size:13px;line-height:1.5}
.browser-blocked .btn-primary{border:0;background:var(--accent);color:#041;border-radius:9px;padding:10px 16px;font-weight:700;cursor:pointer}
.chip{font-size:10.5px;font-weight:550;padding:3px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:transparent;letter-spacing:.01em}
.chip.on{color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
.chip.off{color:#fca5a5;border-color:rgba(248,113,113,.3);background:rgba(248,113,113,.08)}
.chip.warn{color:#fde047;border-color:rgba(234,179,8,.3);background:rgba(234,179,8,.08)}
.side,.rail,.screen-col{background:var(--bg2);border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0;pointer-events:auto;position:relative;z-index:5;overflow:hidden}
.screen-col{
  border-left:1px solid var(--line);min-width:0;width:100%;
  display:none; /* width driven by grid --screen-w */
}
body.screen-col-open .screen-col{display:flex}
.screen-col .sc-h{
  flex:0 0 auto;padding:10px 12px;display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--line);font-size:11px;font-weight:650;
  letter-spacing:.05em;text-transform:uppercase;color:var(--muted)
}
.screen-col .sc-h b{color:var(--fg);font-weight:700;letter-spacing:-.01em;text-transform:none;font-size:13px}
.screen-col .sc-h .grow{flex:1}
.screen-col .sc-modes{display:flex;gap:4px;padding:8px 10px;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.screen-col .sc-modes button{
  border:1px solid var(--line);background:transparent;color:var(--muted);
  border-radius:999px;padding:5px 10px;font-size:11px;font-weight:600;cursor:pointer
}
.screen-col .sc-modes button.on{background:rgba(16,163,127,.15);border-color:rgba(16,163,127,.4);color:#6ee7b7}
.screen-col .sc-modes button.danger.on{background:rgba(248,113,113,.12);border-color:rgba(248,113,113,.4);color:#fca5a5}
.screen-col .sc-frame-wrap{
  flex:0 0 auto;margin:10px;border-radius:12px;overflow:hidden;
  border:1px solid rgba(34,211,238,.25);background:#050508;position:relative;
  aspect-ratio:16/10;max-height:220px
}
.screen-col .sc-frame-wrap img{width:100%;height:100%;object-fit:contain;display:block;background:#000}
.screen-col .sc-frame-wrap .sc-badge{
  position:absolute;top:8px;left:8px;font-size:10px;font-weight:700;
  padding:3px 8px;border-radius:999px;background:rgba(0,0,0,.65);color:#67e8f9;
  border:1px solid rgba(34,211,238,.35)
}
.screen-col .sc-body{flex:1;min-height:0;overflow:auto;padding:0 10px 12px}
.screen-col .sc-card{
  margin:0 0 10px;padding:10px 11px;border-radius:10px;border:1px solid var(--line);background:var(--panel)
}
.screen-col .sc-card h4{margin:0 0 6px;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.screen-col .sc-card pre,.screen-col .sc-brief{
  margin:0;font-size:11px;line-height:1.45;color:var(--text);white-space:pre-wrap;max-height:120px;overflow:auto
}
.screen-col .sc-syms{display:flex;flex-wrap:wrap;gap:4px;max-height:90px;overflow:auto}
.screen-col .sc-syms span{
  font-size:10px;padding:2px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:rgba(0,0,0,.2)
}
.screen-col .sc-acts{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.screen-col .sc-acts button{
  border:1px solid var(--line);background:transparent;color:var(--muted);
  border-radius:7px;padding:6px 9px;font-size:11px;font-weight:550;cursor:pointer
}
.screen-col .sc-acts button:hover{color:var(--fg);border-color:var(--line2)}
/* Left Agents column scrolls as one pane — same pattern as right Workspace rail */
.side-scroll,.rail-scroll{
  flex:1 1 auto;min-height:0;overflow-y:auto;overflow-x:hidden;
  overscroll-behavior:contain;-webkit-overflow-scrolling:touch;
  display:block;padding-bottom:10px
}
.side .side-h,.rail > .side-h{flex:0 0 auto}
.side .actions button,.side .slist .sitem,.empty-actions button{pointer-events:auto;cursor:pointer;position:relative;z-index:6}
.rail{border-right:0;border-left:1px solid var(--line);min-width:280px;max-width:360px}
.ai-sum,.ai-prev,.ai-bus{margin:0 10px 10px;padding:10px 11px;border-radius:10px;border:1px solid var(--line);background:var(--panel)}
.ai-sum h3,.ai-prev h3,.ai-bus h3{margin:0 0 8px;font-size:10.5px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.ai-sum .body{font-size:11.5px;line-height:1.5;color:var(--text);max-height:160px;overflow:auto;white-space:pre-wrap}
.ai-sum .meta{font-size:10px;color:var(--muted);margin-top:6px}
.ai-prev .pv{border:1px solid var(--line);border-radius:8px;padding:7px 8px;margin-bottom:6px;background:rgba(0,0,0,.25);cursor:pointer}
.ai-prev .pv:hover{border-color:rgba(16,163,127,.35)}
.ai-prev .pv b{display:block;font-size:11px;color:var(--fg);margin-bottom:3px}
.ai-prev .pv pre{margin:0;font-size:10px;line-height:1.4;color:var(--muted);max-height:72px;overflow:hidden;white-space:pre-wrap;font-family:var(--mono)}
.ai-prev .tree{font-size:10.5px;font-family:var(--mono);color:var(--muted);max-height:100px;overflow:auto;line-height:1.45}
.ai-bus .bm{font-size:10.5px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);color:var(--muted);line-height:1.4}
.ai-bus .bm b{color:var(--accent);font-weight:600}
.ai-bus .bm .hm{font-family:var(--mono);font-size:9px;opacity:.7}
.side-h{padding:14px 14px 8px;display:flex;justify-content:space-between;align-items:center;font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.ai-sum,.ai-prev,.ai-bus{
  border:1px solid var(--line)!important;border-radius:14px!important;
  background:linear-gradient(165deg,rgba(255,255,255,.025),transparent 50%),var(--panel)!important
}
.ai-sum h3,.ai-prev h3,.ai-bus h3{letter-spacing:-.02em!important}
.icon{border:1px solid transparent;background:transparent;color:var(--muted);border-radius:7px;padding:5px 7px;font-size:12px;transition:background .12s,color .12s}
.icon:hover{color:var(--text);background:rgba(255,255,255,.05)}
.actions{display:flex;flex-direction:column;gap:1px;padding:0 8px 8px;flex:0 0 auto;overflow:visible}
.actions button{
  text-align:left;border:1px solid transparent;background:transparent;border-radius:11px;
  padding:10px 12px;font-size:13px;font-weight:500;color:var(--text);transition:all var(--t)
}
.actions button:hover{background:rgba(255,255,255,.04);border-color:var(--line)}
.actions button:active{background:rgba(16,163,127,.1);border-color:rgba(16,163,127,.25)}
.actions button b{font-weight:650;letter-spacing:-.02em;color:var(--fg)}
.actions button small{display:block;color:var(--muted);font-weight:400;margin-top:2px;font-size:11px;line-height:1.35}
.actions .more-btn{color:var(--muted);font-size:11.5px;padding:8px 11px;font-weight:500}
.actions .more-agents{
  display:none;flex-direction:column;gap:1px;
  max-height:0;overflow:hidden;opacity:0;transition:max-height .15s ease,opacity .12s
}
.actions .more-agents.open{
  display:flex;max-height:min(42vh,320px);overflow-y:auto;overflow-x:hidden;
  opacity:1;border:1px solid var(--line);border-radius:10px;margin-top:4px;
  padding:4px;background:rgba(0,0,0,.2);scrollbar-width:thin
}
.actions .more-agents.open::-webkit-scrollbar{width:6px}
.actions .more-agents.open::-webkit-scrollbar-thumb{background:rgba(255,255,255,.15);border-radius:99px}
.toolrow{padding:0 10px 10px;display:grid;gap:6px;flex:0 0 auto;overflow:visible}
.toolrow button,.toolrow label.btn{display:block;width:100%;text-align:center;border:1px solid var(--line);background:transparent;border-radius:8px;padding:7px;font-size:11.5px;font-weight:550;color:var(--muted);transition:border-color .12s,color .12s,background .12s}
.toolrow button:hover,label.btn:hover{color:var(--text);border-color:var(--line2);background:rgba(255,255,255,.03)}
#fileInput{display:none}
/* Sessions grow naturally; parent .side-scroll owns the scrollbar (like rail) */
.slist{flex:none;overflow:visible;padding:4px 8px 18px;min-height:48px}
.stack-card{margin:0 10px 10px;padding:9px 11px;border-radius:10px;border:1px solid var(--line);background:var(--panel);font-size:11px;line-height:1.4}
.stack-card .sk{display:flex;justify-content:space-between;gap:8px;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.stack-card .sk:last-child{border-bottom:0}
.stack-card .sk b{font-weight:600;color:var(--fg);font-size:11px}
.stack-card .sk span.on{color:#6ee7b7;font-weight:550}
.stack-card .sk span.off{color:#f87171;font-weight:550}
.slist .hint{color:var(--muted);font-size:11.5px;padding:10px 8px;line-height:1.5}
.sitem{display:flex;gap:8px;padding:9px 10px;border-radius:9px;border:1px solid transparent;margin-bottom:2px;cursor:pointer;transition:background .12s,border-color .12s}
.sitem:hover{background:rgba(255,255,255,.03)}
.sitem.on{background:rgba(16,163,127,.08);border-color:rgba(16,163,127,.22)}
.dot{width:7px;height:7px;border-radius:50%;margin-top:5px;flex:0 0 auto}
.sitem b{display:block;font-size:12.5px;font-weight:600;letter-spacing:-.01em}
.sitem .meta{font-size:10.5px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sitem .x{margin-left:auto;border:0;background:transparent;color:var(--muted);font-size:15px;padding:0 4px;line-height:1;opacity:.6}
.sitem .x:hover{color:var(--red);opacity:1}
.main{display:flex;flex-direction:column;min-width:0;min-height:0;background:var(--bg)}
.main-h{
  padding:10px 18px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:8px;min-height:48px;
  background:linear-gradient(180deg,rgba(255,255,255,.02),transparent)
}
.main-h h1{margin:0;font-size:13.5px;font-weight:650;letter-spacing:-.03em;color:var(--fg)}
.tag{font-size:10.5px;font-weight:600;padding:3px 9px;border-radius:999px;background:rgba(255,255,255,.02);border:1px solid var(--line);color:var(--muted)}
.main-h select{margin-left:auto;background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:6px 10px;font-size:11.5px;color:var(--muted)}
.transcript{flex:1;overflow:auto;padding:18px 22px 24px;display:flex;flex-direction:column;gap:2px}
.empty{margin:auto;max-width:440px;text-align:center;color:var(--muted);line-height:1.55;padding:36px 20px}
.empty .mark{
  width:44px;height:44px;border-radius:14px;background:linear-gradient(145deg,#34d399,var(--accent),#0a7a5f);color:#041;
  display:grid;place-items:center;font-size:18px;font-weight:800;margin:0 auto 18px;
  box-shadow:0 0 0 1px rgba(16,163,127,.4),0 12px 36px rgba(16,163,127,.22),0 0 60px rgba(16,163,127,.08)
}
.empty h2{color:var(--fg);font-size:22px;margin:0 0 10px;font-weight:700;letter-spacing:-.04em}
.empty p{font-size:13.5px;margin:0;color:var(--muted);max-width:36em;margin-left:auto;margin-right:auto;line-height:1.55}
.empty .empty-actions{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:22px}
.empty .empty-actions button{
  border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));
  color:var(--text);border-radius:999px;padding:9px 16px;font-size:12.5px;font-weight:600;
  transition:all var(--t);box-shadow:0 1px 0 rgba(255,255,255,.04) inset
}
.empty .empty-actions button:hover{
  border-color:rgba(16,163,127,.5);color:var(--fg);background:rgba(16,163,127,.12);
  transform:translateY(-1px);box-shadow:var(--glow)
}
.empty .empty-actions button:active{transform:translateY(0)}
.empty kbd{
  font-family:var(--mono);font-size:11px;padding:1px 5px;border-radius:4px;
  border:1px solid var(--line);background:var(--panel);color:var(--fg)
}
/* Chat — iMessage-style bubbles (plan + all conversational modes) */
.transcript{display:flex;flex-direction:column;gap:6px}
.transcript.imsg{padding:16px 18px 28px;background:linear-gradient(180deg,#0a0a0c 0%,#09090b 40%)}
.msg{border:0;border-radius:0;background:transparent;overflow:visible;max-width:720px;width:100%;margin:0 auto}
.msg.user{margin-top:10px;display:flex;flex-direction:column;align-items:flex-end}
.msg.user .mb{
  white-space:pre-wrap;font-size:14.5px;line-height:1.45;font-family:var(--font);
  padding:10px 14px;border-radius:18px 18px 5px 18px;
  background:#0b84fe;border:0;color:#fff;max-width:min(78%,520px);
  box-shadow:0 1px 2px rgba(0,0,0,.25);word-break:break-word
}
.msg.agent{display:flex;flex-direction:column;align-items:flex-start;max-width:min(92%,680px);margin:2px auto 2px 0}
.msg.agent .mb{
  /* normal flow so code cards don't become one tall pre-wrap blob */
  white-space:normal;font-size:14.5px;line-height:1.55;font-family:var(--font);
  padding:10px 14px;color:var(--fg);max-height:none;overflow:visible;
  background:#2c2c2e;border:0;border-radius:18px 18px 18px 5px;
  max-width:100%;box-shadow:0 1px 2px rgba(0,0,0,.2);word-break:break-word
}
.msg.agent .mb.prose p{margin:0 0 .55em}
.msg.agent .mb.prose p:last-child{margin:0}
.msg.agent .mb.prose strong{color:#fff;font-weight:600}
.msg.agent .mb.prose code,.msg.user .mb code{
  font-family:var(--mono);font-size:12.5px;background:rgba(0,0,0,.28);padding:1px 6px;border-radius:5px;
  word-break:break-all
}
.msg.user .mb code{background:rgba(0,0,0,.2);color:#e8f1ff}
/* Compact code snippets — never “tall weird” full-height walls */
.code-snip{
  margin:.55em 0;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.1);
  background:#141416;max-width:100%;display:block
}
.code-snip .cs-head{
  display:flex;align-items:center;justify-content:space-between;gap:8px;
  padding:5px 10px;background:rgba(0,0,0,.4);border-bottom:1px solid rgba(255,255,255,.06);
  font-size:10.5px;font-weight:600;color:var(--muted);letter-spacing:.02em
}
.code-snip .cs-head .cs-lang{text-transform:lowercase;color:#a1a1aa;font-family:var(--mono)}
.code-snip .cs-copy{
  border:0;background:rgba(255,255,255,.08);color:#e4e4e7;border-radius:6px;
  padding:3px 9px;font-size:11px;font-weight:600;cursor:pointer
}
.code-snip .cs-copy:hover{background:rgba(16,163,127,.25);color:#fff}
.code-snip pre{
  margin:0;font-family:var(--mono);font-size:11.5px;line-height:1.45;
  padding:10px 12px;overflow:auto;max-height:min(200px,32vh);color:#c8f0d4;
  white-space:pre;tab-size:2;-webkit-overflow-scrolling:touch
}
.msg.agent .mb.prose pre:not(.code-snip pre){
  font-family:var(--mono);font-size:11.5px;line-height:1.45;background:#141416;border:1px solid var(--line);
  border-radius:10px;padding:10px 12px;overflow:auto;max-height:min(200px,32vh);margin:.55em 0;color:#b7f0c6;
  white-space:pre
}
/* In-chat app preview bubbles (agents render live UI) */
.app-preview{
  margin:.65em 0 .4em;border-radius:14px;overflow:hidden;
  border:1px solid rgba(34,211,238,.28);background:#0c0c10;
  box-shadow:0 4px 18px rgba(0,0,0,.35);max-width:100%
}
.app-preview .ap-head{
  display:flex;align-items:center;gap:8px;padding:7px 10px;
  background:linear-gradient(180deg,rgba(34,211,238,.12),rgba(0,0,0,.25));
  border-bottom:1px solid rgba(255,255,255,.06);font-size:11.5px;color:var(--muted)
}
.app-preview .ap-head b{color:var(--fg);font-weight:650;letter-spacing:-.01em}
.app-preview .ap-head .ap-dot{
  width:7px;height:7px;border-radius:50%;background:#22d3ee;box-shadow:0 0 8px rgba(34,211,238,.6);flex:0 0 auto
}
.app-preview .ap-actions{margin-left:auto;display:flex;gap:5px;flex-wrap:wrap}
.app-preview .ap-actions button,.app-preview .ap-actions a{
  border:1px solid var(--line);background:rgba(255,255,255,.05);color:var(--muted);
  border-radius:7px;padding:3px 8px;font-size:10.5px;font-weight:600;cursor:pointer;text-decoration:none
}
.app-preview .ap-actions button:hover,.app-preview .ap-actions a:hover{color:var(--fg);border-color:var(--line2)}
.app-preview .ap-frame-wrap{
  position:relative;width:100%;height:min(320px,42vh);background:#09090b;overflow:hidden
}
.app-preview.expanded .ap-frame-wrap{height:min(560px,68vh)}
.app-preview iframe{
  position:absolute;inset:0;width:100%;height:100%;border:0;background:#fff
}
.app-preview .ap-url{
  padding:5px 10px;font-size:10px;font-family:var(--mono);color:var(--muted);
  border-top:1px solid rgba(255,255,255,.05);overflow:hidden;text-overflow:ellipsis;white-space:nowrap
}
.github-card .gh-row{display:flex;justify-content:space-between;gap:8px;font-size:11.5px;padding:3px 0;color:var(--muted)}
.github-card .gh-row b{color:var(--fg);font-weight:600}
/* Live stream first-class */
.msg.agent.streaming .mb{border:1px solid rgba(16,163,127,.28);box-shadow:0 0 0 1px rgba(16,163,127,.08)}
.msg.agent.streaming .mh .live-dot{display:inline-block!important}
.stream-caret{
  display:inline-block;width:8px;height:1.05em;margin-left:2px;vertical-align:text-bottom;
  background:var(--accent);border-radius:1px;animation:caretBlink 1s step-end infinite
}
@keyframes caretBlink{50%{opacity:0}}
.msg.pop-in{animation:msgPop .28s cubic-bezier(.2,1.1,.4,1) both}
@keyframes msgPop{from{opacity:0;transform:translateY(8px) scale(.98)}to{opacity:1;transform:none}}
.stream-banner{
  max-width:min(92%,680px);margin:4px 0 8px;padding:8px 12px;border-radius:12px;
  border:1px solid rgba(16,163,127,.25);background:rgba(16,163,127,.08);
  display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted)
}
.stream-banner b{color:var(--fg)}
.v2v-panel{
  max-width:min(92%,680px);margin:8px 0 12px;padding:14px 16px;border-radius:16px;
  border:1px solid rgba(11,132,254,.35);background:linear-gradient(165deg,rgba(11,132,254,.12),#141416);
  box-shadow:0 0 0 1px rgba(0,0,0,.2)
}
.v2v-panel .v2v-title{font-size:12px;font-weight:700;color:#7dd3fc;letter-spacing:.04em;text-transform:uppercase;margin-bottom:8px}
.v2v-panel .v2v-wave{display:flex;align-items:flex-end;gap:3px;height:28px;margin:8px 0}
.v2v-panel .v2v-wave i{
  display:block;width:4px;border-radius:99px;background:#0b84fe;height:30%;
  animation:v2vBar 1s ease-in-out infinite
}
.v2v-panel .v2v-wave i:nth-child(2){animation-delay:.1s}
.v2v-panel .v2v-wave i:nth-child(3){animation-delay:.2s}
.v2v-panel .v2v-wave i:nth-child(4){animation-delay:.3s}
.v2v-panel .v2v-wave i:nth-child(5){animation-delay:.4s}
.v2v-panel.live .v2v-wave i{animation-play-state:running}
.v2v-panel:not(.live) .v2v-wave i{animation:none;opacity:.35}
@keyframes v2vBar{0%,100%{height:28%}50%{height:100%}}
.v2v-panel .v2v-status{font-size:12.5px;color:var(--text);line-height:1.45}
.v2v-panel .v2v-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.v2v-panel .v2v-actions button{
  border:1px solid var(--line);background:rgba(0,0,0,.25);color:var(--fg);
  border-radius:999px;padding:7px 12px;font-size:12px;font-weight:600;cursor:pointer
}
.v2v-panel .v2v-actions button.hot{background:#0b84fe;border-color:transparent;color:#fff}
.msg .mh{
  display:flex;justify-content:space-between;gap:8px;padding:2px 6px 4px;
  background:transparent;border:0;font-size:11px;font-weight:500;color:var(--muted);
  max-width:100%;width:100%
}
.msg .mb.term{
  background:#1c1c1e;color:#b7f0c6;max-height:320px;min-height:36px;font-family:var(--mono);
  font-size:12.5px;line-height:1.5;padding:12px 14px;border-radius:14px;border:1px solid var(--line);overflow:auto
}
.msg.running .mh{color:var(--blue)}
.msg.failed .mh{color:var(--red)}
.msg.done .mh{color:var(--accent)}
.msg.cancelled .mh{color:#f59e0b}
.msg.agent .mh{opacity:.9;letter-spacing:.01em}
/* Plan mode: tighter iMessage column */
.transcript.imsg .msg.user{margin-left:auto;margin-right:0;width:auto}
.transcript.imsg .msg.agent{margin-left:0;margin-right:auto}
.transcript.imsg .think-row,.transcript.imsg .worked-meta{max-width:min(92%,680px);margin-left:0;margin-right:auto}
.mic-patient{outline:2px solid rgba(11,132,254,.55)!important;box-shadow:0 0 0 3px rgba(11,132,254,.15)}
.mic-dictation{outline:2px solid rgba(16,163,127,.5)!important;box-shadow:0 0 0 3px rgba(16,163,127,.12)}
.mic-interim{font-size:11.5px;color:var(--muted);padding:4px 10px 2px;min-height:18px;line-height:1.35}
.mic-interim:empty{display:none}
/* Working board — operational work surface (not coding chat) */
.work-board-panel{
  margin:0 12px 10px;padding:14px 16px 12px;border-radius:16px;
  border:1px solid rgba(244,114,182,.4);background:linear-gradient(165deg,rgba(244,114,182,.1),rgba(12,12,16,.98));
  box-shadow:0 12px 40px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.04)
}
.work-board-panel .wbp-h{display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap}
.work-board-panel .wbp-h b{font-size:14px;color:#f9a8d4;letter-spacing:-.03em;font-weight:700}
.work-board-panel .wbp-sub{font-size:11px;color:var(--muted)}
.work-board-panel .wbp-pills{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 10px}
.work-board-panel .wbp-pills button{
  font-size:11.5px;font-weight:650;padding:6px 11px;border-radius:999px;border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.04);color:#e4e4e7;cursor:pointer;transition:border-color .12s,background .12s
}
.work-board-panel .wbp-pills button:hover{border-color:rgba(244,114,182,.5);background:rgba(244,114,182,.12);color:#fdf2f8}
.work-board-panel .wbp-hint{font-size:11.5px;color:var(--muted);line-height:1.45;margin-bottom:10px}
.work-board-panel .wbp-hint em{color:#fbcfe8;font-style:normal}
.work-board-panel .wbp-stats{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.work-board-panel .wbp-stat{
  font-size:11px;font-weight:650;padding:4px 10px;border-radius:999px;border:1px solid var(--line);color:var(--muted)
}
.work-board-panel .wbp-stat.need{border-color:rgba(251,191,36,.35);color:#fbbf24;background:rgba(251,191,36,.08)}
.work-board-panel .wbp-stat.ok{border-color:rgba(74,222,128,.3);color:#4ade80;background:rgba(74,222,128,.08)}
.work-board-panel .wbp-stat.run{border-color:rgba(96,165,250,.35);color:#93c5fd}
.work-board-panel .wbp-table{max-height:280px;overflow:auto;border-radius:12px;border:1px solid var(--line);background:rgba(0,0,0,.3)}
.work-board-panel .wbp-card{
  padding:10px 12px;border-bottom:1px solid rgba(255,255,255,.05);display:grid;
  grid-template-columns:auto 1fr auto;gap:8px 12px;align-items:start
}
.work-board-panel .wbp-card:last-child{border-bottom:0}
.work-board-panel .wbp-card .kind{font-size:16px;line-height:1.2;padding-top:2px}
.work-board-panel .wbp-card .title{font-size:12.5px;font-weight:650;color:var(--fg);letter-spacing:-.01em}
.work-board-panel .wbp-card .meta{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.4}
.work-board-panel .wbp-card .st{
  font-size:10.5px;font-weight:750;text-transform:uppercase;letter-spacing:.04em;
  padding:4px 8px;border-radius:6px;white-space:nowrap
}
.work-board-panel .wbp-card .st.done{background:rgba(74,222,128,.12);color:#4ade80}
.work-board-panel .wbp-card .st.needs_you{background:rgba(251,191,36,.12);color:#fbbf24}
.work-board-panel .wbp-card .st.blocked{background:rgba(248,113,113,.12);color:#f87171}
.work-board-panel .wbp-card .st.running,.work-board-panel .wbp-card .st.queued{background:rgba(96,165,250,.12);color:#93c5fd}
.work-board-panel .wbp-card .row-actions{grid-column:2 / -1;display:flex;flex-wrap:wrap;gap:6px;margin-top:2px}
.work-board-panel .wbp-card .row-actions button{
  font-size:11px;font-weight:650;padding:4px 9px;border-radius:7px;border:1px solid var(--line);
  background:rgba(255,255,255,.04);color:var(--text);cursor:pointer
}
.work-board-panel .wbp-card .row-actions button.primary{border-color:rgba(244,114,182,.4);color:#f9a8d4}
.work-board-panel .wbp-card .row-actions button:hover{background:rgba(255,255,255,.08)}
.work-board-panel .wbp-card .detail{grid-column:2 / -1;font-size:11px;color:#a1a1aa;line-height:1.45;display:none}
.work-board-panel .wbp-card.open .detail{display:block;margin-top:2px;padding:8px;border-radius:8px;background:rgba(0,0,0,.25)}
.work-board-panel .wbp-empty{padding:18px 14px;text-align:center;color:var(--muted);font-size:12.5px;line-height:1.5}
.work-board-panel .wbp-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.work-board-panel .wbp-actions button{
  font-size:12px;font-weight:650;padding:8px 13px;border-radius:9px;border:1px solid var(--line);
  background:rgba(255,255,255,.05);color:var(--fg);cursor:pointer
}
.work-board-panel .wbp-actions button.cta{background:rgba(244,114,182,.18);border-color:rgba(244,114,182,.4);color:#fce7f3}
.work-board-panel .wbp-actions button:hover{border-color:rgba(244,114,182,.45);background:rgba(244,114,182,.12)}
body.work-mode-on .composer-hint{color:#f9a8d4}
body.work-mode-on #input{border-color:rgba(244,114,182,.25)}
/* Production status pills — mature host/voice/mic indicators */
.prod-pill{
  display:inline-flex;align-items:center;gap:5px;font-size:10.5px;font-weight:700;
  letter-spacing:.02em;padding:3px 8px;border-radius:999px;border:1px solid var(--line);
  color:var(--muted);background:rgba(255,255,255,.03);white-space:nowrap
}
.prod-pill i{width:6px;height:6px;border-radius:50%;background:#52525b;display:inline-block}
.prod-pill.on{color:#bbf7d0;border-color:rgba(74,222,128,.3);background:rgba(74,222,128,.08)}
.prod-pill.on i{background:#4ade80;box-shadow:0 0 6px rgba(74,222,128,.6)}
.prod-pill.warn{color:#fde68a;border-color:rgba(251,191,36,.3);background:rgba(251,191,36,.08)}
.prod-pill.warn i{background:#fbbf24}
.prod-pill.off{color:#fca5a5;border-color:rgba(248,113,113,.25);background:rgba(248,113,113,.06)}
.prod-pill.off i{background:#f87171}
.prod-rail{display:flex;align-items:center;gap:5px;flex-wrap:wrap;max-width:min(42vw,420px);justify-content:flex-end}
.top-meta .chip{transition:none}
/* Mature empty states */
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px 24px;text-align:center;min-height:40vh}
.empty .mark{
  width:48px;height:48px;border-radius:14px;display:grid;place-items:center;
  background:linear-gradient(145deg,#10a37f,#0a7a5f);color:#041;font-weight:800;font-size:18px;
  margin-bottom:14px;box-shadow:0 0 0 1px rgba(16,163,127,.3),0 12px 32px rgba(0,0,0,.35)
}
.empty h2{margin:0 0 8px;font-size:18px;letter-spacing:-.03em;color:var(--fg);font-weight:700}
.empty p{margin:0;max-width:36ch;color:var(--muted);font-size:13.5px;line-height:1.5}
.composer-inner{transition:border-color .15s ease}
body.work-mode-on .composer-inner{box-shadow:inset 0 0 0 1px rgba(244,114,182,.12)}
/* Integrated agent console (WSL / Python / PowerShell) */
.agent-console-panel{
  margin:0 12px 10px;padding:12px 14px;border-radius:14px;
  border:1px solid rgba(139,92,246,.4);background:linear-gradient(165deg,rgba(139,92,246,.1),rgba(10,10,14,.98));
  box-shadow:0 10px 32px rgba(0,0,0,.3)
}
.agent-console-panel .acp-h{display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.agent-console-panel .acp-h b{font-size:13px;color:#c4b5fd;font-weight:700;letter-spacing:-.02em}
.agent-console-panel .acp-sub{font-size:11px;color:var(--muted)}
.agent-console-panel #acpKind{
  font-size:11.5px;padding:4px 8px;border-radius:8px;border:1px solid var(--line);
  background:var(--panel);color:var(--fg)
}
.agent-console-panel .acp-log{
  margin:0;max-height:200px;overflow:auto;padding:10px 12px;border-radius:10px;
  background:#050508;border:1px solid rgba(255,255,255,.06);color:#86efac;
  font-family:var(--mono);font-size:11.5px;line-height:1.45;white-space:pre-wrap;word-break:break-word
}
.agent-console-panel .acp-row{display:flex;gap:8px;margin-top:8px}
.agent-console-panel #acpInput{
  flex:1;padding:9px 12px;border-radius:9px;border:1px solid var(--line);
  background:rgba(0,0,0,.35);color:var(--fg);font-family:var(--mono);font-size:12.5px
}
.agent-console-panel .acp-go{
  padding:9px 14px;border-radius:9px;border:1px solid rgba(139,92,246,.45);
  background:rgba(139,92,246,.2);color:#ede9fe;font-weight:700;font-size:12.5px;cursor:pointer
}
.agent-console-panel .acp-go:hover{background:rgba(139,92,246,.32)}
.agent-console-panel .acp-hint{font-size:11px;color:var(--muted);margin-top:8px;line-height:1.4}
.agent-console-panel .acp-hint code{color:#c4b5fd;font-size:10.5px}
/* Toast mature */
#toast.show{animation:toastIn .2s var(--ease)}
@keyframes toastIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.think-row{
  max-width:720px;width:100%;margin:4px auto 8px;display:flex;align-items:center;gap:12px;
  padding:8px 6px;color:var(--muted);font-size:12.5px;font-weight:500
}
.think-orb{
  width:26px;height:26px;border-radius:50%;position:relative;flex:0 0 auto;
  background:radial-gradient(circle at 32% 32%,#6ee7b7,var(--accent) 48%,#0a7a5f 82%);
  box-shadow:0 0 0 0 rgba(16,163,127,.4);animation:thinkPulse 1.35s ease-in-out infinite
}
.think-orb::after{
  content:"";position:absolute;inset:-5px;border-radius:50%;
  border:2px solid transparent;border-top-color:var(--violet);border-right-color:var(--cyan);
  animation:thinkSpin .9s linear infinite
}
.think-dots span{
  display:inline-block;width:5px;height:5px;margin:0 2px;border-radius:50%;background:var(--accent);
  animation:thinkDot 1.15s ease-in-out infinite
}
.think-dots span:nth-child(2){animation-delay:.14s}
.think-dots span:nth-child(3){animation-delay:.28s}
.think-label{color:var(--muted)}
.think-label b{color:var(--fg);font-weight:600}
@keyframes thinkPulse{0%,100%{box-shadow:0 0 0 0 rgba(16,163,127,.35);transform:scale(1)}50%{box-shadow:0 0 0 12px rgba(16,163,127,0);transform:scale(1.06)}}
@keyframes thinkSpin{to{transform:rotate(360deg)}}
@keyframes thinkDot{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}
.live-dot{
  width:7px;height:7px;border-radius:50%;background:var(--accent);display:inline-block;margin-right:6px;vertical-align:middle;
  box-shadow:0 0 0 0 rgba(16,163,127,.5);animation:thinkPulse 1.4s ease-in-out infinite
}
.novae-pill{
  display:inline-flex;align-items:center;gap:6px;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:650;
  border:1px solid rgba(167,139,250,.35);color:#c4b5fd;background:rgba(124,58,237,.12)
}
/* Infinite Wiki profile cards in chat */
.wiki-card{
  max-width:720px;width:100%;margin:8px auto 10px;border:1px solid rgba(16,163,127,.28);
  border-radius:12px;background:linear-gradient(165deg,rgba(16,163,127,.07),var(--panel));
  overflow:hidden;box-shadow:0 0 0 1px rgba(0,0,0,.2)
}
.wiki-card .wc-head{
  display:flex;align-items:flex-start;gap:10px;padding:10px 12px;border-bottom:1px solid var(--line)
}
.wiki-card .wc-badge{
  flex:0 0 auto;font-size:10px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;
  color:#041;background:var(--accent);border-radius:6px;padding:3px 7px
}
.wiki-card .wc-title{flex:1;min-width:0}
.wiki-card .wc-title b{display:block;font-size:12.5px;color:var(--fg);word-break:break-all}
.wiki-card .wc-title span{font-size:11px;color:var(--muted)}
.wiki-card .wc-ast{
  font-size:10px;font-weight:700;padding:2px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted)
}
.wiki-card .wc-ast.ts{color:#a78bfa;border-color:rgba(167,139,250,.4)}
.wiki-card .wc-sum{padding:8px 12px;font-size:12px;color:var(--muted);line-height:1.45;border-bottom:1px solid rgba(255,255,255,.04)}
.wiki-card .wc-syms{display:flex;flex-wrap:wrap;gap:6px;padding:10px 12px 12px}
.wiki-card .wc-sym{
  display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:rgba(0,0,0,.25);
  border-radius:8px;padding:5px 8px;font-size:11.5px;color:var(--text);cursor:pointer;transition:border-color .12s,background .12s
}
.wiki-card .wc-sym:hover{border-color:rgba(16,163,127,.5);background:rgba(16,163,127,.1);color:var(--fg)}
.wiki-card .wc-sym b{font-family:var(--mono);font-weight:600;font-size:11px;color:var(--accent)}
.wiki-card .wc-sym em{font-style:normal;color:var(--muted);font-size:10.5px}
.wiki-card .wc-actions{display:flex;flex-wrap:wrap;gap:6px;padding:0 12px 12px}
.wiki-card .wc-actions button{
  border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:8px;
  padding:6px 10px;font-size:11.5px;font-weight:600
}
.wiki-card .wc-actions button:hover{color:var(--fg);border-color:var(--line2);background:rgba(255,255,255,.04)}
.wiki-card .wc-actions button.primary{background:var(--accent);color:#041;border-color:transparent}
.wiki-slice{
  max-width:720px;width:100%;margin:6px auto 12px;border:1px solid var(--line);border-radius:10px;
  background:#0a0a0c;overflow:auto;max-height:280px
}
.wiki-slice pre{margin:0;padding:10px 12px;font-family:var(--mono);font-size:11.5px;line-height:1.45;color:#b7f0c6;white-space:pre}
.sess-ctl{font-size:12px;padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--muted);cursor:pointer}
.sess-ctl:hover{color:var(--fg);border-color:var(--muted)}
.sess-ctl.hot{color:#fbbf24;border-color:rgba(251,191,36,.45);background:rgba(251,191,36,.08)}
.sess-ctl.voice-on{
  color:#7dd3fc!important;border-color:rgba(11,132,254,.5)!important;
  background:rgba(11,132,254,.14)!important;box-shadow:0 0 0 1px rgba(11,132,254,.15)
}
.sess-ctl.voice-on:hover{background:rgba(11,132,254,.22)!important;color:#fff!important}
#btnEnd:hover{color:#f87171;border-color:rgba(248,113,113,.4)}
.worked-meta{
  max-width:720px;width:100%;margin:2px auto 0;padding:2px 4px 8px;
  font-size:11px;color:var(--muted);display:flex;align-items:center;gap:8px;flex-wrap:wrap
}
.worked-meta summary{cursor:pointer;list-style:none;user-select:none;color:var(--muted)}
.worked-meta summary::-webkit-details-marker{display:none}
.worked-meta summary:hover{color:var(--text)}
.worked-meta .wm-body{margin-top:6px;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--panel);font-size:11px;line-height:1.45;color:var(--muted);font-family:var(--mono);max-height:120px;overflow:auto;white-space:pre-wrap}
.subagents-panel{
  max-width:720px;width:100%;margin:8px auto 12px;border:1px solid var(--line);
  border-radius:10px;background:var(--panel);overflow:hidden
}
.subagents-panel > summary{
  display:flex;align-items:center;gap:8px;padding:10px 12px;cursor:pointer;list-style:none;
  font-size:12px;font-weight:550;color:var(--text);user-select:none
}
.subagents-panel > summary::-webkit-details-marker{display:none}
.subagents-panel > summary:hover{background:rgba(255,255,255,.03)}
.subagents-panel > summary .sa-label{flex:1}
.subagents-panel > summary .sa-chev{
  color:var(--muted);font-size:10px;margin-left:4px;transition:transform .15s ease
}
.subagents-panel[open] > summary .sa-chev{transform:rotate(90deg);color:var(--accent)}
.subagents-panel .spin{
  width:11px;height:11px;border:2px solid rgba(16,163,127,.2);border-top-color:var(--accent);
  border-radius:50%;animation:sa-spin .7s linear infinite;flex:0 0 auto
}
@keyframes sa-spin{to{transform:rotate(360deg)}}
.subagents-panel .sa-list{padding:0 8px 10px;display:flex;flex-direction:column;gap:2px}
.subagents-panel .sa-row,.sa-row{
  display:flex;align-items:center;gap:8px;padding:7px 8px;border-radius:8px;font-size:12px
}
.subagents-panel .sa-row:hover,.rail .sa-row:hover{background:rgba(255,255,255,.03)}
.sa-dot{width:7px;height:7px;border-radius:50%;flex:0 0 auto;background:var(--muted)}
.sa-dot.run{background:var(--accent);box-shadow:0 0 0 3px rgba(16,163,127,.15);animation:pulse 1.2s infinite}
.sa-dot.done{background:var(--accent);opacity:.85}
.sa-dot.ready{background:var(--cyan);opacity:.75}
.sa-dot.mesh{background:var(--violet);opacity:.8}
.sa-dot.fail{background:var(--red)}
.sa-name{font-weight:600;color:var(--fg);letter-spacing:.02em;font-size:12px}
.sa-meta{color:var(--muted);font-size:11px;margin-left:auto;text-align:right;max-width:55%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sa-src{font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);padding:1px 5px;border-radius:4px;border:1px solid var(--line);flex:0 0 auto}
.sa-src.headless{color:var(--violet);border-color:rgba(179,157,219,.35)}
.sa-src.design{color:var(--cyan);border-color:rgba(86,212,221,.35)}
.sa-src.latin{color:var(--accent);border-color:rgba(16,163,127,.3)}
.sa-src.harness{color:#fbbf24;border-color:rgba(251,191,36,.4);background:rgba(251,191,36,.08)}
.sa-row.harness-run{
  background:rgba(16,163,127,.08);border:1px solid rgba(16,163,127,.22);border-radius:8px;
  animation:saPulseRow 1.4s ease-in-out infinite
}
@keyframes saPulseRow{0%,100%{box-shadow:0 0 0 0 rgba(16,163,127,.15)}50%{box-shadow:0 0 0 4px rgba(16,163,127,0)}}
.sa-row .sa-pulse{
  width:14px;height:14px;border-radius:50%;border:2px solid transparent;
  border-top-color:var(--accent);border-right-color:var(--cyan);
  animation:sa-spin .7s linear infinite;flex:0 0 auto;margin-right:2px
}
.composer{padding:14px 18px 18px;border-top:1px solid var(--line);background:linear-gradient(180deg,transparent,rgba(0,0,0,.35) 40%,var(--bg))}
.composer-inner{max-width:720px;margin:0 auto;width:100%}
.presets{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}
.presets button{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:999px;padding:5px 11px;font-size:11px;font-weight:550;transition:all var(--t)}
.presets button:hover{color:var(--text);border-color:var(--line2);background:var(--panel)}
.box{
  display:flex;gap:8px;align-items:flex-end;
  background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.01)),var(--panel);
  border:1px solid var(--line);border-radius:16px;padding:10px 12px;
  transition:border-color var(--t), box-shadow var(--t);
  box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 8px 28px rgba(0,0,0,.2)
}
.box:focus-within{border-color:rgba(16,163,127,.55);box-shadow:var(--focus),0 1px 0 rgba(255,255,255,.04) inset,0 12px 32px rgba(16,163,127,.08)}
.box textarea{flex:1;min-height:48px;max-height:160px;resize:none;border:0;outline:0;background:transparent;padding:9px 6px;line-height:1.45;color:var(--text);font-size:14.5px}
.box textarea::placeholder{color:var(--muted)}
.box .iconbtn{border:0;background:transparent;border-radius:10px;padding:8px 10px;font-size:14px;color:var(--muted);transition:all var(--t)}
.box .iconbtn:hover{color:var(--text);background:rgba(255,255,255,.05)}
.box .iconbtn.hot{color:var(--red);background:rgba(248,113,113,.12)}
.box .send{
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;border:0;border-radius:11px;
  padding:11px 18px;font-weight:700;font-size:13px;min-width:72px;
  transition:background var(--t),transform .08s,box-shadow var(--t);
  box-shadow:0 2px 12px rgba(16,163,127,.3)
}
.box .send:hover{background:linear-gradient(180deg,#6ee7b7,#10a37f);box-shadow:0 4px 18px rgba(16,163,127,.4)}
.box .send:active{transform:scale(.97)}
.box .send:disabled{opacity:.35;cursor:not-allowed;transform:none;box-shadow:none}
.composer-bar{display:flex;align-items:center;gap:10px;margin-top:8px;padding:0 2px;position:relative}
.agent-pick-wrap{position:relative;flex:0 1 auto;min-width:0}
.agent-pick-btn{
  display:inline-flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:7px 12px;font-size:12.5px;font-weight:600;color:var(--fg);cursor:pointer;
  max-width:min(280px,55vw);min-width:140px
}
.agent-pick-btn:hover{border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.06)}
.agent-pick-btn .ap-dot{width:8px;height:8px;border-radius:50%;flex:0 0 auto;background:var(--accent)}
.agent-pick-btn .ap-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.agent-pick-btn .ap-chev{color:var(--muted);font-size:10px;margin-left:auto}
.agent-pick-menu{
  display:none;position:absolute;left:0;bottom:calc(100% + 6px);width:min(320px,92vw);
  max-height:min(52vh,380px);overflow:hidden;border:1px solid var(--line);border-radius:12px;
  background:var(--panel);box-shadow:0 16px 48px rgba(0,0,0,.55);z-index:80;flex-direction:column
}
.agent-pick-menu.open{display:flex}
.agent-pick-menu .ap-search{
  border:0;border-bottom:1px solid var(--line);border-radius:0;padding:10px 12px;background:transparent;
  font-size:12.5px;color:var(--fg);width:100%
}
.agent-pick-menu .ap-search:focus{outline:0}
.agent-pick-menu .ap-list{overflow-y:auto;flex:1;padding:4px;scrollbar-width:thin}
.agent-pick-menu .ap-group{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:8px 10px 4px}
.agent-pick-menu .ap-item{
  display:flex;align-items:flex-start;gap:10px;width:100%;text-align:left;border:0;background:transparent;
  border-radius:8px;padding:8px 10px;cursor:pointer;color:var(--text)
}
.agent-pick-menu .ap-item:hover,.agent-pick-menu .ap-item.on{background:rgba(16,163,127,.1)}
.agent-pick-menu .ap-item.kb{background:rgba(16,163,127,.16);box-shadow:inset 0 0 0 1px rgba(16,163,127,.35)}
.agent-pick-menu .ap-item b{display:block;font-size:12.5px;font-weight:650;color:var(--fg)}
.agent-pick-menu .ap-item small{display:block;font-size:11px;color:var(--muted);margin-top:2px;line-height:1.35}
.agent-pick-menu .ap-item .ap-live{font-size:10px;color:var(--accent);margin-left:auto;flex:0 0 auto;padding-top:2px}
.model-pick{display:none}
.composer-hint{font-size:11px;color:var(--muted);margin-left:auto}
.composer-hint kbd{font-family:var(--mono);font-size:10px;padding:1px 5px;border-radius:4px;border:1px solid var(--line);background:var(--panel);color:var(--muted)}
/* Integrations — Claude-style dropdown under chat */
.composer-tools{
  display:flex;align-items:center;gap:8px;margin-top:8px;padding:0 2px;flex-wrap:wrap;position:relative
}
.int-btn{
  display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:rgba(255,255,255,.03);
  color:var(--muted);border-radius:999px;padding:6px 12px;font-size:12px;font-weight:650;cursor:pointer;
  transition:all var(--t)
}
.int-btn:hover,.int-btn.open{
  color:var(--fg);border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1);box-shadow:var(--glow)
}
.int-btn .int-ico{font-size:13px;line-height:1}
.int-btn .int-count{
  font-size:10px;font-weight:700;color:var(--accent);background:rgba(16,163,127,.14);
  border-radius:999px;padding:1px 6px
}
.int-panel{
  display:none;position:absolute;left:0;bottom:calc(100% + 8px);width:min(420px,94vw);
  max-height:min(58vh,480px);z-index:90;flex-direction:column;
  background:rgba(14,14,18,.98);border:1px solid var(--line2);border-radius:16px;
  box-shadow:0 20px 56px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.04);
  backdrop-filter:blur(20px) saturate(1.1);overflow:hidden;animation:moreIn .16s var(--ease)
}
.int-panel.open{display:flex}
.int-panel .int-head{
  display:flex;align-items:center;gap:8px;padding:12px 14px 8px;border-bottom:1px solid var(--line)
}
.int-panel .int-head b{font-size:13px;color:var(--fg);letter-spacing:-.02em}
.int-panel .int-head span{font-size:11px;color:var(--muted)}
.int-panel .int-search{
  margin:10px 12px 6px;width:calc(100% - 24px);border:1px solid var(--line);border-radius:10px;
  background:rgba(0,0,0,.25);color:var(--fg);padding:9px 12px;font-size:12.5px
}
.int-panel .int-search:focus{outline:none;border-color:rgba(16,163,127,.45);box-shadow:var(--focus)}
.int-panel .int-cats{display:flex;flex-wrap:wrap;gap:4px;padding:4px 12px 8px}
.int-panel .int-cats button{
  border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:999px;
  padding:4px 9px;font-size:10.5px;font-weight:650;cursor:pointer
}
.int-panel .int-cats button.on,.int-panel .int-cats button:hover{
  color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)
}
.int-panel .int-list{overflow-y:auto;flex:1;padding:4px 8px 12px;scrollbar-width:thin}
.int-panel .int-group{
  font-size:10px;font-weight:750;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);
  padding:10px 8px 4px;opacity:.75
}
.int-panel .int-item{
  display:grid;grid-template-columns:36px 1fr auto;gap:10px;align-items:center;
  width:100%;text-align:left;border:0;background:transparent;border-radius:12px;
  padding:9px 10px;cursor:pointer;color:var(--text);transition:background var(--t)
}
.int-panel .int-item:hover{background:rgba(255,255,255,.05)}
.int-panel .int-item.featured{box-shadow:inset 0 0 0 1px rgba(16,163,127,.18)}
.int-panel .int-item .ii{
  width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
  background:rgba(255,255,255,.05);border:1px solid var(--line);font-size:16px
}
.int-panel .int-item b{display:block;font-size:12.5px;font-weight:650;color:var(--fg);letter-spacing:-.01em}
.int-panel .int-item small{display:block;font-size:11px;color:var(--muted);margin-top:2px;line-height:1.35}
.int-panel .int-item .use{
  border:1px solid rgba(16,163,127,.35);background:rgba(16,163,127,.12);color:#6ee7b7;
  border-radius:8px;padding:5px 10px;font-size:11px;font-weight:700;white-space:nowrap
}
.int-panel .int-item:hover .use{background:rgba(16,163,127,.22);color:#fff}
.int-panel .int-empty{padding:24px 12px;text-align:center;color:var(--muted);font-size:12.5px}
.int-chip-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.int-chip{
  border:1px solid var(--line);background:rgba(255,255,255,.02);color:var(--muted);
  border-radius:999px;padding:4px 9px;font-size:11px;font-weight:650;cursor:pointer
}
.int-chip:hover{color:#6ee7b7;border-color:rgba(16,163,127,.35);background:rgba(16,163,127,.1)}
.int-chip.hot{color:#6ee7b7;border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.12)}
.slash-menu,.mention-menu{
  display:none;margin:0 0 8px;border:1px solid var(--line);border-radius:10px;background:var(--panel);
  overflow:hidden;max-height:200px;overflow-y:auto
}
.slash-menu.open,.mention-menu.open{display:block}
.slash-menu button,.mention-menu button{
  display:flex;align-items:center;gap:10px;width:100%;text-align:left;border:0;background:transparent;
  padding:9px 12px;font-size:12px;color:var(--text);border-bottom:1px solid var(--line)
}
.slash-menu button:last-child,.mention-menu button:last-child{border-bottom:0}
.slash-menu button:hover,.slash-menu button.on,
.mention-menu button:hover,.mention-menu button.on{background:rgba(16,163,127,.08)}
.slash-menu button b,.mention-menu button b{font-weight:600;min-width:72px;font-family:var(--mono);font-size:11px;color:var(--accent)}
.slash-menu button span,.mention-menu button span{color:var(--muted);font-size:11px;flex:1}
.mention-menu button .mdot{width:6px;height:6px;border-radius:50%;background:var(--cyan);flex:0 0 auto}
.mention-menu button .mdot.headless{background:var(--violet)}
.mention-menu button .mdot.latin{background:var(--accent)}
/* Clean dispatch result card in transcript */
.dispatch-card{
  max-width:720px;width:100%;margin:6px auto 10px;padding:10px 12px;border-radius:10px;
  border:1px solid rgba(16,163,127,.28);background:rgba(16,163,127,.06);
  font-size:12px;line-height:1.45;color:var(--text)
}
.dispatch-card .dc-h{display:flex;align-items:center;gap:8px;font-weight:600;color:var(--fg);margin-bottom:4px}
.dispatch-card .dc-h .ok{color:var(--accent);font-size:11px;font-weight:700;letter-spacing:.03em}
.dispatch-card .dc-agents{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.dispatch-card .dc-chip{
  font-family:var(--mono);font-size:11px;padding:3px 8px;border-radius:999px;
  border:1px solid var(--line);background:var(--bg);color:var(--fg)
}
.dispatch-card .dc-chip.fail{border-color:rgba(240,113,120,.4);color:var(--red)}
.dispatch-card .dc-note{margin-top:6px;font-size:11px;color:var(--muted)}
.walkthrough{margin:8px 10px;padding:0;border-radius:10px;border:1px solid var(--line);background:var(--panel);overflow:hidden}
.walkthrough .wt-h{padding:10px 12px 6px;font-size:11px;letter-spacing:.04em;color:var(--muted);font-weight:600;display:flex;justify-content:space-between;align-items:center}
.walkthrough .wt-body{padding:0 8px 10px;max-height:200px;overflow:auto}
.walkthrough .wt-step{display:flex;gap:8px;padding:6px 4px;font-size:12px;line-height:1.4;border-left:2px solid transparent;margin-left:4px;padding-left:8px}
.walkthrough .wt-step.on{border-left-color:var(--accent);color:var(--text)}
.walkthrough .wt-step.done{border-left-color:rgba(16,163,127,.35);color:var(--muted)}
.walkthrough .wt-n{flex:0 0 16px;font-size:10px;font-weight:700;color:var(--muted);padding-top:2px;font-family:var(--mono)}
.walkthrough .wt-step.on .wt-n{color:var(--accent)}
.walkthrough .wt-empty{font-size:11px;color:var(--muted);padding:4px 6px;line-height:1.45}
.rail-roster{margin:8px 10px;padding:0;border-radius:10px;border:1px solid var(--line);background:var(--panel);overflow:hidden}
.rail-roster .rr-h{padding:10px 12px 6px;font-size:11px;letter-spacing:.04em;color:var(--muted);font-weight:600;display:flex;justify-content:space-between;align-items:center;gap:8px}
.rail-roster .rr-meta{display:flex;align-items:center;gap:6px;font-weight:500}
.rail-roster .rr-body{padding:0 6px 10px;max-height:260px;overflow:auto}
.rail-roster .rr-empty{font-size:11px;color:var(--muted);padding:6px 8px;line-height:1.4}
.rail-roster .rr-sec{font-size:10px;letter-spacing:.05em;color:var(--muted);padding:8px 8px 4px;font-weight:600;text-transform:uppercase}
.mesh-pill{
  font-size:10px;font-weight:700;letter-spacing:.03em;padding:2px 7px;border-radius:999px;
  border:1px solid rgba(86,212,221,.35);color:var(--cyan);background:rgba(86,212,221,.08)
}
.mesh-pill.off{border-color:var(--line);color:var(--muted);background:transparent}
.sa-count{font-weight:500;color:var(--muted)}
.rail .card{margin:8px 10px;padding:12px 13px;border-radius:11px;border:1px solid var(--line);background:var(--panel)}
.rail .card h3{margin:0 0 9px;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:650}
.rail .grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.rail .grid div{background:var(--bg);border-radius:8px;padding:8px}
.rail .grid span{display:block;font-size:10px;color:var(--muted)}
.rail .grid strong{font-size:14px;font-weight:600}
.rail .btns{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.rail .btns button{border:1px solid var(--line);background:transparent;border-radius:7px;padding:6px 9px;font-size:11px;font-weight:500;color:var(--muted)}
.rail .btns button:hover{color:var(--text);border-color:var(--line2)}
.rail .hint{font-size:11px;color:var(--muted);line-height:1.4}
.svc{padding:8px;border:1px solid var(--line);border-radius:10px;margin-bottom:6px;background:var(--bg)}
.svc .row{display:flex;justify-content:space-between;align-items:center;gap:6px}
.svc b{font-size:12px}
.svc .st{font-size:10px;font-weight:800}
.svc .st.live{color:var(--accent)}
.svc .st.down{color:var(--red)}
.svc .act{display:flex;gap:6px;margin-top:6px}
.svc .act button,.svc .act a{font-size:11px;font-weight:650;padding:5px 8px;border-radius:7px;border:1px solid var(--line);background:var(--panel2);color:var(--text);text-decoration:none}
.hint{font-size:11px;color:var(--muted);line-height:1.45;padding:4px 2px}
.live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent);margin-right:5px;animation:pulse 1.2s infinite}
@keyframes pulse{50%{opacity:.35}}
.toast{
  position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(8px);
  background:rgba(18,18,24,.96);border:1px solid var(--line);color:var(--text);
  padding:11px 18px;border-radius:12px;font-size:13px;font-weight:550;z-index:10000;
  box-shadow:var(--shadow-lg);display:none;max-width:min(480px,92vw);text-align:center;
  backdrop-filter:blur(16px);opacity:0;transition:opacity .2s var(--ease),transform .2s var(--ease)
}
.toast.show{display:block;opacity:1;transform:translateX(-50%) translateY(0)}
.toast.ok{border-color:rgba(16,163,127,.45);color:#86efac;box-shadow:var(--glow)}
.toast.err{border-color:rgba(240,113,120,.45);color:#fca5a5}
.gate{position:fixed;inset:0;z-index:10050;background:rgba(0,0,0,.92);backdrop-filter:blur(14px) saturate(1.1);display:none;align-items:center;justify-content:center;padding:20px;pointer-events:none;visibility:hidden}
.gate.open{display:flex;pointer-events:auto;visibility:visible}
.gate .card{
  width:100%;max-width:400px;background:linear-gradient(165deg,rgba(255,255,255,.04),transparent 40%),var(--panel);
  border:1px solid var(--line);border-radius:20px;padding:28px;box-shadow:var(--shadow-lg);pointer-events:auto;position:relative;z-index:1
}
.gate h2{margin:0 0 6px;font-size:20px;letter-spacing:-.04em;font-weight:700;color:var(--fg)}
.gate p{margin:0 0 14px;color:var(--muted);font-size:13px;line-height:1.5}
.gate label{display:block;font-size:11px;color:var(--muted);margin:12px 0 5px;font-weight:650;letter-spacing:.02em;text-transform:uppercase}
.gate input{width:100%;padding:11px 13px;border-radius:11px;border:1px solid var(--line);background:#0a0a0e;margin-bottom:4px;color:var(--fg);transition:border-color var(--t),box-shadow var(--t)}
.gate input:focus{outline:0;border-color:rgba(16,163,127,.5);box-shadow:var(--focus)}
.gate .primary{
  width:100%;margin-top:16px;border:0;border-radius:11px;padding:12px;font-weight:700;
  background:linear-gradient(180deg,#34d399,var(--accent));color:#041;cursor:pointer;
  box-shadow:0 4px 20px rgba(16,163,127,.3);transition:transform var(--t),box-shadow var(--t)
}
.gate .primary:hover{box-shadow:0 6px 28px rgba(16,163,127,.4)}
.gate .primary:disabled{opacity:.55;cursor:wait}
.gate .secondary{width:100%;margin-top:8px;border:1px solid var(--line);border-radius:8px;padding:10px;font-weight:500;background:transparent;color:var(--muted);cursor:pointer}
.gate .err{color:#fca5a5;font-size:12px;margin-top:10px;min-height:18px;line-height:1.4;white-space:pre-wrap}
.tabs{display:flex;gap:6px;margin-bottom:10px}
.tabs button{flex:1;border:1px solid var(--line);background:transparent;border-radius:8px;padding:8px;font-size:12px;font-weight:500;color:var(--muted)}
.tabs button.on{color:var(--text);border-color:rgba(16,163,127,.4);background:rgba(16,163,127,.1)}
/* Computer (default) */
body.device-computer .phone-nav{display:none}
body.device-computer .phone-only{display:none!important}
/* scrim only when rail drawer open on narrow computer */
body.device-computer:not(.rail-open) .scrim{display:none!important}
/* Tablet: keep 3-col when wide enough; drawer if cramped */
body.device-tablet .app{grid-template-columns:220px minmax(0,1fr) 280px;grid-template-rows:52px 1fr}
body.device-tablet .phone-nav{display:none}
body.device-tablet .phone-only{display:none!important}
body.device-tablet .menu-btn.rail-toggle{display:inline-flex}
/* Phone: single column chat + drawers + bottom nav */
body.device-phone{overflow:hidden}
body.device-phone .app{
  grid-template-columns:1fr;
  grid-template-rows:52px 1fr 56px;
  height:100dvh;
  padding-bottom:env(safe-area-inset-bottom,0);
}
body.device-phone .top{padding:0 10px;gap:8px}
body.device-phone .top-meta{display:none}
body.device-phone .side{
  position:fixed;left:0;top:52px;bottom:56px;width:min(88vw,320px);z-index:40;
  transform:translateX(-105%);transition:transform .22s ease;
  border-right:1px solid var(--line);border-bottom:0;max-height:none;
  box-shadow:8px 0 30px rgba(0,0,0,.4);
}
body.device-phone.side-open .side{transform:translateX(0)}
body.device-phone .rail{
  position:fixed;right:0;top:52px;bottom:56px;width:min(90vw,340px);z-index:40;
  transform:translateX(105%);transition:transform .22s ease;
  border-left:1px solid var(--line);display:flex;
  box-shadow:-8px 0 30px rgba(0,0,0,.4);
}
body.device-phone.rail-open .rail{transform:translateX(0)}
body.device-phone .main{grid-row:2;min-height:0}
body.device-phone .main-h{padding:8px 12px;flex-wrap:wrap;gap:6px;min-height:auto}
body.device-phone .main-h h1{font-size:14px}
body.device-phone .main-h select{margin-left:0;width:100%;max-width:100%}
body.device-phone .transcript{padding:12px}
body.device-phone .habitat{display:none!important}
body.device-phone.habitat-open .main-stage{flex-direction:column}
body.device-tablet .habitat{width:min(280px,40vw)}
body.device-phone .msg .mb.term{max-height:min(40vh,280px);font-size:12.5px}
body.device-phone .msg .mb.prose{font-size:13.5px}
body.device-phone .composer{padding:8px 10px calc(10px + env(safe-area-inset-bottom,0))}
body.device-phone .composer-bar{flex-wrap:wrap}
body.device-phone .composer-hint{display:none}
body.device-phone .box{padding:8px;border-radius:12px}
body.device-phone .box textarea{min-height:44px;font-size:16px} /* prevent iOS zoom */
body.device-phone .box .send{padding:12px 14px;min-height:44px}
body.device-phone .actions button{padding:12px;min-height:48px}
body.device-phone .presets{gap:8px}
body.device-phone .presets button{padding:8px 12px;font-size:12px}
body.device-phone .computer-only{display:none!important}
.phone-nav{
  display:none;grid-column:1;grid-row:3;border-top:1px solid var(--line);
  background:rgba(17,17,19,.96);backdrop-filter:blur(12px);
  align-items:stretch;justify-content:space-around;padding:4px 6px env(safe-area-inset-bottom,4px);
  z-index:50;
}
body.device-phone .phone-nav{display:flex}
.phone-nav button{
  flex:1;border:0;background:transparent;color:var(--muted);font-size:10px;font-weight:700;
  padding:6px 4px;border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:2px;
}
.phone-nav button span{font-size:18px;line-height:1}
.phone-nav button.on{color:var(--accent);background:#0c1f14}
.scrim{display:none;position:fixed;inset:52px 0 56px 0;background:rgba(0,0,0,.45);z-index:30}
body.device-phone.side-open .scrim,body.device-phone.rail-open .scrim{display:block}
.device-chip.phone{color:#7dd3fc;border-color:#0e7490;background:#083344}
.device-chip.tablet{color:#c4b5fd;border-color:#6d28d9;background:#2e1065}
.device-chip.computer{color:#86efac;border-color:#166534;background:#052e16}
.menu-btn{display:none;border:1px solid var(--line);background:var(--panel);border-radius:8px;padding:8px 10px;font-size:12px;font-weight:700;align-items:center;gap:4px;color:var(--text);cursor:pointer}
body.device-phone .menu-btn{display:inline-flex}
/* Side toggle visible on phone always; computer only when CSS media shows it */
body.device-computer .menu-btn.side-toggle{display:none}
body.device-computer .menu-btn.rail-toggle{display:none}
/* Right Context rail MUST stay visible on computer (was blank: display:none under 1100px) */
.rail{min-width:240px;display:flex;flex-direction:column;min-height:0;overflow:hidden}
body.device-computer .rail{display:flex!important}
@media(max-width:1100px){
  /* Shrink columns — never hide Context on desktop */
  body.device-computer .app{grid-template-columns:200px minmax(0,1fr) 260px}
  body.device-computer .rail{min-width:220px}
}
@media(max-width:900px){
  /* Agents side becomes a drawer (was display:none — users could not pick agents) */
  body.device-computer .app{grid-template-columns:minmax(0,1fr) 240px}
  body.device-computer .side{
    display:flex!important;position:fixed;left:0;top:48px;bottom:0;
    width:min(88vw,300px);z-index:45;max-height:none;
    transform:translateX(-105%);transition:transform .2s ease;
    border-right:1px solid var(--line);box-shadow:8px 0 30px rgba(0,0,0,.45);
    background:var(--bg2);
  }
  body.device-computer.side-open .side{transform:translateX(0)}
  body.device-computer .menu-btn.side-toggle{display:inline-flex!important}
  body.device-computer.side-open .scrim{display:block!important;z-index:35}
  body.device-computer .rail{display:flex!important;min-width:200px}
}
@media(max-width:720px){
  /* Very narrow: rail as overlay drawer, with toggle */
  body.device-computer .app{grid-template-columns:1fr}
  body.device-computer .side{
    display:flex!important;position:fixed;left:0;top:48px;bottom:0;
    width:min(90vw,300px);z-index:45;
    transform:translateX(-105%);transition:transform .2s ease;
  }
  body.device-computer.side-open .side{transform:translateX(0)}
  body.device-computer .menu-btn.side-toggle{display:inline-flex!important}
  body.device-computer .rail{
    position:fixed;right:0;top:48px;bottom:0;width:min(92vw,320px);z-index:40;
    transform:translateX(105%);transition:transform .2s ease;
    border-left:1px solid var(--line);box-shadow:-8px 0 30px rgba(0,0,0,.45);
    display:flex!important;
  }
  body.device-computer.rail-open .rail{transform:translateX(0)}
  body.device-computer .menu-btn.rail-toggle{display:inline-flex}
  body.device-computer.rail-open .scrim{display:block!important;z-index:30}
  body.device-computer.side-open .scrim{display:block!important;z-index:35}
}
</style>
<script src="/auth/client.js"></script>
</head>
<body class="device-computer habitat-open">
<div class="boot-splash" id="bootSplash" aria-hidden="false">
  <div class="boot-mark">P</div>
  <div class="boot-title">POCKET</div>
  <div class="boot-sub">Native Agent OS · remote browser · phone IoT · our clouds</div>
  <div class="boot-bar" aria-hidden="true"><i></i></div>
</div>
<div class="scrim" id="scrim" onclick="closeDrawers()"></div>
<div class="browser-layer" id="browserLayer" aria-hidden="true">
  <div class="browser-chrome" role="toolbar" aria-label="POCKET Browser">
    <button type="button" class="b-back" id="btnBrowserDesk" onclick="closeBrowser()" title="Back to POCKET desk">← Desk</button>
    <button type="button" class="b-ico" onclick="browserHistBack()" title="Page back">◀</button>
    <button type="button" class="b-ico" onclick="browserHistFwd()" title="Page forward">▶</button>
    <button type="button" class="b-ico" onclick="browserReload()" title="Reload">↻</button>
    <input id="browserUrl" type="url" placeholder="https://… or /studio" autocomplete="off" spellcheck="false"
      onkeydown="if(event.key==='Enter'){event.preventDefault();browserGo()}"/>
    <button type="button" class="b-go" onclick="browserGo()" title="Load in browser pane">Go</button>
    <button type="button" class="b-ico" onclick="browserOpenNewTab()" title="Open in a new tab">New tab</button>
  </div>
  <div class="browser-quick">
    <button type="button" onclick="browserQuick('/tour')">Overview</button>
    <button type="button" onclick="browserQuick('/studio/voice')">Voice Studio</button>
    <button type="button" onclick="browserQuick('/phone')">Phone</button>
    <button type="button" onclick="browserQuick('/os')">Agent OS</button>
    <button type="button" onclick="browserQuick('/developers')">API · MCP</button>
    <button type="button" onclick="remoteBrowserOpenQuick()">Our remote browser</button>
    <button type="button" onclick="browserQuick('/studio')">Studio</button>
    <button type="button" onclick="browserQuick('/desk')">This desk</button>
  </div>
  <div class="browser-stage">
    <iframe id="browserFrame" title="POCKET Browser" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox allow-downloads allow-modals"></iframe>
    <div class="browser-blocked" id="browserBlocked">
      <h3>This site won’t load inside the pane</h3>
      <p>POCKET desk stays open. Use <b style="color:var(--fg)">New tab</b> for sites that block embedding — or pick Studio / Overview above (those open in-pane with ← Desk always available).</p>
      <button type="button" class="btn-primary" onclick="browserOpenNewTab()">Open in new tab</button>
    </div>
  </div>
</div>
<div class="app">
  <header class="top">
    <button type="button" class="top-back" id="btnBack" onclick="goAppBack()" title="Back">← Back</button>
    <button type="button" class="menu-btn side-toggle" id="btnAgents" onclick="toggleSide()" aria-label="Agents" title="Agents">☰ Agents</button>
    <div class="brand" onclick="goDeskHome()" style="cursor:pointer" title="POCKET desk"><div class="mark">P</div>POCKET</div>
    <nav class="top-links" id="appTabs" aria-label="POCKET app">
      <!-- Primary ops — always visible, each its own surface -->
      <a href="#" class="on-desk" data-tab="desk" data-group="primary" onclick="event.preventDefault();showAppTab('desk')" title="Chat · Working board · agents">Desk</a>
      <a href="#" data-tab="habitat" data-group="primary" onclick="event.preventDefault();showAppTab('habitat')" title="Agents live on this floor">Habitat</a>
      <a href="#" data-tab="screen" data-group="primary" onclick="event.preventDefault();showAppTab('screen')" title="Screen eyes · VComputer">Screen</a>
      <a href="#" data-tab="working" data-group="primary" onclick="event.preventDefault();showAppTab('working')" title="Ops board — buy · analyze · reserve">Working</a>
      <a href="#" data-tab="browser" data-group="primary" onclick="event.preventDefault();showAppTab('browser')" title="In-app browser">Browser</a>
      <a href="#" data-tab="remote" data-group="primary" onclick="event.preventDefault();showAppTab('remote')" title="Host Edge remote browser">Remote</a>
      <a href="#" data-tab="phone" data-group="primary" onclick="event.preventDefault();showAppTab('phone')" title="Aether phone · IoT · pair">Phone</a>
      <a href="#" data-tab="platform" data-group="primary" onclick="event.preventDefault();showAppTab('platform')" title="Sovereign stack · clouds · OS">Platform</a>
      <span class="tab-sep" aria-hidden="true"></span>
      <div class="tab-more-wrap">
        <button type="button" class="tab-more-btn" id="tabMoreBtn" onclick="toggleTabMore(event)" aria-haspopup="true" aria-expanded="false" title="Studios &amp; systems">More <span class="chev">▾</span></button>
        <div class="tab-more-menu" id="tabMoreMenu" role="menu" aria-label="More surfaces">
          <div class="mm-label">Studios</div>
          <a href="#" data-tab="work" role="menuitem" onclick="event.preventDefault();showAppTab('work');closeTabMore()" title="Design agent loops"><span>Work Studio</span><small>Design loops → run on desk</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="studio" role="menuitem" onclick="event.preventDefault();showAppTab('studio');closeTabMore()" title="Record · viral · ship"><span>Product Studio</span><small>Record · viral pack · agent ship</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="loomgraph" role="menuitem" onclick="event.preventDefault();showAppTab('loomgraph');closeTabMore()" title="LOOMGRAPH — graphs + loops harness"><span>LOOMGRAPH</span><small>See the graph · run the loop</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="creative" role="menuitem" onclick="event.preventDefault();showAppTab('creative');closeTabMore()" title="Friendly AI chat · image · video · blog"><span>Creative Studio</span><small>Chat · image · video · blog · social</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="community" role="menuitem" onclick="event.preventDefault();showAppTab('community');closeTabMore()" title="Intentional public shares"><span>Community</span><small>What users share on purpose</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="voice_studio" role="menuitem" onclick="event.preventDefault();showAppTab('voice_studio');closeTabMore()" title="V2V canvas"><span>Voice Studio</span><small>Canvas · persona · code snap</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="lab" role="menuitem" onclick="event.preventDefault();showAppTab('lab');closeTabMore()" title="Studio · Capsules · Life · Phone readiness"><span>Lab</span><small>Readiness · capsules · ship loop</small><span class="mm-go">→</span></a>
          <div class="mm-label">Systems</div>
          <a href="#" data-tab="os" role="menuitem" onclick="event.preventDefault();showAppTab('os');closeTabMore()" title="Every system first-class"><span>Agent OS</span><small>Systems map · parity</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="mcp" role="menuitem" onclick="event.preventDefault();showAppTab('mcp');closeTabMore()" title="MCP tools &amp; API"><span>API · MCP</span><small>Keys · tools · developers</small><span class="mm-go">→</span></a>
          <a href="#" data-tab="curiosities" role="menuitem" onclick="event.preventDefault();showAppTab('curiosities');closeTabMore()"><span>Curiosities</span><small>Dream · Duel · lab</small><span class="mm-go">→</span></a>
          <div class="mm-foot">Each opens its own panel — never merges into Desk.</div>
        </div>
      </div>
    </nav>
    <span class="chip device-chip computer" id="deviceChip" title="Client device">Computer</span>
    <div class="grow"></div>
    <div class="top-meta" id="topMeta"></div>
    <span class="chip wallet-chip" id="walletChip" title="Operator wallet · POCK">POCK —</span>
    <span class="chip" id="userChip">signed out</span>
    <button type="button" class="icon" id="logoutBtn" onclick="doLogout()" title="Sign out" style="display:none">Out</button>
    <button type="button" class="menu-btn on" id="btnHabitat" onclick="toggleHabitat()" aria-label="Agent habitat" title="Habitat floor (open/close)">Habitat</button>
    <button type="button" class="menu-btn" id="btnScreenCol" onclick="toggleScreenCol()" aria-label="Screen column" title="Screen · VComputer (open/close)">Screen</button>
    <button type="button" class="menu-btn rail-toggle" id="btnSys" onclick="toggleWorkspacePanel()" aria-label="Workspace panel" title="Workspace (open/close)">Workspace</button>
  </header>

  <aside class="side" id="sidePanel">
    <div class="side-h"><span>Agents</span><button type="button" class="icon" onclick="refreshSessions();refreshStack()" title="Refresh">↻</button></div>
    <div class="side-scroll">
    <div class="stack-card" id="stackCard" title="Status">
      <div class="sk"><b>App</b><span class="on" id="stPocket">ready</span></div>
      <div class="sk"><b>NEXUS</b><span class="off" id="stNexus">…</span></div>
      <div class="sk"><b>MESIE</b><span class="off" id="stMesie">…</span></div>
      <div class="sk"><b>Mesh</b><span class="off" id="stMesh">…</span></div>
    </div>
    <div class="actions">
      <button type="button" onclick="pickAgent('codex')" title="OpenAI Codex coding agent"><b>Codex</b><small>Code on this host</small></button>
      <button type="button" onclick="pickAgent('grok')" title="Grok coding &amp; research agent"><b>Grok</b><small>Code &amp; research</small></button>
      <button type="button" onclick="pickAgent('claude')" title="Claude Agent SDK loop (Read/Edit/Bash) · streams to desk"><b>Claude</b><small>Agent SDK · tools</small></button>
      <button type="button" onclick="pickAgent('assist')" title="Digital assistant — real-life help"><b>Assistant</b><small>Life · research · ops</small></button>
      <button type="button" onclick="pickAgent('studio')" title="Product Studio agent — record · viral · ship"><b>Studio</b><small>Record → ship demos</small></button>
      <button type="button" onclick="pickAgent('muse_spark')" title="Muse Spark — Meta multimodal reasoning · parallel lanes"><b>Muse Spark</b><small>Multimodal · research lanes</small></button>
      <button type="button" onclick="pickAgent('auro')" title="Auro14B local LMR + meaning"><b>Auro</b><small>Local LMR · meaning</small></button>
      <button type="button" onclick="pickAgent('voice')" title="Aria — real voice product · lists · life ops · screen · speak-back"><b>Aria · Voice</b><small>Talk · act · speak back</small></button>
      <button type="button" onclick="startWorkingMode()" title="Working board — multi-part real work with tools and a live table"><b>Working</b><small>Board · buy · analyze · reserve</small></button>
      <button type="button" onclick="pickAgent('plan')"><b>Plan</b><small>Planning only</small></button>
      <button type="button" onclick="pickAgent('build')" title="Plan → code → test → ship"><b>Build</b><small>Multi-agent ship loop</small></button>
      <button type="button" onclick="pickAgent('genetic')" title="Internal models as modules · genetic flow evolves which run"><b>Genetic</b><small>Models · evolve · express</small></button>
      <button type="button" onclick="location.href='/mail'" title="Agent email accounts + inboxes"><b>Mail</b><small>Agent inboxes</small></button>
      <button type="button" onclick="location.href='/docs'" title="Docs hub + how-to guides"><b>Docs</b><small>How-to · catalog</small></button>
      <button type="button" onclick="showAppTab('lab')" title="Lab readiness — Studio · Capsules · Life · Phone"><b>Lab</b><small>Readiness map</small></button>
      <button type="button" onclick="activateNovae('CODEX_NOVAE')" title="Codex hands in platform workspace"><b>Codex Novae</b><small>Hands · code + forge</small></button>
      <button type="button" onclick="activateNovae('GROK_NOVAE')" title="Grok hands in platform workspace"><b>Grok Novae</b><small>Hands · browser + day ops</small></button>
      <button type="button" onclick="pickAgent('wiki')"><b>Infinite Wiki</b><small>Codebase profile cards</small></button>
      <button type="button" onclick="pickAgent('dual')"><b>Dual loop</b><small>Talk while work runs</small></button>
      <button type="button" onclick="pickAgent('web')"><b>Web</b><small>Search · fetch</small></button>
      <button type="button" onclick="pickAgent('git')"><b>Git</b><small>Vault repos</small></button>
      <button type="button" class="more-btn" id="moreAgentsBtn" onclick="toggleMoreAgents()">More agents ▾</button>
      <div class="more-agents" id="moreAgents" role="region" aria-label="More agents">
        <button type="button" onclick="pickAgent('coding_swarm')" title="Sophia · Solver · Twin — artifacts to pixel memory"><b>Coding Swarm</b><small>Multi-agent · pixel artifacts</small></button>
        <button type="button" onclick="pickAgent('swarm')"><b>Always-on Swarm</b><small>Background pulses</small></button>
        <button type="button" onclick="pickAgent('use_case')"><b>Use cases</b><small>Playbooks</small></button>
        <button type="button" onclick="pickAgent('custom_agent')"><b>Custom agent</b><small>Builder · tools</small></button>
        <button type="button" onclick="pickAgent('offload')"><b>Offload</b><small>Background queue</small></button>
        <button type="button" onclick="pickAgent('cowork')"><b>Cowork</b><small>Desk + record</small></button>
        <button type="button" onclick="pickAgent('desktop')"><b>Desktop</b><small>Open apps</small></button>
        <button type="button" onclick="pickAgent('browser')"><b>Browser agent</b><small>Edge · X · Copilot</small></button>
        <button type="button" onclick="pickAgent('capture')"><b>Capture</b><small>Screenshot</small></button>
        <button type="button" onclick="pickAgent('vision')" title="OCULUS — screen eyes, UI map, OCR, click-by-name"><b>Vision</b><small>OCULUS · see · map · act</small></button>
        <button type="button" onclick="pickAgent('github')" title="First-class GitHub via signed-in gh"><b>GitHub</b><small>repos · issues · PRs · gh</small></button>
        <button type="button" onclick="pickAgent('repos')"><b>Repos</b><small>Git · GitHub tools</small></button>
        <button type="button" onclick="pickAgent('nexus')"><b>NEXUS</b><small>Intelligence tools</small></button>
        <button type="button" onclick="pickAgent('mesie')"><b>MESIE</b><small>Spectral · compute</small></button>
        <button type="button" onclick="pickAgent('auro')"><b>Auro14B</b><small>Local model</small></button>
        <button type="button" onclick="pickAgent('wsl_native')"><b>WSL</b><small>Linux console</small></button>
        <button type="button" onclick="pickAgent('python')"><b>Python</b><small>Host CLI</small></button>
        <button type="button" onclick="pickAgent('python_wsl')"><b>Py·WSL</b><small>python3 in Debian</small></button>
        <button type="button" class="admin-only" onclick="pickAgent('term')"><b>Term</b><small>PowerShell</small></button>
        <button type="button" onclick="pickAgent('archon')"><b>ARCHON</b><small>Orchestrator</small></button>
        <button type="button" onclick="pickAgent('guppy')"><b>Guppy</b><small>Local helper</small></button>
        <button type="button" onclick="showAppTab('work')"><b>Work Studio</b><small>Design loops → run on desk</small></button>
        <button type="button" onclick="showAppTab('voice_studio')"><b>Voice Studio</b><small>Canvas · persona · code snap</small></button>
        <button type="button" onclick="runWorkflow('remote_loop')"><b>Remote browser</b><small>Beat theirs · Edge + Fusion</small></button>
        <button type="button" onclick="runWorkflow('phone_iot')"><b>Phone · IoT</b><small>Pair + home devices</small></button>
        <button type="button" onclick="showAppTab('curiosities')"><b>Curiosities</b><small>Dream · Duel</small></button>
        <button type="button" onclick="showAppTab('studio')"><b>Studio</b><small>Product demos</small></button>
        <button type="button" onclick="showAppTab('lab')"><b>Lab</b><small>Capsules · readiness</small></button>
        <button type="button" onclick="pickAgent('studio')"><b>Studio agent</b><small>Record → ship</small></button>
        <button type="button" onclick="showAppTab('platform')"><b>Platform</b><small>Sovereign · clouds · OS</small></button>

        <button type="button" class="admin-only" onclick="pickAgent('shell')"><b>Shell</b><small>Host PS</small></button>
      </div>
    </div>
    <div class="toolrow">
      <label class="btn" for="fileInput">Upload</label>
      <input id="fileInput" type="file" multiple />
      <div class="hint" id="uploadNote"></div>
    </div>
    <div class="side-h" style="padding-top:4px"><span>Sessions</span></div>
    <div class="slist" id="slist"><div class="hint">Sign in, then start Codex or Grok. Sessions appear here — click to open.</div></div>
    </div>
  </aside>

  <section class="main">
    <div class="main-h">
      <h1 id="mainTitle">Main desk</h1>
      <span class="tag" id="mainTag">—</span>
      <span class="tag" id="mainWs">workspace</span>
      <select id="wsSelect"></select>
      <div class="grow"></div>
      <button type="button" class="icon sess-ctl" id="btnVoiceEngine" onclick="toggleVoiceEngine()" title="Activate voice engine — this agent talks and listens" style="display:none">🎙 Voice engine</button>
      <button type="button" class="icon sess-ctl" id="btnStop" onclick="stopActiveSession()" title="Stop work (keep this chat)" style="display:none">Stop</button>
      <button type="button" class="icon sess-ctl" id="btnEnd" onclick="endActiveSession()" title="End this chat" style="display:none">End</button>
    </div>
    <div class="main-stage" id="mainStage">
    <div class="transcript" id="transcript">
      <div class="empty" id="emptyHome">
        <div class="mark">P</div>
        <h2>Main desk</h2>
        <p>This is home base — seat an agent to chat and run tools. Other surfaces stay their own tabs (never merge into this chat).</p>
        <div class="empty-actions">
          <button type="button" data-mode="codex">Codex</button>
          <button type="button" data-mode="grok">Grok</button>
          <button type="button" data-mode="claude">Claude</button>
          <button type="button" data-mode="assist">Assist</button>
          <button type="button" data-mode="studio">Studio</button>
          <button type="button" data-mode="muse_spark">Muse</button>
          <button type="button" data-mode="voice">Aria</button>
          <button type="button" data-mode="build">Build</button>
          <button type="button" data-mode="plan">Plan</button>
          <button type="button" data-mode="auro">Auro</button>
        </div>
        <div class="empty-map" aria-label="Open a surface">
          <button type="button" onclick="showAppTab('working')"><b>Working</b></button>
          <button type="button" onclick="showAppTab('habitat')"><b>Habitat</b></button>
          <button type="button" onclick="showAppTab('screen')"><b>Screen</b></button>
          <button type="button" onclick="showAppTab('studio')"><b>Studio</b></button>
          <button type="button" onclick="showAppTab('lab')"><b>Lab</b></button>
          <button type="button" onclick="showAppTab('phone')"><b>Phone</b></button>
          <button type="button" onclick="showAppTab('work')"><b>Work Studio</b></button>
          <button type="button" onclick="showAppTab('remote')"><b>Remote</b></button>
          <button type="button" onclick="showAppTab('browser')"><b>Browser</b></button>
          <button type="button" onclick="showAppTab('platform')"><b>Platform</b></button>
          <button type="button" onclick="showAppTab('voice_studio')"><b>Voice</b></button>
        </div>
        <div class="empty-actions" style="margin-top:14px">
          <button type="button" onclick="runWorkflow('studio_loop')">Studio loop</button>
          <button type="button" onclick="runWorkflow('ship_loop')">Ship loop</button>
          <button type="button" onclick="runWorkflow('voice_loop')">Voice + Fusion</button>
          <button type="button" onclick="runWorkflow('phone_iot')">Phone + IoT</button>
          <button type="button" onclick="showAppTab('lab')">Lab readiness</button>
        </div>
        <div id="deskReadyStrip" style="margin-top:16px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center;max-width:480px;margin-left:auto;margin-right:auto"></div>
        <div id="firstRunTips" style="display:none;margin-top:18px;text-align:left;max-width:460px;margin-left:auto;margin-right:auto;border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--panel)">
          <div style="font-size:12px;font-weight:700;color:var(--fg);margin-bottom:8px">How the main desk flows</div>
          <ol style="margin:0;padding-left:18px;font-size:12.5px;color:var(--muted);line-height:1.55">
            <li><b style="color:var(--fg)">Desk</b> — chat + tools + Working board. Agents sit here.</li>
            <li><b style="color:var(--fg)">Habitat / Screen</b> — agents on the floor; host eyes View/Control.</li>
            <li><b style="color:var(--fg)">Working</b> — life ops board (buy / reserve — you pay).</li>
            <li><b style="color:var(--fg)">Studio / Lab</b> — demos &amp; readiness (own panels under More).</li>
            <li><b style="color:var(--fg)">Phone / Remote / Platform</b> — PWA, Edge, sovereign stack — own tabs.</li>
          </ol>
          <button type="button" class="icon" style="margin-top:10px;border:1px solid var(--line);padding:4px 10px" onclick="dismissFirstRun()">Got it</button>
        </div>
      </div>
    </div>
    <!-- Hybrid habitat: some agents live & work here (GUI floor next to chat) -->
    <aside class="habitat" id="agentHabitat" aria-label="Agent habitat">
      <div class="hb-h">
        <b>Habitat</b>
        <span class="grow"></span>
        <button type="button" class="icon" onclick="document.getElementById('mainStage').classList.toggle('habitat-wide')" title="Widen floor">↔</button>
        <button type="button" class="icon" onclick="refreshHabitat()" title="Refresh">↻</button>
        <button type="button" class="icon" onclick="toggleHabitat(false)" title="Close">✕</button>
      </div>
      <div class="hb-floor" id="habitatFloor">
        <div class="hint" style="padding:8px;color:var(--muted);font-size:12px">Agents take their seats…</div>
      </div>
      <div class="hb-feed" id="habitatFeed" aria-live="polite"></div>
    </aside>
    </div>
    <div class="composer">
      <div class="composer-inner">
      <div class="presets" id="presets"></div>
      <div class="slash-menu" id="slashMenu" role="listbox" aria-label="Actions"></div>
      <div class="mention-menu" id="mentionMenu" role="listbox" aria-label="Mention helpers"></div>
      <div class="box">
        <button class="iconbtn" id="micBtn" type="button" title="Dictation into the box" onclick="toggleMic()" disabled aria-label="Microphone">🎙</button>
        <textarea id="input" placeholder="Describe what you need…" disabled rows="2"></textarea>
        <button class="send" id="sendBtn" disabled onclick="sendMsg()">Send</button>
      </div>
      <div class="composer-bar">
        <div class="agent-pick-wrap" id="agentPickWrap">
          <button type="button" class="agent-pick-btn" id="agentPickBtn" onclick="toggleAgentPicker()" aria-haspopup="listbox" aria-expanded="false" title="Switch agent">
            <span class="ap-dot" id="agentPickDot"></span>
            <span class="ap-name" id="agentPickName">Choose agent</span>
            <span class="ap-chev">▾</span>
          </button>
          <div class="agent-pick-menu" id="agentPickMenu" role="listbox" aria-label="Agents">
            <input class="ap-search" id="agentPickSearch" type="search" placeholder="Search agents…" autocomplete="off" oninput="renderAgentPicker()"/>
            <div class="ap-list" id="agentPickList"></div>
          </div>
        </div>
        <select id="modelPick" class="model-pick" title="Agent" aria-label="Agent (legacy)" tabindex="-1">
          <option value="">Session agent</option>
          <option value="codex">Codex</option>
          <option value="grok">Grok</option>
          <option value="claude">Claude</option>
          <option value="muse_spark">Muse Spark</option>
          <option value="voice">Voice ↔ Voice</option>
          <option value="coding_swarm">Coding Swarm</option>
          <option value="plan">Plan</option>
          <option value="build">Build</option>
          <option value="web">Web</option>
          <option value="wiki">Infinite Wiki</option>
          <option value="custom_agent">Custom agent</option>
          <option value="browser">Browser</option>
          <option value="nexus">NEXUS</option>
          <option value="mesie">MESIE</option>
          <option value="auro">Auro14B</option>
        </select>
        <span class="composer-hint" id="composerHint"><kbd>/</kbd> actions · <kbd>Ctrl</kbd>+<kbd>Enter</kbd> send · 🎙 dictation</span>
      </div>
      <div class="composer-tools" id="composerTools">
        <div style="position:relative">
          <button type="button" class="int-btn" id="intBtn" onclick="toggleIntegrations(event)" aria-haspopup="true" aria-expanded="false" title="Integrations">
            <span class="int-ico">⧉</span>
            <span>Integrations</span>
            <span class="int-count" id="intCount">50</span>
            <span class="chev" style="font-size:9px;opacity:.75">▾</span>
          </button>
          <div class="int-panel" id="intPanel" role="dialog" aria-label="Integrations">
            <div class="int-head">
              <b>Integrations</b>
              <span id="intHeadMeta">Connect tools agents can use</span>
              <span style="flex:1"></span>
              <button type="button" class="icon" onclick="closeIntegrations()" title="Close" style="border:1px solid var(--line);padding:3px 8px;border-radius:7px">✕</button>
            </div>
            <input class="int-search" id="intSearch" type="search" placeholder="Search OpenTable, GitHub, Slack…" autocomplete="off" oninput="renderIntegrations()"/>
            <div class="int-cats" id="intCats"></div>
            <div class="int-list" id="intList"><div class="int-empty">Loading…</div></div>
          </div>
        </div>
        <div class="int-chip-row" id="intQuickChips" aria-label="Featured integrations"></div>
      </div>
      </div>
    </div>
  </section>

  <!-- Claude-style middle column: Screen share + Fusion + VComputer (all agents) -->
  <aside class="screen-col" id="screenCol" aria-label="Screen and virtual computer">
    <div class="sc-h">
      <b>Screen</b>
      <span class="grow"></span>
      <button type="button" class="icon" onclick="document.body.classList.toggle('screen-col-wide')" title="Widen">↔</button>
      <button type="button" class="icon" onclick="toggleScreenCol(false)" title="Close">✕</button>
    </div>
    <div class="sc-modes" role="group" aria-label="Share mode">
      <button type="button" id="scOff" class="on" onclick="setScreenMode('off')">Off</button>
      <button type="button" id="scView" onclick="setScreenMode('view')" title="Agents see fusion screen">View</button>
      <button type="button" id="scCtrl" class="danger" onclick="setScreenMode('control')" title="Agents may use mouse/keyboard">Control</button>
      <button type="button" id="scVcomp" onclick="toggleVcompShare()" title="Virtual computer workspace">VComp</button>
    </div>
    <div class="sc-card" style="margin:8px 10px 0;padding:8px 10px">
      <h4 style="margin:0 0 6px">Watch target</h4>
      <p class="hint" style="font-size:11px;color:var(--muted);margin:0 0 6px;line-height:1.4">Keep POCKET open. Pick <b style="color:var(--fg)">All monitors</b> or another app window so agents see that surface — not only this Edge window.</p>
      <select id="scTarget" onchange="setScreenTarget(this.value)" style="width:100%;font-size:12px;padding:6px 8px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--fg)">
        <option value="desktop">All monitors (desktop)</option>
        <option value="primary">Primary monitor only</option>
      </select>
      <div class="sc-acts" style="margin-top:6px">
        <button type="button" onclick="refreshScreenTargets()">Refresh apps</button>
      </div>
    </div>
    <div class="sc-frame-wrap">
      <span class="sc-badge" id="scBadge">share off</span>
      <img id="scFrame" alt="Shared screen" />
    </div>
    <div class="sc-body">
      <div class="sc-card">
        <h4>Fusion · diffusion <span id="scTargetHint" style="font-weight:500;color:var(--muted);font-size:11px"></span></h4>
        <div class="sc-brief" id="scBrief">Enable View so agents receive live UIA+OCR+visual symbols on every turn. Choose a window above to watch VS Code / browser / etc. while POCKET stays open.</div>
        <div class="sc-syms" id="scSyms"></div>
        <div class="sc-acts">
          <button type="button" onclick="refreshScreenCol(true)">Refresh eyes</button>
          <button type="button" onclick="screenSense()">Sense</button>
          <button type="button" onclick="screenHealDesktop()" title="Reset to all monitors if share is stuck">Heal desktop</button>
          <button type="button" onclick="screenRemake()">Remake</button>
        </div>
      </div>
      <div class="sc-card">
        <h4>VComputer · input</h4>
        <div class="hint" id="scVcompHint" style="font-size:11px;color:var(--muted);margin-bottom:6px">Control mode unlocks click / type for agents on this host.</div>
        <div class="sc-acts">
          <button type="button" onclick="screenAct('sense')">Sense</button>
          <button type="button" onclick="screenAct('open_app',{app:'notepad'})">Notepad</button>
          <button type="button" onclick="screenActClick()">Click name…</button>
          <button type="button" onclick="screenAct('scroll')">Scroll</button>
        </div>
        <pre id="scActOut" style="display:none;margin-top:8px;font-size:10px;max-height:80px;overflow:auto;color:#86efac"></pre>
      </div>
      <div class="sc-card">
        <h4>All agents</h4>
        <div class="hint" style="font-size:11px;color:var(--muted);line-height:1.45">
          When <b style="color:var(--fg)">View</b> or <b style="color:var(--fg)">Control</b> is on, Codex · Grok · Claude · Swarm · Build · Desktop · Vision all receive the same screen context. They work with each other through harness helpers + mesh.
        </div>
      </div>
    </div>
  </aside>

  <aside class="rail" id="contextRail" aria-label="Workspace panel">
    <div class="side-h">
      <span>Workspace</span>
      <span style="display:flex;gap:4px;align-items:center">
        <button class="icon" onclick="refreshAiWorkspace();pollSubagents();connectAll();refreshStack();refreshNodes();refreshVmem()" title="Refresh">↻</button>
        <button class="icon" onclick="toggleWorkspacePanel(false)" title="Close workspace (click Workspace to reopen)" id="railCloseBtn">✕</button>
      </span>
    </div>
    <div class="rail-scroll">
      <div class="ai-sum" id="aiSumCard">
        <h3>Summary</h3>
        <div class="body" id="aiSummary">Updates as you work so you don’t re-explain every turn</div>
        <div class="meta" id="aiSumMeta">Keeps context for this chat</div>
      </div>
      <div class="ai-prev" id="aiPrevCard">
        <h3>Files &amp; previews</h3>
        <div id="aiPreviews"><div class="hint" style="font-size:11px;color:var(--muted)">Docs and outputs show up here</div></div>
        <div class="tree" id="aiTree" style="margin-top:8px"></div>
      </div>
      <div class="ai-bus" id="aiBusCard">
        <h3>Activity</h3>
        <div id="aiBus"><div class="hint" style="font-size:11px;color:var(--muted)">Helper notes appear as work finishes</div></div>
      </div>
      <div class="ai-sum" id="platformCard">
        <h3>Platform · workflows</h3>
        <div class="body" id="platformStatus" style="font-size:11px;line-height:1.45;color:var(--muted)">Sovereign stack · remote browser · IoT · clouds</div>
        <div class="meta" style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="runWorkflow('ship_loop')">Ship</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="runWorkflow('remote_loop')">Remote</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="runWorkflow('voice_loop')">Voice</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="runWorkflow('phone_iot')">Phone·IoT</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="showAppTab('platform')">Map</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="refreshPlatformRail()">↻</button>
        </div>
        <div id="platformRailDetail" style="margin-top:8px;font-size:11px;color:var(--muted);max-height:120px;overflow:auto"></div>
      </div>
      <div class="ai-sum" id="nodeCard">
        <h3>Devices · pair · same Wi‑Fi</h3>
        <div class="body" id="nodeStatus" style="font-size:11px;line-height:1.45;color:var(--muted)">Phone + IoT on this network · shared registry</div>
        <div class="meta" style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="nodeMintPair()">Get pair code</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="showAppTab('phone')">Phone</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="iotDiscoverLan()">Scan Wi‑Fi</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="nodeOfferText()">Send a note</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="refreshNodes();refreshIotRail()">↻</button>
        </div>
        <div id="nodeOffers" style="margin-top:8px;font-size:11px;color:var(--muted)"></div>
        <div id="iotLanUrl" style="margin-top:6px;font-size:11px;color:#6ee7b7;word-break:break-all"></div>
        <div id="iotRailList" style="margin-top:6px;font-size:11px;color:var(--muted)"></div>
      </div>
      <div class="ai-sum" id="vmemCard">
        <h3>Pixel memory · artifacts</h3>
        <div class="body" id="vmemStatus" style="font-size:11px;line-height:1.45;color:var(--muted)">Agentic lattice — store · look · recreate · pass · map</div>
        <div class="meta" style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemStoreNote()">Store</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px;border-color:rgba(16,163,127,.4)" onclick="vmemStoreLastTurn()" title="Store last chat turn in pixel memory">Store last turn</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemLook()">Look</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemSearch()">Search</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemRecreate()">Recreate</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemPass()">Pass</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemArtifacts()">Artifacts</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="vmemBringBack()">Bring back</button>
          <button type="button" class="icon" style="border:1px solid var(--line);padding:2px 8px" onclick="refreshVmem()">Map</button>
        </div>
        <div id="vmemList" style="margin-top:8px;font-size:11px;color:var(--muted);max-height:180px;overflow:auto"></div>
        <pre id="vmemLookOut" style="display:none;margin-top:8px;font-size:11px;white-space:pre-wrap;max-height:200px;overflow:auto;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px;color:var(--fg)"></pre>
        <img id="vmemMap" alt="memory map" style="display:none;width:100%;margin-top:8px;border-radius:8px;border:1px solid var(--line);image-rendering:pixelated"/>
      </div>
      <div class="ai-sum" id="offloadCard">
        <h3>Background queue</h3>
        <div class="body" id="offloadList" style="max-height:100px">Long tasks run here while you keep chatting</div>
        <div class="meta"><button type="button" class="icon" onclick="refreshOffload()" style="border:1px solid var(--line);padding:2px 8px">Refresh</button></div>
      </div>
      <div class="walkthrough" id="walkthrough">
        <div class="wt-h"><span>Progress</span><span id="wtCount" style="font-weight:500;color:var(--muted)">0</span></div>
        <div class="wt-body" id="walkthroughBody">
          <div class="wt-empty">Steps show up as work runs</div>
        </div>
      </div>
      <div class="rail-roster">
        <div class="rr-h">
          <span>Helpers</span>
          <span class="rr-meta">
            <span class="mesh-pill off" id="meshDrive" title="Storage">local</span>
            <span class="sa-count" id="saCount" title="Helpers available">0</span>
          </span>
        </div>
        <div class="rr-body" id="subagentRoster">
          <div class="rr-empty">Helpers activate when a task needs them</div>
        </div>
      </div>
      <div class="card">
        <h3>Status</h3>
        <div class="grid">
          <div><span>Heart</span><strong id="heartLabel">—</strong></div>
          <div><span>Stream</span><strong id="uStream">0</strong></div>
          <div><span>Tokens</span><strong id="uTok">0</strong></div>
          <div><span>POCK</span><strong id="uBal">—</strong></div>
        </div>
        <div class="hint" id="thought" style="margin-top:8px"></div>
      </div>
      <div class="card" id="economyCard">
        <h3 style="display:flex;align-items:center;justify-content:space-between;gap:8px">
          <span>Economy</span>
          <span class="econ-rail paper" id="econRail">paper</span>
        </h3>
        <div class="hint" style="margin:0 0 8px;line-height:1.4">Wallets · digital twins · clearing · Parallax-shaped paper rails</div>
        <div class="econ-row"><span>Operator</span><b id="econOp">—</b></div>
        <div class="econ-row"><span>Twin pool</span><b id="econTwinPool">—</b></div>
        <div class="econ-row"><span>Escrow</span><b id="econEscrow">—</b></div>
        <div class="econ-twins" id="econTwins"></div>
        <div class="btns" style="margin-top:10px">
          <button type="button" onclick="refreshEconomy()">Refresh</button>
          <button type="button" onclick="economyTopup()">+1k POCK</button>
          <button type="button" onclick="economySyncParallax()">Sync Parallax</button>
        </div>
        <div class="hint" id="econHint" style="margin-top:8px;line-height:1.4">Paper-first · AI twin wallets · Parallax @ai-wallet</div>
      </div>
      <div class="card github-card" id="githubCard">
        <h3>GitHub</h3>
        <div class="gh-row"><span>Auth</span><b id="ghAuth">…</b></div>
        <div class="gh-row"><span>User</span><b id="ghUser">—</b></div>
        <div class="hint" id="ghHint" style="margin-top:6px">Signed-in <code>gh</code> on this host</div>
        <div class="btns">
          <button type="button" onclick="refreshGithub()">Refresh</button>
          <button type="button" onclick="pickAgent('github')">Open agent</button>
          <button type="button" onclick="pickAgent('repos')">Repos</button>
        </div>
      </div>
      <div class="card" id="surfaceCard">
        <h3>Work surface</h3>
        <div class="hint" id="surfaceHint" style="margin-bottom:6px">Preview → draft → local/browser → promote to folder or GitHub</div>
        <div class="gh-row"><span>Drafts</span><b id="draftCount">—</b></div>
        <div class="gh-row"><span>Layers</span><b style="font-weight:500;font-size:10.5px">hardware · local · browser · cloud</b></div>
        <div class="btns">
          <button type="button" onclick="refreshWorkSurface()">Refresh</button>
          <button type="button" onclick="newHtmlDraft()">New HTML draft</button>
          <button type="button" onclick="pickAgent('github')">Cloud</button>
        </div>
        <div id="draftList" class="hint" style="margin-top:6px;max-height:100px;overflow:auto"></div>
      </div>
      <div class="card">
        <h3>Vision</h3>
        <img id="liveVision" alt="live" style="width:100%;border-radius:8px;border:1px solid var(--line);margin-top:2px;min-height:72px;background:#0a0a0a;object-fit:contain"/>
        <div class="hint" id="liveVisionMeta" style="margin-top:4px"></div>
        <div class="btns">
          <button type="button" onclick="fullPageRender()">Full page</button>
          <button type="button" onclick="visionObserve()">Understand</button>
          <button type="button" onclick="streamToggle()">Stream</button>
        </div>
        <pre id="visionOut" style="display:none;margin-top:6px;max-height:90px;overflow:auto;font-size:10px;background:#0a0a0a;padding:6px;border-radius:8px;color:var(--muted);white-space:pre-wrap"></pre>
      </div>
      <div class="card">
        <h3>Run</h3>
        <textarea id="orchChat" rows="2" style="width:100%;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px;resize:vertical;font-size:12px;color:var(--text)" placeholder="e.g. screenshot and sense page"></textarea>
        <div class="btns">
          <button type="button" onclick="orchChatSend(false)">Run</button>
          <button type="button" onclick="orchChatSend(true)">Record</button>
        </div>
        <pre id="orchOut" style="display:none;margin-top:6px;max-height:100px;overflow:auto;font-size:10px;background:#0a0a0a;padding:6px;border-radius:8px;color:#86efac;white-space:pre-wrap"></pre>
      </div>
      <div class="card" style="display:none">
        <h3>Activity</h3>
        <div id="liveActions" style="max-height:140px;overflow:auto;font-size:11px;margin-top:2px;font-family:var(--mono);line-height:1.45;color:var(--muted)"></div>
      </div>
      <div class="card">
        <h3>API</h3>
        <div class="hint">Keys for Grok, Codex, Claude, apps</div>
        <div class="btns">
          <button type="button" class="icon" onclick="showAppTab('mcp')" style="border:1px solid var(--line);padding:6px 9px;border-radius:7px">Developers</button>
          <button type="button" onclick="createApiKey()">New key</button>
          <button type="button" onclick="loadAiCatalog()">Catalog</button>
        </div>
        <pre id="aiOut" style="display:none;margin-top:6px;max-height:120px;overflow:auto;font-size:10px;background:#0a0a0a;padding:6px;border-radius:8px;color:var(--muted);white-space:pre-wrap"></pre>
      </div>
      <div class="card" style="display:none">
        <div id="liveList"></div>
        <div id="deployList"></div>
        <pre id="deployLog"></pre>
        <div id="pubUrl"></div>
        <pre id="doctorOut"></pre>
        <button type="button" onclick="pixelText()" id="pixelTextBtn"></button>
        <button type="button" onclick="spawnDynamic()" id="spawnBtn"></button>
        <button type="button" onclick="runCampaign()" id="campBtn"></button>
        <button type="button" onclick="runDoctor()" id="docBtn"></button>
        <button type="button" onclick="deployKind('static')"></button>
        <button type="button" onclick="deployKind('npm')"></button>
        <button type="button" onclick="deployKind('python')"></button>
        <button type="button" onclick="quickDesktop()"></button>
        <button type="button" onclick="quickWeb()"></button>
        <button type="button" onclick="quickNexus()"></button>
      </div>
      <div class="card phone-only">
        <h3>Device</h3>
        <div class="hint" id="deviceDetail">Detecting…</div>
      </div>
    </div>
  </aside>

  <nav class="phone-nav" id="phoneNav" aria-label="Phone navigation">
    <button type="button" id="navAgents" onclick="toggleSide()"><span>☰</span>Agents</button>
    <button type="button" class="on" id="navChat" onclick="closeDrawers();focusChat();showAppTab('desk')"><span>💬</span>Chat</button>
    <button type="button" id="navSys" onclick="showAppTab('workspace')"><span>⚙</span>System</button>
  </nav>
</div>

<!-- In-app product surfaces — each tab is its own first-class panel (no merge) -->
<div class="app-panel-layer" id="appPanelLayer" aria-hidden="true">
  <div class="app-panel-bar">
    <button type="button" class="ap-back" onclick="showAppTab('desk')" title="Back to desk (Esc)">← Desk</button>
    <div class="ap-meta">
      <div class="ap-title-row">
        <span class="ap-title" id="appPanelTitle">POCKET</span>
        <span class="ap-group" id="appPanelGroup"></span>
      </div>
      <span class="ap-path" id="appPanelPath"></span>
    </div>
    <div class="ap-tools">
      <button type="button" class="icon" onclick="appPanelOpenExternal()" title="Open in new tab">↗</button>
      <button type="button" class="icon" onclick="appPanelReload()" title="Reload">↻</button>
      <button type="button" class="icon" onclick="showAppTab('desk')" title="Close">✕</button>
    </div>
  </div>
  <div class="app-panel-actions" id="appPanelActions" aria-label="Tab actions"></div>
  <div class="app-panel-stage" id="appPanelStage">
    <iframe id="appPanelFrame" title="POCKET panel" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-downloads allow-modals"></iframe>
  </div>
</div>

<div class="toast" id="toast"></div>

<div class="gate" id="loginGate" role="dialog" aria-modal="true" aria-labelledby="loginTitle">
  <div class="card">
    <h2 id="loginTitle">Sign in to POCKET</h2>
    <p id="loginBlurb">Use your workspace account. Teammates join with an invite — each person has their own login.</p>
    <div class="tabs">
      <button type="button" class="on" id="tabLogin" onclick="setAuthTab('login')">Sign in</button>
      <button type="button" id="tabReg" onclick="setAuthTab('register')">Join with invite</button>
    </div>
    <div id="loginPane">
      <form id="loginForm" autocomplete="on" onsubmit="event.preventDefault();doLogin();return false;">
      <label for="loginUser">Username</label>
      <input id="loginUser" name="username" value="" placeholder="your username" autocomplete="username"/>
      <label for="loginPass">Password</label>
      <input id="loginPass" name="password" type="password" autocomplete="current-password" placeholder="your password"/>
      <label style="display:flex;gap:8px;align-items:center;margin-top:8px"><input type="checkbox" id="loginRemember" checked/> Stay signed in on this device</label>
      <button class="primary" id="loginBtn" type="submit">Continue</button>
      </form>
      <button class="secondary" id="localUnlockBtn" type="button" style="display:none" title="This computer only">Continue on this computer</button>
    </div>
    <div id="regPane" style="display:none">
      <p style="font-size:12px;color:var(--muted);margin:0 0 10px;line-height:1.45">Create <b style="color:var(--fg)">your own</b> account with the invite your admin sent. You will not use their password.</p>
      <label>Invite code</label>
      <input id="regInvite" placeholder="Paste the invite code"/>
      <label>Choose username</label>
      <input id="regUser" autocomplete="username" placeholder="your name"/>
      <label>Choose password (min 8)</label>
      <input id="regPass" type="password" autocomplete="new-password"/>
      <label>Display name</label>
      <input id="regDisplay" placeholder="optional"/>
      <label style="display:flex;gap:8px;align-items:flex-start;margin-top:10px;font-size:12px;color:var(--muted);font-weight:500">
        <input type="checkbox" id="regTerms" style="margin-top:3px"/>
        <span>I accept the <a href="/v1/legal" target="_blank" rel="noopener">terms</a>. My files stay in my workspace — not mixed with the admin’s.</span>
      </label>
      <button class="primary" id="regBtn" type="button">Create account</button>
    </div>
    <div class="err" id="loginErr"></div>
  </div>
</div>

<script>
const $=id=>document.getElementById(id);
const MODE_COLOR={codex:'#22c55e',claude:'#f59e0b',voice:'#0b84fe',v2v:'#0b84fe',voice_agent:'#0b84fe',voice2voice:'#0b84fe',muse_spark:'#a855f7',muse:'#a855f7',spark:'#a855f7',assist:'#2dd4bf',assistant:'#2dd4bf',digital:'#2dd4bf',auro:'#fbbf24',auro14b:'#fbbf24',work:'#f472b6',working:'#f472b6',live_work:'#f472b6',mcp:'#c4b5fd',coding_swarm:'#c084fc',pixel_swarm:'#c084fc',harness:'#c084fc',swarm_code:'#c084fc',code_swarm:'#c084fc',swarm:'#34d399',shell:'#3b82f6',wsl:'#8b5cf6',wsl_native:'#8b5cf6',linux:'#8b5cf6',ask:'#f59e0b',plan:'#eab308',grok:'#06b6d4',handoff:'#a1a1aa',term:'#34d399',desktop:'#a78bfa',web:'#38bdf8',nexus:'#f472b6',mesie:'#a78bfa',auro:'#fbbf24',auro14b:'#fbbf24',ro14b:'#fbbf24',him:'#fbbf24',agent:'#fb7185',doer:'#fb7185',guppy:'#38bdf8',browser:'#f97316',capture:'#a3e635',vision:'#22d3ee',oculus:'#22d3ee',see:'#22d3ee',screen:'#67e8f9',vcomp:'#a5f3fc',repos:'#94a3b8',github:'#e6edf3',gh:'#e6edf3',copilot:'#818cf8',archon:'#f43f5e',alpha:'#f43f5e',workers:'#e11d48',novae_grok:'#a78bfa',novae_codex:'#34d399',novae:'#a78bfa',offload:'#fbbf24',build:'#f472b6',ship:'#f472b6',use_case:'#fb7185',emergent:'#f472b6',loop:'#f472b6',custom_agent:'#c084fc',genetic:'#34d399',genetic_flow:'#34d399',internal:'#34d399',internal_models:'#34d399',mail:'#2dd4bf',agent_mail:'#2dd4bf'};
/** Specialized Voice ↔ Voice agent only — never applies to Codex/Grok/Plan/etc. */
const VOICE_MODES=new Set(['voice','v2v','voice_agent','voice2voice']);
// Working mode uses voice skills + TTS but is broader than V2V
const WORK_MODES=new Set(['work','working','live_work','work_mode','persistent']);
let _activeSessionMode='';
function isWorkSessionMode(){
  const m=String(_activeSessionMode||'').toLowerCase();
  if(WORK_MODES.has(m)) return true;
  try{
    const s=sessions.find(x=>x.id===activeId);
    if(s && WORK_MODES.has(String(s.mode||'').toLowerCase())) return true;
  }catch(_){}
  return false;
}
let _workBoardTimer=null, _workBoardSig='';
const WORK_CHIPS=[
  {label:'🛒 Buy…', fill:'Buy '},
  {label:'📊 Analyze…', fill:'Analyze '},
  {label:'🍽 Reserve…', fill:'Make a restaurant reservation for '},
  {label:'🔎 Research…', fill:'Research '},
  {label:'👁 Screen', fill:"What's on my screen"},
  {label:'Demo 3-pack', fill:'Buy wireless headphones under $100, analyze my business pipeline today, and reserve a table Friday 7pm'},
];

/* ——— Integrations (Claude-style dropdown under chat) ——— */
let _integrations=[], _intCat='All', _intLoaded=false;
const INTEGRATIONS_FALLBACK=[
  {id:'opentable',name:'OpenTable',category:'Dining',icon:'🍽',blurb:'Find tables · drive reservations',action:'reserve',url:'https://www.opentable.com',prompt:'Make a restaurant reservation via OpenTable: ',featured:true},
  {id:'github',name:'GitHub',category:'Dev',icon:'🐙',blurb:'Repos, PRs, issues',action:'agent',agent:'github',url:'https://github.com',prompt:'GitHub: ',featured:true},
  {id:'working_board',name:'Working board',category:'Host',icon:'✓',blurb:'Buy · analyze · reserve',action:'working',featured:true},
];
async function loadIntegrations(){
  if(_intLoaded && _integrations.length) return _integrations;
  try{
    const j=await api('/v1/integrations');
    _integrations=j.integrations||j.items||[];
    if(_integrations.length){ _intLoaded=true; }
  }catch(_){}
  if(!_integrations.length) _integrations=INTEGRATIONS_FALLBACK.slice();
  const c=$('intCount'); if(c) c.textContent=String(_integrations.length||50);
  renderIntegrationChips();
  return _integrations;
}
function toggleIntegrations(ev){
  if(ev){ try{ ev.stopPropagation(); }catch(_){} }
  const p=$('intPanel'), b=$('intBtn');
  if(!p) return;
  const open=!p.classList.contains('open');
  if(open){
    closeTabMore();
    try{ const m=$('agentPickMenu'); if(m) m.classList.remove('open'); }catch(_){}
    p.classList.add('open');
    if(b){ b.classList.add('open'); b.setAttribute('aria-expanded','true'); }
    loadIntegrations().then(()=>{ renderIntegrations(); try{ $('intSearch').focus(); }catch(_){} });
  }else closeIntegrations();
}
function closeIntegrations(){
  const p=$('intPanel'), b=$('intBtn');
  if(p) p.classList.remove('open');
  if(b){ b.classList.remove('open'); b.setAttribute('aria-expanded','false'); }
}
document.addEventListener('click', function(e){
  const wrap=$('composerTools');
  if(wrap && !wrap.contains(e.target)) closeIntegrations();
});
document.addEventListener('keydown', function(e){
  if(e.key==='Escape' && $('intPanel')&&$('intPanel').classList.contains('open')){
    closeIntegrations(); e.preventDefault();
  }
});
function renderIntegrationChips(){
  const row=$('intQuickChips'); if(!row) return;
  const featured=(_integrations||[]).filter(x=>x.featured).slice(0,6);
  const forceOt=(_integrations||[]).find(x=>x.id==='opentable');
  const list=[];
  if(forceOt) list.push(forceOt);
  featured.forEach(f=>{ if(!list.find(x=>x.id===f.id)) list.push(f); });
  row.innerHTML='';
  list.slice(0,5).forEach(it=>{
    const b=document.createElement('button');
    b.type='button';
    b.className='int-chip'+(it.id==='opentable'?' hot':'');
    b.textContent=(it.icon?it.icon+' ':'')+it.name;
    b.title=it.blurb||it.name;
    b.onclick=()=>useIntegration(it.id);
    row.appendChild(b);
  });
}
function renderIntegrations(){
  const list=$('intList'), cats=$('intCats');
  if(!list) return;
  const q=String(($('intSearch')&&$('intSearch').value)||'').toLowerCase().trim();
  const all=_integrations||[];
  // categories
  const catSet=['All'];
  all.forEach(it=>{ const c=it.category||'Other'; if(!catSet.includes(c)) catSet.push(c); });
  if(cats){
    cats.innerHTML='';
    catSet.forEach(c=>{
      const b=document.createElement('button');
      b.type='button'; b.textContent=c;
      b.className=_intCat===c?'on':'';
      b.onclick=()=>{ _intCat=c; renderIntegrations(); };
      cats.appendChild(b);
    });
  }
  let items=all.slice();
  if(_intCat && _intCat!=='All') items=items.filter(it=>(it.category||'')===_intCat);
  if(q) items=items.filter(it=>
    (it.name||'').toLowerCase().includes(q)||
    (it.blurb||'').toLowerCase().includes(q)||
    (it.category||'').toLowerCase().includes(q)||
    (it.id||'').toLowerCase().includes(q)
  );
  // Featured OpenTable first when browsing Dining / All without search
  if(!q && (_intCat==='All'||_intCat==='Dining')){
    items.sort((a,b)=>{
      if(a.id==='opentable') return -1;
      if(b.id==='opentable') return 1;
      return (b.featured?1:0)-(a.featured?1:0);
    });
  }
  const meta=$('intHeadMeta');
  if(meta) meta.textContent=items.length+' of '+(all.length||50)+(_intCat!=='All'?' · '+_intCat:'');
  if(!items.length){
    list.innerHTML='<div class="int-empty">No integrations match</div>';
    return;
  }
  // group by category
  const groups={};
  items.forEach(it=>{
    const c=it.category||'Other';
    (groups[c]=groups[c]||[]).push(it);
  });
  let html='';
  Object.keys(groups).forEach(g=>{
    html+='<div class="int-group">'+esc(g)+'</div>';
    groups[g].forEach(it=>{
      html+='<button type="button" class="int-item'+(it.featured?' featured':'')+'" data-int="'+esc(it.id)+'">';
      html+='<span class="ii">'+(it.icon||'•')+'</span>';
      html+='<span><b>'+esc(it.name||it.id)+'</b><small>'+esc(it.blurb||'')+'</small></span>';
      html+='<span class="use">'+(it.id==='opentable'?'Reserve':'Use')+'</span>';
      html+='</button>';
    });
  });
  list.innerHTML=html;
  list.querySelectorAll('[data-int]').forEach(btn=>{
    btn.onclick=()=>useIntegration(btn.getAttribute('data-int'));
  });
}
async function useIntegration(id){
  await loadIntegrations();
  const it=(_integrations||[]).find(x=>x.id===id) || INTEGRATIONS_FALLBACK.find(x=>x.id===id);
  if(!it){ toast('Unknown integration','err'); return; }
  closeIntegrations();
  const act=String(it.action||'open').toLowerCase();
  const prompt=it.prompt||'';
  const el=$('input');

  // Server-side execute — Discord desktop, Edge SaaS, board intents (real launch)
  let exec=null;
  try{
    exec=await api('/v1/integrations/execute',{method:'POST',body:JSON.stringify({
      id:id,
      text:prompt||'',
      prefer:it.prefer||'auto',
      open_browser:true,
      open_desktop:true
    })});
  }catch(e){ exec=null; }

  // OpenTable / dining → Working board reservation path
  if(id==='opentable' || act==='reserve'){
    try{ await startWorkingMode(); }catch(_){}
    if(el){
      el.disabled=false;
      el.value=prompt||'Make a restaurant reservation via OpenTable: ';
      el.focus();
      try{ el.setSelectionRange(el.value.length, el.value.length); }catch(_){}
    }
    toast((exec&&exec.message)||'OpenTable · describe place, time, party — e.g. Del Frisco Dallas 8:30 for 2','ok');
    return;
  }
  if(act==='working'){
    try{ await startWorkingMode(); }catch(_){}
    toast((exec&&exec.message)||'Working board live','ok');
    return;
  }
  if(act==='agent' && it.agent){
    try{ await pickAgent(it.agent); }catch(_){}
    if(el && prompt){ el.value=prompt; el.focus(); }
    toast((exec&&exec.message)||((it.name||'Agent')+' ready'));
    return;
  }
  if(act==='tab' && it.tab){
    showAppTab(it.tab);
    toast((exec&&exec.message)||('Tab: '+it.tab));
    return;
  }
  if(act==='screen'){
    showAppTab('screen');
    try{ await setScreenMode('control'); }catch(_){}
    if(el && prompt){ el.value=prompt; el.focus(); }
    toast((exec&&exec.message)||'Screen control');
    return;
  }
  if(act==='remote'){
    showAppTab('remote');
    toast((exec&&exec.message)||(it.name+' in Edge'), exec&&exec.ok===false?'err':'ok');
    return;
  }
  if(act==='buy' || act==='research' || act==='analysis' || act==='notify' || act==='schedule' || act==='errand'){
    try{ await startWorkingMode(); }catch(_){}
    if(el){
      el.disabled=false;
      el.value=prompt||'';
      el.focus();
    }
    toast((exec&&exec.message)||(it.name+' · type details and Send on Working board'));
    return;
  }
  // default open — execute already launched desktop and/or browser
  if(exec && exec.ok){
    try{ toggleScreenCol(true); }catch(_){}
    toast(exec.message||(it.name+' opened'),'ok');
  }else if(it.url){
    // fallback if execute API unavailable
    try{
      await api('/v1/remote-browser/open',{method:'POST',body:JSON.stringify({url:it.url})});
      toggleScreenCol(true);
      toast(it.name+' opened in Edge','ok');
    }catch(_){
      try{ window.open(it.url,'_blank','noopener'); }catch(__){}
    }
  }else if(exec && exec.ok===false){
    toast(exec.message||exec.error||'Could not open '+it.name,'err');
  }
  if(el && prompt){
    el.disabled=false;
    el.value=prompt;
    el.focus();
  }
}
// Prefetch integrations after boot
setTimeout(()=>{ try{ loadIntegrations(); }catch(_){} }, 1200);
async function startWorkingMode(){
  // Working state = operational board (not coding chat)
  try{ toggleScreenCol(true); }catch(_){}
  try{ await setScreenMode('view'); }catch(_){ try{ await setScreenMode('control'); }catch(__){} }
  try{
    await api('/v1/work/start',{method:'POST',body:JSON.stringify({
      voice:true, screen:'view', chrome:true,
      goal:'Working board — real tasks, real tools'
    })});
  }catch(_){}
  await pickAgent('work');
  ensureWorkingBoardPanel(true);
  _workBoardSig=''; // force one paint
  refreshWorkingBoard();
  startWorkBoardPoll();
  const inp=$('input');
  if(inp){
    inp.placeholder='Working: buy X, analyze Y, reserve Z — multi-part OK';
    inp.disabled=false;
  }
  if($('sendBtn')) $('sendBtn').disabled=false;
  if($('micBtn')) $('micBtn').disabled=false;
  toast('Working board live — multi-part asks become rows with tools');
}
function startWorkBoardPoll(){
  if(_workBoardTimer) clearInterval(_workBoardTimer);
  // Faster while live so search choices stream onto the board
  _workBoardTimer=setInterval(()=>{
    if(!isWorkSessionMode() && !($('workBoardPanel')&&$('workBoardPanel').style.display!=='none')){
      clearInterval(_workBoardTimer); _workBoardTimer=null; return;
    }
    try{ refreshWorkingBoard(); }catch(_){}
  }, 2800);
}
function ensureWorkingBoardPanel(show){
  let p=$('workBoardPanel');
  if(!show){
    if(p) p.style.display='none';
    if(_workBoardTimer){ clearInterval(_workBoardTimer); _workBoardTimer=null; }
    return p;
  }
  if(!p){
    p=document.createElement('div');
    p.id='workBoardPanel';
    p.className='work-board-panel';
    p.innerHTML=`
      <div class="wbp-h">
        <b>✓ Working board</b>
        <span class="wbp-sub">Tools run · table is truth · not coding chat</span>
        <span class="grow"></span>
        <button type="button" class="icon" onclick="refreshWorkingBoard()" title="Refresh">↻</button>
        <button type="button" class="icon" onclick="ensureWorkingBoardPanel(false)" title="Hide">✕</button>
      </div>
      <div class="wbp-pills" id="workBoardChips"></div>
      <div class="wbp-stats" id="workBoardStats"></div>
      <div class="wbp-table" id="workBoardTable"><div class="wbp-empty">Loading board…</div></div>
      <div class="wbp-actions">
        <button type="button" class="cta" onclick="workingBoardAsk()">+ Add work</button>
        <button type="button" onclick="workingBoardDirect('board')">Refresh table</button>
        <button type="button" onclick="workingBoardClear()">Clear done</button>
        <button type="button" onclick="workingBoardCmd('package')">Package</button>
      </div>`;
    const host=document.querySelector('.chat-col')||document.querySelector('.main')||document.body;
    const composer=document.querySelector('.composer');
    if(composer&&composer.parentNode) composer.parentNode.insertBefore(p, composer);
    else host.appendChild(p);
    const chips=$('workBoardChips');
    if(chips){
      WORK_CHIPS.forEach(c=>{
        const b=document.createElement('button');
        b.type='button'; b.textContent=c.label;
        b.onclick=()=>{
          const el=$('input');
          if(!el) return;
          el.disabled=false;
          if(c.fill.endsWith('…')||c.label.includes('…')){
            el.value=c.fill;
            el.focus();
            try{ el.setSelectionRange(el.value.length, el.value.length); }catch(_){}
          }else if(c.label==='Demo 3-pack'||c.fill.length>40){
            el.value=c.fill;
            workingBoardSendNow();
          }else{
            el.value=c.fill;
            el.focus();
          }
        };
        chips.appendChild(b);
      });
    }
  }
  p.style.display='block';
  startWorkBoardPoll();
  return p;
}
function _kindIcon(k){
  return ({buy:'🛒',reservation:'🍽',analysis:'📊',research:'🔎',notify:'📬',schedule:'📅',capture:'👁',open:'🌐',errand:'✓'})[k]||'·';
}
async function refreshWorkingBoard(){
  ensureWorkingBoardPanel(true);
  const el=$('workBoardTable');
  const stats=$('workBoardStats');
  if(!el) return;
  try{
    const j=await api('/v1/working/board');
    const items=j.items||(j.board&&j.board.items)||[];
    const c=j.counts||{};
    // Signature includes stream/choices so live findings re-paint
    const sig=(items||[]).map(it=>[it.id,it.status,it.result_summary||'',(it.choices||[]).length,(it.stream||[]).length,it.updated_at||''].join(':')).join('|')
      +'#'+(c.needs_you||0)+':'+(c.done||0)+':'+(c.total||0);
    if(sig===_workBoardSig && el.childNodes.length){
      return;
    }
    _workBoardSig=sig;
    if(stats){
      stats.innerHTML=
        '<span class="wbp-stat need">'+(c.needs_you||0)+' need you</span>'+
        '<span class="wbp-stat ok">'+(c.done||0)+' done</span>'+
        '<span class="wbp-stat run">'+(c.running||c.queued||0)+' active</span>'+
        '<span class="wbp-stat">'+(c.total||items.length)+' total</span>';
    }
    if(!items.length){
      el.innerHTML='<div class="wbp-empty">Board empty.<br><strong style="color:var(--fg)">Type a real multi-part ask</strong> or tap a chip above.<br><span style="opacity:.8">Example: buy X, analyze Y, reserve Z</span></div>';
      return;
    }
    // newest first
    const list=items.slice().reverse().slice(0,30);
    let html='';
    list.forEach((it)=>{
      const st=String(it.status||'queued');
      const id=esc(it.id||'');
      const open=(st==='needs_you'||st==='running'||(it.choices&&it.choices.length))?' open':'';
      html+='<div class="wbp-card'+open+'" data-id="'+id+'">';
      html+='<div class="kind">'+_kindIcon(it.kind)+'</div>';
      html+='<div><div class="title">'+esc((it.title||'').slice(0,90))+'</div>';
      html+='<div class="meta">'+esc((it.result_summary||it.gate_message||it.kind||'—').slice(0,120))+'</div></div>';
      html+='<div class="st '+esc(st)+'">'+esc(st.replace('_',' '))+'</div>';
      html+='<div class="row-actions">';
      if(st==='needs_you'||st==='blocked'){
        html+='<button type="button" class="primary" data-act="done" data-id="'+id+'">Mark done</button>';
        html+='<button type="button" data-act="dismissed" data-id="'+id+'">Dismiss</button>';
      }else if(st==='done'){
        html+='<button type="button" data-act="dismissed" data-id="'+id+'">Remove</button>';
      }else if(st==='running'||st==='queued'){
        html+='<span class="meta" style="padding:2px 0">live…</span>';
      }else{
        html+='<button type="button" class="primary" data-act="done" data-id="'+id+'">Done</button>';
      }
      html+='<button type="button" data-act="toggle" data-id="'+id+'">Details</button>';
      html+='</div>';
      let det='';
      if(it.gate_message) det+='<div style="margin-bottom:6px;color:#fbbf24">'+esc(it.gate_message)+'</div>';
      // Live stream trail
      if(it.stream&&it.stream.length){
        det+='<div class="wbp-stream" style="margin-bottom:8px;font-size:11px;color:#a1a1aa;line-height:1.45">';
        (it.stream||[]).slice(-6).forEach(s=>{
          const t=typeof s==='string'?s:(s&&s.text)||'';
          if(t) det+='<div>· '+esc(String(t).slice(0,160))+'</div>';
        });
        det+='</div>';
      }
      // Numbered choices (restaurants, products, etc.)
      const ch=it.choices||[];
      if(ch.length){
        det+='<div class="wbp-choices" style="margin-bottom:8px">';
        ch.slice(0,8).forEach((l,i)=>{
          det+='<div style="margin:4px 0;padding:6px 8px;border-radius:8px;background:rgba(0,0,0,.22);border:1px solid var(--line)">';
          det+='<b style="color:var(--fg)">'+(i+1)+'. '+esc((l.title||'option').slice(0,90))+'</b>';
          if(l.snippet) det+='<div style="color:var(--muted);font-size:11px;margin-top:2px">'+esc(String(l.snippet).slice(0,120))+'</div>';
          if(l.url) det+='<div><a href="'+esc(l.url)+'" target="_blank" rel="noopener" style="color:#f9a8d4;font-size:11.5px">'+esc(l.url.slice(0,70))+(l.url.length>70?'…':'')+'</a></div>';
          det+='</div>';
        });
        det+='</div>';
      }else if(it.links&&it.links.length){
        det+='<div>'+(it.links||[]).slice(0,6).map(l=>
          '<a href="'+esc(l.url||'#')+'" target="_blank" rel="noopener" style="color:#f9a8d4;margin-right:10px;display:inline-block;margin-bottom:4px">'+esc(l.title||'link')+'</a>'
        ).join('')+'</div>';
      }
      if(it.evidence&&it.evidence.length){
        det+='<div style="white-space:pre-wrap;margin-bottom:6px;font-size:11px;color:#a1a1aa">'+esc((it.evidence||[]).join('\n\n').slice(0,500))+'</div>';
      }
      if(it.next_steps&&it.next_steps.length){
        det+='<div style="margin-top:6px;color:#a1a1aa">Next: '+esc((it.next_steps||[]).join(' → '))+'</div>';
      }
      if(!det) det='<span style="color:var(--muted)">No extra detail</span>';
      html+='<div class="detail">'+det+'</div>';
      html+='</div>';
    });
    el.innerHTML=html;
    el.querySelectorAll('[data-act]').forEach(btn=>{
      btn.onclick=(ev)=>{
        ev.stopPropagation();
        const act=btn.getAttribute('data-act');
        const iid=btn.getAttribute('data-id');
        if(act==='toggle'){
          const card=btn.closest('.wbp-card');
          if(card) card.classList.toggle('open');
          return;
        }
        workingBoardSetStatus(iid, act);
      };
    });
  }catch(e){
    el.innerHTML='<div class="wbp-empty">Board offline — '+esc(e.message||e)+'</div>';
  }
}
async function workingBoardSetStatus(id, status){
  if(!id||!status) return;
  try{
    await api('/v1/working/board',{method:'POST',body:JSON.stringify({item_id:id,status:status})});
    refreshWorkingBoard();
    toast(status==='done'?'Marked done':(status==='dismissed'?'Removed':'Updated'),'ok');
  }catch(e){ toast(e.message||'update failed','err'); }
}
async function workingBoardDirect(text){
  try{
    const j=await api('/v1/working/board',{method:'POST',body:JSON.stringify({
      text:text, session_id:activeId||'', execute:true
    })});
    refreshWorkingBoard();
    if(j.reply){
      // Surface result in transcript if possible
      try{
        const box=$('transcript');
        if(box && !box.querySelector('.empty')){
          /* board panel is source of truth */
        }
      }catch(_){}
    }
    toast(j.ran?('Tools ran on '+(j.ran)+' item(s)'):'Board updated','ok');
  }catch(e){ toast(e.message||'board failed','err'); }
}
async function workingBoardSendNow(){
  const el=$('input');
  if(!el||!el.value.trim()) return;
  el.disabled=false;
  if($('sendBtn')) $('sendBtn').disabled=false;
  // Prefer direct board API for speed + reliability
  const t=el.value.trim();
  el.value='';
  await workingBoardDirect(t);
  // Also post into work session so history stays coherent
  try{
    if(isWorkSessionMode()&&activeId){
      el.value=t;
      await sendMsg();
      el.value='';
    }
  }catch(_){}
  setTimeout(refreshWorkingBoard, 400);
}
async function workingBoardAsk(){
  const t=prompt('What do you need done? (multi-part OK)\n\nExample:\nBuy wireless headphones under $100, analyze my pipeline, reserve Friday 7pm','');
  if(!t||!t.trim()) return;
  const el=$('input');
  if(el){ el.value=t.trim(); el.disabled=false; }
  await workingBoardSendNow();
}
async function workingBoardClear(){
  try{
    // dismiss all done items client-side via API clear of done only: re-fetch and dismiss
    const j=await api('/v1/working/board');
    const items=j.items||[];
    for(const it of items){
      if(it.status==='done'||it.status==='dismissed'){
        try{ await api('/v1/working/board',{method:'POST',body:JSON.stringify({item_id:it.id,status:'dismissed'})}); }catch(_){}
      }
    }
    refreshWorkingBoard();
    toast('Cleared finished items','ok');
  }catch(e){ toast(e.message||'clear failed','err'); }
}
async function workingBoardCmd(cmd){
  if(cmd==='board'){ refreshWorkingBoard(); return; }
  const el=$('input');
  if(el){ el.value=cmd; el.disabled=false; }
  $('sendBtn')&&($('sendBtn').disabled=false);
  try{ await sendMsg(); }catch(_){}
  setTimeout(refreshWorkingBoard, 600);
}
function isVoiceSessionMode(){
  // Native Aria modes OR any chat agent with voice_engine activated
  const m=String(_activeSessionMode||'').toLowerCase();
  if(VOICE_MODES.has(m)) return true;
  try{
    const s=(sessions||[]).find(x=>x&&x.id===activeId)
      || (window.__activeSessCache&&window.__activeSessCache.id===activeId?window.__activeSessCache:null);
    if(!s) return false;
    if(VOICE_MODES.has(String(s.mode||'').toLowerCase())) return true;
    if(s.voice_engine) return true;
  }catch(_){}
  return false;
}
function activeSessionVoiceEngine(){
  if(VOICE_MODES.has(String(_activeSessionMode||'').toLowerCase())) return true;
  try{
    const s=(sessions||[]).find(x=>x&&x.id===activeId)
      || (window.__activeSessCache&&window.__activeSessCache.id===activeId?window.__activeSessCache:null);
    return !!(s&&s.voice_engine);
  }catch(_){ return false; }
}
async function quickMuseOpen(){
  try{
    if(!activeId || !['muse_spark','muse','spark','muse-spark','musespark'].includes(String(_activeSessionMode||'').toLowerCase())){
      await pickAgent('muse_spark');
    }
    const el=$('input');
    if(el){ el.disabled=false; el.value='open meta'; }
    if($('sendBtn')) $('sendBtn').disabled=false;
    await sendMsg();
  }catch(e){ toast(e.message||'open meta failed','err'); }
}
async function toggleVoiceEngine(){
  if(!activeId){
    toast('Open a chat agent first, then activate voice engine');
    return;
  }
  const on=activeSessionVoiceEngine();
  // Native voice agent: always on
  if(VOICE_MODES.has(String(_activeSessionMode||'').toLowerCase())){
    toast('This is already a voice agent (Aria)');
    paintVoiceEngineBtn(true);
    try{ if(!micOn) await toggleMic(); }catch(_){}
    return;
  }
  try{
    const j=await api('/v1/sessions/'+activeId+'/voice-engine',{
      method:'POST',
      body:JSON.stringify({enabled:!on})
    });
    const ve=!!(j.voice_engine||(j.session&&j.session.voice_engine));
    // Update local session cache
    try{
      const ix=(sessions||[]).findIndex(x=>x&&x.id===activeId);
      if(ix>=0){
        sessions[ix].voice_engine=ve;
        if(j.session&&j.session.title) sessions[ix].title=j.session.title;
      }
      if(window.__activeSessCache&&window.__activeSessCache.id===activeId){
        window.__activeSessCache.voice_engine=ve;
        if(j.session&&j.session.title) window.__activeSessCache.title=j.session.title;
      }
    }catch(_){}
    paintVoiceEngineBtn(ve);
    updateMicChrome(_activeSessionMode);
    if($('mainTitle')&&j.session&&j.session.title) $('mainTitle').textContent=j.session.title;
    if(ve){
      toast((agentMeta(_activeSessionMode).name||'Agent')+' · voice engine ON — talk; it speaks back','ok');
      try{ await probeVoiceApi(); }catch(_){}
      // Arm mic for talk if not already
      try{ if(!micOn) await toggleMic(); }catch(_){}
    }else{
      toast('Voice engine OFF — mic is dictation only');
      try{ if(window.speechSynthesis) window.speechSynthesis.cancel(); }catch(_){}
      if(micOn){ try{ await toggleMic(); }catch(_){} }
    }
    try{ refreshSessions(); }catch(_){}
  }catch(e){ toast(e.message||'voice engine failed','err'); }
}
function paintVoiceEngineBtn(on){
  const b=$('btnVoiceEngine');
  if(!b) return;
  const native=VOICE_MODES.has(String(_activeSessionMode||'').toLowerCase());
  const active=!!on || native;
  b.classList.toggle('voice-on', active);
  b.textContent=active?(native?'🎙 Voice agent':'🎙 Voice on'):'🎙 Voice engine';
  b.title=active
    ? (native?'Native voice agent — mic + speak-back':'Voice engine active — click to turn off')
    : 'Activate voice engine — this chat agent talks and listens';
}
const LATIN_WORKERS=['ARCHON','HYDRA','SCRUTATOR','SCRIPTOR','PORTARIUS','OCULUS','SPECULUM','REPOSITOR','CONSILIARIUS','TABELLARIUS','NAVIGATOR','GUPPY'];
const MESH_AGENTS=['DESIGN','AESTHETE','LAYOUT','MOTION','FORGE_HEADLESS','SENTINEL_HEADLESS','RESEARCH_HEADLESS','SHIP_HEADLESS','GROK_NOVAE','CODEX_NOVAE'];
const MESH_AGENT_ROLES={
  DESIGN:'UI + product craft',
  AESTHETE:'Visual taste',
  LAYOUT:'Structure + spacing',
  MOTION:'Motion + feedback',
  FORGE_HEADLESS:'Build / test / package',
  SENTINEL_HEADLESS:'Security + audit',
  RESEARCH_HEADLESS:'Research packs',
  SHIP_HEADLESS:'Release / beta ship',
  FORGE:'→ FORGE_HEADLESS',
  SENTINEL:'→ SENTINEL_HEADLESS',
  RESEARCH:'→ RESEARCH_HEADLESS',
  SHIP:'→ SHIP_HEADLESS',
  DESIGNER:'→ DESIGN',
  UI:'→ DESIGN',
  UX:'→ AESTHETE',
  CSS:'→ LAYOUT',
  ANIM:'→ MOTION'
};
const MENTION_ALIASES=['DESIGN','DESIGNER','UI','UX','AESTHETE','LAYOUT','MOTION','CSS','ANIM','FORGE','FORGE_HEADLESS','SENTINEL','SENTINEL_HEADLESS','RESEARCH','RESEARCH_HEADLESS','SHIP','SHIP_HEADLESS'];
let sessions=[], activeId=null, pollTimer=null, status=null, micRec=null, micOn=false, authTab='login';
window.__pocketBootAt=Date.now();
let liveSeq=0, liveTimer=null, subagentTimer=null;
let subagentState=[], subagentCatalog=[], liveAgentHits={}, walkthroughSteps=[];
let meshInfo={agent_count:0, mesh_root:'', drive:''};
let DEVICE={kind:'computer',label:'Computer',remote:false};
let ME={user:'',role:'member',display:''};
const SLASH_ACTIONS=[
  {cmd:'help', label:'Show actions', fill:'/help'},
  {cmd:'workers', label:'List Latin workers', fill:'workers'},
  {cmd:'screenshot', label:'Capture screen (OCULUS)', fill:'@OCULUS screenshot'},
  {cmd:'status', label:'Agent status', fill:'status'},
  {cmd:'demo', label:'Run focused demo', fill:'@ARCHON focused demo'},
  {cmd:'sense', label:'Sense page (vision)', fill:'@OCULUS sense page'},
  {cmd:'design', label:'Dispatch DESIGN', fill:'@DESIGN '},
  {cmd:'forge', label:'Ask the build helper', fill:'@FORGE_HEADLESS '},
  {cmd:'ship', label:'Ask the ship helper', fill:'@SHIP_HEADLESS '},
];
function mentionRoster(){
  const names=new Set([...LATIN_WORKERS, ...MESH_AGENTS, ...MENTION_ALIASES]);
  (subagentCatalog||[]).forEach(w=>{
    const n=String(w.name||w.id||'').toUpperCase();
    if(n && n.length>=2) names.add(n);
  });
  return Array.from(names).sort();
}
function mentionKind(name){
  const n=String(name||'').toUpperCase();
  if(['DESIGN','DESIGNER','UI','UX','AESTHETE','LAYOUT','MOTION','CSS','ANIM'].includes(n)) return 'design';
  if(n.includes('HEADLESS')||['FORGE','SENTINEL','RESEARCH','SHIP'].includes(n)) return 'headless';
  if(LATIN_WORKERS.includes(n)) return 'latin';
  return 'mesh';
}
function mentionLabel(name){
  const n=String(name||'').toUpperCase();
  return MESH_AGENT_ROLES[n]||(LATIN_WORKERS.includes(n)?'Latin worker':'Mesh agent');
}

function toggleMoreAgents(){
  const el=$('moreAgents'); if(!el) return;
  const open=el.classList.toggle('open');
  const btn=$('moreAgentsBtn');
  if(btn) btn.textContent=open?'More agents ▴':'More agents ▾';
  if(open){
    // ensure the expanded list is visible inside the side scroll
    try{ el.scrollIntoView({block:'nearest',behavior:'smooth'}); }catch(_){}
  }
}
let AGENT_CATALOG=[
  {group:'Primary', items:[
    {id:'codex', name:'Codex', blurb:'Write and fix code · harnessed subagents', color:'#22c55e', first_class:true, harness:true},
    {id:'grok', name:'Grok', blurb:'Code, research · harnessed subagents', color:'#06b6d4', first_class:true, harness:true},
    {id:'claude', name:'Claude', blurb:'Agent SDK loop · tools · harnessed', color:'#f59e0b', first_class:true, harness:true},
    {id:'muse_spark', name:'Muse Spark', blurb:'Meta multimodal · parallel lanes · voice engine OK', color:'#a855f7', first_class:true, harness:true},
    {id:'assist', name:'Digital assistant', blurb:'Real-life help · routes engines · Work Studio', color:'#2dd4bf', first_class:true, harness:true},
    {id:'auro', name:'Auro14B', blurb:'Local LMR + meaning model', color:'#fbbf24', first_class:true},
    {id:'voice', name:'Voice ↔ Voice', blurb:'Specialized agent — talk and hear back', color:'#0b84fe', first_class:true},
    {id:'work', name:'Working mode', blurb:'Live voice + screen Control + CLI/MCP + package→artifacts', color:'#f472b6', first_class:true, harness:true},
    {id:'plan', name:'Plan', blurb:'Outline only — harnessed helpers', color:'#eab308', first_class:true, harness:true},
    {id:'genetic', name:'Genetic', blurb:'Internal models as modules · evolve which run', color:'#34d399', first_class:true, harness:true},
  ]},
  {group:'Build', items:[
    {id:'coding_swarm', name:'Coding Swarm', blurb:'Sophia · Solver · Twin → pixel artifacts', color:'#c084fc', first_class:true},
    {id:'build', name:'Build', blurb:'Plan → code → test → ship', color:'#f472b6', first_class:true, harness:true},
    {id:'wiki', name:'Infinite Wiki', blurb:'Navigate code without dumping files', color:'#a78bfa', first_class:true, harness:true},
    {id:'dual', name:'Dual loop', blurb:'Chat while background work runs', color:'#818cf8', first_class:true},
    {id:'use_case', name:'Use cases', blurb:'Ready playbooks', color:'#fb7185', first_class:true, harness:true},
    {id:'custom_agent', name:'Custom agent', blurb:'Your tools and rules', color:'#c084fc', first_class:true, harness:true},
  ]},
  {group:'Host', items:[
    {id:'web', name:'Web', blurb:'Search and fetch', color:'#38bdf8', first_class:true},
    {id:'git', name:'Git', blurb:'Vault repos and export', color:'#94a3b8', first_class:true},
    {id:'desktop', name:'Desktop', blurb:'Open apps on this PC', color:'#a78bfa', first_class:true},
    {id:'browser', name:'Browser agent', blurb:'Edge, X, Copilot', color:'#f97316', first_class:true},
    {id:'capture', name:'Capture', blurb:'Screenshots', color:'#a3e635', first_class:true},
    {id:'vision', name:'Vision', blurb:'OCULUS · observe · UI map · OCR · click', color:'#22d3ee', first_class:true},
    {id:'github', name:'GitHub', blurb:'repos · issues · PRs · clone · create', color:'#e6edf3', first_class:true},
    {id:'cowork', name:'Cowork', blurb:'Desk demo + record', color:'#f472b6', first_class:true},
    {id:'offload', name:'Offload', blurb:'Background ticket queue', color:'#fbbf24', first_class:true},
  ]},
  {group:'Advanced', items:[
    {id:'swarm', name:'Swarm', blurb:'Coding swarm or always-on pulses', color:'#34d399', first_class:true},
    {id:'nexus', name:'NEXUS', blurb:'Intelligence tools', color:'#f472b6', first_class:true},
    {id:'mesie', name:'MESIE', blurb:'Spectral / compute', color:'#a78bfa', first_class:true},
    {id:'auro', name:'Auro14B', blurb:'Local model', color:'#fbbf24', first_class:true},
    {id:'wsl_native', name:'WSL', blurb:'Integrated Linux console (Debian)', color:'#8b5cf6', first_class:true},
    {id:'python', name:'Python', blurb:'Host Python CLI for agents', color:'#fbbf24', first_class:true},
    {id:'python_wsl', name:'Py·WSL', blurb:'python3 in WSL for agents', color:'#a78bfa', first_class:true},
    {id:'archon', name:'ARCHON', blurb:'Orchestrator · harnessed', color:'#f43f5e', first_class:true, harness:true},
    {id:'guppy', name:'Guppy', blurb:'Local helper', color:'#38bdf8', first_class:true},
    {id:'mcp', name:'MCP tools', blurb:'3 internal + 7 external · agent CLIs', color:'#c4b5fd', first_class:true},
    {id:'repos', name:'Repos', blurb:'GitHub links', color:'#94a3b8', first_class:true},
    {id:'term', name:'Term', blurb:'Host shell (admin)', color:'#34d399', first_class:true},
    {id:'shell', name:'Shell', blurb:'Host PowerShell (admin)', color:'#34d399', first_class:true},
    {id:'ship', name:'Ship', blurb:'Release ship loop', color:'#f472b6', first_class:true, harness:true},
    {id:'emergent', name:'Emergent', blurb:'Ship factory', color:'#f472b6', first_class:true, harness:true},
    {id:'agent', name:'Doer', blurb:'Headless multi-step', color:'#fb7185', first_class:true, harness:true},
    {id:'novae_grok', name:'Grok Novae', blurb:'Novae hands', color:'#a78bfa', first_class:true},
    {id:'novae_codex', name:'Codex Novae', blurb:'Novae hands', color:'#34d399', first_class:true},
    {id:'dream', name:'Dream', blurb:'Idle consolidator', color:'#a78bfa', first_class:true},
    {id:'proof', name:'Proof', blurb:'Work receipts', color:'#86efac', first_class:true},
    {id:'copilot', name:'Copilot', blurb:'Windows Copilot', color:'#818cf8', first_class:true},
  ]},
];
/** Merge server first-class catalog so every agent is discoverable. */
async function loadFirstClassCatalog(){
  try{
    const j=await api('/v1/agents/catalog');
    if(!j||!j.ok||!Array.isArray(j.groups)) return;
    // Keep Primary order; replace/extend from server
    const prefer=j.groups.filter(g=>['Primary','Build','Host','Advanced'].includes(g.group));
    if(prefer.length){
      AGENT_CATALOG=prefer.map(g=>({
        group:g.group,
        items:(g.items||[]).map(it=>({
          id:it.id, name:it.name, blurb:it.blurb||'', color:it.color||'#94a3b8',
          first_class:true, harness:!!it.harness
        }))
      }));
    }
    // Side "More agents" — append any Advanced extras not in side buttons
    try{ rebuildMoreAgentsFromCatalog(); }catch(_){}
    // model pick options
    try{ rebuildModelPickFromCatalog(); }catch(_){}
  }catch(_){}
}
function rebuildMoreAgentsFromCatalog(){
  const more=$('moreAgents'); if(!more) return;
  const existing=new Set(Array.from(more.querySelectorAll('[onclick]')).map(b=>{
    const m=String(b.getAttribute('onclick')||'').match(/pickAgent\('([^']+)'\)/);
    return m?m[1]:'';
  }).filter(Boolean));
  // also scan main actions
  document.querySelectorAll('.actions button[onclick]').forEach(b=>{
    const m=String(b.getAttribute('onclick')||'').match(/pickAgent\('([^']+)'\)/);
    if(m) existing.add(m[1]);
  });
  const adv=(AGENT_CATALOG.find(g=>g.group==='Advanced')||{}).items||[];
  const host=(AGENT_CATALOG.find(g=>g.group==='Host')||{}).items||[];
  const build=(AGENT_CATALOG.find(g=>g.group==='Build')||{}).items||[];
  [...build, ...host, ...adv].forEach(it=>{
    if(!it.id||existing.has(it.id)) return;
    existing.add(it.id);
    const b=document.createElement('button');
    b.type='button';
    b.setAttribute('onclick', `pickAgent('${it.id}')`);
    b.innerHTML=`<b>${esc(it.name)}</b><small>${esc(it.blurb||'first-class')}</small>`;
    more.appendChild(b);
  });
}
function rebuildModelPickFromCatalog(){
  const mp=$('modelPick'); if(!mp) return;
  const have=new Set(Array.from(mp.options).map(o=>o.value));
  AGENT_CATALOG.forEach(g=>{
    (g.items||[]).forEach(it=>{
      if(!it.id||have.has(it.id)) return;
      have.add(it.id);
      const o=document.createElement('option');
      o.value=it.id; o.textContent=it.name;
      mp.appendChild(o);
    });
  });
}
function agentMeta(id){
  for(const g of AGENT_CATALOG){
    const hit=g.items.find(x=>x.id===id);
    if(hit) return hit;
  }
  return {id, name:id, blurb:'first-class agent', color:MODE_COLOR[id]||'#94a3b8', first_class:true};
}
function setAgentPickUI(mode){
  const m=agentMeta(mode||'');
  const name=$('agentPickName'), dot=$('agentPickDot');
  if(name) name.textContent=m.name||'Choose agent';
  if(dot) dot.style.background=m.color||'#10a37f';
  const mp=$('modelPick');
  if(mp && mode){ try{ mp.value=mode; }catch(_){ } }
  updateMicChrome(mode);
}
/** Mic: dictation by default; voice engine (or Aria) = auto-send + speak-back. */
function updateMicChrome(mode){
  const b=$('micBtn'); if(!b) return;
  const voice=isVoiceSessionMode() || VOICE_MODES.has(String(mode||_activeSessionMode||'').toLowerCase());
  b.title=voice
    ? 'Voice engine — patient listen; auto-send + this agent speaks back'
    : 'Dictation only — adds text to the prompt box (never auto-sends). Activate Voice engine to talk.';
  b.setAttribute('aria-label', voice?'Voice engine mic':'Dictation into prompt box');
  b.classList.toggle('mic-patient', !!voice && micOn);
  const hint=$('composerHint')||document.querySelector('.composer-hint');
  if(hint){
    hint.innerHTML=voice
      ? '<kbd>/</kbd> actions · <kbd>Ctrl</kbd>+<kbd>Enter</kbd> send · 🎙 voice engine (talk + hear)'
      : '<kbd>/</kbd> actions · <kbd>Ctrl</kbd>+<kbd>Enter</kbd> send · 🎙 dictation · Voice engine in header';
  }
  paintVoiceEngineBtn(activeSessionVoiceEngine());
}
function toggleAgentPicker(){
  const menu=$('agentPickMenu'), btn=$('agentPickBtn');
  if(!menu) return;
  const open=!menu.classList.contains('open');
  menu.classList.toggle('open', open);
  if(btn) btn.setAttribute('aria-expanded', open?'true':'false');
  if(open){
    _apKbIndex=-1;
    renderAgentPicker();
    const s=$('agentPickSearch');
    if(s){ s.value=''; setTimeout(()=>s.focus(), 30); }
  }
}
function closeAgentPicker(){
  const menu=$('agentPickMenu'), btn=$('agentPickBtn');
  if(menu) menu.classList.remove('open');
  if(btn) btn.setAttribute('aria-expanded','false');
  _apKbIndex=-1;
}
let _apKbIndex=-1;
function apPickerItems(){
  return Array.from(document.querySelectorAll('#agentPickList .ap-item'));
}
function apKbHighlight(i){
  const items=apPickerItems();
  if(!items.length){ _apKbIndex=-1; return; }
  _apKbIndex=Math.max(0, Math.min(items.length-1, i));
  items.forEach((el,idx)=>{
    el.classList.toggle('kb', idx===_apKbIndex);
    if(idx===_apKbIndex){ try{ el.scrollIntoView({block:'nearest'}); }catch(_){ } }
  });
}
function apKbMove(delta){
  const items=apPickerItems();
  if(!items.length) return;
  if(_apKbIndex<0) apKbHighlight(delta>0?0:items.length-1);
  else apKbHighlight(_apKbIndex+delta);
}
function apKbActivate(){
  const items=apPickerItems();
  if(_apKbIndex>=0 && items[_apKbIndex]){
    const id=items[_apKbIndex].getAttribute('data-mode');
    if(id){ closeAgentPicker(); pickAgent(id); }
  }
}
function renderAgentPicker(){
  const list=$('agentPickList'); if(!list) return;
  const q=(($('agentPickSearch')&&$('agentPickSearch').value)||'').trim().toLowerCase();
  const activeMode=(sessions.find(s=>s.id===activeId)||{}).mode||'';
  list.innerHTML='';
  AGENT_CATALOG.forEach(g=>{
    const items=g.items.filter(it=>{
      if(!q) return true;
      return (it.name+' '+it.blurb+' '+it.id).toLowerCase().includes(q);
    });
    if(!items.length) return;
    const gh=document.createElement('div'); gh.className='ap-group'; gh.textContent=g.group; list.appendChild(gh);
    items.forEach(it=>{
      const live=(sessions||[]).find(s=>s.mode===it.id);
      const b=document.createElement('button');
      b.type='button';
      b.className='ap-item'+(activeMode===it.id?' on':'');
      b.setAttribute('data-mode', it.id);
      b.setAttribute('role','option');
      b.innerHTML=`<span class="ap-dot" style="background:${it.color};margin-top:5px"></span>
        <span style="min-width:0;flex:1"><b>${esc(it.name)}</b><small>${esc(it.blurb)}</small></span>
        ${live?'<span class="ap-live">open</span>':''}`;
      b.onclick=()=>{ closeAgentPicker(); pickAgent(it.id); };
      list.appendChild(b);
    });
  });
  if(!list.children.length){
    list.innerHTML='<div style="padding:14px;color:var(--muted);font-size:12px">No agents match</div>';
  }
  // keep keyboard selection if still valid
  if(_apKbIndex>=0) apKbHighlight(_apKbIndex);
}
/** Prefer resume existing session of this agent; else start new. */
async function pickAgent(mode){
  if(!mode) return;
  try{
    hideGate();
    // Clear any stuck full-screen blockers so clicks always land
    try{
      const g=$('loginGate'); if(g){ g.classList.remove('open'); g.style.display='none'; g.style.pointerEvents='none'; }
      const sp=$('bootSplash'); if(sp){ sp.classList.add('done'); sp.style.pointerEvents='none'; }
    }catch(_){}
    setAgentPickUI(mode);
    const existing=(sessions||[]).filter(s=>s.mode===mode);
    if(existing.length){
      const s=existing[0];
      await selectSess(s.id);
      toast(agentMeta(mode).name+' · resumed');
      if(sideIsDrawer()) closeDrawers();
      return;
    }
    await newSess(mode);
    if(sideIsDrawer()) closeDrawers();
  }catch(e){
    toast('Could not open '+(mode||'agent')+': '+(e.message||e),'err');
  }
}
function toast(msg, kind){
  const t=$('toast'); if(!t) return;
  t.textContent=String(msg||'');
  t.classList.remove('ok','err');
  if(kind==='ok'||kind==='err') t.classList.add(kind);
  t.classList.add('show');
  clearTimeout(toast._t);
  toast._t=setTimeout(()=>{ t.classList.remove('show','ok','err'); }, 3200);
}

/** Detect phone vs computer (and tablet). UA + viewport + touch + pointer. */
function detectDevice(){
  const ua=navigator.userAgent||'';
  const w=Math.min(window.innerWidth||0, screen.width||0)||window.innerWidth||0;
  const h=window.innerHeight||0;
  const touch=('ontouchstart' in window)||(navigator.maxTouchPoints>0);
  let coarse=false;
  try{ coarse=!!window.matchMedia && window.matchMedia('(pointer: coarse)').matches; }catch(_){}
  let standalone=false;
  try{ standalone=!!(window.navigator.standalone||window.matchMedia('(display-mode: standalone)').matches); }catch(_){}
  const platform=navigator.platform||navigator.userAgentData&&navigator.userAgentData.platform||'';
  const uaPhone=/Mobile|Android.*Mobile|iPhone|iPod|webOS|BlackBerry|IEMobile|Opera Mini|Windows Phone/i.test(ua);
  const uaTablet=/iPad|Android(?!.*Mobile)|Tablet|Kindle|Silk/i.test(ua);
  // iPadOS 13+ often reports MacIntel with touch
  const iPadDesktopUA=/Macintosh/i.test(ua) && touch && navigator.maxTouchPoints>1;

  let kind='computer';
  if(uaPhone || (w>0 && w<=720 && (touch||coarse) && !/Windows NT|CrOS/i.test(ua))) kind='phone';
  else if(uaTablet || iPadDesktopUA || (w>720 && w<=1024 && (touch||coarse) && !/Windows NT/i.test(ua))) kind='tablet';
  else kind='computer';

  // Narrow desktop browser window stays computer (mouse primary)
  if(kind==='phone' && !uaPhone && !iPadDesktopUA && !coarse && w>0 && w<=720) kind='computer';

  const label={phone:'Phone',tablet:'Tablet',computer:'Computer'}[kind];
  DEVICE={
    kind, label, remote: kind==='phone'||kind==='tablet',
    width:w, height:h, touch, coarse, standalone,
    platform: String(platform||'').slice(0,80),
    ua: String(ua).slice(0,200),
    source:'client',
    at: Date.now()
  };
  try{ sessionStorage.setItem('pocket_device', JSON.stringify(DEVICE)); }catch(_){}
  return DEVICE;
}

function applyDevice(){
  const d=DEVICE||detectDevice();
  document.body.classList.remove('device-phone','device-tablet','device-computer','side-open','rail-open');
  document.body.classList.add('device-'+d.kind);
  const chip=$('deviceChip');
  if(chip){
    chip.textContent=d.label;
    chip.className='chip device-chip '+d.kind;
    chip.title=d.kind+' · '+d.width+'x'+d.height+(d.touch?' · touch':'')+(d.remote?' · remote':' · local UI');
  }
  const det=$('deviceDetail');
  if(det){
    det.innerHTML=`<b>${d.label}</b> · ${d.width}×${d.height}<br>`+
      `${d.remote?'Remote UI (jobs still run on the host PC)':'Computer UI'}<br>`+
      `touch=${!!d.touch} coarse=${!!d.coarse} PWA=${!!d.standalone}`;
  }
  const blurb=$('loginBlurb');
  if(blurb){
    blurb.textContent=d.kind==='phone'
      ? 'Phone remote desk. You control agents on the host PC. Password required.'
      : (d.kind==='tablet'
        ? 'Tablet remote desk for your PC. Password required on public access.'
        : 'Multi-agent desk for your PC. Password required on public access.');
  }
  document.title=d.kind==='phone'?'POCKET · Phone':(d.kind==='tablet'?'POCKET · Tablet':'POCKET');
  updatePhoneNav();
}

function sideIsDrawer(){
  // Phone always drawer; computer becomes drawer under 900px (CSS)
  try{
    if(DEVICE && DEVICE.kind==='phone') return true;
    return (window.innerWidth||0) <= 900;
  }catch(_){ return true; }
}
function toggleSide(){
  // Wide desktop: side is always visible — still allow force-open for recovery
  if(!sideIsDrawer()){
    document.body.classList.add('side-open');
    try{
      const sp=$('sidePanel');
      if(sp){
        sp.scrollTop=0;
        const b=sp.querySelector('.actions button');
        if(b&&b.focus) b.focus();
      }
    }catch(_){}
    return;
  }
  document.body.classList.toggle('side-open');
  document.body.classList.remove('rail-open');
  updatePhoneNav();
}
function toggleRail(){
  // Phone + narrow computer: drawer; wide computer rail is always on-screen
  document.body.classList.toggle('rail-open');
  document.body.classList.remove('side-open');
  updatePhoneNav();
  const close=$('railCloseBtn');
  if(close) close.style.display=document.body.classList.contains('rail-open')?'inline-flex':'none';
  const b=$('btnSys'); if(b) b.classList.toggle('on', document.body.classList.contains('rail-open'));
  try{ localStorage.setItem('pocket_rail', document.body.classList.contains('rail-open')?'1':'0'); }catch(_){}
}
function toggleWorkspacePanel(force){
  // Explicit open/close so Workspace can always be brought back after X
  const open=document.body.classList.contains('rail-open');
  const on=force===true?true:(force===false?false:!open);
  document.body.classList.toggle('rail-open', on);
  document.body.classList.remove('side-open');
  updatePhoneNav();
  const close=$('railCloseBtn');
  if(close) close.style.display=on?'inline-flex':'';
  const b=$('btnSys'); if(b) b.classList.toggle('on', on);
  try{ localStorage.setItem('pocket_rail', on?'1':'0'); }catch(_){}
  if(on){
    try{ refreshPlatformRail(); refreshIotRail(); warmIotRail(); refreshAiWorkspace(); pollSubagents(); }catch(_){}
  }
  _markAppTabs(on?'workspace':(_activeAppTab==='workspace'?'desk':_activeAppTab));
}
let _screenColTimer=null, _screenMode='off', _screenVcomp=false;
let _habitatTimer=null;
function toggleHabitat(force){
  const on=force===true?true:(force===false?false:!document.body.classList.contains('habitat-open'));
  document.body.classList.toggle('habitat-open', on);
  try{ localStorage.setItem('pocket_habitat', on?'1':'0'); }catch(_){}
  const b=$('btnHabitat'); if(b) b.classList.toggle('on', on);
  if(on){
    refreshHabitat();
    if(_habitatTimer) clearInterval(_habitatTimer);
    _habitatTimer=setInterval(()=>{ try{ refreshHabitat(); }catch(_){} }, 8000);
    _markAppTabs('habitat');
  }else if(_habitatTimer){
    clearInterval(_habitatTimer); _habitatTimer=null;
    if(_activeAppTab==='habitat') _markAppTabs('desk');
    else _markAppTabs(_activeAppTab);
  }
  try{ api('/v1/habitat',{method:'POST',body:JSON.stringify({open:on})}); }catch(_){}
}
function _habInitial(name){
  const n=String(name||'?').trim();
  return (n[0]||'?').toUpperCase();
}
function _habStatusClass(st){
  st=String(st||'idle').toLowerCase();
  if(st==='working'||st==='thinking'||st==='running') return 'live';
  if(st==='sensing') return 'sensing';
  if(st==='speaking') return 'speaking';
  return '';
}
let _habitatSig='';
async function refreshHabitat(){
  if(!document.body.classList.contains('habitat-open')) return;
  try{
    const j=await api('/v1/habitat');
    const floor=$('habitatFloor');
    const feed=$('habitatFeed');
    if(!floor) return;
    const residents=j.residents||[];
    // group by room
    const rooms={};
    residents.forEach(r=>{
      const rm=r.room||'floor';
      (rooms[rm]=rooms[rm]||[]).push(r);
    });
    const order=['ops','forge','lab','studio','lounge','swarm','watch','bridge','cloud','guest','floor'];
    const keys=Object.keys(rooms).sort((a,b)=>order.indexOf(a)-order.indexOf(b));
    let html='';
    keys.forEach(rm=>{
      html+='<div class="hb-room">'+esc(rm)+'</div>';
      rooms[rm].forEach(r=>{
        const st=String(r.status||'idle');
        const cls=_habStatusClass(st);
        const mode=r.desk_mode||r.id;
        html+='<div class="hab-card '+cls+'" data-mode="'+esc(mode)+'" role="button" tabindex="0" title="Open '+esc(r.name)+'">'+
          '<div class="hb-av" style="background:'+esc(r.color||'#22c55e')+'">'+esc(_habInitial(r.name))+
          '<span class="hb-dot" aria-hidden="true"></span></div>'+
          '<div class="hb-meta"><div class="hb-name">'+esc(r.name)+'</div>'+
          '<div class="hb-role">'+esc(r.role||'')+'</div>'+
          '<div class="hb-line">'+esc(r.last_line||r.task||'At home')+'</div></div>'+
          '<div class="hb-st">'+esc(st)+'</div></div>';
      });
    });
    const floorHtml=html||'<div class="hint" style="padding:8px">No residents</div>';
    const act=j.activity||[];
    const feedHtml=act.slice(0,8).map(a=>
      '<div class="hf"><b>'+esc(a.agent||'?')+'</b> · '+esc(a.status||'')+' — '+esc((a.line||a.task||'').slice(0,80))+'</div>'
    ).join('')||'<div class="hf">Quiet floor — agents idle in their rooms</div>';
    const sig=floorHtml.length+':'+(residents||[]).map(r=>(r.id||'')+':'+(r.status||'')+':'+(r.last_line||'')).join('|');
    if(sig===_habitatSig) return;
    _habitatSig=sig;
    floor.innerHTML=floorHtml;
    floor.querySelectorAll('.hab-card').forEach(card=>{
      card.onclick=()=>{
        const m=card.getAttribute('data-mode');
        if(m==='work') startWorkingMode();
        else if(m) pickAgent(m);
      };
    });
    if(feed) feed.innerHTML=feedHtml;
    const b=$('btnHabitat'); if(b) b.classList.toggle('on', true);
  }catch(e){
    const floor=$('habitatFloor');
    if(floor && floor.dataset.offline!=='1'){
      floor.dataset.offline='1';
      floor.innerHTML='<div class="hint" style="padding:8px;color:var(--muted)">Habitat offline</div>';
    }
  }
}
function toggleScreenCol(force){
  const on=force===true?true:(force===false?false:!document.body.classList.contains('screen-col-open'));
  document.body.classList.toggle('screen-col-open', on);
  try{ localStorage.setItem('pocket_screen_col', on?'1':'0'); }catch(_){}
  const b=$('btnScreenCol');
  if(b) b.classList.toggle('on', on);
  if(on){
    refreshScreenCol(true);
    refreshScreenTargets();
    if(_screenColTimer) clearInterval(_screenColTimer);
    // 5s is enough for live eyes; faster updates caused visible blink
    _screenColTimer=setInterval(()=>{ try{ refreshScreenCol(false); }catch(_){} }, 5000);
    _markAppTabs('screen');
  }else if(_screenColTimer){
    clearInterval(_screenColTimer); _screenColTimer=null;
    if(_activeAppTab==='screen') _markAppTabs('desk');
    else _markAppTabs(_activeAppTab);
  }
}
async function refreshScreenTargets(){
  const sel=$('scTarget');
  if(!sel) return;
  const cur=sel.value||'desktop';
  try{
    const st=await api('/v1/screen');
    const t=st.targets||{};
    const mons=t.monitors||[];
    const wins=t.windows||[];
    let html='';
    mons.forEach(m=>{
      html+='<option value="'+esc(m.id||'')+'">'+esc(m.label||m.id)+'</option>';
    });
    // Non-POCKET windows first (already sorted server-side)
    const apps=wins.filter(w=>!w.is_pocket);
    const pocket=wins.filter(w=>w.is_pocket);
    if(apps.length){
      html+='<optgroup label="Other apps (keep POCKET open)">';
      apps.forEach(w=>{
        html+='<option value="hwnd:'+esc(String(w.hwnd||''))+'">'+esc((w.title||'Window').slice(0,70))+'</option>';
      });
      html+='</optgroup>';
    }
    if(pocket.length){
      html+='<optgroup label="POCKET windows">';
      pocket.forEach(w=>{
        html+='<option value="hwnd:'+esc(String(w.hwnd||''))+'">'+esc((w.title||'POCKET').slice(0,70))+'</option>';
      });
      html+='</optgroup>';
    }
    sel.innerHTML=html||'<option value="desktop">All monitors (desktop)</option>';
    // restore selection
    const want=st.target==='window'&&st.window_hwnd?('hwnd:'+st.window_hwnd):(st.target||cur||'desktop');
    if([...sel.options].some(o=>o.value===want)) sel.value=want;
    else if([...sel.options].some(o=>o.value===cur)) sel.value=cur;
  }catch(e){
    if(!sel.options.length) sel.innerHTML='<option value="desktop">All monitors (desktop)</option>';
  }
}
async function setScreenTarget(val){
  val=String(val||'desktop');
  const body={};
  if(val.startsWith('hwnd:')){
    body.target='window';
    body.window_hwnd=parseInt(val.split(':')[1],10)||0;
  }else{
    body.target=val;
    body.window_hwnd=0;
    body.window_title='';
  }
  // Keep share mode if already viewing
  if(_screenMode==='off') body.mode='view';
  else body.mode=_screenMode;
  try{
    const j=await api('/v1/screen',{method:'POST',body:JSON.stringify(body)});
    _screenMode=j.mode||_screenMode;
    _paintScreenMode();
    toast(val.startsWith('hwnd:')?'Watching that window — keep POCKET open':'Watch target: '+(j.target||val));
    refreshScreenCol(true);
  }catch(e){ toast(e.message||'target failed','err'); }
}
function _paintScreenMode(){
  ['scOff','scView','scCtrl'].forEach(id=>{
    const el=$(id); if(!el) return;
    el.classList.toggle('on', (id==='scOff'&&_screenMode==='off')||(id==='scView'&&_screenMode==='view')||(id==='scCtrl'&&_screenMode==='control'));
  });
  const vc=$('scVcomp'); if(vc) vc.classList.toggle('on', !!_screenVcomp);
  const badge=$('scBadge');
  if(badge){
    badge.textContent=_screenMode==='off'?'share off':(_screenMode==='control'?'CONTROL · agents drive':'VIEW · agents see');
    badge.style.color=_screenMode==='control'?'#fca5a5':(_screenMode==='view'?'#67e8f9':'#a1a1aa');
  }
}
async function setScreenMode(mode){
  try{
    // When enabling share, heal/reset stale window targets (broken reservation hwnd etc.)
    const body={mode:mode,vcomp:_screenVcomp};
    if(mode==='view'||mode==='control'){
      body.reset_target=true;
      body.target=body.target||'desktop';
    }
    const j=await api('/v1/screen',{method:'POST',body:JSON.stringify(body)});
    _screenMode=j.mode||mode;
    _screenVcomp=!!j.vcomp;
    _paintScreenMode();
    if(j.healed&&j.healed.healed) toast('Screen target healed → desktop');
    toast(_screenMode==='off'?'Screen share off':(_screenMode==='control'?'Agents may control mouse/keyboard':'Agents can see your screen'));
    if(_screenMode!=='off') refreshScreenCol(true);
  }catch(e){ toast(e.message||'screen mode failed','err'); }
}
async function toggleVcompShare(){
  _screenVcomp=!_screenVcomp;
  try{
    const j=await api('/v1/screen',{method:'POST',body:JSON.stringify({mode:_screenMode==='off'?'view':_screenMode,vcomp:_screenVcomp})});
    _screenMode=j.mode||_screenMode;
    _screenVcomp=!!j.vcomp;
    if(_screenVcomp){
      try{ await api('/v1/vcomp/open',{method:'POST',body:JSON.stringify({label:'desk'})}); }catch(_){}
    }
    _paintScreenMode();
    toast(_screenVcomp?'VComputer armed':'VComputer idle');
  }catch(e){ toast(e.message||'vcomp failed','err'); }
}
async function refreshScreenCol(force){
  if(!document.body.classList.contains('screen-col-open') && !force) return;
  try{
    const st=await api('/v1/screen');
    _screenMode=st.mode||'off';
    _screenVcomp=!!st.vcomp;
    _paintScreenMode();
    // Surface target so dead windows are obvious (not the select#scTarget)
    const tg=$('scTargetHint');
    if(tg) tg.textContent='· '+(st.target||'desktop')+(st.label&&st.label!=='desktop'?' · '+String(st.label).slice(0,20):'');
  }catch(_){}
  if(_screenMode==='off'){
    const br=$('scBrief'); if(br) br.textContent='Share is off. Choose View (agents see fusion) or Control (mouse + keyboard).';
    const img=$('scFrame'); if(img){ img.removeAttribute('src'); img.dataset.sig=''; }
    return;
  }
  try{
    const fr=await api('/v1/screen/frame');
    const img=$('scFrame');
    if(img && fr.ok!==false && fr.base64){
      // Only swap image when frame changes — constant src rewrites cause blink
      const sig=(fr.seq||'')+':'+(fr.base64.length)+':'+(fr.base64.slice(-24));
      if(img.dataset.sig!==sig){
        img.dataset.sig=sig;
        img.src='data:'+(fr.mime||'image/jpeg')+';base64,'+fr.base64;
      }
    }else if(img && fr && fr.ok===false){
      // One-shot heal then retry once
      try{ await api('/v1/screen/heal',{method:'POST',body:JSON.stringify({desktop:true})}); }catch(_){}
      try{
        const fr2=await api('/v1/screen/frame');
        if(img && fr2.base64){
          img.dataset.sig='heal';
          img.src='data:'+(fr2.mime||'image/jpeg')+';base64,'+fr2.base64;
        }
      }catch(_){}
    }
  }catch(_){}
  try{
    const cx=await api('/v1/screen/context?agent=desk');
    const br=$('scBrief');
    let brief=cx.brief||cx.message||'';
    if(cx.shared===false) brief='Share off for agents — click View or Control above.';
    if(!brief) brief=JSON.stringify(cx).slice(0,200);
    if(br && br.textContent!==brief) br.textContent=brief;
    const sym=$('scSyms');
    if(sym){
      const list=cx.symbols_sample||[];
      const html=list.slice(0,18).map(s=>'<span>'+esc(String(s).slice(0,28))+'</span>').join('')||'<span>no symbols yet</span>';
      if(sym.dataset.sig!==html){ sym.dataset.sig=html; sym.innerHTML=html; }
    }
  }catch(e){
    const br=$('scBrief');
    if(br) br.textContent='Sense failed — try View again or Heal desktop.';
  }
}
async function screenSense(){
  try{
    if(_screenMode==='off') await setScreenMode('view');
    let j;
    try{ j=await api('/v1/screen/sense',{method:'POST',body:JSON.stringify({agent:'desk',ensure:true})}); }
    catch(_){ j=await api('/v1/screen/context?agent=desk'); }
    const br=$('scBrief'); if(br) br.textContent=j.brief||j.message||'sensed';
    toast(j.ok===false?(j.message||'sense soft-fail'):'Fusion sense ok');
    refreshScreenCol(true);
  }catch(e){ toast(e.message||'sense failed','err'); }
}
async function screenHealDesktop(){
  try{
    await api('/v1/screen/heal',{method:'POST',body:JSON.stringify({desktop:true})});
    await setScreenMode(_screenMode==='off'?'view':_screenMode);
    toast('Screen target → desktop');
    refreshScreenCol(true);
  }catch(e){ toast(e.message||'heal failed','err'); }
}
async function screenRemake(){
  try{
    const j=await api('/v1/fusion/remake',{method:'POST',body:JSON.stringify({refresh_page:true})});
    toast(j.ok?'Remake ready':'Remake: '+(j.error||'done'));
    const out=$('scActOut'); if(out){ out.style.display='block'; out.textContent=JSON.stringify(j,null,2).slice(0,1200); }
  }catch(e){
    try{
      const j=await api('/v1/rfe/synthesize',{method:'POST',body:JSON.stringify({refresh:true})});
      toast('RFE synthesize');
      const out=$('scActOut'); if(out){ out.style.display='block'; out.textContent=JSON.stringify(j,null,2).slice(0,1200); }
    }catch(e2){ toast(e2.message||'remake failed','err'); }
  }
}
async function screenAct(action, extra){
  try{
    if(_screenMode!=='control'){
      toast('Switch to Control to let agents drive input');
      return;
    }
    const body=Object.assign({action:action,agent:'desk'}, extra||{});
    const j=await api('/v1/screen/act',{method:'POST',body:JSON.stringify(body)});
    const out=$('scActOut'); if(out){ out.style.display='block'; out.textContent=JSON.stringify(j,null,2).slice(0,1400); }
    toast(j.ok?('act '+action): (j.error||'act failed'));
    setTimeout(()=>refreshScreenCol(true), 400);
  }catch(e){ toast(e.message||'act failed','err'); }
}
function screenActClick(){
  const name=prompt('UI name to click (fusion / UIA):','');
  if(!name) return;
  screenAct('click',{name:name});
}
function closeDrawers(){
  document.body.classList.remove('side-open','rail-open');
  updatePhoneNav();
}
function focusChat(){
  closeDrawers();
  try{ $('input').focus(); }catch(_){}
}
function updatePhoneNav(){
  if(DEVICE.kind!=='phone') return;
  const side=document.body.classList.contains('side-open');
  const rail=document.body.classList.contains('rail-open');
  const a=$('navAgents'), c=$('navChat'), s=$('navSys');
  if(a) a.classList.toggle('on', side);
  if(s) s.classList.toggle('on', rail);
  if(c) c.classList.toggle('on', !side && !rail);
}

function authHeaders(){
  const h={'Content-Type':'application/json'};
  const tok=sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'';
  const u=sessionStorage.getItem('pocket_user')||localStorage.getItem('pocket_user')||'';
  // Prefer session token only (production — no password in storage)
  if(tok){
    h['X-Pocket-Token']=tok;
    h['Authorization']='Bearer '+tok;
  }
  // Tell server: phone | tablet | computer
  h['X-Pocket-Device']=(DEVICE&&DEVICE.kind)||'computer';
  if(u) h['X-Pocket-User']=u;
  return h;
}
async function api(path, opts){
  opts=opts||{};
  opts.headers=Object.assign({}, authHeaders(), opts.headers||{});
  let r;
  try{
    r=await fetch(path, opts);
  }catch(net){
    const err=new Error('Network: '+(net&&net.message||'Failed to fetch')+' — is host on :8787?');
    err.code='network';
    throw err;
  }
  if(r.status===401){
    const err=new Error('Login required');
    err.code='auth';
    // Don't thrash gate on every background poll — only clear session on explicit auth fail
    // (boot / doLogout decide when to show gate)
    throw err;
  }
  if(r.status===429){ const e=new Error('Too many failed logins'); e.code='rate'; throw e; }
  if(!r.ok){
    const t=(await r.text()).slice(0,300);
    const e=new Error(t||('HTTP '+r.status));
    e.code='http';
    e.status=r.status;
    throw e;
  }
  const ct=r.headers.get('content-type')||'';
  if(ct.includes('application/json')) return r.json();
  return {text: await r.text()};
}
function setLoginErr(msg){
  const el=$('loginErr');
  if(el) el.textContent=msg||'';
  if(msg) try{ toast(msg,'err'); }catch(_){}
}
function showGate(){
  dismissBootSplash(true);
  const g=$('loginGate');
  if(!g) return;
  g.classList.add('open');
  g.style.display='flex';
  g.style.visibility='visible';
  g.style.pointerEvents='auto';
  // Localhost: offer one-click unlock
  const local=location.hostname==='127.0.0.1'||location.hostname==='localhost';
  const lub=$('localUnlockBtn');
  if(lub) lub.style.display=local?'block':'none';
  const u=$('loginUser');
  if(u && !u.value) u.value='pocket';
  try{ ($('loginPass')||u).focus(); }catch(_){}
}
function hideGate(){
  const g=$('loginGate');
  if(!g) return;
  g.classList.remove('open');
  g.style.display='none';
  g.style.visibility='hidden';
  g.style.pointerEvents='none';
  // never leave scrim/browser covering the desk by accident
  try{ closeDrawers(); }catch(_){}
  try{
    const bl=$('browserLayer');
    if(bl && !bl.classList.contains('open')){
      bl.style.pointerEvents='none';
    }
  }catch(_){}
}
function setAuthTab(t){
  authTab=t;
  const tl=$('tabLogin'), tr=$('tabReg'), lp=$('loginPane'), rp=$('regPane');
  if(tl) tl.classList.toggle('on', t==='login');
  if(tr) tr.classList.toggle('on', t==='register');
  if(lp) lp.style.display=t==='login'?'block':'none';
  if(rp) rp.style.display=t==='register'?'block':'none';
  setLoginErr('');
}
function storeSession(user, token, rem){
  // Always keep sessionStorage; persist to localStorage when remembered (default true)
  try{
    sessionStorage.setItem('pocket_user', user||'');
    sessionStorage.setItem('pocket_token', token||'');
    sessionStorage.removeItem('pocket_pass');
    localStorage.removeItem('pocket_pass');
    const persist = rem!==false;
    if(persist && token){
      localStorage.setItem('pocket_user', user||'');
      localStorage.setItem('pocket_token', token||'');
    }
  }catch(e){ console.warn('storeSession', e); }
}
function showFirstRunIfNeeded(){
  try{
    if(localStorage.getItem('pocket_first_run_done')==='1') return;
    const tip=$('firstRunTips');
    if(tip) tip.style.display='block';
  }catch(_){}
}
function dismissFirstRun(){
  try{ localStorage.setItem('pocket_first_run_done','1'); }catch(_){}
  const tip=$('firstRunTips');
  if(tip) tip.style.display='none';
}
async function finishLogin(u, token){
  storeSession(u, token, true);
  hideGate();
  dismissBootSplash(true);
  try{
    await boot({afterLogin:true});
    toast('Welcome, '+u,'ok');
    showFirstRunIfNeeded();
  }catch(bootErr){
    hideGate();
    toast('Signed in','ok');
    console.warn('boot after login', bootErr);
  }
}
async function tryDesktopAutoLogin(force){
  // Electron / localhost only — host issues operator session without typing password
  if(location.hostname!=='127.0.0.1' && location.hostname!=='localhost') return false;
  if(!force && (sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token'))) return false;
  try{
    const r=await fetch('/v1/auth/desktop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
    if(!r.ok) return false;
    const j=await r.json();
    if(!j.ok||!j.token) return false;
    await finishLogin((j.user&&j.user.user)||'pocket', j.token);
    return true;
  }catch(_){ return false; }
}
async function doLogin(){
  try{
    const uEl=$('loginUser'), pEl=$('loginPass'), btn=$('loginBtn');
    let u=(uEl&&uEl.value||'').trim();
    const p=(pEl&&pEl.value||'');
    if(!p){
      setLoginErr('Enter your password (username defaults to pocket).');
      return;
    }
    if(!u){ u='pocket'; if(uEl) uEl.value='pocket'; }
    setLoginErr('Signing in…');
    if(btn) btn.disabled=true;
    // Unified client — same path as phone / public gate / studio
    if(window.PocketAuth && PocketAuth.login){
      const res=await PocketAuth.login(u, p, {device:'desk'});
      if(!res.ok){
        if((location.hostname==='127.0.0.1'||location.hostname==='localhost')){
          const auto=await tryDesktopAutoLogin(true);
          if(auto){ if(btn) btn.disabled=false; return; }
        }
        setLoginErr(res.error||'Could not sign in. Try username pocket + ACCESS.txt password.');
        if(btn) btn.disabled=false;
        return;
      }
      const uname=(res.user&&(res.user.user||res.user.display))||u||'pocket';
      await finishLogin(uname, res.token);
      if(btn) btn.disabled=false;
      return;
    }
    const r=await fetch('/v1/auth/login',{
      method:'POST',
      credentials:'same-origin',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({user:u,password:p,username:u})
    });
    let j={};
    try{ j=await r.json(); }catch(_){ j={ok:false,error:'Login returned non-JSON (HTTP '+r.status+')'}; }
    const tok=j.token||j.session_token||'';
    if(!r.ok||(!j.ok&&!tok)){
      if((location.hostname==='127.0.0.1'||location.hostname==='localhost')){
        const auto=await tryDesktopAutoLogin(true);
        if(auto){ if(btn) btn.disabled=false; return; }
      }
      setLoginErr(j.error||('Could not sign in ('+r.status+'). Check username/password (try pocket).'));
      if(btn) btn.disabled=false;
      return;
    }
    if(!tok){ setLoginErr('Sign-in did not return a session. Try again.'); if(btn) btn.disabled=false; return; }
    await finishLogin(u, tok);
    if(btn) btn.disabled=false;
  }catch(e){
    setLoginErr('Cannot reach POCKET right now. Open the app on this computer and try again.');
    const btn=$('loginBtn'); if(btn) btn.disabled=false;
  }
}
async function doRegister(){
  try{
    if(!$('regTerms')||!$('regTerms').checked){
      $('loginErr').textContent='Accept the terms to register';
      return;
    }
    const j=await fetch('/v1/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      invite:$('regInvite').value.trim(),
      user:$('regUser').value.trim(),
      password:$('regPass').value,
      display:$('regDisplay').value.trim(),
      accepted_terms:true
    })}).then(r=>r.json());
    if(!j.ok){ $('loginErr').textContent=j.error||'Register failed'; return; }
    storeSession(j.user, j.token||'', true);
    hideGate();
    await boot();
    toast('Account created — welcome');
  }catch(e){ $('loginErr').textContent=String(e.message||e); }
}
async function doLogout(){
  try{
    await api('/v1/auth/logout',{method:'POST',body:JSON.stringify({})});
  }catch(_){}
  sessionStorage.clear();
  localStorage.removeItem('pocket_token');
  localStorage.removeItem('pocket_pass');
  ME={user:'',role:'member',display:''};
  showGate();
  toast('Signed out');
}
function applyRoleUI(){
  const admin = (ME.role||'')==='admin';
  document.querySelectorAll('.admin-only').forEach(el=>{
    el.style.display = admin ? '' : 'none';
  });
  const lb=$('logoutBtn');
  if(lb) lb.style.display = ME.user ? 'inline-flex' : 'none';
  if($('userChip')) $('userChip').textContent = ME.user ? ((ME.display||ME.user)+' · '+ME.role) : 'signed out';
}
async function boot(opts){
  opts=opts||{};
  ensureLivePoll();
  detectDevice();
  applyDevice();
  // Restore Screen column preference (Claude-style side panel)
  try{
    if(localStorage.getItem('pocket_screen_col')==='1'){
      document.body.classList.add('screen-col-open');
      const b=$('btnScreenCol'); if(b) b.classList.toggle('on', true);
      setTimeout(()=>{ try{ refreshScreenCol(true); refreshScreenTargets(); }catch(_){} }, 800);
      if(_screenColTimer) clearInterval(_screenColTimer);
      _screenColTimer=setInterval(()=>{ try{ refreshScreenCol(false); }catch(_){} }, 5000);
    }
  }catch(_){}
  // Habitat hybrid floor — open by default unless user closed it
  try{
    const pref=localStorage.getItem('pocket_habitat');
    if(pref!=='0'){
      document.body.classList.add('habitat-open');
      const b=$('btnHabitat'); if(b) b.classList.toggle('on', true);
      setTimeout(()=>{ try{ refreshHabitat(); }catch(_){} }, 400);
      if(_habitatTimer) clearInterval(_habitatTimer);
      _habitatTimer=setInterval(()=>{ try{ refreshHabitat(); }catch(_){} }, 8000);
    }else{
      document.body.classList.remove('habitat-open');
      const b=$('btnHabitat'); if(b) b.classList.toggle('on', false);
    }
  }catch(_){}
  // Workspace rail preference
  try{
    if(localStorage.getItem('pocket_rail')==='1'){
      document.body.classList.add('rail-open');
      const b=$('btnSys'); if(b) b.classList.toggle('on', true);
    }
  }catch(_){}
  try{ _markAppTabs('desk'); }catch(_){}
  try{ setTimeout(()=>{ refreshPlatformRail(); refreshIotRail(); refreshDeskReadyStrip(); }, 900); }catch(_){}
  try{ localStorage.removeItem('pocket_pass'); sessionStorage.removeItem('pocket_pass'); }catch(_){}
  // Mirror localStorage → sessionStorage so one tab stays signed in
  if(!sessionStorage.getItem('pocket_token') && localStorage.getItem('pocket_token')){
    sessionStorage.setItem('pocket_token', localStorage.getItem('pocket_token'));
    sessionStorage.setItem('pocket_user', localStorage.getItem('pocket_user')||'');
  }
  let has = sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token');
  if(!has && !opts.afterLogin){
    // Desktop/localhost: auto session so Electron feels like a normal app
    const auto=await tryDesktopAutoLogin();
    if(auto) return;
    has = sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token');
  }
  if(!has){ showGate(); dismissBootSplash(); return; }

  // Auth check only — 401 returns to gate; anything else keeps session
  try{
    const me=await api('/v1/auth/me',{method:'POST',body:JSON.stringify({})});
    if(me&&me.user){ ME=me.user; }
    else if(me&&me.ok===false){ showGate(); dismissBootSplash(); return; }
  }catch(e){
    if(e&&e.code==='auth'){ showGate(); dismissBootSplash(); return; }
    // network/http: stay optimistic if we have a token after login
    if(!opts.afterLogin){ /* still try to load UI */ }
  }
  hideGate();
  // belt-and-suspenders: never leave full-screen blockers after login
  try{
    const g=$('loginGate'); if(g){ g.style.display='none'; g.style.pointerEvents='none'; g.classList.remove('open'); }
    const sp=$('bootSplash'); if(sp){ sp.classList.add('done'); sp.style.pointerEvents='none'; }
  }catch(_){}
  applyRoleUI();
  try{
    status=await api('/v1/status');
  }catch(e){
    if(e&&e.code==='auth'){ showGate(); return; }
    status={ok:true,degraded:true,version:'',engine:{},how:{}};
  }
  try{
    const e=status.engine||{};
    const pub=status.public_url||(status.how&&status.how.phone_anywhere);
    if($('topMeta')){
      const grade = status.class || status.grade || '';
      const classOn = status.first_class===true || grade==='A' || grade==='S';
      // Production status rail — host always on if we painted; voice filled async
      $('topMeta').innerHTML =
        `<div class="prod-rail" id="prodRail">`+
        `<span class="prod-pill on" title="POCKET host :8787"><i></i>Host</span>`+
        `<span class="prod-pill warn" id="pillVoice" title="Pocket Voice API"><i></i>Voice…</span>`+
        `<span class="prod-pill ${micOn?'on':'warn'}" id="pillMic" title="Microphone"><i></i>Mic</span>`+
        `</div>`+
        chip('Codex',e.codex)+chip('Grok',e.grok)+
        (grade?`<span class="chip ${classOn?'on':'warn'}" title="GET /v1/class">${esc(String(grade))}</span>`:'')+
        `<span class="chip on">v${status.version||''}</span>`;
      try{ refreshProdPills(); }catch(_){}
    }
    if($('pubUrl')) $('pubUrl').innerHTML = pub&&String(pub).startsWith('http') ? ('Public <a href="'+pub+'" target="_blank">'+pub+'</a>') : 'Public host not set';
    const sel=$('wsSelect');
    if(sel){
      sel.innerHTML='';
      (e.workspaces||[]).forEach(w=>{
        if(w.exists===false) return;
        const o=document.createElement('option'); o.value=w.id; o.textContent=w.label; sel.appendChild(o);
      });
      if(!sel.options.length){ const o=document.createElement('option'); o.value='workspace'; o.textContent='workspace'; sel.appendChild(o); }
    }
    if($('userChip')) $('userChip').textContent = (ME.display||ME.user)||sessionStorage.getItem('pocket_user')||'user';
  }catch(_){}

  // Soft-load panels — never bounce to login for panel failures
  await Promise.allSettled([
    refreshSessions().catch(()=>{}),
    refreshLive().catch(()=>{}),
    refreshUsage().catch(()=>{}),
    refreshOrganism().catch(()=>{}),
    refreshStack().catch(()=>{}),
  ]);
  try{ await api('/v1/live/connect',{method:'POST',body:JSON.stringify({service:'all'})}); }catch(_){}
  ensureLivePoll();
  try{ pollSubagents(); }catch(_){}
  if(!boot._timers){
    boot._timers=true;
    setInterval(()=>{ try{ refreshLive(); }catch(_){} }, 15000);
    setInterval(()=>{ try{ refreshUsage(); }catch(_){} }, 30000);
    // Sessions list only — transcript updates via scheduleSessPoll (no blink)
    setInterval(()=>{ try{ refreshSessions(); }catch(_){} }, 14000);
    setInterval(()=>{ try{ refreshOrganism(); }catch(_){} }, 20000);
    setInterval(()=>{ try{ refreshProdPills(); }catch(_){} }, 18000);
  }
  // Production: wake voice once at boot so mic is never cold
  try{ probeVoiceApi().then(()=>refreshProdPills()); }catch(_){}
  dismissBootSplash();
}
async function refreshProdPills(){
  const v=$('pillVoice'), m=$('pillMic'), st=$('stPocket');
  // Voice
  if(v){
    let ok=false;
    try{ ok=await probeVoiceApi(); }catch(_){ ok=false; }
    v.className='prod-pill '+(ok?'on':'off');
    v.innerHTML='<i></i>Voice';
    v.title=ok?('Voice API · '+String(micVoiceBase||'').replace(location.origin,'')):'Voice offline — will auto-start on mic';
  }
  // Mic state
  if(m){
    m.className='prod-pill '+(micOn?'on':(window.isSecureContext||location.hostname==='127.0.0.1'?'warn':'off'));
    m.innerHTML='<i></i>'+(micOn?'Mic on':'Mic');
    m.title=micOn?'Microphone active':'Click 🎙 in composer to talk';
  }
  if(st){ st.textContent='ready'; st.className='on'; }
  // Stack card voice line if present
  try{
    let nv=$('stVoice');
    if(!nv){
      const card=$('stackCard');
      if(card){
        const row=document.createElement('div');
        row.className='sk';
        row.innerHTML='<b>Voice</b><span class="off" id="stVoice">…</span>';
        card.appendChild(row);
        nv=$('stVoice');
      }
    }
    if(nv){
      nv.textContent=micVoiceApi?'live':'down';
      nv.className=micVoiceApi?'on':'off';
    }
  }catch(_){}
}
function dismissBootSplash(immediate){
  const el=$('bootSplash');
  if(!el) return;
  const finish=()=>{ el.classList.add('done'); el.setAttribute('aria-hidden','true'); el.style.pointerEvents='none'; };
  if(immediate || el.classList.contains('done')){ finish(); return; }
  // Minimum show so the production intro is visible
  const minMs=400;
  const started=window.__pocketBootAt||Date.now();
  const wait=Math.max(0, minMs-(Date.now()-started));
  setTimeout(finish, wait);
}
function goAppBack(){
  // Prefer in-app surfaces — never yank the user out of the POCKET shell
  if($('appPanelLayer')&&$('appPanelLayer').classList.contains('open')){ showAppTab('desk'); return; }
  if($('browserLayer')&&$('browserLayer').classList.contains('open')){ closeBrowser(); return; }
  if(document.body.classList.contains('screen-col-open')){ toggleScreenCol(false); return; }
  if(document.body.classList.contains('habitat-open') && window.innerWidth<900){ toggleHabitat(false); return; }
  showAppTab('desk');
}
function goDeskHome(){
  showAppTab('desk');
  activeId=null;
  try{ showEmpty(); }catch(_){}
  try{ refreshSessions(); }catch(_){}
  try{ refreshDeskReadyStrip(); }catch(_){}
}

/**
 * Every product tab is first-class: own route or column, own actions, own job.
 * Tabs stay separate — never merged into one surface.
 */
const APP_TAB_ROUTES={
  os:{
    path:'/os', title:'Agent OS', group:'Systems',
    blurb:'Every system first-class — map, parity, projects.',
    actions:[
      {label:'Refresh OS', fn:'refreshPlatformRail', primary:true},
      {label:'Ship loop', fn:'runWorkflow', arg:'ship_loop'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  work:{
    path:'/work', title:'Work Studio', group:'Studios',
    blurb:'First-class digital assistant — life ops, research, Muse, Auro (separate from coding desk).',
    actions:[
      {label:'Open Studio', fn:'appPanelReload', primary:true},
      {label:'Life ops board', fn:'startWorkingMode'},
      {label:'Seat assistant', fn:'pickAgent', arg:'assist'},
      {label:'Muse Spark', fn:'pickAgent', arg:'muse_spark'},
      {label:'Auro', fn:'pickAgent', arg:'auro'}
    ]
  },
  studio:{
    path:'/studio', title:'Product Studio', group:'Studios',
    blurb:'First-class for agents — record · storyboard · viral pack · caption · ship.',
    actions:[
      {label:'Studio loop', fn:'runWorkflow', arg:'studio_loop', primary:true},
      {label:'Seat Studio', fn:'pickAgent', arg:'studio'},
      {label:'Ship pack', fn:'runStudioShip'},
      {label:'Viral pack', fn:'runStudioViral'},
      {label:'Storyboard', fn:'runStudioStoryboard'},
      {label:'Creative chat', fn:'showAppTab', arg:'creative'},
      {label:'Screen eyes', fn:'showAppTab', arg:'screen'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  loomgraph:{
    path:'/loomgraph', title:'LOOMGRAPH', group:'Studios',
    blurb:'Default forever harness — readable graphs + control loops orchestrated on Pocket.',
    actions:[
      {label:'Open LOOMGRAPH', fn:'appPanelReload', primary:true},
      {label:'Creative Studio', fn:'showAppTab', arg:'creative'},
      {label:'Product Studio', fn:'showAppTab', arg:'studio'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  creative:{
    path:'/studio/create', title:'Creative Studio', group:'Studios',
    blurb:'Friendly OpenAI-style chat — image · video · blog · paper · social. Share to Community on purpose only.',
    actions:[
      {label:'Open Creative', fn:'appPanelReload', primary:true},
      {label:'Community feed', fn:'showAppTab', arg:'community'},
      {label:'Product Studio', fn:'showAppTab', arg:'studio'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  community:{
    path:'/community', title:'Community', group:'Studios',
    blurb:'Intentional public shares from Pocket users — nothing auto-posts from private chats.',
    actions:[
      {label:'Open feed', fn:'appPanelReload', primary:true},
      {label:'Create & share', fn:'showAppTab', arg:'creative'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  voice_studio:{
    path:'/studio/voice', title:'Voice Studio', group:'Studios',
    blurb:'V2V canvas · persona · code snap.',
    actions:[
      {label:'Seat Aria', fn:'pickAgent', arg:'voice', primary:true},
      {label:'Voice + Fusion', fn:'runWorkflow', arg:'voice_loop'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  lab:{
    path:'/lab', title:'Lab', group:'Studios',
    blurb:'First-class readiness — Studio · Capsules · Life · Phone. Opens own panel; never merges Desk.',
    actions:[
      {label:'Refresh Lab', fn:'appPanelReload', primary:true},
      {label:'Seat Studio', fn:'pickAgent', arg:'studio'},
      {label:'Allocate capsule', fn:'runCapsuleAllocate'},
      {label:'Studio loop', fn:'runWorkflow', arg:'studio_loop'},
      {label:'Phone · IoT', fn:'runWorkflow', arg:'phone_iot'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  mcp:{
    path:'/developers', title:'API · MCP', group:'Systems',
    blurb:'Keys, MCP tools, and developer docs.',
    actions:[
      {label:'Open API docs', fn:'appPanelReload', primary:true},
      {label:'Seat Codex', fn:'pickAgent', arg:'codex'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  curiosities:{
    path:'/curiosities', title:'Curiosities', group:'Lab',
    blurb:'Dream, Duel, and experimental surfaces.',
    actions:[
      {label:'Habitat', fn:'showAppTab', arg:'habitat', primary:true},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  phone:{
    path:'/phone', title:'Phone · Aether', group:'Device',
    blurb:'Aether phone, pair codes, IoT home.',
    actions:[
      {label:'Pair + IoT', fn:'runWorkflow', arg:'phone_iot', primary:true},
      {label:'Refresh IoT', fn:'refreshIotRail'},
      {label:'Desk', fn:'showAppTab', arg:'desk'}
    ]
  },
  platform:{
    path:'/os', title:'Platform', group:'Systems',
    blurb:'Sovereign stack · clouds · remote · IoT.',
    actions:[
      {label:'Refresh stack', fn:'refreshPlatformRail', primary:true},
      {label:'Ship loop', fn:'runWorkflow', arg:'ship_loop'},
      {label:'Remote browser', fn:'runWorkflow', arg:'remote_loop'},
      {label:'Phone · IoT', fn:'runWorkflow', arg:'phone_iot'}
    ]
  },
  sovereign:{path:'/os', title:'Sovereign stack', group:'Systems', blurb:'Sovereign stack status.', actions:[]}
};
const APP_MORE_TABS=new Set(['work','studio','voice_studio','lab','os','mcp','curiosities']);
let _activeAppTab='desk';
function toggleTabMore(ev){
  if(ev){ try{ ev.stopPropagation(); }catch(_){} }
  const m=$('tabMoreMenu'); const b=$('tabMoreBtn');
  if(!m) return;
  const open=!m.classList.contains('open');
  m.classList.toggle('open', open);
  if(b){ b.setAttribute('aria-expanded', open?'true':'false'); b.classList.toggle('on', open || APP_MORE_TABS.has(_activeAppTab)); }
}
function closeTabMore(){
  const m=$('tabMoreMenu'); const b=$('tabMoreBtn');
  if(m) m.classList.remove('open');
  if(b){
    b.setAttribute('aria-expanded','false');
    b.classList.toggle('on', APP_MORE_TABS.has(_activeAppTab));
  }
}
document.addEventListener('click', function(e){
  const wrap=document.querySelector('.tab-more-wrap');
  if(wrap && !wrap.contains(e.target)) closeTabMore();
});
document.addEventListener('keydown', function(e){
  if(e.key!=='Escape') return;
  if($('tabMoreMenu')&&$('tabMoreMenu').classList.contains('open')){ closeTabMore(); e.preventDefault(); return; }
  if($('appPanelLayer')&&$('appPanelLayer').classList.contains('open')){ showAppTab('desk'); e.preventDefault(); return; }
  if($('browserLayer')&&$('browserLayer').classList.contains('open')){ closeBrowser(); e.preventDefault(); return; }
});
function _markAppTabs(tab){
  _activeAppTab=tab||'desk';
  document.querySelectorAll('#appTabs a[data-tab], #tabMoreMenu a[data-tab]').forEach(a=>{
    const t=a.getAttribute('data-tab');
    a.classList.toggle('on', t===_activeAppTab);
    a.classList.toggle('on-desk', t==='desk' && _activeAppTab==='desk');
  });
  const moreBtn=$('tabMoreBtn');
  if(moreBtn) moreBtn.classList.toggle('on', APP_MORE_TABS.has(_activeAppTab));
  const bh=$('btnHabitat'); if(bh) bh.classList.toggle('on', _activeAppTab==='habitat' || document.body.classList.contains('habitat-open'));
  const bs=$('btnScreenCol'); if(bs) bs.classList.toggle('on', _activeAppTab==='screen' || document.body.classList.contains('screen-col-open'));
  const bw=$('btnSys'); if(bw) bw.classList.toggle('on', _activeAppTab==='workspace' || document.body.classList.contains('rail-open'));
}
function _runTabAction(fn, arg){
  try{
    if(fn==='showAppTab') return showAppTab(arg);
    if(fn==='runWorkflow') return runWorkflow(arg);
    if(fn==='runStudioViral') return runStudioViral();
    if(fn==='runStudioStoryboard') return runStudioStoryboard();
    if(fn==='runStudioShip') return runStudioShip();
    if(fn==='runCapsuleAllocate') return runCapsuleAllocate();
    if(fn==='pickAgent') return pickAgent(arg);
    if(fn==='startWorkingMode') return startWorkingMode();
    if(fn==='refreshPlatformRail') return refreshPlatformRail();
    if(fn==='refreshIotRail') return refreshIotRail();
    if(fn==='appPanelReload') return appPanelReload();
    if(fn==='toggleHabitat') return toggleHabitat(true);
    if(fn==='toggleScreenCol') return toggleScreenCol(true);
    if(typeof window[fn]==='function') return arg!=null?window[fn](arg):window[fn]();
  }catch(e){ try{ toast(e.message||String(e),'err'); }catch(_){} }
}
function _renderAppPanelActions(route){
  const box=$('appPanelActions');
  if(!box) return;
  box.innerHTML='';
  if(!route) return;
  if(route.blurb){
    const b=document.createElement('span');
    b.className='ap-blurb';
    b.textContent=route.blurb;
    box.appendChild(b);
  }
  (route.actions||[]).forEach(a=>{
    const btn=document.createElement('button');
    btn.type='button';
    btn.textContent=a.label||'Action';
    if(a.primary) btn.className='primary';
    btn.onclick=function(){ _runTabAction(a.fn, a.arg); };
    box.appendChild(btn);
  });
}
function closeAppPanel(){
  const layer=$('appPanelLayer');
  if(!layer) return;
  layer.classList.remove('open');
  layer.setAttribute('aria-hidden','true');
  const frame=$('appPanelFrame');
  if(frame){ try{ frame.src='about:blank'; }catch(_){} }
  const acts=$('appPanelActions');
  if(acts) acts.innerHTML='';
  const g=$('appPanelGroup'); if(g) g.textContent='';
  const st=$('appPanelStage'); if(st) st.classList.remove('loading');
  window.__appPanelPath='';
}
function openAppPanel(path, title, route){
  closeBrowser();
  closeTabMore();
  const layer=$('appPanelLayer');
  if(!layer) return;
  layer.classList.add('open');
  layer.setAttribute('aria-hidden','false');
  const p=path||(route&&route.path)||'/';
  window.__appPanelPath=p;
  if($('appPanelTitle')) $('appPanelTitle').textContent=title||(route&&route.title)||'POCKET';
  if($('appPanelPath')) $('appPanelPath').textContent=p;
  if($('appPanelGroup')) $('appPanelGroup').textContent=(route&&route.group)||'';
  _renderAppPanelActions(route||null);
  const stage=$('appPanelStage');
  if(stage) stage.classList.add('loading');
  const frame=$('appPanelFrame');
  if(frame){
    const src=String(p).startsWith('http')?p:(location.origin+(String(p).startsWith('/')?p:('/'+p)));
    const clearLoad=function(){ if(stage) stage.classList.remove('loading'); };
    try{ frame.onload=clearLoad; frame.onerror=clearLoad; }catch(_){}
    try{ frame.src=src; }catch(_){ frame.src=p; clearLoad(); }
    setTimeout(clearLoad, 4000);
  }
}
function appPanelReload(){
  const frame=$('appPanelFrame');
  if(!frame) return;
  const stage=$('appPanelStage');
  if(stage) stage.classList.add('loading');
  try{ frame.src=frame.src; }catch(_){}
  setTimeout(function(){ if(stage) stage.classList.remove('loading'); }, 2500);
}
function appPanelOpenExternal(){
  const p=window.__appPanelPath||($('appPanelPath')&&$('appPanelPath').textContent)||'/';
  const url=String(p).startsWith('http')?p:(location.origin+(String(p).startsWith('/')?p:('/'+p)));
  try{ window.open(url,'_blank','noopener'); }catch(_){ location.href=url; }
}
function showAppTab(tab){
  tab=String(tab||'desk').toLowerCase().replace(/-/g,'_');
  closeTabMore();
  // Desk home: close overlays, keep habitat floor available
  if(tab==='desk' || tab==='chat' || tab==='home'){
    closeAppPanel();
    closeBrowser();
    _markAppTabs('desk');
    try{ closeDrawers(); }catch(_){}
    try{ focusChat(); }catch(_){}
    return;
  }
  if(tab==='habitat'){
    closeAppPanel();
    closeBrowser();
    if(document.body.classList.contains('habitat-open') && _activeAppTab==='habitat'){
      toggleHabitat(false);
      _markAppTabs('desk');
      return;
    }
    toggleHabitat(true);
    _markAppTabs('habitat');
    try{ refreshSessions(); }catch(_){}
    return;
  }
  if(tab==='screen'){
    closeAppPanel();
    closeBrowser();
    if(document.body.classList.contains('screen-col-open') && _activeAppTab==='screen'){
      toggleScreenCol(false);
      _markAppTabs('desk');
      return;
    }
    toggleScreenCol(true);
    _markAppTabs('screen');
    try{ refreshScreenCol(true); }catch(_){}
    return;
  }
  if(tab==='workspace' || tab==='system' || tab==='rail'){
    closeAppPanel();
    if(document.body.classList.contains('rail-open') && _activeAppTab==='workspace'){
      toggleWorkspacePanel(false);
      _markAppTabs('desk');
      return;
    }
    toggleWorkspacePanel(true);
    _markAppTabs('workspace');
    try{ refreshPlatformRail(); refreshIotRail(); }catch(_){}
    return;
  }
  if(tab==='browser'){
    closeAppPanel();
    openBrowser($('browserUrl')?$('browserUrl').value:'/tour');
    _markAppTabs('browser');
    return;
  }
  if(tab==='remote' || tab==='remote_browser'){
    closeAppPanel();
    _markAppTabs('remote');
    runWorkflow('remote_loop');
    return;
  }
  if(tab==='platform' || tab==='sovereign'){
    const route=APP_TAB_ROUTES.platform;
    openAppPanel(route.path, route.title, route);
    _markAppTabs('platform');
    try{ refreshPlatformRail(); refreshIotRail(); }catch(_){}
    return;
  }
  if(tab==='voice' || tab==='aria'){
    closeAppPanel();
    closeBrowser();
    _markAppTabs('desk');
    try{ pickAgent('voice'); }catch(_){}
    toast('Aria seated');
    return;
  }
  if(tab==='working' || tab==='work_mode'){
    closeAppPanel();
    closeBrowser();
    _markAppTabs('working');
    try{ startWorkingMode(); }catch(_){}
    return;
  }
  const route=APP_TAB_ROUTES[tab];
  if(route){
    openAppPanel(route.path, route.title, route);
    _markAppTabs(tab);
    if(tab==='phone'){ try{ refreshIotRail(); }catch(_){} }
    else if(tab==='os' || tab==='platform'){ try{ refreshPlatformRail(); }catch(_){} }
    else if(tab==='lab'){ try{ /* lab self-loads */ }catch(_){} }
    return;
  }
  showAppTab('desk');
}

// Lab panel → desk (iframe postMessage): open tab / seat agent without merging UIs
window.addEventListener('message', (ev)=>{
  try{
    const d=ev&&ev.data;
    if(!d || d.pocket!=='lab') return;
    if(d.agent){ try{ pickAgent(d.agent); }catch(_){} }
    if(d.tab){ try{ showAppTab(d.tab); }catch(_){} }
  }catch(_){}
});

/** Real multi-tab workflows — tabs + columns + agents work as one product. */
async function runWorkflow(name){
  name=String(name||'').toLowerCase();
  try{
    if(name==='ship_loop'){
      // Habitat + Screen eyes + Codex for ship work
      closeAppPanel(); closeBrowser();
      toggleHabitat(true);
      toggleScreenCol(true);
      try{ await setScreenMode('view'); }catch(_){}
      _markAppTabs('desk');
      try{ pickAgent('build'); }catch(_){ try{ pickAgent('codex'); }catch(__){} }
      toast('Ship loop — Habitat · Screen View · Build/Codex');
      try{ refreshPlatformRail(); }catch(_){}
      return;
    }
    if(name==='voice_loop'){
      closeAppPanel();
      toggleHabitat(true);
      _markAppTabs('desk');
      try{ pickAgent('voice'); }catch(_){}
      // Pre-warm fusion
      try{
        await api('/v1/fusion/voice',{method:'POST',body:JSON.stringify({text:'voice studio ready',stress:0.3,session_id:'desk-voice'})});
      }catch(_){}
      toast('Voice + Fusion — Aria seated · open Voice Studio tab for canvas');
      return;
    }
    if(name==='remote_loop'){
      closeAppPanel();
      toggleScreenCol(true);
      try{ await setScreenMode('view'); }catch(_){}
      try{ await api('/v1/remote-browser/open',{method:'POST',body:JSON.stringify({url:'https://example.com'})}); }catch(e){ toast(e.message||'remote open','err'); }
      try{
        const s=await api('/v1/remote-browser/sense',{method:'POST',body:JSON.stringify({})});
        const dens=s.symbol_density|| (s.perception&&s.perception.counts&&s.perception.counts.symbols) || 0;
        toast('Remote browser — Edge + Fusion sense · density '+dens);
      }catch(_){ toast('Remote browser — Edge opened · Screen View'); }
      openBrowser('/tour');
      _markAppTabs('remote');
      try{ refreshScreenCol(true); }catch(_){}
      return;
    }
    if(name==='phone_iot'){
      try{ await api('/v1/iot/devices',{method:'POST',body:JSON.stringify({seed:true})}); }catch(_){}
      try{
        const p=await api('/v1/node/pair',{method:'POST',body:JSON.stringify({label:'phone'})});
        if(p&&p.code){
          toast('Pair code '+p.code+' · open Phone tab · enter code');
          try{ await navigator.clipboard.writeText(String(p.code)); }catch(_){}
        }
      }catch(e){ toast(e.message||'pair'); }
      openAppPanel('/phone', 'Phone · IoT', APP_TAB_ROUTES.phone);
      _markAppTabs('phone');
      try{ refreshIotRail(); }catch(_){}
      return;
    }
    if(name==='studio_loop'){
      // First-class Product Studio: Screen View + Studio agent + open /studio
      closeBrowser();
      toggleHabitat(true);
      toggleScreenCol(true);
      try{ await setScreenMode('view'); }catch(_){}
      try{ pickAgent('studio'); }catch(_){ try{ pickAgent('build'); }catch(__){} }
      openAppPanel('/studio', 'Product Studio', APP_TAB_ROUTES.studio);
      _markAppTabs('studio');
      try{
        const st=await api('/v1/studio/first-class');
        const rec=(st.status&&st.status.video&&st.status.video.recordings)||0;
        const ff=st.status&&st.status.ready;
        toast('Studio first-class · '+(ff?'ffmpeg ready':'need ffmpeg')+' · '+rec+' recordings · agent seated');
      }catch(_){ toast('Studio loop — Product Studio open · seat Studio agent'); }
      return;
    }
    toast('Unknown workflow');
  }catch(e){ toast(e.message||String(e),'err'); }
}

async function runStudioViral(){
  try{
    toast('Polishing latest recording…');
    const j=await api('/v1/studio/auto',{method:'POST',body:JSON.stringify({title:'POCKET',subtitle:'Host co-pilot',cta:'ItsNotAI Labs'})});
    toast(j.message||('Viral pack '+(j.count||0)+'/'+(j.total||0)));
    try{ showAppTab('studio'); }catch(_){}
  }catch(e){ toast(e.message||'viral failed','err'); }
}
async function runStudioShip(){
  try{
    toast('Studio ship — viral + caption…');
    const j=await api('/v1/studio/ship',{method:'POST',body:JSON.stringify({title:'POCKET',subtitle:'Host co-pilot',cta:'ItsNotAI Labs',prompt:'Ship demo pack'})});
    toast(j.message||('Shipped '+(j.exports||[]).length+' exports'));
    try{ showAppTab('studio'); }catch(_){}
    try{ pickAgent('studio'); }catch(_){}
  }catch(e){ toast(e.message||'ship failed','err'); }
}
async function runCapsuleAllocate(){
  try{
    toast('Allocating capsule…');
    const j=await api('/v1/capsule/allocate',{method:'POST',body:JSON.stringify({tier:'512MB',enableWebGPU:true,runtime:'HostWorker',label:'desk-lab'})});
    const id=j.capsule&&j.capsule.id;
    toast(j.message||('Capsule '+(id||'ready')));
    try{ showAppTab('lab'); }catch(_){}
  }catch(e){ toast(e.message||'capsule failed','err'); }
}
async function runStudioStoryboard(){
  try{
    const j=await api('/v1/studio/storyboard',{method:'POST',body:JSON.stringify({prompt:'POCKET host co-pilot demo for X'})});
    const beats=(j.beats||[]).map(b=>b.name).join(' → ');
    toast(j.message||('Storyboard: '+beats));
    try{
      if(typeof setComposer==='function'){
        setComposer('Studio storyboard:\n'+(j.beats||[]).map(b=>b.beat+'. '+b.name+': '+b.caption).join('\n')+'\n\nNext: '+ (j.next||'studio_viral'));
      }
    }catch(_){}
    try{ pickAgent('studio'); }catch(_){}
  }catch(e){ toast(e.message||'storyboard failed','err'); }
}

async function remoteBrowserOpenQuick(){
  const u=prompt('URL for our remote browser (signed-in Edge)','https://');
  if(u==null||!String(u).trim()) return;
  try{
    await api('/v1/remote-browser/open',{method:'POST',body:JSON.stringify({url:String(u).trim()})});
    toggleScreenCol(true);
    try{ await setScreenMode('view'); }catch(_){}
    toast('Opened in host Edge · Screen View on');
    openBrowser(String(u).trim());
  }catch(e){ toast(e.message||'open failed','err'); }
}

async function refreshPlatformRail(){
  const el=$('platformStatus');
  const det=$('platformRailDetail');
  if(!el&&!det) return;
  try{
    const j=await api('/v1/sovereign');
    const clouds=(j.computing_clouds&&j.computing_clouds.clouds)||[];
    const rb=j.remote_browser||{};
    const iot=j.iot_home||{};
    const pub=(j.remote&&j.remote.public_url)||'';
    if(el) el.textContent=(clouds.length||0)+' clouds · remote '+(rb.mode||'?')+' · IoT '+(iot.device_count||0)+' · '+(pub? 'tunnel' : 'local');
    if(det){
      det.innerHTML=clouds.slice(0,6).map(c=>
        '<div><b style="color:var(--fg)">'+(c.name||c.id)+'</b> · '+(c.status||'')+'</div>'
      ).join('')+(pub?('<div style="margin-top:4px">Remote '+esc(pub)+'</div>'):'');
    }
  }catch(_){
    if(el) el.textContent='Sign in for sovereign stack status';
  }
}
async function refreshIotRail(){
  const box=$('iotRailList');
  const lan=$('iotLanUrl');
  if(!box&&!lan) return;
  try{
    const j=await api('/v1/iot');
    const devs=j.devices||[];
    const phone=(j.phone||{});
    if(lan){
      if(phone.phone_lan){
        lan.innerHTML='Phone Wi‑Fi: <a href="'+esc(phone.phone_lan)+'" target="_blank" rel="noopener" style="color:#6ee7b7">'+esc(phone.phone_lan)+'</a>'+
          (j.subnet?(' · '+esc(j.subnet)):'')+
          ' · <button type="button" class="icon" style="border:1px solid var(--line);padding:1px 6px;margin-left:4px" onclick="iotDiscoverLan()">Scan</button>'+
          ' <button type="button" class="icon" style="border:1px solid var(--line);padding:1px 6px" onclick="iotCopyLan()">Copy</button>';
        window.__pocketPhoneLan=phone.phone_lan;
      } else {
        lan.textContent=j.host_ip?('Host LAN '+j.host_ip+' · Scan Wi‑Fi'):'';
      }
    }
    if(box){
      if(!devs.length){
        box.innerHTML='<div style="line-height:1.45">No devices yet — <b style="color:var(--fg)">Scan Wi‑Fi</b> to find same-network hosts, or open Phone → Seed rooms.</div>';
      } else {
        box.innerHTML=devs.slice(0,10).map(d=>{
          const st=String(d.state|| (d.reachable?'online':'?')).toLowerCase();
          const on=st==='on'||st==='online';
          const id=esc(d.id||'');
          const canTog=d.kind!=='desk'&&d.kind!=='router'&&d.kind!=='phone';
          return '<div style="display:flex;align-items:center;gap:6px;padding:5px 0;border-bottom:1px solid var(--line)">'+
            '<span style="flex:1;min-width:0"><b style="color:var(--fg)">'+esc(d.name||'?')+'</b>'+
            '<span style="color:var(--muted)"> · '+esc(d.kind||'')+(d.address?' · '+esc(d.address):'')+'</span></span>'+
            '<span style="font-size:10px;color:'+(on?'#6ee7b7':'var(--muted)')+'">'+esc(st)+'</span>'+
            (canTog?'<button type="button" class="icon" data-iot-tog="'+id+'" style="border:1px solid rgba(16,163,127,.35);color:#6ee7b7;padding:2px 7px;font-size:10px">Toggle</button>':'')+
            '</div>';
        }).join('');
        box.querySelectorAll('[data-iot-tog]').forEach(btn=>{
          btn.onclick=async(ev)=>{
            ev.stopPropagation();
            try{
              await api('/v1/iot/control',{method:'POST',body:JSON.stringify({id:btn.getAttribute('data-iot-tog'),action:'toggle'})});
              toast('Toggled','ok');
              refreshIotRail();
            }catch(e){ toast(e.message||'control failed','err'); }
          };
        });
      }
    }
  }catch(_){ if(box) box.textContent=''; }
}
async function iotCopyLan(){
  const u=window.__pocketPhoneLan||'';
  if(!u) return toast('No LAN URL yet — Scan Wi‑Fi');
  try{ await navigator.clipboard.writeText(u); toast('Phone URL copied','ok'); }
  catch(_){ toast(u); }
}
async function iotDiscoverLan(){
  toast('Scanning same Wi‑Fi…');
  try{
    const j=await api('/v1/iot/discover',{method:'POST',body:JSON.stringify({deep:false})});
    toast('Found '+(j.found||0)+' · registry '+(j.registry_count||0),'ok');
    await refreshIotRail();
    await refreshNodes();
  }catch(e){ toast(e.message||'scan failed','err'); }
}
// One light auto-refresh of IoT when workspace opens
let _iotRailWarmed=false;
function warmIotRail(){
  if(_iotRailWarmed) return;
  _iotRailWarmed=true;
  try{ refreshIotRail(); }catch(_){}
}
function openBrowser(url){
  const layer=$('browserLayer');
  if(!layer) return;
  layer.classList.add('open');
  layer.setAttribute('aria-hidden','false');
  document.body.classList.add('browser-open');
  const raw=url!=null?String(url):($('browserUrl').value||'/tour');
  $('browserUrl').value=raw.startsWith('http')||raw.startsWith('/')?raw:('https://'+raw);
  browserGo();
  setTimeout(()=>{ try{ $('browserUrl').focus(); }catch(_){} }, 80);
}
function closeBrowser(){
  const layer=$('browserLayer');
  if(!layer) return;
  layer.classList.remove('open');
  layer.setAttribute('aria-hidden','true');
  document.body.classList.remove('browser-open');
  const frame=$('browserFrame');
  if(frame){
    try{ frame.src='about:blank'; }catch(_){}
  }
  const blk=$('browserBlocked');
  if(blk) blk.classList.remove('show');
}
function normalizeBrowserUrl(raw){
  let u=String(raw||'').trim();
  if(!u) return location.origin+'/tour';
  if(u.startsWith('/')) return location.origin+u;
  if(!/^https?:\/\//i.test(u)) u='https://'+u;
  return u;
}
function browserIsSameOrigin(u){
  try{ return new URL(u, location.href).origin===location.origin; }catch(_){ return false; }
}
function browserQuick(pathOrUrl){
  $('browserUrl').value=pathOrUrl;
  browserGo();
}
/** Load in the in-app browser pane — desk stays mounted; ← Desk always visible. */
function browserGo(){
  const u=normalizeBrowserUrl($('browserUrl').value);
  $('browserUrl').value=u;
  try{ sessionStorage.setItem('pocket_browser_last', u); }catch(_){}
  const frame=$('browserFrame');
  const blk=$('browserBlocked');
  if(blk) blk.classList.remove('show');
  if(!frame) return;
  // Same-origin product pages embed cleanly. External may hit X-Frame-Options.
  frame.onload=function(){
    if(blk) blk.classList.remove('show');
    // If same-origin and empty body, treat as fail
    try{
      const doc=frame.contentDocument;
      if(doc && doc.location && doc.location.href==='about:blank') return;
    }catch(_){ /* cross-origin loaded — ok */ }
  };
  frame.onerror=function(){ if(blk) blk.classList.add('show'); };
  try{
    frame.src=u;
  }catch(e){
    if(blk) blk.classList.add('show');
  }
  // Many external sites refuse iframe after a blank paint — offer new tab, keep chrome
  if(!browserIsSameOrigin(u)){
    setTimeout(()=>{
      try{
        // still open — user may see content; if blocked, browser shows empty; nudge gently
        const blk2=$('browserBlocked');
        // Don't force blocked UI for all external; only if we detect nothing after load
      }catch(_){}
    }, 2500);
  }
}
function browserHistBack(){
  try{ $('browserFrame').contentWindow.history.back(); }catch(_){ toast('Page back works on in-pane pages'); }
}
function browserHistFwd(){
  try{ $('browserFrame').contentWindow.history.forward(); }catch(_){ toast('Page forward works on in-pane pages'); }
}
function browserReload(){
  try{ $('browserFrame').contentWindow.location.reload(); }catch(_){ browserGo(); }
}
/** Optional: leave the pane and open a real Edge tab */
function browserOpenNewTab(){
  const u=normalizeBrowserUrl($('browserUrl').value);
  window.open(u,'_blank','noopener');
  toast('Opened in new tab — desk is still here');
}
function chip(name,on){ return `<span class="chip ${on?'on':'off'}">${name}</span>`; }

async function refreshOrganism(){
  try{
    const o=await api('/v1/organism');
    const h=o.heart||{}, b=o.brain||{};
    $('heartLabel').textContent=(h.bpm||'—')+' bpm';
    $('thought').textContent=b.thought||o.motto||'';
  }catch(_){}
}
async function refreshStack(){
  try{
    const j=await api('/v1/stack');
    const nx=j.nexus||{}, me=j.mesie||{}, mh=j.mesh||{};
    const set=(id,ok,label)=>{ const el=$(id); if(!el) return; el.textContent=label; el.className=ok?'on':'off'; };
    set('stPocket', true, 'live');
    set('stNexus', !!nx.ok, nx.ok?((nx.workers||[]).length+' workers'):'missing');
    set('stMesie', !!me.ok, me.ok?((me.engine_count||0)+' eng'):'missing');
    set('stMesh', !!mh.ok, mh.ok?((mh.agent_count||0)+' @ E:'):'off');
  }catch(_){
    ['stNexus','stMesie','stMesh'].forEach(id=>{ const el=$(id); if(el){ el.textContent='offline'; el.className='off'; }});
  }
  try{ refreshGithub(); }catch(_){}
}
async function refreshGithub(){
  try{
    const j=await api('/v1/github');
    const auth=$('ghAuth'), user=$('ghUser'), hint=$('ghHint');
    if(auth){
      auth.textContent=j.authenticated?'signed in':(j.gh?'not signed in':'gh missing');
      auth.style.color=j.authenticated?'#6ee7b7':(j.gh?'#fde047':'#fca5a5');
    }
    if(user) user.textContent=j.user?('@'+j.user):(j.gh?'—':'install gh');
    if(hint){
      hint.textContent=j.authenticated
        ? ('First-class · repos / issues / PRs via desk agent')
        : (j.gh?'Run gh auth login on this host once':'Install GitHub CLI (gh) on PATH');
    }
  }catch(_){
    const auth=$('ghAuth'); if(auth){ auth.textContent='offline'; auth.style.color='#fca5a5'; }
  }
  try{ refreshWorkSurface(); }catch(_){}
}
async function refreshWorkSurface(){
  try{
    const j=await api('/v1/work-surface');
    const n=(j.drafts&&j.drafts.count)||0;
    const el=$('draftCount'); if(el) el.textContent=String(n);
    const hint=$('surfaceHint');
    if(hint&&j.doctrine) hint.textContent=j.doctrine;
    const list=$('draftList');
    if(list){
      const items=(j.drafts&&j.drafts.drafts)||[];
      if(!items.length){ list.textContent='No drafts yet — agents can create HTML/sim previews before GitHub'; return; }
      list.innerHTML=items.slice(0,6).map(d=>
        '<div style="margin:0 0 5px"><b style="color:var(--fg)">'+(esc(d.title||d.id||'draft'))+'</b> · '+
        esc(d.kind||'')+' · '+esc(d.status||'draft')+
        (d.preview_url?(' · <a href="'+esc(d.preview_url)+'" target="_blank" style="color:var(--accent)">preview</a>'):'')+
        '</div>'
      ).join('');
    }
  }catch(_){
    const el=$('draftCount'); if(el) el.textContent='—';
  }
}
async function newHtmlDraft(){
  try{
    const title='Desk draft '+new Date().toLocaleTimeString();
    const html='<h1>Draft</h1><p>Edit me before promoting to a folder or GitHub.</p><button onclick="this.textContent=\'clicked\'">Click</button>';
    const j=await api('/v1/drafts',{method:'POST',body:JSON.stringify({title,kind:'html',content:html,layer:'preview',source:'desk'})});
    if(j.ok){
      toast('Draft created');
      refreshWorkSurface();
      const el=$('input');
      if(el && j.fence){
        el.value=(el.value?el.value+'\n\n':'')+j.fence;
        try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(_){}
      }
    }else toast(j.error||'draft failed','err');
  }catch(e){ toast(e.message||'draft failed','err'); }
}
async function refreshSessions(){
  try{
    const j=await api('/v1/sessions?limit=40');
    sessions=j.sessions||[];
    renderSessionList();
    // Do NOT full-repaint transcript on timer — that made the app blink.
    // Live session updates only go through scheduleSessPoll + signature check.
    if(activeId){
      try{
        const fresh=await api('/v1/sessions/'+activeId);
        const sig=transcriptSig(fresh);
        if(sig!==_lastTranscriptSig){
          _lastTranscriptSig=sig;
          renderTranscript(fresh);
          updateLiveSummaryFromSession(fresh);
        }else{
          updateSessionControls(fresh);
        }
      }catch(_){}
    }
  }catch(e){
    const box=$('slist');
    if(box) box.innerHTML='<div class="hint">Sessions need sign-in. Use the login panel, then click NEXUS / MESIE / Codex above.</div>';
  }
}
function renderSessionList(){
  const box=$('slist'); if(!box) return; box.innerHTML='';
  if(!sessions.length){ box.innerHTML='<div class="hint">No sessions yet. Start <b>NEXUS</b>, <b>MESIE</b>, Codex, or Term — they show here.</div>'; return; }
  sessions.forEach(s=>{
    const d=document.createElement('div');
    d.className='sitem'+(s.id===activeId?' on':'');
    const last=(s.messages&&s.messages.length)?s.messages[s.messages.length-1]:null;
    const preview=last?((last.text||last.result||'').slice(0,42)):(s.mode);
    const thr=s.engine_thread_id||s.codex_session_id||'';
    const thrHint=thr?(s.mode==='codex'?' · thread '+(thr.slice(0,8)+'…'):' · bound'):' · new thread';
    const resumeN=s.engine_resumes?(' · r'+s.engine_resumes):'';
    const modeLabel=s.mode==='codex'?'Codex':(s.mode==='grok'?'Grok':(s.mode||'session'));
    const ve=s.voice_engine||VOICE_MODES.has(String(s.mode||'').toLowerCase())?' · 🎙':'';
    d.innerHTML=`<div class="dot" style="background:${s.color||MODE_COLOR[s.mode]||'#22c55e'}"></div>
      <div style="min-width:0;flex:1"><b>${esc(s.title||modeLabel)}</b><div class="meta">${esc(modeLabel)}${ve} · ${esc(s.status||'idle')}${thrHint}${resumeN} · ${esc(preview)}</div></div>
      <button type="button" class="x" title="Close" data-close="1">×</button>`;
    d.onclick=e=>{
      e.preventDefault(); e.stopPropagation();
      if(e.target && (e.target.classList.contains('x')||e.target.getAttribute('data-close'))){ closeSess(s.id); return; }
      selectSess(s.id);
    };
    box.appendChild(d);
  });
}
async function newSess(mode){
  try{
    hideGate();
    const ws=($('wsSelect')&&$('wsSelect').value)||'workspace';
    const j=await api('/v1/sessions',{method:'POST',body:JSON.stringify({mode, workspace:ws, device:DEVICE})});
    if(!j||!j.id){ toast('Session not created — sign in again?','err'); showGate(); return; }
    await refreshSessions();
    await selectSess(j.id);
    setAgentPickUI(mode);
    if(DEVICE.kind==='phone') closeDrawers();
    toast((agentMeta(mode).name||mode)+' session ready');
  }catch(e){
    const msg=String(e.message||e);
    toast('Could not start session: '+msg,'err');
    if(/auth|401|sign in|unauthorized/i.test(msg)) showGate();
  }
}
/** Activate Grok/Codex Novae hands in platform workspace (not founder personal disk for market). */
async function activateNovae(id){
  try{
    const n=await api('/v1/novae/activate',{method:'POST',body:JSON.stringify({id, goal:'desk activate', host_power:true})});
    if(!n.ok && n.error) throw new Error(n.error);
    toast((n.title||id)+' · hands active');
    if(n.session_id){
      await refreshSessions();
      await selectSess(n.session_id);
    } else if(n.mode){
      await newSess(n.mode);
    }
    if(DEVICE.kind==='phone') closeDrawers();
    try{ pollSubagents(); }catch(_){}
  }catch(e){ toast('Novae: '+(e.message||e),'err'); }
}
async function closeSess(id){
  try{
    // Stop running Grok/Codex jobs before deleting the tab
    try{ await api('/v1/sessions/'+id+'/stop',{method:'POST',body:JSON.stringify({reason:'session closed'})}); }catch(_){}
    await api('/v1/sessions/'+id,{method:'DELETE'});
    if(activeId===id){ activeId=null; showEmpty(); }
    refreshSessions();
  }catch(e){ toast('Close failed'); }
}
async function stopActiveSession(){
  if(!activeId) return;
  try{
    const r=await api('/v1/sessions/'+activeId+'/stop',{method:'POST',body:JSON.stringify({reason:'stopped by user'})});
    const n=(r.cancelled_jobs||[]).length;
    toast(n?('Stopped '+n+' job'+(n===1?'':'s')):'Nothing running');
    await selectSess(activeId);
    refreshSessions();
  }catch(e){ toast('Stop failed: '+e.message,'err'); }
}
async function endActiveSession(){
  if(!activeId) return;
  const id=activeId;
  await closeSess(id);
  toast('Session ended');
}
function updateSessionControls(s){
  const stop=$('btnStop'), end=$('btnEnd'), ve=$('btnVoiceEngine');
  if(!s||!activeId){
    if(stop) stop.style.display='none';
    if(end) end.style.display='none';
    if(ve) ve.style.display='none';
    return;
  }
  if(end) end.style.display='inline-flex';
  if(ve){
    ve.style.display='inline-flex';
    const native=VOICE_MODES.has(String(s.mode||'').toLowerCase());
    paintVoiceEngineBtn(!!s.voice_engine || native);
  }
  const running=(s.messages||[]).some(m=>m.status==='running'||m.status==='queued') || s.status==='running';
  if(stop){
    stop.style.display=running?'inline-flex':'none';
    stop.classList.toggle('hot', !!running);
  }
}
let _lastTranscriptSig='';
let _sessPollMs=1200;
function transcriptSig(s){
  const msgs=s.messages||[];
  return msgs.map(m=>{
    const body=String(m.result||m.error||m.stream_preview||'');
    return [m.id||'',m.status||'',m.stream_tokens||0,body.length,body.slice(-80)].join('|');
  }).join(';')+'#'+((s.terminal&&s.terminal.log_tail)||'').length+'#'+(s.status||'');
}
function scheduleSessPoll(id){
  if(pollTimer) clearInterval(pollTimer);
  const tick=async()=>{
    if(activeId!==id) return;
    try{
      const fresh=await api('/v1/sessions/'+id);
      window.__activeSessCache=fresh;
      try{
        const ix=(sessions||[]).findIndex(x=>x&&x.id===id);
        if(ix>=0) sessions[ix].voice_engine=!!fresh.voice_engine;
      }catch(_){}
      const running=(fresh.messages||[]).some(m=>m.status==='running'||m.status==='queued')||fresh.status==='running';
      // Adaptive poll: snappy while working, calm when idle (cuts desk latency)
      const want=running?550:2800;
      if(want!==_sessPollMs){
        _sessPollMs=want;
        if(pollTimer) clearInterval(pollTimer);
        pollTimer=setInterval(tick,_sessPollMs);
      }
      const sig=transcriptSig(fresh);
      if(sig!==_lastTranscriptSig){
        _lastTranscriptSig=sig;
        renderTranscript(fresh);
        updateLiveSummaryFromSession(fresh);
      } else {
        updateSessionControls(fresh);
      }
      let stok=0;
      (fresh.messages||[]).forEach(m=>{ if(m.status==='running') stok+=(m.stream_tokens||0); });
      const us=$('uStream'); if(us) us.textContent=stok.toLocaleString();
    }catch(_){}
  };
  _sessPollMs=900;
  pollTimer=setInterval(tick,_sessPollMs);
}
async function selectSess(id){
  activeId=id;
  if(pollTimer) clearInterval(pollTimer);
  _lastTranscriptSig='';
  try{
    const s=await api('/v1/sessions/'+id);
    window.__activeSessCache=s;
    _activeSessionMode=String((s&&s.mode)||'').toLowerCase();
    // Leaving voice-enabled sessions: stop TTS so other chats stay quiet
    if(!VOICE_MODES.has(_activeSessionMode) && !s.voice_engine){
      try{ if(window.speechSynthesis) window.speechSynthesis.cancel(); }catch(_){}
    }
    // keep sessions[] in sync for voice_engine flag
    try{
      const ix=(sessions||[]).findIndex(x=>x&&x.id===id);
      if(ix>=0) sessions[ix]=Object.assign({}, sessions[ix], {voice_engine:!!s.voice_engine, title:s.title||sessions[ix].title});
    }catch(_){}
    renderSessionList();
    _lastTranscriptSig=transcriptSig(s);
    renderTranscript(s);
    $('input').disabled=false; $('sendBtn').disabled=false; $('micBtn').disabled=false; $('input').focus();
    setPresets(s.mode);
    setAgentPickUI(s.mode);
    updateMicChrome(s.mode);
    updateSessionControls(s);
    updateLiveSummaryFromSession(s);
    scheduleSessPoll(id);
  }catch(e){ toast('Open session failed'); }
}
/** Real human-readable summary from chat turns (not raw log tails). */
function summarizeMessages(messages){
  const msgs=(messages||[]).filter(m=>m && (m.role==='user'||m.role==='assistant'||m.role==='agent'||!m.role));
  if(!msgs.length) return '';
  const users=[], agents=[];
  msgs.forEach(m=>{
    const role=String(m.role||'').toLowerCase();
    let t=String(m.content||m.text||m.result||'').replace(/\s+/g,' ').trim();
    if(!t) return;
    // strip engine noise
    t=t.replace(/\[engine=[^\]]+\]/gi,'').replace(/\[cli=[^\]]+\]/gi,'').replace(/\[stream_tokens[^\]]*\]/gi,'').trim();
    if(t.length<8) return;
    if(role==='user'||m.from==='user') users.push(t.slice(0,180));
    else agents.push(t.slice(0,220));
  });
  const lastUser=users[users.length-1]||'';
  const lastAgent=agents[agents.length-1]||'';
  const lines=[];
  lines.push('Turns: '+msgs.length+(users.length?' · you asked '+users.length+' time(s)':''));
  if(lastUser) lines.push('Latest ask: '+lastUser);
  if(lastAgent) lines.push('Latest result: '+lastAgent);
  if(users.length>1) lines.push('Earlier: '+users.slice(0,-1).slice(-2).map(u=>'• '+u).join(' '));
  return lines.join('\n');
}
function updateLiveSummaryFromSession(s){
  const sum=$('aiSummary'); if(!sum||!s) return;
  const brief=summarizeMessages(s.messages||[]);
  if(brief){
    sum.textContent=brief;
    sum.dataset.had='1';
    const meta=$('aiSumMeta');
    if(meta) meta.textContent=(agentMeta(s.mode).name||s.mode)+' · live session summary';
  }
}
function showEmpty(){
  _activeSessionMode='';
  window.__activeSessCache=null;
  try{ if(window.speechSynthesis) window.speechSynthesis.cancel(); }catch(_){}
  $('mainTitle').textContent='Main desk';
  $('mainTag').textContent='home';
  $('mainWs').textContent='workspace';
  updateSessionControls(null);
  updateMicChrome('');
  setAgentPickUI('');
  $('input').disabled=true; $('sendBtn').disabled=true; $('micBtn').disabled=true;
  // Full main-desk home (agents + surfaces + loops) — not a thin stub
  $('transcript').innerHTML=`<div class="empty" id="emptyHome">
    <div class="mark">P</div>
    <h2>Main desk</h2>
    <p>Home base — seat an agent to chat and run tools. Other surfaces stay their own tabs.</p>
    <div class="empty-actions">
      <button type="button" data-mode="codex">Codex</button>
      <button type="button" data-mode="grok">Grok</button>
      <button type="button" data-mode="claude">Claude</button>
      <button type="button" data-mode="assist">Assist</button>
      <button type="button" data-mode="studio">Studio</button>
      <button type="button" data-mode="muse_spark">Muse</button>
      <button type="button" data-mode="voice">Aria</button>
      <button type="button" data-mode="build">Build</button>
      <button type="button" data-mode="plan">Plan</button>
      <button type="button" data-mode="auro">Auro</button>
    </div>
    <div class="empty-map" aria-label="Open a surface">
      <button type="button" data-tab="working"><b>Working</b></button>
      <button type="button" data-tab="habitat"><b>Habitat</b></button>
      <button type="button" data-tab="screen"><b>Screen</b></button>
      <button type="button" data-tab="studio"><b>Studio</b></button>
      <button type="button" data-tab="lab"><b>Lab</b></button>
      <button type="button" data-tab="phone"><b>Phone</b></button>
      <button type="button" data-tab="work"><b>Work Studio</b></button>
      <button type="button" data-tab="remote"><b>Remote</b></button>
      <button type="button" data-tab="platform"><b>Platform</b></button>
    </div>
    <div class="empty-actions" style="margin-top:14px">
      <button type="button" data-wf="studio_loop">Studio loop</button>
      <button type="button" data-wf="ship_loop">Ship loop</button>
      <button type="button" data-wf="voice_loop">Voice + Fusion</button>
      <button type="button" data-wf="phone_iot">Phone + IoT</button>
      <button type="button" data-tab="lab">Lab readiness</button>
    </div>
    <div id="deskReadyStrip" style="margin-top:16px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center;max-width:480px;margin-left:auto;margin-right:auto"></div>
  </div>`;
  $('transcript').querySelectorAll('[data-mode]').forEach(btn=>{
    btn.onclick=(ev)=>{ ev.preventDefault(); pickAgent(btn.getAttribute('data-mode')); };
  });
  $('transcript').querySelectorAll('[data-tab]').forEach(btn=>{
    btn.onclick=(ev)=>{ ev.preventDefault(); showAppTab(btn.getAttribute('data-tab')); };
  });
  $('transcript').querySelectorAll('[data-wf]').forEach(btn=>{
    btn.onclick=(ev)=>{ ev.preventDefault(); runWorkflow(btn.getAttribute('data-wf')); };
  });
  $('presets').innerHTML='';
  try{ refreshDeskReadyStrip(); }catch(_){}
}
async function refreshDeskReadyStrip(){
  const el=$('deskReadyStrip');
  if(!el) return;
  try{
    const j=await api('/v1/lab');
    const cards=j.cards||[];
    el.innerHTML=cards.map(c=>{
      const ok=!!c.ok;
      return `<span class="prod-pill ${ok?'on':'warn'}" title="${(c.blurb||'').replace(/"/g,'')}"><i></i>${c.name||c.id}</span>`;
    }).join('') + (j.all_first_class?`<span class="prod-pill on"><i></i>Desk ready</span>`:`<span class="prod-pill warn"><i></i>${j.ready||0}/${j.total||0}</span>`);
  }catch(_){
    el.innerHTML='<span class="prod-pill warn"><i></i>Host…</span>';
  }
}
function emptyHint(mode){
  const m={
    desktop:'Ask to open an app or a website on this PC.',
    web:'Ask to search the web or open a link.',
    nexus:'Ask for advanced tools available on this host.',
    term:'Integrated PowerShell console for agents (hidden process — log below). Type commands or use the console panel.',
    shell:'Run a one-off shell command (admin).',
    python:'Host Python CLI — interactive REPL integrated for agents. Type Python lines here.',
    python_wsl:'python3 inside WSL (Debian) — integrated for agents. Linux packages live here.',
    plan:'Describe the goal — you get a plan, not file changes yet.',
    voice:'Meet Aria — your patient voice persona. Talk and she answers out loud (other agents stay text).',
    v2v:'Aria voice session — specialized duplex agent only.',
    voice_agent:'Aria voice session — specialized duplex agent only.',
    voice2voice:'Aria voice session — specialized duplex agent only.',
    muse_spark:'Muse Spark — multimodal reasoning with parallel research lanes. Say open meta for meta.ai. Activate Voice engine to talk.',
    muse:'Muse Spark — same as Muse Spark.',
    spark:'Muse Spark — same as Muse Spark.',
    assist:'Digital assistant — research, plans, drafts, buy/reserve, screen. Or open Work Studio tab for the full life surface.',
    assistant:'Digital assistant — same as assist.',
    auro:'Auro14B — local meaning model + native LMR. Prefix native for full checkpoint. Open /auro/ for browser model.',
    auro14b:'Auro14B — same as Auro.',
    vision:'OCULUS vision — observe the screen, UI map, OCR, click-by-name. First-class sensory layer.',
    oculus:'OCULUS vision agent — same as Vision.',
    see:'OCULUS vision agent — same as Vision.',
    github:'GitHub first-class — status, repos, issues, PRs, clone, create (signed-in gh on this host).',
    gh:'GitHub first-class — same as GitHub agent.',
    repos:'List, open, analyze, or create repos (GitHub + local workspaces).',
    work:'Working state — not coding. Say real work: buy X, analyze Y, reserve Z. Multi-part OK. Lives on the Working board table with tools.',
    working:'Working state — operational board (buy · research · reservations · analysis). Not a chat agent.',
    live_work:'Working state — same as Working.',
    mcp:'10 embedded MCPs (3 internal + 7 external). Agents use CLIs — not user browser tabs.',
    coding_swarm:'Multi-agent coding harness (Sophia · Solver · Twin). Each turn writes pixel artifacts — look/recreate/pass in Workspace.',
    genetic:'Genetic flow — internal models (ghost·world·auro·guppy·heuristic·identity) evolve which modules run for your goal. Try: hash the plan and next steps.',
    genetic_flow:'Same as Genetic — evolve internal model modules.',
    internal:'Same as Genetic — internal models as modules.',
    internal_models:'Same as Genetic — internal models as modules.',
    pixel_swarm:'Same as Coding Swarm — artifacts land in pixel memory.',
    harness:'Coding Swarm harness — @sophia @solver @twin routing.',
    swarm_code:'Coding Swarm harness.',
    code_swarm:'Coding Swarm harness.',
    swarm:'Coding task → multi-agent swarm + pixels. Or type status/pulse for always-on daemon.',
    claude:'Claude Agent SDK loop — tools stream live into this chat with compact code cards.',
    grok:'Describe what you need. New messages take priority; use Stop or End in the header if needed.',
    codex:'Describe the coding task. New messages take priority; use Stop or End if needed.',
    wsl:'Linux workspace on this PC. Ask for a status check or a command.',
    wsl_native:'Linux workspace on this PC. Ask for a status check or a command.',
    linux:'Linux workspace on this PC.',
    build:'Describe the product to build. POCKET plans, implements, tests, and ships in steps.',
    ship:'Describe what to ship — same multi-step build flow.',
    use_case:'Pick a playbook (list) or describe the outcome you want.',
    emergent:'Run a playbook or describe a full delivery.',
    custom_agent:'Create a custom agent or run one you already made.',
    wiki:'Ask about a file path, symbol, or search across the codebase.',
    infinite_wiki:'Explore the codebase without dumping whole files.',
    codebase:'Explore the codebase without dumping whole files.',
    agent:'Give a short multi-step task.',
    doer:'Give a short multi-step task to run quietly.',
    guppy:'Local helper — ask for lookups or simple actions.',
    browser:'Research and draft with the browser.',
    capture:'Ask for a screenshot.',
    repos:'List or open repositories.',
    copilot:'Open Windows Copilot or related tools.',
    archon:'Coordinate helpers on a larger task.',
    alpha:'Coordinate helpers on a larger task.',
    workers:'List available helpers.',
    handoff:'Create a plan package to hand off.'
  };
  return m[mode]||'Describe what you need in plain language.';
}
function workedSeconds(m){
  const start=Number(m.at||0), end=Number(m.finished_at||m.stream_updated_at||0);
  if(start&&end&&end>=start) return Math.max(1, Math.round(end-start));
  if(start&&(m.status==='running'||m.status==='queued')) return Math.max(1, Math.round(Date.now()/1000 - start));
  return 0;
}
/** Parse explicit @NAME mentions (ARCHON, DESIGN, FORGE_HEADLESS, …). */
function parseMentions(text){
  const found=[];
  const re=/@([A-Za-z][A-Za-z0-9_]*)/g;
  let m;
  while((m=re.exec(String(text||'')))){
    const name=String(m[1]||'').toUpperCase();
    if(!name||found.includes(name)) continue;
    // Latin, mesh/headless, aliases, or any named agent ≥2 chars
    if(LATIN_WORKERS.includes(name) || MESH_AGENTS.includes(name) || MENTION_ALIASES.includes(name) || name.length>=2){
      found.push(name);
    }
  }
  return found;
}
function hasAtMention(text){
  return /@[A-Za-z]/.test(String(text||''));
}
function mentionWorkers(text){
  const raw=String(text||'');
  const upper=raw.toUpperCase();
  const fromAt=parseMentions(raw);
  const bare=LATIN_WORKERS.concat(MESH_AGENTS).filter(w=>new RegExp('\\b'+w+'\\b').test(upper));
  return Array.from(new Set(fromAt.concat(bare)));
}
/** Summarize dispatch API payload into a short human line (no raw dumps). */
function summarizeDispatchResult(j, name){
  if(!j||typeof j!=='object') return '';
  const mentions=j.mentions||[];
  const n=j.dispatched!=null?j.dispatched:1;
  if(j.ok===false){
    const err=(j.error||j.message||'').toString().slice(0,120);
    return err||'failed';
  }
  // Prefer nested run summary without dumping full objects
  let note='';
  try{
    const results=j.results||[];
    const mine=results.find(r=>String(r.agent||'').toUpperCase()===String(name||'').toUpperCase())||results[0];
    const run=mine&&mine.run;
    if(run&&typeof run==='object'){
      if(typeof run.message==='string'&&run.message.trim()) note=run.message.trim().slice(0,140);
      else if(typeof run.brief==='string') note=run.brief.trim().slice(0,140);
      else if(run.ok!=null) note=run.ok?'ok':'failed';
    }
  }catch(_){}
  if(!note && mentions.length) note='mesh · '+n+' agent'+(n===1?'':'s');
  return note;
}
/** Append a clean dispatch card into the chat transcript (not JSON dumps). */
function showDispatchInline(dispatched, message){
  const box=$('transcript');
  if(!box) return;
  // Clear empty state
  const empty=box.querySelector('.empty');
  if(empty) box.innerHTML='';
  const ok=dispatched.filter(d=>d.ok);
  const fail=dispatched.filter(d=>!d.ok);
  const card=document.createElement('div');
  card.className='dispatch-card';
  const chips=dispatched.map(d=>{
    const tip=d.ok?(d.summary||'dispatched'):(d.error||'failed');
    return `<span class="dc-chip ${d.ok?'':'fail'}" title="${esc(tip)}">@${esc(d.name)}</span>`;
  }).join('');
  const note=ok.map(d=>d.summary).filter(Boolean).slice(0,2).join(' · ')
    || (message?String(message).slice(0,100):'');
  card.innerHTML=`<div class="dc-h"><span class="ok">${fail.length&&!ok.length?'DISPATCH':'DISPATCHED'}</span>
    <span>${ok.length} ok${fail.length?(' · '+fail.length+' failed'):''}</span></div>
    <div class="dc-agents">${chips}</div>
    ${note?`<div class="dc-note">${esc(note)}</div>`:''}`;
  box.appendChild(card);
  box.scrollTop=box.scrollHeight;
}
/** POST /v1/subagents/dispatch {name, message} for each @MENTION. Soft-fails if route missing. */
async function dispatchMentions(text){
  const names=parseMentions(text);
  if(!names.length) return {dispatched:[], endpointMissing:false};
  const message=String(text||'').replace(/@[A-Za-z][A-Za-z0-9_]*/g,' ').replace(/\s+/g,' ').trim()||text;
  const dispatched=[];
  let endpointMissing=false;
  for(const name of names){
    try{
      const r=await fetch('/v1/subagents/dispatch',{
        method:'POST',
        headers:authHeaders(),
        body:JSON.stringify({name, message})
      });
      if(r.status===404){
        endpointMissing=true;
        break;
      }
      const raw=await r.text();
      let j={};
      try{ j=raw?JSON.parse(raw):{}; }catch(_){ j={}; }
      if(r.ok){
        const summary=summarizeDispatchResult(j, name);
        dispatched.push({name, ok:true, summary});
        liveAgentHits[name]={t:Date.now(),message:(summary||message).slice(0,160),status:'running'};
        // Also mark canonical headless ids when short alias used
        if(name==='FORGE') liveAgentHits['FORGE_HEADLESS']=liveAgentHits[name];
        if(name==='SENTINEL') liveAgentHits['SENTINEL_HEADLESS']=liveAgentHits[name];
        if(name==='SHIP') liveAgentHits['SHIP_HEADLESS']=liveAgentHits[name];
        if(name==='RESEARCH') liveAgentHits['RESEARCH_HEADLESS']=liveAgentHits[name];
        if(name==='DESIGN'||name==='DESIGNER'||name==='UI') liveAgentHits['DESIGN']={t:Date.now(),message:(summary||message).slice(0,160),status:'running'};
        walkthroughSteps.push({
          agent:name,
          message:'Dispatched · '+(summary||message.slice(0,100)||'run'),
          kind:'dispatch',
          ts:new Date().toISOString().slice(11,19)
        });
      } else {
        let err=j.error||j.message||('HTTP '+r.status);
        if(typeof err!=='string') err='HTTP '+r.status;
        dispatched.push({name, ok:false, error:String(err).slice(0,160)});
      }
    }catch(e){
      dispatched.push({name, ok:false, error:String(e.message||e).slice(0,160)});
    }
  }
  if(dispatched.length){
    showDispatchInline(dispatched, message);
    const okNames=dispatched.filter(d=>d.ok).map(d=>d.name);
    if(okNames.length) toast('Dispatched @'+okNames.join(' @'), 'ok');
    else toast('Dispatch failed', 'err');
    renderWalkthrough(walkthroughSteps);
    try{ pollSubagents(); }catch(_){}
  }
  return {dispatched, endpointMissing, message};
}
function resolveSlash(text){
  const t=String(text||'').trim();
  if(!t.startsWith('/')) return t;
  const body=t.slice(1).trim();
  if(!body) return t;
  const sp=body.indexOf(' ');
  const cmd=(sp<0?body:body.slice(0,sp)).toLowerCase();
  const arg=(sp<0?'':body.slice(sp+1)).trim();
  if(cmd==='help'||cmd==='actions'){
    return 'Available actions: '+SLASH_ACTIONS.map(a=>'/'+a.cmd).join(' · ')+
      '\nLatin: '+LATIN_WORKERS.map(w=>'@'+w).join(' ')+
      '\nMesh: '+MESH_AGENTS.map(w=>'@'+w).join(' ');
  }
  const hit=SLASH_ACTIONS.find(a=>a.cmd===cmd);
  if(hit && hit.fill && hit.fill.startsWith('/')) return resolveSlash(hit.fill+(arg?' '+arg:''));
  if(hit) return (hit.fill+(arg?' '+arg:'')).trim();
  return t;
}
function closeComposerMenus(){
  const sm=$('slashMenu'); if(sm){ sm.classList.remove('open'); sm.innerHTML=''; }
  const mm=$('mentionMenu'); if(mm){ mm.classList.remove('open'); mm.innerHTML=''; }
}
function updateSlashMenu(){
  const el=$('slashMenu');
  const input=$('input');
  if(!el||!input) return;
  const v=String(input.value||'');
  // Prefer @mention menu when typing a mention token
  if(currentMentionQuery(v)!=null){ el.classList.remove('open'); el.innerHTML=''; return; }
  if(!v.startsWith('/') || v.includes('\n')){
    el.classList.remove('open'); el.innerHTML=''; return;
  }
  const q=v.slice(1).split(/\s/)[0].toLowerCase();
  const items=SLASH_ACTIONS.filter(a=>!q||a.cmd.startsWith(q)||a.label.toLowerCase().includes(q));
  if(!items.length){ el.classList.remove('open'); el.innerHTML=''; return; }
  el.innerHTML='';
  items.forEach(a=>{
    const b=document.createElement('button');
    b.type='button'; b.setAttribute('role','option');
    b.innerHTML=`<b>/${esc(a.cmd)}</b><span>${esc(a.label)}</span>`;
    b.onclick=()=>{ input.value=a.fill; el.classList.remove('open'); el.innerHTML=''; input.focus(); };
    el.appendChild(b);
  });
  el.classList.add('open');
}
/** Return partial mention token after last @ (or null if not in @-mode). */
function currentMentionQuery(v){
  const s=String(v||'');
  // Active when last @ has no space after it yet
  const m=s.match(/(^|[\s])@([A-Za-z0-9_]*)$/);
  if(!m) return null;
  return String(m[2]||'').toUpperCase();
}
function updateMentionMenu(){
  const el=$('mentionMenu');
  const input=$('input');
  if(!el||!input) return;
  const v=String(input.value||'');
  const q=currentMentionQuery(v);
  if(q==null){ el.classList.remove('open'); el.innerHTML=''; return; }
  // Hide slash while mentioning
  const sm=$('slashMenu'); if(sm){ sm.classList.remove('open'); sm.innerHTML=''; }
  const roster=mentionRoster();
  const items=roster.filter(n=>!q||n.startsWith(q)||n.includes(q)).slice(0,14);
  // Always surface DESIGN + headless near top when query empty / matching
  const priority=['DESIGN','FORGE_HEADLESS','SENTINEL_HEADLESS','RESEARCH_HEADLESS','SHIP_HEADLESS','ARCHON','OCULUS','SCRIPTOR'];
  items.sort((a,b)=>{
    const ia=priority.indexOf(a), ib=priority.indexOf(b);
    if(ia>=0||ib>=0) return (ia<0?99:ia)-(ib<0?99:ib);
    return a.localeCompare(b);
  });
  if(!items.length){ el.classList.remove('open'); el.innerHTML=''; return; }
  el.innerHTML='';
  items.forEach(n=>{
    const b=document.createElement('button');
    b.type='button'; b.setAttribute('role','option');
    const kind=mentionKind(n);
    b.innerHTML=`<span class="mdot ${kind}"></span><b>@${esc(n)}</b><span>${esc(mentionLabel(n))}</span>`;
    b.onclick=()=>{
      // Replace trailing @partial with full @NAME + space
      const cur=String(input.value||'');
      input.value=cur.replace(/@([A-Za-z0-9_]*)$/, '@'+n+' ');
      el.classList.remove('open'); el.innerHTML='';
      input.focus();
    };
    el.appendChild(b);
  });
  el.classList.add('open');
}
function inlineSubagentsFromMsg(m, mode){
  const names=new Set(mentionWorkers(m.text||'').concat(mentionWorkers(m.result||'')));
  (subagentState||[]).forEach(w=>{ if(w&&w.name) names.add(String(w.name).toUpperCase()); });
  Object.keys(liveAgentHits||{}).forEach(k=>{ if(liveAgentHits[k] && (Date.now()-liveAgentHits[k].t)<90000) names.add(k); });
  if(m.status==='running'||m.status==='queued'){
    const eng=String(m.engine||mode||'').toUpperCase();
    if(eng) names.add(eng);
  }
  return Array.from(names).map(n=>{
    const hit=liveAgentHits[n];
    const dyn=(subagentState||[]).find(w=>String(w.name||'').toUpperCase()===n);
    return {
      name:n,
      status: dyn?(dyn.status||'running'):(hit?(hit.status||'running'):((m.status==='running'||m.status==='queued')?'running':'done')),
      goal: dyn?(dyn.goal||''):(hit?(hit.message||''):''),
      steps: dyn?dyn.steps:undefined
    };
  });
}
function renderTranscript(s){
  if(!s) return;
  window.__activeSessCache=s;
  $('mainTitle').textContent=s.title||s.mode;
  const thr=s.engine_thread_id||s.codex_session_id||'';
  const thrTag=thr?(' · thread '+(String(thr).slice(0,8)+'…')):'';
  const anyRun=(s.messages||[]).some(m=>m.status==='running'||m.status==='queued');
  const veTag=(s.voice_engine||VOICE_MODES.has(String(s.mode||'').toLowerCase()))?' · 🎙 voice':'';
  $('mainTag').textContent=s.mode+(anyRun||s.status==='running'?' · running':'')+veTag+thrTag+(s.engine_resumes?(' · resumes '+s.engine_resumes):'');
  $('mainWs').textContent=s.workspace||'workspace';
  updateSessionControls(s);
  updateMicChrome(s.mode);
  const mp=$('modelPick');
  if(mp && !mp.dataset.userSet){ try{ mp.value=s.mode||''; }catch(_){} }
  const box=$('transcript');
  // Track mode for specialized agents (Voice ↔ Voice only when mode is voice*)
  const modeKey=String(s.mode||'').toLowerCase();
  _activeSessionMode=modeKey;
  const isWorkMode=WORK_MODES.has(modeKey);
  document.body.classList.toggle('work-mode-on', isWorkMode);
  if(isWorkMode){ try{ ensureWorkingBoardPanel(true); refreshWorkingBoard(); }catch(_){} }
  else { try{ ensureWorkingBoardPanel(false); }catch(_){} }
  const imsgModes=new Set(['plan','grok','claude','codex','build','web','custom_agent','ship','voice','v2v','voice_agent','voice2voice','muse_spark','muse','spark','coding_swarm','pixel_swarm','harness','swarm_code','code_swarm','swarm','genetic','genetic_flow','internal','internal_models']);
  // Voice panel: native Aria OR any agent with Voice engine activated
  const isVoiceMode=isVoiceSessionMode();
  box.classList.toggle('imsg', imsgModes.has(modeKey) || modeKey.includes('novae'));
  const msgs=s.messages||[];
  if(!msgs.length){
    box.innerHTML=`<div class="empty"><div class="mark">${isWorkMode?'✓':(modeKey==='muse_spark'||modeKey==='muse'||modeKey==='spark'?'✦':'P')}</div><h2>${esc(s.title||s.mode)}</h2><p>${esc(emptyHint(s.mode))}</p>
      <div class="empty-actions" style="margin-top:14px">
        <button type="button" onclick="toggleVoiceEngine()">${isVoiceMode?'🎙 Voice on':'🎙 Activate voice engine'}</button>
        ${(modeKey==='muse_spark'||modeKey==='muse'||modeKey==='spark')?'<button type="button" onclick="quickMuseOpen()">Open meta.ai</button>':''}
      </div></div>`;
    if(isVoiceMode) appendVoicePanel(box, false);
    if(isWorkMode) try{ ensureWorkingBoardPanel(true); refreshWorkingBoard(); }catch(_){}
    return;
  }
  const stick = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
  box.innerHTML='';
  // Voice panel when voice engine is on (any agent) or native Aria
  if(isVoiceMode) appendVoicePanel(box, true);
  const anyRunning=msgs.some(m=>m.status==='running'||m.status==='queued');
  msgs.forEach(m=>{
    const u=document.createElement('div');
    u.className='msg user pop-in';
    // user bubble: light markdown for code fences / inline code if they paste snippets
    const ut=String(m.text||'');
    const hasCode=ut.indexOf('`')>=0;
    u.innerHTML='<div class="mb">'+(hasCode?lightMarkdown(ut):esc(ut))+'</div>';
    box.appendChild(u);
    const sec=workedSeconds(m);
    if(sec && (m.status==='done'||m.status==='failed'||m.status==='cancelled'||m.status==='running'||m.result||m.error)){
      const meta=document.createElement('details');
      meta.className='worked-meta';
      const label=m.status==='running'||m.status==='queued'
        ? `Streaming · ${sec}s`
        : (m.status==='cancelled' ? `Stopped · ${sec}s` : `Worked for ${sec}s`);
      const eng=m.engine||s.mode||'';
      const tok=m.stream_tokens?` · ~${m.stream_tokens} tok`:'';
      const stExtra=m.status==='failed'?' · failed':(m.status==='cancelled'?' · cancelled':'');
      meta.innerHTML=`<summary>${esc(label)}${esc(stExtra)} · ${esc(eng)}${esc(tok)}</summary>
        <div class="wm-body">${esc((m.error||m.result||'').slice(0,1200)||'No detail')}</div>`;
      box.appendChild(meta);
    }
    const mentioned=mentionWorkers(m.text||'');
    if(mentioned.length){
      const hint=document.createElement('div');
      hint.className='worked-meta';
      hint.innerHTML=`<span style="color:var(--accent)">@ ${esc(mentioned.join(' · '))}</span>
        <span style="color:var(--muted)">· live status on right Workspace rail</span>`;
      box.appendChild(hint);
      try{ pollSubagents(); }catch(_){}
    }
    if(m.status==='running'||m.status==='queued'||m.status==='cancelled'||m.result||m.error||m.stream_preview){
      const streaming=(m.status==='running'||m.status==='queued');
      const isTerm=s.mode==='term'||s.mode==='shell'||s.mode==='wsl';
      const eng=m.engine||s.mode||'agent';
      const tok=m.stream_tokens?` · ~${m.stream_tokens} tok`:'';
      // Prefer live stream body whenever any text exists (first-class streaming)
      const streamBody=m.result||m.stream_preview||m.error||'';
      if(streaming && !String(streamBody).trim()){
        const tr=document.createElement('div');
        tr.className='think-row pop-in';
        const novae=String(s.mode||'').includes('novae');
        tr.innerHTML=`<div class="think-orb" aria-hidden="true"></div>
          <span class="think-label"><b>${esc(eng)}</b> thinking${novae?' · Novae hands':''}${isVoiceMode?' · listening':''}</span>
          <span class="think-dots" aria-hidden="true"><span></span><span></span><span></span></span>
          <span style="margin-left:auto;font-size:11px;opacity:.75">${esc(String(workedSeconds(m)||0)+'s')}${esc(tok)}</span>`;
        box.appendChild(tr);
      } else {
        if(streaming){
          const ban=document.createElement('div');
          ban.className='stream-banner pop-in';
          ban.innerHTML=`<span class="live-dot"></span><span><b>${esc(eng)}</b> streaming live</span>
            <span style="margin-left:auto;opacity:.8">${esc(String(workedSeconds(m)||0)+'s')}${esc(tok)}</span>`;
          box.appendChild(ban);
        }
        const a=document.createElement('div');
        a.className='msg agent pop-in '+(streaming?'streaming ':'')+(m.status||'');
        const raw=streamBody||(streaming?'':(m.status==='cancelled'?'Stopped — send a new message to reorganize.':''));
        const novaeBadge=String(s.mode||'').includes('novae')?' <span class="novae-pill">Novae</span>':'';
        const bodyHtml=isTerm?formatAgentBody(raw):formatProseBody(raw||(streaming?'…':''));
        const caret=streaming?'<span class="stream-caret" aria-hidden="true"></span>':'';
        a.innerHTML=`<div class="mh"><span><span class="live-dot" style="display:${streaming?'inline-block':'none'}"></span>${esc(eng)}${novaeBadge}${esc(tok)}</span><span>${esc(streaming?'live':(m.status||''))}</span></div>
          <div class="mb ${isTerm?'term':'prose'}">${bodyHtml}${caret}</div>`;
        box.appendChild(a);
        // Speak back ONLY in Voice ↔ Voice agent (never Codex/Grok/Plan/etc.)
        if(isVoiceMode && !streaming && m.status==='done' && raw){
          try{ speakVoiceReply(raw, m.id||''); }catch(_){}
        }
      }
    }
  });
  // Integrated agent consoles (WSL / Python / PowerShell) — always show live panel
  const consoleModes=new Set(['term','shell','wsl','wsl_native','linux','python','python_wsl','py']);
  if(consoleModes.has(String(s.mode||'').toLowerCase())){
    try{ ensureAgentConsolePanel(s); }catch(_){}
  }else{
    try{ const p=$('agentConsolePanel'); if(p) p.style.display='none'; }catch(_){}
  }
  if(s.mode==='term' && s.terminal && s.terminal.log_tail){
    const a=document.createElement('div');
    a.className='msg agent pop-in';
    a.innerHTML=`<div class="mh"><span><span class="live-dot"></span>terminal ${s.terminal.alive?'live':'off'}</span><span>pid ${s.terminal.pid||'—'}</span></div><div class="mb term">${esc(s.terminal.log_tail)}</div>`;
    box.appendChild(a);
  }
  if(anyRunning) ensureLivePoll();
  if(stick) box.scrollTop=box.scrollHeight;
  try{ refreshAiWorkspace(); }catch(_){}
  // Do not auto-start mic — user opts in on the Voice agent panel only
}
/* —— Integrated agent console (WSL + Python CLI + PowerShell) —— */
const CONSOLE_KINDS=[
  {id:'powershell', label:'PowerShell'},
  {id:'wsl', label:'WSL bash'},
  {id:'python', label:'Python (host)'},
  {id:'python_wsl', label:'Python (WSL)'},
];
function ensureAgentConsolePanel(sess){
  let p=$('agentConsolePanel');
  if(!p){
    p=document.createElement('div');
    p.id='agentConsolePanel';
    p.className='agent-console-panel';
    p.innerHTML=`
      <div class="acp-h">
        <b>Agent console</b>
        <span class="acp-sub" id="acpMeta">integrated · hidden process</span>
        <span class="grow"></span>
        <select id="acpKind" title="Console kind"></select>
        <button type="button" class="icon" onclick="refreshAgentConsole()" title="Refresh log">↻</button>
      </div>
      <pre class="acp-log" id="acpLog" aria-live="polite"></pre>
      <div class="acp-row">
        <input id="acpInput" type="text" placeholder="Command or Python line — runs in integrated console" autocomplete="off"
          onkeydown="if(event.key==='Enter'){event.preventDefault();sendAgentConsole()}"/>
        <button type="button" class="acp-go" onclick="sendAgentConsole()">Run</button>
      </div>
      <div class="acp-hint">Agents share this console. <code>use wsl</code> · <code>use python</code> · <code>use python_wsl</code> in chat also works.</div>`;
    const host=document.querySelector('.chat-col')||document.querySelector('.main')||document.body;
    const composer=document.querySelector('.composer');
    if(composer&&composer.parentNode) composer.parentNode.insertBefore(p, composer);
    else host.appendChild(p);
    const sel=$('acpKind');
    if(sel){
      CONSOLE_KINDS.forEach(k=>{
        const o=document.createElement('option'); o.value=k.id; o.textContent=k.label; sel.appendChild(o);
      });
      sel.onchange=()=>switchAgentConsoleKind(sel.value);
    }
  }
  p.style.display='block';
  // Sync kind from session
  const mode=String((sess&&sess.mode)||'').toLowerCase();
  const map={term:'powershell',shell:'powershell',wsl:'wsl',wsl_native:'wsl',linux:'wsl',python:'python',py:'python',python_wsl:'python_wsl'};
  const want=map[mode]||(sess&&sess.terminal_kind)||'powershell';
  const sel=$('acpKind');
  if(sel && [...sel.options].some(o=>o.value===want)) sel.value=want;
  // Prefill log from session terminal if any
  if(sess&&sess.terminal&&sess.terminal.log_tail){
    const log=$('acpLog');
    if(log) log.textContent=sess.terminal.log_tail.slice(-8000);
  }
  refreshAgentConsole();
  if(!ensureAgentConsolePanel._timer){
    ensureAgentConsolePanel._timer=setInterval(()=>{
      const panel=$('agentConsolePanel');
      if(!panel||panel.style.display==='none') return;
      try{ refreshAgentConsole(true); }catch(_){}
    }, 2500);
  }
}
let _acpTid=null, _acpSig='';
async function refreshAgentConsole(quiet){
  const log=$('acpLog'), meta=$('acpMeta');
  try{
    // Prefer bound session terminal
    let tid=_acpTid;
    if(activeId){
      try{
        const s=await api('/v1/sessions/'+activeId);
        if(s.terminal_id) tid=s.terminal_id;
        if(s.terminal&&s.terminal.log_tail){
          const sig=s.terminal.log_tail.length+':'+(s.terminal.log_tail.slice(-40));
          if(sig!==_acpSig && log){
            _acpSig=sig;
            log.textContent=s.terminal.log_tail.slice(-10000);
            log.scrollTop=log.scrollHeight;
          }
          if(meta) meta.textContent=(s.terminal.kind||'?')+' · '+(s.terminal.alive?'live':'off')+' · pid '+(s.terminal.pid||'—');
          _acpTid=s.terminal_id||tid;
          return;
        }
      }catch(_){}
    }
    if(tid){
      const t=await api('/v1/terminals/'+tid);
      if(t&&t.log_tail&&log){
        const sig=t.log_tail.length+':'+(t.log_tail.slice(-40));
        if(sig!==_acpSig){
          _acpSig=sig;
          log.textContent=t.log_tail.slice(-10000);
          log.scrollTop=log.scrollHeight;
        }
        if(meta) meta.textContent=(t.kind||'?')+' · '+(t.alive?'live':'off')+' · pid '+(t.pid||'—');
      }
    }else if(!quiet){
      // Ensure a console for current kind
      const kind=($('acpKind')&&$('acpKind').value)||'powershell';
      const j=await api('/v1/console/ensure',{method:'POST',body:JSON.stringify({session_id:activeId||'',kind})});
      if(j.id){ _acpTid=j.id; }
      if(j.log_tail&&log){
        log.textContent=j.log_tail.slice(-10000);
        log.scrollTop=log.scrollHeight;
      }
      if(meta) meta.textContent=(j.kind||kind)+' · '+(j.alive?'live':'off')+' · pid '+(j.pid||'—');
    }
  }catch(e){
    if(meta&&!quiet) meta.textContent='console offline';
  }
}
async function switchAgentConsoleKind(kind){
  try{
    const j=await api('/v1/console/ensure',{method:'POST',body:JSON.stringify({session_id:activeId||'',kind:kind||'powershell'})});
    _acpTid=j.id||null;
    _acpSig='';
    refreshAgentConsole();
    toast('Console · '+(j.kind||kind),'ok');
  }catch(e){ toast(e.message||'console switch failed','err'); }
}
async function sendAgentConsole(){
  const inp=$('acpInput');
  const cmd=(inp&&inp.value||'').trim();
  if(!cmd) return;
  if(inp) inp.value='';
  try{
    const kind=($('acpKind')&&$('acpKind').value)||'powershell';
    // Prefer send to known tid, else agent_run via POST /v1/terminals
    let j;
    if(_acpTid){
      j=await api('/v1/terminals/'+_acpTid+'/send',{method:'POST',body:JSON.stringify({command:cmd})});
    }else{
      j=await api('/v1/terminals',{method:'POST',body:JSON.stringify({command:cmd,kind,session_id:activeId||''})});
      if(j.id) _acpTid=j.id;
    }
    _acpSig='';
    setTimeout(()=>refreshAgentConsole(), 400);
  }catch(e){ toast(e.message||'run failed','err'); }
}
let _aiWsTimer=null;
async function refreshAiWorkspace(){
  try{
    const ws=($('wsSelect')&&$('wsSelect').value)||'parallax';
    const sid=activeId||'';
    // Prefer live chat summary when a session is open
    if(sid){
      try{
        const s=await api('/v1/sessions/'+sid);
        updateLiveSummaryFromSession(s);
      }catch(_){}
    }
    const q='/v1/ai-workspace?workspace='+encodeURIComponent(ws)+'&session_id='+encodeURIComponent(sid);
    const j=await api(q);
    const sum=$('aiSummary'), meta=$('aiSumMeta'), prev=$('aiPreviews'), tree=$('aiTree'), bus=$('aiBus');
    if(sum){
      const live=sum.dataset.had==='1' && (sum.textContent||'').trim();
      const t=(j.brief||j.summary||'').trim();
      // Keep live session brief if better; else use workspace brief
      if(!live && t) sum.textContent=t;
      else if(!live) sum.textContent='No turns yet — send a message; this panel summarizes the chat.';
    }
    if(meta){
      meta.textContent=(j.cwd?j.cwd+' · ':'')+'ctx ~'+(j.context_chars||0)+' chars · '+(j.updated_h||'live');
    }
    if(prev){
      const list=j.previews||[];
      if(!list.length){
        prev.innerHTML='<div class="hint" style="font-size:11px;color:var(--muted)">Agent outputs &amp; docs preview here after work</div>';
      } else {
        prev.innerHTML='';
        list.forEach(p=>{
          const el=document.createElement('div');
          el.className='pv';
          el.innerHTML='<b>'+esc(p.name||'preview')+'</b><pre>'+esc((p.preview||'').slice(0,500))+'</pre>';
          el.onclick=()=>{ try{ navigator.clipboard.writeText(p.preview||''); toast('Preview copied'); }catch(_){ } };
          prev.appendChild(el);
        });
      }
    }
    if(tree){
      const files=j.index||[];
      tree.innerHTML=files.slice(0,24).map(f=>esc(f.path||'')).join('<br>')||'<span style="color:var(--muted)">index empty — will build on first job</span>';
    }
    if(bus){
      const msgs=j.bus||[];
      if(!msgs.length){
        bus.innerHTML='<div class="hint" style="font-size:11px;color:var(--muted)">Hashed swarm notes appear as agents finish</div>';
      } else {
        bus.innerHTML=msgs.slice(0,8).map(m=>
          '<div class="bm"><b>'+esc(m.from||'?')+'</b> → '+esc(m.to||'?')
          +' <span class="hm">'+(m.hmac?esc(m.hmac):'')+'</span><br>'
          +esc((m.body||'').slice(0,160))+'</div>'
        ).join('');
      }
    }
  }catch(e){
    const sum=$('aiSummary');
    if(sum && !sum.dataset.had) sum.textContent='Workspace API warming…';
  }
}
function ensureAiWorkspacePoll(){
  if(_aiWsTimer) return;
  // Less chatty rail refresh — cuts background latency while typing
  _aiWsTimer=setInterval(()=>{ if(activeId) refreshAiWorkspace(); refreshOffload(); }, 7000);
}
async function refreshOffload(){
  try{
    const j=await api('/v1/offload?limit=8');
    const el=$('offloadList'); if(!el) return;
    const tasks=j.tasks||[];
    if(!tasks.length){ el.textContent='No tickets yet · start Offload agent or POST /v1/offload'; return; }
    el.innerHTML=tasks.slice(0,6).map(t=>
      '<div style="margin:0 0 6px"><b style="color:var(--accent)">'+esc(t.status||'')+'</b> '+
      esc((t.id||'').slice(0,14))+' · '+esc((t.goal||'').slice(0,80))+'</div>'
    ).join('');
  }catch(_){}
}
function setPresets(mode){
  const box=$('presets'); box.innerHTML='';
  const sets={
    codex:[['Ship code','Implement one concrete production fix in this workspace, run the smallest check, summarize the diff.'],['Continue','Continue from where you left off — code first, not a research essay.'],['Preview UI','Build a tiny self-contained HTML demo for this feature and end with an ```html-preview block so it shows in the chat bubble.']],
    vision:[['Observe','observe'],['UI map','map'],['OCR text','ocr'],['Find button','find Save'],['Click name','click Start'],['Status','status'],['Help','help']],
    oculus:[['Observe','observe'],['Map','map'],['Help','help']],
    github:[['Status','status'],['List repos','list repos'],['Issues','issues'],['PRs','prs'],['Help','help']],
    gh:[['Status','status'],['List repos','list repos'],['Help','help']],
    voice:[['Who are you','who are you?'],['What can you do','what can you help with?'],['Add todo','add call the bank to my todo'],['Grocery','add milk to grocery list'],['What time','what time is it?'],['Focus','help me focus'],['Plan day','plan my day']],
    work:[['Start','start work'],['Sense screen','sense'],['Package','package'],['Handoff artifacts','handoff'],['CLI gh','cli gh auth status'],['MCP catalog','mcp pocket cli_list'],['Click Save','click Save']],
    working:[['Start','start work'],['Package','package'],['Handoff','handoff']],
    mcp:[['Catalog','list'],['Pocket tools','mcp pocket cli_list'],['GitHub repos','mcp github repos'],['Screen status','mcp pocket screen_status']],
    grok:[['Ship code','Implement one useful code improvement, verify briefly, report files changed.'],['Explain','Summarize this project in 8 bullets.'],['Stop & reorganize','Stop prior work. Inventory production gaps and ship one concrete code fix.']],
    offload:[['Desk proof','capability snapshot then screenshot then note: operator away embodiment sprint'],['Open edge','open edge https://pocket.medinatechlabs.net/'],['Refresh workspace','workspace_refresh for parallax then screenshot']],
    cowork:[['Record demo','record demo: open edge https://pocket.medinatechlabs.net/ then screenshot'],['Desk tour','open notepad then screenshot then deliver note: cowork tour'],['No record','without record: capability snapshot and screenshot']],
    git:[['Create repo','create repo my-app'],['List','list repos'],['Help','help']],
    ghost:[['Hash chain','chain hash a|b|c'],['Phi','phi 21'],['Digest','digest this prompt']],
    plan:[['Next features','Plan only: next 5 product features, ordered, with risks. No code.'],['Phone UX','Plan only: improve mobile UX. No implementation.']],
    term:[['List','Get-ChildItem'],['Python','python --version'],['Git','git status']],
    shell:[['Dir','dir'],['Git','git status']],
    wsl:[['Status','status'],['Workspace','pwd; ls -la'],['Python','python3 --version'],['Tools','which python3 node npm git'],['use python_wsl','use python_wsl']],
    wsl_native:[['Status','status'],['Workspace','pwd; ls -la'],['Python','python3 --version'],['Tools','which python3 node npm git']],
    linux:[['Status','status'],['Workspace','pwd; ls -la']],
    python:[['Help','help'],['Version','import sys; print(sys.version)'],['Cwd','import os; print(os.getcwd())'],['use wsl','use wsl']],
    python_wsl:[['Version','import sys; print(sys.version)'],['Cwd','import os; print(os.getcwd())'],['List','import os; print(os.listdir("."))']],
    term:[['Help','help'],['use wsl','use wsl'],['use python','use python'],['Dir','Get-ChildItem | Select -First 12']],
    build:[['List use cases','list'],['Parity','parity'],['Full-stack app','use_case:fullstack_web_app'],['SaaS dashboard','use_case:saas_dashboard'],['API service','use_case:api_microservice']],
    ship:[['Full-stack','use_case:fullstack_web_app'],['Ship swarm','use_case:multi_agent_swarm']],
    use_case:[['List','list'],['Web app','fullstack_web_app'],['API','api_microservice'],['Custom agent','agent_inside_product'],['Test-fix','test_troubleshoot']],
    emergent:[['Parity matrix','parity'],['Beat Emergent web app','use_case:fullstack_web_app'],['Swarm until done','use_case:multi_agent_swarm']],
    custom_agent:[['List','list'],['Create support','create SupportAgent: customer support specialist'],['Help','help']],
    wiki:[['Help','help'],['Profile server.py','profile C:/Users/Medin/OneDrive/pocket-os/src/pocket/server.py'],['Read lines 164-190','read_lines C:/Users/Medin/OneDrive/pocket-os/src/pocket/server.py 164 190'],['Find symbol','symbol get_file_profile'],['Index pocket src','index C:/Users/Medin/OneDrive/pocket-os/src/pocket'],['Search','search orchestrator']],
    infinite_wiki:[['Help','help'],['Profile','profile C:/Users/Medin/OneDrive/pocket-os/src/pocket/infinite_wiki.py'],['Symbol','symbol read_file_lines']],
    codebase:[['Help','help'],['Search','search infinite wiki']],
    handoff:[['Defer plan','Package a full research plan for multi-user seats and cost.']],
    claude:[['Review','Review for bugs and missing tests.']],
    agent:[['Lookup+bring back','lookup multi-agent desktop AI platforms 2026'],['Edge+calc+snip','open edge https://pocket.medinatechlabs.net/ then open calc then open snip'],['Daily schedule','schedule daily lookup AI agent news'],['10-step style','open explorer then open notepad then lookup POCKET multi-agent desk']],
    doer:[['3-step desk','open edge https://example.com then open notepad then open calc'],['Lookup','lookup Cloudflare tunnels'],['Schedule','schedule daily lookup market brief']],
    guppy:[['Who','help'],['Lookup','lookup multi-agent desk platforms'],['Open Copilot query','open copilot POCKET host co-pilot'],['Daily fetch','schedule daily lookup AI and markets'],['Status','status'],['Schedule list','schedule list']],
    browser:[['Help','help'],['Research→Tweet','look up multi-agent desktop AI then write a tweet for my page https://x.com/ItsnotAILabs'],['Tweet only','tweet Shipping POCKET Browser mode — real desk agents from ItsNotAI Labs'],['Open X','open x'],['Win Copilot','open copilot'],['Web Copilot','open copilot web multi-agent platforms'],['Lookup','lookup Cloudflare named tunnels'],['Open 5 repos','open my 5 repos'],['Screenshot','screenshot'],['Use Grok','engine:grok look up AI agents and draft a tweet for https://x.com/ItsnotAILabs'],['Use Codex','engine:codex research POCKET and draft a launch tweet']],
    capture:[['Screenshot','screenshot'],['Snip tool','snip'],['Help','help']],
    repos:[['Analyze Brain AI','analyze brain ai'],['Analyze Imagine','analyze imagine'],['Open 5 repos','open my 5 repos'],['List repos','list repos'],['gh status','gh status'],['New git repo','new repo pocket-demo'],['Help','help']],
    copilot:[['Introduce+send','introduce'],['As Grok','introduce as Grok: multi-agent desk on this PC'],['Open app','open'],['Web','open web'],['Help','help']],
    archon:[['Platform map','platform_map'],['Find feature','find_feature habitat'],['Fusion voice','fusion_voice flight delayed hotel'],['Pair phone','pair_mint'],['Workers','workers'],['Skills list','list skills'],['Habitat','habitat_status'],['Screen sense','screen_sense'],['Working start','work_start'],['Screenshot','screenshot']],
    workers:[['List','workers'],['ARCHON help','ARCHON help'],['SCRUTATOR brain','SCRUTATOR analyze neuroemergence-core']],
    desktop:[['List apps','list apps'],['Copilot','open copilot'],['Antigravity','open antigravity'],['Snip','open snip'],['Screen clip','open screenclip'],['Notepad','open notepad'],['Explorer','open explorer'],['Edge+URL','open edge https://pocket.medinatechlabs.net/'],['VS Code','open code'],['Cursor','open cursor'],['Chrome','open chrome'],['Discord','open discord'],['Teams','open teams'],['GitHub Desktop','open github'],['Word','open word'],['Excel','open excel'],['Calc','open calc'],['Multi-step','open edge https://example.com then open notepad then open calc'],['Settings','open settings'],['Task Manager','open taskmgr']],
    web:[['Search','search multi agent desktop AI platforms 2026'],['Fetch','fetch https://example.com'],['Research','research Cloudflare tunnel named vs quick tunnel']],
    nexus:[['List','list'],['Bridge servers','run Bridge list_servers'],['Status','help']]
  };
  (sets[mode]||[]).forEach(([label,text])=>{
    const b=document.createElement('button'); b.type='button'; b.textContent=label;
    b.onclick=()=>{$('input').value=text};
    box.appendChild(b);
  });
}
function formatAgentBody(body){
  // Allow data-URI screenshots from capture agent; escape everything else
  const s=String(body||'');
  const re=/!\[([^\]]*)\]\((data:image\/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+)\)/g;
  let html='', last=0, m;
  while((m=re.exec(s))){
    html+=esc(s.slice(last,m.index));
    html+=`<div style="margin:8px 0"><img alt="${esc(m[1]||'shot')}" src="${m[2]}" style="max-width:100%;border-radius:8px;border:1px solid var(--line)"/></div>`;
    last=m.index+m[0].length;
  }
  html+=esc(s.slice(last));
  return html;
}
function polishChatText(raw){
  // Client-side mirror of pocket.reply_format — strip CLI chrome so convo looks good
  let s=String(raw||'');
  if(!s) return '';
  // Fix common mojibake
  const pairs=[['â€™',"'"],['â€˜',"'"],['â€œ','"'],['â€\u009d','"'],['â€”','—'],['â€“','-'],['â€¦','...'],['Â·','·'],['Â ',' '],['â†’','→'],['\uFFFD','']];
  pairs.forEach(([a,b])=>{ if(s.includes(a)) s=s.split(a).join(b); });
  const banner=/^(Reading additional input from stdin\.?|OpenAI Codex v[\d.]+|-{3,}|workdir:.+|model:.+|provider:.+|approval:.+|sandbox:.+|reasoning (?:effort|summaries):.+|session id:.+|tokens used|\d{1,3}(?:,\d{3})*$|user$|codex$|\[stream_tokens[^\]]*\]|\[llm_tokens[^\]]*\]|\[pocket_session[^\]]*\]|\[engine=[^\]]+\]|\[cli=[^\]]+\]|\[research_package=[^\]]+\])\s*$/i;
  const lines=s.replace(/\r\n/g,'\n').replace(/\r/g,'\n').split('\n');
  const kept=[];
  let skipUser=false;
  lines.forEach(line=>{
    const t=line.trim();
    if(/^user$/i.test(t)){ skipUser=true; return; }
    if(skipUser){
      if(/^\[Client device:/i.test(t) || !t){ return; }
      skipUser=false;
      if(/^codex$/i.test(t)) return;
    }
    if(banner.test(t)) return;
    kept.push(line);
  });
  s=kept.join('\n').replace(/\n{3,}/g,'\n\n').trim();
  // Unstick run-on stream blobs when almost no newlines
  if((s.match(/\n/g)||[]).length < Math.max(3, s.length/500)){
    s=s.replace(/([.!?])([A-Z][a-z])/g,'$1\n\n$2');
  }
  // Prefer text after last "tokens used" summary block
  const parts=s.split(/\ntokens used\n[\d,]+\s*\n/i);
  if(parts.length>=2 && parts[parts.length-1].trim().length>40) s=parts[parts.length-1].trim();
  return s;
}
function extractProse(raw){
  let s=String(raw||'').trim();
  if(!s) return '';
  if(s==='Thinking…'||s==='… running …') return s;
  s=polishChatText(s);
  // Prefer human fields when result is JSON dump
  if((s.startsWith('{')||s.startsWith('[')) && s.length>2){
    try{
      const j=JSON.parse(s);
      if(typeof j==='string') return j;
      if(j && typeof j==='object'){
        for(const k of ['message','brief','summary','text','result','answer','output','content','note']){
          if(typeof j[k]==='string' && j[k].trim()) return polishChatText(j[k]);
        }
        if(Array.isArray(j.steps)){
          return j.steps.map((st,i)=>{
            if(typeof st==='string') return (i+1)+'. '+st;
            return (i+1)+'. '+(st.skill||st.name||st.action||'')+' '+(st.message||st.prompt||st.status||'');
          }).join('\n');
        }
        if(j.ok!=null && j.message) return String(j.message);
        // compact non-noisy keys only
        const skip=new Set(['ok','status','id','job_id','session_id','ts','created_at','finished_at']);
        const lines=[];
        Object.keys(j).forEach(k=>{
          if(skip.has(k)) return;
          const v=j[k];
          if(v==null||v==='') return;
          if(typeof v==='string'||typeof v==='number'||typeof v==='boolean') lines.push(k+': '+v);
        });
        if(lines.length) return lines.join('\n');
      }
    }catch(_){}
  }
  return s;
}
function buildAppPreviewBubble(opts){
  const title=String((opts&&opts.title)||'App preview').slice(0,80);
  let url=String((opts&&opts.url)||'').trim();
  const htmlRaw=(opts&&opts.html)||'';
  const id='ap_'+Math.random().toString(36).slice(2,10);
  // Relative /v1/preview/… → absolute on this host
  if(url && url.startsWith('/')){
    try{ url=location.origin+url; }catch(_){ url='http://127.0.0.1:8787'+url; }
  }
  let frame='';
  if(htmlRaw){
    // srcdoc: escape & and " only (browser HTML-parses the attribute value)
    const safe=String(htmlRaw).replace(/&/g,'&amp;').replace(/"/g,'&quot;');
    frame='<iframe class="ap-frame" title="'+esc(title)+'" sandbox="allow-scripts allow-forms allow-modals allow-popups allow-same-origin" srcdoc="'+safe+'"></iframe>';
  }else if(url){
    frame='<iframe class="ap-frame" title="'+esc(title)+'" sandbox="allow-scripts allow-forms allow-modals allow-popups allow-same-origin allow-downloads" src="'+esc(url)+'"></iframe>';
  }else{
    frame='<div style="padding:24px;color:var(--muted);font-size:12px">No preview URL or HTML</div>';
  }
  const openHref=url?esc(url):'#';
  return '<div class="app-preview" id="'+id+'" data-ap="1">'+
    '<div class="ap-head"><span class="ap-dot" aria-hidden="true"></span><b>'+esc(title)+'</b>'+
    '<span class="ap-actions">'+
    '<button type="button" onclick="this.closest(\'.app-preview\').classList.toggle(\'expanded\')">Expand</button>'+
    (url?'<a href="'+openHref+'" target="_blank" rel="noopener">Open</a>':'')+
    '<button type="button" onclick="var f=this.closest(\'.app-preview\').querySelector(\'iframe\');if(f){if(f.srcdoc!=null&&f.srcdoc!==\'\'){var d=f.srcdoc;f.srcdoc=\'\';f.srcdoc=d;}else{try{f.src=f.src;}catch(_){}}}">Reload</button>'+
    '</span></div>'+
    '<div class="ap-frame-wrap">'+frame+'</div>'+
    (url?'<div class="ap-url" title="'+esc(url)+'">'+esc(url)+'</div>':'')+
    '</div>';
}
function parsePreviewMeta(body){
  const lines=String(body||'').split(/\r?\n/);
  let title='App preview', url='', htmlLines=[];
  let inHtml=false;
  for(const ln of lines){
    const mTitle=ln.match(/^\s*title\s*[:=]\s*(.+)$/i);
    const mUrl=ln.match(/^\s*url\s*[:=]\s*(\S+)/i);
    const mSrc=ln.match(/^\s*(src|href)\s*[:=]\s*(\S+)/i);
    if(mTitle){ title=mTitle[1].trim(); continue; }
    if(mUrl){ url=mUrl[1].trim(); continue; }
    if(mSrc){ url=mSrc[2].trim(); continue; }
    if(/^\s*https?:\/\//i.test(ln.trim()) && !url){ url=ln.trim(); continue; }
    if(/^\s*\/v1\/preview\//i.test(ln.trim()) && !url){ url=ln.trim(); continue; }
    if(/^\s*<(!DOCTYPE|html|div|body|section|main)/i.test(ln) || inHtml){
      inHtml=true; htmlLines.push(ln); continue;
    }
  }
  return {title, url, html: htmlLines.join('\n').trim()};
}
function lightMarkdown(text){
  // Escape then light markdown: **bold**, `code`, fenced snippets with Copy, lists, headings
  // + in-chat app preview bubbles (```preview / ```html-preview)
  let s=esc(text);
  // Hide internal TTS payload fences from chat (spoken separately)
  s=s.replace(/```tts\n?[\s\S]*?```/gi,'');
  const snips=[];
  function pushPreview(kind, code){
    const raw=String(code||'').replace(/^\n+/,'').replace(/\n+$/,'');
    // Unescape entities we just applied via esc() for HTML body
    const unesc=raw
      .replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
    const k=(kind||'').toLowerCase();
    let title='App preview', url='', html='';
    if(k==='html-preview'||k==='preview-html'||k==='htmlpreview'||k==='app-html'||
       k==='simulation'||k==='sim'||k==='artifact-preview'){
      html=unesc;
      const tm=unesc.match(/<title[^>]*>([^<]*)<\/title>/i);
      if(tm) title=tm[1].trim()||title;
      if(k==='simulation'||k==='sim') title=title==='App preview'?'Simulation':title;
    }else{
      // preview / app / preview-url — meta lines or raw URL/HTML
      const meta=parsePreviewMeta(unesc);
      title=meta.title||title;
      url=meta.url||'';
      html=meta.html||'';
      if(!url && !html && /^\s*https?:\/\//i.test(unesc.trim())){
        url=unesc.trim().split(/\s+/)[0];
      }
      if(!url && !html && unesc.trim().startsWith('<')){
        html=unesc;
      }
    }
    const htmlBubble=buildAppPreviewBubble({title, url, html});
    snips.push({html:htmlBubble, full:unesc, id:null});
    return '\u0000SNIP'+ (snips.length-1) +'\u0000';
  }
  function pushSnip(lang, code){
    const id='cs_'+Math.random().toString(36).slice(2,9);
    let label=(lang||'code').trim()||'code';
    const low=label.toLowerCase();
    if(low==='tts') return ''; // never show tts as tall code
    // App / site / simulation fences → bubble iframe (not code wall)
    if(low==='preview'||low==='app'||low==='preview-url'||low==='app-preview'||
       low==='html-preview'||low==='preview-html'||low==='htmlpreview'||low==='app-html'||
       low==='simulation'||low==='sim'||low==='artifact-preview'||low==='site'||low==='web-preview'){
      return pushPreview(low, code);
    }
    const body=(code||'').replace(/^\n+/,'').replace(/\n+$/,'');
    // Cap absurd walls of code in the bubble (still copyable full text)
    const lines=body.split('\n');
    const truncated=lines.length>80;
    const shown=truncated?lines.slice(0,80).join('\n')+'\n/* … truncated for display · Copy for full */':body;
    const html='<div class="code-snip" data-cs="1"><div class="cs-head"><span class="cs-lang">'+label+(truncated?' · '+lines.length+' lines':'')+'</span>'+
      '<button type="button" class="cs-copy" data-cs-id="'+id+'">Copy</button></div>'+
      '<pre id="'+id+'">'+shown+'</pre></div>';
    // store full body for copy
    snips.push({html:html, full:body, id:id});
    return '\u0000SNIP'+ (snips.length-1) +'\u0000';
  }
  // Fenced code → compact snippet cards (lang + copy) — not tall walls
  // Also: preview fences → live app bubbles
  s=s.replace(/```([a-zA-Z0-9_+#.-]*)\n?([\s\S]*?)```/g,(_,lang,code)=>pushSnip(lang,code));
  s=s.replace(/`([^`\n]+)`/g,'<code>$1</code>');
  s=s.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  // line-level: headings + bullets
  const blocks=s.split(/\n{2,}/).map(block=>{
    if(/\u0000SNIP\d+\u0000/.test(block) && !block.replace(/\u0000SNIP\d+\u0000/g,'').trim()){
      return block; // pure snippet block
    }
    const lines=block.split('\n');
    const allBullets=lines.every(ln=>/^\s*([-*]|\d+\.)\s+/.test(ln)||!ln.trim()||/\u0000SNIP/.test(ln));
    if(allBullets && lines.some(ln=>ln.trim() && !/\u0000SNIP/.test(ln))){
      const items=lines.filter(ln=>ln.trim() && !/\u0000SNIP/.test(ln)).map(ln=>'<li>'+ln.replace(/^\s*([-*]|\d+\.)\s+/,'')+'</li>').join('');
      const snipBits=lines.filter(ln=>/\u0000SNIP/.test(ln)).join('');
      return (items?'<ul style="margin:0.4em 0 0.6em 1.1em;padding:0">'+items+'</ul>':'')+snipBits;
    }
    const rendered=lines.map(ln=>{
      if(/\u0000SNIP\d+\u0000/.test(ln)) return ln;
      if(/^#{1,3}\s+/.test(ln)){
        const lvl=Math.min(3,(ln.match(/^#+/)||['#'])[0].length);
        const t=ln.replace(/^#{1,3}\s+/,'');
        return '<div class="md-h" style="font-weight:700;font-size:'+(lvl===1?'1.05em':lvl===2?'1em':'0.95em')+';margin:0.5em 0 0.25em">'+t+'</div>';
      }
      if(/^\s*([-*]|\d+\.)\s+/.test(ln)) return '<div class="md-li" style="padding-left:1em">• '+ln.replace(/^\s*([-*]|\d+\.)\s+/,'')+'</div>';
      return ln;
    }).join('<br>');
    if(!rendered.trim()) return '';
    return '<p style="margin:0.45em 0">'+rendered+'</p>';
  });
  let out=blocks.join('');
  out=out.replace(/\u0000SNIP(\d+)\u0000/g,(_,i)=>{
    const item=snips[Number(i)];
    if(!item) return '';
    if(typeof item==='string') return item;
    return item.html||'';
  });
  // stash full code for copy
  try{
    if(!window.__pocketSnipFull) window.__pocketSnipFull={};
    snips.forEach(it=>{ if(it&&it.id&&it.full!=null) window.__pocketSnipFull[it.id]=it.full; });
  }catch(_){}
  return out;
}
// Copy buttons on code snippets (event delegation) — prefers full source
document.addEventListener('click',(ev)=>{
  const btn=ev.target && ev.target.closest && ev.target.closest('.cs-copy');
  if(!btn) return;
  const id=btn.getAttribute('data-cs-id');
  const pre=id?document.getElementById(id):null;
  let t='';
  try{ if(id&&window.__pocketSnipFull&&window.__pocketSnipFull[id]!=null) t=window.__pocketSnipFull[id]; }catch(_){}
  if(!t) t=pre?(pre.innerText||pre.textContent||''):'';
  if(!t) return;
  try{
    navigator.clipboard.writeText(t).then(()=>{
      const old=btn.textContent; btn.textContent='Copied'; setTimeout(()=>{ btn.textContent=old||'Copy'; },1200);
    }).catch(()=>{ toast('Copy failed','err'); });
  }catch(_){ toast('Copy failed','err'); }
});

/* —— Voice ↔ Voice panel + TTS —— */
const _voiceSpoken={};
function appendVoicePanel(box, live){
  if(!box) return;
  const p=document.createElement('div');
  p.className='v2v-panel'+(live?' live':'');
  p.id='v2vPanel';
  p.innerHTML=`<div class="v2v-title">Aria · Voice persona</div>
    <div class="v2v-wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <div class="v2v-status" id="v2vStatus">${live
      ? 'Aria is ready · patient 1400ms · natural breath pauses · neural voice when available'
      : 'Start talking — Aria listens patiently and answers like a real person.'}</div>
    <div class="v2v-actions">
      <button type="button" id="v2vMic" class="${micOn?'hot':''}">${micOn?'⏹ Stop mic':'🎙 Start talking'}</button>
      <button type="button" id="v2vGreet">Meet Aria</button>
    </div>`;
  box.insertBefore(p, box.firstChild);
  const micB=p.querySelector('#v2vMic');
  if(micB) micB.onclick=()=>{ toggleMic(); micB.classList.toggle('hot', !!micOn); micB.textContent=micOn?'⏹ Stop mic':'🎙 Start talking'; };
  const gB=p.querySelector('#v2vGreet');
  if(gB) gB.onclick=()=>{
    const el=$('input');
    if(el){ el.value='Hey Aria — introduce yourself briefly as my voice partner, warm and human, then ask what I need help with.'; sendMsg(); }
  };
}
/** Aria — human-like voice persona (warm, unhurried, slightly imperfect cadence). */
const VOICE_PERSONA={
  name:'Aria',
  // Prefer natural/neural Windows/Edge voices over robotic defaults
  prefer:/aria|jenny|natural|neural|google us english|samantha|zira|susan|eva|emma|michelle|sonia|female/i,
  avoid:/microsoft david|microsoft mark|compact|robot|espeak/i,
  rate:0.92,
  pitch:1.06,
  lang:'en-US',
  // Micro-variation so consecutive turns do not sound identical
  rateJitter:0.04,
  pitchJitter:0.03,
};
let _voiceVoiceCache=null;
function pickHumanVoice(){
  if(!window.speechSynthesis) return null;
  try{
    const list=window.speechSynthesis.getVoices()||[];
    if(!list.length) return _voiceVoiceCache;
    if(_voiceVoiceCache && list.some(v=>v.voiceURI===_voiceVoiceCache.voiceURI)) return _voiceVoiceCache;
    const ranked=list
      .filter(v=>/en(-|_)?(us|gb|au)?/i.test(v.lang||'en') || /english/i.test(v.name||''))
      .map(v=>{
        let score=0;
        const n=(v.name||'')+' '+(v.voiceURI||'');
        if(VOICE_PERSONA.prefer.test(n)) score+=5;
        if(VOICE_PERSONA.avoid.test(n)) score-=4;
        if(/neural|natural|online/i.test(n)) score+=3;
        if(/local/i.test(n)) score+=1;
        if(/en-US/i.test(v.lang||'')) score+=1;
        return {v,score};
      })
      .sort((a,b)=>b.score-a.score);
    _voiceVoiceCache=(ranked[0]&&ranked[0].v) || list.find(v=>/en/i.test(v.lang||'')) || list[0] || null;
    return _voiceVoiceCache;
  }catch(_){ return null; }
}
try{ if(window.speechSynthesis){ window.speechSynthesis.onvoiceschanged=()=>{ _voiceVoiceCache=null; pickHumanVoice(); }; } }catch(_){}
function extractTtsMeta(raw){
  const s=String(raw||'');
  const m=s.match(/```tts\n?([\s\S]*?)```/i);
  let rate=null, pitch=null, text='';
  if(m){
    let body=m[1].trim();
    const rm=body.match(/^rate\s*=\s*([\d.]+)\s*\n?/i);
    if(rm){ rate=parseFloat(rm[1]); body=body.slice(rm[0].length); }
    const pm=body.match(/^pitch\s*=\s*([\d.]+)\s*\n?/i);
    if(pm){ pitch=parseFloat(pm[1]); body=body.slice(pm[0].length); }
    text=body.trim();
  }
  if(!text){
    text=s
      .replace(/```[\s\S]*?```/g,' ')
      .replace(/\[engine=[^\]]+\]/gi,'')
      .replace(/\*\*?/g,'')
      .replace(/_listening:[^\n]*/gi,'')
      .replace(/\*\*Context buffer:\*\*[^\n]*/gi,'')
      .replace(/\s+/g,' ')
      .trim();
  }
  // Human cadence: break run-ons; keep for speech only
  text=text
    .replace(/\s*—\s*/g,', ')
    .replace(/\s*…\s*/g,'… ')
    .replace(/([.!?])\s+/g,'$1 ')
    .slice(0,720);
  return {text, rate, pitch};
}
function extractTtsText(raw){ return extractTtsMeta(raw).text; }
/** Split into breath groups so TTS sounds conversational, not monologue-dump. */
function breathChunks(text){
  const t=String(text||'').trim();
  if(!t) return [];
  // Prefer sentence boundaries; fall back to clause commas for long lines
  const parts=t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  const out=[];
  for(const p of parts){
    if(p.length>160){
      p.split(/(?<=[,;:])\s+/).forEach(c=>{ if(c.trim()) out.push(c.trim()); });
    }else out.push(p);
  }
  return out.length?out:[t];
}
function extractAudioUrl(raw){
  const m=String(raw||'').match(/```audio\n?([^\n`]+)```/i);
  if(m) return (m[1]||'').trim();
  return '';
}
let _ariaAudio=null;
function speakVoiceReply(raw, id){
  // Voice agent always; Working mode also speaks brief replies
  if(!isVoiceSessionMode() && !isWorkSessionMode()) return;
  const key=String(id||'')+'|'+(String(raw||'').length);
  if(_voiceSpoken[key]) return;
  _voiceSpoken[key]=1;
  const meta=extractTtsMeta(raw);
  const text=meta.text;
  if(!text||text.length<2) return;
  const st=$('v2vStatus');
  // Prefer free neural TTS (edge-tts via host) when available — more natural than browser robot
  const audioUrl=extractAudioUrl(raw);
  const playBrowser=()=>{
    if(!window.speechSynthesis) return;
    try{ window.speechSynthesis.cancel(); }catch(_){}
    try{ if(_ariaAudio){ _ariaAudio.pause(); _ariaAudio=null; } }catch(_){}
    const voice=pickHumanVoice();
    const chunks=breathChunks(text);
    const baseRate=meta.rate!=null?meta.rate:(micOn?0.98:VOICE_PERSONA.rate);
    const basePitch=meta.pitch!=null?meta.pitch:VOICE_PERSONA.pitch;
    if(st) st.textContent=VOICE_PERSONA.name+' speaking… '+text.slice(0,72)+(text.length>72?'…':'');
    let i=0;
    const speakNext=()=>{
      if(i>=chunks.length){
        const s2=$('v2vStatus');
        if(s2&&micOn) s2.textContent='Listening… patient 1400ms · '+VOICE_PERSONA.name;
        return;
      }
      const chunk=chunks[i++];
      const u=new SpeechSynthesisUtterance(chunk);
      u.lang=VOICE_PERSONA.lang;
      const jR=(Math.random()*2-1)*VOICE_PERSONA.rateJitter;
      const jP=(Math.random()*2-1)*VOICE_PERSONA.pitchJitter;
      u.rate=Math.max(0.75, Math.min(1.15, baseRate+jR));
      u.pitch=Math.max(0.85, Math.min(1.25, basePitch+jP));
      if(voice) u.voice=voice;
      u.onend=()=>{ setTimeout(speakNext, i<chunks.length?90:0); };
      u.onerror=()=>{ speakNext(); };
      try{ window.speechSynthesis.speak(u); }catch(_){ speakNext(); }
    };
    pickHumanVoice();
    speakNext();
  };
  const playNeural=(url)=>{
    try{ if(_ariaAudio){ _ariaAudio.pause(); } }catch(_){}
    try{ window.speechSynthesis&&window.speechSynthesis.cancel(); }catch(_){}
    const a=new Audio(url);
    _ariaAudio=a;
    if(st) st.textContent=VOICE_PERSONA.name+' speaking (neural)…';
    a.onended=()=>{
      if(st&&micOn) st.textContent='Listening… patient 1400ms · '+VOICE_PERSONA.name;
    };
    a.onerror=()=>{ playBrowser(); };
    a.play().catch(()=>playBrowser());
  };
  if(audioUrl){
    playNeural(audioUrl);
    return;
  }
  // Ask host for free edge-tts audio; fall back to browser voices
  (async()=>{
    try{
      const j=await api('/v1/voice/tts',{method:'POST',body:JSON.stringify({text:text.slice(0,480)})});
      if(j&&j.ok&&j.url_path){ playNeural(j.url_path); return; }
    }catch(_){}
    playBrowser();
  })();
}
function formatProseBody(body){
  // Infinite Wiki Profile Card JSON → interactive card UI
  const wikiHtml = tryRenderWikiCard(body);
  if(wikiHtml) return wikiHtml;
  const prose=extractProse(body);
  // keep image embeds from original
  const imgs=[];
  const re=/!\[([^\]]*)\]\((data:image\/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+)\)/g;
  let m, src=String(body||'');
  while((m=re.exec(src))){
    imgs.push(`<div style="margin:8px 0"><img alt="${esc(m[1]||'shot')}" src="${m[2]}" style="max-width:100%;border-radius:8px;border:1px solid var(--line)"/></div>`);
  }
  const cleaned=prose.replace(/!\[[^\]]*\]\(data:image\/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+\)/g,'').trim();
  // Collapse engine meta into a small dim line when still present
  let main=cleaned;
  const metaLines=[];
  main=main.split('\n').filter(ln=>{
    if(/^\[(engine|cli|research_package|pocket_session|stream_tokens|llm_tokens)/i.test(ln.trim())){
      metaLines.push(ln.trim().replace(/^\[|\]$/g,''));
      return false;
    }
    return true;
  }).join('\n').trim();
  const metaHtml=metaLines.length
    ? `<div class="mh-meta" style="opacity:0.55;font-size:11px;margin-bottom:6px">${esc(metaLines.slice(0,3).join(' · '))}</div>`
    : '';
  return metaHtml+lightMarkdown(main||(imgs.length?'':'…'))+imgs.join('');
}
/** Parse Profile Card / goto JSON from agent output and render interactive UI. */
function tryRenderWikiCard(body){
  const raw=String(body||'').trim();
  if(!raw || raw[0]!=='{' ) return '';
  let j=null;
  try{ j=JSON.parse(raw); }catch(_){
    // try first JSON object embedded
    const i=raw.indexOf('{'), k=raw.lastIndexOf('}');
    if(i>=0 && k>i){
      try{ j=JSON.parse(raw.slice(i,k+1)); }catch(__){ return ''; }
    } else return '';
  }
  if(!j || typeof j!=='object') return '';
  // goto_definition payload
  if(Array.isArray(j.definitions)){
    return renderGotoCard(j);
  }
  // profile card
  if(j.ok && (j.symbols || j.sections) && (j.path || j.schema==='pocket.file_profile.v1')){
    return renderProfileCard(j);
  }
  return '';
}
function renderProfileCard(card){
  const path=card.path||'';
  const id='wc_'+Math.random().toString(36).slice(2,9);
  const ast=card.ast_engine||'heuristic';
  const syms=(card.symbols||[]).slice(0,24);
  const symHtml=syms.map(s=>{
    const n=s.name||'?';
    const ln=s.line||1;
    const en=s.end_line||ln;
    return `<button type="button" class="wc-sym" data-wiki-open="1" data-path="${esc(path)}" data-name="${esc(n)}" data-start="${ln}" data-end="${en}" title="Open definition L${ln}–L${en}">
      <b>${esc(n)}</b><em>${esc(s.kind||'sym')} · L${ln}–L${en}</em>
    </button>`;
  }).join('') || '<span style="color:var(--muted);font-size:12px">No symbols</span>';
  return `<div class="wiki-card" id="${id}" data-wiki-path="${esc(path)}">
    <div class="wc-head">
      <span class="wc-badge">Wiki</span>
      <div class="wc-title"><b>${esc(card.name||path.split(/[/\\\\]/).pop()||'file')}</b>
        <span>${esc(card.language||'')} · ${esc(String(card.line_count||'?'))} lines · ${esc(String((card.deps||[]).length))} deps</span>
      </div>
      <span class="wc-ast ${ast==='tree-sitter'?'ts':''}" title="AST engine">${esc(ast)}</span>
    </div>
    <div class="wc-sum">${esc((card.summary||'').slice(0,280))}</div>
    <div class="wc-syms">${symHtml}</div>
    <div class="wc-actions">
      <button type="button" class="primary" data-wiki-open-top="1" data-path="${esc(path)}" data-name="${esc((syms[0]&&syms[0].name)||'')}" data-start="${(syms[0]&&syms[0].line)||1}" data-end="${(syms[0]&&syms[0].end_line)||40}">Open definition</button>
      <button type="button" data-wiki-slice="1" data-path="${esc(path)}" data-start="1" data-end="40">Read head</button>
      <button type="button" data-wiki-copy="1" data-path="${esc(path)}">Copy path</button>
    </div>
    <div class="wiki-slice" id="${id}_slice" style="display:none"><pre></pre></div>
  </div>`;
}
function renderGotoCard(g){
  const defs=g.definitions||[];
  const rows=defs.slice(0,12).map(d=>`
    <button type="button" class="wc-sym" data-wiki-open="1" data-path="${esc(d.path||'')}" data-name="${esc(d.name||g.name||'')}" data-start="${d.line||1}" data-end="${d.end_line||(d.line||1)}">
      <b>${esc(d.name||'?')}</b><em>${esc((d.path||'').split(/[/\\\\]/).pop()||'')} · L${d.line||'?'}–L${d.end_line||'?'} ${d.via?('· '+d.via):''}</em>
    </button>`).join('') || '<span style="color:var(--muted);font-size:12px">No definitions</span>';
  return `<div class="wiki-card">
    <div class="wc-head">
      <span class="wc-badge">Def</span>
      <div class="wc-title"><b>goto ${esc(g.name||'')}</b>
        <span>${defs.length} hit(s)${g.from_path ? (' · from ' + esc(String(g.from_path).split(/[/\\\\]/).pop() || '')) : ''}</span>
      </div>
    </div>
    <div class="wc-syms">${rows}</div>
  </div>`;
}
async function openWikiDefinition(path, name, start, end){
  if(!path){ toast('No path','err'); return; }
  const s=Number(start)||1, e=Number(end)|| (s+30);
  try{
    // Prefer goto when we have a name (cross-file)
    if(name){
      try{
        const g=await api('/v1/wiki/goto',{method:'POST',body:JSON.stringify({name, from_path:path})});
        const d=(g.definitions||[])[0];
        if(d && d.path){
          path=d.path; start=d.line||s; end=d.end_line||e;
        }
      }catch(_){}
    }
    const slice=await api('/v1/wiki/lines',{method:'POST',body:JSON.stringify({path, start:Number(start)||s, end:Number(end)||e})});
    if(!slice.ok){ toast(slice.error||'read failed','err'); return; }
    // Find nearest card slice pane or append under transcript
    let host=document.querySelector('.wiki-card[data-wiki-path="'+CSS.escape(path)+'"] .wiki-slice');
    if(!host){
      // last wiki-card slice or create ephemeral
      const cards=document.querySelectorAll('.wiki-card .wiki-slice');
      host=cards[cards.length-1]||null;
    }
    if(!host){
      const box=$('transcript');
      const wrap=document.createElement('div');
      wrap.className='wiki-slice';
      wrap.innerHTML='<pre></pre>';
      box.appendChild(wrap);
      host=wrap;
      box.scrollTop=box.scrollHeight;
    }
    host.style.display='block';
    const pre=host.querySelector('pre');
    if(pre) pre.textContent = (name?('// '+name+' @ '+path+'\n'):('// '+path+'\n'))+(slice.text||'');
    toast((name||'slice')+' · L'+(slice.start)+'–L'+(slice.end));
  }catch(e){ toast('Open definition: '+(e.message||e),'err'); }
}
// Event delegation for wiki card buttons
document.addEventListener('click', (ev)=>{
  const t=ev.target.closest('[data-wiki-open],[data-wiki-open-top],[data-wiki-slice],[data-wiki-copy]');
  if(!t) return;
  ev.preventDefault();
  const path=t.getAttribute('data-path')||'';
  const name=t.getAttribute('data-name')||'';
  const start=t.getAttribute('data-start')||'1';
  const end=t.getAttribute('data-end')||'40';
  if(t.hasAttribute('data-wiki-copy')){
    try{ navigator.clipboard.writeText(path); toast('Path copied'); }catch(_){ toast(path); }
    return;
  }
  if(t.hasAttribute('data-wiki-slice')){
    openWikiDefinition(path, '', start, end);
    return;
  }
  openWikiDefinition(path, name, start, end);
});
function saDotClass(w){
  const st=String(w.status||'idle').toLowerCase();
  if(/run|active|busy|queue|created/.test(st)) return 'run';
  if(/fail|error/.test(st)) return 'fail';
  if(/done|ok/.test(st)) return 'done';
  const src=String(w.source||'').toLowerCase();
  const name=String(w.name||w.id||'').toUpperCase();
  if(src==='harness') return 'run';
  if(src==='mesh'||MESH_AGENTS.includes(name)||name.includes('HEADLESS')||name==='DESIGN') return 'mesh';
  if(/ready|idle|catalog/.test(st)) return 'ready';
  return '';
}
function saSrcBadge(w){
  const name=String(w.name||w.id||'').toUpperCase();
  const src=String(w.source||'').toLowerCase();
  if(src==='harness') return '<span class="sa-src harness">harness</span>';
  if(name==='DESIGN'||name==='DESIGNER'||src==='design') return '<span class="sa-src design">design</span>';
  if(name.includes('HEADLESS')||src==='headless') return '<span class="sa-src headless">helper</span>';
  if(src==='latin'||LATIN_WORKERS.includes(name)) return '<span class="sa-src latin">core</span>';
  if(src==='mesh') return '<span class="sa-src headless">helper</span>';
  if(src==='dynamic'||src==='dispatch') return '<span class="sa-src">live</span>';
  return '';
}
function updateMeshChrome(){
  const cnt=$('saCount');
  const drive=$('meshDrive');
  const n=meshInfo.agent_count||0;
  if(cnt){
    cnt.textContent=String(n||subagentState.length||0);
    cnt.title=n?('Helpers: '+n):'Helpers';
  }
  if(drive){
    const root=String(meshInfo.mesh_root||'');
    const onE=/^E:/i.test(root)||String(meshInfo.drive||'').toUpperCase()==='E:';
    if(root){
      drive.style.display='inline-flex';
      drive.textContent=onE?'storage':(String(meshInfo.drive||'local')||'local');
      drive.className='mesh-pill'+(onE?'':' off');
      drive.title='Private storage on this computer';
      drive.title=root;
    } else {
      drive.style.display='none';
    }
  }
}
function renderSubagents(list){
  subagentState=Array.isArray(list)?list:[];
  const roster=$('subagentRoster');
  updateMeshChrome();
  if(roster){
    if(!subagentState.length){
      roster.innerHTML='<div class="rr-empty">Helpers idle — start a chat to use them</div>';
    } else {
      roster.innerHTML='';
      // Section: mesh core (DESIGN + headless) then live others
      const meshCore=subagentState.filter(w=>{
        const n=String(w.name||w.id||'').toUpperCase();
        const src=String(w.source||'');
        return MESH_AGENTS.includes(n)||src==='mesh'||src==='headless'||src==='design';
      });
      const live=subagentState.filter(w=>{
        const n=String(w.name||w.id||'').toUpperCase();
        const src=String(w.source||'');
        return !MESH_AGENTS.includes(n)&&src!=='mesh'&&src!=='headless'&&src!=='design';
      });
      const paint=(arr, label)=>{
        if(!arr.length) return;
        if(label){
          const sec=document.createElement('div');
          sec.className='rr-sec';
          sec.textContent=label;
          roster.appendChild(sec);
        }
        arr.forEach(w=>{
          const row=document.createElement('div');
          const st=String(w.status||'').toLowerCase();
          const running=/run|active|busy|queue/.test(st);
          const harness=String(w.source||'')==='harness';
          row.className='sa-row'+(running||harness&&running?' harness-run':'');
          const dot=saDotClass(w);
          const pulse=running?'<span class="sa-pulse" aria-hidden="true"></span>':'';
          row.innerHTML=`${pulse}<span class="sa-dot ${dot}"></span>${saSrcBadge(w)}<span class="sa-name">${esc(w.name||w.id||'?')}</span>
            <span class="sa-meta">${esc(w.goal||w.role||w.job||w.status||'')}${w.steps!=null?(' · '+w.steps):''}</span>`;
          roster.appendChild(row);
        });
      };
      // Harness (Codex/Grok/Claude spawned) first — animated when running
      const harness=subagentState.filter(w=>String(w.source||'')==='harness' || /run|active|busy/.test(String(w.status||'').toLowerCase()) && String(w.source||'')!=='latin');
      const coreOrder=MESH_AGENTS.slice();
      const orderedCore=[];
      coreOrder.forEach(id=>{
        const hit=meshCore.find(w=>String(w.name||w.id||'').toUpperCase()===id);
        if(hit) orderedCore.push(hit);
      });
      meshCore.forEach(w=>{
        const n=String(w.name||w.id||'').toUpperCase();
        if(!coreOrder.includes(n) && !orderedCore.includes(w)) orderedCore.push(w);
      });
      paint(harness.filter(w=>String(w.source||'')==='harness' || /run|active|busy/.test(String(w.status||'').toLowerCase())), harness.length?'Live harness':'');
      paint(orderedCore, orderedCore.length?'Mesh':'');
      paint(live.filter(w=>String(w.source||'')!=='harness'), live.length?'Active':'');
    }
  }
  // Live-refresh open inline accordions from current roster
  try{
    document.querySelectorAll('.subagents-panel[open] .sa-list').forEach(listEl=>{
      if(!subagentState.length) return;
      listEl.innerHTML='';
      subagentState.forEach(w=>{
        const row=document.createElement('div');
        row.className='sa-row';
        const dot=saDotClass(w);
        row.innerHTML=`<span class="sa-dot ${dot}"></span><span class="sa-name">${esc(w.name||w.id||'?')}</span>
          <span class="sa-meta">${esc(w.goal||w.role||w.status||'')}</span>`;
        listEl.appendChild(row);
      });
    });
  }catch(_){}
}
function renderWalkthrough(steps){
  walkthroughSteps=Array.isArray(steps)?steps.slice(-24):walkthroughSteps;
  const body=$('walkthroughBody');
  const c=$('wtCount');
  if(c) c.textContent=String(walkthroughSteps.length);
  if(!body) return;
  if(!walkthroughSteps.length){
    body.innerHTML='<div class="wt-empty">Steps appear as agents work.</div>';
    return;
  }
  body.innerHTML='';
  walkthroughSteps.forEach((st,i)=>{
    const d=document.createElement('div');
    const last=i===walkthroughSteps.length-1;
    d.className='wt-step '+(last?'on':'done');
    d.innerHTML=`<span class="wt-n">${i+1}</span><div><b style="font-weight:600;color:var(--fg)">${esc(st.agent||st.kind||'step')}</b>
      <div style="color:var(--muted);font-size:11px;margin-top:2px">${esc(st.message||'')}</div></div>`;
    body.appendChild(d);
  });
  body.scrollTop=body.scrollHeight;
}
async function pollSubagents(){
  const byName={};
  // Primary: unified registry GET /v1/subagents (latin + mesh DESIGN/headless + dynamic)
  try{
    const j=await api('/v1/subagents');
    const arr=j.subagents||j.workers||j.items||[];
    if(j.mesh && typeof j.mesh==='object'){
      meshInfo={
        agent_count:Number(j.mesh.agent_count||0)||0,
        mesh_root:String(j.mesh.mesh_root||''),
        drive:String(j.mesh.drive||'')
      };
    }
    if(Array.isArray(arr)){
      subagentCatalog=arr;
      arr.forEach(w=>{
        // Prefer canonical id (FORGE_HEADLESS) over display name
        const id=String(w.id||'').toUpperCase().replace(/\s+/g,'_');
        let name=String(w.name||w.id||'SUB').toUpperCase().replace(/\s+/g,'_');
        if(MESH_AGENTS.includes(id)) name=id;
        if(!name) return;
        const st=String(w.status||'').toLowerCase();
        const live=/run|active|busy|queue|created|done/.test(st);
        const src=String(w.source||'');
        // Always surface DESIGN + 4 headless + harness (Codex/Grok subagents) + live
        const isMeshCore=MESH_AGENTS.includes(name)||src==='mesh'||src==='headless'||src==='design'||src==='harness';
        if(live||isMeshCore){
          byName[name]={
            id:id||name, name,
            goal:w.goal||w.task||w.message||w.role||MESH_AGENT_ROLES[name]||'',
            status:live?(w.status||'running'):(w.status||'ready'),
            steps:w.steps, role:w.role, source:src||(isMeshCore?'mesh':'')
          };
        }
      });
    }
  }catch(_){}
  // Ensure DESIGN + 4 headless always appear even if registry soft-fails
  MESH_AGENTS.forEach(name=>{
    if(!byName[name]){
      byName[name]={
        id:name, name,
        goal:MESH_AGENT_ROLES[name]||'mesh',
        status:'ready',
        source:'mesh',
        role:MESH_AGENT_ROLES[name]||'mesh'
      };
    }
  });
  // Dynamic workers (extra live signal)
  try{
    const j=await api('/v1/workers/dynamic');
    (j.workers||[]).forEach(w=>{
      const name=String(w.name||w.id||'WORKER').toUpperCase();
      byName[name]={id:w.id,name,goal:w.goal||'',status:w.status||'running',steps:w.steps,source:'dynamic'};
    });
  }catch(_){}
  // Latin live daemon
  try{
    const j=await api('/v1/workers/live');
    const workers=j.workers||j.status||j.live||{};
    const list=Array.isArray(workers)?workers:Object.values(workers||{});
    const nowSec=Date.now()/1000;
    list.forEach(w=>{
      if(!w||typeof w!=='object') return;
      const name=String(w.id||w.name||'').toUpperCase();
      if(!name) return;
      const st=String(w.status||'idle').toLowerCase();
      const recent=w.last_at && (nowSec-Number(w.last_at))<120;
      if(/run|busy|active|queue/.test(st) || recent){
        byName[name]=byName[name]||{id:name,name,goal:w.last_job||'',status:w.status||'idle',steps:w.runs,source:'latin'};
        if(/run|busy|active|queue/.test(st)) byName[name].status=w.status;
        if(w.last_job) byName[name].goal=w.last_job;
      }
    });
  }catch(_){}
  // Mentions / dispatches from recent activity (override status → running)
  Object.keys(liveAgentHits).forEach(k=>{
    const hit=liveAgentHits[k];
    if(!hit||(Date.now()-hit.t)>120000) return;
    if(!byName[k]) byName[k]={id:k,name:k,goal:hit.message||'',status:hit.status||'running',source:'dispatch'};
    else {
      byName[k].status=hit.status||'running';
      if(hit.message) byName[k].goal=hit.message;
    }
  });
  // Fallback mesh status if not attached to /v1/subagents
  if(!meshInfo.mesh_root){
    try{
      const m=await api('/v1/mesh');
      if(m&&m.ok!==false){
        meshInfo={
          agent_count:Number(m.agent_count||0)||Object.keys(byName).length,
          mesh_root:String(m.mesh_root||''),
          drive:String(m.drive||'')
        };
      }
    }catch(_){}
  }
  if(!meshInfo.agent_count) meshInfo.agent_count=Object.keys(byName).length;
  renderSubagents(Object.values(byName));
}
async function pollLiveActions(){
  try{
    const j=await api('/v1/live/events?after='+liveSeq);
    const evs=j.events||[];
    if(!evs.length) return;
    const box=$('liveActions');
    evs.forEach(e=>{
      liveSeq=Math.max(liveSeq, e.seq||0);
      const agent=String(e.agent||e.kind||'').toUpperCase();
      const msg=String(e.message||'');
      // Track latin / mesh / named workers for subagent panel
      let hitName=agent;
      const known=LATIN_WORKERS.concat(MESH_AGENTS);
      if(!known.includes(hitName)){
        const found=known.find(w=>agent.includes(w)||msg.toUpperCase().includes(w));
        if(found) hitName=found;
      }
      if(hitName && (known.includes(hitName)||agent)){
        liveAgentHits[hitName||agent]={t:Date.now(),message:msg,status:'running',role:e.role||'host'};
      }
      walkthroughSteps.push({agent:e.agent||e.kind||'host', message:msg, kind:e.kind, ts:e.ts});
      if(box){
        const line=document.createElement('div');
        const role=(e.role||'host');
        const col=role==='llm'?'#fbbf24':(role==='python'?'#34d399':'#94a3b8');
        line.innerHTML=`<span style="color:var(--muted)">${esc(e.ts||'')}</span> <b style="color:${col}">${esc(e.agent||e.kind||'')}</b> <span style="color:var(--muted)">[${esc(role)}]</span> ${esc(msg)}`;
        box.appendChild(line);
      }
    });
    if(box){
      box.scrollTop=box.scrollHeight;
      while(box.children.length>80) box.removeChild(box.firstChild);
    }
    renderWalkthrough(walkthroughSteps);
    // refresh roster when workers chatter
    pollSubagents();
  }catch(_){}
}
async function pollLiveVision(){
  try{
    const j=await api('/v1/live/vision');
    if(j.base64){
      const img=$('liveVision');
      if(img) img.src='data:'+(j.mime||'image/jpeg')+';base64,'+j.base64;
      const m=$('liveVisionMeta');
      if(m) m.textContent='seq '+(j.seq||0)+' · OCULUS first-class';
    }
  }catch(_){}
}
async function refreshNodes(){
  try{
    const j=await api('/v1/node');
    const el=$('nodeStatus');
    if(el&&j&&j.me){
      el.innerHTML=`This device · <b style="color:var(--fg)">${esc(String((j.peers||[]).length))} paired</b>
        · ${esc(String(j.open_pair_codes||0))} open code(s)`;
    }
    const box=$('nodeOffers');
    if(box){
      const offs=j.offers||[];
      if(!offs.length) box.textContent='No shared files yet. Get a pair code for another device.';
      else box.innerHTML=offs.slice(0,6).map(o=>`<div style="margin:4px 0;padding:4px 0;border-top:1px solid var(--line)">
        <b style="color:var(--fg)">${esc(o.name||'?')}</b> · ${esc(String(o.bytes||0))} B
        ${o.claimed?' · received':' · <button type="button" class="icon" style="border:1px solid var(--line);padding:0 6px" onclick="nodeClaim(\''+esc(o.offer_id||'')+'\')">Receive</button>'}
      </div>`).join('');
    }
  }catch(e){ const el=$('nodeStatus'); if(el) el.textContent=String(e.message||e); }
}
async function nodeMintPair(){
  try{
    const j=await api('/v1/node/pair',{method:'POST',body:JSON.stringify({label:'device'})});
    if(!j.ok){ toast(j.error||'Could not create code','err'); return; }
    toast('Pair code '+j.code+' · expires in about 15 minutes','ok');
    try{ await navigator.clipboard.writeText(String(j.code||'')); }catch(_){}
    refreshNodes();
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function nodeOfferText(){
  const text=prompt('Note to send to a paired device:','');
  if(text==null||!String(text).trim()) return;
  try{
    const j=await api('/v1/node/offer',{method:'POST',body:JSON.stringify({name:'note.txt',text:String(text),note:'app'})});
    if(!j.ok){ toast(j.error||'Could not send','err'); return; }
    toast('Ready to receive: '+j.name,'ok');
    refreshNodes();
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function nodeClaim(id){
  if(!id) return;
  try{
    const j=await api('/v1/node/claim',{method:'POST',body:JSON.stringify({offer_id:id})});
    if(!j.ok){ toast(j.error||'Could not receive','err'); return; }
    let preview='';
    try{ preview=atob(j.data_b64||''); }catch(_){ preview='(file, '+j.bytes+' bytes)'; }
    toast('Received '+j.name,'ok');
    alert(j.name+'\n\n'+(preview||'').slice(0,2000));
    refreshNodes();
  }catch(e){ toast(String(e.message||e),'err'); }
}
let vmemLastSymbol='';
async function refreshVmem(){
  try{
    const st=await api('/v1/vmem');
    let arts=0;
    try{ const a=await api('/v1/vmem/artifacts?limit=5'); arts=(a.artifacts||[]).length; if(a.count!=null) arts=a.count; }catch(_){}
    const el=$('vmemStatus');
    if(el&&st){
      el.innerHTML=`<b style="color:var(--fg)">${esc(String(st.symbols||0))}</b> memories · <b style="color:var(--fg)">${esc(String(arts))}</b> artifacts · ${esc(String(st.pages||0))} pages`;
    }
    // Prefer agent artifacts when present, else recent
    let items=[];
    try{
      const a=await api('/v1/vmem/artifacts?limit=12');
      items=(a.artifacts||[]).map(x=>({symbol:x.symbol,bytes:x.bytes,preview:x.preview||x.note,kind:x.kind||'artifact'}));
    }catch(_){}
    if(!items.length){
      const rec=await api('/v1/vmem/recent');
      items=rec.recent||[];
    }
    const box=$('vmemList');
    if(box){
      if(!items.length) box.textContent='No memories yet — run Coding Swarm or Store a note';
      else {
        box.innerHTML='';
        items.slice(0,10).forEach(r=>{
          const row=document.createElement('div');
          row.style.cssText='margin:3px 0;padding:4px 0;border-top:1px solid var(--line);cursor:pointer';
          const badge=(r.kind==='artifact'||String(r.symbol||'').startsWith('artifacts/'))?' · artifact':'';
          row.innerHTML=`<b style="color:var(--fg)">${esc(r.symbol||'?')}</b>${badge} · ${esc(String(r.bytes||0))} B
            <div style="opacity:.85">${esc((r.preview||'').slice(0,90))}</div>`;
          row.onclick=()=>vmemOpen(r.symbol||'');
          box.appendChild(row);
        });
      }
    }
    const map=await api('/v1/vmem/map?size=256');
    const img=$('vmemMap');
    if(img&&map&&map.base64){
      img.style.display='block';
      img.src='data:'+(map.mime||'image/png')+';base64,'+map.base64;
    }
  }catch(e){ const el=$('vmemStatus'); if(el) el.textContent=String(e.message||e); }
}
async function vmemArtifacts(){
  try{
    const j=await api('/v1/vmem/artifacts?limit=30');
    const box=$('vmemList');
    const items=j.artifacts||[];
    if(box){
      if(!items.length) box.textContent='No agent artifacts yet — open Coding Swarm and give a coding task';
      else {
        box.innerHTML='';
        items.forEach(h=>{
          const row=document.createElement('div');
          row.style.cssText='margin:3px 0;padding:4px 0;border-top:1px solid var(--line);cursor:pointer';
          row.innerHTML=`<b style="color:#c084fc">${esc(h.symbol||'?')}</b>
            <div style="opacity:.85">${esc((h.note||h.preview||'').slice(0,100))}</div>`;
          row.onclick=()=>vmemOpen(h.symbol||'');
          box.appendChild(row);
        });
      }
    }
    toast((items.length||0)+' artifact(s)','ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemBringBack(){
  const sym=prompt('Bring back which pixel symbol into chat context?', vmemLastSymbol||'')||'';
  if(!sym.trim()) return;
  try{
    const j=await api('/v1/vmem/bring-back',{method:'POST',body:JSON.stringify({symbol:sym.trim()})});
    if(!j.ok){ toast(j.error||'Not found','err'); return; }
    vmemLastSymbol=j.symbol||sym.trim();
    const out=$('vmemLookOut');
    if(out){
      out.style.display='block';
      out.textContent=(j.text||j.preview||'').slice(0,6000);
    }
    // Inject into composer for the active agent
    const el=$('input');
    if(el && !el.disabled){
      const clip='\n\n[pixel bring-back `'+vmemLastSymbol+'`]\n'+(j.text||j.preview||'').slice(0,2500);
      el.value=(el.value||'')+clip;
      try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(_){}
    }
    if(j.pages&&j.pages[0]){
      const map=await api('/v1/vmem/map?page='+encodeURIComponent(j.pages[0])+'&size=256');
      const img=$('vmemMap');
      if(img&&map&&map.base64){ img.style.display='block'; img.src='data:'+(map.mime||'image/png')+';base64,'+map.base64; }
    }
    toast('Brought back '+vmemLastSymbol,'ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemStoreNote(){
  const text=prompt('What should memory store?','');
  if(text==null||!String(text).trim()) return;
  const sym=prompt('Name (so you can look it up later):', vmemLastSymbol||'work/note')||'';
  try{
    const j=await api('/v1/vmem/put',{method:'POST',body:JSON.stringify({text:String(text),symbol:sym,mesh:true,pass_to:'context'})});
    if(!j.ok){ toast(j.error||'Could not store','err'); return; }
    vmemLastSymbol=j.symbol||sym;
    toast('Stored '+vmemLastSymbol+' · '+(j.total_bytes||0)+' B','ok');
    refreshVmem();
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemStoreLastTurn(){
  try{
    const s=(sessions||[]).find(x=>x&&x.id===activeId)
      || (window.__activeSessCache&&window.__activeSessCache.id===activeId?window.__activeSessCache:null);
    const msgs=(s&&s.messages)||[];
    if(!msgs.length){ toast('No messages in this chat yet','err'); return; }
    // last user + last agent/assistant pair if possible
    let user='', agent='';
    for(let i=msgs.length-1;i>=0;i--){
      const m=msgs[i];
      const role=String(m.role||m.kind||'').toLowerCase();
      const text=m.text||m.content||m.body||'';
      if(!agent && (role==='assistant'||role==='agent'||role==='system'||m.engine)) agent=text;
      else if(!user && (role==='user'||role==='human')) user=text;
      if(user && agent) break;
    }
    if(!user && !agent){
      const last=msgs[msgs.length-1];
      agent=last.text||last.content||JSON.stringify(last).slice(0,2000);
    }
    const pack=[
      '# Pixel · last chat turn',
      'session: '+(activeId||''),
      'mode: '+(s&&s.mode||''),
      '',
      '## User',
      (user||'(none)').slice(0,6000),
      '',
      '## Agent',
      (agent||'(none)').slice(0,8000),
    ].join('\\n');
    const sym='chat/'+(activeId||'session').slice(0,12)+'/turn-'+Date.now().toString(36);
    const j=await api('/v1/vmem/put',{method:'POST',body:JSON.stringify({text:pack,symbol:sym,mesh:true,kind:'chat_turn',pass_to:'context'})});
    if(!j.ok){ toast(j.error||'Could not store','err'); return; }
    vmemLastSymbol=j.symbol||sym;
    toast('Stored last turn → '+vmemLastSymbol,'ok');
    refreshVmem();
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemOpen(sym){
  if(!sym) return;
  vmemLastSymbol=sym;
  try{
    const j=await api('/v1/vmem/look?symbol='+encodeURIComponent(sym));
    const out=$('vmemLookOut');
    if(out){
      out.style.display='block';
      out.textContent=(j.text||j.preview||JSON.stringify(j,null,2)||'').slice(0,4000);
    }
    if(j.pages&&j.pages[0]){
      const map=await api('/v1/vmem/map?page='+encodeURIComponent(j.pages[0])+'&size=256');
      const img=$('vmemMap');
      if(img&&map&&map.base64){ img.style.display='block'; img.src='data:'+(map.mime||'image/png')+';base64,'+map.base64; }
    }
    toast('Looking at '+sym,'ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemLook(){
  const sym=prompt('Look into which memory name?', vmemLastSymbol||'')||'';
  if(!sym.trim()){ refreshVmem(); return; }
  await vmemOpen(sym.trim());
}
async function vmemSearch(){
  const q=prompt('Search memories:','')||'';
  if(!q.trim()) return;
  try{
    const j=await api('/v1/vmem/search?q='+encodeURIComponent(q.trim()));
    const box=$('vmemList');
    const hits=j.hits||[];
    if(box){
      if(!hits.length) box.textContent='No matches for “'+q+'”';
      else {
        box.innerHTML='';
        hits.slice(0,10).forEach(h=>{
          const row=document.createElement('div');
          row.style.cssText='margin:3px 0;padding:3px 0;border-top:1px solid var(--line);cursor:pointer';
          row.innerHTML=`<b style="color:var(--fg)">${esc(h.symbol||'?')}</b> · score ${esc(String(h.score||0))}
            <div style="opacity:.85">${esc((h.preview||'').slice(0,80))}</div>`;
          row.onclick=()=>vmemOpen(h.symbol||'');
          box.appendChild(row);
        });
      }
    }
    toast(hits.length+' match(es)','ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemRecreate(){
  const sym=prompt('Recreate which memory into a file?', vmemLastSymbol||'')||'';
  if(!sym.trim()) return;
  try{
    const j=await api('/v1/vmem/recreate',{method:'POST',body:JSON.stringify({symbol:sym.trim(),export:true})});
    if(!j.ok){ toast(j.error||'Recreate failed','err'); return; }
    const out=$('vmemLookOut');
    if(out){
      out.style.display='block';
      out.textContent=(j.text||('(binary '+j.bytes+' B)')||'').slice(0,4000)
        + (j.export_path?'\n\nSaved: '+j.export_path:'');
    }
    if(j.pixel_map&&j.pixel_map.base64){
      const img=$('vmemMap');
      if(img){ img.style.display='block'; img.src='data:'+(j.pixel_map.mime||'image/png')+';base64,'+j.pixel_map.base64; }
    }
    vmemLastSymbol=sym.trim();
    toast('Recreated · '+(j.export_path||j.bytes+' B'),'ok');
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function vmemPass(){
  const sym=prompt('Pass which memory?', vmemLastSymbol||'')||'';
  if(!sym.trim()) return;
  const to=prompt('Pass to: context | agent | device | clipboard','context')||'context';
  try{
    const j=await api('/v1/vmem/pass',{method:'POST',body:JSON.stringify({symbol:sym.trim(),to:to.trim()})});
    if(!j.ok){ toast(j.error||'Pass failed','err'); return; }
    if(j.clipboard_text){
      try{ await navigator.clipboard.writeText(j.clipboard_text); toast('Copied to clipboard','ok'); }
      catch(_){ toast('Ready to copy — open Look for text','ok'); }
    } else if(j.offer&&j.offer.offer_id){
      toast('On device tray · offer '+j.offer.offer_id.slice(0,8),'ok');
    } else if(j.message_id){
      toast('Passed to helper','ok');
    } else {
      toast('Passed to '+to,'ok');
    }
    vmemLastSymbol=sym.trim();
    refreshVmem();
  }catch(e){ toast(String(e.message||e),'err'); }
}
async function visionObserve(){
  try{
    const j=await api('/v1/vision/understand');
    const el=$('visionOut'); if(el){ el.style.display='block';
      el.textContent=(j.primary_modality||'')+'\n'+(j.why_primary||'')+'\n\n'+(j.brief||'').slice(0,1200); }
    toast('Primary: '+(j.primary_modality||'?'));
  }catch(e){ toast(e.message); }
}
async function pixelText(){
  try{
    const j=await api('/v1/pixel/text');
    const el=$('visionOut'); if(el){ el.style.display='block'; el.textContent=(j.text||j.brief||'').slice(0,2000); }
    toast('Pixel→text · '+(j.primary_modality||''));
  }catch(e){ toast(e.message); }
}
async function fullPageRender(){
  try{
    toast('Full page render…');
    const j=await api('/v1/vision/page');
    const el=$('visionOut'); if(el){ el.style.display='block';
      el.textContent=(j.brief||'')+'\n\ncounts '+JSON.stringify(j.counts||{})+'\n\n'+(j.page_text||'').slice(0,2500); }
    toast('Symbols '+(j.counts&&j.counts.symbols||0)+' · '+(j.primary_modality||''));
  }catch(e){ toast(e.message); }
}
let _streamOn=false;
async function streamToggle(){
  try{
    if(!_streamOn){
      await api('/v1/vision/stream/start',{method:'POST',body:JSON.stringify({interval:1.5})});
      _streamOn=true; toast('Vision stream ON');
      pollStream();
    }else{
      await api('/v1/vision/stream/stop',{method:'POST',body:JSON.stringify({})});
      _streamOn=false; toast('Vision stream OFF');
    }
  }catch(e){ toast(e.message); }
}
let _streamAfter=0;
async function pollStream(){
  if(!_streamOn) return;
  try{
    const j=await api('/v1/vision/stream?after='+_streamAfter);
    const latest=j.latest||(j.frames&&j.frames[j.frames.length-1]);
    if(latest){
      _streamAfter=latest.seq||_streamAfter;
      const el=$('visionOut'); if(el){ el.style.display='block';
        el.textContent='STREAM #'+latest.seq+' · '+(latest.primary_modality||'')+'\n'+(latest.brief||'')+'\n\n'+(latest.page_text_head||'').slice(0,1800); }
      if(latest.seq) $('liveVisionMeta').textContent='stream seq '+latest.seq+' · '+(latest.page_hint||'');
    }
  }catch(_){}
  if(_streamOn) setTimeout(pollStream, 1600);
}
async function spawnDynamic(){
  const goal=prompt('Worker goal (dynamic AI-style, not a fixed script):','explore the current screen and scroll like a user');
  if(!goal) return;
  try{
    const j=await api('/v1/workers/spawn',{method:'POST',body:JSON.stringify({goal,name:'AUTON',max_steps:8})});
    toast(j.message||j.name||'spawned');
    const el=$('orchOut'); if(el){ el.style.display='block'; el.textContent=JSON.stringify(j,null,2).slice(0,4000); }
  }catch(e){ toast(e.message); }
}
async function orchChatSend(record){
  const t=($('orchChat')&&$('orchChat').value||'').trim();
  if(!t){ toast('Type a workflow'); return; }
  try{
    toast('Platform API running…');
    const j=await api('/v1/orchestrator/chat',{method:'POST',body:JSON.stringify({text:t,prompt:t,record:!!record})});
    const el=$('orchOut'); if(el){ el.style.display='block'; el.textContent=JSON.stringify(j.result||j,null,2).slice(0,5000); }
    toast((j.result&&j.result.message)||'done');
  }catch(e){ toast(e.message); }
}
async function runCampaign(){
  const t=($('orchChat')&&$('orchChat').value||'').trim()||'POCKET host co-pilot research campaign';
  try{
    toast('Campaign via platform API…');
    const j=await api('/v1/campaigns/run',{method:'POST',body:JSON.stringify({topic:t,record:true,commercial:true})});
    const el=$('orchOut'); if(el){ el.style.display='block'; el.textContent=JSON.stringify(j.campaign||j,null,2).slice(0,5000); }
    toast((j.campaign&&j.campaign.message)||'campaign done');
  }catch(e){ toast(e.message); }
}
let _livePollBusy=false;
async function _livePollTick(){
  // Skip when tab/app is backgrounded — multiple Edge --app windows were
  // hammering /v1/live/* every 900ms and killing the host under TIME_WAIT flood.
  if(document.hidden) return;
  if(_livePollBusy) return;
  _livePollBusy=true;
  try{
    await pollLiveActions();
    await pollLiveVision();
  }catch(_){}
  finally{ _livePollBusy=false; }
}
function ensureLivePoll(){
  if(liveTimer) return;
  // 3.5s is plenty for live feed; never stack overlapping polls
  liveTimer=setInterval(()=>{ _livePollTick(); }, 3500);
  _livePollTick();
  if(!subagentTimer){
    subagentTimer=setInterval(()=>{ if(!document.hidden) pollSubagents(); }, 5000);
    pollSubagents();
  }
  try{ refreshNodes(); refreshVmem(); }catch(_){}
}
async function sendMsg(){
  if(!activeId){ toast('Start or select a session first'); return; }
  let text=$('input').value.trim();
  if(!text) return;
  // Resolve /actions before send
  if(text.startsWith('/')){
    const sm=$('slashMenu'); if(sm){ sm.classList.remove('open'); sm.innerHTML=''; }
    if(/^\/(help|actions)\b/i.test(text)){
      const resolved=resolveSlash(text);
      $('input').value='';
      const box=$('transcript');
      if(box && !box.querySelector('.msg')) box.innerHTML='';
      if(box){
        const u=document.createElement('div'); u.className='msg user';
        u.innerHTML=`<div class="mb">${esc(text)}</div>`; box.appendChild(u);
        const a=document.createElement('div'); a.className='msg agent done';
        a.innerHTML=`<div class="mh"><span>pocket</span><span>done</span></div>
          <div class="mb prose">${lightMarkdown(resolved)}</div>`;
        box.appendChild(a);
        box.scrollTop=box.scrollHeight;
      }
      return;
    }
    text=resolveSlash(text);
  }
  $('sendBtn').disabled=true;
  closeComposerMenus();
  ensureLivePoll();
  let dispatchNote=null;
  try{
    // Always fire dispatch when @ is present (DESIGN / headless / Latin / any @NAME)
    if(hasAtMention(text) || parseMentions(text).length){
      dispatchNote=await dispatchMentions(text);
      if(dispatchNote.endpointMissing){
        console.info('POST /v1/subagents/dispatch not available yet — session message carries work');
        toast('Mesh dispatch offline — message still sent', 'err');
      }
      // toast + inline card handled inside dispatchMentions
    }
    const sendRes=await api('/v1/sessions/'+activeId+'/messages',{method:'POST',body:JSON.stringify({
      text,
      workspace:$('wsSelect').value||'workspace',
      device:DEVICE,
      interrupt:true
    })});
    if(sendRes && sendRes.superseded_jobs && sendRes.superseded_jobs.length){
      toast('Stopped prior turn · running latest prompt');
    }
    $('input').value='';
    if(DEVICE.kind==='phone') closeDrawers();
    await selectSess(activeId);
    // Re-attach clean dispatch card after transcript reload (avoid raw JSON dumps)
    if(dispatchNote && dispatchNote.dispatched && dispatchNote.dispatched.length && !dispatchNote.endpointMissing){
      showDispatchInline(dispatchNote.dispatched, dispatchNote.message);
    }
  }catch(e){ toast('Send failed: '+e.message, 'err'); }
  $('sendBtn').disabled=false;
  // Working board stays in sync after every turn
  if(isWorkSessionMode()){ try{ setTimeout(refreshWorkingBoard, 500); }catch(_){} }
}
/* Mic dual-path:
   - Regular chats = DICTATION only → text into the prompt box (never auto-send)
   - Voice ↔ Voice = patient VAD (1400ms) + auto-send + speak-back
*/
// Prefer same-origin proxy so Edge app never hits "API unreachable" (CORS / port down).
// Falls back to direct :8790 only if proxy fails.
const VOICE_API_DIRECT=(window.POCKET_VOICE_URL||'http://127.0.0.1:8790').replace(/\/$/,'');
const VOICE_API=(window.POCKET_VOICE_PROXY||(location.origin+'/v1/pocket-voice')).replace(/\/$/,'');
let micPartial='', micSilenceTimer=null, micLastSpeech=0, micVoiceApi=false, micFinalAt=0, micVoiceBase=VOICE_API;
function micIsDictation(){
  // Everything except specialized Voice ↔ Voice is dictation-into-box
  return !isVoiceSessionMode();
}
function micIsIncomplete(t){
  t=String(t||'').trim();
  if(!t) return true;
  if(/\b(um+|uh+|er+|hmm+|like|you know)\s*$/i.test(t)) return true;
  if(/\b(and|or|but|so|because|if|when|then|with|to|for|of|the|a|an)\s*$/i.test(t)) return true;
  if(/\d[\d\s\-.]{0,8}$/.test(t) && !/[.!?]$/.test(t)) return true;
  if(/[,:]\s*$/.test(t)) return true;
  if(t.length<12 && !/[.!?]$/.test(t)) return true;
  return false;
}
function micThresholdMs(){
  // Dictation: snappy so text lands in the box; Voice agent: patient 1400ms
  if(micIsDictation()) return 700;
  return 1400;
}
async function micShouldEnd(transcript, silenceMs){
  // Dictation never waits on "semantic incomplete" forever — just land text
  if(micIsDictation()){
    const thr=micThresholdMs();
    if(silenceMs<thr) return {end:false, reason:'silence_wait', threshold_ms:thr};
    return {end:true, reason:'dictation_silence', threshold_ms:thr};
  }
  // Voice ↔ Voice: hybrid patient decide via Pocket Voice API when live
  if(micVoiceApi){
    try{
      const decidePath=micVoiceBase.indexOf('pocket-voice')>=0?'/v1/turn/decide':'/v1/turn/decide';
      const r=await fetch(micVoiceBase+decidePath,{
        method:'POST',
        headers:Object.assign({'Content-Type':'application/json'},_voiceFetchHeaders()),
        body:JSON.stringify({transcript,silence_ms:silenceMs,scenario:'patient'})
      });
      if(r.ok){
        const j=await r.json();
        return {end:!!j.end, reason:j.reason||'', threshold_ms:j.threshold_ms||1400};
      }
    }catch(_){ micVoiceApi=false; }
  }
  const thr=micThresholdMs();
  if(silenceMs<thr) return {end:false, reason:'silence_wait', threshold_ms:thr};
  // Cap incomplete wait at 2.8s so turns never hang forever
  if(micIsIncomplete(transcript) && silenceMs<2800) return {end:false, reason:'semantic_incomplete', threshold_ms:thr};
  return {end:true, reason:'silence_threshold', threshold_ms:thr};
}
function micAppendToBox(chunk){
  const t=String(chunk||'').trim();
  if(!t) return false;
  const el=$('input');
  if(!el) return false;
  // Don't insert if disabled (signed out) — still allow when enabled
  const base=String(el.value||'').replace(/\s+$/,'');
  el.value=base?(base+' '+t):t;
  try{ el.dispatchEvent(new Event('input',{bubbles:true})); }catch(_){}
  try{ el.focus(); }catch(_){}
  // caret at end
  try{ const n=el.value.length; el.setSelectionRange(n,n); }catch(_){}
  return true;
}
function micCommitPartial(){
  const t=String(micPartial||'').trim();
  if(!t) return;
  const el=$('input');
  const ok=micAppendToBox(t);
  micPartial='';
  const hint=$('micInterim');
  if(hint){
    if(micIsDictation()){
      hint.textContent=ok?('In box · '+(el&&el.value?el.value.slice(-60):t.slice(-60))):'Could not write to box';
    }else hint.textContent='';
  }
  // ONLY Voice ↔ Voice auto-sends + barges TTS. Dictation never sends.
  if(!micIsDictation() && isVoiceSessionMode() && el && el.value.trim() && !$('sendBtn').disabled){
    try{
      const st=$('v2vStatus');
      if(st) st.textContent='Heard you — sending…';
      try{ if(window.speechSynthesis) window.speechSynthesis.cancel(); }catch(_){}
      sendMsg();
    }catch(_){}
  }else if(micIsDictation() && ok){
    // Feedback only in mic hint — no toast spam per phrase
  }
}
function micScheduleCommit(){
  if(micSilenceTimer) clearTimeout(micSilenceTimer);
  micSilenceTimer=setTimeout(async()=>{
    if(!micOn || !micPartial.trim()) return;
    // Use last FINAL speech time so interim pings don't block forever
    const silence=Date.now()-(micFinalAt||micLastSpeech||Date.now());
    const d=await micShouldEnd(micPartial, silence);
    if(d.end) micCommitPartial();
    else micScheduleCommit();
  }, micIsDictation()?120:180);
}
function ensureMicHint(){
  let h=$('micInterim');
  if(h) return h;
  // Prefer under composer box so dictation is always visible
  const host=document.querySelector('.composer-inner')||document.querySelector('.composer-bar')||document.querySelector('.composer');
  if(!host) return null;
  h=document.createElement('div');
  h.id='micInterim'; h.className='mic-interim';
  h.setAttribute('aria-live','polite');
  host.appendChild(h);
  return h;
}
function _voiceFetchHeaders(){
  const h={'Accept':'application/json'};
  try{
    const tok=sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token')||'';
    if(tok) h['Authorization']='Bearer '+tok;
  }catch(_){}
  return h;
}
async function probeVoiceApi(){
  // 1) Same-origin proxy (preferred for Edge --app)
  // 2) Direct :8790 fallback
  const attempts=[
    {base:VOICE_API, path:'/health'},
    {base:VOICE_API_DIRECT, path:'/health'},
  ];
  for(const a of attempts){
    try{
      const r=await fetch(a.base+a.path,{method:'GET',cache:'no-store',headers:_voiceFetchHeaders()});
      if(r.ok){
        micVoiceApi=true;
        micVoiceBase=a.base;
        return true;
      }
    }catch(_){}
  }
  // Ask host to wake voice service
  try{
    await fetch('/v1/pocket-voice/ensure',{
      method:'POST',
      headers:Object.assign({'Content-Type':'application/json'},_voiceFetchHeaders()),
      body:'{}'
    });
    await new Promise(res=>setTimeout(res,900));
    for(const a of attempts){
      try{
        const r2=await fetch(a.base+a.path,{method:'GET',cache:'no-store',headers:_voiceFetchHeaders()});
        if(r2.ok){ micVoiceApi=true; micVoiceBase=a.base; return true; }
      }catch(_){}
    }
  }catch(_){}
  micVoiceApi=false;
  return false;
}
let _micStream=null;
async function primeMicPermission(){
  // Edge app mode often needs an explicit getUserMedia grant before SpeechRecognition works
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia) return true;
  try{
    if(_micStream){
      try{ _micStream.getTracks().forEach(t=>t.stop()); }catch(_){}
      _micStream=null;
    }
    _micStream=await navigator.mediaDevices.getUserMedia({audio:true,video:false});
    // Keep track alive briefly so the OS marks the app as using mic; SR uses its own path
    return true;
  }catch(e){
    const name=(e&&e.name)||'';
    if(name==='NotAllowedError'||name==='PermissionDeniedError'){
      toast('Mic blocked — click the lock icon → allow microphone for 127.0.0.1','err');
      return false;
    }
    if(name==='NotFoundError'){
      toast('No microphone found','err');
      return false;
    }
    // Secure context / other — still try SpeechRecognition
    return true;
  }
}
function _micClearUi(){
  const b=$('micBtn');
  if(b){ b.classList.remove('hot'); b.classList.remove('mic-patient'); b.classList.remove('mic-dictation'); }
  const hint=$('micInterim'); if(hint) hint.textContent='';
  try{ if(_micStream){ _micStream.getTracks().forEach(t=>t.stop()); _micStream=null; } }catch(_){}
}
async function toggleMic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){
    toast('Mic needs Chromium speech — use Edge/Chrome, or open http://127.0.0.1:8787/desk','err');
    return;
  }
  // Secure context required for mic in modern Edge
  if(location.protocol==='http:' && location.hostname!=='127.0.0.1' && location.hostname!=='localhost'){
    toast('Mic requires localhost or HTTPS — open http://127.0.0.1:8787/desk','err');
    return;
  }
  const el=$('input');
  if(el && el.disabled){
    toast('Sign in first — then use the mic');
    return;
  }
  if(micOn){
    micOn=false;
    if(micSilenceTimer) clearTimeout(micSilenceTimer);
    if(micPartial.trim()) micCommitPartial();
    try{ if(micRec) micRec.stop(); }catch(_){}
    micRec=null;
    _micClearUi();
    try{ refreshProdPills(); }catch(_){}
    toast(micIsDictation()?'Dictation off':'Mic off');
    return;
  }
  const okPerm=await primeMicPermission();
  if(!okPerm) return;
  micOn=true; micPartial=''; micLastSpeech=Date.now(); micFinalAt=Date.now();
  const b=$('micBtn');
  if(b){
    b.classList.add('hot');
    b.classList.toggle('mic-patient', !micIsDictation());
    b.classList.toggle('mic-dictation', micIsDictation());
    b.disabled=false;
  }
  ensureMicHint();
  try{ refreshProdPills(); }catch(_){}
  if(micIsDictation()){
    toast('Dictation on · text goes into the box (not sent)');
    const hint=$('micInterim'); if(hint) hint.textContent='Dictation… speak, then pause — text lands in the box';
  }else{
    probeVoiceApi().then(ok=>{
      const hint=$('micInterim');
      try{ refreshProdPills(); }catch(_){}
      if(ok){
        toast('Aria listening · voice API ready · patient 1400ms');
        if(hint) hint.textContent='Listening (API '+String(micVoiceBase||'').replace(location.origin,'')+')…';
      }else{
        toast('Aria listening · local VAD (voice API offline — still works)');
        if(hint) hint.textContent='Listening locally… voice API offline (built-in timing)';
      }
    });
  }
  const startRec=()=>{
    if(!micOn) return;
    try{
      try{ if(micRec){ micRec.onend=null; micRec.stop(); } }catch(_){}
      micRec=new SR();
      micRec.lang='en-US';
      micRec.interimResults=true;
      micRec.continuous=true;
      micRec.maxAlternatives=1;
      micRec.onresult=(e)=>{
        let interim='', final='';
        for(let i=e.resultIndex;i<e.results.length;i++){
          const t=e.results[i][0].transcript||'';
          if(e.results[i].isFinal) final+=t;
          else interim+=t;
        }
        // Only final segments advance the silence clock (interim must not block commits)
        if(final){
          micFinalAt=Date.now();
          micLastSpeech=Date.now();
          const piece=final.trim();
          if(piece){
            // DICTATION: append finals immediately into the box so user always sees text
            if(micIsDictation()){
              micAppendToBox(piece);
              const hint=$('micInterim');
              if(hint) hint.textContent='In box · '+(interim?('…'+interim.slice(-40)):(''+(el&&el.value?el.value.slice(-50):piece.slice(-50))));
            }else{
              micPartial=(micPartial?micPartial+' ':'')+piece;
              if(micPartial) micScheduleCommit();
            }
          }
        }else if(interim){
          // interim only updates hint — does not reset dictation commit clock
          micLastSpeech=Date.now();
          const hint=$('micInterim');
          if(hint){
            if(micIsDictation()) hint.textContent='Hearing… '+interim.slice(-70);
            else{
              const show=((micPartial||'')+(interim?(' '+interim):'')).trim();
              hint.textContent=show?('Listening… '+show.slice(-90)):'Listening…';
            }
          }
        }
        // Voice path: schedule patient commit on partial buffer
        if(!micIsDictation() && micPartial) micScheduleCommit();
      };
      micRec.onerror=(ev)=>{
        const err=ev&&ev.error||'';
        const hard=['not-allowed','service-not-allowed','audio-capture'];
        if(hard.includes(err)){
          micOn=false;
          _micClearUi();
          toast(err==='not-allowed'
            ? 'Mic permission denied — allow mic for this site in Edge'
            : ('Mic: '+err),'err');
          return;
        }
        if(err==='network'){
          // Edge sometimes reports network when online SR backend glitches — retry
          const hint=$('micInterim');
          if(hint) hint.textContent='Mic reconnecting…';
          return;
        }
        // "no-speech" / "aborted" — keep listening
      };
      micRec.onend=()=>{
        if(micOn){
          setTimeout(()=>{ try{ if(micOn) startRec(); }catch(_){ } }, 220);
        } else _micClearUi();
      };
      micRec.start();
    }catch(e){
      if(String(e).indexOf('already')<0){
        toast('Mic start failed — try Edge settings → Site permissions → Mic','err');
        micOn=false;
        _micClearUi();
      }
    }
  };
  startRec();
}
async function uploadFiles(list){
  const ws=$('wsSelect').value||'workspace';
  const note=$('uploadNote');
  note.textContent='Uploading…';
  let ok=0, fail=0;
  for(const f of list){
    try{
      const b64=await fileToB64(f);
      const j=await api('/v1/files/upload',{method:'POST',body:JSON.stringify({workspace:ws,filename:f.name,content_base64:b64,size:f.size})});
      if(j.ok) ok++; else fail++;
    }catch(_){ fail++; }
  }
  note.textContent=`Uploaded ${ok}${fail?(' · failed '+fail):''} → ${ws}/uploads`;
  toast(note.textContent);
}
function fileToB64(file){
  return new Promise((res,rej)=>{
    const r=new FileReader();
    r.onload=()=>{ const s=String(r.result||''); const i=s.indexOf('base64,'); res(i>=0?s.slice(i+7):s); };
    r.onerror=rej; r.readAsDataURL(file);
  });
}
async function refreshLive(){
  try{
    const j=await api('/v1/live');
    const box=$('liveList'); box.innerHTML='';
    (j.services||[]).forEach(s=>{
      const d=document.createElement('div'); d.className='svc';
      const live=!!s.live;
      let acts='';
      if(s.url) acts+=`<a href="${s.url}" target="_blank">Open</a>`;
      if(s.connectable && !live) acts+=`<button type="button" data-id="${s.id}">Connect</button>`;
      d.innerHTML=`<div class="row"><b>${esc(s.name)}</b><span class="st ${live?'live':'down'}">${live?'LIVE':'DOWN'}</span></div><div class="act">${acts}</div>`;
      const btn=d.querySelector('button[data-id]');
      if(btn) btn.onclick=()=>connectOne(s.id);
      box.appendChild(d);
    });
  }catch(_){}
}
async function connectOne(id){
  try{ await api('/v1/live/connect',{method:'POST',body:JSON.stringify({service:id})}); toast('Connect requested'); setTimeout(refreshLive,1500);}catch(e){ toast(e.message); }
}
async function connectAll(){
  try{ await api('/v1/live/connect',{method:'POST',body:JSON.stringify({service:'all'})}); toast('Connecting services…'); setTimeout(refreshLive,2000);}catch(e){ toast(e.message); }
}
async function refreshUsage(){
  try{
    const u=await api('/v1/usage');
    if($('uTok')) $('uTok').textContent=(u.llm_tokens||u.est_tokens||0).toLocaleString();
  }catch(_){}
  try{
    const t=await api('/v1/tokenomics');
    const bal=(t.balance||0).toLocaleString();
    if($('uBal')) $('uBal').textContent=bal;
    if($('walletChip')) $('walletChip').textContent='POCK '+bal;
  }catch(_){}
  try{ await refreshEconomy(); }catch(_){}
  try{
    const p=await api('/v1/platform');
    const box=$('deployList'); if(!box) return;
    box.innerHTML='';
    (p.deploys||[]).filter(d=>d.status==='running').forEach(d=>{
      const row=document.createElement('div');
      row.style.margin='4px 0';
      row.innerHTML=`<a href="${d.url_local||'#'}" target="_blank">${esc(d.title||d.id)}</a> <span>${d.kind||''}</span> `;
      if(d.id && d.log_path){
        const b=document.createElement('button'); b.type='button'; b.textContent='logs'; b.className='icon';
        b.onclick=async()=>{ const lg=await api('/v1/deploys/'+d.id+'/log'); const el=$('deployLog'); el.style.display='block'; el.textContent=lg.log_tail||'(empty)'; };
        row.appendChild(b);
      }
      box.appendChild(row);
    });
    if(!(p.deploys||[]).filter(d=>d.status==='running').length) box.textContent='No live deploys';
  }catch(_){}
}
async function refreshEconomy(){
  try{
    const e=await api('/v1/economy');
    if(!e||!e.ok) return;
    const op=e.operator||{};
    const bal=Number(op.balance||0);
    if($('econOp')) $('econOp').textContent=bal.toLocaleString()+' '+(e.unit||'POCK');
    if($('econTwinPool')) $('econTwinPool').textContent=Number(e.twin_total||0).toLocaleString();
    if($('econEscrow')) $('econEscrow').textContent=Number(e.escrow_locked||0).toLocaleString();
    const rail=(e.settlement_rail||'paper').toLowerCase();
    const railEl=$('econRail');
    if(railEl){
      railEl.textContent=rail;
      railEl.className='econ-rail'+(rail==='paper'?' paper':'');
    }
    if($('uBal')) $('uBal').textContent=bal.toLocaleString();
    if($('walletChip')) $('walletChip').textContent='POCK '+bal.toLocaleString();
    const box=$('econTwins');
    if(box){
      const twins=(e.twins||[]).slice(0,8);
      box.innerHTML=twins.map(t=>
        `<span class="econ-twin" title="${esc(t.label||t.agent_id||'')}">${esc((t.agent_id||t.id||'').replace(/^twin_/,''))}<strong>${Number(t.balance||0).toLocaleString()}</strong></span>`
      ).join('')||'<span class="hint">No twin wallets yet</span>';
    }
    const px=e.parallax||{};
    if($('econHint')){
      $('econHint').textContent=px.bridge_enabled
        ?('Parallax bridge on · '+(px.mode||'paper')+(px.workspace_exists?' · workspace ok':''))
        :'Paper-first · enable Parallax bridge for live rails';
    }
  }catch(_){}
}
async function economyTopup(){
  try{
    await api('/v1/economy/mint',{method:'POST',body:JSON.stringify({wallet:'wallet_operator',amount:1000,reason:'desk_topup'})});
    toast('Minted 1,000 POCK to operator');
    await refreshEconomy();
  }catch(e){ toast(e.message||'Mint failed','err'); }
}
async function economySyncParallax(){
  try{
    toast('Syncing Parallax AI wallets…');
    const j=await api('/v1/economy/parallax',{method:'POST',body:JSON.stringify({enabled:true,mode:'paper',sync:true})});
    const s=j.sync||{};
    const n=s.export_count!=null?s.export_count:(j.parallax&&j.parallax.ai_wallet_package_exists? 'ok':'');
    toast(s.ok!==false?('Parallax sync · '+n+' AI wallets · chain '+(s.receipt_chain_valid?'valid':'?')):'Sync failed');
    await refreshEconomy();
  }catch(e){ toast(e.message||'Parallax sync failed','err'); }
}
window.refreshEconomy=refreshEconomy;
window.economyTopup=economyTopup;
window.economySyncParallax=economySyncParallax;
async function deployKind(kind){
  try{
    const ws=$('wsSelect').value||'workspace';
    const j=await api('/v1/deploy',{method:'POST',body:JSON.stringify({kind,workspace:ws,title:ws+'-'+kind})});
    if(j.ok){
      if(j.url_local) window.open(j.url_local,'_blank');
      toast((kind)+' deploy ready');
      if(j.id){ try{ const lg=await api('/v1/deploys/'+j.id+'/log'); const el=$('deployLog'); el.style.display='block'; el.textContent=lg.log_tail||''; }catch(_){ } }
      refreshUsage();
    } else toast(j.error||'deploy failed');
  }catch(e){ toast('Deploy: '+e.message); }
}
async function openDoc(key){
  try{
    const j=await api('/v1/docs/'+key);
    const text=j.text||JSON.stringify(j,null,2);
    const w=window.open('','_blank');
    w.document.write('<pre style="white-space:pre-wrap;font:13px/1.45 ui-monospace,monospace;padding:16px;background:#0a0a0b;color:#e4e4e7">'+esc(text)+'</pre>');
  }catch(e){ toast('Doc failed: '+e.message); }
}
async function grokPull(){
  try{
    await api('/v1/grok/pull',{method:'POST',body:JSON.stringify({prompt:'Full status pull with research plan'})});
    toast('Research pull written');
  }catch(e){ toast(e.message); }
}
async function runDoctor(){
  try{
    let j;
    try{ j=await api('/v1/ready'); }catch(_){ j=await api('/v1/doctor'); }
    const el=$('doctorOut');
    el.style.display='block';
    if(j.items){
      el.textContent = 'POCKET '+j.version+' production '+j.ready_score+'\n'+
        'trust: '+(j.trust_model||'')+'\n'+
        (j.items||[]).map(c=>(c.ok?'OK ':'-- ')+c.id+' '+c.name+(c.detail?(' · '+c.detail):'')).join('\n');
    } else {
      el.textContent = 'POCKET '+j.version+' ready '+j.ready_score+'\n'+
        (j.checks||[]).map(c=>(c.ok?'OK ':'-- ')+c.name+' '+(c.detail||'')).join('\n');
    }
    toast('Ready '+(j.ready_score||''));
  }catch(e){ toast(e.message); }
}
async function quickDesktop(){
  try{
    await newSess('desktop');
    $('input').value='open notepad';
    await sendMsg();
  }catch(e){ toast(e.message); }
}
async function quickWeb(){
  try{
    await newSess('web');
    $('input').value='search multi agent desktop AI platforms';
    await sendMsg();
  }catch(e){ toast(e.message); }
}
async function quickNexus(){
  try{
    await newSess('nexus');
    $('input').value='list';
    await sendMsg();
  }catch(e){ toast(e.message); }
}
async function loadAiCatalog(){
  try{
    const j=await api('/v1/ai');
    const el=$('aiOut'); el.style.display='block';
    const agents=(j.agents||[]).map(a=>`${a.id} · ${a.tier} · ${a.pock} POCK · $${a.usd_hint}`).join('\n');
    el.textContent='POCKET AI API '+((j.product&&j.product.version)||'')+'\n'+
      'Sell starter $'+(j.sell&&j.sell.starter_usd)+' / pro $'+(j.sell&&j.sell.pro_usd)+'\n\n'+agents;
    toast('AI catalog loaded');
  }catch(e){ toast(e.message); }
}
async function createApiKey(){
  try{
    const j=await api('/v1/ai/keys',{method:'POST',body:JSON.stringify({name:'desk-'+Date.now(),tier:'pro'})});
    const el=$('aiOut'); el.style.display='block';
    el.textContent='API KEY (copy now — shown once):\n'+(j.key||'')+'\n\n'+
      (j.auth_header||'')+'\n\nid='+j.id+' tier='+j.tier;
    if(j.key){ try{ await navigator.clipboard.writeText(j.key); toast('API key copied'); }catch(_){ toast('API key created — copy from panel'); } }
    else toast(j.error||'key failed');
  }catch(e){ toast(e.message); }
}
async function runHeadless(agentId){
  try{
    const task=prompt('Task for headless agent "'+agentId+'":','')||'';
    if(!task) return;
    toast('Running '+agentId+'…');
    const j=await api('/v1/ai/agents/'+agentId+'/run',{method:'POST',body:JSON.stringify({task,sync:true,device:DEVICE})});
    const el=$('aiOut'); el.style.display='block';
    const body=typeof j.result==='string'?j.result:JSON.stringify(j.result||j,null,2);
    el.textContent='agent='+agentId+' ok='+j.ok+' status='+j.status+'\n\n'+(body||j.error||'').slice(0,6000);
    toast(j.ok?'Done '+agentId:'Failed '+agentId);
  }catch(e){ toast(e.message); }
}
function esc(s){return String(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}

// Login bindings — null-safe so a missing node never kills the rest of the desk JS
(function bindLogin(){
  const form=$('loginForm');
  if(form) form.addEventListener('submit',e=>{ e.preventDefault(); doLogin(); });
  const lb=$('loginBtn');
  if(lb){ lb.onclick=function(e){ if(e) e.preventDefault(); doLogin(); }; }
  const rb=$('regBtn');
  if(rb) rb.onclick=doRegister;
  const lp=$('loginPass');
  if(lp) lp.onkeydown=e=>{ if(e.key==='Enter'){ e.preventDefault(); doLogin(); } };
  const lub=$('localUnlockBtn');
  if(lub) lub.onclick=async()=>{
    setLoginErr('Unlocking this PC…');
    const ok=await tryDesktopAutoLogin(true);
    if(!ok) setLoginErr('Local unlock failed — is host running on :8787?');
  };
  // Expose for inline handlers
  window.doLogin=doLogin;
  window.doRegister=doRegister;
  window.setAuthTab=setAuthTab;
})();
const _inputEl=$('input');
if(_inputEl){
  _inputEl.addEventListener('keydown',e=>{
    if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){ e.preventDefault(); sendMsg(); }
    // Phone: Enter sends (Shift+Enter newline)
    if(e.key==='Enter' && !e.shiftKey && DEVICE.kind==='phone'){ e.preventDefault(); sendMsg(); }
    if(e.key==='Escape'){ closeComposerMenus(); }
    // Tab accepts first @mention suggestion
    if(e.key==='Tab'){
      const mm=$('mentionMenu');
      if(mm&&mm.classList.contains('open')){
        const first=mm.querySelector('button');
        if(first){ e.preventDefault(); first.click(); }
      }
    }
  });
  _inputEl.addEventListener('input',()=>{ updateMentionMenu(); updateSlashMenu(); });
}
const _fileIn=$('fileInput');
if(_fileIn) _fileIn.onchange=()=>{ const f=$('fileInput').files; if(f&&f.length) uploadFiles(f); $('fileInput').value=''; };
const _modelPick=$('modelPick');
if(_modelPick){
  _modelPick.addEventListener('change', async()=>{
    _modelPick.dataset.userSet='1';
    const mode=_modelPick.value;
    if(!mode) return;
    try{ await pickAgent(mode); }catch(e){ toast(e.message||'switch failed'); }
  });
}
// Close agent picker when clicking outside
document.addEventListener('click',(e)=>{
  const wrap=$('agentPickWrap');
  if(!wrap) return;
  if(!wrap.contains(e.target)) closeAgentPicker();
});
// Empty-state + any [data-mode] chip uses pickAgent (bubbles from nested <b>/<small>)
document.addEventListener('click',(e)=>{
  const t=e.target && e.target.closest && e.target.closest('[data-mode]');
  if(!t) return;
  // don't steal clicks from real form controls
  if(t.tagName==='SELECT'||t.tagName==='OPTION'||t.tagName==='TEXTAREA'||t.tagName==='INPUT') return;
  const mode=t.getAttribute('data-mode');
  if(!mode) return;
  e.preventDefault();
  e.stopPropagation();
  pickAgent(mode);
});
// Safety: if gate/scrim stuck, Escape dismisses blockers
// Agent picker: ↑ ↓ Enter Escape
document.addEventListener('keydown',(e)=>{
  const menu=$('agentPickMenu');
  const pickerOpen=menu && menu.classList.contains('open');
  if(pickerOpen){
    if(e.key==='ArrowDown'){ e.preventDefault(); apKbMove(1); return; }
    if(e.key==='ArrowUp'){ e.preventDefault(); apKbMove(-1); return; }
    if(e.key==='Enter'){
      // only hijack Enter when a row is highlighted (search box can still submit selection)
      if(_apKbIndex>=0){ e.preventDefault(); apKbActivate(); return; }
    }
    if(e.key==='Escape'){ e.preventDefault(); closeAgentPicker(); return; }
  }
  if(e.key==='Escape'){
    try{ hideGate(); closeDrawers(); closeAgentPicker(); dismissBootSplash(true); }catch(_){}
  }
});
// Re-render picker filter resets keyboard index
document.addEventListener('input',(e)=>{
  if(e.target && e.target.id==='agentPickSearch'){
    _apKbIndex=-1;
    renderAgentPicker();
  }
});
// Prefill from Work Studio handoff
try{
  const handoff=localStorage.getItem('pocket_work_handoff');
  if(handoff){
    const h=JSON.parse(handoff);
    localStorage.removeItem('pocket_work_handoff');
    window.__pocketHandoff=h;
  }
}catch(_){}

// Device awareness: detect early + re-check on rotate/resize
detectDevice();
applyDevice();
let _devResizeT=null;
window.addEventListener('resize',()=>{
  clearTimeout(_devResizeT);
  _devResizeT=setTimeout(()=>{ detectDevice(); applyDevice(); }, 200);
});
window.addEventListener('orientationchange',()=>{ setTimeout(()=>{ detectDevice(); applyDevice(); }, 300); });

// boot — then honor ?agent=mesie|nexus|auro from landing cards
boot().then(async()=>{
  // Load full first-class agent catalog (every agent elevated)
  try{ await loadFirstClassCatalog(); }catch(_){}
  // Agent OS deep-link: open a mode after landing on desk
  try{
    const m=sessionStorage.getItem('pocket_os_mode');
    if(m){ sessionStorage.removeItem('pocket_os_mode'); setTimeout(()=>pickAgent(m), 400); }
  }catch(_){}
  try{
    const q=new URLSearchParams(location.search||'');
    const agent=(q.get('agent')||'').toLowerCase();
    const authed=sessionStorage.getItem('pocket_token')||localStorage.getItem('pocket_token');
    if(agent && authed){
      const map={
        mesie:'mesie',nexus:'nexus',auro:'auro',auro14b:'auro',ro14b:'auro',
        grok:'grok',codex:'codex',claude:'claude',build:'build',wiki:'wiki',
        dual:'dual',swarm:'swarm',assist:'assist',assistant:'assist',
        muse:'muse_spark',muse_spark:'muse_spark',spark:'muse_spark',
        work:'work',working:'work',voice:'voice',plan:'plan',
        genetic:'genetic',genetic_flow:'genetic',internal:'genetic',internal_models:'genetic',
        mail:'assist'
      };
      const mode=map[agent]||agent;
      await pickAgent(mode);
    }
    // Work Studio → desk handoff: start agent + fill prompt
    const h=window.__pocketHandoff;
    if(h && authed){
      const handMap={assist:'assist',assistant:'assist',digital:'assist',muse:'muse_spark',spark:'muse_spark'};
      const mode=handMap[(h.mode||'').toLowerCase()]||h.mode||'assist';
      if(mode) await pickAgent(mode);
      if(h.voice && activeId){
        try{ await api('/v1/sessions/'+activeId+'/voice-engine',{method:'POST',body:JSON.stringify({enabled:true})}); paintVoiceEngineBtn(true); updateMicChrome(mode); }catch(_){}
      }
      if(h.prompt && $('input')){
        $('input').value=h.prompt;
        $('input').disabled=false;
        if($('sendBtn')) $('sendBtn').disabled=false;
        try{ $('input').focus(); }catch(_){}
        toast('From Work Studio — review and Send','ok');
      }
    }
  }catch(_){}
  try{ ensureAiWorkspacePoll(); refreshAiWorkspace(); renderAgentPicker(); }catch(_){}
});
</script>
</body>
</html>
"""
