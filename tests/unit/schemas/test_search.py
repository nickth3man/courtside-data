from __future__ import annotations

import pytest
from pydantic import ValidationError

from courtside_data.data import League
from courtside_data.schemas.search import SearchResultRow


class TestSearchResultRow:
    def test_happy_path(self):
        row = SearchResultRow.model_validate({"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": "NBA/ABA"})
        assert row.name == "Kobe Bryant"
        assert row.identifier == "bryanko01"
        assert row.leagues == {
            League.NATIONAL_BASKETBALL_ASSOCIATION,
            League.AMERICAN_BASKETBALL_ASSOCIATION,
        }

    def test_comma_and_space_separated_leagues(self):
        row = SearchResultRow.model_validate(
            {"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": "NBA, ABA, BAA"}
        )
        assert row.leagues == {
            League.NATIONAL_BASKETBALL_ASSOCIATION,
            League.AMERICAN_BASKETBALL_ASSOCIATION,
            League.BASKETBALL_ASSOCIATION_OF_AMERICA,
        }

    def test_empty_leagues_becomes_empty_set(self):
        row = SearchResultRow.model_validate({"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": ""})
        assert row.leagues == set()

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            SearchResultRow.model_validate({"identifier": "bryanko01", "leagues": "NBA"})

    def test_league_enum_collection_accepted(self):
        row = SearchResultRow.model_validate(
            {
                "name": "Kobe Bryant",
                "identifier": "bryanko01",
                "leagues": [League.NATIONAL_BASKETBALL_ASSOCIATION],
            }
        )
        assert row.leagues == {League.NATIONAL_BASKETBALL_ASSOCIATION}
