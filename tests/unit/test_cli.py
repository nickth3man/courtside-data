"""Registry-driven CLI behavior."""

from unittest import mock

import pytest

from courtside_data import cli
from courtside_data.data import OutputType, Team
from courtside_data.endpoints import ENDPOINTS


class TestParser:
    def test_every_endpoint_is_a_subcommand(self, capsys):
        parser = cli.build_parser()
        for name in ENDPOINTS:
            args = parser.parse_args([name, *_required_args(name)])
            assert args.endpoint == name

    def test_unknown_endpoint_exits(self):
        with pytest.raises(SystemExit):
            cli.build_parser().parse_args(["not_an_endpoint"])

    def test_team_value_accepts_separators(self):
        assert cli._team_value("boston_celtics") is Team.BOSTON_CELTICS
        assert cli._team_value("BOSTON CELTICS") is Team.BOSTON_CELTICS

    def test_team_value_rejects_unknown(self):
        with pytest.raises(cli.argparse.ArgumentTypeError):
            cli._team_value("SPRINGFIELD ATOMS")


class TestMain:
    def test_list_prints_every_endpoint(self, capsys):
        assert cli.main(["list"]) == 0
        out = capsys.readouterr().out
        for name in ENDPOINTS:
            assert name in out

    def test_endpoint_call_passes_params(self, capsys):
        with mock.patch.object(cli.client, "team_roster") as func:
            func.return_value = '[{"player": "X"}]'
            assert cli.main(["team_roster", "--team-abbreviation", "BOS", "--season-end-year", "2024"]) == 0
        func.assert_called_once_with(
            team_abbreviation="BOS",
            season_end_year=2024,
            output_type=OutputType.JSON,
            output_file_path=None,
            output_write_option=None,
        )
        assert '[{"player": "X"}]' in capsys.readouterr().out

    def test_csv_requires_output_file(self):
        with pytest.raises(SystemExit):
            cli.main(["league_per_game_stats", "--season-end-year", "2024", "--output-type", "csv"])


def _required_args(name):
    endpoint = ENDPOINTS[name]
    values = {
        "season_end_year": "2024",
        "day": "1",
        "month": "1",
        "year": "2024",
        "player_identifier": "jamesle01",
        "team_abbreviation": "BOS",
        "home_team": "BOSTON CELTICS",
        "term": "james",
    }
    args = []
    for param in endpoint.params:
        if param in cli._FLAG_PARAMS:
            continue
        args.extend(["--" + param.replace("_", "-"), values[param]])
    return args
