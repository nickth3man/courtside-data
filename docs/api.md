# API

## Client

The `import`ed `client` contains the API methods that will access **Basketball Reference**

```python
from courtside_data import client

client.team_roster(team_abbreviation="BOS", season_end_year=2024)
```

These module-level functions share one HTTP session per process (TCP/TLS
connection reuse and one response cache).

!!! note
    Only a handful of endpoints are shown on this page. The full set of 50+
    endpoints — with parameters, URL patterns, and CSV columns — is in the
    [Endpoint Reference](reference.md).

### `CourtsideClient`

To control session behavior, construct a `CourtsideClient`. It exposes every
endpoint as a same-named method bound to its own HTTP session:

```python
from courtside_data import CourtsideClient

client = CourtsideClient(cache=False)
roster = client.team_roster(team_abbreviation="BOS", season_end_year=2024)
```

The constructor accepts:

| Argument      | Default       | Purpose                                              |
| ------------- | ------------- | ---------------------------------------------------- |
| `cache`       | `True`        | RFC 9111 response caching (SQLite-backed)            |
| `headers`     | `None`        | Override or extend the browser-like default headers  |
| `impersonate` | `"chrome124"` | TLS fingerprint impersonation; `None` for plain TLS  |
| `timeout`     | `None`        | An `httpx.Timeout`; defaults to 30s (10s connect)    |

!!! warning
    Rate limiting is **not** configurable. Requests are paced at a 6-second
    minimum interval (~9 requests/minute) process-wide, across all sessions
    and threads, because **Basketball Reference** bans clients that exceed
    ~20 requests/minute.

### Command line

Every endpoint is also available as a CLI subcommand:

```bash
courtside-data list
courtside-data league_per_game_stats --season-end-year 2024
courtside-data team_roster --team-abbreviation BOS --season-end-year 2024 \
    --output-type csv --output-file roster.csv
```

## Enums

Various `enum` values are returned as part of the result set for API methods **_or_** as inputs for various API methods.

They are `import`ed from the `data` path.

=== "League"
    ```python
    from courtside_data.data import League
    ```
    
    !!! note
        Represents the league designated by **Basketball Reference**.
        
        The values are `League.NATIONAL_BASKETBALL_ASSOCIATION`, `League.AMERICAN_BASKETBALL_ASSOCIATION`, and 
        `League.BASKETBALL_ASSOCIATION_OF_AMERICA`.

=== "Location"
    ```python
    from courtside_data.data import Location 
    ```
    
    !!! note
        Represents whether a game was played at home or away. 
        
        The two possible values are `Location.HOME` and `Location.AWAY`
        
=== "Outcome"
    ```python
    from courtside_data.data import Outcome 
    ```
    
    !!! note
        Represents if a game ended in a win or a loss. 
        
        The two possible values are `Outcome.WIN` and `Outcome.LOSS`

=== "OutputType"
    ```python
    from courtside_data.data import OutputType 
    ```
    
    !!! note
        Represents the type of data output.
        
        The three possible values are `OutputType.JSON`, `OutputType.CSV`, and
        `OutputType.DATAFRAME`

=== "OutputWriteOption"
    ```python
    from courtside_data.data import OutputWriteOption 
    ```
    
    !!! note
        Represents Python file modes when outputting data.
        
        The four possible values are `OutputWriteOption.WRITE`, `OutputWriteOption.CREATE_AND_WRITE`, 
        `OutputWriteOption.APPEND`, and `OutputWriteOption.APPEND_AND_WRITE` 

=== "Position"
    ```python
    from courtside_data.data import Position 
    ```
    
    !!! note
        Represents one of the seven positon designations (`Position.POINT_GUARD`, `Position.SHOOTING_GUARD`, `Position.SMALL_FORWARD`, 
        `Position.POWER_FORWARD`, `Position.CENTER`, `Position.FORWARD`, `Position.GUARD`) in **Basketball Reference**

=== "PeriodType"
    ```python
    from courtside_data.data import PeriodType 
    ```
    
    !!! note
        Represents if a period was a quarter (`PeriodType.QUARTER`) or an overtime period (`PeriodType.OVERTIME`)
        
=== "Team"
    ```python
    from courtside_data.data import Team
    ```
    
    !!! note
        Represents a team in the NBA (for example, `Team.BOSTON_CELTICS`).

