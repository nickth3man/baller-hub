from unittest import TestCase

from src.core.domain import LOCATION_ABBREVIATIONS_TO_POSITION, Location
from src.scraper.parsers import LocationAbbreviationParser


class TestLocationAbbreviationParser(TestCase):
    def setUp(self):
        self.parser = LocationAbbreviationParser(
            abbreviations_to_locations=LOCATION_ABBREVIATIONS_TO_POSITION
        )

    def test_parse_away_symbol(self):
        assert self.parser.from_abbreviation("@") == Location.AWAY

    def test_parse_home_symbol(self):
        assert self.parser.from_abbreviation("") == Location.HOME

    def test_parse_unknown_location_symbol(self):
        self.assertRaises(ValueError, self.parser.from_abbreviation, "jaebaebae")  # noqa: PT027
