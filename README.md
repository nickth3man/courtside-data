# Courtside Data

A typed Python client for [Basketball Reference](https://www.basketball-reference.com). Courtside Data exposes an explicit, schema-backed API for NBA stats, with process-wide rate limiting, offline HTML fixtures, and JSON / CSV / DataFrame output.

The public API is intentionally typed-only. Raw Basketball-Reference pages in `raw/` are development fixtures, not public endpoints.

## Installation

```bash
pip install courtside-data
```

Requires Python 3.12 or newer.

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
from courtside_data.domain import OutputType

client.league_per_game_stats(
    season_end_year=2024,
    output_type=OutputType.CSV,
    output_file_path="stats.csv",
)

# Or get a pandas DataFrame
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

The authoritative list of served endpoints is the `ENDPOINTS` registry in the [`courtside_data/endpoints/`](courtside_data/endpoints/) package (assembled in `_registry.py`), or at runtime:

```bash
courtside-data list
```

No static list is maintained here — the code is the source of truth. An endpoint name appearing anywhere in this repo outside of that registry does not mean it is fully implemented and tested. For the rendered field tables and per-endpoint metadata, see the [API reference](docs/api/endpoints.md).

## Documentation

Rendered docs are published at <https://nickth3man.github.io/courtside-data>. Source lives under [`docs/`](docs/):

- [Endpoint Runtime](docs/architecture/endpoints.md) — how `EndpointSpec`, `EndpointMetadata`, `WorkflowSpec`, and the generic-table path drive every call.
- [Schemas](docs/api/schemas.md) — the typed `BRRow` Pydantic models returned by each endpoint (auto-generated from source).
- [Endpoints](docs/api/endpoints.md) — the `ENDPOINTS` registry and `EndpointSpec` reference (auto-generated from source).

Schema and endpoint field tables in those pages are generated from source via mkdocstrings — do not hand-edit them; update the docstrings and rebuild.

## Raw Fixture Corpus

The `raw/` directory stores downloaded Basketball-Reference HTML pages. These fixtures are used to regression-test typed endpoints without live network calls and to preserve edge cases across old seasons, renamed teams, playoff tables, and unusual page layouts.

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

[**`AGENTS.md`**](AGENTS.md) is the authoritative guide for the dev toolchain: environment setup (`uv sync` with the PEP 735 `dev` group), the Ruff + ty + pytest-xdist workflow, the full set of `uv run task <name>` tasks, the live endpoint probe, environment variables, and the one-command pre-commit gate.

Quick reference:

```bash
# Install with dev dependencies (PEP 735 dev group)
uv sync

# Run the offline fixture-replay suite in parallel
uv run pytest tests -n auto

# Full pre-commit gate: lint + format check + type + tests
uv run task audit
```

## Lineage and Attribution

This project is derived from
[Jae Bradley's basketball_reference_web_scraper](https://github.com/jaebradley/basketball_reference_web_scraper),
licensed under the [MIT License](LICENSE).

The original project provided the initial package structure, core NBA endpoints,
parsing pipeline, output writers, and test approach. This project is independently
maintained and extends that foundation with typed endpoint schemas, generic table
parsing primitives, rate limiting, fixture tooling, and updated packaging.

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
