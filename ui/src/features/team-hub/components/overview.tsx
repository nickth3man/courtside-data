"use client";

import { Activity, Shield, Target } from "lucide-react";
import type { ReactNode } from "react";

import { SectionHeading } from "@/components/section-heading";
// TODO(team-hub): migrate the `DataTable` import from player-hub to
// `@/components/data-table.tsx` once the cross-feature extraction lands.
//
// What: the shared `DataTable` component (sortable, filterable, paginated,
//   column-toggleable) lives in `ui/src/features/player-hub/components/data-table.tsx`
//   (178 lines, used by both hubs today). It is feature-agnostic — it takes
//   `rows: Record<string, unknown>[]` and `columns: ColumnMeta[]` and has
//   no player-specific behavior — so it should live next to the other
//   shared primitives in `ui/src/components/`.
// Where:
//   - source: `ui/src/features/player-hub/components/data-table.tsx` (move)
//   - source: `ui/src/features/player-hub/components/data-table.test.tsx`
//     (move alongside the component)
//   - target: `ui/src/components/data-table.tsx` and
//     `ui/src/components/data-table.test.tsx`
//   - import sites to update (grep `player-hub/components/data-table`):
//       - this file, line ~9 (the import below)
//       - `ui/src/features/team-hub/components/dataset-panel.tsx:7`
//       - `ui/src/features/player-hub/components/dataset-panel.tsx:7`
//       - `ui/src/features/player-hub/components/overview.tsx:8`
//       - `ui/src/features/player-hub/components/data-table.test.tsx:4`
//     All five should switch to `@/components/data-table`.
// How:
//   1. `git mv ui/src/features/player-hub/components/data-table.tsx
//         ui/src/components/data-table.tsx`
//   2. `git mv ui/src/features/player-hub/components/data-table.test.tsx
//         ui/src/components/data-table.test.tsx`
//   3. In the moved file, change the `ColumnMeta` import from
//      `@/features/player-hub/types` to either (a) a re-export from
//      `@/features/team-hub/types` (which also defines `ColumnMeta`,
//      identical shape — see `types.ts:14-19`) or (b) hoist `ColumnMeta`
//      to `ui/src/lib/column-meta.ts` and have both feature types re-export
//      it. Default to (b) — keeps `types.ts` mirror of Pydantic clean.
//   4. Update all five import sites listed above.
// Decision needed: see the cross-component TODO in
//   `ui/src/features/team-hub/components/dataset-panel.tsx:7` — bundle the
//   `DataTable` and `EmptyState` extraction into a single PR so neither
//   feature imports from the other.
// Verify: from `ui/`, `npx tsc --noEmit && npx eslint .` and
//   `npx vitest run` — all five consumers of `DataTable` should still
//   render their existing fixtures with the new path.
import { DataTable } from "@/features/player-hub/components/data-table";
import type { TeamHubSummary } from "@/features/team-hub/types";
import { formatStat } from "@/features/player-hub/utils/format";

interface OverviewProps {
  summary: TeamHubSummary;
}

