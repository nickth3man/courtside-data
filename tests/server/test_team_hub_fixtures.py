"""Team Hub fixture transport tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from courtside_data.server.fixtures import (
    MissingFixtureError,
    fixture_seasons_for_team,
    fixture_url_map,
)


def _write_fixture(raw_root: Path, endpoint_name: str, filename: str) -> Path:
    path = raw_root / endpoint_name / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<html></html>", encoding="utf-8")
    return path


def test_team_only_fixture_url_map_uses_team_identifier_file(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path, "franchise_history", "BOS.html")

    mapping = fixture_url_map("franchise_history", {"team_abbreviation": "BOS"}, raw_root=tmp_path)

    assert mapping == {"https://www.basketball-reference.com/teams/BOS/": fixture}


def test_team_season_fixture_url_map_uses_team_and_year_file(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path, "team_roster", "BOS_2024.html")

    mapping = fixture_url_map(
        "team_roster",
        {"team_abbreviation": "BOS", "season_end_year": 2024},
        raw_root=tmp_path,
    )

    assert mapping == {"https://www.basketball-reference.com/teams/BOS/2024.html": fixture}


def test_team_injury_report_uses_default_fixture_for_every_team_season(tmp_path: Path) -> None:
    fixture = _write_fixture(tmp_path, "team_injury_report", "default.html")

    mapping = fixture_url_map(
        "team_injury_report",
        {"team_abbreviation": "LAL", "season_end_year": 2021},
        raw_root=tmp_path,
    )

    assert mapping == {"https://www.basketball-reference.com/friv/injuries.fcgi": fixture}


def test_team_fixture_url_map_raises_for_missing_team_file(tmp_path: Path) -> None:
    with pytest.raises(MissingFixtureError, match="Missing fixture file"):
        fixture_url_map(
            "team_roster",
            {"team_abbreviation": "BOS", "season_end_year": 2024},
            raw_root=tmp_path,
        )


def test_fixture_seasons_for_team_groups_seasons_by_endpoint(tmp_path: Path) -> None:
    _write_fixture(tmp_path, "team_roster", "BOS_2024.html")
    _write_fixture(tmp_path, "team_roster", "BOS_1980.html")
    _write_fixture(tmp_path, "team_splits", "BOS_2024.html")
    _write_fixture(tmp_path, "team_roster", "LAL_2023.html")
    _write_fixture(tmp_path, "team_roster", "BOS_notes.html")

    assert fixture_seasons_for_team("BOS", raw_root=tmp_path) == {
        "team_roster": [2024, 1980],
        "team_splits": [2024],
    }
