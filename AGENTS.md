# Agent guide — courtside-data

Instructions for AI coding agents working in this repository.

## Before you start

1. Read `codemap.md` for architecture, entry points, and data flow.
2. For folder-specific work, read that folder’s `codemap.md` if present.
3. Use the PEP 735 dev group via `uv sync --group dev` and run checks with `uv run <tool>`; do not use `--extra dev`.

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
# If dev dependencies are not installed, run `uv sync --group dev` first.
uv run pytest tests -n auto --randomly-seed=last
```

---

## taskipy (task runner)

[taskipy](https://github.com/taskipy/taskipy) reads task definitions from `[tool.taskipy.tasks]` in `pyproject.toml` and exposes them as `uv run task <name>`. The project defines 11 tasks that wrap the underlying tools documented below.

### Commands

```bash
# List all tasks and the command each expands to
uv run task --list

# Day-to-day
uv run task lint        # ruff check .
uv run task format      # ruff format --check .
uv run task fix         # ruff check --fix . && ruff format .
uv run task type        # ty check
uv run task test        # pytest tests -n auto
uv run task audit       # lint + format --check + type + test  (the full gate)

# Refactor / ad-hoc audits
uv run task refactor    # ruff fix + format + flynt
uv run task vulture     # vulture courtside_data --min-confidence 80
uv run task deptry      # deptry .
uv run task bandit      # bandit -r courtside_data -lll
uv run task test-cov    # coverage run --source=courtside_data --module pytest tests

# Pass extra args through to the underlying command
uv run task test -k test_foo     # → pytest tests -n auto -k test_foo
```

CI does **not** call taskipy — workflows invoke the underlying tools directly. taskipy is a local-dev convenience only.

**Exit code:** taskipy propagates the exit code of the underlying command (or the first failing command in a `&&` chain).

> Docs: https://github.com/taskipy/taskipy

---

## flynt (f-string conversion)

[flynt](https://github.com/ikamensh/flynt) auto-converts `%`-formatted and `.format(...)` strings (plus concatenations and static joins) to f-strings in place. Used by the `refactor` task.

### Commands

```bash
# Convert in place (the `refactor` task's flynt step)
uv run flynt -tc -tj courtside_data/ tests/ scripts/   # -tc: concats, -tj: joins

# Single file vs directory
uv run flynt courtside_data/cli.py
uv run flynt courtside_data/

# Dry-run / verbose / CI fail mode
uv run flynt -d courtside_data/          # diff, no writes
uv run flynt -v courtside_data/          # DEBUG logs
uv run flynt -d -f courtside_data/       # CI: exit 1 if anything would change
uv run flynt --report courtside_data/    # per-file conversion report
```

> **Flag-clustering gotcha:** `-tc` and `-tj` are multi-character short options — argparse does **not** auto-cluster them. `flynt -tjc` fails with `unrecognized arguments: -tjc`; always pass them separately as `-tc -tj`.

Config (since v0.71): `[tool.flynt]` in `pyproject.toml`, auto-discovered by walking up from the first `src` argument.

> Docs: https://github.com/ikamensh/flynt

---

## vulture (dead code)

[vulture](https://github.com/jendrikseipp/vulture) finds unused Python code via static AST analysis. Used by the `vulture` task.

### Commands

```bash
# The `vulture` task — confidence 80 is the sweet spot vs false positives
uv run vulture courtside_data --min-confidence 80

# Stricter: only 100%-confident dead code
uv run vulture courtside_data --min-confidence 100

# Triage big reports first
uv run vulture courtside_data --sort-by-size --min-confidence 60

# Auto-generate a whitelist module for known false positives
uv run vulture courtside_data --make-whitelist > vulture_whitelist.py
uv run vulture courtside_data vulture_whitelist.py
```

**Suppressing false positives** (in order of preference): (1) whitelist module passed as an extra path, (2) `--ignore-names "visit_*,do_*"` for patterns, (3) `# noqa: F401`/`F841` inline. Confidence levels: imports 90 · function args + unreachable code 100 · attributes/classes/functions/variables 60.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Clean |
| 1 | Invalid input (missing file, syntax error) |
| 2 | Bad CLI args |
| 3 | Dead code found (this is what blocks CI) |

