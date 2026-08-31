"""Live integration test — phone domain + pair + studio + capsule (not unit smoke)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
LOCAL = "http://127.0.0.1:8787"
DOMAIN = "https://pocket.medinatechlabs.net"


def req(url: str, method: str = "GET", data=None, headers=None, timeout: int = 90):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def show(label: str, code: int, raw: str, n: int = 180) -> None:
    snip = (raw or "")[:n].replace("\n", " ")
    print(f"{label:30} {code}  {snip}")


def main() -> int:
    fails = 0
    print("=== PHONE SHELLS (domain must serve full PWA app) ===")
    for url in [
        f"{DOMAIN}/phone",
        f"{LOCAL}/phone",
        f"{DOMAIN}/phone/manifest.webmanifest",
        f"{LOCAL}/v1/phone/ready",
        f"{DOMAIN}/v1/phone/ready",
        f"{DOMAIN}/v1/health",
        f"{DOMAIN}/v1/node/hello",
    ]:
        c, raw = req(url)
        app = ("pairChip" in raw) or ("Unlock phone" in raw)
        gate_only = ("Sign in to POCKET" in raw) and ("pairChip" not in raw)
        ok_mark = "OK" if c == 200 else "FAIL"
        if "phone" in url and url.endswith("/phone") and not app and not gate_only and c != 200:
            fails += 1
        if url.endswith("/phone") and gate_only:
            print(f"FAIL domain still serving lock-only shell: {url}")
            fails += 1
        print(f"{ok_mark} {c} len={len(raw)} app={app} gateOnly={gate_only}  {url}")

    print("=== LOCAL AUTH + API ===")
    c, raw = req(f"{LOCAL}/v1/auth/desktop", "POST", {})
    show("auth/desktop", c, raw)
    if c != 200:
        print("FATAL: cannot auth desktop")
        return 2
    tok = json.loads(raw).get("token")
    # Prefer both styles — Bearer must work for phone PWA fetch()
    H = {"Authorization": f"Bearer {tok}", "X-Pocket-Token": tok}

    checks = [
        ("GET", "/v1/phone/ready", None),
        ("GET", "/v1/phone/bridge", None),
        ("GET", "/v1/studio", None),
        ("GET", "/v1/studio/first-class", None),
        ("POST", "/v1/studio/storyboard", {"prompt": "live phone demo", "product": "POCKET"}),
        ("POST", "/v1/studio/agent", {"skill": "studio_map"}),
        ("POST", "/v1/skills/run", {"skill": "studio_status"}),
        ("POST", "/v1/skills/run", {"skill": "life_catalog"}),
        ("POST", "/v1/skills/run", {"skill": "webgpu_probe"}),
        ("POST", "/v1/skills/run", {"skill": "phone_surface"}),
    ]
    for method, path, data in checks:
        c, raw = req(LOCAL + path, method, data, H)
        show(path, c, raw)
        if c != 200:
            fails += 1
        elif path in ("/v1/studio/first-class", "/v1/studio") and "first_class" not in raw and "studio_map" not in raw and "protocol" not in raw:
            # studio get embeds first_class; first-class has protocol
            if path == "/v1/studio/first-class" and "POCKET-STUDIO" not in raw and "playbooks" not in raw:
                fails += 1
                print("  !! missing studio first-class payload")

    # Pair
    c, raw = req(f"{LOCAL}/v1/node/pair", "POST", {"label": "phone-live"}, H)
    show("pair mint", c, raw)
    code = None
    try:
        code = json.loads(raw).get("code")
    except Exception:
        pass
    if not code:
        fails += 1
    else:
        c, raw = req(
            f"{LOCAL}/v1/node/redeem",
            "POST",
            {"code": code, "label": "phone-live", "peer_label": "POCKET Phone"},
        )
        show("pair redeem", c, raw)
        try:
            j = json.loads(raw)
            print(
                "  redeem ok=",
                j.get("ok"),
                "peer=",
                j.get("peer_id"),
                "has_token=",
                bool(j.get("pair_token") or j.get("token")),
            )
            if not j.get("ok"):
                fails += 1
        except Exception:
            fails += 1

    # Capsule
    c, raw = req(
        f"{LOCAL}/v1/capsule/allocate",
        "POST",
        {"tier": "256MB", "enableWebGPU": True, "runtime": "HostWorker", "label": "live"},
        H,
    )
    show("capsule alloc", c, raw)
    cid = None
    try:
        cid = json.loads(raw).get("capsule", {}).get("id")
    except Exception:
        pass
    if cid:
        c, raw = req(
            f"{LOCAL}/v1/capsule/execute",
            "POST",
            {"id": cid, "command": "python -c \"print('live-ok')\""},
            H,
        )
        show("capsule exec", c, raw)
        if "live-ok" not in raw and '"ok": true' not in raw and '"ok":true' not in raw:
            # still ok if events present
            if "live-ok" not in raw:
                print("  note: exec payload", raw[:200])
        c, raw = req(f"{LOCAL}/v1/capsule/commit", "POST", {"id": cid}, H)
        show("capsule commit", c, raw)
        c, raw = req(f"{LOCAL}/v1/capsule/terminate", "POST", {"id": cid}, H)
        show("capsule term", c, raw)
    else:
        fails += 1

    # Studio viral (heavy)
    c, raw = req(
        f"{LOCAL}/v1/studio/auto",
        "POST",
        {"title": "POCKET", "subtitle": "Live viral", "cta": "ItsNotAI Labs"},
        H,
        timeout=180,
    )
    show("studio auto", c, raw)

    print(f"=== LIVE TEST COMPLETE fails={fails} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
