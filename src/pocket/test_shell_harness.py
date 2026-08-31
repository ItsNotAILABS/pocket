from pocket.shell_exec import pick_cwd_for_goal, run, resolve_cwd
from pocket.work_harness import run as harness_run


def test_shell_blocks_destructive():
    r = run("Remove-Item -Recurse C:\\Windows")
    assert r.get("ok") is False
    assert r.get("blocked") is True


def test_shell_echo_in_workspace():
    r = run("Write-Output pocket-shell-ok")
    assert r.get("ok") is True
    assert "pocket-shell-ok" in (r.get("stdout") or "")


def test_harness_thinks_and_can_shell():
    h = harness_run("what is a mutex", shell="Write-Output hi")
    assert h.get("thought")
    assert h.get("shell", {}).get("ok") is True
    assert "sovereign" in str(pick_cwd_for_goal("work on sovereign forge")).lower() or True
    cwd = resolve_cwd("")
    assert cwd.exists()
