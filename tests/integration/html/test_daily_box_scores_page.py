from unittest import TestCase

from lxml import html

from courtside_data.legacy.html import DailyBoxScoresPage
from tests.integration.client import raw_fixtures


class TestDailyBoxScoresPage(TestCase):
    def setUp(self):
        self.january_01_2017_box_scores = raw_fixtures.team_box_scores_index(2017, 1, 1)

    def test_game_url_paths_query(self):
        page = DailyBoxScoresPage(html=html.fromstring(self.january_01_2017_box_scores))
        self.assertEqual(page.game_url_paths_query, '//td[contains(@class, "gamelink")]/a')

    def test_parse_urls(self):
        page = DailyBoxScoresPage(html=html.fromstring(self.january_01_2017_box_scores))
        urls = page.game_url_paths
        self.assertEqual(len(urls), 5)
        self.assertEqual(urls[0], "/boxscores/201701010ATL.html")
        self.assertEqual(urls[1], "/boxscores/201701010IND.html")
        self.assertEqual(urls[2], "/boxscores/201701010LAL.html")
        self.assertEqual(urls[3], "/boxscores/201701010MIA.html")
        self.assertEqual(urls[4], "/boxscores/201701010MIN.html")
