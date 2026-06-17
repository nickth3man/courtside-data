# Agent guide — courtside-data

Instructions for AI coding agents working in this repository.

## Before you start

1. Read `codemap.md` for architecture, entry points, and data flow.
2. For folder-specific work, read that folder’s `codemap.md` if present.
3. Use `uv` and the `dev` dependency group for linting, type checking, and tests.

```bash
uv sync
```

Python **3.12+**. Source lives in `courtside_data/`. Tests live in `tests/` (offline fixture-replay suite; parallel-safe with `-n auto`).

**Dev dependencies now live in `[dependency-groups]` (PEP 735).** After this change, `uv sync` installs them automatically and `uv run <tool>` works without `--extra dev`.

---

## Ruff (lint + format)

[Ruff](https://docs.astral.sh/ruff/) is the single linter and formatter. Config: `[tool.ruff]` and `[tool.ruff.lint]` in `pyproject.toml`.

**This project enables:** `E`, `W`, `F`, `I`, `UP`, `B`, `PT`, `ASYNC`, plus safe refactoring rules `C4`, `SIM`, `PIE`, `RSE`, `RET`, `ISC`, `FLY`, `FURB`, `RUF`, `ERA` · line length **120** · target **py312**.

**Per-file ignores:** `tests/**` → `E501`, `W291`, `S101`, `B011`; `scripts/**` → `E501`.

### Commands (run from repo root)

```bash
# Lint — matches CI
uv run ruff check .

# Lint with safe auto-fixes
uv run ruff check . --fix

# Lint with all fixes (including unsafe — review the diff)
uv run ruff check . --fix --unsafe-fixes

# Format — apply
uv run ruff format .

# Format — CI check only (no writes)
uv run ruff format --check .

# Lint a path
uv run ruff check courtside_data tests

# Inspect / debug
uv run ruff check . --diff
uv run ruff check . --show-fixes
uv run ruff check . --statistics
uv run ruff rule F401          # explain one rule
uv run ruff check --watch .    # watch mode
```

### GitHub Actions output

```bash
uv run ruff check . --output-format github
```

### Suppression (use sparingly)

```python
x = 1  # noqa: F841
# ruff: noqa: F401   # file-level
```

Prefer fixing the issue or a `[tool.ruff.lint.per-file-ignores]` entry over blanket `# noqa`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Clean, or all violations fixed |
| 1 | Violations remain |
| 2 | Config / internal error |

---

## ty (type checker)

[ty](https://docs.astral.sh/ty/) is the type checker (Astral; beta). Config: `[tool.ty.environment]` and `[tool.ty.src]` in `pyproject.toml`.

**This project:** Python 3.12 · `extra-paths = ["courtside_data"]` · excludes `.venv`, `dist`, `.slim`.

### Commands (run from repo root)

```bash
# Typecheck — matches CI
uv run ty check

# Typecheck specific paths
uv run ty check courtside_data
uv run ty check tests

# Output formats
uv run ty check --output-format full      # default; verbose with hints
uv run ty check --output-format concise   # one line per diagnostic
uv run ty check --output-format github    # GitHub Actions annotations
uv run ty check --output-format gitlab    # GitLab Code Quality JSON
uv run ty check --output-format junit     # JUnit XML

# Auto-fix / suppress (review diffs carefully)
uv run ty check --fix
uv run ty check --add-ignore

# Rule severity overrides (CLI overrides pyproject.toml)
uv run ty check --error possibly-unresolved-reference
uv run ty check --warn division-by-zero
uv run ty check --ignore redundant-cast

# Watch mode
uv run ty check --watch

# Exit behavior
uv run ty check --error-on-warning   # exit 1 on warnings too
uv run ty check --exit-zero          # always exit 0

# Other subcommands
uv run ty version
uv run ty explain <RULE>
uv run ty server                     # language server (editors)
uv run ty --help
uv run ty check --help
```

### Suppression

```python
x: int = "hello"  # type: ignore[incompatible-assignment]
y = risky()       # type: ignore[possibly-unresolved-reference, invalid-argument-type]
```

### Common rules (defaults)

| Rule | Default | Description |
|------|---------|-------------|
| `possibly-unresolved-reference` | error | Name may be undefined |
| `invalid-argument-type` | error | Argument type mismatch |
| `incompatible-assignment` | error | Assigned value incompatible |
| `missing-argument` | error | Required argument missing |
| `unsupported-operator` | error | Operator not supported for types |
| `invalid-return-type` | error | Return type mismatch |
| `division-by-zero` | warn | Possible division by zero |
| `unused-ignore-comment` | warn | Unneeded `# type: ignore` |
| `redundant-cast` | warn | Cast has no effect |
| `possibly-unbound-attribute` | warn | Attribute may not exist |

Override severity in `pyproject.toml` under `[tool.ty.rules]` or per-path via `[[tool.ty.overrides]]`.

---

## Tests

Offline fixture-replay suite in `tests/` (~300 cases). Network access is blocked by `tests/conftest.py`. The suite is **parallel-safe** via [pytest-xdist](https://pytest-xdist.readthedocs.io/).

**Preferred local command** — use workers (roughly 2× faster than serial):

```bash
uv run pytest tests -n auto
```

Pin worker count when debugging flakes: `-n 4`. Run serial only when isolating a xdist-specific issue:

```bash
uv run pytest tests
```

`-n auto` is **not** in `[tool.pytest.ini_options] addopts` because CI collects coverage with `coverage run -m pytest`, which does not merge metrics from xdist worker subprocesses. CI therefore runs serial; local dev should prefer `-n auto`.

Coverage locally (serial — matches CI):

```bash
uv run coverage run --source=courtside_data --module pytest tests
uv run coverage report
```

Optional determinism check after changes to shared state (`HTTPService` class vars, fixtures):

```bash
uv run --extra dev pytest tests -n auto --randomly-seed=last
```

---

## Live endpoint probe (debug)

Opt-in debug tracing lives in `courtside_data/debug/`. See that folder’s `codemap.md` for trace schema, sinks, and runner integration.

**Requires live network access** to Basketball Reference. Respects built-in rate limiting (~8–9 req/min); a full probe of all ~55 endpoints takes several minutes.

### Probe all or selected endpoints

`courtside_data/debug/probe.py` calls each endpoint once with `debug=True`, using **one sample param set per endpoint** from `tests/fixture_manifest.py` (`ALL_CASES`). Paramless endpoints fall back to `{}`.

```bash
# All registry endpoints → summary report + one debug trace JSON per successful call
uv run python -m courtside_data.debug

# Single endpoint
uv run python -m courtside_data.debug.probe -e play_by_play

# Several endpoints
uv run python -m courtside_data.debug.probe -e team_roster -e friv_7_game_playoff_series_outcomes_team_is_tied

# Custom summary report path
uv run python -m courtside_data.debug.probe -o logs/my_probe.json
```

Repeat `-e` / `--endpoint` to filter; omit it to probe everything. Unknown endpoint names exit **2**.

### Output

| Artifact | Location |
|----------|----------|
| Summary report (ok/failed counts, per-endpoint stats) | `./logs/endpoint_probe_report_<timestamp>.json` (or `-o` path) |
| Per-call trace envelope (`{"data": ..., "debug": ...}`) | `./logs/<timestamp>_<endpoint>_<trace_id8>.json` |

Override the log directory with `COURTSIDE_DEBUG_LOG_DIR`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All probed endpoints succeeded |
| 1 | One or more failures (or missing sample params in the selection) |
| 2 | Invalid `--endpoint` name |

### Single manual call (CLI)

For one-off debugging with explicit params, use the CLI with `--debug` (JSON output only):

```bash
uv run courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 --debug
```

---

## Pre-commit checklist

Run these before claiming a task is done:

```bash
uv run --extra dev ruff check .
uv run --extra dev ruff format --check .
uv run --extra dev ty check
uv run --extra dev pytest tests -n auto
```

---

## References

- Ruff: https://docs.astral.sh/ruff/
- Ruff rules: https://docs.astral.sh/ruff/rules/
- ty: https://docs.astral.sh/ty/
- ty playground: https://play.astral.sh/ty

## Repository Map

A full codemap is available at `codemap.md` in the project root.

Before working on any task, read `codemap.md` to understand:
- Project architecture and entry points
- Directory responsibilities and design patterns
- Data flow and integration points between modules

For deep work on a specific folder, also read that folder's `codemap.md`.
