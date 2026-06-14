# Endpoint Smoke Test Results

- **Started**: 2026-06-14T06:44:26.591811+00:00
- **Seed**: 20260614
- **Elapsed**: 422.1s
- **Total endpoints**: 50
- **OK**: 30
- **Error**: 20
- **Skipped**: 0
- **By category**: {"schema_drift": 19, "domain": 1}

| Endpoint | Status | Rows | Time | Category | Note |
|----------|--------|------|------|----------|------|
| league_per_game_stats | ok | 736 | 1.5s | - | rows=736 |
| league_per_36_minutes | ok | 709 | 7.2s | - | rows=709 |
| league_totals | ok | 652 | 7.0s | - | rows=652 |
| league_per_100_possessions | ok | 652 | 6.4s | - | rows=652 |
| league_shooting | ok | 706 | 7.1s | - | rows=706 |
| league_transactions | ok | 1799 | 5.4s | - | rows=1799 |
| rookie_stats | ok | 85 | 6.7s | - | rows=85 |
| standings | ok | 30 | 6.1s | - | rows=30 |
| standings_by_date | error | - | 13.0s | schema_drift | Schema drift detected for endpoint 'standings_by_date' (https://www.basketball-r… |
| attendance | error | - | 6.4s | schema_drift | Schema drift detected for endpoint 'attendance' (https://www.basketball-referenc… |
| playoff_per_game | ok | 218 | 7.2s | - | rows=218 |
| playoff_totals | ok | 240 | 6.4s | - | rows=240 |
| playoff_bracket | error | - | 6.1s | schema_drift | Schema drift detected for endpoint 'playoff_bracket' (https://www.basketball-ref… |
| draft_picks | error | - | 7.0s | schema_drift | Schema drift detected for endpoint 'draft_picks' (https://www.basketball-referen… |
| season_awards | error | - | 7.0s | schema_drift | Schema drift detected for endpoint 'season_awards' (https://www.basketball-refer… |
| season_leaders | error | - | 6.5s | schema_drift | Schema drift detected for endpoint 'season_leaders' (https://www.basketball-refe… |
| career_leaders | error | - | 6.9s | schema_drift | Schema drift detected for endpoint 'career_leaders' (https://www.basketball-refe… |
| player_career_stats | error | - | 6.9s | schema_drift | Schema drift detected for endpoint 'player_career_stats' (https://www.basketball… |
| player_playoff_series | error | - | 6.7s | schema_drift | Schema drift detected for endpoint 'player_playoff_series' (https://www.basketba… |
| player_adjusted_shooting | error | - | 6.8s | schema_drift | Schema drift detected for endpoint 'player_adjusted_shooting' (https://www.baske… |
| player_play_by_play | error | - | 6.4s | schema_drift | Schema drift detected for endpoint 'player_play_by_play' (https://www.basketball… |
| player_game_highs | ok | 20 | 6.3s | - | rows=20 |
| player_all_star | error | - | 6.2s | schema_drift | Schema drift detected for endpoint 'player_all_star' (https://www.basketball-ref… |
| player_similarity_scores | ok | 11 | 6.3s | - | rows=11 |
| player_salaries | ok | 8 | 6.9s | - | rows=8 |
| player_splits | ok | 66 | 6.6s | - | rows=66 |
| player_on_off | error | - | 7.2s | schema_drift | Schema drift detected for endpoint 'player_on_off' (https://www.basketball-refer… |
| player_shot_charts | ok | 0 | 7.5s | - | rows=0 |
| team_roster | ok | 20 | 7.0s | - | rows=20 |
| team_injury_report | ok | 42 | 6.2s | - | rows=42 |
| team_and_opponent | error | - | 6.8s | schema_drift | Schema drift detected for endpoint 'team_and_opponent' (https://www.basketball-r… |
| team_misc_four_factors | ok | 2 | 6.3s | - | rows=2 |
| team_opponent_stats | error | - | 6.4s | schema_drift | Schema drift detected for endpoint 'team_opponent_stats' (https://www.basketball… |
| team_schedule | ok | 82 | 7.1s | - | rows=82 |
| team_transactions | ok | 37 | 6.5s | - | rows=37 |
| team_splits | error | - | 6.3s | schema_drift | Schema drift detected for endpoint 'team_splits' (https://www.basketball-referen… |
| team_contracts | ok | 20 | 6.1s | - | rows=20 |
| team_lineups | error | - | 7.3s | schema_drift | Schema drift detected for endpoint 'team_lineups' (https://www.basketball-refere… |
| team_starting_lineups | ok | 82 | 6.8s | - | rows=82 |
| team_on_off | error | - | 6.7s | schema_drift | Schema drift detected for endpoint 'team_on_off' (https://www.basketball-referen… |
| franchise_history | error | - | 6.3s | schema_drift | Schema drift detected for endpoint 'franchise_history' (https://www.basketball-r… |
| player_box_scores | ok | 92 | 7.5s | - | rows=92 |
| team_box_scores | ok | 10 | 40.5s | - | rows=10 |
| play_by_play | error | - | 6.7s | domain | Date with year set to 2024, month set to 12, and day set to 25 is invalid |
| regular_season_player_box_scores | ok | 73 | 7.0s | - | rows=73 |
| playoff_player_box_scores | ok | 19 | 7.4s | - | rows=19 |
| season_schedule | ok | 1312 | 59.4s | - | rows=1312 |
| players_season_totals | ok | 715 | 7.6s | - | rows=715 |
| players_advanced_season_totals | ok | 626 | 6.3s | - | rows=626 |
| search | ok | 5 | 6.2s | - | rows=5 |

## Per-endpoint detail

### league_per_game_stats

- **Params**: `{"season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2024_per_game.html`
- **Status**: ok
- **Duration**: 1.456s
- **Row count**: 736
- **Columns**: `[]`

**Sample**:
```json
["name_display='Joel Embiid' positions=[<Position.CENTER: 'CENTER'>] age=29 team=<Team.PHILADELPHIA_76ERS: 'PHILADELPHIA 76ERS'> games_played=39 games_started=39 minutes_played_per_game=33.6 made_field_goals_per_game=11.5 attempted_field_goals_per_game=21.8 field_goal_percentage=0.529 made_three_point_field_goals_per_game=1.4 attempted_three_point_field_goals_per_game=3.6 three_point_field_goal_percentage=0.388 made_two_point_field_goals_per_game=10.2 attempted_two_point_field_goals_per_game=18.
```

### league_per_36_minutes

- **Params**: `{"season_end_year": 2019}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2019_per_minute.html`
- **Status**: ok
- **Duration**: 7.240s
- **Row count**: 709
- **Columns**: `[]`

**Sample**:
```json
["name_display='Bradley Beal' team=<Team.WASHINGTON_WIZARDS: 'WASHINGTON WIZARDS'> positions=[<Position.SHOOTING_GUARD: 'SHOOTING GUARD'>] age=25 games_played=82 games_started=82 minutes_played=3028 made_field_goals_per_36_min=9.1 attempted_field_goals_per_36_min=19.1 field_goal_percentage=0.475 made_three_point_field_goals_per_36_min=2.5 attempted_three_point_field_goals_per_36_min=7.1 three_point_field_goal_percentage=0.351 made_two_point_field_goals_per_36_min=6.6 attempted_two_point_field_go
```

### league_totals

- **Params**: `{"season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2020_totals.html`
- **Status**: ok
- **Duration**: 6.985s
- **Row count**: 652
- **Columns**: `[]`

**Sample**:
```json
["games_played=68 games_started=68 minutes_played=2483 made_field_goals=672 attempted_field_goals=1514 made_three_point_field_goals=299 attempted_three_point_field_goals=843 made_free_throws=692 attempted_free_throws=800 offensive_rebounds=70 defensive_rebounds=376 total_rebounds=446 assists=512 steals=125 blocks=60 turnovers=308 personal_fouls=227 points=2335 name_display='James Harden' team=<Team.HOUSTON_ROCKETS: 'HOUSTON ROCKETS'> positions=[<Position.SHOOTING_GUARD: 'SHOOTING GUARD'>] age=30
```

### league_per_100_possessions

- **Params**: `{"season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2020_per_poss.html`
- **Status**: ok
- **Duration**: 6.439s
- **Row count**: 652
- **Columns**: `[]`

**Sample**:
```json
["name_display='CJ McCollum' team=<Team.PORTLAND_TRAIL_BLAZERS: 'PORTLAND TRAIL BLAZERS'> positions=[<Position.SHOOTING_GUARD: 'SHOOTING GUARD'>] age=28 games_played=70 games_started=70 minutes_played=2556 made_field_goals_per_100_possessions=11.4 attempted_field_goals_per_100_possessions=25.3 field_goal_percentage=0.451 made_three_point_field_goals_per_100_possessions=3.6 attempted_three_point_field_goals_per_100_possessions=9.5 three_point_field_goal_percentage=0.379 made_two_point_field_goals
```

### league_shooting

- **Params**: `{"season_end_year": 2021}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2021_shooting.html`
- **Status**: ok
- **Duration**: 7.124s
- **Row count**: 706
- **Columns**: `[]`

**Sample**:
```json
["name_display='Julius Randle' team=<Team.NEW_YORK_KNICKS: 'NEW YORK KNICKS'> positions=[<Position.POWER_FORWARD: 'POWER FORWARD'>] age=26 games_played=71 games_started=71 minutes_played=2667 field_goal_percentage=0.456 average_shot_distance=14.5 percentage_of_field_goal_attempts_from_two_point_range=0.706 percentage_of_field_goal_attempts_from_zero_to_three_feet=0.162 percentage_of_field_goal_attempts_from_three_to_ten_feet=0.176 percentage_of_field_goal_attempts_from_ten_to_sixteen_feet=0.201 
```

### league_transactions

- **Params**: `{"season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2020_transactions.html`
- **Status**: ok
- **Duration**: 5.382s
- **Row count**: 1799
- **Columns**: `[]`

**Sample**:
```json
["date='July 1, 2019' transaction='The Utah Jazz waived Raul Neto .' from_team_abbreviations=['UTA'] to_team_abbreviations=[] linked_resources=[{'text': 'Utah Jazz', 'href': '/teams/UTA/2020.html', 'from_team_abbreviation': 'UTA', 'to_team_abbreviation': ''}, {'text': 'Raul Neto', 'href': '/players/n/netora01.html', 'from_team_abbreviation': '', 'to_team_abbreviation': ''}]", "date='July 1, 2019' transaction='The New Orleans Pelicans signed Zion Williamson to a multi-year contract.' from_team_ab
```

### rookie_stats

- **Params**: `{"season_end_year": 2023}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2023_rookies.html`
- **Status**: ok
- **Duration**: 6.664s
- **Row count**: 85
- **Columns**: `[]`

**Sample**:
```json
["name_display='Ochai Agbaji' debut=\"Oct 19, '22, UTA vs. DEN\" age=22 years=4 team=None positions=[] games_played=263 minutes_played=5562 made_field_goals=731 attempted_field_goals=1633 made_three_point_field_goals=278 attempted_three_point_field_goals=820 made_free_throws=163 attempted_free_throws=216 offensive_rebounds=224 total_rebounds=720 assists=295 steals=145 blocks=106 turnovers=190 personal_fouls=434 points=1903 field_goal_percentage=0.448 three_point_field_goal_percentage=0.339 free_
```

### standings

- **Params**: `{"season_end_year": 2021}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2021.html`
- **Status**: ok
- **Duration**: 6.148s
- **Row count**: 30
- **Columns**: `[]`

**Sample**:
```json
["team=<Team.PHILADELPHIA_76ERS: 'PHILADELPHIA 76ERS'> wins=49 losses=23 division=<Division.ATLANTIC: 'ATLANTIC'> conference=<Conference.EASTERN: 'EASTERN'>", "team=<Team.BROOKLYN_NETS: 'BROOKLYN NETS'> wins=48 losses=24 division=<Division.ATLANTIC: 'ATLANTIC'> conference=<Conference.EASTERN: 'EASTERN'>"]
```

### standings_by_date

- **Params**: `{"season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_{season_end_year}_standings_by_date_{conference}.html`
- **Status**: error
- **Duration**: 12.996s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 960
- **Message**: Schema drift detected for endpoint 'standings_by_date' (https://www.basketball-reference.com/leagues/NBA_{season_end_year}_standings_by_date_{conference}.html): missing field/alias: 0.team_name_abbr

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 960 validation errors for list[StandingsByDateRow]
0.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.wins
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.losses
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.wins
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.losses
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'WAS (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.wins
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'WAS (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.losses
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'WAS (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'WAS (0-1) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.wins
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'WAS (0-1) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.losses
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'WAS (0-1) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'BRK (0-2) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.wins
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'BRK (0-2) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.losses
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'BRK (0-2) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...9', '15th': 'BRK (0-2)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.wins
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...9', '15th': 'BRK (0-2)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.losses
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...9', '15th': 'BRK (0-2)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'TOR (1-3) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.wins
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'TOR (1-3) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.losses
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'TOR (1-3) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'TOR (1-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.wins
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'TOR (1-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.losses
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'TOR (1-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.wins
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.losses
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.wins
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.losses
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...3', '15th': 'MIA (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.wins
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.losses
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.wins
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.losses
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...3', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.wins
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...3', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.losses
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...3', '15th': 'WAS (1-4)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'WAS (1-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.wins
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'WAS (1-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.losses
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'WAS (1-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.wins
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.losses
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.wins
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.losses
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...3', '15th': 'DET (2-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.wins
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.losses
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.wins
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.losses
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'DET (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.wins
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.losses
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.wins
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.losses
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...)', '15th': 'DET (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.wins
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.losses
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.wins
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.losses
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.wins
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.losses
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...', '15th': 'DET (2-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.wins
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.losses
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.wins
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.losses
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'DET (2-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...', '15th': 'DET (2-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.wins
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...', '15th': 'DET (2-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.losses
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...', '15th': 'DET (2-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.wins
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.losses
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.wins
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.losses
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.wins
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.losses
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'DET (2-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'DET (2-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.wins
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'DET (2-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.losses
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'DET (2-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.wins
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.losses
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.wins
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.losses
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...15th': 'WAS (2-14) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.wins
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.losses
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.wins
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.losses
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'DET (2-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'DET (2-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.wins
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'DET (2-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.losses
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'DET (2-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.wins
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.losses
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.wins
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.losses
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'DET (2-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.wins
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.losses
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.wins
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.losses
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.wins
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.losses
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'DET (2-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.wins
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.losses
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.wins
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.losses
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'DET (2-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'DET (2-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.wins
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'DET (2-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.losses
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'DET (2-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.wins
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.losses
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.wins
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.losses
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'DET (2-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.wins
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.losses
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.wins
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.losses
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'DET (2-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'DET (2-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.wins
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'DET (2-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.losses
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'DET (2-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.wins
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.losses
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.wins
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.losses
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'DET (2-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.wins
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.losses
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.wins
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.losses
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.wins
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.losses
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'DET (2-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.wins
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.losses
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.wins
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.losses
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'DET (2-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.wins
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.losses
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.wins
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.losses
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'DET (2-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.wins
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.losses
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.wins
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.losses
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'DET (2-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.wins
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.losses
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.wins
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.losses
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'DET (2-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.wins
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.losses
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.wins
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.losses
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'DET (3-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.wins
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.losses
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.wins
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.losses
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'DET (3-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.wins
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.losses
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.wins
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.losses
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'DET (3-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.wins
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.losses
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.wins
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.losses
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'DET (3-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.wins
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.losses
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.wins
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.losses
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'DET (3-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'DET (3-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.wins
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'DET (3-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.losses
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'DET (3-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.wins
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.losses
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.wins
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.losses
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'DET (3-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.wins
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.losses
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.wins
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.losses
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.wins
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.losses
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'DET (3-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.wins
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.losses
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.wins
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.losses
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'DET (4-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.wins
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.losses
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.wins
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.losses
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.wins
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.losses
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'DET (4-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.wins
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.losses
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.wins
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.losses
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'DET (4-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.wins
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.losses
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.wins
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.losses
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'DET (4-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.wins
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.losses
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.wins
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.losses
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.wins
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.losses
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'DET (5-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ...', '15th': 'DET (5-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.wins
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ...', '15th': 'DET (5-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.losses
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ...', '15th': 'DET (5-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.wins
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.losses
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.wins
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.losses
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.wins
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.losses
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ...', '15th': 'DET (6-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.wins
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.losses
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.wins
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.losses
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '...', '15th': 'DET (6-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.wins
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.losses
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.wins
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.losses
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '...', '15th': 'DET (6-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.wins
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.losses
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.wins
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.losses
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.wins
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.losses
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '...', '15th': 'DET (6-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '...', '15th': 'DET (7-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.wins
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '...', '15th': 'DET (7-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.losses
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '...', '15th': 'DET (7-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.wins
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.losses
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.wins
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.losses
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '...', '15th': 'DET (8-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.wins
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.losses
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.wins
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.losses
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.wins
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.losses
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ...', '15th': 'DET (8-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ...', '15th': 'DET (8-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.wins
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ...', '15th': 'DET (8-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.losses
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ...', '15th': 'DET (8-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.wins
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.losses
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.wins
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.losses
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ...', '15th': 'DET (8-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.wins
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.losses
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.wins
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.losses
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ...', '15th': 'DET (8-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.wins
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.losses
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.wins
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.losses
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ...', '15th': 'DET (8-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
113.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ...', '15th': 'DET (8-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
113.wins
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ...', '15th': 'DET (8-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
113.losses
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ...', '15th': 'DET (8-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
114.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
114.wins
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
114.losses
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
115.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
115.wins
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
115.losses
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ...15th': 'WAS (9-49) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
116.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ...', '15th': 'WAS (9-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
116.wins
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ...', '15th': 'WAS (9-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
116.losses
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ...', '15th': 'WAS (9-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
117.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
117.wins
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
117.losses
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
118.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
118.wins
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
118.losses
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '...', '15th': 'WAS (9-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
119.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '...15th': 'WAS (9-51) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
119.wins
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '...15th': 'WAS (9-51) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
119.losses
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '...15th': 'WAS (9-51) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
120.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '...', '15th': 'WAS (9-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
120.wins
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '...', '15th': 'WAS (9-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
120.losses
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '...', '15th': 'WAS (9-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
121.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '...15th': 'WAS (9-52) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
121.wins
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '...15th': 'WAS (9-52) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
121.losses
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '...15th': 'WAS (9-52) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
122.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
122.wins
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
122.losses
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
123.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
123.wins
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
123.losses
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '...', '15th': 'WAS (9-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
124.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'WAS (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
124.wins
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'WAS (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
124.losses
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'WAS (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
125.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '...5th': 'WAS (10-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
125.wins
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '...5th': 'WAS (10-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
125.losses
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '...5th': 'WAS (10-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
126.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'DET (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
126.wins
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'DET (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
126.losses
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'DET (10-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
127.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ...5th': 'WAS (11-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
127.wins
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ...5th': 'WAS (11-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
127.losses
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ...5th': 'WAS (11-53) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
128.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
128.wins
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
128.losses
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
129.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
129.wins
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
129.losses
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'WAS (11-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
130.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
130.wins
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
130.losses
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
131.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
131.wins
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
131.losses
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'WAS (11-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
132.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'WAS (11-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
132.wins
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'WAS (11-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
132.losses
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'WAS (11-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
133.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
133.wins
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
133.losses
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
134.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
134.wins
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
134.losses
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'WAS (11-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
135.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
135.wins
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
135.losses
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
136.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
136.wins
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
136.losses
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'WAS (11-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
137.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'WAS (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
137.wins
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'WAS (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
137.losses
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'WAS (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
138.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ...5th': 'WAS (12-58) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
138.wins
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ...5th': 'WAS (12-58) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
138.losses
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ...5th': 'WAS (12-58) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
139.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'DET (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
139.wins
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'DET (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
139.losses
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'DET (12-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
140.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'DET (12-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
140.wins
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'DET (12-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
140.losses
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'DET (12-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
141.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
141.wins
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
141.losses
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
142.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
142.wins
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
142.losses
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'DET (12-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
143.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
143.wins
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
143.losses
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
144.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
144.wins
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
144.losses
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'DET (12-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
145.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
145.wins
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
145.losses
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
146.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
146.wins
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
146.losses
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
147.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
147.wins
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
147.losses
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'DET (13-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
148.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
148.wins
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
148.losses
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
149.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
149.wins
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
149.losses
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'DET (13-62)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
150.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
150.wins
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
150.losses
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
151.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
151.wins
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
151.losses
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'DET (13-63)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
152.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'DET (13-64)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
152.wins
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'DET (13-64)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
152.losses
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'DET (13-64)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
153.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
153.wins
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
153.losses
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
154.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
154.wins
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
154.losses
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'DET (13-65)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
155.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
155.wins
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
155.losses
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
156.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
156.wins
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
156.losses
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'DET (13-66)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
157.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'DET (13-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
157.wins
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'DET (13-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
157.losses
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'DET (13-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
158.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ..., '15th': 'DET (14-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
158.wins
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ..., '15th': 'DET (14-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
158.losses
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ..., '15th': 'DET (14-67)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
159.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'DET (14-68)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
159.wins
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'DET (14-68)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
159.losses
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'DET (14-68)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
160.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
160.wins
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
160.losses
  Field required [type=missing, input_value={'date': 'Oct 24, 2023', ... '14th': '', '15th': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
161.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '15th': 'UTA (0-1) T8'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
161.wins
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '15th': 'UTA (0-1) T8'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
161.losses
  Field required [type=missing, input_value={'date': 'Oct 25, 2023', ... '15th': 'UTA (0-1) T8'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
162.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'UTA (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
162.wins
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'UTA (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
162.losses
  Field required [type=missing, input_value={'date': 'Oct 26, 2023', ... '15th': 'UTA (0-1) T9'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
163.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'POR (0-2) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
163.wins
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'POR (0-2) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
163.losses
  Field required [type=missing, input_value={'date': 'Oct 27, 2023', ...'15th': 'POR (0-2) T12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
164.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'POR (0-2) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
164.wins
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'POR (0-2) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
164.losses
  Field required [type=missing, input_value={'date': 'Oct 28, 2023', ...'15th': 'POR (0-2) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
165.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...'15th': 'POR (0-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
165.wins
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...'15th': 'POR (0-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
165.losses
  Field required [type=missing, input_value={'date': 'Oct 29, 2023', ...'15th': 'POR (0-3) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
166.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
166.wins
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
166.losses
  Field required [type=missing, input_value={'date': 'Oct 30, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
167.team_name_abbr
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
167.wins
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
167.losses
  Field required [type=missing, input_value={'date': 'Oct 31, 2023', ...'15th': 'MEM (0-4) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
168.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
168.wins
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
168.losses
  Field required [type=missing, input_value={'date': 'Nov 1, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
169.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
169.wins
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
169.losses
  Field required [type=missing, input_value={'date': 'Nov 2, 2023', '...)', '15th': 'MEM (0-5)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
170.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
170.wins
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
170.losses
  Field required [type=missing, input_value={'date': 'Nov 3, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
171.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
171.wins
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
171.losses
  Field required [type=missing, input_value={'date': 'Nov 4, 2023', '...)', '15th': 'MEM (0-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
172.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
172.wins
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
172.losses
  Field required [type=missing, input_value={'date': 'Nov 5, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
173.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
173.wins
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
173.losses
  Field required [type=missing, input_value={'date': 'Nov 6, 2023', '...)', '15th': 'MEM (1-6)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
174.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
174.wins
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
174.losses
  Field required [type=missing, input_value={'date': 'Nov 8, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
175.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
175.wins
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
175.losses
  Field required [type=missing, input_value={'date': 'Nov 9, 2023', '...)', '15th': 'MEM (1-7)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
176.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
176.wins
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
176.losses
  Field required [type=missing, input_value={'date': 'Nov 10, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
177.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
177.wins
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
177.losses
  Field required [type=missing, input_value={'date': 'Nov 11, 2023', ...)', '15th': 'MEM (1-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
178.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
178.wins
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
178.losses
  Field required [type=missing, input_value={'date': 'Nov 12, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
179.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
179.wins
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
179.losses
  Field required [type=missing, input_value={'date': 'Nov 13, 2023', ...3', '15th': 'MEM (2-8)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
180.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...)', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
180.wins
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...)', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
180.losses
  Field required [type=missing, input_value={'date': 'Nov 14, 2023', ...)', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
181.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
181.wins
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
181.losses
  Field required [type=missing, input_value={'date': 'Nov 15, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
182.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
182.wins
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
182.losses
  Field required [type=missing, input_value={'date': 'Nov 16, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
183.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
183.wins
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
183.losses
  Field required [type=missing, input_value={'date': 'Nov 17, 2023', ...3', '15th': 'MEM (2-9)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
184.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'SAS (3-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
184.wins
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'SAS (3-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
184.losses
  Field required [type=missing, input_value={'date': 'Nov 18, 2023', ...', '15th': 'SAS (3-10)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
185.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...15th': 'SAS (3-10) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
185.wins
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...15th': 'SAS (3-10) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
185.losses
  Field required [type=missing, input_value={'date': 'Nov 19, 2023', ...15th': 'SAS (3-10) T13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
186.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'SAS (3-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
186.wins
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'SAS (3-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
186.losses
  Field required [type=missing, input_value={'date': 'Nov 20, 2023', ...', '15th': 'SAS (3-11)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
187.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...15th': 'SAS (3-11) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
187.wins
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...15th': 'SAS (3-11) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
187.losses
  Field required [type=missing, input_value={'date': 'Nov 21, 2023', ...15th': 'SAS (3-11) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
188.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'SAS (3-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
188.wins
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'SAS (3-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
188.losses
  Field required [type=missing, input_value={'date': 'Nov 22, 2023', ...', '15th': 'SAS (3-12)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
189.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
189.wins
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
189.losses
  Field required [type=missing, input_value={'date': 'Nov 24, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
190.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
190.wins
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
190.losses
  Field required [type=missing, input_value={'date': 'Nov 25, 2023', ...', '15th': 'SAS (3-13)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
191.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
191.wins
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
191.losses
  Field required [type=missing, input_value={'date': 'Nov 26, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
192.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
192.wins
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
192.losses
  Field required [type=missing, input_value={'date': 'Nov 27, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
193.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
193.wins
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
193.losses
  Field required [type=missing, input_value={'date': 'Nov 28, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
194.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
194.wins
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
194.losses
  Field required [type=missing, input_value={'date': 'Nov 29, 2023', ...', '15th': 'SAS (3-14)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
195.team_name_abbr
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'SAS (3-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
195.wins
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'SAS (3-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
195.losses
  Field required [type=missing, input_value={'date': 'Nov 30, 2023', ...', '15th': 'SAS (3-15)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
196.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
196.wins
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
196.losses
  Field required [type=missing, input_value={'date': 'Dec 1, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
197.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
197.wins
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
197.losses
  Field required [type=missing, input_value={'date': 'Dec 2, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
198.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
198.wins
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
198.losses
  Field required [type=missing, input_value={'date': 'Dec 4, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
199.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
199.wins
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
199.losses
  Field required [type=missing, input_value={'date': 'Dec 5, 2023', '...', '15th': 'SAS (3-16)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
200.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
200.wins
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
200.losses
  Field required [type=missing, input_value={'date': 'Dec 6, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
201.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
201.wins
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
201.losses
  Field required [type=missing, input_value={'date': 'Dec 7, 2023', '...', '15th': 'SAS (3-17)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
202.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'SAS (3-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
202.wins
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'SAS (3-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
202.losses
  Field required [type=missing, input_value={'date': 'Dec 8, 2023', '...', '15th': 'SAS (3-18)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
203.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
203.wins
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
203.losses
  Field required [type=missing, input_value={'date': 'Dec 11, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
204.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
204.wins
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
204.losses
  Field required [type=missing, input_value={'date': 'Dec 12, 2023', ...', '15th': 'SAS (3-19)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
205.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
205.wins
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
205.losses
  Field required [type=missing, input_value={'date': 'Dec 13, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
206.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
206.wins
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
206.losses
  Field required [type=missing, input_value={'date': 'Dec 14, 2023', ...', '15th': 'SAS (3-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
207.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
207.wins
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
207.losses
  Field required [type=missing, input_value={'date': 'Dec 15, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
208.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
208.wins
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
208.losses
  Field required [type=missing, input_value={'date': 'Dec 16, 2023', ...', '15th': 'SAS (4-20)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
209.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
209.wins
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
209.losses
  Field required [type=missing, input_value={'date': 'Dec 17, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
210.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
210.wins
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
210.losses
  Field required [type=missing, input_value={'date': 'Dec 18, 2023', ...', '15th': 'SAS (4-21)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
211.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
211.wins
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
211.losses
  Field required [type=missing, input_value={'date': 'Dec 19, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
212.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
212.wins
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
212.losses
  Field required [type=missing, input_value={'date': 'Dec 20, 2023', ...', '15th': 'SAS (4-22)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
213.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
213.wins
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
213.losses
  Field required [type=missing, input_value={'date': 'Dec 21, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
214.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
214.wins
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
214.losses
  Field required [type=missing, input_value={'date': 'Dec 22, 2023', ...', '15th': 'SAS (4-23)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
215.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
215.wins
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
215.losses
  Field required [type=missing, input_value={'date': 'Dec 23, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
216.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
216.wins
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
216.losses
  Field required [type=missing, input_value={'date': 'Dec 25, 2023', ...', '15th': 'SAS (4-24)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
217.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
217.wins
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
217.losses
  Field required [type=missing, input_value={'date': 'Dec 26, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
218.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
218.wins
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
218.losses
  Field required [type=missing, input_value={'date': 'Dec 27, 2023', ...', '15th': 'SAS (4-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
219.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'SAS (5-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
219.wins
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'SAS (5-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
219.losses
  Field required [type=missing, input_value={'date': 'Dec 28, 2023', ...', '15th': 'SAS (5-25)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
220.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
220.wins
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
220.losses
  Field required [type=missing, input_value={'date': 'Dec 29, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
221.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
221.wins
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
221.losses
  Field required [type=missing, input_value={'date': 'Dec 30, 2023', ...', '15th': 'SAS (5-26)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
222.team_name_abbr
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
222.wins
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
222.losses
  Field required [type=missing, input_value={'date': 'Dec 31, 2023', ...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
223.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
223.wins
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
223.losses
  Field required [type=missing, input_value={'date': 'Jan 1, 2024', '...', '15th': 'SAS (5-27)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
224.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
224.wins
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
224.losses
  Field required [type=missing, input_value={'date': 'Jan 2, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
225.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
225.wins
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
225.losses
  Field required [type=missing, input_value={'date': 'Jan 3, 2024', '...', '15th': 'SAS (5-28)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
226.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
226.wins
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
226.losses
  Field required [type=missing, input_value={'date': 'Jan 4, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
227.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
227.wins
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
227.losses
  Field required [type=missing, input_value={'date': 'Jan 5, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
228.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
228.wins
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
228.losses
  Field required [type=missing, input_value={'date': 'Jan 6, 2024', '...', '15th': 'SAS (5-29)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
229.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
229.wins
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
229.losses
  Field required [type=missing, input_value={'date': 'Jan 7, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
230.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
230.wins
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
230.losses
  Field required [type=missing, input_value={'date': 'Jan 8, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
231.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
231.wins
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
231.losses
  Field required [type=missing, input_value={'date': 'Jan 9, 2024', '...', '15th': 'SAS (5-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
232.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
232.wins
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
232.losses
  Field required [type=missing, input_value={'date': 'Jan 10, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
233.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
233.wins
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
233.losses
  Field required [type=missing, input_value={'date': 'Jan 11, 2024', ...', '15th': 'SAS (6-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
234.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'SAS (7-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
234.wins
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'SAS (7-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
234.losses
  Field required [type=missing, input_value={'date': 'Jan 12, 2024', ...', '15th': 'SAS (7-30)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
235.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
235.wins
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
235.losses
  Field required [type=missing, input_value={'date': 'Jan 13, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
236.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
236.wins
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
236.losses
  Field required [type=missing, input_value={'date': 'Jan 14, 2024', ...', '15th': 'SAS (7-31)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
237.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
237.wins
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
237.losses
  Field required [type=missing, input_value={'date': 'Jan 15, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
238.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
238.wins
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
238.losses
  Field required [type=missing, input_value={'date': 'Jan 16, 2024', ...', '15th': 'SAS (7-32)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
239.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
239.wins
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
239.losses
  Field required [type=missing, input_value={'date': 'Jan 17, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
240.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
240.wins
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
240.losses
  Field required [type=missing, input_value={'date': 'Jan 18, 2024', ...', '15th': 'SAS (7-33)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
241.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'SAS (7-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
241.wins
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'SAS (7-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
241.losses
  Field required [type=missing, input_value={'date': 'Jan 19, 2024', ...', '15th': 'SAS (7-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
242.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
242.wins
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
242.losses
  Field required [type=missing, input_value={'date': 'Jan 20, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
243.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
243.wins
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
243.losses
  Field required [type=missing, input_value={'date': 'Jan 21, 2024', ...', '15th': 'SAS (8-34)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
244.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
244.wins
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
244.losses
  Field required [type=missing, input_value={'date': 'Jan 22, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
245.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
245.wins
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
245.losses
  Field required [type=missing, input_value={'date': 'Jan 23, 2024', ...', '15th': 'SAS (8-35)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
246.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
246.wins
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
246.losses
  Field required [type=missing, input_value={'date': 'Jan 24, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
247.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
247.wins
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
247.losses
  Field required [type=missing, input_value={'date': 'Jan 25, 2024', ...', '15th': 'SAS (8-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
248.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'SAS (9-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
248.wins
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'SAS (9-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
248.losses
  Field required [type=missing, input_value={'date': 'Jan 26, 2024', ...', '15th': 'SAS (9-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
249.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
249.wins
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
249.losses
  Field required [type=missing, input_value={'date': 'Jan 27, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
250.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
250.wins
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
250.losses
  Field required [type=missing, input_value={'date': 'Jan 28, 2024', ..., '15th': 'SAS (10-36)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
251.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
251.wins
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
251.losses
  Field required [type=missing, input_value={'date': 'Jan 29, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
252.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
252.wins
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
252.losses
  Field required [type=missing, input_value={'date': 'Jan 30, 2024', ..., '15th': 'SAS (10-37)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
253.team_name_abbr
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
253.wins
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
253.losses
  Field required [type=missing, input_value={'date': 'Jan 31, 2024', ..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
254.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
254.wins
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
254.losses
  Field required [type=missing, input_value={'date': 'Feb 1, 2024', '..., '15th': 'SAS (10-38)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
255.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '..., '15th': 'SAS (10-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
255.wins
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '..., '15th': 'SAS (10-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
255.losses
  Field required [type=missing, input_value={'date': 'Feb 2, 2024', '..., '15th': 'SAS (10-39)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
256.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
256.wins
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
256.losses
  Field required [type=missing, input_value={'date': 'Feb 3, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
257.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
257.wins
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
257.losses
  Field required [type=missing, input_value={'date': 'Feb 4, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
258.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
258.wins
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
258.losses
  Field required [type=missing, input_value={'date': 'Feb 5, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
259.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
259.wins
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
259.losses
  Field required [type=missing, input_value={'date': 'Feb 6, 2024', '..., '15th': 'SAS (10-40)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
260.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '..., '15th': 'SAS (10-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
260.wins
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '..., '15th': 'SAS (10-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
260.losses
  Field required [type=missing, input_value={'date': 'Feb 7, 2024', '..., '15th': 'SAS (10-41)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
261.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
261.wins
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
261.losses
  Field required [type=missing, input_value={'date': 'Feb 8, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
262.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
262.wins
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
262.losses
  Field required [type=missing, input_value={'date': 'Feb 9, 2024', '..., '15th': 'SAS (10-42)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
263.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
263.wins
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
263.losses
  Field required [type=missing, input_value={'date': 'Feb 10, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
264.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
264.wins
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
264.losses
  Field required [type=missing, input_value={'date': 'Feb 11, 2024', ..., '15th': 'SAS (10-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
265.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
265.wins
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
265.losses
  Field required [type=missing, input_value={'date': 'Feb 12, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
266.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
266.wins
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
266.losses
  Field required [type=missing, input_value={'date': 'Feb 13, 2024', ..., '15th': 'SAS (11-43)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
267.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
267.wins
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
267.losses
  Field required [type=missing, input_value={'date': 'Feb 14, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
268.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
268.wins
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
268.losses
  Field required [type=missing, input_value={'date': 'Feb 15, 2024', ..., '15th': 'SAS (11-44)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
269.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ..., '15th': 'SAS (11-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
269.wins
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ..., '15th': 'SAS (11-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
269.losses
  Field required [type=missing, input_value={'date': 'Feb 22, 2024', ..., '15th': 'SAS (11-45)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
270.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
270.wins
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
270.losses
  Field required [type=missing, input_value={'date': 'Feb 23, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
271.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
271.wins
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
271.losses
  Field required [type=missing, input_value={'date': 'Feb 24, 2024', ..., '15th': 'SAS (11-46)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
272.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
272.wins
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
272.losses
  Field required [type=missing, input_value={'date': 'Feb 25, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
273.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
273.wins
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
273.losses
  Field required [type=missing, input_value={'date': 'Feb 26, 2024', ..., '15th': 'SAS (11-47)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
274.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
274.wins
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
274.losses
  Field required [type=missing, input_value={'date': 'Feb 27, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
275.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
275.wins
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
275.losses
  Field required [type=missing, input_value={'date': 'Feb 28, 2024', ..., '15th': 'SAS (11-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
276.team_name_abbr
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
276.wins
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
276.losses
  Field required [type=missing, input_value={'date': 'Feb 29, 2024', ..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
277.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
277.wins
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
277.losses
  Field required [type=missing, input_value={'date': 'Mar 1, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
278.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
278.wins
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
278.losses
  Field required [type=missing, input_value={'date': 'Mar 2, 2024', '..., '15th': 'SAS (12-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
279.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
279.wins
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
279.losses
  Field required [type=missing, input_value={'date': 'Mar 3, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
280.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
280.wins
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
280.losses
  Field required [type=missing, input_value={'date': 'Mar 4, 2024', '..., '15th': 'SAS (13-48)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
281.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
281.wins
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
281.losses
  Field required [type=missing, input_value={'date': 'Mar 5, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
282.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
282.wins
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
282.losses
  Field required [type=missing, input_value={'date': 'Mar 6, 2024', '..., '15th': 'SAS (13-49)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
283.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
283.wins
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
283.losses
  Field required [type=missing, input_value={'date': 'Mar 7, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
284.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
284.wins
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
284.losses
  Field required [type=missing, input_value={'date': 'Mar 8, 2024', '..., '15th': 'SAS (13-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
285.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
285.wins
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
285.losses
  Field required [type=missing, input_value={'date': 'Mar 9, 2024', '..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
286.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
286.wins
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
286.losses
  Field required [type=missing, input_value={'date': 'Mar 10, 2024', ..., '15th': 'SAS (14-50)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
287.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ..., '15th': 'SAS (14-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
287.wins
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ..., '15th': 'SAS (14-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
287.losses
  Field required [type=missing, input_value={'date': 'Mar 11, 2024', ..., '15th': 'SAS (14-51)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
288.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
288.wins
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
288.losses
  Field required [type=missing, input_value={'date': 'Mar 12, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
289.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
289.wins
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
289.losses
  Field required [type=missing, input_value={'date': 'Mar 13, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
290.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
290.wins
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
290.losses
  Field required [type=missing, input_value={'date': 'Mar 14, 2024', ..., '15th': 'SAS (14-52)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
291.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
291.wins
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
291.losses
  Field required [type=missing, input_value={'date': 'Mar 15, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
292.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
292.wins
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
292.losses
  Field required [type=missing, input_value={'date': 'Mar 16, 2024', ..., '15th': 'SAS (14-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
293.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
293.wins
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
293.losses
  Field required [type=missing, input_value={'date': 'Mar 17, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
294.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
294.wins
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
294.losses
  Field required [type=missing, input_value={'date': 'Mar 18, 2024', ..., '15th': 'SAS (15-53)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
295.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
295.wins
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
295.losses
  Field required [type=missing, input_value={'date': 'Mar 19, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
296.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
296.wins
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
296.losses
  Field required [type=missing, input_value={'date': 'Mar 20, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
297.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
297.wins
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
297.losses
  Field required [type=missing, input_value={'date': 'Mar 21, 2024', ..., '15th': 'SAS (15-54)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
298.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ..., '15th': 'SAS (15-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
298.wins
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ..., '15th': 'SAS (15-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
298.losses
  Field required [type=missing, input_value={'date': 'Mar 22, 2024', ..., '15th': 'SAS (15-55)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
299.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
299.wins
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
299.losses
  Field required [type=missing, input_value={'date': 'Mar 23, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
300.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
300.wins
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
300.losses
  Field required [type=missing, input_value={'date': 'Mar 24, 2024', ..., '15th': 'SAS (15-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
301.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
301.wins
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
301.losses
  Field required [type=missing, input_value={'date': 'Mar 25, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
302.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
302.wins
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
302.losses
  Field required [type=missing, input_value={'date': 'Mar 26, 2024', ..., '15th': 'SAS (16-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
303.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
303.wins
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
303.losses
  Field required [type=missing, input_value={'date': 'Mar 27, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
304.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
304.wins
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
304.losses
  Field required [type=missing, input_value={'date': 'Mar 28, 2024', ..., '15th': 'SAS (17-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
305.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
305.wins
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
305.losses
  Field required [type=missing, input_value={'date': 'Mar 29, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
306.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
306.wins
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
306.losses
  Field required [type=missing, input_value={'date': 'Mar 30, 2024', ..., '15th': 'SAS (18-56)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
307.team_name_abbr
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
307.wins
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
307.losses
  Field required [type=missing, input_value={'date': 'Mar 31, 2024', ..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
308.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
308.wins
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
308.losses
  Field required [type=missing, input_value={'date': 'Apr 1, 2024', '..., '15th': 'SAS (18-57)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
309.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
309.wins
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
309.losses
  Field required [type=missing, input_value={'date': 'Apr 2, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
310.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
310.wins
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
310.losses
  Field required [type=missing, input_value={'date': 'Apr 3, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
311.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
311.wins
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
311.losses
  Field required [type=missing, input_value={'date': 'Apr 4, 2024', '..., '15th': 'SAS (18-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
312.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
312.wins
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
312.losses
  Field required [type=missing, input_value={'date': 'Apr 5, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
313.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
313.wins
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
313.losses
  Field required [type=missing, input_value={'date': 'Apr 6, 2024', '..., '15th': 'SAS (19-58)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
314.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'SAS (19-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
314.wins
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'SAS (19-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
314.losses
  Field required [type=missing, input_value={'date': 'Apr 7, 2024', '..., '15th': 'SAS (19-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
315.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'SAS (20-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
315.wins
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'SAS (20-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
315.losses
  Field required [type=missing, input_value={'date': 'Apr 9, 2024', '..., '15th': 'SAS (20-59)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
316.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
316.wins
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
316.losses
  Field required [type=missing, input_value={'date': 'Apr 10, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
317.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
317.wins
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
317.losses
  Field required [type=missing, input_value={'date': 'Apr 11, 2024', ..., '15th': 'SAS (20-60)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
318.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ...5th': 'SAS (21-60) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
318.wins
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ...5th': 'SAS (21-60) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
318.losses
  Field required [type=missing, input_value={'date': 'Apr 12, 2024', ...5th': 'SAS (21-60) T14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
319.team_name_abbr
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'POR (21-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
319.wins
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'POR (21-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
319.losses
  Field required [type=missing, input_value={'date': 'Apr 14, 2024', ..., '15th': 'POR (21-61)'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\league.py", line 225, in standings_by_date
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'standings_by_date' (https://www.basketball-reference.com/leagues/NBA_{season_end_year}_standings_by_date_{conference}.html): missing field/alias: 0.team_name_abbr
```

### attendance

- **Params**: `{"season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2020.html`
- **Status**: error
- **Duration**: 6.405s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 30
- **Message**: Schema drift detected for endpoint 'attendance' (https://www.basketball-reference.com/leagues/NBA_2020.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 30 validation errors for list[AttendanceRow]
0.team
  Value error, Unknown team abbreviation: 'Milwaukee Bucks' [type=value_error, input_value='Milwaukee Bucks', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.team
  Value error, Unknown team abbreviation: 'Boston Celtics' [type=value_error, input_value='Boston Celtics', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.team
  Value error, Unknown team abbreviation: 'Los Angeles Clippers' [type=value_error, input_value='Los Angeles Clippers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.team
  Value error, Unknown team abbreviation: 'Toronto Raptors' [type=value_error, input_value='Toronto Raptors', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.team
  Value error, Unknown team abbreviation: 'Los Angeles Lakers' [type=value_error, input_value='Los Angeles Lakers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.team
  Value error, Unknown team abbreviation: 'Dallas Mavericks' [type=value_error, input_value='Dallas Mavericks', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.team
  Value error, Unknown team abbreviation: 'Miami Heat' [type=value_error, input_value='Miami Heat', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.team
  Value error, Unknown team abbreviation: 'Houston Rockets' [type=value_error, input_value='Houston Rockets', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.team
  Value error, Unknown team abbreviation: 'Utah Jazz' [type=value_error, input_value='Utah Jazz', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.team
  Value error, Unknown team abbreviation: 'Philadelphia 76ers' [type=value_error, input_value='Philadelphia 76ers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.team
  Value error, Unknown team abbreviation: 'Denver Nuggets' [type=value_error, input_value='Denver Nuggets', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.team
  Value error, Unknown team abbreviation: 'Indiana Pacers' [type=value_error, input_value='Indiana Pacers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.team
  Value error, Unknown team abbreviation: 'Oklahoma City Thunder' [type=value_error, input_value='Oklahoma City Thunder', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.team
  Value error, Unknown team abbreviation: 'Phoenix Suns' [type=value_error, input_value='Phoenix Suns', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.team
  Value error, Unknown team abbreviation: 'Brooklyn Nets' [type=value_error, input_value='Brooklyn Nets', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.team
  Value error, Unknown team abbreviation: 'Orlando Magic' [type=value_error, input_value='Orlando Magic', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.team
  Value error, Unknown team abbreviation: 'San Antonio Spurs' [type=value_error, input_value='San Antonio Spurs', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.team
  Value error, Unknown team abbreviation: 'Memphis Grizzlies' [type=value_error, input_value='Memphis Grizzlies', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.team
  Value error, Unknown team abbreviation: 'Portland Trail Blazers' [type=value_error, input_value='Portland Trail Blazers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.team
  Value error, Unknown team abbreviation: 'New Orleans Pelicans' [type=value_error, input_value='New Orleans Pelicans', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.team
  Value error, Unknown team abbreviation: 'Sacramento Kings' [type=value_error, input_value='Sacramento Kings', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.team
  Value error, Unknown team abbreviation: 'Chicago Bulls' [type=value_error, input_value='Chicago Bulls', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.team
  Value error, Unknown team abbreviation: 'Detroit Pistons' [type=value_error, input_value='Detroit Pistons', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.team
  Value error, Unknown team abbreviation: 'Minnesota Timberwolves' [type=value_error, input_value='Minnesota Timberwolves', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.team
  Value error, Unknown team abbreviation: 'Washington Wizards' [type=value_error, input_value='Washington Wizards', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.team
  Value error, Unknown team abbreviation: 'New York Knicks' [type=value_error, input_value='New York Knicks', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.team
  Value error, Unknown team abbreviation: 'Charlotte Hornets' [type=value_error, input_value='Charlotte Hornets', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.team
  Value error, Unknown team abbreviation: 'Atlanta Hawks' [type=value_error, input_value='Atlanta Hawks', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.team
  Value error, Unknown team abbreviation: 'Cleveland Cavaliers' [type=value_error, input_value='Cleveland Cavaliers', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.team
  Value error, Unknown team abbreviation: 'Golden State Warriors' [type=value_error, input_value='Golden State Warriors', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\league.py", line 250, in attendance
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'attendance' (https://www.basketball-reference.com/leagues/NBA_2020.html): missing field/alias: unknown
```

### playoff_per_game

- **Params**: `{"season_end_year": 2023}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2023_per_game.html`
- **Status**: ok
- **Duration**: 7.193s
- **Row count**: 218
- **Columns**: `[]`

**Sample**:
```json
["name_display='Kawhi Leonard' positions=[<Position.SMALL_FORWARD: 'SMALL FORWARD'>] age=31 team=<Team.LOS_ANGELES_CLIPPERS: 'LOS ANGELES CLIPPERS'> games_played=2 games_started=2 minutes_played_per_game=40.0 made_field_goals_per_game=12.0 attempted_field_goals_per_game=22.0 field_goal_percentage=0.545 made_three_point_field_goals_per_game=3.0 attempted_three_point_field_goals_per_game=5.0 three_point_field_goal_percentage=0.6 made_two_point_field_goals_per_game=9.0 attempted_two_point_field_goa
```

### playoff_totals

- **Params**: `{"season_end_year": 2021}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2021_totals.html`
- **Status**: ok
- **Duration**: 6.416s
- **Row count**: 240
- **Columns**: `[]`

**Sample**:
```json
["games_played=21 games_started=21 minutes_played=800 made_field_goals=250 attempted_field_goals=439 made_three_point_field_goals=13 attempted_three_point_field_goals=70 made_free_throws=121 attempted_free_throws=206 offensive_rebounds=59 defensive_rebounds=210 total_rebounds=269 assists=108 steals=21 blocks=25 turnovers=64 personal_fouls=61 points=634 name_display='Giannis Antetokounmpo' team=<Team.MILWAUKEE_BUCKS: 'MILWAUKEE BUCKS'> positions=[<Position.POWER_FORWARD: 'POWER FORWARD'>] age=26 
```

### playoff_bracket

- **Params**: `{"season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/playoffs/NBA_2020.html`
- **Status**: error
- **Duration**: 6.084s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 339
- **Message**: Schema drift detected for endpoint 'playoff_bracket' (https://www.basketball-reference.com/playoffs/NBA_2020.html): missing field/alias: 0.series

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 339 validation errors for list[PlayoffBracketRow]
0.series
  Field required [type=missing, input_value={'col_1': 'Finals', 'col_...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.team
  Field required [type=missing, input_value={'col_1': 'Finals', 'col_...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.result
  Field required [type=missing, input_value={'col_1': 'Finals', 'col_...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Wed, Se...i Heat', 'col_37': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Wed, Se...i Heat', 'col_37': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Wed, Se...i Heat', 'col_37': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '116'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '116'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '116'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...mi Heat', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...mi Heat', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...mi Heat', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Se... Heat', 'col_37': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Se... Heat', 'col_37': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Se... Heat', 'col_37': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '112'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '112'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '112'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...eltics', 'col_6': '121'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...eltics', 'col_6': '121'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...eltics', 'col_6': '121'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...i Heat', 'col_6': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...i Heat', 'col_6': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...i Heat', 'col_6': '125'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '126'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '126'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Lakers', 'col_6': '126'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...uggets', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...uggets', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...uggets', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Sun, Au...aptors', 'col_43': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Sun, Au...aptors', 'col_43': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Sun, Au...aptors', 'col_43': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Raptors', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Raptors', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Raptors', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Raptors', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Raptors', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Raptors', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...eltics', 'col_6': '103'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...eltics', 'col_6': '103'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...eltics', 'col_6': '103'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Celtics', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Celtics', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Celtics', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Raptors', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Raptors', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Raptors', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...eltics', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...eltics', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...eltics', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.series
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Raptors', 'col_6': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.team
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Raptors', 'col_6': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.result
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Raptors', 'col_6': '87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Bucks', 'col_31': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Bucks', 'col_31': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Bucks', 'col_31': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...i Heat', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...e Bucks', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...e Bucks', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...e Bucks', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Thu, Se...ippers', 'col_43': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Thu, Se...ippers', 'col_43': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Thu, Se...ippers', 'col_43': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '120'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '120'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '120'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...uggets', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Nuggets', 'col_6': '85'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Nuggets', 'col_6': '85'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...Nuggets', 'col_6': '85'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...uggets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...uggets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...uggets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.series
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...lippers', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.team
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...lippers', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.result
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...lippers', 'col_6': '89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Fri, Se...akers', 'col_31': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ockets', 'col_6': '102'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ockets', 'col_6': '102'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ockets', 'col_6': '102'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ockets', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ockets', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ockets', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...76ers', 'col_25': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...76ers', 'col_25': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...76ers', 'col_25': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '109'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '109'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...eltics', 'col_6': '109'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '128'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '128'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...eltics', 'col_6': '128'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...a 76ers', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...a 76ers', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...a 76ers', 'col_6': '94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... 76ers', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... 76ers', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... 76ers', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...i Heat', 'col_25': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...i Heat', 'col_25': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...i Heat', 'col_25': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Pacers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Pacers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...Pacers', 'col_6': '101'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Pacers', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Pacers', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Pacers', 'col_6': '100'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...i Heat', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...mi Heat', 'col_6': '99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...Bucks', 'col_31': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...Bucks', 'col_31': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...Bucks', 'col_31': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '110'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '110'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Bucks', 'col_6': '110'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_... Bucks', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_... Magic', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_... Magic', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_... Magic', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... Magic', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... Magic', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_... Magic', 'col_6': '106'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_... Bucks', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_... Bucks', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_... Bucks', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.series
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.team
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.result
  Field required [type=missing, input_value={'col_1': 'Eastern Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Nets', 'col_25': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Nets', 'col_25': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au... Nets', 'col_25': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...aptors', 'col_6': '134'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...aptors', 'col_6': '134'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...aptors', 'col_6': '134'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...aptors', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...aptors', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...aptors', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...yn Nets', 'col_6': '92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...yn Nets', 'col_6': '92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...yn Nets', 'col_6': '92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...n Nets', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...n Nets', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...n Nets', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...uggets', 'col_43': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...uggets', 'col_43': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...uggets', 'col_43': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...uggets', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...uggets', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...uggets', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...uggets', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...uggets', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...uggets', 'col_6': '105'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...h Jazz', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...h Jazz', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...h Jazz', 'col_6': '124'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...h Jazz', 'col_6': '129'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...h Jazz', 'col_6': '129'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...h Jazz', 'col_6': '129'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...uggets', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...uggets', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...uggets', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...h Jazz', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...h Jazz', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...h Jazz', 'col_6': '107'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.series
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Nuggets', 'col_6': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.team
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Nuggets', 'col_6': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.result
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...Nuggets', 'col_6': '80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...ckets', 'col_43': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...ckets', 'col_43': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...ckets', 'col_43': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ockets', 'col_6': '123'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ockets', 'col_6': '123'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ockets', 'col_6': '123'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ockets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ockets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ockets', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...hunder', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...hunder', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...hunder', 'col_6': '119'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...hunder', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...hunder', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...hunder', 'col_6': '117'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ockets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ockets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ockets', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...hunder', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...hunder', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...hunder', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.series
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...ockets', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.team
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...ockets', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.result
  Field required [type=missing, input_value={'col_1': 'Game 7', 'col_...ockets', 'col_6': '104'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...ericks', 'col_37': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...ericks', 'col_37': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Mon, Au...ericks', 'col_37': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_...ippers', 'col_6': '118'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...ippers', 'col_6': '114'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ericks', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ericks', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...ericks', 'col_6': '122'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ericks', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ericks', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...ericks', 'col_6': '135'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '154'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '154'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...ippers', 'col_6': '154'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.series
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...vericks', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.team
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...vericks', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.result
  Field required [type=missing, input_value={'col_1': 'Game 6', 'col_...vericks', 'col_6': '97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.series
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.team
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.result
  Field required [type=missing, input_value={'col_1': 'Western Confer...'col_3': 'Series Stats'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.series
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...akers', 'col_31': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.team
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...akers', 'col_31': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.result
  Field required [type=missing, input_value={'col_1': 'Game 1 Tue, Au...akers', 'col_31': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.series
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.team
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.result
  Field required [type=missing, input_value={'col_1': 'Game 1', 'col_... Lakers', 'col_6': '93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.series
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.team
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.result
  Field required [type=missing, input_value={'col_1': 'Game 2', 'col_...Lakers', 'col_6': '111'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.series
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...lazers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.team
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...lazers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.result
  Field required [type=missing, input_value={'col_1': 'Game 3', 'col_...lazers', 'col_6': '108'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.series
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...lazers', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.team
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...lazers', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.result
  Field required [type=missing, input_value={'col_1': 'Game 4', 'col_...lazers', 'col_6': '115'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.series
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.team
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.result
  Field required [type=missing, input_value={'col_1': 'Game 5', 'col_...Lakers', 'col_6': '131'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\playoffs.py", line 74, in playoff_bracket
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'playoff_bracket' (https://www.basketball-reference.com/playoffs/NBA_2020.html): missing field/alias: 0.series
```

### draft_picks

- **Params**: `{"season_end_year": 2022}`
- **URL**: `https://www.basketball-reference.com/draft/NBA_2022.html`
- **Status**: error
- **Duration**: 6.995s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 4
- **Message**: Schema drift detected for endpoint 'draft_picks' (https://www.basketball-reference.com/draft/NBA_2022.html): missing field/alias: 58.pick_overall

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 4 validation errors for list[DraftPicksRow]
58.pick_overall
  Field required [type=missing, input_value={'skip': 'Milwaukee Bucks...eir Second Round pick.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.player
  Field required [type=missing, input_value={'skip': 'Milwaukee Bucks...eir Second Round pick.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.pick_overall
  Field required [type=missing, input_value={'skip': 'Miami Heat forf...eir Second Round pick.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.player
  Field required [type=missing, input_value={'skip': 'Miami Heat forf...eir Second Round pick.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\draft.py", line 24, in draft_picks
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'draft_picks' (https://www.basketball-reference.com/draft/NBA_2022.html): missing field/alias: 58.pick_overall
```

### season_awards

- **Params**: `{"season_end_year": 2018}`
- **URL**: `https://www.basketball-reference.com/awards/awards_2018.html`
- **Status**: error
- **Duration**: 7.015s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 2
- **Message**: Schema drift detected for endpoint 'season_awards' (https://www.basketball-reference.com/awards/awards_2018.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 2 validation errors for list[SeasonAwardsRow]
9.rank
  Value error, Invalid integer value: '10T' [type=value_error, input_value='10T', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.rank
  Value error, Invalid integer value: '10T' [type=value_error, input_value='10T', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\draft.py", line 49, in season_awards
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'season_awards' (https://www.basketball-reference.com/awards/awards_2018.html): missing field/alias: unknown
```

### season_leaders

- **Params**: `{}`
- **URL**: `https://www.basketball-reference.com/leaders/per_season.html`
- **Status**: error
- **Duration**: 6.457s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 500
- **Message**: Schema drift detected for endpoint 'season_leaders' (https://www.basketball-reference.com/leaders/per_season.html): missing field/alias: 0.value

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 500 validation errors for list[SeasonLeadersRow]
0.rank
  Value error, Invalid integer value: '1.' [type=value_error, input_value='1.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.value
  Field required [type=missing, input_value={'rank': '1.', 'player': ...5', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.rank
  Value error, Invalid integer value: '2.' [type=value_error, input_value='2.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.value
  Field required [type=missing, input_value={'rank': '2.', 'player': ...5', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.rank
  Value error, Invalid integer value: '3.' [type=value_error, input_value='3.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.value
  Field required [type=missing, input_value={'rank': '3.', 'player': ...8', 'season': '1961-62'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.rank
  Value error, Invalid integer value: '4.' [type=value_error, input_value='4.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.value
  Field required [type=missing, input_value={'rank': '4.', 'player': ...5', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.rank
  Value error, Invalid integer value: '5.' [type=value_error, input_value='5.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.value
  Field required [type=missing, input_value={'rank': '5.', 'player': ...4', 'season': '2024-25'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.rank
  Value error, Invalid integer value: '6.' [type=value_error, input_value='6.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.value
  Field required [type=missing, input_value={'rank': '6.', 'player': ...6', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.rank
  Value error, Invalid integer value: '7.' [type=value_error, input_value='7.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.value
  Field required [type=missing, input_value={'rank': '7.', 'player': ...2', 'season': '1962-63'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.rank
  Value error, Invalid integer value: '8.' [type=value_error, input_value='8.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.value
  Field required [type=missing, input_value={'rank': '8.', 'player': ...1', 'season': '1987-88'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.rank
  Value error, Invalid integer value: '9.' [type=value_error, input_value='9.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.value
  Field required [type=missing, input_value={'rank': '9.', 'player': ...7', 'season': '2008-09'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.rank
  Value error, Invalid integer value: '10.' [type=value_error, input_value='10.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.value
  Field required [type=missing, input_value={'rank': '10.', 'player':...3', 'season': '1963-64'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.rank
  Value error, Invalid integer value: '11.' [type=value_error, input_value='11.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.value
  Field required [type=missing, input_value={'rank': '11.', 'player':...3', 'season': '1990-91'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.rank
  Value error, Invalid integer value: '12.' [type=value_error, input_value='12.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.value
  Field required [type=missing, input_value={'rank': '12.', 'player':...9', 'season': '2012-13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.rank
  Value error, Invalid integer value: '13.' [type=value_error, input_value='13.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.value
  Field required [type=missing, input_value={'rank': '13.', 'player':...1', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.rank
  Value error, Invalid integer value: '14.' [type=value_error, input_value='14.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.value
  Field required [type=missing, input_value={'rank': '14.', 'player':...6', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.rank
  Value error, Invalid integer value: '15.' [type=value_error, input_value='15.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.value
  Field required [type=missing, input_value={'rank': '15.', 'player':...9', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.rank
  Value error, Invalid integer value: '16.' [type=value_error, input_value='16.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.value
  Field required [type=missing, input_value={'rank': '16.', 'player':...8', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.rank
  Value error, Invalid integer value: '17.' [type=value_error, input_value='17.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.value
  Field required [type=missing, input_value={'rank': '17.', 'player':...8', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.rank
  Value error, Invalid integer value: '18.' [type=value_error, input_value='18.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.value
  Field required [type=missing, input_value={'rank': '18.', 'player':...6', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.rank
  Value error, Invalid integer value: '19.' [type=value_error, input_value='19.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.value
  Field required [type=missing, input_value={'rank': '19.', 'player':...4', 'season': '1988-89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.rank
  Value error, Invalid integer value: '20.' [type=value_error, input_value='20.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.value
  Field required [type=missing, input_value={'rank': '20.', 'player':...0', 'season': '2009-10'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.rank
  Value error, Invalid integer value: '21.' [type=value_error, input_value='21.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.value
  Field required [type=missing, input_value={'rank': '21.', 'player':...7', 'season': '2023-24'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.rank
  Value error, Invalid integer value: '22.' [type=value_error, input_value='22.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.value
  Field required [type=missing, input_value={'rank': '22.', 'player':...9', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.rank
  Value error, Invalid integer value: '23.' [type=value_error, input_value='23.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.value
  Field required [type=missing, input_value={'rank': '23.', 'player':...1', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.rank
  Value error, Invalid integer value: '24.' [type=value_error, input_value='24.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.value
  Field required [type=missing, input_value={'rank': '24.', 'player':...1', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.rank
  Value error, Invalid integer value: '25.' [type=value_error, input_value='25.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.value
  Field required [type=missing, input_value={'rank': '25.', 'player':...4', 'season': '2011-12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.rank
  Value error, Invalid integer value: '26.' [type=value_error, input_value='26.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.value
  Field required [type=missing, input_value={'rank': '26.', 'player':...6', 'season': '1993-94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.rank
  Value error, Invalid integer value: '27.' [type=value_error, input_value='27.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.value
  Field required [type=missing, input_value={'rank': '27.', 'player':...6', 'season': '2024-25'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.rank
  Value error, Invalid integer value: '28.' [type=value_error, input_value='28.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.value
  Field required [type=missing, input_value={'rank': '28.', 'player':...5', 'season': '1999-00'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.rank
  Value error, Invalid integer value: '29.' [type=value_error, input_value='29.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.value
  Field required [type=missing, input_value={'rank': '29.', 'player':...3', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.rank
  Value error, Invalid integer value: '30.' [type=value_error, input_value='30.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.value
  Field required [type=missing, input_value={'rank': '30.', 'player':...7', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.rank
  Value error, Invalid integer value: '31.' [type=value_error, input_value='31.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.value
  Field required [type=missing, input_value={'rank': '31.', 'player':...5', 'season': '1998-99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.rank
  Value error, Invalid integer value: '32.' [type=value_error, input_value='32.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.value
  Field required [type=missing, input_value={'rank': '32.', 'player':...9', 'season': '2024-25'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.rank
  Value error, Invalid integer value: '33.' [type=value_error, input_value='33.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.value
  Field required [type=missing, input_value={'rank': '33.', 'player':...6', 'season': '2008-09'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.rank
  Value error, Invalid integer value: '34.' [type=value_error, input_value='34.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.value
  Field required [type=missing, input_value={'rank': '34.', 'player':...7', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.rank
  Value error, Invalid integer value: '35.' [type=value_error, input_value='35.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.value
  Field required [type=missing, input_value={'rank': '35.', 'player':...6', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.rank
  Value error, Invalid integer value: '36.' [type=value_error, input_value='36.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.value
  Field required [type=missing, input_value={'rank': '36.', 'player':...6', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.rank
  Value error, Invalid integer value: '37.' [type=value_error, input_value='37.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.value
  Field required [type=missing, input_value={'rank': '37.', 'player':...3', 'season': '2000-01'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.rank
  Value error, Invalid integer value: '38.' [type=value_error, input_value='38.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.value
  Field required [type=missing, input_value={'rank': '38.', 'player':...6', 'season': '2008-09'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.rank
  Value error, Invalid integer value: '39.' [type=value_error, input_value='39.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.value
  Field required [type=missing, input_value={'rank': '39.', 'player':...4', 'season': '1971-72'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.rank
  Value error, Invalid integer value: '40.' [type=value_error, input_value='40.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.value
  Field required [type=missing, input_value={'rank': '40.', 'player':...8', 'season': '2023-24'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.rank
  Value error, Invalid integer value: '41.' [type=value_error, input_value='41.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.value
  Field required [type=missing, input_value={'rank': '41.', 'player':...5', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.rank
  Value error, Invalid integer value: '42.' [type=value_error, input_value='42.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.value
  Field required [type=missing, input_value={'rank': '42.', 'player':...3', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.rank
  Value error, Invalid integer value: '43.' [type=value_error, input_value='43.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.value
  Field required [type=missing, input_value={'rank': '43.', 'player':...2', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.rank
  Value error, Invalid integer value: '44.' [type=value_error, input_value='44.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.value
  Field required [type=missing, input_value={'rank': '44.', 'player':...8', 'season': '1986-87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.rank
  Value error, Invalid integer value: '45.' [type=value_error, input_value='45.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.value
  Field required [type=missing, input_value={'rank': '45.', 'player':...4', 'season': '1968-69'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.rank
  Value error, Invalid integer value: '46.' [type=value_error, input_value='46.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.value
  Field required [type=missing, input_value={'rank': '46.', 'player':...0', 'season': '1992-93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.rank
  Value error, Invalid integer value: '47.' [type=value_error, input_value='47.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.value
  Field required [type=missing, input_value={'rank': '47.', 'player':...8', 'season': '2001-02'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.rank
  Value error, Invalid integer value: '48.' [type=value_error, input_value='48.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.value
  Field required [type=missing, input_value={'rank': '48.', 'player':...9', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.rank
  Value error, Invalid integer value: '49.' [type=value_error, input_value='49.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.value
  Field required [type=missing, input_value={'rank': '49.', 'player':...4', 'season': '2003-04'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.rank
  Value error, Invalid integer value: '50.' [type=value_error, input_value='50.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.value
  Field required [type=missing, input_value={'rank': '50.', 'player':...1', 'season': '1995-96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.rank
  Value error, Invalid integer value: '51.' [type=value_error, input_value='51.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.value
  Field required [type=missing, input_value={'rank': '51.', 'player':...5', 'season': '1995-96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.rank
  Value error, Invalid integer value: '52.' [type=value_error, input_value='52.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.value
  Field required [type=missing, input_value={'rank': '52.', 'player':...1', 'season': '2023-24'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.rank
  Value error, Invalid integer value: '53.' [type=value_error, input_value='53.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.value
  Field required [type=missing, input_value={'rank': '53.', 'player':...0', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.rank
  Value error, Invalid integer value: '54.' [type=value_error, input_value='54.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.value
  Field required [type=missing, input_value={'rank': '54.', 'player':...2', 'season': '1977-78'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.rank
  Value error, Invalid integer value: '55.' [type=value_error, input_value='55.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.value
  Field required [type=missing, input_value={'rank': '55.', 'player':...8', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.rank
  Value error, Invalid integer value: '56.' [type=value_error, input_value='56.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.value
  Field required [type=missing, input_value={'rank': '56.', 'player':...4', 'season': '2007-08'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.rank
  Value error, Invalid integer value: '57.' [type=value_error, input_value='57.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.value
  Field required [type=missing, input_value={'rank': '57.', 'player':...3', 'season': '1994-95'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.rank
  Value error, Invalid integer value: '58.' [type=value_error, input_value='58.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.value
  Field required [type=missing, input_value={'rank': '58.', 'player':...8', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.rank
  Value error, Invalid integer value: '59.' [type=value_error, input_value='59.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.value
  Field required [type=missing, input_value={'rank': '59.', 'player':...6', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.rank
  Value error, Invalid integer value: '60.' [type=value_error, input_value='60.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.value
  Field required [type=missing, input_value={'rank': '60.', 'player':...1', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.rank
  Value error, Invalid integer value: '61.' [type=value_error, input_value='61.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.value
  Field required [type=missing, input_value={'rank': '61.', 'player':...0', 'season': '1953-54'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.rank
  Value error, Invalid integer value: '62.' [type=value_error, input_value='62.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.value
  Field required [type=missing, input_value={'rank': '62.', 'player':...5', 'season': '1970-71'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.rank
  Value error, Invalid integer value: '63.' [type=value_error, input_value='63.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
62.value
  Field required [type=missing, input_value={'rank': '63.', 'player':...3', 'season': '1990-91'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.rank
  Value error, Invalid integer value: '64.' [type=value_error, input_value='64.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
63.value
  Field required [type=missing, input_value={'rank': '64.', 'player':...1', 'season': '2006-07'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.rank
  Value error, Invalid integer value: '65.' [type=value_error, input_value='65.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
64.value
  Field required [type=missing, input_value={'rank': '65.', 'player':...1', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.rank
  Value error, Invalid integer value: '66.' [type=value_error, input_value='66.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
65.value
  Field required [type=missing, input_value={'rank': '66.', 'player':...0', 'season': '1996-97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.rank
  Value error, Invalid integer value: '67.' [type=value_error, input_value='67.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
66.value
  Field required [type=missing, input_value={'rank': '67.', 'player':...9', 'season': '1997-98'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.rank
  Value error, Invalid integer value: '68.' [type=value_error, input_value='68.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
67.value
  Field required [type=missing, input_value={'rank': '68.', 'player':...5', 'season': '1967-68'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.rank
  Value error, Invalid integer value: '69.' [type=value_error, input_value='69.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
68.value
  Field required [type=missing, input_value={'rank': '69.', 'player':...9', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.rank
  Value error, Invalid integer value: '70.' [type=value_error, input_value='70.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
69.value
  Field required [type=missing, input_value={'rank': '70.', 'player':...8', 'season': '1975-76'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.rank
  Value error, Invalid integer value: '71.' [type=value_error, input_value='71.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
70.value
  Field required [type=missing, input_value={'rank': '71.', 'player':...2', 'season': '1964-65'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.rank
  Value error, Invalid integer value: '72.' [type=value_error, input_value='72.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
71.value
  Field required [type=missing, input_value={'rank': '72.', 'player':...9', 'season': '1994-95'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.rank
  Value error, Invalid integer value: '73.' [type=value_error, input_value='73.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
72.value
  Field required [type=missing, input_value={'rank': '73.', 'player':...8', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.rank
  Value error, Invalid integer value: '74.' [type=value_error, input_value='74.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
73.value
  Field required [type=missing, input_value={'rank': '74.', 'player':...3', 'season': '1993-94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.rank
  Value error, Invalid integer value: '75.' [type=value_error, input_value='75.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
74.value
  Field required [type=missing, input_value={'rank': '75.', 'player':...7', 'season': '1952-53'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.rank
  Value error, Invalid integer value: '76.' [type=value_error, input_value='76.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
75.value
  Field required [type=missing, input_value={'rank': '76.', 'player':...5', 'season': '1972-73'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.rank
  Value error, Invalid integer value: '77.' [type=value_error, input_value='77.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
76.value
  Field required [type=missing, input_value={'rank': '77.', 'player':...1', 'season': '1956-57'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.rank
  Value error, Invalid integer value: '78.' [type=value_error, input_value='78.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
77.value
  Field required [type=missing, input_value={'rank': '78.', 'player':...1', 'season': '2007-08'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.rank
  Value error, Invalid integer value: '79.' [type=value_error, input_value='79.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
78.value
  Field required [type=missing, input_value={'rank': '79.', 'player':...9', 'season': '2012-13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.rank
  Value error, Invalid integer value: '80.' [type=value_error, input_value='80.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
79.value
  Field required [type=missing, input_value={'rank': '80.', 'player':...6', 'season': '1965-66'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.rank
  Value error, Invalid integer value: '81.' [type=value_error, input_value='81.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
80.value
  Field required [type=missing, input_value={'rank': '81.', 'player':...4', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.rank
  Value error, Invalid integer value: '82.' [type=value_error, input_value='82.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
81.value
  Field required [type=missing, input_value={'rank': '82.', 'player':...4', 'season': '1960-61'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.rank
  Value error, Invalid integer value: '83.' [type=value_error, input_value='83.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
82.value
  Field required [type=missing, input_value={'rank': '83.', 'player':...0', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.rank
  Value error, Invalid integer value: '84.' [type=value_error, input_value='84.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
83.value
  Field required [type=missing, input_value={'rank': '84.', 'player':...0', 'season': '1958-59'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.rank
  Value error, Invalid integer value: '85.' [type=value_error, input_value='85.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
84.value
  Field required [type=missing, input_value={'rank': '85.', 'player':...7', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.rank
  Value error, Invalid integer value: '86.' [type=value_error, input_value='86.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
85.value
  Field required [type=missing, input_value={'rank': '86.', 'player':...9', 'season': '2023-24'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.rank
  Value error, Invalid integer value: '87.' [type=value_error, input_value='87.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
86.value
  Field required [type=missing, input_value={'rank': '87.', 'player':...8', 'season': '1959-60'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.rank
  Value error, Invalid integer value: '88.' [type=value_error, input_value='88.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
87.value
  Field required [type=missing, input_value={'rank': '88.', 'player':...6', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.rank
  Value error, Invalid integer value: '89.' [type=value_error, input_value='89.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
88.value
  Field required [type=missing, input_value={'rank': '89.', 'player':...6', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.rank
  Value error, Invalid integer value: '90.' [type=value_error, input_value='90.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
89.value
  Field required [type=missing, input_value={'rank': '90.', 'player':...2', 'season': '2009-10'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.rank
  Value error, Invalid integer value: '91.' [type=value_error, input_value='91.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
90.value
  Field required [type=missing, input_value={'rank': '91.', 'player':...0', 'season': '1969-70'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.rank
  Value error, Invalid integer value: '92.' [type=value_error, input_value='92.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
91.value
  Field required [type=missing, input_value={'rank': '92.', 'player':...8', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.rank
  Value error, Invalid integer value: '93.' [type=value_error, input_value='93.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
92.value
  Field required [type=missing, input_value={'rank': '93.', 'player':...7', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.rank
  Value error, Invalid integer value: '94.' [type=value_error, input_value='94.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
93.value
  Field required [type=missing, input_value={'rank': '94.', 'player':...2', 'season': '1997-98'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.rank
  Value error, Invalid integer value: '95.' [type=value_error, input_value='95.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
94.value
  Field required [type=missing, input_value={'rank': '95.', 'player':...8', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.rank
  Value error, Invalid integer value: '96.' [type=value_error, input_value='96.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
95.value
  Field required [type=missing, input_value={'rank': '96.', 'player':...8', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
96.rank
  Value error, Invalid integer value: '97.' [type=value_error, input_value='97.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
96.value
  Field required [type=missing, input_value={'rank': '97.', 'player':...5', 'season': '1997-98'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
97.rank
  Value error, Invalid integer value: '98.' [type=value_error, input_value='98.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
97.value
  Field required [type=missing, input_value={'rank': '98.', 'player':...0', 'season': '1976-77'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
98.rank
  Value error, Invalid integer value: '99.' [type=value_error, input_value='99.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
98.value
  Field required [type=missing, input_value={'rank': '99.', 'player':...7', 'season': '1960-61'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
99.rank
  Value error, Invalid integer value: '100.' [type=value_error, input_value='100.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
99.value
  Field required [type=missing, input_value={'rank': '100.', 'player'...7', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
100.rank
  Value error, Invalid integer value: '101.' [type=value_error, input_value='101.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
100.value
  Field required [type=missing, input_value={'rank': '101.', 'player'...7', 'season': '1987-88'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
101.rank
  Value error, Invalid integer value: '102.' [type=value_error, input_value='102.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
101.value
  Field required [type=missing, input_value={'rank': '102.', 'player'...6', 'season': '1996-97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
102.rank
  Value error, Invalid integer value: '103.' [type=value_error, input_value='103.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
102.value
  Field required [type=missing, input_value={'rank': '103.', 'player'...5', 'season': '1991-92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
103.rank
  Value error, Invalid integer value: '104.' [type=value_error, input_value='104.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
103.value
  Field required [type=missing, input_value={'rank': '104.', 'player'...4', 'season': '1963-64'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
104.rank
  Value error, Invalid integer value: '105.' [type=value_error, input_value='105.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
104.value
  Field required [type=missing, input_value={'rank': '105.', 'player'...3', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
105.rank
  Value error, Invalid integer value: '106.' [type=value_error, input_value='106.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
105.value
  Field required [type=missing, input_value={'rank': '106.', 'player'...0', 'season': '2006-07'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
106.rank
  Value error, Invalid integer value: '107.' [type=value_error, input_value='107.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
106.value
  Field required [type=missing, input_value={'rank': '107.', 'player'...9', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
107.rank
  Value error, Invalid integer value: '108.' [type=value_error, input_value='108.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
107.value
  Field required [type=missing, input_value={'rank': '108.', 'player'...8', 'season': '1987-88'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
108.rank
  Value error, Invalid integer value: '109.' [type=value_error, input_value='109.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
108.value
  Field required [type=missing, input_value={'rank': '109.', 'player'...8', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
109.rank
  Value error, Invalid integer value: '110.' [type=value_error, input_value='110.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
109.value
  Field required [type=missing, input_value={'rank': '110.', 'player'...8', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
110.rank
  Value error, Invalid integer value: '111.' [type=value_error, input_value='111.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
110.value
  Field required [type=missing, input_value={'rank': '111.', 'player'...8', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
111.rank
  Value error, Invalid integer value: '112.' [type=value_error, input_value='112.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
111.value
  Field required [type=missing, input_value={'rank': '112.', 'player'...7', 'season': '2007-08'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
112.rank
  Value error, Invalid integer value: '113.' [type=value_error, input_value='113.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
112.value
  Field required [type=missing, input_value={'rank': '113.', 'player'...5', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
113.rank
  Value error, Invalid integer value: '114.' [type=value_error, input_value='114.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
113.value
  Field required [type=missing, input_value={'rank': '114.', 'player'...5', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
114.rank
  Value error, Invalid integer value: '115.' [type=value_error, input_value='115.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
114.value
  Field required [type=missing, input_value={'rank': '115.', 'player'...1', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
115.rank
  Value error, Invalid integer value: '116.' [type=value_error, input_value='116.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
115.value
  Field required [type=missing, input_value={'rank': '116.', 'player'...1', 'season': '1991-92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
116.rank
  Value error, Invalid integer value: '117.' [type=value_error, input_value='117.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
116.value
  Field required [type=missing, input_value={'rank': '117.', 'player'...4', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
117.rank
  Value error, Invalid integer value: '118.' [type=value_error, input_value='118.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
117.value
  Field required [type=missing, input_value={'rank': '118.', 'player'...3', 'season': '1990-91'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
118.rank
  Value error, Invalid integer value: '119.' [type=value_error, input_value='119.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
118.value
  Field required [type=missing, input_value={'rank': '119.', 'player'...8', 'season': '1955-56'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
119.rank
  Value error, Invalid integer value: '120.' [type=value_error, input_value='120.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
119.value
  Field required [type=missing, input_value={'rank': '120.', 'player'...7', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
120.rank
  Value error, Invalid integer value: '121.' [type=value_error, input_value='121.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
120.value
  Field required [type=missing, input_value={'rank': '121.', 'player'...1', 'season': '1992-93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
121.rank
  Value error, Invalid integer value: '122.' [type=value_error, input_value='122.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
121.value
  Field required [type=missing, input_value={'rank': '122.', 'player'...0', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
122.rank
  Value error, Invalid integer value: '123.' [type=value_error, input_value='123.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
122.value
  Field required [type=missing, input_value={'rank': '123.', 'player'...7', 'season': '2010-11'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
123.rank
  Value error, Invalid integer value: '124.' [type=value_error, input_value='124.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
123.value
  Field required [type=missing, input_value={'rank': '124.', 'player'...4', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
124.rank
  Value error, Invalid integer value: '125.' [type=value_error, input_value='125.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
124.value
  Field required [type=missing, input_value={'rank': '125.', 'player'...1', 'season': '1975-76'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
125.rank
  Value error, Invalid integer value: '126.' [type=value_error, input_value='126.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
125.value
  Field required [type=missing, input_value={'rank': '126.', 'player'...0', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
126.rank
  Value error, Invalid integer value: '127.' [type=value_error, input_value='127.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
126.value
  Field required [type=missing, input_value={'rank': '127.', 'player'...2', 'season': '1996-97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
127.rank
  Value error, Invalid integer value: '128.' [type=value_error, input_value='128.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
127.value
  Field required [type=missing, input_value={'rank': '128.', 'player'...1', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
128.rank
  Value error, Invalid integer value: '129.' [type=value_error, input_value='129.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
128.value
  Field required [type=missing, input_value={'rank': '129.', 'player'...9', 'season': '1999-00'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
129.rank
  Value error, Invalid integer value: '130.' [type=value_error, input_value='130.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
129.value
  Field required [type=missing, input_value={'rank': '130.', 'player'...9', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
130.rank
  Value error, Invalid integer value: '131.' [type=value_error, input_value='131.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
130.value
  Field required [type=missing, input_value={'rank': '131.', 'player'...6', 'season': '2003-04'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
131.rank
  Value error, Invalid integer value: '132.' [type=value_error, input_value='132.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
131.value
  Field required [type=missing, input_value={'rank': '132.', 'player'...4', 'season': '2011-12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
132.rank
  Value error, Invalid integer value: '133.' [type=value_error, input_value='133.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
132.value
  Field required [type=missing, input_value={'rank': '133.', 'player'...4', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
133.rank
  Value error, Invalid integer value: '134.' [type=value_error, input_value='134.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
133.value
  Field required [type=missing, input_value={'rank': '134.', 'player'...4', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
134.rank
  Value error, Invalid integer value: '135.' [type=value_error, input_value='135.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
134.value
  Field required [type=missing, input_value={'rank': '135.', 'player'...3', 'season': '1986-87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
135.rank
  Value error, Invalid integer value: '136.' [type=value_error, input_value='136.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
135.value
  Field required [type=missing, input_value={'rank': '136.', 'player'...1', 'season': '2001-02'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
136.rank
  Value error, Invalid integer value: '137.' [type=value_error, input_value='137.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
136.value
  Field required [type=missing, input_value={'rank': '137.', 'player'...6', 'season': '1988-89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
137.rank
  Value error, Invalid integer value: '138.' [type=value_error, input_value='138.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
137.value
  Field required [type=missing, input_value={'rank': '138.', 'player'...5', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
138.rank
  Value error, Invalid integer value: '139.' [type=value_error, input_value='139.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
138.value
  Field required [type=missing, input_value={'rank': '139.', 'player'...3', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
139.rank
  Value error, Invalid integer value: '140.' [type=value_error, input_value='140.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
139.value
  Field required [type=missing, input_value={'rank': '140.', 'player'...2', 'season': '1988-89'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
140.rank
  Value error, Invalid integer value: '141.' [type=value_error, input_value='141.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
140.value
  Field required [type=missing, input_value={'rank': '141.', 'player'...2', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
141.rank
  Value error, Invalid integer value: '142.' [type=value_error, input_value='142.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
141.value
  Field required [type=missing, input_value={'rank': '142.', 'player'...0', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
142.rank
  Value error, Invalid integer value: '143.' [type=value_error, input_value='143.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
142.value
  Field required [type=missing, input_value={'rank': '143.', 'player'...7', 'season': '1972-73'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
143.rank
  Value error, Invalid integer value: '144.' [type=value_error, input_value='144.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
143.value
  Field required [type=missing, input_value={'rank': '144.', 'player'...5', 'season': '1956-57'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
144.rank
  Value error, Invalid integer value: '145.' [type=value_error, input_value='145.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
144.value
  Field required [type=missing, input_value={'rank': '145.', 'player'...5', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
145.rank
  Value error, Invalid integer value: '146.' [type=value_error, input_value='146.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
145.value
  Field required [type=missing, input_value={'rank': '146.', 'player'...1', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
146.rank
  Value error, Invalid integer value: '147.' [type=value_error, input_value='147.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
146.value
  Field required [type=missing, input_value={'rank': '147.', 'player'...0', 'season': '1961-62'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
147.rank
  Value error, Invalid integer value: '148.' [type=value_error, input_value='148.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
147.value
  Field required [type=missing, input_value={'rank': '148.', 'player'...7', 'season': '1981-82'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
148.rank
  Value error, Invalid integer value: '149.' [type=value_error, input_value='149.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
148.value
  Field required [type=missing, input_value={'rank': '149.', 'player'...2', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
149.rank
  Value error, Invalid integer value: '150.' [type=value_error, input_value='150.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
149.value
  Field required [type=missing, input_value={'rank': '150.', 'player'...0', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
150.rank
  Value error, Invalid integer value: '151.' [type=value_error, input_value='151.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
150.value
  Field required [type=missing, input_value={'rank': '151.', 'player'...8', 'season': '1964-65'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
151.rank
  Value error, Invalid integer value: '152.' [type=value_error, input_value='152.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
151.value
  Field required [type=missing, input_value={'rank': '152.', 'player'...4', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
152.rank
  Value error, Invalid integer value: '153.' [type=value_error, input_value='153.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
152.value
  Field required [type=missing, input_value={'rank': '153.', 'player'...3', 'season': '1951-52'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
153.rank
  Value error, Invalid integer value: '154.' [type=value_error, input_value='154.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
153.value
  Field required [type=missing, input_value={'rank': '154.', 'player'...3', 'season': '1962-63'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
154.rank
  Value error, Invalid integer value: '155.' [type=value_error, input_value='155.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
154.value
  Field required [type=missing, input_value={'rank': '155.', 'player'...0', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
155.rank
  Value error, Invalid integer value: '156.' [type=value_error, input_value='156.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
155.value
  Field required [type=missing, input_value={'rank': '156.', 'player'...8', 'season': '1971-72'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
156.rank
  Value error, Invalid integer value: '157.' [type=value_error, input_value='157.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
156.value
  Field required [type=missing, input_value={'rank': '157.', 'player'...8', 'season': '1961-62'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
157.rank
  Value error, Invalid integer value: '158.' [type=value_error, input_value='158.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
157.value
  Field required [type=missing, input_value={'rank': '158.', 'player'...5', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
158.rank
  Value error, Invalid integer value: '159.' [type=value_error, input_value='159.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
158.value
  Field required [type=missing, input_value={'rank': '159.', 'player'...4', 'season': '1984-85'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
159.rank
  Value error, Invalid integer value: '160.' [type=value_error, input_value='160.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
159.value
  Field required [type=missing, input_value={'rank': '160.', 'player'...1', 'season': '1966-67'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
160.rank
  Value error, Invalid integer value: '161.' [type=value_error, input_value='161.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
160.value
  Field required [type=missing, input_value={'rank': '161.', 'player'...1', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
161.rank
  Value error, Invalid integer value: '162.' [type=value_error, input_value='162.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
161.value
  Field required [type=missing, input_value={'rank': '162.', 'player'...0', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
162.rank
  Value error, Invalid integer value: '163.' [type=value_error, input_value='163.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
162.value
  Field required [type=missing, input_value={'rank': '163.', 'player'...8', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
163.rank
  Value error, Invalid integer value: '164.' [type=value_error, input_value='164.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
163.value
  Field required [type=missing, input_value={'rank': '164.', 'player'...7', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
164.rank
  Value error, Invalid integer value: '165.' [type=value_error, input_value='165.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
164.value
  Field required [type=missing, input_value={'rank': '165.', 'player'...6', 'season': '2006-07'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
165.rank
  Value error, Invalid integer value: '166.' [type=value_error, input_value='166.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
165.value
  Field required [type=missing, input_value={'rank': '166.', 'player'...8', 'season': '2012-13'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
166.rank
  Value error, Invalid integer value: '167.' [type=value_error, input_value='167.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
166.value
  Field required [type=missing, input_value={'rank': '167.', 'player'...8', 'season': '1986-87'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
167.rank
  Value error, Invalid integer value: '168.' [type=value_error, input_value='168.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
167.value
  Field required [type=missing, input_value={'rank': '168.', 'player'...8', 'season': '1995-96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
168.rank
  Value error, Invalid integer value: '169.' [type=value_error, input_value='169.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
168.value
  Field required [type=missing, input_value={'rank': '169.', 'player'...7', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
169.rank
  Value error, Invalid integer value: '170.' [type=value_error, input_value='170.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
169.value
  Field required [type=missing, input_value={'rank': '170.', 'player'...6', 'season': '1974-75'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
170.rank
  Value error, Invalid integer value: '171.' [type=value_error, input_value='171.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
170.value
  Field required [type=missing, input_value={'rank': '171.', 'player'...5', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
171.rank
  Value error, Invalid integer value: '172.' [type=value_error, input_value='172.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
171.value
  Field required [type=missing, input_value={'rank': '172.', 'player'...4', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
172.rank
  Value error, Invalid integer value: '173.' [type=value_error, input_value='173.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
172.value
  Field required [type=missing, input_value={'rank': '173.', 'player'...2', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
173.rank
  Value error, Invalid integer value: '174.' [type=value_error, input_value='174.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
173.value
  Field required [type=missing, input_value={'rank': '174.', 'player'...1', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
174.rank
  Value error, Invalid integer value: '175.' [type=value_error, input_value='175.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
174.value
  Field required [type=missing, input_value={'rank': '175.', 'player'...1', 'season': '2011-12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
175.rank
  Value error, Invalid integer value: '176.' [type=value_error, input_value='176.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
175.value
  Field required [type=missing, input_value={'rank': '176.', 'player'...8', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
176.rank
  Value error, Invalid integer value: '177.' [type=value_error, input_value='177.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
176.value
  Field required [type=missing, input_value={'rank': '177.', 'player'...6', 'season': '1957-58'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
177.rank
  Value error, Invalid integer value: '178.' [type=value_error, input_value='178.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
177.value
  Field required [type=missing, input_value={'rank': '178.', 'player'...5', 'season': '2024-25'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
178.rank
  Value error, Invalid integer value: '179.' [type=value_error, input_value='179.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
178.value
  Field required [type=missing, input_value={'rank': '179.', 'player'...4', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
179.rank
  Value error, Invalid integer value: '180.' [type=value_error, input_value='180.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
179.value
  Field required [type=missing, input_value={'rank': '180.', 'player'...3', 'season': '1961-62'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
180.rank
  Value error, Invalid integer value: '181.' [type=value_error, input_value='181.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
180.value
  Field required [type=missing, input_value={'rank': '181.', 'player'...2', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
181.rank
  Value error, Invalid integer value: '182.' [type=value_error, input_value='182.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
181.value
  Field required [type=missing, input_value={'rank': '182.', 'player'...1', 'season': '1992-93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
182.rank
  Value error, Invalid integer value: '183.' [type=value_error, input_value='183.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
182.value
  Field required [type=missing, input_value={'rank': '183.', 'player'...0', 'season': '2011-12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
183.rank
  Value error, Invalid integer value: '184.' [type=value_error, input_value='184.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
183.value
  Field required [type=missing, input_value={'rank': '184.', 'player'...8', 'season': '1974-75'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
184.rank
  Value error, Invalid integer value: '185.' [type=value_error, input_value='185.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
184.value
  Field required [type=missing, input_value={'rank': '185.', 'player'...7', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
185.rank
  Value error, Invalid integer value: '186.' [type=value_error, input_value='186.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
185.value
  Field required [type=missing, input_value={'rank': '186.', 'player'...7', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
186.rank
  Value error, Invalid integer value: '187.' [type=value_error, input_value='187.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
186.value
  Field required [type=missing, input_value={'rank': '187.', 'player'...6', 'season': '2009-10'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
187.rank
  Value error, Invalid integer value: '188.' [type=value_error, input_value='188.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
187.value
  Field required [type=missing, input_value={'rank': '188.', 'player'...4', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
188.rank
  Value error, Invalid integer value: '189.' [type=value_error, input_value='189.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
188.value
  Field required [type=missing, input_value={'rank': '189.', 'player'...2', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
189.rank
  Value error, Invalid integer value: '190.' [type=value_error, input_value='190.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
189.value
  Field required [type=missing, input_value={'rank': '190.', 'player'...0', 'season': '2006-07'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
190.rank
  Value error, Invalid integer value: '191.' [type=value_error, input_value='191.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
190.value
  Field required [type=missing, input_value={'rank': '191.', 'player'...7', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
191.rank
  Value error, Invalid integer value: '192.' [type=value_error, input_value='192.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
191.value
  Field required [type=missing, input_value={'rank': '192.', 'player'...6', 'season': '2010-11'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
192.rank
  Value error, Invalid integer value: '193.' [type=value_error, input_value='193.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
192.value
  Field required [type=missing, input_value={'rank': '193.', 'player'...6', 'season': '2025-26'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
193.rank
  Value error, Invalid integer value: '194.' [type=value_error, input_value='194.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
193.value
  Field required [type=missing, input_value={'rank': '194.', 'player'...6', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
194.rank
  Value error, Invalid integer value: '195.' [type=value_error, input_value='195.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
194.value
  Field required [type=missing, input_value={'rank': '195.', 'player'...5', 'season': '2006-07'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
195.rank
  Value error, Invalid integer value: '196.' [type=value_error, input_value='196.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
195.value
  Field required [type=missing, input_value={'rank': '196.', 'player'...3', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
196.rank
  Value error, Invalid integer value: '197.' [type=value_error, input_value='197.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
196.value
  Field required [type=missing, input_value={'rank': '197.', 'player'...1', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
197.rank
  Value error, Invalid integer value: '198.' [type=value_error, input_value='198.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
197.value
  Field required [type=missing, input_value={'rank': '198.', 'player'...9', 'season': '1954-55'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
198.rank
  Value error, Invalid integer value: '199.' [type=value_error, input_value='199.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
198.value
  Field required [type=missing, input_value={'rank': '199.', 'player'...8', 'season': '1994-95'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
199.rank
  Value error, Invalid integer value: '200.' [type=value_error, input_value='200.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
199.value
  Field required [type=missing, input_value={'rank': '200.', 'player'...8', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
200.rank
  Value error, Invalid integer value: '201.' [type=value_error, input_value='201.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
200.value
  Field required [type=missing, input_value={'rank': '201.', 'player'...7', 'season': '1995-96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
201.rank
  Value error, Invalid integer value: '202.' [type=value_error, input_value='202.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
201.value
  Field required [type=missing, input_value={'rank': '202.', 'player'...6', 'season': '2017-18'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
202.rank
  Value error, Invalid integer value: '203.' [type=value_error, input_value='203.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
202.value
  Field required [type=missing, input_value={'rank': '203.', 'player'...4', 'season': '2014-15'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
203.rank
  Value error, Invalid integer value: '204.' [type=value_error, input_value='204.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
203.value
  Field required [type=missing, input_value={'rank': '204.', 'player'...3', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
204.rank
  Value error, Invalid integer value: '205.' [type=value_error, input_value='205.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
204.value
  Field required [type=missing, input_value={'rank': '205.', 'player'...2', 'season': '2013-14'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
205.rank
  Value error, Invalid integer value: '206.' [type=value_error, input_value='206.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
205.value
  Field required [type=missing, input_value={'rank': '206.', 'player'...1', 'season': '1981-82'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
206.rank
  Value error, Invalid integer value: '207.' [type=value_error, input_value='207.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
206.value
  Field required [type=missing, input_value={'rank': '207.', 'player'...0', 'season': '1960-61'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
207.rank
  Value error, Invalid integer value: '208.' [type=value_error, input_value='208.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
207.value
  Field required [type=missing, input_value={'rank': '208.', 'player'...0', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
208.rank
  Value error, Invalid integer value: '209.' [type=value_error, input_value='209.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
208.value
  Field required [type=missing, input_value={'rank': '209.', 'player'...0', 'season': '1992-93'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
209.rank
  Value error, Invalid integer value: '210.' [type=value_error, input_value='210.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
209.value
  Field required [type=missing, input_value={'rank': '210.', 'player'...8', 'season': '2022-23'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
210.rank
  Value error, Invalid integer value: '211.' [type=value_error, input_value='211.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
210.value
  Field required [type=missing, input_value={'rank': '211.', 'player'...6', 'season': '1952-53'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
211.rank
  Value error, Invalid integer value: '212.' [type=value_error, input_value='212.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
211.value
  Field required [type=missing, input_value={'rank': '212.', 'player'...5', 'season': '1984-85'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
212.rank
  Value error, Invalid integer value: '213.' [type=value_error, input_value='213.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
212.value
  Field required [type=missing, input_value={'rank': '213.', 'player'...2', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
213.rank
  Value error, Invalid integer value: '214.' [type=value_error, input_value='214.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
213.value
  Field required [type=missing, input_value={'rank': '214.', 'player'...2', 'season': '1953-54'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
214.rank
  Value error, Invalid integer value: '215.' [type=value_error, input_value='215.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
214.value
  Field required [type=missing, input_value={'rank': '215.', 'player'...8', 'season': '2023-24'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
215.rank
  Value error, Invalid integer value: '216.' [type=value_error, input_value='216.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
215.value
  Field required [type=missing, input_value={'rank': '216.', 'player'...7', 'season': '1989-90'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
216.rank
  Value error, Invalid integer value: '217.' [type=value_error, input_value='217.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
216.value
  Field required [type=missing, input_value={'rank': '217.', 'player'...6', 'season': '1974-75'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
217.rank
  Value error, Invalid integer value: '218.' [type=value_error, input_value='218.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
217.value
  Field required [type=missing, input_value={'rank': '218.', 'player'...5', 'season': '2016-17'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
218.rank
  Value error, Invalid integer value: '219.' [type=value_error, input_value='219.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
218.value
  Field required [type=missing, input_value={'rank': '219.', 'player'...5', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
219.rank
  Value error, Invalid integer value: '220.' [type=value_error, input_value='220.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
219.value
  Field required [type=missing, input_value={'rank': '220.', 'player'...5', 'season': '1999-00'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
220.rank
  Value error, Invalid integer value: '221.' [type=value_error, input_value='221.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
220.value
  Field required [type=missing, input_value={'rank': '221.', 'player'...0', 'season': '1967-68'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
221.rank
  Value error, Invalid integer value: '222.' [type=value_error, input_value='222.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
221.value
  Field required [type=missing, input_value={'rank': '222.', 'player'...9', 'season': '1973-74'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
222.rank
  Value error, Invalid integer value: '223.' [type=value_error, input_value='223.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
222.value
  Field required [type=missing, input_value={'rank': '223.', 'player'...9', 'season': '1951-52'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
223.rank
  Value error, Invalid integer value: '224.' [type=value_error, input_value='224.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
223.value
  Field required [type=missing, input_value={'rank': '224.', 'player'...7', 'season': '2004-05'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
224.rank
  Value error, Invalid integer value: '225.' [type=value_error, input_value='225.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
224.value
  Field required [type=missing, input_value={'rank': '225.', 'player'...5', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
225.rank
  Value error, Invalid integer value: '226.' [type=value_error, input_value='226.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
225.value
  Field required [type=missing, input_value={'rank': '226.', 'player'...5', 'season': '2005-06'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
226.rank
  Value error, Invalid integer value: '227.' [type=value_error, input_value='227.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
226.value
  Field required [type=missing, input_value={'rank': '227.', 'player'...1', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
227.rank
  Value error, Invalid integer value: '228.' [type=value_error, input_value='228.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
227.value
  Field required [type=missing, input_value={'rank': '228.', 'player'...1', 'season': '1985-86'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
228.rank
  Value error, Invalid integer value: '229.' [type=value_error, input_value='229.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
228.value
  Field required [type=missing, input_value={'rank': '229.', 'player'...1', 'season': '2020-21'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
229.rank
  Value error, Invalid integer value: '230.' [type=value_error, input_value='230.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
229.value
  Field required [type=missing, input_value={'rank': '230.', 'player'...0', 'season': '1998-99'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
230.rank
  Value error, Invalid integer value: '231.' [type=value_error, input_value='231.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
230.value
  Field required [type=missing, input_value={'rank': '231.', 'player'...8', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
231.rank
  Value error, Invalid integer value: '232.' [type=value_error, input_value='232.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
231.value
  Field required [type=missing, input_value={'rank': '232.', 'player'...7', 'season': '2010-11'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
232.rank
  Value error, Invalid integer value: '233.' [type=value_error, input_value='233.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
232.value
  Field required [type=missing, input_value={'rank': '233.', 'player'...5', 'season': '2002-03'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
233.rank
  Value error, Invalid integer value: '234.' [type=value_error, input_value='234.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
233.value
  Field required [type=missing, input_value={'rank': '234.', 'player'...4', 'season': '1996-97'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
234.rank
  Value error, Invalid integer value: '235.' [type=value_error, input_value='235.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
234.value
  Field required [type=missing, input_value={'rank': '235.', 'player'...2', 'season': '1966-67'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
235.rank
  Value error, Invalid integer value: '236.' [type=value_error, input_value='236.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
235.value
  Field required [type=missing, input_value={'rank': '236.', 'player'...2', 'season': '1995-96'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
236.rank
  Value error, Invalid integer value: '237.' [type=value_error, input_value='237.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
236.value
  Field required [type=missing, input_value={'rank': '237.', 'player'...9', 'season': '2019-20'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
237.rank
  Value error, Invalid integer value: '238.' [type=value_error, input_value='238.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
237.value
  Field required [type=missing, input_value={'rank': '238.', 'player'...8', 'season': '1980-81'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
238.rank
  Value error, Invalid integer value: '239.' [type=value_error, input_value='239.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
238.value
  Field required [type=missing, input_value={'rank': '239.', 'player'...6', 'season': '1978-79'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
239.rank
  Value error, Invalid integer value: '240.' [type=value_error, input_value='240.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
239.value
  Field required [type=missing, input_value={'rank': '240.', 'player'...5', 'season': '2018-19'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
240.rank
  Value error, Invalid integer value: '241.' [type=value_error, input_value='241.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
240.value
  Field required [type=missing, input_value={'rank': '241.', 'player'...1', 'season': '2021-22'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
241.rank
  Value error, Invalid integer value: '242.' [type=value_error, input_value='242.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
241.value
  Field required [type=missing, input_value={'rank': '242.', 'player'...7', 'season': '2008-09'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
242.rank
  Value error, Invalid integer value: '243.' [type=value_error, input_value='243.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
242.value
  Field required [type=missing, input_value={'rank': '243.', 'player'...7', 'season': '1991-92'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
243.rank
  Value error, Invalid integer value: '244.' [type=value_error, input_value='244.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
243.value
  Field required [type=missing, input_value={'rank': '244.', 'player'...6', 'season': '2011-12'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
244.rank
  Value error, Invalid integer value: '245.' [type=value_error, input_value='245.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
244.value
  Field required [type=missing, input_value={'rank': '245.', 'player'...6', 'season': '1979-80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
245.rank
  Value error, Invalid integer value: '246.' [type=value_error, input_value='246.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
245.value
  Field required [type=missing, input_value={'rank': '246.', 'player'...6', 'season': '1952-53'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
246.rank
  Value error, Invalid integer value: '247.' [type=value_error, input_value='247.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
246.value
  Field required [type=missing, input_value={'rank': '247.', 'player'...1', 'season': '1975-76'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
247.rank
  Value error, Invalid integer value: '248.' [type=value_error, input_value='248.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
247.value
  Field required [type=missing, input_value={'rank': '248.', 'player'...0', 'season': '1979-80'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
248.rank
  Value error, Invalid integer value: '249.' [type=value_error, input_value='249.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
248.value
  Field required [type=missing, input_value={'rank': '249.', 'player'...9', 'season': '2015-16'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
249.rank
  Value error, Invalid integer value: '250.' [type=value_error, input_value='250.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
249.value
  Field required [type=missing, input_value={'rank': '250.', 'player'...9', 'season': '1993-94'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\draft.py", line 73, in season_leaders
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'season_leaders' (https://www.basketball-reference.com/leaders/per_season.html): missing field/alias: 0.value
```

### career_leaders

- **Params**: `{}`
- **URL**: `https://www.basketball-reference.com/leaders/`
- **Status**: error
- **Duration**: 6.910s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 288
- **Message**: Schema drift detected for endpoint 'career_leaders' (https://www.basketball-reference.com/leaders/): missing field/alias: 0.rank

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 288 validation errors for list[CareerLeadersRow]
0.rank
  Field required [type=missing, input_value={'totals': 'Games', 'col_...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.player
  Field required [type=missing, input_value={'totals': 'Games', 'col_...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
0.value
  Field required [type=missing, input_value={'totals': 'Games', 'col_...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.rank
  Field required [type=missing, input_value={'totals': 'Minutes Playe... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.player
  Field required [type=missing, input_value={'totals': 'Minutes Playe... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
1.value
  Field required [type=missing, input_value={'totals': 'Minutes Playe... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.rank
  Field required [type=missing, input_value={'totals': 'Field Goals',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.player
  Field required [type=missing, input_value={'totals': 'Field Goals',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
2.value
  Field required [type=missing, input_value={'totals': 'Field Goals',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.rank
  Field required [type=missing, input_value={'totals': 'Field Goal At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.player
  Field required [type=missing, input_value={'totals': 'Field Goal At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
3.value
  Field required [type=missing, input_value={'totals': 'Field Goal At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
4.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
5.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
6.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
7.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.rank
  Field required [type=missing, input_value={'totals': 'Field Goals M... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.player
  Field required [type=missing, input_value={'totals': 'Field Goals M... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
8.value
  Field required [type=missing, input_value={'totals': 'Field Goals M... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.rank
  Field required [type=missing, input_value={'totals': 'Free Throws',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.player
  Field required [type=missing, input_value={'totals': 'Free Throws',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
9.value
  Field required [type=missing, input_value={'totals': 'Free Throws',... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.rank
  Field required [type=missing, input_value={'totals': 'Free Throw At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.player
  Field required [type=missing, input_value={'totals': 'Free Throw At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
10.value
  Field required [type=missing, input_value={'totals': 'Free Throw At... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.rank
  Field required [type=missing, input_value={'totals': 'Offensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.player
  Field required [type=missing, input_value={'totals': 'Offensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
11.value
  Field required [type=missing, input_value={'totals': 'Offensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.rank
  Field required [type=missing, input_value={'totals': 'Defensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.player
  Field required [type=missing, input_value={'totals': 'Defensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.value
  Field required [type=missing, input_value={'totals': 'Defensive Reb... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.rank
  Field required [type=missing, input_value={'totals': 'Total Rebound... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.player
  Field required [type=missing, input_value={'totals': 'Total Rebound... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
13.value
  Field required [type=missing, input_value={'totals': 'Total Rebound... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.rank
  Field required [type=missing, input_value={'totals': 'Assists', 'co... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.player
  Field required [type=missing, input_value={'totals': 'Assists', 'co... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
14.value
  Field required [type=missing, input_value={'totals': 'Assists', 'co... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.rank
  Field required [type=missing, input_value={'totals': 'Steals', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.player
  Field required [type=missing, input_value={'totals': 'Steals', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.value
  Field required [type=missing, input_value={'totals': 'Steals', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.rank
  Field required [type=missing, input_value={'totals': 'Blocks', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.player
  Field required [type=missing, input_value={'totals': 'Blocks', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
16.value
  Field required [type=missing, input_value={'totals': 'Blocks', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.rank
  Field required [type=missing, input_value={'totals': 'Turnovers', '... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.player
  Field required [type=missing, input_value={'totals': 'Turnovers', '... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
17.value
  Field required [type=missing, input_value={'totals': 'Turnovers', '... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.rank
  Field required [type=missing, input_value={'totals': 'Personal Foul... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.player
  Field required [type=missing, input_value={'totals': 'Personal Foul... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
18.value
  Field required [type=missing, input_value={'totals': 'Personal Foul... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.rank
  Field required [type=missing, input_value={'totals': 'Points', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.player
  Field required [type=missing, input_value={'totals': 'Points', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
19.value
  Field required [type=missing, input_value={'totals': 'Points', 'col... 'col_8': 'Single Game'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.rank
  Field required [type=missing, input_value={'totals': 'Triple-Double...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.player
  Field required [type=missing, input_value={'totals': 'Triple-Double...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
20.value
  Field required [type=missing, input_value={'totals': 'Triple-Double...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.rank
  Field required [type=missing, input_value={'totals': 'Field Goal Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.player
  Field required [type=missing, input_value={'totals': 'Field Goal Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
21.value
  Field required [type=missing, input_value={'totals': 'Field Goal Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
22.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
23.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.rank
  Field required [type=missing, input_value={'totals': 'Free Throw Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.player
  Field required [type=missing, input_value={'totals': 'Free Throw Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
24.value
  Field required [type=missing, input_value={'totals': 'Free Throw Pc...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.rank
  Field required [type=missing, input_value={'totals': 'True Shooting...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.player
  Field required [type=missing, input_value={'totals': 'True Shooting...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
25.value
  Field required [type=missing, input_value={'totals': 'True Shooting...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.rank
  Field required [type=missing, input_value={'totals': 'Effective Fie...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.player
  Field required [type=missing, input_value={'totals': 'Effective Fie...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
26.value
  Field required [type=missing, input_value={'totals': 'Effective Fie...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.rank
  Field required [type=missing, input_value={'totals': 'Minutes Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.player
  Field required [type=missing, input_value={'totals': 'Minutes Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
27.value
  Field required [type=missing, input_value={'totals': 'Minutes Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.rank
  Field required [type=missing, input_value={'totals': 'Points Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.player
  Field required [type=missing, input_value={'totals': 'Points Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
28.value
  Field required [type=missing, input_value={'totals': 'Points Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.rank
  Field required [type=missing, input_value={'totals': 'Rebounds Per ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.player
  Field required [type=missing, input_value={'totals': 'Rebounds Per ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
29.value
  Field required [type=missing, input_value={'totals': 'Rebounds Per ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.rank
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.player
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
30.value
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.rank
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.player
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
31.value
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.rank
  Field required [type=missing, input_value={'totals': 'Assists Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.player
  Field required [type=missing, input_value={'totals': 'Assists Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
32.value
  Field required [type=missing, input_value={'totals': 'Assists Per G...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.rank
  Field required [type=missing, input_value={'totals': 'Steals Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.player
  Field required [type=missing, input_value={'totals': 'Steals Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
33.value
  Field required [type=missing, input_value={'totals': 'Steals Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.rank
  Field required [type=missing, input_value={'totals': 'Blocks Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.player
  Field required [type=missing, input_value={'totals': 'Blocks Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
34.value
  Field required [type=missing, input_value={'totals': 'Blocks Per Ga...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.rank
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.player
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
35.value
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.rank
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.player
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
36.value
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
37.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
38.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
39.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
40.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.rank
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.player
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
41.value
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.rank
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.player
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
42.value
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.rank
  Field required [type=missing, input_value={'totals': 'Player Effici...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.player
  Field required [type=missing, input_value={'totals': 'Player Effici...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
43.value
  Field required [type=missing, input_value={'totals': 'Player Effici...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.rank
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.player
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
44.value
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.rank
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.player
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
45.value
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.rank
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.player
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
46.value
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.rank
  Field required [type=missing, input_value={'totals': 'Assist Pct', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.player
  Field required [type=missing, input_value={'totals': 'Assist Pct', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
47.value
  Field required [type=missing, input_value={'totals': 'Assist Pct', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.rank
  Field required [type=missing, input_value={'totals': 'Steal Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.player
  Field required [type=missing, input_value={'totals': 'Steal Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
48.value
  Field required [type=missing, input_value={'totals': 'Steal Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.rank
  Field required [type=missing, input_value={'totals': 'Block Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.player
  Field required [type=missing, input_value={'totals': 'Block Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
49.value
  Field required [type=missing, input_value={'totals': 'Block Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.rank
  Field required [type=missing, input_value={'totals': 'Turnover Pct'...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.player
  Field required [type=missing, input_value={'totals': 'Turnover Pct'...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
50.value
  Field required [type=missing, input_value={'totals': 'Turnover Pct'...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.rank
  Field required [type=missing, input_value={'totals': 'Usage Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.player
  Field required [type=missing, input_value={'totals': 'Usage Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
51.value
  Field required [type=missing, input_value={'totals': 'Usage Pct', '...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.rank
  Field required [type=missing, input_value={'totals': 'Offensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.player
  Field required [type=missing, input_value={'totals': 'Offensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
52.value
  Field required [type=missing, input_value={'totals': 'Offensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.rank
  Field required [type=missing, input_value={'totals': 'Defensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.player
  Field required [type=missing, input_value={'totals': 'Defensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
53.value
  Field required [type=missing, input_value={'totals': 'Defensive Rat...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.rank
  Field required [type=missing, input_value={'totals': 'Offensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.player
  Field required [type=missing, input_value={'totals': 'Offensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
54.value
  Field required [type=missing, input_value={'totals': 'Offensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.rank
  Field required [type=missing, input_value={'totals': 'Defensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.player
  Field required [type=missing, input_value={'totals': 'Defensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
55.value
  Field required [type=missing, input_value={'totals': 'Defensive Win...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.rank
  Field required [type=missing, input_value={'totals': 'Win Shares', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.player
  Field required [type=missing, input_value={'totals': 'Win Shares', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
56.value
  Field required [type=missing, input_value={'totals': 'Win Shares', ...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.rank
  Field required [type=missing, input_value={'totals': 'Win Shares Pe...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.player
  Field required [type=missing, input_value={'totals': 'Win Shares Pe...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
57.value
  Field required [type=missing, input_value={'totals': 'Win Shares Pe...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.rank
  Field required [type=missing, input_value={'totals': 'Box Plus/Minu...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.player
  Field required [type=missing, input_value={'totals': 'Box Plus/Minu...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
58.value
  Field required [type=missing, input_value={'totals': 'Box Plus/Minu...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.rank
  Field required [type=missing, input_value={'totals': 'Offensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.player
  Field required [type=missing, input_value={'totals': 'Offensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
59.value
  Field required [type=missing, input_value={'totals': 'Offensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.rank
  Field required [type=missing, input_value={'totals': 'Defensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.player
  Field required [type=missing, input_value={'totals': 'Defensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
60.value
  Field required [type=missing, input_value={'totals': 'Defensive Box...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.rank
  Field required [type=missing, input_value={'totals': 'Value Over Re...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.player
  Field required [type=missing, input_value={'totals': 'Value Over Re...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
61.value
  Field required [type=missing, input_value={'totals': 'Value Over Re...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.rank
  Field required [type=missing, input_value={'totals': 'Points Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.player
  Field required [type=missing, input_value={'totals': 'Points Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
62.value
  Field required [type=missing, input_value={'totals': 'Points Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.rank
  Field required [type=missing, input_value={'totals': 'Assists Per 3...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.player
  Field required [type=missing, input_value={'totals': 'Assists Per 3...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
63.value
  Field required [type=missing, input_value={'totals': 'Assists Per 3...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.rank
  Field required [type=missing, input_value={'totals': 'Blocks Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.player
  Field required [type=missing, input_value={'totals': 'Blocks Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
64.value
  Field required [type=missing, input_value={'totals': 'Blocks Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.rank
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.player
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
65.value
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.rank
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.player
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
66.value
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
67.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
68.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
69.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
70.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.rank
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.player
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
71.value
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.rank
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.player
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
72.value
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.rank
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.player
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
73.value
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.rank
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.player
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
74.value
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.rank
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.player
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
75.value
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.rank
  Field required [type=missing, input_value={'totals': 'Steals Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.player
  Field required [type=missing, input_value={'totals': 'Steals Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
76.value
  Field required [type=missing, input_value={'totals': 'Steals Per 36...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.rank
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.player
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
77.value
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.rank
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.player
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
78.value
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.rank
  Field required [type=missing, input_value={'totals': 'Points Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.player
  Field required [type=missing, input_value={'totals': 'Points Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
79.value
  Field required [type=missing, input_value={'totals': 'Points Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.rank
  Field required [type=missing, input_value={'totals': 'Assists Per 1...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.player
  Field required [type=missing, input_value={'totals': 'Assists Per 1...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
80.value
  Field required [type=missing, input_value={'totals': 'Assists Per 1...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.rank
  Field required [type=missing, input_value={'totals': 'Blocks Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.player
  Field required [type=missing, input_value={'totals': 'Blocks Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
81.value
  Field required [type=missing, input_value={'totals': 'Blocks Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.rank
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.player
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
82.value
  Field required [type=missing, input_value={'totals': 'Defensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.rank
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.player
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
83.value
  Field required [type=missing, input_value={'totals': 'Field Goals P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
84.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.rank
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.player
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
85.value
  Field required [type=missing, input_value={'totals': '2-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
86.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.rank
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.player
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
87.value
  Field required [type=missing, input_value={'totals': '3-Pt Field Go...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.rank
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.player
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
88.value
  Field required [type=missing, input_value={'totals': 'Field Goal At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.rank
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.player
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
89.value
  Field required [type=missing, input_value={'totals': 'Free Throws P...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.rank
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.player
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
90.value
  Field required [type=missing, input_value={'totals': 'Free Throw At...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.rank
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.player
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
91.value
  Field required [type=missing, input_value={'totals': 'Offensive Reb...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.rank
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.player
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
92.value
  Field required [type=missing, input_value={'totals': 'Personal Foul...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.rank
  Field required [type=missing, input_value={'totals': 'Steals Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.player
  Field required [type=missing, input_value={'totals': 'Steals Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
93.value
  Field required [type=missing, input_value={'totals': 'Steals Per 10...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.rank
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.player
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
94.value
  Field required [type=missing, input_value={'totals': 'Turnovers Per...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.rank
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.player
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
95.value
  Field required [type=missing, input_value={'totals': 'Total Rebound...ar Top 10', 'col_8': ''}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\draft.py", line 97, in career_leaders
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'career_leaders' (https://www.basketball-reference.com/leaders/): missing field/alias: 0.rank
```

### player_career_stats

- **Params**: `{"player_identifier": "duranke01"}`
- **URL**: `https://www.basketball-reference.com/players/d/duranke01.html`
- **Status**: error
- **Duration**: 6.889s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 25
- **Message**: Schema drift detected for endpoint 'player_career_stats' (https://www.basketball-reference.com/players/d/duranke01.html): missing field/alias: 12.age

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 25 validation errors for list[PlayerCareerStatsRow]
12.age
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.team_name_abbr
  Value error, Unknown team abbreviation: 'Did not play - injury' [type=value_error, input_value='Did not play - injury', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.games
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.games_started
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.mp_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fg_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fga_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fg_pct
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fg3_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fg3a_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fg3_pct
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.efg_pct
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.ft_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.fta_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.ft_pct
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.orb_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.drb_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.trb_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.ast_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.stl_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.blk_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.tov_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.pf_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
12.pts_per_g
  Field required [type=missing, input_value={'year_id': '2019-20', 't...'Did not play - injury'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/missing
15.team_name_abbr
  Value error, Unknown team abbreviation: '2TM' [type=value_error, input_value='2TM', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 24, in player_career_stats
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_career_stats' (https://www.basketball-reference.com/players/d/duranke01.html): missing field/alias: 12.age
```

### player_playoff_series

- **Params**: `{"player_identifier": "duranke01"}`
- **URL**: `https://www.basketball-reference.com/players/d/duranke01.html`
- **Status**: error
- **Duration**: 6.716s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 3
- **Message**: Schema drift detected for endpoint 'player_playoff_series' (https://www.basketball-reference.com/players/d/duranke01.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 3 validation errors for list[PlayerPlayoffSeriesRow]
13.team_name_abbr
  Value error, Unknown team abbreviation: '' [type=value_error, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.team_name_abbr
  Value error, Unknown team abbreviation: '' [type=value_error, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.team_name_abbr
  Value error, Unknown team abbreviation: '' [type=value_error, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 49, in player_playoff_series
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_playoff_series' (https://www.basketball-reference.com/players/d/duranke01.html): missing field/alias: unknown
```

### player_adjusted_shooting

- **Params**: `{"player_identifier": "embiijo01"}`
- **URL**: `https://www.basketball-reference.com/players/e/embiijo01.html`
- **Status**: error
- **Duration**: 6.754s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 2
- **Message**: Schema drift detected for endpoint 'player_adjusted_shooting' (https://www.basketball-reference.com/players/e/embiijo01.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 2 validation errors for list[PlayerAdjustedShootingRow]
0.team_name_abbr
  Value error, Unknown team abbreviation: 'Did not play - injury' [type=value_error, input_value='Did not play - injury', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.team_name_abbr
  Value error, Unknown team abbreviation: 'Did not play - injury' [type=value_error, input_value='Did not play - injury', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 74, in player_adjusted_shooting
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_adjusted_shooting' (https://www.basketball-reference.com/players/e/embiijo01.html): missing field/alias: unknown
```

### player_play_by_play

- **Params**: `{"player_identifier": "doncilu01"}`
- **URL**: `https://www.basketball-reference.com/players/d/doncilu01.html`
- **Status**: error
- **Duration**: 6.419s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 1
- **Message**: Schema drift detected for endpoint 'player_play_by_play' (https://www.basketball-reference.com/players/d/doncilu01.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for list[PlayerPlayByPlayStatsRow]
6.team_name_abbr
  Value error, Unknown team abbreviation: '2TM' [type=value_error, input_value='2TM', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 99, in player_play_by_play
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_play_by_play' (https://www.basketball-reference.com/players/d/doncilu01.html): missing field/alias: unknown
```

### player_game_highs

- **Params**: `{"player_identifier": "westbru01"}`
- **URL**: `https://www.basketball-reference.com/players/w/westbru01.html`
- **Status**: ok
- **Duration**: 6.328s
- **Row count**: 20
- **Columns**: `[]`

**Sample**:
```json
["season='2008-09' age=20 team='OKC' league='NBA' time_on_court='46:56' made_field_goals=13 attempted_field_goals=32 made_three_point_field_goals=3 attempted_three_point_field_goals=6 made_two_point_field_goals=13 attempted_two_point_field_goals=26 made_free_throws=20 attempted_free_throws=22 offensive_rebounds=8 defensive_rebounds=8 total_rebounds=12 assists=12 steals=5 blocks=2 turnovers=9 personal_fouls=5 points=34 game_score='27.6'", "season='2009-10' age=21 team='OKC' league='NBA' time_on_c
```

### player_all_star

- **Params**: `{"player_identifier": "jordami01"}`
- **URL**: `https://www.basketball-reference.com/players/j/jordami01.html`
- **Status**: error
- **Duration**: 6.163s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 13
- **Message**: Schema drift detected for endpoint 'player_all_star' (https://www.basketball-reference.com/players/j/jordami01.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 13 validation errors for list[PlayerAllStarRow]
0.mp
  Value error, Invalid integer value: '22:00' [type=value_error, input_value='22:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.mp
  Value error, Invalid integer value: '28:00' [type=value_error, input_value='28:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.mp
  Value error, Invalid integer value: '29:00' [type=value_error, input_value='29:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.mp
  Value error, Invalid integer value: '33:00' [type=value_error, input_value='33:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.mp
  Value error, Invalid integer value: '29:00' [type=value_error, input_value='29:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.mp
  Value error, Invalid integer value: '36:00' [type=value_error, input_value='36:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.mp
  Value error, Invalid integer value: '31:00' [type=value_error, input_value='31:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.mp
  Value error, Invalid integer value: '36:00' [type=value_error, input_value='36:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.mp
  Value error, Invalid integer value: '22:00' [type=value_error, input_value='22:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.mp
  Value error, Invalid integer value: '26:00' [type=value_error, input_value='26:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.mp
  Value error, Invalid integer value: '32:00' [type=value_error, input_value='32:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.mp
  Value error, Invalid integer value: '22:00' [type=value_error, input_value='22:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.mp
  Value error, Invalid integer value: '36:00' [type=value_error, input_value='36:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 149, in player_all_star
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_all_star' (https://www.basketball-reference.com/players/j/jordami01.html): missing field/alias: unknown
```

### player_similarity_scores

- **Params**: `{"player_identifier": "jordami01"}`
- **URL**: `https://www.basketball-reference.com/players/j/jordami01.html`
- **Status**: ok
- **Duration**: 6.327s
- **Row count**: 11
- **Columns**: `[]`

**Sample**:
```json
["player='Michael Jordan' sim_score=None year1='21.2' year2='20.4' year3='20.3' year4='19.8' year5='19.0' year6='18.3' year7='17.7' year8='17.2' year9='16.9' year10='15.8' year11='14.0' year12='6.2' year13='3.3' year14='2.3' year15='1.5' year16=None year17=None year18=None year19=None year20=None year21=None year22=None", "player='Oscar Robertson' sim_score=80.4 year1='20.6' year2='17.4' year3='17.0' year4='16.9' year5='16.8' year6='15.6' year7='13.2' year8='12.9' year9='12.4' year10='12.3' year
```

### player_salaries

- **Params**: `{"player_identifier": "tatumja01"}`
- **URL**: `https://www.basketball-reference.com/players/t/tatumja01.html`
- **Status**: ok
- **Duration**: 6.876s
- **Row count**: 8
- **Columns**: `[]`

**Sample**:
```json
["season='2017-18' team_name='Boston Celtics' lg_id='NBA' salary='$5,645,400'", "season='2018-19' team_name='Boston Celtics' lg_id='NBA' salary='$6,700,800'"]
```

### player_splits

- **Params**: `{"player_identifier": "leonaka01", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/players/l/leonaka01/splits/2024`
- **Status**: ok
- **Duration**: 6.554s
- **Row count**: 66
- **Columns**: `[]`

**Sample**:
```json
["split_id=None split_value='Total' games_played=68 games_started=68 minutes_played=2330 made_field_goals=610 attempted_field_goals=1162 made_three_point_field_goals=140 attempted_three_point_field_goals=336 made_free_throws=253 attempted_free_throws=286 offensive_rebounds=84 total_rebounds=416 assists=244 steals=111 blocks=59 turnovers=119 personal_fouls=97 points=1613 field_goal_percentage=0.525 three_point_field_goal_percentage=0.417 free_throw_percentage=0.885 true_shooting_percentage=0.626 
```

### player_on_off

- **Params**: `{"player_identifier": "lillada01", "season_end_year": 2019}`
- **URL**: `https://www.basketball-reference.com/players/l/lillada01/on-off/2019`
- **Status**: error
- **Duration**: 7.154s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 1
- **Message**: Schema drift detected for endpoint 'player_on_off' (https://www.basketball-reference.com/players/l/lillada01/on-off/2019): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for list[PlayerOnOffRow]
2.mp
  Value error, Invalid integer value: '71%' [type=value_error, input_value='71%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\players.py", line 251, in player_on_off
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'player_on_off' (https://www.basketball-reference.com/players/l/lillada01/on-off/2019): missing field/alias: unknown
```

### player_shot_charts

- **Params**: `{"player_identifier": "jordami01", "season_end_year": 2020}`
- **URL**: `https://www.basketball-reference.com/players/j/jordami01/shooting/2020`
- **Status**: ok
- **Duration**: 7.502s
- **Row count**: 0
- **Columns**: `[]`

**Sample**:
```json
[]
```

### team_roster

- **Params**: `{"team_abbreviation": "NOP", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/teams/NOP/2024.html`
- **Status**: ok
- **Duration**: 6.988s
- **Row count**: 20
- **Columns**: `[]`

**Sample**:
```json
["player='Jose Alvarado' number='15' positions=[<Position.POINT_GUARD: 'POINT GUARD'>] height='6-0' weight=179 birth_date='April 12, 1998' flag='us US' years_experience='2' college='Georgia Tech'", "player='Izaiah Brockington' number='21' positions=[<Position.POINT_GUARD: 'POINT GUARD'>] height='6-4' weight=196 birth_date='July 12, 1999' flag='us US' years_experience='R' college='St. Bonaventure , Penn State , Iowa State'"]
```

### team_injury_report

- **Params**: `{"team_abbreviation": "ORL", "season_end_year": 2021}`
- **URL**: `https://www.basketball-reference.com/friv/injuries.fcgi`
- **Status**: ok
- **Duration**: 6.189s
- **Row count**: 42
- **Columns**: `[]`

**Sample**:
```json
["player='Egor Dёmin' team_name='Brooklyn Nets' date_update='Mon, Mar 9, 2026' note='Out For Season (Foot) - The Nets reported Egor Demin will miss rest of season with plantar fasciitis.'", "player='Michael Porter Jr.' team_name='Brooklyn Nets' date_update='Fri, Apr 3, 2026' note='Out For Season (Hamstring) - Porter (hamstring) has been ruled out for the remainder of the 2025-26 season, according to Erik Slater of ClutchPoints.com.'"]
```

### team_and_opponent

- **Params**: `{"team_abbreviation": "DAL", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/teams/DAL/2024.html`
- **Status**: error
- **Duration**: 6.757s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 36
- **Message**: Schema drift detected for endpoint 'team_and_opponent' (https://www.basketball-reference.com/teams/DAL/2024.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 36 validation errors for list[TeamAndOpponentRow]
3.mp_per_g
  Value error, Invalid float value: '-1.1%' [type=value_error, input_value='-1.1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg_per_g
  Value error, Invalid float value: '7.7%' [type=value_error, input_value='7.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fga_per_g
  Value error, Invalid float value: '6.4%' [type=value_error, input_value='6.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3_per_g
  Value error, Invalid float value: '-3.9%' [type=value_error, input_value='-3.9%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3a_per_g
  Value error, Invalid float value: '-3.6%' [type=value_error, input_value='-3.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg2_per_g
  Value error, Invalid float value: '14.8%' [type=value_error, input_value='14.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg2a_per_g
  Value error, Invalid float value: '15.9%' [type=value_error, input_value='15.9%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ft_per_g
  Value error, Invalid float value: '-10.1%' [type=value_error, input_value='-10.1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fta_per_g
  Value error, Invalid float value: '-10.5%' [type=value_error, input_value='-10.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.orb_per_g
  Value error, Invalid float value: '27.5%' [type=value_error, input_value='27.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.drb_per_g
  Value error, Invalid float value: '6.6%' [type=value_error, input_value='6.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.trb_per_g
  Value error, Invalid float value: '10.7%' [type=value_error, input_value='10.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ast_per_g
  Value error, Invalid float value: '12.0%' [type=value_error, input_value='12.0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.stl_per_g
  Value error, Invalid float value: '9.5%' [type=value_error, input_value='9.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.blk_per_g
  Value error, Invalid float value: '33.6%' [type=value_error, input_value='33.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.tov_per_g
  Value error, Invalid float value: '2.5%' [type=value_error, input_value='2.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pf_per_g
  Value error, Invalid float value: '-11.6%' [type=value_error, input_value='-11.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pts_per_g
  Value error, Invalid float value: '3.2%' [type=value_error, input_value='3.2%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.mp_per_g
  Value error, Invalid float value: '-1.1%' [type=value_error, input_value='-1.1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg_per_g
  Value error, Invalid float value: '2.8%' [type=value_error, input_value='2.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fga_per_g
  Value error, Invalid float value: '4.9%' [type=value_error, input_value='4.9%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3_per_g
  Value error, Invalid float value: '17.7%' [type=value_error, input_value='17.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3a_per_g
  Value error, Invalid float value: '12.5%' [type=value_error, input_value='12.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg2_per_g
  Value error, Invalid float value: '-2.6%' [type=value_error, input_value='-2.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg2a_per_g
  Value error, Invalid float value: '0.5%' [type=value_error, input_value='0.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ft_per_g
  Value error, Invalid float value: '-14.6%' [type=value_error, input_value='-14.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fta_per_g
  Value error, Invalid float value: '-13.4%' [type=value_error, input_value='-13.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_orb_per_g
  Value error, Invalid float value: '8.0%' [type=value_error, input_value='8.0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_drb_per_g
  Value error, Invalid float value: '-1.3%' [type=value_error, input_value='-1.3%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_trb_per_g
  Value error, Invalid float value: '0.8%' [type=value_error, input_value='0.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ast_per_g
  Value error, Invalid float value: '10.5%' [type=value_error, input_value='10.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_stl_per_g
  Value error, Invalid float value: '15.5%' [type=value_error, input_value='15.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_blk_per_g
  Value error, Invalid float value: '6.1%' [type=value_error, input_value='6.1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_tov_per_g
  Value error, Invalid float value: '4.8%' [type=value_error, input_value='4.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pf_per_g
  Value error, Invalid float value: '-6.8%' [type=value_error, input_value='-6.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pts_per_g
  Value error, Invalid float value: '1.3%' [type=value_error, input_value='1.3%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 80, in team_and_opponent
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'team_and_opponent' (https://www.basketball-reference.com/teams/DAL/2024.html): missing field/alias: unknown
```

### team_misc_four_factors

- **Params**: `{"team_abbreviation": "SAS", "season_end_year": 2019}`
- **URL**: `https://www.basketball-reference.com/teams/SAS/2019.html`
- **Status**: ok
- **Duration**: 6.345s
- **Row count**: 2
- **Columns**: `[]`

**Sample**:
```json
["player='Team' wins=48 losses=34 wins_pyth=45.0 losses_pyth=37.0 mov=1.68 sos=0.12 srs=1.8 off_rtg=112.9 def_rtg=111.2 pace=98.3 fta_per_fga_pct=0.237 fg3a_per_fga_pct=0.286 efg_pct=0.534 tov_pct=11.0 orb_pct=21.0 ft_rate=0.194 opp_efg_pct=0.528 opp_tov_pct=11.0 drb_pct=79.4 opp_ft_rate=0.17 arena_name='AT&T Center' attendance=750616", "player='Lg Rank' wins=11 losses=18 wins_pyth=12.0 losses_pyth=12.0 mov=12.0 sos=15.0 srs=12.0 off_rtg=7.0 def_rtg=19.0 pace=22.0 fta_per_fga_pct=24.0 fg3a_per_f
```

### team_opponent_stats

- **Params**: `{"team_abbreviation": "LAC", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/teams/LAC/2024.html`
- **Status**: error
- **Duration**: 6.444s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 36
- **Message**: Schema drift detected for endpoint 'team_opponent_stats' (https://www.basketball-reference.com/teams/LAC/2024.html): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 36 validation errors for list[TeamOpponentStatsRow]
3.mp_per_g
  Value error, Invalid float value: '-0.6%' [type=value_error, input_value='-0.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg_per_g
  Value error, Invalid float value: '3.1%' [type=value_error, input_value='3.1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fga_per_g
  Value error, Invalid float value: '0.7%' [type=value_error, input_value='0.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3_per_g
  Value error, Invalid float value: '-0.5%' [type=value_error, input_value='-0.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3a_per_g
  Value error, Invalid float value: '-0.6%' [type=value_error, input_value='-0.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg2_per_g
  Value error, Invalid float value: '4.6%' [type=value_error, input_value='4.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg2a_per_g
  Value error, Invalid float value: '1.5%' [type=value_error, input_value='1.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ft_per_g
  Value error, Invalid float value: '-2.2%' [type=value_error, input_value='-2.2%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fta_per_g
  Value error, Invalid float value: '-7.4%' [type=value_error, input_value='-7.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.orb_per_g
  Value error, Invalid float value: '2.4%' [type=value_error, input_value='2.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.drb_per_g
  Value error, Invalid float value: '-1.5%' [type=value_error, input_value='-1.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.trb_per_g
  Value error, Invalid float value: '-0.6%' [type=value_error, input_value='-0.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ast_per_g
  Value error, Invalid float value: '7.0%' [type=value_error, input_value='7.0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.stl_per_g
  Value error, Invalid float value: '10.3%' [type=value_error, input_value='10.3%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.blk_per_g
  Value error, Invalid float value: '13.5%' [type=value_error, input_value='13.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.tov_per_g
  Value error, Invalid float value: '-7.6%' [type=value_error, input_value='-7.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pf_per_g
  Value error, Invalid float value: '-4.9%' [type=value_error, input_value='-4.9%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pts_per_g
  Value error, Invalid float value: '1.8%' [type=value_error, input_value='1.8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.mp_per_g
  Value error, Invalid float value: '-0.6%' [type=value_error, input_value='-0.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg_per_g
  Value error, Invalid float value: '-0.5%' [type=value_error, input_value='-0.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fga_per_g
  Value error, Invalid float value: '0.6%' [type=value_error, input_value='0.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3_per_g
  Value error, Invalid float value: '5.4%' [type=value_error, input_value='5.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3a_per_g
  Value error, Invalid float value: '6.0%' [type=value_error, input_value='6.0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg2_per_g
  Value error, Invalid float value: '-2.9%' [type=value_error, input_value='-2.9%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg2a_per_g
  Value error, Invalid float value: '-2.6%' [type=value_error, input_value='-2.6%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ft_per_g
  Value error, Invalid float value: '-5.7%' [type=value_error, input_value='-5.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fta_per_g
  Value error, Invalid float value: '-6.2%' [type=value_error, input_value='-6.2%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_orb_per_g
  Value error, Invalid float value: '8.5%' [type=value_error, input_value='8.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_drb_per_g
  Value error, Invalid float value: '-5.5%' [type=value_error, input_value='-5.5%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_trb_per_g
  Value error, Invalid float value: '-2.2%' [type=value_error, input_value='-2.2%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ast_per_g
  Value error, Invalid float value: '5.7%' [type=value_error, input_value='5.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_stl_per_g
  Value error, Invalid float value: '-6.7%' [type=value_error, input_value='-6.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_blk_per_g
  Value error, Invalid float value: '12.0%' [type=value_error, input_value='12.0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_tov_per_g
  Value error, Invalid float value: '0.4%' [type=value_error, input_value='0.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pf_per_g
  Value error, Invalid float value: '-4.4%' [type=value_error, input_value='-4.4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pts_per_g
  Value error, Invalid float value: '-0.7%' [type=value_error, input_value='-0.7%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 132, in team_opponent_stats
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'team_opponent_stats' (https://www.basketball-reference.com/teams/LAC/2024.html): missing field/alias: unknown
```

### team_schedule

- **Params**: `{"team_abbreviation": "SAS", "season_end_year": 2023}`
- **URL**: `https://www.basketball-reference.com/teams/SAS/2023_games.html`
- **Status**: ok
- **Duration**: 7.058s
- **Row count**: 82
- **Columns**: `[]`

**Sample**:
```json
["g=1 date_game='Wed, Oct 19, 2022' game_start_time='8:00p' network=None box_score_text='Box Score' game_location=None opp_name='Charlotte Hornets' game_result='L' overtimes=None pts=102 opp_pts=129 wins=0 losses=1 game_streak='L 1' attendance=16236 game_duration='2:07' game_remarks=None", "g=2 date_game='Fri, Oct 21, 2022' game_start_time='7:00p' network=None box_score_text='Box Score' game_location='@' opp_name='Indiana Pacers' game_result='W' overtimes=None pts=137 opp_pts=134 wins=1 losses=1
```

### team_transactions

- **Params**: `{"team_abbreviation": "CHO", "season_end_year": 2018}`
- **URL**: `https://www.basketball-reference.com/teams/CHO/2018_transactions.html`
- **Status**: ok
- **Duration**: 6.538s
- **Row count**: 37
- **Columns**: `[]`

**Sample**:
```json
["date='July 2, 2017' transaction='Signed Malik Monk to a multi-year contract.'", "date='July 6, 2017' transaction='Signed Dwayne Bacon to a multi-year contract.'"]
```

### team_splits

- **Params**: `{"team_abbreviation": "TOR", "season_end_year": 2023}`
- **URL**: `https://www.basketball-reference.com/teams/TOR/2023/splits/`
- **Status**: error
- **Duration**: 6.346s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 1736
- **Message**: Schema drift detected for endpoint 'team_splits' (https://www.basketball-reference.com/teams/TOR/2023/splits/): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1736 validation errors for list[TeamSplitsRow]
0.fg
  Value error, Invalid integer value: '41.9' [type=value_error, input_value='41.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.fga
  Value error, Invalid integer value: '91.3' [type=value_error, input_value='91.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.fg3a
  Value error, Invalid integer value: '32.0' [type=value_error, input_value='32.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.ft
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.fta
  Value error, Invalid integer value: '23.4' [type=value_error, input_value='23.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.orb
  Value error, Invalid integer value: '12.7' [type=value_error, input_value='12.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.trb
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.ast
  Value error, Invalid integer value: '23.9' [type=value_error, input_value='23.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.stl
  Value error, Invalid integer value: '9.4' [type=value_error, input_value='9.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.blk
  Value error, Invalid integer value: '5.2' [type=value_error, input_value='5.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.tov
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.pts
  Value error, Invalid integer value: '112.9' [type=value_error, input_value='112.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_fg
  Value error, Invalid integer value: '40.4' [type=value_error, input_value='40.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_fga
  Value error, Invalid integer value: '82.3' [type=value_error, input_value='82.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_fg3
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_fg3a
  Value error, Invalid integer value: '32.6' [type=value_error, input_value='32.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_ft
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_fta
  Value error, Invalid integer value: '23.1' [type=value_error, input_value='23.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_orb
  Value error, Invalid integer value: '9.2' [type=value_error, input_value='9.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_trb
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_ast
  Value error, Invalid integer value: '26.2' [type=value_error, input_value='26.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_stl
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_blk
  Value error, Invalid integer value: '4.6' [type=value_error, input_value='4.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_tov
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_pf
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
0.opp_pts
  Value error, Invalid integer value: '111.4' [type=value_error, input_value='111.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.fg
  Value error, Invalid integer value: '42.1' [type=value_error, input_value='42.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.fga
  Value error, Invalid integer value: '91.0' [type=value_error, input_value='91.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.fg3a
  Value error, Invalid integer value: '31.7' [type=value_error, input_value='31.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.ft
  Value error, Invalid integer value: '19.4' [type=value_error, input_value='19.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.fta
  Value error, Invalid integer value: '24.8' [type=value_error, input_value='24.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.orb
  Value error, Invalid integer value: '13.4' [type=value_error, input_value='13.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.trb
  Value error, Invalid integer value: '44.4' [type=value_error, input_value='44.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.ast
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.stl
  Value error, Invalid integer value: '9.6' [type=value_error, input_value='9.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.blk
  Value error, Invalid integer value: '5.2' [type=value_error, input_value='5.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.tov
  Value error, Invalid integer value: '11.6' [type=value_error, input_value='11.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.pf
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.pts
  Value error, Invalid integer value: '114.4' [type=value_error, input_value='114.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_fg
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_fga
  Value error, Invalid integer value: '82.3' [type=value_error, input_value='82.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_fg3
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_fg3a
  Value error, Invalid integer value: '32.6' [type=value_error, input_value='32.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_ft
  Value error, Invalid integer value: '18.1' [type=value_error, input_value='18.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_fta
  Value error, Invalid integer value: '22.7' [type=value_error, input_value='22.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_orb
  Value error, Invalid integer value: '9.2' [type=value_error, input_value='9.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_trb
  Value error, Invalid integer value: '41.3' [type=value_error, input_value='41.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_ast
  Value error, Invalid integer value: '25.6' [type=value_error, input_value='25.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_stl
  Value error, Invalid integer value: '6.1' [type=value_error, input_value='6.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_blk
  Value error, Invalid integer value: '4.2' [type=value_error, input_value='4.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_tov
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.opp_pts
  Value error, Invalid integer value: '109.7' [type=value_error, input_value='109.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.fg
  Value error, Invalid integer value: '41.6' [type=value_error, input_value='41.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.fga
  Value error, Invalid integer value: '91.7' [type=value_error, input_value='91.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.fg3
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.ft
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.fta
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.orb
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.trb
  Value error, Invalid integer value: '41.6' [type=value_error, input_value='41.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.ast
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.stl
  Value error, Invalid integer value: '9.2' [type=value_error, input_value='9.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.blk
  Value error, Invalid integer value: '5.1' [type=value_error, input_value='5.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.tov
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.pts
  Value error, Invalid integer value: '111.3' [type=value_error, input_value='111.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_fg
  Value error, Invalid integer value: '41.0' [type=value_error, input_value='41.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_fga
  Value error, Invalid integer value: '82.4' [type=value_error, input_value='82.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_fg3
  Value error, Invalid integer value: '12.4' [type=value_error, input_value='12.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_fg3a
  Value error, Invalid integer value: '32.6' [type=value_error, input_value='32.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_ft
  Value error, Invalid integer value: '18.7' [type=value_error, input_value='18.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_fta
  Value error, Invalid integer value: '23.4' [type=value_error, input_value='23.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_orb
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_trb
  Value error, Invalid integer value: '43.2' [type=value_error, input_value='43.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_ast
  Value error, Invalid integer value: '26.8' [type=value_error, input_value='26.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_stl
  Value error, Invalid integer value: '5.9' [type=value_error, input_value='5.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_tov
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_pf
  Value error, Invalid integer value: '19.1' [type=value_error, input_value='19.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.opp_pts
  Value error, Invalid integer value: '113.0' [type=value_error, input_value='113.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fga
  Value error, Invalid integer value: '90.9' [type=value_error, input_value='90.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3
  Value error, Invalid integer value: '10.9' [type=value_error, input_value='10.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ft
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.fta
  Value error, Invalid integer value: '24.9' [type=value_error, input_value='24.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.orb
  Value error, Invalid integer value: '12.7' [type=value_error, input_value='12.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.trb
  Value error, Invalid integer value: '42.8' [type=value_error, input_value='42.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.ast
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.stl
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.blk
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.tov
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.pts
  Value error, Invalid integer value: '113.3' [type=value_error, input_value='113.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_fg
  Value error, Invalid integer value: '40.6' [type=value_error, input_value='40.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_fga
  Value error, Invalid integer value: '82.8' [type=value_error, input_value='82.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_fg3
  Value error, Invalid integer value: '12.4' [type=value_error, input_value='12.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_fg3a
  Value error, Invalid integer value: '33.5' [type=value_error, input_value='33.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_ft
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_fta
  Value error, Invalid integer value: '23.7' [type=value_error, input_value='23.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_orb
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_trb
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_ast
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_stl
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_blk
  Value error, Invalid integer value: '4.6' [type=value_error, input_value='4.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_tov
  Value error, Invalid integer value: '16.6' [type=value_error, input_value='16.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_pf
  Value error, Invalid integer value: '20.7' [type=value_error, input_value='20.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.opp_pts
  Value error, Invalid integer value: '112.5' [type=value_error, input_value='112.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.fg
  Value error, Invalid integer value: '42.9' [type=value_error, input_value='42.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.fga
  Value error, Invalid integer value: '92.5' [type=value_error, input_value='92.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.fg3
  Value error, Invalid integer value: '10.4' [type=value_error, input_value='10.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.fg3a
  Value error, Invalid integer value: '31.3' [type=value_error, input_value='31.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.ft
  Value error, Invalid integer value: '15.4' [type=value_error, input_value='15.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.fta
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.orb
  Value error, Invalid integer value: '12.8' [type=value_error, input_value='12.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.trb
  Value error, Invalid integer value: '43.7' [type=value_error, input_value='43.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.ast
  Value error, Invalid integer value: '25.4' [type=value_error, input_value='25.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.stl
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.tov
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.pf
  Value error, Invalid integer value: '18.9' [type=value_error, input_value='18.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.pts
  Value error, Invalid integer value: '111.7' [type=value_error, input_value='111.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_fg
  Value error, Invalid integer value: '39.9' [type=value_error, input_value='39.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_fga
  Value error, Invalid integer value: '81.3' [type=value_error, input_value='81.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_fg3
  Value error, Invalid integer value: '11.6' [type=value_error, input_value='11.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_fg3a
  Value error, Invalid integer value: '30.4' [type=value_error, input_value='30.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_ft
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_fta
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_orb
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_trb
  Value error, Invalid integer value: '42.2' [type=value_error, input_value='42.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_ast
  Value error, Invalid integer value: '26.7' [type=value_error, input_value='26.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_stl
  Value error, Invalid integer value: '5.9' [type=value_error, input_value='5.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_blk
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_tov
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_pf
  Value error, Invalid integer value: '16.6' [type=value_error, input_value='16.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.opp_pts
  Value error, Invalid integer value: '108.6' [type=value_error, input_value='108.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.fg
  Value error, Invalid integer value: '43.6' [type=value_error, input_value='43.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.fga
  Value error, Invalid integer value: '91.5' [type=value_error, input_value='91.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.fg3
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.ft
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.fta
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.orb
  Value error, Invalid integer value: '13.1' [type=value_error, input_value='13.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.trb
  Value error, Invalid integer value: '44.6' [type=value_error, input_value='44.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.ast
  Value error, Invalid integer value: '25.3' [type=value_error, input_value='25.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.stl
  Value error, Invalid integer value: '10.1' [type=value_error, input_value='10.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.blk
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.tov
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.pf
  Value error, Invalid integer value: '20.4' [type=value_error, input_value='20.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.pts
  Value error, Invalid integer value: '117.2' [type=value_error, input_value='117.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_fg
  Value error, Invalid integer value: '38.0' [type=value_error, input_value='38.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_fga
  Value error, Invalid integer value: '81.0' [type=value_error, input_value='81.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_fg3a
  Value error, Invalid integer value: '31.1' [type=value_error, input_value='31.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_ft
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_fta
  Value error, Invalid integer value: '23.7' [type=value_error, input_value='23.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_orb
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_trb
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_ast
  Value error, Invalid integer value: '24.7' [type=value_error, input_value='24.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_stl
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_tov
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_pf
  Value error, Invalid integer value: '19.2' [type=value_error, input_value='19.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.opp_pts
  Value error, Invalid integer value: '105.6' [type=value_error, input_value='105.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.fg
  Value error, Invalid integer value: '40.2' [type=value_error, input_value='40.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.fga
  Value error, Invalid integer value: '91.2' [type=value_error, input_value='91.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.fg3
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.fg3a
  Value error, Invalid integer value: '31.0' [type=value_error, input_value='31.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.ft
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.fta
  Value error, Invalid integer value: '23.9' [type=value_error, input_value='23.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.orb
  Value error, Invalid integer value: '12.3' [type=value_error, input_value='12.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.trb
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.ast
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.stl
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.blk
  Value error, Invalid integer value: '4.7' [type=value_error, input_value='4.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.tov
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.pts
  Value error, Invalid integer value: '108.5' [type=value_error, input_value='108.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_fg
  Value error, Invalid integer value: '42.8' [type=value_error, input_value='42.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_fga
  Value error, Invalid integer value: '83.7' [type=value_error, input_value='83.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_fg3
  Value error, Invalid integer value: '13.4' [type=value_error, input_value='13.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_fg3a
  Value error, Invalid integer value: '34.1' [type=value_error, input_value='34.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_ft
  Value error, Invalid integer value: '18.2' [type=value_error, input_value='18.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_fta
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_orb
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_trb
  Value error, Invalid integer value: '44.7' [type=value_error, input_value='44.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_ast
  Value error, Invalid integer value: '27.7' [type=value_error, input_value='27.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_stl
  Value error, Invalid integer value: '6.2' [type=value_error, input_value='6.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_blk
  Value error, Invalid integer value: '5.1' [type=value_error, input_value='5.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_tov
  Value error, Invalid integer value: '16.3' [type=value_error, input_value='16.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_pf
  Value error, Invalid integer value: '19.9' [type=value_error, input_value='19.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.opp_pts
  Value error, Invalid integer value: '117.2' [type=value_error, input_value='117.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.fga
  Value error, Invalid integer value: '86.4' [type=value_error, input_value='86.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.fg3
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.fg3a
  Value error, Invalid integer value: '34.1' [type=value_error, input_value='34.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.ft
  Value error, Invalid integer value: '18.7' [type=value_error, input_value='18.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.fta
  Value error, Invalid integer value: '25.1' [type=value_error, input_value='25.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.orb
  Value error, Invalid integer value: '10.1' [type=value_error, input_value='10.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.trb
  Value error, Invalid integer value: '42.7' [type=value_error, input_value='42.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.ast
  Value error, Invalid integer value: '23.9' [type=value_error, input_value='23.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.blk
  Value error, Invalid integer value: '5.4' [type=value_error, input_value='5.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.tov
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.pf
  Value error, Invalid integer value: '21.3' [type=value_error, input_value='21.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.pts
  Value error, Invalid integer value: '109.7' [type=value_error, input_value='109.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg
  Value error, Invalid integer value: '37.9' [type=value_error, input_value='37.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fga
  Value error, Invalid integer value: '80.1' [type=value_error, input_value='80.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fg3a
  Value error, Invalid integer value: '32.9' [type=value_error, input_value='32.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ft
  Value error, Invalid integer value: '18.7' [type=value_error, input_value='18.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_fta
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_orb
  Value error, Invalid integer value: '7.3' [type=value_error, input_value='7.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_trb
  Value error, Invalid integer value: '40.6' [type=value_error, input_value='40.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_ast
  Value error, Invalid integer value: '25.7' [type=value_error, input_value='25.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_stl
  Value error, Invalid integer value: '4.7' [type=value_error, input_value='4.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_tov
  Value error, Invalid integer value: '14.9' [type=value_error, input_value='14.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.opp_pts
  Value error, Invalid integer value: '106.6' [type=value_error, input_value='106.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.fg
  Value error, Invalid integer value: '41.3' [type=value_error, input_value='41.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.fga
  Value error, Invalid integer value: '93.1' [type=value_error, input_value='93.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.fg3
  Value error, Invalid integer value: '9.9' [type=value_error, input_value='9.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.ft
  Value error, Invalid integer value: '18.7' [type=value_error, input_value='18.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.fta
  Value error, Invalid integer value: '23.4' [type=value_error, input_value='23.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.orb
  Value error, Invalid integer value: '14.4' [type=value_error, input_value='14.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.trb
  Value error, Invalid integer value: '44.2' [type=value_error, input_value='44.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.ast
  Value error, Invalid integer value: '22.9' [type=value_error, input_value='22.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.stl
  Value error, Invalid integer value: '10.4' [type=value_error, input_value='10.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.tov
  Value error, Invalid integer value: '13.9' [type=value_error, input_value='13.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.pf
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.pts
  Value error, Invalid integer value: '111.1' [type=value_error, input_value='111.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_fg
  Value error, Invalid integer value: '40.3' [type=value_error, input_value='40.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_fga
  Value error, Invalid integer value: '83.1' [type=value_error, input_value='83.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_fg3
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_fg3a
  Value error, Invalid integer value: '35.3' [type=value_error, input_value='35.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_ft
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_fta
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_orb
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_trb
  Value error, Invalid integer value: '42.9' [type=value_error, input_value='42.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_ast
  Value error, Invalid integer value: '26.9' [type=value_error, input_value='26.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_stl
  Value error, Invalid integer value: '7.3' [type=value_error, input_value='7.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_blk
  Value error, Invalid integer value: '5.6' [type=value_error, input_value='5.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_tov
  Value error, Invalid integer value: '18.6' [type=value_error, input_value='18.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_pf
  Value error, Invalid integer value: '21.2' [type=value_error, input_value='21.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.opp_pts
  Value error, Invalid integer value: '110.7' [type=value_error, input_value='110.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.fg
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.fga
  Value error, Invalid integer value: '88.1' [type=value_error, input_value='88.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.fg3
  Value error, Invalid integer value: '9.9' [type=value_error, input_value='9.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.fg3a
  Value error, Invalid integer value: '30.5' [type=value_error, input_value='30.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.ft
  Value error, Invalid integer value: '21.3' [type=value_error, input_value='21.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.fta
  Value error, Invalid integer value: '26.3' [type=value_error, input_value='26.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.orb
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.trb
  Value error, Invalid integer value: '40.7' [type=value_error, input_value='40.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.ast
  Value error, Invalid integer value: '21.7' [type=value_error, input_value='21.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.blk
  Value error, Invalid integer value: '4.1' [type=value_error, input_value='4.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.tov
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.pts
  Value error, Invalid integer value: '112.2' [type=value_error, input_value='112.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_fg
  Value error, Invalid integer value: '41.1' [type=value_error, input_value='41.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_fga
  Value error, Invalid integer value: '81.7' [type=value_error, input_value='81.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_fg3
  Value error, Invalid integer value: '12.6' [type=value_error, input_value='12.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_ft
  Value error, Invalid integer value: '19.1' [type=value_error, input_value='19.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_fta
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_orb
  Value error, Invalid integer value: '9.2' [type=value_error, input_value='9.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_trb
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_ast
  Value error, Invalid integer value: '25.9' [type=value_error, input_value='25.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_stl
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_blk
  Value error, Invalid integer value: '3.4' [type=value_error, input_value='3.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_tov
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_pf
  Value error, Invalid integer value: '20.9' [type=value_error, input_value='20.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.opp_pts
  Value error, Invalid integer value: '113.9' [type=value_error, input_value='113.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.fg
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.fga
  Value error, Invalid integer value: '92.6' [type=value_error, input_value='92.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.fg3
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.fg3a
  Value error, Invalid integer value: '34.1' [type=value_error, input_value='34.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.ft
  Value error, Invalid integer value: '19.8' [type=value_error, input_value='19.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.fta
  Value error, Invalid integer value: '25.1' [type=value_error, input_value='25.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.orb
  Value error, Invalid integer value: '13.1' [type=value_error, input_value='13.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.trb
  Value error, Invalid integer value: '42.9' [type=value_error, input_value='42.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.ast
  Value error, Invalid integer value: '24.4' [type=value_error, input_value='24.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.tov
  Value error, Invalid integer value: '10.4' [type=value_error, input_value='10.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.pf
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.pts
  Value error, Invalid integer value: '116.1' [type=value_error, input_value='116.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_fg
  Value error, Invalid integer value: '41.4' [type=value_error, input_value='41.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_fga
  Value error, Invalid integer value: '84.6' [type=value_error, input_value='84.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_fg3
  Value error, Invalid integer value: '13.4' [type=value_error, input_value='13.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_fg3a
  Value error, Invalid integer value: '33.8' [type=value_error, input_value='33.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_ft
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_fta
  Value error, Invalid integer value: '23.2' [type=value_error, input_value='23.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_orb
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_trb
  Value error, Invalid integer value: '43.7' [type=value_error, input_value='43.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_ast
  Value error, Invalid integer value: '25.6' [type=value_error, input_value='25.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_stl
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_blk
  Value error, Invalid integer value: '4.2' [type=value_error, input_value='4.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_tov
  Value error, Invalid integer value: '15.6' [type=value_error, input_value='15.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_pf
  Value error, Invalid integer value: '20.7' [type=value_error, input_value='20.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.opp_pts
  Value error, Invalid integer value: '114.7' [type=value_error, input_value='114.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.fg
  Value error, Invalid integer value: '41.9' [type=value_error, input_value='41.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.fga
  Value error, Invalid integer value: '92.5' [type=value_error, input_value='92.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.fg3
  Value error, Invalid integer value: '10.6' [type=value_error, input_value='10.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.fg3a
  Value error, Invalid integer value: '30.7' [type=value_error, input_value='30.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.ft
  Value error, Invalid integer value: '17.2' [type=value_error, input_value='17.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.fta
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.orb
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.trb
  Value error, Invalid integer value: '44.7' [type=value_error, input_value='44.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.ast
  Value error, Invalid integer value: '23.4' [type=value_error, input_value='23.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.stl
  Value error, Invalid integer value: '9.2' [type=value_error, input_value='9.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.blk
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.tov
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.pts
  Value error, Invalid integer value: '111.6' [type=value_error, input_value='111.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_fg
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_fga
  Value error, Invalid integer value: '82.8' [type=value_error, input_value='82.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_fg3
  Value error, Invalid integer value: '11.1' [type=value_error, input_value='11.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_fg3a
  Value error, Invalid integer value: '30.1' [type=value_error, input_value='30.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_ft
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_fta
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_orb
  Value error, Invalid integer value: '8.6' [type=value_error, input_value='8.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_trb
  Value error, Invalid integer value: '42.2' [type=value_error, input_value='42.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_ast
  Value error, Invalid integer value: '26.4' [type=value_error, input_value='26.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_stl
  Value error, Invalid integer value: '6.1' [type=value_error, input_value='6.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_blk
  Value error, Invalid integer value: '5.4' [type=value_error, input_value='5.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_tov
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_pf
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.opp_pts
  Value error, Invalid integer value: '110.3' [type=value_error, input_value='110.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.fg
  Value error, Invalid integer value: '43.9' [type=value_error, input_value='43.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.fga
  Value error, Invalid integer value: '92.2' [type=value_error, input_value='92.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.fg3a
  Value error, Invalid integer value: '31.2' [type=value_error, input_value='31.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.ft
  Value error, Invalid integer value: '15.6' [type=value_error, input_value='15.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.fta
  Value error, Invalid integer value: '19.4' [type=value_error, input_value='19.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.orb
  Value error, Invalid integer value: '13.2' [type=value_error, input_value='13.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.trb
  Value error, Invalid integer value: '43.2' [type=value_error, input_value='43.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.ast
  Value error, Invalid integer value: '26.1' [type=value_error, input_value='26.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.stl
  Value error, Invalid integer value: '10.1' [type=value_error, input_value='10.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.tov
  Value error, Invalid integer value: '11.9' [type=value_error, input_value='11.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.pts
  Value error, Invalid integer value: '114.1' [type=value_error, input_value='114.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_fga
  Value error, Invalid integer value: '80.1' [type=value_error, input_value='80.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_fg3
  Value error, Invalid integer value: '11.1' [type=value_error, input_value='11.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_fg3a
  Value error, Invalid integer value: '29.1' [type=value_error, input_value='29.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_ft
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_fta
  Value error, Invalid integer value: '23.7' [type=value_error, input_value='23.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_orb
  Value error, Invalid integer value: '8.9' [type=value_error, input_value='8.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_trb
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_ast
  Value error, Invalid integer value: '26.2' [type=value_error, input_value='26.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_stl
  Value error, Invalid integer value: '6.6' [type=value_error, input_value='6.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_blk
  Value error, Invalid integer value: '4.4' [type=value_error, input_value='4.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_tov
  Value error, Invalid integer value: '16.9' [type=value_error, input_value='16.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_pf
  Value error, Invalid integer value: '16.2' [type=value_error, input_value='16.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.opp_pts
  Value error, Invalid integer value: '110.7' [type=value_error, input_value='110.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.fg
  Value error, Invalid integer value: '44.6' [type=value_error, input_value='44.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.fga
  Value error, Invalid integer value: '94.0' [type=value_error, input_value='94.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.fg3
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.fg3a
  Value error, Invalid integer value: '31.6' [type=value_error, input_value='31.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.ft
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.fta
  Value error, Invalid integer value: '17.2' [type=value_error, input_value='17.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.orb
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.trb
  Value error, Invalid integer value: '43.2' [type=value_error, input_value='43.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.stl
  Value error, Invalid integer value: '10.2' [type=value_error, input_value='10.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.tov
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.pf
  Value error, Invalid integer value: '17.4' [type=value_error, input_value='17.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.pts
  Value error, Invalid integer value: '112.8' [type=value_error, input_value='112.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_fg
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_fga
  Value error, Invalid integer value: '82.8' [type=value_error, input_value='82.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_fg3
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_fg3a
  Value error, Invalid integer value: '35.6' [type=value_error, input_value='35.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_ft
  Value error, Invalid integer value: '13.6' [type=value_error, input_value='13.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_fta
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_orb
  Value error, Invalid integer value: '9.4' [type=value_error, input_value='9.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_trb
  Value error, Invalid integer value: '43.6' [type=value_error, input_value='43.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_ast
  Value error, Invalid integer value: '27.6' [type=value_error, input_value='27.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_stl
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_tov
  Value error, Invalid integer value: '17.2' [type=value_error, input_value='17.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_pf
  Value error, Invalid integer value: '14.8' [type=value_error, input_value='14.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.opp_pts
  Value error, Invalid integer value: '106.2' [type=value_error, input_value='106.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.fg
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.fga
  Value error, Invalid integer value: '94.3' [type=value_error, input_value='94.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.fg3
  Value error, Invalid integer value: '10.9' [type=value_error, input_value='10.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.fg3a
  Value error, Invalid integer value: '31.4' [type=value_error, input_value='31.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.ft
  Value error, Invalid integer value: '17.1' [type=value_error, input_value='17.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.fta
  Value error, Invalid integer value: '21.6' [type=value_error, input_value='21.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.orb
  Value error, Invalid integer value: '13.7' [type=value_error, input_value='13.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.trb
  Value error, Invalid integer value: '43.2' [type=value_error, input_value='43.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.ast
  Value error, Invalid integer value: '24.3' [type=value_error, input_value='24.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.stl
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.blk
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.tov
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.pts
  Value error, Invalid integer value: '113.0' [type=value_error, input_value='113.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_fg
  Value error, Invalid integer value: '39.7' [type=value_error, input_value='39.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_fga
  Value error, Invalid integer value: '81.7' [type=value_error, input_value='81.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_fg3
  Value error, Invalid integer value: '14.3' [type=value_error, input_value='14.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_fg3a
  Value error, Invalid integer value: '35.0' [type=value_error, input_value='35.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_ft
  Value error, Invalid integer value: '17.7' [type=value_error, input_value='17.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_fta
  Value error, Invalid integer value: '23.1' [type=value_error, input_value='23.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_orb
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_ast
  Value error, Invalid integer value: '27.3' [type=value_error, input_value='27.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_stl
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_blk
  Value error, Invalid integer value: '5.1' [type=value_error, input_value='5.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_tov
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_pf
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.opp_pts
  Value error, Invalid integer value: '111.3' [type=value_error, input_value='111.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.fg
  Value error, Invalid integer value: '39.2' [type=value_error, input_value='39.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.fga
  Value error, Invalid integer value: '87.6' [type=value_error, input_value='87.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.fg3
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.ft
  Value error, Invalid integer value: '20.9' [type=value_error, input_value='20.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.orb
  Value error, Invalid integer value: '10.9' [type=value_error, input_value='10.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.trb
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.ast
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.stl
  Value error, Invalid integer value: '7.3' [type=value_error, input_value='7.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.blk
  Value error, Invalid integer value: '6.7' [type=value_error, input_value='6.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.tov
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.pf
  Value error, Invalid integer value: '21.7' [type=value_error, input_value='21.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.pts
  Value error, Invalid integer value: '110.5' [type=value_error, input_value='110.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_fg
  Value error, Invalid integer value: '38.9' [type=value_error, input_value='38.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_fga
  Value error, Invalid integer value: '86.3' [type=value_error, input_value='86.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_fg3
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_fg3a
  Value error, Invalid integer value: '32.5' [type=value_error, input_value='32.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_ft
  Value error, Invalid integer value: '21.1' [type=value_error, input_value='21.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_fta
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_orb
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_trb
  Value error, Invalid integer value: '45.0' [type=value_error, input_value='45.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_ast
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_stl
  Value error, Invalid integer value: '6.2' [type=value_error, input_value='6.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_blk
  Value error, Invalid integer value: '3.3' [type=value_error, input_value='3.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_tov
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_pf
  Value error, Invalid integer value: '20.2' [type=value_error, input_value='20.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.opp_pts
  Value error, Invalid integer value: '109.5' [type=value_error, input_value='109.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.fg
  Value error, Invalid integer value: '44.8' [type=value_error, input_value='44.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.fga
  Value error, Invalid integer value: '90.9' [type=value_error, input_value='90.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.fg3
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.fg3a
  Value error, Invalid integer value: '33.4' [type=value_error, input_value='33.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.ft
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.fta
  Value error, Invalid integer value: '21.6' [type=value_error, input_value='21.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.orb
  Value error, Invalid integer value: '14.9' [type=value_error, input_value='14.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.trb
  Value error, Invalid integer value: '44.6' [type=value_error, input_value='44.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.ast
  Value error, Invalid integer value: '27.1' [type=value_error, input_value='27.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.tov
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.pf
  Value error, Invalid integer value: '16.1' [type=value_error, input_value='16.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.pts
  Value error, Invalid integer value: '118.1' [type=value_error, input_value='118.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_fg
  Value error, Invalid integer value: '41.0' [type=value_error, input_value='41.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_fga
  Value error, Invalid integer value: '81.6' [type=value_error, input_value='81.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_fg3a
  Value error, Invalid integer value: '32.1' [type=value_error, input_value='32.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_ft
  Value error, Invalid integer value: '16.4' [type=value_error, input_value='16.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_fta
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_orb
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_trb
  Value error, Invalid integer value: '38.0' [type=value_error, input_value='38.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_ast
  Value error, Invalid integer value: '26.5' [type=value_error, input_value='26.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_stl
  Value error, Invalid integer value: '6.1' [type=value_error, input_value='6.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_tov
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_pf
  Value error, Invalid integer value: '17.4' [type=value_error, input_value='17.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.opp_pts
  Value error, Invalid integer value: '110.9' [type=value_error, input_value='110.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.fg
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.fga
  Value error, Invalid integer value: '96.1' [type=value_error, input_value='96.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.fg3
  Value error, Invalid integer value: '10.4' [type=value_error, input_value='10.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.fg3a
  Value error, Invalid integer value: '33.6' [type=value_error, input_value='33.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.ft
  Value error, Invalid integer value: '16.9' [type=value_error, input_value='16.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.fta
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.orb
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.ast
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.stl
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.blk
  Value error, Invalid integer value: '5.2' [type=value_error, input_value='5.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.tov
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.pf
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.pts
  Value error, Invalid integer value: '113.4' [type=value_error, input_value='113.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_fg
  Value error, Invalid integer value: '39.5' [type=value_error, input_value='39.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_fga
  Value error, Invalid integer value: '81.9' [type=value_error, input_value='81.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_fg3
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_fg3a
  Value error, Invalid integer value: '34.2' [type=value_error, input_value='34.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_ft
  Value error, Invalid integer value: '18.2' [type=value_error, input_value='18.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_fta
  Value error, Invalid integer value: '22.9' [type=value_error, input_value='22.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_orb
  Value error, Invalid integer value: '9.4' [type=value_error, input_value='9.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_trb
  Value error, Invalid integer value: '43.6' [type=value_error, input_value='43.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_ast
  Value error, Invalid integer value: '25.8' [type=value_error, input_value='25.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_stl
  Value error, Invalid integer value: '5.9' [type=value_error, input_value='5.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_tov
  Value error, Invalid integer value: '18.2' [type=value_error, input_value='18.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_pf
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.opp_pts
  Value error, Invalid integer value: '109.4' [type=value_error, input_value='109.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.fg
  Value error, Invalid integer value: '43.2' [type=value_error, input_value='43.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.fga
  Value error, Invalid integer value: '91.2' [type=value_error, input_value='91.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.fg3a
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.ft
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.fta
  Value error, Invalid integer value: '26.2' [type=value_error, input_value='26.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.orb
  Value error, Invalid integer value: '12.7' [type=value_error, input_value='12.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.ast
  Value error, Invalid integer value: '25.2' [type=value_error, input_value='25.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.stl
  Value error, Invalid integer value: '10.3' [type=value_error, input_value='10.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.tov
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.pts
  Value error, Invalid integer value: '117.8' [type=value_error, input_value='117.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_fg
  Value error, Invalid integer value: '42.7' [type=value_error, input_value='42.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_fga
  Value error, Invalid integer value: '87.2' [type=value_error, input_value='87.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_fg3
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_fg3a
  Value error, Invalid integer value: '32.2' [type=value_error, input_value='32.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_ft
  Value error, Invalid integer value: '17.7' [type=value_error, input_value='17.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_fta
  Value error, Invalid integer value: '22.2' [type=value_error, input_value='22.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_orb
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_trb
  Value error, Invalid integer value: '42.8' [type=value_error, input_value='42.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_ast
  Value error, Invalid integer value: '27.7' [type=value_error, input_value='27.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_stl
  Value error, Invalid integer value: '6.3' [type=value_error, input_value='6.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_tov
  Value error, Invalid integer value: '15.7' [type=value_error, input_value='15.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.opp_pts
  Value error, Invalid integer value: '116.8' [type=value_error, input_value='116.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.fga
  Value error, Invalid integer value: '87.8' [type=value_error, input_value='87.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.fg3a
  Value error, Invalid integer value: '31.8' [type=value_error, input_value='31.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.ft
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.orb
  Value error, Invalid integer value: '11.6' [type=value_error, input_value='11.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.trb
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.ast
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.stl
  Value error, Invalid integer value: '9.6' [type=value_error, input_value='9.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.tov
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.pf
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.pts
  Value error, Invalid integer value: '110.5' [type=value_error, input_value='110.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_fg
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_fga
  Value error, Invalid integer value: '79.7' [type=value_error, input_value='79.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_fg3
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_fg3a
  Value error, Invalid integer value: '32.1' [type=value_error, input_value='32.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_ft
  Value error, Invalid integer value: '18.2' [type=value_error, input_value='18.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_fta
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_orb
  Value error, Invalid integer value: '8.1' [type=value_error, input_value='8.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_trb
  Value error, Invalid integer value: '41.3' [type=value_error, input_value='41.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_stl
  Value error, Invalid integer value: '6.6' [type=value_error, input_value='6.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_blk
  Value error, Invalid integer value: '5.2' [type=value_error, input_value='5.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_tov
  Value error, Invalid integer value: '17.6' [type=value_error, input_value='17.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.opp_pts
  Value error, Invalid integer value: '114.8' [type=value_error, input_value='114.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.fg
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.fga
  Value error, Invalid integer value: '90.4' [type=value_error, input_value='90.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.fg3
  Value error, Invalid integer value: '8.9' [type=value_error, input_value='8.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.fg3a
  Value error, Invalid integer value: '29.7' [type=value_error, input_value='29.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.ft
  Value error, Invalid integer value: '17.8' [type=value_error, input_value='17.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.fta
  Value error, Invalid integer value: '23.1' [type=value_error, input_value='23.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.orb
  Value error, Invalid integer value: '11.9' [type=value_error, input_value='11.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.trb
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.ast
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.blk
  Value error, Invalid integer value: '4.7' [type=value_error, input_value='4.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.tov
  Value error, Invalid integer value: '12.3' [type=value_error, input_value='12.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.pf
  Value error, Invalid integer value: '20.6' [type=value_error, input_value='20.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.pts
  Value error, Invalid integer value: '111.3' [type=value_error, input_value='111.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_fg
  Value error, Invalid integer value: '39.5' [type=value_error, input_value='39.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_fga
  Value error, Invalid integer value: '81.8' [type=value_error, input_value='81.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_fg3a
  Value error, Invalid integer value: '29.3' [type=value_error, input_value='29.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_ft
  Value error, Invalid integer value: '18.9' [type=value_error, input_value='18.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_fta
  Value error, Invalid integer value: '22.9' [type=value_error, input_value='22.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_orb
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_trb
  Value error, Invalid integer value: '42.1' [type=value_error, input_value='42.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_ast
  Value error, Invalid integer value: '25.1' [type=value_error, input_value='25.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_stl
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_blk
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_tov
  Value error, Invalid integer value: '16.2' [type=value_error, input_value='16.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_pf
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.opp_pts
  Value error, Invalid integer value: '108.5' [type=value_error, input_value='108.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.fg
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.fga
  Value error, Invalid integer value: '90.3' [type=value_error, input_value='90.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.fg3a
  Value error, Invalid integer value: '32.9' [type=value_error, input_value='32.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.ft
  Value error, Invalid integer value: '17.7' [type=value_error, input_value='17.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.fta
  Value error, Invalid integer value: '22.8' [type=value_error, input_value='22.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.orb
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.trb
  Value error, Invalid integer value: '42.4' [type=value_error, input_value='42.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.ast
  Value error, Invalid integer value: '22.2' [type=value_error, input_value='22.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.stl
  Value error, Invalid integer value: '9.1' [type=value_error, input_value='9.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.tov
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.pf
  Value error, Invalid integer value: '19.3' [type=value_error, input_value='19.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.pts
  Value error, Invalid integer value: '109.3' [type=value_error, input_value='109.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_fg
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_fga
  Value error, Invalid integer value: '80.5' [type=value_error, input_value='80.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_fg3
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_fg3a
  Value error, Invalid integer value: '35.3' [type=value_error, input_value='35.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_ft
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_fta
  Value error, Invalid integer value: '22.6' [type=value_error, input_value='22.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_orb
  Value error, Invalid integer value: '7.8' [type=value_error, input_value='7.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_trb
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_ast
  Value error, Invalid integer value: '26.7' [type=value_error, input_value='26.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_stl
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_blk
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_tov
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_pf
  Value error, Invalid integer value: '19.3' [type=value_error, input_value='19.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.opp_pts
  Value error, Invalid integer value: '111.8' [type=value_error, input_value='111.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.fg
  Value error, Invalid integer value: '41.9' [type=value_error, input_value='41.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.fga
  Value error, Invalid integer value: '91.4' [type=value_error, input_value='91.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.fg3a
  Value error, Invalid integer value: '32.1' [type=value_error, input_value='32.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.ft
  Value error, Invalid integer value: '18.1' [type=value_error, input_value='18.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.fta
  Value error, Invalid integer value: '23.1' [type=value_error, input_value='23.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.orb
  Value error, Invalid integer value: '12.7' [type=value_error, input_value='12.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.trb
  Value error, Invalid integer value: '43.1' [type=value_error, input_value='43.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.ast
  Value error, Invalid integer value: '24.6' [type=value_error, input_value='24.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.stl
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.blk
  Value error, Invalid integer value: '5.2' [type=value_error, input_value='5.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.tov
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.pf
  Value error, Invalid integer value: '20.2' [type=value_error, input_value='20.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.pts
  Value error, Invalid integer value: '113.1' [type=value_error, input_value='113.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_fg
  Value error, Invalid integer value: '40.4' [type=value_error, input_value='40.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_fga
  Value error, Invalid integer value: '82.7' [type=value_error, input_value='82.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_fg3
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_ft
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_fta
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_orb
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_trb
  Value error, Invalid integer value: '42.6' [type=value_error, input_value='42.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_ast
  Value error, Invalid integer value: '25.9' [type=value_error, input_value='25.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_stl
  Value error, Invalid integer value: '6.1' [type=value_error, input_value='6.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_blk
  Value error, Invalid integer value: '4.7' [type=value_error, input_value='4.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_tov
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_pf
  Value error, Invalid integer value: '19.4' [type=value_error, input_value='19.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.opp_pts
  Value error, Invalid integer value: '111.1' [type=value_error, input_value='111.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.fg
  Value error, Invalid integer value: '43.6' [type=value_error, input_value='43.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.fga
  Value error, Invalid integer value: '92.3' [type=value_error, input_value='92.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.fg3
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.fg3a
  Value error, Invalid integer value: '32.0' [type=value_error, input_value='32.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.ft
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.fta
  Value error, Invalid integer value: '25.3' [type=value_error, input_value='25.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.orb
  Value error, Invalid integer value: '12.9' [type=value_error, input_value='12.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.trb
  Value error, Invalid integer value: '42.7' [type=value_error, input_value='42.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.ast
  Value error, Invalid integer value: '24.3' [type=value_error, input_value='24.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.stl
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.blk
  Value error, Invalid integer value: '6.7' [type=value_error, input_value='6.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.tov
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.pf
  Value error, Invalid integer value: '21.1' [type=value_error, input_value='21.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.pts
  Value error, Invalid integer value: '116.9' [type=value_error, input_value='116.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_fg
  Value error, Invalid integer value: '40.4' [type=value_error, input_value='40.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_fga
  Value error, Invalid integer value: '82.8' [type=value_error, input_value='82.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_fg3
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_fg3a
  Value error, Invalid integer value: '31.3' [type=value_error, input_value='31.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_ft
  Value error, Invalid integer value: '19.8' [type=value_error, input_value='19.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_fta
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_orb
  Value error, Invalid integer value: '8.7' [type=value_error, input_value='8.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_trb
  Value error, Invalid integer value: '41.1' [type=value_error, input_value='41.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_ast
  Value error, Invalid integer value: '26.7' [type=value_error, input_value='26.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_stl
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_tov
  Value error, Invalid integer value: '16.4' [type=value_error, input_value='16.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_pf
  Value error, Invalid integer value: '20.8' [type=value_error, input_value='20.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.opp_pts
  Value error, Invalid integer value: '111.9' [type=value_error, input_value='111.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.fg
  Value error, Invalid integer value: '41.4' [type=value_error, input_value='41.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.fga
  Value error, Invalid integer value: '91.2' [type=value_error, input_value='91.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.fg3
  Value error, Invalid integer value: '9.4' [type=value_error, input_value='9.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.fg3a
  Value error, Invalid integer value: '28.6' [type=value_error, input_value='28.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.ft
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.fta
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.orb
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.trb
  Value error, Invalid integer value: '44.8' [type=value_error, input_value='44.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.ast
  Value error, Invalid integer value: '20.2' [type=value_error, input_value='20.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.stl
  Value error, Invalid integer value: '10.6' [type=value_error, input_value='10.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.blk
  Value error, Invalid integer value: '3.4' [type=value_error, input_value='3.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.tov
  Value error, Invalid integer value: '12.4' [type=value_error, input_value='12.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.pts
  Value error, Invalid integer value: '111.8' [type=value_error, input_value='111.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_fg
  Value error, Invalid integer value: '41.8' [type=value_error, input_value='41.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_fga
  Value error, Invalid integer value: '82.4' [type=value_error, input_value='82.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_fg3
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_fg3a
  Value error, Invalid integer value: '31.8' [type=value_error, input_value='31.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_ft
  Value error, Invalid integer value: '16.4' [type=value_error, input_value='16.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_fta
  Value error, Invalid integer value: '20.6' [type=value_error, input_value='20.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_orb
  Value error, Invalid integer value: '7.6' [type=value_error, input_value='7.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_trb
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_ast
  Value error, Invalid integer value: '27.2' [type=value_error, input_value='27.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_stl
  Value error, Invalid integer value: '7.6' [type=value_error, input_value='7.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_tov
  Value error, Invalid integer value: '15.2' [type=value_error, input_value='15.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_pf
  Value error, Invalid integer value: '19.6' [type=value_error, input_value='19.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.opp_pts
  Value error, Invalid integer value: '112.2' [type=value_error, input_value='112.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.fg
  Value error, Invalid integer value: '40.8' [type=value_error, input_value='40.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.fga
  Value error, Invalid integer value: '90.2' [type=value_error, input_value='90.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.fg3
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.ft
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.fta
  Value error, Invalid integer value: '24.2' [type=value_error, input_value='24.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.orb
  Value error, Invalid integer value: '12.4' [type=value_error, input_value='12.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.trb
  Value error, Invalid integer value: '42.6' [type=value_error, input_value='42.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.ast
  Value error, Invalid integer value: '23.9' [type=value_error, input_value='23.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.stl
  Value error, Invalid integer value: '8.9' [type=value_error, input_value='8.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.blk
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.tov
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.pts
  Value error, Invalid integer value: '111.0' [type=value_error, input_value='111.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_fg
  Value error, Invalid integer value: '39.9' [type=value_error, input_value='39.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_fga
  Value error, Invalid integer value: '81.6' [type=value_error, input_value='81.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_fg3a
  Value error, Invalid integer value: '32.7' [type=value_error, input_value='32.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_ft
  Value error, Invalid integer value: '17.6' [type=value_error, input_value='17.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_fta
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_orb
  Value error, Invalid integer value: '9.1' [type=value_error, input_value='9.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_trb
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_ast
  Value error, Invalid integer value: '25.8' [type=value_error, input_value='25.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_stl
  Value error, Invalid integer value: '5.4' [type=value_error, input_value='5.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_tov
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_pf
  Value error, Invalid integer value: '20.2' [type=value_error, input_value='20.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.opp_pts
  Value error, Invalid integer value: '110.0' [type=value_error, input_value='110.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.fg
  Value error, Invalid integer value: '43.7' [type=value_error, input_value='43.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.fga
  Value error, Invalid integer value: '93.3' [type=value_error, input_value='93.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.fg3
  Value error, Invalid integer value: '11.1' [type=value_error, input_value='11.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.fg3a
  Value error, Invalid integer value: '31.6' [type=value_error, input_value='31.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.ft
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.fta
  Value error, Invalid integer value: '22.2' [type=value_error, input_value='22.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.orb
  Value error, Invalid integer value: '13.2' [type=value_error, input_value='13.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.trb
  Value error, Invalid integer value: '43.7' [type=value_error, input_value='43.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.ast
  Value error, Invalid integer value: '23.9' [type=value_error, input_value='23.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.stl
  Value error, Invalid integer value: '10.2' [type=value_error, input_value='10.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.blk
  Value error, Invalid integer value: '4.7' [type=value_error, input_value='4.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.tov
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.pts
  Value error, Invalid integer value: '116.1' [type=value_error, input_value='116.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_fg
  Value error, Invalid integer value: '41.2' [type=value_error, input_value='41.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_fga
  Value error, Invalid integer value: '83.6' [type=value_error, input_value='83.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_fg3
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_fg3a
  Value error, Invalid integer value: '32.5' [type=value_error, input_value='32.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_ft
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_fta
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_orb
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_trb
  Value error, Invalid integer value: '41.8' [type=value_error, input_value='41.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_ast
  Value error, Invalid integer value: '26.9' [type=value_error, input_value='26.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_stl
  Value error, Invalid integer value: '7.1' [type=value_error, input_value='7.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_blk
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_tov
  Value error, Invalid integer value: '16.6' [type=value_error, input_value='16.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_pf
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.opp_pts
  Value error, Invalid integer value: '113.8' [type=value_error, input_value='113.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.fg
  Value error, Invalid integer value: '39.5' [type=value_error, input_value='39.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.fga
  Value error, Invalid integer value: '88.4' [type=value_error, input_value='88.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.fg3
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.fg3a
  Value error, Invalid integer value: '31.2' [type=value_error, input_value='31.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.ft
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.fta
  Value error, Invalid integer value: '24.2' [type=value_error, input_value='24.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.orb
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.trb
  Value error, Invalid integer value: '42.4' [type=value_error, input_value='42.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.ast
  Value error, Invalid integer value: '21.7' [type=value_error, input_value='21.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.stl
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.blk
  Value error, Invalid integer value: '4.4' [type=value_error, input_value='4.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.tov
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.pf
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.pts
  Value error, Invalid integer value: '107.6' [type=value_error, input_value='107.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_fg
  Value error, Invalid integer value: '41.1' [type=value_error, input_value='41.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_fga
  Value error, Invalid integer value: '82.4' [type=value_error, input_value='82.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_fg3
  Value error, Invalid integer value: '13.6' [type=value_error, input_value='13.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_fg3a
  Value error, Invalid integer value: '35.4' [type=value_error, input_value='35.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_ft
  Value error, Invalid integer value: '16.2' [type=value_error, input_value='16.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_fta
  Value error, Invalid integer value: '21.4' [type=value_error, input_value='21.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_orb
  Value error, Invalid integer value: '9.9' [type=value_error, input_value='9.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_trb
  Value error, Invalid integer value: '43.4' [type=value_error, input_value='43.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_ast
  Value error, Invalid integer value: '25.7' [type=value_error, input_value='25.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_stl
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_blk
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_tov
  Value error, Invalid integer value: '15.6' [type=value_error, input_value='15.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_pf
  Value error, Invalid integer value: '20.6' [type=value_error, input_value='20.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.opp_pts
  Value error, Invalid integer value: '111.9' [type=value_error, input_value='111.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.fg
  Value error, Invalid integer value: '39.9' [type=value_error, input_value='39.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.fga
  Value error, Invalid integer value: '92.4' [type=value_error, input_value='92.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.fg3
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.fg3a
  Value error, Invalid integer value: '33.7' [type=value_error, input_value='33.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.ft
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.fta
  Value error, Invalid integer value: '24.2' [type=value_error, input_value='24.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.orb
  Value error, Invalid integer value: '12.8' [type=value_error, input_value='12.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.trb
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.ast
  Value error, Invalid integer value: '23.1' [type=value_error, input_value='23.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.stl
  Value error, Invalid integer value: '8.7' [type=value_error, input_value='8.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.blk
  Value error, Invalid integer value: '6.1' [type=value_error, input_value='6.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.tov
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.pf
  Value error, Invalid integer value: '20.1' [type=value_error, input_value='20.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.pts
  Value error, Invalid integer value: '109.3' [type=value_error, input_value='109.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_fg
  Value error, Invalid integer value: '39.6' [type=value_error, input_value='39.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_fga
  Value error, Invalid integer value: '82.2' [type=value_error, input_value='82.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_fg3
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_fg3a
  Value error, Invalid integer value: '32.6' [type=value_error, input_value='32.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_ft
  Value error, Invalid integer value: '18.1' [type=value_error, input_value='18.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_fta
  Value error, Invalid integer value: '23.4' [type=value_error, input_value='23.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_orb
  Value error, Invalid integer value: '9.6' [type=value_error, input_value='9.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_trb
  Value error, Invalid integer value: '44.7' [type=value_error, input_value='44.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_ast
  Value error, Invalid integer value: '26.8' [type=value_error, input_value='26.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_stl
  Value error, Invalid integer value: '5.4' [type=value_error, input_value='5.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_blk
  Value error, Invalid integer value: '4.9' [type=value_error, input_value='4.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_tov
  Value error, Invalid integer value: '17.1' [type=value_error, input_value='17.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_pf
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.opp_pts
  Value error, Invalid integer value: '109.1' [type=value_error, input_value='109.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.fg
  Value error, Invalid integer value: '45.0' [type=value_error, input_value='45.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.fga
  Value error, Invalid integer value: '92.5' [type=value_error, input_value='92.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.fg3
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.fg3a
  Value error, Invalid integer value: '29.2' [type=value_error, input_value='29.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.ft
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.fta
  Value error, Invalid integer value: '25.2' [type=value_error, input_value='25.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.orb
  Value error, Invalid integer value: '13.7' [type=value_error, input_value='13.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.trb
  Value error, Invalid integer value: '44.4' [type=value_error, input_value='44.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.ast
  Value error, Invalid integer value: '25.7' [type=value_error, input_value='25.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.stl
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.blk
  Value error, Invalid integer value: '4.1' [type=value_error, input_value='4.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.tov
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.pf
  Value error, Invalid integer value: '21.6' [type=value_error, input_value='21.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.pts
  Value error, Invalid integer value: '121.1' [type=value_error, input_value='121.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_fg
  Value error, Invalid integer value: '42.6' [type=value_error, input_value='42.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_fga
  Value error, Invalid integer value: '84.5' [type=value_error, input_value='84.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_fg3
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_fg3a
  Value error, Invalid integer value: '31.3' [type=value_error, input_value='31.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_ft
  Value error, Invalid integer value: '20.9' [type=value_error, input_value='20.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_orb
  Value error, Invalid integer value: '9.4' [type=value_error, input_value='9.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_trb
  Value error, Invalid integer value: '39.9' [type=value_error, input_value='39.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_ast
  Value error, Invalid integer value: '26.3' [type=value_error, input_value='26.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_stl
  Value error, Invalid integer value: '6.7' [type=value_error, input_value='6.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_tov
  Value error, Invalid integer value: '15.9' [type=value_error, input_value='15.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_pf
  Value error, Invalid integer value: '19.3' [type=value_error, input_value='19.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.opp_pts
  Value error, Invalid integer value: '116.9' [type=value_error, input_value='116.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.fg
  Value error, Invalid integer value: '43.4' [type=value_error, input_value='43.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.fga
  Value error, Invalid integer value: '93.5' [type=value_error, input_value='93.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.fg3
  Value error, Invalid integer value: '10.4' [type=value_error, input_value='10.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.fg3a
  Value error, Invalid integer value: '31.9' [type=value_error, input_value='31.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.ft
  Value error, Invalid integer value: '16.1' [type=value_error, input_value='16.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.fta
  Value error, Invalid integer value: '19.9' [type=value_error, input_value='19.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.orb
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.trb
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.ast
  Value error, Invalid integer value: '23.6' [type=value_error, input_value='23.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.stl
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.blk
  Value error, Invalid integer value: '4.2' [type=value_error, input_value='4.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.tov
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.pf
  Value error, Invalid integer value: '19.2' [type=value_error, input_value='19.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.pts
  Value error, Invalid integer value: '113.3' [type=value_error, input_value='113.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_fg
  Value error, Invalid integer value: '41.7' [type=value_error, input_value='41.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_fga
  Value error, Invalid integer value: '82.6' [type=value_error, input_value='82.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_fg3
  Value error, Invalid integer value: '13.2' [type=value_error, input_value='13.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_fg3a
  Value error, Invalid integer value: '33.9' [type=value_error, input_value='33.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_ft
  Value error, Invalid integer value: '19.3' [type=value_error, input_value='19.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_fta
  Value error, Invalid integer value: '22.6' [type=value_error, input_value='22.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_orb
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_trb
  Value error, Invalid integer value: '42.4' [type=value_error, input_value='42.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_ast
  Value error, Invalid integer value: '27.7' [type=value_error, input_value='27.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_stl
  Value error, Invalid integer value: '6.8' [type=value_error, input_value='6.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_blk
  Value error, Invalid integer value: '3.1' [type=value_error, input_value='3.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_tov
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_pf
  Value error, Invalid integer value: '16.2' [type=value_error, input_value='16.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.opp_pts
  Value error, Invalid integer value: '115.9' [type=value_error, input_value='115.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.fg
  Value error, Invalid integer value: '42.9' [type=value_error, input_value='42.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.fga
  Value error, Invalid integer value: '89.6' [type=value_error, input_value='89.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.fg3
  Value error, Invalid integer value: '10.6' [type=value_error, input_value='10.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.fg3a
  Value error, Invalid integer value: '31.8' [type=value_error, input_value='31.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.ft
  Value error, Invalid integer value: '19.4' [type=value_error, input_value='19.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.fta
  Value error, Invalid integer value: '24.1' [type=value_error, input_value='24.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.orb
  Value error, Invalid integer value: '12.2' [type=value_error, input_value='12.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.trb
  Value error, Invalid integer value: '42.1' [type=value_error, input_value='42.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.ast
  Value error, Invalid integer value: '26.8' [type=value_error, input_value='26.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.stl
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.tov
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.pf
  Value error, Invalid integer value: '20.2' [type=value_error, input_value='20.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.pts
  Value error, Invalid integer value: '115.7' [type=value_error, input_value='115.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_fg
  Value error, Invalid integer value: '39.3' [type=value_error, input_value='39.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_fga
  Value error, Invalid integer value: '80.3' [type=value_error, input_value='80.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_fg3
  Value error, Invalid integer value: '12.1' [type=value_error, input_value='12.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_fg3a
  Value error, Invalid integer value: '30.5' [type=value_error, input_value='30.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_ft
  Value error, Invalid integer value: '18.4' [type=value_error, input_value='18.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_fta
  Value error, Invalid integer value: '22.6' [type=value_error, input_value='22.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_orb
  Value error, Invalid integer value: '7.9' [type=value_error, input_value='7.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_trb
  Value error, Invalid integer value: '39.6' [type=value_error, input_value='39.6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_ast
  Value error, Invalid integer value: '24.8' [type=value_error, input_value='24.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_stl
  Value error, Invalid integer value: '4.9' [type=value_error, input_value='4.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_tov
  Value error, Invalid integer value: '17.2' [type=value_error, input_value='17.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.opp_pts
  Value error, Invalid integer value: '109.1' [type=value_error, input_value='109.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.fg
  Value error, Invalid integer value: '42.8' [type=value_error, input_value='42.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.fga
  Value error, Invalid integer value: '93.9' [type=value_error, input_value='93.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.fg3
  Value error, Invalid integer value: '11.4' [type=value_error, input_value='11.4', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.fg3a
  Value error, Invalid integer value: '33.7' [type=value_error, input_value='33.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.ft
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.fta
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.orb
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.trb
  Value error, Invalid integer value: '45.3' [type=value_error, input_value='45.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.ast
  Value error, Invalid integer value: '22.3' [type=value_error, input_value='22.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.stl
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.blk
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.tov
  Value error, Invalid integer value: '12.9' [type=value_error, input_value='12.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.pf
  Value error, Invalid integer value: '20.7' [type=value_error, input_value='20.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.pts
  Value error, Invalid integer value: '113.8' [type=value_error, input_value='113.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_fg
  Value error, Invalid integer value: '39.3' [type=value_error, input_value='39.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_fga
  Value error, Invalid integer value: '83.8' [type=value_error, input_value='83.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_fg3
  Value error, Invalid integer value: '11.2' [type=value_error, input_value='11.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_fg3a
  Value error, Invalid integer value: '32.3' [type=value_error, input_value='32.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_ft
  Value error, Invalid integer value: '18.9' [type=value_error, input_value='18.9', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_fta
  Value error, Invalid integer value: '24.2' [type=value_error, input_value='24.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_orb
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_trb
  Value error, Invalid integer value: '43.1' [type=value_error, input_value='43.1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_ast
  Value error, Invalid integer value: '26.8' [type=value_error, input_value='26.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_stl
  Value error, Invalid integer value: '7.7' [type=value_error, input_value='7.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_tov
  Value error, Invalid integer value: '17.2' [type=value_error, input_value='17.2', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.opp_pts
  Value error, Invalid integer value: '108.7' [type=value_error, input_value='108.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.fg
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.fga
  Value error, Invalid integer value: '95.7' [type=value_error, input_value='95.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.fg3
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.fg3a
  Value error, Invalid integer value: '33.3' [type=value_error, input_value='33.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.ft
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.fta
  Value error, Invalid integer value: '30.7' [type=value_error, input_value='30.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.orb
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.trb
  Value error, Invalid integer value: '46.0' [type=value_error, input_value='46.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.ast
  Value error, Invalid integer value: '23.7' [type=value_error, input_value='23.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.stl
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.blk
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.tov
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.pf
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.pts
  Value error, Invalid integer value: '121.3' [type=value_error, input_value='121.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_fg
  Value error, Invalid integer value: '42.7' [type=value_error, input_value='42.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_fga
  Value error, Invalid integer value: '86.7' [type=value_error, input_value='86.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_fg3
  Value error, Invalid integer value: '9.7' [type=value_error, input_value='9.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_fg3a
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_ft
  Value error, Invalid integer value: '20.7' [type=value_error, input_value='20.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_fta
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_orb
  Value error, Invalid integer value: '7.7' [type=value_error, input_value='7.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_trb
  Value error, Invalid integer value: '42.3' [type=value_error, input_value='42.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_ast
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_stl
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_blk
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_tov
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_pf
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.opp_pts
  Value error, Invalid integer value: '115.7' [type=value_error, input_value='115.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.fg
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.fga
  Value error, Invalid integer value: '88.5' [type=value_error, input_value='88.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.fg3
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.fg3a
  Value error, Invalid integer value: '27.8' [type=value_error, input_value='27.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.ft
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.fta
  Value error, Invalid integer value: '17.8' [type=value_error, input_value='17.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.orb
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.trb
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.ast
  Value error, Invalid integer value: '21.0' [type=value_error, input_value='21.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.stl
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.tov
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.pf
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.pts
  Value error, Invalid integer value: '102.3' [type=value_error, input_value='102.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_fg
  Value error, Invalid integer value: '41.3' [type=value_error, input_value='41.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_fga
  Value error, Invalid integer value: '86.3' [type=value_error, input_value='86.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_fg3
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_fg3a
  Value error, Invalid integer value: '38.3' [type=value_error, input_value='38.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_ft
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_fta
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_orb
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_trb
  Value error, Invalid integer value: '47.8' [type=value_error, input_value='47.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_ast
  Value error, Invalid integer value: '27.3' [type=value_error, input_value='27.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_stl
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_blk
  Value error, Invalid integer value: '6.3' [type=value_error, input_value='6.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_tov
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_pf
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.opp_pts
  Value error, Invalid integer value: '110.0' [type=value_error, input_value='110.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.fga
  Value error, Invalid integer value: '89.0' [type=value_error, input_value='89.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.fg3
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.fg3a
  Value error, Invalid integer value: '26.3' [type=value_error, input_value='26.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.ft
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.orb
  Value error, Invalid integer value: '12.3' [type=value_error, input_value='12.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.ast
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.stl
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.blk
  Value error, Invalid integer value: '2.3' [type=value_error, input_value='2.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.tov
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.pts
  Value error, Invalid integer value: '106.0' [type=value_error, input_value='106.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_fg
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_fga
  Value error, Invalid integer value: '80.0' [type=value_error, input_value='80.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_fg3a
  Value error, Invalid integer value: '32.8' [type=value_error, input_value='32.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_ft
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_fta
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_orb
  Value error, Invalid integer value: '7.8' [type=value_error, input_value='7.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_trb
  Value error, Invalid integer value: '40.3' [type=value_error, input_value='40.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_ast
  Value error, Invalid integer value: '26.8' [type=value_error, input_value='26.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_stl
  Value error, Invalid integer value: '6.3' [type=value_error, input_value='6.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_blk
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_tov
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_pf
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.opp_pts
  Value error, Invalid integer value: '113.5' [type=value_error, input_value='113.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.fg
  Value error, Invalid integer value: '46.5' [type=value_error, input_value='46.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.fga
  Value error, Invalid integer value: '91.5' [type=value_error, input_value='91.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.fg3
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.fg3a
  Value error, Invalid integer value: '33.3' [type=value_error, input_value='33.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.ft
  Value error, Invalid integer value: '19.8' [type=value_error, input_value='19.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.fta
  Value error, Invalid integer value: '24.8' [type=value_error, input_value='24.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.orb
  Value error, Invalid integer value: '12.8' [type=value_error, input_value='12.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.trb
  Value error, Invalid integer value: '41.8' [type=value_error, input_value='41.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.ast
  Value error, Invalid integer value: '31.8' [type=value_error, input_value='31.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.blk
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.tov
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.pts
  Value error, Invalid integer value: '126.0' [type=value_error, input_value='126.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_fg
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_fga
  Value error, Invalid integer value: '81.3' [type=value_error, input_value='81.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_fg3
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_fg3a
  Value error, Invalid integer value: '32.5' [type=value_error, input_value='32.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_ft
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_orb
  Value error, Invalid integer value: '7.8' [type=value_error, input_value='7.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_trb
  Value error, Invalid integer value: '38.8' [type=value_error, input_value='38.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_ast
  Value error, Invalid integer value: '28.3' [type=value_error, input_value='28.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_stl
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_blk
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_tov
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.opp_pts
  Value error, Invalid integer value: '110.5' [type=value_error, input_value='110.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.fg
  Value error, Invalid integer value: '39.3' [type=value_error, input_value='39.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.fga
  Value error, Invalid integer value: '94.0' [type=value_error, input_value='94.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.fg3
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.fg3a
  Value error, Invalid integer value: '35.7' [type=value_error, input_value='35.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.ft
  Value error, Invalid integer value: '14.7' [type=value_error, input_value='14.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.fta
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.orb
  Value error, Invalid integer value: '15.7' [type=value_error, input_value='15.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.trb
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.ast
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.stl
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.blk
  Value error, Invalid integer value: '7.7' [type=value_error, input_value='7.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.tov
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.pf
  Value error, Invalid integer value: '17.7' [type=value_error, input_value='17.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.pts
  Value error, Invalid integer value: '104.7' [type=value_error, input_value='104.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_fg
  Value error, Invalid integer value: '39.7' [type=value_error, input_value='39.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_fga
  Value error, Invalid integer value: '79.7' [type=value_error, input_value='79.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_fg3a
  Value error, Invalid integer value: '29.7' [type=value_error, input_value='29.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_ft
  Value error, Invalid integer value: '14.3' [type=value_error, input_value='14.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_fta
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_orb
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_trb
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_ast
  Value error, Invalid integer value: '28.3' [type=value_error, input_value='28.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_stl
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_blk
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_tov
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_pf
  Value error, Invalid integer value: '19.7' [type=value_error, input_value='19.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.opp_pts
  Value error, Invalid integer value: '104.3' [type=value_error, input_value='104.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.fg
  Value error, Invalid integer value: '37.8' [type=value_error, input_value='37.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.fga
  Value error, Invalid integer value: '86.8' [type=value_error, input_value='86.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.fg3
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.fg3a
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.ft
  Value error, Invalid integer value: '16.0' [type=value_error, input_value='16.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.fta
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.orb
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.trb
  Value error, Invalid integer value: '43.5' [type=value_error, input_value='43.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.ast
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.stl
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.tov
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.pf
  Value error, Invalid integer value: '19.0' [type=value_error, input_value='19.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.pts
  Value error, Invalid integer value: '104.8' [type=value_error, input_value='104.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_fg
  Value error, Invalid integer value: '38.8' [type=value_error, input_value='38.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_fga
  Value error, Invalid integer value: '81.8' [type=value_error, input_value='81.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_fg3a
  Value error, Invalid integer value: '33.8' [type=value_error, input_value='33.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_ft
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_fta
  Value error, Invalid integer value: '20.8' [type=value_error, input_value='20.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_orb
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_trb
  Value error, Invalid integer value: '41.3' [type=value_error, input_value='41.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_ast
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_blk
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_tov
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_pf
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.opp_pts
  Value error, Invalid integer value: '104.5' [type=value_error, input_value='104.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.fg
  Value error, Invalid integer value: '38.5' [type=value_error, input_value='38.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.fga
  Value error, Invalid integer value: '88.0' [type=value_error, input_value='88.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.fg3
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.fg3a
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.ft
  Value error, Invalid integer value: '21.0' [type=value_error, input_value='21.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.orb
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.trb
  Value error, Invalid integer value: '46.0' [type=value_error, input_value='46.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.ast
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.tov
  Value error, Invalid integer value: '16.0' [type=value_error, input_value='16.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.pf
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.pts
  Value error, Invalid integer value: '107.5' [type=value_error, input_value='107.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_fg
  Value error, Invalid integer value: '37.0' [type=value_error, input_value='37.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_fga
  Value error, Invalid integer value: '75.0' [type=value_error, input_value='75.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_fg3a
  Value error, Invalid integer value: '36.5' [type=value_error, input_value='36.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_ft
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_fta
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_orb
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_trb
  Value error, Invalid integer value: '32.5' [type=value_error, input_value='32.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_ast
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_stl
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_tov
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_pf
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.opp_pts
  Value error, Invalid integer value: '105.5' [type=value_error, input_value='105.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.fg
  Value error, Invalid integer value: '46.0' [type=value_error, input_value='46.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.fga
  Value error, Invalid integer value: '89.5' [type=value_error, input_value='89.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.fg3a
  Value error, Invalid integer value: '28.5' [type=value_error, input_value='28.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.ft
  Value error, Invalid integer value: '16.0' [type=value_error, input_value='16.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.orb
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.trb
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.stl
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.tov
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.pf
  Value error, Invalid integer value: '19.0' [type=value_error, input_value='19.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.pts
  Value error, Invalid integer value: '119.0' [type=value_error, input_value='119.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_fg
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_fga
  Value error, Invalid integer value: '81.0' [type=value_error, input_value='81.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_fg3
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_fg3a
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_ft
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_fta
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_orb
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_trb
  Value error, Invalid integer value: '36.5' [type=value_error, input_value='36.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_ast
  Value error, Invalid integer value: '29.5' [type=value_error, input_value='29.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_stl
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_tov
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_pf
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.opp_pts
  Value error, Invalid integer value: '114.0' [type=value_error, input_value='114.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.fga
  Value error, Invalid integer value: '87.3' [type=value_error, input_value='87.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.fg3
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.fg3a
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.ft
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.fta
  Value error, Invalid integer value: '31.8' [type=value_error, input_value='31.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.orb
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.trb
  Value error, Invalid integer value: '43.5' [type=value_error, input_value='43.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.ast
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.stl
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.blk
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.tov
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.pf
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.pts
  Value error, Invalid integer value: '111.8' [type=value_error, input_value='111.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_fg
  Value error, Invalid integer value: '36.8' [type=value_error, input_value='36.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_fga
  Value error, Invalid integer value: '80.8' [type=value_error, input_value='80.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_fg3
  Value error, Invalid integer value: '8.8' [type=value_error, input_value='8.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_fg3a
  Value error, Invalid integer value: '28.5' [type=value_error, input_value='28.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_ft
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_fta
  Value error, Invalid integer value: '29.8' [type=value_error, input_value='29.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_orb
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_trb
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_ast
  Value error, Invalid integer value: '24.3' [type=value_error, input_value='24.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_stl
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_tov
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_pf
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.opp_pts
  Value error, Invalid integer value: '104.3' [type=value_error, input_value='104.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.fg
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.fga
  Value error, Invalid integer value: '98.0' [type=value_error, input_value='98.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.ft
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.fta
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.orb
  Value error, Invalid integer value: '16.0' [type=value_error, input_value='16.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.ast
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.stl
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.tov
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.pf
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.pts
  Value error, Invalid integer value: '113.5' [type=value_error, input_value='113.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_fg
  Value error, Invalid integer value: '46.5' [type=value_error, input_value='46.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_fga
  Value error, Invalid integer value: '85.5' [type=value_error, input_value='85.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_fg3
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_fg3a
  Value error, Invalid integer value: '41.0' [type=value_error, input_value='41.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_ft
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_fta
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_orb
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_ast
  Value error, Invalid integer value: '35.5' [type=value_error, input_value='35.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_stl
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_blk
  Value error, Invalid integer value: '1.5' [type=value_error, input_value='1.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_tov
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_pf
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.opp_pts
  Value error, Invalid integer value: '127.5' [type=value_error, input_value='127.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.fg
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.fga
  Value error, Invalid integer value: '96.0' [type=value_error, input_value='96.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.fg3
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.fg3a
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.ft
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.fta
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.orb
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.trb
  Value error, Invalid integer value: '46.5' [type=value_error, input_value='46.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.ast
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.stl
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.blk
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.tov
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.pf
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.pts
  Value error, Invalid integer value: '116.5' [type=value_error, input_value='116.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_fg
  Value error, Invalid integer value: '38.5' [type=value_error, input_value='38.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_fga
  Value error, Invalid integer value: '82.0' [type=value_error, input_value='82.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_fg3
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_fg3a
  Value error, Invalid integer value: '28.0' [type=value_error, input_value='28.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_ft
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_fta
  Value error, Invalid integer value: '32.0' [type=value_error, input_value='32.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_orb
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_ast
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_blk
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_tov
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_pf
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.opp_pts
  Value error, Invalid integer value: '110.0' [type=value_error, input_value='110.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.fga
  Value error, Invalid integer value: '91.3' [type=value_error, input_value='91.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.fg3
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.fg3a
  Value error, Invalid integer value: '37.0' [type=value_error, input_value='37.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.ft
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.fta
  Value error, Invalid integer value: '30.3' [type=value_error, input_value='30.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.orb
  Value error, Invalid integer value: '13.7' [type=value_error, input_value='13.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.trb
  Value error, Invalid integer value: '39.7' [type=value_error, input_value='39.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.ast
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.stl
  Value error, Invalid integer value: '9.3' [type=value_error, input_value='9.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.blk
  Value error, Invalid integer value: '8.7' [type=value_error, input_value='8.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.tov
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.pf
  Value error, Invalid integer value: '22.3' [type=value_error, input_value='22.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.pts
  Value error, Invalid integer value: '110.7' [type=value_error, input_value='110.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_fg
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_fga
  Value error, Invalid integer value: '84.0' [type=value_error, input_value='84.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_fg3
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_fg3a
  Value error, Invalid integer value: '30.3' [type=value_error, input_value='30.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_ft
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_fta
  Value error, Invalid integer value: '24.7' [type=value_error, input_value='24.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_orb
  Value error, Invalid integer value: '11.3' [type=value_error, input_value='11.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_trb
  Value error, Invalid integer value: '46.7' [type=value_error, input_value='46.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_ast
  Value error, Invalid integer value: '28.0' [type=value_error, input_value='28.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_stl
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_blk
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_tov
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_pf
  Value error, Invalid integer value: '23.7' [type=value_error, input_value='23.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.opp_pts
  Value error, Invalid integer value: '119.3' [type=value_error, input_value='119.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.fga
  Value error, Invalid integer value: '90.0' [type=value_error, input_value='90.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.fg3
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.fg3a
  Value error, Invalid integer value: '27.5' [type=value_error, input_value='27.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.ft
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.fta
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.orb
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.trb
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.ast
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.stl
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.tov
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.pf
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.pts
  Value error, Invalid integer value: '106.5' [type=value_error, input_value='106.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_fg
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_fga
  Value error, Invalid integer value: '82.0' [type=value_error, input_value='82.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_fg3
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_fg3a
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_ft
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_fta
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_orb
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_trb
  Value error, Invalid integer value: '45.5' [type=value_error, input_value='45.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_ast
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_blk
  Value error, Invalid integer value: '3.5' [type=value_error, input_value='3.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_tov
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_pf
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.opp_pts
  Value error, Invalid integer value: '116.0' [type=value_error, input_value='116.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.fg
  Value error, Invalid integer value: '46.5' [type=value_error, input_value='46.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.fga
  Value error, Invalid integer value: '99.0' [type=value_error, input_value='99.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.fg3a
  Value error, Invalid integer value: '35.5' [type=value_error, input_value='35.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.ft
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.orb
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.trb
  Value error, Invalid integer value: '45.5' [type=value_error, input_value='45.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.stl
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.tov
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.pf
  Value error, Invalid integer value: '19.0' [type=value_error, input_value='19.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.pts
  Value error, Invalid integer value: '119.0' [type=value_error, input_value='119.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_fg
  Value error, Invalid integer value: '41.0' [type=value_error, input_value='41.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_fga
  Value error, Invalid integer value: '83.5' [type=value_error, input_value='83.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_fg3
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_fg3a
  Value error, Invalid integer value: '31.5' [type=value_error, input_value='31.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_ft
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_fta
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_orb
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_trb
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_ast
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_blk
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_tov
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_pf
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
46.opp_pts
  Value error, Invalid integer value: '117.5' [type=value_error, input_value='117.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.fg
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.fga
  Value error, Invalid integer value: '98.5' [type=value_error, input_value='98.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.fg3
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.fg3a
  Value error, Invalid integer value: '32.0' [type=value_error, input_value='32.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.ft
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.fta
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.orb
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.ast
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.stl
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.tov
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.pts
  Value error, Invalid integer value: '106.0' [type=value_error, input_value='106.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_fg
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_fga
  Value error, Invalid integer value: '86.5' [type=value_error, input_value='86.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_fg3a
  Value error, Invalid integer value: '28.0' [type=value_error, input_value='28.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_ft
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_orb
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_trb
  Value error, Invalid integer value: '48.5' [type=value_error, input_value='48.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_ast
  Value error, Invalid integer value: '31.0' [type=value_error, input_value='31.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_blk
  Value error, Invalid integer value: '6.5' [type=value_error, input_value='6.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_tov
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.opp_pts
  Value error, Invalid integer value: '111.0' [type=value_error, input_value='111.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.fga
  Value error, Invalid integer value: '88.0' [type=value_error, input_value='88.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.fg3
  Value error, Invalid integer value: '10.8' [type=value_error, input_value='10.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.fg3a
  Value error, Invalid integer value: '33.3' [type=value_error, input_value='33.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.ft
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.fta
  Value error, Invalid integer value: '19.8' [type=value_error, input_value='19.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.orb
  Value error, Invalid integer value: '12.3' [type=value_error, input_value='12.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.trb
  Value error, Invalid integer value: '44.5' [type=value_error, input_value='44.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.ast
  Value error, Invalid integer value: '25.3' [type=value_error, input_value='25.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.blk
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.tov
  Value error, Invalid integer value: '10.3' [type=value_error, input_value='10.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.pf
  Value error, Invalid integer value: '20.8' [type=value_error, input_value='20.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.pts
  Value error, Invalid integer value: '106.3' [type=value_error, input_value='106.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_fg
  Value error, Invalid integer value: '33.8' [type=value_error, input_value='33.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_fga
  Value error, Invalid integer value: '76.3' [type=value_error, input_value='76.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_fg3
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_ft
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_fta
  Value error, Invalid integer value: '23.8' [type=value_error, input_value='23.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_orb
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_trb
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_ast
  Value error, Invalid integer value: '21.0' [type=value_error, input_value='21.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_stl
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_tov
  Value error, Invalid integer value: '16.8' [type=value_error, input_value='16.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_pf
  Value error, Invalid integer value: '17.8' [type=value_error, input_value='17.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
48.opp_pts
  Value error, Invalid integer value: '99.5' [type=value_error, input_value='99.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.fg
  Value error, Invalid integer value: '44.0' [type=value_error, input_value='44.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.fga
  Value error, Invalid integer value: '102.8' [type=value_error, input_value='102.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.fg3
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.fg3a
  Value error, Invalid integer value: '37.0' [type=value_error, input_value='37.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.ft
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.fta
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.orb
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.trb
  Value error, Invalid integer value: '45.8' [type=value_error, input_value='45.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.ast
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.stl
  Value error, Invalid integer value: '7.8' [type=value_error, input_value='7.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.tov
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.pf
  Value error, Invalid integer value: '17.8' [type=value_error, input_value='17.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.pts
  Value error, Invalid integer value: '113.8' [type=value_error, input_value='113.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_fg
  Value error, Invalid integer value: '40.5' [type=value_error, input_value='40.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_fga
  Value error, Invalid integer value: '84.5' [type=value_error, input_value='84.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_fg3
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_fg3a
  Value error, Invalid integer value: '39.3' [type=value_error, input_value='39.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_ft
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_fta
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_orb
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_trb
  Value error, Invalid integer value: '49.5' [type=value_error, input_value='49.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_ast
  Value error, Invalid integer value: '28.3' [type=value_error, input_value='28.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_stl
  Value error, Invalid integer value: '4.3' [type=value_error, input_value='4.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_blk
  Value error, Invalid integer value: '4.8' [type=value_error, input_value='4.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_tov
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_pf
  Value error, Invalid integer value: '17.3' [type=value_error, input_value='17.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
49.opp_pts
  Value error, Invalid integer value: '114.3' [type=value_error, input_value='114.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.fg
  Value error, Invalid integer value: '47.0' [type=value_error, input_value='47.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.fga
  Value error, Invalid integer value: '88.5' [type=value_error, input_value='88.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.fg3a
  Value error, Invalid integer value: '27.5' [type=value_error, input_value='27.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.ft
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.fta
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.orb
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.trb
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.ast
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.stl
  Value error, Invalid integer value: '9.5' [type=value_error, input_value='9.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.blk
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.tov
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.pf
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.pts
  Value error, Invalid integer value: '124.0' [type=value_error, input_value='124.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_fg
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_fga
  Value error, Invalid integer value: '87.0' [type=value_error, input_value='87.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_fg3a
  Value error, Invalid integer value: '31.5' [type=value_error, input_value='31.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_ft
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_orb
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_trb
  Value error, Invalid integer value: '39.5' [type=value_error, input_value='39.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_ast
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_blk
  Value error, Invalid integer value: '3.5' [type=value_error, input_value='3.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_tov
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_pf
  Value error, Invalid integer value: '21.5' [type=value_error, input_value='21.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.opp_pts
  Value error, Invalid integer value: '117.5' [type=value_error, input_value='117.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.fg
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.fga
  Value error, Invalid integer value: '90.0' [type=value_error, input_value='90.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.fg3
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.fg3a
  Value error, Invalid integer value: '34.5' [type=value_error, input_value='34.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.ft
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.fta
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.orb
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.trb
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.ast
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.stl
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.blk
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.tov
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.pts
  Value error, Invalid integer value: '111.5' [type=value_error, input_value='111.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_fg
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_fga
  Value error, Invalid integer value: '85.0' [type=value_error, input_value='85.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_fg3
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_fg3a
  Value error, Invalid integer value: '31.5' [type=value_error, input_value='31.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_ft
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_fta
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_orb
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_trb
  Value error, Invalid integer value: '47.5' [type=value_error, input_value='47.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_ast
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_stl
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_blk
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_tov
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_pf
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
51.opp_pts
  Value error, Invalid integer value: '118.0' [type=value_error, input_value='118.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.fga
  Value error, Invalid integer value: '90.8' [type=value_error, input_value='90.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.fg3
  Value error, Invalid integer value: '11.8' [type=value_error, input_value='11.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.fg3a
  Value error, Invalid integer value: '35.3' [type=value_error, input_value='35.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.ft
  Value error, Invalid integer value: '27.5' [type=value_error, input_value='27.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.fta
  Value error, Invalid integer value: '33.3' [type=value_error, input_value='33.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.orb
  Value error, Invalid integer value: '14.8' [type=value_error, input_value='14.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.trb
  Value error, Invalid integer value: '42.8' [type=value_error, input_value='42.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.ast
  Value error, Invalid integer value: '21.8' [type=value_error, input_value='21.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.blk
  Value error, Invalid integer value: '5.8' [type=value_error, input_value='5.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.tov
  Value error, Invalid integer value: '6.5' [type=value_error, input_value='6.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.pf
  Value error, Invalid integer value: '21.0' [type=value_error, input_value='21.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.pts
  Value error, Invalid integer value: '117.3' [type=value_error, input_value='117.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_fg
  Value error, Invalid integer value: '40.8' [type=value_error, input_value='40.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_fga
  Value error, Invalid integer value: '85.0' [type=value_error, input_value='85.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_fg3
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_fg3a
  Value error, Invalid integer value: '33.8' [type=value_error, input_value='33.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_ft
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_fta
  Value error, Invalid integer value: '26.3' [type=value_error, input_value='26.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_orb
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_trb
  Value error, Invalid integer value: '47.5' [type=value_error, input_value='47.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_ast
  Value error, Invalid integer value: '22.8' [type=value_error, input_value='22.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_stl
  Value error, Invalid integer value: '3.0' [type=value_error, input_value='3.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_tov
  Value error, Invalid integer value: '14.8' [type=value_error, input_value='14.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_pf
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
52.opp_pts
  Value error, Invalid integer value: '113.8' [type=value_error, input_value='113.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.fg
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.fga
  Value error, Invalid integer value: '92.5' [type=value_error, input_value='92.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.fg3a
  Value error, Invalid integer value: '31.0' [type=value_error, input_value='31.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.ft
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.fta
  Value error, Invalid integer value: '32.0' [type=value_error, input_value='32.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.orb
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.trb
  Value error, Invalid integer value: '49.0' [type=value_error, input_value='49.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.ast
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.stl
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.tov
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.pts
  Value error, Invalid integer value: '120.5' [type=value_error, input_value='120.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_fg
  Value error, Invalid integer value: '46.0' [type=value_error, input_value='46.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_fga
  Value error, Invalid integer value: '93.5' [type=value_error, input_value='93.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_fg3
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_fg3a
  Value error, Invalid integer value: '33.5' [type=value_error, input_value='33.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_ft
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_orb
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_trb
  Value error, Invalid integer value: '41.5' [type=value_error, input_value='41.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_ast
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_stl
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_tov
  Value error, Invalid integer value: '16.0' [type=value_error, input_value='16.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_pf
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.opp_pts
  Value error, Invalid integer value: '121.5' [type=value_error, input_value='121.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.fg
  Value error, Invalid integer value: '40.8' [type=value_error, input_value='40.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.fga
  Value error, Invalid integer value: '81.8' [type=value_error, input_value='81.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.fg3
  Value error, Invalid integer value: '8.3' [type=value_error, input_value='8.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.fg3a
  Value error, Invalid integer value: '28.3' [type=value_error, input_value='28.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.ft
  Value error, Invalid integer value: '23.3' [type=value_error, input_value='23.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.fta
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.orb
  Value error, Invalid integer value: '9.8' [type=value_error, input_value='9.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.trb
  Value error, Invalid integer value: '36.0' [type=value_error, input_value='36.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.ast
  Value error, Invalid integer value: '25.8' [type=value_error, input_value='25.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.blk
  Value error, Invalid integer value: '6.8' [type=value_error, input_value='6.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.tov
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.pts
  Value error, Invalid integer value: '113.0' [type=value_error, input_value='113.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_fg
  Value error, Invalid integer value: '39.8' [type=value_error, input_value='39.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_fga
  Value error, Invalid integer value: '77.5' [type=value_error, input_value='77.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_fg3
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_fg3a
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_ft
  Value error, Invalid integer value: '19.8' [type=value_error, input_value='19.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_fta
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_orb
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_trb
  Value error, Invalid integer value: '35.8' [type=value_error, input_value='35.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_ast
  Value error, Invalid integer value: '24.5' [type=value_error, input_value='24.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_stl
  Value error, Invalid integer value: '5.3' [type=value_error, input_value='5.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_tov
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_pf
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
54.opp_pts
  Value error, Invalid integer value: '111.3' [type=value_error, input_value='111.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.fg
  Value error, Invalid integer value: '39.5' [type=value_error, input_value='39.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.fga
  Value error, Invalid integer value: '85.5' [type=value_error, input_value='85.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.fg3a
  Value error, Invalid integer value: '35.5' [type=value_error, input_value='35.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.ft
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.fta
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.orb
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.ast
  Value error, Invalid integer value: '25.5' [type=value_error, input_value='25.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.stl
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.blk
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.tov
  Value error, Invalid integer value: '13.8' [type=value_error, input_value='13.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.pf
  Value error, Invalid integer value: '18.8' [type=value_error, input_value='18.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.pts
  Value error, Invalid integer value: '105.0' [type=value_error, input_value='105.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_fga
  Value error, Invalid integer value: '78.5' [type=value_error, input_value='78.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_fg3
  Value error, Invalid integer value: '14.8' [type=value_error, input_value='14.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_fg3a
  Value error, Invalid integer value: '36.8' [type=value_error, input_value='36.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_ft
  Value error, Invalid integer value: '17.8' [type=value_error, input_value='17.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_fta
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_orb
  Value error, Invalid integer value: '6.0' [type=value_error, input_value='6.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_trb
  Value error, Invalid integer value: '38.3' [type=value_error, input_value='38.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_ast
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_stl
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_blk
  Value error, Invalid integer value: '3.8' [type=value_error, input_value='3.8', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_tov
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_pf
  Value error, Invalid integer value: '18.3' [type=value_error, input_value='18.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
55.opp_pts
  Value error, Invalid integer value: '110.5' [type=value_error, input_value='110.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.fga
  Value error, Invalid integer value: '85.0' [type=value_error, input_value='85.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.fg3
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.fg3a
  Value error, Invalid integer value: '33.0' [type=value_error, input_value='33.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.ft
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.fta
  Value error, Invalid integer value: '22.5' [type=value_error, input_value='22.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.orb
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.trb
  Value error, Invalid integer value: '37.5' [type=value_error, input_value='37.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.ast
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.stl
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.blk
  Value error, Invalid integer value: '3.5' [type=value_error, input_value='3.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.tov
  Value error, Invalid integer value: '13.0' [type=value_error, input_value='13.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.pf
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.pts
  Value error, Invalid integer value: '109.5' [type=value_error, input_value='109.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_fg
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_fga
  Value error, Invalid integer value: '79.0' [type=value_error, input_value='79.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_fg3
  Value error, Invalid integer value: '12.5' [type=value_error, input_value='12.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_fg3a
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_ft
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_fta
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_orb
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_stl
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_blk
  Value error, Invalid integer value: '2.5' [type=value_error, input_value='2.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_tov
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_pf
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.opp_pts
  Value error, Invalid integer value: '109.0' [type=value_error, input_value='109.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.fg
  Value error, Invalid integer value: '44.0' [type=value_error, input_value='44.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.fga
  Value error, Invalid integer value: '91.5' [type=value_error, input_value='91.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.fg3a
  Value error, Invalid integer value: '30.5' [type=value_error, input_value='30.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.ft
  Value error, Invalid integer value: '21.0' [type=value_error, input_value='21.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.fta
  Value error, Invalid integer value: '23.5' [type=value_error, input_value='23.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.orb
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.trb
  Value error, Invalid integer value: '43.0' [type=value_error, input_value='43.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.ast
  Value error, Invalid integer value: '25.0' [type=value_error, input_value='25.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.stl
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.blk
  Value error, Invalid integer value: '5.5' [type=value_error, input_value='5.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.tov
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.pf
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.pts
  Value error, Invalid integer value: '120.0' [type=value_error, input_value='120.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_fg
  Value error, Invalid integer value: '37.0' [type=value_error, input_value='37.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_fga
  Value error, Invalid integer value: '76.0' [type=value_error, input_value='76.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_fg3
  Value error, Invalid integer value: '8.0' [type=value_error, input_value='8.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_fg3a
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_ft
  Value error, Invalid integer value: '23.0' [type=value_error, input_value='23.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_fta
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_orb
  Value error, Invalid integer value: '6.5' [type=value_error, input_value='6.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_trb
  Value error, Invalid integer value: '34.5' [type=value_error, input_value='34.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_ast
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_stl
  Value error, Invalid integer value: '4.0' [type=value_error, input_value='4.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_tov
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_pf
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
57.opp_pts
  Value error, Invalid integer value: '105.0' [type=value_error, input_value='105.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.fg
  Value error, Invalid integer value: '47.5' [type=value_error, input_value='47.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.fga
  Value error, Invalid integer value: '95.5' [type=value_error, input_value='95.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.fg3
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.fg3a
  Value error, Invalid integer value: '30.5' [type=value_error, input_value='30.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.ft
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.fta
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.orb
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.trb
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.ast
  Value error, Invalid integer value: '26.5' [type=value_error, input_value='26.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.stl
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.blk
  Value error, Invalid integer value: '7.5' [type=value_error, input_value='7.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.tov
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.pf
  Value error, Invalid integer value: '17.5' [type=value_error, input_value='17.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.pts
  Value error, Invalid integer value: '118.0' [type=value_error, input_value='118.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_fg
  Value error, Invalid integer value: '40.0' [type=value_error, input_value='40.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_fga
  Value error, Invalid integer value: '83.0' [type=value_error, input_value='83.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_fg3
  Value error, Invalid integer value: '15.0' [type=value_error, input_value='15.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_fg3a
  Value error, Invalid integer value: '39.0' [type=value_error, input_value='39.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_ft
  Value error, Invalid integer value: '14.5' [type=value_error, input_value='14.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_fta
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_orb
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_trb
  Value error, Invalid integer value: '42.0' [type=value_error, input_value='42.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_ast
  Value error, Invalid integer value: '29.0' [type=value_error, input_value='29.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_stl
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_blk
  Value error, Invalid integer value: '2.5' [type=value_error, input_value='2.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_tov
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_pf
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
58.opp_pts
  Value error, Invalid integer value: '109.5' [type=value_error, input_value='109.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.fg
  Value error, Invalid integer value: '50.0' [type=value_error, input_value='50.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.fga
  Value error, Invalid integer value: '97.0' [type=value_error, input_value='97.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.fg3
  Value error, Invalid integer value: '12.0' [type=value_error, input_value='12.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.fg3a
  Value error, Invalid integer value: '30.5' [type=value_error, input_value='30.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.ft
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.fta
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.orb
  Value error, Invalid integer value: '9.0' [type=value_error, input_value='9.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.trb
  Value error, Invalid integer value: '50.5' [type=value_error, input_value='50.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.ast
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.stl
  Value error, Invalid integer value: '13.5' [type=value_error, input_value='13.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.blk
  Value error, Invalid integer value: '6.5' [type=value_error, input_value='6.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.tov
  Value error, Invalid integer value: '14.0' [type=value_error, input_value='14.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.pf
  Value error, Invalid integer value: '18.0' [type=value_error, input_value='18.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.pts
  Value error, Invalid integer value: '127.5' [type=value_error, input_value='127.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_fg
  Value error, Invalid integer value: '36.0' [type=value_error, input_value='36.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_fga
  Value error, Invalid integer value: '90.5' [type=value_error, input_value='90.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_fg3a
  Value error, Invalid integer value: '37.5' [type=value_error, input_value='37.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_ft
  Value error, Invalid integer value: '15.5' [type=value_error, input_value='15.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_fta
  Value error, Invalid integer value: '20.5' [type=value_error, input_value='20.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_orb
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_trb
  Value error, Invalid integer value: '42.5' [type=value_error, input_value='42.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_ast
  Value error, Invalid integer value: '26.5' [type=value_error, input_value='26.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_stl
  Value error, Invalid integer value: '7.0' [type=value_error, input_value='7.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_blk
  Value error, Invalid integer value: '5.0' [type=value_error, input_value='5.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_tov
  Value error, Invalid integer value: '19.5' [type=value_error, input_value='19.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_pf
  Value error, Invalid integer value: '19.0' [type=value_error, input_value='19.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.opp_pts
  Value error, Invalid integer value: '99.0' [type=value_error, input_value='99.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.fg
  Value error, Invalid integer value: '45.5' [type=value_error, input_value='45.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.fga
  Value error, Invalid integer value: '100.5' [type=value_error, input_value='100.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.fg3
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.fg3a
  Value error, Invalid integer value: '28.5' [type=value_error, input_value='28.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.ft
  Value error, Invalid integer value: '20.0' [type=value_error, input_value='20.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.fta
  Value error, Invalid integer value: '28.0' [type=value_error, input_value='28.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.orb
  Value error, Invalid integer value: '17.0' [type=value_error, input_value='17.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.trb
  Value error, Invalid integer value: '46.0' [type=value_error, input_value='46.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.ast
  Value error, Invalid integer value: '27.5' [type=value_error, input_value='27.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.stl
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.blk
  Value error, Invalid integer value: '2.5' [type=value_error, input_value='2.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.tov
  Value error, Invalid integer value: '10.5' [type=value_error, input_value='10.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.pf
  Value error, Invalid integer value: '26.0' [type=value_error, input_value='26.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.pts
  Value error, Invalid integer value: '122.0' [type=value_error, input_value='122.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_fg
  Value error, Invalid integer value: '45.5' [type=value_error, input_value='45.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_fga
  Value error, Invalid integer value: '85.0' [type=value_error, input_value='85.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_fg3
  Value error, Invalid integer value: '11.5' [type=value_error, input_value='11.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_fg3a
  Value error, Invalid integer value: '35.5' [type=value_error, input_value='35.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_ft
  Value error, Invalid integer value: '24.0' [type=value_error, input_value='24.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_fta
  Value error, Invalid integer value: '29.5' [type=value_error, input_value='29.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_orb
  Value error, Invalid integer value: '11.0' [type=value_error, input_value='11.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_trb
  Value error, Invalid integer value: '47.5' [type=value_error, input_value='47.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_ast
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_stl
  Value error, Invalid integer value: '4.5' [type=value_error, input_value='4.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_blk
  Value error, Invalid integer value: '8.5' [type=value_error, input_value='8.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_tov
  Value error, Invalid integer value: '16.5' [type=value_error, input_value='16.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_pf
  Value error, Invalid integer value: '18.5' [type=value_error, input_value='18.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
60.opp_pts
  Value error, Invalid integer value: '126.5' [type=value_error, input_value='126.5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.fg
  Value error, Invalid integer value: '44.3' [type=value_error, input_value='44.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.fga
  Value error, Invalid integer value: '93.3' [type=value_error, input_value='93.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.fg3
  Value error, Invalid integer value: '10.7' [type=value_error, input_value='10.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.fg3a
  Value error, Invalid integer value: '31.3' [type=value_error, input_value='31.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.ft
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.fta
  Value error, Invalid integer value: '15.7' [type=value_error, input_value='15.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.orb
  Value error, Invalid integer value: '13.7' [type=value_error, input_value='13.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.trb
  Value error, Invalid integer value: '43.3' [type=value_error, input_value='43.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.ast
  Value error, Invalid integer value: '26.7' [type=value_error, input_value='26.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.stl
  Value error, Invalid integer value: '11.7' [type=value_error, input_value='11.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.blk
  Value error, Invalid integer value: '5.7' [type=value_error, input_value='5.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.tov
  Value error, Invalid integer value: '13.7' [type=value_error, input_value='13.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.pf
  Value error, Invalid integer value: '20.3' [type=value_error, input_value='20.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.pts
  Value error, Invalid integer value: '112.7' [type=value_error, input_value='112.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_fg
  Value error, Invalid integer value: '39.7' [type=value_error, input_value='39.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_fga
  Value error, Invalid integer value: '81.7' [type=value_error, input_value='81.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_fg3
  Value error, Invalid integer value: '14.7' [type=value_error, input_value='14.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_fg3a
  Value error, Invalid integer value: '30.0' [type=value_error, input_value='30.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_ft
  Value error, Invalid integer value: '16.7' [type=value_error, input_value='16.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_fta
  Value error, Invalid integer value: '22.0' [type=value_error, input_value='22.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_orb
  Value error, Invalid integer value: '10.0' [type=value_error, input_value='10.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_trb
  Value error, Invalid integer value: '43.7' [type=value_error, input_value='43.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_ast
  Value error, Invalid integer value: '27.0' [type=value_error, input_value='27.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_stl
  Value error, Invalid integer value: '6.7' [type=value_error, input_value='6.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_blk
  Value error, Invalid integer value: '3.7' [type=value_error, input_value='3.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_tov
  Value error, Invalid integer value: '19.0' [type=value_error, input_value='19.0', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_pf
  Value error, Invalid integer value: '13.3' [type=value_error, input_value='13.3', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
61.opp_pts
  Value error, Invalid integer value: '110.7' [type=value_error, input_value='110.7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 210, in team_splits
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'team_splits' (https://www.basketball-reference.com/teams/TOR/2023/splits/): missing field/alias: unknown
```

### team_contracts

- **Params**: `{"team_abbreviation": "NOP"}`
- **URL**: `https://www.basketball-reference.com/contracts/NOP.html`
- **Status**: ok
- **Duration**: 6.092s
- **Row count**: 20
- **Columns**: `[]`

**Sample**:
```json
["player='Zion Williamson' age_today='25' y1='$39,446,090' y2='$42,166,510' y3='$44,886,930' y4=None y5=None y6=None remain_gtd='$126,499,530'", "player='Jordan Poole' age_today='26' y1='$31,848,215' y2='$34,044,642' y3=None y4=None y5=None y6=None remain_gtd='$65,892,857'"]
```

### team_lineups

- **Params**: `{"team_abbreviation": "PHI", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/teams/PHI/2024/lineups/`
- **Status**: error
- **Duration**: 7.261s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 20
- **Message**: Schema drift detected for endpoint 'team_lineups' (https://www.basketball-reference.com/teams/PHI/2024/lineups/): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 20 validation errors for list[TeamLineupsRow]
0.mp
  Value error, Invalid float value: '219:15' [type=value_error, input_value='219:15', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.mp
  Value error, Invalid float value: '135:45' [type=value_error, input_value='135:45', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.mp
  Value error, Invalid float value: '109:01' [type=value_error, input_value='109:01', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.mp
  Value error, Invalid float value: '98:58' [type=value_error, input_value='98:58', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.mp
  Value error, Invalid float value: '74:39' [type=value_error, input_value='74:39', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.mp
  Value error, Invalid float value: '67:57' [type=value_error, input_value='67:57', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.mp
  Value error, Invalid float value: '51:28' [type=value_error, input_value='51:28', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.mp
  Value error, Invalid float value: '49:25' [type=value_error, input_value='49:25', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.mp
  Value error, Invalid float value: '44:56' [type=value_error, input_value='44:56', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.mp
  Value error, Invalid float value: '43:11' [type=value_error, input_value='43:11', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.mp
  Value error, Invalid float value: '39:41' [type=value_error, input_value='39:41', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.mp
  Value error, Invalid float value: '39:15' [type=value_error, input_value='39:15', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.mp
  Value error, Invalid float value: '39:12' [type=value_error, input_value='39:12', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.mp
  Value error, Invalid float value: '37:24' [type=value_error, input_value='37:24', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.mp
  Value error, Invalid float value: '30:00' [type=value_error, input_value='30:00', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.mp
  Value error, Invalid float value: '29:36' [type=value_error, input_value='29:36', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.mp
  Value error, Invalid float value: '27:30' [type=value_error, input_value='27:30', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.mp
  Value error, Invalid float value: '26:37' [type=value_error, input_value='26:37', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.mp
  Value error, Invalid float value: '26:28' [type=value_error, input_value='26:28', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.mp
  Value error, Invalid float value: '25:56' [type=value_error, input_value='25:56', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 261, in team_lineups
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'team_lineups' (https://www.basketball-reference.com/teams/PHI/2024/lineups/): missing field/alias: unknown
```

### team_starting_lineups

- **Params**: `{"team_abbreviation": "NOP", "season_end_year": 2019}`
- **URL**: `https://www.basketball-reference.com/teams/NOP/2019_start.html`
- **Status**: ok
- **Duration**: 6.800s
- **Row count**: 82
- **Columns**: `[]`

**Sample**:
```json
["g=1 date_game='2018-10-17' game_start_time=None network=None box_score_text='Box Score' game_location='@' opp_name='Houston Rockets' game_result='W' overtimes=None pts=131 opp_pts=112 wins=1 losses=0 game_starters='A. Davis · J. Holiday · N. Mirotić · E. Moore · E. Payton'", "g=2 date_game='2018-10-19' game_start_time=None network=None box_score_text='Box Score' game_location=None opp_name='Sacramento Kings' game_result='W' overtimes=None pts=149 opp_pts=129 wins=2 losses=0 game_starters='A. D
```

### team_on_off

- **Params**: `{"team_abbreviation": "NOP", "season_end_year": 2024}`
- **URL**: `https://www.basketball-reference.com/teams/NOP/2024/on-off/`
- **Status**: error
- **Duration**: 6.721s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 20
- **Message**: Schema drift detected for endpoint 'team_on_off' (https://www.basketball-reference.com/teams/NOP/2024/on-off/): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 20 validation errors for list[TeamOnOffRow]
2.mp
  Value error, Invalid integer value: '59%' [type=value_error, input_value='59%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.mp
  Value error, Invalid integer value: '56%' [type=value_error, input_value='56%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.mp
  Value error, Invalid integer value: '55%' [type=value_error, input_value='55%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.mp
  Value error, Invalid integer value: '53%' [type=value_error, input_value='53%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.mp
  Value error, Invalid integer value: '49%' [type=value_error, input_value='49%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.mp
  Value error, Invalid integer value: '43%' [type=value_error, input_value='43%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.mp
  Value error, Invalid integer value: '34%' [type=value_error, input_value='34%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.mp
  Value error, Invalid integer value: '32%' [type=value_error, input_value='32%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.mp
  Value error, Invalid integer value: '31%' [type=value_error, input_value='31%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.mp
  Value error, Invalid integer value: '29%' [type=value_error, input_value='29%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.mp
  Value error, Invalid integer value: '26%' [type=value_error, input_value='26%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.mp
  Value error, Invalid integer value: '10%' [type=value_error, input_value='10%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.mp
  Value error, Invalid integer value: '8%' [type=value_error, input_value='8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.mp
  Value error, Invalid integer value: '8%' [type=value_error, input_value='8%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.mp
  Value error, Invalid integer value: '4%' [type=value_error, input_value='4%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
47.mp
  Value error, Invalid integer value: '1%' [type=value_error, input_value='1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
50.mp
  Value error, Invalid integer value: '1%' [type=value_error, input_value='1%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
53.mp
  Value error, Invalid integer value: '0%' [type=value_error, input_value='0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
56.mp
  Value error, Invalid integer value: '0%' [type=value_error, input_value='0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
59.mp
  Value error, Invalid integer value: '0%' [type=value_error, input_value='0%', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 313, in team_on_off
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'team_on_off' (https://www.basketball-reference.com/teams/NOP/2024/on-off/): missing field/alias: unknown
```

### franchise_history

- **Params**: `{"team_abbreviation": "DAL"}`
- **URL**: `https://www.basketball-reference.com/teams/DAL/`
- **Status**: error
- **Duration**: 6.330s
- **Error type**: `courtside_data.errors.SchemaDriftError`
- **Error category**: `schema_drift`
- **Pydantic errors**: 71
- **Message**: Schema drift detected for endpoint 'franchise_history' (https://www.basketball-reference.com/teams/DAL/): missing field/alias: unknown

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 208, in _execute
    values = adapter.validate_python(raw_rows)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pydantic\type_adapter.py", line 441, in validate_python
    return self.validator.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 71 validation errors for list[FranchiseHistoryRow]
0.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
1.rank_team
  Value error, Invalid integer value: '3rd of 5' [type=value_error, input_value='3rd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.rank_team
  Value error, Invalid integer value: '1st of 5' [type=value_error, input_value='1st of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
2.rank_team_playoffs
  Value error, Invalid integer value: 'Lost Finals' [type=value_error, input_value='Lost Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
3.rank_team
  Value error, Invalid integer value: '3rd of 5' [type=value_error, input_value='3rd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
4.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Finals' [type=value_error, input_value='Lost W. Conf. Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.rank_team
  Value error, Invalid integer value: '1st of 5' [type=value_error, input_value='1st of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
5.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
6.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
7.rank_team
  Value error, Invalid integer value: '5th of 5' [type=value_error, input_value='5th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
8.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
9.rank_team
  Value error, Invalid integer value: '5th of 5' [type=value_error, input_value='5th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
10.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
11.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
12.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
13.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.rank_team
  Value error, Invalid integer value: '3rd of 5' [type=value_error, input_value='3rd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
14.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
15.rank_team_playoffs
  Value error, Invalid integer value: 'Won Finals' [type=value_error, input_value='Won Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.rank_team
  Value error, Invalid integer value: '1st of 5' [type=value_error, input_value='1st of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
16.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.rank_team
  Value error, Invalid integer value: '3rd of 5' [type=value_error, input_value='3rd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
17.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.rank_team
  Value error, Invalid integer value: '4th of 5' [type=value_error, input_value='4th of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
18.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.rank_team
  Value error, Invalid integer value: '1st of 5' [type=value_error, input_value='1st of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
19.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
20.rank_team_playoffs
  Value error, Invalid integer value: 'Lost Finals' [type=value_error, input_value='Lost Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.rank_team
  Value error, Invalid integer value: '2nd of 5' [type=value_error, input_value='2nd of 5', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
21.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.rank_team
  Value error, Invalid integer value: '3rd of 7' [type=value_error, input_value='3rd of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
22.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.rank_team
  Value error, Invalid integer value: '2nd of 7' [type=value_error, input_value='2nd of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
23.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Finals' [type=value_error, input_value='Lost W. Conf. Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.rank_team
  Value error, Invalid integer value: '2nd of 7' [type=value_error, input_value='2nd of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
24.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.rank_team
  Value error, Invalid integer value: '3rd of 7' [type=value_error, input_value='3rd of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
25.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
26.rank_team
  Value error, Invalid integer value: '4th of 7' [type=value_error, input_value='4th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
27.rank_team
  Value error, Invalid integer value: '5th of 7' [type=value_error, input_value='5th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
28.rank_team
  Value error, Invalid integer value: '5th of 7' [type=value_error, input_value='5th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
29.rank_team
  Value error, Invalid integer value: '4th of 7' [type=value_error, input_value='4th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
30.rank_team
  Value error, Invalid integer value: '6th of 7' [type=value_error, input_value='6th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
31.rank_team
  Value error, Invalid integer value: '5th of 6' [type=value_error, input_value='5th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
32.rank_team
  Value error, Invalid integer value: '6th of 6' [type=value_error, input_value='6th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
33.rank_team
  Value error, Invalid integer value: '6th of 6' [type=value_error, input_value='6th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
34.rank_team
  Value error, Invalid integer value: '5th of 6' [type=value_error, input_value='5th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
35.rank_team
  Value error, Invalid integer value: '6th of 7' [type=value_error, input_value='6th of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.rank_team
  Value error, Invalid integer value: '3rd of 7' [type=value_error, input_value='3rd of 7', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
36.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
37.rank_team
  Value error, Invalid integer value: '4th of 6' [type=value_error, input_value='4th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.rank_team
  Value error, Invalid integer value: '2nd of 6' [type=value_error, input_value='2nd of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
38.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Finals' [type=value_error, input_value='Lost W. Conf. Finals', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.rank_team
  Value error, Invalid integer value: '1st of 6' [type=value_error, input_value='1st of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
39.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.rank_team
  Value error, Invalid integer value: '3rd of 6' [type=value_error, input_value='3rd of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
40.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.rank_team
  Value error, Invalid integer value: '3rd of 6' [type=value_error, input_value='3rd of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
41.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. 1st Rnd.' [type=value_error, input_value='Lost W. Conf. 1st Rnd.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.rank_team
  Value error, Invalid integer value: '2nd of 6' [type=value_error, input_value='2nd of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
42.rank_team_playoffs
  Value error, Invalid integer value: 'Lost W. Conf. Semis' [type=value_error, input_value='Lost W. Conf. Semis', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
43.rank_team
  Value error, Invalid integer value: '4th of 6' [type=value_error, input_value='4th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
44.rank_team
  Value error, Invalid integer value: '5th of 6' [type=value_error, input_value='5th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
45.rank_team
  Value error, Invalid integer value: '6th of 6' [type=value_error, input_value='6th of 6', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\teams.py", line 338, in franchise_history
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 226, in _execute
    raise SchemaDriftError(
courtside_data.errors.SchemaDriftError: Schema drift detected for endpoint 'franchise_history' (https://www.basketball-reference.com/teams/DAL/): missing field/alias: unknown
```

### player_box_scores

- **Params**: `{"day": 25, "month": 12, "year": 2024}`
- **URL**: `https://www.basketball-reference.com/friv/dailyleaders.cgi?month=12&day=25&year=2024`
- **Status**: ok
- **Duration**: 7.473s
- **Row count**: 92
- **Columns**: `[]`

**Sample**:
```json
["field_goal_percentage=0.68 three_point_field_goal_percentage=0.667 free_throw_percentage=1.0 seconds_played=2595 made_field_goals=17 attempted_field_goals=25 made_three_point_field_goals=6 attempted_three_point_field_goals=9 made_free_throws=1 attempted_free_throws=1 offensive_rebounds=1 defensive_rebounds=0 assists=4 steals=2 blocks=2 turnovers=0 personal_fouls=2 points=41 game_score=36.4 slug='bridgmi01' name='Mikal Bridges' team=<Team.NEW_YORK_KNICKS: 'NEW YORK KNICKS'> location=<Location.H
```

### team_box_scores

- **Params**: `{"day": 25, "month": 12, "year": 2024}`
- **URL**: `https://www.basketball-reference.com/boxscores/?month=12&day=25&year=2024`
- **Status**: ok
- **Duration**: 40.465s
- **Row count**: 10
- **Columns**: `[]`

**Sample**:
```json
["field_goal_percentage=0.466 three_point_field_goal_percentage=0.425 free_throw_percentage=1.0 minutes_played=240 made_field_goals=41 attempted_field_goals=88 made_three_point_field_goals=17 attempted_three_point_field_goals=40 made_free_throws=19 attempted_free_throws=19 offensive_rebounds=5 defensive_rebounds=34 assists=28 steals=10 blocks=5 turnovers=6 personal_fouls=17 points=118 team=<Team.PHILADELPHIA_76ERS: 'PHILADELPHIA 76ERS'> outcome=<Outcome.WIN: 'WIN'>", "field_goal_percentage=0.453
```

### play_by_play

- **Params**: `{"home_team": "LOS_ANGELES_LAKERS", "day": 25, "month": 12, "year": 2024}`
- **URL**: `https://www.basketball-reference.com/boxscores/pbp/`
- **Status**: error
- **Duration**: 6.736s
- **Error type**: `courtside_data.errors.InvalidDate`
- **Error category**: `domain`
- **Message**: Date with year set to 2024, month set to 12, and day set to 25 is invalid

```
Traceback (most recent call last):
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\scripts\smoke_test_endpoints.py", line 317, in main
    result = func(**params)
             ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\games.py", line 82, in play_by_play
    return _run_endpoint(
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 420, in _run_endpoint
    return _execute(
           ^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 165, in _execute
    values = _call_with_error_mapping(service_call, error_mappings)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 72, in _call_with_error_mapping
    return service_call()
           ^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\client\_runner.py", line 414, in service_call
    return getattr(service, name)(**params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\nicolas\Documents\GitHub\courtside-data\courtside_data\http_service.py", line 843, in play_by_play
    raise InvalidDate(day=day, month=month, year=year)
courtside_data.errors.InvalidDate: Date with year set to 2024, month set to 12, and day set to 25 is invalid
```

### regular_season_player_box_scores

- **Params**: `{"player_identifier": "westbru01", "season_end_year": 2023, "include_inactive_games": false}`
- **URL**: `https://www.basketball-reference.com/players/w/westbru01/gamelog/2023`
- **Status**: ok
- **Duration**: 7.002s
- **Row count**: 73
- **Columns**: `[]`

**Sample**:
```json
["field_goal_percentage=0.583 three_point_field_goal_percentage=0.333 free_throw_percentage=0.8 seconds_played=1841 made_field_goals=7 attempted_field_goals=12 made_three_point_field_goals=1 attempted_three_point_field_goals=3 made_free_throws=4 attempted_free_throws=5 offensive_rebounds=1 defensive_rebounds=10 assists=3 steals=1 blocks=0 turnovers=4 personal_fouls=1 points=19 game_score=15.4 active=True date=datetime.date(2022, 10, 18) points_scored=19 team=<Team.LOS_ANGELES_LAKERS: 'LOS ANGELE
```

### playoff_player_box_scores

- **Params**: `{"player_identifier": "tatumja01", "season_end_year": 2024, "include_inactive_games": false}`
- **URL**: `https://www.basketball-reference.com/players/t/tatumja01/gamelog/2024`
- **Status**: ok
- **Duration**: 7.403s
- **Row count**: 19
- **Columns**: `[]`

**Sample**:
```json
["field_goal_percentage=0.389 three_point_field_goal_percentage=0.125 free_throw_percentage=1.0 seconds_played=2468 made_field_goals=7 attempted_field_goals=18 made_three_point_field_goals=1 attempted_three_point_field_goals=8 made_free_throws=8 attempted_free_throws=8 offensive_rebounds=1 defensive_rebounds=9 assists=10 steals=2 blocks=0 turnovers=3 personal_fouls=4 points=23 game_score=21.0 active=True date=datetime.date(2024, 4, 21) points_scored=23 team=<Team.BOSTON_CELTICS: 'BOSTON CELTICS'
```

### season_schedule

- **Params**: `{"season_end_year": 2018}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2018_games.html`
- **Status**: ok
- **Duration**: 59.383s
- **Row count**: 1312
- **Columns**: `[]`

**Sample**:
```json
["start_time=datetime.datetime(2017, 10, 18, 0, 1, tzinfo=datetime.timezone.utc) away_team=<Team.BOSTON_CELTICS: 'BOSTON CELTICS'> away_team_score=99 home_team=<Team.CLEVELAND_CAVALIERS: 'CLEVELAND CAVALIERS'> home_team_score=102", "start_time=datetime.datetime(2017, 10, 18, 2, 30, tzinfo=datetime.timezone.utc) away_team=<Team.HOUSTON_ROCKETS: 'HOUSTON ROCKETS'> away_team_score=122 home_team=<Team.GOLDEN_STATE_WARRIORS: 'GOLDEN STATE WARRIORS'> home_team_score=121"]
```

### players_season_totals

- **Params**: `{"season_end_year": 2022}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2022_totals.html`
- **Status**: ok
- **Duration**: 7.601s
- **Row count**: 715
- **Columns**: `[]`

**Sample**:
```json
["slug='youngtr01' name='Trae Young' positions=[<Position.POINT_GUARD: 'POINT GUARD'>] age=23 team=<Team.ATLANTA_HAWKS: 'ATLANTA HAWKS'> games_played=76 games_started=76 minutes_played=2652 made_field_goals=711 attempted_field_goals=1544 made_three_point_field_goals=233 attempted_three_point_field_goals=610 made_free_throws=500 attempted_free_throws=553 offensive_rebounds=50 defensive_rebounds=234 assists=737 steals=72 blocks=7 turnovers=303 personal_fouls=128 points=2155", "slug='derozde01' nam
```

### players_advanced_season_totals

- **Params**: `{"season_end_year": 2021, "include_combined_values": false}`
- **URL**: `https://www.basketball-reference.com/leagues/NBA_2021_advanced.html`
- **Status**: ok
- **Duration**: 6.269s
- **Row count**: 626
- **Columns**: `[]`

**Sample**:
```json
["slug='randlju01' name='Julius Randle' positions=[<Position.POWER_FORWARD: 'POWER FORWARD'>] age=26 team=<Team.NEW_YORK_KNICKS: 'NEW YORK KNICKS'> games_played=71 minutes_played=2667 player_efficiency_rating=19.7 true_shooting_percentage=0.567 three_point_attempt_rate=0.294 free_throw_attempt_rate=0.325 offensive_rebound_percentage=3.5 defensive_rebound_percentage=25.7 total_rebound_percentage=14.7 assist_percentage=27.2 steal_percentage=1.2 block_percentage=0.6 turnover_percentage=13.8 usage_p
```

### search

- **Params**: `{"term": "Wilt"}`
- **URL**: `https://www.basketball-reference.com/search/search.fcgi?search=Wilt`
- **Status**: ok
- **Duration**: 6.225s
- **Row count**: 5
- **Columns**: `[]`

**Sample**:
```json
["name='Wilt Chamberlain' identifier='chambwi01' leagues=set()", "name='Anthony Davis' identifier='davisan02' leagues=set()"]
```
