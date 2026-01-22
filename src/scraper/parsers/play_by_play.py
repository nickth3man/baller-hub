"""Parsers for play-by-play data."""

import re
from datetime import datetime

from src.core.domain import PeriodType


class SecondsPlayedParser:
    """
    Parses time strings (MM:SS) into total seconds (int).

    Note: Can handle times > 60 minutes (e.g., 5OT games).
    """

    def parse(self, formatted_playing_time):
        """
        Convert "MM:SS" string to total seconds.

        Args:
            formatted_playing_time (str): Time string (e.g. "12:00").

        Returns:
            int: Total seconds.
        """
        if formatted_playing_time == "":
            return 0

        # It seems like basketball reference formats everything in MM:SS
        # even when the playing time is greater than 59 minutes, 59 seconds.
        #
        # Because of this, we can't use strptime / %M as valid values are 0-59.
        # So have to parse time by splitting on ":" and assuming that
        # the first part is the minute part and the second part is the seconds part
        time_parts = formatted_playing_time.split(":")
        minutes_played = time_parts[0]
        seconds_played = time_parts[1]
        return 60 * int(minutes_played) + int(seconds_played)


class PeriodDetailsParser:
    """
    Identifies the period type (Quarter/OT) and number from a period count.
    """

    def __init__(self, regulation_periods_count):
        self.regulation_periods_count = regulation_periods_count

    def is_overtime(self, period_count):
        """Check if period is overtime (e.g. > 4 for NBA)."""
        return period_count > self.regulation_periods_count

    def parse_period_number(self, period_count):
        """
        Get the period number relative to its type.

        For NBA:
        - 1 -> 1st Quarter
        - 5 -> 1st Overtime
        """
        if self.is_overtime(period_count=period_count):
            return period_count - self.regulation_periods_count

        return period_count

    def parse_period_type(self, period_count):
        """Get PeriodType enum (QUARTER or OVERTIME)."""
        if self.is_overtime(period_count=period_count):
            return PeriodType.OVERTIME

        return PeriodType.QUARTER


class PeriodTimestampParser:
    """
    Parses timestamp strings into seconds remaining.
    """

    def __init__(self, timestamp_format):
        self.timestamp_format = timestamp_format

    def to_seconds(self, timestamp):
        """
        Convert timestamp string to float seconds.

        Args:
            timestamp (str): e.g. "11:45.0".

        Returns:
            float: Total seconds remaining.
        """
        dt = datetime.strptime(timestamp, self.timestamp_format)
        return float((dt.minute * 60) + dt.second + (dt.microsecond / 1000000))


class ScoresParser:
    """
    Parses score strings (e.g. "10-8") into integer scores.
    """

    def __init__(
        self,
        scores_regex,
        away_team_score_group_name="away_team_score",
        home_team_score_group_name="home_team_score",
    ):
        self.scores_regex = scores_regex
        self.away_team_score_group_name = away_team_score_group_name
        self.home_team_score_group_name = home_team_score_group_name

    def parse_scores(self, formatted_scores):
        """Regex match the score string."""
        return re.search(self.scores_regex, formatted_scores)

    def parse_away_team_score(self, formatted_scores):
        """Extract away team score integer."""
        return int(
            self.parse_scores(formatted_scores=formatted_scores).group(
                self.away_team_score_group_name
            )
        )

    def parse_home_team_score(self, formatted_scores):
        """Extract home team score integer."""
        return int(
            self.parse_scores(formatted_scores=formatted_scores).group(
                self.home_team_score_group_name
            )
        )


class PlayByPlaysParser:
    """
    Parses raw play-by-play table rows into structured events.

    Logic:
    - Tracks the current period (Q1, Q2, etc.) as it iterates through rows.
    - Identifies which team initiated the event.
    - Extracts score, time remaining, and play description.
    """

    def __init__(self, period_details_parser, period_timestamp_parser, scores_parser):
        self.period_details_parser = period_details_parser
        self.period_timestamp_parser = period_timestamp_parser
        self.scores_parser = scores_parser

    def parse(self, play_by_plays, away_team, home_team):
        """
        Parse all play-by-play rows for a game.

        Args:
            play_by_plays (list[PlayByPlayRow]): Raw rows from the PBP table.
            away_team (Team): The visiting team enum.
            home_team (Team): The home team enum.

        Returns:
            list[dict]: Chronological list of play events.
        """
        current_period = 0
        result = []
        for play_by_play in play_by_plays:
            if play_by_play.is_start_of_period:
                current_period += 1
            elif play_by_play.has_play_by_play_data:
                result.append(
                    self.format_data(
                        current_period=current_period,
                        play_by_play=play_by_play,
                        away_team=away_team,
                        home_team=home_team,
                    )
                )
        return result

    def format_data(self, current_period, play_by_play, away_team, home_team):
        """
        Format a single play event into a dictionary.
        """
        return {
            "period": self.period_details_parser.parse_period_number(
                period_count=current_period
            ),
            "period_type": self.period_details_parser.parse_period_type(
                period_count=current_period
            ),
            "remaining_seconds_in_period": self.period_timestamp_parser.to_seconds(
                timestamp=play_by_play.timestamp
            ),
            "relevant_team": away_team if play_by_play.is_away_team_play else home_team,
            "away_team": away_team,
            "home_team": home_team,
            "away_score": self.scores_parser.parse_away_team_score(
                formatted_scores=play_by_play.formatted_scores
            ),
            "home_score": self.scores_parser.parse_home_team_score(
                formatted_scores=play_by_play.formatted_scores
            ),
            "description": play_by_play.away_team_play_description
            if play_by_play.is_away_team_play
            else play_by_play.home_team_play_description,
        }
