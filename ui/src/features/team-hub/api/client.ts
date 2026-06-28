// TODO(team-hub): migrate to the shared @/lib/api-client (fix-1 already landed in
// player-hub; mirror the player-hub shim).
//
// What: replace this file's hand-rolled HTTP plumbing with a thin re-export
//   shim over `ui/src/lib/api-client.ts` so every URL the UI hits is built
//   and error-mapped in one place. The shared `apiFetch` already gives us:
//     - 10s request timeout + caller `AbortSignal` linking (lib lines 24-81)
//     - one automatic 429 retry that honors `Retry-After` / `retry_after`
//       (lib lines 121-127)
//     - typed errors via `parseApiError` + `TypedApiError` from
//       `ui/src/lib/api-errors.ts` — no more bare `Error(message)` on
//       non-2xx responses.
// Where:
//   - delete: this file's local `apiFetch` (lines 13-28 of the current
//     87-line module), the local `API_BASE_URL` (line 11), and the local
//     `buildDatasetParams` helper (lines 30-42) — they have direct
//     equivalents in `@/lib/api-client` (see `buildDatasetParams` at
//     lib lines 133-142).
//   - keep / re-export: `csvExportUrl` (lines 44-56 of this file) — see
//     the "Decision needed" block below; the simplest path is to leave
//     the function in place because it builds a team-flavored URL
//     (`/api/teams/{id}/export`) that the lib helper does not yet know
//     about, and *additionally* re-export `csvExportUrl` from
//     `@/lib/api-client` only if downstream callers need the player
//     helper here. Confirm before deleting.
//   - mirror: `ui/src/features/player-hub/api/client.ts` is the canonical
//     49-line shim — its imports (`apiFetch, API_BASE_URL, csvExportUrl`
//     from `@/lib/api-client`) and its re-export pattern are the target.
//     The player shim also renames its functions to player-specific names
//     (`getPlayerDataset`, `searchPlayers`); the team shim should do the
//     same (`getTeamDataset`, `searchTeams`).
// How:
//   1. Add imports:
//        import { apiFetch, API_BASE_URL, csvExportUrl } from "@/lib/api-client";
//        import { TypedApiError } from "@/lib/api-errors";
//      (drop the `ApiErrorEnvelope` type import — `parseApiError` now
//      owns that shape; only `StatusResponse` etc. stay as type imports
//      from `@/features/team-hub/types`.)
//   2. Delete the local `apiFetch` (lines 13-28) and `API_BASE_URL`
//      (line 11). Rewrite each `get*` export as a one-liner that calls
//      `apiFetch<...>(path)`, matching player-hub lines 21-48.
//   3. Re-export `API_BASE_URL` so existing imports
//      (`@/features/team-hub/api/client` consumers reading
//      `API_BASE_URL` directly) keep working, exactly as player-hub
//      line 19 does.
//   4. Decide what to do with this file's `csvExportUrl` — see below.
//   5. Drop the now-unused `ApiErrorEnvelope` import (line 3).
// Decision needed: should the team-flavored `csvExportUrl` (this file
//   lines 44-56) move to `@/lib/api-client` as a second exported helper
//   (e.g. `csvExportUrl("BOS", "roster", …)` and the helper picks the
//   right `/api/players|teams/…/export` prefix from a new
//   `entity: "player" | "team"` first arg), or stay a per-feature shim
//   re-exported by team-hub only? Option A centralises all URL
//   construction in lib and matches the spirit of the migration;
//   option B keeps the lib surface smaller and avoids forcing player
//   callers to pass an `entity` discriminator. Default to option B
//   unless a third feature needs the helper.
// Verify: from `ui/`,
//   - `npx tsc --noEmit` (must stay clean — comments only here, no
//     signature changes for the 8 named exports).
//   - `npx eslint .`
//   - `npx vitest run src/features/team-hub` (no test should regress;
//     the existing tests mock the client module, not `apiFetch`).
import type {
  ApiErrorEnvelope,
  EndpointRowsResponse,
  StatusResponse,
  TeamHubCatalog,
  TeamHubSummary,
  TeamSearchResult,
} from "@/features/team-hub/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_COURTSIDE_API_URL ?? "http://127.0.0.1:8765";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as ApiErrorEnvelope;
      message = payload.detail?.message ?? message;
    } catch {
      // Keep the HTTP status message when the body is not JSON.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

function buildDatasetParams(opts: {
  seasonEndYear?: number;
  includeInactiveGames?: boolean;
}): URLSearchParams {
  const params = new URLSearchParams();
  if (opts.seasonEndYear !== undefined) {
    params.set("season_end_year", String(opts.seasonEndYear));
  }
  if (opts.includeInactiveGames) {
    params.set("include_inactive_games", "true");
  }
  return params;
}

export function csvExportUrl(
  identifier: string,
  dataset: string,
  seasonEndYear?: number,
  includeInactiveGames = false,
): string {
  const params = new URLSearchParams({ dataset });
  const overlay = buildDatasetParams({ seasonEndYear, includeInactiveGames });
  for (const [key, value] of overlay) {
    params.set(key, value);
  }
  return `${API_BASE_URL}/api/teams/${identifier}/export?${params.toString()}`;
}

export function getStatus(): Promise<StatusResponse> {
  return apiFetch<StatusResponse>("/api/status");
}

export function getCatalog(): Promise<TeamHubCatalog> {
  return apiFetch<TeamHubCatalog>("/api/endpoints/team-hub");
}

export function searchTeams(term: string): Promise<TeamSearchResult[]> {
  return apiFetch<TeamSearchResult[]>(`/api/teams/search?term=${encodeURIComponent(term)}`);
}

export function getSummary(identifier: string): Promise<TeamHubSummary> {
  return apiFetch<TeamHubSummary>(`/api/teams/${identifier}/summary`);
}

export function getTeamDataset(identifier: string, dataset: string): Promise<EndpointRowsResponse> {
  return apiFetch<EndpointRowsResponse>(`/api/teams/${identifier}/${dataset}`);
}

export function getSeasonDataset(
  identifier: string,
  seasonEndYear: number,
  dataset: string,
  includeInactiveGames = false,
): Promise<EndpointRowsResponse> {
  const params = buildDatasetParams({ includeInactiveGames });
  const suffix = params.size > 0 ? `?${params.toString()}` : "";
  return apiFetch<EndpointRowsResponse>(`/api/teams/${identifier}/seasons/${seasonEndYear}/${dataset}${suffix}`);
}
