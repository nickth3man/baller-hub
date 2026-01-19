"""Parsers for standings data."""

from src.utils.casting import str_to_int


class TeamStandingsParser:
    """
    Parses a team name string into a Team enum.
    """

    def __init__(self, teams):
        self.teams = teams

    def parse_team(self, formatted_name):
        """
        Find Team enum that matches the start of the string.

        Args:
            formatted_name (str): e.g. "Boston Celtics (1)"

        Returns:
            Team | None: The matching Team enum.
        """
        for team in self.teams:
            if formatted_name.upper().startswith(team.value):
                return team

        return None


class DivisionNameParser:
    """
    Parses a division name string into a Division enum.
    """

    def __init__(self, divisions):
        self.divisions = divisions

    def parse_division(self, formatted_name):
        """
        Convert "Atlantic Division" string to Division.ATLANTIC.
        """
        for division in self.divisions:
            if formatted_name.upper() == f"{division.value} DIVISION":
                return division

        return None


class ConferenceDivisionStandingsParser:
    """
    Parses full conference standings tables.

    Handles grouping teams by division as they appear in the table rows.
    """

    def __init__(
        self, division_name_parser, team_standings_parser, divisions_to_conferences
    ):
        self.division_name_parser = division_name_parser
        self.team_standings_parser = team_standings_parser
        self.divisions_to_conferences = divisions_to_conferences

    def parse(self, division_standings):
        """
        Parse table rows into structured standings data.

        Args:
            division_standings (list[ConferenceDivisionStandingsRow]): Table rows.

        Returns:
            list[dict]: List of team standings dicts.
        """
        current_division = None
        results = []
        for standing in division_standings:
            if standing.is_division_name_row:
                current_division = self.division_name_parser.parse_division(
                    formatted_name=standing.division_name
                )
            else:
                results.append(
                    {
                        "team": self.team_standings_parser.parse_team(
                            formatted_name=standing.team_name
                        ),
                        "wins": str_to_int(standing.wins),
                        "losses": str_to_int(standing.losses),
                        "division": current_division,
                        "conference": self.divisions_to_conferences.get(
                            current_division
                        ),
                    }
                )
        return results
