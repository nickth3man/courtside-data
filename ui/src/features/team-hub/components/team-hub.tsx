"use client";

import { ArrowLeft, RefreshCcw } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { Button } from "@/components/button";
import { QueryBoundary } from "@/components/query-boundary";
import { useCatalog, useTeamSummary } from "@/features/team-hub/api/queries";
import { DatasetPanel } from "@/features/team-hub/components/dataset-panel";
import { Overview } from "@/features/team-hub/components/overview";
import { TeamSearch } from "@/features/team-hub/components/team-search";
import type { TeamDatasetCatalogEntry, TeamHubTab } from "@/features/team-hub/types";
import { fallbackTeamTabs, teamDatasetLabel, teamDatasetScope } from "@/features/team-hub/utils/catalog";
import { formatValue } from "@/features/player-hub/utils/format";
import { seasonLabel } from "@/features/player-hub/utils/season";
import { useUrlParam } from "@/lib/use-url-param";

interface TeamHubProps {
  identifier: string;
}

export function TeamHub({ identifier }: TeamHubProps) {
  const summaryQuery = useTeamSummary(identifier);
  const catalogQuery = useCatalog();
  const { get: getParam, set: setParam } = useUrlParam();
  const [includeInactiveGames, setIncludeInactiveGames] = useState(false);

  const tabs = catalogQuery.data?.tabs ?? fallbackTeamTabs;
  const datasetById = useMemo(() => {
    const entries = catalogQuery.data?.datasets ?? [];
    return new Map(entries.map((entry) => [entry.id, entry]));
  }, [catalogQuery.data?.datasets]);

  const activeTab = normalizeTab(getParam("tab"), tabs);
  const seasonFromUrl = Number(getParam("season"));
  const selectedSeason =
    Number.isFinite(seasonFromUrl) && seasonFromUrl > 0 ? seasonFromUrl : summaryQuery.data?.default_season ?? null;
  const currentTab = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  return (
    <Shell>
      <QueryBoundary query={summaryQuery} loadingLabel="Loading team" errorTitle="Team unavailable">
        {(summary) => (
          <>
            <header className="space-y-4 border-b border-court-line bg-white px-4 py-4 sm:px-6 lg:px-8">
              <div className="mx-auto flex max-w-7xl flex-col gap-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <div className="min-w-0">
                    <Link href="/teams" className="inline-flex items-center gap-2 text-sm text-court-muted hover:text-court-ink">
                      <ArrowLeft className="size-4" aria-hidden="true" />
                      Teams
                    </Link>
                    <h1 className="mt-2 truncate text-2xl font-semibold text-court-ink sm:text-3xl">{summary.display_name}</h1>
                    <p className="text-sm text-court-muted">
                      {summary.identifier} · {summary.leagues.join("/")} · {formatValue(summary.hero_stats.conference)}
                    </p>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                    {/* TODO(team-hub): surface the API status pill in the team-hub
                     * header (the slot is the right-hand side of the title row,
                     * roughly line 62 in the current file).
                     *
                     * Cross-reference: the same TODO exists at
                     *   `ui/src/features/team-hub/components/search-page.tsx`
                     *   line ~26 (the team-hub search-page header). That comment
                     *   has the full expansion — the "Decision needed" block
                     *   there documents the shared `ui/src/components/status-pill.tsx`
                     *   vs per-feature copy trade-off. This file's pill would
                     *   sit to the right of `<TeamSearch compact />` so the
                     *   transport mode is visible while a user browses tabs.
                     *
                     * Once the shared extraction lands (or the per-feature copy
                     * is created), the JSX to drop in is:
                     *     <StatusPill />
                     * imported from `@/components/status-pill` (preferred) or
                     * `@/features/team-hub/components/status-pill`. */}
                    <TeamSearch compact />
                  </div>
                </div>

                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                  <nav className="flex gap-1 overflow-x-auto pb-1" aria-label="Team Hub tabs">
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
                    <Button size="icon" onClick={() => summaryQuery.refetch()} title="Refresh team">
                      <RefreshCcw className="size-4" aria-hidden="true" />
                      <span className="sr-only">Refresh team</span>
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

function normalizeTab(value: string | null, tabs: TeamHubTab[]): string {
  if (value && tabs.some((tab) => tab.id === value)) {
    return value;
  }
  return tabs[0]?.id ?? "overview";
}

function fallbackDataset(datasetId: string, tab: TeamHubTab): TeamDatasetCatalogEntry {
  return {
    id: datasetId,
    label: teamDatasetLabel(datasetId),
    endpoint_name: datasetId,
    scope: teamDatasetScope(datasetId) ?? tab.scope,
    description: tab.description,
    columns: [],
    default_visible_columns: [],
    supports_export: true,
  };
}
