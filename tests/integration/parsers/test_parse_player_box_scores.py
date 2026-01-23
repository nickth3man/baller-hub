import datetime
import os
from unittest import TestCase

from lxml import html

from src.core.domain import (
    LOCATION_ABBREVIATIONS_TO_POSITION,
    OUTCOME_ABBREVIATIONS_TO_OUTCOME,
    TEAM_ABBREVIATIONS_TO_TEAM,
    Outcome,
    Team,
)
from src.scraper.html import DailyLeadersPage
from src.scraper.parsers import (
    LocationAbbreviationParser,
    OutcomeAbbreviationParser,
    PlayerBoxScoresParser,
    SecondsPlayedParser,
    TeamAbbreviationParser,
)


class BaseBoxScoresTestCase(TestCase):
    _date: datetime.date = None

    @classmethod
    def setUpClass(cls):
        year, month, day = cls._date.year, cls._date.month, cls._date.day
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/player_box_scores/{year}/{month}/{day}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            _html = file_input.read()
        cls._parsed_results = PlayerBoxScoresParser(
            team_abbreviation_parser=TeamAbbreviationParser(
                abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM
            ),
            location_abbreviation_parser=LocationAbbreviationParser(
                abbreviations_to_locations=LOCATION_ABBREVIATIONS_TO_POSITION
            ),
            outcome_abbreviation_parser=OutcomeAbbreviationParser(
                abbreviations_to_outcomes=OUTCOME_ABBREVIATIONS_TO_OUTCOME
            ),
            seconds_played_parser=SecondsPlayedParser(),
        ).parse(DailyLeadersPage(html=html.fromstring(_html)).daily_leaders)


class TestNovemberFirst2006(BaseBoxScoresTestCase):
    _date = datetime.date(year=2006, month=11, day=1)

    def test_length(self):
        assert len(self._parsed_results) == 272  # noqa: PLR2004

    def test_new_orleans_oklahoma_city_hornets(self):
        chris_paul = self._parsed_results[10]

        assert chris_paul["slug"] == "paulch01"
        assert chris_paul["name"] == "Chris Paul"
        assert chris_paul["team"] == Team.NEW_ORLEANS_OKLAHOMA_CITY_HORNETS


class TestDecemberEighteenth2015(BaseBoxScoresTestCase):
    _date = datetime.date(year=2015, month=12, day=18)

    def test_length(self):
        assert len(self._parsed_results) == 250  # noqa: PLR2004


class TestNovemberThird2003(BaseBoxScoresTestCase):
    _date = datetime.date(year=2003, month=11, day=3)

    def test_length(self):
        assert len(self._parsed_results) == 145  # noqa: PLR2004

    def test_new_orleans_hornets(self):
        pj_brown = self._parsed_results[51]

        assert pj_brown["slug"] == "brownpj01"
        assert pj_brown["name"] == "P.J. Brown"
        assert pj_brown["team"] == Team.NEW_ORLEANS_HORNETS


class TestDecemberTwelfth2017(BaseBoxScoresTestCase):
    _date = datetime.date(year=2017, month=12, day=12)

    def test_length(self):
        assert len(self._parsed_results) == 149  # noqa: PLR2004

    def test_andrew_bogut(self):
        andrew_bogut = self._parsed_results[128]
        assert andrew_bogut["made_three_point_field_goals"] == 0
        assert andrew_bogut["attempted_three_point_field_goals"] == 0


class TestJanuaryTwentyNinth2017(BaseBoxScoresTestCase):
    _date = datetime.date(year=2017, month=1, day=29)

    def test_length(self):
        assert len(self._parsed_results) == 170  # noqa: PLR2004

    def test_paul_millsap(self):
        paul_millsap = self._parsed_results[0]

        assert paul_millsap["slug"] == "millspa01"
        assert paul_millsap["name"] == "Paul Millsap"
        assert paul_millsap["team"] == Team.ATLANTA_HAWKS
        assert paul_millsap["opponent"] == Team.NEW_YORK_KNICKS
        assert paul_millsap["outcome"] == Outcome.WIN
        assert paul_millsap["seconds_played"] == 3607  # noqa: PLR2004
        assert paul_millsap["made_field_goals"] == 13  # noqa: PLR2004
        assert paul_millsap["attempted_field_goals"] == 29  # noqa: PLR2004
        assert paul_millsap["made_three_point_field_goals"] == 3  # noqa: PLR2004
        assert paul_millsap["attempted_three_point_field_goals"] == 8  # noqa: PLR2004
        assert paul_millsap["made_free_throws"] == 8  # noqa: PLR2004
        assert paul_millsap["attempted_free_throws"] == 10  # noqa: PLR2004
        assert paul_millsap["offensive_rebounds"] == 8  # noqa: PLR2004
        assert paul_millsap["defensive_rebounds"] == 11  # noqa: PLR2004
        assert paul_millsap["assists"] == 7  # noqa: PLR2004
        assert paul_millsap["steals"] == 1
        assert paul_millsap["blocks"] == 0
        assert paul_millsap["turnovers"] == 3  # noqa: PLR2004
        assert paul_millsap["personal_fouls"] == 4  # noqa: PLR2004
        assert paul_millsap["game_score"] == 31.3  # noqa: PLR2004
