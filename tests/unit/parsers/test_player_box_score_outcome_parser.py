from unittest import TestCase

from courtside_data.data import OUTCOME_ABBREVIATIONS_TO_OUTCOME
from courtside_data.legacy.parsers import OutcomeAbbreviationParser, PlayerBoxScoreOutcomeParser


class TestPlayerBoxScoreOutcomeParser(TestCase):
    def setUp(self):
        self.parser = PlayerBoxScoreOutcomeParser(
            outcome_abbreviation_parser=OutcomeAbbreviationParser(
                abbreviations_to_outcomes=OUTCOME_ABBREVIATIONS_TO_OUTCOME
            )
        )

    def test_parse_win_abbreviation_for_single_digit_margin_of_victory(self):
        self.assertEqual("W", self.parser.parse_outcome_abbreviation(formatted_outcome="W, (1, 0)"))
