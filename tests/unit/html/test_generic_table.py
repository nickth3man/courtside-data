from unittest import TestCase

from parsel import Selector

from basketball_reference_web_scraper.html import GenericTable, GenericTableRow, extract_commented_table


SIMPLE_TABLE_HTML = """
<table id="per_game_stats">
  <thead>
    <tr>
      <th data-stat="player">Player</th>
      <th data-stat="g">G</th>
      <th data-stat="pts">PTS</th>
    </tr>
  </thead>
  <tbody>
    <tr class="thead">
      <th colspan="100">Some Header Row</th>
    </tr>
    <tr>
      <td data-stat="player">LeBron James</td>
      <td data-stat="g">70</td>
      <td data-stat="pts">25.4</td>
    </tr>
    <tr>
      <td data-stat="player">Anthony Davis</td>
      <td data-stat="g">60</td>
      <td data-stat="pts">24.7</td>
    </tr>
  </tbody>
</table>
"""

TABLE_WITH_EMPTY_ROW_HTML = """
<table id="mixed">
  <tbody>
    <tr class="thead">
      <th colspan="100">Header</th>
    </tr>
    <tr>
      <td data-stat="player">A Player</td>
      <td data-stat="pts">10</td>
    </tr>
    <tr>
      <td colspan="2">No data-stat cells here</td>
    </tr>
    <tr>
      <td data-stat="player">Another Player</td>
      <td data-stat="pts">15</td>
    </tr>
  </tbody>
</table>
"""

TABLE_WITH_LINK_HTML = """
<table id="with_links">
  <tbody>
    <tr>
      <td data-stat="player"><a href="/players/j/jamesle01.html" data-append-csv="jamesle01">LeBron James</a></td>
      <td data-stat="pts">25.4</td>
    </tr>
  </tbody>
</table>
"""

COMMENTED_TABLE_HTML = """
<html>
<body>
<div>
<!--table id="playoffs_totals" class="stats_table">
<table id="playoffs_totals">
  <tbody>
    <tr>
      <td data-stat="player">Playoff Player</td>
      <td data-stat="pts">30.0</td>
    </tr>
  </tbody>
</table>
-->
</div>
</body>
</html>
"""

COMMENTED_TABLE_SINGLE_QUOTE_HTML = """
<html>
<body>
<div>
<!--table id='per_poss' class="stats_table">
<table id="per_poss">
  <tbody>
    <tr>
      <td data-stat="player">Per Poss Player</td>
    </tr>
  </tbody>
</table>
-->
</div>
</body>
</html>
"""


