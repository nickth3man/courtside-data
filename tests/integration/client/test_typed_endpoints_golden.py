from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
import pytest
from parsel import Selector
from pydantic import AliasChoices

from courtside_data import client
from courtside_data.client._runner import _validate_row_model_rows
from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM
from courtside_data.endpoints import ENDPOINTS, TableEndpoint
from courtside_data.errors import MissingPlayerSlug
from courtside_data.http_service import HTTPService
from courtside_data.schemas import ROW_ADAPTERS
from courtside_data.schemas._base import BRRow
from courtside_data.tables import GenericTable, extract_commented_table, parse_transaction_list
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures

EXPECTED_PATH = Path(__file__).with_name("expected") / "typed_endpoints_golden.json"

GLOBAL_DROP_KEYS = frozenset(
    {
        "",
        "ranker",
        "counter",
        "DUMMY",
    }
)
SHARED_FIXTURE_ENDPOINTS = {
    "friv_7_game_playoff_series_outcomes_team_is_tied": "friv_7_game_playoff_series_outcomes_team_is_down",
    "friv_7_game_playoff_series_outcomes_team_is_up": "friv_7_game_playoff_series_outcomes_team_is_down",
}


def _is_dropped_key(key: str) -> bool:
    return key in GLOBAL_DROP_KEYS or key.startswith("header")


def _sidecar_for(html_path: Path) -> dict[str, Any]:
    sidecar_path = html_path.with_name(html_path.name + ".meta.json")
    if not sidecar_path.exists():
        return {}
    return json.loads(sidecar_path.read_text(encoding="utf8"))


def _html(relative_path: str) -> str:
    return raw_fixtures.read(relative_path)


def _find_table_by_id(selector: Selector, table_id: str) -> Selector | None:
    table = selector.css(f"table#{table_id}")
    if table:
        return table[0]
    return extract_commented_table(selector, table_id)


def _candidate_table_ids(endpoint: TableEndpoint, sidecar: dict[str, Any]) -> list[str]:
    ids = [table_id for table_id in sidecar.get("table_ids", []) if table_id]
    for table_id in (endpoint.table_id, *endpoint.fallback_table_ids, endpoint.commented_table_id):
        if table_id and "{" not in table_id and table_id not in ids:
            ids.append(table_id)
    return ids


def _generic_rows(endpoint: TableEndpoint, fixture: str) -> list[dict[str, Any]]:
    html_path = raw_fixtures.RAW_ROOT / fixture
    selector = Selector(text=_html(fixture))
    table = None
    for table_id in _candidate_table_ids(endpoint, _sidecar_for(html_path)):
        table = _find_table_by_id(selector, table_id)
        if table is not None:
            break
    if table is None and endpoint.table_id is None and endpoint.commented_table_id is None:
        tables = selector.css("table")
        table = tables[0] if tables else None
    if table is None:
        if endpoint.transaction_list_fallback:
            return parse_transaction_list(selector)
        return []

    rows = [
        row.to_dict()
        for row in GenericTable(
            table,
            use_header_fallback=endpoint.use_header_fallback,
            exclude_summary_rows=endpoint.exclude_summary_rows,
        ).rows
    ]
    if endpoint.projection is not None:
        rows = [{key: row.get(key, "") for key in endpoint.projection} for row in rows]
    return rows


class FixtureHTTPService(HTTPService):
    def __init__(self, fixtures: list[str]) -> None:
        self._fixtures_by_url: dict[str, tuple[str, str]] = {}
        for fixture in fixtures:
            path = raw_fixtures.RAW_ROOT / fixture
            text = path.read_text(encoding="utf8")
            sidecar = _sidecar_for(path)
            for key in ("url", "final_url"):
                url = sidecar.get(key)
                if url:
                    self._fixtures_by_url[url] = (text, sidecar.get("final_url") or url)

    def _lookup(self, url: str, **kwargs: Any) -> tuple[str, str]:
        if kwargs.get("params"):
            url = f"{url}?{urlencode(kwargs['params'])}"
        if url in self._fixtures_by_url:
            return self._fixtures_by_url[url]
        raise AssertionError(f"Fixture URL was not registered: {url}")

    def _get_selector(self, url: str) -> Selector:
        text, _ = self._lookup(url)
        return Selector(text=text)

    def _get(self, url: str, **kwargs: Any) -> httpx.Response:
        text, final_url = self._lookup(url, **kwargs)
        request = httpx.Request("GET", final_url)
        return httpx.Response(200, text=text, request=request)


def _custom_rows(endpoint_name: str, case: dict[str, Any]) -> list[dict[str, Any]]:
    service = FixtureHTTPService(case["fixtures"])
    params = case.get("params", {})
    if endpoint_name == "play_by_play" and isinstance(params.get("home_team"), str):
        params = {**params, "home_team": TEAM_ABBREVIATIONS_TO_TEAM[params["home_team"]]}

    if endpoint_name == "players_season_totals":
        selector = Selector(text=_html(case["fixtures"][0]))
        return service._player_totals_rows(selector, "totals_stats", include_combined=False)
    if endpoint_name == "players_advanced_season_totals":
        selector = Selector(text=_html(case["fixtures"][0]))
        return service._player_totals_rows(
            selector,
            "advanced",
            include_combined=params.get("include_combined_values", False),
        )
    if endpoint_name == "player_box_scores":
        selector = Selector(text=_html(case["fixtures"][0]))
        table = service._find_table(selector, "stats")
        assert table is not None
        rows = []
        for row_index, (row, metadata) in enumerate(service._raw_rows_from_table(table)):
            row["slug"] = service._slug_from_metadata(metadata, "player")
            service._require_slug("player_box_scores", row, row_index)
            rows.append(row)
        return rows
    if endpoint_name in {"regular_season_player_box_scores", "playoff_player_box_scores"}:
        selector = Selector(text=_html(case["fixtures"][0]))
        table_id = "player_game_log_post" if endpoint_name.startswith("playoff") else "player_game_log_reg"
        table = service._find_table(selector, table_id)
        assert table is not None
        return service._player_season_box_score_rows(table, include_inactive_games=params.get("include_inactive_games", False))
    if endpoint_name == "search":
        return service.search(**params)["players"]

    return getattr(service, endpoint_name)(**params)


