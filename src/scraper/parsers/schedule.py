"""Parsers for schedule data."""

from datetime import datetime

import pytz

from src.scraper.utils.casting import str_to_int


class TeamNameParser:
    """
    Normalizes team names (e.g. "Boston Celtics") to Team enums.
    """

    def __init__(self, team_names_to_teams):
        self.team_names_to_teams = team_names_to_teams

    def parse_team_name(self, team_name):
        """
        Convert string name to Team enum.

        Args:
            team_name (str): e.g. "Boston Celtics" (case insensitive).

        Returns:
            Team: The corresponding Team enum.
        """
        return self.team_names_to_teams[team_name.strip().upper()]


class ScheduledStartTimeParser:
    """
    Parses game start times into timezone-aware datetime objects.

    Handles historical format changes:
    - 2001-2017: Times used "am/pm" (e.g., "7:00 pm").
    - 2018-Present: Times use "p/a" suffix (e.g., "7:00p").

    All times are converted from US/Eastern (site default) to UTC.
    """

    def __init__(self, time_zone=pytz.utc):
        self.time_zone = time_zone

    def parse_start_time(self, formatted_date, formatted_time_of_day):
        """
        Combine date and time strings into a timezone-aware datetime.

        Args:
            formatted_date (str): e.g. "Wed, Oct 25, 2023".
            formatted_time_of_day (str): e.g. "7:30p" or "7:30 pm".

        Returns:
            datetime: UTC start time.
        """
        est = pytz.timezone("US/Eastern")
        if formatted_time_of_day is not None and formatted_time_of_day not in ["", " "]:
            # Starting in 2018, the start times had a "p" or "a" appended to the end
            # Between 2001 and 2017, the start times had a "pm" or "am"
            #
            # https://www.basketball-reference.com/leagues/NBA_2018_games.html
            # vs.
            # https://www.basketball-reference.com/leagues/NBA_2001_games.html
            is_prior_format = (
                formatted_time_of_day[-2:] == "am" or formatted_time_of_day[-2:] == "pm"
            )

            # If format contains only "p" or "a" add an "m" so it can be parsed by datetime module
            if is_prior_format:
                combined_formatted_time = formatted_date + " " + formatted_time_of_day
            else:
                combined_formatted_time = (
                    formatted_date + " " + formatted_time_of_day + "m"
                )

            if is_prior_format:
                start_time = est.localize(
                    datetime.strptime(combined_formatted_time, "%a, %b %d, %Y %I:%M %p")  # noqa: DTZ007
                )
            else:
                start_time = est.localize(
                    datetime.strptime(combined_formatted_time, "%a, %b %d, %Y %I:%M%p")  # noqa: DTZ007
                )
        else:
            start_time = est.localize(
                datetime.strptime(formatted_date, "%a, %b %d, %Y")  # noqa: DTZ007
            )

        return start_time.astimezone(self.time_zone)


class ScheduledGamesParser:
    """
    Parses rows from the monthly schedule table.
    """

    def __init__(self, start_time_parser, team_name_parser):
        self.start_time_parser = start_time_parser
        self.team_name_parser = team_name_parser

    def parse_games(self, games):
        """
        Parse a list of schedule rows into game dictionaries.

        Args:
            games (list[ScheduleRow]): Raw DOM wrappers.

        Returns:
            list[dict]: List of game dicts with keys: start_time, away_team,
                home_team, away_team_score, home_team_score.
        """
        return [
            {
                "start_time": self.start_time_parser.parse_start_time(
                    formatted_date=game.start_date,
                    formatted_time_of_day=game.start_time_of_day,
                ),
                "away_team": self.team_name_parser.parse_team_name(
                    team_name=game.away_team_name
                ),
                "home_team": self.team_name_parser.parse_team_name(
                    team_name=game.home_team_name
                ),
                "away_team_score": str_to_int(value=game.away_team_score, default=None),
                "home_team_score": str_to_int(value=game.home_team_score, default=None),
            }
            for game in games
        ]
