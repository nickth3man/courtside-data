#!/usr/bin/env python3
"""Offline audit: reconcile the ``raw/`` corpus against the endpoint registry.

For every endpoint in :data:`courtside_data.endpoints.ENDPOINTS`, this tool
extracts the REAL ``data-stat`` keys present in that endpoint's downloaded
fixture table(s) and diffs them against the declared column contract — the
union of the endpoint's ``csv_columns`` and its row model's
``validation_alias`` values. It surfaces three classes of drift:

* **MISSING** — a real ``data-stat`` key present in the page table but absent
  from the contract. The runtime keeps such columns out of the served data
  (``extra="ignore"`` on ``BRRow``), so this is silent data loss / incompleteness.
* **EXTRA** — a declared key never seen in any fixture. Possibly a stale or
  typo'd contract column (or a column only valid for seasons not in the corpus).
* **UNRESOLVED** — a 200-status fixture whose declared table id(s) do not match
  any table on the page (visible or comment-wrapped): a table-id drift.

The audit is **offline**: it reads only ``raw/<endpoint>/**.html`` plus the
``*.html.meta.json`` sidecars and the in-process registry. It re-uses the same
extraction primitives the runtime uses (:class:`courtside_data.tables.GenericTable`
and :func:`courtside_data.tables.extract_commented_table`) so it sees exactly
what ``HTTPService.fetch_table`` would produce, without importing the HTTP /
cache / rate-limit machinery.

Usage
-----
    python scripts/audit_table_coverage.py                 # human report
    python scripts/audit_table_coverage.py --json out.json # + machine report
    python scripts/audit_table_coverage.py --endpoint league_per_game_stats
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from parsel import Selector
from pydantic import AliasChoices

# Make the repo importable regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from courtside_data.endpoints import ENDPOINTS, TableEndpoint  # noqa: E402
from courtside_data.schemas._base import BRRow  # noqa: E402
from courtside_data.tables import GenericTable, extract_commented_table  # noqa: E402

DEFAULT_CORPUS_ROOT = REPO_ROOT / "raw"

# ── Allowlists ─────────────────────────────────────────────────────────────
# Structural cells that GenericTable keeps (they carry a data-stat) but that are
# never real, user-facing columns.
GLOBAL_DROP_KEYS: frozenset[str] = frozenset(
    {
        "ranker",  # row-number gutter cell (first column of every stats table)
        "",  # empty-string data-stat (e.g. blank spacer cells)
        "counter",  # "Count" column header in awards/milestones tables
        "DUMMY",  # over-header spacer cell used to separate grouped stat columns
    }
)


def _is_dropped_key(key: str) -> bool:
    return key in GLOBAL_DROP_KEYS or key.startswith("header")


# Declared columns legitimately absent from the corpus's eras (kept minimal;
# the union-across-fixtures usually removes the need). Key: endpoint -> data-stat keys.
# Entries here are backward-compat AliasChoices aliases that don't appear as
# data-stat keys on the page but are kept for API stability.
ERA_OK_EXTRA: dict[str, set[str]] = {
    "franchise_history": {"team_abbreviation", "team_name_abbr"},
    "player_career_stats": {"league_id", "season"},
    "rookie_stats": {"name_display", "pos", "team_name_abbr"},
}

# Known gaps deliberately not fixed yet (debt escape hatch). Key: endpoint -> data-stat keys.
KNOWN_MISSING_ACCEPTED: dict[str, set[str]] = {}

# Endpoints whose row model intentionally models a curated subset of a much
# wider page table (so "missing" columns are by design, not drift).
INTENTIONAL_SUBSET: frozenset[str] = frozenset({"attendance"})


@dataclass
class EndpointAudit:
    endpoint: str
    fixtures: list[str] = field(default_factory=list)
    real_keys: set[str] = field(default_factory=set)
    declared_keys: set[str] = field(default_factory=set)
    missing: set[str] = field(default_factory=set)
    extra: set[str] = field(default_factory=set)
    unresolved_fixtures: list[str] = field(default_factory=list)
    table_id_declared: list[str] = field(default_factory=list)
    table_id_discovered: list[str] = field(default_factory=list)
    table_id_mismatch: bool = False
    custom: bool = False
    header_fallback: bool = False
    transaction_list: bool = False
    intentional_subset: bool = False
    skipped_reason: str | None = None

    @property
    def actionable(self) -> bool:
        """True for endpoints whose missing/unresolved findings warrant a fix."""
        if self.skipped_reason is not None:
            return False
        if self.header_fallback or self.transaction_list or self.intentional_subset or self.custom:
            return False
        return bool(self.missing) or bool(self.unresolved_fixtures) or self.table_id_mismatch

    @property
    def has_any_finding(self) -> bool:
        return bool(self.missing or self.extra or self.unresolved_fixtures or self.table_id_mismatch)

    def to_json(self) -> dict[str, Any]:
        return {
            "fixtures": self.fixtures,
            "real_keys": sorted(self.real_keys),
            "declared_keys": sorted(self.declared_keys),
            "missing": sorted(self.missing),
            "extra": sorted(self.extra),
            "unresolved_fixtures": self.unresolved_fixtures,
            "table_id_declared": self.table_id_declared,
            "table_id_discovered": self.table_id_discovered,
            "table_id_mismatch": self.table_id_mismatch,
            "custom": self.custom,
            "header_fallback": self.header_fallback,
            "transaction_list": self.transaction_list,
            "intentional_subset": self.intentional_subset,
            "skipped_reason": self.skipped_reason,
        }


def model_datastat_keys(model: type[BRRow] | None) -> set[str]:
    """Return the set of ``data-stat`` keys a row model reads.

    For each field the read key is its ``validation_alias`` (a plain string, or
    each string member of an ``AliasChoices``); fields with no alias are read by
    their Python attribute name (``populate_by_name=True`` on ``BRRow``).
    """
    keys: set[str] = set()
    if model is None:
        return keys
    for name, info in model.model_fields.items():
        alias = info.validation_alias
        if alias is None:
            keys.add(name)
        elif isinstance(alias, str):
            keys.add(alias)
        elif isinstance(alias, AliasChoices):
            keys.update(choice for choice in alias.choices if isinstance(choice, str))
        else:  # pragma: no cover - defensive
            keys.add(name)
    return keys


def declared_keys(endpoint: TableEndpoint) -> set[str]:
    declared = set(endpoint.csv_columns or ())
    declared |= model_datastat_keys(endpoint.row_model)
    return declared


def _sidecar_for(html_path: Path) -> dict[str, Any]:
    sidecar_path = html_path.with_name(html_path.name + ".meta.json")
    if not sidecar_path.exists():
        return {}
    try:
        return json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _candidate_table_ids(endpoint: TableEndpoint, sidecar: dict[str, Any]) -> list[str]:
    """Table ids to try, in resolution order.

    The downloader records the rendered expected ids in the sidecar's
    ``table_ids`` (handles templated ids like ``franchise_history``); fall back
    to the endpoint's static (non-templated) ids.
    """
    ids: list[str] = [tid for tid in sidecar.get("table_ids", []) if tid]
    for candidate in (endpoint.table_id, endpoint.commented_table_id, *endpoint.fallback_table_ids):
        if candidate and "{" not in candidate and candidate not in ids:
            ids.append(candidate)
    return ids


def _resolve_table(selector: Selector, endpoint: TableEndpoint, sidecar: dict[str, Any]) -> Selector | None:
    """Find the endpoint's target table on a page for any candidate id.

    The resolution order mirrors ``HTTPService.fetch_table`` — CSS
    ``table#<id>`` first, then comment-wrapped fallback — but with one
    **deliberate broadening for audit purposes**: ``extract_commented_table``
    is tried for *every* candidate id, not just ``commented_table_id``.
    ``fetch_table`` only unwraps ``commented_table_id`` because the
    downloader already knows which table is comment-wrapped.  An audit
    tool cannot assume that: if a table has drifted from visible to
    comment-wrapped (or vice versa), the audit still needs to locate it
    and flag the mismatch.  This broadening is by design.
    """
    for table_id in _candidate_table_ids(endpoint, sidecar):
        found = _find_table_by_id(selector, table_id)
        if found:
            return found[0]
        commented = extract_commented_table(selector, table_id)
        if commented is not None:
            return commented
    if endpoint.table_id is None and endpoint.commented_table_id is None:
        found = selector.css("table")
        if found:
            return found[0]
    return None


def _xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"


def _find_table_by_id(selector: Selector, table_id: str) -> list[Selector]:
    return list(selector.xpath(f"//table[@id={_xpath_literal(table_id)}]"))


def _extract_params_from_url(url: str, path_template: str) -> dict[str, str]:
    """Extract format-string params from a URL using the endpoint's path template.

    Converts a path template like ``/teams/{team_abbreviation}/`` into a regex
    with named groups, then matches against the URL's path component.  Returns
    an empty dict if the URL / template is missing or matching fails.
    """
    if not url or not path_template or "{" not in path_template:
        return {}
    parsed = urlparse(url)
    url_path = parsed.path
    # Build regex: escape template, then replace escaped braces with named groups.
    escaped = re.escape(path_template)

    def _replacement(m: re.Match[str]) -> str:
        raw = m.group(1)
        # Strip Python format-spec suffixes like [0] for valid regex group name
        clean = re.sub(r"\[[^\]]*\]", "", raw)
        return f"(?P<{clean}>[^/]+)"

    try:
        pattern = re.sub(r"\\\{([^}]+)\\\}", _replacement, escaped)
        compiled = re.compile(f"^{pattern}$")
    except re.error:
        return {}
    match = compiled.match(url_path)
    if match:
        return match.groupdict()
    return {}


def _render_table_id(template: str | None, params: dict[str, str]) -> str | None:
    """Render a table_id template with *params*, returning None on failure."""
    if template is None:
        return None
    if "{" not in template:
        return template
    try:
        return template.format(**params)
    except (KeyError, ValueError, IndexError):
        return None


def _declared_table_ids(endpoint: TableEndpoint, params: dict[str, str]) -> set[str]:
    """Build the rendered declared table-id set for one fixture."""
    ids: set[str] = set()
    for tid in (endpoint.table_id, endpoint.commented_table_id, *endpoint.fallback_table_ids):
        rendered = _render_table_id(tid, params)
        if rendered:
            ids.add(rendered)
    return ids


def _real_keys_for_fixture(html_text: str, endpoint: TableEndpoint, sidecar: dict[str, Any]) -> tuple[list[str], bool]:
    """Return (ordered real data-stat keys, resolved?) for one fixture.

    Keys are returned in first-seen document order (the union of each row's
    keys, in order), which is the order the contract should list them.
    """
    selector = Selector(text=html_text)
    table = _resolve_table(selector, endpoint, sidecar)
    if table is None:
        return [], False
    ordered: list[str] = []
    seen: set[str] = set()
    for row in generic_rows(table, endpoint):
        for key in row:
            if key not in seen:
                seen.add(key)
                ordered.append(key)
    return ordered, True


def generic_rows(table: Selector, endpoint: TableEndpoint) -> list[dict[str, str]]:
    generic = GenericTable(table, use_header_fallback=endpoint.use_header_fallback)
    return [row.to_dict() for row in generic.rows]


def ordered_real_keys(name: str, endpoint: TableEndpoint, corpus_root: Path) -> list[str]:
    """Ordered, drop-filtered real keys, from the most complete (modern) fixture.

    Older-era fixtures omit columns (3pt, steals, blocks ...), so the canonical
    column order comes from whichever 200 fixture yields the most keys; any keys
    seen only in other fixtures are appended at the end.
    """
    best: list[str] = []
    extras: list[str] = []
    seen: set[str] = set()
    for html_path in discover_fixtures(corpus_root, name):
        sidecar = _sidecar_for(html_path)
        if sidecar.get("status_code", 200) != 200:
            continue
        try:
            html_text = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        keys, resolved = _real_keys_for_fixture(html_text, endpoint, sidecar)
        if not resolved:
            continue
        filtered = [k for k in keys if not _is_dropped_key(k)]
        if len(filtered) > len(best):
            best = filtered
        for key in filtered:
            seen.add(key)
    base_set = set(best)
    for key in seen:
        if key not in base_set:
            extras.append(key)
    return best + sorted(extras)


def discover_fixtures(corpus_root: Path, endpoint_name: str) -> list[Path]:
    endpoint_dir = corpus_root / endpoint_name
    if not endpoint_dir.is_dir():
        return []
    return sorted(p for p in endpoint_dir.rglob("*.html") if p.is_file())


# Matches ``<table ... id="X">`` in raw HTML, including tables nested inside
# HTML comments (comment-wrapped tables are part of the raw text).  Case-
# insensitive; tolerates single/double quotes and attributes preceding ``id``.
_TABLE_ID_RE = re.compile(r"""<table\b[^>]*?\bid=["']([^"']+)["']""", re.IGNORECASE)


def _discover_table_ids_from_html(html_text: str) -> set[str]:
    """Return every ``<table id="...">`` id present in *html_text*.

    Scans the raw markup so tables wrapped in ``<!-- ... -->`` comments are
    included.  This is the audit's authoritative source of "which table ids
    does this page actually contain" and intentionally does NOT depend on
    sidecar vintage: a large fraction of corpus sidecars predate the
    ``discovered_table_ids`` field and would otherwise yield an empty
    discovered set, producing false-positive table-id mismatches.
    """
    return {tid for tid in _TABLE_ID_RE.findall(html_text)}


def audit_endpoint(name: str, endpoint: TableEndpoint, corpus_root: Path) -> EndpointAudit:
    result = EndpointAudit(
        endpoint=name,
        custom=endpoint.custom,
        header_fallback=endpoint.use_header_fallback,
        transaction_list=endpoint.transaction_list_fallback,
        intentional_subset=name in INTENTIONAL_SUBSET,
    )
    result.declared_keys = declared_keys(endpoint)

    fixtures = discover_fixtures(corpus_root, name)
    if not fixtures:
        result.skipped_reason = "no fixtures in corpus"
        return result

    real: set[str] = set()
    declared_table_ids: set[str] = set()
    discovered_table_ids: set[str] = set()

    for html_path in fixtures:
        rel = html_path.relative_to(corpus_root).as_posix()
        result.fixtures.append(rel)
        sidecar = _sidecar_for(html_path)

        # ── Table-id comparison (per-fixture, union across all eras) ──────
        # Even for custom / header-fallback / transaction-list endpoints we
        # collect the declared-vs-discovered table-id sets so the JSON report
        # always carries them.  The mismatch boolean is the primary signal.
        params = _extract_params_from_url(
            sidecar.get("final_url") or sidecar.get("url", ""),
            endpoint.path,
        )
        declared_table_ids |= _declared_table_ids(endpoint, params)

        if sidecar.get("status_code", 200) != 200:
            continue  # 404 / error fixtures carry no table
        try:
            html_text = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # ── Discovered table ids — ground truth read from the page itself ──
        # Every <table id="..."> in the raw markup (comment-wrapped tables
        # included).  This is authoritative and self-contained; the sidecar's
        # `discovered_table_ids` is unioned in only as a cross-check, since
        # ~62% of corpus sidecars predate that field and would otherwise make
        # the discovered set look empty (false-positive mismatches).
        discovered_table_ids |= _discover_table_ids_from_html(html_text)
        sidecar_discovered = sidecar.get("discovered_table_ids")
        if sidecar_discovered:
            discovered_table_ids |= {tid for tid in sidecar_discovered if tid}

        if endpoint.custom:
            # Custom endpoints (bespoke HTTPService methods) have no single
            # fetch_table-style resolution.  Give them a lighter audit:
            # collect every data-stat key found across ALL <table> elements
            # on the page — visible via CSS and comment-wrapped via regex.
            selector = Selector(text=html_text)
            page_keys: set[str] = set(selector.css("table [data-stat]::attr(data-stat)").getall())
            # Also scan raw HTML for data-stat inside comment-wrapped tables.
            for comment_body in re.findall(r"<!--(.*?)-->", html_text, flags=re.DOTALL):
                page_keys.update(re.findall(r"""data-stat=["']([^"']+)["']""", comment_body))
            real.update(page_keys)
        else:
            keys, resolved = _real_keys_for_fixture(html_text, endpoint, sidecar)
            real.update(keys)
            # Only call a fixture "unresolved" when a table was genuinely expected:
            # transaction-list endpoints have no data-stat table by design.
            if not resolved and not endpoint.transaction_list_fallback and _candidate_table_ids(endpoint, sidecar):
                result.unresolved_fixtures.append(rel)

    result.real_keys = {key for key in real if not _is_dropped_key(key)}
    result.table_id_declared = sorted(declared_table_ids)
    result.table_id_discovered = sorted(discovered_table_ids)
    result.table_id_mismatch = bool(declared_table_ids - discovered_table_ids)

    if result.transaction_list or result.header_fallback:
        # No data-stat column contract to diff; keep table-resolution signal only.
        return result

    accepted_missing = KNOWN_MISSING_ACCEPTED.get(name, set())
    era_ok_extra = ERA_OK_EXTRA.get(name, set())
    result.missing = result.real_keys - result.declared_keys - accepted_missing
    result.extra = result.declared_keys - result.real_keys - era_ok_extra
    return result


def run_audit(corpus_root: Path, only: str | None = None) -> list[EndpointAudit]:
    names = [only] if only else list(ENDPOINTS)
    return [audit_endpoint(name, ENDPOINTS[name], corpus_root) for name in names if name in ENDPOINTS]


def summarize(results: list[EndpointAudit]) -> dict[str, int]:
    audited = [r for r in results if r.skipped_reason is None]
    actionable = [r for r in results if r.actionable]
    return {
        "endpoints_audited": len(audited),
        "endpoints_skipped_no_fixtures": sum(1 for r in results if r.skipped_reason),
        "endpoints_with_drift": len(actionable),
        "total_missing_columns": sum(len(r.missing) for r in actionable),
        "total_extra_columns": sum(len(r.extra) for r in results if not (r.header_fallback or r.transaction_list)),
        "table_id_mismatches": sum(1 for r in results if r.table_id_mismatch),
    }


def print_report(results: list[EndpointAudit]) -> None:
    summary = summarize(results)
    print("=" * 78)
    print("TABLE COVERAGE AUDIT  (raw/ corpus vs ENDPOINTS registry)")
    print("=" * 78)
    for key, value in summary.items():
        print(f"  {key:32} {value}")

    actionable = [r for r in results if r.actionable]
    if actionable:
        print("\n" + "-" * 78)
        print("ACTION NEEDED — missing real columns / unresolved tables / table-id mismatches")
        print("-" * 78)
        for r in sorted(actionable, key=lambda a: a.endpoint):
            print(f"\n• {r.endpoint}")
            if r.missing:
                print(f"    MISSING ({len(r.missing)}): {', '.join(sorted(r.missing))}")
            if r.extra:
                print(f"    extra   ({len(r.extra)}): {', '.join(sorted(r.extra))}")
            if r.table_id_mismatch:
                print("    TABLE-ID MISMATCH")
                print(f"        declared (rendered): {r.table_id_declared}")
                print(f"        discovered (sidecar): {r.table_id_discovered}")
            for fixture in r.unresolved_fixtures:
                print(f"    UNRESOLVED table in fixture: {fixture}")

    advisory = [
        r
        for r in results
        if r.skipped_reason is None
        and not r.actionable
        and (r.has_any_finding or r.custom or r.header_fallback or r.transaction_list or r.intentional_subset)
    ]
    if advisory:
        print("\n" + "-" * 78)
        print("ADVISORY — custom / header-fallback / transaction / intentional-subset")
        print("-" * 78)
        for r in sorted(advisory, key=lambda a: a.endpoint):
            tags = []
            if r.custom:
                tags.append("custom")
            if r.header_fallback:
                tags.append("header_fallback")
            if r.transaction_list:
                tags.append("transaction_list")
            if r.intentional_subset:
                tags.append("intentional_subset")
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            note = []
            if r.missing:
                note.append(f"missing={len(r.missing)}")
            if r.extra:
                note.append(f"extra={len(r.extra)}")
            if r.table_id_mismatch:
                note.append("table_id_mismatch")
            if r.unresolved_fixtures:
                note.append(f"unresolved={len(r.unresolved_fixtures)}")
            print(f"• {r.endpoint}{tag_str} {' '.join(note)}")

    skipped = [r for r in results if r.skipped_reason]
    if skipped:
        print("\n" + "-" * 78)
        print("SKIPPED")
        print("-" * 78)
        for r in sorted(skipped, key=lambda a: a.endpoint):
            print(f"• {r.endpoint}: {r.skipped_reason}")
    print()


def write_json(path: Path, results: list[EndpointAudit]) -> None:
    payload = {
        "summary": summarize(results),
        "endpoints": {r.endpoint: r.to_json() for r in results},
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus-root", default=str(DEFAULT_CORPUS_ROOT), help="Path to the raw/ corpus")
    parser.add_argument("--endpoint", default=None, help="Audit only this endpoint key")
    parser.add_argument("--json", dest="json_path", default=None, help="Also write a machine-readable JSON report")
    parser.add_argument(
        "--keys",
        action="store_true",
        help="Print the ordered REAL data-stat keys (authoring input) instead of the audit report",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus_root = Path(args.corpus_root)
    if not corpus_root.is_dir():
        print(f"Corpus root not found: {corpus_root} (run scripts/raw_download.py first)", file=sys.stderr)
        return 2

    if args.keys:
        names = [args.endpoint] if args.endpoint else list(ENDPOINTS)
        for name in names:
            if name not in ENDPOINTS:
                continue
            endpoint = ENDPOINTS[name]
            real = ordered_real_keys(name, endpoint, corpus_root)
            declared = declared_keys(endpoint)
            print(f"\n# {name}")
            print(f"real ({len(real)}): {real}")
            missing = [k for k in real if k not in declared]
            print(f"missing-from-contract ({len(missing)}): {missing}")
        return 0

    results = run_audit(corpus_root, only=args.endpoint)
    print_report(results)
    if args.json_path:
        write_json(Path(args.json_path), results)
        print(f"Wrote JSON report to {args.json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
