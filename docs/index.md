# Courtside Data

A typed Python client for [Basketball Reference](https://www.basketball-reference.com). Courtside Data exposes an explicit, schema-backed API for NBA stats, with process-wide rate limiting, TLS impersonation, an offline HTML fixture corpus, and JSON / CSV / DataFrame output.

The public API is intentionally typed-only. Raw Basketball-Reference pages in `raw/` are development fixtures, not public endpoints.

## Quick start

```bash
pip install courtside-data
```

```python
from courtside_data import client

# League-wide per-game stats for the 2024 season
stats = client.league_per_game_stats(season_end_year=2024)

# A team roster
roster = client.team_roster(season_end_year=2024, team_abbreviation="BOS")

# Save to CSV
from courtside_data.data import OutputType

client.league_per_game_stats(
    season_end_year=2024,
    output_type=OutputType.CSV,
    output_file_path="stats.csv",
)
```

Every endpoint is also a CLI subcommand:

```bash
courtside-data list
courtside-data league_per_game_stats --season-end-year 2024
```

## Where to go next

- **[API: Schemas](api/schemas.md)** — the Pydantic v2 row models behind every endpoint, auto-generated from source via mkdocstrings.
- **[API: Endpoints](api/endpoints.md)** — the declarative `TableEndpoint` registry and its 50+ entries.
- **[Source, CLI, rate-limiting policy & endpoint catalog](https://github.com/nickth3man/courtside-data)** — the repository README is the source of truth for installation, lineage, and attribution.
