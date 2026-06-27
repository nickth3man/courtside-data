import type { DatasetCatalogEntry, PlayerHubTab } from "@/features/player-hub/types";

export const fallbackTabs: PlayerHubTab[] = [
  { id: "overview", label: "Overview", description: "Overview", scope: "player", datasets: ["career"], default_dataset: "career" },
  { id: "career", label: "Career", description: "Career", scope: "player", datasets: ["career"], default_dataset: "career" },
  {
    id: "playoffs",
    label: "Playoffs",
    description: "Playoffs",
    scope: "player",
    datasets: ["playoff-series", "playoff-games"],
    default_dataset: "playoff-series",
  },
  {
    id: "shooting",
    label: "Shooting",
    description: "Shooting",
    scope: "player",
    datasets: ["adjusted-shooting", "shooting-breakdown"],
    default_dataset: "adjusted-shooting",
  },
  { id: "splits", label: "Splits", description: "Splits", scope: "season", datasets: ["splits"], default_dataset: "splits" },
  { id: "on-off", label: "On/Off", description: "On/Off", scope: "season", datasets: ["on-off"], default_dataset: "on-off" },
  {
    id: "games",
    label: "Games",
    description: "Games",
    scope: "season",
    datasets: ["regular-games", "playoff-games"],
    default_dataset: "regular-games",
  },
  {
    id: "more",
    label: "More",
    description: "More",
    scope: "player",
    datasets: ["game-highs", "all-star", "salaries", "similarity", "derived-play-by-play"],
    default_dataset: "game-highs",
  },
];

export function datasetLabel(datasets: DatasetCatalogEntry[] | undefined, dataset: string): string {
  return datasets?.find((entry) => entry.id === dataset)?.label ?? dataset.replaceAll("-", " ");
}

export function datasetScope(datasets: DatasetCatalogEntry[] | undefined, dataset: string): "player" | "season" | undefined {
  return datasets?.find((entry) => entry.id === dataset)?.scope;
}
