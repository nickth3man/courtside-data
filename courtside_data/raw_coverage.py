"""Generated-style endpoint coverage for the local raw Basketball-Reference corpus.

The hand-written registry remains the source of truth for curated typed
endpoints.  This module adds the broad fixture coverage layer used while the
project is being expanded toward every Basketball-Reference page family found
in ``raw/``.  Generated endpoints intentionally avoid row models: their output
shape is the table's raw ``data-stat``/header keys, and CSV columns are detected
from the parsed rows.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parent.parent
_RAW_ROOT = _REPO_ROOT / "raw"
_BACKLOG_PATH = _REPO_ROOT / "docs" / "raw_coverage_backlog.json"
_REPORT_PATH = _REPO_ROOT / "docs" / "unserved_data_report.json"

_PLACEHOLDER_MAP = {
    "ID": "team_abbreviation",
    "TEAM": "team_abbreviation",
    "YEAR": "season_end_year",
    "YYYY": "season_end_year",
    "SEASON": "season_end_year",
    "YYYYMMDD": "game_date",
    "GAME_CODE": "game_code",
    "PLAYER": "player_identifier",
}


def extend_endpoints(endpoints: dict[str, Any], endpoint_cls: type[Any]) -> None:
    """Append raw-corpus endpoints to ``endpoints`` in-place.

    The extension is best-effort and intentionally silent when the raw corpus or
    generated unserved-data report is absent, so installed-package imports do not
    depend on developer-only fixture artifacts.
    """

    report = _load_report()
    if not report:
        return

    for family in report.get("unserved_families", []):
        if family.get("html_files", 0) <= 0:
            continue
        family_name = family["family"]
        metas = _family_sidecars(family_name)
        if not metas:
            continue
        path = _path_template(metas[0])
        table_ids = _ordered_table_ids(family, metas)
        if table_ids:
            for index, table_id in enumerate(table_ids):
                endpoint_name = family_name if index == 0 else _dedupe_name(
                    endpoints,
                    f"{family_name}_{_normalize_identifier(table_id)}",
                )
                if endpoint_name in endpoints:
                    continue
                endpoints[endpoint_name] = endpoint_cls(
                    path=path,
                    params=_params_for_path(path),
                    table_id=table_id,
                    commented_table_id=table_id,
                    use_header_fallback=True,
                )
        elif family_name not in endpoints:
            endpoints[family_name] = endpoint_cls(
                path=path,
                params=_params_for_path(path),
                use_header_fallback=True,
                transaction_list_fallback="transactions" in family_name,
            )

    for group in report.get("orphan_tables", []):
        path = group["path"]
        base = group.get("endpoint_dirs", ["raw"])[0]
        for table_id in group.get("orphans", []):
            endpoint_name = _dedupe_name(endpoints, f"{base}_{_normalize_identifier(table_id)}")
            endpoints[endpoint_name] = endpoint_cls(
                path=path,
                params=_params_for_path(path),
                table_id=table_id,
                commented_table_id=table_id,
                use_header_fallback=True,
            )


def _load_report() -> dict[str, Any]:
    source = _BACKLOG_PATH if _BACKLOG_PATH.exists() else _REPORT_PATH
    if not source.exists():
        return {}
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _family_sidecars(family: str) -> list[dict[str, Any]]:
    family_dir = _RAW_ROOT / family
    if not family_dir.is_dir():
        return []
    metas: list[dict[str, Any]] = []
    for path in sorted(family_dir.rglob("*.html.meta.json")):
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("status_code", 200) == 200:
            metas.append(meta)
    return metas


def _ordered_table_ids(family: dict[str, Any], metas: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for candidate in family.get("discovered_table_ids", []):
        if candidate and candidate not in ids:
            ids.append(candidate)
    for meta in metas:
        for candidate in meta.get("discovered_table_ids", []):
            if candidate and candidate not in ids:
                ids.append(candidate)
    return ids


def _path_template(meta: dict[str, Any]) -> str:
    pattern = str(meta.get("canonical_pattern") or "")
    if pattern:
        converted = _convert_placeholders(pattern)
        cleaned = _clean_path_template(converted)
        if _is_valid_format_template(cleaned):
            return cleaned
    parsed = urlparse(str(meta.get("final_url") or meta.get("url") or ""))
    return parsed.path or pattern or "/"


def _clean_path_template(pattern: str) -> str:
    """Strip corpus notes from generated URL templates.

    Some raw sidecars preserve human notes in ``canonical_pattern`` (for
    example ``, player_post_*.html`` or ``(~30 stats x 7-9 views)``). Keep the
    concrete URL template only, so generated endpoints and smoke reports format
    usable Basketball-Reference paths.
    """

    return pattern.strip().split(",", 1)[0].split(None, 1)[0].split("#", 1)[0]


def _convert_placeholders(pattern: str) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        if "," in raw or raw.startswith("{"):
            return match.group(0)
        return "{" + _PLACEHOLDER_MAP.get(raw, _normalize_identifier(raw)) + "}"

    return re.sub(r"\{([^{}]+)\}", replace, pattern)


def _is_valid_format_template(pattern: str) -> bool:
    try:
        for field in re.findall(r"\{([^{}]+)\}", pattern):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]+\])?", field):
                return False
        pattern.format(**{param: "X" for param in _params_for_path(pattern)})
    except (KeyError, IndexError, ValueError):
        return False
    return True


def _params_for_path(path: str) -> tuple[str, ...]:
    params: list[str] = []
    for raw in re.findall(r"\{([^{}]+)\}", path):
        clean = re.sub(r"\[[^\]]*\]", "", raw)
        if clean not in params:
            params.append(clean)
    return tuple(params)


def _normalize_identifier(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", value.strip().lower()).strip("_")
    if not normalized:
        normalized = "table"
    if normalized[0].isdigit():
        normalized = f"t_{normalized}"
    return normalized


def _dedupe_name(endpoints: dict[str, Any], preferred: str) -> str:
    if preferred not in endpoints:
        return preferred
    index = 2
    while f"{preferred}_{index}" in endpoints:
        index += 1
    return f"{preferred}_{index}"
