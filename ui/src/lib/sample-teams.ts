/**
 * Hand-curated fallback list of featured franchises for the "Featured
 * franchises" sidebar on the teams landing page.
 *
 * Identifiers MUST match the canonical Basketball Reference team
 * abbreviations already used by the rest of the app (e.g. the live API,
 * existing fixtures, and deep links — `/teams/BOS`, `/teams/LAL`, etc.).
 *
 * TODO(lib): drive the sidebar from a backend endpoint so the list can be
 * updated without a UI release. Mirror the migration plan documented in
 * `ui/src/lib/sample-athletes.ts:9-60` — add a `GET /api/teams/featured`
 * endpoint, expose `useFeaturedTeams()` in
 * `ui/src/features/team-hub/api/queries.ts`, and render
 * `data?.teams ?? SAMPLE_TEAMS` so the sidebar never empties.
 *
 * The `blurb?` field is optional so the team sidebar can mirror the
 * player-hub sidebar's data shape. Today this UI renders the blurb (a
 * richer sidebar than the player-hub's, which currently ignores its
 * blurb); asymmetry is acceptable for v1 and can be aligned later.
 */
export interface SampleTeam {
  identifier: string;
  name: string;
  /** Optional blurb shown under the name in the featured sidebar. */
  blurb?: string;
}

export const SAMPLE_TEAMS: readonly SampleTeam[] = [
  { identifier: "LAL", name: "Los Angeles Lakers", blurb: "Tied for most NBA titles" },
  { identifier: "BOS", name: "Boston Celtics", blurb: "Tied for most NBA titles" },
  { identifier: "GSW", name: "Golden State Warriors" },
  { identifier: "CHI", name: "Chicago Bulls" },
  { identifier: "SAS", name: "San Antonio Spurs" },
] as const;
