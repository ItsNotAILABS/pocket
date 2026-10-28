"""Nebius Token Factory lane — config seam, key gate, and wire format.

The live-account path needs the owner's NEBIUS_API_KEY, so everything here
runs against either no key (deterministic refusal) or a local mock server
that speaks the OpenAI-compatible shape Token Factory documents. Nothing in
this file touches the real Nebius endpoint.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from pocket.nebius_api import chat, models, save, status

TEST_KEY = "sk-" + "nebius-test-key"  # concatenated: never a token-shaped literal in source


@pytest.fixture(autouse=True)
def _isolated_cfg(tmp_path, monkeypatch):
    monkeypatch.setattr("pocket.nebius_api.CFG", tmp_path / "nebius.json")
    monkeypatch.setattr("pocket.nebius_api.ROOT", tmp_path)
    for var in ("NEBIUS_API_KEY", "NEBIUS_BASE_URL", "NEBIUS_MODEL"):
        monkeypatch.delenv(var, raising=False)


def test_save_and_status_no_network():
    st = save(api_key=TEST_KEY, model="nvidia/nemotron-3-nano-30b-a3b")
    assert st["configured"] is True
    assert st["provider"] == "nebius-token-factory"
    assert st["model"] == "nvidia/nemotron-3-nano-30b-a3b"
    assert st["base_url"] == "https://api.tokenfactory.nebius.com/v1"
    assert st["key_prefix"] == TEST_KEY[:12] + "…"
    assert TEST_KEY not in str(st)


def test_status_unconfigured_by_default():
    st = status()
    assert st["configured"] is False
    assert st["ok"] is False
    assert st["key_prefix"] == ""


def test_env_key_configures_without_file(monkeypatch):
    monkeypatch.setenv("NEBIUS_API_KEY", "sk-env-key-123456")
    st = status()
    assert st["configured"] is True
    assert st["key_prefix"].startswith("sk-env-key-1")


def test_chat_requires_key():
    r = chat("hi")
    assert r["ok"] is False
    assert r["engine"] == "nebius"
    assert "not configured" in (r.get("error") or "")


def test_models_requires_key():
    r = models()
    assert r["ok"] is False
    assert "not configured" in (r.get("error") or "")


class _MockTokenFactory(BaseHTTPRequestHandler):
    seen = {}

    def log_message(self, *args):  # keep test output clean
        pass

    def _reply(self, code, payload):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        type(self).seen["auth"] = self.headers.get("Authorization")
        if self.path.endswith("/models"):
            self._reply(200, {"data": [{"id": "nvidia/nemotron-3-nano-30b-a3b"}, {"id": "nvidia/nemotron-3-ultra-550b-a55b"}]})
        else:
            self._reply(404, {"error": "nope"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        type(self).seen["auth"] = self.headers.get("Authorization")
        type(self).seen["body"] = body
        if self.path.endswith("/chat/completions"):
            if body.get("model") == "force-401":
                self._reply(401, {"error": {"message": "invalid api key"}})
                return
            self._reply(
                200,
                {
                    "id": "chatcmpl-mock-1",
                    "model": body.get("model"),
                    "choices": [{"message": {"role": "assistant", "content": "mock nemotron reply"}}],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 4, "total_tokens": 15},
                },
            )
        else:
            self._reply(404, {"error": "nope"})


@pytest.fixture()
def mock_factory():
    _MockTokenFactory.seen = {}
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _MockTokenFactory)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    save(api_key=TEST_KEY, base_url=f"http://127.0.0.1:{port}/v1")
    yield _MockTokenFactory.seen
    srv.shutdown()


def test_chat_against_local_mock(mock_factory):
    r = chat("Write today's brief", system="grounded only")
    assert r["ok"] is True
    assert r["engine"] == "nebius"
    assert r["reply"] == "mock nemotron reply"
    assert r["model"] == "nvidia/nemotron-3-nano-30b-a3b"
    assert r["usage"]["total_tokens"] == 15
    # wire format: bearer auth + OpenAI chat shape + configured default model
    assert mock_factory["auth"] == "Bearer " + TEST_KEY
    body = mock_factory["body"]
    assert body["model"] == "nvidia/nemotron-3-nano-30b-a3b"
    assert body["messages"][0] == {"role": "system", "content": "grounded only"}
    assert body["messages"][1]["role"] == "user"


def test_models_against_local_mock(mock_factory):
    r = models()
    assert r["ok"] is True
    assert r["count"] == 2
    assert "nvidia/nemotron-3-ultra-550b-a55b" in r["models"]
    assert mock_factory["auth"] == "Bearer " + TEST_KEY


def test_chat_http_error_surfaces(mock_factory):
    r = chat("hi", model="force-401")
    assert r["ok"] is False
    assert r["http"] == 401
    assert "invalid api key" in (r.get("error") or "")