## Output

The default data returned by API methods are Python objects (e.g. a `list` of `dictionaries`).

All API methods come with `output_type`, `output_file_path`, `output_write_option`, and `json_options` arguments that are
**_optional_**, and by default, are `None`.

These arguments can be used to specify `JSON` / `CSV` / `DataFrame` output; `JSON` and `CSV` output may be written to a file.

Use the `OutputType` `enum` as the `output_type` value to specify `CSV`, `JSON`, or `DATAFRAME` output.

The `output_file_path` argument takes a string and specifies where the result output should be written.

!!! warning
    Specifying an `output_type` of `OutputType.CSV` **requires** an `output_file_path` value.
    
    `JSON` output can be returned by API methods without having to be written to a file.

!!! note
    `OutputType.DATAFRAME` returns a `pandas.DataFrame` and requires the
    `pandas` extra (`pip install "courtside-data[pandas]"`). It does **not**
    support `output_file_path` — use the returned DataFrame's own `to_csv` /
    `to_parquet` methods instead.

Use the `OutputWriteOption` `enum` as the `output_write_option` value to specify if the result output should be written,
or appended to the specified file path (or any of other the Python file mode options).

!!! note
    The default `OutputWriteOption` if it is **_not_** specified (but an `output_file_path` value **_is_** specified) is 
    `OutputWriteOption.WRITE`.

## Errors

All domain errors inherit from `CourtsideDataError`, so library-specific
failures can be caught without swallowing `httpx` transport errors:

```python
from courtside_data import client
from courtside_data.errors import CourtsideDataError, InvalidSeason, RateLimitJailed

try:
    client.league_per_game_stats(season_end_year=2024)
except RateLimitJailed as error:
    print(f"Jailed by Basketball Reference; retry in {error.retry_after:.0f}s")
except CourtsideDataError as error:
    print(error)
```

The concrete errors are `InvalidDate`, `InvalidSeason`, `InvalidPlayer`,
`InvalidTeam`, `InvalidPlayerAndSeason`, `InvalidSearch`, and
`RateLimitJailed`. Per-endpoint mappings (which HTTP status raises which
error) are listed in the [Endpoint Reference](reference.md).

!!! warning
    `RateLimitJailed` means **Basketball Reference** has jailed the session
    (a `Retry-After` longer than 5 minutes). Further calls fail fast until
    the jail expires; the state is persisted to `.cache/courtside/jail.json`
    so restarted processes honor it too. Back off — do not retry in a loop.

## Methods

A representative sample is shown below — see the
[Endpoint Reference](reference.md) for all 50+ typed endpoints.

