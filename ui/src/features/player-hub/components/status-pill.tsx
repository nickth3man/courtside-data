"use client";

import { Database, LoaderCircle, WifiOff } from "lucide-react";

import { useStatus } from "@/features/player-hub/api/queries";

export function StatusPill() {
  const status = useStatus();

  if (status.isLoading) {
    return (
      <span className="inline-flex h-8 items-center gap-2 rounded-md border border-court-line bg-white px-3 text-xs text-court-muted">
        <LoaderCircle className="size-3.5 animate-spin" aria-hidden="true" />
        API
      </span>
    );
  }

  if (status.isError || !status.data?.ok) {
    return (
      <span className="inline-flex h-8 items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 text-xs font-medium text-court-danger">
        <WifiOff className="size-3.5" aria-hidden="true" />
        Offline
      </span>
    );
  }

  return (
    <span className="inline-flex h-8 items-center gap-2 rounded-md border border-teal-200 bg-court-accent-soft px-3 text-xs font-medium text-teal-900">
      <Database className="size-3.5" aria-hidden="true" />
      {status.data.transport}
    </span>
  );
}
