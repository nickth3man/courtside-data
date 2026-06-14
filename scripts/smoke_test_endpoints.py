#!/usr/bin/env python3
"""Smoke-test every public endpoint of the courtside-data library against the
LIVE basketball-reference.com site, capturing full results to JSON + Markdown.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import httpx  # noqa: E402  — sys.path must be bootstrapped first

import courtside_data  # noqa: E402,F401  — endpoint functions (importable)
from courtside_data import client  # noqa: E402
from courtside_data import errors as cderrors  # noqa: E402
from courtside_data.data import TEAM_ABBREVIATIONS_TO_TEAM, Team  # noqa: E402
from courtside_data.endpoints import ENDPOINTS  # noqa: E402

# ═══════════════════════════════════════════════════════════════════════════════
# Verified query pools — DO NOT CHANGE
# ═══════════════════════════════════════════════════════════════════════════════
SEASONS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
TEAMS = [
    "ATL",
    "BOS",
    "BRK",
    "CHI",
    "CHO",
    "CLE",
    "DAL",
    "DEN",
    "DET",
    "GSW",
    "HOU",
    "IND",
    "LAC",
    "LAL",
    "MEM",
    "MIA",
    "MIL",
    "MIN",
    "NOP",
    "NYK",
    "OKC",
    "ORL",
    "PHI",
    "PHO",
    "POR",
    "SAC",
    "SAS",
    "TOR",
    "UTA",
    "WAS",
]
PLAYERS = [
    "jordami01",
    "curryst01",
    "duranke01",
    "antetgi01",
    "embiijo01",
    "doncilu01",
    "tatumja01",
    "willizi01",
    "hardeja01",
    "westbru01",
    "leonaka01",
    "lillada01",
]
SEARCH_TERMS = ["Jordan", "Curry", "LeBron", "Wilt"]

# Date defaults — Christmas 2024 (deterministic date shared by any endpoint
# that takes day/month/year params; ``play_by_play`` is overridden from the
# corpus via ``_resolve_play_by_play_params``).
DEFAULT_DAY = 25
DEFAULT_MONTH = 12
DEFAULT_YEAR = 2024

RAW_ROOT = REPO_ROOT / "raw"
_CORPUS_PARAM_CACHE: dict[str, list[dict[str, Any]]] = {}

# ═══════════════════════════════════════════════════════════════════════════════
# Hardcoded overrides for endpoints that need a curated query (override the
# random builder). ``play_by_play`` is resolved at runtime from the corpus —
# see ``_resolve_play_by_play_params`` below — because its ``home_team`` and
# date pairing must be one that the live BBR index actually exposes.
# ═══════════════════════════════════════════════════════════════════════════════
HARDCODED_PARAMS: dict[str, dict[str, Any]] = {
    "playoff_player_box_scores": {
        "player_identifier": "tatumja01",
        "season_end_year": 2024,
        "include_inactive_games": False,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _serialize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *params* with Team enums stringified to ``.name``."""
    out: dict[str, Any] = {}
    for k, v in params.items():
        if isinstance(v, Team):
            out[k] = v.name
        else:
            out[k] = v
    return out


def _clean_path_template(path: str) -> str:
    return path.strip().split(",", 1)[0].split(None, 1)[0].split("#", 1)[0]


def _field_regex(param_name: str) -> str:
    if param_name == "game_date":
        return r"\d{8,9}"
    if param_name in {"day", "month"}:
        return r"\d{1,2}"
    if param_name in {"year", "season_end_year"}:
        return r"\d{4}"
    if param_name in {"game_code", "away", "team_abbreviation", "team_a", "team_b"}:
        return r"[A-Za-z0-9]+"
    if param_name in {"player_identifier", "slug", "round", "stat", "view"}:
        return r"[A-Za-z0-9_-]+"
    return r"[^/&]+"


