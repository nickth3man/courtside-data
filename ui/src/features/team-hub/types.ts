import type { components } from "@/lib/openapi-types";

export type TransportMode = components["schemas"]["TeamHubSummary"]["transport"];
export type TeamDatasetScope = components["schemas"]["TeamHubTab"]["scope"];
export type ColumnMeta = components["schemas"]["ColumnMeta"];
export type TeamSearchResult = components["schemas"]["TeamSearchResult"] & {
  leagues: string[];
};
export type TeamHubTab = components["schemas"]["TeamHubTab"];
export type TeamDatasetCatalogEntry = components["schemas"]["TeamDatasetCatalogEntry"];
export type TeamHubCatalog = components["schemas"]["TeamHubCatalog"];
export type EndpointRowsResponse = components["schemas"]["EndpointRowsResponse"];
export type StatusResponse = components["schemas"]["StatusResponse"];
export type FranchiseArcPoint = components["schemas"]["FranchiseArcPoint"];

type GeneratedTeamHeroStats = components["schemas"]["TeamHeroStats"];
type GeneratedTeamHubSummary = components["schemas"]["TeamHubSummary"];

export type TeamHeroStats = GeneratedTeamHeroStats & {
  season: GeneratedTeamHeroStats["season"] | null;
  wins: number | null;
  losses: number | null;
  win_pct: number | null;
};

export type TeamHubSummary = Omit<
  GeneratedTeamHubSummary,
  "available_seasons" | "hero_stats" | "leagues" | "season_dataset_availability"
> & {
  leagues: string[];
  available_seasons: number[];
  hero_stats: TeamHeroStats;
  season_dataset_availability: Record<string, number[]>;
};
