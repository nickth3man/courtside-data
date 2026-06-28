import { useQuery } from "@tanstack/react-query";

import {
  getCatalog,
  getPlayerDataset,
  getSeasonDataset,
  getStatus,
  getSummary,
  searchPlayers,
} from "@/features/player-hub/api/client";
import { queryKeys } from "@/features/player-hub/api/query-keys";

export function useStatus() {
  return useQuery({
    queryKey: queryKeys.status,
    queryFn: getStatus,
  });
}

export function useCatalog() {
  return useQuery({
    queryKey: queryKeys.catalog,
    queryFn: getCatalog,
  });
}

export function usePlayerSearch(term: string) {
  return useQuery({
    queryKey: queryKeys.playerSearch(term),
    queryFn: () => searchPlayers(term),
    enabled: term.trim().length >= 2,
  });
}

export function usePlayerSummary(identifier: string) {
  return useQuery({
    queryKey: queryKeys.playerSummary(identifier),
    queryFn: () => getSummary(identifier),
  });
}

export function usePlayerDataset(identifier: string, dataset: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.playerDataset(identifier, dataset),
    queryFn: () => getPlayerDataset(identifier, dataset),
    enabled,
  });
}

export function useSeasonDataset(
  identifier: string,
  seasonEndYear: number | null,
  dataset: string,
  enabled = true,
  includeInactiveGames = false,
) {
  return useQuery({
    queryKey: queryKeys.seasonDataset(identifier, seasonEndYear, dataset, includeInactiveGames),
    queryFn: () => getSeasonDataset(identifier, seasonEndYear ?? 0, dataset, includeInactiveGames),
    enabled: enabled && seasonEndYear !== null,
  });
}
