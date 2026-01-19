"""Parsers for box score data."""

import re
from datetime import datetime

from src.parsers.base import PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX
from src.utils.casting import str_to_float, str_to_int


class PlayerBoxScoreOutcomeParser:
    """
    Parses the game outcome from the box score string (e.g., 'W' or 'L').
    """

    def __init__(
        self,
        outcome_abbreviation_parser,
        formatted_outcome_regex=PLAYER_SEASON_BOX_SCORES_OUTCOME_REGEX,
        outcome_abbreviation_regex_group_name="outcome_abbreviation",
    ):
        self.outcome_abbreviation_parser = outcome_abbreviation_parser
        self.formatted_outcome_regex = formatted_outcome_regex
        self.outcome_abbreviation_regex_group_name = (
            outcome_abbreviation_regex_group_name
        )

    def search_formatted_outcome(self, formatted_outcome):
        """Regex match the outcome string (e.g. 'W, 110-95')."""
        return re.search(self.formatted_outcome_regex, formatted_outcome)

    def parse_outcome_abbreviation(self, formatted_outcome):
        """Extract just the 'W' or 'L' from the string."""
        return self.search_formatted_outcome(formatted_outcome=formatted_outcome).group(
            self.outcome_abbreviation_regex_group_name
        )

    def parse_outcome(self, formatted_outcome):
        """
        Convert outcome string to Outcome enum.

        Args:
            formatted_outcome (str): e.g. "W, 105-100" or "L (OT)"

        Returns:
            Outcome: Outcome.WIN or Outcome.LOSS
        """
        return self.outcome_abbreviation_parser.from_abbreviation(
            abbreviation=self.parse_outcome_abbreviation(
                formatted_outcome=formatted_outcome
            )
        )


class PlayerBoxScoresParser:
    """
    Parses raw data from 'Daily Leaders' tables into structured dictionaries.

    This parser handles the specific format of the daily leaders page,
    converting raw strings into ints, floats, and Enums.
    """

    def __init__(
        self,
        team_abbreviation_parser,
        location_abbreviation_parser,
        outcome_abbreviation_parser,
        seconds_played_parser,
    ):
        self.team_abbreviation_parser = team_abbreviation_parser
        self.location_abbreviation_parser = location_abbreviation_parser
        self.outcome_abbreviation_parser = outcome_abbreviation_parser
        self.seconds_played_parser = seconds_played_parser

    def parse(self, box_scores):
        """
        Parse list of box score rows into dicts.

        Args:
            box_scores (list[PlayerGameBoxScoreRow]): List of raw DOM wrappers.

        Returns:
            list[dict]: List of cleaned, type-converted stats dictionaries.
        """
        return [
            {
                "slug": str(box_score.slug),
                "name": str(box_score.name).rstrip("*"),
                "team": self.team_abbreviation_parser.from_abbreviation(
                    box_score.team_abbreviation
                ),
                "location": self.location_abbreviation_parser.from_abbreviation(
                    box_score.location_abbreviation.strip()
                ),
                "opponent": self.team_abbreviation_parser.from_abbreviation(
                    box_score.opponent_abbreviation
                ),
                "outcome": self.outcome_abbreviation_parser.from_abbreviation(
                    box_score.outcome
                ),
                "seconds_played": self.seconds_played_parser.parse(
                    box_score.playing_time
                ),
                "made_field_goals": str_to_int(box_score.made_field_goals),
                "attempted_field_goals": str_to_int(box_score.attempted_field_goals),
                "made_three_point_field_goals": str_to_int(
                    box_score.made_three_point_field_goals
                ),
                "attempted_three_point_field_goals": str_to_int(
                    box_score.attempted_three_point_field_goals
                ),
                "made_free_throws": str_to_int(box_score.made_free_throws),
                "attempted_free_throws": str_to_int(box_score.attempted_free_throws),
                "offensive_rebounds": str_to_int(box_score.offensive_rebounds),
                "defensive_rebounds": str_to_int(box_score.defensive_rebounds),
                "assists": str_to_int(box_score.assists),
                "steals": str_to_int(box_score.steals),
                "blocks": str_to_int(box_score.blocks),
                "turnovers": str_to_int(box_score.turnovers),
                "personal_fouls": str_to_int(box_score.personal_fouls),
                "plus_minus": str_to_float(box_score.plus_minus),
                "game_score": str_to_float(box_score.game_score),
            }
            for box_score in box_scores
        ]