def _path_template_regex(path_template: str) -> tuple[re.Pattern[str], dict[str, str]]:
    template = _clean_path_template(path_template)
    parts: list[str] = []
    group_params: dict[str, str] = {}
    group_counts: dict[str, int] = {}
    cursor = 0
    for match in re.finditer(r"\{([^{}]+)\}", template):
        parts.append(re.escape(template[cursor : match.start()]))
        raw_param_name = match.group(1)
        param_name = re.sub(r"\[[^\]]*\]", "", raw_param_name)
        group_counts[param_name] = group_counts.get(param_name, 0) + 1
        group_name = f"{param_name}__{group_counts[param_name]}"
        if "[" not in raw_param_name:
            group_params[group_name] = param_name
        parts.append(f"(?P<{group_name}>{_field_regex(param_name)})")
        cursor = match.end()
    parts.append(re.escape(template[cursor:]))
    return re.compile("^" + "".join(parts) + "$"), group_params


_FAMILIES_CACHE: list[str] | None = None


def _endpoint_family(name: str) -> str | None:
    global _FAMILIES_CACHE
    if not RAW_ROOT.is_dir():
        return None
    if _FAMILIES_CACHE is None:
        _FAMILIES_CACHE = sorted(
            (path.name for path in RAW_ROOT.iterdir() if path.is_dir()),
            key=len,
            reverse=True,
        )
    for family in _FAMILIES_CACHE:
        if name == family or name.startswith(f"{family}_"):
            return family
    return None


def _corpus_param_sets(name: str, endpoint: Any) -> list[dict[str, Any]]:
    family = _endpoint_family(name)
    if not family:
        return []
    cache_key = f"{family}:{endpoint.path}"
    if cache_key in _CORPUS_PARAM_CACHE:
        return _CORPUS_PARAM_CACHE[cache_key]

    family_dir = RAW_ROOT / family
    path_re, group_params = _path_template_regex(endpoint.path)
    candidates: list[dict[str, Any]] = []
    for sidecar in sorted(family_dir.rglob("*.html.meta.json")):
        try:
            meta = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("status_code", 200) != 200:
            continue
        parsed = urlparse(str(meta.get("final_url") or meta.get("url") or ""))
        url_to_match = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        match = path_re.fullmatch(url_to_match)
        if not match:
            continue
        groups = match.groupdict()
        params = {
            param_name: groups[group_name]
            for group_name, param_name in group_params.items()
            if param_name in endpoint.params
        }
        if params:
            candidates.append(params)

    _CORPUS_PARAM_CACHE[cache_key] = candidates
    return candidates


def build_params(name: str, endpoint: Any) -> dict[str, Any]:
    """Build a random-but-valid param dict for *endpoint*.

    Rules (per param name):
    - season_end_year      → random.choice(SEASONS)
    - team_abbreviation    → random.choice(TEAMS)
    - player_identifier    → random.choice(PLAYERS)
    - term                 → random.choice(SEARCH_TERMS)
    - day / month / year   → Christmas 2024 defaults (not randomized)
    - include_inactive_games → False (bool)
    - include_combined_values → False (bool)
    """
    params: dict[str, Any] = {}
    corpus_params = _corpus_param_sets(name, endpoint)
    if corpus_params:
        params.update(corpus_params[0])

    for param_name in endpoint.params:
        if param_name in params:
            continue
        if param_name == "season_end_year":
            params[param_name] = random.choice(SEASONS)
        elif param_name == "team_abbreviation":
            params[param_name] = random.choice(TEAMS)
        elif param_name == "player_identifier":
            params[param_name] = random.choice(PLAYERS)
        elif param_name == "term":
            params[param_name] = random.choice(SEARCH_TERMS)
        elif param_name == "day":
            params[param_name] = DEFAULT_DAY
        elif param_name == "month":
            params[param_name] = DEFAULT_MONTH
        elif param_name == "year":
            params[param_name] = DEFAULT_YEAR
        elif param_name in ("include_inactive_games", "include_combined_values"):
            params[param_name] = False
    return params


