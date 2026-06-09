# **Exhaustive Integration Blueprint for Basketball-Reference Scraping Expansion**

Expanding the capabilities of a lightweight, synchronous, web-scraping package requires a clear approach to DOM parsing and resource handling. The architecture of the scraper utilizes a thin-façade client design, avoiding thick, stateful connection pools or runtime engines like Selenium.1 Instead, it relies on direct, synchronous HTTP execution paired with targeted DOM parsing via lxml and XPath selectors.5  
This integration blueprint details the steps required to support several previously unsupported data categories on Basketball-Reference.com, including player, team, league, draft, leader, and award data.7

## **URL and XPath Mapping Protocol**

Basketball-Reference employs a dual-rendering structure to optimize page performance.1 Primary tables, such as basic season averages, are delivered directly within the active DOM.2 Secondary datasets, such as detailed play-by-play, shooting by distance, and historical salary schedules, are embedded within HTML comments.1 Traditional DOM selectors cannot access commented-out tables because standard browsers and document parsers ignore comment boundaries.1  
To extract commented data without the overhead of browser automation, the scraper must run a comment-isolation routine.1 This routine selects the comment nodes, extracts their text, replaces the comment tags, and reparses the resulting HTML string into an active document fragment.1  
The following table maps the target page configurations, their URL subpaths, their HTML table IDs, their active DOM or commented DOM status, and the precise XPath strings required to isolate the elements:

| Statistical Category | Subpath URL | Table ID | Render State | Target XPath Selector | Key Fields |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Per Game (League-wide)** | /leagues/NBA\_{year}\_per\_game.html 7 | per\_game\_stats 14 | Standard DOM | //table\[@id='per\_game\_stats'\]/tbody/tr\[not(contains(@class,'thead'))\] | Player, Age, Team, Pos, G, GS, rate stats 7 |
| **Per 36 Minutes (League)** | /leagues/NBA\_{year}\_per\_minute.html 7 | per\_minute\_stats 15 | Standard DOM | //table\[@id='per\_minute\_stats'\]/tbody/tr\[not(contains(@class,'thead'))\] | Player rate stats normalized to 36 mins 7 |
| **Per 100 Possessions (League)** | /leagues/NBA\_{year}\_per\_poss.html 7 | per\_poss\_stats 15 | Commented DOM 12 | //comment()\[contains(., 'id="per\_poss\_stats"') or contains(., "id='per\_poss\_stats'")\] | Player rate stats, ORtg, DRtg 7 |
| **Shooting by Distance (League)** | /leagues/NBA\_{year}\_shooting.html 7 | shooting\_stats | Commented DOM 12 | //comment()\[contains(., 'id="shooting\_stats"') or contains(., "id='shooting\_stats'")\] | Dist., % of FGA by distance, Dunks, Corner 3s 7 |
| **Adjusted Shooting (Player)** | /players/{initial}/{player\_id}.html 7 | adj\_shooting | Commented DOM 12 | //comment()\[contains(., 'id="adj\_shooting"') or contains(., "id='adj\_shooting'")\] | FG+, 2P+, 3P+, eFG+, TS+, FG Add, TS Add 7 |
| **Play-by-Play (Player)** | /players/{initial}/{player\_id}.html 7 | pbp | Commented DOM 12 | //comment()\[contains(., 'id="pbp"') or contains(., "id='pbp'")\] | PG%, SG%, OnCourt, On-Off, BadPass, And1 7 |
| **Game Highs (Player)** | /players/{initial}/{player\_id}.html 7 | highs\_totals | Commented DOM 12 | //comment()\[contains(., 'id="highs\_totals"') or contains(., "id='highs\_totals'")\] | Stat category highs, date, opponent 7 |
| **Playoff Series (Player)** | /players/{initial}/{player\_id}.html 7 | playoffs\_per\_game | Standard DOM | //table\[@id='playoffs\_per\_game'\]/tbody/tr\[not(contains(@class,'thead'))\] | Series averages, Opponent, W/L, G 7 |
| **All-Star Game (Player)** | /players/{initial}/{player\_id}.html 7 | all\_star\_g\_stats | Commented DOM 12 | //comment()\[contains(., 'id="all\_star\_g\_stats"') or contains(., "id='all\_star\_g\_stats'")\] | Appearance metrics, PTS, TRB, AST 7 |
| **Similarity Scores (Player)** | /players/{initial}/{player\_id}.html 7 | sim\_career | Commented DOM 12 | //comment()\[contains(., 'id="sim\_career"') or contains(., "id='sim\_career'")\] | Sim Score, Player Name, Career Span 7 |
| **Salaries (Player)** | /players/{initial}/{player\_id}.html 7 | salaries | Commented DOM 2 | //comment()\[contains(., 'id="salaries"') or contains(., "id='salaries'")\] | Season, Team, Lg, Salary 7 |
| **Splits (Player)** | /players/{player\_id}/splits/{year} 7 | splits | Standard DOM | //table\[contains(@id, 'splits')\]/tbody/tr\[not(contains(@class,'thead'))\] | Split category, G, MP, FG%, rate stats 7 |
| **On/Off Court (Player)** | /players/{player\_id}/on-off/{year} 7 | on-off | Standard DOM | //table\[contains(@id, 'on-off')\]/tbody/tr\[not(contains(@class,'thead'))\] | On Court, Off Court differentials 7 |
| **Shot Charts (Player)** | /players/{player\_id}/shooting/{year} 7 | shot\_charts | Standard DOM | //table\[contains(@id, 'shooting')\]/tbody/tr\[not(contains(@class,'thead'))\] | Zones, FGA, FG%, Frequency, Diff 7 |
| **Career Stats (Player)** | /players/{initial}/{player\_id}.html 7 | per\_game | Standard DOM | //table\[@id='per\_game'\]/tbody/tr\[not(contains(@class,'thead'))\] | Full career averages per season 7 |
| **Roster (Team)** | /teams/{team}/{year}.html 7 | roster | Standard DOM | //table\[@id='roster'\]/tbody/tr\[not(contains(@class,'thead'))\] | No., Player, Pos, Height, Weight, College 7 |
| **Injury Report (Team)** | /teams/{team}/{year}.html 7 | injuries | Standard DOM | //table\[@id='injuries'\]/tbody/tr\[not(contains(@class,'thead'))\] | Player, Team, Update Date, Description 4 |
| **Team & Opponent (Team)** | /teams/{team}/{year}.html 7 | team\_and\_opponent | Commented DOM 13 | //comment()\[contains(., 'id="team\_and\_opponent"') or contains(., "id='team\_and\_opponent'")\] | G, MP, FG, FGA, TRB, AST, TOV, PTS 7 |
| **Team Misc / Four Factors** | /teams/{team}/{year}.html 7 | team\_misc | Commented DOM 13 | //comment()\[contains(., 'id="team\_misc"') or contains(., "id='team\_misc'")\] | W, L, MOV, SOS, SRS, ORtg, DRtg, Pace 7 |
| **Team Schedule & Results** | /teams/{team}/{year}\_games.html 7 | games | Standard DOM | //table\[@id='games'\]/tbody/tr\[not(contains(@class,'thead'))\] | G, Date, Opponent, W/L, Tm, Opp, Streak 7 |
| **Team Transactions** | /teams/{team}/{year}\_transactions.html 7 | transactions | Standard DOM | //table\[@id='transactions'\]/tbody/tr\[not(contains(@class,'thead'))\] | Date, Transaction details 7 |
| **Team Splits** | /teams/{team}/{year}/splits/ 7 | team\_splits | Standard DOM | //table\[contains(@id, 'splits')\]/tbody/tr\[not(contains(@class,'thead'))\] | Home/Away, monthly team records 7 |
| **Contracts (Team)** | /contracts/{team}.html 7 | contracts | Standard DOM | //table\[@id='contracts'\]/tbody/tr\[not(contains(@class,'thead'))\] | Player, yearly salary, Guaranteed, Notes 7 |
| **Lineups (Team)** | /teams/{team}/{year}/lineups/ 7 | lineups | Standard DOM | //table\[contains(@id, 'lineups')\]/tbody/tr\[not(contains(@class,'thead'))\] | GP, Poss, MP, Plus-Minus, Net Rtg 7 |
| **Starting Lineups (Team)** | /teams/{team}/{year}\_start.html 7 | starting\_lineups 18 | Standard DOM | //table\[@id='starting\_lineups'\]/tbody/tr\[not(contains(@class,'thead'))\] | Date, Opponent, Starter names, W/L 18 |
| **On/Off Impact (Team)** | /teams/{team}/{year}/on-off/ 7 | on-off | Standard DOM | //table\[contains(@id, 'on-off')\]/tbody/tr\[not(contains(@class,'thead'))\] | Player, MP, On/Off Net Rtg 7 |
| **Opponent Stats (Team)** | /teams/{team}/{year}\_opp.html 7 | opp\_stats | Standard DOM | //table\[contains(@id, 'opp')\]/tbody/tr\[not(contains(@class,'thead'))\] | Opponent shooting, rate averages 7 |
| **Franchise History** | /teams/{team}/ 7 | history | Standard DOM | //table\[@id='history'\]/tbody/tr\[not(contains(@class,'thead'))\] | Season, W, L, SRS, Pace, Playoffs 7 |
| **League Totals** | /leagues/NBA\_{year}\_totals.html 7 | totals\_stats 15 | Standard DOM | //table\[@id='totals\_stats'\]/tbody/tr\[not(contains(@class,'thead'))\] | Raw totals for all active players 7 |
| **Rookie Stats (League)** | /leagues/NBA\_{year}\_rookies.html 7 | rookies 20 | Standard DOM | //table\[@id='rookies'\]/tbody/tr\[not(contains(@class,'thead'))\] | Debut, Age, Totals, rate averages 20 |
| **Playoff Player Per Game** | /leagues/NBA\_{year}\_per\_game.html 7 | playoffs\_per\_game | Commented DOM 12 | //comment()\[contains(., 'id="playoffs\_per\_game"') or contains(., "id='playoffs\_per\_game'")\] | Postseason per-game rate averages 7 |
| **Playoff Player Totals** | /leagues/NBA\_{year}\_totals.html 7 | playoffs\_totals | Commented DOM 12 | //comment()\[contains(., 'id="playoffs\_totals"') or contains(., "id='playoffs\_totals'")\] | Postseason totals for all roster players 7 |
| **Standings by Date** | /leagues/NBA\_{year}\_standings\_by\_date.html 7 | standings | Standard DOM | //table\[contains(@id, 'standings')\]/tbody/tr\[not(contains(@class,'thead'))\] | Date, Team, Conference, GB 7 |
| **Attendance (League)** | /leagues/NBA\_{year}\_attendance.html 7 | attendance | Standard DOM | //table\[@id='attendance'\]/tbody/tr\[not(contains(@class,'thead'))\] | Team, Games, Total, Home Avg, Road Avg 7 |
| **Draft Picks** | /draft/NBA\_{year}.html 7 | stats | Standard DOM | //table\[@id='stats'\]/tbody/tr\[not(contains(@class,'thead'))\] | Pick, Team, Player, College, Career stats 21 |
| **Season Leaders** | /leaders/per\_season.html 7 | leaders | Standard DOM | //table\[contains(@id, 'leaders')\]/tbody/tr\[not(contains(@class,'thead'))\] | Rank, Player, Stat value, Season 7 |
| **Career Leaders** | /leaders/ 7 | leaders | Standard DOM | //table\[contains(@id, 'leaders')\]/tbody/tr\[not(contains(@class,'thead'))\] | Rank, Player, Career stat totals 7 |
| **Playoff Bracket** | /playoffs/NBA\_{year}.html 7 | bracket | Standard DOM | //table\[contains(@id, 'bracket')\]/tbody/tr\[not(contains(@class,'thead'))\] | Round, Series, Team, W, L, Games 7 |
| **Season Awards** | /awards/awards\_{year}.html 7 | awards | Standard DOM | //table\[contains(@id, 'awards')\]/tbody/tr\[not(contains(@class,'thead'))\] | Award, Winner, Team, raw voting metrics 7 |
| **League Transactions** | /leagues/NBA\_{year}\_transactions.html 7 | transactions | Standard DOM | //table\[@id='transactions'\]/tbody/tr\[not(contains(@class,'thead'))\] | Date, transaction description detail 7 |

