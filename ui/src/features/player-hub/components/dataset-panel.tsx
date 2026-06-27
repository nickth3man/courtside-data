"use client";

import { LoaderCircle } from "lucide-react";

import { csvExportUrl } from "@/features/player-hub/api/client";
import { usePlayerDataset, useSeasonDataset } from "@/features/player-hub/api/queries";
import { DataTable } from "@/features/player-hub/components/data-table";
import { EmptyState } from "@/features/player-hub/components/empty-state";
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
        <PanelHeading dataset={dataset} />
        <EmptyState title="No fixture for this season" detail="Choose another season or switch the API server to live mode." />
      </section>
    );
  }

  if (query.isLoading) {
    return (
      <section className="space-y-3">
        <PanelHeading dataset={dataset} />
        <div className="flex h-40 items-center justify-center rounded-md border border-court-line bg-white text-sm text-court-muted">
          <LoaderCircle className="mr-2 size-4 animate-spin" aria-hidden="true" />
          Loading
        </div>
      </section>
    );
  }

  if (query.isError) {
    return (
      <section className="space-y-3">
        <PanelHeading dataset={dataset} />
        <EmptyState title="Dataset unavailable" detail={query.error.message} />
      </section>
    );
  }

  const response = query.data;
  if (!response || response.rows.length === 0) {
    return (
      <section className="space-y-3">
        <PanelHeading dataset={dataset} />
        <EmptyState title="No rows returned" />
      </section>
    );
  }

  return (
    <section className="space-y-3">
      <PanelHeading dataset={dataset} rowCount={response.row_count} />
      <DataTable
        rows={response.rows}
        columns={response.columns}
        defaultVisibleColumns={response.default_visible_columns}
        exportUrl={csvExportUrl(
          identifier,
          dataset.id,
          dataset.scope === "season" && seasonEndYear !== null ? seasonEndYear : undefined,
          includeInactiveGames,
        )}
      />
    </section>
  );
}

function PanelHeading({ dataset, rowCount }: { dataset: DatasetCatalogEntry; rowCount?: number }) {
  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 className="text-base font-semibold text-court-ink">{dataset.label}</h2>
        <p className="text-sm text-court-muted">{dataset.description}</p>
      </div>
      {rowCount !== undefined ? <span className="text-sm text-court-muted">{rowCount.toLocaleString()} rows</span> : null}
    </div>
  );
}
