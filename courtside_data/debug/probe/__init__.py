"""Live endpoint probe: call each registry endpoint once and record outcomes.

Usage::

    uv run python -m courtside_data.debug.probe
    uv run python -m courtside_data.debug.probe --output logs/my_report.json
    uv run python -m courtside_data.debug.probe -e play_by_play -e team_roster
    uv run python -m courtside_data.debug.probe --endpoint friv_7_game_playoff_series_outcomes_team_is_tied
"""

# During the transition phase, re-export everything from the legacy module.
# As functions are extracted into sub-modules, replace these with direct imports.
from courtside_data.debug.probe._legacy import *  # noqa: F403

# Explicit imports for _prefixed names not in __all__ but used by external tests.
from courtside_data.debug.probe._legacy import (  # noqa: F401
    __all__,
    _default_enrichment,
    _infer_output_type,
    _preview_result,
    _sample_params_per_endpoint,
    _summarize_debug_events,
    _summarize_report,
    _summarize_row_counts,
)
