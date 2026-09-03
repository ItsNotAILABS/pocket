from pocket.phoneai_os_ui import phoneai_os_html, phoneai_system_html


def test_kernel_and_os_are_distinct():
    k = phoneai_os_html()
    o = phoneai_system_html()
    assert "PhoneAI Kernel" in k
    assert "PhoneAI OS" in o
    assert "/phoneai/os" in k
    assert "Codex" in o


def test_catalog_only_ready_engines(monkeypatch):
    from pocket.engines import catalog

    monkeypatch.setattr(
        "pocket.model_clis.detect",
        lambda spec: {"available": spec["id"] in ("grok",), "path": "/bin/grok" if spec["id"] == "grok" else ""},
    )
    monkeypatch.setattr(
        "pocket.internal_models.registry.list_models",
        lambda: [{"id": "auro", "name": "Auro", "ready": True, "kind": "internal"}],
    )
    c = catalog()
    assert "codex" not in c["desk"]
    assert "codex" not in c["first_class"]
    assert "codex" not in c["ready"]
    assert "grok" in c["desk"]
    assert "auro" in c["ready"]


def test_endure_native_cannot_claim_learning_without_stateful_eval(monkeypatch):
    from pocket.auro_endure import run

    monkeypatch.setattr(
        "pocket.auro_endure._native",
        lambda *a, **k: {"ok": True, "learning": True, "text": "pretend"},
    )
    r = run("stay alive", experiments=1, cycles=0)
    assert r["native"] is True
    assert r["learning"] is False


def test_endure_fallback(monkeypatch):
    from pocket.auro_endure import run

    class Fake:
        def as_dict(self):
            return {"ok": True, "text": "kept going", "model_id": "auro"}

    monkeypatch.setattr("pocket.auro_endure._native", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no auro root")))
    monkeypatch.setattr("pocket.internal_models.registry.express_one", lambda *a, **k: Fake())
    r = run("stay alive", experiments=2, cycles=1)
    assert r["ok"] is True
    assert r["schema"] == "pocket.auro.endure.v1"
    assert r["native"] is False
    assert r["learning"] is False
    assert r.get("stateful_eval") is False
    assert "best" not in r or r.get("best") in (None, {})
    assert len(r["receipts"]) == 3
    assert "not learning" in (r.get("summary") or "").lower()