## **Service-Level Impact Analysis**

Expanding the scraping library requires integrating updates into each decoupled service layer.1 The library enforces a strict architectural boundary.22 client.py exposes module-level helper functions that orchestrate sequential execution across the underlying layers:

┌─────────────────┐     ┌────────────────┐     ┌──────────────────┐     ┌─────────────────┐  
│   client.py     │ ──\> │  HTTPService   │ ──\> │  ParserService   │ ──\> │  OutputService  │  
│  (Thin Facade)  │     │ (Requests/Raw) │     │  (lxml / XPath)  │     │  (JSON / CSV)   │  
└─────────────────┘     └────────────────┘     └──────────────────┘     └─────────────────┘

The code base remains untyped, avoiding all standard type annotations or imports from the typing library.

### **HTTPService Layer**

The fetch engine must dynamically accept variable subpaths and query parameters, then return the raw HTML string.5 Since Basketball-Reference returns a 200 HTTP status even for some missing pages (displaying an internal error message), the helper must inspect the text of the body to detect empty responses.5

Python  
\# http\_service.py  
import requests  
import time

BASE\_URL \= "https://www.basketball-reference.com"

def get\_html\_payload(subpath, query\_params=None):  
    """  
    Constructs the absolute URI and dispatches a synchronous GET request.  
    Enforces a strict browser User-Agent header to prevent block triggers.  
    """  
    absolute\_url \= f"{BASE\_URL}/{subpath.lstrip('/')}"  
    browser\_headers \= {  
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10\_15\_7) "  
                      "AppleWebKit/537.36 (KHTML, like Gecko) "  
                      "Chrome/122.0.0.0 Safari/537.36"  
    }  
      
    response \= requests.get(absolute\_url, params=query\_params, headers=browser\_headers)  
      
    if response.status\_code \== 429:  
        raise RuntimeError("HTTP 429: Rate limit exceeded on Basketball-Reference")  
    elif response.status\_code\!= 200:  
        raise ValueError(f"HTTP Error {response.status\_code}: Failed to resolve {absolute\_url}")  
          
    response\_text \= response.text  
    if "404 \- File or directory not found" in response\_text or "Page Not Found" in response\_text:  
        raise FileNotFoundError(f"Target document path does not exist: {subpath}")  
          
    return response\_text

