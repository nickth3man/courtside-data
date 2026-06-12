"""Season-schedule page and row classes."""

from __future__ import annotations

from lxml.html import HtmlElement

from courtside_data.legacy.html._helpers import cell_text, th_text


class SchedulePage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def other_months_schedule_links_query(self):
        return '//div[@id="content"]/div[@class="filter"]/div[not(contains(@class, "current"))]/a'

    @property
    def rows_query(self):
        return '//table[@id="schedule"]//tbody/tr'

    @property
    def other_months_schedule_urls(self):
        links = self.html.xpath(self.other_months_schedule_links_query)
        return [link.attrib["href"] for link in links]

    @property
    def rows(self):
        return [
            ScheduleRow(html=row)
            for row in self.html.xpath(self.rows_query)
            # Every row in each month's schedule table represents a game
            # except for the row where the only content is "Playoffs"
            if row.text_content() != "Playoffs"
        ]


class ScheduleRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    def __eq__(self, other):
        if isinstance(other, ScheduleRow):
            return self.html == other.html
        return False

    @property
    def start_date(self):
        return th_text(self.html, "date_game")

    @property
    def start_time_of_day(self):
        return cell_text(self.html, "game_start_time")

    @property
    def away_team_name(self):
        return cell_text(self.html, "visitor_team_name")

    @property
    def home_team_name(self):
        return cell_text(self.html, "home_team_name")

    @property
    def away_team_score(self):
        return cell_text(self.html, "visitor_pts")

    @property
    def home_team_score(self):
        return cell_text(self.html, "home_pts")