# Regex matching the corpus directory naming convention used by
# ``scripts/raw_download.py`` for ``play_by_play`` fixtures:
# ``<TEAM_ABBR>_<YYYY>_<MM>_<DD>``. Parsing the directory name directly is the
# authoritative source of (home_team, date) pairings known to round-trip
# through the live BBR box-score index.
_PBP_DIR_RE = re.compile(r"^([A-Z]+)_(\d{4})_(\d{2})_(\d{2})$")

# Filename of the per-game PBP page written by ``raw_download.py`` for a
# ``play_by_play`` fixture, of the form ``<YYYYMMDD>0<TEAM_ABBR>.html`` (the
# ``0`` is BBR's home-team slot marker in the daily index URL). Requiring the
# existence of this file ensures the (home_team, date) pairing is one for
# which a PBP HTML body was actually downloaded — directory-level metadata
# (e.g. a daily index page) alone is not enough.
_PBP_FILE_RE = re.compile(r"^(\d{8})0([A-Z]+)\.html$")


def _resolve_play_by_play_params(seed: int) -> dict[str, Any]:
    """Pick a known-valid ``play_by_play`` (home_team, date) from the corpus.

    Walks ``raw/play_by_play/`` (committed, version-pinned corpus mirrors of
    real BBR pbp pages), parses each subdirectory name of the form
    ``<TEAM_ABBR>_<YYYY>_<MM>_<DD>``, requires that the directory also contain
    a sibling per-game PBP HTML file (``<YYYYMMDD>0<TEAM_ABBR>.html``), and
    yields a ``{home_team, day, month, year}`` dict for each such fixture.
    The list is sorted for reproducibility, then one entry is selected
    deterministically via a separate :class:`random.Random` seeded with
    *seed*. Using a dedicated RNG keeps the pick reproducible regardless of
    how many other endpoints the harness has iterated by the time
    ``play_by_play`` is reached.

    A hardcoded fallback (``MIL + 2018-10-27``) is used when the corpus
    directory is absent or contains no qualifying fixtures, so the script
    still runs on a fresh clone with no downloaded fixtures.
    """
    corpus_root = Path(__file__).resolve().parent.parent / "raw" / "play_by_play"
    candidates: list[dict[str, Any]] = []
    if corpus_root.is_dir():
        for sub in sorted(corpus_root.iterdir()):
            if not sub.is_dir():
                continue
            match = _PBP_DIR_RE.match(sub.name)
            if match is None:
                continue
            abbr, year, month, day = (
                match.group(1),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
            )
            team = TEAM_ABBREVIATIONS_TO_TEAM.get(abbr)
            if team is None:
                # Unknown / historical abbreviation — skip rather than guess.
                continue
            # Require the per-game PBP HTML file (not just a daily index).
            pbp_filename = f"{year:04d}{month:02d}{day:02d}0{abbr}.html"
            if not (sub / pbp_filename).is_file():
                continue
            candidates.append(
                {
                    "home_team": team,
                    "day": day,
                    "month": month,
                    "year": year,
                }
            )

    if not candidates:
        # Fallback pairing: MIL hosted on 2018-10-27 (a real BBR-indexed game).
        candidates.append(
            {
                "home_team": Team.MILWAUKEE_BUCKS,
                "day": 27,
                "month": 10,
                "year": 2018,
            }
        )

    rng = random.Random(seed)
    return rng.choice(candidates)


def build_url(endpoint: Any, params: dict[str, Any]) -> str:
    """Compute the request URL for reporting.

    Format the endpoint path template with params; on failure (e.g. custom
    endpoints with multi-part paths, or ``standings_by_date`` whose path
    contains ``{conference}`` that is *not* in params) fall back to the raw
    template string.  Prefix with ``https://www.basketball-reference.com``.
    """
    path = _clean_path_template(endpoint.path)
    try:
        formatted = path.format(**params)
    except (KeyError, IndexError, ValueError, TypeError):
        formatted = path
    return f"https://www.basketball-reference.com{formatted}"


def _first_list_value(result: dict[str, Any]) -> list[Any] | None:
    """Return the first list-valued entry in *result*, or None."""
    for v in result.values():
        if isinstance(v, list):
            return v
    return None


