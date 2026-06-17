"""Player-contracts row class."""

from __future__ import annotations

from lxml.html import HtmlElement


class PlayerContractsRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def player_name(self):
        matching_cells = self.html.xpath('.//td[@data-stat="player"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    @property
    def player_identifier(self):
        matching_attribute_value = self.html.xpath(".//td/@data-append-csv")
        if len(matching_attribute_value) == 1:
            return matching_attribute_value[0]

        return None

    @property
    def team_abbreviation(self):
        matching_cells = self.html.xpath('.//td[@data-stat="team_id"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    @property
    def first_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y1")

    @property
    def second_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y2")

    @property
    def third_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y3")

    @property
    def fourth_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y4")

    @property
    def fifth_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y5")

    @property
    def sixth_contract_year_data(self):
        return self.get_contract_year_data(data_stat="y6")

    @property
    def guaranteed(self):
        matching_cells = self.html.xpath('.//td[@data-stat="remain_gtd"]')

        if len(matching_cells) == 1:
            return matching_cells[0].text_content()

        return None

    def get_contract_year_data(self, data_stat):
        matching_cells = self.html.xpath(f'.//td[@data-stat="{data_stat}"]')

        if len(matching_cells) == 1:
            salary = matching_cells[0].text_content()
            class_names = matching_cells[0].get("class")

            return salary, class_names

        return None
