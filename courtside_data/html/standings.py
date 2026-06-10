"""Division/conference standings page and row classes."""

from __future__ import annotations

from lxml.html import HtmlElement


class StandingsPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def division_standings(self):
        division_standings = self.html.xpath('.//div[@id="all_standings"]')

        if len(division_standings) == 1:
            return DivisionStandings(html=division_standings[0])

        return None


class DivisionStandings:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def eastern_conference_table(self):
        tables = self.html.xpath('.//table[@id="divs_standings_E"]')

        if len(tables) == 1:
            return ConferenceDivisionStandingsTable(html=tables[0])

        return None

    @property
    def western_conference_table(self):
        tables = self.html.xpath('.//table[@id="divs_standings_W"]')

        if len(tables) == 1:
            return ConferenceDivisionStandingsTable(html=tables[0])

        return None


class ConferenceDivisionStandingsTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows(self):
        return [ConferenceDivisionStandingsRow(html=row_html) for row_html in self.html.xpath(".//tbody/tr")]


class ConferenceDivisionStandingsRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def is_division_name_row(self):
        return self.html.attrib["class"] == "thead"

    @property
    def is_standings_row(self):
        return self.html.attrib["class"] == "full_table"

    @property
    def division_name(self):
        cells = self.html.xpath(".//th")

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def team_name(self):
        cells = self.html.xpath('.//th[@data-stat="team_name"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def wins(self):
        cells = self.html.xpath('.//td[@data-stat="wins"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None

    @property
    def losses(self):
        cells = self.html.xpath('.//td[@data-stat="losses"]')

        if len(cells) == 1:
            return cells[0].text_content()

        return None
