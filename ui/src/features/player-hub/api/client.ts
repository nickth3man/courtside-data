import type {
  ApiErrorEnvelope,
  EndpointRowsResponse,
  PlayerHubCatalog,
  PlayerHubSummary,
  PlayerSearchResult,
  StatusResponse,
} from "@/features/player-hub/types";

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
  return `${API_BASE_URL}/api/players/${identifier}/export?${params.toString()}`;
}

export function getStatus(): Promise<StatusResponse> {
  return apiFetch<StatusResponse>("/api/status");
}

export function getCatalog(): Promise<PlayerHubCatalog> {
  return apiFetch<PlayerHubCatalog>("/api/endpoints/player-hub");
}

export function searchPlayers(term: string): Promise<PlayerSearchResult[]> {
  return apiFetch<PlayerSearchResult[]>(`/api/players/search?term=${encodeURIComponent(term)}`);
}

export function getSummary(identifier: string): Promise<PlayerHubSummary> {
  return apiFetch<PlayerHubSummary>(`/api/players/${identifier}/summary`);
}

export function getPlayerDataset(identifier: string, dataset: string): Promise<EndpointRowsResponse> {
  return apiFetch<EndpointRowsResponse>(`/api/players/${identifier}/${dataset}`);
}

export function getSeasonDataset(
  identifier: string,
  seasonEndYear: number,
  dataset: string,
  includeInactiveGames = false,
): Promise<EndpointRowsResponse> {
  const params = buildDatasetParams({ includeInactiveGames });
  const suffix = params.size > 0 ? `?${params.toString()}` : "";
  return apiFetch<EndpointRowsResponse>(`/api/players/${identifier}/seasons/${seasonEndYear}/${dataset}${suffix}`);
}
