"use client";

import { QueryBoundary } from "@/components/query-boundary";
import { SectionHeading } from "@/components/section-heading";
import { csvExportUrl } from "@/features/team-hub/api/client";
import { useSeasonDataset, useTeamDataset } from "@/features/team-hub/api/queries";
// TODO: extract DataTable + EmptyState to @/components so team-hub and player-hub can share them.
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
