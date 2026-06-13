import json

from courtside_data.debug import DebugConfig, DebugTrace


def test_trace_redacts_sensitive_keys_and_exports_json():
    trace = DebugTrace(endpoint="search", params={"term": "james", "api_key": "secret"})

    trace.record("http", "request_prepare", authorization="Bearer abc", url="https://example.test")
    trace.artifact("headers", {"set-cookie": "session=abc", "content-type": "text/html"})

    payload = trace.to_dict()
    request_event = next(event for event in payload["events"] if event["event"] == "request_prepare")
    assert payload["params"]["api_key"] == "<redacted>"
    assert request_event["attributes"]["authorization"] == "<redacted>"
    assert request_event["severity_text"] == "INFO"
    assert request_event["severity_number"] == 9
    assert payload["runtime"]["service.name"] == "courtside-data"
    assert payload["runtime"]["telemetry.sdk.language"] == "python"
    assert payload["runtime"]["process.pid"] > 0
    assert payload["artifacts"]["headers"]["set-cookie"] == "<redacted>"

    encoded = trace.to_json()
    assert json.loads(encoded)["schema_version"] == 3


def test_trace_bounds_artifacts_and_records_index():
    trace = DebugTrace(
        endpoint="rows",
        params={},
        config=DebugConfig(max_artifact_items=3, artifact_sample="head_tail"),
    )

    trace.artifact("rows", [{"idx": idx} for idx in range(10)])

    assert trace.artifacts["rows"] == [{"idx": 0}, {"__debug_truncation__": 7}, {"idx": 9}]
    assert trace.artifact_index["rows"]["truncated"] is True
    assert trace.artifact_index["rows"]["original_count"] == 10
    assert trace.artifact_index["rows"]["stored_count"] == 3
    assert trace.artifact_index["rows"]["sha256"]


def test_trace_records_exception_and_jsonl_events():
    trace = DebugTrace(endpoint="validation", params={})

    try:
        with trace.span("validate rows", stage="validation"):
            raise ValueError("bad row")
    except ValueError as exc:
        trace.record_exception(exc, stage="validation", row_index=2)

    payload = trace.to_dict()
    event = next(event for event in payload["events"] if event["attributes"].get("row_index") == 2)
    span = payload["spans"][0]
    assert payload["status"]["code"] == "error"
    assert event["status"] == "error"
    assert event["severity_text"] == "ERROR"
    assert event["severity_number"] == 17
    assert event["attributes"]["exception.type"] == "ValueError"
    assert event["attributes"]["row_index"] == 2
    assert "ValueError: bad row" in event["attributes"]["exception.stacktrace"]
    assert span["name"] == "validate rows"
    assert span["status"] == "error"
    assert span["error_type"] == "ValueError"
    assert span["duration_ms"] is not None

    jsonl = trace.events_jsonl()
    assert any(event["event"] == "exception" for event in map(json.loads, jsonl.splitlines()))


def test_trace_metrics_stage_counts_and_row_diagnostics():
    trace = DebugTrace(endpoint="rows", params={})

    trace.metric("rows.total", 2)
    trace.observe_rows(
        "rows",
        [{"name": "A", "games": 1}, {"name": "", "extra": "x"}],
        expected_columns=("name", "games"),
    )

    payload = trace.to_dict()
    assert payload["metrics"]["rows.total"] == 2
    assert payload["stage_counts"]["debug"] >= 1
    diagnostics = payload["artifacts"]["rows_diagnostics"]
    assert diagnostics["row_count"] == 2
    assert diagnostics["extra_columns"] == ["extra"]
    assert diagnostics["by_column"]["games"]["missing_count"] == 1
    assert diagnostics["by_column"]["name"]["empty_count"] == 1


def test_trace_event_limit_tracks_dropped_events():
    trace = DebugTrace(endpoint="limited", params={}, config=DebugConfig(max_events=1, include_runtime=False))

    trace.record("stage", "one")
    trace.record("stage", "two")

    assert len(trace.events) == 1
    assert trace.dropped_events == 1
