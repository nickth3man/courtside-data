import { Suspense } from "react";

import { TeamHub } from "@/features/team-hub/components/team-hub";

interface TeamPageProps {
  params: Promise<{ identifier: string }>;
}

// TODO(team-hub): this dynamic route is missing the three Next.js
// route-segment files that the player-hub equivalent has
// (`ui/src/app/players/[identifier]/`, added in fix-4). The team route
// is the only dynamic segment in the app without them, so it gets
// Next.js's default loading skeleton (none) and a generic error page on
// any thrown `TypedApiError` — which loses the rate-limit, invalid-team,
// and missing-fixture UX that `players/[identifier]/error.tsx` provides.
//
// What: create three new files at `ui/src/app/teams/[identifier]/`
//   next to this `page.tsx`. Each is a sibling route segment that
//   Next.js auto-wraps around `page.tsx`.
// Where (files to create):
//   - `ui/src/app/teams/[identifier]/loading.tsx` — server component,
//     renders a `<LoadingBlock label="Loading team…" minHeight="h-64" />`
//     from `@/components/loading-block`. Mirror:
//     `ui/src/app/players/[identifier]/loading.tsx` (18 lines).
//   - `ui/src/app/teams/[identifier]/error.tsx` — client component
//     (`"use client";`) — must be a client component because Next.js
//     requires it for `error.tsx` route segments. Branches on the
//     `TypedApiError.code` from `ui/src/lib/api-errors.ts:42`. The team
//     server raises `invalid_team` and `missing_fixture` codes that
//     don't exist in the player error boundary — see "Decision needed"
//     below. Mirror: `ui/src/app/players/[identifier]/error.tsx` (145
//     lines).
//   - `ui/src/app/teams/[identifier]/not-found.tsx` — server component.
//     Triggered by `notFound()` or an unknown team identifier. Mirror:
//     `ui/src/app/players/[identifier]/not-found.tsx` (31 lines), but
//     with the back-link pointing to `/teams` (not `/players`).
// How:
//   1. Copy `ui/src/app/players/[identifier]/loading.tsx` verbatim to
//      `ui/src/app/teams/[identifier]/loading.tsx`; change the label
//      to "Loading team…".
//   2. Copy `ui/src/app/players/[identifier]/error.tsx` to the team
//      path; rename the component (`PlayerError` → `TeamError`), swap
//      the `EmptyState` import from
//      `@/features/player-hub/components/empty-state` to the shared
//      `@/components/empty-state` (after the extraction in
//      `ui/src/features/team-hub/components/dataset-panel.tsx:7` lands),
//      and change the `invalid_player` branch to `invalid_team` (see
//      "Decision needed" below).
//   3. Copy `ui/src/app/players/[identifier]/not-found.tsx` to the
//      team path; change the back-link `href` from `/players` to
//      `/teams` and the title copy from "Player not found" to
//      "Team not found".
// Decision needed: what `TypedApiError.code` does the server raise
//   for an unknown / missing-fixture team?
//   - The player code set is defined in
//     `ui/src/lib/api-errors.ts:8-16` (`invalid_player`, `invalid_season`,
//     `missing_fixture`, …). The team server in
//     `courtside_data/server/team_service.py` raises
//     `MissingFixtureError` from
//     `courtside_data/server/team_service.py:404` and the route layer
//     in `courtside_data/server/app.py` likely maps it to one of the
//     existing codes (the team's search at `team_service.py:455` raises
//     `NotImplementedError`, surfaced as `internal_error`).
//   - If a new `invalid_team` code is needed, it must be added to
//     `ui/src/lib/api-errors.ts:18-27` (the `KNOWN_CODES` set) and
//     the `ApiErrorCode` union at line 8, AND to the server-side
//     `courtside_data.server.app._map_exception` mapping.
//   - Until that lands, fall back to the generic
//     `ErrorCard title="Something went wrong" detail={error.message}`
//     branch and surface the server-supplied message verbatim.
// Verify: after the three files exist, `npx tsc --noEmit && npx eslint .`
//   from `ui/`. Add a vitest snapshot of the new `TeamError` mirroring
//   the player one if and when the test surface for route segments is
//   wired up (today the player error boundary is tested by hand; the
//   task is to mirror the files, not the tests).
export default async function TeamPage({ params }: TeamPageProps) {
  const { identifier } = await params;
  return (
    <Suspense fallback={<div className="min-h-screen bg-court-paper p-6 text-sm text-court-muted">Loading team</div>}>
      <TeamHub identifier={identifier} />
    </Suspense>
  );
}