class PlayerSeasonBoxScoresParser:
    """
    Parses a player's full season game log.

    Handles two types of rows:
    1. Active games (where stats exist).
    2. Inactive games (DNP/Inactive), which contain None for stats.

    The 'include_inactive_games' flag determines if type 2 rows are returned.
    """

    def __init__(
        self,
        team_abbreviation_parser,
        location_abbreviation_parser,
        outcome_parser,
        seconds_played_parser,
    ):
        self.team_abbreviation_parser = team_abbreviation_parser
        self.location_abbreviation_parser = location_abbreviation_parser
        self.outcome_parser = outcome_parser
        self.seconds_played_parser = seconds_played_parser

    def parse(self, box_scores, include_inactive_games=False):
        """
        Parse list of season box score rows.

        Args:
            box_scores (list[PlayerSeasonBoxScoresRow]): Rows to parse.
            include_inactive_games (bool): If True, returns dicts with 'active': False
                for games where the player didn't play. If False, these rows are skipped.

        Returns:
            list[dict]: List of game log entries.
        """
        results = []

        for box_score in box_scores:
            common = {
                "date": datetime.strptime(str(box_score.date), "%Y-%m-%d").date(),
                "team": self.team_abbreviation_parser.from_abbreviation(
                    box_score.team_abbreviation
                ),
                "location": self.location_abbreviation_parser.from_abbreviation(
                    box_score.location_abbreviation.strip()
                ),
                "opponent": self.team_abbreviation_parser.from_abbreviation(
                    box_score.opponent_abbreviation
                ),
                "outcome": self.outcome_parser.parse_outcome(
                    formatted_outcome=box_score.outcome
                ),
            }
            if box_score.is_active:
                results.append(
                    {
                        **common,
                        "active": True,
                        "seconds_played": self.seconds_played_parser.parse(
                            box_score.playing_time
                        ),
                        "made_field_goals": str_to_int(box_score.made_field_goals),
                        "attempted_field_goals": str_to_int(
                            box_score.attempted_field_goals
                        ),
                        "made_three_point_field_goals": str_to_int(
                            box_score.made_three_point_field_goals
                        ),
                        "attempted_three_point_field_goals": str_to_int(
                            box_score.attempted_three_point_field_goals
                        ),
                        "made_free_throws": str_to_int(box_score.made_free_throws),
                        "attempted_free_throws": str_to_int(
                            box_score.attempted_free_throws
                        ),
                        "offensive_rebounds": str_to_int(box_score.offensive_rebounds),
                        "defensive_rebounds": str_to_int(box_score.defensive_rebounds),
                        "assists": str_to_int(box_score.assists),
                        "steals": str_to_int(box_score.steals),
                        "blocks": str_to_int(box_score.blocks),
                        "turnovers": str_to_int(box_score.turnovers),
                        "personal_fouls": str_to_int(box_score.personal_fouls),
                        "points_scored": str_to_int(box_score.points_scored),
                        "game_score": str_to_float(box_score.game_score),
                        "plus_minus": str_to_int(box_score.plus_minus),
                    }
                )
            elif include_inactive_games:
                results.append(
                    {
                        **common,
                        "active": False,
                        "seconds_played": None,
                        "made_field_goals": None,
                        "attempted_field_goals": None,
                        "made_three_point_field_goals": None,
                        "attempted_three_point_field_goals": None,
                        "made_free_throws": None,
                        "attempted_free_throws": None,
                        "offensive_rebounds": None,
                        "defensive_rebounds": None,
                        "assists": None,
                        "steals": None,
                        "blocks": None,
                        "turnovers": None,
                        "personal_fouls": None,
                        "points_scored": None,
                        "game_score": None,
                        "plus_minus": None,
                    }
                )

        return results
