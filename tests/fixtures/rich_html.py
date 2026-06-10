"""
Rich HTML fixtures for Basketball Reference integration tests.

Each fixture includes realistic data-stat attributes matching the
GenericTable parser expectations, with known player values for spot checks.
"""

# ---------------------------------------------------------------------------
# League per-game stats (table id = per_game_stats)
# ---------------------------------------------------------------------------
RICH_PER_GAME_TABLE = """
<table id="per_game_stats">
    <thead>
        <tr><th>Rk</th><th>Player</th><th>Pos</th><th>Age</th><th>Team</th>
            <th>G</th><th>GS</th><th>MP</th><th>FG</th><th>FGA</th>
            <th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th><th>2P</th>
            <th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th>
            <th>FT%</th><th>ORB</th><th>DRB</th><th>TRB</th>
            <th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp_per_g">35.3</td>
            <td data-stat="fg_per_g">9.8</td>
            <td data-stat="fga_per_g">19.6</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3_per_g">2.1</td>
            <td data-stat="fg3a_per_g">5.1</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="fg2_per_g">7.7</td>
            <td data-stat="fg2a_per_g">14.5</td>
            <td data-stat="fg2_pct">.531</td>
            <td data-stat="efg_pct">.550</td>
            <td data-stat="ft_per_g">3.4</td>
            <td data-stat="fta_per_g">4.5</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb_per_g">0.8</td>
            <td data-stat="drb_per_g">5.5</td>
            <td data-stat="trb_per_g">6.3</td>
            <td data-stat="ast_per_g">8.3</td>
            <td data-stat="stl_per_g">1.3</td>
            <td data-stat="blk_per_g">0.5</td>
            <td data-stat="tov_per_g">2.9</td>
            <td data-stat="pf_per_g">1.1</td>
            <td data-stat="pts_per_g">25.1</td>
        </tr>
        <tr>
            <td data-stat="name_display">Giannis Antetokounmpo</td>
            <td data-stat="pos">PF</td>
            <td data-stat="age">29</td>
            <td data-stat="team_name_abbr">MIL</td>
            <td data-stat="games">73</td>
            <td data-stat="games_started">73</td>
            <td data-stat="mp_per_g">35.0</td>
            <td data-stat="fg_per_g">11.3</td>
            <td data-stat="fga_per_g">18.8</td>
            <td data-stat="fg_pct">.611</td>
            <td data-stat="fg3_per_g">0.5</td>
            <td data-stat="fg3a_per_g">1.3</td>
            <td data-stat="fg3_pct">.274</td>
            <td data-stat="fg2_per_g">10.8</td>
            <td data-stat="fg2a_per_g">17.5</td>
            <td data-stat="fg2_pct">.617</td>
            <td data-stat="efg_pct">.620</td>
            <td data-stat="ft_per_g">7.2</td>
            <td data-stat="fta_per_g">10.1</td>
            <td data-stat="ft_pct">.657</td>
            <td data-stat="orb_per_g">2.4</td>
            <td data-stat="drb_per_g">8.9</td>
            <td data-stat="trb_per_g">11.3</td>
            <td data-stat="ast_per_g">6.2</td>
            <td data-stat="stl_per_g">1.1</td>
            <td data-stat="blk_per_g">1.4</td>
            <td data-stat="tov_per_g">3.4</td>
            <td data-stat="pf_per_g">2.6</td>
            <td data-stat="pts_per_g">30.4</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Per-minute stats (table id = per_minute_stats)
# ---------------------------------------------------------------------------
RICH_PER_MINUTE_TABLE = """
<table id="per_minute_stats">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG/36</th><th>FGA/36</th><th>FG%</th><th>3P/36</th><th>3PA/36</th><th>3P%</th>
            <th>2P/36</th><th>2PA/36</th><th>2P%</th><th>FT/36</th><th>FTA/36</th><th>FT%</th>
            <th>ORB/36</th><th>DRB/36</th><th>TRB/36</th><th>AST/36</th><th>STL/36</th><th>BLK/36</th>
            <th>TOV/36</th><th>PF/36</th><th>PTS/36</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg_per_36_min">10.0</td>
            <td data-stat="fga_per_36_min">20.0</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3_per_36_min">2.1</td>
            <td data-stat="fg3a_per_36_min">5.2</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="fg2_per_36_min">7.9</td>
            <td data-stat="fg2a_per_36_min">14.8</td>
            <td data-stat="fg2_pct">.531</td>
            <td data-stat="ft_per_36_min">3.5</td>
            <td data-stat="fta_per_36_min">4.6</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb_per_36_min">0.8</td>
            <td data-stat="drb_per_36_min">5.6</td>
            <td data-stat="trb_per_36_min">6.4</td>
            <td data-stat="ast_per_36_min">8.4</td>
            <td data-stat="stl_per_36_min">1.3</td>
            <td data-stat="blk_per_36_min">0.5</td>
            <td data-stat="tov_per_36_min">3.0</td>
            <td data-stat="pf_per_36_min">1.1</td>
            <td data-stat="pts_per_36_min">25.6</td>
        </tr>
        <tr>
            <td data-stat="name_display">Giannis Antetokounmpo</td>
            <td data-stat="pos">PF</td>
            <td data-stat="age">29</td>
            <td data-stat="team_name_abbr">MIL</td>
            <td data-stat="games">73</td>
            <td data-stat="games_started">73</td>
            <td data-stat="mp">2555</td>
            <td data-stat="fg_per_36_min">11.6</td>
            <td data-stat="fga_per_36_min">19.3</td>
            <td data-stat="fg_pct">.611</td>
            <td data-stat="fg3_per_36_min">0.5</td>
            <td data-stat="fg3a_per_36_min">1.3</td>
            <td data-stat="fg3_pct">.274</td>
            <td data-stat="fg2_per_36_min">11.1</td>
            <td data-stat="fg2a_per_36_min">18.0</td>
            <td data-stat="fg2_pct">.617</td>
            <td data-stat="ft_per_36_min">7.4</td>
            <td data-stat="fta_per_36_min">10.4</td>
            <td data-stat="ft_pct">.657</td>
            <td data-stat="orb_per_36_min">2.5</td>
            <td data-stat="drb_per_36_min">9.2</td>
            <td data-stat="trb_per_36_min">11.7</td>
            <td data-stat="ast_per_36_min">6.4</td>
            <td data-stat="stl_per_36_min">1.1</td>
            <td data-stat="blk_per_36_min">1.4</td>
            <td data-stat="tov_per_36_min">3.5</td>
            <td data-stat="pf_per_36_min">2.7</td>
            <td data-stat="pts_per_36_min">31.3</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Totals stats (table id = totals_stats)
