from pocket.browser_mode import open_windows_copilot
from pocket.step_agent import _lookup_and_bring_back, parse_steps


def test_lookup_does_not_open_copilot(monkeypatch):
    opened = []

    def fake_open(app, args=""):
        opened.append((app, args))
        return {"ok": True, "app": app}

    monkeypatch.setattr("pocket.desktop.open_app", fake_open)
    monkeypatch.setattr("pocket.web_research.search_web", lambda q, max_results=8: {"ok": True, "results": []})
    r = _lookup_and_bring_back("AI and markets", open_ui=True)
    assert "copilot" not in {a[0] for a in opened}
    opened.clear()
    r2 = _lookup_and_bring_back("AI and markets", open_ui=False)
    assert opened == []
    assert r.get("ok") is True
    assert r2.get("ok") is True


def test_parse_steps_lookup_stays_lookup():
    steps = parse_steps("lookup AI and markets")
    assert steps
    assert not any(s.lower().startswith("open copilot") for s in steps)


def test_copilot_explicit_gate(monkeypatch):
    monkeypatch.setenv("POCKET_COPILOT_AUTO", "0")
    r2 = open_windows_copilot(explicit=False)
    assert r2.get("skipped") is True
    opened = []

    def fake_popen(*a, **k):
        opened.append(a)
        class P:
            pass
        return P()

    monkeypatch.setattr("subprocess.Popen", fake_popen)
    r = open_windows_copilot(explicit=True)
    assert r.get("skipped") is not True
    assert r.get("ok") is True
    assert opened
    monkeypatch.delenv("POCKET_COPILOT_AUTO", raising=False)
    r3 = open_windows_copilot(explicit=False)
    assert r3.get("skipped") is True
