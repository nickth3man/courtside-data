"""Player-contracts row class."""

from __future__ import annotations

from lxml.html import HtmlElement


class PlayerContractsRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def player_name(self):
        matching_cells = self.html.xpath('.//td[@data-stat="player"]')

        if 1 == len(matching_cells):
            return matching_cells[0].text_content()

        return None

    @property
    def player_identifier(self):
        matching_attribute_value = self.html.xpath(".//td/@data-append-csv")
        if 1 == len(matching_attribute_value):
            return matching_attribute_value[0]

        return None

    @property
    def team_abbreviation(self):
        matching_cells = self.html.xpath('.//td[@data-stat="team_id"]')

        if 1 == len(matching_cells):
            return matching_cells[0].text_content()

        return None

    @property
    def first_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y1")

    @property
    def second_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y2")

    @property
    def third_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y3")

    @property
    def fourth_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y4")

    @property
    def fifth_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y5")

    @property
    def sixth_contract_year_data(self):
        return self.calculate_contract_year_data(contract_year_data_stat_attribute_value="y6")

    @property
    def guaranteed(self):
        matching_cells = self.html.xpath('.//td[@data-stat="remain_gtd"]')

        if 1 == len(matching_cells):
            return matching_cells[0].text_content()

        return None

    def calculate_contract_year_data(self, contract_year_data_stat_attribute_value):
        matching_cells = self.html.xpath(f'.//td[@data-stat="{contract_year_data_stat_attribute_value}"]')

        if 1 == len(matching_cells):
            salary = matching_cells[0].text_content()
            class_names = matching_cells[0].get("class")

            return salary, class_names

        return None
