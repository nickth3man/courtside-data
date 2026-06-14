#!/usr/bin/env python3
"""Smoke-test every public endpoint of the courtside-data library against the
LIVE basketball-reference.com site, capturing full results to JSON + Markdown.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Any

import courtside_data  # noqa: F401  — the 50 endpoint functions (importable)
from courtside_data import client
from courtside_data.data import Team
from courtside_data.endpoints import ENDPOINTS
from courtside_data import errors as cderrors

import httpx

# ═══════════════════════════════════════════════════════════════════════════════
# Verified query pools — DO NOT CHANGE
# ═══════════════════════════════════════════════════════════════════════════════
SEASONS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
TEAMS = [
    "ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS",
]
PLAYERS = [
    "jordami01", "curryst01", "duranke01", "antetgi01", "embiijo01",
    "doncilu01", "tatumja01", "willizi01", "hardeja01", "westbru01",
    "leonaka01", "lillada01",
]
SEARCH_TERMS = ["Jordan", "Curry", "LeBron", "Wilt"]

# Date defaults — Christmas 2024 slate (Lakers host Warriors)
DEFAULT_DAY = 25
DEFAULT_MONTH = 12
DEFAULT_YEAR = 2024

# ═══════════════════════════════════════════════════════════════════════════════
# Hardcoded overrides for two endpoints (override the random builder)
# ═══════════════════════════════════════════════════════════════════════════════
HARDCODED_PARAMS: dict[str, dict[str, Any]] = {
    "play_by_play": {
        "home_team": Team.LOS_ANGELES_LAKERS,
        "day": 25,
        "month": 12,
        "year": 2024,
    },
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


def build_params(endpoint: Any) -> dict[str, Any]:
    """Build a random-but-valid param dict for *endpoint*.

    Rules (per param name):
    - season_end_year      → random.choice(SEASONS)
    - team_abbreviation    → random.choice(TEAMS)
    - player_identifier    → random.choice(PLAYERS)
    - term                 → random.choice(SEARCH_TERMS)
    - day / month / year   → Christmas 2024 defaults (not randomized)
    - home_team            → Team.LOS_ANGELES_LAKERS
    - include_inactive_games → False (bool)
    - include_combined_values → False (bool)
    """
    params: dict[str, Any] = {}
    for param_name in endpoint.params:
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
        elif param_name == "home_team":
            params[param_name] = Team.LOS_ANGELES_LAKERS
        elif param_name in ("include_inactive_games", "include_combined_values"):
            params[param_name] = False
    return params


def build_url(endpoint: Any, params: dict[str, Any]) -> str:
    """Compute the request URL for reporting.

    Format the endpoint path template with params; on failure (e.g. custom
    endpoints with multi-part paths, or ``standings_by_date`` whose path
    contains ``{conference}`` that is *not* in params) fall back to the raw
    template string.  Prefix with ``https://www.basketball-reference.com``.
    """
    try:
        formatted = endpoint.path.format(**params)
    except (KeyError, IndexError, ValueError, TypeError):
        formatted = endpoint.path
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
        entry["row_count"] = sum(
            len(v) for v in result.values() if isinstance(v, list)
        )
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
    args = parser.parse_args()

    seed: int = args.seed
    random.seed(seed)

    started_at = datetime.now(timezone.utc)
    total = len(ENDPOINTS)
    endpoint_items = list(ENDPOINTS.items())  # insertion-order snapshot

    results: list[dict[str, Any]] = []
    jailed = False
    t0 = time.perf_counter()

    for i, (name, endpoint) in enumerate(endpoint_items, 1):
        # ── Already jailed → skip ──
        if jailed:
            results.append({
                "name": name,
                "status": "skipped",
                "reason": "rate_limit_jailed_earlier",
            })
            print(
                f"[{i:2d}/{total}] {name} ... SKIPPED  (rate_limit_jailed_earlier)",
                flush=True,
            )
            continue

        # ── Apply hardcoded overrides ──
        if name in HARDCODED_PARAMS:
            params = dict(HARDCODED_PARAMS[name])
        else:
            params = build_params(endpoint)

        url = build_url(endpoint, params)

        # ── Call the endpoint ──
        try:
            func = getattr(client, name)
        except AttributeError:
            # Shouldn't happen if registry ↔ client exports stay in sync
            results.append({
                "name": name,
                "status": "error",
                "duration_s": 0.0,
                "params": _serialize_params(params),
                "url": url,
                "error_type": "AttributeError",
                "error_message": f"Function '{name}' not found on client module",
                "error_category": "other",
                "traceback": "",
            })
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
        "total_endpoints": total,
        "elapsed_s": round(elapsed, 2),
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
    md_lines.append(f"- **Elapsed**: {meta['elapsed_s']:.1f}s")
    md_lines.append(f"- **Total endpoints**: {meta['total_endpoints']}")
    md_lines.append(f"- **OK**: {meta['summary']['ok']}")
    md_lines.append(f"- **Error**: {meta['summary']['error']}")
    md_lines.append(f"- **Skipped**: {meta['summary']['skipped']}")
    if by_category:
        md_lines.append(f"- **By category**: {json.dumps(by_category)}")
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
        md_lines.append(f"- **Params**: `{json.dumps(r.get('params', {}), default=str)}`")
        md_lines.append(f"- **URL**: `{r.get('url', '')}`")
        md_lines.append(f"- **Status**: {r['status']}")

        if r["status"] == "ok":
            md_lines.append(f"- **Duration**: {r.get('duration_s', 0):.3f}s")
            md_lines.append(f"- **Row count**: {r.get('row_count', 0)}")
            md_lines.append(f"- **Columns**: `{json.dumps(r.get('keys_or_columns', []))}`")
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
