package main

import (
    "bufio"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "errors"
    "fmt"
    "os"
    "strings"
    "time"
)

type Scope struct {
    Tenant    string `json:"tenant"`
    Project   string `json:"project"`
    Session   string `json:"session"`
    Workspace string `json:"workspace"`
}

type Envelope struct {
    Schema       string                 `json:"schema"`
    RequestID    string                 `json:"request_id"`
    Origin       string                 `json:"origin"`
    Transcript   string                 `json:"transcript"`
    Intent       string                 `json:"intent"`
    Action       string                 `json:"action"`
    Agent        string                 `json:"agent"`
    ModelLane    string                 `json:"model_lane,omitempty"`
    Scope        Scope                  `json:"scope"`
    Risk         string                 `json:"risk"`
    Approval     string                 `json:"approval"`
    Parameters   map[string]any         `json:"parameters"`
    Acceptance   []string               `json:"acceptance"`
    State        string                 `json:"state"`
    Events       []map[string]any       `json:"events"`
    Artifacts    []map[string]any       `json:"artifacts"`
    Verification []map[string]any       `json:"verification"`
    Receipt      map[string]any         `json:"receipt,omitempty"`
    CreatedAt    string                 `json:"created_at"`
}

func classify(text string) (intent, action, agent, risk string) {
    low := strings.ToLower(text)
    intent, action, agent, risk = "assist", "agent.run", "pocket-agent", "low"
    switch {
    case strings.Contains(low, "deploy") || strings.Contains(low, "publish"):
        return "deploy", "deploy.plan", "sovereign-forge-os", "high"
    case strings.Contains(low, "build") || strings.Contains(low, "make") || strings.Contains(low, "create"):
        return "build", "build.execute", "pocket-agent", "medium"
    case strings.Contains(low, "code") || strings.Contains(low, "fix") || strings.Contains(low, "refactor") || strings.Contains(low, "test"):
        return "code", "agent.run", "pocket-agent", "medium"
    case strings.Contains(low, "research") || strings.Contains(low, "find out"):
        return "research", "research.skill.search", "researchers-hub", "low"
    case strings.Contains(low, "benchmark") || strings.Contains(low, "matrix"):
        return "compute", "compute.validate_matrices", "matdaemon", "low"
    }
    return
}

func normalizeApproval(risk string) string {
    if risk == "high" {
        return "confirm"
    }
    return "allow"
}

func digest(v any) string {
    b, _ := json.Marshal(v)
    h := sha256.Sum256(b)
    return "sha256:" + hex.EncodeToString(h[:])
}

func validate(e Envelope) error {
    if e.Schema != "pocket.voice-reality-envelope.v1" {
        return errors.New("invalid schema")
    }
    if strings.TrimSpace(e.RequestID) == "" || strings.TrimSpace(e.Transcript) == "" {
        return errors.New("request_id and transcript are required")
    }
    if e.Scope.Project == "" || e.Scope.Workspace == "" {
        return errors.New("project and workspace scope are required")
    }
    if e.Risk == "high" && e.Approval != "confirm" && e.Approval != "approved" {
        return errors.New("high-risk execution requires confirmation")
    }
    return nil
}

func compile(transcript, requestID, project, workspace string) Envelope {
    intent, action, agent, risk := classify(transcript)
    now := time.Now().UTC().Format(time.RFC3339Nano)
    return Envelope{
        Schema:     "pocket.voice-reality-envelope.v1",
        RequestID:  requestID,
        Origin:     "voice",
        Transcript: transcript,
        Intent:     intent,
        Action:     action,
        Agent:      agent,
        Scope: Scope{Project: project, Workspace: workspace, Session: requestID},
        Risk:       risk,
        Approval:   normalizeApproval(risk),
        Parameters: map[string]any{"prompt": transcript},
        Acceptance: []string{"execution receipt exists", "artifacts are hashed when produced", "verification result is attached"},
        State:      "compiled",
        Events: []map[string]any{{"type": "compiled", "at": now, "message": fmt.Sprintf("voice compiled to %s via %s", action, agent)}},
        Artifacts:    []map[string]any{},
        Verification: []map[string]any{},
        CreatedAt:    now,
    }
}

func main() {
    mode := "compile"
    if len(os.Args) > 1 {
        mode = os.Args[1]
    }
    var e Envelope
    dec := json.NewDecoder(bufio.NewReader(os.Stdin))
    if mode == "compile" {
        var req struct {
            Transcript string `json:"transcript"`
            RequestID  string `json:"request_id"`
            Project    string `json:"project"`
            Workspace  string `json:"workspace"`
        }
        if err := dec.Decode(&req); err != nil {
            panic(err)
        }
        e = compile(req.Transcript, req.RequestID, req.Project, req.Workspace)
    } else {
        if err := dec.Decode(&e); err != nil {
            panic(err)
        }
    }
    if err := validate(e); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(2)
    }
    if mode == "seal" {
        base := map[string]any{
            "schema": e.Schema, "request_id": e.RequestID, "action": e.Action, "agent": e.Agent,
            "state": e.State, "artifacts": e.Artifacts, "verification": e.Verification,
        }
        e.Receipt = map[string]any{
            "schema": "pocket.voice-reality-receipt.v1",
            "request_id": e.RequestID,
            "status": e.State,
            "digest": digest(base),
            "sealed_at": time.Now().UTC().Format(time.RFC3339Nano),
        }
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(e)
}
