# Courtside Data

A comprehensive Python client for [Basketball Reference](https://www.basketball-reference.com) with 50+ endpoints, rate limiting, and offline fixture testing.

## Installation

```bash
pip install courtside-data
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
client.league_per_game_stats(
    season_end_year=2024,
    output_type="csv",
    output_file_path="stats.csv",
)
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

Courtside Data includes built-in rate limiting to be respectful to Basketball Reference:

- **Default:** 3.5 second interval with 1.2 second jitter
- **Configure via constructor:**
  ```python
  http_service = HTTPService(parser=ParserService(), rate_limit_interval=5.0)
  ```
- **Configure via environment variables:**
  ```bash
  export BASKETBALL_REF_RATE_LIMIT_INTERVAL=3.5
  export BASKETBALL_REF_RATE_LIMIT_JITTER=1.2
  ```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage report
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
