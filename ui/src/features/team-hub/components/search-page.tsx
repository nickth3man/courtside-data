import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { TeamSearch } from "@/features/team-hub/components/team-search";

// TODO: make data-driven once /api/teams/featured or a similar endpoint exists.
const featuredTeams = [
  { name: "Los Angeles Lakers", identifier: "LAL" },
  { name: "Boston Celtics", identifier: "BOS" },
  { name: "Golden State Warriors", identifier: "GSW" },
  { name: "Chicago Bulls", identifier: "CHI" },
  { name: "San Antonio Spurs", identifier: "SAS" },
];

export function SearchPage() {
  return (
    <main className="min-h-screen bg-court-paper">
      <header className="border-b border-court-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-court-accent">Courtside Data</p>
            <h1 className="text-xl font-semibold text-court-ink">Team Hub</h1>
          </div>
          {/* TODO: add a team-hub-native status pill once ui/src/features/team-hub/components/status-pill.tsx exists. */}
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:px-8">
        <section className="space-y-5">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold tracking-normal text-court-ink sm:text-3xl">Find a team</h2>
            <p className="mt-2 text-sm leading-6 text-court-muted">
              Search Basketball Reference team identifiers and open a fixture-backed franchise workspace.
            </p>
          </div>
          <TeamSearch />
        </section>

        <aside className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-court-muted">Featured franchises</h2>
          <div className="divide-y divide-zinc-100 rounded-md border border-court-line bg-white">
            {featuredTeams.map((team) => (
              <Link
                key={team.identifier}
                href={`/teams/${team.identifier}`}
                className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-zinc-50"
              >
                <span>
                  <span className="block font-medium text-court-ink">{team.name}</span>
                  <span className="text-xs text-court-muted">{team.identifier}</span>
                </span>
                <ArrowRight className="size-4 shrink-0 text-court-muted" aria-hidden="true" />
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </main>
  );
}