# ---------------------------------------------------------------------------
RICH_TOTALS_TABLE = """
<table id="totals_stats">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG</th><th>FGA</th><th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th>
            <th>2P</th><th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg">696</td>
            <td data-stat="fga">1392</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3">149</td>
            <td data-stat="fg3a">362</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="fg2">547</td>
            <td data-stat="fg2a">1030</td>
            <td data-stat="fg2_pct">.531</td>
            <td data-stat="efg_pct">.550</td>
            <td data-stat="ft">241</td>
            <td data-stat="fta">320</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb">57</td>
            <td data-stat="drb">391</td>
            <td data-stat="trb">448</td>
            <td data-stat="ast">589</td>
            <td data-stat="stl">92</td>
            <td data-stat="blk">36</td>
            <td data-stat="tov">206</td>
            <td data-stat="pf">78</td>
            <td data-stat="pts">1782</td>
        </tr>
        <tr>
            <td data-stat="name_display">Giannis Antetokounmpo</td>
            <td data-stat="pos">PF</td>
            <td data-stat="age">29</td>
            <td data-stat="team_name_abbr">MIL</td>
            <td data-stat="games">73</td>
            <td data-stat="games_started">73</td>
            <td data-stat="mp">2555</td>
            <td data-stat="fg">825</td>
            <td data-stat="fga">1372</td>
            <td data-stat="fg_pct">.611</td>
            <td data-stat="fg3">37</td>
            <td data-stat="fg3a">95</td>
            <td data-stat="fg3_pct">.274</td>
            <td data-stat="fg2">788</td>
            <td data-stat="fg2a">1277</td>
            <td data-stat="fg2_pct">.617</td>
            <td data-stat="efg_pct">.620</td>
            <td data-stat="ft">526</td>
            <td data-stat="fta">737</td>
            <td data-stat="ft_pct">.657</td>
            <td data-stat="orb">175</td>
            <td data-stat="drb">650</td>
            <td data-stat="trb">825</td>
            <td data-stat="ast">453</td>
            <td data-stat="stl">80</td>
            <td data-stat="blk">102</td>
            <td data-stat="tov">248</td>
            <td data-stat="pf">190</td>
            <td data-stat="pts">2212</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Rookies (table id = rookies)
# ---------------------------------------------------------------------------
RICH_ROOKIES_TABLE = """
<table id="rookies">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG</th><th>FGA</th><th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th>
            <th>2P</th><th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">Victor Wembanyama</td>
            <td data-stat="pos">C</td>
            <td data-stat="age">20</td>
            <td data-stat="team_name_abbr">SAS</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp_per_g">29.7</td>
            <td data-stat="fg_per_g">7.5</td>
            <td data-stat="fga_per_g">16.5</td>
            <td data-stat="fg_pct">.465</td>
            <td data-stat="fg3_per_g">1.8</td>
            <td data-stat="fg3a_per_g">5.5</td>
            <td data-stat="fg3_pct">.325</td>
            <td data-stat="fg2_per_g">5.7</td>
            <td data-stat="fg2a_per_g">11.0</td>
            <td data-stat="fg2_pct">.525</td>
            <td data-stat="efg_pct">.510</td>
            <td data-stat="ft_per_g">4.5</td>
            <td data-stat="fta_per_g">5.8</td>
            <td data-stat="ft_pct">.796</td>
            <td data-stat="orb_per_g">1.8</td>
            <td data-stat="drb_per_g">8.7</td>
            <td data-stat="trb_per_g">10.5</td>
            <td data-stat="ast_per_g">3.9</td>
            <td data-stat="stl_per_g">1.2</td>
            <td data-stat="blk_per_g">3.5</td>
            <td data-stat="tov_per_g">3.1</td>
            <td data-stat="pf_per_g">1.9</td>
            <td data-stat="pts_per_g">21.4</td>
        </tr>
        <tr>
            <td data-stat="name_display">Chet Holmgren</td>
            <td data-stat="pos">C</td>
            <td data-stat="age">22</td>
            <td data-stat="team_name_abbr">OKC</td>
            <td data-stat="games">82</td>
            <td data-stat="games_started">82</td>
            <td data-stat="mp_per_g">30.2</td>
            <td data-stat="fg_per_g">6.5</td>
            <td data-stat="fga_per_g">12.5</td>
            <td data-stat="fg_pct">.530</td>
            <td data-stat="fg3_per_g">1.5</td>
            <td data-stat="fg3a_per_g">4.3</td>
            <td data-stat="fg3_pct">.370</td>
            <td data-stat="fg2_per_g">5.0</td>
            <td data-stat="fg2a_per_g">8.2</td>
            <td data-stat="fg2_pct">.615</td>
            <td data-stat="efg_pct">.580</td>
            <td data-stat="ft_per_g">2.8</td>
            <td data-stat="fta_per_g">3.5</td>
            <td data-stat="ft_pct">.793</td>
            <td data-stat="orb_per_g">1.6</td>
            <td data-stat="drb_per_g">6.3</td>
            <td data-stat="trb_per_g">7.9</td>
            <td data-stat="ast_per_g">2.9</td>
            <td data-stat="stl_per_g">0.8</td>
            <td data-stat="blk_per_g">2.6</td>
            <td data-stat="tov_per_g">1.5</td>
            <td data-stat="pf_per_g">2.2</td>
            <td data-stat="pts_per_g">16.5</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Standings by date (table id = standings_by_date)
