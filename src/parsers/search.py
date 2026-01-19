import re

from src.parsers.base import SEARCH_RESULT_NAME_REGEX


class SearchResultNameParser:
    def __init__(
        self,
        search_result_name_regex=SEARCH_RESULT_NAME_REGEX,
        result_name_regex_group_name="name",
    ):
        self.search_result_name_regex = search_result_name_regex
        self.result_name_regex_group_name = result_name_regex_group_name

    def parse(self, search_result_name):
        return (
            re.search(self.search_result_name_regex, search_result_name)
            .group(self.result_name_regex_group_name)
            .strip()
        )


class ResourceLocationParser:
    def __init__(
        self,
        resource_location_regex,
        resource_type_regex_group_name="resource_type",
        resource_identifier_regex_group_name="resource_identifier",
    ):
        self.resource_location_regex = resource_location_regex
        self.resource_type_regex_group_name = resource_type_regex_group_name
        self.resource_identifier_regex_group_name = resource_identifier_regex_group_name

    def search(self, resource_location):
        return re.search(self.resource_location_regex, resource_location)

    def parse_resource_type(self, resource_location):
        return self.search(resource_location=resource_location).group(
            self.resource_type_regex_group_name
        )

    def parse_resource_identifier(self, resource_location):
        return self.search(resource_location=resource_location).group(
            self.resource_identifier_regex_group_name
        )


class SearchResultsParser:
    def __init__(
        self,
        search_result_name_parser,
        search_result_location_parser,
        league_abbreviation_parser,
    ):
        self.search_result_name_parser = search_result_name_parser
        self.search_result_location_parser = search_result_location_parser
        self.league_abbreviation_parser = league_abbreviation_parser

    def parse(self, nba_aba_baa_players):
        return {
            "players": [
                {
                    "name": self.search_result_name_parser.parse(
                        search_result_name=result.resource_name
                    ),
                    "identifier": self.search_result_location_parser.parse_resource_identifier(
                        resource_location=result.resource_location
                    ),
                    "leagues": set(
                        self.league_abbreviation_parser.from_abbreviations(
                            abbreviations=result.league_abbreviations
                        )
                    ),
                }
                for result in nba_aba_baa_players
            ]
        }


class PlayerDataParser:
    def __init__(self, search_result_location_parser, league_abbreviation_parser):
        self.search_result_location_parser = search_result_location_parser
        self.league_abbreviation_parser = league_abbreviation_parser

    def parse(self, player):
        return {
            "name": player.name,
            "identifier": self.search_result_location_parser.parse_resource_identifier(
                resource_location=player.resource_location
            ),
            "leagues": {
                self.league_abbreviation_parser.from_abbreviation(
                    abbreviation=abbreviation
                )
                for abbreviation in player.league_abbreviations
            },
        }
