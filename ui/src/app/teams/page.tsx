// TODO(team-hub): add cross-navigation between `/players` and `/teams` once a
// shared layout/nav exists. Today both pages render their `<SearchPage />`
// in isolation — there is no way to switch from a player workspace to a
// team workspace without editing the URL by hand.
//
// What: build a single navigation surface that lets a user move between
//   the player-hub and team-hub landing pages (and ideally the per-entity
//   workspaces). This page (`/teams`) and `ui/src/app/players/page.tsx`
//   are currently the only two pages in the app, so the nav is small.
// Where:
//   - this file, line ~5: wrap the `<SearchPage />` in a layout once the
//     shared nav component exists.
//   - mirror: `ui/src/app/players/page.tsx` (5 lines, identical shape).
//   - layout placement options:
//       (a) Root layout: `ui/src/app/layout.tsx` (21 lines today) currently
//           only wraps `<QueryProvider>`. Adding the nav here is the
//           minimum-diff path but it appears on every route — including
//           the not-found/error/loading segments that don't need it.
//       (b) Route-group layout: create `ui/src/app/(hub)/layout.tsx`
//           and move `/players` and `/teams` (and `/`) under that group
//           so the nav only appears on hub pages. Cleaner separation but
//           requires moving the two existing route folders.
//   - the home page currently redirects to `/players` via
//     `ui/src/app/page.tsx:3` (`redirect("/players")`). The TODO here
//     assumes the home page becomes a hub/landing page with both links
//     side by side, instead of an unconditional redirect.
// How:
//   1. Pick (a) or (b) — default: (b), the route-group layout, because
//      it leaves room to add non-hub routes (docs, settings) without
//      dragging the nav along.
//   2. Build `ui/src/components/hub-nav.tsx` (new shared component,
//      sibling to `ui/src/components/button.tsx`) with two `<Link>`s to
//      `/players` and `/teams`, and a `usePathname()` call to highlight
//      the active entry.
//   3. Move `ui/src/app/page.tsx` under the route group (or replace
//      the redirect with a real landing page that links to both hubs).
//   4. Add `<HubNav />` to the new `app/(hub)/layout.tsx` so it renders
//      above both `app/(hub)/players/page.tsx` and
//      `app/(hub)/teams/page.tsx`.
// Decision needed: which entity set belongs in the nav? Today: players
//   and teams. The `courtside_data.endpoints` registry has ~55 endpoint
//   specs, and there's a future "coaches" / "referees" hub on the
//   roadmap. The nav should accept an array of `{ label, href }` from
//   a new `ui/src/lib/hubs.ts` so adding a hub is a one-line config
//   change instead of a JSX edit.
// Verify: after the layout lands, `npx tsc --noEmit && npx eslint .` from
//   `ui/`, then a manual smoke test: `npm run dev`, visit `/`, `/players`,
//   and `/teams`, confirm the nav links work and the active state is
//   correct. Add a vitest snapshot for `<HubNav />` if the component
//   becomes non-trivial.
import { SearchPage } from "@/features/team-hub/components/search-page";

export default function TeamsPage() {
  return <SearchPage />;
}
