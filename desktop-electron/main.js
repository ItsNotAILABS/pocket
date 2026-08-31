/**
 * POCKET Electron — sovereign desktop shell
 * - Operator/Owner (POCKET_CLIENT_ROLE=operator): local host only, no onboarding
 * - User (POCKET_CLIENT_ROLE=user or packaged default): first-run source picker
 * Separate userData per role so Owner + User can run without clobbering config.
 * Never kills a healthy host. Never stores passwords or seat keys.
 * Navigation stays on the chosen desk origin; other https opens in system browser.
 * Doctrine: work runs on YOUR host (or your team's host) — not a vendor chat tab.
 */
const { app, BrowserWindow, shell, ipcMain, Menu } = require("electron");
const path = require("path");
const fs = require("fs");
const http = require("http");
const https = require("https");
const { spawn } = require("child_process");
const { URL } = require("url");

const OWNER_PORT = 8787;
const USERS_PORT = 8788;
const PORT = OWNER_PORT;
/** Public demo default (not a secret). Operators can override via POCKET_PUBLIC_URL. */
const DEFAULT_CLOUD =
  (process.env.POCKET_PUBLIC_URL || "https://pocket.medinatechlabs.net").replace(
    /\/$/,
    ""
  );

let mainWindow = null;
let hostProc = null;
let quitting = false;

// ---- Role + isolated profiles (must run before ready / single-instance) ----
function envRole() {
  const r = (process.env.POCKET_CLIENT_ROLE || "").toLowerCase().trim();
  if (r === "operator" || r === "owner") return "operator";
  if (r === "user") return "user";
  return null; // packaged install → treat as user
}

const LAUNCH_ROLE = envRole() || "user";
const IS_OPERATOR = LAUNCH_ROLE === "operator";

if (app.setName) {
  app.setName(IS_OPERATOR ? "POCKET Owner" : "POCKET for Users");
}
if (process.platform === "win32" && app.setAppUserModelId) {
  app.setAppUserModelId(
    IS_OPERATOR ? "com.medinatech.pocket.owner" : "com.medinatech.pocket.user"
  );
}

// Separate profiles so Owner + User can run / be tested without shared state
try {
  const base = app.getPath("appData");
  const profile = IS_OPERATOR ? "POCKET-Owner" : "POCKET-User";
  app.setPath("userData", path.join(base, profile));
} catch (_) {
  /* appData available before ready on Electron */
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

function configPath() {
  return path.join(app.getPath("userData"), "pocket-client.json");
}

function localPort() {
  return IS_OPERATOR ? OWNER_PORT : USERS_PORT;
}

function defaultConfig() {
  if (IS_OPERATOR) {
    return {
      role: "operator",
      source: "local",
      baseUrl: `http://127.0.0.1:${OWNER_PORT}`,
      onboarded: true,
    };
  }
  return {
    role: "user",
    source: null,
    baseUrl: null,
    onboarded: false,
    defaultCloud: DEFAULT_CLOUD,
    localUsersUrl: `http://127.0.0.1:${USERS_PORT}`,
  };
}

function readConfig() {
  try {
    const p = configPath();
    if (fs.existsSync(p)) {
      const j = JSON.parse(fs.readFileSync(p, "utf8"));
      // Launch role always wins over stale file (profile already isolates)
      const base = defaultConfig();
      return {
        ...base,
        ...j,
        role: base.role,
        defaultCloud: DEFAULT_CLOUD,
      };
    }
  } catch (_) {}
  return defaultConfig();
}

function writeConfig(cfg) {
  const p = configPath();
  fs.mkdirSync(path.dirname(p), { recursive: true });
  // never store passwords or invite keys
  const safe = {
    role: IS_OPERATOR ? "operator" : "user",
    source: cfg.source || null,
    baseUrl: cfg.baseUrl || null,
    onboarded: !!cfg.onboarded,
    updatedAt: Date.now(),
  };
  fs.writeFileSync(p, JSON.stringify(safe, null, 2), "utf8");
  return { ...safe, defaultCloud: DEFAULT_CLOUD };
}

function root() {
  return process.env.POCKET_ROOT || path.resolve(__dirname, "..");
}

function py() {
  const c = path.join(
    process.env.LOCALAPPDATA || "",
    "Programs",
    "Python",
    "Python311-arm64",
    "python.exe"
  );
  return fs.existsSync(c) ? c : "python";
}

function healthLocal() {
  return new Promise((resolve) => {
    const req = http.get(
      { hostname: "127.0.0.1", port: localPort(), path: "/health", timeout: 2000 },
      (res) => {
        res.resume();
        resolve(res.statusCode === 200);
      }
    );
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

function probeUrl(baseUrl) {
  return new Promise((resolve) => {
    let u;
    try {
      u = new URL(baseUrl.replace(/\/$/, "") + "/health");
    } catch {
      resolve({ ok: false, error: "Invalid URL" });
      return;
    }
    const lib = u.protocol === "https:" ? https : http;
    const req = lib.get(
      {
        hostname: u.hostname,
        port: u.port || (u.protocol === "https:" ? 443 : 80),
        path: u.pathname,
        timeout: 8000,
        rejectUnauthorized: true,
      },
      (res) => {
        res.resume();
        // 200 health, or 401/403 still means host is up (auth in front)
        const code = res.statusCode || 0;
        resolve({
          ok: code > 0 && code < 500,
          status: code,
          error: code >= 500 ? `HTTP ${code}` : null,
        });
      }
    );
    req.on("error", (e) => resolve({ ok: false, error: String(e.message || e) }));
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, error: "Timeout reaching desk" });
    });
  });
}

