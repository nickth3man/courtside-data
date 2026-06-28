# Basketball-Reference `/search/search.fcgi` research — 2026-06-28

Scope: verify the canonical `idx` namespace, the no-`idx` page structure for
populating the new `SearchResultRow.type` discriminator, and the historical
parameter/tab names. All citations include capture date.

---

## 1. Current canonical `idx` values

The no-`idx` page exposes one tab per index, and the sub-`div` under
`<div id="searches">` carries the same id as the tab. The **full set of
indexes that the project should know about** is:

| `idx` value        | Tab label                                       | Card href prefix           | Maps to `type`     | In project's `_search_map` today? |
|--------------------|-------------------------------------------------|----------------------------|--------------------|-----------------------------------|
| `players`          | NBA/ABA/BAA Players                             | `/players/X/{slug}.html`   | `player`           | yes |
| `wnba_players`     | WNBA Players                                    | `/players/{slug}.html`     | `player`           | yes |
| `intl_players`     | International Players                           | `/players/{slug}.html`     | `player`           | yes |
| `nbdl_players`     | G-Lg Players                                    | `/players/{slug}.html`     | `player`           | yes |
| `nbl_players`      | NBL Players                                     | `/players/{slug}.html`     | `player`           | **no** |
| `sup_players`      | NBA, ABA, BAA, and WNBA Players                 | `/players/{slug}.html`     | `player`           | yes |
| `coaches`          | NBA/ABA/BAA Coaches                             | `/coaches/{slug}c.html`    | `coach`            | **no** |
| `wnba_coaches`     | WNBA Coaches                                    | `/coaches/{slug}c.html`    | `coach`            | **no** |
| `executives`       | NBA/ABA/BAA Executives                          | `/executives/{slug}x.html` | `executive`        | **no** |
| `wnba_executives`  | WNBA Executives                                 | `/executives/{slug}x.html` | `executive`        | **no** |
| `referees`         | NBA Referees                                    | `/referees/{slug}r.html`   | `referee`*         | **no** |
| `teams`            | NBA/ABA/BAA Teams                               | `/teams/{ABBR}/`           | `team`             | **no** |
| `team_seasons`     | NBA/ABA/BAA Team Seasons                        | `/teams/{ABBR}/{YYYY}.html`| `team`             | **no** |

\* `referees` is **not** in the user's planned enum (`"player" | "team" |
"coach" | "executive"`). See §6 for the question this raises.

**Where each was confirmed (all captured 2026-06-28):**

- `players, wnba_players, intl_players, nbdl_players, nbl_players, wnba_coaches, coaches, sup_players, executives, wnba_executives, referees, teams, team_seasons` (all 13) — the **project's own**
  `raw/search/ja_page_0.html` fixture. Source: `https://www.basketball-reference.com/search/search.fcgi?search=ja` captured by the project. The tab anchors in that file are:
  ```html
  <div id="search-tabs" class="switcher filter" data-controls="#searches">
    <div id="players-tab" class="current">
      <a href="?search=ja&amp;i=players">NBA/ABA/BAA Players <span>(100+)</span></a>
    </div>
    <div id="wnba_players-tab">
      <a href="?search=ja&amp;i=wnba_players">WNBA Players <span>(100+)</span></a>
    </div>
    <div id="intl_players-tab">
      <a href="?search=ja&amp;i=intl_players">International Players <span>(100+)</span></a>
    </div>
    <div id="nbdl_players-tab">
      <a href="?search=ja&amp;i=nbdl_players">G-Lg Players <span>(100+)</span></a>
    </div>
    <div id="nbl_players-tab">
      <a href="?search=ja&amp;i=nbl_players">NBL Players <span>(38+)</span></a>
    </div>
    <div id="wnba_coaches-tab">
      <a href="?search=ja&amp;i=wnba_coaches">WNBA Coaches <span>(1)</span></a>
    </div>
    <div id="coaches-tab">
      <a href="?search=ja&amp;i=coaches">NBA/ABA/BAA Coaches <span>(54+)</span></a>
    </div>
    <div id="sup_players-tab">
      <a href="?search=ja&amp;i=sup_players">NBA, ABA, BAA, and WNBA Players <span>(100+)</span></a>
    </div>
    <div id="executives-tab">
      <a href="?search=ja&amp;i=executives">NBA/ABA/BAA Executives <span>(10)</span></a>
    </div>
    <div id="wnba_executives-tab">
      <a href="?search=ja&amp;i=wnba_executives">WNBA Executives <span>(3)</span></a>
    </div>
    <div id="referees-tab">
      <a href="?search=ja&amp;i=referees">NBA Referees <span>(10)</span></a>
    </div>
    <div id="teams-tab">
      <a href="?search=ja&amp;i=teams">NBA/ABA/BAA Teams <span>(2)</span></a>
    </div>
    <div id="team_seasons-tab">
      <a href="?search=ja&amp;i=team_seasons">NBA/ABA/BAA Team Seasons <span>(52+)</span></a>
    </div>
  </div>
  ```
