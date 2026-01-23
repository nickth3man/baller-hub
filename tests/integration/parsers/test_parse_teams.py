import os
from unittest import TestCase

from lxml import html

from src.core.domain import TEAM_ABBREVIATIONS_TO_TEAM, Outcome, Team, TeamTotal
from src.scraper.html import BoxScoresPage
from src.scraper.parsers import TeamAbbreviationParser, TeamTotalsParser


class TestParseTeams(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(  # noqa: PTH123
            os.path.join(  # noqa: PTH118
                os.path.dirname(__file__),  # noqa: PTH120
                "../files/boxscores/2017/1/201701010ATL.html",
            ),
            encoding="utf-8",
        ) as file_input:
            _html = file_input.read()
        first_team_totals, second_team_totals = [
            TeamTotal(
                team_abbreviation=table.team_abbreviation, totals=table.team_totals
            )
            for table in BoxScoresPage(
                html.fromstring(html=_html)
            ).basic_statistics_tables
        ]
        cls._parsed_results = TeamTotalsParser(
            team_abbreviation_parser=TeamAbbreviationParser(
                abbreviations_to_teams=TEAM_ABBREVIATIONS_TO_TEAM
            ),
        ).parse(
            first_team_totals=first_team_totals,
            second_team_totals=second_team_totals,
        )

    def test_length(self):
        assert len(self._parsed_results) == 2  # noqa: PLR2004

    def test_parse_san_antonio_team_totals(self):
        sas_team_totals = self._parsed_results[0]
        assert sas_team_totals["team"] == Team.SAN_ANTONIO_SPURS
        assert sas_team_totals["outcome"] == Outcome.LOSS
        assert sas_team_totals["minutes_played"] == 265  # noqa: PLR2004
        assert sas_team_totals["made_field_goals"] == 42  # noqa: PLR2004
        assert sas_team_totals["attempted_field_goals"] == 90  # noqa: PLR2004
        assert sas_team_totals["made_three_point_field_goals"] == 9  # noqa: PLR2004
        assert sas_team_totals["attempted_three_point_field_goals"] == 27  # noqa: PLR2004
        assert sas_team_totals["made_free_throws"] == 19  # noqa: PLR2004
        assert sas_team_totals["attempted_free_throws"] == 22  # noqa: PLR2004
        assert sas_team_totals["offensive_rebounds"] == 9  # noqa: PLR2004
        assert sas_team_totals["defensive_rebounds"] == 38  # noqa: PLR2004
        assert sas_team_totals["assists"] == 27  # noqa: PLR2004
        assert sas_team_totals["steals"] == 5  # noqa: PLR2004
        assert sas_team_totals["blocks"] == 6  # noqa: PLR2004
        assert sas_team_totals["turnovers"] == 12  # noqa: PLR2004
        assert sas_team_totals["personal_fouls"] == 21  # noqa: PLR2004
        assert sas_team_totals["points"] == 112  # noqa: PLR2004

    def test_parse_atlanta_team_totals(self):
        atl_team_totals = self._parsed_results[1]
        assert atl_team_totals["team"] == Team.ATLANTA_HAWKS
        assert atl_team_totals["outcome"] == Outcome.WIN
        assert atl_team_totals["minutes_played"] == 265  # noqa: PLR2004
        assert atl_team_totals["made_field_goals"] == 42  # noqa: PLR2004
        assert atl_team_totals["attempted_field_goals"] == 92  # noqa: PLR2004
        assert atl_team_totals["made_three_point_field_goals"] == 14  # noqa: PLR2004
        assert atl_team_totals["attempted_three_point_field_goals"] == 28  # noqa: PLR2004
        assert atl_team_totals["made_free_throws"] == 16  # noqa: PLR2004
        assert atl_team_totals["attempted_free_throws"] == 27  # noqa: PLR2004
        assert atl_team_totals["offensive_rebounds"] == 11  # noqa: PLR2004
        assert atl_team_totals["defensive_rebounds"] == 35  # noqa: PLR2004
        assert atl_team_totals["assists"] == 25  # noqa: PLR2004
        assert atl_team_totals["steals"] == 6  # noqa: PLR2004
        assert atl_team_totals["blocks"] == 6  # noqa: PLR2004
        assert atl_team_totals["turnovers"] == 11  # noqa: PLR2004
        assert atl_team_totals["personal_fouls"] == 21  # noqa: PLR2004
        assert atl_team_totals["points"] == 114  # noqa: PLR2004
