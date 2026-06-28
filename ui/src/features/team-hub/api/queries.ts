import { useQuery } from "@tanstack/react-query";

import {
  getCatalog,
  getSeasonDataset,
  getStatus,
  getSummary,
  getTeamDataset,
  searchTeams,
} from "@/features/team-hub/api/client";
import { queryKeys } from "@/features/team-hub/api/query-keys";

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

export function useTeamSearch(term: string) {
  return useQuery({
    queryKey: queryKeys.teamSearch(term),
    queryFn: () => searchTeams(term),
    enabled: term.trim().length >= 2,
  });
}

export function useTeamSummary(identifier: string) {
  return useQuery({
    queryKey: queryKeys.teamSummary(identifier),
    queryFn: () => getSummary(identifier),
  });
}

export function useTeamDataset(identifier: string, dataset: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.teamDataset(identifier, dataset),
    queryFn: () => getTeamDataset(identifier, dataset),
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
