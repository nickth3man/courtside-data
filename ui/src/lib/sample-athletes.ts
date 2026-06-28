/**
 * Hand-curated fallback list of featured players for the "Fixture starters"
 * sidebar on the players landing page.
 *
 * Identifiers MUST match the canonical Basketball Reference player IDs
 * already used by the rest of the app (e.g. the live API, existing
 * fixtures, and deep links).
 *
 * TODO(lib): drive the sidebar from a backend endpoint so the list can be
 * updated without a UI release.
 *
 * What: add a new server route that returns a curated list of featured
 *   athletes, and have the UI fetch it at render time. The current
 *   `SAMPLE_ATHLETES` constant stays as a fallback for offline / error
 *   states, mirroring the `fallbackTabs` pattern in
 *   `ui/src/features/player-hub/utils/catalog.ts`.
 *
 * Proposed endpoint shape:
 *   GET /api/players/featured
 *     → { athletes: FeaturedAthlete[] }
 *   type FeaturedAthlete = {
 *     identifier: string;   // Basketball Reference player id
 *     name: string;         // display name
 *     blurb?: string;       // optional sidebar blurb
 *     leagues: string[];    // e.g. ["NBA"]
 *   }
 *
 * Where:
 *   - add the route in `courtside_data/server/app.py` near the existing
 *     player routes (`/api/players/search`, `/api/players/{id}/summary`).
 *   - add the Pydantic response model in `courtside_data/server/models.py`
 *     (or a new `featured.py` alongside `team_models.py`).
 *   - add a typed `getFeaturedAthletes()` to
 *     `ui/src/features/player-hub/api/client.ts` and a `useFeaturedAthletes`
 *     query to `ui/src/features/player-hub/api/queries.ts`.
 *   - consume from `ui/src/features/player-hub/components/search-page.tsx`
 *     (replacing the `SAMPLE_ATHLETES.map(...)` block).
 *
 * How:
 *   1. Backend: source the list from a curated config (YAML/JSON in the
 *      package) OR a "popular players" heuristic (e.g. players with the
 *      most available seasons in the fixture set, or a static list with
 *      a `popularity_score` column the heuristic re-ranks).
 *   2. UI: add `useFeaturedAthletes()` that calls the new endpoint with
 *      `enabled: true` and `staleTime: 5 * 60_000` (the list changes
 *      rarely). Keep `SAMPLE_ATHLETES` as the `placeholderData` /
 *      error fallback so the sidebar never renders empty.
 *   3. Render: `data?.athletes ?? SAMPLE_ATHLETES` in `search-page.tsx`.
 *
 * Decision needed:
 *   - Per-league (NBA-only today) or multi-league (one list per league,
 *     league selector in the sidebar)?
 *   - Personalized (per-user) or global (same list for everyone)?
 *     The current constant is a single global list, so a global v1 is
 *     the smallest delta.
 *
 * Verify: after wiring, `npm run dev` + navigate to `/players` and
 *   confirm the sidebar still renders the four canonical players
 *   (LeBron, MJ, Curry, Bird) when the endpoint is reachable, and
 *   continues to render them when it returns 500.
 */
export interface SampleAthlete {
  identifier: string;
  name: string;
  /** Optional blurb shown under the name in the featured sidebar. */
  blurb?: string;
}

export const SAMPLE_ATHLETES: readonly SampleAthlete[] = [
  { identifier: "jamesle01", name: "LeBron James", blurb: "All-time scoring leader" },
  { identifier: "jordami01", name: "Michael Jordan" },
  { identifier: "curryst01", name: "Stephen Curry" },
  { identifier: "birdla01", name: "Larry Bird" },
] as const;
