"""Parsers for search results."""

import re

from src.scraper.parsers.base import SEARCH_RESULT_NAME_REGEX


class SearchResultNameParser:
    """
    Parses the player/team name from the search result string.
    """

    def __init__(
        self,
        search_result_name_regex=SEARCH_RESULT_NAME_REGEX,
        result_name_regex_group_name="name",
    ):
        self.search_result_name_regex = search_result_name_regex
        self.result_name_regex_group_name = result_name_regex_group_name

    def parse(self, search_result_name):
        """
        Extract clean name from formatted string.

        Args:
            search_result_name (str): e.g. "LeBron James (LAL)"

        Returns:
            str: "LeBron James"
        """
        match = re.search(self.search_result_name_regex, search_result_name)
        if match is None:
            message = f"Could not parse search result name: {search_result_name}"
            raise ValueError(message)
        return match.group(self.result_name_regex_group_name).strip()


class ResourceLocationParser:
    """
    Parses the URL path to extract resource type and ID.
    """

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
        """Perform regex search on URL."""
        return re.search(self.resource_location_regex, resource_location)

    def parse_resource_type(self, resource_location):
        """
        Extract type from URL (e.g. 'players').
        """
        return self.search(resource_location=resource_location).group(
            self.resource_type_regex_group_name
        )

    def parse_resource_identifier(self, resource_location):
        """
        Extract unique ID from URL (e.g. 'jamesle01').
        """
        return self.search(resource_location=resource_location).group(
            self.resource_identifier_regex_group_name
        )


class SearchResultsParser:
    """
    Parses lists of search results into structured dictionaries.
    """

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
        """
        Parse raw search result rows.

        Args:
            nba_aba_baa_players (list[PlayerSearchResult]): Raw DOM wrappers.

        Returns:
            dict: { "players": [ ... ] }
        """
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
    """
    Parses a player's profile page data.
    """

    def __init__(self, search_result_location_parser, league_abbreviation_parser):
        self.search_result_location_parser = search_result_location_parser
        self.league_abbreviation_parser = league_abbreviation_parser

    def parse(self, player):
        """
        Parse player object into dict.
        """
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
