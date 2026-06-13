from types import SimpleNamespace
from unittest import mock

from pydantic import BaseModel, TypeAdapter

from courtside_data.client import _runner
from courtside_data.errors import SchemaDriftError


class ExampleRow(BaseModel):
    player: str
    games: int


def _endpoint(path: str = "/leagues/NBA_{season_end_year}_totals.html"):
    return SimpleNamespace(row_model=ExampleRow, path=path)


def test_row_model_endpoint_returns_models_and_skips_legacy_pipeline():
    adapter = TypeAdapter(list[ExampleRow])

    with mock.patch.dict(_runner.ROW_ADAPTERS, {"example_endpoint": adapter}, clear=False):
        with mock.patch.object(_runner, "coerce_data", side_effect=AssertionError("coerce_data should not run")):
            with mock.patch.object(
                _runner, "validate_rows", side_effect=AssertionError("validate_rows should not run")
            ):
                result = _runner._execute(
                    service_call=lambda: [{"player": "Jayson Tatum", "games": "74"}],
                    endpoint=_endpoint(),
                    endpoint_name="example_endpoint",
                    endpoint_params={"season_end_year": 2024},
                )

    assert result == [ExampleRow(player="Jayson Tatum", games=74)]


def test_row_model_endpoint_raw_returns_extracted_rows_before_validation():
    adapter = TypeAdapter(list[ExampleRow])
    raw_rows = [{"player": "Jayson Tatum", "games": "not validated"}]

    with mock.patch.dict(_runner.ROW_ADAPTERS, {"example_endpoint": adapter}, clear=False):
        result = _runner._execute(
            service_call=lambda: {"rows": raw_rows},
            endpoint=_endpoint(),
            endpoint_name="example_endpoint",
            endpoint_params={"season_end_year": 2024},
            raw=True,
        )

    assert result == raw_rows


def test_row_model_validation_error_is_schema_drift_with_endpoint_context():
    adapter = TypeAdapter(list[ExampleRow])

    with mock.patch.dict(_runner.ROW_ADAPTERS, {"player_endpoint": adapter}, clear=False):
        try:
            _runner._execute(
                service_call=lambda: [{"games": "74"}],
                endpoint=_endpoint("/players/{player_identifier[0]}/{player_identifier}.html"),
                endpoint_name="player_endpoint",
                endpoint_params={"player_identifier": "tatumja01"},
            )
        except SchemaDriftError as error:
            assert error.endpoint_name == "player_endpoint"
            assert error.url == "https://www.basketball-reference.com/players/t/tatumja01.html"
            assert "player_endpoint" in str(error)
            assert "player" in str(error)
        else:
            raise AssertionError("Expected SchemaDriftError")
