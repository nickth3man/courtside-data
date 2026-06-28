// TODO(team-hub): remove `fallbackTeamTabs` once the backend catalog endpoint
// (`GET /api/endpoints/team-hub`) is confirmed wired and returning real data
// for the fixture set in `tests/test_endpoint_metadata.py`.
//
// What: `fallbackTeamTabs` (lines 8-43 below) and the `TEAM_SEASON_SCOPE_DATASETS`
//   set (lines 45-51) are temporary client-side mirrors of the static catalog
//   the server already publishes. The real catalog endpoint returns
//   `GET /api/endpoints/team-hub` → `{ tabs: TeamHubTab[], datasets: Record<string,
//   TeamDatasetCatalogEntry> }` (note: the API returns a *list* of entries, not
//   a map — the client builds a `Map` in `team-hub.tsx` lines 31-34).
//   The endpoint is defined by `team_hub_catalog()` in
//   `courtside_data/server/team_catalog.py:304` and registered in
//   `courtside_data/server/app.py` (the `team_hub_catalog` route).
// Where:
//   - this file: `fallbackTeamTabs` (lines 8-43), `TEAM_SEASON_SCOPE_DATASETS`
//     (lines 45-51), `teamDatasetScope` (lines 57-59) all go away once the
//     real catalog is the sole source of truth.
//   - consumer: `ui/src/features/team-hub/components/team-hub.tsx:30` currently
//     does `const tabs = catalogQuery.data?.tabs ?? fallbackTeamTabs;` — the
//     `??` fallback disappears and the line becomes `const tabs =
//     catalogQuery.data?.tabs ?? [];` (or an error boundary kicks in).
//   - cross-reference: must stay in sync with the server's
//     `TEAM_TABS` tuple in `courtside_data/server/team_catalog.py:260` and
//     `TEAM_DATASETS` tuple in `courtside_data/server/team_catalog.py:54`
//     — both are the single source of truth for tab and dataset metadata.
//     If the fallback is kept past the migration, it MUST be regenerated
//     from those tuples so the UI never diverges from what the server
//     claims is available.
// How:
//   1. Run the live probe (`uv run python -m courtside_data.debug -e
//      team_hub_catalog` from the repo root) and confirm
//      `/api/endpoints/team-hub` returns a non-empty `tabs` array with the
//      same ids as the fallback (`overview`, `roster`, `season`, `lineups`,
//      `schedule`).
//   2. Update `ui/src/features/team-hub/api/client.ts` so `getCatalog()`
//      is called eagerly on first hub mount (e.g. via `useCatalog()`
//      in `team-hub.tsx:26` — already wired).
//   3. Delete `fallbackTeamTabs` and the `??` fallback at
//      `team-hub.tsx:30`; replace with `catalogQuery.data?.tabs ?? []`
//      and let `QueryBoundary` show a real loading/error state.
//   4. Delete `TEAM_SEASON_SCOPE_DATASETS` and `teamDatasetScope`; the
//      real catalog's `TeamDatasetCatalogEntry.scope` is authoritative.
// Decision needed: should the UI tolerate a *partial* server catalog
//   (e.g. show fallback tabs when the server responds with 200 but
//   `tabs.length === 0`)? Default: no — empty tabs is an error, surface
//   it. This makes the "fallback removed" branch a hard cutover.
// Verify: with the fallback deleted, `uv run pytest tests -n auto` must
//   still pass — the offline fixture suite replays recorded catalog
//   payloads, so removing the in-file fallback should not regress
//   existing tests.
import type {
  TeamDatasetCatalogEntry,
  TeamDatasetScope,
  TeamHubTab,
} from "@/features/team-hub/types";

export const fallbackTeamTabs: TeamHubTab[] = [
  { id: "overview", label: "Overview", description: "Overview", scope: "team", datasets: ["roster"], default_dataset: "roster" },
  { id: "roster", label: "Roster", description: "Roster", scope: "team", datasets: ["roster"], default_dataset: "roster" },
  {
    id: "season",
    label: "Season",
    description: "Season",
    scope: "team_season",
    datasets: ["splits", "and-opponent", "opponent-stats", "misc-four-factors"],
    default_dataset: "splits",
  },
  {
    id: "schedule",
    label: "Schedule",
    description: "Schedule",
    scope: "team_season",
    datasets: ["schedule"],
    default_dataset: "schedule",
  },
  {
    id: "more",
    label: "More",
    description: "More",
    scope: "team",
    datasets: [
      "contracts",
      "transactions",
      "lineups",
      "starting-lineups",
      "on-off",
      "franchise-history",
      "injury-report",
    ],
    default_dataset: "transactions",
  },
];

const TEAM_SEASON_SCOPE_DATASETS = new Set<string>([
  "splits",
  "and-opponent",
  "opponent-stats",
  "misc-four-factors",
  "schedule",
]);

export function teamDatasetLabel(id: string): string {
  return id.replaceAll("-", " ");
}

export function teamDatasetScope(id: string): TeamDatasetScope {
  return TEAM_SEASON_SCOPE_DATASETS.has(id) ? "team_season" : "team";
}

export function lookupTeamDataset(
  datasets: TeamDatasetCatalogEntry[] | undefined,
  id: string,
): TeamDatasetCatalogEntry | undefined {
  return datasets?.find((entry) => entry.id === id);
}
