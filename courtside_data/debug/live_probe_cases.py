"""Live-audit sample parameters for ``python -m courtside_data.debug.probe``.

These overrides are used *only* by the live debug probe to select recent,
dense parameter sets instead of the oldest historical cases from the
offline fixture manifest. This reduces noisy but expected nulls and
``invalid_*_value`` drops in probe reports for historical data.

Offline regression tests continue to use ``tests.fixture_manifest.ALL_CASES``
unchanged.
"""

from __future__ import annotations

from typing import Any

from courtside_data.endpoints import ENDPOINTS

LIVE_AUDIT_SOURCE = "live_audit"

# Recent dense seasons (2024) that produce complete modern tables.
# These seasons are already exercised in the test suite for many endpoints.
LIVE_AUDIT_OVERRIDES: dict[str, dict[str, Any]] = {
    # Historical year fixtures (1965) produced many invalid_team_value drops.
    "draft_picks": {"season_end_year": 2024},
    # 1955-era league per-game table had many missing team / sparse rate stats.
    "league_per_game_stats": {"season_end_year": 2024},
    # 1973-era league totals had historical team and zero-denom issues.
    "league_totals": {"season_end_year": 2024},
    # 1980 rookies table lacked a "team" column entirely.
    "rookie_stats": {"season_end_year": 2024},
    # 1974 awards page used old data shapes.
    "season_awards": {"season_end_year": 2024},
    # 1980 season schedule had many null schedule fields + team issues.
    "season_schedule": {"season_end_year": 2024},
    # 1974 team-and-opponent used historical team names.
    "team_and_opponent": {"team_abbreviation": "BOS", "season_end_year": 2024},
}


# Fail fast at import time if an override key is not a real endpoint.
_unknown = sorted(set(LIVE_AUDIT_OVERRIDES) - set(ENDPOINTS))
if _unknown:
    raise RuntimeError(
        f"Unknown endpoint(s) in LIVE_AUDIT_OVERRIDES: {_unknown}. Either remove the key or register the endpoint."
    )


def get_live_audit_sample(endpoint_name: str) -> dict[str, Any] | None:
    """Return the live-audit params dict for an endpoint, or None if no override."""
    return LIVE_AUDIT_OVERRIDES.get(endpoint_name)
