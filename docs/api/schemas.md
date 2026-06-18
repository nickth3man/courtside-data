# Schemas

The `courtside_data.schemas` package holds the Pydantic v2 row models that
validate raw `dict[str, str]` rows extracted from Basketball-Reference
tables. Each model subclasses [`BRRow`][courtside_data.schemas._base.BRRow]
and declares its column-to-attribute mapping via `Field(validation_alias=...)`
or `AliasChoices` against Basketball-Reference's `data-stat` keys.

The runner looks up a `TypeAdapter[list[BRRow]]` per endpoint in
[`ROW_ADAPTERS`][courtside_data.schemas._registry.ROW_ADAPTERS] and feeds
the adapter every raw row from the generic table pipeline. A model that
fails to validate raises `SchemaDriftError`, which the runner surfaces as
a clear drift signal.

## Base class

::: courtside_data.schemas._base.BRRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Registry

The `register(name, model)` helper is the single registration API. Domain
modules call it at import time with the endpoint name declared in
[`ENDPOINTS`][courtside_data.endpoints.ENDPOINTS] and the matching row
model.

::: courtside_data.schemas._registry.ROW_ADAPTERS
    options:
      show_root_heading: true
      show_root_full_path: false

::: courtside_data.schemas._registry.register
    options:
      show_root_heading: true
      show_root_full_path: false

## Field vocabulary

`courtside_data/schemas/_fields.py` defines the
`Annotated[Type, BeforeValidator(...)]` aliases that normalise raw
Basketball-Reference cell strings into typed Python values. The most
heavily used public aliases are listed below; see the source module for
the complete catalogue.

::: courtside_data.schemas._fields.BRIntOrNone
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.BRFloatOrNone
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.BRPercentage
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.SecondsPlayed
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.TeamField
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.PositionsField
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.BRDate
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

::: courtside_data.schemas._fields.BRDatetime
    options:
      show_root_heading: true
      show_root_full_path: false
      members: false

## League-wide tables

Row models for the per-season league tables under
`/leagues/NBA_{year}_*.html`, plus league-wide awards, leaders, and
attendance.

::: courtside_data.schemas.league.LeaguePerGameStatsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeaguePer36MinutesRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeaguePer100PossessionsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeagueTotalsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeagueShootingRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeaguePlayByPlayRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.RookieStatsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.AttendanceRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.LeagueTransactionRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.SeasonAwardsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.SeasonAwardsVotingRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.SeasonLeadersRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.league.CareerLeadersRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Playoff tables

Row models for playoff per-game, totals, bracket, and seven-game series
outcomes.

::: courtside_data.schemas.playoffs.PlayoffPerGameRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.playoffs.PlayoffTotalsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.playoffs.PlayoffBracketRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.playoffs.SevenGamePlayoffSeriesOutcomesRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.playoffs.PlayedGame
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Standings

::: courtside_data.schemas.standings.StandingsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.standings.StandingsByDateRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Draft

::: courtside_data.schemas.draft.DraftPicksRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Player pages

Row models for the per-player Basketball-Reference pages
(`/players/{id}/{player}.html` and the per-season sub-pages).

### Career / season totals

::: courtside_data.schemas.players.PlayerCareerStatsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerSeasonTotalsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerAdvancedSeasonTotalsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

### Playoff series, All-Star, game highs

::: courtside_data.schemas.players.PlayerPlayoffSeriesRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerAllStarRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerGameHighsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

### Shooting, play-by-play, similarity, salaries, shot charts

::: courtside_data.schemas.players.PlayerAdjustedShootingRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerPlayByPlayStatsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerSimilarityScoresRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerSalariesRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerShotChartsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

### Splits and on-off

::: courtside_data.schemas.players.PlayerSplitsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.players.PlayerOnOffRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Team pages

Row models for the per-team Basketball-Reference pages
(`/teams/{abbr}/{year}.html` and the per-season sub-pages).

### Roster, injuries, contracts, franchise history

::: courtside_data.schemas.teams.TeamRosterRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamInjuryReportRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamContractsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.FranchiseHistoryRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

### Stats aggregates

::: courtside_data.schemas.teams.TeamAndOpponentRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamOpponentStatsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamMiscFourFactorsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

### Schedule, transactions, splits, lineups, on-off

::: courtside_data.schemas.teams.TeamTransactionsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamSplitsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamLineupsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamStartingLineupsRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.teams.TeamOnOffRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Schedule

::: courtside_data.schemas.schedule.SeasonScheduleRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.schedule.TeamScheduleRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Box scores

Row models for the per-day leaders page and the per-game player game
logs (regular season and playoffs).

::: courtside_data.schemas.boxscores.PlayerBoxScoreRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.boxscores.RegularSeasonPlayerBoxScoreRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.boxscores.PlayoffPlayerBoxScoreRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

::: courtside_data.schemas.boxscores.TeamBoxScoreRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Play-by-play

::: courtside_data.schemas.playbyplay.PlayByPlayRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true

## Search

::: courtside_data.schemas.search.SearchResultRow
    options:
      show_root_heading: true
      show_root_full_path: false
      members: true
