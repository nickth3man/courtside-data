export type TransportMode = "fixture" | "live";
export type DatasetScope = "player" | "season";

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

export interface PlayerSearchResult {
  name: string;
  identifier: string;
  leagues: string[];
}

export interface PlayerHubTab {
  id: string;
  label: string;
  description: string;
  scope: DatasetScope;
  datasets: string[];
  default_dataset: string;
}

export interface DatasetCatalogEntry {
  id: string;
  label: string;
  endpoint_name: string;
  scope: DatasetScope;
  description: string;
  columns: ColumnMeta[];
  default_visible_columns: string[];
  supports_export: boolean;
}

export interface PlayerHubCatalog {
  tabs: PlayerHubTab[];
  datasets: DatasetCatalogEntry[];
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

export interface PlayerHubSummary {
  identifier: string;
  display_name: string;
  leagues: string[];
  default_season: number | null;
  available_seasons: number[];
  hero_stats: Record<string, unknown>;
  career: EndpointRowsResponse;
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
