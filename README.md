# Courtside Data

A comprehensive Python client for [Basketball Reference](https://www.basketball-reference.com) with 50+ endpoints, rate limiting, and offline fixture testing.

## Installation

```bash
pip install courtside-data

# with pandas DataFrame support
pip install "courtside-data[pandas]"
```

## Quick Start

```python
from courtside_data import client

# Get league-wide per-game stats for the 2024 season
stats = client.league_per_game_stats(season_end_year=2024)

# Get a team roster
roster = client.team_roster(season_end_year=2024, team_abbreviation="BOS")

# Get player career stats
career = client.player_career_stats(player_identifier="jamesle01")

# Save to CSV
from courtside_data.data import OutputType

client.league_per_game_stats(
    season_end_year=2024,
    output_type=OutputType.CSV,
    output_file_path="stats.csv",
)

# Or get a pandas DataFrame (requires the pandas extra)
frame = client.league_per_game_stats(season_end_year=2024, output_type=OutputType.DATAFRAME)
```

The module-level functions share one HTTP session per process (connection
reuse, one response cache). To control session behavior, use
`CourtsideClient`:

```python
from courtside_data import CourtsideClient

client = CourtsideClient(cache=False)  # also: headers=..., impersonate=..., timeout=...
roster = client.team_roster(team_abbreviation="BOS", season_end_year=2024)
```

## Command line

Every endpoint is also a CLI subcommand:

```bash
courtside-data list
courtside-data league_per_game_stats --season-end-year 2024
courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 \
    --output-type csv --output-file roster.csv
```

## Endpoints

| Category    | Endpoint                       | Description                              |
| ----------- | ------------------------------ | ---------------------------------------- |
| **League**    | `league_per_game_stats`          | League-wide per-game statistics          |
|             | `league_per_36_minutes`          | Per-36-minute stats                      |
|             | `league_per_100_possessions`     | Per-100-possessions stats                |
|             | `league_totals`                  | Season totals for all players            |
|             | `league_shooting`                | Shooting by distance                     |
|             | `rookie_stats`                   | Rookie season statistics                 |
|             | `standings_by_date`              | Standings on a specific date             |
|             | `attendance`                     | Team attendance figures                  |
|             | `league_transactions`            | League-wide transactions                 |
| **Player**    | `player_career_stats`            | Career stats for a player                |
|             | `player_splits`                  | Home/away splits                         |
|             | `player_on_off`                  | On/off court impact                      |
|             | `player_shot_charts`             | Shot chart data                          |
|             | `player_adjusted_shooting`       | Adjusted shooting stats                  |
|             | `player_play_by_play`            | Play-by-play stats                       |
|             | `player_game_highs`              | Career game highs                        |
|             | `player_all_star`                | All-Star game appearances                |
|             | `player_similarity_scores`       | Similarity scores                        |
|             | `player_salaries`                | Salary information                       |
|             | `player_playoff_series`          | Playoff series stats                     |
| **Team**      | `team_roster`                    | Team roster                              |
|             | `team_schedule`                  | Full season schedule                     |
|             | `team_injury_report`             | Current injury report                    |
|             | `team_and_opponent`              | Team vs opponent stats                   |
|             | `team_misc_four_factors`         | Four factors and miscellaneous stats     |
|             | `team_transactions`              | Team transactions                        |
|             | `team_splits`                    | Team splits                              |
|             | `team_contracts`                 | Player contracts                         |
|             | `team_lineups`                   | Lineup data                              |
|             | `team_starting_lineups`          | Starting lineup data                     |
|             | `team_on_off`                    | Team on/off court impact                 |
|             | `team_opponent_stats`            | Opponent statistics                      |
|             | `franchise_history`              | Franchise history                        |
| **Draft/Awards** | `draft_picks`                  | Draft pick history                       |
|             | `season_leaders`                 | Season statistical leaders               |
|             | `career_leaders`                 | Career statistical leaders               |
|             | `playoff_bracket`                | Playoff bracket results                  |
|             | `season_awards`                  | Season awards (MVP, ROY, etc.)           |
| **Playoffs**  | `playoff_per_game`               | Playoff per-game stats                   |
|             | `playoff_totals`                 | Playoff totals                           |

See [REFERENCE.md](REFERENCE.md) for detailed endpoint documentation including URL patterns and table IDs.

## Rate Limiting

Basketball Reference bans clients that exceed ~20 requests per minute, so
rate limiting is built in and **not configurable**:

- Requests are paced at a 6-second minimum interval (plus jitter, ~9 req/min),
  enforced process-wide across all sessions and threads.
- `Retry-After` headers are honored on retries.
- If Basketball Reference jails the session (a `Retry-After` longer than
  5 minutes), a circuit breaker makes further calls fail fast with
  `RateLimitJailed` instead of burning requests against the ban. The jail
  state is persisted to `.cache/courtside/jail.json` so restarted processes
  honor it too.

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage report

# Regenerate REFERENCE.md after changing the endpoint registry
uv run python scripts/generate_reference.py
```

## Lineage and Attribution

This project is derived from
[Jae Bradley's basketball_reference_web_scraper](https://github.com/jaebradley/basketball_reference_web_scraper),
licensed under the [MIT License](LICENSE).

The original project provided the initial package structure, core NBA endpoints,
parsing pipeline, output writers, and test approach. This project is independently
maintained and extends that foundation with ~40 additional endpoints, generic table
parsing, rate limiting, fixture tooling, and updated packaging.

### Original Project Contributors

- [Jae Bradley](https://github.com/jaebradley) (creator)
- [@DaiJunyan](https://github.com/DaiJunyan)
- [@ecallahan5](https://github.com/ecallahan5)
- [@Yotamho](https://github.com/Yotamho)
- [@ntsirakis](https://github.com/ntsirakis)
- [@allanbelliti](https://github.com/allanbelliti)
- [@krlu](https://github.com/krlu)
- [@aaronbannin](https://github.com/aaronbannin)
- [@benjaminmesser](https://github.com/benjaminmesser)

## License

[MIT](LICENSE) — Original work Copyright (c) 2018 Jae Bradley. Modifications and additional work Copyright (c) 2026 Nicolas Alexander.
