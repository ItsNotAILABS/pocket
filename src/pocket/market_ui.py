"""Customer join — the sold POCKET first-run (not the founder gate)."""

from __future__ import annotations

from pocket.market import COMMERCIAL_LICENSE, SOLD_VERSION, catalog


def join_html() -> str:
    plans = catalog()["plans"]
    cards = []
    for p in plans:
        if p.get("consumable"):
            blurb = f"{int(p['pock_monthly']):,} POCK one-time"
        else:
            blurb = f"{p['seats']} seat{'s' if p['seats']!=1 else ''} · {int(p['pock_monthly']):,} POCK / mo"
        cards.append(
            f"""<button type="button" class="plan" data-plan="{p['id']}">
  <b>{p['name']}</b>
  <span class="price">${p['usd']}</span>
  <small>{blurb}</small>
</button>"""
        )
    plan_html = "\n".join(cards)
    lic = COMMERCIAL_LICENSE
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Join POCKET</title>
<meta name="description" content="Create your POCKET seat. Your files, your password, your plan."/>
<meta name="theme-color" content="#09090b"/>
<script src="/auth/client.js"></script>
<style>
:root{{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.08);--text:#e4e4e7;--muted:#71717a;--fg:#fafafa;--accent:#10a37f;--ease:cubic-bezier(.22,1,.36,1)}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(1000px 480px at 10% -12%,rgba(16,163,127,.12),transparent 52%),var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}}
.pnav{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid var(--line);background:rgba(9,9,11,.78);backdrop-filter:blur(22px)}}
.pnav a{{color:#a1a1aa;text-decoration:none;font-size:13px;padding:7px 11px;border-radius:8px}}
.pnav a.on,.pnav a:hover{{color:#fff;background:#1a1a1e}}
.brand{{display:flex;align-items:center;gap:8px;color:#fff;font-weight:700;text-decoration:none}}
.brand i{{width:22px;height:22px;border-radius:7px;background:linear-gradient(145deg,#34d399,#10a37f);display:grid;place-items:center;font-style:normal;color:#041;font-size:11px;font-weight:800}}
.wrap{{max-width:720px;margin:0 auto;padding:36px 18px 88px}}
h1{{letter-spacing:-.045em;font-size:clamp(28px,4vw,40px);margin:0 0 8px;color:var(--fg)}}
.lead{{color:var(--muted);max-width:520px;line-height:1.55;margin:0 0 28px}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:0 0 22px}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
.plan{{text-align:left;border:1px solid var(--line);background:linear-gradient(165deg,rgba(255,255,255,.04),transparent 50%),var(--panel);color:inherit;border-radius:14px;padding:14px 16px;cursor:pointer;transition:border-color .2s var(--ease),transform .2s var(--ease)}}
.plan:hover,.plan.on{{border-color:rgba(16,163,127,.5);transform:translateY(-1px)}}
.plan b{{display:block;color:var(--fg)}}
.plan .price{{display:block;font-size:22px;font-weight:750;letter-spacing:-.03em;margin:6px 0 4px}}
.plan small{{color:var(--muted)}}
.card{{border:1px solid var(--line);border-radius:16px;padding:18px;background:var(--panel);margin-bottom:14px}}
label{{display:block;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px}}
input{{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);font:inherit}}
.row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}
.btn{{border:0;border-radius:10px;padding:11px 16px;font-weight:750;cursor:pointer;background:linear-gradient(180deg,#34d399,#10a37f);color:#041}}
.btn.ghost{{background:transparent;border:1px solid var(--line);color:var(--fg)}}
.err{{color:#f87171;font-size:13px;min-height:18px;margin-top:8px}}
.ok{{color:#6ee7b7}}
.hint{{font-size:12px;color:var(--muted);line-height:1.5}}
.terms{{display:flex;gap:8px;align-items:flex-start;font-size:12.5px;color:var(--muted);margin-top:12px}}
#license{{font-size:13px;color:var(--muted);line-height:1.55}}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/"><i>P</i>POCKET</a>
  <a class="on" href="/join">Join</a>
  <a href="/billing">Plans</a>
  <a href="/download">Download</a>
  <a href="/desk">Sign in</a>
</header>
<main class="wrap">
  <h1>Create your account</h1>
  <p class="lead">Sign up with your own username and password. An invite key is optional. You never use the operator login. Sold v{SOLD_VERSION}.</p>

  <div class="grid" id="plans">{plan_html}</div>

  <div class="card">
    <label for="user">Username</label>
    <input id="user" autocomplete="username" placeholder="pick a username"/>
    <label for="invite">Invite key (optional) <code>pk_seat_…</code></label>
    <input id="invite" autocomplete="off" spellcheck="false" placeholder="skip if you do not have one"/>
    <label for="display">Display name</label>
    <input id="display" placeholder="How agents greet you"/>
    <label for="pass">Password (min 8)</label>
    <input id="pass" type="password" autocomplete="new-password"/>
    <label for="pass2">Confirm password</label>
    <input id="pass2" type="password" autocomplete="new-password"/>
    <label class="terms"><input type="checkbox" id="terms"/> I accept the <a href="#license" style="color:#6ee7b7">{lic['title']}</a> and will not use the owner login.</label>
    <div class="err" id="err"></div>
    <div class="row">
      <button type="button" class="btn" id="go">Create my account</button>
      <a class="btn ghost" href="/login">I already have an account</a>
    </div>
    <p class="hint" style="margin-top:12px">After you join, open Desk. Your files stay in your tenant. Host desktop and founder folders stay locked.</p>
  </div>

  <div class="card" id="license">
    <b style="color:var(--fg)">{lic['title']}</b>
    <p>{lic['summary']}</p>
  </div>
</main>
<script>
let plan = 'pocket_pro';
document.querySelectorAll('.plan').forEach(el => {{
  if (el.dataset.plan === plan) el.classList.add('on');
  el.onclick = () => {{
    plan = el.dataset.plan;
    document.querySelectorAll('.plan').forEach(x => x.classList.toggle('on', x === el));
  }};
}});
(function(){{
  try {{
    const q = new URLSearchParams(location.search);
    const inv = q.get('invite') || q.get('seat') || q.get('code');
    if (inv && !document.getElementById('invite').value) document.getElementById('invite').value = inv;
  }} catch (_) {{}}
}})();
document.getElementById('go').onclick = async () => {{
  const err = document.getElementById('err');
  err.textContent = '';
  err.className = 'err';
  const p1 = document.getElementById('pass').value;
  const p2 = document.getElementById('pass2').value;
  if (p2 && p1 !== p2) {{ err.textContent = 'Passwords do not match.'; return; }}
  if (!document.getElementById('terms').checked) {{ err.textContent = 'Accept the commercial license.'; return; }}
  document.getElementById('go').disabled = true;
  try {{
    let j;
    if (window.PocketAuth && PocketAuth.register) {{
      j = await PocketAuth.register({{
        invite: document.getElementById('invite').value.trim(),
        user: document.getElementById('user').value.trim(),
        password: p1,
        password2: p2,
        display: document.getElementById('display').value.trim(),
        accepted_terms: true,
        plan,
        channel: (document.getElementById('invite').value.trim() ? 'sold' : 'public'),
        device: 'join'
      }});
    }} else {{
      const r = await fetch('/v1/auth/register', {{method:'POST', credentials:'same-origin', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{
        invite: document.getElementById('invite').value.trim(),
        user: document.getElementById('user').value.trim(),
        password: p1,
        display: document.getElementById('display').value.trim(),
        plan,
        accepted_terms: true,
        channel: (document.getElementById('invite').value.trim() ? 'sold' : 'public')
      }})}});
      j = await r.json();
    }}
    if (!j.ok) {{ err.textContent = j.error || 'Could not create seat'; document.getElementById('go').disabled = false; return; }}
    if (window.PocketAuth && j.token) PocketAuth.storeSession(j.user, j.token);
    err.className = 'err ok';
    err.textContent = 'Seat ready. Opening desk…';
    location.href = '/desk?authed=1';
  }} catch (e) {{
    err.textContent = String(e.message || e);
    document.getElementById('go').disabled = false;
  }}
}};
</script>
</body></html>
"""


def seats_html() -> str:
    """Owner console — mint pk_seat_ keys and see members. This is how you sell."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>POCKET · Seats</title>
<script src="/auth/client.js"></script>
<style>
:root{--bg:#09090b;--panel:#141416;--line:rgba(255,255,255,.08);--text:#e4e4e7;--muted:#71717a;--fg:#fafafa;--accent:#10a37f;--ease:cubic-bezier(.22,1,.36,1)}
*{box-sizing:border-box}
body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif;background:radial-gradient(900px 400px at 0% 0%,rgba(16,163,127,.1),transparent 50%),var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}
.pnav{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:12px 18px;border-bottom:1px solid var(--line);background:rgba(9,9,11,.78);backdrop-filter:blur(22px)}
.pnav a{color:#a1a1aa;text-decoration:none;font-size:13px;padding:7px 11px;border-radius:8px}
.pnav a.on,.pnav a:hover{color:#fff;background:#1a1a1e}
.brand{display:flex;align-items:center;gap:8px;color:#fff;font-weight:700;text-decoration:none}
.brand i{width:22px;height:22px;border-radius:7px;background:linear-gradient(145deg,#34d399,#10a37f);display:grid;place-items:center;font-style:normal;color:#041;font-size:11px;font-weight:800}
.wrap{max-width:880px;margin:0 auto;padding:32px 18px 80px}
h1{letter-spacing:-.04em;margin:0 0 8px}
.lead{color:var(--muted);max-width:560px;line-height:1.5}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:22px}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
.card{border:1px solid var(--line);border-radius:16px;padding:16px;background:linear-gradient(165deg,rgba(255,255,255,.035),transparent 48%),var(--panel)}
label{display:block;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px}
input{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:#0c0c0e;color:var(--fg);font:inherit}
.btn{border:0;border-radius:10px;padding:10px 14px;font-weight:750;cursor:pointer;background:linear-gradient(180deg,#34d399,#10a37f);color:#041;margin-top:12px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--fg)}
.key{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:#86efac;background:#050506;border:1px dashed rgba(16,163,127,.4);border-radius:10px;padding:12px;word-break:break-all;display:none;margin-top:12px}
.row{display:flex;justify-content:space-between;gap:8px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:13px}
.row:last-child{border:0}
.muted{color:var(--muted);font-size:12px}
.err{color:#f87171;font-size:13px;margin-top:8px}
</style>
</head>
<body>
<header class="pnav">
  <a class="brand" href="/desk"><i>P</i>POCKET</a>
  <a class="on" href="/seats">Seats</a>
  <a href="/join">Join (customer)</a>
  <a href="/billing">Billing</a>
  <a href="/desk">Desk</a>
</header>
<main class="wrap">
  <h1>Sell seats</h1>
  <p class="lead">Mint a <code>pk_seat_</code> key, send the customer <b>/join</b>. They create their own login. You stay owner. Shown once — copy it.</p>
  <div class="grid">
    <div class="card">
      <b>Mint invite</b>
      <label>Label</label>
      <input id="label" placeholder="alice · acme trial"/>
      <label>Max uses</label>
      <input id="uses" type="number" min="1" max="50" value="1"/>
      <label>Expires (days)</label>
      <input id="days" type="number" min="1" max="365" value="30"/>
      <button class="btn" id="mint">Mint seat key</button>
      <div class="err" id="err"></div>
      <div class="key" id="key"></div>
    </div>
    <div class="card">
      <b>Members</b>
      <p class="muted" id="sum">Loading…</p>
      <div id="people"></div>
    </div>
  </div>
  <div class="card" style="margin-top:14px">
    <b>Open invites</b>
    <div id="invs"></div>
  </div>
</main>
<script>
async function api(path, opt){
  const h={'Content-Type':'application/json'};
  try{ const t=localStorage.getItem('pocket_token')||sessionStorage.getItem('pocket_token'); if(t) h['X-Pocket-Token']=t; }catch(_){}
  const r=await fetch(path,{credentials:'same-origin',...(opt||{}),headers:{...h,...((opt&&opt.headers)||{})}});
  return r.json();
}
async function load(){
  const j=await api('/v1/admin/invites');
  if(!j.ok){ document.getElementById('sum').textContent='Sign in as owner to mint seats.'; return; }
  const users=j.users||[];
  const members=users.filter(u=>!u.is_owner);
  document.getElementById('sum').textContent=members.length+' member'+(members.length===1?'':'s')+' · '+users.length+' total';
  document.getElementById('people').innerHTML=users.map(u=>
    `<div class="row"><span>${u.display||u.user} <span class="muted">${u.user}</span></span><span class="muted">${u.is_owner?'owner':(u.plan||'member')}</span></div>`
  ).join('')||'<p class="muted">No seats yet</p>';
  document.getElementById('invs').innerHTML=(j.invites||[]).map(i=>
    `<div class="row"><span>${i.label} <span class="muted">${i.prefix}</span></span><span class="muted">${i.remaining} left · ${i.expired?'expired':'active'}</span></div>`
  ).join('')||'<p class="muted">No invites</p>';
}
document.getElementById('mint').onclick=async()=>{
  const err=document.getElementById('err'); err.textContent='';
  const j=await api('/v1/admin/invites',{method:'POST',body:JSON.stringify({
    label:document.getElementById('label').value.trim()||'seat',
    max_uses:parseInt(document.getElementById('uses').value,10)||1,
    expires_days:parseInt(document.getElementById('days').value,10)||30
  })});
  if(!j.ok){ err.textContent=j.error||'Could not mint'; return; }
  const box=document.getElementById('key');
  box.style.display='block';
  box.textContent=j.invite_key;
  try{ await navigator.clipboard.writeText(j.invite_key); box.textContent=j.invite_key+'  (copied)'; }catch(_){}
  load();
};
load();
</script>
</body></html>
"""
