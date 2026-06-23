"""Unit tests for output-layer coercion helpers."""

from __future__ import annotations

import warnings

from courtside_data.output._coercions import coerce_years_experience


def test_coerce_years_experience_rookie_marker() -> None:
    assert coerce_years_experience("R") is None
    assert coerce_years_experience("r") is None


def test_coerce_years_experience_numeric() -> None:
    assert coerce_years_experience("5") == 5
    assert coerce_years_experience(5) == 5


def test_coerce_years_experience_empty() -> None:
    assert coerce_years_experience("") is None
    assert coerce_years_experience("   ") is None


def test_coerce_years_experience_no_warning_for_rookie() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert coerce_years_experience("R") is None
    assert not caught
