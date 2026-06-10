"""Season-totals tables and rows (basic and advanced)."""

from __future__ import annotations

from lxml.html import HtmlElement

from courtside_data.html._helpers import cell_text
from courtside_data.html.boxscores import PlayerIdentificationRow


class PlayerAdvancedSeasonTotalsTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows_query(self):
        # Basketball Reference includes individual rows for players that played for multiple teams in a season.
        # It also includes a "League Average" row that has a class value of 'norank'.
        return """
            //table[@id="advanced"]
            /tbody
            /tr[
                (
                    not(contains(@class, 'thead')) and
                    not(contains(@class, 'norank'))
                )
            ]
        """

    def get_rows(self, include_combined_totals=False):
        player_advanced_season_totals_rows = []
        for row_html in self.html.xpath(self.rows_query):
            row = PlayerAdvancedSeasonTotalsRow(html=row_html)
            if (include_combined_totals is True and row.is_combined_totals is True) or row.is_combined_totals is False:
                # Basketball Reference includes a "total" row for players that got traded
                # which is essentially a sum of all player team rows
                # I want to avoid including those, so I check the "team" field value for "TOT"
                player_advanced_season_totals_rows.append(row)

        return player_advanced_season_totals_rows


class PlayerSeasonTotalTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows_query(self):
        # Basketball Reference includes individual rows for players that played for multiple teams in a season.
        # It also includes a "League Average" row that has a class value of 'norank'.
        return """
                    //table[@id='totals_stats']
                    /tbody
                    /tr[
                        not(contains(@class, 'thead')) and
                        not(contains(@class, 'norank'))
                    ]
                """

    @property
    def rows(self):
        player_season_totals_rows = []
        for row_html in self.html.xpath(self.rows_query):
            row = PlayerSeasonTotalsRow(html=row_html)
            # Basketball Reference includes a "total" row for players that got traded
            # which is essentially a sum of all player team rows
            # I want to avoid including those, so I check the "team" field value for "TOT"
            if not row.is_combined_totals:
                player_season_totals_rows.append(row)

        return player_season_totals_rows


class PlayerAdvancedSeasonTotalsRow(PlayerIdentificationRow):
    def __init__(self, html: HtmlElement) -> None:
        super().__init__(html=html)

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="name_display"]')

        if len(cells) > 0:
            return cells[0]

        return None

    @property
    def slug(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.get("data-append-csv")

    @property
    def name(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.text_content()

    @property
    def position_abbreviations(self):
        return cell_text(self.html, "pos")

    @property
    def age(self):
        return cell_text(self.html, "age")

    @property
    def team_abbreviation(self):
        return cell_text(self.html, "team_name_abbr")

    @property
    def games_played(self):
        return cell_text(self.html, "games")

    @property
    def minutes_played(self):
        return cell_text(self.html, "mp")

    @property
    def player_efficiency_rating(self):
        return cell_text(self.html, "per")

    @property
    def true_shooting_percentage(self):
        return cell_text(self.html, "ts_pct")

    @property
    def three_point_attempt_rate(self):
        return cell_text(self.html, "fg3a_per_fga_pct")

    @property
    def free_throw_attempt_rate(self):
        return cell_text(self.html, "fta_per_fga_pct")

    @property
    def offensive_rebound_percentage(self):
        return cell_text(self.html, "orb_pct")

    @property
    def defensive_rebound_percentage(self):
        return cell_text(self.html, "drb_pct")

    @property
    def total_rebound_percentage(self):
        return cell_text(self.html, "trb_pct")

    @property
    def assist_percentage(self):
        return cell_text(self.html, "ast_pct")

    @property
    def steal_percentage(self):
        return cell_text(self.html, "stl_pct")

    @property
    def block_percentage(self):
        return cell_text(self.html, "blk_pct")

    @property
    def turnover_percentage(self):
        return cell_text(self.html, "tov_pct")

    @property
    def usage_percentage(self):
        return cell_text(self.html, "usg_pct")

    @property
    def offensive_win_shares(self):
        return cell_text(self.html, "ows")

    @property
    def defensive_win_shares(self):
        return cell_text(self.html, "dws")

    @property
    def win_shares(self):
        return cell_text(self.html, "ws")

    @property
    def win_shares_per_48_minutes(self):
        return cell_text(self.html, "ws_per_48")

    @property
    def offensive_plus_minus(self):
        return cell_text(self.html, "obpm")

    @property
    def defensive_plus_minus(self):
        return cell_text(self.html, "dbpm")

    @property
    def plus_minus(self):
        return cell_text(self.html, "bpm")

    @property
    def value_over_replacement_player(self):
        return cell_text(self.html, "vorp")

    @property
    def is_combined_totals(self):
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use the 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")


class PlayerSeasonTotalsRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def position_abbreviations(self):
        return cell_text(self.html, "pos")

    @property
    def age(self):
        return cell_text(self.html, "age")

    @property
    def games_played(self):
        return cell_text(self.html, "games")

    @property
    def games_started(self):
        return cell_text(self.html, "games_started")

    @property
    def is_combined_totals(self):
        #  No longer says 'TOT' - now says 2TM, 3TM, etc.
        # Can safely use the 'TM' suffix as an identifier as no team abbreviations
        # end in 'TM'
        return self.team_abbreviation.endswith("TM")

    @property
    def team_abbreviation(self):
        return cell_text(self.html, "team_name_abbr")

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="name_display"]')

        if len(cells) > 0:
            return cells[0]

        return None

    @property
    def slug(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.get("data-append-csv")

    @property
    def name(self):
        cell = self.player_cell
        if cell is None:
            return ""

        return cell.text_content()

    @property
    def playing_time(self):
        return cell_text(self.html, "mp")

    @property
    def minutes_played(self):
        return self.playing_time

    @property
    def made_field_goals(self):
        return cell_text(self.html, "fg")

    @property
    def attempted_field_goals(self):
        return cell_text(self.html, "fga")

    @property
    def made_three_point_field_goals(self):
        return cell_text(self.html, "fg3")

    @property
    def attempted_three_point_field_goals(self):
        return cell_text(self.html, "fg3a")

    @property
    def made_free_throws(self):
        return cell_text(self.html, "ft")

    @property
    def attempted_free_throws(self):
        return cell_text(self.html, "fta")

    @property
    def offensive_rebounds(self):
        return cell_text(self.html, "orb")

    @property
    def defensive_rebounds(self):
        return cell_text(self.html, "drb")

    @property
    def assists(self):
        return cell_text(self.html, "ast")

    @property
    def steals(self):
        return cell_text(self.html, "stl")

    @property
    def blocks(self):
        return cell_text(self.html, "blk")

    @property
    def turnovers(self):
        return cell_text(self.html, "tov")

    @property
    def personal_fouls(self):
        return cell_text(self.html, "pf")

    @property
    def points(self):
        return cell_text(self.html, "pts")