class TestGenericTableRow(TestCase):
    def test_extracts_cells_by_data_stat(self):
        selector = Selector(text='<tr><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        self.assertEqual(row.get("pts"), "25.4")

    def test_extracts_multiple_cells(self):
        selector = Selector(text='<tr><td data-stat="player">LeBron</td><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        self.assertEqual(row.get("player"), "LeBron")
        self.assertEqual(row.get("pts"), "25.4")

    def test_missing_stat_returns_default(self):
        selector = Selector(text='<tr><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        self.assertEqual(row.get("missing_stat"), "")

    def test_missing_stat_returns_provided_default(self):
        selector = Selector(text='<tr><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        self.assertEqual(row.get("missing_stat", "N/A"), "N/A")

    def test_to_dict_returns_copy(self):
        selector = Selector(text='<tr><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        d = row.to_dict()
        self.assertEqual(d, {"pts": "25.4"})
        # Mutating the returned dict should not affect internal state
        d["pts"] = "changed"
        self.assertEqual(row.get("pts"), "25.4")

    def test_to_dict_includes_all_data_stat_keys(self):
        selector = Selector(text='<tr><td data-stat="g">70</td><td data-stat="pts">25.4</td></tr>')
        row = GenericTableRow(selector)
        d = row.to_dict()
        self.assertIn("g", d)
        self.assertIn("pts", d)
        self.assertEqual(len(d), 2)

    def test_cell_with_link_text(self):
        html = '<tr><td data-stat="player"><a href="/players/j/jamesle01.html">LeBron James</a></td></tr>'
        selector = Selector(text=html)
        row = GenericTableRow(selector)
        # text content of the cell includes the link text
        self.assertIn("LeBron James", row.get("player"))

    def test_strips_asterisks(self):
        selector = Selector(text='<tr><td data-stat="player">LeBron James*</td></tr>')
        row = GenericTableRow(selector)
        self.assertEqual(row.get("player"), "LeBron James")

    def test_exposes_cell_attributes_via_metadata(self):
        """For cells with data-append-csv, the raw attributes are exposed."""
        html = '<tr><td data-stat="player"><a href="/players/j/jamesle01.html" data-append-csv="jamesle01">LeBron James</a></td></tr>'
        selector = Selector(text=html)
        row = GenericTableRow(selector)
        metadata = row.metadata
        self.assertIn("player", metadata)
        self.assertEqual(metadata["player"]["data-append-csv"], "jamesle01")

    def test_metadata_empty_for_cells_without_attributes(self):
        html = '<tr><td data-stat="pts">25.4</td></tr>'
        selector = Selector(text=html)
        row = GenericTableRow(selector)
        metadata = row.metadata
        self.assertIn("pts", metadata)
        self.assertEqual(metadata["pts"], {})


class TestGenericTable(TestCase):
    def test_extracts_data_rows(self):
        selector = Selector(text=SIMPLE_TABLE_HTML)
        table_el = selector.css("table#per_game_stats")[0]
        table = GenericTable(table_el)
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].get("player"), "LeBron James")
        self.assertEqual(table.rows[0].get("pts"), "25.4")

    def test_skips_thead_rows(self):
        selector = Selector(text=SIMPLE_TABLE_HTML)
        table_el = selector.css("table#per_game_stats")[0]
        table = GenericTable(table_el)
        for row in table.rows:
            # No row should have "Some Header Row" as a player
            self.assertNotEqual(row.get("player"), "Some Header Row")

    def test_skips_rows_without_data_cells(self):
        selector = Selector(text=TABLE_WITH_EMPTY_ROW_HTML)
        table_el = selector.css("table#mixed")[0]
        table = GenericTable(table_el)
        # Should only have 2 rows with data-stat cells (the one without data-stat is skipped)
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.rows[0].get("player"), "A Player")
        self.assertEqual(table.rows[1].get("player"), "Another Player")

    def test_rows_property_is_list(self):
        selector = Selector(text=SIMPLE_TABLE_HTML)
        table_el = selector.css("table#per_game_stats")[0]
        table = GenericTable(table_el)
        self.assertIsInstance(table.rows, list)

    def test_table_with_no_data_rows(self):
        html = '<table id="empty"><tbody><tr class="thead"><th colspan="5">H</th></tr></tbody></table>'
        selector = Selector(text=html)
        table_el = selector.css("table#empty")[0]
        table = GenericTable(table_el)
        self.assertEqual(len(table.rows), 0)


class TestExtractCommentedTextBox(TestCase):
    def test_finds_commented_table_by_id(self):
        selector = Selector(text=COMMENTED_TABLE_HTML)
        result = extract_commented_table(selector, "playoffs_totals")
        self.assertIsNotNone(result)
        # The returned Selector should find the table
        rows = GenericTable(result)
        self.assertEqual(len(rows.rows), 1)
        self.assertEqual(rows.rows[0].get("player"), "Playoff Player")

    def test_returns_none_for_missing_table_id(self):
        selector = Selector(text=COMMENTED_TABLE_HTML)
        result = extract_commented_table(selector, "nonexistent_table")
        self.assertIsNone(result)

    def test_finds_table_with_single_quote_id(self):
        selector = Selector(text=COMMENTED_TABLE_SINGLE_QUOTE_HTML)
        result = extract_commented_table(selector, "per_poss")
        self.assertIsNotNone(result)
        rows = GenericTable(result)
        self.assertEqual(len(rows.rows), 1)
        self.assertEqual(rows.rows[0].get("player"), "Per Poss Player")

    def test_no_comments_returns_none(self):
        html = "<html><body><p>No comments here</p></body></html>"
        selector = Selector(text=html)
        result = extract_commented_table(selector, "anything")
        self.assertIsNone(result)
