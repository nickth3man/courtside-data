"use client";

import { QueryBoundary } from "@/components/query-boundary";
import { SectionHeading } from "@/components/section-heading";
import { csvExportUrl } from "@/features/player-hub/api/client";
import { usePlayerDataset, useSeasonDataset } from "@/features/player-hub/api/queries";
import { DataTable } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import type { DatasetCatalogEntry, PlayerHubSummary } from "@/features/player-hub/types";

interface DatasetPanelProps {
  identifier: string;
  dataset: DatasetCatalogEntry;
  summary: PlayerHubSummary;
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
    dataset.scope === "player" || summary.transport === "live" || (seasonEndYear !== null && availableSeasons.includes(seasonEndYear));
  const playerQuery = usePlayerDataset(identifier, dataset.id, dataset.scope === "player");
  const seasonQuery = useSeasonDataset(
    identifier,
    seasonEndYear,
    dataset.id,
    dataset.scope === "season" && seasonAvailable,
    includeInactiveGames,
  );
  const query = dataset.scope === "player" ? playerQuery : seasonQuery;

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
              dataset.scope === "season" && seasonEndYear !== null ? seasonEndYear : undefined,
              includeInactiveGames,
            )}
          />
        )}
      </QueryBoundary>
    </section>
  );
}
