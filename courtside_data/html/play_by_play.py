"""Play-by-play page, table, and row classes."""

from __future__ import annotations

from lxml.html import HtmlElement


class PlayByPlayPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def table_query(self):
        return '//table[@id="pbp"]'

    @property
    def team_names_query(self):
        return '//*[@id="content"]//div[@class="scorebox"]//strong//a'

    @property
    def play_by_play_table(self):
        return PlayByPlayTable(html=self.html.xpath(self.table_query)[0])

    @property
    def team_names(self):
        names = self.html.xpath(self.team_names_query)

        return [name.text_content() for name in names]

    @property
    def away_team_name(self):
        return self.team_names[0]

    @property
    def home_team_name(self):
        return self.team_names[1]


class PlayByPlayTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows(self):
        return [
            PlayByPlayRow(html=row_html)
            # Ignore first row in table
            for row_html in self.html[1:]
        ]


class PlayByPlayRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def timestamp_cell(self):
        return self.html[0]

    @property
    def timestamp(self):
        return self.timestamp_cell.text_content().strip()

    @property
    def away_team_play_description(self):
        if 6 == len(self.html):
            return self.html[1].text_content().strip()

        return ""

    @property
    def home_team_play_description(self):
        if 6 == len(self.html):
            return self.html[5].text_content().strip()

        return ""

    @property
    def is_away_team_play(self):
        return self.away_team_play_description != ""

    @property
    def is_home_team_play(self):
        return self.home_team_play_description != ""

    @property
    def formatted_scores(self):
        if 6 == len(self.html):
            return self.html[3].text_content().strip()
        return ""

    @property
    def is_start_of_period(self):
        return self.timestamp_cell.get("colspan") == "6"

    @property
    def has_play_by_play_data(self):
        # TODO: @jaebradley refactor this to be slightly clearer
        # Need to avoid rows that indicate start of period
        # Or denote tipoff / end of period (colspan = 5)
        # Or are one of the table headers for each period group (aria-label = Time)
        # There are certain cases, like at the 10 minute mark in https://www.basketball-reference.com/boxscores/pbp/199911160ATL.html
        # where there are no event details. Probably a visual bug on Basketball Reference's side of things.
        return (
            not self.is_start_of_period
            and 2 <= len(self.html)
            and self.html[1].get("colspan") != "5"
            and self.timestamp_cell.get("aria-label") != "Time"
        )
