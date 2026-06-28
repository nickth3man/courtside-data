"use client";

import { Activity, Shield, Target } from "lucide-react";
import type { ReactNode } from "react";

import { SectionHeading } from "@/components/section-heading";
// TODO: extract DataTable to @/components/data-table.tsx so team-hub and player-hub can share it.
import { DataTable } from "@/features/player-hub/components/data-table";
import type { TeamHubSummary } from "@/features/team-hub/types";
import { formatStat } from "@/features/player-hub/utils/format";

interface OverviewProps {
  summary: TeamHubSummary;
}

export function Overview({ summary }: OverviewProps) {
  // TODO: confirm hero_stats keys with the backend contract (wins/losses/win_pct/ppg/opp_ppg …).
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
        {/* TODO: render a recharts LineChart driven by summary.roster rows (or a dedicated series endpoint). */}
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
