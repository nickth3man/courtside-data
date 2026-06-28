import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { StatusPill } from "@/features/player-hub/components/status-pill";
import { PlayerSearch } from "@/features/player-hub/components/player-search";
import { SAMPLE_ATHLETES } from "@/lib/sample-athletes";

export function SearchPage() {
  return (
    <main className="min-h-screen bg-court-paper">
      <header className="border-b border-court-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-court-accent">Courtside Data</p>
            <h1 className="text-xl font-semibold text-court-ink">Player Hub</h1>
          </div>
          <StatusPill />
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:px-8">
        <section className="space-y-5">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold tracking-normal text-court-ink sm:text-3xl">Find a player</h2>
            <p className="mt-2 text-sm leading-6 text-court-muted">
              Search Basketball Reference player identifiers and open a fixture-backed research workspace.
            </p>
          </div>
          <PlayerSearch />
        </section>

        <aside className="space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-court-muted">Fixture starters</h2>
          <div className="divide-y divide-zinc-100 rounded-md border border-court-line bg-white">
            {SAMPLE_ATHLETES.map((player) => (
              <Link
                key={player.identifier}
                href={`/players/${player.identifier}`}
                className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-zinc-50"
              >
                <span>
                  <span className="block font-medium text-court-ink">{player.name}</span>
                  <span className="text-xs text-court-muted">{player.identifier}</span>
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
