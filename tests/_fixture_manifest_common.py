"""Shared primitives for the offline fixture manifest."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from courtside_data.endpoints import EndpointSpec

from tests.fixture_transport import FixtureValue

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
RAW_ROOT: Path = PROJECT_ROOT / "raw"

BASE_URL = "https://www.basketball-reference.com"


@dataclass(frozen=True, slots=True)
class Case:
    """One offline test case: an endpoint plus a specific parameter set."""

    endpoint_name: str
    params: dict
    url_to_file: dict[str, FixtureValue]
    id: str


# Pin the repr/debug class path to the public ``tests.fixture_manifest``
# location; ``Case`` is defined here but re-homed for its repr.
Case.__module__ = "tests.fixture_manifest"


ResolveResult = tuple[list[Case] | None, str | None]

MONTH_RE = re.compile(r"^([0-9]{4})_([0-9]{1,2})_([0-9]{1,2})$")
TEAM_DATE_RE = re.compile(r"^([A-Z]{2,3})_([0-9]{4})_([0-9]{1,2})_([0-9]{1,2})$")
TEAM_YEAR_RE = re.compile(r"^([A-Z]{2,3})_([0-9]{4})$")
YEAR_RE = re.compile(r"^([0-9]{4})$")
PLAYER_YEAR_RE = re.compile(r"^([a-z]+\d{2})_([0-9]{4})$")
GAME_ID_RE = re.compile(r"^(\d{8})(\d)([A-Z]{2,3})$")


def case_id(endpoint_name: str, params: dict) -> str:
    """Build a pytest-safe id from the endpoint name and params."""
    if not params:
        return endpoint_name
    parts = [endpoint_name]
    for key in sorted(params):
        parts.append(_sanitize(params[key]))
    return "-".join(parts)


def render_url(endpoint: EndpointSpec, params: dict) -> str:
    """Render the absolute Basketball-Reference URL for an endpoint call."""
    return BASE_URL + endpoint.path.format(**params)


def list_html(dir_: Path) -> list[Path]:
    """List HTML files in deterministic order."""
    if not dir_.is_dir():
        return []
    return sorted(path for path in dir_.iterdir() if path.suffix.lower() == ".html")


def make_case(endpoint_name: str, params: dict, url_to_file: dict[str, FixtureValue]) -> Case:
    """Create a manifest case with the canonical id format."""
    return Case(
        endpoint_name=endpoint_name,
        params=params,
        url_to_file=url_to_file,
        id=case_id(endpoint_name, params),
    )


def _sanitize(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-")