def _raw_rows(endpoint_name: str, case: dict[str, Any]) -> list[dict[str, Any]]:
    endpoint = ENDPOINTS[endpoint_name]
    if endpoint.custom:
        return _custom_rows(endpoint_name, case)
    return _generic_rows(endpoint, case["fixtures"][0])


def _accepted_keys(model: type[BRRow]) -> set[str]:
    keys = set()
    for name, field in model.model_fields.items():
        alias = field.validation_alias
        if alias is None:
            keys.add(name)
        elif isinstance(alias, str):
            keys.add(alias)
        elif isinstance(alias, AliasChoices):
            keys.update(choice for choice in alias.choices if isinstance(choice, str))
        else:
            keys.add(name)
    return keys


def _observed_columns(rows: list[dict[str, Any]]) -> list[str]:
    seen = {}
    for row in rows:
        for key in row:
            if not _is_dropped_key(key):
                seen.setdefault(key, None)
    return list(seen)


def _valid_raw_rows(endpoint_name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    adapter = ROW_ADAPTERS[endpoint_name]
    valid_rows = []
    for row in rows:
        try:
            adapter.validate_python([row])
        except Exception:
            continue
        valid_rows.append(row)
    return valid_rows


def _golden_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(EXPECTED_PATH.read_text(encoding="utf8"))
    typed_endpoint_names = {name for name, endpoint in ENDPOINTS.items() if endpoint.row_model is not None}
    assert set(payload) == typed_endpoint_names
    return payload


@pytest.mark.parametrize(
    "endpoint_name",
    sorted(name for name, endpoint in ENDPOINTS.items() if endpoint.row_model is not None),
)
def test_typed_endpoint_raw_fixture_matches_golden_contract(endpoint_name: str):
    case = _golden_cases()[endpoint_name]
    if reason := case.get("skip"):
        pytest.skip(reason)

    rows = _raw_rows(endpoint_name, case)
    columns = _observed_columns(rows)

    assert len(rows) == case["row_count"]
    assert columns == case["columns"]
    assert not any(re.fullmatch(r"col_\d+", key) for key in columns)

    model = ENDPOINTS[endpoint_name].row_model
    assert model is not None
    unexpected = set(columns) - _accepted_keys(model)
    assert not unexpected

    valid_rows = _valid_raw_rows(endpoint_name, rows)
    assert len(valid_rows) == case["validated_row_count"]
    assert valid_rows or not rows
    assert len(_validate_row_model_rows(model, rows)) == len(valid_rows)


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
    manifest = json.loads((raw_fixtures.RAW_ROOT / "_manifest.json").read_text(encoding="utf8"))
    assert manifest["stats"]["persistent_failures"] == 0
    assert manifest["endpoint_counts"]["league_per_100_possessions"] == 3
    assert not any(fixture["path"] == "league_per_100_possessions/1973.html" for fixture in manifest["fixtures"])


def _play_by_play_fixtures() -> list[str]:
    return [
        "team_box_scores/2017_01_01/index.html",
        "play_by_play/ATL_2017_01_01/201701010ATL.html",
    ]


def _default_params(endpoint_name: str, fixture: str) -> dict[str, Any]:
    stem = Path(fixture).stem
    if endpoint_name in {"standings", "playoff_bracket", "players_season_totals"}:
        return {"season_end_year": int(stem)}
    if endpoint_name == "players_advanced_season_totals":
        year, include_combined = stem.split("_", maxsplit=1)
        return {"season_end_year": int(year), "include_combined_values": include_combined == "true"}
    if endpoint_name == "player_box_scores":
        year, month, day = stem.split("_")
        return {"year": int(year), "month": int(month), "day": int(day)}
    if endpoint_name in {"regular_season_player_box_scores", "playoff_player_box_scores"}:
        player_identifier, year = stem.rsplit("_", maxsplit=1)
        return {"player_identifier": player_identifier, "season_end_year": int(year), "include_inactive_games": False}
    if endpoint_name == "team_box_scores":
        year, month, day = Path(fixture).parts[1].split("_")
        return {"year": int(year), "month": int(month), "day": int(day)}
    if endpoint_name == "season_schedule":
        return {"season_end_year": int(Path(fixture).parts[1])}
    if endpoint_name == "standings_by_date":
        year = Path(fixture).name.split("_", maxsplit=1)[0]
        return {"season_end_year": int(year)}
    if endpoint_name == "play_by_play":
        team_abbreviation, year, month, day = Path(fixture).parts[1].split("_")
        return {
            "home_team": TEAM_ABBREVIATIONS_TO_TEAM[team_abbreviation],
            "year": int(year),
            "month": int(month),
            "day": int(day),
        }
    if endpoint_name == "search":
        return {"term": Path(fixture).stem.replace("_", " ")}
    return {}