export function Overview({ summary }: OverviewProps) {
  // TODO(team-hub): the `hero_stats` keys consumed here (`wins`, `losses`,
  // `win_pct`) MUST match the keys produced by `TeamHubService._team_hero_stats`
  // in `courtside_data/server/team_service.py:386-431`.
  //
  // What: this block reads `summary.hero_stats.wins` / `.losses` / `.win_pct`
  //   as if they were a typed shape, but `TeamHubSummary.hero_stats` is
  //   declared `Record<string, unknown>` in `ui/src/features/team-hub/types.ts:69`
  //   (and the backend Pydantic mirror is `dict[str, Any]` in
  //   `courtside_data/server/team_models.py:76`). A key rename server-side
  //   is therefore silent at compile time — only the runtime
  //   `formatStat(…)` coercion surfaces a wrong value, and even then it
  //   silently renders "—" because `formatValue` returns the em-dash for
  //   `undefined`.
  // Where:
  //   - this file, lines ~22-28: the three `Metric` invocations.
  //   - source of truth: `courtside_data/server/team_service.py:386-431`
  //     (function `_team_hero_stats`). Confirmed keys: `season`, `team`,
  //     `wins`, `losses`, `win_pct`, `wins_pyth`, `losses_pyth`, `mov`,
  //     `srs`, `off_rtg`, `def_rtg`, `pace`. The UI today uses only the
  //     first three; the rest are fair game for the chart placeholder
  //     (see TODO below).
  // How:
  //   1. Replace `formatStat(summary.hero_stats.wins)` with
  //      `formatStat(asNumber(summary.hero_stats.wins))` (helper lives in
  //      `ui/src/features/player-hub/utils/format.ts:25-34`) so a server-
  //      supplied string like `"42"` is coerced to `42` and an absent key
  //      renders "—".
  //   2. Add a defensive `Number.isFinite(...)` check before
  //      `formatStat(..., "%")` for `win_pct` so a backend bug that ships
  //      a non-finite ratio cannot crash the cell.
  // Decision needed: tighten the type? Options:
  //   (a) Keep `hero_stats: Record<string, unknown>` and rely on runtime
  //       coercion via `asNumber()` — the current contract, low churn.
  //   (b) Narrow to `hero_stats: { wins?: number; losses?: number;
  //       win_pct?: number; mov?: number; srs?: number; off_rtg?: number;
  //       def_rtg?: number; pace?: number }` — the full set returned by
  //       `_team_hero_stats`. Catches renames at compile time, but every
  //       new server key needs a TS update.
  //   Recommended: (b) — the server is the only producer of these keys,
  //   the key set is closed, and the type lives next to the consumer that
  //   reads it.
  // Verify: in `ui/`, after the type change (b), `npx tsc --noEmit` will
  //   fail loudly if the backend renames a key. With (a) the only safety
  //   net is the `npx vitest run` suite, which mocks the summary payload.
  return (
    <div className="space-y-5">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric icon={<Target className="size-4" />} label="Wins" value={formatStat(summary.hero_stats.wins)} />
        <Metric icon={<Shield className="size-4" />} label="Losses" value={formatStat(summary.hero_stats.losses)} />
        <Metric
          icon={<Activity className="size-4" />}
          label="Win %"
          value={formatStat(summary.hero_stats.win_pct, "%")}
        />
      </div>

      <section className="space-y-3">
        <SectionHeading
          title="Franchise Arc"
          description="Season-by-season trends for this franchise."
        />
        {/* TODO(team-hub): render the "Franchise Arc" line chart.
         *
         * What: replace the dashed-border placeholder div below with a
         *   `<ResponsiveContainer>`-wrapped `<LineChart>` from recharts.
         *   The X-axis is `season` (use `summary.available_seasons` as
         *   the canonical season list — see `types.ts:68`); the Y-axis
         *   is a team metric. The natural first metric is `wins` (range
         *   0–82, integer-friendly) or `win_pct` (range 0–1, easy to
         *   label with a `%` suffix via a custom `Tooltip`).
         * Where:
         *   - this file, lines ~37-40 (the placeholder div).
         *   - mirror: `ui/src/features/player-hub/components/overview.tsx:42-55`
         *     (the career-arc `<LineChart>` — same `ResponsiveContainer` +
         *     `<CartesianGrid>` + `<Line type="monotone">` + `<Legend>`
         *     pattern; the only difference is the data shape).
         *   - data source: `summary.hero_stats` is per-default-season only
         *     (see `_team_hero_stats` in `courtside_data/server/team_service.py:386-431`).
         *     To plot a per-season series you must either:
         *       (a) add a `franchise_arc` field to `TeamHubSummary` (server
         *           change in `team_models.py:62` + `team_service.py:461`)
         *           shaped like the player hub's `career` field — a list
         *           of `{ season, wins, losses, win_pct, ... }` rows; OR
         *       (b) fetch the `and-opponent` dataset per-season client-side
         *           and project the `wins` column into a series. The
         *           recharts `LineChart` consumes `chartRows` (a flat
         *           array of `{ season, wins }`) the same way the player
         *           hub does — see `overview.tsx:21-30`.
         * How:
         *   1. Add the recharts imports (already used by the player hub):
         *        import { CartesianGrid, Legend, Line, LineChart,
         *          ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
         *   2. Build `chartRows` from the chosen data source (default to
         *      (a) once the server change lands; use (b) with
         *      `useSeasonDataset(identifier, season, "and-opponent")` and
         *      a per-season loop until then).
         *   3. Replace the placeholder div with:
         *        <div className="h-80 rounded-md border border-court-line bg-white p-3">
         *          <ResponsiveContainer width="100%" height="100%">
         *            <LineChart data={chartRows} margin={{ top: 8, right: 20, bottom: 8, left: 0 }}>
         *              <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" />
         *              <XAxis dataKey="season" tick={{ fontSize: 12 }} minTickGap={24} />
         *              <YAxis tick={{ fontSize: 12 }} />
         *              <Tooltip />
         *              <Legend />
         *              <Line type="monotone" dataKey="wins" name="Wins" stroke="#0f766e" strokeWidth={2} dot />
         *              <Line type="monotone" dataKey="win_pct" name="Win %" stroke="#b45309" strokeWidth={2} dot />
         *            </LineChart>
         *          </ResponsiveContainer>
         *        </div>
         * Decision needed: server-side series (option a) vs client-side
         *   per-season fetch (option b)? Option (a) is one round-trip and
         *   matches the player hub; option (b) works today but requires
         *   fetching the `and-opponent` dataset for every season in
         *   `available_seasons` (potentially 10+ parallel queries) and
         *   re-projects data the server already has. Default: (a).
         * Verify: after the change, the chart should render a single line
         *   for the default season from `summary.hero_stats`, and N lines
         *   once the series is wired. `npx vitest run` should still pass
         *   (the `Overview` test mocks the summary payload). */}
        <div className="flex h-80 items-center justify-center rounded-md border border-dashed border-court-line bg-white p-3 text-sm text-court-muted">
          Chart placeholder
        </div>
      </section>

      <section className="space-y-3">
        <SectionHeading
          title="Roster"
          description={`${summary.roster.row_count.toLocaleString()} rows from the current roster.`}
        />
        <DataTable
          rows={summary.roster.rows}
          columns={summary.roster.columns}
          defaultVisibleColumns={summary.roster.default_visible_columns}
        />
      </section>
    </div>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-court-line bg-white p-4">
      <div className="flex items-center gap-2 text-sm text-court-muted">
        <span className="text-court-accent" aria-hidden="true">
          {icon}
        </span>
        {label}
      </div>
      <div className="mt-2 text-2xl font-semibold tabular-nums text-court-ink">{value}</div>
    </div>
  );
}