function ensureLocalHost() {
  return healthLocal().then((ok) => {
    if (ok) return true;
    if (hostProc && hostProc.exitCode == null) return waitLocal(40000);
    const r = root();
    const src = path.join(r, "src");
    if (!fs.existsSync(path.join(src, "pocket"))) {
      return false;
    }
    const port = localPort();
    hostProc = spawn(
      py(),
      ["-u", "-m", "pocket", "serve", "--host", "127.0.0.1", "--port", String(port)],
      {
        cwd: r,
        env: {
          ...process.env,
          PYTHONPATH: src,
          POCKET_PORT: String(port),
          POCKET_PRODUCT: IS_OPERATOR ? "owner" : "users",
          POCKET_EDITION: IS_OPERATOR ? "founder" : "public",
          POCKET_PUBLIC_URL: `http://127.0.0.1:${port}`,
          POCKET_MESH_HOOK: "0",
          POCKET_ALWAYS_MESH: "0",
          POCKET_HEADLESS_AUTO: "0",
          POCKET_AURO_TRAIN: "0",
        },
        windowsHide: true,
        stdio: "ignore",
      }
    );
    hostProc.on("exit", () => {
      hostProc = null;
    });
    return waitLocal(40000);
  });
}

async function waitLocal(ms) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    if (await healthLocal()) return true;
    await new Promise((r) => setTimeout(r, 400));
  }
  return healthLocal();
}

function deskUrl(cfg) {
  const fallback = `http://127.0.0.1:${localPort()}`;
  const base = (cfg.baseUrl || fallback).replace(/\/$/, "");
  return base + "/desk";
}

function loadOnboarding() {
  const file = path.join(__dirname, "onboarding.html");
  mainWindow.loadFile(file);
}

async function openDesk(cfg) {
  const url = deskUrl(cfg);
  if (cfg.source === "local" || /127\.0\.0\.1|localhost/.test(cfg.baseUrl || "")) {
    const ok = await ensureLocalHost();
    if (!ok) {
      mainWindow.loadURL(
        "data:text/html," +
          encodeURIComponent(
            `<body style="background:#09090b;color:#fff;font-family:system-ui;padding:40px">
            <h1>Local host not running</h1>
            <p>Could not start POCKET on this PC. Install the host product or pick Team/cloud desk.</p>
            <p style="color:#a1a1aa">Menu → POCKET → Change desk source…</p>
            </body>`
          )
      );
      return { ok: false, error: "Local host failed to start" };
    }
  }
  mainWindow.loadURL(url);
  return { ok: true, url };
}

