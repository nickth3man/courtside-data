from parsel import Selector

from basketball_reference_web_scraper.html import GenericTable, extract_commented_table
from basketball_reference_web_scraper.parser_service import ParserService
from tests.fixtures.rich_html import (
    RICH_AWARDS_TABLE,
    RICH_LINEUPS_TABLE,
    RICH_TEAM_ON_OFF_TABLE,
)


def _parse_table(table_html, table_id):
    selector = Selector(text=table_html)
    table_selector = selector.css(f'table#{table_id}')
    table = GenericTable(table_selector[0])
    return ParserService().parse_generic_table(table)


def test_parse_generic_table_coerces_award_tied_ranks():
    awards_html = RICH_AWARDS_TABLE.replace(
        '<td data-stat="award">Most Valuable Player</td>',
        '<td data-stat="rank">6T</td><td data-stat="award">Most Valuable Player</td>',
    ).replace(
        '<td data-stat="award">Rookie of the Year</td>',
        '<td data-stat="rank">10T</td><td data-stat="award">Rookie of the Year</td>',
    )

    rows = _parse_table(awards_html, 'mvp')

    assert rows[0]['rank'] == 6
    assert rows[1]['rank'] == 10


def test_parse_generic_table_coerces_lineup_minute_strings_to_seconds():
    lineups_html = RICH_LINEUPS_TABLE.replace(
        '<td data-stat="mp">420</td>',
        '<td data-stat="mp">113:42</td>',
    ).replace(
        '<td data-stat="fg_pct">.486</td>',
        '<td data-stat="diff_fg_pct">+.079</td>',
    )
    selector = Selector(text=f'<html><body>{lineups_html}</body></html>')
    table_selector = extract_commented_table(selector, 'lineups_5-man_')
    rows = ParserService().parse_generic_table(GenericTable(table_selector))

    assert rows[0]['mp'] == 6822
    assert rows[0]['diff_fg_pct'] == 0.079


def test_parse_generic_table_coerces_team_on_off_percentage_fields():
    on_off_html = RICH_TEAM_ON_OFF_TABLE.replace(
        '<td data-stat="mp">19780</td>',
        '<td data-stat="mp">68%</td>',
    ).replace(
        '<td data-stat="fg_pct">.493</td>',
        '<td data-stat="fg_pct">.493</td><td data-stat="diff_efg_pct">−.018</td>',
    ).replace(
        '<td data-stat="orb">890</td>',
        '<td data-stat="orb">890</td><td data-stat="orb_pct">19.9</td>',
    )

    rows = _parse_table(on_off_html, 'on_off')

    assert rows[0]['fg_pct'] == 0.493
    assert rows[0]['diff_efg_pct'] == -0.018
    assert rows[0]['orb_pct'] == 19.9
    assert rows[0]['mp'] == 68.0
