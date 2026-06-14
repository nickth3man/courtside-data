from unittest import TestCase

from lxml import html

from courtside_data.legacy.html import PlayByPlayPage
from tests.integration.client import raw_fixtures


class TestPlayByPlayPage(TestCase):
    def setUp(self):
        self._1999_11_16_ATL_html = raw_fixtures.play_by_play_game("199911160ATL")

    def test_game_url_paths_query(self):
        page = PlayByPlayPage(html=html.fromstring(self._1999_11_16_ATL_html))
        rows = page.play_by_play_table.rows
        self.assertEqual(len(rows), 449)

        last_row = rows[448]
        self.assertEqual(last_row.timestamp, "0:01.0")
        self.assertEqual(last_row.away_team_play_description, "")
        self.assertFalse(last_row.is_away_team_play)
        self.assertTrue(last_row.is_home_team_play)
        self.assertEqual(last_row.home_team_play_description, "Defensive rebound by D. Mutombo")
        self.assertEqual(last_row.formatted_scores, "98-103")
