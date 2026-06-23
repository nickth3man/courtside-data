"""Synthetic error-case construction for the fixture manifest."""

from __future__ import annotations

from courtside_data.endpoints import ENDPOINTS

from tests._fixture_manifest_common import RAW_ROOT, Case, render_url


def build_error_cases() -> list[Case]:
    """Build synthetic 404 cases used to exercise domain error mapping."""
    cases: list[Case] = []

    if (RAW_ROOT / "errors" / "invalid_team_404.html").is_file():
        params = {"team_abbreviation": "BOGUS", "season_end_year": 2024}
        endpoint = ENDPOINTS["team_roster"]
        cases.append(
            Case(
                endpoint_name="error-invalid_team",
                params=params,
                url_to_file={render_url(endpoint, params): (404, None)},
                id="error-invalid_team",
            )
        )

    if (RAW_ROOT / "errors" / "invalid_player_404.html").is_file():
        params = {"player_identifier": "fakefake99"}
        endpoint = ENDPOINTS["player_career_stats"]
        cases.append(
            Case(
                endpoint_name="error-invalid_player",
                params=params,
                url_to_file={render_url(endpoint, params): (404, None)},
                id="error-invalid_player",
            )
        )

    if (RAW_ROOT / "errors").is_dir():
        params = {"season_end_year": 1900}
        endpoint = ENDPOINTS["draft_picks"]
        cases.append(
            Case(
                endpoint_name="error-invalid_season",
                params=params,
                url_to_file={render_url(endpoint, params): (404, None)},
                id="error-invalid_season",
            )
        )

    return cases
