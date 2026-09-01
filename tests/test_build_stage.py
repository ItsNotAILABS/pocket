from pocket.app_ui import HTML
from pocket.phoneai_os_ui import phoneai_os_html, phoneai_twin_html
from pocket.workspace_stage import CSS, HTML as WS


def test_desk_has_square_workspace_stage():
    assert "ws-stage" in HTML
    assert 'id="buildStage"' in HTML
    assert "setBuildStage" in HTML
    assert "ws-chrome" in HTML
    assert "fillRealWorkspace" in HTML
    assert "bb-eye" not in HTML
    assert "startBuildDust" not in HTML
    assert "ws-code" in WS
    assert "wsFiles" in WS


def test_phoneai_landscape_computer_and_workspace():
    home = phoneai_os_html()
    assert "orientation:landscape" in home
    assert "body.desk" in home
    assert "display:contents" in home
    assert "coverWorkspaceWith" in home
    assert "ws-stage" in home
    work = phoneai_twin_html()
    assert "ws-stage" in work
    assert "setBuildStage" in work