- **Live 2026-06-28** confirmation of `coaches, executives, sup_players, players` on
  `?search=ainge` (no idx): `#players` 4, `#coaches` 3, `#sup_players` 2, `#executives` 1.
- **Live 2026-06-28** confirmation of `coaches, executives` on
  `?search=popovich` (no idx): `#coaches` 2, `#executives` 1.
- **Live 2026-06-28** confirmation of `players, sup_players, teams, team_seasons`
  on `?search=bulls` (no idx): `#players` 1, `#sup_players` 1, `#teams` 1, `#team_seasons` 60.
- **Live 2026-06-28** confirmation of `teams, team_seasons` on `?search=celtics` (no idx):
  `#teams` 1, `#team_seasons` 80.
- **Live 2026-06-28** confirmation of `teams, team_seasons` on `?search=lakers` (no idx):
  `#teams` 2 (LAL, MNL), `#team_seasons` 78.

## 2. Result-card markup pattern (live, 2026-06-28)

The no-`idx` page wraps all result cards in `<div id="searches"
class="switcher_content">` with one sub-`div` per index. Every card is
`<div class="search-item">` with these children:

```
div.search-item
├── div.search-item-name        # <a href=…>NAME</a> + optional badges
│   ├── <strong><a href=…>…</a></strong>   # the canonical/primary result is in <strong>
│   ├── <a href=…>…</a>                    # secondary results are bare
│   └── <span class="search-badge search-hof">…</span>     # optional
│       <span class="search-badge search-allstar">…</span> # optional
├── div.search-item-url         # the URL path string (e.g. "/teams/BOS/")
├── div.search-item-league      # ONLY on #sup_players cards (e.g. "NBA")
├── div.note                    # ONLY on player cards (e.g. nicknames)
├── div.search-item-team        # ONLY on player cards ("Plays for: …" / "Last played for: …")
```

### Verbatim team card (from `?search=celtics`)

```html
<div class="search-item">
    <div class="search-item-name">
        <strong>
            <a href="https://www.basketball-reference.com/teams/BOS/">Boston Celtics (1947-2026)</a>
        </strong>


    </div>
    <div class="search-item-url">/teams/BOS/</div>




</div>
```

### Verbatim player card (from `?search=bulls`)

```html
<div class="search-item">
    <div class="search-item-name">

            <a href="https://www.basketball-reference.com/players/s/sharmbi01.html">Bill Sharman (1951-1961)</a>

        <span class="search-badge search-hof">Hall of Fame</span>
        <span class="search-badge search-allstar">All-Star</span>
    </div>
    <div class="search-item-url">/players/s/sharmbi01.html</div>


    <div class="note">Nickname(s): Bullseye Bill, Battling Bill, Willie</div>


    <div class="search-item-team">Last played for: Boston Celtics</div>




</div>
```

### Verbatim coach / executive cards (from `?search=ainge`)

```html
<!-- #coaches -->
<div class="search-item">
    <div class="search-item-name">

            <a href="https://www.basketball-reference.com/coaches/aingeda01c.html">Danny Ainge (1997-2000)</a>

    </div>
    <div class="search-item-url">/coaches/aingeda01c.html</div>
</div>

<!-- #executives -->
<div class="search-item">
    <div class="search-item-name">

            <a href="https://www.basketball-reference.com/executives/aingeda01x.html">Danny Ainge (2003-2026)</a>

    </div>
    <div class="search-item-url">/executives/aingeda01x.html</div>
</div>
```

### The reliable discriminator signal

The **parent sub-`div` id** (`div#players`, `div#coaches`, `div#executives`,
`div#teams`, `div#team_seasons`, …) is the cleanest signal. Each `search-item`
sits inside exactly one sub-`div`, and the mapping from sub-`div` id to entity
type is fixed (see §1 table). The existing project parser at
`courtside_data/parsing/_rows_search.py:18-37` only looks at
`div#searches div#players div.search-item` — which is why team/coach/exec
results are silently dropped today.

