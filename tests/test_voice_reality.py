from pocket.voice_reality import compile_envelope, executable_intent, spoken_summary


def test_code_voice_compiles_to_agent():
    env = compile_envelope("fix the tests and refactor the API", project="pocket")
    assert env["schema"] == "pocket.voice-reality-envelope.v1"
    assert env["intent"] == "code"
    assert env["agent"] == "pocket-agent"
    assert env["scope"]["project"] == "pocket"


def test_deploy_voice_requires_confirmation():
    env = compile_envelope("deploy this application to production", project="pocket")
    assert env["intent"] == "deploy"
    assert env["risk"] == "high"
    assert env["approval"] == "confirm"


def test_executable_intent_detection():
    assert executable_intent("build a web app")
    assert executable_intent("ship this")
    assert not executable_intent("what time is it")


def test_spoken_summary_reflects_state():
    run = {"state": "awaiting_confirmation", "envelope": {"intent": "deploy"}}
    assert "confirm" in spoken_summary(run).lower()
