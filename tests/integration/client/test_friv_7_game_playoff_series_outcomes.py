from courtside_data import client
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures

URL = "https://www.basketball-reference.com/friv/7-game-playoff-series-outcomes-22111.html"


def _mock_page(m):
    m.get(
        URL,
        text=raw_fixtures.read("friv_7_game_playoff_series_outcomes/7-game-playoff-series-outcomes-22111.html"),
        status_code=200,
    )


class TestSevenGamePlayoffSeriesOutcomes:
    def test_team_is_down_table(self):
        with requests_mock.Mocker() as m:
            _mock_page(m)
            result = client.friv_7_game_playoff_series_outcomes(raw=True)

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