### **ParserService Layer**

The extraction logic utilizes lxml.html and XPath exclusively.5 To parse both active and commented-out tables, the service defines a routing method extract\_table\_by\_id. This function searches the active DOM for the table; if not found, it evaluates comment nodes to isolate, unwrap, and parse the target table.1  
To handle table layout variations, the parser matches attributes dynamically using the cell's @data-stat identifier rather than parsing by column index.10 This prevents parsing errors caused by empty cells or shifted columns on the platform.10

Python  
\# parser\_service.py  
from lxml import html

def parse\_html\_document(raw\_html):  
    """  
    Parses a raw HTML string into an lxml element tree.  
    """  
    return html.fromstring(raw\_html)

def extract\_table\_by\_id(tree, table\_id):  
    """  
    Locates a table element inside the standard DOM. If the element is hidden,  
    it falls back to scanning and parsing comment nodes.  
    """  
    \# Active DOM lookup  
    active\_tables \= tree.xpath(f"//table\[@id='{table\_id}'\]")  
    if active\_tables:  
        return active\_tables  
          
    \# Comment DOM lookup  
    comment\_nodes \= tree.xpath("//comment()")  
    for comment in comment\_nodes:  
        comment\_content \= str(comment.text).strip()  
        if f'id="{table\_id}"' in comment\_content or f"id='{table\_id}'" in comment\_content:  
            unwrapped\_tree \= html.fromstring(comment\_content)  
            commented\_tables \= unwrapped\_tree.xpath(f"//table\[@id='{table\_id}'\]")  
            if commented\_tables:  
                return commented\_tables  
                  
    raise LookupError(f"Table element with ID '{table\_id}' could not be located in standard or comment DOM.")

def serialize\_table\_rows(table\_element):  
    """  
    Converts a table element's rows into a list of flat dictionaries.  
    Filters out section dividers and non-data header rows.  
    """  
    data\_records \=  
    \# Ignore divider rows that repeat headers midway through tables  
    rows \= table\_element.xpath(".//tbody/tr\[not(contains(@class, 'thead')) and not(contains(@class, 'over\_header'))\]")  
      
    for row in rows:  
        row\_attributes \= {}  
          
        \# Parse data-stat attributes from row header elements (often Player or Date)  
        row\_headers \= row.xpath(".//th")  
        if row\_headers:  
            header\_cell \= row\_headers  
            stat\_name \= header\_cell.get("data-stat")  
            if stat\_name:  
                row\_attributes\[stat\_name\] \= header\_cell.text\_content().strip().replace("\*", "")  
                  
        \# Parse standard cell elements  
        cells \= row.xpath(".//td")  
        for cell in cells:  
            stat\_name \= cell.get("data-stat")  
            if not stat\_name:  
                continue  
                  
            \# Extract plain text or text nested within inner elements (such as links)  
            cell\_text \= cell.text\_content().strip()  
            row\_attributes\[stat\_name\] \= cell\_text  
              
        if row\_attributes:  
            data\_records.append(row\_attributes)  
              
    return data\_records

### **OutputService Layer**

Because different table types contain varying columns, the output service must resolve headers dynamically.25 This implementation scans the keys of the parsed dictionaries to construct headers dynamically, preventing errors when writing datasets with different field structures.25

Python  
\# output\_service.py  
import json  
import csv

def export\_as\_json(records, filepath):  
    """  
    Writes records directly to a file as a formatted JSON array.  
    """  
    with open(filepath, "w", encoding="utf-8") as file:  
        json.dump(records, file, indent=4, ensure\_ascii=False)

def export\_as\_csv(records, filepath):  
    """  
    Infers headers from parsed dictionary keys and writes records to a CSV file.  
    """  
    if not records:  
        return  
          
    \# Gather all unique keys across all records to avoid missing fields  
    field\_headers \= set()  
    for record in records:  
        field\_headers.update(record.keys())  
    sorted\_headers \= sorted(list(field\_headers))  
      
    with open(filepath, "w", encoding="utf-8", newline="") as file:  
        writer \= csv.DictWriter(file, fieldnames=sorted\_headers)  
        writer.writeheader()  
        writer.writerows(records)

### **client.py Facade Layer**

The top-level interface provides module-level functions that coordinate execution through the HTTP, Parser, and Output layers.1 To handle datetime fields across different timezones, the client uses the pytz package to localize dates and times.22

Python  
\# client.py  
import pytz  
from datetime import datetime  
from.http\_service import get\_html\_payload  
from.parser\_service import parse\_html\_document, extract\_table\_by\_id, serialize\_table\_rows  
from.output\_service import export\_as\_json, export\_as\_csv

def get\_player\_salary\_history(player\_id, output\_path=None):  
    """  
    Retrieves the complete historical salary schedule for a specified player.  
    Saves output as CSV or JSON if a file path is provided.  
    """  
    player\_initial \= player\_id.lower()  
    subpath \= f"players/{player\_initial}/{player\_id}.html"  
      
    html\_text \= get\_html\_payload(subpath)  
    document\_tree \= parse\_html\_document(html\_text)  
    salary\_table \= extract\_table\_by\_id(document\_tree, "salaries")  
    records \= serialize\_table\_rows(salary\_table)  
      
    if output\_path:  
        if output\_path.endswith(".json"):  
            export\_as\_json(records, output\_path)  
        elif output\_path.endswith(".csv"):  
            export\_as\_csv(records, output\_path)  
              
    return records

def get\_team\_starting\_lineups(team\_abbreviation, year, output\_path=None):  
    """  
    Retrieves the game-by-game starting lineups for a team in a given season.  
    Localizes date stamps to Eastern Standard Time using pytz.  
    """  
    subpath \= f"teams/{team\_abbreviation.upper()}/{year}\_start.html"  
      
    html\_text \= get\_html\_payload(subpath)  
    document\_tree \= parse\_html\_document(html\_text)  
    lineups\_table \= extract\_table\_by\_id(document\_tree, "starting\_lineups")  
    records \= serialize\_table\_rows(lineups\_table)  
      
    \# Localize raw date string fields using pytz  
    eastern\_tz \= pytz.timezone("US/Eastern")  
    for record in records:  
        raw\_date \= record.get("date")  
        if raw\_date:  
            try:  
                \# Expects a date pattern like YYYY-MM-DD  
                parsed\_dt \= datetime.strptime(raw\_date, "%Y-%m-%d")  
                localized\_dt \= eastern\_tz.localize(parsed\_dt)  
                record\["localized\_timestamp"\] \= localized\_dt.isoformat()  
            except ValueError:  
                record\["localized\_timestamp"\] \= None  
                  
    if output\_path:  
        if output\_path.endswith(".json"):  
            export\_as\_json(records, output\_path)  
        elif output\_path.endswith(".csv"):  
            export\_as\_csv(records, output\_path)  
              
    return records

