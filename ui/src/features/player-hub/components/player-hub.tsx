"use client";

import { ArrowLeft, RefreshCcw } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { Button } from "@/components/button";
import { QueryBoundary } from "@/components/query-boundary";
import { StatusPill } from "@/components/status-pill";
import { useCatalog, usePlayerSummary } from "@/features/player-hub/api/queries";
import { DatasetPanel } from "@/features/player-hub/components/dataset-panel";
import { Overview } from "@/features/player-hub/components/overview";
import { PlayerSearch } from "@/features/player-hub/components/player-search";
import type { DatasetCatalogEntry, PlayerHubTab } from "@/features/player-hub/types";
import { fallbackTabs } from "@/features/player-hub/utils/catalog";
import { formatValue } from "@/features/player-hub/utils/format";
import { seasonLabel } from "@/features/player-hub/utils/season";
import { TypedApiError } from "@/lib/api-errors";
import { useUrlParam } from "@/lib/use-url-param";

interface PlayerHubProps {
  identifier: string;
}

export function PlayerHub({ identifier }: PlayerHubProps) {
  const summaryQuery = usePlayerSummary(identifier);
  const catalogQuery = useCatalog();
  const { get: getParam, set: setParam } = useUrlParam();
  const [includeInactiveGames, setIncludeInactiveGames] = useState(false);

  const tabs = catalogQuery.data?.tabs ?? fallbackTabs;
  const datasetById = useMemo(() => {
    const entries = catalogQuery.data?.datasets ?? [];
    return new Map(entries.map((entry) => [entry.id, entry]));
  }, [catalogQuery.data?.datasets]);

  const activeTab = normalizeTab(getParam("tab"), tabs);
  const seasonFromUrl = Number(getParam("season"));
  const selectedSeason =
    Number.isFinite(seasonFromUrl) && seasonFromUrl > 0 ? seasonFromUrl : summaryQuery.data?.default_season ?? null;
  const currentTab = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  // Route-boundary integration: let `invalid_player` / `missing_fixture` trigger
  // not-found.tsx, and let every other TypedApiError trigger error.tsx — instead
  // of QueryBoundary collapsing them into an inline "Player unavailable" EmptyState.
  //
  // `notFound()` throws a special sentinel that Next.js catches and maps to the
  // nearest `not-found.tsx`; `throw err` escapes this render and is caught by
  // the nearest `error.tsx` (which in this route branches on `err.code`). This
  // block runs after the query settles — while `summaryQuery` is loading, `error`
  // is null, the block is a no-op, and `QueryBoundary` below still renders its
  // loading block as before.
  if (summaryQuery.error) {
    const err = summaryQuery.error;
    if (err instanceof TypedApiError && (err.code === "invalid_player" || err.code === "missing_fixture")) {
      notFound();
    }
    throw err;
  }

  return (
    <Shell>
      <QueryBoundary query={summaryQuery} loadingLabel="Loading player" errorTitle="Player unavailable">
        {(summary) => (
          <>
            <header className="space-y-4 border-b border-court-line bg-white px-4 py-4 sm:px-6 lg:px-8">
              <div className="mx-auto flex max-w-7xl flex-col gap-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div className="min-w-0">
                    <Link href="/players" className="inline-flex items-center gap-2 text-sm text-court-muted hover:text-court-ink">
                      <ArrowLeft className="size-4" aria-hidden="true" />
                      Players
                    </Link>
                    <h1 className="mt-2 truncate text-2xl font-semibold text-court-ink sm:text-3xl">{summary.display_name}</h1>
                    <p className="text-sm text-court-muted">
                      {summary.identifier} · {formatValue(summary.hero_stats.season)} · {formatValue(summary.hero_stats.team)}
                    </p>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                    <PlayerSearch compact />
                    <StatusPill />
                  </div>
                </div>

                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <nav className="flex gap-1 overflow-x-auto pb-1" aria-label="Player Hub tabs">
                    {tabs.map((tab) => (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setParam("tab", tab.id)}
                        data-active={tab.id === activeTab ? "" : undefined}
                        className="h-9 shrink-0 rounded-md px-3 text-sm font-medium text-court-muted transition hover:bg-zinc-100 hover:text-court-ink data-active:bg-court-accent data-active:text-white"
                      >
                        {tab.label}
                      </button>
                    ))}
                  </nav>

                  <div className="flex flex-wrap items-center gap-2">
                    <label className="flex items-center gap-2 text-sm text-court-muted">
                      Season
                      <select
                        value={selectedSeason ?? ""}
                        onChange={(event) => setParam("season", event.target.value)}
                        className="h-9 rounded-md border border-court-line bg-white px-2 text-sm text-court-ink outline-none focus:border-court-accent focus:ring-2 focus:ring-teal-100"
                      >
                        {summary.available_seasons.map((season) => (
                          <option key={season} value={season}>
                            {seasonLabel(season)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="inline-flex h-9 items-center gap-2 rounded-md border border-court-line bg-white px-3 text-sm text-court-muted">
                      <input
                        type="checkbox"
                        checked={includeInactiveGames}
                        onChange={(event) => setIncludeInactiveGames(event.target.checked)}
                      />
                      Inactive
                    </label>
                    <Button size="icon" onClick={() => summaryQuery.refetch()} title="Refresh player">
                      <RefreshCcw className="size-4" aria-hidden="true" />
                      <span className="sr-only">Refresh player</span>
                    </Button>
                  </div>
                </div>
              </div>
            </header>

            <main className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
              {currentTab.id === "overview" ? (
                <Overview summary={summary} />
              ) : (
                <div className="space-y-6">
                  {currentTab.datasets.map((datasetId) => {
                    const dataset = datasetById.get(datasetId) ?? fallbackDataset(datasetId, currentTab);
                    return (
                      <DatasetPanel
                        key={datasetId}
                        identifier={identifier}
                        dataset={dataset}
                        summary={summary}
                        seasonEndYear={selectedSeason}
                        includeInactiveGames={includeInactiveGames}
                      />
                    );
                  })}
                </div>
              )}
            </main>
          </>
        )}
      </QueryBoundary>
    </Shell>
  );
}

function Shell({ children }: Readonly<{ children: ReactNode }>) {
  return <div className="min-h-screen bg-court-paper">{children}</div>;
}

function normalizeTab(value: string | null, tabs: PlayerHubTab[]): string {
  if (value && tabs.some((tab) => tab.id === value)) {
    return value;
  }
  return tabs[0]?.id ?? "overview";
}

function fallbackDataset(datasetId: string, tab: PlayerHubTab): DatasetCatalogEntry {
  return {
    id: datasetId,
    label: datasetId.replaceAll("-", " "),
    endpoint_name: datasetId,
    scope: tab.scope,
    description: tab.description,
    columns: [],
    default_visible_columns: [],
    supports_export: true,
  };
}
