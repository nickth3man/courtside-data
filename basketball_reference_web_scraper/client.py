import requests

from basketball_reference_web_scraper.errors import InvalidSeason, InvalidDate, InvalidPlayer, InvalidPlayerAndSeason, InvalidSearch, InvalidTeam
from basketball_reference_web_scraper.http_service import HTTPService
from basketball_reference_web_scraper.output.columns import BOX_SCORE_COLUMN_NAMES, SCHEDULE_COLUMN_NAMES, \
    PLAYER_SEASON_TOTALS_COLUMN_NAMES, \
    PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES, TEAM_BOX_SCORES_COLUMN_NAMES, PLAY_BY_PLAY_COLUMN_NAMES, \
    PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES, SEARCH_RESULTS_COLUMN_NAMES, STANDINGS_COLUMNS_NAMES, \
    LEAGUE_PER_GAME_COLUMN_NAMES, LEAGUE_PER_36_COLUMN_NAMES, LEAGUE_TOTALS_COLUMN_NAMES, \
    ROOKIE_STATS_COLUMN_NAMES, STANDINGS_BY_DATE_COLUMN_NAMES, ATTENDANCE_COLUMN_NAMES, \
    LEAGUE_TRANSACTIONS_COLUMN_NAMES, \
    LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES, LEAGUE_SHOOTING_COLUMN_NAMES, \
    PLAYOFF_PER_GAME_COLUMN_NAMES, PLAYOFF_TOTALS_COLUMN_NAMES, \
    DRAFT_PICKS_COLUMN_NAMES, SEASON_LEADERS_COLUMN_NAMES, CAREER_LEADERS_COLUMN_NAMES, \
    PLAYOFF_BRACKET_COLUMN_NAMES, SEASON_AWARDS_COLUMN_NAMES, \
    PLAYER_CAREER_STATS_COLUMN_NAMES, PLAYER_PLAYOFF_SERIES_COLUMN_NAMES, \
    PLAYER_SPLITS_COLUMN_NAMES, PLAYER_ON_OFF_COLUMN_NAMES, PLAYER_SHOT_CHARTS_COLUMN_NAMES, \
    PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES, PLAYER_PLAY_BY_PLAY_COLUMN_NAMES, \
    PLAYER_GAME_HIGHS_COLUMN_NAMES, PLAYER_ALL_STAR_COLUMN_NAMES, \
    PLAYER_SIMILARITY_SCORES_COLUMN_NAMES, PLAYER_SALARIES_COLUMN_NAMES, \
    TEAM_ROSTER_COLUMN_NAMES, TEAM_INJURY_REPORT_COLUMN_NAMES, \
    TEAM_AND_OPPONENT_COLUMN_NAMES, TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES, \
    TEAM_SCHEDULE_COLUMN_NAMES, TEAM_TRANSACTIONS_COLUMN_NAMES, \
    TEAM_SPLITS_COLUMN_NAMES, TEAM_CONTRACTS_COLUMN_NAMES, \
    TEAM_LINEUPS_COLUMN_NAMES, TEAM_STARTING_LINEUPS_COLUMN_NAMES, \
    TEAM_ON_OFF_COLUMN_NAMES, TEAM_OPPONENT_STATS_COLUMN_NAMES, \
    FRANCHISE_HISTORY_COLUMN_NAMES
from basketball_reference_web_scraper.output.fields import format_value, BasketballReferenceJSONEncoder
from basketball_reference_web_scraper.output.service import OutputService
from basketball_reference_web_scraper.output.writers import CSVWriter, JSONWriter, FileOptions, OutputOptions, \
    SearchCSVWriter
from basketball_reference_web_scraper.parser_service import ParserService


