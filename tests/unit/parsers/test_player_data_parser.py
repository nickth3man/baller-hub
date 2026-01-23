from unittest import TestCase

from src.core.domain import LEAGUE_ABBREVIATIONS_TO_LEAGUE, League, PlayerData
from src.scraper.parsers import (
    LeagueAbbreviationParser,
    PlayerDataParser,
    ResourceLocationParser,
)
from src.scraper.services.parsing import ParserService


class TestPlayerDataParser(TestCase):
    def setUp(self):
        self.parser = PlayerDataParser(
            search_result_location_parser=ResourceLocationParser(
                resource_location_regex=ParserService.SEARCH_RESULT_RESOURCE_LOCATION_REGEX,
            ),
            league_abbreviation_parser=LeagueAbbreviationParser(
                abbreviations_to_league=LEAGUE_ABBREVIATIONS_TO_LEAGUE
            ),
        )

    def test_parse_name(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=[],
            )
        )
        assert parsed_player["name"] == "jaebaebae"

    def test_parse_resource_location(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=[],
            )
        )
        assert parsed_player["identifier"] == "bryanko01"

    def test_parse_league_abbreviations_for_single_nba_abbreviation(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["NBA"],
            )
        )
        assert parsed_player["leagues"] == {League.NATIONAL_BASKETBALL_ASSOCIATION}

    def test_parse_league_abbreviations_for_single_aba_abbreviation(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["ABA"],
            )
        )
        assert parsed_player["leagues"] == {League.AMERICAN_BASKETBALL_ASSOCIATION}

    def test_parse_league_abbreviations_for_single_baa_abbreviation(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["BAA"],
            )
        )
        assert parsed_player["leagues"] == {League.BASKETBALL_ASSOCIATION_OF_AMERICA}

    def test_parse_league_abbreviations_for_multiple_nba_abbreviations(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["NBA", "NBA"],
            )
        )
        assert parsed_player["leagues"] == {League.NATIONAL_BASKETBALL_ASSOCIATION}

    def test_parse_league_abbreviations_for_multiple_aba_abbreviations(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["ABA", "ABA"],
            )
        )
        assert parsed_player["leagues"] == {League.AMERICAN_BASKETBALL_ASSOCIATION}

    def test_parse_league_abbreviations_for_multiple_baa_abbreviations(self):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["BAA", "BAA"],
            )
        )
        assert parsed_player["leagues"] == {League.BASKETBALL_ASSOCIATION_OF_AMERICA}

    def test_parse_league_abbreviations_for_multiple_nba_and_aba_and_baa_abbreviations(
        self,
    ):
        parsed_player = self.parser.parse(
            player=PlayerData(
                name="jaebaebae",
                resource_location="/players/b/bryanko01.html",
                league_abbreviations=["NBA", "ABA", "BAA", "NBA", "ABA", "BAA"],
            )
        )
        assert parsed_player["leagues"] == {
            League.NATIONAL_BASKETBALL_ASSOCIATION,
            League.AMERICAN_BASKETBALL_ASSOCIATION,
            League.BASKETBALL_ASSOCIATION_OF_AMERICA,
        }
