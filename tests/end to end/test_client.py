import datetime
import filecmp
import time
from pathlib import Path
from unittest import TestCase

import pytest

from src.core.domain import (
    Location,
    Outcome,
    OutputType,
    OutputWriteOption,
    PeriodType,
    Team,
)
from src.scraper.api.client import (
    play_by_play,
    player_box_scores,
    players_advanced_season_totals,
    players_season_totals,
    season_schedule,
)


@pytest.mark.vcr
class BaseEndToEndTest(TestCase):
    def setUp(self):
        # To avoid getting rate-limited
        time.sleep(3)

    def tearDown(self):
        # To avoid getting rate-limited
        time.sleep(3)


class TestPlayerBoxScores(BaseEndToEndTest):
    def setUp(self):
        super().setUp()

        self.box_scores = player_box_scores(day=11, month=3, year=2024)

    def test_first_entry(self):
        assert self.box_scores is not None
        assert len(self.box_scores) != 0
        assert len(self.box_scores) == 124  # noqa: PLR2004
        self.assertDictEqual(  # noqa: PT009
            {
                "name": "Nikola Jokić",
                "slug": "jokicni01",
                "team": Team.DENVER_NUGGETS,
                "opponent": Team.TORONTO_RAPTORS,
                "location": Location.HOME,
                "outcome": Outcome.WIN,
                "seconds_played": 2286,
                "made_field_goals": 14,
                "attempted_field_goals": 26,
                "made_three_point_field_goals": 1,
                "attempted_three_point_field_goals": 3,
                "made_free_throws": 6,
                "attempted_free_throws": 6,
                "offensive_rebounds": 6,
                "defensive_rebounds": 11,
                "assists": 12,
                "steals": 6,
                "blocks": 2,
                "turnovers": 2,
                "personal_fouls": 3,
                "plus_minus": 13.0,
                "game_score": 42.5,
            },
            self.box_scores[0],
        )


class TestCsvPlayerBoxScores(BaseEndToEndTest):
    def test_csv_output(self):
        output_file_path = (
            Path(__file__).parent / "output/generated/playerboxscores/2024/03/11.csv"
        )
        player_box_scores(
            day=11,
            month=3,
            year=2024,
            output_type=OutputType.CSV,
            output_file_path=str(output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(
            output_file_path,
            Path(__file__).parent / "output/expected/playerboxscores/2024/03/11.csv",
        )


class TestJsonPlayerBoxScores(BaseEndToEndTest):
    def test_json_output(self):
        output_file_path = (
            Path(__file__).parent / "output/generated/playerboxscores/2024/03/11.json"
        )
        player_box_scores(
            day=11,
            month=3,
            year=2024,
            output_type=OutputType.JSON,
            output_file_path=str(output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(
            output_file_path,
            Path(__file__).parent / "output/expected/playerboxscores/2024/03/11.json",
        )


class TestSeasonSchedule(BaseEndToEndTest):
    def test_2001_season_schedule(self):
        schedule = season_schedule(season_end_year=2001)
        assert schedule is not None

    def test_current_year_season_schedule(self):
        schedule = season_schedule(season_end_year=datetime.datetime.now().year)  # noqa: DTZ005
        assert schedule is not None


class TestPlayerAdvancedSeasonTotals(BaseEndToEndTest):
    def test_totals(self):
        player_season_totals = players_advanced_season_totals(season_end_year=2019)
        assert player_season_totals is not None
        assert len(player_season_totals) > 0


class TestPlayByPlay(BaseEndToEndTest):
    def test_BOS_2018_10_16_play_by_play(self):  # noqa: N802
        plays = play_by_play(
            home_team=Team.BOSTON_CELTICS,
            day=16,
            month=10,
            year=2018,
        )
        assert plays is not None

    def test_BOS_2018_10_16_play_by_play_csv_to_file(self):  # noqa: N802
        output_file_path = (
            Path(__file__).parent / "output/generated/2018_10_16_BOS_pbp.csv"
        )
        play_by_play(
            home_team=Team.BOSTON_CELTICS,
            day=16,
            month=10,
            year=2018,
            output_type=OutputType.CSV,
            output_file_path=str(output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(
            output_file_path,
            Path(__file__).parent / "output/expected/2018_10_16_BOS_pbp.csv",
        )

    def test_overtime_play_by_play(self):
        plays = play_by_play(
            home_team=Team.PORTLAND_TRAIL_BLAZERS,
            day=22,
            month=10,
            year=2018,
        )
        last_play = plays[-1]
        assert last_play is not None
        assert last_play["period"] == 1
        assert last_play["period_type"] == PeriodType.OVERTIME

    def test_overtime_play_by_play_to_json_file(self):
        output_file_path = (
            Path(__file__).parent / "output/generated/2018_10_22_POR_pbp.json"
        )
        play_by_play(
            home_team=Team.PORTLAND_TRAIL_BLAZERS,
            day=22,
            month=10,
            year=2018,
            output_type=OutputType.JSON,
            output_file_path=str(output_file_path),
            output_write_option=OutputWriteOption.WRITE,
        )

        assert filecmp.cmp(
            output_file_path,
            Path(__file__).parent / "output/expected/2018_10_22_POR_pbp.json",
        )


class TestPlayersSeasonTotals(BaseEndToEndTest):
    def test_2018(self):
        totals = players_season_totals(season_end_year=2018)

        for total in totals:
            # TODO: @nickth3man turn this into a dataclass with validation
            assert total["name"] != ""
            assert total["name"] != "League Average"
            assert total["slug"]
            assert total["name"]
            assert total["positions"]
            assert total["age"] > 0
            assert total["games_played"] >= 0
            assert total["games_started"] >= 0
            assert total["minutes_played"] >= 0
            assert total["made_field_goals"] >= 0
            assert total["attempted_field_goals"] >= total["made_field_goals"]
            assert total["made_three_point_field_goals"] >= 0
            assert (
                total["attempted_three_point_field_goals"]
                >= total["made_three_point_field_goals"]
            )
            assert total["made_free_throws"] >= 0
            assert total["attempted_free_throws"] >= total["made_free_throws"]
            assert total["offensive_rebounds"] >= 0
            assert total["defensive_rebounds"] >= 0
            assert total["assists"] >= 0
            assert total["steals"] >= 0
            assert total["blocks"] >= 0
            assert total["turnovers"] >= 0
            assert total["personal_fouls"] >= 0
            assert total["points"] >= 0
