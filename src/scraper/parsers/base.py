"""Base classes for data parsers."""

PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT = "%Y-%m-%d"
PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX = "(?P<outcome_abbreviation>W|L),"
SEARCH_RESULT_NAME_REGEX = "(?P<name>^[^\\(]+)"


class TeamAbbreviationParser:
    """
    Converts 3-letter team codes (e.g., 'BOS') to Team enums.
    """

    def __init__(self, abbreviations_to_teams):
        self.abbreviations_to_teams = abbreviations_to_teams

    def from_abbreviation(self, abbreviation):
        """
        Look up Team enum by abbreviation.

        Args:
            abbreviation (str): e.g. "BOS", "LAL".

        Returns:
            Team | None: The Team enum or None if not found.
        """
        return self.abbreviations_to_teams.get(abbreviation)


class PositionAbbreviationParser:
    """
    Parses position codes (e.g., 'PG', 'SF') into Position enums.

    Can handle hyphenated multi-positions like 'SF-PF'.
    """

    def __init__(self, abbreviations_to_positions):
        self.abbreviations_to_positions = abbreviations_to_positions

    def from_abbreviation(self, abbreviation):
        """
        Parse a single position code.

        Args:
            abbreviation (str): e.g. "PG".

        Returns:
            Position | None: Position enum or None.
        """
        return self.abbreviations_to_positions.get(abbreviation)

    def from_abbreviations(self, abbreviations):
        """
        Parse hyphenated position string.

        Args:
            abbreviations (str): e.g. "SF-PF".

        Returns:
            list[Position]: List of Position enums found.
        """
        parsed_positions = [
            self.from_abbreviation(position_abbreviation)
            for position_abbreviation in abbreviations.split("-")
        ]
        return [position for position in parsed_positions if position is not None]


class LocationAbbreviationParser:
    """
    Parses game location indicators ('@' or empty string).
    """

    def __init__(self, abbreviations_to_locations):
        self.abbreviations_to_locations = abbreviations_to_locations

    def from_abbreviation(self, abbreviation):
        """
        Convert location symbol to Location enum.

        Args:
            abbreviation (str): "@" (Away) or "" (Home).

        Returns:
            Location: Location.HOME or Location.AWAY.

        Raises:
            ValueError: If symbol is unknown.
        """
        location = self.abbreviations_to_locations.get(abbreviation)
        if location is None:
            message = f"Unknown symbol: {location}"
            raise ValueError(message)

        return location


class OutcomeAbbreviationParser:
    """
    Parses outcome codes ('W' or 'L').
    """

    def __init__(self, abbreviations_to_outcomes):
        self.abbreviations_to_outcomes = abbreviations_to_outcomes

    def from_abbreviation(self, abbreviation):
        """
        Convert outcome symbol to Outcome enum.

        Args:
            abbreviation (str): "W" or "L".

        Returns:
            Outcome: Outcome.WIN or Outcome.LOSS.

        Raises:
            ValueError: If symbol is unknown.
        """
        outcome = self.abbreviations_to_outcomes.get(abbreviation)
        if outcome is None:
            message = f"Unknown symbol: {outcome}"
            raise ValueError(message)

        return outcome


class LeagueAbbreviationParser:
    """
    Parses league codes (e.g. 'NBA', 'ABA').
    """

    def __init__(self, abbreviations_to_league):
        self.abbreviations_to_league = abbreviations_to_league

    def from_abbreviation(self, abbreviation):
        """
        Convert league code to League enum.

        Args:
            abbreviation (str): e.g. "NBA".

        Returns:
            League: League enum.

        Raises:
            ValueError: If abbreviation is unknown.
        """
        league = self.abbreviations_to_league.get(abbreviation)
        if league is None:
            message = f"Unknown league abbreviation: {abbreviation}"
            raise ValueError(message)

        return league

    def from_abbreviations(self, abbreviations):
        """
        Parse slash-separated league string.

        Args:
            abbreviations (str): e.g. "NBA/ABA".

        Returns:
            list[League]: List of League enums.
        """
        if abbreviations is None:
            return []

        return [
            self.from_abbreviation(abbreviation=league_abbreviation)
            for league_abbreviation in abbreviations.split("/")
        ]
