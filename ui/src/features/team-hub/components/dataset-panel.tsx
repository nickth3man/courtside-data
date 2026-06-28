"use client";

import { QueryBoundary } from "@/components/query-boundary";
import { SectionHeading } from "@/components/section-heading";
import { csvExportUrl } from "@/features/team-hub/api/client";
import { useSeasonDataset, useTeamDataset } from "@/features/team-hub/api/queries";
// TODO(team-hub): extract `DataTable` and `EmptyState` to `ui/src/components/`
// so team-hub and player-hub can share them (both are feature-agnostic).
//
// What: two components currently live under
//   `ui/src/features/player-hub/components/` but are imported by team-hub:
//     - `DataTable` (178 lines, sortable + filterable + paginated +
//       column-toggleable + CSV export; depends only on
//       `ColumnMeta` and `formatValue`).
//     - `EmptyState` (19 lines, dashed-border card with title +
//       optional detail).
//   Both are pure UI primitives with no player-hub-specific behavior —
//   they belong in `ui/src/components/` next to `Button`,
//   `LoadingBlock`, `QueryBoundary`, and `SectionHeading`.
// Where:
//   - source: `ui/src/features/player-hub/components/data-table.tsx` (move)
//   - source: `ui/src/features/player-hub/components/data-table.test.tsx` (move)
//   - source: `ui/src/features/player-hub/components/empty-state.tsx` (move)
//   - source: `ui/src/features/player-hub/components/empty-state.test.tsx` (move)
//   - target: `ui/src/components/data-table.tsx` (+ `.test.tsx`)
//             `ui/src/components/empty-state.tsx` (+ `.test.tsx`)
//   - import sites to update (`grep player-hub/components/data-table` and
//     `grep player-hub/components/empty-state` from repo root):
//       - `ui/src/features/team-hub/components/overview.tsx:9`        (DataTable)
//       - `ui/src/features/team-hub/components/dataset-panel.tsx:8-9` (DataTable + EmptyState)
//       - `ui/src/features/player-hub/components/dataset-panel.tsx:7-8` (DataTable + EmptyState)
//       - `ui/src/features/player-hub/components/overview.tsx:8`      (DataTable)
//       - `ui/src/features/player-hub/components/data-table.test.tsx:4` (DataTable self-ref)
//       - `ui/src/features/player-hub/components/empty-state.test.tsx:12` (EmptyState self-ref)
//       - `ui/src/components/query-boundary.tsx:6` (EmptyState)
//       - `ui/src/app/players/error.tsx:6` (EmptyState)
//       - `ui/src/app/players/not-found.tsx:3` (EmptyState)
//       - `ui/src/app/players/[identifier]/error.tsx:7` (EmptyState)
//       - `ui/src/app/players/[identifier]/not-found.tsx:3` (EmptyState)
//     All eleven should switch to `@/components/data-table` /
//     `@/components/empty-state`.
// How:
//   1. `git mv` both `.tsx` files and their `.test.tsx` counterparts
//      from `features/player-hub/components/` to `ui/src/components/`.
//   2. In the moved `DataTable.tsx`, swap the
//      `import type { ColumnMeta } from "@/features/player-hub/types";`
//      to import from the hoisted location — see
//      `ui/src/features/team-hub/components/overview.tsx` for the
//      matching TODO proposing `ui/src/lib/column-meta.ts`.
//   3. Update all eleven import sites listed above. The player-hub
//      `dataset-panel.tsx` and `overview.tsx` switch too — this is a
//      full cross-feature extraction, not a copy.
// Decision needed: do `DataTable` and `EmptyState` move in the same PR
//   or separate? Default: same PR — they're imported together in this
//   file (lines 8-9) and the test suite's import-graph cycles only
//   resolve once both paths are updated together.
// Verify: from `ui/`, after the move, run
//   `npx tsc --noEmit && npx eslint . && npx vitest run`.
//   All 11 import sites must still resolve; the two `DataTable.test.tsx`
//   and `EmptyState.test.tsx` suites must pass at their new paths.
import { DataTable } from "@/features/player-hub/components/data-table";
import { EmptyState } from "@/features/player-hub/components/empty-state";
import type { TeamDatasetCatalogEntry, TeamHubSummary } from "@/features/team-hub/types";

interface DatasetPanelProps {
  identifier: string;
  dataset: TeamDatasetCatalogEntry;
  summary: TeamHubSummary;
  seasonEndYear: number | null;
  includeInactiveGames?: boolean;
}

export function DatasetPanel({
  identifier,
  dataset,
  summary,
  seasonEndYear,
  includeInactiveGames = false,
}: DatasetPanelProps) {
  const availableSeasons = summary.season_dataset_availability[dataset.id] ?? [];
  const seasonAvailable =
    dataset.scope === "team" ||
    summary.transport === "live" ||
    (seasonEndYear !== null && availableSeasons.includes(seasonEndYear));
  const teamQuery = useTeamDataset(identifier, dataset.id, dataset.scope === "team");
  const seasonQuery = useSeasonDataset(
    identifier,
    seasonEndYear,
    dataset.id,
    dataset.scope === "team_season" && seasonAvailable,
    includeInactiveGames,
  );
  const query = dataset.scope === "team" ? teamQuery : seasonQuery;

  if (!seasonAvailable) {
    return (
      <section className="space-y-3">
        <SectionHeading title={dataset.label} description={dataset.description} />
        <EmptyState title="No fixture for this season" detail="Choose another season or switch the API server to live mode." />
      </section>
    );
  }

  return (
    <section className="space-y-3">
      <SectionHeading
        title={dataset.label}
        description={dataset.description}
        trailing={
          query.data?.row_count !== undefined ? (
            <span className="text-sm text-court-muted">{query.data.row_count.toLocaleString()} rows</span>
          ) : undefined
        }
      />
      <QueryBoundary
        query={query}
        loadingLabel="Loading"
        errorTitle="Dataset unavailable"
        emptyTitle="No rows returned"
        isEmpty={(data) => data.rows.length === 0}
      >
        {(data) => (
          <DataTable
            rows={data.rows}
            columns={data.columns}
            defaultVisibleColumns={data.default_visible_columns}
            exportUrl={csvExportUrl(
              identifier,
              dataset.id,
              dataset.scope === "team_season" && seasonEndYear !== null ? seasonEndYear : undefined,
              includeInactiveGames,
            )}
          />
        )}
      </QueryBoundary>
    </section>
  );
}
