import json
from types import SimpleNamespace
from unittest import mock

from pydantic import BaseModel, TypeAdapter

from courtside_data.client import _runner
from courtside_data.debug import DebugTrace
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


def test_row_model_endpoint_debug_returns_data_and_trace(tmp_path, monkeypatch):
    monkeypatch.setenv("COURTSIDE_DEBUG_LOG_DIR", str(tmp_path))
    adapter = TypeAdapter(list[ExampleRow])
    trace = DebugTrace(endpoint="example_endpoint", params={"season_end_year": 2024})

    with mock.patch.dict(_runner.ROW_ADAPTERS, {"example_endpoint": adapter}, clear=False):
        result = _runner._execute(
            service_call=lambda: [{"player": "Jayson Tatum", "games": "74"}],
            endpoint=_endpoint(),
            endpoint_name="example_endpoint",
            endpoint_params={"season_end_year": 2024},
            debug=True,
            trace=trace,
        )

    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    assert log_files[0].name.endswith(f"_example_endpoint_{trace.trace_id.replace('-', '')[:8]}.json")
    logged = json.loads(log_files[0].read_text(encoding="utf8"))
    assert logged["data"] == [{"player": "Jayson Tatum", "games": 74}]
    assert logged["debug"]["endpoint"] == "example_endpoint"

    assert result["data"] == [ExampleRow(player="Jayson Tatum", games=74)]
    assert result["debug"]["schema_version"] == 3
    assert result["debug"]["endpoint"] == "example_endpoint"
    assert result["debug"]["metrics"]["debug.enabled"] is True
    assert result["debug"]["runtime"]["python_version"]
    assert result["debug"]["artifacts"]["service_values"] == [{"player": "Jayson Tatum", "games": "74"}]
    assert result["debug"]["artifacts"]["validated_rows"] == [{"player": "Jayson Tatum", "games": 74}]
    assert result["debug"]["artifacts"]["validated_rows_diagnostics"]["by_column"]["games"]["type_counts"] == {"int": 1}
    assert result["debug"]["artifact_index"]["service_values"]["stored"] is True
    assert [span["name"] for span in result["debug"]["spans"]] == ["service_call", "pydantic_validation"]
    assert all(span["duration_ms"] is not None for span in result["debug"]["spans"])
    assert [event["event"] for event in result["debug"]["events"]]


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
