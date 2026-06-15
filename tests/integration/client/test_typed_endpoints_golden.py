from __future__ import annotations

import pytest
from parsel import Selector

from courtside_data import client
from courtside_data.endpoints import ENDPOINTS
from courtside_data.errors import MissingPlayerSlug
from courtside_data.http_service import HTTPService
from courtside_data.schemas import ROW_ADAPTERS
from courtside_data.tables import GenericTable, parse_transaction_list
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures


def test_playoff_bracket_parses_top_level_series_only():
    with requests_mock.Mocker() as m:
        m.get(
            "https://www.basketball-reference.com/playoffs/NBA_2024.html",
            text=raw_fixtures.playoff_bracket(2024),
            status_code=200,
        )

        rows = client.playoff_bracket(2024, raw=True)

    assert len(rows) == 15
    assert not any(any(key.startswith("col_") for key in row) for row in rows)
    assert rows[0] == {
        "series": "Finals",
        "team": "Boston Celtics",
        "result": "over Dallas Mavericks (4-1)",
    }
    assert all("Game " not in row["series"] for row in rows)


@pytest.mark.parametrize(
    ("endpoint_name", "fixture_name"),
    [
        ("league_per_game_stats", "1955.html"),
        ("league_totals", "1973.html"),
        ("league_per_36_minutes", "2015.html"),
        ("league_shooting", "1997.html"),
        ("playoff_per_game", "1980.html"),
        ("playoff_totals", "1974.html"),
    ],
)
def test_opt_in_summary_row_filter_removes_league_average(endpoint_name, fixture_name):
    endpoint = ENDPOINTS[endpoint_name]
    table_id = endpoint.table_id
    assert table_id is not None
    html = raw_fixtures.RAW_ROOT.joinpath(endpoint_name, fixture_name).read_text(encoding="utf8")
    table = Selector(text=html).css(f"table#{table_id}")[0]

    unfiltered = [row.to_dict() for row in GenericTable(table).rows]
    filtered = [row.to_dict() for row in GenericTable(table, exclude_summary_rows=endpoint.exclude_summary_rows).rows]

    assert endpoint.exclude_summary_rows is True
    assert len(filtered) == len(unfiltered) - 1
    assert all("League Average" not in row.values() for row in filtered)


@pytest.mark.parametrize(
    ("endpoint_name", "path", "table_id"),
    [
        ("players_season_totals", "players_season_totals/2024.html", "totals_stats"),
        ("players_advanced_season_totals", "players_advanced_season_totals/2024_false.html", "advanced"),
    ],
)
def test_player_totals_capture_all_real_fixture_columns(endpoint_name, path, table_id):
    selector = Selector(text=raw_fixtures.read(path))
    table = selector.css(f"table#{table_id}")[0]
    first_row = GenericTable(table).rows[0].to_dict()
    adapter = ROW_ADAPTERS[endpoint_name]

    if endpoint_name == "players_season_totals":
        first_row["slug"] = "fake01"
    else:
        first_row["slug"] = "fake01"
        first_row["is_combined_totals"] = False

    validated = adapter.validate_python([first_row])[0]
    dumped = validated.model_dump()

    assert not set(first_row) - {
        field.validation_alias
        for field in type(validated).model_fields.values()
        if isinstance(field.validation_alias, str)
    } - {"ranker", "is_combined_totals"}
    assert set(dumped) == set(type(validated).model_fields)


def test_missing_player_slug_raises_named_domain_error():
    service = HTTPService.__new__(HTTPService)
    row = {"name_display": "No Slug", "team_name_abbr": "BOS"}

    with pytest.raises(MissingPlayerSlug, match="players_season_totals"):
        service._require_slug("players_season_totals", row, 3)


@pytest.mark.parametrize(
    "relative_path",
    [
        "team_transactions/BOS_2024.html",
        "league_transactions/2024.html",
    ],
)
def test_transaction_parser_emits_one_row_per_selected_paragraph(relative_path):
    selector = Selector(text=raw_fixtures.read(relative_path))
    parsed = parse_transaction_list(selector)
    explicit_transactions = selector.xpath(
        '//ul[contains(concat(" ", normalize-space(@class), " "), " page_index ")]'
        '/li/p[contains(concat(" ", normalize-space(@class), " "), " transaction ")]'
    )
    fallback_transactions = selector.xpath(
        '//ul[contains(concat(" ", normalize-space(@class), " "), " page_index ")]'
        '/li[not(p[contains(concat(" ", normalize-space(@class), " "), " transaction ")])]'
        "/p[normalize-space()]"
    )

    assert len(parsed) == len(explicit_transactions) + len(fallback_transactions)


def test_raw_failure_directory_is_empty():
    failure_dir = raw_fixtures.RAW_ROOT / "_failures"
    assert not list(failure_dir.glob("*.failed.html"))


def test_negative_404_fixture_is_not_counted_as_positive_manifest_fixture():
    import json

    manifest = json.loads((raw_fixtures.RAW_ROOT / "_manifest.json").read_text(encoding="utf8"))
    assert manifest["stats"]["persistent_failures"] == 0
    assert manifest["endpoint_counts"]["league_per_100_possessions"] == 3
    assert not any(fixture["path"] == "league_per_100_possessions/1973.html" for fixture in manifest["fixtures"])
