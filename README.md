# Courtside Data

![Python version](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-261230)
[![Docs](https://img.shields.io/badge/docs-mkdocs%20material-blue)](https://nickth3man.github.io/courtside-data)

A typed Python client for [Basketball Reference](https://www.basketball-reference.com). Courtside Data exposes an explicit, schema-backed API for NBA stats — 50+ endpoints, Pydantic v2 row models, process-wide rate limiting, TLS impersonation, an offline HTML fixture corpus, and JSON / CSV / DataFrame output.

The public API is intentionally typed-only. Raw Basketball-Reference pages in [`raw/`](raw/) are development fixtures, not public endpoints.

**Highlights**

- **Typed end to end** — every endpoint validates raw HTML rows through a Pydantic `BRRow` model; schema drift raises a clear error instead of silently bad data.
- **One declarative registry** — `ENDPOINTS` drives the Python client, the generated CLI, and the rendered API docs from a single source of truth.
- **Safe by default** — a process-wide pacer and circuit breaker keep you under Basketball Reference's ban threshold (not configurable).
- **Flexible output** — return validated Pydantic models, or serialize to JSON, CSV, or a pandas `DataFrame` per call.
- **CLI mirrors the API** — every endpoint is a subcommand, so scripts and notebooks use the same names and parameters.

## Installation

```bash
pip install courtside-data
# or, with uv
uv add courtside-data
```

Requires Python 3.12 or newer.

## Quick Start

```python
from courtside_data import client

# League-wide per-game stats for the 2024 season
stats = client.league_per_game_stats(season_end_year=2024)

# A team roster
roster = client.team_roster(season_end_year=2024, team_abbreviation="BOS")

# A player's career stats
career = client.player_career_stats(player_identifier="jamesle01")
```

Every endpoint is also a CLI subcommand:

```bash
courtside-data list
courtside-data league_per_game_stats --season-end-year 2024
courtside-data team_roster --team-abbreviation BOS --season-end-year 2024
```

## Usage

### Module-level functions vs. `CourtsideClient`

The module-level functions in `courtside_data.client` share **one HTTP session per process** (connection reuse, one response cache). This is the simplest way to call the library:

```python
from courtside_data import client

roster = client.team_roster(team_abbreviation="BOS", season_end_year=2024)
```

When you need control over the session — caching, headers, TLS impersonation, or timeouts — instantiate [`CourtsideClient`](courtside_data/client/courtside_client.py):

```python
from courtside_data import CourtsideClient

client = CourtsideClient(
    cache=False,            # disable the hishel HTTP response cache
    impersonate="chrome131",  # curl-cffi TLS-impersonation target
    # headers=...,
    # timeout=...,
)

roster = client.team_roster(team_abbreviation="BOS", season_end_year=2024)
```

A `CourtsideClient` owns its own session; the module-level functions continue to share theirs. Rate limiting is **not** configurable on either surface — it is enforced globally across all sessions in the process (see [Rate Limiting](#rate-limiting)).

### Output types

By default, the Python API returns the validated Pydantic row models directly (no serialization). Pass [`OutputType`](courtside_data/domain/enums.py) to change the shape:

- `OutputType.JSON` — serialize rows to a JSON string
- `OutputType.CSV` (with `output_file_path`) — write a CSV file
- `OutputType.DATAFRAME` — return a pandas `DataFrame`

```python
from courtside_data.domain import OutputType

# Default: validated Pydantic model instances
rows = client.league_per_game_stats(season_end_year=2024)

# Write directly to CSV
client.league_per_game_stats(
    season_end_year=2024,
    output_type=OutputType.CSV,
    output_file_path="stats.csv",
)

# Or get a pandas DataFrame
frame = client.league_per_game_stats(season_end_year=2024, output_type=OutputType.DATAFRAME)
```

The CLI mirrors the JSON / CSV options with `--output-type {json,csv}` and `--output-file` (DataFrame output is Python-only):

```bash
courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 \
    --output-type csv --output-file roster.csv
```

For one-off debugging, add `--debug` to emit a JSON envelope (`{"data": ..., "debug": ...}`) for a single call.

## Endpoints

The authoritative list of served endpoints is the `ENDPOINTS` registry in the [`courtside_data/endpoints/`](courtside_data/endpoints/) package (assembled in [`_registry.py`](courtside_data/endpoints/_registry.py)). List them at runtime:

```bash
courtside-data list
```

No static list is maintained here — the code is the source of truth. An endpoint name appearing anywhere in this repo outside of that registry does not mean it is fully implemented and tested. For the rendered field tables, `EndpointSpec` reference, and per-endpoint metadata, see the [Endpoints API reference](docs/api/endpoints.md).

## Documentation

Rendered docs are published at **<https://nickth3man.github.io/courtside-data>**. Source lives under [`docs/`](docs/) — link, don't duplicate:

- [Endpoint Runtime](docs/architecture/endpoints.md) — how `EndpointSpec`, `EndpointMetadata`, `WorkflowSpec`, and the generic-table path drive every call.
- [Schemas](docs/api/schemas.md) — the typed `BRRow` Pydantic models returned by each endpoint (auto-generated from source via mkdocstrings).
- [Endpoints](docs/api/endpoints.md) — the `ENDPOINTS` registry and `EndpointSpec` reference (auto-generated from source).

Schema and endpoint field tables on those pages are generated from source — do not hand-edit them; update the docstrings and rebuild with `mkdocs build`.

### HTML fixture corpus

The [`raw/`](raw/) directory stores downloaded Basketball-Reference HTML pages. These fixtures regression-test typed endpoints without live network calls and preserve edge cases across old seasons, renamed teams, playoff tables, and unusual page layouts. They are **development fixtures**, not part of the public API.

## Rate Limiting

Basketball Reference bans clients that exceed ~20 requests per minute, so rate limiting is built in and **not configurable**:

- Requests are paced at a 6-second minimum interval (plus jitter, ~9 req/min), enforced process-wide across all sessions and threads.
- `Retry-After` headers are honored on retries.
- If Basketball Reference jails the session (a `Retry-After` longer than 5 minutes), a circuit breaker makes further calls fail fast with `RateLimitJailed`   instead of burning requests against the ban. The jail state is persisted to
  the platform-specific cache dir (e.g. `~/.cache/courtside-data/jail.json` on
  Linux, `~/Library/Caches/courtside-data/jail.json` on macOS) so restarted
  processes honor it too.

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

## Contributing

Contributions are welcome. The tooling, task runner, and quality gates are documented in [`AGENTS.md`](AGENTS.md) — start there. Before opening a pull request, run the full gate locally:

```bash
uv run task audit   # ruff check + ruff format --check + ty check + pytest tests -n auto
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