# ---------------------------------------------------------------------------
RICH_STANDINGS_BY_DATE_TABLE = """
<table id="standings_by_date">
    <thead>
        <tr><th>Team</th><th>W</th><th>L</th><th>W/L%</th><th>GB</th><th>PTS/G</th><th>OPP PTS/G</th><th>SRS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="team">Boston Celtics</td>
            <td data-stat="wins">64</td>
            <td data-stat="losses">18</td>
            <td data-stat="win_loss_pct">.780</td>
            <td data-stat="gb">—</td>
            <td data-stat="pts_per_g">120.6</td>
            <td data-stat="opp_pts_per_g">109.2</td>
            <td data-stat="srs">11.35</td>
        </tr>
        <tr>
            <td data-stat="team">Milwaukee Bucks</td>
            <td data-stat="wins">49</td>
            <td data-stat="losses">33</td>
            <td data-stat="win_loss_pct">.598</td>
            <td data-stat="gb">15.0</td>
            <td data-stat="pts_per_g">119.0</td>
            <td data-stat="opp_pts_per_g">116.3</td>
            <td data-stat="srs">2.61</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Attendance (table id = advanced-team)
# ---------------------------------------------------------------------------
RICH_ATTENDANCE_TABLE = """
<table id="advanced-team">
    <thead>
        <tr><th>Team</th><th>Home</th><th>Home Attendance</th><th>Home Att/G</th>
            <th>Away</th><th>Away Attendance</th><th>Away Att/G</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="team">Los Angeles Lakers</td>
            <td data-stat="home_games">41</td>
            <td data-stat="home_attendance">868000</td>
            <td data-stat="home_attendance_per_g">21171</td>
            <td data-stat="away_games">41</td>
            <td data-stat="away_attendance">820000</td>
            <td data-stat="away_attendance_per_g">20000</td>
        </tr>
        <tr>
            <td data-stat="team">Boston Celtics</td>
            <td data-stat="home_games">41</td>
            <td data-stat="home_attendance">763000</td>
            <td data-stat="home_attendance_per_g">18610</td>
            <td data-stat="away_games">41</td>
            <td data-stat="away_attendance">710000</td>
            <td data-stat="away_attendance_per_g">17317</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Transactions (table id = transactions)
# ---------------------------------------------------------------------------
RICH_TRANSACTIONS_TABLE = """
<table id="transactions">
    <thead>
        <tr><th>Date</th><th>Transaction</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="date">2024-06-20</td>
            <td data-stat="transaction">Lakers trade pick to Pelicans</td>
        </tr>
        <tr>
            <td data-stat="date">2024-06-27</td>
            <td data-stat="transaction">Celtics select Jayson Tatum in draft</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Per-100-possessions (table id = per_poss)
# ---------------------------------------------------------------------------
RICH_PER_POSS_TABLE = """
<table id="per_poss">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG/100</th><th>FGA/100</th><th>FG%</th><th>3P/100</th><th>3PA/100</th><th>3P%</th>
            <th>2P/100</th><th>2PA/100</th><th>2P%</th><th>FT/100</th><th>FTA/100</th><th>FT%</th>
            <th>ORB/100</th><th>DRB/100</th><th>TRB/100</th><th>AST/100</th><th>STL/100</th><th>BLK/100</th>
            <th>TOV/100</th><th>PF/100</th><th>PTS/100</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg_per_100_poss">13.8</td>
            <td data-stat="fga_per_100_poss">27.6</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3_per_100_poss">2.9</td>
            <td data-stat="fg3a_per_100_poss">7.2</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="fg2_per_100_poss">10.9</td>
            <td data-stat="fg2a_per_100_poss">20.4</td>
            <td data-stat="fg2_pct">.531</td>
            <td data-stat="ft_per_100_poss">4.8</td>
            <td data-stat="fta_per_100_poss">6.4</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb_per_100_poss">1.1</td>
            <td data-stat="drb_per_100_poss">7.8</td>
            <td data-stat="trb_per_100_poss">8.9</td>
            <td data-stat="ast_per_100_poss">11.7</td>
            <td data-stat="stl_per_100_poss">1.8</td>
            <td data-stat="blk_per_100_poss">0.7</td>
            <td data-stat="tov_per_100_poss">4.1</td>
            <td data-stat="pf_per_100_poss">1.5</td>
            <td data-stat="pts_per_100_poss">35.4</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Shooting (table id = shooting)
# ---------------------------------------------------------------------------
RICH_SHOOTING_TABLE = """
<table id="shooting">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>MP</th>
            <th>%3P</th><th>%3-10</th><th>%10-16</th><th>%16-3P</th><th>%3P</th>
            <th>%FGA 0-3</th><th>%FGA 3-10</th><th>%FGA 10-16</th><th>%FGA 16-3P</th><th>%FGA 3P</th>
            <th>%2P</th><th>%0-3</th><th>%C3</th><th>%FGA C3</th><th>Heaved</th><th>%Heaved</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg_pct_from_0_3_ft">.780</td>
            <td data-stat="fg_pct_from_3_10_ft">.420</td>
            <td data-stat="fg_pct_from_10_16_ft">.450</td>
            <td data-stat="fg_pct_from_16_3p">.390</td>
            <td data-stat="fg_pct_from_3p">.410</td>
            <td data-stat="pct_fga_from_0_3_ft">.250</td>
            <td data-stat="pct_fga_from_3_10_ft">.150</td>
            <td data-stat="pct_fga_from_10_16_ft">.100</td>
            <td data-stat="pct_fga_from_16_3p">.200</td>
            <td data-stat="pct_fga_from_3p">.300</td>
            <td data-stat="fg_pct_from_2p">.550</td>
            <td data-stat="fg_pct_from_0_3_ft_2">.780</td>
            <td data-stat="fg_pct_from_corner_3">.420</td>
            <td data-stat="pct_fga_from_corner_3">.080</td>
            <td data-stat="num_shots_heaved">2</td>
            <td data-stat="pct_shots_heaved">.001</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Helper for commented (hidden) tables
# ---------------------------------------------------------------------------
def _commented(html_table: str) -> str:
    """Wrap an HTML table inside HTML comments."""
    return f"<!--\n{html_table}\n-->"

# ---------------------------------------------------------------------------
# Playoff per-game (commented table id = per_game_stats_post)
# ---------------------------------------------------------------------------
RICH_PLAYOFF_PER_GAME_TABLE = _commented("""
<table id="per_game_stats_post">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG</th><th>FGA</th><th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th>
            <th>2P</th><th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">5</td>
            <td data-stat="games_started">5</td>
            <td data-stat="mp_per_g">38.2</td>
            <td data-stat="fg_per_g">10.4</td>
            <td data-stat="fga_per_g">21.8</td>
            <td data-stat="fg_pct">.477</td>
            <td data-stat="fg3_per_g">2.2</td>
            <td data-stat="fg3a_per_g">6.4</td>
            <td data-stat="fg3_pct">.344</td>
            <td data-stat="fg2_per_g">8.2</td>
            <td data-stat="fg2a_per_g">15.4</td>
            <td data-stat="fg2_pct">.532</td>
            <td data-stat="efg_pct">.530</td>
            <td data-stat="ft_per_g">4.8</td>
            <td data-stat="fta_per_g">5.6</td>
            <td data-stat="ft_pct">.857</td>
            <td data-stat="orb_per_g">1.2</td>
            <td data-stat="drb_per_g">6.4</td>
            <td data-stat="trb_per_g">7.6</td>
            <td data-stat="ast_per_g">9.2</td>
            <td data-stat="stl_per_g">1.6</td>
            <td data-stat="blk_per_g">0.8</td>
            <td data-stat="tov_per_g">3.4</td>
            <td data-stat="pf_per_g">1.8</td>
            <td data-stat="pts_per_g">27.8</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Playoff totals (commented table id = totals_stats_post)
