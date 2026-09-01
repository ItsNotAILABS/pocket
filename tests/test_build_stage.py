from pocket.app_ui import HTML


def test_desk_has_build_stage_animation():
    assert 'id="buildStage"' in HTML
    assert "setBuildStage" in HTML
    assert "bb-eye" in HTML
    assert "startBuildDust" in HTML
    assert "bbWork" in HTML
