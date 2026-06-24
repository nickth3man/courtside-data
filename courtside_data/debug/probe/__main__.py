"""Run ``python -m courtside_data.debug.probe`` to probe endpoints.

Usage::

    uv run python -m courtside_data.debug.probe
    uv run python -m courtside_data.debug.probe -e team_roster --params-json '{"team_abbreviation":"BOS"}'
"""

from courtside_data.debug.probe import main

if __name__ == "__main__":
    raise SystemExit(main())
