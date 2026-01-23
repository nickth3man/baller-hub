import os
from datetime import datetime, timedelta
from unittest import TestCase

import pytz
from lxml import html

from src.core.domain import TEAM_NAME_TO_TEAM, Team
from src.scraper.html import SchedulePage
from src.scraper.parsers import (
    ScheduledGamesParser,
    ScheduledStartTimeParser,
    TeamNameParser,
)


class BaseTest(TestCase):
    _path_from_schedule_directory: str = None

    @classmethod
    def setUpClass(cls):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                f"../files/schedule/{cls._path_from_schedule_directory}",
            ),
            encoding="utf-8",
        ) as file_input:
            _html = file_input.read()
        cls._page = SchedulePage(html=html.fromstring(_html))

        super().setUpClass()


class BaseParserTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                f"../files/schedule/{cls._path_from_schedule_directory}",
            ),
            encoding="utf-8",
        ) as file_input:
            _html = file_input.read()
        cls._parsed_results = ScheduledGamesParser(
            start_time_parser=ScheduledStartTimeParser(),
            team_name_parser=TeamNameParser(team_names_to_teams=TEAM_NAME_TO_TEAM),
        ).parse_games(games=SchedulePage(html=html.fromstring(_html)).rows)

        super().setUpClass()


class TestSchedulePage(BaseTest):
    _path_from_schedule_directory = "2001/2001.html"

    def test_expected_urls(self):
        assert self._page.other_months_schedule_urls == ["/leagues/NBA_2001_games-october.html", "/leagues/NBA_2001_games-november.html", "/leagues/NBA_2001_games-december.html", "/leagues/NBA_2001_games-january.html", "/leagues/NBA_2001_games-february.html", "/leagues/NBA_2001_games-march.html", "/leagues/NBA_2001_games-april.html", "/leagues/NBA_2001_games-may.html", "/leagues/NBA_2001_games-june.html"]


class TestOctober2001Parser(BaseParserTest):
    _path_from_schedule_directory = "2001/2001.html"

    def test_length(self):
        assert len(self._parsed_results) == 13

    def test_first_game(self):
        first_game = self._parsed_results[0]
        expected_datetime = (
            pytz.timezone("US/Eastern")
            .localize(datetime(year=2000, month=10, day=31, hour=19, minute=30))
            .astimezone(pytz.utc)
        )

        assert abs(first_game["start_time"] - expected_datetime) < timedelta(seconds=1)
        assert first_game["away_team"] == Team.CHARLOTTE_HORNETS
        assert first_game["home_team"] == Team.ATLANTA_HAWKS
        assert first_game["away_team_score"] == 106
        assert first_game["home_team_score"] == 82


class TestOctober2018Parser(BaseParserTest):
    _path_from_schedule_directory = "2018/2018.html"

    def test_length(self):
        assert len(self._parsed_results) == 104


class TestParsingUpcomingGames(BaseParserTest):
    _path_from_schedule_directory = "upcoming-games.html"

    def test_length(self):
        assert len(self._parsed_results) == 79

    def test_first_game(self):
        first_game = self._parsed_results[0]

        assert first_game["start_time"] == pytz.timezone("US/Eastern").localize(datetime(year=2019, month=4, day=1, hour=19, minute=30)).astimezone(pytz.utc)
        assert first_game["away_team"] == Team.MIAMI_HEAT
        assert first_game["home_team"] == Team.BOSTON_CELTICS
        assert first_game["away_team_score"] is None
        assert first_game["home_team_score"] is None
