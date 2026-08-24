package main

import "testing"

func TestCompileCode(t *testing.T) {
    e := compile("fix the tests and refactor the API", "req-1", "pocket", "/tmp/pocket")
    if e.Intent != "code" || e.Agent != "pocket-agent" || e.Action != "agent.run" {
        t.Fatalf("unexpected envelope: %+v", e)
    }
    if err := validate(e); err != nil {
        t.Fatal(err)
    }
}

func TestDeployNeedsConfirmation(t *testing.T) {
    e := compile("deploy this application", "req-2", "pocket", "/tmp/pocket")
    if e.Risk != "high" || e.Approval != "confirm" {
        t.Fatalf("deploy should be confirmation-gated: %+v", e)
    }
}

func TestSealDigestStableShape(t *testing.T) {
    e := compile("build an app", "req-3", "pocket", "/tmp/pocket")
    d := digest(map[string]any{"schema": e.Schema, "request_id": e.RequestID})
    if len(d) != len("sha256:")+64 {
        t.Fatalf("invalid digest: %s", d)
    }
}
