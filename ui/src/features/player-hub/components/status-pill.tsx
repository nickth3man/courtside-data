"use client";

import { Database, LoaderCircle, TriangleAlert, WifiOff } from "lucide-react";

import { isRateLimited } from "@/lib/api-errors";

import { useStatus } from "@/features/player-hub/api/queries";

/**
 * API status pill — surfaces the current transport mode plus the two
 * operational signals that need user-visible attention:
 *
 * 1. **Rate-limit jail** — the `useStatus` query is in an error state
 *    with `code === "rate_limit_jailed"`. We read the error from the
 *    query result (not from a prop) so the pill can also surface the
 *    server-supplied `retryAfter` countdown. Using the internal hook
 *    here avoids changing the public prop signature and keeps the
 *    caller in `player-hub.tsx` untouched.
 *
 * 2. **Missing fixture root** — the status payload is healthy but
 *    `transport === "fixture"` and `fixture_root_exists === false`,
 *    meaning the backend has switched to live data because no local
 *    fixtures were found.
 *
 * The `fixture_root_exists` warning uses an inline amber variant
 * (Tailwind's `amber-*` palette) rather than promoting a new shared
 * component, since this is the only consumer.
 */
export function StatusPill() {
  const status = useStatus();

  // 1. Rate-limit — highest priority. Overrides every other state so a
  //    user who is currently throttled always sees the actionable pill.
  if (isRateLimited(status.error)) {
    const retryAfter = status.error.retryAfter;
    const label = retryAfter !== undefined ? `Rate limited (${retryAfter}s)` : "Rate limited";
    return (
      <span className="inline-flex h-8 items-center gap-2 rounded-md border border-court-danger-line bg-court-danger-soft px-3 text-xs font-medium text-court-danger">
        <WifiOff className="size-3.5" aria-hidden="true" />
        {label}
      </span>
    );
  }

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
      <span className="inline-flex h-8 items-center gap-2 rounded-md border border-court-danger-line bg-court-danger-soft px-3 text-xs font-medium text-court-danger">
        <WifiOff className="size-3.5" aria-hidden="true" />
        Offline
      </span>
    );
  }

  // 2. Fixture root missing — the API is reachable and reporting OK,
  //    but the configured fixture directory does not exist on disk.
  //    Only meaningful when transport is `fixture`; on live transport
  //    `fixture_root_exists` is `null` and we fall through to the
  //    transport pill below.
  if (status.data.transport === "fixture" && status.data.fixture_root_exists === false) {
    return (
      <span className="inline-flex h-8 items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 text-xs font-medium text-amber-800">
        <TriangleAlert className="size-3.5" aria-hidden="true" />
        Fixture root missing
      </span>
    );
  }

  return (
    <span className="inline-flex h-8 items-center gap-2 rounded-md border border-court-accent-line bg-court-accent-soft px-3 text-xs font-medium text-court-accent-strong">
      <Database className="size-3.5" aria-hidden="true" />
      {status.data.transport}
    </span>
  );
}
