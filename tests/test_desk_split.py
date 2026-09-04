"""Desk + Desktop/Edge keep agents side-by-side in one window."""

from pathlib import Path

from pocket.app_ui import HTML
from pocket.crew_ui import crew_html


def test_desk_has_split_and_spark():
    assert 'id="btnSplit"' in HTML
    assert "toggleSplit()" in HTML
    assert "sendPane(0)" in HTML
    assert "sendPane(1)" in HTML
    assert "split-stage" in HTML
    assert "pickAgent('spark')" in HTML
    assert "data-mode=\"spark\"" in HTML


def test_second_agent_auto_splits_same_window():
    assert "otherActive" in HTML
    assert "Side by side on this desk — two agents, one window" in HTML
    assert "runWorkflow('side_by_side')" in HTML
    assert "wantSplit" in HTML
    assert "q.get('split')" in HTML
    assert "tabQ==='crew'" in HTML
    assert "APP_TAB_ROUTES" in HTML
    assert "path:'/crew'" in HTML


def test_crew_stays_in_desk_window():
    html = crew_html()
    assert "/desk?split=1" in html
    assert "Desktop / Edge" in html or "Desktop/Edge" in html


def test_electron_menu_stays_on_desk():
    src = (Path(__file__).resolve().parents[1] / "desktop-electron" / "main.js").read_text(
        encoding="utf-8"
    )
    assert 'return base + "/desk"' in src
    assert "/desk?split=1" in src
    assert "/desk?agent=spark" in src
    assert "/desk?tab=crew" in src
