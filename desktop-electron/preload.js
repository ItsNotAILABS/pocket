/**
 * User-facing client bridge only — no secrets, no fs, no shell.
 * Sovereign shell: renderer cannot reach Node or host filesystem.
 */
const { contextBridge, ipcRenderer } = require("electron");

const _role = (process.env.POCKET_CLIENT_ROLE || "").toLowerCase();
const _isOwner = _role === "operator" || _role === "owner";
contextBridge.exposeInMainWorld("pocket", {
  platform: process.platform,
  shell: "electron",
  version: "2.2.0",
  sovereign: true,
  product: _isOwner ? "POCKET Owner" : "POCKET Seat",
  clientRole: _isOwner ? "operator" : "user",
  face: _isOwner ? "owner" : "seat",
  lab: "ItsNotAI Labs",
});

contextBridge.exposeInMainWorld("pocketClient", {
  getConfig: () => ipcRenderer.invoke("pocket:getConfig"),
  getDefaults: () => ipcRenderer.invoke("pocket:defaults"),
  completeOnboarding: (payload) =>
    ipcRenderer.invoke("pocket:completeOnboarding", payload || {}),
});