function originBase(cfg) {
  try {
    const b = (cfg && cfg.baseUrl) || `http://127.0.0.1:${localPort()}`;
    return new URL(b).origin;
  } catch {
    return `http://127.0.0.1:${localPort()}`;
  }
}

function openPath(cfg, pathSuffix) {
  const base = originBase(cfg).replace(/\/$/, "");
  const p = pathSuffix.startsWith("/") ? pathSuffix : `/${pathSuffix}`;
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.loadURL(base + p);
  }
}

function isAllowedNav(url, cfg) {
  try {
    const u = new URL(url);
    if (u.protocol === "file:") return true;
    if (u.protocol === "data:") return true;
    if (u.protocol !== "http:" && u.protocol !== "https:") return false;
    const origin = originBase(cfg);
    if (u.origin === origin) return true;
    // always allow loopback host health while switching
    if (
      (u.hostname === "127.0.0.1" || u.hostname === "localhost") &&
      (u.port === String(OWNER_PORT) || u.port === String(USERS_PORT) || u.port === "")
    ) {
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

function buildMenu(cfg) {
  const template = [
    {
      label: "POCKET",
      submenu: [
        {
          label: "Open desk",
          accelerator: "CmdOrCtrl+1",
          click: () => openDesk(readConfig()),
        },
        {
          label: "Docs hub",
          accelerator: "CmdOrCtrl+2",
          click: () => openPath(readConfig(), "/docs"),
        },
        {
          label: "Agent Mail",
          accelerator: "CmdOrCtrl+3",
          click: () => openPath(readConfig(), "/mail"),
        },
        {
          label: "Install slices",
          click: () => openPath(readConfig(), "/install"),
        },
        {
          label: "Work Studio",
          click: () => openPath(readConfig(), "/work"),
        },
        {
          label: "Phone",
          click: () => openPath(readConfig(), "/phone"),
        },
        { type: "separator" },
        {
          label: "Change desk source…",
          enabled: !IS_OPERATOR,
          click: () => {
            const c = readConfig();
            c.onboarded = false;
            writeConfig(c);
            loadOnboarding();
          },
        },
        {
          label: IS_OPERATOR ? "YOUR POCKET · Owner / this machine" : "USER FACING · Seat client",
          enabled: false,
        },
        {
          label: "Which POCKET?",
          click: () => openPath(readConfig(), "/which"),
        },
        {
          label: "Reset user onboarding (this profile)",
          enabled: !IS_OPERATOR,
          click: () => {
            writeConfig({
              role: "user",
              source: null,
              baseUrl: null,
              onboarded: false,
            });
            loadOnboarding();
          },
        },
        { type: "separator" },
        { role: "quit" },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
        ...(process.env.POCKET_DEV === "1" ? [{ role: "toggleDevTools" }] : []),
      ],
    },
    {
      label: "Help",
      submenu: [
        {
          label: "Ecosystem · pocket (host)",
          click: () => shell.openExternal("https://github.com/ItsNotAILABS/pocket"),
        },
        {
          label: "POCKET Agent (CLI + slices)",
          click: () => shell.openExternal("https://github.com/ItsNotAILABS/pocket-agent"),
        },
        {
          label: "Pocket Voice",
          click: () =>
            shell.openExternal("https://github.com/ItsNotAILABS/pocket-voice-to-text"),
        },
        {
          label: "User hub (pocket-app)",
          click: () => shell.openExternal("https://github.com/ItsNotAILABS/pocket"),
        },
        { type: "separator" },
        {
          label: "Live catalog JSON",
          click: () => openPath(readConfig(), "/v1/catalog"),
        },
        {
          label: "How-to · Agent Mail",
          click: () => openPath(readConfig(), "/docs/view/how-to/AGENT_MAIL"),
        },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// IPC for onboarding page (user profile only)
ipcMain.handle("pocket:getConfig", () => readConfig());
ipcMain.handle("pocket:defaults", () => ({
  defaultCloud: DEFAULT_CLOUD,
  localUsersUrl: `http://127.0.0.1:${USERS_PORT}`,
  role: LAUNCH_ROLE,
  isOperator: IS_OPERATOR,
}));
ipcMain.handle("pocket:completeOnboarding", async (_e, payload) => {
  if (IS_OPERATOR) {
    return { ok: false, error: "Owner mode does not use onboarding" };
  }
  const source = (payload && payload.source) || "cloud";
  let baseUrl = (payload && payload.baseUrl) || "";
  if (source === "local") {
    baseUrl = `http://127.0.0.1:${USERS_PORT}`;
    const ok = await ensureLocalHost();
    if (!ok) {
      return { ok: false, error: "Could not start POCKET for Users on :8788" };
    }
  } else {
    baseUrl = String(baseUrl || "").replace(/\/$/, "");
    if (!/^https?:\/\//i.test(baseUrl)) {
      return { ok: false, error: "URL must start with https://" };
    }
    try {
      const u = new URL(baseUrl);
      if (!u.hostname) return { ok: false, error: "Invalid host" };
      // store origin only
      baseUrl = u.origin;
    } catch {
      return { ok: false, error: "Invalid URL" };
    }
    const probe = await probeUrl(baseUrl);
    if (!probe.ok) {
      return {
        ok: false,
        error: probe.error || "Desk not reachable — check URL / network",
      };
    }
  }
  const cfg = writeConfig({
    role: "user",
    source,
    baseUrl,
    onboarded: true,
  });
  buildMenu(cfg);
  await openDesk(cfg);
  return { ok: true, config: cfg };
});

app.whenReady().then(async () => {
  mainWindow = new BrowserWindow({
    title: IS_OPERATOR ? "POCKET Owner — your machine" : "POCKET Seat — user facing",
    width: 1360,
    height: 880,
    minWidth: 960,
    minHeight: 640,
    backgroundColor: "#09090b",
    show: false,
    autoHideMenuBar: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
    },
  });
  mainWindow.once("ready-to-show", () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
  // Sovereign navigation: stay on desk origin; external https → system browser only
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    const cfgNow = readConfig();
    if (isAllowedNav(url, cfgNow)) {
      return { action: "allow" };
    }
    if (/^https?:/i.test(url) && !/^file:/i.test(url)) {
      shell.openExternal(url);
    }
    return { action: "deny" };
  });
  mainWindow.webContents.on("will-navigate", (event, url) => {
    const cfgNow = readConfig();
    if (isAllowedNav(url, cfgNow)) return;
    event.preventDefault();
    if (/^https?:/i.test(url)) shell.openExternal(url);
  });

  const cfg = readConfig();
  buildMenu(cfg);

  // OWNER: never show source picker — local desk only
  if (IS_OPERATOR) {
    mainWindow.loadURL(
      "data:text/html," +
        encodeURIComponent(
          `<body style="background:#09090b;color:#e4e4e7;font-family:system-ui;padding:48px">
          <p style="letter-spacing:.12em;text-transform:uppercase;color:#fbbf24;font-weight:800;font-size:12px">YOUR POCKET</p>
          <h1 style="color:#eab308">POCKET Owner</h1>
          <p>POCKET Owner on :8787. Users is a different product on :8788. Starting your host…</p></body>`
        )
    );
    mainWindow.show();
    await openDesk({
      role: "operator",
      source: "local",
      baseUrl: `http://127.0.0.1:${PORT}`,
      onboarded: true,
    });
    return;
  }

  // USER: first open → source picker
  if (!cfg.onboarded || !cfg.baseUrl) {
    mainWindow.show();
    loadOnboarding();
    return;
  }

  // Returning user seat
  mainWindow.show();
  await openDesk(cfg);
});

app.on("window-all-closed", () => {
  quitting = true;
  // Do NOT kill host
  app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0 && !quitting) {
    app.relaunch();
  }
});