### Player Box Scores For A Given Day

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.player_box_scores(day=1, month=1, year=2017)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.player_box_scores(day=1, month=1, year=2017, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.player_box_scores(
        day=1, month=1, year=2017, 
        output_type=OutputType.JSON, 
        output_file_path="./1_1_2017_box_scores.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.player_box_scores(
        day=1, month=1, year=2017, 
        output_type=OutputType.CSV, 
        output_file_path="./1_1_2017_box_scores.csv"
    )
    ```

=== "DataFrame"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    frame = client.player_box_scores(day=1, month=1, year=2017, output_type=OutputType.DATAFRAME)
    ```

### Team Box Scores For A Given Day

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.team_box_scores(day=1, month=1, year=2018)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.team_box_scores(day=1, month=1, year=2017, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.team_box_scores(
        day=1, month=1, year=2017, 
        output_type=OutputType.JSON, 
        output_file_path="./1_1_2017_box_scores.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.team_box_scores(
        day=1, month=1, year=2017, 
        output_type=OutputType.CSV, 
        output_file_path="./1_1_2017_box_scores.csv"
    )
    ```
    
### Get Season Schedule

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.season_schedule(season_end_year=2018)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.season_schedule(season_end_year=2018, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType
    
    client.season_schedule(
        season_end_year=2018, 
        output_type=OutputType.JSON, 
        output_file_path="./2017_2018_season.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.season_schedule(
        season_end_year=2018, 
        output_type=OutputType.CSV, 
        output_file_path="./2017_2018_season.csv"
    )
    ```

### Player Season Totals (Basic Statistics)

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.players_season_totals(season_end_year=2018)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.players_season_totals(season_end_year=2018, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType
    
    client.players_season_totals(
        season_end_year=2018, 
        output_type=OutputType.JSON, 
        output_file_path="./2017_2018_player_season_totals.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.players_season_totals(
        season_end_year=2018, 
        output_type=OutputType.CSV, 
        output_file_path="./2017_2018_player_season_totals.csv"
    )
    ```

### Player Season Totals (Advanced Statistics)

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.players_advanced_season_totals(season_end_year=2018)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.players_advanced_season_totals(season_end_year=2018, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType
    
    client.players_advanced_season_totals(
        season_end_year=2018, 
        output_type=OutputType.JSON, 
        output_file_path="./2017_2018_advanced_player_season_totals.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType
    
    client.players_advanced_season_totals(
        season_end_year=2018,
        output_type=OutputType.CSV,
        output_file_path="./2017_2018_advanced_player_season_totals.csv"
    )
    ```

### Play-By-Play

!!! note
    The structure of the API is due to the unique URL pattern that **Basketball Reference** has for getting play-by-play 
    data which depends on the date of the game and the home team.

=== "Python Data Structures"
    ```python
    from courtside_data import client
    from courtside_data.data import Team

    client.play_by_play(home_team=Team.BOSTON_CELTICS, year=2018, month=10, day=16)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType, Team

    client.play_by_play(
        home_team=Team.BOSTON_CELTICS, 
        year=2018, month=10, day=16, 
        output_type=OutputType.JSON
    )
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType, Team
    
    client.play_by_play(
        home_team=Team.BOSTON_CELTICS, 
        year=2018, month=10, day=16, 
        output_type=OutputType.JSON, 
        output_file_path="./2018_10_06_BOS_PBP.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType, Team

    client.play_by_play(
        home_team=Team.BOSTON_CELTICS, 
        year=2018, month=10, day=16, 
        output_type=OutputType.CSV, 
        output_file_path="./2018_10_06_BOS_PBP.csv"
    )
    ```

### Regular Season Player Box Scores

!!! note
    The `player_identifier` is **Basketball Reference's** unique identifier for each player. 
    
    In the case of Russell Westbrook, their `player_identifier` is **`westbru01`**.
    
    You can see this from their player page URL: https://www.basketball-reference.com/players/w/westbru01/gamelog/2020.

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.regular_season_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018
    )
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.regular_season_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.JSON
    )
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.regular_season_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.JSON,
        output_file_path="./2017_2018_russell_westbrook_regular_season_box_scores.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.regular_season_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.CSV, 
        output_file_path="./2017_2018_russell_westbrook_regular_season_box_scores.csv"
    )
    ```


### Playoff Player Box Scores

!!! note
    The `player_identifier` is **Basketball Reference's** unique identifier for each player. 
    
    In the case of Russell Westbrook, their `player_identifier` is **`westbru01`**.
    
    You can see this from their player page URL: https://www.basketball-reference.com/players/w/westbru01/gamelog/2020.

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.playoff_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018
    )
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.playoff_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.JSON
    )
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.playoff_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.JSON,
        output_file_path="./2017_2018_russell_westbrook_playoff_box_scores.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.playoff_player_box_scores(
        player_identifier="westbru01", 
        season_end_year=2018, 
        output_type=OutputType.CSV, 
        output_file_path="./2017_2018_russell_westbrook_playoff_box_scores.csv"
    )
    ```
    
### Search

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.search(term="Ko")
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.search(term="Ko", output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.search(
        term="Ko",
        output_type=OutputType.JSON, 
        output_file_path="./ko_search_results.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.search(
        term="Ko",
        output_type=OutputType.CSV, 
        output_file_path="./ko_search_results.csv"
    )
    ```

### Standings

=== "Python Data Structures"
    ```python
    from courtside_data import client

    client.standings(season_end_year=2019)
    ```
    
=== "JSON"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.standings(season_end_year=2019, output_type=OutputType.JSON)
    ```

=== "JSON to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.standings(
        season_end_year=2019,
        output_type=OutputType.JSON, 
        output_file_path="./2019_standings.json"
    )
    ```
       
=== "CSV to file"
    ```python
    from courtside_data import client
    from courtside_data.data import OutputType

    client.standings(
        season_end_year=2019,
        output_type=OutputType.CSV, 
        output_file_path="./2019_standings.csv"
    )
    ```
