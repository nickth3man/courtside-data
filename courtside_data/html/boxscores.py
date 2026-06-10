"""Box-score pages and rows: daily leaders, game box scores, player game logs."""

from __future__ import annotations

import re

from lxml.html import HtmlElement

from courtside_data.html._helpers import cell_text


class BasicBoxScoreRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

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

    @property
    def location_abbreviation(self):
        return cell_text(self.html, "game_location")

    @property
    def outcome(self):
        return cell_text(self.html, "game_result")

    @property
    def plus_minus(self):
        return cell_text(self.html, "plus_minus")

    @property
    def game_score(self):
        return cell_text(self.html, "game_score")


class PlayerSeasonGameLogRow(BasicBoxScoreRow):
    def __init__(self, html: HtmlElement) -> None:
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerSeasonGameLogRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        return cell_text(self.html, "team_name_abbr")

    @property
    def opponent_abbreviation(self):
        return cell_text(self.html, "opp_name_abbr")


class PlayerBoxScoreRow(BasicBoxScoreRow):
    def __init__(self, html: HtmlElement) -> None:
        super().__init__(html=html)

    def __eq__(self, other):
        if isinstance(other, PlayerBoxScoreRow):
            return self.html == other.html
        return False

    @property
    def team_abbreviation(self):
        return cell_text(self.html, "team_id")

    @property
    def opponent_abbreviation(self):
        return cell_text(self.html, "opp_id")


class PlayerIdentificationRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def player_cell(self):
        cells = self.html.xpath('td[@data-stat="player"]')

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


class BoxScoresPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def statistics_tables(self):
        return [
            StatisticsTable(table_html) for table_html in self.html.xpath('//table[contains(@class, "stats_table")]')
        ]

    @property
    def basic_statistics_tables(self):
        return [table for table in self.statistics_tables if table.has_basic_statistics is True]


class StatisticsTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def has_basic_statistics(self):
        return "game-basic" in self.html.attrib["id"]

    @property
    def team_abbreviation(self):
        # Example id value is box-BOS-game-basic or box-BOS-game-advanced
        match = re.match("^box-(.+)-game", self.html.attrib["id"])
        if match is None:
            raise ValueError(f"Could not parse team abbreviation from table id: {self.html.attrib['id']}")
        return match.group(1)

    @property
    def team_totals(self):
        # Team totals are stored as table footers
        footers = self.html.xpath("tfoot/tr")
        if len(footers) > 0:
            return BasicBoxScoreRow(html=footers[0])

        return None


class DailyLeadersPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def daily_leaders(self):
        return [
            PlayerGameBoxScoreRow(row_html)
            for row_html in self.html.xpath('//table[@id="stats"]//tbody/tr[not(contains(@class, "thead"))]')
        ]


class PlayerSeasonBoxScoresPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def regular_season_box_scores_table_query(self):
        return '//table[@id="player_game_log_reg"]'

    @property
    def regular_season_box_scores_table(self):
        matching_tables = self.html.xpath(self.regular_season_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])

    @property
    def playoff_box_scores_table_query(self):
        return '//table[@id="player_game_log_post"]'

    @property
    def playoff_box_scores_table(self):
        matching_tables = self.html.xpath(self.playoff_box_scores_table_query)

        if len(matching_tables) != 1:
            return None

        return PlayerSeasonBoxScoresTable(html=matching_tables[0])


class PlayerSeasonBoxScoresTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows_query(self):
        # Every 20 rows, there's a row that has the column header values - those should be ignored.
        # Game log tables also contain blank, classless separator rows (e.g. between playoff
        # series); every real game row (active or inactive) has a date, so require one.
        return (
            'tbody/tr[not(contains(@class, "spacer")) and not(contains(@class, "thead"))'
            ' and normalize-space(td[@data-stat="date"]) != ""]'
        )

    @property
    def rows(self):
        return [PlayerSeasonBoxScoresRow(html=row_html) for row_html in self.html.xpath(self.rows_query)]


class PlayerSeasonBoxScoresRow(PlayerSeasonGameLogRow):
    def __init__(self, html: HtmlElement) -> None:
        super().__init__(html)

    def __eq__(self, other):
        if isinstance(other, PlayerSeasonGameLogRow):
            return self.html == other.html
        return False

    @property
    def is_active(self):
        # When a player is not active (for a reason like "Inactive", "Did Not Play", "Did Not Dress")
        # "is_starter" column has a "colspan" attribute. When a player is active, the "is_starter" column does not
        # have a "colspan" attribute
        cells = self.html.xpath('td[@data-stat="is_starter"]')
        if len(cells) > 0:
            colspan_value = cells[0].get("colspan", None)
            return colspan_value is None

        return False

    @property
    def date(self):
        return cell_text(self.html, "date")

    @property
    def points_scored(self):
        return cell_text(self.html, "pts")


class PlayerGameBoxScoreRow(PlayerBoxScoreRow, PlayerIdentificationRow):
    def __init__(self, html: HtmlElement) -> None:
        super().__init__(html)


class DailyBoxScoresPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def game_url_paths_query(self):
        return '//td[contains(@class, "gamelink")]/a'

    @property
    def game_url_paths(self):
        game_links = self.html.xpath(self.game_url_paths_query)
        return [game_link.attrib["href"] for game_link in game_links]