## **Rate Limiting and Defensive Scraping**

Basketball-Reference enforces a rate-limiting threshold of approximately 20 requests per minute.4 If a client exceeds this limit, the server issues an HTTP 429 response and temporary IP block.  
In a lightweight, connection-pool-free architecture where module-level functions are executed independently, maintaining persistent scheduler threads is not a viable option. Instead, the application must deploy a stateless stateful-slewing logic within the HTTPService layer. This is achieved by storing state in module-level timestamp registers or persisting tracking metadata in cache structures to throttle execution pacing.  
A dynamic jittered delay must be computed prior to executing any synchronous HTTP request. The calculation determines the elapsed duration since the previous network hit and blocks the execution path if the limit threshold is violated.  
This adaptive wait interval is calculated as:  
![][image1]  
where:

* ![][image2] represents the minimum required safety gap between requests (configured to a conservative threshold of ![][image3] seconds).4  
* ![][image4] is the current system epoch time.  
* ![][image5] is the cached epoch time of the prior execution.  
* ![][image6] is a randomized fractional sleep interval (with ![][image7] seconds) added to introduce variance to request patterns.

Python  
\# http\_service.py (Rate Limit Integration)  
import time  
import random  
import os

\# Module-level tracking variable  
\_last\_request\_time \= 0.0

def \_apply\_rate\_limiting():  
    """  
    Calculates and applies an adaptive delay to prevent rate limit triggers.  
    """  
    global \_last\_request\_time  
    current\_time \= time.time()  
    time\_since\_last\_request \= current\_time \- \_last\_request\_time  
      
    target\_interval \= 3.5  
    if time\_since\_last\_request \< target\_interval:  
        random\_jitter \= random.uniform(0.0, 1.2)  
        total\_delay \= (target\_interval \- time\_since\_last\_request) \+ random\_jitter  
        time.sleep(total\_delay)  
          
    \_last\_request\_time \= time.time()

If the scraper encounters an HTTP 429 rate limit error, it must apply an exponential backoff routine to allow the cooling-off window to clear:  
![][image8]  
where:

* ![][image9] is the base backoff time (![][image10] seconds).  
* ![][image11] is the multiplier base constant (![][image12]).  
* ![][image13] represents the count of consecutive rate limit responses encountered.  
* ![][image14] adds a jitter interval (with ![][image15] seconds) to distribute retries.

Python  
\# http\_service.py (Backoff Integration)  
def execute\_request\_with\_backoff(subpath, query\_params=None):  
    """  
    Wraps get\_html\_payload with exponential backoff if rate limits are hit.  
    """  
    max\_retries \= 3  
    retry\_count \= 0  
      
    while retry\_count \< max\_retries:  
        try:  
            \_apply\_rate\_limiting()  
            return get\_html\_payload(subpath, query\_params)  
        except RuntimeError as error:  
            if "HTTP 429" in str(error):  
                retry\_count \+= 1  
                if retry\_count \>= max\_retries:  
                    raise error  
                  
                backoff\_time \= (60.0 \* (2.0 \*\* (retry\_count \- 1))) \+ random.uniform(0.0, 5.0)  
                time.sleep(backoff\_time)  
            else:  
                raise error

To limit live requests during local development, developers can save raw HTML payloads to a local cache folder.5 This decouples parser optimization tasks from live network requests, preventing rate limit blocks.5

## **Testing Plan**

A robust testing suite requires isolating the execution pipeline from live web requests using requests-mock.4 Mock inputs should represent both standard DOM tables and tables nested within HTML comment tags.2 The testing framework uses pytest and pytest-freezer to freeze dates and verify localized calculations without timezone variance.22

Python  
\# test\_suite.py  
import pytest  
import pytz  
from datetime import datetime  
from lxml import html

\# Mock standard DOM input payload  
MOCK\_DOM\_STARTING\_LINEUPS \= """  
\<html\>  
\<body\>  
    \<table id="starting\_lineups"\>  
        \<thead\>  
            \<tr class="thead"\>\<th\>G\</th\>\<th\>Date\</th\>\<th\>Opponent\</th\>\<th\>Starting Lineup\</th\>\</tr\>  
        \</thead\>  
        \<tbody\>  
            \<tr\>  
                \<th data-stat="g"\>1\</th\>  
                \<td data-stat="date"\>2025-10-22\</td\>  
                \<td data-stat="opp\_name"\>Boston Celtics\</td\>  
                \<td data-stat="lineup"\>D. Barlow · J. Embiid · T. Maxey\</td\>  
            \</tr\>  
        \</tbody\>  
    \</table\>  
\</body\>  
\</html\>  
"""

\# Mock commented DOM input payload  
MOCK\_DOM\_PLAYER\_SALARY \= """  
\<html\>  
\<body\>  
    \</body\>  
\</html\>  
"""

def test\_extract\_active\_table():  
    """  
    Verifies that active tables are extracted correctly from mock documents.  
    """  
    from.parser\_service import parse\_html\_document, extract\_table\_by\_id, serialize\_table\_rows  
      
    document\_tree \= parse\_html\_document(MOCK\_DOM\_STARTING\_LINEUPS)  
    table\_element \= extract\_table\_by\_id(document\_tree, "starting\_lineups")  
    records \= serialize\_table\_rows(table\_element)  
      
    assert len(records) \== 1  
    assert records\["g"\] \== "1"  
    assert records\["date"\] \== "2025-10-22"  
    assert records\["opp\_name"\] \== "Boston Celtics"  
    assert records\["lineup"\] \== "D. Barlow · J. Embiid · T. Maxey"

def test\_extract\_commented\_table():  
    """  
    Verifies that commented tables are parsed correctly from HTML comment blocks.  
    """  
    from.parser\_service import parse\_html\_document, extract\_table\_by\_id, serialize\_table\_rows  
      
    document\_tree \= parse\_html\_document(MOCK\_DOM\_PLAYER\_SALARY)  
    table\_element \= extract\_table\_by\_id(document\_tree, "salaries")  
    records \= serialize\_table\_rows(table\_element)  
      
    assert len(records) \== 1  
    assert records\["season"\] \== "2003-04"  
    assert records\["team\_id"\] \== "CLE"  
    assert records\["lg\_id"\] \== "NBA"  
    assert records\["salary"\] \== "$4,018,920"

def test\_client\_orchestration\_and\_timezone\_localization(requests\_mock, freezer):  
    """  
    Validates timezone localization using pytest-freezer and pytz,  
    with network traffic mocked via requests-mock.  
    """  
    from.client import get\_team\_starting\_lineups  
      
    \# Freeze time to prevent execution date drift  
    freezer.move\_to("2026-06-08 14:30:00")  
      
    mock\_url \= "https://www.basketball-reference.com/teams/PHI/2026\_start.html"  
    requests\_mock.get(mock\_url, text=MOCK\_DOM\_STARTING\_LINEUPS, status\_code=200)  
      
    records \= get\_team\_starting\_lineups("PHI", 2026)  
      
    assert len(records) \== 1  
    assert records\["date"\] \== "2025-10-22"  
    \# Verify that the timestamp is localized to US/Eastern  
    assert records\["localized\_timestamp"\] \== "2025-10-22T00:00:00-04:00"

