"""Tests for pocket.agent_approval (POCKET-AGENTIC-APPROVAL/1.0).

Pytest-style; also runnable directly: PYTHONPATH=src python tests/test_agent_approval.py
Uses an isolated POCKET_AGENT_APPROVAL_HOME per test run (never touches the
operator's real ~/.pocket/agent_approval).
"""

import json
import os
import shutil
import tempfile

HOME = tempfile.mkdtemp(prefix="pocket-approval-test-")
os.environ["POCKET_AGENT_APPROVAL_HOME"] = HOME

from pocket import agent_approval as aa  # noqa: E402


def _reset():
    for name in ("requests.json", "bindings.json"):
        p = os.path.join(HOME, name)
        if os.path.exists(p):
            os.remove(p)
    rdir = os.path.join(HOME, "receipts")
    if os.path.isdir(rdir):
        shutil.rmtree(rdir)


def _receipts(event):
    rdir = os.path.join(HOME, "receipts")
    out = []
    if not os.path.isdir(rdir):
        return out
    for f in sorted(os.listdir(rdir)):
        if not f.endswith(".json"):
            continue
        body = json.load(open(os.path.join(rdir, f)))
        if body.get("subject") == "pocket.agent-approval." + event:
            out.append(body)
    return out


def test_issue_code_shape():
    _reset()
    r = aa.issue(device_id="iphone-1", app_id="photo-digest",
                 scope="owner-capability", capability="artifact-owner")
    assert r["ok"], r
    code = r["code"]
    assert len(code) == 6
    assert all(c in aa.CODE_ALPHABET for c in code)
    assert r["ttl_s"] == 600
    # raw code must not appear in any receipt
    for f in os.listdir(os.path.join(HOME, "receipts")):
        body = open(os.path.join(HOME, "receipts", f)).read()
        assert code not in body, "raw code leaked into receipt " + f
    rec = _receipts("request.issued")
    assert len(rec) == 1
    assert rec[0]["schema"] == "mesie.receipt.v1"
    assert rec[0]["hash"].startswith("sha256:")


def test_approve_exact_match_creates_binding():
    _reset()
    r = aa.issue(device_id="iphone-1", app_id="photo-digest",
                 scope="owner-capability", capability="artifact-owner")
    a = aa.approve(code=r["code"], approver="owner-agent")
    assert a["ok"], a
    assert a["binding_id"]
    c = aa.check(device_id="iphone-1", app_id="photo-digest",
                 scope="owner-capability", capability="artifact-owner")
    assert c["granted"] is True, c
    assert c["binding_id"] == a["binding_id"]
    rec = _receipts("request.approved")
    assert len(rec) == 1
    assert rec[0]["outputs"]["binding_id"] == a["binding_id"]


def test_approve_normalizes_case_and_whitespace():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    a = aa.approve(code="  " + r["code"].lower() + "\n")
    assert a["ok"], a


def test_approve_wrong_code_denied_and_receipted():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    wrong = "ZZZZZZ" if r["code"] != "ZZZZZZ" else "QQQQQQ"
    a = aa.approve(code=wrong)
    assert a["ok"] is False, a
    assert "no pending request matches" in a["error"]
    c = aa.check(device_id="d", app_id="a", scope="s")
    assert c["granted"] is False
    rec = _receipts("request.denied")
    assert len(rec) == 1
    assert wrong not in json.dumps(rec[0]), "attempted code leaked plaintext"


def test_approve_expired_request_rejected():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c", ttl_s=1)
    # force expiry without sleeping
    rows = json.load(open(os.path.join(HOME, "requests.json")))
    rows[0]["expires_at"] = 1.0
    json.dump(rows, open(os.path.join(HOME, "requests.json"), "w"))
    a = aa.approve(code=r["code"])
    assert a["ok"] is False, a
    assert "no pending request matches" in a["error"]
    c = aa.check(device_id="d", app_id="a", scope="s")
    assert c["granted"] is False


def test_double_approve_rejected():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    assert aa.approve(code=r["code"])["ok"]
    a2 = aa.approve(code=r["code"])
    assert a2["ok"] is False, a2


def test_unauthorized_approver_rejected():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c",
                 approvers=["owner-agent"])
    a = aa.approve(code=r["code"], approver="random-agent")
    assert a["ok"] is False, a
    assert "not authorized" in a["error"]
    assert aa.check(device_id="d", app_id="a", scope="s")["granted"] is False


def test_revoke_binding():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    a = aa.approve(code=r["code"])
    assert aa.check(device_id="d", app_id="a", scope="s")["granted"] is True
    rv = aa.revoke_binding(binding_id=a["binding_id"])
    assert rv["ok"] and rv["count"] == 1, rv
    assert aa.check(device_id="d", app_id="a", scope="s")["granted"] is False
    rec = _receipts("binding.revoked")
    assert len(rec) == 1


def test_scope_isolation_and_wildcard():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="photos.read", capability="c")
    assert aa.approve(code=r["code"])["ok"]
    assert aa.check(device_id="d", app_id="a", scope="photos.read")["granted"] is True
    assert aa.check(device_id="d", app_id="a", scope="photos.write")["granted"] is False
    assert aa.check(device_id="d", app_id="other-app", scope="photos.read")["granted"] is False
    r2 = aa.issue(device_id="d", app_id="a", scope="*", capability="c")
    assert aa.approve(code=r2["code"])["ok"]
    assert aa.check(device_id="d", app_id="a", scope="photos.write")["granted"] is True


def test_list_pending_masks_codes():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    lp = aa.list_pending()
    assert lp["count"] == 1
    row = lp["requests"][0]
    assert r["code"] not in json.dumps(row), "full code exposed in list"
    assert row["code_hint"] == r["code"][:2] + "**" + r["code"][-2:]
    # after approval it leaves the pending list
    assert aa.approve(code=r["code"])["ok"]
    assert aa.list_pending()["count"] == 0


def test_deny_explicit():
    _reset()
    r = aa.issue(device_id="d", app_id="a", scope="s", capability="c")
    d = aa.deny(code=r["code"], reason="not my device")
    assert d["ok"] and d["status"] == "denied", d
    assert aa.check(device_id="d", app_id="a", scope="s")["granted"] is False
    assert aa.approve(code=r["code"])["ok"] is False


TESTS = [v for k, v in sorted(globals().items())
         if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", t.__name__, "->", repr(e))
    print("%d/%d passed" % (len(TESTS) - failed, len(TESTS)))
    shutil.rmtree(HOME, ignore_errors=True)
    raise SystemExit(1 if failed else 0)