def _truncate_json(obj: Any, max_len: int = 500) -> str:
    """JSON-serialize *obj* (using default=str for non-serializable types)
    and truncate to *max_len* characters.
    """
    s = json.dumps(obj, default=str, ensure_ascii=False)
    if len(s) > max_len:
        s = s[:max_len]
    return s


def capture_result(
    name: str,
    endpoint: Any,
    params: dict[str, Any],
    url: str,
    duration_s: float,
    result: Any,
) -> dict[str, Any]:
    """Build a success result record."""
    entry: dict[str, Any] = {
        "name": name,
        "status": "ok",
        "duration_s": duration_s,
        "params": _serialize_params(params),
        "url": url,
    }

    # result_type
    entry["result_type"] = type(result).__name__

    # row_count
    if isinstance(result, list):
        entry["row_count"] = len(result)
    elif isinstance(result, dict):
        entry["row_count"] = sum(len(v) for v in result.values() if isinstance(v, list))
    else:
        entry["row_count"] = 0

    # keys_or_columns
    if isinstance(result, list) and result and isinstance(result[0], dict):
        entry["keys_or_columns"] = list(result[0].keys())
    elif isinstance(result, dict):
        entry["keys_or_columns"] = list(result.keys())
    else:
        entry["keys_or_columns"] = []

    # sample
    sample_rows: list[dict[str, Any]] = []
    if isinstance(result, list):
        sample_rows = result[:2]
    elif isinstance(result, dict):
        first_list = _first_list_value(result)
        if first_list is not None:
            sample_rows = first_list[:2]
    entry["sample"] = _truncate_json(sample_rows) if sample_rows else "[]"

    return entry


def capture_error(
    name: str,
    endpoint: Any,
    params: dict[str, Any],
    url: str,
    duration_s: float,
    exc: Exception,
) -> dict[str, Any]:
    """Build an error result record."""
    entry: dict[str, Any] = {
        "name": name,
        "status": "error",
        "duration_s": duration_s,
        "params": _serialize_params(params),
        "url": url,
        "error_type": type(exc).__module__ + "." + type(exc).__qualname__,
        "error_message": str(exc),
    }

    # Classify
    if isinstance(exc, cderrors.RateLimitJailed):
        entry["error_category"] = "rate_limit_jailed"
    elif isinstance(exc, cderrors.SchemaDriftError):
        entry["error_category"] = "schema_drift"
        pydantic_errors = getattr(exc, "pydantic_errors", [])
        entry["pydantic_errors"] = len(pydantic_errors)
    elif isinstance(exc, cderrors.CourtsideDataError):
        entry["error_category"] = "domain"
    elif isinstance(exc, httpx.HTTPStatusError):
        entry["error_category"] = "http_status"
        entry["http_status_code"] = exc.response.status_code
    elif isinstance(exc, (httpx.TransportError, httpx.HTTPError)):
        entry["error_category"] = "transport"
    else:
        entry["error_category"] = "other"

    entry["traceback"] = traceback.format_exc()
    return entry


