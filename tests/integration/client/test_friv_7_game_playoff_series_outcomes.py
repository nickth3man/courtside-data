from unittest import mock

from courtside_data import client
from courtside_data.client import _runner
from courtside_data.http_service import HTTPService
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures

URL = "https://www.basketball-reference.com/friv/7-game-playoff-series-outcomes-22111.html"
PAGE_HTML = raw_fixtures.seven_game_playoff_series_outcomes_page()


def _mock_page(m):
    m.get(URL, text=PAGE_HTML, status_code=200)


class TestSevenGamePlayoffSeriesOutcomes:
    def test_team_is_down_table(self):
        with requests_mock.Mocker() as m:
            _mock_page(m)
            result = client.friv_7_game_playoff_series_outcomes_team_is_down(raw=True)

        assert len(result) == 46
        assert result[0] == {"record": "0-1", "gameslist": "All series", "wl": "115-349"}
        assert result[-1] == {"record": "2-3", "gameslist": "A A H H A / HA", "wl": "0-9"}

    def test_team_is_tied_table(self):
        with requests_mock.Mocker() as m:
            _mock_page(m)
            result = client.friv_7_game_playoff_series_outcomes_team_is_tied(raw=True)

        assert len(result) == 51
        assert result[0] == {"record": "1-1", "gameslist": "All series", "wl": "188-188"}
        assert result[-1] == {"record": "3-3", "gameslist": "A A H H A H / A", "wl": "2-2"}

    def test_team_is_up_table(self):
        with requests_mock.Mocker() as m:
            _mock_page(m)
            result = client.friv_7_game_playoff_series_outcomes_team_is_up(raw=True)

        assert len(result) == 46
        assert result[0] == {"record": "1-0", "gameslist": "All series", "wl": "349-115"}
        assert result[-1] == {"record": "3-2", "gameslist": "A A H H A / HA", "wl": "2-0"}

    def test_validated_rows_use_shared_model(self):
        with requests_mock.Mocker() as m:
            _mock_page(m)
            result = client.friv_7_game_playoff_series_outcomes_team_is_up()

        assert result[0].record == "1-0"
        assert result[0].gameslist == "All series"
        assert result[0].wl == "349-115"

    def test_shared_page_is_fetched_once_for_all_three_tables(self):
        # Use a fresh HTTPService so the selector cache starts empty and we can
        # verify that calling all three endpoints results in exactly one request.
        with mock.patch.object(_runner, "_shared_service", HTTPService()):
            with requests_mock.Mocker() as m:
                _mock_page(m)
                client.friv_7_game_playoff_series_outcomes_team_is_down(raw=True)
                client.friv_7_game_playoff_series_outcomes_team_is_tied(raw=True)
                client.friv_7_game_playoff_series_outcomes_team_is_up(raw=True)
                call_count = m.call_count

        assert call_count == 1