# ---------------------------------------------------------------------------
RICH_PLAYOFF_TOTALS_TABLE = _commented("""
<table id="totals_stats_post">
    <thead>
        <tr><th>Player</th><th>Pos</th><th>Age</th><th>Team</th><th>G</th><th>GS</th><th>MP</th>
            <th>FG</th><th>FGA</th><th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th>
            <th>2P</th><th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="name_display">LeBron James</td>
            <td data-stat="pos">SF</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="games">5</td>
            <td data-stat="games_started">5</td>
            <td data-stat="mp">191</td>
            <td data-stat="fg">52</td>
            <td data-stat="fga">109</td>
            <td data-stat="fg_pct">.477</td>
            <td data-stat="fg3">11</td>
            <td data-stat="fg3a">32</td>
            <td data-stat="fg3_pct">.344</td>
            <td data-stat="fg2">41</td>
            <td data-stat="fg2a">77</td>
            <td data-stat="fg2_pct">.532</td>
            <td data-stat="efg_pct">.530</td>
            <td data-stat="ft">24</td>
            <td data-stat="fta">28</td>
            <td data-stat="ft_pct">.857</td>
            <td data-stat="orb">6</td>
            <td data-stat="drb">32</td>
            <td data-stat="trb">38</td>
            <td data-stat="ast">46</td>
            <td data-stat="stl">8</td>
            <td data-stat="blk">4</td>
            <td data-stat="tov">17</td>
            <td data-stat="pf">9</td>
            <td data-stat="pts">139</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Draft picks (table id = stats)
# ---------------------------------------------------------------------------
RICH_DRAFT_TABLE = """
<table id="stats">
    <thead>
        <tr><th>Pick</th><th>Player</th><th>College</th><th>Team</th><th>Seasons</th>
            <th>G</th><th>MP</th><th>PTS</th><th>TRB</th><th>AST</th>
            <th>FG%</th><th>3P%</th><th>FT%</th><th>MP/G</th><th>PTS/G</th>
            <th>TRB/G</th><th>AST/G</th><th>WS</th><th>WS/48</th><th>BPM</th><th>VORP</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="pick_overall">1</td>
            <td data-stat="player">LeBron James</td>
            <td data-stat="college_name">St. Vincent-St. Mary HS (OH)</td>
            <td data-stat="team_id">CLE</td>
            <td data-stat="seasons">21</td>
            <td data-stat="g">1492</td>
            <td data-stat="mp">56230</td>
            <td data-stat="pts">40474</td>
            <td data-stat="trb">11185</td>
            <td data-stat="ast">11009</td>
            <td data-stat="fg_pct">.506</td>
            <td data-stat="fg3_pct">.348</td>
            <td data-stat="ft_pct">.735</td>
            <td data-stat="mp_per_g">37.7</td>
            <td data-stat="pts_per_g">27.1</td>
            <td data-stat="trb_per_g">7.5</td>
            <td data-stat="ast_per_g">7.4</td>
            <td data-stat="ws">263.7</td>
            <td data-stat="ws_per_48">.225</td>
            <td data-stat="bpm">8.7</td>
            <td data-stat="vorp">151.2</td>
        </tr>
        <tr>
            <td data-stat="pick_overall">2</td>
            <td data-stat="player">Giannis Antetokounmpo</td>
            <td data-stat="college_name">Filathlitikos (Greece)</td>
            <td data-stat="team_id">MIL</td>
            <td data-stat="seasons">12</td>
            <td data-stat="g">859</td>
            <td data-stat="mp">30077</td>
            <td data-stat="pts">22593</td>
            <td data-stat="trb">9635</td>
            <td data-stat="ast">5167</td>
            <td data-stat="fg_pct">.550</td>
            <td data-stat="fg3_pct">.289</td>
            <td data-stat="ft_pct">.702</td>
            <td data-stat="mp_per_g">35.0</td>
            <td data-stat="pts_per_g">26.3</td>
            <td data-stat="trb_per_g">11.2</td>
            <td data-stat="ast_per_g">6.0</td>
            <td data-stat="ws">149.6</td>
            <td data-stat="ws_per_48">.239</td>
            <td data-stat="bpm">7.1</td>
            <td data-stat="vorp">81.5</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Season leaders (table id = stats_TOT)
# ---------------------------------------------------------------------------
RICH_SEASON_LEADERS_TABLE = """
<table id="stats_TOT">
    <thead>
        <tr><th>Rank</th><th>Player</th><th>Value</th><th>Season</th><th>Team</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="rank">1</td>
            <td data-stat="player">LeBron James</td>
            <td data-stat="value">40474</td>
            <td data-stat="season">2023-24</td>
            <td data-stat="team_id">LAL</td>
        </tr>
        <tr>
            <td data-stat="rank">2</td>
            <td data-stat="player">Giannis Antetokounmpo</td>
            <td data-stat="value">22593</td>
            <td data-stat="season">2023-24</td>
            <td data-stat="team_id">MIL</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Career leaders (table id = leaders_index)
# ---------------------------------------------------------------------------
RICH_CAREER_LEADERS_TABLE = """
<table id="leaders_index">
    <thead>
        <tr><th>Rank</th><th>Player</th><th>Value</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="rank">1</td>
            <td data-stat="player">LeBron James</td>
            <td data-stat="value">40474</td>
        </tr>
        <tr>
            <td data-stat="rank">2</td>
            <td data-stat="player">Kareem Abdul-Jabbar</td>
            <td data-stat="value">38387</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Playoff bracket (table id = all_playoffs)
# ---------------------------------------------------------------------------
RICH_PLAYOFF_BRACKET_TABLE = """
<table id="all_playoffs">
    <thead>
        <tr><th>Series</th><th>Team</th><th>Result</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="series">NBA Finals</td>
            <td data-stat="team">Boston Celtics</td>
            <td data-stat="result">Won NBA Championship</td>
        </tr>
        <tr>
            <td data-stat="series">NBA Finals</td>
            <td data-stat="team">Dallas Mavericks</td>
            <td data-stat="result">Lost NBA Championship</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Season awards (table id = mvp)
# ---------------------------------------------------------------------------
RICH_AWARDS_TABLE = """
<table id="mvp">
    <thead>
        <tr><th>Award</th><th>Player</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="award">Most Valuable Player</td>
            <td data-stat="player">Nikola Jokic</td>
        </tr>
        <tr>
            <td data-stat="award">Rookie of the Year</td>
            <td data-stat="player">Victor Wembanyama</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Player career stats (table id = per_game_stats on player page)
# Uses different data-stat keys than league per_game
# ---------------------------------------------------------------------------
RICH_PLAYER_CAREER_TABLE = """
<table id="per_game_stats">
    <thead>
        <tr><th>Season</th><th>Age</th><th>Team</th><th>Lg</th><th>Pos</th>
            <th>G</th><th>GS</th><th>MP</th><th>FG</th><th>FGA</th>
            <th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th><th>2P</th>
            <th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th>
            <th>FT%</th><th>ORB</th><th>DRB</th><th>TRB</th>
            <th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="games">71</td>
            <td data-stat="games_started">71</td>
            <td data-stat="mp_per_g">35.3</td>
            <td data-stat="fg_per_g">9.8</td>
            <td data-stat="fga_per_g">19.6</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3_per_g">2.1</td>
            <td data-stat="fg3a_per_g">5.1</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="fg2_per_g">7.7</td>
            <td data-stat="fg2a_per_g">14.5</td>
            <td data-stat="fg2_pct">.531</td>
            <td data-stat="efg_pct">.550</td>
            <td data-stat="ft_per_g">3.4</td>
            <td data-stat="fta_per_g">4.5</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb_per_g">0.8</td>
            <td data-stat="drb_per_g">5.5</td>
            <td data-stat="trb_per_g">6.3</td>
            <td data-stat="ast_per_g">8.3</td>
            <td data-stat="stl_per_g">1.3</td>
            <td data-stat="blk_per_g">0.5</td>
            <td data-stat="tov_per_g">2.9</td>
            <td data-stat="pf_per_g">1.1</td>
            <td data-stat="pts_per_g">25.1</td>
        </tr>
        <tr>
            <td data-stat="season">2022-23</td>
            <td data-stat="age">38</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="games">55</td>
            <td data-stat="games_started">55</td>
            <td data-stat="mp_per_g">35.5</td>
            <td data-stat="fg_per_g">10.0</td>
            <td data-stat="fga_per_g">20.8</td>
            <td data-stat="fg_pct">.481</td>
            <td data-stat="fg3_per_g">2.0</td>
            <td data-stat="fg3a_per_g">5.9</td>
            <td data-stat="fg3_pct">.339</td>
            <td data-stat="fg2_per_g">8.0</td>
            <td data-stat="fg2a_per_g">14.9</td>
            <td data-stat="fg2_pct">.537</td>
            <td data-stat="efg_pct">.525</td>
            <td data-stat="ft_per_g">3.1</td>
            <td data-stat="fta_per_g">4.2</td>
            <td data-stat="ft_pct">.738</td>
            <td data-stat="orb_per_g">0.7</td>
            <td data-stat="drb_per_g">5.8</td>
            <td data-stat="trb_per_g">6.5</td>
            <td data-stat="ast_per_g">8.5</td>
            <td data-stat="stl_per_g">1.2</td>
            <td data-stat="blk_per_g">0.6</td>
            <td data-stat="tov_per_g">2.8</td>
            <td data-stat="pf_per_g">1.0</td>
            <td data-stat="pts_per_g">25.0</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Player playoff series (commented table id = playoffs_series)
# ---------------------------------------------------------------------------
RICH_PLAYER_PLAYOFF_SERIES_TABLE = _commented("""
<table id="playoffs_series">
    <thead>
        <tr><th>Season</th><th>Age</th><th>Team</th><th>Lg</th><th>Pos</th>
            <th>G</th><th>GS</th><th>MP</th><th>FG</th><th>FGA</th>
            <th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th><th>2P</th>
            <th>2PA</th><th>2P%</th><th>eFG%</th><th>FT</th><th>FTA</th>
            <th>FT%</th><th>ORB</th><th>DRB</th><th>TRB</th>
            <th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="games">5</td>
            <td data-stat="games_started">5</td>
            <td data-stat="mp_per_g">38.2</td>
            <td data-stat="fg_per_g">10.4</td>
            <td data-stat="fga_per_g">21.8</td>
            <td data-stat="fg_pct">.477</td>
            <td data-stat="fg3_per_g">2.2</td>
            <td data-stat="fg3a_per_g">6.4</td>
            <td data-stat="fg3_pct">.344</td>
            <td data-stat="fg2_per_g">8.2</td>
            <td data-stat="fg2a_per_g">15.4</td>
            <td data-stat="fg2_pct">.532</td>
            <td data-stat="efg_pct">.530</td>
            <td data-stat="ft_per_g">4.8</td>
            <td data-stat="fta_per_g">5.6</td>
            <td data-stat="ft_pct">.857</td>
            <td data-stat="orb_per_g">1.2</td>
            <td data-stat="drb_per_g">6.4</td>
            <td data-stat="trb_per_g">7.6</td>
            <td data-stat="ast_per_g">9.2</td>
            <td data-stat="stl_per_g">1.6</td>
            <td data-stat="blk_per_g">0.8</td>
            <td data-stat="tov_per_g">3.4</td>
            <td data-stat="pf_per_g">1.8</td>
            <td data-stat="pts_per_g">27.8</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player splits (table id = splits)
# ---------------------------------------------------------------------------
RICH_SPLITS_TABLE = """
<table id="splits">
    <thead>
        <tr><th>Split</th><th>Value</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="split_type">Location</td>
            <td data-stat="value">Home</td>
            <td data-stat="g">35</td>
            <td data-stat="mp">1235</td>
            <td data-stat="fg">350</td>
            <td data-stat="fga">680</td>
            <td data-stat="fg_pct">.515</td>
            <td data-stat="fg3">80</td>
            <td data-stat="fg3a">180</td>
            <td data-stat="fg3_pct">.444</td>
            <td data-stat="ft">120</td>
            <td data-stat="fta">160</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb">25</td>
            <td data-stat="drb">190</td>
            <td data-stat="trb">215</td>
            <td data-stat="ast">300</td>
            <td data-stat="stl">45</td>
            <td data-stat="blk">18</td>
            <td data-stat="tov">100</td>
            <td data-stat="pf">40</td>
            <td data-stat="pts">900</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Player on-off (table id = on-off)
# ---------------------------------------------------------------------------
RICH_PLAYER_ON_OFF_TABLE = """
<table id="on-off">
    <thead>
        <tr><th>Situation</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="situation">On Court</td>
            <td data-stat="g">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg">696</td>
            <td data-stat="fga">1392</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3">149</td>
            <td data-stat="fg3a">362</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="ft">241</td>
            <td data-stat="fta">320</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb">57</td>
            <td data-stat="drb">391</td>
            <td data-stat="trb">448</td>
            <td data-stat="ast">589</td>
            <td data-stat="stl">92</td>
            <td data-stat="blk">36</td>
            <td data-stat="tov">206</td>
            <td data-stat="pf">78</td>
            <td data-stat="pts">1782</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Player shot charts (table id = shooting)
# ---------------------------------------------------------------------------
RICH_SHOT_CHARTS_TABLE = """
<table id="shooting">
    <thead>
        <tr><th>Shot Type</th><th>Made</th><th>Attempted</th><th>FG%</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="shot_type">Dunk</td>
            <td data-stat="made">120</td>
            <td data-stat="attempted">125</td>
            <td data-stat="fg_pct">.960</td>
        </tr>
        <tr>
            <td data-stat="shot_type">Jump Shot</td>
            <td data-stat="made">350</td>
            <td data-stat="attempted">850</td>
            <td data-stat="fg_pct">.412</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Player adjusted shooting (commented table id = adj_shooting)
# ---------------------------------------------------------------------------
RICH_ADJUSTED_SHOOTING_TABLE = _commented("""
<table id="adj_shooting">
    <thead>
        <tr><th>Season</th><th>Age</th><th>Team</th><th>Lg</th><th>Pos</th><th>G</th><th>MP</th>
            <th>FG%</th><th>3P%</th><th>FT%</th><th>TS%</th><th>FG/36</th><th>FGA/36</th>
            <th>Adj FG%</th><th>Adj 3P%</th><th>Adj FT%</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="age">39</td>
            <td data-stat="team_id">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="g">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="ts_pct">.580</td>
            <td data-stat="fg_per_36_min">10.0</td>
            <td data-stat="fga_per_36_min">20.0</td>
            <td data-stat="adjusted_fg_pct">.510</td>
            <td data-stat="adjusted_fg3_pct">.420</td>
            <td data-stat="adjusted_ft_pct">.760</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player play-by-play (commented table id = pbp_stats)
# ---------------------------------------------------------------------------
RICH_PLAYER_PBP_TABLE = _commented("""
<table id="pbp_stats">
    <thead>
        <tr><th>Season</th><th>Age</th><th>Team</th><th>Lg</th><th>Pos</th><th>G</th><th>MP</th>
            <th>%2P</th><th>%3P</th><th>%Astd 2P</th><th>%Astd 3P</th>
            <th>%Dunks</th><th>%C3</th><th>%Heaves</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="age">39</td>
            <td data-stat="team_id">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="g">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="pct_fg_2pt">.710</td>
            <td data-stat="pct_fg_3pt">.290</td>
            <td data-stat="pct_ast_2pt">.420</td>
            <td data-stat="pct_ast_3pt">.650</td>
            <td data-stat="pct_dunks">.080</td>
            <td data-stat="pct_corner_3s">.120</td>
            <td data-stat="pct_heaves">.001</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player game highs (commented table id = highs-reg-season)
# ---------------------------------------------------------------------------
RICH_GAME_HIGHS_TABLE = _commented("""
<table id="highs-reg-season">
    <thead>
        <tr><th>Stat</th><th>Value</th><th>Date</th><th>Opponent</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="stat">Points</td>
            <td data-stat="value">48</td>
            <td data-stat="date">2024-01-15</td>
            <td data-stat="opponent">Los Angeles Lakers</td>
        </tr>
        <tr>
            <td data-stat="stat">Rebounds</td>
            <td data-stat="value">20</td>
            <td data-stat="date">2024-02-01</td>
            <td data-stat="opponent">Boston Celtics</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player all-star (commented table id = all_star)
# ---------------------------------------------------------------------------
RICH_ALL_STAR_TABLE = _commented("""
<table id="all_star">
    <thead>
        <tr><th>Season</th><th>Age</th><th>Team</th><th>Lg</th><th>Pos</th>
            <th>G</th><th>GS</th><th>MP</th><th>FG</th><th>FGA</th>
            <th>FG%</th><th>3P</th><th>3PA</th><th>3P%</th>
            <th>FT</th><th>FTA</th><th>FT%</th><th>ORB</th><th>DRB</th><th>TRB</th>
            <th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2024</td>
            <td data-stat="age">39</td>
            <td data-stat="team_name_abbr">LAL</td>
            <td data-stat="league_id">NBA</td>
            <td data-stat="pos">SF</td>
            <td data-stat="games">1</td>
            <td data-stat="games_started">1</td>
            <td data-stat="mp_per_g">14.0</td>
            <td data-stat="fg_per_g">4.0</td>
            <td data-stat="fga_per_g">10.0</td>
            <td data-stat="fg_pct">.400</td>
            <td data-stat="fg3_per_g">0.0</td>
            <td data-stat="fg3a_per_g">2.0</td>
            <td data-stat="fg3_pct">.000</td>
            <td data-stat="ft_per_g">0.0</td>
            <td data-stat="fta_per_g">0.0</td>
            <td data-stat="ft_pct"></td>
            <td data-stat="orb_per_g">0.0</td>
            <td data-stat="drb_per_g">2.0</td>
            <td data-stat="trb_per_g">2.0</td>
            <td data-stat="ast_per_g">4.0</td>
            <td data-stat="stl_per_g">0.0</td>
            <td data-stat="blk_per_g">0.0</td>
            <td data-stat="tov_per_g">2.0</td>
            <td data-stat="pf_per_g">0.0</td>
            <td data-stat="pts_per_g">8.0</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player similarity scores (commented table id = sims-career)
# ---------------------------------------------------------------------------
RICH_SIMILARITY_TABLE = _commented("""
<table id="sims-career">
    <thead>
        <tr><th>Rank</th><th>Player</th><th>Similarity</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="rank">1</td>
            <td data-stat="player">Kareem Abdul-Jabbar</td>
            <td data-stat="similarity_score">98.5</td>
        </tr>
        <tr>
            <td data-stat="rank">2</td>
            <td data-stat="player">Karl Malone</td>
            <td data-stat="similarity_score">95.2</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Player salaries (commented table id = all_salaries)
# ---------------------------------------------------------------------------
RICH_SALARIES_TABLE = _commented("""
<table id="all_salaries">
    <thead>
        <tr><th>Season</th><th>Team</th><th>Salary</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="team_id">LAL</td>
            <td data-stat="salary">$47,607,350</td>
        </tr>
        <tr>
            <td data-stat="season">2024-25</td>
            <td data-stat="team_id">LAL</td>
            <td data-stat="salary">$48,727,654</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Team roster (table id = roster)
# ---------------------------------------------------------------------------
RICH_ROSTER_TABLE = """
<table id="roster">
    <thead>
        <tr><th>Player</th><th>Number</th><th>Pos</th><th>Height</th><th>Weight</th>
            <th>Birth Date</th><th>Flag</th><th>Exp</th><th>College</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="player">LeBron James</td>
            <td data-stat="number">23</td>
            <td data-stat="pos">SF</td>
            <td data-stat="height">6-9</td>
            <td data-stat="weight">250</td>
            <td data-stat="birth_date">1984-12-30</td>
            <td data-stat="flag">USA</td>
            <td data-stat="years_experience">21</td>
            <td data-stat="college"></td>
        </tr>
        <tr>
            <td data-stat="player">Anthony Davis</td>
            <td data-stat="number">3</td>
            <td data-stat="pos">C</td>
            <td data-stat="height">6-10</td>
            <td data-stat="weight">253</td>
            <td data-stat="birth_date">1993-03-11</td>
            <td data-stat="flag">USA</td>
            <td data-stat="years_experience">12</td>
            <td data-stat="college">Kentucky</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team injury report (table id = injuries)
# ---------------------------------------------------------------------------
RICH_INJURY_TABLE = """
<table id="injuries">
    <thead>
        <tr><th>Player</th><th>Date</th><th>Description</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="player">LeBron James</td>
            <td data-stat="date">2024-03-15</td>
            <td data-stat="description">Left ankle soreness, day to day</td>
        </tr>
        <tr>
            <td data-stat="player">Anthony Davis</td>
            <td data-stat="date">2024-03-14</td>
            <td data-stat="description">Right knee contusion, questionable</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team and opponent (commented table id = team_and_opponent)
# ---------------------------------------------------------------------------
RICH_TEAM_AND_OPPONENT_TABLE = _commented("""
<table id="team_and_opponent">
    <thead>
        <tr><th>Type</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="stat_type">Team</td>
            <td data-stat="g">82</td>
            <td data-stat="mp">19780</td>
            <td data-stat="fg">3890</td>
            <td data-stat="fga">7890</td>
            <td data-stat="fg_pct">.493</td>
            <td data-stat="fg3">980</td>
            <td data-stat="fg3a">2760</td>
            <td data-stat="fg3_pct">.355</td>
            <td data-stat="ft">1560</td>
            <td data-stat="fta">2050</td>
            <td data-stat="ft_pct">.761</td>
            <td data-stat="orb">890</td>
            <td data-stat="drb">2980</td>
            <td data-stat="trb">3870</td>
            <td data-stat="ast">2450</td>
            <td data-stat="stl">680</td>
            <td data-stat="blk">450</td>
            <td data-stat="tov">1120</td>
            <td data-stat="pf">1650</td>
            <td data-stat="pts">10320</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Team misc four factors (commented table id = team_misc)
# ---------------------------------------------------------------------------
RICH_TEAM_MISC_TABLE = _commented("""
<table id="team_misc">
    <thead>
        <tr><th>Type</th><th>Pace</th><th>eFG%</th><th>TOV%</th><th>ORB%</th><th>FT/FGA</th>
            <th>Opp eFG%</th><th>Opp TOV%</th><th>DRB%</th><th>Opp FT/FGA</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="stat_type">Team</td>
            <td data-stat="pace">99.5</td>
            <td data-stat="efg_pct">.540</td>
            <td data-stat="tov_pct">12.5</td>
            <td data-stat="orb_pct">28.5</td>
            <td data-stat="ft_rate">.260</td>
            <td data-stat="opp_efg_pct">.520</td>
            <td data-stat="opp_tov_pct">13.2</td>
            <td data-stat="drb_pct">74.5</td>
            <td data-stat="opp_ft_rate">.240</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Team schedule/games (table id = games)
# ---------------------------------------------------------------------------
RICH_GAMES_TABLE = """
<table id="games">
    <thead>
        <tr><th>G</th><th>Date</th><th>Time</th><th>Away</th><th>Away Score</th>
            <th>Home</th><th>Home Score</th><th>Result</th><th>OT</th><th>W</th><th>L</th><th>Streak</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="game_number">1</td>
            <td data-stat="date">2023-10-24</td>
            <td data-stat="start_time">7:30 PM</td>
            <td data-stat="away_team">Los Angeles Lakers</td>
            <td data-stat="away_team_score">107</td>
            <td data-stat="home_team">Denver Nuggets</td>
            <td data-stat="home_team_score">119</td>
            <td data-stat="result">L</td>
            <td data-stat="overtimes">0</td>
            <td data-stat="wins">0</td>
            <td data-stat="losses">1</td>
            <td data-stat="streak">L 1</td>
        </tr>
        <tr>
            <td data-stat="game_number">2</td>
            <td data-stat="date">2023-10-26</td>
            <td data-stat="start_time">10:00 PM</td>
            <td data-stat="away_team">Phoenix Suns</td>
            <td data-stat="away_team_score">104</td>
            <td data-stat="home_team">Los Angeles Lakers</td>
            <td data-stat="home_team_score">100</td>
            <td data-stat="result">L</td>
            <td data-stat="overtimes">0</td>
            <td data-stat="wins">0</td>
            <td data-stat="losses">2</td>
            <td data-stat="streak">L 2</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team splits (table id = team_splits)
# ---------------------------------------------------------------------------
RICH_TEAM_SPLITS_TABLE = """
<table id="team_splits">
    <thead>
        <tr><th>Split</th><th>Value</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="split_type">Location</td>
            <td data-stat="value">Home</td>
            <td data-stat="g">41</td>
            <td data-stat="mp">9890</td>
            <td data-stat="fg">1960</td>
            <td data-stat="fga">3950</td>
            <td data-stat="fg_pct">.496</td>
            <td data-stat="fg3">490</td>
            <td data-stat="fg3a">1380</td>
            <td data-stat="fg3_pct">.355</td>
            <td data-stat="ft">780</td>
            <td data-stat="fta">1025</td>
            <td data-stat="ft_pct">.761</td>
            <td data-stat="orb">445</td>
            <td data-stat="drb">1490</td>
            <td data-stat="trb">1935</td>
            <td data-stat="ast">1225</td>
            <td data-stat="stl">340</td>
            <td data-stat="blk">225</td>
            <td data-stat="tov">560</td>
            <td data-stat="pf">825</td>
            <td data-stat="pts">5160</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team contracts (table id = contracts)
# ---------------------------------------------------------------------------
RICH_CONTRACTS_TABLE = """
<table id="contracts">
    <thead>
        <tr><th>Player</th><th>Salary</th><th>Years Remaining</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="player">LeBron James</td>
            <td data-stat="salary">$47,607,350</td>
            <td data-stat="years_remaining">2</td>
        </tr>
        <tr>
            <td data-stat="player">Anthony Davis</td>
            <td data-stat="salary">$43,219,440</td>
            <td data-stat="years_remaining">4</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team lineups (commented table id = lineups_5-man_)
# ---------------------------------------------------------------------------
RICH_LINEUPS_TABLE = _commented("""
<table id="lineups_5-man_">
    <thead>
        <tr><th>Lineup</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="lineup">D. Russell - A. Reaves - L. James - R. Hachimura - A. Davis</td>
            <td data-stat="g">25</td>
            <td data-stat="mp">420</td>
            <td data-stat="fg">180</td>
            <td data-stat="fga">370</td>
            <td data-stat="fg_pct">.486</td>
            <td data-stat="fg3">45</td>
            <td data-stat="fg3a">130</td>
            <td data-stat="fg3_pct">.346</td>
            <td data-stat="ft">80</td>
            <td data-stat="fta">105</td>
            <td data-stat="ft_pct">.762</td>
            <td data-stat="orb">40</td>
            <td data-stat="drb">140</td>
            <td data-stat="trb">180</td>
            <td data-stat="ast">120</td>
            <td data-stat="stl">35</td>
            <td data-stat="blk">20</td>
            <td data-stat="tov">55</td>
            <td data-stat="pf">80</td>
            <td data-stat="pts">485</td>
        </tr>
    </tbody>
</table>
""")

# ---------------------------------------------------------------------------
# Team starting lineups (table id = starting_lineups_po0)
# ---------------------------------------------------------------------------
RICH_STARTING_LINEUPS_TABLE = """
<table id="starting_lineups_po0">
    <thead>
        <tr><th>Player</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="player">LeBron James</td>
            <td data-stat="g">71</td>
            <td data-stat="mp">2506</td>
            <td data-stat="fg">696</td>
            <td data-stat="fga">1392</td>
            <td data-stat="fg_pct">.502</td>
            <td data-stat="fg3">149</td>
            <td data-stat="fg3a">362</td>
            <td data-stat="fg3_pct">.410</td>
            <td data-stat="ft">241</td>
            <td data-stat="fta">320</td>
            <td data-stat="ft_pct">.750</td>
            <td data-stat="orb">57</td>
            <td data-stat="drb">391</td>
            <td data-stat="trb">448</td>
            <td data-stat="ast">589</td>
            <td data-stat="stl">92</td>
            <td data-stat="blk">36</td>
            <td data-stat="tov">206</td>
            <td data-stat="pf">78</td>
            <td data-stat="pts">1782</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Team on-off (table id = on_off)
# ---------------------------------------------------------------------------
RICH_TEAM_ON_OFF_TABLE = """
<table id="on_off">
    <thead>
        <tr><th>Situation</th><th>G</th><th>MP</th><th>FG</th><th>FGA</th><th>FG%</th>
            <th>3P</th><th>3PA</th><th>3P%</th><th>FT</th><th>FTA</th><th>FT%</th>
            <th>ORB</th><th>DRB</th><th>TRB</th><th>AST</th><th>STL</th><th>BLK</th><th>TOV</th><th>PF</th><th>PTS</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="situation">On Court</td>
            <td data-stat="g">82</td>
            <td data-stat="mp">19780</td>
            <td data-stat="fg">3890</td>
            <td data-stat="fga">7890</td>
            <td data-stat="fg_pct">.493</td>
            <td data-stat="fg3">980</td>
            <td data-stat="fg3a">2760</td>
            <td data-stat="fg3_pct">.355</td>
            <td data-stat="ft">1560</td>
            <td data-stat="fta">2050</td>
            <td data-stat="ft_pct">.761</td>
            <td data-stat="orb">890</td>
            <td data-stat="drb">2980</td>
            <td data-stat="trb">3870</td>
            <td data-stat="ast">2450</td>
            <td data-stat="stl">680</td>
            <td data-stat="blk">450</td>
            <td data-stat="tov">1120</td>
            <td data-stat="pf">1650</td>
            <td data-stat="pts">10320</td>
        </tr>
    </tbody>
</table>
"""

# ---------------------------------------------------------------------------
# Franchise history (table id = team abbreviation, e.g. LAL)
# ---------------------------------------------------------------------------
RICH_FRANCHISE_HISTORY_TABLE = """
<table id="LAL">
    <thead>
        <tr><th>Season</th><th>Team</th><th>W</th><th>L</th><th>Playoffs</th></tr>
    </thead>
    <tbody>
        <tr>
            <td data-stat="season">2023-24</td>
            <td data-stat="team_abbreviation">LAL</td>
            <td data-stat="wins">47</td>
            <td data-stat="losses">35</td>
            <td data-stat="playoffs">First Round</td>
        </tr>
        <tr>
            <td data-stat="season">2022-23</td>
            <td data-stat="team_abbreviation">LAL</td>
            <td data-stat="wins">43</td>
            <td data-stat="losses">39</td>
            <td data-stat="playoffs">Conference Finals</td>
        </tr>
    </tbody>
</table>
"""
