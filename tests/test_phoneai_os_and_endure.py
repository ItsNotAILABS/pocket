from pocket.phoneai_os_ui import phoneai_os_html, phoneai_system_html


def test_kernel_and_os_are_distinct():
    k = phoneai_os_html()
    o = phoneai_system_html()
    assert "PhoneAI Kernel" in k
    assert "PhoneAI OS" in o
    assert "/phoneai/os" in k
    assert "Codex" in o


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
    assert len(r["receipts"]) == 3
    assert "Endure" in (r.get("summary") or "")
