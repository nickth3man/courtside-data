import { useQuery } from "@tanstack/react-query";

import {
  getCatalog,
  getPlayerDataset,
  getSeasonDataset,
  getStatus,
  getSummary,
  searchPlayers,
} from "@/features/player-hub/api/client";

export function useStatus() {
  return useQuery({
    queryKey: ["status"],
    queryFn: getStatus,
  });
}

export function useCatalog() {
  return useQuery({
    queryKey: ["player-hub-catalog"],
    queryFn: getCatalog,
  });
}

export function usePlayerSearch(term: string) {
  return useQuery({
    queryKey: ["player-search", term],
    queryFn: () => searchPlayers(term),
    enabled: term.trim().length >= 2,
  });
}

export function usePlayerSummary(identifier: string) {
  return useQuery({
    queryKey: ["player-summary", identifier],
    queryFn: () => getSummary(identifier),
  });
}

export function usePlayerDataset(identifier: string, dataset: string, enabled = true) {
  return useQuery({
    queryKey: ["player-dataset", identifier, dataset],
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
    queryKey: ["season-dataset", identifier, seasonEndYear, dataset, includeInactiveGames],
    queryFn: () => getSeasonDataset(identifier, seasonEndYear ?? 0, dataset, includeInactiveGames),
    enabled: enabled && seasonEndYear !== null,
  });
}