## **Phased Development Plan**

The expansion of the scraping package follows a phased development roadmap to ensure code quality and prevent rate-limiting issues.4

  Phase 1: Local Capture & Mock Prototyping  
  └── Download target HTML pages to act as local test fixtures.  
  └── Construct a pytest harness to run offline test checks.

  Phase 2: Parser Core Extension  
  └── Implement parse\_commented\_table functionality inside ParserService.  
  └── Verify column mapping using cell @data-stat values.

  Phase 3: Rate Limiter & HTTP Assembly  
  └── Integrate adaptive sleep delays and jitter into HTTPService.  
  └── Implement exponential backoff for HTTP 429 status codes.

  Phase 4: Client Interface & Timezone Packaging  
  └── Expose public functions in client.py using untyped schemas.  
  └── Use pytz to localize timestamps for time-sensitive data.  
  └── Configure Hatchling and uv in pyproject.toml for build isolation.

  Phase 5: Validation & Coverage Audit  
  └── Run a complete coverage analysis to verify all parsing code paths.  
  └── Validate the pipeline offline using the mocked test suite.

### **Phase 1: Local Capture and Mock Prototyping**

Download representative HTML target pages manually to use as local test fixtures. This decouples parser construction from live network resources, avoiding rate limit blocks on the target host during development.5 Set up the basic mock test suite using pytest and requests-mock to establish a local-first validation environment.5

### **Phase 2: Parser Core Extension**

Implement the commented table extraction logic inside ParserService.1 Refactor the row extraction parser to use @data-stat attributes, ensuring the parser handles empty values and shifted table headers without throwing indexing errors.10 Validate parser changes against the mock fixtures saved in Phase 1\.

### **Phase 3: Rate Limiter and HTTP Assembly**

Implement rate-limiting protection inside HTTPService. Integrate an adaptive ![][image3] second safety window and randomized delay jitter to match standard user traffic profiles.4 Implement the exponential backoff error-recovery routine to handle potential HTTP 429 responses safely.

### **Phase 4: Client Interface and Timezone Packaging**

Expose public functions in client.py as untyped, module-level entry points.1 Integrate pytz localization for datasets that contain timezone-specific data, such as game starting times.22 Update pyproject.toml to use hatchling as the build backend, and configure project dependencies with uv.22

### **Phase 5: Validation and Coverage Audit**

Execute the mock test suite using pytest and the coverage package.22 Verify that all standard and commented parser branches are fully covered, and run integration trials with mocked endpoints to ensure the package handles edge cases gracefully.5

## **Conclusions and Actionable Recommendations**

To ensure long-term stability and performance as the package expands, developers should implement the following engineering practices:

* **Avoid Browser Runtimes:** Maintain a lightweight, comment-parsing architecture instead of adopting heavy runtimes like Selenium.2 Parsing raw HTML comment blocks in Python consumes less CPU and memory, and keeps the package dependency-free.1  
* **Decouple Development from Live Sites:** Run parser prototyping tasks against local HTML mock files.5 This protects development environments from rate-limiting blocks and ensures test suites remain fast and reliable.5  
* **Isolate Rate Limiting in HTTPService:** Centralize rate-limiting logic inside the HTTP transport service. This guarantees that all public operations in client.py adhere to rate-limiting policies and remain below the server's traffic thresholds.4  
* **Match Attributes Dynamically:** Parse table cells by checking their @data-stat attribute rather than using absolute index values.10 This keeps parsing routines stable even if the platform alters column positions or inserts advertisement rows.10

#### **Works cited**

