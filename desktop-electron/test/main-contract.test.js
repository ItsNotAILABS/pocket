"use strict";
const fs = require("fs");
const path = require("path");
const test = require("node:test");
const assert = require("node:assert/strict");
const source = fs.readFileSync(path.join(__dirname, "..", "main.js"), "utf8");
const manager = fs.readFileSync(path.join(__dirname, "..", "lib", "host-manager.js"), "utf8");
const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "package.json"), "utf8"));

test("desktop stays on /desk for multi-agent work", () => {
  assert.match(source, /return base \+ "\/desk"/);
  assert.match(source, /\/desk\?split=1/);
  assert.match(source, /\/desk\?agent=spark/);
  assert.match(source, /\/desk\?tab=crew/);
  assert.match(source, /Side by side \(two agents\)/);
});

test("desktop package includes its local host", () => {
  assert.equal(pkg.version, "3.0.0");
  assert.equal(pkg.build.extraResources[0].to, "host/pocket-host.exe");
  assert.match(source, /--edge/);
  assert.match(source, /--cloud/);
  assert.match(source, /--background/);
});

test("owner and users are separate local products", () => {
  assert.match(source, /OWNER_PORT = 8787/);
  assert.match(source, /USERS_PORT = 8788/);
  assert.match(source, /POCKET Owner — your machine/);
  assert.match(source, /POCKET Seat — user facing/);
  assert.match(source, /POCKET_PRODUCT/);
});

test("lifecycle refuses automatic process killing", () => {
  assert.doesNotMatch(source + manager, /taskkill|Stop-Process|process\.kill/);
  assert.match(manager, /will not kill or replace/);
});

test("paired cloud work creates and uses a restricted local API key", () => {
  assert.match(source, /ensureDeviceKey/);
  assert.match(source, /localJson\("\/v1\/ai\/keys"[\s\S]*?token/);
  assert.match(source, /localJson\("\/v1\/ai\/chat"[\s\S]*?apiKey/);
  assert.match(source, /localJson\(`\/v1\/ai\/agents\/\$\{encodeURIComponent\(agent\)\}\/run`[\s\S]*?apiKey/);
});
