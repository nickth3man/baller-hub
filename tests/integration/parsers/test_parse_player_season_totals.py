import os
from unittest import TestCase

from lxml import html

from src.core.domain import (
    POSITION_ABBREVIATIONS_TO_POSITION,
    TEAM_ABBREVIATIONS_TO_TEAM,
    Position,
    Team,
)
from src.scraper.html import PlayerSeasonTotalTable
from src.scraper.parsers import (
    PlayerSeasonTotalsParser,
    PositionAbbreviationParser,
    TeamAbbreviationParser,
)


class BasePlayerSeasonTotalsTestCase(TestCase):
    _season_end_year = None

    @classmethod
    def setUpClass(cls):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                f"../files/players_season_totals/{cls._season_end_year}.html",
            ),
            encoding="utf-8",
        ) as file_input:
            _html = file_input.read()
        cls._parsed_season_totals = PlayerSeasonTotalsParser(
            position_abbreviation_parser=PositionAbbreviationParser(
                abbreviations_to_positions=POSITION_ABBREVIATIONS_TO_POSITION
            ),
            team_abbreviation_parser=TeamAbbreviationParser(
                abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM,
            ),
        ).parse(PlayerSeasonTotalTable(html=html.fromstring(_html)).rows)


class Test2001PlayerSeasonTotals(BasePlayerSeasonTotalsTestCase):
    _season_end_year = 2001

    def test_length(self):
        assert len(Test2001PlayerSeasonTotals._parsed_season_totals) == 490  # noqa: PLR2004

    def test_mahmoud_abdul_rauf(self):
        mahmoud_abdul_rauf = Test2001PlayerSeasonTotals._parsed_season_totals[279]

        assert mahmoud_abdul_rauf["slug"] == "abdulma02"
        assert mahmoud_abdul_rauf["name"] == "Mahmoud Abdul-Rauf"
        assert mahmoud_abdul_rauf["positions"] == [Position.POINT_GUARD]
        assert mahmoud_abdul_rauf["team"] == Team.VANCOUVER_GRIZZLIES
        assert mahmoud_abdul_rauf["games_played"] == 41  # noqa: PLR2004
        assert mahmoud_abdul_rauf["games_started"] == 0
        assert mahmoud_abdul_rauf["minutes_played"] == 486  # noqa: PLR2004
        assert mahmoud_abdul_rauf["made_field_goals"] == 120  # noqa: PLR2004
        assert mahmoud_abdul_rauf["attempted_field_goals"] == 246  # noqa: PLR2004
        assert mahmoud_abdul_rauf["made_three_point_field_goals"] == 4  # noqa: PLR2004
        assert mahmoud_abdul_rauf["attempted_three_point_field_goals"] == 14  # noqa: PLR2004
        assert mahmoud_abdul_rauf["made_free_throws"] == 22  # noqa: PLR2004
        assert mahmoud_abdul_rauf["attempted_free_throws"] == 29  # noqa: PLR2004
        assert mahmoud_abdul_rauf["offensive_rebounds"] == 5  # noqa: PLR2004
        assert mahmoud_abdul_rauf["defensive_rebounds"] == 20  # noqa: PLR2004
        assert mahmoud_abdul_rauf["assists"] == 76  # noqa: PLR2004
        assert mahmoud_abdul_rauf["steals"] == 9  # noqa: PLR2004
        assert mahmoud_abdul_rauf["blocks"] == 1
        assert mahmoud_abdul_rauf["turnovers"] == 26  # noqa: PLR2004
        assert mahmoud_abdul_rauf["personal_fouls"] == 50  # noqa: PLR2004


