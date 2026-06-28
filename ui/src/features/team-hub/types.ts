// TODO(team-hub): replace these hand-written type mirrors with the
// `openapi-typescript`-generated `components["schemas"][…]` types once
// `npm run gen:api` is run against a live server (see
// `ui/src/lib/openapi-types.ts` for the full migration workflow).
//
// What: every interface and type in this file is a hand-written mirror
//   of a Pydantic model in `courtside_data/server/team_models.py`:
//     - `TransportMode`        ← `courtside_data/server/models.py` (alias for `team_models.py:8`)
//     - `TeamDatasetScope`     ← `team_models.py:11`  (Literal["team", "team_season"])
//     - `ApiError` / `ApiErrorEnvelope` ← kept here for the local `apiFetch` shim; will move to
//                                          `ui/src/lib/api-errors.ts` once the team client migrates
//                                          to `@/lib/api-client` (see the TODO in
//                                          `ui/src/features/team-hub/api/client.ts:1`).
//     - `ColumnMeta`           ← `courtside_data/server/models.py:ColumnMeta` (shared with player-hub)
//     - `TeamSearchResult`     ← `team_models.py:14`
//     - `TeamHubTab`           ← `team_models.py:22`
//     - `TeamDatasetCatalogEntry` ← `team_models.py:33`
//     - `TeamHubCatalog`       ← `team_models.py:50`
//     - `EndpointRowsResponse` ← `courtside_data/server/models.py` (shared with player-hub)
//     - `TeamHubSummary`       ← `team_models.py:62`
//     - `StatusResponse`       ← `courtside_data/server/models.py` (shared with player-hub)
//
//   A key rename on the Pydantic side is silent at compile time today
//   because both sides are untyped dicts at the leaf (`dict[str, Any]`
//   on the server, `Record<string, unknown>` on the client). The codegen
//   path produces a strict structural type per model name and breaks the
//   build on drift.
// Where:
//   - this file: the 12 exported types below — replaced wholesale by
//     `import type { components } from "@/lib/openapi-types";` plus
//     `type TeamHubSummary = components["schemas"]["TeamHubSummary"];`
//     style aliases (see the workflow doc at
//     `ui/src/lib/openapi-types.ts:25-45` for the three-phase migration).
//   - sibling: `ui/src/features/player-hub/types.ts` is the player-hub
//     mirror (also 81 lines) and gets the same treatment.
// How (mirroring the JSDoc in `ui/src/lib/openapi-types.ts:8-46`):
//   1. Run codegen: terminal A `uv run courtside-data serve`, terminal B
//      `npm run gen:api` from `ui/`. This produces a real
//      `components["schemas"]` block keyed by Pydantic model name.
//   2. Phase 1 (additive): leave this file in place, add
//      `// @ts-expect-error codegen mismatch` markers only if `tsc`
//      flags divergences.
//   3. Phase 2 (consumer migration): rewrite one consumer at a time
//      (`api/client.ts`, then `api/queries.ts`, then the components) to
//      read from `components["schemas"][…]`. The team-hub re-export
//      shim (post-migration) should look like:
//        export type {
//          components as TeamSchemas,
//        } from "@/lib/openapi-types";
//      plus `export type TeamHubSummary = TeamSchemas["TeamHubSummary"];`
//      aliases for any consumer that still imports from this file.
//   4. Phase 3: delete the hand-written interfaces and the file
//      becomes a pure re-export shim.
// Decision needed: keep `ApiError` and `ApiErrorEnvelope` here or move
//   to `@/lib/api-errors.ts`? The local `apiFetch` in
//   `ui/src/features/team-hub/api/client.ts:13-28` is the only consumer
//   of these types — once that `apiFetch` is deleted (per the migration
//   TODO in `client.ts:1`) the types are dead. Move them at the same
//   time as the `apiFetch` removal, or leave them as no-op exports for
//   one release.
// Verify: from `ui/`, `npx tsc --noEmit` immediately after codegen
//   (should be clean because no consumer references the generated
//   types yet). After each phase-2 consumer migration, re-run
//   `npx tsc --noEmit && npx eslint . && npx vitest run` — no test
//   should regress.
export type TransportMode = "fixture" | "live";
export type TeamDatasetScope = "team" | "team_season";

export interface ApiError {
  code: string;
  message: string;
  detail: Record<string, unknown>;
}

export interface ApiErrorEnvelope {
  detail: ApiError;
}

export interface ColumnMeta {
  key: string;
  label: string;
  default_visible: boolean;
  numeric: boolean;
}

export interface TeamSearchResult {
  name: string;
  identifier: string;
  leagues: string[];
}

export interface TeamHubTab {
  id: string;
  label: string;
  description: string;
  scope: TeamDatasetScope;
  datasets: string[];
  default_dataset: string;
}

export interface TeamDatasetCatalogEntry {
  id: string;
  label: string;
  endpoint_name: string;
  scope: TeamDatasetScope;
  description: string;
  columns: ColumnMeta[];
  default_visible_columns: string[];
  supports_export: boolean;
}

export interface TeamHubCatalog {
  tabs: TeamHubTab[];
  datasets: TeamDatasetCatalogEntry[];
}

export interface EndpointRowsResponse {
  dataset: string;
  endpoint_name: string;
  params: Record<string, unknown>;
  row_count: number;
  columns: ColumnMeta[];
  default_visible_columns: string[];
  rows: Record<string, unknown>[];
  transport: TransportMode;
}

/**
 * Closed shape of the `hero_stats` dict emitted by
 * `TeamHubService._team_hero_stats` in
 * `courtside_data/server/team_service.py:386-431`. Every consumer in the
 * UI reads from this interface; the server still ships the payload as a
 * `dict[str, Any]` so the UI degrades gracefully (extra/missing keys
 * surface as `undefined` / omitted values, not crashes).
 *
 * Forward-compatible design: the optional metrics (`wins_pyth`, `mov`,
 * `srs`, `off_rtg`, `def_rtg`, `pace`) are typed as `number | null` so
 * an older server that ships only the three base keys
 * (`wins`/`losses`/`win_pct`) still type-checks.
 */
export interface TeamHeroStats {
  season: number | string | null;
  team: string;
  wins: number | null;
  losses: number | null;
  win_pct: number | null;
  wins_pyth?: number | null;
  losses_pyth?: number | null;
  mov?: number | null;
  srs?: number | null;
  off_rtg?: number | null;
  def_rtg?: number | null;
  pace?: number | null;
}

/**
 * One row of the per-season "Franchise Arc" series. Forward-compatible:
 * the server-side `franchise_arc` field is deferred to a separate Python
 * track, so this interface is wired in advance and the UI falls back to
 * the empty state until the server starts emitting it.
 */
export interface FranchiseArcPoint {
  season_end_year: number;
  team_name: string | null;
  wins: number | null;
  losses: number | null;
  win_pct: number | null;
}

export interface TeamHubSummary {
  identifier: string;
  display_name: string;
  leagues: string[];
  default_season: number | null;
  available_seasons: number[];
  hero_stats: TeamHeroStats;
  /** Optional — server hasn't shipped the franchise-arc series yet. */
  franchise_arc?: FranchiseArcPoint[];
  roster: EndpointRowsResponse;
  season_dataset_availability: Record<string, number[]>;
  transport: TransportMode;
}

export interface StatusResponse {
  ok: boolean;
  transport: TransportMode;
  endpoint_count: number;
  fixture_root: string | null;
  fixture_root_exists: boolean | null;
}