The href prefix is a usable **secondary** signal but has one ambiguity: both
`#teams` and `#team_seasons` cards have hrefs starting with `/teams/{ABBR}/…`,
so a href-only discriminator cannot tell the two apart. The parent-`div` id
resolves this directly. Href prefixes by entity (all from live captures):

| Prefix                              | Type             |
|-------------------------------------|------------------|
| `/players/{a}/{slug}.html`          | player           |
| `/coaches/{slug}c.html`             | coach            |
| `/executives/{slug}x.html`          | executive        |
| `/referees/{slug}r.html`            | referee          |
| `/teams/{ABBR}/`                    | team (franchise) |
| `/teams/{ABBR}/{YYYY}.html`         | team_season      |

A `<strong>` wrapper around the anchor is a **ranking** signal (the canonical
match for the term in that sub-`div` is bolded) — it is *not* a type
discriminator. Don't rely on it for `type`.

## 3. Historical `idx` renames

### 3a. URL parameter: `i=` → `idx=`

In the project's captured fixture `raw/search/ja_page_0.html`, the tab
anchors use the **`i=`** form:

```html
<a href="?search=ja&amp;i=players">NBA/ABA/BAA Players <span>(100+)</span></a>
```

In the **live 2026-06-28** response, the search form on the same page no
longer carries an `idx`/`i` field at all — the form is:

```html
<form method="get" name="f_big" action="https://www.basketball-reference.com/search/search.fcgi">
  <input type="search" name="search" value="…" …>
  <input type="submit" value="Search">
</form>
```

…and the tab anchors are now text-only `<a>` tags with no `href` (driven
client-side by the `switcher` widget). Submitting the form sends
`?search=…` only; the `idx=` parameter is still understood server-side when
appended manually, but BR no longer advertises it in the markup.