1. Scraping data off of basketball reference \- Niket Thakkar, accessed June 8, 2026, [https://nthakkar.github.io/bballref/](https://nthakkar.github.io/bballref/)  
2. Using BeautifulSoup to scrape tables within comment tags \- Stack Overflow, accessed June 8, 2026, [https://stackoverflow.com/questions/46305314/using-beautifulsoup-to-scrape-tables-within-comment-tags](https://stackoverflow.com/questions/46305314/using-beautifulsoup-to-scrape-tables-within-comment-tags)  
3. johntomlinsonn/NBA-Game-Predictor: Machine learning Model to predict NBA games with an accuracy of 80%. Includes the process of gathering data , cleaning data, training model, tuning model. \- GitHub, accessed June 8, 2026, [https://github.com/johntomlinsonn/NBA-Game-Predictor](https://github.com/johntomlinsonn/NBA-Game-Predictor)  
4. vishaalagartha/basketball\_reference\_scraper: A python module for scraping static and dynamic content from Basketball Reference. \- GitHub, accessed June 8, 2026, [https://github.com/vishaalagartha/basketball\_reference\_scraper](https://github.com/vishaalagartha/basketball_reference_scraper)  
5. How to go about scraping? : r/learnpython \- Reddit, accessed June 8, 2026, [https://www.reddit.com/r/learnpython/comments/7z9p67/how\_to\_go\_about\_scraping/](https://www.reddit.com/r/learnpython/comments/7z9p67/how_to_go_about_scraping/)  
6. Various \`lxml.html\` techniques explained \- DEV Community, accessed June 8, 2026, [https://dev.to/doridoro/various-lxmlhtml-techniques-explained-1ccg](https://dev.to/doridoro/various-lxmlhtml-techniques-explained-1ccg)  
7. missing\_datapoints.md  
8. chrisfeller/Web\_Scraping\_Basketball\_Reference \- GitHub, accessed June 8, 2026, [https://github.com/chrisfeller/Web\_Scraping\_Basketball\_Reference](https://github.com/chrisfeller/Web_Scraping_Basketball_Reference)  
9. Web Scraping with Python: Analyzing NBA Player Statistics | by Datavisiondallas \- Medium, accessed June 8, 2026, [https://medium.com/@datavisiondallas/web-scraping-with-python-analyzing-nba-player-statistics-0b3d0abb1e6e](https://medium.com/@datavisiondallas/web-scraping-with-python-analyzing-nba-player-statistics-0b3d0abb1e6e)  
10. How to scrape the html page that provides more information while scrolling down by using python lxml \- Stack Overflow, accessed June 8, 2026, [https://stackoverflow.com/questions/57228784/how-to-scrape-the-html-page-that-provides-more-information-while-scrolling-down](https://stackoverflow.com/questions/57228784/how-to-scrape-the-html-page-that-provides-more-information-while-scrolling-down)  
11. In Support of Open Seeding in the NBA, Pt. 2 \- Mark H. White II, PhD, accessed June 8, 2026, [https://www.markhw.com/blog/open-seeding-pt2](https://www.markhw.com/blog/open-seeding-pt2)  
12. How to scrape tables inside a comment tag in html with R? \- Stack Overflow, accessed June 8, 2026, [https://stackoverflow.com/questions/40616357/how-to-scrape-tables-inside-a-comment-tag-in-html-with-r](https://stackoverflow.com/questions/40616357/how-to-scrape-tables-inside-a-comment-tag-in-html-with-r)  
13. How to scrape a specific data table from Basketball reference : r/sheets \- Reddit, accessed June 8, 2026, [https://www.reddit.com/r/sheets/comments/1algy4o/how\_to\_scrape\_a\_specific\_data\_table\_from/](https://www.reddit.com/r/sheets/comments/1algy4o/how_to_scrape_a_specific_data_table_from/)  
14. Scraping the NBA p1- Players/Teams \- DEV Community, accessed June 8, 2026, [https://dev.to/loganwohlers/scraping-the-nba-p1-players-teams-5k5](https://dev.to/loganwohlers/scraping-the-nba-p1-players-teams-5k5)  
15. ziyadmir/nba-player-stats-mcp: A Model Context Protocol server for NBA player statistics from basketball-reference.com \- GitHub, accessed June 8, 2026, [https://github.com/ziyadmir/nba-player-stats-mcp](https://github.com/ziyadmir/nba-player-stats-mcp)  
16. LeBron James Stats | Basketball-Reference.com: Salaries, accessed June 8, 2026, [https://www.basketball-reference.com/tools/share.fcgi?id=QV4xW](https://www.basketball-reference.com/tools/share.fcgi?id=QV4xW)  
17. Building an Automatic NBA Stat Scraper with BeautifulSoup in Python \- Medium, accessed June 8, 2026, [https://medium.com/@jleuschen17/building-an-automatic-nba-stat-scraper-with-beautifulsoup-in-python-45fddd29fa70](https://medium.com/@jleuschen17/building-an-automatic-nba-stat-scraper-with-beautifulsoup-in-python-45fddd29fa70)  
18. 2025-26 Philadelphia 76ers Starting Lineups \- Basketball-Reference.com, accessed June 8, 2026, [https://www.basketball-reference.com/teams/PHI/2026\_start.html](https://www.basketball-reference.com/teams/PHI/2026_start.html)  
19. 2025-26 Minnesota Timberwolves Starting Lineups \- Basketball-Reference.com, accessed June 8, 2026, [https://www.basketball-reference.com/teams/MIN/2026\_start.html](https://www.basketball-reference.com/teams/MIN/2026_start.html)  
20. 2022-23 NBA Rookies \- Basketball-Reference.com, accessed June 8, 2026, [https://www.basketball-reference.com/leagues/NBA\_2023\_rookies.html](https://www.basketball-reference.com/leagues/NBA_2023_rookies.html)  
21. Learning Python: Part 1 \- Scraping and Cleaning the NBA Draft \- Savvas Tjortjoglou, accessed June 8, 2026, [http://savvastjortjoglou.com/nba-draft-part01-scraping.html](http://savvastjortjoglou.com/nba-draft-part01-scraping.html)  
22. basketball\_reference\_web\_scra, accessed June 8, 2026, [https://github.com/jaebradley/basketball\_reference\_web\_scraper/blob/v4/pyproject.toml](https://github.com/jaebradley/basketball_reference_web_scraper/blob/v4/pyproject.toml)  
23. What is the best way to scrape the basketball player's team name? \- Stack Overflow, accessed June 8, 2026, [https://stackoverflow.com/questions/52907935/what-is-the-best-way-to-scrape-the-basketball-players-team-name](https://stackoverflow.com/questions/52907935/what-is-the-best-way-to-scrape-the-basketball-players-team-name)  
24. Scraping NBA game data from basketball-reference.com \- R-bloggers, accessed June 8, 2026, [https://www.r-bloggers.com/2018/12/scraping-nba-game-data-from-basketball-reference-com/](https://www.r-bloggers.com/2018/12/scraping-nba-game-data-from-basketball-reference-com/)  
25. fordfishman/3pt-shooting: Predicting shooting performance of nba players \- GitHub, accessed June 8, 2026, [https://github.com/fordfishman/3pt-shooting](https://github.com/fordfishman/3pt-shooting)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAUCAYAAAB1aeb6AAABOklEQVR4Xu2UsUpDQRBFR4gQEkijICKi+YQgKoJIChUbA9paWUgkEG1ErWwsrEWwsLGytbO18AfUL7D2L3IPO5tsgiLIe6YwFw5vmBl23s7Ortl/1piYENPfQIycXDTU4lXxIo7EgfMpLsSeeBa73eyM1RALbvOFVzHjvg2x6nbmYndFt5vOU+LbFHNu5ybO9d45G4jlrkkL7Yb1gdiSOLUwF0A3MtWieHPieaMpcSlmLZw/tJJ4Jhpq8Tho6bChLfEolq13Gw7FuNgRJxauaxQ2PmIV/26LtlPupZqtiTvxId6dazHvcR4ado7S4ucWrmDBQj7rADY+YuRQ+ErUnL7iP+mr4rSdH47vw43Yd27dRww/xX91e9gBbaPt/HVsHQXq4lisWFi85GDjizFeygcLc5TO0kgj/a06jhI1LoFGCe0AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAABCUlEQVR4Xu3SoU9CURTH8eOYwRkIOB2bG8XBZiEYMRCNkGRWgzCds1nZiDQDwTk3q8UggUR3s0pzg//E7897eFwez2Yg8Ns+gXvPLuede802Wcts4xp994YOtuKiKHcY4xHvOHZJqvhCxZ1g6utZaeMJlyik9n6jDmvYdaf4xEFcFOUCxfRiOjtouiHqS7vL0XgecIsB8m4lmpmcW5hjZhEpWWhA0cFdt5J/O1BzO7LFgZrPDFdxkUcH3eDQf9/jxSXR4reFSxAdOEXLwoXVsee092GLF5DZYRnPFp6L9PBq4ZP3McGZ0xfolhsWRjOy0O284yTqZN6h3tZfj1rRnmr0Z7nU3ibrmB+FBSTMhPCWLAAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAATCAYAAAANgSQ9AAABTUlEQVR4Xu3UyysGURjH8UcuhcjCJSFZWrjlEmLjXiJs5FI2FhI2lLJF2YsUCkvZ2SjKv+b76zzTvK/F27t7j8yvPs00zXnmzDNnjlmWf5gyTKDJRZk2fPlRokz0k2zAEt4snWR53h0RZBKveMK0q8y9IYZU4MXCjxNtctdjqTKC3t8Xc6MOqpM12HFV6MIJttCDXbS6VcxiBms4RD823QaWLdTU+QHafdy628YcOvGJUyvQqFG84wwDrgM3qLPwkGZcWTrJYexjEI/oQyPu3IKFOhdYwZiP1zgdpR7PFupdW6hVMLWW/7NowK2FTT7JuaWTVPfVPd2nByTRefJA7RD3mLcwRruIru85JampMWqWmlF0NOFLLGIKLRY+x7g7xgOO8IFuC59K56IXqMaQhS+k5aLJ6rpeXlT320LXtay0nFS76PyJSWbJUqr8ABgjPPzpKG53AAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAATCAYAAADvXT9EAAABgklEQVR4Xu3VyStFcRQH8K8MmQphIQtDElFCxkimIplXRMaQyMJC2aKsWBgSG+zIzsbCH+f77Zxb3mXx9Hr1bt63Pr3LPe5vOvcB0knnT8mgPioP30j1VNKnf0YqkZx4MU3SG2zimS7l00+v9EjDlO1SPln0DHs5kxG9+K1UEL6RaJLd39qYNaoI30g02mnteD6tULXboEXapjrYwvTzAk25ItrxvyujcafaaddES7BnatdVu+f1jW4TtrBZGvI6XasuqPmRbnqnY9iRBrmmDiqFvbg1dEdj1OXuqYdmaJea6Qb2/2DeKfvUSZdUSyV0C/tikHPYxDWenjNKB1QPG1d+jVYYfiGvqB3WoxpE18HvtNOiBbXABi2EtYUmrl2tcopOZYBevtU++bWc+KdOX4vMpRGvWXVxR7u5ThN0BpvEB+zBeU5fo2qlNtiCFJ3AKWzBorZ5gLWe2msZ1k56dlBzRL10CBt3zusHEXtycSWyEw/aIjJpcBe0RTmxt9P5n/kCjHQ/2rOxHt0AAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAATCAYAAAAQ/xqmAAADKElEQVR4Xu2Yy6vNURTH1w3lHa48Qh4lKaI8rmvAgPIoBm7yTinymKCQUCSlUHSTASUDCglhwsBNRkjMzAwV5W/w/bTXcrafc+/9nXMf6jrf+vQ7+7n2Xnv/1t6/Y9ZQQwNNY8RkZ4IzSAzN8qlTr0aLDWKBaCqU9ZWwtd16bm+I2CvOifmehkNialavlFrEXfFFbHKGiSniknghlv+u3blYmMfiVJbHopG3U3z0dF+rWVwRIz09Sdx0jvuTvDJaKVrFCrE5y58mLlpyek06ITosDS4GiBaJ/Vm6O7Hq07M07duzdH9oi4PY0WyWtQ7a6HllxPgvW3WHsmgsQk1qOLq6/omjI2ZHHeL2RKsMIi+PWLZLPLRK3GfiM8Q6S684oGg7zvPoIz8jivZyW7kGW1rYWZ4eK15ZmgcgnuRR1p1GWAqdbcUCabU4W8zsTmUcTcx+Kl47a8RuccfSBCkn1tMXDoPz4o0lxw4Xh8VWSwfkVYd+aHtd/LAU+16K2Zbshc2w997SmJZ4/kwHjbc0nnAii/HJ/nY0eZR1JQ67G+KI+GxpkXPNFbctLXpplXE0oh4TAUT5E6u0oRxC3Dbyus/FKE/jKHhmqT11WSgWjUVB0V/ex1tLDqUNtnMn4jzqxnjqdTSXAZw4z5ItbEb7UNFWKR21zh29LUv3xNH87rBK3Zh8TDqvG6rm6LBXxtHswg+FOvlidSauh9yW6IeNcc/+vs4VbZVSq3hnaWD5K9ImlmXpnjh6jqXYGBMkxsEDS69fbziasd+3Sujg7aBt2EI8yaOMGLzKn7nor91/s6sJa9TPVVfoaBIHLU0aWsQBsc/L0EJLu+OrwwfBLfFTnBFLvRzWOzjimzhp6XXcIa75MxaMAdM3cZl+j1kafNgLm0V7xM7v4pEzw9txT47DEDEunAbEfZy22MvYuZwLnCG5OHAvWPIJ50x+kwrVdRiGGGic6GMKZb0lbh8Rp/tCe6xyvQvl8yruQJzOB0k1MU7GW011Xe8Gkprtzy/DrsTbymFf6xcrX4anrfr9+r9Rw9H9qLJ/KuGoWkJkfIjV9adSQw011FCN+gVgxaA8M5UG4AAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAATCAYAAADWOo4fAAABNElEQVR4Xu3UvytFYRjA8UcYhAwMKJkkGRTZmCjXoBSDMqH8miSlTBaTVRlkoAyWa6Nkt1Lyh/gH+D49j7rn1z1unVNXvd/6dE7nnOE8nfc9IqHmqR9n2HF90dvN357YEJtuLHq7kLowiyqmYvfiLeAaL7hBj8vsACvxiwU3ghl8SP0B9OvfYwjteMCpy+zfDzCBVwy7shrAm9QfoBdPYstNOxFbRiq1itgGvsWFa4k8Yem+WM2Rt3f+MkBtHXjErks0LjaZPjiPZ6cbrowaHWAd52JLSSU6xLGfT+PSpX2BImpkgGWxvdmGTpdIX37Jz/ex5tIqawn9vtycH7VJHGEQo9h2iXTDXmFDbJjMT1VAi7jDl9ifZcuv6w9EffpRN/E7vmvoSlGptaI7fjEUCoVCef0AAXg44pEDkhsAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,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>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAUCAYAAACaq43EAAABMklEQVR4Xu3UTysFYRTH8aModoqSEDaUyEI2EjchNpSN5G8JCyVZUMhdeAUSC4q9vYWNhTeAV2DtXfj+OmcYtxQ10124v/p0n3nmuffcOc/MmP3HVKEBzT/QOa3JPGUr3Ikn7GAjvOMEi3jE3OfqDDODgRjrU57REnMTGI5xptFV1cZ4K9yn5ibRHuNcon28DQcl53JNo3mLZTzmqjGL1WRRHhnES0j2V9Gen6eOM0/ZCic3VfrGUlT4DgthGjXoMn/kllGHjqBtWUc9urGPsfDtfTCCK7zhNZyZ/4iiwpfmX5IpHGEUvVgz/9PFoAJ95h28QRtOQ7/9IaWtTo63zYuu4BitYcm8a/PmT4jefk1Bnfp1VOgaPWEPQzGnq9/FAy6CrnQz1h6iYF+tVvFKKsk3H7zSMwP7Zpk0AAAAAElFTkSuQmCC>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAATCAYAAABhh3Y4AAABTklEQVR4Xu3SvS8EURQF8CtIyBIfKyuiEBKFhCgUmq02lBSqTZQiOoVEKBQKOl8NEYRstBKFr9DYSqOg8G/4H5zjnjc7M+hkk032JL9k5s19776ZeWb11Gq64RDO5Qg69GwESrAO+5CRdJphFbbgRAqJCqVqzVrhEiZhWD5gXM8uYFS1XGxB0pmGPWiAfrmGbLwoD4+Q0wPiBGYIXqBP9zNwJU0aC9mGNV23yb35+lFW4BPmYVZ2zD/LBLxbsllZuFg8/NTpZmXzOVFY8ApdKqBn86b/3oxvxMFQEIo4kf/tzZLN7qRFYyFn9rPZE0xFFea7v4X2WFF4M57IG/MTySzBpjBjwhThQNc98gCDGvsOf/QuLJpPoPDPmDnYMF+Uux8Q5lgYbuzU/FRzU7RslcMWhQPhJMZPYwjfttcqG/grjeanulN+TVWb1VM7+QLu3UArb9AEBgAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAATCAYAAABC3CftAAAAbklEQVR4XmNgGAmAA4gloTQIgwAzEHPBFJgA8S0gfgLEh6BYGIitgdgCpqgciPmhbC8o9gPiJCDmhClCBiJQ3A3E5mhycMADxdMZIIqxAkEoTkaXQAbGUByJLoEM4qDYBl0CGRClyBCKQY4fKAAA6rQLXW0iHrsAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAA9klEQVR4Xu3SP0tCURzG8Z+gomQ4FIVTIDRISUOTRODQkEhLb6FAegGRQ0NLs29Aina3EFdBaApqqalX0R72/XGeeznetSEHH/gM556H37n/zFZZyhRwgwd5xRVycSlKA0/oY4A1SXOiDR/sdvGFVlxSynjEvtbXuJA0x5hgQ9Yxw1lcUup4QU1r74wkn5Sy8dM/sJfdIId4t8WBU6noWprkkYfoZvaS/N9AH3Qv/jF8XYwLygHebHHgWEpJyX+PS3TEy6c4sjC4jU2p4tnCr+Pp4U7StPGDeeTbwt1s4dPCAc5zjls0LbyeHflT/H1tW3iCVZY9v0uRKxkJNXfjAAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAATCAYAAADMBm6RAAACRUlEQVR4Xu2Vy6tPURTHlzzyDJc88jaQGwPlMb7yHnhMlBADyR0pDJRXIhkIKRNlYuAVipSBAXcgJaJkbm7gb/D9tNbqnPb9natfdNPP+dan3z5777PXd+299vmZtWrVqtc1SSwpO6U5oq/sHAU1+flragrQswkvF4fLTmmXWFt2joKa/HSlRWKPWBGMif7x4ry4LObGMycLr8Q2Mas2f7rYGuQ6E8V8MVXMsGodqI8hfnmeZr4u5HxU+skx4hAv41IFjdogvorF4lxwKsb6xf1gt3mi24PP4rQYEOPEOvHIKiNnxFGxQLwQb803iNP5GAyK9TG2zDwec79EPxwUb8yTL/0A14o1N5knymawaY1i0iox2dwQvLRq10kKUvTDc6tKmoQfiuPmwWCHeGx+irx/L+byzrtgtg1fq4zH2k/FsXgux9EF8/ibxUr7zQnPE0/MT2Rv0ClhSmdC9NdNslGU8pA4ZFXCkOVeJsy7UK6FOiV0TdyNdt1PeppiXpnfgoUxt6MuiivRzjIi4f3mJ5ABMDRgw00yj+Sux7wUiW40N/QnCXNafC/2xXPdT3riXnN1iEl7Z8ztKAaHxAFxNngvLpmXI2Xy2rwCuGcsCuz6bXHCfKc55QfiZEB5bxFrxCfx3XxzOKmfAeZ4/4d4JpaaJ/NBHAluiKtWfbjqftLTHXHLfFNoj3jCKA03icShFF/TsUUf5QVpsFvlCWbMvFp15Vh64p7jY6ZV/xgj6r9L+F8Ryd0M8n73tPifXR3QhlatutAvUiRnJvz7g+EAAAAASUVORK5CYII=>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFwAAAATCAYAAAAd4WrhAAADM0lEQVR4Xu2Yy4uPURjHnwnlbhi5hEhZWIgiYygLlLsFRW6RhVs25JpkIaU0pSbJZSMplwUWSixMEiWJFTtLC6X8B76fzvPM7+39/WbmN+/8fpR5v/XpzDnnOed5z3PO+5z3N2alSv3vahXTnSlimDMy045NUY0Xm8VC0ZLra5bwtcua5495AR/4GpDaxX3xTWwVo5wZ4qp4Lpb3WPcuNuiJOO91Ng9o2yM+eb3ZahOdYqzXp4nb4rSXQFsjhA984XNAOiO6rfKQocXicK6tLy0Qs/1vxkJXpfuvaIeDOIUcmnVe3+LQ1ihl/dWtMuDF1bSAR07HhpwOU8WIGv207XUeW+VuQIxZL2Z5HcXYSZZez5gD2/BFGzbYZvtCwx02eK63TRSvLK0DxSGgjb7+xIbxPNl15jVf3LDku27VE3By+jPxWqx19om7lpzRz13AXATukvPGUoC5F7gjTooxXh5yGHtd/BRXxEsxU1wTX53tYo34YumeYKEvRIclTXZ4nggmG/TZqgNOG319aYK4KTaJFeKepfk3Zo287ZGXdauegCPsWFCI/qdWGUc/IL5MIOwJarelQCJK6kAftmwYmzfabWgLmzjhHywFGzE3Nii+qGiL5ykS8HhTOLXHvC0+CE5YJT2F8IXP3uarKSbqttoB35mpDybg+YVGMCIgWdtQrYDzd8zRX8BJBR+tOuBvrfcTyUEAxsXGIuZlrZz8rAoFvMPSyeEBs9omlmXqgwl4m6XcGYugpA70DTbgPDs8tEpK4aRiQypClEAbfaS21V6GyP/wzip+uH8eWEqJeRVKKS3iqKWB7c4RcdD70CJLu/7d0gc/3BG/xAWx1Pthg6WNgB/inKXXcpW4JXZ7SR2Ym7zN3Kfcdo6l8eR1OC4uit+Wciv+sX9vaTxjgO/suDQRz9Ul5lm6J2CJ9/Gjhbm5Y0KsF0gnZy294Ryiy5Y2c3+PZVKhSzMUXwvQmutrlFjMOC+boQNW/ZkW64pNyYrgr8y1hXirsva8Cfnnxlfe35AS6anTqu+jWiJ4fBQU/QWMD05+Pq8PKZUB/weq959X/Jgpkjojzxf651WpUqVKNUh/ADUyn2aZN5t2AAAAAElFTkSuQmCC>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAATCAYAAADSz14iAAABa0lEQVR4Xu3VyysFURzA8Z88osgzEiXZKUkWShYSK3mVIlsL8spGykphpSQLhI2/gJJHkmTnv/Cn+P46Z+aeM3dc6t47SvOtT82dc+bOzJ3HFUlL+3dt4hUXuEO3PxxWji3si5k74g//fcu4wiIaI2NuYzhCCdpwI2Z+rm0SrWgnUolWqy4yVowWxOzrpw6wbZer8YAhK6txnKHLOsQkeu3naGUYxmwOU2iw8+NaxQk2cIpafzjsWvwTecOE5dWHd7Q460ZxizX5fgf51oEqu6wntJsZ8vr1ieyI+SK3fnxiJrK+EOnBK/2R2u06PVA94Lj0OXJP5FnMD6283HswaBD3qImsD8rn1gqeww8xt67mXpEehzaPY7vchEd0Wl56iS/FbLBureAFexKzQZ7p20fpwz6NOTxJ5uqcOzS9tfX4BrAk5pkKviOrUtSLP0H/iCrCGYVP96Ov0GYx+8+Vjuu8JN6maWlpaQn0BWHPN5o3xqy+AAAAAElFTkSuQmCC>