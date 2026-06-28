import { ArrowRight } from "lucide-react";
import Link from "next/link";

import { TeamSearch } from "@/features/team-hub/components/team-search";

// TODO(team-hub): make the featured-franchises sidebar data-driven.
//
// What: the `featuredTeams` constant below (lines 8-14) is a hand-curated
//   list of 5 Basketball Reference team identifiers (LAL, BOS, GSW, CHI,
//   SAS) hard-coded in the UI. The same anti-pattern exists in
//   `ui/src/lib/sample-athletes.ts:69-74` for the player-hub sidebar
//   (LeBron / MJ / Curry / Bird) and is already being tracked for the
//   same migration (see the JSDoc TODO in that file).
// Where:
//   - this file, lines 8-14: the `featuredTeams` array.
//   - mirror: `ui/src/lib/sample-athletes.ts` — the player-hub's
//     canonical home for the sidebar list. Create a parallel
//     `ui/src/lib/sample-teams.ts` so both hubs have the same shape.
//   - long-term: drive from a new `GET /api/teams/featured` endpoint
//     that returns `{ teams: FeaturedTeam[] }` (see the proposed shape
//     in `ui/src/lib/sample-athletes.ts:22-26`).
// How:
//   1. Create `ui/src/lib/sample-teams.ts` with:
//        export interface SampleTeam {
//          identifier: string; name: string; blurb?: string;
//        }
//        export const SAMPLE_TEAMS: readonly SampleTeam[] = [
//          { identifier: "LAL", name: "Los Angeles Lakers", blurb: "..." },
//          { identifier: "BOS", name: "Boston Celtics", blurb: "..." },
//          { identifier: "GSW", name: "Golden State Warriors", blurb: "..." },
//          { identifier: "CHI", name: "Chicago Bulls", blurb: "..." },
//          { identifier: "SAS", name: "San Antonio Spurs", blurb: "..." },
//        ] as const;
//   2. Replace the local constant in this file with
//      `import { SAMPLE_TEAMS } from "@/lib/sample-teams";`.
//   3. Once `GET /api/teams/featured` exists, add
//      `useFeaturedTeams()` to `ui/src/features/team-hub/api/queries.ts`
//      (parallel to a future `useFeaturedAthletes()`) and render
//      `data?.teams ?? SAMPLE_TEAMS` so the sidebar never empties.
// Decision needed: blurb or no blurb? The player-hub sidebar
//   (`search-page.tsx`) doesn't render the optional `blurb` field — only
//   the name + identifier. If the team sidebar mirrors that exactly, the
//   `blurb?` field is dead weight; if we want a richer sidebar (e.g.
//   "Most championships all-time"), keep it.
// Verify: `npx tsc --noEmit && npx eslint .` from `ui/` — the move
//   should be a pure constant relocation, no behavior change.
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
          {/* TODO(team-hub): surface the API status pill in this header.
           *
           * What: the player-hub search page renders `<StatusPill />` in
           *   the same right-hand slot — see
           *   `ui/src/features/player-hub/components/search-page.tsx`
           *   (the analogous header). The team-hub deliberately omits
           *   the pill today to avoid coupling team-hub to player-hub's
           *   `useStatus` (the only consumer of `useStatus` is currently
           *   `ui/src/features/player-hub/components/status-pill.tsx:30`).
           *   We need a team-hub-flavored version that calls the local
           *   `useStatus` from `ui/src/features/team-hub/api/queries.ts:13`.
           * Where:
           *   - this file, the JSX comment placeholder (right of the
           *     title block, roughly line 26 after this comment).
           *   - new file: either
           *       (a) `ui/src/features/team-hub/components/status-pill.tsx`
           *           — a near-copy of the player-hub pill that imports
           *           `useStatus` from `@/features/team-hub/api/queries`,
           *           OR
           *       (b) `ui/src/components/status-pill.tsx` — a *shared*
           *           pill that both features import. The status endpoint
           *           is the same `/api/status` regardless of feature, so
           *           option (b) is the DRY answer.
           *   - mirror: `ui/src/features/player-hub/components/status-pill.tsx`
           *     (the full 4-state pill: rate-limit, loading, error/offline,
           *     fixture-root-missing, healthy).
           * How:
           *   1. Preferred path — option (b):
           *        - extract the player pill body verbatim into
           *          `ui/src/components/status-pill.tsx`,
           *        - replace the local `useStatus` import with a shared
           *          `useStatus` that lives in `ui/src/api/use-status.ts`
           *          and calls the `/api/status` endpoint via
           *          `apiFetch` from `@/lib/api-client`,
           *        - update `ui/src/features/player-hub/components/status-pill.tsx`
           *          to re-export the shared pill, and
           *        - add the import in this file (the placeholder slot).
           *   2. If option (b) is rejected, create
           *      `ui/src/features/team-hub/components/status-pill.tsx`
           *      as a copy with the local `useStatus` import.
           * Decision needed: shared component (`ui/src/components/status-pill.tsx`)
           *   vs per-feature copy? Default: shared. The status endpoint
           *   is feature-agnostic, the pill's behavior is identical, and
           *   the player-hub pill already has the rate-limit and
           *   fixture-root-missing branches that team-hub would otherwise
           *   need to clone.
           * Verify: after extraction, both hubs render the same pill
           *   (same four visual states) and `npx vitest run` passes
           *   for both `player-hub/components/status-pill.test.tsx`
           *   and any new `team-hub/components/status-pill.test.tsx`. */}
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
