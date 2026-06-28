/**
 * Unit tests for the player-hub tab/dataset catalog helpers in
 * `ui/src/features/player-hub/utils/catalog.ts`.
 */
import { describe, expect, it } from "vitest";

import type { DatasetCatalogEntry } from "@/features/player-hub/types";
import { datasetLabel, datasetScope, fallbackTabs } from "@/features/player-hub/utils/catalog";

/** Build a minimal but complete `DatasetCatalogEntry` for test fixtures. */
function makeEntry(id: string, label: string, scope: "player" | "season" = "player"): DatasetCatalogEntry {
  return { id, label, endpoint_name: id, scope, description: label, columns: [], default_visible_columns: [], supports_export: true };
}

describe("fallbackTabs", () => {
  it("is a non-empty array with the expected tab ids", () => {
    expect(Array.isArray(fallbackTabs)).toBe(true);
    expect(fallbackTabs.length).toBeGreaterThan(0);

    const ids = fallbackTabs.map((tab) => tab.id);
    // Sanity-check the canonical tab ids that the player-hub UI relies on.
    for (const expected of ["overview", "career", "playoffs", "shooting", "splits", "on-off", "games", "more"]) {
      expect(ids).toContain(expected);
    }
  });

  it("uses valid scope literals on every tab", () => {
    for (const tab of fallbackTabs) {
      expect(["player", "season"]).toContain(tab.scope);
      expect(tab.datasets.length).toBeGreaterThan(0);
      expect(tab.default_dataset).toBeTruthy();
    }
  });
});

describe("datasetLabel", () => {
  it("returns the catalog label when the dataset id is known", () => {
    const datasets = [makeEntry("career", "Career Totals"), makeEntry("splits", "Season Splits")];
    expect(datasetLabel(datasets, "career")).toBe("Career Totals");
    expect(datasetLabel(datasets, "splits")).toBe("Season Splits");
  });

  it("returns a fallback humanized id when the dataset id is unknown", () => {
    const datasets = [makeEntry("career", "Career Totals")];
    expect(datasetLabel(datasets, "adjusted-shooting")).toBe("adjusted shooting");
  });

  it("returns a fallback humanized id when the catalog is undefined", () => {
    expect(datasetLabel(undefined, "playoff-series")).toBe("playoff series");
  });
});

describe("datasetScope", () => {
  it("returns the catalog scope literal when the dataset id is known", () => {
    const datasets = [makeEntry("career", "Career", "player"), makeEntry("splits", "Splits", "season")];
    expect(datasetScope(datasets, "career")).toBe("player");
    expect(datasetScope(datasets, "splits")).toBe("season");
  });

  it("returns undefined when the dataset id is not in the catalog", () => {
    const datasets = [makeEntry("career", "Career", "player")];
    expect(datasetScope(datasets, "missing")).toBeUndefined();
  });

  it("returns undefined when the catalog is undefined", () => {
    expect(datasetScope(undefined, "anything")).toBeUndefined();
  });
});
