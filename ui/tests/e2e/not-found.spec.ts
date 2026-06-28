import { expect, test } from "@playwright/test";

/**
 * E2E specs for the `/players/[identifier]` not-found / error paths.
 *
 * `PlayerHub` now intercepts `TypedApiError` before it reaches
 * `QueryBoundary` and routes it to the nearest route boundary:
 * - `invalid_player` / `missing_fixture` → `notFound()` → `not-found.tsx`
 * - everything else (`rate_limit_jailed`, `schema_drift`, …) → `throw err` → `error.tsx`
 *
 * The "non-existent route segment" case still has no clean trigger
 * (there's no `app/not-found.tsx` and Next.js's own 404 doesn't match
 * the `players/[identifier]` segment), so it stays as `test.fixme`.
 */

const status = {
  ok: true,
  transport: "fixture",
  endpoint_count: 61,
  fixture_root: "raw",
  fixture_root_exists: true,
};

const catalog = {
  tabs: [
    { id: "overview", label: "Overview", description: "Overview", scope: "player", datasets: ["career"], default_dataset: "career" },
    { id: "career", label: "Career", description: "Career", scope: "player", datasets: ["career"], default_dataset: "career" },
  ],
  datasets: [
    {
      id: "career",
      label: "Career",
      endpoint_name: "player_career_stats",
      scope: "player",
      description: "Career rows",
      supports_export: true,
      default_visible_columns: ["season", "team_name_abbr", "points_per_game"],
      columns: [
        { key: "season", label: "Season", default_visible: true, numeric: false },
        { key: "team_name_abbr", label: "Team", default_visible: true, numeric: false },
        { key: "points_per_game", label: "Points", default_visible: true, numeric: true },
      ],
    },
  ],
};

test.beforeEach(async ({ page }) => {
  await page.route("http://127.0.0.1:8765/api/status", async (route) => {
    await route.fulfill({ json: status });
  });
  await page.route("http://127.0.0.1:8765/api/endpoints/player-hub", async (route) => {
    await route.fulfill({ json: catalog });
  });
  await page.route("http://127.0.0.1:8765/api/players/doesnotexist01/summary", async (route) => {
    await route.fulfill({
      status: 404,
      json: { detail: { code: "invalid_player", message: "Player not found", detail: {} } },
    });
  });
});

test("unknown identifier shows not-found page", async ({ page }) => {
  await page.goto("/players/doesnotexist01");

  // The `not-found.tsx` route segment renders an `<EmptyState>` with
  // title="Player not found" and a `<Link href="/players">Back to players</Link>`.
  await expect(page.getByText("Player not found")).toBeVisible({ timeout: 5_000 });
  await expect(page.getByRole("link", { name: "Back to players" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Back to players" })).toHaveAttribute("href", "/players");
});

test("missing fixture shows tailored message", async ({ page }) => {
  // Per-test override: `page.route` handlers are matched most-recent-first,
  // so this handler shadows the `beforeEach` one for this URL.
  await page.route("http://127.0.0.1:8765/api/players/nofixture01/summary", async (route) => {
    await route.fulfill({
      status: 404,
      json: { detail: { code: "missing_fixture", message: "No fixture data for this player", detail: {} } },
    });
  });

  await page.goto("/players/nofixture01");

  // The `error.tsx` `missing_fixture` branch renders an `<ErrorCard>` with
  // title="Fixture data unavailable" and a back link to `/players`.
  await expect(page.getByText("Fixture data unavailable")).toBeVisible({ timeout: 5_000 });
  await expect(page.getByRole("link", { name: "Back to players" })).toBeVisible();
});

test.fixme("non-existent route segment shows not-found", async () => {});
// TODO(e2e): add a global `app/not-found.tsx` so the root-level 404 path
//   is testable, then flip this `test.fixme` to a real `test(...)`.
//
// Why it's still `fixme`: there is no `ui/src/app/not-found.tsx` (the
// global root-level 404). Next.js's built-in 404 page renders instead
// of any custom UI, so there is no testable heading/CTA to assert on.
// The segment-level `app/players/[identifier]/not-found.tsx` is now
// reachable via `notFound()` (covered by the real tests above), but
// that segment only fires for `notFound()` calls inside its subtree —
// a truly unmatched path (e.g. `/nonexistent`, `/foo/bar`) bubbles up
// to the root and is currently unhandled.
//
// What needs to be created: `ui/src/app/not-found.tsx` — a server
// component that mirrors `ui/src/app/players/not-found.tsx` but lives
// at the app root, so it catches every unmatched route. Shape:
//   - "Page not found" heading (or similar).
//   - One short sentence of supporting copy.
//   - A `<Link href="/players">Back to players</Link>` CTA.
//
// Where:
//   - create `ui/src/app/not-found.tsx` (new file, server component,
//     no hooks, no client state — mirrors `app/players/not-found.tsx`).
//   - cross-reference: `ui/src/app/players/not-found.tsx:1-31` is the
//     per-segment pattern to clone; `ui/src/app/players/[identifier]/
//     not-found.tsx:1-31` is the segment-under-`[identifier]` pattern.
//   - cross-reference: `ui/src/app/players/[identifier]/page.tsx:1-16`
//     shows how `notFound()` is triggered in the segment subtree (the
//     root-level `not-found.tsx` is reached by route miss, not by
//     `notFound()`).
//
// How:
//   1. Create `ui/src/app/not-found.tsx` with a `<main>` + `<EmptyState>`
//      + `<Link href="/players">` (copy the structure from
//      `app/players/not-found.tsx`, swap the title to "Page not found").
//   2. Flip the `test.fixme` below to `test(...)`:
//        await page.goto("/nonexistent");
//        await expect(page.getByText("Page not found")).toBeVisible();
//        await expect(page.getByRole("link", { name: "Back to players" }))
//          .toBeVisible();
//   3. Decide whether to mock any backend routes — the root 404
//      doesn't render `PlayerHub`, so no `/api/players/...` calls are
//      made. The existing `beforeEach` mocks (status + catalog) are
//      harmless to keep.
//
// Distinct from the per-segment `not-found.tsx`:
//   - Global (`app/not-found.tsx`): catches every route that doesn't
//     match any segment, app-wide. Renders for `/nonexistent`,
//     `/foo/bar`, `/players/` (trailing slash, after Next.js
//     normalisation).
//   - Per-segment (`app/players/[identifier]/not-found.tsx`): catches
//     `notFound()` calls within the `players/[identifier]` subtree.
//     Renders for a 404 API response on `/players/doesnotexist01`.
//   - The two never overlap — `notFound()` from a segment never
//     reaches the global fallback; a route miss never reaches a
//     segment fallback.
//
// Decision needed: should the global page share the `EmptyState`
//   component (current proposal) or have its own bespoke layout? The
//   minimal-delta option is to share `EmptyState`; the bespoke option
//   adds a "report a broken link" affordance that doesn't exist today.
//
// Verify: after creating `app/not-found.tsx`, run `npm run dev` and
//   navigate to http://127.0.0.1:3000/nonexistent — the custom 404
//   should render. Then `npx playwright test tests/e2e/not-found.spec.ts`
//   (with the flip applied) should pass.
