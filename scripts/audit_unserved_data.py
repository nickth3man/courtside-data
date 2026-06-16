#!/usr/bin/env python3
"""Offline inventory: what data in ``raw/`` does the project NOT serve?

The ``raw/`` corpus is downloaded from two sources (see ``scripts/raw_download.py``):
the ``courtside_data.endpoints.ENDPOINTS`` registry **and** the page-family
inventory in ``docs/bref_new_page_families.csv``. As a result the corpus contains
far more basketball-reference data than the registered endpoints actually
serve. This tool reconciles the corpus against the registry and reports the gap
across four layers:

* **§A Unserved page families** — ``raw/<dir>`` directories with no endpoint at
  all (allstar/friv/leaders/franchise/coaches/playoff_year/… families fetched
  from the CSV inventory but never wired into a parser).
* **§B Dropped columns** — ``data-stat`` keys present in a *served* endpoint's
  table but absent from its column contract; the runtime drops them via
  ``extra="ignore"`` on ``BRRow``. This layer is computed by re-running
  ``scripts/audit_table_coverage.py`` (its **MISSING** set) — folded in verbatim.
* **§C Orphan tables on served pages** — ``<table id>``s present on a page we
  already download for some endpoint, that *no* registry endpoint declares
  (e.g. the playoff ``_post`` splits and ``adj_shooting``/``totals_stats``
  tables on a team page whose only served table is ``roster``).
* **§D Disallowed / off-domain** — page families in the CSV that ``raw_download``
  deliberately never fetched (robots-disallowed, reachable via another endpoint,
  or off-domain). These have no fixtures; sourced purely from the CSV.

The audit is **read-only** over ``raw/`` and re-uses the exact extraction
primitives the runtime uses, via helpers imported from
``scripts/audit_table_coverage.py``.

Usage
-----
    python scripts/audit_unserved_data.py
    python scripts/audit_unserved_data.py --md docs/unserved_data_report.md \\
                                          --json docs/unserved_data_report.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make both the repo root and this scripts/ dir importable regardless of cwd or
# invocation style (``python scripts/x.py`` vs ``python -m scripts.x``).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (str(REPO_ROOT), str(SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audit_table_coverage as ata  # noqa: E402  (sibling script — reused primitives)

from courtside_data.endpoints import ENDPOINTS  # noqa: E402

DEFAULT_CORPUS_ROOT = REPO_ROOT / "raw"
DEFAULT_CSV = REPO_ROOT / "docs" / "bref_new_page_families.csv"
DEFAULT_MD = REPO_ROOT / "docs" / "unserved_data_report.md"
DEFAULT_JSON = REPO_ROOT / "docs" / "unserved_data_report.json"

# Non-fixture directories under raw/ that are not endpoints and not page families.
NON_FAMILY_DIRS: frozenset[str] = frozenset({"errors", "_failures"})

# Table ids parsed by bespoke (custom=True) HTTPService methods that are NOT
# declared in the registry. Without these, the tables they parse would show up
# as false-positive orphans on pages shared with declarative endpoints.
CUSTOM_PARSED_TABLE_IDS: dict[str, set[str]] = {
    "standings": {"divs_standings_E", "divs_standings_W"},
    "players_season_totals": {"totals_stats"},
    "players_advanced_season_totals": {"advanced_stats", "advanced"},
    "season_schedule": {"schedule", "games"},
}

# Custom endpoints whose target tables are page-instance-specific (e.g.
# ``box-NYK-game-basic``) or fanned across many requests — orphan detection is
# meaningless for the pages they own, so they are not subjects of §C.
DYNAMIC_CUSTOM_ENDPOINTS: frozenset[str] = frozenset(
    {
        "player_box_scores",
        "team_box_scores",
        "play_by_play",
        "search",
        "regular_season_player_box_scores",
        "playoff_player_box_scores",
    }
)

# Substrings in a CSV row's parser_requirements that mark it as a bespoke
# multi-table page rather than a trivial single-table scrape.
_BESPOKE_MARKERS: tuple[str, ...] = ("bespoke", "non-trivial", "multi-table", "multi-anchor", "svg")


# ── CSV inventory ────────────────────────────────────────────────────────────
def load_csv_inventory(csv_path: Path) -> dict[str, dict[str, str]]:
    """Return ``{page_family: row}`` for the page-family inventory CSV."""
    if not csv_path.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            family = (row.get("page_family") or "").strip()
            if family:
                rows[family] = row
    return rows


def _is_bespoke(parser_requirements: str) -> bool:
    text = parser_requirements.lower()
    return any(marker in text for marker in _BESPOKE_MARKERS)


def _normalize_table_id(value: str) -> str:
    """Normalize known corpus/report table-id spelling drift."""

    return re.sub(r"(-man_)_p$", r"\1p", value)


# ── Corpus helpers ───────────────────────────────────────────────────────────
def list_corpus_dirs(corpus_root: Path) -> list[str]:
    """Endpoint/page-family directory names that hold fixtures (top level)."""
    if not corpus_root.is_dir():
        return []
    return sorted(p.name for p in corpus_root.iterdir() if p.is_dir() and not p.name.startswith("__"))


def _family_table_ids(corpus_root: Path, family: str) -> tuple[list[str], int, int]:
    """(sorted discovered table ids, html file count, 200-status file count).

    Prefers each fixture's sidecar ``discovered_table_ids``; falls back to a
    direct scan of the markup (covers older sidecars that predate that field).
    """
    fixtures = ata.discover_fixtures(corpus_root, family)
    ids: set[str] = set()
    ok = 0
    for html_path in fixtures:
        sidecar = ata._sidecar_for(html_path)
        if sidecar.get("status_code", 200) == 200:
            ok += 1
        sidecar_ids = sidecar.get("discovered_table_ids") or []
        if sidecar_ids:
            ids.update(_normalize_table_id(tid) for tid in sidecar_ids if tid)
            continue
        try:
            html_text = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ids.update(_normalize_table_id(tid) for tid in ata._discover_table_ids_from_html(html_text))
    return sorted(ids), len(fixtures), ok


# ── §C orphan-table support ──────────────────────────────────────────────────
def build_claimed_by_path(corpus_root: Path) -> dict[str, set[str]]:
    """For each endpoint ``path`` template, the set of table ids any endpoint
    sharing that page declares (static ids + ids rendered from real fixtures +
    curated bespoke-parser ids).
    """
    claimed: dict[str, set[str]] = defaultdict(set)
    for name, ep in ENDPOINTS.items():
        bucket = claimed[ep.path]
        # Static (non-templated) declared ids.
        for tid in (ep.table_id, ep.commented_table_id, *ep.fallback_table_ids):
            if tid and "{" not in tid:
                bucket.add(_normalize_table_id(tid))
        bucket |= {_normalize_table_id(tid) for tid in CUSTOM_PARSED_TABLE_IDS.get(name, set())}
        # Templated ids (e.g. franchise_history "{team_abbreviation}") rendered
        # from each downloaded fixture's recorded URL.
        for html_path in ata.discover_fixtures(corpus_root, name):
            sidecar = ata._sidecar_for(html_path)
            params = ata._extract_params_from_url(sidecar.get("final_url") or sidecar.get("url", ""), ep.path)
            bucket |= {_normalize_table_id(tid) for tid in ata._declared_table_ids(ep, params)}
    return claimed


@dataclass
class OrphanGroup:
    path: str
    endpoint_dirs: list[str] = field(default_factory=list)
    claimed: list[str] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)


def find_orphan_tables(corpus_root: Path) -> list[OrphanGroup]:
    """Per shared page template, the discovered table ids no endpoint claims."""
    claimed_by_path = build_claimed_by_path(corpus_root)

    # Group declarative (subject-eligible) endpoints by their page template.
    path_to_dirs: dict[str, list[str]] = defaultdict(list)
    for name, ep in ENDPOINTS.items():
        if name in DYNAMIC_CUSTOM_ENDPOINTS:
            continue
        path_to_dirs[ep.path].append(name)

    groups: list[OrphanGroup] = []
    for path, names in sorted(path_to_dirs.items()):
        claimed = claimed_by_path.get(path, set())
        discovered: set[str] = set()
        contributing_dirs: list[str] = []
        for name in names:
            fixtures = ata.discover_fixtures(corpus_root, name)
            if fixtures:
                contributing_dirs.append(name)
            for html_path in fixtures:
                sidecar = ata._sidecar_for(html_path)
                if sidecar.get("status_code", 200) != 200:
                    continue
                try:
                    html_text = html_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                discovered |= {_normalize_table_id(tid) for tid in ata._discover_table_ids_from_html(html_text)}
        orphans = sorted(tid for tid in discovered - claimed if not ata._is_dropped_key(tid))
        if orphans:
            groups.append(
                OrphanGroup(
                    path=path,
                    endpoint_dirs=sorted(contributing_dirs),
                    claimed=sorted(claimed),
                    orphans=orphans,
                )
            )
    return groups


# ── Report assembly ──────────────────────────────────────────────────────────
def build_report(corpus_root: Path, csv_path: Path) -> dict[str, Any]:
    inventory = load_csv_inventory(csv_path)
    endpoint_names = set(ENDPOINTS)
    corpus_dirs = list_corpus_dirs(corpus_root)

    # §A — directories with fixtures that are not endpoints.
    unserved: list[dict[str, Any]] = []
    for family in corpus_dirs:
        if family in endpoint_names or family in NON_FAMILY_DIRS:
            continue
        meta = inventory.get(family, {})
        table_ids, file_count, ok_count = _family_table_ids(corpus_root, family)
        parser_req = (meta.get("parser_requirements") or "").strip()
        unserved.append(
            {
                "family": family,
                "html_files": file_count,
                "status_200_files": ok_count,
                "discovered_table_ids": table_ids,
                "category": (meta.get("category") or "").strip(),
                "tier": (meta.get("tier") or "").strip(),
                "robots_status": (meta.get("robots_status") or "").strip(),
                "resembles_endpoint": (meta.get("resembles_endpoint") or "").strip(),
                "parser_requirements": parser_req,
                "description": (meta.get("description") or "").strip(),
                "bespoke": _is_bespoke(parser_req),
                "in_csv": family in inventory,
            }
        )
    unserved.sort(key=lambda r: (r["category"], r["family"]))

    # §B — dropped columns on served endpoints (re-use the drift auditor verbatim).
    audits = ata.run_audit(corpus_root)
    dropped: dict[str, dict[str, Any]] = {}
    for r in audits:
        if r.skipped_reason is not None or not r.missing:
            continue
        tags = [
            t
            for t, on in (
                ("custom", r.custom),
                ("header_fallback", r.header_fallback),
                ("transaction_list", r.transaction_list),
                ("intentional_subset", r.intentional_subset),
            )
            if on
        ]
        dropped[r.endpoint] = {"missing": sorted(r.missing), "tags": tags, "actionable": r.actionable}

    # §C — orphan tables on served pages.
    orphan_groups = find_orphan_tables(corpus_root)

    # §D — disallowed / off-domain families (no fixtures; CSV-sourced).
    disallowed: list[dict[str, str]] = []
    for family, row in inventory.items():
        robots = (row.get("robots_status") or "").strip()
        tier = (row.get("tier") or "").strip()
        if robots == "allowed" and tier != "off_domain":
            continue
        if family in endpoint_names:
            continue
        disallowed.append(
            {
                "family": family,
                "category": (row.get("category") or "").strip(),
                "tier": tier,
                "robots_status": robots,
                "resembles_endpoint": (row.get("resembles_endpoint") or "").strip(),
                "description": (row.get("description") or "").strip(),
                "parser_requirements": (row.get("parser_requirements") or "").strip(),
            }
        )
    disallowed.sort(key=lambda r: (r["tier"], r["category"], r["family"]))

    summary = {
        "served_endpoints": len(ENDPOINTS),
        "corpus_dirs": len(corpus_dirs),
        "unserved_families": len(unserved),
        "unserved_families_trivial": sum(1 for r in unserved if not r["bespoke"]),
        "unserved_families_bespoke": sum(1 for r in unserved if r["bespoke"]),
        "endpoints_with_dropped_columns": len(dropped),
        "endpoints_with_dropped_columns_actionable": sum(1 for v in dropped.values() if v["actionable"]),
        "total_dropped_columns": sum(len(v["missing"]) for v in dropped.values()),
        "page_groups_with_orphan_tables": len(orphan_groups),
        "total_orphan_tables": sum(len(g.orphans) for g in orphan_groups),
        "disallowed_or_off_domain_families": len(disallowed),
    }

    return {
        "summary": summary,
        "unserved_families": unserved,
        "dropped_columns": dropped,
        "orphan_tables": [
            {"path": g.path, "endpoint_dirs": g.endpoint_dirs, "claimed": g.claimed, "orphans": g.orphans}
            for g in orphan_groups
        ],
        "disallowed_or_off_domain": disallowed,
    }


# ── Markdown rendering ───────────────────────────────────────────────────────
def _md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in rows]
    return out


def render_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines: list[str] = []
    lines.append("# Unserved data in `raw/` — coverage inventory")
    lines.append("")
    lines.append(
        "> Generated by `scripts/audit_unserved_data.py`. Read-only reconciliation of the "
        "`raw/` HTML corpus against `courtside_data.endpoints.ENDPOINTS`. See "
        "`docs/serving_new_endpoints.md` for how to turn any item below into a served endpoint."
    )
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines += _md_table(
        ["Metric", "Value"],
        [[k.replace("_", " "), str(v)] for k, v in s.items()],
    )
    lines.append("")

    # §A
    lines.append("## §A — Unserved page families (downloaded, no endpoint)")
    lines.append("")
    lines.append(
        f"{s['unserved_families']} directories under `raw/` hold fixtures but have no entry in "
        "`ENDPOINTS`. Each was fetched from the page-family inventory. "
        f"**{s['unserved_families_trivial']}** are trivial single-table scrapes; "
        f"**{s['unserved_families_bespoke']}** need bespoke multi-table parsers."
    )
    lines.append("")
    for bespoke, title in ((False, "Trivial table scrapes"), (True, "Bespoke multi-table pages")):
        group = [r for r in report["unserved_families"] if r["bespoke"] is bespoke]
        if not group:
            continue
        lines.append(f"### {title} ({len(group)})")
        lines.append("")
        rows = [
            [
                f"`{r['family']}`",
                r["category"] or "—",
                str(r["html_files"]),
                ", ".join(f"`{t}`" for t in r["discovered_table_ids"][:8])
                + ("…" if len(r["discovered_table_ids"]) > 8 else "")
                or "—",
                f"`{r['resembles_endpoint']}`" if r["resembles_endpoint"] else "—",
            ]
            for r in group
        ]
        lines += _md_table(["Family", "Category", "Files", "Discovered table ids", "Resembles"], rows)
        lines.append("")

    # §B
    lines.append("## §B — Dropped columns on served endpoints")
    lines.append("")
    lines.append(
        f"{s['endpoints_with_dropped_columns']} served endpoints have `data-stat` columns present "
        "in the HTML but absent from their contract (`csv_columns ∪ row_model aliases`); the runtime "
        'discards them via `extra="ignore"`. Computed by `audit_table_coverage.py` (its MISSING set).'
    )
    lines.append("")
    lines.append(
        f"**{s['endpoints_with_dropped_columns_actionable']} are actionable.** Endpoints tagged "
        "`custom` (the audit scans every table on their multi-table page, so most of these keys belong "
        "to tables the endpoint never parses), `header_fallback`, `transaction_list`, or "
        "`intentional_subset` are advisory — their wider key set is by design. A `0` actionable count "
        "means the declarative endpoints' column contracts are already complete for the corpus; the "
        "real coverage gap lives in §A (whole families) and §C (orphan tables)."
    )
    lines.append("")
    if report["dropped_columns"]:
        rows = []
        for endpoint in sorted(report["dropped_columns"]):
            info = report["dropped_columns"][endpoint]
            tag = f" _({', '.join(info['tags'])})_" if info["tags"] else ""
            rows.append(
                [
                    f"`{endpoint}`{tag}",
                    str(len(info["missing"])),
                    ", ".join(f"`{k}`" for k in info["missing"][:12]) + ("…" if len(info["missing"]) > 12 else ""),
                ]
            )
        lines += _md_table(["Endpoint", "# missing", "Missing data-stat keys"], rows)
    else:
        lines.append("_No dropped columns detected._")
    lines.append("")

    # §C
    lines.append("## §C — Orphan tables on already-downloaded pages")
    lines.append("")
    lines.append(
        f"{s['total_orphan_tables']} `<table id>`s appear on pages we already download for a served "
        f"endpoint but are declared by **no** endpoint ({s['page_groups_with_orphan_tables']} page "
        "templates affected). Grouped by page. **Caveat:** an orphan may still be reachable through a "
        "bespoke `custom=True` parser that does not declare its table id — verify before treating it "
        "as a hard gap."
    )
    lines.append("")
    for g in report["orphan_tables"]:
        lines.append(f"### `{g['path']}`")
        lines.append("")
        lines.append(f"- Served via: {', '.join(f'`{d}`' for d in g['endpoint_dirs']) or '—'}")
        lines.append(f"- Claimed tables: {', '.join(f'`{c}`' for c in g['claimed']) or '—'}")
        lines.append(f"- **Orphan tables ({len(g['orphans'])}):** {', '.join(f'`{o}`' for o in g['orphans'])}")
        lines.append("")

    # §D
    lines.append("## §D — Disallowed / off-domain families (no fixtures)")
    lines.append("")
    lines.append(
        f"{s['disallowed_or_off_domain_families']} page families exist upstream but were never "
        "downloaded into `raw/` — robots-disallowed, reachable via an existing endpoint, or "
        "off-domain. Sourced from `docs/bref_new_page_families.csv`; no fixtures exist for these."
    )
    lines.append("")
    rows = [
        [
            f"`{r['family']}`",
            r["tier"] or "—",
            r["robots_status"] or "—",
            r["category"] or "—",
            (r["description"][:90] + "…") if len(r["description"]) > 90 else (r["description"] or "—"),
        ]
        for r in report["disallowed_or_off_domain"]
    ]
    lines += _md_table(["Family", "Tier", "robots", "Category", "Why absent / note"], rows)
    lines.append("")

    return "\n".join(lines) + "\n"


# ── CLI ──────────────────────────────────────────────────────────────────────
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus-root", default=str(DEFAULT_CORPUS_ROOT), help="Path to the raw/ corpus")
    parser.add_argument("--csv", dest="csv_path", default=str(DEFAULT_CSV), help="Page-family inventory CSV")
    parser.add_argument("--md", dest="md_path", default=str(DEFAULT_MD), help="Markdown report output path")
    parser.add_argument("--json", dest="json_path", default=str(DEFAULT_JSON), help="JSON report output path")
    parser.add_argument("--no-write", action="store_true", help="Print the summary only; write no files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus_root = Path(args.corpus_root)
    if not corpus_root.is_dir():
        print(f"Corpus root not found: {corpus_root} (run scripts/raw_download.py first)", file=sys.stderr)
        return 2

    report = build_report(corpus_root, Path(args.csv_path))

    print("=" * 78)
    print("UNSERVED DATA INVENTORY  (raw/ corpus vs ENDPOINTS registry)")
    print("=" * 78)
    for key, value in report["summary"].items():
        print(f"  {key:36} {value}")

    if not args.no_write:
        md_path = Path(args.md_path)
        json_path = Path(args.json_path)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"\nWrote {md_path}")
        print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