Config: `[tool.vulture]` in `pyproject.toml` (`min_confidence`, `ignore_names`, `paths`, …).

> Docs: https://github.com/jendrikseipp/vulture

---

## deptry (dependency linting)

[deptry](https://deptry.com) statically checks declared dependencies against actual imports — catches missing, unused, transitive-only, and misplaced (dev) deps. Used by the `deptry` task.

### Commands

```bash
# The `deptry` task
uv run deptry .

# GitHub Actions annotations
uv run deptry . --github-output

# Ignore rules / per-rule module exclusions
uv run deptry . --ignore DEP001,DEP004
uv run deptry . --per-rule-ignores "DEP001=matplotlib,DEP002=pandas|numpy"

# Extend default excludes (additive; respects .gitignore)
uv run deptry . --extend-exclude ".*/legacy/*"
```

### Rules

| Rule | What it flags |
|------|---------------|
| `DEP001` | **Missing** — imported but not declared |
| `DEP002` | **Unused** — declared but not imported (skipped for dev deps) |
| `DEP003` | **Transitive** — in the dep tree but not declared directly |
| `DEP004` | **Misplaced** — declared in `[dependency-groups]` (dev) but imported from shipped code |
| `DEP005` | **Stdlib** — declared but ships with the standard library |

**PEP 735 support:** ✅ since v0.20. Every group under `[dependency-groups]` is treated as dev by default, so DEP002 is not raised for them and DEP004 fires on leaks into runtime code. Use `--non-dev-dependency-groups "server,telemetry"` to opt specific groups back into the runtime bucket.

Inline suppression: `# deptry: ignore[DEP001,DEP003]` on the import line (cannot silence DEP002/DEP005 — those point at `pyproject.toml`).

Config: `[tool.deptry]` in `pyproject.toml`.

> Docs: https://deptry.com/

---

## bandit (security linting)

[bandit](https://bandit.readthedocs.io) is an AST-based security linter — finds `assert` in production code, shell injection, weak crypto, hard-coded secrets, unsafe `yaml.load`, etc. Used by the `bandit` task.

### Commands

```bash
# The `bandit` task — HIGH severity only
uv run bandit -r courtside_data -lll

# Lower thresholds during triage
uv run bandit -r courtside_data -ll      # MEDIUM+
uv run bandit -r courtside_data          # everything

# Run / skip specific test IDs
uv run bandit -r courtside_data -t B602,B607
uv run bandit -r courtside_data -s B101  # skip assert plugin

# Output formats (NO native `github` formatter — use sarif or json)
uv run bandit -r courtside_data -lll -f sarif -o bandit.sarif   # → github/codeql-action/upload-sarif
uv run bandit -r courtside_data -lll -f json  -o bandit.json
uv run bandit -r courtside_data -lll -f html  -o bandit.html
```

**Severity ladder:** `-l` = LOW+, `-ll` = MEDIUM+, **`-lll` = HIGH+** (the project's choice). Confidence works the same way: `-i`/`-ii`/`-iii`.

> **No `-f github`:** bandit 1.9.x ships `csv, custom, html, json, sarif, screen, txt, xml, yaml`. For GitHub Actions, pair `-f sarif` with `github/codeql-action/upload-sarif@v3`, or `-f json` with an annotator action.

**B101 vs pytest:** `assert_used` fires on every `assert` in `tests/`. The project's `bandit` task only targets `courtside_data/`, avoiding tests entirely. Ruff's `S101` ignore for `tests/**` covers the equivalent lint concern.

**Suppression:** append `# nosec` (or `# nosec B101` to scope) to a line.

Config: `.bandit` INI (auto-discovered with `-r`), or `[tool.bandit]` in `pyproject.toml` (requires `-c pyproject.toml` and `bandit[toml]`).

> Docs: https://bandit.readthedocs.io/en/latest/

---

## diff-cover (PR coverage gate)

[diff-cover](https://github.com/Bachmann1234/diff_cover) gates coverage against the **diff** — how much of the changed code is covered? Enforces "if you touched it, you covered it" on PRs. Declared as a dev dep; **not yet wired into CI**.

### Commands

```bash
# Canonical 3-step flow (run after `task test-cov`)
uv run coverage run --source=courtside_data --module pytest tests   # 1. run tests
uv run coverage xml                                                 # 2. write coverage.xml
uv run diff-cover coverage.xml                                      # 3. compare vs origin/main

# Hard threshold + explicit base branch (the real PR gate)
uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=100

# Reports
uv run diff-cover coverage.xml --format html:diff-cover.html
uv run diff-cover coverage.xml --format markdown:diff-cover.md
uv run diff-cover coverage.xml --show-uncovered
```

| Flag | Effect |
|------|--------|
| `--compare-branch BRANCH` | Default `origin/main`. |
| `--fail-under PCT` | Non-zero exit when diff coverage < `PCT`. The PR-gate flag. |
| `--format FMT:file` | `html:…`, `markdown:…`, `json:…`. (Older `--html-report` etc. deprecated.) |
| `--show-uncovered` | List uncovered diff lines on console. |

> **Requires** a `git` working directory and reachable `origin/main`. In CI: `git fetch origin main:refs/remotes/origin/main` first.

`diff-quality` is the sister tool — runs a linter on the diff (e.g. `uv run diff-quality --violations=ruff.check`).

Config: `[tool.diff_cover]` in a TOML file passed via `-c`.

> Docs: https://github.com/Bachmann1234/diff_cover

---

## mkdocs (docs site)

[mkdocs](https://www.mkdocs.org/) + [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) build the project docs site published to GitHub Pages. Config: `mkdocs.yml` at repo root; content under `docs/`. CI publishes via `mkdocs gh-deploy --force` (see `.github/workflows/ci.yml`).

### Commands

```bash
# Local dev server with live reload on http://127.0.0.1:8000
uv run mkdocs serve

# CI build gate — warnings become errors (broken links, unknown config, …)
uv run mkdocs build --strict

# Publish to the gh-pages branch (this is what CI runs)
uv run mkdocs gh-deploy

# Inspect / scaffold
uv run mkdocs --version
uv run mkdocs get-deps          # list PyPI packages the config requires
```

> **`--strict` is the CI gate** (added in mkdocs 1.4): broken internal links, unknown config keys, and unknown markdown-extension settings all fail the build. Run it locally before pushing. (Note: current CI only runs `gh-deploy`; adding a `build --strict` step is recommended hardening.)

**pymdown-extensions** are provided by the `pymdown-extensions` package (a dep of mkdocs-material ≥ 9) and enabled by name under `markdown_extensions:` in `mkdocs.yml`.

> Docs: mkdocs — https://www.mkdocs.org/ · material — https://squidfunk.github.io/mkdocs-material/

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

If a selected endpoint has no fixture sample in `ALL_CASES`, report that endpoint as missing fixture data and stop with exit 1; do not continue as if the probe succeeded.

If the live probe cannot reach Basketball Reference, times out, or hits rate limiting, stop and report the exact failure for each endpoint; do not retry indefinitely or claim the probe completed.

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
# One command — runs lint + format check + type + test (the full gate)
uv run task audit

# Or individually
uv run task lint
uv run task format
uv run task type
uv run task test

# Raw tool invocations (equivalent; no taskipy)
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest tests -n auto
```

---

## References

- Ruff: https://docs.astral.sh/ruff/
- Ruff rules: https://docs.astral.sh/ruff/rules/
- ty: https://docs.astral.sh/ty/
- ty playground: https://play.astral.sh/ty
- taskipy: https://github.com/taskipy/taskipy
- flynt: https://github.com/ikamensh/flynt
- vulture: https://github.com/jendrikseipp/vulture
- deptry: https://deptry.com/
- bandit: https://bandit.readthedocs.io/en/latest/
- diff-cover: https://github.com/Bachmann1234/diff_cover
- mkdocs: https://www.mkdocs.org/
- mkdocs-material: https://squidfunk.github.io/mkdocs-material/

## Repository Map

A full codemap is available at `codemap.md` in the project root.

Before working on any task, read `codemap.md` to understand:
- Project architecture and entry points
- Directory responsibilities and design patterns
- Data flow and integration points between modules

For deep work on a specific folder, also read that folder's `codemap.md`.
