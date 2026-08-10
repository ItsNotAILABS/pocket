"""Shared browser auth client — every POCKET surface uses the same login path.

Served as ALWAYS_PUBLIC `/auth/client.js` so desk, phone, studio, work, voice,
lab, developers, and the public gate all accept the same username/password and
store the same pocket_token + cookie session.
"""

from __future__ import annotations

# Injected as application/javascript — no build step.
AUTH_CLIENT_JS = r"""
/* POCKET unified auth client v1 */
(function (global) {
  'use strict';

  var TOKEN_KEY = 'pocket_token';
  var USER_KEY = 'pocket_user';

  function $(id) { return document.getElementById(id); }

  function getToken() {
    try {
      return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY) || '';
    } catch (_) { return ''; }
  }

  function getUser() {
    try {
      return sessionStorage.getItem(USER_KEY) || localStorage.getItem(USER_KEY) || 'pocket';
    } catch (_) { return 'pocket'; }
  }

  function storeSession(user, token) {
    user = (user || 'pocket').toString().trim() || 'pocket';
    token = (token || '').toString();
    try {
      sessionStorage.setItem(USER_KEY, user);
      localStorage.setItem(USER_KEY, user);
      if (token) {
        sessionStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(TOKEN_KEY, token);
      }
    } catch (_) {}
    return { user: user, token: token };
  }

  function clearSession() {
    try {
      sessionStorage.removeItem(TOKEN_KEY);
      sessionStorage.removeItem(USER_KEY);
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('pocket_pass');
      localStorage.removeItem('pocket_auth');
    } catch (_) {}
  }

  function authHeaders(extra) {
    var h = { 'Content-Type': 'application/json' };
    var tok = getToken();
    if (tok) {
      h['Authorization'] = 'Bearer ' + tok;
      h['X-Pocket-Token'] = tok;
    }
    var u = getUser();
    if (u) h['X-Pocket-User'] = u;
    if (extra) {
      for (var k in extra) if (Object.prototype.hasOwnProperty.call(extra, k)) h[k] = extra[k];
    }
    return h;
  }

  function normalizeCreds(user, password) {
    user = (user == null ? '' : String(user)).trim();
    password = password == null ? '' : String(password);
    // Many gates leave username blank — default to operator seat
    if (!user && password) user = 'pocket';
    return { user: user, password: password };
  }

  async function login(user, password, opts) {
    opts = opts || {};
    var c = normalizeCreds(user, password);
    if (!c.password) {
      return { ok: false, error: 'Enter your password' };
    }
    if (!c.user) {
      return { ok: false, error: 'Enter your username (try: pocket)' };
    }
    var body = {
      user: c.user,
      username: c.user,
      password: c.password,
      remember: opts.remember !== false
    };
    var r, j = {};
    try {
      r = await fetch((opts.base || '') + '/v1/auth/login', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-Pocket-Device': opts.device || 'web' },
        body: JSON.stringify(body)
      });
      try { j = await r.json(); } catch (_) { j = {}; }
    } catch (e) {
      return { ok: false, error: 'Cannot reach POCKET host: ' + (e && e.message || e) };
    }
    var tok = j.token || j.session_token || j.access_token || '';
    if (!r.ok || (!j.ok && !tok)) {
      // Localhost fallback: desktop unlock without password
      if (location.hostname === '127.0.0.1' || location.hostname === 'localhost') {
        var desk = await desktopLogin(opts);
        if (desk.ok) return desk;
      }
      return { ok: false, error: j.error || j.message || ('Sign-in failed (HTTP ' + r.status + ')') };
    }
    storeSession((j.user && (j.user.user || j.user.display)) || c.user, tok);
    return { ok: true, token: tok, user: j.user || { user: c.user } };
  }

  async function desktopLogin(opts) {
    opts = opts || {};
    if (location.hostname !== '127.0.0.1' && location.hostname !== 'localhost') {
      return { ok: false, error: 'desktop login only on this computer' };
    }
    try {
      var r = await fetch((opts.base || '') + '/v1/auth/desktop', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: '{}'
      });
      var j = await r.json().catch(function () { return {}; });
      if (!r.ok || !j.token) return { ok: false, error: j.error || 'desktop unlock failed' };
      storeSession((j.user && j.user.user) || 'pocket', j.token);
      return { ok: true, token: j.token, user: j.user, desktop: true };
    } catch (e) {
      return { ok: false, error: String(e && e.message || e) };
    }
  }

  async function ensureAuth(opts) {
    opts = opts || {};
    if (getToken()) return { ok: true, token: getToken(), user: getUser() };
    // Try desktop only on loopback
    if (location.hostname === '127.0.0.1' || location.hostname === 'localhost') {
      var d = await desktopLogin(opts);
      if (d.ok) return d;
    }
    return { ok: false, error: 'sign in required' };
  }

  async function me() {
    var tok = getToken();
    if (!tok) return { ok: false, error: 'no token' };
    try {
      var r = await fetch('/v1/auth/me', {
        method: 'POST',
        credentials: 'same-origin',
        headers: authHeaders(),
        body: '{}'
      });
      var j = await r.json().catch(function () { return {}; });
      if (!r.ok) return { ok: false, error: j.error || ('HTTP ' + r.status) };
      return j;
    } catch (e) {
      return { ok: false, error: String(e && e.message || e) };
    }
  }

  async function logout() {
    try {
      await fetch('/v1/auth/logout', {
        method: 'POST',
        credentials: 'same-origin',
        headers: authHeaders(),
        body: '{}'
      });
    } catch (_) {}
    clearSession();
  }

  /**
   * Wire a standard login form.
   * opts: { userId, passId, btnId, errId, formId, onSuccess, device, defaultUser }
   */
  function bindLoginForm(opts) {
    opts = opts || {};
    var userEl = $(opts.userId || 'loginUser') || $(opts.userId || 'u');
    var passEl = $(opts.passId || 'loginPass') || $(opts.passId || 'p');
    var btnEl = $(opts.btnId || 'loginBtn');
    var errEl = $(opts.errId || 'loginErr') || $(opts.errId || 'e');
    var formEl = opts.formId ? $(opts.formId) : null;
    if (userEl && opts.defaultUser !== false && !userEl.value) {
      userEl.value = opts.defaultUser || 'pocket';
      try { userEl.placeholder = userEl.placeholder || 'pocket'; } catch (_) {}
    }
    function setErr(msg) {
      if (errEl) errEl.textContent = msg || '';
    }
    async function run(ev) {
      if (ev) { try { ev.preventDefault(); } catch (_) {} }
      setErr('Signing in…');
      if (btnEl) btnEl.disabled = true;
      var u = userEl ? userEl.value : 'pocket';
      var p = passEl ? passEl.value : '';
      var res = await login(u, p, { device: opts.device || 'web' });
      if (btnEl) btnEl.disabled = false;
      if (!res.ok) {
        setErr(res.error || 'Sign-in failed');
        return false;
      }
      setErr('');
      if (typeof opts.onSuccess === 'function') {
        try { await opts.onSuccess(res); } catch (_) {}
      } else {
        location.replace('/desk?authed=1');
      }
      return true;
    }
    if (formEl) formEl.addEventListener('submit', run);
    if (btnEl) {
      btnEl.addEventListener('click', function (e) {
        if (e) e.preventDefault();
        run(e);
      });
    }
    if (passEl) {
      passEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); run(e); }
      });
    }
    if (userEl) {
      userEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (passEl) passEl.focus();
          else run(e);
        }
      });
    }
    return { run: run };
  }

  /** Minimal overlay gate when a surface has no own login UI (web). */
  function showPasswordGate(opts) {
    opts = opts || {};
    if ($('pocketUnifiedGate')) {
      $('pocketUnifiedGate').style.display = 'flex';
      return;
    }
    var wrap = document.createElement('div');
    wrap.id = 'pocketUnifiedGate';
    wrap.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.72);padding:20px;font-family:system-ui,sans-serif';
    wrap.innerHTML =
      '<div style="width:min(400px,100%);background:#141416;border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px;color:#fafafa">' +
      '<h2 style="margin:0 0 8px;font-size:1.2rem">Sign in to POCKET</h2>' +
      '<p style="margin:0 0 12px;color:#a1a1aa;font-size:13px;line-height:1.45">Same username and password as the desk (ACCESS.txt on this PC).</p>' +
      '<label style="display:block;font-size:12px;color:#a1a1aa;margin:10px 0 6px">Username</label>' +
      '<input id="pugUser" value="pocket" autocomplete="username" style="width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#0c0c0e;color:#fafafa;box-sizing:border-box"/>' +
      '<label style="display:block;font-size:12px;color:#a1a1aa;margin:10px 0 6px">Password</label>' +
      '<input id="pugPass" type="password" autocomplete="current-password" style="width:100%;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#0c0c0e;color:#fafafa;box-sizing:border-box"/>' +
      '<button type="button" id="pugBtn" style="margin-top:14px;width:100%;padding:12px;border:0;border-radius:10px;background:#10a37f;color:#041;font-weight:700;cursor:pointer">Continue</button>' +
      '<div id="pugErr" style="color:#f87171;font-size:13px;min-height:1.2em;margin-top:10px"></div>' +
      '</div>';
    document.body.appendChild(wrap);
    bindLoginForm({
      userId: 'pugUser',
      passId: 'pugPass',
      btnId: 'pugBtn',
      errId: 'pugErr',
      device: opts.device || 'web',
      onSuccess: async function (res) {
        wrap.style.display = 'none';
        if (typeof opts.onSuccess === 'function') await opts.onSuccess(res);
        else location.reload();
      }
    });
    try { $('pugPass').focus(); } catch (_) {}
  }

  global.PocketAuth = {
    getToken: getToken,
    getUser: getUser,
    storeSession: storeSession,
    clearSession: clearSession,
    authHeaders: authHeaders,
    login: login,
    desktopLogin: desktopLogin,
    ensureAuth: ensureAuth,
    me: me,
    logout: logout,
    bindLoginForm: bindLoginForm,
    showPasswordGate: showPasswordGate,
    normalizeCreds: normalizeCreds
  };
})(typeof window !== 'undefined' ? window : this);
"""


def auth_client_js() -> str:
    return AUTH_CLIENT_JS
