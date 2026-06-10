"""Search results and player-page classes used by the search endpoint."""

from __future__ import annotations

from lxml.html import HtmlElement


class SearchPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def nba_aba_baa_players_content_query(self):
        return '//div[@id="searches"]/div[@id="players"]'

    @property
    def nba_aba_baa_players_pagination_links_query(self):
        return f'{self.nba_aba_baa_players_content_query}/div[@class="search-pagination"]/a'

    @property
    def nba_aba_baa_player_search_items_query(self):
        return f'{self.nba_aba_baa_players_content_query}/div[@class="search-item"]'

    @property
    def nba_aba_baa_players_pagination_links(self):
        return self.html.xpath(self.nba_aba_baa_players_pagination_links_query)

    @property
    def nba_aba_baa_players_pagination_url(self):
        links = self.nba_aba_baa_players_pagination_links

        if len(links) <= 0:
            return None

        first_link = links[0]

        if len(links) == 1:
            if first_link.text_content() == "Previous 100 Results":
                return None

            return first_link.attrib["href"]

        return links[1].attrib["href"]

    @property
    def nba_aba_baa_players(self):
        return [
            PlayerSearchResult(html=result_html)
            for result_html in self.html.xpath(self.nba_aba_baa_player_search_items_query)
        ]


class SearchResult:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def resource_link_query(self):
        return './div[@class="search-item-name"]//a'

    @property
    def resource_link(self):
        links = self.html.xpath(self.resource_link_query)

        if len(links) > 0:
            return links[0]

        return None

    @property
    def resource_location(self):
        link = self.resource_link

        if link is None:
            return None

        return link.attrib["href"]

    @property
    def resource_name(self):
        link = self.resource_link

        if link is None:
            return None

        return link.text_content()

    def __eq__(self, other):
        if isinstance(other, SearchResult):
            return self.html == other.html
        return False


class PlayerSearchResult(SearchResult):
    @property
    def league_abbreviation_query(self):
        return './div[@class="search-item-league"]'

    @property
    def league_abbreviations(self):
        abbreviations = self.html.xpath(self.league_abbreviation_query)

        if len(abbreviations) > 0:
            return abbreviations[0].text_content()

        return None


class PlayerPageTotalsRow:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def league_abbreviation(self):
        league_abbreviation_cells = self.html.xpath('.//td[@data-stat="lg_id"]')

        if len(league_abbreviation_cells) > 0:
            return league_abbreviation_cells[0].text_content()

        return None

    def __eq__(self, other):
        if isinstance(other, PlayerPageTotalsRow):
            return self.html == other.html
        return False


class PlayerPageTotalsTable:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def rows(self):
        return [PlayerPageTotalsRow(html=row_html) for row_html in self.html.xpath(".//tbody/tr")]

    def __eq__(self, other):
        if isinstance(other, PlayerPageTotalsTable):
            return self.html == other.html
        return False


class PlayerPage:
    def __init__(self, html: HtmlElement) -> None:
        self.html = html

    @property
    def name(self):
        name_headers = self.html.xpath('.//h1[@itemprop="name"]')

        if len(name_headers) > 0:
            return name_headers[0].text_content().strip()

        return None

    @property
    def totals_table(self):
        totals_tables = self.html.xpath('.//table[@id="per_game"]')

        if len(totals_tables) > 0:
            return PlayerPageTotalsTable(html=totals_tables[0])

        return None
