PLAYER_SEASON_BOX_SCORES_GAME_DATE_FORMAT = "%Y-%m-%d"
PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX = "(?P<outcome_abbreviation>W|L),"
SEARCH_RESULT_NAME_REGEX = "(?P<name>^[^\\(]+)"


class TeamAbbreviationParser:
    def __init__(self, abbreviations_to_teams):
        self.abbreviations_to_teams = abbreviations_to_teams

    def from_abbreviation(self, abbreviation):
        return self.abbreviations_to_teams.get(abbreviation)


class PositionAbbreviationParser:
    def __init__(self, abbreviations_to_positions):
        self.abbreviations_to_positions = abbreviations_to_positions

    def from_abbreviation(self, abbreviation):
        return self.abbreviations_to_positions.get(abbreviation)

    def from_abbreviations(self, abbreviations):
        parsed_positions = [
            self.from_abbreviation(position_abbreviation)
            for position_abbreviation in abbreviations.split("-")
        ]
        return [position for position in parsed_positions if position is not None]


class LocationAbbreviationParser:
    def __init__(self, abbreviations_to_locations):
        self.abbreviations_to_locations = abbreviations_to_locations

    def from_abbreviation(self, abbreviation):
        location = self.abbreviations_to_locations.get(abbreviation)
        if location is None:
            raise ValueError(f"Unknown symbol: {location}")

        return location


class OutcomeAbbreviationParser:
    def __init__(self, abbreviations_to_outcomes):
        self.abbreviations_to_outcomes = abbreviations_to_outcomes

    def from_abbreviation(self, abbreviation):
        outcome = self.abbreviations_to_outcomes.get(abbreviation)
        if outcome is None:
            raise ValueError(f"Unknown symbol: {outcome}")

        return outcome


class LeagueAbbreviationParser:
    def __init__(self, abbreviations_to_league):
        self.abbreviations_to_league = abbreviations_to_league

    def from_abbreviation(self, abbreviation):
        league = self.abbreviations_to_league.get(abbreviation)
        if league is None:
            raise ValueError(f"Unknown league abbreviation: {abbreviation}")

        return league

    def from_abbreviations(self, abbreviations):
        if abbreviations is None:
            return []

        return [
            self.from_abbreviation(abbreviation=league_abbreviation)
            for league_abbreviation in abbreviations.split("/")
        ]