def standings(season_end_year, output_type=None, output_file_path=None, output_write_option=None,
              json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.standings(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": STANDINGS_COLUMNS_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_box_scores(day, month, year, output_type=None, output_file_path=None, output_write_option=None,
                      json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_box_scores(day=day, month=month, year=year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidDate(day=day, month=month, year=year)
        else:
            raise http_error

    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": BOX_SCORE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def regular_season_player_box_scores(player_identifier, season_end_year, output_type=None, output_file_path=None,
                                     output_write_option=None, json_options=None, include_inactive_games=False):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.regular_season_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.internal_server_error \
                or http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def playoff_player_box_scores(player_identifier, season_end_year, output_type=None, output_file_path=None,
                              output_write_option=None, json_options=None, include_inactive_games=False):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.playoff_player_box_scores(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
            include_inactive_games=include_inactive_games,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.internal_server_error \
                or http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayerAndSeason(player_identifier=player_identifier, season_end_year=season_end_year)
        else:
            raise http_error

    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_BOX_SCORE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def season_schedule(season_end_year, output_type=None, output_file_path=None, output_write_option=None,
                    json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.season_schedule(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        # https://github.com/requests/requests/blob/master/requests/status_codes.py#L58
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SCHEDULE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def players_season_totals(season_end_year, output_type=None, output_file_path=None, output_write_option=None,
                          json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.players_season_totals(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SEASON_TOTALS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def players_advanced_season_totals(season_end_year, include_combined_values=False, output_type=None,
                                   output_file_path=None, output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.players_advanced_season_totals(
            season_end_year,
            include_combined_values=include_combined_values
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_ADVANCED_SEASON_TOTALS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_box_scores(day, month, year, output_type=None, output_file_path=None, output_write_option=None,
                    json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_box_scores(day=day, month=month, year=year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidDate(day=day, month=month, year=year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_BOX_SCORES_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def play_by_play(home_team, day, month, year, output_type=None, output_file_path=None, output_write_option=None,
                 json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.play_by_play(home_team=home_team, day=day, month=month, year=year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidDate(day=day, month=month, year=year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAY_BY_PLAY_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def search(term, output_type=None, output_file_path=None, output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.search(term=term)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSearch(term=term)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SEARCH_RESULTS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_roster(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_roster(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_ROSTER_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_injury_report(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                       output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_injury_report(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_INJURY_REPORT_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_and_opponent(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                      output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_and_opponent(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_AND_OPPONENT_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_misc_four_factors(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                           output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_misc_four_factors(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_MISC_FOUR_FACTORS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_per_game_stats(season_end_year, output_type=None, output_file_path=None,
                          output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_per_game_stats(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_PER_GAME_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_per_36_minutes(season_end_year, output_type=None, output_file_path=None,
                          output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_per_36_minutes(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_PER_36_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_totals(season_end_year, output_type=None, output_file_path=None,
                  output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_totals(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_TOTALS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def rookie_stats(season_end_year, output_type=None, output_file_path=None,
                 output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.rookie_stats(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": ROOKIE_STATS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def standings_by_date(season_end_year, output_type=None, output_file_path=None,
                      output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.standings_by_date(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": STANDINGS_BY_DATE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def attendance(season_end_year, output_type=None, output_file_path=None,
               output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.attendance(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": ATTENDANCE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_transactions(season_end_year, output_type=None, output_file_path=None,
                        output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_transactions(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_TRANSACTIONS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_per_100_possessions(season_end_year, output_type=None, output_file_path=None,
                               output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_per_100_possessions(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_PER_100_POSSESSIONS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def league_shooting(season_end_year, output_type=None, output_file_path=None,
                    output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.league_shooting(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": LEAGUE_SHOOTING_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def playoff_per_game(season_end_year, output_type=None, output_file_path=None,
                     output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.playoff_per_game(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYOFF_PER_GAME_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def playoff_totals(season_end_year, output_type=None, output_file_path=None,
                   output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.playoff_totals(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYOFF_TOTALS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def draft_picks(season_end_year, output_type=None, output_file_path=None,
                output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.draft_picks(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": DRAFT_PICKS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def season_leaders(output_type=None, output_file_path=None,
                   output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.season_leaders()
    except requests.exceptions.HTTPError as http_error:
        raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SEASON_LEADERS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def career_leaders(output_type=None, output_file_path=None,
                   output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.career_leaders()
    except requests.exceptions.HTTPError as http_error:
        raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": CAREER_LEADERS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def playoff_bracket(season_end_year, output_type=None, output_file_path=None,
                    output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.playoff_bracket(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYOFF_BRACKET_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def season_awards(season_end_year, output_type=None, output_file_path=None,
                  output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.season_awards(season_end_year=season_end_year)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidSeason(season_end_year=season_end_year)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": SEASON_AWARDS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_career_stats(player_identifier, output_type=None, output_file_path=None,
                        output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_career_stats(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_CAREER_STATS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_playoff_series(player_identifier, output_type=None, output_file_path=None,
                          output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_playoff_series(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_PLAYOFF_SERIES_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_splits(player_identifier, season_end_year, output_type=None, output_file_path=None,
                  output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_splits(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SPLITS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_on_off(player_identifier, season_end_year, output_type=None, output_file_path=None,
                  output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_on_off(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_ON_OFF_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_shot_charts(player_identifier, season_end_year, output_type=None, output_file_path=None,
                       output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_shot_charts(
            player_identifier=player_identifier,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SHOT_CHARTS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_adjusted_shooting(player_identifier, output_type=None, output_file_path=None,
                             output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_adjusted_shooting(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_ADJUSTED_SHOOTING_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_play_by_play(player_identifier, output_type=None, output_file_path=None,
                        output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_play_by_play(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_PLAY_BY_PLAY_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_game_highs(player_identifier, output_type=None, output_file_path=None,
                      output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_game_highs(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_GAME_HIGHS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_all_star(player_identifier, output_type=None, output_file_path=None,
                    output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_all_star(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_ALL_STAR_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_similarity_scores(player_identifier, output_type=None, output_file_path=None,
                             output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_similarity_scores(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SIMILARITY_SCORES_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def player_salaries(player_identifier, output_type=None, output_file_path=None,
                    output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.player_salaries(player_identifier=player_identifier)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidPlayer(player_identifier=player_identifier)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": PLAYER_SALARIES_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_schedule(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                  output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_schedule(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_SCHEDULE_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_transactions(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                      output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_transactions(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_TRANSACTIONS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_splits(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_splits(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_SPLITS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_contracts(team_abbreviation, output_type=None, output_file_path=None,
                   output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_contracts(
            team_abbreviation=team_abbreviation,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_CONTRACTS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_lineups(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                 output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_lineups(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_LINEUPS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_starting_lineups(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                          output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_starting_lineups(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_STARTING_LINEUPS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_on_off(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_on_off(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_ON_OFF_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def team_opponent_stats(team_abbreviation, season_end_year, output_type=None, output_file_path=None,
                        output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.team_opponent_stats(
            team_abbreviation=team_abbreviation,
            season_end_year=season_end_year,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": TEAM_OPPONENT_STATS_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)


def franchise_history(team_abbreviation, output_type=None, output_file_path=None,
                      output_write_option=None, json_options=None):
    try:
        http_service = HTTPService(parser=ParserService())
        values = http_service.franchise_history(
            team_abbreviation=team_abbreviation,
        )
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == requests.codes.not_found:
            raise InvalidTeam(team_abbreviation=team_abbreviation)
        else:
            raise http_error
    options = OutputOptions.of(
        file_options=FileOptions.of(path=output_file_path, mode=output_write_option),
        output_type=output_type,
        json_options=json_options,
        csv_options={"column_names": FRANCHISE_HISTORY_COLUMN_NAMES}
    )
    output_service = OutputService(
        json_writer=JSONWriter(value_formatter=BasketballReferenceJSONEncoder),
        csv_writer=CSVWriter(value_formatter=format_value)
    )
    return output_service.output(data=values, options=options)
