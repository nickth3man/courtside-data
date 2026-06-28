"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { Button } from "@/components/button";
import { useTeamSearch } from "@/features/team-hub/api/queries";

interface TeamSearchProps {
  compact?: boolean;
}

// TODO(team-hub): bring team-search in line with player-search — add a
// 250ms keystroke debounce and `?term=` URL persistence (both already
// implemented in `ui/src/features/player-hub/components/player-search.tsx`).
//
// What: today this component renders results immediately on every
//   keystroke (lines 17 + 35-39 below). The player-hub equivalent debounces
//   the typed value by 250ms before it reaches `usePlayerSearch`, and
//   mirrors the term to `?term=` in the URL on submit and back to the
//   input on mount. Team-search is missing both behaviors — typing
//   fires one request per keystroke, and the term is lost on a hard
//   refresh.
// Where:
//   - this file, lines 16-17: the `useState` + `useTeamSearch(term)` call
//     needs an intermediate `debouncedTerm` state and a `setTimeout` effect.
//   - this file, lines 21-26: the `submit` handler should call
//     `setParam("term", trimmedTerm)` before navigating, mirroring
//     `player-search.tsx:72-80`.
//   - mount: read `?term=` from the URL once via `useUrlParam().get("term")`
//     and prefill `term` + `debouncedTerm` so a hard refresh on
//     `/teams?term=LAL` opens with the LAL result pre-listed.
//   - mirror: `ui/src/features/player-hub/components/player-search.tsx:15-63`
//     (the JSDoc there documents the debounce + URL-persistence contract
//     and the `getParamRef` pattern that captures the `useUrlParam` closure
//     exactly once on mount).
// How:
//   1. Add a `useUrlParam` import from `@/lib/use-url-param` and a
//      `useRef` + `useEffect` block to capture the latest `get` reference
//      — verbatim from `player-search.tsx:39-48`.
//   2. Introduce a `debouncedTerm` state + 250ms debounce effect
//      (`player-search.tsx:51-54`) and feed `debouncedTerm` to
//      `useTeamSearch(debouncedTerm)` instead of `term`.
//   3. On mount, read `?term=` and prefill `term` + `debouncedTerm`
//      (`player-search.tsx:57-63`).
//   4. In `submit`, call `setParam("term", trimmedTerm)` *before* the
//      `router.push` so a user who refreshes the search page after
//      submitting lands back on the same term.
//   5. While the debounce is pending (`term !== debouncedTerm`) or the
//      query is in flight (`query.isFetching`), render a "Searching…"
//      affordance with a `LoaderCircle` spinner — replace the current
//      "Searching" static text on line 50.
// Decision needed: should `useTeamSearch` itself debounce (e.g. accept a
//   `debounceMs` option) or should the debounce stay in the component?
//   Default: keep it in the component. The hook stays a thin wrapper
//   over `apiFetch` and the debounce is a UI concern — matches player-hub.
// Verify: from `ui/`, `npx vitest run src/features/team-hub` and the
//   analogous player-hub test both pass. The new debounce behavior is
//   covered by hand-testing the search box (type "LAL" — exactly one
//   `/api/teams/search?term=LAL` request fires, not three).
export function TeamSearch({ compact = false }: TeamSearchProps) {
  const [term, setTerm] = useState("");
  const router = useRouter();
  const query = useTeamSearch(term);
  const results = query.data ?? [];

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const first = results[0];
    if (first) {
      router.push(`/teams/${first.identifier}`);
    }
  }

  return (
    <div className={compact ? "w-full max-w-xl" : "w-full"}>
      <form className="flex min-h-11 gap-2" onSubmit={submit}>
        <label className="relative flex-1">
          <span className="sr-only">Search teams</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-court-muted" />
          <input
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder="Search teams"
            className="h-11 w-full rounded-md border border-court-line bg-white pl-9 pr-3 text-sm outline-none transition focus:border-court-accent focus:ring-2 focus:ring-teal-100"
          />
        </label>
        <Button type="submit" variant="primary" disabled={results.length === 0}>
          Open
        </Button>
      </form>

      {term.trim().length >= 2 ? (
        <div className="mt-2 max-h-80 overflow-auto rounded-md border border-court-line bg-white shadow-sm">
          {query.isLoading ? (
            <div className="px-3 py-3 text-sm text-court-muted">Searching</div>
          ) : results.length > 0 ? (
            <div className="divide-y divide-zinc-100">
              {results.map((result) => (
                <button
                  key={result.identifier}
                  type="button"
                  onClick={() => router.push(`/teams/${result.identifier}`)}
                  className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm hover:bg-zinc-50"
                >
                  <span>
                    <span className="block font-medium text-court-ink">{result.name}</span>
                    <span className="text-xs text-court-muted">{result.identifier}</span>
                  </span>
                  <span className="shrink-0 rounded-md bg-zinc-100 px-2 py-1 text-xs text-court-muted">
                    {result.leagues.join("/")}
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <div className="px-3 py-3 text-sm text-court-muted">No results</div>
          )}
        </div>
      ) : null}
    </div>
  );
}
