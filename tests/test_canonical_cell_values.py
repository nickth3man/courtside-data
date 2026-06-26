from __future__ import annotations

from datetime import date

import pytest
from courtside_data.output.columns import (
    PLAYER_ALL_STAR_COLUMN_NAMES,
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES,
    STANDINGS_BY_DATE_COLUMN_NAMES,
    TEAM_BOX_SCORES_COLUMN_NAMES,
    TEAM_LINEUPS_COLUMN_NAMES,
)
from courtside_data.parsing._table_shared import canonical_cell_value
from courtside_data.parsing.tables import GenericTable, extract_commented_table
from courtside_data.schemas._fields import ConferenceField, DivisionField
from courtside_data.schemas.players import PlayerSalariesRow
from courtside_data.schemas.standings import StandingsByDateRow
from courtside_data.schemas.teams import TeamContractsRow, TeamInjuryReportRow, TeamMiscFourFactorsRow, TeamRosterRow
from parsel import Selector
from pydantic import TypeAdapter


def test_canonical_cell_value_uses_csk_for_targeted_machine_fields() -> None:
    attrs = {"csk": "47607350"}

    assert canonical_cell_value("salary", "$47,607,350", attrs) == "47607350"
    assert canonical_cell_value("birth_date", "November 7, 1999", {"csk": "19991107"}) == "19991107"
    assert canonical_cell_value("date_update", "Mon, Mar 9, 2026", {"csk": "2026-03-09"}) == "2026-03-09"


def test_canonical_cell_value_preserves_display_values_for_non_targeted_csk_cells() -> None:
    assert canonical_cell_value("player", "Jayson Tatum", {"csk": "Tatum,Jayson"}) == "Jayson Tatum"
    assert canonical_cell_value("pos", "PF", {"csk": "4"}) == "PF"


def test_canonical_cell_value_extracts_roster_flag_code() -> None:
    attrs = {"class": "left f-i f-ca"}

    assert canonical_cell_value("flag", "ca CA", attrs) == "CA"


def test_team_roster_parser_and_schema_emit_canonical_date_and_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COURTSIDE_DATA_PARSE_BACKEND", "parsel")
    selector = Selector(
        text="""
        <table id="roster"><tbody><tr>
          <th data-stat="number">0</th>
          <td data-stat="player" csk="Tatum,Jayson">Jayson Tatum</td>
          <td data-stat="pos" csk="4">PF</td>
          <td data-stat="height" csk="80.0">6-8</td>
          <td data-stat="weight">210</td>
          <td data-stat="birth_date" csk="19980303">March 3, 1998</td>
          <td data-stat="flag"><span class="f-i f-us">us</span> US</td>
          <td data-stat="years_experience" csk="8">8</td>
          <td data-stat="college">Duke</td>
        </tr></tbody></table>
        """
    )

    raw_row = GenericTable(selector.css("table#roster")[0]).rows[0].to_dict()
    row = TeamRosterRow.model_validate(raw_row)

    assert raw_row["birth_date"] == "19980303"
    assert raw_row["flag"] == "US"
    assert raw_row["player"] == "Jayson Tatum"
    assert row.birth_date == date(1998, 3, 3)
    assert row.flag == "US"


def test_player_salary_schema_accepts_csk_salary() -> None:
    row = PlayerSalariesRow.model_validate(
        {"season": "2023-24", "team_name": "Los Angeles Lakers", "lg_id": "NBA", "salary": "47607350"}
    )

    assert row.salary == 47_607_350


def test_team_contract_schema_emits_numeric_age_and_salaries() -> None:
    row = TeamContractsRow.model_validate(
        {
            "player": "Jayson Tatum",
            "age_today": "28",
            "y1": "54126450",
            "y2": "$58,456,566",
            "remain_gtd": "242486496",
        }
    )

    assert row.age_today == 28
    assert row.y1 == 54_126_450
    assert row.y2 == 58_456_566
    assert row.y3 is None
    assert row.remain_gtd == 242_486_496


