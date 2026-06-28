// TODO: replace with the real catalog from /api/endpoints/team-hub once fix-1 lands.
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
