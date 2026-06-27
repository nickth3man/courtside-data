"""CSV column contracts for box-score Basketball-Reference endpoints.

Box-score CSV contracts are derived from the Pydantic row models so the
writer cannot silently drift from JSON/model output when schemas gain fields.
"""

from __future__ import annotations

from pydantic import BaseModel

from courtside_data.schemas import boxscores as boxscore_schemas


def _schema_columns(row_model: type[BaseModel]) -> list[str]:
    return list(row_model.model_fields)


def _schema_prefix(row_model: type[BaseModel], before: str) -> list[str]:
    columns = _schema_columns(row_model)
    return columns[: columns.index(before)]


BOX_SCORE_STAT_COLUMN_NAMES = _schema_prefix(boxscore_schemas.PlayerBoxScoreRow, "slug")

BOX_SCORE_COLUMN_NAMES = _schema_columns(boxscore_schemas.PlayerBoxScoreRow)

PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES = _schema_columns(boxscore_schemas.RegularSeasonPlayerBoxScoreRow)

TEAM_BOX_SCORES_COLUMN_NAMES = _schema_columns(boxscore_schemas.TeamBoxScoreRow)


# -- Per-game box-score readers -------------------------------------------
# The matching row models live in courtside_data/schemas/boxscores.py.
# Keep these contracts schema-derived so CSV output stays aligned with each
# registered row model.

BOX_SCORE_PLAYER_ADVANCED_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScorePlayerAdvancedRow)

BOX_SCORE_TEAM_FOUR_FACTORS_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScoreTeamFourFactorsRow)

BOX_SCORE_LINE_SCORE_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScoreLineScoreRow)

BOX_SCORE_PLAYER_QUARTER_SPLITS_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScorePlayerQuarterSplitRow)

BOX_SCORE_GAME_INFO_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScoreGameInfoRow)

BOX_SCORE_PLAYER_BASIC_COLUMN_NAMES = _schema_columns(boxscore_schemas.BoxScorePlayerBasicRow)