class Test2018PlayerSeasonTotals(BasePlayerSeasonTotalsTestCase):
    _season_end_year = 2018

    def test_length(self):
        assert len(Test2018PlayerSeasonTotals._parsed_season_totals) == 605  # noqa: PLR2004

    def test_alex_abrines(self):
        alex_abrines = Test2018PlayerSeasonTotals._parsed_season_totals[300]

        assert alex_abrines["slug"] == "abrinal01"
        assert alex_abrines["name"] == "Álex Abrines"
        assert alex_abrines["positions"] == [Position.SHOOTING_GUARD]
        assert alex_abrines["team"] == Team.OKLAHOMA_CITY_THUNDER
        assert alex_abrines["games_played"] == 75  # noqa: PLR2004
        assert alex_abrines["games_started"] == 8  # noqa: PLR2004
        assert alex_abrines["minutes_played"] == 1134  # noqa: PLR2004
        assert alex_abrines["made_field_goals"] == 115  # noqa: PLR2004
        assert alex_abrines["attempted_field_goals"] == 291  # noqa: PLR2004
        assert alex_abrines["made_three_point_field_goals"] == 84  # noqa: PLR2004
        assert alex_abrines["attempted_three_point_field_goals"] == 221  # noqa: PLR2004
        assert alex_abrines["made_free_throws"] == 39  # noqa: PLR2004
        assert alex_abrines["attempted_free_throws"] == 46  # noqa: PLR2004
        assert alex_abrines["offensive_rebounds"] == 26  # noqa: PLR2004
        assert alex_abrines["defensive_rebounds"] == 88  # noqa: PLR2004
        assert alex_abrines["assists"] == 28  # noqa: PLR2004
        assert alex_abrines["steals"] == 38  # noqa: PLR2004
        assert alex_abrines["blocks"] == 8  # noqa: PLR2004
        assert alex_abrines["turnovers"] == 25  # noqa: PLR2004
        assert alex_abrines["personal_fouls"] == 124  # noqa: PLR2004

    def test_omer_asik(self):
        pelicans_omer_asik = Test2018PlayerSeasonTotals._parsed_season_totals[528]

        assert pelicans_omer_asik["slug"] == "asikom01"
        assert pelicans_omer_asik["name"] == "Ömer Aşık"  # noqa: RUF001
        assert pelicans_omer_asik["positions"] == [Position.CENTER]
        assert pelicans_omer_asik["team"] == Team.NEW_ORLEANS_PELICANS
        assert pelicans_omer_asik["games_played"] == 14  # noqa: PLR2004
        assert pelicans_omer_asik["games_started"] == 0
        assert pelicans_omer_asik["minutes_played"] == 121  # noqa: PLR2004
        assert pelicans_omer_asik["made_field_goals"] == 7  # noqa: PLR2004
        assert pelicans_omer_asik["attempted_field_goals"] == 16  # noqa: PLR2004
        assert pelicans_omer_asik["made_three_point_field_goals"] == 0
        assert pelicans_omer_asik["attempted_three_point_field_goals"] == 0
        assert pelicans_omer_asik["made_free_throws"] == 4  # noqa: PLR2004
        assert pelicans_omer_asik["attempted_free_throws"] == 12  # noqa: PLR2004
        assert pelicans_omer_asik["offensive_rebounds"] == 7  # noqa: PLR2004
        assert pelicans_omer_asik["defensive_rebounds"] == 30  # noqa: PLR2004
        assert pelicans_omer_asik["assists"] == 2  # noqa: PLR2004
        assert pelicans_omer_asik["steals"] == 1
        assert pelicans_omer_asik["blocks"] == 2  # noqa: PLR2004
        assert pelicans_omer_asik["turnovers"] == 5  # noqa: PLR2004
        assert pelicans_omer_asik["personal_fouls"] == 14  # noqa: PLR2004

        bulls_omer_asik = Test2018PlayerSeasonTotals._parsed_season_totals[529]

        assert pelicans_omer_asik["slug"] == "asikom01"
        assert bulls_omer_asik["name"] == "Ömer Aşık"  # noqa: RUF001
        assert bulls_omer_asik["positions"] == [Position.CENTER]
        assert bulls_omer_asik["team"] == Team.CHICAGO_BULLS
        assert bulls_omer_asik["games_played"] == 4  # noqa: PLR2004
        assert bulls_omer_asik["games_started"] == 0
        assert bulls_omer_asik["minutes_played"] == 61  # noqa: PLR2004
        assert bulls_omer_asik["made_field_goals"] == 2  # noqa: PLR2004
        assert bulls_omer_asik["attempted_field_goals"] == 6  # noqa: PLR2004
        assert bulls_omer_asik["made_three_point_field_goals"] == 0
        assert bulls_omer_asik["attempted_three_point_field_goals"] == 0
        assert bulls_omer_asik["made_free_throws"] == 0
        assert bulls_omer_asik["attempted_free_throws"] == 1
        assert bulls_omer_asik["offensive_rebounds"] == 2  # noqa: PLR2004
        assert bulls_omer_asik["defensive_rebounds"] == 8  # noqa: PLR2004
        assert bulls_omer_asik["assists"] == 1
        assert bulls_omer_asik["steals"] == 1
        assert bulls_omer_asik["blocks"] == 2  # noqa: PLR2004
        assert bulls_omer_asik["turnovers"] == 4  # noqa: PLR2004
        assert bulls_omer_asik["personal_fouls"] == 6  # noqa: PLR2004


class Test2019PlayerSeasonTotals(BasePlayerSeasonTotalsTestCase):
    _season_end_year = 2019

    def test_jimmy_butler(self):
        philly_jimmy_butler = Test2019PlayerSeasonTotals._parsed_season_totals[60]

        assert philly_jimmy_butler["slug"] == "butleji01"
        assert philly_jimmy_butler["name"] == "Jimmy Butler"
        assert philly_jimmy_butler["positions"] == [Position.SMALL_FORWARD]
        assert philly_jimmy_butler["team"] == Team.PHILADELPHIA_76ERS
        assert philly_jimmy_butler["games_played"] == 55  # noqa: PLR2004
        assert philly_jimmy_butler["games_started"] == 55  # noqa: PLR2004
        assert philly_jimmy_butler["minutes_played"] == 1824  # noqa: PLR2004
        assert philly_jimmy_butler["made_field_goals"] == 344  # noqa: PLR2004
        assert philly_jimmy_butler["attempted_field_goals"] == 747  # noqa: PLR2004
        assert philly_jimmy_butler["made_three_point_field_goals"] == 50  # noqa: PLR2004
        assert philly_jimmy_butler["attempted_three_point_field_goals"] == 148  # noqa: PLR2004
        assert philly_jimmy_butler["made_free_throws"] == 264  # noqa: PLR2004
        assert philly_jimmy_butler["attempted_free_throws"] == 304  # noqa: PLR2004
        assert philly_jimmy_butler["offensive_rebounds"] == 105  # noqa: PLR2004
        assert philly_jimmy_butler["defensive_rebounds"] == 185  # noqa: PLR2004
        assert philly_jimmy_butler["assists"] == 220  # noqa: PLR2004
        assert philly_jimmy_butler["steals"] == 99  # noqa: PLR2004
        assert philly_jimmy_butler["blocks"] == 29  # noqa: PLR2004
        assert philly_jimmy_butler["turnovers"] == 81  # noqa: PLR2004
        assert philly_jimmy_butler["personal_fouls"] == 93  # noqa: PLR2004