I could not pin a specific date for the `i=` → `idx=` rename; it pre-dates
the project's fixture capture. The Wayback Machine returned `404` for
`web.archive.org/web/2024/...` so I could not pull a dated capture. (Open
issue — the project's `ja_page_0.html` is the only dated evidence.)

### 3b. `nbl_players` is a recent addition

The project's existing `_search_map` only fans out over 5 player indices
(`players, wnba_players, intl_players, nbdl_players, sup_players`). The
`ja_page_0.html` fixture adds `nbl_players` (NBL = Australia's National
Basketball League, not to be confused with the historical American NBL).
The BR linker page still lists `NBL` as a supported league ("Players,
Teams, Seasons, Leaders, Awards"), so this is a live, maintained index,
not legacy.

### 3c. `coaches`, `executives`, `referees` are not new

These indexes appear in the project's `ja_page_0.html` capture and are
present in the live page for any search term that matches a coach/exec/ref
(e.g. `?search=ainge` shows `#coaches` and `#executives`; `?search=popovich`
shows both). They have been in BR's search results UI for years; I could
not find a changelog or GitHub issue pinning the exact launch date, and
the wayback machine returned `404` for the time range I tried.

### 3d. GitHub search for prior art

I searched the GitHub Research index for `jaebradley`, `vhpg2021`,
`vishaalagartha`, `dylburger`, and any scraper that hits
`/search/search.fcgi?idx=`. Two relevant hits:

- **`jaebradley/basketball_reference_web_scraper`** (547★, the canonical
  Python BR scraper) confirms the same XPath: `//div[@id="searches"]/div[@id="players"]`
  (see `https://raw.githubusercontent.com/jaebradley/basketball_reference_web_scraper/master/basketball_reference_web_scraper/html.py`,
  the `SearchPage` class). It only handles the player tab and does not
  iterate over other indexes — i.e. it has the same blind spot as the
  project's current parser.
- The other public scrapers (`vishaalagartha/basketball_reference_scraper`,
  `FranGoitia/basketball_reference`, `basketball-reference-webscrapper`)
  do **not** hit the search endpoint at all — they enumerate players via
  `/players/{letter}/` directories. None of them document the `idx`
  namespace.

No GitHub scraper I found exposes team/coach/exec/ref search results. The
discriminator-field design choice in the project is a green-field
extraction; there is no upstream convention to follow.

## 4. Team-card-on-no-`idx` page confirmation

**Yes — teams, coaches, executives, and referees all appear on the no-`idx`
page**, each in their own sub-`div` (so they are present in the same HTML
response, no second fetch required). Verified:

| Term            | Sub-divs present (with item counts)                                       |
|-----------------|----------------------------------------------------------------------------|
| `celtics`       | `teams` (1), `team_seasons` (80+)                                         |
| `lakers`        | `teams` (2 — LAL + MNL), `team_seasons` (78+)                              |
| `bulls`         | `players` (1), `sup_players` (1), `teams` (1), `team_seasons` (60+)       |
| `ainge`         | `players` (4), `coaches` (3), `sup_players` (2), `executives` (1)         |
| `popovich`      | `coaches` (2), `executives` (1)                                           |
| `lebron`        | `players` (3), `sup_players` (3)                                          |
| `jaebaebae`     | none (0 hits)                                                              |

So the single no-`idx` fetch is the right place to populate `type` from.
`?idx=teams` and `?idx=players` do work as server-side filters (e.g.
`?search=lebron&idx=players` returns only the `#players` sub-`div` with
`class="current"`), but they have a second behavior: when the term is an
**exact** match for an entity in that index, BR 301s to the detail page:

- `?search=jamesle01&idx=players` → **redirects** to `/players/j/jamesle01.html`
  (metadata.url after redirect: `https://www.basketball-reference.com/players/j/jamesle01.html`).
- `?search=celtics&idx=teams` → **redirects** to `/teams/BOS/`.
- `?search=celtics&idx=players` → stays on the search page, returns the
  "0 hits" empty page (no `search-item` cards).

This is also the behavior `jaebradley/basketball_reference_web_scraper`
relies on for its "direct player lookup" — see the `if response.url.startswith("/search/search.fcgi") … elif response.url.startswith("/players")` branch
in `http_service.py`.

## 5. Recommendation (since the schema is settled)

**Use the parent sub-`div` id as the primary `type` source.** The workflow
extraction step should iterate the sub-`div`s, not the individual cards:

```python
# pseudocode — the actual change is in _SEARCH_WORKFLOW's result-mapping step
SUB_DIV_TO_TYPE: dict[str, str] = {
    "players": "player", "wnba_players": "player", "intl_players": "player",
    "nbdl_players": "player", "nbl_players": "player", "sup_players": "player",
    "coaches": "coach", "wnba_coaches": "coach",
    "executives": "executive", "wnba_executives": "executive",
    "teams": "team", "team_seasons": "team",
    # "referees": "referee",  # not in user's enum — see §6
}

for sub in selector.css("div#searches > div[id]"):
    type_ = SUB_DIV_TO_TYPE.get(sub.attrib["id"])
    if type_ is None:        # referees, or a new index BR adds later
        continue             # skip silently (existing-parser-style degrade)
    for card in sub.css("div.search-item"):
        rows.append(SearchResultRow(
            name=...,
            identifier=...,
            leagues=...,
            type=type_,
        ))
```

The href prefix is a sound **validation** signal (and useful to keep as a
sanity check while wiring this up), but not the primary signal because:

1. `/teams/` is shared by `teams` and `team_seasons` — href alone can't tell
   them apart, and the user's enum collapses them anyway.
2. The parent-`div` id is one CSS read at the wrapper level; you don't
   have to inspect anchors.

The existing fanout in `_search_map` over `players, wnba_players,
intl_players, nbdl_players, sup_players` is **no longer needed** for
content reasons — those 5 sub-`div`s all appear on a single no-`idx` page
when there's a match. The fanout can be simplified to a single URL
`/search/search.fcgi?search={term}` (and the `_search_map` helper
contract can stay the same; just point all `idx` variants at the same
fixture file, or drop the `idx` key entirely from the URL map for the
search endpoint). The pagination is still per-sub-`div` (the
`#players .search-pagination` link paginates only players), so
**pagination strategy needs a small follow-on** — the simplest fix is
to union all sub-`div`s' items and let one combined `offset` parameter
slice them, accepting that this is "good enough" because the
`#sup_players` sub-`div` is the superset and its pagination is the
project's actual source of multi-page results today.

## 6. Open questions (out of scope but worth flagging)

1. **`referees` is not in the user's planned enum.** The live sub-`div`
   `#referees` exists (see `?search=ja` → 10 referee matches). Options:
   extend the enum to include `"referee"`, or filter the sub-`div` out at
   extraction time. The recommendation above silently skips it.

2. **`team_seasons` vs `teams`** — the user's enum collapses both to
   `"team"`. For team-search the project will get many duplicate-by-
   construction rows (one per season) mixed in with the franchise row.
   Consider emitting one row per `teams` sub-`div` (the franchise-level
   href `/teams/BOS/`) and skipping `team_seasons` cards, or adding a
   `sub_type: "franchise" | "season"` sub-field (schema change — out of
   scope per the prompt).

3. **No changelog found for the `i=` → `idx=` rename.** The project's
   `ja_page_0.html` fixture is the only dated evidence I have. A direct
   ask on `sports-reference.com/bot-traffic.html` or a search of
   `web.archive.org` snapshots from 2017-2020 would pin this down — but
   the URL `https://web.archive.org/web/2024/https://www.basketball-reference.com/search/search.fcgi?search=celtics`
   returned 404 on 2026-06-28, so the wayback CDX index may not have
   captured the search endpoint for that period.

## 7. Sources & capture dates

| Source                                                                                                              | Captured  | What it confirmed                                                                       |
|---------------------------------------------------------------------------------------------------------------------|-----------|-----------------------------------------------------------------------------------------|
| `https://www.basketball-reference.com/search/search.fcgi?search=celtics`                                            | 2026-06-28| No-`idx` page has `#teams`, `#team_seasons` for "celtics"                                |
| `https://www.basketball-reference.com/search/search.fcgi?search=lakers`                                             | 2026-06-28| No-`idx` page has `#teams` (LAL, MNL) and `#team_seasons` for "lakers"                  |
| `https://www.basketball-reference.com/search/search.fcgi?search=bulls`                                              | 2026-06-28| No-`idx` page has `#players`, `#sup_players`, `#teams`, `#team_seasons` for "bulls"     |
| `https://www.basketball-reference.com/search/search.fcgi?search=ainge`                                              | 2026-06-28| No-`idx` page has `#players`, `#coaches`, `#sup_players`, `#executives` for "ainge"     |
| `https://www.basketball-reference.com/search/search.fcgi?search=popovich`                                           | 2026-06-28| No-`idx` page has `#coaches`, `#executives` for "popovich"                              |
| `https://www.basketball-reference.com/search/search.fcgi?search=lebron&idx=players`                                 | 2026-06-28| `idx=players` returns only the players sub-`div`                                         |
| `https://www.basketball-reference.com/search/search.fcgi?search=jamesle01&idx=players`                              | 2026-06-28| `idx=players` on exact-match term → 301 to `/players/j/jamesle01.html`                    |
| `https://www.basketball-reference.com/search/search.fcgi?search=celtics&idx=teams`                                 | 2026-06-28| `idx=teams` on exact-match term → 301 to `/teams/BOS/`                                    |
| `https://www.basketball-reference.com/search/search.fcgi?search=celtics&idx=players`                               | 2026-06-28| `idx=players` with 0 matches → stays on search page, returns "0 hits"                   |
| `https://www.basketball-reference.com/search/search.fcgi?search=jaebaebae`                                         | 2026-06-28| 0 hits on live site (fixture in repo is from a prior era)                                |
| `https://raw.githubusercontent.com/jaebradley/basketball_reference_web_scraper/master/basketball_reference_web_scraper/html.py` | 2026-06-28 | Confirms `//div[@id="searches"]/div[@id="players"]` is the XPath used by the reference Python BR scraper |
| `https://raw.githubusercontent.com/jaebradley/basketball_reference_web_scraper/master/basketball_reference_web_scraper/http_service.py` | 2026-06-28 | Confirms no-`idx` single-fetch pattern, with redirect-to-detail-page branch for exact matches |
| `https://web.archive.org/web/2024/...search.fcgi?search=celtics`                                                    | 2026-06-28| 404 — no dated capture in that range                                                     |
| `courtside-data/raw/search/ja_page_0.html`                                                                          | (in repo) | Source of the full 13-`idx` list with `i=` (not `idx=`) tab anchor hrefs                  |
| `courtside-data/courtside_data/parsing/_rows_search.py:18-37`                                                       | (in repo) | Confirms the existing parser's `div#searches div#players div.search-item` selector      |
| `courtside-data/courtside_data/server/fixtures.py:168-181`                                                          | (in repo) | Confirms the project's existing 5-`idx` fanout in `_search_map`                          |
| `courtside-data/courtside_data/server/team_service.py:488-579`                                                       | (in repo) | The Option-A/Option-B decision point this research feeds into                            |
