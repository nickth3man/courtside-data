"use client";

import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";

import { Button } from "@/components/button";
import { usePlayerSearch } from "@/features/player-hub/api/queries";

interface PlayerSearchProps {
  compact?: boolean;
}

export function PlayerSearch({ compact = false }: PlayerSearchProps) {
  const [term, setTerm] = useState("");
  const router = useRouter();
  const query = usePlayerSearch(term);
  const results = query.data ?? [];

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const first = results[0];
    if (first) {
      router.push(`/players/${first.identifier}`);
    }
  }

  return (
    <div className={compact ? "w-full max-w-xl" : "w-full"}>
      <form className="flex min-h-11 gap-2" onSubmit={submit}>
        <label className="relative flex-1">
          <span className="sr-only">Search players</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-court-muted" />
          <input
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder="Search players"
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
                  onClick={() => router.push(`/players/${result.identifier}`)}
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