def test_team_injury_report_schema_emits_date() -> None:
    row = TeamInjuryReportRow.model_validate(
        {"player": "Egor Demin", "team_name": "Brooklyn Nets", "date_update": "2026-03-09", "note": "Out"}
    )

    assert row.date_update == date(2026, 3, 9)


def test_team_misc_four_factors_normalizes_mixed_percentage_scales() -> None:
    row = TeamMiscFourFactorsRow.model_validate(
        {"tov_pct": "10.8", "orb_pct": "24.9", "efg_pct": ".578", "fta_per_fga_pct": ".224", "drb_pct": "76.3"}
    )

    assert row.tov_pct == pytest.approx(0.108)
    assert row.orb_pct == pytest.approx(0.249)
    assert row.efg_pct == pytest.approx(0.578)
    assert row.fta_per_fga_pct == pytest.approx(0.224)
    assert row.drb_pct == pytest.approx(0.763)


def test_standings_by_date_exposes_structured_rank_fields() -> None:
    row = StandingsByDateRow.model_validate({"conference": "EASTERN", "date": "Oct 25, 2023", "1st": "BOS (1-0) T1"})

    assert row.first == "BOS (1-0) T1"
    assert row.first_team is not None
    assert row.first_team.value == "BOSTON CELTICS"
    assert row.first_wins == 1
    assert row.first_losses == 0
    assert row.first_tie_rank == 1


def test_historical_conference_and_division_labels_resolve() -> None:
    conference_adapter = TypeAdapter(ConferenceField)
    division_adapter = TypeAdapter(DivisionField)

    assert conference_adapter.validate_python("East").value == "EASTERN"
    assert conference_adapter.validate_python("West").value == "WESTERN"
    assert division_adapter.validate_python("Eastern Division").value == "EASTERN"
    assert division_adapter.validate_python("Western Division").value == "WESTERN"


def test_corrected_csv_contracts_include_issue_fields() -> None:
    for column in (
        "total_rebounds",
        "field_goal_percentage",
        "three_point_field_goal_percentage",
        "free_throw_percentage",
        "two_point_field_goal_percentage",
        "effective_field_goal_percentage",
        "made_two_point_field_goals",
        "attempted_two_point_field_goals",
    ):
        assert column in TEAM_BOX_SCORES_COLUMN_NAMES
        assert column in PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES

    assert "seconds_played" in PLAYER_ALL_STAR_COLUMN_NAMES
    assert "mp" not in PLAYER_ALL_STAR_COLUMN_NAMES
    assert "seconds_played" in TEAM_LINEUPS_COLUMN_NAMES
    assert "mp" not in TEAM_LINEUPS_COLUMN_NAMES
    assert "first_team" in STANDINGS_BY_DATE_COLUMN_NAMES
    assert "first_wins" in STANDINGS_BY_DATE_COLUMN_NAMES
    assert "first_losses" in STANDINGS_BY_DATE_COLUMN_NAMES
    assert "first_tie_rank" in STANDINGS_BY_DATE_COLUMN_NAMES


def test_commented_salary_table_parser_uses_csk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COURTSIDE_DATA_PARSE_BACKEND", "parsel")
    selector = Selector(
        text="""
        <html><body>
          <!--
          <table id="all_salaries"><tbody><tr>
            <th data-stat="season">2023-24</th>
            <td data-stat="team_name">Los Angeles Lakers</td>
            <td data-stat="lg_id">NBA</td>
            <td data-stat="salary" csk="47607350">$47,607,350</td>
          </tr></tbody></table>
          -->
        </body></html>
        """
    )
    table = extract_commented_table(selector, "all_salaries")
    assert table is not None

    raw_row = GenericTable(table).rows[0].to_dict()

    assert raw_row["salary"] == "47607350"
