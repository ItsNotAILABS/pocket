"""POCKET integrations — real execute path for every catalog entry.

Every integration can run via execute(id, ...):
  · desktop apps (Discord, Slack, Teams, …) → pocket.desktop.open_app
  · web / SaaS → remote Edge browser (signed-in profile)
  · life ops (reserve / buy / research / …) → browser + working-board intent
  · host tabs / screen / agents → structured desk actions

Agents, MCP, desk UI, and POST /v1/integrations/{id}/execute all share this.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from pocket.integrations_catalog import INTEGRATIONS, get as catalog_get

# Map catalog id → desktop allowlist app id (safety.ALLOWED_APPS)
DESKTOP_MAP: Dict[str, str] = {
    "discord": "discord",
    "slack": "slack",
    "teams": "teams",
    "spotify": "spotify",
    "zoom": "zoom",
    "notion": "notion",
    "figma": "figma",
    "github": "github",
    "outlook": "outlook",
    "linear": "linear",
    "browser_edge": "edge",
    "telegram": "telegram",
    "chatgpt": "chatgpt",
    "obsidian": "obsidian",
    "copilot": "copilot",
    "steam": "steam",
    "postman": "postman",
    "chrome": "chrome",
    "code": "code",
    "cursor": "cursor",
}

# Actions that open the Working board and seed a prompt
BOARD_ACTIONS = frozenset(
    {"reserve", "buy", "research", "analysis", "notify", "schedule", "errand"}
)


def _find(integration_id: str) -> Optional[Dict[str, Any]]:
    r = catalog_get(integration_id)
    if r.get("ok"):
        return r.get("integration")  # type: ignore[return-value]
    return None


def _open_browser(url: str, *, profile: str = "Default") -> Dict[str, Any]:
    if not url:
        return {"ok": False, "error": "no url"}
    try:
        from pocket.remote_browser import open_url

        return open_url(url, profile=profile)
    except Exception as e:
        try:
            from pocket.desktop import open_app

            return open_app("edge", args=url)
        except Exception as e2:
            return {"ok": False, "error": f"browser open failed: {e}; fallback: {e2}"}


def _open_desktop(app_id: str, *, args: str = "") -> Dict[str, Any]:
    from pocket.desktop import open_app

    return open_app(app_id, args=args or "")


def _probe_desktop(app_id: str) -> Dict[str, Any]:
    """Check whether a desktop app is resolvable without launching it."""
    try:
        from pocket.desktop import _resolve_cmd
        from pocket.safety import ALLOWED_APPS, allow_app

        ok, msg, meta = allow_app(app_id)
        if not ok or not meta:
            return {"ok": False, "available": False, "error": msg, "app": app_id}
        resolved, available = _resolve_cmd(app_id, meta.get("cmd") or app_id)
        return {
            "ok": True,
            "available": bool(available),
            "app": app_id,
            "label": meta.get("label"),
            "resolved": resolved if available else None,
        }
    except Exception as e:
        return {"ok": False, "available": False, "error": str(e)[:200], "app": app_id}


def execute(
    integration_id: str,
    *,
    text: str = "",
    prompt: str = "",
    dry_run: bool = False,
    prefer: str = "",  # desktop | browser | auto
    profile: str = "Default",
    open_browser: bool = True,
    open_desktop: bool = True,
) -> Dict[str, Any]:
    """Execute one integration for real (or dry_run plan).

    Returns a structured receipt every caller can surface:
      ok, id, name, action, mode, steps[], results{}, prompt, message
    """
    iid = (integration_id or "").strip().lower()
    it = _find(iid)
    if not it:
        return {
            "ok": False,
            "error": "unknown integration",
            "id": iid,
            "hint": "GET /v1/integrations for catalog",
        }

    act = str(it.get("action") or "open").lower()
    url = str(it.get("url") or "")
    name = str(it.get("name") or iid)
    seed = (text or prompt or "").strip() or str(it.get("prompt") or "")
    desk_id = str(it.get("desktop_app") or DESKTOP_MAP.get(iid) or "").strip().lower()
    prefer_n = (prefer or it.get("prefer") or "auto").strip().lower()
    if prefer_n not in ("desktop", "browser", "auto"):
        prefer_n = "auto"

    steps: List[Dict[str, Any]] = []
    results: Dict[str, Any] = {}
    mode = "open"
    message = ""

    # ---- Host / desk actions (no external launch always needed) ----
    if act == "working" or iid == "working_board":
        mode = "working"
        steps.append({"step": "working_board", "status": "ready"})
        message = "Working board — buy · analyze · reserve ops"
        return _receipt(
            True, it, mode, steps, results, seed, message, dry_run=dry_run
        )

    if act == "tab":
        mode = "tab"
        tab = str(it.get("tab") or "mcp")
        steps.append({"step": "show_tab", "tab": tab, "status": "ready"})
        message = f"Open desk tab: {tab}"
        return _receipt(
            True, it, mode, steps, results, seed, message, dry_run=dry_run, extra={"tab": tab}
        )

    if act == "screen" or iid == "screen_control":
        mode = "screen"
        steps.append({"step": "screen_control", "status": "ready"})
        message = "Screen control — agents see and drive host UI"
        return _receipt(
            True, it, mode, steps, results, seed, message, dry_run=dry_run
        )

    if act == "agent":
        mode = "agent"
        agent = str(it.get("agent") or iid)
        steps.append({"step": "pick_agent", "agent": agent, "status": "ready"})
        # Still warm the surface when URL present
        if url and open_browser and not dry_run:
            br = _open_browser(url, profile=profile)
            results["browser"] = br
            steps.append(
                {
                    "step": "browser",
                    "url": url,
                    "ok": bool(br.get("ok")),
                    "status": "done" if br.get("ok") else "failed",
                }
            )
        elif url:
            steps.append({"step": "browser", "url": url, "status": "planned" if dry_run else "skipped"})
        message = f"Agent {agent} ready" + (f" · {url}" if url else "")
        return _receipt(
            True,
            it,
            mode,
            steps,
            results,
            seed,
            message,
            dry_run=dry_run,
            extra={"agent": agent},
        )

    if act == "remote" or iid == "browser_edge":
        mode = "remote"
        target = url or "https://www.bing.com"
        if dry_run:
            steps.append({"step": "remote_browser", "url": target, "status": "planned"})
            message = f"Would open Edge remote: {target}"
        else:
            br = _open_browser(target, profile=profile)
            results["browser"] = br
            steps.append(
                {
                    "step": "remote_browser",
                    "url": target,
                    "ok": bool(br.get("ok")),
                    "status": "done" if br.get("ok") else "failed",
                }
            )
            message = br.get("message") or f"Opened Edge: {target}"
        return _receipt(
            bool(results.get("browser", {}).get("ok", dry_run)),
            it,
            mode,
            steps,
            results,
            seed,
            message,
            dry_run=dry_run,
        )

    # ---- Board / life ops: warm URL + return board intent ----
    if act in BOARD_ACTIONS:
        mode = f"board:{act}"
        steps.append({"step": "working_board", "intent": act, "status": "ready"})
        # Desktop companion first when available (e.g. outlook, slack)
        if desk_id and open_desktop and prefer_n != "browser":
            probe = _probe_desktop(desk_id)
            results["desktop_probe"] = probe
            if probe.get("available"):
                if dry_run:
                    steps.append({"step": "desktop", "app": desk_id, "status": "planned"})
                else:
                    dr = _open_desktop(desk_id, args="")
                    results["desktop"] = dr
                    steps.append(
                        {
                            "step": "desktop",
                            "app": desk_id,
                            "ok": bool(dr.get("ok")),
                            "status": "done" if dr.get("ok") else "failed",
                        }
                    )
            elif prefer_n == "desktop":
                steps.append(
                    {
                        "step": "desktop",
                        "app": desk_id,
                        "status": "unavailable",
                        "error": probe.get("error") or "not installed",
                    }
                )
        # Always warm the web surface for board intents when URL present
        if url and open_browser:
            if dry_run:
                steps.append({"step": "browser", "url": url, "status": "planned"})
            else:
                br = _open_browser(url, profile=profile)
                results["browser"] = br
                steps.append(
                    {
                        "step": "browser",
                        "url": url,
                        "ok": bool(br.get("ok")),
                        "status": "done" if br.get("ok") else "failed",
                    }
                )
        message = f"{name} · {act} — type details on Working board"
        if results.get("desktop", {}).get("ok"):
            message = f"Opened {name} desktop · {act} on Working board"
        elif results.get("browser", {}).get("ok"):
            message = f"Opened {name} in Edge · {act} on Working board"
        if seed:
            message += f" · seed: {seed[:80]}"
        return _receipt(
            True,
            it,
            mode,
            steps,
            results,
            seed,
            message,
            dry_run=dry_run,
            extra={"board_intent": act, "url": url or None},
        )

    # ---- Default: desktop and/or browser open ----
    mode = "open"
    desktop_ok = False
    browser_ok = False

    # Prefer desktop for known apps (Discord, Slack, …)
    try_desktop = bool(desk_id) and open_desktop and prefer_n in ("auto", "desktop")
    try_browser = bool(url) and open_browser and prefer_n in ("auto", "browser")

    if try_desktop and prefer_n == "desktop":
        # force desktop only first
        pass
    if try_desktop:
        probe = _probe_desktop(desk_id)
        results["desktop_probe"] = probe
        if probe.get("available"):
            if dry_run:
                steps.append(
                    {
                        "step": "desktop",
                        "app": desk_id,
                        "resolved": probe.get("resolved"),
                        "status": "planned",
                    }
                )
                desktop_ok = True
            else:
                dr = _open_desktop(desk_id, args="")
                results["desktop"] = dr
                desktop_ok = bool(dr.get("ok"))
                steps.append(
                    {
                        "step": "desktop",
                        "app": desk_id,
                        "ok": desktop_ok,
                        "resolved": dr.get("resolved") or probe.get("resolved"),
                        "status": "done" if desktop_ok else "failed",
                        "message": dr.get("message") or dr.get("error"),
                    }
                )
        else:
            steps.append(
                {
                    "step": "desktop",
                    "app": desk_id,
                    "status": "unavailable",
                    "error": probe.get("error") or "not installed",
                }
            )

    # Browser: always for pure web; fallback when desktop missing; also when prefer=browser
    need_browser = try_browser and (
        prefer_n == "browser"
        or not desk_id
        or not desktop_ok
        or (prefer_n == "auto" and act == "open" and url and not desk_id)
    )
    # For desktop-first apps (discord), still open web only if desktop failed
    if try_browser and not desktop_ok and url:
        need_browser = True
    # Dual-open optional: catalog flag open_both
    if it.get("open_both") and try_browser and url and desktop_ok:
        need_browser = True

    if need_browser and url:
        if dry_run:
            steps.append({"step": "browser", "url": url, "status": "planned"})
            browser_ok = True
        else:
            br = _open_browser(url, profile=profile)
            results["browser"] = br
            browser_ok = bool(br.get("ok"))
            steps.append(
                {
                    "step": "browser",
                    "url": url,
                    "ok": browser_ok,
                    "status": "done" if browser_ok else "failed",
                    "message": br.get("message") or br.get("error"),
                }
            )

    ok = desktop_ok or browser_ok or dry_run and bool(steps)
    if not steps:
        # Last resort: mark as planned open with whatever we have
        if url:
            steps.append({"step": "browser", "url": url, "status": "planned" if dry_run else "skipped"})
            ok = True
        else:
            return _receipt(
                False,
                it,
                mode,
                steps,
                results,
                seed,
                f"No executable surface for {name}",
                dry_run=dry_run,
            )

    if dry_run:
        if desktop_ok and browser_ok:
            message = f"Would open {name} (desktop + browser)"
        elif desktop_ok:
            message = f"Would open {name} desktop app"
        elif browser_ok:
            message = f"Would open {name} in Edge"
        else:
            message = f"Planned {name}"
    elif desktop_ok and not browser_ok:
        message = f"Opened {name} desktop app"
    elif browser_ok and not desktop_ok:
        message = f"Opened {name} in Edge"
    elif desktop_ok and browser_ok:
        message = f"Opened {name} (desktop + browser)"
    else:
        message = f"Tried {name}"

    if seed and not dry_run:
        message += " · prompt ready"

    return _receipt(
        ok if not dry_run else True,
        it,
        mode,
        steps,
        results,
        seed,
        message,
        dry_run=dry_run,
        extra={"desktop_app": desk_id or None, "url": url or None},
    )


def _receipt(
    ok: bool,
    it: Dict[str, Any],
    mode: str,
    steps: List[Dict[str, Any]],
    results: Dict[str, Any],
    seed: str,
    message: str,
    *,
    dry_run: bool,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": ok,
        "schema": "pocket.integrations.execute.v1",
        "id": it.get("id"),
        "name": it.get("name"),
        "category": it.get("category"),
        "action": it.get("action"),
        "mode": mode,
        "dry_run": dry_run,
        "prompt": seed,
        "steps": steps,
        "results": results,
        "message": message,
        "at": time.time(),
        "executable": True,
    }
    if extra:
        out.update(extra)
    return out


def execute_all(
    *,
    dry_run: bool = True,
    only: Optional[List[str]] = None,
    prefer: str = "auto",
) -> Dict[str, Any]:
    """Run (or plan) every integration — used for readiness / smoke."""
    ids = only or [str(i.get("id")) for i in INTEGRATIONS]
    rows: List[Dict[str, Any]] = []
    ok_n = 0
    fail_n = 0
    for iid in ids:
        r = execute(iid, dry_run=dry_run, prefer=prefer)
        rows.append(
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "ok": r.get("ok"),
                "mode": r.get("mode"),
                "message": r.get("message"),
                "steps": [
                    {"step": s.get("step"), "status": s.get("status"), "app": s.get("app"), "url": s.get("url")}
                    for s in (r.get("steps") or [])
                ],
            }
        )
        if r.get("ok"):
            ok_n += 1
        else:
            fail_n += 1
    return {
        "ok": fail_n == 0,
        "schema": "pocket.integrations.execute_all.v1",
        "count": len(rows),
        "ok_count": ok_n,
        "fail_count": fail_n,
        "dry_run": dry_run,
        "results": rows,
        "at": time.time(),
    }


def readiness() -> Dict[str, Any]:
    """Per-integration executable readiness (desktop installed? url? board?)."""
    rows = []
    desktop_ready = 0
    browser_ready = 0
    board_ready = 0
    host_ready = 0
    for it in INTEGRATIONS:
        iid = str(it.get("id"))
        act = str(it.get("action") or "open").lower()
        url = str(it.get("url") or "")
        desk_id = str(it.get("desktop_app") or DESKTOP_MAP.get(iid) or "")
        entry: Dict[str, Any] = {
            "id": iid,
            "name": it.get("name"),
            "action": act,
            "executable": True,
            "surfaces": [],
        }
        if act in ("working", "tab", "screen", "agent"):
            entry["surfaces"].append(act)
            host_ready += 1
        if act in BOARD_ACTIONS:
            entry["surfaces"].append(f"board:{act}")
            board_ready += 1
        if desk_id:
            probe = _probe_desktop(desk_id)
            entry["desktop"] = {
                "app": desk_id,
                "available": bool(probe.get("available")),
                "resolved": probe.get("resolved"),
            }
            entry["surfaces"].append("desktop")
            if probe.get("available"):
                desktop_ready += 1
        if url:
            entry["url"] = url
            entry["surfaces"].append("browser")
            browser_ready += 1
        if not entry["surfaces"]:
            entry["executable"] = False
        rows.append(entry)
    return {
        "ok": True,
        "schema": "pocket.integrations.readiness.v1",
        "count": len(rows),
        "desktop_available": desktop_ready,
        "browser_url": browser_ready,
        "board_intents": board_ready,
        "host_actions": host_ready,
        "integrations": rows,
        "at": time.time(),
    }