def md_escape(text: str) -> str:
    """Minimal Markdown escaping for pipe-table cells."""
    return text.replace("|", "\\|").replace("\n", " ")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke-test every courtside-data endpoint against live BBR."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260614,
        help="RNG seed for reproducible random-query selection (default: 20260614)",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Only run endpoints whose signature includes this parameter. Repeatable.",
    )
    args = parser.parse_args()

    seed: int = args.seed
    random.seed(seed)

    started_at = datetime.now(UTC)
    endpoint_items = list(ENDPOINTS.items())  # insertion-order snapshot
    if args.param:
        selected_params = set(args.param)
        endpoint_items = [
            (name, endpoint)
            for name, endpoint in endpoint_items
            if selected_params.intersection(endpoint.params)
        ]
    total = len(endpoint_items)

    results: list[dict[str, Any]] = []
    jailed = False
    t0 = time.perf_counter()

    # Resolve the play_by_play (home_team, date) pairing once per run, from
    # the corpus. Done before the loop so the result is recorded in the
    # report even if play_by_play trips the rate-limit jail later.
    play_by_play_params = _resolve_play_by_play_params(seed)

    for i, (name, endpoint) in enumerate(endpoint_items, 1):
        # ── Already jailed → skip ──
        if jailed:
            results.append(
                {
                    "name": name,
                    "status": "skipped",
                    "reason": "rate_limit_jailed_earlier",
                }
            )
            print(
                f"[{i:2d}/{total}] {name} ... SKIPPED  (rate_limit_jailed_earlier)",
                flush=True,
            )
            continue

        # ── Apply hardcoded overrides ──
        if name == "play_by_play":
            params = dict(play_by_play_params)
        elif name in HARDCODED_PARAMS:
            params = dict(HARDCODED_PARAMS[name])
        else:
            params = build_params(name, endpoint)

        url = build_url(endpoint, params)

        # ── Call the endpoint ──
        try:
            func = getattr(client, name)
        except AttributeError:
            # Shouldn't happen if registry ↔ client exports stay in sync
            results.append(
                {
                    "name": name,
                    "status": "error",
                    "duration_s": 0.0,
                    "params": _serialize_params(params),
                    "url": url,
                    "error_type": "AttributeError",
                    "error_message": f"Function '{name}' not found on client module",
                    "error_category": "other",
                    "traceback": "",
                }
            )
            print(
                f"[{i:2d}/{total}] {name} ... ERROR other  (func not found, 0.0s)",
                flush=True,
            )
            continue

        t_call = time.perf_counter()
        try:
            result = func(**params)
            duration_s = time.perf_counter() - t_call
            entry = capture_result(name, endpoint, params, url, duration_s, result)
            results.append(entry)
            rows_str = str(entry.get("row_count", "?"))
            print(
                f"[{i:2d}/{total}] {name} ... OK  (rows={rows_str}, {duration_s:.1f}s)",
                flush=True,
            )
        except Exception as exc:
            duration_s = time.perf_counter() - t_call
            entry = capture_error(name, endpoint, params, url, duration_s, exc)
            results.append(entry)

            cat = entry.get("error_category", "?")
            err_type = entry.get("error_type", "?").split(".")[-1]
            print(
                f"[{i:2d}/{total}] {name} ... ERROR {cat} {err_type}  ({duration_s:.1f}s)",
                flush=True,
            )

            # ── RateLimitJailed is a circuit breaker ──
            if isinstance(exc, cderrors.RateLimitJailed):
                jailed = True

    elapsed = time.perf_counter() - t0

    # ── Summary ──
    ok_count = sum(1 for r in results if r["status"] == "ok")
    error_count = sum(1 for r in results if r["status"] == "error")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    by_category: dict[str, int] = {}
    for r in results:
        cat = r.get("error_category")
        if cat:
            by_category[cat] = by_category.get(cat, 0) + 1

    meta = {
        "started_at_utc": started_at.isoformat(),
        "seed": seed,
        "selected_params": args.param,
        "total_endpoints": total,
        "elapsed_s": round(elapsed, 2),
        "play_by_play_params": _serialize_params(play_by_play_params),
        "summary": {
            "ok": ok_count,
            "error": error_count,
            "skipped": skipped_count,
            "by_category": by_category,
        },
    }

    output_json = {
        "meta": meta,
        "results": results,
    }

    # ── Write JSON ──
    with open("endpoint_smoke_results.json", "w", encoding="utf-8") as fh:
        json.dump(output_json, fh, ensure_ascii=False, indent=2, default=str)

    # ── Build Markdown ──
    md_lines: list[str] = []
    md_lines.append("# Endpoint Smoke Test Results")
    md_lines.append("")
    md_lines.append(f"- **Started**: {meta['started_at_utc']}")
    md_lines.append(f"- **Seed**: {meta['seed']}")
    if args.param:
        md_lines.append(f"- **Selected params**: {', '.join(args.param)}")
    md_lines.append(f"- **Elapsed**: {meta['elapsed_s']:.1f}s")
    md_lines.append(f"- **Total endpoints**: {meta['total_endpoints']}")
    md_lines.append(f"- **OK**: {meta['summary']['ok']}")
    md_lines.append(f"- **Error**: {meta['summary']['error']}")
    md_lines.append(f"- **Skipped**: {meta['summary']['skipped']}")
    if by_category:
        md_lines.append(f"- **By category**: {json.dumps(by_category)}")
    md_lines.append(
        f"- **play_by_play pairing**: `{json.dumps(meta['play_by_play_params'])}` "
        f"(resolved from corpus, seed-deterministic)"
    )
    md_lines.append("")

    # Summary table
    md_lines.append("| Endpoint | Status | Rows | Time | Category | Note |")
    md_lines.append("|----------|--------|------|------|----------|------|")
    for r in results:
        ep_name = md_escape(r.get("name", "?"))
        status = r["status"]
        if status == "ok":
            rows_disp = str(r.get("row_count", "?"))
            time_disp = f"{r.get('duration_s', 0):.1f}s"
            cat_disp = "-"
            note = f"rows={rows_disp}"
        elif status == "skipped":
            rows_disp = "-"
            time_disp = "-"
            cat_disp = r.get("reason", "")
            note = ""
        else:  # error
            rows_disp = "-"
            time_disp = f"{r.get('duration_s', 0):.1f}s"
            cat_disp = r.get("error_category", "")
            msg = r.get("error_message", "")
            note = (msg[:80] + "…") if len(msg) > 80 else msg
        md_lines.append(
            f"| {ep_name} | {status} | {rows_disp} | {time_disp} | {cat_disp} | {md_escape(note)} |"
        )
    md_lines.append("")

    # Per-endpoint detail
    md_lines.append("## Per-endpoint detail")
    md_lines.append("")
    for r in results:
        name = r.get("name", "?")
        md_lines.append(f"### {name}")
        md_lines.append("")
        md_lines.append(
            f"- **Params**: `{json.dumps(r.get('params', {}), default=str)}`"
        )
        md_lines.append(f"- **URL**: `{r.get('url', '')}`")
        md_lines.append(f"- **Status**: {r['status']}")

        if r["status"] == "ok":
            md_lines.append(f"- **Duration**: {r.get('duration_s', 0):.3f}s")
            md_lines.append(f"- **Row count**: {r.get('row_count', 0)}")
            md_lines.append(
                f"- **Columns**: `{json.dumps(r.get('keys_or_columns', []))}`"
            )
            md_lines.append("")
            md_lines.append("**Sample**:")
            md_lines.append("```json")
            md_lines.append(r.get("sample", "[]"))
            md_lines.append("```")
        elif r["status"] == "error":
            md_lines.append(f"- **Duration**: {r.get('duration_s', 0):.3f}s")
            md_lines.append(f"- **Error type**: `{r.get('error_type', '')}`")
            md_lines.append(f"- **Error category**: `{r.get('error_category', '')}`")
            if "http_status_code" in r:
                md_lines.append(f"- **HTTP status**: {r['http_status_code']}")
            if "pydantic_errors" in r:
                md_lines.append(f"- **Pydantic errors**: {r['pydantic_errors']}")
            md_lines.append(f"- **Message**: {r.get('error_message', '')}")
            if r.get("traceback"):
                md_lines.append("")
                md_lines.append("```")
                md_lines.append(r["traceback"].rstrip())
                md_lines.append("```")
        else:  # skipped
            md_lines.append(f"- **Reason**: {r.get('reason', '')}")

        md_lines.append("")

    # ── Write Markdown ──
    with open("endpoint_smoke_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    # ── Final summary ──
    print(
        f"DONE: ok={ok_count} error={error_count} skipped={skipped_count}  "
        f"(elapsed {elapsed:.1f}s)  -> endpoint_smoke_results.json/.md"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
